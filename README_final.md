# trajectory-validity-ml



This repository basically tries to really investigate the physical realism of the trajectories before accepting the data as is. Basic ML tools are used to diagnose possible inconsistencies and unphysical ion movement in the trajectories





The trajectory data XDATCAR used here comes from DFT-based atomistic simulations.







This repository analyzes Na motion in an atomistic trajectory using a deliberately simple workflow:   parse the trajectory, validate intermediate data, compute physically interpretable mobility features, and apply a layer of basic diagnostic ML only after the trajectory passes various "checks"



The current example system is a pristine Na-Sb-S trajectory with 48 Na atoms over 3929 frames.

## Repository structure

```text
trajectory-validity-ml/
├── data/
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

### A — XDATCAR audit

   Checks the trajectory structure and basic consistency.

Outputs:

- `results/tables/xdatcar_audit.csv`
- `results/reports/xdatcar_audit.txt`

### B — Na coordinate extraction

Extracts Na fractional coordinates and validates the extracted table.

Outputs:

- `results/tables/na_coordinates.csv`
- `results/reports/na_coordinates_validation.txt`

For the current trajectory this corresponds to 3929 frames with 48 Na atoms tracked per frame.

### C — periodic-boundary step diagnostics

Computes frame-to-frame Na displacements using minimum-image wrapping.

Outputs:

- `results/tables/na_periodic_steps.csv`
- `results/tables/suspicious_jumps.csv`
- `results/reports/step_statistics_validation.txt`

The suspicious-jump table is mainly intended as a quick diagnostic check for relatively large step events.

### D — mobility features

Computes atom-level and frame-level mobility descriptors.

Outputs:

- displacement features
- step statistics
- mobility spread features
- assembled feature tables

### E — diagnostic plots

Generates plots from validated feature tables.

Outputs include:

- MSD plots
- displacement plots
- step histograms
- plot validation reports

### F — lightweight ML diagnostics

Runs PCA and Isolation Forest on the atom-level feature table.

Outputs:

- PCA embeddings
- anomaly scores
- ranked anomaly tables
- PCA/anomaly plots

PCA is mainly used as a compact projection of the feature space.

## Running the repository

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the default pipeline check:

```bash
python run_pipeline.py
```

This mode only checks whether expected outputs already exist.

To regenerate all outputs:

```bash
python run_pipeline.py --force
```

## Reproducibility checks

\## Reproducibility checks



Several stages include rerun consistency checks:

\- \`src/test\_audit\_rerun.py\`



\- \`src/check\_na\_extraction\_consistency.py\`



\- \`src/validate\_step\_outputs.py\`



\- \`src/feature\_rerun\_check.py\`

## Limitations

- Na-only V1
- Uses fractional-coordinate displacement features
- No force or energy validation
- No local-environment analysis
- No direct MLFF validation metrics

## Possible extensions

- coordination analysis
- RDF diagnostics
- force/energy consistency checks
- comparison across doped trajectories


