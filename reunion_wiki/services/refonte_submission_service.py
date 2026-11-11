"""Anonymous proposals and explicit, authenticated moderation orchestration."""
import json
import re
import secrets
import sqlite3
from urllib.parse import parse_qsl, urlencode, urlsplit
from ..repositories import category_repository, city_repository, talent_category_repository, talent_repository, site_repository
from ..repositories import refonte_submission_repository as repository
from ..repositories.site_refusal_repository import validate_reason
from . import site_url_service, site_lifecycle_service, site_location_service, talent_service
from .site_data_validation import publication_data_error


class ProposalError(ValueError):
    """A safe public error with an optional link to already-public content."""
    def __init__(self, message, public_kind=None, public_key=None):
        super().__init__(message)
        self.public_kind, self.public_key = public_kind, public_key


def official_url(value):
    """Canonicalize only transport identity and known tracking, preserving profile paths."""
    value = (value or '').strip()
    if '://' not in value:
        value = 'https://' + value
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in ('http','https') or not parts.hostname or parts.username or parts.password or any(c.isspace() for c in value):
            raise ValueError()
        port = parts.port
    except ValueError as error:
        raise ProposalError('Indique une URL HTTP ou HTTPS valide.') from error
    host = parts.hostname.lower()
    if ':' in host:
        host = '['+host+']'
    if port and (parts.scheme.lower(),port) not in (('http',80),('https',443)):
        host += ':'+str(port)
    query = [(k,v) for k,v in parse_qsl(parts.query,keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in {'fbclid','gclid','igsh'}]
    # Case-sensitive identifiers and functional parameters are deliberately retained.
    path = parts.path.rstrip('/')
    url = parts.scheme.lower()+'://'+host+path+('?' + urlencode(query) if query else '')
    key = json.dumps([host,path,query],ensure_ascii=False,separators=(',',':'))
    return url,key



def reference_url(value):
    """Validate a source link without discarding its functional fragment or parameters."""
    official_url(value)
    cleaned = value.strip()
    if '://' not in cleaned:
        cleaned = 'https://' + cleaned
    if len(cleaned) > 255:
        raise ProposalError('Le lien de source dépasse la longueur autorisée.')
    return cleaned


def clean_data(raw, kind=None, admin=False):
    """Validate the service boundary independently of WTForms and normalize values."""
    data = {field: (raw.get(field) or '').strip() if isinstance(raw.get(field) or '',str) else raw.get(field)
            for field in repository.FIELDS}
    data['kind'] = kind or raw.get('kind')
    if data['kind'] not in ('site','personality'):
        raise ProposalError('Choisis Site ou Personnalité.')
    if not 2 <= len(data['name']) <= 100:
        raise ProposalError('Le nom doit faire entre 2 et 100 caractères.')
    if len(data['url']) > 255 or len(data['description']) > 500 or len(data['email']) > 254:
        raise ProposalError('Un champ dépasse la longueur autorisée.')
    for key,limit in [('reunion_attachment',1000),('private_source_reference',500),('private_source_url',255),('private_source_note',1000)]:
        if len(data[key]) > limit:
            raise ProposalError('Un champ privé dépasse la longueur autorisée.')
    if data['email'] and not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+',data['email']):
        raise ProposalError('Indique un email valide.')
    try:
        data['category_id'] = int(data['category_id'] or 0) or None
    except (TypeError,ValueError) as error:
        raise ProposalError('Catégorie invalide.') from error
    if data['kind'] == 'site':
        official_url(data['url'])  # Reject credentials/schemes before the shared site normalizer.
        data['url'] = site_url_service.normalize_site_url(data['url'])
        issue = publication_data_error({'nom':data['name'],'lien':data['url'],'description':data['description']})
        if issue:
            raise ProposalError(issue)
        if not data['category_id'] or not category_repository.get_category_by_id(data['category_id']):
            raise ProposalError('Choisis une catégorie existante.')
        data['url_key'] = json.dumps(site_url_service.comparison_key(data['url']),separators=(',',':'))
    else:
        data['url'],data['url_key'] = official_url(data['url'])
        if data['category_id'] and not talent_category_repository.get_by_id(data['category_id']):
            raise ProposalError('Choisis une catégorie existante.')
    if len(data['url']) > 255:
        raise ProposalError('Le lien dépasse la longueur autorisée.')
    location = raw.get('location')
    data['city_id'] = None
    data['location_scope'] = None
    if location:
        if location in ('island','online'):
            data['location_scope'] = site_location_service.validate_location(None,location)
        elif isinstance(location,str) and location.startswith('city:'):
            try:
                city_id = int(location[5:])
            except ValueError as error:
                raise ProposalError('Commune invalide.') from error
            city = city_repository.get_city_by_id(city_id)
            if not city:
                raise ProposalError('Choisis une commune existante.')
            data['city_id'] = city_id
        else:
            raise ProposalError('Localisation invalide.')
    if len(data['supplied_evidence_url']) > 255:
        raise ProposalError('Le lien de preuve est trop long.')
    if data['supplied_evidence_url']:
        data['supplied_evidence_url'] = reference_url(data['supplied_evidence_url'])
    if data['private_source_url']:
        data['private_source_url'] = reference_url(data['private_source_url'])
    if not admin:
        for key in ('private_source_reference','private_source_url','private_source_note'):
            data[key] = ''
    return data


def duplicate(data, exclude_proposal_id=None, exclude_talent_id=None, exclude_site_id=None):
    """Identify a duplicate while revealing a destination only when already public."""
    if data['kind'] == 'site':
        decision = site_url_service.assess_site_url(data['url'],exclude_site_id=exclude_site_id)
        if decision.duplicate_site_id:
            row = site_repository.get_site_by_id(decision.duplicate_site_id)
            if row['status'] == 'valide':
                return ProposalError('Ce site est déjà référencé.', 'site', row['nom'])
            return ProposalError('Ce site est déjà enregistré.')
    else:
        for row in repository.list_talent_urls():
            if row['id'] == exclude_talent_id:
                continue
            for field in talent_service.URL_FIELDS:
                if row[field]:
                    try:
                        _,key = official_url(row[field])
                    except ProposalError:
                        continue
                    if key == data['url_key']:
                        if row['status'] == 'published':
                            return ProposalError('Ce profil est déjà référencé.','personality',row['slug'])
                        return ProposalError('Ce profil est déjà enregistré.')
    if repository.find_duplicate(data['kind'],data['url_key'],exclude_proposal_id=exclude_proposal_id):
        return ProposalError('Ce profil est déjà enregistré.' if data['kind']=='personality' else 'Ce site est déjà enregistré.')
    return None


def submit(raw, nonce):
    """Persist one proposal and, for a site, its pending record atomically."""
    existing = repository.get_by_nonce(nonce)
    if existing:
        return existing
    if not isinstance(nonce,str) or not 20 <= len(nonce) <= 100:
        raise ProposalError('Le formulaire a expiré. Recharge la page.')
    data = clean_data(raw)
    error = duplicate(data)
    if error:
        raise error
    token = secrets.token_urlsafe(24)
    try:
        with site_repository.site_write_transaction() as connection:
            site_id = None
            if data['kind'] == 'site':
                # Reuse the existing transaction-level URL guard, not a new comparator.
                site_repository._assert_url_available(connection,data['url'])
                site_id = repository.insert_pending_site(connection,data)
            proposal_id = repository.insert(connection,data,token,nonce,site_id)
    except (sqlite3.IntegrityError,site_url_service.DuplicateSiteUrlError) as error:
        existing = repository.get_by_nonce(nonce)
        if existing:
            return existing
        raise ProposalError('Ce profil est déjà enregistré.' if data['kind']=='personality' else 'Ce site est déjà enregistré.') from error
    return repository.get(proposal_id)


def save_editorial(proposal, raw):
    """Save corrections in the proposal and its linked private/public content."""
    if proposal['status'] in ('refused','archived'):
        raise ProposalError('Cette demande est clôturée.')
    data = clean_data(raw,kind=proposal['kind'],admin=True)
    error = duplicate(data,exclude_proposal_id=proposal['id'],exclude_talent_id=proposal['talent_id'],exclude_site_id=proposal['site_id'])
    if error:
        raise error
    if proposal['site_id']:
        row = repository.get_site_record(proposal['site_id'])
        if not row:
            raise ProposalError('Le site associé est introuvable.')
        if row['status'] == 'valide' and data['url'] != row['lien']:
            raise ProposalError('Archive le site avant de modifier son lien.')
        site_url_service.prepare_site_url(data['url'],exclude_site_id=row['id'])
        if not site_repository.update_site(row['id'],data['name'],data['city_id'],data['url'],data['description'],data['category_id'],row['status'],row['en_vedette'],expected_status=row['status'],location_scope=data['location_scope']):
            raise ProposalError('Le site a changé. Recharge la fiche.')
    if proposal['talent_id']:
        save_talent(proposal,data)
    repository.update(proposal['id'],data)
    return repository.get(proposal['id'])


def save_talent(proposal, data):
    """Prepare or correct a personality via the existing guarded talent service."""
    existing = talent_repository.get_by_id(proposal['talent_id']) if proposal['talent_id'] else None
    values = dict(existing) if existing else {'entity_type':'person','status':'draft','display_order':0}
    values.update({key:data[key] for key in ('category_id','description','reunion_attachment','private_source_reference','private_source_url','private_source_note')})
    values['name'] = data['name']
    values['city_id'] = data.get('city_id')
    url = data['url']
    host = urlsplit(url).hostname or ''
    field = {'instagram.com':'instagram_url','youtube.com':'youtube_url','youtu.be':'youtube_url','tiktok.com':'tiktok_url','facebook.com':'facebook_url'}.get(host.removeprefix('www.'),'website_url')
    values[field] = url
    talent_id,errors = talent_service.save_talent(values,talent_id=proposal['talent_id'])
    if errors:
        raise ProposalError(' '.join(errors))
    return talent_id


def prepare(proposal):
    """Create a separate personality draft, keeping site proposals pending."""
    fresh = repository.get(proposal['id'])
    if not fresh:
        raise ProposalError('Cette demande est introuvable.')
    proposal = current_proposal(fresh)
    if proposal['status'] not in ('pending','preparation'):
        raise ProposalError('Cette demande ne peut pas être préparée.')
    talent_id = proposal['talent_id']
    if proposal['kind'] == 'personality' and not talent_id:
        talent_id = save_talent(proposal,dict(proposal))
    repository.set_state(proposal['id'],'preparation',talent_id=talent_id)


def reject(proposal,reason,admin):
    """Refuse only unpublished proposals and preserve a private required reason."""
    validate_reason(reason)
    if proposal['status'] not in ('pending','preparation'):
        raise ProposalError('Cette demande ne peut pas être refusée.')
    if proposal['site_id']:
        result = site_lifecycle_service.transition_status(proposal['site_id'],'refuse',refusal_reason=reason,admin_username=admin)
        if not result.changed:
            raise ProposalError(result.message)
    if proposal['talent_id']:
        row = talent_repository.get_by_id(proposal['talent_id'])
        if row and row['status'] == 'published':
            raise ProposalError('Archive la fiche publiée au lieu de refuser sa proposition.')
        talent_service.archive(proposal['talent_id'])
    repository.set_state(proposal['id'],'refused',refusal_reason=reason)


def archive(proposal):
    """Archive linked content only after the route's explicit confirmation."""
    if proposal['status'] == 'refused':
        raise ProposalError('Cette demande est déjà refusée.')
    if proposal['site_id']:
        result = site_lifecycle_service.transition_status(proposal['site_id'],'archived')
        if not result.changed:
            raise ProposalError(result.message)
    elif proposal['talent_id']:
        talent_service.archive(proposal['talent_id'])
    else:
        raise ProposalError('Prépare d’abord la fiche avant de l’archiver.')
    repository.set_state(proposal['id'],'archived')


def current_proposal(proposal):
    """Reflect linked content decisions made by existing publication screens."""
    result = dict(proposal)
    linked = repository.get_site_record(proposal['site_id']) if proposal['site_id'] else (
        talent_repository.get_by_id(proposal['talent_id']) if proposal['talent_id'] else None)
    if linked:
        mapped = {'valide':'published','published':'published','archived':'archived','refuse':'refused'}
        result['status'] = mapped.get(linked['status'],result['status'])
    return result
