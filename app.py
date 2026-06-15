# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFError

from auth import admin_required, verify_admin_credentials
from config import config
from db import get_db_connection, init_db_schema
from extensions import csrf, limiter
from forms import AdminLogoutForm
from mail import send_submission_notification
from queries import get_derniers_sites_global, get_sites_en_vedette, get_top_sites
from taxonomy import (
    generate_unique_category_slug,
    get_categories,
    get_categories_slug,
    get_city_choices,
    get_nom_categorie_depuis_slug,
    resolve_category,
    resolve_city,
)
from utils import get_client_ip, is_safe_next_url, mask_ip, parse_positive_int, slugify, slugify_ville


app = Flask(__name__)

ICON_MAP = {
    "culture-et-loisirs": "map.svg",
    "actualites": "newspaper.svg",
    "achats": "shopping-cart.svg",
    "transport": "bus.svg",
    "emploi-et-formation": "briefcase.svg",
    "meteo-et-alertes": "cloud-rain.svg",
    "administratifs": "file-text.svg",
    "nourriture": "utensils.svg",
    "sante": "heart.svg",
}


env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config.get(env, config["default"]))
app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(hours=8))
app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
if env == "production":
    app.config.setdefault("SESSION_COOKIE_SECURE", True)

csrf.init_app(app)

default_limit = app.config.get("RATELIMIT_DEFAULT")
app.config.setdefault("RATELIMIT_STORAGE_URI", app.config.get("RATELIMIT_STORAGE_URL", "memory://"))
app.config.setdefault("RATELIMIT_STRATEGY", "fixed-window")
if default_limit:
    app.config.setdefault("RATELIMIT_DEFAULT", default_limit)
limiter.init_app(app)


@app.context_processor
def asset_versioning():
    def asset_v(path):
        full = os.path.join(app.static_folder, path)
        try:
            return int(os.path.getmtime(full))
        except OSError:
            return 1

    return {"asset_v": asset_v}


@app.context_processor
def inject_admin_logout_form():
    if session.get("admin_authenticated"):
        return {"admin_logout_form": AdminLogoutForm()}
    return {}


@app.context_processor
def inject_categories():
    return {
        "categories": get_categories(),
        "categories_slug": get_categories_slug(),
        "ICON_MAP": ICON_MAP,
    }


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erreur serveur: {e}")
    return render_template("500.html"), 500


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.warning(f"CSRF bloqué: {e.description}")
    flash("Session expirée ou formulaire invalide. Réessaie.", "error")
    return redirect(request.referrer or url_for("accueil"))


@app.after_request
def add_cache_headers(response):
    """Ajoute des headers de cache et de sécurité communs."""
    if request.endpoint == "service_worker":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    elif request.endpoint == "static":
        response.headers["Cache-Control"] = "public, max-age=31536000"
    elif request.endpoint in ["accueil", "voir_categorie"]:
        response.headers["Cache-Control"] = "public, max-age=300"
    elif request.endpoint == "website_submission_form":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


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


app.jinja_env.filters["format_date"] = format_date


@app.template_filter("month_name")
def month_name(date_value):
    if isinstance(date_value, str):
        dt = datetime.fromisoformat(date_value)
    else:
        dt = date_value

    mois_fr = [
        "JAN",
        "FÉV",
        "MAR",
        "AVR",
        "MAI",
        "JUN",
        "JUI",
        "AOÛ",
        "SEP",
        "OCT",
        "NOV",
        "DÉC",
    ]
    return mois_fr[dt.month - 1]


def register_legacy_blueprint_endpoints(bp_name, endpoint_names):
    """Keep pre-blueprint endpoint names available for existing url_for calls."""
    for endpoint_name in endpoint_names:
        blueprint_endpoint = f"{bp_name}.{endpoint_name}"
        if blueprint_endpoint not in app.view_functions:
            continue

        app.view_functions[endpoint_name] = app.view_functions.pop(blueprint_endpoint)
        rules = app.url_map._rules_by_endpoint.pop(blueprint_endpoint, [])
        for rule in rules:
            rule.endpoint = endpoint_name
        app.url_map._rules_by_endpoint.setdefault(endpoint_name, []).extend(rules)


from routes.admin import admin_bp
from routes.public import public_bp
from routes.seo import seo_bp

app.register_blueprint(admin_bp)
app.register_blueprint(public_bp)
app.register_blueprint(seo_bp)

register_legacy_blueprint_endpoints(
    "admin",
    [
        "admin_login",
        "admin_logout",
        "admin_dashboard",
        "admin_sites",
        "admin_clicks",
        "admin_delete_click",
        "admin_categories",
        "admin_create_category",
        "admin_edit_category",
        "admin_delete_category",
        "admin_update_site",
        "admin_edit_site",
        "admin_create_site",
    ],
)
register_legacy_blueprint_endpoints(
    "public",
    [
        "faq",
        "blog",
        "accueil",
        "voir_categorie",
        "redirect_site",
        "recently_added_sites",
        "legal_notices",
        "most_visited_sites",
        "search",
        "website_submission_form",
        "villes_index",
        "voir_ville",
        "most_visited_categories",
        "trends",
    ],
)
register_legacy_blueprint_endpoints(
    "seo",
    [
        "service_worker",
        "google_verification",
        "robots_txt",
        "sitemap",
    ],
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
