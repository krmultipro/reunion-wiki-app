# -*- coding: utf-8 -*-

import os
from datetime import datetime
from urllib.parse import urlparse

from flask import current_app

from social_guides import SOCIAL_GUIDES

from ..repositories import (
    content_repository,
    site_repository,
    talent_category_repository,
    talent_repository,
)
from ..utils import slugify
from . import image_storage


STATUSES = [
    ("draft", "Brouillon"),
    ("published", "Publié"),
    ("archived", "Archivé"),
]
STATUS_KEYS = {key for key, _label in STATUSES}
ENTITY_TYPES = [
    ("person", "Personne"),
    ("duo", "Duo"),
    ("group", "Groupe"),
    ("youtube_channel", "Chaîne YouTube"),
    ("media", "Média"),
    ("association", "Association"),
    ("podcast", "Podcast"),
]
ENTITY_TYPE_KEYS = {key for key, _label in ENTITY_TYPES}
ENTITY_TYPE_LABELS = {key: label for key, label in ENTITY_TYPES}
SOCIAL_LINK_DEFINITIONS = (
    ("instagram_url", "Instagram", "Instagram"),
    ("youtube_url", "YouTube", "YouTube"),
    ("tiktok_url", "TikTok", "TikTok"),
    ("facebook_url", "Facebook", "Facebook"),
    ("website_url", "Site web", "Site web"),
)
DEFAULT_TALENT_IMAGE = "icons/icon-192x192.png"
MAX_LENGTHS = {
    "name": 160,
    "slug": 180,
    "description": 500,
    "image": 255,
    "instagram_url": 255,
    "youtube_url": 255,
    "tiktok_url": 255,
    "facebook_url": 255,
    "website_url": 255,
}
URL_FIELDS = ("instagram_url", "youtube_url", "tiktok_url", "facebook_url", "website_url")


def _now_sql():
    """Retourne l'horodatage courant au format texte SQLite.

    Returns:
        str:
            Date UTC au format `YYYY-MM-DD HH:MM:SS`.
    """

    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _clean_text(value, max_length=None):
    """Nettoie une valeur texte issue d'un formulaire ou d'un import.

    Args:
        value (str | None): Valeur brute.
        max_length (int | None): Longueur maximale conservée.

    Returns:
        str:
            Texte nettoyé.
    """

    cleaned = (value or "").strip()
    return cleaned


def _clean_optional_text(value, max_length=None):
    """Nettoie un texte optionnel et retourne None si vide.

    Args:
        value (str | None): Valeur brute.
        max_length (int | None): Longueur maximale conservée.

    Returns:
        str | None:
            Texte nettoyé ou None.
    """

    cleaned = _clean_text(value, max_length)
    return cleaned or None


def _clean_display_order(value):
    """Normalise l'ordre d'affichage manuel.

    Args:
        value: Valeur brute convertible en entier.

    Returns:
        int:
            Ordre d'affichage positif ou nul.
    """

    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


def _clean_optional_int(value):
    """Normalise un identifiant optionnel.

    Args:
        value: Valeur brute convertible en entier.

    Returns:
        int | None:
            Identifiant positif, ou None si la valeur est vide/invalide.
    """

    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _is_valid_http_url(value):
    """Indique si une URL optionnelle est en HTTP ou HTTPS.

    Args:
        value (str | None): URL à vérifier.

    Returns:
        bool:
            True si l'URL est vide ou valide.
    """

    if not value:
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _remove_uploaded_image(relative_path):
    """Supprime une image uploadée récemment si l'écriture DB échoue.

    Args:
        relative_path (str | None): Chemin relatif retourné par image_storage.

    Returns:
        None
    """

    if not relative_path:
        return

    upload_root = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    relative_upload_path = relative_path.removeprefix("uploads/").lstrip("/")
    absolute_path = os.path.abspath(os.path.join(upload_root, relative_upload_path))
    if os.path.commonpath([upload_root, absolute_path]) != upload_root:
        return
    try:
        os.remove(absolute_path)
    except OSError:
        pass


