# Channel Excitation / SNR Diagnostics 记录

本文档记录 2026-06-03 做的一组 channel excitation / SNR diagnostics，用于解释为什么 measured-massprops + phase-structured correction 中 `fx_b`, `fz_b`, `my_b` 表现较好，而 `fy_b`, `mx_b`, `mz_b` 表现较弱。

分析脚本：

```text
scripts/analyze_channel_excitation_snr.py
```

输出目录：

```text
analysis/channel_excitation_snr/
```

主要输出文件：

```text
analysis/channel_excitation_snr/channel_excitation_summary.csv
analysis/channel_excitation_snr/feature_group_ridge_best_deployable.csv
analysis/channel_excitation_snr/feature_group_ridge_r2.csv
analysis/channel_excitation_snr/condition_bin_excitation.csv
analysis/channel_excitation_snr/mx_roll_subset_metrics.csv
analysis/channel_excitation_snr/frequency_structure_summary.csv
analysis/channel_excitation_snr/summary.md
analysis/channel_excitation_snr/figures/channel_excitation_summary.pdf
analysis/channel_excitation_snr/figures/condition_bin_excitation_snr.pdf
```

## 1. Channel excitation summary

每个 channel 统计了 label 标准差、`p95-p5`、corrected RMSE、`RMSE/std` 和 `R2`。

| Channel | std | p95-p5 | corrected RMSE | RMSE/std | R2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `fx_b` | 4.472 | 13.888 | 1.419 | 0.317 | 0.899 |
| `fy_b` | 1.045 | 3.261 | 0.889 | 0.851 | 0.276 |
| `fz_b` | 8.695 | 27.643 | 2.624 | 0.302 | 0.909 |
| `mx_b` | 0.672 | 2.215 | 0.592 | 0.881 | 0.224 |
| `my_b` | 0.628 | 1.983 | 0.282 | 0.449 | 0.798 |
| `mz_b` | 0.257 | 0.843 | 0.221 | 0.859 | 0.263 |

主要观察：

- `fx_b` 和 `fz_b` 的 label variance 明显大，且 `RMSE/std` 很低，说明模型不是靠目标本身很小取巧，而是抓住了主要变化。
- `my_b` 的 label variance 不如 force channel 大，但 R2 高、`RMSE/std` 中等偏好，是当前 moment channels 里最可信的 supporting result。
- `fy_b`, `mx_b`, `mz_b` 的 normalized error 接近 `0.85-0.88`，说明误差已经接近目标自身变化尺度。

可以支持的表述：

> The strongest channels are not merely the largest channels in absolute RMSE terms; they also have substantially lower normalized error relative to their target variation.

## 2. Deployable feature ridge diagnostics

为了判断“好通道为什么好”，用 deployable features 做了简单 ridge linear model。特征只使用仿真或机载可获得变量：

- phase harmonics
- airspeed / dynamic pressure / pitch-AoA proxy / beta proxy / flapping frequency
- motor / elevon / rudder commands
- body rates `p`, `q`, `r`

注意：`p_dot`, `q_dot`, `r_dot` 没有作为 deployable input 使用，因为 angular acceleration 参与 moment label 构造；如果把它们放入模型，会形成诊断泄漏。

Best deployable feature-group R2：

| Channel | Best deployable feature group | R2 |
| --- | --- | ---: |
| `fx_b` | all deployable features | 0.868 |
| `fy_b` | all deployable features | 0.243 |
| `fz_b` | all deployable features | 0.875 |
| `mx_b` | all deployable features | 0.176 |
| `my_b` | all deployable features | 0.711 |
| `mz_b` | phase only | 0.125 |

主要观察：

- `fx_b`, `fz_b`, `my_b` 即使用简单线性模型和 deployable features 也能解释较多 target variation。
- `fy_b`, `mx_b`, `mz_b` 很难被这些 deployable features 解释。
- 这支持“好通道有更强可观测结构，弱通道可解释输入较弱或 label/noise 占比更高”的叙事。

额外诊断：

- 如果使用 angular-derivative diagnostic features，`mx_b`, `my_b`, `mz_b` 的 R2 接近 1。
- 这不应作为模型结果使用，只说明 moment labels 与 angular acceleration label chain 高度相关。

## 3. Frequency structure diagnostics

引用已有 residual frequency summary，观察每个通道 residual energy 的 dominant component。

| Channel | Dominant component | Dominant true energy fraction | Remaining fraction of true |
| --- | --- | ---: | ---: |
| `fx_b` | `flap_main` | 0.516 | 0.025 |
| `fy_b` | broadband high-frequency | 0.428 | 0.964 |
| `fz_b` | `flap_main` | 0.787 | 0.031 |
| `mx_b` | broadband high-frequency | 0.314 | 1.005 |
| `my_b` | `harmonic_2f` | 0.452 | 0.146 |
| `mz_b` | broadband high-frequency | 0.465 | 0.768 |

主要观察：

