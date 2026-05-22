# Methodology / Random Workflow Notes

This repo is basically a lightweight trajectory-inspection workflow for VASP XDATCAR files.

The main idea was:

- first make sure the trajectory itself is not obviously broken
- then compute some simple Na mobility quantities
- then apply lightweight ML only after the basic checks pass

The ML part is diagnostic only.

I did not want the workflow to pretend that ML automatically proves physical correctness.


---

## Input trajectory

Current input:

```text
data/XDATCAR
```

Current trajectory used here:

- Na / Sb / S system
- 48 Na atoms
- 16 Sb atoms
- 64 S atoms
- 128 total atoms
- 3929 frames

At the moment the workflow only tracks Na motion.


---

## XDATCAR audit

The first stage just checks whether the XDATCAR structure itself looks sane.

Things checked:

- species labels
- atom counts
- frame count
- expected coordinate rows
- malformed frames
- malformed coordinate rows

Outputs:

```text
results/tables/xdatcar_audit.csv
results/reports/xdatcar_audit.txt
```

This is mostly defensive checking before later stages.


---

## Na coordinate extraction

`extract_na_coordinates.py` extracts only Na fractional coordinates.

Output:

```text
results/tables/na_coordinates.csv
```

Current run:

```text
3929 frames × 48 Na atoms = 188592 rows
```

Validation checks include:

- correct Na count per frame
- no missing frames
- finite coordinate values
- coordinates inside `[0,1)`

Probably more validation than strictly necessary but useful while debugging.


---

## Periodic-boundary step calculation

Frame-to-frame Na motion is computed using a minimum-image convention.

Wrapped displacement:

```text
delta_wrapped = delta - round(delta)
```

Without this, periodic boundary crossings would look like fake giant jumps.

Step magnitude:

```text
step_frac = sqrt(dx_frac^2 + dy_frac^2 + dz_frac^2)
```

Output:

```text
results/tables/na_periodic_steps.csv
```

Current run:

```text
(3929 - 1) × 48 = 188544 rows
```

Checks include:

- finite values
- frame continuity
- nonnegative step sizes
- minimum-image bounds
- no obviously broken jumps


---

## Suspicious jump detection

This stage just flags unusually large frame-to-frame Na jumps.

A flagged event is NOT automatically an error.

It only means:

```text
this displacement looks relatively unusual compared to the rest
```

Current threshold:

```text
step_frac > 0.0009
```

Current run:

- 149 flagged events
- across 9 Na atoms

Output:

```text
results/tables/suspicious_jumps.csv
```


---

## Mobility features

The feature stage computes simple mobility descriptors.

Current atom-level features:

- mean squared displacement
- mean displacement
- max displacement
- final displacement
- mean step magnitude
- max step magnitude
- step standard deviation

Main output:

```text
results/tables/atom_features.csv
```

Frame-level summary output:

```text
results/tables/frame_features.csv
```

Nothing extremely fancy here.


---

## Plot generation

Plots are generated from saved CSV outputs.

Examples:

- MSD plots
- displacement plots
- histograms
- PCA projection
- anomaly score plots

There is also a simple PNG validation step to catch corrupted images.


---

## ML input preparation

The ML stage uses the validated atom-level feature table.

Current selected features:

- `msd_frac`
- `mean_displacement_frac`
- `max_displacement_frac`
- `final_displacement_frac`
- `mean_step_frac`
- `max_step_frac`
- `step_std_frac`

The features are scaled using `StandardScaler`.

Output:

```text
results/tables/ml_input_scaled.csv
```

Validation checks:

- finite values
- nonconstant features
- near-zero scaled means
- unit standard deviations


---

## PCA

PCA is used as a low-dimensional projection of the mobility-feature space.

Outputs:

```text
results/tables/pca_embeddings.csv
results/tables/pca_explained_variance.csv
```

Current run:

- PC1 ≈ 0.438 variance
- PC2 ≈ 0.304 variance
- combined ≈ 0.742 variance

Mainly used for visualization/inspection.


---

## Isolation Forest

Isolation Forest is applied to the scaled mobility features.

Output:

```text
results/tables/anomaly_scores.csv
```

Current settings:

```text
contamination = 0.10
random_state = 7
```

Current run flags 5 atoms.

A flagged atom means:

```text
this atom has an unusual mobility-feature combination
```

It does NOT automatically mean the atom is physically wrong.

The ranking is mainly intended to support manual inspection.


---

## Reproducibility checks

Some stages include rerun/hash checks.

Examples:

- audit rerun test
- extraction rerun test
- step pipeline rerun test
- feature rerun test

Reports are stored under:

```text
results/reports/
```

Mostly there to catch accidental output drift during reruns.


---

## Current limitations

Current limitations include:

- Na-only analysis
- no force validation
- no RDF analysis
- no coordination analysis
- no van Hove analysis
- no cage descriptors
- no direct MLFF validation metrics

The ML stage is intentionally lightweight.


---

## Possible future extensions

Possible next extensions:

- framework descriptors
- coordination metrics
- RDF / van Hove diagnostics
- force consistency checks
- pristine vs doped trajectory comparisons
- lightweight autoencoder anomaly scoring


---

## Practical summary

Overall workflow:

1. audit trajectory
2. extract Na coordinates
3. compute periodic-boundary-aware steps
4. validate motion statistics
5. compute mobility features
6. generate plots
7. apply lightweight ML
8. save outputs + rerun checks

So overall this repo is probably best viewed as:

```text
a lightweight trajectory-inspection workflow
```

rather than a complete physical validation framework.
