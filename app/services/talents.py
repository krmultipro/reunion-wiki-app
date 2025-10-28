"""Talent-related database helpers."""

from __future__ import annotations

import sqlite3
from collections import OrderedDict, defaultdict
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

from flask import current_app

from ..database import get_db_connection, get_db_path

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
        "pseudo": "kafmalbarofficiel",
        "instagram": "https://www.instagram.com/kafmalbarofficiel/",
        "description": "Chanteur réunionnais",
        "category": "Chanteurs",
        "image": "talents/kafmalbarofficiel.jpg",
    },
    {
        "pseudo": "pll_off",
        "instagram": "https://www.instagram.com/pll_off/",
        "description": "Groupe de chanteurs réunionnais",
        "category": "Chanteurs",
        "image": "talents/pll_off.jpg",
    },
    {
        "pseudo": "segaelofficiel",
        "instagram": "https://www.instagram.com/segaelofficiel/",
        "description": "Chanteuse réunionnaise",
        "category": "Chanteurs",
        "image": "talents/segaelofficiel.jpg",
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
                date_created TEXT NOT NULL DEFAULT (DATETIME('now')),
                date_updated TEXT NOT NULL DEFAULT (DATETIME('now'))
            )
            """
        )
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


def create_talent_proposal(pseudo: str, instagram: str, description: str) -> bool:
    """Add a new talent proposal."""
    ensure_talents_table()
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO talents (pseudo, instagram, description, status)
            VALUES (?, ?, ?, 'en_attente')
            """,
            (pseudo, instagram, description),
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
            ORDER BY category ASC, pseudo ASC
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
