#!/usr/bin/env bash
set -euo pipefail

release="${1:?}"
commit="${2:?}"
expected_hash="${3:?}"
allow_db_change="${4:-}"
[[ "$release" =~ ^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{12}$ ]] || exit 2
[[ "$commit" =~ ^[a-f0-9]{12}$ ]] || exit 2
[[ "$allow_db_change" == "" || "$allow_db_change" == "--allow-db-change" ]] || exit 2

app_dir=/var/www/reunion-wiki-app-dev
deploy_root=/home/reunionwiki/deployments
release_dir="$deploy_root/$release"
candidate="reunion-wiki-app-dev_web:candidate-$commit"
current="reunion-wiki-app-dev_web:latest"
previous="reunion-wiki-app-dev_web:before-$release"

exec 9>"$deploy_root/.deploy-dev.lock"
flock -n 9 || { echo "Un déploiement dev est déjà en cours." >&2; exit 1; }
umask 077
cd "$release_dir"
echo "$expected_hash  source.tar.gz" | sha256sum -c -
printf 'branch=dev\ncommit=%s\narchive_sha256=%s\n' "$commit" "$expected_hash" > release-info.txt
mkdir -p source db-preflight db-backup data-test
tar -xzf source.tar.gz -C source
test -f source/Dockerfile
test -f source/migrate.py
test -f "$app_dir/.env"
test -f "$app_dir/data/base.db"
docker-compose -p reunion-wiki-app-dev -f "$app_dir/docker-compose.yml" config -q

# Candidate/build layers, data copies and a 512 MiB emergency reserve.
# This estimate never authorizes pruning other applications or rollback images.
old_image="$(docker inspect web_dev --format '{{.Image}}')"
old_bytes="$(docker image inspect "$old_image" --format '{{.Size}}')"
source_bytes="$(du -sb source | cut -f1)"
data_bytes="$(du -sb "$app_dir/data" | cut -f1)"
free_bytes="$(df -B1 --output=avail "$app_dir" | tail -1 | tr -d ' ')"
for measure in "$old_bytes" "$source_bytes" "$data_bytes" "$free_bytes"; do
  [[ "$measure" =~ ^[0-9]+$ ]] || { echo "Capacité disque impossible à mesurer ; déploiement refusé." >&2; exit 1; }
done
required_bytes=$((3 * old_bytes + 3 * source_bytes + 3 * data_bytes + 536870912))
if (( free_bytes < required_bytes )); then
  echo "Déploiement refusé : capacité disque insuffisante pour candidate, copies et réserve. Aucun nettoyage automatique." >&2
  exit 1
fi
printf 'free_bytes=%s\nrequired_bytes=%s\n' "$free_bytes" "$required_bytes" >> release-info.txt

echo "Construction de l'image candidate…"
docker build --label "reunionwiki.branch=dev" --label "reunionwiki.commit=$commit" \
  --label "reunionwiki.release=$release" -t "$candidate" source

echo "Tests automatisés dans l'image candidate, sans réseau ni secrets serveur…"
docker run --rm --network none --tmpfs /tmp:rw,mode=1777 \
  -e DATABASE_PATH=/tmp/deploy-tests/base.db -e UPLOAD_FOLDER=/tmp/deploy-tests/uploads \
  -e SECRET_KEY=isolated-deploy-tests -e MAIL_ENABLED=false -e RATELIMIT_STORAGE_URL=memory:// \
  "$candidate" sh -ec 'mkdir -p /tmp/deploy-tests/uploads; python script/run_app_tests.py'

# Copie préliminaire en ligne pour tester les migrations uniquement.
# Le snapshot destiné au rollback sera pris après arrêt des écritures.
docker run --rm --network none --user 0:0 \
  -v "$app_dir/data:/source" -v "$release_dir/db-preflight:/backup" \
  "$candidate" python script/deploy_sqlite.py snapshot /source/base.db /backup/base.db
docker run --rm --network none --user 0:0 \
  -v "$release_dir/db-preflight:/backup:ro" -v "$app_dir/data:/source:ro" \
  -v "$release_dir/data-test:/data" "$candidate" sh -ec '
  cp /backup/base.db /data/base.db
  if [ -d /source/uploads ]; then cp -a /source/uploads /data/uploads; fi
  chown -R appuser:appuser /data
  chmod -R go-rwx /data
  '

