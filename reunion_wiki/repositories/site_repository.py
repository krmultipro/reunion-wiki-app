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


def get_site_by_id(site_id):
    return _fetchone(
        """
        SELECT
            s.id,
            s.nom,
            s.category_id,
            v.nom AS ville,
            s.lien,
            s.description,
            s.status,
            s.en_vedette,
            c.nom AS categorie
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.id = ?
        """,
        (site_id,),
    )


def get_valid_site_by_id(site_id):
    return _fetchone(
        "SELECT lien, click_count FROM sites WHERE id = ? AND status = 'valide'",
        (site_id,),
    )


def get_site_by_slug(slug):
    return _fetchone(
        """
        SELECT s.*, c.nom AS categorie, v.nom AS ville
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.slug = ?
        """,
        (slug,),
    )


def get_latest_sites(limit=None):
    query = """
        SELECT
            s.id,
            s.nom,
            s.lien,
            c.nom AS categorie,
            s.description,
            s.date_ajout
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        WHERE s.status = 'valide'
        ORDER BY s.date_ajout DESC
    """
    if limit is None:
        return _fetchall(query)
    return _fetchall(f"{query} LIMIT ?", (limit,))


def get_top_sites(limit=None):
    query = """
        SELECT
            s.id,
            s.nom,
            s.lien,
            c.nom AS categorie,
            s.description,
            s.click_count
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        WHERE s.status = 'valide'
        ORDER BY s.click_count DESC
    """
    if limit is None:
        return _fetchall(query)
    return _fetchall(f"{query} LIMIT ?", (limit,))


def get_sites_by_category_id(category_id):
    return _fetchall(
        """
        SELECT s.*, c.nom AS categorie, v.nom AS ville
        FROM sites s
        JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide'
          AND s.category_id = ?
        ORDER BY en_vedette DESC, click_count DESC, date_ajout DESC, id DESC
        """,
        (category_id,),
    )


def get_city_stats():
    return _fetchall(
        """
        SELECT
          v.id,
          v.nom,
          v.slug,
          COUNT(s.id) AS nb_sites,
          COALESCE(SUM(s.click_count), 0) AS total_clicks
        FROM villes v
        LEFT JOIN sites s
          ON s.ville_id = v.id
         AND s.status = 'valide'
        GROUP BY v.id, v.nom, v.slug
        ORDER BY total_clicks DESC, nb_sites DESC, v.nom COLLATE NOCASE ASC
        """
    )


def get_city_by_slug(slug):
    return _fetchone("SELECT id, nom, slug FROM villes WHERE slug = ?", (slug,))


def get_admin_city_filters():
    return _fetchall("SELECT nom, slug FROM villes ORDER BY nom COLLATE NOCASE ASC")


def get_sites_by_city_id(ville_id):
    return _fetchall(
        """
        SELECT s.*, c.nom AS categorie, v.nom AS ville
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide' AND s.ville_id = ?
        ORDER BY s.en_vedette DESC, s.date_ajout DESC
        """,
        (ville_id,),
    )


def get_total_clicks_by_city_id(ville_id):
    return _fetchone(
        """
        SELECT COALESCE(SUM(click_count), 0) AS total_clicks
        FROM sites
        WHERE status = 'valide' AND ville_id = ?
        """,
        (ville_id,),
    )


def get_pending_sites():
    return _fetchall(
        """
        SELECT
            s.id,
            s.nom,
            c.nom AS categorie,
            v.nom AS ville,
            s.lien,
            s.description,
            s.status,
            s.date_ajout
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'en_attente'
        ORDER BY s.date_ajout DESC, s.id DESC
        """
    )


def get_status_counts():
    return _fetchall("SELECT status, COUNT(*) as total FROM sites GROUP BY status")


def count_sites_for_admin(where_sql, params):
    return _fetchone(
        f"""
        SELECT COUNT(*) AS total
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE {where_sql}
        """,
        params,
    )


