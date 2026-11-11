"""Real anonymous submissions and minimal, private moderation screens."""
import secrets
import sqlite3
from urllib.parse import urlsplit
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from ..auth import admin_required
from ..extensions import limiter
from ..forms.refonte_forms import ProposalForm, ProposalAdminForm
from ..repositories import category_repository, city_repository, talent_category_repository, site_repository
from ..repositories import refonte_submission_repository as repository
from ..services import refonte_submission_service as service
from ..services import talent_service, site_publication_service
from ..utils import is_safe_next_url

refonte_submission_bp = Blueprint('refonte_submission',__name__)
STATUS_LABELS = {'pending':'En attente','preparation':'En préparation','refused':'Refusée','published':'Publiée','archived':'Archivée'}


def _choices(form,kind):
    """Load the selected domain's reference categories, never static fixtures."""
    rows = category_repository.get_all_categories() if kind == 'site' else talent_category_repository.list_all()
    form.location.choices = [('', 'Non précisée'),('island','Toute La Réunion'),('online','En ligne')] + [('city:'+str(row['id']),row['nom']) for row in city_repository.get_all_cities()]
    form.category_id.choices = [(0,'Choisir une catégorie')]+[(row['id'],row['nom'] if kind=='site' else row['name']) for row in rows]


def _safe_return():
    """Restore only a same-site queue URL after moderation."""
    value = request.values.get('retour','')
    return value if (is_safe_next_url(value) and urlsplit(value).path == '/admin/refonte' and not any(c in value for c in ('\\','\r','\n'))) else url_for('.admin_index')


@refonte_submission_bp.route('/proposer',methods=['GET','POST'])
@limiter.limit('5 per minute',methods=['POST'],exempt_when=lambda: request.form.get('change_type') == 'yes')
def proposer():
    """Validate, persist and confirm a proposal with no account or automatic publication."""
    form = ProposalForm()
    if request.method == 'GET':
        requested = request.args.get('type','site')
        form.kind.data = 'personality' if requested in ('personality','personnalite','createur') else 'site'
        nonce = secrets.token_urlsafe(24)
        nonces = session.get('proposal_nonces',[])
        session['proposal_nonces'] = (nonces+[nonce])[-12:]
        form.nonce.data = nonce
    changing_type = request.method == 'POST' and request.form.get('change_type') == 'yes'
    type_categories = {kind: request.form.get(kind+'_category_id', '0') for kind in ('site','personality')}
    previous_kind = request.form.get('previous_kind', form.kind.data)
    if request.method == 'POST' and previous_kind in type_categories:
        type_categories[previous_kind] = request.form.get('category_id', '0')
    if changing_type:
        try:
            form.category_id.data = int(type_categories.get(form.kind.data) or 0)
        except (TypeError,ValueError):
            form.category_id.data = 0
    _choices(form,form.kind.data)
    duplicate_href = None
    if not changing_type and form.validate_on_submit():
        if form.nonce.data not in session.get('proposal_nonces',[]):
            form.nonce.errors.append('Le formulaire a expiré. Recharge la page.')
        else:
            try:
                proposal = service.submit(form.data,form.nonce.data)
                confirmations = session.get('proposal_confirmations',[])
                session['proposal_confirmations'] = (confirmations+[proposal['token']])[-12:]
                return redirect(url_for('.confirmation',token=proposal['token']),code=303)
            except service.ProposalError as error:
                form.url.errors.append(str(error))
                if error.public_kind == 'personality':
                    duplicate_href = url_for('creators.creator_detail',slug=error.public_key)
                elif error.public_kind == 'site':
                    duplicate_href = url_for('refonte_public.sites',q=error.public_key)
            except sqlite3.Error:
                current_app.logger.error('Échec de persistance proposition refonte')
                flash('La proposition n’a pas pu être enregistrée. Tes champs sont conservés ; réessaie.','error')
    return render_template('refonte/proposer.html',form=form,duplicate_href=duplicate_href,
                           page_title='Faire une proposition',nav_active='proposer',type_categories=type_categories), 422 if request.method=='POST' and not changing_type else 200


