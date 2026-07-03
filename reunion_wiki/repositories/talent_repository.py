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
    "recent": "t.id DESC",
    "oldest": "t.id ASC",
    "name_asc": "t.name COLLATE NOCASE ASC, t.id ASC",
    "name_desc": "t.name COLLATE NOCASE DESC, t.id DESC",
    "display_order": "t.display_order ASC, t.name COLLATE NOCASE ASC, t.id ASC",
}

TALENT_SELECT_FIELDS = """
    t.id,
    t.name,
    t.slug,
    tc.name AS category,
    v.nom AS city,
    t.category_id,
    t.city_id,
    t.description,
    t.bio,
    t.image,
    t.instagram_url,
    t.youtube_url,
    t.tiktok_url,
    t.facebook_url,
    t.website_url,
    t.status,
    t.display_order,
    t.published_at,
    NULL AS date_created,
    NULL AS date_updated
"""

TALENT_JOIN_SQL = """
    FROM talents t
    LEFT JOIN talent_categories tc ON tc.id = t.category_id
    LEFT JOIN villes v ON v.id = t.city_id
"""

CATEGORY_ALIAS_SQL = "tc.name"
CITY_ALIAS_SQL = "v.nom"


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
        clauses.append("t.status = ?")
        params.append(status)
    if category:
        clauses.append(f"{CATEGORY_ALIAS_SQL} = ?")
        params.append(category)
    if q:
        like = f"%{q}%"
        clauses.append("(t.name LIKE ? OR t.slug LIKE ?)")
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

    return _fetchone(
        f"""
        SELECT {TALENT_SELECT_FIELDS}
        {TALENT_JOIN_SQL}
        WHERE t.id = ?
        """,
        (talent_id,),
    )


def get_by_slug(slug):
    """Récupère un talent à partir de son slug, quel que soit son statut.

    Args:
        slug (str): Slug du talent.

    Returns:
        sqlite3.Row | None:
            Talent trouvé ou None si inexistant.
    """

    return _fetchone(
        f"""
        SELECT {TALENT_SELECT_FIELDS}
        {TALENT_JOIN_SQL}
        WHERE t.slug = ?
        """,
        (slug,),
    )


def get_published_by_slug(slug):
    """Récupère un talent public à partir de son slug.

    Args:
        slug (str): Slug du talent.

    Returns:
        sqlite3.Row | None:
            Talent publié trouvé, ou None.
    """

    return _fetchone(
        f"""
        SELECT {TALENT_SELECT_FIELDS}
        {TALENT_JOIN_SQL}
        WHERE t.slug = ?
          AND t.status = 'published'
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

    query = f"""
        SELECT {TALENT_SELECT_FIELDS}
        {TALENT_JOIN_SQL}
        WHERE t.status = 'published'
        ORDER BY t.display_order ASC, t.name COLLATE NOCASE ASC, t.id ASC
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

    query = f"""
        SELECT {TALENT_SELECT_FIELDS}
        {TALENT_JOIN_SQL}
        WHERE t.status = 'published'
          AND {CATEGORY_ALIAS_SQL} = ?
        ORDER BY t.display_order ASC, t.name COLLATE NOCASE ASC, t.id ASC
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
        f"""
        SELECT {CATEGORY_ALIAS_SQL} AS category, COUNT(*) AS total
        {TALENT_JOIN_SQL}
        WHERE t.status = 'published'
          AND {CATEGORY_ALIAS_SQL} IS NOT NULL
          AND TRIM({CATEGORY_ALIAS_SQL}) != ''
        GROUP BY {CATEGORY_ALIAS_SQL}
        ORDER BY {CATEGORY_ALIAS_SQL} COLLATE NOCASE ASC
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
        SELECT
            t.id,
            t.name,
            t.slug,
            {CATEGORY_ALIAS_SQL} AS category,
            {CITY_ALIAS_SQL} AS city,
            t.image,
            t.status,
            t.display_order,
            t.published_at,
            NULL AS date_created,
            NULL AS date_updated
        {TALENT_JOIN_SQL}
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
        f"""
        SELECT COUNT(*) AS total
        {TALENT_JOIN_SQL}
        WHERE {where_sql}
        """,
        tuple(params),
    )


def insert(name, slug, category_id, city_id, description, bio, image, instagram_url,
           youtube_url, tiktok_url, facebook_url, website_url, status,
           display_order, published_at):
    """Insère un talent dans la base.

    Args:
        name (str): Nom affiché du talent.
        slug (str): Slug unique.
        category_id (int): Identifiant de catégorie talent.
        city_id (int | None): Identifiant de commune.
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
        f"""
        INSERT INTO talents (
            name, slug, category_id, city_id, description, bio, image,
            instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
            status, display_order, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name, slug, category_id, city_id, description, bio, image,
            instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
            status, display_order, published_at,
        ),
    )


def update(talent_id, name, slug, category_id, city_id, description, bio, image,
           instagram_url, youtube_url, tiktok_url, facebook_url, website_url,
           status, display_order, published_at):
    """Met à jour un talent existant.

    Args:
        talent_id (int): Identifiant du talent.
        name (str): Nom affiché du talent.
        slug (str): Slug unique.
        category_id (int): Identifiant de catégorie talent.
        city_id (int | None): Identifiant de commune.
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
        f"""
        UPDATE talents SET
            name = ?, slug = ?, category_id = ?, city_id = ?, description = ?,
            bio = ?, image = ?, instagram_url = ?, youtube_url = ?,
            tiktok_url = ?, facebook_url = ?, website_url = ?, status = ?,
            display_order = ?, published_at = ?
        WHERE id = ?
        """,
        (
            name, slug, category_id, city_id, description, bio, image,
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
        SET status = ?, published_at = ?
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
