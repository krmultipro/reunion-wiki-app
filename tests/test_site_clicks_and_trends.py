"""Tests automatisés des clics, exclusions et tendances des sites."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.repositories import click_repository


class SiteClicksAndTrendsTestCase(unittest.TestCase):
    """Vérifie les cas de la fiche de test 6 des sites."""

    def setUp(self):
        """Crée une base isolée et configure l'application en test."""
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "clicks-test.db"
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
        self.app_context = app.app_context()
        self.app_context.push()
        self._create_schema()
        self.client = app.test_client()

    def tearDown(self):
        """Restaure Flask et supprime la base temporaire."""
        self.app_context.pop()
        app.config.update(self.original_config)
        self.temp_directory.cleanup()

    def _create_schema(self):
        """Crée les tables nécessaires aux clics et aux tendances."""
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
                CREATE TABLE click_deduplication (
                    site_id INTEGER NOT NULL,
                    visitor_token TEXT NOT NULL,
                    expires_at DATETIME NOT NULL,
                    PRIMARY KEY (site_id, visitor_token)
                );
                CREATE TABLE site_geo_daily_stats (
                    site_id INTEGER NOT NULL,
                    stat_date TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    click_count INTEGER NOT NULL DEFAULT 0,
                    visitor_count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE (site_id, stat_date, zone)
                );
                CREATE TABLE site_stats_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    stat_date TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    old_count INTEGER NOT NULL,
                    new_count INTEGER NOT NULL,
                    admin_username TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO categories (nom, slug) VALUES ('Services', 'services');
                INSERT INTO villes (nom, slug) VALUES ('Saint-Denis', 'saint-denis');
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _insert_site(self, name="Site publié", status="valide", click_count=0):
        """Insère un site et retourne son identifiant."""
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(
                """
                INSERT INTO sites (
                    nom, lien, description, category_id, status, date_ajout,
                    click_count, ville_id
                ) VALUES (?, ?, ?, 1, ?, DATETIME('now'), ?, 1)
                """,
                (
                    name,
                    f"https://site-{name.lower().replace(' ', '-')}.example",
                    f"Description de {name}.",
                    status,
                    click_count,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def _insert_aggregate(self, site_id, age_modifier="0 days", clicks=1, visitors=1):
        """Insère un agrégat à une date relative contrôlée."""
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                """
                INSERT INTO site_geo_daily_stats
                    (site_id, stat_date, zone, click_count, visitor_count)
                VALUES (?, DATE('now', ?), 'Inconnu', ?, ?)
                """,
                (site_id, age_modifier, clicks, visitors),
            )
            connection.commit()
        finally:
            connection.close()

    def _site_state(self, site_id):
        """Retourne le compteur et le nombre de clics agrégés d'un site."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            return connection.execute(
                """
                SELECT s.click_count,
                    COALESCE((SELECT SUM(gs.click_count) FROM site_geo_daily_stats gs WHERE gs.site_id = s.id), 0)
                    AS event_count
                FROM sites s
                WHERE s.id = ?
                """,
                (site_id,),
            ).fetchone()
        finally:
            connection.close()

    def test_tc_site_008_01_valid_click_creates_event_and_increments(self):
        """TC-SITE-008-01 — Un clic admissible produit un événement et un incrément."""
        site_id = self._insert_site()

        response = self.client.get(f"/go/{site_id}", headers={"User-Agent": "TestBrowser/1.0"})
        state = self._site_state(site_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["event_count"], 1)
        self.assertEqual(state["click_count"], 1)

    def test_tc_site_008_02_repeat_click_within_30_minutes_is_ignored(self):
        """TC-SITE-008-02 — Un second clic récent du même visiteur est ignoré."""
        site_id = self._insert_site()
        environ = {"REMOTE_ADDR": "198.51.100.20"}
        headers = {"User-Agent": "TestBrowser/1.0"}

        self.client.get(f"/go/{site_id}", headers=headers, environ_overrides=environ)
        self.client.get(f"/go/{site_id}", headers=headers, environ_overrides=environ)
        state = self._site_state(site_id)

        self.assertEqual(state["event_count"], 1)
        self.assertEqual(state["click_count"], 1)

    def test_tc_site_008_03_click_after_30_minutes_is_counted_again(self):
        """TC-SITE-008-03 — Un clic après la fenêtre produit un nouvel événement."""
        site_id = self._insert_site()
        request_options = {
            "headers": {"User-Agent": "TestBrowser/1.0"},
            "environ_overrides": {"REMOTE_ADDR": "198.51.100.30"},
        }
        self.client.get(f"/go/{site_id}", **request_options)
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute(
                "UPDATE click_deduplication SET expires_at=DATETIME('now', '-1 minute') WHERE site_id=?",
                (site_id,),
            )
            connection.commit()
        finally:
            connection.close()

        self.client.get(f"/go/{site_id}", **request_options)
        state = self._site_state(site_id)

        self.assertEqual(state["event_count"], 2)
        self.assertEqual(state["click_count"], 2)

    def test_tc_site_008_04_known_bot_is_not_counted(self):
        """TC-SITE-008-04 — Un robot connu ne produit aucun clic."""
        site_id = self._insert_site()

        response = self.client.get(f"/go/{site_id}", headers={"User-Agent": "GPTBot/1.0"})
        state = self._site_state(site_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["event_count"], 0)
        self.assertEqual(state["click_count"], 0)

    def test_tc_site_008_05_authenticated_admin_clicks_are_not_counted(self):
        """TC-SITE-008-05 — Les clics d'un administrateur sont exclus."""
        site_id = self._insert_site()
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

        self.client.get(f"/go/{site_id}", headers={"User-Agent": "TestBrowser/1.0"})
        state = self._site_state(site_id)

        self.assertEqual(state["event_count"], 0)
        self.assertEqual(state["click_count"], 0)

    def test_tc_site_008_06_unpublished_site_click_is_not_counted(self):
        """TC-SITE-008-06 — Un site non publié ne reçoit aucun clic."""
        site_id = self._insert_site(status="en_attente")

        response = self.client.get(f"/go/{site_id}", headers={"User-Agent": "TestBrowser/1.0"})
        state = self._site_state(site_id)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(state["event_count"], 0)
        self.assertEqual(state["click_count"], 0)

    def test_tc_site_008_07_admin_correction_updates_counter_and_audit(self):
        """TC-SITE-008-07 — Corriger un agrégat ajuste le total et laisse une trace."""
        site_id = self._insert_site(click_count=3)
        self._insert_aggregate(site_id, clicks=3, visitors=3)
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"

        response = self.client.post(
            "/admin/clicks/aggregate-correction",
            data={
                "site_id": str(site_id), "stat_date": self._today(),
                "zone": "Inconnu", "new_count": "1", "reason": "Correction de test",
            },
        )
        state = self._site_state(site_id)
        connection = sqlite3.connect(self.database_path)
        try:
            audit = connection.execute(
                "SELECT old_count, new_count, admin_username, reason FROM site_stats_audit"
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["event_count"], 1)
        self.assertEqual(state["click_count"], 1)
        self.assertEqual(audit, (3, 1, "test-admin", "Correction de test"))

    def test_tc_site_008_08_trends_use_correct_periods_and_exclude_zero_clicks(self):
        """TC-SITE-008-08 — Les tendances respectent leurs périodes et exclusions."""
        active_id = self._insert_site(name="Site actif", click_count=4)
        silent_id = self._insert_site(name="Site sans clic")
        for modifier in ("-1 day", "-2 days", "-3 days"):
            self._insert_aggregate(active_id, modifier)
        self._insert_aggregate(active_id, "-10 days")

        trending = click_repository.get_trending_sites()
        stable = click_repository.get_stable_sites()
        active_trend = next(row for row in trending if row["id"] == active_id)

        self.assertEqual(active_trend["clicks_7d"], 3)
        self.assertEqual(active_trend["clicks_prev_7d"], 1)
        self.assertEqual(active_trend["growth_pct"], 200.0)
        self.assertEqual(next(row for row in stable if row["id"] == active_id)["clicks_30d"], 4)
        self.assertNotIn(silent_id, [row["id"] for row in trending])
        self.assertNotIn(silent_id, [row["id"] for row in stable])

    def test_tc_site_008_09_server_deduplication_does_not_store_raw_ip(self):
        """TC-SITE-008-09 — La déduplication sans cookie ne conserve pas l'IP brute."""
        site_id = self._insert_site()
        remote_ip = "203.0.113.50"
        request_options = {
            "headers": {"User-Agent": "TestBrowser/1.0"},
            "environ_overrides": {"REMOTE_ADDR": remote_ip},
        }

        self.client.get(f"/go/{site_id}", **request_options)
        self.client.get(f"/go/{site_id}", **request_options)

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            raw_table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='site_clicks'"
            ).fetchone()
            tokens = connection.execute(
                "SELECT visitor_token FROM click_deduplication WHERE site_id = ?",
                (site_id,),
            ).fetchall()
        finally:
            connection.close()

        self.assertIsNone(raw_table)
        self.assertEqual(len(tokens), 1)
        self.assertNotIn(remote_ip, tokens[0]["visitor_token"])

    @staticmethod
    def _today():
        """Retourne la date SQLite utilisée par les données de test."""
        connection = sqlite3.connect(":memory:")
        try:
            return connection.execute("SELECT DATE('now')").fetchone()[0]
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
