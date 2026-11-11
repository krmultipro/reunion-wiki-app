# Tableau de bord contributeur — maquette mobile

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.4 |
| Date | 23 octobre 2026 |
| Statut | Conception et choix de maquette délégués à l’agent ; appréciation visuelle utilisateur attendue |
| Périmètre autorisé | Documentation des processus et maquette mobile interactive isolée |
| Réalisation métier | Aucun compte, email, traitement administratif, changement de base ou publication réelle |
| Réalisation de la variante | Maquette locale interactive réalisée et contrôlée ; revue dédiée et captures disponibles, appréciation visuelle utilisateur attendue |
| Référence | [Contribution avec compte](CONTRIBUTOR_WORKFLOW.md), UX-CONTRIB-001 à 010 |

## Révision applicable — clarté du suivi, 23 octobre 2026

**UX-CDM-011 v1.0 — validée puis réalisation demandée.** Après essai, l’utilisateur
signale un temps de compréhension lié aux titres et à l’organisation. La
proposition explicite de simplification est acceptée par « Vas y modifie ».
Cette décision remplace la présentation initiale de UX-CDM-001, les libellés de
navigation de UX-CDM-006 et les libellés de résultat de UX-CDM-008 sur les seuls
points suivants ; les processus, statuts techniques et droits restent conservés.

- Entrée « Mon suivi » : expliquer immédiatement qu’il s’agit des propositions
  de sites, de personnalités et des corrections. L’accueil ne repose plus sur le
  seul message de bienvenue « Bonjour Camille ».
- Trois sections explicites : **À compléter**, **Mes brouillons**,
  **Dernières mises à jour**. Les boutons indiquent **Répondre**, **Continuer**
  ou **Voir le détail**. Toutes les demandes à compléter et tous les brouillons
  sont accessibles dans leurs sections ; les trois dernières autres demandes
  complètent la vue sans répéter celles déjà présentées.
- Supprimer les trois compteurs de l’accueil, dont « Abouties ». Le suivi complet
  et ses filtres restent accessibles par **Toutes mes demandes** et le dock
  **Mes demandes**, avec Proposer et Compte. Les fragments techniques ne changent pas.
- Identifier les cartes par **Proposition de site**, **Proposition de personnalité**
  ou **Correction d’une fiche**. Afficher **En attente de vérification**,
  **Fiche en préparation**, **Publiée** ou **Correction appliquée** selon le
  statut réel de la demande. Un envoi reçu n’est pas présenté comme un examen
  déjà commencé ; une fiche en préparation reste non publique.
- Conserver l’action **Faire une proposition**, la hiérarchie mobile, les couleurs,
  les brouillons et les données de l’onglet. Aucun changement du backend, des
  critères d’admission ou du lancement sans compte.

Le compromis accepté est d’employer des formulations plus explicites, parfois
plus longues. Les cartes doivent permettre leur retour à la ligne sur petit
écran. Les compteurs et titres initiaux restent décrits dans l’historique et la
revue initiale ; ils ne sont plus la présentation courante.

Critères de cette révision, définis avant modification : titres et dock conformes ;
aucun compteur sur Mon suivi ; aucune demande répétée entre ses sections ;
réponse à un complément retirée de À compléter puis retrouvée dans les mises à
jour ; accès/reprise des brouillons et filtres conservés ; états vides expliqués ;
libellés longs sans débordement à 320/390/430 px. La vérification technique et
l’appréciation visuelle de l’utilisateur seront distinguées dans la revue.

## Origine et portée

L’utilisateur demande une maquette du dashboard contributeur pour se projeter,
avec les processus documentés et uniquement une version mobile. Après les cinq
questions de présentation et de droits, il délègue les choix : « fais comme bon
te semble […] vas y bosse bien ». Les décisions ci-dessous sont donc des choix
de conception pris dans cette délégation, et non des réponses utilisateur
inventées `1A 2A 3A 4A 5A`. La maquette servira à les apprécier visuellement.

