#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/reunion-wiki-app"
OUT_DIR="$APP_DIR/backups"

mkdir -p "$OUT_DIR"

cd "$APP_DIR"

docker-compose -f docker-compose.prod.yml exec -T web python - <<'PY'
import os, sqlite3, gzip, shutil
from datetime import datetime, timedelta

db = "/data/base.db"
out_dir = "/app/backups"
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
