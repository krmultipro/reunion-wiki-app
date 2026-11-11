# Produit — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.15 |
| Statut | Brouillon |
| Dernière mise à jour | 11 novembre 2026 |

## Jalon refonte DEV — décision du 11 novembre 2026

La maquette mobile-final et son repli ordinateur sont la cible d’une refonte.
L’utilisateur autorise son implémentation, ses tests, puis sa livraison DEV via
une branche dédiée fusionnée dans `dev`. La production et `main` sont hors de
cette livraison. Les sources privées ne sont pas importées.

L’utilisateur accepte de reporter après cette intégration les compléments de
recherche avancée, les filtres plateforme/Twitch, les outils admin avancés,
la nouvelle présentation du projet/articles et la finalisation des informations
de confidentialité. Cette dernière reste préalable à l’ouverture publique et
à la collecte réelle ; la protection effective du non-public est immédiate.
Les exigences historiques sont conservées, avec un report explicite pour ce
jalon et non une suppression. Voir [REFONTE_DEV](ux/REFONTE_DEV.md) pour les
parcours essentiels et critères d’acceptation validés avant réalisation.

Historique 0.15 — 11 novembre : refonte DEV simplifiée autorisée, reports
fonctionnels et chaîne branche dédiée → dev → publication DEV consignés.

## Révision de l’accueil — choix validés le 17 octobre 2026

Après essai utilisateur, retirer les blocs globaux Plus consultés et Derniers
sites ajoutés de l’accueil, sur mobile et ordinateur. La sélection des trois
derniers créateurs publiés devient un carrousel manuel seulement sur l’accueil
mobile, avec une partie de la carte suivante visible. Grille ordinateur,
liste Créateurs, recherche et aperçus de catégories conservés.

Tendances hors expérience publique cible : aucun lien de maquette ; retrait
effectif de l’accès direct Flask et cohérence SEO à traiter lors de #18.
Clics et statistiques privées admin conservés. Voir [HOME_PAGE.md](ux/HOME_PAGE.md)
pour décisions et critères préparés. Révision de maquette seulement ; aucun
backend ni déploiement réalisé par la validation de ces choix.

## Décision applicable — créateurs de contenu, 17 octobre 2026

Le [périmètre de lancement](ux/CONTENT_CREATORS_SCOPE.md) remplace l’ouverture générale aux
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

## Historique — décision Talents péi du 16 octobre 2026, remplacée sur le périmètre

La rubrique cible devient **Talents péi** : personnes et collectifs, activités,
créations et savoir-faire, y compris créateurs de contenu, artistes et artisans.
Les fiches d’entreprises et les fonctions d’annuaire de prestataires ne font
pas partie de cette rubrique au lancement ; l’annuaire des sites est inchangé.
Proposer son profil ou celui d’un tiers reste possible sans compte et soumis à
modération. Compte avec tableau de bord confirmé pour plus tard, sans propriété
ni publication directe automatiques. Corrections par Contact/email au lancement.

La [fiche de périmètre](ux/TALENTS_PEI_SCOPE.md) fait référence pour les libellés,
les critères, les exemples à préparer et les points ouverts : lien officiel
obligatoire à la proposition, structures existantes et droits du tableau de bord.
Décision validée ; aucune adaptation de maquette, de code ou de données réalisée.
Les mentions génériques de créateurs ci-dessous conservent leur contexte historique.

## Vision

Réunion Wiki est un portail éditorial permettant de découvrir les sites,
ressources numériques et talents ayant un lien réel avec La Réunion.

Le service se distingue d'un annuaire publicitaire : la présence d'un site ou
d'un talent repose sur des critères éditoriaux et non sur l'achat de visibilité.

## Public concerné

- habitants de La Réunion ;
- visiteurs recherchant des ressources locales ;
- créateurs et talents liés à La Réunion ;
- responsables de sites, associations, entreprises et médias locaux.

## Périmètre fonctionnel

Les mentions historiques de tendances et derniers sites dans la liste ci-dessous
ne valent plus exigence d’affichage sur l’accueil. La révision du 17 octobre en
tête fait référence : tendances hors expérience publique cible, deux blocs
supprimés de l’accueil, calculs privés et dates conservés. Le backend réel reste
à aligner dans #18.


### Annuaire des sites réunionnais

