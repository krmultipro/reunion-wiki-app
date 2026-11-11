# Documentation Réunion Wiki

Ce dossier constitue la documentation versionnée du projet selon une approche
**Docs as Code**.

## Source de vérité

- Notion sert à réfléchir, organiser et piloter le travail.
- Les fichiers Markdown du dépôt décrivent les décisions validées qui doivent
  être respectées par l'application.
- En cas de contradiction, la dernière version validée dans le dépôt fait foi.

## Documents principaux

- [`PRODUCT.md`](PRODUCT.md) : vision, périmètre et exigences du produit.
- [`BUSINESS_RULES.md`](BUSINESS_RULES.md) : règles métier et critères
  d'acceptation.
- [`business-rules/RULES_CATALOG.md`](business-rules/RULES_CATALOG.md) :
  catalogue complet des 69 règles, périmètres et états d'implémentation.
- [`business-rules/SITE_RULES.md`](business-rules/SITE_RULES.md) : règles
  détaillées du référencement, de la modération et du classement des sites.
- [`EDITORIAL_GUIDE.md`](EDITORIAL_GUIDE.md) : point d'entrée du guide
  éditorial.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) : point d'entrée de la documentation
  technique.
- [`decisions/`](decisions/README.md) : décisions importantes et ADR.

## Documentation spécialisée

- [`ux/ADMIN_SITES_LAYOUT.md`](ux/ADMIN_SITES_LAYOUT.md) : choix A validé pour
  corriger la liste admin écrasée ; tableau PC, défilement local et filtres souples.
  [Recette avant/après](testing/ADMIN_SITES_LAYOUT_2026-11-11.md).

- [`development/CACHE_DEV_2026-11-11.md`](development/CACHE_DEV_2026-11-11.md) :
  correctif du cache des fichiers publics et logo léger, critères, schéma,
  régressions de confidentialité et preuves de livraison DEV.

- `testing/README.md` résume l'environnement, l'état des tests et la procédure
  de reprise dans une nouvelle conversation.
- `testing/GLOBAL_TEST_STRATEGY.md` cartographie les familles couvertes et
  manquantes, leurs risques, leurs priorités et leur ordre de réalisation.
- `editorial/EDITORIAL_GUIDE.md` explique comment rédiger les fiches et les
  contenus avec un ton neutre.
- `editorial/CONTENT_GUIDE.md` explique comment publier les contenus SEO.
- `architecture/README.md` indexe les diagrammes techniques.
- `development/AGENTS.md` décrit les pratiques de développement.
- `development/SOCIAL_SEO_GUIDES.md` documente les guides SEO sociaux.
- `development/VPS_DEV_ROUTING.md` documente le routage Docker/Nginx de
  `dev.reunionwiki.re`, sa vérification et son retour arrière.
- `ux/README.md` conserve les décisions UX transversales validées.
- `ux/PUBLIC_SEARCH.md` décrit le comportement attendu de la recherche, des
  filtres et des tris publics.
- `testing/TALENT_TEST_CASES.md` conserve les cas de test fonctionnels du
  parcours des talents et leur suivi d'exécution.
- `testing/SITE_TEST_CASES.md` conserve les cas de test prioritaires du parcours
  des sites, leur ordre d'automatisation et leur suivi d'exécution.

- [`development/SITE_SUBMISSION_CORRECTIONS_2026-10-26.md`](development/SITE_SUBMISSION_CORRECTIONS_2026-10-26.md) : corrections locales du parcours de soumission, règles, schémas, tests et limites avant intégration.

## Règles de modification

Une décision validée ne doit jamais disparaître silencieusement.

1. Une correction de forme peut modifier directement le document.
2. Une précision sans changement de sens augmente la version mineure du
   document et ajoute une ligne à son historique.
3. Un changement de sens crée une nouvelle version de la règle ou un ADR qui
   indique explicitement ce qu'il remplace.
4. Une règle remplacée reste visible avec le statut `Remplacée` et un lien vers
   la nouvelle décision.
5. Un ADR accepté n'est pas réécrit : une nouvelle décision le remplace.
6. Git conserve le texte exact de chaque ancienne version.

La convention complète est enregistrée dans
[`ADR-001`](decisions/ADR-001-documentation-as-code-et-tracabilite.md).

## Refonte DEV — 11 novembre 2026

- [Périmètre validé, reports et parcours essentiels](ux/REFONTE_DEV.md).
- [Vérifications de la refonte et limites](testing/REFONTE_DEV_2026-11-11.md).
- [Maquette mobile finale de référence](ux/FINAL_MOBILE_MOCKUP.md).
- [Routage, publication et restauration DEV](development/VPS_DEV_ROUTING.md).
