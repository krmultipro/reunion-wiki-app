# Bilan des tests des sites — 22 septembre 2026

La fiche 2 est validée : ses huit cas passent. La publication exige désormais
une décision éditoriale explicite sur le lien avec La Réunion, conservée en
privé avec l'URL examinée, l'administrateur et la date. Une décision négative
ou un changement d'URL empêche la publication.

```text
Ran 73 tests
OK (skipped=1)
```

La fiche 1 passe désormais ses sept cas. Le test de création directe couvre
les données invalides, le refus éditorial, les échecs HTTP `404` et `503`, puis
la publication et la visibilité publique après validation complète. Le seul
cas ignoré dans la suite concerne le parcours pilote humain de la fiche 8,
exécuté séparément et consigné dans
[`SITE_PILOT_REPORT_2026-09-22.md`](SITE_PILOT_REPORT_2026-09-22.md).
Les deux contrôles complémentaires vérifient que le
repository ne publie pas sans confirmation et qu'une ancienne confirmation
est invalidée par un changement d'URL ou une décision négative ultérieure.

Les tests utilisent des bases SQLite temporaires et un contrôle HTTP simulé.
Ils ne déterminent pas eux-mêmes si le jugement éditorial sur un site réel est
correct ; cette vérification reste humaine.

La fiche 5 est maintenant validée : le filtre public combine texte, catégorie,
commune et portée. L'administrateur peut choisir « Toute La Réunion » ou « En
ligne » ; une commune absente reste « Non précisée ». Un test complémentaire
vérifie que la migration des anciennes tables conserve une portée déjà choisie.
Le filtre décrit les sites et ne nécessite aucune base GeoIP.
