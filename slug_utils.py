# -*- coding: utf-8 -*-
"""Normalisation de slugs partagée, sans dépendance à Flask."""

import re
import unicodedata


def slugify(text: str | None) -> str:
    """Transforme un texte en slug ASCII utilisable dans une URL."""
    normalized = (text or "").replace("&", "et")
    normalized = "".join(
        character
        for character in normalized
        if character.isalnum() or character.isspace() or character in "-_"
    )
    normalized = (
        unicodedata.normalize("NFKD", normalized)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[\s_]+", "-", normalized)
    normalized = re.sub(r"[^a-z0-9-]", "", normalized)
    return re.sub(r"-{2,}", "-", normalized).strip("-")
