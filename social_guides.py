# -*- coding: utf-8 -*-

"""Configuration éditoriale des sélections sociales de Réunion Wiki.

Ces valeurs servent à la fois aux pages publiques dynamiques et au contenu
initial créé par la migration. Une page déjà personnalisée dans l'admin n'est
jamais écrasée par ces textes par défaut.
"""


SOCIAL_GUIDES = {
    "youtube": {
        "field": "youtube_url",
        "slug": "youtubeurs-reunionnais",
        "platform": "YouTube",
        "hub_title": "Youtubeurs réunionnais",
        "hub_description": "Chaînes locales, divertissement, musique, médias et documentaires.",
        "collection_title": "Chaînes YouTube réunionnaises à découvrir",
        "collection_intro": (
            "Ces profils sont ajoutés automatiquement depuis les fiches publiées "
            "qui possèdent une chaîne YouTube."
        ),
        "empty_message": "Les premières chaînes apparaîtront ici dès qu'une fiche YouTube sera publiée.",
        "profile_link_label": "Voir la sélection YouTube",
        "title": "Youtubeurs réunionnais",
        "summary": (
            "Explorez les chaînes YouTube de créateurs réunionnais actifs dans l'humour, "
            "la musique, le voyage, la cuisine, les médias et la culture locale."
        ),
        "body": (
            "<h2>La création réunionnaise en vidéo</h2>"
            "<p>YouTube met en lumière des vidéastes, artistes, humoristes, musiciens et "
            "médias de La Réunion. Leurs vidéos racontent l'île, ses talents et ses "
            "initiatives à travers des univers variés : divertissement, voyage, cuisine, "
            "culture et documentaires.</p>"
            "<h2>Retrouver les chaînes officielles</h2>"
            "<p>Chaque carte mène vers une fiche Réunion Wiki et vers les liens officiels du "
            "créateur. La sélection se met à jour automatiquement avec les nouvelles chaînes "
            "YouTube ajoutées aux fiches publiées.</p>"
        ),
        "meta_title": "Youtubeurs réunionnais : chaînes et créateurs | Réunion Wiki",
        "meta_description": (
            "Découvrez des youtubeurs réunionnais et leurs chaînes : humour, musique, "
            "documentaires, voyage et création locale à La Réunion."
        ),
    },
    "instagram": {
        "field": "instagram_url",
        "slug": "createurs-instagram-reunionnais",
        "platform": "Instagram",
        "hub_title": "Créateurs Instagram réunionnais",
        "hub_description": "Photographie, art, lifestyle, humour et création visuelle locale.",
        "collection_title": "Créateurs réunionnais sur Instagram",
        "collection_intro": (
            "Cette sélection rassemble automatiquement les talents publiés dont la fiche "
            "contient un compte Instagram officiel."
        ),
        "empty_message": "Les premiers comptes apparaîtront ici dès qu'une fiche Instagram sera publiée.",
        "profile_link_label": "Voir la sélection Instagram",
        "title": "Créateurs Instagram réunionnais",
        "summary": (
            "Explorez les comptes Instagram de créateurs réunionnais actifs dans la photo, "
            "l'art, l'humour, la musique, le lifestyle et la culture locale."
        ),
        "body": (
            "<h2>La création réunionnaise en images</h2>"
            "<p>Instagram met en lumière des photographes, artistes, humoristes, musiciens et "
            "créateurs de contenu de La Réunion. Leurs publications racontent l'île, ses "
            "talents et ses initiatives à travers des univers visuels personnels.</p>"
            "<h2>Retrouver les comptes officiels</h2>"
            "<p>Chaque carte mène vers une fiche Réunion Wiki vérifiée. La sélection se met à "
            "jour automatiquement avec les nouveaux profils Instagram publiés.</p>"
        ),
        "meta_title": "Créateurs Instagram réunionnais | Réunion Wiki",
        "meta_description": (
            "Découvrez les créateurs réunionnais sur Instagram : photographie, art, humour, "
            "musique, lifestyle et comptes locaux à suivre."
        ),
    },
    "tiktok": {
        "field": "tiktok_url",
        "slug": "tiktokeurs-reunionnais",
        "platform": "TikTok",
        "hub_title": "TikTokeurs réunionnais",
        "hub_description": "Formats courts, humour péi, tendances, musique et découvertes locales.",
        "collection_title": "TikTokeurs réunionnais à découvrir",
        "collection_intro": (
            "Les fiches ci-dessous sont ajoutées automatiquement lorsqu'un talent publié "
            "renseigne son compte TikTok officiel."
        ),
        "empty_message": "Les premiers comptes apparaîtront ici dès qu'une fiche TikTok sera publiée.",
        "profile_link_label": "Voir la sélection TikTok",
        "title": "TikTokeurs réunionnais",
        "summary": (
            "Découvrez les créateurs TikTok de La Réunion : humour, formats courts, musique, "
            "tendances et contenus inspirés de la vie réunionnaise."
        ),
        "body": (
            "<h2>Les formats courts créés à La Réunion</h2>"
            "<p>Sur TikTok, les créateurs réunionnais partagent humour, musique, scènes du "
            "quotidien, conseils et découvertes locales. Leurs vidéos font vivre les expressions, "
            "les paysages et la culture de l'île dans des formats rapides.</p>"
            "<h2>Une sélection qui évolue avec les talents</h2>"
            "<p>Cette page réunit les comptes officiels associés aux fiches publiées. Elle est "
            "actualisée automatiquement lorsqu'un nouveau profil TikTok rejoint le guide.</p>"
        ),
        "meta_title": "TikTokeurs réunionnais : créateurs TikTok | Réunion Wiki",
        "meta_description": (
            "Découvrez les TikTokeurs réunionnais : humour péi, musique, tendances, formats "
            "courts et créateurs de contenu de La Réunion."
        ),
    },
    "facebook": {
        "field": "facebook_url",
        "slug": "createurs-facebook-reunionnais",
        "platform": "Facebook",
        "hub_title": "Créateurs réunionnais sur Facebook",
        "hub_description": "Pages de créateurs, médias, artistes et communautés locales.",
        "collection_title": "Pages Facebook réunionnaises à découvrir",
        "collection_intro": (
            "Cette liste rassemble automatiquement les talents publiés qui disposent d'une "
            "page Facebook officielle."
        ),
        "empty_message": "Les premières pages apparaîtront ici dès qu'une fiche Facebook sera publiée.",
        "profile_link_label": "Voir la sélection Facebook",
        "title": "Créateurs réunionnais sur Facebook",
        "summary": (
            "Retrouvez des créateurs, artistes, médias et personnalités de La Réunion présents "
            "sur Facebook, avec leurs fiches et pages officielles."
        ),
        "body": (
            "<h2>Les pages locales à retrouver sur Facebook</h2>"
            "<p>Facebook reste un espace important pour suivre des artistes, médias, associations, "
            "personnalités et communautés de La Réunion. Cette sélection facilite l'accès à leurs "
            "présentations et à leurs pages officielles.</p>"
            "<h2>Des fiches reliées au guide des créateurs</h2>"
            "<p>Les profils affichés proviennent directement du répertoire Réunion Wiki. Toute "
            "nouvelle fiche publiée avec une page Facebook est ajoutée automatiquement.</p>"
        ),
        "meta_title": "Créateurs réunionnais sur Facebook | Réunion Wiki",
        "meta_description": (
            "Retrouvez les créateurs, artistes, médias et personnalités réunionnaises sur "
            "Facebook grâce à leurs fiches et pages officielles."
        ),
    },
}

SOCIAL_GUIDES_BY_SLUG = {
    guide["slug"]: {"key": key, **guide}
    for key, guide in SOCIAL_GUIDES.items()
}
