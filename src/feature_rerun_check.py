from pathlib import Path
import hashlib
import subprocess
import sys


# outputs from the D-stage feature pipeline
OUTPUT_FILES = [
    Path("results/tables/displacement_features.csv"),
    Path("results/tables/step_features.csv"),
    Path("results/tables/mobility_spread_features.csv"),
    Path("results/tables/atom_features.csv"),
    Path("results/tables/frame_features.csv"),
]


def sha256(path: Path) -> str:
    # hash the file contents exactly as written
    # this is deliberately a blunt reproducibility check
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_hashes() -> dict[str, str]:
    hashes = {}

    for path in OUTPUT_FILES:
        hashes[str(path)] = sha256(path)

    return hashes


def run_stage(script_name: str) -> None:
    subprocess.run(
        [sys.executable, f"src/{script_name}"],
        check=True,
    )


def main() -> None:

    before = snapshot_hashes()

    # rerun the feature stage in the same order as the pipeline
    # if any of these scripts changes output ordering, the hash check should catch it
    feature_scripts = [
        "compute_displacement_features.py",
        "compute_step_features.py",
        "compute_mobility_spread_features.py",
        "assemble_feature_tables.py",
        "validate_feature_tables.py",
    ]

    for script in feature_scripts:
        run_stage(script)

    after = snapshot_hashes()

    if before != after:
        msg = (
            "D6 failed: feature output hashes changed after rerun: "
            f"{before} != {after}"
        )
        raise SystemExit(msg)

    out = Path("results/reports/feature_pipeline_rerun_test.txt")
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = ["D6 feature pipeline rerun test: PASS"]

    for path, digest in after.items():
        lines.append(f"{path} sha256: {digest}")

    out.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("D6 feature pipeline rerun test: PASS")


if __name__ == "__main__":
    main()
