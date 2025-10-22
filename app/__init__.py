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
from .forms import (
    AdminLoginForm,
    ModerationActionForm,
    SiteForm,
    TalentProposalForm,
    TalentAdminForm,
    TalentModerationActionForm,
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
from collections import OrderedDict, defaultdict

app = Flask(__name__)

# CONFIGURATION : Chargement selon l'environnement
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

# Configuration de la base de données
DATABASE_PATH = os.path.abspath(app.config['DATABASE_PATH'])

TALENT_CATEGORIES = [
    "Comédiens",
    "Chanteurs",
    "Influenceurs",
    "Célébrités",
]

TALENT_STATUSES = ["en_attente", "valide", "refuse"]

TALENT_STATUS_LABELS = {
    "en_attente": "En attente",
    "valide": "Publié",
    "refuse": "Refusé",
}

DEFAULT_TALENTS = [
    {
        "pseudo": "harendra_h24",
        "instagram": "https://www.instagram.com/harendra_h24/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/harendra.jpg",
    },
    {
        "pseudo": "benj_off",
        "instagram": "https://www.instagram.com/benj_off/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/benji.jpg",
    },
    {
        "pseudo": "titilecomik",
        "instagram": "https://www.instagram.com/titilecomik/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/titilecomik.jpg",
    },
    {
        "pseudo": "monsieur__moustache",
        "instagram": "https://www.instagram.com/monsieur__moustache/",
        "description": "Humoriste réunionnais",
        "category": "Comédiens",
        "image": "talents/monsieur__moustache.jpg",
    },
    {
        "pseudo": "lecouple_en_lu",
        "instagram": "https://www.instagram.com/lecouple_en_lu/reels/",
        "description": "Humoristes réunionnais en duo",
        "category": "Comédiens",
        "image": "talents/lecouple_en_lu.jpg",
    },
    {
        "pseudo": "adriana.ftn_",
        "instagram": "https://www.instagram.com/adriana.ftn_/",
        "description": "Humoriste réunionnaise",
        "category": "Comédiens",
        "image": "talents/adriana.ftn_.jpg",
    },
    {
        "pseudo": "kafmalbarofficiel",
        "instagram": "https://www.instagram.com/kafmalbarofficiel/",
        "description": "Chanteur réunionnais",
        "category": "Chanteurs",
        "image": "talents/kafmalbarofficiel.jpg",
    },
    {
        "pseudo": "pll_off",
        "instagram": "https://www.instagram.com/pll_off/",
        "description": "Groupe de chanteurs réunionnais",
        "category": "Chanteurs",
        "image": "talents/pll_off.jpg",
    },
    {
        "pseudo": "segaelofficiel",
        "instagram": "https://www.instagram.com/segaelofficiel/",
        "description": "Chanteuse réunionnaise",
        "category": "Chanteurs",
        "image": "talents/segaelofficiel.jpg",
    },
    {
        "pseudo": "jennie.leonie",
        "instagram": "https://www.instagram.com/jennie.leonie/",
        "description": "Influenceuse réunionnaise",
        "category": "Influenceurs",
        "image": "talents/jennie.leonie.jpg",
    },
    {
        "pseudo": "fanm.kreol",
        "instagram": "https://www.instagram.com/fanm.kreol/",
        "description": "Influenceuse réunionnaise",
        "category": "Influenceurs",
        "image": "talents/fanm.kreol.jpg",
    },
    {
        "pseudo": "dronecopters_974",
        "instagram": "https://www.instagram.com/dronecopters_974/",
        "description": "Influenceur réunionnais",
        "category": "Influenceurs",
        "image": "talents/dronecopters_974.jpg",
    },
    {
        "pseudo": "priyapadavatanoff",
        "instagram": "https://www.instagram.com/priyapadavatanoff/",
        "description": "Miss Réunion 2025",
        "category": "Célébrités",
        "image": "talents/priyapadavatanoff.jpg",
    },
    {
        "pseudo": "manupayet",
        "instagram": "https://www.instagram.com/manupayet/",
        "description": "Acteur réunionnais",
        "category": "Célébrités",
        "image": "talents/manupayet.jpg",
    },
]

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
def get_sites_en_vedette(limit=3):
    """Récupère les derniers sites valides par catégorie (sans filtre en_vedette)."""
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
        raw_categories = [row["categorie"] for row in cur.fetchall() if row["categorie"]]
        if has_request_context():
            g._categories_cache = raw_categories
        data = {cat: [] for cat in raw_categories}

        cur.execute(
            """
                SELECT *
                FROM sites
                WHERE status = 'valide'
                ORDER BY categorie ASC, date_ajout DESC
            """
        )

        for site in cur.fetchall():
            cat = site["categorie"]
            if cat in data and len(data[cat]) < limit:
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
    """Récupère les différentes catégories ayant au moins un site valide"""
    if has_request_context() and hasattr(g, "_categories_cache"):
        return g._categories_cache

    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
        results = cur.fetchall()
        # Pour chaque row dans results prends la première colonne (row[0]) si row[0] n'est pas vide
        categories = [row[0] for row in results if row[0]]
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
    status_filter = request.args.get("status", "en_attente")
    search_query = request.args.get("q", "").strip()
    allowed_statuses = {"en_attente", "valide", "refuse", "tout"}
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("accueil"))

    try:
        cur = conn.cursor()
        params = []
        query_clause = ""

        if search_query and len(search_query) >= 2:
            like_query = f"%{search_query}%"
            query_clause = """AND (
                    nom LIKE ? COLLATE NOCASE
                    OR categorie LIKE ? COLLATE NOCASE
                    OR description LIKE ? COLLATE NOCASE
                    OR IFNULL(ville, '') LIKE ? COLLATE NOCASE
                    OR lien LIKE ? COLLATE NOCASE
                )"""
            params.extend([like_query] * 5)

        status_clause = ""
        if status_filter != "tout":
            status_clause = "AND status = ?"
            params.append(status_filter)

        cur.execute(
            f"""
            SELECT id, nom, categorie, ville, lien, description, status, date_ajout
            FROM sites
            WHERE 1 = 1
            {status_clause}
            {query_clause}
            ORDER BY
                CASE WHEN status = 'en_attente' THEN 0 ELSE 1 END,
                date_ajout DESC,
                id DESC
            LIMIT 200
            """,
            tuple(params),
        )
        entries = cur.fetchall()

        cur.execute(
            "SELECT status, COUNT(*) as total FROM sites GROUP BY status"
        )
        stats_rows = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des propositions: {e}")
        flash("Erreur lors de la récupération des propositions.", "error")
        entries = []
        stats_rows = []
    finally:
        conn.close()

    stats = {row["status"]: row["total"] for row in stats_rows}
    stats["tout"] = sum(stats.values())

    action_forms = {}
    for site in entries:
        form = ModerationActionForm()
        form.site_id.data = str(site["id"])
        action_forms[site["id"]] = form

    return render_template(
        "admin/dashboard.html",
        entries=entries,
        stats=stats,
        status_filter=status_filter,
        search_query=search_query,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
    )


