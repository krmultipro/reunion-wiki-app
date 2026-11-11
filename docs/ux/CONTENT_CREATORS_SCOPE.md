# Personnalités réunionnaises — périmètre et historique

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Date | 20 octobre 2026 |
| Statut | Renommage public validé en maquette ; élargissement métier à préciser |
| Réalisation | Libellés de la maquette publique harmonisés ; aucun backend, donnée ou déploiement modifié |
| Remplace | Orientation large du 16 octobre dans TALENTS_PEI_SCOPE.md et RM-TAL-012 v1.0 |

## Amendement applicable — Personnalités réunionnaises, 20 octobre 2026

**UX-CONT-007 v1.0 — nom public validé.** L’utilisateur demande explicitement
« Personnalités réunionnaises » à la place de « Créateurs ». Le menu emploie
« Personnalités », les titres de rubrique « Personnalités réunionnaises » et
les actions « Proposer une personnalité » / « Toutes les personnalités ».
Ce nom inclut dans l’intention exprimée les créateurs émergents et les artistes
ou sportifs connus ou moins connus ; il n’établit aucun seuil de notoriété.

Ce choix remplace les seuls libellés génériques de UX-CONT-001 et des fiches
liste, profil, recherche et proposition. Les descriptions factuelles comme
« créateur de contenu », les biographies, les catégories et les données
d’exemple restent inchangées. Les routes, fichiers, identifiants techniques et
valeurs de formulaire historiques (`createurs`, `talent`, `createur`) restent
compatibles. Les versions figées et variantes historiques ne sont pas renommées.

**Lacune de conception explicitée avant modification :** le cadrage du
17 octobre ci-dessous limite encore l’admissibilité à la création de contenu.
La nouvelle intention d’ouverture aux artistes et sportifs n’en précise pas les
critères ni les catégories, la place des collectifs/structures, les modalités de
preuve et l’articulation avec le lien officiel obligatoire. Ces points restent
à concevoir avant toute admission ou adaptation métier ; les anciens critères
ne sont ni supprimés silencieusement ni présentés comme la nouvelle cible
validée. Aucune migration, ouverture backend ou nouvelle catégorie n’est réalisée.

La réalisation autorisée porte sur les libellés publics de la maquette : accueil,
menu, liste, recherche, formulaire de proposition, retours et aides. Recherche,
états vide/chargement/erreur et doublons doivent employer le même nom ; les
accords passent au féminin. Les parcours, images et règles de validation restent
ceux de la maquette existante, sans nouvel envoi réel.

Acceptation du renommage : absence de l’ancien nom générique dans le parcours
public courant, conservation des catégories/biographies factuelles et des
routes/valeurs techniques, syntaxe JS valide, puis contrôle mobile des libellés
plus longs. Le carrousel de personnalités et la liste de sites de l’accueil sont
suivis séparément dans [HOME_PAGE.md](HOME_PAGE.md).

### Réalisation et contrôles du renommage en maquette

Les libellés publics sont harmonisés sur liste, recherche, proposition,
confirmation, fiche, retours, Contact, FAQ et Mentions légales, en complément
de l’accueil. Les titres, labels accessibles et messages simulés de liste
vide/chargement/erreur ou doublon emploient le même vocabulaire. Les seuls
anciens termes conservés dans ces écrans sont les mentions d’activité factuelles.

Contrôles statiques du 20 octobre : syntaxe des cinq scripts modifiés vérifiée
avec `node --check` ; attributs techniques HTML (routes, sources d’images,
identifiants, classes et valeurs de formulaire) comparés à l’état précédent,
identiques ; `git diff --check` réussi dans la copie d’intégration. Les captures,
portraits et données n’ont pas été retouchés. Le contrôle visuel des textes plus
longs et de la navigation mobile est réalisé avec la révision de l’accueil ;
les seuls contrôles statiques ne le déclarent pas réussi.

## Historique de décision — 17 octobre 2026

## Décision et raison

L’utilisateur confirme : « on reste sur créateur de contenu ». La première
version se concentre sur la découverte de créateurs et de leurs contenus,
plutôt que sur l’ensemble des métiers et savoir-faire. L’élargissement aux
autres talents est conservé comme piste reportée, sans date ni réalisation
engagée. L’attractivité de ce choix n’est pas présentée comme mesurée.

## Décisions applicables

