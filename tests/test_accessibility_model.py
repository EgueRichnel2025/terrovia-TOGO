"""Tests du pipeline de profils de proximité géographique."""

import numpy as np
import pandas as pd
import pytest

from scripts.train_accessibility_profiles import (
    FEATURES,
    build_pipeline,
    evaluate_candidates,
    load_modeling_data,
    select_model,
)


def test_pipeline_learns_three_stable_groups_on_synthetic_data() -> None:
    rng = np.random.default_rng(42)
    centers = np.array(
        [
            [1, 2, 0.5, 10, 2, 30, 3],
            [3, 4, 1, 35, 8, 5, 10],
            [2, 12, 1.2, 40, 3, 70, 4],
        ],
        dtype=float,
    )
    values = np.vstack(
        [np.maximum(0, rng.normal(center, 0.12, size=(120, 7))) for center in centers]
    )
    pipeline = build_pipeline(3)
    labels = pipeline.fit_predict(values)

    assert np.unique(labels).size == 3
    assert len(labels) == 360


def test_candidate_evaluation_returns_all_requested_cluster_counts() -> None:
    rng = np.random.default_rng(9)
    values = np.exp(rng.normal(size=(180, len(FEATURES)))) - 0.5
    values = np.maximum(values, 0)
    metrics, models = evaluate_candidates(values, max_clusters=4)

    assert metrics["nombre_profils"].tolist() == [2, 3, 4]
    assert set(models) == {2, 3, 4}
    assert metrics["stabilite_ari_moyenne"].between(0, 1).all()


def test_select_model_rejects_degenerate_or_unstable_solutions() -> None:
    metrics = pd.DataFrame(
        {
            "nombre_profils": [2, 3],
            "silhouette": [0.3, 0.4],
            "indice_davies_bouldin": [1.0, 0.8],
            "part_minimale_pct": [0.5, 0.8],
            "stabilite_ari_moyenne": [0.99, 0.65],
        }
    )
    with pytest.raises(RuntimeError, match="Aucun nombre de profils"):
        select_model(metrics)


def test_load_modeling_data_rejects_negative_distance(tmp_path) -> None:
    row = {"farm_id": "A", "region_nom_bdd": "Kara"}
    row.update({feature: 1.0 for feature in FEATURES})
    row[FEATURES[0]] = -1.0
    path = tmp_path / "farms.csv"
    pd.DataFrame([row]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="positives ou nulles"):
        load_modeling_data(path)
