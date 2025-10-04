#!/bin/bash

# Script de diagnostic pour Réunion Wiki
# Utilisation: ./diagnostic.sh

echo "=== Diagnostic Réunion Wiki ==="
echo ""

# Variables
APP_DIR="/var/www/reunion-wiki-app"
NGINX_CONFIG="/etc/nginx/sites-available/reunionwiki"

# Fonction pour afficher le statut d'un service
check_service() {
    local service=$1
    if systemctl is-active --quiet "$service"; then
        echo "✓ $service est actif"
    else
        echo "✗ $service n'est pas actif"
    fi
}

# Fonction pour vérifier un port
check_port() {
    local port=$1
    if netstat -tlnp | grep -q ":$port "; then
        echo "✓ Port $port est ouvert"
        netstat -tlnp | grep ":$port "
    else
        echo "✗ Port $port n'est pas ouvert"
    fi
}

# Fonction pour vérifier un processus
check_process() {
    local process=$1
    if pgrep -f "$process" > /dev/null; then
        echo "✓ $process est en cours d'exécution"
        pgrep -f "$process" | head -5
    else
        echo "✗ $process n'est pas en cours d'exécution"
    fi
}

# Fonction pour vérifier un fichier
check_file() {
    local file=$1
    if [ -f "$file" ]; then
        echo "✓ $file existe"
        ls -la "$file"
    else
        echo "✗ $file n'existe pas"
    fi
}

# Fonction pour tester la connectivité HTTP
test_http() {
    local url=$1
    local description=$2
    echo "Test de $description..."
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        echo "✓ $description répond correctement"
    else
        echo "✗ $description ne répond pas"
    fi
}

echo "1. Vérification des services système"
echo "-----------------------------------"
check_service "nginx"
check_service "redis"
echo ""

echo "2. Vérification des ports"
echo "-------------------------"
check_port "80"
check_port "443"
check_port "8000"
check_port "6379"
echo ""

echo "3. Vérification des processus"
echo "-----------------------------"
check_process "gunicorn.*app:app"
check_process "nginx"
check_process "redis"
echo ""

echo "4. Vérification des fichiers de configuration"
echo "---------------------------------------------"
check_file "$NGINX_CONFIG"
check_file "$APP_DIR/app.py"
check_file "$APP_DIR/base.db"
check_file "$APP_DIR/static/maintenance.html"
echo ""

echo "5. Vérification des permissions"
echo "-------------------------------"
if [ -d "$APP_DIR" ]; then
    echo "Permissions du dossier application:"
    ls -la "$APP_DIR" | head -10
else
    echo "✗ Dossier application $APP_DIR n'existe pas"
fi
echo ""

echo "6. Test de connectivité"
echo "-----------------------"
test_http "http://127.0.0.1:8000/" "Application locale"
test_http "https://reunionwiki.re/" "Site en production"
echo ""

echo "7. Vérification des logs récents"
echo "--------------------------------"
if [ -f "$APP_DIR/logs/error.log" ]; then
    echo "Dernières erreurs Gunicorn:"
    tail -5 "$APP_DIR/logs/error.log"
else
    echo "✗ Fichier de log d'erreur Gunicorn non trouvé"
fi

if [ -f "/var/log/nginx/reunionwiki_error.log" ]; then
    echo ""
    echo "Dernières erreurs Nginx:"
    tail -5 "/var/log/nginx/reunionwiki_error.log"
else
    echo "✗ Fichier de log d'erreur Nginx non trouvé"
fi
echo ""

echo "8. Vérification de la base de données"
echo "------------------------------------"
if [ -f "$APP_DIR/base.db" ]; then
    echo "Taille de la base de données:"
    du -h "$APP_DIR/base.db"
    echo ""
    echo "Nombre de sites dans la base:"
    sqlite3 "$APP_DIR/base.db" "SELECT COUNT(*) FROM sites;" 2>/dev/null || echo "✗ Impossible d'accéder à la base de données"
else
    echo "✗ Base de données non trouvée"
fi
echo ""

echo "=== Fin du diagnostic ==="
echo ""
echo "Si des problèmes sont détectés, utilisez:"
echo "- ./restart_app.sh pour redémarrer l'application"
echo "- systemctl restart nginx pour redémarrer nginx"
echo "- systemctl status nginx pour voir le statut de nginx"
