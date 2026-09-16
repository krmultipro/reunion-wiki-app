# Cas de test — Parcours des sites

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Statut | Automatisation en cours |
| Dernière mise à jour | 16 septembre 2026 |
| Périmètre | MVP — annuaire des sites |

## Signification des identifiants

- **RM** signifie **Règle Métier** et désigne une règle du catalogue général.
- **RM-SITE** signifie **Règle Métier — Site** et désigne une précision propre
  à l'annuaire des sites.
- **TC-SITE** signifie **Test Case — Site** et identifie un cas de test du
  parcours des sites.

Une règle décrit le comportement attendu. Un cas de test décrit les données à
préparer, l'action à exécuter et le résultat observable qui prouve ce
comportement.

## Convention et exécution

- Chaque cas possède un identifiant stable préfixé par `TC-SITE`.
- Un cas réussit uniquement lorsque tous ses résultats attendus sont observés.
- Une règle ne passe au statut **Testée** que lorsque tous ses cas obligatoires
  sont automatisés ou exécutés manuellement avec succès.
- Une évolution d'une règle entraîne la révision des cas associés.
- Les cas critiques sont automatisés avant les cas de priorité haute.

## Préconditions techniques communes

- Une base de test isolée peut être remise dans un état connu.
- Un compte administrateur et un visiteur non authentifié sont disponibles.
- Des catégories et des communes de test existent.
- Un serveur HTTP simulé peut produire des réponses `2xx`, `3xx`, `4xx`, `5xx`,
  des délais dépassés, des redirections et un certificat invalide.
- L'adresse technique, le `User-Agent` et l'horloge peuvent être contrôlés pour
  tester les clics et les dates sans attendre réellement 30 minutes.
- Les emails, URL, noms de domaine et sites utilisés sont réservés aux tests.

## Fiche de test 1 — Proposition, statuts et visibilité

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-07, RM-08, RM-22 à RM-27 et RM-SITE-006 |
| Priorité | Critique |
| Type recommandé | Service et intégration |
| État | À automatiser |

### Objectif

Vérifier l'état initial des sites, les transitions autorisées et l'invisibilité
de tout site qui n'est pas publié.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-006-01 | Aucun site correspondant n'existe. | Un visiteur envoie une proposition valide. | Le site est créé avec le statut `pending`, reste invisible publiquement et apparaît dans l'administration. |
| TC-SITE-006-02 | Une proposition possède le statut `pending`. | L'administrateur corrige ses données sans prendre de décision. | Les corrections sont enregistrées et le statut reste `pending`. |
| TC-SITE-006-03 | Un site se trouve successivement dans chacun des états de départ autorisés. | L'administrateur applique `draft` → `published` ou `archived`, `pending` → `published` ou `refused`, `published` → `archived`, `refused` → `pending` et `archived` → `published`. | Chaque transition autorisée réussit et produit exactement le statut demandé. |
| TC-SITE-006-04 | Un site possède un statut incompatible avec la transition demandée. | L'administrateur tente notamment `published` → `refused`, `pending` → `archived` ou `refused` → `published`. | La transition est refusée, un message explicite est affiché et le statut précédent est conservé. |
| TC-SITE-006-05 | Cinq sites possèdent respectivement les statuts `draft`, `pending`, `published`, `refused` et `archived`. | Un visiteur consulte les listes, la recherche et les URL de détail. | Seul le site `published` est visible ; les quatre autres restent consultables dans l'administration. |
| TC-SITE-006-06 | Une proposition publique est valide. | Aucun administrateur n'intervient. | Elle ne devient jamais automatiquement `published`. |
| TC-SITE-006-07 | Un administrateur crée directement un site. | Il demande le statut `published`. | La publication directe ne réussit que si tous les contrôles métier de la fiche 2 et de la fiche 4 passent. |

### Condition de validation de la fiche 1

Les sept cas doivent passer et aucune route publique ne doit révéler un site non
publié.

