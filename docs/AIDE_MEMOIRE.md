# 📝 AIDE-MÉMOIRE RÉUNION WIKI

> Cheat sheet : Toutes les commandes et concepts essentiels sur une page

---

## 🚀 Commandes essentielles

### Développement local

```bash
# Démarrer l'application
python app.py                           # http://127.0.0.1:5000

# Avec auto-reload Flask
FLASK_ENV=development python app.py

# Vérifier la syntaxe
python -m compileall app

# Optimiser la base
python optimize_db.py

# Backup manuel
python scripts/backup_base.py
```

### Production (VPS)

```bash
# SSH vers le serveur
ssh reunionwiki@ton-serveur.com

# Redémarrer l'application
sudo systemctl restart reunionwiki
sudo systemctl status reunionwiki

# Voir les logs en temps réel
sudo journalctl -u reunionwiki -f

# Logs Nginx
sudo tail -f /var/log/nginx/reunionwiki_access.log
sudo tail -f /var/log/nginx/reunionwiki_error.log

# Recharger Nginx (après modif config)
sudo nginx -t                           # Tester config
sudo nginx -s reload                    # Recharger

# Permissions
sudo chown -R reunionwiki:reunionwiki /var/www/reunion-wiki-app
```

### Git

```bash
# Workflow standard
git checkout -b ma-feature              # Nouvelle branche
git add .                               # Ajouter les fichiers
git commit -m "Description claire"      # Commit
git push origin ma-feature              # Push

# Retour à main
git checkout main
git pull origin main

# Voir l'état
git status
git log --oneline -10                   # 10 derniers commits
```

---

## 📂 Structure rapide

```
app/
├── __init__.py          # Factory Flask
├── routes/
│   ├── public.py       # Routes publiques (/, /recherche, etc.)
│   └── admin.py        # Routes admin (/admin/*)
├── services/
│   ├── sites.py        # Logique sites (CRUD, recherche)
│   ├── talents.py      # Logique talents
│   ├── emails.py       # Envoi emails
│   └── auth.py         # Authentification
├── templates/          # HTML (Jinja2)
├── static/             # CSS, JS, images
├── forms.py            # Formulaires WTForms
├── database.py         # Connexion SQLite
└── config.py           # Configuration
```

---

## 🔄 Flux de requête

```
Utilisateur → Route → Service → Database
            ↓         ↓          ↓
          Valide  Logique    Requête SQL
                     ↓
                  Template ← Données
                     ↓
                  HTML → Utilisateur
```

---

## 🛡 Sécurité : Les 5 règles

1. **SQL** : TOUJOURS paramétrer
   ```python
   ❌ f"SELECT * FROM sites WHERE id={id}"
   ✅ cur.execute("SELECT * FROM sites WHERE id = ?", (id,))
   ```

2. **Inputs** : TOUJOURS limiter
   ```python
   ❌ query = request.args.get("q")
   ✅ query = request.args.get("q", "").strip()[:100]
   ```

3. **Formulaires** : TOUJOURS valider (WTForms)
   ```python
   if form.validate_on_submit():  # ← CSRF + validation
       ...
   ```

4. **Routes sensibles** : TOUJOURS rate-limiter
   ```python
   @limiter.limit("5 per minute")
   def login():
       ...
   ```

5. **Secrets** : JAMAIS dans le code
   ```python
   ❌ SECRET_KEY = "ma-clé-secrète"
   ✅ SECRET_KEY = os.getenv('SECRET_KEY')  # Dans .env
   ```

---

## 📝 Base de données

### Tables principales

```sql
-- Sites web
sites (
    id, nom, ville, lien, description,
    categorie, status, display_order, date_ajout
)

-- Talents Instagram
talents (
    id, pseudo, instagram, description,
    category, image, status, display_order
)
```

### Statuts

- `en_attente` : Proposition en attente de validation
- `valide` : Visible sur le site
- `refuse` : Refusé (masqué)

### Context managers

```python
# Transaction (INSERT, UPDATE, DELETE)
with db_transaction() as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO ...")
    # commit automatique

# Lecture (SELECT)
with db_query() as conn:
    cur = conn.cursor()
    cur.execute("SELECT ...")
    return cur.fetchall()
```

---

## 🎨 Templates (Jinja2)

### Syntaxe de base

```html
{# Commentaire #}

{{ variable }}                  <!-- Affiche et échappe -->
{{ variable|safe }}             <!-- Pas d'échappement -->

{% if condition %}
    ...
{% elif autre %}
    ...
{% else %}
    ...
{% endif %}

{% for item in liste %}
    {{ item.nom }}
{% endfor %}

{% extends "base.html" %}       <!-- Hérite de base.html -->

{% block content %}             <!-- Remplace ce block -->
    ...
{% endblock %}

{{ url_for('public.accueil') }} <!-- Génère URL -->
```

### Filtres courants

```html
{{ date|format_date }}          <!-- Filtre personnalisé -->
{{ text|length }}               <!-- Longueur -->
{{ text|upper }}                <!-- Majuscules -->
{{ text|lower }}                <!-- Minuscules -->
{{ number|round(2) }}           <!-- Arrondi -->
```

---

## 🔧 Configuration (.env)

```bash
# OBLIGATOIRE en production
SECRET_KEY=your-secret-key-here-64-chars-minimum

# Base de données
DATABASE_PATH=data/base.db

# Environnement
FLASK_ENV=production  # ou development

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=pbkdf2:sha256:...

# Email (optionnel)
MAIL_ENABLED=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=reunionwiki974@gmail.com
MAIL_PASSWORD=mot-de-passe-app
MAIL_USE_TLS=true
MAIL_RECIPIENTS=reunionwiki974@gmail.com

# Rate limiting
RATELIMIT_DEFAULT=200 per day, 50 per hour
```

