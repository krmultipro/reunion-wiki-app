# Bilan des tests des sites — 19 septembre 2026

La fiche 7 est validée : ses sept cas passent, ainsi que deux contrôles
complémentaires de migration et de vérification HTTP manuelle.

```text
Ran 69 tests
OK (skipped=6)
```

Les six cas ignorés concernent les transitions complètes de la fiche 1
(3), la confirmation éditoriale de la fiche 2 (1), la portée géographique
de la fiche 5 (1) et le parcours pilote humain de la fiche 8 (1).

La migration ne déduit pas de première publication certaine pour les anciens
sites. Elle utilise leur ancienne `date_ajout` comme estimation du tri
`published_at`, en conservant sa provenance dans
`site_publication_date_inference`. La base locale de l'utilisateur n'a pas
été migrée pendant ces tests ; ils utilisent des bases temporaires.

La structure HTML et les styles existants ont été vérifiés, mais le contrôle
visuel desktop/mobile n'a pas pu être effectué : aucun navigateur pilotable
n'était disponible dans cet environnement. Il reste à faire avant validation
visuelle finale de l'interface.
