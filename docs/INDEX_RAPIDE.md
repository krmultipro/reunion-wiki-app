# 🔍 INDEX RAPIDE - Réunion Wiki

> Guide de navigation rapide dans la documentation et le code

---

## 🎯 Tu cherches quoi ?

### "Je veux comprendre le projet"
👉 **[GUIDE_COMPLET.md](GUIDE_COMPLET.md)** - Commence ici !

### "Je veux modifier une page"
👉 **[GUIDE_COMPLET.md#comment-modifier](GUIDE_COMPLET.md#-comment-modifierajouter-des-fonctionnalités)** - Section "Comment modifier"

### "J'ai une erreur"
👉 **[GUIDE_COMPLET.md#troubleshooting](GUIDE_COMPLET.md#-troubleshooting)** - Section Troubleshooting

### "Je veux déployer"
👉 **[GUIDE_COMPLET.md#déploiement](GUIDE_COMPLET.md#-déploiement)** - Section Déploiement

### "Je cherche une fonction précise"
👉 **[API_SERVICES.md](API_SERVICES.md)** - Documentation API complète

---

## 📁 Où se trouve...

### Routes (URLs de l'application)

| Je veux modifier... | Fichier à éditer |
|---------------------|------------------|
| Page d'accueil | `app/routes/public.py` → `accueil()` |
| Page catégorie | `app/routes/public.py` → `voir_categorie()` |
| Formulaire de proposition | `app/routes/public.py` → `formulaire()` |
| Recherche | `app/routes/public.py` → `search()` |
| Page talents | `app/routes/public.py` → `talents()` |
| Dashboard admin | `app/routes/admin.py` → `dashboard()` |
| Login admin | `app/routes/admin.py` → `login()` |

### Templates (Apparence)

| Je veux modifier... | Fichier à éditer |
|---------------------|------------------|
| Structure commune (header, footer) | `app/templates/base.html` |
| Page d'accueil | `app/templates/index.html` |
| Page catégorie | `app/templates/categorie.html` |
| Formulaire proposition | `app/templates/formulaire.html` |
| Page recherche | `app/templates/search.html` |
| Page talents | `app/templates/talents.html` |
| Dashboard admin | `app/templates/admin/dashboard.html` |

### Styles (CSS)

| Je veux modifier... | Fichier à éditer |
|---------------------|------------------|
| Styles personnalisés | `app/static/style.css` |
| Bootstrap | `app/static/bootstrap/css/bootstrap.min.css` (ne pas modifier) |
| Polices | `app/static/fonts.css` |

### Logique métier (Services)

| Fonctionnalité | Fichier |
|----------------|---------|
| Gestion des sites (CRUD, recherche) | `app/services/sites.py` |
| Gestion des talents | `app/services/talents.py` |
| Envoi d'emails | `app/services/emails.py` |
| Authentification admin | `app/services/auth.py` |

### Formulaires (Validation)

| Formulaire | Fichier | Classe |
|------------|---------|--------|
| Proposition de site | `app/forms.py` | `SiteForm` |
| Proposition de talent | `app/forms.py` | `TalentProposalForm` |
| Login admin | `app/forms.py` | `AdminLoginForm` |
| Édition admin talent | `app/forms.py` | `TalentAdminForm` |

### Configuration

| Type de config | Fichier |
|----------------|---------|
| Variables d'environnement (SECRET_KEY, etc.) | `.env` |
| Configuration Flask (dev/prod) | `config.py` |
| Extensions (rate limiter, etc.) | `app/extensions.py` |

---

## 🔧 Tâches courantes

### Ajouter une nouvelle page

1. Créer le template : `app/templates/ma_page.html`
2. Ajouter la route : `app/routes/public.py`
3. Ajouter le lien dans : `app/templates/base.html` (navigation)

**Voir détails** → [GUIDE_COMPLET.md#ajouter-une-nouvelle-page](GUIDE_COMPLET.md#ajouter-une-nouvelle-page-publique)

### Modifier un formulaire

1. Modifier la classe : `app/forms.py`
2. Modifier la route : `app/routes/public.py`
3. Modifier le template : `app/templates/*.html`
4. Modifier la BDD si besoin : `data/base.db`
5. Modifier le service : `app/services/*.py`

**Voir détails** → [GUIDE_COMPLET.md#ajouter-un-nouveau-champ](GUIDE_COMPLET.md#ajouter-un-nouveau-champ-dans-un-formulaire)

### Modifier le style

1. Éditer : `app/static/style.css`
2. Si nécessaire, vider cache : `Ctrl + Shift + R`

### Débugger une erreur

1. Regarder les logs : `journalctl -u reunionwiki -f` (production)
2. Ou en local : Terminal où tourne `python app.py`
3. Consulter : [GUIDE_COMPLET.md#troubleshooting](GUIDE_COMPLET.md#-troubleshooting)

### Déployer une mise à jour

1. **Local** : Tester avec `python app.py`
2. **Git** : `git add .` → `git commit -m "..."` → `git push`
3. **VPS** : Se connecter en SSH
4. **VPS** : Sauvegarder ancienne version
5. **VPS** : `git clone` nouvelle version
6. **VPS** : Restaurer `.env` et `data/`
7. **VPS** : `sudo systemctl restart reunionwiki`
8. **VPS** : Vérifier logs

**Voir détails** → [GUIDE_COMPLET.md#déploiement](GUIDE_COMPLET.md#-déploiement)

---

## 🐛 Erreurs fréquentes

| Erreur | Voir section |
|--------|--------------|
| "SECRET_KEY doit être défini" | [GUIDE_COMPLET.md#secret-key](GUIDE_COMPLET.md#problème--lapplication-ne-démarre-pas) |
| "502 Bad Gateway" | [GUIDE_COMPLET.md#502](GUIDE_COMPLET.md#problème--erreur-502-bad-gateway-nginx) |
| "Database is locked" | [GUIDE_COMPLET.md#database-locked](GUIDE_COMPLET.md#problème--base-de-données-verrouillée) |
| "429 Too Many Requests" | [GUIDE_COMPLET.md#rate-limiting](GUIDE_COMPLET.md#problème--rate-limiting-trop-strict) |
| "Les emails ne partent pas" | [GUIDE_COMPLET.md#emails](GUIDE_COMPLET.md#problème--les-emails-ne-senvoient-pas) |
| "CSS ne se met pas à jour" | [GUIDE_COMPLET.md#cache](GUIDE_COMPLET.md#problème--les-modifications-cssjs-ne-saffichent-pas) |

---

## 📚 Documentation par sujet

### Architecture
- **Vue d'ensemble** → [GUIDE_COMPLET.md#architecture](GUIDE_COMPLET.md#-architecture-du-projet)
- **Analyse détaillée** → [ANALYSE_MODULARITE.md](ANALYSE_MODULARITE.md)
- **Structure fichiers** → [GUIDE_COMPLET.md#structure](GUIDE_COMPLET.md#-structure-des-fichiers-détaillée)

### Sécurité
- **Résumé** → [GUIDE_COMPLET.md#sécurité](GUIDE_COMPLET.md#-sécurité)
- **Audit complet** → Voir logs conversation (11 nov 2025)

### Développement
- **Guide complet** → [GUIDE_COMPLET.md](GUIDE_COMPLET.md)
- **Conventions** → [GUIDE_DEVELOPPEMENT.md](GUIDE_DEVELOPPEMENT.md)
- **API** → [API_SERVICES.md](API_SERVICES.md)

### Production
- **Déploiement** → [GUIDE_COMPLET.md#déploiement](GUIDE_COMPLET.md#-déploiement)
- **Statut** → [STATUS_PRODUCTION.md](STATUS_PRODUCTION.md)
- **Maintenance** → [GUIDE_COMPLET.md#maintenance](GUIDE_COMPLET.md#-maintenance)

### SEO
- **Documentation** → [SEO_ACTUEL.md](SEO_ACTUEL.md)

---

## 🎓 Par niveau

### Débutant (je découvre le projet)
1. 📖 **[GUIDE_COMPLET.md](GUIDE_COMPLET.md)** - Lis tout !
2. 📝 [GUIDE_DEVELOPPEMENT.md](GUIDE_DEVELOPPEMENT.md) - Conventions
3. 📚 [API_SERVICES.md](API_SERVICES.md) - Fonctions disponibles

### Intermédiaire (je veux modifier)
1. 📖 [GUIDE_COMPLET.md#modifier](GUIDE_COMPLET.md#-comment-modifierajouter-des-fonctionnalités) - Comment modifier
2. 📊 [ANALYSE_MODULARITE.md](ANALYSE_MODULARITE.md) - Architecture
3. 📝 [API_SERVICES.md](API_SERVICES.md) - API complète

### Avancé (je veux optimiser/déployer)
1. 📖 [GUIDE_COMPLET.md#déploiement](GUIDE_COMPLET.md#-déploiement) - Déploiement
2. 📖 [GUIDE_COMPLET.md#maintenance](GUIDE_COMPLET.md#-maintenance) - Maintenance
3. 📊 [STATUS_PRODUCTION.md](STATUS_PRODUCTION.md) - Production

---

## 🔗 Liens rapides

### En local
- Application : http://127.0.0.1:5000
- Admin : http://127.0.0.1:5000/admin

### En production
- Site : https://reunionwiki.re
- Admin : https://reunionwiki.re/admin
- Stats : https://reunionwiki.re/static/report.html

### Commandes fréquentes

```bash
# Démarrer en local
python app.py

# Redémarrer en production
sudo systemctl restart reunionwiki

# Voir les logs
sudo journalctl -u reunionwiki -f

# Backup de la base
python scripts/backup_base.py

# Optimiser la base
python optimize_db.py
```

---

## ✅ Checklist rapide avant modification

- [ ] J'ai lu le [GUIDE_COMPLET.md](GUIDE_COMPLET.md)
- [ ] Je sais quel fichier modifier (voir tableaux ci-dessus)
- [ ] J'ai créé une branche Git (`git checkout -b ma-feature`)
- [ ] J'ai testé en local (`python app.py`)
- [ ] Pas d'erreurs (`python -m compileall app`)
- [ ] J'ai commit (`git commit -m "Description"`)

---

**🎯 RAPPEL : En cas de doute, commence toujours par [GUIDE_COMPLET.md](GUIDE_COMPLET.md) !**

---

*Dernière mise à jour : 11 novembre 2025*

