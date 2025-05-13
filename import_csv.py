import sqlite3
import csv

conn  = sqlite3.connect('base.db')
cur = conn.cursor()

#Lis le fichier CSV et insère chaque ligne 
with open('sites.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader : 
        site = (
            row['categorie'].strip(),
            row['nom_du_site'].strip(),
            row['ville'].strip() if row['ville'] else '',
            row['lien'].strip(),
            row['description'].strip(),
            "valide",
            int(row['en_vedette'].strip()) if row ['en_vedette'] else 0
        )
        print(site)  
        cur.execute("""
            INSERT INTO sites (categorie, nom, ville, lien, description, status, en_vedette)
            VALUES (?, ?, ?, ?, ?, ?, ?)         
        """, site)
    
conn.commit()
conn.close()

print("Base de données créée et remplie !")