# Liste des créateurs — fiche UX

## Aperçu court dans les cartes — 23 octobre 2026

**UX-CREA-010 v1.0 — demande utilisateur après essai : ne pas tout écrire dans
la liste, afficher des points de suspension et lire la suite via le profil.**
Dans `createurs-categories.html` uniquement, limiter visuellement la présentation
à deux lignes avec « … » au débordement, comme l’aperçu court des cartes Sites.
Garder nom, catégorie et « Voir le profil ↗ » visibles, ainsi que les portraits
et les boutons. Le texte intégral reste dans les données et la recherche ; la
fiche dev demeure la destination de lecture complète, sans écriture de base.

Ce choix remplace dans cette variante la conservation visuelle intégrale des
descriptions lors de UX-CREA-009 ; il ne modifie ni les anciennes versions ni la
variante PC. Vérifier à 320/390 px la hauteur de deux lignes, le débordement avec
ellipse, la place du lien de profil, l’absence de débordement horizontal et la
recherche sur un mot présent dans la partie masquée.

## Catégories visibles dans la variante mobile — 23 octobre 2026

**UX-CREA-009 v1.0 — utilisateur : réaliser les boutons Personnalités après
vérification de la base dev, conserver les ambiguïtés de catégories en ticket.**
Cette décision remplace l’absence de filtre UX-CREA-008 uniquement dans la
variante mobile à catégories ; l’ancienne liste et la variante PC sont conservées.
La fiche existante ne tranchait pas cette évolution ; le choix explicite de
reprendre les boutons de Sites s’applique ici, sans refonte de la taxonomie.

- `createurs-categories.html` reprend les cartes et le style de la liste, avec
  les mêmes pastilles que Sites, sélection unique et « Toutes les catégories ».
- Copie statique des seuls champs publics des 29 profils publiés de **dev**,
  lus le 23 octobre en SQLite `mode=ro` ; pas d’accès base au chargement.
  Noms, catégories et descriptions existants conservés, sans nouveau classement
  ni admission métier. Les dix catégories remplies sont proposées ; les deux
  catégories vides Documentaire/Humoristes ne deviennent pas des filtres vides.
- Recherche existante nom/présentation combinée avec catégorie ; q et categorie
  dans l’URL. Retirer la recherche conserve la catégorie, effacer les critères
  rétablit les 29 profils. Historique, rafraîchissement et aides gardent les
  critères ; erreur technique distincte du zéro résultat et reprise conservée.
- Portraits locaux existants facultatifs, sans agrandissement ni enrichissement,
  silhouette si indisponibles. Les cartes ouvrent les fiches réellement présentes
  sur dev, avec sortie de maquette explicitée ; aucune fiche locale inventée.
- Conserver l’accueil, la navbar et les filtres Sites de la variante mobile.
  Les anciennes variantes restent comparables. Pas de pagination, compteur
  visible, compte utilisateur ou nouvelle action admin ; proposition simulée.

Critères avant réalisation : 29 profils et répartition 11/6/3/2/2/1/1/1/1/1
conformes à dev ; toutes catégories, recherche combinée, zéro résultat et
réinitialisation ; historique/rechargement/aide-retour ; boutons d’au moins
44 px, focus visible et sélection annoncée ; pas de débordement à 320/390 px ;
ancienne liste inchangée. Les observations navigateur seront consignées à part.

Les catégories se recoupant (Comédiens/Humoristes, activité versus notoriété de
Célébrités, frontières Divertissement/Influenceurs/Lifestyle) sont des ambiguïtés
à discuter, pas des doublons déjà prouvés. Le ticket Dashboard **#46** (À faire, enregistré et relu le 23 octobre) conserve la question
du périmètre et des critères de classement ; aucun renommage, fusion, suppression
ou réaffectation de profils n’est autorisé par cette réalisation.

## Navigation des variantes de maquette — 22 octobre 2026

