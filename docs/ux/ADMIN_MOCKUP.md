# Maquettes Réunion Wiki

## Dashboard contributeur mobile — 23 octobre 2026

[Ouvrir le dashboard contributeur](contributeur-mobile/index.html) · [Processus et décisions](../docs/ux/CONTRIBUTOR_DASHBOARD_MOBILE.md).

Révision de clarté UX-CDM-011 après essai utilisateur : **Mon suivi**, sections
**À compléter / Mes brouillons / Dernières mises à jour**, actions explicites,
sans compteurs ni demandes répétées. **Toutes mes demandes** conserve les filtres ;
les types de propositions et statuts sont détaillés. Même URL, même stockage de démo.

Variante mobile autonome, également consultable dans une colonne étroite sur PC.
Camille, compte fictif déjà connecté, propose un site ou une personnalité, reprend
un brouillon, répond à un complément et suit ses demandes. Un refus permet une
nouvelle version liée ; les corrections de personnalités passent par modération.
La rubrique Compte montre aussi connexion, activation et récupération simulées.
Les outils de démonstration en bas permettent de jouer les événements admin,
les erreurs et les états vides, et de recharger les exemples après confirmation.

Aucun compte ni mot de passe réel, email, base ou publication. Les enregistrements
de démonstration restent dans cet onglet (`sessionStorage`) ; fermer cet onglet
peut les perdre. N’utiliser que des données fictives. Le lancement sans compte,
les références publiques mobiles et la variante PC restent distincts.
Vérifications : [revue dédiée](../docs/testing/CONTRIBUTOR_MOBILE_REVIEW_2026-10-23.md).


## Logo manuscrit conservé, un peu plus grand — 23 octobre 2026

[Ouvrir la version mobile courante](accueil-categories-mobile.html).
UX-HOME-028 : préférence utilisateur pour Pacifico ; taille proposée de 32 px
au lieu de 28 px dans les en-têtes de cette variante. Montserrat reste une
[piste conservée pour plus tard](accueil-logo-mobile.html), sans suppression.

## Essai du logo géométrique — 23 octobre 2026

[Ouvrir le nouveau logo](accueil-logo-mobile.html) ·
[Comparer avec Pacifico](accueil-categories-mobile.html).
UX-HOME-027 : Montserrat 900 déjà locale, écriture droite et plus affirmée.
Le contexte `logo-mobile` applique cet essai aux pages publiques partagées,
avec la navbar, les catégories et les descriptions courtes conservées.
Essai Montserrat non retenu actuellement ; les autres contextes gardent leur logo.
[Contrôles et limites](../docs/testing/MOBILE_LOGO_REVIEW_2026-10-23.md).

## Nouvelle variante mobile : catégories en boutons — 23 octobre 2026

Complément UX-CREA-009 : [Personnalités par catégorie](createurs-categories.html)
reprend désormais les 29 profils publiés de dev, avec les dix catégories remplies
en boutons et « Toutes les catégories ». Les catégories de la base restent
inchangées ; leurs ambiguïtés sont conservées séparément au ticket Dashboard #46.
Instantané public dans `assets/personnalites-dev-20261023.json`, sans accès base.
Les fiches s’ouvrent sur dev et sont signalées externes ; les portraits absents
localement utilisent la silhouette. La liste précédente à trois profils reste
disponible dans les anciennes variantes.

[Ouvrir les Sites par catégorie](sites-categories.html?version=categories-mobile)
· [Accueil de cette variante](accueil-categories-mobile.html)
· [Comparer les versions](versions/index.html).

Choix utilisateur UX-SITES-007 : neuf catégories visibles en pastilles sur
plusieurs lignes, sélection unique verte et « Toutes les catégories » pour
réafficher la liste. Recherche et catégorie se combinent ; l’URL et les retours
d’aide conservent les critères. Même accueil, navbar retenue et 56 cartes ;
aucune pagination ajoutée. La nouvelle variante reste à relire visuellement.

Les pages `sites.html` et `accueil-navigation-flottante.html` conservent la
référence précédente ; PC V1 reste séparée. Les liens partagés reconnaissent
le nouveau contexte `version=categories-mobile`. Le bandeau des versions donne
accès aux deux références. Aperçu privé existant sur le port 8026, accessible
sur le LAN ou Tailscale lorsque le PC et le serveur restent actifs. Aucun
déploiement du site réel, base ou formulaire réel modifié.

[Décision et critères](../docs/ux/SITE_LIST.md)
· [Contrôles](../docs/testing/MOBILE_CATEGORIES_REVIEW_2026-10-23.md).

