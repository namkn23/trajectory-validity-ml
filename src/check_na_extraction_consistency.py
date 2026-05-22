from pathlib import Path
import hashlib
import subprocess
import sys


CSV_PATH = Path("results/tables/na_coordinates.csv")


def sha256(path: Path) -> str:
    # small helper, kept separate because I may reuse this in other checks
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def main() -> None:

    script = Path("src/extract_na_coordinates.py")

    # first run
    subprocess.run(
        [sys.executable, str(script)],
        check=True
    )

    first_run = sha256(CSV_PATH)

    # run again and make sure the output is identical
    # this catches accidental non-deterministic extraction / ordering issues
    subprocess.run([sys.executable, str(script)], check=True)

    second_run = sha256(CSV_PATH)

    if first_run != second_run:
        msg = (
            "B3 failed: na_coordinates.csv hash changed between reruns: "
            f"{first_run} != {second_run}"
        )
        raise SystemExit(msg)

    out = Path("results/reports/na_extraction_rerun_test.txt")
    out.parent.mkdir(parents=True, exist_ok=True)

    # very plain report, just enough for the pipeline log
    report = (
        "B3 Na extraction rerun test: PASS\n"
        "\n"
        f"na_coordinates.csv sha256: {second_run}\n"
    )

    out.write_text(report, encoding="utf-8")

    # leaving this print short because this is usually called inside pipeline
    print("B3 Na extraction rerun test: PASS")


if __name__ == "__main__":
    main()