[UX-HOME-024](HOME_PAGE.md) complète ce parcours : les liens entre pages partagées
conservent la version d’accueil via un contexte d’URL explicite autorisé ;
Accueil/logo revient à cette version. Les retours intermédiaires gardent leur
page d’origine et leurs critères. Dans l’essai Navigation flottante seulement,
les quatre rubriques restent accessibles en bas sur mobile ; les autres versions
conservent leur menu. Aucun changement des règles métier ou du backend.

## Nom public courant — amendement du 20 octobre 2026

[UX-CONT-007](CONTENT_CREATORS_SCOPE.md) remplace les libellés génériques
« Créateurs » par « Personnalités » dans le menu, « Personnalités réunionnaises »
dans les titres et « Proposer une personnalité » dans les actions de la maquette.
Les paragraphes et preuves historiques ci-dessous conservent leurs noms
antérieurs. Les parcours et données d’exemple restent inchangés ; l’intention
d’ouverture aux artistes et sportifs n’établit pas encore leurs critères
métiers. Aucun backend ni déploiement adapté par ce renommage.


| Métadonnée | Valeur |
| --- | --- |
| Version | 0.14 |
| Date | 23 octobre 2026 |
| Statut | Choix de liste et cartes communes validés ; longue liste à préciser avant intégration |
| Réalisation | Quatre choix réalisés et contrôlés dans la maquette locale ; backend non intégré |

## Simplification demandée — 20 octobre 2026

UX-CREA-008 v1.0 : retirer « Affiner » (et ses champs catégorie/plateforme) et
le nombre de créateurs de la maquette de liste, sur mobile et ordinateur.
Conserver la recherche textuelle explicite, l’ordre alphabétique, les cartes,
les états vide/chargement/erreur, la réinitialisation et le retour de fiche.
Aucun filtre masqué issu d’une ancienne URL ne doit restreindre cette maquette.
Le critère textuel actif reste visible et retirable ; l’annonce accessible
d’actualisation n’affiche ni ne prononce de nombre de créateurs.

Demande limitée à la maquette courante : la V1 figée reste intacte. Ce choix
remplace la présentation Affiner et compteur dans cette liste uniquement ;
les règles métier de filtres RM-TAL-009/RM-40 et les autres pages de recherche
ne sont pas réécrites. Leur articulation avec cette simplification restera
à traiter avant intégration Flask, qui n’est pas demandée ici.

Acceptation : aucun Affiner, champ de filtre ou compteur ; recherche « Adriana »,
zéro résultat, effacement et retour depuis sa fiche utilisables ; ancien lien
filtré sans restriction invisible ; rendu mobile/ordinateur sans débordement.
Réalisation locale : createurs.html/js et createurs-c.css adaptés ; annonce
accessible d’actualisation sans nombre. Navigateur : recherche Adriana ne garde
que sa carte ; accès fiche puis lien Retour conserve q=Adriana ; recherche
introuvable affiche l’état vide, Effacer les critères restaure la liste.
À 1280 px effectifs, ancienne URL categorie=humour&plateforme=tiktok : les trois
profils sont visibles, aucun select ni compteur. Rendu 390 px observé sans
débordement ; Affiner et compteur absents. Syntaxe JS contrôlée par node --check.
Capture locale : `/tmp/reunion-wiki-createurs-simplifie-20261020.jpg`.
Pas de nouvelle exécution complète des états chargement/erreur, ni d’essai
tactile physique, de test backend ou de publication. La copie V1 reste intacte.

## Complément carrousel de l’accueil — 17 octobre 2026

Complément du 20 octobre : UX-HOME-009 autorise désormais une carte verticale
et une présentation limitée visuellement à deux lignes pour le seul accueil
mobile. Cette exception remplace la disposition commune sur ce conteneur ;
la liste Créateurs, les résultats de recherche et l’accueil ordinateur restent
soumis aux cartes déjà validées ci-dessous. Voir [HOME_PAGE.md](HOME_PAGE.md).

Selon [HOME_PAGE.md](HOME_PAGE.md), réponses 1B/2A/3A/4A/5A, seul le conteneur
de la sélection de l’accueil mobile devient un carrousel manuel. Cette précision
complète UX-CREA-005/007 : mêmes cartes, contenu et portraits, mais disposition
du conteneur différente sur accueil mobile. La présente liste et les résultats
de recherche gardent leur disposition et leur ordre validés ; la grille de
l’accueil ordinateur reste inchangée. Aucun contrôle de cette révision encore
exécuté ; preuves historiques distinctes.

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
d’entreprises hors de cette rubrique au lancement. La liste cible s’intitule Talents péi ; son action devient Proposer un talent. Cartes, ordre alphabétique, filtres et retour conservés.

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Objet et sources

Cette fiche décrit la liste des créateurs, distincte de la fiche individuelle
et du formulaire de proposition. Sa création est demandée par l'utilisateur
après le constat d'un affichage mobile trop volumineux. Elle ne valide pas
rétroactivement les choix de présentation présents dans la maquette.

Sources : [décisions UX transversales](README.md),
[règles talents](../BUSINESS_RULES.md) (`RM-TAL-004/006/009`),
[catalogue](../business-rules/RULES_CATALOG.md) (`RM-36/37/38/40`),
[proposition commune](UNIFIED_SUBMISSION.md) et
[stratégie de tests](../testing/GLOBAL_TEST_STRATEGY.md).

## Exigences déjà validées

| Référence | Attendu et critère de vérification |
| --- | --- |
| UX-GEN-009 | Menu Accueil · Créateurs · Proposer. L'entrée Créateurs identifie la page courante. Aucun classement de créateurs n'est ajouté. |
| RM-TAL-006, RM-37 | Seules les fiches publiées apparaissent. Aucun brouillon ni créateur archivé ne doit être exposé, y compris dans les recherches. |
| RM-TAL-009, RM-40 | Recherche par nom, pseudonyme ou présentation ; filtres MVP catégorie principale et plateforme, combinables. Sans résultat, message clair et réinitialisation. |
| UX-GEN-001/002/003 | Recherche explicitement lancée ; filtres appliqués automatiquement ; critères dans l'URL. Sur mobile, filtres derrière Affiner, critères actifs visibles et retirables. |
| RM-36 | Une catégorie principale par créateur au MVP ; catégories secondaires en V2. |
| RM-TAL-004, RM-38 | Portrait facultatif ; image générique en son absence. Vérification manuelle des droits d'une image spécifique. |
| UX-PROP-011 | Lien Proposer un créateur sous la liste, vers le formulaire commun avec Créateur présélectionné et modifiable. Sans compte et sans upload photo selon le parcours validé. |
| UX-GEN-007/008 | Distinguer chargement, liste vide, recherche sans résultat et erreur technique ; labels, clavier, focus visible et contrastes accessibles. |

## Présentation : historique et décisions validées

La direction C enregistrée dans `README.md` prévoyait initialement des cartes
compactes sur l'accueil mobile et des portraits plus grands sur la liste et les
fiches. Les premières finitions de la liste ont conservé ce format.
Le retour utilisateur du 7 octobre 2026 signalait une liste mobile trop grosse.
La version 0.1 conservait la révision proposée sans présumer sa validation.

### Révision validée — réponses `1A 2A 3A 4A`

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-CREA-001 | Sur mobile, cartes horizontales compactes comme sur l'accueil. Les grands portraits restent sur la fiche individuelle ; le format ordinateur n'est pas remis en cause. Ce choix remplace le format mobile de liste à grand portrait précédemment enregistré. |
| UX-CREA-002 | Carte : petit portrait, nom, catégorie, courte présentation et accès au profil. Ne pas masquer ces informations pour gagner de la place ; prévoir les noms longs et une image générique. |
| UX-CREA-003 | Ordre initial alphabétique, sans priorité implicite ni classement de popularité. |
| UX-CREA-004 | Le retour depuis une fiche conserve la recherche, les filtres et la position de lecture de la liste. Vérifier le parcours réel, pas seulement la présence d'un lien Retour. |
| UX-CREA-005 | Complément validé par réponse 1A : l’accueil reprend la même carte créateur que la liste, sur mobile et ordinateur. Même disposition et contenu (portrait, nom, catégorie, présentation, accès au profil), avec styles communs ; la largeur disponible peut différer selon le conteneur. |

Le découpage d'une longue liste et d'éventuels tris supplémentaires restent à
préciser avant intégration réelle ; aucun tri supplémentaire n'est validé.
Ces points ne bloquent pas la maquette. Les dimensions exactes du format
compact seront précisées et contrôlées dans la prochaine réalisation.

## Parcours de bout en bout

- **Visiteur :** accès Créateurs depuis le menu ou l'accueil → consultation,
  recherche/filtres → fiche publique → retour à la liste. L'état des critères
  suit la décision URL ; critères et position de lecture sont restaurés selon
  `UX-CREA-004`.
- **Contributeur :** Proposer un créateur → formulaire commun présélectionné →
  erreurs ou doublon selon le parcours existant → confirmation de réception.
  L'envoi ne fait pas apparaître le créateur dans la liste.
- **Administrateur :** vérification/correction de proposition → création ou
  rattachement à une fiche → brouillon → publication distincte ou refus.
  Seule la publication rend la fiche admissible à la liste ; l'archivage la retire.

La correction et le retrait d'une fiche suivent les règles existantes
`RM-TAL-007` ; aucun droit d'édition directe n'est ajouté au proposant.

## État réel de la maquette et limites

Les quatre nouveaux choix ont été appliqués après la demande « Okayy vas y ».
La réalisation reste limitée aux maquettes locales.

`maquettes/createurs.html` et `createurs-c.css` présentent trois profils,
des portraits compacts sur mobile et grands sur ordinateur, nom, catégorie, courte description, accès aux profils
et proposition présélectionnée. Finitions C réalisées et observées localement
à 390 et 1440 px ; largeur 320 px contrôlée sans débordement. Accès Adriana et
formulaire avec Créateur présélectionné vérifiés le 7 octobre 2026.

`createurs.js` simule la recherche explicite et les filtres catégorie/plateforme
sur les trois profils, en conservant les critères dans l'URL. Les plateformes
sont renseignées pour Adriana uniquement (Instagram/TikTok) ; aucune plateforme
n'est inventée pour les deux autres profils. La liste est alphabétique et le
message sans résultat permet une réinitialisation.

Le lien local vers Adriana transmet une URL de retour autorisée à la fiche ;
`creator-return.js` adapte uniquement son lien Retour. La liste mémorise sa
position dans la session du navigateur. Retour par lien et Retour navigateur
contrôlés avec critères et défilement conservés (220 px avant/après).

Rendu réel observé à 390 px, largeur 320 px contrôlée sans débordement,
ordinateur trois colonnes/grands portraits 240 px conservés. Les contrôles
préparés avant le code et les résultats sont dans
[CREATOR_MOCKUP_CHECKS.md](../testing/CREATOR_MOCKUP_CHECKS.md).

Limites : profils distants Benji/Harendra sans retour adapté, aucun contrôle de
statuts/backend, aucun enregistrement. Chargement/erreur technique et absence
de portrait restent à vérifier avant intégration. Ces simulations ne valident
pas une mise en production ; validation visuelle utilisateur encore attendue.

## Contrôles à préparer avant la prochaine réalisation

À partir du format et des comportements validés, définir les tests avant le code :
cartes mobile/ordinateur, absence de portrait, nom long et description longue,
recherche explicite, combinaison catégorie/plateforme, réinitialisation, URL,
statuts invisibles, états d'interface, ouverture de fiche et retour à la liste.
Vérifier visuellement les tailles, focus et débordements à 320 et 390 px.
Ne pas déclarer ces cas réussis sur la seule lecture du code.

## Carte commune accueil/liste — 7 octobre 2026

`UX-CREA-005` est réalisée localement dans les deux maquettes avec
`creator-card.css`, chargé par `accueil.html` et `createurs.html`. Les classes
communes préservent les titres h3 sur l'accueil et h2 sur la liste, conformément
à leurs hiérarchies. La catégorie passe du badge sur portrait à une ligne de
texte dans le corps sur mobile, puis présentation et accès au profil.

Vérifications navigateur : mêmes styles calculés sur les deux pages à 390 et
1440 px (portrait 96/240 px, titres 18/24 px, texte 13 px, action 44 px,
arrondis 14/20 px, padding 10 px). Rendus réels observés, aucun débordement à
320 px, accès Adriana et Tous les créateurs vérifiés. Catégories repliables de
l'accueil toujours utilisables ; ordre alphabétique de la liste conservé.

La sélection de l'accueil n'est pas réordonnée par cette décision. La recherche
accueil reste un chantier distinct. Aucune modification Flask ou production.
Capture temporaire : `/tmp/reunion-wiki-accueil-cartes-communes.png`.

## Validation visuelle utilisateur — 7 octobre 2026

Après application de la carte commune, l'utilisateur indique « ça m'a l'air
d'être bon ». Validation de la présentation actuelle des cartes accueil/liste,
sans étendre ce constat à la recherche accueil, à la fiche individuelle, aux
cas limites non vérifiés ou au backend. Les limites de contrôle précédentes
restent applicables.

## UX-CREA-006 — petites images sur toutes les pages, 1A validé

L'utilisateur confirme l'extension de la règle provisoire aux images sur
ordinateur, pas seulement à la fiche et aux similaires. Les trois portraits
locaux (Adriana, Benji, Harendra) sont chacun de 150 × 150 pixels.

Pour les cartes communes accueil/liste/recherche : portrait carré limité à
150 × 150 px CSS sur ordinateur, centré dans sa carte ; 96 × 96 px sur mobile,
comme précédemment. Cette précision remplace le portrait ordinateur de 240 px
réalisé dans les versions précédentes ; la disposition et le contenu des cartes
restent communs. Fiche : limite 150 px ordinateur ; similaires : limite 120 px,
selon CREATOR_PROFILE.md. Aucun agrandissement pour remplir la largeur de carte.

Solution de lancement, sans amélioration artificielle ni nouvelle source : les
images restent douces sur un écran à forte densité. Une meilleure source
vérifiée/autorisée sera nécessaire pour un rendu plus défini. Ne pas rétablir
un grand portrait sans réexaminer sa résolution et la décision de présentation.
Décision consignée avant CSS, puis appliquée dans creator-card.css partagé.
Contrôle navigateur sur ordinateur (largeur 830 px) : les trois portraits de
la liste et de l’accueil, ainsi que le portrait des résultats Adriana, mesurent
150 × 150 px CSS. Rendu observé, aucune image locale transformée. La règle
mobile conserve explicitement 96 × 96 px. Diff contrôlé, backend inchangé.
Capture temporaire : `/tmp/reunion-wiki-petits-portraits-pc.png`.

## UX-CREA-007 — carte horizontale sur ordinateur, choix A validé

L'utilisateur valide explicitement les cartes horizontales aussi sur PC après
comparaison critique avec la carte verticale à petite image centrée. Cette
révision remplace la disposition verticale ordinateur des versions précédentes.
Photo seule à gauche ; à droite : nom, catégorie en texte sous le nom,
présentation, puis Voir le profil. Aucun badge de catégorie sur le portrait.
Le placement sur l'image hérité du CSS n'était pas une décision UX validée et
ne doit pas être présenté comme tel.

