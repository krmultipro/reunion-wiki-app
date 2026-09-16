# -*- coding: utf-8 -*-
"""Filtres WTForms partagés par les formulaires de l'application."""

import re


def _strip_filter(value):
    """Retire les espaces au début et à la fin d'une chaîne.

    WTForms appelle ce filtre avant d'exécuter les validateurs du champ. Les
    valeurs qui ne sont pas des chaînes (par exemple ``None``) sont renvoyées
    sans modification.
    """
    return value.strip() if isinstance(value, str) else value


def _sanitize_basic(value):
    """Nettoie une chaîne courte destinée à contenir uniquement du texte.

    Le filtre retire les espaces extérieurs, les balises HTML et les caractères
    de contrôle invisibles. Il convient notamment aux noms, titres et slugs.
    """
    if not isinstance(value, str):
        return value

    value = value.strip()
    # Retire les balises comme <b> ou <script> en conservant leur texte.
    value = re.sub(r"<[^>]+>", "", value)
    # Retire les caractères de contrôle, mais conserve tabulation et retours à
    # la ligne standards (\t, \n et \r).
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    return value


def _sanitize_multiline(value):
    """Nettoie un texte multiligne tout en conservant sa mise en paragraphes.

    En plus du nettoyage de base, les différents types de retours à la ligne
    sont uniformisés et les grands blocs de lignes vides sont réduits.
    """
    if not isinstance(value, str):
        return value

    value = value.strip()
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    # Uniformise les retours Windows (\r\n) et anciens Mac (\r) au format \n.
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    # Trois retours ou plus deviennent deux retours, soit une ligne vide.
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value


def _normalize_url(value):
    """Nettoie une URL et ajoute ``https://`` si aucun protocole n'est fourni.

    Une chaîne vide reste vide afin que les validateurs WTForms puissent gérer
    eux-mêmes le caractère obligatoire ou optionnel du champ.
    """
    if not isinstance(value, str):
        return value

    value = _sanitize_basic(value)
    if not value:
        return value

    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    return value
