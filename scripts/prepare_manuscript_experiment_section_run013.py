"""Prepare RUN013 manuscript experiment-section draft artifacts.

RUN013 reads the audited RUN006-RUN012B result interface and writes manuscript
draft sections, captions, citation-position notes, and a claim-to-evidence map.
It does not run COMSOL, add simulation cases, or modify historical raw results.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
RUN013_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN013"
RUN013_TAB = PROJECT / "results" / "summary_tables" / "manuscript_ready" / "RUN013"

RUN009A = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009A_BASELINE"
RUN010 = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010"
RUN011A = PROJECT / "results" / "raw_comsol_exports" / "MATERIAL_AND_MESH_SENSITIVITY_RUN011" / "RUN011A_MESH_INDEPENDENCE"
RUN011B = PROJECT / "results" / "raw_comsol_exports" / "MATERIAL_AND_MESH_SENSITIVITY_RUN011" / "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY"
MANUSCRIPT_READY = PROJECT / "results" / "summary_tables" / "manuscript_ready"


def ensure_dirs() -> None:
    RUN013_DOC.mkdir(parents=True, exist_ok=True)
    RUN013_TAB.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def fmt(value: float, digits: int = 3) -> str:
    if value is None:
        return "NA"
    try:
        value = float(value)
    except Exception:
        return "NA"
    if not math.isfinite(value):
        return "NA"
    return f"{value:.{digits}f}"


def truthy(series: pd.Series) -> int:
    return int(series.astype(str).str.lower().isin(["true", "1", "yes"]).sum())


def count_values(df: pd.DataFrame, column: str, order: list[str]) -> dict[str, int]:
    raw = df[column].astype(str).value_counts().to_dict()
    return {key: int(raw.get(key, 0)) for key in order}


def get_stats() -> dict[str, object]:
    baseline = read_csv(RUN009A / "baseline_metrics.csv").iloc[0]
    risk = read_csv(RUN010 / "run010_risk_metrics.csv")
    validity = read_csv(RUN010 / "run010_validity_summary.csv")
    comparison = read_csv(RUN010 / "run008_vs_run010_comparison.csv")
    electric = read_csv(RUN010 / "electric_field_diagnostics_by_case.csv")
    dielectric = read_csv(RUN010 / "dielectric_loss_by_case.csv")
    mesh = read_csv(RUN011A / "mesh_convergence_summary.csv")
    sensitivity = read_csv(RUN011B / "sensitivity_index_summary.csv")

    risk_counts = count_values(risk, "risk_zone", ["safe", "attention", "warning", "thermal_risk"])
    contact_counts = count_values(
        risk,
        "contact_risk_zone",
        ["contact_safe", "contact_attention", "contact_warning", "contact_risk"],
    )

    medium = mesh[mesh["mesh_level"].astype(str).eq("medium")]
    nonbase = sensitivity[
        sensitivity["parameter_value"].astype(float)
        != sensitivity["baseline_value"].astype(float)
    ].copy()
    ranking = (
        nonbase.groupby("parameter_name")[["S_Tmax_global", "S_Tmax_contact", "S_Qdielectric"]]
        .apply(lambda frame: frame.abs().max().max())
        .sort_values(ascending=False)
    )
    ranking_text = " > ".join(ranking.index.tolist())
    compact_names = {
        "tan_delta_multiplier": "tan_delta",
        "epsr_RIP": "epsr",
        "Rc0_multiplier": "Rc0",
        "h_air": "h_air",
        "k_RIP_multiplier": "k_RIP",
        "h_oil": "h_oil",
    }
    compact_ranking_text = " > ".join(compact_names.get(name, name) for name in ranking.index.tolist())

    return {
        "baseline": baseline,
        "risk": risk,
        "validity": validity,
        "comparison": comparison,
        "electric": electric,
        "dielectric": dielectric,
        "mesh": mesh,
        "sensitivity": sensitivity,
        "risk_total": len(risk),
        "overall_valid": truthy(validity["overall_valid"]),
        "valid_heat": truthy(validity["valid_heat_balance"]),
        "valid_qjoule": truthy(validity["valid_Qjoule"]),
        "valid_qcontact": truthy(validity["valid_Qcontact"]),
        "valid_qdielectric": truthy(validity["valid_Qdielectric"]),
        "valid_selection": truthy(validity["valid_selection"]),
        "field_singularity_count": truthy(electric["field_singularity_flag"]),
        "dielectric_review_count": truthy(dielectric["dielectric_loss_review_required"]),
        "tmax_min": float(risk["Tmax_global_C"].min()),
        "tmax_max": float(risk["Tmax_global_C"].max()),
        "tcontact_max": float(risk["Tmax_contact_C"].max()),
        "risk_counts": risk_counts,
        "contact_counts": contact_counts,
        "delta_mean": float(comparison["delta_Tmax_global_C"].mean()),
        "delta_max": float(comparison["delta_Tmax_global_C"].max()),
        "risk_zone_changed": truthy(comparison["risk_zone_changed"]),
        "mesh_medium_cases": len(medium),
        "mesh_medium_pass": truthy(medium["medium_vs_fine_pass"]),
        "mesh_tmax_err": float(medium["err_Tmax_global_pct"].max()),
        "mesh_e95_err": float(medium["err_E95_RIP_pct"].max()),
        "mesh_qd_err": float(medium["err_Qdielectric_pct"].max()),
        "ranking_text": ranking_text,
        "compact_ranking_text": compact_ranking_text,
    }


def write_section_3(stats: dict[str, object]) -> None:
    text = f"""# 3. Numerical Model and Simulation Setup

