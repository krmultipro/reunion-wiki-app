# Style du bouton de partage sur DEV — 11 novembre 2026

Version 1.1 — contrat rédigé avant vérification du défaut et correction ; preuves
locales puis DEV ajoutées après exécution.

## Autorisation, sources et périmètre

L'utilisateur demande la correction du bouton « Partager cette fiche » de DEV,
selon le déroulé de modification documenté le 11 novembre. Branche dédiée depuis
le dernier `dev` distant, critères, défaut reproduit, correction, contrôles,
commit/revue, fusion `dev`, publication du commit exact et vérification effective.
`main` et production hors modification. Départ : `351d134c5afa`.

Le choix visuel est déjà validé par UX-SHARE-001 v1.1 : action texte verte
soulignée, secondaire, fond transparent et aucune bordure, après les liens
officiels et avant la correction. Cible tactile de 44 px et focus visible.
Référence : `../ux/PROFILE_SHARING.md`, règle existante de
`maquettes/mobile-final/public.css` et recette du 26 octobre.

Constat en lecture du code actif DEV : `templates/refonte/detail.html` fournit
la classe `profile-share-trigger`, mais les styles chargés ne la définissent
pas. `components.css` définit seulement le dialogue. La classe `.button` des
boutons du dialogue ne concerne pas le déclencheur. Le rendu natif du navigateur
reste donc visible. Il s'agit d'un écart d'intégration CSS, sans choix UX ouvert.

## Schéma et critères avant correction

```text
Fiche publiée → liens officiels → Partager cette fiche (action discrète)
  → dialogue de copie existant → fermeture / Échap → retour à la fiche
```

| ID | Contrat de recette |
| --- | --- |
| SHARE-STYLE-01 | Déclencheur texte vert #087548, 13 px et poids normal ; fond transparent, bordure nulle, texte souligné. |
| SHARE-STYLE-02 | Hauteur tactile au moins 44 px ; focus clavier visible, ouverture et fermeture du dialogue toujours utilisables. |
| SHARE-STYLE-03 | Après les liens officiels et avant la correction ; aucun débordement horizontal à 320/390/1280 px. |
| SHARE-STYLE-04 | Copie du lien déjà livrée, routes, contenu, données, autres boutons et confidentialité inchangés. Aucune transmission réelle nécessaire pour la recette du style. |
| SHARE-STYLE-05 | Suites et livraison contrôlée DEV réussies ; empreinte CSS et version active vérifiées, production inchangée. |

Le contrôle navigateur des styles calculés doit d'abord constater l'absence
des propriétés attendues, puis leur présence après correction sur la même fiche
synthétique. Il vérifie le résultat visuel réel ; aucun test qui recopie une
chaîne CSS n'est ajouté. Les suites applicatives et de livraison existantes
restent les contrôles de non-régression et les barrières du déploiement.

## Implémentation prévue et livraison

Ajouter uniquement la règle du déclencheur dans `static/refonte/components.css`,
en réutilisant les propriétés de la référence et le focus commun de `app.css`.
Pas de nouveau bouton plein ni de modification JavaScript ou template.

Appliquer `VPS_DEV_ROUTING.md`, section refonte DEV, et `deploy-dev.sh` : `dev`
propre, archive exacte, capacité, candidate, tests sans réseau, migration sur
copie sans changement attendu, sauvegarde DB+uploads, bascule DEV et smoke.
Pas de `--allow-db-change`, de patch du conteneur actif ou de nettoyage disque.
La sauvegarde privée indépendante existante doit être vérifiée avant bascule.

## Résultats

### Recette locale et relecture

- Défaut reproduit sur une fiche synthétique et une base vierge jetable :
  fond rgb(239,239,239), bordure 2 px, texte noir de 15 px, hauteur 30 px,
  aucune décoration. Le contrat visuel échoue avant correction.
- Après correction, sur cette même fiche : transparent, bordure 0, texte
  rgb(8,117,72) de 13 px et poids 400, souligné, hauteur 44 px. Le contrat passe.
- Ordre DOM inchangé : liens officiels → déclencheur → correction.
  Entrée clavier ouvre le dialogue existant ; Échap ferme et restitue le focus
  au déclencheur, contour de focus 3 px visible.
- Vues 320/390/1280 px sans débordement horizontal (largeurs documentaires
  305/375/1265 px). Nom long et portrait de remplacement dans la fixture.
  Aucun presse-papiers, partage externe ou destinataire utilisé pour cette recette.
- 140 cas applicatifs : 139 réussis, un cas manuel historique ignoré.
  49 tests de livraison réussis ; compilation et `git diff --check` réussis.
