# Bannières des pages PC — UX-PC-004

## Amendement validé — UX-PC-004 v1.1, 26 octobre 2026

Après essai visuel, l’utilisateur demande de retirer les bandeaux des pages
FAQ, Contact et assimilées : ils paraissent décoratifs et gênent la composition.
Retirer les cinq bandeaux de FAQ, Contact, Mentions légales, Proposer et
confirmation, ainsi que leurs styles devenus inutiles. Les bannières de l’accueil,
des annuaires, de la catégorie et de la recherche restent en place ; la fiche
individuelle conserve le portrait. Cette décision remplace uniquement le choix
de bandeaux fins décrit ci-dessous, conservé comme historique.

Critères : aucun paysage décoratif sur ces cinq pages, logo et contenu préservés,
bannières des quatre pages de liste/recherche intactes. Réalisé dans les cinq
HTML et `page-banners.css` ; FAQ et Contact observés au navigateur à 1265×712,
sans bandeau, logo/titres/actions conservés. Absence du bandeau et de sa feuille
CSS vérifiée sur les cinq pages ; présence des quatre hero d’annuaire/recherche
contrôlée statiquement. `render.py --check`, compilation Python et contrôle du
diff réussis. Maquette locale, commit demandé, sans publication.

## Historique — UX-PC-004 v1.0

| Métadonnée | Valeur |
| --- | --- |
| Date | 26 octobre 2026 |
| Statut | Réalisé et vérifié localement ; relecture utilisateur attendue |
| Source | Proposition de déclinaison par page, réponse utilisateur « oui voilà et oublie pas de commit à la fin » |
| Références | [PC V1](DESKTOP_MOCKUP_V1.md), UX-PC-002 ; [logo](APP_ICON.md), UX-ICON-001 v1.2 |

## Choix retenu et limites

Réutiliser la photo locale du hero de l’accueil pour harmoniser la maquette PC.
L’accueil garde son hero de recherche. Sites et Personnalités reçoivent une
bannière moins haute, avec le titre dans la photo et la recherche juste dessous.
La recherche globale et la page catégorie reprennent cette même famille de pages.
Un voile clair protège la lisibilité du titre et de la description.

Proposer, Contact, FAQ et Mentions légales reçoivent seulement un bandeau photo
fin, avant le contenu. La confirmation reprend ce rappel discret. Les fiches
individuelles gardent le portrait au premier plan, sans paysage concurrent.
Les titres, formulaires, catégories, filtres et liens conservent leurs fonctions.
Même image locale, aucun téléchargement ni nouveau contenu.

Cette décision complète UX-PC-001/002 pour la présentation des pages internes.
La version mobile, le backend Flask, les données et les parcours de modération
restent hors périmètre. Pas de déploiement ou de push autorisé. Le commit local
inclut aussi le logo PC demandé dans cette conversation, encore non commité.

## Critères avant livraison

- Titre lisible dans les bannières d’annuaire, recherche et filtres dessous.
- Bandeaux fins sur les cinq pages de formulaire/aide/confirmation, avec le
  contenu utile proche du haut ; aucun paysage ajouté à la fiche individuelle.
- Logo R chargé, nom et menu lisibles ; lien d’accueil et icône d’onglet présents.
- Vérifier visuellement une liste, un formulaire, une aide et une fiche ;
  contrôler les neuf pages touchées et la conservation des liens et titres.
- Contrôler la compatibilité du générateur de versions et le diff avant commit.

## Réalisation et vérification

Styles isolés dans `maquettes/pc-v1/page-banners.css` et `brand.css` ; quatre
bannières de titre et cinq bandeaux décoratifs dans les HTML PC. L’accueil et
la fiche individuelle ne reçoivent aucun paysage supplémentaire.

Le 26 octobre, accueil/annuaire Sites, formulaire Proposer, FAQ et fiche Adriana
observés au navigateur intégré à 1265×712 : logo chargé, titres et menus lisibles,
recherche/filtres sous la bannière, bandeau fin distinct du contenu, portrait
conservé au premier plan. Les onze HTML ont été comparés à main hors comparateur
de versions, en retirant les seuls ajouts de logo et bannière : aucun autre
changement de contenu ou de lien. Les comparateurs de chaque checkout sont
conservés tels quels. Contrôle statique des quatre bannières et cinq bandeaux ;
`render.py --check`, `python3 -m compileall -q .` et `git diff --check` réussis.

Limites : pas de nouveau test visuel multi-largeur, téléphone physique ou audit
exhaustif d’accessibilité ; voiles et repli CSS à relire par l’utilisateur.
Maquette locale uniquement, sans publication.
