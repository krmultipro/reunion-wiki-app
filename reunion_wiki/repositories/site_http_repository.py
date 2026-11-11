# -*- coding: utf-8 -*-
"""Persistance des contrôles HTTP et des validations manuelles."""

from ..db import get_db_connection
from . import site_repository


def _ensure_table(connection):
    connection.execute(
        """CREATE TABLE IF NOT EXISTS site_http_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            requested_url TEXT NOT NULL,
            final_url TEXT NOT NULL,
            status_code INTEGER,
            decision TEXT NOT NULL,
            reason TEXT NOT NULL,
            redirect_count INTEGER NOT NULL DEFAULT 0,
            checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            checked_by TEXT NOT NULL,
            manually_approved_at DATETIME,
            manually_approved_by TEXT,
            manual_note TEXT
        )"""
    )
    connection.execute(
        """CREATE INDEX IF NOT EXISTS idx_site_http_checks_site_id
           ON site_http_checks(site_id, checked_at DESC)"""
    )
    if "new_publication" not in {
        row[1] for row in connection.execute("PRAGMA table_info(site_http_checks)")
    }:
        connection.execute(
            "ALTER TABLE site_http_checks ADD COLUMN new_publication INTEGER NOT NULL DEFAULT 0"
        )


def record_check(site_id, result, admin_username, new_publication=False):
    """Enregistre le résultat d'une tentative de publication."""
    connection = get_db_connection()
    try:
        _ensure_table(connection)
        cursor = connection.execute(
            """INSERT INTO site_http_checks (
                site_id, requested_url, final_url, status_code, decision,
                reason, redirect_count, checked_by, new_publication
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                site_id,
                result.requested_url,
                result.final_url,
                result.status_code,
                result.decision,
                result.reason,
                result.redirect_count,
                admin_username,
                1 if new_publication else 0,
            ),
        )
        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_manual_review(check_id, site_id):
    """Retourne la revue courante si aucun contrôle plus récent ne la remplace."""
    connection = get_db_connection()
    try:
        _ensure_table(connection)
        return connection.execute(
            """SELECT hc.*, s.nom AS site_name, s.lien AS current_url,
                      s.status AS site_status
               FROM site_http_checks hc
               JOIN sites s ON s.id = hc.site_id
               WHERE hc.id = ? AND hc.site_id = ?
                 AND hc.decision = 'manual_review'
                 AND hc.manually_approved_at IS NULL
                 AND hc.requested_url = s.lien
                 AND hc.id = (
                     SELECT MAX(latest.id) FROM site_http_checks latest
                     WHERE latest.site_id = hc.site_id
                 )
                 AND s.status IN ('draft', 'en_attente', 'archived')""",
            (check_id, site_id),
        ).fetchone()
    finally:
        connection.close()


def confirm_manual_review(check_id, site_id, admin_username, note, published_at, connection=None):
    """Consomme la dernière revue et publie sous le même verrou d'écriture."""
    owns_connection = connection is None
    connection = connection if connection is not None else get_db_connection()
    try:
        if not connection.in_transaction:
            connection.execute("BEGIN IMMEDIATE")
        _ensure_table(connection)
        check = connection.execute(
            """SELECT hc.requested_url, hc.new_publication, s.lien AS current_url,
                      s.status AS site_status
               FROM site_http_checks hc
               JOIN sites s ON s.id = hc.site_id
               WHERE hc.id = ? AND hc.site_id = ?
                 AND hc.decision = 'manual_review'
                 AND hc.manually_approved_at IS NULL
                 AND hc.id = (
                     SELECT MAX(latest.id) FROM site_http_checks latest
                     WHERE latest.site_id = hc.site_id
                 )
                 AND s.status IN ('draft', 'en_attente', 'archived')""",
            (check_id, site_id),
        ).fetchone()
        if not check or check["requested_url"] != check["current_url"]:
            connection.rollback()
            return False
        if check["new_publication"] and check["site_status"] != "archived":
            connection.rollback()
            return False

        cursor = connection.execute(
            """UPDATE site_http_checks
               SET manually_approved_at = CURRENT_TIMESTAMP,
                   manually_approved_by = ?, manual_note = ?
               WHERE id = ? AND manually_approved_at IS NULL""",
            (admin_username, note, check_id),
        )
        if cursor.rowcount != 1:
            connection.rollback()
            return False

        if not site_repository.apply_publication(
            connection, site_id, admin_username, published_at,
            new_publication=bool(check["new_publication"]),
        ):
            connection.rollback()
            return False
        if owns_connection:
            connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        if owns_connection:
            connection.close()
