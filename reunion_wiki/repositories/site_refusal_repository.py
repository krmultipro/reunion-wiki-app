"""Private refusal history, written in the caller's site transaction."""

from ..db import get_db_connection


REASON_CHOICES = [
    ("", "Choisir un motif de refus"),
    ("duplicate", "Doublon"),
    ("no_reunion_link", "Absence de lien avec La Réunion"),
    ("inaccessible", "Site inaccessible"),
    ("prohibited_content", "Contenu interdit ou dangereux"),
    ("insufficient_information", "Informations insuffisantes"),
    ("editorial_scope", "Hors ligne éditoriale"),
]
REASON_LABELS = dict(REASON_CHOICES[1:])


class InvalidRefusalReason(ValueError):
    """A new refusal requires one of the documented reasons."""


def validate_reason(reason):
    """Return a stable known reason or reject the new refusal."""
    if reason not in REASON_LABELS:
        raise InvalidRefusalReason("Choisissez un motif de refus valide.")
    return reason


def ensure_table(connection):
    """Create the private history without committing or inventing old decisions."""
    connection.execute(
        """CREATE TABLE IF NOT EXISTS site_refusal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            reason TEXT NOT NULL CHECK(reason IN (
                'duplicate', 'no_reunion_link', 'inaccessible',
                'prohibited_content', 'insufficient_information', 'editorial_scope'
            )),
            admin_username TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_site_refusal_history_site ON site_refusal_history(site_id, id DESC)"
    )


def record_refusal(connection, site_id, reason, admin_username):
    """Append a refusal inside the caller's transaction, never commit here."""
    validated = validate_reason(reason)
    ensure_table(connection)
    connection.execute(
        "INSERT INTO site_refusal_history (site_id, reason, admin_username) VALUES (?, ?, ?)",
        (site_id, validated, admin_username),
    )


def get_latest_refusals(site_ids):
    """Return the latest private decision for each requested admin-visible site."""
    ids = tuple(site_ids)
    if not ids:
        return {}
    connection = get_db_connection()
    try:
        if not connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='site_refusal_history'"
        ).fetchone():
            return {}
        placeholders = ",".join("?" for _ in ids)
        rows = connection.execute(
            f"""SELECT h.* FROM site_refusal_history h
                JOIN (SELECT site_id, MAX(id) AS latest_id FROM site_refusal_history
                      WHERE site_id IN ({placeholders}) GROUP BY site_id) latest
                ON h.id = latest.latest_id""",
            ids,
        ).fetchall()
        return {row["site_id"]: {**dict(row), "label": REASON_LABELS[row["reason"]]} for row in rows}
    finally:
        connection.close()


def get_latest_refusal(site_id):
    """Return one private decision for the authenticated editing screen."""
    return get_latest_refusals((site_id,)).get(site_id)
