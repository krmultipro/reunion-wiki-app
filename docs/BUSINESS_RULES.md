# Règles métier — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version du document | 1.8 |
| Statut | Validé |
| Dernière mise à jour | 11 novembre 2026 |

## Jalon refonte DEV — 11 novembre 2026

L’utilisateur valide la refonte selon la maquette avec recherche simple et
administration essentielle, puis publication DEV via `dev`. Les compléments
avancés sont reportés après cette étape selon [REFONTE_DEV](ux/REFONTE_DEV.md)
et le catalogue v1.8. Les exigences et leur historique restent conservés ;
contrôles de publication, brouillon imposé et protection du privé restent requis.
Cette décision ne publie pas la production et ne supprime aucune donnée.

Historique 1.8 — 11 novembre : jalon DEV et reports explicites consignés.

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

## Complément du 16 octobre 2026

La règle RM-TAL-012 précise le périmètre Talents péi. Elle complète les règles
existantes sans lever les questions de proposition sans lien officiel ni
requalifier les structures déjà enregistrées. Référence :
[conception Talents péi](ux/TALENTS_PEI_SCOPE.md). Documentation seule.

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

## Catalogue complet

Les 69 règles suivies dans Notion, avec leur périmètre projet, leur critère
d'acceptation et l'état d'implémentation observé, sont conservées dans
[`business-rules/RULES_CATALOG.md`](business-rules/RULES_CATALOG.md).

Les règles `RM-TAL` ci-dessous et les règles `RM-SITE` du document
[`business-rules/SITE_RULES.md`](business-rules/SITE_RULES.md) apportent des
précisions éditoriales à ce catalogue. La table de correspondance entre les
systèmes d'identifiants est conservée à la fin du catalogue.

## Talents péi

### RM-TAL-001 — Lien avec La Réunion

- **Version :** 1.0
- **Statut :** Active
- **Règle :** un talent doit avoir un lien réel et significatif avec La Réunion.
- **Critère d'acceptation :** au moins un rattachement est renseigné avant la
  publication : naissance, enfance, résidence, activité durable ou œuvre
  directement liée à La Réunion.

#### Amendement 1.1 — Moment et multiplicité du rattachement

- **Statut :** Actif
- **Précision :** un brouillon peut rester incomplet. Le rattachement devient
  obligatoire lors de la publication.
- **Multiplicité :** plusieurs rattachements peuvent être enregistrés pour une
  même fiche.
- **Critère d'acceptation complété :** la publication est refusée si aucun
  rattachement n'est renseigné ; la présence de plusieurs rattachements est
  acceptée.

### RM-TAL-002 — Notoriété et activité

- **Version :** 1.0
- **Statut :** Active
- **Règle :** un talent peut être connu ou émergent, actuellement actif,
  inactif ou historique.
- **Critère d'acceptation :** aucun seuil d'abonnés, d'audience, de récompense
  ou de fréquence de publication ne conditionne l'admissibilité.

### RM-TAL-003 — Source du lien réunionnais, version 2.0

- **Statut :** Active, décision utilisateur 2A (dernier questionnaire lancement),
  7 octobre 2026. Remplace la version 1.0 et son amendement 1.1 ci-dessous.
- **Lancement/MVP :** l'administrateur vérifie le lien réel à La Réunion avec
  une source simple et pertinente, conservée en privé dans l'administration.
  Aucune rubrique Sources ni justification publique obligatoire sur la fiche.
- **Source simple :** bio officielle, déclaration publique explicite du créateur,
  profil/site officiel, interview ou autre source déjà acceptée. Un article de
  presse ou une recherche approfondie systématique n'est pas exigé. La source
  doit réellement confirmer le rattachement ; la seule existence d'un compte
  social ou d'un nom réunionnais ne suffit pas.
- **Conservation :** référence identifiable et lien de la source, avec une courte
  note utile à la vérification, sans dossier éditorial lourd imposé au lancement.
  Les données détaillées/historiques déjà disponibles restent conservées.
- **Publication :** conserver l'exigence d'au moins un rattachement et d'une source
  vérifiable enregistrée ; un brouillon peut rester incomplet. Une source non
  trouvée ne devient pas une validation implicite du lien.
