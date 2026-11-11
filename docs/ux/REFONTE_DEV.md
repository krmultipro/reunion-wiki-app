# Refonte DEV — périmètre validé le 11 novembre 2026

Version 1.2 — décisions utilisateur validées, implémentation et recette locale réalisées.
Publication DEV attestée séparément par le journal de release et les labels d’image.

## Sources et choix applicables

L’utilisateur autorise l’intégration de la maquette comme nouvelle version de Réunion Wiki, puis sa livraison sur dev.reunionwiki.re. Source visuelle : `maquettes/mobile-final/` et son repli ordinateur existant, avec les compléments documentés dans FINAL_MOBILE_MOCKUP.md. La variante PC isolée et l’aperçu éditorial privé ne sont pas fusionnés implicitement dans cette référence. Les données viennent de SQLite ; le catalogue statique et sessionStorage ne deviennent pas le backend.

Le 11 novembre, l’utilisateur accepte le report après cette intégration DEV de la recherche avancée (commune/domaine/URL, filtres géographiques, tris), du filtre plateforme/Twitch, des fonctions admin avancées (photos/réseaux, communes, contenus éditoriaux, correction clics), de la nouvelle présentation du projet et des articles. La confidentialité détaillée et le traitement complet des demandes sont à terminer avant ouverture publique et collecte réelle. Ces fonctionnalités restent dans le cahier des charges ; elles ne conditionnent pas cette première refonte DEV.

Restent indispensables dès cette étape : consultation et recherche simple, catégories, fiches, propositions Site/Personnalité sans compte avec erreurs/doublons/confirmation réelle, administration authentifiée permettant examen/modification/refus/brouillon/publication distincte/archivage, non-public et données privées protégés, FAQ/Contact/mentions et liens de retour. Pas de compte contributeur ni de notification réelle ajouté. Les capacités backend existantes peuvent rester disponibles sans imposer leur ancienne interface.

La fiche admin dédiée antérieure est insuffisante : le présent document fixe le périmètre d’intégration aux actions explicitement simulées dans la référence, en réutilisant les validations métier existantes. Aucun nouveau parcours ouvert n’est inventé. Nom public Personnalités réunionnaises, tutoiement, ressources locales et URLs existantes conservés. La fiche pilote privée et son portrait ne sont pas importés ou publiés ; les données ne sont pas attribuées à une catégorie par supposition.

## Contrats des parcours

- Visiteur : accueil → liste ou recherche groupée → fiche publiée → retour avec critères ; catégories combinées à recherche simple, alphabet des listes. Les liens sortants des sites passent par le compteur serveur existant. Aucun contenu draft/archive dans listes, détails, recherche ou sitemap.
- Proposition : type Site/Personnalité → validation serveur → doublon public avec accès utile ou message neutre si non-public → attente privée → confirmation. Nom/lien/catégorie/description obligatoires Site ; nom/lien officiel obligatoires Personnalité ; email facultatif privé. Ni photo ni compte requis. POST/Redirect/GET et réessai sans faux succès.
- Administration : connexion → file mixte → vérifier/compléter → refus avec motif ou préparation d’un brouillon → publication distincte contrôlée → correction ou archivage. Sources et rattachements de personnalité privés, vérifiés avant publication. Brouillon initial imposé côté service. Reprise d’un contenu publié existant n’invente pas rétroactivement une source ; nouvelle publication/republication doit respecter les contrôles.
- Contacts : page explicative et accès au canal existant, sans simulation d’envoi ni promesse de délai. Accès correction/retrait depuis fiche. Compteurs contacts externes non inventés.

## Critères d’acceptation avant code

