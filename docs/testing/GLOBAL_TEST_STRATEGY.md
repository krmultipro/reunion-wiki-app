# Stratégie globale de tests — Réunion Wiki

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.2 |
| Statut | Référence active |
| Dernière mise à jour | 24 septembre 2026 |
| Périmètre | Application publique, administration, données et déploiement |

## Objectif

Ce document donne une vue globale de la couverture de tests. Il complète les
cas détaillés des sites et des talents sans les dupliquer. Il sert à choisir les
prochains chantiers, à suivre leur état et à éviter qu'une fonctionnalité soit
considérée comme terminée sur la seule base de ses règles métier.

Un écran peut répondre avec un code HTTP `200` tout en étant inutilisable. Une
route peut aussi afficher correctement son interface tout en acceptant une
transition métier interdite. La stratégie combine donc plusieurs niveaux de
contrôle.

## États de suivi

- **Validé** : couverture reproductible suffisante pour le risque suivi.
- **Partiel** : certains comportements sont testés, mais des risques importants
  restent sans contrôle.
- **Documenté** : les cas existent, mais ne sont pas encore automatisés.
- **À définir** : aucun ensemble de cas stable n'existe encore.

## Carte globale de couverture

| Famille | État | Risque principal | Type de test recommandé | Priorité |
| --- | --- | --- | --- | --- |
| Métier des sites | Validé | Publication ou visibilité incorrecte | Service et intégration Flask | Terminée |
| Parcours réel des sites | Validé manuellement | Écart entre les tests isolés et l'usage réel | Navigateur et observation humaine | Terminée |
| Navigation et cohérence UI admin | Validé | Régression d'un layout commun ou d'une destination | Intégration HTML et navigateur | Terminée |
| Parcours navigateur de bout en bout | Partiel | Clics, JavaScript ou redirections non vérifiés | Playwright ou équivalent | Critique |
| Authentification et autorisations admin | Partiel | Accès ou mutation sans droit | Intégration Flask et sécurité | Critique |
| Gestion admin des sites | Partiel | Filtres, pagination ou actions incohérentes | Intégration et navigateur | Haute |
| Catégories de sites | À définir | Doublon, suppression impossible ou relation cassée | Service et intégration | Haute |
| Talents et catégories de talents | Documenté | Brouillon exposé, publication ou relations incorrectes | Service et intégration | Critique |
| Contenus SEO, blog et pages éditoriales | À définir | Brouillon public, slug dupliqué ou workflow cassé | Service et intégration | Haute |
| Accessibilité | À définir | Interface inutilisable au clavier ou par lecteur d'écran | Analyse automatique et contrôle humain | Haute |
| Responsive et régression visuelle | Partiel | Débordement, élément masqué ou navigation cassée | Navigateur multi-viewport et comparaison visuelle | Haute |
| SEO technique | À définir | Mauvaise indexation ou exposition de contenu privé | Intégration HTTP | Haute |
| Sécurité applicative transversale | Partiel | XSS, CSRF, SSRF, redirection ouverte ou fuite de données | Intégration et audit ciblé | Critique |
| Uploads et fichiers | À définir | Fichier dangereux, perte ou accès hors dossier | Intégration fichiers | Haute |
| Migrations SQLite | Partiel | Schéma incomplet, perte de données ou migration non idempotente | Migration sur bases temporaires représentatives | Critique |
| Démarrage et déploiement Docker | À définir | Nouveau code actif avant la migration ou service indisponible | Test de fumée du conteneur | Critique |
| Performance et concurrence | À définir | Recherche lente, verrou SQLite ou perte de clics | Mesures et charge ciblée | Moyenne |

## Couverture existante

### Sites

Les fichiers `SITE_TEST_CASES.md` et `tests/test_site_*.py` couvrent notamment :

- admissibilité et publication ;
- statuts, transitions et visibilité publique ;
- normalisation des URL et doublons ;
- accessibilité HTTP avant publication ;
- recherche, filtres, tris et portée géographique ;
- clics, tendances et confidentialité ;
- dates de publication et certaines migrations ;
- parcours réel de la proposition à l'archivage.

Cette couverture valide le métier des sites. Elle ne constitue pas une
validation générale de toutes les interfaces et de tous les modules.

### Talents

`TALENT_TEST_CASES.md` décrit déjà les comportements attendus, mais les cas
restent à automatiser. Aucun fichier `tests/test_talent_*.py` n'est présent à la
date de ce document.

## Chantiers manquants

### 1. Navigation et cohérence de l'administration

Chaque page administrative doit conserver un moyen clair d'accéder au tableau
de bord et aux sections principales. Les tests doivent vérifier au minimum :

- la présence de la navigation admin commune ;
- les liens vers le tableau de bord, les sites, les clics, les catégories, les
  talents et les contenus ;
- la déconnexion par formulaire protégé ;
- l'indication de la section active ;
- un retour possible après une création, une modification ou une erreur ;
- le comportement sur ordinateur et mobile.

