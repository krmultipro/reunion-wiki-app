# Décisions UX — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.46 |
| Statut | Décisions validées |
| Dernière mise à jour | 23 octobre 2026 |

## Dashboard contributeur mobile — 23 octobre 2026

L’utilisateur délègue les choix de conception après demande de documentation
complète et de maquette mobile. [CONTRIBUTOR_DASHBOARD_MOBILE.md](CONTRIBUTOR_DASHBOARD_MOBILE.md)
consigne UX-CDM-001 à 010 et les parcours : accès au compte, brouillons,
propositions, compléments, annulation, refus, corrections et suivi privé.
Variante autonome dans `maquettes/contributeur-mobile/`, sans variante PC ni
modification de la navigation publique retenue. Lancement sans compte inchangé ;
backend, emails et publication non réalisés. Validation visuelle utilisateur attendue.
[Contrôles et limites](../testing/CONTRIBUTOR_MOBILE_REVIEW_2026-10-23.md).

## Onglet Sites — maquette simple, 20 octobre 2026

Demande utilisateur : ajouter un onglet Sites aussi simple que la page Créateurs.
UX-GEN-009 v3.0, maquette courante uniquement : menu Accueil · Sites · Créateurs ·
Proposer. Sites ouvre la liste simple dédiée sites.html ; pas de filtres ni
compteur dans cette liste. La recherche avancée et les catégories restent
distinctes et inchangées. Remplace sur le menu courant la version v2.0 ci-dessous,
conservée pour historique ; retrait des tendances toujours applicable.
Voir [SITE_LIST.md](SITE_LIST.md) pour sources, parcours, périmètre d’essai et
critères. Aucune intégration Flask ni publication demandée.

## Révision applicable — accueil, 17 octobre 2026 après essai utilisateur

Les choix 1B/2A/3A/4A/5A et le retrait des tendances publiques remplacent
l’interdiction du carrousel et l’affichage des deux blocs Plus consultés/
Derniers sites ajoutés sur l’accueil. Carrousel manuel réservé à l’accueil
mobile ; cartes communes et grille ordinateur conservées. Références :
[HOME_PAGE.md](HOME_PAGE.md), UX-HOME-001 v2.0, 007 v2.0 et 008 v1.0.

UX-GEN-009 v2.0 : menu Accueil · Créateurs · Proposer conservé ; retirer les
accès publics aux tendances de la cible. La règle v1.0 plus bas est remplacée
sur ce point et reste historique. Aucun lien de remplacement dans le pied de
page demandé. Route Flask actuelle inchangée par la maquette ; retrait public,
liens et SEO à traiter avec #18, données/clics et admin préservés.

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
d’entreprises hors de cette rubrique au lancement. Le menu cible devient Accueil · Talents péi · Proposer (complément de UX-GEN-009).

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Objet

Ce dossier décrit comment les règles produit sont présentées et manipulées
par les utilisateurs. Les règles métier restent dans `docs/business-rules/` ;
les comportements vérifiables restent suivis dans `docs/testing/`.

Une décision UX ne doit pas être considérée comme implémentée uniquement
parce qu'elle figure dans ce document. Son état doit être confirmé par le code
et par un test adapté, notamment un test d'interface lorsqu'une interaction est
concernée.

## Méthode de conception visuelle

Une évolution d'interface ne doit pas déclencher un nouveau questionnaire
visuel complet lorsque le site possède déjà les composants et les conventions
nécessaires. La méthode par défaut est la suivante :

1. Réutiliser le langage visuel existant : couleurs, typographie, espacements,
   composants, états de focus et règles responsive.
2. Préparer un rendu cohérent par défaut à partir du HTML et du CSS déjà
   présents.
3. Demander une décision produit uniquement pour les choix visuels réellement
   ambigus ou susceptibles de modifier sensiblement le parcours.
4. Vérifier le résultat visuellement sur ordinateur et sur mobile, et pas
   seulement au moyen du HTML rendu ou de l'arbre d'accessibilité.

La validation finale doit aussi confirmer que les feuilles de style sont bien
chargées, que les styles calculés attendus sont appliqués et que les contenus
réservés aux technologies d'assistance ne sont pas visibles à l'écran. Les
tests automatisés de structure complètent cette vérification, mais ne la
remplacent pas.

