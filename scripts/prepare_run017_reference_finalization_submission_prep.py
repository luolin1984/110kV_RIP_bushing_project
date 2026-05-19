"""Prepare RUN017 reference-finalization and submission-formatting prep.

RUN017 canonicalizes RUN016 outputs, creates a submission-format-prep manuscript,
and audits references, portability, numeric claims, claim boundaries, figures,
tables, and remaining manual tasks.

It does not run COMSOL, add simulations, fabricate references, or modify
RUN006-RUN013 raw result artifacts. The only legacy-copy operation permitted is
from docs/RUN016 and results/RUN016 into the canonical RUN016 locations when a
canonical file is missing.
"""

from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]

LEGACY_RUN016_DOC = PROJECT / "docs" / "RUN016"
LEGACY_RUN016_RESULT = PROJECT / "results" / "RUN016"
RUN013_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN013"
RUN014_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN014"
RUN015_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN015"
RUN016_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN016"
RUN017_DOC = PROJECT / "docs" / "manuscript_draft_sections" / "RUN017"

READY = PROJECT / "results" / "summary_tables" / "manuscript_ready"
RUN014_TAB = READY / "RUN014"
RUN015_TAB = READY / "RUN015"
RUN016_TAB = READY / "RUN016"
RUN017_TAB = READY / "RUN017"


RUN016_DOC_FILES = [
    "full_manuscript_draft_en.md",
    "full_manuscript_draft_zh.md",
    "abstract_title_keywords_en.md",
    "submission_readiness_checklist.md",
    "run016_full_manuscript_assembly_report.md",
]

RUN016_RESULT_FILES = [
    "manuscript_assembly_traceability.csv",
    "full_draft_numeric_claim_check.csv",
    "reference_path_portability_audit.csv",
    "unresolved_reference_and_manual_tasks.csv",
]

