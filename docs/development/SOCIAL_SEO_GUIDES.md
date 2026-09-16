# Guides SEO sociaux dynamiques

## Objectif

Réunion Wiki possède une page SEO publique par réseau social :

| Réseau | URL publique | Champ de la fiche talent |
| --- | --- | --- |
| YouTube | `/youtubeurs-reunionnais` | `youtube_url` |
| Instagram | `/createurs-instagram-reunionnais` | `instagram_url` |
| TikTok | `/tiktokeurs-reunionnais` | `tiktok_url` |
| Facebook | `/createurs-facebook-reunionnais` | `facebook_url` |

Ces pages sont fixes et éditables, tandis que leur sélection de talents est
dynamique. Il n'existe donc pas une nouvelle page SEO pour chaque talent : une
page par réseau rassemble automatiquement les fiches publiées qui possèdent
l'URL sociale correspondante.

Exemple : un talent publié avec une `youtube_url` et une `instagram_url`
apparaît automatiquement dans les sélections YouTube et Instagram.

## Vue d'ensemble du flux

Le projet respecte l'architecture habituelle :

```text
Route Flask
    ↓
Service métier
    ↓
Repository
    ↓
SQLite
    ↓
Service métier
    ↓
Template Jinja
```

Pour une page TikTok, le flux concret est :

```text
GET /tiktokeurs-reunionnais
→ reunion_wiki/routes/content.py
→ content_service.get_public_page_context()
→ talent_service.get_public_social_creator_cards("tiktok")
→ talent_repository.list_published_with_social_url("tiktok_url")
→ base SQLite
→ templates/content/page.html
```

La responsabilité de chaque couche reste distincte :

- la route reçoit la requête et retourne la réponse HTTP ;
- le service applique les règles métier et prépare les données ;
- le repository exécute les requêtes SQL ;
- le template présente les données sans décider quelles fiches sélectionner.

## Configuration centrale

Le fichier `reunion_wiki/social_guides.py` contient `SOCIAL_GUIDES`, la configuration unique
des quatre réseaux.

Chaque entrée définit notamment :

- `field` : colonne sociale de la table `talents` ;
- `slug` : URL publique stable ;
- `platform` : nom du réseau ;
- `hub_title` et `hub_description` : présentation dans le hub ;
- `collection_title` et `collection_intro` : présentation de la sélection ;
- `count_label_singular` et `count_label_plural` : phrase compacte après le compteur ;
- `empty_message` : texte affiché lorsqu'aucun talent ne correspond ;
- `profile_link_label` : texte du lien inverse sur une fiche talent ;
- `title`, `summary` et `body` : contenu éditorial initial ;
- `meta_title` et `meta_description` : métadonnées SEO initiales.

Exemple simplifié :

```python
"instagram": {
    "field": "instagram_url",
    "slug": "createurs-instagram-reunionnais",
    "platform": "Instagram",
    "title": "Créateurs Instagram réunionnais",
}
```

`SOCIAL_GUIDES_BY_SLUG` construit aussi une table de correspondance inverse.
Elle permet de retrouver la configuration d'un réseau à partir du slug demandé.

Cette configuration sert à deux moments différents :

1. lors de la migration, comme contenu par défaut pour créer une page absente ;
2. lors d'une requête publique, pour savoir quel champ social utiliser.

Elle ne remplace pas l'administration. Après la création d'une page, son titre,
son résumé, son corps et ses métadonnées sont lus depuis la base de données.

## Création des pages par la migration

La fonction `_ensure_social_content_pages()` de `migrate.py` parcourt la
configuration et insère les pages sociales qui n'existent pas encore.

La migration est idempotente :

```text
Page absente
→ création avec les valeurs par défaut

Page déjà présente
→ aucune modification
```

Il est donc possible d'exécuter plusieurs fois `python migrate.py` sans créer de
doublon et sans écraser un texte personnalisé dans l'administration.

Une migration éditoriale ciblée peut exceptionnellement faire évoluer un ancien
texte par défaut. Elle doit alors reconnaître précisément les versions
historiques connues et mettre à jour chaque champ séparément. C'est le cas de
`_upgrade_youtube_default_copy()` : le nouveau résumé ou le nouveau corps
YouTube est appliqué seulement si le champ contient encore une ancienne valeur
par défaut. Un champ personnalisé dans l'administration reste inchangé.

