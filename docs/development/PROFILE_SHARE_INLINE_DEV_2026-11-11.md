# Partage avec icône dans la ligne des réseaux — DEV

Version 1.0 — 11 novembre 2026. Contrat et critères écrits avant tests et code.

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

Publication et recette du conteneur actif à compléter après exécution.
