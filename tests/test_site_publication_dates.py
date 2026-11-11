"""Fiche 7 : dates métier et republication des sites."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest

from reunion_wiki.app import app
from reunion_wiki.repositories import site_repository
from reunion_wiki.services.site_http_service import ACCESSIBLE, HttpCheckResult
from reunion_wiki.services.site_http_service import MANUAL_REVIEW
from migrate import ensure_site_publication_dates


class SitePublicationDatesTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary.name) / "dates.db"
        self.original_config = {key: app.config.get(key) for key in (
            "TESTING", "WTF_CSRF_ENABLED", "RATELIMIT_ENABLED",
            "DATABASE_PATH", "SITE_HTTP_CHECKER", "SITE_CLOCK",
        )}
        self.now = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
        app.config.update(
            TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False,
            DATABASE_PATH=str(self.database_path), SITE_CLOCK=lambda: self.now,
            SITE_HTTP_CHECKER=lambda url: HttpCheckResult(
                ACCESSIBLE, url, url, 200, "Contrôle simulé accessible."
            ),
        )
        self.context = app.app_context()
        self.context.push()
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY, nom TEXT, slug TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE villes (id INTEGER PRIMARY KEY, nom TEXT, slug TEXT);
                CREATE TABLE sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL,
                    lien TEXT NOT NULL, description TEXT, category_id INTEGER,
                    status TEXT DEFAULT 'en_attente', date_ajout DATETIME,
                    submitted_at DATETIME, first_published_at DATETIME,
                    published_at DATETIME, updated_at DATETIME,
                    en_vedette INTEGER DEFAULT 0, click_count INTEGER DEFAULT 0,
                    ville_id INTEGER, location_scope TEXT
                );
                INSERT INTO categories (id, nom, slug) VALUES (1, 'Services', 'services');
            """)
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

    def tearDown(self):
        self.context.pop()
        app.config.update(self.original_config)
        self.temporary.cleanup()

    def _connect(self):
        db = sqlite3.connect(self.database_path)
        db.row_factory = sqlite3.Row
        return db

    def _row(self, site_id):
        with self._connect() as db:
            return db.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()

    def _site(self, status="en_attente", published_at=None, first_published_at=None,
              clicks=0, name="Site test"):
        with self._connect() as db:
            cursor = db.execute(
                """INSERT INTO sites
                   (nom, lien, description, category_id, status, date_ajout,
                    published_at, first_published_at, click_count)
                   VALUES (?, 'https://example.com', 'Description du site réunionnais.',
                           1, ?, '2026-01-01 10:00:00', ?, ?, ?)""",
                (name, status, published_at, first_published_at, clicks),
            )
            return cursor.lastrowid

    def _moderate(self, site_id, action):
        response = self.client.post(
            f"/admin/propositions/{site_id}",
            data={"site_id": site_id, "action": action, "return_to": "/admin/sites"},
        )
        return self._complete_editorial_review(response) if action == "approve" else response

    def _complete_editorial_review(self, response):
        if "editorial-review" not in response.location:
            return response
        site_id = int(response.location.split("/propositions/")[1].split("/")[0])
        return self.client.post(
            response.location,
            data={
                "reviewed_url": self._row(site_id)["lien"],
                "criterion": "reunion_content",
            },
        )

    def _edit(self, site_id, new_publication=False):
        response = self.client.post(
            f"/admin/propositions/{site_id}/edit",
            data={
                "nom": "Site corrigé", "ville": "", "lien": "https://example.com",
                "description": "Description du site réunionnais corrigée.",
                "categorie": "Services", "status": "valide", "honeypot": "",
                "new_publication": "y" if new_publication else "",
            },
        )
        return self._complete_editorial_review(response)

    def test_tc_site_009_01_submission_sets_only_submitted_at(self):
        site_id = site_repository.create_site(
            "Proposition", None, "https://example.com", "Description de proposition.",
            1, submitted=True,
        )
        row = self._row(site_id)
        self.assertIsNotNone(row["submitted_at"])
        self.assertIsNone(row["first_published_at"])
        self.assertIsNone(row["published_at"])

    def test_tc_site_009_02_first_publication_sets_both_publication_dates(self):
        site_id = self._site()
        self.assertEqual(self._moderate(site_id, "approve").status_code, 302)
        row = self._row(site_id)
        self.assertEqual(row["status"], "valide")
        self.assertEqual(row["first_published_at"], "2026-09-01 12:00:00")
        self.assertEqual(row["published_at"], row["first_published_at"])

    def test_tc_site_009_03_edit_changes_only_updated_at(self):
        site_id = self._site("valide", "2026-01-02 10:00:00", "2026-01-02 10:00:00")
        with self._connect() as db:
            db.execute(
                "UPDATE sites SET updated_at = '2026-01-03 10:00:00' WHERE id = ?",
                (site_id,),
            )
        self._edit(site_id)
        row = self._row(site_id)
        self.assertNotEqual(row["updated_at"], "2026-01-03 10:00:00")
        self.assertEqual(row["first_published_at"], "2026-01-02 10:00:00")
        self.assertEqual(row["published_at"], "2026-01-02 10:00:00")

    def test_tc_site_009_04_normal_republication_keeps_published_at(self):
        site_id = self._site("valide", "2026-01-02 10:00:00", "2026-01-02 10:00:00")
        self._moderate(site_id, "archive")
        self.assertEqual(self._row(site_id)["status"], "archived")
        self.assertNotIn(site_id, [row["id"] for row in site_repository.get_latest_sites()])
        self._moderate(site_id, "approve")
        self.assertEqual(self._row(site_id)["status"], "valide")
        self.assertEqual(self._row(site_id)["published_at"], "2026-01-02 10:00:00")

    def test_tc_site_009_05_explicit_new_publication_refreshes_published_at(self):
        site_id = self._site("archived", "2026-01-02 10:00:00", "2026-01-02 10:00:00")
        html = self.client.get(f"/admin/propositions/{site_id}/edit").get_data(as_text=True)
        self.assertIn("Traiter comme une nouvelle publication", html)
        self.assertIn('class="admin-form__checkbox"', html)
        self.assertNotIn('name="new_publication" checked', html)
        self._edit(site_id, new_publication=True)
        row = self._row(site_id)
        self.assertEqual(row["status"], "valide")
        self.assertEqual(row["published_at"], "2026-09-01 12:00:00")
        self.assertEqual(row["first_published_at"], "2026-01-02 10:00:00")

    def test_tc_site_009_06_new_publication_preserves_clicks_and_history(self):
        site_id = self._site(
            "archived", "2026-01-02 10:00:00", "2026-01-02 10:00:00", 42
        )
        with self._connect() as db:
            db.execute(
                """CREATE TABLE site_url_history (
                    id INTEGER PRIMARY KEY, site_id INTEGER, proposed_url TEXT
                )"""
            )
            db.execute(
                "INSERT INTO site_url_history (site_id, proposed_url) VALUES (?, ?)",
                (site_id, "https://old.example.com"),
            )
        self._edit(site_id, new_publication=True)
        self.assertEqual(self._row(site_id)["click_count"], 42)
        with self._connect() as db:
            event = db.execute(
                "SELECT * FROM site_publication_history WHERE site_id = ?", (site_id,)
            ).fetchone()
            previous_history = db.execute(
                "SELECT proposed_url FROM site_url_history WHERE site_id = ?",
                (site_id,),
            ).fetchone()
        self.assertEqual(event["action"], "new_publication")
        self.assertEqual(event["admin_username"], "test-admin")
        self.assertEqual(event["published_at"], "2026-09-01 12:00:00")
        self.assertEqual(previous_history["proposed_url"], "https://old.example.com")

    def test_tc_site_009_07_latest_sites_are_sorted_only_by_published_at(self):
        old = self._site("valide", "2026-02-01 10:00:00", name="Ancien")
        recent = self._site("valide", "2026-03-01 10:00:00", name="Récent")
        with self._connect() as db:
            db.execute(
                "UPDATE sites SET date_ajout = '2026-12-01 10:00:00' WHERE id = ?",
                (old,),
            )
        self.assertEqual(
            [row["id"] for row in site_repository.get_latest_sites()], [recent, old]
        )

    def test_manual_review_preserves_explicit_new_publication(self):
        site_id = self._site("archived", "2026-01-02 10:00:00", "2026-01-02 10:00:00")
        app.config["SITE_HTTP_CHECKER"] = lambda url: HttpCheckResult(
            MANUAL_REVIEW, url, url, 403, "Contrôle humain requis."
        )
        response = self._edit(site_id, new_publication=True)
        self.assertEqual(response.status_code, 302)
        self.assertIn("http-review", response.location)
        self.assertEqual(self._row(site_id)["status"], "archived")
        check_id = int(response.location.rstrip("/").split("/")[-1])
        confirmed = self.client.post(
            response.location,
            data={
                "site_id": site_id, "check_id": check_id,
                "note": "Site consulté sans compte, contenu vérifié.",
            },
        )
        self.assertEqual(confirmed.status_code, 302)
        self.assertEqual(self._row(site_id)["published_at"], "2026-09-01 12:00:00")
        with self._connect() as db:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM site_publication_history WHERE site_id = ?",
                    (site_id,),
                ).fetchone()[0], 1,
            )

    def test_migration_marks_legacy_dates_as_inferred_and_is_idempotent(self):
        legacy = self._site("valide")
        with self._connect() as db:
            # Simule une base antérieure à la fiche 7, sans toucher à la base locale.
            db.execute("ALTER TABLE sites DROP COLUMN submitted_at")
            db.execute("ALTER TABLE sites DROP COLUMN first_published_at")
            db.execute("ALTER TABLE sites DROP COLUMN published_at")
            db.execute("ALTER TABLE sites DROP COLUMN updated_at")
            ensure_site_publication_dates(db.cursor())
            ensure_site_publication_dates(db.cursor())
            row = db.execute(
                """SELECT s.first_published_at, s.published_at,
                          i.source_column, i.inferred_published_at
                   FROM sites s JOIN site_publication_date_inference i
                     ON i.site_id = s.id WHERE s.id = ?""",
                (legacy,),
            ).fetchone()
        self.assertIsNone(row["first_published_at"])
        self.assertEqual(row["published_at"], "2026-01-01 10:00:00")
        self.assertEqual(row["source_column"], "date_ajout")
        self.assertEqual(row["inferred_published_at"], row["published_at"])


if __name__ == "__main__":
    unittest.main()
