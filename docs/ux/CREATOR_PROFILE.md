# Fiche individuelle créateur — cadrage UX

## Aperçu ordinateur agrandi — 26 octobre 2026

[UX-PC-007](DESKTOP_MOCKUP_V1.md) remplace UX-FICHE-006 pour la seule fiche
`maquettes/pc-v1/personnalite.html` : l’utilisateur demande une composition PC
plus ample et accepte provisoirement le flou des petites photos en attendant
de meilleurs fichiers. Grand portrait et informations sur deux colonnes,
thème conservé, sans enrichissement des données. Les plafonds historiques
ci-dessous restent applicables aux autres variantes ; cette décision n’est
pas une intégration dans le site réel. Critères et preuves dans la fiche PC.

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
| Date | 17 octobre 2026 |
| Statut | Cinq choix validés ; source privée au lancement, prête pour adaptation |
| Réalisation | Maquette locale adaptée et contrôlée ; aucun backend modifié |

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
d’entreprises hors de cette rubrique au lancement. La fiche cible présente aussi artistes et artisans : activité, créations ou savoir-faire, pas seulement contenus sociaux. Aucun nouveau champ portfolio ni droit d’édition ajouté. Contact/email pour les demandes selon RM-TAL-007.

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Sources et périmètre

Sources : BUSINESS_RULES.md (RM-TAL-001 à 008, 010/011), catalogue RM-30 à 39,
CREATOR_LIST.md (retour avec critères/position), HOME_SEARCH.md (retour vers
recherche), UNIFIED_SUBMISSION.md (proposition/modération) et UX-GEN-006/007/008.
Première version : fiche publique sans compte et sans édition directe par le
visiteur. Ne pas intégrer les badges : leur proposition reste au ticket #10.
Les compteurs d'abonnés, contenus sociaux embarqués et nouveaux formulaires
spécifiques ne sont pas ajoutés par ce travail.

## Exigences validées à respecter

- Nom/pseudonyme, catégorie principale et présentation neutre ; pas de
  seuil d'audience ou d'activité pour être admissible (RM-TAL-002/005).
- Au moins un rattachement réel à La Réunion vérifié avec une source simple
  conservée en privé selon RM-TAL-001 et RM-TAL-003 v2.0 ; aucune rubrique
  Sources publique obligatoire au lancement, preuves privées jamais affichées.
- Portrait de taille limitée selon UX-FICHE-006 (complément utilisateur du
  7 octobre remplaçant le grand portrait de fiche) ; portrait facultatif,
  image générique sans droit vérifié manuellement (RM-TAL-004). Ce cadrage ne
  vérifie ni droits ni contenu de la fiche réelle d'Adriana.
- Réseaux et site officiel facultatifs (RM-TAL-008), afficher seulement les liens
  renseignés ; pas de bouton vide. Liens externes signalés, nouvel onglet et
  noopener noreferrer (UX-GEN-006). L'absence de réseau n'empêche pas une fiche.
- Fiche visible seulement si publiée ; brouillon/archivée absents du public.
  Création en brouillon et publication séparée (RM-TAL-006/010).
- Retour vers accueil, liste ou recherche d’origine selon provenance (A validé
  le 8 octobre) ; critères restaurés pour liste/recherche, position de
  liste conservée selon UX-CREA-004. Accès direct à la fiche : retour Créateurs.
- Demande de correction/retrait via contact ou email officiel, vérification
  admin et trace privée ; aucun accès direct d'édition (RM-TAL-007).

## Choix validés — réponses 1A/3A/4A/5A

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-FICHE-001 | Nom/catégorie puis présentation, puis liens officiels ; portrait limité selon UX-FICHE-006. La source est traitée séparément ci-dessous. |
| UX-FICHE-003 | Lien discret « Une information à corriger ? » sous la fiche, vers le contact existant, sans nouveau formulaire. Aucun droit de modification directe. |
| UX-FICHE-004 | Conserver jusqu'à trois créateurs publiés de la même catégorie dans À découvrir aussi ; masquer le bloc sans suggestion. |
| UX-FICHE-005 | Harmoniser l'exemple Adriana en « Humour & lifestyle » sur carte et fiche. Pas de modification automatique de taxonomie ni de donnée active. |

## UX-FICHE-002 — source privée au lancement, dernier choix 2A validé

L'utilisateur valide **2A du dernier questionnaire de lancement** : vérification
légère avec une source simple conservée dans l'administration, sans rubrique
Sources publique. Ce choix ne correspond pas au 2A précédemment proposé
(une source publique discrète) : ce dernier n'a pas été validé.

