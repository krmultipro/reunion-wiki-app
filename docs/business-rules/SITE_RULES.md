# Règles métier détaillées — Sites réunionnais

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.0 |
| Statut | Validé |
| Dernière mise à jour | 16 septembre 2026 |
| Domaine | Annuaire des sites réunionnais |

## Objet

Ce document précise les décisions métier applicables aux sites référencés dans
Réunion Wiki. Il complète le
[`RULES_CATALOG.md`](RULES_CATALOG.md) sans remplacer les identifiants `RM-01`
à `RM-29`, `RM-55`, `RM-58`, `RM-68` et `RM-69` issus du catalogue général.

## RM-SITE-001 — Admissibilité et lien avec La Réunion

- **Version :** 1.0
- **Statut :** Active
- **Règle :** un site peut être référencé s'il satisfait au moins l'un des
  critères suivants :
  - il représente une entreprise, une association ou un organisme réunionnais ;
  - son contenu est consacré principalement ou régulièrement à La Réunion ;
  - il s'agit d'un service national disposant d'une page ou d'une offre
    spécifique à La Réunion ;
  - il constitue une ressource particulièrement utile au public réunionnais.
- **Service national :** un site national sans contenu local particulier est
  refusé. Il ne devient admissible que si une section, une offre ou une utilité
  clairement identifiable pour La Réunion peut être constatée.
- **Contrôle éditorial :** l'administrateur vérifie ce lien avant publication.
  Il peut conserver une courte justification et, lorsque cela est possible,
  l'URL d'une page qui démontre le rattachement.
- **Caractère facultatif :** la justification écrite et l'URL de preuve ne sont
  pas des champs obligatoires et ne sont jamais affichées publiquement.
- **Critère d'acceptation :** un site sans lien réel constaté avec La Réunion
  n'est pas publié, même si aucune justification formelle n'est exigée dans le
  formulaire.

## RM-SITE-002 — Données minimales d'un site publié

- **Version :** 1.0
- **Statut :** Active
- **Règle :** un site publié possède un nom, une URL valide, une description
  neutre et une catégorie principale.
- **Critère d'acceptation :** la publication échoue si l'un de ces quatre
  éléments est absent ou invalide. La commune, la portée géographique, la
  justification du lien réunionnais, l'URL de preuve, les mots-clés et l'email
  du proposant restent facultatifs.

## RM-SITE-003 — Normalisation des URL et doublons

- **Version :** 1.0
- **Statut :** Active
- **Normalisation :** la comparaison ignore les majuscules du domaine, le `/`
  final, les ports standards et les paramètres publicitaires tels que
  `utm_source`.
- **HTTP et HTTPS :** les variantes HTTP et HTTPS sont considérées comme le
  même site lorsque le domaine et le chemin sont identiques. La version HTTPS
  est conservée lorsqu'elle fonctionne.
- **Doublon exact :** une URL normalisée identique est bloquée, qu'elle soit
  déjà en attente ou enregistrée dans un autre statut.
- **Même domaine :** plusieurs URL d'un même domaine sont autorisées si elles
  représentent des services réellement différents. Elles déclenchent seulement
  un avertissement destiné à l'administrateur.
- **Moments du contrôle :** la détection est exécutée lors d'une proposition
  publique, d'une création administrative et de toute modification de l'URL.
- **Critère d'acceptation :** un doublon exact n'est pas enregistré ; un domaine
  déjà connu ne bloque pas automatiquement une URL distincte.

## RM-SITE-004 — Catégorisation

- **Version :** 1.0
- **Statut :** Active
- **MVP :** chaque site possède exactement une catégorie principale. Ses autres
  activités peuvent être mentionnées dans sa description.
- **Évolution :** les catégories secondaires sont reportées en V2.
- **Désactivation :** à terme, une catégorie désactivée n'est plus proposée
  pour les nouveaux sites, mais les sites existants qui l'utilisent sont
  conservés.
- **Suppression :** une catégorie utilisée ne peut pas être supprimée. Les sites
  concernés doivent d'abord être réaffectés, ou la catégorie doit être archivée.
- **Critère d'acceptation :** le MVP refuse une publication sans catégorie
  principale et ne propose aucune catégorie secondaire.

## RM-SITE-005 — Commune et portée géographique

