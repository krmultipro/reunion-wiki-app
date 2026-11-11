"""Exercise real SQLite WAL snapshots and offline restoration on disposable data."""
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from script.deploy_sqlite import restore, snapshot


class SQLiteDeployTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.live = self.root / "live.db"
        self.saved = self.root / "saved.db"
        with sqlite3.connect(self.live) as db:
            db.execute("CREATE TABLE items (value TEXT)")
            db.execute("INSERT INTO items VALUES ('before')")

    def values(self, path):
        with sqlite3.connect(path) as db:
            return [row[0] for row in db.execute("SELECT value FROM items")]

    def test_snapshot_includes_committed_wal_and_does_not_change_source(self):
        with sqlite3.connect(self.live) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("INSERT INTO items VALUES ('latest')")
            db.commit()
            self.assertTrue(Path(str(self.live) + "-wal").is_file())
            snapshot(self.live, self.saved)
            self.assertEqual(self.values(self.saved), ["before", "latest"])
            self.assertEqual(self.values(self.live), ["before", "latest"])
        with sqlite3.connect(self.saved) as db:
            self.assertEqual(db.execute("PRAGMA journal_mode").fetchone(), ("delete",))

    def test_final_snapshot_keeps_write_after_preliminary_snapshot(self):
        preliminary = self.root / "preflight.db"
        snapshot(self.live, preliminary)
        with sqlite3.connect(self.live) as db:
            db.execute("INSERT INTO items VALUES ('between snapshots')")
        snapshot(self.live, self.saved)
        with sqlite3.connect(self.live) as db:
            db.execute("DELETE FROM items")
        restore(self.saved, self.live)
        self.assertEqual(self.values(self.live), ["before", "between snapshots"])
        self.assertEqual(self.values(preliminary), ["before"])

    def test_restore_removes_stale_sidecars_and_preserves_permissions(self):
        snapshot(self.live, self.saved)
        os.chmod(self.live, 0o640)
        for suffix in ("-wal", "-shm", "-journal"):
            Path(str(self.live) + suffix).write_bytes(b"stale candidate data")
        restore(self.saved, self.live)
        self.assertEqual(self.values(self.live), ["before"])
        self.assertEqual(self.live.stat().st_mode & 0o777, 0o640)
        for suffix in ("-wal", "-shm", "-journal"):
            self.assertFalse(Path(str(self.live) + suffix).exists())

    def test_bad_snapshot_preserves_live_database_and_sidecars(self):
        self.saved.write_bytes(b"invalid")
        sidecar = Path(str(self.live) + "-wal")
        sidecar.write_bytes(b"keep")
        original = self.live.read_bytes()
        with self.assertRaises(sqlite3.DatabaseError):
            restore(self.saved, self.live)
        self.assertEqual(self.live.read_bytes(), original)
        self.assertEqual(sidecar.read_bytes(), b"keep")
        self.assertFalse(list(self.root.glob(".restore-*")))

    def test_missing_snapshot_does_not_create_an_empty_backup(self):
        with self.assertRaises(sqlite3.OperationalError):
            restore(self.saved, self.live)
        self.assertFalse(self.saved.exists())
        self.assertEqual(self.values(self.live), ["before"])

    def test_permission_failure_is_propagated_before_live_data_changes(self):
        snapshot(self.live, self.saved)
        original = self.live.read_bytes()
        with patch("script.deploy_sqlite.os.chown", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                restore(self.saved, self.live)
        self.assertEqual(self.live.read_bytes(), original)

    def test_same_file_rejected(self):
        for operation in (snapshot, restore):
            with self.assertRaises(ValueError):
                operation(self.live, self.live)
