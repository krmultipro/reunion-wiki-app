"""Authorization and restricted Docker facade integration tests."""
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

import test_monitor as baseline
m = baseline.m
spec = importlib.util.spec_from_file_location('gateway', Path(__file__).parents[1]/'gateway/gateway.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class CommandTests(unittest.TestCase):
    setUp = baseline.MonitoringTests.setUp
    tearDown = baseline.MonitoringTests.tearDown
    messages = baseline.MonitoringTests.messages

    def message(self, text='/help', **overrides):
        result = {'chat': {'id': 123, 'type':'private'}, 'from':{'id':123, 'is_bot':False}, 'text':text}
        result.update(overrides)
        return result

    def enable(self):
        self.bot.chat = '123'
        self.monitor.owner = '123'

    def test_all_commands_authorized_and_no_raw_secrets(self):
        self.enable()
        self.store.set('https_ok',1)
        self.store.set('https_last_check',100)
        with patch.object(self.monitor.reader,'status',return_value={'running':True}):
            for i, command in enumerate(['/help','/status','/queue','/test']):
                self.monitor.handle_command(self.message(command),100+i*11)
        self.assertEqual(len(self.messages()),4)
        self.assertIn('actif',self.messages()[1][0])
        self.assertFalse(any('fake-token' in text[0] for text in self.messages()))

    def test_other_users_chats_groups_forwards_and_bots_are_silent(self):
        self.enable()
        denied = [self.message(**{'from':{'id':456,'is_bot':False}}), self.message(chat={'id':456,'type':'private'}), self.message(chat={'id':123,'type':'group'}), self.message(**{'from':{'id':123,'is_bot':True}}), self.message(forward_origin={'type':'user'}), self.message(sender_chat={'id':123}), None, {'chat':None,'from':None}]
        with patch.object(self.monitor.reader,'status') as status:
            for item in denied:self.monitor.handle_command(item,100)
            status.assert_not_called()
        self.assertEqual(self.messages(),[])

    def test_no_owner_is_fail_closed(self):
        self.monitor.handle_command(self.message(),100)
        self.assertEqual(self.messages(),[])

    def test_shell_arguments_and_unknown_commands_are_ignored(self):
        self.enable()
        with patch.object(self.monitor.reader,'status') as status:
            for text in ['/status; id','/status $(id)','/exec','/restart','/status\n/queue','/status@another_bot']:
                self.monitor.handle_command(self.message(text),100)
            status.assert_not_called()
        self.assertEqual(self.messages(),[])

    def test_command_cooldown_survives_restart(self):
        self.enable()
        self.monitor.handle_command(self.message(),100)
        self.store.db.commit()
        self.store.db.close()
        self.store=m.Store(self.path)
        self.monitor=m.Monitor(self.store,self.bot,'web','https://example.com',owner='123')
        self.monitor.handle_command(self.message(),101)
        self.monitor.handle_command(self.message(),111)
        self.assertEqual(len(self.messages()),2)

    def test_offset_and_response_commit_together_and_unauthorized_consumed(self):
        self.enable()
        self.store.set('telegram_offset',1)
        updates=[{'update_id':1,'message':self.message(**{'from':{'id':456,'is_bot':False}})}, {'update_id':2,'message':self.message()}]
        with patch.object(self.bot,'updates',return_value=updates):self.monitor.poll_commands(100)
        self.assertEqual(self.store.get('telegram_offset'),'3')
        self.assertEqual(len(self.messages()),1)

    def test_first_start_discards_old_commands(self):
        self.enable()
        with patch.object(self.bot,'updates',return_value=[{'update_id':10,'message':self.message()}]):self.monitor.poll_commands(100)
        self.assertEqual(self.store.get('telegram_offset'),'11')
        self.assertEqual(self.messages(),[])

    def test_menu_scope_is_only_private_chat(self):
        self.enable()
        with patch.object(self.bot,'api',return_value=True) as api:self.bot.register_commands()
        method, payload=api.call_args.args
        self.assertEqual(method,'setMyCommands')
        self.assertEqual(json.loads(payload['scope']),{'type':'chat','chat_id':123})


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=str(Path(self.temp.name)/'reader.sock')
        self.server=g.Gateway(self.path,'only-this-container','/fake/docker.sock')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2);self.temp.cleanup()

    def call(self,method,route):
        client=g.UnixHTTP(self.path)
        try:
            client.request(method,route)
            response=client.getresponse()
            return response.status,json.load(response)
        finally:client.close()

    def test_only_expected_status_fields_no_environment(self):
        payload=json.dumps({'State':{'Running':True,'Status':'running'},'Config':{'Env':['SECRET=hidden']}}).encode()
        with patch.object(g,'docker_read',return_value=payload) as read:
            status,data=self.call('GET','/status')
            self.assertEqual(read.call_args.args,('/fake/docker.sock','only-this-container','json'))
        self.assertEqual(status,200)
        self.assertEqual(data,{'running':True,'status':'running','health':'unknown'})

    def test_arbitrary_paths_and_all_mutations_never_reach_docker(self):
        with patch.object(g,'docker_read') as read:
            for method in ['POST','PUT','DELETE','PATCH','OPTIONS']:
                self.assertEqual(self.call(method,'/status')[0],403)
            for path in ['/containers/json','/containers/other/logs','/v1.41/containers/web/exec','/../status','/%73tatus','/status?container=other']:
                self.assertEqual(self.call('GET',path)[0],403)
            read.assert_not_called()

    def test_strict_query_and_log_window(self):
        valid={'since':'2026-10-02T00:00:00Z','until':'2026-10-02T00:01:00Z'}
        with patch.object(g,'docker_read',return_value=b'2026-10-02T00:00:01Z ERROR test\n') as read:
            code,data=self.call('GET','/logs?'+urlencode(valid))
            self.assertEqual(code,200);self.assertIn('ERROR test',data['logs'])
            self.assertEqual(read.call_args.args[1],'only-this-container')
        with patch.object(g,'docker_read') as read:
            for query in [urlencode({**valid,'container':'other'}),urlencode(valid)+'&since=x','since=invalid&until=invalid',urlencode({**valid,'until':'2026-10-03T00:00:00Z'}),urlencode({**valid,'until':'2026-10-01T00:00:00Z'})]:
                self.assertEqual(self.call('GET','/logs?'+query)[0],400)
            read.assert_not_called()

    def test_multiplexed_stdout_stderr_decoding(self):
        def frame(stream,text):
            b=text.encode();return bytes([stream,0,0,0])+struct.pack('>I',len(b))+b
        self.assertEqual(g.decode_logs(frame(1,'normal\n')+frame(2,'error\n')),'normal\nerror\n')
        with self.assertRaises(ValueError):g.decode_logs(frame(1,'normal')[:-1])

    def test_transport_failure_is_generic(self):
        with patch.object(g,'docker_read',side_effect=OSError('SECRET internal')):
            code,data=self.call('GET','/status')
        self.assertEqual(code,503);self.assertNotIn('SECRET',str(data))