@app.route("/admin/propositions/<int:site_id>", methods=["POST"])
@admin_required
def admin_update_site(site_id):
    form = ModerationActionForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        site_id_form = int(form.site_id.data)
    except (TypeError, ValueError):
        abort(400)

    if site_id_form != site_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete"}:
        flash("Action inconnue.", "error")
        return redirect(url_for("admin_dashboard"))

    status_redirect = request.form.get("status_filter", "en_attente")
    query_redirect = request.form.get("search_query", "")

    conn = get_db_connection()
    if not conn:
        flash("Impossible d'accéder à la base de données.", "error")
        return redirect(url_for("admin_dashboard", status=status_redirect, q=query_redirect))

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

    return redirect(url_for("admin_dashboard", status=status_redirect, q=query_redirect))


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
            SELECT id, nom, categorie, ville, lien, description, status
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

    form = SiteForm()
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
        if site["categorie"] not in categories_list:
            form.categorie.choices.append((site["categorie"], site["categorie"]))
        form.categorie.data = site["categorie"]
    elif form.validate_on_submit():
        conn_to_update = get_db_connection()
        if not conn_to_update:
            flash("Impossible de se connecter à la base de données.", "error")
            conn.close()
            return redirect(url_for("admin_dashboard", status=request.args.get("status", "en_attente"), q=request.args.get("q", "")))
        try:
            cur_update = conn_to_update.cursor()
            cur_update.execute(
                """
                UPDATE sites
                SET nom = ?, ville = ?, lien = ?, description = ?, categorie = ?
                WHERE id = ?
                """,
                (
                    form.nom.data,
                    form.ville.data or None,
                    form.lien.data,
                    form.description.data,
                    form.categorie.data,
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
        form_action=url_for("admin_edit_site", site_id=site_id, status=request.args.get("status"), q=request.args.get("q")),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier la proposition #{site_id}",
        subtitle=f"Statut actuel : <strong>{site['status']}</strong>",
        status_filter=request.args.get("status", "en_attente"),
        search_query=request.args.get("q", ""),
    )


@app.route("/admin/propositions/new", methods=["GET", "POST"])
@admin_required
def admin_create_site():
    form = SiteForm()
    form.honeypot.data = ""
    categories_list = get_categories()
    form.categorie.choices = [(cat, cat) for cat in categories_list]
    form.categorie.choices.insert(0, ("", "Sélectionnez une catégorie"))
    posted_category = request.form.get("categorie")
    if posted_category and posted_category not in [choice[0] for choice in form.categorie.choices]:
        form.categorie.choices.append((posted_category, posted_category))

    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_dashboard", status="valide"))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout, en_vedette)
                VALUES (?, ?, ?, ?, ?, 'valide', DATETIME('now'), 0)
                """,
                (
                    form.nom.data,
                    form.ville.data or None,
                    form.lien.data,
                    form.description.data,
                    form.categorie.data,
                ),
            )
            conn.commit()
            flash("Nouveau site ajouté et publié.", "success")
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
        status_filter="valide",
        search_query="",
    )

@app.route("/")
def accueil():
    data = get_sites_en_vedette()
    derniers_sites = get_derniers_sites_global(12)
    talents_home = get_talents_data()
    # Prépare un formulaire inline (mêmes règles que le formulaire complet)
    form_inline = SiteForm()
    form_inline.categorie.choices = [(cat, cat) for cat in get_categories()]
    form_inline.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    return render_template(
        "index.html",
        data=data,
        derniers_sites=derniers_sites,
        talents=talents_home,
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



@app.route("/recherche")
def search():
    query = request.args.get("q", "").strip()
    results = []
    total = 0

    if query and len(query) >= 2:
        conn = get_db_connection()
        if not conn:
            flash("Impossible d'accéder à la base de données pour la recherche.", "error")
            return render_template(
                "search.html",
                query=query,
                results=[],
                total=0,
            )
        try:
            cur = conn.cursor()
            like_query = f"%{query}%"
            cur.execute(
                """
                SELECT id, nom, categorie, ville, lien, description, date_ajout
                FROM sites
                WHERE status = 'valide'
                  AND (
                        nom LIKE ? COLLATE NOCASE
                        OR categorie LIKE ? COLLATE NOCASE
                        OR description LIKE ? COLLATE NOCASE
                        OR IFNULL(ville, '') LIKE ? COLLATE NOCASE
                        OR lien LIKE ? COLLATE NOCASE
                  )
                ORDER BY en_vedette DESC, date_ajout DESC
                LIMIT 100
                """,
                (like_query, like_query, like_query, like_query, like_query),
            )
            results = cur.fetchall()
            total = len(results)
        except sqlite3.Error as e:
            app.logger.error(f"Erreur lors de la recherche '{query}': {e}")
            flash("Erreur lors de la recherche.", "error")
        finally:
            conn.close()

    elif query:
        flash("Tape au moins 2 caractères pour lancer la recherche.", "error")

    return render_template(
        "search.html",
        query=query,
        results=results,
        total=total,
    )

@app.route("/blog")
def blog():
    cats = get_categories()
    cats_slug = get_categories_slug()
    return render_template("blog.html", categories=cats, categories_slug=cats_slug)


@app.route("/talents", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def talents():
    form = TalentProposalForm()
    if form.validate_on_submit():
        success = create_talent_proposal(
            form.pseudo.data,
            form.instagram.data,
            form.description.data,
        )
        if success:
            flash("Merci ! Ta proposition de talent est en attente de validation.", "success")
            return redirect(url_for("talents"))
        flash("Erreur lors de l'enregistrement de ta proposition. Réessaie plus tard.", "error")
    talents_by_category = get_talents_data()
    return render_template("talents.html", talents=talents_by_category, form=form)


@app.route("/mentions-legales")
def mentions_legales():
    return render_template("mentions_legales.html")


@app.route("/contact")
def contact():
    contact_channels = [
        {
            "title": "Email",
            "value": "reunionwiki974@gmail.com",
            "action": "mailto:reunionwiki974@gmail.com",
            "label": "Envoyer un email",
        },
        {
            "title": "Formulaire",
            "value": "Formulaire Google",
            "action": "https://forms.gle/GScJkMiEZXVSted78",
            "label": "Proposer une idée",
        },
        {
            "title": "Instagram",
            "value": "@kery.rdd",
            "action": "https://www.instagram.com/kery.rdd",
            "label": "Suivre le projet",
        },
    ]

    support_blocks = [
        {
            "title": "Besoin d'aide rapide ?",
            "description": "Consulte la FAQ.",
            "link": url_for("faq"),
            "label": "Voir la FAQ",
        },
        {
            "title": "Tu veux contribuer ?",
            "description": "Propose un site directement via le formulaire dédié ou contacte moi pour des données supplémentaires.",
            "link": url_for("formulaire"),
            "label": "Proposer un site",
        },
    ]

    return render_template(
        "contact.html",
        contact_channels=contact_channels,
        support_blocks=support_blocks,
    )

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
    # >>> AJOUT : garantit que les slugs affichés dans les menus/lien sont bien en ASCII canonique
    categories_slug = {cat: slugify(cat) for cat in categories}

    if has_request_context():
        g._categories_slug_cache = categories_slug
    return categories_slug


def ensure_talents_table():
    """Crée la table des talents si nécessaire."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS talents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                instagram TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT '',
                image TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'en_attente',
                date_created TEXT NOT NULL DEFAULT (DATETIME('now')),
                date_updated TEXT NOT NULL DEFAULT (DATETIME('now'))
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_talents_status ON talents(status)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_talents_category ON talents(category)"
        )
        conn.commit()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la création de la table talents: {e}")
    finally:
        if conn:
            conn.close()


