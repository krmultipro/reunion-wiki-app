"""Operational failure scenarios, with no production or Telegram access."""
from collections import namedtuple
import sqlite3
import io
import json
import unittest
from unittest.mock import patch, MagicMock
import test_monitor as baseline
m = baseline.m


class ImprovementsTests(unittest.TestCase):
    setUp = baseline.MonitoringTests.setUp
    tearDown = baseline.MonitoringTests.tearDown
    messages = baseline.MonitoringTests.messages

    def test_different_errors_are_bounded_and_count_survives_restart(self):
        for i in range(5000):
            self.monitor.emit(f'ERROR distinct failure {i}', 1000)
        self.store.db.commit()
        self.assertEqual(len(self.messages()), 50)
        self.assertEqual(self.store.get('overflow_count'), '4950')
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM groups').fetchone()[0], 50)
        other = m.Store(self.path)
        other.summaries(1301)
        other.db.commit()
        other.db.close()
        self.assertEqual(len(self.messages()), 51)
        self.assertIn('4950', self.messages()[-1][0])

    def test_outbox_cap_preserves_aggregation_until_space_returns(self):
        for i in range(1200):
            self.store.enqueue(f'notification {i}', 100)
        self.assertEqual(len(self.messages()), 1000)
        self.assertEqual(self.store.get('overflow_count'), '200')
        self.store.summaries(401)
        self.assertEqual(self.store.get('overflow_count'), '200')
        self.store.db.execute('DELETE FROM outbox WHERE id<=200')
        self.store.summaries(402)
        self.assertEqual(len(self.messages()), 801)
        self.assertIn('200 notification', self.messages()[-1][0])

    def test_disk_and_backlog_alert_once_then_recover_with_hysteresis(self):
        usage = namedtuple('Usage','total used free')
        gib = 1024 ** 3
        with patch.object(m.shutil,'disk_usage',return_value=usage(100*gib,95*gib,5*gib)):
            for now in (100,160,220,280): self.monitor.maintenance(now)
        self.assertEqual(len(self.messages()),1)
        with patch.object(m.shutil,'disk_usage',return_value=usage(100*gib,89*gib,11*gib)):
            self.monitor.maintenance(340)
        self.assertEqual(len(self.messages()),1)
        with patch.object(m.shutil,'disk_usage',return_value=usage(100*gib,80*gib,20*gib)):
            self.monitor.maintenance(400)
        self.assertIn('rétabli',self.messages()[-1][0])
        self.store.db.execute('DELETE FROM outbox')
        self.store.enqueue('old',100)
        with patch.object(m.shutil,'disk_usage',return_value=usage(100*gib,80*gib,20*gib)):
            for now in (1100,1160,1220,1280): self.monitor.maintenance(now)
            self.assertEqual(len(self.messages()),2)
            self.store.db.execute('DELETE FROM outbox')
            self.monitor.maintenance(1340)
        self.assertEqual(len(self.messages()),1)
        self.assertIn('File Telegram rétabli',self.messages()[0][0])

    def test_certificate_thresholds_no_repeat_and_renewal(self):
        context = MagicMock()
        socket_context = context.wrap_socket.return_value.__enter__.return_value
        with patch.object(m.ssl,'create_default_context',return_value=context), patch.object(m.socket,'create_connection'), patch.object(m.ssl,'cert_time_to_seconds') as expiry:
            socket_context.getpeercert.return_value = {'notAfter':'fixed test certificate'}
            for days in (29,28,13,6,2,90):
                expiry.return_value = 1000+days*86400
                self.monitor.probe_certificate(1000)
        self.assertEqual(len(self.messages()),5)
        self.assertIn('renouvelé',self.messages()[-1][0])
        self.assertEqual(self.store.get('tls_level'),'0')
        context.wrap_socket.assert_called_with(unittest.mock.ANY,server_hostname='example.com')

    def test_extended_gateway_outage_keeps_cursor_and_replays_once(self):
        cursor = self.store.get('cursor')
        with patch.object(self.monitor.reader,'logs',side_effect=OSError('offline')):
            for now in range(100,3700,60): self.monitor.poll_logs(now)
        self.assertEqual(len(self.messages()),1)
        self.assertEqual(self.store.get('cursor'),cursor)
        self.assertEqual(self.store.get('logs_ok'),'0')
        logs = '2026-10-02T00:00:00.000000001Z ERROR recovered'
        with patch.object(self.monitor.reader,'logs',return_value=logs):
            self.monitor.poll_logs(3800)
            self.monitor.poll_logs(3860)
        self.assertEqual(len(self.messages()),3)
        self.assertEqual(self.store.get('logs_last_success'),'3860')

    def test_sqlite_capacity_exhaustion_does_not_commit_cursor(self):
        original = self.store.get('cursor')
        pages = self.store.db.execute('PRAGMA page_count').fetchone()[0]
        self.store.db.execute(f'PRAGMA max_page_count={pages}')
        with self.assertRaises(sqlite3.OperationalError):
            # A real SQLite capacity failure, not a mocked exception.
            self.monitor.ingest('\n'.join(f'2026-10-02T00:00:00.{i:09d}Z ERROR capacity {i}' for i in range(500)),m.utc(100),100)
        self.store.db.rollback()
        self.assertEqual(self.store.get('cursor'),original)
        self.assertEqual(self.messages(),[])
        self.store.db.execute('PRAGMA max_page_count=10000')
        self.monitor.ingest('2026-10-02T00:00:00.000000001Z ERROR recovered',m.utc(105),105)
        self.store.db.commit()
        self.assertEqual(len(self.messages()),1)

    def test_lost_ack_retries_and_can_duplicate_accepted_message(self):
        accepted=[]
        def send(text):
            accepted.append(text)
            return (len(accepted)>1,0,'Réponse perdue')
        self.store.enqueue('event',100)
        with patch.object(self.bot,'send',side_effect=send):
            self.monitor.deliver(100)
            self.assertEqual(len(self.messages()),1)
            self.monitor.deliver(106)
        self.assertEqual(accepted,['event','event'])
        self.assertEqual(self.messages(),[])

    def test_new_commands_private_and_sanitized(self):
        self.bot.chat=self.monitor.owner='123'
        self.monitor.emit('ERROR password=secret-value',100)
        self.store.set('logs_last_success',100)
        with patch.dict(m.os.environ,MONITORING_RELEASE='a'*40):
            for i,cmd in enumerate(('version','lastalert','lastcheck')):
                msg={'chat':{'id':123,'type':'private'},'from':{'id':123,'is_bot':False},'text':'/'+cmd}
                self.monitor.handle_command(msg,110+i*11)
        replies='\n'.join(text[0] for text in self.messages()[1:])
        self.assertIn('aaaaaaaaaaaa',replies)
        self.assertIn('Erreur applicative',replies)
        self.assertIn('Logs, succès',replies)
        self.assertNotIn('secret-value',replies)
        self.assertNotIn('password',replies)

    def test_snapshot_is_read_only_and_does_not_initialize_telegram(self):
        self.store.set('https_ok',1)
        self.store.set('password','private-value')
        self.store.enqueue('sensitive log',100)
        self.store.db.commit()
        output=io.StringIO()
        with patch.object(__import__('sys'),'argv',['monitor.py','--snapshot']), patch.dict(m.os.environ,STATE_PATH=self.path), patch.object(m,'Telegram') as telegram, patch('sys.stdout',output):
            m.main()
        telegram.assert_not_called()
        data=json.loads(output.getvalue())
        self.assertEqual(data['queue_count'],1)
        self.assertEqual(data['https_ok'],'1')
        self.assertNotIn('private-value',output.getvalue())
        self.assertNotIn('sensitive log',output.getvalue())
        self.assertEqual(len(self.messages()),1)

    def test_upgrade_old_database_and_rollback_remain_compatible(self):
        self.store.db.execute('DROP TABLE outbox')
        self.store.db.execute('CREATE TABLE outbox (id INTEGER PRIMARY KEY,text TEXT,due REAL,attempts INTEGER DEFAULT 0)')
        self.store.db.execute("INSERT INTO outbox(text,due) VALUES ('before upgrade',100)")
        self.store.db.commit()
        other=m.Store(self.path)
        self.assertEqual(other.db.execute('SELECT created FROM outbox').fetchone()[0],100)
        # The previous release can still insert with its explicit original columns.
        other.db.execute("INSERT INTO outbox(text,due) VALUES ('during rollback',200)")
        other.db.commit()
        other.db.close()
        upgraded=m.Store(self.path)
        self.assertEqual(upgraded.db.execute('SELECT created FROM outbox ORDER BY id').fetchall(),[(100.0,),(200.0,)])
        upgraded.db.close()
