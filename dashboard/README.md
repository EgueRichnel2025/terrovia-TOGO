# Tableau de bord TERROVIA

## Lancer

    uv sync
    uv run streamlit run dashboard/app.py

Puis ouvrir l'adresse locale affichée par Streamlit, généralement http://localhost:8501.

## Parcours de l'application

1. **Vue d'ensemble** : périmètre de l'analyse, comparaison des distances médianes des sept familles de services et exemple d'interprétation nationale.
2. **Explorer les territoires** : filtres région/service/repère, indicateurs, carte nationale, comparaison régionale et classements communaux. Les distributions, détails individuels et exports restent accessibles dans des sections dédiées.
3. **Méthode et limites** : explication des calculs, définitions des indicateurs et limites scientifiques.

Le guide détaillé est dans docs/USER_GUIDE.md.

## Fichiers requis

L'application lit les fichiers préparés de data/processed/accessibility/ :
- small_farms_potential_accessibility.csv
- regional_accessibility_summary.csv
- regions_accessibility.geojson
- methodology.json

Elle ne reconstruit pas automatiquement ces fichiers à partir des sources brutes.

## Précaution d'interprétation

Les distances sont euclidiennes, en ligne droite, en EPSG:32631. Elles ne représentent ni un trajet routier ni un temps de parcours. Les seuils sont descriptifs et non normatifs. La présence d'un équipement dans les données ne garantit pas son fonctionnement.
