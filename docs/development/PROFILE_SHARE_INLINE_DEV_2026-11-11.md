# Partage avec icône dans la ligne des réseaux — DEV

Version 1.1 — 11 novembre 2026. Contrat et critères écrits avant tests et code,
puis preuves de la recette et de la livraison ajoutées après exécution.

## Décision et périmètre

L'utilisateur valide le choix A proposé après le correctif initial : icône à
gauche, libellé « Partager cette fiche » à droite, action après les réseaux
sur la même ligne si la place le permet, retour à la ligne sur petit écran.
UX-SHARE-001 v1.2 dans `../ux/PROFILE_SHARING.md` remplace le placement séparé
de v1.1. Style discret vert/souligné, cible 44 px et focus conservés.

Branche dédiée depuis `dev` `8c7f01f2a36e` ; documentation → tests rouges →
correction/tests verts → revue → fusion DEV → déploiement du commit officiel →
recette réelle. `main`, production, stockage et comportement de copie exclus.

```text
Fiche publiée avec liens :
  Instagram / YouTube / TikTok ... → [icône] Partager cette fiche
  (la ligne se replie naturellement si nécessaire)
  → dialogue existant → fermeture / Échap → retour du focus

Fiche publiée sans liens : présentation → [icône] Partager cette fiche
Fiche privée ou introuvable : aucune action de partage publique
```

## Critères définis avant réalisation

| ID | Contrat |
| --- | --- |
| SHARE-INLINE-01 | Un seul déclencheur par fiche publiée, placé après les liens dans leur conteneur adaptatif lorsque des liens existent ; repli après présentation sans liens. |
| SHARE-INLINE-02 | Icône SVG de partage avant le texte, aria-hidden et non focalisable, nom accessible « Partager cette fiche » inchangé. |
| SHARE-INLINE-03 | Styles précédents conservés, espace horizontal icône/texte, hauteur au moins 44 px et focus visible ; même ligne que les réseaux dès que la place le permet. |
| SHARE-INLINE-04 | À 320/390/1280 px : aucune coupure horizontale, ordre logique préservé et retour à la ligne naturel si nécessaire. Contrôler aussi un nom long et l'absence de liens. |
| SHARE-INLINE-05 | Entrée ouvre le dialogue, Échap/fermeture restituent la fiche et le focus ; copie de lien existante inchangée. Aucun presse-papiers ou envoi externe requis pour cette recette. |
| SHARE-INLINE-06 | Tests applicatifs et livraison, compilation, revue, version CSS/HTML servie, données et protection DEV vérifiés après déploiement ; production inchangée. |

Les tests d'intégration doivent échouer sur le code initial pour le placement
du déclencheur et l'icône absente, puis réussir avec les mêmes assertions.
La disposition, le focus et la cible tactile sont vérifiés dans le navigateur.

## Implémentation et livraison prévues

Déclencheur rendu par une macro unique de `templates/refonte/detail.html` pour
éviter les variations entre fiche avec/sans liens. Il rejoint le conteneur
`official-links` existant, qui possède déjà `display:flex;flex-wrap:wrap`.
SVG local en traits, sans asset distant ; styles limités au déclencheur et à
son alignement dans cette ligne. Aucun nouveau comportement JavaScript.

Appliquer `VPS_DEV_ROUTING.md` et `deploy-dev.sh`. Pas de modification de schéma
ni `--allow-db-change`, pas de patch direct du conteneur, pas de purge implicite.
Sauvegarde DEV fraîche sur VPS ; vérifier la voie de récupération privée déjà
disponible sur le PC sans relancer le transfert précédemment refusé. Les preuves
doivent distinguer une copie indépendante existante d'une copie fraîche identique.

## Résultats

### Tests et recette locale

- Rouge : les deux nouveaux cas de `test_refonte_public.py` échouent avant
  modification (déclencheur hors du groupe officiel et icône absente), sans
  erreur de fixture. Les mêmes neuf tests publics passent après correction.
- Suite complète : 142 cas, 141 réussis et un manuel historique ignoré.
  Livraison : 49 tests réussis. Compilation et `git diff --check` réussis.
- Navigateur sur deux fiches synthétiques et stockage jetable : à 1280 px,
  les trois réseaux et le partage sont alignés sur la même ligne ; icône 18 px
  à gauche du texte, bouton 44 px centré face aux liens PC de 52 px.
