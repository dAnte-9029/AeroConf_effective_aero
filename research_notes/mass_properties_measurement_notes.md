# 机体与机翼质量属性测量记录

本文档用于记录后续实测质量、重心和惯量矩阵时采用的坐标系与合成规则。目标是让实测数据能同时服务于 effective-wrench label、论文说明和后续 IsaacLab/低维仿真模型。

## 1. 总体坐标约定

飞控日志和当前 system-identification metadata 采用机体系 `FRD`：

- `x`: forward
- `y`: right
- `z`: down

因此所有最终进入论文、metadata 和 label reconstruction 的质量属性都应表达在 `FRD` 机体系下。

建议区分两个 frame：

- `U_FRD`: URDF 原点处的 FRD 测量坐标系。原点取 URDF/base link 原点，但坐标轴人为定义为 FRD。它不一定等同于 URDF link frame。
- `I_FRD`: 飞控 IMU 原点处的 FRD 坐标系。当前 metadata 中 `body_reference_origin` 和 `cg_reference_origin` 都是 `imu_origin`。

测量时可以先在 `U_FRD` 下记录，最后转换到 `I_FRD`：

```text
r_cg^I_FRD = r_cg^U_FRD - r_imu^U_FRD
```

如果 IMU 安装轴与定义的 body FRD 不完全平行，则还需要加入 IMU 相对 `U_FRD` 的旋转矩阵。

## 2. 机体测量

机体测量建议针对“不含可拆机翼”的主体构型进行，包含机身、尾翼、飞控、电池、传感器、扑翼机构中留在机体上的部分，以及实际飞行时固定在机体上的线缆和安装件。

需要记录：

```text
m_body = <待填> kg
r_cg_body^U_FRD = [<待填>, <待填>, <待填>] m
r_imu^U_FRD = [<待填>, <待填>, <待填>] m
I_body,cg^FRD = diag([<待填>, <待填>, <待填>]) kg*m^2
```

重心测量：

- 四个起落架接触点坐标统一在 `U_FRD` 下测量。
- 四点称重主要给出重心在支撑平面内的投影，即 `x_cg` 和 `y_cg`。
- `z_cg` 建议用吊线法、侧向/俯仰倾斜称重法，或可靠的几何测量补充。

惯量测量：

- 主对角项建议用双线摆分别测量绕 `x`、`y`、`z` 轴的转动惯量。
- 第一版可以只使用对角惯量矩阵；非对角项如果没有可靠测量，显式记为 0 或待测，不要隐含假设。
- 惯量应为绕机体自身重心、并在 FRD 轴下表达的惯量。

### 2.1 机体惯量记录

机体当前质量和重心记录为：

```text
m_body = 0.78261 kg
r_cg_body^U_FRD = [-0.13103, 0.00625, -0.01500] m
```

机体三轴惯量采用双线摆测量，当前推荐值为：

```text
I_body,cg^U_FRD = diag([2.98e-3, 2.316e-2, 1.987e-2]) kg*m^2
```

其中：

```text
Ixx_body = 2.98e-3 kg*m^2
Iyy_body = 2.316e-2 kg*m^2
Izz_body = 1.987e-2 kg*m^2
```

`Ixx` 测量参数：

```text
L = 0.610 m
2a = 0.086 m
d = 0
```

五次重复结果稳定，推荐 `Ixx_body = 2.98e-3 kg*m^2`。

`Iyy` 测量参数：

```text
L = 0.550 m
2a = 0.306 m
d = 0
```

六次重复结果稳定，推荐 `Iyy_body = 2.316e-2 kg*m^2`。

`Izz` 测量参数：

```text
L = 0.520 m
2a = 0.395 m
d = 0.030 m
axis_alignment_uncertainty ~= 5 deg
```

`Izz` 的双线摆摆轴相对机体重心有约 `3 cm` 偏距，因此按平行轴定理修正：

```text
Izz_body = Izz_axis - m_body d^2
```

修正量为：

```text
m_body d^2 = 0.78261 * 0.030^2 = 7.04e-4 kg*m^2
```

原始摆轴惯量均值约为 `2.057e-2 kg*m^2`，修正后推荐：

```text
Izz_body = 1.987e-2 kg*m^2
```

测量时机体 `z` 轴与竖直方向约有 `5 deg` 夹角。该项记录为轴对准不确定性；若横向惯量差异较大，可能带来数个百分点量级的混轴误差。

## 3. 右翼单独测量

右翼拆下后单独测量。建议定义右翼中位测量系：

```text
W_R0: right-wing neutral measurement frame
origin = 右翼转动轴与前缘参考线交点
axes = 机翼扑动角为 0 deg 时，与机体 FRD 平行
```

其中 `0 deg` 指扑动角中位，也就是机翼平着的测量姿态。

需要记录：

```text
m_R = <待填> kg
r_cg_R^W_R0 = [<待填>, <待填>, <待填>] m
p_W_R0^U_FRD = [<待填>, <待填>, <待填>] m
I_R,cg^W_R0 = diag([<待填>, <待填>, <待填>]) kg*m^2
```

