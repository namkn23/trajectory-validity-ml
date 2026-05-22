from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("results/tables/ml_input_scaled.csv")
REPORT_PATH = Path("results/reports/f2_ml_input_validation.txt")


EXPECTED_ROWS = 48

EXPECTED_COLUMNS = [
    "na_index",
    "msd_frac_scaled",
    "mean_displacement_frac_scaled",
    "max_displacement_frac_scaled",
    "final_displacement_frac_scaled",
    "mean_step_frac_scaled",
    "max_step_frac_scaled",
    "step_std_frac_scaled",
]


def main() -> None:

    df = pd.read_csv(INPUT_PATH)
    failures = []

    if list(df.columns) != EXPECTED_COLUMNS:
        failures.append(f"Unexpected ML input columns: {list(df.columns)}")

    if len(df) != EXPECTED_ROWS:
        failures.append(f"Unexpected row count: {len(df)} != {EXPECTED_ROWS}")

    if df["na_index"].nunique() != EXPECTED_ROWS:
        failures.append("ML input table does not contain 48 unique Na indices.")

    numeric = df.drop(columns=["na_index"])

    if not np.isfinite(numeric.to_numpy()).all():
        failures.append("ML input table contains non-finite values.")

    if numeric.isna().any().any():
        failures.append("ML input table contains NaN values.")

    # after scaling none of these columns should be flat
    constant_columns = []

    for column in numeric.columns:
        if np.isclose(numeric[column].std(ddof=0), 0.0):
            constant_columns.append(column)

    if constant_columns:
        failures.append(f"Constant scaled features detected: {constant_columns}")

    means = numeric.mean()
    population_stds = numeric.std(ddof=0)

    mean_tolerance = 1e-12
    std_tolerance = 1e-12

    if not (means.abs() < mean_tolerance).all():
        failures.append(
            "Some scaled feature means are not sufficiently close to zero."
        )

    if not ((population_stds - 1.0).abs() < std_tolerance).all():
        failures.append(
            "Some scaled feature standard deviations are not sufficiently close to one."
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "F2 ML input validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )

        raise SystemExit("F2 ML input validation failed. See report.")

    max_mean_error = means.abs().max()
    max_std_error = (population_stds - 1.0).abs().max()

    REPORT_PATH.write_text(
        "F2 ML input validation: PASS\n"
        f"rows: {len(df)}\n"
        f"scaled feature count: {len(numeric.columns)}\n"
        f"maximum absolute scaled mean: {max_mean_error}\n"
        f"maximum std deviation error: {max_std_error}\n",
        encoding="utf-8",
    )

    print("F2 ML input validation: PASS")


if __name__ == "__main__":
    main()
