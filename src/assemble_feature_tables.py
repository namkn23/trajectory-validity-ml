from pathlib import Path
import pandas as pd


DISPLACEMENT_PATH = Path("results/tables/displacement_features.csv")
STEP_FEATURE_PATH = Path("results/tables/step_features.csv")
STEP_TABLE_PATH = Path("results/tables/na_periodic_steps.csv")

ATOM_OUTPUT_PATH = Path("results/tables/atom_features.csv")
FRAME_OUTPUT_PATH = Path("results/tables/frame_features.csv")

REPORT_PATH = Path("results/reports/d4_feature_assembly_report.txt")


def main() -> None:

    # load outputs from previous stages
    displacement = pd.read_csv(DISPLACEMENT_PATH)

    step_features = pd.read_csv(STEP_FEATURE_PATH)
    step_table = pd.read_csv(STEP_TABLE_PATH)

    # combine atom-wise displacement + step stats
    atom_features = displacement.merge(
        step_features,
        on="na_index",
        how="inner"
    )

    # frame-level stats
    # keeping this separate for now because might add extra frame diagnostics later
    frame_features = (
        step_table.groupby("to_frame")
        .agg(
            frame_mean_step_frac=("step_frac", "mean"),
            frame_max_step_frac=("step_frac", "max"),
            frame_step_std_frac=("step_frac", "std"),
        )
        .reset_index()
    )

    # rename frame column after aggregation
    frame_features = frame_features.rename(
        columns={"to_frame": "frame"}
    )

    # output dirs
    ATOM_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    FRAME_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    atom_features.to_csv(
        ATOM_OUTPUT_PATH,
        index=False
    )

    frame_features.to_csv(FRAME_OUTPUT_PATH, index=False)

    # quick summary report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("D4 feature table assembly: COMPLETE\n")

        f.write(f"atom feature rows: {len(atom_features)}\n")
        f.write(f"frame feature rows: {len(frame_features)}\n")

        f.write("\n")

        f.write(
            f"atom feature columns: {len(atom_features.columns)}\n"
        )

        f.write(
            f"frame feature columns: {len(frame_features.columns)}\n"
        )

    # maybe later also dump missing-value counts here or something
    print(
        f"D4 complete: wrote {len(atom_features)} atom rows "
        f"and {len(frame_features)} frame rows."
    )


if __name__ == "__main__":
    main()