## Variante PC V1 séparée — 22 octobre 2026

[Ouvrir l’accueil PC](pc-v1/accueil.html) · [Comparer les versions](versions/index.html).
La référence mobile et sa navbar sont conservées. Les bandeaux de comparaison
séparent Versions PC et Versions mobile, avec date et heure triées dans chaque
groupe. La PC V1 reste à relire visuellement ; elle ne remplace aucune référence.

Cadre ordinateur commun, sites en grandes cartes, portraits sans agrandissement,
annuaire de 56 sites paginé par 12, recherche commune, trois fiches locales et
parcours de proposition simulé. Les pages PC sont autonomes dans `pc-v1/` ; les
captures et portraits existants sont réutilisés sans copie. Les portraits restent
facultatifs et exclus de Git. Aucun backend ou déploiement de Réunion Wiki.

Conception, critères et vérifications :
[UX-PC-001](../docs/ux/DESKTOP_MOCKUP_V1.md).
Le catalogue `versions/catalog.json` conserve la provenance des dates ; après une
mise à jour autorisée, régénérer les comparaisons avec
`python3 maquettes/versions/render.py`, puis contrôler `--check`. Le générateur
actualise uniquement les bandeaux attendus, l’index et les manifestes courants ;
les manifestes historiques restent inchangés.


## Dates et tri des versions — 22 octobre 2026

Les cartes de l’[index](versions/index.html) et les raccourcis de comparaison
indiquent la date et l’heure à la minute (UTC+4), dans l’ordre du plus récent au
plus ancien. Ces dates désignent l’enregistrement de chaque état de référence,
pas les retouches communes des liens. Sept versions sont représentées ; deux
anciennes variantes partagent le même enregistrement et la même heure.
[Décision UX-HOME-026](../docs/ux/HOME_PAGE.md) et
[provenance et vérifications](../docs/testing/VERSION_TIMES_REVIEW_2026-10-22.md).

## Dernière version : navbar flottante retenue — 22 octobre 2026

[Accueil avec barre flottante](accueil-navigation-flottante.html) : même contenu
que les grandes cartes, avec Accueil, Sites, Personnalités et Proposer en bas sur
mobile ; logo et photo en haut, menu du haut conservé sur ordinateur. Version
séparée, accessible dans tous les bandeaux de comparaison.

Le contexte de version circule dans les URL des pages partagées : les liens
Accueil et les retours depuis les listes, la recherche, la proposition et les
aides rejoignent la variante utilisée. Il ne repose pas sur une sélection globale
entre onglets. Les anciennes variantes gardent leur aspect et les archives leur
navigation interne. [Décision UX-HOME-024](../docs/ux/HOME_PAGE.md).
[Contrôles du navigateur et limites](../docs/testing/FLOATING_NAV_REVIEW_2026-10-22.md).
Navbar retenue explicitement par l’utilisateur (UX-HOME-025) ; cette page est
la dernière référence de maquette. Les autres choix restent à relire.
[Liens revérifiés](../docs/testing/NAVBAR_RETAINED_LINKS_2026-10-22.md) et repère Git
local maquette-navbar-retenue-20261022. Sans intégration Flask ni déploiement.

## Navigation de comparaison corrigée — 22 octobre 2026

Les six accueils et l’[index des versions](versions/index.html) présentent tous
le même bandeau en bas : Petits aperçus, Grandes cartes, Checkpoint du 22 octobre,
Sites du 20 octobre, Profondeur V1, Coverflow V2 et Toutes les versions.
Les liens relatifs conservent l’adresse utilisée, y compris sur téléphone en LAN.

Cet ajout étend la conservation initiale : seuls le bandeau et sa feuille CSS
sont ajoutés aux accueils archivés ; le contenu historique reste inchangé.
Les tags d’origine et les anciens manifestes sont conservés, les manifestes
courants actualisés et les README des archives amendés.
[Décision UX-HOME-023](../docs/ux/HOME_PAGE.md) et
[42 passages directs vérifiés](../docs/testing/MOCKUP_VERSION_NAVIGATION_2026-10-22.md).

## Essai Grandes cartes — 22 octobre 2026

Choix utilisateur **1A**, réalisé dans [un accueil séparé](accueil-grandes-cartes.html) :
trois grandes captures 16:9, nom et catégorie dessous, puis les portraits agrandis.
Sites empilés sur mobile, trois colonnes sur ordinateur ; carrousel manuel des
personnalités sur mobile. Menu, bannière, palette et contenus existants conservés.
Les deux accueils proposent tout en bas les liens Petits aperçus, Grandes cartes,
Checkpoint du 22 octobre et Toutes les versions. Les versions figées restent intactes.

