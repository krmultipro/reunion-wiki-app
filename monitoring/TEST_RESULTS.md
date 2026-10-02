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
