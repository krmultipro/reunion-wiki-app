#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export des sites depuis la base SQLite Réunion Wiki.
Usage type (sur le VPS) :
    python3 script/export_sites.py \
        --database /var/www/reunion-wiki-app/base.db \
        --output-dir /home/reunionwiki/exports
Le script crée le dossier cible si besoin puis génère un CSV horodaté.
"""

import argparse
import csv
import os
import sqlite3
from datetime import datetime

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:  # pragma: no cover
    load_dotenv = None


def parse_args() -> argparse.Namespace:
    if load_dotenv:
        load_dotenv()

    default_db = os.getenv("DATABASE_PATH", "base.db")
    default_output = os.getenv("EXPORT_OUTPUT_DIR", "backups/exports")

    parser = argparse.ArgumentParser(
        description="Exporte la table `sites` vers un CSV."
    )
    parser.add_argument(
        "--database",
        default=default_db,
        help=f"Chemin vers la base SQLite (défaut: {default_db})",
    )
    parser.add_argument(
        "--output-dir",
        default=default_output,
        help=f"Dossier de destination des exports (défaut: {default_output})",
    )
    parser.add_argument(
        "--delimiter",
        default=";",
        help="Séparateur CSV (défaut: ';')",
    )
    return parser.parse_args()


def export_sites(database: str, output_dir: str, delimiter: str) -> str:
    if not os.path.exists(database):
        raise FileNotFoundError(f"Base introuvable: {database}")

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"sites_export_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
                id,
                categorie,
                nom,
                ville,
                lien,
                description,
                status,
                date_ajout,
                en_vedette
            FROM sites
            ORDER BY date_ajout DESC, id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter)
        writer.writerow(rows[0].keys() if rows else [
            "id",
            "categorie",
            "nom",
            "ville",
            "lien",
            "description",
            "status",
            "date_ajout",
            "en_vedette",
        ])
        for row in rows:
            writer.writerow([row[key] for key in row.keys()])

    return filepath


def main() -> None:
    args = parse_args()
    try:
        output_file = export_sites(args.database, args.output_dir, args.delimiter)
    except Exception as exc:  # pragma: no cover
        print(f"❌ Export impossible: {exc}")
        raise SystemExit(1) from exc

    print(f"Export terminé : {output_file}")


if __name__ == "__main__":
    main()
