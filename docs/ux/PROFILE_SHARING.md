# Partager une fiche de personnalité — simulation validée

| Métadonnée | Valeur |
| --- | --- |
| Version | 1.3 |
| Date | 11 novembre 2026 |
| Statut | Référence visuelle validée ; partage avec icône dans la ligne des réseaux sur DEV |
| Périmètre autorisé | Simulation historique mobile-final ; reprise du style sur DEV dans la refonte autorisée, sans extension du partage |
| Suivi | Dashboard Réunion Wiki, ticket #44 ; notifications réelles distinctes au #47 |

## Décisions applicables — UX-SHARE-001 v1.2

### Choix A validé le 11 novembre 2026 — icône et placement adaptatif

Après la correction initiale du style, l'utilisateur valide « okay vas y » pour
la proposition A : **icône de partage à gauche, texte « Partager cette fiche »
à droite**, après les liens des réseaux dans leur ligne lorsque la largeur le
permet. Sur petit écran, les actions passent naturellement à la ligne pour
rester lisibles. Cette décision remplace le placement séparé après le bloc
officiel de v1.1 ; elle ne change ni l'ordre logique réseaux → partage → correction,
ni le style secondaire vert souligné, le fond transparent et la cible de 44 px.

L'icône est décorative (aria-hidden), sans nom annoncé en double ; le nom
accessible reste le texte complet. Le partage reste identifiable comme action
du site par son style discret, distinct des liens de réseaux en boutons.
Une fiche sans lien officiel conserve un seul partage après sa présentation.
Une fiche introuvable ou non publiée n'affiche aucune action de partage.

Portée : templates et styles de la refonte DEV, reprise de la copie de lien
déjà livrée. Pas de partage natif, de nouvelle destination ou de mesure d'envoi.
Schéma, tests et preuves :
[partage dans la ligne des réseaux](../development/PROFILE_SHARE_INLINE_DEV_2026-11-11.md).

## Historique — application de UX-SHARE-001 v1.1

### Application du style à DEV — 11 novembre 2026

La refonte DEV autorisée dans [REFONTE_DEV.md](REFONTE_DEV.md) fournit déjà
un dialogue de copie réelle du lien, distinct de la simulation du 26 octobre.
L'utilisateur demande de corriger l'apparence native du déclencheur en suivant
la procédure de modification DEV. Les choix visuels UX-SHARE-001 v1.1 ci-dessous
restent inchangés : texte vert souligné, sans fond/bordure, 13 px et cible 44 px,
après les liens officiels. La règle manquante est ajoutée à
`static/refonte/components.css`. Aucun nouveau comportement de partage, parcours,
API ou envoi n'est ajouté. Contrat et preuves :
[correction du style DEV](../development/PROFILE_SHARE_STYLE_DEV_2026-11-11.md).
Les descriptions de simulation ci-dessous restent historiques sur le comportement.

Correction explicite de l’utilisateur le 26 octobre : « partager le profil ça
vient après les liens officiels et plus discret aussi ». Ce choix remplace
l’emplacement 1A initial et son bouton plein : action texte verte sans fond ni
bordure, taille secondaire, après le bloc de liens officiels et avant le lien
de correction. Cible tactile d’au moins 44 px et focus visible conservés.
Sans liens officiels, l’action reste après la présentation. Texte partagé,
menu simulé et absence d’envoi réel restent ceux de 2A/3A.

Réponse utilisateur du 26 octobre : **« 1a 2a 3a vas y »**.

- **Emplacement révisé** : action discrète **Partager cette fiche** après les
  liens officiels, sur chaque fiche publique disponible. Pas de bouton ajouté aux cartes.
- **2A** : titre **[Nom] — Réunion Wiki**, texte **Découvre [Nom] sur Réunion Wiki.**
  et lien de la fiche. Le nom vient du catalogue ; pas de portrait envoyé.
