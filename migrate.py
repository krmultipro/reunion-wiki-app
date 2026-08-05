import os
import re
import shutil
import sqlite3
from datetime import datetime
from flask import Flask
from config import config
from social_guides import SOCIAL_GUIDES

# Charge la config Flask
app = Flask(__name__)
env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config.get(env, config["default"]))
DATABASE_PATH = app.config["DATABASE_PATH"]
UPLOAD_FOLDER = app.config["UPLOAD_FOLDER"]
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

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


def _next_upload_collision_path(path: str) -> str:
    """Retourne un chemin disponible en cas de collision de fichier uploadé.

    Args:
        path (str): Chemin cible initial.

    Returns:
        str:
            Chemin disponible sans écraser un fichier existant.
    """

    root, extension = os.path.splitext(path)
    suffix = 2
    candidate = f"{root}-legacy-{suffix}{extension}"
    while os.path.exists(candidate):
        suffix += 1
        candidate = f"{root}-legacy-{suffix}{extension}"
    return candidate


def _copy_upload_source(source_dir: str, target_root: str) -> int:
    """Copie les uploads d'un ancien dossier vers le dossier persistant.

    Args:
        source_dir (str): Ancienne racine des uploads.
        target_root (str): Nouvelle racine persistante.

    Returns:
        int:
            Nombre de fichiers copiés.
    """

    if not os.path.isdir(source_dir):
        return 0

    source_dir = os.path.abspath(source_dir)
    target_root = os.path.abspath(target_root)
    if source_dir == target_root:
        return 0

    copied = 0
    for current_dir, _dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            source_path = os.path.join(current_dir, filename)
            relative_path = os.path.relpath(source_path, source_dir)
            target_path = os.path.join(target_root, relative_path)
            if os.path.abspath(source_path) == os.path.abspath(target_path):
                continue
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            if os.path.exists(target_path):
                if os.path.getsize(source_path) == os.path.getsize(target_path):
                    continue
                target_path = _next_upload_collision_path(target_path)
            shutil.copy2(source_path, target_path)
            copied += 1
    return copied


def _migrate_upload_files() -> None:
    """Regroupe les anciens uploads dans le dossier persistant configuré."""

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    sources = [
        os.path.join(PROJECT_ROOT, "static", "uploads"),
        os.path.join(PROJECT_ROOT, "uploads_dev"),
        os.path.join(PROJECT_ROOT, "uploads_prod"),
    ]
    total = 0
    for source in sources:
        copied = _copy_upload_source(source, UPLOAD_FOLDER)
        if copied:
            print(f"🖼️ Uploads copiés depuis {source}: {copied} fichier(s)")
            total += copied
    if not total:
        print("🖼️ Aucun ancien upload à migrer")


def rename_column_if_needed(cur, table_name: str, old_name: str, new_name: str) -> None:
    """Renomme une colonne legacy uniquement si la colonne cible n'existe pas.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.
        table_name (str): Nom de la table à faire évoluer.
        old_name (str): Nom actuel de la colonne legacy.
        new_name (str): Nouveau nom attendu.

    Returns:
        None
    """

    if column_exists(cur, table_name, old_name) and not column_exists(cur, table_name, new_name):
        print(f"✏️ Renommage colonne {table_name}.{old_name} -> {new_name}")
        cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}")


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


