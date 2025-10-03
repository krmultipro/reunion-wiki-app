# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, send_from_directory, request, flash, url_for, redirect
from datetime import datetime
import sqlite3
import os
from forms import SiteForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

# >>> AJOUT : imports utilitaires pour un slug ASCII propre (sans emojis/accents)
import re
import unicodedata

app = Flask(__name__)

# CONFIGURATION : Chargement selon l'environnement
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

# Configuration de la base de données
DATABASE_PATH = app.config['DATABASE_PATH']

# SÉCURITÉ : Rate limiting pour éviter le spam
limiter = Limiter(
    key_func=get_remote_address,
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
    
    # SÉCURITÉ : CSP et HSTS uniquement en production
    if env == 'production':
        # CSP minimale; ajustable selon besoins (PWA, analytics, etc.)
        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self' data:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers['Content-Security-Policy'] = csp
        # HSTS (uniquement si HTTPS configuré côté serveur)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
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
        cur.execute("""SELECT DISTINCT categorie 
                    FROM sites 
                    WHERE status = 'valide'
                    """)
        categories = cur.fetchall()
        
        # Récupère sites de chaque catégorie avec le statut valide et dans la limite de 3
        data = {}
        for cat in categories:
            nom_cat = cat["categorie"]
            cur.execute("""
                SELECT * 
                FROM sites
                WHERE categorie = ? AND status = 'valide' AND en_vedette = 1
                ORDER BY date_ajout DESC
                LIMIT 3         
            """, (nom_cat,))
            data[nom_cat] = cur.fetchall()
        
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
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
        results = cur.fetchall()
        # Pour chaque row dans results prends la première colonne (row[0]) si row[0] n'est pas vide
        return [row[0] for row in results if row[0]]
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
    conn = get_db_connection()
    if not conn:
        return None
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT categorie FROM sites WHERE status='valide'")
    toutes = [row[0] for row in cur.fetchall()]
    conn.close()
    #si le slug du cat correspond au slug alors on retourne le cat, donc non sluggé
    for cat in toutes:
        if slugify(cat) == slug:
            return cat
    return None

@app.route("/")
def accueil():
    data = get_sites_en_vedette()
    derniers_sites = get_derniers_sites_global(3)
    return render_template("index.html", data=data, derniers_sites=derniers_sites)


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

    #return sur le html
    return render_template(
        "categorie.html",
        nom_categorie=nom_categorie,
        sites=sites,
        # >>> AJOUT SEO : passe les variables au template
        slug=canonical_slug,
        seo_title=seo_title,
        seo_description=seo_description,
        canonical=canonical
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
                form.nom.data.strip(),
                form.ville.data.strip() if form.ville.data else None,
                form.lien.data.strip(),
                form.description.data.strip(),
                form.categorie.data
            ))
            
            conn.commit()
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
    categories = get_categories()
    # >>> AJOUT : garantit que les slugs affichés dans les menus/lien sont bien en ASCII canonique
    return {cat: slugify(cat) for cat in categories}

if __name__ == "__main__":
    app.run(debug=True)