Les captures réelles font 1440×810 ; les trois portraits locaux facultatifs ne
font que 150×150 et deviennent visiblement moins nets en grand. Aucun portrait
copié ou amélioré artificiellement. Cet essai reste à comparer par l’utilisateur,
sans adoption définitive, backend, base ni publication.
[Décision UX-HOME-022](../docs/ux/HOME_PAGE.md) et
[contrôles locaux](../docs/testing/HOME_LARGE_CARDS_REVIEW_2026-10-22.md).

## Checkpoint avant refonte visuelle — 22 octobre 2026

État actuel conservé sous **maquette-avant-refonte-visuelle-20261022** :
[accueil indépendant](versions/2026-10-22-avant-refonte-visuelle/maquettes/accueil.html),
[Sites](versions/2026-10-22-avant-refonte-visuelle/maquettes/sites.html),
[provenance et limites](versions/2026-10-22-avant-refonte-visuelle/README.md).
Pages publiques, 45 captures de sites, photo, polices et icônes figées ; portraits
locaux facultatifs non copiés. L’accueil de travail n’est pas redessiné.
Lors de ce checkpoint, les essais d’images plus grandes restaient en conception.
Le choix 1A a ensuite autorisé la variante séparée décrite ci-dessus. Versionnement
local uniquement ; ancienne référence conservée.


## Photo d’en-tête — 20 octobre 2026

Demande UX-HOME-017 : photo de paysage déplacée derrière le logo Réunion Wiki
et la navigation sur mobile et ordinateur, avec voile clair. La recherche reste
sur le fond clair en dessous. Même image locale, aucune nouvelle photo ni
publication. Ce choix remplace l’emplacement de la bannière dans le hero décrit
par les essais précédents. Contrôles à 320/390/1280 px dans
[HOME_PAGE.md](../docs/ux/HOME_PAGE.md).

## Accueil : sites en liste, puis personnalités — 20 octobre 2026

Demande vocale explicite UX-HOME-014 : trois sites en liste verticale avec
aperçu à gauche, nom/catégorie/flèche à droite et Explorer tous les sites en
fin de section. Le carrousel des profils existant est placé en dessous ;
portraits et captures conservés. Libellés publics Personnalités demandés.
Anciennes versions figées inchangées, aucun flou ajouté. Maquette locale
uniquement, aucun backend ni déploiement.
[Décision](../docs/ux/HOME_PAGE.md) et
[contrôles](../docs/testing/HOME_LIST_REVIEW_2026-10-20.md).

## Hero retenu — 20 octobre 2026

L’[accueil courant](accueil.html) conserve un fond clair sur mobile et affiche
la bannière du VPS avec son voile clair sur ordinateur (à partir de 1000 px,
seuil existant de la grille des créateurs). Titre, recherche et contenus courants
conservés ; photo servie localement. Décision UX-HOME-013 dans
[HOME_PAGE.md](../docs/ux/HOME_PAGE.md),
[contrôles et limites](../docs/testing/HOME_HERO_REVIEW_2026-10-20.md).

L’ancien lien de l’essai hero redirige vers cet accueil : il n’existe plus de
seconde copie d’accueil à maintenir. Les variantes figées précédentes restent
indépendantes. Maquette locale uniquement, sans publication.

## Référence validée avant essai de volume — 20 octobre 2026

L’utilisateur valide provisoirement la maquette actuelle avant l’ajout de tous
les sites publiés dans la liste. Repère Git local :
**maquette-sites-v1-validee-20261020**, état à trois sites. Copie indépendante :
[accueil validé](versions/2026-10-20-sites-v1-validee/maquettes/accueil.html) et
[Sites à trois exemples](versions/2026-10-20-sites-v1-validee/maquettes/sites.html).
[Sources et limites](versions/2026-10-20-sites-v1-validee/README.md).

Validation visuelle de l’accueil, des listes courantes et de la navigation ;
elle ne vaut pas contrôle complet d’accessibilité, validation admin/backend
ou publication. Les trois aperçus et les mini-descriptions de référence sont
conservés ; les essais suivants ne remplacent pas cette copie.

## Onglet Sites — 20 octobre 2026

[Sites](sites.html) reprend la simplicité de la liste Créateurs : recherche
textuelle, ordre alphabétique, cartes compactes avec les aperçus locaux 16:9,
sans filtres ni compteur. Le menu courant devient Accueil · Sites · Créateurs ·
Proposer ; Explorer tous les sites ouvre cette nouvelle liste. La recherche
avancée de démonstration reste disponible à son adresse précédente.

