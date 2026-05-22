from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_PATH = Path("results/tables/displacement_features.csv")
OUTPUT_PATH = Path("results/plots/msd_by_na_atom.png")

REPORT_PATH = Path("results/reports/e1_msd_plot_report.txt")


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        df["na_index"],
        df["msd_frac"],
        marker="o",
        linewidth=1,
    )

    ax.set_xlabel("Na atom index")
    ax.set_ylabel("MSD in fractional-coordinate units")
    ax.set_title("Mean squared displacement by Na atom")
    ax.grid(True, linewidth=0.4, alpha=0.5)

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=200)
    plt.close(fig)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report = (
        "E1 MSD plot generation: COMPLETE\n"
        f"input: {INPUT_PATH}\n"
        f"output: {OUTPUT_PATH}\n"
        f"rows plotted: {len(df)}\n"
        f"msd_frac min: {df['msd_frac'].min()}\n"
        f"msd_frac max: {df['msd_frac'].max()}\n"
        f"output bytes: {OUTPUT_PATH.stat().st_size}\n"
    )

    REPORT_PATH.write_text(report, encoding="utf-8")

    print(f"E1 complete: wrote MSD plot to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
