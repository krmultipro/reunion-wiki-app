"""Tests automatisés du contrôle d'accessibilité HTTP des sites."""

import re
import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.services import site_http_service


def _public_resolver(_hostname):
    return {"1.1.1.1"}


class SequenceTransport:
    """Transport déterministe qui ne réalise aucune requête réseau."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.urls = []

    def request(self, url, timeout):
        self.urls.append(url)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _response(status, location=None):
    headers = {} if location is None else {"Location": location}
    return site_http_service.HttpResponse(status, headers)


class SiteHttpAccessibilityTestCase(unittest.TestCase):
    """Vérifie les cas critiques de la fiche de test 4 des sites."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "http-checks.db"
        self.original_config = {
            key: app.config.get(key)
            for key in (
                "TESTING",
                "WTF_CSRF_ENABLED",
                "RATELIMIT_ENABLED",
                "DATABASE_PATH",
                "SITE_HTTP_CHECKER",
            )
        }
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
            DATABASE_PATH=str(self.database_path),
            SITE_HTTP_CHECKER=None,
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
                    id INTEGER PRIMARY KEY, nom TEXT NOT NULL, slug TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE villes (
                    id INTEGER PRIMARY KEY, nom TEXT NOT NULL, slug TEXT NOT NULL
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
                    location_scope TEXT
                );
                INSERT INTO categories (id, nom, slug)
                VALUES (1, 'Services', 'services');
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _insert_pending_site(self, url="https://example.com"):
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """INSERT INTO sites
                   (nom, lien, description, category_id, status, date_ajout)
                   VALUES ('Site à contrôler', ?, 'Description neutre.', 1,
                           'en_attente', DATETIME('now'))""",
                (url,),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def _fetch_one(self, query, params=()):
        connection = sqlite3.connect(self.database_path)
        try:
            return connection.execute(query, params).fetchone()
        finally:
            connection.close()

    def _check(self, outcomes, url="https://example.com"):
        return site_http_service.check_url(
            url,
            transport=SequenceTransport(outcomes),
            resolver=_public_resolver,
        )

    def test_tc_site_http_01_final_2xx_is_accessible(self):
        """TC-SITE-HTTP-01 — Une réponse finale 2xx confirme l'accessibilité."""
        for status in (200, 204, 299):
            with self.subTest(status=status):
                result = self._check([_response(status)])
                self.assertEqual(result.decision, site_http_service.ACCESSIBLE)
                self.assertEqual(result.status_code, status)

        site_id = self._insert_pending_site()
        app.config["SITE_HTTP_CHECKER"] = lambda url: self._check([_response(200)], url)
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"
        response = self.client.post(
            f"/admin/propositions/{site_id}/edit",
            data={
                "nom": "Site accessible",
                "ville": "",
                "lien": "https://example.com",
                "description": "Description publique neutre et suffisamment longue.",
                "categorie": "Services",
                "status": "valide",
                "honeypot": "",
            },
        )

        response = self.client.post(
            response.location,
            data={"reviewed_url": "https://example.com", "criterion": "reunion_content"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self._fetch_one("SELECT status FROM sites WHERE id = ?", (site_id,))[0],
            "valide",
        )

    def test_tc_site_http_02_up_to_five_redirects_then_2xx_succeeds(self):
        """TC-SITE-HTTP-02 — Une à cinq redirections vers un 2xx réussissent."""
        outcomes = [
            _response(302, f"https://example.com/{index}")
            for index in range(1, 6)
        ] + [_response(200)]

        result = self._check(outcomes)

        self.assertEqual(result.decision, site_http_service.ACCESSIBLE)
        self.assertEqual(result.redirect_count, 5)
        self.assertEqual(result.final_url, "https://example.com/5")

    def test_tc_site_http_03_too_many_redirects_or_loop_fails(self):
        """TC-SITE-HTTP-03 — Les boucles et redirections excessives échouent."""
        too_many = self._check(
            [
                _response(302, f"https://example.com/{index}")
                for index in range(1, 7)
            ]
        )
        loop = self._check(
            [
                _response(302, "https://example.com/b"),
                _response(302, "https://example.com"),
            ]
        )
        private_transport = SequenceTransport([_response(200)])
        private = site_http_service.check_url(
            "http://127.0.0.1/admin",
            transport=private_transport,
            resolver=lambda _hostname: {"127.0.0.1"},
        )

        self.assertEqual(too_many.decision, site_http_service.BLOCKED)
        self.assertEqual(loop.decision, site_http_service.BLOCKED)
        self.assertEqual(private.decision, site_http_service.BLOCKED)
        self.assertEqual(private_transport.urls, [])

    def test_tc_site_http_04_not_found_or_gone_is_inaccessible(self):
        """TC-SITE-HTTP-04 — Les réponses 404 et 410 rendent le site inaccessible."""
        for status in (404, 410):
            with self.subTest(status=status):
                result = self._check([_response(status)])
                self.assertEqual(result.decision, site_http_service.INACCESSIBLE)

    def test_tc_site_http_05_auth_errors_require_manual_review(self):
        """TC-SITE-HTTP-05 — Les réponses 401 et 403 demandent une revue humaine."""
        for status in (401, 403):
            with self.subTest(status=status):
                result = self._check([_response(status)])
                self.assertEqual(result.decision, site_http_service.MANUAL_REVIEW)

        site_id = self._insert_pending_site()
        app.config["SITE_HTTP_CHECKER"] = lambda url: self._check([_response(403)], url)
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

        blocked = self.client.post(
            f"/admin/propositions/{site_id}",
            data={"site_id": site_id, "action": "approve", "return_to": "/admin"},
        )
        blocked = self.client.post(
            blocked.location,
            data={"reviewed_url": "https://example.com", "criterion": "reunion_content"},
        )
        self.assertEqual(blocked.status_code, 302)
        match = re.search(r"/http-review/(\d+)$", blocked.location)
        self.assertIsNotNone(match)
        check_id = int(match.group(1))

        review_page = self.client.get(blocked.location)
        self.assertIn("Vérification manuelle requise", review_page.get_data(as_text=True))
        confirmed = self.client.post(
            blocked.location,
            data={
                "site_id": site_id,
                "check_id": check_id,
                "note": "Site ouvert en navigation privée et contenu public vérifié.",
            },
        )

        self.assertEqual(confirmed.status_code, 302)
        self.assertEqual(
            self._fetch_one("SELECT status FROM sites WHERE id = ?", (site_id,))[0],
            "valide",
        )
        audit = self._fetch_one(
            """SELECT manually_approved_by, manual_note
               FROM site_http_checks WHERE id = ?""",
            (check_id,),
        )
        self.assertEqual(audit[0], "test-admin")
        self.assertIn("navigation privée", audit[1])

        second_site_id = self._insert_pending_site("https://example.com/second")
        second_blocked = self.client.post(
            f"/admin/propositions/{second_site_id}",
            data={
                "site_id": second_site_id,
                "action": "approve",
                "return_to": "/admin",
            },
        )
        second_blocked = self.client.post(
            second_blocked.location,
            data={"reviewed_url": "https://example.com/second", "criterion": "reunion_content"},
        )
        second_check_id = int(
            re.search(r"/http-review/(\d+)$", second_blocked.location).group(1)
        )
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE sites SET lien = ? WHERE id = ?",
                ("https://example.com/changed", second_site_id),
            )
            connection.commit()
        finally:
            connection.close()

        invalidated = self.client.post(
            second_blocked.location,
            data={
                "site_id": second_site_id,
                "check_id": second_check_id,
                "note": "Cette ancienne confirmation ne doit plus être utilisable.",
            },
        )
        self.assertEqual(invalidated.status_code, 302)
        self.assertEqual(
            self._fetch_one(
                "SELECT status FROM sites WHERE id = ?",
                (second_site_id,),
            )[0],
            "en_attente",
        )
        self.assertIsNone(
            self._fetch_one(
                """SELECT manually_approved_at FROM site_http_checks
                   WHERE id = ?""",
                (second_check_id,),
            )[0]
        )

    def test_tc_site_http_06_temporary_errors_keep_site_unpublished(self):
        """TC-SITE-HTTP-06 — Les erreurs temporaires conservent le statut privé."""
        for outcome in (
            _response(429),
            _response(500),
            site_http_service.HttpTimeoutError("timeout"),
        ):
            with self.subTest(outcome=outcome):
                result = self._check([outcome])
                self.assertEqual(result.decision, site_http_service.TEMPORARY_ERROR)

        app.config["SITE_HTTP_CHECKER"] = lambda url: self._check([_response(503)], url)
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"
        response = self.client.post(
            "/admin/propositions/new",
            data={
                "nom": "Site temporairement indisponible",
                "ville": "",
                "lien": "https://example.com/temporary",
                "description": "Description publique neutre et suffisamment longue.",
                "categorie": "Services",
                "status": "valide",
                "honeypot": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self._fetch_one("SELECT status FROM sites ORDER BY id DESC LIMIT 1")[0],
            "draft",
        )

    def test_tc_site_http_07_invalid_certificate_blocks_publication(self):
        """TC-SITE-HTTP-07 — Un certificat invalide bloque la publication."""
        result = self._check(
            [site_http_service.InvalidCertificateError("invalid certificate")]
        )

        self.assertEqual(result.decision, site_http_service.BLOCKED)
        self.assertIn("Certificat", result.reason)


if __name__ == "__main__":
    unittest.main()
