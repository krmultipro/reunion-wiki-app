# Bouton de partage neutre — DEV, 11 novembre 2026

## Décision et périmètre

UX-SHARE-001 v1.3 : prévisualisation du bouton gris chaud validée explicitement,
puis demande d'implémentation. CSS uniquement, sans ajout fonctionnel au MVP.
Icône décorative à gauche et libellé « Partager cette fiche » conservés ; les
réseaux précèdent le partage, puis vient la correction. Fiche sans réseaux :
partage après présentation. Fiche privée/introuvable : aucune action publique.
Le dialogue, la copie et les parcours de contribution/modération sont inchangés.

## Critères définis avant modification

- Gris chaud #e9e9e2, bordure #d5d8cc, anthracite #30362e, sans soulignement ;
  survol #dedfd6, rayon 14 px, graisse 600, icône 18 px.
- Cible minimale 44 px mobile et hauteur 52 px PC, centrée dans la ligne des
  réseaux ; repli naturel, texte complet et aucun débordement à 320/390/1280 px.
- Un seul bouton accessible, ouverture par Entrée, fermeture Échap et retour
  du focus visible ; disponibilité sans réseaux et absence sur fiche privée.
- Modifier les styles de la refonte seulement ; aucun changement de données,
  URL, partage natif, envoi ou ressource externe.

## Schéma de réalisation

Branche isolée depuis le dernier dev → constater les styles anciens dans le
navigateur → CSS → recette navigateur et suites existantes → revue → commit →
publication/fusion dev → déploiement du commit officiel → vérification active.
La publication DEV suit VPS_DEV_ROUTING.md ; main et production sont exclus.
Sauvegarde fraîche VPS et restauration isolée de la copie PC existante avant
publication ; comparaison des empreintes sans exporter de nouveau contenu privé.

## Réalisation et preuves

### Recette locale et revue

- Avant changement, styles calculés : transparent, vert rgb(8,117,72), souligné.
  Ce constat échoue au contrat neutre ; après changement : rgb(233,233,226),
  anthracite rgb(48,54,46), aucun soulignement, rayon 14 px.
- Navigateur sur fixture synthétique à nom long : 320/390/1280 px sans
  débordement. À 320 px TikTok et partage sur la seconde ligne ; à 390 px
  partage replié ; à 1280 px les quatre actions alignées, hauteur 52 px.
  Mobile : bouton 44 px. Icône décorative et texte complet conservés.
- Entrée ouvre le dialogue ; Échap ferme et rend le focus au bouton, contour
  visible 3 px. Fiche sans liens : un seul bouton disponible.
- Suite applicative : 142 cas, 141 réussis et un manuel ignoré ; outillage :
  49 réussis. Compilation Python et git diff --check réussis.
- Revue indépendante du CSS et des documents : aucun défaut fonctionnel ;
  historique documentaire complété. Aucun test qui recopie les chaînes CSS.

### Récupération préparée

Snapshot cohérent frais DB+uploads conservé sur VPS hors conteneur. Copie PC
indépendante déjà existante vérifiée puis restaurée isolément. Empreintes de
contenu hors compteurs et des 34 uploads identiques au snapshot frais ; zéro
violation de clé étrangère. Les compteurs récents restent protégés par le
snapshot VPS. Aucun nouveau transfert privé vers le PC effectué. La copie PC
n'est pas présentée comme un snapshot frais identique de tous les compteurs.

### Publication

À compléter après déploiement et vérification du conteneur DEV réellement actif.
Journaux privés : /tmp/reunion-share-neutral-qa-20261111/, hors Git.
