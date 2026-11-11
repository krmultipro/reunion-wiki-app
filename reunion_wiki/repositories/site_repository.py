# -*- coding: utf-8 -*-

from contextlib import contextmanager

from ..db import get_db_connection
from ..site_urls import DuplicateSiteUrlError, comparison_key, normalize_site_url
from . import site_editorial_repository, site_refusal_repository


SEARCH_SORTS = ("relevance", "popularite", "date", "nom")


def _lock_writes(connection):
    """Sérialise lecture de contrainte et écriture sans imbriquer une transaction."""
    if not connection.in_transaction:
        connection.execute('BEGIN IMMEDIATE')


@contextmanager
def site_write_transaction():
    """Fournit au service une unité de travail SQLite sérialisée et atomique."""
    connection = get_db_connection()
    try:
        _lock_writes(connection)
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_stored_site(connection, site_id):
    """Relit la fiche dans la transaction déjà détenue par l'appelant."""
    return connection.execute('SELECT * FROM sites WHERE id=?', (site_id,)).fetchone()


def _duplicate_url_id(connection, url, exclude_site_id=None):
    """Lit une identité URL déjà stockée, avec le comparateur commun des services."""
    target = comparison_key(url)
    for row in connection.execute('SELECT id, lien FROM sites'):
        if row['id'] != exclude_site_id and comparison_key(row['lien']) == target:
            return row['id']
    return None


def _assert_url_available(connection, url, exclude_site_id=None):
    """Refuse un conflit dans la transaction qui protège aussi l'écriture."""
    duplicate = _duplicate_url_id(connection, url, exclude_site_id)
    if duplicate is not None:
        raise DuplicateSiteUrlError(f'Cette URL correspond déjà au site #{duplicate}.')


def _publication_issue(connection, site):
    """Vérifie relation catégorie et unicité sur les données courantes."""
    if not connection.execute('SELECT 1 FROM categories WHERE id=?', (site['category_id'],)).fetchone():
        return 'Une catégorie principale existante est nécessaire avant publication.'
    if _duplicate_url_id(connection, site['lien'], site['id']) is not None:
        return 'Cette URL correspond déjà à un autre site ; corrigez le doublon avant publication.'
    return None


def get_publication_issue(site_id):
    """Expose les contraintes SQL avant le contrôle HTTP du service."""
    connection = get_db_connection()
    try:
        site = connection.execute('SELECT * FROM sites WHERE id=?', (site_id,)).fetchone()
        return _publication_issue(connection, site) if site else 'Proposition introuvable.'
    finally:
        connection.close()


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


def list_site_urls():
    """Retourne les URL de tous les sites, quel que soit leur statut."""
    return _fetchall("SELECT id, lien FROM sites ORDER BY id")


