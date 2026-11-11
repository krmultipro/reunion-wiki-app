"""Validated geographic scope for a listed site."""


SITE_SCOPES = ("island", "online")


def validate_location(city_id, scope):
    """Valide une commune, une portée explicite ou une localisation inconnue.

    Args:
        city_id (int | None): Commune choisie pour le site.
        scope (str | None): Portée explicite choisie pour le site.

    Returns:
        str | None: Portée nettoyée à enregistrer.

    Raises:
        ValueError: Choix inconnu ou combinaison commune et portée.
    """
    cleaned_scope = scope or None
    if cleaned_scope not in (None, *SITE_SCOPES):
        raise ValueError("Portée géographique non valide.")
    if city_id is not None and cleaned_scope is not None:
        raise ValueError("Choisissez une commune ou une portée, pas les deux.")
    return cleaned_scope
