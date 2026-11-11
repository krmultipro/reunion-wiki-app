# Contribution avec compte — conception en cours

## Révision de présentation — 23 octobre 2026, après essai

L’utilisateur demande d’appliquer la simplification proposée après sa difficulté
initiale de compréhension : UX-CDM-011 dans
[CONTRIBUTOR_DASHBOARD_MOBILE.md](CONTRIBUTOR_DASHBOARD_MOBILE.md).
Mon suivi, À compléter, Mes brouillons et Dernières mises à jour remplacent les
titres indirects ; les compteurs sont retirés et les demandes ne sont plus répétées.
Le suivi complet s’appelle Toutes mes demandes. Les statuts techniques et processus
ci-dessous restent inchangés ; `acceptee` s’affiche désormais Correction appliquée,
`en_attente` En attente de vérification et `preparation` Fiche en préparation.

## Amendement applicable — maquette du dashboard mobile, 23 octobre 2026

L’utilisateur demande désormais de documenter les processus et de réaliser une
maquette mobile du tableau de bord contributeur pour se projeter. Après les
questions de conception, il délègue les choix à l’agent (« fais comme bon te
semble […] vas y bosse bien »). Cette autorisation remplace les mentions
antérieures « aucune maquette demandée » pour cette variante isolée seulement.
Elle n’autorise pas de backend, migration, email réel ou déploiement et ne change
pas le lancement sans compte.

Les [contrôles de maquette et captures](../testing/CONTRIBUTOR_MOBILE_REVIEW_2026-10-23.md)
ont été réalisés localement : ils ne remplacent ni la validation visuelle
utilisateur ni les futurs tests métier et de permissions serveur.

La fiche [CONTRIBUTOR_DASHBOARD_MOBILE.md](CONTRIBUTOR_DASHBOARD_MOBILE.md)
consigne UX-CDM-001 à 010, les processus et AC-CDM-01 à 12 avant réalisation.
Choix retenus sous délégation : actions prioritaires au dashboard ; brouillons
manuels ; envoi en lecture seule, annulation avant décision et réponse aux
compléments ; nouvelle version liée après refus ; corrections du nom, de la
présentation et du lien officiel avec motif, sans portrait. Le compte ne donne
aucun droit propriétaire ni de publication. « Acceptée » pour une correction
appliquée reste distinct de « Publiée » pour une proposition.

Dans la variante réalisée, une proposition retenue passe par « En préparation »
avant publication administrative séparée ; la décision positive déjà prise
interdit alors l’annulation. Les corrections appliquées passent directement à
« Acceptée ». Les écrans restent des simulations locales et non des routes ou
comptes Flask.

Le nom public courant est « Personnalités » selon UX-CONT-007 du 20 octobre ;
les noms Créateur/Talent historiques ci-dessous sont conservés. La maquette
emploie des données fictives et une authentification simulée ; la validation
visuelle utilisateur et les tests des fonctions serveur restent à effectuer.
Les modalités techniques de stockage réel, durée des jetons, conservation,
fermeture de compte et conflits administratifs détaillés restent ouvertes.

## Décision applicable — 17 octobre 2026

Le lancement reste centré sur les créateurs de contenu selon
[CONTENT_CREATORS_SCOPE.md](CONTENT_CREATORS_SCOPE.md). Le renommage Site/Talent
et l’ouverture générale du complément du 16 octobre sont remplacés : Site/Créateur
reste la cible. Le souhait du compte avec tableau de bord demeure reporté ; ses
droits détaillés et une éventuelle revendication de fiche restent ouverts.
Au lancement : proposition sans compte avec nom et lien officiel, demandes de
correction/retrait par Contact/email selon RM-TAL-007. Aucun compte réalisé.


Version : 0.8. Date : 23 octobre 2026.
Statut : conception d’une évolution ultérieure ; hors première version de lancement.
Réalisation : documentation et maquette mobile isolée autorisées le 23 octobre ;
aucune implémentation métier, migration ou publication autorisée.

## Confirmation — Talents péi et tableau de bord, 16 octobre 2026

L’utilisateur confirme vouloir à terme un compte avec tableau de bord, tout en
le reportant après le lancement. La rubrique cible est Talents péi selon
[TALENTS_PEI_SCOPE.md](TALENTS_PEI_SCOPE.md), UX-TAL-001 à 006. Les mentions
Site/Créateur dans les décisions précédentes se lisent Site/Talent dans cette
cible ; les identifiants existants sont conservés.