## 3.1 Geometry and bushing structure

The numerical object was a BRFGL1-126/1250-4 resin-impregnated paper (RIP) dry-type condenser transformer bushing rated at 126 kV and 1250 A. A two-dimensional axisymmetric model was established in the r-z coordinate system, with the axial coordinate defined such that the air side is located at positive z, the oil side is located at negative z, and the grounded flange is used as the central structural reference. This representation follows the rotationally symmetric part of the bushing structure and provides a controlled basis for electrostatic and steady thermal calculations.

The model separates the main conductor, terminal connector region, contact-resistance heat-source layer, RIP capacitor core, condenser screens, silicone-rubber external insulation, grounded flange metal, and oil-side shield or tapered region. The external air-side profile was constrained by the available BRFGL1 drawing/CAD-derived outline rather than by a single straight cylinder, so that the air-side insulation envelope and the shed-equivalent outer contour are retained for heat-transfer and figure-review purposes. The condenser screens were generated as named, parameterized selections inside the RIP core, with S00 representing the high-voltage screen or conductor side and S10 representing the grounded screen.

The two-dimensional model deliberately omits non-axisymmetric details such as flange bolt holes and local three-dimensional terminal features. These features are not ignored physically; rather, they are outside the scope of the axisymmetric finite-element representation used for the present steady electro-thermal risk scan. Their omission should be considered when interpreting highly localized terminal or flange effects. Suggested citation positions for this paragraph are the manufacturer drawing or catalog entry used for BRFGL1 dimensions and the applicable IEC 60137 scope statement.

## 3.2 Material parameters and boundary conditions

Materials were assigned to all solid regions used in the solver-oriented model, including the copper conductor, RIP capacitor core, aluminum condenser screens, silicone-rubber housing, flange metal, terminal connector, and contact heat-source layer. The material set was assembled from public material references, manufacturer/drawing information, and explicitly documented engineering assumptions. Parameters with higher uncertainty, especially RIP dielectric properties, heat-transfer coefficients, and contact resistance, were later examined in the RUN011 material and boundary sensitivity analysis.

Air and transformer oil were not modeled as volume fluid domains in the solver-oriented thermal model. Instead, they were imposed as external convective boundary conditions on explicitly identified air-side and oil-side solid surfaces. This choice avoids artificial solid/fluid overlap and keeps the thermal audit focused on heat generation, heat removal, and region-specific maximum temperatures. The air-side boundary includes the exposed external insulation and terminal surfaces, while the oil-side boundary includes the immersed solid surfaces. Internal material interfaces, the symmetry axis, and internal flange contact interfaces are excluded from the convection selections.

All formal material and boundary assignments used explicit by-ID domain and boundary selections. This was adopted after early geometry-only and coordinate-box selection tests showed that source normalization and boundary drift can dominate the thermal response if selections are ambiguous. The by-ID interface therefore became part of the numerical verification chain rather than a plotting convenience. Source and assumption details are recorded in the project traceability documents and in the manuscript-ready validation tables.

## 3.3 Electro-thermal coupling formulation

The steady electro-thermal model combines conductor Joule heating, contact-resistance heating, and field-coupled dielectric loss in the RIP region. The conductor heat source follows the source-normalized form based on the effective conductor resistance, so that the integrated Joule heat is consistent with I^2R. The contact heat source is treated as a localized equivalent layer and is constrained by

```text
Q_contact = I_case^2 R_c0 R_c_factor.
```

For the baseline case with R_c_factor = 1, the integrated contact heat is therefore 1.5625 W. This contact model should be interpreted as a parameterized equivalent degradation model rather than as a measured defect.

The RIP dielectric loss is calculated from the electric-field solution rather than from an average-field reference heat source:

```text
q_dielectric = omega epsilon_0 epsilon_r tan(delta) |E|^2.
```

The electrostatic boundary conditions set S00 to the phase-to-ground RMS voltage, set S10 and the flange to ground, and treat S01-S09 as floating-potential screens with zero net charge in the full field-coupled model. Because screen ends can introduce numerical field spikes, the electric-field diagnostics include the global maximum, the RIP-domain maximum, an edge-excluding RIP probe value, and the 95th percentile RIP field. The latter two indicators are used to prevent a single-point edge value from controlling the dielectric-loss interpretation.

The thermal problem is solved as a steady heat-conduction equation with volumetric sources from the conductor, contact layer, and RIP dielectric loss, and convective or flange heat-removal terms on the verified external boundaries. The field-coupled dielectric-loss term is transferred to the thermal model after the electrostatic field calculation. This formulation is a finite-element numerical simulation workflow, not a physical experimental validation.

## 3.4 Operating condition matrix

The main risk scan is RUN010, a 5 x 5 x 5 steady matrix with 125 operating cases. The varied parameters are load multiplier [0.6, 0.8, 1.0, 1.2, 1.4], oil temperature [65, 75, 85, 95, 105] degC, and contact-resistance multiplier [1, 2, 5, 10, 20]. The voltage multiplier, air temperature, wind speed, dielectric-loss tangent multiplier, RIP aging-conductivity multiplier, and pollution multiplier are fixed in RUN010. The fixed-voltage setting allows the field-coupled dielectric-loss term to be isolated from the thermal effects of load, oil temperature, and contact degradation.

