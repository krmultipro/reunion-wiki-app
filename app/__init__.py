# -*- coding: utf-8 -*-
"""Application factory for Réunion Wiki."""

from __future__ import annotations

import os

from flask import Flask

from config import config

from .errors import register_error_handlers
from .extensions import init_extensions
from .filters import init_app as init_filters
from .hooks import register_hooks
from .routes.admin import admin_bp
from .routes.public import public_bp
from .services.sites import get_categories, get_categories_slug


def apply_security_settings(app: Flask, env: str) -> None:
    """Harden session/cookie settings while respecting explicit overrides."""
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("REMEMBER_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    if env == "production":
        app.config.setdefault("SESSION_COOKIE_SECURE", True)
        app.config.setdefault("REMEMBER_COOKIE_SECURE", True)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config.get(env, config["default"]))

    apply_security_settings(app, env)
    init_extensions(app)
    init_filters(app)
    register_hooks(app)
    register_error_handlers(app)
    register_blueprints(app)
    register_context_processors(app)

    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)


def register_context_processors(app: Flask) -> None:
    @app.context_processor
    def inject_categories():
        return {
            "categories": get_categories(),
            "categories_slug": get_categories_slug(),
        }


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
