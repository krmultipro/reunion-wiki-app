import sqlite3

#connecte à la base
conn = sqlite3.connect("base.db")
cur = conn.cursor()

#crée la table sites
with open("schema.sql", "r", encoding="utf-8") as f:
    cur.executescript(f.read())

conn.commit()
conn.close()
print(" Table 'sites' créée dans base.db")
