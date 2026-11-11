"""Régressions COR-SITE-01 : fraîcheur et consommation des revues HTTP."""

import sqlite3
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from tests import test_site_http_accessibility as http_fixture
from reunion_wiki.app import app
from reunion_wiki.repositories import site_http_repository
from reunion_wiki.services import site_publication_service
from reunion_wiki.services.site_http_service import (
    HttpCheckResult, MANUAL_REVIEW, TEMPORARY_ERROR,
)


class SiteHttpReviewFreshnessTestCase(unittest.TestCase):
    """Vérifie les décisions sur SQLite temporaire, sans accès réseau."""

    setUp = http_fixture.SiteHttpAccessibilityTestCase.setUp
    tearDown = http_fixture.SiteHttpAccessibilityTestCase.tearDown
    _create_schema = http_fixture.SiteHttpAccessibilityTestCase._create_schema
    _insert_pending_site = http_fixture.SiteHttpAccessibilityTestCase._insert_pending_site
    _fetch_one = http_fixture.SiteHttpAccessibilityTestCase._fetch_one

    def _attempt(self, site_id, status_code):
        """Exécute la revue éditoriale et un contrôle HTTP déterministe."""
        decision = MANUAL_REVIEW if status_code in (401, 403) else TEMPORARY_ERROR
        app.config["SITE_HTTP_CHECKER"] = lambda url: HttpCheckResult(
            decision, url, url, status_code, "Contrôle HTTP simulé.",
        )
        url = self._fetch_one("SELECT lien FROM sites WHERE id = ?", (site_id,))[0]
        return site_publication_service.review_and_attempt_publication(
            site_id, url, "reunion_content", None, None, "test-admin",
        )

    def _confirm(self, site_id, check_id):
        """Confirme une revue avec une note humaine et un auteur identifiés."""
        return site_publication_service.confirm_manual_publication(
            site_id, check_id, "test-admin", "Site ouvert en navigation privée.",
        )

    def test_old_403_cannot_publish_after_a_new_503(self):
        """COR01-OLD — Un contrôle temporaire remplace une ancienne revue."""
        site_id = self._insert_pending_site()
        first = self._attempt(site_id, 403)
        self._attempt(site_id, 503)

        self.assertFalse(self._confirm(site_id, first.manual_check_id))
        self.assertEqual(self._fetch_one(
            "SELECT status, published_at FROM sites WHERE id = ?", (site_id,),
        ), ("en_attente", None))
        self.assertEqual(self._fetch_one(
            "SELECT COUNT(*), COUNT(manually_approved_at) FROM site_http_checks WHERE site_id = ?",
            (site_id,),
        ), (2, 0))

    def test_only_latest_403_can_be_confirmed_once(self):
        """COR01-LATEST — Le nouveau contrôle remplace l'ancien sans le perdre."""
        site_id = self._insert_pending_site()
        first = self._attempt(site_id, 403)
        latest = self._attempt(site_id, 403)

        self.assertFalse(self._confirm(site_id, first.manual_check_id))
        self.assertTrue(self._confirm(site_id, latest.manual_check_id))
        self.assertEqual(self._fetch_one(
            "SELECT status FROM sites WHERE id = ?", (site_id,),
        ), ("valide",))
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("UPDATE sites SET status = 'archived' WHERE id = ?", (site_id,))
        self.assertFalse(self._confirm(site_id, latest.manual_check_id))
        self.assertEqual(self._fetch_one(
            "SELECT COUNT(*), COUNT(manually_approved_at) FROM site_http_checks WHERE site_id = ?",
            (site_id,),
        ), (2, 1))

    def test_obsolete_review_is_no_longer_offered(self):
        """La lecture du formulaire ne propose que le dernier contrôle."""
        site_id = self._insert_pending_site()
        first = self._attempt(site_id, 403)
        self.assertIsNotNone(site_http_repository.get_manual_review(first.manual_check_id, site_id))
        latest = self._attempt(site_id, 403)
        self.assertIsNone(site_http_repository.get_manual_review(first.manual_check_id, site_id))
        self.assertIsNotNone(site_http_repository.get_manual_review(latest.manual_check_id, site_id))

    def test_failed_publication_does_not_consume_manual_review(self):
        """Le refus transactionnel de publication annule aussi la confirmation."""
        site_id = self._insert_pending_site()
        latest = self._attempt(site_id, 403)
        with patch.object(site_http_repository.site_repository, "apply_publication", return_value=False):
            self.assertFalse(self._confirm(site_id, latest.manual_check_id))
        self.assertEqual(self._fetch_one(
            "SELECT manually_approved_at FROM site_http_checks WHERE id = ?",
            (latest.manual_check_id,),
        ), (None,))
        self.assertEqual(self._fetch_one("SELECT status FROM sites WHERE id = ?", (site_id,)), ("en_attente",))
        self.assertTrue(self._confirm(site_id, latest.manual_check_id))

    def test_sql_error_rolls_back_confirmation_and_publication(self):
        """Une erreur après le début de publication annule les deux écritures."""
        site_id = self._insert_pending_site()
        latest = self._attempt(site_id, 403)

        def failing_publication(connection, *args, **kwargs):
            connection.execute("UPDATE sites SET status = 'valide' WHERE id = ?", (site_id,))
            raise sqlite3.OperationalError("Erreur transactionnelle simulée.")

        with patch.object(site_http_repository.site_repository, "apply_publication", side_effect=failing_publication):
            with self.assertRaises(sqlite3.OperationalError):
                self._confirm(site_id, latest.manual_check_id)
        self.assertEqual(self._fetch_one("SELECT status FROM sites WHERE id = ?", (site_id,)), ("en_attente",))
        self.assertEqual(self._fetch_one(
            "SELECT manually_approved_at FROM site_http_checks WHERE id = ?", (latest.manual_check_id,),
        ), (None,))

    def test_two_concurrent_confirmations_consume_review_only_once(self):
        """Deux confirmations simultanées produisent une seule publication."""
        site_id = self._insert_pending_site()
        latest = self._attempt(site_id, 403)
        start = Barrier(2)

        def confirm():
            with app.app_context():
                start.wait(timeout=5)
                return self._confirm(site_id, latest.manual_check_id)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: confirm(), range(2)))
        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(self._fetch_one(
            "SELECT COUNT(manually_approved_at) FROM site_http_checks WHERE site_id = ?", (site_id,),
        ), (1,))


if __name__ == "__main__":
    unittest.main()
