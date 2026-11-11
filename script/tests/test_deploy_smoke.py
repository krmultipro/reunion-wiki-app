"""Check failed HTTP responses cannot silently pass the deployment probes."""
from email.message import Message
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from script.deploy_smoke import check_pages, find_public_upload


class Response(io.BytesIO):
    def __init__(self, body=b'<html><input type="password"></html>', mime="text/html", status=200):
        super().__init__(body)
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = mime


class SmokeTests(unittest.TestCase):
    def responses(self):
        return [Response(), Response(), Response(), Response(b"ico", "image/x-icon")]

    @patch("script.deploy_smoke.urlopen")
    def test_representative_pages_and_upload_are_checked(self, request):
        request.side_effect = self.responses() + [Response(b"png", "image/png")]
        check_pages("http://127.0.0.1:8000", "/static/uploads/test.png")
        self.assertEqual([c.args[0] for c in request.call_args_list], [
            "http://127.0.0.1:8000/", "http://127.0.0.1:8000/recherche?q=reunion",
            "http://127.0.0.1:8000/admin/login", "http://127.0.0.1:8000/static/favicon.ico",
            "http://127.0.0.1:8000/static/uploads/test.png",
        ])

    @patch("script.deploy_smoke.urlopen")
    def test_search_error_fails_probe(self, request):
        request.side_effect = [Response(), HTTPError("search", 500, "failed", {}, None)]
        with self.assertRaises(HTTPError):
            check_pages("http://localhost")

    @patch("script.deploy_smoke.urlopen")
    def test_missing_login_form_fails_probe(self, request):
        request.side_effect = [Response(), Response(), Response(b"generic page")]
        with self.assertRaisesRegex(RuntimeError, "Login form"):
            check_pages("http://localhost")

    @patch("script.deploy_smoke.urlopen")
    def test_html_instead_of_image_fails_probe(self, request):
        request.side_effect = self.responses()[:3] + [Response()]
        with self.assertRaisesRegex(RuntimeError, "image"):
            check_pages("http://localhost")

    @patch("script.deploy_smoke.urlopen")
    def test_empty_html_fails_probe(self, request):
        request.return_value = Response(b"")
        with self.assertRaisesRegex(RuntimeError, "HTML"):
            check_pages("http://localhost")


class PublicUploadSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.database = self.root / "base.db"
        self.uploads = self.root / "uploads"
        self.uploads.mkdir()

    def test_draft_orphan_and_missing_images_are_never_chosen(self):
        for filename in ("a-orphan.png", "b-draft.png", "z-public.png"):
            (self.uploads / filename).write_bytes(b"image fixture")
        with sqlite3.connect(self.database) as db:
            db.execute("CREATE TABLE talents(image TEXT, status TEXT)")
            db.executemany("INSERT INTO talents VALUES(?, ?)", [
                ("uploads/b-draft.png", "draft"),
                ("uploads/c-missing.png", "published"),
                ("uploads/z-public.png", "published"),
            ])
        self.assertEqual(find_public_upload(self.database, self.uploads), "/static/uploads/z-public.png")

    def test_content_image_allowed_with_talents_table_absent(self):
        (self.uploads / "article.png").write_bytes(b"image fixture")
        with sqlite3.connect(self.database) as db:
            db.execute("CREATE TABLE content(featured_image TEXT, status TEXT)")
            db.execute("INSERT INTO content VALUES('uploads/article.png', 'published')")
        self.assertEqual(find_public_upload(self.database, self.uploads), "/static/uploads/article.png")

    def test_no_public_image_means_favicon_without_creating_database(self):
        (self.uploads / "orphan.png").write_bytes(b"image fixture")
        self.assertIsNone(find_public_upload(self.database, self.uploads))
        self.assertFalse(self.database.exists())
        with sqlite3.connect(self.database) as db:
            db.execute("CREATE TABLE talents(image TEXT, status TEXT)")
            db.execute("INSERT INTO talents VALUES('uploads/orphan.png', 'archived')")
        self.assertIsNone(find_public_upload(self.database, self.uploads))
