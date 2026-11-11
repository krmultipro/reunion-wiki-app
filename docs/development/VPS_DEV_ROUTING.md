# Routage VPS de l'environnement de développement

Dernière vérification : 17 septembre 2026.

## Résultat attendu

- `https://reunionwiki.re` et `https://www.reunionwiki.re` servent le backend
  de production.
- `https://dev.reunionwiki.re` sert le conteneur `web_dev`.
- `http://dev.reunionwiki.re` redirige vers HTTPS.

Le DNS de `dev.reunionwiki.re` pointe vers le même VPS que la production. La
séparation est donc effectuée par Nginx selon le nom de domaine demandé.

## Ce qui est commun

```text
Internet
   │
   ▼
Adresse IP publique du VPS
   │
   ├── port 80  : HTTP
   └── port 443 : HTTPS
             │
             ▼
        Nginx commun
          │       │
          │       └── dev.reunionwiki.re → web_dev
          └────────── reunionwiki.re     → web production
```

Les deux domaines partagent quatre éléments :

- **L'entrée Internet** : ils pointent vers la même adresse IP publique.
- **Les ports 80 et 443** : le port 80 reçoit HTTP et redirige vers HTTPS ; le
  port 443 reçoit les connexions HTTPS.
- **Le processus Nginx** : c'est l'aiguilleur qui choisit le bon conteneur en
  lisant le domaine demandé.
- **Le dossier des certificats** : il est commun, mais contient un certificat
  distinct pour `reunionwiki.re` et pour `dev.reunionwiki.re`.

Le code, les conteneurs applicatifs, Redis, la base et les fichiers envoyés par
les utilisateurs restent séparés entre production et développement.

## Architecture Docker

Le Nginx public appartient à deux réseaux :

- le réseau de production, pour joindre `reunionwiki_prod_web_1` ;
- `reunionwiki_dev_proxy`, réseau dédié pour joindre `web_dev`.

Le réseau `reunionwiki_dev_proxy` est déclaré comme réseau externe dans les
fichiers Compose de production et de développement. Cette séparation est
importante : les deux projets Compose créent naturellement un alias `web`.
Connecter Nginx directement au réseau applicatif dev peut donc rendre
`proxy_pass http://web:8000` ambigu et envoyer des requêtes de production vers
le backend dev.

Les upstreams Nginx doivent rester explicites :

```nginx
# Production
proxy_pass http://reunionwiki_prod_web_1:8000;

# Développement
proxy_pass http://web_dev:8000;
```

## HTTPS

Le virtual host de développement utilise le certificat suivant :

```text
/etc/letsencrypt/live/dev.reunionwiki.re/fullchain.pem
/etc/letsencrypt/live/dev.reunionwiki.re/privkey.pem
```

Avant un rechargement, toujours vérifier le certificat et la configuration :

```bash
docker exec reunionwiki_prod_nginx_1 nginx -t
curl -I https://dev.reunionwiki.re/
curl -I https://reunionwiki.re/
```

Le certificat dev renouvelé le 17 septembre 2026 expire le 16 décembre 2026.
Son renouvellement doit être surveillé ou automatisé avec Certbot.

## Protection par mot de passe

`dev.reunionwiki.re` est protégé par l'authentification HTTP Basic de Nginx.
La production n'est pas concernée.

- Identifiant actuel : `yagamireunionwiki`
- Fichier d'identifiants sur le VPS :
  `/var/www/reunion-wiki-app/nginx/.htpasswd`
- Montage dans Nginx : `/etc/nginx/.htpasswd`, en lecture seule

Le mot de passe n'est jamais conservé dans cette documentation. Le fichier
`.htpasswd` contient uniquement son hash et doit rester hors de Git.

Après une modification, vérifier :

```text
dev sans identifiants → HTTP 401
dev avec identifiants → HTTP 200
production             → HTTP 200 sans identifiants
```

Sauvegardes créées avant l'activation :

```text
/var/www/reunion-wiki-app/nginx/default.conf.backup-before-dev-auth-20260917
/var/www/reunion-wiki-app/docker-compose.prod.yml.backup-before-dev-auth-20260917
```

## Déploiement de la branche `test`

### Contrôles locaux — décision validée le 17 octobre 2026

Contrôles introduits lors du premier changement du 17 octobre 2026 (séquence
complétée par le renforcement ci-dessous), avant tout transfert au VPS :

1. Vérifier la présence de l'interpréteur exécutable `.venv/bin/python`.
2. Vérifier la syntaxe avec
   `.venv/bin/python -m compileall -q app.py migrate.py reunion_wiki tests`.
