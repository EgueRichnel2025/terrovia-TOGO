# ruff: noqa: E501
"""Vue de démonstration TERROVIA fondée uniquement sur des agrégats.
# ruff: noqa: E501

Ce module n'ouvre aucun fichier de parcelles et ne manipule aucun identifiant individuel.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

LIMITATION_TRANSLATIONS = {
    "No road-network route distance or travel time is estimated.": "L'étude ne calcule ni distance par le réseau routier ni durée de déplacement.",
    "No road condition, seasonality, transport mode, service capacity, prices or opening-hour constraints are represented.": "L'état des routes, les variations saisonnières, les modes de transport, la capacité des services, les prix et les horaires d'ouverture ne sont pas pris en compte.",
    "A mapped facility's existence does not prove that it is operational or accessible to every farmer.": "La présence d'un équipement sur la carte ne prouve ni son fonctionnement ni son accessibilité à chaque producteur.",
    "Small-holding polygons are represented by an interior representative point; this is not a farm entrance or household location.": "Chaque petite exploitation est représentée par un point situé à l'intérieur de sa parcelle. Ce point ne correspond pas nécessairement à une entrée d'exploitation ni au lieu d'habitation du producteur.",
    "ZAAP/ZAPB layer is not semantically disambiguated and is reported under the combined source-layer label.": "La couche source ne permet pas de distinguer de façon fiable les ZAAP des ZAPB. Les résultats sont donc présentés sous l'appellation combinée « ZAAP / ZAPB ».",
    "The nearest-neighbour result measures geometric proximity only.": "La méthode du plus proche voisin mesure uniquement une proximité géographique en ligne droite.",
}


def format_fr_number(value: float | int, decimals: int = 0) -> str:
    """Format a number with French grouping and decimal separators."""
    rendered = f"{value:,.{decimals}f}"
    return rendered.replace(",", "\u202f").replace(".", ",")


def translate_limitations(limitations: list[str]) -> list[str]:
    unknown = [item for item in limitations if item not in LIMITATION_TRANSLATIONS]
    if unknown:
        raise ValueError(
            "Des limites méthodologiques ne disposent pas encore d'une traduction française."
        )
    return [LIMITATION_TRANSLATIONS[item] for item in limitations]


SERVICE_COLUMNS = {
    "Marchés": {
        "indicator": "market_distance_km",
        "median": "market_distance_median_km",
        "p90": "market_distance_p90_km",
        "over_5": "market_distance_over_5km_pct",
        "over_10": "market_distance_over_10km_pct",
        "features": "market_features",
    },
    "Magasins d'intrants": {
        "indicator": "input_store_distance_km",
        "median": "input_store_distance_median_km",
        "p90": "input_store_distance_p90_km",
        "over_5": "input_store_distance_over_5km_pct",
        "over_10": "input_store_distance_over_10km_pct",
        "features": "input_store_features",
    },
    "Coopératives": {
        "indicator": "cooperative_distance_km",
        "median": "cooperative_distance_median_km",
        "p90": "cooperative_distance_p90_km",
        "over_5": "cooperative_distance_over_5km_pct",
        "over_10": "cooperative_distance_over_10km_pct",
        "features": "cooperative_features",
    },
    "ESOP": {
        "indicator": "esop_distance_km",
        "median": "esop_distance_median_km",
        "p90": "esop_distance_p90_km",
        "over_5": "esop_distance_over_5km_pct",
        "over_10": "esop_distance_over_10km_pct",
        "features": "esop_features",
    },
    "Pépinières · points": {
        "indicator": "nursery_distance_km",
        "median": "nursery_distance_median_km",
        "p90": "nursery_distance_p90_km",
        "over_5": "nursery_distance_over_5km_pct",
        "over_10": "nursery_distance_over_10km_pct",
        "features": "nursery_point_features",
    },
    "Pépinières · surfaces": {
        "indicator": "nursery_other_distance_km",
        "median": "nursery_other_distance_median_km",
        "p90": "nursery_other_distance_p90_km",
        "over_5": "nursery_other_distance_over_5km_pct",
        "over_10": "nursery_other_distance_over_10km_pct",
        "features": "nursery_other_polygon_features",
    },
    "ZAAP / ZAPB": {
        "indicator": "zaap_zapb_distance_km",
        "median": "zaap_zapb_distance_median_km",
        "p90": "zaap_zapb_distance_p90_km",
        "over_5": "zaap_zapb_distance_over_5km_pct",
        "over_10": "zaap_zapb_distance_over_10km_pct",
        "features": "zaap_zapb_polygon_features",
    },
}

EXPECTED_REGIONS = {"Centrale", "Kara", "Maritime", "Plateaux", "Savanes"}
PALETTE = {
    "forest": "#174A6E",
    "forest_light": "#267A9B",
    "paper": "#FFFFFF",
    "ink": "#16384A",
    "muted": "#607D8B",
    "clay": "#16866A",
    "gold": "#174A6E",
    "line": "#D9E6ED",
}


def validate_aggregate_frames(
    overall: pd.DataFrame,
    regional: pd.DataFrame,
    methodology: dict,
) -> None:
    """Reject incomplete or malformed aggregate inputs before rendering."""
    overall_required = {
        "indicator",
        "n",
        "median_km",
        "p90_km",
        "over_5km_pct",
        "over_10km_pct",
    }
    regional_required = {"region_nom_bdd", "farm_count"}
    for columns in SERVICE_COLUMNS.values():
        regional_required.update(
            {columns["median"], columns["p90"], columns["over_5"], columns["over_10"]}
        )

    missing_overall = sorted(overall_required - set(overall.columns))
    missing_regional = sorted(regional_required - set(regional.columns))
    if missing_overall:
        raise ValueError(f"Colonnes nationales manquantes : {', '.join(missing_overall)}")
    if missing_regional:
        raise ValueError(f"Colonnes régionales manquantes : {', '.join(missing_regional)}")

    expected_indicators = {item["indicator"] for item in SERVICE_COLUMNS.values()}
    actual_indicators = set(overall["indicator"].astype(str))
    if actual_indicators != expected_indicators:
        raise ValueError(
            "La synthèse nationale ne contient pas exactement les sept indicateurs attendus."
        )
    if overall["indicator"].duplicated().any():
        raise ValueError("La synthèse nationale contient des indicateurs en double.")
    if regional["region_nom_bdd"].duplicated().any():
        raise ValueError("La synthèse régionale contient des régions en double.")

    actual_regions = set(regional["region_nom_bdd"].astype(str))
    if actual_regions != EXPECTED_REGIONS:
        raise ValueError("La synthèse doit contenir les cinq régions administratives attendues.")

    expected_farms = int(methodology.get("farm_features", 0))
    national_counts = pd.to_numeric(overall["n"], errors="coerce")
    regional_counts = pd.to_numeric(regional["farm_count"], errors="coerce")
    if expected_farms <= 0 or national_counts.isna().any() or regional_counts.isna().any():
        raise ValueError("Les effectifs agrégés ou le périmètre méthodologique sont invalides.")
    if set(national_counts.astype(int)) != {expected_farms}:
        raise ValueError(
            "Les effectifs nationaux ne correspondent pas au périmètre méthodologique."
        )
    if int(regional_counts.sum()) != expected_farms:
        raise ValueError("La somme des effectifs régionaux ne correspond pas au total national.")

    percentage_columns = ["over_5km_pct", "over_10km_pct"]
    for columns in SERVICE_COLUMNS.values():
        percentage_columns.extend([columns["over_5"], columns["over_10"]])
    for column in percentage_columns:
        values = pd.to_numeric(
            overall[column] if column in overall else regional[column],
            errors="coerce",
        )
        if values.isna().any() or not values.between(0, 100).all():
            raise ValueError(f"Les pourcentages de la colonne {column} sont invalides.")


def load_aggregate_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Load only national and regional aggregates, never individual farm records."""
    overall_path = data_dir / "overall_accessibility_summary.csv"
    regional_path = data_dir / "regional_accessibility_summary.csv"
    methodology_path = data_dir / "methodology.json"
    missing = [
        path.name for path in (overall_path, regional_path, methodology_path) if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"Fichiers agrégés manquants dans {data_dir}: {', '.join(missing)}")

    overall = pd.read_csv(overall_path)
    regional = pd.read_csv(regional_path)
    methodology = json.loads(methodology_path.read_text(encoding="utf-8"))
    validate_aggregate_frames(overall, regional, methodology)
    return overall, regional, methodology


