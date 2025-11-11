# 📖 GUIDE COMPLET RÉUNION WIKI

> **Guide de référence complet pour comprendre et maintenir le projet Réunion Wiki**  
> Dernière mise à jour : 11 novembre 2025

---

## 📚 TABLE DES MATIÈRES

1. [Vue d'ensemble](#-vue-densemble)
2. [Architecture du projet](#-architecture-du-projet)
3. [Structure des fichiers détaillée](#-structure-des-fichiers-détaillée)
4. [Comment ça fonctionne ?](#-comment-ça-fonctionne-)
5. [Flux de données](#-flux-de-données)
6. [Sécurité](#-sécurité)
7. [Comment modifier/ajouter des fonctionnalités](#-comment-modifierajouter-des-fonctionnalités)
8. [Déploiement](#-déploiement)
9. [Maintenance](#-maintenance)
10. [Troubleshooting](#-troubleshooting)

---

## 🎯 Vue d'ensemble

**Réunion Wiki** est une application web Flask qui permet de :
- Référencer des sites web utiles de La Réunion
- Permettre aux utilisateurs de proposer des sites
- Gérer les propositions via une interface admin
- Afficher les sites par catégories
- Offrir une recherche rapide

### Technologies utilisées

```
Backend :  Python 3.10+ + Flask 3.1
Database : SQLite3
Frontend : HTML5 + CSS3 + JavaScript vanilla
Déploiement : Gunicorn + Nginx + systemd
```

---

## 🏗 Architecture du projet

### Principe : Architecture en couches

Le projet suit une **architecture en 3 couches** pour séparer les responsabilités :

```
┌─────────────────────────────────────┐
│   COUCHE PRÉSENTATION (Routes)     │ ← Gère les requêtes HTTP
│   app/routes/*.py                   │
├─────────────────────────────────────┤
│   COUCHE MÉTIER (Services)          │ ← Logique business
│   app/services/*.py                 │
├─────────────────────────────────────┤
│   COUCHE DONNÉES (Database)         │ ← Accès base de données
│   app/database.py                   │
└─────────────────────────────────────┘
```

### Pourquoi cette architecture ?

✅ **Séparation des responsabilités** : Chaque couche a un rôle précis  
✅ **Testabilité** : On peut tester chaque couche séparément  
✅ **Maintenabilité** : Facile de modifier une partie sans casser le reste  
✅ **Réutilisabilité** : Les services peuvent être utilisés par plusieurs routes

---

## 📂 Structure des fichiers détaillée

### Vue d'ensemble

```
reunionwiki/
├── app/                      # 🎯 Code de l'application
│   ├── __init__.py          # Factory Flask (point d'entrée)
│   ├── routes/              # 🌐 Routes HTTP (ce que l'utilisateur voit)
│   ├── services/            # 🔧 Logique métier (traitement des données)
│   ├── templates/           # 📄 Pages HTML (Jinja2)
│   ├── static/              # 🎨 CSS, JS, images
│   └── utils/               # 🛠 Outils helper
├── data/                     # 💾 Base de données SQLite
├── docs/                     # 📚 Documentation
├── scripts/                  # 🤖 Scripts utilitaires
├── config.py                 # ⚙️ Configuration centralisée
└── app.py                    # 🚀 Point de démarrage
```

### Détail fichier par fichier

#### 📁 Racine du projet

| Fichier | Rôle | Quand le modifier ? |
|---------|------|---------------------|
| `app.py` | Point d'entrée pour lancer l'app | Jamais (sauf changement majeur) |
| `config.py` | Configuration dev/prod | Ajouter nouvelles variables d'env |
| `requirements.txt` | Dépendances Python | Après install de nouveaux packages |
| `.env` | Variables secrètes | Config locale/production |

#### 📁 app/ (Cœur de l'application)

| Fichier | Rôle | Modifier pour... |
|---------|------|-----------------|
| `__init__.py` | Factory Flask, enregistre tout | Ajouter nouveaux blueprints/extensions |
| `database.py` | Connexion SQLite + context managers | Jamais (sauf bug) |
| `extensions.py` | Extensions (rate limiter) | Ajouter nouvelles extensions |
| `filters.py` | Filtres Jinja (ex: dates) | Ajouter filtres templates |
| `forms.py` | Formulaires WTForms | Ajouter/modifier formulaires |
| `hooks.py` | Hooks globaux (headers) | Ajouter headers de sécurité |
| `errors.py` | Pages erreur 404/500 | Modifier pages d'erreur |

#### 📁 app/routes/ (Routes HTTP)

| Fichier | Contient | URLs gérées |
|---------|----------|-------------|
| `public.py` | Routes publiques | `/`, `/categorie/<slug>`, `/recherche`, `/formulaire`, `/talents`, etc. |
| `admin.py` | Routes admin | `/admin`, `/admin/login`, `/admin/propositions`, `/admin/talents` |

**🔑 Règle d'or** : Les routes doivent être **FINES** - elles ne font que :
1. Recevoir la requête HTTP
2. Valider les données (formulaire)
3. Appeler un service
4. Retourner une réponse

❌ **Ne jamais faire dans une route :**
- Requêtes SQL directes
- Logique métier complexe
- Calculs

✅ **Tout cela va dans les services !**

#### 📁 app/services/ (Logique métier)

| Fichier | Responsable de... | Fonctions principales |
|---------|-------------------|----------------------|
| `sites.py` | Gestion des sites web | `get_admin_sites()`, `search_sites()`, `submit_site_proposal()`, `update_site_status()` |
| `talents.py` | Gestion des talents Instagram | `get_talents_data()`, `create_talent_proposal()`, `update_talent_status()` |
| `emails.py` | Envoi d'emails | `send_submission_notification()` |
| `auth.py` | Authentification admin | `verify_admin_credentials()`, `admin_required()` |

**🔑 Règle d'or** : Les services contiennent :
- TOUTES les requêtes SQL
- La logique métier
- Les validations business

#### 📁 app/templates/ (HTML)

```
templates/
├── base.html              # Template parent (structure commune)
├── index.html             # Page d'accueil
├── categorie.html         # Page catégorie
├── search.html            # Page recherche
├── formulaire.html        # Formulaire proposition site
├── talents.html           # Page talents
├── admin/                 # Templates admin
│   ├── dashboard.html     # Dashboard modération
│   ├── edit_site.html     # Édition site
│   └── edit_talent.html   # Édition talent
└── emails/                # Templates emails
    └── new_submission.txt # Email notification
```

**Héritage des templates :**

```
base.html (structure)
    ↓
index.html (contenu spécifique)
```

#### 📁 app/static/ (Assets)

```
static/
├── style.css              # Styles personnalisés
├── fonts.css              # Polices
├── bootstrap/             # Bootstrap 5
├── icons/                 # Icônes PWA
├── talents/               # Photos talents
├── service-worker.js      # PWA
├── manifest.webmanifest   # PWA manifest
├── sitemap.xml            # SEO
└── robots.txt             # SEO
```

#### 📁 data/ (Base de données)

```
data/
├── base.db               # Base SQLite principale
└── backups/              # Sauvegardes automatiques
    ├── base_backup_2025-05-12_16-27-58.db
    └── base_backup_2025-06-20_20-25-17.db
```

**⚠️ IMPORTANT** : `base.db` n'est **JAMAIS** versionné sur Git !

---

## ⚙️ Comment ça fonctionne ?

### 1. Démarrage de l'application

```
1. app.py est exécuté
     ↓
2. app/__init__.py → create_app()
     ↓
3. Chargement config (config.py)
     ↓
4. Initialisation extensions (limiter, etc.)
     ↓
5. Enregistrement blueprints (routes)
     ↓
6. Application prête à recevoir des requêtes !
```

### 2. Traitement d'une requête (exemple : recherche)

```
Utilisateur tape dans la barre de recherche "météo"
     ↓
1. Navigateur → GET /recherche?q=météo
     ↓
2. Flask → app/routes/public.py → search()
     ↓
3. Route valide et limite la requête ([:100])
     ↓
4. Route appelle → services/sites.py → search_sites("météo")
     ↓
5. Service fait requête SQL (LIKE %météo%)
     ↓
6. Service retourne les résultats
     ↓
7. Route passe à template → search.html
     ↓
8. Jinja2 génère HTML final
     ↓
9. Flask envoie HTML au navigateur
```

### 3. Soumission d'un formulaire (exemple : proposer un site)

```
Utilisateur remplit formulaire sur /formulaire
     ↓
1. POST /formulaire
     ↓
2. Flask → public.py → formulaire()
     ↓
3. WTForms valide les données (forms.py → SiteForm)
   - Vérification CSRF token ✅
   - Validation longueur ✅
   - Sanitization HTML ✅
   - Vérification honeypot ✅
     ↓
4. Si valide → services/sites.py → submit_site_proposal()
     ↓
5. Service insère en base avec status='en_attente'
     ↓
6. Service retourne (True, "Message succès")
     ↓
7. Route envoie email via services/emails.py
     ↓
8. Route affiche message flash "Proposition envoyée !"
     ↓
9. Redirection vers page d'accueil
```

### 4. Connexion admin

```
Admin va sur /admin
     ↓
1. Middleware vérifie session (auth.py → @admin_required)
     ↓
2. Si pas connecté → redirect /admin/login
     ↓
3. Admin entre identifiants
     ↓
4. POST /admin/login
     ↓
5. services/auth.py → verify_admin_credentials()
   - Compare username (timing-safe) ✅
   - Vérifie password hash ✅
     ↓
6. Si OK → session["admin_authenticated"] = True
     ↓
7. Redirect vers /admin (dashboard)
```

---

## 🔄 Flux de données

### Base de données SQLite

**Structure des tables principales :**

#### Table `sites`

```sql
CREATE TABLE sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,              -- Nom du site
    ville TEXT,                     -- Ville (optionnel)
    lien TEXT NOT NULL,             -- URL
    description TEXT NOT NULL,      -- Description
    categorie TEXT NOT NULL,        -- Catégorie
    status TEXT DEFAULT 'en_attente', -- en_attente|valide|refuse
    en_vedette INTEGER DEFAULT 0,  -- 1 si en vedette
    display_order INTEGER DEFAULT 0, -- Ordre d'affichage
    date_ajout TEXT NOT NULL        -- Date d'ajout
);
```

#### Table `talents`

```sql
CREATE TABLE talents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pseudo TEXT NOT NULL,           -- Pseudo Instagram
    instagram TEXT NOT NULL,        -- Lien Instagram
    description TEXT NOT NULL,      -- Description
    category TEXT,                  -- Catégorie
    image TEXT,                     -- Chemin image
    status TEXT DEFAULT 'en_attente', -- en_attente|valide|refuse
    display_order INTEGER DEFAULT 0,
    date_created TEXT NOT NULL,
    date_updated TEXT NOT NULL
);
```

### Cycle de vie d'une proposition de site

```
1. [en_attente] ← Utilisateur soumet via /formulaire
        ↓
2. Admin se connecte sur /admin
        ↓
3. Admin voit la proposition dans dashboard
        ↓
4. Admin clique "Approuver" ou "Refuser"
        ↓
5. [valide] → Site visible sur le site public
   OU
   [refuse] → Site masqué mais conservé en base
```

---

## 🛡 Sécurité

### Protections mises en place

#### 1. Protection contre les injections SQL

**❌ Mauvais (vulnérable) :**
```python
query = f"SELECT * FROM sites WHERE nom = '{user_input}'"
```

**✅ Bon (sécurisé) :**
```python
cur.execute("SELECT * FROM sites WHERE nom = ?", (user_input,))
```

👉 **Utilisé partout** dans `services/sites.py` et `services/talents.py`

#### 2. Protection XSS (Cross-Site Scripting)

**3 niveaux de protection :**

1. **Sanitization formulaires** (`forms.py`)
   ```python
   filters=[_sanitize_basic]  # Supprime HTML
   ```

2. **Validation stricte**
   ```python
   if re.search(r'<script|javascript:|on\w+\s*=', field.data):
       raise ValidationError(...)
   ```

3. **Auto-escape Jinja2**
   ```html
   {{ site.nom }}  <!-- Automatiquement échappé -->
   ```

#### 3. Protection CSRF

```python
# forms.py
class SiteForm(FlaskForm):
    # FlaskForm ajoute automatiquement un token CSRF
    ...

# Template
{{ form.hidden_tag() }}  <!-- Inclut le token CSRF -->
```

#### 4. Rate Limiting

```python
# Limite les tentatives de connexion admin
@limiter.limit("5 per minute")
def login():
    ...

# Limite les soumissions de formulaires
@limiter.limit("5 per hour")
def formulaire():
    ...
```

#### 5. Honeypot anti-bot

```python
# forms.py
honeypot = StringField('Ne pas remplir ce champ')

def validate_honeypot(self, field):
    if field.data:  # Si un bot a rempli le champ
        raise ValidationError("Formulaire invalide.")
```

#### 6. Headers de sécurité

```python
# hooks.py
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'DENY'
response.headers['X-XSS-Protection'] = '1; mode=block'
```

#### 7. Authentification admin sécurisée

```python
# Timing-safe comparison (évite timing attacks)
secrets.compare_digest(username, stored_username)

# Password hashing (Werkzeug)
check_password_hash(stored_hash, password)
```

#### 8. Validation des longueurs

```python
# Toutes les entrées utilisateur sont limitées
query = request.args.get("q", "").strip()[:100]
category = request.args.get("category", "").strip()[:50]
```

### Configuration sécurisée

#### Variables d'environnement (.env)

```bash
# JAMAIS en clair dans le code !
SECRET_KEY=your-secret-key-here-use-strong-random-value
ADMIN_PASSWORD_HASH=pbkdf2:sha256:...

# ⚠️ En production, SECRET_KEY est OBLIGATOIRE
```

**Génération d'une SECRET_KEY forte :**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Génération d'un password hash :**

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("votre-mot-de-passe"))
```

---

## 🔧 Comment modifier/ajouter des fonctionnalités

### Ajouter une nouvelle page publique

**Exemple : Ajouter une page "À propos"**

#### Étape 1 : Créer le template

```html
<!-- app/templates/a_propos.html -->
{% extends "base.html" %}

{% block seo_title %}À propos - Réunion Wiki{% endblock %}

{% block content %}
<section>
    <h1>À propos de Réunion Wiki</h1>
    <p>Contenu de la page...</p>
</section>
{% endblock %}
```

#### Étape 2 : Ajouter la route

```python
# app/routes/public.py

@public_bp.route("/a-propos")
def a_propos():
    return render_template("a_propos.html")
```

#### Étape 3 : Ajouter dans la navigation

```html
<!-- app/templates/base.html -->
<nav>
    <a href="{{ url_for('public.accueil') }}">Accueil</a>
    <a href="{{ url_for('public.a_propos') }}">À propos</a>
</nav>
```

C'est tout ! ✅

### Ajouter un nouveau champ dans un formulaire

**Exemple : Ajouter un champ "Email" dans le formulaire de proposition**

#### Étape 1 : Modifier la base de données

```python
# Manuellement dans SQLite ou via script
ALTER TABLE sites ADD COLUMN email TEXT;
```

#### Étape 2 : Ajouter le champ dans le formulaire

```python
# app/forms.py

class SiteForm(FlaskForm):
    nom = StringField(...)
    lien = StringField(...)
    # NOUVEAU
    email = StringField(
        'Email de contact',
        [
            Optional(),
            Email(message="Email invalide"),
            Length(max=100)
        ],
        filters=[_sanitize_basic]
    )
    ...
```

#### Étape 3 : Mettre à jour le service

```python
# app/services/sites.py

def submit_site_proposal(nom, lien, description, categorie, ville, email):
    ...
    cur.execute(
        """
        INSERT INTO sites (nom, lien, description, categorie, ville, email, status, date_ajout)
        VALUES (?, ?, ?, ?, ?, ?, 'en_attente', DATETIME('now'))
        """,
        (nom, lien, description, categorie, ville, email)
    )
    ...
```

#### Étape 4 : Mettre à jour la route

```python
# app/routes/public.py

if form.validate_on_submit():
    success, message = submit_site_proposal(
        nom=form.nom.data,
        lien=form.lien.data,
        description=form.description.data,
        categorie=form.categorie.data,
        ville=form.ville.data or None,
        email=form.email.data or None,  # NOUVEAU
    )
```

#### Étape 5 : Ajouter dans le template

```html
<!-- app/templates/formulaire.html -->

<div class="form-field">
    {{ form.email.label(class="form-label") }}
    {{ form.email(class="form-input", placeholder="contact@example.com") }}
    {% if form.email.errors %}
        <div class="form-errors">...</div>
    {% endif %}
</div>
```

### Ajouter une nouvelle fonctionnalité de recherche

**Exemple : Recherche avancée avec filtres**

#### Étape 1 : Créer la fonction dans le service

```python
# app/services/sites.py

def search_sites_advanced(query, category=None, ville=None, limit=30):
    """Recherche avancée avec filtres."""
    try:
        with db_query() as conn:
            cur = conn.cursor()
            
            sql = """
                SELECT * FROM sites
                WHERE status = 'valide'
                AND nom LIKE ? COLLATE NOCASE
            """
            params = [f"%{query}%"]
            
            if category:
                sql += " AND categorie = ?"
                params.append(category)
            
            if ville:
                sql += " AND ville = ?"
                params.append(ville)
            
            sql += " ORDER BY date_ajout DESC LIMIT ?"
            params.append(limit)
            
            cur.execute(sql, tuple(params))
            return cur.fetchall()
    except DatabaseError:
        return []
```

#### Étape 2 : Ajouter la route

```python
# app/routes/public.py

@public_bp.route("/recherche-avancee")
@limiter.limit("30 per minute")
def search_advanced():
    query = request.args.get("q", "").strip()[:100]
    category = request.args.get("category", "").strip()[:100]
    ville = request.args.get("ville", "").strip()[:100]
    
    results = []
    if query and len(query) >= 2:
        results = search_sites_advanced(
            query=query,
            category=category or None,
            ville=ville or None
        )
    
    return render_template(
        "search_advanced.html",
        query=query,
        category=category,
        ville=ville,
        results=results
    )
```

#### Étape 3 : Créer le template

```html
<!-- app/templates/search_advanced.html -->
{% extends "base.html" %}

{% block content %}
<form method="get">
    <input type="text" name="q" value="{{ query }}" placeholder="Rechercher...">
    <select name="category">
        <option value="">Toutes catégories</option>
        {% for cat in categories %}
        <option value="{{ cat }}" {% if cat == category %}selected{% endif %}>
            {{ cat }}
        </option>
        {% endfor %}
    </select>
    <input type="text" name="ville" value="{{ ville }}" placeholder="Ville">
    <button type="submit">Rechercher</button>
</form>

{% for site in results %}
    <article>...</article>
{% endfor %}
{% endblock %}
```

---

## 🚀 Déploiement

### En local (développement)

```bash
# 1. Activer l'environnement virtuel
source .venv/bin/activate

# 2. Définir l'environnement
export FLASK_ENV=development

# 3. Lancer l'application
python app.py

# L'app tourne sur http://127.0.0.1:5000
```

### Sur le VPS (production)

#### Configuration systemd

```ini
# /etc/systemd/system/reunionwiki.service

[Unit]
Description=Réunion Wiki Application
After=network.target

[Service]
Type=notify
User=reunionwiki
Group=reunionwiki
WorkingDirectory=/var/www/reunion-wiki-app
Environment="PATH=/var/www/reunion-wiki-app/.venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/var/www/reunion-wiki-app/.venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/reunion-wiki-app/reunionwiki.sock \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Configuration Nginx

```nginx
# /etc/nginx/sites-available/reunionwiki

server {
    listen 80;
    server_name reunionwiki.re www.reunionwiki.re;
    
    location / {
        proxy_pass http://unix:/var/www/reunion-wiki-app/reunionwiki.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/reunion-wiki-app/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Workflow de déploiement

```bash
# 1. Sur ta machine locale : pousser sur Git
git add .
git commit -m "Nouvelle fonctionnalité"
git push origin main

# 2. Sur le VPS : se connecter
ssh reunionwiki@ton-serveur.com

# 3. Sauvegarder l'ancienne version
cd /var/www
sudo mv reunion-wiki-app reunion-wiki-app.bak.$(date +%Y%m%d)

# 4. Cloner la nouvelle version
sudo git clone https://github.com/ton-repo/reunion-wiki.git reunion-wiki-app

# 5. Restaurer les fichiers sensibles
sudo cp reunion-wiki-app.bak.*/.env reunion-wiki-app/
sudo cp -r reunion-wiki-app.bak.*/data reunion-wiki-app/

# 6. Installer les dépendances
cd reunion-wiki-app
sudo -u reunionwiki python3 -m venv .venv
sudo -u reunionwiki .venv/bin/pip install -r requirements.txt

# 7. Corriger les permissions
sudo chown -R reunionwiki:reunionwiki /var/www/reunion-wiki-app

# 8. Redémarrer le service
sudo systemctl restart reunionwiki

# 9. Vérifier le statut
sudo systemctl status reunionwiki

# 10. Regarder les logs
sudo journalctl -u reunionwiki -f
```

---

## 🔧 Maintenance

### Sauvegardes automatiques

**Script de backup** (`scripts/backup_base.py`) :

```python
import sqlite3
from datetime import datetime
from pathlib import Path

def backup_database():
    source = Path("data/base.db")
    backup_dir = Path("data/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destination = backup_dir / f"base_backup_{timestamp}.db"
    
    # Copie avec SQLite
    source_conn = sqlite3.connect(source)
    backup_conn = sqlite3.connect(destination)
    source_conn.backup(backup_conn)
    source_conn.close()
    backup_conn.close()
    
    print(f"✅ Backup créé : {destination}")

if __name__ == "__main__":
    backup_database()
```

**Cron job** (sur le VPS) :

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne pour backup quotidien à 3h du matin
0 3 * * * /var/www/reunion-wiki-app/.venv/bin/python /var/www/reunion-wiki-app/scripts/backup_base.py
```

### Optimisation de la base

```bash
# Lancer l'optimisation
python optimize_db.py
```

Ce script :
- ✅ Créé les index manquants
- ✅ Exécute ANALYZE (optimise le query planner)
- ✅ Exécute VACUUM (récupère l'espace)

### Monitoring des logs

```bash
# Logs de l'application
sudo journalctl -u reunionwiki -f

# Logs Nginx (accès)
sudo tail -f /var/log/nginx/reunionwiki_access.log

# Logs Nginx (erreurs)
sudo tail -f /var/log/nginx/reunionwiki_error.log

# Statistiques avec GoAccess
goaccess /var/log/nginx/reunionwiki_access.log \
    -o /var/www/reunion-wiki-app/app/static/report.html \
    --log-format=COMBINED
```

### Nettoyage des anciennes propositions

```python
# Script à créer : scripts/cleanup_old_refused.py

import sqlite3
from datetime import datetime, timedelta

def cleanup_old_refused(days=90):
    """Supprime les propositions refusées de plus de X jours."""
    conn = sqlite3.connect("data/base.db")
    cur = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    cur.execute(
        "DELETE FROM sites WHERE status = 'refuse' AND date_ajout < ?",
        (cutoff_date,)
    )
    
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ {deleted} propositions refusées supprimées")

if __name__ == "__main__":
    cleanup_old_refused()
```

---

## 🔍 Troubleshooting

### Problème : L'application ne démarre pas

#### Symptômes
```
ERROR: SECRET_KEY doit être défini en production !
```

#### Solution
```bash
# Vérifier que .env existe
cat .env | grep SECRET_KEY

# Si absent, générer une clé
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

---

### Problème : Erreur 502 Bad Gateway (Nginx)

#### Symptômes
- Nginx affiche "502 Bad Gateway"
- Le site est inaccessible

#### Diagnostic
```bash
# 1. Vérifier que Gunicorn tourne
sudo systemctl status reunionwiki

# 2. Vérifier les logs
sudo journalctl -u reunionwiki -n 50
```

#### Solutions possibles

**Si Gunicorn est arrêté :**
```bash
sudo systemctl start reunionwiki
```

**Si erreur de dépendances :**
```bash
cd /var/www/reunion-wiki-app
sudo -u reunionwiki .venv/bin/pip install -r requirements.txt
sudo systemctl restart reunionwiki
```

**Si problème de permissions :**
```bash
sudo chown -R reunionwiki:reunionwiki /var/www/reunion-wiki-app
sudo systemctl restart reunionwiki
```

---

### Problème : Base de données verrouillée

#### Symptômes
```
DatabaseError: database is locked
```

#### Causes
- Plusieurs processus accèdent à SQLite simultanément
- Transaction non fermée

#### Solutions

**Temporaire :**
```bash
# Redémarrer l'application
sudo systemctl restart reunionwiki
```

**Permanent (si récurrent) :**

Passer à PostgreSQL ou MySQL pour la production. SQLite n'est pas optimal pour haute concurrence.

---

### Problème : Rate limiting trop strict

#### Symptômes
```
429 Too Many Requests
```

#### Solution temporaire (développement)

```python
# config.py - DevelopmentConfig

RATELIMIT_ENABLED = False  # Désactive complètement
```

#### Solution permanente (production)

Ajuster les limites dans les routes :

```python
# app/routes/public.py

@limiter.limit("30 per minute")  # Au lieu de 5
def formulaire():
    ...
```

---

### Problème : Les emails ne s'envoient pas

#### Diagnostic

```bash
# Vérifier la config
cat .env | grep MAIL

# Tester l'envoi depuis Python
python3 - <<'PY'
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content("Test")
msg["Subject"] = "Test"
msg["From"] = "reunionwiki974@gmail.com"
msg["To"] = "destinataire@example.com"

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login("reunionwiki974@gmail.com", "mot-de-passe-app")
        smtp.send_message(msg)
    print("✅ Email envoyé")
except Exception as e:
    print(f"❌ Erreur : {e}")
PY
```

#### Solutions

**Erreur d'authentification Gmail :**
- Utiliser un "mot de passe d'application" (pas le mot de passe Gmail normal)
- Activer l'authentification à 2 facteurs sur Gmail
- Générer un mot de passe d'application : https://myaccount.google.com/apppasswords

---

### Problème : Les modifications CSS/JS ne s'affichent pas

#### Causes
- Cache navigateur
- Cache Nginx

#### Solutions

```bash
# 1. Vider cache navigateur
Ctrl + Shift + R (ou Cmd + Shift + R sur Mac)

# 2. Sur le serveur, forcer Nginx à recharger
sudo nginx -s reload

# 3. Ajouter un versioning des assets
# Dans base.html :
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}?v=2">
```

---

## 📚 Ressources supplémentaires

### Documentation officielle

- [Flask](https://flask.palletsprojects.com/)
- [Flask-WTF](https://flask-wtf.readthedocs.io/)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [SQLite](https://www.sqlite.org/docs.html)

### Fichiers de documentation du projet

- `docs/API_SERVICES.md` - Documentation complète des fonctions
- `docs/ANALYSE_MODULARITE.md` - Architecture détaillée
- `docs/GUIDE_DEVELOPPEMENT.md` - Conventions de code
- `docs/CHANGELOG.md` - Historique des versions

---

## ✅ Checklist avant modification

Avant de modifier le code, vérifie :

- [ ] J'ai lu la section concernée dans ce guide
- [ ] Je comprends où se situe le fichier à modifier
- [ ] J'ai créé une branche Git (`git checkout -b ma-feature`)
- [ ] J'ai testé en local avant de pousser
- [ ] J'ai vérifié qu'il n'y a pas d'erreurs (`python -m compileall app`)
- [ ] J'ai mis à jour la documentation si nécessaire
- [ ] J'ai fait un commit clair (`git commit -m "Description"`)

---

## 🎯 Récapitulatif : Les 10 règles d'or

1. **Séparer les responsabilités** : Routes → Services → Database
2. **Jamais de SQL dans les routes** : Tout dans les services
3. **Toujours valider les entrées** : WTForms + sanitization
4. **Toujours paramétrer les requêtes SQL** : `execute("SELECT * WHERE id = ?", (id,))`
5. **Logger les actions importantes** : `current_app.logger.info(...)`
6. **Limiter les longueurs** : `[:100]` sur tous les inputs
7. **Ne jamais commiter .env** : Ajouter dans .gitignore
8. **Tester en local avant déploiement** : `python app.py`
9. **Faire des backups réguliers** : Automatiser avec cron
10. **Documenter les changements** : Mettre à jour CHANGELOG.md

---

**🎉 Félicitations ! Tu as maintenant toutes les clés pour maîtriser ton projet Réunion Wiki !**

**Des questions ? Consulte les autres documents dans `docs/` ou crée une issue sur le dépôt Git.**

---

*Dernière mise à jour : 11 novembre 2025*  
*Maintenu par : Kery (reunionwiki974@gmail.com)*

