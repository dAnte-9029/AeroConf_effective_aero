# 2026-06-04 Tail Prior Alignment Then Gain/Bias Note

This note records a proposed route for using real-flight data to improve the tail model without overclaiming isolated tail-aerodynamic identification.

## Core Idea

Use a two-stage grey-box procedure:

1. **Physically constrained tail-prior alignment**: adjust bounded geometry/reference and aerodynamic parameters so the tail prior has plausible sign, shape, channel coupling, and held-out correlation with the effective moment residual.
2. **Train-only gain/bias calibration**: after the prior has reasonable structure, apply a simple gain/bias wrapper to correct scale and offset.

This mirrors the current DeLaurier force-prior workflow: first make the physics prior directionally useful, then apply a low-dimensional correction.

## Interpretation Boundary

The target remains the complete-vehicle effective wrench from outdoor flight logs. The tail model is a component prior, not an isolated measured tail load.

Safe wording:

> A physically constrained tail-prior alignment was used to test whether the effective moment residuals were consistent with plausible tail-surface contributions.

Avoid:

> The true tail aerodynamic parameters were identified from flight data.

## Parameter Groups To Adjust

### 1. Geometry and Reference Parameters

These mainly affect moments through `tau = r x F`.

| parameter family | main channels | role |
|---|---|---|
| horizontal-tail aerodynamic-center `x_ac` | `my_b` | changes pitch-moment arm |
| elevon aerodynamic-center `x_ac` | `my_b`, `mx_b` | changes pitch and roll moment arms |
| elevon aerodynamic-center `y_ac` | `mx_b` | changes differential-elevon roll arm |
| vertical/rudder aerodynamic-center `x_ac` | `mz_b` | changes yaw-moment arm |
| vertical/rudder aerodynamic-center `z_ac` | `mx_b`, `mz_b` | changes side-force roll/yaw coupling |
| `base_com_pos_b` / CG reference | all moments | changes all moment arms |

CG should preferably come from measured mass properties. It can be used for small sensitivity checks, but should not be freely optimized over a large range.

Recommended constraints:

- aerodynamic centers should stay inside or near the physical tail surfaces;
- chordwise AC should remain in a plausible range such as roughly quarter-chord to mid-chord;
- CG sensitivity should be bounded tightly around measured values.

### 2. Tail Aerodynamic Parameters

These mainly affect force magnitude, force direction, and control effectiveness.

| parameter | main channels | role |
|---|---|---|
| `horizontal_tail_incidence_bias_deg` | `fz_b`, `my_b` | fixed horizontal-tail incidence or zero-angle offset |
| `fixed_horizontal_effectiveness` | `fz_b`, `my_b` | fixed horizontal-tail lift-slope scale |
| `elevon_effectiveness` | `fz_b`, `my_b`, `mx_b` | elevon lift/control effectiveness |
| `horizontal_tail_q_scale` | `fz_b`, `my_b`, `mx_b` | local dynamic-pressure scale for horizontal tail surfaces |
| `elevon_alpha_limit_deg` | large-deflection `my_b`, `mx_b` | saturation/limit for elevon effective angle of attack |
| vertical/rudder effectiveness | `fy_b`, `mz_b` | vertical-tail and rudder side-force effectiveness |
| `cd0`, `cd_k` | drag-related small components | drag assumptions; lower priority initially |

Initial priority should be the longitudinal tail parameters related to `my_b`, not all surfaces and all moments at once.

## Suggested Experiment Flow

### Step 1: Convention Check

Verify before calibration:

- elevon sign;
- rudder sign;
- left/right elevon mapping;
- elevon and rudder max-angle mapping;
- FLU/FRD frame conversion;
- moment reference point.

Reason: a sign or mapping error can make later sweeps meaningless.

### Step 2: Geometry/Reference Alignment

Hold aerodynamic effectiveness mostly fixed and sweep bounded geometry/reference parameters:

- horizontal-tail and elevon `x_ac`;
- elevon `y_ac`;
- vertical/rudder `x_ac` and `z_ac`;
- small CG sensitivity around measured values.

Selection should emphasize validation-set channel correlation, sign correctness, and expected control coupling, not only RMSE.

Questions to answer:

- Does symmetric elevon activity align mostly with `my_b`?
- Does differential elevon activity align mostly with `mx_b`?
- Does rudder activity align mostly with `mz_b` and/or `fy_b`?
- Does the improved geometry produce plausible moment arms?

### Step 3: Aerodynamic Effectiveness Alignment

With geometry fixed, sweep a small set of aerodynamic parameters:

- `horizontal_tail_incidence_bias_deg`;
- `fixed_horizontal_effectiveness`;
- `elevon_effectiveness`;
- `horizontal_tail_q_scale`;
- `elevon_alpha_limit_deg`;
- optional vertical/rudder effectiveness if focusing on `fy_b`/`mz_b`.

Primary target:

- `my_b` as a secondary moment result.

Secondary/diagnostic targets:

- `mx_b`, `mz_b`, and `fy_b`.

### Step 4: Train-Only Gain/Bias Wrapper

After the tail prior has reasonable structure, fit:

```text
M_corr_i = a_i M_tail_i + b_i
```

or a similarly low-dimensional per-channel gain/bias wrapper.

Purpose:

- correct residual scale and offset;
- avoid letting gain/bias hide sign/convention failures;
- separate physically plausible shape alignment from scalar calibration.

### Step 5: Compare Against Direct Moment Correction

Compare:

| model | purpose |
|---|---|
| zero/mean moment baseline | lower bound |
| raw tail prior | pure component prior |
| geometry-aligned tail prior | checks moment-arm plausibility |
| aerodynamically aligned tail prior | checks tail effectiveness plausibility |
| tail prior + gain/bias | low-dimensional calibrated component model |
| direct moment correction head | flexible upper/comparison baseline |

Interpretation:

- If tail prior + gain/bias approaches the direct moment head, the tail model explains a meaningful part of the moment residual.
- If direct correction remains much better, moment labels likely contain coupled wing/body/tail/reference-point/differentiation effects beyond the simple quasi-steady tail model.

## Paper Positioning

If results are good:

> The pitch-moment residual was partly consistent with a bounded tail-surface prior after geometry and effectiveness alignment, and a train-only gain/bias wrapper further reduced held-out error.

If results are mixed:

> The tail-prior diagnostic improved selected moment channels, especially pitch moment, but did not fully explain the rotational effective wrench. This supports treating moment prediction as an effective-wrench correction rather than as isolated tail-load identification.

## Current Recommendation

Prioritize `my_b`.

Do not let weak `fy_b`, `mx_b`, or `mz_b` results derail the main paper story. These channels are useful diagnostics and limitations, but the primary evidence remains `fx_b`/`fz_b` force-prior correction.

