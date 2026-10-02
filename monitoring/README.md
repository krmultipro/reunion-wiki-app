# Monitoring Réunion Wiki

Service autonome : aucun changement du site web, Nginx, Redis ou de leurs volumes.
Les alertes vont au bot et au chat privé existants. Secrets exclusivement dans
`/home/reunionwiki/reunionwiki/monitoring/.env` (permissions 600), jamais dans Git
ni dans l'image. Le bot accède à une façade limitée, sans socket Docker direct.
Commandes privées et modèle de sécurité : [COMMANDS_SECURITY.md](COMMANDS_SECURITY.md).

## Comportement

- Lecture de **toutes** les lignes Docker depuis le curseur précédent, toutes les
  5 secondes, avec bornes UTC `--since` / `--until`. Le curseur et les alertes sont
  enregistrés ensemble dans SQLite. Première installation : démarrage à l'heure
  courante, sans renvoi des anciens logs. Après redémarrage : reprise du curseur.
- Erreurs explicites, exceptions et statuts HTTP 5xx des logs d'accès. Tracebacks
  regroupés sur 30 lignes au maximum, finalisés après 5 secondes sans suite.
- Première occurrence immédiate, répétitions **identiques** résumées après
  5 minutes. Des messages variables peuvent donc produire des alertes distinctes.
- File persistante dans `state/monitor.db`, réessais de 5 secondes à 1 heure,
  respect global du `retry_after` Telegram, avec pause persistante de tous les
  envois après un échec. La file n'a pas de limite automatique :
  surveiller l'espace disque en cas de longue coupure et de nombreuses erreurs.
- Contrôle HTTPS toutes les 60 secondes (HTTP 200 attendu, redirections suivies).
  Alerte après 3 échecs consécutifs, puis message de rétablissement.
- Alerte après 3 échecs consécutifs de lecture Docker, puis rétablissement.
  Le curseur reste conservé pendant une indisponibilité du daemon/conteneur.
- Healthcheck : boucle active depuis moins de 120 secondes. Il ne garantit pas
  la livraison Telegram ; Docker ne redémarre pas un conteneur uniquement parce
  qu'il est `unhealthy`. Les échecs Telegram sont visibles dans les logs.

Limites : les logs déjà supprimés par rotation ou disparition d'un ancien
conteneur ne sont pas récupérables. Un accusé Telegram perdu après livraison
peut entraîner un doublon au réessai (livraison au moins une fois). Le contrôle
HTTPS depuis le VPS ne détecte pas une panne totale du VPS : ajouter une sonde
extérieure pour cette couverture. Aucun suivi séparé des logs Nginx ici.

## Tests sans Telegram

```bash
python3 -m unittest discover -s monitoring/tests -v
```

Résultats détaillés et limites de la campagne de résistance :
[TEST_RESULTS.md](TEST_RESULTS.md). Les tests Docker de résistance se lancent
séparément avec `python3 monitoring/tests/stress_docker.py IMAGE_CANDIDAT IMAGE_PRECEDENTE`
et créent uniquement des fixtures jetables.

## Déploiement depuis Git

Depuis le dépôt local : commit, push de la branche, puis `./deploy-monitoring.sh`.
Ce script transfère **uniquement le dossier monitoring du commit HEAD** via SSH,
sans `git pull` du site : la production et la branche locale de développement
peuvent différer. Le VPS conserve son installation hors checkout Git, mais son
`DEPLOYED_COMMIT` identifie exactement la source versionnée.

Le script sauvegarde les anciens fichiers et l'image, construit et teste le
candidat avec le réseau désactivé, conserve les secrets actuels puis recrée
`telegram-logbot` et sa façade `docker-reader`, sans toucher au site. Il vérifie la santé du bot et l'identité des autres
conteneurs. Retour automatique à l'ancienne installation si l'activation échoue.
Les sauvegardes privées sont dans `/home/reunionwiki/deployments/monitoring-backup-*`.
Exécuter leur `rollback.sh` pour revenir en arrière. Ne pas supprimer ces
sauvegardes ni l'image `before-*` avant validation.

Sur le VPS, pour consulter et tester :

