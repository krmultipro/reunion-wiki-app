# Pied de page et pages d’aide — cadrage UX

## Navigation des variantes de maquette — 22 octobre 2026

[UX-HOME-024](HOME_PAGE.md) complète ce parcours : les liens entre pages partagées
conservent la version d’accueil via un contexte d’URL explicite autorisé ;
Accueil/logo revient à cette version. Les retours intermédiaires gardent leur
page d’origine et leurs critères. Dans l’essai Navigation flottante seulement,
les quatre rubriques restent accessibles en bas sur mobile ; les autres versions
conservent leur menu. Aucun changement des règles métier ou du backend.

| Métadonnée | Valeur |
| --- | --- |
| Version | 0.7 |
| Date | 17 octobre 2026 |
| Statut | 1A/2A/3A/5A et absence de Blog au footer validés |
| Réalisation | Trois maquettes et footer commun réalisés et contrôlés localement ; backend inchangé |

## Décision applicable — créateurs de contenu, 17 octobre 2026

Le [périmètre de lancement](CONTENT_CREATORS_SCOPE.md) remplace l’ouverture générale aux
Talents péi du 16 octobre : **créateurs de contenu**, rubrique **Créateurs** et
**Proposer un créateur**. Les autres talents restent une piste reportée.
Les compléments du 16 octobre ci-dessous sont historiques sur le nom et
l’élargissement ; ils ne doivent pas guider une adaptation artiste/artisan.
RM-TAL-012 v2.0 et UX-CONT-001 à 006 font référence.

Nom et lien officiel restent obligatoires à la proposition (UX-PROP-002), sans
compte au lancement ; aucune proposition sans lien ajoutée. Contact/email pour
les corrections et retraits, tableau de bord différé. Les choix de présentation
et de navigation existants sont conservés. Documentation seule : aucun code,
maquette ni test fonctionnel modifié ou exécuté.

## Historique — complément Talents péi du 16 octobre 2026, remplacé sur le périmètre

La [fiche de périmètre](TALENTS_PEI_SCOPE.md) fait référence : UX-TAL-001 à
006 et RM-TAL-012, personnes et collectifs, dont artistes et artisans ; fiches
d’entreprises hors de cette rubrique au lancement. La FAQ cible doit expliquer qui peut être proposé (soi ou un tiers), la modération et les demandes de correction/archivage/retrait par Contact/email avec contrôle d’identité. Aucune promesse de compte ou d’édition immédiate au lancement.

Ce complément remplace les libellés génériques Créateurs dans la conception
cible ; les décisions et comptes rendus antérieurs ci-dessous restent historiques.
Aucun changement de maquette, code, URL ou modèle de données réalisé ; aucune
nouvelle vérification visuelle ou fonctionnelle. Le tableau de bord est différé.
Les points ouverts du cadrage restent à trancher avant les adaptations dépendantes.

## Sources et autorisation

Demande utilisateur : compléter les écrans FAQ, Contact et Mentions légales,
avec leurs accès depuis le pied de page, avant de considérer le lot complet.
Sources : PRODUCT.md, section Information et contenu (document encore brouillon),
BUSINESS_RULES.md RM-TAL-007 amendement 1.1 (correction via contact/email),
CREATOR_PROFILE.md UX-FICHE-003 (contact existant), UX-GEN-006/008/009,
ADR-001 ; code existant listé ci-dessous. Une proposition ne vaut pas validation.

## État observé dans les fichiers

- `templates/base.html` : pied de page en trois colonnes ; Tendances, Proposer
  un site vers Instagram, Blog, FAQ, Mentions légales et Contact. Le lien
  Instagram de proposition diverge du parcours commun Proposer déjà validé.
- `templates/faq.html`, route `/faq` dans `reunion_wiki/routes/public.py` :
  20 questions en details/summary, principalement sites/catégories ; absence
  de questions sur les créateurs et présentation du projet limitée aux sites.
  Certaines réponses décrivent une proposition ou des réseaux du footer qui
  ne correspondent pas aux accès actuels. JSON-LD à synchroniser avec le texte
  si la FAQ est révisée lors de l’intégration ; pas de modification backend ici.
- `templates/legal-notices.html`, route `/mentions-legales` : texte existant,
  coordonnées, hébergement, droits, statistiques, données/cookies et retour
  accueil. Lecture des fichiers seulement, aucune certification de conformité
  juridique ni vérification des coordonnées ou traitements actifs.
- Pas de route/page Contact dédiée trouvée dans les routes publiques : lien
  vers `https://forms.gle/GScJkMiEZXVSted78`. Contenu/champs et réception de ce
  formulaire non vérifiés ; aucun envoi réalisé.
- Maquettes : accueil/liste/catégorie/recherche principalement équipés de notes
  d’aperçu ; fiche avec liens Mentions légales distantes et Contact externe.
  Aucun pied de page commun complet ni FAQ/Contact/légal local en style C.

## Choix initiaux — réponses 1A/2A/3A validées