## Fiche de test 2 — Admissibilité et contrôles de publication

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-01, RM-02, RM-23 et RM-SITE-001, RM-SITE-002, RM-SITE-011 |
| Priorité | Critique |
| Type recommandé | Formulaire, service et intégration |
| État | Partiellement automatisée : 7 réussis, 1 ignoré |

### Objectif

Vérifier les quatre données obligatoires, le contrôle éditorial du lien avec La
Réunion et l'impossibilité de publier un site invalide.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-PUB-01 | Un site ne possède pas de nom. | Une proposition est envoyée ou une publication est demandée. | L'action est refusée avec une erreur sur le nom. |
| TC-SITE-PUB-02 | Un site possède une URL absente ou syntaxiquement invalide. | Une proposition est envoyée ou une publication est demandée. | L'action est refusée avec une erreur sur l'URL. |
| TC-SITE-PUB-03 | Un site ne possède pas de description neutre. | Une proposition est envoyée ou une publication est demandée. | L'action est refusée avec une erreur sur la description. |
| TC-SITE-PUB-04 | Un site ne possède pas de catégorie principale valide. | Une proposition est envoyée ou une publication est demandée. | L'action est refusée avec une erreur sur la catégorie. |
| TC-SITE-PUB-05 | Les quatre champs obligatoires sont valides et les champs facultatifs sont vides. | Le visiteur propose le site. | La proposition est enregistrée en `pending` ; l'absence de commune, de justification, de preuve et d'email ne la bloque pas. |
| TC-SITE-PUB-06 | Un site national ne possède aucune section, offre ni utilité particulière pour La Réunion. | L'administrateur examine puis tente de publier le site. | La publication est refusée pour absence de lien réel avec La Réunion. |
| TC-SITE-PUB-07 | Un site répond à au moins un critère d'admissibilité et tous les autres contrôles passent. | L'administrateur confirme le lien réunionnais et publie le site. | Le statut devient `published`. La justification et l'éventuelle preuve restent privées. |
| TC-SITE-PUB-08 | Un site contient un contenu manifestement illégal, trompeur ou dangereux. | Une publication est demandée. | La publication est refusée et le site reste `draft` ou `pending`. |

### Condition de validation de la fiche 2

Les huit cas doivent passer. Une erreur de publication ne doit supprimer aucune
donnée déjà enregistrée dans le brouillon ou la proposition.

### Exécution automatisée du 16 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_publication`
- **Résultat :** sept cas réussis et un cas ignoré.
- **Cas ignoré :** `TC-SITE-PUB-06`, car le lien réel avec La Réunion relève
  encore d'un jugement éditorial sans mécanisme de confirmation représenté
  dans l'application.
- **Conséquence :** la fiche 2 reste partiellement automatisée et les règles
  correspondantes ne passent pas encore au statut **Testée**.

## Fiche de test 3 — Normalisation des URL et doublons

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-03, RM-28 et RM-SITE-003 |
| Priorité | Critique |
| Type recommandé | Unitaire, service et intégration |
| État | À automatiser |

### Objectif

