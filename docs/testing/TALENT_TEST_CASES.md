# Cas de test — Parcours des talents

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Statut | À automatiser |
| Dernière mise à jour | 15 septembre 2026 |
| Périmètre | MVP talents |

## Signification des identifiants

- **RM** signifie **Règle Métier**. Par exemple, `RM-37` est la règle générale
  du catalogue qui limite la visibilité publique aux fiches publiées.
- **RM-TAL** signifie **Règle Métier — Talent**. Ces règles détaillent les
  décisions propres au module talents. Par exemple, `RM-TAL-006` impose le
  passage initial par un brouillon.
- **TC** signifie **Test Case**, ou **cas de test**. Par exemple,
  `TC-TAL-037-01` est le premier cas de test du module talents associé à
  RM-37.

Une règle décrit ce que le produit doit respecter. Un cas de test décrit la
situation à créer, l'action à effectuer et le résultat concret à observer pour
prouver que la règle fonctionne.

## Convention

- Chaque cas possède un identifiant stable préfixé par `TC-TAL`.
- Chaque cas indique la règle métier qu'il vérifie.
- Un cas passe uniquement si tous ses résultats attendus sont observés.
- Une règle passe au statut **Testée** uniquement lorsque tous ses cas
  obligatoires sont automatisés ou exécutés manuellement avec succès.
- Une évolution d'une règle métier entraîne la révision des cas associés.

## Fiche de test 1 — Brouillon et visibilité

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-TAL-006 et RM-37 |
| Priorité | Critique |
| Type recommandé | Intégration |
| État | À automatiser |

### Objectif

Vérifier qu'une nouvelle fiche commence toujours en brouillon, qu'une action
séparée est nécessaire pour la publier et que seules les fiches publiées sont
accessibles dans l'espace public.

### Préconditions générales

- Un administrateur peut accéder à l'administration des talents.
- Une catégorie principale valide existe.
- Les fiches utilisées par les cas ont des slugs différents.
- Les pages publiques de l'index et du détail des talents sont disponibles.

### TC-TAL-006-01 — Création en brouillon

- **Règle liée :** RM-TAL-006.
- **Situation initiale :** aucune fiche correspondant au talent de test
  n'existe.
- **Action :** un administrateur crée une fiche avec les informations
  obligatoires.
- **Résultats attendus :**
  - la fiche est enregistrée avec le statut `draft` ;
  - la fiche est visible dans l'administration ;
  - la fiche n'apparaît pas dans l'index public ;
  - son URL publique n'affiche pas la fiche.

### TC-TAL-006-02 — Publication directe impossible

- **Règle liée :** RM-TAL-006.
- **Situation initiale :** aucune fiche correspondant au talent de test
  n'existe.
- **Action :** un administrateur utilise le formulaire de création.
- **Résultats attendus :**
  - le formulaire ne permet pas de créer directement une fiche publiée ;
  - l'enregistrement produit un brouillon ;
  - une action de publication distincte est nécessaire.

### TC-TAL-037-01 — Brouillon invisible

- **Règle liée :** RM-37.
- **Situation initiale :** une fiche existe avec le statut `draft`.
- **Action :** un visiteur consulte l'index public puis demande directement
  l'URL de la fiche.
- **Résultats attendus :**
  - la fiche est absente de l'index ;
  - l'URL publique retourne une page introuvable ;
  - la fiche reste accessible dans l'administration.

### TC-TAL-037-02 — Fiche archivée invisible

- **Règle liée :** RM-37.
- **Situation initiale :** une fiche existe avec le statut `archived`.
- **Action :** un visiteur consulte les listes publiques puis demande
  directement l'URL de la fiche.
- **Résultats attendus :**
  - la fiche est absente des listes publiques ;
  - l'URL publique retourne une page introuvable ;
  - les informations de la fiche restent conservées dans l'administration.

### TC-TAL-037-03 — Fiche publiée visible

- **Règle liée :** RM-37.
- **Situation initiale :** une fiche valide existe avec le statut `published`.
- **Action :** un visiteur consulte l'index puis ouvre la fiche.
- **Résultats attendus :**
  - la fiche apparaît dans l'index public ;
  - son URL publique est accessible ;
  - son nom, sa catégorie principale et sa présentation sont affichés.

