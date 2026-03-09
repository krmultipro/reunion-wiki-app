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

CANONICAL_VILLES = [
    (1, "Les Avirons", "les-avirons"),
    (2, "Bras-Panon", "bras-panon"),
    (3, "Cilaos", "cilaos"),
    (4, "Entre-Deux", "entre-deux"),
    (5, "L'Etang-Sale", "letang-sale"),
    (6, "Petite-Ile", "petite-ile"),
    (7, "La Plaine-des-Palmistes", "la-plaine-des-palmistes"),
    (8, "Le Port", "le-port"),
    (9, "La Possession", "la-possession"),
    (10, "Saint-Andre", "saint-andre"),
    (11, "Saint-Benoit", "saint-benoit"),
    (12, "Saint-Denis", "saint-denis"),
    (13, "Saint-Joseph", "saint-joseph"),
    (14, "Saint-Leu", "saint-leu"),
    (15, "Saint-Louis", "saint-louis"),
    (16, "Saint-Paul", "saint-paul"),
    (17, "Saint-Philippe", "saint-philippe"),
    (18, "Saint-Pierre", "saint-pierre"),
    (19, "Sainte-Marie", "sainte-marie"),
    (20, "Sainte-Rose", "sainte-rose"),
    (21, "Sainte-Suzanne", "sainte-suzanne"),
    (22, "Salazie", "salazie"),
    (23, "Le Tampon", "le-tampon"),
    (24, "Trois-Bassins", "trois-bassins"),
]


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


def _next_available_category_slug(cur, base_slug: str) -> str:
    base = base_slug or "categorie"
    candidate = base
    suffix = 1
    while True:
        cur.execute("SELECT 1 FROM categories WHERE slug = ?", (candidate,))
        if not cur.fetchone():
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1


def _ensure_category(cur, category_name: str):
    normalized = (category_name or "").strip()
    if not normalized:
        return None, None

    cur.execute("SELECT id, nom FROM categories WHERE nom = ?", (normalized,))
    row = cur.fetchone()
    if row:
        return row[0], row[1]

    # Fallback robuste si des variantes de casse/espaces existent déjà.
    cur.execute(
        "SELECT id, nom FROM categories WHERE LOWER(TRIM(nom)) = LOWER(?) ORDER BY id ASC LIMIT 1",
        (normalized,),
    )
    row = cur.fetchone()
    if row:
        return row[0], row[1]

    slug = _next_available_category_slug(cur, slugify(normalized))
    cur.execute("INSERT INTO categories (nom, slug) VALUES (?, ?)", (normalized, slug))
    return cur.lastrowid, normalized


def _backfill_sites_category_id(cur) -> int:
    has_legacy_category = column_exists(cur, "sites", "categorie")

    if has_legacy_category:
        cur.execute(
            """
            SELECT id, categorie, category_id
            FROM sites
            WHERE (category_id IS NOT NULL AND category_id != '')
               OR (categorie IS NOT NULL AND TRIM(categorie) != '')
            ORDER BY id ASC
            """
        )
    else:
        cur.execute(
            """
            SELECT id, NULL AS categorie, category_id
            FROM sites
            WHERE category_id IS NOT NULL AND category_id != ''
            ORDER BY id ASC
            """
        )
    rows = cur.fetchall()
    updated = 0

    for site_id, category_text, category_id in rows:
        target_id = None

        if category_id:
            cur.execute("SELECT nom FROM categories WHERE id = ?", (category_id,))
            existing = cur.fetchone()
            if existing:
                target_id = category_id

        if not target_id and has_legacy_category:
            target_id, _target_name = _ensure_category(cur, category_text)

        if not target_id:
            continue

        cur.execute(
            "UPDATE sites SET category_id = ? WHERE id = ?",
            (target_id, site_id),
        )
        updated += 1

    return updated


def _drop_sites_categorie_column(cur) -> bool:
    if not column_exists(cur, "sites", "categorie"):
        return False

    print("🧹 Suppression de la colonne legacy sites.categorie")
    cur.execute(
        """
        CREATE TABLE sites_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            ville TEXT,
            lien TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            status TEXT DEFAULT 'en_attente',
            date_ajout DATETIME,
            en_vedette INTEGER DEFAULT 0,
            click_count INTEGER DEFAULT 0,
            ville_id INTEGER REFERENCES villes(id)
        )
        """
    )
    cur.execute(
        """
        INSERT INTO sites_new (
            id, nom, ville, lien, description, category_id, status, date_ajout, en_vedette, click_count, ville_id
        )
        SELECT
            id,
            nom,
            ville,
            lien,
            description,
            category_id,
            COALESCE(status, 'en_attente'),
            date_ajout,
            COALESCE(en_vedette, 0),
            COALESCE(click_count, 0),
            ville_id
        FROM sites
        """
    )
    cur.execute("DROP TABLE sites")
    cur.execute("ALTER TABLE sites_new RENAME TO sites")
    return True


