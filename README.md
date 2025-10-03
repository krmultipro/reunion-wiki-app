# 🌴 Réunion Wiki

Projet Flask pour regrouper tous les sites utiles de La Réunion.

## 🚀 Technologies

- **Backend** : Python + Flask + Jinja2
- **Base de données** : SQLite avec optimisations
- **Frontend** : HTML5 + CSS3 + JavaScript (PWA)
- **Sécurité** : Flask-WTF + Rate Limiting + Headers sécurisés
- **Déploiement** : VPS OVH + Gunicorn

## 🔧 Installation

```bash
# Cloner le projet
git clone [votre-repo]
cd reunion-wiki

# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances (liste minimale)
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Modifier .env avec vos valeurs

# Optimiser la base de données
python3 optimize_db.py

# Lancer l'application
python3 app.py
```

## 🛡️ Améliorations de Sécurité Implémentées

### 1. **Protection des Secrets**

- ✅ Secret key externalisée dans `.env`
- ✅ Configuration par environnement (dev/prod)
- ✅ `.env` ajouté au `.gitignore`

### 2. **Validation des Données**

- ✅ Formulaires avec Flask-WTF et validation CSRF
- ✅ Validation côté serveur (longueur, format, caractères dangereux)
- ✅ Protection contre les injections XSS et SQL

### 3. **Gestion d'Erreurs**

- ✅ Try/catch sur toutes les opérations SQLite
- ✅ Pages d'erreur 404 et 500 personnalisées
- ✅ Logging des erreurs pour le debugging

### 4. **Rate Limiting**

- ✅ Limitation globale : 200/jour, 50/heure
- ✅ Limitation formulaire : 5 soumissions/minute
- ✅ Protection contre le spam et les attaques

### 5. **Headers de Sécurité**

- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`

## ⚡ Optimisations de Performance

### 1. **Cache HTTP**

- ✅ Fichiers statiques : cache 1 an
- ✅ Pages dynamiques : cache 5 minutes
- ✅ Formulaires : pas de cache

### 2. **Base de Données**

- ✅ Index sur `status`, `categorie`, `date_ajout`
- ✅ Index composites pour requêtes complexes
- ✅ `ANALYZE` et `VACUUM` automatiques

### 3. **Structure du Code**

- ✅ Configuration centralisée (`config.py`)
- ✅ Formulaires séparés (`forms.py`)
- ✅ Fonctions utilitaires avec gestion d'erreurs

## 📁 Structure du Projet

```
reunion-wiki/
├── app.py              # Application principale
├── config.py           # Configuration par environnement
├── forms.py            # Formulaires avec validation
├── optimize_db.py      # Script d'optimisation BDD
├── requirements.txt    # Dépendances Python
├── .env               # Variables d'environnement (à créer)
├── base.db            # Base de données SQLite
├── templates/         # Templates Jinja2
│   ├── base.html
│   ├── formulaire.html # Formulaire sécurisé
│   └── 500.html       # Page d'erreur serveur
└── static/           # Fichiers statiques (CSS, JS, images)
```

## 🔄 Commandes Utiles

```bash
# Optimiser la base de données
python3 optimize_db.py

# Lancer en développement
FLASK_ENV=development python3 app.py

# Lancer en production (avec Redis conseillé pour le rate limit)
FLASK_ENV=production \
RATELIMIT_STORAGE_URL=redis://redis:6379/0 \
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Voir les logs en temps réel
tail -f app.log
```

## 🚨 Points d'Attention pour la Production

1. **Changer la SECRET_KEY** dans `.env`
2. **Configurer HTTPS** sur le serveur
3. **Sauvegarder la base** régulièrement
4. **Monitorer les logs** d'erreurs
5. **Tester le rate limiting** en conditions réelles

## 📊 Statistiques Actuelles

- **52 sites** au total
- **51 sites valides** affichés
- **8 catégories** disponibles
- **Base optimisée** avec 6 index

---

_Dernière mise à jour : Octobre 2024 - Améliorations sécurité et performance_
