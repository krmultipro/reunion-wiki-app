# -*- coding: utf-8 -*-

"""Enregistrement centralisé des blueprints et de leurs endpoints historiques."""

from .routes.admin import admin_bp
from .routes.admin_content import admin_content_bp
from .routes.admin_talent_categories import admin_talent_categories_bp
from .routes.admin_talents import admin_talents_bp
from .routes.content import content_bp
from .routes.creators import creators_bp
from .routes.public import public_bp
from .routes.seo import seo_bp


LEGACY_ENDPOINTS = {
    "admin": (
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
    ),
    "public": (
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
    ),
    "creators": ("creators_index",),
    "seo": (
        "service_worker",
        "google_verification",
        "robots_txt",
        "sitemap",
        "uploaded_file",
    ),
}


def register_legacy_blueprint_endpoints(app, blueprint_name, endpoint_names):
    """Garde les anciens noms d'endpoints après migration vers blueprints.

    Sans ce pont, Flask nommerait par exemple les routes ``public.accueil``.
    Les templates et routes existants utilisent encore ``url_for("accueil")``.
    """
    for endpoint_name in endpoint_names:
        blueprint_endpoint = f"{blueprint_name}.{endpoint_name}"
        if blueprint_endpoint not in app.view_functions:
            continue

        app.view_functions[endpoint_name] = app.view_functions.pop(blueprint_endpoint)
        rules = app.url_map._rules_by_endpoint.pop(blueprint_endpoint, [])
        for rule in rules:
            rule.endpoint = endpoint_name
        app.url_map._rules_by_endpoint.setdefault(endpoint_name, []).extend(rules)


def register_blueprints(app):
    """Enregistre les routes dans l'ordre requis puis restaure leurs anciens noms."""
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_content_bp)
    app.register_blueprint(admin_talent_categories_bp)
    app.register_blueprint(admin_talents_bp)
    app.register_blueprint(creators_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(seo_bp)

    # content_bp expose la route de repli /<slug> : elle reste enregistrée en
    # dernier afin d'être moins prioritaire que les routes publiques explicites.
    app.register_blueprint(content_bp)

    for blueprint_name, endpoint_names in LEGACY_ENDPOINTS.items():
        register_legacy_blueprint_endpoints(app, blueprint_name, endpoint_names)
