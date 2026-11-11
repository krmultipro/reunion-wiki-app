"""Consultation publique des personnalités, URLs historiques conservées."""

from flask import Blueprint, abort, render_template, request, url_for
from ..services import refonte_public_service as service

creators_bp = Blueprint("creators", __name__)


@creators_bp.route("/createurs-reunionnais")
def creators_index():
    """Liste les personnalités publiées avec recherche et catégorie."""
    context = service.list_context('profiles', request.args.get('q',''), request.args.get('categorie',''))
    return render_template('refonte/list.html', **context, **service.page_context('personnalites'),
                           page_title='Personnalités réunionnaises', list_action=url_for('creators_index'), category_page=False)


@creators_bp.route("/createurs/<slug>")
def creator_detail(slug):
    """Affiche une fiche publiée ; brouillons et archives restent introuvables."""
    context = service.profile_context(slug)
    if not context:
        abort(404)
    return render_template('refonte/detail.html', **context,
                           **service.page_context('personnalites', url_for('creators_index')),
                           page_title=context['profile']['name'], seo_description=context['profile']['description'])
