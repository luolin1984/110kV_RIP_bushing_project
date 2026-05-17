# FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009 报告

## 本轮任务目标
RUN009 的目标是把 solid-only 热诊断模型中的 `approximate_Qdielectric_ref` 替换为由静电场求解得到的空间分布介质损耗项，并先通过 RUN009A 基准工况与 RUN009B 27 组小规模工况复核稳定性。本轮不是 SCI 最终结果，不包含全年气象驱动、暂态仿真或 125 组完整风险边界扫描。

## 与 RUN006/RUN007/RUN008/RUN008B 的关系
RUN009 沿用 RUN006 的导体焦耳热与接触热源归一化，沿用 RUN007/RUN008/RUN008B 的 explicit by-ID domain/boundary selections，并保留 RUN008B 的热量收支闭合复核逻辑。

## 为什么切换到 field-coupled Qdielectric
`approximate_Qdielectric_ref` 只用平均径向场强估算 RIP 介质损耗，适合热源量级诊断，但不能反映电容屏结构带来的空间分布差异。RUN009 使用 `omega0 * eps0_solid_const * epsr_rip * tan_delta_rip * es.normE^2` 作为 RIP 域体热源。

## RUN009A 基准结果
- status: SOLVED_VALID
- Tmax_global_C: 88.5885
- Qjoule_conductor_W: 34.4334
- Qcontact_W: 1.5625
- Qdielectric_RIP_field_W: 28.0485
- Qdielectric_RIP_ref_W: 2.54519
- Qdielectric_ratio_field_to_ref: 11.0202

## 电场边界与浮置屏实现说明
S00 设为 72.75 kV RMS，S10 与法兰接地，S01-S09 采用 Floating Potential with zero net charge。屏边界、热边界和材料域均来自显式 COMSOL boundary/domain ID selection，没有回退到 Box selection。

## Emax 与屏端奇异性检查
- Emax_global_V_per_m: 4.56345e+07
- Emax_RIP_V_per_m: 4.56345e+07
- Emax_RIP_probe_excluding_edges_V_per_m: 4.56345e+07
- E95_RIP_V_per_m: 1.31064e+07
- field_singularity_flag: false
- screen_end_hotspot_flag: false

## Qdielectric_ref 与 Qdielectric_field 对比
RUN009A 的 field/ref = 11.0202，略高于 0.1-10 建议复核区间上限，因此所有 RUN009A/B 结果均保留 `DIELECTRIC_LOSS_REVIEW_REQUIRED` 标记。由于 Qdielectric_field 为正且量级未异常巨大，且 field_singularity_flag=false，本轮未将其判为模型失败。

## 热源分解
RUN009A Qtotal = 64.0444 W，其中 Qjoule = 34.4334 W，Qcontact = 1.5625 W，Qdielectric_field = 28.0485 W。RUN009B 中 Qjoule/Qcontact 校验误差最大值分别为 7.628e-13% 和 8.527e-14%。

## 热量收支
RUN009A heat_balance_residual_percent = -1.9022%。RUN009B 27 组最大 |residual_percent_Qgenerated| = 2.3830%，全部为 VALID_STRICT。

## RUN009A 是否通过
RUN009A 通过状态: YES。

## RUN009B 27组有效性统计
- solved/valid cases: 27/27
- Tmax_global_C range: 77.9853 - 107.9617
- heat_balance_valid: 27/27
- field_singularity_flag=false: 27/27

## 趋势检查
- Tmax_increases_with_oil_temperature: PASS
- Tmax_increases_with_load: PASS
- Tmax_contact_responds_to_Rc: PASS
- Qjoule_increases_with_I2: PASS
- Qcontact_increases_with_I2_Rc: PASS

## 是否可以进入 RUN010
RUN009B 全部成功、热量收支和热源归一化全部通过，趋势检查物理合理。因此可以建议进入 `FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010`。该建议只表示可以启动下一阶段 125 组完整电场耦合介质损耗风险边界扫描，不代表 RUN009 是 SCI 最终结论。

Can proceed to FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010: YES