def _drop_sites_ville_column(cur) -> bool:
    if not column_exists(cur, "sites", "ville"):
        return False

    print("🧹 Suppression de la colonne legacy sites.ville")
    cur.execute(
        """
        CREATE TABLE sites_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            lien TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            status TEXT DEFAULT 'en_attente',
            date_ajout DATETIME,
            en_vedette INTEGER DEFAULT 0,
            click_count INTEGER DEFAULT 0,
            ville_id INTEGER REFERENCES villes(id)
        )
        """
    )
    cur.execute(
        """
        INSERT INTO sites_new (
            id, nom, lien, description, category_id, status, date_ajout, en_vedette, click_count, ville_id
        )
        SELECT
            id,
            nom,
            lien,
            description,
            category_id,
            COALESCE(status, 'en_attente'),
            date_ajout,
            COALESCE(en_vedette, 0),
            COALESCE(click_count, 0),
            ville_id
        FROM sites
        """
    )
    cur.execute("DROP TABLE sites")
    cur.execute("ALTER TABLE sites_new RENAME TO sites")
    return True


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
                lien TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                status TEXT DEFAULT 'en_attente',
                date_ajout DATETIME,
                en_vedette INTEGER DEFAULT 0,
                click_count INTEGER DEFAULT 0
            )
            """
        )

        # Colonnes manquantes possibles sur sites
        ensure_column(cur, "sites", "status", "TEXT DEFAULT 'en_attente'")
        ensure_column(cur, "sites", "date_ajout", "DATETIME")
        ensure_column(cur, "sites", "en_vedette", "INTEGER DEFAULT 0")
        ensure_column(cur, "sites", "click_count", "INTEGER DEFAULT 0")
        ensure_column(cur, "sites", "category_id", "INTEGER")

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

        # Backfill category_id depuis la colonne legacy si encore présente.
        sites_updated = _backfill_sites_category_id(cur)
        print(f"🔁 Backfill category_id effectué sur {sites_updated} site(s)")

        # Normalisation canonique des villes:
        # désactive temporairement les FK pour permettre les remaps d'IDs.
        conn.commit()
        cur.execute("PRAGMA foreign_keys = OFF")

        # Supprime définitivement la colonne legacy sites.categorie.
        _drop_sites_categorie_column(cur)

        canonical_by_id = {city_id: (nom, slug) for city_id, nom, slug in CANONICAL_VILLES}
        canonical_by_slug = {slug: city_id for city_id, _nom, slug in CANONICAL_VILLES}
        canonical_by_norm_name = {slugify(nom): city_id for city_id, nom, _slug in CANONICAL_VILLES}
        canonical_ids = set(canonical_by_id.keys())
        has_legacy_ville = column_exists(cur, "sites", "ville")

        # 1) Assure la présence des IDs canoniques (slug temporaire pour éviter les collisions)
        for city_id, nom, _slug in CANONICAL_VILLES:
            cur.execute(
                "INSERT OR IGNORE INTO villes (id, nom, slug) VALUES (?, ?, ?)",
                (city_id, nom, f"tmp-ville-{city_id}"),
            )

        # 2) Remap des anciennes lignes villes vers les IDs canoniques selon le slug
        cur.execute("SELECT id, nom, slug FROM villes")
        existing_cities = cur.fetchall()
        for row in existing_cities:
            old_id = row[0]
            old_nom = row[1]
            old_slug = row[2]
            target_id = canonical_by_slug.get(old_slug) or canonical_by_norm_name.get(slugify(old_nom))
            if target_id and old_id != target_id:
                cur.execute("SELECT 1 FROM villes WHERE id = ?", (target_id,))
                if cur.fetchone():
                    cur.execute("UPDATE sites SET ville_id = ? WHERE ville_id = ?", (target_id, old_id))
                else:
                    cur.execute("UPDATE sites SET ville_id = NULL WHERE ville_id = ?", (old_id,))
                cur.execute("DELETE FROM villes WHERE id = ?", (old_id,))

        # 3) Applique strictement la table canonique (nom + slug + id)
        for city_id, nom, slug in CANONICAL_VILLES:
            cur.execute(
                """
                INSERT INTO villes (id, nom, slug)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nom = excluded.nom,
                    slug = excluded.slug
                """,
                (city_id, nom, slug),
            )

        # 4) Répare les sites qui ont un ville_id hors liste canonique
        if has_legacy_ville:
            cur.execute(
                """
                SELECT id, ville, ville_id
                FROM sites
                WHERE ville_id IS NOT NULL
                """
            )
        else:
            cur.execute(
                """
                SELECT id, NULL AS ville, ville_id
                FROM sites
                WHERE ville_id IS NOT NULL
                """
            )
        sites_with_city_id = cur.fetchall()
        for site_id, ville_nom, ville_id in sites_with_city_id:
            if ville_id in canonical_ids:
                continue
            normalized = slugify(ville_nom or "")
            target_id = canonical_by_slug.get(normalized)
            if target_id:
                cur.execute("SELECT 1 FROM villes WHERE id = ?", (target_id,))
                exists = cur.fetchone() is not None
            else:
                exists = False
            cur.execute(
                "UPDATE sites SET ville_id = ? WHERE id = ?",
                (target_id if exists else None, site_id),
            )

        # 5) Backfill sites.ville_id à partir de sites.ville quand manquant
        if has_legacy_ville:
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
                target_id = canonical_by_slug.get(slugify(ville))
                if target_id:
                    cur.execute("SELECT 1 FROM villes WHERE id = ?", (target_id,))
                    if cur.fetchone():
                        cur.execute("UPDATE sites SET ville_id = ? WHERE id = ?", (target_id, site_id))

        # 6) Nettoyage: supprime les villes non canoniques restantes
        cur.execute(
            "DELETE FROM villes WHERE id NOT IN ({})".format(",".join("?" for _ in canonical_ids)),
            tuple(sorted(canonical_ids)),
        )

        # Supprime définitivement la colonne legacy sites.ville.
        _drop_sites_ville_column(cur)

        # Réactive l'intégrité référentielle
        cur.execute("PRAGMA foreign_keys = ON")

        # Index utiles
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)")
        cur.execute("DROP INDEX IF EXISTS idx_sites_categorie")
        cur.execute("DROP INDEX IF EXISTS idx_sites_ville")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_category_id ON sites(category_id)")
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