- **3A** : menu de démonstration uniquement dans la dernière maquette. Exemples
  d’applications : WhatsApp, Messenger, Messages et Mail, plus **Copier le lien**.
  Choisir une application affiche ce qui se passerait ensuite ; aucune application
  externe, requête, transmission ou sélection réelle de contact n’est déclenchée.
  La copie est elle aussi simulée et annoncée comme telle, sans accès au presse-papiers.
- Le menu indique **Démonstration · aucun envoi réel** et rappelle que les
  applications réelles dépendront du téléphone. Ce dessin illustratif n’est pas
  présenté comme une reproduction exacte du menu système ou un menu natif.
- Lien de démo absolu vers `personnalite.html?id=[id]` sur l’origine utilisée,
  sans `retour`, recherche, filtre ou fragment. Il est explicitement local à la
  maquette : aucun domaine public ou chemin de production n’est inventé.
- Menu modal accessible : titre associé, focus à l’ouverture, parcours clavier
  contenu dans le dialogue, fermeture par croix, **Annuler** ou Échap ; focus
  rendu au déclencheur, fiche, URL et critères conservés. Si le catalogue change,
  fermer le menu avant de réafficher la fiche. Pas de menu sur une fiche introuvable.
- Le partage réel HTTPS, sa copie de secours, les aperçus dans les messageries
  et l’inclusion au MVP restent des évolutions distinctes. Les autres pistes PWA
  restent reportées comme indiqué ci-dessous.

### Critères définis avant réalisation

Vérifier emplacement et phrase pour plusieurs profils ; unicité du menu ;
actions simulées sans appel à `navigator.share`, au presse-papiers ou à une app ;
lien propre ; fermeture/Échap et restitution du focus ; fiche introuvable ;
absence de débordement à 320/390 px et repli ordinateur. Inspecter le rendu,
la console et les contrôles clavier ; consigner les preuves dans
`../testing/PROFILE_SHARING_REVIEW_2026-10-26.md`.

### Réalisation et vérification

Simulation dans `maquettes/mobile-final/public.js` et `public.css`. Contrôles
navigateur sur Harendra et Fishing à La Réunion, 320/390/1280 px, actions fictives,
fermetures, focus, lien nettoyé, accès LAN et fiche introuvable réussis.
[Preuves et limites](../testing/PROFILE_SHARING_REVIEW_2026-10-26.md).
La copie reste fictive ; le lien affiché n’est accessible que sur le PC ou le
réseau local concerné. Aucun partage réel, métadonnée sociale ou backend ajouté.

## Historique de la discussion initiale — remplacé par les choix ci-dessus

L’utilisateur souhaite retenir le partage d’une personnalité et discuter de son
fonctionnement avant réalisation : « il faut documenter donc on en parle avant ».
`CREATOR_PROFILE.md` définit la lecture, les liens officiels, le retour et les
corrections mais pas ce partage. Aucun bouton, API de partage ou parcours
supplémentaire n’est ajouté à la maquette lors de cette conservation.

L’intérêt pour cette fonction ne valide pas son emplacement, son contenu, une
inclusion au MVP, ni une réalisation sur le site public. Le présent brouillon
ne change pas UX-FICHE-001 ou les règles de visibilité des fiches.

## Historique — proposition de parcours avant arbitrage

1. Visiteur sur une fiche publiée → bouton explicite **Partager cette fiche**.
   Aucun compte ou contact personnel n’est nécessaire au parcours proposé.
2. Sur appareil compatible et après l’appui : menu de partage du système,
   via Web Share. Le visiteur choisit l’application et le destinataire ; les
   applications proposées dépendent du téléphone. Aucun envoi automatique.
3. Proposer le lien public stable de la fiche, sans le paramètre de retour,
   filtre de recherche ou état de session de la personne qui partage. Titre
   proposé : **Harendra — Réunion Wiki** ; phrase proposée : **Découvre Harendra
   sur Réunion Wiki.** Ce sont des exemples à valider.
