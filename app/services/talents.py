"""Talent-related database helpers."""

from __future__ import annotations

import sqlite3
from collections import OrderedDict, defaultdict
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from flask import current_app

from ..database import DatabaseError, db_query, db_transaction, get_db_connection, get_db_path

TALENT_CATEGORIES: List[str] = [
    "Comédiens",
    "Chanteurs",
    "Influenceurs",
    "Célébrités",
]

TALENT_STATUSES: List[str] = ["en_attente", "valide", "refuse"]

TALENT_STATUS_LABELS: Dict[str, str] = {
    "en_attente": "En attente",
    "valide": "Publié",
    "refuse": "Refusé",
}

DEFAULT_TALENTS: List[Dict[str, str]] = [
    {
        "pseudo": "harendra_h24",
        "instagram": "https://www.instagram.com/harendra_h24/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/harendra.jpg",
    },
    {
        "pseudo": "benj_off",
        "instagram": "https://www.instagram.com/benj_off/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/benji.jpg",
    },
    {
        "pseudo": "titilecomik",
        "instagram": "https://www.instagram.com/titilecomik/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/titilecomik.jpg",
    },
    {
        "pseudo": "monsieur__moustache",
        "instagram": "https://www.instagram.com/monsieur__moustache/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/monsieur__moustache.jpg",
    },
    {
        "pseudo": "lecouple_en_lu",
        "instagram": "https://www.instagram.com/lecouple_en_lu/reels/",
        "description": "Humoristes réunionnais en duo",
        "category": "Comédiens",
        "image": "talents/lecouple_en_lu.jpg",
    },
    {
        "pseudo": "adriana.ftn_",
        "instagram": "https://www.instagram.com/adriana.ftn_/",
        "description": "Humoriste réunionnaise",
        "category": "Comédiens",
        "image": "talents/adriana.ftn_.jpg",
    },
    {
        "pseudo": "segaelofficiel",
        "instagram": "https://www.instagram.com/segaelofficiel/",
        "description": "Chanteuse réunionnaise",
        "category": "Chanteurs",
        "image": "talents/segaelofficiel.jpg",
    },

    {
        "pseudo": "pll_off",
        "instagram": "https://www.instagram.com/pll_off/",
        "description": "Groupe de chanteurs réunionnais",
        "category": "Chanteurs",
        "image": "talents/pll_off.jpg",
    },

    {
        "pseudo": "kafmalbarofficiel",
        "instagram": "https://www.instagram.com/kafmalbarofficiel/",
        "description": "Chanteur réunionnais",
        "category": "Chanteurs",
        "image": "talents/kafmalbarofficiel.jpg",
    },
    {
        "pseudo": "jennie.leonie",
        "instagram": "https://www.instagram.com/jennie.leonie/",
        "description": "Influenceuse réunionnaise",
        "category": "Influenceurs",
        "image": "talents/jennie.leonie.jpg",
    },
    {
        "pseudo": "fanm.kreol",
        "instagram": "https://www.instagram.com/fanm.kreol/",
        "description": "Influenceuse réunionnaise",
        "category": "Influenceurs",
        "image": "talents/fanm.kreol.jpg",
    },
    {
        "pseudo": "dronecopters_974",
        "instagram": "https://www.instagram.com/dronecopters_974/",
        "description": "Influenceur réunionnais",
        "category": "Influenceurs",
        "image": "talents/dronecopters_974.jpg",
    },
    {
        "pseudo": "priyapadavatanoff",
        "instagram": "https://www.instagram.com/priyapadavatanoff/",
        "description": "Miss Réunion 2025",
        "category": "Célébrités",
        "image": "talents/priyapadavatanoff.jpg",
    },
    {
        "pseudo": "manupayet",
        "instagram": "https://www.instagram.com/manupayet/",
        "description": "Acteur réunionnais",
        "category": "Célébrités",
        "image": "talents/manupayet.jpg",
    },
]


