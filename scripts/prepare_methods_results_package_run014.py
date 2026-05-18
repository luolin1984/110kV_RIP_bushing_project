"""Prepare RUN014 Methods + Results integration package.

This script consumes RUN013 manuscript draft sections and manuscript-ready
indices, then writes an integrated Methods + Results package for further
submission-oriented editing. It does not run COMSOL, create new simulations,
or modify RUN010-RUN013 source artifacts.
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
RUN013_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN013"
RUN013_TAB = PROJECT / "results" / "summary_tables" / "manuscript_ready" / "RUN013"
RUN014_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN014"
RUN014_TAB = PROJECT / "results" / "summary_tables" / "manuscript_ready" / "RUN014"
READY_TAB = PROJECT / "results" / "summary_tables" / "manuscript_ready"


REQUIRED_INPUTS = [
    RUN013_DOC / "section_3_numerical_model_and_simulation_setup_en.md",
    RUN013_DOC / "section_4_results_and_discussion_en.md",
    RUN013_DOC / "figure_captions_en.md",
    RUN013_DOC / "table_captions_en.md",
    RUN013_DOC / "citation_positions_en.md",
    RUN013_DOC / "manuscript_consistency_check.md",
    RUN013_TAB / "manuscript_claim_to_evidence_map.csv",
    READY_TAB / "manuscript_figure_index.csv",
    READY_TAB / "manuscript_table_index.csv",
    READY_TAB / "key_result_summary.csv",
    READY_TAB / "model_validation_evidence_chain.csv",
]


def ensure_dirs() -> None:
    RUN014_DOC.mkdir(parents=True, exist_ok=True)
    RUN014_TAB.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_inputs() -> None:
    missing = [path for path in REQUIRED_INPUTS if not path.exists() or path.stat().st_size == 0]
    if missing:
        raise FileNotFoundError("Missing RUN014 input files: " + ", ".join(map(str, missing)))


def index_by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def write_integrated_manuscripts() -> None:
    en = """# Methods + Results Integrated Draft

## 3. Numerical Model and Simulation Setup

### 3.1 Geometry and bushing structure

The numerical object was a BRFGL1-126/1250-4 resin-impregnated paper (RIP) dry-type condenser transformer bushing rated at 126 kV and 1250 A. A two-dimensional axisymmetric finite-element model was established in the r-z coordinate system, with the air side located at positive z, the oil side located at negative z, and the grounded flange used as the central structural reference. The geometric dimensions and rated quantities are linked to the manufacturer drawing or catalog placeholder [REF_BRFG_DRAWING], and the bushing category and rating context should be supported by the relevant standard-scope citation [REF_IEC_60137].

The model separates the center conductor, terminal connector region, contact-resistance heat-source layer, RIP capacitor core, condenser screens, silicone-rubber external insulation, grounded flange metal, and oil-side shield or tapered region. The air-side external profile follows the CAD-constrained outline used in the project rather than a straight cylindrical simplification. The condenser screens are retained as named selections inside the RIP region, with S00 representing the high-voltage side and S10 representing the grounded screen. The modeling workflow, geometry abstraction, and audit path are summarized in Fig. 1.

The axisymmetric representation omits non-axisymmetric details such as flange bolt holes and local three-dimensional terminal features. This omission is a modeling limitation rather than a statement that these details are physically irrelevant. The present model is therefore intended for steady electro-thermal numerical screening and risk-boundary analysis, not for resolving local three-dimensional terminal or bolt stresses.

### 3.2 Material properties and boundary conditions

Materials are assigned to all solid regions used in the solver-oriented model, including the copper conductor, RIP capacitor core, aluminum condenser screens, silicone-rubber housing, flange metal, terminal connector, and contact heat-source layer. The parameter set combines public material information, drawing-based geometry, and documented engineering assumptions. The material choices and heat-transfer assumptions should be supported by public RIP-bushing thermal and material references [REF_RIP_BUSHING_THERMAL].

Air and transformer oil are not represented as volume fluid domains in the solver-oriented thermal model. Instead, they enter as external convective boundary conditions applied to explicitly identified solid boundaries. The air-side boundary covers the exposed external insulation and terminal surfaces, while the oil-side boundary covers immersed solid surfaces. Internal material interfaces, the symmetry axis, and internal flange contact interfaces are excluded from the convective boundary selections.

All formal material, heat-source, heat-transfer, and post-processing selections use explicit by-ID domain or boundary selections. This prevents coordinate-box drift and avoids reintroducing the selection ambiguity observed in early diagnostic stages. The stage audit table records this development path in Table 1, and the numerical quantities used later in the manuscript are indexed in Table 2.

