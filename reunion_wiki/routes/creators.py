# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

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
