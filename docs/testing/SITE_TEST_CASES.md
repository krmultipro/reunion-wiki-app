# Cas de test — Parcours des sites

| Métadonnée | Valeur |
| --- | --- |
| Version | 3.3 |
| Statut | Automatisation en cours |
| Dernière mise à jour | 26 octobre 2026 |
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
| État | Automatisée : 7 réussis |

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

### Exécution automatisée du 16 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_lifecycle`
- **Résultat :** quatre cas réussis et trois cas ignorés.
- **Cas réussis :** `TC-SITE-006-01`, `TC-SITE-006-02`,
  `TC-SITE-006-05` et `TC-SITE-006-06`.
- **Cas ignorés :** `TC-SITE-006-03` et `TC-SITE-006-04`, car les statuts
  `draft` et `archived` ainsi qu'un service validant les transitions ne sont
  pas encore implémentés ; `TC-SITE-006-07`, car la confirmation éditoriale du
  lien réel avec La Réunion n'est pas encore représentée. Le contrôle HTTP de
  la fiche 4 est désormais disponible.
- **Conséquence :** la fiche 1 reste partiellement automatisée et les règles
  correspondantes ne passent pas encore au statut **Testée**.

### Exécution automatisée du 22 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_lifecycle`
- **Résultat :** six cas réussis et un cas ignoré.
- **Cas validés :** `TC-SITE-006-03` couvre les sept transitions autorisées ;
  `TC-SITE-006-04` vérifie les refus depuis l'administration et la conservation
  du statut précédent.
- **Cas restant :** `TC-SITE-006-07` attend le contrôle intégré de la création
  directe avec toutes les validations éditoriales et HTTP.

### Complément du 22 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_lifecycle`
- **Résultat :** sept cas réussis, aucun cas ignoré : la fiche 1 est validée.
- **Cas `TC-SITE-006-07` :** les données invalides empêchent la création ; une
  demande directe de publication crée d'abord un brouillon privé. Un refus
  éditorial, une réponse HTTP `404` ou une erreur temporaire `503` le laissent
  en brouillon. Après confirmation éditoriale et réponse HTTP `200`, le même
  site devient publié et visible dans la recherche et par son lien public.

## Fiche de test 2 — Admissibilité et contrôles de publication

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-01, RM-02, RM-23 et RM-SITE-001, RM-SITE-002, RM-SITE-011 |
| Priorité | Critique |
| Type recommandé | Formulaire, service et intégration |
| État | Automatisée : 8 réussis |

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

### Exécution automatisée du 22 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_publication`
- **Résultat :** huit cas réussis, aucun cas ignoré.
- **Cas `TC-SITE-PUB-06` :** la décision humaine « aucun lien réel constaté »
  bloque la publication. Le service exige une décision positive liée à l'URL
  courante ; un changement d'URL ou une décision négative ultérieure invalide
  une ancienne confirmation. Le test vérifie ce verrou, pas la justesse du
  jugement éditorial lui-même.

## Fiche de test 3 — Normalisation des URL et doublons

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-03, RM-28 et RM-SITE-003 |
| Priorité | Critique |
| Type recommandé | Unitaire, service et intégration |
| État | Automatisée : 10 réussis |

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

### Exécution automatisée du 16 septembre 2026

- **Commande :**
  `.venv/bin/python -m unittest -v tests.test_site_url_normalization`
- **Résultat :** dix cas réussis.
- **Validation :** la même normalisation est appliquée aux formulaires public et
  administrateur ; les doublons sont bloqués dans les trois écritures ; les cas
  ambigus produisent un avertissement et l'historique privé conserve les URL.
- **Conséquence :** les règles `RM-03`, `RM-28` et `RM-SITE-003` sont testées.

## Fiche de test 4 — Accessibilité HTTP

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-01 et RM-SITE-011 |
| Priorité | Critique |
| Type recommandé | Service avec serveur HTTP simulé |
| État | Automatisée : 7 réussis |

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

### Exécution automatisée du 17 septembre 2026

- **Commande :**
  `.venv/bin/python -m unittest -v tests.test_site_http_accessibility`