Le lancement sans compte reste inchangé. Cette variante décrit une évolution
ultérieure : elle ne remplace pas la proposition publique actuelle. Les choix
historiques et critères métier restent référencés dans CONTRIBUTOR_WORKFLOW et
[UNIFIED_SUBMISSION.md](UNIFIED_SUBMISSION.md). Le nom public courant est
« Personnalités » (UX-CONT-007), sans élargissement implicite de l’admissibilité.

Le document existant ne tranchait pas la disposition du dashboard, les brouillons,
l’annulation, la reprise d’un refus et les champs corrigibles. Ce document les
précise pour l’essai demandé. Aucun rôle propriétaire, privilège de publication,
portrait envoyé, statistiques personnelles, messagerie ou gestion d’équipe ajouté.

## Décisions de conception de la variante

| ID | Choix retenu et conséquence |
| --- | --- |
| UX-CDM-001 | Présentation initiale, remplacée sur titres et compteurs par UX-CDM-011 : dashboard centré sur les actions : demandes de complément d’abord, action de proposition et contributions récentes. Les compteurs secondaires ne remplacent pas les actions. |
| UX-CDM-002 | Brouillon enregistré manuellement dès qu’un titre/nom permet de le retrouver, sans exiger les autres champs ; reprise depuis le dashboard ou la liste. Une saisie non enregistrée provoque un avertissement avant abandon ; aucune promesse de sauvegarde automatique. |
| UX-CDM-003 | Après envoi, contenu consultable en lecture seule. Annulation possible avant décision, avec confirmation. La réponse à un complément est ajoutée à l’historique et retourne à l’examen. |
| UX-CDM-004 | Refus motivé conservé ; « Préparer une nouvelle version » crée un nouveau brouillon lié à la demande refusée. L’ancienne demande et sa décision restent intactes. |
| UX-CDM-005 | Correction d’une personnalité : nom, présentation et lien officiel, avec motif obligatoire et sources facultatives. Au moins un changement requis. Aucun remplacement de portrait ni correction versionnée des sites dans cette variante. |
| UX-CDM-006 | Navigation initiale Tableau de bord, Contributions, Proposer, Compte ; libellés remplacés par Mon suivi / Mes demandes selon UX-CDM-011. Un lien explicite permet de revenir au site public. La navigation publique existante reste la référence pour la consultation. |
| UX-CDM-007 | Suivi dans la liste et le détail, emails aux événements de UX-CONTRIB-009. Pas de nouvelle boîte de notifications ni de badge de messages non lus. |
| UX-CDM-008 | Liste personnelle filtrable, détails avec statut textuel, contenu envoyé, événements et prochaine action. « Publiée » pour une proposition et « Correction appliquée » pour une correction sont deux résultats distincts (libellé initial Acceptée remplacé par UX-CDM-011). |
| UX-CDM-009 | Maquette autonome dans `maquettes/contributeur-mobile/index.html`, routes par fragment. Palette crème/vert, typographies et composants issus des maquettes existantes, tutoiement selon le guide éditorial. |
| UX-CDM-010 | Données fictives et authentification simulée. Stockage de démonstration limité à l’onglet via `sessionStorage`, sans vrai mot de passe ni email conservé. Remise à zéro explicite. |

La solution privilégie des actions visibles avec peu de métriques : le
contributeur occasionnel cherche surtout où en est une demande et ce qu’il doit
faire. Le brouillon manuel évite de laisser croire à une synchronisation entre
appareils. Le contenu envoyé stable simplifie l’examen ; l’annulation et la
nouvelle version gardent une possibilité de correction sans effacer les décisions.

## Architecture des écrans et retours

Les routes ci-dessous sont des destinations logiques de la maquette, pas des
endpoints Flask ni un contrat d’URL de production.

