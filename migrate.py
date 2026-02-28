import sqlite3
import os
from flask import Flask
from config import config

# Recrée une mini app juste pour charger la config proprement
app = Flask(__name__)

env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(env, config['default']))

DATABASE_PATH = app.config['DATABASE_PATH']

print("📂 Vérification DB :", DATABASE_PATH)

EXPECTED_SCHEMA = {
    "sites": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "nom": "TEXT NOT NULL",
        "ville": "TEXT",
        "lien": "TEXT NOT NULL",
        "description": "TEXT",
        "categorie": "TEXT",
        "status": "TEXT DEFAULT 'en_attente'",
        "date_ajout": "DATETIME",
        "en_vedette": "INTEGER DEFAULT 0",
        "click_count": "INTEGER DEFAULT 0",
    },
    "site_clicks": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "site_id": "INTEGER NOT NULL",
        "ip_address": "TEXT NOT NULL",
        "user_agent": "TEXT",
        "clicked_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
    },
}

conn = sqlite3.connect(DATABASE_PATH)
cur = conn.cursor()

for table, columns in EXPECTED_SCHEMA.items():

    # Crée table si absente
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {', '.join(f"{col} {defn}" for col, defn in columns.items())}
        )
    """)

    # Vérifie colonnes existantes
    cur.execute(f"PRAGMA table_info({table})")
    existing_cols = [col[1] for col in cur.fetchall()]

    for col, defn in columns.items():
        if col not in existing_cols:
            print(f"➕ Ajout colonne {col} dans {table}")
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {defn}")

conn.commit()
conn.close()

print("✅ Schéma synchronisé")