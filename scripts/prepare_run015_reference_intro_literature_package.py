"""Prepare RUN015 reference, introduction, literature, and evidence lock package.

RUN015 consumes the RUN014 Methods + Results package and existing audited
evidence tables. It writes introduction/literature drafts, reference-resolution
planning tables, claim-boundary notes, and a text-evidence lock table.

This script does not run COMSOL, add simulation cases, or modify RUN006-RUN014
source artifacts.
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Iterable


PROJECT = Path(__file__).resolve().parents[1]
RUN014_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN014"
RUN014_TAB = PROJECT / "results" / "summary_tables" / "manuscript_ready" / "RUN014"
RUN015_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN015"
RUN015_TAB = PROJECT / "results" / "summary_tables" / "manuscript_ready" / "RUN015"
READY = PROJECT / "results" / "summary_tables" / "manuscript_ready"
RAW = PROJECT / "results" / "raw_comsol_exports"

RUN009A = RAW / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009A_BASELINE"
RUN010 = RAW / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010"
RUN011A = RAW / "MATERIAL_AND_MESH_SENSITIVITY_RUN011" / "RUN011A_MESH_INDEPENDENCE"
RUN011B = RAW / "MATERIAL_AND_MESH_SENSITIVITY_RUN011" / "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY"

LIT_DIR = Path("/Users/luolin/Desktop/@近期思路/5-考虑接触电阻劣化与环境扰动的110 kV RIP变压器套管电热耦合响应及风险边界分析/文献")
BRFGL_DIR = Path("/Users/luolin/Desktop/@近期思路/5-考虑接触电阻劣化与环境扰动的110 kV RIP变压器套管电热耦合响应及风险边界分析/BRFGL1-126:1250-4参数")


REQUIRED_RUN014 = [
    RUN014_DOC / "methods_results_integrated_en.md",
    RUN014_DOC / "reference_placeholder_plan.md",
    RUN014_DOC / "reviewer_risk_checklist.md",
    RUN014_DOC / "run014_methods_results_integration_report.md",
    RUN014_TAB / "figure_table_callout_plan.csv",
    RUN014_TAB / "claim_to_evidence_audit_run014.csv",
    RUN014_TAB / "terminology_consistency_table.csv",
]

REQUIRED_EVIDENCE = [
    READY / "key_result_summary.csv",
    READY / "model_validation_evidence_chain.csv",
    READY / "manuscript_figure_index.csv",
    READY / "manuscript_table_index.csv",
    RUN010 / "run010_risk_metrics.csv",
    RUN010 / "run010_validity_summary.csv",
    RUN010 / "dielectric_loss_by_case.csv",
    RUN010 / "electric_field_diagnostics_by_case.csv",
    RUN011A / "mesh_convergence_summary.csv",
    RUN011B / "sensitivity_index_summary.csv",
]

OPTIONAL_EVIDENCE_FOR_LOCK = [
    RUN009A / "baseline_metrics.csv",
    RUN010 / "heat_balance_by_case.csv",
    RUN010 / "run008_vs_run010_comparison.csv",
]


PLACEHOLDERS = [
    "[REF_BRFG_DRAWING]",
    "[REF_IEC_60137]",
    "[REF_RIP_BUSHING_THERMAL]",
    "[REF_DIELECTRIC_LOSS_THEORY]",
    "[REF_CONDENSER_BUSHING_ELECTROSTATICS]",
    "[REF_COMSOL_FLOATING_POTENTIAL]",
    "[REF_MESH_CONVERGENCE]",
    "[REF_RISK_DIAGNOSTIC_METHOD]",
]


def ensure_dirs() -> None:
    RUN015_DOC.mkdir(parents=True, exist_ok=True)
    RUN015_TAB.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT))
    except ValueError:
        return str(path)


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


def existing(paths: Iterable[Path]) -> list[Path]:
    return [path for path in paths if path.exists() and path.stat().st_size > 0]


def missing(paths: Iterable[Path]) -> list[Path]:
    return [path for path in paths if not path.exists() or path.stat().st_size == 0]


def fnum(value: str | float | int) -> float:
    if isinstance(value, (float, int)):
        return float(value)
    return float(str(value).strip())


def fmt(value: float, digits: int = 3) -> str:
    if not math.isfinite(value):
        return "NA"
    return f"{value:.{digits}f}"


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def count_true(rows: list[dict[str, str]], column: str) -> int:
    return sum(1 for row in rows if truthy(row[column]))


def list_lit(pattern: str) -> list[Path]:
    if not LIT_DIR.exists():
        return []
    return sorted(path for path in LIT_DIR.glob("*.pdf") if re.search(pattern, path.name, re.I))


def candidate_key(path: Path) -> str:
    stem = re.sub(r"\.pdf$", "", path.name, flags=re.I)
    stem = re.sub(r"^\[(\d+)\]\s*", r"LOCAL_LIT_\1_", stem)
    stem = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_")
    return stem[:90]


def title_from_file(path: Path) -> str:
    title = re.sub(r"^\[\d+\]\s*", "", path.name)
    title = re.sub(r"\.pdf$", "", title, flags=re.I)
    return title


def joined_keys(paths: list[Path]) -> str:
    return "; ".join(candidate_key(path) for path in paths)


def joined_titles(paths: list[Path]) -> str:
    return "; ".join(title_from_file(path) for path in paths)


def joined_paths(paths: list[Path]) -> str:
    return "; ".join(str(path) for path in paths)


def build_reference_resolution_rows() -> list[dict[str, str]]:
    drawing_files = existing([
        BRFGL_DIR / "Drawing1.dwg",
        BRFGL_DIR / "Drawing1.dxf",
        BRFGL_DIR / "BRFGL1-126:1250-4.png",
        PROJECT / "data" / "raw_sources" / "manufacturer_catalogs" / "cad" / "BRFGL1-126-1250-4_Drawing1.dxf",
    ])
    rip_thermal = list_lit(r"Temperature distribution|Heat analysis|thermal|3-D coupled|electro-thermal")
    dielectric = list_lit(r"Dielectric|tan|space charge|hot spot temperature|Diagnostic challenges")
    condenser = list_lit(r"Inner insulation|condenser|electro-thermal comprehensive|floating|screen")
    contact = list_lit(r"contact|current-carrying|deterioration")

    rows = [
        {
            "placeholder": "[REF_BRFG_DRAWING]",
            "section": "1; 3.1",
            "claim_or_context": "BRFGL1-126/1250-4 model identity, rated voltage/current, and drawing-constrained geometry.",
            "source_type_needed": "manufacturer drawing, catalog sheet, or controlled CAD drawing",
            "candidate_reference_key": "LOCAL_BRFGL1_DRAWING_FILES" if drawing_files else "",
            "candidate_reference_title": "BRFGL1-126/1250-4 Drawing1 DWG/DXF/PNG local files" if drawing_files else "",
            "candidate_reference_type": "local drawing/CAD file",
            "source_status": "LOCAL_FILE_FOUND_NEEDS_MANUFACTURER_METADATA_CONFIRMATION" if drawing_files else "UNRESOLVED",
            "confidence": "medium" if drawing_files else "low",
            "verified_by": joined_paths(drawing_files) if drawing_files else "not found locally",
            "notes": "Use only after confirming drawing provenance and permissions; do not infer manufacturer name if not in file metadata.",
        },
        {
            "placeholder": "[REF_IEC_60137]",
            "section": "1; 3.1",
            "claim_or_context": "Bushing standard scope and rating-context background.",
            "source_type_needed": "official IEC 60137 text or official IEC page",
            "candidate_reference_key": "IEC60137_2017_WEBSTORE_TRACEABILITY_RECORD",
            "candidate_reference_title": "IEC 60137 official webstore/source traceability record",
            "candidate_reference_type": "standard/source traceability entry",
            "source_status": "TRACEABILITY_RECORD_EXISTS_NEEDS_STANDARD_TEXT_CONFIRMATION",
            "confidence": "medium-low",
            "verified_by": rel(PROJECT / "docs" / "source_traceability.md"),
            "notes": "Do not quote clauses or limits until the official standard text is checked.",
        },
        {
            "placeholder": "[REF_RIP_BUSHING_THERMAL]",
            "section": "1; 2; 3.2",
            "claim_or_context": "RIP bushing thermal modeling, load/oil/ambient effects, finite-element or electro-thermal studies.",
            "source_type_needed": "peer-reviewed RIP/bushing thermal analysis literature",
            "candidate_reference_key": joined_keys(rip_thermal),
            "candidate_reference_title": joined_titles(rip_thermal),
            "candidate_reference_type": "local peer-reviewed PDF candidates",
            "source_status": "LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION" if rip_thermal else "UNRESOLVED",
            "confidence": "medium",
            "verified_by": joined_paths(rip_thermal),
            "notes": "Filenames support relevance only; final bibliography must verify journal, DOI, and exact claims.",
        },
        {
            "placeholder": "[REF_DIELECTRIC_LOSS_THEORY]",
            "section": "2; 3.3; 4.4",
            "claim_or_context": "Dielectric-loss density q = omega epsilon0 epsr tan(delta)|E|^2 and interpretation of tan delta.",
            "source_type_needed": "dielectric theory textbook/standard plus RIP dielectric-response papers",
            "candidate_reference_key": joined_keys(dielectric),
            "candidate_reference_title": joined_titles(dielectric),
            "candidate_reference_type": "local dielectric PDF candidates; theory reference still needed",
            "source_status": "PARTIALLY_RESOLVED_WITH_LOCAL_PDFS_NEEDS_THEORY_REFERENCE_CONFIRMATION" if dielectric else "UNRESOLVED",
            "confidence": "medium-low",
            "verified_by": joined_paths(dielectric),
            "notes": "Local papers may support material response; equation should be checked against a theory source and RMS convention.",
        },
        {
            "placeholder": "[REF_CONDENSER_BUSHING_ELECTROSTATICS]",
            "section": "2; 3.3",
            "claim_or_context": "Condenser screens, field grading, electrostatics, and floating/intermediate screen treatment.",
            "source_type_needed": "peer-reviewed condenser bushing electrostatic/electro-thermal modeling literature",
            "candidate_reference_key": joined_keys(condenser),
            "candidate_reference_title": joined_titles(condenser),
            "candidate_reference_type": "local peer-reviewed PDF candidates",
            "source_status": "LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION" if condenser else "UNRESOLVED",
            "confidence": "medium",
            "verified_by": joined_paths(condenser),
            "notes": "Need verify that selected paper actually discusses screen/electrostatic implementation.",
        },
        {
            "placeholder": "[REF_COMSOL_FLOATING_POTENTIAL]",
            "section": "3.3",
            "claim_or_context": "COMSOL Floating Potential / zero net charge implementation for floating screens.",
            "source_type_needed": "COMSOL official documentation",
            "candidate_reference_key": "",
            "candidate_reference_title": "",
            "candidate_reference_type": "official software documentation",
            "source_status": "UNRESOLVED",
            "confidence": "low",
            "verified_by": "no local official COMSOL documentation found by RUN015 script",
            "notes": "Requires manual or later online lookup of official COMSOL Electrostatics documentation.",
        },
        {
            "placeholder": "[REF_MESH_CONVERGENCE]",
            "section": "2; 3.5; 4.6",
            "claim_or_context": "Finite-element mesh convergence or medium-vs-fine verification criterion.",
            "source_type_needed": "finite-element verification/mesh-convergence reference",
            "candidate_reference_key": "",
            "candidate_reference_title": "",
            "candidate_reference_type": "textbook, standard, or numerical-method paper",
            "source_status": "UNRESOLVED",
            "confidence": "low",
            "verified_by": "internal RUN011A evidence only; external reference not identified",
            "notes": "Internal data prove convergence for this model; external source is still needed for manuscript framing.",
        },
        {
            "placeholder": "[REF_RISK_DIAGNOSTIC_METHOD]",
            "section": "1; 2; 4.3; 4.7",
            "claim_or_context": "Diagnostic risk zoning as a screening method rather than a standard limit.",
            "source_type_needed": "diagnostic screening/risk assessment method reference",
            "candidate_reference_key": joined_keys(contact[:2]) if contact else "",
            "candidate_reference_title": joined_titles(contact[:2]) if contact else "",
            "candidate_reference_type": "local diagnostic/contact-degradation candidates; method reference still needed",
            "source_status": "PARTIALLY_RESOLVED_WITH_LOCAL_APPLICATION_PDFS_NEEDS_METHOD_REFERENCE" if contact else "UNRESOLVED",
            "confidence": "medium-low",
            "verified_by": joined_paths(contact[:2]) if contact else "not found locally",
            "notes": "Use for engineering motivation only unless the candidate explicitly supports risk-zoning methodology.",
        },
    ]
    return rows


def write_introduction_literature() -> None:
    en = """# 1. Introduction

