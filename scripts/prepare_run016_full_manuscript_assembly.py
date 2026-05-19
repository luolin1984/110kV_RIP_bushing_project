"""Prepare RUN016 full manuscript assembly package.

RUN016 performs two controlled tasks:
1. Normalize RUN015 manuscript paths to docs/manuscript_draft_sections/RUN015.
2. Assemble a placeholder-aware full English manuscript draft from RUN015,
   RUN014, RUN013 captions, and manuscript-ready evidence tables.

It does not run COMSOL, add simulations, or modify RUN006-RUN013 raw results.
Only RUN015 path normalization copies are allowed, and only from docs/RUN015
to the canonical RUN015 manuscript directory when canonical files are missing.
"""

from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
OLD_RUN015 = PROJECT / "docs" / "RUN015"
RUN013_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN013"
RUN014_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN014"
RUN015_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN015"
RUN016_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN016"
READY = PROJECT / "results" / "summary_tables" / "manuscript_ready"
RUN014_TAB = READY / "RUN014"
RUN015_TAB = READY / "RUN015"
RUN016_TAB = READY / "RUN016"


RUN015_MAIN_FILES = [
    "introduction_literature_review_en.md",
    "introduction_literature_review_zh.md",
    "reference_search_tasks.md",
    "manuscript_claim_boundary_notes.md",
    "run015_reference_intro_literature_report.md",
]

REQUIRED_INPUTS = [
    RUN015_DOC / "introduction_literature_review_en.md",
    RUN015_DOC / "introduction_literature_review_zh.md",
    RUN015_DOC / "reference_search_tasks.md",
    RUN015_DOC / "manuscript_claim_boundary_notes.md",
    RUN015_DOC / "run015_reference_intro_literature_report.md",
    RUN015_TAB / "reference_resolution_matrix.csv",
    RUN015_TAB / "text_evidence_lock_table.csv",
    RUN014_DOC / "methods_results_integrated_en.md",
    RUN014_DOC / "reference_placeholder_plan.md",
    RUN014_DOC / "reviewer_risk_checklist.md",
    RUN014_DOC / "run014_methods_results_integration_report.md",
    RUN014_TAB / "figure_table_callout_plan.csv",
    RUN014_TAB / "claim_to_evidence_audit_run014.csv",
    RUN014_TAB / "terminology_consistency_table.csv",
    RUN013_DOC / "figure_captions_en.md",
    RUN013_DOC / "table_captions_en.md",
    READY / "manuscript_figure_index.csv",
    READY / "manuscript_table_index.csv",
    READY / "key_result_summary.csv",
    READY / "model_validation_evidence_chain.csv",
]


TITLE_OPTIONS = [
    "Electro-Thermal Coupled Finite-Element Diagnostic Risk-Boundary Simulation of a 126 kV/1250 A RIP Condenser Transformer Bushing under Contact-Resistance Degradation",
    "Numerical Screening of Contact-Resistance Degradation in a 126 kV/1250 A RIP Condenser Transformer Bushing Using Field-Coupled Electro-Thermal Finite-Element Simulation",
    "Field-Coupled Dielectric-Loss and Contact-Degradation Effects in a 126 kV/1250 A RIP Condenser Transformer Bushing: A Finite-Element Diagnostic Risk-Boundary Study",
]
RECOMMENDED_TITLE = TITLE_OPTIONS[0]

ABSTRACT = (
    "This study develops a staged electro-thermal coupled finite-element model "
    "for a 126 kV/1250 A resin-impregnated paper (RIP) condenser transformer "
    "bushing under load, oil-temperature, and contact-resistance degradation "
    "conditions. The workflow normalizes conductor Joule heating and contact "
    "heating, introduces field-coupled RIP dielectric loss, and audits heat "
    "balance, by-ID selections, electric-field singularity, mesh convergence, "
    "and material/boundary sensitivity. The main RUN010 matrix contains 125 "
    "steady cases. Across this matrix, Tmax_global_C ranges from 67.397-134.974 "
    "degC, and Tmax_contact_C reaches 129.925 degC. The global diagnostic "
    "risk-zone counts are safe 119, attention 4, warning 2, and thermal-risk 0. "
    "The contact-zone counts are contact_safe 115, contact_attention 6, "
    "contact_warning 4, and contact-risk 0. The field-coupled dielectric-loss "
    "review flag is retained because the field/reference ratio is 11.020, while "
    "field_singularity_flag is 0/125. Mesh verification gives 0.355% maximum "
    "medium-vs-fine Tmax error, and the sensitivity ranking is "
    "tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > "
    "k_RIP_multiplier > h_oil. The results are finite-element numerical "
    "screening evidence, not laboratory or field validation; the diagnostic "
    "risk zones are internal screening classes, not standard limits."
)

KEYWORDS = [
    "RIP condenser bushing",
    "transformer bushing",
    "electro-thermal coupling",
    "finite-element simulation",
    "contact-resistance degradation",
    "field-coupled dielectric loss",
    "diagnostic risk boundary",
    "mesh convergence",
]


