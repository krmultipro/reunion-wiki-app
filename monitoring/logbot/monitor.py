"""Persistent Docker log alerts and HTTPS availability monitoring, stdlib only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import socket
import ssl
import sqlite3
import time
from datetime import datetime, timezone
from docker_reader import DockerReader
from urllib import error, parse, request

ERROR = re.compile(r'\b(?:ERROR|CRITICAL|FATAL|EXCEPTION)\b|Traceback \(most recent call last\):|"\s+5\d\d\s', re.I)
STAMP = re.compile(r'^\d{4}-\d\d-\d\dT\S+Z ')


def utc(epoch=None):
    return datetime.fromtimestamp(time.time() if epoch is None else epoch, timezone.utc).isoformat().replace('+00:00', 'Z')


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.db = sqlite3.connect(path)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
          CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY, created REAL);
          CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, text TEXT, due REAL, attempts INTEGER DEFAULT 0);
          CREATE TABLE IF NOT EXISTS groups (key TEXT PRIMARY KEY, text TEXT, due REAL, repeats INTEGER);
        ''')
        columns = {row[1] for row in self.db.execute('PRAGMA table_info(outbox)')}
        if 'created' not in columns:
            self.db.execute('ALTER TABLE outbox ADD COLUMN created REAL')
        self.db.execute('UPDATE outbox SET created=due WHERE created IS NULL')
        self.db.commit()

    def get(self, key, default=None):
        row = self.db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
        return row[0] if row else default

    def set(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', (key, str(value)))

    def enqueue(self, text, now):
        if self.db.execute('SELECT count(*) FROM outbox').fetchone()[0] >= 1000:
            self.overflow(now)
            return
        self.db.execute('INSERT INTO outbox(text,due,created) VALUES (?,?,?)', (text[:3500], now, now))

    def overflow(self, now):
        self.set('overflow_count', int(self.get('overflow_count', '0')) + 1)
        if self.get('overflow_since') is None:
            self.set('overflow_since', now)

    def alert(self, key, text, now, window):
        row = self.db.execute('SELECT due FROM groups WHERE key=?', (key,)).fetchone()
        if row and row[0] > now:
            self.db.execute('UPDATE groups SET repeats=repeats+1 WHERE key=?', (key,))
        else:
            self.summaries(now)
            start = float(self.get('burst_start', '0'))
            count = int(self.get('burst_count', '0'))
            if now - start >= window:
                start, count = now, 0
            if count >= 50:
                self.overflow(now)
                return
            self.set('burst_start', start)
            self.set('burst_count', count + 1)
            self.enqueue(text, now)
            self.db.execute('INSERT OR REPLACE INTO groups VALUES (?,?,?,0)', (key, text, now + window))

    def summaries(self, now):
        overflow = int(self.get('overflow_count', '0'))
        since = float(self.get('overflow_since', str(now)))
        if (overflow and now - since >= 300
                and self.db.execute('SELECT count(*) FROM outbox').fetchone()[0] < 900):
            self.enqueue(f'⚠️ Anti-flood : {overflow} notification(s) regroupée(s) depuis {utc(since)}. Détails non conservés dans la file ; consulter les logs du service.', now)
            self.set('overflow_count', 0)
            self.db.execute("DELETE FROM meta WHERE key='overflow_since'")
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
        try:
            retry = max(0, int(data.get('parameters', {}).get('retry_after', 0)))
        except (AttributeError, TypeError, ValueError):
            return False, 0, 'Réponse invalide'
        return False, retry, f"Telegram code {data.get('error_code', 'inconnu')}"


    def api(self, method, payload):
        # Method names come only from this source, never from incoming messages.
        if method not in {'getUpdates', 'setMyCommands', 'getMe', 'getWebhookInfo'}:
            raise ValueError('Unsupported Telegram method')
        req = request.Request(f'https://api.telegram.org/bot{self.token}/{method}', data=parse.urlencode(payload).encode())
        try:
            with request.urlopen(req, timeout=10) as response:
                data = json.load(response)
            if isinstance(data, dict) and data.get('ok') is True:
                return data.get('result')
        except (error.URLError, TimeoutError, OSError, ValueError):
            pass
        raise OSError('Telegram command API unavailable')

    def updates(self, offset):
        return self.api('getUpdates', {'offset': offset, 'timeout': 0, 'limit': 20, 'allowed_updates': json.dumps(['message'])})

    def register_commands(self):
        commands = [
            {'command': 'status', 'description': 'État du site et du monitoring'},
            {'command': 'queue', 'description': 'Nombre d’alertes en attente'},
            {'command': 'test', 'description': 'Vérifier la réponse du bot'},
            {'command': 'lastcheck', 'description': 'Dates des derniers contrôles'},
            {'command': 'version', 'description': 'Version du monitoring déployée'},
            {'command': 'lastalert', 'description': 'Date et catégorie de la dernière alerte'},
            {'command': 'help', 'description': 'Afficher les commandes'},
        ]
        return self.api('setMyCommands', {'commands': json.dumps(commands), 'scope': json.dumps({'type': 'chat', 'chat_id': int(self.chat)})})


class Monitor:
    def __init__(self, store, telegram, container, url, window=300, threshold=3, reader=None, owner=None):
        self.store, self.telegram = store, telegram
        self.container, self.url = container, url
        self.window, self.threshold = window, threshold
        self.reader = reader or DockerReader()
        self.owner = owner
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
        self.record_alert('Erreur applicative', now)
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

    def record_alert(self, category, now):
        self.store.set('last_alert_category', category)
        self.store.set('last_alert_at', now)

    def transition(self, name, healthy, detail, now):
        failures = 0 if healthy else int(self.store.get(name + '_failures', '0')) + 1
        self.store.set(name + '_failures', failures)
        down = self.store.get(name + '_down', '0') == '1'
        if failures >= self.threshold and not down:
            self.record_alert(name, now)
            self.store.enqueue(self.message('🚨 ' + name + ' indisponible', detail, now), now)
            self.store.set(name + '_down', '1')
        elif healthy and down:
            self.store.enqueue(self.message('✅ ' + name + ' rétabli', detail, now), now)
            self.store.set(name + '_down', '0')

    def poll_logs(self, now):
        since = self.store.get('cursor')
        cutoff = utc(min(now, datetime.fromisoformat(since.replace('Z', '+00:00')).timestamp() + 3600))
        try:
            self.ingest(self.reader.logs(since, cutoff), cutoff, now)
            healthy = True
            self.store.set('logs_last_success', now)
        except (OSError, KeyError):
            healthy = False
        self.store.set('logs_last_check', now)
        self.store.set('logs_ok', int(healthy))
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

    def maintenance(self, now):
        # This bind mount and the production data directory share the VPS filesystem.
        disk = shutil.disk_usage(Path(self.store.path).parent)
        free_percent = 100 * disk.free / disk.total
        low = free_percent < 10 or disk.free < 1024 ** 3
        was_low = self.store.get('Disque VPS_down') == '1'
        healthy = not low and (not was_low or (free_percent >= 15 and disk.free >= 2 * 1024 ** 3))
        self.transition('Disque VPS', healthy, f'Espace libre : {free_percent:.1f}% ({disk.free // (1024 ** 2)} Mio).', now)
        count, oldest = self.store.db.execute('SELECT count(*),min(created) FROM outbox').fetchone()
        stuck = count >= 100 or (oldest is not None and now - oldest >= 900)
        self.transition('File Telegram', not stuck, f'{count} message(s) en attente ; délai maximal supérieur à 15 minutes ou file volumineuse.', now)
        self.store.set('resources_last_check', now)
        self.store.db.commit()

    def probe_certificate(self, now):
        host = parse.urlsplit(self.url)
        if host.scheme != 'https' or not host.hostname:
            return
        try:
            with socket.create_connection((host.hostname, host.port or 443), timeout=10) as raw:
                with ssl.create_default_context().wrap_socket(raw, server_hostname=host.hostname) as secure:
                    expires = ssl.cert_time_to_seconds(secure.getpeercert()['notAfter'])
            days = (expires - now) / 86400
            level = next((limit for limit in (3, 7, 14, 30) if days <= limit), 0)
            previous = int(self.store.get('tls_level', '0'))
            if level and (not previous or level < previous):
                self.record_alert('Expiration certificat TLS', now)
                self.store.enqueue(self.message('⚠️ Certificat TLS', f'Expiration dans {max(0, int(days))} jour(s), le {utc(expires)}.', now), now)
            elif not level and previous:
                self.store.enqueue(self.message('✅ Certificat TLS renouvelé', f'Expiration le {utc(expires)}.', now), now)
            self.store.set('tls_level', level)
            self.store.set('tls_expires', expires)
            self.store.set('tls_last_success', now)
            self.transition('Contrôle certificat TLS', True, 'Lecture validée.', now)
        except (OSError, ValueError, KeyError):
            self.transition('Contrôle certificat TLS', False, 'Lecture du certificat indisponible.', now)
        self.store.set('tls_last_check', now)
        self.store.db.commit()

    def deliver(self, now):
        self.store.summaries(now)
        if now < float(self.store.get('telegram_not_before', '0')):
            self.store.db.commit()
            return
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
                self.store.set('telegram_not_before', now + delay)
                print(f'Telegram : {reason}; nouvelle tentative dans {delay}s', flush=True)
            self.store.db.commit()

    def handle_command(self, message, now):
        """Only the pinned owner in the pinned private chat may request fixed reads."""
        if not self.owner or not isinstance(message, dict):
            return
        chat, sender = message.get('chat', {}), message.get('from', {})
        if not isinstance(chat, dict) or not isinstance(sender, dict):
            return
        if (chat.get('type') != 'private' or type(chat.get('id')) is not int
                or type(sender.get('id')) is not int or sender.get('is_bot') is not False
                or str(chat['id']) != self.telegram.chat or str(sender['id']) != self.owner
                or message.get('forward_origin') or message.get('sender_chat')):
            return
        text = message.get('text', '')
        if not isinstance(text, str) or len(text) > 80:
            return
        match = re.fullmatch(r'/(help|start|status|queue|test|lastcheck|version|lastalert)(?:@([A-Za-z0-9_]+))?', text.strip())
        if not match:
            return
        if match[2] and match[2].lower() != os.getenv('BOT_USERNAME', '').lower():
            return
        if now < float(self.store.get('command_not_before', '0')):
            return
        self.store.set('command_not_before', now + 10)
        command = match[1]
        if command in ('help', 'start'):
            reply = 'Commandes privées :\n/status — état du site et du monitoring\n/queue — alertes en attente\n/test — vérifier la réponse\n/lastcheck — derniers contrôles\n/version — version déployée\n/lastalert — dernière alerte sans détails sensibles\n/help — cette aide\nAucune commande d’administration du VPS.'
        elif command == 'queue':
            count = self.store.db.execute('SELECT count(*) FROM outbox').fetchone()[0]
            reply = f'Alertes et réponses en attente : {count}.'
        elif command == 'version':
            release = os.getenv('MONITORING_RELEASE', '')
            reply = 'Version monitoring : ' + (release[:12] if re.fullmatch(r'[a-f0-9]{40}', release) else 'inconnue')
        elif command == 'lastalert':
            stamp = self.store.get('last_alert_at')
            reply = (f"Dernière alerte détectée : {self.store.get('last_alert_category')} — {utc(float(stamp))} (UTC). Son envoi peut encore être en attente." if stamp else 'Aucune alerte enregistrée depuis l’activation de cette fonction.')
        elif command == 'lastcheck':
            def checked(key):
                value = self.store.get(key)
                return utc(float(value)) if value else 'jamais'
            reply = f"Derniers contrôles (UTC) :\nHTTPS : {checked('https_last_check')}\nLogs, tentative : {checked('logs_last_check')}\nLogs, succès : {checked('logs_last_success')}\nDisque et file : {checked('resources_last_check')}\nTLS, tentative : {checked('tls_last_check')}\nTLS, succès : {checked('tls_last_success')}"
        elif command == 'test':
            reply = '✅ Commande reçue et réponse du bot validée. Aucun incident provoqué sur le site.'
        else:
            try:
                state = self.reader.status()
                web = 'actif' if state['running'] else 'arrêté'
            except (OSError, KeyError):
                web = 'état indisponible'
            checked = float(self.store.get('https_last_check', '0'))
            https = 'répond correctement' if self.store.get('https_ok') == '1' else 'échec du dernier contrôle'
            if not checked or now - checked > 180:
                https = 'contrôle récent indisponible'
            reply = f'Réunion Wiki : {https}.\nConteneur web : {web}.\nMonitoring : actif.\nHeure : {utc(now)} (UTC).'
        self.store.enqueue(reply, now)
        self.store.set('command_last_success', now)

    def poll_commands(self, now):
        if not self.owner:
            return
        if now < float(self.store.get('commands_retry_at', '0')):
            return
        offset = self.store.get('telegram_offset')
        try:
            updates = self.telegram.updates(int(offset) if offset else -1)
            if not isinstance(updates, list):
                raise OSError('Invalid Telegram updates')
            for update in updates:
                if not isinstance(update, dict) or type(update.get('update_id')) is not int:
                    continue
                if offset is not None:
                    self.handle_command(update.get('message'), now)
                # Offset and queued replies commit together, including denied updates.
                self.store.set('telegram_offset', update['update_id'] + 1)
            if offset is None and not updates:
                self.store.set('telegram_offset', 0)
            self.store.db.commit()
        except OSError:
            self.store.set('commands_retry_at', now + 30)
            self.store.db.commit()
            print('Réception commandes indisponible ; nouvelle tentative dans 30s', flush=True)

    def run(self):
        next_probe = next_certificate = 0
        print(f'Monitoring démarré : {self.container}', flush=True)
        while self.running:
            now = time.time()
            try:
                self.poll_logs(now)
                if now >= next_probe:
                    self.probe(time.time())
                    self.maintenance(time.time())
                    next_probe = time.time() + 60
                if now >= next_certificate:
                    self.probe_certificate(time.time())
                    next_certificate = time.time() + 6 * 3600
                self.poll_commands(time.time())
                self.deliver(time.time())
                self.store.set('heartbeat', time.time())
                self.store.db.commit()
            except (sqlite3.Error, OSError):
                self.store.db.rollback()
                print('Stockage ou contrôle local indisponible ; nouvelle tentative, heartbeat non renouvelé.', flush=True)
            for _ in range(5):
                if not self.running:
                    break
                time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--healthcheck', action='store_true')
    parser.add_argument('--test-message', action='store_true')
    parser.add_argument('--register-commands', action='store_true')
    parser.add_argument('--snapshot', action='store_true')
    args = parser.parse_args()
    path = os.getenv('STATE_PATH', '/state/monitor.db')
    if args.snapshot:
        keys = ('heartbeat', 'cursor', 'https_last_check', 'https_ok', 'logs_last_check', 'logs_last_success', 'logs_ok', 'resources_last_check', 'tls_last_check', 'tls_last_success', 'tls_expires', 'tls_level', 'telegram_last_success', 'overflow_count', 'Disque VPS_down', 'File Telegram_down')
        with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as db:
            data = {key: db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone() for key in keys}
            data = {key: row[0] if row else None for key, row in data.items()}
            data['queue_count'], data['queue_oldest'] = db.execute('SELECT count(*),min(created) FROM outbox').fetchone()
        data['release'] = os.getenv('MONITORING_RELEASE', '')
        print(json.dumps(data))
        return
    if args.healthcheck:
        try:
            with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as db:
                row = db.execute("SELECT value FROM meta WHERE key='heartbeat'").fetchone()
            raise SystemExit(0 if row and time.time() - float(row[0]) < 120 else 1)
        except sqlite3.Error:
            raise SystemExit(1)
    telegram = Telegram(os.environ['BOT_TOKEN'], os.environ['CHAT_ID'])
    monitor = Monitor(Store(path), telegram, os.getenv('TARGET_CONTAINER', 'reunionwiki_prod_web_1'), os.getenv('SITE_URL', 'https://reunionwiki.re/'), owner=os.getenv('ALLOWED_USER_ID'))
    if args.register_commands:
        if not monitor.owner or not monitor.owner.isdigit() or int(telegram.chat) <= 0:
            raise SystemExit('Propriétaire privé requis')
        telegram.register_commands()
        print('Menu des commandes enregistré pour le chat privé')
        raise SystemExit(0)
    if args.test_message:
        ok, _, reason = telegram.send(monitor.message('🧪 Test du monitoring', 'Connexion Telegram validée. Aucun incident sur le site.', time.time()))
        print('Message test accepté' if ok else reason)
        raise SystemExit(0 if ok else 1)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: setattr(monitor, 'running', False))
    monitor.run()


if __name__ == '__main__':
    main()
