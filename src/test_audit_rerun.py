from pathlib import Path
import hashlib
import subprocess
import sys


TABLE_PATH = Path("results/tables/xdatcar_audit.csv")
REPORT_PATH = Path("results/reports/xdatcar_audit.txt")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_audit() -> None:
    subprocess.run(
        [sys.executable, "src/audit_xdatcar_structure.py"],
        check=True,
    )


def main() -> None:

    run_audit()
    first_run = {
        "table": sha256(TABLE_PATH),
        "report": sha256(REPORT_PATH),
    }

    run_audit()
    second_run = {
        "table": sha256(TABLE_PATH),
        "report": sha256(REPORT_PATH),
    }

    if first_run != second_run:
        raise SystemExit(
            f"A2 failed: rerun hashes differ: {first_run} != {second_run}"
        )

    out = Path("results/reports/audit_rerun_test.txt")
    out.parent.mkdir(parents=True, exist_ok=True)

    text = (
        "A2 audit rerun test: PASS\n"
        f"xdatcar_audit.csv sha256: {second_run['table']}\n"
        f"xdatcar_audit.txt sha256: {second_run['report']}\n"
    )

    out.write_text(text, encoding="utf-8")

    print("A2 audit rerun test: PASS")


if __name__ == "__main__":
    main()