Les pages sont enregistrées comme des contenus standards de type `seo_landing`.
Elles profitent ainsi du CRUD, des statuts et du sitemap déjà existants.

Attention : modifier les textes par défaut dans `reunion_wiki/social_guides.py` ne met pas à
jour les lignes déjà créées dans la base. Une page existante doit être modifiée
depuis l'administration, ou faire l'objet d'une migration explicite si une mise
à jour automatique devient nécessaire.

## Sélection dynamique des talents

Le repository `talent_repository` expose :

```python
list_published_with_social_url(url_field, limit=None, offset=0)
count_published_with_social_url(url_field)
```

Pour Instagram, la requête correspond conceptuellement à :

```sql
SELECT ...
FROM talents
WHERE status = 'published'
  AND instagram_url IS NOT NULL
  AND TRIM(instagram_url) != ''
ORDER BY display_order, name, id;
```

Les règles d'appartenance à une sélection sont donc :

1. la fiche talent doit avoir le statut `published` ;
2. l'URL du réseau doit être renseignée et non vide.

La relation n'est pas enregistrée dans une table de liaison supplémentaire. Elle
est déduite directement des colonnes sociales de la fiche talent.

### Sécurisation du nom de colonne

Le nom de colonne ne peut pas être transmis comme un paramètre SQL classique.
Le repository utilise donc une liste blanche :

```python
SOCIAL_URL_COLUMNS = {
    "instagram_url",
    "youtube_url",
    "tiktok_url",
    "facebook_url",
}
```

Une valeur absente de cette liste est refusée. Cela empêche une entrée externe
d'injecter un nom de colonne ou une expression SQL arbitraire dans la requête.

Les valeurs SQL ordinaires continuent d'utiliser des paramètres `?` SQLite.

## Préparation des données par les services

`talent_service.get_public_social_creator_cards(network_key)` :

1. lit la configuration du réseau ;
2. demande les talents correspondants au repository ;
3. transforme les lignes SQLite en cartes publiques utilisables par Jinja.

`talent_service.get_public_social_guides()` prépare le hub de la page des
créateurs. Pour chaque page sociale publiée, il renvoie son titre, son résumé,
son URL et le nombre de talents correspondant.

`talent_service.get_public_social_guide(network_key)` récupère un guide précis.
La page d'accueil utilise cette fonction pour mettre en avant YouTube uniquement.

`content_service.get_public_page_context(slug)` traite toutes les pages de
contenu publiques. Si le slug demandé appartient à `SOCIAL_GUIDES_BY_SLUG`, il
ajoute au contexte :

```python
{
    "social_guide": ...,           # configuration du réseau
    "dynamic_creators": ...,      # cartes calculées depuis les talents
    "related_social_guides": ..., # autres guides publiés
}
```

Pour un contenu classique, ces valeurs restent vides et le comportement
historique de la page n'est pas modifié.

## Affichage public et liens internes

### Page d'accueil

La page d'accueil affiche un lien visible vers la sélection des youtubeurs.

Le lien n'est affiché que si la page YouTube est publiée. Une page en brouillon
ou archivée ne produit donc pas un lien vers une URL publique indisponible.

Les autres réseaux ne sont volontairement pas mis en avant sur l'accueil.

### Hub des créateurs

La page `/createurs-reunionnais` contient un hub des réseaux sociaux. Il présente
les guides publiés sous forme de cartes avec :

- le réseau ;
- le titre éditorial ;
- le résumé ;
- le nombre de talents ;
- un lien vers la page SEO.

Le titre et le résumé viennent de la base : une modification effectuée dans
l'administration est donc immédiatement reflétée dans le hub.

### Pages SEO sociales

Le template `templates/content/page.html` est commun aux quatre réseaux. Il
affiche le titre de la page, puis immédiatement les cartes dynamiques des
talents. Sur un guide social, le résumé, l'image à la une et le corps éditorial
ne sont pas rendus sur la page publique afin de garder un accès direct aux
profils. Le résumé reste utilisé dans le hub des créateurs et dans les
métadonnées SEO. Les valeurs restent enregistrées et modifiables dans
l'administration. Les pages de contenu classiques conservent leur affichage
éditorial complet.

