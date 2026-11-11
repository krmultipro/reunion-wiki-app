"""Private editorial decisions made before publishing a site."""

from ..db import get_db_connection


APPROVED_CRITERIA = (
    "local_organization",
    "reunion_content",
    "national_local_offer",
    "useful_resource",
)


def ensure_table(connection):
    connection.execute(
        """CREATE TABLE IF NOT EXISTS site_editorial_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            reviewed_url TEXT NOT NULL,
            criterion TEXT NOT NULL,
            note TEXT,
            evidence_url TEXT,
            reviewed_by TEXT NOT NULL,
            reviewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    connection.execute(
        """CREATE INDEX IF NOT EXISTS idx_site_editorial_reviews_site
           ON site_editorial_reviews(site_id, id DESC)"""
    )


def record_review(site_id, reviewed_url, criterion, note, evidence_url, admin_username):
    """Record the latest human decision only if the reviewed URL is still current."""
    connection = get_db_connection()
    try:
        ensure_table(connection)
        row = connection.execute(
            "SELECT lien, status FROM sites WHERE id = ?", (site_id,)
        ).fetchone()
        if not row or row["lien"] != reviewed_url or row["status"] not in {"draft", "en_attente", "archived"}:
            connection.rollback()
            return False
        connection.execute(
            """INSERT INTO site_editorial_reviews
               (site_id, reviewed_url, criterion, note, evidence_url, reviewed_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (site_id, reviewed_url, criterion, note or None, evidence_url or None, admin_username),
        )
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def latest_approval_matches(connection, site_id, current_url):
    """A rejection or URL change invalidates every earlier approval."""
    ensure_table(connection)
    row = connection.execute(
        """SELECT reviewed_url, criterion FROM site_editorial_reviews
           WHERE site_id = ? ORDER BY id DESC LIMIT 1""",
        (site_id,),
    ).fetchone()
    return bool(
        row and row["reviewed_url"] == current_url
        and row["criterion"] in APPROVED_CRITERIA
    )


def latest_approval_matches_for_site(site_id, current_url):
    connection = get_db_connection()
    try:
        return latest_approval_matches(connection, site_id, current_url)
    finally:
        connection.close()