def seed_default_talents():
    """Insère les talents par défaut si la table est vide."""
    ensure_talents_table()
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM talents")
        row = cur.fetchone()
        total = row[0] if row else 0
        if total == 0:
            cur.executemany(
                """
                INSERT INTO talents (pseudo, instagram, description, category, image, status)
                VALUES (?, ?, ?, ?, ?, 'valide')
                """,
                [
                    (
                        talent["pseudo"],
                        talent["instagram"],
                        talent["description"],
                        talent["category"],
                        talent.get("image", ""),
                    )
                    for talent in DEFAULT_TALENTS
                ],
            )
            conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de l'initialisation des talents: {e}")
    finally:
        conn.close()


def prepare_talents_storage():
    """Prépare la table et les données de talents."""
    ensure_talents_table()
    seed_default_talents()


def create_talent_proposal(pseudo, instagram, description):
    """Ajoute une proposition de talent en base."""
    ensure_talents_table()
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO talents (pseudo, instagram, description, status)
            VALUES (?, ?, ?, 'en_attente')
            """,
            (pseudo, instagram, description),
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de l'enregistrement d'un talent: {e}")
        return False
    finally:
        conn.close()

def get_talent_category_choices(current=None):
    """Retourne les choix de catégories pour les formulaires."""
    base_choices = [("", "Sélectionnez une catégorie")]
    for category in TALENT_CATEGORIES:
        base_choices.append((category, category))
    if current and current not in TALENT_CATEGORIES:
        base_choices.append((current, current))
    return base_choices


def get_talent_status_choices():
    """Retourne les choix de statuts localisés."""
    return [(code, TALENT_STATUS_LABELS.get(code, code)) for code in TALENT_STATUSES]


def get_talents_data():
    """Retourne les talents validés regroupés par catégorie pour les pages publiques."""
    prepare_talents_storage()
    conn = get_db_connection()
    if not conn:
        return OrderedDict()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, pseudo, instagram, description, category, image
            FROM talents
            WHERE status = 'valide'
            ORDER BY LOWER(pseudo)
            """
        )
        rows = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des talents: {e}")
        return OrderedDict()
    finally:
        conn.close()

    grouped = defaultdict(list)
    for row in rows:
        category = row["category"] or "Autres talents"
        grouped[category].append(
            {
                "id": row["id"],
                "name": row["pseudo"],
                "instagram": row["instagram"],
                "tagline": row["description"],
                "image": row["image"] or "",
            }
        )

    ordered = OrderedDict()
    for category in TALENT_CATEGORIES:
        if grouped.get(category):
            ordered[category] = grouped.pop(category)

    for category in sorted(grouped.keys()):
        ordered[category] = grouped[category]

    return ordered


