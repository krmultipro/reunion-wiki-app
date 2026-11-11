# Gestion des sites — recette de mise en page du 11 novembre 2026

Version 1.0. Contrat : [UX-ADM-SITES-001](../ux/ADMIN_SITES_LAYOUT.md), choix A.
Branche de départ `dev` au commit `8c7f01f2a36e`, checkout et base de recette isolés.

## Rouge avant code

Navigateur IAB sur la vraie route Flask `/admin/sites`, connecté par session
factice locale sur une base migrée jetable : six sites synthétiques avec noms
longs, statuts publié/refusé/en attente/brouillon/archivé, motif de refus et
catégorie longue. Aucun identifiant réel, nouvel export VPS ou formulaire de
mutation utilisé. Le code testé est celui de DEV ; la base de recette n’y est
jamais transférée.

| Largeur demandée | Défaut mesuré avant correction |
| --- | --- |
| 1280 et 1440 px | Intersection Recherche/Réinitialiser ; contrôle dépassant sa cellule de 201,67 px. |
| 320 px | Document 345 px pour largeur utile 305 px ; contrôle débordant de 44,95 px. |
| 390 px | Pas de débordement mesuré, mais zone de tableau non focalisable. |

Ces mesures précèdent la modification de la feuille et du template. Elles
vérifient les rectangles effectivement rendus, pas la présence d’une règle CSS.

## Vert après correction

Même navigateur, mêmes données et mêmes contrôles de rectangles. La mesure
finale ajoute la non-intersection entre contrôles d’une même cellule, notamment
Modifier/Supprimer. Les valeurs ci-dessous ont été relevées après le dernier
ajustement CSS ; barres de navigateur simulées, aucun téléphone physique.

| Vue demandée | Largeur utile/document | Mode | Zone/tableau |
| --- | --- | --- | --- |
| 320 | 305/305 | Fiches | 205/205 |
| 390 | 375/375 | Fiches | 275/275 |
| 768 | 753/753 | Fiches | 633/633 |
| 1024 | 1009/1009 | Fiches | 889/889 |
| 1200 | 1185/1185 | Fiches | 1065/1065 |
| 1201 | 1186/1186 | Tableau | 1066/1440 |
| 1280 | 1265/1265 | Tableau | 1145/1440 |
| 1440 | 1425/1425 | Tableau | 1305/1440 |
| 1920 | 1905/1905 | Tableau | 1480/1480 |

Pour les neuf vues : zéro intersection de filtres, zéro contrôle hors de sa
cellule, zéro intersection des contrôles de table, neuf colonnes conservées.
Le débordement du tableau intermédiaire est contenu dans la région locale.
La page entière ne défile pas horizontalement ; aucun overflow masqué sur body.

Clavier : la région « Gestion des sites » reçoit le focus, puis Flèche droite
fait passer `scrollLeft` à 19 px à 1280 px. Focus visible défini localement.
Recherche réelle GET « volontairement » : six résultats → un résultat, critères
dans l’URL ; Réinitialiser → URL sans critères et six résultats. Aucun clic sur
Mettre à jour, Publier, Refuser, Supprimer ni déconnexion active.

Capture PC observée avec neuf colonnes lisibles, filtres distincts et boutons
Modifier/Supprimer séparés. L’itération intermédiaire avait révélé un lien inline
dont la marge verticale ne séparait pas les actions ; passage en inline-flex
puis mêmes contrôles relancés sur toutes les largeurs.

## Vérifications et limites

- Suite applicative : 140 cas, 139 réussis et un historique manuel ignoré.
- Pendant la recette, `dev` a avancé avec le partage de personnalité en ligne
  (`7d44fa8635af`). Intégration sans conflit de ces cinq fichiers indépendants,
  puis suite complète relancée : 142 cas, 141 réussis et un historique ignoré.
  Les nouveaux sélecteurs concernent uniquement le partage de la fiche publique,
  sans effet sur les sélecteurs admin contrôlés ci-dessus.
- Suite des scripts : 49 tests réussis.
- Compilation des sources/tests/scripts et `git diff --check` réussis.
- Fichier CSS dédié à la page ; template hérite du même layout via `super()`,
  mêmes champs/actions et jetons CSRF. Aucun service, route ou repository modifié.
- Pas de nouvel automatisme navigateur dans le déploiement : les mesures de
  rendu ci-dessus complètent les suites Python, qui ne prouvent pas la géométrie.
- Aucun téléphone physique, test exhaustif de lecteur d’écran ou zoom 200 %
  déclaré vérifié. La recette visuelle est locale, sur données synthétiques.

## Livraison et récupération

La livraison suit la branche dédiée → fusion dans `dev` → déploiement exact
testé. Les preuves d’exécution active restent dans le dossier privé
`/tmp/reunion-admin-sites-qa-20261111/` : `deploy.log`, `runtime.json`, journaux
`app-tests.log`/`script-tests.log` et contrôles de sauvegarde. Les labels et le
`release-info.txt` VPS relient le résultat au commit actif. Cette fiche décrit
la recette locale et les critères ; elle ne suffit pas à attester une bascule.

Les contrôles actifs doivent vérifier le CSS chargé par l’admin authentifiée,
son empreinte identique à la source testée, le cache privé de la page, le refus
anonyme, les comptages/empreintes DB + uploads et la production inchangée. Ne pas
soumettre de mutation de recette dans la base active.

Avant livraison : snapshot frais DB + uploads créé sur VPS puis restauré dans
un répertoire isolé, intégrité et empreintes identiques, zéro relation cassée,
60 sites/30 personnalités/zéro proposition/34 images. Archive privée conservée
hors conteneur dans le dossier de déploiements du VPS. La copie PC indépendante
du précédent travail reste vérifiée ; sa base est plus ancienne que ce snapshot
(empreinte logique différente, images identiques). Aucun nouveau transfert privé
autorisé ou effectué ici. Le snapshot final de bascule garantit le rollback sur
le VPS ; il ne protège pas d’une perte du VPS avec ses écritures plus récentes.
