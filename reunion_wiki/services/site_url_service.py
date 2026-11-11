"""Normalisation et décisions métier pour les URL des sites."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from ..repositories import site_repository
from ..site_urls import (
    DuplicateSiteUrlError, TRACKING_PARAMETERS, base_domain, comparison_key,
    normalize_site_url, urls_are_equivalent,
)


@dataclass(frozen=True)
class SiteUrlDecision:
    """Résultat de la normalisation et du contrôle de doublon."""

    normalized_url: str
    warning: str | None = None
    duplicate_site_id: int | None = None


def assess_site_url(value: str, exclude_site_id: int | None = None) -> SiteUrlDecision:
    """Normalise une URL, bloque un doublon et signale un domaine déjà connu."""
    normalized = normalize_site_url(value)
    same_domain = False
    for row in site_repository.list_site_urls():
        if exclude_site_id is not None and row["id"] == exclude_site_id:
            continue
        if urls_are_equivalent(normalized, row["lien"]):
            return SiteUrlDecision(normalized, duplicate_site_id=row["id"])
        if base_domain(normalized) == base_domain(row["lien"]):
            same_domain = True
    warning = "Ce domaine existe déjà avec une autre URL ; vérification recommandée." if same_domain else None
    return SiteUrlDecision(normalized, warning=warning)


def prepare_site_url(value: str, exclude_site_id: int | None = None) -> SiteUrlDecision:
    """Valide une URL avant écriture et lève une erreur sur un doublon exact."""
    decision = assess_site_url(value, exclude_site_id=exclude_site_id)
    if decision.duplicate_site_id is not None:
        raise DuplicateSiteUrlError(
            f"Cette URL correspond déjà au site #{decision.duplicate_site_id}."
        )
    return decision


def choose_final_https_url(proposed_url: str, final_url: str) -> str:
    """Conserve une destination finale HTTP(S), en privilégiant sa variante HTTPS."""
    proposed = normalize_site_url(proposed_url)
    final = normalize_site_url(final_url)
    if urlsplit(final).scheme == "https":
        return final
    return proposed
