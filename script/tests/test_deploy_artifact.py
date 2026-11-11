"""Verify private/unsafe tar members cannot reach the DEV image."""

import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from script.deploy_artifact import validate_archive


class ArtifactTests(unittest.TestCase):
    def archive(self, name, kind=tarfile.REGTYPE):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "source.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.linkname = "/etc/passwd" if kind == tarfile.SYMTYPE else ""
            member.size = 2 if kind == tarfile.REGTYPE else 0
            archive.addfile(member, io.BytesIO(b"ok") if member.size else None)
        return path

    def test_application_asset_is_allowed(self):
        validate_archive(self.archive("./static/icons/instagram.svg"))

    def test_private_paths_and_databases_are_refused(self):
        for name in ("maquettes/apercu-prive/README.md", "monitoring/private.py",
                     "static/sephora.jpeg", "static/.env.production", "static/uploads/a.jpg",
                     "static/backup.db.gz", "static/private.sqlite3", "templates/data_prod/x", "static/a.db-wal"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_archive(self.archive(name))

    def test_traversal_absolute_and_symlink_members_are_refused(self):
        for name, kind in (("../app.py", tarfile.REGTYPE), ("/app.py", tarfile.REGTYPE),
                           ("static/linked", tarfile.SYMTYPE)):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_archive(self.archive(name, kind))