High-voltage transformer bushings provide the electrical and mechanical transition between grounded transformer tanks and energized conductors. For a 126 kV/1250 A resin-impregnated paper (RIP) condenser transformer bushing, the thermal margin is shaped by the rated-current path, the condenser-core electric field, the oil-side thermal environment, and the air-side cooling condition. The geometry and rated context of the BRFGL1-126/1250-4 bushing should be supported by the controlled drawing or catalog source [REF_BRFG_DRAWING], while the general bushing rating and standard-scope background should be linked to the appropriate IEC reference [REF_IEC_60137].

RIP condenser bushings are attractive because the condenser core can distribute the electric field through a graded screen structure, but this same structure makes the thermal problem inherently multi-source. Current-driven conductor loss, contact-resistance heating at current-carrying joints, field-dependent dielectric loss in the RIP core, transformer-oil temperature, air-side convection, and material properties all contribute to the steady temperature field. Previous bushing thermal and electro-thermal studies provide the basis for treating these effects with finite-element or coupled numerical models [REF_RIP_BUSHING_THERMAL; REF_CONDENSER_BUSHING_ELECTROSTATICS].

Two modeling choices are particularly important for diagnostic risk-boundary simulation. First, contact resistance should be represented as an equivalent parameter rather than as an unverified measured defect, because the actual internal connection state is usually not directly observable. Second, RIP dielectric loss should not be restricted to a spatially averaged reference field when a resolved electric-field solution is available. The field-coupled loss density, q_dielectric = omega epsilon0 epsr tan(delta)|E|^2, provides a direct route from the electrostatic solution to the thermal source term, but it also requires careful interpretation of dielectric parameters and screen-end field localization [REF_DIELECTRIC_LOSS_THEORY].

