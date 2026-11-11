# Accueil complet — fiche UX

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.23 |
| Date | 23 octobre 2026 |
| Statut | Navbar de la dernière version retenue ; liens contrôlés localement |
| Réalisation | Accueil local interactif adapté ; backend inchangé |

## Essai typographique du logo — 23 octobre 2026

### Choix après comparaison — UX-HOME-028 v1.0

L’utilisateur préfère finalement le titre manuscrit d’origine et demande de le
mettre un peu plus gros. Conserver Pacifico dans la version mobile courante à
catégories ; essai d’agrandissement de 28 à 32 px sur ses en-têtes publics, sans
changer le vert, les cartes ou la navbar. Montserrat n’est pas retenue pour le
moment : sa variante reste disponible à part, sans suppression, pour permettre
de changer d’avis. L’index doit ouvrir d’abord la version courante manuscrite et
identifier l’essai géométrique comme conservé pour plus tard. Vérifier le nom
complet à 320/390 px et le maintien de l’écriture après navigation.

**UX-HOME-027 v1.0 — autorisation utilisateur : proposer une nouvelle police
directement sur la maquette après critique du logo Pacifico.** Aucun choix de
remplacement définitif n’existait ; la charte complète #17 reste différée.
Réaliser un essai séparé `accueil-logo-mobile.html`, contexte `logo-mobile`,
depuis la variante à catégories et descriptions courtes. La référence Pacifico
reste conservée. Proposition d’exécution : Montserrat 900 déjà servie localement,
écriture droite, géométrique, espacement resserré et taille adaptée à l’en-tête.
Vert, nom Réunion Wiki, contenu et disposition de l’accueil restent conservés.

Le même logo suit les pages publiques de cet essai (Sites, Personnalités,
recherche, proposition et aides), sans modifier les autres contextes. Les
filtres, descriptions de deux lignes, liens, retours et navbar gardent leurs
comportements. Aucun nouveau pictogramme, slogan, police distante ou backend.
L’adoption visuelle reste à valider par l’utilisateur après comparaison.

Critères avant réalisation : nom complet lisible à 320/390 px, Montserrat locale
chargée, aucun débordement horizontal ni déplacement de la navbar ; nouvelle
écriture conservée après recherche, navigation et aide-retour ; ancienne version
Pacifico intacte et deux versions accessibles par les comparaisons datées.

## Variante mobile à catégories visibles — 23 octobre 2026

UX-SITES-007 dans [SITE_LIST.md](SITE_LIST.md) autorise une nouvelle version
mobile : `accueil-categories-mobile.html` conserve cet accueil et sa navbar,
mais ses liens Sites ouvrent `sites-categories.html`, avec catégories visibles
en petits boutons. Les pages partagées transportent `version=categories-mobile`
et les liens Accueil reviennent à cette nouvelle entrée. Les anciens contextes
et la référence `accueil-navigation-flottante.html` sont conservés ; les
bandeaux de comparaison ajoutent uniquement la nouvelle destination datée.
La validation du rendu reste distincte de l’autorisation de réaliser l’essai.

Complément UX-CREA-009 : le même contexte mobile ouvre aussi
`createurs-categories.html` depuis la navbar et les liens Personnalités. La liste
utilise un instantané des 29 profils publiés dev et les catégories existantes en
boutons, sans refonte de leur classement. Les autres contextes gardent leur
ancienne liste. Ambiguïtés de taxonomie conservées au ticket Dashboard #46.

## Variante PC séparée autorisée — 22 octobre 2026

[UX-PC-001](DESKTOP_MOCKUP_V1.md) : réalisation d’une variante ordinateur distincte
autorisée avec choix d’exécution délégués après l’audit ; version mobile retenue
préservée. Variante réalisée et vérifiée localement ; validation visuelle utilisateur attendue.
Comparaison séparée en lignes Versions mobile et Versions PC.
Aucun déploiement ou changement de backend autorisé.

## Audit ordinateur demandé — 22 octobre 2026

[Audit de la dernière maquette sur PC](DESKTOP_MOCKUP_AUDIT_2026-10-22.md), réalisé
sur l’accueil à 1366/1440/1920 px et sur les principales pages publiques. Constats
visuels, limites de simulation et pistes de reprise distingués. La navbar mobile
retenue est préservée ; aucun choix de refonte PC ni correction d’interface appliqué.
Suivi dans le ticket Dashboard #45, qui reste à reprendre après discussion.

## Dates et tri des versions — 22 octobre 2026

UX-HOME-026 v1.0 — demande utilisateur : afficher date, heure et minutes sous
chaque version et trier du plus récent au plus ancien. Les cartes de l’index et
les raccourcis des huit bandeaux de comparaison suivent le même ordre. Ajouter
une carte Petits aperçus pour représenter chaque version accessible ; Toutes les
versions reste un lien utilitaire final sans fausse date de version.

Les dates désignent l’enregistrement de l’état de référence dans Git, en UTC+4,
sans employer les dates de copie des fichiers ni les mises à jour communes des
liens. Affichage jour/mois/année · HH:mm avec time datetime complet. Navbar :
repère retenu c58d9b5 ; grandes cartes 3e5fbfd ; checkpoint 1f42337 ; petits
aperçus 4601d45 (dernier état visuel avant les grandes cartes) ; Sites validée
8e7265f ; Coverflow et Profondeur enregistrés ensemble dans f5e73d9, donc même
horaire. À égalité, ordre stable Coverflow puis Profondeur, sans inventer d’heure.

Cette datation de référence ne vaut pas date de dernière modification de chaque
ressource partagée. L’ajout d’une future version doit renseigner son enregistrement
et conserver l’ordre chronologique dans l’index et les bandeaux. Tri HTML statique,
lisible sans JavaScript. Navbar, contenus des cartes et parcours inchangés ;
les archives ne changent que leur bandeau, avec note et manifestes actualisés.
Critères : sept cartes datées, sept raccourcis datés par bandeau, dates cohérentes,
ordre décroissant, liens/état actif conservés et aucune coupure sur mobile.

Réalisation et contrôle : sept cartes datées dans l’index et sept raccourcis
datés dans chacun des huit bandeaux, ordre décroissant identique et liens
conservés. Les sept heures ont été comparées aux dates auteur/commit Git (égales).
64 liens locaux, marqueurs actifs et manifestes vérifiés. Navigateur LAN à
320/390/1280 px sans débordement ; retour depuis l’archive vers la navbar retenue
réussi. [Contrôles et provenance](../testing/VERSION_TIMES_REVIEW_2026-10-22.md).

## Navbar retenue dans la dernière version — 22 octobre 2026

UX-HOME-025 v1.0 — validation explicite de l’utilisateur : « j’adore la navbar,
garde la navbar dans la dernière version » et nouvelle vérification des liens
entre les pages. Conserver la navigation flottante de UX-HOME-024 dans
accueil-navigation-flottante.html, désormais dernière référence de maquette ;
menu supérieur sur ordinateur conservé. Cette validation porte sur la navbar,
sans valider implicitement tous les autres choix visuels ou une intégration Flask.
Les anciennes variantes restent disponibles pour comparaison. L’index distingue
la version actuelle retenue des références historiques et y revient directement.

Contrôle demandé : navigation entre les quatre rubriques, liens Accueil/logo,
retours de profil/recherche/aide, proposition simulée et changement de version.
Un défaut hérité est identifié dans l’état vide de catégorie : « Découvrir les
autres catégories » vise accueil.html#categories, section supprimée des accueils
actifs. Correction dans le parcours existant : « Explorer tous les sites » ouvre
sites.html en conservant le contexte de version ; aucun nouvel écran de catégories.
Aucun changement d’images, contenu des cartes, données ou production.

