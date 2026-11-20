# ruff: noqa: E501
"""TERROVIA — tableau de bord géospatial d'accessibilité agricole."""

from __future__ import annotations

import hashlib
import json
from math import ceil
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/accessibility"

PALETTE = {
    "forest": "#173F3A",
    "forest_light": "#24554E",
    "sand": "#F3F0E7",
    "paper": "#FFFEFA",
    "ink": "#203A36",
    "muted": "#78847D",
    "clay": "#D97757",
    "gold": "#D8A64B",
    "line": "#E7E4DA",
    "mint": "#E4EEE8",
}

METRICS = {
    "Marchés": ("market_distance_km", "Distance au marché le plus proche", "marché"),
    "Magasins d'intrants": (
        "input_store_distance_km",
        "Distance au magasin d'intrants le plus proche",
        "intrants",
    ),
    "Coopératives": (
        "cooperative_distance_km",
        "Distance à la coopérative la plus proche",
        "coopérative",
    ),
    "ESOP": ("esop_distance_km", "Distance à l'ESOP la plus proche", "ESOP"),
    "Pépinières · points": (
        "nursery_distance_km",
        "Distance à la pépinière ponctuelle la plus proche",
        "pépinière",
    ),
    "Pépinières · surfaces": (
        "nursery_other_distance_km",
        "Distance à la pépinière surfacique la plus proche",
        "pépinière",
    ),
    "ZAAP / ZAPB": (
        "zaap_zapb_distance_km",
        "Distance à la géométrie ZAAP / ZAPB la plus proche",
        "ZAAP / ZAPB",
    ),
}


