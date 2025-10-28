"""Site-related queries and helpers."""

from __future__ import annotations

import sqlite3
from typing import Dict, List, Sequence

from flask import current_app, g, has_request_context

from ..database import get_db_connection
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