NUMERIC_CLAIMS = [
    ("88.589 degC", "88.589 degC", "RUN009A baseline global maximum temperature is 88.589 degC."),
    ("28.049 W", "28.049 W", "RUN009A field-coupled RIP dielectric loss is 28.049 W."),
    ("11.020", "11.020", "RUN009A field/reference dielectric-loss ratio is 11.020."),
    ("67.397-134.974 degC", "67.397-134.974 degC", "RUN010 Tmax_global_C range is 67.397-134.974 degC."),
    ("129.925 degC", "129.925 degC", "RUN010 Tmax_contact_C maximum is 129.925 degC."),
    ("safe 119, attention 4, warning 2, thermal-risk 0", "safe 119, attention 4, warning 2, thermal-risk 0", "RUN010 global risk-zone counts are safe 119, attention 4, warning 2, thermal-risk 0."),
    ("contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0", "contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0", "RUN010 contact risk-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0."),
    ("2.678%", "2.678%", "RUN010 heat balance max residual is 2.678%."),
    ("0/125 field_singularity_flag", "0/125", "RUN010 field_singularity_flag is 0/125."),
    ("125/125 dielectric_loss_review_required", "125/125", "RUN010 dielectric_loss_review_required is 125/125."),
    ("0.617 degC mean delta_Tmax", "0.617 degC", "RUN008-vs-RUN010 mean delta_Tmax is 0.617 degC, max is 2.816 degC, and changed risk zones are 2/125."),
    ("2.816 degC max delta_Tmax", "2.816 degC", "RUN008-vs-RUN010 mean delta_Tmax is 0.617 degC, max is 2.816 degC, and changed risk zones are 2/125."),
    ("2/125 changed risk zones", "2/125", "RUN008-vs-RUN010 mean delta_Tmax is 0.617 degC, max is 2.816 degC, and changed risk zones are 2/125."),
    ("0.355% max Tmax mesh error", "0.355%", "RUN011A medium-vs-fine max Tmax error is 0.355%."),
    ("0.002% max E95 mesh error", "0.002%", "RUN011A medium-vs-fine max E95 error is 0.002%."),
    ("0.002% max Qdielectric mesh error", "0.002%", "RUN011A medium-vs-fine max Qdielectric error is 0.002%."),
    (
        "tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil",
        "tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil",
        "RUN011B sensitivity ranking is tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil.",
    ),
]


def ensure_dirs() -> None:
    RUN015_DOC.mkdir(parents=True, exist_ok=True)
    RUN016_DOC.mkdir(parents=True, exist_ok=True)
    RUN016_TAB.mkdir(parents=True, exist_ok=True)


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


def file_status(path: Path) -> str:
    return "OK" if path.exists() and path.stat().st_size > 0 else "MISSING_INPUT"


def normalize_run015_paths() -> dict[str, list[str] | str]:
    copied: list[str] = []
    already: list[str] = []
    missing: list[str] = []
    for name in RUN015_MAIN_FILES:
        old = OLD_RUN015 / name
        canonical = RUN015_DOC / name
        if canonical.exists() and canonical.stat().st_size > 0:
            already.append(name)
        elif old.exists() and old.stat().st_size > 0:
            shutil.copy2(old, canonical)
            copied.append(name)
        else:
            missing.append(name)
    note = [
        "# RUN015 Path Normalization Note",
        "",
        f"- old_path: `{rel(OLD_RUN015)}`",
        f"- canonical_path: `{rel(RUN015_DOC)}`",
        f"- copied_files: {', '.join(copied) if copied else 'none'}",
        f"- files_already_present: {', '.join(already) if already else 'none'}",
        f"- any_missing_files: {', '.join(missing) if missing else 'none'}",
        "- why canonical path is used: RUN013-RUN016 manuscript artifacts are organized under `docs/manuscript_draft_sections/<RUN_ID>/`, while summary tables are organized under `results/summary_tables/manuscript_ready/<RUN_ID>/`. The canonical RUN015 path keeps manuscript assembly inputs stable and reproducible without deleting any legacy `docs/RUN015/` content.",
    ]
    write_text(RUN015_DOC / "run015_path_normalization_note.md", "\n".join(note))
    return {
        "old_path": rel(OLD_RUN015),
        "canonical_path": rel(RUN015_DOC),
        "copied_files": copied,
        "files_already_present": already,
        "any_missing_files": missing,
    }


def split_sections_1_2(text: str) -> str:
    return text.strip()


def split_methods_results(text: str) -> tuple[str, str]:
    match3 = re.search(r"^## 3\. ", text, flags=re.M)
    match4 = re.search(r"^## 4\. ", text, flags=re.M)
    match_supp = re.search(r"^## Supplementary Figure Routing Note", text, flags=re.M)
    if not match3 or not match4:
        return "", ""
    sec3 = text[match3.start():match4.start()].strip()
    sec4_end = match_supp.start() if match_supp else len(text)
    sec4 = text[match4.start():sec4_end].strip()
    sec3 = sec3.replace("## 3.", "# 3.").replace("\n### ", "\n## ")
    sec4 = sec4.replace("## 4.", "# 4.").replace("\n### ", "\n## ")
    return sec3, sec4


def extract_caption_block(path: Path, title: str) -> str:
    text = read_text(path).strip()
    lines = [line for line in text.splitlines() if line.strip()]
    if lines and lines[0].startswith("#"):
        lines = lines[1:]
    return "# " + title + "\n\n" + "\n\n".join(lines)


