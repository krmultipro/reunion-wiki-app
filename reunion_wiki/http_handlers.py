# -*- coding: utf-8 -*-

"""Gestion globale des erreurs et des en-têtes HTTP de l'application."""

from flask import current_app, flash, g, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError
from .utils import is_safe_next_url


def page_not_found(_error):
    """Page 404 commune à toute l'app, routes publiques comme admin."""
    g.skip_navigation_queries = True
    return render_template("refonte/error.html", page_title="Page introuvable",
                           message="Cette page n’est pas disponible. Retrouve les contenus publiés depuis les annuaires."), 404


def internal_server_error(error):
    """Log l'erreur serveur puis affiche la page 500 personnalisée."""
    current_app.logger.error(f"Erreur serveur: {error}")
    g.skip_navigation_queries = True
    return render_template("refonte/error.html", page_title="Une erreur est survenue",
                           message="Le contenu n’a pas pu être chargé. Réessaie dans un instant."), 500


def handle_csrf_error(error):
    """Retour utilisateur propre quand un formulaire expire ou échoue au CSRF."""
    current_app.logger.warning(f"CSRF bloqué: {error.description}")
    flash("Session expirée ou formulaire invalide. Réessaie.", "error")
    target = request.form.get("return_to", "")
    return redirect(target if is_safe_next_url(target) else url_for("accueil"))


def add_cache_headers(response):
    """Ajoute des headers de cache et de sécurité communs."""
    # Le service worker ne doit jamais rester coincé en cache navigateur.
    if request.path.startswith(("/admin", "/proposer", "/proposition-confirmee")) or request.cookies.get("session"):
        response.headers["Cache-Control"] = "private, no-store, max-age=0"
    elif request.endpoint == "service_worker":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    elif request.endpoint == "uploaded_file":
        response.headers["Cache-Control"] = "private, no-store, max-age=0"
    elif request.endpoint == "static":
        response.headers["Cache-Control"] = "public, max-age=31536000"
    elif request.endpoint in {"accueil", "voir_categorie"}:
        # Les pages publiques peuvent être légèrement cachées sans figer les données.
        response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
    elif request.endpoint == "website_submission_form":
        # Les formulaires gardent toujours une réponse fraîche pour éviter les CSRF expirés.
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    # Défense HTTP de base, complétée côté nginx pour la CSP en production.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if response.mimetype == "text/html" and "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
    if request.host.split(":")[0].lower() == "dev.reunionwiki.re":
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response


def register_http_handlers(app):
    """Enregistre les handlers d'erreurs et le hook HTTP global."""
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(CSRFError, handle_csrf_error)
    app.after_request(add_cache_headers)
