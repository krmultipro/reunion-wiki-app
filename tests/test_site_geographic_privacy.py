"""Tests des statistiques géographiques respectueuses de la vie privée."""

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from migrate import migrate_click_privacy
from reunion_wiki.app import app
from reunion_wiki.repositories import click_repository
from reunion_wiki.services.click_privacy_service import ALLOWED_ZONES, reunion_day


class SiteGeographicPrivacyTestCase(unittest.TestCase):
    """Vérifie l'amendement RM-SITE-008 version 1.2."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "privacy-test.db"
        self.original_config = {
            key: app.config.get(key)
            for key in (
                "TESTING", "WTF_CSRF_ENABLED", "RATELIMIT_ENABLED",
                "DATABASE_PATH", "CLICK_HMAC_SECRET", "GEOIP_DATABASE_PATH",
            )
        }
        app.config.update(
            TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False,
            DATABASE_PATH=str(self.database_path),
            CLICK_HMAC_SECRET="secret-de-test-non-public", GEOIP_DATABASE_PATH=None,
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
                CREATE TABLE villes (id INTEGER PRIMARY KEY, nom TEXT NOT NULL, slug TEXT NOT NULL);
                CREATE TABLE sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL,
                    lien TEXT NOT NULL, description TEXT, category_id INTEGER,
                    status TEXT, date_ajout DATETIME, en_vedette INTEGER DEFAULT 0,
                    submitted_at DATETIME, first_published_at DATETIME,
                    published_at DATETIME, updated_at DATETIME,
                    click_count INTEGER DEFAULT 0, ville_id INTEGER,
                    location_scope TEXT
                );
                CREATE TABLE click_deduplication (
                    site_id INTEGER NOT NULL, visitor_token TEXT NOT NULL,
                    expires_at DATETIME NOT NULL, PRIMARY KEY (site_id, visitor_token)
                );
                CREATE TABLE site_geo_daily_stats (
                    site_id INTEGER NOT NULL, stat_date TEXT NOT NULL,
                    zone TEXT NOT NULL CHECK(zone IN ('Nord','Sud','Est','Ouest','Hors Réunion','Inconnu')),
                    click_count INTEGER NOT NULL DEFAULT 0,
                    visitor_count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE (site_id, stat_date, zone)
                );
                CREATE TABLE site_stats_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, site_id INTEGER NOT NULL,
                    stat_date TEXT NOT NULL, zone TEXT NOT NULL,
                    old_count INTEGER NOT NULL, new_count INTEGER NOT NULL,
                    admin_username TEXT NOT NULL, reason TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO categories (id, nom, slug) VALUES (1, 'Services', 'services');
                INSERT INTO villes VALUES (1, 'Saint-Denis', 'saint-denis');
                INSERT INTO sites
                    (nom, lien, description, category_id, status, date_ajout, ville_id)
                VALUES ('Site test', 'https://example.test', 'Test', 1, 'valide', DATETIME('now'), 1);
                """
            )
            connection.commit()
        finally:
            connection.close()

    def _execute(self, query, params=()):
        connection = sqlite3.connect(self.database_path)
        try:
            cursor = connection.execute(query, params)
            connection.commit()
            return cursor.fetchall()
        finally:
            connection.close()

    def test_tc_site_geo_01_only_approved_coarse_zones_are_stored(self):
        """TC-SITE-GEO-01 — Seules les six zones géographiques autorisées existent."""
        self.assertEqual(
            set(ALLOWED_ZONES),
            {"Nord", "Sud", "Est", "Ouest", "Hors Réunion", "Inconnu"},
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self._execute(
                "INSERT INTO site_geo_daily_stats VALUES (1, DATE('now'), 'Saint-Denis', 1, 1)"
            )

    def test_tc_site_geo_02_raw_ip_is_never_persisted(self):
        """TC-SITE-GEO-02 — Aucune adresse IP brute n'est écrite en base."""
        remote_ip = "203.0.113.88"
        self.client.get(
            "/go/1", headers={"User-Agent": "PrivacyBrowser/1.0"},
            environ_overrides={"REMOTE_ADDR": remote_ip},
        )
        connection = sqlite3.connect(self.database_path)
        try:
            schema = " ".join(
                row[0] or "" for row in connection.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table'"
                )
            )
            token = connection.execute("SELECT visitor_token FROM click_deduplication").fetchone()[0]
        finally:
            connection.close()
        self.assertNotIn("ip_address", schema)
        self.assertNotIn(remote_ip, token)

    def test_tc_site_geo_03_small_zones_are_hidden_below_ten_visitors(self):
        """TC-SITE-GEO-03 — Une zone sous le seuil n'est pas détaillée."""
        self._execute("INSERT INTO site_geo_daily_stats VALUES (1, DATE('now'), 'Nord', 9, 9)")
        rows = click_repository.get_admin_geo_stats(30, privacy_threshold=10)
        self.assertEqual(rows[0]["zone_display"], "Sous le seuil")
        self._execute("UPDATE site_geo_daily_stats SET click_count=10, visitor_count=10")
        rows = click_repository.get_admin_geo_stats(30, privacy_threshold=10)
        self.assertEqual(rows[0]["zone_display"], "Nord")

    def test_tc_site_geo_04_admin_only_sees_aggregated_statistics(self):
        """TC-SITE-GEO-04 — L'administration ne révèle aucun événement individuel."""
        self._execute("INSERT INTO site_geo_daily_stats VALUES (1, DATE('now'), 'Ouest', 12, 12)")
        with self.client.session_transaction() as session:
            session["admin_authenticated"] = True
            session["admin_username"] = "test-admin"
        response = self.client.get("/admin/clicks")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Statistiques géographiques agrégées", body)
        self.assertNotIn("Adresse IP", body)
        self.assertEqual(self.client.get("/admin/clicks/legacy").status_code, 404)

    def test_tc_site_geo_05_deduplication_tokens_expire_within_24_hours(self):
        """TC-SITE-GEO-05 — Les empreintes expirent après leur courte finalité."""
        self._execute("INSERT INTO click_deduplication VALUES (1, 'expire', DATETIME('now', '-1 minute'))")
        self._execute("INSERT INTO click_deduplication VALUES (1, 'actif', DATETIME('now', '+30 minutes'))")
        removed_tokens, _ = click_repository.purge_private_click_data()
        self.assertEqual(removed_tokens, 1)
        self.assertEqual(self._execute("SELECT visitor_token FROM click_deduplication"), [("actif",)])

    def test_tc_site_geo_06_aggregates_expire_after_12_months(self):
        """TC-SITE-GEO-06 — Les agrégats trop anciens sont supprimés."""
        self._execute("INSERT INTO site_geo_daily_stats VALUES (1, DATE('now', '-13 months'), 'Inconnu', 2, 2)")
        self._execute("INSERT INTO site_geo_daily_stats VALUES (1, DATE('now'), 'Inconnu', 1, 1)")
        _, removed_aggregates = click_repository.purge_private_click_data()
        self.assertEqual(removed_aggregates, 1)
        self.assertEqual(self._execute("SELECT click_count FROM site_geo_daily_stats"), [(1,)])

    def test_tc_site_geo_07_daily_buckets_use_reunion_timezone(self):
        """TC-SITE-GEO-07 — Les journées suivent le fuseau Indian/Reunion."""
        late_utc = datetime(2026, 1, 1, 22, 30, tzinfo=timezone.utc)
        self.assertEqual(reunion_day(late_utc), "2026-01-02")

    def test_tc_site_geo_08_legacy_migration_preserves_counts_and_removes_ips(self):
        """TC-SITE-GEO-08 — La migration conserve les clics sans garder les IP."""
        connection = sqlite3.connect(":memory:")
        try:
            connection.executescript(
                """
                CREATE TABLE sites (id INTEGER PRIMARY KEY, click_count INTEGER DEFAULT 0);
                INSERT INTO sites VALUES (1, 4);
                CREATE TABLE site_clicks (
                    id INTEGER PRIMARY KEY, site_id INTEGER, ip_address TEXT,
                    user_agent TEXT, clicked_at DATETIME
                );
                INSERT INTO site_clicks VALUES
                    (1, 1, '198.51.100.1', 'A', '2026-01-01 10:00:00'),
                    (2, 1, '198.51.100.1', 'A', '2026-01-01 11:00:00'),
                    (3, 1, '198.51.100.2', 'B', '2026-01-01 12:00:00');
                """
            )
            migrate_click_privacy(connection.cursor())
            connection.commit()
            table = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='site_clicks'"
            ).fetchone()
            total = connection.execute(
                "SELECT SUM(click_count) FROM site_geo_daily_stats WHERE site_id=1"
            ).fetchone()[0]
            site_total = connection.execute("SELECT click_count FROM sites WHERE id=1").fetchone()[0]
        finally:
            connection.close()
        self.assertIsNone(table)
        self.assertEqual(total, 4)
        self.assertEqual(site_total, 4)

    def test_tc_site_geo_09_aggregate_corrections_are_audited(self):
        """TC-SITE-GEO-09 — Chaque correction agrégée conserve auteur et motif."""
        self._execute("INSERT INTO site_geo_daily_stats VALUES (1, DATE('now'), 'Est', 5, 5)")
        self._execute("UPDATE sites SET click_count=5 WHERE id=1")
        today = self._execute("SELECT DATE('now')")[0][0]
        changed = click_repository.correct_geo_aggregate(
            1, today, "Est", 3, "alice", "Retrait de deux clics de test"
        )
        audit = self._execute(
            "SELECT old_count, new_count, admin_username, reason FROM site_stats_audit"
        )[0]
        total = self._execute("SELECT click_count FROM sites WHERE id=1")[0][0]
        self.assertTrue(changed)
        self.assertEqual(audit, (5, 3, "alice", "Retrait de deux clics de test"))
        self.assertEqual(total, 3)


if __name__ == "__main__":
    unittest.main()
