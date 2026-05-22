from pathlib import Path

import pandas as pd


XDATCAR_PATH = Path("data/XDATCAR")
OUTPUT_PATH = Path("results/tables/na_coordinates.csv")


def read_header(path: Path):
    # only need the VASP header here, not the whole huge file
    with open(path, "r", encoding="utf-8") as f:
        lines = [next(f).strip() for _ in range(7)]

    species = lines[5].split()
    counts = [int(x) for x in lines[6].split()]

    if "Na" not in species:
        raise ValueError("No Na species found in XDATCAR header.")

    na_species_index = species.index("Na")

    na_count = counts[na_species_index]
    na_start = sum(counts[:na_species_index])
    na_end = na_start + na_count

    total_atoms = sum(counts)

    return species, counts, na_start, na_end, na_count, total_atoms


def extract_na_from_frame(
    frame: int,
    coordinate_rows: list[str],
    na_start: int,
    na_end: int,
    total_atoms: int,
) -> list[tuple[int, int, float, float, float]]:

    if len(coordinate_rows) < total_atoms:
        raise ValueError(
            f"Frame {frame} has {len(coordinate_rows)} coordinate rows; "
            f"expected {total_atoms}."
        )

    output = []

    for na_index, row in enumerate(coordinate_rows[na_start:na_end]):
        parts = row.split()

        if len(parts) < 3:
            raise ValueError(
                f"Frame {frame}, Na index {na_index} has malformed "
                f"coordinate row: {row}"
            )

        x, y, z = map(float, parts[:3])

        output.append((frame, na_index, x, y, z))

    return output


def extract_na_coordinates(path: Path) -> pd.DataFrame:

    species, counts, na_start, na_end, na_count, total_atoms = read_header(path)

    rows = []
    frame = None
    coordinate_rows = []

    with open(path, "r", encoding="utf-8") as f:

        for raw_line in f:
            line = raw_line.strip()

            if line.startswith("Direct configuration="):

                if frame is not None:
                    rows.extend(
                        extract_na_from_frame(
                            frame,
                            coordinate_rows,
                            na_start,
                            na_end,
                            total_atoms,
                        )
                    )

                frame = int(line.split("=")[-1])
                coordinate_rows = []

            elif frame is not None and line:
                coordinate_rows.append(line)

        # final frame at EOF
        if frame is not None:
            rows.extend(
                extract_na_from_frame(
                    frame,
                    coordinate_rows,
                    na_start,
                    na_end,
                    total_atoms,
                )
            )

    df = pd.DataFrame(
        rows,
        columns=["frame", "na_index", "x", "y", "z"],
    )

    return df


def main() -> None:

    df = extract_na_coordinates(XDATCAR_PATH)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False)

    # no report here for now; validation stage handles the sanity checks
    print(
        f"B1 complete: wrote {len(df)} Na coordinate rows "
        f"to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
