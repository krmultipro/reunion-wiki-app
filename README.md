# 🌴 Réunion Wiki

Portail participatif qui recense les sites internet utiles de La Réunion : culture, emploi, services, météo, transports, etc. L’objectif est double :

- simplifier l’accès à l’information locale de qualité ;
- mettre en lumière des ressources péi parfois méconnues en s’appuyant sur les contributions des Réunionnais.

Le projet est développé et maintenu par Kery dans le cadre d’un déploiement VPS (OVH) et d’une alternance en conception/développement d’applications.

---

## ✨ Fonctionnalités clés

- Liste de catégories thématiques (Emploi & formation, Culture & loisirs, Nourriture, Transport, Météo & alertes, Actualités, Achats) + page “Nouveaux sites”.
- Carte “Proposer un site” sur l’accueil, les pages catégories et page dédiée, avec validation serveur, honeypot anti-bot et notification email.
- Accueil en carrousels (catégories, nouveautés) avec navigation tactile/flèches.
- Navigation mobile façon “ruban” scrollable, PWA installable (manifest + service worker réseau-first).
- SEO optimisé : métadonnées dynamiques, sitemap, robots.txt, FAQ, canonical par slug.
- Sécurité : CSRF, validation WTForms, rate limiting, headers de protection, configuration par environnement.
- Monitoring : logs Nginx/Gunicorn, GoAccess (statistiques publiques), sauvegardes cron, systemd service.
- Espace admin sécurisé (`/admin`) pour valider, modifier, publier ou supprimer les propositions directement sur la base de production.
- Recherche rapide (loupe en haut de page) sur nom, catégorie, description, ville et URL.
- Page contact dédiée (email, formulaire, réseaux) pour centraliser les échanges avec la communauté.
- Page blog avec sélections thématiques et conseils SEO-friendly.

Retrouve l’historique des versions dans [`CHANGELOG.md`](CHANGELOG.md).

---

## 🧱 Architecture

- **Backend** : Python 3, Flask, Jinja2, Flask-WTF, Flask-Limiter.
- **Base de données** : SQLite (index sur colonnes clés, script `optimize_db.py`).
- **Frontend** : HTML5, CSS3, JS léger (PWA, nav scrollable), aucun framework.
- **Notifications** : SMTP (msmtp côté VPS ou configuration Gmail via variables d’environnement).
- **Déploiement** : VPS OVH (Gunicorn + Nginx + Certbot), service systemd `reunionwiki`.
- **Monitoring & sécurité** : UFW, Fail2Ban, backups cron, accès SSH par clés.

---

## ✅ Prérequis

- Python 3.10+
- `pip` et `venv`
- SQLite 3 (inclus dans la plupart des distributions)
- Optionnel : Redis si tu veux utiliser un backend de rate limiting dédié

---

## 🚀 Installation locale

```bash
# 1. Cloner le projet
git clone <URL_DU_REPO> reunion-wiki
cd reunion-wiki

# 2. Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copier l'exemple de configuration (à créer au besoin)
cp script/.env.sample .env  # adapter les valeurs

# 5. Initialiser/optimiser la base (facultatif en dev)
python3 optimize_db.py

# 6. Lancer le serveur Flask
python3 app.py
```

L’application écoute sur `http://127.0.0.1:5000`. Pour stopper : `Ctrl+C`, puis `deactivate`.

---

## ⚙️ Configuration `.env`

Créer un fichier `.env` à la racine (non versionné). Exemple minimal :

```bash
SECRET_KEY=change-me
DATABASE_PATH=base.db
FLASK_ENV=development

# Notifications email (désactivées par défaut)
MAIL_ENABLED=false
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=reunionwiki974@gmail.com
MAIL_PASSWORD=motdepasse_application
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_DEFAULT_SENDER=reunionwiki974@gmail.com
MAIL_RECIPIENTS=reunionwiki974@gmail.com

# Rate limiting (flask-limiter)
RATELIMIT_DEFAULT=200 per day, 50 per hour
# RATELIMIT_STORAGE_URL=redis://localhost:6379/0  # optionnel

# Compte de modération (/admin)
ADMIN_USERNAME=mon-admin
ADMIN_PASSWORD=motdepassefort
# ou utilisez un hash sécurisé et commentez ADMIN_PASSWORD :
# ADMIN_PASSWORD_HASH=pbkdf2:sha256:...
```

Les variables sont chargées automatiquement par `config.py`. Ne jamais commiter `.env`.

---

