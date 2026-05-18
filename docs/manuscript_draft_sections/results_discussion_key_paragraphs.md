# Results and Discussion 关键段落初稿

## 1. 基准工况结果段落

在 `STEADY_1250_LOAD_1p0` 基准工况下，完整电场耦合介质损耗模型得到的 `Tmax_global_C` 为约 `88.589 degC`。导体焦耳热、接触热和 RIP 介质损耗分别由 source-fixed 导体电阻、参数化接触电阻和电场分布积分给出。与早期 solid-only 热诊断相比，RUN009A 将 approximate_Qdielectric_ref 替换为 `omega * epsilon0 * epsr * tan_delta * |E|^2`，因此能够反映 RIP 区域非均匀电场对介质损耗的贡献。该结果属于 finite element numerical simulation，不是实物实验测量。

## 2. RUN010 125组风险边界段落

RUN010 在 5 × 5 × 5 的核心工况矩阵上完成了 125 组稳态有限元计算。所有工况均满足热源归一化、热量收支、selection 完整性和电场奇异性检查，`overall_valid=125/125`。在该矩阵内，`Tmax_global_C` 的范围为 `67.397-134.974 degC`，global risk zone 统计为 `safe:119; attention:4; warning:2`。这里的 safe、attention、warning 和 thermal_risk 仅为本文内部的 diagnostic risk zoning，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## 3. RUN008 vs RUN010 对比段落

RUN008 使用 approximate_Qdielectric_ref 作为 solid-only 诊断热源，而 RUN010 使用 field-coupled Qdielectric。两者对比显示，field-coupled 介质损耗使 `Tmax_global_C` 平均增加约 `0.617 degC`，最大增加约 `2.816 degC`，并导致 `2` 个工况的 risk zone 发生变化。该差异表明平均场参考热源可以用于早期热诊断，但论文主结果应采用电场分布积分得到的介质损耗。

## 4. 热源分解段落

RUN010 的热源分解将总发热量分为导体焦耳热、接触电阻热和 RIP 介质损耗热。导体焦耳热随电流平方变化，接触热严格按照 `Icase^2 * Rc0 * Rc_factor` 计算，RIP 介质损耗由电场分布积分得到。RUN006 首先验证了热源归一化，其中基准 solid-only 模型的 `Qjoule` 为 `34.008 W`，`Qcontact` 为 `1.5625 W`。这一审计链条降低了把几何域、接触层或屏蔽层错误计入导体损耗的风险。

## 5. 接触电阻劣化影响段落

接触电阻劣化在本文中采用参数化等效模型表示，而不是实测缺陷。RUN010 和 RUN011B 结果表明，在较高负荷和较高油温下，接触电阻倍率升高会显著提高接触热点温度。RUN011B 中高风险基准下 `Rc0_multiplier=2` 的工况达到 diagnostic thermal risk，但其热量收支仍为有效，说明这是参数扰动下的物理响应，而不是数值失败。

## 6. 网格无关性段落

RUN011A 选取基准、高接触风险和最高压力三个代表工况进行 coarse、medium 和 fine 三档网格比较。以 fine 网格为参考，medium 网格在三个代表工况中均通过收敛要求，最大 `Tmax_global` 误差为 `0.355%`，最大 `E95_RIP` 误差为 `0.002%`，最大 `Qdielectric_RIP_field` 误差为 `0.002%`。因此，RUN010 使用的 medium 网格可作为当前稳态风险扫描的默认网格。

## 7. 敏感性分析段落

RUN011B 对 RIP 导热率、介质损耗因数、相对介电常数、油侧换热系数、空气侧换热系数和接触电阻基准值进行了单因素扰动分析。敏感性排序为 `tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil`。其中 tan_delta 和 epsr 主要影响介质损耗项，Rc0 和 h_air 对接触热点或整体温升具有明显影响。该结果说明后续模型验证和论文讨论应重点交代介质参数、空气侧换热和接触电阻等工程假设。

## 8. 局限性段落

本文结果基于二维轴对称有限元模型和参数化运行工况。模型没有显式描述法兰螺栓孔、端子三维局部结构、真实污染非均匀分布和全年气象暂态过程。risk zone 阈值仅用于诊断分区，不应解释为标准限值。`dielectric_loss_review_required=true` 也不表示模型失败，而是提示 field-coupled Qdielectric 与平均场参考之间存在需要解释的差异；RUN010 中 field_singularity_flag 为 `0/125`，说明该差异不是由已标记的屏端奇异点直接支配。后续应结合材料参数复核、现场监测或公开实测数据进一步约束模型不确定性。