- afficher les sites par catégorie ;
- rechercher des sites ;
- afficher les tendances à partir des clics ;
- afficher les derniers sites ajoutés ;
- associer une commune à un site lorsque cela est pertinent ;
- permettre à un visiteur de proposer un site ;
- administrer les sites, catégories, villes et propositions.

### Recherche commune depuis l’accueil — complément validé le 7 octobre 2026

Le champ principal de l'accueil recherche les sites, les catégories de sites et
les créateurs. Les résultats sont séparés par type avec leurs nombres ; seules les sections
ayant des résultats apparaissent. Un état global est affiché si tout est vide. Un clic sur une catégorie ouvre sa liste complète. Les règles
des recherches dédiées restent applicables. Le complément de simplification
1A retire les liens Affiner par section ; la page commune reste centrée sur
les accès directs aux résultats, sans panneaux de filtres. Ce choix remplace
le 3A précédent, conservé dans `ux/HOME_SEARCH.md`.

Ce complément remplace le périmètre antérieur de l'accueil limité aux sites et
catégories. Il constitue une décision de conception validée, réalisée en maquette locale
interactive le 7 octobre selon `ux/HOME_SEARCH.md`. Aucune intégration Flask,
migration ou mise en production n’est déclarée. Le reste du cahier des charges demeure brouillon.

### Information et contenu

- présenter le projet ;
- publier des contenus éditoriaux ;
- répondre aux questions fréquentes ;
- permettre de contacter l'éditeur ;
- afficher les informations légales nécessaires.

### Talents péi

- publier des fiches de talents connus ou émergents ;
- accepter les talents actuellement actifs, inactifs ou historiques ;
- classer les talents par catégorie ;
- relier une fiche aux plateformes et sources disponibles ;
- administrer, corriger, publier et archiver les fiches.

Les conditions précises d'admissibilité sont définies dans
[`BUSINESS_RULES.md`](BUSINESS_RULES.md).

## Critère de mise en production des fiches talents

### Complément validé — propositions publiques, 6 octobre 2026

Une page « Proposer » commune aux sites et créateurs fait partie de la première
version du parcours de contribution. Elle fonctionne sans compte, sans envoi
de photo et sans notification automatique. Les propositions sont modérées
avant publication. Les sept choix validés et les questions encore ouvertes sont
consignés dans [`ux/UNIFIED_SUBMISSION.md`](ux/UNIFIED_SUBMISSION.md).
Ce complément est validé ; le statut brouillon du reste du document reste
inchangé. Le parcours ci-dessous demeure obligatoire pour les fiches talents.

### Extension de contribution — conception validée le 9 octobre 2026

Les choix de conception sont étendus : compte contributeur avec email vérifié
obligatoire pour proposer Site/Créateur, inscription email → lien → mot de passe,
connexion avant formulaire, corrections de créateurs proposées par tout
contributeur et validées par l’admin, historique des versions, corrections
concurrentes avec résolution explicite et notifications de suivi.
Cette cible est réservée à une évolution ultérieure. Clarification utilisateur
du 9 octobre : la première version conserve le public sans compte contributeur
et l’administration authentifiée. Le complément du 6 octobre sur l’envoi sans
compte et sans notification automatique reste applicable au lancement.
Il sera remplacé sur ces points lors de l’évolution avec comptes ; aucun rôle
Créateur propriétaire n’est ajouté.
Parcours, critères proposés et questions restantes :
[`ux/CONTRIBUTOR_WORKFLOW.md`](ux/CONTRIBUTOR_WORKFLOW.md).
Évolution différée, hors lancement ; aucune implémentation ni publication
autorisée par ces choix de conception. Les critères de publication restent requis.

Avant de considérer le parcours prêt, une vraie fiche pilote doit être traitée
de bout en bout :

1. choisir un proche créateur ou influenceur disponible pour relire sa fiche ;
2. recueillir les informations et les liens du talent ;
3. vérifier un ou plusieurs rattachements avec La Réunion ;
4. enregistrer une source simple et pertinente en privé selon RM-TAL-003 v2.0
   (décision de lancement du 7 octobre 2026 remplaçant l’affichage public obligatoire) ;
5. si un portrait spécifique est utilisé, vérifier manuellement sa provenance et
   ses droits ; sinon utiliser l'image générique ;