| Écran | Contenu et actions | Retour attendu |
| --- | --- | --- |
| Mon suivi | À compléter, Mes brouillons, Dernières mises à jour sans répétition ; Faire une proposition et Toutes mes demandes ; aucun compteur | Dock privé ; retour site public |
| Toutes mes demandes | Filtres Tous/À compléter/En cours/Brouillons/Terminées ; types et statuts explicites | Détail puis même liste et filtre |
| Détail d’une contribution | Statut expliqué, contenu, historique privé, réponse ou action autorisée | Liste ou dashboard d’origine |
| Choix de proposition | Site, Personnalité ; rappel de modération ; correction d’une fiche existante | Tableau de bord ou liste |
| Formulaire site | Nom, URL, description et catégorie requis ; brouillon, vérification, envoi | Origine conservée ; avertir si saisie non enregistrée |
| Formulaire personnalité | Nom et lien officiel requis ; description, catégorie et lien réunionnais facultatifs | Même règle de retour |
| Correction d’une personnalité | Fiche de référence, valeurs actuelles/proposées par champ, motif, sources | Détail de référence ou liste |
| Confirmation | Réception simulée, attente de vérification, détail et liste | Aucune publication promise |
| Réponse au complément | Question administrative visible, réponse requise, sources facultatives | Demande retournée en attente |
| Compte | Identité fictive, email vérifié fictif, principes de confidentialité, déconnexion | Accès au compte demandé au prochain écran privé |
| Connexion/inscription | Email puis lien de vérification ; accès démo ; destination demandée conservée | Destination privée après accès simulé |
| Email/activation | Aperçu du message, lien actif/expiré/utilisé, création de mot de passe simulée | Reprise de destination ou demande d’un nouveau lien |
| Récupération | Demande générique, aperçu de lien, nouveau mot de passe simulé | Connexion puis destination |
| Outils de démonstration | Choix des scénarios, événements administratifs simulés, erreurs, reset | Hors interface produit, libellé explicite |

Une interface étroite reste centrée dans une grande fenêtre : aucun dashboard
ordinateur distinct n’est conçu. Prévoir 320, 390 et 430 px de largeur, cibles
tactiles d’environ 44 px, dock dégagé du contenu et des zones sûres, titres et
statuts lisibles sans dépendre de la couleur, labels et focus visibles. Les
comparaisons de correction s’empilent par champ ; aucun tableau large imposé.

La variante démarre connectée avec Camille et ses contributions fictives pour
montrer immédiatement le dashboard. Le lien « Retour au site » rejoint
`../accueil-categories-mobile.html`, variante publique existante ; les parcours
d’accès restent rejouables depuis Compte et les outils de démonstration.
Présentation courante UX-CDM-011 : aucun compteur sur Mon suivi. Le suivi
complet reste accessible dans Toutes mes demandes ; « En cours » regroupe attente,
complément et préparation, avec un filtre dédié aux compléments. « Terminées »
inclut publiées, corrections appliquées, refusées et annulées. L’ancien compteur
Abouties (propositions publiées et corrections acceptées) est retiré de l’interface ;
les anciennes URL de filtre restent compatibles pour préserver les liens.

Les fragments réellement retenus pour la variante sont :

| Fragments | Écran |
| --- | --- |
| `#/dashboard`, `#/contributions` | Tableau de bord et liste filtrable |
| `#/proposer`, `#/nouveau?type=site`, `#/nouveau?type=personnalite` | Choix et nouvelle proposition |
| `#/editer/id`, `#/detail/id`, `#/confirmation/id` | Reprise d’un brouillon, suivi et confirmation |
| `#/corriger`, `#/fiche/id` | Correction et fiche publique simulée |
| `#/compte`, `#/connexion`, `#/inscription`, `#/email` | Compte, accès et aperçu d’email |
| `#/activation`, `#/activation?etat=expire`, `#/activation?etat=utilise` | Activation valide, expirée ou déjà utilisée |
| `#/recuperation`, `#/erreur` | Récupération et erreur illustrée |

`id` désigne l’identifiant fictif d’une contribution. Ces fragments ne créent
aucune route publique ou privée de production.

## Parcours visiteur et accès au compte

1. La consultation du site public ne demande pas de compte. Dans la cible future,
   « Proposer » ou « Corriger » mène à l’accès au compte avant le formulaire
   (UX-CONTRIB-008). La démo démarre connectée pour montrer le dashboard.
2. Inscription : saisir l’email → message générique de demande reçue → email
   avec lien → choisir le mot de passe après validation du lien → compte actif,
   email vérifié → destination initiale. Aucun contenu anonyme n’a été commencé.
