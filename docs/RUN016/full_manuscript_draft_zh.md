# 题目候选

1. Electro-Thermal Coupled Finite-Element Diagnostic Risk-Boundary Simulation of a 126 kV/1250 A RIP Condenser Transformer Bushing under Contact-Resistance Degradation
2. Numerical Screening of Contact-Resistance Degradation in a 126 kV/1250 A RIP Condenser Transformer Bushing Using Field-Coupled Electro-Thermal Finite-Element Simulation
3. Field-Coupled Dielectric-Loss and Contact-Degradation Effects in a 126 kV/1250 A RIP Condenser Transformer Bushing: A Finite-Element Diagnostic Risk-Boundary Study

# 摘要（中文内部阅读版）

本文针对 126 kV/1250 A RIP 电容型变压器套管，建立分阶段电热耦合有限元数值筛查模型。模型包括导体焦耳热、接触电阻热、电场耦合 RIP 介质损耗、显式 by-ID selection、热量收支、电场奇异性、网格无关性和参数敏感性审计。RUN010 主矩阵共 125 组稳态工况，Tmax_global_C 范围为 67.397-134.974 degC，Tmax_contact_C 最大为 129.925 degC。全局诊断风险分区为 safe 119、attention 4、warning 2、thermal-risk 0；接触区分区为 contact_safe 115、contact_attention 6、contact_warning 4、contact-risk 0。medium-vs-fine 最大 Tmax 误差为 0.355%，敏感性排序为 tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil。本文结果是有限元数值筛查，不是实验或现场验证；诊断风险分区不是标准限值。

# 关键词

RIP condenser bushing; transformer bushing; electro-thermal coupling; finite-element simulation; contact-resistance degradation; field-coupled dielectric loss; diagnostic risk boundary; mesh convergence

# 1. 引言（中文内部阅读版）

高压变压器套管承担带电导体与接地变压器箱体之间的电气和机械过渡。对于 126 kV/1250 A RIP 电容型变压器套管，热裕度受到载流路径、RIP 电容芯体电场、油侧热环境和空气侧冷却条件共同影响。BRFGL1-126/1250-4 的几何和额定信息需要由图纸或样本占位引用 [REF_BRFG_DRAWING] 支撑，套管标准背景需要由 IEC 60137 占位引用 [REF_IEC_60137] 支撑。

RIP 电容型套管通过电容屏改善电场分布，但这也使热问题具有多源特征：导体焦耳热、接触电阻热、RIP 介质损耗、油温、空气侧换热和材料参数都会影响温度场。因此，本项目采用有限元数值筛查方法，而不是把温升看成单一负荷修正问题。相关 RIP 套管热分析、电热耦合和电容屏电场文献需要用于支撑这一背景 [REF_RIP_BUSHING_THERMAL; REF_CONDENSER_BUSHING_ELECTROSTATICS]。

本文特别强调两个建模边界。第一，接触电阻倍率是参数化等效模型，不是实测缺陷。第二，在已经求解电场的情况下，RIP 介质损耗不应只使用平均场参考，而应使用 q_dielectric = omega epsilon0 epsr tan(delta)|E|^2 的电场耦合热源形式 [REF_DIELECTRIC_LOSS_THEORY]。同时，DIELECTRIC_LOSS_REVIEW_REQUIRED 标记必须保留，用于提示 field/ref 比值偏高这一不确定性。

本研究建立的是分阶段有限元数值筛查流程，不声称实物实验验证、现场监测验证或标准运行限值。RUN006 修正热源归一化，RUN007-RUN008 做 solid-only 诊断，RUN009 引入电场耦合介质损耗，RUN010 完成 125 组主矩阵，RUN011 完成网格和参数稳健性检查。文中的 diagnostic risk zoning 只是内部筛查分类，不是 IEC/IEEE 温升限值、材料寿命阈值或运行规程 [REF_RISK_DIAGNOSTIC_METHOD]。

本文贡献在于：建立 CAD 约束、显式 selection 的二维轴对称 RIP 套管有限元模型；用电场耦合介质损耗替代平均场参考，并保留介质损耗复核标记；量化负荷、油温和接触电阻倍率对全局温度与接触热点的影响；把正文数值结论锁定到 raw result、图表和引用占位符，便于后续投稿加工。

# 2. 文献综述（中文内部阅读版）

## 2.1 变压器套管热分析与电热耦合建模

已有研究使用热网络、二维有限元和三维电磁-流体-热耦合方法分析套管温度场。这些研究说明负荷、油温、环境冷却和热点位置需要作为耦合因素处理，而不是单独修正。对于本文模型，相关文献支撑有限元数值筛查的必要性，同时也提示二维轴对称模型不能完全替代三维流场和端子局部结构分析 [REF_RIP_BUSHING_THERMAL]。