def build_national_summary(overall: pd.DataFrame, methodology: dict) -> pd.DataFrame:
    """Build the human-readable national table from validated aggregates."""
    indexed = overall.set_index("indicator")
    rows = []
    for label, columns in SERVICE_COLUMNS.items():
        row = indexed.loc[columns["indicator"]]
        rows.append(
            {
                "Service": label,
                "Équipements recensés": int(methodology.get(columns["features"], 0)),
                "Médiane (km)": float(row["median_km"]),
                "P90 (km)": float(row["p90_km"]),
                "À plus de 5 km (%)": float(row["over_5km_pct"]),
                "À plus de 10 km (%)": float(row["over_10km_pct"]),
            }
        )
    return pd.DataFrame(rows).sort_values("Médiane (km)", ascending=False).reset_index(drop=True)


def build_regional_view(
    regional: pd.DataFrame,
    service: str,
    threshold_km: int,
) -> pd.DataFrame:
    """Return five regional rows using only published aggregate columns."""
    if service not in SERVICE_COLUMNS:
        raise ValueError(f"Service inconnu : {service}")
    if threshold_km not in (5, 10):
        raise ValueError("Les repères disponibles sont 5 km et 10 km.")

    columns = SERVICE_COLUMNS[service]
    view = regional[
        [
            "region_nom_bdd",
            "farm_count",
            columns["median"],
            columns["p90"],
            columns["over_5"],
            columns["over_10"],
        ]
    ].copy()
    view = view.rename(
        columns={
            "region_nom_bdd": "Région",
            "farm_count": "Exploitations analysées",
            columns["median"]: "Médiane (km)",
            columns["p90"]: "P90 (km)",
            columns["over_5"]: "À plus de 5 km (%)",
            columns["over_10"]: "À plus de 10 km (%)",
        }
    )
    view["Part au-delà du repère (%)"] = view[
        "À plus de 5 km (%)" if threshold_km == 5 else "À plus de 10 km (%)"
    ]
    return view.sort_values("Médiane (km)", ascending=False).reset_index(drop=True)


