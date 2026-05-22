from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("results/tables/anomaly_scores.csv")
REPORT_PATH = Path("results/reports/f7_anomaly_score_validation.txt")


EXPECTED_ROWS = 48

EXPECTED_COLUMNS = [
    "na_index",
    "isolation_forest_score",
    "is_anomaly",
]


def main() -> None:

    df = pd.read_csv(INPUT_PATH)
    failures = []

    if list(df.columns) != EXPECTED_COLUMNS:
        failures.append(
            f"Unexpected anomaly score columns: {list(df.columns)}"
        )

    if len(df) != EXPECTED_ROWS:
        failures.append(
            f"Unexpected anomaly score row count: {len(df)} != {EXPECTED_ROWS}"
        )

    if df["na_index"].nunique() != EXPECTED_ROWS:
        failures.append(
            "Anomaly score table does not contain 48 unique Na indices."
        )

    if not np.isfinite(df["isolation_forest_score"].to_numpy()).all():
        failures.append("Anomaly score table contains non-finite scores.")

    valid_labels = {True, False}
    observed_labels = set(df["is_anomaly"].unique())

    if not observed_labels.issubset(valid_labels):
        failures.append(f"Unexpected anomaly labels: {observed_labels}")

    anomaly_fraction = float(df["is_anomaly"].mean())
    anomaly_count = int(df["is_anomaly"].sum())

    if anomaly_fraction <= 0:
        failures.append("No anomalies were flagged.")

    if anomaly_fraction >= 0.5:
        failures.append(f"Anomaly fraction unusually high: {anomaly_fraction}")

    # fixed because IsolationForest uses contamination=0.10 on 48 atoms
    if anomaly_count != 5:
        failures.append(f"Unexpected anomaly count: {anomaly_count} != 5")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "F7 anomaly score validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )
        raise SystemExit("F7 anomaly score validation failed. See report.")

    REPORT_PATH.write_text(
        "F7 anomaly score validation: PASS\n"
        f"rows: {len(df)}\n"
        f"unique Na indices: {df['na_index'].nunique()}\n"
        f"flagged anomalies: {anomaly_count}\n"
        f"anomaly fraction: {anomaly_fraction}\n"
        f"minimum anomaly score: {df['isolation_forest_score'].min()}\n"
        f"maximum anomaly score: {df['isolation_forest_score'].max()}\n",
        encoding="utf-8",
    )

    print("F7 anomaly score validation: PASS")


if __name__ == "__main__":
    main()
