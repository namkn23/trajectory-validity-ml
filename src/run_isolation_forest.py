from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest


INPUT_PATH = Path("results/tables/ml_input_scaled.csv")

OUTPUT_PATH = Path("results/tables/anomaly_scores.csv")
REPORT_PATH = Path("results/reports/f6_isolation_forest_report.txt")


RANDOM_STATE = 7
CONTAMINATION = 0.10


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    feature_columns = [
        column for column in df.columns
        if column != "na_index"
    ]

    x = df[feature_columns].to_numpy()

    # simple diagnostic model, not a proof that an atom is physically wrong
    model = IsolationForest(
        n_estimators=100,
        contamination=CONTAMINATION,
        random_state=RANDOM_STATE,
    )

    labels = model.fit_predict(x)
    decision_scores = model.decision_function(x)

    output = pd.DataFrame(
        {
            "na_index": df["na_index"],
            "isolation_forest_score": decision_scores,
            "is_anomaly": labels == -1,
        }
    )

    # put flagged atoms first, and most unusual first inside that group
    output = (
        output.sort_values(
            ["is_anomaly", "isolation_forest_score"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output.to_csv(OUTPUT_PATH, index=False)

    anomaly_count = int(output["is_anomaly"].sum())

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("F6 Isolation Forest anomaly scoring: COMPLETE\n")
        f.write(f"input: {INPUT_PATH}\n")
        f.write(f"output: {OUTPUT_PATH}\n")
        f.write(f"rows scored: {len(output)}\n")
        f.write(f"features used: {len(feature_columns)}\n")
        f.write(f"contamination: {CONTAMINATION}\n")
        f.write(f"random_state: {RANDOM_STATE}\n")
        f.write(f"flagged anomalies: {anomaly_count}\n")
        f.write(
            "interpretation: diagnostic ranking only; "
            "flagged atoms require physical inspection.\n"
        )

    print(
        f"F6 complete: scored {len(output)} Na atoms; "
        f"flagged {anomaly_count} anomalies."
    )


if __name__ == "__main__":
    main()
