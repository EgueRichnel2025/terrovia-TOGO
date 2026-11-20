"""Create static maps for the first TERROVIA accessibility diagnostic."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely import from_wkt

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "data/raw/administrative"
AGRI = ROOT / "data/processed/agriculture"
ACCESS = ROOT / "data/processed/accessibility"
FIGURES = ROOT / "reports/figures"
CRS_METRIC = "EPSG:32631"


def read_regions() -> gpd.GeoDataFrame:
    path = next(ADMIN.glob("*regions*.csv"))
    frame = pd.read_csv(path)
    frame["geometry"] = frame["geometry"].map(from_wkt)
    regions = gpd.GeoDataFrame(frame, geometry="geometry", crs="EPSG:4326")
    crosswalk = pd.read_csv(ROOT / "reports/audits/candidate_region_fid_name_crosswalk.csv")
    regions = regions.merge(
        crosswalk[["region_FID", "candidate_region_name", "status"]],
        left_on="FID",
        right_on="region_FID",
        how="left",
        validate="one_to_one",
    )
    if not regions["status"].eq("candidate_strong").all():
        raise ValueError("La correspondance FID-région n'est pas suffisamment convergente.")
    return regions.to_crs(CRS_METRIC)


def add_scale_bar(ax, length_km: int = 20) -> None:
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x = x0 + (x1 - x0) * 0.06
    y = y0 + (y1 - y0) * 0.06
    length = length_km * 1000
    ax.plot([x, x + length], [y, y], color="black", linewidth=3)
    ax.text(
        x + length / 2,
        y + (y1 - y0) * 0.012,
        f"{length_km} km",
        ha="center",
        va="bottom",
        fontsize=8,
    )


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    regions = read_regions()
    summary = pd.read_csv(ACCESS / "regional_accessibility_summary.csv")
    regions = regions.merge(
        summary[
            [
                "region_nom_bdd",
                "farm_count",
                "market_distance_median_km",
                "market_distance_p90_km",
                "market_distance_over_5km_pct",
            ]
        ],
        left_on="candidate_region_name",
        right_on="region_nom_bdd",
        how="left",
        validate="one_to_one",
    )
    if regions["market_distance_median_km"].isna().any():
        raise ValueError("Certaines régions ne disposent pas de statistiques d'accessibilité.")
    regions.to_crs("EPSG:4326").to_file(
        ACCESS / "regions_accessibility.geojson", driver="GeoJSON", index=False
    )

    # Map 1: regional median straight-line proximity to mapped market polygons.
    fig, ax = plt.subplots(figsize=(9, 10))
    regions.plot(
        column="market_distance_median_km",
        cmap="YlOrRd",
        linewidth=0.9,
        edgecolor="#343434",
        legend=True,
        legend_kwds={"label": "Distance médiane au marché le plus proche (km)", "shrink": 0.68},
        ax=ax,
    )
    for row in regions.itertuples():
        point = row.geometry.representative_point()
        ax.annotate(
            f"{row.candidate_region_name}\n{row.market_distance_median_km:.2f} km",
            (point.x, point.y),
            ha="center",
            va="center",
            fontsize=8,
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": "white",
                "alpha": 0.82,
                "edgecolor": "none",
            },
        )
    ax.set_title(
        "TERROVIA — Proximité potentielle des exploitations aux marchés", fontsize=13, pad=16
    )
    ax.text(
        0.5,
        1.005,
        "Médiane régionale des distances en ligne droite · données agricoles cartographiées",
        transform=ax.transAxes,
        ha="center",
        fontsize=8,
    )
    ax.set_axis_off()
    add_scale_bar(ax)
    fig.text(
        0.5,
        0.025,
        "Source : couches agricoles Geodata Togo · Calculs TERROVIA · CRS métrique EPSG:32631\n"
        "Attention : distance euclidienne, non routière ; régions administratives sans CRS source déclaré.",  # noqa: E501
        ha="center",
        fontsize=7,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    fig.savefig(FIGURES / "regional_market_accessibility.png", dpi=260, bbox_inches="tight")
    plt.close(fig)

    # Map 2: spatial context of farms and mapped markets.
    farm_path = next(AGRI.glob("*Petites exploitations agricoles*_repaired.geojson"))
    market_path = next(AGRI.glob("*Marchés*_repaired.geojson"))
    farms = gpd.read_file(farm_path).to_crs(CRS_METRIC)
    markets = gpd.read_file(market_path).to_crs(CRS_METRIC)
    fig, ax = plt.subplots(figsize=(9, 10))
    regions.boundary.plot(ax=ax, color="#444444", linewidth=0.8)
    farms.geometry.representative_point().plot(
        ax=ax,
        color="#2b7a78",
        markersize=0.45,
        alpha=0.32,
        label=f"Petites exploitations ({len(farms):,})",
        rasterized=True,
    )
    markets.geometry.representative_point().plot(
        ax=ax,
        color="#c44e52",
        markersize=8,
        alpha=0.9,
        label=f"Marchés cartographiés ({len(markets):,})",
        zorder=4,
    )
    ax.set_title("TERROVIA — Répartition des exploitations et des marchés", fontsize=13, pad=16)
    ax.legend(loc="lower left", frameon=True, fontsize=8)
    ax.set_axis_off()
    add_scale_bar(ax)
    fig.text(
        0.5,
        0.025,
        "Les points représentent les points intérieurs des polygones agricoles et les centroïdes des marchés.\n"  # noqa: E501
        "Carte descriptive : elle ne représente ni les routes ni les flux commerciaux.",
        ha="center",
        fontsize=7,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    fig.savefig(FIGURES / "farms_and_markets_distribution.png", dpi=260, bbox_inches="tight")
    plt.close(fig)

    print("Maps created:")
    for path in sorted(FIGURES.glob("*.png")):
        print(path, path.stat().st_size)
    print("Regional map values:")
    print(
        regions[
            [
                "candidate_region_name",
                "farm_count",
                "market_distance_median_km",
                "market_distance_p90_km",
                "market_distance_over_5km_pct",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
