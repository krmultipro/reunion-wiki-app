# -*- coding: utf-8 -*-
"""Service métier des catégories de créateurs."""

from ..repositories import talent_category_repository
from ..utils import slugify


MAX_NAME_LENGTH = 120
MAX_SLUG_LENGTH = 160


def _clean_text(value, max_length=None):
    """Nettoie une valeur texte issue d'un formulaire.

    Args:
        value (str | None): Valeur brute.
        max_length (int | None): Longueur maximale conservée.

    Returns:
        str:
            Texte nettoyé.
    """

    cleaned = (value or "").strip()
    if max_length:
        return cleaned[:max_length]
    return cleaned


def _slug_exists(slug, exclude_id=None):
    """Indique si un slug de catégorie créateur existe déjà.

    Args:
        slug (str): Slug à vérifier.
        exclude_id (int | None): Identifiant à ignorer en édition.

    Returns:
        bool:
            True si le slug est déjà pris.
    """

    if exclude_id:
        return talent_category_repository.get_by_slug_excluding_id(slug, exclude_id) is not None
    return talent_category_repository.get_by_slug(slug) is not None


def _name_exists(name, exclude_id=None):
    """Indique si un nom de catégorie créateur existe déjà.

    Args:
        name (str): Nom à vérifier.
        exclude_id (int | None): Identifiant à ignorer en édition.

    Returns:
        bool:
            True si le nom est déjà utilisé.
    """

    expected = (name or "").strip().casefold()
    if not expected:
        return False

    for category in talent_category_repository.list_all():
        if exclude_id and category["id"] == exclude_id:
            continue
        if (category["name"] or "").strip().casefold() == expected:
            return True
    return False


def generate_unique_slug(name, slug_input=None, exclude_id=None):
    """Génère un slug unique pour une catégorie créateur.

    Args:
        name (str): Nom de la catégorie.
        slug_input (str | None): Slug proposé.
        exclude_id (int | None): Identifiant à ignorer en édition.

    Returns:
        str:
            Slug unique disponible.
    """

    base = slugify(slug_input or "") or slugify(name or "") or "categorie-createur"
    candidate = base[:MAX_SLUG_LENGTH]
    suffix = 2
    while _slug_exists(candidate, exclude_id=exclude_id):
        suffix_text = f"-{suffix}"
        candidate = f"{base[:MAX_SLUG_LENGTH - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return candidate


def _validate_category_data(data, category_id=None):
    """Valide les données métier d'une catégorie créateur.

    Args:
        data (dict): Données nettoyées.
        category_id (int | None): Identifiant courant en édition.

    Returns:
        list[str]:
            Messages d'erreur.
    """

    errors = []
    name = data["name"]
    slug = data["slug"]

    if not name:
        errors.append("Le nom de la catégorie est obligatoire.")
    elif len(name) < 2:
        errors.append("Le nom de la catégorie doit faire au moins 2 caractères.")
    elif len(name) > MAX_NAME_LENGTH:
        errors.append(f"Le nom de la catégorie ne doit pas dépasser {MAX_NAME_LENGTH} caractères.")

    if slug and len(slug) > MAX_SLUG_LENGTH:
        errors.append(f"Le slug ne doit pas dépasser {MAX_SLUG_LENGTH} caractères.")

    if name and _name_exists(name, exclude_id=category_id):
        errors.append("Une catégorie créateur porte déjà ce nom.")

    if slug and _slug_exists(slug, exclude_id=category_id):
        errors.append("Une catégorie créateur utilise déjà ce slug.")

    return errors


def normalize_category_data(data, category_id=None):
    """Prépare les données d'une catégorie créateur avant écriture.

    Args:
        data (dict): Données brutes du formulaire.
        category_id (int | None): Identifiant courant en édition.

    Returns:
        dict:
            Données nettoyées.
    """

    name = _clean_text(data.get("name"), MAX_NAME_LENGTH)
    slug_input = slugify(_clean_text(data.get("slug"), MAX_SLUG_LENGTH))
    return {
        "name": name,
        "slug": slug_input or generate_unique_slug(name, exclude_id=category_id),
    }


def list_categories():
    """Retourne toutes les catégories créateurs.

    Returns:
        list[sqlite3.Row]:
            Catégories triées par nom.
    """

    return talent_category_repository.list_all()


def get_category(category_id):
    """Récupère une catégorie créateur par identifiant.

    Args:
        category_id (int): Identifiant de la catégorie.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None.
    """

    return talent_category_repository.get_by_id(category_id)


def save_category(data, category_id=None):
    """Crée ou met à jour une catégorie créateur.

    Args:
        data (dict): Données de formulaire.
        category_id (int | None): Identifiant en édition, None en création.

    Returns:
        tuple[int | None, list[str]]:
            Identifiant enregistré et erreurs éventuelles.
    """

    existing = talent_category_repository.get_by_id(category_id) if category_id else None
    if category_id and not existing:
        return None, ["Catégorie créateur introuvable."]

    cleaned = normalize_category_data(data, category_id=category_id)
    errors = _validate_category_data(cleaned, category_id=category_id)
    if errors:
        return None, errors

    if category_id:
        talent_category_repository.update(category_id, cleaned["name"], cleaned["slug"])
        return category_id, []

    new_id = talent_category_repository.insert(cleaned["name"], cleaned["slug"])
    return new_id, []


def delete_category(category_id):
    """Supprime une catégorie créateur si elle n'est utilisée par aucun talent.

    Args:
        category_id (int): Identifiant de la catégorie.

    Returns:
        tuple[bool, list[str]]:
            Succès et erreurs éventuelles.
    """

    category = talent_category_repository.get_by_id(category_id)
    if not category:
        return False, ["Catégorie créateur introuvable."]

    usage = talent_category_repository.count_talents_by_category(category_id)["total"]
    if usage > 0:
        return False, ["Impossible de supprimer : des créateurs utilisent encore cette catégorie."]

    talent_category_repository.delete(category_id)
    return True, []
