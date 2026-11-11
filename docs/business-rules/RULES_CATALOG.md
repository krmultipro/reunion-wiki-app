# Catalogue des règles métier — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.8 |
| Statut | Référence versionnée |
| Date du relevé | 16 septembre 2026 |
| Origine | Base Notion « Règles métiers Réunion Wiki » et audit statique du dépôt |

## Jalon refonte DEV — 11 novembre 2026

Complément validé par l’utilisateur : intégration fidèle de la maquette, recherche
simple et administration essentielle. Les compléments d’interface RM-10/12/13,
RM-32/40 (plateforme/Twitch), les outils admin avancés, la nouvelle présentation
RM-41 à 47 et la finalisation RM-62/63 sont reportés après ce jalon DEV.
Le texte et l’historique de ces exigences restent conservés. La confidentialité
effective, les droits d’accès, les contrôles de publication et la visibilité
publiée seule ne sont pas reportés. La finalisation de confidentialité précède
l’ouverture publique et la collecte réelle. Voir [REFONTE_DEV](../ux/REFONTE_DEV.md).

Historique 1.8 — 11 novembre : périmètre de livraison DEV simplifié et reports
explicitement validés ; les états historiques ci-dessous ne constituent pas
une validation de la refonte en cours.

## Complément du 17 octobre 2026 — affichage public

Les tendances ne font plus partie de l’expérience publique cible, conformément
à RM-SITE-008 amendement 1.3 et UX-GEN-009 v2.0. RM-18/19 conservent les calculs,
statuts et règles privées, sans imposer une page publique. L’obligation d’accès
public antérieure est remplacée ; le retrait effectif de la route et du SEO est
à réaliser dans #18, pas déclaré implémenté ou testé par la maquette. Les états
historiques ci-dessous ne prouvent pas cette révision. Les blocs globaux Plus
consultés/Nouveautés sont retirés de l’accueil ; dates de publication, catalogue,
catégories et comptabilisation restent inchangés. Voir [HOME_PAGE.md](../ux/HOME_PAGE.md).

## Décision applicable — créateurs de contenu, 17 octobre 2026

Le [périmètre de lancement](../ux/CONTENT_CREATORS_SCOPE.md) remplace l’ouverture générale aux
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

## Historique — complément du 16 octobre 2026, remplacé sur le périmètre

RM-TAL-012 précise le périmètre éditorial **Talents péi** : personnes et
collectifs, création de contenu, arts et artisanat notamment ; fiches
entreprises et fonctions de prestataires hors rubrique au lancement.
Voir [le cadrage](../ux/TALENTS_PEI_SCOPE.md). RM-30 à 40 restent applicables,
notamment RM-39 pour Contact/email. Les états historiques du catalogue ne
prouvent pas l’application de ce complément ; aucun nouvel audit du code ni
contrôle fonctionnel réalisé. Tableau de bord avec compte reporté ; modalités
sans lien officiel et cas frontières des structures encore ouverts.

## Objet du document

Ce catalogue conserve dans le dépôt les 69 règles suivies dans Notion. Notion
reste l'outil de pilotage ; ce document constitue la trace versionnée des règles,
de leur périmètre, de leur critère d'acceptation et de l'état observé dans le
code à la date du relevé.

Les états d'implémentation proviennent d'une lecture statique du code :

- **À faire** : aucun support concret n'a été trouvé ;
- **En cours** : une partie de la règle existe, mais le critère complet n'est
  pas satisfait ;
- **Implémentée** : le comportement correspondant a été trouvé dans le code ;
- **Testée** : le comportement a été vérifié par des tests reproductibles.

Les règles `RM-03` et `RM-28` sont désormais marquées **Testée** : les dix cas
de la fiche 3 couvrent la normalisation, les doublons et les avertissements.
`RM-06` est également **Testée** depuis le 22 septembre 2026 : les choix
géographiques explicites, l'absence de déduction depuis une commune vide et le
filtre public sont vérifiés dans la fiche 5.