Après conservation de la référence validée, la liste courante affiche les
**56 sites publiés de production**, export public lu sans écriture le 20 octobre
à 21:25 (Asia/Dubai). Les champs sont copiés dans le HTML ; la recherche reste
locale, sans accès à la base au chargement. L’[export de provenance](assets/sites-publies-20261020.json)
est conservé pour vérification, sans données privées ni statuts non publics.
Après la demande complémentaire UX-SITES-006, les 53 autres sites ont été
visités sur le PC : 42 nouveaux aperçus exploitables, soit **45 captures sur
56 sites**. Les 11 autres conservent le remplacement prévu après blocage ou
chargement incomplet. Images WebP 1440×810 chargées à la demande, total 4,21 Mo
(~4,01 Mio). URL finale, date, contrôle visuel et motif d’échec sont consignés
dans [sources.json](assets/site-previews/sources.json). Aucun navigateur n’est
lancé lors de la consultation de la maquette. L’accueil garde ses trois sites.
[Fiche UX](../docs/ux/SITE_LIST.md) et
[vérifications](../docs/testing/SITE_LIST_MOCKUP_CHECKS.md). Maquette locale,
aucune intégration Flask ni publication ; relecture de la longue liste attendue.

## Essai Sites « À découvrir » — 20 octobre 2026

Choix utilisateur **1B** : les accordéons de l’accueil de travail sont remplacés
par trois cartes à captures réelles 16:9. Sur mobile, carrousel horizontal simple
avec aperçu suivant, flèches et glissement natif ; sur ordinateur, trois colonnes.
Le bloc Créateurs et son effet de profondeur V1 sont conservés.

Infinity Park, Bus.re et Eau du robinet ont été lus parmi les sites publiés de
la base de production, sans écriture. Les captures ont été réalisées une fois
sur le PC puis optimisées en WebP (total 304 Kio). Les images sont servies
localement : aucun chargement des sites externes à l’ouverture de l’accueil.
Les cartes ouvrent les sites réels dans un nouvel onglet. Destination initiale
d’Explorer tous les sites : recherche-sites.html ; l’ajout de l’onglet Sites
remplace depuis cette destination par sites.html. La recherche avancée de
démonstration reste inchangée à son adresse précédente.

Référence : UX-HOME-012 dans [HOME_PAGE.md](../docs/ux/HOME_PAGE.md).
[Sources des captures](assets/site-previews/sources.json) et
[vérifications](../docs/testing/HOME_SITES_REVIEW_2026-10-20.md).
L’essai n’est pas une sélection automatique, une synchronisation PC/VPS, une
intégration Flask ou une mise en production. Droits de publication des captures
non établis ; usage local d’évaluation. Relecture visuelle utilisateur attendue.
La V1 figée ci-dessous conserve l’accueil antérieur avec ses catégories.

## Versions conservées — 20 octobre 2026

[Index des versions](versions/index.html) :

Repère Git local **maquette-accueil-v1-20261020** (lot f5e73d9, intégré à main).

- **V1 retenue après comparaison** : [accueil de travail sans inclinaison](accueil.html),
  [copie figée de la carte centrale en profondeur](versions/2026-10-20-v1-profondeur/maquettes/accueil.html).
  Copie indépendante des pages, scripts, styles, polices et icônes au moment de
  la demande. [Sources, manifeste et limites](versions/2026-10-20-v1-profondeur/README.md).
- **Variante expérimentale** : [essai coverflow](accueil-coverflow.html), avec
  cartes latérales inclinées selon la nouvelle référence visuelle. Cet essai
  est finalement **non retenu** le 20 octobre ; **la V1 est la version choisie**.

Les portraits ne sont pas figés ni versionnés : `uploads_dev` est ignoré et
leurs droits ne sont pas établis. La version conservée utilise les portraits
locaux actuels s’ils sont disponibles et prévoit la silhouette en secours.
La création de l’instantané ne vaut pas vérification de ses parcours ; les
contrôles navigateur doivent être rapportés séparément.

## Dernier essai du 20 octobre — carte centrale en profondeur

