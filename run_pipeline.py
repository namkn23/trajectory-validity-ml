from pathlib import Path
import argparse
import subprocess
import sys
from datetime import datetime


# keeping this simple for now
REPORT_PATH = Path("results/reports/g1_pipeline_runner_report.txt")


# could probably split this later if the pipeline grows more
STAGES = [
    ("A1", "src/audit_xdatcar_structure.py", [
        "results/tables/xdatcar_audit.csv",
        "results/reports/xdatcar_audit.txt",
    ]),
    ("A2", "src/test_audit_rerun.py", [
        "results/reports/audit_rerun_test.txt",
    ]),
    ("B1", "src/extract_na_coordinates.py", [
        "results/tables/na_coordinates.csv",
    ]),
    ("B2", "src/validate_na_coordinates.py", [
        "results/reports/na_coordinates_validation.txt",
    ]),
    ("B3", "src/check_na_extraction_consistency.py", [
        "results/reports/na_extraction_rerun_test.txt",
    ]),
    ("C1", "src/compute_periodic_boundary_steps.py", [
        "results/tables/na_periodic_steps.csv",
    ]),
    ("C2", "src/validate_step_statistics.py", [
        "results/reports/step_statistics_validation.txt",
    ]),
    ("C3", "src/detect_suspicious_jumps.py", [
        "results/tables/suspicious_jumps.csv",
        "results/reports/suspicious_jump_report.txt",
    ]),
    ("C4", "src/validate_step_outputs.py", [
        "results/reports/step_pipeline_rerun_test.txt",
    ]),
    ("D1", "src/compute_displacement_features.py", [
        "results/tables/displacement_features.csv",
        "results/reports/d1_displacement_feature_report.txt",
    ]),
    ("D2", "src/compute_step_features.py", [
        "results/tables/step_features.csv",
        "results/reports/d2_step_feature_report.txt",
    ]),
    ("D3", "src/compute_mobility_spread_features.py", [
        "results/tables/mobility_spread_features.csv",
        "results/reports/d3_mobility_spread_report.txt",
    ]),
    ("D4", "src/assemble_feature_tables.py", [
        "results/tables/atom_features.csv",
        "results/tables/frame_features.csv",
        "results/reports/d4_feature_assembly_report.txt",
    ]),
    ("D5", "src/validate_feature_tables.py", [
        "results/reports/feature_table_validation.txt",
    ]),
    ("D6", "src/feature_rerun_check.py", [
        "results/reports/feature_pipeline_rerun_test.txt",
    ]),
    ("E1", "src/generate_msd_plot.py", [
        "results/plots/msd_by_na_atom.png",
        "results/reports/e1_msd_plot_report.txt",
    ]),
    ("E2", "src/generate_displacement_plots.py", [
        "results/plots/mean_displacement_by_na_atom.png",
        "results/plots/max_displacement_by_na_atom.png",
        "results/reports/e2_displacement_plot_report.txt",
    ]),
    ("E3", "src/generate_histograms.py", [
        "results/plots/step_magnitude_histogram.png",
        "results/plots/atom_msd_histogram.png",
        "results/plots/atom_mean_step_histogram.png",
        "results/reports/e3_histogram_report.txt",
    ]),
    ("E4", "src/validate_generated_plots.py", [
        "results/reports/plot_validation.txt",
    ]),
    ("F1", "src/prepare_ml_input.py", [
        "results/tables/ml_input_scaled.csv",
        "results/reports/f1_ml_input_report.txt",
    ]),
    ("F2", "src/validate_ml_input.py", [
        "results/reports/f2_ml_input_validation.txt",
    ]),
    ("F3", "src/run_pca.py", [
        "results/tables/pca_embeddings.csv",
        "results/tables/pca_explained_variance.csv",
        "results/reports/f3_pca_report.txt",
    ]),
    ("F4", "src/validate_pca.py", [
        "results/reports/f4_pca_validation.txt",
    ]),
    ("F5", "src/generate_pca_plots.py", [
        "results/plots/pca_embedding_scatter.png",
        "results/reports/f5_pca_plot_report.txt",
    ]),

    # anomaly detection — F6 onwards
    ("F6", "src/run_isolation_forest.py", [
        "results/tables/anomaly_scores.csv",
        "results/reports/f6_isolation_forest_report.txt",
    ]),
    ("F7", "src/validate_anomaly_scores.py", [
        "results/reports/f7_anomaly_score_validation.txt",
    ]),
    ("F8", "src/generate_anomaly_tables.py", [
        "results/tables/anomaly_score_ranking.csv",
        "results/tables/flagged_anomalies.csv",
        "results/reports/f8_anomaly_table_report.txt",
    ]),
    ("F9", "src/generate_anomaly_plots.py", [
        "results/plots/anomaly_score_distribution.png",
        "results/plots/pca_anomaly_overlay.png",
        "results/reports/f9_anomaly_plot_report.txt",
    ]),
]


def existing_outputs_ok(paths) -> bool:
    for path in paths:
        file_path = Path(path)

        # empty file probably means the script crashed mid-write
        if not file_path.exists() or file_path.stat().st_size == 0:
            return False

    return True


def run_script(script_path: str) -> str:
    # TODO: add a timeout here if this is ever used on longer runs
    result = subprocess.run(
        [sys.executable, script_path],

        # subprocess output can get noisy pretty fast
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        # keeping stdout/stderr together makes debugging easier later
        raise RuntimeError(
            f"Script failed: {script_path}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    lines = result.stdout.strip().splitlines()


    # last printed line is enough for this small report
    return lines[-1] if lines else "completed"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run or verify the trajectory diagnostics pipeline."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate every stage output by running all stage scripts.",
    )

    args = parser.parse_args()


    # avoid half-written reports if parent dirs don't exist yet
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # small enough that a text report is still readable
    report_lines = [
        "G1 pipeline runner: PASS",
        f"timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"mode: {'force rebuild' if args.force else 'verify existing outputs'}",
        "",
    ]

    for stage_name, script_path, outputs in STAGES:
        # mostly here so reruns fail loudly instead of silently skipping stages
        if not Path(script_path).exists():
            raise FileNotFoundError(f"{stage_name}: missing script {script_path}")

        if args.force:
            message = run_script(script_path)

            report_lines.append(
                f"{stage_name}: RUN {script_path}: PASS ({message})"
            )

            print(f"{stage_name}: RUN")


        else:
            if not existing_outputs_ok(outputs):
                missing = [path for path in outputs if not Path(path).exists()]

                empty = [
                    path for path in outputs
                    if Path(path).exists() and Path(path).stat().st_size == 0
                ]

                raise FileNotFoundError(
                    f"{stage_name}: expected outputs missing or empty. "
                    f"missing={missing}, empty={empty}. "
                    f"Run with --force to regenerate."
                )

            report_lines.append(f"{stage_name}: existing outputs found")
            print(f"{stage_name}: OK")

    # report is intentionally lightweight/plain text
    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("G1 pipeline runner: PASS")


if __name__ == "__main__":
    main()
