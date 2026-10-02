"""Real Docker rotation, process restarts and isolated execution of rollback template.

Run on the VPS with a candidate image; all credentials are synthetic, networking
is disabled, and every created resource has a random dedicated project name.
"""
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
import threading
import os
sys.path.insert(0,str(Path(__file__).parents[1]/"logbot"))

spec = importlib.util.spec_from_file_location('monitor', Path(__file__).parents[1] / 'logbot/monitor.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
gateway_spec=importlib.util.spec_from_file_location('gateway',Path(__file__).parents[1]/'gateway/gateway.py')
gateway_module=importlib.util.module_from_spec(gateway_spec); gateway_spec.loader.exec_module(gateway_module)
servers=[]
image = sys.argv[1]
previous_image = sys.argv[2] if len(sys.argv) > 2 else image
prefix = 'monitor-stress-' + uuid.uuid4().hex[:10]
containers = []
images = []
root = Path(tempfile.mkdtemp(prefix=prefix + '-'))


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True, stderr=subprocess.STDOUT, timeout=60).strip()


def create(name, code, *options):
    containers.append(name)
    return docker('run', '-d', '--name', name, '--network', 'none', *options, image, 'python', '-u', '-c', code)


def wait_for(check, seconds=30):
    until = time.monotonic() + seconds
    while time.monotonic() < until:
        if check():
            return
        time.sleep(0.5)
    raise AssertionError('Timeout waiting for isolated fixture')


