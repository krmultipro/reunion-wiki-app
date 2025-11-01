"""SQLite helpers."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from flask import current_app


class DatabaseError(Exception):
    """Custom exception for database operations."""


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


@contextmanager
def db_transaction() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database transactions with automatic error handling.
    
    Usage:
        with db_transaction() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO sites ...")
            # conn.commit() is called automatically on success
    """
    conn = get_db_connection()
    if not conn:
        raise DatabaseError("Impossible de se connecter à la base de données")
    
    try:
        yield conn
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        current_app.logger.error(f"Erreur de transaction DB: {exc}")
        raise DatabaseError(f"Erreur de base de données: {exc}") from exc
    finally:
        conn.close()


@contextmanager
def db_query() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for read-only database queries with automatic cleanup.
    
    Usage:
        with db_query() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM sites ...")
            results = cur.fetchall()
    """
    conn = get_db_connection()
    if not conn:
        raise DatabaseError("Impossible de se connecter à la base de données")
    
    try:
        yield conn
    except sqlite3.Error as exc:
        current_app.logger.error(f"Erreur de requête DB: {exc}")
        raise DatabaseError(f"Erreur de base de données: {exc}") from exc
    finally:
        conn.close()
