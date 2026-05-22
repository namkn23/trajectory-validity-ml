from pathlib import Path

import pandas as pd


INPUT_PATH = Path("results/tables/na_periodic_steps.csv")

OUTPUT_PATH = Path("results/tables/suspicious_jumps.csv")
REPORT_PATH = Path("results/reports/suspicious_jump_report.txt")


# conservative threshold for this pristine run
# this is a flag-for-inspection number, not a "physics is broken" number
SUSPICIOUS_STEP_THRESHOLD = 0.0009


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    suspicious = df[
        df["step_frac"] > SUSPICIOUS_STEP_THRESHOLD
    ].copy()

    suspicious = suspicious.sort_values(
        ["step_frac", "from_frame", "na_index"],
        ascending=[False, True, True],
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    suspicious.to_csv(OUTPUT_PATH, index=False)

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report_lines = [
        "C3 suspicious jump detection: COMPLETE",
        f"threshold: {SUSPICIOUS_STEP_THRESHOLD}",
        f"flagged_events: {len(suspicious)}",
    ]

    if len(suspicious) > 0:

        report_lines.extend(
            [
                f"max_step_frac: {suspicious['step_frac'].max()}",
                f"mean_flagged_step_frac: {suspicious['step_frac'].mean()}",
                f"unique_flagged_na_indices: {suspicious['na_index'].nunique()}",
            ]
        )

    # leave a small plain text trail for quick checking
    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print(
        f"C3 complete: flagged {len(suspicious)} suspicious step events."
    )


if __name__ == "__main__":
    main()
