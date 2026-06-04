# Paper Completion Assets and Claim Boundary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the AeroConf paper additions needed to make the measured-mass-properties, structured correction, and simulation-claim boundary defensible.

**Architecture:** Treat the paper as a log-based real-flight effective-wrench correction paper, not a closed-loop simulation-validation paper. Add one editable vector pipeline figure, one representative held-out prediction curve, updated measured-mass-properties wording, updated measured-massprops results tables, and a conservative replay/limitations discussion.

**Tech Stack:** LaTeX (`main.tex`, `sections/*.tex`), editable SVG source exported to PDF for LaTeX inclusion, matplotlib or existing artifact figures for prediction curves, `latexmk -pdf main.tex` for verification.

---

## Evidence Sources

Use these result artifacts as the current measured-mass-properties branch:

- `/home/zn/flap-system-identification/artifacts/20260602_old_vs_measured_massprops_comparison/summary.md`
- `/home/zn/flap-system-identification/artifacts/20260602_old_vs_measured_massprops_comparison/seed_label_scale_delta_summary.json`
- `/home/zn/flap-system-identification/artifacts/20260602_old_vs_measured_massprops_comparison/old_vs_new_phase_structured_selected_test_metrics_pivot.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/evaluation/per_channel_metrics.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/phase_structured/force_metrics_by_split.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/phase_structured/moment_metrics_by_split.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/curves/prediction_curve_manifest.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_replay_measured_massprops_v1/alpha_only_replay_diagnostics/alpha_only_replay_summary.csv`

Use these manuscript files:

- `main.tex`
- `sections/02_dataset.tex`
- `sections/03_method.tex`
- `sections/04_experiments.tex`
- `sections/05_results.tex`
- `sections/06_conclusion.tex`
- `research_notes/mass_properties_measurement_notes.md`

Main claim boundary:

- Strong claim allowed: log-conditioned corrected effective-wrench prediction improves force-channel agreement with real-flight labels.
- Strong claim allowed: measured mass properties make the label definition more physically grounded.
- Strong claim allowed: residual/correction terms show repeatable phase/condition structure.
- Weak/conservative claim only: replay is a diagnostic; it does not validate a closed-loop or full six-degree-of-freedom simulator.
- Do not claim: RL controller training, validated IsaacLab closed-loop deployment, or exact open-loop trajectory replay.

---

### Task 1: Create a Claim-Evidence Note for the New Paper Version

**Files:**

- Create: `research_notes/20260602_measured_massprops_completion_claim_evidence.md`

**Step 1: Write a compact claim-evidence note**

Create a Markdown note with these sections:

- `Current Paper Identity`
- `Claims We Can Make`
- `Claims We Must Avoid`
- `Evidence Table`
- `Numbers to Use`
- `Numbers Not to Mix`

Required content:

- Record force test metrics:
  - `fx_b`: RMSE `1.41888`, MAE `1.05494`, R2 `0.899346`, RMSE/std `0.31726`
  - `fy_b`: RMSE `0.888775`, MAE `0.640577`, R2 `0.276439`, RMSE/std `0.850624`
  - `fz_b`: RMSE `2.62389`, MAE `1.98471`, R2 `0.908929`, RMSE/std `0.301779`
- Record moment test metrics:
  - `mx_b`: RMSE `0.591617`, MAE `0.433001`, R2 `0.224088`, RMSE/std `0.880859`
  - `my_b`: RMSE `0.281844`, MAE `0.219681`, R2 `0.798385`, RMSE/std `0.449016`
  - `mz_b`: RMSE `0.220901`, MAE `0.168601`, R2 `0.262573`, RMSE/std `0.858736`
- Record force RMSE reductions from calibrated prior:
  - `fx_b`: `68.3%`
  - `fy_b`: `15.0%`
  - `fz_b`: `69.8%`
- Record label-scale changes:
  - force std ratio new/old `0.951737`
  - `mx_b` std ratio `230.852`
  - `my_b` std ratio `148.272`
  - `mz_b` std ratio `551.007`
- Record replay boundary:
  - smoothed-alpha and moment-inferred-alpha are algebraically identical to about `2.6e-15 rad/s^2`
  - smoothed-alpha trapezoid replay body-rate median error remains nonzero: `0.135 rad/s` at `0.10 s`, `0.118 rad/s` at `0.25 s`, `0.128 rad/s` at `0.50 s`, `0.139 rad/s` at `1.00 s`

**Step 2: Verify evidence anchors**

Run:

```bash
sed -n '1,220p' /home/zn/flap-system-identification/artifacts/20260602_old_vs_measured_massprops_comparison/summary.md
```