def generate_unique_slug(name, slug_input=None, exclude_id=None):
    """Génère un slug unique pour un talent.

    Args:
        name (str): Nom du talent.
        slug_input (str | None): Slug proposé.
        exclude_id (int | None): Identifiant à ignorer en édition.

    Returns:
        str:
            Slug unique disponible.
    """

    base = slugify(slug_input or "") or slugify(name or "") or "talent"
    candidate = base
    suffix = 2
    while talent_repository.slug_exists(candidate, exclude_id):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def _get_city_by_id(city_id):
    """Récupère une ville par identifiant via les repositories existants.

    Args:
        city_id (int | None): Identifiant de ville.

    Returns:
        sqlite3.Row | None:
            Ville trouvée, ou None.
    """

    if not city_id:
        return None

    for city in site_repository.get_admin_city_filters():
        row = site_repository.get_city_by_slug(city["slug"])
        if row and row["id"] == city_id:
            return row
    return None


def _resolve_category_reference(data):
    """Résout la catégorie obligatoire d'un talent vers category_id.

    Args:
        data (dict): Données nettoyées du talent.

    Returns:
        list[str]:
            Messages d'erreur de résolution.
    """

    category_id = _clean_optional_int(data.get("category_id"))
    if category_id:
        category = talent_category_repository.get_by_id(category_id)
        if not category:
            return ["La catégorie sélectionnée est introuvable."]
        data["category_id"] = category["id"]
        return []

    return ["La catégorie est obligatoire et doit correspondre à une catégorie existante."]


def _resolve_city_reference(data):
    """Résout la commune optionnelle d'un talent vers city_id.

    Args:
        data (dict): Données nettoyées du talent.

    Returns:
        list[str]:
            Messages d'erreur de résolution.
    """

    city_id = _clean_optional_int(data.get("city_id"))
    if city_id:
        city = _get_city_by_id(city_id)
        if not city:
            return ["La commune sélectionnée est introuvable."]
        data["city_id"] = city["id"]
        return []

    data["city_id"] = None
    return []


def _resolve_taxonomy_references(data):
    """Résout les références taxonomiques utilisées par les écritures.

    Args:
        data (dict): Données nettoyées du talent.

    Returns:
        list[str]:
            Messages d'erreur de résolution.
    """

    errors = []
    errors.extend(_resolve_category_reference(data))
    errors.extend(_resolve_city_reference(data))
    return errors


def _validate_existing_taxonomy_references(talent):
    """Valide les références déjà stockées sur un talent.

    Args:
        talent (sqlite3.Row): Talent récupéré depuis le repository.

    Returns:
        list[str]:
            Messages d'erreur de validation.
    """

    errors = []
    category_id = talent["category_id"]
    if not category_id or not talent_category_repository.get_by_id(category_id):
        errors.append("La catégorie associée au talent est introuvable.")

    city_id = talent["city_id"]
    if city_id and not _get_city_by_id(city_id):
        errors.append("La commune associée au talent est introuvable.")

    return errors


def validate_talent_data(data, require_category=True):
    """Valide les champs métier minimaux d'un talent.

    Args:
        data (dict): Données nettoyées du talent.
        require_category (bool): Vérifie la présence d'une catégorie résolue.

    Returns:
        list[str]:
            Messages d'erreur, vide si les données sont valides.
    """

    errors = []
    if not data["name"]:
        errors.append("Le nom est obligatoire.")
    if not data["slug"]:
        errors.append("Le slug est obligatoire.")
    if require_category and not data.get("category_id"):
        errors.append("La catégorie est obligatoire.")
    if not data["description"]:
        errors.append("La description est obligatoire.")
    if data["status"] not in STATUS_KEYS:
        errors.append("Statut invalide.")
    if data["entity_type"] not in ENTITY_TYPE_KEYS:
        errors.append("Type d'entité invalide.")

    for field, max_length in MAX_LENGTHS.items():
        value = data.get(field)
        if value and len(value) > max_length:
            errors.append(f"{field} ne doit pas dépasser {max_length} caractères.")

    for field in URL_FIELDS:
        if not _is_valid_http_url(data.get(field)):
            errors.append(f"{field} doit être une URL http ou https valide.")

    return errors


