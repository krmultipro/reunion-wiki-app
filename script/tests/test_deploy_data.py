"""Exercise complete private snapshots and offline recovery on disposable data."""

import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from script import deploy_data


class DataBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.live = self.root / "live"
        (self.live / "uploads/talents").mkdir(parents=True)
        self.image = self.live / "uploads/talents/image.png"
        self.image.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        with sqlite3.connect(self.live / "base.db") as db:
            db.execute("CREATE TABLE talents(id INTEGER PRIMARY KEY, image TEXT)")
            db.execute("INSERT INTO talents VALUES(1, 'uploads/talents/image.png')")
        self.bundle = self.root / "snapshot"

    def test_snapshot_preserves_source_and_verifies_all_files(self):
        original = self.image.read_bytes()
        result = deploy_data.snapshot_bundle(self.live, self.bundle)
        self.assertEqual(result["database"]["table_counts"]["talents"], 1)
        self.assertEqual(result["database"]["foreign_key_violations"], 0)
        self.assertEqual(deploy_data.verify_bundle(self.bundle), result)
        self.assertEqual(self.image.read_bytes(), original)
        self.assertEqual((self.bundle / "uploads/talents/image.png").stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.bundle.stat().st_mode & 0o777, 0o700)

    def test_wal_is_copied_and_restore_keeps_displaced_candidate_uploads(self):
        with sqlite3.connect(self.live / "base.db") as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("INSERT INTO talents VALUES(2, NULL)")
            db.commit()
            deploy_data.snapshot_bundle(self.live, self.bundle)
        self.image.write_bytes(b"candidate version")
        (self.live / "uploads/new.txt").write_text("received after snapshot")
        with sqlite3.connect(self.live / "base.db") as db:
            db.execute("DELETE FROM talents")
        deploy_data.restore_bundle(self.bundle, self.live)
        self.assertEqual(self.image.read_bytes(), b"\x89PNG\r\n\x1a\nfixture")
        with sqlite3.connect(self.live / "base.db") as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM talents").fetchone()[0], 2)
        displaced = list(self.live.glob(".uploads-before-restore-*"))
        self.assertEqual(len(displaced), 1)
        self.assertEqual((displaced[0] / "new.txt").read_text(), "received after snapshot")
        self.assertFalse(list(self.live.glob(".uploads-restore-*")))

    def test_corrupt_upload_prevents_restore_before_database_changes(self):
        deploy_data.snapshot_bundle(self.live, self.bundle)
        (self.bundle / "uploads/talents/image.png").write_bytes(b"corrupt")
        original_db = (self.live / "base.db").read_bytes()
        with self.assertRaisesRegex(RuntimeError, "inventory mismatch"):
            deploy_data.restore_bundle(self.bundle, self.live)
        self.assertEqual((self.live / "base.db").read_bytes(), original_db)

    def test_extra_upload_is_detected(self):
        deploy_data.snapshot_bundle(self.live, self.bundle)
        (self.bundle / "uploads/extra.txt").write_text("unexpected")
        with self.assertRaises(RuntimeError):
            deploy_data.verify_bundle(self.bundle)

    def test_destination_inside_active_data_or_existing_refused(self):
        for destination in (self.live / "new", self.live, self.root):
            with self.assertRaises(ValueError):
                deploy_data.snapshot_bundle(self.live, destination)

    def test_symbolic_link_cannot_escape_upload_root(self):
        (self.live / "uploads/link").symlink_to(self.root / "outside")
        with self.assertRaises(ValueError):
            deploy_data.snapshot_bundle(self.live, self.bundle)
        self.assertFalse(self.bundle.exists())

    def test_database_link_cannot_copy_another_source(self):
        database = self.live / "base.db"
        database.rename(self.root / "outside.db")
        database.symlink_to(self.root / "outside.db")
        with self.assertRaises(ValueError):
            deploy_data.snapshot_bundle(self.live, self.bundle)
        self.assertFalse(self.bundle.exists())

    def test_concurrent_database_write_refuses_inconsistent_bundle(self):
        original_snapshot = deploy_data.snapshot
        calls = []

        def changing_snapshot(source, destination):
            calls.append(destination)
            if len(calls) == 2:
                with sqlite3.connect(source) as db:
                    db.execute("INSERT INTO talents VALUES(3, NULL)")
            return original_snapshot(source, destination)

        with patch("script.deploy_data.snapshot", side_effect=changing_snapshot):
            with self.assertRaisesRegex(RuntimeError, "changed during snapshot"):
                deploy_data.snapshot_bundle(self.live, self.bundle)
        self.assertFalse(self.bundle.exists())
        self.assertFalse(list(self.root.glob(".snapshot-*")))

    def test_manifest_path_injection_is_refused(self):
        deploy_data.snapshot_bundle(self.live, self.bundle)
        path = self.bundle / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["uploads"]["../../outside"] = manifest["uploads"].pop("talents/image.png")
        path.write_text(json.dumps(manifest))
        with self.assertRaises(RuntimeError):
            deploy_data.restore_bundle(self.bundle, self.live)
        self.assertFalse((self.root / "outside").exists())
