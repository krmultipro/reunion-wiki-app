# Liste Sites — maquette simple

## Nouvelle variante mobile à catégories visibles — 23 octobre 2026

**UX-SITES-007 v1.0 — choix utilisateur validé, réalisation autorisée.**
Après discussion sur la longue liste, l’utilisateur choisit des petits boutons
visibles pour chaque catégorie et « Toutes les catégories » pour réafficher tous
les sites. Il délègue le dessin des boutons, cohérent avec le site, puis demande
une nouvelle version mobile. La présentation proposée et acceptée utilise des
pastilles arrondies sur plusieurs lignes, fond clair et contour discret ; la
catégorie sélectionnée porte un fond vert profond et un texte blanc.

Ce choix remplace l’absence de filtre de UX-SITES-002/005 **dans une variante
séparée uniquement** : `sites-categories.html`, depuis
`accueil-categories-mobile.html`. La référence à navbar retenue, ses cartes et
la variante PC sont conservées. La fiche dédiée existait et laissait les filtres
ouverts après essai de volume ; aucune nouvelle règle métier n’est nécessaire.

### Comportement et critères avant réalisation

- Afficher les neuf catégories existantes sans en inventer ni en renommer ;
  sélection unique, bouton « Toutes les catégories » actif par défaut.
- Les boutons restent tous visibles sur plusieurs lignes, avec cibles d’au
  moins 44 px, focus perceptible et sélection annoncée (`aria-pressed`).
- Combiner catégorie et recherche existante sur nom/catégorie, conserver le tri
  alphabétique, les 56 cartes, 45 captures et remplacements actuels.
- Conserver recherche et catégorie dans l’URL ; rechargement, précédent/suivant
  navigateur et aide/retour retrouvent les critères et la nouvelle variante.
  Une catégorie inconnue ne filtre pas silencieusement la liste.
- Retirer seulement la recherche garde la catégorie ; l’état sans résultat
  permet d’effacer tous les critères. Une erreur est distincte du zéro résultat
  et « Réessayer » garde les critères.
- La navbar mobile retenue accompagne la nouvelle variante ; ses liens Accueil
  et Sites ouvrent les nouvelles pages. Les versions précédentes restent
  accessibles dans la comparaison et gardent leurs parcours propres.
- Vérifier les largeurs effectives 320/390 px, un écran plus large, les textes
  longs, clavier, catégorie Santé (1 site), Transport (7), Culture & Loisirs (18),
  recherche combinée et état vide, retour aide et absence d’effet sur l’ancienne
  version. Les observations navigateur seront consignées séparément.

La pagination reste une proposition non validée et n’est pas incluse. Aucun
nouveau compteur visible, compte, favori, source d’image, backend, écriture de
données ou déploiement. Contributeur et admin gardent leurs parcours simulés.
La nouvelle présentation reste à relire par l’utilisateur après réalisation.

## Navigation des variantes de maquette — 22 octobre 2026

[UX-HOME-024](HOME_PAGE.md) complète ce parcours : les liens entre pages partagées
conservent la version d’accueil via un contexte d’URL explicite autorisé ;
Accueil/logo revient à cette version. Les retours intermédiaires gardent leur
page d’origine et leurs critères. Dans l’essai Navigation flottante seulement,
les quatre rubriques restent accessibles en bas sur mobile ; les autres versions
conservent leur menu. Aucun changement des règles métier ou du backend.

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.6 |
| Date | 23 octobre 2026 |
| Statut | Référence à trois sites validée ; essai à 56 sites et 45 aperçus réalisé localement |
| Réalisation | Maquette locale réalisée et contrôlée ; aucune intégration Flask |

## Demande et sources

### Validation provisoire — 20 octobre 2026

L’utilisateur confirme apprécier la maquette actuelle et demande de la valider
avec un repère avant d’ajouter tous les sites publiés. La version à trois sites,
son accueil, la liste Créateurs et la navigation actuelle constituent une
référence visuelle provisoire retenue. Les titres, mini-descriptions et couleurs
des flèches présents au moment de cette validation sont conservés.
Cette validation n’est pas un audit complet d’accessibilité, une validation des
écrans admin ou des parcours backend, ni une autorisation de publication.

