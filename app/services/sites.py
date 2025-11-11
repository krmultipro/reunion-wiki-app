"""Site-related queries and helpers."""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Optional, Sequence, Tuple

from flask import current_app, g, has_request_context

from ..database import DatabaseError, db_query, db_transaction, get_db_connection, get_db_path
from ..utils.text import slugify



def ensure_sites_table() -> None:
    """Ensure the sites table has the display_order column."""
    try:
        # Vérifier si on est dans un contexte Flask
        from flask import has_app_context
        if not has_app_context():
            return
    except ImportError:
        return
    
    conn = None
    try:
        conn = sqlite3.connect(get_db_path())
        # Vérifier si la colonne existe déjà en essayant de la sélectionner
        try:
            conn.execute("SELECT display_order FROM sites LIMIT 1")
            # Si ça fonctionne, la colonne existe déjà
        except sqlite3.OperationalError:
            # La colonne n'existe pas, on l'ajoute
            try:
                conn.execute("ALTER TABLE sites ADD COLUMN display_order INTEGER DEFAULT 0")
                conn.commit()
            except sqlite3.OperationalError:
                # Peut-être que la table n'existe pas encore ou autre erreur
                pass
    except Exception:
        # En cas d'erreur, on continue quand même
        pass
    finally:
        if conn:
            conn.close()


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

        # Vérifier si display_order existe
        try:
            cur.execute("SELECT display_order FROM sites LIMIT 1")
            has_display_order = True
        except sqlite3.OperationalError:
            has_display_order = False
        
        if has_display_order:
            cur.execute(
                """
                SELECT *
                FROM sites
                WHERE status = 'valide'
                ORDER BY categorie ASC, display_order ASC, date_ajout DESC
                """
            )
        else:
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
            # Vérifier si display_order existe
            try:
                cur.execute("SELECT display_order FROM sites LIMIT 1")
                has_display_order = True
            except sqlite3.OperationalError:
                has_display_order = False
            
            if has_display_order:
                cur.execute(
                    """
                    SELECT *
                    FROM sites
                    WHERE categorie = ? AND status = 'valide'
                    ORDER BY display_order ASC, en_vedette DESC, date_ajout DESC
                    """,
                    (categorie,),
                )
            else:
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


def get_admin_sites(
    status_filter: str = "en_attente", 
    search_query: str = "",
    sort_by: str = "date_ajout",
    sort_order: str = "desc",
    category_filter: Optional[str] = None
) -> Dict[str, any]:
    """Get sites for admin dashboard with filters. Returns dict with entries and stats."""
    ensure_sites_table()
    allowed_statuses = {"en_attente", "valide", "refuse", "tout"}
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"
    
    # Colonnes triables valides
    allowed_sort_columns = {
        "nom": "nom",
        "categorie": "categorie",
        "status": "status",
        "date_ajout": "date_ajout",
        "display_order": "display_order"
    }
    
    sort_column = allowed_sort_columns.get(sort_by, "date_ajout")
    sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
    
    try:
        # Vérifier d'abord si la colonne display_order existe
        ensure_sites_table()
        
        with db_query() as conn:
            cur = conn.cursor()
            # Vérifier si display_order existe dans la table
            try:
                cur.execute("SELECT display_order FROM sites LIMIT 1")
                has_display_order = True
            except sqlite3.OperationalError:
                has_display_order = False
            
            params: List[str] = []
            if has_display_order:
                query = """
                    SELECT id, nom, categorie, ville, lien, description, status, date_ajout, display_order
                    FROM sites
                    WHERE 1 = 1
                """
            else:
                query = """
                    SELECT id, nom, categorie, ville, lien, description, status, date_ajout, 0 as display_order
                    FROM sites
                    WHERE 1 = 1
                """
            
            if status_filter != "tout":
                query += " AND status = ?"
                params.append(status_filter)
            
            if category_filter:
                query += " AND categorie = ?"
                params.append(category_filter)
            
            if search_query and len(search_query) >= 2:
                like_query = f"%{search_query}%"
                query += """
                    AND (
                        nom LIKE ? COLLATE NOCASE
                        OR categorie LIKE ? COLLATE NOCASE
                        OR description LIKE ? COLLATE NOCASE
                        OR IFNULL(ville, '') LIKE ? COLLATE NOCASE
                        OR lien LIKE ? COLLATE NOCASE
                    )
                """
                params.extend([like_query] * 5)
            
            # Si on filtre par catégorie et que le statut est "valide", utiliser display_order par défaut
            if category_filter and status_filter == "valide" and sort_by == "date_ajout" and has_display_order:
                query += """
                    ORDER BY
                        CASE WHEN status = 'en_attente' THEN 0 ELSE 1 END,
                        display_order ASC,
                        nom ASC,
                        id DESC
                """
            else:
                # Si display_order n'existe pas et qu'on veut trier par display_order, utiliser date_ajout
                if sort_by == "display_order" and not has_display_order:
                    sort_column = "date_ajout"
                query += f"""
                    ORDER BY
                        CASE WHEN status = 'en_attente' THEN 0 ELSE 1 END,
                        {sort_column} {sort_direction},
                        id DESC
                """
            
            query += " LIMIT 200"
            
            cur.execute(query, tuple(params))
            entries = cur.fetchall()
            
            # Stats par statut
            stats_query = "SELECT status, COUNT(*) as total FROM sites WHERE 1 = 1"
            stats_params = []
            if category_filter:
                stats_query += " AND categorie = ?"
                stats_params.append(category_filter)
            stats_query += " GROUP BY status"
            
            cur.execute(stats_query, tuple(stats_params))
            stats_rows = cur.fetchall()
            
            stats = {row["status"]: row["total"] for row in stats_rows}
            stats["tout"] = sum(stats.values())
            
            # Stats par catégorie pour les sites publiés
            category_stats = {}
            try:
                cur.execute(
                    "SELECT categorie, COUNT(*) AS total FROM sites WHERE status = 'valide' GROUP BY categorie"
                )
                category_stats_rows = cur.fetchall()
                category_stats = {row["categorie"] or "": row["total"] for row in category_stats_rows}
            except Exception:
                # Si erreur, on retourne un dict vide
                pass
            
            return {"entries": entries, "stats": stats, "category_stats": category_stats}
    except DatabaseError:
        return {"entries": [], "stats": {"en_attente": 0, "valide": 0, "refuse": 0, "tout": 0}, "category_stats": {}}


