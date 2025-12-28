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
from datetime import datetime
import sqlite3
import os
from forms import (
    AdminLoginForm,
    ModerationActionForm,
    SiteForm,
    AdminSiteForm,
    CategoryForm,
    DeleteCategoryForm,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

# Configuration de la base de données
DATABASE_PATH = app.config['DATABASE_PATH']
_HAS_CATEGORIES_TABLE = False

# SÉCURITÉ : Rate limiting pour éviter le spam avec Redis
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
    strategy="fixed-window",
    default_limits=[app.config['RATELIMIT_DEFAULT']]
)
limiter.init_app(app)

# SÉCURITÉ : Fonction utilitaire pour gérer les connexions SQLite
def get_db_connection():
    """Retourne une connexion sécurisée à la base de données"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        init_db_schema(conn)
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Erreur de connexion à la base de données: {e}")
        return None


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


def init_db_schema(conn):
    """Crée la table categories si nécessaire et la pré-remplit depuis sites."""
    global _HAS_CATEGORIES_TABLE
    if _HAS_CATEGORIES_TABLE:
        return

    try:
        cur = conn.cursor()
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
        conn.commit()
        _HAS_CATEGORIES_TABLE = True

        # Pré-remplit avec les catégories existantes si la table est vide
        cur.execute("SELECT COUNT(*) FROM categories")
        existing_count = cur.fetchone()[0]
        if existing_count == 0:
            cur.execute(
                "SELECT DISTINCT categorie FROM sites WHERE categorie IS NOT NULL AND TRIM(categorie) != ''"
            )
            rows = cur.fetchall()
            for row in rows:
                nom_cat = row[0]
                if not nom_cat:
                    continue
                slug = slugify(nom_cat)
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO categories (nom, slug) VALUES (?, ?)",
                        (nom_cat, slug),
                    )
                except sqlite3.IntegrityError:
                    continue
            conn.commit()
    except sqlite3.Error as e:
        app.logger.warning(f"Impossible d'initialiser la table categories: {e}")
        _HAS_CATEGORIES_TABLE = False

# GESTION D'ERREURS : Pages d'erreur personnalisées
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erreur serveur: {e}")
    return render_template('500.html'), 500

# PERFORMANCE : Headers de cache pour les réponses
@app.after_request
def add_cache_headers(response):
    """Ajoute des headers de cache optimisés selon le type de contenu"""
    if request.endpoint in ['static', 'service_worker']:
        # Fichiers statiques : cache long
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 an
    elif request.endpoint in ['accueil', 'voir_categorie']:
        # Pages dynamiques : cache court
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5 minutes
    elif request.endpoint == 'formulaire':
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
    """Récupère les sites en vedette par catégorie"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cur = conn.cursor()

        # Récupère les différentes catégories dont au moins un site a le statut valide
        cur.execute(
            """
                SELECT DISTINCT categorie
                FROM sites
                WHERE status = 'valide'
            """
        )
        categories = [row["categorie"] for row in cur.fetchall() if row["categorie"]]
        if has_request_context():
            g._categories_cache = categories
        data = {cat: [] for cat in categories}

        # Récupère les sites en vedette en une seule requête
        cur.execute(
            """
                SELECT *
                FROM sites
                WHERE status = 'valide' AND en_vedette = 1
                ORDER BY categorie ASC, date_ajout DESC
            """
        )

        for site in cur.fetchall():
            cat = site["categorie"]
            if cat in data and len(data[cat]) < 3:
                data[cat].append(site)

        return data
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des sites en vedette: {e}")
        return {}
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
            SELECT nom, lien, categorie, description, date_ajout
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
def admin_login():
    form = AdminLoginForm()
    next_url = request.args.get("next")
    if not next_url or not next_url.startswith("/"):
        next_url = url_for("admin_dashboard")

    if form.validate_on_submit():
        if verify_admin_credentials(form.username.data, form.password.data):
            session.permanent = True
            session["admin_authenticated"] = True
            session["admin_username"] = form.username.data
            flash("Connexion réussie.", "success")
            return redirect(next_url)
        flash("Identifiants invalides.", "error")

    return render_template("admin/login.html", form=form, next_url=next_url)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    session.pop("admin_username", None)
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

    action_forms = {}
    for site in pending_sites:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
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

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nom, categorie, ville, lien, description, status, date_ajout, en_vedette
            FROM sites
            ORDER BY date_ajout DESC, id DESC
            """
        )
        all_sites = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des sites: {e}")
        flash("Erreur lors du chargement des sites.", "error")
        all_sites = []
    finally:
        conn.close()

    action_forms = {}
    for site in all_sites:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        action_forms[site["id"]] = form

    return render_template(
        "admin/sites.html",
        sites=all_sites,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
    )


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
        categories=categories,
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
    if not form.validate_on_submit():
        app.logger.warning(f"Modération formulaire invalide: {form.errors}")
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        site_id_form = int(form.site_id.data)
    except (TypeError, ValueError):
        abort(400)

    if site_id_form != site_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete", "pending"}:
        flash("Action inconnue.", "error")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()
    if not conn:
        flash("Impossible d'accéder à la base de données.", "error")
        return redirect(url_for("admin_dashboard"))

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

    return redirect(url_for("admin_dashboard"))


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
    posted_category = request.form.get("categorie")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))

    if request.method == "GET":
        form.nom.data = site["nom"]
        form.ville.data = site["ville"]
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
    posted_category = request.form.get("categorie")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))

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
    data = get_sites_en_vedette()
    derniers_sites = get_derniers_sites_global(3)
    # Prépare un formulaire inline (mêmes règles que le formulaire complet)
    form_inline = SiteForm()
    form_inline.categorie.choices = [(cat, cat) for cat in get_categories()]
    form_inline.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    return render_template("index.html", data=data, derniers_sites=derniers_sites, form_inline=form_inline)


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
       ORDER BY en_vedette DESC, date_ajout DESC 
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


@app.route("/nouveaux-sites")
def nouveaux_sites():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()
#recupere tous les sites par ordre descroissant d'ajout
    cur.execute("""
        SELECT nom, lien, categorie, description, date_ajout
        FROM sites
        WHERE status = 'valide'
        ORDER BY date_ajout DESC
    """)
    
    sites = cur.fetchall()
    conn.close()

    return render_template("nouveaux_sites.html", sites=sites)



@app.route("/mentions-legales")
def mentions_legales():
    return render_template("mentions_legales.html")

@app.route('/service-worker.js')
def service_worker():
    response = make_response(send_from_directory('static', 'service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response    


@app.route('/google87e16279463c4021.html')
def google_verification():
    return app.send_static_file('google87e16279463c4021.html')


@app.route("/formulaire", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # SÉCURITÉ : Limite les soumissions de formulaire
def formulaire():
    """SÉCURITÉ : Formulaire avec validation complète"""
    form = SiteForm()
    
    # Charge les catégories dynamiquement pour le SelectField
    form.categorie.choices = [(cat, cat) for cat in get_categories()]
    form.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    
    if form.validate_on_submit():
        nom = form.nom.data
        ville = form.ville.data or None
        lien = form.lien.data
        description = form.description.data
        categorie = form.categorie.data

        if categorie not in get_categories():
            flash("Catégorie non valide.", "error")
            return render_template("formulaire.html", form=form)

        conn = get_db_connection()
        if not conn:
            flash("Erreur technique. Veuillez réessayer plus tard.", "error")
            return render_template("formulaire.html", form=form)
        
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
    
    # Si GET ou formulaire invalide → affiche le formulaire avec erreurs
    return render_template("formulaire.html", form=form)
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

if __name__ == "__main__":
    app.run(debug=True)