La règle métier RM-TAL-003 v2.0 et RM-31 remplacent explicitement l'obligation
d'affichage public. Il reste nécessaire de vérifier le rattachement avant
publication, par exemple via une bio officielle ou déclaration publique explicite.
Un article de presse systématique n'est pas requis. La référence de vérification
ne devient pas une donnée exposée au visiteur. Les réseaux officiels restent
les accès de découverte et ne prouvent pas automatiquement le lien réunionnais.

Historique : la version 0.1 proposait un bloc source visible, la version 0.2
une ligne discrète ; ces propositions ne sont pas retenues pour le lancement.
Cette décision autorise la conception documentaire ; aucun contrôle admin,
stockage, migration ou adaptation de maquette n'est déclaré réalisé ici.

Le nom de catégorie doit rester cohérent entre carte et fiche, conformément à
la catégorie principale unique (RM-36). Une éventuelle évolution de taxonomie
réelle constitue un sujet distinct avant intégration.

## UX-FICHE-006 — portrait peu défini, complément validé

L'utilisateur demande explicitement un portrait moins gros, une solution
provisoire pour les images peu définies et sa documentation. Ce choix remplace
la direction antérieure du grand portrait sur fiche ; les cartes accueil/liste
ne sont pas modifiées par cette demande.

Le fichier local Adriana mesure 150 × 150 pixels. Dans cette maquette, plafonner
le portrait à 150 × 150 px CSS sur ordinateur, 140 × 140 sur mobile et 120 × 120
sur les écrans de 360 px ou moins. Présenter le portrait à côté du nom/catégorie,
puis la présentation et les liens en pleine largeur sur mobile.

Ne pas agrandir une petite source pour remplir une grande surface. Préserver
le cadrage et servir l'original local ; aucun traitement visant à inventer des
détails du visage. Silhouette de profil neutre si absente/inutilisable, selon
la règle déjà validée. Les droits restent à vérifier indépendamment de la taille.

Pour l'intégration future : limiter l'affichage à la taille utile et à la
résolution disponible ; sur un écran à forte densité, une image 150 px peut
rester douce même à 150 px CSS. Ce plafonnement atténue le flou, il ne remplace
pas un meilleur fichier. Remplacement par une source plus définie et autorisée
à traiter ultérieurement, sans upload public ni nouvelle pipeline ajoutés ici.

## Parcours et états

Visiteur : liste/recherche/accueil → fiche publique → lire, suivre un lien
externe → retour à l'origine. Sans portrait : image générique ;
sans réseau : bloc non affiché ; présentation longue : contenu lisible et
reflow mobile. Catégorie/titre longs et cas sans suggestions à vérifier.
Fiche inconnue ou non publiée : état introuvable, sans révéler de statut privé.

Contributeur/talent : contact de correction → réception par canal existant →
vérification admin → correction, archivage ou refus motivé conservé en privé.
Ne pas promettre une notification automatique ou un délai non validé.

Administrateur : vérifie renseignements/rattachements/sources/portrait →
brouillon → publication distincte → correction ou archivage. La maquette ne
validera pas le fonctionnement administratif réel. Le pilote grandeur nature
RM-TAL-011 reste requis avant de déclarer le parcours talents prêt.

## État antérieur observé par lecture, avant adaptation

- Maquette talent-adriana.html : portrait, nom, catégorie, deux liens officiels,
  présentation et suggestions. Aucune rubrique source ni
  lien spécifique de correction ; Contact existe dans le pied de page.
- Écart : fiche « Influenceurs », carte « Humour & lifestyle ».
- creators.py::creator_detail appelle talent_service et renvoie 404 sans contexte.
  talent_service::get_public_talent_detail_context prépare image générique et
  jusqu'à trois profils similaires. Cette lecture ne prouve pas le parcours testé.
- templates/creators/detail.html contient bio/catégorie/commune ; pas de bloc
  source identifié par lecture ciblée. Intégration à comparer aux exigences
  validées avant code, sans réécrire la règle pour refléter cet état.

## Critères à préparer avant adaptation

Après validation des choix : ordre mobile/ordinateur, absence de rubrique source publique et absence de fuite de référence privée, absence d'image/réseau/suggestion, noms/textes longs,
liens externes/clavier/focus, origine/critères/position restaurés et accès contact.
Dans la maquette, les informations non vérifiées resteront clairement simulées :
aucune source justificative inventée pour Adriana ; sa vérification admin réelle
reste distincte de la maquette. Tests backend à partir des
exigences avant leur code ; vérifications de maquette séparées du pilote réel.

## Adaptation et contrôles locaux — 7 octobre 2026