Référence à conserver avant l’évolution : copie indépendante dans
maquettes/versions/2026-10-20-sites-v1-validee/ et repère Git local
maquette-sites-v1-validee-20261020. Le repère doit désigner l’état à trois sites,
pas la future liste complète. Les preuves de fonctionnement antérieures restent
valables dans leurs limites ; l’essai de volume nécessite ses propres contrôles.

L’utilisateur demande « onglet site aussi simple comme page createur de la
maquette ». Aucune fiche dédiée à une liste Sites simplifiée n’existait.
Cette fiche est créée avant la modification. Références :
[CREATOR_LIST.md](CREATOR_LIST.md), simplification UX-CREA-008 du 20 octobre ;
[HOME_PAGE.md](HOME_PAGE.md), trois sites réels et captures UX-HOME-012 ;
[PUBLIC_SEARCH.md](PUBLIC_SEARCH.md), recherche avancée existante conservée.

## Périmètre demandé et réalisation retenue pour l’essai

### Captures restantes demandées — 20 octobre 2026

UX-SITES-006 v0.1 : demande explicite de générer sur le PC les 53 captures
manquantes et de les intégrer à la maquette pour observer le rendu complet.
Complète l’essai de volume UX-SITES-005 sans changer ses cartes, sa recherche,
son ordre ni sa navigation. Cette demande remplace sa limitation initiale à
trois aperçus ; les trois images existantes et la référence validée figée sont
conservées. Capture ponctuelle uniquement, aucune automatisation de production.

Même cadrage réel de l’accueil : viewport bureau 1440×810 (16:9), image WebP
compressée, stockage local et chargement différé dans la liste. Visiter chaque
URL dans un contexte neuf sans compte ni session personnelle ; refuser les
cookies via les commandes visibles lorsque possible, sans masquer ou réinventer
le contenu. Ne pas contourner CAPTCHA, authentification ou erreur de certificat.
Un échec ou une page de blocage doit rester explicite ; ne pas la présenter
comme une capture réussie du site et conserver le remplacement prévu.

Chrome local avec bac à sable activé (démarrage vérifié), au maximum trois
navigateurs de capture simultanés. Proxy temporaire local : destinations publiques
HTTP(S), résolution et connexion à l’IP publique contrôlée pour chaque connexion,
adresses privées/locales/réservées et autres ports refusés. Il s’agit d’un outil
ponctuel de ce test, pas d’une architecture de captures de production validée.
Les scripts temporaires et ce proxy devront être arrêtés à la fin.

Avant livraison : contrôle visuel de chaque image, source/date/URL finale et
éventuel blocage consignés ; aucun aperçu d’erreur intégré ; intégrité de la
référence figée, 56 cartes et correspondance des images aux ids vérifiées ;
rendu mobile/ordinateur et recherche rejoués, images manquantes signalées sans
promettre une réussite pour les sites inaccessibles. Les droits de publication
des captures restent à examiner avant production ; aucun transfert VPS demandé.

### Essai de volume demandé après conservation — 20 octobre 2026

UX-SITES-005 v0.1 : après création et vérification du repère de la version
validée à trois exemples, afficher **tous les sites publiés de la base active
de production** dans la liste courante. Lecture seule du 20 octobre à 21:25
Asia/Dubai : 56 sites, 9 catégories, statut technique valide. Conserver les
cartes compactes, mini-descriptions sur deux lignes, recherche nom/catégorie,
ordre alphabétique et absence de filtres/compteur. L’accueil reste à trois sites.
Cet essai remplace la limitation à trois exemples ci-dessous pour la page
courante uniquement ; la copie figée et les règles de production restent intactes.

La liste est un instantané statique des champs publics id, nom, URL, description
et catégorie ; pas de connexion à la base au chargement ni de synchronisation.
Seuls les espaces périphériques des noms et URL sont retirés. Les descriptions
proviennent de la production ; aucun résumé généré. Conserver les deux entrées
Cinépalmes distinctes, avec leurs URL différentes ; aucun dédoublonnage implicite.
Les liens sont limités aux schémas HTTP/HTTPS et les champs sont échappés dans le
HTML. Aucun contact, secret, brouillon ou site refusé/archivé n’est exporté.

