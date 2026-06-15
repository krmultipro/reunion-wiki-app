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


def insert_click(site_id, ip_address, user_agent):
    return _execute(
        """
        INSERT INTO site_clicks (site_id, ip_address, user_agent)
        VALUES (?, ?, ?)
        """,
        (site_id, ip_address, user_agent),
    )


def get_click_by_ip_and_site(site_id, ip_address):
    return _fetchone(
        """
        SELECT id FROM site_clicks
        WHERE site_id = ?
        AND ip_address = ?
        AND clicked_at >= datetime('now', '-30 minutes')
        """,
        (site_id, ip_address),
    )


def get_click_by_id(click_id):
    return _fetchone("SELECT site_id FROM site_clicks WHERE id = ?", (click_id,))


def increment_click_count(site_id):
    return _execute("UPDATE sites SET click_count = click_count + 1 WHERE id = ?", (site_id,))


def insert_click_and_increment_count(site_id, ip_address, user_agent):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE sites SET click_count = click_count + 1 WHERE id = ?", (site_id,))
        cur.execute(
            """
            INSERT INTO site_clicks (site_id, ip_address, user_agent)
            VALUES (?, ?, ?)
            """,
            (site_id, ip_address, user_agent),
        )
        conn.commit()
        return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def decrement_click_count(site_id):
    return _execute(
        """
        UPDATE sites
        SET click_count = CASE WHEN click_count > 0 THEN click_count - 1 ELSE 0 END
        WHERE id = ?
        """,
        (site_id,),
    )


def delete_click(click_id):
    return _execute("DELETE FROM site_clicks WHERE id = ?", (click_id,))


def delete_click_and_decrement_site(click_id, site_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM site_clicks WHERE id = ?", (click_id,))
        deleted = cur.rowcount
        if deleted:
            cur.execute(
                """
                UPDATE sites
                SET click_count = CASE WHEN click_count > 0 THEN click_count - 1 ELSE 0 END
                WHERE id = ?
                """,
                (site_id,),
            )
        conn.commit()
        return deleted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def count_clicks(where_sql, params):
    return _fetchone(
        f"""
        SELECT COUNT(*) AS total
        FROM site_clicks sc
        JOIN sites s ON s.id = sc.site_id
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE {where_sql}
        """,
        params,
    )


def get_clicks(where_sql, sort_sql, params, limit, offset):
    return _fetchall(
        f"""
        SELECT
            sc.id,
            sc.site_id,
            sc.ip_address,
            sc.user_agent,
            sc.clicked_at,
            s.nom AS site_nom,
            c.nom AS categorie,
            v.nom AS ville,
            s.status
        FROM site_clicks sc
        JOIN sites s ON s.id = sc.site_id
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE {where_sql}
        ORDER BY {sort_sql}
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    )


def get_click_stats():
    return _fetchall(
        """
        SELECT site_id, COUNT(*) AS total
        FROM site_clicks
        GROUP BY site_id
        """
    )


def get_trending_sites():
    return _fetchall(
        """
        WITH clicks_7 AS (
            SELECT site_id, COUNT(*) AS c7
            FROM site_clicks
            WHERE clicked_at >= datetime('now', '-7 days')
            GROUP BY site_id
        ),
        clicks_prev7 AS (
            SELECT site_id, COUNT(*) AS cprev
            FROM site_clicks
            WHERE clicked_at >= datetime('now', '-14 days')
              AND clicked_at < datetime('now', '-7 days')
            GROUP BY site_id
        )
        SELECT
            s.id,
            s.nom,
            c.nom AS categorie,
            COALESCE(c7.c7, 0) AS clicks_7d,
            COALESCE(cp.cprev, 0) AS clicks_prev_7d,
            CASE
                WHEN COALESCE(cp.cprev, 0) = 0 THEN NULL
                ELSE ROUND((COALESCE(c7.c7, 0) - cp.cprev) * 100.0 / cp.cprev, 1)
            END AS growth_pct
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN clicks_7 c7 ON c7.site_id = s.id
        LEFT JOIN clicks_prev7 cp ON cp.site_id = s.id
        WHERE s.status = 'valide'
        ORDER BY clicks_7d DESC, growth_pct DESC
        LIMIT 10
        """
    )


def get_stable_sites():
    return _fetchall(
        """
        SELECT
            s.id,
            s.nom,
            c.nom AS categorie,
            COUNT(sc.id) AS clicks_30d
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN site_clicks sc
          ON sc.site_id = s.id
         AND sc.clicked_at >= datetime('now', '-30 days')
        WHERE s.status = 'valide'
        GROUP BY s.id, s.nom, c.nom
        ORDER BY clicks_30d DESC
        LIMIT 10
        """
    )