### TC-TAL-037-04 — Archivage d'une fiche publiée

- **Règles liées :** RM-37 et RM-TAL-007.
- **Situation initiale :** une fiche publiée est accessible au public.
- **Action :** un administrateur archive la fiche.
- **Résultats attendus :**
  - la fiche disparaît des listes publiques ;
  - son URL publique retourne une page introuvable ;
  - elle reste présente dans l'administration avec le statut `archived`.

### Condition de validation de la fiche 1

La fiche de test est considérée comme réussie lorsque les six cas passent. Les
règles RM-TAL-006 et RM-37 ne peuvent être marquées **Testées** qu'après cette
réussite et l'enregistrement de la date et du contexte d'exécution.

## Fiche de test 2 — Rattachement et sources

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-31, RM-TAL-001 et RM-TAL-003 |
| Priorité | Critique |
| Type recommandé | Service et intégration |
| État | À automatiser |

### Objectif

Vérifier qu'un brouillon peut rester incomplet, mais que la publication exige
au moins un rattachement réel à La Réunion et une source publique pertinente.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-031-01 | Un brouillon ne possède ni rattachement ni source. | L'administrateur enregistre le brouillon. | L'enregistrement réussit et le statut reste `draft`. |
| TC-TAL-031-02 | Un brouillon possède une source, mais aucun rattachement. | L'administrateur demande la publication. | La publication est refusée, une erreur sur le rattachement est affichée et la fiche reste `draft`. |
| TC-TAL-031-03 | Un brouillon possède un rattachement, mais aucune source. | L'administrateur demande la publication. | La publication est refusée, une erreur sur la source est affichée et la fiche reste `draft`. |
| TC-TAL-031-04 | Un brouillon possède un rattachement et une source publique valide. | L'administrateur demande la publication. | Les contrôles RM-31 réussissent et la publication peut continuer. |
| TC-TAL-031-05 | Un brouillon possède plusieurs rattachements et plusieurs sources valides. | L'administrateur enregistre puis publie la fiche. | Toutes les valeurs sont conservées et au moins une source est affichée publiquement. |

### Condition de validation de la fiche 2

Les cinq cas doivent passer. Les erreurs de publication doivent être explicites
et ne doivent jamais supprimer les données déjà saisies dans le brouillon.

## Fiche de test 3 — Données obligatoires et catégorie principale

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-30 et RM-36 |
| Priorité | Critique |
| Type recommandé | Formulaire, service et intégration |
| État | À automatiser |

### Objectif

Vérifier les informations minimales d'une fiche et l'existence d'une seule
catégorie principale.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-030-01 | Une fiche ne possède ni nom affiché ni pseudonyme. | L'administrateur tente de l'enregistrer ou de la publier. | L'action est refusée avec une erreur explicite. |
| TC-TAL-030-02 | Une fiche possède un pseudonyme, mais aucun nom civil. | L'administrateur l'enregistre avec les autres informations obligatoires. | L'enregistrement réussit : un pseudonyme suffit comme nom affiché. |
| TC-TAL-030-03 | Une fiche ne possède aucune présentation. | L'administrateur demande la publication. | La publication est refusée et la fiche reste `draft`. |
| TC-TAL-036-01 | Une fiche ne possède aucune catégorie principale. | L'administrateur demande la publication. | La publication est refusée avec une erreur de catégorie. |
| TC-TAL-036-02 | Une fiche possède une catégorie principale valide. | L'administrateur enregistre puis publie la fiche. | Une seule catégorie principale est conservée et affichée. |

### Condition de validation de la fiche 3

Les cinq cas doivent passer et aucune fiche publique ne doit être dépourvue de
nom affiché, de présentation ou de catégorie principale.

## Fiche de test 4 — Passage en publication

| Propriété | Valeur |
| --- | --- |
| Règle couverte | RM-TAL-010 |
| Priorité | Critique |
| Type recommandé | Service et intégration |
| État | À automatiser |

### Objectif

