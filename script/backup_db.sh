#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$APP_DIR/data_prod/backups"
COMPOSE_FILE="$APP_DIR/docker-compose.prod.yml"

mkdir -p "$OUT_DIR"

cd "$APP_DIR"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose -f "$COMPOSE_FILE")
elif command -v docker >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose -f "$COMPOSE_FILE")
else
  echo "Erreur: docker-compose (ou docker compose) introuvable." >&2
  exit 1
fi

"${COMPOSE_CMD[@]}" exec -T web python - <<'PY'
import os, sqlite3, gzip, shutil
from datetime import datetime, timedelta

db = "/data/base.db"
out_dir = "/data/backups"
os.makedirs(out_dir, exist_ok=True)

ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
tmp = f"{out_dir}/base_{ts}.db"
gz  = f"{tmp}.gz"

src = sqlite3.connect(db)
dst = sqlite3.connect(tmp)
src.backup(dst)
dst.close()
src.close()

with open(tmp, "rb") as f_in, gzip.open(gz, "wb", compresslevel=6) as f_out:
    shutil.copyfileobj(f_in, f_out)
os.remove(tmp)

# rotation 30 jours sur les backups gzip "base_*.db.gz"
limit = datetime.now() - timedelta(days=30)
for name in os.listdir(out_dir):
    if not (name.startswith("base_") and name.endswith(".db.gz")):
        continue
    path = os.path.join(out_dir, name)
    if datetime.fromtimestamp(os.path.getmtime(path)) < limit:
        os.remove(path)

print("Backup OK:", gz)
PY
