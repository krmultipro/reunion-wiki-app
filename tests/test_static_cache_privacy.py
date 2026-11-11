"""Cache des ressources publiques et confidentialité des parcours avec session."""

from html.parser import HTMLParser
import os
from pathlib import Path
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlparse

from flask import session

from reunion_wiki.app import app


class BrandAssets(HTMLParser):
    """Relève les ressources de marque réellement référencées par la page."""

    def __init__(self):
        super().__init__()
        self.logo = None
        self.icon = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'img' and values.get('width') == '44':
            self.logo = values['src']
        if tag == 'link' and values.get('rel') == 'icon':
            self.icon = values['href']


class StaticCachePrivacyTest(unittest.TestCase):
    """Vérifie les réponses Flask réelles sur une base et des médias jetables."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.db = self.root / 'base.db'
        self.uploads = self.root / 'uploads'
        environment = dict(os.environ, DATABASE_PATH=str(self.db),
                           UPLOAD_FOLDER=str(self.uploads), MAIL_ENABLED='false',
                           FLASK_ENV='development', RATELIMIT_STORAGE_URL='memory://')
        result = subprocess.run([sys.executable, 'migrate.py'], env=environment,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.config = dict(app.config)
        app.config.update(TESTING=True, DATABASE_PATH=str(self.db),
                          UPLOAD_FOLDER=str(self.uploads), RATELIMIT_ENABLED=False,
                          WTF_CSRF_ENABLED=False, MAIL_ENABLED=False)
        self.client = app.test_client()

    def tearDown(self):
        app.config.clear()
        app.config.update(self.config)
        self.directory.cleanup()

    def assert_private(self, response):
        self.assertTrue(response.cache_control.private, response.headers)
        self.assertTrue(response.cache_control.no_store, response.headers)
        self.assertFalse(response.cache_control.public, response.headers)

    def test_public_assets_are_cacheable_with_or_without_session(self):
        for state in ('anonymous', 'invalid-cookie', 'admin'):
            client = app.test_client()
            if state == 'invalid-cookie':
                client.set_cookie('session', 'invalid-diagnostic-cookie')
            elif state == 'admin':
                with client.session_transaction() as session:
                    session.permanent = True
                    session['admin_authenticated'] = True
                    session['private_test_marker'] = 'SESSION-MUST-NOT-LEAK'
            for path in ('/static/refonte/app.css', '/static/refonte/public.js',
                         '/static/fonts/inter-v18-latin-regular.woff2',
                         '/static/refonte/logo-r.png'):
                with self.subTest(state=state, path=path):
                    response = client.get(path, buffered=True)
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.cache_control.public, response.headers)
                    self.assertFalse(response.cache_control.no_store, response.headers)
                    self.assertGreater(response.cache_control.max_age, 0)
                    self.assertNotIn('Set-Cookie', response.headers)
                    self.assertNotIn('Cookie', response.vary)
                    self.assertNotIn(b'SESSION-MUST-NOT-LEAK', response.data)

    def test_static_etag_revalidation_is_cacheable_with_session(self):
        with self.client.session_transaction() as session:
            session.permanent = True
            session['admin_authenticated'] = True
        first = self.client.get('/static/refonte/app.css', buffered=True)
        response = self.client.get('/static/refonte/app.css',
                                   headers={'If-None-Match': first.headers['ETag']}, buffered=True)
        self.assertEqual(response.status_code, 304)
        self.assertEqual(response.data, b'')
        self.assertTrue(response.cache_control.public, response.headers)
        self.assertFalse(response.cache_control.no_store, response.headers)
        self.assertNotIn('Set-Cookie', response.headers)
        self.assertNotIn('Cookie', response.vary)

    def test_static_head_and_partial_response_follow_cache_contract(self):
        with self.client.session_transaction() as session:
            session.permanent = True
            session['admin_authenticated'] = True
        head = self.client.head('/static/refonte/app.css', buffered=True)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.data, b'')
        self.assertTrue(head.cache_control.public)
        self.assertNotIn('Set-Cookie', head.headers)
        partial = self.client.get('/static/refonte/app.css', headers={'Range': 'bytes=0-9'}, buffered=True)
        self.assertEqual(partial.status_code, 206)
        self.assert_private(partial)

    def test_missing_static_is_not_publicly_cacheable(self):
        for has_session in (False, True):
            client = app.test_client()
            if has_session:
                client.set_cookie('session', 'invalid-diagnostic-cookie')
            response = client.get('/static/refonte/missing-resource.css', buffered=True)
            self.assertEqual(response.status_code, 404)
            self.assertFalse(response.cache_control.public, response.headers)
            if has_session:
                self.assert_private(response)

    def test_private_routes_and_redirects_remain_no_store(self):
        for authenticated in (False, True):
            client = app.test_client()
            if authenticated:
                with client.session_transaction() as session:
                    session.permanent = True
                    session['admin_authenticated'] = True
            for path in ('/admin', '/admin/login', '/proposer',
                         '/proposition-confirmee/unknown-token'):
                with self.subTest(authenticated=authenticated, path=path):
                    response = client.get(path, buffered=True)
                    self.assert_private(response)

    def test_public_html_with_session_remains_private(self):
        self.client.set_cookie('session', 'invalid-diagnostic-cookie')
        response = self.client.get('/faq', buffered=True)
        self.assertEqual(response.status_code, 200)
        self.assert_private(response)

    def test_permanent_session_still_refreshes_on_private_document(self):
        with self.client.session_transaction() as session:
            session.permanent = True
            session['admin_authenticated'] = True
        response = self.client.get('/faq', buffered=True)
        self.assertEqual(response.status_code, 200)
        self.assert_private(response)
        self.assertIn('Set-Cookie', response.headers)
        self.assertIn('Cookie', response.vary)

    def test_session_mutation_still_sets_cookie_and_forbids_storage(self):
        original = app.view_functions['static']

        def mutate_session(filename):
            session['mutation_test'] = 'preserved'
            response = original(filename=filename)
            response.vary.add('Accept-Encoding')
            return response

        with patch.dict(app.view_functions, {'static': mutate_session}):
            response = self.client.get('/static/refonte/app.css', buffered=True)
        self.assertEqual(response.status_code, 200)
        self.assert_private(response)
        self.assertIn('Set-Cookie', response.headers)
        self.assertIn('Accept-Encoding', response.vary)
        with self.client.session_transaction() as saved:
            self.assertEqual(saved['mutation_test'], 'preserved')

    def test_service_worker_remains_no_store(self):
        for has_session in (False, True):
            client = app.test_client()
            if has_session:
                client.set_cookie('session', 'invalid-diagnostic-cookie')
            response = client.get('/service-worker.js', buffered=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.cache_control.no_store)
            self.assertFalse(response.cache_control.public)

    def test_upload_cache_never_overrides_publication_control(self):
        image = self.uploads / 'talents' / 'cache-privacy.jpg'
        image.parent.mkdir(parents=True)
        image.write_bytes(b'CONTROLLED-MEDIA-CONTENT')
        with sqlite3.connect(self.db) as db:
            category = db.execute("INSERT INTO talent_categories(name,slug) VALUES ('Test','cache-test')").lastrowid
            talent = db.execute("INSERT INTO talents(name,slug,category_id,entity_type,status,image,description) "
                                "VALUES ('Test','cache-test',?,'person','draft',?,'Description de test')",
                                (category, 'uploads/talents/cache-privacy.jpg')).lastrowid
        path = '/static/uploads/talents/cache-privacy.jpg'
        for status in ('draft', 'published', 'archived'):
            with sqlite3.connect(self.db) as db:
                db.execute('UPDATE talents SET status=? WHERE id=?', (status, talent))
            for authenticated in (False, True):
                client = app.test_client()
                if authenticated:
                    with client.session_transaction() as session:
                        session.permanent = True
                        session['admin_authenticated'] = True
                with self.subTest(status=status, authenticated=authenticated):
                    response = client.get(path, buffered=True)
                    allowed = authenticated or status == 'published'
                    self.assertEqual(response.status_code, 200 if allowed else 404)
                    self.assert_private(response)
                    if allowed:
                        conditional = client.get(path, headers={'If-None-Match': response.headers['ETag']}, buffered=True)
                        self.assertEqual(conditional.status_code, 304)
                        self.assert_private(conditional)
                    if not allowed:
                        self.assertNotIn(b'CONTROLLED-MEDIA-CONTENT', response.data)

    def test_rendered_brand_logo_and_favicon_are_lightweight(self):
        response = self.client.get('/faq', buffered=True)
        self.assertEqual(response.status_code, 200)
        assets = BrandAssets()
        assets.feed(response.get_data(as_text=True))
        self.assertIsNotNone(assets.logo)
        self.assertEqual(assets.icon, assets.logo)
        self.assertNotEqual(urlparse(assets.logo).path, '/static/refonte/logo-r.png')
        logo = self.client.get(assets.logo, buffered=True)
        self.assertEqual(logo.status_code, 200)
        self.assertLessEqual(len(logo.data), 60 * 1024)
        self.assertEqual(logo.data[:8], b'\x89PNG\r\n\x1a\n')
        width, height = struct.unpack('>II', logo.data[16:24])
        self.assertEqual(width, height)
        self.assertGreaterEqual(width, 132)


if __name__ == '__main__':
    unittest.main()
