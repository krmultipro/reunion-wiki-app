"""Admin authentication helpers."""

from __future__ import annotations

import secrets
from functools import wraps
from typing import Any, Callable, TypeVar

from flask import current_app, redirect, request, session, url_for
from werkzeug.security import check_password_hash

F = TypeVar("F", bound=Callable[..., Any])


def verify_admin_credentials(username: str, password: str) -> bool:
    """Validate admin credentials against configured secrets."""
    app = current_app
    stored_username = app.config.get("ADMIN_USERNAME")
    stored_password = app.config.get("ADMIN_PASSWORD")
    stored_hash = app.config.get("ADMIN_PASSWORD_HASH")

    if not stored_username:
        app.logger.warning(
            "Tentative de connexion admin alors que ADMIN_USERNAME est vide."
        )
        return False

    if not secrets.compare_digest(username, stored_username):
        return False

    if stored_hash:
        try:
            return check_password_hash(stored_hash, password)
        except ValueError:
            app.logger.error(
                "ADMIN_PASSWORD_HASH invalide : utilisez werkzeug.security.generate_password_hash."
            )
            return False

    if stored_password:
        return secrets.compare_digest(stored_password, password)

    app.logger.warning(
        "Tentative de connexion admin sans mot de passe configuré."
    )
    return False


def admin_required(func: F) -> F:
    """Protect admin routes by ensuring the session is authenticated."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        if not session.get("admin_authenticated"):
            next_url = request.path if request.method == "GET" else url_for("admin.dashboard")
            if not next_url.startswith("/"):
                next_url = url_for("admin.dashboard")
            return redirect(url_for("admin.login", next=next_url))
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
