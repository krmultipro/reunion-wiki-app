# Icône Réunion Wiki — R personnalisé retenu

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.2 |
| Date | 26 octobre 2026 |
| Statut | Direction visuelle retenue par l’utilisateur, révisable ultérieurement |
| Identifiant | UX-ICON-001 v1.0 |
| Périmètre de cette livraison | Intégration autorisée dans la dernière maquette locale ; application Flask et production hors périmètre |
| Suivi | Dashboard Réunion Wiki : charte #17 ; notifications PWA #47 |

## Décision validée

### Complément — intégration de maquette autorisée

Le 26 octobre, l’utilisateur demande explicitement « intègre la notif et le logo
dans la dernière version maquette car je valide ». **UX-ICON-001 v1.1** : ajouter
le R retenu à côté du titre Réunion Wiki dans le cadre partagé de
`maquettes/mobile-final/`, comme icône de l’onglet et dans les notifications
simulées. Le nom reste lisible ; Pacifico et les anciennes variantes sont conservés.
Réutiliser l’image sélectionnée sans la redessiner. Intégration locale réalisée :
`app.js`, `app.css`, `assets/logo-r.png` ; [contrôles et limites](../testing/NOTIFICATIONS_LOGO_REVIEW_2026-10-26.md).

### Complément — logo dans la maquette PC (UX-ICON-001 v1.2)

Le 26 octobre, l’utilisateur signale également le logo manquant sur la version
PC. Reprendre le même R, sans nouvelle création, à côté du nom Réunion Wiki et
comme icône d’onglet sur les onze pages de `maquettes/pc-v1/`. Le nom Pacifico
et son lien vers l’accueil restent présents. La ressource locale déjà conservée
`../mobile-final/assets/logo-r.png` est partagée sans copie. La feuille dédiée
`brand.css` limite cet ajustement à la marque PC.

Critères : R visible et chargé dans l’en-tête de chaque page, nom et menu
lisibles, image décorative (`alt=""`) puisque le nom suit, lien d’accueil
conservé, icône d’onglet locale. Maquette locale seulement, aucun changement
Flask, notification ou déploiement. Contrôles : présence du logo, de sa ressource locale, du lien d’accueil, du
style et de l’icône d’onglet vérifiée dans les onze HTML ; accueil observé au
navigateur intégré à 1265×712, R chargé et nom/menu lisibles. Pas de nouveau
contrôle multi-largeur ni système PWA pour cet ajout. Modification locale,
sans commit ni publication lors de ce premier ajout. L’utilisateur demande
ensuite explicitement le commit à la fin de la déclinaison des bannières PC ;
voir [UX-PC-004](DESKTOP_PAGE_BANNERS.md) pour cette finalisation locale.

### Historique — choix de l’icône

Après présentation du R personnalisé, l’utilisateur confirme : « oui ça me va
bien on part la dessus on viendra changer le logo plus tard si il faut » et
demande de noter le choix. Ce visuel devient la référence d’icône retenue pour
le moment, avec possibilité d’évolution ultérieure. Il ne s’agit plus d’une
simple proposition en attente de retour.

![R personnalisé retenu](references/reunionwiki-r-20261026.png)

- Lettre R crème, épaisse et arrondie, sur carré vert profond à coins arrondis.
- Relief et soleil citron intégrés dans la partie supérieure de la lettre,
  évocation discrète de La Réunion.
- Direction graphique cohérente avec la palette de la maquette publique.
- Référence destinée aux futurs usages d’icône du site, PWA et notifications ;
  formats et déclinaisons techniques à préparer lors d’une intégration demandée.

## Source conservée et limites

Image PNG originale générée le 26 octobre avec l’outil intégré imagegen,
conservée sans retouche dans `references/reunionwiki-r-20261026.png`.
Brief : monogramme R personnalisé, vert profond/crème/accent citron, formes
épaisses et arrondies, évocation du relief réunionnais, lisibilité en petite taille.

Cette validation concerne l’icône montrée. Elle ne décide pas le remplacement
du titre manuscrit Pacifico dans l’en-tête ni une nouvelle charte complète.
Le palmier dans `static/icons/` et le globe du premier aperçu de notifications
restent des éléments historiques. Le complément v1.1 ajoute le R dans la dernière
maquette sans modifier ces sources historiques ni le site réel.

L’image reste une source raster d’exploration : lisibilité favicon et notification,
recadrage PWA/maskable, variante monochrome et éventuelle vectorisation à vérifier
avant intégration au site réel. Lisibilité observée dans la maquette à 320/390 px ;
aucune validation système ou test sur appareil physique n’est déclaré.

## Historique

| Version | Date | Évolution |
| --- | --- | --- |
| 1.2 | 26 octobre 2026 | Même R ajouté dans l’en-tête et comme icône d’onglet des onze pages PC à la demande de l’utilisateur. |
| 1.1 | 26 octobre 2026 | Intégration explicitement demandée dans la dernière maquette : en-tête, icône d’onglet et notifications simulées. |
| 1.0 | 26 octobre 2026 | R présenté puis retenu par l’utilisateur ; image conservée, évolution ultérieure possible, intégration distincte. |