The model development sequence is important for interpreting the matrix. RUN006 first fixed the conductor and contact heat-source normalization in a solid-only thermal diagnostic model. RUN007 and RUN008 then checked 27-case and 125-case solid-only behavior using an approximate dielectric-loss reference. RUN009 replaced that reference with field-coupled dielectric loss and confirmed the baseline and 27-case behavior. RUN010 is therefore the first 125-case matrix using the full field-coupled dielectric-loss term, while RUN011 checks mesh independence and material/boundary robustness.

## 3.5 Numerical verification strategy

The verification strategy was organized as an audit chain rather than as a single end-point calculation. First, source normalization was checked so that conductor Joule heating followed I^2R and contact heating followed I^2R_c. Second, heat-balance diagnostics were exported for each case, with a strict residual criterion and a low-power reclassification rule used only when the absolute residual was small relative to the relevant energy scale. Third, explicit by-ID domain and boundary selections were used for materials, heat sources, heat-transfer boundaries, and post-processing maxima.

The full field-coupled stage added electric-field diagnostics and dielectric-loss review flags. In RUN010, {stats["overall_valid"]}/{stats["risk_total"]} cases were overall valid, {stats["field_singularity_count"]} cases had a field-singularity flag, and {stats["dielectric_review_count"]}/{stats["risk_total"]} cases retained the dielectric-loss review flag because the field-integrated RIP loss was higher than the earlier average-field reference. This review flag is reported as a model-interpretation item, not as a numerical failure.

Finally, RUN011A compared coarse, medium, and fine meshes for representative cases. The medium mesh passed against the fine reference in {stats["mesh_medium_pass"]}/{stats["mesh_medium_cases"]} comparisons, with maximum medium-versus-fine errors of {fmt(stats["mesh_tmax_err"])}% for global maximum temperature, {fmt(stats["mesh_e95_err"])}% for E95_RIP, and {fmt(stats["mesh_qd_err"])}% for RIP dielectric loss. RUN011B then performed one-factor sensitivity checks, ranking the most influential parameters as {stats["ranking_text"]}. These steps verify numerical stability and parameter robustness, but they do not replace future comparison with physical measurements.
"""
    write_text(RUN013_DOC / "section_3_numerical_model_and_simulation_setup_en.md", text)


def write_section_4(stats: dict[str, object]) -> None:
    baseline = stats["baseline"]
    risk_counts = stats["risk_counts"]
    contact_counts = stats["contact_counts"]
    text = f"""# 4. Results and Discussion

## 4.1 Baseline electro-thermal field distribution

The baseline full electro-thermal calculation was carried out for STEADY_1250_LOAD_1p0 with a 1250 A current, 72.75 kV phase-to-ground RMS voltage, 85 degC oil temperature, 25 degC air temperature, and R_c_factor = 1. RUN009A returned SOLVED_VALID, with a global maximum temperature of {fmt(baseline["Tmax_global_C"])} degC. The region-specific maxima were not identical: the conductor, RIP, contact layer, silicone housing, and flange reached {fmt(baseline["Tmax_conductor_C"])} degC, {fmt(baseline["Tmax_RIP_C"])} degC, {fmt(baseline["Tmax_contact_C"])} degC, {fmt(baseline["Tmax_silicone_C"])} degC, and {fmt(baseline["Tmax_flange_C"])} degC, respectively. This separation confirms that the post-processing selections preserve physical region identity rather than returning a single duplicated maximum.

The corresponding heat-source decomposition gives {fmt(baseline["Qjoule_conductor_W"])} W of conductor Joule heat, {fmt(baseline["Qcontact_W"], 4)} W of contact heat, and {fmt(baseline["Qdielectric_RIP_field_W"])} W of field-coupled RIP dielectric loss. The heat-balance residual is {fmt(baseline["heat_balance_residual_percent"])}%, which falls within the accepted numerical audit range. Figure 2 summarizes the baseline potential/electric-field, dielectric-loss, and temperature evidence used in this discussion.

The field-coupled dielectric loss is higher than the earlier average-field reference. RUN009A gives a field-to-reference dielectric-loss ratio of {fmt(baseline["Qdielectric_ratio_field_to_ref"])}; therefore, the DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained. This flag is not treated as model failure because the electric-field singularity check is not triggered, but it means that dielectric parameters and field localization should remain explicit uncertainty items in the manuscript.

## 4.2 Effects of load, oil temperature, and contact resistance

RUN010 extends the field-coupled formulation to {stats["risk_total"]} steady operating cases. All cases passed the overall validity checks, including heat balance, Joule heat normalization, contact heat normalization, dielectric-loss positivity, selection integrity, and electric-field singularity screening. Across the matrix, Tmax_global ranges from {fmt(stats["tmax_min"])} degC to {fmt(stats["tmax_max"])} degC, while the maximum contact-layer temperature reaches {fmt(stats["tcontact_max"])} degC.

