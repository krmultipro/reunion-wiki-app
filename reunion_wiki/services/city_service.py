# -*- coding: utf-8 -*-
"""Services applicatifs des villes."""

import sqlite3

from flask import current_app, g, has_request_context

from ..repositories import city_repository
from ..utils import slugify_ville


def get_name_choices():
    """Retourne les choix WTForms dont la valeur est le nom de la ville."""
    if has_request_context() and hasattr(g, "_city_name_choices_cache"):
        return g._city_name_choices_cache

    choices = [("", "Non précisée")]
    try:
        choices.extend(
            (city["nom"], city["nom"])
            for city in city_repository.get_all_cities()
            if city["nom"]
        )
    except sqlite3.Error as error:
        current_app.logger.error(f"Erreur lors du chargement des villes: {error}")

    if has_request_context():
        g._city_name_choices_cache = choices
    return choices


def get_id_choices():
    """Retourne les choix WTForms dont la valeur est l'identifiant de la ville."""
    if has_request_context() and hasattr(g, "_city_id_choices_cache"):
        return g._city_id_choices_cache

    choices = [("", "Non précisée")]
    try:
        choices.extend(
            (city["id"], city["nom"])
            for city in city_repository.get_all_cities()
            if city["nom"]
        )
    except sqlite3.Error as error:
        current_app.logger.error(f"Erreur lors du chargement des villes: {error}")

    if has_request_context():
        g._city_id_choices_cache = choices
    return choices


def resolve_city(name):
    """Résout un nom ou slug de ville vers son identifiant et son nom canonique.

    Returns:
        tuple[int, str] | None:
            Identifiant et nom canonique de la ville résolue.
    """
    normalized = (name or "").strip()
    if not normalized:
        return None

    city = city_repository.get_city_by_name(normalized)
    if not city:
        city = city_repository.get_city_by_normalized_name(normalized)
    if not city:
        city_slug = slugify_ville(normalized)
        if city_slug:
            city = city_repository.get_city_by_slug(city_slug)

    if not city:
        return None
    return city["id"], city["nom"]
