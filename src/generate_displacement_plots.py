from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_PATH = Path("results/tables/displacement_features.csv")

MEAN_OUTPUT_PATH = Path("results/plots/mean_displacement_by_na_atom.png")
MAX_OUTPUT_PATH = Path("results/plots/max_displacement_by_na_atom.png")

REPORT_PATH = Path("results/reports/e2_displacement_plot_report.txt")


def make_plot(
    df: pd.DataFrame,
    column: str,
    ylabel: str,
    title: str,
    output_path: Path,
) -> None:

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        df["na_index"],
        df[column],
        marker="o",
        linewidth=1,
    )

    ax.set_xlabel("Na atom index")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, linewidth=0.4, alpha=0.5)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    # keep these as two separate calls so the filenames stay explicit
    make_plot(
        df=df,
        column="mean_displacement_frac",
        ylabel="Mean displacement (fractional units)",
        title="Mean displacement by Na atom",
        output_path=MEAN_OUTPUT_PATH,
    )

    make_plot(
        df=df,
        column="max_displacement_frac",
        ylabel="Maximum displacement (fractional units)",
        title="Maximum displacement by Na atom",
        output_path=MAX_OUTPUT_PATH,
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "E2 displacement plot generation: COMPLETE",
        f"input: {INPUT_PATH}",
        f"mean displacement plot: {MEAN_OUTPUT_PATH}",
        f"max displacement plot: {MAX_OUTPUT_PATH}",
        f"rows plotted: {len(df)}",
        f"mean plot bytes: {MEAN_OUTPUT_PATH.stat().st_size}",
        f"max plot bytes: {MAX_OUTPUT_PATH.stat().st_size}",
    ]

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("E2 complete: displacement plots generated.")


if __name__ == "__main__":
    main()
