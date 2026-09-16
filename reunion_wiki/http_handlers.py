# -*- coding: utf-8 -*-

"""Gestion globale des erreurs et des en-têtes HTTP de l'application."""

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError


def page_not_found(_error):
    """Page 404 commune à toute l'app, routes publiques comme admin."""
    return render_template("404.html"), 404


def internal_server_error(error):
    """Log l'erreur serveur puis affiche la page 500 personnalisée."""
    current_app.logger.error(f"Erreur serveur: {error}")
    return render_template("500.html"), 500


def handle_csrf_error(error):
    """Retour utilisateur propre quand un formulaire expire ou échoue au CSRF."""
    current_app.logger.warning(f"CSRF bloqué: {error.description}")
    flash("Session expirée ou formulaire invalide. Réessaie.", "error")
    return redirect(request.referrer or url_for("accueil"))


def add_cache_headers(response):
    """Ajoute des headers de cache et de sécurité communs."""
    # Le service worker ne doit jamais rester coincé en cache navigateur.
    if request.endpoint == "service_worker":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    elif request.endpoint in {"static", "uploaded_file"}:
        response.headers["Cache-Control"] = "public, max-age=31536000"
    elif request.endpoint in {"accueil", "voir_categorie"}:
        # Les pages publiques peuvent être légèrement cachées sans figer les données.
        response.headers["Cache-Control"] = "public, max-age=300"
    elif request.endpoint == "website_submission_form":
        # Les formulaires gardent toujours une réponse fraîche pour éviter les CSRF expirés.
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    # Défense HTTP de base, complétée côté nginx pour la CSP en production.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def register_http_handlers(app):
    """Enregistre les handlers d'erreurs et le hook HTTP global."""
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(CSRFError, handle_csrf_error)
    app.after_request(add_cache_headers)