def _ensure_content_table(cur) -> None:
    """Crée la table `content` et ses index si nécessaire.

    Table plate et réutilisable qui alimentera les pages SEO publiées depuis
    l'admin (landing pages, guides, personnalités...). Les images ne sont jamais
    stockées ici : seul le chemin relatif sur disque est conservé dans
    `featured_image`.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.
    """

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            summary TEXT,
            body TEXT,
            status TEXT NOT NULL DEFAULT 'draft',
            meta_title TEXT,
            meta_description TEXT,
            featured_image TEXT,
            published_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_content_slug ON content(slug)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_content_type_status ON content(content_type, status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_content_status_pub ON content(status, published_at)")


def _ensure_social_content_pages(cur) -> None:
    """Crée les sélections sociales avec des textes éditoriaux par défaut.

    Les contenus existants ne sont jamais modifiés afin de préserver toutes les
    personnalisations réalisées depuis l'administration.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        None
    """

    created = 0
    for guide in SOCIAL_GUIDES.values():
        cur.execute("SELECT 1 FROM content WHERE slug = ?", (guide["slug"],))
        if cur.fetchone():
            continue
        cur.execute(
            """
            INSERT INTO content (
                content_type, title, slug, summary, body, status,
                meta_title, meta_description, featured_image, published_at
            ) VALUES ('seo_landing', ?, ?, ?, ?, 'published', ?, ?, NULL, CURRENT_TIMESTAMP)
            """,
            (
                guide["title"],
                guide["slug"],
                guide["summary"],
                guide["body"],
                guide["meta_title"],
                guide["meta_description"],
            ),
        )
        created += 1
    print(f"🌐 Sélections sociales créées: {created}")


def _normalize_editorial_value(value: str | None) -> str:
    """Normalise les espaces pour reconnaître un ancien texte éditorial.

    Args:
        value (str | None): Valeur enregistrée dans la base.

    Returns:
        str: Valeur sans espaces de présentation significatifs.
    """

    return re.sub(r"\s+", " ", (value or "").strip())


def _upgrade_youtube_default_copy(cur) -> None:
    """Actualise uniquement les anciens textes YouTube non personnalisés.

    Les anciennes installations possèdent soit le texte historique de la page,
    soit la première version du guide dynamique. Chaque champ est remplacé
    seulement s'il correspond encore à l'une de ces valeurs connues, afin de ne
    pas écraser une personnalisation réalisée dans l'administration.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        None
    """

    guide = SOCIAL_GUIDES["youtube"]
    legacy_summaries = {
        _normalize_editorial_value(
            "Découvrez plusieurs youtubeurs réunionnais et créateurs de contenu "
            "qui participent au rayonnement de La Réunion sur les réseaux sociaux."
        ),
        _normalize_editorial_value(
            "Découvrez les youtubeurs et chaînes de La Réunion qui partagent vidéos, "
            "divertissement, musique, documentaires et culture locale."
        ),
    }
    legacy_bodies = {
        _normalize_editorial_value(
            """
            <p>
            La Réunion compte de nombreux créateurs de contenu actifs sur YouTube,
            TikTok et Instagram. Ils partagent leur quotidien, leur humour,
            leurs voyages et leur vision de l'île.
            </p>

            <h2>Pourquoi suivre les créateurs réunionnais ?</h2>

            <p>
            Ils permettent de découvrir La Réunion sous un angle local et authentique.
            </p>
            """
        ),
        _normalize_editorial_value(
            "<h2>Découvrir la création vidéo réunionnaise</h2>"
            "<p>La Réunion compte des chaînes YouTube aux univers variés : humour, musique, "
            "voyage, cuisine, pêche, médias et documentaires. Cette sélection permet de "
            "retrouver leurs fiches et leurs liens officiels.</p>"
            "<h2>Une sélection locale mise à jour</h2>"
            "<p>La liste évolue automatiquement lorsque de nouveaux talents publiés ajoutent "
            "leur chaîne YouTube sur Réunion Wiki.</p>"
        ),
    }

    cur.execute(
        "SELECT summary, body FROM content WHERE slug = ?",
        (guide["slug"],),
    )
    row = cur.fetchone()
    if not row:
        return

    current_summary, current_body = row
    new_summary = current_summary
    new_body = current_body
    if _normalize_editorial_value(current_summary) in legacy_summaries:
        new_summary = guide["summary"]
    if _normalize_editorial_value(current_body) in legacy_bodies:
        new_body = guide["body"]

    if new_summary == current_summary and new_body == current_body:
        return

    cur.execute(
        """
        UPDATE content
        SET summary = ?, body = ?, updated_at = CURRENT_TIMESTAMP
        WHERE slug = ?
        """,
        (new_summary, new_body, guide["slug"]),
    )
    print("✍️ Texte par défaut du guide YouTube actualisé")


def _next_available_talent_slug(cur, base_slug: str, talent_id: int) -> str:
    """Retourne un slug talent unique en ignorant la ligne en cours.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.
        base_slug (str): Base de slug générée depuis le nom.
        talent_id (int): Identifiant du talent en cours de backfill.

    Returns:
        str: Slug disponible pour la table talents.
    """

    base = base_slug or f"talent-{talent_id}"
    candidate = base
    suffix = 1
    while True:
        cur.execute(
            "SELECT 1 FROM talents WHERE slug = ? AND id != ?",
            (candidate, talent_id),
        )
        if not cur.fetchone():
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1


def _backfill_talent_slugs(cur) -> int:
    """Complète les slugs manquants de la table talents à partir du nom.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        int: Nombre de talents mis à jour.
    """

    cur.execute(
        """
        SELECT id, name
        FROM talents
        WHERE slug IS NULL OR TRIM(slug) = ''
        ORDER BY id ASC
        """
    )
    rows = cur.fetchall()
    updated = 0

    for talent_id, name in rows:
        slug = _next_available_talent_slug(cur, slugify(name), talent_id)
        cur.execute("UPDATE talents SET slug = ? WHERE id = ?", (slug, talent_id))
        updated += 1

    return updated


def _dedupe_talent_slugs(cur) -> int:
    """Rend uniques tous les slugs talents avant la création de l'index.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        int: Nombre de slugs modifiés.
    """

    cur.execute("SELECT id, name, slug FROM talents ORDER BY id ASC")
    rows = cur.fetchall()
    seen = set()
    updated = 0

    for talent_id, name, slug in rows:
        base = slugify(slug or "") or slugify(name or "") or f"talent-{talent_id}"
        candidate = base
        suffix = 2
        while candidate in seen:
            candidate = f"{base}-{suffix}"
            suffix += 1
        seen.add(candidate)

        if candidate != (slug or ""):
            cur.execute("UPDATE talents SET slug = ? WHERE id = ?", (candidate, talent_id))
            updated += 1

    return updated


def _normalize_talent_statuses(cur) -> int:
    """Convertit les anciens statuts talents vers le workflow courant.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        int: Nombre de talents mis à jour.
    """

    updates = 0
    cur.execute("UPDATE talents SET status = 'published' WHERE status = 'valide'")
    updates += cur.rowcount
    cur.execute("UPDATE talents SET status = 'draft' WHERE status = 'en_attente'")
    updates += cur.rowcount
    return updates


def _ensure_talent_categories_table(cur) -> None:
    """Crée la table des catégories talents et ses index.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        None
    """

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS talent_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
        """
    )
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_talent_categories_slug ON talent_categories(slug)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_talent_categories_name ON talent_categories(name)")


def _create_final_talents_table(cur, table_name="talents") -> None:
    """Crée une table talents conforme au schéma final normalisé.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.
        table_name (str): Nom de la table à créer.

    Returns:
        None
    """

    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT DEFAULT '',
            entity_type TEXT NOT NULL DEFAULT 'person',
            category_id INTEGER NOT NULL,
            city_id INTEGER,
            description TEXT NOT NULL,
            bio TEXT DEFAULT '',
            image TEXT DEFAULT '',
            instagram_url TEXT DEFAULT '',
            youtube_url TEXT DEFAULT '',
            tiktok_url TEXT DEFAULT '',
            facebook_url TEXT DEFAULT '',
            website_url TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft',
            display_order INTEGER DEFAULT 0,
            published_at TEXT,
            FOREIGN KEY(category_id) REFERENCES talent_categories(id),
            FOREIGN KEY(city_id) REFERENCES villes(id)
        )
        """
    )