3. Exécuter la suite applicative avec
   `.venv/bin/python -m unittest discover -s tests -v`.

Critères d'acceptation : un environnement manquant, une erreur de syntaxe ou
un échec de test arrête le script avec un message explicite et un code non nul,
sans transfert SSH/SCP. Si les deux contrôles réussissent, le déploiement
existant continue. L'option `--allow-db-change` ne contourne pas ces contrôles.
Les tests ignorés par la suite restent signalés sans bloquer son succès.

Le périmètre est la suite applicative `tests/`, avec ses bases temporaires,
pas les tests du monitoring. Sa couverture et ses limites sont décrites dans
[`../testing/README.md`](../testing/README.md). Ces contrôles ne remplacent ni
les vérifications Docker sur le VPS, ni les contrôles visuels et fonctionnels
des parcours modifiés. Aucun déploiement n'est autorisé par la seule
modification du script.

Implémentation et vérification locales le 17 octobre 2026 :

- Contrôles ajoutés dans `deploy-dev.sh` avant la préparation de l'archive.
- Syntaxe Python et Bash valides ; suite applicative : 79 tests, 78 réussis,
  1 ignoré.
- Vérification isolée du script avec SSH/SCP simulés : environnement absent,
  erreur de syntaxe et échec de tests bloquent avant le réseau ; un succès
  autorise la préparation de l'archive et atteint l'étape SSH simulée.
- `--allow-db-change` ne contourne pas un échec de tests.

Aucun déploiement lancé pour cette modification. Les vérifications sur le
conteneur VPS restent celles de la procédure existante, sans nouvelle
validation distante à cette occasion.

Pour envoyer les modifications actuelles du portable vers le site dev :

```bash
git switch test
./deploy-dev.sh
```

Le script exige désormais un arbre propre et la branche `test`. Il teste une
copie isolée du commit identifié et envoie une archive extraite de ce même
snapshot Git, sans fichiers de travail ni artefacts produits par les tests.
Le comportement historique incluant les fichiers non commités est remplacé
par la décision de renforcement du 17 octobre 2026 ci-dessous.

Il n'envoie ni `.env`, ni base, ni uploads, ni le Compose local avec debugger.
Sur le VPS, il construit l'image dans une release privée, teste les migrations
sur une copie SQLite et vérifie le démarrage avant de remplacer `web_dev`.
Il conserve une sauvegarde de la base et l'image précédente pour le retour
arrière. Il vérifie ensuite dev (`401` sans identifiants) et production (`200`).

Si les migrations changent la base, le script s'arrête avant la bascule.
Examiner le changement avant de relancer explicitement :

```bash
./deploy-dev.sh --allow-db-change
```

Cette option autorise une migration de la **base dev uniquement**. Les données
ne sont jamais resynchronisées automatiquement depuis le portable. Une
reconstruction manuelle via Docker Compose reste déconseillée : utiliser le
script pour garder le code, l'image et la version déployée cohérents.

Le 17 septembre 2026, l'ancienne application dev du VPS a été remplacée par
la branche locale `test`, au commit `ae7b2eb8`.

- `web_dev` utilise Gunicorn avec `FLASK_ENV=production`.
- La base et les uploads sont montés dans `/data`.
- Le Compose local en mode debug n'a pas été envoyé sur le VPS.
- L'ancienne application et son ancienne base restent sauvegardées.

La base locale `data/base.db` et `data/uploads/` ont ensuite été copiés vers
l'environnement dev après validation sur une copie. État vérifié après import :

```text
sites             60
talents           29
images de talents 29
uploads           33
```

Les migrations, le chargement d'une image, l'accès authentifié à dev et
l'accès public à la production ont tous été contrôlés avec succès.

Les sauvegardes et instantanés privés sont conservés dans :

```text
/home/reunionwiki/deployments/test-ae7b2eb8/
```

Ce dossier contient notamment l'ancienne dev complète, l'ancienne base et
l'instantané des données locales. Il est accessible uniquement au compte
`reunionwiki`.

## Réinitialisation du mot de passe admin dev

L'administration de l'application utilise un compte différent de la
protection HTTP Basic placée devant `dev.reunionwiki.re`.

- Identifiant admin actuel : `admin`
- Variable utilisée : `ADMIN_PASSWORD_HASH` dans le `.env` dev du VPS
- Le mot de passe et son hash ne doivent jamais être ajoutés à Git ou à cette
  documentation.