1. Contact : A recommandé, petite page locale expliquant les motifs utiles
   (question, lien incorrect, correction/retrait de fiche) et un bouton vers le
   formulaire existant. Lien Proposer séparé vers le parcours déjà validé.
   B, lien direct vers le formulaire, une étape en moins mais pas d’explication
   locale. Nouveau formulaire interne/report de traitement non proposé au MVP.
2. FAQ : A recommandé, 6 à 8 questions courtes sur le service, sites/créateurs,
   recherche, proposition, modération sans délai promis, correction/retrait,
   gratuité ; accordéons natifs fermés par défaut. B, conserver les 20 questions
   en les actualisant : davantage de contenu, plus de maintenance et longueur.
   Le nombre exact et les réponses seront préparés après choix, sans inventer
   garanties de sélection, notifications ou délais.
3. Pied de page : A recommandé, ligne compacte FAQ · Contact · Mentions légales,
   avec nom du site, même disposition logique sur toutes les pages, liens
   pouvant revenir à la ligne sur mobile ; navigation principale déjà présente.
   B, ajouter Blog à ces liens pour conserver sa découvrabilité depuis le footer.
   La route Blog et les autres URLs existantes sont conservées dans les deux cas.
   Tendances reste accessible sur l’accueil conformément à UX-GEN-009.

## Périmètre et contrôles à préparer après validation

Maquettes seulement, ressources locales et finitions C, texte lisible, liens
avec cibles tactiles de 44 px, parcours clavier/focus et contrôle mobile/PC.
Présenter explicitement la sortie vers le formulaire externe ; ne pas simuler
un envoi réussi ni une réception confirmée. Conserver le canal de correction
existant. Mentions légales : proposer une mise en page du contenu existant,
sans réécrire les déclarations sensibles pour les aligner artificiellement sur
la maquette. Vérification juridique/traitements réels distincte avant publication.
Choix 5A explicitement validé : les pages d’aide reviennent à la page d’origine
avec un libellé clair ; accès direct vers accueil. Conserver les critères de
la page d’origine et n’accepter que des destinations locales autorisées.

Contrôles prévus : footer → chaque page → navigation de retour ; FAQ → Proposer
et Contact ; fiche → contact de correction ; liens internes locaux, absence
 de débordement mobile, fonctionnement des accordéons et distinction aide/
proposition. Proposer → confirmation reste le parcours déjà documenté.

## Décisions et examen du Blog — 8 octobre 2026

1A : page Contact locale avec explication courte et accès au formulaire existant.
2A : FAQ courte de 6 à 8 questions dépliables, sites et créateurs.
3A : pied de page compact FAQ · Contact · Mentions légales.
5A : retour à l’origine depuis les pages d’aide, accueil en accès direct.

Demande supplémentaire : examiner le Blog avant de conseiller son accès.
Lecture de `templates/blog.html` et consultation navigateur de
`https://reunionwiki.re/blog` : page publique contenant un seul article de
présentation « Les meilleurs sites internet de La Réunion en 2026 », avec
explication du portail et liens par catégories ; cette page ne présente pas
un index de plusieurs articles. Aucune fréquentation mesurée dans cette revue.

Recommandation : garder 3A au lancement et conserver `/blog` ; le contenu
actuel apporte surtout une présentation du service, partiellement redondante
avec l’accueil/FAQ. Le titre promet une sélection de meilleurs sites alors que
le corps présente principalement des catégories. Ne pas ajouter un espace
éditorial implicite ni supprimer sa route/SEO. Si un accès au footer est
souhaité malgré 3A, le libellé « Le projet » serait plus fidèle après adaptation
éditoriale à valider ; cela reste une proposition, aucune modification réalisée.

## Plan d’application validé — 8 octobre 2026

Confirmation utilisateur : appliquer FAQ · Contact · Mentions légales au
lancement ; signaler toute nouvelle ambiguïté. Aucun autre choix bloquant
repéré après relecture indépendante. Blog conservé dans Flask, absent du
footer de ces maquettes. Trois pages locales : faq.html, contact.html,
mentions-legales.html ; pied de page commun des parcours principaux et des
pages d’aide. Notes de démonstration conservées séparément du footer produit.

FAQ : huit questions : utilité du service, gratuité, recherche, proposition,
vérification avant publication, délai variable sans promesse, demande de
correction/retrait, signalement d’un lien défectueux. Réponses fondées sur les
parcours validés ; aucun ajout de garanties ou de compte utilisateur.
Contact : expliquer question/signalement/correction-retrait et demander URL et
précision utile ; bouton unique vers formulaire externe existant, Proposer
comme lien secondaire. La correction depuis la fiche passe par cette page
Contact, puis le même formulaire existant (UX-FICHE-003, pas de formulaire neuf).
Légal : reprendre le corps existant dans une présentation C lisible, titre H1,
liens externes indiqués ; pas de certification juridique des textes.