- **Version :** 1.0
- **Statut :** Active
- **Commune :** une commune est attribuée lorsque le site représente une
  activité, un établissement ou un service principalement associé à cette
  commune.
- **Toute La Réunion :** cette portée explicite est utilisée pour une activité
  couvrant l'ensemble de l'île ; aucune commune ne lui est attribuée
  arbitrairement.
- **En ligne :** cette portée explicite est utilisée pour une activité
  uniquement numérique qui n'est rattachée à aucune commune particulière.
- **Non précisée :** une commune vide signifie seulement que la localisation
  n'est pas précisée. Elle ne signifie ni `En ligne` ni `Toute La Réunion`.
- **Critère d'acceptation :** toute localisation renseignée correspond soit à
  une commune du référentiel, soit à la portée `Toute La Réunion`, soit à la
  portée `En ligne`. L'absence de choix reste admise comme `Non précisée`.

## RM-SITE-006 — Statuts et cycle de vie

- **Version :** 1.0
- **Statut :** Active
- **Statuts :**
  - `draft` : brouillon créé par un administrateur ;
  - `pending` : proposition publique en attente de modération ;
  - `published` : site visible publiquement ;
  - `refused` : proposition refusée ;
  - `archived` : ancien site retiré du public, mais conservé.
- **Proposition publique :** elle reçoit toujours le statut `pending` et ne peut
  jamais être publiée automatiquement.
- **Création administrative :** pour le MVP, un administrateur peut créer
  directement un site publié si tous les contrôles métier sont exécutés avec
  succès.
- **Archivage :** il est utilisé lorsqu'un site est fermé, inaccessible
  durablement, obsolète ou ne respecte plus les critères. Il retire le site du
  public sans supprimer son historique.
- **Suppression définitive :** elle est réservée à un doublon, une erreur de
  saisie, un contenu illégal ou une demande légitime nécessitant la suppression.
  Dans les autres situations, l'archivage est préféré.
- **Critère d'acceptation :** seuls les sites `published` sont visibles dans
  l'espace public ; un site archivé reste disponible dans l'administration.

## RM-SITE-007 — Recherche, filtres et découverte

- **Version :** 1.0
- **Statut :** Active
- **Recherche :** elle porte sur le nom, la description, la catégorie, la
  commune, le domaine ou l'URL et les éventuels mots-clés.
- **Filtres :** catégorie principale, commune et portée géographique.
- **Tris :** pertinence par défaut, popularité, date de publication la plus
  récente et ordre alphabétique.
- **Combinaison :** la recherche, les filtres et le tri peuvent être utilisés
  ensemble.
- **Visibilité :** tous les sites non publiés sont exclus des résultats.
- **Aucun résultat :** la page affiche un message clair, une action pour
  réinitialiser les filtres, quelques catégories proches et un lien permettant
  de proposer le site manquant.
- **Critère d'acceptation :** une recherche telle que `restaurant`, filtrée sur
  `Gastronomie` et `Saint-Denis`, ne renvoie que les sites publiés respectant
  simultanément ces critères.

## RM-SITE-008 — Clics, popularité et tendances

- **Version :** 1.0
- **Statut :** Active
- **Déclenchement :** un clic est comptabilisé uniquement lorsqu'un visiteur
  utilise le lien sortant géré par Réunion Wiki vers un site publié.
- **Déduplication :** une même adresse technique ne produit qu'un clic par site
  pendant une fenêtre de 30 minutes.
- **Exclusions :** les robots identifiés, les répétitions dans cette fenêtre,
  les administrateurs authentifiés et les liens vers des sites non publiés ne
  sont pas comptabilisés.
- **Indicateurs :**
  - la tendance actuelle utilise les clics des 7 derniers jours ;
  - la progression compare ces 7 jours aux 7 jours précédents ;
  - la popularité stable utilise les clics des 30 derniers jours.
- **Sites sans clic :** ils sont exclus des classements principaux de tendance,
  mais restent visibles dans les nouveautés et leurs catégories.
- **Correction :** un administrateur peut supprimer un événement incorrect ;
  le compteur agrégé du site est alors ajusté.
- **Critère d'acceptation :** un clic admissible crée un seul événement et un
  seul incrément ; sa suppression retire également cet incrément.

