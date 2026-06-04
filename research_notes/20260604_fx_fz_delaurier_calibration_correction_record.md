# 2026-06-04 fx/fz DeLaurier Prior Calibration and Correction Record

This note records the current `fx_b` and `fz_b` results for later paper writing and experiment traceback. The key point is to keep two experiment tracks separate:

1. **Internal/diagnostic DeLaurier-style prior shaping**: fixed twist proxy, then sweep remaining DeLaurier-style parameters and separation options.
2. **Held-out force correction pipeline**: train-only exported-prior affine wrappers and deployable phase/condition correction models.

The results below are log-based effective-force prediction results. They are not closed-loop simulator validation and should not be described as identification of true isolated aerodynamic constants.

## Dataset and Preprocessing Context

- Canonical dataset used by the fixed-twist parameter sweep:
  `/home/zn/flap-system-identification/dataset/canonical_v0.2_training_ready_split_measured_massprops_ratio8_sg0p03_v1`
- Correction dataset/root:
  `/home/zn/flap-system-identification/dataset/delaurier_force_prior_moment_direct_measured_massprops_ratio8_v1`
- Effective-wrench labels use the measured-mass-properties / gear-ratio-8 rebuild and `sg0p03` smoothing context.
- The current force focus is `fx_b` and `fz_b`; `fy_b` remains a weaker lateral channel and should not be framed as a primary DeLaurier result.

## Artifact Index

### Fixed-Twist Internal/Diagnostic Sweep

- Summary:
  `/home/zn/flap-system-identification/artifacts/20260604_delaurier_other_parameter_sweep_fixed_twist10_ratio8_sg0p03_v1/fixed_twist10_other_parameter_sweep_summary.md`
- Artifact root:
  `/home/zn/flap-system-identification/artifacts/20260604_delaurier_other_parameter_sweep_fixed_twist10_ratio8_sg0p03_v1`

### Old-vs-New Prior Visuals

- Artifact root:
  `/home/zn/flap-system-identification/artifacts/20260604_delaurier_old_vs_new_prior_visuals_fixed_twist10`
- Metrics:
  `/home/zn/flap-system-identification/artifacts/20260604_delaurier_old_vs_new_prior_visuals_fixed_twist10/old_vs_new_prior_metrics.csv`
- Figures:
  - `time_series_label_old_new_prior_fx_fz.png/pdf`
  - `scatter_label_old_new_prior_fx_fz.png/pdf`
  - `phase_binned_label_old_new_prior_fx_fz.png/pdf`
  - `fx_raw_vs_zscore_old_new_prior.png/pdf`

### Exported-Prior Affine Recalibration

- Artifact root:
  `/home/zn/flap-system-identification/artifacts/20260603_delaurier_force_recalibration_measured_massprops_ratio8_v1`
- Summary:
  `/home/zn/flap-system-identification/artifacts/20260603_delaurier_force_recalibration_measured_massprops_ratio8_v1/README.md`
- Metrics:
  `/home/zn/flap-system-identification/artifacts/20260603_delaurier_force_recalibration_measured_massprops_ratio8_v1/metrics_by_split.csv`
- Parameters:
  `/home/zn/flap-system-identification/artifacts/20260603_delaurier_force_recalibration_measured_massprops_ratio8_v1/parameters.csv`
- Important scope note: this artifact does **not** re-export IsaacLab with changed internal DeLaurier parameters. It fits train-only affine wrappers around already exported force predictions.

### Deployable Correction Pipeline

- Artifact root:
  `/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1`
- Main all-channel evaluation:
  `/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1/evaluation/per_channel_metrics.csv`
- Force-only first correction:
  `/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1/force_v1`
- Deployable correction:
  `/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1/deployable_v2`
- Phase-structured correction:
  `/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1/phase_structured`

## Fixed Twist Proxy

The twist proxy was selected/fixed before sweeping the other parameters:

| parameter | value | interpretation |
|---|---:|---|
| `twist_eta_max_deg` | 10 deg | fixed implementation proxy for unmodeled wing flexibility |
| `twist_eta_limit_deg` | 10 deg | fixed implementation limit |
| `twist_f_ref_hz` | 4 Hz | reference flapping frequency for twist proxy |

Paper boundary: do not present this as an identified DeLaurier parameter from the original paper. It is an implementation-level proxy for flexible-wing effects.

## Internal/Diagnostic DeLaurier-Style Sweep

### Sweep Scope

Attached-flow stage:

| parameter | tested values |
|---|---|
| `alpha0_deg` | -4, 0, 4 |
| `eta_s` | 0.25, 0.65, 1.05 |
| `cd_f` | 0, 0.028, 0.08 |

