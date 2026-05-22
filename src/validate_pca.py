from pathlib import Path

import numpy as np
import pandas as pd


EMBEDDING_PATH = Path("results/tables/pca_embeddings.csv")
VARIANCE_PATH = Path("results/tables/pca_explained_variance.csv")
REPORT_PATH = Path("results/reports/f4_pca_validation.txt")


EXPECTED_ROWS = 48
EXPECTED_EMBEDDING_COLUMNS = ["na_index", "pc1", "pc2"]
EXPECTED_VARIANCE_COLUMNS = ["component", "explained_variance_ratio"]


def main() -> None:

    embeddings = pd.read_csv(EMBEDDING_PATH)
    variance = pd.read_csv(VARIANCE_PATH)

    failures = []

    if list(embeddings.columns) != EXPECTED_EMBEDDING_COLUMNS:
        failures.append(
            f"Unexpected PCA embedding columns: {list(embeddings.columns)}"
        )

    if list(variance.columns) != EXPECTED_VARIANCE_COLUMNS:
        failures.append(
            f"Unexpected PCA variance columns: {list(variance.columns)}"
        )

    if len(embeddings) != EXPECTED_ROWS:
        failures.append(
            f"Unexpected PCA embedding row count: {len(embeddings)} != {EXPECTED_ROWS}"
        )

    if embeddings["na_index"].nunique() != EXPECTED_ROWS:
        failures.append("PCA embeddings do not contain 48 unique Na indices.")

    if len(variance) != 2:
        failures.append(
            f"Unexpected explained variance row count: {len(variance)} != 2"
        )

    if list(variance["component"]) != ["pc1", "pc2"]:
        failures.append(
            f"Unexpected PCA component labels: {list(variance['component'])}"
        )

    embedding_values = embeddings[["pc1", "pc2"]].to_numpy()
    variance_values = variance["explained_variance_ratio"].to_numpy()

    if not np.isfinite(embedding_values).all():
        failures.append("PCA embeddings contain non-finite values.")

    if not np.isfinite(variance_values).all():
        failures.append("PCA explained variance contains non-finite values.")

    if not ((variance_values >= 0) & (variance_values <= 1)).all():
        failures.append("PCA explained variance ratios must be within [0, 1].")

    variance_sum = float(variance_values.sum())

    if variance_sum > 1.0 + 1e-12:
        failures.append(
            f"PCA explained variance ratio sum exceeds 1: {variance_sum}"
        )

    if variance_sum <= 0:
        failures.append("PCA explained variance ratio sum is not positive.")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "F4 PCA validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )
        raise SystemExit("F4 PCA validation failed. See report.")

    # keep this verbose because PCA mistakes are annoying to diagnose later
    REPORT_PATH.write_text(
        "F4 PCA validation: PASS\n"
        f"embedding rows: {len(embeddings)}\n"
        f"variance rows: {len(variance)}\n"
        f"pc1 explained variance ratio: {variance_values[0]}\n"
        f"pc2 explained variance ratio: {variance_values[1]}\n"
        f"two-component explained variance ratio sum: {variance_sum}\n",
        encoding="utf-8",
    )

    print("F4 PCA validation: PASS")


if __name__ == "__main__":
    main()
