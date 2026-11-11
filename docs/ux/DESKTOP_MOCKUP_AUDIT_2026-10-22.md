# Audit de la maquette ordinateur — 22 octobre 2026

| Métadonnée | Valeur |
| --- | --- |
| Statut | Audit réalisé ; recommandations à discuter, aucune refonte autorisée par cet audit |
| Référence | accueil-navigation-flottante.html, navbar mobile retenue UX-HOME-025 |
| Source inspectée | main ebc3f7a ; maquette locale sur le réseau du PC |
| Suivi | Dashboard Réunion Wiki, ticket #45 ; liens avec #14 et pistes #44 |
| Périmètre | Accueil, Sites, Personnalités, fiche Adriana, proposition, recherche et navigation publique PC |

## Conclusion

La structure reste utilisable et les sites occupent bien la première place.
Le manque d’unité entre l’accueil plus visuel et les pages partagées héritées
est le principal sujet de design. Les portraits agrandis révèlent leur faible
définition. Sur grand écran, la composition reste la même colonne de 1120 px,
et la longue liste perd ses accès de navigation au défilement.
Deux limites de contenu/parcours compliquent aussi une vidéo de démonstration :
la recherche globale fictive ne retrouve pas les vrais sites et deux profils
quittent la maquette locale. Ces limites ne sont pas propres au PC.

Ce document constitue un constat et des propositions. Il ne valide pas une
nouvelle grille, un header fixe, une pagination, une bannière plus grande,
une nouvelle photo ou une évolution du MVP. Aucun HTML/CSS/JS, base ou VPS
modifié pendant l’audit. La navbar mobile retenue reste intacte.

## Méthode et observations

Revue dans le navigateur intégré en dimensions CSS effectives constatées
1366×768, 1440×900 et 1920×1080 pour l’accueil. Pages internes inspectées au
format de référence PC et, ponctuellement, fenêtre plus large. Le zoom du
navigateur a exigé de relever innerWidth/innerHeight après stabilisation : les
chiffres ci-dessous proviennent des mesures, pas seulement du réglage demandé.
Relecture indépendante des sources sans modification ni seconde navigation.

Pas de débordement horizontal observé sur les trois formats d’accueil. À 1440 px,
header d’environ 94 px, conteneur 1120 px, recherche 760 px, cartes sites environ
336 px ; le titre Personnalités commence vers y=675 px. À 1920 px, largeur de
contenu toujours 1120 px et marges d’environ 400 px. Ce plafonnement n’est pas
une erreur technique : son intérêt visuel doit être comparé à une composition PC.

## Constats priorisés

### PC-01 — Rupture entre accueil et annuaires — priorité visuelle haute

**Observé :** grandes captures 16:9 et portraits carrés d’environ 299 px sur
l’accueil ; Sites en deux colonnes avec aperçus 144×81 px ; Personnalités en deux
colonnes avec portraits 120×120 px ; fiche Adriana avec portrait 150×150 px.
Avec trois profils seulement, la liste Personnalités occupe deux cartes sur une
rangée puis une seule à gauche. L’effet de découverte change fortement après le clic.

**Interprétation :** le cadre graphique n’a pas encore été harmonisé avec la
dernière direction de l’accueil. Les cartes compactes de liste ont été validées
historiquement (UX-CREA-007) : ce n’est pas un bug à remplacer d’office.

**Piste à tester :** choisir une famille cohérente de cartes PC avec même vocabulaire
d’image, titre et action, en comparant grille visuelle et liste compacte. Tenir
compte de la densité de 56 sites et des sources d’image avant toute généralisation.
Sources : home-large-sites.css, home-large-profiles.css, sites.css, creator-card.css,
talent-profile.css, CREATOR_LIST.md et SITE_LIST.md.

### PC-02 — Qualité des portraits insuffisante pour le grand format — haute

**Observé :** les trois fichiers naturels font 150×150 px, affichés à environ
299×299 px sur l’accueil. Le manque de détail est visible dans la revue des cartes.
Les listes et la fiche les affichent plus petits et accentuent moins le défaut.

**Piste :** fixer les dimensions à partir des sources réellement disponibles,
puis rechercher séparément des originaux autorisés de meilleure définition si
le grand portrait est conservé. Une sophistication CSS ne crée pas de détails
supplémentaires. Aucun remplacement ou agrandissement de fichier demandé ici.

### PC-03 — Composition du haut de l’accueil à préciser pour PC — moyenne

**Observé :** bandeau photo très bas (~94 px) et recherche de 760 px alignée à
gauche d’une zone utile d’environ 1048 px. À 1920 px, la présentation et les cartes
restent à la même largeur ; le grand écran apporte surtout des marges.

**Jugement de design :** l’ensemble est propre mais peu composé comme une page
PC destinée à présenter le projet. L’espace vide n’est pas un défaut en soi.

**Piste :** tester un alignement assumé entre recherche, titres et grille, puis
une échelle desktop du header cohérente sur les pages. Les anciens grands titres
et slogans ont été retirés explicitement : ne pas les réintroduire sans nouvelle
validation. Ne pas imposer une hero géante pour remplir l’écran.

### PC-04 — Longue liste et navigation perdue au défilement — moyenne