Expected: the numbers above are present or traceable from the summary and associated CSV files.

---

### Task 2: Add an Editable Pipeline Figure Source

**Files:**

- Create: `figures/real_flight_correction_pipeline.svg`
- Create: `figures/real_flight_correction_pipeline.pdf`
- Optional create: `figures/real_flight_correction_pipeline.png`
- Modify: `sections/02_dataset.tex` or `sections/03_method.tex`

**Design requirement:**

The pipeline figure must be editable as a vector source. Do not use a raster-only image. The canonical source is:

```text
figures/real_flight_correction_pipeline.svg
```

The SVG must use editable SVG elements:

- `<rect>` for blocks
- `<text>` for text labels
- `<path>` or `<line>` for arrows
- no text converted to outlines
- no embedded raster images

The LaTeX paper should include the exported PDF:

```latex
\includegraphics[width=\textwidth]{figures/real_flight_correction_pipeline.pdf}
```

**Figure content:**

Use a left-to-right `figure*` pipeline with these blocks:

1. `Outdoor Flight Platform`
   - PX4 logs
   - state estimates
   - airdata
   - actuator commands
   - flapping phase/frequency
2. `Preprocessing`
   - whole-log split
   - resampling
   - time alignment
   - smoothing
3. `Effective-Wrench Labels`
   - measured mass
   - measured CG
   - measured inertia
   - force/moment reconstruction
4. `DeLaurier-Style Prior`
   - fast low-dimensional simulator prior
   - bounded force calibration
5. `Structured Correction`
   - phase terms
   - airspeed/AoA/frequency
   - controls and body rates
   - deployable inputs only
6. `Diagnostics and Use`
   - corrected effective-wrench map
   - residual phase/condition structure
   - replay as diagnostic only

Add one small side note under the final blocks:

```text
Validated here: log-conditioned effective-wrench prediction.
Not claimed here: closed-loop simulator validation.
```

**Step 1: Create SVG**

Use either manual SVG or a small script. If using a script, keep the SVG as the editable source and avoid converting text to paths.

**Step 2: Export PDF**

Try:

```bash
inkscape figures/real_flight_correction_pipeline.svg \
  --export-type=pdf \
  --export-filename=figures/real_flight_correction_pipeline.pdf
```

Fallback if Inkscape is unavailable:

```bash
python -m cairosvg figures/real_flight_correction_pipeline.svg \
  -o figures/real_flight_correction_pipeline.pdf
```

**Step 3: Insert in paper**

Preferred placement: end of `sections/02_dataset.tex`, after preprocessing/model-input description, or beginning of `sections/03_method.tex` before the DeLaurier prior subsection.

Suggested LaTeX:

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/real_flight_correction_pipeline.pdf}
  \caption{Real-flight data pathway used to correct the low-dimensional flapping-wing simulator prior. The pipeline reconstructs effective-wrench labels from outdoor PX4 logs using measured mass properties, aligns them with a calibrated DeLaurier-style force prior, and learns a structured correction from simulator-available inputs. The validation in this paper is log-conditioned effective-wrench prediction; replay is used only as a diagnostic and does not constitute closed-loop simulator validation.}
  \label{fig:real_flight_correction_pipeline}
