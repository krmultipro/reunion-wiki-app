````markdown
# 🌴 Réunion Wiki

Réunion Wiki, c’est un portail participatif pour retrouver rapidement les sites utiles de La Réunion:
emploi, démarches, santé, culture, transports, météo, actus, etc.

Objectif:

- rendre l’info locale plus simple d’accès;
- mettre en avant des ressources péi fiables;
- construire un annuaire utile avec les contributions des Réunionnais.

---

## ✨ Ce que fait le projet

- Annuaire de sites classés par catégories.
- Page “Sites les plus visités”.
- Page “Catégories les plus visitées”.
- Page “Tendances” (tops semaine/mois, catégories en hausse, nouveaux sites qui performent).
- Page “Derniers sites ajoutés”.
- Recherche globale (nom, catégorie, description, lien, ville).
- Villes gérées en base (`villes`) + pages par ville.
- Formulaire “Proposer un site” (accueil + page dédiée + pages catégories).
- Modération admin complète (`/admin`): valider, refuser, modifier, supprimer, créer.
- Suivi des clics (`site_clicks`) + vue admin des clics.
- SEO de base (title/description dynamiques, canonical, OG/Twitter).
- PWA (manifest + service worker).

---

## 🧱 Stack technique

- Backend: Python, Flask, Jinja2
- Formulaires/sécurité: Flask-WTF, WTForms, CSRF
- Limitation de trafic: Flask-Limiter (+ Redis en prod)
- Base de données: SQLite
- Déploiement prod: Docker + Docker Compose + Nginx + Gunicorn + Certbot

---

## 🗂️ Routes principales

- `/` : accueil
- `/recherche?q=...` : recherche
- `/categorie/<slug>` : catégorie
- `/sites-les-plus-visites` : top sites
- `/categories-les-plus-visitees` : top catégories
- `/sites-ajoutes-recemment` : derniers ajouts
- `/tendances` : tendances
- `/villes` : liste des villes
- `/ville/<slug>` : page d’une ville
- `/proposer-site` : formulaire complet
- `/go/<id>` : redirection + incrément clic
- `/admin` : dashboard modération

---

## 🛡️ Sécurité (résumé)

- CSRF actif sur les formulaires.
- Login admin + mot de passe hashé (`ADMIN_PASSWORD_HASH`).
- Limitation de débit sur endpoints sensibles.
- Validation serveur stricte des formulaires.
- Redirections de retour contrôlées (`next` / `return_to`).
- Logout admin en POST.
- Tracking clics avec anti-spam basique:
  - pas de double comptage même IP sur le même site pendant 30 min,
  - filtrage simple des user-agents bots.

---

## 🚀 Lancer en local

```bash
git clone <URL_DU_REPO> reunion-wiki-app
cd reunion-wiki-app

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# config
cp .env.example .env  # ou crée ton .env à la main

# run
python3 app.py
```
````

App dispo sur `http://127.0.0.1:5000`

---

## ⚙️ Variables `.env` utiles

```bash
FLASK_ENV=development
SECRET_KEY=change-me
DATABASE_PATH=data/base.db

ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=...

MAIL_ENABLED=false
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_DEFAULT_SENDER=...
MAIL_RECIPIENTS=...

RATELIMIT_STORAGE_URL=redis://redis:6379/0
RATELIMIT_DEFAULT=
LOG_LEVEL=WARNING
```

---

## 🔐 Générer un hash admin

```bash
./.venv/bin/python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('TON_MOT_DE_PASSE'))"
```

---

## 🐳 Déploiement prod (Docker)

```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```

Le conteneur web lance automatiquement:

- `python migrate.py`
- puis `gunicorn`

Donc les migrations sont appliquées au démarrage.

---

## 🗄️ Migration / base de données

`migrate.py` est idempotent et gère notamment:

- création/mise à jour des tables (`sites`, `site_clicks`, `categories`, `villes`);
- ajout des colonnes manquantes (`click_count`, `en_vedette`, `ville_id`);
- index SQLite;
- normalisation de la table `villes` (liste canonique);
- backfill de `sites.ville_id`.

---

## 💾 Backups

Le projet utilise un script de backup DB (prod) dans `script/backup_db.sh`.

Principe:

- backup de `/data/base.db` depuis le conteneur web,
- sortie dans `backups/`,
- compression `.gz`,
- rotation automatique (ex: 30 jours).

Exemple cron (VPS):

```cron
5 * * * * /var/www/reunion-wiki-app/script/backup_db.sh >> /var/www/reunion-wiki-app/logs/backup_db.log 2>&1
```

---

## 🤝 Workflow conseillé

- Travailler sur `dev`
- Tester
- Merge vers `main`
- Pull + redeploy sur VPS

---

## 📌 Notes

- Les dossiers runtime (`data/`, `backups/`, `logs/`, `certbot/`, `static/reports/`) ne sont pas faits pour être versionnés.
- Le projet évolue en continu: focus sur qualité data locale, UX mobile, sécurité admin, et valeur SEO.

---

## 🙌

Merci à toutes les personnes qui proposent des sites et font vivre l’écosystème local.
La Réunion lé la. 🌋

```

```