Vérifier que l'action de publication exécute tous les contrôles métier et ne
publie jamais une fiche invalide.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-PUB-01 | Une fiche possède toutes les informations obligatoires, un rattachement, une source et des URLs valides. | L'administrateur demande la publication. | Le statut devient `published` et la fiche devient accessible publiquement. |
| TC-TAL-PUB-02 | Une fiche échoue à au moins un contrôle obligatoire. | L'administrateur demande la publication. | Toutes les erreurs utiles sont affichées et la fiche reste `draft`. |
| TC-TAL-PUB-03 | Une première tentative de publication échoue, puis les données sont corrigées. | L'administrateur demande de nouveau la publication. | La deuxième tentative réussit sans recréer la fiche ni perdre les informations précédentes. |

### Condition de validation de la fiche 4

Les trois cas doivent passer. Aucun autre parcours ne doit permettre de
contourner les contrôles de publication.

## Fiche de test 5 — Plateformes et Twitch

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-32, RM-33 et RM-TAL-008 |
| Priorité | Haute |
| Type recommandé | Formulaire, service et intégration |
| État | À automatiser |

### Objectif

Vérifier que les plateformes restent facultatives, que leurs URLs sont valides
et que Twitch fonctionne comme les autres plateformes du MVP.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-PLAT-01 | Une fiche valide ne possède aucun lien de plateforme. | L'administrateur la publie. | La publication réussit et aucun lien social vide n'est affiché. |
| TC-TAL-PLAT-02 | Une fiche possède une ou plusieurs plateformes parmi Instagram, YouTube, TikTok, Facebook, Twitch et site officiel. | L'administrateur l'enregistre. | Chaque champ reste facultatif et les URLs renseignées sont conservées. |
| TC-TAL-PLAT-03 | Une plateforme contient une URL invalide. | L'administrateur enregistre ou publie la fiche. | L'action est refusée avec une erreur associée à la plateforme concernée. |
| TC-TAL-PLAT-04 | Une fiche possède une URL Twitch HTTP ou HTTPS valide. | L'administrateur la publie puis un visiteur ouvre la fiche. | L'URL est conservée et le lien Twitch est affiché publiquement. |
| TC-TAL-PLAT-05 | Une fiche publiée possède Twitch et une autre fiche Twitch reste en brouillon. | Un visiteur utilise le filtre Twitch. | Seule la fiche publiée apparaît dans les résultats. |

### Condition de validation de la fiche 5

Les cinq cas doivent passer. L'absence d'une page SEO Twitch dédiée n'empêche
pas la validation du MVP.

## Fiche de test 6 — Correction et archivage

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-39 et RM-TAL-007 |
| Priorité | Haute |
| Type recommandé | Autorisation et intégration |
| État | À automatiser |

### Objectif

Vérifier que seul un administrateur peut appliquer une correction ou un
archivage et que l'historique d'une fiche archivée est conservé.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-039-01 | Un visiteur non authentifié connaît une URL d'administration. | Il tente de modifier ou d'archiver une fiche. | L'action est refusée et aucune donnée n'est modifiée. |
| TC-TAL-039-02 | Une fiche publiée contient une information à corriger. | Un administrateur modifie puis enregistre la fiche. | La même fiche est mise à jour et la correction apparaît publiquement sans duplication. |
| TC-TAL-039-03 | Une fiche publiée doit être archivée. | Un administrateur l'archive. | La fiche disparaît du public, reste en base et demeure consultable dans l'administration. |
| TC-TAL-039-04 | Une demande vérifiée de correction, d'archivage ou de retrait existe. | L'administrateur enregistre sa décision et applique l'action. | La date, le motif, la décision et l'action restent accessibles uniquement dans l'administration. |

Le comportement public de l'archivage est également vérifié par
`TC-TAL-037-04` dans la fiche 1.

### Condition de validation de la fiche 6

Les quatre cas et `TC-TAL-037-04` doivent passer. Aucun accès public ne doit
permettre de modifier directement une fiche.

## Fiche de test 7 — Recherche et filtres publics

| Propriété | Valeur |
| --- | --- |
| Règle couverte | RM-40 et RM-TAL-009 |
| Priorité | Haute |
| Type recommandé | Repository, service et intégration publique |
| État | À automatiser |

### Objectif

