#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ "$#" -gt 1 || ( "${1:-}" != "" && "${1:-}" != "--allow-db-change" ) ]]; then
  echo "Usage : ./deploy-dev.sh [--allow-db-change]" >&2
  exit 2
fi

[[ "$(git branch --show-current)" == "dev" ]] || {
  echo "Déploiement refusé : passe d'abord sur la branche dev validée." >&2
  exit 1
}

for command in git tar ssh scp sha256sum; do
  command -v "$command" >/dev/null || { echo "Commande manquante : $command" >&2; exit 1; }
done

if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
  echo "Déploiement refusé : commite ou mets de côté les modifications et fichiers nouveaux avant de déployer." >&2
  exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
  echo "Déploiement refusé : .venv/bin/python est absent ou non exécutable. Prépare l'environnement Python et installe requirements.txt." >&2
  exit 1
fi
python="$PWD/.venv/bin/python"
commit="$(git rev-parse --short=12 HEAD)"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
release="${stamp}-${commit}"
remote="reunionwiki"
remote_dir="/home/reunionwiki/deployments/${release}"
tmpdir="$(mktemp -d)"
trap 'rm -rf -- "$tmpdir"' EXIT
mkdir -p "$tmpdir/source" "$tmpdir/package" "$tmpdir/test-data"

# Tous les contrôles et transferts utilisent cette même source du commit.
# Only application sources enter the build, even if private files were force-added.
git archive --format=tar "$commit" app.py migrate.py requirements.txt Dockerfile \
  .dockerignore reunion_wiki templates static script tests > "$tmpdir/commit.tar"
extract_source() {
  tar --exclude='docker-compose.yml' --exclude='docker-compose.prod.yml' \
    --exclude='.env' --exclude='.env.*' --exclude='data' --exclude='data/*' \
    --exclude='*.db' --exclude='*.db-wal' --exclude='*.db-shm' \
    --exclude='data_dev' --exclude='data_dev/*' \
    --exclude='data_prod' --exclude='data_prod/*' \
    --exclude='maquettes' --exclude='monitoring' --exclude='.refonte-runtime' \
    --exclude='sephora.jpeg' --exclude='apercu-prive' \
    --exclude='uploads_dev' --exclude='uploads_dev/*' \
    --exclude='uploads_prod' --exclude='uploads_prod/*' \
    --exclude='static/uploads' --exclude='static/uploads/*' \
    --exclude='backups' --exclude='backups/*' \
    --exclude='certbot' --exclude='certbot/*' \
    --exclude='logs' --exclude='logs/*' \
    -xf "$tmpdir/commit.tar" -C "$1"
}
extract_source "$tmpdir/source"

(
  cd "$tmpdir/source"
  export DATABASE_PATH="$tmpdir/test-data/default.db"
  export UPLOAD_FOLDER="$tmpdir/test-data/uploads"
  export MAIL_ENABLED=false RATELIMIT_STORAGE_URL=memory:// FLASK_ENV=development
  echo "Vérification de la syntaxe Python du commit $commit…"
  if ! "$python" -m compileall -q app.py migrate.py reunion_wiki tests script; then
    echo "Déploiement refusé : erreur de syntaxe Python. Aucun transfert effectué." >&2
    exit 1
  fi
  echo "Exécution des tests applicatifs du commit $commit…"
  if ! "$python" script/run_app_tests.py; then
    echo "Déploiement refusé : tests applicatifs en échec (vérifie aussi les dépendances). Aucun transfert effectué." >&2
    exit 1
  fi
)

# Repartir du snapshot Git : aucun fichier généré ou modifié par les tests envoyé.
extract_source "$tmpdir/package"
tar -czf "$tmpdir/source.tar.gz" -C "$tmpdir/package" .
"$python" "$tmpdir/package/script/deploy_artifact.py" "$tmpdir/source.tar.gz"
if tar -tzf "$tmpdir/source.tar.gz" | grep -E '(^|/)(\.env[^/]*|data|data_dev|uploads_dev|uploads_prod|backups|certbot)(/|$)|(^|/)docker-compose(\.prod)?\.yml$' >/dev/null; then
  echo "Archive refusée : un fichier sensible est présent." >&2
  exit 1
fi

echo "Contrôles locaux réussis pour le commit $commit."
archive_hash="$(sha256sum "$tmpdir/source.tar.gz" | cut -d' ' -f1)"
echo "Archive SHA256 : $archive_hash"
ssh "$remote" "mkdir -p '$remote_dir' && chmod 700 '$remote_dir'"
scp "$tmpdir/source.tar.gz" "$remote:$remote_dir/source.tar.gz"
scp "$tmpdir/package/script/deploy-dev-remote.sh" "$remote:$remote_dir/deploy.sh"

echo "Construction et vérifications sur le VPS…"
ssh "$remote" bash "$remote_dir/deploy.sh" "$release" "$commit" "$archive_hash" "${1:-}"