Procédure sûre :

1. Générer un nouveau hash avec `werkzeug.security.generate_password_hash`,
   en saisissant le mot de passe de manière interactive.
2. Sauvegarder le `.env` dev.
3. Remplacer uniquement `ADMIN_PASSWORD_HASH`.
4. Restreindre les permissions du `.env` au compte `reunionwiki`.
5. Recréer uniquement `web_dev` pour recharger les variables.
6. Tester le nouveau mot de passe avec la fonction d'authentification réelle.
7. Vérifier que dev et production répondent encore correctement.
8. Supprimer toutes les copies temporaires du `.env`.

La réinitialisation du 17 septembre 2026 a été validée avec
`ADMIN_AUTH_OK`. La sauvegarde correspondante est :

```text
/var/www/reunion-wiki-app-dev/.env.backup-before-admin-reset-20260917
```

## Procédure sûre de modification

1. Sauvegarder `nginx/default.conf` et les fichiers Compose concernés.
2. Valider les fichiers Compose avec `docker-compose config -q`.
3. Tester la configuration Nginx avec `nginx -t`.
4. Vérifier que Nginx résout séparément `reunionwiki_prod_web_1` et `web_dev`.
5. Recréer uniquement le service Nginx si ses montages ou réseaux changent.
6. Contrôler immédiatement les trois domaines et leurs certificats.
7. Comparer les réponses publiques aux backends directs pour confirmer que
   dev et production ne sont pas inversés.

Ne pas se contenter d'un code HTTP `200` : un virtual host inconnu peut être
servi par défaut par la production et donner l'impression que le site dev
fonctionne.

## Retour arrière

Des sauvegardes datées sont présentes à côté des fichiers modifiés :

```text
/var/www/reunion-wiki-app/nginx/default.conf.backup-before-dev-route-20260917
/var/www/reunion-wiki-app/docker-compose.prod.yml.backup-before-dev-route-20260917
/var/www/reunion-wiki-app-dev/docker-compose.yml.backup-before-dev-route-20260917
```

En cas de problème, restaurer ces fichiers, retirer le réseau dev du Nginx,
recréer uniquement le service Nginx avec le nom de projet Compose existant,
puis vérifier la production avant toute autre action.

## Renforcement du déploiement — décision du 17 octobre 2026

Décision validée dans la conversation après revue critique ; complète les
contrôles locaux ci-dessus et remplace l'autorisation d'envoyer des fichiers
non commités. Périmètre : scripts et contrôles techniques, sans changement UX,
sans migration métier nouvelle et sans déploiement réel.

### Comportement et critères d'acceptation

1. **Version exacte** : exiger la branche `test` et un arbre propre (fichiers
   suivis et nouveaux non ignorés), avant les contrôles. Construire l'archive
   depuis le commit Git identifié, tester cette même source isolée et envoyer
   le script distant extrait de cette archive. Les secrets, bases, uploads et
   Compose locaux restent exclus. Aucun fichier de travail non commité envoyé.
2. **Tests dans l'image** : conserver les contrôles locaux rapides, puis lancer
   la suite `tests/` dans l'image candidate avec des données temporaires, sans
   réseau ni variables privées du VPS. Bloquer avant toute interruption dev
   si les tests échouent. Une suite vide est un échec.
3. **Sauvegarde et restauration** : conserver une copie préliminaire pour les
   essais de migration. Après ces essais, arrêter `web_dev`, puis prendre une
   sauvegarde SQLite finale cohérente et vérifier son intégrité avant la
   bascule. Restaurer hors connexion, en tenant compte des fichiers WAL/SHM,
   sans ignorer les erreurs. Vérifier le redémarrage après restauration et
   distinguer explicitement échec du déploiement et échec de récupération.
   Préserver les sauvegardes et données permettant une récupération manuelle.
4. **Contrôles fonctionnels** : avant et après bascule, vérifier en lecture
   seule accueil, recherche, accès admin anonyme et une ressource image ;
   contrôler un upload existant si disponible. Ne pas créer de données métier
   ni envoyer d'emails. Ces contrôles ne prouvent ni une connexion admin réelle
   ni le rendu mobile ; ils complètent la suite isolée et les contrôles publics.
5. **Production** : retirer le déclenchement automatique historique sur push.
   Le workflow historique ne doit plus arrêter ni reconstruire la production.
   Tant qu'aucune procédure de production équivalente n'a été implémentée et
   vérifiée, son déclenchement manuel doit refuser explicitement le déploiement.
   L'état réellement actif sur GitHub doit être distingué du fichier local :
   aucun push GitHub n'est autorisé par cette modification.

