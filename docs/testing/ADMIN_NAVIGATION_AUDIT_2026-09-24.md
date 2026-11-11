# Audit de la navigation de l'administration

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.1 |
| Statut | Audit terminé, anomalies corrigées et vérifiées |
| Date | 24 septembre 2026 |
| Périmètre | Gabarits et routes de l'administration |

## Objectif

Cet audit vérifie qu'un administrateur peut identifier sa position, rejoindre
les sections principales et se déconnecter depuis chaque écran. Il couvre la
structure HTML rendue par Flask, les liens présents dans les gabarits et les
règles responsive existantes. Il ne valide pas encore le rendu visuel dans un
navigateur réel.

## Méthode

L'analyse a porté sur les 15 gabarits sous `templates/admin`, les routes
`/admin/*`, le layout `templates/base.html` et les styles `.admin-dashboard`.
Les pages principales ont aussi été rendues avec le client de test Flask dans
une session administrateur afin de confirmer qu'elles répondent et que le
défaut n'est pas seulement théorique.

Les routes `/admin`, `/admin/sites`, `/admin/clicks`, `/admin/categories`,
`/admin/talents`, `/admin/talent-categories`, `/admin/content` ainsi que les
écrans de création représentatifs ont toutes répondu avec un statut HTTP 200.
Ce résultat confirme leur disponibilité, mais pas la présence d'une navigation
cohérente : celle-ci a été contrôlée séparément dans le HTML et les gabarits.

## Résultat synthétique

La navigation admin n'est pas un composant commun. Les 15 gabarits héritent
directement du layout public `base.html`. Les écrans de liste recopient chacun
une sélection différente de boutons dans `.admin-dashboard__actions`, tandis
que les écrans de formulaire et de revue affichent seulement un retour local.

La page `/admin/clicks` est le cas le plus grave : elle ne contient aucun lien
vers le tableau de bord ou une autre section admin et aucun formulaire de
déconnexion. L'administrateur doit utiliser la navigation publique ou le bouton
Précédent du navigateur pour en sortir.

## Matrice de couverture actuelle

| Écran | Tableau de bord | Sections admin | Déconnexion | Section active | Résultat |
| --- | --- | --- | --- | --- | --- |
| Tableau de bord | Écran courant | Toutes les sections | Oui | Non | Partiel |
| Sites | Oui | Clics, catégories | Oui | Non | Partiel |
| Clics | Non | Aucune | Non | Non | Échec |
| Catégories de sites | Oui | Sites, clics, catégories créateurs | Oui | Non | Partiel |
| Créateurs | Oui | Catégories créateurs | Oui | Non | Partiel |
| Catégories créateurs | Oui | Créateurs | Oui | Non | Partiel |
| Contenus SEO | Oui | Aucune autre section | Oui | Non | Partiel |
| Création, modification et revue | Retour local seulement | Aucune | Non | Non | Partiel |
| Connexion | Sans objet | Sans objet | Sans objet | Sans objet | Conforme |

Le tableau de bord est le seul écran qui expose toutes les sections. Même sur
cet écran, les boutons sont regroupés dans un `div` générique et aucune section
n'est indiquée par `aria-current="page"`.

## Anomalies

### ANO-ADMIN-UI-001 — Page Clics isolée — Critique

`templates/admin/clicks_aggregated.html` affiche les filtres, statistiques et
formulaires de correction sans navigation admin ni déconnexion. Le défaut est
présent sur toutes les tailles d'écran puisque ces éléments sont absents du
HTML.

**Critère de correction :** depuis `/admin/clicks`, l'administrateur peut
rejoindre toutes les sections principales, retourner au tableau de bord et se
déconnecter par un formulaire POST protégé par CSRF.

### ANO-ADMIN-UI-002 — Navigation dupliquée et incomplète — Haute

Les pages principales possèdent chacune leur propre liste de boutons. Toute
nouvelle section ou modification de libellé doit donc être reportée à plusieurs
endroits. Cette duplication explique les écarts observés et rend probable une
nouvelle régression.

**Critère de correction :** une seule source définit les destinations, les
libellés, leur ordre et la déconnexion pour toutes les pages admin.

### ANO-ADMIN-UI-003 — Formulaires et revues sans navigation globale — Haute

