from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("results/tables/na_coordinates.csv")
REPORT_PATH = Path("results/reports/na_coordinates_validation.txt")


EXPECTED_NA_PER_FRAME = 48
EXPECTED_FIRST_FRAME = 1
EXPECTED_LAST_FRAME = 3929

EXPECTED_COLUMNS = ["frame", "na_index", "x", "y", "z"]


def main() -> None:

    df = pd.read_csv(INPUT_PATH)
    failures = []

    if list(df.columns) != EXPECTED_COLUMNS:
        failures.append(f"Unexpected columns: {list(df.columns)}")

    expected_frames = set(range(EXPECTED_FIRST_FRAME, EXPECTED_LAST_FRAME + 1))
    observed_frames = set(df["frame"].unique())

    missing_frames = sorted(expected_frames - observed_frames)
    extra_frames = sorted(observed_frames - expected_frames)

    if missing_frames:
        failures.append(f"Missing frames: {missing_frames[:10]}")

    if extra_frames:
        failures.append(f"Unexpected extra frames: {extra_frames[:10]}")

    counts_per_frame = df.groupby("frame").size()
    bad_frame_counts = counts_per_frame[
        counts_per_frame != EXPECTED_NA_PER_FRAME
    ]

    if not bad_frame_counts.empty:
        failures.append(
            "Frames with wrong Na count: "
            + bad_frame_counts.head(10).to_string()
        )

    expected_indices = set(range(EXPECTED_NA_PER_FRAME))
    bad_index_frames = []

    # slower than a vectorized trick, but easier to read when debugging
    for frame, group in df.groupby("frame"):

        observed_indices = set(group["na_index"])

        if observed_indices != expected_indices:
            bad_index_frames.append(frame)

    if bad_index_frames:
        failures.append(
            f"Frames with unexpected Na indices: {bad_index_frames[:10]}"
        )

    coord_values = df[["x", "y", "z"]].to_numpy()

    if not np.isfinite(coord_values).all():
        failures.append("Coordinate table contains non-finite values.")

    below_zero = (df[["x", "y", "z"]] < 0).any().any()
    above_one = (df[["x", "y", "z"]] >= 1).any().any()

    if below_zero or above_one:
        failures.append("Some fractional coordinates are outside [0, 1).")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "B2 Na coordinate validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )
        raise SystemExit("B2 Na coordinate validation failed. See report.")

    lines = [
        "B2 Na coordinate validation: PASS",
        f"rows: {len(df)}",
        f"frames: {df['frame'].min()}-{df['frame'].max()}",
        f"unique_frames: {df['frame'].nunique()}",
        f"Na atoms per frame: {EXPECTED_NA_PER_FRAME}",
        f"x range: {df['x'].min()} to {df['x'].max()}",
        f"y range: {df['y'].min()} to {df['y'].max()}",
        f"z range: {df['z'].min()} to {df['z'].max()}",
    ]

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("B2 Na coordinate validation: PASS")


if __name__ == "__main__":
    main()
