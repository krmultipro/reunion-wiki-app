# -*- coding: utf-8 -*-

import os
from datetime import timedelta

from flask import Flask

from .config import config
from .blueprints import register_blueprints
from .extensions import csrf, limiter
from .http_handlers import register_http_handlers
from .template_helpers import register_template_helpers


# Point d'entrée Flask : ce fichier doit rester centré sur la création de l'app,
# les hooks globaux, les filtres Jinja et l'enregistrement des blueprints.
app = Flask(__name__, static_folder="../static", template_folder="../templates")

# Configuration chargée selon FLASK_ENV. Les setdefault gardent des valeurs sûres
# même si une classe de config oublie une option de session ou de CSRF.
env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config.get(env, config["default"]))
app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(hours=8))
app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
if env == "production":
    app.config.setdefault("SESSION_COOKIE_SECURE", True)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

csrf.init_app(app)

# Flask-Limiter lit sa configuration depuis app.config. On garde le stockage en
# mémoire par défaut pour le dev, et RATELIMIT_STORAGE_URL peut le remplacer en prod.
default_limit = app.config.get("RATELIMIT_DEFAULT")
app.config.setdefault("RATELIMIT_STORAGE_URI", app.config.get("RATELIMIT_STORAGE_URL", "memory://"))
app.config.setdefault("RATELIMIT_STRATEGY", "fixed-window")
if default_limit:
    app.config.setdefault("RATELIMIT_DEFAULT", default_limit)
limiter.init_app(app)

register_template_helpers(app)
register_http_handlers(app)
register_blueprints(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
