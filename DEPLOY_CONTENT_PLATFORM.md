# Déploiement — Plateforme de contenu SEO

Procédure à suivre une seule fois lors du premier déploiement en production.

---

## 1. Backup avant migration

```bash
cp data_prod/base.db data_prod/base.db.bak-$(date +%Y%m%d)
```

---

## 2. Créer les dossiers requis

```bash
# Dossier uploads production dans /data
mkdir -p data_prod/uploads

# L'UID 1000 correspond à appuser dans l'image python:3.10-slim
chown 1000:1000 data_prod data_prod/uploads
chmod 755 data_prod data_prod/uploads
```

> Sans ce `chown`, Flask (appuser) ne peut pas écrire dans le dossier → uploads silencieusement refusés.

---

## 3. Migration base de données

La migration est lancée automatiquement au démarrage du conteneur (`CMD sh -c "python migrate.py && gunicorn ..."`).  
Pour la lancer manuellement avant le rebuild :

```bash
DATABASE_PATH=data_prod/base.db python migrate.py
```

Vérifie que la table `content` est créée :

```bash
sqlite3 data_prod/base.db ".tables" | grep content
# attendu : content
```

---

## 4. Rebuild et redémarrage

```bash
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 5. Vérification post-déploiement

```bash
# Logs au démarrage
docker compose -f docker-compose.prod.yml logs web --tail=30

# Sitemap dynamique (doit retourner XML valide)
curl -s https://reunion.wiki/sitemap.xml | head -5

# Page admin content accessible (doit rediriger vers /admin/login si non connecté)
curl -I https://reunion.wiki/admin/content
```

---

## Rollback

Si la migration échoue ou le site plante :

```bash
docker compose -f docker-compose.prod.yml down
cp data_prod/base.db.bak-<date> data_prod/base.db
git revert HEAD  # ou git checkout <commit-précédent>
docker compose -f docker-compose.prod.yml up -d
```