@app.route("/admin/talents", methods=["GET"])
@admin_required
def admin_talents():
    prepare_talents_storage()
    status_filter = request.args.get("status", "en_attente")
    allowed_statuses = set(TALENT_STATUSES + ["tout"])
    if status_filter not in allowed_statuses:
        status_filter = "en_attente"

    search_query = request.args.get("q", "").strip()

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        cur = conn.cursor()
        params = []
        query = """
            SELECT id, pseudo, instagram, description, category, image, status, date_created, date_updated
            FROM talents
            WHERE 1 = 1
        """

        if status_filter != "tout":
            query += " AND status = ?"
            params.append(status_filter)

        if search_query and len(search_query) >= 2:
            like_query = f"%{search_query}%"
            query += """
                AND (
                    pseudo LIKE ? COLLATE NOCASE
                    OR instagram LIKE ? COLLATE NOCASE
                    OR description LIKE ? COLLATE NOCASE
                    OR IFNULL(category, '') LIKE ? COLLATE NOCASE
                )
            """
            params.extend([like_query] * 4)

        query += """
            ORDER BY
                CASE status
                    WHEN 'en_attente' THEN 0
                    WHEN 'valide' THEN 1
                    ELSE 2
                END,
                date_updated DESC,
                id DESC
            LIMIT 200
        """

        cur.execute(query, tuple(params))
        entries = cur.fetchall()

        cur.execute("SELECT status, COUNT(*) AS total FROM talents GROUP BY status")
        stats_rows = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération des talents admin: {e}")
        flash("Erreur lors de la récupération des talents.", "error")
        entries = []
        stats_rows = []
    finally:
        conn.close()

    stats = {row["status"]: row["total"] for row in stats_rows}
    stats["tout"] = sum(stats.values())

    action_forms = {}
    for talent in entries:
        form = TalentModerationActionForm()
        form.talent_id.data = str(talent["id"])
        action_forms[talent["id"]] = form

    return render_template(
        "admin/talents.html",
        entries=entries,
        stats=stats,
        status_filter=status_filter,
        search_query=search_query,
        action_forms=action_forms,
        admin_username=session.get("admin_username"),
        status_labels=TALENT_STATUS_LABELS,
    )