### Retour d'expérience — rendu visible et représentation accessible

L'arbre d'accessibilité ou une copie textuelle peut inclure des libellés masqués
visuellement, par exemple « Retirer la catégorie ». Leur présence dans cette
représentation ne prouve donc pas qu'ils sont visibles à l'écran. Inversement,
une feuille CSS chargée avec succès ne garantit pas que le rendu est abouti :
des actions peuvent encore conserver l'apparence de liens bruts si leurs
couleurs, leur typographie, leurs états et leur hiérarchie visuelle ne sont pas
explicitement contrôlés.

Avant de valider une évolution visuelle, il faut distinguer ces trois contrôles :

1. vérifier la structure et les libellés dans l'arbre d'accessibilité ;
2. vérifier le chargement des ressources et les styles effectivement appliqués ;
3. observer le rendu réel sur ordinateur et sur mobile, notamment la hiérarchie
   des actions et la cohérence avec les composants existants.

## Décisions transversales validées

### UX-GEN-001 — Actions automatiques et validations explicites

- Les filtres et les tris s'appliquent automatiquement lorsqu'une valeur
  change.
- La recherche textuelle conserve une validation explicite afin d'éviter une
  requête à chaque caractère.
- Les actions sensibles ou destructives conservent une confirmation explicite.

### UX-GEN-002 — État partageable dans l'URL

Le texte recherché, les filtres, le tri et la page courante sont conservés dans
l'URL. Une recherche peut ainsi être partagée, enregistrée et restaurée par la
navigation du navigateur.

### UX-GEN-003 — Comportement mobile des filtres

Sur mobile, les filtres sont regroupés derrière une action « Affiner ». Cette
action indique le nombre de filtres actifs. Les critères actifs restent visibles
et peuvent être retirés sans ouvrir de nouveau le panneau.

### UX-GEN-004 — Validation des formulaires

- Une validation légère peut aider pendant la saisie.
- La validation complète est toujours exécutée côté serveur.
- Les erreurs apparaissent près des champs concernés.
- Les valeurs saisies sont conservées après une erreur.

### UX-GEN-005 — Protection des formulaires commencés

Lorsqu'un formulaire contient des modifications non enregistrées, quitter la
page déclenche un avertissement. Aucune sauvegarde automatique n'est imposée par
la décision actuelle.

### UX-GEN-006 — Actions externes

Les liens vers les sites référencés s'ouvrent dans un nouvel onglet. L'interface
signale visuellement la sortie de Réunion Wiki et les liens utilisent
`noopener noreferrer`.

### UX-GEN-007 — États d'interface

Les interfaces distinguent explicitement :

- le chargement ;
- une liste réellement vide ;
- une recherche sans résultat ;
- une erreur technique avec une action pour réessayer lorsque cela est utile.

### UX-GEN-008 — Accessibilité

Les parcours importants visent le niveau WCAG AA : navigation au clavier,
focus visible, labels explicites, contrastes suffisants, erreurs associées aux
champs et aucune information transmise uniquement par la couleur.

### UX-GEN-009 v1.0 — Historique remplacé sur l’accès public aux tendances

- **Version :** 1.0.
- **Statut :** Remplacée sur les tendances publiques par v2.0 du 17 octobre 2026 ; menu conservé. Décision initiale validée le 6 octobre 2026.
- **Navigation principale :** `Accueil · Créateurs · Proposer`, en priorité
  pour les usages mobile et PWA. « Tendances » n'est plus un onglet du menu.
- **Accès aux tendances :** lien « Tendances des sites → » dans la partie sites
  de l'accueil, près de « Les plus consultés ».
- **Périmètre :** les tendances concernent les sites. Aucun classement de
  créateurs n'est ajouté par cette décision.
- **Conservation :** la page `/tendances` et les règles de calcul
  `RM-SITE-008`, `RM-18` et `RM-19` restent applicables. Le déplacement du lien
  ne supprime pas la fonctionnalité et ne modifie pas ses indicateurs.
