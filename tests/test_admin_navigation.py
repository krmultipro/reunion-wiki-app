"""Tests transversaux de la navigation de l'administration."""

import re
import unittest
from contextlib import ExitStack
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from reunion_wiki.app import app


class AdminNavigationParser(HTMLParser):
    """Extrait les liens et formulaires de la navigation admin rendue."""

    def __init__(self):
        super().__init__()
        self.navigation_count = 0
        self.links = []
        self.forms = []
        self._in_navigation = False
        self._navigation_depth = 0
        self._current_link = None
        self._current_form = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "nav" and attributes.get("aria-label") == "Administration":
            self.navigation_count += 1
            self._in_navigation = True
            self._navigation_depth = 1
            return
        if not self._in_navigation:
            return
        if tag == "nav":
            self._navigation_depth += 1
        elif tag == "a":
            self._current_link = {"attrs": attributes, "text": ""}
        elif tag == "form":
            self._current_form = {"attrs": attributes, "inputs": {}}
            self.forms.append(self._current_form)
        elif tag == "input" and self._current_form is not None:
            name = attributes.get("name")
            if name:
                self._current_form["inputs"][name] = attributes.get("value", "")

    def handle_data(self, data):
        if self._current_link is not None:
            self._current_link["text"] += data

    def handle_endtag(self, tag):
        if not self._in_navigation:
            return
        if tag == "a" and self._current_link is not None:
            self._current_link["text"] = " ".join(self._current_link["text"].split())
            self.links.append(self._current_link)
            self._current_link = None
        elif tag == "form":
            self._current_form = None
        elif tag == "nav":
            self._navigation_depth -= 1
            if self._navigation_depth == 0:
                self._in_navigation = False


