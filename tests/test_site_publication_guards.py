"""Régressions COR-SITE-02 : les données stockées sont revalidées à publication."""

import sqlite3
import unittest

from reunion_wiki.app import app
from reunion_wiki.services.site_http_service import HttpCheckResult, ACCESSIBLE, MANUAL_REVIEW
from tests import test_site_publication as publication_fixture


class StoredPublicationGuardsTests(unittest.TestCase):
    """Exerce les vraies routes et une base jetable, pas une nouvelle saisie valide."""

    def setUp(self):
        """Prépare le schéma et une session admin avec la fixture existante."""
        self.fixture = publication_fixture.SitePublicationTestCase()
        self.fixture.setUp()
        self.client = self.fixture.client
        with self.client.session_transaction() as session:
            session['admin_authenticated'] = True
            session['admin_username'] = 'guard-admin'

    def tearDown(self):
        """Restaure la configuration et supprime les données de test."""
        self.fixture.tearDown()

    def insert(self, **changes):
        """Insère une ancienne fiche, potentiellement non conforme aux formulaires."""
        values = dict(nom='Site ancien', lien='https://stored.example',
                      description='Description neutre suffisamment longue.', category_id=1)
        values.update(changes)
        with sqlite3.connect(self.fixture.database_path) as db:
            cursor = db.execute(
                """INSERT INTO sites(nom,lien,description,category_id,status,date_ajout)
                   VALUES(?,?,?,?,'en_attente',CURRENT_TIMESTAMP)""",
                tuple(values[key] for key in ['nom', 'lien', 'description', 'category_id']),
            )
            return cursor.lastrowid

    def status(self, identifier):
        """Lit le statut final sans se fier au seul code HTTP de la route."""
        with sqlite3.connect(self.fixture.database_path) as db:
            return db.execute('SELECT status FROM sites WHERE id=?', (identifier,)).fetchone()[0]

    def approve(self, identifier, url='https://stored.example'):
        """Soumet la décision éditoriale qui déclenche le contrôle puis publication."""
        return self.client.post(f'/admin/propositions/{identifier}/editorial-review',
                                data={'reviewed_url': url, 'criterion': 'reunion_content'})

    def test_stored_invalid_data_never_becomes_public(self):
        """COR02-STORED — Chaque donnée obligatoire est revalidée pour une fiche ancienne."""
        for index, changes in enumerate([dict(nom=''), dict(nom='x'), dict(description=''),
                        dict(description='court'), dict(category_id=None),
                        dict(category_id=999), dict(lien='javascript:alert(1)')]):
            with self.subTest(changes=changes):
                # Une URL unique empêche le contrôle anti-doublon de masquer
                # une régression sur le champ réellement exercé.
                values = dict(lien=f'https://stored-{index}.example')
                values.update(changes)
                identifier = self.insert(**values)
                response = self.approve(identifier, values['lien'])
                self.assertEqual(response.status_code, 302)
                self.assertEqual(self.status(identifier), 'en_attente')

    def test_manual_confirmation_rechecks_stored_data(self):
        """COR02-STORED — Une revue 403 n'autorise pas une fiche devenue incomplète."""
        identifier = self.insert()
        app.config['SITE_HTTP_CHECKER'] = lambda url: HttpCheckResult(
            MANUAL_REVIEW, url, url, 403, 'Contrôle simulé exigeant une confirmation.')
        review = self.approve(identifier)
        check_id = int(review.location.rsplit('/', 1)[-1])
        with sqlite3.connect(self.fixture.database_path) as db:
            db.execute('UPDATE sites SET description=? WHERE id=?', ('', identifier))
        response = self.client.post(review.location, data={
            'site_id': identifier, 'check_id': check_id,
            'note': 'Site consulté en navigation privée pour le contrôle.'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.status(identifier), 'en_attente')
        with sqlite3.connect(self.fixture.database_path) as db:
            approved = db.execute('SELECT manually_approved_at FROM site_http_checks WHERE id=?',
                                  (check_id,)).fetchone()[0]
        self.assertIsNone(approved)

    def test_data_changed_during_http_check_is_not_published(self):
        """COR02-RACE — Le dernier verrou transactionnel relit les données courantes."""
        identifier = self.insert()
        def checker(url):
            with sqlite3.connect(self.fixture.database_path) as db:
                db.execute('UPDATE sites SET description=? WHERE id=?', ('', identifier))
            return HttpCheckResult(ACCESSIBLE, url, url, 200, 'Réponse simulée accessible.')
        app.config['SITE_HTTP_CHECKER'] = checker
        self.approve(identifier)
        self.assertEqual(self.status(identifier), 'en_attente')

    def test_legacy_duplicate_is_blocked_at_publication(self):
        """COR02-STORED — Des doublons historiques ne sont pas publiés silencieusement."""
        self.insert()
        duplicate = self.insert(lien='http://STORED.example/')
        self.approve(duplicate, 'http://STORED.example/')
        self.assertEqual(self.status(duplicate), 'en_attente')

    def test_valid_stored_site_can_still_be_published(self):
        """Préserve le parcours nominal de la publication existante."""
        identifier = self.insert()
        self.approve(identifier)
        self.assertEqual(self.status(identifier), 'valide')


if __name__ == '__main__':
    unittest.main()
