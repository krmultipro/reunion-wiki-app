# -*- coding: utf-8 -*-

from ..db import get_db_connection


def register_aggregated_click(site_id, visitor_token, zone, stat_date):
    """Déduplique puis agrège un clic sans conserver d'adresse IP brute."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS click_deduplication (
                site_id INTEGER NOT NULL, visitor_token TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                PRIMARY KEY (site_id, visitor_token)
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS site_geo_daily_stats (
                site_id INTEGER NOT NULL, stat_date TEXT NOT NULL, zone TEXT NOT NULL,
                click_count INTEGER NOT NULL DEFAULT 0,
                visitor_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE (site_id, stat_date, zone)
            )"""
        )
        cur.execute("DELETE FROM click_deduplication WHERE expires_at <= CURRENT_TIMESTAMP")
        existing = cur.execute(
            "SELECT 1 FROM click_deduplication WHERE site_id = ? AND visitor_token = ? AND expires_at > CURRENT_TIMESTAMP",
            (site_id, visitor_token),
        ).fetchone()
        if existing:
            conn.commit()
            return False
        cur.execute(
            "INSERT INTO click_deduplication (site_id, visitor_token, expires_at) VALUES (?, ?, DATETIME('now', '+30 minutes'))",
            (site_id, visitor_token),
        )
        cur.execute(
            """
            INSERT INTO site_geo_daily_stats (site_id, stat_date, zone, click_count, visitor_count)
            VALUES (?, ?, ?, 1, 1)
            ON CONFLICT(site_id, stat_date, zone) DO UPDATE SET
                click_count = click_count + 1,
                visitor_count = visitor_count + 1
            """,
            (site_id, stat_date, zone),
        )
        cur.execute("UPDATE sites SET click_count = click_count + 1 WHERE id = ?", (site_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def purge_private_click_data():
    """Supprime les empreintes expirées et les agrégats vieux de plus de 12 mois."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM click_deduplication WHERE expires_at <= CURRENT_TIMESTAMP")
        tokens = cur.rowcount
        cur.execute("DELETE FROM site_geo_daily_stats WHERE stat_date < DATE('now', '+4 hours', '-12 months')")
        aggregates = cur.rowcount
        conn.commit()
        return tokens, aggregates
    finally:
        conn.close()


def get_admin_geo_stats(days=30, privacy_threshold=10):
    """Retourne uniquement des statistiques agrégées respectant le seuil privé."""
    return _fetchall(
        """
        WITH zone_totals AS (
            SELECT gs.site_id, s.nom AS site_nom, gs.zone,
                   SUM(gs.click_count) AS clicks,
                   SUM(gs.visitor_count) AS visitors
            FROM site_geo_daily_stats gs
            JOIN sites s ON s.id = gs.site_id
            WHERE gs.stat_date >= DATE('now', ?)
            GROUP BY gs.site_id, s.nom, gs.zone
        )
        SELECT site_id, site_nom,
               CASE WHEN visitors >= ? THEN zone ELSE 'Sous le seuil' END AS zone_display,
               SUM(clicks) AS click_count,
               SUM(visitors) AS visitor_count
        FROM zone_totals
        GROUP BY site_id, site_nom, zone_display
        ORDER BY click_count DESC, site_nom COLLATE NOCASE
        """,
        (f"-{int(days)} days", int(privacy_threshold)),
    )


def correct_geo_aggregate(site_id, stat_date, zone, new_count, admin_username, reason):
    """Corrige un agrégat, ajuste le total du site et journalise l'action."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute(
            "SELECT click_count FROM site_geo_daily_stats WHERE site_id=? AND stat_date=? AND zone=?",
            (site_id, stat_date, zone),
        ).fetchone()
        if not row:
            return False
        old_count = int(row[0])
        new_count = int(new_count)
        cur.execute(
            "UPDATE site_geo_daily_stats SET click_count=? WHERE site_id=? AND stat_date=? AND zone=?",
            (new_count, site_id, stat_date, zone),
        )
        cur.execute(
            "UPDATE sites SET click_count = MAX(0, click_count + ?) WHERE id=?",
            (new_count - old_count, site_id),
        )
        cur.execute(
            """INSERT INTO site_stats_audit
               (site_id, stat_date, zone, old_count, new_count, admin_username, reason)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (site_id, stat_date, zone, old_count, new_count, admin_username, reason),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_geo_aggregate_rows(days=30, privacy_threshold=10):
    """Retourne les agrégats corrigeables qui dépassent le seuil de confidentialité."""
    return _fetchall(
        """SELECT gs.site_id, s.nom AS site_nom, gs.stat_date, gs.zone,
                  gs.click_count, gs.visitor_count
           FROM site_geo_daily_stats gs JOIN sites s ON s.id=gs.site_id
           WHERE gs.stat_date >= DATE('now', ?)
             AND gs.visitor_count >= ?
           ORDER BY gs.stat_date DESC, s.nom COLLATE NOCASE, gs.zone""",
        (f"-{int(days)} days", int(privacy_threshold)),
    )


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


def get_click_stats():
    """
    Retourne le nombre total de clics groupé par site.

    Returns:
        list[sqlite3.Row]:
            Liste des identifiants de sites avec leur total de clics.
    """

    return _fetchall(
        """
        SELECT site_id, SUM(click_count) AS total
        FROM site_geo_daily_stats
        GROUP BY site_id
        """
    )


def get_trending_sites():
    """
    Retourne les sites ayant le plus de clics récents et leur progression.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés avec clics 7 jours, période précédente et croissance.
    """

    return _fetchall(
        """
        WITH clicks_7 AS (
            SELECT site_id, SUM(click_count) AS c7
            FROM site_geo_daily_stats
            WHERE stat_date >= DATE('now', '-7 days')
            GROUP BY site_id
        ),
        clicks_prev7 AS (
            SELECT site_id, SUM(click_count) AS cprev
            FROM site_geo_daily_stats
            WHERE stat_date >= DATE('now', '-14 days')
              AND stat_date < DATE('now', '-7 days')
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
        WHERE s.status = 'valide' AND COALESCE(c7.c7, 0) > 0
        ORDER BY clicks_7d DESC, growth_pct DESC
        LIMIT 10
        """
    )


def get_stable_sites():
    """
    Retourne les sites les plus cliqués sur les 30 derniers jours.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés classés par clics sur 30 jours.
    """

    return _fetchall(
        """
        SELECT
            s.id,
            s.nom,
            c.nom AS categorie,
            COALESCE(SUM(gs.click_count), 0) AS clicks_30d
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN site_geo_daily_stats gs
          ON gs.site_id = s.id
         AND gs.stat_date >= DATE('now', '-30 days')
        WHERE s.status = 'valide'
        GROUP BY s.id, s.nom, c.nom
        HAVING clicks_30d > 0
        ORDER BY clicks_30d DESC
        LIMIT 10
        """
    )
