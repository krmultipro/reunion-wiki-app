"""Contrats de consultation et recherche simple de la refonte DEV."""

import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, urlunsplit

from flask import current_app, request, url_for

from ..repositories import refonte_public_repository as repository
from ..utils import normalize_search_text


def safe_external_url(value):
    """Accepte une URL HTTP(S) absolue sans identifiants ni caractères de contrôle."""
    value = str(value or '').strip()
    if any(ord(character) < 32 for character in value):
        return ''
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
            return ''
        parsed.port
        return value
    except ValueError:
        return ''


def safe_return(value, fallback=None):
    """Borne un retour à une route de consultation publique locale autorisée."""
    fallback = fallback or url_for('accueil')
    try:
        parsed = urlsplit(value or '')
        if parsed.scheme or parsed.netloc or not parsed.path.startswith('/') or parsed.path.startswith('//') or '\\' in parsed.path:
            return fallback
        allowed = {'/', '/sites', '/createurs-reunionnais', '/recherche', '/faq', '/contact', '/mentions-legales', '/proposer'}
        if parsed.path not in allowed and not parsed.path.startswith(('/createurs/', '/categorie/')):
            return fallback
        if any(ord(character) < 32 for character in (value or '')):
            return fallback
        # Les retours imbriqués restent des données ; aucun redirect HTTP n'est exécuté.
        return urlunsplit(('', '', parsed.path, parsed.query, ''))
    except ValueError:
        return fallback


def _previews():
    """Charge les associations d'aperçus autorisés depuis un manifeste local public."""
    path = Path(current_app.static_folder) / 'refonte' / 'previews.json'
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        return {}


def _site(row, previews):
    """Prépare un lien comptabilisé et un aperçu correspondant à l'URL réelle."""
    item = dict(row)
    item['description'] = item.get('description') or ''
    item['category'] = item.get('category') or 'Sans catégorie'
    item['href'] = url_for('redirect_site', site_id=item['id'])
    item['domain'] = urlsplit(safe_external_url(item.get('url'))).hostname or ''
    preview = previews.get(str(item['id']), {})
    same_url = (item.get('url') or '').rstrip('/') == str(preview.get('url') or '').rstrip('/')
    item['preview'] = url_for('static', filename='refonte/previews/' + preview['image']) if same_url and preview.get('image') else None
    return item


def _profile(row):
    """Prépare une fiche publique, sans HTML libre ni champ administratif."""
    item = dict(row)
    item['description'] = item.get('description') or ''
    item['category'] = item.get('category') or 'Personnalité réunionnaise'
    image = str(item.get('image') or '')
    path = PurePosixPath(image)
    valid_image = image.startswith(('uploads/', 'images/', 'icons/')) and '..' not in path.parts and '\\' not in image
    item['portrait'] = url_for('static', filename=image) if valid_image else url_for('static', filename='refonte/profile-placeholder.svg')
    item['href'] = url_for('creators.creator_detail', slug=item['slug'])
    item['links'] = [(label, safe_external_url(item.get(field))) for label, field in (
        ('Instagram', 'instagram_url'), ('YouTube', 'youtube_url'), ('TikTok', 'tiktok_url'), ('Facebook', 'facebook_url'), ('Site officiel', 'website_url')
    ) if safe_external_url(item.get(field))]
    return item


def catalog():
    """Construit le catalogue courant depuis SQLite, jamais depuis une maquette."""
    previews = _previews()
    return {
        'sites': [_site(row, previews) for row in repository.public_sites()],
        'profiles': [_profile(row) for row in repository.public_profiles()],
        'categories': repository.site_categories(),
    }


def _matches(item, query):
    """Recherche des termes normalisés, indépendamment de leur ordre."""
    terms = normalize_search_text(query).split()
    content = normalize_search_text(' '.join(str(item.get(key) or '') for key in ('name', 'category', 'description')))
    return all(term in content for term in terms)


def list_context(kind, query='', category=''):
    """Combine catégorie unique et texte pour un annuaire alphabétique."""
    data = catalog()
    rows = data[kind]
    categories = data['categories'] if kind == 'sites' else sorted(
        {row['category_slug']: {'slug': row['category_slug'], 'name': row['category']} for row in rows if row.get('category_slug')}.values(),
        key=lambda item: normalize_search_text(item['name']),
    )
    invalid_category = bool(category and not any(item['slug'] == category for item in categories))
    if invalid_category:
        category = ''
    query = (query or '').strip()[:160]
    filtered = [row for row in rows if (not category or row['category_slug'] == category) and _matches(row, query)]
    return {'rows': filtered, 'category_options': categories, 'q': query, 'selected_category': category,
            'invalid_category': invalid_category, 'kind': kind}


def home_context():
    """Reprend la sélection stable de la maquette et les dernières personnalités."""
    data = catalog()
    key = lambda row: (row.get('published_at') or '', row['id'])
    # Source mobile-final : sélection stable explicite, jamais un classement de clics.
    featured_ids = current_app.config.get('HOME_FEATURED_SITE_IDS', (87, 65, 81))
    sites_by_id = {row['id']: row for row in data['sites']}
    selected = [sites_by_id[site_id] for site_id in featured_ids if site_id in sites_by_id]
    selected = selected[:3]
    for site in data['sites']:
        if len(selected) >= 3:
            break
        if site not in selected:
            selected.append(site)
    return {'sites': selected,
            'profiles': sorted(data['profiles'], key=key, reverse=True)[:3]}


def search_context(query):
    """Retourne les trois groupes de résultats publics sans sections vides."""
    data = catalog()
    query = (query or '').strip()[:160]
    return {'q': query,
            'sites': [row for row in data['sites'] if query and _matches(row, query)],
            'profiles': [row for row in data['profiles'] if query and _matches(row, query)],
            'matched_categories': [row for row in data['categories'] if query and all(
                term in normalize_search_text(row['name']) for term in normalize_search_text(query).split())]}


def profile_context(slug):
    """Retourne une fiche publiée et jusqu'à trois profils de sa catégorie."""
    profiles = catalog()['profiles']
    profile = next((row for row in profiles if row['slug'] == slug), None)
    if not profile:
        return None
    texts = list(dict.fromkeys(text for text in (profile['description'], profile.get('bio')) if text))
    paragraphs = [paragraph for text in texts for paragraph in text.replace('\r\n', '\n').split('\n\n') if paragraph.strip()]
    return {'profile': profile, 'similar': [row for row in profiles if row['id'] != profile['id'] and row.get('category_slug') and row['category_slug'] == profile['category_slug']][:3],
            'paragraphs': paragraphs}


def page_context(active='', fallback=None):
    """Fournit un retour sûr et le contexte de navigation commun des pages publiques."""
    back = safe_return(request.args.get('retour'), fallback)
    label = {'/': 'à l’accueil', '/sites': 'aux sites', '/createurs-reunionnais': 'aux personnalités',
             '/recherche': 'aux résultats', '/faq': 'à la FAQ', '/contact': 'au contact',
             '/mentions-legales': 'aux mentions légales', '/proposer': 'à la proposition'}.get(urlsplit(back).path, 'à la fiche')
    return {'nav_active': active, 'back_url': back, 'back_label': label,
            'current_url': safe_return(request.full_path.rstrip('?'))}