Contrôles après validation : les douze passages directs distincts entre les
quatre rubriques ont été cliqués dans le navigateur LAN à 390 px, avec destination
et onglet actif conformes. Catégorie vide → Explorer tous les sites, aide → retour
aux sites, fiche Adriana → liste filtrée, index → dernière version retenue contrôlés.
Audit indépendant : 80 cas de contexte/retours réussis et huit bandeaux cohérents.
[Complément de contrôle](../testing/NAVBAR_RETAINED_LINKS_2026-10-22.md).
Repère Git local de conservation : maquette-navbar-retenue-20261022. La validation
ne vaut ni déploiement ni vérification des destinations des sites externes.

## Essai de navigation flottante et retours cohérents — 22 octobre 2026

UX-HOME-024 v1.0 — l’utilisateur autorise l’essai proposé : barre flottante
mobile blanche arrondie, ombre légère, vert pour l’onglet actif, quatre rubriques
avec icône et libellé Accueil, Sites, Personnalités, Proposer ; sans bouton +
central. Sur mobile, elle remplace les liens de navigation du haut en conservant
le logo et sa photo ; sur ordinateur, conserver le menu du haut. Nouvelle version
accueil-navigation-flottante.html basée sur les grandes cartes, pour comparaison.
La translucidité reste légère et subordonnée à la lisibilité ; espace réservé en
bas pour ne pas cacher le contenu, prise en compte de la zone sûre du téléphone.

Correction explicitement demandée : depuis Sites, Personnalités et les autres
pages publiques de la maquette, les liens Accueil/logo/retour ne doivent plus
ramener implicitement aux petits aperçus. Les pages partagées doivent conserver
la version d’origine par contexte d’URL explicite validé, sans dépendre d’une
mémoire globale qui mélangerait les onglets. Depuis la variante flottante, garder
la barre et l’onglet actif cohérent sur les listes, la recherche, la proposition,
la fiche et les aides. Les autres variantes gardent leur navigation existante
mais bénéficient du bon retour d’accueil. Les retours intermédiaires profil vers
liste/recherche et aide vers page d’origine doivent conserver critères et version.

Le contexte n’a pas encore de traitement commun dans les documents/code lus :
les pages partagées visent accueil.html, les seuls retours profil/aide autorisent
partiellement grandes-cartes. Cette décision complète UX-HOME-022/023. Les archives
gardent leurs pages internes et leur accueil local ; seul le bandeau de comparaison
reçoit la nouvelle destination, avec historique et manifestes actualisés comme
UX-HOME-023. Aucune nouvelle photo, donnée, règle de publication ou implémentation
Flask/VPS. Pas de soumission réelle. Contributeur/admin : maquette simulée inchangée.

Critères : variante séparée accessible depuis chaque version ; barre à quatre
liens d’au moins 44 px, état actif et focus perceptibles ; 320/390 px sans débordement
ni dernier contenu caché ; menu du haut seul sur ordinateur. Tester Accueil →
Sites et Personnalités → accueil, recherche filtrée → profil → retour, proposition,
aides et changement de version ; conservation de l’hôte LAN et du contexte après
recherche, réinitialisation, retour navigateur et rafraîchissement. Les valeurs
inconnues de version et les retours externes ne doivent pas changer la destination
vers un site tiers. Ancien design conservé, nouvel essai à relire par l’utilisateur.

Réalisation locale : nouvelle page séparée, mockup-floating-nav.css et
mockup-navigation.js commun aux quatorze pages partagées existantes. Le contexte
version est limité à petits-apercus, grandes-cartes, navigation-flottante, coverflow.
Il suit les liens/formulaires/recherches/retours sans mémoire entre onglets ; les
liens explicites de comparaison sont exclus pour permettre le changement d’essai.
Les retours imbriqués sont validés à chaque niveau, bornés à huit niveaux.

Vérifié dans le navigateur LAN à 320/390/1280 px : quatre cibles de 58 px de haut,
libellés complets, menu supérieur masqué uniquement sur mobile, contenu final
accessible au-dessus de la barre. Recherche de sites, retour navigateur,
recherche de personnalité puis fiche et retour filtré, recherche globale,
catégorie filtrée, chaîne des trois aides et confirmation simulée conservent
la bonne variante. Les retours Sites/Personnalités de Grandes cartes sont aussi
contrôlés. [Preuves, limites et contrôles indépendants](../testing/FLOATING_NAV_REVIEW_2026-10-22.md).
Essai réalisé et vérifié localement ; préférence visuelle finale non encore validée.

## Navigation entre toutes les versions — 22 octobre 2026

UX-HOME-023 v1.0 — demande explicite après essai sur le réseau local : accéder à
chaque version depuis chaque version avec les liens en bas. Le bandeau précédent
n’existait que sur deux accueils et ne donnait pas directement les trois essais
plus anciens. Correction autorisée : même liste complète, état actif unique,
liens relatifs à l’hôte utilisé (PC ou téléphone), sur les six accueils et l’index.
Aucun nouvel écran, changement de sélection ou de contenu de ces maquettes.

Cette demande étend UX-HOME-022 : les trois accueils archivés reçoivent uniquement
le bandeau de comparaison et sa feuille de style partagée. Leur rendu historique
au-dessus du bandeau, leurs ressources et leurs parcours internes sont conservés.
Les états exacts d’origine restent dans leurs tags Git ; les anciens manifestes
sont gardés sous SHA256SUMS.before-version-navigation, et les manifestes courants
actualisés en signalant cet ajout dans les README. Ne pas présenter les fichiers
HTML ainsi augmentés comme strictement identiques aux instantanés originaux.

Critères : les sept points d’entrée possèdent chacun les sept mêmes destinations,
une seule version active et aucun doublon de bandeau ; chaque passage direct
entre accueils fonctionne, y compris depuis les archives ; conservation de l’hôte
LAN, chemins imbriqués valides, liens tactiles d’au moins 44 px, focus visible et
absence de débordement à 320/390 px. Maquettes locales uniquement, aucun backend.

Réalisation et contrôle : bandeau identique présent sur les sept points d’entrée,
sept liens et un état actif par page. Les 42 passages directs distincts ont été
parcourus dans le navigateur sur l’adresse LAN, puis les sept pages contrôlées
à 320/390 px effectifs ; aucune sortie d’hôte,
page absente ou perte de bandeau. Contrôle indépendant des 49 destinations sur
localhost et LAN ; contenu des accueils archivés identique hors deux ajouts.
Les manifestes historiques sont préservés et les 60/56/105 empreintes courantes
sont conformes. [Détail et limites](../testing/MOCKUP_VERSION_NAVIGATION_2026-10-22.md).

## Essai séparé de grandes cartes — 22 octobre 2026

UX-HOME-022 v1.0 : choix utilisateur 1A, commencer par les grandes cartes avec
les vraies images et le menu actuel, dans une nouvelle version indépendante
pour comparer avec le checkpoint conservé. L’utilisateur demande aussi des
liens tout en bas de la maquette pour passer facilement entre versions.

Format proposé puis accepté pour cet essai : grandes captures réelles 16:9
avec nom et catégorie sous l’image ; portraits plus présents avec informations
sous la photo. Conserver les trois sites Infinity Park, Bus.re et Eau du robinet
et les trois profils existants, leurs images et destinations pour une comparaison
à contenu égal. Sites toujours avant les personnalités. Mobile : trois cartes
de sites empilées, puis le carrousel manuel des profils ; grand écran : trois
colonnes de sites et grille de profils. Pas de nouveau geste ni de rotation.

Variante accueil-grandes-cartes.html, styles propres aux sites et aux portraits,
sans réécrire les composants communs des listes. Menu du haut, fond clair,
bannière actuelle, palette verte sans citron, recherche et proposition conservés.
Aucune navigation en bas de type application : le choix 1B n’est pas retenu ici.
Les liens Versions servent uniquement à la comparaison de maquettes et sont
placés après les outils de démonstration, au bas des deux accueils courants.
Ils donnent accès aux petits aperçus, aux grandes cartes, au checkpoint du
22 octobre et à l’index des autres versions. Les archives immuables ne sont
pas modifiées pour leur ajouter ces liens.