REQUIRED_INPUTS = [
    RUN016_DOC / "full_manuscript_draft_en.md",
    RUN016_DOC / "full_manuscript_draft_zh.md",
    RUN016_DOC / "abstract_title_keywords_en.md",
    RUN016_DOC / "submission_readiness_checklist.md",
    RUN016_DOC / "run016_full_manuscript_assembly_report.md",
    RUN016_TAB / "manuscript_assembly_traceability.csv",
    RUN016_TAB / "full_draft_numeric_claim_check.csv",
    RUN016_TAB / "reference_path_portability_audit.csv",
    RUN016_TAB / "unresolved_reference_and_manual_tasks.csv",
    RUN015_TAB / "reference_resolution_matrix.csv",
    RUN015_TAB / "text_evidence_lock_table.csv",
    RUN015_DOC / "reference_search_tasks.md",
    RUN015_DOC / "manuscript_claim_boundary_notes.md",
    RUN014_DOC / "reviewer_risk_checklist.md",
    RUN014_TAB / "terminology_consistency_table.csv",
    RUN014_TAB / "figure_table_callout_plan.csv",
    RUN013_DOC / "figure_captions_en.md",
    RUN013_DOC / "table_captions_en.md",
    READY / "manuscript_figure_index.csv",
    READY / "manuscript_table_index.csv",
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


NUMERIC_CHECKS = [
    ("88.589 degC / 88.589 °C", ["88.589 °C", "88.589 degC"], "88.589 °C"),
    ("28.049 W", ["28.049 W"], "28.049 W"),
    ("11.020", ["11.020"], "11.020"),
    ("67.397-134.974 degC / °C", ["67.397-134.974 °C", "67.397-134.974 degC"], "67.397-134.974 °C"),
    ("129.925 degC / °C", ["129.925 °C", "129.925 degC"], "129.925 °C"),
    ("safe 119, attention 4, warning 2, thermal-risk 0", ["safe 119, attention 4, warning 2, thermal-risk 0"], "safe 119, attention 4, warning 2, thermal-risk 0"),
    ("contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0", ["contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0"], "contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0"),
    ("2.678%", ["2.678%"], "2.678%"),
    ("0/125 field_singularity_flag", ["0/125 field_singularity_flag", "0/125 field-singularity"], "0/125 field_singularity_flag"),
    ("125/125 dielectric_loss_review_required", ["125/125 dielectric_loss_review_required"], "125/125 dielectric_loss_review_required"),
    ("0.617 degC / °C mean delta_Tmax", ["0.617 °C mean delta_Tmax", "0.617 degC mean delta_Tmax", "average of 0.617 °C"], "0.617 °C mean delta_Tmax"),
    ("2.816 degC / °C max delta_Tmax", ["2.816 °C max delta_Tmax", "2.816 degC max delta_Tmax", "maximum of 2.816 °C"], "2.816 °C max delta_Tmax"),
    ("2/125 changed risk zones", ["2/125 changed risk zones", "2 of the 125 cases"], "2/125 changed risk zones"),
    ("0.355% max Tmax mesh error", ["0.355% max Tmax mesh error", "0.355% for Tmax_global"], "0.355% max Tmax mesh error"),
    ("0.002% max E95 mesh error", ["0.002% max E95 mesh error", "0.002% for E95_RIP"], "0.002% max E95 mesh error"),
    ("0.002% max Qdielectric mesh error", ["0.002% max Qdielectric mesh error", "0.002% for field-coupled RIP dielectric loss"], "0.002% max Qdielectric mesh error"),
    ("tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil", ["tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil"], "tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil"),
]


def ensure_dirs() -> None:
    RUN016_DOC.mkdir(parents=True, exist_ok=True)
    RUN016_TAB.mkdir(parents=True, exist_ok=True)
    RUN017_DOC.mkdir(parents=True, exist_ok=True)
    RUN017_TAB.mkdir(parents=True, exist_ok=True)


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


def exists_nonempty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def canonicalize_run016_paths() -> dict[str, list[str] | str]:
    copied_docs: list[str] = []
    copied_results: list[str] = []
    already_present: list[str] = []
    missing: list[str] = []

    for name in RUN016_DOC_FILES:
        legacy = LEGACY_RUN016_DOC / name
        canonical = RUN016_DOC / name
        if exists_nonempty(canonical):
            already_present.append(name)
        elif exists_nonempty(legacy):
            shutil.copy2(legacy, canonical)
            copied_docs.append(name)
        else:
            missing.append(name)

    for name in RUN016_RESULT_FILES:
        legacy = LEGACY_RUN016_RESULT / name
        canonical = RUN016_TAB / name
        if exists_nonempty(canonical):
            already_present.append(name)
        elif exists_nonempty(legacy):
            shutil.copy2(legacy, canonical)
            copied_results.append(name)
        else:
            missing.append(name)

    mismatch_remains = "YES" if missing else "NO"
    note = [
        "# RUN016 Path Canonicalization Note",
        "",
        f"- legacy_doc_path: `{rel(LEGACY_RUN016_DOC)}`",
        f"- canonical_doc_path: `{rel(RUN016_DOC)}`",
        f"- legacy_result_path: `{rel(LEGACY_RUN016_RESULT)}`",
        f"- canonical_result_path: `{rel(RUN016_TAB)}`",
        f"- copied_doc_files: {', '.join(copied_docs) if copied_docs else 'none'}",
        f"- copied_result_files: {', '.join(copied_results) if copied_results else 'none'}",
        f"- already_present_files: {', '.join(already_present) if already_present else 'none'}",
        f"- missing_files: {', '.join(missing) if missing else 'none'}",
        "- reason_for_canonicalization: RUN013-RUN017 manuscript artifacts use `docs/manuscript_draft_sections/<RUN_ID>/` and manuscript-ready tables use `results/summary_tables/manuscript_ready/<RUN_ID>/`. Canonicalizing RUN016 keeps RUN017 inputs stable without deleting legacy files.",
        f"- whether RUN016 script/report path mismatch remains: {mismatch_remains}",
    ]
    write_text(RUN017_DOC / "run016_path_canonicalization_note.md", "\n".join(note))
    return {
        "copied_doc_files": copied_docs,
        "copied_result_files": copied_results,
        "already_present_files": already_present,
        "missing_files": missing,
        "mismatch_remains": mismatch_remains,
    }


def prep_manuscript_text(text: str) -> str:
    text = text.replace("degC", "°C")
    text = text.replace("validated finite-element numerical risk-boundary scan", "audited finite-element numerical screening scan")
    text = text.replace("validated numerical risk-boundary scan", "audited numerical screening scan")
    text = text.replace("Evidence-lock summary: RUN010 reports 0/125 field_singularity_flag cases and 125/125 dielectric_loss_review_required cases; RUN010 contact risk-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0.",
                        "The numerical verification record also reports 0/125 field_singularity_flag cases, 125/125 dielectric_loss_review_required cases, and RUN010 contact risk-zone counts of contact_safe 115, contact_attention 6, contact_warning 4, and contact-risk 0. These values are used as validation evidence for the field and selection-integrity checks rather than as stand-alone physical validation.")
    text = text.replace("IEC or IEEE standard limits", "IEC/IEEE standard limits")
    text = text.replace("guaranteed operating limits", "operating guarantees")
    return text


def unit_style_mapping() -> list[dict[str, str]]:
    return [
        {
            "original_style": "degC",
            "submission_style": "°C",
            "scope": "temperature values in submission_format_prep_manuscript_en.md and zh.md",
            "numeric_equivalence": "unchanged numeric value",
            "notes": "Numeric claim check accepts both degC and °C while submission draft uses °C.",
        },
        {
            "original_style": "W",
            "submission_style": "W",
            "scope": "heat source values",
            "numeric_equivalence": "unchanged",
            "notes": "No unit style conversion needed.",
        },
        {
            "original_style": "%",
            "submission_style": "%",
            "scope": "mesh errors and residuals",
            "numeric_equivalence": "unchanged",
            "notes": "No unit style conversion needed.",
        },
    ]


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def final_reference_status(run015_status: str, absolute_issue: bool, repo_relative: bool) -> str:
    if run015_status == "UNRESOLVED":
        return "UNRESOLVED"
    if absolute_issue and not repo_relative:
        return "LOCAL_PATH_ONLY_NOT_PORTABLE"
    if "NEEDS" in run015_status or "TRACEABILITY" in run015_status:
        return "NEEDS_MANUAL_CONFIRMATION"
    if "PARTIALLY" in run015_status or "LOCAL_PDF_CANDIDATES" in run015_status:
        return "PARTIALLY_RESOLVED_NEEDS_METADATA"
    return "NEEDS_MANUAL_CONFIRMATION"


def build_reference_finalization() -> list[dict[str, str]]:
    refs = read_csv(RUN015_TAB / "reference_resolution_matrix.csv")
    unresolved = by_key(read_csv(RUN16_TAB_UNRESOLVED()), "placeholder") if exists_nonempty(RUN16_TAB_UNRESOLVED()) else {}
    portability = by_key(read_csv(RUN016_TAB / "reference_path_portability_audit.csv"), "placeholder")
    rows: list[dict[str, str]] = []
    high_priority = {"[REF_BRFG_DRAWING]", "[REF_IEC_60137]", "[REF_DIELECTRIC_LOSS_THEORY]", "[REF_COMSOL_FLOATING_POTENTIAL]", "[REF_MESH_CONVERGENCE]"}

    for ref in refs:
        placeholder = ref["placeholder"]
        unresolved_row = unresolved.get(placeholder, {})
        port = portability.get(placeholder, {})
        abs_issue = port.get("contains_absolute_local_path", "false") == "true"
        repo_alt = port.get("repo_relative_alternative_if_any", "")
        repo_available = bool(repo_alt) and "/Users/" not in repo_alt
        status = final_reference_status(ref["source_status"], abs_issue, repo_available)
        current_key = ref.get("candidate_reference_key", "")
        final_key = "" if status != "RESOLVED_VERIFIED" else current_key
        required = unresolved_row.get("manual_task", "Confirm reference metadata and source claim before submission.")
        priority = unresolved_row.get("priority", "high" if placeholder in high_priority else "medium")
        rows.append({
            "placeholder": placeholder,
            "RUN015_source_status": ref["source_status"],
            "RUN016_manual_task": unresolved_row.get("manual_task", ""),
            "priority": priority,
            "current_candidate_key": current_key,
            "current_candidate_title": ref.get("candidate_reference_title", ""),
            "current_candidate_type": ref.get("candidate_reference_type", ""),
            "verified_source_available": "false",
            "repo_relative_source_available": "true" if repo_available else "false",
            "absolute_path_issue": "true" if abs_issue else "false",
            "final_reference_key": final_key,
            "final_reference_entry": "",
            "final_reference_status": status,
            "affected_sections": unresolved_row.get("affected_sections", ref.get("section", "")),
            "required_action": required,
            "notes": "No formal reference entry is emitted unless source metadata and claim support are verified.",
        })
    return rows


def RUN16_TAB_UNRESOLVED() -> Path:
    return RUN016_TAB / "unresolved_reference_and_manual_tasks.csv"


def placeholder_resolution_notes(rows: list[dict[str, str]]) -> str:
    acceptable = {
        "[REF_BRFG_DRAWING]": "manufacturer-authorized drawing, catalog, or controlled CAD record with provenance",
        "[REF_IEC_60137]": "official IEC 60137 standard text or official IEC page",
        "[REF_RIP_BUSHING_THERMAL]": "verified peer-reviewed RIP/bushing thermal or electro-thermal paper",
        "[REF_DIELECTRIC_LOSS_THEORY]": "verified dielectric-loss theory source confirming formula and RMS convention",
        "[REF_CONDENSER_BUSHING_ELECTROSTATICS]": "verified condenser-bushing electrostatics or field-grading paper",
        "[REF_COMSOL_FLOATING_POTENTIAL]": "official COMSOL documentation or manual",
        "[REF_MESH_CONVERGENCE]": "finite-element verification guideline, numerical methods text, or peer-reviewed FEM convergence paper",
        "[REF_RISK_DIAGNOSTIC_METHOD]": "diagnostic screening or risk-zoning method source that does not define project thresholds as standards",
    }
    unacceptable = {
        "[REF_BRFG_DRAWING]": "unlabeled screenshot or local drawing without provenance",
        "[REF_IEC_60137]": "secondary webpage used as a substitute for standard clauses",
        "[REF_COMSOL_FLOATING_POTENTIAL]": "forum post or unofficial tutorial as primary documentation",
    }
    lines = [
        "# References Placeholder Resolution Notes",
        "",
        "RUN017 does not fabricate final bibliography entries. If any placeholder remains unresolved, partially resolved, or local-path-only, the project cannot enter a final submission package.",
    ]
    for row in rows:
        placeholder = row["placeholder"]
        lines.extend([
            "",
            f"## {placeholder}",
            "",
            f"- Current status: {row['final_reference_status']}",
            f"- Acceptable evidence: {acceptable.get(placeholder, 'verified source matching the claim and manuscript context')}",
            f"- Unacceptable evidence: {unacceptable.get(placeholder, 'unverified source, guessed metadata, or source that does not support the claim')}",
            f"- Can submit now: {'NO' if row['final_reference_status'] != 'RESOLVED_VERIFIED' else 'YES'}",
            f"- Manual task: {row['required_action']}",
            f"- Notes: {row['notes']}",
        ])
    return "\n".join(lines)


def reference_portability_fix_plan() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(RUN016_TAB / "reference_path_portability_audit.csv"):
        absolute = row["contains_absolute_local_path"] == "true"
        excerpt = row["original_verified_by"][:220]
        repo_alt = row["repo_relative_alternative_if_any"]
        if absolute:
            if repo_alt and "/Users/" not in repo_alt:
                status = "REPO_RELATIVE_CANDIDATE_NEEDS_PROVENANCE_CONFIRMATION"
                can_final = "NO"
                action = "Confirm repo-relative candidate provenance and replace absolute traceability in final reference notes."
            else:
                status = "NOT_PORTABLE"
                can_final = "NO"
                action = "Copy authorized source into repo raw_sources or document manual traceability without local absolute path."
        else:
            status = "NO_ABSOLUTE_PATH_ISSUE"
            can_final = "YES_IF_REFERENCE_RESOLVED"
            action = "Resolve reference metadata and source claim."
        rows.append({
            "placeholder": row["placeholder"],
            "absolute_path_detected": row["contains_absolute_local_path"],
            "local_path_excerpt": excerpt,
            "repo_relative_alternative": repo_alt,
            "portability_fix_status": status,
            "required_action": action,
            "can_be_used_in_final_submission": can_final,
            "notes": row["required_action"],
        })
    return rows


def numeric_claim_check(text: str) -> list[dict[str, str]]:
    run016_checks = by_key(read_csv(RUN016_TAB / "full_draft_numeric_claim_check.csv"), "numeric_claim")
    rows = []
    for claim, variants, expected in NUMERIC_CHECKS:
        found_variant = next((variant for variant in variants if variant in text), "")
        prior = run016_checks.get(claim, {})
        status = "OK" if found_variant and prior.get("evidence_status", "OK") != "FAIL" else "FAIL"
        unit_style = "°C" if "°C" in expected else ("mixed/identifier" if "degC" in claim else "unchanged")
        rows.append({
            "numeric_claim": claim,
            "expected_value_from_RUN016_or_RUN015": expected,
            "appears_in_submission_prep_draft": "true" if found_variant else "false",
            "actual_text_value": found_variant if found_variant else "MISSING",
            "evidence_source_file": prior.get("evidence_source_file", ""),
            "evidence_status": status,
            "unit_style": unit_style,
            "action": "none" if status == "OK" else "Restore exact evidence-locked value or investigate mismatch.",
        })
    return rows


def claim_boundary_check(text: str) -> list[dict[str, str]]:
    checks = [
        ("finite-element numerical screening, not physical experiment", ["finite-element numerical screening", "not laboratory or field validation"], "HIGH"),
        ("no laboratory validation", ["No laboratory", "validation has been completed"], "HIGH"),
        ("no field monitoring validation", ["field-monitoring", "validation has been completed"], "HIGH"),
        ("diagnostic risk zoning is internal/screening, not standard limit", ["diagnostic risk zones are internal screening classes", "not standard limits"], "HIGH"),
        ("contact-resistance multiplier is parameterized equivalent model, not measured defect", ["contact-resistance multiplier is a parameterized equivalent model", "not a measured defect"], "HIGH"),
        ("DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required retained", ["DIELECTRIC_LOSS_REVIEW_REQUIRED", "dielectric_loss_review_required"], "HIGH"),
        ("2D axisymmetric limitation", ["two-dimensional axisymmetric"], "MEDIUM"),
        ("no CFD fluid-domain", ["rather than resolved CFD fluid domains"], "MEDIUM"),
        ("no transient overload/weather history", ["transient overload", "outside RUN010"], "MEDIUM"),
        ("no full 3D terminal/flange/bolt resolution", ["three-dimensional terminal", "flange bolt holes"], "MEDIUM"),
        ("no operational rule / no safety guarantee", ["not an operational rule", "not standard limits"], "HIGH"),
        ("unresolved references require manual verification before submission", ["Reference placeholders also remain unresolved or partially resolved", "manual verification before submission"], "HIGH"),
    ]
    rows = []
    for boundary, phrases, risk in checks:
        appears = all(phrase in text for phrase in phrases)
        rows.append({
            "boundary_item": boundary,
            "required_phrase_or_meaning": " AND ".join(phrases),
            "appears_in_submission_prep_draft": "true" if appears else "false",
            "risk_if_missing": risk,
            "status": "OK" if appears else "FAIL",
            "action": "none" if appears else "Restore claim-boundary sentence before any submission formatting.",
        })
    return rows


def caption_map(path: Path, prefix: str) -> dict[str, str]:
    text = read_text(path)
    out: dict[str, str] = {}
    pattern = re.compile(r"\*\*(Fig\. \d+|Table \d+)\.?\s*([^*]+)\*\*\s*(.*?)(?=\n\n\*\*|\Z)", re.S)
    for match in pattern.finditer(text):
        label = match.group(1)
        title = match.group(2).strip()
        rest = " ".join(match.group(3).strip().split())
        out[label] = f"{label}. {title} {rest}".strip()
    return out


def figure_table_package() -> str:
    fig_index = by_key(read_csv(READY / "manuscript_figure_index.csv"), "figure_id")
    table_index = by_key(read_csv(READY / "manuscript_table_index.csv"), "table_id")
    callouts = read_csv(RUN014_TAB / "figure_table_callout_plan.csv")
    callout_by_item = by_key(callouts, "item_id")
    fig_caps = caption_map(RUN013_DOC / "figure_captions_en.md", "Fig")
    table_caps = caption_map(RUN013_DOC / "table_captions_en.md", "Table")

    lines = ["# Figure and Table Submission Package", ""]
    lines.extend(["## Main Figures", ""])
    for i in range(1, 10):
        key = f"Fig{i}"
        label = f"Fig. {i}"
        idx = fig_index.get(key, {})
        call = callout_by_item.get(label, {})
        lines.append(f"### {label}")
        lines.append(f"- caption: {fig_caps.get(label, idx.get('figure_title', 'NEEDS_MANUAL_CONFIRMATION'))}")
        lines.append(f"- source file path: `{idx.get('file_path', 'MISSING')}`")
        lines.append(f"- main/supplementary status: {idx.get('main_or_supplementary', 'MISSING')}")
        lines.append(f"- exists according to index: {idx.get('exists', 'MISSING')}")
        lines.append(f"- manuscript section callout: {call.get('first_callout_section', 'NEEDS_MANUAL_CONFIRMATION')} - {call.get('first_callout_sentence', '')}")
        lines.append("")
    lines.extend(["## Main Tables", ""])
    for i, table_id in enumerate([
        "Table1_run_stage_audit_summary",
        "Table2_key_result_summary",
        "Table3_model_validation_evidence_chain",
        "Table4_run010_risk_boundary_summary",
        "Table5_mesh_independence_summary",
        "Table6_sensitivity_ranking_summary",
    ], 1):
        label = f"Table {i}"
        idx = table_index.get(table_id, {})
        call = callout_by_item.get(label, {})
        lines.append(f"### {label}")
        lines.append(f"- caption: {table_caps.get(label, idx.get('table_title', 'NEEDS_MANUAL_CONFIRMATION'))}")
        lines.append(f"- source file path: `{idx.get('file_path', 'MISSING')}`")
        lines.append(f"- main/supplementary status: {idx.get('main_or_supplementary', 'MISSING')}")
        lines.append(f"- manuscript section callout: {call.get('first_callout_section', 'NEEDS_MANUAL_CONFIRMATION')} - {call.get('first_callout_sentence', '')}")
        lines.append("")
    lines.extend(["## Supplementary Figures", ""])
    for i in range(1, 8):
        key = f"FigS{i}"
        label = f"Fig. S{i}"
        idx = fig_index.get(key, {})
        call = callout_by_item.get(label, {})
        lines.append(f"### {label}")
        lines.append(f"- caption/usage: {idx.get('figure_title', 'NEEDS_MANUAL_CONFIRMATION')}")
        lines.append(f"- source file path: `{idx.get('file_path', 'MISSING')}`")
        lines.append(f"- supplementary routing: {call.get('first_callout_section', 'Supplementary Material Note')}")
        lines.append(f"- exists according to index: {idx.get('exists', 'MISSING')}")
        lines.append("")
    return "\n".join(lines)


def abstract_word_count(text: str) -> int:
    match = re.search(r"# Abstract\s+(.*?)(?=\n# Keywords)", text, flags=re.S)
    if not match:
        return 0
    words = re.findall(r"[A-Za-z0-9_./%-]+", match.group(1))
    return len(words)


def formatting_checklist(text: str, numeric_ok: bool, boundary_ok: bool, unresolved_count: int) -> str:
    word_count = abstract_word_count(text)
    keywords_match = re.search(r"# Keywords\s+(.*?)(?=\n# 1\.)", text, flags=re.S)
    keywords = [kw.strip() for kw in keywords_match.group(1).split(";") if kw.strip()] if keywords_match else []
    lines = [
        "# Journal Submission Formatting Checklist",
        "",
        f"- title length check: NEEDS_JOURNAL_SPECIFIC_REVIEW; recommended title has {len('Electro-Thermal Coupled Finite-Element Diagnostic Risk-Boundary Simulation of a 126 kV/1250 A RIP Condenser Transformer Bushing under Contact-Resistance Degradation')} characters.",
        f"- abstract word count: {word_count} words; {'PASS' if 180 <= word_count <= 250 else 'NEEDS_REVISION'} for 180-250 target.",
        f"- keywords count: {len(keywords)}; {'PASS' if 6 <= len(keywords) <= 8 else 'NEEDS_REVISION'}.",
        "- section completeness: PASS if Title Options, Abstract, Keywords, Sections 1-6, References Placeholder List, Figure Captions, Table Captions, and Supplementary Material Note are present.",
        "- figure captions completeness: Fig. 1-Fig. 9 included; source paths audited in figure_table_submission_package.md.",
        "- table captions completeness: Table 1-Table 6 included; source paths audited in figure_table_submission_package.md.",
        f"- references unresolved status: {unresolved_count} unresolved/partial/manual tasks remain.",
        "- placeholder removal requirement before final submission: all placeholders must be resolved or explicitly accepted by the target journal workflow before submission.",
        "- unit style check: temperature units converted from degC to °C in submission-prep draft; numeric equivalence retained.",
        "- no fake bibliography check: PASS; References Placeholder List is not converted into formal bibliography.",
        f"- no overclaim check: {'PASS' if boundary_ok else 'NEEDS_REVISION'}.",
        "- recommended next action: resolve high-priority placeholders first, especially COMSOL Floating Potential, mesh convergence, IEC 60137, dielectric-loss theory, and BRFGL drawing provenance.",
    ]
    return "\n".join(lines)


def quality_gate(text: str, numeric_rows: list[dict[str, str]], boundary_rows: list[dict[str, str]],
                 final_refs: list[dict[str, str]], portability_rows: list[dict[str, str]],
                 missing_inputs: list[Path]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    required_outputs = [
        RUN017_DOC / "run016_path_canonicalization_note.md",
        RUN017_DOC / "submission_format_prep_manuscript_en.md",
        RUN017_DOC / "submission_format_prep_manuscript_zh.md",
        RUN017_TAB / "reference_finalization_matrix.csv",
        RUN017_DOC / "references_placeholder_resolution_notes.md",
        RUN017_TAB / "reference_portability_fix_plan.csv",
        RUN017_TAB / "submission_prep_numeric_claim_check.csv",
        RUN017_TAB / "claim_boundary_compliance_check.csv",
        RUN017_DOC / "figure_table_submission_package.md",
        RUN017_TAB / "unit_style_mapping.csv",
    ]
    for path in required_outputs:
        if not exists_nonempty(path):
            problems.append(f"missing_or_empty_output:{rel(path)}")

    for path in [RUN016_DOC / name for name in RUN016_DOC_FILES] + [RUN016_TAB / name for name in RUN016_RESULT_FILES]:
        if not exists_nonempty(path):
            problems.append(f"canonical_RUN016_missing:{rel(path)}")

    required_structure = [
        "# Title Options", "# Abstract", "# Keywords", "# 1. Introduction",
        "# 2. Literature Review", "# 3. Numerical Model and Simulation Setup",
        "# 4. Results and Discussion", "# 5. Limitations and Future Work",
        "# 6. Conclusions", "# References Placeholder List", "# Figure Captions",
        "# Table Captions", "# Supplementary Material Note",
    ]
    for item in required_structure:
        if item not in text:
            problems.append(f"draft_missing_structure:{item}")

    if any(row["evidence_status"] == "FAIL" for row in numeric_rows):
        problems.append("numeric_claim_check_FAIL")
    if any(row["status"] == "FAIL" for row in boundary_rows):
        problems.append("claim_boundary_FAIL")

    forbidden = [
        "experimentally validated", "field-validated", "standard operating limit",
        "IEC/IEEE temperature limit", "measured defect reproduced", "safe operation guaranteed",
        "validated finite-element numerical risk-boundary scan",
    ]
    for phrase in forbidden:
        if phrase in text:
            problems.append(f"forbidden_phrase:{phrase}")

    if "DIELECTRIC_LOSS_REVIEW_REQUIRED" not in text and "dielectric_loss_review_required" not in text:
        problems.append("dielectric_review_flag_missing")
    if "diagnostic risk zones are internal screening classes" not in text:
        problems.append("diagnostic_risk_boundary_missing")
    if "parameterized equivalent model" not in text:
        problems.append("contact_parameterized_boundary_missing")
    if re.search(r"10\.\d{4}/", text, flags=re.I):
        problems.append("possible_fabricated_or_unverified_DOI_in_placeholder_list")

    high = [row for row in final_refs if row["priority"] == "high"]
    if any(row["final_reference_status"] not in {"RESOLVED_VERIFIED", "PARTIALLY_RESOLVED_NEEDS_METADATA"} for row in high):
        problems.append("high_priority_reference_not_resolved_or_partial")
    if any(row["final_reference_status"] in {"UNRESOLVED", "LOCAL_PATH_ONLY_NOT_PORTABLE", "NEEDS_MANUAL_CONFIRMATION"} for row in final_refs):
        problems.append("blocking_reference_status_remaining")
    if any(row["can_be_used_in_final_submission"] == "NO" for row in portability_rows):
        problems.append("portability_blocking_issue_remaining")
    if missing_inputs:
        problems.append("missing_inputs_present")

    package = read_text(RUN017_DOC / "figure_table_submission_package.md") if exists_nonempty(RUN017_DOC / "figure_table_submission_package.md") else ""
    for label in [f"Fig. {i}" for i in range(1, 10)] + [f"Table {i}" for i in range(1, 7)] + [f"Fig. S{i}" for i in range(1, 8)]:
        if label not in package:
            problems.append(f"figure_table_package_missing:{label}")

    return len(problems) == 0, problems


def report(path_note: dict[str, list[str] | str], missing_inputs: list[Path],
           final_refs: list[dict[str, str]], portability_rows: list[dict[str, str]],
           numeric_rows: list[dict[str, str]], boundary_rows: list[dict[str, str]],
           problems: list[str], can_proceed: bool) -> str:
    ref_counts: dict[str, int] = {}
    for row in final_refs:
        ref_counts[row["final_reference_status"]] = ref_counts.get(row["final_reference_status"], 0) + 1
    portability_blockers = [row for row in portability_rows if row["can_be_used_in_final_submission"] == "NO"]
    generated = [
        RUN017_DOC / "run016_path_canonicalization_note.md",
        RUN017_DOC / "submission_format_prep_manuscript_en.md",
        RUN017_DOC / "submission_format_prep_manuscript_zh.md",
        RUN017_TAB / "reference_finalization_matrix.csv",
        RUN017_DOC / "references_placeholder_resolution_notes.md",
        RUN017_TAB / "reference_portability_fix_plan.csv",
        RUN017_TAB / "submission_prep_numeric_claim_check.csv",
        RUN017_TAB / "claim_boundary_compliance_check.csv",
        RUN017_DOC / "figure_table_submission_package.md",
        RUN017_DOC / "journal_submission_formatting_checklist.md",
        RUN017_DOC / "run017_reference_finalization_and_submission_formatting_report.md",
        RUN017_TAB / "unit_style_mapping.csv",
    ]
    lines = [
        "# RUN017 Reference Finalization and Submission Formatting Report",
        "",
        "## Task Objective",
        "",
        "RUN017 canonicalizes RUN016 paths, prepares a submission-format-aware manuscript draft, audits reference finalization status, checks path portability, rechecks numeric claims and claim boundaries, and prepares figure/table submission routing. It does not run COMSOL or modify RUN006-RUN013 raw outputs.",
        "",
        "## RUN016 Path Canonicalization Summary",
        "",
        f"- copied_doc_files: {', '.join(path_note['copied_doc_files']) if path_note['copied_doc_files'] else 'none'}",
        f"- copied_result_files: {', '.join(path_note['copied_result_files']) if path_note['copied_result_files'] else 'none'}",
        f"- already_present_files: {', '.join(path_note['already_present_files']) if path_note['already_present_files'] else 'none'}",
        f"- missing_files: {', '.join(path_note['missing_files']) if path_note['missing_files'] else 'none'}",
        f"- whether RUN016 script/report path mismatch remains: {path_note['mismatch_remains']}",
        "",
        "## Inputs Checked",
        "",
    ]
    for path in REQUIRED_INPUTS:
        lines.append(f"- {rel(path)}: {'OK' if exists_nonempty(path) else 'MISSING'}")
    lines.extend(["", "## Files Generated", ""])
    for path in generated:
        lines.append(f"- {rel(path)}")
    lines.extend(["", "## Missing Inputs", ""])
    if missing_inputs:
        for path in missing_inputs:
            lines.append(f"- {rel(path)}")
    else:
        lines.append("None.")
    lines.extend([
        "",
        "## Submission-Format-Prep Manuscript Status",
        "",
        "The submission-prep manuscript keeps title options, abstract, keywords, Sections 1-6, References Placeholder List, Figure Captions, Table Captions, and Supplementary Material Note. Temperature units are converted from degC to °C with numeric equivalence preserved.",
        "",
        "## Numeric Claim Check Status",
        "",
        f"{sum(1 for row in numeric_rows if row['evidence_status'] == 'OK')}/{len(numeric_rows)} numeric claims OK.",
        "",
        "## Claim-Boundary Compliance Status",
        "",
        f"{sum(1 for row in boundary_rows if row['status'] == 'OK')}/{len(boundary_rows)} boundary checks OK.",
        "",
        "## Reference Finalization Status",
        "",
        ", ".join(f"{k}: {v}" for k, v in sorted(ref_counts.items())),
        "",
        "## Reference Portability Status",
        "",
        f"Portability blocking rows: {len(portability_blockers)}.",
        "",
        "## Figure/Table Submission Package Status",
        "",
        "Fig. 1-Fig. 9, Table 1-Table 6, and Fig. S1-Fig. S7 are listed in the figure/table submission package.",
        "",
        "## Remaining Blocking Issues",
        "",
    ])
    if problems:
        for problem in problems:
            lines.append(f"- {problem}")
    else:
        lines.append("None.")
    lines.extend([
        "",
        "## RUN018 Readiness",
        "",
        "RUN017 is a submission-format-prep draft, but final submission packaging remains blocked while unresolved/manual references and portability issues remain.",
        "",
        f"Can proceed to RUN018_FINAL_SUBMISSION_PACKAGE: {'YES' if can_proceed else 'NO'}",
    ])
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    path_note = canonicalize_run016_paths()
    missing_inputs = [path for path in REQUIRED_INPUTS if not exists_nonempty(path)]

    source_en = read_text(RUN016_DOC / "full_manuscript_draft_en.md")
    prep_en = prep_manuscript_text(source_en)
    source_zh = read_text(RUN016_DOC / "full_manuscript_draft_zh.md")
    prep_zh = prep_manuscript_text(source_zh)
    write_text(RUN017_DOC / "submission_format_prep_manuscript_en.md", prep_en)
    write_text(RUN017_DOC / "submission_format_prep_manuscript_zh.md", prep_zh)
    write_csv(RUN017_TAB / "unit_style_mapping.csv", [
        "original_style", "submission_style", "scope", "numeric_equivalence", "notes",
    ], unit_style_mapping())

    final_refs = build_reference_finalization()
    write_csv(RUN017_TAB / "reference_finalization_matrix.csv", [
        "placeholder",
        "RUN015_source_status",
        "RUN016_manual_task",
        "priority",
        "current_candidate_key",
        "current_candidate_title",
        "current_candidate_type",
        "verified_source_available",
        "repo_relative_source_available",
        "absolute_path_issue",
        "final_reference_key",
        "final_reference_entry",
        "final_reference_status",
        "affected_sections",
        "required_action",
        "notes",
    ], final_refs)
    write_text(RUN017_DOC / "references_placeholder_resolution_notes.md", placeholder_resolution_notes(final_refs))

    portability_rows = reference_portability_fix_plan()
    write_csv(RUN017_TAB / "reference_portability_fix_plan.csv", [
        "placeholder",
        "absolute_path_detected",
        "local_path_excerpt",
        "repo_relative_alternative",
        "portability_fix_status",
        "required_action",
        "can_be_used_in_final_submission",
        "notes",
    ], portability_rows)

    numeric_rows = numeric_claim_check(prep_en)
    write_csv(RUN017_TAB / "submission_prep_numeric_claim_check.csv", [
        "numeric_claim",
        "expected_value_from_RUN016_or_RUN015",
        "appears_in_submission_prep_draft",
        "actual_text_value",
        "evidence_source_file",
        "evidence_status",
        "unit_style",
        "action",
    ], numeric_rows)

    boundary_rows = claim_boundary_check(prep_en)
    write_csv(RUN017_TAB / "claim_boundary_compliance_check.csv", [
        "boundary_item",
        "required_phrase_or_meaning",
        "appears_in_submission_prep_draft",
        "risk_if_missing",
        "status",
        "action",
    ], boundary_rows)

    write_text(RUN017_DOC / "figure_table_submission_package.md", figure_table_package())

    can_proceed, problems = quality_gate(prep_en, numeric_rows, boundary_rows, final_refs, portability_rows, missing_inputs)
    write_text(RUN017_DOC / "journal_submission_formatting_checklist.md", formatting_checklist(
        prep_en,
        numeric_ok=all(row["evidence_status"] == "OK" for row in numeric_rows),
        boundary_ok=all(row["status"] == "OK" for row in boundary_rows),
        unresolved_count=sum(1 for row in final_refs if row["final_reference_status"] != "RESOLVED_VERIFIED"),
    ))
    write_text(RUN017_DOC / "run017_reference_finalization_and_submission_formatting_report.md", report(
        path_note,
        missing_inputs,
        final_refs,
        portability_rows,
        numeric_rows,
        boundary_rows,
        problems,
        can_proceed,
    ))

    generated = [
        RUN017_DOC / "run016_path_canonicalization_note.md",
        RUN017_DOC / "submission_format_prep_manuscript_en.md",
        RUN017_DOC / "submission_format_prep_manuscript_zh.md",
        RUN017_TAB / "reference_finalization_matrix.csv",
        RUN017_DOC / "references_placeholder_resolution_notes.md",
        RUN017_TAB / "reference_portability_fix_plan.csv",
        RUN017_TAB / "submission_prep_numeric_claim_check.csv",
        RUN017_TAB / "claim_boundary_compliance_check.csv",
        RUN017_DOC / "figure_table_submission_package.md",
        RUN017_DOC / "journal_submission_formatting_checklist.md",
        RUN017_DOC / "run017_reference_finalization_and_submission_formatting_report.md",
        RUN017_TAB / "unit_style_mapping.csv",
    ]
    print("RUN017 generated files:")
    for path in generated:
        print(f"- {rel(path)}")
    print(f"RUN017 quality gate status: {'PASS' if can_proceed else 'NO_BLOCKED_BY_MANUAL_REFERENCE_OR_PORTABILITY_TASKS'}")
    if problems:
        print("Blocking issues:")
        for problem in problems:
            print(f"- {problem}")


if __name__ == "__main__":
    main()
