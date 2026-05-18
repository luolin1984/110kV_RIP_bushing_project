# 仿真实验部分草稿框架

## 3. Numerical Model and Simulation Setup

### 3.1 Geometry and bushing structure

说明 BRFGL1-126/1250-4 RIP 干式电容型变压器套管的二维轴对称建模方式。重点写明 r-z 坐标、空气侧与油侧方向、法兰位置、外绝缘 CAD 轮廓驱动、油侧过渡段、电容屏和接触热源层。说明螺栓孔和端子局部三维细节没有显式建模，属于二维轴对称近似边界。

### 3.2 Material parameters and boundary conditions

概述铜导体、RIP 芯体、铝电容屏、硅橡胶外绝缘、法兰金属和接触层材料参数。说明空气侧、油侧和法兰换热边界采用 explicit by-ID boundary selections；空气和油作为外表面对流边界条件出现，不作为实体流体域。强调参数来自公开资料、厂家图纸和工程假设，具体来源见 source_traceability 与 parameter_assumptions。

### 3.3 Electro-thermal coupling formulation

给出导体焦耳热、接触热、RIP 介质损耗和稳态热传导方程。介质损耗采用 field-coupled 形式 `Qdielectric = omega * epsilon0 * epsr * tan_delta * |E|^2`。说明 S00 为高压端，S10 和法兰接地，S01-S09 为 floating potential。说明全局最大场强之外还输出 E95 和去边缘 probe 指标，以避免单点尖峰支配结论。

### 3.4 Operating condition matrix

介绍 RUN010 的 125 组核心矩阵：load multiplier、oil temperature、contact resistance multiplier。说明 voltage multiplier、air temperature、wind speed、tan_delta multiplier、RIP aging multiplier 和 pollution multiplier 在 RUN010 中固定。说明 RUN011 用代表工况验证网格无关性，并用单因素扰动分析材料和边界参数稳健性。

### 3.5 Model verification

组织 RUN006-RUN011 的证据链：source normalization、contact heat validation、heat balance validation、explicit by-ID selection、field singularity check、dielectric loss review、mesh independence、material/boundary sensitivity。强调当前是 finite element numerical verification，不是 physical experimental validation。

## 4. Results and Discussion

### 4.1 Baseline electro-thermal field distribution

介绍 RUN009A 基准工况下的电位、电场、介质损耗密度和温度场分布，突出 RIP 区域温度、导体温度和接触层温度并不完全相等，说明 selection 具有物理区分度。

### 4.2 Effect of load, oil temperature and contact resistance

基于 RUN010 讨论负荷倍率、油温和接触电阻倍率对 Tmax_global 与 Tmax_contact 的影响。写作时应强调趋势来自稳态有限元参数化工况。

### 4.3 Field-coupled dielectric loss contribution

比较 RUN008 approximate_Qdielectric_ref 和 RUN010 field-coupled Qdielectric。解释 field/ref 比值超过 10 的 review flag，并结合 field_singularity_flag=false 说明该差异不是由已标记的屏端奇异支配。

### 4.4 Risk boundary analysis

展示 RUN010 风险热力图和安全负荷边界。必须注明 risk zone 是 diagnostic risk zoning, not IEC/IEEE limit。

### 4.5 Mesh independence and sensitivity analysis

汇总 RUN011A medium-vs-fine 收敛结果和 RUN011B 敏感性排序。说明 tan_delta、epsr、Rc0、h_air、k_RIP、h_oil 对温度或介质损耗指标的影响顺序。

### 4.6 Engineering implication

从工程角度讨论接触电阻劣化、油温升高、空气侧换热降低和介质损耗参数不确定性对 RIP 套管热风险诊断的意义。避免把模型诊断阈值写成标准限值或寿命判据。
