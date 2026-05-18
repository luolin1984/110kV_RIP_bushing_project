# MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012 报告

## 本轮任务目标

本轮目标是汇总 RUN006-RUN011 的审计链条，建立论文实验部分可追溯的模型验证材料，整理主图、补充图和关键表格，并生成仿真实验部分的初稿框架。本轮未运行新的 COMSOL 大规模扫描，未做全年气象驱动，未做暂态仿真，也未覆盖 RUN010/RUN011 原始 CSV。

## 输入文件状态

- required inputs: 35
- missing inputs: 0

所有任务说明15列出的必需输入文件均已找到。

## RUN006-RUN011 证据链

RUN006 修复了 solid-only 基准热模型的热源归一化，基准工况 `Tmax_global_C=88.419 degC`，`Qjoule=34.008 W`，`Qcontact=1.5625 W`，热量收支残差 `-3.254%`。RUN007 完成 27 组小规模 solid-only 扫参，`27/27` 有效。RUN008B 对 RUN008 的热量收支进行复核，`125/125` 重新分类为有效。RUN009A/RUN009B 将 approximate_Qdielectric_ref 替换为 field-coupled Qdielectric，并完成基准与 27 组验证。RUN010 完成 125 组完整电场耦合介质损耗风险扫描，`125/125` 有效。RUN011A/RUN011B 完成网格无关性和材料/边界敏感性验证。

## 可作为论文主结果的内容

- RUN009A 基准场分布：电位、电场、介质损耗密度和温度场。
- RUN010 125 组完整 field-coupled Qdielectric 风险扫描。
- RUN010 与 RUN008 的温度差异对比，用于说明 field-coupled Qdielectric 相对 approximate reference 的影响。
- RUN011A medium-vs-fine 网格无关性结论。
- RUN011B 材料与边界敏感性排序。

## 只能作为诊断或补充材料的内容

- RUN001/RUN002 的异常温升历史记录。
- RUN003 物理特征关闭诊断。
- RUN006/RUN007/RUN008 solid-only 结果。它们用于审计和模型搭建，不应写成最终完整电热耦合主结果。
- RUN008B 热量收支复核，用于解释判据而不是作为主风险结论。

## RUN010 主结果概述

RUN010 的 `Tmax_global_C` 范围为 `67.397-134.974 degC`，`Tmax_contact_C` 最大值为 `129.925 degC`。global risk_zone 统计为 `safe:119; attention:4; warning:2`；contact_risk_zone 统计为 `contact_safe:115; contact_attention:6; contact_warning:4`。热量收支最大绝对归一化残差为 `2.678%`。这些 risk_zone 阈值仅为研究内部诊断分区，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## RUN011 网格无关性结论

RUN011A 中 3 个代表工况的 medium-vs-fine 均通过。最大 `Tmax_global` 误差为 `0.355%`，最大 `E95_RIP` 误差为 `0.002%`，最大 `Qdielectric_RIP_field` 误差为 `0.002%`。因此 RUN010 使用的 medium 网格可作为当前稳态风险扫描的默认网格。

## RUN011 敏感性结论

RUN011B 完成 `38` 个材料/边界敏感性工况，热量收支有效 `38/38`，field_singularity_flag true 为 `0`。敏感性排序为：`tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil`。其中高风险基准下低空气换热或接触电阻基准倍增可触发 diagnostic thermal risk，这反映参数化工况响应，不是数值失败。

## dielectric_loss_review_required 的论文解释

`dielectric_loss_review_required=true` 不代表模型失败。该标记来自 `Qdielectric_field/ref` 大于最初设定的 `[0.1, 10]` 复核区间，RUN010 平均比值约为 `11.020`。同时 RUN010 的 field_singularity_flag 为 `0/125`，说明该差异不是由被标记的屏端奇异场直接支配。论文中应解释为：真实电场分布下的介质损耗积分高于平均场参考估计，需保留复核标记并在材料参数/电容屏边缘场处理部分讨论。

## 论文主图建议

主文建议使用 Fig1-Fig9：模型流程与几何、基准场分布、RUN010 全局温度热力图、接触温度热力图、安全负荷边界、热源分解、RUN008 vs RUN010 温度差异、网格无关性、敏感性排序。

## 论文主表建议

建议主文使用 Table1 阶段审计汇总、Table2 关键结果汇总和 Table3 模型验证证据链。详细风险边界、网格误差和敏感性指数可作为补充表。

## 是否可以进入实验部分撰写阶段

RUN012 已生成主图/补充图索引、主表/补充表索引、模型验证证据链、实验部分框架和结果讨论关键段落；没有误称实物实验验证，没有把诊断阈值写成标准限值，也没有删除历史结果。

Can proceed to MANUSCRIPT_EXPERIMENT_SECTION_DRAFT_RUN013: YES