def normalize_talent_data(data, existing=None, talent_id=None):
    """Prépare les données d'un talent avant écriture.

    Args:
        data (dict): Données brutes du talent.
        existing (sqlite3.Row | None): Talent existant en cas d'édition.
        talent_id (int | None): Identifiant ignoré pour l'unicité du slug.

    Returns:
        dict:
            Données nettoyées prêtes pour le repository.
    """

    name = _clean_text(data.get("name"), 160)
    status = _clean_text(data.get("status") or "draft", 40)
    entity_type = _clean_text(data.get("entity_type") or "person", 40)
    published_at = existing["published_at"] if existing else None
    if status == "published" and not published_at:
        published_at = _now_sql()

    return {
        "name": name,
        "slug": generate_unique_slug(name, data.get("slug"), exclude_id=talent_id),
        "entity_type": entity_type,
        "category_id": _clean_optional_int(data.get("category_id")),
        "city_id": _clean_optional_int(data.get("city_id")),
        "description": _clean_text(data.get("description"), 500),
        "bio": _clean_optional_text(data.get("bio")),
        "image": _clean_optional_text(data.get("image"), 255),
        "instagram_url": _clean_text(data.get("instagram_url"), 255),
        "youtube_url": _clean_text(data.get("youtube_url"), 255),
        "tiktok_url": _clean_text(data.get("tiktok_url"), 255),
        "facebook_url": _clean_text(data.get("facebook_url"), 255),
        "website_url": _clean_text(data.get("website_url"), 255),
        "status": status,
        "display_order": _clean_display_order(data.get("display_order")),
        "published_at": published_at,
    }


def save_talent(data, image_file=None, talent_id=None):
    """Crée ou met à jour un talent en appliquant les règles métier.

    Args:
        data (dict): Données du talent.
        image_file: FileStorage optionnel pour l'image du talent.
        talent_id (int | None): Identifiant si mise à jour, None si création.

    Returns:
        tuple[int | None, list[str]]:
            Identifiant du talent enregistré, ou None, et erreurs éventuelles.
    """

    existing = talent_repository.get_by_id(talent_id) if talent_id else None
    if talent_id and not existing:
        return None, ["Talent introuvable."]

    cleaned = normalize_talent_data(data, existing=existing, talent_id=talent_id)
    cleaned["image"] = existing["image"] if existing else cleaned["image"]
    errors = validate_talent_data(cleaned, require_category=False)
    errors.extend(_resolve_taxonomy_references(cleaned))
    if errors:
        return None, errors

    uploaded_image = None
    if image_file is not None and getattr(image_file, "filename", ""):
        try:
            cleaned["image"] = image_storage.save_upload(image_file, namespace="talents")
            uploaded_image = cleaned["image"]
        except image_storage.ImageStorageError as exc:
            return None, [str(exc)]

    try:
        if talent_id:
            talent_repository.update(
                talent_id,
                cleaned["name"],
                cleaned["slug"],
                cleaned["entity_type"],
                cleaned["category_id"],
                cleaned["city_id"],
                cleaned["description"],
                cleaned["bio"],
                cleaned["image"],
                cleaned["instagram_url"],
                cleaned["youtube_url"],
                cleaned["tiktok_url"],
                cleaned["facebook_url"],
                cleaned["website_url"],
                cleaned["status"],
                cleaned["display_order"],
                cleaned["published_at"],
            )
            return talent_id, []

        new_id = talent_repository.insert(
            cleaned["name"],
            cleaned["slug"],
            cleaned["entity_type"],
            cleaned["category_id"],
            cleaned["city_id"],
            cleaned["description"],
            cleaned["bio"],
            cleaned["image"],
            cleaned["instagram_url"],
            cleaned["youtube_url"],
            cleaned["tiktok_url"],
            cleaned["facebook_url"],
            cleaned["website_url"],
            cleaned["status"],
            cleaned["display_order"],
            cleaned["published_at"],
        )
        return new_id, []
    except Exception:
        _remove_uploaded_image(uploaded_image)
        raise


