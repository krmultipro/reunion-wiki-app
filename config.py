# -*- coding: utf-8 -*-
"""
Configuration pour Réunion Wiki
SÉCURITÉ : Configuration centralisée avec variables d'environnement
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "base.db"

# Chargement des variables d'environnement
load_dotenv()

class Config:
    """Configuration de base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(DEFAULT_DB_PATH))
    
    # NOTIFICATIONS : configuration email (désactivée par défaut)
    MAIL_ENABLED = os.getenv('MAIL_ENABLED', 'false').lower() == 'true'
    MAIL_SERVER = os.getenv('MAIL_SERVER', '')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    MAIL_RECIPIENTS = [
        email.strip()
        for email in os.getenv('MAIL_RECIPIENTS', '').split(',')
        if email.strip()
    ]
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')
    
    # PERFORMANCE : Configuration du cache
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 an pour les fichiers statiques
    
    # SÉCURITÉ : Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day, 50 per hour")
    
    # LOGGING
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # SÉCURITÉ : Configuration stricte pour la production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # PERFORMANCE : Configuration optimisée
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    
    # LOGGING : Plus strict en production
    LOG_LEVEL = 'WARNING'

# Sélection de la configuration selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