- **Résultat :** sept cas réussis, sans requête vers un site tiers réel.
- **Validation :** le transport simulé couvre les réponses `2xx`, les
  redirections, les boucles, les erreurs définitives ou temporaires et les
  certificats invalides. Les destinations privées sont bloquées avant toute
  requête.
- **Revue humaine :** une réponse `401` ou `403` conserve le site en attente,
  puis une confirmation distincte avec note obligatoire publie le site et
  conserve l'administrateur, la date et la justification.

## Fiche de test 5 — Recherche, filtres et résultats publics

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-10 à RM-14 et RM-SITE-007 |
| Priorité | Haute |
| Type recommandé | Repository, service et intégration publique |
| État | Automatisée : 9 réussis |

### Objectif

Vérifier la recherche normalisée, les filtres combinables, le classement et
l'exclusion des sites non publiés.

| Cas | Situation initiale | Action | Résultat attendu |
| --- | --- | --- | --- |
| TC-SITE-007-01 | Un site publié contient le terme `Réunion`. | Le visiteur recherche `REUNION`, `Réunion` puis `reunion`. | Les trois recherches retrouvent le même site. |
| TC-SITE-007-02 | Plusieurs sites contiennent tout ou partie de `restaurant créole`. | Le visiteur inverse l'ordre des mots. | L'ordre des mots ne change pas l'ensemble pertinent et les correspondances les plus complètes arrivent en premier. |
| TC-SITE-007-03 | Un site publié contient `restaurant`. | Le visiteur recherche `restau`. | Le site apparaît grâce à la correspondance partielle. |
| TC-SITE-007-04 | Un site contient un mot proche, mais pas identique, à une faute de saisie. | Le visiteur recherche le mot mal orthographié. | Aucune correction automatique n'est appliquée dans le MVP. |
| TC-SITE-007-05A | Plusieurs sites couvrent différentes catégories et communes. | Le visiteur combine texte, catégorie et commune. | Seuls les sites satisfaisant simultanément les critères actifs apparaissent. |
| TC-SITE-007-05B | Plusieurs sites couvrent différentes portées géographiques. | Le visiteur combine texte, catégorie, commune et portée. | La portée complète les autres filtres sans les remplacer. |
| TC-SITE-007-06 | Des sites correspondants existent dans tous les statuts. | Le visiteur effectue une recherche et applique des filtres. | Seuls les sites `published` apparaissent. |
| TC-SITE-007-07 | Aucun site publié ne correspond. | Le visiteur lance la recherche. | Un message clair, une réinitialisation, des catégories proches et le lien de proposition sont affichés. |
| TC-SITE-007-08 | Plusieurs résultats publiés existent. | Le visiteur choisit pertinence, popularité, nouveautés puis ordre alphabétique. | Chaque tri produit l'ordre attendu et la pertinence reste le tri par défaut. |

### Condition de validation de la fiche 5

Les neuf cas doivent passer sur les listes et la recherche publique sans fuite
d'un statut privé.

### Exécution automatisée du 17 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_search`
- **Résultat :** huit cas réussis et un ignoré.
- **Cas réussis :** `TC-SITE-007-01` à `04`, `TC-SITE-007-05A`, `TC-SITE-007-06` et
  `TC-SITE-007-07` à `08`.
- **Cas ignoré :** `TC-SITE-007-05B`, car la portée géographique n'est pas
  encore représentée. Les filtres catégorie et commune sont validés.
- **Interface de `TC-SITE-007-05A` :** les tests vérifient les marqueurs de
  soumission automatique, le compteur « Affiner », les critères actifs et les
  deux actions de réinitialisation. La soumission automatique a aussi été
  vérifiée manuellement dans le navigateur local.
- **Mise à jour du 19 septembre 2026 :** le tri « Plus récents » utilise
  désormais `published_at`. La fiche 7 vérifie aussi que `date_ajout` ne
  détermine plus l'ordre des nouveautés.

### Exécution automatisée du 22 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -q tests.test_site_search`
- **Résultat :** neuf cas de la fiche 5 réussis, aucun cas ignoré ; deux tests
  complémentaires vérifient l'écriture de la portée et la migration legacy.