def record_site_url_history(site_id, proposed_url, final_url, admin_username="system"):
    """Conserve en privé une URL proposée et la destination finale choisie."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS site_url_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL,
                proposed_url TEXT NOT NULL,
                final_url TEXT NOT NULL,
                admin_username TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        cur.execute(
            """INSERT INTO site_url_history
               (site_id, proposed_url, final_url, admin_username)
               VALUES (?, ?, ?, ?)""",
            (site_id, proposed_url, final_url, admin_username),
        )
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
            s.location_scope,
            s.status,
            s.en_vedette,
            s.submitted_at,
            s.first_published_at,
            s.published_at,
            s.updated_at,
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
    Retourne les derniers sites validés par date de publication décroissante.

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
            s.date_ajout,
            s.published_at
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        WHERE s.status = 'valide'
        ORDER BY s.published_at DESC, s.id DESC
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
            s.location_scope,
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
            s.location_scope,
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


def search_sites(terms, sort="relevance", category_id=None, city_id=None, scope=None):
    """
    Recherche les sites validés contenant au moins un terme normalisé.

    Args:
        terms (list[str]): Termes sans accents, en minuscules et non vides.
        sort (str): Tri public parmi pertinence, popularité, date et nom.
        category_id (int | None): Catégorie principale à imposer.
        city_id (int | None): Commune à imposer.
        scope (str | None): Type de portée géographique à imposer.

    Returns:
        list[sqlite3.Row]:
            Liste des sites validés correspondant à la recherche.
    """

    if not terms:
        return []

    searchable_text = """
        NORMALIZE_SEARCH(
            COALESCE(s.nom, '') || ' ' ||
            COALESCE(c.nom, '') || ' ' ||
            COALESCE(s.description, '') || ' ' ||
            COALESCE(s.lien, '') || ' ' ||
            COALESCE(v.nom, '')
        )
    """
    where_sql = " OR ".join(
        f"{searchable_text} LIKE ?"
        for _ in terms
    )
    patterns = [f"%{term}%" for term in terms]
    filters_sql = [f"({where_sql})"]
    filter_params = list(patterns)
    if category_id is not None:
        filters_sql.append("s.category_id = ?")
        filter_params.append(category_id)
    if city_id is not None:
        filters_sql.append("s.ville_id = ?")
        filter_params.append(city_id)
    if scope == "city":
        filters_sql.append("s.ville_id IS NOT NULL")
    elif scope in {"island", "online"}:
        filters_sql.append("s.location_scope = ?")
        filter_params.append(scope)
    elif scope == "unspecified":
        filters_sql.append("s.ville_id IS NULL AND s.location_scope IS NULL")
    elif scope is not None:
        filters_sql.append("1 = 0")

    sort = sort if sort in SEARCH_SORTS else "relevance"
    score_params = []
    if sort == "relevance":
        score_parts = []
        weighted_fields = (
            ("s.nom", 5),
            ("c.nom", 4),
            ("s.description", 3),
            ("v.nom", 2),
            ("s.lien", 1),
        )
        for pattern in patterns:
            for field, weight in weighted_fields:
                score_parts.append(
                    f"CASE WHEN NORMALIZE_SEARCH(COALESCE({field}, '')) LIKE ? "
                    f"THEN {weight} ELSE 0 END"
                )
                score_params.append(pattern)
        score_sql = " + ".join(score_parts)
        order_sql = (
            f"({score_sql}) DESC, s.click_count DESC, "
            "s.published_at DESC, NORMALIZE_SEARCH(s.nom) ASC"
        )
    elif sort == "popularite":
        order_sql = "s.click_count DESC, s.published_at DESC, NORMALIZE_SEARCH(s.nom) ASC"
    elif sort == "date":
        order_sql = "s.published_at DESC, NORMALIZE_SEARCH(s.nom) ASC"
    else:
        order_sql = "NORMALIZE_SEARCH(s.nom) ASC, s.id ASC"

    return _fetchall(
        f"""
        SELECT
            s.id,
            s.nom,
            s.lien,
            v.nom AS ville,
            c.nom AS categorie,
            s.description,
            s.click_count,
            s.date_ajout,
            s.published_at,
            s.location_scope
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide'
          AND {' AND '.join(filters_sql)}
        ORDER BY {order_sql}
        LIMIT 100
        """,
        filter_params + score_params,
    )


def create_site(nom, ville_id, lien, description, category_id, status="en_attente", en_vedette=None,
                submitted=False, location_scope=None):
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
            Identifiant du site inséré.
    """
    if status == "valide":
        raise ValueError("La publication doit passer par le service de publication.")
    if status == 'refuse':
        raise ValueError('Un refus doit porter sur une proposition existante avec un motif.')
    connection = get_db_connection()
    try:
        _lock_writes(connection)
        lien = normalize_site_url(lien)
        _assert_url_available(connection, lien)
        cursor = connection.execute(
            """INSERT INTO sites
               (nom, ville_id, lien, description, category_id, status,
                date_ajout, submitted_at, updated_at, en_vedette, location_scope)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP,
                       CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END,
                       CURRENT_TIMESTAMP, ?, ?)""",
            (nom, ville_id, lien, description, category_id, status,
             1 if submitted else 0, 0 if en_vedette is None else en_vedette,
             location_scope),
        )
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_site(site_id, nom, ville_id, lien, description, category_id, status, en_vedette,
                expected_status=None, location_scope=None, refusal_reason=None, admin_username='admin'):
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

    conn = get_db_connection()
    try:
        _lock_writes(conn)
        cur = conn.cursor()
        previous = cur.execute("SELECT lien, status FROM sites WHERE id = ?", (site_id,)).fetchone()
        if not previous:
            conn.rollback()
            return 0
        lien = normalize_site_url(lien)
        if status == "valide" and (
            not previous or previous["status"] != "valide" or previous["lien"] != lien
        ):
            raise ValueError("La publication doit passer par le service de publication.")
        if expected_status is not None and (
            not previous or previous["status"] != expected_status
        ):
            conn.rollback()
            return 0
        _assert_url_available(conn, lien, site_id)
        new_refusal = status == 'refuse' and previous['status'] != 'refuse'
        if new_refusal:
            site_refusal_repository.validate_reason(refusal_reason)
        cur.execute(
            """UPDATE sites
               SET nom = ?, ville_id = ?, lien = ?, description = ?,
                   category_id = ?, status = ?, en_vedette = ?, location_scope = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND (? IS NULL OR status = ?)""",
            (nom, ville_id, lien, description, category_id, status, en_vedette,
             location_scope,
             site_id, expected_status, expected_status),
        )
        updated = cur.rowcount
        if updated and new_refusal:
            site_refusal_repository.record_refusal(conn, site_id, refusal_reason, admin_username)
        if updated and previous and previous[0] != lien:
            site_editorial_repository.ensure_table(conn)
            cur.execute(
                """INSERT INTO site_editorial_reviews
                   (site_id, reviewed_url, criterion, reviewed_by)
                   VALUES (?, ?, 'url_changed', 'system')""",
                (site_id, lien),
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS site_url_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    proposed_url TEXT NOT NULL,
                    final_url TEXT NOT NULL,
                    admin_username TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            cur.execute(
                """INSERT INTO site_url_history
                   (site_id, proposed_url, final_url, admin_username)
                   VALUES (?, ?, ?, 'admin')""",
                (site_id, previous[0], lien),
            )
        conn.commit()
        return updated
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_site_status(site_id, status, expected_status=None, refusal_reason=None, admin_username='admin'):
    """
    Met à jour le statut d'un site.

    Args:
        site_id (int): Identifiant du site.
        status (str): Nouveau statut.

    Returns:
        int:
            Nombre de lignes mises à jour.
    """

    if status == "valide":
        raise ValueError("La publication doit passer par le service de publication.")
    if status == 'refuse':
        connection = get_db_connection()
        try:
            _lock_writes(connection)
            previous = connection.execute('SELECT status FROM sites WHERE id=?', (site_id,)).fetchone()
            if not previous or (expected_status is not None and previous['status'] != expected_status):
                connection.rollback()
                return 0
            if previous['status'] != 'refuse':
                site_refusal_repository.validate_reason(refusal_reason)
            cursor = connection.execute(
                'UPDATE sites SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND status=?',
                (status, site_id, previous['status']))
            if cursor.rowcount and previous['status'] != 'refuse':
                site_refusal_repository.record_refusal(connection, site_id, refusal_reason, admin_username)
            connection.commit()
            return cursor.rowcount
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
    if expected_status is None:
        return _execute(
            "UPDATE sites SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, site_id),
        )
    return _execute(
        """UPDATE sites SET status = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ? AND status = ?""",
        (status, site_id, expected_status),
    )


def apply_publication(connection, site_id, admin_username, published_at, new_publication=False):
    """Publie dans la transaction appelante et trace toute nouvelle publication."""
    _lock_writes(connection)
    row = connection.execute(
        "SELECT * FROM sites WHERE id = ?",
        (site_id,),
    ).fetchone()
    if not row or row["status"] not in {"draft", "en_attente", "archived"}:
        return False
    if new_publication and row["status"] != "archived":
        return False
    if _publication_issue(connection, row):
        return False
    if not site_editorial_repository.latest_approval_matches(connection, site_id, row["lien"]):
        return False
    first_date = (
        published_at
        if not row["published_at"] and not row["first_published_at"]
        else row["first_published_at"]
    )
    current_date = published_at if new_publication or not row["published_at"] else row["published_at"]
    cursor = connection.execute(
        """UPDATE sites SET status = 'valide', first_published_at = ?,
           published_at = ?, updated_at = ? WHERE id = ? AND status = ?""",
        (first_date, current_date, published_at, site_id, row["status"]),
    )
    if cursor.rowcount != 1:
        return False
    if new_publication:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS site_publication_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, site_id INTEGER NOT NULL,
                action TEXT NOT NULL, published_at DATETIME NOT NULL,
                admin_username TEXT NOT NULL, created_at DATETIME NOT NULL)"""
        )
        connection.execute(
            """INSERT INTO site_publication_history
               (site_id, action, published_at, admin_username, created_at)
               VALUES (?, 'new_publication', ?, ?, ?)""",
            (site_id, published_at, admin_username, published_at),
        )
    return True


def publish_site(site_id, admin_username, published_at, new_publication=False):
    connection = get_db_connection()
    try:
        _lock_writes(connection)
        published = apply_publication(
            connection, site_id, admin_username, published_at, new_publication
        )
        if published:
            connection.commit()
        else:
            connection.rollback()
        return published
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


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
            COALESCE(SUM(gs.click_count), 0) AS clicks_7d
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN site_geo_daily_stats gs
          ON gs.site_id = s.id
         AND gs.stat_date >= DATE('now', '-7 days')
        WHERE s.status = 'valide'
          AND s.published_at >= datetime('now', '-30 days')
        GROUP BY s.id, s.nom, c.nom
        ORDER BY clicks_7d DESC
        LIMIT 10
        """
    )