### Générer une clé secrète

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Générer un hash de mot de passe

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("ton-mot-de-passe"))
```

---

## 🐛 Debugging rapide

### Erreur : "SECRET_KEY doit être défini"

```bash
# Vérifier .env
cat .env | grep SECRET_KEY

# Si absent
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

### Erreur : 502 Bad Gateway

```bash
# Vérifier Gunicorn
sudo systemctl status reunionwiki

# Redémarrer
sudo systemctl restart reunionwiki

# Logs
sudo journalctl -u reunionwiki -f
```

### Erreur : Database locked

```bash
# Redémarrer l'app
sudo systemctl restart reunionwiki
```

### Erreur : 429 Too Many Requests

```python
# Dans la route concernée, augmenter la limite
@limiter.limit("30 per minute")  # Au lieu de 5
```

### CSS ne se met pas à jour

```
1. Vider cache navigateur : Ctrl + Shift + R
2. Sur serveur : sudo nginx -s reload
3. Ajouter versioning : style.css?v=2
```

---

## 📊 Logs et monitoring

### Voir les logs

```bash
# Logs app (stdout/stderr)
sudo journalctl -u reunionwiki -f

# Logs Nginx (accès)
sudo tail -f /var/log/nginx/reunionwiki_access.log

# Logs Nginx (erreurs)
sudo tail -f /var/log/nginx/reunionwiki_error.log

# Filtrer logs app par niveau
sudo journalctl -u reunionwiki -p err    # Erreurs seulement
sudo journalctl -u reunionwiki -p warning # Warnings+
```

### Statistiques avec GoAccess

```bash
goaccess /var/log/nginx/reunionwiki_access.log \
    -o /var/www/reunion-wiki-app/app/static/report.html \
    --log-format=COMBINED
```

---

## 🔄 Workflow de développement

### 1. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### 2. Développer en local

```bash
# Activer venv
source .venv/bin/activate

# Lancer l'app
python app.py

# Tester dans le navigateur
# http://127.0.0.1:5000
```

### 3. Tester

```bash
# Vérifier la syntaxe
python -m compileall app

# Test manuel dans le navigateur
# ✅ Formulaires
# ✅ Navigation
# ✅ Recherche
# ✅ Admin
```

### 4. Commit et push

```bash
git add .
git commit -m "feat: Ajout de la fonctionnalité X"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 5. Déployer

```bash
# Sur le VPS
cd /var/www
sudo mv reunion-wiki-app reunion-wiki-app.bak.$(date +%Y%m%d)
sudo git clone <URL> reunion-wiki-app
sudo cp reunion-wiki-app.bak.*/.env reunion-wiki-app/
sudo cp -r reunion-wiki-app.bak.*/data reunion-wiki-app/
sudo chown -R reunionwiki:reunionwiki reunion-wiki-app
sudo systemctl restart reunionwiki
sudo journalctl -u reunionwiki -f  # Vérifier
```

---

## 🎯 Raccourcis utiles

### Ajouter une page

1. Template : `app/templates/ma_page.html`
2. Route : `app/routes/public.py` → `@public_bp.route("/ma-page")`
3. Lien : `app/templates/base.html` → navigation

### Ajouter un champ formulaire

1. Forme : `app/forms.py` → Ajouter le champ
2. Route : `app/routes/*.py` → Passer `form.champ.data`
3. Service : `app/services/*.py` → Ajouter param
4. BDD : ALTER TABLE si nécessaire
5. Template : `app/templates/*.html` → Afficher

### Modifier le style

1. Éditer : `app/static/style.css`
2. Commit : `git commit -m "style: ..."`
3. Deploy : Push + redémarrer Nginx

---

## 📚 Documentation

| Document | Pour... |
|----------|---------|
| **[GUIDE_COMPLET.md](GUIDE_COMPLET.md)** | **Tout comprendre** |
| [INDEX_RAPIDE.md](INDEX_RAPIDE.md) | Trouver rapidement |
| [API_SERVICES.md](API_SERVICES.md) | API des fonctions |
| [GUIDE_DEVELOPPEMENT.md](GUIDE_DEVELOPPEMENT.md) | Conventions |

---

## ✅ Checklist quotidienne

### Avant de coder

- [ ] `git pull origin main`
- [ ] `git checkout -b feature/...`
- [ ] `source .venv/bin/activate`

### Avant de commit

- [ ] Tester en local (`python app.py`)
- [ ] Vérifier syntaxe (`python -m compileall app`)
- [ ] Commit clair (`git commit -m "..."`)

### Avant de déployer

- [ ] Push sur Git
- [ ] Backup BDD production
- [ ] Redémarrer service
- [ ] Vérifier logs

---

## 🆘 Aide rapide

### "Je suis perdu"
👉 Lis [GUIDE_COMPLET.md](GUIDE_COMPLET.md)

### "Où est le fichier X ?"
👉 Consulte [INDEX_RAPIDE.md](INDEX_RAPIDE.md)

### "J'ai une erreur"
👉 Section debugging ci-dessus + [GUIDE_COMPLET.md#troubleshooting](GUIDE_COMPLET.md#-troubleshooting)

### "Comment faire X ?"
👉 [GUIDE_COMPLET.md#comment-modifier](GUIDE_COMPLET.md#-comment-modifierajouter-des-fonctionnalités)

---

**🎯 Ce document est ton ami ! Garde-le ouvert quand tu codes.**

*Dernière mise à jour : 11 novembre 2025*

