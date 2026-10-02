# Monitoring Réunion Wiki

Service autonome : aucun changement du site web, Nginx, Redis ou de leurs volumes.
Les alertes vont au bot et au chat privé existants. Secrets exclusivement dans
`/home/reunionwiki/reunionwiki/monitoring/.env` (permissions 600), jamais dans Git
ni dans l'image. Le socket Docker donne un accès sensible au daemon même monté
`ro` : réserver cette installation au VPS de confiance.

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
uniquement `telegram-logbot`. Il vérifie la santé du bot et l'identité des autres
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
-d --build`. `DOCKER_API_VERSION=1.41` assure la compatibilité avec le daemon
actuel du VPS ; ajuster si le serveur est mis à niveau et retire cette version.
