# Force-Moment Arm Diagnostic Note

Date: 2026-05-25

## 核心问题

我们关心的是：如果已经能够较好预测 effective force，是否可以通过一个力臂来得到 effective moment。

更具体地说：

```text
M_hat = r_hat x F_hat
```

这个想法有物理直觉，因为力矩确实可以由力和作用点产生。但是对真实飞行日志中的 effective wrench 来说，不能简单假设存在一个固定力臂，使得：

```text
M_eff = r_fixed x F_eff
```

原因是日志中的 effective moment 是完整刚体转动残差：

```text
M_eff = I alpha + omega x I omega
```

它包含左右翼、尾翼、机身阻力、结构不对称、相位相关压力中心变化、自由气动力矩，以及标签重构误差等综合影响。

## 已完成诊断

诊断数据集：

```text
dataset/canonical_v0.2_training_ready_split_hq_v4_direct_airspeed_logsplit_paper_alt5_v1
```

诊断输出：

```text
/home/zn/flap-system-identification/artifacts/20260525_force_moment_arm_diagnostic
/home/zn/flap-system-identification/artifacts/20260525_force_moment_arm_diagnostic_subagent
```

### 1. 逐样本最佳等效力臂

对每个样本，用真实日志力和真实日志力矩反推最小范数力臂：

```text
r_perp = F x M / ||F||^2
M_recon = r_perp x F
```

结果：

```text
overall R2 = 0.943
test R2    = 0.940
parallel/free moment energy ≈ 5.7% - 6.0%
r_perp norm median ≈ 4.16e-4 m
r_perp norm p90    ≈ 1.68e-3 m
r_perp norm p99    ≈ 4.19e-3 m
```

解释：

这个结果说明，大部分日志力矩在几何上可以被某个瞬时等效力臂解释。但是这不是一个预测模型，因为每一帧的 `r_perp` 都使用了真实 `M_eff` 反推出来。它更像一个 diagnostic upper bound。

### 2. 固定力臂诊断

更接近物理模型的假设是，在 train logs 上拟合一个全局固定力臂：

```text
M_hat = r_fixed x F_eff
```

然后在 held-out logs 上评估。

结果：

```text
test overall R2 = 0.0566
all overall R2  = 0.0454
```

test split 按轴：

```text
mx_b R2 = 0.038
my_b R2 = 0.071
mz_b R2 = -0.165
```

拟合得到的全局力臂很小：

```text
r = [8.3e-5, -3.8e-5, -2.3e-5] m
|r| = 9.4e-5 m
```

即使放宽成：

```text
M = r x F + tau_0
```

test R2 也只有约 `0.104`。进一步放宽成任意线性映射：

```text
M = B F
```

test R2 也只有约 `0.136`，加常值项后约 `0.172`。

## 主要结论

这个实验不是说明“力不能产生力矩”。它说明的是：

```text
真实飞行中的 effective moment 不能由 net effective force 通过一个固定力臂稳定预测。
```

因此，力矩不能被简单看成力的附属量。它应该作为 full wrench 的独立部分建模，或者至少需要一个状态相关的结构化力矩模型。

## 对 DeLaurier baseline 的含义

DeLaurier model 可以提供一个 physically grounded force prior，但不能假设：

```text
DeLaurier force accurate => DeLaurier moment accurate
```

当前 DeLaurier moment 本质上主要来自：

```text
wing/tail force applied at assumed aerodynamic centers
M = r_assumed x F
```

而真实日志中的 moment 反映的是分布式载荷和动态压力中心的综合结果。即使质量、重心和转动惯量测得更准确，DeLaurier moment 仍然可能不准，因为主要误差来源可能不在刚体参数，而在 aerodynamic load distribution 和 dynamic center of pressure。

## 可以尝试的结构化方法

固定力臂失败以后，一个更合理的方向是预测状态相关等效力臂：

```text
F_hat = force_model(x)
r_hat = arm_model(x)
M_hat = r_hat(x) x F_hat(x)
```

但是只用 `r_hat x F_hat` 仍然有几何限制，因为任何 `r x F` 都垂直于 `F`，不能表示与 `F` 平行的自由力矩成分。诊断中大约 `6%` 的 moment energy 属于 parallel/free component。

因此更完整的结构是：

```text
F_hat = force branch(x)
r_hat = dynamic arm branch(x)
tau_free_hat = free-moment branch(x)

M_hat = r_hat x F_hat + tau_free_hat
```

其中 `r_hat` 应该解释主要的 force-induced moment，`tau_free_hat` 解释不能由单一合力作用点表示的部分。

英文方法名可以考虑：

```text
state-dependent equivalent moment arm
dynamic center-of-pressure moment head
force-arm structured moment head
wrench-structured neural head
```

## 论文中可以使用的表述

> To test whether the effective moment can be derived from the net effective force, we performed a force-arm diagnostic. A per-sample minimum-norm arm can reconstruct most of the moment energy, but this uses the ground-truth moment at each time step and therefore only represents a diagnostic upper bound. In contrast, a single fixed arm fitted on the training logs explains only a small fraction of the held-out moment variance. This indicates that the real-flight effective moment is not determined by the net force through a stationary center of pressure.

> This motivates treating the effective wrench as a full six-dimensional target, or using a structured moment head in which the predicted force acts through a state-dependent equivalent arm with an additional free-moment residual.

## 推荐论文定位

这部分不建议写成主贡献，除非后续真的实现并验证 dynamic arm head。当前最合适的位置是：

```text
diagnostic evidence / model design motivation
```

它支撑以下选择：

1. 不把 moment 简化成 fixed-arm force product。
2. DeLaurier 更适合作为 force prior，而 moment 需要 direct or residual modeling。
3. 后续可以探索 `M = r_hat x F_hat + tau_free_hat` 作为更有物理结构的 neural moment head。

