# -*- coding: utf-8 -*-

"""Helpers, filtres et variables globales utilisés par les templates Jinja."""

import os
from datetime import datetime

from flask import current_app, session

from .forms.auth_forms import AdminLogoutForm
from .services import category_service


# Mapping partagé avec les templates pour afficher une icône par slug de catégorie.
# Si une catégorie n'est pas listée ici, les templates utilisent une icône par défaut.
ICON_MAP = {
    "culture-et-loisirs": "map.svg",
    "actualites": "newspaper.svg",
    "achats": "shopping-cart.svg",
    "transport": "bus.svg",
    "emploi-et-formation": "briefcase.svg",
    "meteo-et-alertes": "cloud-rain.svg",
    "administratifs": "file-text.svg",
    "nourriture": "utensils.svg",
    "sante": "heart.svg",
}

MONTH_NAMES_FR = (
    "JAN",
    "FÉV",
    "MAR",
    "AVR",
    "MAI",
    "JUN",
    "JUI",
    "AOÛ",
    "SEP",
    "OCT",
    "NOV",
    "DÉC",
)


def asset_versioning():
    """Expose asset_v() dans Jinja pour invalider le cache après changement statique."""

    def asset_v(path):
        full_path = os.path.join(current_app.static_folder, path)
        try:
            return int(os.path.getmtime(full_path))
        except OSError:
            return 1

    return {"asset_v": asset_v}


def inject_admin_logout_form():
    """Ajoute le formulaire CSRF de logout seulement quand un admin est connecté."""
    if session.get("admin_authenticated"):
        return {"admin_logout_form": AdminLogoutForm()}
    return {}


def inject_categories():
    """Expose les variables de navigation utilisées par les templates publics."""
    return {
        "categories": category_service.get_category_names(),
        "categories_slug": category_service.get_category_slug_map(),
        "ICON_MAP": ICON_MAP,
    }


def format_date(value, fmt="%d/%m/%Y"):
    """Filtre Jinja tolérant pour dates SQLite stockées en texte."""
    if not value:
        return ""
    if isinstance(value, str):
        for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                value = datetime.strptime(value, pattern)
                break
            except ValueError:
                continue
    return value.strftime(fmt)


def month_name(date_value):
    """Retourne l'abréviation française du mois pour les dates affichées."""
    if isinstance(date_value, str):
        date_value = datetime.fromisoformat(date_value)
    return MONTH_NAMES_FR[date_value.month - 1]


def register_template_helpers(app):
    """Enregistre tous les helpers de templates sur l'application Flask."""
    app.context_processor(asset_versioning)
    app.context_processor(inject_admin_logout_form)
    app.context_processor(inject_categories)
    app.add_template_filter(format_date, "format_date")
    app.add_template_filter(month_name, "month_name")
