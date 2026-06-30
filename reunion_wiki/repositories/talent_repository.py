# -*- coding: utf-8 -*-

from ..db import get_db_connection


def _fetchone(query, params=()):
    """Exécute une requête SELECT et retourne une seule ligne.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        sqlite3.Row | None:
            Ligne trouvée ou None.
    """

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        conn.close()


def _fetchall(query, params=()):
    """Exécute une requête SELECT et retourne toutes les lignes.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        list[sqlite3.Row]:
            Lignes retournées par SQLite.
    """

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def _execute(query, params=()):
    """Exécute une requête d'écriture et retourne le nombre de lignes touchées.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        int:
            Nombre de lignes modifiées ou supprimées.
    """

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
    """Exécute une requête INSERT et retourne l'identifiant créé.

    Args:
        query (str): Requête SQL paramétrée.
        params (tuple): Paramètres de la requête.

    Returns:
        int:
            Identifiant de la ligne créée.
    """

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


ADMIN_SORTS = {
    "recent": "date_updated DESC, id DESC",
    "oldest": "date_updated ASC, id ASC",
    "name_asc": "name COLLATE NOCASE ASC, id ASC",
    "name_desc": "name COLLATE NOCASE DESC, id DESC",
    "display_order": "display_order ASC, name COLLATE NOCASE ASC, id ASC",
}


def _build_admin_filters(status=None, category=None, q=None):
    """Construit les clauses WHERE paramétrées pour la future liste admin.

    Args:
        status (str | None): Statut à filtrer.
        category (str | None): Catégorie à filtrer.
        q (str | None): Recherche texte sur le nom et le slug.

    Returns:
        tuple[str, list]:
            Clause WHERE et paramètres associés.
    """

    clauses = ["1=1"]
    params = []

    if status:
        clauses.append("status = ?")
        params.append(status)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if q:
        like = f"%{q}%"
        clauses.append("(name LIKE ? OR slug LIKE ?)")
        params.extend([like, like])

    return " AND ".join(clauses), params


def get_by_id(talent_id):
    """Récupère un talent à partir de son identifiant.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        sqlite3.Row | None:
            Talent trouvé ou None si inexistant.
    """

    return _fetchone("SELECT * FROM talents WHERE id = ?", (talent_id,))


def get_by_slug(slug):
    """Récupère un talent à partir de son slug, quel que soit son statut.

    Args:
        slug (str): Slug du talent.

    Returns:
        sqlite3.Row | None:
            Talent trouvé ou None si inexistant.
    """

    return _fetchone("SELECT * FROM talents WHERE slug = ?", (slug,))


def get_published_by_slug(slug):
    """Récupère un talent public à partir de son slug.

    Args:
        slug (str): Slug du talent.

    Returns:
        sqlite3.Row | None:
            Talent publié trouvé, ou None.
    """

    return _fetchone(
        """
        SELECT *
        FROM talents
        WHERE slug = ?
          AND status = 'published'
        """,
        (slug,),
    )


def slug_exists(slug, exclude_id=None):
    """Indique si un slug de talent est déjà utilisé.

    Args:
        slug (str): Slug à tester.
        exclude_id (int | None): Identifiant à ignorer en édition.

    Returns:
        bool:
            True si le slug existe déjà.
    """

    if exclude_id:
        row = _fetchone(
            "SELECT 1 FROM talents WHERE slug = ? AND id != ?",
            (slug, exclude_id),
        )
    else:
        row = _fetchone("SELECT 1 FROM talents WHERE slug = ?", (slug,))
    return row is not None


def list_published(limit=None, offset=0):
    """Liste les talents publics.

    Args:
        limit (int | None): Nombre maximum de talents.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Talents publiés, triés pour l'affichage public.
    """

    query = """
        SELECT *
        FROM talents
        WHERE status = 'published'
        ORDER BY display_order ASC, name COLLATE NOCASE ASC, id ASC
    """
    if limit is None:
        return _fetchall(query)
    return _fetchall(f"{query} LIMIT ? OFFSET ?", (limit, offset))


def list_published_by_category(category, limit=None, offset=0):
    """Liste les talents publics d'une catégorie.

    Args:
        category (str): Catégorie à filtrer.
        limit (int | None): Nombre maximum de talents.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Talents publics de la catégorie demandée.
    """

    query = """
        SELECT *
        FROM talents
        WHERE status = 'published'
          AND category = ?
        ORDER BY display_order ASC, name COLLATE NOCASE ASC, id ASC
    """
    if limit is None:
        return _fetchall(query, (category,))
    return _fetchall(f"{query} LIMIT ? OFFSET ?", (category, limit, offset))