def get_site_by_id(site_id: int) -> Optional[sqlite3.Row]:
    """Get a site by its ID."""
    ensure_sites_table()
    try:
        with db_query() as conn:
            cur = conn.cursor()
            # Vérifier si display_order existe
            try:
                cur.execute("SELECT display_order FROM sites LIMIT 1")
                has_display_order = True
            except sqlite3.OperationalError:
                has_display_order = False
            
            if has_display_order:
                cur.execute(
                    """
                    SELECT id, nom, ville, lien, description, categorie, status, display_order
                    FROM sites
                    WHERE id = ?
                    """,
                    (site_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT id, nom, ville, lien, description, categorie, status, 0 as display_order
                    FROM sites
                    WHERE id = ?
                    """,
                    (site_id,),
                )
            return cur.fetchone()
    except DatabaseError:
        return None


def move_site_order(site_id: int, direction: str, category: Optional[str] = None) -> Tuple[bool, str]:
    """Move a site up or down in display order. Returns (success, message)."""
    ensure_sites_table()
    if direction not in ["up", "down"]:
        return False, "Direction invalide."
    
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            # Récupérer le site actuel
            cur.execute(
                "SELECT id, display_order, categorie FROM sites WHERE id = ?",
                (site_id,)
            )
            site = cur.fetchone()
            if not site:
                return False, "Site introuvable."
            
            current_order = site["display_order"] or 0
            site_category = site["categorie"] or ""
            
            # Filtrer par catégorie et statut valide pour l'ordre d'affichage public
            category_filter = ""
            params = []
            if category:
                category_filter = "AND categorie = ? AND status = 'valide'"
                params.append(category)
            elif site_category:
                category_filter = "AND categorie = ? AND status = 'valide'"
                params.append(site_category)
            else:
                category_filter = "AND status = 'valide'"
            
            if direction == "up":
                # Trouver le site avec display_order immédiatement inférieur dans la même catégorie
                cur.execute(
                    f"""
                    SELECT id, display_order FROM sites 
                    WHERE display_order < ? {category_filter}
                    ORDER BY display_order DESC LIMIT 1
                    """,
                    (current_order,) + tuple(params)
                )
            else:  # down
                # Trouver le site avec display_order immédiatement supérieur dans la même catégorie
                cur.execute(
                    f"""
                    SELECT id, display_order FROM sites 
                    WHERE display_order > ? {category_filter}
                    ORDER BY display_order ASC LIMIT 1
                    """,
                    (current_order,) + tuple(params)
                )
            
            swap_site = cur.fetchone()
            if not swap_site:
                return False, "Impossible de déplacer (déjà en première/dernière position)."
            
            swap_order = swap_site["display_order"] or 0
            swap_id = swap_site["id"]
            
            # Échanger les display_order
            cur.execute(
                "UPDATE sites SET display_order = ?, date_ajout = DATETIME('now') WHERE id = ?",
                (swap_order, site_id)
            )
            cur.execute(
                "UPDATE sites SET display_order = ?, date_ajout = DATETIME('now') WHERE id = ?",
                (current_order, swap_id)
            )
            
            return True, f"Site déplacé vers le {'haut' if direction == 'up' else 'bas'}."
    
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors du déplacement du site {site_id}: {exc}")
        return False, "Erreur lors du déplacement du site."


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
    display_order: Optional[int] = None,
) -> Tuple[bool, str]:
    """Update all fields of a site. Returns (success, message)."""
    ensure_sites_table()
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            if display_order is not None:
                cur.execute(
                    """
                    UPDATE sites
                    SET nom = ?, ville = ?, lien = ?, description = ?, categorie = ?, status = ?, display_order = ?
                    WHERE id = ?
                    """,
                    (nom, ville, lien, description, categorie, status, display_order, site_id),
                )
            else:
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
    display_order: int = 0,
) -> Tuple[bool, str]:
    """Create a new site directly published (admin only). Returns (success, message)."""
    ensure_sites_table()
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout, en_vedette, display_order)
                VALUES (?, ?, ?, ?, ?, 'valide', DATETIME('now'), 0, ?)
                """,
                (nom, ville, lien, description, categorie, display_order),
            )
        return True, "Nouveau site ajouté et publié."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la création d'un site depuis l'admin: {exc}")
        return False, "Erreur lors de l'ajout du site."
