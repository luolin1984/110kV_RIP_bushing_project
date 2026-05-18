# 4. 结果与讨论（中文说明稿）

## 4.1 基准电热场分布

RUN009A 基准工况 STEADY_1250_LOAD_1p0 的求解状态为 SOLVED_VALID，Tmax_global_C = 88.589 degC。导体、RIP、接触层、硅橡胶和法兰的最高温度分别为 74.136、88.589、58.790、57.215 和 46.906 degC，说明后处理 selection 没有把所有区域混成同一个最大值。

RUN009A 的导体焦耳热、接触热和 RIP 电场耦合介质损耗分别为 34.433 W、1.5625 W 和 28.049 W，热量收支残差为 -1.902%。field/ref 介质损耗比为 11.020，因此保留 dielectric_loss_review_required 标记。

## 4.2 负荷、油温和接触电阻影响

RUN010 共完成 125 组完整电场耦合稳态计算，125/125 组通过 overall_valid。Tmax_global_C 范围为 67.397-134.974 degC，Tmax_contact_C 最大为 129.925 degC。油温升高会整体抬升温度场，负荷升高会使导体和接触热随 I^2 增大，接触电阻倍率升高主要增强接触热点响应。

## 4.3 风险边界

RUN010 中 global risk zone 统计为 safe 119 组、attention 4 组、warning 2 组、thermal_risk 0 组。接触热点分区为 contact_safe 115 组、contact_attention 6 组、contact_warning 4 组、contact_risk 0 组。这些分区只是本文内部诊断阈值，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## 4.4 电场耦合介质损耗贡献

RUN008 使用 approximate_Qdielectric_ref，RUN010 使用电场积分介质损耗。两者比较显示，RUN010 相对 RUN008 的 Tmax_global_C 平均增加 0.617 degC，最大增加 2.816 degC，并导致 2 个工况风险分区变化。该结果说明早期平均场热源可以用于诊断，但论文主结果应以 field-coupled Qdielectric 为准。

## 4.5 热源分解与接触退化

RUN010 将热源分为导体焦耳热、接触热和 RIP 介质损耗。导体热满足 I^2R 趋势，接触热满足 I^2R_c。接触电阻退化在本文中是参数化等效模型，不是实测缺陷；它主要影响接触层热点温度，在高负荷和高油温下更明显。

## 4.6 网格无关性与敏感性

RUN011A 中 medium 相对 fine 网格在代表工况中全部通过，Tmax_global、E95_RIP 和 Qdielectric 的最大误差分别为 0.355%、0.002% 和 0.002%。RUN011B 的敏感性排序为 tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil，说明介损因数、相对介电常数、接触电阻和空气侧换热是后续需要重点说明的不确定性来源。

## 4.7 工程意义与局限性

结果表明，高油温、高负荷和接触劣化会共同降低套管热裕度。模型仍存在二维轴对称近似、未解析流场、未显式表达三维端子/螺栓结构、未做全年气象暂态以及缺少实测验证等限制。因此 RUN010 是可审计的数值风险边界扫描，而不是 SCI 最终结论。
