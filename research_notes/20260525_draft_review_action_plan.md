# 20260525 Draft Review Action Plan

本文档凝练 `20260525draft.pdf` 的审查意见，用作 AeroConf 版本后续扩写、改稿和实验补强的行动清单。

## Overall Verdict

当前 9 页版本直接投 AeroConf 风险较高，判断为 **weak reject / borderline reject**。论文已有可投稿核心：

> real flight logs -> effective wrench labels -> DeLaurier-style prior -> calibrated prior -> neural residual/direct prediction -> residual structure diagnostics

主要问题不是主题弱，而是 **claim 与 evidence 尚未闭合**。当前结果强在 log-based supervised effective-wrench prediction，但标题、摘要和结论容易让审稿人期待 simulator-level validation。

## Core Reframing

建议把论文主线收紧为：

> A flight-log-based grey-box identification method for correcting the force component of a DeLaurier-style flapping-wing simulator prior, with direct moment prediction treated as a practical channel-aware component under label and prior uncertainty.

应避免把当前工作写成：

- 已验证的 closed-loop flapping-wing simulator；
- RL controller 或 simulation-based RL paper；
- 完整 six-axis aerodynamic residual model；
- 纯 Transformer benchmark。

更安全的定位是：

- real-flight effective-wrench identification；
- DeLaurier prior alignment and calibration；
- force-channel residual correction；
- direct effective-moment prediction under uncertainty；
- residual structure diagnostics as simulator-gap evidence。

## Highest-Risk Reviewer Attacks

1. **Effective-wrench label credibility is under-proven.**  
   Force label is plausible, but moment label depends on PX4 angular acceleration, CAD-seeded inertia, CG/reference-point assumptions, and differentiation noise. Qualitative error-source discussion is not enough.

2. **DeLaurier moment and effective moment are physically underspecified.**  
   The paper says the prior outputs six-axis wrench, but the final method uses force residual correction and direct moment prediction. This must be explained as a channel-aware engineering choice, not hidden.

3. **Metrics and tables are vulnerable.**  
   Current issues include mixed-unit overall RMSE, row-count differences across models, abstract/table numeric inconsistency, and incomplete same-row per-channel comparisons.

4. **Simulation claim is too strong for the evidence.**  
   Current experiments demonstrate held-out log prediction, not trajectory replay, open-loop rollout, closed-loop simulation, controller evaluation, or RL training.

5. **Method reproducibility is not yet AeroConf-level.**  
   Missing details include DeLaurier implementation, calibration bounds/final values, solver, weights, network architecture, input dimensions, history length, loss, optimizer, and ablations.

## Must Fix Before Submission

### 1. Correct Abstract and Conclusion Claims

- Replace any remaining “letter” wording with “paper”.
- Make all reported numbers consistent with result tables.
- Say “toward simulation correction” or “a prerequisite step toward real-flight-corrected simulation”, not validated simulator performance.
- Explicitly distinguish log-based effective-wrench prediction from closed-loop simulation validation.

### 2. Strengthen Effective-Wrench Definition

Add or revise content in Sec. II:

- body FRD frame, NED frame, CG, IMU, and wrench reference point；
- whether moment is about CG or another reference point；
- whether DeLaurier output is transformed to the same reference point；
- mass, CG, inertia sources；
- angular acceleration source and filtering/smoothing assumptions；
- why the target is an effective non-gravitational wrench rather than pure aerodynamic load。

Best figure to add:

> Vehicle / sensor / coordinate-frame / wrench-reference diagram.

### 3. Quantify Label Uncertainty

At minimum, add one sensitivity analysis:

- inertia perturbation, e.g. +/-20%；
- CG offset, e.g. +/-5--10 mm if metadata supports it；
- angular-acceleration smoothing sensitivity；
- force label sensitivity to acceleration smoothing if relevant。

Write moment results as lower-confidence effective rotational-wrench fitting, not high-confidence aerodynamic moment identification.

### 4. Explain DeLaurier Prior and Calibration

Add a dedicated method table:

- wing strip or aerodynamic discretization；
- wing kinematics from phase/frequency；
- incidence, twist, induced drag, wing normal/chordwise scales；
- tail/body/fuselage terms；
- output frame and reference point；
- calibration parameters, nominal values, bounds, optimized values；
- optimizer/solver, loss, weights, train-only calibration protocol。

The calibrated prior should be shown separately before neural residual learning.

### 5. Rebuild Main Result Tables

All compared models should use the same aligned evaluation rows.

Preferred table structure:

- per-channel RMSE；
- per-channel MAE；
- per-channel RMSE/sigma or NRMSE；
- per-channel R2；
- separate force and moment aggregates；
- optional dimensionless normalized aggregate。

Avoid presenting a single “overall RMSE” that mixes N and N m as the main claim.

### 6. Add Representative Held-Out Time-Series Figure

Add one figure using a held-out test log:

- effective label；
- calibrated prior；
- hybrid prediction；
- remaining residual；
- at least `fx_b`, `fy_b`, `fz_b`；
- optionally one moment channel, e.g. `my_b`, with cautious wording。

This figure is important for AeroConf readers because it shows actual flight-log behavior rather than only sample-level statistics.