Visiteur : même recherche/annuaire/profil/proposition, puis liens de comparaison
accessibles au clavier et par toucher ; état de version actif annoncé. Les
retours internes et états de démonstration de l’essai doivent rester sur l’essai
quand l’origine le permet. Contributeur/admin : aucun changement de données ou
validation. Aucun nouveau portrait, téléchargement ou collecte ; fichiers existants
facultatifs et secours conservés. Si un portrait manque ou manque de définition,
le signaler dans les contrôles plutôt que promettre une qualité améliorée.

Critères avant livraison : rendu contrôlé à 320/390/1280 px sans débordement,
captures larges gardant leur ratio, textes lisibles hors des images, profils
réels et carrousel manuel utilisables, recherche/liens de versions testés,
états vide/erreur et secours, checkpoint et ancien accueil préservés hors ajout
des liens de versions. Aucun backend, base, déploiement ou nouvelle sélection
automatique. Essai local soumis à relecture, pas adoption finale du design.

Réalisation locale contrôlée le 22 octobre : variante et styles isolés disponibles ;
liens de comparaison ajoutés aux deux accueils, retour depuis le profil Adriana
et les pages d’aide adapté à cette origine. Commandes du carrousel sous les
portraits pour laisser les photos dégagées, comportement manuel conservé.
Les captures existantes sont en 1440×810 ; les trois portraits sont en 150×150,
affichés jusqu’à environ 299 px sur ordinateur : manque de netteté observé,
pas de fichier source amélioré. Texte sous les images, sans nouveau fond flouté.

Contrôles 320/390/1280 px, carrousel au clavier et boutons, recherche Adriana,
retours profil/FAQ, vide/erreur et silhouettes, comparaison des versions réussis.
104 empreintes du checkpoint conservées ; ancien accueil inchangé hors outils
de comparaison. [Détail des vérifications et limites](../testing/HOME_LARGE_CARDS_REVIEW_2026-10-22.md).
Statut : essai réalisé et vérifié localement, relecture visuelle utilisateur attendue.
Les autres pages publiques gardent leur retour Accueil habituel ; seule l’origine
explicitement portée par un lien de retour conserve la variante.

## Checkpoint avant une nouvelle direction visuelle — 22 octobre 2026

UX-HOME-021 v1.0 : l’utilisateur demande de mettre de côté et versionner la
maquette actuelle avant un éventuel essai de visuels plus grands pour les
sites ou catégories. Conserver les pages publiques et leurs ressources dans
maquettes/versions/2026-10-22-avant-refonte-visuelle/, avec provenance et empreintes,
puis créer le repère Git local maquette-avant-refonte-visuelle-20261022.
La conservation porte sur l’état réel du disque, y compris le resserrement des
espaces mobiles déjà affiché mais absent de main dans accueil-c.css. Celui-ci
est inclus dans le checkpoint sans changer le rendu actuel.

La référence comprend l’accueil avec trois sites en liste, captures 16:9 à
gauche, bannière derrière le logo/menu, carrousel Personnalités en dessous et
accents verts ; page Sites à 56 entrées et 45 captures, navigation publique et
ressources locales. Les portraits facultatifs ignorés par Git restent à leurs
chemins actuels, sans copie, avec silhouette de secours ; limites précisées
dans le README de l’instantané. Anciennes versions conservées.

Ce checkpoint n’est pas une validation d’une nouvelle mise en page. L’objectif
d’images plus grandes est discuté ; sites ou catégories, composition, nombre
de cartes et direction graphique restent à choisir. Aucune nouvelle variante,
base, règle métier ou publication autorisée par cette seule conservation.
Critères : fichiers publics conservés avec empreintes, liens et assets locaux
contrôlés, repère Git unique et ancienne référence inchangée. Git et copie sur
ce PC sont un versionnement local, pas une sauvegarde indépendante hors site.

Contrôles de conservation réalisés : 102 sources revérifiées, 104 empreintes
conformes dans chacune des deux copies et références antérieures intactes
(59 et 55 empreintes). Vérification indépendante : 307 références locales HTML
et CSS sans absence inattendue ; seuls le lien Admin exclu et huit références
de portraits externes à la copie sont les exceptions documentées. Comptes
confirmés : trois sites sur l’accueil, 56 ids uniques et 45 images WebP 1440×810
sur la liste ; correspondance à l’export et aux sources. Aucun fichier privé,
base, clé, environnement, lien symbolique ou portrait copié dans les 105 fichiers.

Les pages conservées et les ressources hero/police répondent au serveur filtré
8026. Ce contrôle HTTP et les empreintes ne constituent pas une nouvelle
validation visuelle en navigateur ; les vérifications visuelles du 20 octobre
restent celles documentées. Aucun changement de design effectué.

## Accents verts sans jaune citron — 20 octobre 2026

UX-HOME-020 v1.0 : demande de retirer le jaune citron de la flèche « Toutes les
personnalités » et des autres accents de l’accueil, pour reprendre le vert des
flèches. Pastille finale, commandes actives du carrousel et flèches des sites
emploient le fond #64886b avec pictogramme clair #f6f6ef. Remplacer aussi la
bordure citron des commandes actives par du vert. Les commandes en borne
gardent leur état vert atténué ; textes, dimensions et destinations inchangés.
Ce choix remplace la couleur citron des pictogrammes de UX-HOME-019, sans
modifier les variantes historiques ni le design des autres pages. Vérifier la
carte finale sur mobile et ordinateur, l’harmonisation et le contraste.

Contrôle navigateur : à 390 px, Suivant atteint Toutes les personnalités
(4 sur 4), pastille finale, flèches des sites et commande active ont le même
fond rgb(100,136,107) et pictogramme rgb(246,246,239). Bordure active verte.
À 1280 px, même pastille finale, aucun élément affiché avec les anciennes
couleurs citron #e5f49a/#c6d88a ; aucun débordement dans les deux formats.
Capture /tmp/rw-home-green-accents.png. Contrôle ciblé, sans audit complet
d’accessibilité ou publication.

## Flèches des sites harmonisées — 20 octobre 2026

UX-HOME-019 v1.0 : demande de mettre les flèches des sites en vert comme celles
des talents/personnalités. Appliquer aux pastilles de sortie des trois sites
de l’accueil le fond #64886b et la flèche #e5f49a des commandes actives du
carrousel des personnalités. Taille, lien externe et disposition conservés ;
aucun changement de la page Sites ou des copies figées. Maquette locale.
Contrôle navigateur à 390 px : les trois pastilles ont les mêmes couleurs
calculées que la commande active Suivant des personnalités ; aucun débordement.
Capture /tmp/rw-site-arrows-green.png.

## Fond vert du bloc de proposition — 20 octobre 2026

UX-HOME-018 v1.0 : l’utilisateur demande un fond vert, à la place du vert clair,
pour le bloc de proposition de l’accueil. Réutiliser le vert d’action existant
#087548, avec texte clair ; bouton clair à texte foncé pour rester identifiable.
Texte, destination et disposition inchangés. Adaptation limitée à l’accueil
courant, sans réécrire les variantes ou copies figées. Contrôle visuel mobile
et ordinateur, contraste des couleurs et accès au formulaire à vérifier.

Réalisation et contrôle : couleurs calculées conformes dans le navigateur à
390/1280 px, aucun débordement horizontal ; bouton de 48 px de haut, clic vers
proposer.html et retour Accueil fonctionnels, aucun formulaire envoyé.
Contrastes des couleurs unies : texte/fond 5.30:1, texte/bouton 11.05:1.
Capture /tmp/rw-home-proposal-green.png. Vérification ciblée, sans audit complet
d’accessibilité ni déploiement.

