#!/bin/bash

# Se placer a la racine du projet
cd "$(dirname "$0")/.."

# Charger les variables d'environnement DEV
set -a
source .env.dev
set +a

# Activer le virtualenv
source .venv/bin/activate

# Lancer l'application
python3 app.py
