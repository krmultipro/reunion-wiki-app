# Cas de test — Navigation de l'administration

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Statut | Six cas automatisés validés, deux contrôles navigateur validés |
| Dernière mise à jour | 24 septembre 2026 |
| Périmètre | Pages administratives après authentification |

## Objectif

Ces cas traduisent l'audit de navigation admin en résultats vérifiables. Ils
doivent être écrits et exécutés avant la correction de l'interface, puis servir
de protection contre les régressions.

Les exigences décrivent une interface et ne créent pas de règle métier `RM-*`.
Les contrôles automatisables utilisent les identifiants `TC-ADMIN-NAV-*`. Le
rendu responsive conserve un contrôle navigateur humain complémentaire.

## Navigation de référence

La navigation admin commune contient, dans cet ordre :

1. Tableau de bord — `/admin` ;
2. Sites — `/admin/sites` ;
3. Clics — `/admin/clicks` ;
4. Catégories de sites — `/admin/categories` ;
5. Créateurs — `/admin/talents` ;
6. Catégories créateurs — `/admin/talent-categories` ;
7. Contenus SEO — `/admin/content` ;
8. Déconnexion — formulaire `POST` vers `/admin/logout`.

## TC-ADMIN-NAV-01 — Navigation commune sur les pages principales

**Précondition :** l'administrateur est authentifié.

**Action :** ouvrir successivement le tableau de bord, les sites, les clics,
les deux familles de catégories, les créateurs et les contenus SEO.

**Résultat attendu :** chaque réponse est HTTP 200 et contient exactement un
élément `<nav aria-label="Administration">`. Les 14 gabarits authentifiés
utilisent tous le layout admin commun.

**Automatisation :** intégration Flask.

## TC-ADMIN-NAV-02 — Destinations, libellés et ordre stables

**Précondition :** une page admin est affichée.

**Action :** lire les liens de la navigation commune.

**Résultat attendu :** les sept destinations internes correspondent à la
navigation de référence, sans doublon, avec les mêmes libellés et dans le même
ordre sur chaque page.

**Automatisation :** intégration Flask et analyse du HTML.

## TC-ADMIN-NAV-03 — Section active annoncée

**Précondition :** l'administrateur consulte une liste ou un formulaire admin.

**Action :** inspecter les liens de la navigation.

**Résultat attendu :** un seul lien possède `aria-current="page"`. Il désigne
la section de la page, y compris sur les écrans de création ou modification.

**Automatisation :** intégration Flask et analyse du HTML.

## TC-ADMIN-NAV-04 — Déconnexion sécurisée

**Précondition :** l'administrateur est authentifié et CSRF est actif.

**Action :** inspecter puis soumettre le formulaire de déconnexion de la
navigation.

**Résultat attendu :** le formulaire utilise `POST`, cible `/admin/logout`,
contient un jeton CSRF, détruit la session lorsqu'il est soumis et refuse une
requête `GET` avec HTTP 405.

**Automatisation :** intégration Flask.

## TC-ADMIN-NAV-05 — Navigation et retour sur les formulaires

**Précondition :** l'administrateur ouvre les écrans de création d'un site,
d'une catégorie, d'un créateur, d'une catégorie créateur et d'un contenu.

**Action :** inspecter la navigation et l'en-tête du formulaire.

**Résultat attendu :** la navigation commune reste présente et le lien de
retour contextuel vers la liste ou le tableau de bord est conservé.

**Automatisation :** intégration Flask.

## TC-ADMIN-NAV-06 — Accès sans authentification

**Précondition :** aucune session admin n'est active.

**Action :** demander chacune des sept pages principales.

**Résultat attendu :** chaque requête redirige vers `/admin/login` et conserve
la destination interne dans le paramètre `next`. Aucune navigation privée n'est
rendue.

**Automatisation :** intégration Flask.

## TC-ADMIN-NAV-07 — Utilisation sur mobile

**Précondition :** l'administrateur est connecté dans un navigateur large de
390 px.

**Action :** parcourir toutes les destinations, ouvrir puis quitter la page
Clics et utiliser la navigation au clavier et au toucher.

**Résultat attendu :** chaque destination et la déconnexion sont accessibles,
le focus est visible, aucun libellé n'est tronqué et la page ne possède pas de
défilement horizontal global.

**Automatisation :** parcours navigateur à ajouter ; validation humaine
requise pour le confort tactile et la lisibilité.

## TC-ADMIN-NAV-08 — Utilisation sur ordinateur

**Précondition :** l'administrateur est connecté dans un navigateur large de
1280 px.

**Action :** parcourir toutes les destinations et vérifier la section active.

**Résultat attendu :** la navigation reste stable, lisible et entièrement
visible ; les actions propres à la page restent distinctes de la navigation.

**Automatisation :** parcours navigateur à ajouter ; contrôle visuel humain.

## Commandes de vérification

```bash
.venv/bin/python -m unittest -v tests.test_admin_navigation
.venv/bin/python -m unittest discover -v
.venv/bin/python -m compileall -q reunion_wiki tests
```

## Suivi des exécutions

| Étape | Résultat | Preuve |
| --- | --- | --- |
| Avant correction | 6 tests exécutés : 1 réussi, 5 en échec avec 37 sous-cas défaillants | `TC-ADMIN-NAV-06` confirme la protection existante ; les cas 01 à 05 exposent l'absence de navbar commune. |
| Après correction | 6 tests réussis | `python -m unittest -v tests.test_admin_navigation` termine avec `OK`. |
| Suite complète | 79 exécutés : 78 réussis, 1 ignoré | `python -m unittest discover -v` termine avec `OK (skipped=1)`. |
| Navigateur 390 px | Validé | Sept liens présents, déconnexion visible, aucun débordement global et parcours Sites → Clics réussi ; la navigation défile dans son propre conteneur. |
| Navigateur 1280 px | Validé | Sept liens visibles sans défilement, une section active et déconnexion accessible. |

## Traçabilité

| Anomalie | Cas couvrants |
| --- | --- |
| ANO-ADMIN-UI-001 — Page Clics isolée | 01, 02, 04, 07, 08 |
| ANO-ADMIN-UI-002 — Navigation dupliquée | 01, 02 |
| ANO-ADMIN-UI-003 — Formulaires sans navigation globale | 03, 05 |
| ANO-ADMIN-UI-004 — Position non annoncée | 01, 03, 07, 08 |
| ANO-ADMIN-UI-005 — Libellés et ordre variables | 02 |
