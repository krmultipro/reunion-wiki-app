# -*- coding: utf-8 -*-
"""Accès aux données des villes."""

from ..db import get_db_connection


def _fetchone(query, params=()):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        connection.close()


def _fetchall(query, params=()):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        connection.close()


def get_all_cities():
    """Retourne toutes les villes triées par nom."""

    return _fetchall(
        """
        SELECT id, nom, slug
        FROM villes
        ORDER BY nom COLLATE NOCASE ASC
        """
    )


def get_city_by_id(city_id):
    """Récupère une ville à partir de son identifiant."""

    return _fetchone(
        "SELECT id, nom, slug FROM villes WHERE id = ?",
        (city_id,),
    )


def get_city_by_name(nom):
    """Récupère une ville à partir de son nom exact."""

    return _fetchone(
        "SELECT id, nom, slug FROM villes WHERE nom = ?",
        (nom,),
    )


def get_city_by_normalized_name(nom):
    """Recherche une ville sans tenir compte de la casse ni des espaces extérieurs."""

    return _fetchone(
        """
        SELECT id, nom, slug
        FROM villes
        WHERE LOWER(TRIM(nom)) = LOWER(?)
        ORDER BY id ASC
        LIMIT 1
        """,
        ((nom or "").strip(),),
    )


def get_city_by_slug(slug):
    """Récupère une ville à partir de son slug."""

    return _fetchone(
        "SELECT id, nom, slug FROM villes WHERE slug = ?",
        (slug,),
    )


def get_city_stats():
    """Retourne les villes avec leur nombre de sites publiés et leurs clics."""

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


def get_total_clicks_by_city_id(city_id):
    """Retourne le total des clics des sites publiés d'une ville."""

    return _fetchone(
        """
        SELECT COALESCE(SUM(click_count), 0) AS total_clicks
        FROM sites
        WHERE status = 'valide' AND ville_id = ?
        """,
        (city_id,),
    )
