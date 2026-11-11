# Référence ordinateur de la refonte — 11 novembre 2026

Version 1.1 — correction explicitement demandée par l’utilisateur : le site en
résolution PC doit reprendre le design de `maquettes/pc-v1/`. Le 11 novembre,
la première intégration avait repris le repli ordinateur de mobile-final ; cette
interprétation est remplacée. La référence mobile reste `maquettes/mobile-final/`.

## Périmètre validé et réalisation attendue

Reprendre UX-PC-001/003/004/006/007 et les précisions de DESKTOP_MOCKUP_V1 : cadre
maximal 1280 px, menu supérieur clair flottant et persistant, recherche sur la
photo à l’accueil, sections et liens d’exploration alignés, cartes Sites 16:9
avec description et action, petites cartes Personnalités horizontales. Les
annuaires filtrés ont douze résultats par page. Une fiche PC utilise le grand
portrait carré à gauche et les informations/liens à droite, conformément à
UX-PC-007 qui remplace le plafond historique de 150 px sur la fiche PC.
Les bannières de titre sont conservées sur listes/catégories/recherche ; aucun
paysage décoratif sur FAQ, Contact, mentions, formulaire et confirmation,
conformément à l’amendement UX-PC-004 v1.1.

L’adaptation PC s’active à partir de 1000 px CSS, seuil ordinateur déjà utilisé
par les styles du projet ; vérifier spécialement 1024/1280/1440/1920. Le repli
mobile existant reste utilisé sous ce seuil, notamment le dock et le carrousel
à 680 px et moins. Aucun choix de contenu ni de catégorie n’est ajouté.

Les données et actions restent celles de Flask/SQLite : ne pas importer le
catalogue statique PC, sessionStorage de démonstration, confirmations simulées
ou outils de comparaison. Partage réel, protections des brouillons/médias et
propositions réelles sont conservés. Aucun changement de schéma, d’URL ou de
publication de contenu dans cette correction de présentation.

La pagination PC est une amélioration progressive des résultats complets déjà
filtrés par le serveur : douze cartes, liens et paramètre `page`, conservation
de `q`, `categorie` et `retour`. Hors PC ou sans JavaScript, la liste intégrale
reste lisible. Les commandes disparaissent lorsqu’une page suffit. Changer le
filtre ou la recherche repart à la première page ; page invalide bornée, retour
navigateur et retour de fiche cohérents. Les cartes mobile ne sont pas paginées.

## Critères de vérification

1. Comparer visuellement accueil, annuaire Sites/Personnalités, recherche,
   fiche et aide/formulaire au PC V1 ; mêmes grandes compositions, photo et
   typographies, aucun débordement aux quatre largeurs ordinateur.
2. Vérifier aussi 999/1000 px, puis 320/390 px : menu/dock, cartes, carrousel et
   formulaire utilisables, absence de régression de la composition mobile.
3. Plus de douze résultats : page 2, dernière page, retour de fiche et historique ;
   filtre donnant une seule page sans commandes ; aucun profil privé exposé.
4. Photo absente, textes longs, clavier et focus, liens officiels et correction
   conservés ; aucune prétention d’amélioration de résolution des petits portraits.
5. Suites applicatives existantes, syntaxe JS/Python et diff contrôlés. Rendu
   local, déploiement DEV et téléphone physique doivent être distingués dans le bilan.

## Isolation

Travail dans un checkout et une branche dédiés depuis le `dev` observé, sans
modifier les fichiers ou données en cours de traitement dans le chat principal.
Les preuves de comparaison et le résultat réel seront ajoutés après vérification.

## Réalisation et contrôles locaux

Implémentation dans `static/refonte/desktop.css` et `desktop.js`, chargement PC
à partir de 1000 px et adaptations sémantiques des templates communs. Styles
mobile existants conservés ; éléments complémentaires PC masqués hors PC.
Le header des pages admin est exclu. Listes et recherche utilisent les données
publiées fournies par les services existants, sans modification de base.

Contrôles exécutés le 11 novembre :

- Suite applicative : 129 cas découverts, 128 réussis, un cas manuel historique
  ignoré. Après ajout des bannières internes, sept tests publics rejoués, réussis.
- Huit tests de pagination sous Node (`node script/tests/test_desktop_pagination.cjs`) :
  douze résultats, page 2, dernière page, bornage, critères/retour, historique,
  mode mobile et exclusion admin. DOM minimal simulé, pas navigateur réel.
- Dix pages servies en HTTP sur l’aperçu local, dont fiche, formulaire, aides et
  connexion admin ; un H1 par page et 79 ressources statiques relues avec succès.
- Compilation Python applicative/tests/scripts, syntaxe JS et contrôle du diff
  réussis. Aucun contenu ni donnée de recette ajouté au serveur DEV.

