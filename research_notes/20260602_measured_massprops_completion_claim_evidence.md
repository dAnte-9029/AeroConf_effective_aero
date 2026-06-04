# Measured-Massprops Completion Claim-Evidence Note

## Current Paper Identity

This AeroConf draft is an engineering step toward real-flight-corrected flapping-wing simulation through log-conditioned effective-wrench modeling. The paper studies how real flight data can be embedded into a low-dimensional DeLaurier-style simulator prior by reconstructing effective wrench from outdoor PX4 logs, calibrating the prior, and learning a structured correction from simulator-available inputs.

The current evidence supports corrected effective-wrench prediction on held-out logs. It does not support claims of closed-loop simulator validation, reinforcement-learning controller training, or exact open-loop trajectory replay.

## Claims We Can Make

- Measured mass, center of gravity, and inertia are used to regenerate the effective-wrench labels, making the label construction more physically grounded than the earlier CAD-seeded metadata branch.
- The phase-structured correction improves force-channel held-out prediction relative to the calibrated DeLaurier-style prior.
- The remaining/corrected residuals can be analyzed as repeatable phase-, condition-, and frequency-dependent discrepancies in the log-conditioned effective-wrench map.
- Moment channels can be reported as effective rotational-wrench prediction under a smoothed angular-acceleration label definition.
- Replay diagnostics are useful for checking label construction and smoothing choices, but they are not the primary validation.

## Claims We Must Avoid

- Do not claim a validated closed-loop flapping-wing simulator.
- Do not claim the correction directly validates a reinforcement-learning training environment.
- Do not claim exact open-loop replay of outdoor flight trajectories.
- Do not interpret the residual as purely aerodynamic load mismatch; the label is an effective non-gravitational wrench and includes estimator, disturbance, body, tail, and mechanism effects.
- Do not make moment channels the strongest physical claim. The moment labels are more sensitive to inertia, CG/reference-point consistency, and angular-acceleration smoothing.

## Evidence Table

| Claim | Evidence anchor | Paper-safe wording |
| --- | --- | --- |
| Force correction improves held-out log prediction | `/home/zn/flap-system-identification/artifacts/20260602_bc_correction_measured_massprops_v1/evaluation/per_channel_metrics.csv` | "On held-out logs, the phase-structured correction reduces force-channel RMSE relative to the calibrated prior." |
| Lateral force remains weaker | `fy_b` R2 = 0.276439 | "The lateral force channel remains the weakest force channel, consistent with lower lateral excitation and sensitivity to sideslip/wind estimation." |
| Moment prediction is mixed | `mx_b` R2 = 0.224088, `my_b` R2 = 0.798385, `mz_b` R2 = 0.262573 | "Moment channels are reported as effective rotational-wrench prediction metrics under label uncertainty." |
| New moment labels differ strongly from old labels | `seed_label_scale_delta_summary.json` | "The measured inertia branch changes moment-label scale substantially, so old and new moment RMSE values should not be compared directly." |
| Replay should be diagnostic only | `alpha_only_replay_summary.csv` and summary report | "Smoothed-alpha labels are algebraically consistent with moment reconstruction but do not exactly integrate back to raw logged gyro." |

## Numbers to Use

Held-out test metrics for the phase-structured correction:

| Target | RMSE | MAE | R2 | RMSE/std |
| --- | ---: | ---: | ---: | ---: |
| `fx_b` | 1.41888 | 1.05494 | 0.899346 | 0.31726 |
| `fy_b` | 0.888775 | 0.640577 | 0.276439 | 0.850624 |
| `fz_b` | 2.62389 | 1.98471 | 0.908929 | 0.301779 |
| `mx_b` | 0.591617 | 0.433001 | 0.224088 | 0.880859 |
| `my_b` | 0.281844 | 0.219681 | 0.798385 | 0.449016 |
| `mz_b` | 0.220901 | 0.168601 | 0.262573 | 0.858736 |

Force RMSE reduction from calibrated prior to phase-structured correction:

- `fx_b`: 68.3%
- `fy_b`: 15.0%
- `fz_b`: 69.8%

Label-scale changes from old CAD-seeded branch to measured-massprops branch:

- force-channel pooled standard-deviation ratio new/old: 0.951737
- `mx_b`: 230.852
- `my_b`: 148.272
- `mz_b`: 551.007

Replay/alpha diagnostic:

- moment-inferred alpha and smoothed alpha are algebraically identical to about `2.6e-15 rad/s^2`
- smoothed-alpha trapezoid replay body-rate median error remains nonzero:
  - 0.135 rad/s at 0.10 s
  - 0.118 rad/s at 0.25 s
  - 0.128 rad/s at 0.50 s
  - 0.139 rad/s at 1.00 s

## Numbers Not to Mix

- Do not use a single six-axis "overall RMSE" as a main result because it mixes N and N m.
- Do not directly compare old and new moment RMSE values without explaining the moment-label scale change caused by measured inertia.
- Do not combine old Transformer results and new B+C measured-massprops results in one headline metric unless the experiment branches are explicitly separated.
- Do not use replay errors as simulator validation metrics.