- À 390 px, le partage revient naturellement à la ligne ; à 320 px, TikTok et
  partage se placent sur la deuxième ligne. Largeurs documentaires 375/305 px,
  aucune coupure horizontale. Le nom long reste lisible.
- Une fiche sans réseau affiche un seul partage avec icône après présentation.
  Entrée ouvre le dialogue, Échap ferme et restitue le focus visible de 3 px.
  Aucun lien externe cliqué ni presse-papiers utilisé.
- Relecture indépendante : aucun défaut actionnable dans le macro, les branches
  conditionnelles, le SVG, les styles ou les nouvelles assertions d'intégration.

### Récupération et publication

Nouvelle sauvegarde cohérente DEV DB+uploads conservée sur le VPS, hors du
conteneur. La copie indépendante déjà présente sur le PC est vérifiée et
restaurée dans un répertoire isolé ; les 34 images correspondent au snapshot
frais. Les seuls écarts SQLite depuis cette copie concernent les compteurs
(`click_deduplication`, `site_geo_daily_stats`, `sites.click_count`) ; les autres
contenus correspondent. Aucun nouveau transfert privé vers le PC n'a été tenté.
La sauvegarde fraîche VPS protège aussi les compteurs récents ; la copie PC
n'est pas annoncée comme un snapshot frais identique de toutes les tables.

### Publication et recette du conteneur DEV actif

- [PR #54](https://github.com/krmultipro/reunion-wiki-app/pull/54) fusionnée dans
  `dev`. Arbre publié identique à l'arbre testé :
  `fde72a0b6307af37201645f7d9722ee4f45f7f0b`. Publication par le connecteur
  GitHub, sans récupération ni exposition de credentials du client Git.
- Commit applicatif livré : `7d44fa8635aff8f18ef59b03feb04218b60daec7`.
  Release : `20261111T101241Z-7d44fa8635af`. Labels branche/commit/release relus.
- `deploy-dev.sh` depuis le dev officiel propre : contrôles locaux puis
  142 cas dans l'image candidate (141 réussis et un manuel ignoré), migration
  sur copie sans changement, snapshot final DB+uploads, smoke Gunicorn et
  contrôle/rechargement Nginx partagé réussis. Aucune purge implicite.
- CSS livré en GET et HEAD à une nouvelle URL versionnée
  `/static/refonte/components.css?v=1794391932`. SHA-256 :
  `089dbb6d0db1230eb3ece26deb1e7da391c13605c06605ac27194ea0dbead407`.
- Fiche publiée du DEV réellement actif inspectée par un tunnel SSH temporaire
  limité au loopback. À 1280 px : trois liens et partage sur la même ligne,
  bouton 44 px centré face aux liens 52 px, icône 18 px masquée aux lecteurs
  d'écran. À 320 px : TikTok et partage sur la seconde ligne, sans débordement ;
  à 390 px : repli du partage, focus visible 3 px et fermeture Échap vérifiés.
  Une capture conserve le rendu réel de la ligne PC.
- HTML : un seul `data-share-open`, icône décorative non focalisable et texte
  du bouton inchangé. La fiche sans liens et les fiches privées sont couvertes
  par les tests d'intégration et la fixture navigateur locale.
- Empreinte logique SQLite identique au snapshot final, 34 uploads inchangés,
  zéro violation de clé étrangère. Les métadonnées protégées du snapshot final
  ont été relues via un conteneur isolé sans réseau et un montage en lecture
  seule, sans élargir les permissions des sauvegardes.
- Protection Basic conservée (401 anonymement pour DEV et CSS), non-indexation
  vérifiée, pas de port applicatif public sur l'hôte. Production HTTP 200,
  image et date de démarrage applicatives identiques au relevé préalable.
  `main` n'a pas été modifié.
- Rollback code/image et bundle final conservés dans le dossier privé de release.
  Journaux et recette : `/tmp/reunion-share-inline-qa-20261111/`, hors Git.

Limites : aucun téléphone physique ou session HTTPS Basic authentifiée inspecté ;
le navigateur contrôle directement le conteneur livré via SSH. Aucun lien
social ouvert, texte copié ou message transmis pour ces vérifications.
La preuve documentaire ajoutée ensuite ne change pas les sources applicatives
et n'exige pas une nouvelle construction de l'image.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.0 | 11 novembre 2026 | Choix A documenté, régressions rouges puis correction et recette locale. |
| 1.1 | 11 novembre 2026 | Preuves de publication DEV, récupération, affichage et limites. |
