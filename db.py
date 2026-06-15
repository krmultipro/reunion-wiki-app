# -*- coding: utf-8 -*-

import sqlite3

from flask import current_app


def get_db_connection():
    """Retourne une connexion sécurisée à la base de données."""
    try:
        conn = sqlite3.connect(current_app.config["DATABASE_PATH"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        init_db_schema(conn)
        return conn
    except Exception as e:
        print("ERREUR COMPLETE :", e)
        raise


def init_db_schema(conn):
    """Initialise et migre le schéma de la base si nécessaire."""
    from taxonomy import resolve_category, resolve_city

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            lien TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            status TEXT DEFAULT 'en_attente',
            date_ajout DATETIME,
            en_vedette INTEGER DEFAULT 0,
            click_count INTEGER DEFAULT 0
        )
    """)

    cur.execute("PRAGMA table_info(sites)")
    columns = [col[1] for col in cur.fetchall()]

    if "click_count" not in columns:
        cur.execute("ALTER TABLE sites ADD COLUMN click_count INTEGER DEFAULT 0")
    if "en_vedette" not in columns:
        cur.execute("ALTER TABLE sites ADD COLUMN en_vedette INTEGER DEFAULT 0")
    if "ville_id" not in columns:
        cur.execute("ALTER TABLE sites ADD COLUMN ville_id INTEGER")
    if "category_id" not in columns:
        cur.execute("ALTER TABLE sites ADD COLUMN category_id INTEGER")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS site_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT,
            clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS villes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    if "categorie" in columns:
        cur.execute(
            """
            SELECT id, categorie
            FROM sites
            WHERE (category_id IS NULL OR category_id = '')
              AND categorie IS NOT NULL
              AND TRIM(categorie) != ''
            """
        )
        for row in cur.fetchall():
            resolved = resolve_category(cur, row["categorie"])
            if not resolved:
                continue
            resolved_id, _resolved_name = resolved
            cur.execute("UPDATE sites SET category_id = ? WHERE id = ?", (resolved_id, row["id"]))

    if "ville" in columns:
        cur.execute(
            """
            SELECT id, ville
            FROM sites
            WHERE (ville_id IS NULL OR ville_id = '')
              AND ville IS NOT NULL
              AND TRIM(ville) != ''
            """
        )
        for row in cur.fetchall():
            resolved = resolve_city(cur, row["ville"])
            if not resolved:
                continue
            resolved_id, _resolved_name = resolved
            cur.execute("UPDATE sites SET ville_id = ? WHERE id = ?", (resolved_id, row["id"]))

    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)")
    cur.execute("DROP INDEX IF EXISTS idx_sites_categorie")
    cur.execute("DROP INDEX IF EXISTS idx_sites_ville")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_category_id ON sites(category_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_click_count ON sites(click_count)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_ville_id ON sites(ville_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_site_clicks_site_id ON site_clicks(site_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_site_clicks_clicked_at ON site_clicks(clicked_at)")

    conn.commit()
