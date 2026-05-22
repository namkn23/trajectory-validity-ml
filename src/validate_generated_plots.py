from pathlib import Path

from PIL import Image


REPORT_PATH = Path("results/reports/plot_validation.txt")


EXPECTED_PLOTS = [
    Path("results/plots/msd_by_na_atom.png"),
    Path("results/plots/mean_displacement_by_na_atom.png"),
    Path("results/plots/max_displacement_by_na_atom.png"),
    Path("results/plots/step_magnitude_histogram.png"),
    Path("results/plots/atom_msd_histogram.png"),
    Path("results/plots/atom_mean_step_histogram.png"),
]


def validate_png(path: Path) -> tuple[int, tuple[int, int]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing plot file: {path}")

    size_bytes = path.stat().st_size

    if size_bytes == 0:
        raise ValueError(f"Plot file is empty: {path}")

    # Pillow's verify() checks file integrity but does not leave a normal image object
    with Image.open(path) as image:
        image.verify()

    with Image.open(path) as image:
        width, height = image.size

    if width <= 0 or height <= 0:
        raise ValueError(f"Plot has invalid dimensions: {path}")

    return size_bytes, (width, height)


def main() -> None:

    failures = []
    report_lines = ["E4 generated plot validation: PASS"]

    for plot_path in EXPECTED_PLOTS:

        try:
            size_bytes, dimensions = validate_png(plot_path)

            report_lines.append(
                f"{plot_path}: readable PNG, bytes={size_bytes}, "
                f"size={dimensions[0]}x{dimensions[1]}"
            )

        except Exception as exc:
            failures.append(f"{plot_path}: {exc}")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if failures:
        REPORT_PATH.write_text(
            "E4 generated plot validation: FAIL\n"
            + "\n".join(failures)
            + "\n",
            encoding="utf-8",
        )

        raise SystemExit("E4 plot validation failed. See report.")

    REPORT_PATH.write_text(
        "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )

    print("E4 generated plot validation: PASS")


if __name__ == "__main__":
    main()
