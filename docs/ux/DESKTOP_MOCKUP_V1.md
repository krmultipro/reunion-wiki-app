# Variante PC V1 — conception et réalisation

## Essai de présentation plus longue — Adriana, 26 octobre 2026

Demande utilisateur : voir le rendu d’une description un peu plus longue sur
la fiche PC d’Adriana. Complément de réalisation UX-PC-007, sans changement de
composition. Reprendre les deux premières phrases de la description déjà
présente dans `assets/personnalites-dev-20261023.json` et mobile-final/data.js,
séparées en deux paragraphes ; aucune nouvelle information biographique.
La troisième phrase appréciative sur l’audience n’est pas reprise.

Texte stocké dans le champ facultatif `bio` du catalogue PC ; la fiche utilise
`bio` puis `description` en secours. Les cartes et la recherche existante gardent
leurs extraits courts. Seule la maquette PC est concernée ; aucune donnée active,
catégorie, version mobile ou règle d’admission n’est modifiée.

Critère : texte long visible en entier, sans débordement, portrait et liens
officiels conservés ; autres profils inchangés. Essai visuel à relire, pas une
nouvelle vérification éditoriale de la biographie.

Réalisé dans `pc-v1/data.js` et `profile.js`. Contrôle navigateur à 1280 px via
l’adresse LAN : texte complet en deux paragraphes (204 px de haut), portrait
carré d’environ 519 px et deux liens officiels conservés, aucun débordement.
Capture temporaire `/tmp/reunion-pc-adriana-description-longue.png`.
Syntaxe des deux scripts, compilation Python et espaces contrôlés. Comparaison
du catalogue : seul le champ bio d’Adriana est ajouté ; descriptions courtes,
autres profils et sites identiques. Aucun nouveau contrôle responsive nécessaire
pour ce seul texte ; le repli long a été contrôlé lors d’UX-PC-007. Aucun déploiement.

## Fiche de personnalité composée pour PC — 26 octobre 2026 (UX-PC-007)

Demande explicite : agrandir le portrait et composer une fiche plus marquante
pour l’ordinateur, en utilisant la place disponible tout en gardant le thème.
L’utilisateur accepte le flou des photos actuelles pour cet aperçu et prévoit
de fournir de meilleurs fichiers plus tard. Ce choix remplace le plafond de
150 px d’UX-PC-001 et UX-FICHE-006 **sur la fiche PC seulement**.

Choix d’exécution dans le périmètre demandé : grande composition en deux
colonnes, portrait carré à gauche, catégorie, grand nom, présentation puis
liens officiels à droite. Cadre maximal PC de 1280 px, blanc/crème/vert,
angles arrondis et typographies existantes ; aucun effet animé ou détail
biographique ajouté pour remplir l’espace. Demande de correction discrète
sous la fiche ; retour à l’origine avec ses critères conservé.

Sur écran étroit, empiler portrait et informations avec une typographie adaptée.
Afficher seulement les liens renseignés, signaler leur ouverture externe et
conserver le remplacement du portrait absent. Aucun faux réseau, chiffre,
badge, citation, galerie ou bouton de partage supplémentaire. Les originaux
150×150 restent inchangés : agrandissement CSS assumé pour juger la composition,
sans traitement inventant du détail. Les droits des futures photos restent
distincts de cette mise en page.

Critères avant réalisation : portrait nettement plus grand et place PC utilisée,
hiérarchie lisible, nom et descriptions longs sans débordement, parcours avec
ou sans liens/portrait, profil introuvable et retours utilisables ; repli étroit,
navigation clavier et liens externes contrôlés. Données, listes et version
mobile conservées ; maquette locale uniquement, sans intégration Flask.

Réalisé dans `pc-v1/profile.js` et `app.css` : article à deux colonnes, portrait
carré, catégorie en pastille, nom agrandi, présentation lisible et liens officiels
intégrés au panneau d’informations ; correction sous la fiche. État introuvable
avec accès explicite à la liste. `CREATOR_PROFILE.md` conserve l’amendement au
plafond historique ; aucune donnée ou image modifiée.

