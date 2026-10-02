# Commandes Telegram et accès Docker limité

## Commandes du chat privé

- `/status` : dernier contrôle HTTPS, état du conteneur web, activité du bot.
- `/queue` : nombre de notifications et réponses en attente.
- `/test` : réponse de confirmation, sans provoquer d'erreur sur le site.
- `/help` (ou `/start`) : liste des commandes.

Les commandes n'acceptent aucun argument et ne permettent ni shell, ni
redémarrage, ni déploiement. Le bot vérifie à chaque message le type de chat
`private`, son identifiant `CHAT_ID`, l'identifiant expéditeur `ALLOWED_USER_ID`
et le fait que l'expéditeur ne soit pas un bot. Les messages transférés sont
ignorés. Les utilisateurs non autorisés n'obtiennent aucune réponse.

Une commande au maximum toutes les 10 secondes, délai conservé après restart.
Les réponses passent par la même file persistante et le même contrôle Telegram
que les alertes. L'offset `getUpdates` et les réponses sont enregistrés ensemble.
Lors de la première activation, les anciennes commandes sont ignorées.
Le bot effectue des requêtes sortantes `getUpdates` : pas de webhook ni de port
entrant à ouvrir. Le menu est enregistré via `setMyCommands`, uniquement pour
le chat configuré. La déclaration du menu ne remplace pas les contrôles d'accès.

`ALLOWED_USER_ID`, `CHAT_ID`, `BOT_TOKEN`, `BOT_USERNAME` et `DOCKER_SOCKET_GID`
sont conservés dans le fichier privé `.env` du VPS, permissions 600.
Le déploiement vérifie que le chat est privé et qu'aucun webhook n'existe ; il
conserve un propriétaire déjà configuré ou utilise l'identifiant du chat privé
existant lors de cette migration. Ne pas réutiliser cette valeur pour un groupe.

## Isolation Docker

Le bot n'a **ni socket Docker, ni client Docker**. Il tourne comme UID 10002,
sans capacités Linux, avec `no-new-privileges` et un système de fichiers en
lecture seule. Seul son volume SQLite est modifiable ; le volume IPC est monté
pour lui en lecture seule.

Un service `docker-reader`, UID 10001 et groupe supplémentaire du socket Docker,
possède seul le socket. Il n'a aucun réseau (`network_mode: none`) ni port publié.
Il écoute un socket Unix privé, permissions 660, dans un répertoire 750.
Le groupe partagé 10001 permet au bot de se connecter, mais pas de remplacer
le socket via son montage en lecture seule.

La façade accepte uniquement :

- `GET /status` : champs limités `running`, `status`, `health` du web cible.
- `GET /logs?since=...&until=...` : logs du même web, dates explicites avec fuseau,
  intervalle de 1 heure maximum, lecture bornée à 32 Mio.

Le nom de conteneur est fixé côté façade : `reunionwiki_prod_web_1` en production.
Il ne vient jamais d'une commande Telegram ni des paramètres de la requête.
Toutes les mutations et les autres routes sont refusées. Les routes API Docker
sont construites en interne et utilisent exclusivement `GET .../json` et
`GET .../logs`. Le bot rattrape son curseur par tranches de 1 heure.
Aucun inspect complet, variable d'environnement, shell ou lecture d'autres
conteneurs n'est transmis au bot.

## Limites

La façade est une barrière entre le bot et Docker, pas une réduction des pouvoirs
intrinsèques du socket : une compromission de **la façade elle-même** reste
sensible. Son code doit rester petit, sans réception de messages Telegram ni
secret Telegram. Les logs du web peuvent contenir des informations sensibles ;
ils sont accessibles au bot pour ses alertes, mais pas via les commandes de
consultation. Un compte Telegram du propriétaire compromis pourrait demander
ces commandes de consultation, pas administrer le VPS.

Si plus de 32 Mio de logs restent à lire dans une tranche, la façade refuse la
lecture sans avancer le curseur. Il faut examiner ce cas au lieu de tronquer les
logs silencieusement. La rotation Docker peut toujours supprimer des lignes
avant leur lecture. La passerelle n'est pas un moniteur extérieur du VPS.

## Validation

28 tests Python couvrent les scénarios précédents et les contrôles d'accès :
utilisateur/chat/groupe incorrect, bot, transfert, absence de propriétaire,
arguments shell, commandes inconnues, cooldown après redémarrage, offset et
portée privée du menu. Les tests de façade utilisent un vrai socket Unix et
vérifient que les requêtes refusées n'appellent jamais Docker.

Les scripts `integration_docker.py`, `stress_docker.py` et `secure_pair.py`
valident aussi la lecture via la façade, les redémarrages, le rollback isolé
et une paire réelle avec bot non-root sans socket/client Docker, refus d'autres
routes et façade sans réseau. Identifiants fictifs, aucun message Telegram.
