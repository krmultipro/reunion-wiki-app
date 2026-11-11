# -*- coding: utf-8 -*-
"""Contrôle HTTP déterministe des sites avant publication."""

from dataclasses import dataclass
import ipaddress
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


ACCESSIBLE = "accessible"
MANUAL_REVIEW = "manual_review"
TEMPORARY_ERROR = "temporary_error"
INACCESSIBLE = "inaccessible"
BLOCKED = "blocked"

REDIRECT_STATUSES = {301, 302, 303, 307, 308}


@dataclass(frozen=True)
class HttpResponse:
    """Réponse minimale utilisée par le moteur de décision."""

    status_code: int
    headers: object


@dataclass(frozen=True)
class HttpCheckResult:
    """Résultat persistant d'un contrôle d'accessibilité."""

    decision: str
    requested_url: str
    final_url: str
    status_code: int | None
    reason: str
    redirect_count: int = 0


class HttpCheckError(Exception):
    """Erreur de transport HTTP générique."""


class HttpTimeoutError(HttpCheckError):
    """Le serveur n'a pas répondu dans le délai imparti."""


class InvalidCertificateError(HttpCheckError):
    """Le certificat TLS présenté n'est pas valide."""


class UnsafeUrlError(HttpCheckError):
    """L'URL vise une destination interdite ou invalide."""


class _NoRedirectHandler(HTTPRedirectHandler):
    """Laisse le service appliquer lui-même la limite de redirections."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class UrllibHttpTransport:
    """Transport de production fondé sur la bibliothèque standard."""

    def __init__(self):
        self._opener = build_opener(_NoRedirectHandler())

    def request(self, url, timeout):
        """Effectue un GET léger sans suivre automatiquement les redirections."""
        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.1",
                "User-Agent": "ReunionWiki-LinkChecker/1.0",
            },
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                return HttpResponse(response.status, response.headers)
        except HTTPError as error:
            return HttpResponse(error.code, error.headers)
        except (socket.timeout, TimeoutError) as error:
            raise HttpTimeoutError(str(error)) from error
        except URLError as error:
            reason = error.reason
            if isinstance(reason, (ssl.CertificateError, ssl.SSLCertVerificationError)):
                raise InvalidCertificateError(str(reason)) from error
            if isinstance(reason, (socket.timeout, TimeoutError)):
                raise HttpTimeoutError(str(reason)) from error
            raise HttpCheckError(str(reason)) from error


def _resolve_host(hostname):
    """Retourne toutes les adresses résolues pour un nom d'hôte."""
    try:
        return {
            item[4][0]
            for item in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        }
    except socket.gaierror as error:
        raise HttpCheckError(str(error)) from error


def _validate_public_url(url, resolver):
    """Bloque les schémas non HTTP et les destinations réseau non publiques."""
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise UnsafeUrlError("URL invalide.") from error

    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeUrlError("Seules les URL HTTP et HTTPS sont autorisées.")
    if parsed.username or parsed.password:
        raise UnsafeUrlError("Les identifiants intégrés dans une URL sont interdits.")
    if port is not None and not 1 <= port <= 65535:
        raise UnsafeUrlError("Port réseau invalide.")

    addresses = resolver(parsed.hostname)
    if not addresses:
        raise HttpCheckError("Le nom d'hôte ne peut pas être résolu.")
    for address in addresses:
        try:
            if not ipaddress.ip_address(address).is_global:
                raise UnsafeUrlError("La destination réseau n'est pas publique.")
        except ValueError as error:
            raise UnsafeUrlError("Adresse réseau invalide.") from error


def _result(decision, requested_url, final_url, status_code, reason, redirect_count):
    return HttpCheckResult(
        decision=decision,
        requested_url=requested_url,
        final_url=final_url,
        status_code=status_code,
        reason=reason,
        redirect_count=redirect_count,
    )


def check_url(url, transport=None, resolver=None, timeout=5, max_redirects=5):
    """Contrôle une URL et classe le résultat selon RM-SITE-011.

    Le transport et le résolveur sont injectables afin que les tests n'utilisent
    jamais Internet.
    """
    transport = transport or UrllibHttpTransport()
    resolver = resolver or _resolve_host
    requested_url = url
    current_url = url
    visited = set()
    redirect_count = 0

    while True:
        if current_url in visited:
            return _result(
                BLOCKED,
                requested_url,
                current_url,
                None,
                "Boucle de redirection détectée.",
                redirect_count,
            )
        visited.add(current_url)

        try:
            _validate_public_url(current_url, resolver)
            response = transport.request(current_url, timeout)
        except UnsafeUrlError as error:
            return _result(BLOCKED, requested_url, current_url, None, str(error), redirect_count)
        except InvalidCertificateError:
            return _result(
                BLOCKED,
                requested_url,
                current_url,
                None,
                "Certificat HTTPS invalide.",
                redirect_count,
            )
        except (HttpTimeoutError, HttpCheckError):
            return _result(
                TEMPORARY_ERROR,
                requested_url,
                current_url,
                None,
                "Erreur réseau temporaire.",
                redirect_count,
            )

        status = response.status_code
        if 200 <= status <= 299:
            return _result(
                ACCESSIBLE,
                requested_url,
                current_url,
                status,
                "Le site répond correctement.",
                redirect_count,
            )

        if status in REDIRECT_STATUSES:
            location = response.headers.get("Location")
            if not location:
                return _result(
                    BLOCKED,
                    requested_url,
                    current_url,
                    status,
                    "Redirection sans destination.",
                    redirect_count,
                )
            redirect_count += 1
            if redirect_count > max_redirects:
                return _result(
                    BLOCKED,
                    requested_url,
                    current_url,
                    status,
                    "Plus de cinq redirections.",
                    redirect_count,
                )
            current_url = urljoin(current_url, location)
            continue

        if status in {401, 403}:
            return _result(
                MANUAL_REVIEW,
                requested_url,
                current_url,
                status,
                "Le serveur exige une vérification manuelle.",
                redirect_count,
            )
        if status in {404, 410}:
            return _result(
                INACCESSIBLE,
                requested_url,
                current_url,
                status,
                "Le site est introuvable ou n'existe plus.",
                redirect_count,
            )
        if status == 429 or status >= 500:
            return _result(
                TEMPORARY_ERROR,
                requested_url,
                current_url,
                status,
                "Le serveur rencontre un problème temporaire.",
                redirect_count,
            )
        return _result(
            BLOCKED,
            requested_url,
            current_url,
            status,
            f"Réponse HTTP non publiable ({status}).",
            redirect_count,
        )