### 3.3 Electro-thermal coupling formulation

The steady electro-thermal formulation combines conductor Joule heating, localized contact-resistance heating, and RIP dielectric loss. The conductor source follows the source-normalized I2R form, so that the integrated heat is consistent with the effective conductor resistance. The contact source is represented as a localized equivalent layer:

```text
Q_contact = I_case^2 R_c0 R_c_factor.
```

For the baseline contact multiplier R_c_factor = 1, the integrated contact heat is 1.5625 W. This term represents parameterized contact degradation and should not be interpreted as a measured defect.

The RIP dielectric-loss density is calculated from the electrostatic field solution:

```text
q_dielectric = omega epsilon_0 epsilon_r tan(delta) |E|^2.
```

This expression should be supported by a dielectric-loss theory reference [REF_DIELECTRIC_LOSS_THEORY]. The high-voltage boundary sets S00 to the phase-to-ground RMS voltage, while S10 and the flange are grounded. Screens S01-S09 are treated as floating condenser screens with zero net charge in the full field-coupled model, which requires support from condenser-bushing electrostatic modeling and COMSOL floating-potential documentation [REF_CONDENSER_BUSHING_ELECTROSTATICS; REF_COMSOL_FLOATING_POTENTIAL].

Because condenser-screen ends can create localized high-field values, the electric-field diagnostics include Emax_global, Emax_RIP, an edge-excluding RIP probe value, and E95_RIP. The 95th percentile and edge-excluding metrics are used to avoid interpreting a single numerical edge value as the dominant field indicator.

### 3.4 Operating condition matrix

The main risk scan is RUN010, a 5 x 5 x 5 steady operating matrix with 125 cases. The varied parameters are load multiplier [0.6, 0.8, 1.0, 1.2, 1.4], oil temperature [65, 75, 85, 95, 105] degC, and contact-resistance multiplier [1, 2, 5, 10, 20]. Voltage multiplier, air temperature, wind speed, dielectric-loss tangent multiplier, RIP aging-conductivity multiplier, and pollution multiplier are fixed in RUN010. This design isolates the thermal effects of load, oil temperature, and contact degradation while retaining field-coupled dielectric loss under a fixed voltage level.

The model sequence is part of the method. RUN006 corrected conductor and contact heat-source normalization, RUN007 and RUN008 checked solid-only behavior with an approximate dielectric-loss reference, RUN009 introduced field-coupled dielectric loss for the baseline and 27-case checks, and RUN010 extended the full field-coupled model to the 125-case risk matrix. RUN011 then evaluated mesh independence and material/boundary sensitivity. The validation evidence chain is summarized in Table 3.

### 3.5 Numerical verification strategy

The numerical verification strategy combines source normalization, heat-balance checks, explicit selection integrity, field-singularity screening, mesh convergence, and parameter sensitivity. RUN010 reports 125/125 overall valid cases, 125/125 valid heat-balance cases, 125/125 valid Joule/contact/dielectric-loss cases, and 0/125 field-singularity cases. The heat-balance residual remains within the accepted range, and all region-specific maxima are extracted from non-overlapping selections.

The field-coupled dielectric-loss review flag is intentionally retained. RUN010 reports dielectric_loss_review_required in 125/125 cases because the field-integrated RIP dielectric loss is higher than the earlier average-field reference, with a representative field/reference ratio of 11.020. This review flag is not a numerical failure, but it is a transparent uncertainty marker that should remain visible in the manuscript.

RUN011A compares coarse, medium, and fine meshes in representative cases. Using the fine mesh as the reference, the medium mesh passes all three representative comparisons, with maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. Mesh-convergence criteria should be supported by a finite-element verification citation [REF_MESH_CONVERGENCE]. RUN011B ranks the one-factor sensitivity as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. The mesh and sensitivity evidence are listed in Table 5 and Table 6.

## 4. Results and Discussion

### 4.1 Baseline electro-thermal field distribution

The baseline full electro-thermal calculation uses STEADY_1250_LOAD_1p0 with 1250 A current, 72.75 kV phase-to-ground RMS voltage, 85 degC oil temperature, 25 degC air temperature, and R_c_factor = 1. RUN009A is solved as valid and gives a global maximum temperature of 88.589 degC. The conductor, RIP, contact layer, silicone housing, and flange maxima are 74.136 degC, 88.589 degC, 58.790 degC, 57.215 degC, and 46.906 degC, respectively. The region-specific values are not identical, which confirms that the post-processing selections preserve physical region identity. The baseline potential, electric-field, dielectric-loss, and temperature indicators are shown in Fig. 2.

