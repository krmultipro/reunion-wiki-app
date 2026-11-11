# -*- coding: utf-8 -*-
"""Orchestration des contrôles obligatoires avant publication d'un site."""

from dataclasses import dataclass
from datetime import datetime, timezone

from flask import current_app

from ..repositories import site_editorial_repository, site_http_repository, site_repository
from . import site_http_service, site_lifecycle_service
from .site_data_validation import publication_data_error


@dataclass(frozen=True)
class PublicationAttempt:
    """Décision rendue à une route après le contrôle HTTP."""

    published: bool
    message: str
    category: str
    manual_check_id: int | None = None


def _check_url(url):
    checker = current_app.config.get("SITE_HTTP_CHECKER")
    if checker:
        return checker(url)
    return site_http_service.check_url(
        url,
        timeout=current_app.config.get("SITE_HTTP_TIMEOUT_SECONDS", 5),
        max_redirects=current_app.config.get("SITE_HTTP_MAX_REDIRECTS", 5),
    )


def _now_sql():
    clock = current_app.config.get("SITE_CLOCK")
    moment = clock() if clock else datetime.now(timezone.utc)
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def review_and_attempt_publication(
    site_id, reviewed_url, criterion, note, evidence_url, admin_username,
    new_publication=False,
):
    """Store an explicit editorial decision and continue only when approved."""
    site = site_repository.get_site_by_id(site_id)
    if not site or not site_lifecycle_service.can_transition(site["status"], "valide"):
        return PublicationAttempt(False, "Ce site ne peut pas être publié depuis son statut actuel.", "error")
    if site["lien"] != reviewed_url:
        return PublicationAttempt(False, "L'URL a changé. Vérifiez à nouveau le site.", "error")
    if criterion not in (*site_editorial_repository.APPROVED_CRITERIA, "no_link"):
        return PublicationAttempt(False, "Choisissez une décision éditoriale valide.", "error")
    if not site_editorial_repository.record_review(
        site_id, reviewed_url, criterion, note, evidence_url, admin_username,
    ):
        return PublicationAttempt(False, "Le site a changé. Recommencez la vérification.", "error")
    if criterion == "no_link":
        return PublicationAttempt(
            False, "Publication refusée : aucun lien réel avec La Réunion constaté.", "warning",
        )
    return attempt_publication(site_id, admin_username, new_publication=new_publication)


def attempt_publication(site_id, admin_username, new_publication=False):
    """Contrôle l'URL puis publie, bloque ou demande une revue humaine."""
    site = site_repository.get_site_by_id(site_id)
    if not site:
        return PublicationAttempt(False, "Proposition introuvable.", "error")
    if not site_lifecycle_service.can_transition(site["status"], "valide"):
        return PublicationAttempt(False, "Transition de statut non autorisée.", "error")
    if new_publication and site["status"] != "archived":
        return PublicationAttempt(False, "La nouvelle publication exige un site archivé.", "error")
    if not site_editorial_repository.latest_approval_matches_for_site(site_id, site["lien"]):
        return PublicationAttempt(False, "Confirmez d'abord le lien du site avec La Réunion.", "error")

    issue = publication_data_error(site) or site_repository.get_publication_issue(site_id)
    if issue:
        return PublicationAttempt(False, issue, 'error')

    result = _check_url(site["lien"])
    check_id = site_http_repository.record_check(
        site_id, result, admin_username, new_publication=new_publication
    )

    if result.decision == site_http_service.ACCESSIBLE:
        with site_repository.site_write_transaction() as connection:
            stored = site_repository.get_stored_site(connection, site_id)
            if not stored or publication_data_error(stored):
                return PublicationAttempt(False, "Les données du site ont changé ou sont invalides. Vérifiez à nouveau la fiche.", "error")
            updated = site_repository.apply_publication(
                connection, site_id, admin_username, _now_sql(), new_publication=new_publication
            )
        if updated:
            return PublicationAttempt(True, "Site contrôlé et publié.", "success")
        return PublicationAttempt(False, "La publication a échoué.", "error")

    if result.decision == site_http_service.MANUAL_REVIEW:
        return PublicationAttempt(
            False,
            "Le site bloque le contrôle automatique : une vérification manuelle est requise.",
            "warning",
            manual_check_id=check_id,
        )
    if result.decision == site_http_service.TEMPORARY_ERROR:
        return PublicationAttempt(
            False,
            "Le site est temporairement indisponible. Son statut reste inchangé pour un nouvel essai.",
            "warning",
        )
    return PublicationAttempt(False, result.reason, "error")


def get_manual_review(check_id, site_id):
    """Charge une revue manuelle encore utilisable."""
    review = site_http_repository.get_manual_review(check_id, site_id)
    if review and review["requested_url"] == review["current_url"]:
        return review
    return None


def confirm_manual_publication(site_id, check_id, admin_username, note):
    """Confirme une revue humaine liée à l'URL exacte contrôlée."""
    cleaned_note = (note or "").strip()
    if not cleaned_note:
        return False
    with site_repository.site_write_transaction() as connection:
        stored = site_repository.get_stored_site(connection, site_id)
        if not stored or publication_data_error(stored):
            return False
        return site_http_repository.confirm_manual_review(
            check_id, site_id, admin_username, cleaned_note, _now_sql(),
            connection=connection,
        )