## Sites et classement

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-01 | MVP | En cours | Un site ne peut être publié que s'il possède un nom, une URL valide et accessible, une description neutre et une catégorie principale. | La publication est refusée si l'un des quatre éléments manque ou si l'accessibilité HTTP ne peut pas être confirmée automatiquement ou manuellement. |
| RM-02 | MVP | En cours | Un site référencé satisfait au moins un critère de lien réel avec La Réunion : organisme réunionnais, contenu local régulier, offre nationale spécifique ou ressource particulièrement utile au public réunionnais. | L'administrateur confirme le lien avant publication. La justification et son éventuelle URL de preuve sont facultatives, conservées en privé et jamais affichées au public. |
| RM-03 | MVP | Testée | Une même URL normalisée ne peut être enregistrée qu'une seule fois. La normalisation retire le fragment et les paramètres publicitaires, ignore la casse du domaine, mais conserve la casse du chemin et les paramètres fonctionnels. | Un doublon exact est bloqué lors d'une proposition, d'une création admin ou d'une modification. Les variantes avec et sans `www` ne sont fusionnées automatiquement que si une redirection les relie. |
| RM-04 | MVP | Implémentée | En MVP, un site possède exactement une catégorie principale ; ses autres activités sont décrites dans sa présentation. Les catégories secondaires sont reportées en V2. | Une catégorie principale est obligatoire et aucune catégorie secondaire n'est proposée dans le MVP. |
| RM-05 | V2 | À faire | Seules les catégories actives peuvent être attribuées à un nouveau site ; une catégorie désactivée conserve ses sites existants. | Une catégorie inactive n'apparaît plus dans les formulaires. Une catégorie utilisée ne peut être supprimée sans réaffectation et peut être archivée. |
| RM-06 | MVP | Testée | La localisation d'un site est facultative et distingue une commune du référentiel, `Toute La Réunion`, `En ligne` et `Non précisée`. | Une commune vide signifie `Non précisée`. Les portées `Toute La Réunion` et `En ligne` sont des choix explicites et ne sont jamais déduites d'une valeur vide. |
| RM-07 | MVP | Implémentée | Seuls les sites publiés sont visibles publiquement. | Un site dont le statut n'est pas publié est absent des listes, recherches et classements publics. |
| RM-08 | MVP | En cours | Un site peut être brouillon, en attente, publié, refusé ou archivé. Les transitions autorisées sont `draft` vers `published` ou `archived`, `pending` vers `published` ou `refused`, `published` vers `archived`, `refused` vers `pending` et `archived` vers `published`. | Toute autre transition est refusée. Une correction de proposition peut conserver le statut `pending` et ne déclenche aucune transition implicite. |
| RM-09 | MVP | À faire | Un site fermé, durablement inaccessible, obsolète ou non conforme peut être archivé. | L'archivage retire le site du public sans supprimer son historique ni ses statistiques, et le conserve dans l'administration. |

## Recherche, clics et tendances

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-10 | MVP | En cours | Un visiteur peut rechercher un site par nom, description, catégorie, commune, domaine ou URL et éventuels mots-clés. La recherche ignore les accents, la casse et l'ordre des mots, et accepte les termes partiels. | Une recherche renvoie uniquement les sites publiés et classe d'abord ceux qui correspondent au plus grand nombre de termes. La correction orthographique est hors MVP. |
| RM-11 | MVP | Implémentée | La recherche publique ne retourne que les sites publiés. | Aucun site en attente, refusé, brouillon ou archivé n'apparaît dans les résultats. |
| RM-12 | MVP | En cours | Les résultats peuvent être filtrés par catégorie principale, commune et portée géographique. | Les filtres se combinent avec la recherche et limitent les résultats aux sites publiés respectant simultanément les critères. |
| RM-13 | V1 | En cours | Les résultats peuvent être triés par pertinence, popularité, ordre alphabétique ou date de publication. | Le visiteur peut sélectionner chaque tri et l'ordre affiché correspond au choix. |
| RM-14 | V1 | À faire | Une recherche sans résultat propose des catégories proches ou la proposition d'un nouveau site. | Lorsque la recherche ne retourne rien, au moins une suggestion utile et le lien de proposition sont affichés. |
| RM-15 | MVP | Implémentée | Un clic est comptabilisé uniquement lorsqu'un visiteur utilise le lien sortant géré par Réunion Wiki vers un site publié. | Un clic admissible crée un événement et incrémente une seule fois le compteur du site. |
| RM-16 | MVP | En cours | Les clics des administrateurs authentifiés et des robots identifiés par leur `User-Agent` ne sont pas comptabilisés. | Ces accès ne créent aucun événement, qu'ils proviennent de l'administration, d'une prévisualisation ou de la page publique. |
| RM-17 | MVP | En cours | Les clics répétés d'un même visiteur vers un même site pendant 30 minutes ne comptent qu'une fois. | La déduplication côté serveur utilise un identifiant dérivé de l'adresse IP, du `User-Agent` et du site, sans cookie publicitaire ni conservation inutile de l'adresse IP brute. |
| RM-18 | MVP | En cours | Les tendances sont calculées à partir des clics admissibles : tendance sur 7 jours, progression par comparaison avec les 7 jours précédents et popularité stable sur 30 jours. | Chaque indicateur utilise sa période définie ; un site sans clic reste absent des classements principaux, mais demeure visible dans les nouveautés et sa catégorie. |
| RM-19 | MVP | Implémentée | Seuls les sites publiés peuvent apparaître dans les tendances. | Aucun site non publié n'est présent dans les classements calculés. |
| RM-20 | MVP | Testée | Une proposition, une première publication, une publication utilisée pour les nouveautés et une modification possèdent des dates distinctes : `submitted_at`, `first_published_at`, `published_at` et `updated_at`. | `first_published_at` ne change jamais. `published_at` n'est renouvelée que par l'action explicite « Traiter comme une nouvelle publication », jamais sélectionnée par défaut. |
| RM-21 | MVP | Testée | Les derniers sites ajoutés sont classés du plus récemment publié au plus ancien à partir de `published_at`. | Une republication normale ne replace pas le site dans les nouveautés. Une nouvelle publication explicite actualise `published_at`, sans effacer les clics ni l'historique. |