Maquette `talent-adriana.html` adaptée selon les cinq choix, styles dans
`talent-profile.css` et états dans `talent-profile.js`. Portrait 150 × 150 px
sur ordinateur, 140 × 140 sur mobile 390 px et 120 × 120 à 320 px confirmés.
La résolution naturelle 150 × 150 du fichier est également confirmée dans le
navigateur. Aucun fichier image retouché ni source privée ajoutée.

Ordre nom/catégorie → présentation → réseaux observé ; catégorie harmonisée,
lien de correction vers le contact existant, absence de source publique,
image générique et absence de réseaux simulées. Texte long contrôlé à 320 px
sans débordement. Bloc suggestions masqué : aucun des trois profils illustratifs
existants n'a la catégorie Humour & lifestyle. Le code limite à trois les
correspondances de catégorie ; rendu de trois correspondances non testé lors de ce premier contrôle (complété
par les aperçus fictifs ci-dessous).

Retour vers recherche q=adriana contrôlé ; origine externe ignorée avec retour
Créateurs par défaut. Attributs des liens externes et destination de correction
vérifiés sans activer les services tiers. Position de liste déjà contrôlée dans
le parcours liste, non rejouée ici. Lecteur d'écran et zoom 200 % non testés.
Tests et preuves dans `testing/CREATOR_PROFILE_MOCKUP_CHECKS.md`.

Maquette locale uniquement, aucune vérification réelle du lien réunionnais,
autorisation de portrait, traitement contact, mutation admin ou production.
Validation visuelle utilisateur de ce nouveau rendu attendue. Capture temporaire :
`/tmp/reunion-wiki-fiche-adriana-portrait-reduit.png`.

## Aperçu des créateurs similaires — 7 octobre 2026

