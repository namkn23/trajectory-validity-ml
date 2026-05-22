from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("results/tables/na_coordinates.csv")

OUTPUT_PATH = Path("results/tables/displacement_features.csv")
REPORT_PATH = Path("results/reports/d1_displacement_feature_report.txt")


def minimum_image_delta(delta: pd.Series) -> pd.Series:
    # periodic wrapping correction
    # if an ion crosses the cell edge we still want the short jump
    wrapped = delta - np.round(delta)

    return wrapped


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    # keep ordering stable before grouped stuff
    df = (
        df.sort_values(["na_index", "frame"])
        .reset_index(drop=True)
    )

    # initial coordinates for each Na trajectory
    initial = (
        df.groupby("na_index")[["x", "y", "z"]]
        .first()
        .rename(
            columns={
                "x": "x0",
                "y": "y0",
                "z": "z0",
            }
        )
    )

    merged = df.join(initial, on="na_index")

    # relative displacement from starting configuration
    dx = merged["x"] - merged["x0"]
    dy = merged["y"] - merged["y0"]
    dz = merged["z"] - merged["z0"]

    merged["dx0_frac"] = minimum_image_delta(dx)
    merged["dy0_frac"] = minimum_image_delta(dy)
    merged["dz0_frac"] = minimum_image_delta(dz)

    merged["displacement_frac"] = np.sqrt(
        merged["dx0_frac"] ** 2
        + merged["dy0_frac"] ** 2
        + merged["dz0_frac"] ** 2
    )

    # keeping both because sometimes squared displacement is easier to inspect
    merged["squared_displacement_frac"] = (
        merged["displacement_frac"] ** 2
    )

    features = (
        merged
        .groupby("na_index")
        .agg(
            msd_frac=("squared_displacement_frac", "mean"),
            mean_displacement_frac=("displacement_frac", "mean"),
            max_displacement_frac=("displacement_frac", "max"),
            final_displacement_frac=("displacement_frac", "last"),
        )
        .reset_index()
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    features.to_csv(OUTPUT_PATH, index=False)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:

        f.write("D1 displacement feature computation: COMPLETE\n")
        f.write(f"rows: {len(features)}\n")

        f.write("\n")

        f.write(
            f"msd_frac min: {features['msd_frac'].min()}\n"
        )

        f.write(
            f"msd_frac max: {features['msd_frac'].max()}\n"
        )

        f.write(
            f"mean_displacement_frac min: "
            f"{features['mean_displacement_frac'].min()}\n"
        )

        f.write(
            f"mean_displacement_frac max: "
            f"{features['mean_displacement_frac'].max()}\n"
        )

        f.write(
            f"max_displacement_frac min: "
            f"{features['max_displacement_frac'].min()}\n"
        )

        f.write(
            f"max_displacement_frac max: "
            f"{features['max_displacement_frac'].max()}\n"
        )

    # maybe later:
    # directional persistence?
    # hop-length distributions?
    # anisotropy?
    print(
        f"D1 complete: wrote {len(features)} Na displacement "
        f"feature rows to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
