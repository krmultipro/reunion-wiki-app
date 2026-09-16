# -*- coding: utf-8 -*-
"""Services applicatifs des catégories de sites."""

import sqlite3

from flask import current_app, g, has_request_context

from ..repositories import category_repository
from ..utils import slugify


def get_category_names():
    """Retourne les noms de catégories triés, avec un cache par requête."""
    if has_request_context() and hasattr(g, "_category_names_cache"):
        return g._category_names_cache

    try:
        category_names = [
            row["nom"]
            for row in category_repository.get_all_categories()
            if row["nom"]
        ]
        category_names = sorted(set(category_names), key=str.lower)
    except sqlite3.Error as error:
        current_app.logger.error(
            f"Erreur lors de la récupération des catégories: {error}"
        )
        category_names = []

    if has_request_context():
        g._category_names_cache = category_names
    return category_names


def get_category_slug_map():
    """Retourne la correspondance ``nom -> slug`` des catégories."""
    if has_request_context() and hasattr(g, "_category_slug_map_cache"):
        return g._category_slug_map_cache

    category_names = get_category_names()
    try:
        slug_map = {
            row["nom"]: row["slug"]
            for row in category_repository.get_all_categories()
            if row["nom"] and row["slug"]
        }
    except sqlite3.Error as error:
        current_app.logger.error(
            f"Erreur lors de la récupération des slugs de catégories: {error}"
        )
        slug_map = {}

    if not slug_map:
        slug_map = {name: slugify(name) for name in category_names}

    if has_request_context():
        g._category_slug_map_cache = slug_map
    return slug_map


def get_category_name_by_slug(slug):
    """Retourne le nom associé à un slug de catégorie, ou ``None``."""
    category = category_repository.get_category_by_slug(slug)
    return category["nom"] if category else None


def generate_unique_slug(name, exclude_id=None):
    """Génère un slug de catégorie unique."""
    base_slug = slugify(name) or "categorie"
    candidate = base_slug
    suffix = 1

    while True:
        if exclude_id:
            existing = category_repository.get_category_by_slug_excluding_id(
                candidate,
                exclude_id,
            )
        else:
            existing = category_repository.get_category_by_slug(candidate)

        if not existing:
            return candidate

        candidate = f"{base_slug}-{suffix}"
        suffix += 1


def resolve_category(name, create_missing=True):
    """Résout un nom de catégorie et peut créer la catégorie si elle manque.

    Returns:
        tuple[int, str] | None:
            Identifiant et nom canonique de la catégorie résolue.
    """
    normalized = (name or "").strip()
    if not normalized:
        return None

    category = category_repository.get_category_by_name(normalized)
    if not category:
        category = category_repository.get_category_by_normalized_name(normalized)
    if category:
        return category["id"], category["nom"]

    if not create_missing:
        return None

    slug = generate_unique_slug(normalized)
    category_repository.create_category(normalized, slug)
    category = category_repository.get_category_by_name(normalized)
    if not category:
        return None
    return category["id"], category["nom"]
