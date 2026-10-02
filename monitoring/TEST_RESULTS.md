# Tests de résistance du monitoring — 2 octobre 2026

Version initialement en production : `a4cff08df7d64c9f92edcace7b38be2b229dc510`.
Les tests étendus ont été exécutés séparément ; les services réels et le chat
Telegram n'ont pas été utilisés comme cibles de panne. Leurs corrections sont
incluses dans la version qui ajoute les commandes privées et la façade Docker.
Voir aussi [COMMANDS_SECURITY.md](COMMANDS_SECURITY.md).

## Défauts reproduits et corrigés dans le candidat

1. Après une réponse Telegram 429 avec `retry_after`, un autre message de la file
   pouvait partir avant la fin du délai. Le délai est désormais **global**, enregistré
   dans SQLite et appliqué aussi après redémarrage. Les échecs réseau bénéficient
   également de cette pause pour éviter de multiplier les requêtes pendant une panne.
2. Un `retry_after` mal formé pouvait lever `ValueError` et arrêter le bot.
   Une réponse incorrecte est désormais traitée comme un échec avec réessai.

Les tests correspondants échouaient sur la version initiale et passent sur le candidat.

## Résultats

| Scénario | Méthode | Résultat |
|---|---|---|
| Suite Python | 10 tests initiaux et 5 tests de résistance, local et conteneur candidat | 15 tests passent |
| Coupure réseau prolongée | Connexions TCP refusées vers un port local ; 24 heures virtuelles, avec 24 fermetures/réouvertures de SQLite, puis serveur HTTP local rétabli | 20 alertes conservées puis 20 livrées, sans doublon dans ce scénario |
| Charge | 50 000 lignes, dont 5 000 erreurs identiques, ingestion puis relecture des mêmes lignes | Une première alerte et un résumé de 4 999 répétitions ; aucune répétition due à la relecture |
| Transaction interrompue | Ingestion annulée avant commit SQLite, puis relecture | Curseur non avancé et alerte récupérée |
| Rotation réelle Docker | Conteneur jetable `json-file`, 64 Ko × 3 fichiers, 12 000 lignes | Toutes les lignes encore conservées par Docker sont détectées ; les lignes déjà effacées sont irrécupérables |
| Redémarrages réels | Bot candidat sans réseau, identifiants fictifs, volume SQLite dédié, trois redémarrages Docker | Curseur et alertes conservés, reprise de la boucle |
| Retour arrière réel | Installation Compose jetable ; exécution du heredoc de rollback du script de déploiement, avec chemins/projet/tags remplacés | Ancienne image/configuration et faux fichier privé restaurés ; volume d'état conservé |

L'ingestion et la relecture des 50 000 lignes ont pris environ 1,2 s en local
et 2,6 s dans le candidat sur le VPS, sur cette exécution. Ce n'est pas un
engagement de performance et la mémoire maximale n'a pas été mesurée.

Le second test Docker utilise l'image précédente et le candidat, distincts,
puis supprime le tag de l'ancienne image avant le rollback pour obliger la
restauration à utiliser le tag de sauvegarde. Les identités et dates de démarrage
des services préexistants sont comparées avant/après. Les conteneurs et tags
spécifiques aux fixtures sont nettoyés même en cas d'échec.

## Reproduction

```bash
python3 -m unittest discover -s monitoring/tests -v
# Docker disponible, image candidat construite ; tous les identifiants sont fictifs.
python3 monitoring/tests/stress_docker.py IMAGE_CANDIDAT IMAGE_PRECEDENTE
```

Le test Python réseau n'appelle pas Telegram : une adaptation temporaire de
`urlopen` dirige uniquement ses requêtes vers un serveur HTTP sur loopback.
Les conteneurs de résistance ont `--network none` et des noms aléatoires.
Le socket Docker sert uniquement aux fixtures. Le test de rollback exécute le
même contenu de script, mais dans une installation jetable : ce n'est pas un
retour arrière effectué sur la vraie production.

## Ce que ces tests ne prouvent pas