Separation diagnostic stage, initialized from the best attached candidate:

| parameter | tested values |
|---|---|
| `alpha_stall_max_deg` | 8, 12, 18 |
| `cd_cf` | 1.2, 1.95, 2.7 |
| `xi` | 0, 1 |

Selection used validation `fx_fz_mean` RMSE. Test metrics were not used for parameter selection.

### Best Attached Candidate

| parameter | selected value |
|---|---:|
| `alpha0_deg` | 4 deg |
| `eta_s` | 0.65 |
| `cd_f` | 0.0 |
| `enable_separation` | false |

Validation mean RMSE: `6.700`.

Test metrics:

| target | RMSE | MAE | bias | R2 | corr |
|---|---:|---:|---:|---:|---:|
| `fx_b` | 4.346 | 3.128 | -1.115 | 0.050 | 0.342 |
| `fz_b` | 8.952 | 7.252 | 6.024 | -0.068 | 0.918 |
| `fx_fz_mean` | 6.649 | 5.190 | 2.454 | -0.009 | 0.630 |

### Best Separation-Diagnostic Candidate

| parameter | selected value |
|---|---:|
| `alpha0_deg` | 4 deg |
| `eta_s` | 0.65 |
| `cd_f` | 0.0 |
| `enable_separation` | true |
| `alpha_stall_max_deg` | 18 deg |
| `cd_cf` | 1.2 |
| `xi` | 1.0 |

Validation mean RMSE: `5.369`.

Test metrics:

| target | RMSE | MAE | bias | R2 | corr |
|---|---:|---:|---:|---:|---:|
| `fx_b` | 4.047 | 2.629 | -2.064 | 0.176 | 0.781 |
| `fz_b` | 6.626 | 5.256 | 4.121 | 0.415 | 0.892 |
| `fx_fz_mean` | 5.337 | 3.942 | 1.029 | 0.296 | 0.836 |

### Interpretation of Internal/Diagnostic Sweep

- The most important attached-flow adjustment is `alpha0_deg = 4 deg`.
- This is best described as an effective incidence / zero-lift offset. It may absorb AoA alignment, state-estimation, flexible-wing, and complete-vehicle effects.
- `eta_s = 0.65` remains at the nominal/mid value.
- `cd_f = 0.0` suggests the retained chordwise/friction term is not the main contributor to the observed force discrepancy.
- The separation-enabled diagnostic prior improves both validation and test force RMSE, especially relative to the attached-only candidate.
- The selected separation parameters should be treated as prior-shaping diagnostics, not as measured stall or separation constants.

## Old vs New Prior Visual Diagnostics

From `old_vs_new_prior_metrics.csv`:

| target | prior | RMSE | corr |
|---|---|---:|---:|
| `fx_b` | old | 4.738 | 0.156 |
| `fx_b` | new | 4.047 | 0.781 |
| `fz_b` | old | 11.716 | 0.916 |
| `fz_b` | new | 6.626 | 0.892 |

Important interpretation:

- `fx_b` correlation improves substantially in the new prior, but the raw plot can still look visually weak because the prior amplitude remains too small and biased relative to the label. The correlation is mostly reflecting improved trend/phase ordering, not accurate amplitude prediction.
- `fz_b` already had high correlation in the old prior, but large RMSE and bias. The new prior reduces error while retaining strong trend correlation.
- These plots are useful for explaining why a correction layer is still needed after internal prior shaping.

## Exported-Prior Affine Recalibration

This is the `20260603_delaurier_force_recalibration_measured_massprops_ratio8_v1` artifact. It fits train-only wrappers on exported force predictions.

Variants:

| variant | meaning |
|---|---|
| `A0_current_delaurier` | unchanged exported calibrated DeLaurier force prediction |
| `A1_per_channel_affine` | independent train-only affine correction for `fx_b`, `fy_b`, `fz_b` |
| `A2_weighted_shared_gain_bias` | shared force gain plus per-channel bias |

Test metrics:

| variant | target | RMSE | MAE | bias | R2 |
|---|---|---:|---:|---:|---:|
| `A0_current_delaurier` | `fx_b` | 4.738 | 3.425 | -1.353 | -0.129 |
| `A0_current_delaurier` | `fz_b` | 11.716 | 9.821 | 9.628 | -0.829 |
| `A0_current_delaurier` | force mean | 5.818 | 4.674 | 2.768 | -0.319 |
| `A1_per_channel_affine` | `fx_b` | 4.409 | 3.546 | 0.025 | 0.022 |
| `A1_per_channel_affine` | `fz_b` | 3.476 | 2.752 | 0.020 | 0.839 |
| `A1_per_channel_affine` | force mean | 2.961 | 2.358 | 0.001 | 0.287 |
| `A2_weighted_shared_gain_bias` | `fx_b` | 4.420 | 3.500 | 0.025 | 0.018 |
| `A2_weighted_shared_gain_bias` | `fz_b` | 3.473 | 2.760 | 0.020 | 0.839 |
| `A2_weighted_shared_gain_bias` | force mean | 2.964 | 2.345 | 0.001 | 0.285 |