Vérifier la recherche publique, les filtres combinables et l'exclusion de
toutes les fiches qui ne sont pas publiées.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-SEARCH-01 | Plusieurs fiches publiées possèdent des noms différents. | Le visiteur recherche un nom affiché. | Les fiches publiées correspondantes apparaissent. |
| TC-TAL-SEARCH-02 | Une fiche publiée possède un pseudonyme distinct de son nom éventuel. | Le visiteur recherche le pseudonyme. | La fiche correspondante apparaît. |
| TC-TAL-SEARCH-03 | Le terme recherché apparaît uniquement dans la présentation d'une fiche publiée. | Le visiteur lance la recherche. | La fiche correspondante apparaît. |
| TC-TAL-SEARCH-04 | Plusieurs catégories principales sont représentées. | Le visiteur sélectionne une catégorie. | Seules les fiches publiées de cette catégorie apparaissent. |
| TC-TAL-SEARCH-05 | Plusieurs plateformes sont représentées. | Le visiteur sélectionne une plateforme. | Seules les fiches publiées possédant cette plateforme apparaissent. |
| TC-TAL-SEARCH-06 | Des fiches diffèrent par texte, catégorie et plateforme. | Le visiteur combine une recherche, une catégorie et une plateforme. | Seules les fiches satisfaisant simultanément les trois conditions apparaissent. |
| TC-TAL-SEARCH-07 | Une fiche publiée, un brouillon et une fiche archivée correspondent aux mêmes critères. | Le visiteur effectue la recherche. | Seule la fiche publiée apparaît. |
| TC-TAL-SEARCH-08 | Aucun talent publié ne correspond aux critères. | Le visiteur effectue la recherche. | Un message clair et une action de réinitialisation des filtres sont affichés. |

### Condition de validation de la fiche 7

Les huit cas doivent passer sur l'interface publique et les paramètres de
recherche ne doivent jamais permettre d'exposer un brouillon ou une archive.

## Fiche de test 8 — Image générique minimale

| Propriété | Valeur |
| --- | --- |
| Règle couverte | RM-38 et RM-TAL-004 |
| Priorité | Normale |
| Type recommandé | Service et rendu public |
| État | À automatiser |

### Objectif

Vérifier uniquement le comportement minimal retenu pour le MVP pendant le
report de la gestion structurée des autorisations.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-TAL-IMG-01 | Une fiche valide ne possède aucun portrait. | L'administrateur la publie. | La publication n'est pas bloquée par l'absence d'image. |
| TC-TAL-IMG-02 | Une fiche publiée ne possède aucun chemin d'image. | Un visiteur ouvre l'index puis la fiche. | L'image générique Réunion Wiki est affichée aux deux endroits. |

### Condition de validation de la fiche 8

Les deux cas doivent passer. Les cas relatifs aux champs structurés de
provenance, de licence et d'autorisation seront ajoutés lorsque RM-38 entrera
dans le périmètre de développement.

## Suivi d'exécution

| Fiche | Date | Environnement | Résultat | Exécuté par | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 — Brouillon et visibilité | — | — | Non exécuté | — | Automatisation à créer. |
| 2 — Rattachement et sources | — | — | Non exécuté | — | Automatisation à créer. |
| 3 — Données obligatoires | — | — | Non exécuté | — | Automatisation à créer. |
| 4 — Publication | — | — | Non exécuté | — | Automatisation à créer. |
| 5 — Plateformes et Twitch | — | — | Non exécuté | — | Automatisation à créer. |
| 6 — Correction et archivage | — | — | Non exécuté | — | Automatisation à créer. |
| 7 — Recherche et filtres | — | — | Non exécuté | — | Automatisation à créer. |
| 8 — Image générique | — | — | Non exécuté | — | Automatisation à créer. |

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.1 | 15 septembre 2026 | Ajout des fiches prioritaires sur les rattachements, les sources, les données obligatoires, la publication, les plateformes, Twitch, l'administration, la recherche et l'image générique. Ajout du glossaire RM, RM-TAL et TC. |
| 1.0 | 15 septembre 2026 | Création de la première fiche couvrant le brouillon, la publication, la visibilité publique et l'archivage. |