| ID | Décision et conséquence |
| --- | --- |
| UX-CONT-001 | Rubrique publique « Créateurs », action « Proposer un créateur ». Dans les aides, préciser « créateurs de contenu ». Le renommage générique Talents péi / Proposer un talent décidé le 16 octobre est remplacé. |
| UX-CONT-002 | Référencer des personnes ou collectifs pour leur activité de création de contenu et les contenus à découvrir. Être artisan ou artiste ne suffit pas à lui seul ; un artisan ou artiste qui crée aussi du contenu peut être considéré au titre de cette activité, selon les mêmes critères éditoriaux. |
| UX-CONT-003 | Lien réel à La Réunion vérifié, source simple privée, neutralité, portrait facultatif, absence de seuil d’audience, brouillon et publication distincte restent régis par RM-TAL-001 à 010. Aucune obligation de compte sur une plateforme précise ajoutée. |
| UX-CONT-004 | Proposition de soi ou d’un tiers sans compte au lancement. Nom et lien officiel obligatoires à l’envoi selon UX-PROP-002. Le lien sert à découvrir le créateur et son contenu ; il ne prouve pas automatiquement le rattachement à La Réunion. La proposition sans lien n’est pas ajoutée. |
| UX-CONT-005 | Corrections, archivage et retrait via Contact/email, vérification raisonnable d’identité et action administrative selon RM-TAL-007. Aucun accès d’édition directe. |
| UX-CONT-006 | Compte avec tableau de bord maintenu pour plus tard selon CONTRIBUTOR_WORKFLOW.md. Droits détaillés et éventuelle revendication de fiche encore ouverts ; aucun droit de propriété/publication automatique. |

Les fiches d’entreprises et les fonctions de devis, disponibilités, avis ou
classement de prestataires restent hors de cette rubrique. L’annuaire des sites
et ses règles ne changent pas. Les identifiants RM-TAL, noms de fichiers et
valeurs techniques historiques ne sont pas renommés ou supprimés.

## Parcours et présentation

Visiteur : accueil/recherche/liste Créateurs → fiche publiée → contenus et liens
→ retour selon les décisions UX existantes. Garder les cartes, sélection de
l’accueil, filtres et états déjà validés, avec contrôle mobile et clavier.

Proposant : Site/Créateur → nom et lien officiel pour le créateur, compléments
facultatifs selon UX-PROP-002 → erreurs/doublons ou confirmation en attente.
L’administrateur examine, complète ou refuse, rattache à une fiche existante
ou prépare un brouillon, puis publie séparément après contrôles. Rien n’est
publié automatiquement. Demande de correction/retrait → Contact/email →
vérification raisonnable → décision/action admin et trace privée.

## Conséquences sur les travaux précédents

- UX-TAL-001 et 002 sont remplacées par UX-CONT-001 et 002. UX-TAL-003 à 006
  restent compatibles et sont reprises ici pour le périmètre des créateurs.
- RM-TAL-012 v1.0 est remplacée par v2.0 ; le texte ancien reste consultable.
- La question de l’artisan sans présence en ligne ne bloque plus le lancement :
  ce parcours élargi est reporté. UX-PROP-002 conserve son lien obligatoire.
- RM-TAL-008 conserve les plateformes facultatives pour la fiche : ne pas
  confondre un lien demandé à la proposition, un compte social particulier et
  la preuve privée de rattachement. Aucun nouveau blocage de publication ajouté.
- Les trois exemples créateur/artiste/artisan et les tests d’ouverture du
  16 octobre sont reportés. Ne pas les lancer comme prochaine étape du ticket #14.
- Les types existants (chaîne, média, podcast, association, etc.) ne sont pas
  supprimés. Examiner les cas particuliers au regard de l’activité de contenu ;
  pas d’admission fondée uniquement sur un statut ou métier, ni migration implicite.

## Vérification et suivi

Relire les maquettes existantes au regard de ce périmètre avant de modifier les
écrans ; une structure déjà réalisée n’est pas déclarée validée par ce document.
Les critères actuels sont préparés dans testing/TALENT_TEST_CASES.md, non
exécutés par ce travail. Les décisions de normalisation des liens, les détails
du tableau de bord et les autres questions techniques des fiches UX restent
ouverts. Cette décision ne remet pas à zéro les choix UX déjà validés.

Documentation locale seulement. Aucun ticket Dashboard modifié ou clôturé,
aucun code, maquette, référentiel, base ou environnement déployé changé.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.1 | 20 octobre 2026 | Nom public Personnalités réunionnaises validé et appliqué aux libellés de maquette ; intention d’élargissement consignée, critères métier ouverts. |
| 1.0 | 17 octobre 2026 | Retour validé aux créateurs de contenu au lancement ; ouverture générale reportée, lien officiel conservé à la proposition. |

## Vérification navigateur complémentaire — 20 octobre 2026

Nom public observé sur les douze menus courants à 320 px sans débordement,
liste Personnalités réunionnaises, recherche Adriana et accès Proposer une
personnalité avec le bon type technique sélectionné ; formulaire non envoyé.
L’accueil conserve portraits et carrousel sous la liste de sites. Preuves et
limites dans [HOME_LIST_REVIEW_2026-10-20.md](../testing/HOME_LIST_REVIEW_2026-10-20.md).
