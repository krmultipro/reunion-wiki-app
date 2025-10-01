# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, send_from_directory, request, flash, url_for, redirect
from datetime import datetime
import sqlite3

# >>> AJOUT : imports utilitaires pour un slug ASCII propre (sans emojis/accents)
import re
import unicodedata

app = Flask(__name__)

app.secret_key = "b85364b2a18a969a63390e2f3377d2b5"

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


#Recupere les sites pre selectionnes pour etre affiches
def get_sites_en_vedette():
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    #recupere les differentes categories dont au moins un site a le statut valide
    cur.execute("""SELECT DISTINCT categorie 
                FROM sites 
                WHERE status = 'valide'
                """)
    categories = cur.fetchall()
    
    #recupere sites de chaque categorie avec le statut valide et dans la limite de 3 et return la dictionnaire data pour la page index
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
    
    conn.close()
    return data

#recupere les derniers site dans la limite de 3
def get_derniers_sites_global(limit=3):
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

#recupere les derniers sites ajoutes par date d'ajout pour la page index
    cur.execute("""
        SELECT nom, lien, categorie, description, date_ajout
        FROM sites
        WHERE status = 'valide'
        ORDER BY date_ajout DESC
        LIMIT ?
    """, (limit,))

    derniers_sites = cur.fetchall()
    conn.close()
    return derniers_sites


#recupere les differentes categories ayant au moins un site valide
def get_categories():
    conn = sqlite3.connect('base.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
    results = cur.fetchall()
    conn.close()
    #pour chaque row dans results prends la premiere colonne (row[0]) si row[0] n'est pas vide
    return [row[0] for row in results if row[0]]

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
    conn = sqlite3.connect('base.db')
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

    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
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
def formulaire():
    if request.method == "POST":
        nom = request.form["nom"]
        ville = request.form["ville"]
        lien = request.form["lien"]
        description = request.form["description"]
        categorie = request.form["categorie"]

        # Connexion à SQLite
        conn = sqlite3.connect('base.db')
        cur = conn.cursor()

        # Insertion avec status "en attente"
        cur.execute("""
            INSERT INTO sites (nom, ville, lien, description, categorie, status, date_ajout)
            VALUES (?, ?, ?, ?, ?, 'en_attente', DATETIME('now'))
        """, (nom, ville, lien, description, categorie))

        conn.commit()
        conn.close()

        flash("Merci, ta proposition a bien été envoyée ! Elle sera validée prochainement.")
        return redirect(url_for("accueil"))

    # Si GET → on affiche juste le formulaire
    return render_template("formulaire.html")
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
