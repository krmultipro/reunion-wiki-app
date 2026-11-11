# Notifications PWA — piste conservée

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.3 |
| Date | 26 octobre 2026 |
| Statut | Simulation dans la dernière maquette autorisée ; règles d’envoi réel à préciser |
| Autorisation | Intégrer logo et notifications simulées à mobile-final ; aucun push réel, backend ou déploiement |
| Suivi | Dashboard → Projets → Applications → Réunion Wiki, ticket #47 ; saisie et relecture vérifiées le 26 octobre |

## Source et portée du retour

### Complément — simulation de maquette autorisée

**UX-PUSH-002 v1.0.** Le 26 octobre, après la proposition de boutons qui
déclenchent une notification simulée et permettent d’ouvrir le contenu,
l’utilisateur demande cette intégration dans la dernière maquette.

- Deux boutons dans **Outils de la maquette** : **Simuler un nouveau site**
  et **Simuler une nouvelle personnalité**. Les exemples Bus.re et Adriana
  utilisent le catalogue public existant ; aucune fausse publication ajoutée.
- Une notification à la fois, en haut de l’écran, avec R, nom du service,
  mention **Démonstration**, titre et court texte de l’exemple conservé.
- Ouverture volontaire uniquement ; pas de minuterie de fermeture afin de
  permettre les captures. Un bouton ferme l’aperçu ; Échap le ferme également.
  Déclencher l’autre exemple remplace la notification précédente.
- Lien Site : `sites.html?q=Bus.re`, l’annuaire filtré existant, car aucune
  fiche locale Site n’existe ; le lien externe du site reste une action distincte.
  Lien Personnalité : `personnalite.html?id=6`, fiche d’Adriana, avec retour
  vers la page locale d’origine. La fermeture garde la page et ses critères.
- Les contrôles sont accessibles au clavier, l’apparition est annoncée sans
  dialogue modal ; le dock reste utilisable. Pas de demande d’autorisation du
  navigateur, appel réseau push, stockage d’abonnement ou envoi système.
- Anciennes variantes, formulaire, modération et données de session inchangés.
  Si le contenu d’exemple a été archivé dans la session, la simulation ne
  s’ouvre pas et explique son indisponibilité ; aucun contenu n’est restauré.

Critères définis avant réalisation : R présent sur les pages communes et notification ;
deux déclencheurs et bonne destination ; fermeture par bouton/Échap et focus
rendu au déclencheur ; remplacement sans doublon ; absence de débordement à
320/390 px et repli ordinateur ; icône chargée et absence d’erreur JavaScript
nouvelle. Réalisation locale et contrôles observés dans
[la revue du 26 octobre](../testing/NOTIFICATIONS_LOGO_REVIEW_2026-10-26.md).

### Complément validé — icône R, 26 octobre 2026

Après le premier aperçu, l’utilisateur retient le **R personnalisé crème sur
vert profond, avec relief et soleil citron**, avec possibilité de changer plus
tard. [UX-ICON-001 et image conservée](APP_ICON.md) font référence pour les
futurs usages d’icône. Cela tranche le choix visuel initialement ouvert ci-dessous,
sans modifier le fragment historique, activer les notifications ou intégrer
l’icône au site.

### Historique — premier aperçu

**UX-PUSH-001 v0.1.** Discussion du 26 octobre 2026 : après une question sur
les notifications PWA, l’utilisateur demande un visuel pour l’ajout d’un site
ou d’une personnalité, puis indique « j’aime bien » et « note la notif quelque
part ». Conserver cette appréciation des exemples ; elle ne tranche pas les
règles d’envoi, la fréquence, les destinataires ou l’inclusion au lancement.

Le visuel montre des propositions Android et iPhone avec deux notifications :

- **Un nouveau site à découvrir** : « Bus.re rejoint l’annuaire. Retrouve les
  transports en commun de La Réunion. »
- **Une nouvelle personnalité péi** : « Adriana rejoint Réunion Wiki. Découvre
  sa présentation et ses réseaux officiels. »