- **Visibilité :** la référence de vérification reste privée. Les liens officiels
  destinés à découvrir le créateur restent affichables selon RM-TAL-008, sans
  être présentés automatiquement comme preuve du rattachement.
- **Critères d'acceptation :** un contrôle admin s'appuie sur une source enregistrée
  avant publication ; la fiche publique n'exige pas de bloc source. Les preuves
  privées ne sont pas divulguées. Aucune vérification ou migration de stockage
  n'est déclarée réalisée par cette décision documentaire.

#### Historique conservé — version 1.0 et amendement 1.1 remplacés

### RM-TAL-003 — Source du lien réunionnais

- **Version :** 1.0
- **Statut :** Remplacée par la version 2.0 du 7 octobre 2026
- **Règle :** au moins une source publique doit permettre de vérifier le lien
  du talent avec La Réunion.
- **Sources acceptées :** profil officiel sur un réseau social, vidéo,
  interview, article de presse, site officiel, portfolio, page d'un événement,
  d'une association ou d'un organisme identifiable.
- **Critère d'acceptation :** au moins une source pertinente est enregistrée et
  affichée sur la fiche publiée. La source doit confirmer l'information qu'elle
  justifie.

#### Amendement 1.1 — Données et visibilité des sources

- **Statut :** Remplacé par la version 2.0 du 7 octobre 2026
- **Quantité :** une source est obligatoire pour publier et plusieurs sources
  peuvent être associées à la fiche.
- **Données minimales :** chaque source conserve son type, un titre ou une
  description, son URL et le nom du compte officiel, média ou organisme.
- **Visibilité :** au moins une source vérifiable est affichée publiquement. Une
  preuve privée ou contenant des informations personnelles reste réservée à
  l'administration.
- **Brouillon :** une fiche peut être enregistrée sans source tant qu'elle reste
  en brouillon.

### RM-TAL-004 — Provenance et autorisation de l'image

- **Version :** 1.0
- **Statut :** Active
- **Règle :** la provenance de l'image et le nom du photographe ou du titulaire
  des droits doivent être renseignés, et la preuve de l'autorisation
  d'utilisation doit être conservée.
- **Critère d'acceptation :** une image n'est publiée que si sa provenance, son
  crédit et l'état de son autorisation sont documentés. La preuve de
  l'autorisation peut rester privée dans l'administration.

#### Amendement 1.1 — Image temporaire pendant le lancement

- **Statut :** Actif
- **Nature :** précision compatible avec la version 1.0.
- **Précision :** une diffusion temporaire, expérimentale ou destinée à tester
  l'intérêt du service ne dispense pas de disposer des droits nécessaires. Une
  image publique ou créditée n'est pas automatiquement réutilisable.
- **Décision de lancement :** sans autorisation ou licence documentée, la fiche
  est publiée sans portrait avec l'image générique Réunion Wiki. Une image
  spécifique non justifiée est retirée ou remplacée sans délai.
- **Traçabilité :** voir
  [`ADR-002`](decisions/ADR-002-droits-images-talents-au-lancement.md).

#### Amendement 1.2 — Report de la gestion structurée

- **Statut :** Actif
- **Périmètre :** Plus tard.
- **Précision :** l'ajout de champs dédiés à la provenance, au crédit, à la
  licence et à la preuve d'autorisation n'est pas bloquant pour le MVP talents.
- **Règle transitoire :** la présence d'un portrait n'est pas obligatoire. Si
  aucun droit n'est vérifié manuellement, l'image générique est utilisée.
- **Limite :** ce report fonctionnel ne crée pas d'autorisation juridique pour
  publier une image tierce non justifiée.

#### Précision visuelle — 8 octobre 2026

Le choix validé UX-FICHE-008 précise l’image générique : silhouette de profil
neutre pour les créateurs, en remplacement du palmier dans les maquettes.
Les conditions de publication et de droits ci-dessus restent inchangées ;
le backend utilise encore son image de remplacement existante avant intégration.

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

#### Amendement 1.1 — Séparation création et publication