Trois captures existantes restent associées à leur id ; les 53 autres cartes
utilisent le remplacement déjà prévu « Aperçu indisponible ». Pas de capture
supplémentaire ni de service automatique demandé. L’ajout de pagination ou de
filtres n’est pas déduit de cet essai ; leur éventuelle utilité sera examinée
après observation de la longue liste.

Avant livraison : vérifier égalité des 56 ids avec l’export public, trois images,
53 remplacements sans requête d’image cassée, tri et recherche sur le dernier
élément, deux Cinépalmes conservés, effacement/retour, accès au bas de liste,
absence de débordement à 320/390/1280 px. Vérifier aussi que la référence figée
garde trois sites, ses empreintes et ses ressources locales.

### Complément demandé — mini-descriptions, 20 octobre 2026

L’utilisateur demande une mini-description sur la page Sites, avec des points
de suspension si nécessaire. UX-SITES-004 v1.0 : ajouter sous la catégorie un
texte court, limité visuellement à deux lignes, avec « … » au débordement.
Le texte complet reste dans le HTML et est associé au lien par aria-describedby.
Cette demande complète les cartes de liste uniquement ; accueil et recherche
restent inchangés. Ne pas modifier le périmètre de recherche pour cet ajout.

Sources des textes : descriptions de Bus.re et Eau du robinet lues sans écriture
dans la copie locale data/base.db, puis raccourcies ; description d’Infinity Park
tirée du titre de son accueil sur la capture réelle conservée (salle de jeux
multisensorielle à La Réunion). Aucun nouveau contenu promotionnel inventé.
Vérifier deux lignes maximum, ellipsis lorsque nécessaire, nom et accès au site
toujours visibles, sans débordement sur mobile ni modification des captures.

Réalisation locale : descriptions ajoutées dans sites.html et règle dédiée dans
sites.css. Contrôle navigateur séparé à 1280 px : trois textes visibles, accès
aux sites conservés, aucun débordement de page ; style calculé
-webkit-line-clamp:2 et overflow:hidden confirmé, aria-describedby relié au texte
complet. Capture /tmp/rw-sites-mini-descriptions.png. Aucun redimensionnement du
navigateur partagé ni nouveau contrôle sur téléphone physique pour cet ajout.

UX-SITES-001 v0.1 : ajouter Sites au menu public courant, entre Accueil et
Créateurs. Complète UX-GEN-009 sur ce seul menu de maquette : Accueil · Sites ·
Créateurs · Proposer. Sites ouvre sites.html ; l’entrée courante est identifiable.
Le lien Explorer tous les sites de l’accueil ouvre cette nouvelle entrée.
Les versions figées et essais historiques ne sont pas réécrits.

UX-SITES-002 v0.1 : reprendre la simplicité de la liste Créateurs : titre Sites
réunionnais, recherche explicitement lancée, ordre alphabétique, critère textuel
visible et retirable, pas de panneau Affiner, de filtres ou de compteur.
Trois exemples seulement pour cet essai, issus des sites publiés déjà lus en
base de production : Bus.re, Eau du robinet, Infinity Park. Aucune nouvelle
lecture ou synchronisation de la base n’est nécessaire pour les réutiliser.

UX-SITES-003 v0.1 : réutiliser les cartes compactes de liste, avec un petit
aperçu **16:9** à la place du portrait, nom, catégorie et accès au site réel.
Pas de texte descriptif inventé. Toute la carte ouvre le site externe dans un
nouvel onglet annoncé ; aucune nouvelle fiche de site. Deux colonnes sur grand
écran, une sur mobile comme la liste Créateurs. Les captures 16:9 de l’accueil
restent intactes. Ce format réutilisé fait partie de la réalisation à relire,
sans valider de nouvelle règle générale pour les résultats de recherche.

Recherche locale sur nom et catégorie, insensible aux accents et à la casse ;
q conservé dans l’URL, retour navigateur et rechargement restaurent le critère.
Un ancien paramètre de filtre ne restreint jamais cette liste en silence.
États de démonstration vide/chargement/erreur et recherche sans résultat,
effacement, réessai et accès Proposer un site suivent les composants Créateurs.
Une capture absente garde une vignette de remplacement et un lien utilisable.

## Parcours et limites

