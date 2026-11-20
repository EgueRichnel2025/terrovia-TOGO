# Dictionnaire des données — TERROVIA

Ce dictionnaire décrit les principales sorties préparées consommées par le tableau de bord. Les types ci-dessous sont indicatifs ; les types réellement lus dépendent du contenu CSV et de Pandas.

## 1. Observations par exploitation
Fichier : data/processed/accessibility/small_farms_potential_accessibility.csv

Une ligne correspond à une petite exploitation agricole préparée incluse dans l'analyse (13 076 lignes dans la version du 20 novembre 2026).

| Champ | Signification |
|---|---|
| farm_id | Identifiant de l'entité source de l'exploitation ; à conserver comme clé technique, pas comme nom public. |
| region_nom_bdd | Région déclarée dans les attributs de la source agricole. |
| prefecture_nom_bdd | Préfecture déclarée dans la source. |
| commune_nom_bdd | Commune déclarée dans la source. |
| canton_nom_bdd | Canton déclaré dans la source. |
| nom_localite | Libellé de localité ; peut contenir des codes de non-réponse. |
| representative_x_utm31_m | Coordonnée X du point représentatif dans EPSG:32631, en mètres. |
| representative_y_utm31_m | Coordonnée Y du point représentatif dans EPSG:32631, en mètres. |
| *_distance_km | Distance euclidienne minimale, en kilomètres, vers la géométrie la plus proche de la famille indiquée. |
| *_nearest_name | Nom/libellé de l'équipement le plus proche lorsqu'il est disponible. |
| *_nearest_id | Identifiant de l'équipement le plus proche dans la couche source. |

### Colonnes de distance
- market_distance_km : marché ;
- input_store_distance_km : magasin d'intrants ;
- cooperative_distance_km : coopérative ;
- esop_distance_km : ESOP ;
- nursery_distance_km : pépinière ponctuelle ;
- nursery_other_distance_km : pépinière surfacique ;
- zaap_zapb_distance_km : géométrie de la couche combinée ZAAP/ZAPB.

Les colonnes *_nearest_name et *_nearest_id suivent le même préfixe que la colonne de distance associée.

## 2. Synthèse régionale
Fichier : data/processed/accessibility/regional_accessibility_summary.csv

Une ligne par région déclarée. Champs :
- region_nom_bdd : libellé régional ;
- farm_count : nombre d'exploitations incluses ;
- pour chaque famille, *_median_km et *_p90_km : médiane et 90e percentile des distances ;
- *_over_5km_pct et *_over_10km_pct : pourcentages d'exploitations au-delà des seuils descriptifs de 5 et 10 km.

Les suffixes de colonnes sont associés aux familles market, input_store, cooperative, esop, nursery, nursery_other et zaap_zapb.

## 3. Synthèse nationale
Fichier : data/processed/accessibility/overall_accessibility_summary.csv

Une ligne par indicateur. Champs :
- indicator : identifiant de l'indicateur ;
- n : nombre d'observations valides ;
- mean_km : moyenne en kilomètres ;
- median_km : médiane ;
- p75_km, p90_km, p95_km : percentiles ;
- max_km : maximum ;
- over_5km_count / over_5km_pct : nombre et pourcentage au-delà de 5 km ;
- over_10km_count / over_10km_pct : nombre et pourcentage au-delà de 10 km.

## 4. Couche régionale cartographique
Fichier : data/processed/accessibility/regions_accessibility.geojson

FeatureCollection de polygones régionaux enrichis avec des indicateurs d'accessibilité pour alimenter la carte. Les noms régionaux sont issus de correspondances candidates entre les FID des limites et les attributs des données agricoles ; cette correspondance doit rester explicitement qualifiée de candidate tant qu'elle n'est pas confirmée par une source administrative officielle.

## 5. Paramètres et limites
Fichier : data/processed/accessibility/methodology.json

Clés principales :
- metric_crs : système de coordonnées métrique utilisé (EPSG:32631) ;
- distance_type : définition de la distance euclidienne ;
- demand_unit : unité d'analyse ;
- farm_features : nombre d'exploitations ;
- *_features : effectifs des familles d'infrastructures utilisées ;
- thresholds_km_are_descriptive_only : seuils descriptifs de référence ;
- limitations : liste des limites connues du calcul.

## 6. Sources brutes et données préparées
Les sources agricoles originales sont archivées sous data/raw/agriculture/. Leur inventaire, leurs champs, les contrôles structurels et les empreintes SHA-256 figurent dans data/raw/agriculture/README.md.

Les données réparées, normalisées ou agrégées sont des dérivés. Elles ne doivent pas être confondues avec les exports bruts. Consulter les rapports d'audit et le registre de provenance avant toute réutilisation ou redistribution.

## 7. Valeurs manquantes et confidentialité
Les codes tels que Nsp, N/A, Néant et Aucun peuvent représenter des non-réponses même lorsque la cellule n'est pas vide. Ils ne doivent pas être interprétés comme des catégories métier.

Ne pas diffuser d'identifiants source, de contacts ou d'attributs personnels dans les livrables publics. Les références courtes EXP-* affichées dans le dashboard sont des alias de présentation, pas des identifiants officiels.
