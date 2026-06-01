# -*- coding: utf-8 -*-

from flask import (
    Flask,
    render_template,
    make_response,
    send_from_directory,
    request,
    flash,
    url_for,
    redirect,
    session,
    g,
    has_request_context,
    abort,
)
from datetime import datetime, timedelta
import sqlite3
import os
from urllib.parse import urlparse
from forms import (
    AdminLoginForm,
    AdminLogoutForm,
    ModerationActionForm,
    SiteForm,
    AdminSiteForm,
    CategoryForm,
    DeleteCategoryForm,
    DeleteClickForm,
)
from flask_wtf.csrf import CSRFError
from extensions import csrf, limiter
from config import config

# >>> AJOUT : imports utilitaires pour un slug ASCII propre (sans emojis/accents)
import re
import unicodedata
import smtplib
import ssl
from email.message import EmailMessage
import secrets
import sys
from functools import wraps
from werkzeug.security import check_password_hash
from flask import send_from_directory


sys.modules.setdefault("app", sys.modules[__name__])

app = Flask(__name__)

ICON_MAP = {
    "culture-et-loisirs": "map.svg",
    "actualites": "newspaper.svg",
    "achats": "shopping-cart.svg",
    "transport": "bus.svg",
    "emploi-et-formation": "briefcase.svg",
    "meteo-et-alertes": "cloud-rain.svg",
    "administratifs": "file-text.svg",
    "nourriture": "utensils.svg",
    "sante": "heart.svg",
}



# CONFIGURATION : Chargement selon l'environnement
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))
app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(hours=8))
app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
if env == "production":
    app.config.setdefault("SESSION_COOKIE_SECURE", True)
csrf.init_app(app)


def get_client_ip() -> str:
    """Retourne l'IP cliente réelle derrière un reverse proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


default_limit = app.config.get("RATELIMIT_DEFAULT")
app.config.setdefault("RATELIMIT_STORAGE_URI", app.config.get('RATELIMIT_STORAGE_URL', 'memory://'))
app.config.setdefault("RATELIMIT_STRATEGY", "fixed-window")
if default_limit:
    app.config.setdefault("RATELIMIT_DEFAULT", default_limit)
limiter.init_app(app)

# SÉCURITÉ : Fonction utilitaire pour gérer les connexions SQLite
def get_db_connection():
    """Retourne une connexion sécurisée à la base de données"""
    try:
     

        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")


        init_db_schema(conn)

        return conn

    except Exception as e:
        print("ERREUR COMPLETE :", e)
        raise  # important pour voir la vraie erreur



def send_submission_notification(payload):
    """Envoie un email de notification lorsqu'un site est proposé."""
    if not app.config.get('MAIL_ENABLED'):
        return

    server = app.config.get('MAIL_SERVER')
    recipients = app.config.get('MAIL_RECIPIENTS', [])
    if not server or not recipients:
        app.logger.warning("Notification email non envoyée : serveur ou destinataires non configurés.")
        return

    sender = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME') or recipients[0]
    message = EmailMessage()
    message['Subject'] = f"Nouvelle proposition Réunion Wiki : {payload.get('nom')}"
    message['From'] = sender
    message['To'] = ", ".join(recipients)
    message.set_content(render_template("emails/new_submission.txt", **payload))

    context = ssl.create_default_context()
    try:
        if app.config.get('MAIL_USE_SSL'):
            with smtplib.SMTP_SSL(server, app.config.get('MAIL_PORT'), context=context) as smtp:
                username = app.config.get('MAIL_USERNAME')
                password = app.config.get('MAIL_PASSWORD')
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(server, app.config.get('MAIL_PORT')) as smtp:
                smtp.ehlo()
                if app.config.get('MAIL_USE_TLS'):
                    smtp.starttls(context=context)
                username = app.config.get('MAIL_USERNAME')
                password = app.config.get('MAIL_PASSWORD')
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
    except Exception as e:
        app.logger.error(f"Erreur lors de l'envoi de l'email de notification: {e}")


