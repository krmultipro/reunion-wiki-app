# Guide de reprise — Tests Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version | 3.10 |
| Statut | Actif |
| Dernière mise à jour | 26 octobre 2026 |
| Branche de travail | `codex/site-submission-hardening-20261026` (backend isolé, non fusionné) |

## Objectif

Ce document permet de reprendre rapidement le travail sur les tests dans une
nouvelle conversation ou après une interruption. Il résume les sources de
vérité, l'environnement de test, l'état actuel et l'ordre recommandé pour la
suite.

Le bilan du durcissement local du 26 octobre est disponible dans
[`SITE_SUBMISSION_CORRECTIONS_2026-10-26.md`](../development/SITE_SUBMISSION_CORRECTIONS_2026-10-26.md).
Le bilan historique des fiches de septembre est disponible dans
[`TEST_REPORT_2026-09-22.md`](TEST_REPORT_2026-09-22.md).
Le parcours pilote assisté est consigné dans
[`SITE_PILOT_REPORT_2026-09-22.md`](SITE_PILOT_REPORT_2026-09-22.md).
La couverture de toute l'application et les chantiers manquants sont suivis
dans [`GLOBAL_TEST_STRATEGY.md`](GLOBAL_TEST_STRATEGY.md).
L'état précis de la navigation de l'administration est consigné dans
[`ADMIN_NAVIGATION_AUDIT_2026-09-24.md`](ADMIN_NAVIGATION_AUDIT_2026-09-24.md).
Les comportements attendus et leur automatisation sont définis dans
[`ADMIN_NAVIGATION_TEST_CASES.md`](ADMIN_NAVIGATION_TEST_CASES.md).

## Sources de vérité

Lire les documents dans cet ordre :

1. [`GLOBAL_TEST_STRATEGY.md`](GLOBAL_TEST_STRATEGY.md) pour la carte globale,
   les risques et l'ordre des prochains chantiers ;
2. [`../development/AGENTS.md`](../development/AGENTS.md) pour l'architecture,
   les responsabilités des couches et les vérifications attendues ;
3. [`../BUSINESS_RULES.md`](../BUSINESS_RULES.md) pour les conventions générales
   et l'historique des règles ;
4. [`../business-rules/RULES_CATALOG.md`](../business-rules/RULES_CATALOG.md)
   pour les identifiants `RM` et les états d'implémentation ;
5. [`../business-rules/SITE_RULES.md`](../business-rules/SITE_RULES.md) pour les
   décisions détaillées `RM-SITE` ;
6. [`SITE_TEST_CASES.md`](SITE_TEST_CASES.md) pour les 67 cas fonctionnels des
   sites ;
7. [`../../tests/test_site_publication.py`](../../tests/test_site_publication.py)
   [`../../tests/test_site_lifecycle.py`](../../tests/test_site_lifecycle.py) et
   [`../../tests/test_site_url_normalization.py`](../../tests/test_site_url_normalization.py)
   [`../../tests/test_site_http_accessibility.py`](../../tests/test_site_http_accessibility.py)
   [`../../tests/test_site_publication_dates.py`](../../tests/test_site_publication_dates.py)
   [`../../tests/test_site_clicks_and_trends.py`](../../tests/test_site_clicks_and_trends.py)
   [`../../tests/test_site_search.py`](../../tests/test_site_search.py) et
   [`../../tests/test_site_pilot_journey.py`](../../tests/test_site_pilot_journey.py)
   pour les automatisations exécutables des huit fiches et de l'extension 6B.

Une règle métier décrit ce que l'application doit respecter. Un cas `TC-SITE`
décrit comment le vérifier. Le fichier Python transforme ce cas en vérification
répétable.

## Carte des points d'entrée du code

Un agent qui automatise une fiche doit commencer par les fichiers correspondant
au comportement testé, sans parcourir tout le dépôt au hasard :

