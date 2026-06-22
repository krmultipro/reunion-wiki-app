# -*- coding: utf-8 -*-

from flask import Blueprint, render_template


creators_bp = Blueprint("creators", __name__)

CREATOR_UNIVERSES = [
    "Humoristes",
    "Youtubeurs",
    "Photographes",
    "Artistes",
    "Musiciens",
    "Créateurs vidéo",
    "Lifestyle",
    "Sport",
]

EDITORIAL_UNIVERSES = [
    {
        "title": "Humour réunionnais",
        "description": "Sketchs, personnages et scènes du quotidien péi.",
    },
    {
        "title": "Photographie locale",
        "description": "Regards sur les paysages, les villes et les instants de l'île.",
    },
    {
        "title": "Musique péi",
        "description": "Artistes, voix et univers sonores ancrés à La Réunion.",
    },
    {
        "title": "Création vidéo",
        "description": "Formats courts, séries web, coulisses et narration locale.",
    },
    {
        "title": "Lifestyle",
        "description": "Sorties, lieux, habitudes et inspirations du quotidien.",
    },
]

CREATORS = [
    {
        "slug": "harendra",
        "name": "Harendra",
        "discipline": "Humoriste réunionnais",
        "category": "Humoristes",
        "city": "Saint-Pierre",
        "image": "creators/harendra.svg",
        "description": (
            "Originaire du sud de l'île, il est connu pour ses vidéos humoristiques "
            "inspirées du quotidien réunionnais."
        ),
        "creative_universe": "Humour réunionnais",
        "platforms": [
            {"name": "YouTube", "followers": 185000},
            {"name": "Instagram", "followers": 92000},
            {"name": "TikTok", "followers": 140000},
        ],
    },
    {
        "slug": "la-zeba",
        "name": "La Zeba",
        "discipline": "Créatrice lifestyle",
        "category": "Lifestyle",
        "city": "Saint-Pierre",
        "image": "creators/la-zeba.svg",
        "description": "Elle partage des sorties, des lieux de vie et des instants péi avec une tonalité solaire.",
        "creative_universe": "Lifestyle local",
        "platforms": [
            {"name": "Instagram", "followers": 76000},
            {"name": "TikTok", "followers": 118000},
        ],
    },
    {
        "slug": "romuzeuf",
        "name": "Romuzeuf",
        "discipline": "Youtubeur et vidéaste",
        "category": "Youtubeurs",
        "city": "Le Tampon",
        "image": "creators/romuzeuf.svg",
        "description": "Il mêle création vidéo, formats courts et culture web pour parler à une génération connectée.",
        "creative_universe": "Création vidéo",
        "platforms": [
            {"name": "YouTube", "followers": 65000},
            {"name": "Twitch", "followers": 28000},
            {"name": "TikTok", "followers": 54000},
        ],
    },
    {
        "slug": "miazz",
        "name": "Miazz",
        "discipline": "Musicien",
        "category": "Musiciens",
        "city": "Saint-Paul",
        "image": "creators/miazz.svg",
        "description": "Son univers met en avant la musique, les coulisses créatives et une énergie locale affirmée.",
        "creative_universe": "Musique péi",
        "platforms": [
            {"name": "YouTube", "followers": 42000},
            {"name": "Instagram", "followers": 36000},
        ],
    },
    {
        "slug": "space-974",
        "name": "Space 974",
        "discipline": "Photographe",
        "category": "Photographes",
        "city": "Saint-Leu",
        "image": "creators/space-974.svg",
        "description": "Son travail explore les paysages, la lumière et les détails visuels de La Réunion.",
        "creative_universe": "Photographie locale",
        "platforms": [
            {"name": "Instagram", "followers": 58000},
            {"name": "YouTube", "followers": 21000},
            {"name": "TikTok", "followers": 33000},
        ],
    },
]


def format_followers(value):
    """
    Formate un volume d'abonnés pour l'affichage.

    Args:
        value (int): Nombre brut d'abonnés.

    Returns:
        str: Nombre formaté en notation courte.
    """

    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} M".replace(".0", "")
    if value >= 1_000:
        return f"{round(value / 1_000)} k"
    return str(value)


def build_creator_view_model(creator):
    """
    Prépare les données calculées d'un créateur pour le template.

    Args:
        creator (dict): Données statiques du créateur.

    Returns:
        dict: Données enrichies prêtes à être rendues.
    """

    total_followers = sum(platform["followers"] for platform in creator["platforms"])
    platform_names = [platform["name"] for platform in creator["platforms"]]
    if total_followers >= 300_000:
        tier = "Portrait repéré"
    elif total_followers >= 100_000:
        tier = "Parcours installé"
    else:
        tier = "À découvrir"

    return {
        **creator,
        "total_followers": total_followers,
        "total_followers_label": format_followers(total_followers),
        "platform_count": len(platform_names),
        "platform_names": platform_names,
        "platforms_label": ", ".join(platform_names),
        "tier": tier,
    }


def build_region_cards(creators):
    """
    Regroupe les créateurs par ville pour la section découverte régionale.

    Args:
        creators (list[dict]): Créateurs enrichis.

    Returns:
        list[dict]: Cartes de villes avec libellés préparés.
    """

    region_names = ["Saint-Denis", "Saint-Pierre", "Le Tampon"]
    cards = []
    for city in region_names:
        city_creators = [creator for creator in creators if creator["city"] == city]
        cards.append(
            {
                "city": city,
                "title": f"Créateurs à {city}",
                "count": len(city_creators),
                "creator_names": ", ".join(creator["name"] for creator in city_creators) or "Sélection à venir",
            }
        )
    return cards


def build_popular_personality_cards(creators):
    """
    Prépare une sélection éditoriale de personnalités locales à mettre en avant.

    Args:
        creators (list[dict]): Créateurs enrichis.

    Returns:
        list[dict]: Cartes prêtes pour une section de type guide local.
    """

    return sorted(creators, key=lambda creator: creator["total_followers"], reverse=True)[:3]


@creators_bp.route("/createurs-reunionnais")
def creators_index():
    """
    Affiche une page de découverte des talents et créateurs réunionnais.

    Returns:
        str: Page HTML des créateurs réunionnais.
    """

    creators = [build_creator_view_model(creator) for creator in CREATORS]
    featured_creator = creators[0]
    total_followers = sum(creator["total_followers"] for creator in creators)
    stats = {
        "creator_count": len(creators),
        "total_followers": total_followers,
        "total_followers_label": format_followers(total_followers),
        "category_count": len(CREATOR_UNIVERSES),
        "city_count": len({creator["city"] for creator in creators}),
    }
    region_cards = build_region_cards(creators)
    popular_creators = build_popular_personality_cards(creators)

    # TODO: future phase BDD/profil public : /createur/<slug>.
    return render_template(
        "creators/index.html",
        creators=creators,
        editorial_universes=EDITORIAL_UNIVERSES,
        stats=stats,
        region_cards=region_cards,
        featured_creator=featured_creator,
        popular_creators=popular_creators,
    )
