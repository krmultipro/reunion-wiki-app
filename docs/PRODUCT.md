# Produit — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.1 |
| Statut | Brouillon |
| Dernière mise à jour | 2 septembre 2026 |

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

### Annuaire des sites réunionnais

- afficher les sites par catégorie ;
- rechercher des sites ;
- afficher les tendances à partir des clics ;
- afficher les derniers sites ajoutés ;
- associer une commune à un site lorsque cela est pertinent ;
- permettre à un visiteur de proposer un site ;
- administrer les sites, catégories, villes et propositions.

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

Avant de considérer le parcours prêt, une vraie fiche pilote doit être traitée
de bout en bout :

1. recueillir les informations et les liens du talent ;
2. vérifier son lien avec La Réunion ;
3. enregistrer et afficher au moins une source pertinente ;
4. documenter la provenance de l'image et conserver l'autorisation ;
5. rédiger une présentation neutre ;
6. enregistrer la fiche en brouillon ;
7. relire et corriger la fiche ;
8. publier la fiche ;
9. vérifier son affichage sur mobile et ordinateur ainsi que tous ses liens ;
10. vérifier qu'elle peut ensuite être corrigée ou archivée.

Cette fiche pilote est un test grandeur nature du parcours, pas une nouvelle
fonctionnalité.

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
| 0.1 | 2 septembre 2026 | Brouillon | Création du cahier des charges Docs as Code et définition du parcours pilote des talents. |