3. Lien expiré ou déjà utilisé : aucun accès accordé ; expliquer le problème et
   permettre de demander un nouveau lien. Le renvoi ne confirme pas l’existence
   d’un compte et n’annonce pas une réception effective de l’email.
4. Compte actif : connexion email/mot de passe. Mot de passe oublié : demande
   générique → email de récupération → lien valide → choix d’un nouveau mot de
   passe → connexion. Inscription en attente et compte actif restent distincts.
5. Déconnexion volontaire : avertissement si des changements ne sont pas
   enregistrés, puis effacement de la session de démonstration et de la rédaction,
   avec remise des exemples à leur état initial explicitement annoncée.
   Écran public/d’accès. Historique navigateur et accès direct à
   un fragment privé doivent repasser par l’écran d’accès dans la simulation.

Les champs de mot de passe de la démo sont illustratifs : utiliser des valeurs
fictives uniquement, ne jamais les enregistrer dans `sessionStorage`, les logs
ou les fixtures. Aucun email n’est envoyé, aucun jeton ne sécurise un compte.
L’aperçu d’email est une explication du parcours, pas une preuve d’envoi réel.

## Parcours de proposition

1. Contributeur actif → choisir Site ou Personnalité. Le compte fournit l’identité
   d’envoi ; aucune nouvelle adresse email libre à attribuer à la demande.
2. Remplir les champs du type. Enregistrer un brouillon exige au minimum un nom
   pour le retrouver, autorise les autres informations manquantes et produit un
   retour explicite « Brouillon enregistré » ; l’envoi
   exige tous les champs requis selon UX-PROP-002 et RM-SITE-010.
3. Reprendre un brouillon depuis le dashboard ou la liste. Avant de quitter une
   saisie modifiée, proposer de rester ou d’abandonner les changements non
   enregistrés. Le dernier brouillon enregistré reste la référence récupérable.
4. Vérification finale → envoyer → confirmation → détail en attente. Le détail
   devient en lecture seule et garde le contenu effectivement envoyé.
5. Administration future : contrôle d’admissibilité, liens et doublons → demande
   de complément ou refus motivé ou préparation d’une fiche. Une proposition
   de personnalité ne devient pas une fiche publique lors de sa réception ni
   lors de la création d’un brouillon administratif (RM-TAL-006, UX-PROP-004).
   Lorsque la proposition est retenue, le suivi passe par « En préparation » :
   la décision positive est prise, mais la publication distincte reste à faire.
   Le contributeur ne peut plus annuler cette demande.
6. La publication administrative distincte produit le résultat « Publiée »,
   avec lien public seulement si une fiche publique existe réellement. La démo
   affiche un aperçu fictif clairement identifié dans son propre dossier, sans
   inventer une fiche réelle ni relier un exemple à une personnalité réelle.

Doublon public : signaler la fiche existante et proposer sa consultation ou une
correction. Doublon non public : « Ce profil est déjà enregistré », sans exposer
statut, motif, données privées ni lien (UX-PROP-009). Les jeux de doublons de la
maquette sont des scénarios illustratifs ; aucun contrôle global de base n’existe.
Le doublon de démonstration repose sur l’URL exacte
`https://example.org/deja-reference`, avec scénarios public/non public distincts.

## Complément, annulation et refus

Le complément demandé apparaît en priorité sur le dashboard et dans le détail,
avec la question et la date. « Répondre » ouvre une réponse distincte ; elle ne
réécrit pas le contenu initial. Après envoi, réponse horodatée et retour en
attente, sans publication et sans email à chaque étape administrative interne.

« Annuler ma demande » est disponible en attente et en complément. Confirmation :
« Annuler cette demande ? Elle ne sera plus examinée. Son historique restera
dans tes contributions. » Retour possible sans effet. Après confirmation, statut
Annulée, contenu et historique conservés, aucune publication. Avant une future
écriture serveur, vérifier de nouveau l’état : une décision administrative déjà
prise interdit une annulation tardive et doit être expliquée au contributeur.