Vérifier que les URL équivalentes sont détectées sans bloquer deux services
réellement distincts d'un même domaine.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-003-01 | Une URL de référence existe. | La même URL est proposée avec des majuscules dans le domaine, un port standard ou un `/` final. | La nouvelle URL est reconnue comme un doublon exact et refusée. |
| TC-SITE-003-02 | Une URL de référence existe. | La variante HTTP ou HTTPS possède le même domaine et le même chemin. | Elle est reconnue comme équivalente ; HTTPS est conservé lorsqu'il fonctionne. |
| TC-SITE-003-03 | Une URL contient `utm_*`, `fbclid`, `gclid` ou un fragment `#...`. | Elle est normalisée puis comparée. | Les paramètres publicitaires et le fragment sont retirés avant la comparaison. |
| TC-SITE-003-04 | Une URL contient un paramètre nécessaire au fonctionnement de la page. | Elle est normalisée. | Le paramètre fonctionnel est conservé. |
| TC-SITE-003-05 | Deux URL ne diffèrent que par la casse du chemin. | Elles sont comparées. | Elles ne sont pas fusionnées automatiquement et un contrôle administrateur reste possible. |
| TC-SITE-003-06 | `www.exemple.re` redirige réellement vers `exemple.re`. | Les deux variantes sont proposées. | Elles sont considérées comme équivalentes. |
| TC-SITE-003-07 | Les variantes avec et sans `www` ne redirigent pas l'une vers l'autre. | La seconde variante est proposée. | Elle n'est pas bloquée automatiquement ; un avertissement est affiché à l'administrateur. |
| TC-SITE-003-08 | Un domaine existe déjà avec un premier chemin. | Une URL normalisée différente du même domaine représente un autre service. | L'enregistrement reste possible après un avertissement administrateur. |
| TC-SITE-003-09 | Une URL redirige vers une destination HTTPS valide. | L'administrateur choisit de conserver la destination finale. | L'URL finale est enregistrée et l'URL proposée reste dans l'historique privé. |
| TC-SITE-003-10 | Un doublon exact est soumis successivement par le formulaire public, la création admin et la modification d'une URL. | Chaque opération est exécutée. | Le doublon est détecté et bloqué dans les trois parcours. |

### Condition de validation de la fiche 3

Les dix cas doivent passer avec une fonction de normalisation commune aux trois
parcours d'enregistrement.

## Fiche de test 4 — Accessibilité HTTP

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-01 et RM-SITE-011 |
| Priorité | Critique |
| Type recommandé | Service avec serveur HTTP simulé |
| État | À automatiser |

### Objectif

Vérifier que le contrôle d'accessibilité produit une décision déterministe sans
refuser définitivement un site victime d'une erreur temporaire.

| Cas | Réponse simulée | Résultat attendu |
| --- | --- | --- |
| TC-SITE-HTTP-01 | Réponse finale `2xx`. | Le contrôle automatique d'accessibilité réussit. |
| TC-SITE-HTTP-02 | Une à cinq redirections suivies d'une réponse `2xx`. | Les redirections sont suivies et le contrôle réussit. |
| TC-SITE-HTTP-03 | Plus de cinq redirections ou une boucle. | Le contrôle automatique échoue et la publication est bloquée. |
| TC-SITE-HTTP-04 | Réponse `404` ou `410`. | Le site est considéré comme inaccessible. |
| TC-SITE-HTTP-05 | Réponse `401` ou `403`. | Le système demande une vérification manuelle sans refuser automatiquement le site. |
| TC-SITE-HTTP-06 | Réponse `429`, erreur `5xx` ou délai dépassé. | Le problème est déclaré temporaire et le site reste `draft` ou `pending` pour un nouveau contrôle. |
| TC-SITE-HTTP-07 | Certificat HTTPS invalide. | La publication reste bloquée jusqu'à vérification. |

### Condition de validation de la fiche 4

Les sept cas doivent passer sans dépendre d'un site tiers réel ni du réseau de
production.

## Fiche de test 5 — Recherche, filtres et résultats publics

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-10 à RM-14 et RM-SITE-007 |
| Priorité | Haute |
| Type recommandé | Repository, service et intégration publique |
| État | À automatiser |

### Objectif

