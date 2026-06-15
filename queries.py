# -*- coding: utf-8 -*-

import sqlite3

from flask import current_app

from db import get_db_connection


def get_sites_en_vedette():
    """Récupère les catégories triées par clics + sites vedette (sinon top clics)."""
    conn = get_db_connection()
    if not conn:
        return {}, {}

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                c.nom AS categorie,
                COUNT(*) AS site_count,
                COALESCE(SUM(s.click_count), 0) AS total_clicks
            FROM sites s
            JOIN categories c ON c.id = s.category_id
            WHERE s.status = 'valide'
            GROUP BY c.id, c.nom
            ORDER BY total_clicks DESC, site_count DESC, c.nom COLLATE NOCASE ASC
            """
        )
        cat_rows = cur.fetchall()

        data = {row["categorie"]: [] for row in cat_rows}
        category_stats = {
            row["categorie"]: {
                "site_count": row["site_count"],
                "total_clicks": row["total_clicks"],
            }
            for row in cat_rows
        }

        cur.execute(
            """
            SELECT
                s.*,
                c.nom AS categorie,
                v.nom AS ville,
                v.nom AS ville_nom,
                v.slug AS ville_slug
            FROM sites s
            JOIN categories c ON c.id = s.category_id
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE s.status = 'valide' AND s.en_vedette = 1
            ORDER BY c.nom ASC, s.click_count DESC, s.date_ajout DESC
            """
        )
        featured_by_category = {cat: [] for cat in data}
        for site in cur.fetchall():
            cat = site["categorie"]
            if cat in featured_by_category:
                featured_by_category[cat].append(site)

        cur.execute(
            """
            SELECT
                s.*,
                c.nom AS categorie,
                v.nom AS ville,
                v.nom AS ville_nom,
                v.slug AS ville_slug
            FROM sites s
            JOIN categories c ON c.id = s.category_id
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE s.status = 'valide'
            ORDER BY c.nom ASC, s.click_count DESC, s.date_ajout DESC
            """
        )
        top_by_category = {cat: [] for cat in data}
        for site in cur.fetchall():
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
    finally:
        conn.close()


def get_derniers_sites_global(limit=3):
    """Récupère les derniers sites ajoutés."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                s.id,
                s.nom,
                s.lien,
                c.nom AS categorie,
                s.description,
                s.date_ajout
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
            WHERE s.status = 'valide'
            ORDER BY s.date_ajout DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur lors de la récupération des derniers sites: {e}")
        return []
    finally:
        conn.close()


def get_top_sites(limit=5):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                s.id,
                s.nom,
                s.lien,
                c.nom AS categorie,
                s.description,
                s.click_count
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
            WHERE s.status = 'valide'
            ORDER BY s.click_count DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
    except sqlite3.Error as e:
        current_app.logger.error(f"Erreur top sites: {e}")
        return []
    finally:
        conn.close()
