from pathlib import Path
import pandas as pd
import numpy as np

INPUT_PATH = Path("results/tables/na_coordinates.csv")
OUTPUT_PATH = Path("results/tables/na_periodic_steps.csv")
REPORT_PATH = Path("results/reports/c1_periodic_step_report.txt")


def minimum_image_delta(delta: pd.Series) -> pd.Series:
    # Fractional coordinates wrap at cell boundaries; this maps jumps into [-0.5, 0.5).
    return delta - np.round(delta)


def main() -> None:
    df = pd.read_csv(INPUT_PATH)
    df = df.sort_values(["na_index", "frame"]).reset_index(drop=True)

    previous = df.groupby("na_index")[["frame", "x", "y", "z"]].shift(1)

    steps = df.copy()
    steps["from_frame"] = previous["frame"]
    steps["to_frame"] = steps["frame"]

    steps = steps.dropna(subset=["from_frame"]).copy()
    steps["from_frame"] = steps["from_frame"].astype(int)
    steps["to_frame"] = steps["to_frame"].astype(int)

    steps["dx_frac"] = minimum_image_delta(steps["x"] - previous.loc[steps.index, "x"])
    steps["dy_frac"] = minimum_image_delta(steps["y"] - previous.loc[steps.index, "y"])
    steps["dz_frac"] = minimum_image_delta(steps["z"] - previous.loc[steps.index, "z"])

    steps["step_frac"] = np.sqrt(
        steps["dx_frac"] ** 2
        + steps["dy_frac"] ** 2
        + steps["dz_frac"] ** 2
    )

    output = steps[
        ["from_frame", "to_frame", "na_index", "dx_frac", "dy_frac", "dz_frac", "step_frac"]
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "C1 periodic-boundary step computation: COMPLETE\n"
        f"rows: {len(output)}\n"
        f"from_frame range: {output['from_frame'].min()}-{output['from_frame'].max()}\n"
        f"to_frame range: {output['to_frame'].min()}-{output['to_frame'].max()}\n"
        f"unique Na indices: {output['na_index'].nunique()}\n"
        f"step_frac min: {output['step_frac'].min()}\n"
        f"step_frac max: {output['step_frac'].max()}\n"
        f"step_frac mean: {output['step_frac'].mean()}\n",
        encoding="utf-8",
    )

    print(f"C1 complete: wrote {len(output)} periodic step rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
