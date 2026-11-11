# Propositions de sites et créateurs — parcours commun

## Navigation des variantes de maquette — 22 octobre 2026

[UX-HOME-024](HOME_PAGE.md) complète ce parcours : les liens entre pages partagées
conservent la version d’accueil via un contexte d’URL explicite autorisé ;
Accueil/logo revient à cette version. Les retours intermédiaires gardent leur
page d’origine et leurs critères. Dans l’essai Navigation flottante seulement,
les quatre rubriques restent accessibles en bas sur mobile ; les autres versions
conservent leur menu. Aucun changement des règles métier ou du backend.

## Nom public courant — amendement du 20 octobre 2026

[UX-CONT-007](CONTENT_CREATORS_SCOPE.md) remplace les libellés génériques
« Créateurs » par « Personnalités » dans le menu, « Personnalités réunionnaises »
dans les titres et « Proposer une personnalité » dans les actions de la maquette.
Les paragraphes et preuves historiques ci-dessous conservent leurs noms
antérieurs. Les parcours et données d’exemple restent inchangés ; l’intention
d’ouverture aux artistes et sportifs n’établit pas encore leurs critères
métiers. Aucun backend ni déploiement adapté par ce renommage.


| Métadonnée | Valeur |
| --- | --- |
| Version | 0.7 |
| Date | 17 octobre 2026 |
| Statut | Choix 1 à 10 validés ; base suffisante pour adapter la maquette |
| Réalisation | Maquette locale Site / Créateur adaptée ; backend non implémenté |

## Décision applicable — créateurs de contenu, 17 octobre 2026

Le [périmètre de lancement](CONTENT_CREATORS_SCOPE.md) remplace l’ouverture générale aux
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

## Historique — complément Talents péi du 16 octobre 2026, remplacé sur le périmètre

La [fiche de périmètre](TALENTS_PEI_SCOPE.md) fait référence : UX-TAL-001 à
006 et RM-TAL-012, personnes et collectifs, dont artistes et artisans ; fiches
d’entreprises hors de cette rubrique au lancement. Le choix cible Site / Talent et l’action Proposer un talent remplacent Site / Créateur. Proposition de soi ou d’un tiers, sans compte au lancement. UX-PROP-002 conserve pour l’instant nom et lien officiel obligatoires : le cas sans lien reste ouvert, sans suppression implicite de cette exigence.

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Décisions validées

Complément du 9 octobre 2026 : le périmètre de conception est étendu aux comptes
contributeurs, corrections modérées avec historique et notifications fiables.
Voir [CONTRIBUTOR_WORKFLOW.md](CONTRIBUTOR_WORKFLOW.md), décisions validées
`1A 2A 3A`, complétées par 4A, vérification email et 6B. Les décisions initiales
ci-dessous sont conservées historiquement ; 4A remplace la contribution anonyme
par un compte avec email vérifié obligatoire pour Site/Créateur dans la cible
future à concevoir. Clarification ultérieure du même jour : cette évolution
est différée ; le lancement conserve le parcours initial sans compte contributeur.
Aucune
extension de la maquette ou du backend n’est réalisée par ce complément.

