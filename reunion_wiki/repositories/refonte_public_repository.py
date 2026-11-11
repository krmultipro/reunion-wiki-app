"""Lectures publiques SQLite, sans coordonnées ni sources privées."""

from ..db import get_db_connection


def public_sites():
    """Retourne les sites publiés et leur catégorie, jamais les propositions."""
    connection = get_db_connection()
    try:
        return [dict(row) for row in connection.execute("""
            SELECT s.id, s.nom AS name, s.lien AS url, s.description,
                   c.nom AS category, c.slug AS category_slug, s.published_at
            FROM sites s LEFT JOIN categories c ON c.id=s.category_id
            WHERE s.status='valide'
            ORDER BY NORMALIZE_SEARCH(s.nom), s.id
        """)]
    finally:
        connection.close()


def public_profiles():
    """Retourne uniquement les champs affichables des personnalités publiées."""
    connection = get_db_connection()
    try:
        if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='talents'").fetchone():
            return []
        return [dict(row) for row in connection.execute("""
            SELECT t.id, t.name, t.slug, t.description, t.bio, t.image,
                   tc.name AS category, tc.slug AS category_slug,
                   t.instagram_url, t.youtube_url, t.tiktok_url, t.facebook_url,
                   t.website_url, t.published_at
            FROM talents t LEFT JOIN talent_categories tc ON tc.id=t.category_id
            WHERE t.status='published'
            ORDER BY NORMALIZE_SEARCH(t.name), t.id
        """)]
    finally:
        connection.close()


def site_categories():
    """Retourne le référentiel des catégories de sites, y compris les vides."""
    connection = get_db_connection()
    try:
        return [dict(row) for row in connection.execute(
            'SELECT nom AS name, slug FROM categories ORDER BY NORMALIZE_SEARCH(nom)'
        )]
    finally:
        connection.close()
