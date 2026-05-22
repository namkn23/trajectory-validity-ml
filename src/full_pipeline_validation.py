from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
from PIL import Image


REPORT_PATH = Path("results/reports/g5_final_validation_report.txt")


EXPECTED_TABLE_SHAPES = {
    "results/tables/xdatcar_audit.csv": (1, 9),
    "results/tables/na_coordinates.csv": (188592, 5),
    "results/tables/na_periodic_steps.csv": (188544, 7),
    "results/tables/suspicious_jumps.csv": (149, 7),
    "results/tables/displacement_features.csv": (48, 5),
    "results/tables/step_features.csv": (48, 4),
    "results/tables/mobility_spread_features.csv": (6, 7),
    "results/tables/atom_features.csv": (48, 8),
    "results/tables/frame_features.csv": (3928, 4),
    "results/tables/ml_input_scaled.csv": (48, 8),
    "results/tables/pca_embeddings.csv": (48, 3),
    "results/tables/pca_explained_variance.csv": (2, 2),
    "results/tables/anomaly_scores.csv": (48, 3),
    "results/tables/anomaly_score_ranking.csv": (48, 4),
    "results/tables/flagged_anomalies.csv": (5, 4),
}


EXPECTED_PLOTS = [
    "results/plots/msd_by_na_atom.png",
    "results/plots/mean_displacement_by_na_atom.png",
    "results/plots/max_displacement_by_na_atom.png",
    "results/plots/step_magnitude_histogram.png",
    "results/plots/atom_msd_histogram.png",
    "results/plots/atom_mean_step_histogram.png",
    "results/plots/pca_embedding_scatter.png",
    "results/plots/anomaly_score_distribution.png",
    "results/plots/pca_anomaly_overlay.png",
]


EXPECTED_DOCS = [
    "README.md",
    "docs/methodology.md",
    "requirements.txt",
    "run_pipeline.py",
]


# NOTE: create_* helper scripts intentionally not required here.
# The docs/README/requirements should exist as normal repo files.
EXPECTED_CORE_SCRIPTS = [
    "src/audit_xdatcar_structure.py",
    "src/test_audit_rerun.py",
    "src/extract_na_coordinates.py",
    "src/validate_na_coordinates.py",
    "src/test_na_extraction_rerun.py",
    "src/compute_periodic_boundary_steps.py",
    "src/validate_step_statistics.py",
    "src/detect_suspicious_jumps.py",
    "src/test_step_pipeline_rerun.py",
    "src/compute_displacement_features.py",
    "src/compute_step_features.py",
    "src/compute_mobility_spread_features.py",
    "src/assemble_feature_tables.py",
    "src/validate_feature_tables.py",
    "src/test_feature_pipeline_rerun.py",
    "src/generate_msd_plot.py",
    "src/generate_displacement_plots.py",
    "src/generate_histograms.py",
    "src/validate_generated_plots.py",
    "src/prepare_ml_input.py",
    "src/validate_ml_input.py",
    "src/run_pca.py",
    "src/validate_pca.py",
    "src/generate_pca_plots.py",
    "src/run_isolation_forest.py",
    "src/validate_anomaly_scores.py",
    "src/generate_anomaly_tables.py",
    "src/generate_anomaly_plots.py",
]


def require_existing_nonempty(path: str, failures: list[str]) -> None:
    p = Path(path)

    if not p.exists():
        failures.append(f"Missing file: {path}")
        return

    if p.stat().st_size == 0:
        failures.append(f"Empty file: {path}")


def validate_plot(path: str, failures: list[str]) -> None:
    p = Path(path)

    require_existing_nonempty(path, failures)

    if not p.exists() or p.stat().st_size == 0:
        return

    try:
        # verify() consumes the image object, so reopen for dimensions
        with Image.open(p) as image:
            image.verify()

        with Image.open(p) as image:
            width, height = image.size

        if width <= 0 or height <= 0:
            failures.append(f"Invalid plot dimensions: {path}")

    except Exception as exc:
        failures.append(f"Unreadable plot {path}: {exc}")


def validate_expected_files(failures: list[str]) -> None:
    for directory in [
        "data",
        "src",
        "results/tables",
        "results/plots",
        "results/reports",
        "docs",
    ]:
        if not Path(directory).exists():
            failures.append(f"Missing directory: {directory}")

    for path in EXPECTED_DOCS + EXPECTED_CORE_SCRIPTS:
        require_existing_nonempty(path, failures)


def validate_table_shapes(failures: list[str]) -> None:
    for path, expected_shape in EXPECTED_TABLE_SHAPES.items():
        require_existing_nonempty(path, failures)

        p = Path(path)
        if not p.exists() or p.stat().st_size == 0:
            continue

        table = pd.read_csv(p)

        if table.shape != expected_shape:
            failures.append(
                f"Unexpected shape for {path}: {table.shape} != {expected_shape}"
            )