- **Cas `TC-SITE-007-05B` :** les portées « Avec une commune », « Toute La
  Réunion », « En ligne » et « Non précisée » se combinent avec le texte et la
  catégorie. Une commune et « Toute La Réunion » ne donnent aucun résultat
  contradictoire. Un site non publié reste exclu.
- **Règle `RM-SITE-005` :** sans commune ni portée explicite, le site reste
  « Non précisée ». Les formulaires refusent une commune combinée à une portée.
  La migration ajoute `location_scope` sans déduire « En ligne » d'une commune
  vide et conserve la valeur pendant la reconstruction des anciennes tables.
- **Base GeoIP :** aucune base GeoIP n'est nécessaire ; la portée décrit le
  site, et non la position du visiteur.

## Fiche de test 6 — Clics et tendances

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-15 à RM-19, RM-69 et RM-SITE-008 |
| Priorité | Haute |
| Type recommandé | Service, intégration et horloge contrôlée |
| État | Automatisée : 9 réussis |

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

### Exécution automatisée du 16 septembre 2026

- **Commande :**
  `.venv/bin/python -m unittest -v tests.test_site_clicks_and_trends`
- **Résultat :** neuf cas réussis.
- **Cas réussis :** `TC-SITE-008-01` à `09`.
- **Corrections validées :** les administrateurs sont exclus du comptage, les
  classements ignorent les sites sans clic et la déduplication ne conserve plus
  l'adresse IP brute. La correction des compteurs porte sur les agrégats et
  laisse une trace administrative.

## Fiche de test 6B — Confidentialité et statistiques géographiques

| Propriété | Valeur |
| --- | --- |
| Règle couverte | RM-SITE-008, amendement 1.2 |
| Priorité | Critique |
| Type recommandé | Service, repository, migration et intégration admin |
| État | Automatisée : 9 tests réussis |

### Objectif

Produire des statistiques utiles par grande zone sans conserver d'adresse IP
brute ni exposer de visite individuelle.

| Cas | Résultat attendu |
| --- | --- |
| TC-SITE-GEO-01 | Seules les zones `Nord`, `Sud`, `Est`, `Ouest`, `Hors Réunion` et `Inconnu` sont stockées. |
| TC-SITE-GEO-02 | Aucune adresse IP brute n'est persistée ; seule une empreinte HMAC temporaire est utilisée. |
| TC-SITE-GEO-03 | Une zone comptant moins de 10 visiteurs distincts n'est pas affichée séparément. |
| TC-SITE-GEO-04 | L'administration affiche uniquement des agrégats et aucune visite individuelle. |
| TC-SITE-GEO-05 | Les empreintes de déduplication expirent après 30 minutes et sont purgées sous 24 heures. |
| TC-SITE-GEO-06 | Les agrégats géographiques de plus de 12 mois sont supprimés. |
| TC-SITE-GEO-07 | Les journées statistiques utilisent le fuseau `Indian/Reunion`. |
| TC-SITE-GEO-08 | La migration sauvegarde la base, conserve les compteurs et supprime les anciennes IP de la base active. |
| TC-SITE-GEO-09 | Une correction de compteur agrégé conserve sa date, son auteur et son motif. |

### Exécution automatisée du 16 septembre 2026

- **Commande :**
  `.venv/bin/python -m unittest -v tests.test_site_geographic_privacy`
- **Résultat :** neuf cas réussis sur le stockage agrégé, le seuil de 10, la
  rétention, le fuseau, l'audit et la migration sans IP brute.

## Fiche de test 7 — Dates et nouvelle publication

| Propriété | Valeur |
| --- | --- |
| Règles couvertes | RM-20, RM-21 et RM-SITE-009 |
| Priorité | Haute |
| Type recommandé | Service, intégration et horloge contrôlée |
| État | Automatisée : 7 réussis, 2 tests complémentaires réussis |

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

### Exécution automatisée du 16 septembre 2026

- **Commande :**
  `.venv/bin/python -m unittest -v tests.test_site_publication_dates`
