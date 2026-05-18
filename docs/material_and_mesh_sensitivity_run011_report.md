# MATERIAL_AND_MESH_SENSITIVITY_RUN011 报告
## 本轮任务目标
本轮用于验证 RUN010 完整电场耦合介质损耗风险扫描的数值可靠性与参数稳健性，包含 RUN011A 网格无关性和 RUN011B 材料/边界单因素敏感性。RUN011 不是 SCI 最终结论，不包含全年气象、暂态仿真或新的 125 组风险边界扫描。
## 与 RUN006-RUN010 的关系
RUN011 继承 RUN006-RUN010 已验证的 source-fixed 导体/接触热归一化、explicit by-ID domain/boundary selection，以及 RUN009/RUN010 的 field-coupled dielectric loss: Qdielectric = omega * epsilon0 * epsr * tan_delta * |E|^2。
## RUN011A 网格无关性设置
- representative cases: CASE_A_BASELINE, CASE_B_HIGH_CONTACT, CASE_C_HIGHEST_PRESSURE
- mesh levels: coarse(autoMeshSize=9), medium(autoMeshSize=8, RUN010 default), fine(autoMeshSize=6)
- acceptance basis: medium-vs-fine errors for Tmax_global/Tmax_RIP/Tmax_contact < 1%, E95 < 3%, Qdielectric < 5%, heat balance valid, field_singularity_flag=false
## RUN011A 结果统计
- mesh solve rows: 9
- medium-vs-fine pass: 3/3
- CASE_A_BASELINE: Tmax_global_err=0.355%, Tmax_RIP_err=0.355%, Tmax_contact_err=0.163%, E95_err=0.00155%, Qdielectric_err=0.00178%, status=PASS_MEDIUM_VS_FINE
- CASE_B_HIGH_CONTACT: Tmax_global_err=0.0793%, Tmax_RIP_err=0.0767%, Tmax_contact_err=0.0838%, E95_err=0.00155%, Qdielectric_err=0.00178%, status=PASS_MEDIUM_VS_FINE
- CASE_C_HIGHEST_PRESSURE: Tmax_global_err=0.0665%, Tmax_RIP_err=0.0631%, Tmax_contact_err=0.0713%, E95_err=0.00155%, Qdielectric_err=0.00178%, status=PASS_MEDIUM_VS_FINE
## RUN011B 材料/边界敏感性设置
- base cases: SENS_BASELINE(load=1.0, oil=85, Rc=1), SENS_HIGH_RISK(load=1.4, oil=105, Rc=20)
- one-factor-at-a-time parameters: k_RIP_multiplier, tan_delta_multiplier, epsr_RIP, h_oil, h_air, Rc0_multiplier
## RUN011B 结果统计
- sensitivity solve rows: 38
- heat_balance valid: 38/38
- field_singularity_flag true: 0/38
- status counts: {'SOLVED_THERMAL_RISK': 3, 'SOLVED_THERMAL_WARNING': 15, 'SOLVED_VALID': 20}
- dielectric_loss_review_required true: 38/38
DIELECTRIC_LOSS_REVIEW_REQUIRED 标记被保留，用于提示 field/ref 介质损耗比值仍需在论文阶段解释；该标记本身不等价于模型失败，除非伴随电场奇异、热平衡失效或温度不合理。
## 敏感性排序
- tan_delta_multiplier: ranking_score=1, max_abs_S_Tmax_global=0.02505, max_abs_S_Tmax_contact=0.05385, max_abs_S_Qdielectric=1
- epsr_RIP: ranking_score=1, max_abs_S_Tmax_global=0.02505, max_abs_S_Tmax_contact=0.05385, max_abs_S_Qdielectric=1
- Rc0_multiplier: ranking_score=0.4045, max_abs_S_Tmax_global=0.3947, max_abs_S_Tmax_contact=0.4045, max_abs_S_Qdielectric=0
- h_air: ranking_score=0.28, max_abs_S_Tmax_global=0.2734, max_abs_S_Tmax_contact=0.28, max_abs_S_Qdielectric=0
- k_RIP_multiplier: ranking_score=0.2368, max_abs_S_Tmax_global=0.2311, max_abs_S_Tmax_contact=0.2368, max_abs_S_Qdielectric=0
- h_oil: ranking_score=0.05553, max_abs_S_Tmax_global=0.05553, max_abs_S_Tmax_contact=0.0225, max_abs_S_Qdielectric=0
## 是否存在无效工况
RUN011A/RUN011B 未发现阻断性无效工况。若存在 thermal warning，应作为物理风险现象与数值失败区分。
## 下一步建议
RUN011 支持进入模型验证与论文图件整理阶段。下一阶段仍应保持 RUN010/RUN011 的审计轨迹，并在正式论文中说明诊断阈值不是 IEC/IEEE 标准限值或材料寿命阈值。

Can proceed to MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012: YES
