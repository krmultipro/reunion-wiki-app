"""Tests de normalisation et de détection des URL en doublon."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.forms.site_forms import SiteForm
from reunion_wiki.repositories import site_repository
from reunion_wiki.services import site_url_service


class SiteUrlNormalizationTestCase(unittest.TestCase):
    """Vérifie les dix cas critiques de la fiche 3."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "urls-test.db"
        self.original_config = {
            key: app.config.get(key)
            for key in ("TESTING", "WTF_CSRF_ENABLED", "RATELIMIT_ENABLED", "DATABASE_PATH", "MAIL_ENABLED")
        }
        app.config.update(
            TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False,
            DATABASE_PATH=str(self.database_path), MAIL_ENABLED=False,
        )
        self.app_context = app.app_context()
        self.app_context.push()
        self._create_schema()
        self.client = app.test_client()

    def tearDown(self):
        self.app_context.pop()
        app.config.update(self.original_config)
        self.temp_directory.cleanup()

    def _create_schema(self):
        connection = sqlite3.connect(self.database_path)
        try:
            connection.executescript(
                """
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE villes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL UNIQUE,
                    slug TEXT NOT NULL UNIQUE
                );
                CREATE TABLE sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL,
                    lien TEXT NOT NULL, description TEXT, category_id INTEGER,
                    status TEXT DEFAULT 'en_attente', date_ajout DATETIME,
                    submitted_at DATETIME, first_published_at DATETIME,
                    published_at DATETIME, updated_at DATETIME,
                    en_vedette INTEGER DEFAULT 0, click_count INTEGER DEFAULT 0,
                    ville_id INTEGER, location_scope TEXT
                );
                INSERT INTO categories (nom, slug) VALUES ('Services', 'services');
                INSERT INTO villes (nom, slug) VALUES ('Saint-Denis', 'saint-denis');
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _insert_site(self, url, name="Site existant"):
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """INSERT INTO sites
                   (nom, lien, description, category_id, status, date_ajout)
                   VALUES (?, ?, 'Description suffisamment longue.', 1, 'valide', DATETIME('now'))""",
                (name, url),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def _site_count(self):
        connection = sqlite3.connect(self.database_path)
        try:
            return connection.execute("SELECT COUNT(*) FROM sites").fetchone()[0]
        finally:
            connection.close()

    def _validate_public_form_url(self, url):
        with app.test_request_context(
            "/proposer-site", method="POST",
            data={
                "nom": "Annuaire Péi", "ville": "", "lien": url,
                "description": "Un annuaire factuel consacré aux services réunionnais.",
                "categorie": "Services", "honeypot": "",
            },
        ):
            form = SiteForm()
            form.categorie.choices = [("", "Sélectionnez"), ("Services", "Services")]
            form.ville.choices = [("", "Non précisée")]
            return form.validate(), form.lien.data, dict(form.errors)

    def _site_payload(self, url, name="Nouveau site"):
        return {
            "nom": name, "ville": "", "lien": url,
            "description": "Une description neutre et suffisamment longue.",
            "categorie": "Services", "status": "valide", "honeypot": "",
        }

    def test_tc_site_003_01_domain_case_port_and_trailing_slash_are_duplicates(self):
        """TC-SITE-003-01 — Les variantes simples sont un même doublon exact."""
        reference = "https://exemple.re/service"
        self.assertTrue(site_url_service.urls_are_equivalent(reference, "https://EXEMPLE.re:443/service/"))

    def test_tc_site_003_02_http_and_https_are_equivalent(self):
        """TC-SITE-003-02 — HTTP et HTTPS sont comparés comme un même site."""
        self.assertTrue(site_url_service.urls_are_equivalent("http://exemple.re/a", "https://exemple.re/a"))

    def test_tc_site_003_03_tracking_parameters_and_fragment_are_removed(self):
        """TC-SITE-003-03 — Les marqueurs publicitaires et fragments sont retirés."""
        normalized = site_url_service.normalize_site_url(
            "https://Exemple.re/a/?utm_source=facebook&fbclid=abc&utile=oui#contact"
        )
        self.assertEqual(normalized, "https://exemple.re/a?utile=oui")

    def test_tc_site_003_04_functional_parameters_are_preserved(self):
        """TC-SITE-003-04 — Les paramètres fonctionnels restent dans l'URL."""
        url = "https://exemple.re/recherche?categorie=gastro&page=2"
        is_valid, normalized_url, errors = self._validate_public_form_url(url)
        self.assertTrue(is_valid, errors)
        self.assertEqual(normalized_url, url)

    def test_tc_site_003_05_path_case_is_preserved(self):
        """TC-SITE-003-05 — Deux chemins de casse différente restent distincts."""
        self.assertFalse(site_url_service.urls_are_equivalent(
            "https://exemple.re/Service", "https://exemple.re/service"
        ))

    def test_tc_site_003_06_www_redirect_makes_urls_equivalent(self):
        """TC-SITE-003-06 — Une redirection www confirmée établit l'équivalence."""
        self.assertTrue(site_url_service.urls_are_equivalent(
            "https://www.exemple.re/a", "https://exemple.re/a",
            redirected_to="https://exemple.re/a",
        ))

    def test_tc_site_003_07_unrelated_www_variant_only_warns(self):
        """TC-SITE-003-07 — Une variante www indépendante produit un avertissement."""
        self._insert_site("https://exemple.re")
        decision = site_url_service.assess_site_url("https://www.exemple.re")
        self.assertIsNone(decision.duplicate_site_id)
        self.assertIsNotNone(decision.warning)

    def test_tc_site_003_08_distinct_path_on_known_domain_only_warns(self):
        """TC-SITE-003-08 — Un service distinct du même domaine reste admissible."""
        self._insert_site("https://exemple.re/restaurant")
        decision = site_url_service.prepare_site_url("https://exemple.re/transport")
        self.assertIsNotNone(decision.warning)
        self.assertEqual(decision.normalized_url, "https://exemple.re/transport")

    def test_tc_site_003_09_final_https_destination_can_be_kept(self):
        """TC-SITE-003-09 — La destination finale HTTPS peut être conservée."""
        site_id = self._insert_site("http://exemple.re")
        final_url = site_url_service.choose_final_https_url(
            "http://exemple.re", "https://exemple.re/accueil"
        )
        site_repository.record_site_url_history(
            site_id, "http://exemple.re", final_url, "test-admin"
        )
        connection = sqlite3.connect(self.database_path)
        try:
            history = connection.execute(
                "SELECT proposed_url, final_url, admin_username FROM site_url_history"
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(final_url, "https://exemple.re/accueil")
        self.assertEqual(history, ("http://exemple.re", final_url, "test-admin"))

    def test_tc_site_003_10_duplicates_are_blocked_in_all_write_paths(self):
        """TC-SITE-003-10 — Les trois parcours bloquent le même doublon."""
        existing_id = self._insert_site("https://exemple.re/service")
        editable_id = self._insert_site("https://autre.re", name="À modifier")

        public_response = self.client.post(
            "/proposer-site", data=self._site_payload("http://EXEMPLE.re:80/service/", "Public")
        )
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"
        admin_create_response = self.client.post(
            "/admin/propositions/new",
            data=self._site_payload("https://exemple.re/service?utm_source=admin", "Admin"),
        )
        admin_edit_response = self.client.post(
            f"/admin/propositions/{editable_id}/edit",
            data=self._site_payload("https://exemple.re:443/service#edit", "À modifier"),
        )

        connection = sqlite3.connect(self.database_path)
        try:
            editable_url = connection.execute(
                "SELECT lien FROM sites WHERE id=?", (editable_id,)
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(public_response.status_code, 200)
        self.assertEqual(admin_create_response.status_code, 200)
        self.assertEqual(admin_edit_response.status_code, 200)
        self.assertEqual(self._site_count(), 2)
        self.assertEqual(editable_url, "https://autre.re")
        self.assertEqual(existing_id, 1)


if __name__ == "__main__":
    unittest.main()
