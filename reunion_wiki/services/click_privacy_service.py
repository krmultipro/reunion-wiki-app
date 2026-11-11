"""Pseudonymisation et zonage local des clics sortants."""

import hashlib
import hmac
import ipaddress
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


ALLOWED_ZONES = ("Nord", "Sud", "Est", "Ouest", "Hors Réunion", "Inconnu")
COMMUNE_ZONES = {
    "Saint-Denis": "Nord", "Sainte-Marie": "Nord", "Sainte-Suzanne": "Nord",
    "Saint-Pierre": "Sud", "Le Tampon": "Sud", "Saint-Joseph": "Sud",
    "Saint-Philippe": "Sud", "Petite-Île": "Sud", "L'Étang-Salé": "Sud",
    "Les Avirons": "Sud", "Cilaos": "Sud",
    "Saint-André": "Est", "Bras-Panon": "Est", "Saint-Benoît": "Est",
    "Sainte-Rose": "Est", "Salazie": "Est", "La Plaine-des-Palmistes": "Est",
    "Le Port": "Ouest", "La Possession": "Ouest", "Saint-Paul": "Ouest",
    "Trois-Bassins": "Ouest", "Saint-Leu": "Ouest",
}


def build_visitor_token(ip_address, user_agent, site_id):
    """Construit une empreinte HMAC non réversible, propre à un site."""
    secret = current_app.config["CLICK_HMAC_SECRET"].encode("utf-8")
    payload = f"{ip_address}|{user_agent}|{site_id}".encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def reunion_day(now=None):
    """Retourne la journée civile courante dans le fuseau de La Réunion."""
    current = now or datetime.now(ZoneInfo("Indian/Reunion"))
    return current.astimezone(ZoneInfo("Indian/Reunion")).date().isoformat()


def resolve_zone(ip_address):
    """Résout localement une IP en grande zone, ou ``Inconnu`` sans base GeoIP."""
    try:
        address = ipaddress.ip_address(ip_address)
    except ValueError:
        return "Inconnu"
    if address.is_private or address.is_loopback or address.is_reserved:
        return "Inconnu"

    database_path = current_app.config.get("GEOIP_DATABASE_PATH")
    if not database_path:
        return "Inconnu"
    try:
        import geoip2.database
        with geoip2.database.Reader(database_path) as reader:
            response = reader.city(ip_address)
            country = response.country.iso_code
            subdivision = getattr(response.subdivisions.most_specific, "iso_code", None)
            if country == "FR" and subdivision != "RE":
                return "Hors Réunion"
            if country not in {"RE", "FR"}:
                return "Hors Réunion"
            city = response.city.name
            return COMMUNE_ZONES.get(city, "Inconnu")
    except (ImportError, OSError, ValueError, KeyError):
        return "Inconnu"