- **Critères d'acceptation :** le menu utilise les trois entrées retenues ;
  l'accueil fournit un accès identifiable aux tendances des sites ; la page
  reste accessible depuis cet accès et par son URL existante.
- **État réel :** placement réalisé dans les maquettes locales
  `maquettes/accueil.html`, `maquettes/createurs.html` et
  `maquettes/talent-adriana.html`. Rendu de l'accès dans la partie sites observé
  sur mobile et placement validé par l'utilisateur. L'intégration dans les
  templates Flask et la vérification du parcours réel restent à faire ; aucune
  mise en développement ou production n'est déclarée.

## Proposition publique d'un site

### UX-SUBMIT-001 — Doublons

Lorsqu'un doublon exact existe, l'interface explique le blocage, présente le
site existant et permet de le consulter. Un doublon seulement probable produit
un avertissement adapté sans être silencieux.

### UX-SUBMIT-002 — Confirmation de réception

Une proposition valide mène à une page de confirmation dédiée. Cette page
indique que la proposition attend une modération et propose au minimum un retour
à l'accueil et une nouvelle proposition.

## Administration

### UX-ADMIN-001 — Contrôles avant publication

Avant une publication, un écran récapitule les contrôles réussis, les contrôles
manquants et les validations humaines encore nécessaires. La publication reste
une confirmation explicite.

### UX-ADMIN-002 — Confirmations proportionnelles

- Une modification ordinaire ne demande pas de confirmation supplémentaire.
- Un archivage utilise une confirmation légère.
- Un refus demande un motif.
- Une suppression définitive utilise une confirmation forte qui nomme
  explicitement l'élément concerné.

### UX-ADMIN-003 — Destination après une action

- Un enregistrement ordinaire conserve l'utilisateur sur la fiche et confirme
  la réussite.
- Une action de modération lancée depuis une file revient à cette file.
- La page, les filtres et le tri précédents sont conservés.

### UX-ADMIN-004 — Représentation des statuts

Chaque statut possède un libellé textuel, une couleur et, lorsque cela aide, une
icône. La couleur n'est jamais le seul moyen de distinguer Brouillon, En attente,
Publié, Refusé et Archivé.

## Documents par parcours

- [`HOME_PAGE.md`](HOME_PAGE.md) cadre l’accueil complet : blocs, sélection,
  ordre/sélections/raccourcis/aperçus et états vides validés ; maquette locale
  adaptée avec preuves et limites.

- [`CREATOR_PROFILE.md`](CREATOR_PROFILE.md) cadre la fiche individuelle :
  exigences existantes, cinq choix validés dont source privée au lancement, et
  écarts de la maquette.

- [`HOME_SEARCH.md`](HOME_SEARCH.md) cadre la recherche depuis l’accueil ;
  recherche commune sites/catégories/créateurs et trois sections validées ;
  accès directs sans liens Affiner par section ; maquette locale réalisée.

- [`CREATOR_LIST.md`](CREATOR_LIST.md) cadre la liste des créateurs et distingue
  les exigences validées et les quatre choix de présentation/retour désormais
  validés après retour utilisateur.
- [`CATEGORY_PAGE.md`](CATEGORY_PAGE.md) conserve les sept choix validés pour
  les catégories de sites, la maquette locale et ses contrôles ; validation
  visuelle utilisateur encore attendue.
- [`PUBLIC_SEARCH.md`](PUBLIC_SEARCH.md) détaille la recherche publique, ses
  filtres, ses tris et ses états.

[`UNIFIED_SUBMISSION.md`](UNIFIED_SUBMISSION.md) détaille la proposition commune.
Les parcours de modération et des contenus restent à détailler selon les
documents et questions propres à chacun.

## Travail à reprendre plus tard — cohérence visuelle

Demande enregistrée le 5 octobre 2026. **À faire ultérieurement ; aucun audit
ni changement global n'est lancé ou autorisé par cette note.**

- Commencer par trois pages représentatives du site : accueil, liste des
  créateurs et fiche talent. Priorité aux usages mobile et PWA.
- Auditer la cohérence des couleurs, polices, espacements, icônes, boutons,
  cartes et formulaires, en s'appuyant sur l'existant.
