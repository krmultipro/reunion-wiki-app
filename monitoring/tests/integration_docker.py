"""Isolated real-Docker test; never sends Telegram or touches application services."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid
import threading
import os
sys.path.insert(0,str(Path(__file__).parents[1]/"logbot"))

spec = importlib.util.spec_from_file_location('monitor', Path(__file__).parents[1] / 'logbot/monitor.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
gateway_spec = importlib.util.spec_from_file_location('gateway', Path(__file__).parents[1]/'gateway/gateway.py')
gateway_module = importlib.util.module_from_spec(gateway_spec)
gateway_spec.loader.exec_module(gateway_module)
server = None
name = 'monitoring-probe-' + uuid.uuid4().hex[:12]
image = sys.argv[1]


def docker(*args):
    return subprocess.run(['docker', *args], check=True, capture_output=True, text=True, timeout=30).stdout.strip()


try:
    with tempfile.TemporaryDirectory() as directory:
        socket_path = str(Path(directory)/'reader.sock')
        server = gateway_module.Gateway(socket_path,name)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        store = m.Store(str(Path(directory) / 'test.db'))
        bot = m.Telegram('fake-token', 'fake-chat')
        monitor = m.Monitor(store, bot, name, 'https://example.invalid/', reader=m.DockerReader(socket_path))
        store.set('cursor', m.utc(time.time() - 60))
        store.db.commit()
        code = 'print("INFO before"); print("ERROR middle"); print("INFO after"); print("Traceback (most recent call last):"); print("  File test.py"); print("ValueError: isolated test")'
        docker('run', '--name', name, '--network', 'none', image, 'python', '-u', '-c', code)
        assert monitor.poll_logs(time.time())
        # Let the persisted multiline buffer flush without real waiting.
        assert monitor.poll_logs(time.time() + 6)
        texts = [r[0] for r in store.db.execute('SELECT text FROM outbox')]
        assert len(texts) == 2 and any('ERROR middle' in s for s in texts) and any('ValueError' in s for s in texts), texts
        docker('rm', name)
        cursor = store.get('cursor')
        assert not monitor.poll_logs(time.time())
        assert store.get('cursor') == cursor
        # Reset artificial future cutoff before testing real recreation timestamps.
        store.set('cursor', m.utc(time.time()))
        docker('run', '--name', name, '--network', 'none', image, 'python', '-u', '-c', 'print("ERROR recreated")')
        assert monitor.poll_logs(time.time())
        assert any('ERROR recreated' in r[0] for r in store.db.execute('SELECT text FROM outbox'))
        store.db.close()
    print('Docker réel : erreur intermédiaire, traceback et recréation validés; aucun envoi Telegram')
finally:
    if server:
        server.shutdown(); server.server_close(); thread.join(timeout=2)
    subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=30)