## Photo derrière le logo et la navigation — 20 octobre 2026

UX-HOME-017 v1.0 : l’utilisateur demande de mettre la photo de la bannière hero
derrière le titre Réunion Wiki (logo) et la navbar. La photo est déplacée dans
l’en-tête courant de l’accueil, avec son voile clair pour préserver les textes.
Le formulaire de recherche reste sur le fond clair sous l’en-tête. Cette demande
remplace l’emplacement derrière l’ancien hero de UX-HOME-013 ; le nouvel en-tête
illustré est appliqué aux deux présentations mobile/ordinateur, sans ajouter de
hauteur, photo distincte ou nouveau texte. Logo, liens, tailles tactiles, liste
de sites et carrousel conservés. Les anciennes décisions restent historiques.

Réutilisation locale de assets/hero/reunion-hero.webp, 1600×900, 164 328 octets,
SHA256 5c1bfd7e7f4b90fcfe0b835f2923ee29dc08918e0ed39a990660f3361b04ff70.
Aucun téléchargement ou changement de l’image, de la base ou du VPS.
Critères : fond sous le logo et les quatre liens, aucune image de fond sous la
recherche ; rendu lisible et sans débordement à 320/390/1280 px, navigation et
recherche conservées. Maquette locale, relecture utilisateur du cadrage attendue.

Contrôles observés dans le navigateur : photo sous le logo et le menu à
320/390/1280 px, fond de la recherche calculé none, aucune nouvelle hauteur
imposée au header ni débordement horizontal. Les quatre liens gardent 44 px
de haut et une ligne de menu à 320 px. Clic Sites puis Accueil fonctionnel.
Captures /tmp/rw-header-banner-390.png et /tmp/rw-header-banner-1280.png ;
lecture visuelle effectuée, aucun audit complet de contraste ou lecteur d’écran.

## Retrait de la phrase de présentation — 20 octobre 2026

UX-HOME-016 v1.0 : demande explicite de retirer également « Explore les sites
et découvre les personnalités de La Réunion. » de l’accueil courant, après
le retrait du titre. Recherche et deux sections illustrées conservées ; aucune
autre modification de présentation ou des archives. Maquette locale uniquement.
Contrôle navigateur à 390 px : phrase absente, recherche visible, aucun
débordement horizontal ; capture /tmp/rw-home-without-intro-390.png.

## Retrait du titre d’accueil — 20 octobre 2026

UX-HOME-015 v1.0 : demande explicite de retirer « Les sites utiles.
Les personnalités péi. » de l’accueil courant. Le bloc de titre est supprimé ;
le texte de présentation, la recherche, la liste de sites et le carrousel restent
à leur place. Aucun nouveau texte visible ajouté, archives figées conservées.
Contrôle attendu : titre absent et espacement du début de page cohérent sur
mobile et ordinateur. Maquette locale uniquement.
Contrôle observé : titre absent à 390 et 1280 px, sans débordement horizontal ;
capture /tmp/rw-home-without-heading-390.png. Présentation et recherche conservées.

## Liste de sites puis personnalités — décision du 20 octobre 2026

UX-HOME-014 v1.0 : après discussion vocale, l’utilisateur demande de remplacer
le carrousel de sites par une liste courte avec l’image à gauche, puis de placer
le carrousel existant des personnalités en dessous. Les images des sites et des
profils sont explicitement conservées ; aucun flou ou fond photographique de
portraits demandé à ce stade. La fiche précédente ne définissait pas ce nouvel
ordre ni ces cartes horizontales : la demande explicite valide cette adaptation.

Conserver les trois exemples Infinity Park, Bus.re et Eau du robinet, leurs
captures locales 16:9, le nom, la catégorie, la flèche et le lien externe sur
la carte entière. Liste verticale sur mobile et ordinateur, lien Explorer tous
les sites après les trois lignes. Trois exemples respectent la proposition de
3 à 5 sans ajouter de sélection manuelle ou automatique. Carrousel manuel V1
des profils déplacé après la liste : portraits, navigation, relief et grille
ordinateur conservés, sans rotation automatique ni nouveau format de portrait.

Complément explicite : remplacer les libellés Créateurs par Personnalités dans
la maquette publique ; titre Personnalités réunionnaises. Noms techniques et
URL existants conservés. L’élargissement éditorial évoqué aux sportifs/artistes
ne vaut pas modification du modèle, ajout de fiches ou règles de modération.
Les détails transversaux sont consignés dans la fiche de périmètre de rubrique.

Parcours : recherche → liste courte de sites → site externe ou annuaire local ;
puis découverte des personnalités → fiche existante ou liste. Proposition et
modération inchangées. Les états sans contenu/erreur masquent les blocs comme
auparavant ; recherche et proposition restent disponibles. Aucune pagination
de l’accueil, intégration Flask, écriture base ou publication demandée.

Critères avant livraison : ordre réel DOM et visuel, trois sites et images
intacts, une liste sans commandes de slides de sites, accès annuaire et profils,
carrousel manuel des profils encore utilisable ; 320/390/1280 px sans débordement.
Vérifier les états vide/erreur, images de secours et archives figées inchangées.
Relecture utilisateur de cette nouvelle disposition attendue.

Réalisation locale : accueil et styles adaptés ; contrôles observés à 320/390/1280 px,
carrousel manuel, menu, états vide/erreur et portraits de secours vérifiés.
[Preuves et limites](../testing/HOME_LIST_REVIEW_2026-10-20.md).

## Hero adapté à l’écran — décision du 20 octobre 2026

Après comparaison de l’essai séparé avec la photo déjà utilisée sur le VPS,
l’utilisateur retient : **fond clair sans photo sur mobile ; bannière discrète
sur ordinateur**. Il demande son intégration propre dans la maquette courante.

UX-HOME-013 v1.0 : conserver le titre, le texte et la recherche actuels. Réutiliser
la photo WebP existante, le voile clair de production (blanc alpha 0,68 vers
crème alpha 0,82) et un hero compact sur grand écran. La photo ne constitue
pas un bloc supplémentaire avant les créateurs. Réutiliser le seuil de
1000 px de la grille des créateurs pour le mode ordinateur ; en dessous,
conserver la présentation claire actuelle, y compris sur tablette étroite.
Ce seuil est un réglage d’intégration cohérent avec le composant existant,
pas une nouvelle règle générale pour les appareils.

Image vérifiée sur la production : /app/static/images/reunion-hero.webp,
1600×900 et 164 328 octets ; copie locale identique par SHA256
5c1bfd7e7f4b90fcfe0b835f2923ee29dc08918e0ed39a990660f3361b04ff70.
La maquette sert sa copie locale dans assets/hero/. Aucune image de fond
définie hors du média ordinateur ; aucune ressource distante ajoutée.

Nettoyage du seul essai hero : image migrée vers assets/hero/, styles intégrés
dans accueil-hero.css, copie d’accueil et page de contrôle devenues inutiles
retirées. L’ancienne adresse d’essai conserve une redirection vers l’accueil
courant. Les copies figées et repères de validation précédents restent intacts.
Les autres travaux, la base et la production ne sont pas modifiés par ce lot.

Critères : rendu clair à 320/390/999 px, fond photo et voile à 1000/1280 px,
aucun débordement horizontal, titre/recherche lisibles, accès aux créateurs
conservé ; recherche et navigation de l’accueil encore utilisables. Sources
et résultats à distinguer de la validation visuelle :
[HOME_HERO_REVIEW_2026-10-20.md](../testing/HOME_HERO_REVIEW_2026-10-20.md).

## Essai « À découvrir » — choix 1B, 20 octobre 2026

