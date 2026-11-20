"""Measure straight-line proximity of small farms to mapped markets/services.

Distances are Euclidean in projected EPSG:32631 and are NOT travel distances.
All inputs are prepared copies; data/raw is never written.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import STRtree

ROOT = Path(__file__).resolve().parents[1]
AGRI = ROOT / "data/processed/agriculture"
OUT = ROOT / "data/processed/accessibility"
REPORTS = ROOT / "reports"
AUDITS = REPORTS / "audits"
METRIC_CRS = "EPSG:32631"

LAYER_PATTERNS = {
    "farms": "*Petites exploitations agricoles*_repaired.geojson",
    "markets": "*Marchés*_repaired.geojson",
    "input_stores": "*Magasins d'intrants agricoles*_repaired.geojson",
    "cooperatives": "*Coopératives - Agricoles*_repaired.geojson",
    "esop": "*ESOP*_repaired.geojson",
    "nurseries": "*Pépinières agricoles-*_repaired.geojson",
    "nurseries_other": "*Pépinières agricoles - Autres*_repaired.geojson",
    "zaap_zapb": "*ZAAPs - Formes*_repaired.geojson",
}


def get_layer(key: str) -> gpd.GeoDataFrame:
    matches = sorted(AGRI.glob(LAYER_PATTERNS[key]))
    if len(matches) != 1:
        raise RuntimeError(f"Attendu un fichier pour {key}, trouvé: {matches}")
    frame = gpd.read_file(matches[0])
    if frame.crs is None:
        raise ValueError(f"CRS absent: {matches[0]}")
    if frame.geometry.is_empty.any() or (~frame.geometry.is_valid).any():
        raise ValueError(f"Géométries non valides: {matches[0]}")
    return frame.to_crs(METRIC_CRS)


def nearest_metrics(
    points, facilities: gpd.GeoDataFrame, key: str, name_field: str
) -> dict[str, np.ndarray]:
    tree = STRtree(facilities.geometry.to_numpy())
    indices, distances = tree.query_nearest(
        points.to_numpy(), all_matches=False, return_distance=True
    )
    if indices.shape[0] != 2:
        raise RuntimeError(f"Résultat STRtree inattendu pour {key}: {indices.shape}")
    target_idx, facility_idx = indices
    if len(target_idx) != len(points):
        raise RuntimeError(f"{key}: {len(target_idx)} correspondances pour {len(points)} points")
    order = np.argsort(target_idx)
    target_idx = target_idx[order]
    facility_idx = facility_idx[order]
    distances = distances[order]
    if not np.array_equal(target_idx, np.arange(len(points))):
        raise RuntimeError(f"{key}: certaines exploitations n'ont pas de plus proche voisin")
    return {
        f"{key}_distance_km": distances / 1000.0,
        f"{key}_nearest_name": facilities.iloc[facility_idx][name_field]
        .fillna("")
        .astype(str)
        .to_numpy(),
        f"{key}_nearest_id": facilities.iloc[facility_idx]["id"].astype(str).to_numpy(),
    }


def summarize_by_region(frame: pd.DataFrame, metric_columns: list[str]) -> pd.DataFrame:
    rows = []
    for region, group in frame.groupby("region_nom_bdd", dropna=False):
        row: dict[str, object] = {
            "region_nom_bdd": region,
            "farm_count": len(group),
        }
        for column in metric_columns:
            values = group[column].dropna()
            prefix = column.removesuffix("_km")
            row[f"{prefix}_median_km"] = values.median()
            row[f"{prefix}_p90_km"] = values.quantile(0.90)
            row[f"{prefix}_over_5km_pct"] = (values.gt(5).mean() * 100) if len(values) else np.nan
            row[f"{prefix}_over_10km_pct"] = (values.gt(10).mean() * 100) if len(values) else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("region_nom_bdd")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    AUDITS.mkdir(parents=True, exist_ok=True)
    farms = get_layer("farms")
    points = farms.geometry.representative_point()
    markets = get_layer("markets")
    stores = get_layer("input_stores")
    cooperatives = get_layer("cooperatives")
    esop = get_layer("esop")
    nurseries = get_layer("nurseries")
    nurseries_other = get_layer("nurseries_other")
    zaap_zapb = get_layer("zaap_zapb")

    results: dict[str, np.ndarray] = {}
    results.update(nearest_metrics(points, markets, "market", "marche_nom"))
    results.update(nearest_metrics(points, stores, "input_store", "etab_nom"))
    results.update(nearest_metrics(points, cooperatives, "cooperative", "cooperative_nom"))
    results.update(nearest_metrics(points, esop, "esop", "cooperative_nom"))
    results.update(nearest_metrics(points, nurseries, "nursery", "etab_nom"))
    results.update(nearest_metrics(points, nurseries_other, "nursery_other", "pepiniere_nom"))
    results.update(nearest_metrics(points, zaap_zapb, "zaap_zapb", "zaap_nom"))

    output = pd.DataFrame(
        {
            "farm_id": farms["id"].astype(str),
            "region_nom_bdd": farms["region_nom_bdd"].fillna("<NULL>").astype(str),
            "prefecture_nom_bdd": farms["prefecture_nom_bdd"].fillna("<NULL>").astype(str),
            "commune_nom_bdd": farms["commune_nom_bdd"].fillna("<NULL>").astype(str),
            "canton_nom_bdd": farms["canton_nom_bdd"].fillna("<NULL>").astype(str),
            "nom_localite": farms["nom_localite"].fillna("<NULL>").astype(str),
            "representative_x_utm31_m": points.x,
            "representative_y_utm31_m": points.y,
        }
    )
    for key, values in results.items():
        output[key] = values
    csv_path = OUT / "small_farms_potential_accessibility.csv"
    output.to_csv(csv_path, index=False)

    metric_columns = [
        "market_distance_km",
        "input_store_distance_km",
        "cooperative_distance_km",
        "esop_distance_km",
        "nursery_distance_km",
        "nursery_other_distance_km",
        "zaap_zapb_distance_km",
    ]
    regional = summarize_by_region(output, metric_columns)
    regional_path = OUT / "regional_accessibility_summary.csv"
    regional.to_csv(regional_path, index=False)

    overall_rows = []
    for col in metric_columns:
        s = output[col]
        overall_rows.append(
            {
                "indicator": col,
                "n": int(s.notna().sum()),
                "mean_km": s.mean(),
                "median_km": s.median(),
                "p75_km": s.quantile(0.75),
                "p90_km": s.quantile(0.90),
                "p95_km": s.quantile(0.95),
                "max_km": s.max(),
                "over_5km_count": int(s.gt(5).sum()),
                "over_5km_pct": s.gt(5).mean() * 100,
                "over_10km_count": int(s.gt(10).sum()),
                "over_10km_pct": s.gt(10).mean() * 100,
            }
        )
    overall = pd.DataFrame(overall_rows)
    overall_path = OUT / "overall_accessibility_summary.csv"
    overall.to_csv(overall_path, index=False)

    # Explicit method and limitations: no actual travel/network claims.
    metadata = {
        "metric_crs": METRIC_CRS,
        "distance_type": "Euclidean straight-line distance from representative point to nearest mapped facility geometry",  # noqa: E501
        "demand_unit": "mapped small agricultural holding feature",
        "farm_features": len(farms),
        "market_features": len(markets),
        "input_store_features": len(stores),
        "cooperative_features": len(cooperatives),
        "esop_features": len(esop),
        "nursery_point_features": len(nurseries),
        "nursery_other_polygon_features": len(nurseries_other),
        "zaap_zapb_polygon_features": len(zaap_zapb),
        "thresholds_km_are_descriptive_only": [5, 10],
        "limitations": [
            "No road-network route distance or travel time is estimated.",
            "No road condition, seasonality, transport mode, service capacity, prices or opening-hour constraints are represented.",  # noqa: E501
            "A mapped facility's existence does not prove that it is operational or accessible to every farmer.",  # noqa: E501
            "Small-holding polygons are represented by an interior representative point; this is not a farm entrance or household location.",  # noqa: E501
            "ZAAP/ZAPB layer is not semantically disambiguated and is reported under the combined source-layer label.",  # noqa: E501
            "The nearest-neighbour result measures geometric proximity only.",
        ],
    }
    (OUT / "methodology.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Analyse exploratoire de l'accessibilité potentielle — TERROVIA",
        "",
        "Date : 2026-11-20.",
        "",
        "> Les distances ci-dessous sont des distances euclidiennes en ligne droite, calculées en EPSG:32631 depuis un point représentatif intérieur de chaque petite exploitation vers la géométrie de l'infrastructure cartographiée la plus proche. Elles ne sont ni des distances routières ni des temps de trajet.",  # noqa: E501
        "",
        "## 1. Population et infrastructures cartographiées",
        "",
        f"- Petites exploitations préparées : {len(farms):,}.",
        f"- Marchés : {len(markets):,}.",
        f"- Magasins d'intrants : {len(stores):,}.",
        f"- Coopératives : {len(cooperatives):,}.",
        f"- ESOP : {len(esop):,}.",
        f"- Pépinières ponctuelles : {len(nurseries):,}.",
        f"- Autres pépinières surfaciques : {len(nurseries_other):,}.",
        f"- Couche ZAAP/ZAPB non désambiguïsée : {len(zaap_zapb):,}.",
        "",
        "## 2. Statistiques nationales",
        "",
        "| Indicateur | Médiane (km) | P90 (km) | > 5 km (%) | > 10 km (%) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in overall.to_dict(orient="records"):
        lines.append(
            f"| {row['indicator']} | {row['median_km']:.2f} | {row['p90_km']:.2f} | "
            f"{row['over_5km_pct']:.2f} | {row['over_10km_pct']:.2f} |"
        )
    lines += [
        "",
        "## 3. Distance au marché le plus proche par région",
        "",
        "| Région déclarée | Exploitations | Médiane (km) | P90 (km) | > 5 km (%) | > 10 km (%) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in regional.to_dict(orient="records"):
        lines.append(
            f"| {row['region_nom_bdd']} | {row['farm_count']} | "
            f"{row['market_distance_median_km']:.2f} | {row['market_distance_p90_km']:.2f} | "
            f"{row['market_distance_over_5km_pct']:.2f} | {row['market_distance_over_10km_pct']:.2f} |"  # noqa: E501
        )
    lines += [
        "",
        "## 4. Interprétation et précautions",
        "",
        "- Les distances aux marchés sont mesurées jusqu'à la géométrie surfacique du marché, et non jusqu'à son centroïde.",  # noqa: E501
        "- Les distances aux magasins, coopératives, ESOP et pépinières ponctuelles sont mesurées jusqu'au point cartographié.",  # noqa: E501
        "- Les seuils de 5 et 10 km sont des repères descriptifs exploratoires, pas des normes nationales d'accessibilité.",  # noqa: E501
        "- Les résultats ne démontrent pas l'accès effectif, la capacité, la qualité ou l'ouverture des services.",  # noqa: E501
        "- Les couches ZAAP/ZAPB ne sont pas séparées sémantiquement dans la source ; elles ne sont pas interprétées comme des ZAAP seules.",  # noqa: E501
        "- Les exploitations quarantainées lors de la réparation géométrique ne sont pas incluses dans ce calcul : le périmètre est constitué des 13 076 entités préparées.",  # noqa: E501
        "- Le réseau routier brut reste exclu des distances de trajet tant que sa topologie n'est pas validée.",  # noqa: E501
        "",
        "## 5. Fichiers produits",
        "",
        "- `data/processed/accessibility/small_farms_potential_accessibility.csv` — une ligne par exploitation.",  # noqa: E501
        "- `data/processed/accessibility/regional_accessibility_summary.csv` — agrégats régionaux.",
        "- `data/processed/accessibility/overall_accessibility_summary.csv` — synthèse nationale.",
        "- `data/processed/accessibility/methodology.json` — paramètres et limites.",
    ]
    report = REPORTS / "ANALYSE_ACCESSIBILITE_POTENTIELLE_2026-11-20.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Farms: {len(farms)}; markets: {len(markets)}; metric CRS: {METRIC_CRS}")
    print("Overall accessibility:\n", overall.to_string(index=False))
    print(
        "Regional market accessibility:\n",
        regional[
            [
                "region_nom_bdd",
                "farm_count",
                "market_distance_median_km",
                "market_distance_p90_km",
                "market_distance_over_5km_pct",
                "market_distance_over_10km_pct",
            ]
        ].to_string(index=False),
    )
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
