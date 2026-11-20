"""Audit administrative boundaries and their consistency with agricultural layers.

Raw inputs are read-only. EPSG:4326 for administrative WKT is tested as a
provisional hypothesis based on coordinate ranges and agricultural overlays.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import from_wkt, is_valid_reason
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
RAW_ADMIN = ROOT / "data/raw/administrative"
PREP_AGRI = ROOT / "data/processed/agriculture"
REPORTS = ROOT / "reports"
AUDITS = REPORTS / "audits"
CRS_HYPOTHESIS = "EPSG:4326"
ADMIN_FILES = {
    "communes": "limites_administratives_communes_togo.csv",
    "prefectures": "limites_administratives_prefectures_togo.csv",
    "regions": "limites_administratives_regions_togo.csv",
}


def load_admin(level: str, filename: str) -> gpd.GeoDataFrame:
    path = RAW_ADMIN / filename
    frame = pd.read_csv(path)
    if not {"FID", "geometry"}.issubset(frame.columns):
        raise ValueError(f"Colonnes inattendues dans {path.name}: {frame.columns.tolist()}")
    frame["geometry"] = frame["geometry"].map(from_wkt)
    return gpd.GeoDataFrame(frame, geometry="geometry", crs=CRS_HYPOTHESIS).assign(level=level)


def representative_points(gdf: gpd.GeoDataFrame) -> gpd.GeoSeries:
    return gdf.geometry.representative_point()


def safe_area_km2(geometry, metric_crs="EPSG:32631") -> float:
    return gpd.GeoSeries([geometry], crs=CRS_HYPOTHESIS).to_crs(metric_crs).area.iloc[0] / 1_000_000


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    AUDITS.mkdir(exist_ok=True)
    admin = {level: load_admin(level, filename) for level, filename in ADMIN_FILES.items()}
    regions = admin["regions"]
    region_union = unary_union(regions.geometry)

    admin_rows: list[dict] = []
    for level, frame in admin.items():
        for row in frame.itertuples():
            geom = row.geometry
            admin_rows.append(
                {
                    "level": level,
                    "FID": row.FID,
                    "geometry_type": geom.geom_type,
                    "is_valid": bool(geom.is_valid),
                    "validity_reason": "Valid Geometry" if geom.is_valid else is_valid_reason(geom),
                    "area_km2_candidate_32631": safe_area_km2(geom) if geom.is_valid else None,
                    "bounds_minx": geom.bounds[0],
                    "bounds_miny": geom.bounds[1],
                    "bounds_maxx": geom.bounds[2],
                    "bounds_maxy": geom.bounds[3],
                    "crs_status": "EPSG:4326 hypothesis only; source CSV has no CRS metadata",
                }
            )
    pd.DataFrame(admin_rows).to_csv(AUDITS / "administrative_geometry_audit.csv", index=False)

    # Cross-level coverage and overlap tests. Area calculations are provisional.
    commune_union = unary_union(admin["communes"].geometry)
    prefecture_union = unary_union(admin["prefectures"].geometry)
    region_union_area = safe_area_km2(region_union)
    commune_union_area = safe_area_km2(commune_union)
    prefecture_union_area = safe_area_km2(prefecture_union)
    hierarchy = {
        "communes_outside_prefectures_km2": safe_area_km2(
            commune_union.difference(prefecture_union)
        ),
        "prefectures_outside_regions_km2": safe_area_km2(prefecture_union.difference(region_union)),
        "communes_outside_regions_km2": safe_area_km2(commune_union.difference(region_union)),
        "regions_union_area_km2": region_union_area,
        "prefectures_union_area_km2": prefecture_union_area,
        "communes_union_area_km2": commune_union_area,
        "region_polygon_count": len(regions),
        "region_union_valid": bool(region_union.is_valid),
    }

    # Pairwise polygon overlap between regions (area beyond shared boundaries).
    region_overlap_rows = []
    for i, left in regions.iterrows():
        for j, right in regions.iterrows():
            if j <= i:
                continue
            overlap = left.geometry.intersection(right.geometry)
            area = safe_area_km2(overlap) if not overlap.is_empty else 0.0
            if area > 0.001:
                region_overlap_rows.append(
                    {"FID_1": left.FID, "FID_2": right.FID, "overlap_km2": area}
                )
    pd.DataFrame(region_overlap_rows, columns=["FID_1", "FID_2", "overlap_km2"]).to_csv(
        AUDITS / "regional_polygon_overlaps.csv", index=False
    )

    # Agricultural points and polygon representative points are tested against
    # the regional union. This is a spatial consistency test, not proof of CRS.
    agri_rows: list[dict] = []
    region_name_rows: list[dict] = []
    agri_files = sorted(PREP_AGRI.glob("*_repaired.geojson"))
    for path in agri_files:
        frame = gpd.read_file(path)
        if frame.crs is None:
            raise ValueError(f"CRS absent dans la couche préparée: {path.name}")
        points = representative_points(frame)
        inside = points.within(region_union) | points.intersects(region_union.boundary)
        labels = (
            frame["region_nom_bdd"].fillna("<NULL>").astype(str)
            if "region_nom_bdd" in frame
            else pd.Series("<ABSENT>", index=frame.index)
        )
        for label, count in labels.value_counts(dropna=False).items():
            region_name_rows.append(
                {"layer": path.name, "region_nom_bdd": label, "feature_count": int(count)}
            )
        agri_rows.append(
            {
                "layer": path.name,
                "feature_count": len(frame),
                "declared_crs": str(frame.crs),
                "representative_points_inside_region_union": int(inside.sum()),
                "representative_points_outside_region_union": int((~inside).sum()),
                "outside_percent": round(float((~inside).mean() * 100), 3) if len(frame) else 0,
                "geometry_invalid_count": int((~frame.geometry.is_valid).sum()),
                "geometry_empty_count": int(frame.geometry.is_empty.sum()),
                "region_attribute_present": "region_nom_bdd" in frame.columns,
            }
        )

    # Derive a tentative FID-to-region-label crosswalk from agricultural
    # representative points; preserve full counts and ambiguity rather than
    # asserting a name when evidence is weak.
    region_votes: dict[str, dict[str, int]] = {str(fid): {} for fid in regions.FID}
    for path in agri_files:
        frame = gpd.read_file(path)
        if "region_nom_bdd" not in frame.columns:
            continue
        points = representative_points(frame)
        for region_row in regions.itertuples():
            mask = points.within(region_row.geometry) | points.intersects(
                region_row.geometry.boundary
            )
            subset = frame.loc[mask, "region_nom_bdd"].dropna().astype(str)
            votes = region_votes[str(region_row.FID)]
            for label, count in subset.value_counts().items():
                votes[label] = votes.get(label, 0) + int(count)
    crosswalk_rows = []
    for fid, votes in region_votes.items():
        total = sum(votes.values())
        ranked = sorted(votes.items(), key=lambda item: item[1], reverse=True)
        top_label, top_count = ranked[0] if ranked else ("", 0)
        share = top_count / total if total else 0
        crosswalk_rows.append(
            {
                "region_FID": fid,
                "candidate_region_name": top_label,
                "top_vote_count": top_count,
                "all_votes": total,
                "top_vote_share": round(share, 4),
                "status": "candidate_strong"
                if share >= 0.9 and total >= 30
                else "ambiguous_or_insufficient",
                "votes_json": json.dumps(votes, ensure_ascii=False, sort_keys=True),
            }
        )

    pd.DataFrame(agri_rows).to_csv(AUDITS / "agricultural_regional_containment.csv", index=False)
    pd.DataFrame(region_name_rows).to_csv(
        AUDITS / "agricultural_region_attribute_counts.csv", index=False
    )
    pd.DataFrame(crosswalk_rows).to_csv(
        AUDITS / "candidate_region_fid_name_crosswalk.csv", index=False
    )

    lines = [
        "# Audit de cohérence territoriale — TERROVIA",
        "",
        "Date d'exécution : 2026-11-20.",
        "",
        "> **Précaution CRS :** les CSV administratifs ne déclarent aucun CRS. EPSG:4326 est testé comme hypothèse de travail, car les coordonnées ressemblent à des longitudes/latitudes et les couches agricoles sont déclarées EPSG:4326. Cette concordance spatiale ne constitue pas une preuve officielle du CRS.",  # noqa: E501
        "",
        "## 1. Géométries administratives",
        "",
        "| Niveau | Entités | Géométries invalides | CRS |",
        "|---|---:|---:|---|",
    ]
    for level, frame in admin.items():
        lines.append(
            f"| {level} | {len(frame)} | {(~frame.geometry.is_valid).sum()} | non déclaré (hypothèse EPSG:4326) |"  # noqa: E501
        )
    lines += [
        "",
        "Les détails par FID, les types, raisons d'invalidité et emprises sont dans `audits/administrative_geometry_audit.csv`.",  # noqa: E501
        "",
        "## 2. Cohérence entre niveaux administratifs",
        "",
        "| Contrôle | Résultat (km²) |",
        "|---|---:|",
    ]
    for key, value in hierarchy.items():
        if isinstance(value, float):
            lines.append(f"| {key} | {value:.6f} |")
        else:
            lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "Les différences de couverture sont des surfaces calculées sous l'hypothèse EPSG:4326 puis projetées en EPSG:32631. Elles doivent être interprétées comme diagnostics, non comme correction des limites.",  # noqa: E501
        "",
        "## 3. Positionnement des couches agricoles",
        "",
        "| Couche | Entités | Points représentatifs hors union régionale | Hors (%) | Géométries invalides |",  # noqa: E501
        "|---|---:|---:|---:|---:|",
    ]
    for row in agri_rows:
        lines.append(
            f"| {row['layer']} | {row['feature_count']} | {row['representative_points_outside_region_union']} | {row['outside_percent']:.3f} | {row['geometry_invalid_count']} |"  # noqa: E501
        )
    lines += [
        "",
        "Le test utilise un point représentatif par géométrie (y compris pour les polygones). Il vérifie l'appartenance du point à l'union des régions, pas la proportion de surface d'un polygone agricole située à l'intérieur du Togo.",  # noqa: E501
        "",
        "## 4. Correspondance provisoire FID-région",
        "",
        "Les votes des attributs `region_nom_bdd` des couches agricoles sont compilés dans `audits/candidate_region_fid_name_crosswalk.csv`. Un statut `candidate_strong` signifie seulement qu'au moins 90 % des votes convergent avec au moins 30 observations. Cette correspondance reste à confronter à une nomenclature administrative officielle.",  # noqa: E501
        "",
        "## 5. Limites et décisions",
        "",
        "- Les CSV administratifs ne contiennent aucun nom de région, préfecture ou commune ; aucun rapprochement population par libellé n'est autorisé à ce stade.",  # noqa: E501
        "- Le découpage Grand Lomé / Maritime sans Grand Lomé des statistiques RGPH-5 ne correspond pas directement aux cinq polygones régionaux disponibles.",  # noqa: E501
        "- Les FID hiérarchiques peuvent suggérer une structure de codes, mais ils ne suffisent pas à prouver une nomenclature ni à attribuer des noms.",  # noqa: E501
        "- Les chevauchements régionaux détectés, s'il y en a, sont listés dans `audits/regional_polygon_overlaps.csv`.",  # noqa: E501
        "- Aucune donnée brute n'a été modifiée. Aucun CRS n'a été ajouté aux CSV sources. Aucun polygone administratif n'a été réparé automatiquement.",  # noqa: E501
        "",
        "## Fichiers produits",
        "",
        "- `audits/administrative_geometry_audit.csv`",
        "- `audits/regional_polygon_overlaps.csv`",
        "- `audits/agricultural_regional_containment.csv`",
        "- `audits/agricultural_region_attribute_counts.csv`",
        "- `audits/candidate_region_fid_name_crosswalk.csv`",
    ]
    report = REPORTS / "AUDIT_COHERENCE_TERRITORIALE_2026-11-20.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Admin layers: {len(admin)}; total polygons: {sum(map(len, admin.values()))}")
    print(
        f"Agricultural layers: {len(agri_files)}; total features: {sum(r['feature_count'] for r in agri_rows)}"  # noqa: E501
    )
    print(
        f"Regional union valid: {region_union.is_valid}; region overlap pairs: {len(region_overlap_rows)}"  # noqa: E501
    )
    print(f"Report: {report}")
    print("Hierarchy diagnostics:", json.dumps(hierarchy, ensure_ascii=False, indent=2))
    print("Region crosswalk:", json.dumps(crosswalk_rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
