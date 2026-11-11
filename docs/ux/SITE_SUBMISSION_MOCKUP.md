# Proposition de site — premier jet de maquette

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.2 |
| Statut | Proposition visuelle à valider ; maquette locale uniquement |
| Date | 6 octobre 2026 |

## Évolution vers une proposition commune

Le premier jet site ci-dessous est conservé comme historique. La maquette a
été adaptée aux sites et créateurs selon les dix choix validés ; son état et
les contrôles actuels figurent dans [UNIFIED_SUBMISSION.md](UNIFIED_SUBMISSION.md).
Le backend reste inchangé.

## Périmètre et critères du premier jet

Premier jet du parcours visiteur : accueil → formulaire → erreurs/correction →
confirmation → accueil ou nouvelle proposition. Aucun envoi, stockage ou
changement du backend. Le parcours admin reste celui de `RM-SITE-010` ; sa
maquette ne fait pas partie de cette demande.

- `RM-SITE-010` : nom, lien, catégorie et description obligatoires ; localisation,
  justification, preuve et email facultatifs. Ne pas bloquer une proposition
  lorsque les champs facultatifs sont vides.
- `UX-GEN-004` : erreurs près des champs, saisie conservée après une erreur.
- `UX-SUBMIT-002` : confirmation dédiée, modération annoncée, retour à l'accueil
  et nouvelle proposition.
- `UX-GEN-005` : avertissement du navigateur pour une saisie modifiée non envoyée.

Choix proposés : formulaire sur une page dédiée ; informations facultatives
regroupées dans un volet ; localisation dans un seul sélecteur pour éviter le
choix simultané d'une commune et d'une portée. Catégories et communes sont des
exemples statiques, à remplacer par le référentiel réel lors de l'intégration.

## Fichiers et accès

- `maquettes/proposer.html`, `proposer.css`, `proposer.js` : formulaire et
  validation de démonstration ; `?etat=erreur` présente une URL invalide.
- `maquettes/proposition-confirmee.html` : confirmation simulée.
- `maquettes/accueil.html` : navigation « Proposer » et appel en bas de page
  reliés au formulaire local.

## Contrôles réalisés et limites

Le 6 octobre 2026, vérification dans le navigateur local :

- rendu visuel du formulaire à la largeur du panneau ;
- à 390 × 844, envoi vide : erreurs sur les quatre champs obligatoires ;
- saisie des quatre champs puis envoi simulé avec les facultatifs vides :
  navigation vers la confirmation ; rendu mobile de celle-ci observé ;
- retour « Proposer un autre site » demandé ; le contrôle suivant sur ordinateur
  a expiré et le rendu desktop reste à vérifier.

Ce contrôle ne valide pas le parcours de production. Les écarts du backend
restent ouverts : champs facultatifs absents, confirmation dédiée à intégrer,
liens publics vers Instagram à réorienter après validation. La détection des
sites déjà référencés n'est pas simulée dans ce premier jet ; prévoir son état
visuel (`UX-SUBMIT-001`) avant l'intégration. Aucune notification ni modération
réelle n'est exécutée.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.2 | 6 octobre 2026 | Maquette adaptée Site / Créateur ; suivi courant relié au parcours commun, historique conservé. |
| 0.1 | 6 octobre 2026 | Premier jet du formulaire, erreurs et confirmation, lié à l'accueil local. |
