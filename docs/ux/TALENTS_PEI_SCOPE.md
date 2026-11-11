# Talents péi — périmètre et parcours

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Date | 17 octobre 2026 |
| Statut | Orientation large remplacée ; piste reportée, historique conservé |
| Réalisation | Documentation uniquement ; aucune adaptation de code ou de maquette |

## Statut courant — remplacée le 17 octobre 2026

L’ouverture générale et les libellés UX-TAL-001/002 sont remplacés par
[CONTENT_CREATORS_SCOPE.md](CONTENT_CREATORS_SCOPE.md), UX-CONT-001 à 006 et
RM-TAL-012 v2.0 : créateurs de contenu au lancement, ouverture générale reportée.
UX-TAL-003 à 006 restent compatibles pour les exclusions, la modération,
Contact/email et les comptes différés. Les questions propres aux artisans sans
lien et les trois exemples ci-dessous ne conditionnent plus le lancement et ne
sont pas à réaliser maintenant. Ce fichier conserve la décision historique.


## Origine et portée

Après relecture du ticket Dashboard #14, l’utilisateur interroge le sens de
« proposer un talent », notamment pour un créateur de contenu et un menuisier.
Il retient l’orientation Talents péi, exclut les entreprises pour le moment,
confirme son souhait d’un compte avec tableau de bord plus tard, puis demande
de consigner les modifications de conception sans modifier aucun code.

Cette décision complète PRODUCT.md et les règles RM-TAL-001 à 011 par
RM-TAL-012. Elle remplace les libellés publics génériques « Créateurs » et
« Proposer un créateur » comme cible de conception, sans invalider les choix
de présentation et de navigation déjà validés. Les anciens libellés et les
preuves de maquettes restent historiques ; ils ne décrivent pas une adaptation
réalisée le 16 octobre. Les noms de fichiers, routes et identifiants techniques
ne sont pas renommés par cette décision.

## Décisions validées

| ID | Décision |
| --- | --- |
| UX-TAL-001 | Nom public de la rubrique : « Talents péi ». Action : « Proposer un talent ». Employer « talent » dans les aides génériques et « créateur de contenu », « artiste » ou « artisan » lorsque le métier le justifie. |
| UX-TAL-002 | Présenter des personnes et des collectifs, leur activité, leurs créations ou leur savoir-faire : création de contenu, arts et artisanat notamment. Ce ne sont pas des catégories exhaustives ni un nouveau référentiel validé. |
| UX-TAL-003 | Aucune fiche d’entreprise dans cette rubrique au lancement ; aucune fonction de devis, disponibilités, avis ou classement de prestataires ajoutée. Le périmètre existant de l’annuaire des sites reste inchangé. |
| UX-TAL-004 | Chacun peut proposer son propre profil ou celui d’un tiers sans compte au lancement. Une proposition n’est ni une fiche publiée, ni un droit de gestion. Vérification administrative et brouillon avant publication distincte restent obligatoires. |
| UX-TAL-005 | Compte avec tableau de bord souhaité pour une évolution ultérieure, hors lancement. Les choix contributeurs déjà validés restent applicables ; aucun droit automatique de propriété ou de publication n’est ajouté. |
| UX-TAL-006 | Au lancement, demandes de correction, archivage ou retrait par Contact/email, vérification raisonnable de l’identité, décision et action administratives avec trace privée selon RM-TAL-007. |

Le rattachement réel vérifié avec La Réunion, la source simple privée, la
neutralité, le portrait facultatif et l’absence de seuil de notoriété restent
requis selon les règles existantes. Une activité concrète présentable permet
la découverte ; le seul fait de se déclarer « talent » ne vaut pas admission.
L’ouverture n’est pas une promesse d’augmentation d’audience mesurée.

## Parcours de lancement

- Visiteur : accueil/recherche/liste Talents péi → fiche publiée → liens et
  retour avec critères/position selon les parcours déjà validés. États vides,
  erreurs, clavier et mobile restent soumis aux exigences existantes.
- Proposant : choix Site/Talent → formulaire adapté → erreurs ou doublon →
  confirmation de réception en attente ; aucune visibilité publique automatique.
  La possibilité de se proposer n’impose pas que le proposant soit le talent.
- Administrateur : examiner, corriger le type ou rattacher à une fiche existante,
  demander des précisions par le canal disponible, refuser ou préparer un
  brouillon ; vérifier l’admissibilité et publier par une action distincte.
- Talent concerné : demande de correction/archivage/retrait → vérification de
  l’identité → décision administrative → modification ou masquage selon
  RM-TAL-007. L’absence de compte ne bloque pas cette demande. Les messages
  détaillés et délais de traitement ne sont pas nouvellement définis ici.

## Points ouverts avant les adaptations dépendantes

1. **Proposition sans lien officiel :** UX-PROP-002 exige aujourd’hui nom et
   lien officiel, alors que RM-TAL-008 autorise une fiche sans réseau social.
   Le parcours d’un artisan sans site ni profil reste à trancher ; le lien
   obligatoire n’est pas supprimé implicitement. Distinguer lien de proposition,
   réseaux facultatifs et preuve privée du rattachement.
2. **Collectifs et structures existantes :** le guide et le modèle mentionnent
   aussi association, média, chaîne ou podcast. Ne pas supprimer leurs données
   ou types. Préciser les cas frontières avec une entreprise avant toute
   requalification ; aucune migration n’est autorisée.
3. **Tableau de bord futur :** préciser le contenu et les droits, notamment
   suivi des propositions et corrections, éventuelle revendication de fiche et
   vérification d’identité. Un compte contributeur ne rend pas propriétaire.
4. **Catégories :** vérifier la couverture des domaines avant adaptation ; ni
   liste exhaustive, ni catégorie supplémentaire, ni champ portfolio nouveau
   ne sont validés automatiquement.

Ces questions n’empêchent pas de consigner l’orientation ; elles empêchent de
considérer la conception détaillée correspondante comme terminée.

## Vérifications préparées, non exécutées

Avant généralisation aux maquettes puis intégration, préparer trois exemples
éditoriaux : créateur de contenu, artiste et artisan. Ils doivent permettre de
comprendre qui est la personne, son activité et son lien avec La Réunion dans
la même structure de fiche, sans présentation commerciale d’entreprise.
Aucun exemple factuel, nouvelle fiche réelle ou maquette n’est créé par ce lot.

Les critères sont reliés dans testing/TALENT_TEST_CASES.md. Vérifier ensuite
les libellés et la compréhension du périmètre sur mobile/ordinateur, le
formulaire et ses doublons, les statuts non publics et la demande de correction.
Les résultats historiques de maquette ne prouvent pas ces nouveaux critères.

## Suivi et limites

Conception transversale consignée pour la reprise du ticket #14. Aucun ticket
n’est clôturé ou modifié dans le Dashboard par ce travail documentaire. Code,
maquettes, base, référentiels, URLs et environnements déployés inchangés.
Les comptes restent hors lancement selon CONTRIBUTOR_WORKFLOW.md.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.1 | 17 octobre 2026 | Orientation large remplacée par le lancement créateurs de contenu ; conservation de l’historique et de la piste reportée. |
| 1.0 | 16 octobre 2026 | Orientation Talents péi, entreprises exclues de la rubrique au lancement, parcours sans compte, tableau de bord différé et questions ouvertes consignés. |