class AdminNavigationTestCase(unittest.TestCase):
    """Vérifie les cas TC-ADMIN-NAV automatisables."""

    MAIN_PAGES = (
        "/admin",
        "/admin/sites",
        "/admin/clicks",
        "/admin/categories",
        "/admin/talents",
        "/admin/talent-categories",
        "/admin/content",
    )
    FORM_PAGES = (
        ("/admin/propositions/new", "/admin"),
        ("/admin/categories/new", "/admin/categories"),
        ("/admin/talents/new", "/admin/talents"),
        ("/admin/talent-categories/new", "/admin/talent-categories"),
        ("/admin/content/new", "/admin/content"),
    )
    EXPECTED_LINKS = (
        ("Tableau de bord", "/admin"),
        ("Propositions", "/admin/refonte"),
        ("Sites", "/admin/sites"),
        ("Clics", "/admin/clicks"),
        ("Catégories de sites", "/admin/categories"),
        ("Personnalités", "/admin/talents"),
        ("Catégories personnalités", "/admin/talent-categories"),
        ("Contenus SEO", "/admin/content"),
    )
    ACTIVE_SECTIONS = {
        "/admin": "/admin",
        "/admin/sites": "/admin/sites",
        "/admin/propositions/new": "/admin/sites",
        "/admin/clicks": "/admin/clicks",
        "/admin/categories": "/admin/categories",
        "/admin/categories/new": "/admin/categories",
        "/admin/talents": "/admin/talents",
        "/admin/talents/new": "/admin/talents",
        "/admin/talent-categories": "/admin/talent-categories",
        "/admin/talent-categories/new": "/admin/talent-categories",
        "/admin/content": "/admin/content",
        "/admin/content/new": "/admin/content",
    }

    def setUp(self):
        self.original_config = {
            key: app.config.get(key)
            for key in ("TESTING", "WTF_CSRF_ENABLED", "RATELIMIT_ENABLED")
        }
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=True, RATELIMIT_ENABLED=False)
        self.client = app.test_client()
        self._patches = ExitStack()
        empty_admin_list = {"items": [], "page": 1, "total_pages": 1, "total": 0}
        patches = {
            "reunion_wiki.template_helpers.category_service.get_category_names": [],
            "reunion_wiki.template_helpers.category_service.get_category_slug_map": {},
            "reunion_wiki.routes.admin.city_repository.get_all_cities": [],
            "reunion_wiki.routes.admin.site_repository.get_pending_sites": [],
            "reunion_wiki.routes.admin.site_repository.get_status_counts": [],
            "reunion_wiki.routes.admin.site_repository.count_sites_for_admin": {"total": 0},
            "reunion_wiki.routes.admin.site_repository.get_sites_for_admin": [],
            "reunion_wiki.routes.admin.click_repository.get_admin_geo_stats": [],
            "reunion_wiki.routes.admin.click_repository.get_geo_aggregate_rows": [],
            "reunion_wiki.routes.admin.category_repository.get_all_categories": [],
            "reunion_wiki.routes.admin.city_service.get_name_choices": [("", "Non précisée")],
            "reunion_wiki.routes.admin_talents.city_service.get_id_choices": [("", "Non précisée")],
            "reunion_wiki.routes.admin_talents.talent_category_repository.list_all": [],
            "reunion_wiki.routes.admin_talents.talent_service.get_admin_list": empty_admin_list,
            "reunion_wiki.routes.admin_talent_categories.talent_category_service.list_categories": [],
            "reunion_wiki.routes.admin_content.content_service.get_admin_list": empty_admin_list,
        }
        for target, return_value in patches.items():
            self._patches.enter_context(patch(target, return_value=return_value))
        self._authenticate()

    def tearDown(self):
        self._patches.close()
        app.config.update(self.original_config)

    def _authenticate(self):
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

    def _parse_navigation(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, path)
        parser = AdminNavigationParser()
        parser.feed(response.get_data(as_text=True))
        return response, parser

    def test_tc_admin_nav_01_common_navigation_is_on_every_admin_page(self):
        """TC-ADMIN-NAV-01 — Chaque écran admin possède une navigation commune."""
        for path in self.MAIN_PAGES + tuple(path for path, _ in self.FORM_PAGES):
            with self.subTest(path=path):
                _response, navigation = self._parse_navigation(path)
                self.assertEqual(navigation.navigation_count, 1)

        template_root = (Path(app.root_path) / app.template_folder / "admin").resolve()
        authenticated_templates = sorted(
            path for path in template_root.rglob("*.html")
            if path.name not in {"base.html", "login.html"}
        )
        self.assertGreaterEqual(len(authenticated_templates), 14)
        for template in authenticated_templates:
            with self.subTest(template=str(template.relative_to(template_root))):
                first_line = template.read_text(encoding="utf-8").splitlines()[0]
                self.assertEqual(first_line, '{% extends "admin/base.html" %}')

    def test_tc_admin_nav_02_links_have_stable_labels_destinations_and_order(self):
        """TC-ADMIN-NAV-02 — Les liens sont identiques et ordonnés."""
        for path in self.MAIN_PAGES:
            with self.subTest(path=path):
                _response, navigation = self._parse_navigation(path)
                actual = tuple((link["text"], link["attrs"].get("href")) for link in navigation.links)
                self.assertEqual(actual, self.EXPECTED_LINKS)

    def test_tc_admin_nav_03_exactly_one_link_announces_the_active_section(self):
        """TC-ADMIN-NAV-03 — Une seule section courante est annoncée."""
        for path, expected_href in self.ACTIVE_SECTIONS.items():
            with self.subTest(path=path):
                _response, navigation = self._parse_navigation(path)
                active_links = [
                    link for link in navigation.links
                    if link["attrs"].get("aria-current") == "page"
                ]
                self.assertEqual(len(active_links), 1)
                self.assertEqual(active_links[0]["attrs"].get("href"), expected_href)

    def test_tc_admin_nav_04_logout_uses_post_csrf_and_clears_the_session(self):
        """TC-ADMIN-NAV-04 — La déconnexion commune reste protégée par CSRF."""
        _response, navigation = self._parse_navigation("/admin/clicks")
        logout_forms = [
            form for form in navigation.forms
            if form["attrs"].get("action") == "/admin/logout"
        ]
        self.assertEqual(len(logout_forms), 1)
        logout_form = logout_forms[0]
        self.assertEqual(logout_form["attrs"].get("method", "").lower(), "post")
        self.assertTrue(logout_form["inputs"].get("csrf_token"))
        self.assertEqual(self.client.get("/admin/logout").status_code, 405)

        response = self.client.post(
            "/admin/logout",
            data={"csrf_token": logout_form["inputs"]["csrf_token"]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/admin/login"))
        with self.client.session_transaction() as session:
            self.assertNotIn("admin_authenticated", session)

    def test_tc_admin_nav_05_forms_keep_navigation_and_contextual_return(self):
        """TC-ADMIN-NAV-05 — Les formulaires gardent navbar et retour local."""
        for path, return_path in self.FORM_PAGES:
            with self.subTest(path=path):
                response, navigation = self._parse_navigation(path)
                self.assertEqual(navigation.navigation_count, 1)
                body = response.get_data(as_text=True)
                self.assertRegex(
                    body,
                    rf'<a[^>]+href="{re.escape(return_path)}"[^>]*>\s*[^<]*Retour',
                )

    def test_tc_admin_nav_06_anonymous_visitors_are_redirected_to_login(self):
        """TC-ADMIN-NAV-06 — Un visiteur ne reçoit aucune page admin privée."""
        self.client = app.test_client()
        for path in self.MAIN_PAGES:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/admin/login?next=", response.headers["Location"])
                self.assertIn(path, response.headers["Location"])


if __name__ == "__main__":
    unittest.main()