Vérifier la recherche normalisée, les filtres combinables, le classement et
l'exclusion des sites non publiés.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-007-01 | Un site publié contient le terme `Réunion`. | Le visiteur recherche `REUNION`, `Réunion` puis `reunion`. | Les trois recherches retrouvent le même site. |
| TC-SITE-007-02 | Plusieurs sites contiennent tout ou partie de `restaurant créole`. | Le visiteur inverse l'ordre des mots. | L'ordre des mots ne change pas l'ensemble pertinent et les correspondances les plus complètes arrivent en premier. |
| TC-SITE-007-03 | Un site publié contient `restaurant`. | Le visiteur recherche `restau`. | Le site apparaît grâce à la correspondance partielle. |
| TC-SITE-007-04 | Un site contient un mot proche, mais pas identique, à une faute de saisie. | Le visiteur recherche le mot mal orthographié. | Aucune correction automatique n'est appliquée dans le MVP. |
| TC-SITE-007-05 | Plusieurs sites couvrent différentes catégories, communes et portées. | Le visiteur combine texte, catégorie, commune ou portée. | Seuls les sites satisfaisant simultanément les critères actifs apparaissent. |
| TC-SITE-007-06 | Des sites correspondants existent dans tous les statuts. | Le visiteur effectue une recherche et applique des filtres. | Seuls les sites `published` apparaissent. |
| TC-SITE-007-07 | Aucun site publié ne correspond. | Le visiteur lance la recherche. | Un message clair, une réinitialisation, des catégories proches et le lien de proposition sont affichés. |
| TC-SITE-007-08 | Plusieurs résultats publiés existent. | Le visiteur choisit pertinence, popularité, nouveautés puis ordre alphabétique. | Chaque tri produit l'ordre attendu et la pertinence reste le tri par défaut. |

### Condition de validation de la fiche 5

Les huit cas doivent passer sur les listes et la recherche publique sans fuite
d'un statut privé.

## Fiche de test 6 — Clics et tendances

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-15 à RM-19, RM-69 et RM-SITE-008 |
| Priorité | Haute |
| Type recommandé | Service, intégration et horloge contrôlée |
| État | À automatiser |

### Objectif

Vérifier qu'un clic admissible est compté une fois, que les exclusions sont
appliquées et que les indicateurs utilisent les bonnes périodes.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-008-01 | Un site est publié et son compteur vaut zéro. | Un visiteur utilise le lien sortant géré par Réunion Wiki. | Un événement est créé et le compteur passe à un. |
| TC-SITE-008-02 | Le même identifiant technique a déjà cliqué sur le même site. | Un second clic intervient avant 30 minutes. | Aucun nouvel événement ni incrément n'est créé. |
| TC-SITE-008-03 | Le dernier clic admissible date d'au moins 30 minutes. | Le même visiteur clique de nouveau. | Un nouvel événement admissible est créé. |
| TC-SITE-008-04 | Le `User-Agent` correspond à un robot connu. | Le lien est utilisé. | Aucun événement ni incrément n'est créé. |
| TC-SITE-008-05 | Un administrateur est authentifié. | Il clique depuis l'administration, une prévisualisation puis la page publique. | Aucun des trois clics n'est comptabilisé. |
| TC-SITE-008-06 | Le site n'est pas publié. | Une tentative d'accès au lien sortant est effectuée. | Aucun clic n'est comptabilisé. |
| TC-SITE-008-07 | Un événement incorrect existe. | L'administrateur le supprime. | L'événement disparaît et le compteur agrégé est ajusté. |
| TC-SITE-008-08 | Des événements sont répartis sur les 7 derniers jours, les 7 jours précédents et les 30 derniers jours. | Les tendances sont calculées. | La tendance, la progression et la popularité stable utilisent leurs périodes respectives ; un site sans clic reste absent des classements principaux. |
| TC-SITE-008-09 | Un visiteur clique sans cookie publicitaire. | Le second clic survient dans la fenêtre de 30 minutes. | La déduplication côté serveur fonctionne tout de même et l'adresse IP brute n'est pas conservée sans nécessité. |

### Condition de validation de la fiche 6

Les neuf cas doivent passer avec une horloge et des identifiants techniques
contrôlés par le test.

## Fiche de test 7 — Dates et nouvelle publication

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-20, RM-21 et RM-SITE-009 |
| Priorité | Haute |
| Type recommandé | Service, intégration et horloge contrôlée |
| État | À automatiser |

### Objectif

