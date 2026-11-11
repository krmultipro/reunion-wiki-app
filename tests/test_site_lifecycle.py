"""Tests automatisés des statuts et de la visibilité publique des sites."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.services.site_http_service import (
    ACCESSIBLE, INACCESSIBLE, MANUAL_REVIEW, TEMPORARY_ERROR, HttpCheckResult,
)


class SiteLifecycleTestCase(unittest.TestCase):
    """Vérifie les cas critiques de la fiche de test 1 des sites."""

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
                ACCESSIBLE, url, url, 200, "Réponse simulée accessible."
            ),
        )

        self._create_schema()
        self.client = app.test_client()

    def tearDown(self):
        """Supprime la base SQLite temporaire après chaque test."""
        app.config.update(self.original_config)
        self.temp_directory.cleanup()

    def _create_schema(self):
        """Crée le sous-ensemble du schéma nécessaire aux tests de cycle de vie."""
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

                CREATE TABLE site_clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

    def _authenticate_admin(self):
        """Ouvre une session administrateur pour les parcours protégés."""
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

    def _insert_site(self, name, status):
        """Insère un site de test et retourne son identifiant."""
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO sites (
                    nom, lien, description, category_id, status, date_ajout
                )
                VALUES (?, ?, ?, 1, ?, DATETIME('now'))
                """,
                (
                    name,
                    f"https://site-{status.replace('_', '-')}.example",
                    f"Description publique de {name} à La Réunion.",
                    status,
                ),
            )
            connection.execute(
                "UPDATE sites SET lien = ? WHERE id = ?",
                (f"https://site-{cursor.lastrowid}-{status.replace('_', '-')}.example", cursor.lastrowid),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def _fetch_site(self, site_id):
        """Retourne un site de la base de test."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            return connection.execute(
                "SELECT * FROM sites WHERE id = ?",
                (site_id,),
            ).fetchone()
        finally:
            connection.close()

    def _action(self, site_id, action, follow_redirects=False):
        return self.client.post(
            f"/admin/propositions/{site_id}",
            data={
                "site_id": site_id, "action": action, "return_to": "/admin/sites",
                "refusal_reason": "insufficient_information" if action == "reject" else "",
            },
            follow_redirects=follow_redirects,
        )

    def _approve(self, site_id):
        started = self._action(site_id, "approve")
        self.assertIn("editorial-review", started.location)
        site = self._fetch_site(site_id)
        return self.client.post(
            started.location,
            data={"reviewed_url": site["lien"], "criterion": "reunion_content"},
        )

    def _submit_public_site(self, name="Proposition Péi"):
        """Envoie une proposition publique valide."""
        return self.client.post(
            "/proposer-site",
            data={
                "nom": name,
                "ville": "",
                "lien": "https://proposition-pei.example",
                "description": "Un site réunionnais consacré à la cuisine locale.",
                "categorie": "Gastronomie",
                "honeypot": "",
            },
        )

    def test_tc_site_006_01_public_submission_is_pending_and_admin_visible(self):
        """TC-SITE-006-01 — Une proposition reste privée et visible en admin."""
        response = self._submit_public_site()
        site = self._fetch_site(1)

        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(site)
        self.assertEqual(site["status"], "en_attente")

        search_response = self.client.get("/recherche?q=Proposition+Péi")
        category_response = self.client.get("/categorie/gastronomie")
        outgoing_response = self.client.get(f"/go/{site['id']}")
        self.assertIn(b"Aucun r\xc3\xa9sultat", search_response.data)
        self.assertNotIn(f'href="/go/{site["id"]}"'.encode(), search_response.data)
        self.assertNotIn(b"Proposition P\xc3\xa9i", category_response.data)
        self.assertEqual(outgoing_response.status_code, 404)

        self._authenticate_admin()
        admin_response = self.client.get("/admin/sites")
        self.assertIn(b"Proposition P\xc3\xa9i", admin_response.data)

    def test_tc_site_006_02_edit_keeps_pending_status(self):
        """TC-SITE-006-02 — Une correction ne publie pas la proposition."""
        self._submit_public_site()
        self._authenticate_admin()

        response = self.client.post(
            "/admin/propositions/1/edit",
            data={
                "nom": "Proposition Péi corrigée",
                "ville": "Saint-Denis",
                "lien": "https://proposition-pei.example/corrigee",
                "description": "Une description factuelle corrigée pour ce site réunionnais.",
                "categorie": "Gastronomie",
                "status": "en_attente",
                "en_vedette": "",
                "honeypot": "",
            },
        )
        site = self._fetch_site(1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(site["nom"], "Proposition Péi corrigée")
        self.assertEqual(site["status"], "en_attente")
        self.assertEqual(site["ville_id"], 1)

    def test_tc_site_006_03_all_allowed_transitions_succeed(self):
        """TC-SITE-006-03 — Toutes les transitions autorisées réussissent."""
        self._authenticate_admin()
        created = self.client.post(
            "/admin/propositions/new",
            data={
                "nom": "Brouillon administratif", "ville": "",
                "lien": "https://brouillon-admin.example",
                "description": "Présentation factuelle d'un site réunionnais.",
                "categorie": "Gastronomie", "status": "draft", "honeypot": "",
            },
        )
        self.assertEqual(created.status_code, 302)
        self.assertEqual(self._fetch_site(1)["status"], "draft")
        cases = (
            ("draft", "valide", "approve"),
            ("draft", "archived", "archive"),
            ("en_attente", "valide", "approve"),
            ("en_attente", "refuse", "reject"),
            ("valide", "archived", "archive"),
            ("refuse", "en_attente", "pending"),
            ("archived", "valide", "approve"),
        )
        for current, target, action in cases:
            with self.subTest(current=current, target=target):
                site_id = self._insert_site(f"Transition {current} vers {target}", current)
                response = self._approve(site_id) if action == "approve" else self._action(site_id, action)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(self._fetch_site(site_id)["status"], target)

        draft_to_archive = self._insert_site("Brouillon archivé puis publié", "draft")
        self._action(draft_to_archive, "archive")
        self.assertEqual(self._fetch_site(draft_to_archive)["status"], "archived")
        self._approve(draft_to_archive)
        reopened = self._fetch_site(draft_to_archive)
        self.assertEqual(reopened["status"], "valide")
        self.assertIsNotNone(reopened["first_published_at"])

        refused_id = self._insert_site("Réexamen en édition", "refuse")
        site = self._fetch_site(refused_id)
        edited = self.client.post(
            f"/admin/propositions/{refused_id}/edit",
            data={
                "nom": site["nom"], "ville": "", "lien": site["lien"],
                "description": site["description"], "categorie": "Gastronomie",
                "status": "en_attente", "honeypot": "",
            },
        )
        self.assertEqual(edited.status_code, 302)
        self.assertEqual(self._fetch_site(refused_id)["status"], "en_attente")

        app.config["SITE_HTTP_CHECKER"] = lambda url: HttpCheckResult(
            MANUAL_REVIEW, url, url, 403, "Contrôle humain requis."
        )
        draft_id = self._insert_site("Brouillon avec contrôle manuel", "draft")
        manual = self._approve(draft_id)
        self.assertIn("http-review", manual.location)
        self.assertEqual(self._fetch_site(draft_id)["status"], "draft")
        confirmed = self.client.post(
            manual.location,
            data={
                "site_id": draft_id,
                "check_id": int(manual.location.rstrip("/").split("/")[-1]),
                "note": "Site ouvert sans compte et contenu public vérifié.",
            },
        )
        self.assertEqual(confirmed.status_code, 302)
        self.assertEqual(self._fetch_site(draft_id)["status"], "valide")

    def test_tc_site_006_04_forbidden_transitions_are_rejected(self):
        """TC-SITE-006-04 — Les transitions interdites sont refusées."""
        self._authenticate_admin()
        cases = (
            ("valide", "reject"),
            ("en_attente", "archive"),
            ("refuse", "approve"),
            ("archived", "pending"),
            ("draft", "reject"),
        )
        for current, action in cases:
            with self.subTest(current=current, action=action):
                site_id = self._insert_site(f"Transition interdite {current}", current)
                response = self._action(site_id, action, follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn("Transition de statut non autorisée", response.get_data(as_text=True))
                self.assertEqual(self._fetch_site(site_id)["status"], current)

        refused_id = self._insert_site("Refusé en édition", "refuse")
        forged = self.client.post(
            f"/admin/propositions/{refused_id}/edit",
            data={"status": "valide"},
            follow_redirects=True,
        )
        self.assertIn("Transition de statut non autorisée", forged.get_data(as_text=True))
        self.assertEqual(self._fetch_site(refused_id)["status"], "refuse")

        published_id = self._insert_site("URL publiée", "valide")
        published = self._fetch_site(published_id)
        changed_url = self.client.post(
            f"/admin/propositions/{published_id}/edit",
            data={
                "nom": published["nom"], "ville": "", "lien": "https://nouvelle-url.example",
                "description": published["description"], "categorie": "Gastronomie",
                "status": "valide", "honeypot": "",
            },
            follow_redirects=True,
        )
        self.assertIn("Archivez le site avant de modifier son URL", changed_url.get_data(as_text=True))
        self.assertEqual(self._fetch_site(published_id)["lien"], published["lien"])
        self.assertEqual(self._fetch_site(published_id)["status"], "valide")

    def test_tc_site_006_05_only_published_site_is_public(self):
        """TC-SITE-006-05 — Seul le site publié est visible publiquement."""
        sites = {
            "Site Brouillon": "draft",
            "Site En Attente": "en_attente",
            "Site Publié": "valide",
            "Site Refusé": "refuse",
            "Site Archivé": "archived",
        }
        site_ids = {
            name: self._insert_site(name, status)
            for name, status in sites.items()
        }

        search_response = self.client.get("/recherche?q=Site")
        category_response = self.client.get("/categorie/gastronomie")
        self.assertIn("Site Publié", search_response.get_data(as_text=True))
        self.assertIn("Site Publié", category_response.get_data(as_text=True))

        for name in sites:
            if name != "Site Publié":
                self.assertNotIn(name, search_response.get_data(as_text=True))
                self.assertNotIn(name, category_response.get_data(as_text=True))

        for name, site_id in site_ids.items():
            response = self.client.get(f"/go/{site_id}")
            expected_status = 302 if name == "Site Publié" else 404
            self.assertEqual(response.status_code, expected_status)

        self._authenticate_admin()
        admin_response = self.client.get("/admin/sites").get_data(as_text=True)
        for name in sites:
            self.assertIn(name, admin_response)

    def test_tc_site_006_06_submission_is_never_auto_published(self):
        """TC-SITE-006-06 — Une proposition ne change pas de statut seule."""
        self._submit_public_site()

        self.client.get("/recherche?q=Proposition")
        self.client.get("/categorie/gastronomie")

        site = self._fetch_site(1)
        self.assertEqual(site["status"], "en_attente")

    def test_tc_site_006_07_direct_publication_requires_all_checks(self):
        """TC-SITE-006-07 — La publication directe exécute tous les contrôles."""
        self._authenticate_admin()
        payload = {
            "nom": "Pilote direct", "ville": "",
            "lien": "https://pilote-direct.example",
            "description": "Un site réunionnais avec une description factuelle.",
            "categorie": "Gastronomie", "status": "valide", "honeypot": "",
        }

        for invalid in (
            {"nom": ""},
            {"lien": "javascript:alert(1)"},
            {"description": "javascript:alert(1)"},
            {"categorie": ""},
        ):
            with self.subTest(invalid=invalid):
                self.client.post("/admin/propositions/new", data={**payload, **invalid})
                self.assertIsNone(self._fetch_site(1))

        checks = []
        http_state = {"decision": INACCESSIBLE, "code": 404}

        def checker(url):
            checks.append(url)
            return HttpCheckResult(
                http_state["decision"], url, url, http_state["code"],
                "Contrôle HTTP simulé.",
            )

        app.config["SITE_HTTP_CHECKER"] = checker
        created = self.client.post("/admin/propositions/new", data=payload)
        self.assertEqual(created.status_code, 302)
        self.assertIn("editorial-review", created.location)
        site = self._fetch_site(1)
        self.assertEqual(site["status"], "draft")
        self.assertEqual(checks, [])
        self.assertEqual(self.client.get(f"/go/{site['id']}").status_code, 404)

        review_url = created.location
        refused = self.client.post(
            review_url, data={"reviewed_url": site["lien"], "criterion": "no_link"},
        )
        self.assertEqual(refused.status_code, 302)
        self.assertEqual(self._fetch_site(site["id"])["status"], "draft")
        self.assertEqual(checks, [])

        for decision, code in ((INACCESSIBLE, 404), (TEMPORARY_ERROR, 503)):
            with self.subTest(http_decision=decision):
                http_state.update(decision=decision, code=code)
                blocked = self.client.post(
                    review_url,
                    data={"reviewed_url": site["lien"], "criterion": "reunion_content"},
                )
                self.assertEqual(blocked.status_code, 302)
                self.assertEqual(self._fetch_site(site["id"])["status"], "draft")
                self.assertEqual(self.client.get(f"/go/{site['id']}").status_code, 404)

        http_state.update(decision=ACCESSIBLE, code=200)
        published = self.client.post(
            review_url,
            data={"reviewed_url": site["lien"], "criterion": "reunion_content"},
        )
        self.assertEqual(published.status_code, 302)
        final = self._fetch_site(site["id"])
        self.assertEqual(final["status"], "valide")
        self.assertIsNotNone(final["first_published_at"])
        self.assertEqual(checks, [site["lien"]] * 3)
        search = self.client.get("/recherche?q=Pilote+direct")
        self.assertIn("Pilote direct", search.get_data(as_text=True))
        self.assertEqual(self.client.get(f"/go/{site['id']}").status_code, 302)


if __name__ == "__main__":
    unittest.main()