Un refus affiche le motif et la date avec une action de nouvelle version.
Le brouillon issu du refus copie les informations utiles et porte le lien vers
la demande d’origine. Après nouvel envoi, il possède sa propre demande et son
propre historique ; il ne change ni le refus ni son motif. Une annulation ne
retire pas une fiche déjà publiée ; les demandes de retrait restent le parcours
Contact/email applicable tant qu’une nouvelle décision n’en dispose pas.

## Corrections et historique privé

1. Choisir une personnalité existante dans le scénario ou entrer par son action
   de correction. Afficher la fiche de référence et les valeurs actuelles.
2. Proposer au moins un changement de nom, présentation ou lien officiel ; motif
   requis, sources facultatives. Ne pas présenter une source facultative comme
   une dispense de vérification éditoriale. Aucun upload de portrait.
3. Brouillon puis envoi : la fiche publique reste inchangée. Le détail conserve
   la version de référence, les changements proposés et le motif.
4. Administration future : comparer référence, proposition et fiche actuelle.
   Plusieurs corrections peuvent coexister (UX-CONTRIB-005). Si la fiche a changé,
   bloquer l’acceptation directe ; comparaison et résolution explicites, puis
   nouveau contrôle de version à l’écriture (UX-CONTRIB-010).
5. Acceptation d’une correction : appliquer les changements retenus avec
   historique avant/après et décideur. Statut technique `acceptee`, affiché « Correction appliquée », message de correction
   appliquée ; ce résultat n’est pas le statut « Publiée » d’une proposition.
   Refus et complément laissent la fiche publique inchangée.

La maquette ne contient pas d’écran de modération ni de résolution des conflits.
Les outils de démonstration peuvent jouer ces événements pour montrer le suivi
côté contributeur. Aucun bouton « Publier » ni « Accepter » n’est une action
produit du contributeur.

Chaque compte ne consulte que ses demandes et leurs échanges. Emails, brouillons,
motifs de refus, réponses et historique de modération restent privés. Une fiche
publique n’expose pas cet historique. La démo illustre cette frontière avec une
seule identité fictive ; elle ne prouve pas une isolation entre comptes réels.
La visibilité détaillée des identités administratives et la politique de
conservation/fermeture de compte restent à arrêter avant backend.

## États et transitions

Ces états concernent la demande ; ils ne remplacent pas les statuts des fiches.

| État technique de démo | Libellé | Actions contributeur | Transitions autorisées |
| --- | --- | --- | --- |
| `brouillon` | Brouillon | Modifier, enregistrer, envoyer | `en_attente` après validation et envoi |
| `en_attente` | En attente de vérification | Consulter, annuler après confirmation | `complement`, `preparation` (proposition retenue), `acceptee` (correction), `refuse` via admin ; `annule` via contributeur |
| `complement` | À compléter | Consulter, répondre, annuler après confirmation | `en_attente` après réponse ; `annule` via contributeur |
| `preparation` | Fiche en préparation | Consulter ; aucune annulation après décision positive | `publie` par publication administrative distincte |
| `publie` | Publiée | Consulter le résultat et l’historique | Terminal pour la demande initiale ; toute correction crée une autre demande |
| `acceptee` | Correction appliquée | Consulter les changements et l’historique | Terminal, réservé à une correction appliquée |
| `refuse` | Refusée | Consulter le motif, préparer une nouvelle version | Terminal ; nouvelle version = autre `brouillon` lié |
| `annule` | Annulée | Consulter l’historique | Terminal |

Une erreur technique ne constitue pas un statut métier. Un double clic ne crée
pas deux demandes ; un réessai futur doit retrouver l’issue d’un envoi incertain.
Aucune transition ne supprime silencieusement le contenu ni les événements.

## Notifications et états dégradés

| Événement | Attendu dans le produit futur | Démonstration |
| --- | --- | --- |
| Proposition/correction reçue | Email admin et contributeur ; suivi visible | Confirmation et historique fictifs |
| Complément demandé | Email contributeur avec accès authentifié à la demande | Action à traiter et question dans le détail |
| Décision de modération | Email contributeur et état du suivi actualisé | Résultat simulé et historique |
| Panne email | Demande/décision conservée, tentatives bornées et suivi technique | Message explicatif, aucune affirmation de livraison |

