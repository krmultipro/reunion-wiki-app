"""Site-related queries and helpers."""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional, Sequence, Tuple

from flask import current_app, g, has_request_context

from ..database import DatabaseError, db_query, db_transaction, get_db_connection
from ..utils.text import slugify


def get_sites_en_vedette(limit: int = 3) -> Dict[str, List[sqlite3.Row]]:
    """Return the latest validated sites per category."""
    conn = get_db_connection()
    if not conn:
        return {}

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT categorie
            FROM sites
            WHERE status = 'valide'
            """
        )
        categories = [row["categorie"] for row in cur.fetchall() if row["categorie"]]
        if has_request_context():
            g._categories_cache = categories

        data: Dict[str, List[sqlite3.Row]] = {cat: [] for cat in categories}

        cur.execute(
            """
            SELECT *
            FROM sites
            WHERE status = 'valide'
            ORDER BY categorie ASC, date_ajout DESC
            """
        )

        for site in cur.fetchall():
            category = site["categorie"]
            if category in data and len(data[category]) < limit:
                data[category].append(site)

        return data
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération des sites en vedette: {exc}"
        )
        return {}
    finally:
        conn.close()


def get_derniers_sites_global(limit: int = 3) -> Sequence[sqlite3.Row]:
    """Return the latest validated sites regardless of category."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT nom, lien, categorie, description, date_ajout
            FROM sites
            WHERE status = 'valide'
            ORDER BY date_ajout DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération des derniers sites: {exc}"
        )
        return []
    finally:
        conn.close()


def get_categories() -> List[str]:
    """Return distinct categories that have at least one validated site."""
    if has_request_context() and hasattr(g, "_categories_cache"):
        return g._categories_cache

    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
        categories = [row[0] for row in cur.fetchall() if row[0]]
        if has_request_context():
            g._categories_cache = categories
        return categories
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération des catégories: {exc}"
        )
        return []
    finally:
        conn.close()


def get_categories_slug() -> Dict[str, str]:
    """Return a mapping between category names and their slugs."""
    if has_request_context() and hasattr(g, "_categories_slug_cache"):
        return g._categories_slug_cache  # type: ignore[return-value]

    categories = get_categories()
    mapping = {cat: slugify(cat) for cat in categories}

    if has_request_context():
        g._categories_slug_cache = mapping  # type: ignore[attr-defined]
    return mapping


def get_nom_categorie_depuis_slug(slug: str) -> str | None:
    """Return the non-slugged category name from its slug."""
    for cat, cat_slug in get_categories_slug().items():
        if cat_slug == slug:
            return cat
    return None


def get_sites_by_category(categorie: str) -> List[sqlite3.Row]:
    """Return all validated sites for a given category."""
    try:
        with db_query() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT *
                FROM sites
                WHERE categorie = ? AND status = 'valide'
                ORDER BY en_vedette DESC, date_ajout DESC
                """,
                (categorie,),
            )
            return cur.fetchall()
    except DatabaseError:
        return []


def get_all_validated_sites() -> List[sqlite3.Row]:
    """Return all validated sites ordered by date."""
    try:
        with db_query() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nom, lien, categorie, description, date_ajout
                FROM sites
                WHERE status = 'valide'
                ORDER BY date_ajout DESC
                """
            )
            return cur.fetchall()
    except DatabaseError:
        return []


def search_sites(query: str, limit: int = 100) -> List[sqlite3.Row]:
    """Search sites by query string in nom, categorie, description, ville, lien."""
    if not query or len(query) < 2:
        return []
    
    try:
        with db_query() as conn:
            cur = conn.cursor()
            like_query = f"%{query}%"
            cur.execute(
                """
                SELECT id, nom, categorie, ville, lien, description, date_ajout
                FROM sites
                WHERE status = 'valide'
                  AND (
                        nom LIKE ? COLLATE NOCASE
                        OR categorie LIKE ? COLLATE NOCASE
                        OR description LIKE ? COLLATE NOCASE
                        OR IFNULL(ville, '') LIKE ? COLLATE NOCASE
                        OR lien LIKE ? COLLATE NOCASE
                  )
                ORDER BY en_vedette DESC, date_ajout DESC
                LIMIT ?
                """,
                (like_query, like_query, like_query, like_query, like_query, limit),
            )
            return cur.fetchall()
    except DatabaseError:
        return []


