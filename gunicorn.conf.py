# -*- coding: utf-8 -*-
"""
Configuration Gunicorn pour Réunion Wiki
Optimisée pour la production sur VPS
"""

import multiprocessing
import os

# Configuration de base
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000

# Gestion des requêtes
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
keepalive = 2

# MODIFICATION : Pendant la stabilisation, désactiver preload
preload_app = False

# Logs
accesslog = "-"
errorlog = "-"
loglevel = "info"

# RUNTIME : évite d'écrire dans /var/www
runtime_dir = os.getenv("REUNIONWIKI_RUNTIME_DIR", "/run/reunionwiki")
os.makedirs(runtime_dir, exist_ok=True)
worker_tmp_dir = os.path.join(runtime_dir, "tmp")
os.makedirs(worker_tmp_dir, exist_ok=True)

# PID
pidfile = os.path.join(runtime_dir, "gunicorn.pid")

# MODIFICATION : Suppression user/group - laissé à systemd
# user = os.getenv('GUNICORN_USER', 'www-data')
# group = os.getenv('GUNICORN_GROUP', 'www-data')

# Environnement
raw_env = [
    'FLASK_ENV=production',
    'DATABASE_PATH=/var/www/reunion-wiki-app/base.db'
]

# Headers de sécurité
forwarded_allow_ips = '127.0.0.1'

# Configuration pour la production
if os.getenv('FLASK_ENV') == 'production':
    # En production, on utilise plus de workers
    workers = min(workers, 8)
    
    # MODIFICATION : Pendant la stabilisation, garder debug
    loglevel = "debug"  # repasse en "warning" quand tout est ok
    
    # Sécurité renforcée
    limit_request_line = 4094
    limit_request_fields = 100
    limit_request_field_size = 8190