Le tableau de bord doit encore être détaillé : suivi des propositions et
corrections, informations affichées et droits. Une éventuelle revendication de
fiche et sa vérification restent ouvertes ; aucun rôle propriétaire ni droit
d’édition/publication directe n’est accordé par la confirmation. Les décisions
contributeurs déjà validées restent applicables. Au lancement, correction,
archivage et retrait passent par Contact/email puis vérification et action
administratives selon RM-TAL-007. Aucun compte ni écran supplémentaire réalisé.

## Clarification de priorité — 9 octobre 2026

L’utilisateur précise que le formateur a déjà vu la maquette. Cette réflexion
sert maintenant à clarifier une future évolution du projet, en vue de la
présentation de fin d’année qui sera préparée plus tard. Elle ne demande pas
de nouvelle maquette pour le formateur ni de réaliser les comptes maintenant.

Priorité validée : première version publique sans compte contributeur, avec
administration authentifiée. Le parcours initial de proposition sans compte
reste applicable au lancement. Les choix UX-CONTRIB-001 à 010 sont conservés
pour l’évolution ultérieure et ne conditionnent pas la première mise à disposition.
Cette clarification remplace leur interprétation comme périmètre du lancement ;
elle ne supprime pas les choix de conception future ni les questions ouvertes.

## Origine et décisions validées

Après le retour du formateur CDA sur la profondeur fonctionnelle et
l’automatisation, l’utilisateur a validé les réponses `1A 2A 3A` :

- UX-CONTRIB-001 : compte contributeur, sans attribution automatique d’une
  identité de créateur ni propriété d’une fiche.
- UX-CONTRIB-002 : tout contributeur connecté peut proposer une correction
  de fiche créateur ; validation administrative obligatoire avant application.
- UX-CONTRIB-003 : concevoir les trois fonctionnalités : contribution avec
  compte et modération, corrections avec historique des versions, notifications
  automatiques fiables. La validation porte sur la conception, pas la réalisation.

Le périmètre initial de cette extension concernait les créateurs. Après objection
de l’utilisateur, la recommandation a été révisée en faveur d’un compte commun
pour proposer les deux types, puis validée par la réponse 4A.
L’inscription d’un compte ne donne aucun droit de publication directe.

Complément validé dans la même conversation :

- UX-CONTRIB-004 : vérifier l’adresse email avant l’envoi d’une proposition ou
  correction (réponse affirmative à 5A). Les modalités de vérification et de
  renvoi du message restent à concevoir.
- UX-CONTRIB-005 : plusieurs corrections peuvent attendre sur une même fiche
  (6B). Avant acceptation, comparer la correction à la version actuelle et
  traiter les conflits ; aucune ancienne proposition ne doit écraser
  silencieusement une modification déjà acceptée. Interface de résolution
  des conflits encore à préciser.
- UX-CONTRIB-006 : compte contributeur avec email vérifié obligatoire pour
  proposer un site ou un créateur (4A). Le parcours initial anonyme de
  UX-PROP-003/007 est remplacé sur ce point pour la cible à concevoir ; il reste
  visible comme décision historique et comme état de la maquette actuelle.

UX-CONTRIB-007 : après explication des alternatives, l’utilisateur confirme
le parcours email → lien reçu → choix du mot de passe ; les connexions suivantes
utilisent email et mot de passe. L’inscription initiale est en attente, sans
mot de passe ; le compte devient actif après vérification du lien et création
du mot de passe. La reprise d’inscription et la récupération du compte restent
à détailler, sans confondre compte actif et inscription en attente.

Dernières réponses validées : `7A 8A 9A`.

- UX-CONTRIB-008 : connexion ou activation du compte avant de remplir le
  formulaire ; retour au formulaire après inscription. Aucun formulaire de
  proposition commencé anonymement n’est à conserver pendant l’inscription.
- UX-CONTRIB-009 : notifications à l’admin à réception d’une proposition ou
  correction ; au contributeur à réception, demande de complément et décision.
  Les étapes internes de vérification ne produisent pas un email à chaque action.
