# Notes de développement

Notes, idées et TODO pour le projet Réunion Wiki.

---

## 🎯 Prochaines fonctionnalités

### Priorité haute
- [ ] Compléter la suite de tests unitaires (`tests/test_services.py`)
- [ ] Améliorer la gestion des erreurs avec messages plus détaillés
- [ ] Ajouter un système de cache pour améliorer les performances
- [ ] Interface admin : statistiques détaillées (graphiques)

### Priorité moyenne
- [ ] Système d'avis/commentaires sur les sites
- [ ] Recherche avancée avec filtres (date, catégorie, ville)
- [ ] Export des données en différents formats (JSON, XML)
- [ ] API REST pour accès externe (si besoin)

### Priorité basse
- [ ] Logo officiel du projet
- [ ] Carousel avec visuels sur la page d'accueil
- [ ] Système de favoris pour les utilisateurs
- [ ] Intégration avec réseaux sociaux pour partage

---

## 🐛 Bugs connus / À corriger

- [ ] Vérifier le comportement du cache des catégories en cas de modification
- [ ] Optimiser les requêtes de recherche pour les grandes bases
- [ ] Gérer le cas où la base de données est verrouillée

---

## 🔧 Améliorations techniques

### Architecture
- [ ] Introduire un pattern Repository pour abstraction DB encore plus poussée
- [ ] Séparer les constantes (TALENT_CATEGORIES, etc.) dans un fichier dédié
- [ ] Créer des modèles SQLAlchemy (optionnel, si migration vers PostgreSQL)

### Performance
- [ ] Implémenter un système de cache Redis pour les catégories
- [ ] Optimiser les requêtes SQL avec des index supplémentaires
- [ ] Pagination pour les listes longues (dashboard admin)

### Sécurité
- [ ] Ajouter un système de rate limiting par IP plus granulaire
- [ ] Implémenter une authentification 2FA pour l'admin
- [ ] Audit log pour toutes les actions sensibles

---

## 📚 Documentation à compléter

- [ ] Guide de contribution détaillé
- [ ] Documentation des endpoints API (si API REST ajoutée)
- [ ] Guide de migration de données
- [ ] Schéma de base de données (diagramme)

---

## 🧪 Tests à ajouter

### Tests unitaires
- [ ] `test_services_sites.py` : Toutes les fonctions de `services/sites.py`
- [ ] `test_services_talents.py` : Toutes les fonctions de `services/talents.py`
- [ ] `test_database.py` : Context managers et gestion d'erreurs
- [ ] `test_auth.py` : Authentification et décorateurs

### Tests d'intégration
- [ ] `test_routes_public.py` : Routes publiques end-to-end
- [ ] `test_routes_admin.py` : Routes admin avec authentification
- [ ] `test_forms.py` : Validation des formulaires WTForms

---

## 💡 Idées diverses

- Système de tags pour les sites (au-delà des catégories)
- Géolocalisation des sites avec carte interactive
- Système de modération communautaire
- Notifications push pour les nouveaux sites
- Mode sombre pour l'interface
- Internationalisation (français/créole réunionnais)

---

## 📝 Notes importantes

### Conventions à respecter
- Toujours utiliser les services, jamais de SQL direct dans les routes
- Utiliser les context managers DB pour toutes les opérations
- Documenter toutes les nouvelles fonctions publiques
- Tester localement avant de push

### Déploiement
- Toujours vérifier `python3 -m compileall` avant déploiement
- Optimiser la base avec `optimize_db.py` avant backup
- Vérifier les logs après déploiement

---

**Dernière mise à jour** : Après refactorisation v3 (2025-01)