baseline = {i['Name']: (i['Id'], i['State']['StartedAt']) for i in json.loads(docker('inspect', *docker('ps', '-q').split()))}
try:
    def reader(target):
        path=str(root/(target+'.sock'))
        server=gateway_module.Gateway(path,target)
        os.chmod(path,0o666)  # Disposable fixtures only; production uses 660.
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        servers.append((server,thread))
        return m.DockerReader(path)
    # Rotation before polling is intentionally destructive: compare against the
    # exact retained Docker logs instead of claiming deleted lines can be read.
    rotated = prefix + '-rotation'
    create(rotated, 'for i in range(12000): print("ERROR rotation-%05d "%i + "x"*160)', '--log-driver', 'json-file', '--log-opt', 'max-size=64k', '--log-opt', 'max-file=3')
    wait_for(lambda: docker('inspect', rotated, '--format', '{{.State.Running}}') == 'false')
    retained = docker('logs', '--timestamps', rotated).splitlines()
    assert 0 < len(retained) < 12000
    store = m.Store(str(root / 'rotation.db'))
    monitor = m.Monitor(store, m.Telegram('fake-token', 'fake-chat'), rotated, 'https://example.invalid/', reader=reader(rotated))
    store.set('cursor', m.utc(time.time()-60))
    store.db.commit()
    assert monitor.poll_logs(time.time())
    found = {row[0] for row in store.db.execute('SELECT id FROM seen')}
    expected = {hashlib.sha256(line.encode()).hexdigest() for line in retained}
    assert found == expected
    detailed = store.db.execute('SELECT count(*) FROM outbox').fetchone()[0]
    grouped = int(store.get('overflow_count','0'))
    assert detailed == min(50,len(expected)) and detailed + grouped == len(expected)
    print(f'ROTATION : {len(found)}/{len(expected)} lignes conservées détectées ; {detailed} détails et {grouped} regroupées ; {12000-len(expected)} lignes déjà effacées non récupérables', flush=True)
    store.db.close()

    # Run the actual bot repeatedly with --network none and fake credentials.
    # Its failed real network requests must leave all alerts in the mounted DB.
    fixture = prefix + '-source'
    create(fixture, 'import time; print("ERROR restart test"); time.sleep(300)')
    state = root / 'state'
    state.mkdir(); state.chmod(0o777)
    store = m.Store(str(state / 'monitor.db'))
    store.set('cursor', m.utc(time.time()-60))
    store.db.commit()
    store.db.close()
    (state/'monitor.db').chmod(0o666)
    fixture_reader=reader(fixture)
    bot = prefix + '-bot'
    containers.append(bot)
    docker('run', '-d', '--name', bot, '--network', 'none', '-e', 'BOT_TOKEN=fake-token', '-e', 'CHAT_ID=fake-chat', '-e', 'TARGET_CONTAINER='+fixture, '-e', 'SITE_URL=https://example.invalid/', '-v', str(state)+':/state', '-v', fixture_reader.path+':/ipc/docker-read.sock:ro', image)
    def info():
        out=docker('exec', bot, 'python', '-c', 'import sqlite3,json; d=sqlite3.connect("/state/monitor.db"); print(json.dumps({"cursor":d.execute("SELECT value FROM meta WHERE key=\'cursor\'").fetchone()[0],"count":d.execute("SELECT count(*) FROM outbox").fetchone()[0],"heartbeat":d.execute("SELECT value FROM meta WHERE key=\'heartbeat\'").fetchone()}))')
        return json.loads(out)
    wait_for(lambda: info()['heartbeat'] is not None)
    before = info()['cursor']
    for _ in range(3):
        old_beat = info()['heartbeat']
        docker('restart', bot)
        wait_for(lambda: info()['heartbeat'] != old_beat)
        assert info()['cursor'] >= before and info()['count'] >= 1
    print('REDEMARRAGES : 3 redémarrages réels du bot, curseur et alertes conservés, réseau désactivé', flush=True)

    # Execute the real rollback heredoc with paths, project and tags substituted
    # for a disposable installation; no production resource name is allowed.
    app = root / 'installation'
    backup = root / 'backup'
    app.mkdir(); backup.mkdir(); (app/'logbot').mkdir(); (app/'state').mkdir()
    (app/'state'/'sentinel').write_text('persistent')
    (app/'.env').write_text('BOT_TOKEN=fake-token\nCHAT_ID=fake-chat\n')
    project = prefix + '-rollback'
    name = project + '-bot'
    containers.append(name)
    old_tag, new_tag = project+'-old:latest', project+'-new:latest'
    snapshot = 'reunionwiki-telegram-monitor:before-' + prefix
    images.extend([old_tag, new_tag, snapshot])
    docker('tag', previous_image, old_tag)
    docker('tag', image, new_tag)
    docker('tag', previous_image, snapshot)
    def compose(tag, marker):
        return json.dumps({'version':'3.8','services':{'telegram-logbot':{'image':tag,'container_name':name,'network_mode':'none','env_file':['.env'],'volumes':['./state:/state'],'command':['python','-u','-c',f'import time; print("{marker}"); time.sleep(300)']}}})
    (app/'docker-compose.yml').write_text(compose(old_tag, 'old'))
    def up():return subprocess.check_output(['docker-compose','-p',project,'-f',str(app/'docker-compose.yml'),'up','-d','--no-build'],text=True,stderr=subprocess.STDOUT,timeout=60)
    up()
    with tarfile.open(backup/'installation.tar.gz','w:gz') as archive:
        for p in app.iterdir():
            if p.name != 'state': archive.add(p,arcname='./'+p.name)
    (app/'docker-compose.yml').write_text(compose(new_tag, 'new'))
    (app/'.env').write_text('BOT_TOKEN=fake-new-token\nCHAT_ID=fake-chat\n')
    (app/'DEPLOYED_COMMIT').write_text('synthetic')
    up()
    assert docker('inspect', name, '--format', '{{.Config.Image}}') == new_tag
    docker('image', 'rm', old_tag)  # Restoration must use the saved image tag.
    template=(Path(__file__).parents[1]/'deploy-remote.sh').read_text().split('<<ROLLBACK\n',1)[1].split('\nROLLBACK',1)[0]
    rollback=template.replace('$app',str(app)).replace('$backup',str(backup)).replace('$release',prefix).replace('-p monitoring','-p '+project).replace('monitoring_telegram-logbot:latest',old_tag)
    assert '/home/reunionwiki/' not in rollback and '-p monitoring' not in rollback
    script=backup/'rollback.sh'; script.write_text(rollback+'\n')
    subprocess.check_output(['bash',str(script)],text=True,stderr=subprocess.STDOUT,timeout=60)
    assert docker('inspect', name, '--format', '{{.Config.Image}}') == old_tag
    assert docker('inspect', name, '--format', '{{.Image}}') == docker('image', 'inspect', previous_image, '--format', '{{.Id}}')
    env = json.loads(docker('inspect', name))[0]['Config']['Env']
    assert 'BOT_TOKEN=fake-token' in env
    assert (app/'.env').read_text()=='BOT_TOKEN=fake-token\nCHAT_ID=fake-chat\n'
    assert (app/'state'/'sentinel').read_text()=='persistent'
    assert not (app/'DEPLOYED_COMMIT').exists()
    wait_for(lambda: 'old' in docker('logs',name))
    print('ROLLBACK : ancienne configuration et image réactivées, fichier privé restauré, état persistant conservé, installation isolée', flush=True)
finally:
    for server,thread in servers:
        server.shutdown();server.server_close();thread.join(timeout=2)
    for name in reversed(containers):
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30)
    for tag in images:
        subprocess.run(['docker','image','rm',tag],capture_output=True,timeout=30)
    # The state bind mount may contain root-owned files; a disposable cleanup
    # container removes only the explicitly mounted temporary directory.
    subprocess.run(['docker','run','--rm','--user','0:0','--network','none','-v',str(root)+':/cleanup',image,'python','-c','import shutil; shutil.rmtree("/cleanup",ignore_errors=True)'],capture_output=True,timeout=30)
    root.rmdir()
    after = {i['Name']: (i['Id'], i['State']['StartedAt']) for i in json.loads(docker('inspect', *docker('ps', '-q').split()))}
    assert all(after.get(k) == v for k,v in baseline.items()), 'Un service existant a été modifié ou redémarré'
    print('ISOLATION : services existants inchangés, aucun redémarrage, conteneurs et tags de test supprimés', flush=True)