Contrôles navigateur du 26 octobre : Adriana à 1280/1440 px, portrait affiché
sur environ 519/554 px, source naturelle toujours 150 px ; Harendra à 1024 px,
portrait environ 403 px et aucun bloc de liens vide. Pas de débordement.
Repli Adriana à 320 px sur une colonne (portrait 239 px). Fixture technique
temporaire, supprimée après contrôle : nom/catégorie/libellé sans espaces,
présentation longue et portrait absent ; aucun débordement à 320/700/1024 px,
remplacement SVG chargé et une colonne à 700 px, deux à 1024 px.
Profil inconnu : message et lien de reprise. Retour de fiche vers la liste
avec q=Adriana/categorie=humour-lifestyle réellement activé ; critères retrouvés.
Focus clavier visible sur le lien TikTok ; liens externes avec cible _blank et
rel noopener noreferrer inspectés sans ouvrir les services externes. Lien de
correction et son retour vérifiés par leur destination, sans envoi de message.

Syntaxe JS, compilation Python, contrôle des espaces et générateur de versions
réussis ; relecture statique indépendante sans défaut actionnable relevé.
Aperçu conservé dans `/tmp/reunion-pc-fiche-grand-portrait.png` (hors Git).
Limites : flou de la source basse définition accepté pour cet aperçu ; pas de
nouvelle image, d’audit exhaustif d’accessibilité, de traitement contact réel ou
d’intégration Flask. Composition à relire par l’utilisateur, aucun déploiement.

## Pagination Personnalités à reprendre dans l’application — 26 octobre 2026 (UX-PC-006)

Demande utilisateur : préparer le code de la maquette pour que la pagination
Personnalités soit bien reprise lors de la future intégration dans l’application.
Retenir **12 personnalités par page**, après combinaison recherche/catégorie,
comme Sites. Ce choix complète UX-PC-003 et remplace son affichage non paginé
des personnalités ; les trois profils de démonstration existants sont conservés.

Critères : aucune commande de pagination ni compteur visible avec douze
résultats ou moins ; pages et navigation au-delà, libellés accessibles propres
aux personnalités, critères conservés dans l’URL et les retours. Recherche ou
catégorie ramènent à la première page ; page hors limites corrigée. Aucun ajout
de profils fictifs à la maquette ni modification de l’application réelle.

**À l’intégration future :** reprendre ce comportement dans la liste PC réelle,
avec pagination appliquée aux résultats filtrés complets et tests avec plus de
12 profils ; le catalogue à trois exemples ne suffit pas à valider le volume.
L’intégration réelle reste à faire, cette maquette ne l’implémente pas dans Flask.

Réalisé dans `pc-v1/content.js` : annuaire Personnalités relié au paginateur
commun ; commandes au-delà de douze résultats, statut visuellement masqué sur
une seule page, nom accessible Pages des personnalités et commentaire UX-PC-006
pour la reprise future. La liste paginée est calculée après les filtres existants.

Contrôle temporaire du paginateur réel extrait du script, exécuté sous Node
avec des données synthétiques uniquement en mémoire : 3 et 12 résultats sans
commandes ni statut visible ; 13 résultats déclenchent la pagination ; 25 se
découpent en 12/12/1 ; pages hors limites ou invalides corrigées, libellé et
conservation q/categorie vérifiés. Ce contrôle de logique ne remplace pas un
test navigateur de volume ni les tests de la future application réelle.
Syntaxe JS, compilation Python, générateur de versions et espaces contrôlés.
Catalogue et fichiers Flask inchangés. Aucun déploiement.

## Défilement commun de la recherche — 26 octobre 2026 (UX-PC-005)

Choix utilisateur **1A** : seul le menu supérieur reste fixe ; la recherche
défile avec le contenu sur toutes les pages PC, comme sur l’accueil. La
recherche persistante des annuaires n’avait pas été explicitement validée : ce
choix tranche le comportement et complète UX-PC-001/003/004.

Réalisation : `.pc-toolbar` est statique dans la feuille PC commune,
y compris sur Sites, Personnalités, recherche globale et catégorie. Conserver
le menu supérieur sticky, les filtres, la recherche et les URL existants.
L’accueil conserve sa recherche dans le hero ; référence mobile inchangée.

