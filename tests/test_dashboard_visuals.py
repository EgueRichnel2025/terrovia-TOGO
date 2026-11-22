"""Tests des composants visuels du tableau de bord TERROVIA."""

import pandas as pd

from dashboard.app import PALETTE, make_regional_bar


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
