# AGENTS.md

Guide de développement pour Réunion Wiki.

Objectif : garder le projet Flask simple, maintenable et sûr pendant les futurs refactors.

## Architecture

Structure actuelle :

```text
app.py
reunion_wiki/
├── app.py
├── routes/
├── services/
├── repositories/
├── auth.py
├── db.py
├── taxonomy.py
└── utils.py
```

Flux cible :

```text
Routes
↓
Services
↓
Repositories
↓
SQLite
```

## Routes

Les routes Flask doivent rester fines.

Responsabilités autorisées :

- Lire `request`, `args`, `form`, `headers`.
- Instancier et valider les formulaires WTForms.
- Appeler un service ou repository de lecture simple.
- Faire `render_template`, `redirect`, `abort`, `flash`.
- Gérer les erreurs HTTP simples.

À éviter dans les routes :

- SQL direct.
- Règles métier complexes.
- Transactions manuelles.
- Construction longue de filtres SQL.
- Validation métier réutilisable.

Règle admin :

```text
Toute nouvelle fonctionnalité admin :

Route
↓
Service
↓
Repository
```

Interdit : ajouter de la logique métier directement dans `routes/admin.py`.

## Services

Les services contiennent la logique métier.

Responsabilités :

- Orchestrer plusieurs repositories.
- Appliquer les règles métier.
- Valider les décisions applicatives.
- Gérer les workflows.

Exemples :

- Tracking de clic.
- Anti double clic.
- Modération admin.
- Création ou édition de site.
- Résolution catégorie/ville avant écriture.

Les services ne doivent pas contenir de SQL brut.

## Repositories

Les repositories sont responsables uniquement de l'accès aux données.

Autorisé :

- `SELECT`
- `INSERT`
- `UPDATE`
- `DELETE`
- Ouverture/fermeture de connexion.
- Retour de `sqlite3.Row`, listes de rows, ou `rowcount`.

Interdit :

- Détection de bots.
- Validation métier.
- Modération.
- Génération de slugs métier.
- Décisions de workflow.
- Accès direct à `request`, `session`, `flash`, `render_template`.

SQL :

- Toujours utiliser du SQL paramétré.
- Ne pas introduire SQLAlchemy.
- Conserver SQLite.
- Ne pas concaténer d'entrée utilisateur directement dans le SQL.

## Documentation

Toute nouvelle fonction créée dans :

- `repositories/`
- `services/`
- `auth.py`
- `db.py`
- `taxonomy.py`
- `utils.py`

doit avoir une docstring Python.

Format minimal :

```python
def get_site_by_id(site_id):
    """
    Récupère un site à partir de son identifiant.

    Args:
        site_id (int): Identifiant du site.

    Returns:
        sqlite3.Row | None:
            Site trouvé ou None.
    """
```

Commentaires :

- Ajouter un commentaire seulement si la logique n'est pas évidente.
- Ne jamais commenter une ligne triviale.
- Préférer des noms clairs + docstrings utiles.

## SEO

À préserver :

- URLs existantes.
- Redirections canoniques.
- Slugs publics.
- Pages utiles SEO : catégories, villes, tendances, blog, sitemap, robots.
- Templates et blocs meta existants.

Avant de supprimer une route publique :

- Vérifier les liens internes.
- Vérifier l'intérêt SEO.
- Vérifier sitemap/robots/templates.
- Préférer "à réévaluer" à une suppression rapide.

## Flask

Règles :

- Ne pas modifier les URLs sans demande explicite.
- Ne pas casser les endpoints legacy encore utilisés par `url_for`.
- Garder les blueprints par domaine : public, admin, SEO.
- Les templates ne doivent pas recevoir de changements pendant un refactor backend sauf nécessité.
- Les formulaires WTForms ne doivent pas être modifiés pendant un refactor d'architecture.

## Refactors Futurs

Priorité recommandée :

1. Garder les routes admin fines.
2. Créer des services admin au fil des nouvelles fonctionnalités.
3. Sortir progressivement la logique restante de `routes/admin.py`.
4. Casser le cycle fragile `db.py` / `taxonomy.py`.
5. Centraliser les helpers communs des repositories si cela reste simple.
6. Déplacer `queries.py` vers un service de lecture homepage.

À éviter :

- Gros refactor global sans tests.
- Introduction de SQLAlchemy.
- Changement massif des templates.
- Suppression de routes publiques uniquement parce qu'elles sont peu liées.
- Mélanger logique métier et SQL dans un même module.

## Checklist Avant Commit

- `python3 -m compileall .`
- Pas de SQL direct ajouté dans les routes.
- Pas de logique métier ajoutée dans `routes/admin.py`.
- Toute nouvelle fonction concernée a une docstring.
- Aucun template ou formulaire modifié sans nécessité.
- Aucune URL publique changée sans demande explicite.

## Tests

Après chaque modification significative :

- Exécuter `python3 -m compileall .`
- Vérifier le démarrage Flask.
- Tester manuellement les pages impactées.
- Vérifier les logs en cas de modification admin ou base de données.

Avant un commit important :

- Accueil `/`
- Une catégorie
- Une ville
- Recherche
- Admin login
- Dashboard admin

## Déploiement

Le projet est déployé sur :

- VPS OVH Debian
- Docker Compose
- Nginx reverse proxy
- Gunicorn
- Flask
- SQLite
- Redis

Lors d'un refactor :

- Préserver la compatibilité `python3 app.py`
- Préserver la compatibilité `gunicorn app:app`
- Ne pas modifier la structure de déploiement sans demande explicite.

## Philosophie

Privilégier les refactors minimaux.

Avant tout refactor :

- Vérifier qu'il apporte un bénéfice réel.
- Éviter les gros changements de structure.
- Préférer plusieurs petits refactors sûrs à un refactor massif.
- Ne pas introduire de nouvelles couches d'abstraction sans besoin concret.

Objectif :

Maintenir un projet simple, lisible et évolutif.
