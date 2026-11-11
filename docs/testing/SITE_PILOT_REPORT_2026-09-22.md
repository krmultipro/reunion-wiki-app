# Parcours pilote de la fiche 8 — 22 septembre 2026

| Élément | Observation |
| --- | --- |
| Cas | `TC-SITE-012-01` |
| Exécutant | Codex, dans le navigateur de développement local ; URL finale choisie par le propriétaire du projet |
| Environnement | `docker-compose.yml`, application sur `localhost:8086`, base montée depuis `data/base.db` |
| Site pilote retenu | [Accueil officiel de la Ville de Saint-Joseph](https://saintjoseph.re/) |
| Fiche de test | Site `#89`, catégorie « Administratifs », commune « Saint-Joseph » |
| Résultat | Parcours fonctionnel réussi ; fiche archivée à la fin |

Les heures ci-dessous sont celles de la base SQLite et des logs du conteneur
(UTC). L'accueil officiel de la mairie était lisible dans le navigateur et
présentait des démarches d'état civil, des services municipaux et des
informations locales. Le contrôle HTTP de l'application a obtenu `200` sur
l'URL normalisée `https://saintjoseph.re`, sans redirection.

| Étape | Résultat observé |
| --- | --- |
| Proposition publique | Enregistrée à 14:24:47 en `en_attente`, avec catégorie et commune correctes. |
| Doublon | Une deuxième proposition de la même URL est refusée et renvoie à la fiche `#89`. |
| Modération et correction | Fiche visible dans le tableau de bord. Description corrigée à 14:25:07 ; le statut reste `en_attente`. |
| Décision éditoriale | Critère « organisme réunionnais » enregistré avec l'URL officielle, une note et l'administrateur `admin`. |
| Contrôle et publication | HTTP `200`, puis `valide` à 14:25:27. `submitted_at`, `first_published_at` et `published_at` sont renseignées dans cet ordre. |
| Visibilité | Fiche visible dans « Administratifs », dans la recherche combinant texte, catégorie, commune et portée « Avec une commune », ainsi que dans « Derniers ajoutés ». |
| Clic sortant | Un clic visiteur sur `/go/89` redirige vers l'accueil officiel et porte `click_count` à 1. Un second clic rapproché le laisse à 1. |
| Archivage | Passage à `archived` à 14:26:42 via l'administration. L'enregistrement, les dates, la revue éditoriale, le contrôle HTTP et le clic restent conservés. |
| Retrait public | Fiche absente de l'accueil, d'« Administratifs », de Saint-Joseph, de la recherche filtrée et des tendances ; `/go/89` retourne `404`. |
| Affichage | Recherche vérifiée dans le navigateur à 1280 × 800 et 390 × 844 ; aucun débordement horizontal ni anomalie visuelle manifeste. |
| Logs et base | Aucune exception applicative sur le parcours ; `PRAGMA quick_check` retourne `ok`. |

Aucune modification directe de la base n'a été utilisée pour faire évoluer la
fiche : les écritures proviennent des formulaires et actions de l'application.
Les requêtes SQLite ont seulement servi à confirmer les statuts, dates,
compteurs et traces d'audit. La fenêtre de 390 × 844 simule un téléphone dans
le navigateur ; ce n'est pas une mesure sur un appareil physique.

Un premier essai a utilisé l'[article sur le Train Réunion Express](https://saintjoseph.re/Projet-de-Train-Reunion-Express-la).
Le parcours technique de cette fiche `#88` avait réussi, puis elle avait été
archivée. Le propriétaire du projet a ensuite écarté cet article, marqué
« Archive » et portant sur une réunion passée, au profit de l'accueil de la
mairie. Les deux fiches restent archivées dans la base locale, avec leur
historique ; aucune n'est visible publiquement.

Le test `unittest` de la fiche 8 reste ignoré parce qu'il représente une
exécution réelle non reproductible automatiquement. Sa réussite manuelle est
consignée ici ; l'ignorer dans la suite automatisée ne signifie pas que le
parcours pilote reste à faire.