- **Statut :** Actif
- **Précision :** toute fiche créée par un administrateur reçoit d'abord le
  statut brouillon.
- **Critère d'acceptation complété :** le formulaire de création ne permet pas
  une publication directe ; une action séparée déclenche les contrôles puis la
  publication.

### RM-TAL-007 — Correction et archivage

- **Version :** 1.0
- **Statut :** Active
- **Règle :** une fiche publiée doit pouvoir être corrigée ou archivée.
- **Critère d'acceptation :** un administrateur peut modifier une fiche sans la
  recréer et peut la retirer du site sans supprimer définitivement son
  historique.

#### Amendement 1.1 — Demandes émises par le talent

- **Statut :** Actif
- **Canal MVP :** la demande est reçue par le formulaire de contact ou l'adresse
  email officielle de Réunion Wiki.
- **Accès :** le talent ne reçoit aucun accès direct à la modification de sa
  fiche ; seul un administrateur applique la décision.
- **Vérification :** l'identité du demandeur est vérifiée de manière raisonnable,
  notamment à l'aide d'un compte officiel lié au talent.
- **Traçabilité privée :** la date, le motif, la décision et l'action appliquée
  sont conservés dans l'administration.
- **Effets :** une correction maintient la fiche ; un archivage la retire du
  public en conservant son historique ; un retrait définitif supprime la
  publication de la fiche et de son portrait ainsi que les données qui ne
  doivent plus être conservées.

### RM-TAL-008 — Plateformes facultatives

- **Version :** 1.0
- **Statut :** Active
- **Règle :** l'association d'un talent à une plateforme est facultative.
- **Critère d'acceptation :** une fiche peut être publiée sans réseau social et
  n'apparaît dans une sélection de plateforme que si l'URL correspondante est
  renseignée et valide.

#### Amendement 1.1 — Twitch dans le MVP

- **Statut :** Actif
- **Plateformes :** Instagram, YouTube, TikTok, Facebook, Twitch et site
  officiel sont facultatifs.
- **Twitch :** l'URL est validée en HTTP ou HTTPS, affichée sur la fiche et rend
  la fiche disponible dans le filtre Twitch lorsqu'elle est publiée.
- **Hors MVP :** aucune page SEO Twitch dédiée n'est exigée pour le lancement.

### RM-TAL-009 — Recherche et filtres publics

- **Version :** 1.0
- **Statut :** Active
- **Règle :** les fiches publiées peuvent être recherchées par nom affiché,
  pseudonyme ou texte de présentation.
- **Filtres MVP :** catégorie principale et plateforme.
- **Combinaison :** la recherche et les deux filtres peuvent être appliqués
  simultanément.
- **Visibilité :** aucun brouillon ni fiche archivée ne peut apparaître.
- **Résultat vide :** un message clair et une action de réinitialisation des
  filtres sont affichés.

### RM-TAL-010 — Contrôles avant publication

- **Version :** 1.0
- **Statut :** Active
- **Règle :** l'action de publication vérifie le nom ou pseudonyme, la catégorie
  principale, la présentation neutre, au moins un rattachement à La Réunion, au
  moins une source valide et la validité des URLs de plateformes.
- **Image :** la documentation structurée de l'image n'est pas un blocage du MVP.
  La fiche utilise l'image générique lorsqu'aucun portrait justifié n'est
  disponible.
- **Critère d'acceptation :** toute fiche ne respectant pas un contrôle
  obligatoire reste en brouillon avec des erreurs explicites.

### RM-TAL-011 — Fiche pilote grandeur nature

- **Version :** 1.0
- **Statut :** Active
- **Règle :** avant de considérer le parcours talents prêt, une fiche réelle
  d'un proche créateur ou influenceur est traitée entièrement.
- **Parcours vérifié :** brouillon, rattachements, sources, image ou image
  générique, catégorie, plateformes, publication, affichage mobile et ordinateur,
  liens, correction et archivage.
- **Réussite :** le parcours fonctionne sans modification manuelle de la base de
  données et le talent valide le contenu affiché.
- **Retour :** les remarques du talent sont conservées dans des notes et servent
  à améliorer le formulaire et les règles métier.

