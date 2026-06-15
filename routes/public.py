from datetime import datetime
import sqlite3

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from extensions import limiter
from forms import SiteForm
from db import get_db_connection
from mail import send_submission_notification
from queries import get_derniers_sites_global, get_sites_en_vedette, get_top_sites
from taxonomy import (
    get_categories,
    get_city_choices,
    get_nom_categorie_depuis_slug,
    resolve_category,
    resolve_city,
)
from utils import (
    get_client_ip,
    slugify,
)


public_bp = Blueprint("public", __name__)


@public_bp.route("/faq")
def faq():
    return render_template("faq.html")


@public_bp.route("/blog")
def blog():
    return render_template("blog.html")


@public_bp.route("/")
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



@public_bp.route("/categorie/<slug>")
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
    cur.execute("SELECT id FROM categories WHERE nom = ?", (nom_categorie,))
    category_row = cur.fetchone()
    category_id = category_row["id"] if category_row else None

    # Règle d'affichage catégorie: vedettes d'abord, puis popularité.
    cur.execute("""
       SELECT s.*, c.nom AS categorie, v.nom AS ville
       FROM sites s
       JOIN categories c ON c.id = s.category_id
       LEFT JOIN villes v ON v.id = s.ville_id
       WHERE s.status = 'valide'
         AND s.category_id = ?
       ORDER BY en_vedette DESC, click_count DESC, date_ajout DESC, id DESC 
    """, (category_id,))
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


@public_bp.route("/go/<int:site_id>")
def redirect_site(site_id):
    current_app.logger.info(f"[GO] Tentative de redirection pour site_id={site_id}")

    conn = get_db_connection()
    if not conn:
        current_app.logger.error("[GO] Connexion DB impossible")
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
            current_app.logger.warning(f"[GO] Site introuvable ou non valide id={site_id}")
            abort(404)

        current_app.logger.info(
            f"[GO] Site trouvé id={site_id} | ancien compteur={row['click_count']} | url={row['lien']}"
        )
        
        ip = get_client_ip()
        user_agent = (request.headers.get("User-Agent", "") or "")[:400]
        
        # Anti-bot simple
        ua_lower = user_agent.lower()
        if "bot" in ua_lower or "crawl" in ua_lower or "spider" in ua_lower:
            current_app.logger.info(f"[GO] Bot détecté, clic ignoré id={site_id} ua={user_agent}")
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

            current_app.logger.info(f"[GO] Clic validé id={site_id} ip={ip}")
        else:
            current_app.logger.info(f"[GO] Clic ignoré (trop récent) id={site_id} ip={ip}")

        return redirect(row["lien"])

    except sqlite3.Error as e:
        current_app.logger.error(f"[GO] Erreur SQLite site_id={site_id} | {e}")
        abort(500)

    finally:
        conn.close()
        current_app.logger.info(f"[GO] Connexion DB fermée pour site_id={site_id}")



@public_bp.route("/sites-ajoutes-recemment")
def recently_added_sites():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
    cur = conn.cursor()
#recupere tous les sites par ordre descroissant d'ajout
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
    """)
    
    sites = cur.fetchall()
    conn.close()

    return render_template("recently-added-sites.html", sites=sites)



@public_bp.route("/mentions-legales")
def legal_notices():
    return render_template("legal-notices.html")


@public_bp.route("/sites-les-plus-visites")
def most_visited_sites():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500
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
    """)
    sites = cur.fetchall()
    conn.close()

    return render_template("most-visited-sites.html", sites=sites)

@public_bp.route("/recherche")
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
        SELECT
            s.id,
            s.nom,
            s.lien,
            v.nom AS ville,
            c.nom AS categorie,
            s.description,
            s.click_count,
            s.date_ajout
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
        WHERE s.status = 'valide'
          AND (
            s.nom LIKE ?
            OR COALESCE(c.nom, '') LIKE ?
            OR s.description LIKE ?
            OR s.lien LIKE ?
            OR COALESCE(v.nom, '') LIKE ?
            OR LOWER(REPLACE(COALESCE(v.nom, ''), '-', ' ')) LIKE ?
          )
        ORDER BY
          CASE
            WHEN s.nom LIKE ? THEN 0
            WHEN COALESCE(c.nom, '') LIKE ? THEN 1
            WHEN s.description LIKE ? THEN 2
            WHEN COALESCE(v.nom, '') LIKE ? OR LOWER(REPLACE(COALESCE(v.nom, ''), '-', ' ')) LIKE ? THEN 3
            WHEN s.lien LIKE ? THEN 4
            ELSE 5
          END,
          s.click_count DESC,
          s.date_ajout DESC
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