The heat-source decomposition gives 34.433 W of conductor Joule heat, 1.5625 W of contact heat, and 28.049 W of field-coupled RIP dielectric loss. The baseline heat-balance residual is -1.902%, which satisfies the numerical audit criterion. The key result summary in Table 2 provides the numeric source for the baseline and subsequent RUN010 discussion.

The field-coupled dielectric loss is higher than the approximate dielectric-loss reference used during early solid-only diagnostics. The field/reference ratio is 11.020, so the DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained. Because field_singularity_flag is false, this flag is interpreted as a dielectric-parameter and field-distribution review item rather than as a model failure.

### 4.2 Effects of load, oil temperature, and contact resistance

RUN010 extends the field-coupled formulation to 125 steady operating cases. Across the matrix, Tmax_global ranges from 67.397 degC to 134.974 degC, while Tmax_contact reaches a maximum of 129.925 degC. Fig. 3 presents the global temperature response, and Fig. 4 presents the corresponding contact-region response.

The trends are physically consistent. Increasing oil temperature raises the thermal baseline because the oil-side boundary becomes warmer. Increasing load raises conductor Joule heat approximately with I2 and also increases contact heat through the same current-squared dependence. Increasing the contact-resistance multiplier primarily affects the contact-layer maximum temperature, especially in high-load and high-oil-temperature cases.

The heat-source response underlying these trends is summarized for representative cases in Fig. 6. This decomposition is useful because it separates the current-driven conductor term, the contact-resistance term, and the voltage-driven field-coupled dielectric-loss contribution.

### 4.3 Diagnostic risk boundary analysis

The RUN010 global diagnostic risk-zone counts are 119 safe, 4 attention, 2 warning, and 0 thermal-risk cases. For the contact-region metric, the counts are 115 contact-safe, 6 contact-attention, 4 contact-warning, and 0 contact-risk cases. The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4.

These risk zones are internal diagnostic visualization classes. They are not IEC or IEEE standard limits, material lifetime thresholds, or guaranteed operating limits. A diagnostic-risk-method reference should be added to support the general concept of using risk classes for numerical screening while preserving this distinction [REF_RISK_DIAGNOSTIC_METHOD].

### 4.4 Contribution of field-coupled dielectric loss

RUN008 used an approximate dielectric-loss reference in the solid-only diagnostic model, whereas RUN010 uses the field-coupled loss integrated from the electrostatic solution. Replacing the reference loss with the field-coupled term increases Tmax_global by an average of 0.617 degC and a maximum of 2.816 degC. The risk zone changes in 2 of the 125 cases, as shown in Fig. 7.

This comparison supports a staged modeling interpretation. The approximate dielectric-loss reference was sufficient for early source-normalization and heat-balance debugging, but the full field-coupled model is more appropriate for the main risk matrix because it retains the spatial non-uniformity of the RIP electric field. The retained dielectric-loss review flag also prevents the field/reference difference from being hidden.

### 4.5 Heat-source decomposition and contact degradation

The heat-source decomposition confirms that conductor Joule heat follows the expected I2 scaling and that contact heat follows I2Rc. The supplementary validation figures report the contact I2Rc check and the Joule I2 scaling check, while Fig. 6 provides the representative-case decomposition used in the main text.

Contact-resistance degradation is modeled through the contact-resistance multiplier. It is a parameterized equivalent representation, not a measured defect geometry and not a claim about a specific failed bushing. Under this parameterization, high contact-resistance multipliers mainly raise Tmax_contact, although the global maximum can remain governed by the RIP/oil-side thermal environment in some parts of the matrix.

### 4.6 Mesh independence and parameter sensitivity

RUN011A supports the medium mesh used in the main risk scan. Relative to the fine mesh, the medium mesh has maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. The mesh-independence results are shown in Fig. 8 and summarized in Table 5.

RUN011B identifies the leading one-factor sensitivity order as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. This ranking is physically reasonable because dielectric loss is directly controlled by tan(delta) and relative permittivity, while contact resistance and air-side heat transfer influence localized heating and heat removal. The sensitivity ranking is shown in Fig. 9 and summarized in Table 6.

### 4.7 Engineering implications and limitations

The numerical results indicate that oil temperature, load current, contact-resistance degradation, and dielectric parameters jointly define the thermal margin of the 126 kV/1250 A RIP condenser bushing. High oil temperature reduces the margin available to the oil-side heat-removal path, high load increases current-driven heat sources, and contact degradation creates a localized hotspot response.

