# -*- coding: utf-8 -*-

from flask import request
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect


def get_client_ip() -> str:
    """Retourne l'IP cliente réelle derrière un reverse proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


csrf = CSRFProtect()
limiter = Limiter(key_func=get_client_ip)