- **Résultat :** sept cas ignorés.
- **Cause :** les sites utilisent uniquement `date_ajout`. Les quatre dates
  métier, le statut archivé, l'option explicite de nouvelle publication et son
  historique ne sont pas représentés.
- **Conséquence :** la fiche est décrite mais bloquée par le schéma et le
  workflow produit. `RM-20`, `RM-21` et `RM-SITE-009` ne passent pas au statut
  **Testée**.

### Exécution automatisée du 19 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_publication_dates`
- **Résultat :** sept cas métier et deux cas complémentaires réussis.
- **Compléments :** migration idempotente et traçabilité d'une date historique
  estimée ; nouvelle publication explicite après vérification HTTP manuelle.
- **Migration :** `date_ajout` peut alimenter le tri des anciens sites, mais
  cette valeur est enregistrée dans `site_publication_date_inference` comme
  estimation, jamais comme première publication certaine.
- **Conséquence :** la fiche 7 passe au statut **Testée**.

## Fiche de test 8 — Parcours pilote grandeur nature

| Propriété | Valeur |
| --- | --- |
| Règle couverte | RM-SITE-012 |
| Priorité | Critique avant mise en production |
| Type recommandé | Fonctionnel de bout en bout, principalement manuel au départ |
| État | Validée par parcours assisté ; 1 point d'entrée automatisé ignoré |

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

### Exécution automatisée du 16 septembre 2026

- **Commande :** `.venv/bin/python -m unittest -v tests.test_site_pilot_journey`
- **Résultat :** un cas ignoré nécessitant une exécution humaine.
- **Cause :** le scénario utilise un vrai site réunionnais, vérifie le contenu
  et l'affichage sur plusieurs appareils, puis parcourt des workflows encore
  partiellement manquants.
- **Reprise :** le test sert de point d'entrée stable. Il devra être exécuté et
  consigné manuellement lorsque les fiches précédentes seront suffisamment
  complètes.

### Parcours assisté du 22 septembre 2026

Le parcours complet sur l'[accueil officiel de Saint-Joseph](https://saintjoseph.re/)
a été exécuté de la proposition à l'archivage, sans écriture directe en base.
Les étapes et observations sont consignées dans
[`SITE_PILOT_REPORT_2026-09-22.md`](SITE_PILOT_REPORT_2026-09-22.md).
Un article archivé a servi de premier essai avant que le propriétaire du projet
choisisse l'accueil de la mairie. Le test automatisé reste ignoré parce qu'un
parcours réel ne peut pas être rejoué comme un test isolé.

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

| Fiche | Nombre de cas | État actuel |
| --- | ---: | --- |
| 1 — Proposition, statuts et visibilité | 7 | 7 réussis |
| 2 — Admissibilité et publication | 8 | 8 réussis |
| 3 — URL et doublons | 10 | 10 réussis |
| 4 — Accessibilité HTTP | 7 | 7 réussis |
| 5 — Recherche et filtres | 9 | 9 réussis (+ 2 compléments) |
| 6 — Clics et tendances | 9 | 9 réussis |
| 6B — Confidentialité géographique | 9 | 9 réussis |
| 7 — Dates et nouvelle publication | 7 | 7 réussis (+ 2 compléments) |
| 8 — Parcours pilote | 1 | 1 parcours réel validé ; point d'entrée automatisé ignoré |
| **Total** | **73** | **72 réussis, 1 ignoré** |

## Régressions complémentaires du 26 octobre 2026

