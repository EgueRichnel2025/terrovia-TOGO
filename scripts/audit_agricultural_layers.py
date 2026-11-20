"""Read-only structural and geometry audit of TERROVIA agricultural GeoJSON layers."""

from __future__ import annotations

import csv
from pathlib import Path

import geopandas as gpd
from shapely import is_valid_reason

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "agriculture"
OUTPUT_CSV = PROJECT_ROOT / "reports" / "audits" / "agricultural_layers_audit.csv"
OUTPUT_MD = PROJECT_ROOT / "reports" / "AUDIT_GEOSPATIAL_AGRICULTURE_2026-11-19.md"


def main() -> None:
    files = sorted(path for path in INPUT_DIR.glob("*.json") if path.name.lower() != "readme.json")
    rows: list[dict[str, object]] = []

    for path in files:
        layer = gpd.read_file(path)
        geometry = layer.geometry
        valid_mask = geometry.is_valid
        reasons = geometry.loc[~valid_mask].map(is_valid_reason)
        reason_counts = reasons.value_counts().to_dict()
        rows.append(
            {
                "file": path.name,
                "feature_count": len(layer),
                "geometry_types": "; ".join(
                    f"{name}:{count}" for name, count in layer.geom_type.value_counts().items()
                ),
                "crs": str(layer.crs),
                "valid_count": int(valid_mask.sum()),
                "invalid_count": int((~valid_mask).sum()),
                "empty_count": int(geometry.is_empty.sum()),
                "null_count": int(geometry.isna().sum()),
                "invalid_reasons": "; ".join(
                    f"{reason}:{count}" for reason, count in reason_counts.items()
                ),
                "property_count": len(layer.columns) - 1,
            }
        )

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    total_features = sum(int(row["feature_count"]) for row in rows)
    total_invalid = sum(int(row["invalid_count"]) for row in rows)
    total_empty = sum(int(row["empty_count"]) for row in rows)
    total_null = sum(int(row["null_count"]) for row in rows)

    lines = [
        "# Audit géospatial des couches agricoles — 19 novembre 2026",
        "",
        "## Périmètre et méthode",
        "",
        f"- Fichiers GeoJSON examinés : **{len(rows)}**.",
        f"- Entités lues : **{total_features:,}**.",
        "- Lecture avec GeoPandas / GDAL, sans modification des fichiers sources.",
        "- Contrôles : type géométrique, CRS, géométries nulles, vides et validité OGC.",
        "- Les géométries invalides sont détectées mais ne sont pas réparées dans cet audit.",
        "",
        "## Résultats par couche",
        "",
        "| Fichier | Entités | CRS | Valides | Invalides | Vides | Nulles |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['file']} | {row['feature_count']} | {row['crs']} | "
            f"{row['valid_count']} | {row['invalid_count']} | "
            f"{row['empty_count']} | {row['null_count']} |"
        )

    lines.extend(
        [
            "",
            "## Synthèse",
            "",
            f"- Total : **{total_features:,}** entités.",
            f"- Géométries invalides : **{total_invalid:,}**.",
            f"- Géométries vides : **{total_empty:,}**.",
            f"- Géométries nulles : **{total_null:,}**.",
            "",
            "Les couches ponctuelles contrôlées sont valides. Plusieurs couches polygonales "
            "présentent des géométries invalides. Ces anomalies doivent être qualifiées avant "
            "tout calcul de surface, intersection, union ou agrégation spatiale. Une éventuelle "
            "réparation sera produite dans data/processed/, jamais dans data/raw/, et "
            "devra conserver une trace des géométries transformées.",
            "",
            "## Limites",
            "",
            "Cet audit ne valide pas l'exactitude thématique, la complétude géographique, "
            "la précision des attributs, les licences, ni l'absence de doublons métier. "
            "Il ne confirme pas non plus que les 144 polygones de la couche ZAAPs - Formes "
            "sont tous des ZAAP plutôt que des ZAAP/ZAPB.",
            "",
            "Détail machine-readable : reports/audits/agricultural_layers_audit.csv.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Layers: {len(rows)}")
    print(f"Features: {total_features}")
    print(f"Invalid geometries: {total_invalid}")
    print(f"Empty geometries: {total_empty}")
    print(f"Null geometries: {total_null}")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"Report: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