@app.route("/admin/talents/<int:talent_id>", methods=["POST"])
@admin_required
def admin_update_talent(talent_id):
    prepare_talents_storage()
    form = TalentModerationActionForm()
    if not form.validate_on_submit():
        flash("Formulaire invalide.", "error")
        return redirect(url_for("admin_talents"))

    try:
        talent_id_form = int(form.talent_id.data)
    except (TypeError, ValueError):
        abort(400)

    if talent_id_form != talent_id:
        abort(400)

    action = request.form.get("action")
    if action not in {"approve", "reject", "delete"}:
        flash("Action inconnue.", "error")
        return redirect(url_for("admin_talents"))

    status_redirect = request.form.get("status_filter", "en_attente")
    query_redirect = request.form.get("search_query", "").strip()
    allowed_statuses = set(TALENT_STATUSES + ["tout"])
    if status_redirect not in allowed_statuses:
        status_redirect = "en_attente"

    conn = get_db_connection()
    if not conn:
        flash("Impossible d'accéder à la base de données.", "error")
        return redirect(url_for("admin_talents", status=status_redirect, q=query_redirect))

    message = ""
    try:
        cur = conn.cursor()
        if action == "approve":
            cur.execute(
                "UPDATE talents SET status = 'valide', date_updated = DATETIME('now') WHERE id = ?",
                (talent_id,),
            )
            message = "Talent publié."
        elif action == "reject":
            cur.execute(
                "UPDATE talents SET status = 'refuse', date_updated = DATETIME('now') WHERE id = ?",
                (talent_id,),
            )
            message = "Talent refusé."
        else:
            cur.execute("DELETE FROM talents WHERE id = ?", (talent_id,))
            message = "Talent supprimé."

        if cur.rowcount == 0:
            flash("Talent introuvable.", "error")
            conn.rollback()
        else:
            conn.commit()
            flash(message, "success")
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Erreur lors de la mise à jour du talent {talent_id}: {e}")
        flash("Erreur lors de la mise à jour du talent.", "error")
    finally:
        conn.close()

    return redirect(url_for("admin_talents", status=status_redirect, q=query_redirect))