Bus.re et Adriana servent uniquement d’exemples fictifs d’annonce ; ces textes
ne prouvent ni un ajout récent ni l’envoi d’une notification réelle. Titres et
textes restent des propositions éditoriales. La sélection Android dans l’aperçu
ne constitue pas un choix de plateforme exclusif.

Le format apprécié présente le nom Réunion Wiki, un titre court et un petit
texte. Le globe est une icône provisoire : l’utilisateur précise ne pas avoir
de logo officiel. Le palmier déjà présent dans `static/icons/icon-192x192.png`
et ses variantes ne constitue pas une nouvelle identité validée ; provenance
et droits non vérifiés lors de cette conservation. Aucun remplacement demandé.

## Référence visuelle conservée

[Fragment de l’aperçu du 26 octobre](references/pwa-notifications-20261026.html).
Il conserve les deux vues et leurs styles. Il s’agit du fragment de visualisation
conversationnel : les commandes de changement de plateforme et les icônes
dépendent du moteur de prévisualisation. Ce fichier n’est ni une page produit
ni une implémentation des notifications. Rendu indicatif : le système du téléphone
et ses réglages contrôlent la présentation effective.

## État technique observé localement

- `static/manifest.webmanifest` : métadonnées d’installation, icônes et mode
  `standalone` ; `templates/base.html` enregistre le service worker.
- `static/service-worker.js` : cache et repli réseau ; aucun traitement push
  dans le fichier lu le 26 octobre. Recherche ciblée sans mécanisme d’abonnement
  ou d’envoi trouvé dans les routes, services, templates et dépendances consultés.
- Aucun test de réception sur téléphone ni contrôle de la version déployée.
- Le visuel n’effectue aucune demande d’autorisation ni aucun envoi.
- Complément UX-PUSH-002 réalisé localement dans `mobile-final/app.js`,
  `app.css` et les libellés de retour de `public.js`. Simulation contrôlée ;
  aucune réception push réelle ni disponibilité de production revendiquée.

## À arbitrer lors d’une reprise demandée

Évolution à décider séparément du lancement actuellement documenté dans
`PRODUCT.md`. Distinguer ces annonces publiques des notifications de suivi
contributeur décrites dans `CONTRIBUTOR_WORKFLOW.md`.

- Abonnement volontaire, sujets proposés, refus et désabonnement ; nécessité
  ou non d’un compte à décider, sans ajout implicite au MVP.
- Déclenchement après publication effective, envoi manuel ou automatique,
  traitement des corrections, archivages, republications et doublons.
- Envoi par ajout ou sélection regroupée, fréquence et horaires.
- Destination au toucher et retours ; fiche retirée ou contenu indisponible.
- Gestion des abonnements, erreurs, tentatives et contrôles administrateur ;
  stockage, conservation et sauvegardes à concevoir avant réalisation.
- Tests Android/iPhone, autorisations refusées/révoquées et affichage réel.
- Déclinaisons et lisibilité de l’icône R retenue à vérifier selon `APP_ICON.md` ;
  l’apparence système ne doit pas être promise comme identique à la maquette.

Références de faisabilité consultées le 26 octobre :
[Push API — Mozilla](https://developer.mozilla.org/en-US/docs/Web/API/Push_API),
[Web Push pour les applications de l’écran d’accueil — WebKit](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/).
La réception nécessite un abonnement et les autorisations ; sur iPhone/iPad,
le support documenté commence à 16.4 pour les applications ajoutées à l’écran
d’accueil. Ces conditions devront être revérifiées au moment de la réalisation.

## Historique

| Version | Date | Évolution |
| --- | --- | --- |
| 0.3 | 26 octobre 2026 | Simulation explicitement demandée dans mobile-final : parcours et critères définis avant code ; push réel distinct. |
| 0.2 | 26 octobre 2026 | R personnalisé retenu ensuite par l’utilisateur ; lien vers la décision et l’image, premier aperçu conservé. |
| 0.1 | 26 octobre 2026 | Conservation demandée des exemples et de l’appréciation visuelle ; limites et décisions ouvertes explicites. |
