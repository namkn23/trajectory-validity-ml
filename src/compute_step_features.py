from pathlib import Path

import pandas as pd


INPUT_PATH = Path("results/tables/na_periodic_steps.csv")

OUTPUT_PATH = Path("results/tables/step_features.csv")
REPORT_PATH = Path("results/reports/d2_step_feature_report.txt")


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    # one row per Na atom, summarising its frame-to-frame motion
    features = (
        df.groupby("na_index")
        .agg(
            mean_step_frac=("step_frac", "mean"),
            max_step_frac=("step_frac", "max"),
            step_std_frac=("step_frac", "std"),
        )
        .reset_index()
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    features.to_csv(
        OUTPUT_PATH,
        index=False
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("D2 step feature computation: COMPLETE\n")
        f.write(f"rows: {len(features)}\n")

        f.write("\n")

        f.write(f"mean_step_frac min: {features['mean_step_frac'].min()}\n")
        f.write(f"mean_step_frac max: {features['mean_step_frac'].max()}\n")
        f.write(f"max_step_frac min: {features['max_step_frac'].min()}\n")
        f.write(f"max_step_frac max: {features['max_step_frac'].max()}\n")

        f.write(
            f"step_std_frac min: {features['step_std_frac'].min()}\n"
        )
        f.write(
            f"step_std_frac max: {features['step_std_frac'].max()}\n"
        )

    # simple atom-level step stats; nothing fancy here
    print(
        f"D2 complete: wrote {len(features)} Na step feature rows "
        f"to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
