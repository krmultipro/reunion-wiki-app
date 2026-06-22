# -*- coding: utf-8 -*-

from ..db import get_db_connection


def _fetchone(query, params=()):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        conn.close()


def _fetchall(query, params=()):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def _execute(query, params=()):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _insert(query, params=()):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Tri autorisé côté admin : libellé -> clause ORDER BY (jamais d'entrée brute).
ADMIN_SORTS = {
    "recent": "updated_at DESC, id DESC",
    "oldest": "updated_at ASC, id ASC",
    "title_asc": "title COLLATE NOCASE ASC, id DESC",
    "title_desc": "title COLLATE NOCASE DESC, id DESC",
}


def _build_admin_filters(content_type=None, status=None, q=None):
    """Construit les clauses WHERE paramétrées de la liste admin.

    Args:
        content_type (str | None): Filtre sur un type de contenu.
        status (str | None): Filtre sur un statut.
        q (str | None): Recherche texte sur le titre et le slug.

    Returns:
        tuple[str, list]:
            Clause SQL prête à concaténer et liste de paramètres.
    """

    clauses = ["1=1"]
    params = []

    if content_type:
        clauses.append("content_type = ?")
        params.append(content_type)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if q:
        like = f"%{q}%"
        clauses.append("(title LIKE ? OR slug LIKE ?)")
        params.extend([like, like])

    return " AND ".join(clauses), params


def get_by_id(content_id):
    """Récupère un contenu à partir de son identifiant.

    Args:
        content_id (int): Identifiant du contenu.

    Returns:
        sqlite3.Row | None:
            Contenu trouvé ou None si inexistant.
    """

    return _fetchone("SELECT * FROM content WHERE id = ?", (content_id,))


def get_by_slug(slug):
    """Récupère un contenu à partir de son slug, quel que soit son statut.

    Args:
        slug (str): Slug public du contenu.

    Returns:
        sqlite3.Row | None:
            Contenu trouvé ou None si inexistant.
    """

    return _fetchone("SELECT * FROM content WHERE slug = ?", (slug,))


def get_published_by_slug(slug):
    """Récupère un contenu publié à partir de son slug.

    Args:
        slug (str): Slug public du contenu.

    Returns:
        sqlite3.Row | None:
            Contenu publié trouvé ou None.
    """

    return _fetchone(
        "SELECT * FROM content WHERE slug = ? AND status = 'published'",
        (slug,),
    )


def slug_exists(slug, exclude_id=None):
    """Indique si un slug est déjà utilisé.

    Args:
        slug (str): Slug à tester.
        exclude_id (int | None): Identifiant à ignorer (utile en édition).

    Returns:
        bool: True si le slug est déjà pris.
    """

    if exclude_id:
        row = _fetchone(
            "SELECT 1 FROM content WHERE slug = ? AND id != ?",
            (slug, exclude_id),
        )
    else:
        row = _fetchone("SELECT 1 FROM content WHERE slug = ?", (slug,))
    return row is not None


def list_for_admin(content_type=None, status=None, q=None, sort="recent", limit=50, offset=0):
    """Liste paginée des contenus pour l'administration.

    Args:
        content_type (str | None): Filtre par type.
        status (str | None): Filtre par statut.
        q (str | None): Recherche texte (titre/slug).
        sort (str): Clé de tri autorisée (voir ADMIN_SORTS).
        limit (int): Nombre maximum de lignes.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Contenus correspondant aux filtres.
    """

    where_sql, params = _build_admin_filters(content_type, status, q)
    order_sql = ADMIN_SORTS.get(sort, ADMIN_SORTS["recent"])
    return _fetchall(
        f"""
        SELECT id, content_type, title, slug, status, meta_title, meta_description,
               featured_image, published_at, created_at, updated_at
        FROM content
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT ? OFFSET ?
        """,
        (*params, limit, offset),
    )


def count_for_admin(content_type=None, status=None, q=None):
    """Compte les contenus correspondant aux filtres admin.

    Args:
        content_type (str | None): Filtre par type.
        status (str | None): Filtre par statut.
        q (str | None): Recherche texte (titre/slug).

    Returns:
        sqlite3.Row:
            Ligne contenant le total sous la clé `total`.
    """

    where_sql, params = _build_admin_filters(content_type, status, q)
    return _fetchone(
        f"SELECT COUNT(*) AS total FROM content WHERE {where_sql}",
        tuple(params),
    )


def insert(content_type, title, slug, summary, body, status,
           meta_title, meta_description, featured_image, published_at):
    """Insère un nouveau contenu.

    Args:
        content_type (str): Type de contenu.
        title (str): Titre.
        slug (str): Slug unique.
        summary (str | None): Résumé.
        body (str | None): Corps HTML assaini.
        status (str): Statut (draft/published/archived).
        meta_title (str | None): Méta-titre SEO.
        meta_description (str | None): Méta-description SEO.
        featured_image (str | None): Chemin relatif de l'image.
        published_at (str | None): Date de publication ISO ou None.

    Returns:
        int:
            Identifiant du contenu créé.
    """

    return _insert(
        """
        INSERT INTO content (
            content_type, title, slug, summary, body, status,
            meta_title, meta_description, featured_image, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (content_type, title, slug, summary, body, status,
         meta_title, meta_description, featured_image, published_at),
    )


def update(content_id, content_type, title, slug, summary, body, status,
           meta_title, meta_description, featured_image, published_at):
    """Met à jour un contenu existant.

    Args:
        content_id (int): Identifiant du contenu.
        content_type (str): Type de contenu.
        title (str): Titre.
        slug (str): Slug unique.
        summary (str | None): Résumé.
        body (str | None): Corps HTML assaini.
        status (str): Statut (draft/published/archived).
        meta_title (str | None): Méta-titre SEO.
        meta_description (str | None): Méta-description SEO.
        featured_image (str | None): Chemin relatif de l'image.
        published_at (str | None): Date de publication ISO ou None.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE content SET
            content_type = ?, title = ?, slug = ?, summary = ?, body = ?, status = ?,
            meta_title = ?, meta_description = ?, featured_image = ?, published_at = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (content_type, title, slug, summary, body, status,
         meta_title, meta_description, featured_image, published_at, content_id),
    )


def update_status(content_id, status, published_at):
    """Met à jour uniquement le statut et la date de publication.

    Args:
        content_id (int): Identifiant du contenu.
        status (str): Nouveau statut.
        published_at (str | None): Date de publication ISO ou None.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE content SET status = ?, published_at = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (status, published_at, content_id),
    )


def delete(content_id):
    """Supprime un contenu à partir de son identifiant.

    Args:
        content_id (int): Identifiant du contenu.

    Returns:
        int:
            Nombre de lignes supprimées.
    """

    return _execute("DELETE FROM content WHERE id = ?", (content_id,))


def get_published_for_sitemap():
    """Retourne les contenus publiés pour la génération du sitemap.

    Returns:
        list[sqlite3.Row]:
            Lignes (slug, updated_at) des contenus publiés, plus récents d'abord.
    """

    return _fetchall(
        """
        SELECT slug, updated_at
        FROM content
        WHERE status = 'published'
        ORDER BY updated_at DESC
        """
    )
