# -*- coding: utf-8 -*-

import re
from datetime import datetime

from ..repositories import content_repository
from ..utils import slugify
from . import image_storage, talent_service


# Liste fixe des types de contenu pour la V1 (extensible sans migration).
CONTENT_TYPES = [
    ("seo_landing", "Page SEO"),
    ("guide", "Guide"),
    ("personality", "Personnalité"),
    ("creator", "Créateur"),
    ("blog", "Article de blog"),
]
CONTENT_TYPE_KEYS = {key for key, _label in CONTENT_TYPES}
CONTENT_TYPE_LABELS = {key: label for key, label in CONTENT_TYPES}

# Cycle de vie du contenu (distinct du vocabulaire des sites : valide/en_attente).
STATUSES = [
    ("draft", "Brouillon"),
    ("published", "Publié"),
    ("archived", "Archivé"),
]
STATUS_KEYS = {key for key, _label in STATUSES}
STATUS_LABELS = {key: label for key, label in STATUSES}

# Slugs réservés : premiers segments d'URL déjà servis par des routes existantes.
# Un slug de contenu identique serait inaccessible (masqué par la route statique).
RESERVED_SLUGS = {
    "admin", "static", "go", "recherche", "faq", "blog", "villes", "ville",
    "categorie", "tendances", "proposer-site", "mentions-legales",
    "sites-ajoutes-recemment", "sites-les-plus-visites",
    "categories-les-plus-visitees", "createurs-reunionnais",
    "sitemap.xml", "robots.txt", "service-worker.js",
}

# Tags HTML autorisés dans le corps (le reste est neutralisé, contenu conservé).
ALLOWED_HTML_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "ul", "ol", "li",
    "a", "h2", "h3", "h4", "blockquote", "hr",
}