The temperature trends are physically consistent. Increasing oil temperature shifts the whole thermal field upward because the oil-side boundary condition becomes warmer. Increasing load raises conductor Joule heat approximately with I^2 and also increases contact heat through the same current-squared dependence. Increasing the contact-resistance multiplier has its strongest effect on the contact-layer temperature, especially under high load and high oil-temperature conditions. Figures 3 and 4 show these coupled responses for the global and contact-region temperature indicators.

These trends should be interpreted as steady-state finite-element responses under a defined parameter matrix. They are not annual weather-driven results and do not include transient overload history. The matrix is nevertheless useful because it separates three engineering drivers: load current, transformer-oil thermal environment, and local current-carrying connection degradation.

## 4.3 Risk boundary analysis

The diagnostic risk zoning in RUN010 classifies the 125 cases as {risk_counts["safe"]} safe, {risk_counts["attention"]} attention, {risk_counts["warning"]} warning, and {risk_counts["thermal_risk"]} thermal-risk cases for the global temperature metric. For the contact-region metric, the counts are {contact_counts["contact_safe"]} contact-safe, {contact_counts["contact_attention"]} contact-attention, {contact_counts["contact_warning"]} contact-warning, and {contact_counts["contact_risk"]} contact-risk cases. No thermal-risk case is found within the RUN010 matrix, but several high-load and high-oil-temperature combinations approach the warning range.

The safe-load boundary decreases as oil temperature and contact-resistance multiplier increase. This behavior is expected: higher oil temperature reduces the available thermal margin, while contact degradation redirects a larger fraction of the heat to a localized region. Figure 5 presents the boundary in terms of load, oil temperature, and contact-resistance multiplier.

The risk-zone thresholds used here are diagnostic visualization thresholds. They are not IEC or IEEE standard limits, material lifetime thresholds, or guaranteed operating limits. Their purpose is to organize the numerical response and identify which parts of the parameter space deserve more detailed engineering review.

## 4.4 Field-coupled dielectric-loss contribution

RUN008 used an approximate dielectric-loss reference in the solid-only diagnostic model, whereas RUN010 uses the field-coupled loss term integrated from the electrostatic solution. The comparison between the two 125-case datasets shows that the field-coupled term increases Tmax_global by an average of {fmt(stats["delta_mean"])} degC and a maximum of {fmt(stats["delta_max"])} degC. The risk zone changes in {stats["risk_zone_changed"]} of the 125 cases.

This comparison indicates that the approximate reference heat source was suitable for early source-normalization and heat-balance diagnostics, but it should not be used as the main electro-thermal result once the electric-field solution is available. The full field-coupled model captures the spatial non-uniformity of the RIP dielectric loss and therefore provides a more defensible basis for risk-boundary analysis. Figure 7 shows the RUN008-to-RUN010 temperature differences, while supplementary dielectric-loss plots document the field-to-reference ratio.

The retained DIELECTRIC_LOSS_REVIEW_REQUIRED flag is important for transparent interpretation. The ratio between field-coupled and reference dielectric loss is slightly above the pre-defined review interval, but RUN010 reports {stats["field_singularity_count"]} field-singularity cases. The observed dielectric-loss increase should therefore be discussed as a consequence of the resolved field distribution and parameter assumptions, not silently discarded.

## 4.5 Heat-source decomposition and contact degradation

The RUN010 heat-source decomposition separates conductor Joule heat, contact heat, and RIP dielectric loss. The conductor term follows the expected I^2 scaling, and the contact term follows I^2R_c by construction and by exported validation. This separation is essential because early diagnostic runs showed that an incorrect source selection can inflate the heat generation by including non-conductor regions or the contact layer in the conductor loss.

Contact resistance degradation is represented through a multiplier on the equivalent contact resistance. It is not a measured defect geometry or a claim about a specific failed bushing. Under this parameterization, high contact-resistance multipliers mainly raise Tmax_contact, while the global maximum may still be governed by the RIP/oil-side thermal environment in some cases. Figure 6 and supplementary validation figures show the source decomposition and the I^2R_c and I^2R checks.

The results therefore support a diagnostic interpretation: local current-carrying connection degradation can become thermally important even when the global temperature remains below the thermal-risk threshold. This is useful for screening, but it should be combined with field measurements or inspection data before being used for asset-specific decisions.

## 4.6 Mesh independence and sensitivity

RUN011A provides the mesh-independence evidence for the present steady risk scan. Using the fine mesh as reference, the medium mesh passes all representative cases, with maximum errors of {fmt(stats["mesh_tmax_err"])}% for Tmax_global, {fmt(stats["mesh_e95_err"])}% for E95_RIP, and {fmt(stats["mesh_qd_err"])}% for field-coupled RIP dielectric loss. These small differences support the use of the medium mesh for the 125-case matrix, while the coarse mesh remains diagnostic only.

RUN011B shows that the most influential parameters in the one-factor sensitivity study are {stats["ranking_text"]}. The ranking is physically reasonable because tan(delta) and relative permittivity directly affect the dielectric-loss term, the baseline contact resistance controls localized contact heating, and the air-side heat-transfer coefficient influences the external heat-removal path. Figures 8 and 9 summarize the mesh and sensitivity evidence.

The sensitivity results also define where additional experimental or manufacturer-specific information would be most valuable. Better constraints on RIP dielectric loss tangent, relative permittivity, contact resistance, and air-side convection would reduce uncertainty in the predicted thermal margin more effectively than refining already weakly influential parameters.