Un email accepté par le transport ne prouve pas sa réception ; une notification
ne donne aucun droit d’accès ou de modération. La fiabilité technique future
reste décrite dans CONTRIBUTOR_WORKFLOW ; la démo ne réalise ni file ni réessai.

Prévoir les états vides (aucune contribution, aucun résultat pour un filtre),
les erreurs de champ avec valeurs conservées, la demande introuvable et la
session expirée. En cas d’expiration pendant une saisie, demander connexion puis
reprendre la rédaction restée en mémoire dans la même page pour le même compte
fictif. Un rechargement perd les changements non enregistrés et permet seulement
de retrouver le dernier brouillon enregistré ; la différence doit être annoncée.
Ne jamais annoncer une reprise intégrale qui n’a pas été réalisée. Le produit
futur doit définir sa conservation privée avant de promettre cette reprise.

Si une écriture `sessionStorage` échoue, afficher que l’enregistrement de
démonstration est indisponible, bloquer l’enregistrement et proposer de réessayer. Ne pas
afficher « enregistré » après échec. Le reset exige un avertissement et restaure
les données fictives. La fermeture de l’onglet peut perdre la démo ; ce stockage
n’est ni une base active, ni une sauvegarde, ni une stratégie de production.

## Séparation lancement, évolution et questions techniques

| Périmètre | État |
| --- | --- |
| Lancement sans compte, modération administrative, correction/retrait par Contact/email | Décisions existantes maintenues |
| Dashboard, compte vérifié, brouillons, suivi, corrections et notifications | Conception future mise en scène en maquette mobile |
| Backend, base, emails réels, sessions et protection des données | Hors réalisation demandée ; conception technique préalable requise |
| Portraits, rôle propriétaire/modérateur, revendication, historique public, corrections versionnées des sites | Non inclus ou à décider séparément |

Avant réalisation serveur : définir durée et usage unique des jetons, limitations
de renvoi/connexion, récupération des comptes, hachage des mots de passe, session
et reprise de brouillons, versionnement/concurrence, idempotence, transport email,
politique de conservation et fermeture de compte. Ce sont des points techniques
ouverts, pas des valeurs implicites validées par la maquette. Prévoir source
active, sauvegardes indépendantes et restauration testée avant données réelles.

Les écarts RM-22/23/29 et RM-SITE-010 relatifs à l’email/authentification facultatifs
restent à amender lors de l’adoption de l’évolution ; la présente maquette ne
change pas leurs effets au lancement. Ne pas modifier les critères métier pour
les faire coïncider avec les seules possibilités du prototype.

## Acceptation et traçabilité prévue

Les critères ci-dessous sont définis avant réalisation. Leur état initial est
« prévu » ; aucun contrôle n’est déclaré exécuté par ce document initial.