def publish(talent_id):
    """Publie un talent existant.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        tuple[bool, list[str]]:
            Succès et erreurs éventuelles.
    """

    row = talent_repository.get_by_id(talent_id)
    if not row:
        return False, ["Talent introuvable."]

    errors = _validate_existing_taxonomy_references(row)
    errors.extend(validate_talent_data(
        {
            "name": row["name"],
            "slug": row["slug"],
            "entity_type": row["entity_type"],
            "category_id": row["category_id"],
            "city_id": row["city_id"],
            "description": row["description"],
            "image": row["image"],
            "instagram_url": row["instagram_url"],
            "youtube_url": row["youtube_url"],
            "tiktok_url": row["tiktok_url"],
            "facebook_url": row["facebook_url"],
            "website_url": row["website_url"],
            "status": "published",
        }
    ))
    if errors:
        return False, errors

    published_at = row["published_at"] or _now_sql()
    talent_repository.update_status(talent_id, "published", published_at)
    return True, []


def unpublish(talent_id):
    """Repasse un talent publié en brouillon.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        bool:
            True si le talent existait et a été mis à jour.
    """

    row = talent_repository.get_by_id(talent_id)
    if not row:
        return False
    talent_repository.update_status(talent_id, "draft", row["published_at"])
    return True


def archive(talent_id):
    """Archive un talent.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        bool:
            True si le talent existait et a été mis à jour.
    """

    row = talent_repository.get_by_id(talent_id)
    if not row:
        return False
    talent_repository.update_status(talent_id, "archived", row["published_at"])
    return True


def delete_talent(talent_id):
    """Supprime définitivement un talent.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        bool:
            True si une ligne a été supprimée.
    """

    return talent_repository.delete(talent_id) > 0


def get_talent(talent_id):
    """Récupère un talent par identifiant pour l'administration.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        sqlite3.Row | None:
            Talent trouvé ou None.
    """

    return talent_repository.get_by_id(talent_id)


def get_public_talent(slug):
    """Récupère un talent public pour une future page profil.

    Args:
        slug (str): Slug demandé.

    Returns:
        sqlite3.Row | None:
            Talent public ou None.
    """

    return talent_repository.get_published_by_slug(slug)


def get_public_talent_detail_context(slug):
    """Prépare le contexte public d'une fiche créateur.

    Args:
        slug (str): Slug public du talent.

    Returns:
        dict | None:
            Contexte de rendu, ou None si le talent publié n'existe pas.
    """

    talent = get_public_talent(slug)
    if not talent:
        return None

    social_links = _build_social_links(talent)
    similar_rows = talent_repository.list_similar_published(
        talent["id"],
        talent["category_id"],
        talent["entity_type"],
        limit=3,
    )
    seo = _build_talent_seo(talent)
    guide_slugs = [guide["slug"] for guide in SOCIAL_GUIDES.values()]
    published_guide_slugs = {
        row["slug"] for row in content_repository.get_published_by_slugs(guide_slugs)
    }
    social_guide_links = []
    for key, guide in SOCIAL_GUIDES.items():
        if talent[guide["field"]] and guide["slug"] in published_guide_slugs:
            social_guide_links.append({
                "key": key,
                "slug": guide["slug"],
                "platform": guide["platform"],
                "label": guide["profile_link_label"],
            })

    return {
        "talent": talent,
        "image": talent["image"] or DEFAULT_TALENT_IMAGE,
        "entity_type_label": _entity_type_label(talent["entity_type"]),
        "social_links": social_links,
        "primary_social": _primary_social_link(social_links),
        "secondary_social_links": social_links[1:],
        "similar_talents": [build_public_card(row) for row in similar_rows],
        "social_guide_links": social_guide_links,
        "seo_title": seo["title"],
        "seo_description": seo["description"],
    }


