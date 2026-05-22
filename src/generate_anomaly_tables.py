from pathlib import Path

import pandas as pd


SCORES_PATH = Path("results/tables/anomaly_scores.csv")

FLAGGED_OUTPUT_PATH = Path("results/tables/flagged_anomalies.csv")
RANKING_OUTPUT_PATH = Path("results/tables/anomaly_score_ranking.csv")

REPORT_PATH = Path("results/reports/f8_anomaly_table_report.txt")


def main() -> None:

    scores = pd.read_csv(SCORES_PATH)

    # lower Isolation Forest score means more unusual
    ranking = (
        scores.sort_values(
            "isolation_forest_score",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    ranking.insert(
        0,
        "anomaly_rank",
        range(1, len(ranking) + 1),
    )

    flagged = ranking[ranking["is_anomaly"]].reset_index(drop=True)

    FLAGGED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RANKING_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    ranking.to_csv(RANKING_OUTPUT_PATH, index=False)
    flagged.to_csv(FLAGGED_OUTPUT_PATH, index=False)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("F8 anomaly table generation: COMPLETE\n")
        f.write(f"input: {SCORES_PATH}\n")
        f.write(f"ranking output: {RANKING_OUTPUT_PATH}\n")
        f.write(f"flagged output: {FLAGGED_OUTPUT_PATH}\n")
        f.write(f"total ranked atoms: {len(ranking)}\n")
        f.write(f"flagged anomalies: {len(flagged)}\n")
        f.write(
            "interpretation: ranking supports manual trajectory inspection only.\n"
        )

    print(
        f"F8 complete: generated anomaly ranking for {len(ranking)} atoms "
        f"with {len(flagged)} flagged anomalies."
    )


if __name__ == "__main__":
    main()