- UX-CONTRIB-010 : si la fiche a changé depuis une correction proposée,
  bloquer l’acceptation directe ; l’admin compare et résout les différences
  explicitement. Aucune fusion automatique ni écrasement silencieux.

## Lien avec le périmètre existant

Les décisions UX-PROP-003/006/007 de UNIFIED_SUBMISSION.md décrivent le parcours
initial sans compte, email facultatif et sans notifications automatiques.
Le futur périmètre introduit les comptes et notifications pour le parcours
à concevoir ; 4A remplace l’envoi anonyme par une contribution avec compte et
email vérifié pour les deux types dans cette évolution ultérieure seulement.
Le lancement conserve l’envoi sans compte, selon la clarification de priorité.
Ne pas transformer les anciennes décisions en implémentation du nouveau
parcours. RM-TAL-006 et les critères de publication restent applicables.
RM-54 réserve actuellement la gestion aux administrateurs ; distinguer proposer
une correction et appliquer une modification.

## Rôles — proposition à préciser

Visiteur sans compte, contributeur connecté et administrateur sont les trois
profils de parcours envisagés. Visiteur n’est pas nécessairement un rôle stocké.
Un créateur référencé est une entité de contenu ; aucun rôle Créateur n’est
validé. Un rôle Modérateur distinct n’est pas demandé ni validé à ce stade.
La modération reste administrative selon les décisions existantes.

## Parcours complet — base de conception

Les droits de publication et séquences ci-dessous reprennent les choix validés.
Les modalités de reprise, messages, écrans et stockage détaillés constituent
des propositions à relire ; leur présence ici ne vaut pas validation utilisateur.

### Visiteur, inscription et accès

1. La consultation publique reste accessible sans compte. Depuis « Proposer »
   ou une action de correction, une personne non connectée passe par l’accès
   au compte, avant le formulaire (UX-CONTRIB-008).
2. Inscription : email → lien d’activation → choix du mot de passe → compte
   actif avec email vérifié. Conserver le type et la destination demandés,
   sans conserver un formulaire anonyme inexistant.
3. Proposition de reprise : « Renvoyer le lien » pour une inscription inachevée,
   « Mot de passe oublié » pour un compte actif. Lien expiré ou utilisé : message
   explicite et possibilité de demander un nouveau lien, sans activation implicite.
4. Une erreur d’envoi ne doit pas être présentée comme un email livré. Empêcher
   les réponses publiques de révéler si une adresse possède déjà un compte.
5. Une personne connectée accède directement au formulaire. Après déconnexion,
   les pages privées ne restent pas accessibles ; un retour peut demander connexion.

### Proposition Site ou Créateur

1. Compte actif → formulaire adapté au type → contrôles → réception en attente.
   Réutiliser UX-PROP-002 et les critères RM-SITE-010 ; le compte n’annule aucun
   contrôle de doublon, d’admissibilité ou de publication.
2. Le proposant peut suivre ses propres propositions. Les données privées
   d’un autre contributeur restent inaccessibles. Email issu du compte confirmé,
   pas une adresse libre permettant d’attribuer l’envoi à quelqu’un d’autre.
3. Confirmation proposée : « Ta proposition a été reçue. Elle sera vérifiée
   avant publication. » Accès au suivi et retour aux contenus publics.
4. Admin : examiner → demander un complément, refuser avec motif ou poursuivre
   le traitement. Un complément reçu retourne à la vérification, sans publication.
5. Créateur : préparer ou rattacher à un brouillon, compléter les informations
   et effectuer une publication distincte selon RM-TAL-006 et UX-PROP-004.
   Site : appliquer le cycle et les contrôles existants de RM-SITE-002/006.
6. Publication ou refus : suivi et notification au contributeur. Proposition
   refusée ou en attente ne devient jamais publique ; fiche publiée seule visible.
   Les permissions de retrait et de nouvelle soumission après refus restent ouvertes.

### Correction et historique des créateurs

1. Tout contributeur connecté et vérifié peut proposer une correction. Enregistrer
   sa proposition et la version de référence de la fiche, sans toucher au public.
2. Plusieurs corrections peuvent attendre ; chacune conserve son auteur et
   son contenu. Le contributeur suit sa correction, sans obtenir un droit d’édition.
3. Admin : comparer version de référence, proposition et version actuellement
   publiée. Demander un complément, refuser ou accepter après les contrôles métier.
