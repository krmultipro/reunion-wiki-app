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
from forms import AdminLoginForm, ModerationActionForm, SiteForm
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

    action = form.action.data
    if action not in {"approve", "reject", "delete"}:
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
    # >>> AJOUT : garantit que les slugs affichés dans les menus/lien sont bien en ASCII canonique
    categories_slug = {cat: slugify(cat) for cat in categories}

    if has_request_context():
        g._categories_slug_cache = categories_slug
    return categories_slug

if __name__ == "__main__":
    app.run(debug=True)