6. rédiger une présentation neutre ;
7. enregistrer obligatoirement la fiche en brouillon ;
8. relire et corriger la fiche ;
9. publier la fiche au moyen d'une action distincte ;
10. vérifier son affichage sur mobile et ordinateur ainsi que tous ses liens ;
11. vérifier qu'elle peut ensuite être corrigée ou archivée ;
12. confirmer que tout le parcours fonctionne sans modification manuelle de la
    base de données ;
13. faire valider le contenu affiché par le talent et conserver ses remarques
    dans des notes d'amélioration.

Cette fiche pilote est un test grandeur nature du parcours, pas une nouvelle
fonctionnalité.

## Complément validé — source privée des créateurs au lancement

Décision 2A du 7 octobre 2026 : lien réunionnais vérifié par l'administrateur
avec une source simple conservée en privé, sans rubrique Sources publique.
Une bio officielle ou déclaration publique pertinente peut suffire ; aucun
article de presse systématique n'est exigé. Ce choix remplace RM-TAL-003 v1.0
et son amendement d'affichage, conservés dans BUSINESS_RULES.md ; version 2.0
et RM-31 font référence. Maquette/admin/backend non modifiés par cette décision.

## Gestion des versions

- `0.x` : cahier des charges encore en construction ;
- `1.0` : périmètre de la première version validé ;
- `1.x` : précisions ou ajouts compatibles avec la version 1 ;
- `2.0` : changement important de périmètre ou d'orientation.

Une version publiée n'est pas effacée silencieusement. Toute évolution est
inscrite dans l'historique ci-dessous et les changements structurants font
l'objet d'un ADR.

## Historique

| Version | Date | Statut | Modification |
| --- | --- | --- | --- |
| 0.13 | 17 octobre 2026 | Brouillon avec complément validé | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.12 | 16 octobre 2026 | Brouillon avec complément validé | Conception Talents péi, activités et savoir-faire ; entreprises hors rubrique au lancement, tableau de bord différé ; aucune réalisation. |
| 0.11 | 9 octobre 2026 | Brouillon avec compléments validés | Clarification : lancement public sans compte contributeur avec admin ; conception des comptes, corrections et notifications conservée pour une évolution ultérieure. |
| 0.10 | 9 octobre 2026 | Brouillon avec compléments validés | Extension de conception : comptes contributeurs Site/Créateur, corrections modérées versionnées et notifications ; parcours et critères préparés, réalisation non autorisée. |
| 0.9 | 7 octobre 2026 | Brouillon avec compléments validés | Source privée au lancement (2A), vérification légère conservée, étape du pilote alignée sur RM-TAL-003 v2.0 ; aucun code changé. |
| 0.8 | 7 octobre 2026 | Brouillon avec compléments validés | Allègement recherche : sections vides masquées, présentation compacte et bloc de proposition citron conservé ; HOME_SEARCH.md fait référence. |
| 0.7 | 7 octobre 2026 | Brouillon avec compléments validés | Simplification 1A : liens Affiner retirés de la recherche commune, accès directs conservés ; ancien 3A remplacé. |
| 0.6 | 7 octobre 2026 | Brouillon avec compléments validés | Recherche commune réalisée et contrôlée en maquette locale ; backend non intégré. |
| 0.5 | 7 octobre 2026 | Brouillon avec compléments validés | Recherche commune : accès aux filtres dédié par type avec texte conservé (3A), conception prête pour maquette. |
| 0.4 | 7 octobre 2026 | Brouillon avec compléments validés | Recherche accueil commune sites/catégories/créateurs et trois sections validées ; accès aux filtres ouvert, aucune réalisation. |
| 0.3 | 6 octobre 2026 | Brouillon avec complément validé | Page de proposition commune sites/créateurs : sept choix validés, modalités restantes suivies séparément. Aucune réalisation déclarée. |
| 0.2 | 15 septembre 2026 | Brouillon | Précision du parcours pilote talents, du brouillon obligatoire, de la validation par le talent et du recours possible à l'image générique. |
| 0.1 | 2 septembre 2026 | Brouillon | Création du cahier des charges Docs as Code et définition du parcours pilote des talents. |

## Trace de révision — 17 octobre 2026

Version 0.14 : retour utilisateur et choix de carrousel/réduction accueil consignés ; ancienne décision conservée.