Affine parameters:

| variant | output | gain | bias |
|---|---|---:|---:|
| `A1_per_channel_affine` | `fx_b` | 0.2815 | 2.6128 |
| `A1_per_channel_affine` | `fz_b` | 0.5942 | -9.1335 |
| `A2_weighted_shared_gain_bias` | `fx_b` | 0.5879 | 2.0864 |
| `A2_weighted_shared_gain_bias` | `fz_b` | 0.5879 | -9.1259 |

Interpretation:

- Simple exported-prior affine recalibration strongly improves `fz_b`.
- It does not solve `fx_b`; the `fx_b` channel still needs state/phase/condition-dependent correction.
- This supports a two-step story: first align the prior scale/bias, then apply a deployable structured correction for the remaining effective-force discrepancy.

## Deployable and Phase-Structured Correction Results

The current correction artifact is:

`/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1`

All values below are from the held-out test split with `n = 60671`.

### Force Channel Summary

| variant | `fx_b` RMSE | `fx_b` MAE | `fx_b` bias | `fz_b` RMSE | `fz_b` MAE | `fz_b` bias | force mean RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `A1_prior` | 4.409 | 3.546 | 0.025 | 3.476 | 2.752 | 0.020 | 2.961 |
| `force_v1` | 1.212 | 0.932 | 0.041 | 2.101 | 1.667 | -0.004 | 1.416 |
| `deployable_v2` | 1.091 | 0.828 | 0.061 | 2.055 | 1.611 | -0.024 | 1.316 |
| `phase_structured` | 1.091 | 0.828 | 0.061 | 2.055 | 1.611 | -0.024 | 1.316 |

Approximate RMSE reduction from `A1_prior` to `phase_structured`:

| target | reduction |
|---|---:|
| `fx_b` | 75.3% |
| `fz_b` | 40.9% |
| force mean | 55.6% |

### Correction Model Configuration

`force_v1`:

- Best model: affine ridge
- Selected by validation force-mean RMSE
- `alpha = 10.0`
- Targets: `fx_b`, `fy_b`, `fz_b`
- Main feature columns: phase harmonics, AoA proxy, flapping frequency, airspeed, dynamic pressure, and phase interactions.

`deployable_v2`:

- Selected force source: `corrected_force_v2`
- Selected force model:
  - variant: `affine`
  - feature group: `base+rates+controls+lateral+interactions`
  - alpha: `10.0`
- Uses deployable features derived from phase, frequency, airdata, body rates, lateral proxies, and actuator commands.
- Does not use true force at inference.

`phase_structured`:

- Selected force model:
  - variant: `affine`
  - family: `phase_structured_plus_rates_controls`
  - alpha: `10.0`
- Test force metrics are identical to `deployable_v2` in the current artifact.
- Therefore, for force channels, the main gain is already captured by the deployable correction; the phase-structured naming is more useful for method organization and moment/diagnostic interpretation than for additional `fx_b`/`fz_b` numerical improvement.

## Paper-Safe Interpretation

Suggested wording:

> With a fixed implementation-level twist proxy, a low-dimensional sweep of the remaining DeLaurier-style parameters improved the longitudinal force prior on held-out flight logs. The largest attached-flow adjustment was an effective incidence/zero-lift offset, while a separation-enabled diagnostic prior further reduced the `fx_b`/`fz_b` force error. A deployable affine correction using phase, frequency, airdata, body-rate, lateral-proxy, and actuator features then reduced the held-out `fx_b` RMSE from 4.41 N to 1.09 N and the `fz_b` RMSE from 3.48 N to 2.05 N relative to the exported-prior affine baseline.

Shorter version:

> Real-flight logs were used first to align the DeLaurier-style force prior and then to learn a deployable structured correction. On held-out logs, the correction reduced `fx_b` and `fz_b` RMSE to 1.09 N and 2.05 N, respectively.

## Claims to Avoid

Avoid:

