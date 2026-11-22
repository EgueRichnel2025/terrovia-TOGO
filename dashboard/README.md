# Tableau de bord TERROVIA

## Lancer

    uv sync
    uv run python scripts/prepare_streamlit_french.py
    uv run streamlit run dashboard/app.py

Puis ouvrir l'adresse locale affichée par Streamlit, généralement http://localhost:8501.

## Modes de fonctionnement

Le tableau de bord choisit automatiquement son mode selon les fichiers présents :

- **Mode complet local** : si le CSV détaillé des exploitations et le GeoJSON régional sont disponibles, toutes les fonctions détaillées sont activées.
- **Mode agrégé** : si les données individuelles ou le GeoJSON ne sont pas disponibles, l'application utilise uniquement les trois synthèses nationales/régionales et le fichier méthodologique. Il permet de consulter les résultats nationaux et de comparer les cinq régions, sans coordonnées ni identifiants individuels.

Pour forcer le mode agrégé sur une machine qui possède aussi les données détaillées :

    TERROVIA_AGGREGATE_ONLY=1 uv run streamlit run dashboard/app.py

Le mode agrégé ne remplace pas les données sources et ne permet pas les classements communaux ni l'exploration des parcelles.

## Parcours de l'application

1. **Vue d'ensemble** : périmètre de l'analyse, comparaison des distances médianes des sept familles de services et exemple d'interprétation nationale.
2. **Explorer les territoires** : filtres région/service/repère, indicateurs, carte du Togo et comparaison graphique des cinq régions côte à côte, puis classements communaux. Les distributions, détails et exports restent accessibles dans des sections dédiées.
3. **Profils d’accessibilité** : segmentation exploratoire K-Means, composition des trois profils, signatures de distance et répartition régionale. Seuls les agrégats sont affichés ; les affectations individuelles restent locales.
4. **Méthode et limites** : explication des calculs, définitions des indicateurs, étapes du traitement et limites scientifiques.

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

Le script scripts/prepare_streamlit_french.py règle aussi la langue du document HTML servi par Streamlit (fr) et empêche sa traduction automatique partielle par le navigateur. Il faut le relancer après une réinstallation ou une mise à jour de Streamlit. Pour rétablir le document d’origine : uv run python scripts/prepare_streamlit_french.py --restore.


## Identité visuelle

L’interface utilise trois couleurs fonctionnelles : bleu saphir (#174A6E) pour la structure, bleu océan (#267A9B) pour les graphiques et interactions, et vert jade (#16866A) pour les accents. Les surfaces restent blanches ou bleu-gris très pâle afin de préserver le contraste et la lisibilité.

Les signaux territoriaux de la vue d’ensemble sont présentés sous forme de fiches autonomes, sans cartes imbriquées. La page d’exploration associe désormais la carte du Togo à un graphique comparatif des cinq régions. La page méthode présente les indicateurs et les étapes sous forme de blocs visuels.
