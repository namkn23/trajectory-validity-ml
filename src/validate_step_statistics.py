from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("results/tables/na_periodic_steps.csv")
REPORT_PATH = Path("results/reports/step_statistics_validation.txt")


EXPECTED_FIRST_FROM_FRAME = 1
EXPECTED_LAST_FROM_FRAME = 3928
EXPECTED_NA_PER_STEP_FRAME = 48

EXPECTED_COLUMNS = [
    "from_frame",
    "to_frame",
    "na_index",
    "dx_frac",
    "dy_frac",
    "dz_frac",
    "step_frac",
]


# deliberately loose: catches wrapping disasters, not real rare jumps
MAX_REASONABLE_FRACTIONAL_STEP = 0.25


def main() -> None:

    df = pd.read_csv(INPUT_PATH)
    failures = []

    if list(df.columns) != EXPECTED_COLUMNS:
        failures.append(f"Unexpected columns: {list(df.columns)}")

    expected_rows = (
        EXPECTED_LAST_FROM_FRAME
        - EXPECTED_FIRST_FROM_FRAME
        + 1
    ) * EXPECTED_NA_PER_STEP_FRAME

    if len(df) != expected_rows:
        failures.append(
            f"Unexpected row count: {len(df)} != {expected_rows}"
        )

    expected_from_frames = set(
        range(EXPECTED_FIRST_FROM_FRAME, EXPECTED_LAST_FROM_FRAME + 1)
    )
    observed_from_frames = set(df["from_frame"].unique())

    missing_from_frames = sorted(expected_from_frames - observed_from_frames)
    extra_from_frames = sorted(observed_from_frames - expected_from_frames)

    if missing_from_frames:
        failures.append(
            f"Missing from_frame values: {missing_from_frames[:10]}"
        )

    if extra_from_frames:
        failures.append(
            f"Unexpected from_frame values: {extra_from_frames[:10]}"
        )

    if not (df["to_frame"] == df["from_frame"] + 1).all():
        failures.append("Some rows do not satisfy to_frame = from_frame + 1.")

    counts_per_frame = df.groupby("from_frame").size()
    bad_counts = counts_per_frame[
        counts_per_frame != EXPECTED_NA_PER_STEP_FRAME
    ]

    if not bad_counts.empty:
        failures.append("Some from_frame values do not have 48 Na steps.")

    counts_per_na = df.groupby("na_index").size()
    expected_steps_per_na = (
        EXPECTED_LAST_FROM_FRAME
        - EXPECTED_FIRST_FROM_FRAME
        + 1
    )

    bad_na_counts = counts_per_na[
        counts_per_na != expected_steps_per_na
    ]

    if not bad_na_counts.empty:
        failures.append("Some Na indices do not have the expected number of steps.")

    numeric_cols = ["dx_frac", "dy_frac", "dz_frac", "step_frac"]

    if not np.isfinite(df[numeric_cols].to_numpy()).all():
        failures.append("Step table contains non-finite values.")

    if (df["step_frac"] < 0).any():
        failures.append("Step magnitudes contain negative values.")

    component_values = df[["dx_frac", "dy_frac", "dz_frac"]]

    # minimum-image components should stay inside the wrapped half-cell interval
    if not ((component_values >= -0.5) & (component_values <= 0.5)).all().all():
        failures.append("Minimum-image components fall outside [-0.5, 0.5].")

    recomputed = np.sqrt(
        df["dx_frac"] ** 2
        + df["dy_frac"] ** 2
        + df["dz_frac"] ** 2
    )

    max_recompute_error = float(
        np.max(np.abs(recomputed - df["step_frac"]))
    )

    if max_recompute_error > 1e-12:
        failures.append(
            "step_frac does not match vector norm; "
            f"max error = {max_recompute_error}"
        )

    max_step = float(df["step_frac"].max())

    if max_step > MAX_REASONABLE_FRACTIONAL_STEP:
        failures.append(
            f"Possible teleportation jump: max step_frac {max_step} "
            f"exceeds {MAX_REASONABLE_FRACTIONAL_STEP}"
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "C2 step statistics validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )

        raise SystemExit("C2 step statistics validation failed. See report.")

    report = (
        "C2 step statistics validation: PASS\n"
        f"rows: {len(df)}\n"
        f"from_frame range: {df['from_frame'].min()}-{df['from_frame'].max()}\n"
        f"to_frame range: {df['to_frame'].min()}-{df['to_frame'].max()}\n"
        f"unique Na indices: {df['na_index'].nunique()}\n"
        f"step_frac min: {df['step_frac'].min()}\n"
        f"step_frac mean: {df['step_frac'].mean()}\n"
        f"step_frac median: {df['step_frac'].median()}\n"
        f"step_frac max: {df['step_frac'].max()}\n"
        f"max step recomputation error: {max_recompute_error}\n"
    )

    REPORT_PATH.write_text(report, encoding="utf-8")

    print("C2 step statistics validation: PASS")


if __name__ == "__main__":
    main()