Visiteur : menu Sites ou Explorer tous les sites → liste simple → recherche →
site externe dans un nouvel onglet ; la liste garde sa recherche. Le retour
Accueil/Créateurs reste disponible. Contact/FAQ/Mentions légales conservent un
retour vers Sites avec ses critères. Contributeur : Proposer un site ouvre le
formulaire commun avec le type Site présélectionné. Administrateur : aucune
nouvelle action ; données et modération restent inchangées.

La maquette réutilise trois sites fixes, pas l’annuaire complet actif. La
recherche avancée recherche-sites.html et les pages catégorie gardent leurs
exigences et simulations ; ce nouvel écran ne supprime aucun filtre métier.
Import complet, pagination, choix des cartes de production et automatisation
des captures restent hors périmètre. Aucune publication, migration ou BDD modifiée.
Les droits de publication des captures restent à vérifier avant production.

## Acceptation avant livraison

- Sites accessible depuis les menus publics et le bloc de l’accueil ; état actif
  correct sur la liste, sans modifier les archives.
- Trois exemples triés Bus.re, Eau du robinet, Infinity Park ; recherche, aucun
  résultat, effacement, rechargement et retour navigateur utilisables.
- Aucun Affiner, filtre ou compteur ; pas de restriction héritée d’URL.
- Cartes compactes, captures 16:9 et commandes accessibles au clavier.
- Rendu 320/390 et ordinateur sans débordement, en particulier le menu à quatre liens.
- Proposer un site et retour depuis les pages d’aide conservent le parcours.
- Sources statiques locales, aucune requête automatique aux sites externes.

Les contrôles effectifs seront distingués des critères et de la relecture
utilisateur. Aucun comportement backend déduit de ces simulations.

Pour UX-SITES-005, les 56 identifiants et les cinq champs publics du HTML ont
été comparés à l’export de production : égalité complète, tri français et deux
Cinépalmes conservés. Rendu observé sans débordement à 320/390/1280 px ; accès
au dernier site et recherche/effacement vérifiés. La référence à trois sites
garde ses 59 empreintes et a été ouverte indépendamment dans le navigateur.
Le tag local maquette-sites-v1-validee-20261020 désigne le commit 8e7265f,
antérieur à l’ajout des 56 sites. Les contrôles de volume et leurs limites sont
consignés dans SITE_LIST_MOCKUP_CHECKS.md ; relecture utilisateur de la longue
liste attendue, sans remise en cause de la validation visuelle de référence.

## Réalisation et vérification de la liste simple

sites.html/css/js livrés localement ; menus des onze pages publiques courantes
complétés, Explorer tous les sites relié à la liste, retour depuis l’aide étendu
à Sites. Menu compact à quatre entrées sur les petits écrans, zones de 44 px.
Les archives figées et variantes historiques ne sont pas modifiées.
Résultats et limites : [SITE_LIST_MOCKUP_CHECKS.md](../testing/SITE_LIST_MOCKUP_CHECKS.md).

## Résultat de l’essai de captures UX-SITES-006

Les 53 sites restants ont été visités sur le PC : 42 nouveaux aperçus acceptés
après inspection visuelle, 11 indisponibles (protection, erreur distante ou
ressources incomplètes). La liste garde 56 cartes et affiche 45 images locales
au total, toutes WebP 1440×810 avec chargement différé. Petites bannières non
bloquantes parfois visibles ; aucune page de CAPTCHA ou erreur retenue.
Provenance et limites par site dans maquettes/assets/site-previews/sources.json.

Données publiques comparées dans le navigateur à l’export : égalité complète
des 56 identifiants, noms, catégories, descriptions et URL ; recherche Zinfos974
avec image décodée puis retour aux 56 cartes vérifiés. Une colonne à 320/390 px,
deux à 1280 px, sans débordement horizontal observé. Les trois anciennes images
et les 59 empreintes de la référence figée restent identiques. Les scripts et
le proxy temporaires sont arrêtés après capture. Contrôles détaillés dans
[SITE_LIST_MOCKUP_CHECKS.md](../testing/SITE_LIST_MOCKUP_CHECKS.md).

Réalisation locale de l’essai uniquement ; relecture utilisateur du rendu avec
ces images attendue. Aucun automatisme récurrent, transfert VPS, écriture en
base ou intégration Flask.
