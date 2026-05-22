from pathlib import Path

import numpy as np
import pandas as pd


ATOM_FEATURES_PATH = Path("results/tables/atom_features.csv")
FRAME_FEATURES_PATH = Path("results/tables/frame_features.csv")

REPORT_PATH = Path("results/reports/feature_table_validation.txt")


EXPECTED_ATOM_ROWS = 48
EXPECTED_FRAME_ROWS = 3928


ATOM_COLUMNS = [
    "na_index",
    "msd_frac",
    "mean_displacement_frac",
    "max_displacement_frac",
    "final_displacement_frac",
    "mean_step_frac",
    "max_step_frac",
    "step_std_frac",
]

FRAME_COLUMNS = [
    "frame",
    "frame_mean_step_frac",
    "frame_max_step_frac",
    "frame_step_std_frac",
]


def main() -> None:

    atom = pd.read_csv(ATOM_FEATURES_PATH)
    frame = pd.read_csv(FRAME_FEATURES_PATH)

    failures = []

    if list(atom.columns) != ATOM_COLUMNS:
        failures.append(f"Unexpected atom feature columns: {list(atom.columns)}")

    if list(frame.columns) != FRAME_COLUMNS:
        failures.append(f"Unexpected frame feature columns: {list(frame.columns)}")

    if len(atom) != EXPECTED_ATOM_ROWS:
        failures.append(
            f"Unexpected atom feature row count: {len(atom)} != {EXPECTED_ATOM_ROWS}"
        )

    if len(frame) != EXPECTED_FRAME_ROWS:
        failures.append(
            f"Unexpected frame feature row count: {len(frame)} != {EXPECTED_FRAME_ROWS}"
        )

    if atom["na_index"].nunique() != EXPECTED_ATOM_ROWS:
        failures.append("Atom feature table does not contain 48 unique Na indices.")

    if frame["frame"].min() != 2 or frame["frame"].max() != 3929:
        failures.append("Frame feature table should cover frames 2 through 3929.")

    atom_numeric = atom.drop(columns=["na_index"])
    frame_numeric = frame.drop(columns=["frame"])

    if not np.isfinite(atom_numeric.to_numpy()).all():
        failures.append("Atom feature table contains non-finite values.")

    if not np.isfinite(frame_numeric.to_numpy()).all():
        failures.append("Frame feature table contains non-finite values.")

    if (atom_numeric < 0).any().any():
        failures.append("Atom feature table contains negative physical magnitudes.")

    if (frame_numeric < 0).any().any():
        failures.append("Frame feature table contains negative physical magnitudes.")

    if (atom["msd_frac"] < 0).any():
        failures.append("Atom MSD contains negative values.")

    if (atom["max_displacement_frac"] < atom["mean_displacement_frac"]).any():
        failures.append("Some atom max displacement values are below mean displacement.")

    if (atom["max_step_frac"] < atom["mean_step_frac"]).any():
        failures.append("Some atom max step values are below mean step.")

    if (frame["frame_max_step_frac"] < frame["frame_mean_step_frac"]).any():
        failures.append("Some frame max step values are below frame mean step.")

    if atom["max_displacement_frac"].max() > 1.0:
        failures.append("Atom maximum displacement exceeds one fractional cell length.")

    if atom["max_step_frac"].max() > 0.25:
        failures.append("Atom maximum step exceeds conservative teleportation threshold.")

    if frame["frame_max_step_frac"].max() > 0.25:
        failures.append("Frame maximum step exceeds conservative teleportation threshold.")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "D5 feature table validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )

        raise SystemExit("D5 feature table validation failed. See report.")

    report_lines = [
        "D5 feature table validation: PASS",
        f"atom feature rows: {len(atom)}",
        f"frame feature rows: {len(frame)}",
        f"atom feature columns: {len(atom.columns)}",
        f"frame feature columns: {len(frame.columns)}",
        f"max atom MSD: {atom['msd_frac'].max()}",
        f"max atom displacement: {atom['max_displacement_frac'].max()}",
        f"max atom step: {atom['max_step_frac'].max()}",
        f"max frame step: {frame['frame_max_step_frac'].max()}",
    ]

    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("D5 feature table validation: PASS")


if __name__ == "__main__":
    main()