L'utilisateur demande à voir le rendu lorsqu'il existe des créateurs similaires.
Ajouter des états de maquette à un et trois profils fictifs de même catégorie,
avec image générique, sans attribuer un domaine non vérifié à des personnes
réelles. Les exemples ne disposent pas de fiche et ne sont pas cliquables ; le
parcours réel reste celui de UX-FICHE-004 (jusqu'à trois fiches publiées).

Sur ordinateur : trois petites cartes en colonnes. Sur mobile : cartes en
lignes, petit portrait à gauche et nom/catégorie à droite. Le cas sans profil
reste masqué par défaut. L'état de démonstration doit être explicitement signalé
et conserver l'origine de retour. Ne pas transformer cet aperçu en une donnée
active ou un nouveau classement.

### Contrôles de l’aperçu

États zéro/un/trois observés ; quatre candidats fictifs de même catégorie
produisent trois cartes visibles au maximum. Rendu mobile 390 px et ordinateur
1440 px observé, 320 px sans débordement. Vignettes génériques contenues dans
120 px sur ordinateur et 75 px sur mobile. Origine préservée dans les liens
1 similaire/3 similaires. Aucune donnée active, source ou catégorie réelle
modifiée ; exemples non navigables. Capture temporaire :
`/tmp/reunion-wiki-createurs-similaires-mobile.png`.

Retour utilisateur favorable sur la fiche réduite consigné. Complément du
7 octobre : rendu mobile À découvrir aussi validé par l'utilisateur. Il rappelle
que les images doivent également rester petites sur ordinateur du fait de leur
qualité limitée ; limites déjà documentées pour cette fiche : portrait 150 px
et vignettes similaires 120 px maximum. Extension 1A ensuite validée : cartes accueil/liste/recherche limitées à
150 px sur ordinateur, règle UX-CREA-006 dans CREATOR_LIST.md. Les limites
fiche 150 px et similaires 120 px restent inchangées.

## Ambiguïté révélée en revue — 8 octobre 2026

La règle synthétique mentionne retour liste/recherche, le parcours décrit aussi
accueil → fiche → retour à l'origine. La maquette renvoie actuellement vers
Créateurs depuis l'accueil. Question soumise : A retour explicite Accueil dans
ce cas, B garder Créateurs (et origine depuis liste/recherche uniquement).
Aucun retour Accueil ajouté avant réponse ; ne pas présenter le code existant
comme validation. Preuves de revue dans testing/MAQUETTE_UX_REVIEW_2026-10-08.md.

## Retour depuis l’accueil — A validé le 8 octobre 2026

`UX-FICHE-007` : depuis l'accueil, afficher Retour à l'accueil ; depuis la liste,
Retour à Créateurs avec critères/position ; depuis recherche, Retour aux résultats
avec texte conservé. Accès direct sans origine : Retour à Créateurs.

Ce choix résout l'ambiguïté précédente : ne pas limiter le retour à liste/recherche
si la fiche provient de l'accueil. Les destinations restent des pages locales
explicitement autorisées ; une origine externe/arbitraire est ignorée. Décision
consignée avant modification du lien et de son traitement.

Correction locale réalisée puis vérifiée : accueil → fiche → lien Accueil suivi
jusqu’à accueil ; origine externe ignorée et retour Créateurs conservé. Les
retours liste/recherche restent autorisés. Aucun backend modifié.

## UX-FICHE-008 — image de remplacement validée le 8 octobre 2026

L’utilisateur valide une silhouette de profil simple sur fond neutre pour les
portraits absents ou en erreur. La formulation antérieure « image générique
Réunion Wiki » ne définissait pas son dessin : le palmier repris de l’existant
n’avait pas été validé comme choix visuel. La silhouette remplace ce palmier
sur les cartes accueil/liste/recherche, la fiche et les similaires. Ressource
SVG locale, sans portrait inventé, sans agrandissement des dimensions validées.
Texte alternatif : « Photo de profil indisponible ». Les portraits présents
restent affichés. Aucun changement du backend ou des règles de droits.

UX-FICHE-007 confirmé : bouton « Retour à l’accueil », « Retour aux créateurs »
ou « Retour aux résultats » selon l’origine ; accès direct ou origine non
autorisée : « Retour aux créateurs ». Critères de contrôle : mêmes destinations
et critères conservés, libellé explicite, silhouette visible sans photo et sur
image en erreur, rendu compact mobile/ordinateur.

Réalisation locale du 8 octobre : SVG `maquettes/profile-placeholder.svg`
utilisé par creator-card.js et talent-profile.js ; portraits de démonstration
similaires et quatrième carte d’accueil alignés. Libellés explicites dans
creator-return.js et lien par défaut de talent-adriana.html. Navigateur :
silhouette chargée sur fiche sans-photo et trois cartes de liste (120 px PC),
photo Adriana conservée en accès normal, retour accueil suivi, recherche q=adriana
conservée dans la destination et accès direct vers Créateurs. Contrôles de
syntaxe des quatre scripts et git diff --check réussis. Les dimensions CSS
existantes sont conservées ; aucun nouveau contrôle mobile ni publication
backend annoncé pour ce complément.

## Contact depuis la fiche — complément du 8 octobre 2026

La page locale Contact validée dans SUPPORT_PAGES.md (1A) explique la demande
avant d’ouvrir le formulaire existant. UX-FICHE-003 conserve le lien discret
« Une information à corriger ? » ; sa destination maquette devient contact.html
avec origine conservée. Le formulaire et la modération restent inchangés.
Fiche → Contact → fiche vérifié avec retour liste q=adriana conservé.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.14 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.13 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 0.12 | 8 octobre 2026 | Contact local intermédiaire validé en 1A : correction depuis fiche et origine conservée contrôlées. |
| 0.11 | 8 octobre 2026 | Silhouette neutre validée à la place du palmier ; retour à l’origine confirmé avec libellés explicites. |
| 0.10 | 8 octobre 2026 | A validé : retour explicitement vers accueil/liste/recherche selon origine ; ambiguïté précédente résolue avant correction. |
| 0.9 | 8 octobre 2026 | Revue globale : formulations de retour accueil contradictoires signalées ; question A/B en attente, pas de décision implicite. |
| 0.8 | 7 octobre 2026 | Rappel petites images étendu explicitement par 1A aux cartes ordinateur ; UX-CREA-006 fait référence, limites de fiche/similaires inchangées. |
| 0.7 | 7 octobre 2026 | Mobile À découvrir aussi validé ; rappel de petites images ordinateur consigné, limites de fiche confirmées, portée accueil/liste à préciser. |
| 0.6 | 7 octobre 2026 | Aperçus de profils similaires fictifs demandés, états un/trois correspondances préparés, sans données ou catégorie réelle inventées. |
| 0.5 | 7 octobre 2026 | Fiche adaptée localement : contenu/réseaux/correction/catégorie, portrait limité et états facultatifs ; contrôles et limites consignés. |
| 0.4 | 7 octobre 2026 | Demande d’adaptation autorisée, portrait réduit demandé explicitement ; UX-FICHE-006 et limites de la source 150 × 150 documentées avant CSS. |
| 0.3 | 7 octobre 2026 | Dernier 2A validé : source simple privée au lancement, sans bloc public ; RM-TAL-003 v2.0/RM-31 mis à jour, autres choix conservés. |
| 0.2 | 7 octobre 2026 | Choix 1A/3A/4A/5A validés ; utilité de la source publique questionnée, affichage discret proposé, règle RM-TAL-003 conservée tant que non remplacée. |
| 0.1 | 7 octobre 2026 | Fiche dédiée créée avant adaptation ; exigences validées reprises, cinq propositions et écarts documentés. |

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
