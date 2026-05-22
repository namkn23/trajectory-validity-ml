from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


EMBEDDING_PATH = Path("results/tables/pca_embeddings.csv")
VARIANCE_PATH = Path("results/tables/pca_explained_variance.csv")

OUTPUT_PATH = Path("results/plots/pca_embedding_scatter.png")
REPORT_PATH = Path("results/reports/f5_pca_plot_report.txt")


def variance_for(variance: pd.DataFrame, component: str) -> float:
    return variance.loc[
        variance["component"] == component,
        "explained_variance_ratio",
    ].iloc[0]


def main() -> None:

    embeddings = pd.read_csv(EMBEDDING_PATH)
    variance = pd.read_csv(VARIANCE_PATH)

    pc1_var = variance_for(variance, "pc1")
    pc2_var = variance_for(variance, "pc2")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    ax.scatter(
        embeddings["pc1"],
        embeddings["pc2"],
        s=35,
    )

    # annotate atoms because there are only 48 points; still readable enough
    for _, row in embeddings.iterrows():
        ax.annotate(
            str(int(row["na_index"])),
            (row["pc1"], row["pc2"]),
            textcoords="offset points",
            xytext=(3, 3),
            fontsize=6,
        )

    ax.set_xlabel(f"PC1 ({pc1_var:.1%} variance)")
    ax.set_ylabel(f"PC2 ({pc2_var:.1%} variance)")
    ax.set_title("PCA projection of Na mobility features")
    ax.grid(True, linewidth=0.4, alpha=0.5)

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=200)
    plt.close(fig)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("F5 PCA plot generation: COMPLETE\n")
        f.write(f"input embeddings: {EMBEDDING_PATH}\n")
        f.write(f"input explained variance: {VARIANCE_PATH}\n")
        f.write(f"output: {OUTPUT_PATH}\n")
        f.write(f"points plotted: {len(embeddings)}\n")
        f.write(f"pc1 explained variance ratio: {pc1_var}\n")
        f.write(f"pc2 explained variance ratio: {pc2_var}\n")
        f.write(f"output bytes: {OUTPUT_PATH.stat().st_size}\n")

    print(f"F5 complete: wrote PCA plot to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