The present work therefore develops a staged finite-element numerical screening workflow for a 126 kV/1250 A RIP condenser bushing. The study does not claim physical experimental validation, field monitoring validation, or an external operating threshold. Instead, it constructs an auditable diagnostic risk-boundary model: RUN006 fixes conductor and contact heat-source normalization; RUN007-RUN008 test solid-only thermal behavior; RUN009 introduces field-coupled dielectric loss; RUN010 evaluates a 125-case operating matrix; and RUN011 checks mesh independence and parameter sensitivity. The diagnostic risk zones used later are internal screening classes and should not be interpreted as standard temperature limits, material lifetime thresholds, or operational guarantees [REF_RISK_DIAGNOSTIC_METHOD].

The main contributions are as follows. First, the work establishes a CAD-constrained, explicit-selection, two-dimensional axisymmetric finite-element model for the selected 126 kV/1250 A RIP condenser bushing. Second, it replaces an average-field dielectric-loss reference with field-coupled dielectric-loss integration while retaining a transparent DIELECTRIC_LOSS_REVIEW_REQUIRED flag. Third, it quantifies how load multiplier, oil temperature, and contact-resistance multiplier reshape global and contact-region temperature indicators across a 125-case diagnostic matrix. Fourth, it locks each numerical claim to raw result files, manuscript figures, and tables so that subsequent manuscript assembly can separate confirmed simulation evidence from reference items that still need manual verification.

# 2. Literature Review

## 2.1 Thermal and electro-thermal modeling of transformer bushings

Transformer-bushing thermal analysis has been studied using thermal-network models, two-dimensional finite-element models, and three-dimensional electromagnetic-fluid-thermal models. These studies motivate the treatment of current loading, oil temperature, ambient cooling, and local hotspot formation as coupled numerical factors rather than independent scalar corrections [REF_RIP_BUSHING_THERMAL]. For the present 126 kV/1250 A bushing, this literature supports the use of finite-element numerical simulation as a screening tool, while also reminding readers that three-dimensional flow and local terminal details remain limitations when a two-dimensional axisymmetric model is used.

## 2.2 Contact-resistance degradation and localized heating

Current-carrying connections can become localized thermal sources when the equivalent contact resistance increases. Prior contact-degradation and current-carrying-defect studies motivate the use of a contact-resistance multiplier, but they do not allow this project to claim that a measured defect was reproduced. In this manuscript, contact degradation is therefore treated as a parameterized equivalent model. This boundary is important because the RUN010 matrix evaluates thermal response to assumed contact-resistance multipliers rather than to inspected or measured physical defects [REF_RIP_BUSHING_THERMAL; REF_RISK_DIAGNOSTIC_METHOD].

## 2.3 RIP dielectric response and field-coupled dielectric loss

The dielectric response of epoxy- or resin-impregnated paper depends on permittivity, loss tangent, temperature, frequency, and aging-related material state. A resolved electrostatic field can therefore change the spatial distribution of dielectric heat generation relative to an average-field reference. The present model uses the field-coupled dielectric-loss expression in the RIP region and reports both field-based and reference-based dielectric-loss values. The dielectric_loss_review_required flag is retained because the field/reference ratio exceeds the initial review interval; this is a transparent uncertainty marker rather than a failure of the numerical run [REF_DIELECTRIC_LOSS_THEORY].

## 2.4 Condenser screens and electrostatic field representation