Réponses de l'utilisateur : `1A 2A 3A 4A 5A 6A 7A`.
Complément validé : `8A 9A 10A`.

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-PROP-001 | Une page « Proposer » permet de choisir Site ou Créateur et présente les champs adaptés. Réutiliser les composants communs sans confondre les deux types de données. |
| UX-PROP-002 | Pour un créateur, seuls le nom et un lien officiel sont obligatoires à l'envoi ; catégorie, description et lien avec La Réunion sont facultatifs à cette étape. Pour un site, conserver nom, URL, description et catégorie obligatoires selon `RM-SITE-010`. |
| UX-PROP-003 | Toute personne peut proposer un créateur sans compte. Le proposant n'a aucun droit de publication ou modification directe de la fiche. |
| UX-PROP-004 | Proposition en attente → vérification/correction admin → création ou rattachement à une fiche → publication ou refus. Aucune publication automatique. Toute nouvelle fiche talent passe par un brouillon et une publication distincte, conformément à `RM-TAL-006` ; une proposition en attente n'est pas une fiche publiée. |
| UX-PROP-005 | Un même lien officiel de créateur bloque une nouvelle proposition et renvoie à la fiche existante lorsque celle-ci est publique. Un même nom produit un avertissement admin, pas un blocage automatique. Pour les éléments non publics, appliquer le complément `UX-PROP-009`. |
| UX-PROP-006 | L'email du proposant est facultatif et privé pour les deux types ; il permet une demande de précision ou une réponse manuelle. |
| UX-PROP-007 | Première version : sites et créateurs, sans compte, sans envoi de photo ni notification automatique. Ces fonctionnalités sont reportées, pas requises pour le lancement de ce parcours. |
| UX-PROP-008 | Si le lien avec La Réunion est absent de la proposition de créateur, l'administrateur le recherche et le vérifie avant publication. L'envoi reste possible ; la publication exige les preuves prévues par `RM-TAL-001` et `RM-TAL-003`. |
| UX-PROP-009 | Si le même lien officiel correspond à un élément non public (en attente, brouillon, archivé ou refusé), bloquer la nouvelle proposition avec « Ce profil est déjà enregistré ». Ne révéler ni le statut, ni le motif de modération, ni les données privées, et ne renvoyer à aucune fiche non publique. |
| UX-PROP-010 | L'administrateur peut corriger le type d'une proposition et rattacher les liens au créateur concerné, sans demander un nouvel envoi. Cette correction ne publie rien automatiquement et ne supprime pas implicitement une fiche existante. Les critères de publication du type retenu restent applicables. |

Les exigences de publication des talents (`RM-TAL-001` à `RM-TAL-006`) restent
applicables : une proposition minimale ne dispense pas l'administrateur des
contrôles, sources et informations nécessaires à la publication.

## Accès au formulaire — décision validée

`UX-PROP-011` : page dédiée, accessible depuis « Proposer » dans la navigation
principale, l'appel « Un site ou un talent à partager ? » en bas de l'accueil,
et « Proposer un créateur » sous la liste des créateurs. Ce dernier accès ouvre
le choix Créateur présélectionné (`proposer.html?type=createur` dans la maquette).
Le formulaire complet n'est pas intégré à l'accueil. Un seul lien officiel
est demandé pour l'instant ; les réseaux supplémentaires restent reportés.

Réalisation locale : accès de navigation ajouté/rendu actif dans les maquettes
liste et fiche talent ; les deux accès de l'accueil existaient déjà. Ces liens
ouvrent le même formulaire. Vérification dans le navigateur local : clic sur
« Proposer un créateur » et choix Créateur présélectionné confirmé ; clic sur
l’appel en bas de l’accueil et arrivée sur le formulaire commun confirmés.
Rendu de la liste et du nouveau lien observé sur ordinateur. Cette décision ne
déploie pas le parcours réel.

## Détails techniques à préciser avant implémentation

- Quelle normalisation des liens officiels de créateurs utiliser pour les
  doublons (paramètres, variantes, autres comptes du même créateur) ? Ne pas
  appliquer aveuglément les règles d'URL de sites aux identifiants sociaux.
- Préparer une proposition technique et ses cas de test : variantes d'un même
  profil, paramètres fonctionnels à conserver, comptes différents et homonymes.
  Ne pas fusionner deux comptes sur la seule ressemblance du nom.
- Définir le stockage des propositions et la correction de type sans perte de
  saisie ni historique, en réutilisant les parcours existants.

Ces détails ne bloquent pas la maquette et ne justifient pas un nouveau
questionnaire produit à ce stade. Les décisions 8 à 10 résolvent les trois
questions fonctionnelles conservées dans la version 0.1 ; elles restent
traçables dans l'historique Git et ci-dessous.

## Suivi

