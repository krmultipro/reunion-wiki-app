# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for

from ..services import content_service


content_bp = Blueprint("content", __name__)


@content_bp.route("/<slug>")
def show(slug):
    """Affiche une page de contenu publiée.

    Route de repli volontairement peu spécifique : Werkzeug donne la priorité
    aux routes statiques existantes (/faq, /blog, /villes...), donc cette vue
    ne capte que les slugs réellement libres.

    Args:
        slug (str): Slug demandé dans l'URL.

    Returns:
        Réponse HTML de la page, ou 404 si absente/non publiée.
    """

    row = content_service.get_public_page(slug)
    if not row:
        return render_template("404.html"), 404

    seo = content_service.build_seo_context(row)
    canonical = url_for("content.show", slug=row["slug"], _external=True)

    return render_template(
        "content/page.html",
        content=row,
        seo_title=seo["seo_title"],
        seo_description=seo["seo_description"],
        canonical=canonical,
    )