@app.route("/admin/talents/<int:talent_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_talent(talent_id):
    prepare_talents_storage()
    status_filter = request.args.get("status", "en_attente")
    search_query = request.args.get("q", "").strip()

    form = TalentAdminForm()
    form.category.choices = get_talent_category_choices()
    form.status.choices = get_talent_status_choices()

    conn = get_db_connection()
    if not conn:
        flash("Impossible de se connecter à la base de données.", "error")
        return redirect(url_for("admin_talents", status=status_filter, q=search_query))

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, pseudo, instagram, description, category, image, status
            FROM talents
            WHERE id = ?
            """,
            (talent_id,),
        )
        row = cur.fetchone()
    except sqlite3.Error as e:
        app.logger.error(f"Erreur lors de la récupération du talent {talent_id}: {e}")
        flash("Erreur lors de la récupération du talent.", "error")
        conn.close()
        return redirect(url_for("admin_talents", status=status_filter, q=search_query))

    if not row:
        conn.close()
        flash("Talent introuvable.", "error")
        return redirect(url_for("admin_talents", status=status_filter, q=search_query))

    talent = dict(row)
    conn.close()

    form.category.choices = get_talent_category_choices(talent.get("category"))
    form.status.choices = get_talent_status_choices()

    if request.method == "GET":
        form.pseudo.data = talent["pseudo"]
        form.instagram.data = talent["instagram"]
        form.description.data = talent["description"]
        form.category.data = talent["category"] or ""
        form.image.data = talent["image"] or ""
        form.status.data = talent["status"]

    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_talents", status=status_filter, q=search_query))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE talents
                SET pseudo = ?, instagram = ?, description = ?, category = ?, image = ?, status = ?, date_updated = DATETIME('now')
                WHERE id = ?
                """,
                (
                    form.pseudo.data,
                    form.instagram.data,
                    form.description.data,
                    form.category.data or "",
                    form.image.data or "",
                    form.status.data,
                    talent_id,
                ),
            )
            if cur.rowcount == 0:
                flash("Aucune mise à jour n'a été effectuée.", "warning")
                conn.rollback()
            else:
                conn.commit()
                flash("Talent mis à jour.", "success")
                return redirect(url_for("admin_talents", status=status_filter, q=search_query))
        except sqlite3.Error as e:
            conn.rollback()
            app.logger.error(f"Erreur lors de la mise à jour du talent {talent_id}: {e}")
            flash("Erreur lors de la mise à jour du talent.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_talent.html",
        form=form,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_edit_talent", talent_id=talent_id, status=status_filter, q=search_query),
        submit_label="Enregistrer les modifications",
        page_title=f"Modifier le talent #{talent_id}",
        subtitle=f"Statut actuel : <strong>{TALENT_STATUS_LABELS.get(talent['status'], talent['status'])}</strong>",
        status_filter=status_filter,
        search_query=search_query,
    )


@app.route("/admin/talents/new", methods=["GET", "POST"])
@admin_required
def admin_create_talent():
    prepare_talents_storage()
    form = TalentAdminForm()
    form.category.choices = get_talent_category_choices()
    form.status.choices = get_talent_status_choices()

    if form.validate_on_submit():
        conn = get_db_connection()
        if not conn:
            flash("Impossible de se connecter à la base de données.", "error")
            return redirect(url_for("admin_talents"))
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO talents (pseudo, instagram, description, category, image, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    form.pseudo.data,
                    form.instagram.data,
                    form.description.data,
                    form.category.data or "",
                    form.image.data or "",
                    form.status.data,
                ),
            )
            conn.commit()
            flash("Talent ajouté.", "success")
            target_status = form.status.data if form.status.data in TALENT_STATUSES else "en_attente"
            return redirect(url_for("admin_talents", status=target_status))
        except sqlite3.Error as e:
            conn.rollback()
            app.logger.error(f"Erreur lors de l'ajout d'un talent depuis l'admin: {e}")
            flash("Erreur lors de l'ajout du talent.", "error")
        finally:
            conn.close()

    return render_template(
        "admin/edit_talent.html",
        form=form,
        admin_username=session.get("admin_username"),
        form_action=url_for("admin_create_talent"),
        submit_label="Enregistrer le talent",
        page_title="Ajouter un talent",
        subtitle="Renseigne les informations du talent Instagram.",
        status_filter="en_attente",
        search_query="",
    )

if __name__ == "__main__":
    app.run(debug=True)