- Proposer un petit kit réutilisable en HTML/Jinja et CSS : variables visuelles,
  boutons, cartes, champs, badges et états d'interface ; conserver les icônes
  Lucide locales et limiter les dépendances.
- Documenter les conventions retenues dans le cahier des charges et séparer
  propositions, choix validés et réalisations. L'intégration sur toutes les
  pages constitue une étape distincte.
- Limiter les lectures redondantes et fournir un compte rendu court pour
  économiser les tokens. Estimations indicatives discutées : 5 000 à 12 000
  tokens pour un audit ciblé ; 12 000 à 25 000 pour l'audit et une proposition
  de kit documentée. Ce ne sont ni des plafonds approuvés ni des garanties ;
  l'implémentation éventuelle vient en supplément.

### Pourquoi vérifier ces éléments sur mobile/PWA

Objectif : rendre le site agréable, lisible et facile à utiliser sur téléphone,
y compris lorsqu'il est installé comme une application (PWA).

| Élément | Objectif de l'audit futur |
| --- | --- |
| Couleurs | Conserver les mêmes repères d'une page à l'autre et un texte bien lisible. |
| Polices | Harmoniser les titres et textes avec des tailles adaptées au téléphone. |
| Espacements | Aérer les écrans et éviter les appuis accidentels sur des actions proches. |
| Icônes | Garder un style cohérent et des symboles compréhensibles. |
| Boutons | Rendre les actions reconnaissables et faciles à toucher. |
| Cartes | Présenter les créateurs et les sites selon des conventions réutilisables. |
| Formulaires | Simplifier la saisie, avec des champs, libellés et erreurs clairs. |

Le kit visuel servira à réutiliser ces éléments sans redéfinir le design à
chaque page. Cette explication complète le travail différé ; elle ne lance
aucune réalisation maintenant.

## À reprendre plus tard — formaliser la charte graphique

Suivi du travail : **ticket Dashboard #17 — « Formaliser la charte graphique à
partir de la maquette C »**, rattaché à Réunion Wiki, créé et relu sur le VPS le
6 octobre 2026. Le Dashboard fait référence pour son statut ; cette section
conserve le contexte de conception, sans constituer une seconde liste de tickets.

Rappel demandé par l'utilisateur le 6 octobre 2026 : **documenter la charte
graphique ultérieurement**, sans lancer sa rédaction complète maintenant.

- Base visuelle retenue : version **C** de `maquettes/comparaison.html?variante=c`,
  styles dans ce fichier et comportements dans `maquettes/comparaison.js`.
- Direction adoptée : fond crème, vert profond, accent citron ; cartes de
  créateurs compactes sur l'accueil mobile, portraits plus grands sur les listes
  et fiches. Finitions locales : textes secondaires agrandis, vert des petits
  liens assombri, accès tactiles élargis et catégories repliables sur mobile.
- À formaliser : couleurs exactes par rôle, contrastes, polices, tailles et
  graisses, espacements, arrondis, bordures, icônes Lucide locales, composants
  réutilisables, états de focus/erreur et règles responsive mobile/PWA.
- Relire les valeurs réellement utilisées dans C avant de les documenter ;
  ne pas reprendre automatiquement celles du CSS historique ou des variantes A/B.
- Distinguer la direction adoptée des valeurs détaillées restant à valider.
  Prévoir une version et un historique pour permettre les corrections futures.
- Limite visuelle à garder en tête : portraits locaux de faible résolution,
  à remplacer par de meilleures sources lorsque disponibles.
- État : maquette locale uniquement ; charte détaillée non rédigée, composants
  non généralisés à l'application, aucun déploiement effectué.

## Finitions C appliquées à l’accueil — 7 octobre 2026

Sur demande de l’utilisateur, `maquettes/accueil.html` reprend maintenant les
finitions de C présentes dans `comparaison.html`. Styles dans `accueil-c.css`,
comportement des catégories dans `accueil.js` ; la comparaison A/B/C est conservée.

- Mobile : portraits de 96 px, cartes créateurs horizontales et catégories
  initialement repliées, avec leur nombre de sites illustratifs.
- Ordinateur : grands portraits et catégories ouvertes ; retour au layout
  mobile pris en charge lors du changement de largeur.
