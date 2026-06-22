# -*- coding: utf-8 -*-

from xml.sax.saxutils import escape

from flask import url_for

from ..repositories import category_repository, content_repository, site_repository


# Pages publiques stables à toujours inclure dans le sitemap.
STATIC_ENDPOINTS = [
    "accueil",
    "villes_index",
    "most_visited_sites",
    "most_visited_categories",
    "recently_added_sites",
    "trends",
    "faq",
    "blog",
]


def _url_entry(loc, lastmod=None):
    """Construit un bloc <url> de sitemap.

    Args:
        loc (str): URL absolue de la page.
        lastmod (str | None): Date de dernière modification (AAAA-MM-JJ).

    Returns:
        str: Fragment XML <url>...</url>.
    """

    parts = [f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
    inner = "\n".join(parts)
    return f"  <url>\n{inner}\n  </url>"


def build_sitemap_xml():
    """Génère dynamiquement le sitemap XML à partir des données publiées.

    Inclut les pages publiques stables, les catégories, les villes et toutes
    les pages de contenu publiées (donc chaque page créée depuis l'admin).

    Returns:
        str: Document sitemap XML complet.
    """

    entries = []

    for endpoint in STATIC_ENDPOINTS:
        entries.append(_url_entry(url_for(endpoint, _external=True)))

    for category in category_repository.get_all_categories():
        entries.append(_url_entry(url_for("voir_categorie", slug=category["slug"], _external=True)))

    for city in site_repository.get_admin_city_filters():
        entries.append(_url_entry(url_for("voir_ville", slug=city["slug"], _external=True)))

    for page in content_repository.get_published_for_sitemap():
        lastmod = (page["updated_at"] or "")[:10] or None
        entries.append(_url_entry(url_for("content.show", slug=page["slug"], _external=True), lastmod))

    body = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )
