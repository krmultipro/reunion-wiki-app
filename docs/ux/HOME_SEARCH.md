# Recherche depuis l’accueil — cadrage UX

## Navigation des variantes de maquette — 22 octobre 2026

[UX-HOME-024](HOME_PAGE.md) complète ce parcours : les liens entre pages partagées
conservent la version d’accueil via un contexte d’URL explicite autorisé ;
Accueil/logo revient à cette version. Les retours intermédiaires gardent leur
page d’origine et leurs critères. Dans l’essai Navigation flottante seulement,
les quatre rubriques restent accessibles en bas sur mobile ; les autres versions
conservent leur menu. Aucun changement des règles métier ou du backend.

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.10 |
| Date | 17 octobre 2026 |
| Statut | Recherche commune simple validée ; accès directs aux résultats sans liens Affiner |
| Réalisation | Maquette locale interactive contrôlée ; aucun backend intégré |

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
d’entreprises hors de cette rubrique au lancement. La section de résultats générique Créateurs devient Talents péi. Les trois types restent sites, catégories de sites et talents ; critères, nombres et retours conservés.

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Sources et décisions existantes

Le 7 octobre 2026, l'utilisateur reconsidère la recherche de l'accueil après
l'ajout des talents et valide les réponses `1A 2A` à un nouveau questionnaire :
recherche commune des **sites, catégories de sites et créateurs**, résultats en
**trois sections distinctes**, avec nombre de résultats. Il ne s'agit pas des
réponses 1A/2A du premier questionnaire, qui concernait uniquement les sites.

Réutiliser `PUBLIC_SEARCH.md`, `RM-SITE-007`, `CREATOR_LIST.md` et `RM-TAL-009` :
recherche explicitement lancée, texte et critères partageables dans l'URL,
visibilité limitée aux sites et créateurs publiés, états accessibles. Les
catégories de sites et de créateurs restent des référentiels distincts.

La route `/recherche` et le parcours public des sites existent. Leur conservation
et l'articulation technique avec les résultats communs seront précisées avant
intégration ; aucune URL publique n'est modifiée par cette conception. Les
recherches dédiées gardent leurs règles : sites avec catégorie/commune/tris,
créateurs avec catégorie principale/plateforme. Le nouveau choix `1A` de simplification retire les liens vers ces recherches
dédiées de la page commune. Leurs filtres restent disponibles sur leurs pages.

Le libellé actuel « Rechercher un site, une catégorie, une ville… » est encore
illustratif. Proposition adaptée au nouveau périmètre : « Rechercher un site,
une catégorie ou un créateur… ». Le texte exact reste à vérifier visuellement,
notamment sur mobile. Maquette désormais réalisée : libellé accessible complet
et placeholder court « Site, catégorie ou créateur… ».

## Décisions actuelles et historique de remplacement

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-HOME-SEARCH-001, version 3.0 | Recherche commune sites, catégories de sites et créateurs. Présenter les résultats par type : Créateurs, Catégories de sites et Sites, avec nombres. Afficher uniquement les sections ayant des résultats ; si tous les types sont vides, afficher un seul état sans résultat. Aucun classement mélangeant sites et personnes. Remplace la version 2.0 concernant l’affichage systématique des sections. Le périmètre commun de recherche reste inchangé. |
| UX-HOME-SEARCH-002 | Un clic sur une catégorie trouvée ouvre sa page avec tous ses sites, sans hériter du texte ou des filtres de la recherche, selon `UX-CAT-007`. Ce clic n'est pas une action de filtrage des résultats courants. |
| UX-HOME-SEARCH-003, version 2.0 | Nouveau 1A : recherche commune simple, sans panneaux de filtres et sans liens Affiner/Voir tous/Préciser par section. Cliquer directement sur un créateur ouvre sa fiche, sur une catégorie ouvre sa liste complète, sur un site ouvre le site externe. Les recherches dédiées et leurs filtres restent disponibles, sans accès supplémentaire ajouté ici. Remplace la version 1.0 (3A). |

### Allègement validé — 1A avec bloc citron conservé

L'utilisateur valide l'allègement proposé, avec exception explicite : conserver
le bloc citron de proposition. Décision `UX-HOME-SEARCH-004` : titre Résultats,
phrase d'introduction retirée, catégories et sites en lignes compactes sans
grands encadrés individuels. Conserver nom, domaine, description et commune si
renseignée pour les sites, ainsi que le lien externe et les cibles tactiles.
Les cartes créateurs restent le composant commun validé. Les sections vides
ne sont plus affichées, selon `UX-HOME-SEARCH-001` v3.0.

Ces décisions modélisent la modification de maquette ; elles ne sont pas
une adaptation rétroactive de la règle au code. Réalisation locale effectuée ensuite et contrôlée : transport affiche seulement
Catégories de sites (1) et Sites (1), sans section Créateurs vide. Rendu observé
sur ordinateur et mobile 390 px, aucun débordement à 320 px. Titre Résultats,
lignes sans fond blanc individuel et bloc citron confirmé par styles calculés.
Adriana conserve sa carte commune ; aucun résultat conserve un état global.
Syntaxe JS et diff vérifiés. Capture : `/tmp/reunion-wiki-recherche-allegee.png`.

### Choix remplacé conservé

`UX-HOME-SEARCH-001`, version 2.0 (**Remplacée par 3.0**) : trois sections
systématiquement visibles avec message propre à chaque section vide. Le nouveau
choix masque les sections sans résultat et conserve un état global si tout est vide.

`UX-HOME-SEARCH-001`, version 1.0 (**Remplacée par 2.0**) : recherche limitée
aux sites et catégories de sites, catégories et sites séparés, sans résultat
créateur. Ce choix, consigné en version documentaire 0.2, est remplacé par les
nouvelles réponses utilisateur. L'ouverture d'une catégorie vers sa liste
complète (`UX-HOME-SEARCH-002`) reste validée sans changement.

### Simplification validée — nouveau choix 1A

Pour cette version, le visiteur cherche, reconnaît un résultat puis clique.
La page commune conserve la séparation des types et leurs nombres, pour les
sections ayant des résultats selon le complément d’allègement. Aucun lien secondaire
vers une recherche dédiée n'est affiché par section.

`UX-HOME-SEARCH-003`, version 1.0 (**Remplacée par 2.0**) : le choix 3A
prévoyait Affiner les sites et Affiner les créateurs avec texte transmis. Ces
liens ont été réalisés et contrôlés en version 0.5, puis retirés à la demande
utilisateur. Les preuves ci-dessous restent l'historique de ce contrôle, pas
une exigence d'affichage actuelle. Les pages dédiées ne sont pas supprimées.

La validation de conception ne déclenche aucune implémentation. Conserver la
recherche explicitement lancée et les décisions transversales déjà validées ;
aucun résultat asynchrone à chaque caractère n'est ajouté. Les détails d'une
longue liste et de l'intégration seront précisés avant la réalisation concernée.

## Parcours à vérifier après conception

Visiteur : accueil → saisir/valider → résultats créateurs/catégories de sites/sites en sections distinctes →
fiche créateur, site externe ou catégorie → retour avec état de recherche conservé. Contributeur :
aucun résultat → proposition commune selon le parcours existant. Administrateur :
publication/archivage régissent la visibilité, sans nouveau workflow.

Définir avant réalisation les cas de correspondance site/catégorie/créateur, absence de
résultat, URL/retour, transmission du texte aux recherches dédiées, non-public exclu, clavier et mobile. Les tests actuels de
recherche de sites ne couvrent pas automatiquement les catégories ni la recherche commune de créateurs.

## Réalisation et vérifications — 7 octobre 2026

Réalisation demandée après validation : champ réel dans `accueil.html`, page
commune `recherche.html`, page dédiée `recherche-sites.html`, styles
`recherche.css` et simulation `recherche.js`. Données fictives de sites/catalogue
partagées avec la catégorie via `search-data.js`, afin de conserver les mêmes
noms et sites dans les résultats et dans les listes de catégorie.

- Trois profils de démonstration, cinq catégories et dix sites fictifs, sans
  base ni réseau pour rechercher ; aucun clic comptabilisé.
- Cartes créateurs communes réutilisées ; catégories vers leur liste complète.
- Liens Affiner vers les sites ou créateurs avec texte transmis. Page dédiée
  sites avec catégorie/commune/quatre tris, URL, réinitialisations, Affiner mobile.
- Lien retour d'Adriana adapté de façon limitée aux pages locales de liste ou
  recherche. Aucun portrait ou contenu éditorial de fiche modifié.
- Etats vide, sans résultat, chargement figé et erreur simulée accessibles par
  les liens d'aperçu ; Réessayer restitue la même recherche.

Parcours observés dans le navigateur : accueil/Entrée → emploi (une catégorie,
six sites), recherche Adriana (une créatrice), transmission du texte vers les
deux pages dédiées, clic catégorie sans texte hérité (six sites), retour Adriana,
filtre Saint-Denis (deux sites) puis effacement (six), Nouvelle recherche → champ
vide, erreur/Réessayer, chargement et sans résultat. REUNION retrouve les
correspondances Réunion dans les données simulées. Rendu observé à 390 et 1440 px,
largeur 320 px contrôlée sans débordement sur recherche commune et dédiée.

