# trajectory-validity-ml

Lightweight validation-first trajectory diagnostics for VASP `XDATCAR` files.

This repository analyzes Na motion in an atomistic trajectory using a deliberately simple workflow:
parse the trajectory, validate intermediate data, compute physically interpretable mobility features,
and then apply lightweight diagnostic ML only after the basic trajectory checks pass.

The current example trajectory is a pristine Na-Sb-S system with 48 Na atoms over 3929 frames.

## Design philosophy

- Use simple intermediate CSV files rather than opaque binary formats.
- Keep each script focused on one task.
- Validate outputs immediately after generation.
- Prefer physically interpretable quantities before applying ML.
- Treat ML outputs as diagnostic flags for inspection, not proof of physical correctness.
- Keep the workflow easy to rerun and debug.

## Repository structure

```text
trajectory-validity-ml/
├── data/
│   └── XDATCAR
├── src/
├── tests/
├── results/
│   ├── tables/
│   ├── plots/
│   └── reports/
├── docs/
├── requirements.txt
├── README.md
└── run_pipeline.py
```

## Workflow overview

The workflow is split into small stages.

### A — XDATCAR audit

Checks the basic structure of the trajectory file:

- species and atom counts
- total atom count
- number of frames
- coordinate rows per frame
- malformed coordinate blocks

Main outputs:

- `results/tables/xdatcar_audit.csv`
- `results/reports/xdatcar_audit.txt`

### B — Na coordinate extraction

Extracts only Na fractional coordinates and validates the extracted coordinate table.

Main outputs:

- `results/tables/na_coordinates.csv`
- `results/reports/na_coordinates_validation.txt`

For the current trajectory, this table contains 188592 rows, corresponding to 3929 frames and 48 Na atoms per frame.

### C — periodic-boundary step diagnostics

Computes frame-to-frame Na displacements using the minimum-image convention in fractional coordinates.

Main outputs:

- `results/tables/na_periodic_steps.csv`
- `results/tables/suspicious_jumps.csv`
- `results/reports/step_statistics_validation.txt`
- `results/reports/suspicious_jump_report.txt`

The suspicious-jump table is a diagnostic list of relatively large step events. These events are not automatically treated as physical errors.

### D — physically interpretable mobility features

Computes atom-level and frame-level mobility descriptors.

Main outputs:

- `results/tables/displacement_features.csv`
- `results/tables/step_features.csv`
- `results/tables/mobility_spread_features.csv`
- `results/tables/atom_features.csv`
- `results/tables/frame_features.csv`

The features include:

- mean squared displacement in fractional-coordinate units
- mean displacement from the initial position
- maximum displacement from the initial position
- mean step magnitude
- maximum step magnitude
- step-magnitude standard deviation

### E — diagnostic plots

Generates basic plots from validated CSV outputs.

Main outputs:

- `results/plots/msd_by_na_atom.png`
- `results/plots/mean_displacement_by_na_atom.png`
- `results/plots/max_displacement_by_na_atom.png`
- `results/plots/step_magnitude_histogram.png`
- `results/plots/atom_msd_histogram.png`
- `results/plots/atom_mean_step_histogram.png`
- `results/reports/plot_validation.txt`

### F — lightweight ML diagnostics

Applies simple ML methods to the validated atom-level feature table.

Main outputs:

- `results/tables/ml_input_scaled.csv`
- `results/tables/pca_embeddings.csv`
- `results/tables/pca_explained_variance.csv`
- `results/tables/anomaly_scores.csv`
- `results/tables/anomaly_score_ranking.csv`
- `results/tables/flagged_anomalies.csv`
- `results/plots/pca_embedding_scatter.png`
- `results/plots/pca_anomaly_overlay.png`
- `results/plots/anomaly_score_distribution.png`

PCA is used as a diagnostic projection of the feature space.
Isolation Forest is used to rank atoms with unusual mobility-feature combinations.
Flagged atoms should be inspected manually in the trajectory and feature tables.

## Running the repository

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the default pipeline check:

```bash
python run_pipeline.py
```

The default mode verifies that expected outputs already exist and are non-empty.
This is useful when working with a repository that already contains generated results.

To regenerate all stage outputs from scripts:

```bash
python run_pipeline.py --force
```

A full rebuild can take longer because it reparses the XDATCAR file and regenerates all tables and plots.

## Reproducibility checks

Several stages include hash-based rerun checks:

- `src/test_audit_rerun.py`
- `src/test_na_extraction_rerun.py`
- `src/test_step_pipeline_rerun.py`
- `src/test_feature_pipeline_rerun.py`

The corresponding reports are saved in `results/reports/`.

## Current results summary

For the included trajectory:

- species: Na, Sb, S
- atom counts: 48 Na, 16 Sb, 64 S
- total atoms: 128
- frames: 3929
- Na coordinate rows: 188592
- periodic step rows: 188544
- maximum periodic step magnitude: approximately 0.00109 in fractional-coordinate units
- atom feature rows: 48
- frame feature rows: 3928
- Isolation Forest flagged atoms: 5

These numbers are reported from saved output files in `results/tables/` and `results/reports/`.

## Interpretation notes

This repository is intended as a trajectory diagnostics toolkit.

It checks whether the parsed trajectory and Na mobility descriptors are internally consistent.
It can flag unusual behavior for inspection.
It does not prove that a simulation is physically correct.

The ML stages are deliberately lightweight and diagnostic. They summarize validated mobility features; they do not replace physical validation.

## Limitations

- Na-only V1.
- Uses fractional-coordinate displacement features.
- No force or energy validation.
- No temperature, timestep, or thermostat analysis.
- No full local-environment analysis.
- No coordination-number or cage analysis.
- No Voronoi/free-volume descriptors.
- No direct MLFF validation metrics.
- Anomaly detection is diagnostic, not proof of physical correctness.

# Future extensions

Possible extensions include:

- framework atom descriptors
- Na coordination and cage analysis
- Voronoi or free-volume descriptors
- RDF or van Hove correlation diagnostics
- force and energy consistency checks
- MLFF validation metric integration
- comparison across pristine, doped, and vacancy-containing trajectories