before="$(docker run --rm --network none --user 0:0 -v "$release_dir/data-test:/data" "$candidate" python -c 'import hashlib,sqlite3; db=sqlite3.connect("file:/data/base.db?mode=ro",uri=True); print(hashlib.sha256("\n".join(db.iterdump()).encode()).hexdigest())')"
echo "Test des migrations sur une copie de la base…"
docker run --rm --network none --user 0:0 \
  -e SECRET_KEY=isolated-deploy-probe -e MAIL_ENABLED=false -e FLASK_ENV=production -e DATABASE_PATH=/data/base.db \
  -e UPLOAD_FOLDER=/data/uploads -e RATELIMIT_STORAGE_URL=memory:// \
  -v "$release_dir/data-test:/data" "$candidate" \
  sh -c 'python migrate.py && python -c "from app import app; assert len(list(app.url_map.iter_rules())) > 0"'
after="$(docker run --rm --network none --user 0:0 -v "$release_dir/data-test:/data" "$candidate" python -c 'import hashlib,sqlite3; db=sqlite3.connect("file:/data/base.db?mode=ro",uri=True); print(hashlib.sha256("\n".join(db.iterdump()).encode()).hexdigest())')"
if [[ "$before" != "$after" && "$allow_db_change" != "--allow-db-change" ]]; then
  echo "La migration modifie la base. Rien n'a été basculé." >&2
  echo "Vérifie le changement puis relance avec --allow-db-change." >&2
  exit 1
fi

# Test réel du démarrage, mais sans port public et avec la copie de données.
probe="dev-probe-${commit}"
docker run -d --name "$probe" --network none \
  -e SECRET_KEY=isolated-deploy-probe -e MAIL_ENABLED=false -e FLASK_ENV=production -e DATABASE_PATH=/data/base.db \
  -e UPLOAD_FOLDER=/data/uploads -e RATELIMIT_STORAGE_URL=memory:// \
  -v "$release_dir/data-test:/data" "$candidate" >/dev/null
cleanup_probe() { docker rm -f "$probe" >/dev/null 2>&1 || true; }
trap cleanup_probe EXIT
if ! docker exec -i "$probe" python - < source/script/deploy_smoke.py; then
  docker logs --tail 40 "$probe"
  exit 1
fi
cleanup_probe
trap - EXIT

docker tag "$old_image" "$previous"
# Sauvegarder le code avant toute mutation, indépendamment de sa restauration.
docker run --rm --network none --user 0:0 -v "$app_dir:/appdir:ro" \
  -v "$release_dir:/release" "$candidate" sh -ec '
  tar -czf /release/previous-source.tar.gz -C /appdir \
    --exclude=data --exclude=.env --exclude=".env.*" \
    --exclude=docker-compose.yml --exclude="docker-compose.yml.backup-*" .
  '