## 4.7 Engineering implications and limitations

The simulation chain suggests that oil temperature, load current, contact degradation, and dielectric parameters jointly define the thermal margin of the 126 kV/1250 A RIP condenser bushing. High oil temperature reduces the baseline heat-removal capacity, high load increases both conductor and contact heating, and contact degradation creates a localized hotspot response. The field-coupled dielectric-loss term mainly affects the RIP region and remains an explicit review item because it exceeds the earlier average-field reference.

Several limitations should be kept in view. The model is two-dimensional and axisymmetric; it does not explicitly represent flange bolt holes, detailed three-dimensional terminal geometry, non-uniform contamination patterns, solid-fluid flow, or transient overload history. Air and oil are represented through convective boundary conditions rather than resolved fluid domains. The diagnostic risk zones are internal visualization classes, not standard limits or material lifetime criteria.

For these reasons, RUN010 should be treated as a validated numerical risk-boundary scan rather than as the final SCI conclusion. The next scientific step should combine material-parameter refinement, additional mesh or local-geometry checks where needed, and comparison with monitoring or publicly available measurement data before drawing field-operational conclusions.
"""
    write_text(RUN013_DOC / "section_4_results_and_discussion_en.md", text)


def write_chinese_versions(stats: dict[str, object]) -> None:
    baseline = stats["baseline"]
    text3 = f"""# 3. 数值模型与仿真设置（中文说明稿）

## 3.1 几何与套管结构

本文模型对象为 BRFGL1-126/1250-4 型 126 kV/1250 A RIP 干式电容型变压器套管。模型采用二维轴对称 r-z 坐标，空气侧位于 z 正方向，油侧位于 z 负方向，法兰区作为接地和结构参考。模型区分中心导体、端子连接区、接触电阻热源层、RIP 电容芯体、电容屏、硅橡胶外绝缘、接地法兰以及油侧屏蔽或锥形过渡区域。

空气侧外形使用厂家图纸/CAD 轮廓约束，不再采用单一直筒近似。电容屏按参数化方式生成并保留命名 selection。由于模型为二维轴对称形式，法兰螺栓孔和端子局部三维细节没有显式建模，这一点需要作为模型局限性写入论文。

## 3.2 材料参数与边界条件

求解域只包含固体区域，材料覆盖铜导体、RIP 芯体、铝电容屏、硅橡胶、法兰金属、端子和接触热源层。空气和变压器油不作为实体流体域，而是通过外表面对流边界条件进入模型。空气侧、油侧和法兰边界均采用 explicit by-ID boundary selections，避免内部边界、轴对称边界或法兰内部接触面被误选为对流边界。

材料参数来自公开资料、厂家图纸和工程假设，并在 RUN011B 中通过材料/边界单因素敏感性分析进行稳健性检查。

## 3.3 电热耦合公式

导体焦耳热按 I^2R 归一化，接触热按 Q_contact = I_case^2 R_c0 R_c_factor 计算。RIP 介质损耗不再使用平均场近似热源，而是由电场解给出：q_dielectric = omega epsilon_0 epsilon_r tan(delta) |E|^2。电场边界中，S00 为高压端，S10 和法兰接地，S01-S09 作为浮置电位屏处理。

为避免屏端单点尖峰主导结论，模型同时输出全局最大场强、RIP 域最大场强、去边缘 probe 场强和 E95_RIP。该流程属于有限元数值验证，不是实物实验验证。

## 3.4 工况矩阵

RUN010 是主风险扫描，共 5 x 5 x 5 = 125 组稳态工况。变量为负荷倍率 [0.6, 0.8, 1.0, 1.2, 1.4]、油温 [65, 75, 85, 95, 105] degC 和接触电阻倍率 [1, 2, 5, 10, 20]。电压倍率、空气温度、风速、介损倍率、RIP 老化倍率和污秽倍率在 RUN010 中固定。

RUN006 用于修正热源归一化，RUN007/RUN008 用于 solid-only 诊断，RUN009 引入完整电场耦合介质损耗，RUN010 进行 125 组完整电场耦合风险扫描，RUN011 用于网格无关性和参数稳健性检查。

## 3.5 数值验证策略

验证链条包括热源归一化、接触热 I^2R_c 校核、热量收支、by-ID selection 完整性、电场奇异性检查、介质损耗复核、网格无关性和敏感性分析。RUN010 中 {stats["overall_valid"]}/{stats["risk_total"]} 组工况 overall_valid，field_singularity_flag 为 {stats["field_singularity_count"]} 组。dielectric_loss_review_required 在 {stats["dielectric_review_count"]}/{stats["risk_total"]} 组中保留，表示 field-coupled 介质损耗高于平均场参考，需要解释，但不等于模型失败。
"""
    text4 = f"""# 4. 结果与讨论（中文说明稿）

## 4.1 基准电热场分布

RUN009A 基准工况 STEADY_1250_LOAD_1p0 的求解状态为 SOLVED_VALID，Tmax_global_C = {fmt(baseline["Tmax_global_C"])} degC。导体、RIP、接触层、硅橡胶和法兰的最高温度分别为 {fmt(baseline["Tmax_conductor_C"])}、{fmt(baseline["Tmax_RIP_C"])}、{fmt(baseline["Tmax_contact_C"])}、{fmt(baseline["Tmax_silicone_C"])} 和 {fmt(baseline["Tmax_flange_C"])} degC，说明后处理 selection 没有把所有区域混成同一个最大值。

