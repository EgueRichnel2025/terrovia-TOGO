"""Entraînement reproductible de profils de proximité des exploitations agricoles.

Le modèle est non supervisé : il regroupe les exploitations selon les sept distances
géométriques disponibles. Il n'apprend pas l'accès réel et ne prédit aucun résultat.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, RobustScaler

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/processed/accessibility/small_farms_potential_accessibility.csv"
DEFAULT_OUTPUT = ROOT / "data/processed/accessibility/model"

FEATURE_LABELS = {
    "market_distance_km": "Marchés",
    "input_store_distance_km": "Magasins d'intrants",
    "cooperative_distance_km": "Coopératives",
    "esop_distance_km": "ESOP",
    "nursery_distance_km": "Pépinières ponctuelles",
    "nursery_other_distance_km": "Pépinières surfaciques",
    "zaap_zapb_distance_km": "ZAAP / ZAPB",
}
FEATURES = list(FEATURE_LABELS)
STABILITY_SEEDS = (7, 21, 84)


def build_pipeline(n_clusters: int, random_state: int = 42) -> Pipeline:
    """Log-transform, robust-scale and cluster the seven distance indicators."""
    return Pipeline(
        steps=[
            ("logarithme", FunctionTransformer(np.log1p, validate=True)),
            ("centrage_robuste", RobustScaler()),
            (
                "kmeans",
                KMeans(
                    n_clusters=n_clusters,
                    random_state=random_state,
                    n_init=30,
                    max_iter=500,
                    algorithm="lloyd",
                ),
            ),
        ]
    )


def load_modeling_data(path: Path) -> tuple[pd.DataFrame, np.ndarray]:
    """Load only the fields required for modeling and validate their integrity."""
    required = ["farm_id", "region_nom_bdd", *FEATURES]
    frame = pd.read_csv(path, usecols=required)
    if frame.empty:
        raise ValueError("Le fichier ne contient aucune exploitation.")
    if frame["farm_id"].isna().any() or frame["farm_id"].duplicated().any():
        raise ValueError("Les références d'exploitation sont manquantes ou dupliquées.")
    if frame["region_nom_bdd"].isna().any():
        raise ValueError("Certaines exploitations n'ont pas de région renseignée.")

    distances = frame[FEATURES].apply(pd.to_numeric, errors="coerce")
    values = distances.to_numpy(dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError("Les distances contiennent des valeurs manquantes ou non finies.")
    if (values < 0).any():
        raise ValueError("Les distances doivent être positives ou nulles.")
    if np.unique(values, axis=0).shape[0] < 9:
        raise ValueError("La diversité des profils est insuffisante pour tester plusieurs groupes.")
    frame.loc[:, FEATURES] = values
    return frame, values


def evaluate_candidates(
    raw_distances: np.ndarray,
    max_clusters: int = 8,
    random_state: int = 42,
    silhouette_sample_size: int = 3500,
) -> tuple[pd.DataFrame, dict[int, Pipeline]]:
    """Compare candidate KMeans models using separation, compactness and stability."""
    upper = min(max_clusters, len(raw_distances) - 1)
    if upper < 2:
        raise ValueError("Il faut au moins trois exploitations pour évaluer un clustering.")

    rows: list[dict[str, float | int]] = []
    models: dict[int, Pipeline] = {}
    sample_size = min(silhouette_sample_size, len(raw_distances))

    for k in range(2, upper + 1):
        pipeline = build_pipeline(k, random_state)
        labels = pipeline.fit_predict(raw_distances)
        if np.unique(labels).size != k:
            continue
        transformed = pipeline[:-1].transform(raw_distances)

        silhouettes = silhouette_score(
            transformed,
            labels,
            sample_size=sample_size,
            random_state=random_state,
        )
        db_index = davies_bouldin_score(transformed, labels)
        ch_index = calinski_harabasz_score(transformed, labels)
        counts = np.bincount(labels, minlength=k)
        min_share = float(counts.min() / counts.sum() * 100)

        ari_values = []
        for seed in STABILITY_SEEDS:
            alternate = build_pipeline(k, seed)
            alternate_labels = alternate.fit_predict(raw_distances)
            ari_values.append(adjusted_rand_score(labels, alternate_labels))

        rows.append(
            {
                "nombre_profils": k,
                "silhouette": float(silhouettes),
                "indice_davies_bouldin": float(db_index),
                "indice_calinski_harabasz": float(ch_index),
                "part_minimale_pct": min_share,
                "stabilite_ari_moyenne": float(np.mean(ari_values)),
                "inertie": float(pipeline.named_steps["kmeans"].inertia_),
            }
        )
        models[k] = pipeline

    metrics = pd.DataFrame(rows)
    if metrics.empty:
        raise RuntimeError("Aucun modèle candidat n'a pu être entraîné.")
    return metrics, models


def select_model(metrics: pd.DataFrame) -> int:
    """Prefer robust, non-degenerate solutions; do not force tiny or unstable groups."""
    eligible = metrics.loc[
        metrics["part_minimale_pct"].ge(1.0) & metrics["stabilite_ari_moyenne"].ge(0.70)
    ].copy()
    if eligible.empty:
        raise RuntimeError(
            "Aucun nombre de profils ne satisfait les critères minimaux de taille "
            "des groupes (1 %) et de stabilité (ARI 0,70). Le clustering n'est pas "
            "retenu comme segmentation suffisamment robuste."
        )

    # Le score silhouette privilégie la séparation ; Davies-Bouldin départage les solutions proches.
    eligible = eligible.sort_values(
        ["silhouette", "indice_davies_bouldin", "nombre_profils"],
        ascending=[False, True, True],
    )
    return int(eligible.iloc[0]["nombre_profils"])


def build_outputs(
    frame: pd.DataFrame,
    raw_distances: np.ndarray,
    metrics: pd.DataFrame,
    pipeline: Pipeline,
    selected_k: int,
    output_dir: Path,
    random_state: int,
) -> dict:
    """Create model artefacts and privacy-safe aggregate tables."""
    original_labels = pipeline.predict(raw_distances)

    # Les numéros de profil suivent l'ordre croissant de la moyenne des sept médianes
    # normalisées par leur médiane nationale. Ce tri ne constitue pas un indice composite.
    medians_by_cluster = (
        pd.DataFrame(raw_distances, columns=FEATURES)
        .assign(cluster=original_labels)
        .groupby("cluster")[FEATURES]
        .median()
    )
    national_medians = pd.Series(np.median(raw_distances, axis=0), index=FEATURES).replace(
        0, np.nan
    )
    relative_medians = medians_by_cluster.div(national_medians, axis=1)
    order = relative_medians.mean(axis=1).sort_values().index.tolist()
    label_map = {int(old): position + 1 for position, old in enumerate(order)}
    profile_ids = np.array([label_map[int(label)] for label in original_labels])

    assignment = pd.DataFrame(
        {
            "farm_id": frame["farm_id"].astype(str),
            "cluster_id": profile_ids,
            "profil": [f"Profil {number}" for number in profile_ids],
        }
    )
    assignments_path = output_dir / "affectations_exploitations_locales.csv"
    assignment.to_csv(assignments_path, index=False)

    profiled = pd.DataFrame(raw_distances, columns=FEATURES)
    profiled["cluster_id"] = profile_ids
    profile_rows = []
    for profile_id, group in profiled.groupby("cluster_id", sort=True):
        row: dict[str, float | int | str] = {
            "cluster_id": int(profile_id),
            "profil": f"Profil {profile_id}",
            "nombre_exploitations": int(len(group)),
            "part_nationale_pct": float(len(group) / len(profiled) * 100),
        }
        for feature in FEATURES:
            row[f"{feature}_mediane_km"] = float(group[feature].median())
            row[f"{feature}_p90_km"] = float(group[feature].quantile(0.90))
        profile_rows.append(row)
    profiles = pd.DataFrame(profile_rows)
    profiles_path = output_dir / "profils_accessibilite.csv"
    profiles.to_csv(profiles_path, index=False, float_format="%.4f")

    regional = frame[["region_nom_bdd"]].copy()
    regional["cluster_id"] = profile_ids
    counts = (
        regional.groupby(["region_nom_bdd", "cluster_id"])
        .size()
        .rename("nombre_exploitations")
        .reset_index()
    )
    totals = regional.groupby("region_nom_bdd").size().rename("total_region")
    counts = counts.join(totals, on="region_nom_bdd")
    counts["part_dans_region_pct"] = counts["nombre_exploitations"] / counts["total_region"] * 100
    counts["profil"] = counts["cluster_id"].map(lambda value: f"Profil {value}")
    regional_path = output_dir / "repartition_regionale_profils.csv"
    counts.to_csv(regional_path, index=False, float_format="%.4f")

    selected_metrics = metrics.loc[metrics["nombre_profils"].eq(selected_k)].iloc[0]
    silhouette = float(selected_metrics["silhouette"])
    stability = float(selected_metrics["stabilite_ari_moyenne"])
    quality = (
        "Structure exploratoire nette"
        if silhouette >= 0.25 and stability >= 0.85
        else "Structure exploratoire modérée"
        if silhouette >= 0.15 and stability >= 0.75
        else "Structure exploratoire faible"
    )

    metadata = {
        "date_entrainement": date.today().isoformat(),
        "modele": "K-Means",
        "version_scikit_learn": __import__("sklearn").__version__,
        "nombre_exploitations": int(len(frame)),
        "nombre_variables": len(FEATURES),
        "variables": [{"colonne": key, "libelle": value} for key, value in FEATURE_LABELS.items()],
        "transformation": "log1p, puis RobustScaler (médiane et intervalle interquartile)",
        "nombre_profils_retenu": selected_k,
        "random_state": random_state,
        "initialisations_kmeans": 30,
        "echantillon_silhouette": min(3500, len(frame)),
        "silhouette": silhouette,
        "davies_bouldin": float(selected_metrics["indice_davies_bouldin"]),
        "calinski_harabasz": float(selected_metrics["indice_calinski_harabasz"]),
        "stabilite_ari_moyenne": stability,
        "part_minimale_pct": float(selected_metrics["part_minimale_pct"]),
        "qualite_structure": quality,
        "correspondance_cluster_profil": {str(key): value for key, value in label_map.items()},
        "limites": [
            "Apprentissage non supervisé sans variable cible ni vérité terrain.",
            "Les profils décrivent uniquement les sept distances euclidiennes cartographiées.",
            "La segmentation ne mesure ni itinéraire routier, ni durée, ni coût, "
            "ni accès effectif.",
            "Le modèle ne prédit pas la disponibilité, l'utilisation ou la qualité d'un service.",
            "Le tri des profils sert uniquement à faciliter la lecture et ne constitue "
            "pas un indice composite.",
            "Les affectations individuelles demeurent dans les fichiers locaux non versionnés.",
        ],
    }
    metadata_path = output_dir / "metadonnees_modele.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    joblib_path = output_dir / "modele_kmeans_accessibilite.joblib"
    joblib.dump(
        {
            "pipeline": pipeline,
            "colonnes": FEATURES,
            "correspondance_cluster_profil": label_map,
        },
        joblib_path,
    )

    metrics_path = output_dir / "evaluation_candidats.csv"
    metrics.to_csv(metrics_path, index=False, float_format="%.6f")

    return {
        "metadata": metadata,
        "profiles_path": profiles_path,
        "regional_path": regional_path,
        "metrics_path": metrics_path,
        "assignments_path": assignments_path,
        "model_path": joblib_path,
    }


def write_report(
    metadata: dict,
    metrics: pd.DataFrame,
    profiles_path: Path,
    regional_path: Path,
    output_dir: Path,
) -> Path:
    """Write a French, aggregate-only report with no individual farm information."""
    profiles = pd.read_csv(profiles_path)
    regional = pd.read_csv(regional_path)
    metric_table = metrics.rename(
        columns={
            "nombre_profils": "Profils",
            "silhouette": "Silhouette",
            "indice_davies_bouldin": "Davies-Bouldin",
            "indice_calinski_harabasz": "Calinski-Harabasz",
            "part_minimale_pct": "Part minimale (%)",
            "stabilite_ari_moyenne": "Stabilité ARI moyenne",
            "inertie": "Inertie",
        }
    ).to_markdown(index=False, floatfmt=".3f")
    profile_columns = {
        "cluster_id": "Numéro",
        "profil": "Profil",
        "nombre_exploitations": "Exploitations",
        "part_nationale_pct": "Part nationale (%)",
    }
    for feature, label in FEATURE_LABELS.items():
        profile_columns[f"{feature}_mediane_km"] = f"{label} · médiane (km)"
        profile_columns[f"{feature}_p90_km"] = f"{label} · P90 (km)"
    profile_table = profiles.rename(columns=profile_columns).to_markdown(
        index=False, floatfmt=".2f"
    )
    regional_pivot = regional.pivot(
        index="region_nom_bdd", columns="profil", values="part_dans_region_pct"
    ).fillna(0)
    regional_table = regional_pivot.to_markdown(floatfmt=".1f")
    text = f"""# Profils de proximité géographique — TERROVIA

