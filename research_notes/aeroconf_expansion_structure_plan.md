# AeroConf 论文扩展结构建议

日期：2026-05-21

## 总体判断

目标页数可以放在 12--14 页。不要为了页数把论文拆成很多一级 section；这篇更适合围绕一条主线展开：

> 如何从真实 outdoor flight logs 构造 effective wrench，并用这些数据校正和诊断 DeLaurier-style flapping-wing simulator prior 的 residual。

10 个一级 section 太碎。更合适的是 6--7 个 section，把相关内容合并。

## 推荐 Section 结构

| Section | 内容 | 页数目标 |
|---|---|---:|
| I. Introduction | motivation + related work 融合进去 | 2--2.5 |
| II. Real-Flight Effective-Wrench Dataset | platform、logging、effective-wrench reconstruction、preprocessing/split | 2.5--3 |
| III. Simulator Prior and Residual Model | DeLaurier prior、calibration、residual Transformer | 2.5--3 |
| IV. Evaluation Protocol | compared models、split、metrics | 1 |
| V. Results and Residual Diagnostics | main metrics、cross-log、ablation、phase/condition/frequency diagnostics | 3.5--4 |
| VI. Discussion and Limitations | simulator 意义、moment 问题、label 误差、未来闭环仿真 | 1--1.5 |
| VII. Conclusion | 简短总结 | 0.5 |

Related Work 不必单独作为一级 section。可以放在 Introduction 后半部分，或作为 Introduction 里的一个 subsection。DeLaurier prior 和 residual learning 也应合并到同一个模型 section，不要拆成两个一级标题。

## 最值得补充的内容

### 1. Real-Flight Effective-Wrench Dataset

这是第一优先级。当前内容可以从约 1000 words 扩到 1600--2000 words，但平台细节必须服务于 effective-wrench reconstruction 和 simulator residual。

建议补：

- 更完整的平台参数表：tail surfaces、flight controller、airspeed sensor、RTK-GNSS、logging rate。
- 数据处理流程图：`ULog -> synchronization/resampling -> phase correction -> effective wrench reconstruction -> split`。
- flight segment selection：哪些段被保留，哪些段被剔除。
- operating envelope 统计：airspeed、angle of attack、sideslip、flapping frequency、dynamic pressure 的分布图或表。
- effective-wrench reconstruction 的误差来源表：acceleration noise、attitude error、gyro differentiation、CG/inertia uncertainty、time alignment。

### 2. Effective-Wrench Reconstruction

建议作为 Dataset 里的 subsection，不单独升成一级 section。

这里要主动回答审稿人可能的问题：“这个 force/moment label 靠不靠谱？”

建议补：

- 为什么叫 effective wrench，而不是 aerodynamic wrench。
- force label 来自重力补偿后的刚体平动动力学。
- moment label 来自刚体转动动力学。
- angular acceleration 如何由 gyro rate 得到，是否滤波。
- inertia / CG 从哪里来。
- label 包含 tail、body、mechanism、disturbance，因此是 net non-gravitational effective wrench。

### 3. Simulator Prior and Residual Model

这是论文 “theory-guided” 的核心。建议把 DeLaurier prior、calibration 和 residual learning 放在同一个 section。

建议补：

- DeLaurier prior 的输入输出说明。
- calibration 参数表：参数、物理意义、初始值、bounds、optimized value。
- calibration 前后 RMSE 对比。
- 为什么 calibration 是 bounded low-dimensional，而不是让 prior 任意拟合。
- 为什么 force channels 用 residual，moment channels 用 direct neural head。
- Transformer 输入变量和 history window 的说明表。

### 4. Results and Residual Diagnostics

这是把论文扩成 AeroConf 完整稿的主要空间。

建议补：

- per-log RMSE/MAE，而不只是 aggregate。
- train/validation/test operating envelope 对比。
- input-group ablation：no phase / no airdata / no actuation / no history。
- phase correction ablation：raw phase vs corrected phase。
- history length sensitivity：例如 `H = 16, 32, 64, 128`。
- residual diagnostics 拆成更清楚的图：phase-binned、condition-binned、frequency-band、representative time-series。

如果只能新增两个实验，优先选：

1. phase correction / no phase ablation：直接支撑 wingbeat phase structure matters。
2. input-group ablation：直接支撑 residual can be explained by onboard-measurable flight, actuation, and airdata variables。

## 不建议扩展的内容

- 不要把师兄论文里的 GNC transfer、NPFG/L1/WC-L1 大段搬进来。
- 不要单独写很长的 Related Work。
- 不要把 Evaluation Protocol 写太长。
- 不要为了页数把 Discussion 写成泛泛的 future work。
- 不要在没有 closed-loop simulation validation 的情况下过度强调已经完成 simulation deployment。

## 推荐推进方式

先把当前稿件扩成 11--12 页的扎实版本，重点补 Dataset、Effective Wrench、Calibration table、Ablation。等这些内容成立后，再看 residual diagnostics 是否能自然扩到 14 页。

核心原则是：每个新增段落、表格和图都必须服务于同一个问题：

> how to correct a physics-based flapping-wing simulator using real-flight residual structure.