- Relecture indépendante : aucun défaut actionnable ; périmètre du sélecteur,
  absence de conflit PC et maintien du focus commun contrôlés.
- Seul fichier applicatif modifié : `static/refonte/components.css`.
  SHA-256 après correction :
  `8660e5be5a6990e5c0ca8cf509fb8b1a0564911ae81e772db57f7d2c2870d96d`.

### Récupération et publication

Snapshot DEV frais DB+uploads vérifié et conservé hors du conteneur, sur le VPS.
Une nouvelle copie privée complète vers le PC a été refusée par la validation
automatique, faute d'autorisation explicite du payload et de sa destination.
Aucun contournement ni nouveau transfert de base/image. La copie indépendante
déjà présente sur le PC a été vérifiée et restaurée isolément avec les helpers.
Les 34 images ont les mêmes empreintes agrégées que le snapshot VPS frais.
Les différences SQLite constatées depuis cette copie sont évaluées séparément
dans la recette privée : seules `click_deduplication`, `site_geo_daily_stats`
et la colonne `sites.click_count` diffèrent. Les autres colonnes de sites et
les autres tables, dont les personnalités, sont identiques. La voie de
récupération conserve donc les contenus dans la copie PC existante et les
compteurs récents dans le snapshot VPS frais ; les deux bases ne sont pas
déclarées intégralement identiques. Aucune migration de données n'est autorisée
par cette correction ; le script doit confirmer l'absence de changement.

### Publication et recette du DEV actif

- [PR #52](https://github.com/krmultipro/reunion-wiki-app/pull/52) fusionnée dans
  `dev`. Les trois fichiers de la branche publiée ont les mêmes blobs et le
  même arbre `5ccd65c6dc6d809899cf9e773f018d6f87cf4541` que la source testée.
  Le connecteur GitHub a servi à publier après indisponibilité de l'écriture
  authentifiée du client Git local ; aucun secret récupéré ou affiché.
- Commit DEV livré : `b4ac45bf8c891bf8669eaeff55e59d479abf4191`.
  Release : `20261111T093028Z-b4ac45bf8c89`. `release-info.txt`, labels d'image
  `reunionwiki.branch=dev` et `reunionwiki.commit=b4ac45bf8c89` relus.
- Publication par `deploy-dev.sh` depuis le `dev` officiel propre : contrôles
  locaux puis 140 cas dans l'image candidate (139 réussis, un manuel ignoré),
  migration sur copie sans modification de données, snapshot final DB+uploads,
  smoke Gunicorn, test/rechargement Nginx partagé réussis. Pas de purge ni de
  nettoyage des anciens conteneurs signalés par Compose.
- CSS réellement servi via GET et HEAD, versionné
  `/static/refonte/components.css?v=1794389397`, empreinte identique à la recette.
  Le cache public des assets existant est conservé ; cette nouvelle URL permet
  au navigateur de charger le style mis à jour.
- Fiche publiée de DEV contrôlée dans le navigateur par un tunnel SSH temporaire
  limité au loopback : style calculé identique au contrat sur PC ; à 390 px,
  cible 44 px, absence de débordement, Entrée/Échap et focus 3 px vérifiés.
  La capture représente le conteneur DEV actif, pas la maquette statique.
- DEV et son CSS restent refusés sans Basic (401), robots/non-indexation
  vérifiés. Le port applicatif n'est pas publié sur l'hôte. Session HTTPS
  authentifiée et téléphone physique non inspectés.
- Empreinte logique SQLite et inventaire complet des uploads identiques au
  snapshot VPS pris avant publication ; 34 uploads et zéro violation de clé
  étrangère. Les données actives n'ont pas été remplacées par la recette PC.
- Image et date de démarrage du conteneur production identiques au relevé
  préalable ; production HTTP 200. `main` inchangé par cette livraison.
- Rollback de code/image et bundle final conservés dans le dossier de release
  privé du VPS. Les journaux locaux de recette et livraison restent dans
  `/tmp/reunion-share-style-qa-20261111/`, hors Git et hors artefact.

Le fonctionnement réel de copie du lien ne doit pas être confondu avec la
simulation historique. La recette n'a transmis aucun lien à un tiers et n'a
pas testé la réception dans une messagerie. La mise à jour de cette preuve
documentaire n'exige pas de reconstruire l'image : les documents ne font pas
partie de l'artefact applicatif.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.0 | 11 novembre 2026 | Contrat, défaut reproduit puis règle CSS et vérifications locales. |
| 1.1 | 11 novembre 2026 | Preuves de publication, sauvegardes, recette DEV et limites observées. |