Date d'entraînement : {metadata["date_entrainement"]}

## Objectif

Un modèle K-Means non supervisé a été entraîné sur les sept distances séparant les
13 076 petites exploitations préparées des familles d'équipements cartographiées.
L'objectif est d'identifier des profils de proximité similaires, et non de prédire
l'accès réel aux services.

## Préparation des variables

Les sept distances en kilomètres sont transformées par `log1p`, puis mises à
l'échelle avec `RobustScaler`. Cette préparation limite l'influence de distributions
très asymétriques et des écarts de dispersion entre les familles d'équipements.

## Comparaison des modèles

{metric_table}

La silhouette mesure la cohésion et la séparation des groupes (plus elle est élevée,
mieux c'est). L'indice de Davies-Bouldin est préférable lorsqu'il est plus faible ;
l'indice de Calinski-Harabasz lorsqu'il est plus élevé. La stabilité est évaluée par
l'indice ARI entre plusieurs initialisations. Ces critères décrivent la structure des
données, pas une précision prédictive.

## Modèle retenu

- Algorithme : K-Means.
- Nombre de profils : {metadata["nombre_profils_retenu"]}.
- Silhouette : {metadata["silhouette"]:.3f}.
- Davies-Bouldin : {metadata["davies_bouldin"]:.3f}.
- Calinski-Harabasz : {metadata["calinski_harabasz"]:.1f}.
- Stabilité ARI moyenne : {metadata["stabilite_ari_moyenne"]:.3f}.
- Taille du plus petit profil : {metadata["part_minimale_pct"]:.2f} %.
- Appréciation : **{metadata["qualite_structure"]}**.

## Résumé des profils

{profile_table}

Les numéros de profil sont ordonnés selon les médianes relatives des distances afin
de faciliter la lecture. Ils ne constituent ni score synthétique, ni classement de
performance ou d'investissement.

## Répartition régionale

Part de chaque profil au sein de chaque région (en %) :

{regional_table}

Cette répartition décrit la composition des groupes dans les données préparées.
Elle ne mesure pas la qualité des services ni l'accès effectif.

## Limites d'interprétation

- Il n'existe pas de variable cible ni d'étiquettes de référence : aucune précision
  supervisée ne peut être annoncée.
- Les groupes sont exploratoires et dépendent des données cartographiées.
- Les distances sont euclidiennes, en ligne droite, et ne représentent pas un trajet.
- Le modèle ne connaît ni l'état des routes, ni les horaires, les prix, les stocks,
  la capacité, le statut opérationnel ou l'utilisation réelle des équipements.
- La présence d'un groupe dans une région ne suffit pas à conclure à une privation
  d'accès ou à justifier une implantation.

## Protection des données

Seules des synthèses par profil et région figurent dans ce rapport. Les affectations
individuelles et le fichier du modèle sont conservés dans `data/processed/`, exclu
du dépôt public.
"""
    report_path = output_dir / "RAPPORT_PROFILS_ACCESSIBILITE.md"
    report_path.write_text(text, encoding="utf-8")
    return report_path


def train(
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT,
    max_clusters: int = 8,
    random_state: int = 42,
) -> dict:
    """Run the complete training, selection, export and reporting workflow."""
    frame, raw_distances = load_modeling_data(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics, models = evaluate_candidates(
        raw_distances, max_clusters=max_clusters, random_state=random_state
    )
    selected_k = select_model(metrics)
    selected_pipeline = models[selected_k]
    # Refit the selected pipeline on the untouched full matrix using the declared seed.
    selected_pipeline = build_pipeline(selected_k, random_state)
    selected_pipeline.fit(raw_distances)

    outputs = build_outputs(
        frame,
        raw_distances,
        metrics,
        selected_pipeline,
        selected_k,
        output_dir,
        random_state,
    )
    outputs["report_path"] = write_report(
        outputs["metadata"],
        metrics,
        outputs["profiles_path"],
        outputs["regional_path"],
        output_dir,
    )
    print("\nÉVALUATION DES MODÈLES CANDIDATS")
    print(metrics.round(3).to_string(index=False))
    print("\nPROFILS RETENUS")
    print(pd.read_csv(outputs["profiles_path"]).round(2).to_string(index=False))
    print("\nRÉPARTITION RÉGIONALE")
    print(pd.read_csv(outputs["regional_path"]).round(2).to_string(index=False))
    print("\nMODÈLE RETENU")
    print(json.dumps(outputs["metadata"], ensure_ascii=False, indent=2))
    print("\nFICHIERS PRODUITS")
    for key, value in outputs.items():
        print(f"- {key}: {value}")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-clusters", type=int, default=8)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()
    train(args.input, args.output, args.max_clusters, args.random_state)


if __name__ == "__main__":
    main()
