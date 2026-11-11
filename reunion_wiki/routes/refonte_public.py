"""Entrées publiques complémentaires de la refonte, sans mutation."""

from flask import Blueprint, render_template, request, url_for

from ..services import refonte_public_service as service

refonte_public_bp = Blueprint('refonte_public', __name__)


@refonte_public_bp.route('/sites')
def sites():
    """Affiche l'annuaire réel des sites publiés avec ses critères URL."""
    context = service.list_context('sites', request.args.get('q', ''), request.args.get('categorie', ''))
    return render_template('refonte/list.html', **context, **service.page_context('sites'),
                           page_title='Sites réunionnais', list_action=url_for('refonte_public.sites'), category_page=False)


@refonte_public_bp.route('/contact')
def contact():
    """Explique le canal externe existant sans simuler une réception."""
    return render_template('refonte/contact.html', **service.page_context(), page_title='Contact')