\end{figure*}
```

**Step 4: Visual check**

Run:

```bash
pdfinfo figures/real_flight_correction_pipeline.pdf
```

Expected: file exists and has a single page.

---

### Task 3: Add a Representative Held-Out Prediction Curve

**Files:**

- Create or modify: `scripts/make_prediction_curve_figure.py`
- Create: `figures/heldout_force_prediction_curve.pdf`
- Optional create: `figures/heldout_force_prediction_curve.png`
- Modify: `sections/05_results.tex`

**Step 1: Select one held-out log**

Use the existing manifest:

```bash
sed -n '1,80p' /home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/curves/prediction_curve_manifest.csv
```

Pick one log whose force channels are visually representative rather than cherry-picked for best performance. Prefer an overview or a moderate zoom from:

```text
/home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/curves/
```

**Step 2: Generate a paper-ready figure**

If using the existing PNGs is enough for draft review, copy one overview PNG into `figures/`. For final paper quality, regenerate from:

```text
/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/evaluation/aligned/test_phase_structured_aligned.parquet
```

The plot should include three force channels only:

- `fx_b`
- `fy_b`
- `fz_b`

Each panel should show:

- effective-wrench label
- calibrated prior
- phase-structured corrected prediction

Do not make moment channels the main visual evidence. Moment can be discussed in text or table.

**Step 3: Insert in `sections/05_results.tex`**

Place in `Calibration and Residual Prediction Performance` before or after the main per-channel table.

Suggested caption:

```latex
\caption{Representative held-out log segment comparing reconstructed effective-force labels, calibrated DeLaurier-style prior predictions, and the phase-structured correction. The plot is a log-conditioned prediction diagnostic rather than an open-loop trajectory replay.}
```

**Step 4: Verify figure inclusion**

Run:

```bash
latexmk -pdf main.tex
```

Expected: no missing-file warning for `heldout_force_prediction_curve.pdf`.

---

### Task 4: Update the Measured Mass-Properties Description in Section 2

**Files:**

- Modify: `sections/02_dataset.tex`
- Reference: `research_notes/mass_properties_measurement_notes.md`
- Reference: `/home/zn/flap-system-identification/metadata/aircraft/flapper_01/aircraft_metadata.yaml`

**Step 1: Add a concise measurement paragraph**

In `Effective-Wrench Reconstruction`, describe the measurement sources:

- mass and horizontal CG from four-point weighing at landing-gear contact points
- vertical CG from suspension/plumb-line geometry
- wing inertial measurement from bifilar-pendulum measurements where feasible
- body inertial measurement from bifilar-pendulum measurements
- assembled aircraft inertia from measured body and wing components at the neutral wing pose

Keep this concise. Do not turn the paper into a measurement-method paper.

**Step 2: Add measured values**

Use values from metadata where available. If any final value is still uncertain, mark it visibly in red with the existing `\textcolor{red}{...}` convention.

Values already used in the current metadata branch:

```text
mass = 0.90415 kg
cg_b_m = [-0.12154, 0.00541, -0.04298] m relative to IMU-origin FRD metadata frame
inertia_b_kg_m2 diagonal approximately [0.02329, 0.02573, 0.04270]
```

Check whether Section 2 currently defines the body frame as CG-attached or metadata/IMU-origin attached. If both appear, make the wording consistent:

- labels and prior wrench are reported about the CG reference point
- measured CG is needed to define the CG reference and any transforms from metadata/IMU-origin measurements

**Step 3: Add one sentence about moment sensitivity**

Add:

```text
The moment labels are correspondingly more sensitive than the force labels to inertia, CG/reference-point consistency, and angular-acceleration smoothing; therefore moment results are interpreted as effective rotational-wrench prediction rather than isolated aerodynamic moment measurement.
```

Rewrite in final paper prose, not as a raw note.

---

### Task 5: Update Results Tables to Measured-Massprops B+C Metrics

**Files:**

- Modify: `sections/05_results.tex`

**Step 1: Replace old main metrics**

Use:

```text
/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/evaluation/per_channel_metrics.csv
```

Main table should compare:

- calibrated prior
- phase-structured correction

Recommended columns:

- target
- calibrated-prior RMSE
- corrected RMSE
- corrected MAE
- corrected R2
- corrected RMSE/std

Keep force and moment blocks visually separated.

**Step 2: Add force improvement statement**

Use exact wording that avoids overclaim:

```text
On the held-out test logs, the phase-structured correction reduces force-channel RMSE by 68.3% for fx,b, 15.0% for fy,b, and 69.8% for fz,b relative to the calibrated prior.
```

Then immediately qualify:

```text
The lateral force channel remains the weakest force channel, with R2 = 0.276, consistent with lower lateral excitation and stronger sensitivity to sideslip/wind-estimation errors.
```

**Step 3: Add moment interpretation**

Use:

```text
For the effective moment channels, my,b has the strongest held-out fit (R2 = 0.798), while mx,b and mz,b remain lower-SNR channels (R2 = 0.224 and 0.263). These scores are reported as effective rotational-wrench prediction metrics under the smoothed angular-acceleration label definition, not as direct validation of isolated aerodynamic moments.
```

**Step 4: Remove or rewrite old Transformer claims**

If `sections/05_results.tex` still frames the main method as a causal Transformer, update it to the current B+C correction story:

- low-dimensional prior
- bounded calibration
- structured deployable correction
- phase/condition residual diagnostics

Do not mix old Transformer headline numbers with new B+C numbers unless the table explicitly identifies both experiment branches.

---

### Task 6: Add Correction-Structure and Residual-Diagnostic Evidence

**Files:**

- Modify: `sections/05_results.tex`
- Optional copy/create:
  - `figures/phase_residual_medians_measured_massprops.pdf`
  - `figures/condition_residual_rmse_measured_massprops.pdf`
  - `figures/frequency_residual_energy_measured_massprops.pdf`

**Step 1: Use latest diagnostic figures**

Source files:

```text
/home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/phase/phase_residual_medians.pdf
/home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/conditions/condition_residual_rmse_key_targets.pdf
/home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/frequency/frequency_residual_energy_key_targets.pdf
```

Either copy these into `figures/` with measured-massprops names or regenerate them from the current artifacts.

**Step 2: Keep residual-diagnostic language conservative**

Allowed language:

- residuals contain repeatable phase/condition/frequency structure
- correction reduces structured discrepancy on held-out logs
- this supports data-guided correction of a low-dimensional prior

Avoid:

- residuals are purely aerodynamic
- residuals prove a specific unmodeled physical mechanism
- residuals validate closed-loop simulation

---

### Task 7: Add Replay as Diagnostic, Not Validation

**Files:**

- Modify: `sections/04_experiments.tex`
- Modify: `sections/05_results.tex`
- Modify: `sections/06_conclusion.tex`

**Step 1: Add a short experiment-protocol paragraph**

In `sections/04_experiments.tex`, add a paragraph titled or worded around:

```text
Replay diagnostics
```

Content:

- replay is not a primary evaluation metric
- outdoor replay compounds estimator noise, smoothing choices, time alignment, wind/disturbances, and controller-response mismatch
- primary validation remains log-conditioned effective-wrench prediction
- alpha-only replay is used to check label consistency

**Step 2: Add the alpha-only finding**

In Results or Discussion:

```text
Moment-inferred angular acceleration is algebraically identical to the smoothed angular acceleration used for label generation, but smoothed alpha does not exactly integrate back to raw logged gyro. This is expected because smoothing changes local slopes and suppresses spikes. We therefore use replay only as a diagnostic for label construction and do not present it as simulator-level validation.
```

Use exact numbers only if they fit naturally:

- norm RMSE about `2.6e-15 rad/s^2`
- smoothed-alpha trapezoid body-rate median error `0.118 rad/s` at `0.25 s`

**Step 3: Update conclusion**

Conclusion should say:

```text
The corrected map is a prerequisite step toward simulator embedding. Closed-loop simulator validation, trajectory replay with modeled disturbances, and controller-in-the-loop evaluation remain future work.
```

Do not say:

```text
The simulator is validated.
```

---

### Task 8: Final LaTeX QA

**Files:**

- Modify as needed: `main.tex`, `sections/*.tex`, `figures/*`

**Step 1: Check figure files**

Run:

```bash
ls -lh figures/real_flight_correction_pipeline.svg \
       figures/real_flight_correction_pipeline.pdf \
       figures/heldout_force_prediction_curve.pdf
```

Expected: all files exist. The SVG source is the editable canonical pipeline figure.

**Step 2: Compile**

Run:

```bash
latexmk -pdf main.tex
```

Expected:

- PDF builds successfully
- no missing figure files
- no unresolved citation warnings
- no undefined references for new labels

**Step 3: Scan for overclaim terms**

Run:

```bash
rg -n "closed-loop|validated simulator|simulation validation|RL controller|replay|Transformer|letter|TODO|placeholder" main.tex sections tex
```

Expected:

- `replay` appears only in diagnostic/limitation wording
- `Transformer` does not remain as the headline method unless intentionally retained and backed by current results
- `letter` does not appear
- TODOs remain only in author/acknowledgement/biography or explicitly red final-measurement placeholders

**Step 4: Save a short implementation report**

Create:

```text
research_notes/20260602_paper_completion_asset_update_report.md
```

Include:

- files modified
- figures created
- metrics updated
- compile command and result
- remaining red placeholders or TODOs

---

## Suggested Execution Order

1. Task 1 claim-evidence note.
2. Task 2 editable pipeline SVG/PDF.
3. Task 3 held-out force prediction curve.
4. Task 4 measured mass-properties description.
5. Task 5 measured-massprops results table.
6. Task 6 residual diagnostics update.
7. Task 7 replay diagnostic wording.
8. Task 8 LaTeX QA and implementation report.

This order avoids rewriting claims before the new visual and metric anchors are in place.

## Commit Strategy

If committing is requested later, use two or three focused commits:

```bash
git add research_notes/20260602_measured_massprops_completion_claim_evidence.md \
        docs/plans/2026-06-02-paper-completion-assets-and-claim-boundary-plan.md
git commit -m "docs: plan measured-massprops paper completion"

git add figures/real_flight_correction_pipeline.* figures/heldout_force_prediction_curve.* sections/*.tex
git commit -m "paper: add pipeline and measured-massprops result updates"

git add research_notes/20260602_paper_completion_asset_update_report.md
git commit -m "docs: record paper completion asset update"
```

Do not commit generated intermediate artifacts from `/home/zn/flap-system-identification/artifacts`.