snapshot_ready=0
source_sync_started=0
rollback() {
  local original_status="$?"
  trap - ERR
  echo "Échec : restauration de l'image précédente et contrôle du service." >&2
  # Chaque échec est explicite : aucune étape dépendante ne doit continuer.
  if ! docker stop web_dev >/dev/null; then
    echo "ROLLBACK ÉCHOUÉ : impossible d'arrêter web_dev ; base préservée." >&2; exit 1
  fi
  if [[ "$snapshot_ready" == 1 ]]; then
    # Preserve writes received by a failed candidate for manual reconciliation.
    if ! docker run --rm --network none --user 0:0 \
      -v "$release_dir/db-backup:/backup" -v "$app_dir/data:/data:ro" \
      "$candidate" python script/deploy_data.py snapshot /data /backup/failed-candidate; then
      echo "ROLLBACK ÉCHOUÉ : conservation des écritures candidates impossible ; service laissé arrêté." >&2; exit 1
    fi
    if ! docker run --rm --network none --user 0:0 \
      -v "$release_dir/db-backup:/backup:ro" -v "$app_dir/data:/data" \
      "$candidate" python script/deploy_data.py restore /backup/data /data; then
      echo "ROLLBACK ÉCHOUÉ : restauration SQLite/uploads impossible ; service laissé arrêté." >&2; exit 1
    fi
  fi
  if [[ "$source_sync_started" == 1 ]]; then
    if ! docker run --rm --network none --user 0:0 -v "$release_dir:/release:ro" \
      -v "$app_dir:/appdir" "$candidate" sh -ec '
      find /appdir -mindepth 1 -maxdepth 1 \
        ! -name data ! -name .env ! -name ".env.*" \
        ! -name docker-compose.yml ! -name "docker-compose.yml.backup-*" \
        -exec rm -rf -- {} +
      tar -xzf /release/previous-source.tar.gz -C /appdir
      find /appdir -mindepth 1 -maxdepth 1 \
        ! -name data ! -name .env ! -name ".env.*" \
        ! -name docker-compose.yml ! -name "docker-compose.yml.backup-*" \
        -exec chown -R 1000:1000 -- {} +
      '; then
      echo "ROLLBACK ÉCHOUÉ : restauration du code impossible ; service laissé arrêté." >&2; exit 1
    fi
  fi
  if ! docker tag "$previous" "$current" || \
     ! docker-compose -p reunion-wiki-app-dev -f "$app_dir/docker-compose.yml" up -d --no-deps --force-recreate web; then
    echo "ROLLBACK ÉCHOUÉ : redémarrage de l'ancienne image impossible." >&2; exit 1
  fi
  if ! docker exec reunionwiki_prod_nginx_1 nginx -t || \
     ! docker exec reunionwiki_prod_nginx_1 nginx -s reload || \
     ! docker exec -i web_dev python - < source/script/deploy_smoke.py || \
     ! docker exec reunionwiki_prod_nginx_1 sh -c 'wget -qO /dev/null http://web_dev:8000/'; then
    echo "ROLLBACK ÉCHOUÉ : ancien service non validé ; intervention nécessaire." >&2; exit 1
  fi
  if [[ "$snapshot_ready" == 1 ]]; then
    echo "Retour arrière contrôlé : ancienne image et base restaurées. Déploiement en échec." >&2
  else
    echo "Retour arrière contrôlé : ancienne image redémarrée, base initiale conservée. Déploiement en échec." >&2
  fi
  exit "$original_status"
}
trap rollback ERR
echo "Arrêt de web_dev et snapshot final avant bascule…"
docker stop web_dev >/dev/null
docker run --rm --network none --user 0:0 \
  -v "$app_dir/data:/source:ro" -v "$release_dir/db-backup:/backup" \
  "$candidate" python script/deploy_data.py snapshot /source /backup/data
snapshot_ready=1
echo "Bascule du seul conteneur web_dev…"
docker tag "$candidate" "$current"
docker-compose -p reunion-wiki-app-dev -f "$app_dir/docker-compose.yml" up -d --no-deps --force-recreate web
docker exec -i web_dev python - < source/script/deploy_smoke.py
docker exec reunionwiki_prod_nginx_1 nginx -t
docker exec reunionwiki_prod_nginx_1 nginx -s reload
docker exec reunionwiki_prod_nginx_1 sh -c 'wget -qO /dev/null http://web_dev:8000/'
[[ "$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' https://dev.reunionwiki.re/)" == 401 ]]
[[ "$(curl -sS --max-time 15 -o /dev/null -w '%{http_code}' https://reunionwiki.re/)" == 200 ]]

# Le code du répertoire de travail du VPS doit correspondre à l'image active.
# Les données, secrets et le Compose VPS restent intacts.
source_sync_started=1
docker run --rm --network none --user 0:0 -v "$app_dir:/appdir" \
  -v "$release_dir:/release" "$candidate" sh -ec '
  find /appdir -mindepth 1 -maxdepth 1 \
    ! -name data ! -name .env ! -name ".env.*" \
    ! -name docker-compose.yml ! -name "docker-compose.yml.backup-*" \
    -exec rm -rf -- {} +
  cp -a /release/source/. /appdir/
  find /appdir -mindepth 1 -maxdepth 1 \
    ! -name data ! -name .env ! -name ".env.*" \
    ! -name docker-compose.yml ! -name "docker-compose.yml.backup-*" \
    -exec chown -R 1000:1000 -- {} +
  '
trap - ERR
echo "Déployé : branche dev, commit $commit, release $release."
echo "Sauvegardes : $release_dir (image précédente et base incluses)."
