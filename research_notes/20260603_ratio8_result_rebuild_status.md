# 2026-06-03 Ratio-8 Result Rebuild Status

## Status

The flapping-drive ratio has been rebuilt using `encoder_to_drive_ratio = 8.0`.
The old `20260602` and `20260603_delaurier_prior_measured_massprops_key_aligned_v1` artifacts should be treated as stale for paper numbers.

Use these ratio-8 artifacts for future paper updates:

- Split: `/home/zn/flap-system-identification/dataset/canonical_v0.2_training_ready_split_measured_massprops_ratio8_sg0p03_v1`
- Phase/frequency audit: `/home/zn/flap-system-identification/artifacts/20260603_ratio8_phase_frequency_audit_v1`
- DeLaurier prior export: `/home/zn/flap-system-identification/artifacts/20260603_delaurier_prior_measured_massprops_ratio8_v1`
- A1 calibrated prior: `/home/zn/flap-system-identification/artifacts/20260603_delaurier_force_recalibration_measured_massprops_ratio8_v1/A1_prior_for_residual_split`
- Residual split: `/home/zn/flap-system-identification/dataset/delaurier_force_prior_moment_direct_measured_massprops_ratio8_v1`
- B+C correction: `/home/zn/flap-system-identification/artifacts/20260603_bc_correction_measured_massprops_ratio8_v1`
- Residual diagnostics: `/home/zn/flap-system-identification/artifacts/20260603_residual_diagnostics_measured_massprops_ratio8_v1`
- Replay diagnostics: `/home/zn/flap-system-identification/artifacts/20260603_replay_measured_massprops_ratio8_v1`

## Key Checks

- PX4 source defaults were updated to `FLAP_RATIO = 8.0`.
- Canonical phase uses Hall-indexed `wing_phase` when present.
- Canonical flapping frequency uses `wing_phase.flap_frequency_hz`; the old `flap_frequency` topic is preserved only as `flap_frequency_topic_hz`.
- The phase/frequency audit passes against `wing_phase`; `encoder_rpm_est/(60*8)` shows a legacy 7.5 semantic mismatch and should be treated as diagnostic only for these logs.
- Lineage audit passed with no stale `20260602` or old key-aligned prior references in new ratio-8 artifacts.

## Current Test Metrics

From `artifacts/20260603_bc_correction_measured_massprops_ratio8_v1/evaluation/per_channel_metrics.csv` on the held-out test split:

| Variant | fx RMSE | fy RMSE | fz RMSE | force mean RMSE | mx RMSE | my RMSE | mz RMSE | moment mean RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A1 calibrated prior | 4.409 | 0.999 | 3.476 | 2.961 | 0.671 | 0.628 | 0.257 | 0.519 |
| force v1 | 1.212 | 0.934 | 2.101 | 1.416 | - | - | - | - |
| deployable v2 | 1.091 | 0.803 | 2.055 | 1.316 | 0.590 | 0.308 | 0.217 | 0.372 |
| phase-structured | 1.091 | 0.803 | 2.055 | 1.316 | 0.591 | 0.292 | 0.211 | 0.365 |

Interpretation for the paper:

- The final force result is essentially identical between deployable v2 and phase-structured correction.
- The phase-structured model mainly improves or organizes the moment head and residual diagnostics, not the force RMSE.
- Side force remains the weakest force channel.
- Moment results should be described as effective rotational-wrench prediction, not validated aerodynamic moment modeling.

## Replay Boundary

The short-horizon oracle translational sanity check is usable only as a local consistency diagnostic:

- 0.10 s median position error: about 0.020 m.
- 0.25 s median position error: about 0.047 m.

The rotational smoke diagnostics do not support six-DOF replay claims:

- `moment_label_closure_gate = fail`
- `forward_omega_replay_gate = fail`
- `kinematic_attitude_gate = conditional`

Paper wording should not claim closed-loop simulator validation, exact trajectory replay, or validated six-degree-of-freedom simulator behavior. Safe wording is: log-conditioned correction of an effective-wrench simulator prior, and a prerequisite step toward simulator correction.

## Paper Update Guidance

- Replace old result numbers only from the ratio-8 evaluation CSV above.
- Keep `FLAP_RATIO = 8.0` and Hall-indexed `wing_phase` in Sec. 2/3.
- State that smoothing is used for label reconstruction only and is not a deployed model input.
- Explain the DeLaurier wrapper conservatively: it aligns a structured wing-force prior with real-flight effective-force labels; it is not a full re-identification of all aerodynamic parameters.
- Keep replay as diagnostic evidence only.