@public_bp.route("/proposer-site", methods=["GET", "POST"])
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
            resolved = resolve_category(cur, categorie)
            if not resolved:
                flash("Catégorie non valide.", "error")
                return render_template("website-submission-form.html", form=form)
            resolved_category_id, resolved_category_name = resolved
            resolved_city = resolve_city(cur, ville)
            if (ville or "").strip() and not resolved_city:
                flash("Ville non valide.", "error")
                return render_template("website-submission-form.html", form=form)
            resolved_city_id = resolved_city[0] if resolved_city else None
            resolved_city_name = resolved_city[1] if resolved_city else None

            # SÉCURITÉ : Insertion avec paramètres liés (protection contre SQL injection)
            cur.execute("""
                INSERT INTO sites (nom, ville_id, lien, description, category_id, status, date_ajout)
                VALUES (?, ?, ?, ?, ?, 'en_attente', DATETIME('now'))
            """, (
                nom,
                resolved_city_id,
                lien,
                description,
                resolved_category_id
            ))
            
            conn.commit()
            send_submission_notification({
                "nom": nom,
                "ville": resolved_city_name,
                "lien": lien,
                "description": description,
                "categorie": resolved_category_name,
                "date_submission": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "remote_addr": request.remote_addr or "IP inconnue",
            })
            flash("Merci, ta proposition a bien été envoyée ! Elle sera validée prochainement.", "success")
            return redirect(url_for("accueil"))
            
        except sqlite3.Error as e:
            current_app.logger.error(f"Erreur lors de l'insertion du site: {e}")
            flash("Erreur lors de l'enregistrement. Veuillez réessayer.", "error")
        finally:
            conn.close()
    
    # Si GET ou website-submission-form invalide → affiche le formulaire avec erreurs
    return render_template("website-submission-form.html", form=form)
#decorateur, injecte automatiquement variable dans tous les templates Jinja2


@public_bp.route("/villes")
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


@public_bp.route("/ville/<slug>")
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
        SELECT s.*, c.nom AS categorie, v.nom AS ville
        FROM sites s
        LEFT JOIN categories c ON c.id = s.category_id
        LEFT JOIN villes v ON v.id = s.ville_id
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



@public_bp.route("/categories-les-plus-visitees")
def most_visited_categories():
    conn = get_db_connection()
    if not conn:
        return render_template("500.html"), 500

    try:
        cur = conn.cursor()
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
        categories_rank = cur.fetchall()
        return render_template("most-visited-categories.html", categories_rank=categories_rank)
    finally:
        conn.close()

@public_bp.route("/tendances")
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
                c.nom AS categorie,
                COALESCE(c7.c7, 0) AS clicks_7d,
                COALESCE(cp.cprev, 0) AS clicks_prev_7d,
                CASE
                    WHEN COALESCE(cp.cprev, 0) = 0 THEN NULL
                    ELSE ROUND((COALESCE(c7.c7, 0) - cp.cprev) * 100.0 / cp.cprev, 1)
                END AS growth_pct
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
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
                c.nom AS categorie,
                COUNT(sc.id) AS clicks_30d
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
            LEFT JOIN site_clicks sc
              ON sc.site_id = s.id
             AND sc.clicked_at >= datetime('now', '-30 days')
            WHERE s.status = 'valide'
            GROUP BY s.id, s.nom, c.nom
            ORDER BY clicks_30d DESC
            LIMIT 10
            """
        )
        stable_sites = cur.fetchall()

        # Catégories en hausse (7j vs 7j précédents)
        cur.execute(
            """
            WITH c7 AS (
                SELECT c.nom AS categorie, COUNT(sc.id) AS clicks_7d
                FROM sites s
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN site_clicks sc
                  ON sc.site_id = s.id
                 AND sc.clicked_at >= datetime('now', '-7 days')
                WHERE s.status = 'valide'
                  AND c.nom IS NOT NULL
                  AND TRIM(c.nom) != ''
                GROUP BY c.nom
            ),
            cp AS (
                SELECT c.nom AS categorie, COUNT(sc.id) AS clicks_prev_7d
                FROM sites s
                LEFT JOIN categories c ON c.id = s.category_id
                LEFT JOIN site_clicks sc
                  ON sc.site_id = s.id
                 AND sc.clicked_at >= datetime('now', '-14 days')
                 AND sc.clicked_at < datetime('now', '-7 days')
                WHERE s.status = 'valide'
                  AND c.nom IS NOT NULL
                  AND TRIM(c.nom) != ''
                GROUP BY c.nom
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
                c.nom AS categorie,
                COUNT(sc.id) AS clicks_7d
            FROM sites s
            LEFT JOIN categories c ON c.id = s.category_id
            LEFT JOIN site_clicks sc
              ON sc.site_id = s.id
             AND sc.clicked_at >= datetime('now', '-7 days')
            WHERE s.status = 'valide'
              AND s.date_ajout >= datetime('now', '-30 days')
            GROUP BY s.id, s.nom, c.nom
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
