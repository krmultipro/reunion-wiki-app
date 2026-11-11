"""Parcours publics de la refonte : vraies lectures SQLite et confidentialité."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from reunion_wiki.app import app
from reunion_wiki.services import refonte_public_service as service


class RefontePublicTestCase(unittest.TestCase):
    """Teste visibilité, navigation et échappement sur une base isolée."""

    def setUp(self):
        """Installe des publications, brouillons et données privées distinctes."""
        self.directory = tempfile.TemporaryDirectory()
        self.database = Path(self.directory.name) / 'public.db'
        self.previous = {key: app.config.get(key) for key in ('TESTING', 'DATABASE_PATH', 'WTF_CSRF_ENABLED', 'RATELIMIT_ENABLED')}
        app.config.update(TESTING=True, DATABASE_PATH=str(self.database), WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False)
        with sqlite3.connect(self.database) as connection:
            connection.executescript('''
                CREATE TABLE categories(id INTEGER PRIMARY KEY, nom TEXT, slug TEXT, created_at TEXT);
                INSERT INTO categories VALUES(1,'Culture','culture',NULL),(2,'Transport','transport',NULL);
                CREATE TABLE sites(id INTEGER PRIMARY KEY, nom TEXT, lien TEXT, description TEXT,
                    category_id INTEGER, status TEXT, published_at TEXT);
                INSERT INTO sites VALUES(1,'Bus Péï','https://bus.example','Transport local',2,'valide','2026-01-01');
                INSERT INTO sites VALUES(2,'SECRET_SITE_PENDING','https://pending.example','Private',1,'en_attente',NULL);
                INSERT INTO sites VALUES(3,'SECRET_SITE_ARCHIVE','https://archive.example','Private',1,'archive',NULL);
                INSERT INTO sites VALUES(4,'Zéphyr','https://zephyr.example','Culture en images',1,'valide','2026-03-01');
                CREATE TABLE talent_categories(id INTEGER PRIMARY KEY, name TEXT, slug TEXT);
                INSERT INTO talent_categories VALUES(1,'Culture','culture'),(2,'Humour','humour');
                CREATE TABLE talents(id INTEGER PRIMARY KEY, name TEXT, slug TEXT, description TEXT,
                    bio TEXT,image TEXT,category_id INTEGER, instagram_url TEXT,youtube_url TEXT,
                    tiktok_url TEXT,facebook_url TEXT,website_url TEXT,status TEXT,published_at TEXT,
                    source_private TEXT,email_private TEXT);
                INSERT INTO talents VALUES(1,'Zoé','zoe','Culture et vidéo','Premier paragraphe.\n\n<script>alert("unsafe")</script>',NULL,1,
                    'https://instagram.com/zoe',NULL,'javascript:alert(1)',NULL,NULL,'published','2026-02-01','PRIVATE_SOURCE_TOKEN','PRIVATE_EMAIL_TOKEN');
                INSERT INTO talents VALUES(2,'SECRET_DRAFT','secret-draft','Private','Private',NULL,1,NULL,NULL,NULL,NULL,NULL,'draft',NULL,'PRIVATE_SOURCE_TOKEN','PRIVATE_EMAIL_TOKEN');
                INSERT INTO talents VALUES(3,'SECRET_ARCHIVE','secret-archive','Private','Private',NULL,1,NULL,NULL,NULL,NULL,NULL,'archived',NULL,NULL,NULL);
                INSERT INTO talents VALUES(4,'Amélie','amelie','Culture et photos','Présentation publique.',NULL,1,NULL,NULL,NULL,NULL,NULL,'published','2026-04-01',NULL,NULL);
                INSERT INTO talents VALUES(5,'Bilal','bilal','Humour','Présentation publique.',NULL,2,NULL,NULL,NULL,NULL,NULL,'published','2026-01-01',NULL,NULL);
            ''')
        self.client = app.test_client()

    def tearDown(self):
        """Restaure la configuration sans toucher à une base active."""
        app.config.update(self.previous)
        self.directory.cleanup()

    def html(self, path):
        """Retourne le HTML d'une route réussie."""
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, path)
        return response.get_data(as_text=True)

    def test_private_records_never_render(self):
        """Les quatre entrées publiques excluent tous les champs et statuts privés."""
        for path in ('/', '/sites', '/createurs-reunionnais', '/recherche?q=Culture'):
            text = self.html(path)
            for secret in ('SECRET_SITE_PENDING', 'SECRET_SITE_ARCHIVE', 'SECRET_DRAFT', 'SECRET_ARCHIVE', 'PRIVATE_SOURCE_TOKEN', 'PRIVATE_EMAIL_TOKEN'):
                self.assertNotIn(secret, text, path)
            self.assertNotIn('Outils de la maquette', text)
            self.assertNotIn('apercu-prive', text)

    def test_profile_privacy_safe_text_links_and_fallback(self):
        """La fiche échappe le texte et refuse une URL réseau dangereuse."""
        text = self.html('/createurs/zoe')
        self.assertIn('&lt;script&gt;', text)
        self.assertNotIn('<script>alert', text)
        self.assertNotIn('javascript:alert', text)
        self.assertIn('/static/refonte/profile-placeholder.svg', text)
        self.assertIn('https://instagram.com/zoe', text)
        self.assertIn('noopener noreferrer', text)
        self.assertIn('À découvrir aussi', text)
        self.assertNotIn('Bilal', text)
        for path in ('/createurs/secret-draft','/createurs/secret-archive','/createurs/inconnu'):
            self.assertEqual(self.client.get(path).status_code,404)

    def test_category_and_normalized_search_combine(self):
        """Accents/casse et catégorie se combinent sans restriction silencieuse."""
        text = self.html('/createurs-reunionnais?q=AMELIE&categorie=culture')
        self.assertIn('Amélie', text)
        self.assertNotIn('Zoé', text)
        text = self.html('/createurs-reunionnais?q=AMELIE&categorie=humour')
        self.assertIn('Aucune personnalité ne correspond', text)
        text = self.html('/sites?categorie=inconnue')
        self.assertIn('Cette catégorie n’existe pas', text)
        self.assertIn('Bus Péï', text)

    def test_list_alphabet_and_home_publication_order(self):
        """Liste alphabétique et accueil récent utilisent deux ordres explicites."""
        text = self.html('/createurs-reunionnais')
        self.assertLess(text.index('>Amélie<'), text.index('>Bilal<'))
        self.assertLess(text.index('>Bilal<'), text.index('>Zoé<'))
        text = self.html('/')
        self.assertLess(text.index('>Amélie<'), text.index('>Zoé<'))
        self.assertLess(text.index('>Zoé<'), text.index('>Bilal<'))

    def test_sites_use_counter_and_category_has_no_inherited_query(self):
        """Les clics gardent la route compteur et le résultat catégorie retire q."""
        text = self.html('/sites?q=bus')
        self.assertIn('href="/go/1"', text)
        self.assertNotIn('href="https://bus.example"', text)
        text = self.html('/recherche?q=Culture')
        self.assertIn('href="/categorie/culture"', text)
        self.assertNotIn('href="/categorie/culture?q=', text)
        text = self.html('/categorie/transport')
        self.assertIn('Bus Péï', text)
        self.assertNotIn('Zéphyr', text)

    def test_returns_and_direct_navigation(self):
        """Retours autorisés conservent critères et refusent les destinations externes."""
        text = self.html('/createurs/zoe?retour=%2Fcreateurs-reunionnais%3Fq%3Dzoe')
        self.assertIn('href="/createurs-reunionnais?q=zoe"', text)
        text = self.html('/createurs/zoe?retour=https://example.org')
        self.assertIn('href="/createurs-reunionnais"', text)
        with app.test_request_context('/'):
            for value in ('https://evil.example','//evil.example','/admin','/\\evil.example','/sites\nLocation: evil'):
                self.assertEqual(service.safe_return(value), '/')

    def test_support_routes_and_noscript_content(self):
        """Aides et contenu principal sont rendus sans dépendre de JavaScript."""
        self.assertEqual(self.html('/faq').count('<details>'),8)
        self.assertIn('forms.gle/GScJkMiEZXVSted78', self.html('/contact'))
        self.assertIn('Mentions', self.html('/mentions-legales'))
        text = self.html('/sites')
        self.assertIn('Bus Péï',text)
        self.assertIn('Aller au contenu',text)
        self.assertIn('Navigation mobile',text)


if __name__ == '__main__':
    unittest.main()
