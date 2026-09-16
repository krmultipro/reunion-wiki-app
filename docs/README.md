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

- `editorial/EDITORIAL_GUIDE.md` explique comment rédiger les fiches et les
  contenus avec un ton neutre.
- `editorial/CONTENT_GUIDE.md` explique comment publier les contenus SEO.
- `architecture/README.md` indexe les diagrammes techniques.
- `development/AGENTS.md` décrit les pratiques de développement.
- `development/SOCIAL_SEO_GUIDES.md` documente les guides SEO sociaux.
- `testing/TALENT_TEST_CASES.md` conserve les cas de test fonctionnels du
  parcours des talents et leur suivi d'exécution.
- `testing/SITE_TEST_CASES.md` conserve les cas de test prioritaires du parcours
  des sites, leur ordre d'automatisation et leur suivi d'exécution.

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