```bash
docker logs --tail 50 telegram-logbot
docker inspect telegram-logbot --format '{{.State.Health.Status}}'
# Envoie réellement un message dans le chat configuré :
docker exec telegram-logbot python /app/monitor.py --test-message
```

Pour une installation neuve : copier `.env.example` en `.env`, saisir les secrets
sur le serveur, appliquer `chmod 600 .env`, puis `docker-compose -p monitoring up
-d --build`. La façade utilise l'API Docker 1.41 du VPS ; vérifier sa compatibilité si le
serveur est mis à niveau. Les volumes IPC et SQLite doivent appartenir respectivement
aux UID 10001 et 10002 avec groupe 10001 ; le script de déploiement prépare ces droits.

## Serveurs : ne pas confondre

L’alias SSH `reunionwiki` désigne le VPS Réunion Wiki de production.
L’alias `vps-devops` est réservé aux cours de l’utilisateur : ne jamais y
installer, déployer ou planifier le monitoring Réunion Wiki.
La surveillance extérieure du VPS reste à configurer sur un service dédié ;
aucun autre serveur personnel n’est autorisé pour cet usage.

## Alertes complémentaires

Le bot contrôle le disque et la file chaque minute. Une alerte apparaît après
3 contrôles en échec : moins de 10 % libres **ou** moins de 1 Gio ; retour sain
à partir de 15 % **et** 2 Gio. Le contrôle utilise le volume `/state` ; le
02/10/2026, sa partition et celle de `/var/www/reunion-wiki-app/data_prod`
ont été vérifiées identiques. Si les données sont déplacées sur un autre disque,
ce contrôle doit être adapté. Aucun nouveau accès Docker ou volume de données
applicatives n’a été accordé au bot.

La file est considérée anormale à 100 messages ou si son plus ancien message
attend depuis 15 minutes. Une notification puis une notification de retour sain
évitent la répétition à chaque minute ; si Telegram est coupé, elles restent en
attente et ne peuvent pas être livrées immédiatement.

Le certificat TLS est vérifié au démarrage puis toutes les 6 heures, avec
validation TLS normale. Alertes aux seuils 30, 14, 7 et 3 jours, puis confirmation
après renouvellement. Une impossibilité de lire le certificat est signalée après
3 contrôles TLS en échec ; le contrôle HTTPS reste effectué chaque minute.

Anti-flood : maximum 50 nouvelles signatures d’erreurs sur 5 minutes. Les
suivantes sont comptées dans un résumé persistant, sans conserver leur détail.
La file globale est limitée à 1 000 notifications ; les dépassements sont
comptés également. Un résumé est ajouté après 5 minutes, dès que la file passe
sous 900 messages. Les répétitions des signatures déjà retenues gardent leur
résumé habituel. Consulter les logs du service pour retrouver les détails,
sous réserve de leur rotation Docker. Ce mécanisme borne les messages, pas
la croissance des logs ou de la table temporaire de déduplication sur 24 heures.

Si SQLite est plein ou indisponible, le bot annule la transaction et réessaie,
sans renouveler son heartbeat. Il ne peut pas garantir une alerte Telegram
quand son propre stockage est déjà épuisé. Une surveillance extérieure reste
nécessaire pour les pannes complètes du VPS ou du monitoring.

Une réponse Telegram perdue après acceptation entraîne une nouvelle tentative :
un doublon est possible. La livraison garantit une nouvelle tentative, pas
l’unicité parfaite des messages côté Telegram.

## Observation après déploiement

`python3 monitoring/observe.py --record` réalise un contrôle HTTPS depuis la
machine locale et lit un instantané limité du bot via SSH **reunionwiki**.
Aucun secret, détail de logs ou texte Telegram n’est lu. Les résultats sont
conservés localement dans `monitoring/state/observation.jsonl` (ignoré par Git).
`--snapshot` dans le bot lit SQLite en lecture seule sans initialiser Telegram.
Un suivi horaire de 48 heures est prévu depuis ce chat ; il dépend de la
machine locale et de l’application ouverte, et ne remplace pas un service
extérieur disponible en permanence. Les intervalles non observés doivent être
mentionnés dans le bilan, sans extrapoler une disponibilité continue.
