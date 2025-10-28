"""Application error handlers."""

from __future__ import annotations

from flask import Flask, current_app, render_template


def register_error_handlers(app: Flask) -> None:
    """Register 404/500 handlers with logging."""

    @app.errorhandler(404)
    def page_not_found(error):  # type: ignore[unused-variable]
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):  # type: ignore[unused-variable]
        current_app.logger.error(f"Erreur serveur: {error}")
        return render_template("500.html"), 500
