# -*- coding: utf-8 -*-
from flask import Flask, render_template, make_response, send_from_directory
import sqlite3

app = Flask(__name__)

def get_sites_en_vedette():
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
    categories = cur.fetchall()
    
    data = {}
    for cat in categories:
        nom_cat = cat["categorie"]
        cur.execute("""
           SELECT * FROM sites
           WHERE categorie = ? AND status = 'valide' AND en_vedette = 1
           ORDER BY date_ajout DESC
           LIMIT 3         
            
        """, (nom_cat,))
        data[nom_cat] = cur.fetchall()
    
    conn.close()
    return data

def get_derniers_sites_global(limit=3):
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT nom, lien, categorie, description
        FROM sites
        WHERE status = 'valide'
        ORDER BY date_ajout DESC
        LIMIT ?
    """, (limit,))

    derniers_sites = cur.fetchall()
    conn.close()
    return derniers_sites

def get_categories():
    conn = sqlite3.connect('base.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT categorie FROM sites WHERE status = 'valide'")
    results = cur.fetchall()
    conn.close()
    return [row[0] for row in results if row[0]]

def slugify(nom):
    return nom.lower().replace(" ", "-").replace("&", "et")

def get_nom_categorie_depuis_slug(slug):
    conn = sqlite3.connect('base.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT categorie FROM sites WHERE status='valide'")
    toutes = [row[0] for row in cur.fetchall()]
    conn.close()
    for cat in toutes:
        if slugify(cat) == slug:
            return cat
    return None

@app.route("/categorie/<slug>")
def voir_categorie(slug):
    nom_categorie = get_nom_categorie_depuis_slug(slug)
    if not nom_categorie:
        return render_template("404.html"), 404

    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
       SELECT * FROM sites
       WHERE categorie = ? AND status = 'valide'
       ORDER BY en_vedette DESC, date_ajout DESC 
    """, (nom_categorie,))
    sites = cur.fetchall()
    conn.close()

    return render_template(
        "categorie.html",
        nom_categorie=nom_categorie,
        sites=sites
    )


@app.route("/nouveaux-sites")
def nouveaux_sites():
    conn = sqlite3.connect('base.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT nom, lien, categorie, description, date_ajout
        FROM sites
        WHERE status = 'valide'
        ORDER BY date_ajout DESC
    """)
    
    sites = cur.fetchall()
    conn.close()

    return render_template("nouveaux_sites.html", sites=sites)

@app.route("/")
def accueil():
    data = get_sites_en_vedette()
    derniers_sites = get_derniers_sites_global(3)
    return render_template("index.html", data=data, derniers_sites=derniers_sites)




@app.route("/mentions-legales")
def mentions_legales():
    return render_template("mentions_legales.html")

@app.route('/service-worker.js')
def service_worker():
    response = make_response(send_from_directory('static', 'service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response    


@app.route('/googlee4ac9f96a74612c3.html')
def google_verification():
    return app.send_static_file('googlee4ac9f96a74612c3.html')

@app.context_processor
def inject_categories():
    return {
        "categories": get_categories(),
        "categories_slug": get_categories_slug()
    }


def get_categories_slug():
    categories = get_categories()
    return {cat: slugify(cat) for cat in categories}

if __name__ == "__main__":
    app.run(debug=True)