Retour : transmettre une URL locale autorisée incluant les critères ; une
navigation FAQ → Contact conserve le contexte de FAQ pour pouvoir ensuite
revenir à sa page d’origine. Origine absente/externe/inconnue → accueil.
Les brouillons de formulaires ne sont pas sauvegardés par les pages d’aide ;
la protection de sortie existante reste applicable.

## Réalisation et vérification locale

Pages faq.html (8 accordéons), contact.html, mentions-legales.html réalisées.
Styles et transmission des retours partagés dans support-pages.css/js ; footer
statique identique sur 11 pages (3 aides et 8 parcours principaux), fonctionne
sans JS avec destinations directes. Le JS conserve les origines/critères.
Anciennes notes de maquette conservées en aside, séparées du footer produit.

Contrôles navigateur du 8 octobre 2026 : catégorie emploi, q=formation et commune
Saint-Denis → FAQ → réponse correction → Contact → FAQ → catégorie : critères
retrouvés. Fiche Adriana → Contact → fiche : retour de fiche vers liste
q=adriana conservé. Contact en accès direct → accueil ; origine externe dans
mentions ignorée → accueil. Huit accordéons fermés au chargement ; ouverture
clavier Enter et focus visible contrôlés sur le premier. Contact, FAQ et légal
sans débordement horizontal à 320 px ; Contact observé à 390 px et 1440 px,
footer accueil trois liens avec hauteur 44 px vérifiée sur PC.

Texte légal comparé au template existant : mêmes déclarations, seul libellé
du lien OVHcloud et niveaux des titres adaptés. Formulaire externe : cible,
nouvel onglet, noopener/noreferrer et explication vérifiés ; aucun envoi et
aucune vérification de sa réception. node --check support-pages.js et
git diff --check réussis. Pas d’audit WCAG complet ni d’intégration Flask ;
maquettes à relire visuellement par l’utilisateur avant finalisation du lot.
Captures temporaires : /tmp/reunion-wiki-faq-mobile.png et
/tmp/reunion-wiki-contact-mobile.png.

## Ton — correction explicite du 8 octobre 2026

Tutoiement du visiteur et absence de nous/notre/nos dans la voix du service,
selon le guide éditorial canonique. Contact/FAQ et les autres maquettes sont
harmonisés ; ancien titre « Comment pouvons-nous vous aider ? » remplacé par
« Une question, un signalement ou une correction ? ». Aucun texte légal réécrit.

## Formulaire Google existant — suivi du 8 octobre 2026

L’utilisateur demande de conserver sa révision : ticket Dashboard Réunion Wiki
#24 « Revoir le formulaire Google Contact pour les parcours publics », À faire,
enregistré et relu sur le VPS. La maquette valide l’accès, pas le contenu du
formulaire ni sa réception. Lors de sa reprise, examiner champs, questions,
ton au tutoiement, correction/retrait et message final ; documenter les choix
avant toute modification. La création du ticket ne lance aucune édition ou
soumission réelle du Google Form. Le suivi des tâches reste dans le Dashboard.

## Historique

| Version | Date | Modification |
| --- | --- | --- |
| 0.7 | 17 octobre 2026 | Retour aux créateurs de contenu pour le lancement ; ouverture Talents péi reportée, lien officiel conservé, documentation seule. |
| 0.6 | 16 octobre 2026 | Complément Talents péi : périmètre et libellés cibles, parcours conservés ; maquettes et preuves antérieures non actualisées. |
| 0.5 | 8 octobre 2026 | Règle de ton durable consignée dans guide éditorial et AGENTS ; maquettes harmonisées au tutoiement, voix collective retirée. |
| 0.4 | 8 octobre 2026 | Trois pages et footer 11 pages réalisés ; retours en chaîne, mobile, clavier et texte légal contrôlés localement. |
| 0.3 | 8 octobre 2026 | Footer sans Blog confirmé ; plan, huit sujets FAQ et critères de retour fixés avant adaptation locale. |
| 0.2 | 8 octobre 2026 | Réponses 1A/2A/3A et 5A consignées ; Blog public lu, recommandation distincte de la réalisation. |
| 0.1 | 8 octobre 2026 | Audit des fichiers et lacunes consignés ; propositions Contact/FAQ/footer ouvertes avant modification. |

## Relecture et validation du 17 octobre 2026

L’utilisateur confirme que la présentation publique et les parcours vus lui
conviennent et demande la finalisation des contrôles. Preuves et limites
actuelles : [revue finale](../testing/MAQUETTE_FINAL_REVIEW_2026-10-17.md).
Messages au tutoiement et libellés créateurs harmonisés dans la maquette ;
aucune intégration Flask ni publication. Le contrôle mobile des quatre
rubriques admin historiques est maintenant observé à 320/390 px effectifs ;
l’extension admin V1 non réalisée reste au suivi #34, sans validation implicite.
Les mentions d’attente antérieures restent historiques et ne rouvrent pas
les choix publics déjà validés.