Validation visuelle provisoire utilisateur du 20 octobre : la maquette actuelle
est retenue et doit être conservée avant l’essai de la liste Sites à tous les
publiés. Référence : maquette-sites-v1-validee-20261020 et copie figée
maquettes/versions/2026-10-20-sites-v1-validee/. Inclut les titres et les couleurs
actuelles des flèches ; aucune modification de l’accueil n’est demandée pour
l’essai de volume de la page Sites. Cette validation ne vaut ni audit complet
d’accessibilité ni validation du backend/admin ou mise en production.

Libellés validés par l’utilisateur le même jour : **« Sites réunionnais à
découvrir »** pour le titre de cette section de l’accueil, **« Sites réunionnais »**
pour la page dédiée et **« Sites »** dans le menu. Ce complément remplace
uniquement le titre court « À découvrir » ci-dessous ; présentation et parcours
restent identiques.

Demande utilisateur : essayer dans la maquette de l’accueil trois sites réels
présents en base Réunion Wiki, avec de véritables captures de leur accueil.
Réponse explicite **1B** : carrousel horizontal simple sur mobile, grande carte
et aperçu de la suivante, déplacement manuel et flèches. La fiche précédente
ne définissait pas ce bloc ; le présent ajout documente l’essai avant modification.

**UX-HOME-012 v0.1 — essai validé, adoption produit non décidée :** remplacer
les accordéons de catégories de l’accueil de travail par « À découvrir ».
Conserver le bloc des créateurs et son relief V1 sans modification. Sur ordinateur,
afficher ensemble les trois cartes de sites. Chaque carte comprend un aperçu
16:9, le nom, la catégorie et une flèche ; le lien entier ouvre le site externe
dans un nouvel onglet, conformément aux accès externes de la maquette. Le lien
« Explorer tous les sites » mène à recherche-sites.html, annuaire de démonstration
existant (ses données restent fictives). Aucun parcours de fiche de site inventé.

Exemples choisis dans la **base de production lue sans écriture le 20 octobre** :
Infinity Park (id 87, Culture & Loisirs), Bus.re (id 65, Transport), Eau du robinet
(id 81, Santé). Sélection fixe pour comparaison visuelle ; ni dates réelles de
publication, ni sélection automatique, ni diversité calculée ne sont simulées.
Le schéma de production observé ne possède pas encore published_at : ne pas
présenter l’ordre des exemples comme un tri par publication vérifié.

Captures réalisées ponctuellement sur le PC, compressées et servies localement.
Aucun traitement périodique, transfert VPS ou changement de base autorisé dans
cet essai. Sources et limites des images à conserver avec les captures ; le test
ne tranche pas les droits de reproduction pour une publication du futur produit.

Critères avant livraison : trois images réelles et lisibles au format 16:9 ;
aperçu de la carte suivante à 320/390 px, trois colonnes sur ordinateur ; aucun
débordement horizontal de page ; flèches, bornes sans boucle et navigation clavier ;
zones tactiles de 44 px pour les commandes ; liens externes annoncés ; remplacement
si capture absente ; aucune requête aux sites externes au chargement de l’accueil.
Respecter le mouvement réduit et garder un défilement natif sans JavaScript.
Rejouer les états de démonstration existants pour détecter les erreurs de script ;
ils ne constituent pas de nouvelles décisions produit pour les états du futur bloc.
Documenter les résultats séparément ; adoption visuelle finale attendue.

Réalisation : accueil.html, accueil.js et fichiers dédiés home-sites.css/js ;
captures sous maquettes/assets/site-previews/. Les cartes de créateurs et
home-carousel.js sont conservés. Résultats et limites :
[HOME_SITES_REVIEW_2026-10-20.md](../testing/HOME_SITES_REVIEW_2026-10-20.md).

Correction après relecture du même jour : l’utilisateur signale les flèches
manquantes sur les slides de sites. Elles étaient réalisées sous les cartes,
hors de la partie visible de son aperçu. Rendre les commandes déjà prévues
immédiatement repérables au niveau des slides : boutons latéraux de 44 px sur
mobile, sans modifier le carrousel simple 1B ni la grille ordinateur. Le lien
Explorer tous les sites reste sous les cartes. Vérifier visibilité, clics et
absence de débordement à 320/390 px avant livraison de cette correction.

UX-HOME-006 et les exigences de catégories précédentes restent historiques et
applicables hors de cet essai local. Cet essai ne vaut pas réouverture des tendances,
intégration Flask, automatisation de captures ou publication.

## Choix retenu après comparaison — V1, 20 octobre 2026

L’utilisateur préfère finalement la version précédant la demande d’inclinaison
selon la nouvelle image : **V1, carte centrale au premier plan, voisines
réduites et légèrement atténuées, sans inclinaison**. UX-HOME-008 v3.0 reste
applicable. L’entrée accueil.html présente déjà ce rendu ; l’instantané
versions/2026-10-20-v1-profondeur reste intact avec son repère Git.
L’essai UX-HOME-011 v0.2 est **non retenu**, conservé pour historique et
comparaison, sans intégration à la cible. Aucun backend ni déploiement demandé.

## Historique de l’essai — perspective inclinée, 20 octobre 2026

Demande explicite : versionner la maquette actuelle pour y revenir facilement,
puis essayer la nouvelle référence visuelle où les cartes latérales sont
inclinées en perspective. Autorisation de préparer et comparer une variante,
pas validation de son adoption. La V1 figée conserve UX-HOME-008 v3.0 ci-dessous.

UX-HOME-011 v0.1 (essai) : entrée accueil-coverflow.html dédiée ; même contenu,
petits portraits, carte centrale droite et lisible, voisines orientées autour
de l’axe vertical et reculées dans la profondeur. Conserver fond clair, absence
de flou, navigation manuelle, flèches/clavier/glissement, absence de boucle et
Tous les créateurs en fin. Ordinateur inchangé. La référence ne valide ni un
fond sombre, ni l’agrandissement des portraits, ni une dépendance d’animation.

Correction demandée le même jour — UX-HOME-011 v0.2 : la réalisation initiale
inclinait les cartes dans le sens opposé à la référence. Le bord de chaque
carte latérale situé vers le centre doit paraître plus proche et plus haut ;
son bord extérieur recule. Rotation Y négative à gauche, positive à droite,
centrale à zéro. Cette précision corrige l’essai sans modifier la V1 figée.

Critères avant comparaison : V1 encore accessible indépendamment des fichiers
de l’essai ; manifeste vérifiable ; perspective visible sans débordement à
320/390 px ; centrale lisible et accessible ; bornes, lien final, retour fiche,
texte long et silhouette préservés. Contrôles de la variante à consigner
séparément ; relecture utilisateur nécessaire pour choisir entre V1 et essai.

Réalisation et contrôles de l’instantané et de l’essai :
[HOME_COVERFLOW_REVIEW_2026-10-20.md](../testing/HOME_COVERFLOW_REVIEW_2026-10-20.md).

## Référence conservée — cartes superposées, 20 octobre 2026

Après les deux références visuelles fournies, choix utilisateur **1A** : carte
centrale au premier plan, cartes latérales réduites et légèrement atténuées,
sans flou. UX-HOME-008 v3.0 remplace l’aperçu côte à côte sur le seul accueil
mobile ; les cartes verticales et retraits de textes/fond/bordure restent acquis.
La grille ordinateur est conservée. Aucune rotation automatique ni boucle :
bornes, ordre des profils et dernière carte Tous les créateurs conservés.

Détails de la maquette : flèches et balayage horizontal changent le profil
central ; toucher une carte latérale la centre, toucher la carte centrale ouvre
son lien. Au clavier, flèches/Début/Fin sur la zone et lien central accessible
par Tab ; les cartes atténuées ne sont pas des arrêts Tab supplémentaires.
Le défilement vertical de page doit rester possible. Sans script, le carrousel
natif précédent reste disponible ; mouvement réduit sans animation.