Conserver la carte commune sur accueil/liste/recherche. Mise en œuvre prévue :
portrait 120 × 120 px sur PC (sous le plafond 150), 96 px sur mobile ; titre
20 px PC/18 px mobile. Deux colonnes quand la largeur permet un texte confortable,
une colonne sous 1000 px, y compris sur mobile. Pas trois cartes étroites
avec photo à gauche. Catégorie 13 px PC/12 px mobile, description 13 px,
accès profil 44 px minimum. Les fichiers de portrait ne sont pas agrandis.

Décision consignée avant CSS puis appliquée au composant commun. Contrôles
navigateur : accueil/liste/recherche à 1440 px en deux colonnes, portrait 120 px,
catégorie visible dans le texte et badge masqué ; PC étroit 830 px en une
colonne, mobile 390 px avec portrait 96 px. Aucun débordement à 320 px.
L’ordre nom/catégorie/description/profil est également inscrit dans le HTML,
pas seulement dans le CSS. Syntaxe recherche.js et diff contrôlés. Fiche
individuelle et catégories de sites inchangées ; suggestions conservent leur
dispositif validé. Validation visuelle de cette nouvelle disposition attendue.
Capture temporaire : `/tmp/reunion-wiki-cartes-horizontales-pc.png`.

## Complément de revue globale — 8 octobre 2026

creator-card.js gère désormais l'image générique sur carte absente ou en erreur,
y compris ajout dynamique sur accueil/liste/recherche. Aperçu portrait=absent
vérifié. États liste vide, chargement et erreur ajoutés, distincts du zéro résultat ;
Réessayer conserve le texte et les filtres. Ces compléments réalisent des exigences
déjà validées UX-GEN-007/RM-TAL-004, sans nouvelles règles produit.

Mémoire d'origine normalisée et restauration après disponibilité des polices ;
critères q/catégorie/plateforme contrôlés. Petit écart de position (6 px) dans
l'émulation observé : précision exacte non déclarée validée. Preuves et limites
courantes dans testing/MAQUETTE_UX_REVIEW_2026-10-08.md.

## Image de remplacement — complément validé le 8 octobre 2026

Selon UX-FICHE-008, les cartes communes utilisent une silhouette de profil
neutre locale si le portrait manque ou échoue, à la place du palmier hérité.
Les dimensions et le format horizontal validés sont conservés. Cette décision
s’applique aussi à l’accueil et aux résultats de recherche.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.12 | 17 octobre 2026 | Révision après essai utilisateur : carrousel accueil mobile, retrait des deux blocs de sites et des tendances publiques ; choix et limites tracés. |
| 0.11 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.10 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 0.9 | 8 octobre 2026 | Silhouette neutre validée pour les portraits absents/en erreur des cartes communes. |
| 0.8 | 8 octobre 2026 | Revue globale : fallback cartes, états de liste et restauration normalisée complétés, preuves navigateur/limites consignées. |
| 0.7 | 7 octobre 2026 | Choix A : carte horizontale PC, catégorie sous nom et aucun badge sur image ; largeur de grille et petit portrait définis avant CSS. |
| 0.6 | 7 octobre 2026 | Extension 1A validée : petites images aussi sur cartes ordinateur, max 150 px ; source des trois portraits confirmée, carte mobile 96 px conservée. |
| 0.5 | 7 octobre 2026 | Retour utilisateur favorable consigné comme validation visuelle des cartes communes, sans validation globale du parcours ni du backend. |
| 0.4 | 7 octobre 2026 | Réponse 1A : carte commune accueil/liste validée sur mobile et ordinateur, styles partagés et contrôles locaux réalisés. |
| 0.3 | 7 octobre 2026 | Quatre choix appliqués aux maquettes après demande explicite ; recherche/filtres simulés, retour Adriana et position contrôlés ; limites documentées. |
| 0.2 | 7 octobre 2026 | Réponses 1A/2A/3A/4A validées : liste mobile compacte, contenu des cartes, ordre alphabétique et retour avec critères/position conservés. Réalisation encore distincte. |
| 0.1 | 7 octobre 2026 | Création demandée, sources et exigences reprises ; critique du volume mobile et proposition de format compact conservées sans validation supposée. |

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