Condenser bushings use graded conductive screens to control electric-field distribution. Modeling these screens requires a consistent electrostatic boundary strategy: the high-voltage and grounded screens can be assigned fixed potentials, while intermediate condenser screens should not be forced to arbitrary fixed values if the intended physics is floating charge balance. The present model therefore treats S00 as high voltage, S10 and the flange as grounded, and S01-S09 as floating condenser screens in the full field-coupled stage. The physical rationale should be supported by condenser-bushing electrostatics literature, and the implementation should be checked against official COMSOL floating-potential documentation [REF_CONDENSER_BUSHING_ELECTROSTATICS; REF_COMSOL_FLOATING_POTENTIAL].

## 2.5 Numerical verification, mesh convergence, and diagnostic risk zoning

Numerical risk-boundary studies require more than a solved temperature field. They need source-normalization checks, heat-balance checks, selection-integrity checks, electric-field singularity screening, mesh convergence evidence, and sensitivity analysis. RUN011A provides the mesh-convergence evidence used in the present work, while RUN011B identifies the most influential material and boundary assumptions. External mesh-convergence and diagnostic-risk-method references are still needed to support the general verification language and risk-zoning terminology [REF_MESH_CONVERGENCE; REF_RISK_DIAGNOSTIC_METHOD].

## 2.6 Gap addressed by the present study

Existing bushing studies provide strong foundations for thermal modeling, electro-thermal coupling, dielectric response, and contact-defect diagnosis, but the manuscript-ready gap addressed here is narrower: an auditable, source-normalized, field-coupled finite-element screening workflow for a 126 kV/1250 A RIP condenser transformer bushing, with each numerical conclusion locked to raw result files and each literature-dependent statement retained as a reference placeholder until manually confirmed. This structure is intended to make the manuscript safer to assemble, not to overstate the simulation as a measured or field-confirmed operating rule.
"""
    zh = """# 1. 引言（中文内部阅读版）

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
"""
    write_text(RUN015_DOC / "introduction_literature_review_en.md", en)
    write_text(RUN015_DOC / "introduction_literature_review_zh.md", zh)


def write_reference_search_tasks(reference_rows: list[dict[str, str]]) -> None:
    task_details = {
        "[REF_BRFG_DRAWING]": (
            "Verify the BRFGL1-126/1250-4 drawing/catalog source.",
            "BRFGL1-126/1250-4 RIP bushing 126 kV 1250 A drawing, transformer bushing catalog BRFGL1",
            "A manufacturer-controlled drawing/catalog or project-authorized CAD file with model name and dimensions.",
            "Unlabeled images, copied screenshots without provenance, or dimensions not matching the selected model.",
            "The numerical object was a BRFGL1-126/1250-4 RIP dry-type condenser transformer bushing rated at 126 kV and 1250 A.",
        ),
        "[REF_IEC_60137]": (
            "Confirm IEC 60137 scope/rating language.",
            "IEC 60137 insulated bushings scope rated voltage current transformer bushings",
            "Official IEC standard text or official IEC page; use only for scope/rating background.",
            "Secondary pages that quote limits without traceable clause context.",
            "The bushing category and rating context should be linked to the appropriate IEC reference.",
        ),
        "[REF_RIP_BUSHING_THERMAL]": (
            "Find peer-reviewed RIP/bushing thermal or electro-thermal modeling support.",
            "RIP transformer bushing thermal finite element electro-thermal oil temperature load contact resistance",
            "Peer-reviewed paper on bushing thermal/FEM/electro-thermal modeling with relevant variables.",
            "Papers on unrelated cable joints or generic insulation without bushing thermal model.",
            "Current-driven conductor loss, contact heating, dielectric loss, oil temperature, and air convection contribute to the steady temperature field.",
        ),
        "[REF_DIELECTRIC_LOSS_THEORY]": (
            "Confirm dielectric-loss equation and RMS convention.",
            "dielectric loss density omega epsilon0 epsr tan delta E squared RMS field",
            "Textbook, standard, or peer-reviewed source giving the harmonic dielectric-loss expression and conventions.",
            "Uncited web notes or formulas without unit/convention explanation.",
            "The field-coupled loss density q_dielectric = omega epsilon0 epsr tan(delta)|E|^2 links the electrostatic field to the thermal source.",
        ),
        "[REF_CONDENSER_BUSHING_ELECTROSTATICS]": (
            "Support condenser screens and field grading treatment.",
            "condenser bushing electrostatic finite element floating screen field grading RIP bushing",
            "Peer-reviewed bushing electrostatics/electro-thermal paper discussing screens or grading.",
            "Generic capacitor papers not connected to condenser bushings.",
            "Condenser bushings use graded conductive screens to control electric-field distribution.",
        ),
        "[REF_COMSOL_FLOATING_POTENTIAL]": (
            "Locate official COMSOL floating-potential documentation.",
            "COMSOL electrostatics floating potential zero net charge documentation",
            "Official COMSOL documentation page/manual section for Floating Potential and zero net charge.",
            "Forum posts or unofficial tutorials unless used only as secondary implementation hints.",
            "Screens S01-S09 are treated as floating condenser screens with zero net charge in the full field-coupled model.",
        ),
        "[REF_MESH_CONVERGENCE]": (
            "Support finite-element mesh convergence verification wording.",
            "finite element mesh convergence verification relative error fine mesh reference",
            "Numerical-method textbook, verification guideline, or peer-reviewed FEM convergence reference.",
            "Claims that convergence proves physical validation.",
            "RUN011A compares coarse, medium, and fine meshes and uses the fine mesh as reference.",
        ),
        "[REF_RISK_DIAGNOSTIC_METHOD]": (
            "Support diagnostic risk zoning as screening, not standard limit.",
            "diagnostic risk zoning screening matrix thermal risk assessment transformer bushing",
            "Risk-screening or diagnostic-threshold method reference that does not imply standard operating limits.",
            "Standards or papers that would be misread as defining the project's thresholds.",
            "Diagnostic risk zones are internal screening classes, not IEC/IEEE limits or operating guarantees.",
        ),
    }
    body = [
        "# RUN015 Reference Search Tasks",
        "",
        "These tasks are for manual follow-up or a later verified online/reference-manager workflow. No bibliography entry is fabricated in RUN015.",
        "",
    ]
    for row in reference_rows:
        placeholder = row["placeholder"]
        target, keywords, accept, reject, sentence = task_details[placeholder]
        body.extend([
            f"## {placeholder}",
            "",
            f"- Search target: {target}",
            f"- Recommended keywords: `{keywords}`",
            f"- Acceptance criteria: {accept}",
            f"- Rejection criteria: {reject}",
            f"- Sentence to support: {sentence}",
            f"- RUN015 status: {row['source_status']}",
            "",
        ])
    write_text(RUN015_DOC / "reference_search_tasks.md", "\n".join(body))


def write_claim_boundary_notes() -> None:
    text = """# Manuscript Claim Boundary Notes

