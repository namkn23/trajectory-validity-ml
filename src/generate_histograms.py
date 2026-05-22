from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


STEP_TABLE_PATH = Path("results/tables/na_periodic_steps.csv")
ATOM_FEATURES_PATH = Path("results/tables/atom_features.csv")

STEP_HIST_PATH = Path("results/plots/step_magnitude_histogram.png")
MSD_HIST_PATH = Path("results/plots/atom_msd_histogram.png")
MEAN_STEP_HIST_PATH = Path("results/plots/atom_mean_step_histogram.png")

REPORT_PATH = Path("results/reports/e3_histogram_report.txt")


def make_histogram(
    values,
    xlabel: str,
    title: str,
    output_path: Path,
    bins: int = 30,
) -> None:

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 4.5))

    ax.hist(values, bins=bins)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.grid(True, linewidth=0.4, alpha=0.5)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:

    steps = pd.read_csv(STEP_TABLE_PATH)
    atom = pd.read_csv(ATOM_FEATURES_PATH)

    # this one has many more rows, so use a slightly finer histogram
    make_histogram(
        values=steps["step_frac"],
        xlabel="Periodic step magnitude (fractional units)",
        title="Distribution of Na periodic step magnitudes",
        output_path=STEP_HIST_PATH,
        bins=40,
    )

    make_histogram(
        values=atom["msd_frac"],
        xlabel="MSD (fractional-coordinate units)",
        title="Distribution of per-atom MSD values",
        output_path=MSD_HIST_PATH,
        bins=15,
    )

    make_histogram(
        values=atom["mean_step_frac"],
        xlabel="Mean step magnitude (fractional units)",
        title="Distribution of per-atom mean step magnitudes",
        output_path=MEAN_STEP_HIST_PATH,
        bins=15,
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "E3 histogram generation: COMPLETE",
        f"step histogram: {STEP_HIST_PATH}",
        f"atom MSD histogram: {MSD_HIST_PATH}",
        f"atom mean step histogram: {MEAN_STEP_HIST_PATH}",
        f"step rows plotted: {len(steps)}",
        f"atom rows plotted: {len(atom)}",
        f"step histogram bytes: {STEP_HIST_PATH.stat().st_size}",
        f"MSD histogram bytes: {MSD_HIST_PATH.stat().st_size}",
        f"mean step histogram bytes: {MEAN_STEP_HIST_PATH.stat().st_size}",
    ]

    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("E3 complete: histograms generated.")


if __name__ == "__main__":
    main()
