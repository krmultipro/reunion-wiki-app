"""Application extensions (Flask-Limiter, etc.)."""

from __future__ import annotations

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Shared limiter instance so blueprints can import and reuse the decorators.
limiter = Limiter(key_func=get_remote_address)


def init_extensions(app: Flask) -> None:
    """Configure third-party extensions with application settings."""
    storage_uri = app.config.get("RATELIMIT_STORAGE_URL")
    if not storage_uri:
        app.config["RATELIMIT_STORAGE_URL"] = "memory://"

    default_limit = app.config.get("RATELIMIT_DEFAULT")
    if default_limit:
        limiter.default_limits = [default_limit]

    limiter.init_app(app)
