# Bilan visuel des tests des sites — 16 septembre 2026

> Mis à jour le 17 septembre 2026.

## Vue d'ensemble

| Couleur | Signification | Nombre |
| --- | --- | ---: |
| 🟢 | Comportement testé et conforme | **54** |
| 🔵 | Validation humaine nécessaire | **2** |
| 🟠 | Test bloqué par une fonctionnalité produit absente | **11** |
| 🔴 | Test exécuté révélant un écart réel | **0** |
|  | **Total** | **67** |

La suite automatisée reste verte ; les fonctionnalités absentes et les deux
validations humaines sont marquées `skip` :

```text
Ran 67 tests
OK (skipped=13)
```

Les 13 tests ignorés se répartissent entre **11 prérequis produit absents** et
**2 validations humaines**.

## Résultat par fiche

| Fiche | 🟢 | 🔵 | 🟠 | 🔴 | Lecture rapide |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 — Statuts et visibilité | 4 | 0 | 3 | 0 | Le parcours actuel protège bien les propositions, mais le cycle complet manque. |
| 2 — Publication | 7 | 1 | 0 | 0 | Les validations techniques actuelles fonctionnent ; le lien réunionnais reste humain. |
| 3 — URL et doublons | 10 | 0 | 0 | 0 | Normalisation, doublons, avertissements et historique sont validés. |
| 4 — Accessibilité HTTP | 7 | 0 | 0 | 0 | Contrôle simulable, erreurs classées et revue 401/403 auditée. |
| 5 — Recherche et filtres | 8 | 0 | 1 | 0 | Recherche, tris, catégorie et commune conformes ; portée reportée. |
| 6 — Clics et tendances | 9 | 0 | 0 | 0 | Comptage, exclusions, tendances et correction auditée sont conformes. |
| 6B — Confidentialité géographique | 9 | 0 | 0 | 0 | HMAC temporaire, zones agrégées, seuil, rétention et migration sont validés. |
| 7 — Dates métier | 0 | 0 | 7 | 0 | Le modèle à quatre dates et la nouvelle publication n'existent pas encore. |
| 8 — Parcours pilote | 0 | 1 | 0 | 0 | Le parcours réel complet doit être exécuté par une personne. |

## 🟢 Tests positifs — 54

### Fiche 1 — 4

- `TC-SITE-006-01` : une proposition publique devient `en_attente`, reste
  privée et apparaît dans l'administration.
- `TC-SITE-006-02` : une correction conserve le statut en attente.
- `TC-SITE-006-05` : seul un site publié est visible dans les espaces publics.
- `TC-SITE-006-06` : aucune publication automatique n'intervient.

### Fiche 2 — 7

- `TC-SITE-PUB-01` à `05` : nom, URL, description et catégorie obligatoires ;
  champs facultatifs acceptés.
- `TC-SITE-PUB-07` : un site administrateur valide peut être publié.
- `TC-SITE-PUB-08` : un motif dangereux explicite est rejeté.

### Fiche 3 — 10

- `TC-SITE-003-01` à `10` : variantes équivalentes, paramètres publicitaires,
  casse du chemin, `www`, avertissements, destination HTTPS, historique privé
  et blocage dans les trois parcours sont vérifiés.

### Fiche 4 — 7

- `TC-SITE-HTTP-01` à `07` : réponses `2xx`, cinq redirections au maximum,
  boucles, erreurs définitives ou temporaires et certificats invalides sont
  classés sans réseau externe.
- Les URL internes sont bloquées avant la requête. Les réponses `401/403`
  ouvrent une confirmation manuelle liée à l'URL exacte et conservent la note,
  la date et l'administrateur.

### Fiche 5 — 8

- `TC-SITE-007-01` : la recherche ignore la casse et les accents.
- `TC-SITE-007-02` : l'ordre des termes ne change pas les résultats pertinents.
- `TC-SITE-007-03` : la recherche accepte un terme partiel.
- `TC-SITE-007-04` : aucune correction orthographique automatique n'est
  appliquée dans le MVP.
- `TC-SITE-007-05A` : catégorie et commune se combinent entre elles et avec le
  texte recherché.
- `TC-SITE-007-06` : seuls les sites publiés apparaissent dans la recherche.
- `TC-SITE-007-07` : l'écran vide propose réinitialisation, catégories et
  soumission d'un site.
- `TC-SITE-007-08` : les tris par pertinence, popularité, date disponible et
  nom produisent l'ordre attendu.

Le tri par date repose provisoirement sur `date_ajout`. La colonne
`published_at` est reportée à la fiche 7 afin d'être ajoutée avec les trois
autres dates métier, la migration et les règles de première publication ou de
nouvelle publication. Ajouter cette colonne seule pendant le chantier des tris
laisserait sa valeur et sa mise à jour sans workflow cohérent.

### Fiche 6 — 9

- `TC-SITE-008-01` à `04` : comptage atomique, déduplication pendant 30 minutes,
  nouveau clic après 30 minutes et exclusion des robots.
- `TC-SITE-008-05` et `06` : administrateurs et sites non publiés sont exclus.
- `TC-SITE-008-07` : une correction agrégée ajuste le total et laisse un audit.
- `TC-SITE-008-08` : les périodes de tendances sont exactes et les sites sans
  clic sont exclus.
- `TC-SITE-008-09` : la déduplication ne stocke aucune IP brute.

### Fiche 6B — 9

- `TC-SITE-GEO-01` à `09` : seules les six grandes zones sont admises ; les IP
  ne sont pas persistées ; le seuil de 10, l'écran admin agrégé, les purges,
  le fuseau `Indian/Reunion`, la migration et l'audit sont vérifiés.

## 🔵 Validations humaines — 2

- `TC-SITE-PUB-06` : confirmer qu'un site possède un lien réel et utile avec
  La Réunion relève d'une décision éditoriale humaine.
- `TC-SITE-PILOT-01` : le parcours pilote exige un vrai site, une validation du
  contenu et de l'affichage, puis une observation sur mobile et ordinateur.

## 🟠 Fonctionnalités absentes — 11

| Domaine | Cas | Prérequis manquant |
| --- | --- | --- |
| Cycle de vie | `TC-SITE-006-03`, `04`, `07` | Statuts `draft` et `archived`, service de transitions et confirmation éditoriale du lien réunionnais. |
| Recherche | `TC-SITE-007-05B` | Portée géographique combinable, explicitement reportée. |
| Dates métier | `TC-SITE-009-01` à `07` | Quatre dates distinctes, archivage, nouvelle publication et historique. |
## 🔴 Écarts réels confirmés — 0

Les trois écarts de recherche précédemment confirmés sont corrigés.

## Ordre de correction conseillé

1. 🟠 Ajouter le cycle de vie complet et les dates métier.
2. 🟠 Ajouter la portée géographique lorsque son modèle sera prêt.
3. 🔵 Exécuter le parcours pilote réel en dernier.

## Commandes de vérification

```bash
.venv/bin/python -m unittest discover -v
.venv/bin/python -m compileall -q reunion_wiki tests
```

L'avertissement existant sur `datetime.utcnow()` reste non bloquant et n'est pas
compté comme un échec de test.
