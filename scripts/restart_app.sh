#!/bin/bash
set -e

# Script simplifié pour redémarrer l'application Réunion Wiki via systemd
# Utilisation: ./restart_app.sh

echo "=== Restart Reunion Wiki via systemd ==="

# Redémarrage via systemd
sudo systemctl restart reunionwiki

# Vérification du statut
echo ""
echo "=== Statut du service ==="
sudo systemctl status reunionwiki --no-pager -l | sed -n '1,25p'

# Test de connectivité
echo ""
echo "=== Test de connectivité ==="
if curl -I http://127.0.0.1:8000/ 2>/dev/null | head -1; then
    echo "✓ Application accessible localement"
else
    echo "✗ Application non accessible"
fi

echo ""
echo "=== Vérification du port ==="
if ss -ltnp | grep 127.0.0.1:8000; then
    echo "✓ Port 8000 ouvert"
else
    echo "✗ Port 8000 fermé"
fi

echo ""
echo "=== Logs récents ==="
journalctl -u reunionwiki -n 10 --no-pager

echo ""
echo "=== Redémarrage terminé ==="