Critères : après défilement, seule la navigation supérieure reste visible,
la recherche quitte l’écran avec le contenu ; même comportement sur accueil,
Sites et Personnalités, repli étroit conservé. Recherche/filtres utilisables.
Maquette locale uniquement, sans données ni déploiement.

Contrôles navigateur du 26 octobre à 1280 px : sur Sites, après 720 px de
scroll, menu à y=16 px et bas de la recherche à y=-318 px ; sur l’accueil,
menu à y=16 px et recherche hors écran après 720 px. Sur Personnalités,
la courte page permet 345 px de scroll : la recherche remonte avec le contenu
(bas à y=57 px, sous le menu) et son style calculé est `static` ; menu à y=16 px.
La recherche n’est donc plus maintenue sous le menu. Capture temporaire :
`/tmp/reunion-pc-scroll-sites.png`. Les règles responsive utilisent maintenant
le même positionnement statique, sans exception à 850 px (contrôle de source).
`python3 -m compileall -q .`, `render.py --check` et contrôle des espaces réussis.
Changement limité au positionnement CSS et à cette fiche ; données, formulaires,
filtres et référence mobile inchangés. Maquette locale ; aucun déploiement.

## Cohérence des annuaires PC — 26 octobre 2026 (UX-PC-004)

Demande utilisateur explicite : le sous-titre **À découvrir** de la liste
Personnalités est inutile et incohérent avec Sites. Retirer ce sous-titre sans
en ajouter à Sites : les deux annuaires suivent titre de page → recherche →
catégories → cartes. Conserver le statut de pagination nécessaire à Sites.
Ce choix précise la présentation de la liste issue d’UX-PC-001/003 ; il ne
modifie pas le titre de découverte de l’accueil décidé par UX-PC-002.

Critères avant réalisation : aucun sous-titre **À découvrir** dans l’annuaire
Personnalités, région des cartes nommée pour l’accessibilité ; filtres, recherche,
état sans résultat et ouverture/retour de fiche conservés. Les titres de groupes
Sites/Personnalités restent utiles dans les résultats de recherche globale.
Périmètre : maquette PC locale et fiche dédiée, sans données ni déploiement.

Réalisé dans `pc-v1/content.js` : grille directement dans une section nommée
Personnalités, sans en-tête supplémentaire. Contrôle navigateur du 26 octobre :
trois cartes sans sous-titre ; Comédiens → Benji → fiche → retour avec Comédiens
conservé ; Toutes les catégories rétablit les trois profils. Rendu observé dans
le repli étroit de la maquette PC (461 px), capture temporaire
`/tmp/reunion-pc-coherence-personnalites.png`. Les titres des sections de recherche
globale et les branches recherche/état vide restent inchangés (contrôle de source).
`node --check`, compilation Python et contrôle des espaces réussis.
Relecture utilisateur attendue ; aucun déploiement.

## Filtres des annuaires PC — 26 octobre 2026 (UX-PC-003)

Source : demande utilisateur de retrouver les filtres Sites et Personnalités
« comme sur mobile ». UX-PC-001 excluait de nouveaux filtres sur PC ; cette
demande remplace cette exclusion pour les deux annuaires seulement. Reprendre
la sélection unique en pastilles d’UX-SITES-007 et UX-CREA-009, sous la recherche,
avec **Toutes les catégories**, sélection verte et état `aria-pressed`.

Recherche et catégorie se combinent ; `q` et `categorie` sont conservés dans
l’URL, l’historique, le rechargement et les retours depuis aide ou fiche. Changer
de catégorie ou rechercher ramène à la première page des sites. Effacer la
recherche conserve la catégorie ; l’état sans résultat permet d’effacer tous
les critères. Une catégorie inconnue est retirée explicitement de l’URL.
Conserver le focus sur la pastille activée et annoncer l’actualisation.

Conserver les sources et présentations PC : 56 sites, pagination par douze,
trois profils de démonstration et leurs fiches locales. Les neuf catégories de
sites et les trois catégories présentes sur ces profils sont proposées ; le
catalogue mobile de 29 profils n’est pas importé par cet ajustement. Aucun
renommage ou réaffectation de catégorie. Les pages catégorie et recherche globale
gardent leur parcours. Proposition et administration restent simulées/inchangées.

