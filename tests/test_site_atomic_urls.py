"""Régressions COR-SITE-03 : unicité pendant les écritures concurrentes."""

from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading
import unittest
from unittest.mock import patch

from reunion_wiki.app import app
from reunion_wiki.repositories import site_repository
from reunion_wiki.services import site_url_service
from tests import test_site_publication as publication_fixture


class AtomicSiteUrlsTests(unittest.TestCase):
    """Force les interleavings qui contournaient le contrôle avant écriture."""

    def setUp(self):
        """Réutilise une base jetable complète pour le formulaire public."""
        self.fixture = publication_fixture.SitePublicationTestCase()
        self.fixture.setUp()

    def tearDown(self):
        """Supprime les données et restaure les réglages de Flask."""
        self.fixture.tearDown()

    def rows(self):
        """Retourne les URL stockées après les requêtes concurrentes."""
        with sqlite3.connect(self.fixture.database_path) as db:
            return db.execute('SELECT id,lien FROM sites ORDER BY id').fetchall()

    def create(self, url):
        """Appelle le repository sous un contexte propre au thread."""
        with app.app_context():
            return site_repository.create_site('Site audit', None, url,
                'Description neutre suffisamment longue.', 1, submitted=True)

    def test_concurrent_public_submissions_only_insert_one_site(self):
        """COR03-CONCURRENT — Le second POST concurrent est refusé, sans doublon."""
        barrier = threading.Barrier(2)
        prepare = site_url_service.prepare_site_url
        def synchronize(*args, **kwargs):
            decision = prepare(*args, **kwargs)
            barrier.wait(timeout=5)
            return decision
        def submit(index):
            with app.test_client() as client:
                return client.post('/proposer-site', data={
                    'nom': 'Site audit', 'lien': 'https://concurrent.example',
                    'description': 'Description neutre suffisamment longue.',
                    'categorie': 'Gastronomie', 'ville': '', 'portee': '', 'honeypot': ''},
                    environ_overrides={'REMOTE_ADDR': f'192.0.2.{130+index}'})
        with patch.object(site_url_service, 'prepare_site_url', side_effect=synchronize):
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(pool.map(submit, range(2)))
        self.assertEqual(sorted(r.status_code for r in responses), [200, 302])
        rejected = next(r for r in responses if r.status_code == 200)
        self.assertIn('déjà', rejected.get_data(as_text=True))
        self.assertEqual(len(self.rows()), 1)

    def test_repository_blocks_equivalent_url_without_route_precheck(self):
        """Le verrou d'écriture applique aussi l'équivalence HTTP/HTTPS et tracking."""
        self.create('https://EXAMPLE.test/Service?utm_source=test')
        with self.assertRaises(site_url_service.DuplicateSiteUrlError):
            self.create('http://example.test/Service/')
        self.assertEqual(len(self.rows()), 1)

    def test_two_edits_cannot_adopt_the_same_url(self):
        """COR03-EDIT — Les écritures de deux fiches préservent l'unicité."""
        identifiers = [self.create('https://first.example'), self.create('https://second.example')]
        barrier = threading.Barrier(2)
        def edit(identifier):
            with app.app_context():
                barrier.wait(timeout=5)
                try:
                    site_repository.update_site(identifier, 'Site audit', None,
                        'https://target.example', 'Description neutre suffisamment longue.',
                        1, 'en_attente', 0, expected_status='en_attente')
                    return 'saved'
                except site_url_service.DuplicateSiteUrlError:
                    return 'duplicate'
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(edit, identifiers))
        self.assertEqual(sorted(outcomes), ['duplicate', 'saved'])
        self.assertEqual(sum(url == 'https://target.example' for _, url in self.rows()), 1)

    def test_distinct_paths_case_and_functional_queries_remain_distinct(self):
        """COR03-DISTINCT — L'unicité ne fusionne pas des services différents."""
        for url in ['https://distinct.example/Service', 'https://distinct.example/service',
                    'https://distinct.example/service?id=1', 'https://distinct.example/service?id=2']:
            self.create(url)
        self.assertEqual(len(self.rows()), 4)


if __name__ == '__main__':
    unittest.main()
