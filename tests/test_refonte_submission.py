"""Anonymous submission and minimal moderation on disposable SQLite databases."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from flask import Flask
from jinja2 import ChoiceLoader, DictLoader
from reunion_wiki.extensions import csrf, limiter
from reunion_wiki.routes.refonte_submission import refonte_submission_bp
from reunion_wiki.refonte_schema import ensure_schema
from reunion_wiki.repositories import refonte_submission_repository as repository
from reunion_wiki.services import refonte_submission_service as service
from reunion_wiki.services import talent_service
from reunion_wiki.services.site_http_service import ACCESSIBLE, HttpCheckResult
from tests import test_site_publication
from migrate import _ensure_talent_categories_table, _create_final_talents_table


class RefonteSubmissionTest(unittest.TestCase):
    """Prove persistence, privacy and separate draft/publication actions."""
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.directory.name)/'test.db'
        test_site_publication.SitePublicationTestCase._create_schema(self)
        connection = sqlite3.connect(self.database_path)
        _ensure_talent_categories_table(connection.cursor())
        _create_final_talents_table(connection.cursor())
        connection.execute("INSERT INTO talent_categories(name,slug) VALUES ('Création','creation')")
        ensure_schema(connection)
        ensure_schema(connection)
        connection.commit()
        connection.close()
        root = Path(__file__).resolve().parents[1]
        self.app = Flask('refonte-tests',template_folder=str(root/'templates'))
        self.app.config.update(SECRET_KEY='only-test-secret',TESTING=True,DATABASE_PATH=str(self.database_path),WTF_CSRF_ENABLED=False,RATELIMIT_ENABLED=False)
        self.app.jinja_loader = ChoiceLoader([DictLoader({'refonte/base.html':'{% block content %}{% endblock %}','admin/base.html':'{% block content %}{% endblock %}'}),self.app.jinja_loader])
        self.app.register_blueprint(refonte_submission_bp)
        for endpoint,path in [('accueil','/'),('admin_login','/admin/login'),('admin_sites','/admin/sites'),('admin_talents.list_talents','/admin/talents'),('refonte_public.sites','/sites'),('creators.creator_detail','/createurs/<slug>')]:
            self.app.add_url_rule(path,endpoint,lambda **kw:'test')
        csrf.init_app(self.app)
        limiter.init_app(self.app)
        self.context = self.app.app_context()
        self.context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.context.pop()
        self.directory.cleanup()

    def data(self,kind='personality',**overrides):
        self.client.get('/proposer?type='+kind)
        with self.client.session_transaction() as session:
            nonce = session['proposal_nonces'][-1]
        data = dict(kind=kind,nonce=nonce,name='Profil exemple',url='https://example.org/profil',category_id='0',description='',email='',reunion_attachment='',honeypot='')
        if kind == 'site':
            data.update(category_id='1',description='Un site utile consacré à La Réunion.')
        data.update(overrides)
        return data

    def admin(self):
        with self.client.session_transaction() as session:
            session['admin_authenticated']=True
            session['admin_username']='test-admin'

    def test_minimal_personality_is_pending_and_confirmation_is_private(self):
        payload = self.data(email='private@example.org')
        result = self.client.post('/proposer',data=payload)
        self.assertEqual(result.status_code,303)
        receipt = self.client.get(result.location)
        self.assertEqual(receipt.status_code,200)
        self.assertIn('no-store',receipt.headers['Cache-Control'])
        self.assertNotIn(b'private@example.org',receipt.data)
        self.assertEqual(self.app.test_client().get(result.location).status_code,404)
        rows = repository.list_all()
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['status'],'pending')
        self.assertIsNone(rows[0]['talent_id'])
        self.assertEqual(sqlite3.connect(self.database_path).execute('SELECT COUNT(*) FROM talents').fetchone()[0],0)

    def test_double_post_same_nonce_is_idempotent_and_nonpublic_duplicate_is_neutral(self):
        payload = self.data()
        first = self.client.post('/proposer',data=payload)
        second = self.client.post('/proposer',data=payload)
        self.assertEqual(first.location,second.location)
        duplicate = self.client.post('/proposer',data=self.data())
        self.assertEqual(duplicate.status_code,422)
        self.assertIn('déjà enregistré',duplicate.get_data(as_text=True))
        self.assertNotIn('pending',duplicate.get_data(as_text=True))
        self.assertNotIn('propositions/1',duplicate.get_data(as_text=True))
        self.assertEqual(len(repository.list_all()),1)

    def test_site_submission_is_pending_and_four_required_fields_are_enforced(self):
        invalid = self.data('site',description='')
        response = self.client.post('/proposer',data=invalid)
        self.assertEqual(response.status_code,422)
        self.assertEqual(len(repository.list_all()),0)
        valid = self.client.post('/proposer',data=self.data('site'))
        self.assertEqual(valid.status_code,303)
        proposal=repository.list_all()[0]
        row=sqlite3.connect(self.database_path).execute('SELECT status FROM sites WHERE id=?',(proposal['site_id'],)).fetchone()
        self.assertEqual(row[0],'en_attente')

    def test_preparation_then_publication_requires_private_evidence(self):
        self.client.post('/proposer',data=self.data())
        proposal=repository.list_all()[0]
        self.admin()
        values=dict(proposal)
        values.update(action='prepare',category_id='1',description='Présentation neutre du profil.',kind='personality')
        path='/admin/refonte/propositions/'+str(proposal['id'])
        result=self.client.post(path,data=values)
        self.assertEqual(result.status_code,303)
        prepared=repository.get(proposal['id'])
        talent=talent_service.get_talent(prepared['talent_id'])
        self.assertEqual(talent['status'],'draft')
        values.update(action='publish',confirm='yes')
        result=self.client.post(path,data=values)
        self.assertEqual(result.status_code,422)
        self.assertEqual(talent_service.get_talent(talent['id'])['status'],'draft')
        values.update(reunion_attachment='Activité durable à La Réunion',private_source_reference='Bio officielle',private_source_url='https://example.org/source',private_source_note='Note privée')
        result=self.client.post(path,data=values)
        self.assertEqual(result.status_code,303)
        self.assertEqual(talent_service.get_talent(talent['id'])['status'],'published')
        values.update(action='archive',confirm='yes')
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        self.assertEqual(talent_service.get_talent(talent['id'])['status'],'archived')

    def test_refusal_requires_reason_and_anonymous_admin_access_is_denied(self):
        self.client.post('/proposer',data=self.data('site'))
        proposal=repository.list_all()[0]
        path='/admin/refonte/propositions/'+str(proposal['id'])
        self.assertEqual(self.client.get(path).status_code,302)
        self.admin()
        values=dict(proposal,action='reject')
        self.assertEqual(self.client.post(path,data=values).status_code,422)
        self.assertEqual(repository.get(proposal['id'])['status'],'pending')
        values['refusal_reason']='editorial_scope'
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        self.assertEqual(repository.get(proposal['id'])['status'],'refused')

    def test_forged_nonce_csrf_and_service_validation_cannot_persist(self):
        payload=self.data(nonce='forged')
        self.assertEqual(self.client.post('/proposer',data=payload).status_code,422)
        self.assertEqual(len(repository.list_all()),0)
        with self.assertRaises(service.ProposalError):
            service.submit(dict(kind='personality',name='Test',url='javascript:alert(1)'), 'valid-length-test-nonce-123')
        self.app.config['WTF_CSRF_ENABLED']=True
        self.assertEqual(self.client.post('/proposer',data=payload).status_code,400)
        self.admin()
        self.assertEqual(self.client.post('/admin/refonte/propositions/1',data={}).status_code,400)

    def test_site_publication_uses_existing_editorial_and_http_controls(self):
        self.client.post('/proposer',data=self.data('site'))
        proposal=repository.list_all()[0]
        self.admin()
        values=dict(proposal,action='prepare')
        path='/admin/refonte/propositions/'+str(proposal['id'])
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        values.update(action='publish',confirm='yes')
        self.assertEqual(self.client.post(path,data=values).status_code,422)
        self.assertEqual(repository.get_site_record(proposal['site_id'])['status'],'en_attente')
        self.app.config['SITE_HTTP_CHECKER']=lambda url: HttpCheckResult(ACCESSIBLE,url,url,200,'Test accessible.')
        values.update(editorial_criterion='reunion_content')
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        self.assertEqual(repository.get_site_record(proposal['site_id'])['status'],'valide')
        self.assertEqual(repository.get(proposal['id'])['status'],'published')

    def test_site_and_proposal_rollback_together(self):
        payload=self.data('site')
        with patch.object(repository,'insert',side_effect=sqlite3.IntegrityError('test failure')):
            result=self.client.post('/proposer',data=payload)
        self.assertEqual(result.status_code,422)
        self.assertEqual(len(repository.list_all()),0)
        self.assertEqual(sqlite3.connect(self.database_path).execute('SELECT COUNT(*) FROM sites').fetchone()[0],0)

    def test_optional_location_and_proposed_evidence_stay_private_and_unverified(self):
        payload=self.data('site',location='city:1',supplied_evidence_url='https://example.org/preuve?source=utile',email='proposant@example.org',reunion_attachment='Justification reçue')
        result=self.client.post('/proposer',data=payload)
        self.assertEqual(result.status_code,303)
        proposal=repository.list_all()[0]
        self.assertEqual(proposal['city_id'],1)
        self.assertEqual(proposal['supplied_evidence_url'],'https://example.org/preuve?source=utile')
        self.assertEqual(proposal['private_source_reference'],'')
        self.assertEqual(proposal['private_source_url'],'')
        site=repository.get_site_record(proposal['site_id'])
        self.assertEqual(site['ville_id'],1)
        receipt=self.client.get(result.location).get_data(as_text=True)
        self.assertNotIn('proposant@example.org',receipt)
        self.assertNotIn('source=utile',receipt)
        self.assertNotIn('Justification reçue',receipt)
        self.admin()
        detail=self.client.get('/admin/refonte/propositions/'+str(proposal['id']))
        self.assertIn('city:1',detail.get_data(as_text=True))
        self.assertIn('source=utile',detail.get_data(as_text=True))
        values=dict(proposal,action='prepare',location='online')
        self.assertEqual(self.client.post('/admin/refonte/propositions/'+str(proposal['id']),data=values).status_code,303)
        stored=repository.get_site_record(proposal['site_id'])
        self.assertIsNone(stored['ville_id'])
        self.assertEqual(stored['location_scope'],'online')

    def test_safe_return_and_existing_manual_publication_state(self):
        self.client.post('/proposer',data=self.data('site'))
        proposal=repository.list_all()[0]
        self.admin()
        path='/admin/refonte/propositions/'+str(proposal['id'])
        values=dict(proposal,action='prepare',retour='https://outside.example/')
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        connection=sqlite3.connect(self.database_path)
        connection.execute("UPDATE sites SET status='valide' WHERE id=?",(proposal['site_id'],))
        connection.commit()
        connection.close()
        queue=self.client.get('/admin/refonte?statut=published').get_data(as_text=True)
        self.assertIn('Profil exemple',queue)
        values.update(action='archive',confirm='yes',retour='/\\outside.example/')
        result=self.client.post(path,data=values)
        self.assertEqual(result.location,'/admin/refonte')

    def test_evidence_fragments_are_preserved_and_never_promoted_to_verified_source(self):
        raw=self.data('personality',supplied_evidence_url='https://example.org/article?section=2#preuve')
        self.assertEqual(self.client.post('/proposer',data=raw).status_code,303)
        stored=repository.list_all()[0]
        self.assertEqual(stored['supplied_evidence_url'],'https://example.org/article?section=2#preuve')
        self.assertEqual(stored['private_source_url'],'')

    def test_admin_duplicate_cannot_partially_change_proposal_or_linked_talent(self):
        self.client.post('/proposer',data=self.data('personality',name='Profil A',url='https://example.org/a'))
        proposal_a=repository.list_all()[0]
        self.client.post('/proposer',data=self.data('personality',name='Profil B',url='https://example.org/b'))
        proposal_b=repository.list_all()[0]
        self.admin()
        path='/admin/refonte/propositions/'+str(proposal_a['id'])
        values=dict(proposal_a,action='prepare',category_id='1',description='Présentation du profil A.')
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        prepared=repository.get(proposal_a['id'])
        talent_before=dict(talent_service.get_talent(prepared['talent_id']))
        # Ordinary editing does not flag the proposal's own official URL as a duplicate.
        values.update(action='save')
        self.assertEqual(self.client.post(path,data=values).status_code,303)
        values.update(name='Nom ne devant pas être écrit',url=proposal_b['url'])
        self.assertEqual(self.client.post(path,data=values).status_code,422)
        stored=repository.get(proposal_a['id'])
        self.assertEqual(stored['name'],'Profil A')
        self.assertEqual(stored['url'],'https://example.org/a')
        self.assertEqual(dict(talent_service.get_talent(prepared['talent_id'])),talent_before)
        # An existing linked talent is also protected when no proposal owns its URL.
        other_values=dict(proposal_b,category_id=1,description='Présentation du profil B.')
        service.prepare(service.save_editorial(proposal_b,other_values))
        linked_b=repository.get(proposal_b['id'])
        connection=sqlite3.connect(self.database_path)
        connection.execute("UPDATE talents SET website_url='https://example.org/autre-lien' WHERE id=?",(linked_b['talent_id'],))
        connection.commit()
        connection.close()
        values.update(url='https://example.org/autre-lien')
        self.assertEqual(self.client.post(path,data=values).status_code,422)
        self.assertEqual(repository.get(proposal_a['id'])['url'],'https://example.org/a')
        self.assertEqual(dict(talent_service.get_talent(prepared['talent_id'])),talent_before)

    def test_prepare_reloads_a_stale_proposal_before_creating_a_second_draft(self):
        self.client.post('/proposer',data=self.data('personality'))
        proposal=repository.list_all()[0]
        stale=service.save_editorial(proposal,dict(proposal,category_id=1,description='Présentation du profil.'))
        service.prepare(stale)
        first_id=repository.get(proposal['id'])['talent_id']
        service.prepare(stale)
        self.assertEqual(repository.get(proposal['id'])['talent_id'],first_id)
        self.assertEqual(sqlite3.connect(self.database_path).execute('SELECT COUNT(*) FROM talents').fetchone()[0],1)

    def test_type_switch_preserves_fields_without_sending(self):
        payload=self.data('site',name='Nom conservé',email='private@example.org')
        payload.update(kind='personality',change_type='yes')
        result=self.client.post('/proposer',data=payload)
        self.assertEqual(result.status_code,200)
        self.assertIn('Nom conservé',result.get_data(as_text=True))
        self.assertEqual(len(repository.list_all()),0)


if __name__ == '__main__':
    unittest.main()
