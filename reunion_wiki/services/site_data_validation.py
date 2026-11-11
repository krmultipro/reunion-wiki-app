"""Invariants des données stockées avant publication, sans accès à Flask ou SQL."""

import re
from types import SimpleNamespace

from wtforms.validators import URL, ValidationError


def publication_data_error(site):
    """Retourne une erreur sur les valeurs stockées, sans les corriger en silence."""
    name = site['nom']
    if not isinstance(name, str) or not 2 <= len(name.strip()) <= 100:
        return 'Le nom du site doit faire entre 2 et 100 caractères avant publication.'
    if re.search(r'[<>"\']', name):
        return 'Le nom du site contient des caractères non autorisés.'
    description = site['description']
    if not isinstance(description, str) or not 10 <= len(description.strip()) <= 500:
        return 'Une description de 10 à 500 caractères est nécessaire avant publication.'
    if re.search(r'<script|javascript:|on\w+\s*=', description, re.IGNORECASE):
        return 'La description contient du contenu non autorisé.'
    url = site['lien']
    if not isinstance(url, str) or not url.lower().startswith(('http://', 'https://')):
        return 'Une URL HTTP ou HTTPS valide est nécessaire avant publication.'
    try:
        URL(message='URL invalide.')(None, SimpleNamespace(data=url))
    except (ValidationError, ValueError):
        return 'Une URL HTTP ou HTTPS valide est nécessaire avant publication.'
    return None