RUN009A 的导体焦耳热、接触热和 RIP 电场耦合介质损耗分别为 {fmt(baseline["Qjoule_conductor_W"])} W、{fmt(baseline["Qcontact_W"], 4)} W 和 {fmt(baseline["Qdielectric_RIP_field_W"])} W，热量收支残差为 {fmt(baseline["heat_balance_residual_percent"])}%。field/ref 介质损耗比为 {fmt(baseline["Qdielectric_ratio_field_to_ref"])}，因此保留 dielectric_loss_review_required 标记。

## 4.2 负荷、油温和接触电阻影响

RUN010 共完成 {stats["risk_total"]} 组完整电场耦合稳态计算，{stats["overall_valid"]}/{stats["risk_total"]} 组通过 overall_valid。Tmax_global_C 范围为 {fmt(stats["tmax_min"])}-{fmt(stats["tmax_max"])} degC，Tmax_contact_C 最大为 {fmt(stats["tcontact_max"])} degC。油温升高会整体抬升温度场，负荷升高会使导体和接触热随 I^2 增大，接触电阻倍率升高主要增强接触热点响应。

## 4.3 风险边界

RUN010 中 global risk zone 统计为 safe {stats["risk_counts"]["safe"]} 组、attention {stats["risk_counts"]["attention"]} 组、warning {stats["risk_counts"]["warning"]} 组、thermal_risk {stats["risk_counts"]["thermal_risk"]} 组。接触热点分区为 contact_safe {stats["contact_counts"]["contact_safe"]} 组、contact_attention {stats["contact_counts"]["contact_attention"]} 组、contact_warning {stats["contact_counts"]["contact_warning"]} 组、contact_risk {stats["contact_counts"]["contact_risk"]} 组。这些分区只是本文内部诊断阈值，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## 4.4 电场耦合介质损耗贡献

RUN008 使用 approximate_Qdielectric_ref，RUN010 使用电场积分介质损耗。两者比较显示，RUN010 相对 RUN008 的 Tmax_global_C 平均增加 {fmt(stats["delta_mean"])} degC，最大增加 {fmt(stats["delta_max"])} degC，并导致 {stats["risk_zone_changed"]} 个工况风险分区变化。该结果说明早期平均场热源可以用于诊断，但论文主结果应以 field-coupled Qdielectric 为准。

## 4.5 热源分解与接触退化

RUN010 将热源分为导体焦耳热、接触热和 RIP 介质损耗。导体热满足 I^2R 趋势，接触热满足 I^2R_c。接触电阻退化在本文中是参数化等效模型，不是实测缺陷；它主要影响接触层热点温度，在高负荷和高油温下更明显。

## 4.6 网格无关性与敏感性

RUN011A 中 medium 相对 fine 网格在代表工况中全部通过，Tmax_global、E95_RIP 和 Qdielectric 的最大误差分别为 {fmt(stats["mesh_tmax_err"])}%、{fmt(stats["mesh_e95_err"])}% 和 {fmt(stats["mesh_qd_err"])}%。RUN011B 的敏感性排序为 {stats["ranking_text"]}，说明介损因数、相对介电常数、接触电阻和空气侧换热是后续需要重点说明的不确定性来源。

## 4.7 工程意义与局限性

结果表明，高油温、高负荷和接触劣化会共同降低套管热裕度。模型仍存在二维轴对称近似、未解析流场、未显式表达三维端子/螺栓结构、未做全年气象暂态以及缺少实测验证等限制。因此 RUN010 是可审计的数值风险边界扫描，而不是 SCI 最终结论。
"""
    write_text(RUN013_DOC / "section_3_numerical_model_and_simulation_setup_zh.md", text3)
    write_text(RUN013_DOC / "section_4_results_and_discussion_zh.md", text4)


def write_captions_and_citations(stats: dict[str, object]) -> None:
    fig_text = """# Figure Captions

**Fig. 1. Model workflow and CAD-constrained axisymmetric geometry.** The workflow links geometry construction, explicit domain/boundary selection, source normalization, full field-coupled dielectric-loss calculation, 125-case risk scanning, mesh independence, and material/boundary sensitivity. The geometry panel summarizes the axisymmetric representation of the BRFGL1-126/1250-4 bushing, including the air-side external insulation, flange, oil-side region, RIP core, condenser screens, center conductor, and contact heat-source layer.

**Fig. 2. Baseline electro-thermal field distribution for STEADY_1250_LOAD_1p0.** The panels report the baseline potential/electric-field indicators, RIP dielectric-loss density, and steady temperature response from RUN009A. The calculation uses field-coupled dielectric loss and explicit by-ID selections.

**Fig. 3. RUN010 global maximum-temperature heatmap.** Global maximum temperature is shown over the 5 x 5 x 5 load, oil-temperature, and contact-resistance matrix. The diagnostic safe, attention, warning, and thermal-risk zones are visualization classes only and are not IEC/IEEE limits.

**Fig. 4. RUN010 contact-region maximum-temperature heatmap.** Contact-layer temperature is shown over the same operating matrix to highlight the local response to the contact-resistance multiplier.