| ID | Critère observable | Sources et écrans | Contrôle prévu |
| --- | --- | --- | --- |
| AC-CDM-01 | Dashboard expose les compléments avant les récents et permet de proposer. | UX-CDM-001, dashboard | Inspection mobile et clics |
| AC-CDM-02 | Dock et retours couvrent les quatre rubriques sans perdre filtre/origine. | UX-CDM-006, liste/détail | Parcours de navigation et historique navigateur |
| AC-CDM-03 | Brouillon incomplet enregistré, repris ; abandon non enregistré averti. | UX-CDM-002, formulaires | Saisie, navigation, rechargement du même onglet |
| AC-CDM-04 | Champs requis selon le type ; erreur conserve les autres valeurs ; envoi crée une seule demande en attente. | UX-PROP-002, AC-CONTRIB-04, formulaires | Envois invalides/valides Site et Personnalité, double clic |
| AC-CDM-05 | Demande envoyée en lecture seule ; complément ajouté sans réécrire l’envoi ; annulation confirmée. | UX-CDM-003, détail/réponse | Complément et annulation ; retour sans confirmer |
| AC-CDM-06 | Nouvelle version d’un refus liée, avec décision initiale intacte. | UX-CDM-004, détail/formulaire | Refus → brouillon → nouvel envoi |
| AC-CDM-07 | Correction change au moins un champ avec motif, aucun portrait ; Correction appliquée distincte de Publiée. | UX-CDM-005/008, AC-CONTRIB-06/08 | Formulaire correction, états de résultats |
| AC-CDM-08 | Accès, activation, expiration, renvoi et récupération présentés comme simulations ; destination reprise. | UX-CONTRIB-004/007/008, accès/compte | Parcours déconnexion, accès direct, activation et récupération |
| AC-CDM-09 | Aucune action produit contributeur ne publie ; proposition retenue En préparation avant publication séparée, sans annulation ; événements admin uniquement dans outils démo identifiés. | AC-CONTRIB-03/05, détail/outils | Inspection actions et transitions |
| AC-CDM-10 | Filtres sans résultat, compte vide, demande absente, session/stockage en échec expliqués. | AC-CONTRIB-10, scénarios | Scénarios dédiés et réessai |
| AC-CDM-11 | Pas de débordement à 320/390/430 px ; dock ne masque pas les actions ; clavier/focus/labels utilisables. | AC-CONTRIB-10, tous écrans | Mesures navigateur, captures et navigation clavier |
| AC-CDM-12 | Fixtures fictives, reset explicite, aucun secret conservé ; email et états clairement simulés. | UX-CDM-010, compte/outils | Inspection code/stockage, reset et rechargement |
| AC-CDM-13 | Mon suivi présente trois sections explicites, aucun compteur et aucune demande répétée ; réponse reçue déplacée dans les mises à jour. | UX-CDM-011, dashboard | Comparer les identifiants, réponse et retour au suivi, plusieurs brouillons et états vides |
| AC-CDM-14 | Types complets et statuts explicites lisibles sur 320/390/430 px, Mes demandes accessible avec filtres et retours. | UX-CDM-011, liste/détail/dock | Mesures et captures mobile, reprise d’un brouillon depuis une liste filtrée |

Ces contrôles de maquette ne valident ni les permissions Flask, ni l’isolation
réelle de deux comptes, les transactions, conflits concurrents, emails ou
sauvegardes. AC-CONTRIB-01 à 10 conservent leurs futurs tests métier/intégration.
Les preuves effectivement obtenues doivent être ajoutées dans une revue dédiée,
avec commandes, environnement, captures et limites ; la validation esthétique
utilisateur reste distincte de la vérification technique.

## Réalisation et preuves — 23 octobre 2026

La variante est disponible dans `maquettes/contributeur-mobile/index.html` et
liée au comparateur « Mobile · Contributeur ». Formulaires, brouillons, réponses,
annulation, nouvelle version après refus, corrections, accès au compte et
événements administratifs sont simulés. Le statut En préparation précède la
publication distincte ; Correction appliquée (`acceptee`) reste propre aux corrections.

La révision UX-CDM-011 est réalisée : Mon suivi sans compteurs, sections explicites sans demandes répétées, Toutes mes demandes accessible dans le dock et libellés détaillés. Les données et fragments existants restent compatibles.

Les contrôles et captures réellement obtenus figurent dans la
[revue dédiée](../testing/CONTRIBUTOR_MOBILE_REVIEW_2026-10-23.md), avec résultat
par critère et limites. Rendu dashboard/liste/complément observé à trois largeurs,
parcours de création/suivi/compte testés au navigateur et revue indépendante des
points corrigés. Cette vérification technique ne constitue pas une adoption
visuelle utilisateur ni une validation du backend. Livraison locale, sans
modification des règles de lancement et sans finalisation Git de ce lot.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.4 | 23 octobre 2026 | Révision de clarté UX-CDM-011 validée après retour utilisateur ; décisions et critères consignés avant modification. |
| 0.3 | 23 octobre 2026 | Réalisation et revue navigateur reliées, captures conservées, limites explicites ; validation visuelle utilisateur attendue. |
| 0.2 | 23 octobre 2026 | État de maquette locale consigné sans présumer les contrôles ; fragments, préparation avant publication, compteur Abouties, erreurs de stockage et reset à la déconnexion précisés. |
| 0.1 | 23 octobre 2026 | Processus et choix de la variante mobile documentés sous délégation utilisateur avant réalisation ; critères prévus, backend hors périmètre. |
