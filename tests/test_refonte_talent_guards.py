"""Publication, visibilité privée des médias et migrations de la refonte."""

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.services import talent_service
from reunion_wiki.repositories import talent_repository


class TalentPublicationGuardsTest(unittest.TestCase):
    """Vérifie les limites métier réelles sur une base migrée jetable."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.db = self.root / 'base.db'
        self.uploads = self.root / 'uploads'
        self.environment = dict(os.environ, DATABASE_PATH=str(self.db), UPLOAD_FOLDER=str(self.uploads),
                                MAIL_ENABLED='false', FLASK_ENV='development')
        self._migrate()
        self.config = dict(app.config)
        app.config.update(TESTING=True, DATABASE_PATH=str(self.db), UPLOAD_FOLDER=str(self.uploads),
                          WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False, MAIL_ENABLED=False)
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO talent_categories(name,slug) VALUES ('Essai privé','essai-prive')")
            self.category = conn.execute("SELECT id FROM talent_categories WHERE slug='essai-prive'").fetchone()[0]
        self.data = dict(name='Profil de test', category_id=self.category, entity_type='person',
                         description='Présentation neutre du profil de test.', status='published')

    def tearDown(self):
        app.config.clear()
        app.config.update(self.config)
        self.directory.cleanup()

    def _migrate(self):
        result = subprocess.run([sys.executable, 'migrate.py'], env=self.environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def _create(self):
        talent_id, errors = talent_service.save_talent(self.data)
        self.assertEqual(errors, [])
        return talent_id

    def test_creation_and_edit_cannot_publish_even_with_forged_status(self):
        with app.app_context():
            talent_id = self._create()
            self.assertEqual(talent_repository.get_by_id(talent_id)['status'], 'draft')
            talent_service.save_talent(self.data, talent_id=talent_id)
            self.assertEqual(talent_repository.get_by_id(talent_id)['status'], 'draft')
            self.assertIsNone(talent_repository.get_published_by_slug('profil-de-test'))

    def test_publication_requires_private_verification_and_keeps_it_out_of_public_row(self):
        with app.app_context():
            talent_id = self._create()
            ok, errors = talent_service.publish(talent_id)
            self.assertFalse(ok)
            self.assertEqual(len(errors), 3)
            self.data.update(reunion_attachment='Activité à La Réunion vérifiée.',
                             private_source_reference='REFERENCE-PRIVEE-TEST',
                             private_source_url='https://example.org/source-verification',
                             private_source_note='NOTE-PRIVEE-TEST')
            talent_service.save_talent(self.data, talent_id=talent_id)
            self.assertEqual(talent_service.publish(talent_id), (True, []))
            row = talent_repository.get_published_by_slug('profil-de-test')
            self.assertIsNotNone(row)
            self.assertNotIn('private_source_reference', row.keys())
            response = app.test_client().get('/createurs/profil-de-test')
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'REFERENCE-PRIVEE-TEST', response.data)

    def test_upload_url_is_not_public_for_draft_or_archived_talent(self):
        image = self.uploads / 'talents' / 'private-test.jpg'
        image.parent.mkdir(parents=True)
        image.write_bytes(b'image-test')
        with app.app_context():
            talent_id = self._create()
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE talents SET image=? WHERE id=?", ('uploads/talents/private-test.jpg', talent_id))
        client = app.test_client()
        self.assertEqual(client.get('/static/uploads/talents/private-test.jpg').status_code, 404)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE talents SET status='published' WHERE id=?", (talent_id,))
        self.assertEqual(client.get('/static/uploads/talents/private-test.jpg').status_code, 200)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE talents SET status='archived' WHERE id=?", (talent_id,))
        self.assertEqual(client.get('/static/uploads/talents/private-test.jpg').status_code, 404)
        with client.session_transaction() as session:
            session['admin_authenticated'] = True
        response = client.get('/static/uploads/talents/private-test.jpg')
        self.assertEqual(response.status_code, 200)
        self.assertIn('no-store', response.headers['Cache-Control'])

    def test_repeated_migration_preserves_private_fields_and_linked_proposal(self):
        with app.app_context():
            talent_id = self._create()
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE talents SET private_source_note='NOTE-CONSERVEE' WHERE id=?", (talent_id,))
            conn.execute("INSERT INTO refonte_proposals(token,nonce,kind,name,url,url_key,talent_id) "
                         "VALUES ('token-test','nonce-test','personality','Essai','https://example.org/p','test',?)",
                         (talent_id,))
        self._migrate()
        self._migrate()
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT private_source_note FROM talents WHERE id=?", (talent_id,)).fetchone()[0],
                             'NOTE-CONSERVEE')
            self.assertEqual(conn.execute("SELECT talent_id FROM refonte_proposals WHERE token='token-test'").fetchone()[0], talent_id)
            self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_dev_is_not_indexable_and_admin_responses_are_not_cached(self):
        client = app.test_client()
        response = client.get('/robots.txt', base_url='https://dev.reunionwiki.re')
        self.assertIn(b'Disallow: /', response.data)
        self.assertIn('noindex', response.headers['X-Robots-Tag'])
        self.assertIn('no-store', client.get('/admin').headers['Cache-Control'])


if __name__ == '__main__':
    unittest.main()