## Proposition et modération des sites

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-22 | MVP | Implémentée | Un visiteur peut proposer un site sans compte administrateur. | Le formulaire public peut être envoyé sans authentification. |
| RM-23 | MVP | En cours | Une proposition exige le nom, l'URL, la description et la catégorie principale. La commune ou portée, la justification du lien réunionnais, son éventuelle URL de preuve et l'email restent facultatifs. | L'envoi est refusé lorsqu'un des quatre champs obligatoires manque et accepte les autres champs vides. La justification privée n'est pas rendue publique. |
| RM-24 | MVP | Implémentée | Les coordonnées éventuelles du proposant ne sont jamais publiques. | Aucune coordonnée du proposant n'est rendue dans les pages publiques. |
| RM-25 | MVP | Implémentée | Toute proposition publique reçoit le statut en attente. | Après un envoi valide, le site est enregistré en attente de modération. |
| RM-26 | MVP | Implémentée | Une proposition n'est jamais publiée automatiquement. | Le site reste invisible jusqu'à une action volontaire d'un administrateur. |
| RM-27 | MVP | Implémentée | Un administrateur peut modifier, accepter ou refuser une proposition. | Chaque action est accessible dans l'administration et modifie le statut ou les données attendus. |
| RM-28 | MVP | Testée | Une URL normalisée déjà enregistrée est bloquée avant l'enregistrement, quel que soit son statut. Un domaine déjà connu avec un chemin différent produit un avertissement admin. | Le contrôle est exécuté lors de la proposition publique, de la création admin et de la modification de l'URL. |
| RM-29 | V1 | À faire | Le proposant peut être informé manuellement ou automatiquement de la décision lorsqu'il a fourni un email. | L'email n'est jamais public. Le MVP peut fonctionner sans notification automatique et permettre une réponse manuelle. |