Critères avant réalisation : filtres visibles dans les deux annuaires,
sélection unique annoncée, combinaison recherche/catégorie, effacement séparé,
zéro résultat, pagination filtrée, URL et retours persistants, catégories
invalides normalisées, boutons utilisables au clavier et sans débordement.
Maquette PC locale uniquement ; aucune base, référence mobile ou publication.

Réalisé dans `pc-v1/content.js`, `app.css`, `sites.html` et
`personnalites.html`. Correction complémentaire de fermetures `details`
superflues laissées par UX-PC-002, sans modifier les autres parcours.

Contrôles navigateur du 26 octobre : neuf pastilles Sites plus Toutes les
catégories, trois pastilles Personnalités plus Toutes ; Transport = sept sites,
Santé = un site, Culture & Loisirs = douze puis six sites. Recherche Bus.re
combinée avec Transport = un site, combinée avec Santé = zéro ; effacer la
recherche conserve Santé, y compris au rechargement. Précédent depuis la seconde
page Culture & Loisirs rétablit la première et sa sélection. Comédiens activé
avec Entrée affiche Benji et conserve le focus ; sa fiche s’ouvre avec une URL
de retour comprenant le filtre. L’activation effective de ce retour a été
interrompue par l’arrêt de l’aperçu ; après relance, annuaires à nouveau ouverts.
Une catégorie inconnue avec page=5 rétablit Toutes les catégories et page 1.
Rendu observé à 461 px (repli) et 1265 px (PC), pastilles sur plusieurs lignes.
Captures temporaires : `/tmp/reunion-pc-sites-filtres.png` et
`/tmp/reunion-pc-personnalites-filtres.png`.

Contrôles de source : syntaxe JS, `render.py --check`, compilation Python,
espaces et équilibre des `details`. Référence mobile et données PC inchangées.
Limites : pas de catalogue de 29 profils ni d’audit exhaustif d’accessibilité ;
relecture visuelle utilisateur attendue. Finalisation Git isolée des autres
travaux selon la consigne commune du 5 octobre autorisant commit et fusion
locale sur main après contrôle. Le premier essai avait été refusé par le contrôle
automatique, faute d’autorisation explicite reconnue ; la consigne commune a
été relue et fournie lors de la reprise du 26 octobre. Aucun push ni déploiement.

## Ajustement demandé — 26 octobre 2026 (UX-PC-002)

Source validée : demande explicite de modification de la maquette PC dans le
chat du 26 octobre. Ce choix remplace, pour cet accueil PC seulement, le hero
en deux colonnes et son titre visible décrits par UX-PC-001 ; l’historique reste
conservé ci-dessous.

- Placer la photo locale de paysage en fond de la bannière de recherche, avec
  un voile clair et le formulaire opaque pour garder une recherche lisible.
- Déplacer le libellé visible dans le titre de la section des sites :
  **Sites réunionnais à découvrir**, à la place de **À découvrir**. Garder un
  titre principal accessible, sans répéter ce texte visuellement dans le hero.
- Sur les pages PC, replier le comparateur de versions dans **Outils de la
  maquette**, fermé au chargement, comme dans la maquette mobile finale. Les
  versions restent accessibles après ouverture, y compris sans JavaScript.

Critères : photo derrière la recherche et plus d’image à côté ; titre visible
unique au-dessus des cartes ; recherche fonctionnelle ; outils fermés au
chargement, ouvrables au clavier, liens conservés ; repli lisible sur petit écran.
Périmètre : maquette locale PC et documentation ; aucune intégration Flask,
modification de la référence mobile, nouvelle donnée ou publication.

Réalisé dans `maquettes/pc-v1/accueil.html`, `app.css` et les onze pages HTML PC.
Contrôles du 26 octobre : rendu observé au navigateur intégré (1265×712),
photo derrière la recherche et nouveau titre ; recherche Bus.re → résultat réel
local ; outils fermés au chargement sur l’accueil et la recherche, ouverture
à la souris puis fermeture avec Entrée. Le contrôle statique des onze pages
confirme un unique `details` fermé contenant tous les liens de comparaison.
`render.py --check`, `python3 -m compileall -q .` et `git diff --check` réussis.
Le générateur conserve les wrappers repliables. Repli CSS adapté aux petits
écrans ; pas de nouvelle vérification visuelle multi-largeur pour cet ajustement.
Relecture visuelle utilisateur attendue ; aucun déploiement.

