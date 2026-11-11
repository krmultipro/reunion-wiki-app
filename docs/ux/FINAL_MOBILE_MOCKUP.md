# Maquette mobile finale — consolidation du 23 octobre 2026

## Partage de fiche simulé — 26 octobre 2026

Choix initiaux **1A/2A/3A**, puis correction explicite après essai : **après les
liens officiels**, l’action texte discrète **Partager cette fiche** ouvre un menu fictif avec nom, phrase
et lien local nettoyé. Aucun partage réel ni copie du presse-papiers.
[Décision UX-SHARE-001](PROFILE_SHARING.md) ·
[Réalisation, preuves et limites](../testing/PROFILE_SHARING_REVIEW_2026-10-26.md).

## Complément du 26 octobre 2026 — logo et notifications de démonstration

Intégration explicitement demandée par l’utilisateur : R retenu dans le cadre
partagé et deux notifications déclenchables dans les outils de la maquette.
[UX-ICON-001 v1.1](APP_ICON.md) et [UX-PUSH-002 v1.0](PWA_NOTIFICATIONS.md)
décrivent la portée, les destinations et les critères avant modification.
Ce complément porte uniquement sur `maquettes/mobile-final/`, sans push réel,
intégration Flask ou changement des anciennes variantes.
[Intégration locale vérifiée et limites](../testing/NOTIFICATIONS_LOGO_REVIEW_2026-10-26.md).

### UX-FINAL-002 v1.0 — paysage sur le cadre public

Complément explicite du 26 octobre : « mets la bannière hero derrière le titre
sur page site et personnalité et autres ». Étendre le paysage déjà retenu pour
l’accueil derrière le titre Réunion Wiki du cadre partagé à toutes les pages
publiques de cette version : Sites, Personnalités, fiche, recherche, proposition,
confirmation, FAQ, Contact et mentions légales. Même photo locale, voile clair,
position et arrondis ; titres de contenu conservés dans le corps de page.
La page de modération garde son cadre administratif. Aucun changement des
anciennes variantes ou du site Flask. Contrôler au moins Sites et Personnalités
sur mobile ainsi que la fiche et le repli ordinateur.

## Autorisation et périmètre

**UX-FINAL-001 v1.0.** Après le constat des écarts publics/modération,
l’utilisateur demande de remettre la maquette finale au propre. Réaliser une
version isolée `maquettes/mobile-final/`, en conservant les variantes existantes.
Cette demande autorise la maquette et ses simulations, pas une intégration Flask,
une migration, des emails ou un déploiement du site réel.

Références : HOME_PAGE (Pacifico 32 px, sites puis personnalités, navbar retenue),
SITE_LIST UX-SITES-007 (catégories visibles), CREATOR_LIST UX-CREA-009/010
(catégories et descriptions de deux lignes), HOME_SEARCH, CREATOR_PROFILE,
UNIFIED_SUBMISSION, ADMIN_MOCKUP V1, SUPPORT_PAGES. La fiche de consolidation
manquait ; ce document relie ces choix avant les modifications dépendantes.

## Choix de consolidation dans le périmètre autorisé

- Même présentation publique retenue ; pas de refonte graphique. Pacifico
  agrandie, crème/vert, cartes et navbar conservés. Les outils de démonstration
  sont regroupés à part du contenu public plutôt que dispersés dans les pages.
- Un seul instantané de 56 sites et 29 personnalités publiées sert à l’accueil,
  la recherche, les catégories et les fiches. Champs publics déjà présents,
  sans biographie ou classement inventé ; portraits facultatifs et silhouettes.
- Les fiches de personnalités du parcours final sont locales et exploitent
  uniquement les informations publiques disponibles ; liens officiels externes
  annoncés, origine de retour limitée aux pages autorisées avec critères gardés.
- Proposition publique **sans compte** au lancement : règles existantes, erreurs,
  doublon public/privé, confirmation explicitement simulée. La demande d’essai
  peut rejoindre la file de modération du même onglet, en mémoire de session.
  Aucune donnée n’est envoyée ; les outils demandent d’utiliser des exemples.
- Admin essentiel V1 selon les arbitrages déjà validés : connexion/déconnexion
  simulées, tableau de bord, propositions, sites, personnalités, catégories,
  clics illustratifs et Contact externe. Reprendre le style admin existant.
- Proposition → examen → correction du type si nécessaire → brouillon distinct
  → contrôles illustratifs et récapitulatif → publication, ou refus avec motif.
  Publication et archivage modifient seulement la visibilité du catalogue de
  démonstration dans le même onglet. Historique des décisions conservé.
- Catégories : référentiels Sites/Personnalités distincts, renommage gardant le
  slug, suppression inutilisée confirmée et suppression utilisée bloquée. Ce
  sont des actions de simulation ; aucune taxonomie réelle n’est modifiée.
- La source originale demeure les instantanés publics ; les modifications de
  démonstration sont isolées dans une clé `sessionStorage` dédiée à cette
  version. Rechargement conservé dans l’onglet, reset confirmé ; ce stockage
  temporaire n’est pas une sauvegarde ni une source de production.

## Questions conservées, sans décision implicite

- Catégories Personnalités et leurs chevauchements : ticket #46, sans fusion
  ni réaffectation lors de cette consolidation.
- Admissibilité artistes/sportifs et collectifs : UX-CONT-007, toujours ouverte ;
  la reprise de fiches déjà publiées n’établit pas de nouveaux critères métier.
- Compte contributeur : maquette séparée, évolution ultérieure, non ajouté au
  lancement public. Les demandes de complément/corrections versionnées de cette
  évolution ne deviennent pas des écrans obligatoires du MVP sans compte.
- Contact réel Google : #24, lien conservé sans envoi ni édition du formulaire.
- Normalisation réelle des URLs sociales, sécurité/authentification, transactions,
  stockage serveur et tests backend : #18/#7/#8/#9, hors de cette maquette.
- Pas de pagination mobile ajoutée : elle reste une proposition à décider.

## Critères avant réalisation et clôture technique

1. Accueil, recherche Bus.re/Adriana et annuaires utilisent les mêmes données ;
   aucun lien de carte vers une fiche locale inexistante ou un site fictif.
2. Filtres, q, origine de retour et historique restent cohérents ; noms longs,
   texte court avec ellipse, absence de portrait, zéro résultat et erreur traités.
3. Proposition site valide et personnalité minimale → confirmation → file admin
   du même onglet ; aucun envoi réel. Champs invalides/doublons bloquent l’action.
4. Examen, correction de type, brouillon, contrôles de publication, refus motivé,
   publication et archivage simulés avec transitions et historique vérifiables.
5. Une proposition ou un brouillon ne sont pas visibles publiquement ; une
   publication de démonstration apparaît, un archivage la retire du catalogue.
6. Les catégories gardent leur slug lors d’un renommage ; suppression utilisée
   bloquée. Les statistiques sont des agrégats fictifs avec période affichée.
7. Vérifier 320/390 px effectifs, clavier et focus, absence de débordement, contenu
   accessible au-dessus du dock ; contrôler un écran plus large en repli.
8. Les anciennes variantes restent disponibles, Montserrat conservée pour plus
   tard ; comparaison datée, ressources locales et liens vérifiés.
9. Documentation, preuves et suivi #14/#34 reflètent ce qui est réellement
   vérifié. La clôture technique de la maquette ne vaut ni validation utilisateur
   de tous les nouveaux écrans ni disponibilité du parcours réel.