def ensure_talents_table() -> None:
    """Create the talents table if needed."""
    conn = None
    try:
        conn = sqlite3.connect(get_db_path())
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS talents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                instagram TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT '',
                image TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'en_attente',
                display_order INTEGER DEFAULT 0,
                date_created TEXT NOT NULL DEFAULT (DATETIME('now')),
                date_updated TEXT NOT NULL DEFAULT (DATETIME('now'))
            )
            """
        )
        # Migration: ajouter display_order si la colonne n'existe pas
        try:
            conn.execute("ALTER TABLE talents ADD COLUMN display_order INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            # La colonne existe déjà, c'est normal
            pass
        
        conn.execute("CREATE INDEX IF NOT EXISTS idx_talents_status ON talents(status)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_talents_category ON talents(category)"
        )
        conn.commit()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la création de la table talents: {exc}"
        )
    finally:
        if conn:
            conn.close()


def seed_default_talents() -> None:
    """Seed the talents table with default entries when empty."""
    ensure_talents_table()
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM talents")
        row = cur.fetchone()
        total = row[0] if row else 0
        if total == 0:
            cur.executemany(
                """
                INSERT INTO talents (pseudo, instagram, description, category, image, status)
                VALUES (?, ?, ?, ?, ?, 'valide')
                """,
                [
                    (
                        talent["pseudo"],
                        talent["instagram"],
                        talent["description"],
                        talent["category"],
                        talent.get("image", ""),
                    )
                    for talent in DEFAULT_TALENTS
                ],
            )
            conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        current_app.logger.error(
            f"Erreur lors de l'initialisation des talents: {exc}"
        )
    finally:
        conn.close()


def prepare_talents_storage() -> None:
    """Ensure tables exist and defaults are loaded."""
    ensure_talents_table()
    seed_default_talents()


def create_talent_proposal(pseudo: str, instagram: str, description: str, category: str | None = None) -> bool:
    """Add a new talent proposal."""
    ensure_talents_table()
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # Valider la catégorie si fournie
        if category and category not in TALENT_CATEGORIES:
            category = None
        cur.execute(
            """
            INSERT INTO talents (pseudo, instagram, description, category, status)
            VALUES (?, ?, ?, ?, 'en_attente')
            """,
            (pseudo, instagram, description, category),
        )
        conn.commit()
        return True
    except sqlite3.Error as exc:
        conn.rollback()
        current_app.logger.error(
            f"Erreur lors de l'enregistrement d'un talent: {exc}"
        )
        return False
    finally:
        conn.close()


def get_talent_category_choices(current: str | None = None) -> List[Tuple[str, str]]:
    """Return select choices for talent categories."""
    choices: List[Tuple[str, str]] = [("", "Sélectionnez une catégorie")]
    for category in TALENT_CATEGORIES:
        choices.append((category, category))
    if current and current not in TALENT_CATEGORIES:
        choices.append((current, current))
    return choices


def get_talent_status_choices() -> List[Tuple[str, str]]:
    """Return localized status choices."""
    return [(code, TALENT_STATUS_LABELS.get(code, code)) for code in TALENT_STATUSES]


def get_talents_data() -> OrderedDict[str, List[Dict[str, str]]]:
    """Return validated talents grouped by category for public pages."""
    prepare_talents_storage()
    conn = get_db_connection()
    if not conn:
        return OrderedDict()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT pseudo, instagram, description, category, image
            FROM talents
            WHERE status = 'valide'
            ORDER BY category ASC, display_order ASC, pseudo ASC
            """
        )
        rows = cur.fetchall()
    except sqlite3.Error as exc:
        current_app.logger.error(
            f"Erreur lors de la récupération des talents: {exc}"
        )
        return OrderedDict()
    finally:
        conn.close()

    grouped: MutableMapping[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["category"] or ""].append(
            {
                "name": row["pseudo"],
                "instagram": row["instagram"],
                "tagline": row["description"],
                "image": row["image"] or "",
            }
        )

    ordered: OrderedDict[str, List[Dict[str, str]]] = OrderedDict()
    for category in TALENT_CATEGORIES:
        if grouped.get(category):
            ordered[category] = grouped.pop(category)

    for category in sorted(grouped.keys()):
        ordered[category] = grouped[category]

    return ordered


