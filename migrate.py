import os
import re
import shutil
import sqlite3
from datetime import datetime
from flask import Flask
from config import config

# Charge la config Flask
app = Flask(__name__)
env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config.get(env, config["default"]))
DATABASE_PATH = app.config["DATABASE_PATH"]


def slugify(text: str) -> str:
    s = (text or "").strip().lower()
    replacements = {
        "à": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = s.replace("'", "").replace("’", "").replace(".", "").replace(",", "")
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def table_exists(cur, table_name: str) -> bool:
    cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def column_exists(cur, table_name: str, column_name: str) -> bool:
    cur.execute(f"PRAGMA table_info({table_name})")
    return any(row[1] == column_name for row in cur.fetchall())


def ensure_column(cur, table_name: str, column_name: str, definition: str) -> None:
    if not column_exists(cur, table_name, column_name):
        print(f"➕ Ajout colonne {table_name}.{column_name}")
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def main():
    print("📂 DB cible:", DATABASE_PATH)

    # Backup auto
    os.makedirs("backups", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join("backups", f"base_backup_{ts}.db")
    shutil.copy2(DATABASE_PATH, backup_path)
    print("💾 Backup créé:", backup_path)

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    try:
        cur.execute("PRAGMA foreign_keys = ON")

        # Table sites (si absente)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                ville TEXT,
                lien TEXT NOT NULL,
                description TEXT,
                categorie TEXT,
                status TEXT DEFAULT 'en_attente',
                date_ajout DATETIME,
                en_vedette INTEGER DEFAULT 0,
                click_count INTEGER DEFAULT 0
            )
            """
        )

        # Colonnes manquantes possibles sur sites
        ensure_column(cur, "sites", "ville", "TEXT")
        ensure_column(cur, "sites", "status", "TEXT DEFAULT 'en_attente'")
        ensure_column(cur, "sites", "date_ajout", "DATETIME")
        ensure_column(cur, "sites", "en_vedette", "INTEGER DEFAULT 0")
        ensure_column(cur, "sites", "click_count", "INTEGER DEFAULT 0")

        # Table site_clicks
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS site_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Table categories
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Table villes
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS villes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE
            )
            """
        )

        # Colonne FK ville_id sur sites
        ensure_column(cur, "sites", "ville_id", "INTEGER REFERENCES villes(id)")

        # Backfill villes depuis sites.ville
        cur.execute(
            """
            SELECT DISTINCT TRIM(ville)
            FROM sites
            WHERE ville IS NOT NULL AND TRIM(ville) != ''
            """
        )
        city_names = [row[0] for row in cur.fetchall() if row[0]]

        for nom_ville in city_names:
            slug = slugify(nom_ville)
            cur.execute(
                "INSERT OR IGNORE INTO villes (nom, slug) VALUES (?, ?)",
                (nom_ville, slug),
            )

        # Backfill sites.ville_id (sans écraser si déjà rempli)
        cur.execute(
            """
            SELECT id, ville
            FROM sites
            WHERE (ville_id IS NULL OR ville_id = '')
              AND ville IS NOT NULL
              AND TRIM(ville) != ''
            """
        )
        rows = cur.fetchall()

        for site_id, ville in rows:
            slug = slugify(ville)
            cur.execute("SELECT id FROM villes WHERE slug = ?", (slug,))
            v = cur.fetchone()
            if v:
                cur.execute(
                    "UPDATE sites SET ville_id = ? WHERE id = ?",
                    (v[0], site_id),
                )

        # Index utiles
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_categorie ON sites(categorie)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_click_count ON sites(click_count)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_ville_id ON sites(ville_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_site_clicks_site_id ON site_clicks(site_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_site_clicks_clicked_at ON site_clicks(clicked_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_villes_slug ON villes(slug)")

        conn.commit()
        print("✅ Migration terminée avec succès")

    except Exception as e:
        conn.rollback()
        print("❌ Erreur migration:", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