## 2.2 接触电阻劣化与局部过热

载流连接结构的等效接触电阻升高会形成局部热源。相关接触劣化和连接缺陷研究可以支撑 contact-resistance multiplier 的设置，但不能让本文声称复现了某个实测缺陷。因此，本文将接触退化表述为参数化等效模型 [REF_RISK_DIAGNOSTIC_METHOD]。

## 2.3 RIP 介电响应与电场耦合介质损耗

RIP 的介电响应与相对介电常数、介损因数、温度、频率和老化状态有关。电场分布会影响介质损耗空间分布，因此本文使用电场耦合介质损耗，并同时报告 field/ref 比值。由于该比值超过初始复核区间，dielectric_loss_review_required 被保留为透明不确定性标记，而不是模型失败标志 [REF_DIELECTRIC_LOSS_THEORY]。

## 2.4 电容屏与电场建模

电容型套管通过多层电容屏均化电场。建模时，高压屏和接地屏可设定固定电位，中间屏若按浮置屏处理，不应被任意固定电位约束。本文将 S00 设为高压，S10 与法兰接地，S01-S09 作为浮置屏处理。该部分需要电容套管电场文献和 COMSOL floating potential 官方文档支撑 [REF_CONDENSER_BUSHING_ELECTROSTATICS; REF_COMSOL_FLOATING_POTENTIAL]。

## 2.5 数值验证、网格收敛与诊断风险分区

数值风险边界研究不能只依赖一张温度云图，还需要热源归一化、热量收支、selection 完整性、电场奇异性、网格收敛和敏感性分析。RUN011A 和 RUN011B 分别提供网格和参数稳健性证据，但外部网格收敛和诊断分区方法文献仍需人工确认 [REF_MESH_CONVERGENCE; REF_RISK_DIAGNOSTIC_METHOD]。

## 2.6 本文拟解决的问题

已有研究为热分析、电热耦合、介电响应和接触缺陷诊断提供基础。本文进一步面向 126 kV/1250 A RIP 电容型变压器套管，构建可审计、热源归一化、电场耦合介质损耗的有限元数值筛查流程，并把每个关键结论锁定到数据证据和图表。这一结构服务于论文主稿组装，但不把仿真结果夸大为实验验证或运行规程。

# Methods + Results 整合说明稿（RUN014）

## 3. 数值模型与仿真设置

### 3.1 几何与套管结构

模型对象为 BRFGL1-126/1250-4 型 126 kV/1250 A RIP 干式电容型变压器套管。模型采用二维轴对称有限元 r-z 坐标，空气侧为 z 正方向，油侧为 z 负方向，法兰作为接地和结构参考。几何尺寸和额定参数需要由厂家图纸或样本占位引用 [REF_BRFG_DRAWING] 支撑，套管类别和额定等级背景需要由 IEC 60137 占位引用 [REF_IEC_60137] 支撑。

模型区分中心导体、端子连接区、接触电阻热源层、RIP 电容芯体、电容屏、硅橡胶外绝缘、接地法兰和油侧屏蔽或锥形过渡区。空气侧外形使用 CAD 轮廓约束，不再使用单一直筒近似。整体建模流程、几何抽象和审计链见 Fig. 1。

二维轴对称模型没有显式描述法兰螺栓孔和端子局部三维结构，这属于模型局限性，不代表这些结构在物理上不重要。

### 3.2 材料参数与边界条件

所有固体求解域均赋予材料，包括铜导体、RIP 芯体、铝电容屏、硅橡胶外绝缘、法兰金属、端子和接触热源层。材料和换热参数来自公开资料、图纸信息和工程假设，需要后续由材料和 RIP 套管热分析文献支撑 [REF_RIP_BUSHING_THERMAL]。

空气和变压器油不作为体流体域建模，而是作为外表面对流边界条件进入模型。空气侧边界覆盖外绝缘和端子外表面，油侧边界覆盖油浸固体表面。内部材料界面、轴对称边界和法兰内部接触界面不作为对流边界。正式材料、热源、换热和后处理 selection 均使用 explicit by-ID 方式。阶段审计见 Table 1，关键数值索引见 Table 2。

### 3.3 电热耦合公式

稳态电热模型包括导体焦耳热、接触电阻热和 RIP 介质损耗。导体热源按 I2R 归一化，接触热按 Q_contact = I_case^2 R_c0 R_c_factor 计算。基准接触倍率为 1 时，接触热积分为 1.5625 W。接触退化在本文中是参数化等效模型，不是实测缺陷。

