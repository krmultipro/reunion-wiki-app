#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'optimisation de la base de données Réunion Wiki
PERFORMANCE : Ajoute des index pour accélérer les requêtes
"""

import sqlite3
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'base.db')

def optimize_database():
    """Ajoute des index pour optimiser les performances"""
    print("🔧 Optimisation de la base de données...")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        
        # PERFORMANCE : Index sur les colonnes fréquemment utilisées
        indexes = [
            ("idx_sites_status", "CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status)"),
            ("idx_sites_categorie", "CREATE INDEX IF NOT EXISTS idx_sites_categorie ON sites(categorie)"),
            ("idx_sites_date_ajout", "CREATE INDEX IF NOT EXISTS idx_sites_date_ajout ON sites(date_ajout DESC)"),
            ("idx_sites_en_vedette", "CREATE INDEX IF NOT EXISTS idx_sites_en_vedette ON sites(en_vedette)"),
            ("idx_sites_status_categorie", "CREATE INDEX IF NOT EXISTS idx_sites_status_categorie ON sites(status, categorie)"),
            ("idx_sites_status_vedette", "CREATE INDEX IF NOT EXISTS idx_sites_status_vedette ON sites(status, en_vedette)")
        ]
        
        for index_name, query in indexes:
            print(f"  ✅ Création de l'index {index_name}")
            cur.execute(query)
        
        # PERFORMANCE : Analyse des statistiques pour l'optimiseur
        print("  📊 Analyse des statistiques...")
        cur.execute("ANALYZE")
        
        # MAINTENANCE : Nettoyage de la base
        print("  🧹 Nettoyage de la base...")
        cur.execute("VACUUM")
        
        conn.commit()
        print("✅ Optimisation terminée avec succès !")
        
        # Affichage des statistiques
        cur.execute("SELECT COUNT(*) FROM sites")
        total_sites = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM sites WHERE status = 'valide'")
        sites_valides = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT categorie) FROM sites WHERE status = 'valide'")
        categories = cur.fetchone()[0]
        
        print(f"\n📈 Statistiques de la base :")
        print(f"  • Total des sites : {total_sites}")
        print(f"  • Sites valides : {sites_valides}")
        print(f"  • Catégories : {categories}")
        
    except sqlite3.Error as e:
        print(f"❌ Erreur lors de l'optimisation : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    optimize_database()