def _validate_talent_foreign_keys(cur) -> None:
    """Vérifie que les références talents sont prêtes avant reconstruction.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Raises:
        RuntimeError:
            Si une catégorie obligatoire manque ou si une ville est invalide.
    """

    if not column_exists(cur, "talents", "category_id"):
        cur.execute("SELECT COUNT(*) FROM talents")
        total = cur.fetchone()[0]
        if total:
            raise RuntimeError("Migration talents impossible: category_id est absent sur des talents existants.")
        return

    cur.execute(
        """
        SELECT COUNT(*)
        FROM talents t
        LEFT JOIN talent_categories tc ON tc.id = t.category_id
        WHERE t.category_id IS NULL OR tc.id IS NULL
        """
    )
    invalid_categories = cur.fetchone()[0]
    if invalid_categories:
        raise RuntimeError(
            "Migration talents impossible: certains talents n'ont pas de category_id valide."
        )

    if not column_exists(cur, "talents", "city_id"):
        return

    cur.execute(
        """
        SELECT COUNT(*)
        FROM talents t
        LEFT JOIN villes v ON v.id = t.city_id
        WHERE t.city_id IS NOT NULL AND v.id IS NULL
        """
    )
    invalid_cities = cur.fetchone()[0]
    if invalid_cities:
        raise RuntimeError(
            "Migration talents impossible: certains talents ont un city_id invalide."
        )