4. Si le partage système est absent ou échoue : permettre **Copier le lien**,
   avec confirmation uniquement après copie effective. Si la copie est bloquée,
   afficher le lien sélectionnable et une instruction simple de copie manuelle.
   L’annulation du menu laisse la fiche intacte, sans message d’erreur alarmant.
5. Le destinataire ouvre la fiche publique directement, sans compte/PWA
   obligatoires ; retour par défaut vers l’annuaire des personnalités. Une fiche
   archivée ou indisponible garde l’état introuvable existant sans information privée.

L’API peut ne pas conserver tous les champs selon l’application cible ; ne pas
promettre un texte, une image ou un aperçu identique dans chaque messagerie.
Le succès de l’appel ne prouve pas que le destinataire a reçu ou lu le message.
Pas de nouvelle mesure d’envoi, liste de contacts ou compteur proposée ici.
Les contributeurs et administrateurs gardent les parcours actuels ; aucun
partage public de brouillon ou bouton admin supplémentaire n’est prévu.

## Historique — choix ouverts avant les réponses 1A/2A/3A

**Emplacement** : recommandation sous la présentation, avant les liens officiels,
pour distinguer l’action Réunion Wiki des réseaux de la personne. Alternative
compacte près du nom, mais risque de surcharge avec les noms longs ; autre
possibilité en fin de fiche, moins visible. Aucun choix encore retenu.

**Contenu** : recommandation nom + courte phrase neutre + lien ; alternative
lien seul. Le portrait n’est pas un fichier partagé par défaut. Un futur aperçu
de lien (titre/image/description) demanderait un contrôle des métadonnées publiques
et des images autorisées ; sa présentation dépendrait de la messagerie.

**Maquette et réel** : recommander d’abord une simulation clairement annoncée,
puis l’intégration réelle sur HTTPS après validation du parcours. Un lien PC/LAN
de maquette ne devient pas partageable publiquement ; aucun domaine public ou
accès extérieur n’est publié pour ce travail. Web Share dépend d’un contexte
sécurisé et de la compatibilité navigateur ; ne pas promettre le menu natif sur
l’aperçu HTTP accessible par IP locale.

## Autres pistes PWA conservées pour plus tard

L’utilisateur reporte les favoris, notifications réelles choisies, consultation
hors connexion, raccourcis sur l’icône et proposition d’un lien reçu par le menu
de partage. Ce report ne supprime pas les simulations de notifications déjà
validées dans mobile-final. #44 conserve les pistes mobile/PWA ; #47 porte déjà
les annonces push réelles. Pas d’élargissement implicite du lancement ni de
développement de ces pistes à partir de cette demande.

## Historique — vérifications envisagées avant arbitrage

Conception à compléter avec les réponses, puis critères de contrôle proportionnés :
emplacement mobile/ordinateur, nom long, menu natif disponible/absent, annulation,
copie réussie/refusée, lien propre, ouverture directe et contenu indisponible.
Ce sont des contrôles envisagés, aucun test ou rendu n’est déclaré réalisé.

Référence technique consultée le 26 octobre :
[Navigator.share — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share).

## Historique

| Version | Date | Évolution |
| --- | --- | --- |
| 1.3 | 11 novembre 2026 | UX-SHARE-001 v1.2 : choix A, icône à gauche du texte et action après les réseaux dans une ligne adaptative ; repli sans liens conservé. |
| 1.2 | 11 novembre 2026 | Application du style déjà validé au déclencheur de la refonte DEV ; comportement de copie existant inchangé, historique de simulation conservé. |
| 1.1 | 26 octobre 2026 | Après essai, emplacement après les liens officiels et bouton texte discret demandés ; remplace 1A et le bouton plein. 2A/3A conservés. |
| 1.0 | 26 octobre 2026 | Réponses 1A/2A/3A puis réalisation demandée : simulation dans la dernière maquette ; critères définis avant code. |
| 0.1 | 26 octobre 2026 | Besoin retenu pour discussion ; propositions explicites et autres pistes différées, aucun code modifié. |
