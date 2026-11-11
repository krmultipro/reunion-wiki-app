"""Tests automatisés de la recherche, des filtres et des tris de sites."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from migrate import _drop_sites_categorie_column, _drop_sites_ville_column, ensure_column


class SiteSearchTestCase(unittest.TestCase):
    """Vérifie les cas de la fiche de test 5 des sites."""

    def setUp(self):
        """Crée une base SQLite isolée et configure Flask."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "search-test.db"
        self.original_config = {
            key: app.config.get(key)
            for key in (
                "TESTING",
                "WTF_CSRF_ENABLED",
                "RATELIMIT_ENABLED",
                "DATABASE_PATH",
            )
        }
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            RATELIMIT_ENABLED=False,
            DATABASE_PATH=str(self.database_path),
        )
        self._create_schema()
        self.client = app.test_client()

    def tearDown(self):
        """Restaure Flask et supprime la base temporaire."""
        app.config.update(self.original_config)
        self.temp_directory.cleanup()

    def _create_schema(self):
        """Crée les tables nécessaires à la recherche publique."""
        connection = sqlite3.connect(self.database_path)
        try:
            connection.executescript(
                """
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
                    status TEXT,
                    date_ajout DATETIME,
                    submitted_at DATETIME,
                    first_published_at DATETIME,
                    published_at DATETIME,
                    updated_at DATETIME,
                    en_vedette INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    ville_id INTEGER, location_scope TEXT
                );
                INSERT INTO categories (nom, slug) VALUES
                    ('Gastronomie', 'gastronomie'),
                    ('Services', 'services');
                INSERT INTO villes (nom, slug) VALUES
                    ('Saint-Denis', 'saint-denis'),
                    ('Saint-Pierre', 'saint-pierre');
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _insert_site(
        self,
        name,
        description="Ressource utile pour La Réunion.",
        status="valide",
        category_id=1,
        city_id=1,
        scope=None,
        clicks=0,
        added_at="2026-09-17 12:00:00",
    ):
        """Insère un site indexable et retourne son identifiant."""
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO sites (
                    nom, lien, description, category_id, status, date_ajout,
                    published_at, click_count, ville_id, location_scope
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    f"https://site-{name.lower().replace(' ', '-')}.example",
                    description,
                    category_id,
                    status,
                    added_at,
                    added_at if status == "valide" else None,
                    clicks,
                    city_id,
                    scope,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def _search_text(self, query, **parameters):
        """Exécute une recherche publique et retourne le HTML décodé."""
        query_parameters = {"q": query, **parameters}
        return self.client.get("/recherche-sites", query_string=query_parameters).get_data(as_text=True)

    def test_tc_site_007_01_search_ignores_accents_and_case(self):
        """TC-SITE-007-01 — Casse et accents produisent les mêmes résultats."""
        self._insert_site("Guide Réunion")

        for query in ("REUNION", "Réunion", "reunion"):
            self.assertIn("Guide Réunion", self._search_text(query))

    def test_tc_site_007_02_word_order_does_not_change_relevance(self):
        """TC-SITE-007-02 — L'ordre des termes ne change pas les résultats pertinents."""
        self._insert_site("Restaurant créole complet")
        self._insert_site("Restaurant tropical", description="Cuisine locale.")

        normal = self._search_text("restaurant créole")
        reversed_terms = self._search_text("créole restaurant")

        self.assertIn("Restaurant créole complet", normal)
        self.assertIn("Restaurant créole complet", reversed_terms)
        self.assertIn("Restaurant tropical", normal)
        self.assertIn("Restaurant tropical", reversed_terms)
        self.assertLess(
            normal.index("Restaurant créole complet"),
            normal.index("Restaurant tropical"),
        )
        self.assertLess(
            reversed_terms.index("Restaurant créole complet"),
            reversed_terms.index("Restaurant tropical"),
        )

    def test_tc_site_007_03_partial_term_matches(self):
        """TC-SITE-007-03 — Un terme incomplet retrouve le site publié."""
        self._insert_site("Restaurant du Port")

        response = self._search_text("restau")

        self.assertIn("Restaurant du Port", response)

    def test_tc_site_007_04_spelling_is_not_automatically_corrected(self):
        """TC-SITE-007-04 — Le MVP ne corrige pas automatiquement une faute."""
        self._insert_site("Restaurant du Port")

        response = self._search_text("restarant")

        self.assertNotIn("Restaurant du Port", response)
        self.assertIn("Aucun résultat trouvé", response)

    def test_tc_site_007_05a_category_and_city_filters_can_be_combined(self):
        """TC-SITE-007-05A — Texte, catégorie et commune se combinent."""
        self._insert_site("Annuaire Nord Gastro", category_id=1, city_id=1)
        self._insert_site("Annuaire Sud Gastro", category_id=1, city_id=2)
        self._insert_site("Annuaire Nord Services", category_id=2, city_id=1)

        by_category = self._search_text("annuaire", categorie="gastronomie")
        by_city = self._search_text("annuaire", commune="saint-denis")
        combined = self._search_text(
            "annuaire",
            categorie="gastronomie",
            commune="saint-denis",
        )

        self.assertIn("Annuaire Nord Gastro", by_category)
        self.assertIn("Annuaire Sud Gastro", by_category)
        self.assertNotIn("Annuaire Nord Services", by_category)
        self.assertIn("Annuaire Nord Gastro", by_city)
        self.assertIn("Annuaire Nord Services", by_city)
        self.assertNotIn("Annuaire Sud Gastro", by_city)
        self.assertIn("Annuaire Nord Gastro", combined)
        self.assertNotIn("Annuaire Sud Gastro", combined)
        self.assertNotIn("Annuaire Nord Services", combined)
        self.assertIn('value="gastronomie" selected', combined)
        self.assertIn('value="saint-denis" selected', combined)
        self.assertIn('data-auto-submit="true"', combined)
        self.assertIn('class="js-search-control"', combined)
        self.assertIn("Affiner (2)", combined)
        self.assertIn("Effacer les filtres", combined)
        self.assertIn("Nouvelle recherche", combined)
        self.assertNotIn(">Appliquer<", combined)

    def test_tc_site_007_05b_geographic_scope_filter_can_be_combined(self):
        """TC-SITE-007-05B — La portée se combine au texte et aux filtres."""
        self._insert_site("Resto Saint-Denis", city_id=1)
        self._insert_site("Resto Saint-Pierre", city_id=2)
        self._insert_site("Resto Toute La Réunion", city_id=None, scope="island")
        self._insert_site("Resto En ligne", city_id=None, scope="online")
        self._insert_site("Resto Non précisé", city_id=None)
        self._insert_site("Resto Brouillon En ligne", city_id=None, scope="online", status="draft")
        self._insert_site("Resto Services En ligne", city_id=None, scope="online", category_id=2)

        combined = self._search_text(
            "Resto", categorie="gastronomie", commune="saint-denis", portee="city"
        )
        self.assertIn("Resto Saint-Denis", combined)
        for excluded in ("Resto Saint-Pierre", "Resto Toute La Réunion", "Resto En ligne"):
            self.assertNotIn(excluded, combined)
        self.assertIn("Affiner (3)", combined)
        self.assertIn("Retirer la portée", combined)

        for scope, expected in (
            ("island", "Resto Toute La Réunion"),
            ("online", "Resto En ligne"),
            ("unspecified", "Resto Non précisé"),
        ):
            with self.subTest(scope=scope):
                html = self._search_text("Resto", categorie="gastronomie", portee=scope)
                self.assertIn(expected, html)
                self.assertNotIn("Resto Services En ligne", html)
                self.assertNotIn("Resto Brouillon En ligne", html)
                for other in ("Resto Saint-Denis", "Resto Saint-Pierre", "Resto Toute La Réunion", "Resto En ligne", "Resto Non précisé"):
                    if other != expected:
                        self.assertNotIn(other, html)

        contradictory = self._search_text(
            "Resto", categorie="gastronomie", commune="saint-denis", portee="island"
        )
        self.assertIn("Aucun résultat trouvé", contradictory)

    def test_location_scope_can_be_saved_and_cannot_overlap_a_city(self):
        """Admin input keeps geographic choices mutually exclusive."""
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"
        payload = {
            "nom": "Service pour toute La Réunion", "ville": "", "portee": "island",
            "lien": "https://toute-ile.example",
            "description": "Un service disponible sur toute La Réunion.",
            "categorie": "Services", "status": "draft", "honeypot": "",
        }
        created = self.client.post("/admin/propositions/new", data=payload)
        self.assertEqual(created.status_code, 302)
        connection = sqlite3.connect(self.database_path)
        try:
            saved = connection.execute(
                "SELECT id, ville_id, location_scope FROM sites WHERE nom = ?",
                (payload["nom"],),
            ).fetchone()
        finally:
            connection.close()
        self.assertIsNotNone(saved)
        self.assertEqual(saved[1:], (None, "island"))

        invalid = self.client.post(
            "/admin/propositions/new",
            data={**payload, "nom": "Choix contradictoire", "ville": "Saint-Denis", "portee": "online", "lien": "https://contradictoire.example"},
        )
        self.assertEqual(invalid.status_code, 200)
        self.assertIn("Choisissez une commune ou une portée", invalid.get_data(as_text=True))

        edited = self.client.post(
            f"/admin/propositions/{saved[0]}/edit",
            data={**payload, "ville": "Saint-Denis", "portee": ""},
        )
        self.assertEqual(edited.status_code, 302)
        connection = sqlite3.connect(self.database_path)
        try:
            updated = connection.execute(
                "SELECT ville_id, location_scope FROM sites WHERE id = ?", (saved[0],)
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(updated, (1, None))

    def test_legacy_site_rebuild_preserves_explicit_scope(self):
        """La migration des anciennes colonnes ne perd pas la portée choisie."""
        connection = sqlite3.connect(":memory:")
        try:
            cursor = connection.cursor()
            cursor.executescript("""
                CREATE TABLE sites (
                    id INTEGER PRIMARY KEY, nom TEXT NOT NULL, ville TEXT,
                    categorie TEXT, lien TEXT NOT NULL, description TEXT,
                    category_id INTEGER, status TEXT, date_ajout DATETIME,
                    en_vedette INTEGER, click_count INTEGER, ville_id INTEGER
                );
                INSERT INTO sites VALUES
                    (1, 'Annuaire île', NULL, 'Services', 'https://ile.example',
                     'Service local', 1, 'valide', NULL, 0, 0, NULL);
            """)
            ensure_column(cursor, "sites", "location_scope", "TEXT")
            cursor.execute("UPDATE sites SET location_scope = 'island' WHERE id = 1")
            self.assertTrue(_drop_sites_categorie_column(cursor))
            self.assertTrue(_drop_sites_ville_column(cursor))
            self.assertEqual(
                cursor.execute(
                    "SELECT ville_id, location_scope FROM sites WHERE id = 1"
                ).fetchone(),
                (None, "island"),
            )
        finally:
            connection.close()

    def test_tc_site_007_06_only_published_sites_are_returned(self):
        """TC-SITE-007-06 — La recherche n'expose aucun statut privé."""
        statuses = {
            "Résultat Brouillon": "draft",
            "Résultat Attente": "en_attente",
            "Résultat Publié": "valide",
            "Résultat Refusé": "refuse",
            "Résultat Archivé": "archived",
        }
        for name, status in statuses.items():
            self._insert_site(name, status=status)

        response = self._search_text("Résultat")

        self.assertIn("Résultat Publié", response)
        for name in statuses:
            if name != "Résultat Publié":
                self.assertNotIn(name, response)

    def test_tc_site_007_07_empty_result_offers_all_expected_actions(self):
        """TC-SITE-007-07 — Un résultat vide propose aide et réinitialisation."""
        response = self._search_text(
            "introuvable",
            categorie="gastronomie",
            commune="saint-denis",
        )

        self.assertIn("Aucun résultat trouvé", response)
        self.assertIn("Effacer les filtres", response)
        self.assertIn("Nouvelle recherche", response)
        self.assertIn("/proposer-site", response)
        self.assertIn("Catégories", response)

    def test_tc_site_007_08_all_public_sorts_are_available(self):
        """TC-SITE-007-08 — Les quatre tris publics produisent l'ordre demandé."""
        newest_publication = self._insert_site(
            "Alpha Annuaire",
            description="Sélection test locale.",
            clicks=5,
            added_at="2026-09-03 12:00:00",
        )
        self._insert_site(
            "Beta Test",
            description="Sélection locale.",
            clicks=10,
            added_at="2026-09-01 12:00:00",
        )
        self._insert_site(
            "Zeta Portail",
            description="Sélection test locale.",
            clicks=50,
            added_at="2026-09-02 12:00:00",
        )
        # La date d'ajout ne doit plus déterminer le tri des nouveautés.
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "UPDATE sites SET date_ajout = '2026-01-01 12:00:00' WHERE id = ?",
                (newest_publication,),
            )

        by_relevance = self._search_text("test")
        by_popularity = self._search_text("test", sort="popularite")
        by_date = self._search_text("test", sort="date")
        by_name = self._search_text("test", sort="nom")

        self.assertLess(by_relevance.index("Beta Test"), by_relevance.index("Zeta Portail"))
        self.assertLess(by_popularity.index("Zeta Portail"), by_popularity.index("Beta Test"))
        self.assertLess(by_date.index("Alpha Annuaire"), by_date.index("Zeta Portail"))
        self.assertLess(by_name.index("Alpha Annuaire"), by_name.index("Beta Test"))
        for sort_value in ("relevance", "popularite", "date", "nom"):
            self.assertIn(f'value="{sort_value}"', by_relevance)


if __name__ == "__main__":
    unittest.main()
