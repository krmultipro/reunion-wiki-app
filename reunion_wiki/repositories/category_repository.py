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




def get_category_by_id(category_id):
    """
    Récupère une catégorie à partir de son identifiant.

    Args:
        category_id (int): Identifiant de la catégorie.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None si inexistante.
    """

    return _fetchone("SELECT id, nom, slug FROM categories WHERE id = ?", (category_id,))


def get_category_by_name(nom):
    """
    Récupère une catégorie à partir de son nom.

    Args:
        nom (str): Nom de la catégorie.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée ou None si inexistante.
    """

    return _fetchone("SELECT id, nom, slug FROM categories WHERE nom = ?", (nom,))


def get_category_by_normalized_name(nom):
    """Recherche une catégorie sans tenir compte de la casse ni des espaces extérieurs."""

    return _fetchone(
        """
        SELECT id, nom, slug
        FROM categories
        WHERE LOWER(TRIM(nom)) = LOWER(?)
        ORDER BY id ASC
        LIMIT 1
        """,
        ((nom or "").strip(),),
    )


def get_category_by_name_excluding_id(nom, category_id):
    """
    Récupère une catégorie par nom en excluant un identifiant donné.

    Args:
        nom (str): Nom de la catégorie recherchée.
        category_id (int): Identifiant de catégorie à exclure.

    Returns:
        sqlite3.Row | None:
            Catégorie trouvée hors identifiant exclu, ou None.
    """

    return _fetchone("SELECT id FROM categories WHERE nom = ? AND id != ?", (nom, category_id))


def get_category_by_slug(slug):
    """Récupère une catégorie à partir de son slug."""

    return _fetchone(
        "SELECT id, nom, slug FROM categories WHERE slug = ?",
        (slug,),
    )


def get_category_by_slug_excluding_id(slug, category_id):
    """Recherche un slug en ignorant la catégorie en cours d'édition."""

    return _fetchone(
        "SELECT id, nom, slug FROM categories WHERE slug = ? AND id != ?",
        (slug, category_id),
    )


def get_all_categories():
    """
    Retourne toutes les catégories.

    Returns:
        list[sqlite3.Row]:
            Liste des catégories triées par nom.
    """

    return _fetchall(
        """
        SELECT id, nom, slug, created_at
        FROM categories
        ORDER BY nom COLLATE NOCASE ASC
        """
    )

def get_categories_rank():
    """
    Retourne le classement des catégories par clics et nombre de sites.

    Returns:
        list[sqlite3.Row]:
            Liste des catégories avec nombre de sites et total de clics.
    """

    return _fetchall(
        """
        SELECT
            c.nom AS categorie,
            COUNT(*) AS site_count,
            COALESCE(SUM(s.click_count), 0) AS total_clicks
        FROM sites s
        JOIN categories c ON c.id = s.category_id
        WHERE s.status = 'valide'
        GROUP BY c.id, c.nom
        ORDER BY total_clicks DESC, site_count DESC, c.nom COLLATE NOCASE ASC
        """
    )


def get_category_stats():
    """
    Retourne les statistiques publiques des catégories.

    Returns:
        list[sqlite3.Row]:
            Liste des catégories avec nombre de sites validés et total de clics.
    """

    return _fetchall(
        """
        SELECT
            c.nom AS categorie,
            COUNT(*) AS site_count,
            COALESCE(SUM(s.click_count), 0) AS total_clicks
        FROM sites s
        JOIN categories c ON c.id = s.category_id
        WHERE s.status = 'valide'
        GROUP BY c.id, c.nom
        ORDER BY total_clicks DESC, site_count DESC, c.nom COLLATE NOCASE ASC
        """
    )


def get_trending_categories():
    """
    Retourne les catégories ayant le plus de clics récents et leur progression.

    Returns:
        list[sqlite3.Row]:
            Liste des catégories avec clics 7 jours, période précédente et croissance.
    """

    return _fetchall(
        """
        WITH c7 AS (
            SELECT c.nom AS categorie, COUNT(sc.id) AS clicks_7d
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
            LEFT JOIN site_clicks sc
              ON sc.site_id = s.id
             AND sc.clicked_at >= datetime('now', '-7 days')
            WHERE s.status = 'valide'
              AND c.nom IS NOT NULL
              AND TRIM(c.nom) != ''
            GROUP BY c.nom
        ),
        cp AS (
            SELECT c.nom AS categorie, COUNT(sc.id) AS clicks_prev_7d
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
            LEFT JOIN site_clicks sc
              ON sc.site_id = s.id
             AND sc.clicked_at >= datetime('now', '-14 days')
             AND sc.clicked_at < datetime('now', '-7 days')
            WHERE s.status = 'valide'
              AND c.nom IS NOT NULL
              AND TRIM(c.nom) != ''
            GROUP BY c.nom
        )
        SELECT
            c7.categorie,
            COALESCE(c7.clicks_7d, 0) AS clicks_7d,
            COALESCE(cp.clicks_prev_7d, 0) AS clicks_prev_7d,
            CASE
                WHEN COALESCE(cp.clicks_prev_7d, 0) = 0 THEN NULL
                ELSE ROUND((COALESCE(c7.clicks_7d, 0) - cp.clicks_prev_7d) * 100.0 / cp.clicks_prev_7d, 1)
            END AS growth_pct
        FROM c7
        LEFT JOIN cp ON cp.categorie = c7.categorie
        WHERE c7.categorie IS NOT NULL AND TRIM(c7.categorie) != ''
        ORDER BY clicks_7d DESC, growth_pct DESC
        LIMIT 10
        """
    )


def count_sites_by_category(category_id):
    """
    Compte les sites associés à une catégorie.

    Args:
        category_id (int): Identifiant de la catégorie.

    Returns:
        sqlite3.Row:
            Ligne contenant le total de sites associés.
    """

    return _fetchone(
        """
        SELECT COUNT(*) as total
        FROM sites
        WHERE category_id = ?
        """,
        (category_id,),
    )


def create_category(nom, slug):
    """
    Crée une nouvelle catégorie.

    Args:
        nom (str): Nom de la catégorie.
        slug (str): Slug de la catégorie.

    Returns:
        int:
            Nombre de lignes insérées.
    """

    return _execute("INSERT INTO categories (nom, slug) VALUES (?, ?)", (nom, slug))


def update_category(category_id, nom, slug):
    """
    Met à jour une catégorie existante.

    Args:
        category_id (int): Identifiant de la catégorie.
        nom (str): Nouveau nom de la catégorie.
        slug (str): Nouveau slug de la catégorie.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute("UPDATE categories SET nom = ?, slug = ? WHERE id = ?", (nom, slug, category_id))


def delete_category(category_id):
    """
    Supprime une catégorie à partir de son identifiant.

    Args:
        category_id (int): Identifiant de la catégorie.

    Returns:
        int:
            Nombre de lignes supprimées.
    """

    return _execute("DELETE FROM categories WHERE id = ?", (category_id,))