- `fx_b` 和 `fz_b` 的 dominant residual energy 在 wingbeat fundamental，且 correction 后 dominant band energy 只剩约 `2.5%` 和 `3.1%`。
- `my_b` dominant component 为 `harmonic_2f`，correction 后剩余约 `14.6%`，说明它也有可重复结构。
- `fy_b`, `mx_b`, `mz_b` dominant component 更偏 broadband high-frequency，correction 后剩余比例高，说明可重复结构弱或噪声/扰动占比高。

可以支持的表述：

> The channels with strong prediction performance also contain repeatable frequency-localized residual structure, whereas weaker channels are dominated more by broadband high-frequency residual energy.

## 4. Condition-bin excitation diagnostics

按每个 channel 对应的关键变量分 bin，并统计每个 bin 内的 label std、corrected RMSE、`RMSE/std` 和 sample count。

分 bin 变量：

- `fx_b`: cycle flapping frequency
- `fy_b`: beta proxy
- `fz_b`: pitch/AoA proxy
- `mx_b`: smoothed `p_dot`
- `my_b`: elevon sum
- `mz_b`: rudder command

主要图：

```text
analysis/channel_excitation_snr/figures/condition_bin_excitation_snr.pdf
```

主要观察：

- `fx_b` 和 `fz_b` 在各 bin 中 label std 明显，且多数 bin 的 `RMSE/std` 较低。
- `my_b` 在 elevon-sum bins 中 `RMSE/std` 大约为 `0.43-0.48`，比较稳定。
- `fy_b` 和 `mz_b` 在各 bin 中 `RMSE/std` 基本维持在 `0.84-0.88`。
- `mx_b` 在 `p_dot` bins 中表现很差，部分 bin 的 `RMSE/std` 大于 2 或 3，说明它不是简单缺少某个工况 bin 的数据。

## 5. Roll-specific `mx_b` diagnostics

为了专门检查 `mx_b`，做了以下 subset：

- all samples
- `|p_dot_smooth| > p75`
- `|p_dot_smooth| > p90`
- `|p| > p75`
- `|p| > p90`
- `|roll angle| > p75`
- `|roll angle| > p90`
- `|elevon_diff| > p75`
- `|elevon_diff| > p90`

结果摘要：

| Subset | n | `mx` std | RMSE | RMSE/std | R2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| all | 60658 | 0.672 | 0.592 | 0.881 | 0.224 |
| `|p_dot_smooth| > p75` | 15164 | 1.185 | 1.005 | 0.848 | 0.280 |
| `|p_dot_smooth| > p90` | 6066 | 1.506 | 1.332 | 0.884 | 0.218 |
| `|p| > p75` | 15159 | 0.731 | 0.683 | 0.933 | 0.129 |
| `|p| > p90` | 6065 | 0.755 | 0.744 | 0.986 | 0.028 |
| `|elevon_diff| > p75` | 15165 | 0.818 | 0.751 | 0.918 | 0.157 |
| `|elevon_diff| > p90` | 6066 | 0.902 | 0.840 | 0.931 | 0.132 |

主要观察：

- 高 `|p_dot|` subset 中 `mx_b` 的 std 确实变大，但 `RMSE/std` 仍然约 `0.85-0.88`。
- 高 roll-rate 或高 elevon-diff subset 中结果没有明显变好，有时反而更差。
- 因此 `mx_b` 弱项不能简单解释为“roll excitation 不够”。更合理的解释是：`mx_b` 同时受到 angular-acceleration derivative、reference point、timing alignment、smoothing 或 moment label uncertainty 影响。

## 6. 论文中建议使用的结论

可以比较稳地写：

> The channels with the strongest prediction performance are also the channels with sustained excitation and repeatable phase/condition/frequency structure. The weaker channels have higher normalized error and more broadband residual energy. In particular, the roll-moment channel does not become reliable even in high-roll-transient subsets, suggesting derivative, reference-point, timing, or smoothing sensitivity rather than weak excitation alone.

中文解释：

- `fx_b` 和 `fz_b` 是主力/纵向力通道，variance 大、phase/frequency structure 强、deployable features 可解释性强，所以结果好。
- `my_b` 是当前 moment channels 中最有结构、最可预测的通道，可以作为 supporting result。
- `fy_b`, `mx_b`, `mz_b` 不应被隐藏，而应作为限制：它们的 residual 更 broadband，normalized error 高，可解释输入弱；其中 `mx_b` 还显示出更强的 derivative/reference/timing sensitivity。

## 7. 对 claim framing 的影响

建议论文主线不要改成“只做三个 channel”，而是：

1. six-axis effective wrench reconstruction 是问题定义和 dataset/formulation 贡献；
2. simulator-prior correction 的最强证据集中在 force channels，尤其 `fx_b` 和 `fz_b`；
3. `my_b` 是 effective moment prediction 的 strongest supporting result；
4. `fy_b`, `mx_b`, `mz_b` 是 limitations，并通过 excitation/SNR diagnostics 解释。

推荐表述：

> We formulate and report six-axis effective-wrench reconstruction, but the strongest correction evidence is channel-specific: axial and vertical force residuals are strongly structured and corrected, pitch moment is predicted well as an effective rotational-wrench channel, and lateral force plus roll/yaw moments remain the main limitations.