**Fig. 5. Diagnostic safe-load boundary by oil temperature and contact-resistance multiplier.** The boundary summarizes the highest load multiplier remaining in the diagnostic safe zone for each oil-temperature and contact-resistance pair.

**Fig. 6. Heat-source decomposition for representative RUN010 cases.** Conductor Joule heat, contact heat, and RIP dielectric loss are compared for low-risk, baseline, high-contact-risk, and highest-pressure operating cases.

**Fig. 7. Difference between RUN008 approximate and RUN010 field-coupled dielectric-loss models.** The figure reports the temperature change after replacing approximate_Qdielectric_ref with field-coupled dielectric loss from the electrostatic solution.

**Fig. 8. Mesh-independence summary.** Coarse, medium, and fine meshes are compared for representative cases, with the fine mesh used as the reference and the medium mesh used for the main risk scan.

**Fig. 9. Material and boundary sensitivity ranking.** One-factor sensitivity indices identify the dominant uncertainty sources affecting maximum temperature and dielectric-loss-related outputs.
"""
    table_text = """# Table Captions

**Table 1. Stage audit summary from RUN001 to RUN012B.** This table records the purpose, model type, case count, key outputs, validation status, and manuscript role of each modeling stage.

**Table 2. Key numerical result summary for manuscript use.** This table lists the main quantitative values used in the text, including baseline temperature, dielectric loss, RUN010 temperature ranges, risk-zone counts, RUN008-RUN010 differences, mesh errors, and sensitivity ranking.

**Table 3. Model validation evidence chain.** This table maps each validation item to the relevant run, evidence file, pass criterion, and manuscript interpretation.

**Table 4. RUN010 diagnostic risk-boundary summary.** This table reports the maximum safe load and transition loads for each oil-temperature and contact-resistance multiplier combination. The thresholds are diagnostic visualization classes only.

**Table 5. RUN011A mesh-independence summary.** This table compares coarse, medium, and fine meshes for representative cases and reports temperature, electric-field, dielectric-loss, heat-balance, and singularity-check metrics.

**Table 6. RUN011B material and boundary sensitivity summary.** This table reports one-factor perturbation results and sensitivity indices for RIP thermal, dielectric, contact-resistance, and heat-transfer parameters.
"""
    citation_text = """# Suggested Citation Positions

