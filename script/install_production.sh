#!/bin/bash
set -e

# Script d'installation complète pour la production
# Utilisation: ./install_production.sh

echo "=== Installation production Réunion Wiki ==="

# Variables
APP_DIR="/var/www/reunion-wiki-app"
SERVICE_FILE="/etc/systemd/system/reunionwiki.service"
NGINX_CONFIG="/etc/nginx/sites-available/reunionwiki"

# Vérification des droits root
if [ "$EUID" -ne 0 ]; then
    echo "Ce script doit être exécuté en tant que root ou avec sudo"
    exit 1
fi

echo "1. Création des dossiers et permissions"
echo "--------------------------------------"
mkdir -p "$APP_DIR"/{tmp,logs}
chown -R reunionwik:www-data "$APP_DIR"/{tmp,logs}
chmod 755 "$APP_DIR"/{tmp,logs}
echo "✓ Dossiers créés avec les bonnes permissions"

echo ""
echo "2. Installation du service systemd"
echo "---------------------------------"
if [ -f "reunionwiki.service" ]; then
    cp reunionwiki.service "$SERVICE_FILE"
    systemctl daemon-reload
    systemctl enable reunionwiki
    echo "✓ Service systemd installé et activé"
else
    echo "✗ Fichier reunionwiki.service non trouvé"
    exit 1
fi

echo ""
echo "3. Installation de la configuration nginx"
echo "----------------------------------------"
if [ -f "nginx_reunionwiki.conf" ]; then
    cp nginx_reunionwiki.conf "$NGINX_CONFIG"
    nginx -t
    systemctl reload nginx
    echo "✓ Configuration nginx installée et rechargée"
else
    echo "✗ Fichier nginx_reunionwiki.conf non trouvé"
    exit 1
fi

echo ""
echo "4. Installation des dépendances Redis"
echo "------------------------------------"
if command -v pip3 &> /dev/null; then
    pip3 install "flask-limiter[redis]"
    echo "✓ Flask-Limiter avec Redis installé"
else
    echo "⚠ pip3 non trouvé, installez manuellement: pip3 install 'flask-limiter[redis]'"
fi

echo ""
echo "5. Démarrage du service"
echo "----------------------"
systemctl restart reunionwiki
sleep 3

if systemctl is-active --quiet reunionwiki; then
    echo "✓ Service reunionwiki démarré avec succès"
else
    echo "✗ Échec du démarrage du service"
    systemctl status reunionwiki --no-pager
    exit 1
fi

echo ""
echo "6. Tests de connectivité"
echo "-----------------------"
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
echo "7. Vérification des logs"
echo "-----------------------"
echo "Logs du service:"
journalctl -u reunionwiki -n 5 --no-pager

echo ""
echo "=== Installation terminée ==="
echo ""
echo "Commandes utiles:"
echo "- systemctl status reunionwiki"
echo "- journalctl -u reunionwiki -f"
echo "- ./restart_app.sh"
echo "- ./diagnostic.sh"
echo ""
echo "Votre site devrait maintenant être accessible sur https://reunionwiki.re/"