Acceptation : relief sans flou ni débordement à 320/390 px, carte centrale
entièrement lisible, navigation/bornes et lien final, description longue et
silhouette, état vide/erreur, retour de fiche et grille ordinateur. Vérification
de cette nouvelle réalisation à consigner séparément des preuves précédentes.

## Historique — cartes verticales, 20 octobre 2026

Demande utilisateur dans la conversation « Préparer maquette et vidéo » : photo
en haut, nom en dessous, mini-description terminée par trois points lorsqu’elle
est tronquée ; flèches de part et d’autre de la carte, sans compteur visible.
« Trois petits » désigne les points de suspension, pas trois cartes simultanées.
Cette demande tranche l’ambiguïté soulevée dans la conversation avant modification.

| Référence | Décision applicable |
| --- | --- |
| UX-HOME-009 v1.0 | Accueil mobile uniquement : carte verticale, petit portrait conservé à 96 px maximum, nom, catégorie, courte description et accès au profil. Description visuelle limitée à deux lignes avec points de suspension si elle dépasse ; texte complet conservé dans le document. Remplace la disposition horizontale et l’exigence de présentation intégrale sur cette seule sélection. Liste, recherche et grille ordinateur conservent leurs cartes actuelles. |
| UX-HOME-008 v2.0 | Flèches manuelles à gauche/droite du carrousel, centrées sur la carte ; retirer le compteur visuel « 1 sur 4 », conserver l’annonce de position pour les technologies d’assistance. Glissement, clavier, bornes sans boucle, aperçu suivant et lien final Tous les créateurs conservés. |
| UX-HOME-010 v1.1 | Retirer « Portail local · La Réunion » et « Humour, culture, vidéos… des talents à découvrir. » de l’accueil ; resserrer les espacements titre/texte/recherche et entre les textes des cartes. Complément utilisateur du 20 octobre : retirer aussi le fond vert du bloc Créateurs réunionnais, sur le fond de page existant. |
| UX-HOME-001 v3.0 | Recherche → créateurs → catégories → proposition ; accès rapides retirés selon la demande finale du 17 octobre. « Tous les créateurs » reste la dernière carte du carrousel. Remplace les mentions de raccourcis conservés dans la révision antérieure. |

Périmètre : maquette locale, sans backend ni déploiement. Acceptation avant
livraison : rendu 320/390 px sans débordement, photo au-dessus du nom, texte
long tronqué visuellement avec accès au profil intact, commandes latérales
utilisables et sans compteur visible ; grille ordinateur préservée. Les états
vide/erreur et le lien final doivent rester utilisables. Relecture utilisateur
du nouveau rendu attendue après réalisation ; essais tactiles physiques distincts.

Complément utilisateur du 20 octobre (UX-HOME-010 v1.2) : retirer également
la bordure extérieure du bloc Créateurs réunionnais après son fond vert.
Les bordures des cartes et boutons ne sont pas concernées.

## Historique — carrousel mobile, 17 octobre 2026

Après essai de la maquette par un tiers, l’utilisateur valide `1B 2A 3A 4A 5A`,
puis précise « Pour les tendances je veux plus que le public voit » et répond
6C (retirer le lien de l’accueil). Cette décision remplace les exclusions du
carrousel et les parties relatives aux classements/nouveautés des choix du
8 octobre. Elle porte sur les créateurs de contenu, pas une réouverture à tous
les métiers. Les sections et preuves antérieures ci-dessous restent historiques.

### Décisions et critères applicables

| Référence | Décision validée et conséquence |
| --- | --- |
| UX-HOME-001 v2.0 | Ordre : recherche → accès rapides → créateurs → catégories → proposition. Retirer entièrement Plus consultés et Derniers sites ajoutés de l’accueil, sur mobile et ordinateur. Les aperçus de deux sites dans chaque catégorie restent selon UX-HOME-006 ; ce ne sont pas le bloc global de nouveautés. |
| UX-HOME-008 v1.0 | Carrousel uniquement pour la sélection de créateurs de l’accueil mobile, au seuil existant 680 px. Déplacement manuel par glissement, précédent/suivant et clavier ; une carte complète et une partie de la suivante visibles au début. Pas de rotation automatique. |
| UX-HOME-002 conservée | Jusqu’aux trois derniers créateurs publiés, par publication décroissante. Garder Tous les créateurs. Aucun profil supplémentaire ni sélection de popularité implicite. |
| UX-CREA-005/007 complétées | Contenu et petit portrait des cartes communs conservés ; seul le conteneur mobile de l’accueil défile. Grille ordinateur actuelle, liste Créateurs et recherche inchangées. |
| UX-HOME-007 v2.0 | Zéro créateur : masquer tout le bloc. Un créateur : carte seule et pas de commandes inutiles. Les blocs de sites retirés ne réapparaissent dans aucun état. Catégories, recherche, accès rapides et proposition conservés. Erreur de chargement signalée distinctement. |
| UX-GEN-009 v2.0 | Aucun lien Tendances public dans la maquette ; tendances hors expérience publique cible. Le retrait effectif de la route Flask publique /tendances sera traité lors de l’intégration #18, avec ses liens/sitemap/SEO ; aucun changement backend autorisé ici. Les clics et leur consultation privée restent conservés. |

### Détails de fonctionnement de la maquette

Pas de boucle de fin vers le début : commandes désactivées aux bornes ;
indication de position utile quand plusieurs cartes débordent. La navigation
verticale de la page reste possible. Le défilement ne déplace pas le focus ;
les flèches/Début/Fin agissent lorsque la zone est focalisée ; Tab/Entrée
permettent d’atteindre les liens et profils sans les déplacer hors champ.
Sans JavaScript, défilement horizontal natif disponible sur mobile ; pas de
commandes simulées inactives. Respect de prefers-reduced-motion.

Au retour de la fiche, conserver la page d’origine déjà validée et la position
du carrousel de la session lorsque possible ; au redimensionnement, recalculer
les bornes et revenir à la grille ordinateur. Aucun stockage serveur ajouté.
Les cartes longues restent lisibles sans supprimer catégorie, présentation ou
accès au profil ; silhouettes locales si image absente. Les détails purement
techniques d’ajustement sont à vérifier sur rendu réel, pas déclarés testés ici.

### Parcours et périmètre

Visiteur : accueil mobile → déplacement manuel → fiche → retour accueil au
profil lu. Sur ordinateur : accès direct depuis la grille existante.
Contributeur/admin : proposition, modération, brouillon/publication/archivage
inchangés ; seuls les publiés entrent dans la sélection. Pas de compte,
classement, nouveau CRUD ni changement des périodes de clics. Les tendances
publiques sont retirées de la cible, pas les données statistiques privées.

### Réalisation et vérification de la révision

Décisions consignées avant modifications. Critères préparés dans
[HOME_PAGE_MOCKUP_CHECKS.md](../testing/HOME_PAGE_MOCKUP_CHECKS.md).
Réalisation locale et contrôles partiels de cette révision consignés dans
[HOME_CAROUSEL_REVIEW_2026-10-17.md](../testing/HOME_CAROUSEL_REVIEW_2026-10-17.md).
Relecture visuelle utilisateur attendue. La validation et la
clôture #14 précédentes restent une preuve de la version antérieure, pas de ce
carrousel. L’intégration publique reste un chantier distinct.

## Décision applicable — créateurs de contenu, 17 octobre 2026

Le [périmètre de lancement](CONTENT_CREATORS_SCOPE.md) remplace l’ouverture générale aux
Talents péi du 16 octobre : **créateurs de contenu**, rubrique **Créateurs** et
**Proposer un créateur**. Les autres talents restent une piste reportée.
Les compléments du 16 octobre ci-dessous sont historiques sur le nom et
l’élargissement ; ils ne doivent pas guider une adaptation artiste/artisan.
RM-TAL-012 v2.0 et UX-CONT-001 à 006 font référence.