RIP 介质损耗由电场解计算：q_dielectric = omega epsilon_0 epsilon_r tan(delta) |E|^2，需要由介质损耗理论引用支撑 [REF_DIELECTRIC_LOSS_THEORY]。S00 设为相对地 RMS 电压，S10 和法兰接地，S01-S09 作为浮置电容屏处理，对应引用占位符为 [REF_CONDENSER_BUSHING_ELECTROSTATICS] 和 [REF_COMSOL_FLOATING_POTENTIAL]。

### 3.4 工况矩阵

RUN010 是主风险扫描，共 125 组稳态工况。变量为负荷倍率、油温和接触电阻倍率；电压倍率、空气温度、风速、介损倍率、RIP 老化倍率和污秽倍率固定。RUN006 修正热源归一化，RUN007/RUN008 用于 solid-only 诊断，RUN009 引入电场耦合介质损耗，RUN010 扩展到 125 组主矩阵，RUN011 进行网格无关性和参数敏感性验证。验证证据链见 Table 3。

### 3.5 数值验证策略

验证内容包括热源归一化、热量收支、selection 完整性、电场奇异性检查、网格收敛和参数敏感性。RUN010 中 125/125 组整体有效，field_singularity_flag 为 0/125。dielectric_loss_review_required 在 125/125 组中保留，因为电场积分介质损耗高于早期平均场参考；这不是模型失败，而是需要在论文中透明说明的不确定性标记。

RUN011A 表明 medium 网格相对 fine 网格在代表工况中通过，Tmax_global、E95_RIP 和 Qdielectric 的最大误差分别为 0.355%、0.002% 和 0.002%。网格收敛判据需要文献占位引用 [REF_MESH_CONVERGENCE]。RUN011B 的敏感性排序为 tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil。网格和敏感性结果见 Table 5 和 Table 6。

## 4. 结果与讨论

### 4.1 基准电热场分布

RUN009A 基准工况为 STEADY_1250_LOAD_1p0，求解状态有效。Tmax_global 为 88.589 degC，导体、RIP、接触层、硅橡胶和法兰最高温度分别为 74.136、88.589、58.790、57.215 和 46.906 degC。各区域最高温度并不相同，说明 selection 保持了物理区分。基准电位、电场、介质损耗和温度指标见 Fig. 2。

基准热源分解为导体焦耳热 34.433 W、接触热 1.5625 W 和 RIP 电场耦合介质损耗 28.049 W，热量收支残差为 -1.902%。field/ref 比值为 11.020，因此保留 DIELECTRIC_LOSS_REVIEW_REQUIRED 标记。

### 4.2 负荷、油温和接触电阻影响

RUN010 完成 125 组完整电场耦合稳态工况。Tmax_global 范围为 67.397 至 134.974 degC，Tmax_contact 最大为 129.925 degC。全局温度响应见 Fig. 3，接触区响应见 Fig. 4。油温升高会抬升整体温度，负荷升高使导体热和接触热按电流平方增大，接触电阻倍率升高主要增强接触层热点。代表工况热源分解见 Fig. 6。

### 4.3 诊断风险边界

RUN010 的全局诊断风险分区为 safe 119 组、attention 4 组、warning 2 组、thermal-risk 0 组。接触区分区为 contact-safe 115 组、contact-attention 6 组、contact-warning 4 组、contact-risk 0 组。安全负荷边界随油温和接触电阻倍率升高而降低，见 Fig. 5 和 Table 4。风险分区只是内部诊断可视化类别，不是 IEC/IEEE 标准限值、材料寿命阈值或保证运行限值，需要由诊断分区方法引用支撑 [REF_RISK_DIAGNOSTIC_METHOD]。

### 4.4 电场耦合介质损耗贡献

RUN008 使用平均场参考介质损耗，RUN010 使用电场解积分介质损耗。替换后 Tmax_global 平均增加 0.617 degC，最大增加 2.816 degC，125 组中有 2 组风险分区变化，见 Fig. 7。该比较说明平均场参考适合早期诊断，但主矩阵应采用 field-coupled dielectric loss。

### 4.5 热源分解与接触退化

RUN010 的热源分解表明导体热满足 I2 趋势，接触热满足 I2Rc。补充图 S2 和 S3 分别给出 Qcontact 和 Qjoule 验证。接触退化通过接触电阻倍率表示，是参数化等效模型，不是实测缺陷。

### 4.6 网格无关性与参数敏感性