- La simulation de 24 heures ne remplace pas une observation pendant 24 heures réelles.
- Le serveur HTTP local ne teste pas une panne réelle de l'infrastructure Telegram,
  ni sa couche TLS. Le message réel de validation avait été accepté lors du déploiement initial.
- Les logs supprimés lors d'une rotation ou disparition de conteneur restent perdus.
- Une réponse d'acceptation perdue peut toujours entraîner un doublon au réessai.
- Pas de test de panne totale du VPS, de disque plein ni de mesure de mémoire sous charge.
- Pas de messages de cette campagne dans le chat privé et pas de redémarrage du site.

## Extension : commandes privées et façade Docker

28 tests Python passent après l'ajout des commandes et du filtrage Docker.
Les tests de socket Unix couvrent les routes et méthodes interdites, les dates,
le conteneur cible fixe, les utilisateurs/chats/groupes refusés et la limitation
de fréquence persistante. L'intégration Docker et les tests de rotation,
redémarrages et rollback isolé ont été refaits via la façade.

Une paire Docker réelle confirme : bot UID 10002 sans client/socket Docker,
système de fichiers en lecture seule, capacités supprimées ; façade UID 10001
sans réseau, accès à un seul conteneur via ses routes fixes.

La première intégration a détecté que le daemon du VPS attend des timestamps
Unix dans ses paramètres de logs. La façade convertit maintenant les dates
validées en timestamps Unix ; l'intégration passe après cette correction.

## Compléments du 2 octobre 2026

38 tests distincts réussis localement (28 précédents + 10 nouveaux), sans
requête à Telegram ni modification de production. Les sockets de test Unix et
localhost nécessitent une exécution hors du sandbox local.

- 5 000 erreurs différentes : 50 notifications détaillées, puis un résumé
  de 4 950 notifications, compteur conservé après réouverture de SQLite.
- 1 200 notifications : file bornée à 1 000, 200 regroupées ; résumé récupéré
  quand de la place revient.
- Disque à 5 % libres : une alerte après 3 contrôles, aucune répétition ;
  pas de faux retour sain à 11 %, confirmation à 20 %.
- File bloquée : une alerte et une confirmation de retour sain.
- Certificat : seuils 30/14/7/3 jours et renouvellement ; aucune répétition
  au deuxième contrôle du même seuil. Réseau TLS simulé pour ce scénario.
- Passerelle indisponible pendant 60 contrôles : curseur conservé, une alerte,
  puis reprise, récupération de l’erreur et une confirmation de retour sain.
- SQLite : limite réelle `PRAGMA max_page_count` atteinte ; exception
  « database or disk full », curseur et alertes non validés, replay réussi
  après restauration de capacité. Aucun disque de production rempli.
- Accusé de réception perdu : nouvelle tentative démontrée et doublon possible,
  limite assumée du protocole de livraison.
- Les 3 nouvelles commandes répondent au propriétaire privé sans exposer
  les détails de logs ni les secrets.

L’observation continue de 24–48 heures réelles reste distincte des scénarios
accélérés. Ne pas présenter ces tests comme une observation déjà accomplie.
Le contrôle depuis un service extérieur n’est pas encore configuré.

Deux tests supplémentaires valident l’instantané sans Telegram ni secrets et la
migration SQLite, y compris une insertion par l’ancienne version après rollback.

Validation Docker candidate sur le VPS Réunion Wiki, le 02/10/2026 :
38 tests distincts réussis dans l’image `reunionwiki-telegram-monitor:improvements-test`.
Lecture réelle de l’erreur intermédiaire, traceback et recréation validée.
Rotation : 525/525 lignes encore présentes détectées, 50 détails retenus et
475 erreurs regroupées ; 11 475 lignes déjà supprimées par rotation ne sont
pas récupérables. Trois redémarrages réels ont conservé curseur et alertes.
Rollback isolé entre l’image candidate et l’image de production 7101794 :
ancienne image/configuration et fichier privé restaurés, état conservé.
Paire non-root testée sans socket/client Docker dans le bot, autres routes
refusées et passerelle sans réseau. Aucun message Telegram ; identifiants
fictifs. Identifiants et dates de démarrage des services existants inchangés.
