"""Real least-privilege pair, fake credentials, no production service changes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

bot_image, gateway_image = sys.argv[1:3]
name = 'secure-monitor-' + uuid.uuid4().hex[:10]
root = Path(tempfile.mkdtemp(prefix=name))
created=[]


def docker(*args):
    return subprocess.check_output(['docker',*args],stderr=subprocess.STDOUT,text=True,timeout=60).strip()


def start(label,image,*args):
    container=name+'-'+label;created.append(container)
    docker('run','-d','--name',container,*args,image)
    return container


try:
    (root/'ipc').mkdir();(root/'state').mkdir()
    docker('run','--rm','--user','0:0','--network','none','-v',str(root)+':/fixture',bot_image,'python','-c','import os; os.chown("/fixture/ipc",10001,10001); os.chmod("/fixture/ipc",0o750); os.chown("/fixture/state",10002,10001); os.chmod("/fixture/state",0o750)')
    source=name+'-source';created.append(source)
    docker('run','-d','--name',source,'--network','none',bot_image,'python','-u','-c','import time; print("ERROR isolated secure fixture"); time.sleep(300)')
    gid=str(Path('/var/run/docker.sock').stat().st_gid)
    gateway=start('reader',gateway_image,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--group-add',gid,'-e','TARGET_CONTAINER='+source,'-v','/var/run/docker.sock:/var/run/docker.sock:ro','-v',str(root/'ipc')+':/ipc')
    bot=start('bot',bot_image,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','-e','BOT_TOKEN=fake-token','-e','CHAT_ID=123','-e','ALLOWED_USER_ID=123','-e','TARGET_CONTAINER='+source,'-e','SITE_URL=https://example.invalid/','-v',str(root/'ipc')+':/ipc:ro','-v',str(root/'state')+':/state')
    code='''import os,json,pathlib,shutil,sqlite3
from docker_reader import DockerReader
assert os.getuid()==10002
assert not pathlib.Path('/var/run/docker.sock').exists()
assert shutil.which('docker') is None
r=DockerReader(); assert r.status()['running'] is True
for path in ('/containers/json','/containers/other/json','/status?container=other'):
 try:r.get(path)
 except OSError:pass
 else:raise AssertionError('Unexpected Docker access')
print('PAIR SECURE : bot non-root, sans socket/client Docker ; état autorisé ; autres lectures refusées')
'''
    end=time.monotonic()+30
    while time.monotonic()<end:
        try:
            result=docker('exec',bot,'python','-c',code)
            print(result,flush=True);break
        except subprocess.CalledProcessError:time.sleep(1)
    else:raise AssertionError('Secure pair not ready')
    info=json.loads(docker('inspect',bot))[0]
    assert info['HostConfig']['ReadonlyRootfs'] and info['HostConfig']['CapDrop']==['ALL']
    assert not any(x.get('Source')=='/var/run/docker.sock' for x in info['Mounts'])
    assert json.loads(docker('inspect',gateway))[0]['HostConfig']['NetworkMode']=='none'
finally:
    for container in reversed(created):subprocess.run(['docker','rm','-f',container],capture_output=True,timeout=30)
    subprocess.run(['docker','run','--rm','--user','0:0','--network','none','-v',str(root)+':/cleanup',bot_image,'python','-c','import shutil; shutil.rmtree("/cleanup",ignore_errors=True)'],capture_output=True,timeout=30)
    root.rmdir()