| Métadonnée | Valeur |
| --- | --- |
| Date | 22 octobre 2026 |
| Statut | Réalisée et vérifiée localement ; validation visuelle utilisateur attendue |
| Décision | UX-PC-001 |
| Sources | Audit DESKTOP_MOCKUP_AUDIT_2026-10-22.md ; confirmation utilisateur puis « vas-y bosse » |

## Périmètre autorisé

Créer une nouvelle variante ordinateur indépendante, sans modifier la version
mobile retenue. L’utilisateur délègue les choix d’exécution issus de l’audit.
Les modifications des références existantes se limitent aux outils de comparaison :
lignes distinctes Versions mobile et Versions PC, dates/heures et tri par groupe.
L’autorisation permet cette variante de maquette, pas un déploiement ou une refonte
Flask. Les autres idées mobile du ticket #44 restent différées.

## Choix d’exécution pour PC seulement

- Dossier autonome maquettes/pc-v1/ et pages de navigation propres ; aucun script,
  style, donnée ou carte de la version mobile modifié hors bandeaux de versions.
- Menu supérieur commun conservé pendant le défilement, même cadre vert/crème,
  contenu plus ample (1280 px maximum), recherche et grille alignées.
- Accueil : trois mêmes sites en premier, cartes visuelles 16:9 avec description
  déjà présente dans l’annuaire. Personnalités ensuite, portraits plafonnés à
  leur définition réelle (150 px), sans nouvelle image ni effet d’agrandissement.
  Photo locale existante réutilisée ; aucun ancien slogan supprimé réintroduit.
- Annuaire PC : grille cohérente de cartes de sites, ordre alphabétique, recherche
  textuelle, douze sites par page, pagination explicite et critères conservés dans
  l’URL. Pas de nouveaux filtres, favoris, classement de clics ou règle de publication.
- Recherche PC, annuaire et catégories utilisent le même instantané local des
  56 sites publiés déjà présents ; aucun accès base ni nouvelle collecte.
- Trois fiches de personnalités locales, uniquement les informations existantes
  et leurs images facultatives. Aucun enrichissement biographique inventé ni badge.
- Proposition/confirmation/aides reprennent le parcours simulé et les obligations
  actuelles. Aucun envoi réel ni nouveau droit contributeur/admin.
- Citron remplacé par les accents verts dans cette variante PC. Tutoiement dans
  tous les textes nouveaux ; textes légaux/citations repris sans remplacement global.

## Parcours à vérifier

Visiteur : accueil → annuaire paginé/recherche → site externe (nouvel onglet),
catégorie ou personnalité → retour avec critères/page ; menu et actions accessibles
pendant le défilement. Recherche Bus.re/Infinity Park doit retrouver les vrais sites.
Contributeur : proposition locale, erreurs/duplicata simulés, confirmation puis
retour d’origine, sans enregistrement. Aides : origine conservée, retours bornés
aux pages locales autorisées, aucune redirection externe introduite.

Versions : depuis chaque comparaison, ouvrir les références mobile ou PC sans
mélanger les parcours. PC possède ses pages ; références mobiles gardent leurs
comportements et leur navbar. Une URL PC ouverte sur petit écran reste un aperçu
PC avec repli lisible ; elle ne remplace pas la version mobile retenue.

## Acceptation avant livraison

1. Aucune modification des fichiers d’interface mobiles, scripts ou ressources,
   hors bandeaux de comparaison et leur style spécifique ; contrôle contre main.
2. PC sans débordement à 1024/1366/1440/1920 px ; cadre commun, menu au défilement,
   portraits non agrandis, images manquantes explicites, textes longs lisibles.
3. 56 sites et 45 captures conservés ; pagination cinq pages de douze, filtre,
   réinitialisation, retour navigateur et rechargement cohérents ; pas de doublon/perte.
4. Recherche commune des sites et des trois profils cohérente avec l’annuaire,
   fiches et retours accessibles, navigation clavier et contrastes vérifiés.
5. Proposition et confirmation simulées, états vides/erreur et aides contrôlés.
6. Deux groupes PC/mobile datés et triés dans toutes les comparaisons ; chemins
   locaux valides sur localhost/LAN, archive modifiée seulement dans son bandeau.