@st.cache_data(show_spinner="Chargement des données territoriales…")
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
    farms = pd.read_csv(DATA / "small_farms_potential_accessibility.csv")
    summary = pd.read_csv(DATA / "regional_accessibility_summary.csv")
    with (DATA / "regions_accessibility.geojson").open(encoding="utf-8") as stream:
        regions = json.load(stream)
    with (DATA / "methodology.json").open(encoding="utf-8") as stream:
        methodology = json.load(stream)
    return farms, summary, regions, methodology


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {{
            --forest: {PALETTE["forest"]};
            --forest-light: {PALETTE["forest_light"]};
            --sand: {PALETTE["sand"]};
            --paper: {PALETTE["paper"]};
            --ink: {PALETTE["ink"]};
            --muted: {PALETTE["muted"]};
            --clay: {PALETTE["clay"]};
            --gold: {PALETTE["gold"]};
            --line: {PALETTE["line"]};
        }}
        html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
        .stApp {{ background: var(--sand); color: var(--ink); }}
        /* Interface épurée : retirer la barre d'outils Streamlit et son bandeau coloré.
           On conserve l'en-tête fonctionnel pour ne pas perdre le contrôle de la sidebar. */
        [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        [data-testid="stHeader"] {{ background: transparent; box-shadow: none; }}
        [data-testid="stMainBlockContainer"] {{
            max-width: 1380px; padding-top: 1.25rem; padding-bottom: 2.5rem;
        }}
        [data-testid="stSidebar"] {{
            background: var(--forest); border-right: 1px solid rgba(255,255,255,.08);
        }}
        [data-testid="stSidebar"] * {{ color: #F4F1E8; }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ color: #D4E0D8; }}
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            color: #E2EAE3; font-size: .78rem; font-weight: 600; letter-spacing: .02em;
        }}
        /* Selectbox: surface claire + texte sombre, y compris la valeur sélectionnée. */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: #FFFEFA !important; border: 1px solid #D8DED7 !important;
            border-radius: 10px !important; min-height: 42px;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] [data-baseweb="select"] div,
        [data-testid="stSidebar"] [data-baseweb="select"] span {{
            color: #173F3A !important; -webkit-text-fill-color: #173F3A !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] input {{
            color: #173F3A !important; -webkit-text-fill-color: #173F3A !important;
            caret-color: #173F3A !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] svg {{ fill: #173F3A !important; }}
        /* Le menu déroulant BaseWeb est rendu dans un portail hors de la sidebar. */
        [data-baseweb="popover"] [data-baseweb="menu"],
        [data-baseweb="popover"] ul {{ background: #FFFEFA !important; }}
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="popover"] [role="option"] * {{
            color: #173F3A !important; -webkit-text-fill-color: #173F3A !important;
        }}
        [data-baseweb="popover"] [role="option"]:hover {{ background: #E4EEE8 !important; }}
        [data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] {{ padding-top: .35rem; }}
        [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{ background: #E2B66F; border-color: #E2B66F; }}
        [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.17); }}
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ color: #B8CBC0; font-size: .72rem; }}
        [data-testid="stPlotlyChart"] {{
            background: transparent; border-radius: 14px;
        }}
        [data-testid="stDataFrame"] {{ border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: var(--paper); border: 1px solid var(--line); border-radius: 16px;
            padding: .95rem 1rem .65rem;
        }}
        [data-testid="stExpander"] {{ border: 1px solid var(--line); border-radius: 12px; background: var(--paper); }}
        [data-testid="stDownloadButton"] button {{
            background: var(--forest); color: white; border: 0; border-radius: 9px;
            padding: .55rem 1rem; font-weight: 600;
        }}
        [data-testid="stDownloadButton"] button:hover {{ background: var(--forest-light); color: white; }}
        .brand-lockup {{ display:flex; align-items:center; gap:11px; margin: .25rem 0 2.1rem; }}
        .brand-mark {{
            width:40px; height:40px; border-radius:13px; background:#D9A65C;
            display:flex; align-items:center; justify-content:center; color:#173F3A;
            font-family:'Manrope',sans-serif; font-weight:800; font-size:1rem;
        }}
        .brand-name {{ color:#FFFDF5; font:800 1.12rem 'Manrope',sans-serif; letter-spacing:.08em; }}
        .brand-sub {{ color:#B8CBC0; font-size:.62rem; letter-spacing:.16em; text-transform:uppercase; margin-top:2px; }}
        .side-kicker {{ color:#D9A65C; font-size:.66rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; margin:0 0 .45rem; }}
        .side-title {{ color:#FFFDF5; font:700 1.05rem 'Manrope',sans-serif; margin:0 0 .35rem; }}
        .side-copy {{ color:#B8CBC0; font-size:.88rem; line-height:1.6; margin-bottom:1.15rem; }}
        .hero {{
            background:var(--forest); color:#F9F6EC; padding:1.25rem 1.55rem 1.2rem;
            border-radius:20px; position:relative; overflow:hidden; margin-bottom:1.25rem;
            box-shadow:0 12px 32px rgba(23,63,58,.10);
        }}
        .hero:after {{
            content:''; position:absolute; right:-56px; top:-125px; width:340px; height:340px;
            border:1px solid rgba(222,183,120,.22); border-radius:50%;
            box-shadow:0 0 0 32px rgba(222,183,120,.035),0 0 0 70px rgba(222,183,120,.025);
        }}
        .hero-top {{ display:flex; align-items:center; gap:10px; margin-bottom:.8rem; position:relative; z-index:1; }}
        .hero-tag {{ font-size:.74rem; font-weight:700; letter-spacing:.12em; color:#E5B873; text-transform:uppercase; }}
        .hero-dot {{ width:4px; height:4px; border-radius:50%; background:#E5B873; }}
        .hero h1 {{
            color:#FFFDF5; font:800 clamp(1.5rem,2.15vw,2rem) 'Manrope',sans-serif;
            letter-spacing:-.045em; line-height:1.12; margin:0 0 .6rem; max-width:820px; position:relative; z-index:1;
        }}
        .hero p {{ color:#D6E1D9; font-size:.91rem; max-width:780px; line-height:1.55; margin:0; position:relative; z-index:1; }}
        .hero-foot {{ display:flex; gap:18px; flex-wrap:wrap; margin-top:1.1rem; position:relative; z-index:1; }}
        .hero-foot span {{ color:#D6E1D9; font-size:.78rem; letter-spacing:.02em; }}
        .hero-foot b {{ color:#FFFDF5; font-weight:700; }}
        .section-head {{ display:flex; align-items:flex-end; justify-content:space-between; gap:12px; margin:1.5rem 0 .7rem; }}
        .section-kicker {{ color:var(--clay); font-size:.73rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.2rem; }}
        .section-title {{ color:var(--ink); font:800 1.08rem 'Manrope',sans-serif; letter-spacing:-.025em; margin:0; }}
        .section-note {{ color:var(--muted); font-size:.82rem; }}
        .kpi-card {{
            background:var(--paper); border:1px solid var(--line); border-radius:15px;
            padding:1rem 1.05rem .95rem; min-height:120px; box-shadow:0 3px 14px rgba(32,58,54,.025);
        }}
        .kpi-label {{ color:var(--muted); font-size:.82rem; font-weight:600; margin-bottom:.55rem; }}
        .kpi-value {{ color:var(--ink); font:800 1.65rem 'Manrope',sans-serif; letter-spacing:-.055em; line-height:1.08; }}
        .kpi-unit {{ color:var(--forest-light); font-size:.84rem; font-weight:700; margin-left:3px; }}
        .kpi-foot {{ color:#89958D; font-size:.74rem; line-height:1.4; margin-top:.55rem; }}
        .panel {{ background:var(--paper); border:1px solid var(--line); border-radius:16px; padding:1rem 1rem .6rem; }}
        .panel-title {{ color:var(--ink); font:700 .94rem 'Manrope',sans-serif; margin:0 0 .15rem; }}
        .panel-sub {{ color:var(--muted); font-size:.79rem; margin:0 0 .65rem; }}
        .insight {{
            border-left:3px solid var(--clay); padding:.75rem .9rem; background:#F8F1E7;
            border-radius:0 10px 10px 0; color:#53645B; font-size:.88rem; line-height:1.6;
        }}
        .insight strong {{ color:var(--forest); }}
        .method-banner {{
            background:#E7EEE8; border:1px solid #D3E1D8; border-radius:11px;
            color:#405A50; padding:.72rem .95rem; font-size:.75rem; line-height:1.55;
            margin:.15rem 0 .25rem;
        }}
        .method-banner b {{ color:#24554E; font-size:.65rem; letter-spacing:.1em; margin-right:.35rem; }}
        .method-banner strong {{ color:#A34E3C; }}
        .status-pill {{
            display:inline-block; padding:.28rem .55rem; border-radius:30px;
            background:#E5EEE8; color:#28564B; font-size:.63rem; font-weight:700; letter-spacing:.04em;
        }}
        .footnote {{ color:#7D8981; font-size:.76rem; line-height:1.55; padding:.8rem .1rem; }}
        /* Mise en page fluide : les colonnes se réorganisent selon la largeur disponible. */
        [data-testid="stMainBlockContainer"] {{
            width: 100%;
            max-width: 1380px;
            box-sizing: border-box;
        }}
        [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap;
            align-items: stretch;
        }}
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            min-width: 0;
        }}
        [data-testid="stPlotlyChart"] {{
            width: 100% !important;
            max-width: 100%;
            min-width: 0;
            overflow: hidden;
        }}
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {{
            width: 100%;
            max-width: 100%;
            overflow-x: auto;
        }}
        .hero, .method-banner, .insight, .kpi-card {{
            max-width: 100%;
            overflow-wrap: anywhere;
        }}

        @media (max-width: 1100px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-left: 1.25rem;
                padding-right: 1.25rem;
            }}
        }}

        @media (max-width: 900px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }}
            [data-testid="stHorizontalBlock"] {{
                gap: .85rem;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
                flex: 1 1 calc(50% - .85rem) !important;
                width: auto !important;
                min-width: min(100%, 250px) !important;
            }}
            .section-head {{
                align-items: flex-start;
                flex-direction: column;
                gap: .25rem;
            }}
            .section-note {{
                max-width: 100%;
            }}
            .hero {{
                padding: 1.2rem 1.25rem;
                border-radius: 16px;
            }}
            .hero h1 {{
                font-size: clamp(1.65rem, 3.4vw, 2.1rem);
            }}
            .brand-lockup {{
                margin-bottom: 1.25rem;
            }}
        }}

        @media (max-width: 640px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-left: .75rem;
                padding-right: .75rem;
                padding-top: .65rem;
                padding-bottom: 1.5rem;
            }}
            [data-testid="stHorizontalBlock"] {{
                flex-direction: column !important;
                flex-wrap: nowrap !important;
                gap: .7rem;
            }}
            [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 0 !important;
                max-width: 100% !important;
            }}
            .hero {{
                padding: 1rem;
                margin-bottom: .9rem;
                border-radius: 14px;
            }}
            .hero-top {{
                align-items: flex-start;
                flex-wrap: wrap;
                gap: 6px;
                margin-bottom: .65rem;
            }}
            .hero-tag {{
                font-size: .7rem;
                letter-spacing: .08em;
            }}
            .hero h1 {{
                font-size: clamp(1.45rem, 6.5vw, 1.85rem);
                line-height: 1.18;
                letter-spacing: -.03em;
            }}
            .hero p {{
                font-size: .98rem;
                line-height: 1.6;
            }}
            .hero:after {{
                right: -180px;
                top: -180px;
            }}
            .method-banner {{
                padding: .7rem .8rem;
                font-size: .86rem;
            }}
            .section-head {{
                margin-top: 1.15rem;
                margin-bottom: .6rem;
            }}
            .section-title {{
                font-size: 1.14rem;
                line-height: 1.3;
            }}
            .section-note {{
                font-size: .86rem;
                line-height: 1.5;
            }}
            .kpi-card {{
                min-height: 0;
                padding: .9rem;
            }}
            .kpi-value {{
                font-size: 1.7rem;
            }}
            [data-testid="stVerticalBlockBorderWrapper"] {{
                padding: .7rem .7rem .45rem;
                border-radius: 13px;
            }}
            [data-testid="stPlotlyChart"] {{
                min-height: 260px;
            }}
            [data-testid="stDataFrame"] {{
                font-size: .82rem;
            }}
            [data-testid="stDownloadButton"] button {{
                width: 100%;
                min-height: 44px;
                white-space: normal;
            }}
            [data-testid="stSidebar"] {{
                width: min(88vw, 20rem);
                min-width: min(88vw, 20rem);
                max-width: min(88vw, 20rem);
            }}
            [data-testid="stSidebarNav"] a {{
                white-space: normal;
                line-height: 1.35;
            }}
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
                font-size: .94rem;
            }}
            .footnote {{
                font-size: .82rem;
            }}
        }}

        @media (max-width: 380px) {{
            [data-testid="stMainBlockContainer"] {{
                padding-left: .6rem;
                padding-right: .6rem;
            }}
            .hero h1 {{
                font-size: 1.42rem;
            }}
            .section-title {{
                font-size: 1.08rem;
            }}
            .kpi-value {{
                font-size: 1.55rem;
            }}
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: .45rem; border-bottom: 1px solid #DEDCD3; margin-bottom: 1.2rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding: .65rem 1rem; font-size: .9rem; font-weight: 650;
        }}
        .stTabs [aria-selected="true"] {{
            color: #173F3A !important; border-bottom-color: #D97757 !important;
        }}
        [data-testid="stExpander"] {{
            border: 1px solid #E2DFD5; border-radius: 12px; background: #FFFEFA;
        }}
        /* Lisibilité renforcée : textes, navigation, contrôles et tableaux. */
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {{
            font-size: 1.02rem; line-height: 1.72;
        }}
        [data-testid="stCaptionContainer"] p,
        .stCaption {{ font-size: .88rem !important; line-height: 1.55; }}
        [data-testid="stWidgetLabel"] p,
        [data-testid="stSelectbox"] label,
        [data-testid="stSlider"] label {{
            font-size: .98rem !important; font-weight: 650;
        }}
        [data-testid="stSidebar"] [data-testid="stRadio"] label {{
            font-size: 1.02rem !important; line-height: 1.5;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
            font-size: 1.18rem;
        }}
        [data-testid="stDataFrame"] * {{ font-size: .94rem; }}
        .section-kicker {{ font-size: .82rem; }}
        .section-title {{ font-size: 1.28rem; }}
        .section-note {{ font-size: .92rem; }}
        .hero h1 {{ font-size: clamp(1.8rem, 2.5vw, 2.35rem); }}
        .hero p {{ font-size: 1.04rem; line-height: 1.7; }}
        .hero-tag {{ font-size: .82rem; }}
        .kpi-label {{ font-size: .94rem; }}
        .kpi-value {{ font-size: 1.85rem; }}
        .kpi-foot {{ font-size: .86rem; }}
        .panel-title {{ font-size: 1.05rem; }}
        .panel-sub {{ font-size: .9rem; }}
        .insight {{ font-size: 1rem; line-height: 1.72; }}
        .method-banner {{ font-size: .9rem; line-height: 1.7; }}
        .method-banner b {{ font-size: .76rem; }}
        .footnote {{ font-size: .88rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_header(kicker: str, title: str, note: str = "") -> None:
    st.markdown(
        f"""<div class="section-head"><div><div class="section-kicker">{kicker}</div>
        <div class="section-title">{title}</div></div>
        <div class="section-note">{note}</div></div>""",
        unsafe_allow_html=True,
    )


def card(label: str, value: str, unit: str, foot: str, accent: str) -> str:
    return (
        f'<div class="kpi-card" style="border-top:3px solid {accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>'
        f'<div class="kpi-foot">{foot}</div></div>'
    )


def metric_columns(metric: str) -> tuple[str, str]:
    base = metric.removesuffix("_km")
    return f"{base}_median_km", f"{base}_p90_km"


def stable_farm_reference(farm_id: object) -> str:
    """Return a short, reproducible reference without exposing the long source ID."""
    digest = hashlib.blake2s(str(farm_id).encode("utf-8"), digest_size=5).hexdigest()
    return f"EXP-{digest.upper()}"


def display_locality(value: object) -> str:
    """Replace source placeholders by a human-readable missing-value label."""
    if pd.isna(value):
        return "Non renseignée"
    label = str(value).strip()
    if label.casefold() in {"", "nsp", "n/a", "na", "null", "none", "aucun", "néant", "neant"}:
        return "Non renseignée"
    return label


def build_commune_summary(
    frame: pd.DataFrame, metric: str, threshold: float, min_observations: int = 10
) -> pd.DataFrame:
    """Aggregate farm-to-facility distances to avoid ranking isolated records as territories."""
    keys = ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd"]
    grouped = (
        frame.groupby(keys, dropna=False)[metric]
        .agg(
            exploitations="count",
            median_km="median",
            p90_km=lambda values: values.quantile(0.90),
            maximum_km="max",
            beyond_count=lambda values: int(values.gt(threshold).sum()),
        )
        .reset_index()
    )
    grouped["beyond_pct"] = grouped["beyond_count"] / grouped["exploitations"] * 100
    for column in keys:
        grouped[column] = grouped[column].map(display_locality)
    grouped = grouped.loc[grouped.exploitations.ge(min_observations)].copy()
    return grouped.sort_values(
        ["p90_km", "median_km", "exploitations"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def make_map(map_data: pd.DataFrame, geojson: dict, median_col: str) -> object:
    fig = px.choropleth(
        map_data,
        geojson=geojson,
        locations="region_nom_bdd",
        featureidkey="properties.candidate_region_name",
        color=median_col,
        hover_name="region_nom_bdd",
        hover_data={
            "farm_count": ":,",
            median_col: ":.2f",
        },
        color_continuous_scale=["#F0D98B", "#E3A75D", "#D97757", "#A94738"],
        labels={median_col: "Médiane (km)", "farm_count": "Exploitations"},
    )
    fig.update_traces(marker_line_color="#FFFEFA", marker_line_width=2.2)
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        bgcolor=PALETTE["paper"],
        showframe=False,
    )
    fig.update_layout(
        height=440,
        margin={"l": 0, "r": 0, "t": 5, "b": 0},
        paper_bgcolor=PALETTE["paper"],
        plot_bgcolor=PALETTE["paper"],
        font={"family": "DM Sans, sans-serif", "color": PALETTE["ink"]},
        coloraxis_colorbar={
            "title": {"text": "km", "font": {"size": 11}},
            "thickness": 9,
            "len": 0.65,
            "outlinewidth": 0,
            "tickfont": {"size": 9},
        },
    )
    return fig


def make_regional_bar(summary: pd.DataFrame, median_col: str, selected_region: str) -> object:
    plot = summary.sort_values(median_col, ascending=True).copy()
    plot["focus"] = (
        plot["region_nom_bdd"].eq(selected_region)
        if selected_region != "Toutes les régions"
        else False
    )
    colors = [PALETTE["clay"] if focus else PALETTE["forest_light"] for focus in plot["focus"]]
    fig = px.bar(
        plot,
        x=median_col,
        y="region_nom_bdd",
        orientation="h",
        text=median_col,
        labels={median_col: "Distance médiane (km)", "region_nom_bdd": "Région"},
    )
    fig.update_traces(
        marker_color=colors,
        texttemplate="%{text:.2f} km",
        textposition="outside",
        cliponaxis=False,
        textfont={"size": 10, "color": PALETTE["ink"]},
        hovertemplate="%{y}<br>%{x:.2f} km<extra></extra>",
    )
    fig.update_layout(
        height=340,
        margin={"l": 4, "r": 48, "t": 5, "b": 25},
        paper_bgcolor=PALETTE["paper"],
        plot_bgcolor=PALETTE["paper"],
        font={"family": "DM Sans, sans-serif", "color": PALETTE["ink"], "size": 10},
        xaxis={"showgrid": True, "gridcolor": "#ECEAE2", "zeroline": False, "title": None},
        yaxis={"showgrid": False, "title": None, "tickfont": {"size": 10}},
        showlegend=False,
    )
    return fig


def render_dashboard_content(page_key: str) -> None:
    farms, summary, geojson, methodology = load_data()

    st.markdown(
        """<div class="hero">
        <div class="hero-top"><span class="hero-tag">TERROVIA · TOGO</span>
        <span class="hero-dot"></span><span class="hero-tag">DIAGNOSTIC TERRITORIAL AGRICOLE</span></div>
        <h1>Les exploitations agricoles sont-elles proches des services dont elles ont besoin ?</h1>
        <p>Explorez la proximité des petites exploitations recensées avec les marchés et les services de production. Repérez les territoires où les distances observées méritent une attention particulière.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="method-banner"><b>MESURE UTILISÉE</b> '
        "Les distances sont calculées en ligne droite, entre un point représentatif de chaque exploitation "
        "et l'équipement cartographié le plus proche. Elles ne représentent ni un trajet routier ni un temps de déplacement."
        "</div>",
        unsafe_allow_html=True,
    )

    if page_key == "overview":
        section_header(
            "Périmètre de l'étude",
            "Une vue simple du territoire agricole étudié",
            "Les données actuellement préparées dans TERROVIA",
        )
        k1, k2, k3 = st.columns(3, gap="medium")
        with k1:
            st.markdown(
                card(
                    "PETITES EXPLOITATIONS",
                    f"{len(farms):,}".replace(",", " "),
                    "",
                    "Entités incluses dans les calculs",
                    PALETTE["forest_light"],
                ),
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                card(
                    "RÉGIONS",
                    str(summary["region_nom_bdd"].nunique()),
                    "",
                    "Régions présentes dans les données",
                    PALETTE["gold"],
                ),
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                card(
                    "FAMILLES DE SERVICES",
                    str(len(METRICS)),
                    "",
                    "Étudiées séparément",
                    PALETTE["clay"],
                ),
                unsafe_allow_html=True,
            )

        section_header(
            "Constat national",
            "Les distances varient selon le service étudié",
            "Distance médiane entre les exploitations et l'équipement cartographié le plus proche",
        )
        feature_keys = {
            "Marchés": "market_features",
            "Magasins d'intrants": "input_store_features",
            "Coopératives": "cooperative_features",
            "ESOP": "esop_features",
            "Pépinières · points": "nursery_point_features",
            "Pépinières · surfaces": "nursery_other_polygon_features",
            "ZAAP / ZAPB": "zaap_zapb_polygon_features",
        }
        national_rows = []
        for label, (metric, _, _) in METRICS.items():
            distances = farms[metric].dropna()
            national_rows.append(
                {
                    "Service": label,
                    "Équipements recensés": int(methodology.get(feature_keys[label], 0)),
                    "Médiane (km)": float(distances.median()),
                    "P90 (km)": float(distances.quantile(0.90)),
                }
            )
        national = pd.DataFrame(national_rows).sort_values("Médiane (km)", ascending=True)
        with st.container(border=True):
            fig = px.bar(
                national,
                x="Médiane (km)",
                y="Service",
                orientation="h",
                text="Médiane (km)",
                labels={"Médiane (km)": "Distance médiane (km)", "Service": ""},
            )
            fig.update_traces(
                marker_color=PALETTE["forest_light"],
                texttemplate="%{text:.1f} km",
                textposition="outside",
                cliponaxis=False,
                textfont={"size": 12, "color": PALETTE["ink"]},
                hovertemplate="%{y}<br>Médiane : %{x:.2f} km<extra></extra>",
            )
            fig.update_layout(
                height=340,
                margin={"l": 5, "r": 55, "t": 8, "b": 25},
                paper_bgcolor=PALETTE["paper"],
                plot_bgcolor=PALETTE["paper"],
                font={"family": "DM Sans, sans-serif", "color": PALETTE["ink"], "size": 12},
                xaxis={"showgrid": True, "gridcolor": "#ECEAE2", "title": None},
                yaxis={"showgrid": False, "title": None},
                showlegend=False,
            )
            st.plotly_chart(
                fig, width="stretch", config={"displayModeBar": False, "responsive": True}
            )
        st.caption(
            "Les familles d'équipements rendent des services différents : ce graphique compare des distances, "
            "pas la qualité ni l'importance des services. Le nombre d'équipements recensés ne garantit pas leur fonctionnement."
        )
        with st.expander("Voir les valeurs détaillées"):
            st.dataframe(
                national.sort_values("Médiane (km)", ascending=False),
                width="stretch",
                hide_index=True,
                column_config={
                    "Médiane (km)": st.column_config.NumberColumn(format="%.2f km"),
                    "P90 (km)": st.column_config.NumberColumn(format="%.2f km"),
                },
            )

        market_median = float(farms["market_distance_km"].median())
        farthest_market_region = summary.sort_values(
            "market_distance_median_km", ascending=False
        ).iloc[0]
        section_header(
            "Un exemple concret",
            "La proximité des marchés varie d'une région à l'autre",
            "Lecture descriptive des résultats",
        )
        insight_cols = st.columns([1, 2], gap="medium")
        with insight_cols[0]:
            st.markdown(
                card(
                    "MÉDIANE NATIONALE · MARCHÉS",
                    f"{market_median:.2f}",
                    "km",
                    "Distance en ligne droite",
                    PALETTE["gold"],
                ),
                unsafe_allow_html=True,
            )
        with insight_cols[1]:
            st.markdown(
                f"""<div class="insight" style="height:100%">
                <strong>Observation :</strong> la région « {farthest_market_region["region_nom_bdd"]} »
                présente la distance médiane la plus élevée aux marchés parmi les cinq régions
                ({farthest_market_region["market_distance_median_km"]:.2f} km).
                <br><br><strong>Ce que cela signifie :</strong> cette région mérite une analyse plus approfondie.
                Ce résultat ne prouve pas que les producteurs sont privés d'accès à un marché.
                </div>""",
                unsafe_allow_html=True,
            )
        with st.expander("Voir le nombre d'exploitations recensées par région"):
            region_counts = (
                summary[["region_nom_bdd", "farm_count"]]
                .rename(
                    columns={
                        "region_nom_bdd": "Région",
                        "farm_count": "Petites exploitations",
                    }
                )
                .sort_values("Petites exploitations", ascending=False)
            )
            st.dataframe(region_counts, width="stretch", hide_index=True)
            st.caption(
                "Ces effectifs décrivent uniquement les entités du fichier analysé. "
                "Ils ne constituent pas une mesure de densité agricole."
            )

        st.info(
            "Pour examiner une région, choisir un service précis et repérer les communes à approfondir, "
            "choisissez « Explorer les territoires » dans le menu de navigation à gauche."
        )

    elif page_key == "explore":
        section_header(
            "Analyse ciblée",
            "Choisissez un territoire et un service",
            "Les filtres actualisent les indicateurs et la carte",
        )
        with st.container(border=True):
            filter_cols = st.columns([1, 1.2, 1], gap="medium")
            region_options = [
                "Toutes les régions",
                *sorted(farms.region_nom_bdd.dropna().unique()),
            ]
            with filter_cols[0]:
                selected_region = st.selectbox(
                    "Région",
                    region_options,
                    key="explore_region",
                )
            with filter_cols[1]:
                metric_label = st.selectbox(
                    "Service à examiner",
                    list(METRICS),
                    format_func=lambda label: {
                        "Pépinières · points": "Pépinières (points)",
                        "Pépinières · surfaces": "Pépinières (surfaces)",
                        "ZAAP / ZAPB": "ZAAP / ZAPB (couche combinée)",
                    }.get(label, label),
                    key="explore_metric",
                )
            metric, _, entity_label = METRICS[metric_label]
            national_distances = farms[metric].dropna()
            suggested_threshold = round(float(national_distances.quantile(0.75)), 1)
            threshold_max = max(1, ceil(float(national_distances.max())))
            with filter_cols[2]:
                threshold = st.slider(
                    "Repère de distance",
                    min_value=0.0,
                    max_value=float(threshold_max),
                    value=min(suggested_threshold, float(threshold_max)),
                    step=0.5,
                    format="%.1f km",
                    key=f"explore_threshold_{metric}",
                    help="Repère descriptif modifiable. Ce n'est pas une norme officielle.",
                )
            st.caption(
                f"Valeur initiale : {suggested_threshold:.1f} km, correspondant au 75e percentile national "
                "de cette catégorie. Ce repère peut être modifié."
            )

        filtered = farms
        if selected_region != "Toutes les régions":
            filtered = farms.loc[farms.region_nom_bdd.eq(selected_region)]
        filtered = filtered.copy()
        values = filtered[metric].dropna()
        if values.empty:
            st.warning("Aucune observation disponible pour cette sélection.")
            return

        median = float(values.median())
        p90 = float(values.quantile(0.90))
        over_count = int(values.gt(threshold).sum())
        over_pct = float(values.gt(threshold).mean() * 100)
        median_col, p90_col = metric_columns(metric)

        st.caption(
            f"{selected_region} · {len(filtered):,} petites exploitations analysées".replace(
                ",", " "
            )
        )
        k1, k2, k3 = st.columns(3, gap="medium")
        with k1:
            st.markdown(
                card(
                    "DISTANCE MÉDIANE",
                    f"{median:.2f}",
                    "km",
                    f"Vers le {entity_label} le plus proche",
                    PALETTE["gold"],
                ),
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                card(
                    "90 % DES DISTANCES",
                    f"{p90:.2f}",
                    "km",
                    "Ne dépassent pas cette valeur",
                    PALETTE["forest_light"],
                ),
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                card(
                    "AU-DELÀ DU REPÈRE",
                    f"{over_pct:.1f}",
                    "%",
                    f"{over_count:,} exploitations".replace(",", " "),
                    PALETTE["clay"],
                ),
                unsafe_allow_html=True,
            )

        national_median = float(farms[metric].median())
        if selected_region == "Toutes les régions":
            lead = (
                f"La médiane nationale est de {median:.2f} km. "
                "La carte permet de voir comment cette distance varie selon les régions."
            )
        else:
            difference = median - national_median
            direction = "supérieure" if difference > 0 else "inférieure"
            lead = (
                f"Dans la région « {selected_region} », la médiane est de {median:.2f} km, "
                f"soit {abs(difference):.2f} km {direction} à la médiane nationale "
                f"({national_median:.2f} km)."
            )
        st.markdown(
            f'<div class="insight"><strong>À retenir :</strong> {lead} '
            f"{over_pct:.1f} % des exploitations dépassent le repère de {threshold:.1f} km. "
            "Il s'agit d'un signal de proximité géographique, pas d'une mesure d'accès réel.</div>",
            unsafe_allow_html=True,
        )

        section_header(
            "Carte nationale",
            f"Distance aux {metric_label.lower()}",
            "La carte conserve les cinq régions pour garder le contexte national",
        )
        map_data = summary[["region_nom_bdd", "farm_count", median_col, p90_col]].copy()
        with st.container(border=True):
            st.plotly_chart(
                make_map(map_data, geojson, median_col),
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
            )

        with st.expander("Comparer les cinq régions en chiffres"):
            regional_stats = (
                summary[["region_nom_bdd", "farm_count", median_col, p90_col]]
                .copy()
                .rename(
                    columns={
                        "region_nom_bdd": "Région",
                        "farm_count": "Exploitations",
                        median_col: "Médiane (km)",
                        p90_col: "90 % à moins de (km)",
                    }
                )
                .sort_values("Médiane (km)", ascending=False)
            )
            st.dataframe(
                regional_stats,
                width="stretch",
                hide_index=True,
                column_config={
                    "Médiane (km)": st.column_config.NumberColumn(format="%.2f km"),
                    "90 % à moins de (km)": st.column_config.NumberColumn(format="%.2f km"),
                },
            )

        with st.expander("Quelles communes méritent une vérification ?"):
            commune_summary = build_commune_summary(filtered, metric, threshold)
            if commune_summary.empty:
                st.info(
                    "Aucune commune ne compte au moins 10 exploitations dans ce filtre. "
                    "Élargissez la sélection pour afficher un classement."
                )
            else:
                commune_display = commune_summary.head(20).rename(
                    columns={
                        "region_nom_bdd": "Région",
                        "prefecture_nom_bdd": "Préfecture",
                        "commune_nom_bdd": "Commune",
                        "exploitations": "Exploitations",
                        "median_km": "Médiane (km)",
                        "p90_km": "90 % à moins de (km)",
                        "maximum_km": "Maximum (km)",
                        "beyond_count": "Au-delà du repère",
                        "beyond_pct": "Part au-delà (%)",
                    }
                )
                top = commune_summary.iloc[0]
                st.markdown(
                    f'<div class="insight"><strong>Première commune du classement :</strong> '
                    f"{top['commune_nom_bdd']} ({top['prefecture_nom_bdd']}, {top['region_nom_bdd']}) "
                    f"présente un P90 de {top['p90_km']:.2f} km sur "
                    f"{int(top['exploitations'])} exploitations. Ce classement indique où "
                    "approfondir le diagnostic, pas automatiquement où investir.</div>",
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    commune_display,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Médiane (km)": st.column_config.NumberColumn(format="%.2f km"),
                        "90 % à moins de (km)": st.column_config.NumberColumn(format="%.2f km"),
                        "Maximum (km)": st.column_config.NumberColumn(format="%.2f km"),
                        "Part au-delà (%)": st.column_config.NumberColumn(format="%.1f %%"),
                    },
                )
                st.download_button(
                    "Télécharger le classement communal (CSV)",
                    data=commune_summary.to_csv(index=False).encode("utf-8"),
                    file_name="terrovia_communes_a_examiner.csv",
                    mime="text/csv",
                )

        with st.expander("Voir la distribution des distances"):
            hist = px.histogram(
                filtered,
                x=metric,
                nbins=32,
                labels={metric: "Distance (km)", "count": "Exploitations"},
            )
            hist.update_traces(
                marker_color=PALETTE["forest_light"],
                marker_line_color=PALETTE["paper"],
                marker_line_width=1,
            )
            hist.add_vline(
                x=threshold,
                line_dash="dash",
                line_color=PALETTE["clay"],
                annotation_text=f"Repère : {threshold:.1f} km",
                annotation_position="top right",
            )
            hist.update_layout(
                height=310,
                margin={"l": 5, "r": 20, "t": 25, "b": 35},
                paper_bgcolor=PALETTE["paper"],
                plot_bgcolor=PALETTE["paper"],
                font={"family": "DM Sans, sans-serif", "color": PALETTE["ink"], "size": 12},
                xaxis={"showgrid": False, "title": "Distance en ligne droite (km)"},
                yaxis={"showgrid": True, "gridcolor": "#ECEAE2", "title": "Exploitations"},
            )
            st.plotly_chart(
                hist, width="stretch", config={"displayModeBar": False, "responsive": True}
            )
            st.caption(
                "La ligne verticale représente le repère choisi. Les barres montrent le nombre "
                "d'exploitations dans chaque intervalle de distance."
            )

        with st.expander("Voir les 20 exploitations les plus éloignées"):
            nearest_name = metric.replace("_distance_km", "_nearest_name")
            individual = filtered.nlargest(20, metric).copy()
            individual["reference_exploitation"] = individual["farm_id"].map(stable_farm_reference)
            individual["localite_affichee"] = individual["nom_localite"].map(display_locality)
            table = individual[
                [
                    "reference_exploitation",
                    "region_nom_bdd",
                    "prefecture_nom_bdd",
                    "commune_nom_bdd",
                    "localite_affichee",
                    metric,
                    nearest_name,
                ]
            ].rename(
                columns={
                    "reference_exploitation": "Référence",
                    "region_nom_bdd": "Région",
                    "prefecture_nom_bdd": "Préfecture",
                    "commune_nom_bdd": "Commune",
                    "localite_affichee": "Localité",
                    metric: "Distance (km)",
                    nearest_name: "Équipement cartographié le plus proche",
                }
            )
            st.dataframe(
                table,
                width="stretch",
                hide_index=True,
                column_config={
                    "Référence": st.column_config.TextColumn(
                        help="Référence d'affichage, pas un identifiant administratif."
                    ),
                    "Distance (km)": st.column_config.NumberColumn(format="%.2f km"),
                },
            )
        export_filtered = filtered.copy()
        export_filtered["reference_exploitation"] = export_filtered["farm_id"].map(
            stable_farm_reference
        )
        export_filtered["localite_affichee"] = export_filtered["nom_localite"].map(display_locality)
        st.download_button(
            "Télécharger les exploitations filtrées (CSV)",
            data=export_filtered.to_csv(index=False).encode("utf-8"),
            file_name="terrovia_exploitations_filtrees.csv",
            mime="text/csv",
        )

    else:
        section_header(
            "Méthode",
            "Comment lire les chiffres ?",
            "Les définitions utiles pour interpréter les résultats",
        )
        st.subheader("Ce qui est mesuré")
        st.write(
            "Pour chaque petite exploitation cartographiée, TERROVIA calcule la distance "
            "en ligne droite jusqu'à l'équipement recensé le plus proche. Le calcul est répété "
            "séparément pour chaque famille de services."
        )
        st.subheader("Trois indicateurs")
        definition_cols = st.columns(3, gap="medium")
        with definition_cols[0]:
            st.markdown(
                "**Distance médiane**\n\nLa moitié des exploitations se trouve à cette distance ou moins."
            )
        with definition_cols[1]:
            st.markdown(
                "**90 % des distances**\n\nNeuf exploitations sur dix se trouvent à cette distance ou moins."
            )
        with definition_cols[2]:
            st.markdown(
                "**Part au-delà du repère**\n\nPourcentage d'exploitations dont la distance dépasse le curseur."
            )
        st.subheader("Étapes du calcul")
        st.markdown(
            "1. Préparer et contrôler les géométries des petites exploitations.\n"
            "2. Placer un point représentatif à l'intérieur de chaque exploitation.\n"
            "3. Calculer les distances vers la géométrie la plus proche de chaque service, en EPSG:32631.\n"
            "4. Résumer les distances par région et par commune."
        )
        st.subheader("Ce que les résultats ne disent pas")
        st.markdown(
            "- Ils ne mesurent pas la distance par route ni le temps de trajet.\n"
            "- Ils ne prennent pas en compte l'état des pistes, les saisons, les obstacles ou les modes de transport.\n"
            "- Ils ne confirment pas qu'un équipement est ouvert, opérationnel, approvisionné ou accessible à tous.\n"
            "- Le point représentatif d'une parcelle n'est pas forcément son entrée.\n"
            "- Les inventaires peuvent être incomplets ; la couche source regroupe ZAAP et ZAPB sans les distinguer."
        )
        st.subheader("Données utilisées")
        st.write(
            f"L'analyse porte sur {len(farms):,} petites exploitations préparées et sept familles d'équipements. "
            "Les sources brutes sont conservées séparément des données corrigées et des résultats.".replace(
                ",", " "
            )
        )
        st.caption(
            "Les seuils de 5 km et 10 km ainsi que le P75 utilisé comme valeur initiale du curseur "
            "sont des repères descriptifs, pas des normes officielles."
        )

    st.markdown(
        '<div class="footnote">TERROVIA · Relier les territoires agricoles aux opportunités.<br>'
        "Analyse exploratoire de proximité géographique · Sources et limites documentées dans le projet.</div>",
        unsafe_allow_html=True,
    )


def render_overview_page() -> None:
    render_dashboard_content("overview")


def render_explore_page() -> None:
    render_dashboard_content("explore")


def render_method_page() -> None:
    render_dashboard_content("method")


def main() -> None:
    st.set_page_config(
        page_title="TERROVIA | Accès aux services agricoles",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="auto",
    )
    inject_theme()

    with st.sidebar:
        st.markdown(
            '<div class="brand-lockup"><div class="brand-mark">T</div>'
            '<div><div class="brand-name">TERROVIA</div>'
            '<div class="brand-sub">Diagnostic territorial · Togo</div></div></div>',
            unsafe_allow_html=True,
        )

    pages = {
        "ESPACE DE TRAVAIL": [
            st.Page(
                render_overview_page,
                title="Vue d'ensemble",
                icon=":material/home:",
                default=True,
                help="Comprendre le périmètre de l'étude et les principaux constats nationaux.",
            ),
            st.Page(
                render_explore_page,
                title="Explorer les territoires",
                icon=":material/map:",
                url_path="explorer",
                help="Comparer les régions, examiner les services et repérer les territoires à approfondir.",
            ),
            st.Page(
                render_method_page,
                title="Méthode et limites",
                icon=":material/menu_book:",
                url_path="methode",
                help="Comprendre les données, les calculs et les précautions d'interprétation.",
            ),
        ]
    }
    current_page = st.navigation(pages, position="sidebar", expanded=True)

    with st.sidebar:
        st.divider()
        st.markdown(
            '<div class="side-footer"><strong>Relier les territoires agricoles aux opportunités.</strong><br>'
            "<span>Diagnostic géospatial · Togo</span></div>",
            unsafe_allow_html=True,
        )

    current_page.run()


if __name__ == "__main__":
    main()