- Textes secondaires 12–13 px, petits liens verts `#087548`, liens principaux
  et navigation de 44 px minimum, proposition de 48 px minimum, SVG locaux.
- Navigation Accueil/Créateurs/Proposer et accès Tendances conservés ; liens
  Explorer ouvrent les maquettes catégorie existantes.

Vérifications locales : rendu observé à 390 × 844 et 1440 × 900, absence de
débordement horizontal contrôlée à 320 px ; catégorie Emploi ouverte avec
Entrée puis lien Explorer suivi jusqu’à la catégorie. Styles calculés confirmés
(portrait mobile 96 px, lien Explorer 13 px/44 px, vert `rgb(8,117,72)`).
`node --check maquettes/accueil.js` et `git diff --check` réussis.

Maquette seulement : recherche, accès rapides et noms de sites restent des
illustrations statiques comme auparavant ; aucun parcours backend ajouté ni
mise en production. Portraits de faible résolution toujours présents. Charte
complète toujours reportée au ticket #17, validation visuelle finale attendue.
Finalisation Git différée jusqu’à cette validation, sans inclure les travaux
étrangers présents dans le dépôt.

## Finitions C appliquées à la liste créateurs — 7 octobre 2026

Sur demande utilisateur, `maquettes/createurs.html` charge `createurs-c.css` :
en-tête/navigation alignés avec l'accueil C, vert des petits liens `#087548`,
texte secondaire `#65705F`, descriptions/profil à 13 px, badges/footer à 12 px,
contours fins, surfaces blanches, arrondis cohérents et focus visible. La
navigation Créateurs est un lien marqué `aria-current="page"`. Les grands
portraits de la liste sont conservés selon la direction validée ; ils ne sont
pas remplacés par les cartes compactes de l'accueil mobile.

Rendu observé à 390 × 844 et 1440 × 900 ; aucun débordement horizontal à 320 px.
Styles calculés vérifiés : navigation 44 px, descriptions/profil 13 px, badges
12 px, portrait desktop 240 px. Lien Adriana suivi vers sa maquette, lien
Proposer suivi et choix Créateur présélectionné confirmé. `git diff --check`
réussi. Capture temporaire : `/tmp/reunion-wiki-createurs-c.png`.

Maquette locale uniquement : recherche et filtres restent illustratifs, autres
profils restent liés au site dev comme auparavant. Aucune modification de la
fiche talent, du backend ou de la production. Portraits de faible résolution
conservés ; validation visuelle finale utilisateur encore attendue.

## Recherche de l’accueil — périmètre précisé le 7 octobre 2026

L'utilisateur demande de reprendre ce sujet après la liste des créateurs : la
recherche de l'accueil concerne les sites et catégories pour le moment. Ne pas
supposer une recherche commune avec les créateurs.

Le complément `1A/2A` valide des sections distinctes pour les sites et catégories,
et le clic vers la page catégorie complète. Ces décisions sont consignées dans
`HOME_SEARCH.md` ; leur réalisation reste distincte. La maquette actuelle mentionne aussi « une
ville » dans son champ illustratif : libellé à réexaminer pendant cette reprise,
sans réécrire les règles de recherche et filtres des sites déjà validées.
Aucune évolution de recherche ni backend réalisée ou lancée par cette précision.

## Carte créateur commune accueil/liste — 7 octobre 2026

Réponse **1A** : l'accueil doit reprendre la même carte que la liste créateurs,
sur mobile et ordinateur. Décision `UX-CREA-005` dans `CREATOR_LIST.md`.
Le rendu historique de l'accueil C (catégorie sous le portrait mobile, portrait
150 px sur ordinateur) est remplacé par le composant commun : catégorie dans
le corps mobile et portrait 240 px sur ordinateur, petit portrait 96 px sur
mobile, présentation et Voir le profil sur les deux pages.

Réalisation locale : `creator-card.css` partagé ; rendu et styles comparés sur
les deux pages à 390/1440 px, absence de débordement à 320 px, liens vérifiés.
La largeur effective dépend du conteneur ; ni sélection de l'accueil ni fiche
individuelle ni recherche accueil modifiées. Backend inchangé et validation
visuelle des cartes communes confirmée par le retour utilisateur du 7 octobre
2026 ; les autres parcours et limites ne sont pas déclarés validés.

