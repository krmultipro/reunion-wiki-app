from datetime import datetime
import sqlite3

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from ..extensions import limiter
from ..forms.site_forms import SiteForm
from ..repositories import (
    category_repository,
    city_repository,
    click_repository,
    site_repository,
)
from ..services import refonte_public_service

from ..services import (
    category_service,
    city_service,
    click_service,
    mail_service,
    site_location_service,
    site_service,
    site_url_service,
    talent_service,
)
from ..utils import (
    normalize_search_text,
    slugify,
)


public_bp = Blueprint("public", __name__)


@public_bp.route("/faq")
def faq():
    return render_template("refonte/faq.html", **refonte_public_service.page_context(), page_title="Questions fréquentes")


@public_bp.route("/blog")
def blog():
    return render_template("blog.html")


@public_bp.route("/")
def accueil():
    return render_template("refonte/home.html", **refonte_public_service.home_context(),
                           **refonte_public_service.page_context("home"), page_title="Accueil")



@public_bp.route("/categorie/<slug>")
def voir_categorie(slug):
    category_name = category_service.get_category_name_by_slug(slug)
    if not category_name:
        abort(404)
    canonical_slug = slugify(category_name)
    if slug != canonical_slug:
        return redirect(url_for("voir_categorie", slug=canonical_slug), code=301)
    context = refonte_public_service.list_context("sites", request.args.get("q", ""), canonical_slug)
    return render_template("refonte/list.html", **context, **refonte_public_service.page_context("sites"),
                           page_title=category_name, list_action=url_for("voir_categorie", slug=canonical_slug), category_page=True)


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
    sites = site_service.get_latest_sites()

    return render_template("recently-added-sites.html", sites=sites)



@public_bp.route("/mentions-legales")
def legal_notices():
    return render_template("refonte/legal.html", **refonte_public_service.page_context(), page_title="Mentions légales")


@public_bp.route("/sites-les-plus-visites")
def most_visited_sites():
    sites = site_service.get_top_sites()

    return render_template("most-visited-sites.html", sites=sites)

@public_bp.route("/recherche")
def search():
    return render_template("refonte/search.html", **refonte_public_service.search_context(request.args.get("q", "")),
                           **refonte_public_service.page_context("recherche"), page_title="Résultats")


@public_bp.route("/recherche-sites")
def advanced_site_search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return redirect(url_for("accueil"))

    sort = (request.args.get("sort") or "relevance").strip().lower()
    if sort not in site_repository.SEARCH_SORTS:
        sort = "relevance"

    category_slug = (request.args.get("categorie") or "").strip().lower()
    city_slug = (request.args.get("commune") or "").strip().lower()
    scope_slug = (request.args.get("portee") or "").strip().lower()
    categories = category_repository.get_all_categories()
    cities = city_repository.get_all_cities()

    category = next(
        (row for row in categories if row["slug"] == category_slug),
        None,
    )
    city = next(
        (row for row in cities if row["slug"] == city_slug),
        None,
    )
    category_id = category["id"] if category else (-1 if category_slug else None)
    city_id = city["id"] if city else (-1 if city_slug else None)

    terms = normalize_search_text(q).split()
    sites = site_repository.search_sites(
        terms,
        sort=sort,
        category_id=category_id,
        city_id=city_id,
        scope=scope_slug or None,
    )

    return render_template(
        "search-results.html",
        q=q,
        sites=sites,
        sort=sort,
        categories=categories,
        cities=cities,
        selected_category=category_slug,
        selected_city=city_slug,
        selected_scope=scope_slug,
        selected_scope_name={
            "city": "Avec une commune",
            "island": "Toute La Réunion",
            "online": "En ligne",
            "unspecified": "Non précisée",
        }.get(scope_slug, "Portée inconnue"),
        selected_category_name=(
            category["nom"] if category else "Catégorie inconnue"
        ),
        selected_city_name=(city["nom"] if city else "Commune inconnue"),
        active_filter_count=int(bool(category_slug)) + int(bool(city_slug)) + int(bool(scope_slug)),
    )



@public_bp.route("/proposer-site", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # SÉCURITÉ : Limite les soumissions de formulaire
def website_submission_form():
    """SÉCURITÉ : Formulaire avec validation complète"""
    if request.method == "GET":
        return redirect(url_for("refonte_submission.proposer", type="site"))
    form = SiteForm()
    
    # Charge les catégories dynamiquement pour le SelectField
    form.categorie.choices = [
        (category, category)
        for category in category_service.get_category_names()
    ]
    form.categorie.choices.insert(0, ('', 'Sélectionnez une catégorie'))
    form.ville.choices = city_service.get_name_choices()
    
    if form.validate_on_submit():
        nom = form.nom.data
        ville = form.ville.data or None
        lien = form.lien.data
        description = form.description.data
        categorie = form.categorie.data

        if categorie not in category_service.get_category_names():
            flash("Catégorie non valide.", "error")
            return render_template("website-submission-form.html", form=form)

        try:
            resolved = category_service.resolve_category(categorie)
            if not resolved:
                flash("Catégorie non valide.", "error")
                return render_template("website-submission-form.html", form=form)
            resolved_category_id, resolved_category_name = resolved
            resolved_city = city_service.resolve_city(ville)
            if (ville or "").strip() and not resolved_city:
                flash("Ville non valide.", "error")
                return render_template("website-submission-form.html", form=form)
            resolved_city_id = resolved_city[0] if resolved_city else None
            resolved_city_name = resolved_city[1] if resolved_city else None
            location_scope = site_location_service.validate_location(
                resolved_city_id, form.portee.data
            )

            url_decision = site_url_service.prepare_site_url(lien)
            site_repository.create_site(
                nom,
                resolved_city_id,
                url_decision.normalized_url,
                description,
                resolved_category_id,
                status="en_attente",
                submitted=True,
                location_scope=location_scope,
            )

            mail_service.send_submission_notification({
                "nom": nom,
                "ville": resolved_city_name,
                "lien": url_decision.normalized_url,
                "description": description,
                "categorie": resolved_category_name,
                "date_submission": datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "remote_addr": request.remote_addr or "IP inconnue",
            })
            flash("Ta proposition a été reçue et attend une vérification avant publication.", "success")
            return redirect(url_for("accueil"))
        except site_url_service.DuplicateSiteUrlError:
            form.lien.errors.append("Cette URL correspond déjà à un site enregistré.")
            flash("Ce site est déjà enregistré.", "error")
        except ValueError as e:
            form.portee.errors.append(str(e))
        except sqlite3.Error as e:
            current_app.logger.error(f"Erreur lors de l'insertion du site: {e}")
            flash("Erreur lors de l'enregistrement. Veuillez réessayer.", "error")
    
    # Si GET ou website-submission-form invalide → affiche le formulaire avec erreurs
    return render_template("website-submission-form.html", form=form)
#decorateur, injecte automatiquement variable dans tous les templates Jinja2


@public_bp.route("/villes")
def villes_index():
    villes = city_repository.get_city_stats()

    return render_template("cities.html", villes=villes)


@public_bp.route("/ville/<slug>")
def voir_ville(slug):
    ville = city_repository.get_city_by_slug(slug)
    if not ville:
        return render_template("404.html"), 404

    sites = site_repository.get_sites_by_city_id(ville["id"])
    total_clicks = city_repository.get_total_clicks_by_city_id(ville["id"])["total_clicks"]

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
