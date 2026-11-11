# Page catégorie de sites

## Correction du lien de sortie de l’état vide — 22 octobre 2026

[UX-HOME-025](HOME_PAGE.md) : la section #categories a disparu des accueils actifs.
Le bouton d’état vide vers cette ancre devient « Explorer tous les sites » et
ouvre l’annuaire sites.html avec le contexte de maquette courant. Changer de
catégorie reste possible avec le sélecteur existant ; proposition préremplie,
recherche et règles métier inchangées. Contrôle navigateur : Météo vide →
Explorer tous les sites → liste Sites, navbar et version conservées.

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.5 |
| Date | 7 octobre 2026 |
| Statut | Sept choix validés ; conception suffisante pour préparer la maquette |
| Réalisation | Maquette locale interactive vérifiée ; intégration Flask non réalisée |

## Décisions validées

Réponse utilisateur : `1A 2A 3B 4A 5A`.
Complément validé : `6A 7A`.

| ID | Décision et critère d'acceptation |
| --- | --- |
| UX-CAT-001 | Chaque site présente son nom, une courte description, son domaine, sa commune si renseignée et « Visiter le site ↗ ». Les liens externes suivent `UX-GEN-006` et passent par le lien sortant géré par Réunion Wiki (`RM-SITE-008`). |
| UX-CAT-002 | À l'ouverture sans critères, les sites sont classés par ordre alphabétique. Les sites publiés sans clic restent visibles ; seuls les sites publiés sont exposés (`RM-SITE-006`, `RM-SITE-008`). |
| UX-CAT-003 | Recherche dans la catégorie courante, filtre commune et choix du tri. Réutiliser `RM-SITE-007`, `PUBLIC_SEARCH.md` et `UX-GEN-001` à `003` : recherche lancée explicitement, filtre/tri automatiques, état dans l'URL, « Affiner » sur mobile et critères actifs retirables. La catégorie reste le périmètre de la page. La portée géographique reste reportée comme dans la recherche publique. |
| UX-CAT-004 | Fil « Accueil › Catégorie » et commande compacte « Changer de catégorie ». Préserver les URLs publiques et redirections canoniques existantes. |
| UX-CAT-005 | Lien de proposition sous la liste et dans l'état vide vers le formulaire commun. Type Site et catégorie présélectionnés, tous deux modifiables. Réutiliser `UNIFIED_SUBMISSION.md` : envoi sans compte, modération avant publication, aucun droit de publication ou correction directe accordé au proposant. |

Une catégorie principale par site au MVP ; catégories secondaires en V2
(`RM-SITE-004`). La direction visuelle C est conservée sans lancer la
formalisation différée de la charte.

## UX-CAT-006 — Tri après recherche, validé

La recherche textuelle utilise la pertinence lorsque le visiteur n'a pas choisi
un autre tri ; tout tri explicitement choisi est conservé. Sans texte ni tri
explicite, retrouver l'ordre alphabétique. La différence entre tri par défaut
et choix explicite doit être conservée lors des changements de critères et
de la restauration de l'URL.

Les tris existants de la recherche sont pertinence, popularité, date de
publication et nom. La popularité doit respecter la période de 30 jours de
`RM-SITE-008`, et les nouveautés `RM-SITE-009`.

## UX-CAT-007 — États et retours, validés

- Catégorie vide : message « Aucun site référencé pour le moment », accès aux
  autres catégories et proposition préremplie.
- Recherche sans résultat : conserver les critères, permettre de les effacer
  sans quitter la catégorie, accéder aux autres catégories et proposer un site.
- Changement de catégorie : ouvrir la nouvelle catégorie sans critères hérités.
- Depuis la confirmation de proposition, fournir un retour à la catégorie
  d'origine, en complément des accès déjà validés vers l'accueil et une nouvelle
  proposition. L'origine ne change pas si le proposant corrige la catégorie.
- Chargement et erreur technique distincts d'une liste vide, avec possibilité
  de réessayer ; navigation clavier et rendu mobile selon `UX-GEN-007/008`.

Les quatre comportements soumis à la question 7 sont validés par `7A`.
Les états de chargement/erreur et l'accessibilité réutilisent les décisions
transversales déjà validées. Aucune question produit bloquante ne reste avant
la maquette ; les détails de présentation réutiliseront la direction C.

## Parcours et vérification future

Visiteur : ouvrir la catégorie → parcourir/rechercher/filtrer/trier → visiter
un site dans un nouvel onglet ou changer de catégorie. Le retour navigateur
doit restaurer les critères présents dans l'URL.

Contributeur : proposer depuis la catégorie → corriger si nécessaire les
présélections → envoyer → confirmation de réception. La proposition ne rejoint
pas immédiatement la liste publique.

Administrateur : vérifier/corriger la proposition → publier ou refuser selon
`RM-SITE-010` et le parcours commun. Une correction de catégorie se reflète dans
la catégorie de publication ; l'archivage retire le site de la liste publique.

