# -*- coding: utf-8 -*-

from flask import Blueprint, abort, render_template

from ..services import talent_service


creators_bp = Blueprint("creators", __name__)


@creators_bp.route("/createurs-reunionnais")
def creators_index():
    """
    Affiche l'index public des talents réunionnais publiés.

    Returns:
        str: Page HTML des créateurs réunionnais.
    """

    context = talent_service.get_public_index_context()
    return render_template("creators/index.html", **context)


@creators_bp.route("/createurs/<slug>")
def creator_detail(slug):
    """
    Affiche la fiche publique d'un talent réunionnais publié.

    Args:
        slug (str): Slug public du talent.

    Returns:
        str: Page HTML de fiche créateur.
    """

    context = talent_service.get_public_talent_detail_context(slug)
    if not context:
        abort(404)
    return render_template("creators/detail.html", **context)
