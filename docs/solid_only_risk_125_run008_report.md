# SOLID_ONLY_RISK_125_RUN008 阶段报告

## 1. 本轮任务目标

本轮基于 RUN006/RUN007 已验证的 source-fixed、explicit by-ID、solid-only thermal diagnostic model，完成 5 x 5 x 5 共 125 组核心风险边界扫描。目标是扩展负荷倍率、油温和接触电阻倍率范围，检查热源分解、热量收支和风险分区。本轮不是完整电热耦合主实验，也不是最终 SCI 论文结果。

## 2. 与 RUN006/RUN007 的关系

RUN006 用于修正导体焦耳热和接触热源归一化；RUN007 用 27 组小规模扫参验证了显式 by-ID selection、热源缩放和热量收支。RUN008 在此基础上扩展为 125 组风险边界扫描。RIP 介质损耗仍采用 `approximate_Qdielectric_ref`，不能写成真实电场耦合介质损耗。

## 3. 125 组工况矩阵

load_multiplier_pu = [0.6, 0.8, 1.0, 1.2, 1.4]；oil_temperature_C = [65, 75, 85, 95, 105]；contact_resistance_multiplier_pu = [1, 2, 5, 10, 20]。固定条件为 voltage_multiplier_pu=1.0、air_temperature_C=25、wind_speed_m_s=1.0、tan_delta_multiplier_pu=1.0、rip_aging_conductivity_multiplier_pu=1.0、pollution_multiplier_pu=1.0。

## 4. 模型边界说明

本轮沿用 RUN006/RUN007 的 source-fixed 热源归一化方式，沿用 explicit by-ID domain selections 和 explicit by-ID boundary selections。没有回退到 Box selection。contact layer 未纳入 conductor Joule loss，RIP、screen、flange、terminal 也未纳入 conductor Joule loss。

## 5. 风险分区阈值说明

全局温度风险区为 safe: Tmax_global_C < 110；attention: 110 <= Tmax_global_C < 130；warning: 130 <= Tmax_global_C < 150；thermal_risk: Tmax_global_C >= 150。接触热点风险区为 contact_safe: Tmax_contact_C < 100；contact_attention: 100 <= Tmax_contact_C < 120；contact_warning: 120 <= Tmax_contact_C < 150；contact_risk: Tmax_contact_C >= 150。这些阈值只用于 solid-only 诊断阶段的风险分区和可视化，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## 6. 有效性统计

- 工况数量：125
- 求解状态：{'SOLVED_VALID': 116, 'INVALID_CASE': 9}
- risk_zone 统计：{'safe': 111, 'invalid_case': 9, 'attention': 4, 'warning': 1}
- contact_risk_zone 统计：{'contact_safe': 117, 'contact_attention': 5, 'contact_warning': 3}
- valid_heat_balance：116/125
- valid_Qjoule：125/125
- valid_Qcontact：125/125
- valid_selection：125/125
- overall_valid：116/125
- thermal_warning：1/125
- thermal_risk_case：0/125

Tmax_global_C 范围为 67.225 至 132.179 degC；Tmax_contact_C 最大值为 127.152 degC。最大 heat-balance residual_percent 绝对值为 13.622%。最大 Qjoule 相对误差绝对值为 7.224e-13%，最大 Qcontact 相对误差绝对值为 8.527e-14%。

## 7. 是否存在 invalid_case

存在 9 个 invalid_case，均由 heat_balance residual_percent 超过 10% 引起，主要集中在低负荷、高油温、低接触电阻倍率工况。具体如下：

- RUN008_CASE_011: load=0.600000, oil=85.000000 C, Rc=1.000000, failure=heat_balance, residual_percent=-10.626%
- RUN008_CASE_016: load=0.600000, oil=95.000000 C, Rc=1.000000, failure=heat_balance, residual_percent=-12.136%
- RUN008_CASE_021: load=0.600000, oil=105.000000 C, Rc=1.000000, failure=heat_balance, residual_percent=-13.622%
- RUN008_CASE_036: load=0.600000, oil=85.000000 C, Rc=2.000000, failure=heat_balance, residual_percent=-10.365%
- RUN008_CASE_041: load=0.600000, oil=95.000000 C, Rc=2.000000, failure=heat_balance, residual_percent=-11.819%
- RUN008_CASE_046: load=0.600000, oil=105.000000 C, Rc=2.000000, failure=heat_balance, residual_percent=-13.252%
- RUN008_CASE_066: load=0.600000, oil=95.000000 C, Rc=5.000000, failure=heat_balance, residual_percent=-10.994%
- RUN008_CASE_071: load=0.600000, oil=105.000000 C, Rc=5.000000, failure=heat_balance, residual_percent=-12.287%
- RUN008_CASE_096: load=0.600000, oil=105.000000 C, Rc=10.000000, failure=heat_balance, residual_percent=-11.043%