Avant une future implémentation, écrire les tests à partir des exigences
validées, puis le code, conformément à la demande utilisateur. Couvrir les
présélections modifiables, visibilité des statuts, tris, combinaison des
critères, restauration de l'URL et retours ; vérifier visuellement mobile et
ordinateur. Les contrôles de maquette sont consignés dans [CATEGORY_MOCKUP_CHECKS.md](../testing/CATEGORY_MOCKUP_CHECKS.md). Ils ne valident pas le backend.

## Écarts observés par lecture du code

- `templates/categorie.html` : nom, description, commune et lien sortant présents ;
  domaine et outils de recherche absents, propositions encore vers Instagram.
- `reunion_wiki/routes/public.py::voir_categorie` : URL et canonical existants,
  aucune gestion des critères sur la catégorie.
- `reunion_wiki/repositories/site_repository.py::get_sites_by_category_id` :
  tri actuel par vedette, clics cumulés et date d'ajout, différent du choix validé.
- `search_sites` exige du texte et utilise les clics cumulés pour le tri
  populaire : ne pas supposer qu'il couvre directement le parcours catégorie.

Ces écarts concernent toujours le backend existant : aucun template Flask,
service, repository, migration ou déploiement modifié par la maquette.

## Maquette locale — 7 octobre 2026

Réalisation demandée après validation : `maquettes/categorie.html`, styles et
interactions dans `categorie.css` et `categorie.js`. Liens des trois catégories
illustrées ajoutés dans `accueil.html`. `proposer.js` présélectionne la catégorie
et conserve son origine pour le retour dans `proposition-confirmee.html`.

- Six sites fictifs pour Emploi & formation, autres catégories illustratives,
  Météo vide ; liens de démonstration vers `example.org`, sans suivi de clics.
- Recherche explicite, commune et quatre tris simulés, état partageable dans
  l'URL, retour navigateur, filtres mobiles et critères retirables.
- États vide, aucun résultat, chargement et erreur accessibles par les liens
  d'aperçu ; chargement volontairement figé pour observer cet état.
- Formulaire commun et confirmation simulés : aucun envoi, stockage ou
  publication. Retour à l'origine confirmé même après correction de catégorie.
- Polices et icônes locales, direction C. Rendu observé à 1440 × 900,
  390 × 844 et 320 × 844 ; détails des contrôles et limites dans le plan lié.

Disponible uniquement en local sur
`http://127.0.0.1:8765/maquettes/categorie.html?categorie=emploi-formation`.
Validation visuelle utilisateur encore attendue. La finalisation Git de cette
maquette reste différée jusqu'à cette validation ; les modifications étrangères
présentes dans le dépôt sont préservées.

### Correction de densité — retour utilisateur du 7 octobre 2026

Le premier rendu reprenait la palette C mais restait trop aéré par rapport à
l'accueil compact. Correction locale de `categorie.css` : suppression des
monogrammes et du surtitre décoratif, cartes sans hauteur minimale, espacements
réduits, recherche sobre et changement de catégorie sur une ligne sur mobile.
Les informations validées et les cibles tactiles restent présentes.

Rendu compact observé sur mobile 390 px et ordinateur 1440 px ; filtre commune
et retrait de critère revérifiés, absence de débordement contrôlée à 320 px.
La validation visuelle utilisateur reste attendue. La charte détaillée demeure
reportée ; il ne s'agit pas d'une nouvelle direction graphique.

### Complément de finitions C — 7 octobre 2026

Après nouveau retour utilisateur, les finitions restantes sont appliquées à la
catégorie : en-tête et contour de Proposer comme sur l'accueil, navigation et
textes secondaires à 13 px, tailles des titres et arrondis cohérents avec C,
action de proposition vert profond/texte citron, contour de focus vert assombri.
Le fichier CSS est versionné dans le lien de maquette pour éviter un aperçu
ancien conservé en cache. La densité compacte des sites est conservée.

Rendu observé à 390 et 1440 px, aucun débordement à 320 px ; styles calculés
confirmés (navigation et domaine 13 px, navigation 44 px, texte de proposition
`rgb(229,244,154)`), filtre commune revérifié. Aucun backend modifié.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.5 | 7 octobre 2026 | Finitions C restantes alignées sur l’accueil après retour utilisateur ; rendu, styles calculés et filtre revérifiés. |
| 0.4 | 7 octobre 2026 | Densité corrigée après retour utilisateur : rapprochement de l’accueil C compact, contrôles visuels et filtre revérifiés localement. |
| 0.3 | 7 octobre 2026 | Maquette locale demandée et réalisée, parcours simulés vérifiés, limites et validation visuelle restante consignées. |
| 0.2 | 7 octobre 2026 | Validation de 6A et 7A : pertinence après recherche sauf tri explicite, états vides et retours validés ; conception prête pour une future maquette. |
| 0.1 | 7 octobre 2026 | Cinq choix validés consignés, dernier choix de tri et compléments proposés distingués ; écarts du code et vérifications futures identifiés. |