### Limites et méthode de vérification

Tester les refus locaux et l'identité de l'archive dans des dépôts temporaires,
avec SSH/SCP simulés ; tester SQLite WAL et les erreurs de restauration sur des
bases jetables ; vérifier le déroulement distant sans conteneur actif par
simulation et, si Docker est disponible, dans une instance jetable sans montage
vers les données actives. Un test Docker indisponible reste signalé, jamais
présenté comme réussi. Mettre à jour le bilan avec les preuves réellement obtenues.
La sauvegarde locale au VPS protège ce déploiement, pas la perte du VPS ; elle
ne remplace pas une sauvegarde indépendante. Une coupure dev courte est assumée
pour la sauvegarde finale. La production ne doit pas être arrêtée.

### Réalisation et vérifications

Conception consignée avant code. Réalisation locale : `deploy-dev.sh`,
`script/run_app_tests.py`, `script/deploy-dev-remote.sh`,
`script/deploy_sqlite.py`, `script/deploy_smoke.py`, tests dans `script/tests/`.
Le runner refuse aussi un dossier `tests/` absent ou une suite vide. Les tests
locaux utilisent des chemins temporaires de base/uploads et désactivent les emails.

Le workflow `.github/workflows/deploy.yml` est remplacé localement par un
refus manuel explicite sans accès serveur ni secrets. Ce n'est pas une procédure
de production achevée. Lecture GitHub le 17 octobre : le fichier distant sur `main` contient toujours
le déclenchement sur push, et la dernière exécution retournée est un succès
le 16 juin 2026 (run `27639245790`). L'état activé/désactivé actuel du workflow
n'a pas pu être lu par le connecteur. Aucun push réalisé ; le retrait local
n'est donc pas encore effectif sur GitHub.
Sources : [workflow distant](https://github.com/krmultipro/reunion-wiki-app/blob/main/.github/workflows/deploy.yml),
[dernier run retourné](https://github.com/krmultipro/reunion-wiki-app/actions/runs/27639245790).

Limites opérationnelles : la candidate peut recevoir des écritures pendant sa
courte validation après bascule. Un rollback restaure le snapshot final et peut
perdre ces écritures récentes ; aucune maintenance Nginx n'a été ajoutée.
Les uploads actifs ne sont pas restaurés. Les migrations futures qui modifient
des fichiers nécessitent une stratégie dédiée avant déploiement. Les sauvegardes
précédentes sont conservées, sans rotation automatique dans cette intervention.

Preuves obtenues le 17 octobre 2026 :

- Syntaxe Bash/Python et `git diff --check` réussis.
- Suite applicative locale : 79 tests, 78 réussis et 1 ignoré.
- Régressions scripts : 31 tests locaux réussis, dont refus arbre sale,
  syntaxe invalide, vraie assertion en échec, suite absente/vide et identité
  commit/archive/script malgré des modifications pendant les tests.
- Image d'essai construite avec le Dockerfile du projet (Python 3.10).
  Suite applicative dans cette image, sans réseau ni volumes : 79 tests,
  78 réussis et 1 ignoré ; 7 tests SQLite WAL et 5 tests smoke réussis.
- Essai réel Gunicorn dans un conteneur jetable sans réseau extérieur : base
  vierge migrée, site synthétique et PNG temporaire ; accueil, recherche,
  formulaire de connexion, favicon et upload validés par HTTP.
- Une tentative d'exécuter aussi les tests d'orchestration dans l'image slim
  échoue faute d'outils hôte (Git/flock). Ces tests sont exécutés sur le poste ;
  ils ne font pas partie du runner applicatif de l'image.

Le déroulement du script distant et ses échecs ont été testés avec Docker
simulé ; le cycle complet Compose/Nginx/rollback sur une copie de l'infrastructure
VPS reste à vérifier avant de le déclarer validé sur cet environnement.
Aucun déploiement ni modification des données actives dans cette intervention.


## Refonte DEV — autorisation du 11 novembre 2026

L’utilisateur autorise la refonte fidèle aux maquettes retenues, sa finalisation
feature → `dev` et sa publication sur le VPS DEV. `main`, la production, les
fonctionnalités avancées reportées et le monitoring sont exclus de ce travail.
Cette section remplace, pour ce chantier, la branche de publication `test` des
procédures historiques ci-dessus ; elle ne modifie pas leur historique.

### Contrat de publication et protection des sources

`deploy-dev.sh` exige désormais `dev` propre. Tests, script distant et archive
proviennent du même commit. L’archive ne contient que l’application, ses assets,
les scripts et les tests : aucune maquette, documentation privée, configuration
monitoring, base ou upload. Le validateur refuse les chemins privés, les liens
symboliques et les sorties de répertoire ; `.dockerignore` applique aussi une
liste d’inclusion au build direct. Les fichiers ignorés ne sont pas une barrière
suffisante : inspection de l’archive et de l’image candidate avant bascule.
Les labels et `release-info.txt` enregistrent `branch=dev`, commit et hash.

Le budget distant est contrôlé avant build : trois fois la taille de l’image
actuelle, des sources et des données, plus une réserve de 512 Mio. Ce calcul
est une estimation conservatrice du pic et doit être confronté aux mesures
réelles ; aucune purge automatique d’images ou de sauvegardes n’est autorisée.
Relevé du 11 novembre à 09:10 Asia/Dubai : 1 351 172 096 octets libres (94 %
utilisés), image DEV 168 642 748 octets, données DEV environ 980 Kio. Ces valeurs
ne sont pas des constantes et doivent être relues avant publication.

### Sauvegarde complète et récupération DEV

`script/deploy_data.py` complète le helper SQLite : snapshot par API backup,
copie des uploads réguliers sans liens, manifeste SHA-256, intégrité SQLite,
comptages et nombre d’écarts de clés étrangères. Deux snapshots et un nouvel
inventaire détectent les écritures pendant une copie en ligne ; un changement
interdit de déclarer ce bundle cohérent. Le snapshot final de bascule reste pris
après arrêt des écrivains. Aucun mot de passe ou fichier `.env` n’entre dans ce
bundle ; leur récupération relève du stockage privé existant.

Avant toute migration active, conserver une copie hors VPS et vérifier sa
restauration isolée, les empreintes/comptages/contraintes et une image. Le helper
refuse une destination existante ou imbriquée dans la source. Les bundles sont
privés (répertoires 700, fichiers 600). Une copie sur le même VPS ne protège pas
d’une perte de l’hôte. La préparation du 11 novembre est distincte du snapshot
final du futur déploiement et ne remplace pas une stratégie récurrente complète.

`--allow-db-change` conserve son sens explicite : après examen du diff de schéma
et des données issu de la migration sur copie, autoriser ce changement précis
sur DEV. Ce n’est ni un contournement des tests ni une autorisation générique de
migration destructive. Rejouer la migration sur copie et vérifier conservation
et idempotence ; ne jamais remplacer la base active par une base du PC.

Le rollback arrête DEV, conserve DB **et uploads** de la candidate échouée pour
réconciliation, puis restaure le bundle final DB+uploads, l’image et le code
précédents. Les uploads déplacés sont conservés, pas effacés. Une récupération
qui échoue laisse DEV arrêté et signale l’étape. Les nouvelles écritures ne sont
pas fusionnées automatiquement : leur conservation ne prouve pas leur rejeu.
Prévoir une fenêtre sans saisie pour éviter cette situation.

Le proxy Nginx partagé peut nécessiter un reload contrôlé après recreation de
`web_dev` (résolution de son adresse). Aucun changement du fichier Nginx, de
l’upstream production ni des services production n’est inclus. Contrôler
immédiatement production en lecture seule ; ce contrôle ne valide pas le
nouveau parcours DEV. Le workflow GitHub prod historique n’est pas utilisé.
Les résultats réels de préparation et de restauration sont consignés dans le
rapport privé de travail ; aucune bascule n’est réalisée par cette documentation.


Préparation réellement vérifiée le 11 novembre 2026 : nouvelle copie privée
DB+uploads DEV sur VPS puis PC ; restauration dans un répertoire de test neuf,
intégrité SQLite OK, aucune violation de clé étrangère, 60 sites/29 talents,
33 fichiers uploadés (451 595 octets). Toutes empreintes concordent ; les
33 images ont été relues et décodées. Deux emplacements indépendants pour cette
copie ponctuelle, pas de troisième lieu ni de planification annoncés. Aucune
donnée active, configuration ou service modifié. Suite des outils : 46 tests
réussis (dont WAL, corruption, copie concurrente, fichiers déplacés conservés,
archive privée forcée et refus capacité), syntaxe Bash et diff contrôlés.
Le cycle complet bascule/rollback VPS reste une vérification future.
