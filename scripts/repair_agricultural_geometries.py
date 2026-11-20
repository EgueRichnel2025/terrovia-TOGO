"""Conservative, auditable repair of invalid agricultural polygon geometries."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import is_valid_reason, make_valid
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "agriculture"
PROCESSED = ROOT / "data" / "processed" / "agriculture"
QUARANTINE = PROCESSED / "quarantine"
REPORT = ROOT / "reports" / "GEOMETRY_REPAIR_REVIEW_2026-11-19.md"
MANIFEST = ROOT / "reports" / "audits" / "geometry_repair_manifest.csv"
AREA_CRS = "EPSG:32631"
MAX_AREA_CHANGE_PCT = 1.0


def polygon_parts(geometry):
    parts = []

    def collect(item):
        if item.geom_type == "Polygon":
            parts.append(item)
        elif item.geom_type == "MultiPolygon":
            parts.extend(item.geoms)
        elif item.geom_type == "GeometryCollection":
            for child in item.geoms:
                collect(child)

    collect(geometry)
    return parts


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    summary = []

    for source in sorted(RAW.glob("*.json")):
        if source.name.lower() == "readme.json":
            continue
        original = gpd.read_file(source)
        if original.empty or original.geometry.name not in original:
            continue
        clean_records = []
        review_records = []
        repaired_count = 0
        unchanged_count = 0

        for position, (_, row) in enumerate(original.iterrows()):
            record = row.to_dict()
            geom = row.geometry
            if geom is None or geom.is_empty or geom.is_valid:
                clean_records.append(record)
                unchanged_count += 1
                continue

            reason = is_valid_reason(geom)
            candidate = make_valid(geom)
            parts = polygon_parts(candidate)
            if not parts:
                review_records.append(
                    {
                        "source_file": source.name,
                        "source_row": position,
                        "reason": reason,
                        "repair_result_type": candidate.geom_type,
                        "area_change_pct": None,
                        "review_status": "QUARANTINE_NO_POLYGONAL_COMPONENT",
                        "attributes_json": json.dumps(
                            {k: v for k, v in record.items() if k != original.geometry.name},
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )
                continue

            repaired = unary_union(parts)
            if repaired.geom_type not in {"Polygon", "MultiPolygon"}:
                review_records.append(
                    {
                        "source_file": source.name,
                        "source_row": position,
                        "reason": reason,
                        "repair_result_type": repaired.geom_type,
                        "area_change_pct": None,
                        "review_status": "QUARANTINE_NON_POLYGON_RESULT",
                        "attributes_json": json.dumps(
                            {k: v for k, v in record.items() if k != original.geometry.name},
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )
                continue

            before_area = gpd.GeoSeries([geom], crs=original.crs).to_crs(AREA_CRS).area.iloc[0]
            after_area = gpd.GeoSeries([repaired], crs=original.crs).to_crs(AREA_CRS).area.iloc[0]
            delta = (
                abs(after_area - before_area) / before_area * 100
                if before_area > 0
                else float("inf")
            )

            if not repaired.is_valid or delta > MAX_AREA_CHANGE_PCT:
                review_records.append(
                    {
                        "source_file": source.name,
                        "source_row": position,
                        "reason": reason,
                        "repair_result_type": repaired.geom_type,
                        "area_before_m2": before_area,
                        "area_after_m2": after_area,
                        "area_change_pct": delta,
                        "review_status": (
                            "QUARANTINE_INVALID_OUTPUT"
                            if not repaired.is_valid
                            else "QUARANTINE_AREA_CHANGE_OVER_1_PERCENT"
                        ),
                        "attributes_json": json.dumps(
                            {k: v for k, v in record.items() if k != original.geometry.name},
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )
                continue

            record[original.geometry.name] = repaired
            clean_records.append(record)
            repaired_count += 1

        clean = gpd.GeoDataFrame(clean_records, geometry=original.geometry.name, crs=original.crs)
        output = PROCESSED / f"{source.stem}_repaired.geojson"
        clean.to_file(output, driver="GeoJSON")
        # Validate the serialized GeoJSON as well: coordinate serialization can
        # expose degeneracies that were not detected in the in-memory object.
        serialized = gpd.read_file(output)
        serialized_bad = serialized.loc[~serialized.geometry.is_valid]
        if not serialized_bad.empty:
            for _output_index, bad_row in serialized_bad.iterrows():
                review_records.append(
                    {
                        "source_file": source.name,
                        "source_row": None,
                        "reason": is_valid_reason(bad_row.geometry),
                        "repair_result_type": bad_row.geometry.geom_type,
                        "area_change_pct": None,
                        "review_status": "QUARANTINE_INVALID_AFTER_GEOJSON_SERIALIZATION",
                        "attributes_json": json.dumps(
                            {k: v for k, v in bad_row.items() if k != serialized.geometry.name},
                            ensure_ascii=False,
                            default=str,
                        ),
                    }
                )
            serialized = serialized.loc[serialized.geometry.is_valid].copy()
            repaired_count -= len(serialized_bad)
            serialized.to_file(output, driver="GeoJSON")
        clean = gpd.read_file(output)

        if review_records:
            review = pd.DataFrame(review_records)
            review_path = QUARANTINE / f"{source.stem}_review.csv"
            review.to_csv(review_path, index=False, encoding="utf-8-sig")
        else:
            review_path = None

        summary.append(
            {
                "source_file": source.name,
                "source_features": len(original),
                "output_file": str(output.relative_to(ROOT)),
                "output_features": len(clean),
                "unchanged_features": unchanged_count,
                "repaired_features": repaired_count,
                "quarantined_features": len(review_records),
                "quarantine_file": str(review_path.relative_to(ROOT)) if review_path else "",
                "output_invalid_geometries": int((~clean.geometry.is_valid).sum()),
                "area_crs": AREA_CRS,
                "max_accepted_area_change_pct": MAX_AREA_CHANGE_PCT,
            }
        )

    pd.DataFrame(summary).to_csv(MANIFEST, index=False, encoding="utf-8-sig")
    total_source = sum(x["source_features"] for x in summary)
    total_output = sum(x["output_features"] for x in summary)
    total_repaired = sum(x["repaired_features"] for x in summary)
    total_quarantine = sum(x["quarantined_features"] for x in summary)
    lines = [
        "# Revue des réparations géométriques agricoles — 19 novembre 2026",
        "",
        "## Règle conservatrice",
        "",
        "- Réparation : Shapely make_valid, extraction des seules composantes polygonales.",
        f"- Mesure de surface : {AREA_CRS} (mètres).",
        (
            f"- Acceptation automatique si l'écart relatif de surface est ≤ "
            f"{MAX_AREA_CHANGE_PCT:.1f} %."
        ),
        "- Les résultats non polygonaux, invalides ou dépassant le seuil sont mis en quarantaine.",
        "- Les attributs des entités mises en quarantaine sont conservés dans le CSV.",
        "- Les données de data/raw/ ne sont jamais modifiées.",
        "",
        "## Résultats",
        "",
        f"- Entités sources des couches traitées : {total_source:,}.",
        f"- Entités écrites dans les couches préparées : {total_output:,}.",
        f"- Géométries invalides réparées et acceptées : {total_repaired:,}.",
        f"- Entités mises en quarantaine pour revue : {total_quarantine:,}.",
        "",
        "| Source | Entités | Réparées | Quarantaine | Invalides en sortie |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in summary:
        lines.append(
            f"| {item['source_file']} | {item['source_features']} | "
            f"{item['repaired_features']} | {item['quarantined_features']} | "
            f"{item['output_invalid_geometries']} |"
        )
    lines.extend(
        [
            "",
            "## Interprétation et limites",
            "",
            "Une variation de surface faible ne garantit pas à elle seule que la géométrie "
            "réparée représente exactement l'intention cartographique initiale. Le seuil de 1 % "
            "est un filtre de prudence opérationnel, pas une vérité métier. Les cas en quarantaine "
            "doivent être visualisés et comparés à la source avant toute décision.",
            "",
            "Les lignes en quarantaine ne sont pas perdues : le CSV conserve le nom de la source, "
            "la position de ligne, la cause de validité, le type obtenu et les attributs en JSON.",
            "",
            "Détail : reports/audits/geometry_repair_manifest.csv.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Sources: {len(summary)}")
    print(f"Features: source={total_source}; output={total_output}")
    print(f"Accepted repairs={total_repaired}; quarantine={total_quarantine}")
    print(f"Manifest={MANIFEST}")
    print(f"Report={REPORT}")


if __name__ == "__main__":
    main()