**Anomalie initiale `ANO-ADMIN-UI-001` :** la page `/admin/clicks` utilisait
`templates/admin/clicks_aggregated.html` sans afficher les actions de navigation
présentes sur le tableau de bord. Le layout admin commun et les tests
transversaux corrigent désormais ce défaut sur toutes les pages administratives
authentifiées.

L'audit détaillé des 15 gabarits, la matrice de navigation, les cinq anomalies
et les critères de correction sont consignés dans
[`ADMIN_NAVIGATION_AUDIT_2026-09-24.md`](ADMIN_NAVIGATION_AUDIT_2026-09-24.md).

### 2. Parcours navigateur de bout en bout

Les tests Flask doivent être complétés par quelques parcours réels dans un
navigateur : connexion, navigation entre sections, formulaires, filtres avec
JavaScript, messages visibles, redirections et menus mobiles. Ces tests doivent
rester peu nombreux et couvrir les parcours critiques.

### 3. Authentification et autorisations

Il faut contrôler toutes les routes `/admin/*`, les mutations `POST`, CSRF, la
déconnexion, les destinations `next` et l'impossibilité pour un visiteur de
publier, archiver, corriger ou supprimer une donnée.

### 4. Gestion administrative des sites et catégories

La couverture doit inclure les filtres admin, le tri, la pagination, la
conservation du contexte après une action, les pages vides, les catégories
dupliquées et le refus de supprimer une catégorie encore utilisée.

### 5. Talents et catégories de talents

La priorité est d'automatiser `TALENT_TEST_CASES.md` : brouillon initial,
publication, archivage, visibilité, slugs, plateformes, images, catégories et
recherche publique.

### 6. Contenus SEO et blog

Il faut vérifier création, modification, publication, dépublication,
archivage, unicité des slugs, ordre public, métadonnées et invisibilité des
brouillons.

### 7. Accessibilité et responsive

Les contrôles doivent couvrir le clavier, le focus, les labels, les titres,
les messages d'erreur, les attributs ARIA, les contrastes et les principaux
breakpoints. Une vérification de largeur ne suffit pas à prouver
l'accessibilité ou la qualité visuelle.

### 8. SEO technique

Les routes `sitemap.xml`, `robots.txt`, les balises canoniques, les titres, les
descriptions, les erreurs `404` et l'exclusion des contenus privés doivent être
vérifiés automatiquement.

### 9. Sécurité transversale

Un lot dédié doit couvrir XSS, CSRF, injections SQL, SSRF, redirections
ouvertes, traversée de chemins, cookies de production, limitation de débit et
absence de secrets ou de données privées dans les pages et les logs.

### 10. Uploads et fichiers

Les tests doivent vérifier extensions, taille, noms dangereux, remplacement,
persistance Docker, image absente, URL publique et impossibilité de sortir du
dossier d'uploads.

### 11. Migrations et déploiement

Une migration doit être testée depuis une base vide et depuis une ancienne base
représentative, puis exécutée une seconde fois. Les données, contraintes et
index doivent être conservés. Un test de fumée Docker doit ensuite confirmer :

- l'exécution de `migrate.py` avant Flask ou Gunicorn ;
- le démarrage de l'application ;
- l'accès à SQLite et Redis ;
- les réponses de l'accueil, de la recherche et de l'administration ;
- l'absence d'exception dans les logs.

L'incident `no such column: s.location_scope` a montré ce besoin : Flask avait
rechargé le nouveau code dans un conteneur déjà actif sans relancer la
migration.

### 12. Performance et concurrence

Après les familles critiques, mesurer la recherche avec un volume réaliste, la
pagination, les écritures simultanées de clics, les verrous SQLite et le
comportement lorsque Redis est indisponible.

## Ordre de réalisation recommandé

1. Navigation et cohérence UI de l'administration.
2. Authentification et autorisations admin.
3. Automatisation des talents et de leurs catégories.
4. Contenus SEO, blog et catégories de sites.
5. Migrations complètes et test de fumée Docker.
6. Accessibilité, responsive et parcours navigateur critiques.
7. SEO technique, sécurité transversale et uploads.
8. Performance et concurrence.

## Règle de suivi

Chaque chantier crée ses cas détaillés dans un document dédié ou complète un
document existant. Après implémentation, il doit préciser la commande exécutée,
le résultat réel, les cas encore ignorés et les limites humaines. Cette carte
globale est mise à jour uniquement pour refléter cet état constaté.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 1.2 | 24 septembre 2026 | Validation de la navigation admin commune par six tests automatisés et deux contrôles navigateur. |
| 1.1 | 24 septembre 2026 | Audit de la navigation admin terminé, cinq anomalies classées et stratégie de correction définie. |
| 1.0 | 24 septembre 2026 | Création de la carte globale, priorisation des familles manquantes et enregistrement de l'anomalie de navigation de la page Clics. |
