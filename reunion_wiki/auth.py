# -*- coding: utf-8 -*-

import secrets
from functools import wraps

from flask import current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash


def verify_admin_credentials(username, password):
    """Vérifie les identifiants admin configurés via les variables d'environnement."""
    stored_username = current_app.config.get("ADMIN_USERNAME")
    stored_password = current_app.config.get("ADMIN_PASSWORD")
    stored_hash = current_app.config.get("ADMIN_PASSWORD_HASH")

    if not stored_username:
        current_app.logger.warning("Tentative de connexion admin alors que ADMIN_USERNAME est vide.")
        return False

    if not secrets.compare_digest(username, stored_username):
        return False

    if stored_hash:
        try:
            return check_password_hash(stored_hash, password)
        except ValueError:
            current_app.logger.error("ADMIN_PASSWORD_HASH invalide : utilisez werkzeug.security.generate_password_hash.")
            return False

    if stored_password:
        return secrets.compare_digest(stored_password, password)

    current_app.logger.warning("Tentative de connexion admin sans mot de passe configuré.")
    return False


def admin_required(func):
    """Décorateur de protection des routes admin."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_authenticated"):
            next_url = request.path if request.method == "GET" else url_for("admin_dashboard")
            if not next_url.startswith("/"):
                next_url = url_for("admin_dashboard")
            return redirect(url_for("admin_login", next=next_url))
        return func(*args, **kwargs)

    return wrapper