Nom et lien officiel restent obligatoires à la proposition (UX-PROP-002), sans
compte au lancement ; aucune proposition sans lien ajoutée. Contact/email pour
les corrections et retraits, tableau de bord différé. Les choix de présentation
et de navigation existants sont conservés. Documentation seule : aucun code,
maquette ni test fonctionnel modifié ou exécuté.

## Historique — complément Talents péi du 16 octobre 2026, remplacé sur le périmètre

La [fiche de périmètre](TALENTS_PEI_SCOPE.md) fait référence : UX-TAL-001 à
006 et RM-TAL-012, personnes et collectifs, dont artistes et artisans ; fiches
d’entreprises hors de cette rubrique au lancement. Le menu et le bloc de découverte ciblent Talents péi ; la sélection reste celle des derniers profils publiés selon UX-HOME-002, sans changer l’ordre des blocs.

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Sources et périmètre

Sources : PRODUCT.md, UX-GEN-009, HOME_SEARCH.md, CREATOR_LIST.md,
CATEGORY_PAGE.md, UNIFIED_SUBMISSION.md, RM-SITE-004/006/008/009 et catalogue
RM-07/18/19/21/37. Suivi du travail : Dashboard #14, conception accueil avant
contrôles globaux et intégration #18. La charte complète #17 reste différée.

L'accueil oriente vers ressources et créateurs et permet de proposer un contenu.
Ne pas ajouter de compte, personnalisation, classement de créateurs, carrousel
ou widgets sociaux dans cette première version.

## Décisions déjà validées à réutiliser

- Menu Accueil · Créateurs · Proposer ; Tendances des sites accessible près des
  plus consultés, sans nouvel onglet de menu (UX-GEN-009).
- Recherche commune créateurs/catégories de sites/sites, lancée explicitement ;
  résultats par type, sections vides masquées et clic direct sans Affiner par
  section. Présentation allégée et bloc citron conservé selon HOME_SEARCH.md.
- Cartes créateurs communes accueil/liste/recherche, horizontales sur PC/mobile,
  petit portrait, nom/catégorie/présentation/profil dans cet ordre. Catégorie
  jamais sur le portrait ; portraits 120 px PC/96 px mobile selon UX-CREA-007.
- Catégories de sites repliables sur mobile selon la direction C ; accès vers
  leurs pages complètes. Ne pas assimiler la catégorie d'un site à celle d'un créateur.
- Nouveautés par date de publication des sites (RM-SITE-009/RM-21) ; popularité
  stable sur 30 jours et tendances sur 7 jours (RM-SITE-008). Aucune préférence
  d'affichage ne modifie ces périodes ou la visibilité des statuts.
- Proposition commune accessible par menu et bloc en bas de l'accueil, page
  dédiée sans compte. Le proposant ne publie rien directement (UX-PROP-011).
- Seuls sites/créateurs publiés exposés ; archivage retire des listes, absence
  de portrait gérée par image générique. Ressources locales et finitions C.

## Ordre validé — précision utilisateur du 8 octobre 2026

`UX-HOME-001` : conserver l'ordre de la maquette : recherche → accès rapides
→ créateurs réunionnais → Un site pour chaque besoin → plus
consultés/nouveautés → proposition. Il s'agit de l'accueil avant toute recherche,
pas de l'ordre des sections sur la page de résultats. Les accès rapides sont désormais validés par le choix manuel A ci-dessous ;
la précision initiale d’ordre ne les avait pas validés implicitement.

La proposition précédente de passer les catégories avant les créateurs n'est
pas retenue. Cette validation initiale d’ordre ne tranchait pas les sélections ; celles-ci
sont désormais définies dans les décisions ci-dessous.

## Sélections validées — réponses 2A et 3A

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-HOME-002 | Jusqu'à trois derniers créateurs publiés, triés par date de publication décroissante. Moins de trois : tous disponibles ; brouillons/archivés exclus. Pas de classement par audience et pas de sélection manuelle implicite. |
| UX-HOME-003 | Toutes les catégories de sites accessibles dans une présentation compacte ; catégories repliables sur mobile selon la direction validée. Ne pas limiter silencieusement à trois catégories d'exemple. |

Dates de publication et ordre admin existent dans le modèle ; leur lecture ne
prouve pas l'accueil testé. Ces choix ne modifient ni ordre alphabétique de la
liste Créateurs ni cartes/portraits communs déjà validés. Les alternatives de
sélection manuelle/alphabet et de trois catégories seulement ne sont pas retenues.

## UX-HOME-004 — accès rapides manuels, choix A validé

Garder jusqu'à trois raccourcis textuels discrets vers des catégories choisies
par l'utilisateur/administrateur, sans sélection automatique des plus consultées.
Le choix est celui du dernier échange (catégories choisies manuellement plutôt
que par visites) ; ne pas le confondre avec le 4A initial qui proposait de retirer
les raccourcis. Une action ouvre la catégorie complète, pas une recherche préremplie.

Ils facilitent l'accès aux ressources du quotidien avant les créateurs, surtout
sur mobile. Les plus consultés restent un bloc distinct fondé sur les clics.
La liste complète de catégories reste accessible plus bas. Aucun carrousel,
widget ou nouveau panneau ajouté. Catégories exactes définies par UX-HOME-005 ci-dessous.

Historique : le retrait avait été recommandé puis reconsidéré avec l'ordre
créateurs avant catégories ; aucune de ces propositions non validées n'avait
modifié la maquette. Le maintien manuel est maintenant validé.

## Raccourcis et aperçus validés — réponses 5A et 6A

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-HOME-005 | Raccourcis Météo, Transports et Emploi, dans cet ordre, vers les catégories complètes correspondantes. Employer les libellés courts sur l'accueil et les slugs/libellés canoniques existants en destination ; Emploi peut ouvrir Emploi & formation. Pas de choix selon les visites. |
| UX-HOME-006 | Aperçu de chaque catégorie : jusqu'à deux derniers sites publiés, par date de publication décroissante. Un seul site publié : un seul affiché ; aucun : ne pas inventer de site. Respecter les dates métier RM-SITE-009 et exclure les statuts non publics. La catégorie complète garde son ordre alphabétique validé, distinct de cet aperçu. |

Les alternatives popularité ou absence d'aperçu ne sont pas retenues. Le code
actuel qui privilégie vedette/clics cumulés diffère de UX-HOME-006 ; cette règle
est une décision produit à intégrer ultérieurement, pas un comportement déjà
vérifié. Les trois derniers créateurs suivent UX-HOME-002, pas ce tri des sites.

## UX-HOME-007 — blocs sans contenu, réponse 7A validée

Masquer les blocs Créateurs, Nouveautés et Plus consultés lorsqu'ils n'ont
aucun contenu public admissible. Exemple : aucun créateur publié → aucun titre
ni carte fictive de ce bloc, passage direct aux catégories. Aucun clic admissible
→ pas de faux classement. Ne pas cacher un bloc contenant au moins un résultat.

Conserver toutes les catégories selon 3A : une catégorie vide reste accessible
avec nombre zéro et sa page dédiée vide/proposition selon UX-CAT-007. Recherche,
accès rapides et bloc de proposition restent disponibles. Le masquage du
classement ne doit pas supprimer l'accès aux Tendances déjà validé par UX-GEN-009.

La variante B (titre conservé avec phrase de liste vide) n'est pas retenue pour
ces blocs. Ce choix vient d'une validation propre à l'accueil, pas d'une
transposition implicite de la recherche. Une erreur technique reste signalée
comme erreur, jamais interprétée comme absence de contenu.

Pas de question de conception bloquante identifiée avant adaptation de maquette.
Les critères ci-dessous doivent être préparés avant code ; toute nouvelle
ambiguïté observée devra être signalée. Ces validations n'autorisent pas à elles
seules une implémentation Flask, un nouveau CRUD, une migration ou un déploiement.

## Parcours et états