def get_admin_talents(
    status_filter: str = "en_attente", 
    search_query: str = "",
    sort_by: str = "date_updated",
    sort_order: str = "desc",
    category_filter: Optional[str] = None
) -> Dict[str, any]:
    """Get talents for admin dashboard with filters and sorting. Returns dict with entries and stats."""
    prepare_talents_storage()
    allowed_statuses = set(TALENT_STATUSES + ["tout"])
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"
    
    # Colonnes triables valides
    allowed_sort_columns = {
        "pseudo": "pseudo",
        "category": "category",
        "status": "status",
        "date_created": "date_created",
        "date_updated": "date_updated",
        "display_order": "display_order"
    }
    
    sort_column = allowed_sort_columns.get(sort_by, "date_updated")
    sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
    
    try:
        with db_query() as conn:
            cur = conn.cursor()
            params: List[str] = []
            query = """
                SELECT id, pseudo, instagram, description, category, image, status, display_order, date_created, date_updated
                FROM talents
                WHERE 1 = 1
            """
            
            if status_filter != "tout":
                query += " AND status = ?"
                params.append(status_filter)
            
            if category_filter:
                query += " AND category = ?"
                params.append(category_filter)
            
            if search_query and len(search_query) >= 2:
                like_query = f"%{search_query}%"
                query += """
                    AND (
                        pseudo LIKE ? COLLATE NOCASE
                        OR instagram LIKE ? COLLATE NOCASE
                        OR description LIKE ? COLLATE NOCASE
                        OR IFNULL(category, '') LIKE ? COLLATE NOCASE
                    )
                """
                params.extend([like_query] * 4)
            
            query += f"""
                ORDER BY
                    CASE status
                        WHEN 'en_attente' THEN 0
                        WHEN 'valide' THEN 1
                        ELSE 2
                    END,
                    {sort_column} {sort_direction},
                    id DESC
                LIMIT 200
            """
            
            cur.execute(query, tuple(params))
            entries = cur.fetchall()
            
            # Stats par statut
            stats_query = "SELECT status, COUNT(*) AS total FROM talents WHERE 1 = 1"
            stats_params = []
            if category_filter:
                stats_query += " AND category = ?"
                stats_params.append(category_filter)
            stats_query += " GROUP BY status"
            
            cur.execute(stats_query, tuple(stats_params))
            stats_rows = cur.fetchall()
            
            stats = {row["status"]: row["total"] for row in stats_rows}
            stats["tout"] = sum(stats.values())
            
            # Stats par catégorie pour les talents publiés
            cur.execute(
                "SELECT category, COUNT(*) AS total FROM talents WHERE status = 'valide' GROUP BY category"
            )
            category_stats_rows = cur.fetchall()
            category_stats = {row["category"] or "": row["total"] for row in category_stats_rows}
            
            return {"entries": entries, "stats": stats, "category_stats": category_stats}
    except DatabaseError:
        return {"entries": [], "stats": {"en_attente": 0, "valide": 0, "refuse": 0, "tout": 0}}


def get_talent_by_id(talent_id: int) -> Optional[sqlite3.Row]:
    """Get a talent by its ID."""
    prepare_talents_storage()
    try:
        with db_query() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, pseudo, instagram, description, category, image, status, display_order
                FROM talents
                WHERE id = ?
                """,
                (talent_id,),
            )
            return cur.fetchone()
    except DatabaseError:
        return None


def update_talent_status(talent_id: int, status: str) -> Tuple[bool, str]:
    """Update talent status. Returns (success, message)."""
    valid_statuses = {"valide", "refuse"}
    if status not in valid_statuses:
        return False, "Statut invalide."
    
    prepare_talents_storage()
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            if status == "valide":
                cur.execute(
                    "UPDATE talents SET status = 'valide', date_updated = DATETIME('now') WHERE id = ?",
                    (talent_id,),
                )
                message = "Talent publié."
            else:
                cur.execute(
                    "UPDATE talents SET status = 'refuse', date_updated = DATETIME('now') WHERE id = ?",
                    (talent_id,),
                )
                message = "Talent refusé."
            
            if cur.rowcount == 0:
                return False, "Talent introuvable."
            
            return True, message
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la mise à jour du talent {talent_id}: {exc}")
        return False, "Erreur lors de la mise à jour du talent."


def delete_talent(talent_id: int) -> Tuple[bool, str]:
    """Delete a talent. Returns (success, message)."""
    prepare_talents_storage()
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM talents WHERE id = ?", (talent_id,))
            if cur.rowcount == 0:
                return False, "Talent introuvable."
            return True, "Talent supprimé."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la suppression du talent {talent_id}: {exc}")
        return False, "Erreur lors de la suppression."


def update_talent_full(
    talent_id: int,
    pseudo: str,
    instagram: str,
    description: str,
    category: str,
    image: str,
    status: str,
    display_order: int = 0,
) -> Tuple[bool, str]:
    """Update all fields of a talent. Returns (success, message)."""
    prepare_talents_storage()
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE talents
                SET pseudo = ?, instagram = ?, description = ?, category = ?, image = ?, status = ?, display_order = ?, date_updated = DATETIME('now')
                WHERE id = ?
                """,
                (pseudo, instagram, description, category or "", image or "", status, display_order or 0, talent_id),
            )
            if cur.rowcount == 0:
                return False, "Aucune mise à jour n'a été effectuée."
            return True, "Talent mis à jour."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de la mise à jour du talent {talent_id}: {exc}")
        return False, "Erreur lors de la mise à jour du talent."


