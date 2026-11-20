# Données locales TERROVIA

Les fichiers de données ne sont volontairement pas distribués dans le dépôt public. Les sources brutes peuvent contenir des coordonnées, identifiants, noms, adresses et contacts. Les exports dérivés peuvent conserver une partie de ces attributs.

## Fichiers attendus par le dashboard

Placer les sorties préparées localement dans data/processed/accessibility/ :

- small_farms_potential_accessibility.csv
- regional_accessibility_summary.csv
- overall_accessibility_summary.csv
- regions_accessibility.geojson
- methodology.json

## Reconstitution

Les scripts d'audit, de réparation, de calcul et de cartographie se trouvent dans scripts/. Ils doivent être exécutés uniquement après avoir obtenu les sources autorisées et vérifié leurs licences, leurs schémas et leur provenance.

Consulter reports/REGISTRE_PROVENANCE_DONNEES.md et docs/PUBLICATION_POLICY.md avant tout téléchargement, transformation ou partage.

Ne jamais committer les fichiers sources ni les exports détaillés sans revue explicite des licences et des données personnelles.
