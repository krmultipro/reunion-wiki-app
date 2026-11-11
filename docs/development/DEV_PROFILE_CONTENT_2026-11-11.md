# Ajout d’une fiche et d’un portrait sur DEV — 11 novembre 2026

Version 1.0. Décision utilisateur explicite : ajouter le contenu préparé et son
portrait dans la base DEV en suivant le fonctionnement des branches validé.
Ce document décrit l’opération et ses critères ; il ne déclare pas à lui seul
une écriture active ou un déploiement réussi.

## Périmètre et source

- Reprendre le nom, les deux paragraphes, le type personne et les deux liens
  de l’aperçu privé validé ; ne pas exporter ce catalogue ou le JPEG dans Git.
- Catégorie Lifestyle choisie explicitement par l’utilisateur le 11 novembre ;
  référentiel actif relu (ID 8), commune laissée vide. Conserver en privé la provenance éditoriale réelle et les limites
  de vérification ; aucun rattachement géographique ou accord tiers inventé.
- Photo transmise en privé, sans retouche, vers `UPLOAD_FOLDER/talents/...` par
  le service d’upload. Le fichier est un JPEG décodé et vérifié avant transfert.
- Publication uniquement dans la base DEV derrière Basic. L’interface actuelle
  est réutilisée ; aucune nouvelle présentation ou modification métier requise.
- Autorisation publique/production, crédit et relecture de la personne restent
  des étapes distinctes. La demande actuelle couvre l’usage de la photo sur DEV.

## Préparation, branches et confidentialité

1. Lire le `dev` distant, créer une branche `codex/ajout-fiche-dev-20261111`
   depuis cette référence dans le worktree propre ; préserver le checkout sale.
2. Identifier par inspection le conteneur `web_dev`, ses labels et son volume
   `/data`. Vérifier la séparation avec la production, le référentiel des
   catégories et l’absence de fiche ayant le slug demandé.
3. Prendre un snapshot cohérent DB+uploads avec `script/deploy_data.py` ; vérifier
   manifeste/intégrité, copier sur le PC puis restaurer isolément pour la recette.
4. Garder le contenu privé, les notes de provenance, le JPEG et le script
   d’opération dans un dossier privé hors Git. Transfert SSH/SCP privé seulement,
   hors archive applicative et contexte de build Docker. Aucun secret transféré
   dans GitHub, aucun portrait téléchargé depuis un réseau social.
5. Tester l’opération sur la restauration avant commit/fusion et écriture active.
   Les changements de cette branche sont documentaires ; les enregistrements
   SQLite et les uploads persistants ne sont pas versionnés dans Git.
6. Commit/push de la branche, fusion vers `dev`, récupération de ce `dev` et
   déploiement contrôlé du commit officiel ; aucune fusion ou publication `main`.

## Écriture par les services existants

Après sauvegarde et contrôle des labels DEV, utiliser un contexte Flask dont
`DATABASE_PATH` et `UPLOAD_FOLDER` correspondent aux chemins attendus, puis :

1. Rechercher le slug exact par `talent_repository.get_by_slug`. S’il existe,
   comparer tous les champs et l’empreinte de la photo ; ne pas créer un suffixe
   ni remplacer automatiquement une fiche différente.
2. `talent_service.save_talent(data, image_file=FileStorage(...))` crée un
   **brouillon** et conserve le JPEG via `image_storage.save_upload`. Relire les
   champs, le statut, le chemin et l’empreinte ; conserver l’identifiant obtenu.
3. Vérifier l’invisibilité anonyme du brouillon et de son portrait. Un nouvel
   appel de préparation identique doit reprendre le même identifiant et la même
   image, sans créer de nouvelle fiche ni fichier.
4. `talent_service.publish(id)` est une action séparée : il applique les
   validations de catégorie, URL et rattachement/source privés existantes.
   Aucune mise à jour SQL directe du statut, aucun contournement des services.
5. Relire le résultat dans la base active, vérifier la fiche, son image, la
   recherche, l’annuaire et les liens. Un nouvel appel identique ne crée rien.

## Critères d’acceptation et limites

- Une seule fiche supplémentaire, slug stable, contenu et liens fidèles, commune
  non inventée, catégorie choisie et sources privées non exposées dans le HTML.
- Un seul nouveau JPEG, empreinte identique à l’original ; brouillon et portrait
  invisibles avant publication, puis fiche et image accessibles seulement par
  le site DEV protégé. Aucun accès direct publié au port applicatif.
- Intégrité SQLite et relations valides ; tous les anciens enregistrements et
  uploads restent inchangés. Aucun profil de recette fictif dans la base active.
- Recette de la fiche avec photo sur ordinateur et vue mobile ; le téléphone
  physique reste à vérifier si aucun essai réel n’est effectué.
- Production inchangée ; seule la base DEV et son stockage d’uploads évoluent.
  En cas d’erreur de contenu, corriger/archiver uniquement cette fiche par le
  service ; ne pas écraser la base active avec la copie locale de recette.
- Snapshot avant écriture conservé et copie PC vérifiée. Un rollback de code
  n’annule pas une saisie de contenu ; toute restauration complète de données
  exige l’arrêt des écrivains et la protection des écritures plus récentes.

Les preuves d’exécution actives et les identifiants de la fiche restent dans le
journal privé de l’opération ; ce document conserve la procédure sans recopier
les données personnelles ni le portrait dans le dépôt public.

## Recette préalable réalisée sur restauration isolée

Snapshot frais de la base DEV et de ses uploads, copie sur le PC vérifiée puis
restaurée : intégrité OK et zéro relation cassée. Le JPEG fourni est décodé,
878 × 1560 pixels, 141 369 octets ; son empreinte est conservée dans le journal privé.

La création par `save_talent` produit un brouillon ; fiche et portrait retournent
404 anonymement. Une deuxième préparation conserve le même identifiant et la
même image. L’action séparée `publish` rend la fiche et sa photo accessibles ;
nouveaux appels de publication et préparation sans nouveau contenu. Deux
paragraphes et deux liens fidèles ; recherche accentuée et non accentuée et
annuaire retrouvent la fiche. Notes, référence éditoriale et rattachement privés
absents du HTML, photo servie avec une empreinte identique.

Comparaison de toutes les tables et de chaque ancien upload avec le snapshot :
aucune ancienne ligne ni image modifiée, exactement une fiche et un JPEG ajoutés.
Ces preuves concernent la restauration locale ; l’exécution active et la recette
navigateur DEV sont attestées séparément après le passage du commit dans `dev`.