Choix 1A : accueil mobile avec carte centrale au premier plan, voisines réduites
et légèrement atténuées, sans flou. Flèches, glissement manuel et clavier ;
toucher une voisine la centre, toucher la centrale ouvre le profil. Aucun fond
vert, bordure extérieure, compteur visible ou rotation automatique ajouté.
Grille ordinateur conservée. Référence UX-HOME-008 v3 dans HOME_PAGE.md ;
[contrôles et limites](../docs/testing/HOME_DEPTH_REVIEW_2026-10-20.md).
Relecture utilisateur attendue, livraison locale uniquement.

## Révision du 20 octobre 2026 — accueil compact

Accueil mobile : cartes verticales, descriptions sur deux lignes avec points de
suspension au débordement, commandes latérales et compteur visuellement masqué.
Retrait des deux textes demandés et espacements resserrés. « Tous les créateurs »
reste en fin de carrousel ; accès rapides retirés lors de l’essai du 17 octobre.
Décisions : UX-HOME-008 v2 et UX-HOME-009/010 dans HOME_PAGE.md.
[Contrôles locaux et limites](../docs/testing/HOME_VERTICAL_REVIEW_2026-10-20.md).
Relecture utilisateur attendue ; aucune intégration Flask ni publication.

Prototype public et quatre rubriques admin historiques, sans backend. Le
périmètre applicable est [Créateurs de contenu](../docs/ux/CONTENT_CREATORS_SCOPE.md).
La [revue finale](../docs/testing/MAQUETTE_FINAL_REVIEW_2026-10-17.md) décrit les
contrôles et limites. Entrée publique : accueil.html ; admin : admin.html.

## Aperçu local

Servir les pages sous /maquettes/ ainsi que /static/fonts/ et /static/icons/
avec un serveur statique local. Ne pas exposer le dépôt entier (.git, secrets,
bases). Le serveur temporaire courant écoute sur 8026 et n’autorise que les
maquettes, polices, icônes et portraits publics locaux ; il n’est pas un service
installé ni un déploiement. URL du réseau local actuel :
http://192.168.1.14:8026/maquettes/accueil.html.

Les trois portraits ../uploads_dev/2026/07/ sont des dépendances locales
facultatives, ignorées par Git. Ne pas les ajouter au dépôt : les cartes et
la fiche utilisent profile-placeholder.svg lorsqu’ils manquent. Aucun droit
sur ces images n’est établi par cette livraison. Le prototype fonctionne avec
les silhouettes dans un checkout neuf. Les polices et icônes sont locales.

## Nature des données

Les propositions, confirmations, états et actions admin sont simulés. Aucun
enregistrement, email, clic suivi, authentification ni publication réelle.
Les liens marqués ↗ peuvent ouvrir le site de développement ou un service
externe. Les sites fictifs utilisent example.org. Ne pas envoyer le formulaire
Google lors d’une simple revue de maquette. comparaison.html conserve l’ancienne
exploration visuelle A/B/C et ses textes historiques ; accueil.html est la cible.

La gestion admin V1 des catégories, clics, connexion/déconnexion et correction
de type n’est pas livrée par ces quatre rubriques : suivi distinct #34.
L’intégration publique Flask reste #18. Les comptes contributeurs sont différés.

## Révision de l’accueil après essai utilisateur — 17 octobre 2026

Carrousel manuel uniquement sur l’accueil mobile (≤680 px), grille ordinateur
conservée ; blocs Plus consultés/Derniers sites ajoutés et lien Tendances retirés.
La page Créateurs et la recherche gardent leurs listes. Voir la
[revue du carrousel](../docs/testing/HOME_CAROUSEL_REVIEW_2026-10-17.md) pour les
nouveaux tests et limites, distincts de la validation de la version antérieure.
Aucun retrait de route Flask ni déploiement effectué.


## Consolidation mobile finale du 23 octobre 2026

Les arbitrages V1 déjà validés sont désormais simulés dans
[mobile-final/admin.html](../../maquettes/mobile-final/admin.html) : connexion,
tableau de bord, propositions, sites, personnalités, catégories, clics fictifs
sur 30 jours et Contact externe. Brouillons distincts, correction du type,
contrôles humains illustratifs, publication, refus motivé et archivage utilisent
le même état temporaire que les pages publiques. Les catégories gardent leur
identifiant lors d’un renommage ; une catégorie utilisée ne se supprime pas.

[Consolidation UX-FINAL-001](FINAL_MOBILE_MOCKUP.md) et
[preuves de vérification](../testing/FINAL_MOBILE_REVIEW_2026-10-23.md).
L’extension auparavant absente est réalisée en maquette ; elle reste à relire
par l’utilisateur. Aucun backend, authentification réelle ni déploiement.
Les constats et limites datés ci-dessus restent l’historique, non l’état courant.
