"""Persistent Docker log alerts and HTTPS availability monitoring, stdlib only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from urllib import error, parse, request

ERROR = re.compile(r'\b(?:ERROR|CRITICAL|FATAL|EXCEPTION)\b|Traceback \(most recent call last\):|"\s+5\d\d\s', re.I)
STAMP = re.compile(r'^\d{4}-\d\d-\d\dT\S+Z ')


def utc(epoch=None):
    return datetime.fromtimestamp(time.time() if epoch is None else epoch, timezone.utc).isoformat().replace('+00:00', 'Z')


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
          CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY, created REAL);
          CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, text TEXT, due REAL, attempts INTEGER DEFAULT 0);
          CREATE TABLE IF NOT EXISTS groups (key TEXT PRIMARY KEY, text TEXT, due REAL, repeats INTEGER);
        ''')
        self.db.commit()

    def get(self, key, default=None):
        row = self.db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
        return row[0] if row else default

    def set(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key, str(value)))

    def enqueue(self, text, now):
        self.db.execute('INSERT INTO outbox(text,due) VALUES (?,?)', (text[:3500], now))

    def alert(self, key, text, now, window):
        row = self.db.execute('SELECT due FROM groups WHERE key=?', (key,)).fetchone()
        if row and row[0] > now:
            self.db.execute('UPDATE groups SET repeats=repeats+1 WHERE key=?', (key,))
        else:
            self.summaries(now)
            self.enqueue(text, now)
            self.db.execute('INSERT OR REPLACE INTO groups VALUES (?,?,?,0)', (key, text, now + window))

    def summaries(self, now):
        for key, text, repeats in self.db.execute('SELECT key,text,repeats FROM groups WHERE due<=?', (now,)).fetchall():
            if repeats:
                self.enqueue(f'🔁 {repeats} répétition(s) supplémentaire(s)\n{text}', now)
            self.db.execute('DELETE FROM groups WHERE key=?', (key,))


class Telegram:
    def __init__(self, token, chat):
        self.token, self.chat = token, chat

    def send(self, text):
        """Return (accepted, retry delay, safe error), never include request URLs."""
        payload = parse.urlencode({'chat_id': self.chat, 'text': text[:3500], 'disable_web_page_preview': 'true'}).encode()
        req = request.Request(f'https://api.telegram.org/bot{self.token}/sendMessage', data=payload)
        try:
            with request.urlopen(req, timeout=10) as response:
                data = json.load(response)
        except error.HTTPError as exc:
            try:
                data = json.loads(exc.read())
            except (ValueError, OSError):
                return False, 0, f'HTTP {exc.code}'
        except (error.URLError, TimeoutError, OSError, ValueError):
            return False, 0, 'Réseau indisponible ou réponse invalide'
        if not isinstance(data, dict):
            return False, 0, 'Réponse invalide'
        if data.get('ok') is True:
            return True, 0, ''
        return False, int(data.get('parameters', {}).get('retry_after', 0)), f"Telegram code {data.get('error_code', 'inconnu')}"


class Monitor:
    def __init__(self, store, telegram, container, url, window=300, threshold=3):
        self.store, self.telegram = store, telegram
        self.container, self.url = container, url
        self.window, self.threshold = window, threshold
        self.running = True
        if self.store.get('cursor') is None:
            self.store.set('cursor', utc())
            self.store.db.commit()

    def message(self, title, body, now):
        return f'{title} — PROD\nService : {self.container}\nHeure : {utc(now)} (UTC)\n{self.url}\n\n{self.redact(body)}'[:3500]

    def redact(self, text):
        for secret in (self.telegram.token, self.telegram.chat):
            if secret:
                text = text.replace(secret, '<masqué>')
        return re.sub(r'(?i)((?:bot_token|password|authorization|secret|api_key)\s*[:=]\s*)\S+', r'\1<masqué>', text)

    def emit(self, body, now):
        key = hashlib.sha256(body.encode()).hexdigest()
        self.store.alert(key, self.message('🚨 Erreur Réunion Wiki', body, now), now, self.window)

    def ingest(self, output, cutoff, now):
        """Persist each alert and its cursor together, including partial tracebacks."""
        pending = json.loads(self.store.get('pending', '[]'))
        pending_at = float(self.store.get('pending_at', '0'))
        for line in sorted(output.splitlines(), key=lambda s: s.split(' ', 1)[0]):
            if not STAMP.match(line):
                continue
            digest = hashlib.sha256(line.encode()).hexdigest()
            if not self.store.db.execute('INSERT OR IGNORE INTO seen VALUES (?,?)', (digest, now)).rowcount:
                continue
            text = line.split(' ', 1)[1]
            if pending:
                # Indented frames and final exception lines belong to the active traceback.
                continuation = text.startswith((' ', '\t')) or re.match(r'^[\w.]+(?:Error|Exception):', text) or text.startswith(('During handling', 'The above exception'))
                if continuation:
                    if len(pending) < 30:
                        pending.append(text)
                    pending_at = now
                    continue
                self.emit('\n'.join(pending), now)
                pending = []
            if 'Traceback (most recent call last):' in text:
                pending = [text]
                pending_at = now
            elif ERROR.search(text):
                self.emit(text, now)
        if pending and now - pending_at >= 5:
            self.emit('\n'.join(pending), now)
            pending = []
        self.store.set('pending', json.dumps(pending))
        self.store.set('pending_at', pending_at)
        self.store.set('cursor', cutoff)
        self.store.db.execute('DELETE FROM seen WHERE created<?', (now - 86400,))

    def transition(self, name, healthy, detail, now):
        failures = 0 if healthy else int(self.store.get(name + '_failures', '0')) + 1
        self.store.set(name + '_failures', failures)
        down = self.store.get(name + '_down', '0') == '1'
        if failures >= self.threshold and not down:
            self.store.enqueue(self.message('🚨 ' + name + ' indisponible', detail, now), now)
            self.store.set(name + '_down', '1')
        elif healthy and down:
            self.store.enqueue(self.message('✅ ' + name + ' rétabli', detail, now), now)
            self.store.set(name + '_down', '0')

    def poll_logs(self, now):
        cutoff = utc(now)
        try:
            result = subprocess.run(['docker', 'logs', '--timestamps', '--since', self.store.get('cursor'), '--until', cutoff, self.container], capture_output=True, text=True, timeout=20)
            healthy = result.returncode == 0
            if healthy:
                self.ingest(result.stdout + '\n' + result.stderr, cutoff, now)
        except (OSError, subprocess.TimeoutExpired):
            healthy = False
        self.transition('Lecture des logs Docker', healthy, 'Accès aux logs du conteneur surveillé.', now)
        self.store.db.commit()
        return healthy

    def probe(self, now):
        try:
            req = request.Request(self.url, headers={'User-Agent': 'ReunionWiki-monitor/1.0'})
            with request.urlopen(req, timeout=10) as response:
                status = response.status
            healthy, detail = status == 200, f'HTTP {status}'
        except error.HTTPError as exc:
            healthy, detail = False, f'HTTP {exc.code}'
        except (error.URLError, TimeoutError, OSError):
            healthy, detail = False, 'Échec réseau, TLS ou délai dépassé'
        self.transition('Site HTTPS', healthy, detail, now)
        self.store.set('https_last_check', now)
        self.store.set('https_ok', int(healthy))
        self.store.db.commit()

    def deliver(self, now):
        self.store.summaries(now)
        row = self.store.db.execute('SELECT id,text,attempts FROM outbox WHERE due<=? ORDER BY id LIMIT 1', (now,)).fetchone()
        self.store.db.commit()
        if row:
            ident, text, attempts = row
            accepted, retry, reason = self.telegram.send(text)
            if accepted:
                self.store.db.execute('DELETE FROM outbox WHERE id=?', (ident,))
                self.store.set('telegram_last_success', time.time())
                print('Telegram : message accepté', flush=True)
            else:
                delay = max(retry, min(3600, 5 * 2 ** min(attempts, 10)))
                self.store.db.execute('UPDATE outbox SET due=?,attempts=attempts+1 WHERE id=?', (now + delay, ident))
                print(f'Telegram : {reason}; nouvelle tentative dans {delay}s', flush=True)
            self.store.db.commit()

    def run(self):
        next_probe = 0
        print(f'Monitoring démarré : {self.container}', flush=True)
        while self.running:
            now = time.time()
            self.poll_logs(now)
            if now >= next_probe:
                self.probe(time.time())
                next_probe = time.time() + 60
            self.deliver(time.time())
            self.store.set('heartbeat', time.time())
            self.store.db.commit()
            for _ in range(5):
                if not self.running:
                    break
                time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--healthcheck', action='store_true')
    parser.add_argument('--test-message', action='store_true')
    args = parser.parse_args()
    path = os.getenv('STATE_PATH', '/state/monitor.db')
    if args.healthcheck:
        try:
            with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as db:
                row = db.execute("SELECT value FROM meta WHERE key='heartbeat'").fetchone()
            raise SystemExit(0 if row and time.time() - float(row[0]) < 120 else 1)
        except sqlite3.Error:
            raise SystemExit(1)
    telegram = Telegram(os.environ['BOT_TOKEN'], os.environ['CHAT_ID'])
    monitor = Monitor(Store(path), telegram, os.getenv('TARGET_CONTAINER', 'reunionwiki_prod_web_1'), os.getenv('SITE_URL', 'https://reunionwiki.re/'))
    if args.test_message:
        ok, _, reason = telegram.send(monitor.message('🧪 Test du monitoring', 'Connexion Telegram validée. Aucun incident sur le site.', time.time()))
        print('Message test accepté' if ok else reason)
        raise SystemExit(0 if ok else 1)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: setattr(monitor, 'running', False))
    monitor.run()


if __name__ == '__main__':
    main()
