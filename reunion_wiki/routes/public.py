from datetime import datetime
import sqlite3

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from ..db import get_db_connection
from ..extensions import limiter
from ..forms.site_forms import SiteForm
from ..mail import send_submission_notification
from ..queries import get_derniers_sites_global, get_sites_en_vedette, get_top_sites
from ..repositories import category_repository, click_repository, site_repository
from ..services import click_service, talent_service
from ..taxonomy import (
    get_categories,
    get_city_choices,
    get_nom_categorie_depuis_slug,
    resolve_category,
    resolve_city,
)
from ..utils import (
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
    youtube_guide = talent_service.get_public_social_guide("youtube")
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
        youtube_guide=youtube_guide,
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

    category_row = category_repository.get_category_by_name(nom_categorie)
    category_id = category_row["id"] if category_row else None
    sites = site_repository.get_sites_by_category_id(category_id)

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
    try:
        result = click_service.handle_click(site_id, request.headers)
        if not result.found:
            abort(404)
        return redirect(result.url)
    except sqlite3.Error as e:
        current_app.logger.error(f"[GO] Erreur SQLite site_id={site_id} | {e}")
        abort(500)

    finally:
        current_app.logger.info(f"[GO] Connexion DB fermée pour site_id={site_id}")



@public_bp.route("/sites-ajoutes-recemment")
def recently_added_sites():
    sites = site_repository.get_latest_sites()

    return render_template("recently-added-sites.html", sites=sites)



@public_bp.route("/mentions-legales")
def legal_notices():
    return render_template("legal-notices.html")


@public_bp.route("/sites-les-plus-visites")
def most_visited_sites():
    sites = site_repository.get_top_sites()

    return render_template("most-visited-sites.html", sites=sites)

@public_bp.route("/recherche")
def search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return redirect(url_for("accueil"))

    like = f"%{q}%"

    # Normalisation "saint-denis" <-> "saint denis"
    q_city = " ".join(q.lower().replace("-", " ").split())
    like_city = f"%{q_city}%"
    sites = site_repository.search_sites(like, like_city)

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

            conn.commit()
            site_repository.create_site(
                nom,
                resolved_city_id,
                lien,
                description,
                resolved_category_id,
                status="en_attente",
            )

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
    villes = site_repository.get_city_stats()

    return render_template("cities.html", villes=villes)


@public_bp.route("/ville/<slug>")
def voir_ville(slug):
    ville = site_repository.get_city_by_slug(slug)
    if not ville:
        return render_template("404.html"), 404

    sites = site_repository.get_sites_by_city_id(ville["id"])
    total_clicks = site_repository.get_total_clicks_by_city_id(ville["id"])["total_clicks"]

    return render_template("city.html", ville=ville, sites=sites, total_clicks=total_clicks)



@public_bp.route("/categories-les-plus-visitees")
def most_visited_categories():
    categories_rank = category_repository.get_categories_rank()
    return render_template("most-visited-categories.html", categories_rank=categories_rank)

@public_bp.route("/tendances")
def trends():
    trending_sites = click_repository.get_trending_sites()
    stable_sites = click_repository.get_stable_sites()
    trending_categories = category_repository.get_trending_categories()
    new_performers = site_repository.get_new_performers()

    return render_template(
        "trends.html",
        trending_sites=trending_sites,
        stable_sites=stable_sites,
        trending_categories=trending_categories,
        new_performers=new_performers,
    )