def _chart_style(fig: object, height: int = 330) -> object:
    fig.update_layout(
        height=height,
        margin={"l": 8, "r": 30, "t": 12, "b": 25},
        paper_bgcolor=PALETTE["paper"],
        plot_bgcolor=PALETTE["paper"],
        font={"family": "DM Sans, sans-serif", "color": PALETTE["ink"], "size": 12},
        xaxis={"showgrid": True, "gridcolor": "#EAF2F6", "zeroline": False},
        yaxis={"showgrid": False},
        showlegend=False,
    )
    return fig


def _render_overview(
    overall: pd.DataFrame,
    regional: pd.DataFrame,
    methodology: dict,
) -> None:
    national = build_national_summary(overall, methodology)
    st.markdown(
        """<div class="hero">
        <div class="hero-top"><span class="hero-tag">TERROVIA · TOGO</span>
        <span class="hero-dot"></span><span class="hero-tag">APERÇU AGRÉGÉ</span></div>
        <h1>À quelle distance les exploitations se trouvent-elles des services agricoles ?</h1>
        <p>Cette vue rassemble les résultats nationaux et régionaux du diagnostic. Elle permet de comparer les catégories de services et de repérer les situations qui méritent une vérification complémentaire.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.info(
        "Mode agrégé : seuls des indicateurs nationaux et régionaux sont chargés. "
        "Aucune coordonnée de parcelle, aucun identifiant et aucune ligne individuelle ne sont utilisés."
    )

    k1, k2, k3 = st.columns(3)
    k1.metric("Exploitations étudiées", format_fr_number(int(methodology["farm_features"])))
    k2.metric("Régions couvertes", str(regional["region_nom_bdd"].nunique()))
    k3.metric("Familles de services", str(len(SERVICE_COLUMNS)))
    st.caption(
        "Les effectifs représentent les entités préparées pour cette étude, pas le recensement exhaustif des exploitations du Togo."
    )

    st.subheader("La distance varie fortement selon le service étudié")
    fig = px.bar(
        national.sort_values("Médiane (km)", ascending=True),
        x="Médiane (km)",
        y="Service",
        orientation="h",
        text="Médiane (km)",
        hover_data=["P90 (km)", "À plus de 5 km (%)", "À plus de 10 km (%)"],
        labels={"Médiane (km)": "Distance médiane en ligne droite", "Service": ""},
    )
    fig.update_traces(
        marker_color=PALETTE["forest_light"],
        texttemplate="%{text:.2f} km",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "%{y}<br>Médiane : %{x:.2f} km"
            "<br>P90 : %{customdata[0]:.2f} km"
            "<br>À plus de 5 km : %{customdata[1]:.1f} %"
            "<br>À plus de 10 km : %{customdata[2]:.1f} %<extra></extra>"
        ),
    )
    _chart_style(fig, 385)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "responsive": True})
    st.caption(
        "Les catégories de services ont des fonctions différentes. Ce graphique compare des distances, "
        "pas l'importance des services ni leur qualité."
    )
    with st.expander("Consulter tous les résultats nationaux"):
        st.dataframe(national, hide_index=True, width="stretch")

    st.subheader("Comparer une catégorie entre les régions")
    selected_service = st.selectbox(
        "Service à comparer", list(SERVICE_COLUMNS), key="preview_overview_service"
    )
    regional_view = build_regional_view(regional, selected_service, 5)
    chart = px.bar(
        regional_view.sort_values("Médiane (km)", ascending=True),
        x="Médiane (km)",
        y="Région",
        orientation="h",
        text="Médiane (km)",
        hover_data=["Exploitations analysées", "P90 (km)", "À plus de 5 km (%)"],
        labels={"Médiane (km)": "Distance médiane (km)", "Région": ""},
    )
    chart.update_traces(
        marker_color=PALETTE["clay"],
        texttemplate="%{text:.2f} km",
        textposition="outside",
        cliponaxis=False,
    )
    _chart_style(chart, 300)
    st.plotly_chart(chart, width="stretch", config={"displayModeBar": False, "responsive": True})

    st.subheader("Trois situations à examiner de plus près")
    signals = [
        (
            "Savanes · Magasins d'intrants",
            "43,27 % des exploitations étudiées sont à plus de 10 km d'un magasin cartographié. "
            "La médiane régionale est de 8,54 km.",
            "Vérifier l'activité des magasins, les stocks et les circuits d'approvisionnement.",
        ),
        (
            "Plateaux · Marchés",
            "La distance médiane atteint 3,42 km et 26,08 % des exploitations dépassent 5 km.",
            "Identifier les localités concernées et confronter les distances aux itinéraires réellement utilisés.",
        ),
        (
            "Savanes · Pépinières surfaciques",
            "La médiane calculée atteint 116,29 km, une valeur très atypique.",
            "Auditer d'abord la couverture et la géolocalisation de l'inventaire avant toute interprétation.",
        ),
    ]
    signal_columns = st.columns(3)
    for column, (title, observation, action) in zip(signal_columns, signals, strict=True):
        with column:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.write(observation)
                st.caption(f"À vérifier : {action}")

    st.caption(
        "Ces signaux orientent des vérifications. Ils ne constituent ni un diagnostic d'accès effectif "
        "ni un classement automatique des investissements."
    )


def _render_explorer(regional: pd.DataFrame) -> None:
    st.title("Explorer les résultats régionaux")
    st.write(
        "Choisissez un service, une région et l'un des deux repères descriptifs. "
        "Les chiffres affichés proviennent des agrégats calculés sur les exploitations préparées."
    )
    controls = st.columns([1.5, 1, 1])
    with controls[0]:
        service = st.selectbox(
            "Famille de services", list(SERVICE_COLUMNS), key="preview_explore_service"
        )
    with controls[1]:
        region = st.selectbox(
            "Région",
            ["Toutes les régions", *sorted(EXPECTED_REGIONS)],
            key="preview_explore_region",
        )
    with controls[2]:
        threshold = st.selectbox(
            "Repère descriptif", [5, 10], format_func=lambda value: f"{value} km"
        )

    view = build_regional_view(regional, service, threshold)
    filtered = view if region == "Toutes les régions" else view.loc[view["Région"].eq(region)]
    if filtered.empty:
        st.warning("Aucun résultat disponible pour cette sélection.")
        return

    if region == "Toutes les régions":
        median = float(filtered["Médiane (km)"].median())
        p90 = float(filtered["P90 (km)"].max())
        share = float(filtered["Part au-delà du repère (%)"].mean())
        context = "Comparaison des cinq régions ; les indicateurs affichés ci-dessous sont des résumés régionaux."
    else:
        selected = filtered.iloc[0]
        median = float(selected["Médiane (km)"])
        p90 = float(selected["P90 (km)"])
        share = float(selected["Part au-delà du repère (%)"])
        context = f"Résultats de la région {region}."

    k1, k2, k3 = st.columns(3)
    k1.metric("Médiane régionale", f"{format_fr_number(median, 2)} km")
    k2.metric("P90 régional", f"{format_fr_number(p90, 2)} km")
    k3.metric(f"Part à plus de {threshold} km", f"{format_fr_number(share, 1)} %")
    st.caption(context)

    chart_data = filtered.sort_values("Médiane (km)", ascending=True)
    chart = px.bar(
        chart_data,
        x="Médiane (km)",
        y="Région",
        orientation="h",
        text="Médiane (km)",
        hover_data=["Exploitations analysées", "P90 (km)", "Part au-delà du repère (%)"],
        labels={"Médiane (km)": "Distance médiane (km)", "Région": ""},
    )
    chart.update_traces(
        marker_color=PALETTE["forest_light"],
        texttemplate="%{text:.2f} km",
        textposition="outside",
        cliponaxis=False,
    )
    _chart_style(chart, max(240, 90 + 55 * len(chart_data)))
    st.plotly_chart(chart, width="stretch", config={"displayModeBar": False, "responsive": True})
    st.dataframe(filtered, hide_index=True, width="stretch")
    st.download_button(
        "Télécharger cette synthèse régionale (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="terrovia_synthese_regionale.csv",
        mime="text/csv",
    )
    st.caption(
        "Attention : pour « Toutes les régions », la médiane ci-dessus est la médiane des cinq médianes régionales "
        "et le P90 affiché est le plus élevé des cinq P90 régionaux. Consultez le tableau pour comparer les régions."
    )


def _render_method(methodology: dict) -> None:
    st.title("Méthode et limites")
    st.write(
        "TERROVIA calcule, pour chaque exploitation cartographiée, la distance euclidienne "
        "entre un point représentatif intérieur et la géométrie recensée la plus proche. "
        "Les calculs sont effectués séparément pour chaque famille d'équipements."
    )
    cols = st.columns(3)
    cols[0].metric("Système de coordonnées", methodology.get("metric_crs", "Non précisé"))
    cols[1].metric("Unité d'analyse", "Exploitation cartographiée")
    cols[2].metric("Seuils fixes", "5 km et 10 km")
    st.subheader("Comment interpréter les indicateurs ?")
    st.markdown(
        "- **Médiane :** la moitié des exploitations a une distance inférieure ou égale à cette valeur.\n"
        "- **P90 :** 90 % des distances sont inférieures ou égales à cette valeur.\n"
        "- **Part au-delà de 5 ou 10 km :** proportion des exploitations qui dépassent le repère choisi."
    )
    st.subheader("Limites à garder en tête")
    limitations = translate_limitations(methodology.get("limitations", []))
    if limitations:
        st.markdown("\n".join(f"- {item}" for item in limitations))
    st.warning(
        "Une proximité géométrique ne garantit pas un accès réel : les itinéraires, les temps, "
        "les coûts, les horaires, les stocks, les capacités et le fonctionnement des équipements "
        "ne sont pas mesurés par cette analyse."
    )
    st.info(
        "Ce mode de démonstration ne charge que les synthèses nationales et régionales. "
        "Les données détaillées restent locales et ne sont pas nécessaires à cette exploration."
    )


def render_aggregate_preview(
    page_key: str,
    overall: pd.DataFrame,
    regional: pd.DataFrame,
    methodology: dict,
) -> None:
    """Render one of the existing three dashboard spaces in aggregate-only mode."""
    if page_key == "overview":
        _render_overview(overall, regional, methodology)
    elif page_key == "explore":
        _render_explorer(regional)
    else:
        _render_method(methodology)

    st.markdown(
        '<div class="footnote">TERROVIA · Aperçu fondé sur des agrégats régionaux et nationaux. '
        "Aucune observation individuelle n'est chargée dans ce mode.</div>",
        unsafe_allow_html=True,
    )
