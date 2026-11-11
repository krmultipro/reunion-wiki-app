# UX — Recherche publique des sites

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Statut | Décision validée et implémentée |
| Dernière mise à jour | 17 septembre 2026 |
| Règles liées | RM-10 à RM-14 et RM-SITE-007 |

## Parcours attendu

1. Le visiteur saisit du texte puis lance explicitement la recherche.
2. La page affiche les résultats et les critères disponibles.
3. Un changement de catégorie, de commune ou de tri actualise automatiquement
   les résultats sans bouton « Appliquer ».
4. Le texte, les autres filtres et le tri restent actifs pendant cette
   actualisation.
5. L'URL reflète l'état complet de la recherche.

La portée géographique reste reportée tant que le modèle des sites ne la
représente pas explicitement.

## Paramètres d'URL

| Paramètre | Usage |
| --- | --- |
| `q` | Texte recherché |
| `categorie` | Slug de la catégorie principale |
| `commune` | Slug de la commune |
| `sort` | `relevance`, `popularite`, `date` ou `nom` |
| `page` | Page courante lorsque la pagination sera nécessaire |

Une valeur de filtre inconnue ne doit pas exposer de résultat inattendu. Elle
doit être ignorée de manière visible ou produire un état sans résultat clair,
mais ne doit jamais être interprétée comme une clause SQL.

## Actualisation automatique

L'automatisation peut utiliser une soumission GET classique. Une mise à jour
asynchrone n'est pas obligatoire. Le comportement attendu est l'absence d'une
seconde action de validation après le changement d'un filtre ou du tri.

Le clavier doit permettre de modifier un choix et de déclencher le même
comportement. Le focus doit rester prévisible après l'actualisation.

## Réinitialisation

Deux actions distinctes sont proposées :

- « Effacer les filtres » conserve le texte recherché, remet le tri sur la
  pertinence et retire la catégorie et la commune ;
- « Nouvelle recherche » efface le texte, les filtres, le tri et la page.

## Mobile

Les filtres sont regroupés derrière « Affiner ». Le libellé indique le nombre de
filtres actifs. Les critères actifs restent visibles sous une forme compacte et
peuvent être retirés individuellement.

## États à distinguer

- **Chargement :** annoncer l'actualisation en cours.
- **Résultats :** afficher la liste et, lorsque disponible, son nombre total.
- **Aucun résultat :** proposer l'effacement des filtres, les catégories et la
  proposition d'un site.
- **Erreur :** expliquer que la recherche n'a pas pu aboutir et proposer de
  réessayer.

## Critères d'acceptation prioritaires

1. Changer la catégorie actualise les résultats sans clic supplémentaire.
2. Changer la commune actualise les résultats sans clic supplémentaire.
3. Changer le tri actualise l'ordre sans clic supplémentaire.
4. Chaque actualisation conserve le texte et les autres critères actifs.
5. L'URL obtenue restaure la même recherche après rechargement.
6. « Effacer les filtres » conserve le texte et retire les filtres.
7. « Nouvelle recherche » remet le parcours dans son état initial.
8. Les interactions fonctionnent au clavier et les changements sont annoncés
   de manière accessible.

## État observé au 17 septembre 2026

La recherche, les filtres catégorie et commune ainsi que les quatre tris sont
implémentés. Les changements de filtre et de tri soumettent automatiquement le
formulaire GET, conservent les autres critères dans l'URL et annoncent le
chargement. Sur mobile, les filtres sont regroupés derrière « Affiner » avec le
nombre de critères actifs. Les critères peuvent être retirés individuellement,
et les actions « Effacer les filtres » et « Nouvelle recherche » sont séparées.

Les marqueurs et liens de cette interface sont couverts par les tests
d'intégration. Le parcours automatique a également été vérifié manuellement
dans un navigateur local. Un test de navigateur de bout en bout reste à ajouter
si cette couche d'automatisation est introduite dans le projet.

Le tri par date utilise `published_at`. Une simple correction ou une
republication normale ne fait pas remonter un site ; seule l'option explicite
« Traiter comme une nouvelle publication » actualise cette date.
