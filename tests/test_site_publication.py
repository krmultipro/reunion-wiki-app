"""Tests automatisés de l'admissibilité et de la publication des sites."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.forms.site_forms import SiteForm
from reunion_wiki.repositories import site_repository
from reunion_wiki.services.site_http_service import ACCESSIBLE, HttpCheckResult


class SitePublicationTestCase(unittest.TestCase):
    """Vérifie les cas critiques de la fiche de test 2 des sites."""

    def setUp(self):
        """Crée une base SQLite isolée et configure l'application en test."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "reunion-wiki-test.db"
        self.original_config = {
            key: app.config.get(key)
            for key in (
                "TESTING",
                "WTF_CSRF_ENABLED",
                "RATELIMIT_ENABLED",
                "DATABASE_PATH",
                "MAIL_ENABLED",
                "SITE_HTTP_CHECKER",
            )
        }

        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
            DATABASE_PATH=str(self.database_path),
            MAIL_ENABLED=False,
            SITE_HTTP_CHECKER=lambda url: HttpCheckResult(
                ACCESSIBLE,
                url,
                url,
                200,
                "Réponse simulée accessible.",
            ),
        )

        self.app_context = app.app_context()
        self.app_context.push()
        self._create_schema()
        self.client = app.test_client()

    def tearDown(self):
        """Supprime la base SQLite temporaire après chaque test."""
        self.app_context.pop()
        app.config.update(self.original_config)
        self.temp_directory.cleanup()

    def _create_schema(self):
        """Crée le sous-ensemble du schéma nécessaire aux tests des sites."""
        connection = sqlite3.connect(self.database_path)
        try:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE villes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE
                );

                CREATE TABLE sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    lien TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER,
                    status TEXT DEFAULT 'en_attente',
                    date_ajout DATETIME,
                    submitted_at DATETIME,
                    first_published_at DATETIME,
                    published_at DATETIME,
                    updated_at DATETIME,
                    en_vedette INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    ville_id INTEGER,
                    location_scope TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories(id),
                    FOREIGN KEY (ville_id) REFERENCES villes(id)
                );

                INSERT INTO categories (nom, slug)
                VALUES ('Gastronomie', 'gastronomie');

                INSERT INTO villes (nom, slug)
                VALUES ('Saint-Denis', 'saint-denis');
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _validate_public_form(self, **overrides):
        """Valide un formulaire public et renvoie son résultat et ses erreurs."""
        data = {
            "nom": "Cuisine Péi",
            "ville": "",
            "lien": "https://cuisine-pei.example",
            "description": "Un site réunionnais consacré à la cuisine locale.",
            "categorie": "Gastronomie",
            "honeypot": "",
        }
        data.update(overrides)

        with app.test_request_context(
            "/proposer-site",
            method="POST",
            data=data,
        ):
            form = SiteForm()
            form.categorie.choices = [
                ("", "Sélectionnez une catégorie"),
                ("Gastronomie", "Gastronomie"),
            ]
            form.ville.choices = [
                ("", "Non précisée"),
                ("Saint-Denis", "Saint-Denis"),
            ]
            return form.validate(), dict(form.errors)

    def _fetch_one_site(self):
        """Retourne l'unique site de la base de test, ou ``None``."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            return connection.execute(
                """
                SELECT s.*, c.nom AS categorie
                FROM sites s
                LEFT JOIN categories c ON c.id = s.category_id
                ORDER BY s.id ASC
                LIMIT 1
                """
            ).fetchone()
        finally:
            connection.close()

    def test_tc_site_pub_01_missing_name_is_rejected(self):
        """TC-SITE-PUB-01 — Le nom est obligatoire."""
        is_valid, errors = self._validate_public_form(nom="")

        self.assertFalse(is_valid)
        self.assertIn("nom", errors)

    def test_tc_site_pub_02_invalid_url_is_rejected(self):
        """TC-SITE-PUB-02 — Une URL syntaxiquement invalide est refusée."""
        is_valid, errors = self._validate_public_form(lien="http://")

        self.assertFalse(is_valid)
        self.assertIn("lien", errors)

    def test_tc_site_pub_03_missing_description_is_rejected(self):
        """TC-SITE-PUB-03 — La description est obligatoire."""
        is_valid, errors = self._validate_public_form(description="")

        self.assertFalse(is_valid)
        self.assertIn("description", errors)

    def test_tc_site_pub_04_missing_category_is_rejected(self):
        """TC-SITE-PUB-04 — La catégorie principale est obligatoire."""
        is_valid, errors = self._validate_public_form(categorie="")

        self.assertFalse(is_valid)
        self.assertIn("categorie", errors)

    def test_tc_site_pub_05_optional_fields_allow_pending_submission(self):
        """TC-SITE-PUB-05 — Les champs facultatifs vides ne bloquent pas l'envoi."""
        response = self.client.post(
            "/proposer-site",
            data={
                "nom": "Cuisine Péi",
                "ville": "",
                "lien": "https://cuisine-pei.example",
                "description": "Un site réunionnais consacré à la cuisine locale.",
                "categorie": "Gastronomie",
                "honeypot": "",
            },
        )

        site = self._fetch_one_site()
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(site)
        self.assertEqual(site["status"], "en_attente")
        self.assertIsNone(site["ville_id"])

    def test_tc_site_pub_06_national_site_without_local_link_is_rejected(self):
        """TC-SITE-PUB-06 — Une décision négative empêche la publication."""
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"
        response = self.client.post(
            "/admin/propositions/new",
            data={
                "nom": "Service national", "ville": "", "lien": "https://national.example",
                "description": "Un service national sans offre locale particulière.",
                "categorie": "Gastronomie", "status": "valide", "honeypot": "",
            },
        )
        site = self._fetch_one_site()
        self.assertEqual(site["status"], "draft")
        review_page = self.client.get(response.location)
        self.assertEqual(review_page.status_code, 200)
        self.assertIn("Vérifier le lien avec La Réunion", review_page.get_data(as_text=True))
        rejected = self.client.post(
            response.location,
            data={"reviewed_url": site["lien"], "criterion": "no_link"},
        )
        self.assertEqual(rejected.status_code, 302)
        self.assertEqual(self._fetch_one_site()["status"], "draft")

    def test_editorial_approval_is_required_at_repository_boundary(self):
        """No route or HTTP review can bypass the central publication guard."""
        with self.assertRaises(ValueError):
            site_repository.create_site(
                "Site direct", None, "https://direct.example",
                "Description publique neutre et suffisante.", 1, status="valide",
            )
        site_id = site_repository.create_site(
            "Site test", None, "https://site-test.example",
            "Description publique neutre et suffisante.", 1, status="en_attente",
        )
        with self.assertRaises(ValueError):
            site_repository.update_site_status(site_id, "valide")
        self.assertFalse(site_repository.publish_site(site_id, "test-admin", "2026-09-22 10:00:00"))
        self.assertEqual(self._fetch_one_site()["status"], "en_attente")

    def test_editorial_decision_is_url_bound_and_latest_decision_wins(self):
        """A changed URL or a later refusal invalidates an earlier approval."""
        from reunion_wiki.repositories import site_editorial_repository

        site_id = site_repository.create_site(
            "Site test", None, "https://site-test.example",
            "Description publique neutre et suffisante.", 1, status="en_attente",
        )
        self.assertTrue(site_editorial_repository.record_review(
            site_id, "https://site-test.example", "reunion_content", None, None, "test-admin",
        ))
        site_repository.update_site(
            site_id, "Site test", None, "https://changed.example",
            "Description publique neutre et suffisante.", 1, "en_attente", 0,
        )
        self.assertFalse(site_repository.publish_site(site_id, "test-admin", "2026-09-22 10:00:00"))
        self.assertFalse(site_editorial_repository.record_review(
            site_id, "https://site-test.example", "reunion_content", None, None, "test-admin",
        ))
        site_repository.update_site(
            site_id, "Site test", None, "https://site-test.example",
            "Description publique neutre et suffisante.", 1, "en_attente", 0,
        )
        self.assertFalse(site_repository.publish_site(site_id, "test-admin", "2026-09-22 10:00:00"))
        self.assertTrue(site_editorial_repository.record_review(
            site_id, "https://site-test.example", "reunion_content", None, None, "test-admin",
        ))
        self.assertTrue(site_editorial_repository.record_review(
            site_id, "https://site-test.example", "no_link", None, None, "test-admin",
        ))
        self.assertFalse(site_repository.publish_site(site_id, "test-admin", "2026-09-22 10:00:00"))

    def test_tc_site_pub_07_valid_admin_site_can_be_published(self):
        """TC-SITE-PUB-07 — Un administrateur peut publier un site valide."""
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

        response = self.client.post(
            "/admin/propositions/new",
            data={
                "nom": "Cuisine Péi",
                "ville": "",
                "lien": "https://cuisine-pei.example",
                "description": "Un site réunionnais consacré à la cuisine locale.",
                "categorie": "Gastronomie",
                "status": "valide",
                "honeypot": "",
            },
        )

        site = self._fetch_one_site()
        self.assertEqual(site["status"], "draft")
        response = self.client.post(
            response.location,
            data={"reviewed_url": site["lien"], "criterion": "reunion_content"},
        )

        site = self._fetch_one_site()
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(site)
        self.assertEqual(site["status"], "valide")
        self.assertEqual(site["categorie"], "Gastronomie")
        connection = sqlite3.connect(self.database_path)
        try:
            review = connection.execute(
                """SELECT reviewed_url, criterion, reviewed_by, reviewed_at, note, evidence_url
                   FROM site_editorial_reviews WHERE site_id = ?""",
                (site["id"],),
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(review[0], site["lien"])
        self.assertEqual(review[1:3], ("reunion_content", "test-admin"))
        self.assertIsNotNone(review[3])
        self.assertEqual(review[4:], (None, None))

    def test_tc_site_pub_08_manifestly_dangerous_description_is_rejected(self):
        """TC-SITE-PUB-08 — Un motif dangereux explicite est refusé."""
        is_valid, errors = self._validate_public_form(
            description="javascript:alert('contenu dangereux')",
        )

        self.assertFalse(is_valid)
        self.assertIn("description", errors)


if __name__ == "__main__":
    unittest.main()
