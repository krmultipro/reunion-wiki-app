"""Request/response hooks."""

from __future__ import annotations

from flask import Flask, request


def register_hooks(app: Flask) -> None:
    """Attach global Flask hooks (after_request, etc.)."""

    @app.after_request
    def add_cache_headers(response):  # type: ignore[unused-variable]
        endpoint = (request.endpoint or "").lower()

        if endpoint in {"static", "public.service_worker"}:
            response.headers["Cache-Control"] = "public, max-age=31536000"
        elif endpoint in {"public.accueil", "public.voir_categorie"}:
            response.headers["Cache-Control"] = "public, max-age=300"
        elif endpoint == "public.formulaire":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