Les écrans de création, modification et revue ne proposent qu'un retour vers
une liste ou le tableau de bord. Ils n'exposent ni les autres sections ni la
déconnexion. Une erreur de formulaire laisse donc l'administrateur dans un
écran au contexte de navigation réduit.

**Critère de correction :** le retour contextuel reste disponible et la
navigation admin commune est également présente.

### ANO-ADMIN-UI-004 — Position courante non annoncée — Moyenne

Aucun lien admin n'utilise `aria-current="page"` et le bloc de boutons n'est pas
un élément `nav` nommé. La position courante dépend uniquement du titre de
page, et les technologies d'assistance ne disposent pas d'une navigation admin
identifiable.

**Critère de correction :** la navigation utilise
`<nav aria-label="Administration">` et marque la destination courante avec
`aria-current="page"`.

### ANO-ADMIN-UI-005 — Libellés et ordre variables — Moyenne

La destination des sites est appelée « Tous les sites » sur le tableau de bord
et « Sites » ailleurs. Les sections changent aussi d'ordre selon l'écran. Cette
variation augmente l'effort nécessaire pour se repérer.

**Critère de correction :** chaque destination conserve le même libellé et le
même ordre sur tous les écrans.

## Comportement responsive

Les règles existantes autorisent le retour à la ligne des boutons et les
alignent à gauche sous 768 px. Elles limitent donc certains débordements des
pages qui possèdent `.admin-dashboard__actions`. Elles ne peuvent pas corriger
les liens absents et ne définissent pas le comportement d'une navigation admin
complète sur petit écran.

La correction devra être vérifiée au minimum à 390 px et 1280 px. À 390 px,
chaque destination et le bouton de déconnexion doivent rester atteignables au
clavier et au toucher, sans défilement horizontal de la page.

## Solution recommandée

1. Créer `templates/admin/base.html`, qui étend `base.html` et contient la
   navigation commune.
2. Faire hériter tous les gabarits admin de ce layout, sauf la page de
   connexion.
3. Définir les destinations dans un ordre stable : tableau de bord, sites,
   clics, catégories de sites, créateurs, catégories créateurs et contenus SEO.
4. Calculer la section active à partir de l'endpoint Flask et ajouter
   `aria-current="page"`.
5. Conserver les actions propres à la page, par exemple « Ajouter un site »,
   dans un bloc distinct de la navigation globale.
6. Placer la déconnexion POST avec son jeton CSRF dans la navigation commune.

Le processeur de contexte `inject_admin_logout_form` fournit déjà le formulaire
de déconnexion à toutes les pages admin authentifiées. La centralisation ne
demande donc pas de dupliquer sa création dans chaque route.

## Tests à ajouter avec la correction

Créer `tests/test_admin_navigation.py` avec les contrôles suivants :

- rendre en session authentifiée chaque page principale et une page de
  formulaire de chaque module ;
- vérifier la présence d'un unique
  `<nav aria-label="Administration">` ;
- vérifier les sept destinations communes et leurs URL ;
- vérifier qu'un seul lien porte `aria-current="page"` ;
- vérifier la déconnexion par formulaire POST et la présence du jeton CSRF ;
- vérifier que le lien de retour contextuel reste présent sur les formulaires ;
- confirmer que les visiteurs non authentifiés sont redirigés vers la
  connexion ;
- exécuter un parcours navigateur à 390 px et 1280 px, notamment entrée puis
  sortie de la page Clics.

## Décision de réalisation

La correction doit être traitée avant d'ajouter de nouveaux parcours admin de
bout en bout. Elle fournit le socle commun que ces parcours testeront et règle
directement l'anomalie visible signalée sur la page Clics.

## Résultat de la correction

Les cinq anomalies sont corrigées par `templates/admin/base.html`. Les 14
gabarits authentifiés utilisent ce layout ; la connexion reste volontairement
sur le layout public. Les actions propres aux écrans restent dans leur en-tête
et les destinations globales ne sont plus dupliquées.

Les six tests `TC-ADMIN-NAV-01` à `06` passent, ainsi que la suite complète de
79 tests automatisés avec un test manuel ignoré. Les contrôles navigateur à
390 px et 1280 px valident la présence des sept destinations, la section
active, la déconnexion et l'absence de débordement horizontal global. Le détail
est conservé dans
[`ADMIN_NAVIGATION_TEST_CASES.md`](ADMIN_NAVIGATION_TEST_CASES.md).