def verify_admin_credentials(username, password):
    """Vérifie les identifiants admin configurés via les variables d'environnement."""
    stored_username = app.config.get('ADMIN_USERNAME')
    stored_password = app.config.get('ADMIN_PASSWORD')
    stored_hash = app.config.get('ADMIN_PASSWORD_HASH')

    if not stored_username:
        app.logger.warning("Tentative de connexion admin alors que ADMIN_USERNAME est vide.")
        return False

    if not secrets.compare_digest(username, stored_username):
        return False

    if stored_hash:
        try:
            return check_password_hash(stored_hash, password)
        except ValueError:
            app.logger.error("ADMIN_PASSWORD_HASH invalide : utilisez werkzeug.security.generate_password_hash.")
            return False

    if stored_password:
        return secrets.compare_digest(stored_password, password)

    app.logger.warning("Tentative de connexion admin sans mot de passe configuré.")
    return False


def is_safe_next_url(next_url: str) -> bool:
    """Autorise uniquement les chemins locaux internes."""
    if not next_url:
        return False
    if not next_url.startswith("/") or next_url.startswith("//"):
        return False
    parsed = urlparse(next_url)
    return parsed.scheme == "" and parsed.netloc == ""


def parse_positive_int(value, default=1):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def mask_ip(ip_value: str) -> str:
    """Masque les IP dans l'admin pour limiter l'exposition de données personnelles."""
    if not ip_value:
        return "—"
    ip = ip_value.split(",")[0].strip()
    if ":" in ip:  # IPv6
        parts = ip.split(":")
        return ":".join(parts[:3]) + ":*:*"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.x.x"
    return "—"


