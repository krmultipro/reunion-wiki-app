# Refonte DEV — vérifications du 11 novembre 2026

Version 1.0. Implémentation et recette locale ; la publication s’atteste séparément
par les labels d’image et le journal `release-info` du déploiement DEV.

## Périmètre livré

Référence visuelle mobile-final et repli PC : cadre, logo/paysage, navigation,
accueil, annuaires Sites/Personnalités, recherche simple groupée, catégories,
fiches et retours, FAQ/Contact/mentions, confirmation et erreurs. Données SQLite
réelles, aucun catalogue ni état de démonstration importé. Aperçus de sites
associés à leur ID ET URL, image de remplacement en cas de changement.

Contribution réelle sans compte Site/Personnalité, facultatifs repliés et
conservation des saisies lors du changement de type. Doublons publics et privés
distingués sans ID/statut privé exposé, envoi idempotent, confirmation liée à
la session. File admin authentifiée mixte, édition, brouillon séparé, refus
motivé, publication distincte, archivage. Les contrôles Site URL/HTTP/rattachement
existants sont réutilisés ; sources privées exigées avant publication personnelle.

Protection des médias brouillon/archives, HTML échappé, liens HTTP(S), CSRF,
retours locaux et réponses privées sans cache. Service worker limité aux icônes,
anciens caches de documents Réunion Wiki purgés ; aucune promesse offline.
Partage simple : copie réelle du lien canonique ou sélection manuelle, sans
partage natif ni notification. Les fonctionnalités reportées restent documentées
dans [REFONTE_DEV](../ux/REFONTE_DEV.md).

## Contrôles reproductibles

- Suite applicative `script/run_app_tests.py` sur bases et uploads temporaires :
  129 cas découverts, 128 réussis, un cas historique manuel volontairement ignoré.
  La suite inclut les 103 cas du correctif Site repris, les nouveaux parcours
  publics, propositions et contrôles talents. Le cas manuel ignoré reste décrit
  dans SITE_PILOT_REPORT_2026-09-22.md ; il ne valide pas une exécution actuelle.
- Scripts de livraison `python -m unittest discover -s script/tests -v` :
  49 tests réussis, incluant archives privées/liens, disque, snapshots WAL,
  uploads, concurrence de sauvegarde et orchestration/rollback simulés.
- Compilation Python applicative/tests/scripts, syntaxe JS public/service worker,
  syntaxe Bash et `git diff --check` réussis.
- Recherche avancée préexistante testée à `/recherche-sites`, distincte de la
  nouvelle recherche commune simple `/recherche`. Aucun panneau avancé ajouté.

## Données et migrations

Snapshot DEV complet base+uploads copié sur le PC et restauré isolément :
intégrité SQLite OK, aucune relation cassée, 60 sites, 29 personnalités et 33
images relues/décodées avec empreintes identiques. Il s’agit d’une copie indépendante
du VPS, pas d’une stratégie récurrente ou de trois lieux déjà atteints.

Migration sur cette copie avant recette : ajout de `site_refusal_history`,
`refonte_proposals` et de quatre champs éditoriaux privés aux talents ; aucune
colonne retirée, aucun nombre de lignes des tables antérieures modifié.
Les champs de localisation/preuve proposée de la nouvelle table sont additifs.
La migration répétée préserve sources et relation proposition→talent (test dédié).
La table talents normalisée n’est plus reconstruite à chaque démarrage.

Les données de test navigateur restent dans cette copie locale. Aucun profil
de recette, source fictive ou portrait privé n’est inclus dans l’artefact ni
destiné à la base DEV active. Le pilote éditorial privé n’a pas été saisi.

## Recette navigateur observée

Navigateur IAB sur copie restaurée, avec compte admin de recette local seulement :

1. Accueil depuis les vrais sites/profils, portraits et aperçus chargés.
2. Recherche Adriana → une fiche → retour résultats avec texte conservé.
3. Proposition personnalité minimale → confirmation réelle → demande en file.
4. Compléments synthétiques locaux → préparation brouillon → publication distincte.
5. Fiche visible, sans source privée → archivage → URL publique introuvable.
6. Repli 320/390 px demandé et ordinateur 1280 px : absence de débordement aux
   largeurs effectives mesurées (notamment 320/305, 390/375 et 1280/1265).
   Une vue formulaire a utilisé une largeur effective réduite à 291 px,
   document 277 px, sans débordement ; pas assimilée à 320 px.

Les contrôles ne couvrent pas un téléphone physique, tous les lecteurs d’écran
ou toutes les combinaisons de navigateur/barres/clavier. Le pilote privé avec
portrait vertical et gras reste distinct, non importé et non validé par ces vues.
La fiche de référence garde ses petits portraits et le texte éditorial actif.

## Livraison et limites

Branche dédiée issue du socle test puis fusion vers `dev`, sans commits de
monitoring. Publication SSH privée du même commit testé/archivé ; aucun push
`main` ni déploiement production. Le workflow prod distant ne sert pas à DEV.
Archive applicative et Docker excluent maquettes, monitoring, secrets et données.

Avant bascule : capacité mesurée, candidat isolé, tests dans l’image, migration
sur copie examinée, probe Gunicorn, snapshot final DB+uploads après arrêt des
écrivains DEV. Retour arrière prévu avec conservation des écritures candidates
et restauration DB+uploads/image/code. Les tests du rollback sont simulés ;
aucun échec volontaire de bascule sur service actif n’est déclaré réalisé.

Limites restantes du jalon : préparation multi-admin concurrente non éprouvée
(un worker Gunicorn dans le déploiement actuel) ; récupération des écritures
post-snapshot nécessite une réconciliation explicite en cas de rollback.
Confidentialité complète, fonctions avancées et ouverture publique restent les
étapes ultérieures validées. Aucun ticket Dashboard modifié par cette livraison.