| Fichier | Rôle pour les tests des sites |
| --- | --- |
| [`../../reunion_wiki/app.py`](../../reunion_wiki/app.py) | Création et configuration de l'application Flask importée par les tests. |
| [`../../reunion_wiki/forms/site_forms.py`](../../reunion_wiki/forms/site_forms.py) | Validation des formulaires publics et administratifs des sites. |
| [`../../reunion_wiki/services/site_location_service.py`](../../reunion_wiki/services/site_location_service.py) | Validation du choix exclusif entre commune et portée explicite. |
| [`../../reunion_wiki/routes/public.py`](../../reunion_wiki/routes/public.py) | Proposition publique, recherche et routes visibles par les visiteurs. |
| [`../../reunion_wiki/routes/admin.py`](../../reunion_wiki/routes/admin.py) | Création administrative, modification et modération des propositions. |
| [`../../reunion_wiki/services/site_service.py`](../../reunion_wiki/services/site_service.py) | Logique applicative de lecture actuellement extraite pour les sites. |
| [`../../reunion_wiki/repositories/site_repository.py`](../../reunion_wiki/repositories/site_repository.py) | Accès SQLite, statuts et requêtes de visibilité. |
| [`../../reunion_wiki/db.py`](../../reunion_wiki/db.py) | Ouverture des connexions à partir de `DATABASE_PATH`. |

Les huit fiches possèdent maintenant un point d'entrée dans la suite. Le
parcours pilote de la fiche 8 a été validé par une exécution réelle et son point
d'entrée `unittest` reste volontairement ignoré. Toute nouvelle règle
applicative devra vivre dans un service, conformément à
`development/AGENTS.md`.

## État actuel

| Élément | État |
| --- | --- |
| Cas fonctionnels définis pour les sites | 67 répartis dans 8 fiches et l'extension 6B |
| Fiches représentées dans la suite | Fiches 1 à 8 et 6B |
| Tests exécutables découverts | 103 |
| Tests réussis | 102 |
| Tests ignorés | 1 |
| Échecs attendus confirmés | 0 |
| Règles entièrement marquées `Testée` | RM-03, RM-06, RM-20, RM-21 et RM-28 |

Les lots automatisés sont techniquement concluants : la suite utilise une base
isolée et vérifie réellement les formulaires, les écritures, la correction sans
transition, la visibilité publique et la conservation des paramètres d'URL
fonctionnels. Les fiches 1, 2 et 3 sont désormais entièrement automatisées.

Les 24 régressions ajoutées le 26 octobre couvrent revue HTTP périmée, données
stockées invalides, concurrence des URL et motifs privés de refus. Les 31 tests
des scripts passent séparément. Ces chiffres concernent la branche isolée,
pas main ni la production ; les anciens rapports conservent leurs résultats.

## Exécution

Depuis la racine du dépôt et sur la branche `test` :

```bash
git status --short --branch
```

La première ligne doit commencer par `## test`. Ensuite, exécuter :

```bash
.venv/bin/python -m unittest discover -v
```

Vérification de syntaxe recommandée après une modification :

```bash
.venv/bin/python -m compileall -q reunion_wiki tests
```

Le résultat de référence est actuellement :

```text
Ran 73 tests
OK (skipped=1)
```

## Contrôles avant déploiement dev — 17 octobre 2026

Premier ajout du 17 octobre (historique, complété par le renforcement ci-dessous) :

```bash
.venv/bin/python -m compileall -q app.py migrate.py reunion_wiki tests
.venv/bin/python -m unittest discover -s tests -v
```