def list_categories():
    """Retourne les catégories représentées par des talents publics.

    Returns:
        list[sqlite3.Row]:
            Catégories distinctes avec le nombre de talents publics.
    """

    return _fetchall(
        """
        SELECT category, COUNT(*) AS total
        FROM talents
        WHERE status = 'published'
          AND category IS NOT NULL
          AND TRIM(category) != ''
        GROUP BY category
        ORDER BY category COLLATE NOCASE ASC
        """
    )


def list_for_admin(status=None, category=None, q=None, sort="recent", limit=50, offset=0):
    """Liste les talents pour une future interface admin.

    Args:
        status (str | None): Filtre par statut.
        category (str | None): Filtre par catégorie.
        q (str | None): Recherche texte.
        sort (str): Clé de tri autorisée.
        limit (int): Nombre maximum de lignes.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Talents correspondant aux filtres.
    """

    where_sql, params = _build_admin_filters(status, category, q)
    order_sql = ADMIN_SORTS.get(sort, ADMIN_SORTS["recent"])
    return _fetchall(
        f"""
        SELECT id, name, slug, category, city, image, status, display_order,
               published_at, date_created, date_updated
        FROM talents
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT ? OFFSET ?
        """,
        (*params, limit, offset),
    )


def count_for_admin(status=None, category=None, q=None):
    """Compte les talents pour une future interface admin.

    Args:
        status (str | None): Filtre par statut.
        category (str | None): Filtre par catégorie.
        q (str | None): Recherche texte.

    Returns:
        sqlite3.Row:
            Ligne contenant le total sous la clé `total`.
    """

    where_sql, params = _build_admin_filters(status, category, q)
    return _fetchone(
        f"SELECT COUNT(*) AS total FROM talents WHERE {where_sql}",
        tuple(params),
    )


def insert(name, slug, category, city, description, bio, image, instagram_url,
           youtube_url, tiktok_url, facebook_url, website_url, status,
           display_order, published_at):
    """Insère un talent dans la base.

    Args:
        name (str): Nom affiché du talent.
        slug (str): Slug unique.
        category (str): Catégorie du talent.
        city (str): Commune associée.
        description (str): Courte description.
        bio (str | None): Biographie longue.
        image (str | None): Chemin relatif de l'image.
        instagram_url (str | None): URL Instagram.
        youtube_url (str | None): URL YouTube.
        tiktok_url (str | None): URL TikTok.
        facebook_url (str | None): URL Facebook.
        website_url (str | None): URL officielle.
        status (str): Statut du talent.
        display_order (int): Ordre manuel d'affichage.
        published_at (str | None): Date de publication.

    Returns:
        int:
            Identifiant du talent créé.
    """

    return _insert(
        """
        INSERT INTO talents (
            name, slug, category, city, description, bio, image,
            instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
            status, display_order, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name, slug, category, city, description, bio, image,
            instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
            status, display_order, published_at,
        ),
    )


def update(talent_id, name, slug, category, city, description, bio, image,
           instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
           status, display_order, published_at):
    """Met à jour un talent existant.

    Args:
        talent_id (int): Identifiant du talent.
        name (str): Nom affiché du talent.
        slug (str): Slug unique.
        category (str): Catégorie du talent.
        city (str): Commune associée.
        description (str): Courte description.
        bio (str | None): Biographie longue.
        image (str | None): Chemin relatif de l'image.
        instagram_url (str | None): URL Instagram.
        youtube_url (str | None): URL YouTube.
        tiktok_url (str | None): URL TikTok.
        facebook_url (str | None): URL Facebook.
        website_url (str | None): URL officielle.
        status (str): Statut du talent.
        display_order (int): Ordre manuel d'affichage.
        published_at (str | None): Date de publication.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE talents SET
            name = ?, slug = ?, category = ?, city = ?, description = ?,
            bio = ?, image = ?, instagram_url = ?, youtube_url = ?,
            tiktok_url = ?, facebook_url = ?, website_url = ?, status = ?,
            display_order = ?, published_at = ?, date_updated = DATETIME('now')
        WHERE id = ?
        """,
        (
            name, slug, category, city, description, bio, image,
            instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
            status, display_order, published_at, talent_id,
        ),
    )


def update_status(talent_id, status, published_at):
    """Met à jour uniquement le statut et la date de publication d'un talent.

    Args:
        talent_id (int): Identifiant du talent.
        status (str): Nouveau statut.
        published_at (str | None): Date de publication.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE talents
        SET status = ?, published_at = ?, date_updated = DATETIME('now')
        WHERE id = ?
        """,
        (status, published_at, talent_id),
    )


def delete(talent_id):
    """Supprime un talent à partir de son identifiant.

    Args:
        talent_id (int): Identifiant du talent.

    Returns:
        int:
            Nombre de lignes supprimées.
    """

    return _execute("DELETE FROM talents WHERE id = ?", (talent_id,))
