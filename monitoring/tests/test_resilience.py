"""Failure and load tests with synthetic logs and a local Telegram API stand-in."""
import contextlib
import io
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import socket
import threading
import time
from unittest.mock import patch
from urllib import request

import unittest
import test_monitor as baseline
m = baseline.m


class ResilienceTests(unittest.TestCase):
    setUp = baseline.MonitoringTests.setUp
    tearDown = baseline.MonitoringTests.tearDown
    messages = baseline.MonitoringTests.messages
    def test_global_telegram_rate_limit(self):
        self.store.enqueue('first', 100)
        self.store.enqueue('second', 100)
        with patch.object(self.bot, 'send', return_value=(False, 42, 'Telegram code 429')) as send:
            self.monitor.deliver(100)
            self.store.db.close()
            self.store = m.Store(self.path)
            self.monitor = m.Monitor(self.store, self.bot, "web", "https://example.com/")
            self.monitor.deliver(101)
            self.assertEqual(send.call_count, 1, 'retry_after must pause every alert, not only the rejected one')

    def test_malformed_retry_after_does_not_crash_monitor(self):
        from urllib.error import HTTPError
        exc = HTTPError('synthetic', 429, 'limited', {}, io.BytesIO(b'{"ok":false,"parameters":{"retry_after":"invalid"}}'))
        with patch.object(m.request, 'urlopen', side_effect=exc):
            accepted, _, _ = self.bot.send('test')
        self.assertFalse(accepted)

    def test_50000_lines_with_5000_repeated_errors(self):
        logs = '\n'.join(f'2026-10-02T00:00:00.{i:09d}Z ' + ('ERROR repeated failure' if i % 10 == 0 else 'INFO processed 500 records') for i in range(50000))
        started = time.monotonic()
        self.monitor.ingest(logs, m.utc(100), 100)
        self.store.db.commit()
        self.assertEqual(len(self.messages()), 1)
        self.assertEqual(self.store.db.execute('SELECT repeats FROM groups').fetchone()[0], 4999)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM seen').fetchone()[0], 50000)
        self.monitor.ingest(logs, m.utc(101), 101)
        self.assertEqual(self.store.db.execute('SELECT repeats FROM groups').fetchone()[0], 4999)
        self.store.summaries(401)
        self.assertEqual(len(self.messages()), 2)
        print(f'Charge : 50000 lignes / 5000 erreurs, 2 notifications, {time.monotonic()-started:.2f}s')

    def test_transaction_rollback_replays_uncommitted_alert(self):
        before = self.store.get('cursor')
        logs = '2026-10-02T00:00:00.000000001Z ERROR before crash'
        self.monitor.ingest(logs, m.utc(100), 100)
        self.store.db.rollback()
        self.assertEqual(self.store.get('cursor'), before)
        self.assertEqual(self.messages(), [])
        self.monitor.ingest(logs, m.utc(100), 100)
        self.store.db.commit()
        self.assertEqual(len(self.messages()), 1)

    def test_24h_network_outage_and_restart_then_drain(self):
        accepted = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                accepted.append(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"ok":true,"result":{"message_id":1}}')
            def log_message(self, *_):
                pass
        # Reserve a closed local port: every attempt fails through a real socket.
        with socket.socket() as reserve:
            reserve.bind(('127.0.0.1', 0))
            port = reserve.getsockname()[1]
        original_open = request.urlopen
        def route(req, timeout):
            return original_open(request.Request(f'http://127.0.0.1:{port}/sendMessage', data=req.data), timeout=0.5)
        for i in range(20):
            self.monitor.emit(f'ERROR isolated {i}', 100)
        self.store.db.commit()
        attempts = 0
        with patch.object(m.request, 'urlopen', side_effect=route), contextlib.redirect_stdout(io.StringIO()):
            virtual_now = 100
            while virtual_now < 86500:
                self.monitor.deliver(virtual_now)
                self.store.db.close()
                self.store = m.Store(self.path)
                self.monitor = m.Monitor(self.store, self.bot, 'web', 'https://example.com/')
                attempts += 1
                virtual_now += 3600
        self.assertEqual(len(self.messages()), 20)
        server = HTTPServer(('127.0.0.1', port), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(m.request, 'urlopen', side_effect=route), contextlib.redirect_stdout(io.StringIO()):
                for i in range(20):
                    self.monitor.deliver(100000 + i * 5)
            self.assertEqual(len(accepted), 20)
            self.assertEqual(len(set(accepted)), 20)
            self.assertEqual(self.messages(), [])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        print(f'Réseau : 24h accélérées, {attempts} réouvertures de SQLite, 20/20 alertes récupérées via HTTP local')
