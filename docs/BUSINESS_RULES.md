# Règles métier — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version du document | 1.0 |
| Statut | Validé |
| Dernière mise à jour | 2 septembre 2026 |

## Convention

- Chaque règle possède un identifiant stable.
- Les identifiants préfixés par domaine, comme `RM-TAL`, évitent les collisions
  lors de l'ajout de nouvelles familles de règles.
- Une règle validée ne doit pas être supprimée ni réécrite avec un sens
  différent.
- Une évolution mineure produit une nouvelle révision, par exemple `1.1`.
- Un changement de décision produit une nouvelle version, par exemple `2.0`.
- La version précédente reste présente avec le statut `Remplacée` et indique la
  règle ou la décision qui la remplace.
- Les décisions structurantes sont consignées dans [`decisions/`](decisions/README.md).

## Migration depuis Notion

Ce document commence par les règles talents validées pendant la mise en place
du Docs as Code. Les règles déjà présentes dans Notion ne sont ni supprimées ni
invalidées.

Lors de leur migration vers Markdown, elles doivent être copiées avec leur
identifiant, leur formulation et leur statut d'origine. Une contradiction doit
être résolue par une nouvelle version ou un amendement explicite, jamais en
écrasant silencieusement la règle existante.

## Talents péi

### RM-TAL-001 — Lien avec La Réunion

- **Version :** 1.0
- **Statut :** Active
- **Règle :** un talent doit avoir un lien réel et significatif avec La Réunion.
- **Critère d'acceptation :** au moins un rattachement est renseigné avant la
  publication : naissance, enfance, résidence, activité durable ou œuvre
  directement liée à La Réunion.

### RM-TAL-002 — Notoriété et activité

- **Version :** 1.0
- **Statut :** Active
- **Règle :** un talent peut être connu ou émergent, actuellement actif,
  inactif ou historique.
- **Critère d'acceptation :** aucun seuil d'abonnés, d'audience, de récompense
  ou de fréquence de publication ne conditionne l'admissibilité.

### RM-TAL-003 — Source du lien réunionnais

- **Version :** 1.0
- **Statut :** Active
- **Règle :** au moins une source publique doit permettre de vérifier le lien
  du talent avec La Réunion.
- **Sources acceptées :** profil officiel sur un réseau social, vidéo,
  interview, article de presse, site officiel, portfolio, page d'un événement,
  d'une association ou d'un organisme identifiable.
- **Critère d'acceptation :** au moins une source pertinente est enregistrée et
  affichée sur la fiche publiée. La source doit confirmer l'information qu'elle
  justifie.

### RM-TAL-004 — Provenance et autorisation de l'image

- **Version :** 1.0
- **Statut :** Active
- **Règle :** la provenance de l'image et le nom du photographe ou du titulaire
  des droits doivent être renseignés, et la preuve de l'autorisation
  d'utilisation doit être conservée.
- **Critère d'acceptation :** une image n'est publiée que si sa provenance, son
  crédit et l'état de son autorisation sont documentés. La preuve de
  l'autorisation peut rester privée dans l'administration.

### RM-TAL-005 — Neutralité de la présentation

- **Version :** 1.0
- **Statut :** Active
- **Règle :** le texte de présentation doit être factuel, neutre et dépourvu de
  slogan ou de jugement de valeur.
- **Critère d'acceptation :** la fiche ne contient pas de formulation comme
  « le meilleur », « incontournable » ou toute affirmation promotionnelle non
  vérifiable.

### RM-TAL-006 — Brouillon obligatoire

- **Version :** 1.0
- **Statut :** Active
- **Règle :** toute nouvelle fiche talent doit passer par un brouillon avant sa
  première publication.
- **Critère d'acceptation :** la création d'une fiche ne la rend pas visible au
  public et une action volontaire de publication est nécessaire.

### RM-TAL-007 — Correction et archivage

- **Version :** 1.0
- **Statut :** Active
- **Règle :** une fiche publiée doit pouvoir être corrigée ou archivée.
- **Critère d'acceptation :** un administrateur peut modifier une fiche sans la
  recréer et peut la retirer du site sans supprimer définitivement son
  historique.

### RM-TAL-008 — Plateformes facultatives

- **Version :** 1.0
- **Statut :** Active
- **Règle :** l'association d'un talent à une plateforme est facultative.
- **Critère d'acceptation :** une fiche peut être publiée sans réseau social et
  n'apparaît dans une sélection de plateforme que si l'URL correspondante est
  renseignée et valide.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.0 | 2 septembre 2026 | Validation des premières règles d'admissibilité, de sourcing, d'image, de rédaction et de publication des talents. |
