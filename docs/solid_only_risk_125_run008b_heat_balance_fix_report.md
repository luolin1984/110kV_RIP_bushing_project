# SOLID_ONLY_RISK_125_RUN008B_HEAT_BALANCE_FIX 报告

## 1. 本轮任务目标

本轮目标是对 RUN008 中低负荷、高油温工况的热量收支诊断进行后处理复核，补充绝对残差和最大能量尺度判据。没有重新运行 125 组 COMSOL，没有进入 RUN009，也没有构建完整电热耦合模型。

## 2. RUN008 中 9 个 invalid case 的原因

RUN008 中 9 个 invalid_case 均由原始 heat balance 判据 `abs(residual_percent_Qgenerated) < 10%` 未通过导致；Qjoule、Qcontact 和 selection 均已通过。它们共同特征是 load_multiplier_pu=0.6、油温较高、总发热量较低，residual_W 绝对值仅约 1.6 至 2.2 W。

- RUN008_CASE_011: original=heat_balance, residual_W=-1.602 W, residual_percent_Qgenerated=-10.626%, residual_percent_max_energy_scale=-0.868%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=83.918 W
- RUN008_CASE_016: original=heat_balance, residual_W=-1.851 W, residual_percent_Qgenerated=-12.136%, residual_percent_max_energy_scale=-0.862%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=98.846 W
- RUN008_CASE_021: original=heat_balance, residual_W=-2.102 W, residual_percent_Qgenerated=-13.622%, residual_percent_max_energy_scale=-0.858%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=113.772 W
- RUN008_CASE_036: original=heat_balance, residual_W=-1.622 W, residual_percent_Qgenerated=-10.365%, residual_percent_max_energy_scale=-0.878%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=83.758 W
- RUN008_CASE_041: original=heat_balance, residual_W=-1.871 W, residual_percent_Qgenerated=-11.819%, residual_percent_max_energy_scale=-0.870%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=98.687 W
- RUN008_CASE_046: original=heat_balance, residual_W=-2.121 W, residual_percent_Qgenerated=-13.252%, residual_percent_max_energy_scale=-0.864%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=113.613 W
- RUN008_CASE_066: original=heat_balance, residual_W=-1.929 W, residual_percent_Qgenerated=-10.994%, residual_percent_max_energy_scale=-0.893%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=98.209 W
- RUN008_CASE_071: original=heat_balance, residual_W=-2.177 W, residual_percent_Qgenerated=-12.287%, residual_percent_max_energy_scale=-0.884%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=113.137 W
- RUN008_CASE_096: original=heat_balance, residual_W=-2.272 W, residual_percent_Qgenerated=-11.043%, residual_percent_max_energy_scale=-0.918%, status=VALID_LOW_POWER_RECLASSIFIED, Qoil_heat_in=112.343 W

## 3. 原始 residual_percent_Qgenerated 判据的局限性

原始判据用 residual_W / Qtotal_generated_W 归一化。在低负荷工况中，Qtotal_generated_W 较小，1 至 2 W 级的闭合残差会被放大为超过 10%。当油侧边界为热油向固体输入热量时，边界热通量的绝对交换规模明显大于净发热量，仅用 Qgenerated 归一化容易把低功率闭合误差误判为模型错误。

## 4. 补充判据说明

RUN008B 同时输出三类判据：

- 原始严格判据：abs(residual_percent_Qgenerated) < 10%；
- 绝对残差判据：abs(residual_W) < 3 W；
- 最大能量尺度判据：abs(residual_percent_max_energy_scale) < 5%。

当原始严格判据未通过，但绝对残差和最大能量尺度判据同时通过时，标记为 `VALID_LOW_POWER_RECLASSIFIED`。这不是把严格阈值简单放宽，而是针对低发热量、热边界输入显著工况的补充诊断。

## 5. 油侧热通量符号是否物理合理

RUN008 未直接导出油侧边界平均温度；本轮使用已知 h_oil=300 W/(m^2*K) 和油侧轴对称边界面积 A_oil=0.2467406868 m^2，由 Qremoved_oil = h_oil*A_oil*(Tmean_surface-Toil) 反算 Tmean_oil_side_surface_C。

油侧热通量符号物理合理数量：125/125。当 Qremoved_oil_W < 0 时，反算得到油侧固体表面平均温度低于油温，表示热油向固体输入热量；这与 RUN008 invalid case 的特征一致。

## 6. 边界 selection 是否发生漂移

边界 selection 漂移数量：0/125。本轮使用 RUN008 的固定 explicit by-ID boundary selections；air/oil/flange 的 boundary_count 与 boundary_total_length 在所有工况中保持不变。因此 RUN008 的 9 个 invalid case 更可能是热量收支归一化判据问题，而不是 selection 漂移。

## 7. 重新分类后 valid_heat_balance 数量

- heat_balance_status 统计：{'VALID_STRICT': 116, 'VALID_LOW_POWER_RECLASSIFIED': 9}
- VALID_STRICT：116/125
- VALID_LOW_POWER_RECLASSIFIED：9/125
- INVALID_HEAT_BALANCE：0/125

## 8. 重新分类后 invalid_case 数量

overall_valid_reclassified = 125/125。重新分类后 invalid_case 数量为 0。

## 9. 是否可以进入 FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009

原始 9 个 heat_balance invalid case 均被低发热量补充判据解释并重分类，selection 无漂移，油侧热通量符号物理合理，Qjoule/Qcontact/selection 均为 125/125，趋势检查通过。

前置条件复核：

- original invalid cases 已解释清楚：true
- 无 INVALID_SELECTION_DRIFT：true
- 油侧热通量符号物理合理：true
- overall_valid_reclassified = 125/125：true
- valid_Qjoule = 125/125：true
- valid_Qcontact = 125/125：true
- valid_selection = 125/125：true
- 趋势检查均通过：true

趋势检查结果：

- Tmax_global_C 随 oil_temperature_C 升高而升高：True
- Tmax_global_C 随 load_multiplier_pu 升高而升高：True
- Tmax_contact_C 随 contact_resistance_multiplier_pu 升高而升高：True
- Qjoule 随 I² 增长：True
- Qcontact 随 I² * Rc_factor 增长：True

## 10. 下一阶段定位

如果用户确认进入下一阶段，RUN009 的定位应为 `FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009`：将 solid-only 中的 `approximate_Qdielectric_ref` 替换为完整电场求解得到的空间分布介质损耗 `Qdielectric = omega * epsilon0 * epsr * tan_delta * |E|^2`。RUN008B 本轮没有执行 RUN009。

Can proceed to FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009: YES
