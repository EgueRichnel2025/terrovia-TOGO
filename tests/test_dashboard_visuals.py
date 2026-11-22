"""Tests des composants visuels du tableau de bord TERROVIA."""

import pandas as pd

from dashboard.app import PALETTE, format_fr_number, make_regional_bar, resolve_data_directory


def test_regional_comparison_orders_values_and_highlights_selected_region() -> None:
    summary = pd.DataFrame(
        {
            "region_nom_bdd": ["Centrale", "Kara", "Maritime", "Plateaux", "Savanes"],
            "market_distance_median_km": [2.23, 1.74, 2.52, 3.42, 2.11],
        }
    )

    figure = make_regional_bar(
        summary,
        "market_distance_median_km",
        "Plateaux",
    )

    assert list(figure.data[0].y) == ["Kara", "Savanes", "Centrale", "Maritime", "Plateaux"]
    assert list(figure.data[0].marker.color) == [
        PALETTE["forest_light"],
        PALETTE["forest_light"],
        PALETTE["forest_light"],
        PALETTE["forest_light"],
        PALETTE["clay"],
    ]
    assert figure.layout.height == 340


def test_regional_comparison_uses_only_the_three_brand_colors_without_filter() -> None:
    summary = pd.DataFrame(
        {
            "region_nom_bdd": ["Centrale", "Kara", "Maritime", "Plateaux", "Savanes"],
            "market_distance_median_km": [2.23, 1.74, 2.52, 3.42, 2.11],
        }
    )

    figure = make_regional_bar(summary, "market_distance_median_km", "Toutes les régions")

    assert set(figure.data[0].marker.color) == {PALETTE["forest_light"]}
    assert figure.layout.showlegend is False


def test_regional_comparison_axis_displays_lowest_value_at_top() -> None:
    summary = pd.DataFrame(
        {
            "region_nom_bdd": ["Centrale", "Kara", "Maritime", "Plateaux", "Savanes"],
            "market_distance_median_km": [2.23, 1.74, 2.52, 3.42, 2.11],
        }
    )

    figure = make_regional_bar(summary, "market_distance_median_km", "Toutes les régions")

    assert list(figure.layout.yaxis.categoryarray) == [
        "Kara",
        "Savanes",
        "Centrale",
        "Maritime",
        "Plateaux",
    ]
    assert figure.layout.yaxis.autorange == "reversed"


def test_french_number_format_uses_narrow_grouping_and_decimal_comma() -> None:
    assert format_fr_number(13_076) == "13\u202f076"
    assert format_fr_number(3.42, 2) == "3,42"
    assert format_fr_number(43.267, 1) == "43,3"


def test_public_data_is_selected_when_private_farm_files_are_absent(tmp_path) -> None:
    local = tmp_path / "data/processed/accessibility"
    public = tmp_path / "data/public/accessibility"
    local.mkdir(parents=True)
    public.mkdir(parents=True)
    (public / "overall_accessibility_summary.csv").write_text("indicator\n", encoding="utf-8")

    assert resolve_data_directory(tmp_path) == public


def test_full_local_data_takes_precedence_over_public_aggregates(tmp_path) -> None:
    local = tmp_path / "data/processed/accessibility"
    public = tmp_path / "data/public/accessibility"
    local.mkdir(parents=True)
    public.mkdir(parents=True)
    (local / "small_farms_potential_accessibility.csv").touch()
    (local / "regions_accessibility.geojson").touch()
    (public / "overall_accessibility_summary.csv").write_text("indicator\n", encoding="utf-8")

    assert resolve_data_directory(tmp_path) == local