Entre le titre principal et les cartes, une seule phrase compacte indique le
nombre de résultats et décrit la sélection. Le nombre vient de
`dynamic_creators|length`, tandis que les variantes singulière et plurielle sont
définies par `count_label_singular` et `count_label_plural` dans
`reunion_wiki/social_guides.py`. La phrase n'est pas affichée lorsque la sélection est vide.

Chaque carte conduit vers la fiche Réunion Wiki du talent. Le système favorise
ainsi la navigation interne avant la sortie éventuelle vers le réseau social.

En bas de chaque guide, un bloc « Explorez les créateurs sur d'autres réseaux »
propose toutes les autres pages sociales publiées. Le guide courant est exclu.
Chaque page renvoie ainsi vers les trois autres lorsque les quatre guides sont
publiés, ce qui forme un maillage interne continu sans lien mort. Les cartes
reprennent le titre, le résumé et le compteur dynamiques de chaque sélection.

### Fiches talents

La fiche d'un talent construit `social_guide_links` à partir de ses URLs
sociales. Le bloc « Retrouvez ce créateur dans nos guides » permet la navigation
inverse :

```text
Page SEO du réseau → fiche talent → page SEO du réseau
```

Un lien inverse est affiché uniquement si :

1. l'URL sociale est renseignée sur le talent ;
2. la page SEO correspondante est publiée.

## Administration des pages sociales

Les pages se gèrent dans :

```text
Admin
→ Contenu SEO
```

L'administrateur peut modifier :

- le titre ;
- le résumé ;
- le corps de la page ;
- l'image à la une ;
- le meta title ;
- la meta description ;
- le statut.

Le slug d'une page sociale existante est volontairement en lecture seule dans
le formulaire. Le service protège aussi cette valeur côté serveur et ignore un
slug falsifié envoyé manuellement.

Cette double protection est nécessaire : un attribut HTML `readonly` améliore
l'interface, mais ne constitue pas une règle de sécurité serveur.

Le slug est verrouillé parce qu'il sert à relier l'enregistrement `content` à la
configuration du réseau. Le modifier casserait la détection dynamique et les
liens internes associés.

## Effet des statuts

Les statuts du contenu pilotent la visibilité de tout le guide :

| Statut | Page publique | Hub | Liens depuis les talents | Sitemap |
| --- | --- | --- | --- | --- |
| `draft` | Non | Non | Non | Non |
| `published` | Oui | Oui | Oui | Oui |
| `archived` | Non | Non | Non | Non |

Un talent en brouillon ou archivé n'apparaît jamais dans une sélection, même si
ses URLs sociales sont renseignées.

## Sitemap

Aucune liste spéciale des quatre URLs n'est maintenue dans le code du sitemap.

Les guides sont des contenus publiés standards. Le repository du sitemap les
sélectionne donc automatiquement avec les autres pages publiques. Cette solution
évite de maintenir la même information dans deux endroits différents.

## Suppression et remplacement de l'image à la une

Le formulaire de contenu possède une case :

```text
Supprimer l'image actuelle
```

Le service applique les règles suivantes :

| Action dans le formulaire | Résultat |
| --- | --- |
| Aucun nouveau fichier et case décochée | L'image actuelle est conservée |
| Nouveau fichier envoyé | La nouvelle image remplace l'ancienne |
| Case de suppression cochée sans nouveau fichier | Le champ est vidé et l'ancien fichier est supprimé |

Un nouvel upload est prioritaire sur la case de suppression : si un fichier est
envoyé, il devient la nouvelle image.

`image_storage.delete_upload()` vérifie que le chemin résolu reste à l'intérieur
du dossier configuré pour les uploads. Cette vérification protège contre les
tentatives de traversée de répertoires, par exemple `../../fichier`.

Le service nettoie aussi les fichiers devenus inutiles :

- nouvel upload suivi d'une erreur de validation ;
- nouvel upload suivi d'une erreur de base de données ;
- ancienne image après un remplacement réussi ;
- ancienne image après une suppression réussie.

La base SQLite ne stocke que le chemin relatif de l'image. Le fichier physique
reste dans le stockage des uploads.