Les critères `COR01-OLD` à `COR04-PRIVATE`, schémas, code associé et résultats
figurent dans le [rapport de correction](../development/SITE_SUBMISSION_CORRECTIONS_2026-10-26.md).
Ils complètent les fiches 1 à 4 sans réécrire les exécutions de septembre :
24 nouveaux tests durables, suite totale de 103 tests dont un pilote manuel
ignoré. Contrôles locaux en branche isolée ; aucun déploiement ni validation
visuelle utilisateur déduits de ces résultats.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 3.3 | 26 octobre 2026 | Ajout des régressions COR01 à COR04 et de leur traçabilité ; résultats locaux distincts des validations historiques. |
| 3.2 | 22 septembre 2026 | Validation assistée de la fiche 8 sur l'accueil de la mairie de Saint-Joseph ; parcours réel consigné séparément. |
| 3.1 | 22 septembre 2026 | Validation du filtre de portée géographique et des quatre états de localisation ; deux contrôles complémentaires couvrent les écritures et la migration. |
| 3.0 | 22 septembre 2026 | Validation complète de la fiche 1 avec le test intégré de création directe, revue éditoriale, contrôle HTTP et visibilité publique. |
| 2.9 | 22 septembre 2026 | Validation des transitions autorisées et interdites de la fiche 1 ; le brouillon administratif est disponible, le test de publication directe reste à compléter. |
| 2.8 | 22 septembre 2026 | Validation de la fiche 2 avec décision éditoriale privée, liée à l'URL et imposée à toute publication. Deux contrôles complémentaires couvrent le verrou du repository et l'invalidation des confirmations. |
| 2.7 | 19 septembre 2026 | Validation de la fiche 7, migration prudente des anciennes dates et republication explicite auditée. |
| 2.6 | 17 septembre 2026 | Validation complète de la fiche 4 avec contrôle HTTP simulable et revue manuelle auditée. |
| 2.5 | 17 septembre 2026 | Couverture de l'actualisation automatique et des actions UX de la recherche filtrée. |
| 2.4 | 17 septembre 2026 | Validation des filtres catégorie et commune ; scission du cas de portée géographique reporté. |
| 2.3 | 17 septembre 2026 | Validation des quatre tris publics ; le filtre géographique reste reporté. |
| 2.2 | 17 septembre 2026 | Validation de la recherche sans accents, multi-termes et de l'écran sans résultat. |
| 2.1 | 17 septembre 2026 | Validation des dix cas de la fiche 3 avec normalisation commune et blocage des doublons. |
| 2.0 | 16 septembre 2026 | Validation complète des fiches 6 et 6B après passage aux statistiques géographiques agrégées. |
| 1.9 | 16 septembre 2026 | Ajout de neuf cas pour les zones agrégées, le seuil de confidentialité, la rétention et la migration sans perte des anciens clics. |
| 1.8 | 16 septembre 2026 | Ajout du point d'entrée automatisé de la fiche 8, ignoré jusqu'à l'exécution humaine du parcours pilote réel. |
| 1.7 | 16 septembre 2026 | Automatisation de la fiche 5 : trois réussites, deux fonctionnalités absentes et trois écarts confirmés. |
| 1.6 | 16 septembre 2026 | Automatisation de la fiche 6 : six cas réussis et trois écarts produit confirmés comme échecs attendus. |
| 1.5 | 16 septembre 2026 | Automatisation bloquée de la fiche 7 : sept cas ignorés en attente des quatre dates métier et du workflow de nouvelle publication. |
| 1.4 | 16 septembre 2026 | Automatisation bloquée de la fiche 4 : sept cas ignorés en attente d'un service simulable de contrôle d'accessibilité HTTP. |
| 1.3 | 16 septembre 2026 | Automatisation partielle de la fiche 3 : un cas réussi et neuf cas ignorés en attente d'une normalisation et d'une détection des doublons communes aux trois parcours. |
| 1.2 | 16 septembre 2026 | Automatisation partielle de la fiche 1 : quatre cas réussis et trois cas ignorés en attente du cycle de vie complet et des contrôles de publication. |
| 1.1 | 16 septembre 2026 | Automatisation de la fiche 2 : sept cas réussis et `TC-SITE-PUB-06` ignoré en attente d'un mécanisme de confirmation éditoriale. |
| 1.0 | 16 septembre 2026 | Création des 57 cas prioritaires à partir des règles validées `RM-SITE-001` à `RM-SITE-012`. |


## Refonte DEV — 11 novembre 2026

Voir [preuves et limites](REFONTE_DEV_2026-11-11.md). La recherche simple
commune est à `/recherche` ; les tests avancés existants sont conservés
sur `/recherche-sites`, sans nouveau panneau dans le parcours de maquette.
Les suites ne travaillent que sur des bases jetables.
