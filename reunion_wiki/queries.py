# -*- coding: utf-8 -*-

import sqlite3

from flask import current_app

from .repositories import category_repository, site_repository


def get_sites_en_vedette():
    """Récupère les catégories triées par clics + sites vedette (sinon top clics)."""
    try:
        cat_rows = category_repository.get_category_stats()

        data = {row["categorie"]: [] for row in cat_rows}
        category_stats = {
            row["categorie"]: {
                "site_count": row["site_count"],
                "total_clicks": row["total_clicks"],
            }
            for row in cat_rows
        }

        featured_by_category = {cat: [] for cat in data}
        for site in site_repository.get_featured_valid_sites():
            cat = site["categorie"]
            if cat in featured_by_category:
                featured_by_category[cat].append(site)

        top_by_category = {cat: [] for cat in data}
        for site in site_repository.get_all_valid_sites_by_category_order():
            cat = site["categorie"]
            if cat in top_by_category:
                top_by_category[cat].append(site)

        for cat in data:
            featured_sites = sorted(
                featured_by_category[cat],
                key=lambda s: ((s["click_count"] or 0), (s["date_ajout"] or "")),
                reverse=True,
            )
            if featured_sites:
                data[cat] = featured_sites[:3]
                continue

            data[cat] = sorted(
                top_by_category[cat],
                key=lambda s: ((s["click_count"] or 0), (s["date_ajout"] or "")),
                reverse=True,
            )[:3]

        return data, category_stats
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des sites en vedette: {e}")
        return {}, {}


def get_derniers_sites_global(limit=3):
    """Récupère les derniers sites ajoutés."""
    try:
        return site_repository.get_latest_sites(limit)
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des derniers sites: {e}")
        return []


def get_top_sites(limit=5):
    try:
        return site_repository.get_top_sites(limit)
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur top sites: {e}")
        return []
