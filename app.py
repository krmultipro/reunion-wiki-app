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


@app.route("/")
def accueil():
    data = get_sites_en_vedette()
    return render_template("index.html", data=data)

@app.route("/categorie/<nom_categorie>")
def voir_categorie(nom_categorie):
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
    
    return render_template("categorie.html", nom_categorie=nom_categorie, sites=sites)

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

if __name__ == "__main__":
    app.run(debug=True)