## RM-SITE-009 — Dates métier

- **Version :** 1.0
- **Statut :** Active
- **Dates distinctes :**
  - `submitted_at` conserve la date d'une proposition publique ;
  - `published_at` conserve la date de première publication ;
  - `updated_at` conserve la date de dernière modification.
- **Nouveautés :** les derniers sites ajoutés sont triés à partir de
  `published_at`.
- **Modification :** une correction ne modifie jamais la date de première
  publication.
- **Republication :** le désarchivage ou la republication ne donne pas une
  nouvelle date par défaut. Une nouvelle date n'est attribuée que si
  l'administrateur choisit explicitement de traiter le site comme une nouvelle
  publication.
- **Critère d'acceptation :** proposition, première publication et modification
  peuvent être distinguées sans déduire une date à partir d'une autre.

## RM-SITE-010 — Proposition publique et modération

- **Version :** 1.0
- **Statut :** Active
- **Champs proposés :** nom du site, URL, description, catégorie principale,
  commune ou portée, courte justification du lien avec La Réunion et email
  facultatif.
- **Champs obligatoires :** seuls le nom, l'URL, la description et la catégorie
  principale sont nécessaires à l'envoi. La commune ou portée, la justification,
  une éventuelle URL de preuve et l'email restent facultatifs.
- **Email :** il sert uniquement à demander une précision ou à informer le
  proposant de la décision. Il n'est jamais affiché publiquement.
- **Validation humaine :** aucune proposition n'est publiée automatiquement ;
  une validation administrative est toujours nécessaire.
- **Correction :** avant publication, l'administrateur peut corriger notamment
  la description, la catégorie, la commune, la portée ou l'URL normalisée.
- **Refus :** le motif est conservé au moins dans l'administration parmi :
  doublon, absence de lien avec La Réunion, site inaccessible, contenu interdit
  ou dangereux, informations insuffisantes, ou contenu hors ligne éditoriale.
- **Information du proposant :** elle n'est possible que si un email a été
  fourni. Le MVP peut utiliser une réponse manuelle sans notification
  automatique.
- **Critère d'acceptation :** un envoi public valide crée un élément `pending`,
  invisible publiquement, que l'administrateur peut corriger, publier ou refuser.

## RM-SITE-011 — Contrôles avant publication

- **Version :** 1.0
- **Statut :** Active
- **Contrôles :** avant toute publication, le système et l'administrateur
  vérifient :
  - la présence du nom ;
  - une URL HTTP ou HTTPS valide ;
  - l'absence de doublon exact ;
  - l'accessibilité du site ;
  - une description neutre ;
  - une catégorie principale valide ;
  - une commune ou une portée valide lorsqu'elle est renseignée ;
  - un lien réel avec La Réunion ;
  - l'absence de contenu manifestement illégal, trompeur ou dangereux.
- **Échec :** un site invalide reste en `draft` ou `pending` et les erreurs sont
  affichées à l'administrateur.
- **Critère d'acceptation :** aucune erreur de validation ne peut produire un
  statut `published`, y compris lors d'une création directe par un
  administrateur.

## RM-SITE-012 — Parcours pilote grandeur nature

- **Version :** 1.0
- **Statut :** Active
- **Site pilote :** le premier test utilise un vrai site réunionnais, simple,
  actif, dont la catégorie et la commune sont faciles à vérifier.
- **Parcours vérifié :**
  1. proposition publique ;
  2. détection de doublon ;
  3. enregistrement en attente ;
  4. modération ;
  5. correction éventuelle ;
  6. publication ;
  7. apparition dans la catégorie ;
  8. recherche ;
  9. redirection et comptage du clic ;
  10. apparition dans les nouveautés ;
  11. archivage ;
  12. disparition complète de l'espace public.
- **Critère de réussite :** le parcours fonctionne sans modification manuelle
  de la base de données et les compteurs, statuts et dates restent cohérents.
- **Portée :** cette règle décrit un test grandeur nature ; elle n'ajoute pas une
  fonctionnalité au produit.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.0 | 16 septembre 2026 | Première validation détaillée de l'admissibilité, des doublons, catégories, localisations, statuts, recherches, clics, dates, propositions, contrôles de publication et du parcours pilote des sites. |
