# -*- coding: utf-8 -*-

from flask import (
    Flask,
    current_app,
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
from dotenv import load_dotenv
import locale
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
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import config

# >>> AJOUT : imports utilitaires pour un slug ASCII propre (sans emojis/accents)
import re
import unicodedata
import smtplib
import ssl
from email.message import EmailMessage
import secrets
from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)



# CONFIGURATION : Chargement selon l'environnement
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))
app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(hours=8))
app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
if env == "production":
    app.config.setdefault("SESSION_COOKIE_SECURE", True)
csrf = CSRFProtect(app)


def get_client_ip() -> str:
    """Retourne l'IP cliente réelle derrière un reverse proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


default_limit = app.config.get("RATELIMIT_DEFAULT")



# SÉCURITÉ : Rate limiting pour éviter le spam avec Redis
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
    strategy="fixed-window",
    default_limits=[default_limit] if default_limit else []
)
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
            ville TEXT,
            lien TEXT NOT NULL,
            description TEXT,
            categorie TEXT,
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

    # ======================
    # INDEXES
    # ======================
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sites_categorie ON sites(categorie)")
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

@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/blog")
def blog():
    return render_template("blog.html")


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
    """Récupère les catégories triées par clics + sites en vedette triés par clics."""
    conn = get_db_connection()
    if not conn:
        return {}, {}

    try:
        cur = conn.cursor()

        # Catégories triées par popularité (somme des clics)
        cur.execute(
            """
            SELECT
                categorie,
                COUNT(*) AS site_count,
                COALESCE(SUM(click_count), 0) AS total_clicks
            FROM sites
            WHERE status = 'valide'
              AND categorie IS NOT NULL
              AND TRIM(categorie) != ''
            GROUP BY categorie
            ORDER BY total_clicks DESC, site_count DESC, categorie COLLATE NOCASE ASC
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

        # Sites en vedette: triés d'abord par clics
        cur.execute(
            """
            SELECT
                s.*,
                v.nom AS ville_nom,
                v.slug AS ville_slug
            FROM sites s
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE s.status = 'valide' AND s.en_vedette = 1
            ORDER BY s.categorie ASC, s.click_count DESC, s.date_ajout DESC
            """
        )

        for site in cur.fetchall():
            cat = site["categorie"]
            if cat in data:
                data[cat].append(site)

        for cat in data:
            data[cat].sort(
                key=lambda s: ((s["click_count"] or 0), (s["date_ajout"] or "")),
                reverse=True,
            )
            data[cat] = data[cat][:3]


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
            SELECT id, nom, lien, categorie, description, date_ajout
            FROM sites
            WHERE status = 'valide'
            ORDER BY date_ajout DESC
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
            SELECT id, nom, lien, categorie, description, click_count
            FROM sites
            WHERE status = 'valide'
            ORDER BY click_count DESC
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
        # Utilise la table categories si elle existe, sinon fallback sur les sites valides
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
        )
        has_table = cur.fetchone() is not None

        if has_table:
            cur.execute("SELECT nom FROM categories ORDER BY nom COLLATE NOCASE ASC")
            results = cur.fetchall()
            categories = [row[0] for row in results if row[0]]

            # Synchronise les catégories manquantes depuis la table sites
            cur.execute("SELECT DISTINCT categorie FROM sites WHERE categorie IS NOT NULL AND TRIM(categorie) != ''")
            site_categories = [row[0] for row in cur.fetchall() if row[0]]
            missing = [cat for cat in site_categories if cat not in categories]
            for cat in missing:
                slug = generate_unique_category_slug(cur, cat)
                cur.execute(
                    "INSERT OR IGNORE INTO categories (nom, slug) VALUES (?, ?)",
                    (cat, slug),
                )
            if missing:
                conn.commit()
                categories.extend(missing)

            # Si aucune catégorie n'est encore enregistrée, fallback pour éviter de casser le front
            if not categories:
                cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
                results = cur.fetchall()
                categories = [row[0] for row in results if row[0]]
        else:
            cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
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

#obtenir le nom de la categorie depuis le slug 
def get_nom_categorie_depuis_slug(slug):
    categories_slug = get_categories_slug()
    #si le slug du cat correspond au slug alors on retourne le cat, donc non sluggé
    for cat, cat_slug in categories_slug.items():
        if cat_slug == slug:
            return cat
    return None


@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():
    form = AdminLoginForm()
    next_url = request.args.get("next")
    if not is_safe_next_url(next_url):
        next_url = url_for("admin_dashboard")

    if form.validate_on_submit():
        if verify_admin_credentials(form.username.data, form.password.data):
            session.clear()
            session.permanent = True
            session["admin_authenticated"] = True
            session["admin_username"] = form.username.data
            session["admin_login_at"] = datetime.utcnow().isoformat()
            flash("Connexion réussie.", "success")
            return redirect(next_url)
        flash("Identifiants invalides.", "error")

    return render_template("admin/login.html", form=form, next_url=next_url)