- Visiteur pressé : recherche → résultats → catégorie/site/fiche ; retour de
  recherche selon parcours validé. Visiteur en découverte : blocs d'accueil →
  liste catégorie ou créateurs → fiche/site → retour. Mobile : sections lisibles,
  pas de carrousel ni scroll horizontal imposé pour atteindre un résultat.
- Contributeur : menu ou bloc Proposer → formulaire commun → erreurs/doublon
  selon parcours existant → confirmation, sans ajout immédiat dans l'accueil.
- Administrateur : publication rend le contenu admissible aux blocs ; correction
  conserve les dates métier applicables ; archivage retire du public. Aucun droit
  public de changer une sélection admin.
- Créateurs absents : bloc masqué selon UX-HOME-007, sans fausse carte. Catégorie vide : route catégorie et proposition selon
  UX-CAT-007. Aucun clic admissible : pas de faux classement, conserver accès aux
  catégories/nouveautés. Pas de nouveautés : bloc masqué sans inventer de date.
- Erreur technique distincte d'une vraie liste vide. Le comportement de secours
  et les messages seront détaillés avant réalisation, après choix des blocs.

## État antérieur constaté par lecture, avant adaptation

La maquette affiche actuellement recherche → trois créateurs illustratifs →
trois catégories avec deux sites chacune → plus consultés/nouveautés → proposition.
Les accès rapides sont des spans non interactifs. Toutes les catégories renvoie
à la même ancre, sans révéler d'autres catégories. Les nombres et classements
sont illustratifs, pas une preuve de données réelles.

Le service site_service::get_featured_sites_by_category privilégie les sites
mis en vedette, puis clics cumulés/date d'ajout, jusqu'à trois par catégorie.
Cette lecture n'est pas une validation produit de la sélection ni un test du
classement sur la période validée. Les écarts au futur choix doivent rester
explicites, sans réécrire les exigences pour reproduire le SQL existant.

## Critères préparés et vérifications locales

Après décisions : couverture/ordre des blocs et liens réellement accessibles,
sélection des profils/sites, cases zéro/un/plusieurs, compteurs cohérents,
statuts exclus, clavier/focus, contrastes et textes longs à 320/390 px et PC.
Définir les contrôles depuis les exigences avant code. Distinguer vérification
locale de la maquette des tests Flask et des données actives.

## Réalisation locale — 8 octobre 2026

`accueil.html`, `accueil.js` et `accueil-c.css` adaptés après validation.
`search-data.js` fournit le même catalogue et les mêmes dix sites fictifs que
les recherches/catégories : cinq catégories toutes affichées. Les dates/statuts
et agrégats de popularité sont simulés, jamais lus de la base active.

- Raccourcis Météo/Transports/Emploi réellement cliquables, slugs canoniques.
- Trois créateurs par dates de publication fictives ; brouillons/archivés de
  contrôle exclus. Un quatrième publié plus ancien n'entre pas dans la sélection.
- Jusqu'à deux récents par catégorie ; compteurs globaux des publiés et non du
  nombre de lignes d'aperçu. Emploi compte six et montre Passerelle/ Déclic.
- Catégories repliées sur mobile et ouvertes sur PC ; Météo vide accessible.
- Les plus consultés et nouveautés gardent deux lignes comme dans la maquette
  initiale. Les règles de périodes/dates restent applicables à l'intégration.
- État sans contenu : blocs vides masqués, cinq catégories zéro visibles,
  recherche/proposition/Tendances disponibles. Un contenu et Sans clics testés.
- Erreur distincte avec Réessayer vers état normal ; aucune fausse liste vide.

Sous-agent : grille de contrôles préparée avant code et relecture ciblée sans
modification concurrente du code. Vérifications navigateur : recherche via
Entrée, raccourci Météo, catégorie Emploi via dépliage clavier, états 0/1/4
créateurs et zéro clic, erreur/Réessayer, rendus 390/1440 et largeur 320 px sans
débordement. Compteurs et exclusion des fixtures non publiques contrôlés.
Détails et contrôles partiels dans `testing/HOME_PAGE_MOCKUP_CHECKS.md`.

Limites : cinq catégories du catalogue de démonstration, pas du référentiel
actif. Dates des trois créateurs fictives, pas leurs véritables dates de
publication. Popularité simulée, tracking/statuts/backend non testés. Portraits
sans source meilleure, liens de sites vers example.org et certains profils vers
dev. Pas de traitement admin ni publication ; validation visuelle utilisateur de
l'accueil complet encore attendue, contrôles globaux/finalisation Git distincts.

Aperçu local : `http://127.0.0.1:8765/maquettes/accueil.html?apercu=home-complet-final`.
Captures temporaires : `/tmp/reunion-wiki-accueil-complet-mobile.png` et
`/tmp/reunion-wiki-accueil-complet-pc.png`.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.20 | 20 octobre 2026 | UX-HOME-014 : sites en liste illustrée en premier, carrousel des personnalités en dessous, images conservées et renommage public demandé. |
| 0.19 | 20 octobre 2026 | UX-HOME-013 validée : fond clair sur mobile, bannière du VPS discrète sur ordinateur dans l’accueil courant ; essai séparé nettoyé. |
| 0.17 | 20 octobre 2026 | Libellés validés : Sites réunionnais à découvrir sur l’accueil, Sites réunionnais sur la page dédiée, Sites au menu. |
| 0.16 | 20 octobre 2026 | Correction après relecture : flèches des sites remontées de part et d’autre des slides mobiles pour rester visibles ; carrousel 1B et grille ordinateur conservés. |
| 0.15 | 20 octobre 2026 | Essai Sites « À découvrir », réponse 1B : carrousel horizontal simple et trois captures réelles locales ; catégories retirées de l’accueil de travail, V1 figée conservée. Aucun backend ni automatisme. |
| 0.9 | 17 octobre 2026 | Révision après essai utilisateur : carrousel accueil mobile, retrait des deux blocs de sites et des tendances publiques ; choix et limites tracés. |
| 0.8 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.7 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 0.6 | 8 octobre 2026 | Accueil adapté localement après validation : sélections, raccourcis, toutes catégories et états contrôlés ; preuves/limites consignées, backend inchangé. |
| 0.5 | 8 octobre 2026 | 7A validé : blocs Créateurs/Nouveautés/Plus consultés masqués si vides, catégories/recherche/proposition conservées ; prêt pour maquette, pas de réalisation. |
| 0.4 | 8 octobre 2026 | 5A/6A validés : Météo/Transports/Emploi et deux derniers sites publiés par catégorie ; un choix d'état vide reste ouvert avant maquette. |
| 0.3 | 8 octobre 2026 | A manuel des accès rapides, 2A et 3A validés : trois récents publiés, toutes catégories ; raccourcis exacts et aperçus de sites encore ouverts, pas de maquette modifiée. |
| 0.2 | 8 octobre 2026 | Ordre actuel de maquette conservé par utilisateur, formulation avant/après recherche clarifiée ; utilité des accès rapides réexaminée avec créateurs avant catégories, aucun choix implicite. |
| 0.1 | 8 octobre 2026 | Fiche complète créée avant changement : sources validées, quatre propositions et questions de sélection/états encore ouvertes. |

## Relecture et validation du 17 octobre 2026

L’utilisateur confirme que la présentation publique et les parcours vus lui
conviennent et demande la finalisation des contrôles. Preuves et limites
actuelles : [revue finale](../testing/MAQUETTE_FINAL_REVIEW_2026-10-17.md).
Messages au tutoiement et libellés créateurs harmonisés dans la maquette ;
aucune intégration Flask ni publication. Le contrôle mobile des quatre
rubriques admin historiques est maintenant observé à 320/390 px effectifs ;
l’extension admin V1 non réalisée reste au suivi #34, sans validation implicite.
Les mentions d’attente antérieures restent historiques et ne rouvrent pas
les choix publics déjà validés.