The following claim boundaries must be preserved during submission-oriented editing.

1. The project is a finite-element numerical simulation and diagnostic screening workflow. It is not a physical experiment.
2. The diagnostic risk zoning used in RUN010 is not an IEC/IEEE standard limit, material lifetime threshold, operating rule, or safety guarantee.
3. The contact-resistance multiplier is a parameterized equivalent model. It is not a measured defect, inspected failure geometry, or asset-specific diagnosis.
4. The DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required flag must remain visible. The field-coupled dielectric loss exceeds the average-field reference, and this difference is a review item rather than a failed run.
5. The model is two-dimensional and axisymmetric. Local 3D terminal, flange, and bolt effects are not explicitly resolved.
6. 2D axisymmetric limitation: the model is two-dimensional and axisymmetric. Local 3D terminal, flange, and bolt effects are not explicitly resolved.
7. no CFD limitation: air and oil are represented by boundary heat-transfer conditions. No CFD fluid-domain solution is included.
8. no transient limitation: the present results are steady-state. Transient overload, annual weather driving, and time-dependent thermal inertia are outside RUN010.
9. The local terminal/flange bolt geometry is not a full 3D resolved model.
10. no field/lab validation: no field-monitoring or laboratory validation has been completed yet.
11. The RUN010 risk boundary is a numerical screening result. It should not be written as an operational rule before external validation.

