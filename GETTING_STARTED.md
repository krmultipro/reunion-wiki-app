# 🚀 DÉMARRAGE RAPIDE - Réunion Wiki

> Guide ultra-simple pour démarrer en 5 minutes

---

## ⏱️ Installation en 5 minutes

```bash
# 1. Cloner le projet
git clone <URL_DU_REPO> reunion-wiki
cd reunion-wiki

# 2. Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env
cat > .env << 'EOF'
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_PATH=data/base.db
FLASK_ENV=development
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
MAIL_ENABLED=false
EOF

# 5. Lancer l'application
python app.py
```

**✅ C'est prêt ! Ouvre ton navigateur sur http://127.0.0.1:5000**

---

## 📖 Par où commencer ?

### Je veux juste voir le site
👉 Lance `python app.py` et va sur http://127.0.0.1:5000

### Je veux comprendre le projet
👉 Lis le **[GUIDE COMPLET](docs/GUIDE_COMPLET.md)**

### Je veux modifier quelque chose
👉 Consulte l'**[INDEX RAPIDE](docs/INDEX_RAPIDE.md)**

### J'ai besoin d'un aide-mémoire
👉 Garde l'**[AIDE-MÉMOIRE](docs/AIDE_MEMOIRE.md)** ouvert

---

## 🎯 3 choses à savoir

### 1. Architecture simple

```
Routes (HTTP) → Services (Logique) → Database (SQLite)
```

### 2. Où est quoi ?

```
app/routes/public.py    → Pages du site (/accueil, /recherche, etc.)
app/services/sites.py   → Logique des sites (recherche, CRUD, etc.)
app/templates/          → HTML (Jinja2)
app/static/style.css    → Styles CSS
```

### 3. Pour modifier une page

1. Template HTML → `app/templates/*.html`
2. Route (logique) → `app/routes/public.py`
3. Style CSS → `app/static/style.css`

---

## 🛠️ Commandes essentielles

```bash
# Démarrer l'app
python app.py

# Accéder à l'admin
# http://127.0.0.1:5000/admin
# Login : admin / admin123 (défini dans .env)

# Arrêter l'app
Ctrl + C

# Désactiver l'environnement virtuel
deactivate
```

---

## ❓ FAQ Rapide

### Q: Où sont les données ?
**R:** `data/base.db` (SQLite)

### Q: Comment modifier le CSS ?
**R:** Édite `app/static/style.css`

### Q: Comment ajouter une page ?
**R:** 
1. Crée `app/templates/ma_page.html`
2. Ajoute route dans `app/routes/public.py`

### Q: J'ai une erreur, que faire ?
**R:** Consulte [GUIDE_COMPLET.md#troubleshooting](docs/GUIDE_COMPLET.md#-troubleshooting)

### Q: Comment déployer en production ?
**R:** Consulte [GUIDE_COMPLET.md#déploiement](docs/GUIDE_COMPLET.md#-déploiement)

---

## 📚 Documentation complète

| Document | Utilité |
|----------|---------|
| **[GUIDE COMPLET](docs/GUIDE_COMPLET.md)** | Tout comprendre (⭐ commence ici) |
| **[INDEX RAPIDE](docs/INDEX_RAPIDE.md)** | Trouver rapidement |
| **[AIDE-MÉMOIRE](docs/AIDE_MEMOIRE.md)** | Cheat sheet |
| **[ARCHITECTURE VISUELLE](docs/ARCHITECTURE_VISUELLE.md)** | Schémas |

---

## ✅ Checklist premier lancement

- [ ] Python 3.10+ installé
- [ ] Environnement virtuel créé (`.venv`)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` créé avec SECRET_KEY
- [ ] App lancée (`python app.py`)
- [ ] Site accessible (http://127.0.0.1:5000)
- [ ] Admin accessible (http://127.0.0.1:5000/admin)

---

## 🆘 Aide

**Bloqué ?**  
👉 Lis le [GUIDE COMPLET](docs/GUIDE_COMPLET.md) - il répond à tout !

**Besoin d'une réponse rapide ?**  
👉 Consulte l'[INDEX RAPIDE](docs/INDEX_RAPIDE.md)

**Contact**  
📧 reunionwiki974@gmail.com

---

**🎉 Bienvenue sur Réunion Wiki ! Bon développement !**