Vérifier la séparation des dates métier et le caractère volontaire d'une
nouvelle publication.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-009-01 | Une proposition publique vient d'être créée. | Les dates sont consultées. | `submitted_at` est renseignée ; aucune date de publication n'est inventée. |
| TC-SITE-009-02 | Un site est publié pour la première fois. | La publication réussit. | `first_published_at` et `published_at` reçoivent la même date. |
| TC-SITE-009-03 | Un site publié est corrigé. | L'administrateur enregistre la modification. | `updated_at` change, tandis que `first_published_at` et `published_at` restent inchangées. |
| TC-SITE-009-04 | Un site archivé est republié sans option particulière. | L'administrateur confirme la republication. | L'option « nouvelle publication » est désactivée par défaut et `published_at` reste inchangée. |
| TC-SITE-009-05 | Un site archivé est republié avec l'option explicite. | L'administrateur choisit « Traiter comme une nouvelle publication ». | `published_at` est actualisée, `first_published_at` reste inchangée et le site réapparaît dans les nouveautés. |
| TC-SITE-009-06 | Un site possède déjà des clics et un historique. | Il est traité comme une nouvelle publication. | Les clics et l'historique sont conservés ; l'action, sa date et l'administrateur sont tracés. |
| TC-SITE-009-07 | Plusieurs sites possèdent des dates métier différentes. | La page des nouveautés est consultée. | L'ordre dépend uniquement de `published_at` décroissant. |

### Condition de validation de la fiche 7

Les sept cas doivent passer avec une horloge contrôlée. Aucun simple
désarchivage ne doit artificiellement faire remonter un site dans les nouveautés.

## Fiche de test 8 — Parcours pilote grandeur nature

| Propriété | Valeur |
| --- | --- |
| Règle couverte | RM-SITE-012 |
| Priorité | Critique avant mise en production |
| Type recommandé | Fonctionnel de bout en bout, principalement manuel au départ |
| État | À exécuter |

### TC-SITE-012-01 — Site réel complet

- **Situation initiale :** un vrai site réunionnais actif, simple à vérifier,
  est choisi avec une catégorie et une commune évidentes.
- **Action :** exécuter successivement la proposition publique, la détection de
  doublon, l'enregistrement en attente, la modération, une correction, la
  publication, l'affichage dans sa catégorie, la recherche, le clic sortant,
  les nouveautés, l'archivage et la vérification de sa disparition publique.
- **Résultats attendus :**
  - aucune modification manuelle de la base de données n'est nécessaire ;
  - chaque statut et chaque date suivent les règles précédentes ;
  - le clic admissible est compté exactement une fois ;
  - le site archivé disparaît de tous les espaces publics sans perdre son
    historique administratif.

### Condition de validation de la fiche 8

Le parcours est réussi lorsque toutes les observations sont consignées avec la
date, l'environnement, la personne ayant exécuté le test et les éventuelles
anomalies.

## Ordre d'automatisation recommandé

1. Fiche 2 — contrôles de publication.
2. Fiche 1 — statuts et visibilité.
3. Fiche 3 — normalisation et doublons.
4. Fiche 4 — accessibilité HTTP.
5. Fiche 7 — dates et nouvelle publication.
6. Fiche 6 — clics et tendances.
7. Fiche 5 — recherche et filtres.
8. Fiche 8 — parcours pilote complet.

## Suivi d'exécution

| Fiche | Nombre de cas | État initial |
| --- | ---: | --- |
| 1 — Proposition, statuts et visibilité | 7 | À automatiser |
| 2 — Admissibilité et publication | 8 | 7 réussis, 1 ignoré |
| 3 — URL et doublons | 10 | À automatiser |
| 4 — Accessibilité HTTP | 7 | À automatiser |
| 5 — Recherche et filtres | 8 | À automatiser |
| 6 — Clics et tendances | 9 | À automatiser |
| 7 — Dates et nouvelle publication | 7 | À automatiser |
| 8 — Parcours pilote | 1 | À exécuter |
| **Total** | **57** | **Non exécuté** |

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.1 | 16 septembre 2026 | Automatisation de la fiche 2 : sept cas réussis et `TC-SITE-PUB-06` ignoré en attente d'un mécanisme de confirmation éditoriale. |
| 1.0 | 16 septembre 2026 | Création des 57 cas prioritaires à partir des règles validées `RM-SITE-001` à `RM-SITE-012`. |