def list_public_talents(limit=None, offset=0):
    """Retourne les talents publics pour une future liste.

    Args:
        limit (int | None): Nombre maximum de talents.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Talents publics.
    """

    return talent_repository.list_published(limit=limit, offset=offset)


def get_public_social_creator_cards(network_key):
    """Prépare les fiches publiques associées à un réseau social.

    Args:
        network_key (str): Clé déclarée dans ``SOCIAL_GUIDES``.

    Returns:
        list[dict]:
            Cartes publiques prêtes pour la page SEO du réseau.
    """

    guide = SOCIAL_GUIDES.get(network_key)
    if not guide:
        return []
    talents = talent_repository.list_published_with_social_url(guide["field"])
    return [build_public_card(talent) for talent in talents]


def get_public_social_guides():
    """Retourne les sélections sociales publiées pour le hub créateurs.

    Returns:
        list[dict]:
            Guides publiés avec leurs libellés et nombre de profils.
    """

    guide_slugs = [guide["slug"] for guide in SOCIAL_GUIDES.values()]
    published_pages = {
        row["slug"]: row
        for row in content_repository.get_published_by_slugs(guide_slugs)
    }
    guides = []
    for key, guide in SOCIAL_GUIDES.items():
        page = published_pages.get(guide["slug"])
        if not page:
            continue
        total = talent_repository.count_published_with_social_url(guide["field"])
        guides.append({
            "key": key,
            "slug": guide["slug"],
            "platform": guide["platform"],
            "title": page["title"] or guide["hub_title"],
            "description": page["summary"] or guide["hub_description"],
            "total": total,
        })
    return guides


def get_public_social_guide(network_key):
    """Retourne un guide social publié, notamment pour une mise en avant.

    Args:
        network_key (str): Clé déclarée dans ``SOCIAL_GUIDES``.

    Returns:
        dict | None:
            Guide publié et son total de profils, ou None.
    """

    guide = SOCIAL_GUIDES.get(network_key)
    if not guide:
        return None
    page = content_repository.get_published_by_slug(guide["slug"])
    if not page:
        return None
    total = talent_repository.count_published_with_social_url(guide["field"])
    return {
        "key": network_key,
        "slug": guide["slug"],
        "platform": guide["platform"],
        "title": page["title"] or guide["hub_title"],
        "description": page["summary"] or guide["hub_description"],
        "total": total,
    }


def list_public_talents_by_category(category, limit=None, offset=0):
    """Retourne les talents publics d'une catégorie.

    Args:
        category (str): Catégorie demandée.
        limit (int | None): Nombre maximum de talents.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Talents publics de la catégorie.
    """

    cleaned_category = _clean_text(category, 120)
    if not cleaned_category:
        return []
    return talent_repository.list_published_by_category(cleaned_category, limit=limit, offset=offset)


def list_public_categories():
    """Retourne les catégories ayant au moins un talent public.

    Returns:
        list[sqlite3.Row]:
            Catégories représentées et leur total.
    """

    return talent_repository.list_categories()


def _entity_type_label(entity_type):
    """Retourne le libellé public d'un type d'entité talent.

    Args:
        entity_type (str): Clé de type d'entité.

    Returns:
        str:
            Libellé lisible par l'utilisateur.
    """

    return ENTITY_TYPE_LABELS.get(entity_type, "Talent réunionnais")