## Talents réunionnais

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-30 | MVP | Implémentée | Un talent possède un nom ou pseudonyme, une présentation et une catégorie principale. | L'enregistrement est refusé si l'un de ces éléments manque. |
| RM-31 | MVP | À faire | Selon RM-TAL-003 v2.0, un talent publié possède un rattachement réel vérifié avec une source simple conservée en privé. Plusieurs rattachements/sources restent possibles ; brouillon incomplet admis. | Publication refusée sans rattachement ni source enregistrée. Référence identifiable et lien conservés en privé avec une courte note ; aucun affichage public de source obligatoire au lancement. Décision validée, backend non vérifié. |
| RM-32 | MVP | En cours | Un talent peut être associé facultativement à Instagram, YouTube, TikTok, Facebook, Twitch ou un site officiel. Une page SEO Twitch n'est pas exigée dans le MVP. | Chaque plateforme accepte une URL HTTP ou HTTPS valide. Une fiche publiée avec une URL Twitch affiche ce lien et apparaît dans le filtre Twitch. |
| RM-33 | MVP | Implémentée | Toute URL de plateforme renseignée doit être valide. | Une URL sans protocole HTTP ou HTTPS ou sans domaine est refusée. |
| RM-34 | MVP | Implémentée | Une plateforme ne peut apparaître qu'une seule fois sur une même fiche. | Une fiche ne conserve qu'une URL par plateforme. |
| RM-35 | MVP | Implémentée | La commune d'un talent est facultative. | Une fiche peut être enregistrée sans commune ; une valeur renseignée doit exister dans le référentiel. |
| RM-36 | MVP | Implémentée | En MVP, un talent possède une seule catégorie principale ; ses autres activités sont décrites dans sa présentation. Les catégories secondaires sont envisagées en V2. | Une fiche publiée référence exactement une catégorie principale. |
| RM-37 | MVP | Implémentée | Seules les fiches talents publiées sont visibles dans l'espace public. | Une fiche brouillon ou archivée est absente de l'index et son URL publique retourne une page introuvable. |
| RM-38 | Plus tard | En cours | Une fiche peut être publiée sans portrait. La gestion structurée de la provenance et des autorisations est reportée ; une image spécifique reste soumise à une vérification manuelle de ses droits. | Dans le MVP, l'absence d'image n'empêche pas la publication et déclenche l'image générique. Aucun portrait tiers non justifié n'est rendu obligatoire par le parcours. |
| RM-39 | MVP | En cours | Un talent peut demander par contact ou email la correction, l'archivage ou le retrait de sa fiche ; seul un administrateur applique la modification après une vérification raisonnable de l'identité. | La demande conserve de manière privée sa date, son motif, la décision et l'action. Une correction maintient la fiche, un archivage la masque en conservant l'historique et un retrait arrête sa publication. |
| RM-40 | MVP | En cours | Les fiches publiées peuvent être recherchées par nom affiché, pseudonyme ou présentation et filtrées par catégorie principale ou plateforme. | La recherche et les filtres peuvent être combinés, n'exposent que les fiches publiées et affichent en l'absence de résultat une action de réinitialisation. |

### Portée juridique de RM-38

La mise en ligne dite « temporaire », le lancement expérimental du service,
l'absence de réponse de la personne représentée, la disponibilité publique de
l'image ou la seule mention d'un crédit ne constituent pas une autorisation
d'utilisation. La durée limitée de diffusion ne supprime ni le droit d'auteur
attaché à la photographie ni, selon le contexte, les droits de la personne
représentée.

En conséquence, la phase de lancement ne crée aucune exception à RM-38. En
l'absence de preuve suffisante, la fiche peut être publiée sans portrait avec
l'image générique Réunion Wiki. Une image spécifique déjà publiée sans base
d'utilisation documentée doit être retirée sans délai dès son identification ou
à la première contestation, dans l'attente d'une régularisation éventuelle.

Cette règle et son choix de lancement sont détaillés dans
[`ADR-002`](../decisions/ADR-002-droits-images-talents-au-lancement.md).

## Articles, FAQ et présentation

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-41 | V1 | En cours | Un article possède un titre, un contenu, un auteur, une date de publication et un statut. | L'article ne peut être publié sans ces informations et les affiche correctement. |
| RM-42 | V1 | Implémentée | Seuls les articles publiés sont accessibles publiquement. | Une URL de contenu brouillon ou archivé retourne une page introuvable. |
| RM-43 | V1 | Implémentée | Un article peut être enregistré en brouillon avant publication. | L'enregistrement d'un brouillon réussit sans rendre le contenu public. |
| RM-44 | V1 | À faire | Les articles publiés sont affichés du plus récent au plus ancien. | La page blog liste uniquement les articles publiés par date de publication décroissante. |
| RM-45 | V2 | À faire | Une entrée de FAQ possède une question, une réponse et un ordre d'affichage. | L'administrateur peut renseigner ces trois éléments et l'ordre public est respecté. |
| RM-46 | V2 | À faire | Seules les entrées de FAQ actives sont affichées. | Une FAQ désactivée disparaît du public sans être supprimée. |
| RM-47 | MVP | En cours | Une page de présentation explique l'objectif de Réunion Wiki et ses critères de référencement. | Le visiteur peut consulter une page dédiée exposant clairement ces deux informations. |

