# -*- coding: utf-8 -*-

"""Exports conservés pour les anciens scripts qui importent depuis ``app``."""

from .app import app
from .auth import admin_required, verify_admin_credentials
from .blueprints import register_legacy_blueprint_endpoints as _register_legacy_endpoints
from .http_handlers import (
    add_cache_headers,
    handle_csrf_error,
    internal_server_error,
    page_not_found,
)
from .template_helpers import (
    ICON_MAP,
    asset_versioning,
    format_date,
    inject_admin_logout_form,
    inject_categories,
    month_name,
)
from .utils import (
    get_client_ip,
    is_safe_next_url,
    mask_ip,
    parse_positive_int,
    slugify,
    slugify_ville,
)


def register_legacy_blueprint_endpoints(blueprint_name, endpoint_names):
    """Conserve la signature historique liée à l'application globale."""
    return _register_legacy_endpoints(app, blueprint_name, endpoint_names)


__all__ = [
    "ICON_MAP",
    "add_cache_headers",
    "admin_required",
    "asset_versioning",
    "format_date",
    "get_client_ip",
    "handle_csrf_error",
    "inject_admin_logout_form",
    "inject_categories",
    "internal_server_error",
    "is_safe_next_url",
    "mask_ip",
    "month_name",
    "page_not_found",
    "parse_positive_int",
    "register_legacy_blueprint_endpoints",
    "slugify",
    "slugify_ville",
    "verify_admin_credentials",
]