- "We identified the true DeLaurier parameters."
- "The separation parameters are measured stall parameters."
- "The corrected model has been validated in closed-loop simulation."
- "The force correction proves isolated wing aerodynamics."
- "The phase-structured force model outperforms deployable correction on `fx_b`/`fz_b`." In the current artifact their force metrics are identical.

## Current Main Takeaway

The current evidence supports the following story:

1. The original/exported DeLaurier-style force prior had useful structure for `fz_b` but weak usable amplitude and poor `fx_b` alignment.
2. Fixing a twist proxy and sweeping low-dimensional DeLaurier-style parameters improves the prior shape, especially the `fx_b` correlation and `fz_b` error.
3. A simple affine wrapper around exported prior outputs mainly fixes `fz_b`; `fx_b` still requires state/phase/condition-dependent correction.
4. The deployable structured correction brings `fx_b` to about `1.09 N` RMSE and `fz_b` to about `2.05 N` RMSE on the held-out test split.
5. This is strong enough for a primary force-channel result, but it should be framed as log-based effective-force correction toward simulator-prior improvement, not as simulator rollout validation.

## 2026-06-04 Correction Update: Best Separation Prior as Force Baseline

After the tail/moment discussion, the force result was rerun in a cleaner sequence:

```text
fixed-twist separation-enabled DeLaurier-style prior
-> focused fx/fz structured correction
```

This avoids mixing the newer internal/separation prior diagnostics with the older exported-prior affine baseline.

Artifact:

`/home/zn/flap-system-identification/artifacts/20260604_fx_fz_structured_correction_best_separation_prior_v1`

Input prior:

`/home/zn/flap-system-identification/artifacts/20260604_delaurier_other_parameter_sweep_fixed_twist10_ratio8_sg0p03_v1/priors/separation__twist_eta_max_deg_10p0__alpha0_deg_4p0__eta_s_0p65__cd_f_0p0__enable_separation_sep_on__alpha_stall_max_deg_18p0__cd_cf_1p2__xi_1p0`

Selected correction:

| item | value |
|---|---|
| selected model | `dense_deployable_affine_alpha_1` |
| family | `dense_deployable_affine` |
| alpha | `1.0` |
| feature count | `132` |
| validation `fx_fz_mean` RMSE | `1.540` |

Test metrics:

| model | target | RMSE | MAE | bias | R2 | corr |
|---|---|---:|---:|---:|---:|---:|
| raw separation prior | `fx_b` | 4.047 | 2.629 | -2.064 | 0.176 | 0.781 |
| raw separation prior | `fz_b` | 6.626 | 5.256 | 4.121 | 0.415 | 0.892 |
| raw separation prior | `fx_fz_mean` | 5.337 | 3.942 | 1.029 | 0.296 | 0.836 |
| constant affine | `fx_b` | 2.794 | 2.081 | 0.061 | 0.607 | 0.781 |
| constant affine | `fz_b` | 3.926 | 3.104 | -0.094 | 0.795 | 0.892 |
| phase/frequency gain-bias | `fx_b` | 1.300 | 0.985 | 0.118 | 0.915 | 0.957 |
| phase/frequency gain-bias | `fz_b` | 2.201 | 1.731 | 0.046 | 0.935 | 0.967 |
| pitch-oriented gain-bias | `fx_b` | 1.205 | 0.914 | 0.027 | 0.927 | 0.963 |
| pitch-oriented gain-bias | `fz_b` | 2.177 | 1.718 | -0.008 | 0.937 | 0.968 |
| selected dense deployable | `fx_b` | 1.052 | 0.799 | 0.019 | 0.944 | 0.972 |
| selected dense deployable | `fz_b` | 2.090 | 1.629 | -0.002 | 0.942 | 0.970 |
| selected dense deployable | `fx_fz_mean` | 1.571 | 1.214 | 0.009 | 0.943 | 0.971 |

Updated paper-safe force result:

> Starting from the fixed-twist, separation-enabled DeLaurier-style force prior, a deployable structured correction reduces held-out `fx_b` and `fz_b` RMSE to `1.05 N` and `2.09 N`, respectively.

Important interpretation:

- The raw separation prior has much better `fx_b` correlation than the older raw prior, but its amplitude and bias are still poor.
- Constant affine calibration removes a large part of the scale/bias error, especially for `fz_b`, but remains insufficient for `fx_b`.
- Phase/frequency and pitch-oriented gain-bias models capture most of the structured force residual with fewer features.
- The selected dense deployable correction gives the lowest validation RMSE and the best held-out test force metrics.
- Keep this force result separate from moment attribution. Wing-force errors can generate `my_b` through moment arms, so future pitch-moment diagnostics should include a wing-force moment-arm model before assigning residual moment to the tail.
