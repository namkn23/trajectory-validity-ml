from pathlib import Path
import hashlib
import subprocess
import sys


TABLE_PATH = Path("results/tables/xdatcar_audit.csv")
REPORT_PATH = Path("results/reports/xdatcar_audit.txt")


def sha256(path: Path) -> str:
    # very blunt reproducibility check
    # if rerunning the audit changes either file hash,
    # then something nondeterministic is happening somewhere
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_audit() -> None:
    subprocess.run(
        [sys.executable, "src/audit_xdatcar_structure.py"],
        check=True,
    )


def snapshot_hashes() -> dict[str, str]:

    # keeping this as a tiny helper because I ended up
    # repeating the same thing twice while debugging
    return {
        "table": sha256(TABLE_PATH),
        "report": sha256(REPORT_PATH),
    }


def main() -> None:

    # first run
    run_audit()
    first = snapshot_hashes()

    # rerun immediately and compare hashes
    # this is intentionally a strict equality check
    run_audit()
    second = snapshot_hashes()

    if first != second:

        raise SystemExit(
            "A2 failed: rerun hashes differ: "
            f"{first} != {second}"
        )

    out = Path("results/reports/audit_rerun_test.txt")
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "A2 audit rerun test: PASS",
        f"xdatcar_audit.csv sha256: {second['table']}",
        f"xdatcar_audit.txt sha256: {second['report']}",
    ]

    out.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("A2 audit rerun test: PASS")


if __name__ == "__main__":
    main()
