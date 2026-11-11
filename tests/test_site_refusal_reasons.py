"""COR-SITE-04: private, mandatory and atomic refusal decisions."""

import importlib
import re
import sqlite3
import unittest
from unittest.mock import patch

from reunion_wiki.app import app
from reunion_wiki.repositories import site_repository
from tests import test_site_lifecycle as lifecycle


class SiteRefusalReasonsTests(unittest.TestCase):
    setUp = lifecycle.SiteLifecycleTestCase.setUp
    tearDown = lifecycle.SiteLifecycleTestCase.tearDown
    _create_schema = lifecycle.SiteLifecycleTestCase._create_schema
    _authenticate_admin = lifecycle.SiteLifecycleTestCase._authenticate_admin
    _insert_site = lifecycle.SiteLifecycleTestCase._insert_site
    _fetch_site = lifecycle.SiteLifecycleTestCase._fetch_site

    def _refuse(self, site_id, reason=None, **extra):
        data = {"site_id": site_id, "action": "reject", "return_to": "/admin/sites"}
        if reason is not None:
            data["refusal_reason"] = reason
        return self.client.post(f"/admin/propositions/{site_id}", data={**data, **extra}, follow_redirects=True)

    def _history(self, site_id):
        with sqlite3.connect(self.database_path) as db:
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='site_refusal_history'").fetchone()
            if not exists:
                return []
            return db.execute(
                "SELECT reason, admin_username, created_at FROM site_refusal_history WHERE site_id=? ORDER BY id",
                (site_id,),
            ).fetchall()

    def test_missing_and_unknown_reasons_cannot_change_status(self):
        self._authenticate_admin()
        for reason in (None, "", "invented_reason"):
            with self.subTest(reason=reason):
                site_id = self._insert_site("Proposition sans motif", "en_attente")
                response = self._refuse(site_id, reason)
                self.assertEqual(self._fetch_site(site_id)["status"], "en_attente")
                self.assertEqual(self._history(site_id), [])
                self.assertIn("motif de refus", response.get_data(as_text=True).lower())

    def test_six_documented_reasons_store_author_date_and_private_admin_history(self):
        self._authenticate_admin()
        for reason in ("duplicate", "no_reunion_link", "inaccessible", "prohibited_content", "insufficient_information", "editorial_scope"):
            with self.subTest(reason=reason):
                site_id = self._insert_site("Proposition contrôlée", "en_attente")
                self._refuse(site_id, reason)
                self.assertEqual(self._fetch_site(site_id)["status"], "refuse")
                history = self._history(site_id)
                self.assertEqual(len(history), 1)
                self.assertEqual(history[0][:2], (reason, "test-admin"))
                self.assertTrue(history[0][2])

    def test_edit_refusal_also_requires_and_records_reason(self):
        self._authenticate_admin()
        site_id = self._insert_site("Refus en édition", "en_attente")
        site = self._fetch_site(site_id)
        payload = {"nom": site["nom"], "ville": "", "lien": site["lien"],
                   "description": site["description"], "categorie": "Gastronomie", "status": "refuse", "honeypot": ""}
        self.client.post(f"/admin/propositions/{site_id}/edit", data=payload)
        self.assertEqual(self._fetch_site(site_id)["status"], "en_attente")
        self.client.post(f"/admin/propositions/{site_id}/edit", data={**payload, "refusal_reason": "insufficient_information"})
        self.assertEqual(self._fetch_site(site_id)["status"], "refuse")
        self.assertEqual(self._history(site_id)[0][:2], ("insufficient_information", "test-admin"))

    def test_refusal_and_audit_roll_back_together_on_history_failure(self):
        refusal_repository = importlib.import_module("reunion_wiki.repositories.site_refusal_repository")
        site_id = self._insert_site("Décision atomique", "en_attente")
        with app.app_context(), patch.object(refusal_repository, "record_refusal", side_effect=sqlite3.OperationalError("audit unavailable")):
            with self.assertRaises(sqlite3.OperationalError):
                site_repository.update_site_status(site_id, "refuse", expected_status="en_attente", refusal_reason="duplicate", admin_username="test-admin")
        self.assertEqual(self._fetch_site(site_id)["status"], "en_attente")
        self.assertEqual(self._history(site_id), [])

    def test_history_survives_reexamination_and_stays_private(self):
        self._authenticate_admin()
        site_id = self._insert_site("Proposition privée", "en_attente")
        self._refuse(site_id, "editorial_scope")
        self.client.post(f"/admin/propositions/{site_id}", data={"site_id": site_id, "action": "pending"})
        self.assertEqual(self._fetch_site(site_id)["status"], "en_attente")
        self.assertEqual(len(self._history(site_id)), 1)
        for url in ("/admin/sites", f"/admin/propositions/{site_id}/edit", "/admin"):
            page = self.client.get(url).get_data(as_text=True)
            self.assertIn("Hors ligne éditoriale", page)
            self.assertIn("test-admin", page)
        site = self._fetch_site(site_id)
        self.client.post(
            f"/admin/propositions/{site_id}/editorial-review",
            data={"reviewed_url": site["lien"], "criterion": "reunion_content"},
        )
        self.assertEqual(self._fetch_site(site_id)["status"], "valide")
        for url in ("/recherche?q=Proposition", "/categorie/gastronomie"):
            page = self.client.get(url).get_data(as_text=True)
            self.assertIn("Proposition privée", page)
            self.assertNotIn("Hors ligne éditoriale", page)
            self.assertNotIn("test-admin", page)
        self.client.post(f"/admin/propositions/{site_id}", data={"site_id": site_id, "action": "archive"})
        self.assertEqual(self._fetch_site(site_id)["status"], "archived")
        self.assertEqual(len(self._history(site_id)), 1)

    def test_historical_refusals_have_explicit_unknown_reason_without_fake_history(self):
        site_id = self._insert_site("Ancien refus", "refuse")
        self._authenticate_admin()
        for url in ("/admin/sites", f"/admin/propositions/{site_id}/edit"):
            self.assertIn("Motif historique non renseigné", self.client.get(url).get_data(as_text=True))
        self.assertEqual(self._history(site_id), [])

    def test_refusal_form_is_protected_by_csrf_and_admin_authentication(self):
        site_id = self._insert_site("Proposition protégée", "en_attente")
        anonymous = self._refuse(site_id, "duplicate")
        self.assertEqual(self._fetch_site(site_id)["status"], "en_attente")
        self.assertIn("Connexion", anonymous.get_data(as_text=True))
        self._authenticate_admin()
        app.config["WTF_CSRF_ENABLED"] = True
        response = self.client.post(f"/admin/propositions/{site_id}", data={"site_id": site_id, "action": "reject", "refusal_reason": "duplicate"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")
        with self.client.session_transaction() as session:
            self.assertIn(("error", "Session expirée ou formulaire invalide. Réessaie."), session["_flashes"])
        self.assertEqual(self._fetch_site(site_id)["status"], "en_attente")
        self.assertEqual(self._history(site_id), [])

    def test_rendered_reason_field_with_real_csrf_token_allows_refusal(self):
        site_id = self._insert_site("Formulaire réel", "en_attente")
        self._authenticate_admin()
        app.config["WTF_CSRF_ENABLED"] = True
        page = self.client.get("/admin/sites").get_data(as_text=True)
        self.assertIn(f'id="refusal-reason-{site_id}"', page)
        token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page)
        self.assertIsNotNone(token)
        response = self.client.post(
            f"/admin/propositions/{site_id}",
            data={"site_id": site_id, "action": "reject", "refusal_reason": "duplicate", "csrf_token": token.group(1)},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self._fetch_site(site_id)["status"], "refuse")
        self.assertEqual(self._history(site_id)[0][0], "duplicate")

    def test_administrative_creation_cannot_forge_an_initial_refused_status(self):
        self._authenticate_admin()
        for reason in (None, "duplicate"):
            with self.subTest(reason=reason):
                payload = {
                    "nom": "Création refusée forgée", "ville": "", "lien": "https://creation.example",
                    "description": "Description factuelle suffisamment longue.",
                    "categorie": "Gastronomie", "status": "refuse", "honeypot": "",
                }
                if reason:
                    payload["refusal_reason"] = reason
                response = self.client.post("/admin/propositions/new", data=payload, follow_redirects=True)
                self.assertIn("doit commencer en brouillon", response.get_data(as_text=True))
                self.assertIsNone(self._fetch_site(1))
                self.assertEqual(self._history(1), [])


if __name__ == "__main__":
    unittest.main()
