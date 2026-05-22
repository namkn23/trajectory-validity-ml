from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


SCORES_PATH = Path("results/tables/anomaly_scores.csv")
PCA_PATH = Path("results/tables/pca_embeddings.csv")

DIST_OUTPUT_PATH = Path("results/plots/anomaly_score_distribution.png")
PCA_OUTPUT_PATH = Path("results/plots/pca_anomaly_overlay.png")

REPORT_PATH = Path("results/reports/f9_anomaly_plot_report.txt")


def main() -> None:

    scores = pd.read_csv(SCORES_PATH)
    pca = pd.read_csv(PCA_PATH)

    merged = pca.merge(
        scores,
        on="na_index",
        how="inner",
    )

    DIST_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PCA_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # score histogram first; mostly for checking whether the flagged tail is obvious
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))

    ax1.hist(merged["isolation_forest_score"], bins=20)

    ax1.set_xlabel("Isolation Forest score")
    ax1.set_ylabel("Count")
    ax1.set_title("Distribution of anomaly scores")
    ax1.grid(True, linewidth=0.4, alpha=0.5)

    fig1.tight_layout()
    fig1.savefig(DIST_OUTPUT_PATH, dpi=200)
    plt.close(fig1)

    # PCA overlay with flagged atoms marked separately
    fig2, ax2 = plt.subplots(figsize=(6.5, 5.5))

    normal = merged[~merged["is_anomaly"]]
    anomalous = merged[merged["is_anomaly"]]

    ax2.scatter(
        normal["pc1"],
        normal["pc2"],
        s=35,
        label="Normal",
    )

    ax2.scatter(
        anomalous["pc1"],
        anomalous["pc2"],
        s=55,
        marker="x",
        label="Flagged",
    )

    for _, row in anomalous.iterrows():
        ax2.annotate(
            str(int(row["na_index"])),
            (row["pc1"], row["pc2"]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=7,
        )

    ax2.set_xlabel("PC1")
    ax2.set_ylabel("PC2")
    ax2.set_title("PCA projection with anomaly overlay")
    ax2.grid(True, linewidth=0.4, alpha=0.5)
    ax2.legend()

    fig2.tight_layout()
    fig2.savefig(PCA_OUTPUT_PATH, dpi=200)
    plt.close(fig2)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "F9 anomaly plot generation: COMPLETE",
        f"score input: {SCORES_PATH}",
        f"pca input: {PCA_PATH}",
        f"distribution plot: {DIST_OUTPUT_PATH}",
        f"overlay plot: {PCA_OUTPUT_PATH}",
        f"rows plotted: {len(merged)}",
        f"flagged anomalies: {int(merged['is_anomaly'].sum())}",
        "interpretation: plots support diagnostic inspection only.",
    ]

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print(
        "F9 complete: generated anomaly distribution and PCA overlay "
        f"plots for {len(merged)} Na atoms."
    )


if __name__ == "__main__":
    main()
