"""Site status transitions for the administrative workflow."""

from dataclasses import dataclass

from ..repositories import site_refusal_repository, site_repository


ALLOWED_TRANSITIONS = {
    "draft": frozenset({"valide", "archived"}),
    "en_attente": frozenset({"valide", "refuse"}),
    "valide": frozenset({"archived"}),
    "refuse": frozenset({"en_attente"}),
    "archived": frozenset({"valide"}),
}

STATUS_LABELS = {
    "draft": "Brouillon",
    "en_attente": "En attente",
    "valide": "Publié",
    "refuse": "Refusé",
    "archived": "Archivé",
}


@dataclass(frozen=True)
class TransitionResult:
    changed: bool
    message: str
    category: str


def allowed_targets(status):
    """Return the statuses an administrator may choose from the current state."""
    return ALLOWED_TRANSITIONS.get(status, frozenset())


def can_transition(current_status, target_status):
    return target_status in allowed_targets(current_status)


def transition_status(site_id, target_status, refusal_reason=None, admin_username="admin"):
    """Apply a non-publication transition with an optimistic status check."""
    site = site_repository.get_site_by_id(site_id)
    if not site:
        return TransitionResult(False, "Proposition introuvable.", "error")
    current_status = site["status"]
    if not can_transition(current_status, target_status):
        return TransitionResult(False, "Transition de statut non autorisée.", "error")
    if target_status == "valide":
        return TransitionResult(False, "La publication exige une revue éditoriale.", "error")
    if target_status == "refuse":
        try:
            site_refusal_repository.validate_reason(refusal_reason)
        except site_refusal_repository.InvalidRefusalReason as error:
            return TransitionResult(False, str(error), "error")
    if not site_repository.update_site_status(
        site_id, target_status, expected_status=current_status,
        refusal_reason=refusal_reason, admin_username=admin_username,
    ):
        return TransitionResult(False, "Le statut a changé. Réessayez après actualisation.", "error")
    return TransitionResult(True, "Statut mis à jour.", "success")


def edit_status(current_status, requested_status, url_changed=False):
    """Return the stored status and whether publication review is needed."""
    if current_status not in ALLOWED_TRANSITIONS:
        return None, False, "Statut actuel inconnu."
    if requested_status == current_status:
        if current_status == "valide" and url_changed:
            return None, False, "Archivez le site avant de modifier son URL."
        return current_status, False, None
    if not can_transition(current_status, requested_status):
        return None, False, "Transition de statut non autorisée."
    if requested_status == "valide":
        return current_status, True, None
    return requested_status, False, None
