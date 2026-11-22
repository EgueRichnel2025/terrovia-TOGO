"""Tests du mode de démonstration agrégé TERROVIA."""

from pathlib import Path

import pytest

from dashboard.aggregate_preview import (
    SERVICE_COLUMNS,
    build_national_summary,
    build_regional_view,
    load_aggregate_data,
    translate_limitations,
    validate_aggregate_frames,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data/processed/accessibility"


def test_local_aggregate_files_are_valid_and_cover_all_regions() -> None:
    overall, regional, methodology = load_aggregate_data(DATA_DIR)

    assert len(overall) == 7
    assert set(regional["region_nom_bdd"]) == {
        "Centrale",
        "Kara",
        "Maritime",
        "Plateaux",
        "Savanes",
    }
    assert int(regional["farm_count"].sum()) == 13_076
    assert int(methodology["farm_features"]) == 13_076


def test_national_summary_has_seven_service_families() -> None:
    overall, _, methodology = load_aggregate_data(DATA_DIR)

    result = build_national_summary(overall, methodology)

    assert len(result) == 7
    assert set(result["Service"]) == set(SERVICE_COLUMNS)
    market = result.loc[result["Service"].eq("Marchés")].iloc[0]
    assert market["Médiane (km)"] == pytest.approx(2.3442, abs=0.001)
    assert market["À plus de 5 km (%)"] == pytest.approx(12.7256, abs=0.001)


def test_regional_view_returns_only_selected_region_and_valid_repere() -> None:
    _, regional, _ = load_aggregate_data(DATA_DIR)

    result = build_regional_view(regional, "Magasins d'intrants", 10)
    savanes = result.loc[result["Région"].eq("Savanes")].iloc[0]

    assert len(result) == 5
    assert savanes["Médiane (km)"] == pytest.approx(8.5375, abs=0.001)
    assert savanes["Part au-delà du repère (%)"] == pytest.approx(43.2673, abs=0.001)
    with pytest.raises(ValueError):
        build_regional_view(regional, "Magasins d'intrants", 7)


def test_validation_rejects_missing_region() -> None:
    overall, regional, methodology = load_aggregate_data(DATA_DIR)
    incomplete = regional.loc[regional["region_nom_bdd"] != "Savanes"]

    with pytest.raises(ValueError, match="cinq régions"):
        validate_aggregate_frames(overall, incomplete, methodology)


def test_limitations_are_translated_to_french_and_unknown_values_fail() -> None:
    translated = translate_limitations(
        ["No road-network route distance or travel time is estimated."]
    )
    assert translated == [
        "L'étude ne calcule ni distance par le réseau routier ni durée de déplacement."
    ]
    with pytest.raises(ValueError, match="traduction française"):
        translate_limitations(["New limitation in English."])