### 7. Add Ablations

Minimum useful ablations:

- phase ablation: no phase / raw or sin-cos phase / corrected phase；
- temporal history: MLP vs temporal model, and at least one history-length comparison；
- output semantics: full direct / full residual / force residual + moment direct；
- input groups: state only / +actuation / +phase / +airdata or wind；
- optional smoothing sensitivity for label construction。

Do not claim “Transformer is best” unless the comparison table is included.

### 8. Redraw Residual Structure Diagnostics

Current residual-structure figure should be made more readable.

Recommended split:

- Figure A: force residual phase and frequency structure for main force channels；
- Figure B: condition-binned RMSE with bin sample counts；
- Moment diagnostics separate or clearly marked as lower-confidence。

Use wording such as “repeatable effective-wrench discrepancy” rather than “not random aerodynamic mechanism”.

## Should Fix If Space Allows

1. **Flight campaign table**  
   Include date, log count, retained duration, valid samples, mission type, altitude/speed range, and wind estimate summary.

2. **Log-level split map**  
   Show whole-log split by date/log, so the leakage defense is visually clear.

3. **Leave-one-date-out stress test**  
   If feasible, this directly addresses date/generalization concerns. Even degraded results are useful if framed as a stress test.

4. **Per-log error distribution**  
   Add boxplot or table of per-log RMSE so results are not dominated by long logs or correlated samples.

5. **Side-force limitation analysis**  
   Explain weak `fy_b` performance through lateral excitation, sideslip/wind estimation, yaw/side-force coupling, and label noise.

6. **Moment failure analysis**  
   Show why DeLaurier moment prior is not reliable enough for residual correction, then justify direct moment prediction.

## Nice To Have

1. **Short-horizon trajectory replay**  
   Add 1--3 s open-loop replay in IsaacLab using held-out logs. This would strongly support the “toward simulator correction” claim.

2. **Reproducibility paragraph**  
   Describe logs, split manifest, preprocessing script, calibration config, and model config if they can be shared.

3. **OOD/envelope warning**  
   Define that the learned correction should be used only within the retained operating envelope unless further validation is done.

## Recommended Section Organization

### I. Introduction

- Compress future RL/perception/grasping motivation.
- Focus on complete-vehicle flapping-wing effective-wrench modeling.
- State the gap: outdoor logs + effective wrench + DeLaurier prior + residual diagnostics.
- End with conservative contribution statements.

### II. Vehicle, Flight Logs, and Effective-Wrench Labels

1. Flapping-wing platform and sensor setup；
2. Flight campaign and retained operating envelope；
3. Effective-wrench reconstruction and label uncertainty。

### III. DeLaurier-Style Simulator Prior and Calibration

1. Aerodynamic prior implementation；
2. Bounded physical calibration；
3. Why channel-aware prediction is needed。

### IV. Causal Neural Residual Model

1. Inputs and causality boundary；
2. Model architectures and training；
3. Force residual plus direct moment output。

### V. Evaluation Protocol

1. Whole-log split and date-stratified cross-validation；
2. Metrics and normalization；
3. Baselines and ablations。

### VI. Results and Discussion

1. Calibration improves but does not close the gap；
2. Held-out log prediction；
3. Cross-log/date-stratified robustness；
4. Ablations；
5. Residual structure diagnostics；
6. Limitations。

### VII. Conclusion

Short conclusion aligned with evidence. State clearly that simulator rollout remains future work unless new replay results are added.

## Safer Contribution Statements

1. We formulate a real-flight effective-wrench identification problem for a bird-scale flapping-wing vehicle by reconstructing body-frame non-gravitational force and moment labels from outdoor PX4 flight logs and aligning them with a DeLaurier-style simulator prior under a whole-log evaluation protocol.

2. We develop a channel-aware grey-box predictor in which a bounded, training-log-calibrated DeLaurier prior is retained for force-channel residual correction, while low-variance moment channels are predicted directly to account for reference-point, inertia, and differentiation sensitivity.

3. We show on held-out whole-log and date-stratified evaluations that the learned force residual removes repeatable wingbeat-phase, flapping-frequency, and flight-condition-dependent discrepancies left by the calibrated prior, while identifying side-force and moment prediction as the main remaining limitations.

## Claim Wording Rules

Use:

- “effective wrench”；
- “simulator-to-flight discrepancy”；
- “log-based prediction”；
- “within the retained outdoor operating envelope”；
- “a prerequisite step toward real-flight-corrected simulation”；
- “comparable accuracy with interpretable force residual decomposition”。

Avoid or qualify:

- “pure aerodynamic force/moment”；
- “validated simulator”；
- “closed-loop simulation performance”；
- “broad generalization”；
- “six-axis DeLaurier residual correction”；
- “Transformer superiority” without an ablation table。

## Immediate Next Work Package

The most efficient next revision sequence is:

1. Fix Abstract/Conclusion claims and numeric consistency.
2. Add coordinate-frame/reference-point figure and revise effective-wrench section.
3. Add DeLaurier calibration parameter table.
4. Recompute same-row metrics and rebuild result tables.
5. Add one held-out time-series figure.
6. Add at least phase/output-semantics ablations.
7. Redraw residual structure diagnostics.