@refonte_submission_bp.route('/proposition-confirmee/<token>')
def confirmation(token):
    """Show a receipt only in the submitting browser, without private input."""
    if token not in session.get('proposal_confirmations',[]):
        abort(404)
    response = current_app.make_response(render_template('refonte/confirmation.html',page_title='Proposition reçue',nav_active='proposer'))
    response.headers['Cache-Control'] = 'private, no-store'
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@refonte_submission_bp.route('/admin/refonte')
@admin_required
def admin_index():
    """List both proposal types for authenticated administrators."""
    status = request.args.get('statut') or None
    if status not in STATUS_LABELS:
        status = None
    items = [service.current_proposal(row) for row in repository.list_all()]
    if status:
        items = [row for row in items if row['status'] == status]
    return render_template('admin/refonte_queue.html',items=items,statuses=STATUS_LABELS,status=status or '',page_title='Propositions')


@refonte_submission_bp.route('/admin/refonte/propositions/<int:proposal_id>',methods=['GET','POST'])
@admin_required
def admin_detail(proposal_id):
    """Edit a proposal and run only explicit, authenticated lifecycle actions."""
    proposal = repository.get(proposal_id)
    if not proposal:
        abort(404)
    proposal = service.current_proposal(proposal)
    form = ProposalAdminForm()
    form.kind.data = proposal['kind']
    _choices(form,proposal['kind'])
    back = _safe_return()
    if request.method == 'GET':
        for field in repository.FIELDS:
            if hasattr(form,field):
                getattr(form,field).data = proposal[field] if proposal[field] is not None else (0 if field=='category_id' else '')
        form.location.data = 'city:'+str(proposal['city_id']) if proposal['city_id'] else (proposal['location_scope'] or '')
    elif form.validate_on_submit():
        try:
            action = form.action.data
            if action == 'reject':
                service.reject(proposal,form.refusal_reason.data,session.get('admin_username','admin'))
            elif action == 'archive':
                if form.confirm.data != 'yes':
                    raise service.ProposalError('Confirme explicitement l’archivage avant de continuer.')
                service.archive(proposal)
            else:
                proposal = service.save_editorial(proposal,form.data)
                if action == 'prepare':
                    service.prepare(proposal)
                elif action == 'publish':
                    if proposal['status'] != 'preparation':
                        raise service.ProposalError('Prépare et enregistre d’abord le brouillon. La publication est une action distincte.')
                    if form.confirm.data != 'yes':
                        raise service.ProposalError('Relis les champs et confirme explicitement la publication.')
                    if proposal['kind'] == 'personality':
                        if not proposal['talent_id']:
                            raise service.ProposalError('Prépare d’abord le brouillon de personnalité.')
                        ok,errors = talent_service.publish(proposal['talent_id'])
                        if not ok:
                            raise service.ProposalError(' '.join(errors))
                    else:
                        row = site_repository.get_site_by_id(proposal['site_id'])
                        result = site_publication_service.review_and_attempt_publication(
                            row['id'],row['lien'],form.editorial_criterion.data,form.private_source_note.data,
                            form.private_source_url.data,session.get('admin_username','admin'))
                        if result.manual_check_id:
                            return redirect(url_for('admin_http_review',site_id=row['id'],check_id=result.manual_check_id))
                        if not result.published:
                            raise service.ProposalError(result.message)
                    repository.set_state(proposal_id,'published')
            flash('Action enregistrée.','success')
            if action in ('reject','archive','publish'):
                return redirect(back,code=303)
            return redirect(url_for('.admin_detail',proposal_id=proposal_id,retour=back),code=303)
        except (service.ProposalError,ValueError) as error:
            flash(str(error),'error')
        except sqlite3.Error:
            current_app.logger.error('Échec action admin refonte proposition_id=%s',proposal_id)
            flash('L’action n’a pas abouti. Recharge la fiche avant de réessayer.','error')
    return render_template('admin/refonte_detail.html',proposal=proposal,form=form,back=back,statuses=STATUS_LABELS,page_title='Examiner la proposition'),422 if request.method=='POST' else 200


@refonte_submission_bp.after_request
def private_headers(response):
    """Prevent indexing or caching private moderation and form responses."""
    response.headers['Cache-Control'] = 'private, no-store'
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response