## Exemple complet d'utilisation

Un administrateur crée et publie une fiche « Exemple Péi » avec :

```text
youtube_url = https://youtube.com/@exemple
instagram_url = https://instagram.com/exemple
tiktok_url = vide
facebook_url = vide
```

Au prochain chargement des pages :

- la fiche apparaît dans `/youtubeurs-reunionnais` ;
- elle apparaît dans `/createurs-instagram-reunionnais` ;
- elle n'apparaît pas dans les pages TikTok et Facebook ;
- sa fiche propose des liens vers les guides YouTube et Instagram ;
- les compteurs YouTube et Instagram du hub incluent cette fiche.

Si la fiche passe en brouillon, elle disparaît de ces sélections sans qu'il soit
nécessaire de modifier les pages SEO.

## Fichiers importants

| Fichier | Responsabilité |
| --- | --- |
| `reunion_wiki/social_guides.py` | Configuration commune et contenus initiaux |
| `migrate.py` | Création idempotente des pages absentes |
| `reunion_wiki/repositories/talent_repository.py` | Requêtes des talents par réseau et compteurs |
| `reunion_wiki/repositories/content_repository.py` | Lecture groupée des pages publiées |
| `reunion_wiki/services/talent_service.py` | Cartes, hub et liens inverses |
| `reunion_wiki/services/content_service.py` | Détection d'un guide, contexte public, slug et image |
| `reunion_wiki/routes/content.py` | Route publique générique `/<slug>` |
| `reunion_wiki/routes/public.py` | Mise en avant YouTube sur l'accueil |
| `templates/content/page.html` | Affichage commun des pages sociales |
| `templates/creators/index.html` | Hub des réseaux sociaux |
| `templates/creators/detail.html` | Liens inverses depuis un talent |
| `templates/admin/content/form.html` | Slug verrouillé et suppression d'image |
| `reunion_wiki/services/image_storage.py` | Stockage et suppression sécurisée des images |

## Déploiement

En local, la migration peut être lancée avec :

```bash
python migrate.py
```

En production, le conteneur web exécute déjà la migration avant le démarrage de
Gunicorn. Il faut néanmoins vérifier les logs du déploiement afin de confirmer
que la migration s'est terminée correctement.

Après le déploiement, contrôler au minimum :

1. les quatre URLs publiques ;
2. le hub de `/createurs-reunionnais` ;
3. le lien YouTube de l'accueil ;
4. une fiche possédant plusieurs réseaux ;
5. le sitemap ;
6. l'édition et la suppression de l'image d'une page dans l'administration.

## Limites et évolution possible

Le système actuel privilégie l'automatisation : toute URL sociale renseignée sur
un talent publié entraîne son ajout au guide correspondant.

Il n'est pas encore possible d'exclure manuellement un talent d'un seul guide
tout en conservant son URL sociale. Si ce besoin apparaît, deux évolutions sont
possibles :

- ajouter un booléen par réseau, par exemple `show_in_youtube_guide` ;
- créer une table de liaison pour sélectionner et ordonner précisément les
  talents de chaque guide.

La première solution serait plus simple. La table de liaison serait pertinente
uniquement si une véritable sélection éditoriale manuelle, avec classement, est
nécessaire.

Pour ajouter un nouveau réseau au système actuel, il faut au minimum :

1. disposer d'une colonne URL sur `talents` et dans son formulaire ;
2. ajouter cette colonne à `SOCIAL_URL_COLUMNS` ;
3. ajouter la configuration dans `SOCIAL_GUIDES` ;
4. exécuter la migration ;
5. ajouter ou adapter le style visuel du réseau ;
6. tester la page, le hub, les liens inverses et le sitemap.

## Vérifications techniques recommandées

Avant un commit touchant ce système :

```bash
python3 -m compileall -q .
git diff --check
```

Compléter par des tests fonctionnels :

- talent publié avec une URL sociale ;
- talent publié sans URL sociale ;
- talent en brouillon avec une URL sociale ;
- page sociale publiée puis archivée ;
- tentative de modification du slug côté serveur ;
- remplacement et suppression de l'image à la une ;
- affichage mobile sans débordement horizontal.
