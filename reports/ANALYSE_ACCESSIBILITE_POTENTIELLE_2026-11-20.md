# Analyse exploratoire de l'accessibilité potentielle — TERROVIA

Date : 2026-11-20.

> Les distances ci-dessous sont des distances euclidiennes en ligne droite, calculées en EPSG:32631 depuis un point représentatif intérieur de chaque petite exploitation vers la géométrie de l'infrastructure cartographiée la plus proche. Elles ne sont ni des distances routières ni des temps de trajet.

## 1. Population et infrastructures cartographiées

- Petites exploitations préparées : 13,076.
- Marchés : 1,073.
- Magasins d'intrants : 463.
- Coopératives : 6,859.
- ESOP : 12.
- Pépinières ponctuelles : 728.
- Autres pépinières surfaciques : 209.
- Couche ZAAP/ZAPB non désambiguïsée : 144.

## 2. Statistiques nationales

| Indicateur | Médiane (km) | P90 (km) | > 5 km (%) | > 10 km (%) |
|---|---:|---:|---:|---:|
| market_distance_km | 2.34 | 5.47 | 12.73 | 0.69 |
| input_store_distance_km | 5.51 | 14.71 | 54.70 | 23.14 |
| cooperative_distance_km | 0.72 | 2.18 | 0.82 | 0.02 |
| esop_distance_km | 34.71 | 57.09 | 98.08 | 93.59 |
| nursery_distance_km | 5.93 | 17.48 | 56.88 | 26.73 |
| nursery_other_distance_km | 13.28 | 125.63 | 76.78 | 59.31 |
| zaap_zapb_distance_km | 6.98 | 14.92 | 66.97 | 29.83 |

## 3. Distance au marché le plus proche par région

| Région déclarée | Exploitations | Médiane (km) | P90 (km) | > 5 km (%) | > 10 km (%) |
|---|---:|---:|---:|---:|---:|
| Centrale | 389 | 2.23 | 4.89 | 9.51 | 0.00 |
| Kara | 1424 | 1.74 | 5.27 | 12.15 | 0.35 |
| Maritime | 5421 | 2.52 | 5.44 | 12.47 | 0.09 |
| Plateaux | 1453 | 3.42 | 6.81 | 26.08 | 0.62 |
| Savanes | 4389 | 2.11 | 4.86 | 9.09 | 1.62 |

## 4. Interprétation et précautions

- Les distances aux marchés sont mesurées jusqu'à la géométrie surfacique du marché, et non jusqu'à son centroïde.
- Les distances aux magasins, coopératives, ESOP et pépinières ponctuelles sont mesurées jusqu'au point cartographié.
- Les seuils de 5 et 10 km sont des repères descriptifs exploratoires, pas des normes nationales d'accessibilité.
- Les résultats ne démontrent pas l'accès effectif, la capacité, la qualité ou l'ouverture des services.
- Les couches ZAAP/ZAPB ne sont pas séparées sémantiquement dans la source ; elles ne sont pas interprétées comme des ZAAP seules.
- Les exploitations quarantainées lors de la réparation géométrique ne sont pas incluses dans ce calcul : le périmètre est constitué des 13 076 entités préparées.
- Le réseau routier brut reste exclu des distances de trajet tant que sa topologie n'est pas validée.

## 5. Fichiers produits

- `data/processed/accessibility/small_farms_potential_accessibility.csv` — une ligne par exploitation.
- `data/processed/accessibility/regional_accessibility_summary.csv` — agrégats régionaux.
- `data/processed/accessibility/overall_accessibility_summary.csv` — synthèse nationale.
- `data/processed/accessibility/methodology.json` — paramètres et limites.