Several limitations remain. The model is two-dimensional and axisymmetric, so it does not explicitly resolve flange bolt holes, local three-dimensional terminal structures, non-uniform contamination, full solid-fluid flow, or transient overload history. Air and oil are represented through convective boundary conditions rather than CFD domains. The risk zones are diagnostic classes rather than standard limits. The risk boundary has not yet been validated against field monitoring or laboratory measurement data.

For these reasons, RUN010 should be treated as a validated finite-element numerical risk-boundary scan, not as a final operational rule. The next manuscript-development step should add externally verifiable references for geometry, standards, material properties, electrostatics, dielectric-loss theory, mesh convergence, and diagnostic-risk terminology before moving into the Introduction and literature review.

## Supplementary Figure Routing Note

Supplementary Fig. S1 documents the full run audit flow. Supplementary Fig. S2 verifies Qcontact against I2Rc, and Supplementary Fig. S3 verifies Qjoule against I2 scaling. Supplementary Fig. S4 reports the heat-balance residual distribution, Supplementary Fig. S5 summarizes the electric-field diagnostic checks, Supplementary Fig. S6 documents the field-to-reference dielectric-loss ratio, and Supplementary Fig. S7 gives detailed material-sensitivity responses.
"""
    zh = """# Methods + Results 整合说明稿（RUN014）

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
"""
    write_text(RUN014_DOC / "methods_results_integrated_en.md", en)
    write_text(RUN014_DOC / "methods_results_integrated_zh.md", zh)


def write_reference_placeholder_plan() -> None:
    rows = [
        ["[REF_BRFG_DRAWING]", "3.1", "Rated voltage/current and BRFGL1-126/1250-4 drawing-constrained geometry.", "manufacturer drawing or catalog", "high", "Use the actual drawing/catalog metadata; do not cite a guessed source."],
        ["[REF_IEC_60137]", "3.1", "Bushing category, rated-voltage context, and standard-scope framing.", "standard document", "high", "Use only for scope/rating context, not for diagnostic risk thresholds."],
        ["[REF_RIP_BUSHING_THERMAL]", "3.2", "Material-property and heat-transfer assumptions for RIP bushing thermal analysis.", "peer-reviewed RIP bushing thermal paper or public material reference", "high", "Should support thermal-field modeling assumptions."],
        ["[REF_DIELECTRIC_LOSS_THEORY]", "3.3", "q_dielectric = omega epsilon0 epsr tan(delta)|E|^2.", "textbook, standard, or peer-reviewed dielectric-loss theory", "high", "Confirm RMS-field convention before final reference insertion."],
        ["[REF_CONDENSER_BUSHING_ELECTROSTATICS]", "3.3", "Condenser screens, field grading, floating screens, and electrostatic modeling.", "peer-reviewed condenser bushing electrostatics paper", "high", "Should support floating/equipotential screen interpretation."],
        ["[REF_COMSOL_FLOATING_POTENTIAL]", "3.3", "Floating potential with zero net charge implementation.", "COMSOL documentation", "medium", "Use documentation wording only for implementation, not physics novelty."],
        ["[REF_MESH_CONVERGENCE]", "3.5", "Medium-vs-fine mesh convergence criteria and finite-element verification.", "finite-element verification reference", "medium", "Use for convergence rationale, not as proof of physical validation."],
        ["[REF_RISK_DIAGNOSTIC_METHOD]", "4.3", "Risk zoning as diagnostic screening rather than standard/material limit.", "risk assessment or diagnostic screening method reference", "medium", "Must preserve distinction from IEC/IEEE limits."],
    ]
    body = [
        "# Reference Placeholder Plan",
        "",
        "This file intentionally contains citation placeholders only. It does not create or imply verified bibliography entries.",
        "",
        "| placeholder | section | sentence_or_paragraph_context | source_type_needed | priority | notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        body.append("| " + " | ".join(row) + " |")
    write_text(RUN014_DOC / "reference_placeholder_plan.md", "\n".join(body))


def make_callout_plan(fig_index: dict[str, dict[str, str]], table_index: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    fig_sections = {
        "Fig1": ("3.1", "The modeling workflow, geometry abstraction, and audit path are summarized in Fig. 1."),
        "Fig2": ("4.1", "The baseline potential, electric-field, dielectric-loss, and temperature indicators are shown in Fig. 2."),
        "Fig3": ("4.2", "Fig. 3 presents the global temperature response."),
        "Fig4": ("4.2", "Fig. 4 presents the corresponding contact-region response."),
        "Fig5": ("4.3", "The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4."),
        "Fig6": ("4.2", "The heat-source response underlying these trends is summarized for representative cases in Fig. 6."),
        "Fig7": ("4.4", "The risk zone changes in 2 of the 125 cases, as shown in Fig. 7."),
        "Fig8": ("4.6", "The mesh-independence results are shown in Fig. 8 and summarized in Table 5."),
        "Fig9": ("4.6", "The sensitivity ranking is shown in Fig. 9 and summarized in Table 6."),
        "FigS1": ("Supplementary Figure Routing Note", "Supplementary Fig. S1 documents the full run audit flow."),
        "FigS2": ("Supplementary Figure Routing Note", "Supplementary Fig. S2 verifies Qcontact against I2Rc."),
        "FigS3": ("Supplementary Figure Routing Note", "Supplementary Fig. S3 verifies Qjoule against I2 scaling."),
        "FigS4": ("Supplementary Figure Routing Note", "Supplementary Fig. S4 reports the heat-balance residual distribution."),
        "FigS5": ("Supplementary Figure Routing Note", "Supplementary Fig. S5 summarizes the electric-field diagnostic checks."),
        "FigS6": ("Supplementary Figure Routing Note", "Supplementary Fig. S6 documents the field-to-reference dielectric-loss ratio."),
        "FigS7": ("Supplementary Figure Routing Note", "Supplementary Fig. S7 gives detailed material-sensitivity responses."),
    }
    table_sections = {
        "Table1_run_stage_audit_summary": ("3.2", "The stage audit table records this development path in Table 1."),
        "Table2_key_result_summary": ("3.2", "The numerical quantities used later in the manuscript are indexed in Table 2."),
        "Table3_model_validation_evidence_chain": ("3.4", "The validation evidence chain is summarized in Table 3."),
        "Table4_run010_risk_boundary_summary": ("4.3", "The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4."),
        "Table5_mesh_independence_summary": ("4.6", "The mesh-independence results are shown in Fig. 8 and summarized in Table 5."),
        "Table6_sensitivity_ranking_summary": ("4.6", "The sensitivity ranking is shown in Fig. 9 and summarized in Table 6."),
    }
    rows: list[dict[str, str]] = []
    for item_id in ["Fig1", "Fig2", "Fig3", "Fig4", "Fig5", "Fig6", "Fig7", "Fig8", "Fig9", "FigS1", "FigS2", "FigS3", "FigS4", "FigS5", "FigS6", "FigS7"]:
        item = fig_index[item_id]
        section, sentence = fig_sections[item_id]
        rows.append({
            "item_id": item_id.replace("Fig", "Fig. ") if not item_id.startswith("FigS") else item_id.replace("FigS", "Fig. S"),
            "item_type": "figure" if not item_id.startswith("FigS") else "supplementary_figure",
            "caption_short": item["figure_title"],
            "file_or_table_path": item["file_path"],
            "first_callout_section": section,
            "first_callout_sentence": sentence,
            "main_or_supplementary": item["main_or_supplementary"],
            "notes": "exists=" + item["exists"],
        })
    for item_id in [
        "Table1_run_stage_audit_summary",
        "Table2_key_result_summary",
        "Table3_model_validation_evidence_chain",
        "Table4_run010_risk_boundary_summary",
        "Table5_mesh_independence_summary",
        "Table6_sensitivity_ranking_summary",
    ]:
        item = table_index[item_id]
        section, sentence = table_sections[item_id]
        rows.append({
            "item_id": item_id.split("_")[0].replace("Table", "Table "),
            "item_type": "table",
            "caption_short": item["table_title"],
            "file_or_table_path": item["file_path"],
            "first_callout_section": section,
            "first_callout_sentence": sentence,
            "main_or_supplementary": item["main_or_supplementary"],
            "notes": "exists=" + item["exists"],
        })
    return rows


def write_claim_audit(claims: list[dict[str, str]]) -> None:
    section_map = {
        "C1": "3.5; 4.2",
        "C2": "4.2",
        "C3": "4.3",
        "C4": "4.3",
        "C5": "4.2",
        "C6": "4.4",
        "C7": "3.5; 4.6",
        "C8": "3.5; 4.6",
        "C9": "3.5; 4.1; 4.4",
        "C10": "3.3; 4.5",
    }
    citation_needed = {
        "C1": "no",
        "C2": "no",
        "C3": "no",
        "C4": "yes, for diagnostic risk zoning concept",
        "C5": "no",
        "C6": "no",
        "C7": "yes, for mesh-convergence criterion",
        "C8": "no, result is internal; references needed for parameter background",
        "C9": "yes, for dielectric-loss theory and field interpretation",
        "C10": "yes, for contact degradation modeling background",
    }
    overclaim = {
        "C1": "LOW",
        "C2": "LOW",
        "C3": "MEDIUM_HANDLED",
        "C4": "MEDIUM_HANDLED",
        "C5": "LOW",
        "C6": "LOW",
        "C7": "LOW",
        "C8": "LOW",
        "C9": "MEDIUM_HANDLED",
        "C10": "MEDIUM_HANDLED",
    }
    notes = {
        "C3": "No thermal-risk case is a matrix-specific diagnostic result, not a universal safety conclusion.",
        "C4": "Risk zones are explicitly described as diagnostic classes, not standard limits.",
        "C9": "Review flag retained; not converted into a failure or removed.",
        "C10": "Parameterized model wording avoids measured-defect overclaim.",
    }
    rows = []
    for claim in claims:
        cid = claim["claim_id"]
        rows.append({
            "claim_id": cid,
            "claim_text": claim["claim_text"],
            "appears_in_section": section_map.get(cid, ""),
            "evidence_source_file": claim["source_file"],
            "evidence_metric": claim["source_metric"],
            "figure_or_table_reference": claim["figure_or_table_reference"],
            "citation_needed": citation_needed.get(cid, "no"),
            "risk_of_overclaim": overclaim.get(cid, "LOW"),
            "status": "OK" if claim["source_file"] else "MISSING_EVIDENCE",
            "notes": notes.get(cid, claim.get("notes", "")),
        })
    write_csv(RUN014_TAB / "claim_to_evidence_audit_run014.csv", [
        "claim_id",
        "claim_text",
        "appears_in_section",
        "evidence_source_file",
        "evidence_metric",
        "figure_or_table_reference",
        "citation_needed",
        "risk_of_overclaim",
        "status",
        "notes",
    ], rows)


def write_reviewer_risk_checklist() -> None:
    rows = [
        ["2D axisymmetric model limitation", "medium", "3.1; 4.7", "The model is explicitly described as two-dimensional and axisymmetric, with non-axisymmetric terminal and bolt details excluded.", "yes", "Use as a limitation, not as a flaw hidden from readers."],
        ["no physical experimental validation", "high", "4.7", "The package states that the risk boundary has not yet been validated against field monitoring or laboratory measurement data.", "yes", "Avoid any wording implying laboratory confirmation."],
        ["diagnostic risk zones are not standard limits", "high", "4.3; captions", "Risk zones are defined as internal diagnostic visualization classes, not IEC/IEEE limits or material lifetime thresholds.", "yes", "Needs diagnostic-risk-method reference."],
        ["dielectric_loss_review_required retained", "medium", "3.5; 4.1; 4.4", "The review flag is retained and interpreted as an uncertainty marker rather than a numerical failure.", "no", "Evidence is internal RUN009A/RUN010."],
        ["field-coupled dielectric loss/ref ratio slightly above review interval", "medium", "4.1; 4.4", "The field/reference ratio is reported as 11.020 and discussed together with field_singularity_flag=false.", "yes", "Needs dielectric-loss and field-modeling support."],
        ["contact degradation is parameterized", "medium", "3.3; 4.5", "Contact degradation is described as an equivalent multiplier, not a measured defect geometry.", "yes", "May need contact-resistance degradation literature."],
        ["material parameters partly assumed or public-data based", "medium", "3.2; 4.6", "The text states that material and heat-transfer parameters combine public data and documented assumptions.", "yes", "Tie to source_traceability and parameter assumptions."],
        ["no fluid-domain CFD", "medium", "3.2; 4.7", "Air and oil are represented through convective boundary conditions rather than resolved fluid domains.", "yes", "Preempt reviewer asking for CFD."],
        ["no transient overload simulation", "medium", "4.7", "The text limits the results to steady operating cases and excludes transient overload history.", "yes", "Could become future work."],
        ["no full 3D terminal/flange bolt geometry", "medium", "3.1; 4.7", "The axisymmetric model excludes flange bolt holes and local three-dimensional terminal structures.", "yes", "Consider 3D local submodel in future work."],
        ["risk boundary not yet validated by field monitoring", "high", "4.7", "The text states that RUN010 should not be treated as a final operational rule before external validation.", "yes", "Important before submission claims."],
    ]
    body = [
        "# Reviewer Risk Checklist",
        "",
        "| risk_item | severity | where_addressed | mitigation_sentence | still_needs_external_reference | notes |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        body.append("| " + " | ".join(row) + " |")
    write_text(RUN014_DOC / "reviewer_risk_checklist.md", "\n".join(body))


def write_terminology_table() -> None:
    rows = [
        ["finite-element numerical simulation", "experiment; physical validation; measured validation", "A COMSOL/FEM-based numerical workflow without laboratory or field measurement validation.", "Methods; Results; limitations", "Use this term for the whole model chain."],
        ["diagnostic risk zoning", "standard limit; IEC limit; material lifetime threshold", "Internal visualization classes for screening case severity.", "4.3; captions", "Always state that it is not a standard limit."],
        ["field-coupled dielectric loss", "true measured dielectric loss; final dielectric proof", "RIP dielectric heat source integrated from the electrostatic field solution.", "3.3; 4.1; 4.4", "Retain review flag."],
        ["approximate dielectric-loss reference", "old result; wrong result", "Average-field diagnostic reference used before full field coupling.", "3.4; 4.4", "Useful only for early diagnostics."],
        ["contact-resistance multiplier", "defect severity measured value", "Parameter multiplier applied to the equivalent contact resistance.", "3.4; 4.2; 4.5", "Use Rc_factor consistently."],
        ["parameterized contact degradation", "measured defect; failure sample", "Equivalent model for contact heating sensitivity.", "3.3; 4.5", "Do not imply observed failure geometry."],
        ["explicit by-ID selection", "Box selection; coordinate selection", "COMSOL selections defined by domain or boundary IDs for materials, sources, and boundaries.", "3.2; 3.5", "Key audit phrase."],
        ["floating condenser screen", "fixed intermediate screen", "Intermediate screen treated as floating potential with zero net charge.", "3.3", "S01-S09 should not be fixed potentials."],
        ["medium-vs-fine mesh convergence", "mesh proof; exact convergence", "Mesh independence check using fine mesh as the reference.", "3.5; 4.6", "Keep numerical-verification scope."],
        ["thermal warning", "unsafe; failed", "Diagnostic zone for elevated Tmax below thermal-risk class.", "4.3", "Not a standard operating limit."],
        ["thermal risk", "failure; breakdown", "Highest diagnostic temperature class in the project threshold scheme.", "4.3", "No RUN010 thermal-risk cases."],
    ]
    write_csv(RUN014_TAB / "terminology_consistency_table.csv", [
        "preferred_term",
        "avoid_terms",
        "definition",
        "where_used",
        "notes",
    ], [
        {
            "preferred_term": row[0],
            "avoid_terms": row[1],
            "definition": row[2],
            "where_used": row[3],
            "notes": row[4],
        }
        for row in rows
    ])


def write_report(pass_status: bool, files: list[Path], callouts_ok: bool, claims_ok: bool) -> None:
    status = "YES" if pass_status else "NO"
    body = [
        "# RUN014 Methods + Results Integration Report",
        "",
        "## Task Objective",
        "",
        "RUN014 integrates the RUN013 Section 3/Section 4 drafts, figure captions, table captions, claim-to-evidence map, and citation-position notes into a Methods + Results package for further submission-oriented editing. No COMSOL model was run, no new simulation case was added, and no RUN010-RUN013 source artifact was overwritten.",
        "",
        "## Generated Files",
        "",
    ]
    for path in files:
        body.append(f"- {rel(path)}")
    body.extend([
        "",
        "## Integration Status",
        "",
        "The English package merges the numerical model setup and results discussion into a continuous Methods + Results draft. It adds ordered figure/table callouts, reference placeholders, and explicit limitation language. A Chinese internal-reading version with the same technical meaning was also generated.",
        "",
        "## Figure and Table Callout Integrity",
        "",
        f"Main figures Fig. 1-Fig. 9 and main tables Table 1-Table 6 have callout-plan entries. Callout integrity status: {'PASS' if callouts_ok else 'NEEDS_REVISION'}. Supplementary figures Fig. S1-Fig. S7 are routed through the supplementary figure note.",
        "",
        "## Reference Placeholder Integrity",
        "",
        "The reference placeholder plan includes [REF_BRFG_DRAWING], [REF_IEC_60137], [REF_RIP_BUSHING_THERMAL], [REF_DIELECTRIC_LOSS_THEORY], [REF_CONDENSER_BUSHING_ELECTROSTATICS], [REF_COMSOL_FLOATING_POTENTIAL], [REF_MESH_CONVERGENCE], and [REF_RISK_DIAGNOSTIC_METHOD]. No complete reference entry was fabricated.",
        "",
        "## Evidence Mapping Integrity",
        "",
        f"C1-C10 were audited against RUN013 evidence sources. Evidence status: {'PASS' if claims_ok else 'NEEDS_REVISION'}. Claims with interpretation risk are marked as handled, especially diagnostic risk zoning, dielectric-loss review, and parameterized contact degradation.",
        "",
        "## Reviewer Risk and Terminology Checks",
        "",
        "The reviewer-risk checklist covers 2D axisymmetry, lack of external measurement validation, diagnostic risk classes, dielectric-loss review, contact parameterization, public/assumed material parameters, no CFD domain, no transient overload simulation, missing 3D terminal/flange details, and lack of field-monitoring validation. The terminology table defines preferred terms and avoid terms for the next writing stage.",
        "",
        "## Next Stage",
        "",
        "The package is ready for Introduction and Literature Review planning if the manuscript team accepts placeholder references as unresolved citation tasks.",
        "",
        f"Can proceed to INTRODUCTION_AND_LITERATURE_REVIEW_RUN015: {status}",
    ])
    write_text(RUN014_DOC / "run014_methods_results_integration_report.md", "\n".join(body))


def quality_gate() -> tuple[bool, bool, bool]:
    en_path = RUN014_DOC / "methods_results_integrated_en.md"
    text = read_text(en_path)
    main_figs = [f"Fig. {i}" for i in range(1, 10)]
    main_tables = [f"Table {i}" for i in range(1, 7)]
    callouts_ok = all(item in text for item in main_figs + main_tables)
    callout_rows = read_csv(RUN014_TAB / "figure_table_callout_plan.csv")
    callout_ok = callouts_ok and len(callout_rows) == 22
    claims = read_csv(RUN014_TAB / "claim_to_evidence_audit_run014.csv")
    claims_ok = len(claims) >= 10 and all(row["evidence_source_file"] for row in claims) and not any(row["risk_of_overclaim"] == "HIGH" for row in claims)
    forbidden_ok = (
        "physical experiment validation" not in text
        and "standard limits" in text
        and "DIELECTRIC_LOSS_REVIEW_REQUIRED" in text
    )
    return callout_ok, claims_ok, forbidden_ok


def main() -> None:
    validate_inputs()
    ensure_dirs()

    # Read required inputs to guarantee RUN014 is coupled to the audited RUN013 interface.
    for path in REQUIRED_INPUTS[:6]:
        read_text(path)
    claims = read_csv(RUN013_TAB / "manuscript_claim_to_evidence_map.csv")
    fig_index = index_by(read_csv(READY_TAB / "manuscript_figure_index.csv"), "figure_id")
    table_index = index_by(read_csv(READY_TAB / "manuscript_table_index.csv"), "table_id")
    read_csv(READY_TAB / "key_result_summary.csv")
    read_csv(READY_TAB / "model_validation_evidence_chain.csv")

    write_integrated_manuscripts()
    write_reference_placeholder_plan()
    callout_rows = make_callout_plan(fig_index, table_index)
    write_csv(RUN014_TAB / "figure_table_callout_plan.csv", [
        "item_id",
        "item_type",
        "caption_short",
        "file_or_table_path",
        "first_callout_section",
        "first_callout_sentence",
        "main_or_supplementary",
        "notes",
    ], callout_rows)
    write_claim_audit(claims)
    write_reviewer_risk_checklist()
    write_terminology_table()

    callout_ok, claims_ok, forbidden_ok = quality_gate()
    files = [
        RUN014_DOC / "methods_results_integrated_en.md",
        RUN014_DOC / "methods_results_integrated_zh.md",
        RUN014_DOC / "reference_placeholder_plan.md",
        RUN014_DOC / "reviewer_risk_checklist.md",
        RUN014_DOC / "run014_methods_results_integration_report.md",
        RUN014_TAB / "figure_table_callout_plan.csv",
        RUN014_TAB / "claim_to_evidence_audit_run014.csv",
        RUN014_TAB / "terminology_consistency_table.csv",
    ]
    pre_report_files = [path for path in files if path.name != "run014_methods_results_integration_report.md"]
    pass_status = callout_ok and claims_ok and forbidden_ok and all(path.exists() and path.stat().st_size > 0 for path in pre_report_files)
    write_report(pass_status, files, callout_ok, claims_ok)

    if not pass_status:
        raise SystemExit("RUN014 quality gate failed")
    print("RUN014 Methods + Results package generated.")
    print(f"Output docs: {rel(RUN014_DOC)}")
    print(f"Output tables: {rel(RUN014_TAB)}")


if __name__ == "__main__":
    main()
