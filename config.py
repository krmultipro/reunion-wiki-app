# -*- coding: utf-8 -*-
"""
Configuration pour Réunion Wiki
SÉCURITÉ : Configuration centralisée avec variables d'environnement
"""

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class Config:
    """Configuration de base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'base.db')
    
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