4. Si la version actuelle a changé, interdire l’acceptation directe. Présenter
   les différences et faire préparer explicitement le résultat retenu. Vérifier
   de nouveau la version lors de l’enregistrement : une seconde modification
   concurrente doit rouvrir le conflit plutôt qu’écraser la fiche.
5. Acceptation : mettre à jour la fiche et conserver l’auteur de la correction,
   l’admin ayant décidé, la date et les valeurs avant/après. Refus : fiche inchangée,
   décision conservée et notification au contributeur.
6. Une modification directe par l’admin doit aussi alimenter l’historique pour
   éviter des changements sans trace. Détail du périmètre et accès à cet historique
   restent à valider. Restaurer une ancienne version n’est pas inclus implicitement.

### Notifications fiables — conception technique proposée

| Événement validé | Destinataire |
| --- | --- |
| Nouvelle proposition ou correction reçue | Administrateur et contributeur concerné |
| Complément demandé | Contributeur concerné |
| Décision de modération | Contributeur concerné |

Enregistrer l’événement métier et la notification à envoyer de manière cohérente,
puis traiter l’envoi séparément. Une panne email ne supprime pas la proposition
et ne bloque pas une décision enregistrée. Suivre les tentatives et échecs,
réessayer de manière bornée et éviter de recréer plusieurs notifications pour
le même événement. Ne pas promettre une livraison exactement une fois si le
prestataire accepte un email puis coupe la connexion avant confirmation.
Un envoi accepté par le prestataire ne prouve pas la réception dans la boîte mail.
Les liens de suivi demandent une connexion et ne donnent pas de droit de modération.

### États, retours et mobile — proposition de présentation

- Espace contributeur vide : expliquer le suivi et fournir « Proposer ».
- Recherche sans résultat : conserver les critères et permettre leur retrait.
- Formulaire invalide : erreurs près des champs et valeurs conservées.
- Panne technique : message avec possibilité de réessayer sans doubler l’envoi.
- Session expirée pendant une saisie : prévoir une reprise après connexion ;
  modalités de conservation privée à préciser, sans sauvegarde anonyme implicite.
- Après envoi : confirmation et accès à la demande ; après modération : retour
  à la file avec filtres conservés, selon UX-ADMIN-003.
- Mobile : étapes lisibles, actions accessibles au clavier, statuts en texte ;
  comparaison des corrections par champ plutôt qu’un tableau horizontal imposé.
  La disposition de cette nouvelle interface reste à relire avant maquette.

## Critères d’acceptation et vérifications proposées

Ces critères dérivent des décisions validées et prépareront les tests ; aucun
test ni contrôle de la nouvelle fonctionnalité n’a encore été exécuté.

| ID | Critère | Vérification prévue |
| --- | --- | --- |
| AC-CONTRIB-01 | Visiteur et compte non activé ne peuvent envoyer Site/Créateur/correction ; consultation publique conservée. | Intégration Flask, accès GET/POST et permissions. |
| AC-CONTRIB-02 | L’activation exige un lien valide et un mot de passe ; lien expiré/utilisé refusé et reprise disponible. | Service et parcours navigateur d’inscription. |
| AC-CONTRIB-03 | Le compte ne donne accès qu’à ses demandes ; aucune action contributeur ne publie directement. | Tests de deux comptes distincts et mutations interdites. |
| AC-CONTRIB-04 | Les deux types gardent leurs champs, doublons et contrôles ; envoi valide crée une demande en attente. | Formulaire, service, base isolée et visibilité publique. |
| AC-CONTRIB-05 | Créateur proposé passe par un brouillon et publication distincte ; refus/complément ne publient rien. | Intégration de bout en bout, RM-TAL-006 et UX-PROP-004. |
| AC-CONTRIB-06 | Plusieurs corrections coexistent sans modifier la version publique avant acceptation. | Intégration SQLite et vérification publique. |
| AC-CONTRIB-07 | Modification intervenante bloque l’acceptation directe ; changement entre comparaison et écriture également détecté. | Tests de versions concurrentes et résolution humaine au navigateur. |
| AC-CONTRIB-08 | Acceptation conserve avant/après et décideur ; refus conserve la fiche publiée inchangée. | Transaction, historique et intégrité. |
| AC-CONTRIB-09 | Événements 8A créent les notifications destinées aux bons acteurs ; panne email ne perd ni demande ni décision. | Service avec transport email simulé, panne et réessai. |
| AC-CONTRIB-10 | Retours, erreurs et suivi restent utilisables au clavier et sur mobile. | Parcours navigateur, inspection visuelle PC/mobile. |

