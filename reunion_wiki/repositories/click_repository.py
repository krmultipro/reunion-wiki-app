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
    """
    Insère un clic dans la table site_clicks.

    Args:
        site_id (int): Identifiant du site cliqué.
        ip_address (str): Adresse IP du visiteur.
        user_agent (str): User-Agent du visiteur.

    Returns:
        int:
            Nombre de lignes insérées.
    """

    return _execute(
        """
        INSERT INTO site_clicks (site_id, ip_address, user_agent)
        VALUES (?, ?, ?)
        """,
        (site_id, ip_address, user_agent),
    )


def get_click_by_ip_and_site(site_id, ip_address):
    """
    Récupère un clic récent pour un couple site/IP.

    Args:
        site_id (int): Identifiant du site.
        ip_address (str): Adresse IP du visiteur.

    Returns:
        sqlite3.Row | None:
            Clic trouvé sur la fenêtre récente, ou None.
    """

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
    """
    Récupère le site associé à un clic.

    Args:
        click_id (int): Identifiant du clic.

    Returns:
        sqlite3.Row | None:
            Ligne contenant site_id, ou None si le clic est introuvable.
    """

    return _fetchone("SELECT site_id FROM site_clicks WHERE id = ?", (click_id,))


def increment_click_count(site_id):
    """
    Incrémente le compteur de clics d'un site.

    Args:
        site_id (int): Identifiant du site.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute("UPDATE sites SET click_count = click_count + 1 WHERE id = ?", (site_id,))


def insert_click_and_increment_count(site_id, ip_address, user_agent):
    """
    Incrémente le compteur d'un site et insère le clic correspondant.

    Args:
        site_id (int): Identifiant du site cliqué.
        ip_address (str): Adresse IP du visiteur.
        user_agent (str): User-Agent du visiteur.

    Returns:
        int:
            Nombre de lignes affectées par la dernière insertion.
    """

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
    """
    Décrémente le compteur de clics d'un site sans descendre sous zéro.

    Args:
        site_id (int): Identifiant du site.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE sites
        SET click_count = CASE WHEN click_count > 0 THEN click_count - 1 ELSE 0 END
        WHERE id = ?
        """,
        (site_id,),
    )


def delete_click(click_id):
    """
    Supprime un clic à partir de son identifiant.

    Args:
        click_id (int): Identifiant du clic.

    Returns:
        int:
            Nombre de lignes supprimées.
    """

    return _execute("DELETE FROM site_clicks WHERE id = ?", (click_id,))


def delete_click_and_decrement_site(click_id, site_id):
    """
    Supprime un clic et décrémente le compteur du site associé.

    Args:
        click_id (int): Identifiant du clic à supprimer.
        site_id (int): Identifiant du site associé au clic.

    Returns:
        int:
            Nombre de clics supprimés.
    """

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
    """
    Compte les clics correspondant aux filtres fournis.

    Args:
        where_sql (str): Clause WHERE déjà construite par l'appelant.
        params (list | tuple): Paramètres SQL associés à la clause WHERE.

    Returns:
        sqlite3.Row:
            Ligne contenant le total.
    """

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
    """
    Retourne les clics paginés pour l'administration.

    Args:
        where_sql (str): Clause WHERE déjà construite par l'appelant.
        sort_sql (str): Clause ORDER BY déjà construite par l'appelant.
        params (list): Paramètres SQL associés aux filtres.
        limit (int): Nombre maximum de clics à retourner.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Liste des clics avec site, catégorie, ville et statut.
    """

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
    """
    Retourne le nombre total de clics groupé par site.

    Returns:
        list[sqlite3.Row]:
            Liste des identifiants de sites avec leur total de clics.
    """

    return _fetchall(
        """
        SELECT site_id, COUNT(*) AS total
        FROM site_clicks
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