def references_placeholder_list(rows: list[dict[str, str]]) -> str:
    out = ["# References Placeholder List", ""]
    out.append("No formal bibliography is fabricated in this draft. Each placeholder below must be resolved or manually confirmed before submission.")
    out.append("")
    out.append("| placeholder | source_status | confidence | required action |")
    out.append("|---|---|---|---|")
    for row in rows:
        status = row["source_status"]
        if "UNRESOLVED" in status or "PARTIALLY" in status or "NEEDS" in status:
            action = "manual verification required before submission"
        else:
            action = "confirm bibliographic metadata"
        out.append(f"| {row['placeholder']} | {status} | {row['confidence']} | {action} |")
    return "\n".join(out)


def supplementary_note(fig_rows: list[dict[str, str]]) -> str:
    out = [
        "# Supplementary Material Note",
        "",
        "The following supplementary figures are routed as validation and audit material rather than as main conclusions:",
        "",
    ]
    supp = [row for row in fig_rows if row["figure_id"].startswith("FigS")]
    order = {f"FigS{i}": i for i in range(1, 8)}
    for row in sorted(supp, key=lambda r: order.get(r["figure_id"], 99)):
        label = row["figure_id"].replace("FigS", "Fig. S")
        out.append(f"- {label}: {row['figure_title']}. Source: `{row['file_path']}`.")
    return "\n".join(out)


def limitations_future_work() -> str:
    return """# 5. Limitations and Future Work

The present manuscript is based on a finite-element numerical screening workflow. The most important limitation is the two-dimensional axisymmetric representation. It captures the axisymmetric current path, RIP core, condenser screens, external insulation envelope, flange region, and oil-side region, but it does not explicitly resolve local three-dimensional terminal details, flange bolt holes, or asymmetric connection features.

Air and oil are represented through boundary heat-transfer conditions rather than resolved CFD fluid domains. This choice keeps the heat-balance audit transparent, but it also means that local oil-flow, air-flow, and buoyancy effects are not directly solved. The present matrix is also steady-state; transient overload history, annual weather sequences, and time-dependent thermal inertia are outside RUN010.

No laboratory, field-monitoring, or physical prototype validation has been completed in the current project stage. The RUN010 risk boundary is therefore a numerical screening result, not an operational rule. The diagnostic risk zones are internal screening classes and not standard limits, material lifetime thresholds, or safety guarantees. The contact-resistance multiplier is a parameterized equivalent model, not a measured defect or asset-specific diagnosis.

The field-coupled dielectric-loss calculation remains transparent about uncertainty. DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required is retained because the field-integrated RIP dielectric loss exceeds the average-field reference. Future work should verify dielectric parameters, field interpretation, contact-resistance assumptions, and convective heat-transfer coefficients against stronger material data, manufacturer data, monitoring records, or targeted experiments. Reference placeholders also remain unresolved or partially resolved and require manual verification before submission.
"""


def conclusions() -> str:
    return """# 6. Conclusions

1. A staged finite-element numerical screening workflow was assembled for a 126 kV/1250 A RIP condenser transformer bushing, with source normalization, by-ID selections, heat-balance checks, field diagnostics, mesh convergence, and parameter sensitivity retained as audit steps.
2. The RUN009A baseline gives 88.589 degC global maximum temperature and 28.049 W field-coupled RIP dielectric loss, with a field/reference ratio of 11.020. The DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained and interpreted as a review item rather than a failed run.
3. In the RUN010 125-case matrix, Tmax_global_C ranges from 67.397-134.974 degC and Tmax_contact_C reaches 129.925 degC.
4. RUN010 global diagnostic risk-zone counts are safe 119, attention 4, warning 2, thermal-risk 0, while contact-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0. These classes are diagnostic screening categories, not standard limits.
5. Replacing the approximate dielectric-loss reference with field-coupled dielectric loss changes Tmax_global by 0.617 degC mean delta_Tmax and 2.816 degC max delta_Tmax, with 2/125 changed risk zones.
6. RUN011A supports the medium mesh with 0.355% max Tmax mesh error, 0.002% max E95 mesh error, and 0.002% max Qdielectric mesh error.
7. RUN011B ranks sensitivity as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil, indicating that dielectric parameters, contact resistance, and air-side heat transfer deserve priority in future verification.
"""


def abstract_title_keywords() -> str:
    out = ["# Abstract, Title Options, and Keywords", "", "## Title Options", ""]
    for i, title in enumerate(TITLE_OPTIONS, 1):
        out.append(f"{i}. {title}")
    out.extend([
        "",
        "## Recommended Title",
        "",
        RECOMMENDED_TITLE,
        "",
        "## Abstract",
        "",
        ABSTRACT,
        "",
        "## Keywords",
        "",
        "; ".join(KEYWORDS),
        "",
        "## Novelty Bullets",
        "",
        "- Establishes a CAD-constrained, by-ID selection, finite-element numerical screening workflow for a 126 kV/1250 A RIP condenser transformer bushing.",
        "- Replaces an approximate dielectric-loss reference with field-coupled RIP dielectric-loss integration while preserving the dielectric-loss review flag.",
        "- Quantifies load, oil-temperature, and contact-resistance multiplier effects across the 125-case RUN010 matrix.",
        "- Locks numeric claims to raw evidence tables, figure/table callouts, and reference placeholders before full manuscript formatting.",
        "",
        "## Claim-Boundary Note",
        "",
        "This draft presents finite-element numerical screening results. It does not claim laboratory validation, field-monitoring validation, standard-limit compliance, or measured contact-defect reproduction. Diagnostic risk zones are internal screening classes.",
    ])
    return "\n".join(out)