Traçabilité technique future : routes fines → services de comptes/contribution/
modération/notifications → repositories → SQLite, selon development/AGENTS.md.
Les fichiers précis et migrations seront proposés après inspection ciblée du code.
Réutiliser les contrôles existants des sites et l’authentification admin sans
déclarer les tests actuels suffisants pour les nouveaux droits contributeurs.

## Périmètre et questions restantes

- Retenu pour conception : inscription commune Site/Créateur, suivi, modération,
  corrections versionnées des créateurs, gestion des conflits et notifications.
- Non inclus : rôle Créateur vérifié, rôle Modérateur distinct, publication en
  lot, restauration d’une version, extension des corrections versionnées aux sites.
- Livraison ultérieure validée, hors première version. À décider : champs
  corrigeables (notamment portraits/liens/preuves privées), visibilité et durée
  de conservation de l’historique, retrait/reprise des demandes, traitement des
  anciennes propositions anonymes et accès à l’historique après fermeture d’un compte.
- À détailler techniquement : expiration des liens, limites de renvoi, protection
  des mots de passe, reprise de session, transport email et procédures d’exploitation.
- Documents métier à amender avant réalisation : RM-22/23/29 et RM-SITE-010
  décrivent encore l’authentification facultative ou l’email libre. Cette cible
  documentée remplacera ces points pour le futur parcours avec compte ; les critères de
  publication et coordonnées privées restent conservés. RM-59 est un journal
  d’actions, à distinguer de l’historique détaillé des versions ici retenu.

Publication multiple et rôle Modérateur ne sont pas intégrés implicitement.
Préproduction et CI sont des sujets distincts de cette conception fonctionnelle.

## Suivi

État courant du 23 octobre : conception détaillée de la variante mobile consignée
dans CONTRIBUTOR_DASHBOARD_MOBILE.md avant réalisation. La maquette interactive
locale est réalisée et traitée séparément du backend ; les preuves de contrôle
et captures sont consignées dans [la revue dédiée](../testing/CONTRIBUTOR_MOBILE_REVIEW_2026-10-23.md).
Aucune validation visuelle utilisateur n’est déduite de ces contrôles. Les mentions
de suivi ci-dessous décrivent la situation historique antérieure à cet amendement.

Décisions consignées et base de parcours/critères préparée ; aucune maquette ni
fonctionnalité modifiée. Les points ouverts sont explicites ; la conception
détaillée reste à relire. Pas de test métier, migration ni déploiement de ce lot.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.8 | 23 octobre 2026 | Révision UX-CDM-011 demandée après essai : titres, actions, statuts explicites, retrait compteurs et doublons ; processus conservés. |
| 0.7 | 23 octobre 2026 | Revue de la maquette mobile et captures reliées ; limites des simulations et validation visuelle attendue conservées. |
| 0.6 | 23 octobre 2026 | Maquette contributeur mobile et documentation des processus demandées ; choix détaillés sous délégation dans CONTRIBUTOR_DASHBOARD_MOBILE.md, lancement sans compte conservé, aucun backend autorisé. |
| 0.5 | 17 octobre 2026 | Retour aux créateurs de contenu ; tableau de bord toujours différé, aucun droit de propriétaire ajouté. |
| 0.4 | 16 octobre 2026 | Souhait du compte avec tableau de bord confirmé et différé ; Talents péi, droits de propriété ouverts, parcours Contact/email conservé au lancement. |
| 0.3 | 9 octobre 2026 | Clarification utilisateur : lancement public sans compte contributeur et admin ; évolution avec comptes différée, préparation de présentation ultérieure, aucune maquette demandée maintenant. |
| 0.2 | 9 octobre 2026 | 7A/8A/9A consignés ; parcours complet, notifications, conflits, critères et questions restantes préparés. |
| 0.1 | 9 octobre 2026 | Choix initiaux, comptes communs, vérification email, corrections concurrentes et inscription par lien consignés. |
