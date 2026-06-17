# -*- coding: utf-8 -*-

from flask import Blueprint, render_template


creators_bp = Blueprint("creators", __name__)

CREATOR_UNIVERSES = [
    "Humour",
    "Lifestyle",
    "Voyage",
    "Food",
    "Musique",
    "Gaming",
    "Art & Image",
    "Sport",
]

CREATORS = [
    {
        "slug": "harendra",
        "name": "Harendra",
        "category": "Humour",
        "city": "Saint-Denis",
        "image": "creators/harendra.svg",
        "description": "Un regard drôle et local sur le quotidien réunionnais.",
        "platforms": [
            {"name": "YouTube", "followers": 185000},
            {"name": "Instagram", "followers": 92000},
            {"name": "TikTok", "followers": 140000},
        ],
    },
    {
        "slug": "la-zeba",
        "name": "La Zeba",
        "category": "Lifestyle",
        "city": "Saint-Pierre",
        "image": "creators/la-zeba.svg",
        "description": "Lifestyle, sorties et instants péi avec une tonalité solaire.",
        "platforms": [
            {"name": "Instagram", "followers": 76000},
            {"name": "TikTok", "followers": 118000},
        ],
    },
    {
        "slug": "romuzeuf",
        "name": "Romuzeuf",
        "category": "Gaming",
        "city": "Le Tampon",
        "image": "creators/romuzeuf.svg",
        "description": "Création vidéo, gaming et formats courts pour une audience jeune.",
        "platforms": [
            {"name": "YouTube", "followers": 65000},
            {"name": "Twitch", "followers": 28000},
            {"name": "TikTok", "followers": 54000},
        ],
    },
    {
        "slug": "miazz",
        "name": "Miazz",
        "category": "Musique",
        "city": "Saint-Paul",
        "image": "creators/miazz.svg",
        "description": "Univers musical, coulisses créatives et énergie locale.",
        "platforms": [
            {"name": "YouTube", "followers": 42000},
            {"name": "Instagram", "followers": 36000},
        ],
    },
    {
        "slug": "space-974",
        "name": "Space 974",
        "category": "Art & Image",
        "city": "Saint-Leu",
        "image": "creators/space-974.svg",
        "description": "Photo, image et exploration visuelle des paysages réunionnais.",
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
        tier = "Audience majeure"
    elif total_followers >= 100_000:
        tier = "Talent confirmé"
    else:
        tier = "À suivre"

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


@creators_bp.route("/createurs-reunionnais")
def creators_index():
    """
    Affiche la première maquette statique de l'annuaire des créateurs réunionnais.

    Returns:
        str: Page HTML des créateurs réunionnais.
    """

    creators = [build_creator_view_model(creator) for creator in CREATORS]
    categories = sorted({creator["category"] for creator in creators})
    featured_creator = creators[0]
    total_followers = sum(creator["total_followers"] for creator in creators)
    stats = {
        "creator_count": len(creators),
        "total_followers": total_followers,
        "total_followers_label": format_followers(total_followers),
        "category_count": len(categories),
    }
    region_cards = build_region_cards(creators)

    # TODO: future phase BDD/profil public : /createur/<slug>.
    return render_template(
        "creators/index.html",
        creators=creators,
        universes=CREATOR_UNIVERSES,
        stats=stats,
        region_cards=region_cards,
        featured_creator=featured_creator,
    )
