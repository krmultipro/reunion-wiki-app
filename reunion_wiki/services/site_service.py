# -*- coding: utf-8 -*-
"""Services de lecture et de présentation des sites publics."""

import sqlite3

from flask import current_app

from ..repositories import category_repository, site_repository


def get_featured_sites_by_category():
    """Construit les sélections de sites affichées pour chaque catégorie.

    Les sites explicitement mis en vedette sont prioritaires. Lorsqu'une
    catégorie n'en possède aucun, ses sites les plus visités sont utilisés.

    Returns:
        tuple[dict, dict]:
            Sites sélectionnés par catégorie et statistiques des catégories.
    """
    try:
        category_rows = category_repository.get_category_stats()

        sites_by_category = {row["categorie"]: [] for row in category_rows}
        category_stats = {
            row["categorie"]: {
                "site_count": row["site_count"],
                "total_clicks": row["total_clicks"],
            }
            for row in category_rows
        }

        featured_by_category = {category: [] for category in sites_by_category}
        for site in site_repository.get_featured_valid_sites():
            category = site["categorie"]
            if category in featured_by_category:
                featured_by_category[category].append(site)

        top_by_category = {category: [] for category in sites_by_category}
        for site in site_repository.get_all_valid_sites_by_category_order():
            category = site["categorie"]
            if category in top_by_category:
                top_by_category[category].append(site)

        for category in sites_by_category:
            featured_sites = sorted(
                featured_by_category[category],
                key=lambda site: (
                    (site["click_count"] or 0),
                    (site["date_ajout"] or ""),
                ),
                reverse=True,
            )
            if featured_sites:
                sites_by_category[category] = featured_sites[:3]
                continue

            sites_by_category[category] = sorted(
                top_by_category[category],
                key=lambda site: (
                    (site["click_count"] or 0),
                    (site["date_ajout"] or ""),
                ),
                reverse=True,
            )[:3]

        return sites_by_category, category_stats
    except sqlite3.Error as error:
        current_app.logger.error(
            f"Erreur lors de la récupération des sites en vedette: {error}"
        )
        return {}, {}


def get_latest_sites(limit=None):
    """Retourne les derniers sites publiés, avec une limite optionnelle."""
    try:
        return site_repository.get_latest_sites(limit)
    except sqlite3.Error as error:
        current_app.logger.error(
            f"Erreur lors de la récupération des derniers sites: {error}"
        )
        return []


def get_top_sites(limit=None):
    """Retourne les sites publiés les plus visités."""
    try:
        return site_repository.get_top_sites(limit)
    except sqlite3.Error as error:
        current_app.logger.error(f"Erreur lors de la récupération des meilleurs sites: {error}")
        return []


def get_homepage_data(latest_limit=3, top_limit=5):
    """Rassemble les données de sites nécessaires à la page d'accueil."""
    sites_by_category, category_stats = get_featured_sites_by_category()

    return {
        "sites_by_category": sites_by_category,
        "category_stats": category_stats,
        "latest_sites": get_latest_sites(latest_limit),
        "top_sites": get_top_sites(top_limit),
    }