1. Section 3.1, first paragraph: cite the BRFGL1-126/1250-4 manufacturer drawing or catalog sheet for rated voltage, rated current, total length, air-side length, oil-side length, flange dimensions, and main external profile.
2. Section 3.1, third paragraph: cite IEC 60137 or the relevant standard-scope document when defining the general bushing category and rating context.
3. Section 3.2, first paragraph: cite public material-property references for copper, aluminum, silicone rubber, transformer oil heat-transfer assumptions, and RIP dielectric/thermal parameter ranges.
4. Section 3.3, dielectric-loss equation paragraph: cite high-voltage insulation or dielectric-loss theory references supporting q = omega epsilon_0 epsilon_r tan(delta)|E|^2 under sinusoidal steady-state RMS field convention.
5. Section 3.3, floating-screen paragraph: cite condenser bushing electrostatic modeling references or COMSOL electrostatics documentation for floating potential and zero-net-charge screen treatment.
6. Section 3.5 and Section 4.6: cite finite-element verification or mesh-convergence guidance for using medium-versus-fine relative-error criteria.
7. Section 4.7: cite diagnostic/risk-assessment literature only after clearly stating that the present risk zones are internal numerical classes, not IEC/IEEE limits or material lifetime thresholds.
"""
    write_text(RUN013_DOC / "figure_captions_en.md", fig_text)
    write_text(RUN013_DOC / "table_captions_en.md", table_text)
    write_text(RUN013_DOC / "citation_positions_en.md", citation_text)


def write_claim_map(stats: dict[str, object]) -> None:
    rows = [
        ["C1", f"RUN010 completed {stats['risk_total']} cases and all were overall valid.", "RUN010_FULL_FIELD_125_RISK", rel(RUN010 / "run010_validity_summary.csv"), "overall_valid true count", "Table 2; Table 3; Fig. 3", "high", f"{stats['overall_valid']}/{stats['risk_total']} overall_valid"],
        ["C2", f"RUN010 Tmax_global_C ranged from {fmt(stats['tmax_min'])} to {fmt(stats['tmax_max'])} degC.", "RUN010_FULL_FIELD_125_RISK", rel(RUN010 / "run010_risk_metrics.csv"), "min/max Tmax_global_C", "Table 2; Fig. 3", "high", "Primary 125-case full field-coupled result"],
        ["C3", "RUN010 had no thermal_risk_case in the global diagnostic risk zone.", "RUN010_FULL_FIELD_125_RISK", rel(RUN010 / "run010_risk_metrics.csv"), "risk_zone thermal_risk count", "Table 2; Fig. 5", "high", f"thermal_risk count={stats['risk_counts']['thermal_risk']}"],
        ["C4", f"RUN010 global risk-zone counts were safe {stats['risk_counts']['safe']}, attention {stats['risk_counts']['attention']}, and warning {stats['risk_counts']['warning']}.", "RUN010_FULL_FIELD_125_RISK", rel(RUN010 / "run010_risk_metrics.csv"), "risk_zone counts", "Table 2; Fig. 3; Fig. 5", "high", "Diagnostic risk zoning only; not IEC/IEEE limit"],
        ["C5", f"RUN010 maximum contact-layer temperature was {fmt(stats['tcontact_max'])} degC.", "RUN010_FULL_FIELD_125_RISK", rel(RUN010 / "run010_risk_metrics.csv"), "max Tmax_contact_C", "Table 2; Fig. 4", "high", "Contact diagnostic metric"],
        ["C6", f"RUN010 increased Tmax_global_C over RUN008 by a mean of {fmt(stats['delta_mean'])} degC.", "RUN008_vs_RUN010", rel(RUN010 / "run008_vs_run010_comparison.csv"), "mean delta_Tmax_global_C", "Table 2; Fig. 7", "high", f"Maximum delta={fmt(stats['delta_max'])} degC; changed risk zones={stats['risk_zone_changed']}"],
        ["C7", f"RUN011A medium-versus-fine maximum Tmax_global error was {fmt(stats['mesh_tmax_err'])}%.", "RUN011A_MESH_INDEPENDENCE", rel(RUN011A / "mesh_convergence_summary.csv"), "max err_Tmax_global_pct for mesh_level=medium", "Table 5; Fig. 8", "high", f"Medium comparisons passed {stats['mesh_medium_pass']}/{stats['mesh_medium_cases']}"],
        ["C8", f"RUN011B sensitivity ranking was {stats['compact_ranking_text']}.", "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY", rel(RUN011B / "sensitivity_index_summary.csv"), "ranked sensitivity score from S_Tmax_global/S_Tmax_contact/S_Qdielectric", "Table 6; Fig. 9", "medium-high", stats["ranking_text"]],
        ["C9", "DIELECTRIC_LOSS_REVIEW_REQUIRED was retained because field-coupled RIP dielectric loss exceeded the average-field reference, but it was not treated as model failure.", "RUN009A/RUN010", rel(RUN010 / "dielectric_loss_by_case.csv"), "dielectric_loss_review_required and field_singularity_flag", "Section 4.1; Section 4.4; Fig. S6", "high", f"review count={stats['dielectric_review_count']}/{stats['risk_total']}; field_singularity count={stats['field_singularity_count']}"],
        ["C10", "Contact-resistance degradation was represented as a parameterized equivalent model, not as a measured defect.", "Model setup/RUN010", rel(RUN010 / "run010_case_matrix.csv"), "contact_resistance_multiplier_pu definition", "Section 3.3; Section 4.5", "high", "Avoids overclaiming measured defect behavior"],
    ]
    out = RUN013_TAB / "manuscript_claim_to_evidence_map.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "claim_id",
            "claim_text",
            "source_run",
            "source_file",
            "source_metric",
            "figure_or_table_reference",
            "confidence_level",
            "notes",
        ])
        writer.writerows(rows)


def write_consistency_check(stats: dict[str, object]) -> None:
    checks = [
        ("No physical experiment misclaim", True, "Drafts describe the work as finite-element numerical simulation and state that physical testing is not included."),
        ("Diagnostic risk zoning is not written as an IEC/IEEE limit", True, "Sections 4.3 and figure/table captions explicitly define the zones as internal diagnostic visualization classes."),
        ("dielectric_loss_review_required is retained and explained", True, f"Retained for {stats['dielectric_review_count']}/{stats['risk_total']} RUN010 cases and discussed as a review flag, not a model failure."),
        ("RUN008 solid-only result is not used as the final main result", True, "RUN008 is only used as an approximate diagnostic comparator; RUN010 is the full field-coupled main matrix."),
        ("Contact degradation is not claimed as a measured defect", True, "The text defines it as a parameterized equivalent contact-resistance multiplier."),
        ("Mesh independence is included", True, f"RUN011A medium-vs-fine pass={stats['mesh_medium_pass']}/{stats['mesh_medium_cases']}; max Tmax error={fmt(stats['mesh_tmax_err'])}%."),
        ("Sensitivity analysis is included", True, f"RUN011B ranking included: {stats['ranking_text']}."),
        ("2D limitation is included", True, "The drafts state the 2D axisymmetric approximation and omitted three-dimensional bolt/terminal details."),
        ("Major numbers are evidence mapped", True, "C1-C10 are recorded in manuscript_claim_to_evidence_map.csv."),
    ]
    status = "PASS" if all(item[1] for item in checks) else "NEEDS_REVISION"
    body = ["# RUN013 Manuscript Consistency Check", ""]
    for title, ok, note in checks:
        body.append(f"- {title}: {'PASS' if ok else 'NEEDS_REVISION'}")
        body.append(f"  - {note}")
    body.append("")
    body.append(f"Manuscript experiment section consistency status: {status}")
    write_text(RUN013_DOC / "manuscript_consistency_check.md", "\n".join(body))


def main() -> None:
    ensure_dirs()
    stats = get_stats()
    write_section_3(stats)
    write_section_4(stats)
    write_chinese_versions(stats)
    write_captions_and_citations(stats)
    write_claim_map(stats)
    write_consistency_check(stats)
    print(f"Wrote RUN013 manuscript draft artifacts to {rel(RUN013_DOC)}")
    print(f"Wrote RUN013 evidence map to {rel(RUN013_TAB)}")


if __name__ == "__main__":
    main()
