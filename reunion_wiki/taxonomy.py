# -*- coding: utf-8 -*-

import sqlite3

from flask import current_app, g, has_request_context

from .db import get_db_connection
from .utils import slugify, slugify_ville


def get_categories():
    """Récupère les catégories depuis la table dédiée si disponible."""
    if has_request_context() and hasattr(g, "_categories_cache"):
        return g._categories_cache

    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
        has_table = cur.fetchone() is not None

        if has_table:
            cur.execute("SELECT nom FROM categories ORDER BY nom COLLATE NOCASE ASC")
            results = cur.fetchall()
            categories = [row[0] for row in results if row[0]]
        else:
            categories = []

        if not categories and has_table:
            cur.execute(
                """
                SELECT DISTINCT c.nom
                FROM sites s
                JOIN categories c ON c.id = s.category_id
                WHERE s.status = 'valide'
                  AND c.nom IS NOT NULL
                  AND TRIM(c.nom) != ''
                ORDER BY c.nom COLLATE NOCASE ASC
                """
            )
            results = cur.fetchall()
            categories = [row[0] for row in results if row[0]]

        categories = sorted(set(categories), key=lambda x: x.lower())
        if has_request_context():
            g._categories_cache = categories
        return categories
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des catégories: {e}")
        return []
    finally:
        conn.close()


def get_city_choices():
    """Retourne les choix de villes pour les formulaires publics."""
    if has_request_context() and hasattr(g, "_city_choices_cache"):
        return g._city_choices_cache

    choices = [("", "Non précisée")]
    conn = get_db_connection()
    if not conn:
        return choices

    try:
        cur = conn.cursor()
        cur.execute("SELECT nom FROM villes ORDER BY nom COLLATE NOCASE ASC")
        for row in cur.fetchall():
            nom = row["nom"]
            if nom:
                choices.append((nom, nom))
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors du chargement des villes: {e}")
    finally:
        conn.close()

    if has_request_context():
        g._city_choices_cache = choices
    return choices


def get_categories_slug():
    if has_request_context() and hasattr(g, "_categories_slug_cache"):
        return g._categories_slug_cache

    categories = get_categories()
    conn = get_db_connection()
    categories_slug = {}

    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
            has_table = cur.fetchone() is not None
            if has_table:
                cur.execute("SELECT nom, slug FROM categories")
                rows = cur.fetchall()
                categories_slug = {row["nom"]: row["slug"] for row in rows}
        except sqlite3.Error as e:
            current_app.logger.error(f"Erreur lors de la récupération des slugs de catégories: {e}")
        finally:
            conn.close()

    if not categories_slug:
        categories_slug = {cat: slugify(cat) for cat in categories}

    if has_request_context():
        g._categories_slug_cache = categories_slug
    return categories_slug


def get_nom_categorie_depuis_slug(slug):
    categories_slug = get_categories_slug()
    for cat, cat_slug in categories_slug.items():
        if cat_slug == slug:
            return cat
    return None


def generate_unique_category_slug(cursor, nom, exclude_id=None):
    """Génère un slug unique pour la table categories."""
    base_slug = slugify(nom) or "categorie"
    candidate = base_slug
    suffix = 1
    while True:
        if exclude_id:
            cursor.execute("SELECT id FROM categories WHERE slug = ? AND id != ?", (candidate, exclude_id))
        else:
            cursor.execute("SELECT id FROM categories WHERE slug = ?", (candidate,))
        row = cursor.fetchone()
        if not row:
            return candidate
        candidate = f"{base_slug}-{suffix}"
        suffix += 1


def resolve_category(cursor, category_name):
    """Retourne (id, nom) pour une catégorie, en la créant si nécessaire."""
    normalized = (category_name or "").strip()
    if not normalized:
        return None

    cursor.execute("SELECT id, nom FROM categories WHERE nom = ?", (normalized,))
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    cursor.execute(
        "SELECT id, nom FROM categories WHERE LOWER(TRIM(nom)) = LOWER(?) ORDER BY id ASC LIMIT 1",
        (normalized,),
    )
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    slug = generate_unique_category_slug(cursor, normalized)
    cursor.execute("INSERT INTO categories (nom, slug) VALUES (?, ?)", (normalized, slug))
    return cursor.lastrowid, normalized


def resolve_city(cursor, city_name):
    """Retourne (id, nom) pour une ville existante."""
    normalized = (city_name or "").strip()
    if not normalized:
        return None

    cursor.execute("SELECT id, nom FROM villes WHERE nom = ?", (normalized,))
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    cursor.execute(
        "SELECT id, nom FROM villes WHERE LOWER(TRIM(nom)) = LOWER(?) ORDER BY id ASC LIMIT 1",
        (normalized,),
    )
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    city_slug = slugify_ville(normalized)
    if city_slug:
        cursor.execute("SELECT id, nom FROM villes WHERE slug = ? ORDER BY id ASC LIMIT 1", (city_slug,))
        row = cursor.fetchone()
        if row:
            return row["id"], row["nom"]

    return None