def validate_core_tables(failures: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.DataFrame]:
    na = pd.read_csv("results/tables/na_coordinates.csv")
    steps = pd.read_csv("results/tables/na_periodic_steps.csv")
    ml = pd.read_csv("results/tables/ml_input_scaled.csv")
    pca_variance = pd.read_csv("results/tables/pca_explained_variance.csv")
    scores = pd.read_csv("results/tables/anomaly_scores.csv")
    ranking = pd.read_csv("results/tables/anomaly_score_ranking.csv")
    flagged = pd.read_csv("results/tables/flagged_anomalies.csv")

    if not np.isfinite(na[["x", "y", "z"]].to_numpy()).all():
        failures.append("Na coordinate table contains non-finite values.")

    in_unit_cell = ((na[["x", "y", "z"]] >= 0) & (na[["x", "y", "z"]] < 1))
    if not in_unit_cell.all().all():
        failures.append("Na fractional coordinates are outside [0, 1).")

    na_per_frame = na.groupby("frame").size()
    if na_per_frame.min() != 48 or na_per_frame.max() != 48:
        failures.append(
            "Na coordinate table does not contain exactly 48 Na atoms per frame."
        )

    if not (steps["to_frame"] == steps["from_frame"] + 1).all():
        failures.append("Step table frame continuity failed.")

    step_cols = ["dx_frac", "dy_frac", "dz_frac", "step_frac"]
    if not np.isfinite(steps[step_cols].to_numpy()).all():
        failures.append("Step table contains non-finite values.")

    if (steps["step_frac"] < 0).any():
        failures.append("Step table contains negative step magnitudes.")

    if steps["step_frac"].max() > 0.25:
        failures.append("Step table contains teleportation-scale jumps.")

    numeric_ml = ml.drop(columns=["na_index"])

    if not np.isfinite(numeric_ml.to_numpy()).all():
        failures.append("ML input contains non-finite values.")

    if numeric_ml.mean().abs().max() > 1e-12:
        failures.append("Scaled ML input means are not close to zero.")

    if (numeric_ml.std(ddof=0) - 1).abs().max() > 1e-12:
        failures.append("Scaled ML input population stds are not close to one.")

    variance_values = pca_variance["explained_variance_ratio"]

    if not ((variance_values >= 0) & (variance_values <= 1)).all():
        failures.append("PCA variance ratios outside [0, 1].")

    if variance_values.sum() > 1.0 + 1e-12:
        failures.append("PCA explained variance sum exceeds 1.")

    if scores["is_anomaly"].sum() != 5:
        failures.append("Unexpected anomaly count.")

    if not ranking["isolation_forest_score"].is_monotonic_increasing:
        failures.append("Anomaly ranking is not sorted by score.")

    flagged_indices = set(flagged["na_index"])
    score_indices = set(scores.loc[scores["is_anomaly"], "na_index"])

    if flagged_indices != score_indices:
        failures.append("Flagged anomaly table does not match anomaly labels.")

    return na, steps, ml, variance_values, scores


def validate_pipeline_runner(failures: list[str]) -> None:
    pipeline_result = subprocess.run(
        [sys.executable, "run_pipeline.py"],
        capture_output=True,
        text=True,
    )

    if pipeline_result.returncode != 0:
        failures.append("run_pipeline.py did not complete successfully.")

    if "G1 pipeline runner: PASS" not in pipeline_result.stdout:
        failures.append("run_pipeline.py did not report PASS.")


def main() -> None:

    failures = []
    report_lines = ["G5 final repository validation: PASS"]

    validate_expected_files(failures)
    validate_table_shapes(failures)

    for path in EXPECTED_PLOTS:
        validate_plot(path, failures)

    na, steps, ml, variance_values, scores = validate_core_tables(failures)

    validate_pipeline_runner(failures)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "G5 final repository validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )
        raise SystemExit("G5 final repository validation failed. See report.")

    report_lines.extend(
        [
            f"validated tables: {len(EXPECTED_TABLE_SHAPES)}",
            f"validated plots: {len(EXPECTED_PLOTS)}",
            f"validated scripts: {len(EXPECTED_CORE_SCRIPTS)}",
            "run_pipeline.py: PASS",
            f"Na coordinate rows: {len(na)}",
            f"periodic step rows: {len(steps)}",
            f"max step_frac: {steps['step_frac'].max()}",
            f"ML input rows: {len(ml)}",
            f"PCA variance sum: {variance_values.sum()}",
            f"flagged anomalies: {int(scores['is_anomaly'].sum())}",
        ]
    )

    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("G5 final repository validation: PASS")


if __name__ == "__main__":
    main()
