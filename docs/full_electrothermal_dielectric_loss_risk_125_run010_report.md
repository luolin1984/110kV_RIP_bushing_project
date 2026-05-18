# FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010 报告

## 本轮任务目标
RUN010 在 RUN008 相同 125 组核心矩阵上使用完整电场耦合介质损耗项，检查更宽工况下热源、热量收支、电场诊断和风险边界是否稳定。本轮仍不是 SCI 最终结论。

## 与 RUN006-RUN009 的关系
RUN010 沿用 RUN006 的 source-fixed 导体/接触热源归一化，沿用 RUN007/RUN008B 的 explicit by-ID domain/boundary selections，并在 RUN009A/B 已通过的完整电场耦合介质损耗模型上扩展到 125 组。

## RUN010 与 RUN008 的区别
RUN008 使用 solid-only thermal diagnostic model，并以 `approximate_Qdielectric_ref` 作为 RIP 介质损耗热源。RUN010 使用 `omega0 * eps0_solid_const * epsr_rip * tan_delta_rip * es.normE^2`，由静电场分布直接给出 RIP 介质损耗。

## 125组有效性统计
- total cases: 125
- overall_valid: 125/125
- valid_heat_balance: 125/125
- valid_Qjoule: 125/125
- valid_Qcontact: 125/125
- valid_Qdielectric: 125/125
- valid_selection: 125/125

## field_singularity_flag 统计
- field_singularity_flag=true: 0/125
- field_singularity_flag=false: 125/125

## dielectric_loss_review_required 统计
- dielectric_loss_review_required=true: 125/125
该标记来自 Qdielectric_field/ref 超出 [0.1,10]，保留为复核标记，不等于模型失败。

## 热源分解趋势
- Qjoule relative error max: 7.759e-13%
- Qcontact relative error max: 8.527e-14%
- Qdielectric_field range: 28.0485 - 28.0485 W

## 热量收支趋势
- max |residual_percent_Qgenerated|: 2.6777%
- heat_balance_status counts: {'VALID_STRICT': 125}

## 风险分区结果
- global risk_zone counts: {'safe': 119, 'attention': 4, 'warning': 2}
- contact_risk_zone counts: {'contact_safe': 115, 'contact_attention': 6, 'contact_warning': 4}
这些阈值仅用于诊断阶段的风险分区和可视化，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## RUN008 vs RUN010 风险边界差异
- risk_zone_changed cases: 2/125
- delta_Tmax_global_C range: 0.1353 - 2.8163
- mean delta_Tmax_global_C: 0.6174

## thermal_risk_case 与 invalid_case
- thermal_risk_case: 0/125
- invalid_case: 0/125

## 趋势检查
- Tmax_global_increases_with_oil_temperature: PASS
- Tmax_global_increases_with_load: PASS
- Tmax_contact_increases_with_Rc_factor: PASS
- Qjoule_increases_with_I2: PASS
- Qcontact_increases_with_I2Rc: PASS

## 是否建议进入下一阶段
只有当 125 组全部有效、热源归一化、电场奇异性、热量收支和趋势检查全部通过时，才建议进入材料参数敏感性或网格无关性验证。

Can proceed to MATERIAL_AND_MESH_SENSITIVITY_RUN011: YES
