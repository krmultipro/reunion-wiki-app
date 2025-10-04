#!/bin/bash
set -e

# Script pour corriger la structure du VPS et déployer la configuration
# À exécuter sur le VPS après avoir copié les fichiers

echo "=== Correction de la structure VPS Réunion Wiki ==="

# Variables
APP_DIR="/var/www/reunion-wiki-app"
BACKUP_DIR="/var/www/reunion-wiki-app-backup-$(date +%Y%m%d-%H%M%S)"
TEMP_DIR="/tmp/reunion-wiki-app-clean"

echo "1. Sauvegarde de l'ancienne structure"
echo "------------------------------------"
if [ -d "$APP_DIR" ]; then
    echo "Sauvegarde vers: $BACKUP_DIR"
    sudo mv "$APP_DIR" "$BACKUP_DIR"
    echo "✓ Ancienne structure sauvegardée"
else
    echo "✓ Aucune ancienne structure à sauvegarder"
fi

echo ""
echo "2. Création de la nouvelle structure"
echo "-----------------------------------"
sudo mkdir -p "$APP_DIR"
sudo chown reunionwiki:www-data "$APP_DIR"
echo "✓ Nouveau dossier créé"

echo ""
echo "3. Copie des fichiers depuis /tmp"
echo "--------------------------------"
if [ -d "$TEMP_DIR" ]; then
    sudo cp -r "$TEMP_DIR"/* "$APP_DIR/"
    echo "✓ Fichiers de l'application copiés"
else
    echo "✗ Dossier $TEMP_DIR non trouvé"
    echo "Copiez d'abord les fichiers depuis votre machine locale"
    exit 1
fi

# Copie des fichiers de configuration
if [ -f "/tmp/nginx_reunionwiki.conf" ]; then
    sudo cp /tmp/nginx_reunionwiki.conf "$APP_DIR/"
    echo "✓ Configuration nginx copiée"
fi

if [ -f "/tmp/gunicorn.conf.py" ]; then
    sudo cp /tmp/gunicorn.conf.py "$APP_DIR/"
    echo "✓ Configuration gunicorn copiée"
fi

if [ -f "/tmp/reunionwiki.service" ]; then
    sudo cp /tmp/reunionwiki.service "$APP_DIR/"
    echo "✓ Service systemd copié"
fi

if [ -d "/tmp/script" ]; then
    sudo cp -r /tmp/script "$APP_DIR/"
    echo "✓ Scripts copiés"
fi

echo ""
echo "4. Correction des permissions"
echo "----------------------------"
sudo chown -R reunionwiki:www-data "$APP_DIR"
sudo chmod +x "$APP_DIR"/script/*.sh
echo "✓ Permissions corrigées"

echo ""
echo "5. Création des dossiers nécessaires"
echo "-----------------------------------"
sudo mkdir -p "$APP_DIR"/{tmp,logs}
sudo chown -R reunionwiki:www-data "$APP_DIR"/{tmp,logs}
echo "✓ Dossiers tmp et logs créés"

echo ""
echo "6. Installation du service systemd"
echo "---------------------------------"
if [ -f "$APP_DIR/reunionwiki.service" ]; then
    sudo cp "$APP_DIR/reunionwiki.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable reunionwiki
    echo "✓ Service systemd installé et activé"
else
    echo "✗ Fichier reunionwiki.service non trouvé"
fi

echo ""
echo "7. Installation de la configuration nginx"
echo "----------------------------------------"
if [ -f "$APP_DIR/nginx_reunionwiki.conf" ]; then
    sudo cp "$APP_DIR/nginx_reunionwiki.conf" /etc/nginx/sites-available/reunionwiki
    sudo nginx -t
    sudo systemctl reload nginx
    echo "✓ Configuration nginx installée et rechargée"
else
    echo "✗ Fichier nginx_reunionwiki.conf non trouvé"
fi

echo ""
echo "8. Installation des dépendances"
echo "------------------------------"
# Redis
if ! systemctl is-active --quiet redis-server; then
    sudo apt update
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    echo "✓ Redis installé et démarré"
else
    echo "✓ Redis déjà installé"
fi

# Flask-Limiter avec Redis
if command -v pip3 &> /dev/null; then
    pip3 install "flask-limiter[redis]"
    echo "✓ Flask-Limiter avec Redis installé"
else
    echo "⚠ pip3 non trouvé, installez manuellement: pip3 install 'flask-limiter[redis]'"
fi

echo ""
echo "9. Démarrage du service"
echo "----------------------"
sudo systemctl start reunionwiki
sleep 3

if systemctl is-active --quiet reunionwiki; then
    echo "✓ Service reunionwiki démarré avec succès"
else
    echo "✗ Échec du démarrage du service"
    sudo systemctl status reunionwiki --no-pager
    exit 1
fi

echo ""
echo "10. Tests de connectivité"
echo "------------------------"
echo "Test local:"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ | grep -q "200"; then
    echo "✓ Application accessible localement (200 OK)"
else
    echo "✗ Application non accessible localement"
fi

echo "Test healthcheck:"
if curl -s -o /dev/null -w "%{http_code}" https://reunionwiki.re/healthz | grep -q "200"; then
    echo "✓ Healthcheck accessible (200 OK)"
else
    echo "✗ Healthcheck non accessible"
fi

echo "Test site principal:"
if curl -s -o /dev/null -w "%{http_code}" https://reunionwiki.re/ | grep -q "200"; then
    echo "✓ Site principal accessible (200 OK)"
else
    echo "✗ Site principal non accessible"
fi

echo ""
echo "=== Correction terminée ==="
echo ""
echo "Structure corrigée:"
echo "- Application: $APP_DIR"
echo "- Ancienne structure sauvegardée: $BACKUP_DIR"
echo ""
echo "Commandes utiles:"
echo "- systemctl status reunionwiki"
echo "- journalctl -u reunionwiki -f"
echo "- $APP_DIR/script/restart_app.sh"
echo "- $APP_DIR/script/diagnostic.sh"
echo ""
echo "Votre site devrait maintenant être accessible sur https://reunionwiki.re/"