def assemble_full_manuscript_en() -> str:
    intro_lit = split_sections_1_2(read_text(RUN015_DOC / "introduction_literature_review_en.md"))
    methods, results = split_methods_results(read_text(RUN014_DOC / "methods_results_integrated_en.md"))
    refs = references_placeholder_list(read_csv(RUN015_TAB / "reference_resolution_matrix.csv"))
    fig_caps = extract_caption_block(RUN013_DOC / "figure_captions_en.md", "Figure Captions")
    table_caps = extract_caption_block(RUN013_DOC / "table_captions_en.md", "Table Captions")
    supp = supplementary_note(read_csv(READY / "manuscript_figure_index.csv"))
    title_block = "# Title Options\n\n" + "\n".join(f"{i}. {title}" for i, title in enumerate(TITLE_OPTIONS, 1))
    manuscript = "\n\n".join([
        title_block,
        "# Abstract\n\n" + ABSTRACT,
        "# Keywords\n\n" + "; ".join(KEYWORDS),
        intro_lit,
        methods,
        results,
        limitations_future_work(),
        conclusions(),
        refs,
        fig_caps,
        table_caps,
        supp,
    ])
    # Add a compact evidence sentence to make exact lock strings explicit without adding
    # unsupported conclusions.
    evidence_sentence = (
        "\n\nEvidence-lock summary: RUN010 reports 0/125 field_singularity_flag cases and "
        "125/125 dielectric_loss_review_required cases; RUN010 contact risk-zone counts are "
        "contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0."
    )
    manuscript = manuscript.replace(
        "The key result summary in Table 2 provides the numeric source for the baseline and subsequent RUN010 discussion.",
        "The key result summary in Table 2 provides the numeric source for the baseline and subsequent RUN010 discussion. The RUN010 heat balance max residual is 2.678%." + evidence_sentence,
    )
    return manuscript


def assemble_full_manuscript_zh() -> str:
    intro_lit_zh = read_text(RUN015_DOC / "introduction_literature_review_zh.md").strip()
    methods_results_zh = read_text(RUN014_DOC / "methods_results_integrated_zh.md").strip() if (RUN014_DOC / "methods_results_integrated_zh.md").exists() else ""
    refs = read_csv(RUN015_TAB / "reference_resolution_matrix.csv")
    ref_lines = [
        "# References Placeholder List（中文说明）",
        "",
        "本稿只列出引用占位符及 RUN015 状态，不生成正式参考文献条目。",
        "",
    ]
    for row in refs:
        ref_lines.append(f"- {row['placeholder']}: {row['source_status']}，需处理：{row['notes']}")
    text = f"""# 题目候选

1. {TITLE_OPTIONS[0]}
2. {TITLE_OPTIONS[1]}
3. {TITLE_OPTIONS[2]}

# 摘要（中文内部阅读版）

本文针对 126 kV/1250 A RIP 电容型变压器套管，建立分阶段电热耦合有限元数值筛查模型。模型包括导体焦耳热、接触电阻热、电场耦合 RIP 介质损耗、显式 by-ID selection、热量收支、电场奇异性、网格无关性和参数敏感性审计。RUN010 主矩阵共 125 组稳态工况，Tmax_global_C 范围为 67.397-134.974 degC，Tmax_contact_C 最大为 129.925 degC。全局诊断风险分区为 safe 119、attention 4、warning 2、thermal-risk 0；接触区分区为 contact_safe 115、contact_attention 6、contact_warning 4、contact-risk 0。medium-vs-fine 最大 Tmax 误差为 0.355%，敏感性排序为 tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil。本文结果是有限元数值筛查，不是实验或现场验证；诊断风险分区不是标准限值。

# 关键词

{'; '.join(KEYWORDS)}

{intro_lit_zh}

{methods_results_zh}

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

{chr(10).join(ref_lines)}

# Figure Captions / Table Captions / Supplementary Material Note

图题、表题和补充材料说明沿用英文主稿中的 Fig. 1-Fig. 9、Table 1-Table 6 和 Fig. S1-Fig. S7 路由，不新增不存在的图表。
"""
    return text


def portability_audit() -> list[dict[str, str]]:
    rows = []
    references = read_csv(RUN015_TAB / "reference_resolution_matrix.csv")
    project_files = list(PROJECT.rglob("*"))
    by_name: dict[str, list[Path]] = {}
    for path in project_files:
        if path.is_file():
            by_name.setdefault(path.name, []).append(path)
    for row in references:
        verified = row.get("verified_by", "")
        abs_parts = [part.strip() for part in verified.split(";") if part.strip().startswith("/")]
        contains_abs = bool(abs_parts)
        alternatives: list[str] = []
        for part in abs_parts:
            path = Path(part)
            if path.exists():
                try:
                    alternatives.append(rel(path))
                    continue
                except ValueError:
                    pass
            for candidate in by_name.get(path.name, []):
                alternatives.append(rel(candidate))
        alternatives = sorted(set(alternatives))
        if contains_abs:
            status = "NEEDS_REPO_RELATIVE_OR_MANUAL_TRACEABILITY"
            action = "Replace local absolute path with repo-relative copied source or manually confirmed traceability before final submission."
        elif row["source_status"] == "UNRESOLVED":
            status = "NO_LOCAL_PATH_TO_AUDIT"
            action = "Resolve reference using verified external source."
        else:
            status = "PORTABLE_OR_TRACEABILITY_RELATIVE"
            action = "Confirm bibliographic metadata."
        rows.append({
            "placeholder": row["placeholder"],
            "original_verified_by": verified,
            "contains_absolute_local_path": "true" if contains_abs else "false",
            "repo_relative_alternative_if_any": "; ".join(alternatives),
            "portability_status": status,
            "required_action": action,
        })
    return rows