@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    form = AdminLogoutForm()
    if not form.validate_on_submit():
        abort(400)
    session.clear()
    flash("Déconnexion effectuée.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("accueil"))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nom, categorie, ville, lien, description, status, date_ajout
            FROM sites
            WHERE status = 'en_attente'
            ORDER BY date_ajout DESC, id DESC
            """
        )
        pending_sites = cur.fetchall()

        cur.execute(
            "SELECT status, COUNT(*) as total FROM sites GROUP BY status"
        )
        stats_rows = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des propositions: {e}")
        flash("Erreur lors de la récupération des propositions.", "error")
        pending_sites = []
        stats_rows = []
    finally:
        conn.close()

    stats = {row["status"]: row["total"] for row in stats_rows}

    current_path = request.full_path.rstrip("?")
    action_forms = {}
    for site in pending_sites:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        form.return_to.data = current_path
        action_forms[site["id"]] = form

    return render_template(
        "admin/dashboard.html",
        pending_sites=pending_sites,
        stats=stats,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
    )


@app.route("/admin/sites", methods=["GET"])
@admin_required
def admin_sites():
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_dashboard"))

    status_filter = (request.args.get("status") or "all").strip()
    city_filter = (request.args.get("city") or "all").strip()
    query_text = (request.args.get("q") or "").strip()
    sort_filter = (request.args.get("sort") or "date_desc").strip()
    page = parse_positive_int(request.args.get("page"), default=1)
    per_page = 50

    allowed_status = {"all", "valide", "en_attente", "refuse"}
    allowed_sorts = {
        "date_desc": "s.date_ajout DESC, s.id DESC",
        "date_asc": "s.date_ajout ASC, s.id ASC",
        "clicks_desc": "s.click_count DESC, s.id DESC",
        "clicks_asc": "s.click_count ASC, s.id ASC",
        "name_asc": "s.nom COLLATE NOCASE ASC, s.id DESC",
        "name_desc": "s.nom COLLATE NOCASE DESC, s.id DESC",
    }

    if status_filter not in allowed_status:
        status_filter = "all"
    if sort_filter not in allowed_sorts:
        sort_filter = "date_desc"
    if len(query_text) > 120:
        query_text = query_text[:120]

    try:
        cur = conn.cursor()
        cur.execute("SELECT nom, slug FROM villes ORDER BY nom COLLATE NOCASE ASC")
        cities = cur.fetchall()

        allowed_city_slugs = {row["slug"] for row in cities}
        if city_filter != "all" and city_filter not in allowed_city_slugs:
            city_filter = "all"

        where_clauses = ["1=1"]
        params = []

        if status_filter != "all":
            where_clauses.append("s.status = ?")
            params.append(status_filter)

        if city_filter != "all":
            where_clauses.append("v.slug = ?")
            params.append(city_filter)

        if query_text:
            like = f"%{query_text}%"
            where_clauses.append(
                """
                (
                    s.nom LIKE ?
                    OR s.categorie LIKE ?
                    OR s.description LIKE ?
                    OR s.lien LIKE ?
                    OR COALESCE(v.nom, s.ville, '') LIKE ?
                )
                """
            )
            params.extend([like, like, like, like, like])

        where_sql = " AND ".join(where_clauses)
        sort_sql = allowed_sorts[sort_filter]

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM sites s
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE {where_sql}
        """
        cur.execute(count_sql, params)
        total_sites = cur.fetchone()["total"]

        total_pages = max((total_sites + per_page - 1) // per_page, 1)
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page

        query_sql = f"""
            SELECT
                s.id,
                s.nom,
                s.categorie,
                COALESCE(v.nom, s.ville) AS ville_display,
                v.slug AS ville_slug,
                s.lien,
                s.description,
                s.status,
                s.date_ajout,
                s.en_vedette,
                s.click_count
            FROM sites s
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE {where_sql}
            ORDER BY {sort_sql}
            LIMIT ? OFFSET ?
        """
        cur.execute(query_sql, params + [per_page, offset])
        all_sites = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des sites: {e}")
        flash("Erreur lors du chargement des sites.", "error")
        all_sites = []
        cities = []
        total_sites = 0
        total_pages = 1
        page = 1
    finally:
        conn.close()

    current_path = request.full_path.rstrip("?")
    action_forms = {}
    for site in all_sites:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        form.return_to.data = current_path
        action_forms[site["id"]] = form

    return render_template(
        "admin/sites.html",
        sites=all_sites,
        action_forms=action_forms,
        cities=cities,
        status_filter=status_filter,
        city_filter=city_filter,
        query_text=query_text,
        sort_filter=sort_filter,
        page=page,
        total_pages=total_pages,
        total_sites=total_sites,
        admin_username=session.get("admin_username"),
    )


@app.route("/admin/clicks", methods=["GET"])
@admin_required
def admin_clicks():
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_dashboard"))

    query_text = (request.args.get("q") or "").strip()
    sort_filter = (request.args.get("sort") or "newest").strip()
    days_filter = parse_positive_int(request.args.get("days"), default=30)
    page = parse_positive_int(request.args.get("page"), default=1)
    per_page = 100

    if len(query_text) > 120:
        query_text = query_text[:120]
    if sort_filter not in {"newest", "oldest"}:
        sort_filter = "newest"
    if days_filter not in {1, 7, 30, 90, 365}:
        days_filter = 30

    try:
        cur = conn.cursor()
        where_clauses = [
            "sc.clicked_at >= datetime('now', ?)"
        ]
        params = [f"-{days_filter} days"]

        if query_text:
            like = f"%{query_text}%"
            where_clauses.append(
                """
                (
                    s.nom LIKE ?
                    OR s.categorie LIKE ?
                    OR COALESCE(v.nom, s.ville, '') LIKE ?
                    OR s.lien LIKE ?
                    OR sc.user_agent LIKE ?
                )
                """
            )
            params.extend([like, like, like, like, like])

        where_sql = " AND ".join(where_clauses)
        sort_sql = "sc.clicked_at DESC, sc.id DESC" if sort_filter == "newest" else "sc.clicked_at ASC, sc.id ASC"

        cur.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM site_clicks sc
            JOIN sites s ON s.id = sc.site_id
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE {where_sql}
            """,
            params,
        )
        total_clicks = cur.fetchone()["total"]
        total_pages = max((total_clicks + per_page - 1) // per_page, 1)
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page

        cur.execute(
            f"""
            SELECT
                sc.id,
                sc.site_id,
                sc.ip_address,
                sc.user_agent,
                sc.clicked_at,
                s.nom AS site_nom,
                s.categorie,
                COALESCE(v.nom, s.ville) AS ville,
                s.status
            FROM site_clicks sc
            JOIN sites s ON s.id = sc.site_id
            LEFT JOIN villes v ON v.id = s.ville_id
            WHERE {where_sql}
            ORDER BY {sort_sql}
            LIMIT ? OFFSET ?
            """,
            params + [per_page, offset],
        )
        rows = cur.fetchall()

        click_events = []
        delete_forms = {}
        current_path = request.full_path.rstrip("?")
        for row in rows:
            row_dict = dict(row)
            row_dict["ip_masked"] = mask_ip(row["ip_address"])
            click_events.append(row_dict)
            delete_forms[row["id"]] = DeleteClickForm(click_id=str(row["id"]))

    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors du chargement des clics admin: {e}")
        flash("Erreur lors du chargement des clics.", "error")
        click_events = []
        delete_forms = {}
        current_path = url_for("admin_clicks")
        total_clicks = 0
        total_pages = 1
        page = 1
    finally:
        conn.close()

    return render_template(
        "admin/clicks.html",
        click_events=click_events,
        delete_forms=delete_forms,
        query_text=query_text,
        sort_filter=sort_filter,
        days_filter=days_filter,
        page=page,
        total_pages=total_pages,
        total_clicks=total_clicks,
        return_to=current_path,
        admin_username=session.get("admin_username"),
    )


@app.route("/admin/clicks/<int:click_id>/delete", methods=["POST"])
@admin_required
def admin_delete_click(click_id):
    form = DeleteClickForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_clicks"))

    try:
        form_click_id = int(form.click_id.data)
    except (TypeError, ValueError):
        abort(400)

    if form_click_id != click_id:
        abort(400)

    return_to = request.form.get("return_to", "")
    if not is_safe_next_url(return_to):
        return_to = url_for("admin_clicks")

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(return_to)

    try:
        cur = conn.cursor()
        cur.execute("SELECT site_id FROM site_clicks WHERE id = ?", (click_id,))
        click_row = cur.fetchone()
        if not click_row:
            flash("Clic introuvable.", "error")
            return redirect(return_to)

        site_id = click_row["site_id"]
        cur.execute("DELETE FROM site_clicks WHERE id = ?", (click_id,))
        if cur.rowcount == 0:
            flash("Clic introuvable.", "error")
            conn.rollback()
            return redirect(return_to)

        cur.execute(
            """
            UPDATE sites
            SET click_count = CASE WHEN click_count > 0 THEN click_count - 1 ELSE 0 END
            WHERE id = ?
            """,
            (site_id,),
        )
        conn.commit()
        flash("Événement de clic supprimé.", "success")
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de la suppression du clic {click_id}: {e}")
        flash("Erreur lors de la suppression du clic.", "error")
    finally:
        conn.close()

    return redirect(return_to)


@app.route("/admin/categories", methods=["GET"])
@admin_required
def admin_categories():
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nom, slug, created_at
            FROM categories
            ORDER BY nom COLLATE NOCASE ASC
            """
        )
        categories = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des catégories: {e}")
        flash("Erreur lors du chargement des catégories.", "error")
        categories = []
    finally:
        conn.close()

    delete_forms = {cat["id"]: DeleteCategoryForm(category_id=str(cat["id"])) for cat in categories}

    return render_template(
        "admin/categories.html",
        categories_=categories,
        delete_forms=delete_forms,
        admin_username=session.get("admin_username"),
    )


@app.route("/admin/categories/new", methods=["GET", "POST"])
@admin_required
def admin_create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_categories"))
        try:
            cur = conn.cursor()
            # Vérifie unicité du nom
            cur.execute("SELECT id FROM categories WHERE nom = ?", (form.nom.data,))
            if cur.fetchone():
                flash("Cette catégorie existe déjà.", "error")
                conn.close()
                return redirect(url_for("admin_categories"))

            slug = generate_unique_category_slug(cur, form.nom.data)
            cur.execute(
                "INSERT INTO categories (nom, slug) VALUES (?, ?)",
                (form.nom.data, slug),
            )
            conn.commit()
            flash("Catégorie créée.", "success")
            return redirect(url_for("admin_categories"))
        except sqlite3.Error as e:
            conn.rollback()
            app.logger.error(f"Erreur lors de la création d'une catégorie: {e}")
            flash("Erreur lors de la création de la catégorie.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_category.html",
        form=form,
        admin_username=session.get("admin_username"),
        page_title="Créer une catégorie",
        submit_label="Créer la catégorie",
    )


@app.route("/admin/categories/<int:category_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_category(category_id):
    form = CategoryForm()
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_categories"))

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, nom, slug FROM categories WHERE id = ?",
            (category_id,),
        )
        category = cur.fetchone()
    except sqlite3.Error as e:
        conn.close()
        app.logger.error(f"Erreur lors du chargement de la catégorie {category_id}: {e}")
        flash("Impossible de charger la catégorie.", "error")
        return redirect(url_for("admin_categories"))

    if not category:
        conn.close()
        flash("Catégorie introuvable.", "error")
        return redirect(url_for("admin_categories"))

    if request.method == "GET":
        form.nom.data = category["nom"]
    elif form.validate_on_submit():
        try:
            cur.execute(
                "SELECT id FROM categories WHERE nom = ? AND id != ?",
                (form.nom.data, category_id),
            )
            if cur.fetchone():
                flash("Une autre catégorie porte déjà ce nom.", "error")
                conn.close()
                return redirect(url_for("admin_categories"))

            slug = generate_unique_category_slug(cur, form.nom.data, exclude_id=category_id)
            old_nom = category["nom"]
            cur.execute(
                "UPDATE categories SET nom = ?, slug = ? WHERE id = ?",
                (form.nom.data, slug, category_id),
            )
            # Mets à jour les sites qui pointaient vers l'ancien nom
            cur.execute(
                "UPDATE sites SET categorie = ? WHERE categorie = ?",
                (form.nom.data, old_nom),
            )
            conn.commit()
            flash("Catégorie mise à jour.", "success")
            conn.close()
            return redirect(url_for("admin_categories"))
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            app.logger.error(f"Erreur lors de la mise à jour de la catégorie {category_id}: {e}")
            flash("Erreur lors de la mise à jour.", "error")
            return redirect(url_for("admin_categories"))

    conn.close()
    return render_template(
        "admin/edit_category.html",
        form=form,
        admin_username=session.get("admin_username"),
        page_title=f"Éditer la catégorie « {category['nom']} »",
        submit_label="Enregistrer",
    )


@app.route("/admin/categories/<int:category_id>/delete", methods=["POST"])
@admin_required
def admin_delete_category(category_id):
    form = DeleteCategoryForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_categories"))

    try:
        category_id_form = int(form.category_id.data)
    except (TypeError, ValueError):
        abort(400)

    if category_id != category_id_form:
        abort(400)

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_categories"))

    try:
        cur = conn.cursor()
        cur.execute("SELECT nom FROM categories WHERE id = ?", (category_id,))
        row = cur.fetchone()
        if not row:
            flash("Catégorie introuvable.", "error")
            conn.close()
            return redirect(url_for("admin_categories"))

        cur.execute(
            "SELECT COUNT(*) as total FROM sites WHERE categorie = ?",
            (row["nom"],),
        )
        usage = cur.fetchone()["total"]
        if usage > 0:
            flash("Impossible de supprimer : des sites utilisent encore cette catégorie.", "error")
            conn.close()
            return redirect(url_for("admin_categories"))

        cur.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        flash("Catégorie supprimée.", "success")
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de la suppression de la catégorie {category_id}: {e}")
        flash("Erreur lors de la suppression.", "error")
    finally:
        conn.close()

    return redirect(url_for("admin_categories"))


@app.route("/admin/propositions/<int:site_id>", methods=["POST"])
@admin_required
def admin_update_site(site_id):
    form = ModerationActionForm()
    return_to = form.return_to.data if is_safe_next_url(form.return_to.data or "") else url_for("admin_dashboard")
    if not form.validate_on_submit():
        app.logger.warning(f"Modération formulaire invalide: {form.errors}")
        flash("Formulaire invalide.", "error")
        return redirect(return_to)

    try:
        site_id_form = int(form.site_id.data)
    except (TypeError, ValueError):
        abort(400)

    if site_id_form != site_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete", "pending"}:
        flash("Action inconnue.", "error")
        return redirect(return_to)

    conn = get_db_connection()
    if not conn:
        flash("Impossible d'accéder à la base de données.", "error")
        return redirect(return_to)

    message = ""
    try:
        cur = conn.cursor()
        if action == "approve":
            cur.execute(
                "UPDATE sites SET status = 'valide', date_ajout = DATETIME('now') WHERE id = ?",
                (site_id,),
            )
            message = "Proposition validée et publiée."
        elif action == "reject":
            cur.execute(
                "UPDATE sites SET status = 'refuse' WHERE id = ?",
                (site_id,),
            )
            message = "Proposition refusée."
        elif action == "pending":
            cur.execute(
                "UPDATE sites SET status = 'en_attente' WHERE id = ?",
                (site_id,),
            )
            message = "Statut remis en attente."
        else:
            cur.execute("DELETE FROM sites WHERE id = ?", (site_id,))
            message = "Proposition supprimée."

        if cur.rowcount == 0:
            flash("Proposition introuvable.", "error")
            conn.rollback()
        else:
            conn.commit()
            flash(message, "success")
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de la mise à jour de la proposition {site_id}: {e}")
        flash("Erreur lors de la mise à jour de la proposition.", "error")
    finally:
        conn.close()

    return redirect(return_to)


@app.route("/admin/propositions/<int:site_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_site(site_id):
    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nom, categorie, ville, lien, description, status, en_vedette
            FROM sites
            WHERE id = ?
            """,
            (site_id,),
        )
        site = cur.fetchone()
    except sqlite3.Error as e:
        conn.close()
        app.logger.error(f"Erreur lors de la récupération du site {site_id}: {e}")
        flash("Impossible de charger la proposition.", "error")
        return redirect(url_for("admin_dashboard"))

    if not site:
        conn.close()
        flash("Proposition introuvable.", "error")
        return redirect(url_for("admin_dashboard"))

    form = AdminSiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    form.ville.choices = get_city_choices()
    posted_category = request.form.get("categorie")
    posted_ville = request.form.get("ville")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))
    if posted_ville and posted_ville not in [choice[0] for choice in form.ville.choices]:
        form.ville.choices.append((posted_ville, posted_ville))

    if request.method == "GET":
        form.nom.data = site["nom"]
        if site["ville"] and site["ville"] not in [choice[0] for choice in form.ville.choices]:
            form.ville.choices.append((site["ville"], site["ville"]))
        form.ville.data = site["ville"] or ""
        form.lien.data = site["lien"]
        form.description.data = site["description"]
        form.status.data = site["status"]
        form.en_vedette.data = bool(site["en_vedette"])
        if site["categorie"] not in categories_list:
            form.categorie.choices.append((site["categorie"], site["categorie"]))
        form.categorie.data = site["categorie"]
    elif form.validate_on_submit():
        conn_to_update = get_db_connection()
        if not conn_to_update:
            flash("Impossible de se connecter à la base de données.", "error")
            conn.close()
            return redirect(url_for("admin_dashboard"))
        # Sécurise la catégorie envoyée (doit exister)
        if form.categorie.data not in [choice[0] for choice in form.categorie.choices if choice[0]]:
            flash("Catégorie non valide.", "error")
            conn.close()
            conn_to_update.close()
            return redirect(url_for("admin_dashboard"))
        try:
            cur_update = conn_to_update.cursor()
            cur_update.execute(
                """
                UPDATE sites
                SET nom = ?, ville = ?, lien = ?, description = ?, categorie = ?, status = ?, en_vedette = ?
                WHERE id = ?
                """,
                (
                    form.nom.data,
                    form.ville.data or None,
                    form.lien.data,
                    form.description.data,
                    form.categorie.data,
                    form.status.data,
                    1 if form.en_vedette.data else 0,
                    site_id,
                ),
            )
            if cur_update.rowcount == 0:
                flash("La mise à jour a échoué : proposition introuvable.", "error")
                conn_to_update.rollback()
            else:
                conn_to_update.commit()
                flash("Proposition mise à jour avec succès.", "success")
            conn_to_update.close()
            conn.close()
            return redirect(url_for("admin_dashboard"))
        except sqlite3.Error as e:
            conn_to_update.rollback()
            conn_to_update.close()
            conn.close()
            app.logger.error(f"Erreur lors de la mise à jour du site {site_id}: {e}")
            flash("Erreur lors de la mise à jour.", "error")
            return redirect(url_for("admin_dashboard"))
    else:
        flash("Formulaire invalide.", "error")

    conn.close()
    return render_template(
        "admin/edit_site.html",
        form=form,
        site=site,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_edit_site", site_id=site_id),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier la proposition #{site_id}",
        subtitle=f"Statut actuel : <strong>{site['status']}</strong>",
    )


@app.route("/admin/propositions/new", methods=["GET", "POST"])
@admin_required
def admin_create_site():
    form = AdminSiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    form.ville.choices = get_city_choices()
    posted_category = request.form.get("categorie")
    posted_ville = request.form.get("ville")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))
    if posted_ville and posted_ville not in [choice[0] for choice in form.ville.choices]:
        form.ville.choices.append((posted_ville, posted_ville))

    if form.validate_on_submit():
        if form.categorie.data not in [choice[0] for choice in form.categorie.choices if choice[0]]:
            flash("Catégorie non valide.", "error")
            return redirect(url_for("admin_create_site"))
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_dashboard"))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout, en_vedette)
                VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'), ?)
                """,
                (
                    form.nom.data,
                    form.ville.data or None,
                    form.lien.data,
                    form.description.data,
                    form.categorie.data,
                    form.status.data or "valide",
                    1 if form.en_vedette.data else 0,
                ),
            )
            conn.commit()
            flash(f"Nouveau site ajouté (statut : {form.status.data}).", "success")
            return redirect(url_for("admin_dashboard"))
        except sqlite3.Error as e:
            conn.rollback()
            app.logger.error(f"Erreur lors de la création d'un site depuis l'admin: {e}")
            flash("Erreur lors de l'ajout du site.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_site.html",
        form=form,
        site=None,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_create_site"),
        submit_label="Publier le site",
        page_title="Ajouter un nouveau site",
        subtitle="Complète les champs pour publier le site instantanément.",
    )

@app.route("/")
def accueil():
    data, category_stats = get_sites_en_vedette()
    derniers_sites = get_derniers_sites_global(3)
    top_sites = get_top_sites(5)
    form_inline = SiteForm()
    form_inline.categorie.choices = [(cat, cat) for cat in get_categories()]
    form_inline.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    form_inline.ville.choices = get_city_choices()
    return render_template(
        "index.html",
        data=data,
        category_stats=category_stats,
        derniers_sites=derniers_sites,
        top_sites=top_sites,
        form_inline=form_inline
    )



@app.route("/categorie/<slug>")
def voir_categorie(slug):
    #stocke le nom sans slug
    nom_categorie = get_nom_categorie_depuis_slug(slug)
    if not nom_categorie:
        return render_template("404.html"), 404

    # >>> AJOUT SEO : calcule le slug canonique à partir du nom en BDD
    canonical_slug = slugify(nom_categorie)

    # >>> AJOUT SEO : redirection 301 si l'URL ne correspond pas au slug canonique (emoji, majuscules, etc.)
    if slug != canonical_slug:
        return redirect(url_for('voir_categorie', slug=canonical_slug), code=301)

    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()
    #recupere tous les sites de la categorie par ordre decroissant
    cur.execute("""
       SELECT * FROM sites
       WHERE categorie = ? AND status = 'valide'
       ORDER BY click_count DESC, en_vedette DESC, date_ajout DESC, id DESC 
    """, (nom_categorie,))
    sites = cur.fetchall()
    conn.close()

    # >>> AJOUT SEO : metas dynamiques (utilisées dans categorie.html via les blocks Jinja)
    seo_title = f"{nom_categorie} à La Réunion – Réunion Wiki"
    seo_description = (
        f"Découvrez les meilleurs sites {nom_categorie.lower()} : infos utiles et adresses à La Réunion."
    )
    canonical = url_for('voir_categorie', slug=canonical_slug, _external=True)

    # Prépare un formulaire inline pré-rempli avec la catégorie
    form_inline = SiteForm()
    cats = get_categories()
    form_inline.categorie.choices = [(cat, cat) for cat in cats]
    form_inline.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    form_inline.ville.choices = get_city_choices()
    if nom_categorie in cats:
        form_inline.categorie.data = nom_categorie

    #return sur le html
    return render_template(
        "categorie.html",
        nom_categorie=nom_categorie,
        sites=sites,
        # >>> AJOUT SEO : passe les variables au template
        slug=canonical_slug,
        seo_title=seo_title,
        seo_description=seo_description,
        canonical=canonical,
        form_inline=form_inline
    )


@app.route("/go/<int:site_id>")
def redirect_site(site_id):
    app.logger.info(f"[GO] Tentative de redirection pour site_id={site_id}")

    conn = get_db_connection()
    if not conn:
        app.logger.error("[GO] Connexion DB impossible")
        abort(500)

    try:
        cur = conn.cursor()

        # Vérifie que le site existe
        cur.execute(
            "SELECT lien, click_count FROM sites WHERE id = ? AND status = 'valide'",
            (site_id,)
        )
        row = cur.fetchone()

        if not row:
            app.logger.warning(f"[GO] Site introuvable ou non valide id={site_id}")
            abort(404)

        app.logger.info(
            f"[GO] Site trouvé id={site_id} | ancien compteur={row['click_count']} | url={row['lien']}"
        )
        
        ip = get_client_ip()
        user_agent = (request.headers.get("User-Agent", "") or "")[:400]
        
        # Anti-bot simple
        ua_lower = user_agent.lower()
        if "bot" in ua_lower or "crawl" in ua_lower or "spider" in ua_lower:
            app.logger.info(f"[GO] Bot détecté, clic ignoré id={site_id} ua={user_agent}")
            return redirect(row["lien"])


        # Vérifie si cette IP a cliqué ce site dans les 30 dernières minutes
        cur.execute("""
            SELECT id FROM site_clicks
            WHERE site_id = ?
            AND ip_address = ?
            AND clicked_at >= datetime('now', '-30 minutes')
        """, (site_id, ip))

        recent_click = cur.fetchone()

        if not recent_click:
            # Incrémente compteur
            cur.execute(
                "UPDATE sites SET click_count = click_count + 1 WHERE id = ?",
                (site_id,)
            )

            # Log clic
            cur.execute("""
                INSERT INTO site_clicks (site_id, ip_address, user_agent)
                VALUES (?, ?, ?)
            """, (site_id, ip, user_agent))

            conn.commit()

            app.logger.info(f"[GO] Clic validé id={site_id} ip={ip}")
        else:
            app.logger.info(f"[GO] Clic ignoré (trop récent) id={site_id} ip={ip}")

        return redirect(row["lien"])

    except sqlite3.Error as e:
        app.logger.error(f"[GO] Erreur SQLite site_id={site_id} | {e}")
        abort(500)

    finally:
        conn.close()
        app.logger.info(f"[GO] Connexion DB fermée pour site_id={site_id}")



@app.route("/sites-ajoutes-recemment")
def recently_added_sites():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()
#recupere tous les sites par ordre descroissant d'ajout
    cur.execute("""
        SELECT id, nom, lien, categorie, description, date_ajout
        FROM sites
        WHERE status = 'valide'
        ORDER BY date_ajout DESC
    """)
    
    sites = cur.fetchall()
    conn.close()

    return render_template("recently-added-sites.html", sites=sites)



@app.route("/mentions-legales")
def legal_notices():
    return render_template("legal-notices.html")


@app.route("/sites-les-plus-visites")
def most_visited_sites():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nom, lien, categorie, description, click_count
        FROM sites
        WHERE status = 'valide'
        ORDER BY click_count DESC
    """)
    sites = cur.fetchall()
    conn.close()

    return render_template("most-visited-sites.html", sites=sites)



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


@app.route("/recherche")
def search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return redirect(url_for("accueil"))

    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500

    cur = conn.cursor()

    like = f"%{q}%"

    # Normalisation "saint-denis" <-> "saint denis"
    q_city = " ".join(q.lower().replace("-", " ").split())
    like_city = f"%{q_city}%"

    cur.execute(
        """
        SELECT id, nom, lien, ville, categorie, description, click_count, date_ajout
        FROM sites
        WHERE status = 'valide'
          AND (
            nom LIKE ?
            OR categorie LIKE ?
            OR description LIKE ?
            OR lien LIKE ?
            OR ville LIKE ?
            OR LOWER(REPLACE(COALESCE(ville, ''), '-', ' ')) LIKE ?
          )
        ORDER BY
          CASE
            WHEN nom LIKE ? THEN 0
            WHEN categorie LIKE ? THEN 1
            WHEN description LIKE ? THEN 2
            WHEN ville LIKE ? OR LOWER(REPLACE(COALESCE(ville, ''), '-', ' ')) LIKE ? THEN 3
            WHEN lien LIKE ? THEN 4
            ELSE 5
          END,
          click_count DESC,
          date_ajout DESC
        LIMIT 100
        """,
        (
            like, like, like, like, like, like_city,
            like, like, like, like, like_city, like
        ),
    )

    sites = cur.fetchall()
    conn.close()

    return render_template("search-results.html", q=q, sites=sites)





@app.route('/service-worker.js')
def service_worker():
    response = make_response(send_from_directory('static', 'service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response    


@app.route('/google87e16279463c4021.html')
def google_verification():
    return app.send_static_file('google87e16279463c4021.html')


@app.route("/proposer-site", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # SÉCURITÉ : Limite les soumissions de formulaire
def website_submission_form():
    """SÉCURITÉ : Formulaire avec validation complète"""
    form = SiteForm()
    
    # Charge les catégories dynamiquement pour le SelectField
    form.categorie.choices = [(cat, cat) for cat in get_categories()]
    form.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    form.ville.choices = get_city_choices()
    
    if form.validate_on_submit():
        nom = form.nom.data
        ville = form.ville.data or None
        lien = form.lien.data
        description = form.description.data
        categorie = form.categorie.data

        if categorie not in get_categories():
            flash("Catégorie non valide.", "error")
            return render_template("website-submission-form.html", form=form)

        conn = get_db_connection()
        if not conn:
            flash("Erreur technique. Veuillez réessayer plus tard.", "error")
            return render_template("website-submission-form.html", form=form)
        
        try:
            cur = conn.cursor()

            # SÉCURITÉ : Insertion avec paramètres liés (protection contre SQL injection)
            cur.execute("""
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout)
                VALUES (?, ?, ?, ?, ?, 'en_attente', DATETIME('now'))
            """, (
                nom,
                ville,
                lien,
                description,
                categorie
            ))
            
            conn.commit()
            send_submission_notification({
                "nom": nom,
                "ville": ville,
                "lien": lien,
                "description": description,
                "categorie": categorie,
                "date_submission": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "remote_addr": request.remote_addr or "IP inconnue",
            })
            flash("Merci, ta proposition a bien été envoyée ! Elle sera validée prochainement.", "success")
            return redirect(url_for("accueil"))
            
        except sqlite3.Error as e:
            app.logger.error(f"Erreur lors de l'insertion du site: {e}")
            flash("Erreur lors de l'enregistrement. Veuillez réessayer.", "error")
        finally:
            conn.close()
    
    # Si GET ou website-submission-form invalide → affiche le formulaire avec erreurs
    return render_template("website-submission-form.html", form=form)
#decorateur, injecte automatiquement variable dans tous les templates Jinja2




@app.context_processor
def inject_categories():
    return {
        "categories": get_categories(),
        "categories_slug": get_categories_slug()
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

@app.route("/villes")
def villes_index():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()

    cur.execute("""
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

    """)
    villes = cur.fetchall()
    conn.close()

    return render_template("cities.html", villes=villes)


@app.route("/ville/<slug>")
def voir_ville(slug):
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()

    cur.execute("SELECT id, nom, slug FROM villes WHERE slug = ?", (slug,))
    ville = cur.fetchone()
    if not ville:
        conn.close()
        return render_template("404.html"), 404

    cur.execute("""
        SELECT s.*
        FROM sites s
        WHERE s.status = 'valide' AND s.ville_id = ?
        ORDER BY s.en_vedette DESC, s.date_ajout DESC
    """, (ville["id"],))
    sites = cur.fetchall()

    cur.execute("""
        SELECT COALESCE(SUM(click_count), 0) AS total_clicks
        FROM sites
        WHERE status = 'valide' AND ville_id = ?
    """, (ville["id"],))
    total_clicks = cur.fetchone()["total_clicks"]

    conn.close()
    return render_template("city.html", ville=ville, sites=sites, total_clicks=total_clicks)



@app.route("/categories-les-plus-visitees")
def most_visited_categories():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                categorie,
                COUNT(*) AS site_count,
                COALESCE(SUM(click_count), 0) AS total_clicks
            FROM sites
            WHERE status = 'valide'
              AND categorie IS NOT NULL
              AND TRIM(categorie) != ''
            GROUP BY categorie
            ORDER BY total_clicks DESC, site_count DESC, categorie COLLATE NOCASE ASC
            """
        )
        categories_rank = cur.fetchall()
        return render_template("most-visited-categories.html", categories_rank=categories_rank)
    finally:
        conn.close()