### Révision du périmètre de recherche — 7 octobre 2026

Après réflexion sur les talents présents sur l'accueil, l'utilisateur valide
une recherche commune sites/catégories de sites/créateurs, avec trois sections
et nombres de résultats. Cette décision remplace le périmètre limité aux sites
précédemment consigné, sans effacer son historique. Le clic sur une catégorie
ouvre toujours sa liste complète. Voir `HOME_SEARCH.md`, règle
`UX-HOME-SEARCH-001` version 2.0. Complément `3A` validé : Affiner les sites
et Affiner les créateurs ouvrent les recherches dédiées avec texte conservé,
sans panneaux de filtres sur la page commune.
Aucune réalisation backend ni changement de maquette déclaré par cette révision.

### Simplification de la recherche commune — 7 octobre 2026

Nouveau choix 1A : suppression des liens Affiner par section. Les trois sections
restent directement consultables (fiche créateur, catégorie complète, site
externe). Ce complément remplace le 3A ci-dessus ; les recherches dédiées
restent disponibles et leurs filtres conservés. Traçabilité dans
`HOME_SEARCH.md`, UX-HOME-SEARCH-003 version 2.0. Maquette locale uniquement.

### Allègement des résultats avec bloc citron conservé — 7 octobre 2026

Choix 1A avec exception explicite validée : titre Résultats sans introduction,
sections vides masquées, catégories/sites en lignes compactes ; bloc citron
conservé. Les cartes créateurs communes ne changent pas. Référence
`HOME_SEARCH.md`, UX-HOME-SEARCH-001 v3.0 et UX-HOME-SEARCH-004. Maquette locale
réalisée et observée sur ordinateur/mobile, largeur 320 px sans débordement.

### Lisibilité de la recherche allégée — 7 octobre 2026

Choix 1A : noms vert profond, descriptions plus sombres à 14 px, domaines et
communes secondaires à 13 px, actions vertes et fond crème conservé. Décision
UX-HOME-SEARCH-005 dans HOME_SEARCH.md consignée avant CSS ; maquette locale
réalisée et contrôlée, sans généralisation de charte aux autres pages.

### Fiche créateur adaptée et portrait réduit — 7 octobre 2026

Adaptation demandée après les cinq choix : présentation avant réseaux,
correction discrète, catégorie cohérente, suggestions seulement de même catégorie,
aucune rubrique Sources publique au lancement. Complément explicite : portrait
moins gros car sources peu définies. UX-FICHE-006 remplace le grand portrait
prévu sur fiche : maquette limitée à 150 px ordinateur, 140 px mobile/120 px
petit écran pour le fichier local 150 × 150. Image générique si absente.

Solution documentée dans CREATOR_PROFILE.md avant CSS ; elle limite le flou,
sans créer de détails ni remplacer une source mieux définie et autorisée.
Carte commune accueil/liste inchangée. Rendu et états contrôlés localement,
backend inchangé et validation visuelle finale de cette fiche attendue.

### Portraits limités sur toutes les pages — 7 octobre 2026

Extension 1A validée : les cartes accueil/liste/recherche passent aussi à de
petits portraits sur ordinateur, limités à 150 × 150 px pour les trois fichiers
actuels 150 × 150 ; carte mobile 96 × 96 conservée. UX-CREA-006 dans
CREATOR_LIST.md remplace le portrait ordinateur 240 px historique. Fiche et
similaires conservent leurs limites 150/120 px. Rendu local et tailles calculées
contrôlés sur les trois pages ; aucune source retouchée ni backend modifié.

### Cartes horizontales sur ordinateur — 7 octobre 2026

Choix A validé après réflexion critique : carte commune horizontale aussi sur
PC, photo seule à gauche, puis nom/catégorie/présentation/profil à droite.
Aucune catégorie superposée au portrait. UX-CREA-007 dans CREATOR_LIST.md
remplace la carte verticale ordinateur ; mise en œuvre avec portrait 120 px
et deux colonnes sur grand écran, une colonne sous 1000 px, mobile 96 px.
Décision documentée avant code, rendus et dimensions comparés sur accueil,
liste et recherche, 320 px sans débordement. Backend inchangé.