这些工况的 Qjoule 与 Qcontact 校核仍通过，selection 也未异常；当前问题更像是低总发热量条件下油侧热输入和热量收支归一化/边界通量闭合的诊断阈值问题，而不是导体或接触热源归一化错误。

## 8. 是否存在 thermal_risk_case

不存在 thermal_risk_case。最高温工况为 Tmax_global_C = 132.179 degC，属于 warning 区而非 thermal_risk 区。

## 9. 热源分解趋势

Qjoule_conductor_W 范围为 11.616 至 76.603 W，并随 I² 增长。Qcontact_W 范围为 0.562 至 61.250 W，严格满足 Icase² * Rc0 * Rc_factor。Qjoule 对 I² 的线性拟合为 Q = 23.581 * (I²/1e6) - 1.801，R² = 0.99523。

## 10. 热量收支趋势

116/125 工况满足 abs(residual_percent) < 10%。9 个 invalid_case 的 residual_percent 为 -10.364% 至 -13.622%，全部为负残差，表示热移除项大于体热源积分；这些工况同时具有低负荷、热源小和热油边界向固体输入热量的特征。

## 11. 风险边界初步结论

- oil=65 C, Rc=20: safe up to load 1.2; first attention 1.4
- oil=75 C, Rc=20: safe up to load 1.2; first attention 1.4
- oil=85 C, Rc=20: safe up to load 1.2; first attention 1.4
- oil=95 C, Rc=20: safe up to load 1.2; first attention 1.4
- oil=105 C, Rc=20: safe up to load 1.2; first warning 1.4

在当前扫描范围内没有出现 Tmax_global_C >= 150 degC 的 thermal_risk 区，但最高压力工况 load=1.4、oil=105 C、Rc=20 进入 warning 区，Tmax_global_C = 132.179 degC，Tmax_contact_C = 127.152 degC。

## 12. 代表性风险工况说明

代表性工况包括低风险工况 load=0.6、oil=65 C、Rc=1；基准工况 load=1.0、oil=85 C、Rc=1；高接触风险工况 load=1.2、oil=95 C、Rc=20；最高压力工况 load=1.4、oil=105 C、Rc=20。对应热源分解见 `fig05_heat_source_decomposition_risk_cases.png`。

## 13. 是否建议进入下一步完整电热耦合介质损耗修正

不建议直接进入 `FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009`。虽然 125 组均完成求解，Qjoule、Qcontact 和 selection 均通过，但 valid_heat_balance 不是 100%，存在 9 个 invalid_case，未满足文档给出的进入 RUN009 前置条件。

趋势检查结果：

- Tmax_global_C 随 oil_temperature_C 升高而升高：True
- Tmax_global_C 随 load_multiplier_pu 升高而升高：True
- Tmax_contact_C 随 contact_resistance_multiplier_pu 升高而升高：True
- Qjoule_conductor_W 随 I² 增长：True
- Qcontact_W 随 I² * Rc_factor 增长：True

## 14. 下一轮修正任务

建议先开展 RUN008B 热量收支闭合修正，重点检查低负荷/高油温条件下油侧对流热通量符号、法兰散热边界、外表面对流积分边界是否完整，以及 residual_percent 在低 Qtotal 工况下是否需要同时引入 residual_W 的绝对阈值作为辅助诊断。修正后重新运行 125 组有效性校核；只有 invalid_case = 0 且 valid_heat_balance = 125/125 后，再进入 RUN009。

## 必须回答的问题

1. 125组是否全部成功求解？是，COMSOL 均完成求解；但有效性状态为 116 个 SOLVED_VALID、9 个 INVALID_CASE。
2. valid_heat_balance 是否为100%？否，为 116/125。
3. valid_Qjoule 是否为100%？是，为 125/125。
4. valid_Qcontact 是否为100%？是，为 125/125。
5. 是否存在 selection 异常？否，valid_selection = 125/125。
6. thermal_risk_case 是否存在？否，为 0/125。
7. 风险边界是否具有物理趋势？主要趋势合理，趋势检查均为 True。
8. 是否可以进入 FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009？否。

Can proceed to FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009: NO

依据：存在 9 个 invalid_case，且 valid_heat_balance=116/125，未达到进入 RUN009 的前置条件。