def _copy_talents_to_final_table(cur) -> None:
    """Recopie les talents existants vers la table finale reconstruite.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        None
    """

    cur.execute(
        """
        INSERT INTO talents_new (
            id,
            name,
            slug,
            entity_type,
            category_id,
            city_id,
            description,
            bio,
            image,
            instagram_url,
            youtube_url,
            tiktok_url,
            facebook_url,
            website_url,
            status,
            display_order,
            published_at
        )
        SELECT
            id,
            name,
            slug,
            entity_type,
            category_id,
            city_id,
            description,
            bio,
            image,
            instagram_url,
            youtube_url,
            tiktok_url,
            facebook_url,
            website_url,
            status,
            display_order,
            published_at
        FROM talents
        """
    )


def _recreate_talent_indexes(cur) -> None:
    """Recrée les index utiles de la table talents.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        None
    """

    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_talents_slug ON talents(slug)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_talents_status ON talents(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_talents_category_id ON talents(category_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_talents_city_id ON talents(city_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_talents_display_order ON talents(display_order)")


def _ensure_talents_table(cur) -> None:
    """Reconstruit la table talents avec le schéma final normalisé.

    Args:
        cur (sqlite3.Cursor): Curseur de la base cible.

    Returns:
        None
    """

    _ensure_talent_categories_table(cur)
    if not table_exists(cur, "talents"):
        _create_final_talents_table(cur)
        _recreate_talent_indexes(cur)
        return

    slugs_updated = _backfill_talent_slugs(cur)
    print(f"🔁 Backfill talents.slug effectué sur {slugs_updated} talent(s)")
    slugs_deduped = _dedupe_talent_slugs(cur)
    print(f"🔁 Dédoublonnage talents.slug effectué sur {slugs_deduped} talent(s)")
    statuses_updated = _normalize_talent_statuses(cur)
    print(f"🔁 Normalisation talents.status effectuée sur {statuses_updated} talent(s)")
    ensure_column(cur, "talents", "entity_type", "TEXT NOT NULL DEFAULT 'person'")
    _validate_talent_foreign_keys(cur)

    cur.execute("DROP TABLE IF EXISTS talents_new")
    _create_final_talents_table(cur, "talents_new")
    _copy_talents_to_final_table(cur)
    cur.execute("DROP TABLE talents")
    cur.execute("ALTER TABLE talents_new RENAME TO talents")
    _recreate_talent_indexes(cur)


def main():
    print("📂 DB cible:", DATABASE_PATH)

    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    _migrate_upload_files()

    # Backup auto
    os.makedirs("backups", exist_ok=True)
    if os.path.exists(DATABASE_PATH):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join("backups", f"base_backup_{ts}.db")
        shutil.copy2(DATABASE_PATH, backup_path)
        print("💾 Backup créé:", backup_path)
    else:
        print("ℹ️ Base absente, création au premier démarrage.")

    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    # WAL améliore la concurrence lecture/écriture. À régler hors transaction.
    cur.execute("PRAGMA journal_mode=WAL")

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

        # Plateforme de contenu SEO (table plate réutilisable).
        _ensure_content_table(cur)
        _ensure_social_content_pages(cur)
        _upgrade_youtube_default_copy(cur)

        # Talents locaux: évolution du prototype Instagram vers un modèle wiki.
        _ensure_talents_table(cur)

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