1. Cadre crème/vert, logo/hero/dock/cartes/footer de la maquette présents sur les pages cibles, sans outils de démonstration ni liens de versions ; ressources locales complètes.
2. Données SQLite effectivement affichées sur accueil/listes/recherche/fiches ; critères URL/restauration des retours, 0 résultat, nom long, image absente/cassée, sans réseau.
3. Proposition minimale valide des deux types → réception privée persistante et confirmation → action admin ; erreurs conservent champs, doublon non-public ne révèle ni ID ni statut, aucune publication automatique.
4. Auth/CSRF sur mutations, validation service, brouillon forcé, publication séparée, refus motivé et archivage. Sources/emails/portraits non autorisés absents du public et de ses caches. Rendu texte échappé, pas de HTML arbitraire.
5. Syntaxe et tests métier/intégration sur bases temporaires ; démarrage Flask/Gunicorn, parcours navigateur mobile/PC et 320px sans débordement/dock masquant ; limites de téléphone réel explicitement signalées si non disponible.
6. Migration additive et répétable sur copie DEV, sauvegarde DB+uploads restaurée isolément avant écriture active. Jamais de remplacement de base active par celle du PC.
7. Branche dédiée → version testée fusionnée dans `dev` → artefact exact de ce commit et déploiement DEV contrôlé. Branche `main` et production hors livraison. Pas de maquette privée, photo originale, secrets/base/backup dans Git ou contexte Docker.

## Traçabilité

RM-10/12/13 et RM-32/40 : compléments d’interface reportés pour ce jalon DEV, règles historiques conservées. RM-22 à 28, RM-30/31/33/36/37/39, RM-TAL-006/010 et UX-PROP/UX-FICHE/UX-FINAL : socle applicable. RM-41 à 47 et extensions admin : report de présentation/édition avancée, pas suppression des contenus. RM-62/63 : finalisation avant ouverture publique, confidentialité effective immédiate.

Réalisation et preuves seront ajoutées après les contrôles ; aucun test n’est déclaré passé par cette fiche préalable.

## Précisions d’implémentation dans le périmètre validé

- Sélection Sites accueil reprise de la maquette (87,65,81), configurable par
  `HOME_FEATURED_SITE_IDS` ; seuls les sites encore publiés sont retenus,
  remplissage alphabétique comme dans la référence si une sélection manque.
  Ce choix ne crée ni rotation ni classement par nouveautés.
- `/recherche` devient la recherche simple groupée. Le moteur avancé existant
  reste à `/recherche-sites` pour compatibilité/test, sans panneau ajouté au
  nouveau parcours. Les tests avancés sont réorientés sur cette entrée.
- Médias : lecture publique seulement si référencés par une fiche ou contenu
  publié ; lecture authentifiée pour les brouillons, sans cache public.
- Champs privés de vérification ajoutés aux talents sans attribution fictive
  aux fiches historiques. Toute nouvelle publication et toute sauvegarde d’une
  fiche publiée exigent rattachement/source ; simple consultation des fiches
  déjà publiées conservée.
- Formulaire minimal de personnalité prépare un brouillon séparé avec nom,
  présentation et catégorie vérifiés ; la proposition initiale reste minimale
  (nom/lien). La sélection de catégorie se fait explicitement en administration.

- Partage simple de fiche selon UX-SHARE-001 : menu avec lien canonique propre
  et copie réelle du lien ; repli sélection manuelle si presse-papiers refusé.
  Aucun partage natif, notification ou succès simulé.

Preuves locales du 11 novembre : voir [recette et limites](../testing/REFONTE_DEV_2026-11-11.md).

## Complément utilisateur — ajout d’un contenu préparé sur DEV

Le 11 novembre, après la livraison initiale, l’utilisateur demande explicitement
d’ajouter la fiche préparée dans l’aperçu privé et sa photo à la base DEV, avec
le fonctionnement branche dédiée depuis `dev` → contrôles/commit → fusion `dev`
→ publication DEV. Cette demande remplace l’exclusion d’import ci-dessus pour
cette seule fiche ; elle n’autorise aucune publication en production ni aucun
ajout du portrait ou du catalogue privé dans GitHub.

Il s’agit d’une saisie de contenu par les services existants : brouillon puis
publication distincte dans la base DEV protégée par Basic. Le texte et les liens
déjà préparés sont repris ; aucune commune ni information biographique n’est
inventée. Une catégorie existante doit être choisie explicitement, conformément
à RM-30/36 et à la contrainte actuelle du modèle. La mise en page commune DEV
reste utilisée ; la variante grand portrait/gras de l’aperçu privé n’est pas une
nouvelle modification d’interface dans cette demande d’ajout en base.

Procédure et critères : [ajout de contenu DEV](../development/DEV_PROFILE_CONTENT_2026-11-11.md).