def submit_site_proposal(
    nom: str, lien: str, description: str, categorie: str, ville: Optional[str] = None
) -> Tuple[bool, str]:
    """Submit a new site proposal. Returns (success, message)."""
    if categorie not in get_categories():
        return False, "Catégorie non valide."
    
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout)
                VALUES (?, ?, ?, ?, ?, 'en_attente', DATETIME('now'))
                """,
                (nom, ville, lien, description, categorie),
            )
        return True, "Merci, ta proposition a bien été envoyée ! Elle sera validée prochainement."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de l'insertion du site: {exc}")
        return False, "Erreur lors de l'enregistrement. Veuillez réessayer."


def get_admin_sites(status_filter: str = "en_attente", search_query: str = "") -> Dict[str, any]:
    """Get sites for admin dashboard with filters. Returns dict with entries and stats."""
    allowed_statuses = {"en_attente", "valide", "refuse", "tout"}
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"
    
    try:
        with db_query() as conn:
            cur = conn.cursor()
            params: List[str] = []
            query_clause = ""
            
            if search_query and len(search_query) >= 2:
                like_query = f"%{search_query}%"
                query_clause = """AND (
                        nom LIKE ? COLLATE NOCASE
                        OR categorie LIKE ? COLLATE NOCASE
                        OR description LIKE ? COLLATE NOCASE
                        OR IFNULL(ville, '') LIKE ? COLLATE NOCASE
                        OR lien LIKE ? COLLATE NOCASE
                    )"""
                params.extend([like_query] * 5)
            
            status_clause = ""
            if status_filter != "tout":
                status_clause = "AND status = ?"
                params.append(status_filter)
            
            cur.execute(
                f"""
                SELECT id, nom, categorie, ville, lien, description, status, date_ajout
                FROM sites
                WHERE 1 = 1
                {status_clause}
                {query_clause}
                ORDER BY
                    CASE WHEN status = 'en_attente' THEN 0 ELSE 1 END,
                    date_ajout DESC,
                    id DESC
                LIMIT 200
                """,
                tuple(params),
            )
            entries = cur.fetchall()
            
            cur.execute("SELECT status, COUNT(*) as total FROM sites GROUP BY status")
            stats_rows = cur.fetchall()
            
            stats = {row["status"]: row["total"] for row in stats_rows}
            stats["tout"] = sum(stats.values())
            
            return {"entries": entries, "stats": stats}
    except DatabaseError:
        return {"entries": [], "stats": {"en_attente": 0, "valide": 0, "refuse": 0, "tout": 0}}


def get_site_by_id(site_id: int) -> Optional[sqlite3.Row]:
    """Get a site by its ID."""
    try:
        with db_query() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, nom, ville, lien, description, categorie, status
                FROM sites
                WHERE id = ?
                """,
                (site_id,),
            )
            return cur.fetchone()
    except DatabaseError:
        return None


def update_site_status(site_id: int, status: str) -> Tuple[bool, str]:
    """Update site status. Returns (success, message)."""
    valid_statuses = {"valide", "refuse"}
    if status not in valid_statuses:
        return False, "Statut invalide."
    
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            if status == "valide":
                cur.execute(
                    "UPDATE sites SET status = 'valide', date_ajout = DATETIME('now') WHERE id = ?",
                    (site_id,),
                )
                message = "Proposition validée et publiée."
            else:
                cur.execute(
                    "UPDATE sites SET status = 'refuse' WHERE id = ?",
                    (site_id,),
                )
                message = "Proposition refusée."
            
            if cur.rowcount == 0:
                return False, "La proposition est introuvable."
            
            return True, message
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la mise à jour du site {site_id}: {exc}")
        return False, "Erreur lors de la mise à jour."


def delete_site(site_id: int) -> Tuple[bool, str]:
    """Delete a site. Returns (success, message)."""
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM sites WHERE id = ?", (site_id,))
            if cur.rowcount == 0:
                return False, "La proposition est introuvable."
            return True, "Proposition supprimée."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la suppression du site {site_id}: {exc}")
        return False, "Erreur lors de la suppression."


def update_site_full(
    site_id: int,
    nom: str,
    ville: Optional[str],
    lien: str,
    description: str,
    categorie: str,
    status: str,
) -> Tuple[bool, str]:
    """Update all fields of a site. Returns (success, message)."""
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE sites
                SET nom = ?, ville = ?, lien = ?, description = ?, categorie = ?, status = ?
                WHERE id = ?
                """,
                (nom, ville, lien, description, categorie, status, site_id),
            )
            if cur.rowcount == 0:
                return False, "La mise à jour a échoué : proposition introuvable."
            return True, "Proposition mise à jour avec succès."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la mise à jour du site {site_id}: {exc}")
        return False, "Erreur lors de la mise à jour."


def create_site_admin(
    nom: str,
    ville: Optional[str],
    lien: str,
    description: str,
    categorie: str,
) -> Tuple[bool, str]:
    """Create a new site directly published (admin only). Returns (success, message)."""
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout, en_vedette)
                VALUES (?, ?, ?, ?, ?, 'valide', DATETIME('now'), 0)
                """,
                (nom, ville, lien, description, categorie),
            )
        return True, "Nouveau site ajouté et publié."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la création d'un site depuis l'admin: {exc}")
        return False, "Erreur lors de l'ajout du site."