RUN011A 支撑 RUN010 使用 medium 网格，结果见 Fig. 8 和 Table 5。RUN011B 给出的敏感性排序为 tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil，见 Fig. 9 和 Table 6。介损因数和相对介电常数直接控制介质损耗，接触电阻和空气侧换热影响局部热点和散热路径。

### 4.7 工程意义与局限性

结果表明，油温、负荷电流、接触电阻退化和介质参数共同决定 126 kV/1250 A RIP 电容型套管的热裕度。模型仍有二维轴对称近似、未解析流体域、未显式三维端子/螺栓结构、未考虑非均匀污秽和暂态过载、未用现场监测或实验数据验证等限制。RUN010 应被视为可审计的有限元数值风险边界扫描，而不是最终运行规则。

## 补充图路由说明

Fig. S1 记录运行审计流程，Fig. S2 验证 Qcontact 与 I2Rc，Fig. S3 验证 Qjoule 与 I2，Fig. S4 给出热量收支残差，Fig. S5 给出电场诊断，Fig. S6 说明 field/ref 介质损耗比，Fig. S7 展示各参数敏感性细节。

# 5. 局限性与未来工作

本稿仍受二维轴对称近似、无 CFD 流体域、无暂态过载/全年气象历程、无三维端子/法兰螺栓局部解析、无现场或实验验证等限制。diagnostic risk zoning 只作为内部筛查分区，不是标准限值或运行规程。contact-resistance multiplier 是参数化等效模型，不是实测缺陷。DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required 必须保留，说明电场耦合介质损耗高于平均场参考这一复核项。

# 6. 结论

1. 本文形成了面向 126 kV/1250 A RIP 电容型套管的可审计有限元数值筛查流程。
2. RUN009A 基准温度为 88.589 degC，RIP 电场耦合介质损耗为 28.049 W，field/ref 比值为 11.020。
3. RUN010 125 组工况中 Tmax_global_C 为 67.397-134.974 degC，Tmax_contact_C 最大为 129.925 degC。
4. 全局风险分区为 safe 119、attention 4、warning 2、thermal-risk 0；接触区分区为 contact_safe 115、contact_attention 6、contact_warning 4、contact-risk 0。
5. RUN008 与 RUN010 对比得到 0.617 degC mean delta_Tmax、2.816 degC max delta_Tmax 和 2/125 changed risk zones。
6. RUN011A 网格误差为 0.355% max Tmax、0.002% max E95 和 0.002% max Qdielectric。
7. RUN011B 敏感性排序为 tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil。

# References Placeholder List（中文说明）

本稿只列出引用占位符及 RUN015 状态，不生成正式参考文献条目。

- [REF_BRFG_DRAWING]: LOCAL_FILE_FOUND_NEEDS_MANUFACTURER_METADATA_CONFIRMATION，需处理：Use only after confirming drawing provenance and permissions; do not infer manufacturer name if not in file metadata.
- [REF_IEC_60137]: TRACEABILITY_RECORD_EXISTS_NEEDS_STANDARD_TEXT_CONFIRMATION，需处理：Do not quote clauses or limits until the official standard text is checked.
- [REF_RIP_BUSHING_THERMAL]: LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION，需处理：Filenames support relevance only; final bibliography must verify journal, DOI, and exact claims.
- [REF_DIELECTRIC_LOSS_THEORY]: PARTIALLY_RESOLVED_WITH_LOCAL_PDFS_NEEDS_THEORY_REFERENCE_CONFIRMATION，需处理：Local papers may support material response; equation should be checked against a theory source and RMS convention.
- [REF_CONDENSER_BUSHING_ELECTROSTATICS]: LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION，需处理：Need verify that selected paper actually discusses screen/electrostatic implementation.
- [REF_COMSOL_FLOATING_POTENTIAL]: UNRESOLVED，需处理：Requires manual or later online lookup of official COMSOL Electrostatics documentation.
- [REF_MESH_CONVERGENCE]: UNRESOLVED，需处理：Internal data prove convergence for this model; external source is still needed for manuscript framing.
- [REF_RISK_DIAGNOSTIC_METHOD]: PARTIALLY_RESOLVED_WITH_LOCAL_APPLICATION_PDFS_NEEDS_METHOD_REFERENCE，需处理：Use for engineering motivation only unless the candidate explicitly supports risk-zoning methodology.

# Figure Captions / Table Captions / Supplementary Material Note

图题、表题和补充材料说明沿用英文主稿中的 Fig. 1-Fig. 9、Table 1-Table 6 和 Fig. S1-Fig. S7 路由，不新增不存在的图表。
