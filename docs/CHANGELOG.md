# Changelog – Réunion Wiki

Le projet suit un versionnement simple où chaque version majeure correspond à une brique fonctionnelle clé du portail. Les dates sont indicatives et suivent la chronologie des mises en ligne.

## v2 – Formulaire intégré & notifications (2024-06-27)
- Ajout d’un formulaire complet pour proposer des sites directement depuis l’accueil, les pages catégories et une page dédiée.
- Validation renforcée : filtrage des champs, honeypot anti-bot, contrôle des catégories et sauvegarde en base en statut `en_attente`.
- Notifications email automatiques vers `reunionwiki974@gmail.com` lors de chaque soumission (paramétrable via `.env`).
- Navigation mobile revue façon “ruban” scrollable, suppression du burger menu.
- Nettoyage CSS mobile (forms responsive) et ajustement du service worker (stratégie réseau-first) pour éviter les versions en cache.
- Espace admin sécurisé : filtres de statut, recherche, validation, modification, publication ou suppression des propositions et ajout manuel d’un nouveau site publié.
- Nouvelle barre de recherche (icône loupe) accessible sur toutes les pages.
- Page contact dédiée avec liens email, formulaire et réseaux sociaux.
- Page blog avec recommandations thématiques pour un meilleur SEO éditorial.
- Refonte de l'accueil avec carrousels glissables (catégories, derniers ajouts) et CTA intégrés.

## v1 – Navigation et structure (2024-06-15)
- Création d’une barre de navigation dynamique listant toutes les catégories + liens FAQ, Contact, page “Derniers sites ajoutés”.
- Mise en place du caching des catégories et de la normalisation des slugs pour garantir des URLs stables.
- Optimisation SEO : titres/canoniques dynamiques pour les pages catégories, filtres `format_date`, blocs OpenGraph/Twitter dans `base.html`.
- Premier service worker et PWA (install prompt, manifest, icônes) + redirection `/service-worker.js`.
- Durcissement de la configuration : rate limiting (Flask-Limiter), try/except SQLite, headers de sécurité et configuration centralisée (`config.py`).

## v0 – Base du site (2024-06-10)
- Publication initiale : liste des catégories avec sélection de sites, page “Nouveaux sites”, FAQ, mentions légales et liens externes.
- Architecture Flask minimale (routes, templates Jinja2, base SQLite, fichier `schema.sql`).
- Mise en place de l’infrastructure OVH : Gunicorn + Nginx + HTTPS, sauvegardes cron, logs, système systemd.
- Intégration du portail statique (HTML/CSS) avec ambiance réunionnaise et structure responsive de base.