def create_talent_admin(
    pseudo: str,
    instagram: str,
    description: str,
    category: str,
    image: str,
    status: str,
    display_order: int = 0,
) -> Tuple[bool, str]:
    """Create a new talent (admin only). Returns (success, message)."""
    prepare_talents_storage()
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO talents (pseudo, instagram, description, category, image, status, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (pseudo, instagram, description, category or "", image or "", status, display_order or 0),
            )
        return True, "Talent ajouté."
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors de l'ajout d'un talent depuis l'admin: {exc}")
        return False, "Erreur lors de l'ajout du talent."


def move_talent_order(talent_id: int, direction: str, category: Optional[str] = None) -> Tuple[bool, str]:
    """Move a talent up or down in display order. Returns (success, message)."""
    prepare_talents_storage()
    if direction not in ["up", "down"]:
        return False, "Direction invalide."
    
    try:
        with db_transaction() as conn:
            cur = conn.cursor()
            # Récupérer le talent actuel
            cur.execute(
                "SELECT id, display_order, category FROM talents WHERE id = ?",
                (talent_id,)
            )
            talent = cur.fetchone()
            if not talent:
                return False, "Talent introuvable."
            
            current_order = talent["display_order"] or 0
            talent_category = talent["category"] or ""
            
            # Filtrer par catégorie et statut valide pour l'ordre d'affichage public
            category_filter = ""
            params = []
            if category:
                category_filter = "AND category = ? AND status = 'valide'"
                params.append(category)
            elif talent_category:
                category_filter = "AND category = ? AND status = 'valide'"
                params.append(talent_category)
            else:
                category_filter = "AND status = 'valide'"
            
            if direction == "up":
                # Trouver le talent avec display_order immédiatement inférieur dans la même catégorie
                cur.execute(
                    f"""
                    SELECT id, display_order FROM talents 
                    WHERE display_order < ? {category_filter}
                    ORDER BY display_order DESC LIMIT 1
                    """,
                    (current_order,) + tuple(params)
                )
            else:  # down
                # Trouver le talent avec display_order immédiatement supérieur dans la même catégorie
                cur.execute(
                    f"""
                    SELECT id, display_order FROM talents 
                    WHERE display_order > ? {category_filter}
                    ORDER BY display_order ASC LIMIT 1
                    """,
                    (current_order,) + tuple(params)
                )
            
            swap_talent = cur.fetchone()
            if not swap_talent:
                return False, "Impossible de déplacer (déjà en première/dernière position)."
            
            swap_order = swap_talent["display_order"] or 0
            swap_id = swap_talent["id"]
            
            # Échanger les display_order
            cur.execute(
                "UPDATE talents SET display_order = ?, date_updated = DATETIME('now') WHERE id = ?",
                (swap_order, talent_id)
            )
            cur.execute(
                "UPDATE talents SET display_order = ?, date_updated = DATETIME('now') WHERE id = ?",
                (current_order, swap_id)
            )
            
            return True, f"Talent déplacé vers le {'haut' if direction == 'up' else 'bas'}."
    
    except DatabaseError as exc:
        current_app.logger.error(f"Erreur lors du déplacement du talent {talent_id}: {exc}")
        return False, "Erreur lors du déplacement du talent."