**Observé :** 56 sites, deux colonnes, 28 rangées et page d’environ 5050 px à
1440 px. Après défilement, menu et recherche sortent de l’écran ; header position
static, dock PC display:none. Les liens d’aide et proposition de fin de liste
restent loin. La recherche propre à Sites est disponible en haut.

**Pistes à arbitrer :** accès PC au menu/recherche pendant la consultation, et
choix entre liste complète ou progression/pagination. La pagination est déjà une
question ouverte de SITE_LIST.md ; ne pas ajouter filtre, compteur ou pagination
comme une décision acquise. La navbar mobile ne doit pas être copiée automatiquement
sur PC : le menu supérieur a été conservé explicitement dans UX-HOME-024.

### PC-05 — En-têtes et accents visuels hétérogènes — moyenne

**Observé :** photo derrière le header uniquement sur l’accueil ; autres pages
sur fond uni. Recherche affiche un bloc de proposition citron rgb(229,244,154),
contre le bloc vert de l’accueil. Header proposition mesuré à 88 px, logo 27 px
et menu 12 px, contre ~94 px, 28 px et 13 px sur les listes/recherche.

**Piste :** harmoniser le cadre commun (header, liens, actions, espacements),
puis arbitrer les accents de couleur. Le citron de recherche était explicitement
conservé dans une décision antérieure ; son retrait n’est pas encore validé pour
cette page. Garder des largeurs de lecture adaptées : le formulaire de 600 px
et la fiche plus étroite n’ont pas à être aussi larges que la grille.

### PC-06 — Recherche globale déconnectée des sites réels — haute pour une démo

**Reproduit :** accueil → recherche « Bus.re » → 0 résultat, alors que Bus.re est
mis en avant sur l’accueil et présent dans Sites. La recherche globale utilise
les dix sites fictifs de search-data.js, l’annuaire ses 56 sites réels.

**Piste :** préparer un jeu de données cohérent pour le parcours de démonstration
et préciser l’intégration réelle lors du chantier prévu. Limite de simulation
partagée mobile/PC, pas preuve d’un bug de production ; aucun branchement base
ou changement métier effectué pendant cet audit.

### PC-07 — Parcours de démonstration et petits textes à finir — moyenne

**Source vérifiée :** Benji/Harendra mènent à dev.reunionwiki.re dans le même
onglet ; leurs fiches locales n’existent pas. Le retour navigateur est possible,
le retour interne à la version locale n’est pas maîtrisé. Limite déjà documentée.
Les blocs d’états de démo et de versions sont visibles en fin de maquette : en
préparer le cadrage pour la vidéo, sans les confondre avec l’interface publique.

**Reproduit :** l’état vide de recherche mélange « Essaie » et « proposez » ;
la branche de recherche vide contient aussi « Saisissez ... lancez ». Écart à
la règle de tutoiement du 8 octobre, partagé mobile/PC. À relire lors des finitions.
Aucun texte modifié dans cet audit.

## Contraintes réelles pour la prochaine proposition

Les 56 sites comprennent 45 captures et 11 remplacements ; une future présentation
plus visuelle devra aussi être examinée avec ces absences, sans inventer des
captures. Les deux Cinépalmes ont des URL distinctes mais des textes très proches :
l’information permettant de les différencier mérite une vérification de contenu,
sans fusion ou déduplication silencieuse.

Les documents existants décrivent des adaptations PC par page, mais ne tranchent
pas encore une composition desktop d’ensemble pour la dernière direction. Lors
de la reprise, préparer des alternatives concrètes et les faire valider avant
modification. Pas de favoris, nouveau stockage, collecte ou automatisation ajoutés.

## Ordre de reprise proposé, non encore validé

1. Stabiliser le parcours de présentation (recherche et destinations locales/externes).
2. Choisir une composition PC cohérente accueil → listes et des dimensions d’image réalistes.
3. Décliner le header, les actions et les espacements ; décider de l’accès pendant le défilement.
4. Arbitrer la longue liste, puis finaliser les textes et le cadrage vidéo.

La priorité proposée sert à discuter, pas à lancer ces travaux. Garder les sites
en premier, la palette claire/verte, les versions comparables et la navbar mobile.

## Preuves et limites

Captures locales temporaires (non versionnées pour ne pas recopier les portraits) :
- /tmp/rw-pc-audit-laptop.png : accueil, 1366×768 relevés.
- /tmp/rw-pc-audit-home-1440-final.png : accueil, 1440×900 relevés.
- /tmp/rw-pc-audit-wide.png : accueil, 1920×1080 relevés.
- /tmp/rw-pc-audit-profiles-1440.png : grandes cartes de profils.
- /tmp/rw-pc-audit-sites.png et /tmp/rw-pc-audit-sites-scrolled.png : grille et défilement.
- /tmp/rw-pc-audit-personnalites-1440.png et /tmp/rw-pc-audit-fiche-1440.png : continuité de profils.
- /tmp/rw-pc-audit-proposer-1440.png et /tmp/rw-pc-audit-search-bus.png : autres pages et recherche.

Pas d’étude utilisateur, d’audit WCAG complet, de mesure de performance ou de
validation du contenu/droit des images. Aucun clic sur les fiches externes ni
contrôle de production. Pas de déduction sur l’expérience réelle de tous les
visiteurs à partir de ces seuls constats. Seul le rapport et le suivi sont mis
à jour ; aucune correction de maquette effectuée.