La maquette [du formulaire site](SITE_SUBMISSION_MOCKUP.md) reste un premier
jet désormais adapté aux deux types selon les dix choix validés. Pas de modification du backend,
de migration ou de déploiement autorisée par la validation de conception.
Les cas de doublons, erreurs, confirmation et correction seront reliés aux
contrôles de la future réalisation ; les vérifications de maquette sont consignées ci-dessous et ne valident pas
le backend.

## Vérification de la maquette commune — 6 octobre 2026

- Parcours créateur vide : erreurs sur le nom et le lien uniquement.
- Parcours site vide : erreurs sur les quatre champs obligatoires.
- Nom et lien de créateur conservés après passage Site puis Créateur ; envoi
  simulé réussi avec les champs facultatifs vides, vers la confirmation commune.
- Rendu créateur observé sur mobile (390 × 844) ; rendu desktop observé à
  1280 × 900, notamment pour le doublon non public.
- Doublon public simulé : lien vers la fiche d'Adriana et bouton d'envoi désactivé.
  Doublon non public : message générique sans statut ni lien privé, envoi désactivé.
- Les informations facultatives sont regroupées ; l'email reste commun aux deux
  types. Les autres saisies sont conservées séparément en mémoire durant la page.
- Le changement de type seul ne déclenche pas l'avertissement de perte de saisie.

Limites : catégories/communes illustratives, doublons affichés uniquement par
les liens d'aperçu, aucun contrôle de base réel, aucune sauvegarde ni modération
admin. La validation visuelle finale par l'utilisateur reste attendue.

## Complément de revue globale — 8 octobre 2026

Aperçus doublons publics/non publics disponibles séparément pour Site/Créateur.
Site public : consultation dans sa catégorie filtrée ; créateur public : fiche.
Non-public : message générique sans statut/motif ni lien. Changer l'URL enlève
l'alerte illustrative, rétablir la même URL la réactive. Champs conservés ;
correction puis confirmation simulée vérifiées. Texte d'aide 12 px et navigation
mobile 13 px pour cohérence C. Ces corrections ne simulent pas la normalisation
réelle ni une modération ou notification automatique.

Cas site depuis catégorie et créateur minimal rejoués, retours et erreurs
contrôlés. Preuves globales dans testing/MAQUETTE_UX_REVIEW_2026-10-08.md.
L'URL de doublon reconnue est uniquement celle de la fixture, pas une base.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.7 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.6 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 0.5 | 8 octobre 2026 | Revue globale : doublons Site/Créateur et correction d’URL simulée complétés ; minimum créateur et présélection/retour site rejoués, aucune intégration. |
| 0.4 | 6 octobre 2026 | Accès validés et ajoutés à la maquette : navigation, bas de l’accueil et liste des créateurs avec type présélectionné. Un seul lien officiel conservé. |
| 0.3 | 6 octobre 2026 | Maquette commune adaptée, saisies distinctes conservées, validation selon le type, confirmation et doublons simulés ; contrôles locaux consignés. |
| 0.2 | 6 octobre 2026 | Validation de 8A, 9A et 10A : rattachement réunionnais vérifié par l'admin, doublons non publics masqués et correction du type en modération. Questions fonctionnelles résolues ; détails techniques différés. |
| 0.1 | 6 octobre 2026 | Enregistrement des sept réponses validées et des questions restantes. |

## Relecture et validation du 17 octobre 2026

L’utilisateur confirme que la présentation publique et les parcours vus lui
conviennent et demande la finalisation des contrôles. Preuves et limites
actuelles : [revue finale](../testing/MAQUETTE_FINAL_REVIEW_2026-10-17.md).
Messages au tutoiement et libellés créateurs harmonisés dans la maquette ;
aucune intégration Flask ni publication. Le contrôle mobile des quatre
rubriques admin historiques est maintenant observé à 320/390 px effectifs ;
l’extension admin V1 non réalisée reste au suivi #34, sans validation implicite.
Les mentions d’attente antérieures restent historiques et ne rouvrent pas
les choix publics déjà validés.
