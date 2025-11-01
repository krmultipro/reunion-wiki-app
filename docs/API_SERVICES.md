# API des Services – Réunion Wiki

Documentation des fonctions de service utilisables dans le projet. Ces fonctions encapsulent toute la logique métier et l'accès à la base de données.

---

## 📦 Services disponibles

- [`services/sites.py`](#services-sites) : Gestion des sites
- [`services/talents.py`](#services-talents) : Gestion des talents
- [`services/auth.py`](#services-auth) : Authentification admin
- [`services/emails.py`](#services-emails) : Notifications email

---

## 🗄️ Database (`app/database.py`)

### Context Managers

#### `db_transaction()`

Context manager pour les transactions avec commit automatique.

```python
from app.database import db_transaction

with db_transaction() as conn:
    cur = conn.cursor()
    cur.execute("INSERT INTO sites ...")
    # Le commit est automatique en cas de succès
    # Le rollback est automatique en cas d'erreur
```

**Raises** : `DatabaseError` si la connexion échoue ou en cas d'erreur SQLite

#### `db_query()`

Context manager pour les requêtes en lecture seule.

```python
from app.database import db_query

with db_query() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM sites ...")
    results = cur.fetchall()
    # Fermeture automatique
```

**Raises** : `DatabaseError` si la connexion échoue ou en cas d'erreur SQLite

---

## 📍 Services Sites (`app/services/sites.py`)

### Récupération de données

#### `get_categories() -> List[str]`

Retourne la liste des catégories qui ont au moins un site validé.

```python
from app.services.sites import get_categories

categories = get_categories()
# Retourne : ['Emploi & formation', 'Culture & loisirs', ...]
```

#### `get_categories_slug() -> Dict[str, str]`

Retourne un mapping entre noms de catégories et leurs slugs.

```python
from app.services.sites import get_categories_slug

mapping = get_categories_slug()
# Retourne : {'Emploi & formation': 'emploi-formation', ...}
```

#### `get_sites_by_category(categorie: str) -> List[sqlite3.Row]`

Récupère tous les sites validés d'une catégorie.

```python
from app.services.sites import get_sites_by_category

sites = get_sites_by_category("Emploi & formation")
# Retourne une liste de Row SQLite avec les sites validés
```

#### `get_all_validated_sites() -> List[sqlite3.Row]`

Récupère tous les sites validés, ordonnés par date.

```python
from app.services.sites import get_all_validated_sites

sites = get_all_validated_sites()
```

#### `get_sites_en_vedette(limit: int = 3) -> Dict[str, List[sqlite3.Row]]`

Récupère les derniers sites validés par catégorie (pour la page d'accueil).

```python
from app.services.sites import get_sites_en_vedette

data = get_sites_en_vedette(limit=3)
# Retourne : {'Emploi & formation': [site1, site2, ...], ...}
```

#### `get_derniers_sites_global(limit: int = 3) -> Sequence[sqlite3.Row]`

Récupère les N derniers sites validés toutes catégories confondues.

```python
from app.services.sites import get_derniers_sites_global

derniers = get_derniers_sites_global(limit=12)
```

#### `search_sites(query: str, limit: int = 100) -> List[sqlite3.Row]`

Recherche des sites par mot-clé (nom, catégorie, description, ville, lien).

```python
from app.services.sites import search_sites

results = search_sites("emploi", limit=50)
# Retourne les sites contenant "emploi" dans les champs recherchés
```

**Note** : Retourne une liste vide si `query` fait moins de 2 caractères.

### Opérations CRUD

#### `submit_site_proposal(nom: str, lien: str, description: str, categorie: str, ville: Optional[str] = None) -> Tuple[bool, str]`

Soumet une nouvelle proposition de site (statut : `en_attente`).

```python
from app.services.sites import submit_site_proposal

success, message = submit_site_proposal(
    nom="Exemple Site",
    lien="https://example.com",
    description="Un super site",
    categorie="Emploi & formation",
    ville="Saint-Denis"  # Optionnel
)
if success:
    print(message)  # "Merci, ta proposition a bien été envoyée..."
```

**Returns** : `(bool, str)` - (succès, message utilisateur)

#### `get_admin_sites(status_filter: str = "en_attente", search_query: str = "") -> Dict[str, any]`

Récupère les sites pour le dashboard admin avec filtres.

```python
from app.services.sites import get_admin_sites

data = get_admin_sites(
    status_filter="en_attente",  # ou "valide", "refuse", "tout"
    search_query="emploi"
)
# Retourne : {'entries': [site1, site2, ...], 'stats': {...}}
```

**Returns** : `Dict` avec `entries` (liste de sites) et `stats` (statistiques par statut)

#### `get_site_by_id(site_id: int) -> Optional[sqlite3.Row]`

Récupère un site par son ID.

```python
from app.services.sites import get_site_by_id

site = get_site_by_id(123)
if site:
    print(site["nom"])
```

#### `update_site_status(site_id: int, status: str) -> Tuple[bool, str]`

Met à jour le statut d'un site (`valide` ou `refuse`).

```python
from app.services.sites import update_site_status

success, message = update_site_status(123, "valide")
```

#### `delete_site(site_id: int) -> Tuple[bool, str]`

Supprime un site de la base de données.

```python
from app.services.sites import delete_site

success, message = delete_site(123)
```

#### `update_site_full(site_id: int, nom: str, ville: Optional[str], lien: str, description: str, categorie: str, status: str) -> Tuple[bool, str]`

Met à jour tous les champs d'un site.

```python
from app.services.sites import update_site_full

success, message = update_site_full(
    site_id=123,
    nom="Nouveau nom",
    ville="Saint-Pierre",
    lien="https://nouveau-site.com",
    description="Nouvelle description",
    categorie="Culture & loisirs",
    status="valide"
)
```

#### `create_site_admin(nom: str, ville: Optional[str], lien: str, description: str, categorie: str) -> Tuple[bool, str]`

Crée un nouveau site directement publié (admin uniquement).

```python
from app.services.sites import create_site_admin

success, message = create_site_admin(
    nom="Site publié",
    ville=None,
    lien="https://site.com",
    description="Description",
    categorie="Transport"
)
```

---

## ⭐ Services Talents (`app/services/talents.py`)

### Constantes

```python
from app.services.talents import TALENT_CATEGORIES, TALENT_STATUSES, TALENT_STATUS_LABELS

TALENT_CATEGORIES = ["Comédiens", "Chanteurs", "Influenceurs", "Célébrités"]
TALENT_STATUSES = ["en_attente", "valide", "refuse"]
TALENT_STATUS_LABELS = {"en_attente": "En attente", "valide": "Publié", ...}
```

### Récupération de données

#### `get_talents_data() -> OrderedDict[str, List[Dict[str, str]]]`

Récupère les talents validés groupés par catégorie (pour pages publiques).

```python
from app.services.talents import get_talents_data

talents_by_category = get_talents_data()
# Retourne : OrderedDict avec catégories comme clés
```

#### `get_admin_talents(status_filter: str = "en_attente", search_query: str = "") -> Dict[str, any]`

Récupère les talents pour le dashboard admin.

```python
from app.services.talents import get_admin_talents

data = get_admin_talents(status_filter="valide", search_query="comedien")
```

#### `get_talent_by_id(talent_id: int) -> Optional[sqlite3.Row]`

Récupère un talent par son ID.

### Opérations CRUD

#### `create_talent_proposal(pseudo: str, instagram: str, description: str) -> bool`

Crée une proposition de talent (statut : `en_attente`).

```python
from app.services.talents import create_talent_proposal

success = create_talent_proposal(
    pseudo="talent_pseudo",
    instagram="https://instagram.com/talent",
    description="Description du talent"
)
```

#### `update_talent_status(talent_id: int, status: str) -> Tuple[bool, str]`

Met à jour le statut d'un talent.

#### `delete_talent(talent_id: int) -> Tuple[bool, str]`

Supprime un talent.

#### `update_talent_full(talent_id: int, pseudo: str, instagram: str, description: str, category: str, image: str, status: str) -> Tuple[bool, str]`

Met à jour tous les champs d'un talent.

#### `create_talent_admin(pseudo: str, instagram: str, description: str, category: str, image: str, status: str) -> Tuple[bool, str]`

Crée un talent directement (admin uniquement).

### Helpers

#### `get_talent_category_choices(current: str | None = None) -> List[Tuple[str, str]]`

Retourne les choix pour un SelectField de catégorie.

```python
from app.services.talents import get_talent_category_choices

choices = get_talent_category_choices()
# Retourne : [("", "Sélectionnez..."), ("Comédiens", "Comédiens"), ...]
```

#### `get_talent_status_choices() -> List[Tuple[str, str]]`

Retourne les choix pour un SelectField de statut.

---

## 🔐 Services Auth (`app/services/auth.py`)

#### `verify_admin_credentials(username: str, password: str) -> bool`

Vérifie les identifiants admin.

```python
from app.services.auth import verify_admin_credentials

is_valid = verify_admin_credentials("admin", "password")
```

#### `admin_required(func: F) -> F`

Décorateur pour protéger les routes admin.

```python
from app.services.auth import admin_required

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    # Route protégée
    pass
```

---

## 📧 Services Emails (`app/services/emails.py`)

#### `send_submission_notification(payload: Mapping[str, Any]) -> None`

Envoie un email de notification lors d'une nouvelle proposition.

```python
from app.services.emails import send_submission_notification

send_submission_notification({
    "nom": "Site exemple",
    "ville": "Saint-Denis",
    "lien": "https://site.com",
    "description": "Description",
    "categorie": "Transport",
    "date_submission": "01/01/2025 10:00",
    "remote_addr": "192.168.1.1"
})
```

**Note** : L'envoi est silencieusement ignoré si `MAIL_ENABLED=false` dans la config.

---

## 🔄 Gestion d'erreurs

Toutes les fonctions de service utilisant la base de données peuvent lever `DatabaseError` :

```python
from app.database import DatabaseError
from app.services.sites import get_sites_by_category

try:
    sites = get_sites_by_category("Transport")
except DatabaseError as exc:
    # Gérer l'erreur (logging, message utilisateur, etc.)
    current_app.logger.error(f"Erreur DB: {exc}")
    sites = []  # Valeur par défaut
```

---

## 📝 Notes importantes

1. **Toutes les fonctions de service sont synchrones** (pas d'async pour l'instant)
2. **Les fonctions CRUD retournent `(bool, str)`** pour indiquer succès/échec
3. **Les requêtes utilisent des paramètres liés** pour éviter les injections SQL
4. **Le cache des catégories** est géré automatiquement via Flask `g`

Pour plus de détails, consulter le code source dans `app/services/`.

