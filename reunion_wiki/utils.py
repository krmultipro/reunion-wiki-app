# -*- coding: utf-8 -*-

from urllib.parse import urlparse

from flask import request

# Réexport conservé pour les imports historiques depuis reunion_wiki.utils.
from slug_utils import slugify


def get_client_ip() -> str:
    """Retourne l'IP cliente réelle derrière un reverse proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def is_safe_next_url(next_url: str) -> bool:
    """Autorise uniquement les chemins locaux internes."""
    if not next_url:
        return False
    if not next_url.startswith("/") or next_url.startswith("//"):
        return False
    parsed = urlparse(next_url)
    return parsed.scheme == "" and parsed.netloc == ""


def parse_positive_int(value, default=1):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def mask_ip(ip_value: str) -> str:
    """Masque les IP dans l'admin pour limiter l'exposition de données personnelles."""
    if not ip_value:
        return "—"
    ip = ip_value.split(",")[0].strip()
    if ":" in ip:  # IPv6
        parts = ip.split(":")
        return ":".join(parts[:3]) + ":*:*"
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.x.x"
    return "—"


def slugify_ville(nom: str) -> str:
    s = (nom or "").strip().lower()
    repl = {
        "à": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    for ch in ["'", "’", ".", ","]:
        s = s.replace(ch, "")
    return "-".join(s.split())
