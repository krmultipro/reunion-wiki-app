#!/usr/bin/env bash
set -euo pipefail
umask 077
stage=$1
commit=$2
[[ "$stage" == /home/reunionwiki/deployments/monitoring-* && "$commit" =~ ^[a-f0-9]{40}$ ]] || exit 2
app=/home/reunionwiki/reunionwiki/monitoring
release="$(date -u +%Y%m%dT%H%M%SZ)-${commit:0:12}"
backup="/home/reunionwiki/deployments/monitoring-backup-$release"
image="reunionwiki-telegram-monitor:$commit"
cd "$app"
# The old files may contain credentials: backup permissions stay private.
mkdir -p "$backup"
tar --exclude='./state' -czf "$backup/installation.tar.gz" .
docker inspect telegram-logbot --format '{{.Image}}' > "$backup/image-id"
docker tag "$(cat "$backup/image-id")" "reunionwiki-telegram-monitor:before-$release"
docker inspect telegram-logbot --format '{{.Id}}' > "$backup/container-id"
python3 - "$backup" <<'PY'
import json, pathlib, subprocess, sys
info=json.loads(subprocess.check_output(['docker','inspect','telegram-logbot']))[0]
(pathlib.Path(sys.argv[1])/'other-containers.json').write_text(json.dumps({i['Name']:i['Id'] for i in json.loads(subprocess.check_output(['docker','inspect']+subprocess.check_output(['docker','ps','-q'],text=True).split())) if i['Name']!='/telegram-logbot'}))
PY
docker build -t "$image" "$stage/monitoring/logbot"
docker run --rm --network none -v "$stage/monitoring:/source:ro" "$image" python -m unittest discover -s /source/tests -v
docker run --rm --network none -v /var/run/docker.sock:/var/run/docker.sock:ro -v "$stage/monitoring:/source:ro" "$image" python /source/tests/integration_docker.py "$image"
# The original SSH installation may be root-owned. Limit ownership changes to
# the monitoring directories and files that this deployment manages.
if [[ ! -w "$app" || ! -w "$app/docker-compose.yml" || ! -w "$app/logbot" || ! -w "$app/logbot/Dockerfile" ]]; then
  docker run --rm --network none -v "$app:/installation" "$image" python -c '
import os,sys
for name in ("", "docker-compose.yml", "logbot", "logbot/Dockerfile", "logbot/monitor.py", "logbot/.dockerignore", ".env", "README.md", "DEPLOYED_COMMIT"):
 p=os.path.join("/installation",name)
 if os.path.exists(p): os.chown(p,int(sys.argv[1]),int(sys.argv[2]))
' "$(id -u)" "$(id -g)"
fi
# Preserve existing credentials on the server; never put them in the archive.
python3 - "$app" "$commit" <<'PY'
import json, pathlib, subprocess, sys
p=pathlib.Path(sys.argv[1])
env=dict(v.split('=',1) for v in json.loads(subprocess.check_output(['docker','inspect','telegram-logbot']))[0]['Config']['Env'] if '=' in v)
assert env.get('BOT_TOKEN') and env.get('CHAT_ID')
for key in ('BOT_TOKEN','CHAT_ID'):
 assert '\n' not in env[key] and '\r' not in env[key]
(p/'.env').write_text('BOT_TOKEN='+env['BOT_TOKEN']+'\nCHAT_ID='+env['CHAT_ID']+'\nMONITORING_RELEASE='+sys.argv[2]+'\n')
(p/'.env').chmod(0o600)
PY
cp "$stage/monitoring/docker-compose.yml" "$app/docker-compose.yml"
cp "$stage/monitoring/logbot/Dockerfile" "$stage/monitoring/logbot/monitor.py" "$stage/monitoring/logbot/.dockerignore" "$app/logbot/"
cp "$stage/monitoring/README.md" "$app/README.md"
printf '%s\n' "$commit" > "$app/DEPLOYED_COMMIT"
# Explicit rollback command restores only the monitoring installation.
cat > "$backup/rollback.sh" <<ROLLBACK
#!/usr/bin/env bash
set -euo pipefail
cd '$app'
docker-compose -p monitoring down
rm -f .env DEPLOYED_COMMIT logbot/monitor.py logbot/.dockerignore
 tar -xzf '$backup/installation.tar.gz' -C '$app'
docker tag 'reunionwiki-telegram-monitor:before-$release' monitoring_telegram-logbot:latest
docker-compose -p monitoring up -d --no-build telegram-logbot
ROLLBACK
chmod 700 "$backup/rollback.sh"
rollback() { "$backup/rollback.sh"; }
trap rollback ERR
docker-compose -p monitoring config -q
docker-compose -p monitoring up -d --no-build --no-deps telegram-logbot
healthy=false
for attempt in $(seq 1 30); do
  if [[ "$(docker inspect telegram-logbot --format '{{.State.Health.Status}}')" == healthy ]]; then healthy=true; break; fi
  sleep 2
done
[[ "$healthy" == true ]]
python3 - "$backup" <<'PY'
import json,pathlib,subprocess,sys
before=json.loads((pathlib.Path(sys.argv[1])/'other-containers.json').read_text())
current={i['Name']:i['Id'] for i in json.loads(subprocess.check_output(['docker','inspect']+subprocess.check_output(['docker','ps','-q'],text=True).split()))}
assert all(current.get(k)==v for k,v in before.items()), 'Un autre conteneur a changé'
print('Autres conteneurs inchangés')
PY
trap - ERR
printf 'Déployé : %s\nRetour arrière : %s/rollback.sh\n' "$commit" "$backup"
