# -*- coding: utf-8 -*-

import sqlite3

from flask import current_app

from .utils import normalize_search_text


def get_db_connection():
    """Ouvre et configure une connexion SQLite pour les repositories."""
    conn = sqlite3.connect(current_app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function(
        "NORMALIZE_SEARCH",
        1,
        normalize_search_text,
        deterministic=True,
    )
    return conn