7. Syntaxe, contrôles de source et vérification navigateur proportionnés ; docs,
   preuves et ticket #45 actualisés. Version PC à relire, pas déclarée retenue.

## Réalisation et vérification locales — 22 octobre 2026

| Exigence | Réalisation | Contrôle |
| --- | --- | --- |
| Isolation | Dossier `maquettes/pc-v1/`, menu supérieur commun | Les sept accueils de référence sont identiques à main après retrait du seul bandeau et normalisation du cache CSS de comparaison ; scripts, cartes, assets et navbar mobile inchangés |
| Composition PC | `app.css`, `accueil.html`, `home.js` | Accueil observé à 1024×900, 1366×768, 1440×1000 et 1920×1080 ; trois colonnes de sites, largeur maximale 1280 px, pas de débordement horizontal ; 1366×768 montre les noms des sites dès le premier écran |
| Données | `data.js` et `content.js` | 56 IDs uniques, 45 captures locales, neuf catégories ; pagination réelle 12/12/12/12/8 observée, conservation des deux entrées Cinépalmes distinctes |
| Recherche et retours | `content.js`, `app.js` | Bus.re trouvé dans l’annuaire, Infinity Park par recherche globale ; filtre Harendra, rechargement, effacement, historique navigateur et retour de fiche avec q conservé ; liens aide et proposition prennent les critères courants |
| Parcours de contribution | `proposer.js`, `proposition-confirmee.html` | Catégorie Transport préremplie ; envoi vide affiche trois erreurs et focalise le nom ; données de test valides mènent à la confirmation simulée et au retour catégorie ; doublon Bus.re désactive l’envoi et ouvre son résultat réel |
| Portraits et accès | `home.js`, `profile.js`, `app.css` | Images existantes chargées, 96 px sur les cartes et 150 px maximum sur fiche ; source 150 px ; profil Harendra local, aucun lien inventé ; focus clavier visible 3 px et lien d’évitement accessible |
| Comparaison | `versions/catalog.json`, `versions/render.py`, `mockup-versions.css` | Deux groupes datés/triés ; 171 destinations de comparaison vérifiées statiquement ; index → mobile retenue → PC testé au navigateur, mobile 390 px sans débordement et navbar conservée |

Le menu reste visible pendant la pagination/défilement ; le changement de page
ramène au statut des résultats, sans rester au pied de la liste. Les états
vide/chargement/erreur sont explicites et simulés, avec action de reprise. Les
retours sont bornés aux pages autorisées du dossier PC (URL externes, scripts et
autres dossiers refusés). Les aides reprennent les textes existants ; la revue
indépendante a comparé leur contenu à la référence, sans réécriture juridique.

Contrôles de source : `node --check` sur les six scripts PC,
`python3 -m compileall -q .`, `git diff --check`, rendu `--check` idempotent et
manifestes courants des trois archives vérifiés (60/56/105 entrées).
Revue statique indépendante et contrôle navigateur par l’agent principal.
Les couleurs principales vert #087548/blanc offrent un contraste d’environ
5,7:1 ; ce contrôle ponctuel et le test clavier ne constituent pas un audit
exhaustif d’accessibilité.

Limites : instantané local, pas de synchronisation avec la base ; 11 sites sans
capture conservent leur remplacement explicite. Les portraits et les droits des
images ne sont pas enrichis par cette variante. Les profils restent limités aux
faits disponibles. Aucun formulaire ne transmet ou n’enregistre de proposition.
Le rendu mobile de la variante PC est un repli de consultation ; la référence
mobile reste l’URL dédiée. La validation visuelle de la PC V1 par l’utilisateur
reste attendue ; ticket Dashboard #45 à vérifier, intégration Flask hors périmètre.

Aperçu local/LAN : `http://192.168.1.14:8026/maquettes/pc-v1/accueil.html`.
Les captures de contrôle restent temporaires hors Git. Le port 8026 expose
uniquement les chemins publics filtrés de la maquette locale.

Provenance de la PC V1 : commit `c781bef`, daté du `2026-10-22T19:44:13+04:00` ; cette date
est reprise par le catalogue et les bandeaux, sans date manuelle fictive.
