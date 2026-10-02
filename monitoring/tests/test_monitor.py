import importlib.util
import io
import json
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "logbot"))
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

spec = importlib.util.spec_from_file_location('monitor', Path(__file__).parents[1] / 'logbot/monitor.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MonitoringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / 'state.db')
        self.store = m.Store(self.path)
        self.bot = m.Telegram('fake-token', 'fake-chat')
        self.monitor = m.Monitor(self.store, self.bot, 'web', 'https://example.com/')

    def tearDown(self):
        self.store.db.close()
        self.temp.cleanup()

    def messages(self):
        return self.store.db.execute('SELECT text FROM outbox ORDER BY id').fetchall()

    def test_error_between_normal_lines_is_not_lost_and_boundary_is_deduplicated(self):
        logs = '\n'.join(f'2026-10-02T00:00:0{i}.000000001Z {s}' for i, s in enumerate(['INFO normal', 'ERROR failure', 'INFO next']))
        self.monitor.ingest(logs, m.utc(100), 100)
        self.monitor.ingest(logs, m.utc(105), 105)
        self.assertEqual(len(self.messages()), 1)
        self.assertIn('ERROR failure', self.messages()[0][0])

    def test_repeated_errors_are_summarized_even_after_restart(self):
        self.monitor.emit('ERROR failure', 100)
        self.monitor.emit('ERROR failure', 110)
        self.store.db.commit()
        other = m.Store(self.path)
        other.summaries(401)
        other.db.commit()
        self.assertEqual(len(self.messages()), 2)
        self.assertIn('1 répétition', self.messages()[1][0])
        other.db.close()

    def test_traceback_across_polls_preserves_final_exception(self):
        self.monitor.ingest('2026-10-02T00:00:00.000000001Z Traceback (most recent call last):\n2026-10-02T00:00:01.000000001Z   File "app.py", line 1', m.utc(100), 100)
        self.assertEqual(self.messages(), [])
        self.monitor.ingest('2026-10-02T00:00:02.000000001Z ValueError: bad value', m.utc(102), 102)
        self.monitor.ingest('', m.utc(108), 108)
        self.assertEqual(len(self.messages()), 1)
        self.assertIn('ValueError: bad value', self.messages()[0][0])

    def test_plain_number_500_is_not_an_http_error(self):
        self.assertFalse(m.ERROR.search('INFO processed 500 records'))
        self.assertTrue(m.ERROR.search('127.0.0.1 "GET / HTTP/1.1" 503 12'))

    def test_failed_send_is_persistent_and_success_removes_it(self):
        self.store.enqueue('test', 100)
        with patch.object(self.bot, 'send', return_value=(False, 30, 'Telegram code 429')):
            self.monitor.deliver(100)
        self.assertEqual(self.store.db.execute('SELECT due,attempts FROM outbox').fetchone(), (130, 1))
        with patch.object(self.bot, 'send', return_value=(True, 0, '')):
            self.monitor.deliver(131)
        self.assertEqual(self.messages(), [])

    def test_https_requires_three_failures_and_sends_one_recovery(self):
        for now in [100, 160]:
            self.monitor.transition('Site HTTPS', False, 'HTTP 503', now)
        self.assertEqual(self.messages(), [])
        self.monitor.transition('Site HTTPS', False, 'HTTP 503', 220)
        self.monitor.transition('Site HTTPS', False, 'HTTP 503', 280)
        self.monitor.transition('Site HTTPS', True, 'HTTP 200', 340)
        self.monitor.transition('Site HTTPS', True, 'HTTP 200', 400)
        self.assertEqual(len(self.messages()), 2)
        self.assertIn('rétabli', self.messages()[1][0])

    def test_docker_failure_keeps_cursor_and_reconnects(self):
        cursor = self.store.get('cursor')
        with patch.object(self.monitor.reader, 'logs', side_effect=OSError('missing')):
            self.assertFalse(self.monitor.poll_logs(100))
        self.assertEqual(self.store.get('cursor'), cursor)
        with patch.object(self.monitor.reader, 'logs', return_value='2026-10-02T00:00:00.000000001Z ERROR after recreation'):
            self.assertTrue(self.monitor.poll_logs(110))
        self.assertIn('after recreation', self.messages()[0][0])

    def test_telegram_rejects_ok_false_and_honors_retry_after(self):
        exc = HTTPError('redacted', 429, 'Too many requests', {}, io.BytesIO(json.dumps({'ok': False, 'error_code': 429, 'parameters': {'retry_after': 42}}).encode()))
        with patch.object(m.request, 'urlopen', side_effect=exc):
            self.assertEqual(self.bot.send('test'), (False, 42, 'Telegram code 429'))

    def test_network_exception_never_exposes_token(self):
        with patch.object(m.request, 'urlopen', side_effect=URLError('https://fake-token')):
            result = self.bot.send('test')
        self.assertFalse(result[0])
        self.assertNotIn('fake-token', result[2])

    def test_redacts_credentials_in_alerts(self):
        self.monitor.emit('ERROR fake-token password=hello', 100)
        self.assertNotIn('fake-token', self.messages()[0][0])
        self.assertNotIn('hello', self.messages()[0][0])


if __name__ == '__main__':
    unittest.main()