## Contact

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-48 | MVP | En cours | Le formulaire de contact demande un nom, un email valide, un sujet et un message. | L'envoi est refusé si un champ obligatoire manque ou si l'email est invalide. |
| RM-49 | MVP | En cours | L'utilisateur accepte le traitement de ses données avant l'envoi. | Une case non précochée est obligatoire et bloque l'envoi tant qu'elle n'est pas acceptée. |
| RM-50 | V1 | En cours | Un message de contact possède une date et un statut : nouveau, lu, traité ou archivé. | Chaque message reçoit automatiquement une date et un statut initial nouveau, puis peut changer de statut. |
| RM-51 | MVP | En cours | Les messages de contact ne sont accessibles qu'aux administrateurs autorisés. | Un utilisateur non authentifié ne peut ni lister ni lire les messages. |
| RM-52 | MVP | En cours | Le formulaire de contact est protégé contre le spam et les envois excessifs. | Les soumissions automatisées ou dépassant la limite prévue sont refusées. |

Les règles RM-48 à RM-52 sont actuellement partiellement externalisées dans
Google Forms. Leur passage à **Implémentée** exige une vérification du formulaire,
de ses réponses, de ses permissions et de sa politique de conservation.

## Administration et intégrité

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-53 | MVP | Implémentée | L'administration nécessite une authentification. | Toute route admin redirige un visiteur non authentifié vers la connexion. |
| RM-54 | MVP | En cours | Seuls les administrateurs autorisés peuvent gérer les sites, talents, contenus et référentiels. | Chaque opération de création, lecture privée, modification, publication, archivage ou suppression est protégée. |
| RM-55 | MVP | Implémentée | Une catégorie utilisée ne peut pas être supprimée avant réaffectation ; son archivage reste possible. | La suppression est refusée tant qu'au moins un site ou talent utilise la catégorie. |
| RM-56 | V1 | À faire | Une commune ou une plateforme utilisée ne peut pas être supprimée sans traitement explicite de ses relations. | L'administration exige une réaffectation, une suppression des relations ou une confirmation adaptée avant la suppression. |
| RM-57 | MVP | Implémentée | Toute suppression définitive demande une confirmation explicite. | L'utilisateur doit confirmer l'action avant l'envoi de la suppression. |
| RM-58 | MVP | En cours | L'archivage est préféré lorsque la suppression ferait perdre un historique ou des statistiques. Pour un site, la suppression définitive est réservée aux doublons, erreurs de saisie, contenus illégaux ou demandes légitimes l'exigeant. | L'archivage retire l'élément du public tout en conservant ses données ; la suppression reste une action exceptionnelle et distincte. |
| RM-59 | V2 | À faire | Les actions administratives sensibles sont journalisées. | Une entrée durable conserve l'administrateur, l'action, la cible et la date. |
| RM-60 | V1 | En cours | Le tableau de bord affiche au minimum les propositions en attente, les messages non traités, les sites publiés et les clics. | Les quatre indicateurs sont visibles et correspondent aux données enregistrées. |

## Obligations légales et règles complémentaires

| ID | Périmètre | Implémentation | Règle | Critère d'acceptation |
| --- | --- | --- | --- | --- |
| RM-61 | MVP | Implémentée | Les mentions légales identifient l'éditeur, le responsable de publication et l'hébergeur. | Ces informations sont présentes et accessibles depuis toutes les pages. |
| RM-62 | MVP | À faire | La politique de confidentialité décrit les données collectées, leur finalité et leur durée de conservation. | Le document couvre notamment les formulaires, les adresses IP, les User-Agents, les destinataires et les durées. |
| RM-63 | MVP | En cours | Toute personne peut demander l'accès, la rectification ou la suppression de ses données personnelles. | Un canal documenté permet de recevoir, vérifier, traiter et tracer chaque demande. |
| RM-64 | MVP | Implémentée sous réserve | Aucun cookie non essentiel n'est déposé avant le consentement du visiteur. | Sans consentement, seuls les cookies strictement nécessaires sont présents ; l'ajout d'un cookie non essentiel déclenche un mécanisme de consentement. |
| RM-65 | MVP | En cours | Les formulaires ne collectent que les données nécessaires à leur finalité. | Chaque champ collecté possède une finalité documentée et aucun champ superflu n'est obligatoire. |
| RM-66 | MVP | Implémentée | Un visiteur peut signaler un lien mort, inapproprié ou obsolète. | La FAQ ou la fiche fournit un canal de signalement permettant d'identifier l'URL et le problème. |
| RM-67 | MVP | Implémentée | Réunion Wiki précise que les éditeurs externes restent responsables de leurs sites. | Une clause visible indique que Réunion Wiki ne contrôle pas le contenu des sites externes. |
| RM-68 | MVP | À faire | Un site peut utiliser les portées fonctionnelles `En ligne` ou `Toute La Réunion`, distinctes d'une commune et de `Non précisée`. | Chaque portée peut être choisie explicitement, filtrée publiquement et distinguée d'une commune vide. |
| RM-69 | MVP | Implémentée | Les administrateurs peuvent consulter le nombre de clics par site et supprimer un événement incorrect. | La liste ou la fiche admin affiche le compteur ; la suppression d'un événement ajuste également ce compteur. |