Limite à la fin de la discussion parallèle, avant transmission : inventaire CUA
vide et navigateur IAB indisponible ; ouverture de l’aperçu dans Codex en attente. Aucune
capture ni mesure de débordement aux différentes largeurs ne vaut donc preuve
visuelle actuelle. La comparaison visuelle PC/mobile et le téléphone physique
restent à effectuer. Le travail est isolé localement, sans fusion dans `dev`,
publication GitHub ni déploiement depuis cette discussion parallèle.

## Reprise et recette dans le chat principal — 11 novembre

L’utilisateur autorise explicitement la transmission du correctif et la poursuite
de la vérification/intégration DEV. Le commit local initial est repris, sur la
même branche dédiée. La maquette PC est ouverte dans le navigateur pour une
comparaison directe ; l’application candidate utilise une restauration isolée
de la base DEV actuelle, avec 30 profils et 34 images, sans données inventées.

Corrections complémentaires dans les décisions existantes :

- Priorité CSS de l’en-tête renforcée pour conserver ses quatre coins arrondis
  malgré l’ancien style du bandeau mobile.
- Formulaire de proposition aligné sur une colonne centrale de 760 px comme
  PC V1 : titre et panneau sur le même axe, deux choix de type de largeur égale,
  rythme des champs, focus clavier des radios conservé. Typographie des aides
  et seuils de titres 1150/1600 px repris de la référence PC.
- Défilement : la clé de mémorisation suit désormais l’URL courante après
  `pushState`, au lieu de conserver celle de la première page. Ce correctif
  préserve une position distincte pour chaque page et chaque critère.

Contrôles observés sur la version finale locale :

| Zone | Vérification |
| --- | --- |
| Ordinateur | Accueil, Sites, Personnalités, recherche, proposition, FAQ et fiche à 1024/1280/1440/1920 px ; un H1 et aucun débordement horizontal sur ces 28 vues ; cadre plafonné à 1280 px |
| Seuil | Accueil/Sites/proposition/fiche à 999/1000 px ; en-tête statique puis sticky et pagination PC activée ; redimensionner l’annuaire sous 1000 restitue ses 30 profils |
| Mobile | Les sept pages à 320/390 px ; documents mesurés 305/375 px avec scrollbar, sans débordement ; composition mobile, dock et liste complète conservés |
| Pagination | Personnalités 12/12/6, page 2 → fiche → retour avec page conservée et position rétablie ; précédent/suivant du navigateur observés |
| Filtres | Catégorie puis recherche accentuée → un profil ; critères conservés dans l’URL et pagination masquée lorsqu’une seule page suffit |
| Proposition | Changement de type Site → Personnalité par les vrais radios/POST, nouveaux champs corrects ; aucun envoi de proposition de recette |
| Administration | Connexion sans classe `desktop-responsive`, en-tête statique ; styles PC exclus |

Les huit tests Node de pagination et trois tests d’intégration défilement
réussissent en exécutant les vrais scripts dans un DOM simulé. Syntaxe JS et
diff contrôlés. Comparaison de toutes les tables de la copie avant/après recette :
aucune ligne modifiée et zéro proposition ajoutée. Aucune erreur console observée.

Les fichiers de mesures/captures restent hors Git dans le dossier privé de
recette. Un override de largeur avec deux onglets n’avait pas affecté l’onglet
testé : ces premières mesures ont été reconnues comme 1280 px, puis les contrôles
ont été refaits avec une largeur effective vérifiée sur l’unique onglet de test.
La matrice ci-dessus correspond aux largeurs mesurées, pas aux seules demandes.

Limites : pas de téléphone physique ni d’audit complet de lecteurs d’écran ;
l’affichage agrandi ne change pas la définition des portraits existants.
Cette section atteste la recette locale ; commit GitHub, image et déploiement
DEV sont attestés séparément après la fusion, sans confondre copie et base active.

## Convergence avec le dev courant

Pendant la recette, `dev` reçoit le correctif cache public/session et le logo
léger (`1fb34e5`). Il est intégré à la branche PC. Le conflit unique de l’en-tête
est résolu en conservant les deux évolutions : logo 144×144 et favicon légers,
styles/scripts PC et bouton Proposer. Le logo original reste utilisé pour OG.
Les fichiers de protection du cache et leurs tests sont conservés sans changement.

Après résolution, la suite applicative complète réussit : 140 cas découverts,
139 réussis, un cas historique manuel ignoré. Navigateur relancé sur le code
fusionné : accueil PC, en-tête arrondi et logo léger 144×144 effectivement chargés,
largeur document 1265 pour viewport 1280. Les deux jeux de corrections sont donc
conservés ; aucune ancienne version de l’en-tête n’est réintroduite.