def get_sites_for_admin(where_sql, sort_sql, params, limit, offset):
    return _fetchall(
        f"""
        SELECT
            s.id,
            s.nom,
            c.nom AS categorie,
            v.nom AS ville_display,
            v.slug AS ville_slug,
            s.lien,
            s.description,
            s.status,
            s.date_ajout,
            s.en_vedette,
            s.click_count
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE {where_sql}
        ORDER BY {sort_sql}
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    )


def search_sites(like, like_city):
    return _fetchall(
        """
        SELECT
            s.id,
            s.nom,
            s.lien,
            v.nom AS ville,
            c.nom AS categorie,
            s.description,
            s.click_count,
            s.date_ajout
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide'
          AND (
            s.nom LIKE ?
            OR COALESCE(c.nom, '') LIKE ?
            OR s.description LIKE ?
            OR s.lien LIKE ?
            OR COALESCE(v.nom, '') LIKE ?
            OR LOWER(REPLACE(COALESCE(v.nom, ''), '-', ' ')) LIKE ?
          )
        ORDER BY
          CASE
            WHEN s.nom LIKE ? THEN 0
            WHEN COALESCE(c.nom, '') LIKE ? THEN 1
            WHEN s.description LIKE ? THEN 2
            WHEN COALESCE(v.nom, '') LIKE ? OR LOWER(REPLACE(COALESCE(v.nom, ''), '-', ' ')) LIKE ? THEN 3
            WHEN s.lien LIKE ? THEN 4
            ELSE 5
          END,
          s.click_count DESC,
          s.date_ajout DESC
        LIMIT 100
        """,
        (like, like, like, like, like, like_city, like, like, like, like, like_city, like),
    )


def create_site(nom, ville_id, lien, description, category_id, status="en_attente", en_vedette=None):
    if en_vedette is None:
        return _execute(
            """
            INSERT INTO sites (nom, ville_id, lien, description, category_id, status, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'))
            """,
            (nom, ville_id, lien, description, category_id, status),
        )
    return _execute(
        """
        INSERT INTO sites (nom, ville_id, lien, description, category_id, status, date_ajout, en_vedette)
        VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'), ?)
        """,
        (nom, ville_id, lien, description, category_id, status, en_vedette),
    )


def update_site(site_id, nom, ville_id, lien, description, category_id, status, en_vedette):
    return _execute(
        """
        UPDATE sites
        SET nom = ?, ville_id = ?, lien = ?, description = ?, category_id = ?, status = ?, en_vedette = ?
        WHERE id = ?
        """,
        (nom, ville_id, lien, description, category_id, status, en_vedette, site_id),
    )


def update_site_status(site_id, status, refresh_date=False):
    if refresh_date:
        return _execute(
            "UPDATE sites SET status = ?, date_ajout = DATETIME('now') WHERE id = ?",
            (status, site_id),
        )
    return _execute("UPDATE sites SET status = ? WHERE id = ?", (status, site_id))


def delete_site(site_id):
    return _execute("DELETE FROM sites WHERE id = ?", (site_id,))


def get_featured_valid_sites():
    return _fetchall(
        """
        SELECT
            s.*,
            c.nom AS categorie,
            v.nom AS ville,
            v.nom AS ville_nom,
            v.slug AS ville_slug
        FROM sites s
        JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide' AND s.en_vedette = 1
        ORDER BY c.nom ASC, s.click_count DESC, s.date_ajout DESC
        """
    )


def get_all_valid_sites_by_category_order():
    return _fetchall(
        """
        SELECT
            s.*,
            c.nom AS categorie,
            v.nom AS ville,
            v.nom AS ville_nom,
            v.slug AS ville_slug
        FROM sites s
        JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide'
        ORDER BY c.nom ASC, s.click_count DESC, s.date_ajout DESC
        """
    )


def get_new_performers():
    return _fetchall(
        """
        SELECT
            s.id,
            s.nom,
            c.nom AS categorie,
            COUNT(sc.id) AS clicks_7d
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN site_clicks sc
          ON sc.site_id = s.id
         AND sc.clicked_at >= datetime('now', '-7 days')
        WHERE s.status = 'valide'
          AND s.date_ajout >= datetime('now', '-30 days')
        GROUP BY s.id, s.nom, c.nom
        ORDER BY clicks_7d DESC
        LIMIT 10
        """
    )
