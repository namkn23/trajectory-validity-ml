from pathlib import Path

import pandas as pd
from sklearn.decomposition import PCA


INPUT_PATH = Path("results/tables/ml_input_scaled.csv")

EMBEDDING_OUTPUT_PATH = Path("results/tables/pca_embeddings.csv")
VARIANCE_OUTPUT_PATH = Path("results/tables/pca_explained_variance.csv")

REPORT_PATH = Path("results/reports/f3_pca_report.txt")


N_COMPONENTS = 2


def main() -> None:

    df = pd.read_csv(INPUT_PATH)

    feature_columns = [
        column for column in df.columns
        if column != "na_index"
    ]

    x = df[feature_columns].to_numpy()

    pca = PCA(n_components=N_COMPONENTS)
    embedding = pca.fit_transform(x)

    embeddings = pd.DataFrame(
        {
            "na_index": df["na_index"],
            "pc1": embedding[:, 0],
            "pc2": embedding[:, 1],
        }
    )

    explained = pd.DataFrame(
        {
            "component": ["pc1", "pc2"],
            "explained_variance_ratio": pca.explained_variance_ratio_,
        }
    )

    EMBEDDING_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VARIANCE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    embeddings.to_csv(EMBEDDING_OUTPUT_PATH, index=False)
    explained.to_csv(VARIANCE_OUTPUT_PATH, index=False)

    variance_sum = pca.explained_variance_ratio_.sum()

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("F3 PCA computation: COMPLETE\n")
        f.write(f"input: {INPUT_PATH}\n")
        f.write(f"embedding output: {EMBEDDING_OUTPUT_PATH}\n")
        f.write(f"explained variance output: {VARIANCE_OUTPUT_PATH}\n")
        f.write(f"rows: {len(embeddings)}\n")
        f.write(f"features used: {len(feature_columns)}\n")
        f.write(
            f"pc1 explained variance ratio: "
            f"{pca.explained_variance_ratio_[0]}\n"
        )
        f.write(
            f"pc2 explained variance ratio: "
            f"{pca.explained_variance_ratio_[1]}\n"
        )
        f.write(
            f"two-component explained variance ratio sum: {variance_sum}\n"
        )

    # PCA is just a diagnostic projection here, not a classifier
    print("F3 PCA computation: COMPLETE")


if __name__ == "__main__":
    main()
