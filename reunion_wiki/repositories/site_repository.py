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
    """
    Récupère un site à partir de son identifiant pour l'administration.

    Args:
        site_id (int): Identifiant du site.

    Returns:
        sqlite3.Row | None:
            Site trouvé avec sa catégorie et sa ville, ou None si inexistant.
    """

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
    """
    Récupère l'URL et le compteur de clics d'un site validé.

    Args:
        site_id (int): Identifiant du site.

    Returns:
        sqlite3.Row | None:
            Site validé contenant lien et click_count, ou None si introuvable.
    """

    return _fetchone(
        "SELECT lien, click_count FROM sites WHERE id = ? AND status = 'valide'",
        (site_id,),
    )




def get_latest_sites(limit=None):
    """
    Retourne les derniers sites validés par date d'ajout décroissante.

    Args:
        limit (int | None): Nombre maximum de sites à retourner.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés les plus récemment ajoutés.
    """

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
    """
    Retourne les sites validés les plus visités.

    Args:
        limit (int | None): Nombre maximum de sites à retourner.

    Returns:
        list[sqlite3.Row]:
            Liste des sites classés par nombre de clics décroissant.
    """

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
    """
    Retourne les sites validés d'une catégorie.

    Args:
        category_id (int): Identifiant de la catégorie.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés associés à la catégorie.
    """

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
    """
    Retourne les statistiques publiques des villes.

    Returns:
        list[sqlite3.Row]:
            Liste des villes avec nombre de sites validés et total de clics.
    """

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
    """
    Récupère une ville à partir de son slug.

    Args:
        slug (str): Slug de la ville.

    Returns:
        sqlite3.Row | None:
            Ville trouvée ou None si inexistante.
    """

    return _fetchone("SELECT id, nom, slug FROM villes WHERE slug = ?", (slug,))


def get_admin_city_filters():
    """
    Retourne les villes disponibles pour les filtres d'administration.

    Returns:
        list[sqlite3.Row]:
            Liste des villes triées par nom.
    """

    return _fetchall("SELECT nom, slug FROM villes ORDER BY nom COLLATE NOCASE ASC")


def get_sites_by_city_id(ville_id):
    """
    Retourne les sites validés associés à une ville.

    Args:
        ville_id (int): Identifiant de la ville.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés pour cette ville.
    """

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
    """
    Retourne le total des clics des sites validés d'une ville.

    Args:
        ville_id (int): Identifiant de la ville.

    Returns:
        sqlite3.Row:
            Ligne contenant total_clicks.
    """

    return _fetchone(
        """
        SELECT COALESCE(SUM(click_count), 0) AS total_clicks
        FROM sites
        WHERE status = 'valide' AND ville_id = ?
        """,
        (ville_id,),
    )


def get_pending_sites():
    """
    Retourne les sites en attente de validation.

    Returns:
        list[sqlite3.Row]:
            Liste des sites dont le statut est en_attente.
    """

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
    """
    Compte les sites par statut.

    Returns:
        list[sqlite3.Row]:
            Liste des statuts avec leur nombre de sites.
    """

    return _fetchall("SELECT status, COUNT(*) as total FROM sites GROUP BY status")


def count_sites_for_admin(where_sql, params):
    """
    Compte les sites correspondant aux filtres d'administration.

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
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE {where_sql}
        """,
        params,
    )


def get_sites_for_admin(where_sql, sort_sql, params, limit, offset):
    """
    Retourne les sites paginés pour l'administration.

    Args:
        where_sql (str): Clause WHERE déjà construite par l'appelant.
        sort_sql (str): Clause ORDER BY déjà construite par l'appelant.
        params (list): Paramètres SQL associés aux filtres.
        limit (int): Nombre maximum de sites à retourner.
        offset (int): Décalage de pagination.

    Returns:
        list[sqlite3.Row]:
            Liste des sites avec catégorie, ville, statut et compteur de clics.
    """

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
    """
    Recherche des sites validés par nom, catégorie, description, lien ou ville.

    Args:
        like (str): Motif SQL LIKE principal.
        like_city (str): Motif SQL LIKE pour la ville normalisée.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés correspondant à la recherche.
    """

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
    """
    Crée un nouveau site.

    Args:
        nom (str): Nom du site.
        ville_id (int | None): Identifiant de la ville associée.
        lien (str): URL du site.
        description (str): Description du site.
        category_id (int): Identifiant de la catégorie.
        status (str): Statut initial du site.
        en_vedette (int | None): Valeur du marqueur de mise en avant.

    Returns:
        int:
            Nombre de lignes insérées.
    """

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
    """
    Met à jour les données principales d'un site.

    Args:
        site_id (int): Identifiant du site.
        nom (str): Nouveau nom du site.
        ville_id (int | None): Nouvel identifiant de ville.
        lien (str): Nouvelle URL du site.
        description (str): Nouvelle description du site.
        category_id (int): Nouvel identifiant de catégorie.
        status (str): Nouveau statut du site.
        en_vedette (int): Nouvelle valeur du marqueur de mise en avant.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    return _execute(
        """
        UPDATE sites
        SET nom = ?, ville_id = ?, lien = ?, description = ?, category_id = ?, status = ?, en_vedette = ?
        WHERE id = ?
        """,
        (nom, ville_id, lien, description, category_id, status, en_vedette, site_id),
    )


def update_site_status(site_id, status, refresh_date=False):
    """
    Met à jour le statut d'un site.

    Args:
        site_id (int): Identifiant du site.
        status (str): Nouveau statut.
        refresh_date (bool): Indique si date_ajout doit être remise à maintenant.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    if refresh_date:
        return _execute(
            "UPDATE sites SET status = ?, date_ajout = DATETIME('now') WHERE id = ?",
            (status, site_id),
        )
    return _execute("UPDATE sites SET status = ? WHERE id = ?", (status, site_id))


def delete_site(site_id):
    """
    Supprime un site à partir de son identifiant.

    Args:
        site_id (int): Identifiant du site.

    Returns:
        int:
            Nombre de lignes supprimées.
    """

    return _execute("DELETE FROM sites WHERE id = ?", (site_id,))


def get_featured_valid_sites():
    """
    Retourne les sites validés mis en avant.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés marqués en vedette avec catégorie et ville.
    """

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
    """
    Retourne tous les sites validés triés par catégorie.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés avec catégorie et ville.
    """

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
    """
    Retourne les nouveaux sites performants sur les clics récents.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés ajoutés récemment, classés par clics sur 7 jours.
    """

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
