"""Tests des fonctions de préparation du tableau de bord TERROVIA."""

from dashboard.app import (
    build_commune_summary,
    display_locality,
    load_profile_outputs,
    stable_farm_reference,
)


def test_stable_farm_reference_is_reproducible_and_short() -> None:
    first = stable_farm_reference("source-feature-001")
    second = stable_farm_reference("source-feature-001")

    assert first == second
    assert first.startswith("EXP-")
    assert len(first) == 14


def test_display_locality_handles_missing_placeholders() -> None:
    for value in (None, "", "   ", "Nsp", "N/A", "Néant", "Aucun"):
        assert display_locality(value) == "Non renseignée"

    assert display_locality("Avégbo") == "Avégbo"


def test_commune_summary_aggregates_and_excludes_small_groups() -> None:
    import pandas as pd

    frame = pd.DataFrame(
        {
            "region_nom_bdd": ["Savanes"] * 4 + ["Plateaux"] * 2,
            "prefecture_nom_bdd": ["Oti-Sud"] * 4 + ["Haho"] * 2,
            "commune_nom_bdd": ["Oti-Sud 1"] * 4 + ["Haho 3"] * 2,
            "market_distance_km": [2.0, 6.0, 10.0, 14.0, 30.0, 40.0],
        }
    )

    result = build_commune_summary(
        frame,
        metric="market_distance_km",
        threshold=5.0,
        min_observations=3,
    )

    assert len(result) == 1
    commune = result.iloc[0]
    assert commune["commune_nom_bdd"] == "Oti-Sud 1"
    assert commune["exploitations"] == 4
    assert commune["median_km"] == 8.0
    assert commune["p90_km"] == 12.8
    assert commune["beyond_count"] == 3
    assert commune["beyond_pct"] == 75.0


def test_commune_summary_sorts_highest_p90_first() -> None:
    import pandas as pd

    frame = pd.DataFrame(
        {
            "region_nom_bdd": ["A"] * 3 + ["B"] * 3,
            "prefecture_nom_bdd": ["P1"] * 3 + ["P2"] * 3,
            "commune_nom_bdd": ["Commune 1"] * 3 + ["Commune 2"] * 3,
            "market_distance_km": [1.0, 2.0, 3.0, 10.0, 20.0, 30.0],
        }
    )

    result = build_commune_summary(frame, "market_distance_km", 5.0, 3)

    assert result["commune_nom_bdd"].tolist() == ["Commune 2", "Commune 1"]


def test_profile_outputs_are_aggregate_and_cover_all_regions() -> None:
    profiles, regional, metadata = load_profile_outputs()

    assert metadata["nombre_profils_retenu"] == 3
    assert profiles["nombre_exploitations"].sum() == 13_076
    assert set(regional["region_nom_bdd"]) == {
        "Centrale",
        "Kara",
        "Maritime",
        "Plateaux",
        "Savanes",
    }
    assert regional["part_dans_region_pct"].between(0, 100).all()