@app.route("/tendances")
def trends():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500

    try:
        cur = conn.cursor()

        # Top en ce moment (7 jours) + variation vs 7 jours précédents
        cur.execute(
            """
            WITH clicks_7 AS (
                SELECT site_id, COUNT(*) AS c7
                FROM site_clicks
                WHERE clicked_at >= datetime('now', '-7 days')
                GROUP BY site_id
            ),
            clicks_prev7 AS (
                SELECT site_id, COUNT(*) AS cprev
                FROM site_clicks
                WHERE clicked_at >= datetime('now', '-14 days')
                  AND clicked_at < datetime('now', '-7 days')
                GROUP BY site_id
            )
            SELECT
                s.id,
                s.nom,
                s.categorie,
                COALESCE(c7.c7, 0) AS clicks_7d,
                COALESCE(cp.cprev, 0) AS clicks_prev_7d,
                CASE
                    WHEN COALESCE(cp.cprev, 0) = 0 THEN NULL
                    ELSE ROUND((COALESCE(c7.c7, 0) - cp.cprev) * 100.0 / cp.cprev, 1)
                END AS growth_pct
            FROM sites s
            LEFT JOIN clicks_7 c7 ON c7.site_id = s.id
            LEFT JOIN clicks_prev7 cp ON cp.site_id = s.id
            WHERE s.status = 'valide'
            ORDER BY clicks_7d DESC, growth_pct DESC
            LIMIT 10
            """
        )
        trending_sites = cur.fetchall()

        # Top stable (30 jours)
        cur.execute(
            """
            SELECT
                s.id,
                s.nom,
                s.categorie,
                COUNT(sc.id) AS clicks_30d
            FROM sites s
            LEFT JOIN site_clicks sc
              ON sc.site_id = s.id
             AND sc.clicked_at >= datetime('now', '-30 days')
            WHERE s.status = 'valide'
            GROUP BY s.id, s.nom, s.categorie
            ORDER BY clicks_30d DESC
            LIMIT 10
            """
        )
        stable_sites = cur.fetchall()

        # Catégories en hausse (7j vs 7j précédents)
        cur.execute(
            """
            WITH c7 AS (
                SELECT s.categorie, COUNT(sc.id) AS clicks_7d
                FROM sites s
                LEFT JOIN site_clicks sc
                  ON sc.site_id = s.id
                 AND sc.clicked_at >= datetime('now', '-7 days')
                WHERE s.status = 'valide'
                GROUP BY s.categorie
            ),
            cp AS (
                SELECT s.categorie, COUNT(sc.id) AS clicks_prev_7d
                FROM sites s
                LEFT JOIN site_clicks sc
                  ON sc.site_id = s.id
                 AND sc.clicked_at >= datetime('now', '-14 days')
                 AND sc.clicked_at < datetime('now', '-7 days')
                WHERE s.status = 'valide'
                GROUP BY s.categorie
            )
            SELECT
                c7.categorie,
                COALESCE(c7.clicks_7d, 0) AS clicks_7d,
                COALESCE(cp.clicks_prev_7d, 0) AS clicks_prev_7d,
                CASE
                    WHEN COALESCE(cp.clicks_prev_7d, 0) = 0 THEN NULL
                    ELSE ROUND((COALESCE(c7.clicks_7d, 0) - cp.clicks_prev_7d) * 100.0 / cp.clicks_prev_7d, 1)
                END AS growth_pct
            FROM c7
            LEFT JOIN cp ON cp.categorie = c7.categorie
            WHERE c7.categorie IS NOT NULL AND TRIM(c7.categorie) != ''
            ORDER BY clicks_7d DESC, growth_pct DESC
            LIMIT 10
            """
        )
        trending_categories = cur.fetchall()

        # Nouveaux sites qui performent (ajoutés récemment + clics 7j)
        cur.execute(
            """
            SELECT
                s.id,
                s.nom,
                s.categorie,
                COUNT(sc.id) AS clicks_7d
            FROM sites s
            LEFT JOIN site_clicks sc
              ON sc.site_id = s.id
             AND sc.clicked_at >= datetime('now', '-7 days')
            WHERE s.status = 'valide'
              AND s.date_ajout >= datetime('now', '-30 days')
            GROUP BY s.id, s.nom, s.categorie
            ORDER BY clicks_7d DESC
            LIMIT 10
            """
        )
        new_performers = cur.fetchall()

        return render_template(
            "trends.html",
            trending_sites=trending_sites,
            stable_sites=stable_sites,
            trending_categories=trending_categories,
            new_performers=new_performers,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