### RM-TAL-012 — Créateurs de contenu au lancement, version 2.0

- **Version :** 2.0
- **Statut :** Active, conception validée le 17 octobre 2026 ; aucune réalisation vérifiée par ce lot.
- **Remplace :** v1.0 du 16 octobre, conservée ci-dessous.
- **Règle :** la rubrique Créateurs présente des personnes ou collectifs pour
  leur activité de création de contenu en lien réel avec La Réunion. Un métier
  artistique ou artisanal seul ne vaut pas admission ; l’ouverture générale
  aux autres talents est reportée.
- **Critère d’acceptation :** la présentation et les liens permettent de
  comprendre l’activité de contenu du créateur. Les contrôles RM-TAL-001 à 010
  restent applicables, sans seuil de notoriété. Nom et lien officiel exigés à la
  proposition selon UX-PROP-002 ; aucun compte social particulier obligatoire.
  Aucun contrôle supplémentaire de plateforme à la publication ne remplace RM-TAL-008.
- **Exclusions :** fiches d’entreprises et fonctions de prestataires hors de
  cette rubrique ; annuaire des sites inchangé. Aucun type historique supprimé.
- **Référence :** UX-CONT-001 à 006 dans
  [CONTENT_CREATORS_SCOPE.md](ux/CONTENT_CREATORS_SCOPE.md).

### RM-TAL-012 — Version 1.0 remplacée : périmètre éditorial Talents péi

- **Version :** 1.0
- **Statut :** Remplacée par RM-TAL-012 v2.0 du 17 octobre 2026 ; ouverture large reportée.
- **Règle :** la rubrique présente des personnes et des collectifs dont
  l’activité, les créations ou le savoir-faire peuvent être décrits concrètement.
  Créateurs de contenu, artistes et artisans sont notamment admissibles sous
  réserve des contrôles RM-TAL-001 à 010. Aucun seuil de notoriété n’est ajouté.
- **Exclusions au lancement :** fiches d’entreprises dans cette rubrique et
  fonctions de devis, disponibilités, avis ou classement de prestataires.
  Cette exclusion ne modifie pas l’annuaire des sites.
- **Critère d’acceptation :** une fiche décrit la personne ou le collectif et
  son travail de manière neutre ; le lien réunionnais et sa source sont vérifiés,
  le passage en brouillon et la publication distincte restent requis. Une
  demande centrée sur une entreprise n’est pas publiée comme fiche talent.
- **Limites :** collectifs/structures existantes et entreprises doivent être
  distingués avant toute requalification ; aucune suppression automatique.
  Voir UX-TAL-001 à 006 et les questions ouvertes de TALENTS_PEI_SCOPE.md.


## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.7 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 1.6 | 16 octobre 2026 | Ajout RM-TAL-012 : périmètre Talents péi et exclusions au lancement, sans changement des contrôles ni réalisation. |
| 1.5 | 7 octobre 2026 | RM-TAL-003 v2.0 validée : vérification légère et source privée au lancement ; affichage public obligatoire remplacé, anciennes versions conservées. Aucun backend modifié. |
| 1.4 | 16 septembre 2026 | Ajout des décisions de cas limites pour les sites : transitions de statut, accessibilité HTTP, redirections et normalisation, recherche, identification des clics répétés et nouvelle publication explicite. |
| 1.3 | 16 septembre 2026 | Validation des décisions relatives aux sites : admissibilité, données minimales, normalisation et doublons, catégorie unique, portée géographique, statuts, recherche, clics, dates, modération, contrôles de publication et parcours pilote. |
| 1.2 | 15 septembre 2026 | Validation des décisions talents : rattachements multiples, sources publiques, Twitch, recherche et filtres, demandes de correction, brouillon obligatoire, contrôles de publication et fiche pilote. Report de la gestion structurée des droits d'image. |
| 1.1 | 14 septembre 2026 | Ajout du catalogue complet des 69 règles et clarification juridique de RM-TAL-004 pour le lancement. |
| 1.0 | 2 septembre 2026 | Validation des premières règles d'admissibilité, de sourcing, d'image, de rédaction et de publication des talents. |