Cas définis avant réalisation et résultats consignés dans
[HOME_SEARCH_MOCKUP_CHECKS.md](../testing/HOME_SEARCH_MOCKUP_CHECKS.md).
Limites : statut public réel et moteur backend non vérifiés, profils distants
sans retour adapté, pas d'audit WCAG complet ni de longue liste paginée ;
classements et clics simulés seulement. Accès rapides de l'accueil encore
illustratifs. Validation visuelle utilisateur attendue ; finalisation Git des
maquettes encore distincte. Aucun template Flask, migration ou déploiement.

Disponible localement : `http://127.0.0.1:8765/maquettes/accueil.html` et
`http://127.0.0.1:8765/maquettes/recherche.html?q=emploi`.
Capture temporaire : `/tmp/reunion-wiki-recherche-mobile.png`.

## Contrôle de simplification — 7 octobre 2026

Liens retirés de `recherche.html` et références JS supprimées. Le parcours
Accueil → recherche et les accès aux résultats restent conservés. Réalisation
locale uniquement ; vérifier les trois types d'accès et l'absence des liens
avant livraison. Contrôle navigateur effectué : zéro lien secondaire, Transports
ouvre sa catégorie avec champ vide, Adriana ouvre sa fiche et son retour conserve
q=adriana ; attributs nouvel onglet/noopener noreferrer des liens sites vérifiés,
destination externe non activée. Les filtres dédiés restent inchangés. Tickets
#14/#18 actualisés et relus, état À faire. Syntaxe JS et diff vérifiés.
Capture temporaire : `/tmp/reunion-wiki-recherche-simple.png`.

## Lisibilité des résultats — choix 1A validé, 7 octobre 2026

`UX-HOME-SEARCH-005` : sur la recherche commune allégée, conserver le fond crème
`#F6F6EF` et les lignes sans grands encadrés. Noms de sites et catégories en
vert profond `#203C30`, descriptions de sites en `#405348` à 14 px, interligne
1.6. Domaines et communes restent secondaires en `#65705F` à 13 px ; liens
d'action verts `#087548`. Bloc citron et cartes créateurs communes conservés.

Cette décision est consignée avant modification CSS, sans formaliser la charte
complète ni généraliser ce changement aux autres pages. Vérifier le rendu et
les styles calculés après application, notamment les domaines qui doivent
rester à 13 px malgré la règle de description.

Réalisation locale et contrôle effectués : rendu observé à 390 px sur formation,
styles calculés conformes (noms rgb(32,60,48), descriptions rgb(64,83,72) et
14 px, domaines 13 px, actions rgb(8,117,72), fond rgb(246,246,239)). Aucun
débordement horizontal à 320 px. Diff vérifié, backend inchangé. Capture :
`/tmp/reunion-wiki-recherche-lisible.png`.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.10 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.9 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 0.8 | 7 octobre 2026 | Lisibilité 1A validée : noms foncés, descriptions 14 px plus sombres, fond crème et textes secondaires conservés ; UX-HOME-SEARCH-005 consignée avant CSS. |
| 0.7 | 7 octobre 2026 | 1A avec exception : sections vides masquées, titre et listes allégés ; bloc citron conservé. Règle 001 v3.0 et décision 004, avant modification de maquette. |
| 0.6 | 7 octobre 2026 | Nouveau 1A : retrait des liens Affiner par section, règle 003 version 1.0 remplacée par 2.0 ; parcours directs conservés. |
| 0.5 | 7 octobre 2026 | Maquette commune et dédiée sites réalisées, recherche accueil interactive, contrôles navigateur consignés ; backend inchangé. |
| 0.4 | 7 octobre 2026 | Réponse 3A : liens vers les recherches dédiées avec texte conservé ; conception suffisante pour maquette, aucune réalisation. |
| 0.3 | 7 octobre 2026 | Nouveau questionnaire 1A/2A : périmètre étendu aux créateurs, trois sections avec nombres validées ; ancienne règle marquée remplacée, accès aux filtres encore ouvert. |
| 0.2 | 7 octobre 2026 | Réponses 1A/2A validées : catégories et sites séparés, clic catégorie vers liste complète ; maquette non réalisée. |
| 0.1 | 7 octobre 2026 | Cadrage après réalisation de la maquette créateurs ; périmètre existant repris, deux questions ouvertes, aucune implémentation. |

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
