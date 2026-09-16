# ADR-001 — Documentation as Code et traçabilité des décisions

| Métadonnée | Valeur |
| --- | --- |
| Statut | Accepté |
| Date | 2 septembre 2026 |
| Remplace | — |
| Remplacé par | — |

## Contexte

Le cahier des charges et les règles métier évoluent pendant la construction de
Réunion Wiki. Modifier directement une décision ancienne sans conserver son
historique rendrait difficile la compréhension des choix et des écarts entre la
documentation et l'application.

## Décision

La documentation validée est conservée en Markdown dans le dépôt Git.

- Notion sert au pilotage et à la préparation des décisions.
- Les fichiers Markdown constituent la référence des décisions validées.
- Chaque document principal possède un numéro de version et un historique.
- Chaque règle métier possède un identifiant stable et sa propre version.
- Une décision validée qui change de sens est marquée comme remplacée ; elle
  n'est pas supprimée.
- La nouvelle règle ou le nouvel ADR indique explicitement ce qu'il remplace.
- Git conserve le contenu exact des versions précédentes.

## Amendements

- Une correction de forme ne nécessite pas de nouvelle version.
- Une précision compatible augmente la version mineure, par exemple de `1.0` à
  `1.1`, et ajoute une entrée à l'historique.
- Un changement de sens augmente la version majeure, par exemple de `1.0` à
  `2.0`, ou crée un nouvel ADR.
- Un retour sur une décision crée également une nouvelle version ou un nouvel
  ADR ; l'ancienne décision reste consultable.

## Conséquences

Cette méthode ajoute une petite étape lors des changements importants, mais
elle évite les décisions silencieusement écrasées et permet de comprendre
pourquoi le produit a évolué.
