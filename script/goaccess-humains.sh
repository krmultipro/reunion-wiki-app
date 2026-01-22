#!/bin/bash

BASE_DIR="/var/www/reunion-wiki-app"
LOG_FILE="$BASE_DIR/logs/nginx/access.log"
REPORT_DIR="$BASE_DIR/static/reports"

DATE=$(date +"%Y-%m-%d-%Hh%M")
REPORT_FILE="report-humains-$DATE.html"
LATEST_LINK="report-humains.html"

# Génération du rapport horodaté
goaccess "$LOG_FILE" \
  --log-format=COMBINED \
  --ignore-crawlers \
  -o "$REPORT_DIR/$REPORT_FILE"

# Mise à jour du lien stable
ln -sf "$REPORT_FILE" "$REPORT_DIR/$LATEST_LINK"