## Résumé du relevé d'implémentation

| État | Nombre de règles |
| --- | ---: |
| Implémentée | 25 |
| Implémentée sous réserve | 1 |
| En cours | 28 |
| À faire | 13 |
| Testée | 2 |

## Règles détaillées complémentaires

Les règles `RM-TAL-001` à `RM-TAL-011` du document parent précisent les choix
éditoriaux applicables aux talents. Les règles `RM-SITE-001` à `RM-SITE-012` du
document [`SITE_RULES.md`](SITE_RULES.md) précisent les choix applicables aux
sites. Elles ne remplacent pas les identifiants Notion : elles les détaillent
et sont reliées comme suit.

| Catalogue | Détail éditorial |
| --- | --- |
| RM-31 | RM-TAL-001, RM-TAL-002 et RM-TAL-003 |
| RM-38 | RM-TAL-004 |
| RM-30 | RM-TAL-005 |
| RM-37 | RM-TAL-006 |
| RM-39 | RM-TAL-007 |
| RM-32 à RM-34 | RM-TAL-008 |
| RM-40 | RM-TAL-009 |
| RM-30, RM-31, RM-33 et RM-37 | RM-TAL-010 |
| Parcours pilote talents | RM-TAL-011 |
| RM-02 | RM-SITE-001 |
| RM-01 | RM-SITE-002 |
| RM-03 et RM-28 | RM-SITE-003 |
| RM-04, RM-05 et RM-55 | RM-SITE-004 |
| RM-06 et RM-68 | RM-SITE-005 |
| RM-07 à RM-09 et RM-58 | RM-SITE-006 |
| RM-10 à RM-14 | RM-SITE-007 |
| RM-15 à RM-19 et RM-69 | RM-SITE-008 |
| RM-20 et RM-21 | RM-SITE-009 |
| RM-22 à RM-29 | RM-SITE-010 |
| RM-01 à RM-03, RM-05 et RM-06 | RM-SITE-011 |
| Parcours pilote sites | RM-SITE-012 |

## Remplacement de RM-31 — 7 octobre 2026

La définition antérieure (versions du catalogue jusqu'à 1.3) exigeait une source
publique affichée avec type, titre/description, URL et organisme. Elle est
remplacée par RM-TAL-003 v2.0 : vérification légère et référence conservée en
privé au lancement. Le texte ancien de la règle et son amendement sont conservés
avec statut Remplacée dans BUSINESS_RULES.md. Aucune exigence de rattachement
réel ou de contrôle avant publication n'est supprimée.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.7 | 17 octobre 2026 | Révision après essai utilisateur : carrousel accueil mobile, retrait des deux blocs de sites et des tendances publiques ; choix et limites tracés. |
| 1.6 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 1.5 | 16 octobre 2026 | Lien RM-TAL-012 et périmètre Talents péi ; états de réalisation historiques conservés, aucun test métier exécuté. |
| 1.4 | 7 octobre 2026 | RM-31 alignée sur RM-TAL-003 v2.0 après décision 2A : source privée, affichage public non obligatoire ; implémentation non déclarée. |
| 1.3 | 16 septembre 2026 | Précision des transitions, contrôles HTTP, règles de normalisation et de recherche, identification des clics répétés et dates de republication. Les états d'implémentation sont réévalués selon ces critères plus stricts. |
| 1.2 | 16 septembre 2026 | Intégration des décisions validées pour l'annuaire des sites et alignement des périmètres, critères d'acceptation et états d'implémentation sur les règles détaillées `RM-SITE`. |
| 1.1 | 15 septembre 2026 | Intégration des réponses validées pour RM-31, RM-32, RM-38, RM-39 et RM-40, et report de la gestion structurée des images. |
| 1.0 | 14 septembre 2026 | Première transcription complète des 69 règles, ajout des périmètres, critères d'acceptation et états issus de l'audit du code. |