def _build_social_links(talent):
    """Construit la liste des réseaux disponibles pour un talent.

    Args:
        talent (sqlite3.Row): Talent publié.

    Returns:
        list[dict]:
            Liens sociaux disponibles dans l'ordre de priorité.
    """

    links = []
    for field, label, aria_label in SOCIAL_LINK_DEFINITIONS:
        url = talent[field]
        if url:
            links.append({
                "field": field,
                "label": label,
                "aria_label": aria_label,
                "url": url,
            })
    return links


def _primary_social_link(social_links):
    """Retourne le réseau principal selon l'ordre de priorité éditorial.

    Args:
        social_links (list[dict]): Liens sociaux disponibles.

    Returns:
        dict | None:
            Premier lien disponible, ou None.
    """

    return social_links[0] if social_links else None


def _truncate_text(value, max_length=155):
    """Raccourcit un texte pour une meta description.

    Args:
        value (str | None): Texte source.
        max_length (int): Longueur maximale.

    Returns:
        str:
            Texte raccourci proprement.
    """

    text = " ".join((value or "").split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def _build_talent_seo(talent):
    """Construit les métadonnées SEO d'une fiche créateur.

    Args:
        talent (sqlite3.Row): Talent publié.

    Returns:
        dict:
            Titre et description SEO.
    """

    category = talent["category"] or "création réunionnaise"
    city = talent["city"] or "La Réunion"
    entity_label = _entity_type_label(talent["entity_type"]).lower()
    title = f"{talent['name']} - {category} à {city} | Réunion Wiki"
    fallback = (
        f"Découvrez {talent['name']}, {entity_label} de La Réunion référencé "
        f"dans le guide des créateurs réunionnais."
    )
    description = _truncate_text(talent["description"] or talent["bio"] or fallback)
    return {"title": title, "description": description}


def build_public_card(talent):
    """Prépare un talent publié pour l'affichage dans l'index public.

    Args:
        talent (sqlite3.Row): Ligne de talent publiée.

    Returns:
        dict:
            Données minimales attendues par le template public.
    """

    return {
        "slug": talent["slug"],
        "image": talent["image"] or DEFAULT_TALENT_IMAGE,
        "name": talent["name"],
        "category": talent["category"] or "Talent réunionnais",
        "city": talent["city"] or "La Réunion",
        "description": talent["description"] or "",
    }


def get_public_index_context():
    """Prépare les données publiques de la page des créateurs réunionnais.

    Returns:
        dict:
            Dictionnaire contenant les talents publiés et les statistiques.
    """

    talents = list_public_talents()
    cards = [build_public_card(talent) for talent in talents]
    category_count = len({talent["category"] for talent in talents if talent["category"]})
    city_count = len({talent["city"] for talent in talents if talent["city"]})

    return {
        "creators": cards,
        "social_guides": get_public_social_guides(),
        "stats": {
            "creator_count": len(cards),
            "category_count": category_count,
            "city_count": city_count,
        },
    }


def get_admin_list(status=None, category=None, q=None, sort="recent", page=1, per_page=20):
    """Prépare une liste paginée de talents pour une future interface admin.

    Args:
        status (str | None): Filtre par statut.
        category (str | None): Filtre par catégorie.
        q (str | None): Recherche texte.
        sort (str): Clé de tri.
        page (int): Page demandée.
        per_page (int): Taille de page.

    Returns:
        dict:
            Items, page courante, nombre total de pages et total.
    """

    status_filter = status if status in STATUS_KEYS else None
    category_filter = _clean_optional_text(category, 120)
    search = _clean_optional_text(q, 120)

    total = talent_repository.count_for_admin(status_filter, category_filter, search)["total"]
    total_pages = max((total + per_page - 1) // per_page, 1)
    page = max(min(int(page or 1), total_pages), 1)
    offset = (page - 1) * per_page

    items = talent_repository.list_for_admin(
        status_filter, category_filter, search, sort, per_page, offset
    )
    return {"items": items, "page": page, "total_pages": total_pages, "total": total}