def _now_sql() -> str:
    """Retourne l'horodatage courant au format texte SQLite."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_html(value):
    """Assainit du HTML utilisateur en ne gardant qu'une liste de balises sûres.

    Approche allowlist conservatrice (V1) : supprime les blocs dangereux avec
    leur contenu, retire tous les attributs sauf un `href` sûr sur les liens, et
    neutralise toute balise hors liste en conservant son texte.

    Args:
        value (str | None): HTML brut saisi dans l'admin.

    Returns:
        str | None: HTML nettoyé, ou la valeur d'origine si non textuelle.
    """

    if not isinstance(value, str):
        return value

    value = value.strip()
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)

    # Supprime les éléments dangereux avec leur contenu.
    value = re.sub(
        r"(?is)<(script|style|iframe|object|embed|form|svg|math)[^>]*>.*?</\1>",
        "",
        value,
    )
    # Supprime les balises dangereuses autonomes ou auto-fermantes.
    value = re.sub(
        r"(?is)<(script|style|iframe|object|embed|form|svg|math|link|meta)[^>]*/?>",
        "",
        value,
    )
    # Supprime les commentaires HTML.
    value = re.sub(r"(?s)<!--.*?-->", "", value)

    def _clean_tag(match):
        raw = match.group(0)
        name_match = re.match(r"</?\s*([a-zA-Z0-9]+)", raw)
        if not name_match:
            return ""
        name = name_match.group(1).lower()
        if name not in ALLOWED_HTML_TAGS:
            return ""  # Neutralise la balise, conserve le texte interne.
        if raw.startswith("</"):
            return f"</{name}>"
        if name == "a":
            href_match = (
                re.search(r'href\s*=\s*"([^"]*)"', raw, re.IGNORECASE)
                or re.search(r"href\s*=\s*'([^']*)'", raw, re.IGNORECASE)
            )
            href = href_match.group(1).strip() if href_match else ""
            if href.lower().startswith(("http://", "https://", "/", "mailto:")):
                return f'<a href="{href}" rel="noopener noreferrer">'
            return "<a>"
        return f"<{name}>"

    return re.sub(r"(?s)<[^>]+>", _clean_tag, value)


def generate_unique_slug(title, slug_input, exclude_id=None):
    """Génère un slug unique, non réservé, pour un contenu.

    Args:
        title (str): Titre du contenu (source de repli du slug).
        slug_input (str | None): Slug proposé par l'utilisateur.
        exclude_id (int | None): Identifiant à ignorer lors du test d'unicité.

    Returns:
        str: Slug final unique et publiable.
    """

    base = slugify(slug_input or "") or slugify(title or "") or "page"
    candidate = base
    suffix = 2
    while candidate in RESERVED_SLUGS or content_repository.slug_exists(candidate, exclude_id):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def _publish_errors(title, slug, meta_title, meta_description):
    """Valide les exigences SEO d'une publication (Décision 7).

    Args:
        title (str): Titre.
        slug (str): Slug.
        meta_title (str | None): Méta-titre.
        meta_description (str | None): Méta-description.

    Returns:
        list[str]: Liste des messages d'erreur (vide si publiable).
    """

    errors = []
    if not (title or "").strip():
        errors.append("Le titre est obligatoire pour publier.")
    if not (slug or "").strip():
        errors.append("Le slug est obligatoire pour publier.")
    if not (meta_title or "").strip():
        errors.append("Le meta title est obligatoire pour publier.")
    if not (meta_description or "").strip():
        errors.append("La meta description est obligatoire pour publier.")
    return errors


def save_content(data, image_file=None, content_id=None):
    """Crée ou met à jour un contenu en appliquant toutes les règles métier.

    Args:
        data (dict): Valeurs du formulaire (content_type, title, slug, summary,
            body, meta_title, meta_description, status).
        image_file: FileStorage optionnel pour l'image à la une.
        content_id (int | None): Identifiant si mise à jour, None si création.

    Returns:
        tuple[int | None, list[str]]:
            Identifiant du contenu enregistré (ou None) et liste d'erreurs.
    """

    errors = []

    content_type = (data.get("content_type") or "").strip()
    if content_type not in CONTENT_TYPE_KEYS:
        errors.append("Type de contenu invalide.")

    status = (data.get("status") or "draft").strip()
    if status not in STATUS_KEYS:
        errors.append("Statut invalide.")

    title = (data.get("title") or "").strip()
    if not title:
        errors.append("Le titre est obligatoire.")

    if errors:
        return None, errors

    existing = content_repository.get_by_id(content_id) if content_id else None
    if content_id and not existing:
        return None, ["Contenu introuvable."]

    slug = generate_unique_slug(title, data.get("slug"), exclude_id=content_id)
    summary = (data.get("summary") or "").strip() or None
    body = sanitize_html(data.get("body") or "") or None
    meta_title = (data.get("meta_title") or "").strip() or None
    meta_description = (data.get("meta_description") or "").strip() or None

    # Image : nouvelle image valide, sinon on conserve l'existante.
    featured_image = existing["featured_image"] if existing else None
    if image_file is not None and getattr(image_file, "filename", ""):
        try:
            featured_image = image_storage.save_upload(image_file, namespace="content")
        except image_storage.ImageStorageError as exc:
            return None, [str(exc)]

    # Exigences SEO uniquement à la publication ; les brouillons restent libres.
    if status == "published":
        publish_errors = _publish_errors(title, slug, meta_title, meta_description)
        if publish_errors:
            return None, publish_errors

    # published_at posé à la première publication, conservé ensuite.
    published_at = existing["published_at"] if existing else None
    if status == "published" and not published_at:
        published_at = _now_sql()

    if content_id:
        content_repository.update(
            content_id, content_type, title, slug, summary, body, status,
            meta_title, meta_description, featured_image, published_at,
        )
        return content_id, []

    new_id = content_repository.insert(
        content_type, title, slug, summary, body, status,
        meta_title, meta_description, featured_image, published_at,
    )
    return new_id, []


def publish(content_id):
    """Publie un contenu après contrôle des exigences SEO.

    Args:
        content_id (int): Identifiant du contenu.

    Returns:
        tuple[bool, list[str]]: Succès et messages d'erreur éventuels.
    """

    row = content_repository.get_by_id(content_id)
    if not row:
        return False, ["Contenu introuvable."]

    publish_errors = _publish_errors(
        row["title"], row["slug"], row["meta_title"], row["meta_description"]
    )
    if publish_errors:
        return False, publish_errors

    published_at = row["published_at"] or _now_sql()
    content_repository.update_status(content_id, "published", published_at)
    return True, []


def unpublish(content_id):
    """Repasse un contenu en brouillon (le retire du public et du sitemap).

    Args:
        content_id (int): Identifiant du contenu.

    Returns:
        bool: True si le contenu existait et a été mis à jour.
    """

    row = content_repository.get_by_id(content_id)
    if not row:
        return False
    content_repository.update_status(content_id, "draft", row["published_at"])
    return True


def archive(content_id):
    """Archive un contenu (le retire du public et du sitemap).

    Args:
        content_id (int): Identifiant du contenu.

    Returns:
        bool: True si le contenu existait et a été mis à jour.
    """

    row = content_repository.get_by_id(content_id)
    if not row:
        return False
    content_repository.update_status(content_id, "archived", row["published_at"])
    return True


def delete_content(content_id):
    """Supprime définitivement un contenu.

    Args:
        content_id (int): Identifiant du contenu.

    Returns:
        bool: True si une ligne a été supprimée.
    """

    return content_repository.delete(content_id) > 0


def get_public_page(slug):
    """Récupère une page publiée pour l'affichage public.

    Args:
        slug (str): Slug demandé dans l'URL.

    Returns:
        sqlite3.Row | None: Contenu publié ou None (404).
    """

    return content_repository.get_published_by_slug(slug)


def get_public_page_context(slug):
    """Prépare une page SEO publiée et ses éventuels contenus dynamiques.

    La page dédiée aux youtubeurs est enrichie automatiquement avec les
    talents publiés qui possèdent une URL YouTube. Les autres pages conservent
    le rendu éditorial générique.

    Args:
        slug (str): Slug public demandé.

    Returns:
        dict | None:
            Contexte métier de la page, ou None si elle n'est pas publiée.
    """

    row = get_public_page(slug)
    if not row:
        return None

    youtube_creators = None
    if row["slug"] == talent_service.YOUTUBE_CREATORS_CONTENT_SLUG:
        youtube_creators = talent_service.get_public_youtube_creator_cards()

    return {
        "content": row,
        "seo": build_seo_context(row),
        "youtube_creators": youtube_creators,
    }


def build_seo_context(row):
    """Prépare les métadonnées SEO d'une page avec repli sur les champs de base.

    Args:
        row (sqlite3.Row): Ligne de contenu.

    Returns:
        dict: Variables SEO prêtes pour les blocs Jinja.
    """

    return {
        "seo_title": (row["meta_title"] or row["title"]),
        "seo_description": (row["meta_description"] or row["summary"] or ""),
    }


def get_admin_list(content_type=None, status=None, q=None, sort="recent", page=1, per_page=20):
    """Prépare la liste paginée des contenus pour l'administration.

    Args:
        content_type (str | None): Filtre par type.
        status (str | None): Filtre par statut.
        q (str | None): Recherche texte (titre/slug).
        sort (str): Clé de tri.
        page (int): Page demandée (1-based).
        per_page (int): Taille de page.

    Returns:
        dict: items, page, total_pages, total.
    """

    type_filter = content_type if content_type in CONTENT_TYPE_KEYS else None
    status_filter = status if status in STATUS_KEYS else None
    search = (q or "").strip()[:120] or None

    total = content_repository.count_for_admin(type_filter, status_filter, search)["total"]
    total_pages = max((total + per_page - 1) // per_page, 1)
    page = max(min(page, total_pages), 1)
    offset = (page - 1) * per_page

    items = content_repository.list_for_admin(
        type_filter, status_filter, search, sort, per_page, offset
    )
    return {"items": items, "page": page, "total_pages": total_pages, "total": total}
