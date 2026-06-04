# 2026-06-02 Paper Completion Asset Update Report

## Scope

This draft pass implements the paper-completion plan in `docs/plans/2026-06-02-paper-completion-assets-and-claim-boundary-plan.md`. The manuscript is now framed around measured-mass-properties effective-wrench labels and a deployable phase-structured correction of a DeLaurier-style simulator prior.

## Files Modified

- `main.tex`
  - Updated title from neural residual wording to structured correction wording.
- `sections/00_abstract.tex`
  - Replaced old Transformer and five-fold numbers with measured-mass-properties B+C results.
- `sections/01_intro.tex`
  - Updated contribution statements to measured labels, structured correction, residual diagnostics, and replay boundary.
- `sections/02_dataset.tex`
  - Added measured mass, CG, and inertia values.
  - Replaced three-point weighing wording with four-point weighing where relevant.
  - Added measured-mass-properties label description and moment-label sensitivity language.
  - Inserted the editable pipeline figure.
- `sections/02_related.tex`
  - Updated old letter/Transformer wording even though the section is not currently included by `main.tex`.
- `sections/03_method.tex`
  - Changed the method from a causal Transformer framing to a structured correction framing.
  - Added deployable correction features and force/moment channel semantics.
- `sections/04_experiments.tex`
  - Updated compared models to the measured-mass-properties B+C branch.
  - Added replay diagnostics as a non-primary evaluation.
- `sections/05_results.tex`
  - Rewritten around measured-mass-properties metrics.
  - Added current per-channel results, per-log results, prediction curve, residual diagnostics, and replay claim boundary.
- `sections/06_conclusion.tex`
  - Rewrote conclusion to avoid closed-loop simulator validation claims.
- `scripts/make_real_flight_correction_pipeline.py`
  - Generates editable pipeline SVG plus PDF/PNG.
- `scripts/make_prediction_curve_figure.py`
  - Generates held-out force prediction curve PDF/PNG from aligned measured-massprops artifacts.

## Files Created

- `research_notes/20260602_measured_massprops_completion_claim_evidence.md`
- `research_notes/20260602_paper_completion_asset_update_report.md`
- `figures/real_flight_correction_pipeline.svg`
- `figures/real_flight_correction_pipeline.pdf`
- `figures/real_flight_correction_pipeline.png`
- `figures/heldout_force_prediction_curve.pdf`
- `figures/heldout_force_prediction_curve.png`
- `figures/phase_residual_medians_measured_massprops.pdf`
- `figures/condition_residual_rmse_measured_massprops.pdf`
- `figures/frequency_residual_energy_measured_massprops.pdf`

## Evidence Sources

- `/home/zn/flap-system-identification/artifacts/20260602_old_vs_measured_massprops_comparison/summary.md`
- `/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/evaluation/per_channel_metrics.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/evaluation/per_log_metrics.csv`
- `/home/zn/flap-system-identification/artifacts/20260602_residual_diagnostics_measured_massprops_v1/`
- `/home/zn/flap-system-identification/artifacts/20260602_replay_measured_massprops_v1/alpha_only_replay_diagnostics/alpha_only_replay_summary.csv`

## Key Numbers Now Used

- Force RMSE reduction from calibrated prior to phase-structured correction:
  - `fx_b`: 68.3%
  - `fy_b`: 15.0%
  - `fz_b`: 69.8%
- Final held-out phase-structured force metrics:
  - `fx_b`: RMSE 1.41888, R2 0.899346
  - `fy_b`: RMSE 0.888775, R2 0.276439
  - `fz_b`: RMSE 2.62389, R2 0.908929
- Final held-out phase-structured moment metrics:
  - `mx_b`: RMSE 0.591617, R2 0.224088
  - `my_b`: RMSE 0.281844, R2 0.798385
  - `mz_b`: RMSE 0.220901, R2 0.262573
- Replay diagnostic:
  - moment-inferred alpha matches smoothed alpha to about `2.6e-15 rad/s^2`
  - smoothed alpha does not exactly integrate back to raw logged gyro, so replay remains diagnostic only

## Verification

Command run:

```bash
latexmk -pdf main.tex
```

Result:

- `main.pdf` generated successfully.
- PDF path: `/home/zn/paper/AeroConf_effective_aero/main.pdf`
- PDF pages: 13.
- No unresolved citations or undefined references found in `main.log` after the final run.
- Remaining LaTeX warnings are layout/template warnings, mostly underfull boxes and one unused `letterpaper` class option.

Additional scan:

```bash
rg -n "Transformer|letter|residual Transformer|overall RMSE|date-stratified five-fold|validated simulator|simulation validation|RL controller" main.tex sections tex
```

Result:

- Old Transformer/letter headline wording removed from included sections.
- Remaining `simulation validation` wording is negative/claim-boundary text in the conclusion.

## Remaining Placeholders

These are intentionally still visible:

- Author, affiliation, acknowledgement, and biography TODOs in `main.tex`.
- Flight-campaign notes and weather records in `sections/02_dataset.tex`.
- Component load-reference coordinates and some label uncertainty table entries in `sections/02_dataset.tex`.

These should be filled after final field-test/weather records, component coordinates, and sensitivity diagnostics are ready.
