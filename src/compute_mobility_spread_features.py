from pathlib import Path

import pandas as pd


DISPLACEMENT_PATH = Path("results/tables/displacement_features.csv")
STEP_PATH = Path("results/tables/step_features.csv")

OUTPUT_PATH = Path("results/tables/mobility_spread_features.csv")
REPORT_PATH = Path("results/reports/d3_mobility_spread_report.txt")


def coefficient_of_variation(series: pd.Series) -> float:
    mean_value = series.mean()

    # avoid dividing by zero for a completely flat/zero feature
    if mean_value == 0:
        return 0.0

    cv = series.std() / mean_value
    return float(cv)


def main() -> None:

    displacement = pd.read_csv(DISPLACEMENT_PATH)
    step = pd.read_csv(STEP_PATH)

    # atom-level displacement + step summaries
    merged = displacement.merge(
        step,
        on="na_index",
        how="inner"
    )

    # features where I want one small spread summary across Na atoms
    metrics = {
        "msd_frac": merged["msd_frac"],
        "mean_displacement_frac": merged["mean_displacement_frac"],
        "max_displacement_frac": merged["max_displacement_frac"],

        "mean_step_frac": merged["mean_step_frac"],
        "max_step_frac": merged["max_step_frac"],
        "step_std_frac": merged["step_std_frac"],
    }

    rows = []

    for name, values in metrics.items():

        row = {
            "feature": name,
            "mean": values.mean(),
            "std": values.std(),
            "min": values.min(),
            "max": values.max(),
            "range": values.max() - values.min(),
            "coefficient_of_variation": coefficient_of_variation(values),
        }

        rows.append(row)

    spread = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    spread.to_csv(OUTPUT_PATH, index=False)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    sorted_spread = spread.sort_values(
        "coefficient_of_variation",
        ascending=False,
    )

    top_feature = sorted_spread.iloc[0]["feature"]
    top_value = spread["coefficient_of_variation"].max()

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("D3 mobility spread feature computation: COMPLETE\n")
        f.write(f"input Na atoms: {len(merged)}\n")
        f.write(f"summary rows: {len(spread)}\n")

        f.write("\n")

        f.write(
            "largest coefficient_of_variation feature: "
            f"{top_feature}\n"
        )
        f.write(
            "largest coefficient_of_variation value: "
            f"{top_value}\n"
        )

    # rough spread summary, not meant to be a full statistical analysis
    print(
        f"D3 complete: wrote {len(spread)} mobility spread rows "
        f"to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
