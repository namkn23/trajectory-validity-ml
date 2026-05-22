from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler


INPUT_PATH = Path("results/tables/atom_features.csv")

OUTPUT_PATH = Path("results/tables/ml_input_scaled.csv")
REPORT_PATH = Path("results/reports/f1_ml_input_report.txt")


FEATURE_COLUMNS = [
    "msd_frac",
    "mean_displacement_frac",
    "max_displacement_frac",
    "final_displacement_frac",
    "mean_step_frac",
    "max_step_frac",
    "step_std_frac",
]


def main() -> None:

    atom = pd.read_csv(INPUT_PATH)

    # keep Na index out of the scaler, obviously
    feature_matrix = atom[FEATURE_COLUMNS].copy()

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(feature_matrix)

    scaled_columns = [
        f"{column}_scaled"
        for column in FEATURE_COLUMNS
    ]

    scaled = pd.DataFrame(
        scaled_values,
        columns=scaled_columns,
    )

    scaled.insert(0, "na_index", atom["na_index"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    scaled.to_csv(OUTPUT_PATH, index=False)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "F1 ML input preparation: COMPLETE",
        f"input: {INPUT_PATH}",
        f"output: {OUTPUT_PATH}",
        f"rows: {len(scaled)}",
        f"features selected: {len(FEATURE_COLUMNS)}",
        f"feature columns: {', '.join(FEATURE_COLUMNS)}",
        "scaling: StandardScaler fit on atom-level feature table",
    ]

    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(f"F1 complete: wrote scaled ML input to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
