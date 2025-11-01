# Guide de développement – Réunion Wiki

Ce guide détaille les conventions, bonnes pratiques et workflows de développement pour le projet Réunion Wiki.

---

## 📋 Table des matières

1. [Environnement de développement](#environnement-de-développement)
2. [Architecture du code](#architecture-du-code)
3. [Conventions de code](#conventions-de-code)
4. [Workflow Git](#workflow-git)
5. [Tests](#tests)
6. [Déploiement](#déploiement)

---

## 🛠️ Environnement de développement

### Prérequis

- **Python** : 3.10 ou supérieur
- **pip** : Gestionnaire de paquets Python
- **venv** : Pour créer un environnement virtuel
- **Git** : Contrôle de version
- **SQLite** : Base de données (incluse dans Python)

### Configuration initiale

```bash
# 1. Cloner le projet
git clone <URL_DU_REPO> reunion-wiki
cd reunion-wiki

# 2. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Créer le fichier .env (copier depuis l'exemple si disponible)
cp docs/.env.example .env
# Éditer .env avec tes configurations

# 5. Initialiser la base de données
python3 scripts/init_db.py

# 6. Lancer l'application en développement
python3 app.py
```

L'application sera accessible sur `http://127.0.0.1:5000`

---

## 🏗️ Architecture du code

### Structure modulaire en couches

Le projet suit une architecture en couches pour séparer les responsabilités :

```
┌─────────────────────────────────────┐
│         Routes (HTTP)               │  ← Gestion HTTP uniquement
│    app/routes/public.py             │
│    app/routes/admin.py              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Services (Logique métier)      │  ← Toute la logique métier
│    app/services/sites.py            │
│    app/services/talents.py          │
│    app/services/auth.py             │
│    app/services/emails.py           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Database (Abstraction)         │  ← Context managers DB
│    app/database.py                  │
│    - db_transaction()               │
│    - db_query()                     │
└─────────────────────────────────────┘
```

### Règles d'architecture

1. **Routes (`app/routes/`)** :
   - ❌ Ne JAMAIS mettre de requêtes SQL directement
   - ❌ Ne JAMAIS mettre de logique métier complexe
   - ✅ Appeler les fonctions des services
   - ✅ Gérer uniquement HTTP (request, response, redirect, flash)

2. **Services (`app/services/`)** :
   - ✅ Toute la logique métier
   - ✅ Toutes les requêtes SQL
   - ✅ Utiliser les context managers DB (`db_transaction`, `db_query`)
   - ✅ Retourner des tuples `(success: bool, message: str)` pour les opérations

3. **Database (`app/database.py`)** :
   - ✅ Context managers pour transactions sécurisées
   - ✅ Gestion automatique des erreurs et rollbacks
   - ✅ Fermeture automatique des connexions

### Exemple de bonne pratique

#### ❌ AVANT (mauvaise pratique)

```python
# Dans app/routes/public.py
@public_bp.route("/categorie/<slug>")
def voir_categorie(slug: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sites WHERE categorie = ?", (slug,))
    sites = cur.fetchall()
    conn.close()
    return render_template("categorie.html", sites=sites)
```

#### ✅ APRÈS (bonne pratique)

```python
# Dans app/services/sites.py
def get_sites_by_category(categorie: str) -> List[sqlite3.Row]:
    """Return all validated sites for a given category."""
    try:
        with db_query() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM sites WHERE categorie = ? AND status = 'valide'",
                (categorie,),
            )
            return cur.fetchall()
    except DatabaseError:
        return []

# Dans app/routes/public.py
@public_bp.route("/categorie/<slug>")
def voir_categorie(slug: str):
    sites = get_sites_by_category(nom_categorie)
    return render_template("categorie.html", sites=sites)
```

---

## 📝 Conventions de code

### Style Python

- Suivre **PEP 8** pour le style de code
- Utiliser des **type hints** partout où c'est possible
- Limiter les lignes à **88 caractères** (Black recommandé)

### Nomenclature

- **Fichiers** : `snake_case.py`
- **Classes** : `PascalCase`
- **Fonctions/variables** : `snake_case`
- **Constantes** : `UPPER_SNAKE_CASE`

### Documentation

- **Docstrings** : Utiliser le format Google pour toutes les fonctions publiques
- **Commentaires** : Expliquer le **pourquoi**, pas le **quoi**

```python
def submit_site_proposal(
    nom: str, lien: str, description: str, categorie: str, ville: Optional[str] = None
) -> Tuple[bool, str]:
    """Submit a new site proposal.
    
    Args:
        nom: Nom du site
        lien: URL du site
        description: Description du site
        categorie: Catégorie du site
        ville: Ville (optionnelle)
        
    Returns:
        Tuple contenant (success, message) où:
        - success: True si la proposition a été enregistrée
        - message: Message de retour pour l'utilisateur
    """
```

### Gestion d'erreurs

- Utiliser les **context managers** pour les transactions DB
- Lever `DatabaseError` pour les erreurs de base de données
- Logger les erreurs avec `current_app.logger.error()`
- Retourner des messages clairs à l'utilisateur

```python
try:
    with db_transaction() as conn:
        # Opération DB
        pass
except DatabaseError as exc:
    current_app.logger.error(f"Erreur lors de l'insertion: {exc}")
    return False, "Erreur lors de l'enregistrement."
```

---

## 🌿 Workflow Git

### Branches

- `main` : Branche de production (toujours stable)
- `develop` : Branche de développement
- `feature/nom-feature` : Nouvelles fonctionnalités
- `fix/nom-bug` : Corrections de bugs
- `refactor/nom-refactor` : Refactorisations

### Commit messages

Format : `type: description courte`

Types :
- `feat:` : Nouvelle fonctionnalité
- `fix:` : Correction de bug
- `refactor:` : Refactorisation
- `docs:` : Documentation
- `style:` : Formatage
- `test:` : Tests

Exemples :
```
feat: Ajout de la recherche par ville
fix: Correction de l'erreur 500 sur les catégories
refactor: Extraction des requêtes SQL vers services
docs: Mise à jour du README
```

### Pull Requests

1. Créer une branche depuis `develop`
2. Développer la fonctionnalité
3. Tester localement
4. Vérifier avec `python3 -m compileall app config.py`
5. Créer une PR avec description détaillée
6. Attendre la revue avant merge

---

## 🧪 Tests

### Structure des tests

Les tests sont dans `tests/`. Actuellement, seul `test_routes.py` existe.

### Lancer les tests

```bash
# Tester la syntaxe Python
python3 -m compileall app config.py optimize_db.py

# Lancer les tests (quand ils seront écrits)
python3 -m pytest tests/
```

### Écrire des tests

```python
# tests/test_services.py
import pytest
from app.services.sites import get_categories, submit_site_proposal

def test_get_categories():
    categories = get_categories()
    assert isinstance(categories, list)
    assert len(categories) > 0
```

**À faire** : Compléter la suite de tests pour les services.

---

## 🚀 Déploiement

### Pré-déploiement

Avant de déployer, vérifier :

1. ✅ Tests passent
2. ✅ Syntaxe Python valide : `python3 -m compileall app config.py`
3. ✅ Variables d'environnement configurées (`.env`)
4. ✅ Base de données optimisée : `python3 optimize_db.py`

### Déploiement sur VPS

Voir la section "Déploiement OVH" dans le `README.md` principal.

### Post-déploiement

```bash
# Vérifier les logs
journalctl -u reunionwiki -f

# Vérifier le statut
sudo systemctl status reunionwiki

# Tester l'application
curl http://localhost:8000
```

---

## 📚 Ressources

- **Documentation Flask** : https://flask.palletsprojects.com/
- **PEP 8** : https://pep8.org/
- **Type hints** : https://docs.python.org/3/library/typing.html
- **Architecture** : Voir `docs/ANALYSE_MODULARITE.md`

---

## 🆘 Dépannage

### Problème : Module non trouvé

```bash
# Vérifier que l'environnement virtuel est activé
which python3  # Doit pointer vers .venv/bin/python3

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : Erreur de base de données

```bash
# Vérifier que la base existe
ls -lh data/base.db

# Réinitialiser la base (ATTENTION : perte de données)
python3 scripts/init_db.py
```

### Problème : Port déjà utilisé

```bash
# Trouver le processus utilisant le port 5000
lsof -i :5000

# Tuer le processus si nécessaire
kill -9 <PID>
```

---

## 💡 Bonnes pratiques supplémentaires

1. **Ne jamais commiter** :
   - Fichiers `.env`
   - Bases de données (`*.db`)
   - Dossiers `__pycache__/`

2. **Toujours** :
   - Tester localement avant de push
   - Vérifier la syntaxe Python
   - Documenter les nouvelles fonctions
   - Utiliser les services au lieu de SQL direct dans les routes

3. **Code review** :
   - Vérifier la séparation des responsabilités
   - S'assurer que les services sont utilisés
   - Valider la gestion d'erreurs

---

Pour toute question, consulter la documentation principale ou ouvrir une issue.

