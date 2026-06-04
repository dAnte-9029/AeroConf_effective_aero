# Channel Excitation and SNR Diagnostics

This diagnostic is a draft analysis for explaining why the strongest measured-massprops results occur in `fx_b`, `fz_b`, and `my_b`, while `fy_b`, `mx_b`, and `mz_b` remain weaker.

## Main Observations

- Stronger channels (`fx_b`, `fz_b`, `my_b`) have mean corrected RMSE/std `0.356`.
- Weaker channels (`fy_b`, `mx_b`, `mz_b`) have mean corrected RMSE/std `0.863`.
- `fx_b` and `fz_b` have large target variance, high deployable-feature linear R2, and strong wingbeat-frequency residual structure, supporting the phase/condition correction story.
- `my_b` has the best moment-channel prediction and strong structured frequency content, making it a reasonable supporting effective-moment result.
- `fy_b`, `mx_b`, and `mz_b` have higher normalized errors and weaker or more broadband residual structure; they should be framed as limitations rather than hidden failures.
- `mx_b` does not become clearly strong in high-roll-rate or high-elevon-difference subsets, so the current evidence points beyond simple low excitation toward derivative/reference/timing sensitivity.
- Feature-group ridge rows named `angular_derivatives_label_diagnostic` are diagnostic only because angular acceleration is part of moment-label construction and is not a deployable correction input.

## Best Deployable Ridge Feature Groups by Channel

- `fx_b`: best linear feature group `all` with test R2 `0.868`.
- `fy_b`: best linear feature group `all` with test R2 `0.243`.
- `fz_b`: best linear feature group `all` with test R2 `0.875`.
- `mx_b`: best linear feature group `all` with test R2 `0.176`.
- `my_b`: best linear feature group `all` with test R2 `0.711`.
- `mz_b`: best linear feature group `phase` with test R2 `0.125`.

## Angular-Derivative Diagnostic Rows

- `fx_b`: derivative-diagnostic R2 `0.027`. This is label-chain information, not a deployable model input.
- `fy_b`: derivative-diagnostic R2 `0.264`. This is label-chain information, not a deployable model input.
- `fz_b`: derivative-diagnostic R2 `0.208`. This is label-chain information, not a deployable model input.
- `mx_b`: derivative-diagnostic R2 `1.000`. This is label-chain information, not a deployable model input.
- `my_b`: derivative-diagnostic R2 `1.000`. This is label-chain information, not a deployable model input.
- `mz_b`: derivative-diagnostic R2 `1.000`. This is label-chain information, not a deployable model input.

## Top Pearson Correlations

- `fx_b`: phase_cos_1 (-0.67), phase_sin_2 (+0.47), phase_sin_1 (-0.42), p (+0.30), r (+0.21)
- `fy_b`: p (+0.24), phase_cos_2 (+0.24), phase_cos_1 (+0.24), q (-0.23), r (-0.18)
- `fz_b`: phase_cos_1 (+0.91), q (-0.26), r (-0.19), phase_cos_2 (+0.18), phase_sin_1 (-0.13)
- `mx_b`: phase_cos_1 (-0.37), q (+0.27), phase_cos_2 (-0.17), phase_sin_2 (-0.16), phase_sin_1 (+0.12)
- `my_b`: phase_cos_2 (-0.78), p (-0.29), phase_cos_1 (-0.23), phase_sin_2 (+0.16), phase_sin_1 (+0.16)
- `mz_b`: phase_cos_2 (+0.30), phase_sin_1 (+0.22), q (-0.11), p (-0.10), phase_sin_2 (-0.06)

## mx Roll-Specific Subsets

- `all`: n=60658, std=0.672, RMSE=0.592, RMSE/std=0.881, R2=0.224.
- `abs_p_dot_smooth_gt_p75`: n=15164, std=1.185, RMSE=1.005, RMSE/std=0.848, R2=0.280.
- `abs_p_dot_smooth_gt_p90`: n=6066, std=1.506, RMSE=1.332, RMSE/std=0.884, R2=0.218.
- `abs_roll_rate_p_gt_p75`: n=15159, std=0.731, RMSE=0.683, RMSE/std=0.933, R2=0.129.
- `abs_roll_rate_p_gt_p90`: n=6065, std=0.755, RMSE=0.744, RMSE/std=0.986, R2=0.028.
- `abs_roll_angle_gt_p75`: n=15167, std=0.729, RMSE=0.657, RMSE/std=0.902, R2=0.187.
- `abs_roll_angle_gt_p90`: n=6067, std=0.735, RMSE=0.663, RMSE/std=0.902, R2=0.187.
- `abs_elevon_diff_gt_p75`: n=15165, std=0.818, RMSE=0.751, RMSE/std=0.918, R2=0.157.
- `abs_elevon_diff_gt_p90`: n=6066, std=0.902, RMSE=0.840, RMSE/std=0.931, R2=0.132.

## Frequency Structure Anchor

- `fx_b`: dominant component `flap_main`, true energy fraction `0.516`, remaining fraction of true `0.025`.
- `fy_b`: dominant component `broadband_high_8_25hz_excl_structured`, true energy fraction `0.428`, remaining fraction of true `0.964`.
- `fz_b`: dominant component `flap_main`, true energy fraction `0.787`, remaining fraction of true `0.031`.
- `mx_b`: dominant component `broadband_high_8_25hz_excl_structured`, true energy fraction `0.314`, remaining fraction of true `1.005`.
- `my_b`: dominant component `harmonic_2f`, true energy fraction `0.452`, remaining fraction of true `0.146`.
- `mz_b`: dominant component `broadband_high_8_25hz_excl_structured`, true energy fraction `0.465`, remaining fraction of true `0.768`.

## Paper-Safe Interpretation

The channels with the strongest prediction performance are also the channels with sustained excitation and repeatable phase/condition/frequency structure. The weaker channels should be described as directions where the retained logs provide less informative excitation or where the labels are more sensitive to wind, sideslip, reference-point assumptions, and gyro differentiation.
