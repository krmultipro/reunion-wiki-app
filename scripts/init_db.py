import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "base.db"

#connecte à la base
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

#crée la table sites
with open(BASE_DIR / "schema.sql", "r", encoding="utf-8") as f:
    cur.executescript(f.read())

conn.commit()
conn.close()
print(f" Table 'sites' créée dans {DB_PATH}")
