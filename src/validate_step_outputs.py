from pathlib import Path
import hashlib
import subprocess
import sys


STEP_TABLE = Path("results/tables/na_periodic_steps.csv")
SUSPICIOUS_TABLE = Path("results/tables/suspicious_jumps.csv")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_hashes() -> dict[str, str]:
    # keep the short names in the report, easier to read
    return {
        "na_periodic_steps.csv": sha256(STEP_TABLE),
        "suspicious_jumps.csv": sha256(SUSPICIOUS_TABLE),
    }


def run_script(script_name: str) -> None:
    subprocess.run(
        [sys.executable, f"src/{script_name}"],
        check=True,
    )


def main() -> None:

    before = snapshot_hashes()

    # rerun the C-stage outputs and make sure nothing moves around
    for script in [
        "compute_periodic_boundary_steps.py",
        "validate_step_statistics.py",
        "detect_suspicious_jumps.py",
    ]:
        run_script(script)

    after = snapshot_hashes()

    if before != after:
        msg = (
            "C4 failed: output hashes changed after rerun: "
            f"{before} != {after}"
        )
        raise SystemExit(msg)

    out = Path("results/reports/step_pipeline_rerun_test.txt")
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "C4 step pipeline rerun test: PASS",
        "Method: compared existing C-stage output hashes against hashes after one full C1-C3 rerun.",
        f"na_periodic_steps.csv sha256: {after['na_periodic_steps.csv']}",
        f"suspicious_jumps.csv sha256: {after['suspicious_jumps.csv']}",
    ]

    out.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("C4 step pipeline rerun test: PASS")


if __name__ == "__main__":
    main()
