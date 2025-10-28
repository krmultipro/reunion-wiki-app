"""SQLite helpers."""

from __future__ import annotations

import os
import sqlite3
from typing import Optional

from flask import current_app


def get_db_path() -> str:
    """Return the absolute path to the configured SQLite database."""
    path = current_app.config["DATABASE_PATH"]
    return os.path.abspath(path)


def get_db_connection() -> Optional[sqlite3.Connection]:
    """Create a SQLite connection with row factory enabled."""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as exc:
        current_app.logger.error(f"Erreur de connexion à la base de données: {exc}")
        return None