## Historique des ajouts

Suivi du plan demandé le 7 octobre 2026 : le ticket Dashboard **#14** conserve
l'ordre de reprise des maquettes, de la conception et des vérifications ;
**#18** suit l'intégration Flask ultérieure avec tests avant le code. Le **#17**
conserve la charte différée et son contexte de cartes communes a été actualisé.
Enregistrements relus sur le VPS. Le Dashboard fait référence pour les états
et le plan de travail ; cette note ne constitue pas une seconde liste à faire
et ne lance aucun chantier.

| Version | Date | Modification |
| --- | --- | --- |
| 1.44 | 17 octobre 2026 | Révision après essai utilisateur : carrousel accueil mobile, retrait des deux blocs de sites et des tendances publiques ; choix et limites tracés. |
| 1.43 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 1.42 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 1.41 | 8 octobre 2026 | Retour accueil A validé, documenté puis corrigé/testé ; rapport de revue simplifié, aucune autre ambiguïté UX bloquante identifiée. |
| 1.40 | 8 octobre 2026 | Revue globale locale doc/code et navigateur : fallback cartes/états créateurs/doublons complétés, limites et question retour accueil consignées ; backend inchangé. |
| 1.39 | 8 octobre 2026 | Accueil complet adapté localement, grille préalable/relecture déléguées, sélections et états contrôlés navigateur ; backend inchangé. |
| 1.38 | 8 octobre 2026 | Accueil : 7A validé, masquage des blocs vides ; fiche UX prête pour adaptation avec décisions précédentes, maquette inchangée. |
| 1.37 | 8 octobre 2026 | Accueil : 5A/6A validés (raccourcis exacts, deux récents par catégorie) ; état des blocs vides encore ouvert. |
| 1.36 | 8 octobre 2026 | Accueil : accès rapides manuels A, trois derniers créateurs 2A et toutes catégories 3A validés ; détails de raccourcis/aperçus encore ouverts. |
| 1.35 | 8 octobre 2026 | Accueil : ordre de maquette conservé, nécessité des raccourcis ouverte et recommandation réexaminée selon la position des catégories. |
| 1.34 | 8 octobre 2026 | Fiche UX accueil complet créée avant évolution ; décisions existantes reprises, quatre choix proposés sans modification de maquette. |
| 1.33 | 7 octobre 2026 | Cartes horizontales PC validées (A), catégorie sous nom, grille adaptée ; UX-CREA-007 documentée puis appliquée et contrôlée. |
| 1.32 | 7 octobre 2026 | Petits portraits ordinateur généralisés après 1A via la carte commune : accueil/liste/recherche 150 px, mobile 96 px conservé ; doc avant CSS et contrôle local. |
| 1.31 | 7 octobre 2026 | Aperçus un/trois créateurs similaires fictifs ajoutés à la fiche ; zéro/un/trois et limites de rendu contrôlés sans données actives modifiées. |
| 1.30 | 7 octobre 2026 | Fiche créateur adaptée après validation ; portrait réduit explicitement demandé, source 150 × 150 et solution provisoire documentées, contrôles locaux consignés. |
| 1.29 | 7 octobre 2026 | Fiche créateur : dernier 2A validé, source simple privée au lancement, RM-TAL-003 v2.0 et RM-31 alignés avec historique ; pas de code changé. |
| 1.28 | 7 octobre 2026 | Fiche individuelle : 1A/3A/4A/5A validés ; visibilité des sources à préciser, RM-TAL-003 non modifiée. |
| 1.27 | 7 octobre 2026 | Fiche UX individuelle créateur créée avant modification ; cinq choix proposés, source manquante et catégorie divergente signalées. |
| 1.26 | 7 octobre 2026 | Lisibilité recherche : choix 1A documenté puis appliqué et contrôlé ; couleurs/tailles distinctes pour noms, descriptions et métadonnées. |
| 1.25 | 7 octobre 2026 | Allègement 1A avec bloc citron conservé : doc puis maquette, états et rendu contrôlés. |
| 1.24 | 7 octobre 2026 | Nouveau 1A : recherche commune simplifiée, liens Affiner retirés, historique 3A conservé. |
| 1.23 | 7 octobre 2026 | Recherche accueil commune et dédiée sites réalisées dans les maquettes ; texte transmis, retours et états contrôlés, preuves dans HOME_SEARCH.md. |
| 1.22 | 7 octobre 2026 | Recherche accueil : 3A validé, filtres sur pages dédiées avec texte conservé ; conception prête pour maquette. |
| 1.21 | 7 octobre 2026 | Recherche commune étendue aux créateurs après nouveau 1A/2A ; trois sections validées, périmètre précédent remplacé avec trace, accès aux filtres ouvert. |
| 1.20 | 7 octobre 2026 | Plan conservé au Dashboard : #14 complété, #17 actualisé et #18 créé pour l'intégration ultérieure ; références relues, aucun travail lancé. |
| 1.19 | 7 octobre 2026 | Validation visuelle utilisateur des cartes communes consignée ; limites et autres parcours préservés. |
| 1.18 | 7 octobre 2026 | Carte créateur commune accueil/liste validée par 1A et réalisée localement sur mobile et ordinateur ; détails dans UX-CREA-005. |
| 1.17 | 7 octobre 2026 | Recherche accueil : 1A/2A validés et consignés ; sections distinctes et accès à la catégorie complète, maquette non réalisée. |
| 1.16 | 7 octobre 2026 | Choix créateurs appliqués et contrôlés dans la maquette locale ; fiche de recherche accueil créée avec deux questions ouvertes. |
| 1.15 | 7 octobre 2026 | Liste créateurs : quatre choix validés. Recherche accueil à reprendre ensuite, périmètre sites/catégories précisé, fonctionnement encore à concevoir. |
| 1.14 | 7 octobre 2026 | Fiche dédiée à la liste créateurs créée ; volume mobile contesté, format compact proposé mais non présumé validé. Consigne de signalement des lacunes documentaires ajoutée à AGENTS.md. |
| 1.13 | 7 octobre 2026 | Liste créateurs : finitions C appliquées et contrôlées localement, grands portraits conservés. |
| 1.12 | 7 octobre 2026 | Finitions C transférées à accueil.html à la demande utilisateur ; cartes mobile, catégories repliables, textes et cibles vérifiés localement. |
| 1.11 | 7 octobre 2026 | Densité de la maquette catégorie corrigée après retour utilisateur pour se rapprocher de l’accueil C compact ; rendu local revérifié. |
| 1.10 | 7 octobre 2026 | Maquette catégorie réalisée et contrôlée localement ; backend inchangé et validation visuelle encore attendue. |
| 1.9 | 7 octobre 2026 | Page catégorie : validation de 6A et 7A, tri après recherche et retours précisés ; conception prête pour une future maquette, aucune réalisation déclarée. |
| 1.8 | 7 octobre 2026 | Page catégorie : cinq choix validés consignés dans un document dédié ; tri après recherche encore ouvert, aucune réalisation déclarée. |
| 1.7 | 6 octobre 2026 | Rappel de charte relié au ticket Dashboard #17 ; suivi du travail conservé dans le Dashboard. |
| 1.6 | 6 octobre 2026 | Rappel différé : formaliser la charte graphique à partir de C et de ses finitions, avec valeurs détaillées et historique à établir plus tard. |
| 1.5 | 6 octobre 2026 | Validation de `UX-GEN-009` après essai de maquette : menu Accueil/Créateurs/Proposer et accès aux tendances des sites près des plus consultés ; page et calculs conservés. |
| 1.4 | 5 octobre 2026 | Ajout de l'objectif de chaque élément à auditer et de l'utilité du kit visuel ; travail toujours différé. |
| 1.3 | 5 octobre 2026 | Ajout du travail différé : audit de cohérence mobile/PWA et kit visuel réutilisable, avec périmètre initial et estimations de tokens. Les décisions précédentes restent inchangées. |

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

- [Maquette mobile finale consolidée — 23 octobre 2026](FINAL_MOBILE_MOCKUP.md) : périmètre, décisions et preuves.
