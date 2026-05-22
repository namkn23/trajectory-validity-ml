from pathlib import Path

import pandas as pd


XDATCAR_PATH = Path("data/XDATCAR")

TABLE_PATH = Path("results/tables/xdatcar_audit.csv")
REPORT_PATH = Path("results/reports/xdatcar_audit.txt")


def parse_xdatcar(path: Path) -> dict:
    # read as plain text; errors="replace" is mostly just paranoia
    with path.open("r", encoding="utf-8", errors="replace") as f:
        lines = [line.strip() for line in f]

    if len(lines) < 8:
        raise ValueError("XDATCAR is too short to contain a valid VASP header.")

    # basic VASP header bits
    scale = float(lines[1].split()[0])

    species = lines[5].split()
    counts = [int(x) for x in lines[6].split()]

    if len(species) != len(counts):
        raise ValueError(
            "Number of species labels does not match number of atom counts."
        )

    total_atoms = sum(counts)

    # each MD frame starts with this marker in XDATCAR
    frame_indices = [
        i for i, line in enumerate(lines)
        if line.startswith("Direct configuration=")
    ]

    malformed_frames = 0
    bad_coordinate_rows = 0

    for idx in frame_indices:
        block = lines[idx + 1: idx + 1 + total_atoms]

        if len(block) != total_atoms:
            malformed_frames += 1
            continue

        for row in block:
            parts = row.split()

            if len(parts) < 3:
                bad_coordinate_rows += 1
                malformed_frames += 1
                break

            try:
                coords = [
                    float(parts[0]),
                    float(parts[1]),
                    float(parts[2]),
                ]
            except ValueError:
                bad_coordinate_rows += 1
                malformed_frames += 1
                break

            # fractional coords should basically live in [0,1]
            # allow tiny numerical edge noise so we don't flag harmless rows
            if not all(-1e-8 <= value <= 1.0 + 1e-8 for value in coords):
                bad_coordinate_rows += 1
                malformed_frames += 1
                break

    results = {
        "source_file": str(path),
        "scale": scale,
        "species": " ".join(species),
        "counts": " ".join(str(x) for x in counts),
        "total_atoms": total_atoms,
        "frame_count": len(frame_indices),
        "coordinate_rows_per_frame_expected": total_atoms,
        "malformed_frames": malformed_frames,
        "bad_coordinate_rows": bad_coordinate_rows,
    }

    return results


def write_outputs(results: dict) -> None:
    # make folders in case the repo was freshly cloned
    TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([results]).to_csv(TABLE_PATH, index=False)

    # simple text report for quick checking without opening the csv
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("XDATCAR structural audit\n")
        f.write("=======================\n\n")

        for key, value in results.items():
            f.write(f"{key}: {value}\n")


def main() -> None:
    results = parse_xdatcar(XDATCAR_PATH)

    write_outputs(results)

    print("A1 audit complete")
    print(results)


if __name__ == "__main__":
    main()