Any future Introduction, Abstract, Conclusion, or graphical abstract must be checked against these boundaries before use.
"""
    write_text(RUN015_DOC / "manuscript_claim_boundary_notes.md", text)


def metric_range(rows: list[dict[str, str]], column: str) -> tuple[float, float]:
    values = [fnum(row[column]) for row in rows]
    return min(values), max(values)


def counts(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        key = row[column]
        out[key] = out.get(key, 0) + 1
    return out


def approx_equal(actual: float, expected: float, tol: float = 0.0015) -> bool:
    return abs(actual - expected) <= tol


def make_lock_row(section: str, claim: str, value: str, source: Path, metric: str, callout: str,
                  citation: str, status: str, risk: str, action: str) -> dict[str, str]:
    return {
        "manuscript_section": section,
        "sentence_or_claim": claim,
        "numerical_value_if_any": value,
        "evidence_source_file": rel(source),
        "evidence_metric_or_column": metric,
        "figure_or_table_callout": callout,
        "citation_or_placeholder": citation,
        "evidence_status": status,
        "overclaim_risk": risk,
        "required_action": action,
    }


def build_text_evidence_lock(missing_inputs: list[Path]) -> list[dict[str, str]]:
    lock_rows: list[dict[str, str]] = []
    baseline_path = RUN009A / "baseline_metrics.csv"
    risk_path = RUN010 / "run010_risk_metrics.csv"
    hb_path = RUN010 / "heat_balance_by_case.csv"
    electric_path = RUN010 / "electric_field_diagnostics_by_case.csv"
    dielectric_path = RUN010 / "dielectric_loss_by_case.csv"
    cmp_path = RUN010 / "run008_vs_run010_comparison.csv"
    mesh_path = RUN011A / "mesh_convergence_summary.csv"
    sens_path = RUN011B / "sensitivity_index_summary.csv"

    if baseline_path.exists():
        baseline = read_csv(baseline_path)[0]
        checks = [
            ("4.1", "RUN009A baseline global maximum temperature is 88.589 degC.", 88.589, fnum(baseline["Tmax_global_C"]), "Tmax_global_C", "Fig. 2; Table 2", ""),
            ("4.1", "RUN009A field-coupled RIP dielectric loss is 28.049 W.", 28.049, fnum(baseline["Qdielectric_RIP_field_W"]), "Qdielectric_RIP_field_W", "Fig. 2; Table 2", "[REF_DIELECTRIC_LOSS_THEORY]"),
            ("4.1", "RUN009A field/reference dielectric-loss ratio is 11.020.", 11.020, fnum(baseline["Qdielectric_ratio_field_to_ref"]), "Qdielectric_ratio_field_to_ref", "Fig. S6; Table 2", "[REF_DIELECTRIC_LOSS_THEORY]"),
        ]
        for section, claim, expected, actual, metric, callout, citation in checks:
            status = "OK" if approx_equal(actual, expected, 0.0015) else "FAIL"
            lock_rows.append(make_lock_row(section, claim, fmt(expected), baseline_path, metric, callout, citation, status, "LOW" if status == "OK" else "HIGH", "Use exact raw value before final typesetting."))
    else:
        missing_inputs.append(baseline_path)

    risk = read_csv(risk_path)
    tmin, tmax = metric_range(risk, "Tmax_global_C")
    tcontact_max = max(fnum(row["Tmax_contact_C"]) for row in risk)
    risk_counts = counts(risk, "risk_zone")
    contact_counts = counts(risk, "contact_risk_zone")
    lock_rows.extend([
        make_lock_row("4.2", "RUN010 Tmax_global_C range is 67.397-134.974 degC.", f"{fmt(tmin)}-{fmt(tmax)} degC", risk_path, "min/max Tmax_global_C", "Fig. 3; Table 2", "", "OK" if approx_equal(tmin, 67.397, 0.0015) and approx_equal(tmax, 134.974, 0.0015) else "FAIL", "LOW", "Keep as matrix-specific RUN010 result."),
        make_lock_row("4.2", "RUN010 Tmax_contact_C maximum is 129.925 degC.", f"{fmt(tcontact_max)} degC", risk_path, "max Tmax_contact_C", "Fig. 4; Table 2", "", "OK" if approx_equal(tcontact_max, 129.925, 0.0015) else "FAIL", "LOW", "Keep as contact diagnostic metric."),
        make_lock_row("4.3", "RUN010 global risk-zone counts are safe 119, attention 4, warning 2, thermal-risk 0.", f"safe {risk_counts.get('safe', 0)}, attention {risk_counts.get('attention', 0)}, warning {risk_counts.get('warning', 0)}, thermal-risk {risk_counts.get('thermal_risk', 0)}", risk_path, "risk_zone counts", "Fig. 3; Fig. 5; Table 4", "[REF_RISK_DIAGNOSTIC_METHOD]", "OK" if [risk_counts.get(k, 0) for k in ["safe", "attention", "warning", "thermal_risk"]] == [119, 4, 2, 0] else "FAIL", "MEDIUM_HANDLED", "Must state diagnostic zoning only, not a standard limit."),
        make_lock_row("4.3", "RUN010 contact risk-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0.", f"contact_safe {contact_counts.get('contact_safe', 0)}, contact_attention {contact_counts.get('contact_attention', 0)}, contact_warning {contact_counts.get('contact_warning', 0)}, contact-risk {contact_counts.get('contact_risk', 0)}", risk_path, "contact_risk_zone counts", "Fig. 4; Table 2", "[REF_RISK_DIAGNOSTIC_METHOD]", "OK" if [contact_counts.get(k, 0) for k in ["contact_safe", "contact_attention", "contact_warning", "contact_risk"]] == [115, 6, 4, 0] else "FAIL", "MEDIUM_HANDLED", "Must state diagnostic contact zoning only."),
    ])

    if hb_path.exists():
        hb = read_csv(hb_path)
        max_residual = max(abs(fnum(row["residual_percent_Qgenerated"])) for row in hb)
        lock_rows.append(make_lock_row("3.5", "RUN010 heat balance max residual is 2.678%.", f"{fmt(max_residual)}%", hb_path, "max abs residual_percent_Qgenerated", "Table 3; Fig. S4", "", "OK" if approx_equal(max_residual, 2.678, 0.0015) else "FAIL", "LOW", "Use as numerical audit evidence."))
    else:
        missing_inputs.append(hb_path)

    electric = read_csv(electric_path)
    singular = count_true(electric, "field_singularity_flag")
    lock_rows.append(make_lock_row("3.5", "RUN010 field_singularity_flag is 0/125.", f"{singular}/125", electric_path, "field_singularity_flag true count", "Fig. S5; Table 3", "[REF_CONDENSER_BUSHING_ELECTROSTATICS]", "OK" if singular == 0 and len(electric) == 125 else "FAIL", "LOW", "Do not use as proof of physical validation."))

    dielectric = read_csv(dielectric_path)
    review = count_true(dielectric, "dielectric_loss_review_required")
    lock_rows.append(make_lock_row("3.5; 4.4", "RUN010 dielectric_loss_review_required is 125/125.", f"{review}/125", dielectric_path, "dielectric_loss_review_required true count", "Fig. S6; Table 3", "[REF_DIELECTRIC_LOSS_THEORY]", "OK" if review == 125 and len(dielectric) == 125 else "FAIL", "MEDIUM_HANDLED", "Flag must remain visible and explained."))

    if cmp_path.exists():
        cmp_rows = read_csv(cmp_path)
        mean_delta = sum(fnum(row["delta_Tmax_global_C"]) for row in cmp_rows) / len(cmp_rows)
        max_delta = max(fnum(row["delta_Tmax_global_C"]) for row in cmp_rows)
        changed = count_true(cmp_rows, "risk_zone_changed")
        status = "OK" if approx_equal(mean_delta, 0.617, 0.0015) and approx_equal(max_delta, 2.816, 0.0015) and changed == 2 else "FAIL"
        lock_rows.append(make_lock_row("4.4", "RUN008-vs-RUN010 mean delta_Tmax is 0.617 degC, max is 2.816 degC, and changed risk zones are 2/125.", f"mean {fmt(mean_delta)} degC; max {fmt(max_delta)} degC; changed {changed}/125", cmp_path, "delta_Tmax_global_C mean/max and risk_zone_changed count", "Fig. 7; Table 2", "[REF_DIELECTRIC_LOSS_THEORY]", status, "LOW" if status == "OK" else "HIGH", "Use only to compare approximate reference with field-coupled model."))
    else:
        missing_inputs.append(cmp_path)

    mesh = read_csv(mesh_path)
    medium = [row for row in mesh if row["mesh_level"] == "medium"]
    max_t = max(fnum(row["err_Tmax_global_pct"]) for row in medium)
    max_e = max(fnum(row["err_E95_RIP_pct"]) for row in medium)
    max_q = max(fnum(row["err_Qdielectric_pct"]) for row in medium)
    lock_rows.extend([
        make_lock_row("3.5; 4.6", "RUN011A medium-vs-fine max Tmax error is 0.355%.", f"{fmt(max_t)}%", mesh_path, "max err_Tmax_global_pct where mesh_level=medium", "Fig. 8; Table 5", "[REF_MESH_CONVERGENCE]", "OK" if approx_equal(max_t, 0.355, 0.0015) else "FAIL", "LOW", "Internal convergence evidence; external reference still needed."),
        make_lock_row("3.5; 4.6", "RUN011A medium-vs-fine max E95 error is 0.002%.", f"{fmt(max_e)}%", mesh_path, "max err_E95_RIP_pct where mesh_level=medium", "Fig. 8; Table 5", "[REF_MESH_CONVERGENCE]", "OK" if approx_equal(max_e, 0.002, 0.0015) else "FAIL", "LOW", "Internal convergence evidence; external reference still needed."),
        make_lock_row("3.5; 4.6", "RUN011A medium-vs-fine max Qdielectric error is 0.002%.", f"{fmt(max_q)}%", mesh_path, "max err_Qdielectric_pct where mesh_level=medium", "Fig. 8; Table 5", "[REF_MESH_CONVERGENCE]", "OK" if approx_equal(max_q, 0.002, 0.0015) else "FAIL", "LOW", "Internal convergence evidence; external reference still needed."),
    ])

    sens = read_csv(sens_path)
    nonbase = [row for row in sens if row["parameter_value"] != row["baseline_value"]]
    scores: dict[str, float] = {}
    for row in nonbase:
        vals = []
        for col in ["S_Tmax_global", "S_Tmax_contact", "S_Qdielectric"]:
            try:
                vals.append(abs(fnum(row[col])))
            except Exception:
                pass
        if vals:
            scores[row["parameter_name"]] = max(scores.get(row["parameter_name"], 0.0), max(vals))
    ranking = " > ".join(key for key, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True))
    expected_ranking = "tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil"
    lock_rows.append(make_lock_row("3.5; 4.6", "RUN011B sensitivity ranking is tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil.", ranking, sens_path, "ranked max absolute sensitivity over S_Tmax_global/S_Tmax_contact/S_Qdielectric", "Fig. 9; Table 6", "[REF_RIP_BUSHING_THERMAL]", "OK" if ranking == expected_ranking else "FAIL", "LOW", "Internal OFAT ranking; explain parameter assumptions."))

    return lock_rows


def quality_gate(reference_rows: list[dict[str, str]], lock_rows: list[dict[str, str]],
                 missing_inputs: list[Path]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    required_outputs = [
        RUN015_DOC / "introduction_literature_review_en.md",
        RUN015_DOC / "introduction_literature_review_zh.md",
        RUN015_TAB / "reference_resolution_matrix.csv",
        RUN015_DOC / "reference_search_tasks.md",
        RUN015_TAB / "text_evidence_lock_table.csv",
        RUN015_DOC / "manuscript_claim_boundary_notes.md",
    ]
    for path in required_outputs:
        if not path.exists() or path.stat().st_size == 0:
            problems.append(f"missing_or_empty_output:{rel(path)}")

    found_placeholders = {row["placeholder"] for row in reference_rows}
    if set(PLACEHOLDERS) - found_placeholders:
        problems.append("reference_resolution_missing_placeholders:" + ",".join(sorted(set(PLACEHOLDERS) - found_placeholders)))

    required_claim_fragments = [
        "88.589",
        "28.049",
        "11.020",
        "67.397-134.974",
        "129.925",
        "safe 119",
        "contact_safe 115",
        "2.678",
        "0/125",
        "125/125",
        "0.617",
        "0.355",
        "max E95",
        "max Qdielectric",
        "tan_delta_multiplier > epsr_RIP",
    ]
    lock_text = "\n".join(row["sentence_or_claim"] + " " + row["numerical_value_if_any"] for row in lock_rows)
    for fragment in required_claim_fragments:
        if fragment not in lock_text:
            problems.append(f"text_evidence_lock_missing:{fragment}")

    if any(row["evidence_status"] == "FAIL" for row in lock_rows):
        problems.append("text_evidence_lock_has_FAIL")

    boundary = read_text(RUN015_DOC / "manuscript_claim_boundary_notes.md") if (RUN015_DOC / "manuscript_claim_boundary_notes.md").exists() else ""
    for phrase in ["finite-element numerical simulation", "diagnostic risk zoning", "contact-resistance multiplier", "DIELECTRIC_LOSS_REVIEW_REQUIRED", "2D axisymmetric", "no CFD", "no transient", "no field/lab validation"]:
        if phrase not in boundary:
            problems.append(f"boundary_note_missing:{phrase}")

    intro = read_text(RUN015_DOC / "introduction_literature_review_en.md") if (RUN015_DOC / "introduction_literature_review_en.md").exists() else ""
    forbidden = [
        "experimentally validated",
        "field-validated",
        "validated by field monitoring",
        "IEC/IEEE temperature limit",
        "standard operating limit",
    ]
    for phrase in forbidden:
        if phrase in intro:
            problems.append(f"forbidden_intro_phrase:{phrase}")

    if "DIELECTRIC_LOSS_REVIEW_REQUIRED" not in intro and "dielectric_loss_review_required" not in intro:
        problems.append("intro_missing_dielectric_review_flag")

    # Missing inputs are recorded but do not automatically fail if no evidence lock row depends on
    # an unavailable value. If a required evidence file is missing, its dependent rows would be absent
    # or NEEDS_MANUAL_CONFIRMATION.
    return len(problems) == 0, problems


def write_report(missing_inputs: list[Path], reference_rows: list[dict[str, str]],
                 lock_rows: list[dict[str, str]], quality_ok: bool, problems: list[str]) -> None:
    files = [
        RUN015_DOC / "introduction_literature_review_en.md",
        RUN015_DOC / "introduction_literature_review_zh.md",
        RUN015_TAB / "reference_resolution_matrix.csv",
        RUN015_DOC / "reference_search_tasks.md",
        RUN015_TAB / "text_evidence_lock_table.csv",
        RUN015_DOC / "manuscript_claim_boundary_notes.md",
        RUN015_DOC / "run015_reference_intro_literature_report.md",
    ]
    status_counts: dict[str, int] = {}
    for row in reference_rows:
        status_counts[row["source_status"]] = status_counts.get(row["source_status"], 0) + 1
    lock_status_counts: dict[str, int] = {}
    for row in lock_rows:
        lock_status_counts[row["evidence_status"]] = lock_status_counts.get(row["evidence_status"], 0) + 1
    high_risk = [row for row in lock_rows if row["overclaim_risk"] == "HIGH"]

    body = [
        "# RUN015 Reference, Introduction, Literature, and Evidence Lock Report",
        "",
        "## Task Objective",
        "",
        "RUN015 resolves the RUN014 reference placeholders as far as possible from local traceability and literature files, drafts Section 1 Introduction and Section 2 Literature Review, and locks manuscript claims to raw data evidence, figures, tables, and citation placeholders. It does not run COMSOL, add simulations, or modify RUN006-RUN014 source outputs.",
        "",
        "## Inputs Checked",
        "",
        "Required RUN014 inputs:",
    ]
    for path in REQUIRED_RUN014:
        body.append(f"- {rel(path)}: {'OK' if path.exists() else 'MISSING'}")
    body.append("")
    body.append("Required evidence inputs:")
    for path in REQUIRED_EVIDENCE:
        body.append(f"- {rel(path)}: {'OK' if path.exists() else 'MISSING'}")
    body.append("")
    body.append("Additional evidence files used for text lock:")
    for path in OPTIONAL_EVIDENCE_FOR_LOCK:
        body.append(f"- {rel(path)}: {'OK' if path.exists() else 'MISSING'}")

    body.extend([
        "",
        "## Files Generated",
        "",
    ])
    for path in files:
        body.append(f"- {rel(path)}")

    body.extend([
        "",
        "## Missing Inputs",
        "",
    ])
    if missing_inputs:
        body.append("| missing_input | affected_content | status |")
        body.append("|---|---|---|")
        for path in missing_inputs:
            body.append(f"| {rel(path)} | dependent claim/reference content | NEEDS_MANUAL_CONFIRMATION |")
    else:
        body.append("No required input was missing. Reference placeholders may still require manual confirmation because some external sources are not present locally.")

    body.extend([
        "",
        "## Reference Placeholder Status",
        "",
        ", ".join(f"{key}: {value}" for key, value in sorted(status_counts.items())),
        "",
        "Resolved or partially resolved entries are based on local files or existing traceability records only. UNRESOLVED entries are intentionally left for manual reference verification; no DOI, author/year, or standard clause was fabricated.",
        "",
        "## Introduction/Literature Review Status",
        "",
        "Section 1 and Section 2 drafts were generated with placeholders and explicit claim boundaries. The draft states finite-element numerical screening, avoids physical/field validation claims, avoids standard-limit claims, and retains DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required language.",
        "",
        "## Text-Evidence Lock Status",
        "",
        ", ".join(f"{key}: {value}" for key, value in sorted(lock_status_counts.items())),
        "",
        "## Overclaim Risk Status",
        "",
        f"High-risk evidence-lock rows: {len(high_risk)}.",
    ])
    if high_risk:
        for row in high_risk:
            body.append(f"- {row['sentence_or_claim']} -> {row['required_action']}")
    else:
        body.append("No HIGH overclaim row remains in the text-evidence lock. Medium-risk interpretation claims are handled by claim-boundary notes.")
    body.extend([
        "",
        "## Quality Gate Problems",
        "",
    ])
    if problems:
        for problem in problems:
            body.append(f"- {problem}")
    else:
        body.append("None.")
    body.extend([
        "",
        "## RUN016 Readiness",
        "",
        "The package can enter full manuscript assembly only as a placeholder-aware draft: bibliography finalization and manual verification of unresolved reference placeholders remain required.",
        "",
        f"Can proceed to FULL_MANUSCRIPT_ASSEMBLY_RUN016: {'YES' if quality_ok else 'NO'}",
    ])
    write_text(RUN015_DOC / "run015_reference_intro_literature_report.md", "\n".join(body))


def main() -> None:
    ensure_dirs()
    missing_inputs = missing(REQUIRED_RUN014 + REQUIRED_EVIDENCE)
    # Optional inputs are needed for a stronger lock; record missing ones but continue.
    missing_optional = missing(OPTIONAL_EVIDENCE_FOR_LOCK)

    # Read all available required files to force early failure on corrupted content.
    for path in existing(REQUIRED_RUN014):
        if path.suffix.lower() == ".csv":
            read_csv(path)
        else:
            read_text(path)
    for path in existing(REQUIRED_EVIDENCE):
        read_csv(path)

    write_introduction_literature()
    reference_rows = build_reference_resolution_rows()
    write_csv(RUN015_TAB / "reference_resolution_matrix.csv", [
        "placeholder",
        "section",
        "claim_or_context",
        "source_type_needed",
        "candidate_reference_key",
        "candidate_reference_title",
        "candidate_reference_type",
        "source_status",
        "confidence",
        "verified_by",
        "notes",
    ], reference_rows)
    write_reference_search_tasks(reference_rows)
    write_claim_boundary_notes()
    lock_rows = build_text_evidence_lock(missing_inputs)
    write_csv(RUN015_TAB / "text_evidence_lock_table.csv", [
        "manuscript_section",
        "sentence_or_claim",
        "numerical_value_if_any",
        "evidence_source_file",
        "evidence_metric_or_column",
        "figure_or_table_callout",
        "citation_or_placeholder",
        "evidence_status",
        "overclaim_risk",
        "required_action",
    ], lock_rows)

    quality_ok, problems = quality_gate(reference_rows, lock_rows, missing_inputs + missing_optional)
    write_report(missing_inputs + missing_optional, reference_rows, lock_rows, quality_ok, problems)
    print("RUN015 generated files:")
    for path in [
        RUN015_DOC / "introduction_literature_review_en.md",
        RUN015_DOC / "introduction_literature_review_zh.md",
        RUN015_TAB / "reference_resolution_matrix.csv",
        RUN015_DOC / "reference_search_tasks.md",
        RUN015_TAB / "text_evidence_lock_table.csv",
        RUN015_DOC / "manuscript_claim_boundary_notes.md",
        RUN015_DOC / "run015_reference_intro_literature_report.md",
    ]:
        print(f"- {rel(path)}")
    print(f"RUN015 quality gate status: {'PASS' if quality_ok else 'NEEDS_REVISION'}")
    if problems:
        print("Problems:")
        for problem in problems:
            print(f"- {problem}")
    if not quality_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