La découverte est explicitement limitée à `tests/` pour contrôler l'application
sans lancer les suites du monitoring. Un interpréteur absent, une erreur de
syntaxe, une dépendance manquante ou un échec de test bloque le déploiement.
Les tests explicitement ignorés restent visibles dans le bilan `unittest`.
La procédure et les critères sont conservés dans
[`VPS_DEV_ROUTING.md`](../development/VPS_DEV_ROUTING.md#déploiement-de-la-branche-test).
La réussite de ces contrôles ne couvre pas les parcours sans tests ni le rendu
visuel ; les contrôles du conteneur sur le VPS restent nécessaires.

Vérification locale le 17 octobre 2026 : syntaxe valide, 79 tests exécutés,
78 réussis et 1 ignoré. Les cas de blocage et la poursuite après succès ont
aussi été vérifiés avec les commandes réseau simulées ; aucun déploiement
n'a été lancé.

### Renforcement du même jour — version exacte et récupération

Les commandes du premier ajout restent l'historique de ce contrôle. Désormais,
le script exige un arbre Git propre et teste une copie isolée du commit avec :

```bash
.venv/bin/python -m compileall -q app.py migrate.py reunion_wiki tests script
.venv/bin/python script/run_app_tests.py
```

Le runner conserve la suite `tests/` mais refuse zéro test. Le script lance
ces commandes depuis la copie temporaire avec l'interpréteur local ; les
chemins de base/uploads sont temporaires et les emails désactivés. La même
suite est lancée dans l'image Docker candidate sans réseau, secrets serveur
ni données actives, avant arrêt du service dev.

Pour les régressions des outils de déploiement, exécuter séparément :

```bash
.venv/bin/python -m unittest discover -s script/tests -v
```

Cette suite utilise des dépôts et bases temporaires, du WAL réel et des
commandes SSH/Docker simulées. Elle ne déploie aucun service. Les contrôles
HTTP incluent recherche, formulaire admin anonyme et image ; ils ne couvrent
ni la connexion admin authentifiée ni le rendu visuel. Bilan local : 31 tests
scripts réussis ; suite applicative : 78 réussis, 1 ignoré. Dans l'image Python
3.10 : mêmes résultats applicatifs, 12 tests SQLite/smoke réussis et contrôle
HTTP réel Gunicorn sur une base synthétique migrée. Le cycle distant complet
Compose/Nginx reste vérifié par simulation seulement. Voir les preuves et
limites dans [`VPS_DEV_ROUTING.md`](../development/VPS_DEV_ROUTING.md).

## Isolation technique

Les classes d'intégration `SitePublicationTestCase`, `SiteLifecycleTestCase` et
`SiteHttpAccessibilityTestCase` :

- créent une base SQLite temporaire pour chaque test ;
- créent uniquement les tables et données nécessaires au scénario ;
- remplacent temporairement `DATABASE_PATH` ;
- désactivent CSRF, la limitation de débit et les emails pendant le test ;
- restaurent la configuration Flask à la fin ;
- ne lisent ni ne modifient `data/base.db`, `data_dev/base.db` ou une base de
  production.

Les tests utilisent `unittest`, inclus dans Python. Aucune dépendance de test
supplémentaire n'est nécessaire pour ces lots.

## Limites connues

### TC-SITE-012-01 — Parcours pilote réel

Le parcours complet a été exécuté sur l'accueil officiel de la mairie de
Saint-Joseph, depuis la proposition jusqu'à l'archivage, avec contrôle
d'affichage sur deux tailles de fenêtre. Le propriétaire du projet a retenu
cette URL après un premier essai sur un article archivé. Le test automatique
reste ignoré car il ne peut pas reproduire une vérification réelle du site.

### TC-SITE-007 — Recherche publique validée

La recherche neutralise la casse et les accents, traite chaque terme
indépendamment de son ordre, accepte les correspondances partielles et exclut
les statuts privés. L'écran vide propose la réinitialisation, les catégories et
la proposition d'un site. Les quatre tris publics fonctionnent ; le tri par
date utilise `published_at`.
Les filtres par catégorie, commune et portée fonctionnent seuls ou ensemble
avec le texte et les tris. Leur changement, comme celui du tri, actualise
automatiquement les résultats tout en conservant les critères actifs dans
l'URL. « Toute La Réunion » et « En ligne » sont des choix explicites ; une
commune vide reste « Non précisée ». La migration ajoute `location_scope` aux
sites existants sans inférer une portée. Ce filtre ne dépend pas de GeoIP.

#### Tri par date et données historiques

Le tri « Plus récents » utilise `published_at`. La fiche 7 a ajouté
`submitted_at`, `first_published_at`, `published_at` et `updated_at`.
Une correction ou une republication normale conserve `published_at` ;
seule la nouvelle publication explicite l'actualise. Pour les anciens sites
publiés, `date_ajout` est reprise comme estimation de `published_at` et sa
provenance est enregistrée dans `site_publication_date_inference`.
`first_published_at` reste vide quand sa date réelle est inconnue.

### TC-SITE-008-05, 08 et 09 — Écarts corrigés

Ces trois cas passent désormais : les clics administrateur sont exclus, les
sites sans clic n'apparaissent plus dans les classements et aucune adresse IP
brute n'est conservée. La suppression d'un événement individuel a été remplacée
par une correction d'agrégat auditée.

### TC-SITE-009-01 à 07 — Dates métier validées

Les sept cas passent. Deux tests complémentaires vérifient la migration
idempotente des anciennes dates et le parcours 403 → revue humaine →
nouvelle publication auditée.

### TC-SITE-HTTP-01 à 07 — Contrôle HTTP validé

Les sept cas passent avec un transport simulé sans réseau externe. Le service
classe les réponses, limite les redirections, bloque les destinations réseau
non publiques et conserve les erreurs temporaires en attente. Les réponses
`401` et `403` déclenchent une confirmation humaine liée à l'URL exacte et
auditée avec l'administrateur, la date et une note obligatoire.

### TC-SITE-003-01 à 10 — Normalisation et doublons validés

Les dix cas de la fiche 3 passent. La normalisation gère notamment la casse du
domaine, les ports par défaut, les fragments et les paramètres publicitaires,
tout en conservant la casse du chemin et les paramètres fonctionnels. Les
doublons sont bloqués dans les trois parcours d'écriture ; les variantes
ambiguës produisent un avertissement et l'historique privé conserve l'URL
proposée lorsque cela est nécessaire.

### TC-SITE-006-03, 04 et 07 — Cycle de vie

Le service de cycle de vie contrôle les transitions autorisées et interdites.
Les statuts historiques `en_attente`, `valide` et `refuse` restent utilisés en
base ; `draft` et `archived` complètent le parcours. Les cas 03 et 04 passent.
Le cas 07 vérifie la création directe de bout en bout : contrôles de formulaire,
revue éditoriale, réponse HTTP simulée et visibilité publique après publication.

### TC-SITE-PUB-06 — Lien réel avec La Réunion

La machine ne peut pas décider seule si un site national possède une utilité
réelle pour La Réunion. L'administrateur choisit explicitement un critère
d'admissibilité ou constate l'absence de lien. La décision privée est liée à
l'URL examinée et le repository bloque toute publication sans confirmation
positive courante. Le cas vérifie ce verrou ; la qualité du jugement humain
reste à contrôler pendant la revue éditoriale réelle.

### Portée des tests réussis

Les tests réussis confirment les contrôles techniques existants : champs
obligatoires, URL syntaxiquement valide, proposition en attente, correction
sans publication, invisibilité des sites non publiés, création administrative
et rejet d'un motif dangereux explicite. Ils ne prouvent pas à eux seuls la
neutralité éditoriale d'un texte, l'accessibilité HTTP réelle ou la pertinence
réunionnaise du site.

### Avertissement Python existant

La soumission publique déclenche un avertissement de dépréciation sur
`datetime.utcnow()`. Il ne fait pas échouer les tests et n'a pas été corrigé
pendant l'automatisation afin de ne pas mélanger test et modification
fonctionnelle.

## Méthode pour automatiser une nouvelle fiche

1. Lire toutes les règles `RM` et `RM-SITE` couvertes par la fiche.
2. Exécuter la suite existante pour obtenir un état de référence.
3. Identifier ce qui est déterministe et ce qui relève d'un jugement humain.
4. Préparer uniquement les données nécessaires dans la base temporaire.
5. Écrire un test par identifiant `TC-SITE`, sans modifier sa signification.
6. Exécuter la fiche seule, puis toute la suite.
7. Ne pas implémenter une fonctionnalité manquante sauf demande explicite.
8. Utiliser un test ignoré avec une raison précise lorsqu'un prérequis produit
   manque réellement.
9. Mettre à jour `SITE_TEST_CASES.md` avec le résultat observé.
10. Marquer une règle **Testée** uniquement lorsque tous ses cas obligatoires
    passent.

## Suite recommandée

Les 67 cas possèdent désormais un test ou un point d'entrée documenté. La suite
du travail consiste à implémenter les prérequis absents, puis à exécuter
humainement le parcours pilote.

## Contexte à copier dans une nouvelle conversation

```text
Je travaille sur Réunion Wiki, sur la branche `test`.

Lis d'abord :
- docs/testing/README.md
- docs/development/AGENTS.md
- docs/BUSINESS_RULES.md
- docs/business-rules/RULES_CATALOG.md
- docs/business-rules/SITE_RULES.md
- docs/testing/SITE_TEST_CASES.md
- tests/test_site_publication.py
- tests/test_site_lifecycle.py
- tests/test_site_url_normalization.py
- tests/test_site_http_accessibility.py
- tests/test_site_publication_dates.py
- tests/test_site_clicks_and_trends.py
- tests/test_site_search.py
- tests/test_site_pilot_journey.py
- tests/test_site_geographic_privacy.py

Les huit fiches et l'extension 6B possèdent 73 tests : 72 passent et 1 est
ignoré. Les fiches 1 et 2 sont validées ; la fiche 3 est
entièrement positive ; les fiches 4 et 7 sont validées. La fiche 6 et l'extension 6B sont
désormais entièrement positives. Les neuf cas de la fiche 5 passent ; deux
tests complémentaires vérifient l'enregistrement et la migration de la portée.
La fiche 8 est validée par le parcours réel consigné dans son rapport ; son
point d'entrée `unittest` reste ignoré.
Les tests utilisent
unittest et des bases SQLite temporaires lorsque le scénario écrit en base.

Exécute d'abord `.venv/bin/python -m unittest discover -v`. Corrige ensuite un
prérequis ou un écart documenté sans modifier la signification des cas, puis
active les tests concernés et mets à jour les résultats réels.
```

## À reprendre plus tard — base GeoIP locale

La carte et la répartition réelle par zone sont volontairement reportées. Le
comptage privé fonctionne déjà, mais les visiteurs restent classés `Inconnu`
tant qu'aucune base locale n'est configurée.

Pour reprendre ce chantier :

1. télécharger `GeoLite2-City.mmdb` depuis un compte MaxMind GeoLite ;
2. placer le fichier dans `data/geoip/GeoLite2-City.mmdb` sans le versionner ;
3. installer les dépendances de `requirements.txt` ;
4. définir `GEOIP_DATABASE_PATH=data/geoip/GeoLite2-City.mmdb` dans `.env` ;
5. transmettre `/data/geoip/GeoLite2-City.mmdb` au conteneur Docker ;
6. vérifier les six zones puis prévoir la mise à jour régulière de la base.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 3.10 | 26 octobre 2026 | Quatre corrections de soumission/publication, 103 tests applicatifs (1 ignoré), 31 tests de scripts ; intégration main différée pour réconciliation #42. |
| 3.9 | 17 octobre 2026 | Renforcement documenté avant code : commit exact, tests image isolés, SQLite WAL, récupération vérifiée et retrait local de l’ancien déploiement automatique de production. |
| 3.8 | 17 octobre 2026 | Ajout des contrôles locaux bloquants avant déploiement dev : syntaxe des points d'entrée et modules, puis suite applicative `tests/`. |
| 3.7 | 24 septembre 2026 | Validation de `TC-ADMIN-NAV-01` à `08`, navbar commune sur les 14 gabarits admin authentifiés et contrôles à 390 px et 1280 px. |
| 3.6 | 24 septembre 2026 | Ajout de l'audit détaillé de la navigation admin, de sa matrice et de ses critères de correction. |
| 3.5 | 24 septembre 2026 | Ajout de la stratégie globale de tests, de la priorisation des familles manquantes et de l'anomalie de navigation de la page Clics. |
| 3.4 | 22 septembre 2026 | Parcours pilote réel validé sur l'accueil officiel de Saint-Joseph ; rapport daté et conservation du point d'entrée manuel ignoré. |
| 3.3 | 22 septembre 2026 | Validation de la fiche 5 : portée explicite des sites, filtre public combinable et migration conservant les choix existants. |
| 3.2 | 22 septembre 2026 | Validation complète de la fiche 1 avec test du parcours de publication directe et de ses blocages éditoriaux et HTTP. |
| 3.1 | 22 septembre 2026 | Validation des transitions de la fiche 1 et ajout du brouillon administratif ; seul le cas de publication directe reste ignoré. |
| 3.0 | 22 septembre 2026 | Validation de la fiche 2 : revue éditoriale explicite, audit privé lié à l'URL et verrou central de publication. |
| 2.9 | 19 septembre 2026 | Validation des sept cas de la fiche 7, migration idempotente et traçabilité des dates historiques estimées. |
| 2.8 | 17 septembre 2026 | Validation des sept contrôles HTTP et de la confirmation manuelle auditée des réponses 401/403. |
| 2.7 | 17 septembre 2026 | Ajout de l'actualisation automatique des filtres et du tri, des critères actifs et des actions de réinitialisation distinctes. |
| 2.6 | 17 septembre 2026 | Ajout des filtres combinables par catégorie et commune ; portée géographique conservée comme sous-cas reporté. |
| 2.5 | 17 septembre 2026 | Ajout des tris publics par pertinence, popularité, date disponible et nom. |
| 2.4 | 17 septembre 2026 | Correction des trois écarts de recherche : accents, ordre des termes et actions sans résultat. |
| 2.3 | 17 septembre 2026 | Validation complète de la fiche 3 et des règles de normalisation et de doublons. |
| 2.2 | 17 septembre 2026 | Report documenté de la carte GeoIP locale et procédure de reprise. |
| 2.1 | 16 septembre 2026 | Validation des neuf tests de confidentialité et correction des trois écarts de clics et tendances. |
| 2.0 | 16 septembre 2026 | Ajout de l'extension 6B sur les statistiques géographiques agrégées et la migration des anciennes IP sans perte de clics. |
| 1.9 | 16 septembre 2026 | Ajout d'un bilan visuel complet séparant réussites, validations humaines, fonctionnalités absentes et écarts confirmés. |
| 1.8 | 16 septembre 2026 | Ajout du point d'entrée de la fiche 8, conservé comme test humain ignoré jusqu'au parcours pilote réel. |
| 1.7 | 16 septembre 2026 | Automatisation de la fiche 5 : trois tests réussis, deux ignorés et trois échecs attendus sur la recherche publique. |
| 1.6 | 16 septembre 2026 | Automatisation de la fiche 6 : six tests réussis et trois échecs attendus documentent des écarts réels du produit. |
| 1.5 | 16 septembre 2026 | Ajout des sept cas de la fiche 7, ignorés tant que les dates métier et la nouvelle publication explicite ne sont pas implémentées. |
| 1.4 | 16 septembre 2026 | Ajout des sept cas de la fiche 4, tous ignorés avec une raison explicite tant que le contrôle HTTP simulable n'existe pas. |
| 1.3 | 16 septembre 2026 | Automatisation partielle de la fiche 3 : un cas réussi confirme la conservation des paramètres fonctionnels et neuf cas ignorés documentent la normalisation et la déduplication manquantes. |
| 1.2 | 16 septembre 2026 | Automatisation partielle de la fiche 1, ajout de quatre tests réussis et de trois cas ignorés documentant les prérequis produit manquants. |
| 1.1 | 16 septembre 2026 | Ajout du guide de développement à la chaîne de lecture et d'une carte des points d'entrée du code nécessaires aux prochaines fiches. |
| 1.0 | 16 septembre 2026 | Création du guide de reprise après l'automatisation partielle de la fiche 2. |


## Refonte DEV — 11 novembre 2026

Voir [preuves et limites](REFONTE_DEV_2026-11-11.md). La recherche simple
commune est à `/recherche` ; les tests avancés existants sont conservés
sur `/recherche-sites`, sans nouveau panneau dans le parcours de maquette.
Les suites ne travaillent que sur des bases jetables.