## 🛡️ Interface admin & modération
- URL : `/admin` (formulaire de connexion `/admin/login`, déconnexion `/admin/logout`).
- Les identifiants sont lus dans l’environnement (`ADMIN_USERNAME` + `ADMIN_PASSWORD` **ou** `ADMIN_PASSWORD_HASH`).
- Pour générer un hash sécurisé :
  ```bash
  python3 - <<'PY'
  from werkzeug.security import generate_password_hash
  print(generate_password_hash("motdepassefort"))
  PY
  ```
  Copie le résultat dans `ADMIN_PASSWORD_HASH` et supprime `ADMIN_PASSWORD`.
- Une fois connecté, tu peux filtrer par statut, rechercher par mot-clé, modifier, publier un nouveau site ou supprimer des propositions ; la mise à jour est faite directement dans `base.db` (celle du VPS).
- Chaque action est journalisée dans les logs Gunicorn (`journalctl -u reunionwiki -f`).

---

## 🧪 Validation rapide

- `python3 -m compileall app.py forms.py config.py optimize_db.py`  
  (permet de détecter des erreurs de syntaxe avant push)
- Tests manuels : navigation, soumission du formulaire, vérification des mails (si activés).

---

## 🛠️ Commandes utiles

```bash
# Optimiser la base (index, ANALYZE, VACUUM)
python3 optimize_db.py

# Lancer l'app en mode développement (auto reload via Flask)
FLASK_ENV=development python3 app.py

# Lancer via Gunicorn (local)
gunicorn -w 4 -b 127.0.0.1:8000 app:app

# Regarder les logs Gunicorn (stdout/stderr)
journalctl -u reunionwiki -f

# Sur le VPS : redémarrer le service
sudo systemctl restart reunionwiki

# Exporter la table `sites` (CSV horodaté)
python3 script/export_sites.py \
  --database /var/www/reunion-wiki-app/base.db \
  --output-dir /home/reunionwiki/exports
```

---

## 🚀 Déploiement OVH (workflow recommandé)

1. **Développer/tester localement**, pousser sur GitHub/Gitea.
2. Sur le VPS :
   ```bash
   cd /var/www
   sudo mv reunion-wiki-app reunion-wiki-app.bak.$(date +%Y%m%d)
   git clone <URL_DU_REPO> reunion-wiki-app
   ```
3. Copier les fichiers sensibles depuis l’ancienne version (`.env`, `base.db`, uploads, etc.).
4. Vérifier les permissions (`sudo chown -R reunionwiki:reunionwiki /var/www/reunion-wiki-app`).
5. Redémarrer Gunicorn via systemd :
   ```bash
   sudo systemctl restart reunionwiki
   sudo systemctl status reunionwiki
   ```
6. Regarder les logs (`journalctl -u reunionwiki -f`) et Nginx (`/var/log/nginx/reunionwiki_access.log`).

> ℹ️ Un script `update_from_github.sh` peut être utilisé s’il travaille sur un clone git valide. Toujours tester en staging avant de toucher la prod.

---

## 🔐 Sécurité & bonnes pratiques

- Validation serveur stricte (WTForms + filtres custom) et champ honeypot.
- CSRF sur tous les formulaires, rate limiting global et par endpoint.
- Headers HTTP durcis (`X-Frame-Options`, `X-Content-Type-Options`, etc.).
- Auth SMTP via mots de passe d’application (Gmail) ; pas de mot de passe en clair dans le code.
- Service worker en mode réseau-first pour éviter les pages obsolètes.
- Sauvegardes automatiques via cron (`/root/backup_reunionwiki.sh`) vers `/home/reunionwiki/`.
- Accès SSH uniquement par clé, port personnalisé, Fail2Ban actif.

---

## 📈 Observabilité

- Tableau GoAccess public : `http://reunionwiki.re/static/report.html`
- Logs applicatifs : `journalctl -u reunionwiki`
- Logs Nginx : `/var/log/nginx/reunionwiki_access.log` (trafic) et `_error.log`
- Notifications système par msmtp (liées au compte Gmail).

---

## 🤝 Contribution & roadmap

- Travail sur branches, PR revues avant merge.
- Idées prioritaires : carousel avec visuels, moteur de recherche + tris, interface admin de modération, statistiques par site, système d’avis/commentaires, logo officiel.
- Toute nouvelle feature doit respecter :
  1. pas de styles inline (tout dans `static/style.css`);
  2. pas d’accents/emoji dans les commandes bash pour éviter les soucis d’encodage ;
  3. tests locaux avant déploiement (et `python3 -m compileall`).

---

## 📜 Changelog & licence

- Historique détaillé : voir [`CHANGELOG.md`](CHANGELOG.md).
- Licence : privée (usage interne au projet Réunion Wiki). Contacte `reunionwiki974@gmail.com` pour toute demande.

---

## 🙌 Remerciements

Le projet est né grâce à la communauté réunionnaise très active sur les réseaux et soutenu par la formation ExperNet / EDF Réunion.  
Lancement officiel : 10 juin 2024.