如果 `W_R0` 轴与 `U_FRD` 轴完全平行，则中位姿态下：

```text
R_U_W_R0 = I
r_cg_R^U_FRD = p_W_R0^U_FRD + r_cg_R^W_R0
I_R,cg^U_FRD = I_R,cg^W_R0
```

如果左右翼都实测，左翼同理定义 `W_L0`。如果只测右翼并镜像得到左翼，则镜像时注意：

- `y` 坐标取反。
- 对角惯量 `Ixx, Iyy, Izz` 不变。
- 如果未来使用完整惯量矩阵，`Ixy` 和 `Iyz` 镜像后变号，`Ixz` 不变。

### 3.1 右翼惯量记录

右翼当前采用如下质量属性记录：

```text
m_R = 0.06077 kg
r_cg_R^W_R0 = [-0.06040, 0.29394, 0.00000] m
```

其中 `z_cg=0` 是薄平面机翼假设。测量时机翼为竖直平面，面外厚度和面外质量偏置相对较小，因此面外重心偏移取 0。

右翼面外惯量 `Izz` 采用双线摆测量。参数和推荐值为：

```text
L = 0.580 m
2a = 0.690 m
a = 0.345 m
d = 0.10606 m
Izz_R = 3.71e-3 kg*m^2
```

其中第 3、4 次双线摆结果明显偏低，可能由释放、计时或摆动状态不一致造成；推荐值采用较一致的第 1、2、5、6 次。

右翼面内惯量 `Ixx` 和 `Iyy` 不采用双线摆直测结果。实际绕面内轴摆动时空气阻尼过强，振动在一到两个周期内明显衰减，周期不可靠。因此当前使用薄平面机翼近似和已有右翼平面测量数据估计 `Ixx/Iyy` 比例：

```text
source_points = /home/zn/IsaacLab/source/flapping_bot/scripts/data/right_wing_te_polyline_mm.json
source_chord_csv = /home/zn/IsaacLab/outputs_DeLaurier/right_wing_te_fit_poly5_gap50.csv
```

用拟合弦长分布计算平面面积二阶矩，并用实测 `Izz_R` 归一化，约束满足：

```text
Izz_R ~= Ixx_R + Iyy_R
```

得到推荐惯量：

```text
I_R,cg^W_R0 = diag([2.70e-3, 1.01e-3, 3.71e-3]) kg*m^2
```

这个结果应在论文和 metadata 中标注为：`Izz` 为双线摆测量，`Ixx/Iyy` 为基于平面弦长分布的薄翼估计。

## 4. 中位姿态质量属性合成

论文和当前 effective-wrench label 建议先使用中位姿态的固定质量属性。总质量：

```text
m_total = m_body + m_R + m_L
```

总重心：

```text
r_cg,total = (m_body r_cg,body + m_R r_cg,R + m_L r_cg,L) / m_total
```

总惯量用平行轴定理合成。对每个部件 `i`：

```text
I_i,total_cg = I_i,cg + m_i * ((d_i^T d_i) I_3 - d_i d_i^T)
d_i = r_cg,i - r_cg,total
```

最终得到：

```text
I_total,cg^FRD = sum_i I_i,total_cg
```

最后将总重心从 `U_FRD` 转换到当前 metadata 使用的 `I_FRD`：

```text
r_cg,total^I_FRD = r_cg,total^U_FRD - r_imu^U_FRD
```

## 5. 扑动时的处理边界

如果机翼被看作刚体 link，扑动角为 `theta` 时，右翼质量属性可以通过刚体旋转更新：

```text
R_U_WR(theta) = R_hinge(theta) R_U_W_R0
r_cg_R(theta) = p_hinge_R + R_U_WR(theta) r_cg_R^W_R0
I_R,cg(theta) = R_U_WR(theta) I_R,cg^W_R0 R_U_WR(theta)^T
```

但只在低维单刚体模型里更新 time-varying inertia 并不等于完整处理扑翼惯性，因为还会涉及机翼相对机身运动产生的动量、关节反作用力、离心/科氏项和 `dI/dt` 项。

因此当前建议是：

- 论文和 effective-wrench reconstruction 使用中位姿态的固定总质量、重心和惯量。
- 把扑动刚体惯性、柔性翼形变、added-mass、机构反作用和未建模气动效应都视为 effective wrench 中的一部分。
- 如果后续 IsaacLab 使用显式 articulated wing links，则把实测机翼质量、重心和惯量填入左右翼 link，让仿真器处理刚体扑动惯性。
- 柔性翼导致的惯量变化、气动相位滞后和翼面变形可以交给 residual model 或 domain randomization 处理。

论文中可以表述为：

```text
Mass properties were measured in the neutral wing pose. The effective-wrench reconstruction uses a fixed neutral-pose inertia tensor; therefore periodic inertial effects from flapping motion, wing flexibility, and mechanism reaction loads are included in the reconstructed effective wrench rather than isolated as pure aerodynamic loads.
```