def admin_required(func):
    """Décorateur de protection des routes admin."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_authenticated'):
            next_url = request.path if request.method == "GET" else url_for('admin_dashboard')
            if not next_url.startswith('/'):
                next_url = url_for('admin_dashboard')
            return redirect(url_for('admin_login', next=next_url))
        return func(*args, **kwargs)

    return wrapper

# Cache en memoire pour eviter de recreer la table categories a chaque requete
_HAS_CATEGORIES_TABLE = False



@app.context_processor
def asset_versioning():
    def asset_v(path):
        full = os.path.join(app.static_folder, path)
        try:
            return int(os.path.getmtime(full))
        except OSError:
            return 1
    return {"asset_v": asset_v}


@app.context_processor
def inject_admin_logout_form():
    if session.get("admin_authenticated"):
        return {"admin_logout_form": AdminLogoutForm()}
    return {}


def init_db_schema(conn):
    """Initialise et migre le schéma de la base si nécessaire."""
    cur = conn.cursor()

    # ======================
    # TABLE SITES (si inexistante)
    # ======================
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

    # ======================
    # MIGRATION COLONNES SITES
    # ======================
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

    # ======================
    # TABLE SITE_CLICKS
    # ======================
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

    # ======================
    # TABLE VILLES
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS villes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
    """)

    # ======================
    # TABLE CATEGORIES (ta logique)
    # ======================
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Backfill léger pour les anciennes BDD qui ont encore sites.categorie.
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
            cur.execute(
                "UPDATE sites SET category_id = ? WHERE id = ?",
                (resolved_id, row["id"]),
            )

    # Backfill léger pour les anciennes BDD qui ont encore sites.ville.
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
            cur.execute(
                "UPDATE sites SET ville_id = ? WHERE id = ?",
                (resolved_id, row["id"]),
            )

    # ======================
    # INDEXES
    # ======================
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)")
    cur.execute("DROP INDEX IF EXISTS idx_sites_categorie")
    cur.execute("DROP INDEX IF EXISTS idx_sites_ville")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_category_id ON sites(category_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_click_count ON sites(click_count)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_ville_id ON sites(ville_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_site_clicks_site_id ON site_clicks(site_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_site_clicks_clicked_at ON site_clicks(clicked_at)")

    conn.commit()

# GESTION D'ERREURS : Pages d'erreur personnalisées
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erreur serveur: {e}")
    return render_template('500.html'), 500


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.warning(f"CSRF bloqué: {e.description}")
    flash("Session expirée ou formulaire invalide. Réessaie.", "error")
    return redirect(request.referrer or url_for("accueil"))

# PERFORMANCE : Headers de cache pour les réponses
@app.after_request
def add_cache_headers(response):
    """Ajoute des headers de cache optimisés selon le type de contenu"""
    if request.endpoint == 'service_worker':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    elif request.endpoint == 'static':
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    elif request.endpoint in ['accueil', 'voir_categorie']:
        # Pages dynamiques : cache court
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
    elif request.endpoint == 'website_submission_form':
        # Formulaires : pas de cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    # SÉCURITÉ : Headers de sécurité
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # SÉCURITÉ : CSP gérée par nginx, pas par Flask
    # if env == 'production':
    #     # CSP désactivée - gérée par nginx
    #     pass
    
    return response



def format_date(value, fmt="%d/%m/%Y"):
    if not value:
        return ""
    if isinstance(value, str):
        for pat in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                value = datetime.strptime(value, pat)
                break
            except ValueError:
                continue
    return value.strftime(fmt)

# ENREGISTREMENT (faites l’un OU l’autre)
app.jinja_env.filters["format_date"] = format_date
# ou:
# @app.template_filter("format_date")
# def format_date_filter(value, fmt="%d/%m/%Y"): ...

# ... les routes en dessous


# SÉCURITÉ : Récupère les sites pré-sélectionnés avec gestion d'erreurs
def get_sites_en_vedette():
    """Récupère les catégories triées par clics + sites vedette (sinon top clics)."""
    conn = get_db_connection()
    if not conn:
        return {}, {}

    try:
        cur = conn.cursor()

        # Catégories triées par popularité (somme des clics)
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

        # 1) Sites en vedette (si présents dans la catégorie)
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

        # 2) Fallback: sites les plus cliqués par catégorie (tous les sites valides)
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
        app.logger.error(f"Erreur lors de la récupération des sites en vedette: {e}")
        return {}, {}
    finally:
        conn.close()

# SÉCURITÉ : Récupère les derniers sites avec gestion d'erreurs
def get_derniers_sites_global(limit=3):
    """Récupère les derniers sites ajoutés"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        # Récupère les derniers sites ajoutés par date d'ajout pour la page index
        cur.execute("""
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
        """, (limit,))

        return cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des derniers sites: {e}")
        return []
    finally:
        conn.close()



def get_top_sites(limit=5):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute("""
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
        """, (limit,))
        return cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur top sites: {e}")
        return []
    finally:
        conn.close()




# SÉCURITÉ : Récupère les catégories avec gestion d'erreurs
def get_categories():
    """Récupère les catégories depuis la table dédiée si disponible."""
    if has_request_context() and hasattr(g, "_categories_cache"):
        return g._categories_cache

    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        # Utilise la table categories si elle existe, sinon fallback depuis les liens sites -> categories.
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
        )
        has_table = cur.fetchone() is not None

        if has_table:
            cur.execute("SELECT nom FROM categories ORDER BY nom COLLATE NOCASE ASC")
            results = cur.fetchall()
            categories = [row[0] for row in results if row[0]]
        else:
            categories = []

        # Fallback: reconstruit la liste depuis les sites valides reliés à categories.
        if not categories and has_table:
            cur.execute(
                """
                SELECT DISTINCT c.nom
                FROM sites s
                JOIN categories c ON c.id = s.category_id
                WHERE s.status = 'valide'
                  AND c.nom IS NOT NULL
                  AND TRIM(c.nom) != ''
                ORDER BY c.nom COLLATE NOCASE ASC
                """
            )
            results = cur.fetchall()
            categories = [row[0] for row in results if row[0]]

        categories = sorted(set(categories), key=lambda x: x.lower())
        if has_request_context():
            g._categories_cache = categories
        return categories
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des catégories: {e}")
        return []
    finally:
        conn.close()


def get_city_choices():
    """Retourne les choix de villes pour les formulaires publics."""
    if has_request_context() and hasattr(g, "_city_choices_cache"):
        return g._city_choices_cache

    choices = [("", "Non précisée")]
    conn = get_db_connection()
    if not conn:
        return choices

    try:
        cur = conn.cursor()
        cur.execute("SELECT nom FROM villes ORDER BY nom COLLATE NOCASE ASC")
        for row in cur.fetchall():
            nom = row["nom"]
            if nom:
                choices.append((nom, nom))
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors du chargement des villes: {e}")
    finally:
        conn.close()

    if has_request_context():
        g._city_choices_cache = choices
    return choices

#slug pour rendre compatible le nom de categorie dans la barre d'adresse
def slugify(nom):
    # >>> AJOUT : slug ASCII propre et stable (supprime emojis/accents/symboles)
    # - garde uniquement lettres/chiffres/espaces/-/_
    # - remplace '&' par 'et' (cohérent avec ton code existant)
    nom = nom.replace("&", "et")
    # retire tout caractère non utile (dont emojis) sauf lettres/chiffres/espace/-/_
    nom = ''.join(ch for ch in nom if ch.isalnum() or ch.isspace() or ch in "-_")
    # décompose les accents, puis convertit en ASCII
    nom = unicodedata.normalize('NFKD', nom).encode('ascii', 'ignore').decode('ascii')
    nom = nom.lower().strip()
    nom = re.sub(r'[\s_]+', '-', nom)      # espaces/underscores -> tirets
    nom = re.sub(r'[^a-z0-9-]', '', nom)   # supprime le reste
    nom = re.sub(r'-{2,}', '-', nom).strip('-')  # normalise tirets
    return nom


def generate_unique_category_slug(cursor, nom, exclude_id=None):
    """Génère un slug unique pour la table categories."""
    base_slug = slugify(nom) or "categorie"
    candidate = base_slug
    suffix = 1
    while True:
        if exclude_id:
            cursor.execute(
                "SELECT id FROM categories WHERE slug = ? AND id != ?",
                (candidate, exclude_id),
            )
        else:
            cursor.execute(
                "SELECT id FROM categories WHERE slug = ?",
                (candidate,),
            )
        row = cursor.fetchone()
        if not row:
            return candidate
        candidate = f"{base_slug}-{suffix}"
        suffix += 1


def resolve_category(cursor, category_name):
    """Retourne (id, nom) pour une catégorie, en la créant si nécessaire."""
    normalized = (category_name or "").strip()
    if not normalized:
        return None

    cursor.execute("SELECT id, nom FROM categories WHERE nom = ?", (normalized,))
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    cursor.execute(
        "SELECT id, nom FROM categories WHERE LOWER(TRIM(nom)) = LOWER(?) ORDER BY id ASC LIMIT 1",
        (normalized,),
    )
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    slug = generate_unique_category_slug(cursor, normalized)
    cursor.execute(
        "INSERT INTO categories (nom, slug) VALUES (?, ?)",
        (normalized, slug),
    )
    return cursor.lastrowid, normalized


def resolve_city(cursor, city_name):
    """Retourne (id, nom) pour une ville existante."""
    normalized = (city_name or "").strip()
    if not normalized:
        return None

    cursor.execute("SELECT id, nom FROM villes WHERE nom = ?", (normalized,))
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    cursor.execute(
        "SELECT id, nom FROM villes WHERE LOWER(TRIM(nom)) = LOWER(?) ORDER BY id ASC LIMIT 1",
        (normalized,),
    )
    row = cursor.fetchone()
    if row:
        return row["id"], row["nom"]

    city_slug = slugify_ville(normalized)
    if city_slug:
        cursor.execute(
            "SELECT id, nom FROM villes WHERE slug = ? ORDER BY id ASC LIMIT 1",
            (city_slug,),
        )
        row = cursor.fetchone()
        if row:
            return row["id"], row["nom"]

    return None


#obtenir le nom de la categorie depuis le slug 
def get_nom_categorie_depuis_slug(slug):
    categories_slug = get_categories_slug()
    #si le slug du cat correspond au slug alors on retourne le cat, donc non sluggé
    for cat, cat_slug in categories_slug.items():
        if cat_slug == slug:
            return cat
    return None












@app.context_processor
def inject_categories():
    return {
        "categories": get_categories(),
        "categories_slug": get_categories_slug(),
        "ICON_MAP": ICON_MAP,
    }





def get_categories_slug():
    if has_request_context() and hasattr(g, "_categories_slug_cache"):
        return g._categories_slug_cache

    categories = get_categories()
    conn = get_db_connection()
    categories_slug = {}

    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
            )
            has_table = cur.fetchone() is not None
            if has_table:
                cur.execute("SELECT nom, slug FROM categories")
                rows = cur.fetchall()
                categories_slug = {row["nom"]: row["slug"] for row in rows}
        except sqlite3.Error as e:
            app.logger.error(f"Erreur lors de la récupération des slugs de catégories: {e}")
        finally:
            conn.close()

    # Si la table n'existe pas ou est vide, on calcule les slugs à la volée
    if not categories_slug:
        categories_slug = {cat: slugify(cat) for cat in categories}

    if has_request_context():
        g._categories_slug_cache = categories_slug
    return categories_slug




def slugify_ville(nom: str) -> str:
    s = (nom or "").strip().lower()
    repl = {
        "à":"a","â":"a","ä":"a","é":"e","è":"e","ê":"e","ë":"e",
        "î":"i","ï":"i","ô":"o","ö":"o","ù":"u","û":"u","ü":"u","ç":"c"
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    for ch in ["'", "’", ".", ","]:
        s = s.replace(ch, "")
    s = "-".join(s.split())
    return s


@app.template_filter('month_name')
def month_name(date_value):
    if isinstance(date_value, str):
        dt = datetime.fromisoformat(date_value)
    else:
        dt = date_value

    mois_fr = [
        "JAN", "FÉV", "MAR", "AVR", "MAI", "JUN",
        "JUI", "AOÛ", "SEP", "OCT", "NOV", "DÉC"
    ]

    return mois_fr[dt.month - 1]


def register_legacy_blueprint_endpoints(bp_name, endpoint_names):
    """Keep pre-blueprint endpoint names available for existing url_for calls."""
    for endpoint_name in endpoint_names:
        blueprint_endpoint = f"{bp_name}.{endpoint_name}"
        if blueprint_endpoint not in app.view_functions:
            continue

        app.view_functions[endpoint_name] = app.view_functions.pop(blueprint_endpoint)
        rules = app.url_map._rules_by_endpoint.pop(blueprint_endpoint, [])
        for rule in rules:
            rule.endpoint = endpoint_name
        app.url_map._rules_by_endpoint.setdefault(endpoint_name, []).extend(rules)


from routes.admin import admin_bp
from routes.public import public_bp
from routes.seo import seo_bp

app.register_blueprint(admin_bp)
app.register_blueprint(public_bp)
app.register_blueprint(seo_bp)

register_legacy_blueprint_endpoints(
    "admin",
    [
        "admin_login",
        "admin_logout",
        "admin_dashboard",
        "admin_sites",
        "admin_clicks",
        "admin_delete_click",
        "admin_categories",
        "admin_create_category",
        "admin_edit_category",
        "admin_delete_category",
        "admin_update_site",
        "admin_edit_site",
        "admin_create_site",
    ],
)
register_legacy_blueprint_endpoints(
    "public",
    [
        "faq",
        "blog",
        "accueil",
        "voir_categorie",
        "redirect_site",
        "recently_added_sites",
        "legal_notices",
        "most_visited_sites",
        "search",
        "website_submission_form",
        "villes_index",
        "voir_ville",
        "most_visited_categories",
        "trends",
    ],
)
register_legacy_blueprint_endpoints(
    "seo",
    [
        "service_worker",
        "google_verification",
        "robots_txt",
        "sitemap",
    ],
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