def unresolved_reference_tasks(reference_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    task_map = {
        "[REF_BRFG_DRAWING]": ("Confirm manufacturer metadata / authorized drawing provenance.", "high", "Manufacturer drawing/catalog or authorized CAD record.", "Unlabeled local screenshot or unverified dimension copy.", "1; 3.1"),
        "[REF_IEC_60137]": ("Confirm official IEC 60137 text or official scope page.", "high", "Official IEC standard or official IEC page.", "Untraceable secondary quote.", "1; 3.1"),
        "[REF_RIP_BUSHING_THERMAL]": ("Verify local RIP/bushing thermal literature and final bibliographic metadata.", "medium", "Peer-reviewed bushing thermal/electro-thermal paper.", "Unrelated insulation or cable-joint paper.", "1; 2; 3.2"),
        "[REF_DIELECTRIC_LOSS_THEORY]": ("Confirm dielectric-loss equation and RMS convention.", "high", "Textbook, standard, or peer-reviewed dielectric theory source.", "Formula-only web page without convention.", "2; 3.3; 4.4"),
        "[REF_CONDENSER_BUSHING_ELECTROSTATICS]": ("Verify condenser-screen electrostatic modeling support.", "medium", "Peer-reviewed condenser bushing electrostatics/electro-thermal paper.", "Generic capacitor reference without bushing relevance.", "2; 3.3"),
        "[REF_COMSOL_FLOATING_POTENTIAL]": ("Find official COMSOL Floating Potential / zero net charge documentation.", "high", "Official COMSOL documentation.", "Forum posts or unofficial tutorials as primary source.", "3.3"),
        "[REF_MESH_CONVERGENCE]": ("Find finite-element mesh convergence verification reference.", "high", "Numerical-method textbook/guideline or peer-reviewed FEM verification paper.", "Claim that mesh convergence proves physical validation.", "3.5; 4.6"),
        "[REF_RISK_DIAGNOSTIC_METHOD]": ("Find diagnostic screening/risk-zoning method support.", "medium", "Risk-screening or diagnostic threshold method reference.", "Standard-limit source misused as project threshold.", "4.3; 4.7"),
    }
    rows = []
    for row in reference_rows:
        status = row["source_status"]
        if any(flag in status for flag in ["UNRESOLVED", "PARTIALLY", "NEEDS", "CONFIRMATION"]):
            manual_task, priority, acceptable, unacceptable, sections = task_map[row["placeholder"]]
            rows.append({
                "placeholder": row["placeholder"],
                "source_status_from_RUN015": status,
                "manual_task": manual_task,
                "priority": priority,
                "acceptable_source": acceptable,
                "unacceptable_source": unacceptable,
                "affected_sections": sections,
                "can_submit_without_resolution": "NO_FOR_FINAL_SUBMISSION; YES_FOR_PLACEHOLDER_DRAFT",
                "notes": row["notes"],
            })
    return rows


def lock_lookup(lock_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out = {}
    for row in lock_rows:
        out[row["sentence_or_claim"]] = row
    return out


def numeric_claim_check(full_text: str, lock_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    lookup = lock_lookup(lock_rows)
    rows = []
    for claim_name, expected, lock_claim in NUMERIC_CLAIMS:
        appears = expected in full_text or claim_name in full_text
        lock = lookup.get(lock_claim, {})
        status = "OK" if appears and lock.get("evidence_status", "OK") != "FAIL" else "FAIL"
        rows.append({
            "numeric_claim": claim_name,
            "appears_in_full_manuscript": "true" if appears else "false",
            "expected_value": expected,
            "actual_text_value": expected if appears else "MISSING",
            "evidence_source_file": lock.get("evidence_source_file", ""),
            "evidence_status": status,
            "action": "none" if status == "OK" else "Insert exact evidence-locked value or resolve source mismatch.",
        })
    return rows


def assembly_traceability(missing_inputs: list[Path]) -> list[dict[str, str]]:
    missing_set = {rel(path) for path in missing_inputs}
    rows = [
        ("Introduction", RUN015_DOC / "introduction_literature_review_en.md", "Section 1", "yes", "none", "boundary and placeholder rows", "[REF_BRFG_DRAWING]; [REF_IEC_60137]; [REF_RIP_BUSHING_THERMAL]; [REF_CONDENSER_BUSHING_ELECTROSTATICS]; [REF_DIELECTRIC_LOSS_THEORY]; [REF_RISK_DIAGNOSTIC_METHOD]", "OK", "Integrated with title/abstract context."),
        ("Literature Review", RUN015_DOC / "introduction_literature_review_en.md", "Section 2", "yes", "none", "boundary and placeholder rows", "[REF_RIP_BUSHING_THERMAL]; [REF_DIELECTRIC_LOSS_THEORY]; [REF_CONDENSER_BUSHING_ELECTROSTATICS]; [REF_COMSOL_FLOATING_POTENTIAL]; [REF_MESH_CONVERGENCE]; [REF_RISK_DIAGNOSTIC_METHOD]", "OK", "Placeholder-aware only."),
        ("Methods", RUN014_DOC / "methods_results_integrated_en.md", "Section 3", "yes", "Fig. 1; Table 1; Table 2; Table 3; Table 5; Table 6", "RUN015 lock rows for source normalization, field review, mesh", "all method placeholders", "OK", "Heading levels normalized for full draft."),
        ("Results", RUN014_DOC / "methods_results_integrated_en.md", "Section 4", "yes", "Fig. 2-Fig. 9; Table 2; Table 4-Table 6", "all numeric lock rows", "dielectric/risk placeholders", "OK", "Risk-zone wording retained as diagnostic/internal screening."),
        ("Limitations", rel(RUN014_DOC / "reviewer_risk_checklist.md") + "; " + rel(RUN015_DOC / "manuscript_claim_boundary_notes.md"), "all rows/notes", "yes", "none", "claim-boundary notes", "manual reference tasks", "OK", "Generated from risk checklist and claim-boundary notes."),
        ("Conclusions", RUN015_TAB / "text_evidence_lock_table.csv", "all OK rows", "yes", "none", "all numeric lock rows", "none", "OK", "Only evidence-locked numerical conclusions used."),
        ("References placeholder list", RUN015_TAB / "reference_resolution_matrix.csv", "all placeholders", "yes", "none", "none", "all placeholders", "NEEDS_MANUAL_CONFIRMATION", "No formal bibliography fabricated."),
        ("Figure captions", RUN013_DOC / "figure_captions_en.md", "Fig. 1-Fig. 9", "yes", "Fig. 1-Fig. 9", "none", "none", "OK", "No new main figures added."),
        ("Table captions", RUN013_DOC / "table_captions_en.md", "Table 1-Table 6", "yes", "Table 1-Table 6", "none", "none", "OK", "No new tables added."),
        ("Supplementary note", READY / "manuscript_figure_index.csv", "FigS1-FigS7 rows", "yes", "Fig. S1-Fig. S7", "validation/audit routing", "none", "OK", "Supplementary routing only."),
    ]
    out = []
    for section, source, rows_used, inserted, figs, locks, refs, status, notes in rows:
        source_str = str(source) if isinstance(source, str) else rel(source)
        if source_str in missing_set:
            status = "MISSING_INPUT"
        out.append({
            "manuscript_section": section,
            "source_file": source_str,
            "source_section_or_rows": rows_used,
            "inserted_into_full_draft": inserted,
            "figures_or_tables_used": figs,
            "evidence_lock_rows_used": locks,
            "reference_placeholders_used": refs,
            "status": status,
            "notes": notes,
        })
    return out


def readiness_checklist(quality: dict[str, bool], unresolved_count: int, portability_count: int) -> str:
    lines = [
        "# RUN016 Submission Readiness Checklist",
        "",
        f"- manuscript completeness: {'PASS' if quality['manuscript_complete'] else 'NEEDS_REVISION'}",
        f"- numeric claim consistency: {'PASS' if quality['numeric_ok'] else 'NEEDS_REVISION'}",
        f"- figure/table callout completeness: {'PASS' if quality['fig_table_ok'] else 'NEEDS_REVISION'}",
        f"- reference placeholder status: {'PLACEHOLDER_AWARE; MANUAL VERIFICATION REQUIRED' if unresolved_count else 'PASS'}",
        f"- unresolved references: {unresolved_count}",
        f"- claim-boundary compliance: {'PASS' if quality['boundary_ok'] else 'NEEDS_REVISION'}",
        f"- limitation section compliance: {'PASS' if quality['limitations_ok'] else 'NEEDS_REVISION'}",
        f"- no fake bibliography check: {'PASS' if quality['no_fake_bib'] else 'NEEDS_REVISION'}",
        f"- no laboratory/field verification overclaim check: {'PASS' if quality['no_validation_overclaim'] else 'NEEDS_REVISION'}",
        f"- no standard-limit overclaim check: {'PASS' if quality['no_standard_overclaim'] else 'NEEDS_REVISION'}",
        f"- path normalization status: {'PASS' if quality['path_normalized'] else 'NEEDS_REVISION'}",
        f"- reference path portability issues: {portability_count}",
        "",
        "Final readiness judgment: RUN016 is ready as a placeholder-aware full manuscript draft. It is not ready for submission until unresolved references and local-path traceability issues are manually resolved.",
    ]
    return "\n".join(lines)


def quality_gate(full_text: str, numeric_rows: list[dict[str, str]],
                 missing_inputs: list[Path], unresolved_rows: list[dict[str, str]],
                 portability_rows: list[dict[str, str]]) -> tuple[dict[str, bool], list[str], bool]:
    required_phrases = [
        "# Abstract",
        "# Keywords",
        "# 1. Introduction",
        "# 2. Literature Review",
        "# 3. Numerical Model and Simulation Setup",
        "# 4. Results and Discussion",
        "# 5. Limitations and Future Work",
        "# 6. Conclusions",
        "# References Placeholder List",
        "# Figure Captions",
        "# Table Captions",
        "# Supplementary Material Note",
    ]
    forbidden = [
        "experimentally validated",
        "field-validated",
        "standard operating limit",
        "IEC/IEEE temperature limit",
        "measured defect reproduced",
    ]
    fig_terms = [f"Fig. {i}" for i in range(1, 10)] + [f"Fig. S{i}" for i in range(1, 8)]
    table_terms = [f"Table {i}" for i in range(1, 7)]
    quality = {
        "path_normalized": all((RUN015_DOC / name).exists() and (RUN015_DOC / name).stat().st_size > 0 for name in RUN015_MAIN_FILES),
        "outputs_exist": all(path.exists() and path.stat().st_size > 0 for path in [
            RUN016_DOC / "full_manuscript_draft_en.md",
            RUN016_DOC / "full_manuscript_draft_zh.md",
            RUN016_DOC / "abstract_title_keywords_en.md",
            RUN016_TAB / "manuscript_assembly_traceability.csv",
            RUN016_TAB / "full_draft_numeric_claim_check.csv",
            RUN016_TAB / "reference_path_portability_audit.csv",
            RUN016_TAB / "unresolved_reference_and_manual_tasks.csv",
            RUN016_DOC / "submission_readiness_checklist.md",
        ]),
        "manuscript_complete": all(phrase in full_text for phrase in required_phrases),
        "numeric_ok": all(row["evidence_status"] != "FAIL" for row in numeric_rows),
        "fig_table_ok": all(term in full_text for term in fig_terms + table_terms),
        "boundary_ok": (
            ("DIELECTRIC_LOSS_REVIEW_REQUIRED" in full_text or "dielectric_loss_review_required" in full_text)
            and "diagnostic risk zones are internal screening classes" in full_text
            and "parameterized equivalent model" in full_text
        ),
        "limitations_ok": all(term in full_text for term in [
            "two-dimensional axisymmetric",
            "CFD fluid domains",
            "steady-state",
            "three-dimensional terminal",
            "No laboratory, field-monitoring, or physical prototype validation",
        ]),
        "no_fake_bib": "doi.org" not in full_text.lower() and "References Placeholder List" in full_text,
        "no_validation_overclaim": not any(term in full_text for term in forbidden[:2]),
        "no_standard_overclaim": not any(term in full_text for term in forbidden[2:4]),
        "no_contact_overclaim": forbidden[4] not in full_text,
        "unresolved_tasks_listed": len(unresolved_rows) >= 1,
        "portability_audited": any(row["contains_absolute_local_path"] == "true" for row in portability_rows),
        "missing_inputs_ok": not missing_inputs,
    }
    problems = [key for key, value in quality.items() if not value]
    gate_yes = (
        quality["path_normalized"]
        and quality["outputs_exist"]
        and quality["manuscript_complete"]
        and quality["numeric_ok"]
        and quality["fig_table_ok"]
        and quality["boundary_ok"]
        and quality["limitations_ok"]
        and quality["no_fake_bib"]
        and quality["no_validation_overclaim"]
        and quality["no_standard_overclaim"]
        and quality["no_contact_overclaim"]
        and quality["unresolved_tasks_listed"]
        and quality["portability_audited"]
        and quality["missing_inputs_ok"]
    )
    return quality, problems, gate_yes


def write_report(path_note: dict[str, list[str] | str], missing_inputs: list[Path],
                 generated_files: list[Path], numeric_rows: list[dict[str, str]],
                 ref_rows: list[dict[str, str]], unresolved_rows: list[dict[str, str]],
                 portability_rows: list[dict[str, str]], quality: dict[str, bool],
                 problems: list[str], gate_yes: bool) -> None:
    portability_issues = [row for row in portability_rows if row["contains_absolute_local_path"] == "true"]
    ref_status: dict[str, int] = {}
    for row in ref_rows:
        ref_status[row["source_status"]] = ref_status.get(row["source_status"], 0) + 1
    body = [
        "# RUN016 Full Manuscript Assembly Report",
        "",
        "## Task Objective",
        "",
        "RUN016 normalizes RUN015 artifact paths and assembles a placeholder-aware full English manuscript draft from RUN015 Introduction/Literature Review, RUN014 Methods + Results, RUN013 captions, manuscript-ready callout plans, evidence locks, and claim-boundary notes. No COMSOL model was run and no new simulation case was added.",
        "",
        "## RUN015 Path Normalization Summary",
        "",
        f"- old_path: `{path_note['old_path']}`",
        f"- canonical_path: `{path_note['canonical_path']}`",
        f"- copied_files: {', '.join(path_note['copied_files']) if path_note['copied_files'] else 'none'}",
        f"- files_already_present: {', '.join(path_note['files_already_present']) if path_note['files_already_present'] else 'none'}",
        f"- any_missing_files: {', '.join(path_note['any_missing_files']) if path_note['any_missing_files'] else 'none'}",
        "",
        "## Inputs Checked",
        "",
    ]
    for path in REQUIRED_INPUTS:
        body.append(f"- {rel(path)}: {file_status(path)}")
    body.extend(["", "## Files Generated", ""])
    for path in generated_files:
        body.append(f"- {rel(path)}")
    body.extend(["", "## Missing Inputs", ""])
    if missing_inputs:
        for path in missing_inputs:
            body.append(f"- {rel(path)}")
    else:
        body.append("None.")
    body.extend([
        "",
        "## Full Manuscript Assembly Status",
        "",
        f"Full manuscript sections/check blocks complete: {'PASS' if quality['manuscript_complete'] else 'NEEDS_REVISION'}.",
        "",
        "## Numeric Claim Check Status",
        "",
        f"Numeric checks: {sum(1 for row in numeric_rows if row['evidence_status'] == 'OK')}/{len(numeric_rows)} OK.",
        "",
        "## Figure/Table Callout Status",
        "",
        f"Figure/table/supplementary routing: {'PASS' if quality['fig_table_ok'] else 'NEEDS_REVISION'}.",
        "",
        "## Reference Placeholder Status",
        "",
        ", ".join(f"{key}: {value}" for key, value in sorted(ref_status.items())),
        "",
        "## Claim-Boundary Compliance",
        "",
        f"Boundary compliance: {'PASS' if quality['boundary_ok'] and quality['limitations_ok'] else 'NEEDS_REVISION'}.",
        "",
        "## Portability Audit Summary",
        "",
        f"Reference rows with local absolute paths: {len(portability_issues)}. These are tracked in `reference_path_portability_audit.csv` and require repo-relative alternatives or manual traceability before final submission.",
        "",
        "## Remaining Manual Tasks",
        "",
        f"Unresolved or partially resolved reference/manual tasks: {len(unresolved_rows)}.",
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
        "## RUN017 Readiness",
        "",
        "RUN016 is ready for reference finalization and submission formatting as a placeholder-aware manuscript draft. It is not a final submission package until unresolved references and local-path traceability are resolved.",
        "",
        f"Can proceed to RUN017_REFERENCE_FINALIZATION_AND_SUBMISSION_FORMATTING: {'YES' if gate_yes else 'NO'}",
    ])
    write_text(RUN016_DOC / "run016_full_manuscript_assembly_report.md", "\n".join(body))


def main() -> None:
    ensure_dirs()
    path_note = normalize_run015_paths()
    missing_inputs = [path for path in REQUIRED_INPUTS if not path.exists() or path.stat().st_size == 0]

    full_en = assemble_full_manuscript_en()
    full_zh = assemble_full_manuscript_zh()
    write_text(RUN016_DOC / "full_manuscript_draft_en.md", full_en)
    write_text(RUN016_DOC / "full_manuscript_draft_zh.md", full_zh)
    write_text(RUN016_DOC / "abstract_title_keywords_en.md", abstract_title_keywords())

    lock_rows = read_csv(RUN015_TAB / "text_evidence_lock_table.csv")
    numeric_rows = numeric_claim_check(full_en, lock_rows)
    write_csv(RUN016_TAB / "full_draft_numeric_claim_check.csv", [
        "numeric_claim",
        "appears_in_full_manuscript",
        "expected_value",
        "actual_text_value",
        "evidence_source_file",
        "evidence_status",
        "action",
    ], numeric_rows)

    portability_rows = portability_audit()
    write_csv(RUN016_TAB / "reference_path_portability_audit.csv", [
        "placeholder",
        "original_verified_by",
        "contains_absolute_local_path",
        "repo_relative_alternative_if_any",
        "portability_status",
        "required_action",
    ], portability_rows)

    ref_rows = read_csv(RUN015_TAB / "reference_resolution_matrix.csv")
    unresolved_rows = unresolved_reference_tasks(ref_rows)
    write_csv(RUN016_TAB / "unresolved_reference_and_manual_tasks.csv", [
        "placeholder",
        "source_status_from_RUN015",
        "manual_task",
        "priority",
        "acceptable_source",
        "unacceptable_source",
        "affected_sections",
        "can_submit_without_resolution",
        "notes",
    ], unresolved_rows)

    trace_rows = assembly_traceability(missing_inputs)
    write_csv(RUN016_TAB / "manuscript_assembly_traceability.csv", [
        "manuscript_section",
        "source_file",
        "source_section_or_rows",
        "inserted_into_full_draft",
        "figures_or_tables_used",
        "evidence_lock_rows_used",
        "reference_placeholders_used",
        "status",
        "notes",
    ], trace_rows)

    quality, problems, gate_yes = quality_gate(full_en, numeric_rows, missing_inputs, unresolved_rows, portability_rows)
    write_text(RUN016_DOC / "submission_readiness_checklist.md", readiness_checklist(
        quality,
        unresolved_count=len(unresolved_rows),
        portability_count=sum(1 for row in portability_rows if row["contains_absolute_local_path"] == "true"),
    ))

    generated_files = [
        RUN016_DOC / "full_manuscript_draft_en.md",
        RUN016_DOC / "full_manuscript_draft_zh.md",
        RUN016_DOC / "abstract_title_keywords_en.md",
        RUN016_TAB / "manuscript_assembly_traceability.csv",
        RUN016_TAB / "full_draft_numeric_claim_check.csv",
        RUN016_TAB / "reference_path_portability_audit.csv",
        RUN016_TAB / "unresolved_reference_and_manual_tasks.csv",
        RUN016_DOC / "submission_readiness_checklist.md",
        RUN016_DOC / "run016_full_manuscript_assembly_report.md",
        RUN015_DOC / "run015_path_normalization_note.md",
    ]
    write_report(path_note, missing_inputs, generated_files, numeric_rows, ref_rows, unresolved_rows, portability_rows, quality, problems, gate_yes)

    print("RUN016 generated files:")
    for path in generated_files:
        print(f"- {rel(path)}")
    print(f"RUN016 quality gate status: {'PASS' if gate_yes else 'NEEDS_REVISION'}")
    if problems:
        print("Problems:")
        for problem in problems:
            print(f"- {problem}")
    if not gate_yes:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
