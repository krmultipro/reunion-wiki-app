"""Identité pure des URL partagée par services et contraintes de persistance."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMETERS = {
    "fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid",
}


class DuplicateSiteUrlError(ValueError):
    """Signale qu'une URL équivalente existe déjà."""


def normalize_site_url(value: str) -> str:
    """Produit une URL stable sans fragment ni paramètres publicitaires."""
    value = (value or "").strip()
    if not value:
        return value
    if not value.lower().startswith(("http://", "https://")):
        value = "https://" + value

    parts = urlsplit(value)
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    try:
        port = parts.port
    except ValueError:
        return value
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname

    path = parts.path
    if path == "/":
        path = ""
    elif path.endswith("/"):
        path = path.rstrip("/")

    kept_query = []
    for key, item_value in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in TRACKING_PARAMETERS:
            continue
        kept_query.append((key, item_value))

    return urlunsplit((scheme, netloc, path, urlencode(kept_query, doseq=True), ""))


def comparison_key(value: str) -> tuple[str, str, str]:
    """Retourne une clé ignorant le protocole mais conservant la casse du chemin."""
    parts = urlsplit(normalize_site_url(value))
    return parts.netloc, parts.path, parts.query


def base_domain(value: str) -> str:
    """Retourne le domaine en ignorant uniquement le préfixe ``www``."""
    hostname = (urlsplit(normalize_site_url(value)).hostname or "").lower()
    return hostname[4:] if hostname.startswith("www.") else hostname


def urls_are_equivalent(first: str, second: str, redirected_to: str | None = None) -> bool:
    """Compare deux URL, avec confirmation facultative d'une redirection ``www``."""
    first_key = comparison_key(first)
    second_key = comparison_key(second)
    if first_key == second_key:
        return True
    if base_domain(first) != base_domain(second):
        return False
    first_parts = urlsplit(normalize_site_url(first))
    second_parts = urlsplit(normalize_site_url(second))
    if first_parts.path != second_parts.path or first_parts.query != second_parts.query:
        return False
    return redirected_to is not None and comparison_key(redirected_to) in {first_key, second_key}


