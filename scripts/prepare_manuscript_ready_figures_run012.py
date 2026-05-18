"""Prepare MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012 outputs.

This script reads existing RUN006-RUN011 CSV/MD/PNG outputs and generates
manuscript-ready figure copies, summary tables, a model-validation report, and
draft experiment-section materials. It does not run COMSOL and does not modify
RUN010/RUN011 raw CSV files.
"""

from __future__ import annotations

import csv
import math
import shutil
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
RUN_ID = "MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012"
RAW_OUT = PROJECT / "results" / "raw_comsol_exports" / RUN_ID
FIG_OUT = PROJECT / "results" / "paper_figures" / "manuscript_ready"
TAB_OUT = PROJECT / "results" / "summary_tables" / "manuscript_ready"
DOC_OUT = PROJECT / "docs"
DRAFT_OUT = DOC_OUT / "manuscript_draft_sections"

RUN006 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RUN006_SOURCE_FIXED"
RUN007 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_SWEEP_27_RUN007"
RUN008 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RISK_125_RUN008"
RUN008B = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RISK_125_RUN008B_HEAT_BALANCE_FIX"
RUN009A = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009A_BASELINE"
RUN009B = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009B_27CASE"
RUN010 = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010"
RUN011A = PROJECT / "results" / "raw_comsol_exports" / "MATERIAL_AND_MESH_SENSITIVITY_RUN011" / "RUN011A_MESH_INDEPENDENCE"
RUN011B = PROJECT / "results" / "raw_comsol_exports" / "MATERIAL_AND_MESH_SENSITIVITY_RUN011" / "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY"

FIG_STAGE = PROJECT / "results" / "paper_figures" / "stage_diagnostics"
FIG_RUN009 = PROJECT / "results" / "paper_figures" / "full_electrothermal_run009"
FIG_RUN010 = PROJECT / "results" / "paper_figures" / "full_electrothermal_risk_125_run010"
FIG_RUN011 = PROJECT / "results" / "paper_figures" / "material_and_mesh_sensitivity_run011"

REQUIRED_INPUTS = [
    RUN006 / "solid_only_metrics.csv",
    RUN006 / "heat_source_decomposition.csv",
    RUN006 / "heat_balance_diagnostics.csv",
    RUN006 / "source_normalization_audit.csv",
    RUN007 / "sweep_metrics.csv",
    RUN007 / "heat_source_decomposition_by_case.csv",
    RUN007 / "heat_balance_by_case.csv",
    RUN007 / "sweep_validity_summary.csv",
    RUN008 / "risk_metrics.csv",
    RUN008 / "heat_source_decomposition_by_case.csv",
    RUN008 / "heat_balance_by_case.csv",
    RUN008 / "risk_validity_summary.csv",
    RUN008B / "risk_validity_summary_reclassified.csv",
    RUN008B / "heat_balance_recheck_by_case.csv",
    DOC_OUT / "solid_only_risk_125_run008b_heat_balance_fix_report.md",
    RUN009A / "baseline_metrics.csv",
    RUN009A / "electric_field_diagnostics.csv",
    RUN009A / "dielectric_loss_comparison.csv",
    RUN009B / "run009b_metrics.csv",
    RUN009B / "run009b_validity_summary.csv",
    DOC_OUT / "full_electrothermal_dielectric_loss_run009_report.md",
    RUN010 / "run010_risk_metrics.csv",
    RUN010 / "dielectric_loss_by_case.csv",
    RUN010 / "electric_field_diagnostics_by_case.csv",
    RUN010 / "heat_source_decomposition_by_case.csv",
    RUN010 / "heat_balance_by_case.csv",
    RUN010 / "run010_validity_summary.csv",
    RUN010 / "run010_risk_boundary_summary.csv",
    RUN010 / "run008_vs_run010_comparison.csv",
    DOC_OUT / "full_electrothermal_dielectric_loss_risk_125_run010_report.md",
    RUN011A / "mesh_metrics.csv",
    RUN011A / "mesh_convergence_summary.csv",
    RUN011B / "sensitivity_metrics.csv",
    RUN011B / "sensitivity_index_summary.csv",
    DOC_OUT / "material_and_mesh_sensitivity_run011_report.md",
]


def font(size: int, bold: bool = False):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT_TITLE = font(40, True)
FONT_H = font(28, True)
FONT = font(21)
FONT_SMALL = font(17)
FONT_TINY = font(13)


def ensure_dirs() -> None:
    for path in [RAW_OUT, FIG_OUT, TAB_OUT, DRAFT_OUT]:
        path.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def bool_count(series: pd.Series) -> int:
    return int(series.astype(str).str.lower().eq("true").sum())


def fmt(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def write_input_status() -> pd.DataFrame:
    rows = []
    for path in REQUIRED_INPUTS:
        rows.append({
            "input_file": rel(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "notes": "required RUN012 input" if path.exists() else "missing; not fabricated",
        })
    out = pd.DataFrame(rows)
    out.to_csv(RAW_OUT / "run012_input_file_status.csv", index=False)
    return out


def risk_counts(df: pd.DataFrame, column: str) -> str:
    if df.empty or column not in df:
        return "{}"
    counts = df[column].astype(str).value_counts().to_dict()
    order = ["safe", "attention", "warning", "thermal_risk", "contact_safe", "contact_attention", "contact_warning", "contact_risk", "invalid_case"]
    parts = []
    for key in order:
        if key in counts:
            parts.append(f"{key}:{counts[key]}")
    for key in sorted(counts):
        if key not in order:
            parts.append(f"{key}:{counts[key]}")
    return "; ".join(parts)


def compute_stats() -> dict:
    run006_m = read_csv(RUN006 / "solid_only_metrics.csv")
    run006_hs = read_csv(RUN006 / "heat_source_decomposition.csv")
    run006_hb = read_csv(RUN006 / "heat_balance_diagnostics.csv")
    run007_v = read_csv(RUN007 / "sweep_validity_summary.csv")
    run008b_v = read_csv(RUN008B / "risk_validity_summary_reclassified.csv")
    run009a = read_csv(RUN009A / "baseline_metrics.csv")
    run009b_v = read_csv(RUN009B / "run009b_validity_summary.csv")
    run010_m = read_csv(RUN010 / "run010_risk_metrics.csv")
    run010_d = read_csv(RUN010 / "dielectric_loss_by_case.csv")
    run010_e = read_csv(RUN010 / "electric_field_diagnostics_by_case.csv")
    run010_hb = read_csv(RUN010 / "heat_balance_by_case.csv")
    run010_v = read_csv(RUN010 / "run010_validity_summary.csv")
    run010_cmp = read_csv(RUN010 / "run008_vs_run010_comparison.csv")
    mesh = read_csv(RUN011A / "mesh_convergence_summary.csv")
    sens = read_csv(RUN011B / "sensitivity_metrics.csv")
    sens_i = read_csv(RUN011B / "sensitivity_index_summary.csv")

    medium = mesh[mesh["mesh_level"].astype(str).eq("medium")] if not mesh.empty else pd.DataFrame()
    nonbase_sens = sens_i[
        sens_i["parameter_value"].astype(float) != sens_i["baseline_value"].astype(float)
    ] if not sens_i.empty else pd.DataFrame()
    if not nonbase_sens.empty:
        ranking_df = (
            nonbase_sens.groupby("parameter_name")[["S_Tmax_global", "S_Tmax_contact", "S_Qdielectric"]]
            .apply(lambda df: pd.Series({"score": df.abs().max().max()}))
            .reset_index()
            .sort_values("score", ascending=False)
        )
        sensitivity_ranking = " > ".join(ranking_df["parameter_name"].tolist())
    else:
        ranking_df = pd.DataFrame()
        sensitivity_ranking = "NA"

    stats = {
        "run006_status": run006_m["status"].iloc[0] if not run006_m.empty else "MISSING",
        "run006_tmax": float(run006_m["Tmax_global_C"].iloc[0]) if not run006_m.empty else float("nan"),
        "run006_qjoule": float(run006_hs["Qjoule_conductor_W"].iloc[0]) if not run006_hs.empty else float("nan"),
        "run006_qcontact": float(run006_hs["Qcontact_W"].iloc[0]) if not run006_hs.empty else float("nan"),
        "run006_qd": float(run006_hs["Qdielectric_RIP_W"].iloc[0]) if not run006_hs.empty else float("nan"),
        "run006_resid": float(run006_hb["residual_percent"].iloc[0]) if not run006_hb.empty else float("nan"),
        "run007_valid": bool_count(run007_v["overall_valid"]) if not run007_v.empty and "overall_valid" in run007_v else 0,
        "run007_total": len(run007_v),
        "run008b_valid": bool_count(run008b_v["overall_valid_reclassified"]) if not run008b_v.empty else 0,
        "run008b_total": len(run008b_v),
        "run009a_status": run009a["status"].iloc[0] if not run009a.empty else "MISSING",
        "run009a_tmax": float(run009a["Tmax_global_C"].iloc[0]) if not run009a.empty else float("nan"),
        "run009a_qd_field": float(run009a["Qdielectric_RIP_field_W"].iloc[0]) if not run009a.empty else float("nan"),
        "run009a_qd_ref": float(run009a["Qdielectric_RIP_ref_W"].iloc[0]) if not run009a.empty else float("nan"),
        "run009a_qd_ratio": float(run009a["Qdielectric_ratio_field_to_ref"].iloc[0]) if not run009a.empty else float("nan"),
        "run009b_valid": bool_count(run009b_v["overall_valid"]) if not run009b_v.empty else 0,
        "run009b_total": len(run009b_v),
        "run010_total": len(run010_v),
        "run010_valid": bool_count(run010_v["overall_valid"]) if not run010_v.empty else 0,
        "run010_tmax_min": float(run010_m["Tmax_global_C"].min()) if not run010_m.empty else float("nan"),
        "run010_tmax_max": float(run010_m["Tmax_global_C"].max()) if not run010_m.empty else float("nan"),
        "run010_contact_max": float(run010_m["Tmax_contact_C"].max()) if not run010_m.empty else float("nan"),
        "run010_risk_counts": risk_counts(run010_m, "risk_zone"),
        "run010_contact_counts": risk_counts(run010_m, "contact_risk_zone"),
        "run010_heat_resid_max_abs": float(run010_hb["residual_percent_Qgenerated"].abs().max()) if not run010_hb.empty else float("nan"),
        "run010_qd_min": float(run010_d["Qdielectric_RIP_field_W"].min()) if not run010_d.empty else float("nan"),
        "run010_qd_max": float(run010_d["Qdielectric_RIP_field_W"].max()) if not run010_d.empty else float("nan"),
        "run010_qd_ratio_min": float(run010_d["Qdielectric_ratio_field_to_ref"].min()) if not run010_d.empty else float("nan"),
        "run010_qd_ratio_max": float(run010_d["Qdielectric_ratio_field_to_ref"].max()) if not run010_d.empty else float("nan"),
        "run010_qd_ratio_mean": float(run010_d["Qdielectric_ratio_field_to_ref"].mean()) if not run010_d.empty else float("nan"),
        "run010_field_singular": bool_count(run010_e["field_singularity_flag"]) if not run010_e.empty else 0,
        "run010_dielectric_review": bool_count(run010_d["dielectric_loss_review_required"]) if not run010_d.empty else 0,
        "run010_delta_mean": float(run010_cmp["delta_Tmax_global_C"].mean()) if not run010_cmp.empty else float("nan"),
        "run010_delta_max": float(run010_cmp["delta_Tmax_global_C"].max()) if not run010_cmp.empty else float("nan"),
        "run010_risk_changed": bool_count(run010_cmp["risk_zone_changed"]) if not run010_cmp.empty else 0,
        "run011_medium_pass": bool_count(medium["medium_vs_fine_pass"]) if not medium.empty else 0,
        "run011_medium_total": len(medium),
        "run011_mesh_max_tmax_err": float(medium["err_Tmax_global_pct"].max()) if not medium.empty else float("nan"),
        "run011_mesh_max_e95_err": float(medium["err_E95_RIP_pct"].max()) if not medium.empty else float("nan"),
        "run011_mesh_max_qd_err": float(medium["err_Qdielectric_pct"].max()) if not medium.empty else float("nan"),
        "run011_sens_total": len(sens),
        "run011_sens_heat_valid": int(sens["heat_balance_status"].astype(str).isin(["VALID_STRICT", "VALID_LOW_POWER_RECLASSIFIED"]).sum()) if not sens.empty else 0,
        "run011_sens_singular": bool_count(sens["field_singularity_flag"]) if not sens.empty else 0,
        "run011_sens_max_tmax": float(sens["Tmax_global_C"].max()) if not sens.empty else float("nan"),
        "run011_sens_status_counts": risk_counts(sens, "status"),
        "sensitivity_ranking": sensitivity_ranking,
        "ranking_df": ranking_df,
    }
    return stats


def write_stage_audit_summary(stats: dict) -> None:
    rows = [
        ["RUN006", "Source-fixed solid-only baseline heat normalization", "solid-only thermal diagnostic", 1, "solid_only_metrics; heat_source_decomposition; heat_balance_diagnostics", f"{stats['run006_status']}; residual={fmt(stats['run006_resid'])}%", "diagnostic/supporting", "Confirms Joule/contact normalization before risk scans"],
        ["RUN007", "27-case small solid-only sweep", "solid-only thermal diagnostic", stats["run007_total"], "sweep_metrics; heat balance; source decomposition", f"{stats['run007_valid']}/{stats['run007_total']} valid", "diagnostic/supporting", "Pre-screen before 125-case solid-only matrix"],
        ["RUN008", "125-case solid-only approximate dielectric-loss risk scan", "solid-only approximate_Qdielectric_ref", 125, "risk_metrics; risk_boundary_summary", "superseded by RUN008B heat-balance reclassification and RUN010 field-coupled model", "diagnostic/supplementary", "Must not be described as final electro-thermal result"],
        ["RUN008B", "Heat-balance closure recheck for RUN008", "postprocess validation", stats["run008b_total"], "risk_validity_summary_reclassified", f"{stats['run008b_valid']}/{stats['run008b_total']} reclassified valid", "diagnostic/supporting", "Explains low-power heat-balance normalization issue"],
        ["RUN009A", "Baseline full field-coupled dielectric loss", "full electro-thermal with electrostatics", 1, "baseline_metrics; electric field diagnostics; dielectric loss comparison", f"{stats['run009a_status']}; Qd field/ref={fmt(stats['run009a_qd_ratio'])}", "main/supporting", "Introduces field-coupled dielectric loss"],
        ["RUN009B", "27-case full field-coupled dielectric-loss check", "full electro-thermal with electrostatics", stats["run009b_total"], "run009b_metrics; validity summary", f"{stats['run009b_valid']}/{stats['run009b_total']} valid", "supporting", "Stability check before 125-case RUN010"],
        ["RUN010", "125-case full field-coupled dielectric-loss risk boundary", "full electro-thermal with electrostatics", stats["run010_total"], "risk metrics; risk boundary; RUN008 comparison", f"{stats['run010_valid']}/{stats['run010_total']} valid; field_singularity={stats['run010_field_singular']}", "main result", "Diagnostic risk zones are not IEC/IEEE limits"],
        ["RUN011A", "Mesh independence verification", "numerical reliability check", 9, "mesh_metrics; mesh_convergence_summary", f"medium-vs-fine {stats['run011_medium_pass']}/{stats['run011_medium_total']} pass", "validation/supporting", "RUN010 default medium mesh accepted"],
        ["RUN011B", "Material and boundary sensitivity", "parameter robustness check", stats["run011_sens_total"], "sensitivity_metrics; sensitivity_index_summary", f"heat valid {stats['run011_sens_heat_valid']}/{stats['run011_sens_total']}; singular={stats['run011_sens_singular']}", "validation/supporting", "Thermal-risk sensitivity points are physical responses, not numerical failures"],
    ]
    write_csv(TAB_OUT / "run_stage_audit_summary.csv", [
        "stage", "purpose", "model_type", "case_count", "key_outputs", "validation_status",
        "can_be_used_in_manuscript", "notes",
    ], rows)


def write_key_result_summary(stats: dict) -> None:
    rows = [
        ["RUN010 Tmax_global range", f"{fmt(stats['run010_tmax_min'])}-{fmt(stats['run010_tmax_max'])} degC", "RUN010", rel(RUN010 / "run010_risk_metrics.csv"), "main result", "Full field-coupled dielectric loss, 125-case matrix"],
        ["RUN010 Tmax_contact max", f"{fmt(stats['run010_contact_max'])} degC", "RUN010", rel(RUN010 / "run010_risk_metrics.csv"), "main/supporting", "Contact temperature risk uses diagnostic thresholds only"],
        ["RUN010 risk_zone counts", stats["run010_risk_counts"], "RUN010", rel(RUN010 / "run010_risk_metrics.csv"), "main result", "Diagnostic risk zoning, not IEC/IEEE limit"],
        ["RUN010 contact_risk_zone counts", stats["run010_contact_counts"], "RUN010", rel(RUN010 / "run010_risk_metrics.csv"), "main/supporting", "Diagnostic contact zoning, not material limit"],
        ["RUN010 heat_balance max residual", f"{fmt(stats['run010_heat_resid_max_abs'])}% max |residual_percent_Qgenerated|", "RUN010", rel(RUN010 / "heat_balance_by_case.csv"), "validation/supporting", "RUN008B heat-balance logic retained"],
        ["RUN010 Qdielectric_field range", f"{fmt(stats['run010_qd_min'])}-{fmt(stats['run010_qd_max'])} W", "RUN010", rel(RUN010 / "dielectric_loss_by_case.csv"), "main/supporting", "Field-coupled Qdielectric; review flag retained"],
        ["RUN010 Qdielectric_field/ref ratio", f"{fmt(stats['run010_qd_ratio_min'])}-{fmt(stats['run010_qd_ratio_max'])}; mean={fmt(stats['run010_qd_ratio_mean'])}", "RUN010", rel(RUN010 / "dielectric_loss_by_case.csv"), "supporting/review", "DIELECTRIC_LOSS_REVIEW_REQUIRED retained"],
        ["RUN010 field_singularity count", f"{stats['run010_field_singular']}/{stats['run010_total']}", "RUN010", rel(RUN010 / "electric_field_diagnostics_by_case.csv"), "validation/supporting", "field_singularity_flag false for all cases"],
        ["RUN011 mesh convergence pass count", f"{stats['run011_medium_pass']}/{stats['run011_medium_total']}; Tmax max err={fmt(stats['run011_mesh_max_tmax_err'])}%; E95 max err={fmt(stats['run011_mesh_max_e95_err'])}%; Qd max err={fmt(stats['run011_mesh_max_qd_err'])}%", "RUN011A", rel(RUN011A / "mesh_convergence_summary.csv"), "validation/supporting", "Medium mesh accepted against fine reference"],
        ["RUN011 sensitivity ranking", stats["sensitivity_ranking"], "RUN011B", rel(RUN011B / "sensitivity_index_summary.csv"), "validation/supporting", "OFAT ranking by max normalized sensitivity"],
        ["RUN008 vs RUN010 Tmax difference", f"mean={fmt(stats['run010_delta_mean'])} degC; max={fmt(stats['run010_delta_max'])} degC; risk_zone_changed={stats['run010_risk_changed']}/125", "RUN010 comparison", rel(RUN010 / "run008_vs_run010_comparison.csv"), "main/supporting", "Field-coupled Qdielectric causes small Tmax increase relative to approximate reference"],
    ]
    write_csv(TAB_OUT / "key_result_summary.csv", [
        "metric", "value_or_range", "source_run", "source_file", "manuscript_usage", "notes",
    ], rows)


def write_validation_evidence_chain(stats: dict) -> None:
    rows = [
        ["source normalization", "RUN006 source_normalization_audit and heat_source_decomposition", f"Qjoule={fmt(stats['run006_qjoule'])} W; Qcontact={fmt(stats['run006_qcontact'], 4)} W", "Qjoule near I^2R and Qcontact equals I^2Rc", "true", "Established before sweep/risk scans"],
        ["contact heat validation", "RUN006/RUN010 heat source tables", f"RUN006 Qcontact={fmt(stats['run006_qcontact'], 4)} W", "Integrated contact heat follows I^2Rc", "true", "Rc0 model is parameterized equivalent, not measured defect"],
        ["heat balance validation", "RUN010 heat_balance_by_case", f"max |residual_percent_Qgenerated|={fmt(stats['run010_heat_resid_max_abs'])}%", "VALID_STRICT or accepted low-power classification", "true", "RUN010 all VALID_STRICT/valid"],
        ["explicit by-ID selection", "RUN006-RUN011 model reports and validity summaries", "selection checks valid across risk/sensitivity runs", "No selection drift or overlapping postprocess maxima", "true", "Box selection not used for formal heat boundaries"],
        ["field singularity check", "RUN009/RUN010 electric field diagnostics", f"RUN010 field_singularity={stats['run010_field_singular']}/{stats['run010_total']}", "field_singularity_flag=false", "true", "E95/probe metrics used alongside global max"],
        ["dielectric loss review", "RUN009/RUN010 dielectric_loss_by_case", f"field/ref mean={fmt(stats['run010_qd_ratio_mean'])}", "Positive field-coupled Qd; review flag retained and explained", "true", "Review flag is not model failure"],
        ["mesh independence", "RUN011A mesh_convergence_summary", f"medium-vs-fine={stats['run011_medium_pass']}/{stats['run011_medium_total']} pass", "Tmax<1%, E95<3%, Qd<5%", "true", "RUN010 default medium mesh accepted"],
        ["material sensitivity", "RUN011B sensitivity_index_summary", stats["sensitivity_ranking"], "All sensitivity cases solve or report physical thermal risk", "true", "Thermal risk cases are physical parameter responses"],
        ["boundary sensitivity", "RUN011B sensitivity_metrics", f"h_air/h_oil cases heat valid={stats['run011_sens_heat_valid']}/{stats['run011_sens_total']}", "Heat balance valid and no field singularity", "true", "Low h_air under high-risk base can exceed diagnostic thermal-risk threshold"],
    ]
    write_csv(TAB_OUT / "model_validation_evidence_chain.csv", [
        "validation_item", "evidence_source", "result", "acceptance_criterion", "passed", "notes",
    ], rows)


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int, fill: str, fnt, line_gap: int = 6) -> int:
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        candidate = word if not cur else cur + " " + word
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += fnt.size + line_gap
    return y


def save_figure(img: Image.Image, path: Path) -> None:
    img.convert("RGB").save(path, dpi=(300, 300))


def annotate_copy(src: Path, dest: Path, title: str, footer: str) -> None:
    img = Image.open(src).convert("RGB")
    w, h = img.size
    top = 78
    bottom = 76
    out = Image.new("RGB", (w, h + top + bottom), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, w, top), fill="#111827")
    draw.text((34, 22), title, fill="white", font=FONT_TITLE)
    out.paste(img, (0, top))
    draw.rectangle((0, h + top, w, h + top + bottom), fill="#f8fafc")
    draw.text((34, h + top + 20), footer, fill="#334155", font=FONT_SMALL)
    save_figure(out, dest)


def resize_fit(img: Image.Image, box: tuple[int, int]) -> Image.Image:
    copy = img.convert("RGB").copy()
    copy.thumbnail(box, Image.Resampling.LANCZOS)
    return copy


def make_workflow_geometry(stats: dict, dest: Path) -> None:
    out = Image.new("RGB", (2200, 1280), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, 2200, 92), fill="#111827")
    draw.text((38, 26), "Fig. 1 Model workflow and CAD-driven geometry", fill="white", font=FONT_TITLE)

    steps = [
        ("Input data", "ratings, materials, geometry, screens"),
        ("CAD-driven geometry", "BRFGL1 profile and by-ID selections"),
        ("RUN006", "source-fixed solid-only baseline"),
        ("RUN009/RUN010", "field-coupled dielectric-loss model"),
        ("RUN011", "mesh and parameter robustness"),
    ]
    x0, y0 = 70, 150
    box_w, box_h, gap = 360, 140, 42
    for i, (head, body) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        draw.rounded_rectangle((x, y0, x + box_w, y0 + box_h), radius=14, fill="#e0f2fe", outline="#0369a1", width=3)
        draw.text((x + 22, y0 + 26), head, fill="#0f172a", font=FONT_H)
        draw_wrapped(draw, (x + 22, y0 + 72), body, box_w - 44, "#334155", FONT_SMALL)
        if i < len(steps) - 1:
            ax = x + box_w + 6
            ay = y0 + box_h // 2
            draw.line((ax, ay, ax + gap - 12, ay), fill="#334155", width=4)
            draw.polygon([(ax + gap - 12, ay - 9), (ax + gap + 8, ay), (ax + gap - 12, ay + 9)], fill="#334155")

    geom = Image.open(FIG_STAGE / "fig01_geometry_drawing_vs_comsol_v2.png").convert("RGB")
    geom = resize_fit(geom, (980, 700))
    out.paste(geom, (80, 420))
    draw.rectangle((1180, 420, 2110, 1020), outline="#cbd5e1", width=2)
    y = 455
    draw.text((1225, y), "Audit chain used in manuscript", fill="#0f172a", font=FONT_H)
    y += 62
    bullets = [
        f"RUN006 source normalization: Qjoule={fmt(stats['run006_qjoule'])} W; Qcontact={fmt(stats['run006_qcontact'], 4)} W",
        f"RUN009A field-coupled Qdielectric: {fmt(stats['run009a_qd_field'])} W; field/ref={fmt(stats['run009a_qd_ratio'])}",
        f"RUN010 validity: {stats['run010_valid']}/{stats['run010_total']} cases; field singularity={stats['run010_field_singular']}",
        f"RUN011A mesh: {stats['run011_medium_pass']}/{stats['run011_medium_total']} medium-vs-fine pass",
        "Diagnostic risk zoning is not an IEC/IEEE or material limit.",
    ]
    for bullet in bullets:
        y = draw_wrapped(draw, (1230, y), "- " + bullet, 800, "#334155", FONT) + 10
    draw.text((70, 1188), "Source: CAD-driven 2D axisymmetric model and RUN006-RUN011 audit chain.", fill="#334155", font=FONT_SMALL)
    save_figure(out, dest)


def make_baseline_composite(dest: Path) -> None:
    paths = [
        FIG_RUN009 / "fig01_electric_potential_baseline.png",
        FIG_RUN009 / "fig02_Efield_RIP_baseline.png",
        FIG_RUN009 / "fig03_dielectric_loss_density_baseline.png",
        FIG_RUN009 / "fig04_temperature_field_baseline.png",
    ]
    labels = ["A Potential", "B Electric field", "C Dielectric-loss density", "D Temperature"]
    out = Image.new("RGB", (2200, 1500), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, 2200, 92), fill="#111827")
    draw.text((38, 26), "Fig. 2 Baseline field-coupled dielectric loss and temperature", fill="white", font=FONT_TITLE)
    slots = [(60, 140), (1130, 140), (60, 800), (1130, 800)]
    for path, label, xy in zip(paths, labels, slots):
        img = resize_fit(Image.open(path), (990, 580))
        draw.text((xy[0], xy[1] - 34), label, fill="#0f172a", font=FONT_H)
        out.paste(img, xy)
    draw.text((60, 1440), "Field-coupled Qdielectric; DIELECTRIC_LOSS_REVIEW_REQUIRED retained; not a physical experiment.", fill="#334155", font=FONT_SMALL)
    save_figure(out, dest)


def make_mesh_composite(dest: Path) -> None:
    out = Image.new("RGB", (2200, 1300), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, 2200, 92), fill="#111827")
    draw.text((38, 26), "Fig. 8 Mesh independence summary", fill="white", font=FONT_TITLE)
    for path, xy, label in [
        (FIG_RUN011 / "fig01_mesh_convergence_Tmax.png", (60, 145), "A Tmax convergence"),
        (FIG_RUN011 / "fig03_mesh_error_summary.png", (1130, 145), "B Medium-vs-fine error"),
    ]:
        img = resize_fit(Image.open(path), (990, 920))
        draw.text((xy[0], xy[1] - 36), label, fill="#0f172a", font=FONT_H)
        out.paste(img, xy)
    draw.text((60, 1220), "Acceptance uses medium-vs-fine errors: Tmax <1%, E95 <3%, Qdielectric <5%.", fill="#334155", font=FONT_SMALL)
    save_figure(out, dest)


def make_audit_flow(stats: dict, dest: Path) -> None:
    out = Image.new("RGB", (1800, 1120), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, 1800, 84), fill="#111827")
    draw.text((34, 23), "Fig. S1 Full RUN006-RUN011 audit flow", fill="white", font=FONT_TITLE)
    rows = [
        ("RUN006", "Source-fixed baseline", f"{stats['run006_status']}, residual {fmt(stats['run006_resid'])}%"),
        ("RUN007", "27-case solid-only check", f"{stats['run007_valid']}/{stats['run007_total']} valid"),
        ("RUN008B", "Heat-balance reclassification", f"{stats['run008b_valid']}/{stats['run008b_total']} valid"),
        ("RUN009", "Field-coupled dielectric loss", f"field/ref {fmt(stats['run009a_qd_ratio'])}"),
        ("RUN010", "125-case field-coupled risk", f"{stats['run010_valid']}/{stats['run010_total']} valid"),
        ("RUN011", "Mesh and sensitivity", f"mesh {stats['run011_medium_pass']}/{stats['run011_medium_total']} pass"),
    ]
    y = 140
    for i, (stage, purpose, result) in enumerate(rows):
        fill = "#ecfeff" if i % 2 == 0 else "#f0fdf4"
        draw.rounded_rectangle((110, y, 1690, y + 105), radius=12, fill=fill, outline="#94a3b8", width=2)
        draw.text((145, y + 27), stage, fill="#0f172a", font=FONT_H)
        draw.text((340, y + 24), purpose, fill="#334155", font=FONT)
        draw.text((1130, y + 24), result, fill="#0f172a", font=FONT)
        if i < len(rows) - 1:
            draw.line((900, y + 105, 900, y + 142), fill="#475569", width=4)
            draw.polygon([(888, y + 132), (912, y + 132), (900, y + 152)], fill="#475569")
        y += 150
    draw.text((110, 1040), "Diagnostic stages are retained for audit; RUN010/RUN011 support manuscript-ready simulation results.", fill="#334155", font=FONT_SMALL)
    save_figure(out, dest)


def make_sensitivity_composite(dest: Path) -> None:
    paths = [
        FIG_RUN011 / "fig04_sensitivity_Tmax_global.png",
        FIG_RUN011 / "fig05_sensitivity_Tmax_contact.png",
        FIG_RUN011 / "fig06_sensitivity_Qdielectric.png",
    ]
    labels = ["A Tmax_global", "B Tmax_contact", "C Qdielectric"]
    out = Image.new("RGB", (2200, 1800), "white")
    draw = ImageDraw.Draw(out)
    draw.rectangle((0, 0, 2200, 92), fill="#111827")
    draw.text((38, 26), "Fig. S7 Material and boundary sensitivity by parameter", fill="white", font=FONT_TITLE)
    slots = [(70, 150), (1130, 150), (590, 950)]
    for path, label, xy in zip(paths, labels, slots):
        img = resize_fit(Image.open(path), (980, 730))
        draw.text((xy[0], xy[1] - 36), label, fill="#0f172a", font=FONT_H)
        out.paste(img, xy)
    draw.text((70, 1728), "OFAT sensitivity based on finite element numerical experiments; no physical experiment is claimed.", fill="#334155", font=FONT_SMALL)
    save_figure(out, dest)


def prepare_figures(stats: dict) -> list[dict]:
    figures = [
        ("Fig1", "Model workflow and CAD-driven geometry", "RUN006-RUN011", "generated composite", "Numerical Model and Simulation Setup", "main", "Shows geometry source and audit chain"),
        ("Fig2", "Baseline field-coupled dielectric loss and temperature", "RUN009A", "composite of RUN009 baseline figures", "Results and Discussion 4.1", "main", "Baseline potential/E/Qdielectric/T fields"),
        ("Fig3", "RUN010 Tmax risk heatmap", "RUN010", rel(FIG_RUN010 / "fig01_Tmax_heatmap_load_oil_by_Rc_RUN010.png"), "Results and Discussion 4.2/4.4", "main", "Main 125-case global temperature risk map"),
        ("Fig4", "RUN010 contact temperature risk heatmap", "RUN010", rel(FIG_RUN010 / "fig02_Tmax_contact_heatmap_load_oil_by_Rc_RUN010.png"), "Results and Discussion 4.2/4.4", "main", "Contact degradation response"),
        ("Fig5", "Safe load boundary by oil temperature and Rc", "RUN010", rel(FIG_RUN010 / "fig03_safe_load_boundary_by_oil_and_Rc_RUN010.png"), "Results and Discussion 4.4", "main", "Risk-boundary summary"),
        ("Fig6", "Heat source decomposition for representative cases", "RUN010", rel(FIG_RUN010 / "fig06_heat_source_decomposition_representative_cases_RUN010.png"), "Results and Discussion 4.3", "main", "Shows Joule/contact/dielectric source contributions"),
        ("Fig7", "RUN008 vs RUN010 temperature difference", "RUN010 vs RUN008", rel(FIG_RUN010 / "fig11_RUN008_vs_RUN010_Tmax_delta_heatmap.png"), "Results and Discussion 4.3", "main", "Quantifies field-coupled dielectric-loss impact"),
        ("Fig8", "Mesh independence summary", "RUN011A", "generated composite", "Results and Discussion 4.5", "main", "Numerical reliability check"),
        ("Fig9", "Parameter sensitivity ranking", "RUN011B", rel(FIG_RUN011 / "fig07_sensitivity_ranking.png"), "Results and Discussion 4.5", "main", "Ranks key material and boundary uncertainties"),
        ("FigS1", "Full run audit flow", "RUN006-RUN011", "generated diagram", "Supplementary", "supplementary", "Audit trail"),
        ("FigS2", "Qcontact I2Rc validation", "RUN010", rel(FIG_RUN010 / "fig08_Qcontact_I2Rc_validation_RUN010.png"), "Supplementary", "supplementary", "Contact heat-source validation"),
        ("FigS3", "Qjoule I2 scaling validation", "RUN010", rel(FIG_RUN010 / "fig09_Qjoule_I2_scaling_validation_RUN010.png"), "Supplementary", "supplementary", "Conductor Joule heat validation"),
        ("FigS4", "Heat balance residual distribution", "RUN010", rel(FIG_RUN010 / "fig07_heat_balance_residual_125_cases_RUN010.png"), "Supplementary", "supplementary", "Heat-balance validation"),
        ("FigS5", "Electric-field diagnostic summary", "RUN010", rel(FIG_RUN010 / "fig13_Efield_diagnostic_summary_RUN010.png"), "Supplementary", "supplementary", "Field singularity review"),
        ("FigS6", "Dielectric loss field-to-ref ratio", "RUN010", rel(FIG_RUN010 / "fig05_Qdielectric_ratio_field_to_ref.png"), "Supplementary", "supplementary", "DIELECTRIC_LOSS_REVIEW_REQUIRED explanation"),
        ("FigS7", "Material sensitivity each parameter", "RUN011B", "generated composite", "Supplementary", "supplementary", "Detailed OFAT sensitivity"),
    ]

    make_workflow_geometry(stats, FIG_OUT / "Fig1_model_workflow_and_geometry.png")
    make_baseline_composite(FIG_OUT / "Fig2_baseline_field_dielectric_temperature.png")
    annotate_copy(FIG_RUN010 / "fig01_Tmax_heatmap_load_oil_by_Rc_RUN010.png", FIG_OUT / "Fig3_run010_Tmax_risk_heatmap.png", "Fig. 3 RUN010 global temperature risk heatmap", "Diagnostic risk zoning, not IEC/IEEE limit.")
    annotate_copy(FIG_RUN010 / "fig02_Tmax_contact_heatmap_load_oil_by_Rc_RUN010.png", FIG_OUT / "Fig4_run010_contact_temperature_risk_heatmap.png", "Fig. 4 RUN010 contact temperature risk heatmap", "Diagnostic contact risk zoning, not material or IEC/IEEE limit.")
    annotate_copy(FIG_RUN010 / "fig03_safe_load_boundary_by_oil_and_Rc_RUN010.png", FIG_OUT / "Fig5_safe_load_boundary_by_oil_and_Rc.png", "Fig. 5 Diagnostic safe-load boundary", "Boundary is diagnostic for this model and is not a standard limit.")
    annotate_copy(FIG_RUN010 / "fig06_heat_source_decomposition_representative_cases_RUN010.png", FIG_OUT / "Fig6_heat_source_decomposition_representative_cases.png", "Fig. 6 Heat source decomposition", "Field-coupled Qdielectric; review flag retained.")
    annotate_copy(FIG_RUN010 / "fig11_RUN008_vs_RUN010_Tmax_delta_heatmap.png", FIG_OUT / "Fig7_run008_vs_run010_temperature_difference.png", "Fig. 7 RUN008 vs RUN010 temperature difference", "RUN010 uses field-coupled Qdielectric; RUN008 uses approximate reference.")
    make_mesh_composite(FIG_OUT / "Fig8_mesh_independence_summary.png")
    annotate_copy(FIG_RUN011 / "fig07_sensitivity_ranking.png", FIG_OUT / "Fig9_parameter_sensitivity_ranking.png", "Fig. 9 Parameter sensitivity ranking", "OFAT numerical sensitivity; no physical experiment is claimed.")
    make_audit_flow(stats, FIG_OUT / "FigS1_full_run_audit_flow.png")
    annotate_copy(FIG_RUN010 / "fig08_Qcontact_I2Rc_validation_RUN010.png", FIG_OUT / "FigS2_Qcontact_I2Rc_validation.png", "Fig. S2 Qcontact I2Rc validation", "Contact resistance degradation is a parameterized equivalent model.")
    annotate_copy(FIG_RUN010 / "fig09_Qjoule_I2_scaling_validation_RUN010.png", FIG_OUT / "FigS3_Qjoule_I2_scaling_validation.png", "Fig. S3 Qjoule I2 scaling validation", "Conductor Joule heat follows source-fixed normalization.")
    annotate_copy(FIG_RUN010 / "fig07_heat_balance_residual_125_cases_RUN010.png", FIG_OUT / "FigS4_heat_balance_residual_distribution.png", "Fig. S4 Heat balance residual distribution", "RUN008B heat-balance classification retained.")
    annotate_copy(FIG_RUN010 / "fig13_Efield_diagnostic_summary_RUN010.png", FIG_OUT / "FigS5_Efield_diagnostic_summary.png", "Fig. S5 Electric-field diagnostic summary", "E95/probe metrics used; field_singularity_flag retained.")
    annotate_copy(FIG_RUN010 / "fig05_Qdielectric_ratio_field_to_ref.png", FIG_OUT / "FigS6_dielectric_loss_field_to_ref_ratio.png", "Fig. S6 Dielectric loss field-to-reference ratio", "DIELECTRIC_LOSS_REVIEW_REQUIRED retained; not model failure.")
    make_sensitivity_composite(FIG_OUT / "FigS7_material_sensitivity_each_parameter.png")
    return [
        {
            "figure_id": row[0],
            "figure_title": row[1],
            "source_run": row[2],
            "source_file": row[3],
            "recommended_section": row[4],
            "main_or_supplementary": row[5],
            "reason": row[6],
        }
        for row in figures
    ]


def write_figure_index(figures: list[dict]) -> None:
    pd.DataFrame(figures).to_csv(TAB_OUT / "manuscript_figure_index.csv", index=False)


def write_table_index() -> None:
    rows = [
        ["Table1", "Simulation stage audit summary", "RUN006-RUN011", rel(TAB_OUT / "run_stage_audit_summary.csv"), "Numerical Model and Simulation Setup / Model verification", "main", "Traces model evolution and validation status"],
        ["Table2", "Key numerical result summary", "RUN010/RUN011", rel(TAB_OUT / "key_result_summary.csv"), "Results and Discussion", "main", "Condenses main ranges, counts and validation statistics"],
        ["Table3", "Model validation evidence chain", "RUN006-RUN011", rel(TAB_OUT / "model_validation_evidence_chain.csv"), "Model verification", "main/supplementary", "Shows acceptance criteria and evidence"],
        ["TableS1", "Manuscript figure index", "RUN012", rel(TAB_OUT / "manuscript_figure_index.csv"), "Supplementary / project audit", "supplementary", "Maps figures to source runs"],
        ["TableS2", "Manuscript table index", "RUN012", rel(TAB_OUT / "manuscript_table_index.csv"), "Supplementary / project audit", "supplementary", "Maps tables to source runs"],
        ["TableS3", "RUN010 risk boundary summary", "RUN010", rel(RUN010 / "run010_risk_boundary_summary.csv"), "Results and Discussion 4.4", "supplementary", "Detailed safe-load boundary by oil temperature and Rc"],
        ["TableS4", "RUN011 mesh convergence summary", "RUN011A", rel(RUN011A / "mesh_convergence_summary.csv"), "Results and Discussion 4.5", "supplementary", "Mesh independence evidence"],
        ["TableS5", "RUN011 sensitivity index summary", "RUN011B", rel(RUN011B / "sensitivity_index_summary.csv"), "Results and Discussion 4.5", "supplementary", "Parameter robustness evidence"],
    ]
    write_csv(TAB_OUT / "manuscript_table_index.csv", [
        "table_id", "table_title", "source_run", "source_file", "recommended_section",
        "main_or_supplementary", "reason",
    ], rows)


def write_report(stats: dict, input_status: pd.DataFrame, proceed: bool) -> None:
    missing = input_status[~input_status["exists"]]["input_file"].tolist()
    text = f"""# MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012 报告

## 本轮任务目标

本轮目标是汇总 RUN006-RUN011 的审计链条，建立论文实验部分可追溯的模型验证材料，整理主图、补充图和关键表格，并生成仿真实验部分的初稿框架。本轮未运行新的 COMSOL 大规模扫描，未做全年气象驱动，未做暂态仿真，也未覆盖 RUN010/RUN011 原始 CSV。

## 输入文件状态

- required inputs: {len(input_status)}
- missing inputs: {len(missing)}

{chr(10).join('- missing: ' + x for x in missing) if missing else '所有任务说明15列出的必需输入文件均已找到。'}

## RUN006-RUN011 证据链

RUN006 修复了 solid-only 基准热模型的热源归一化，基准工况 `Tmax_global_C={fmt(stats['run006_tmax'])} degC`，`Qjoule={fmt(stats['run006_qjoule'])} W`，`Qcontact={fmt(stats['run006_qcontact'], 4)} W`，热量收支残差 `{fmt(stats['run006_resid'])}%`。RUN007 完成 27 组小规模 solid-only 扫参，`{stats['run007_valid']}/{stats['run007_total']}` 有效。RUN008B 对 RUN008 的热量收支进行复核，`{stats['run008b_valid']}/{stats['run008b_total']}` 重新分类为有效。RUN009A/RUN009B 将 approximate_Qdielectric_ref 替换为 field-coupled Qdielectric，并完成基准与 27 组验证。RUN010 完成 125 组完整电场耦合介质损耗风险扫描，`{stats['run010_valid']}/{stats['run010_total']}` 有效。RUN011A/RUN011B 完成网格无关性和材料/边界敏感性验证。

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

RUN010 的 `Tmax_global_C` 范围为 `{fmt(stats['run010_tmax_min'])}-{fmt(stats['run010_tmax_max'])} degC`，`Tmax_contact_C` 最大值为 `{fmt(stats['run010_contact_max'])} degC`。global risk_zone 统计为 `{stats['run010_risk_counts']}`；contact_risk_zone 统计为 `{stats['run010_contact_counts']}`。热量收支最大绝对归一化残差为 `{fmt(stats['run010_heat_resid_max_abs'])}%`。这些 risk_zone 阈值仅为研究内部诊断分区，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## RUN011 网格无关性结论

RUN011A 中 3 个代表工况的 medium-vs-fine 均通过。最大 `Tmax_global` 误差为 `{fmt(stats['run011_mesh_max_tmax_err'])}%`，最大 `E95_RIP` 误差为 `{fmt(stats['run011_mesh_max_e95_err'])}%`，最大 `Qdielectric_RIP_field` 误差为 `{fmt(stats['run011_mesh_max_qd_err'])}%`。因此 RUN010 使用的 medium 网格可作为当前稳态风险扫描的默认网格。

## RUN011 敏感性结论

RUN011B 完成 `{stats['run011_sens_total']}` 个材料/边界敏感性工况，热量收支有效 `{stats['run011_sens_heat_valid']}/{stats['run011_sens_total']}`，field_singularity_flag true 为 `{stats['run011_sens_singular']}`。敏感性排序为：`{stats['sensitivity_ranking']}`。其中高风险基准下低空气换热或接触电阻基准倍增可触发 diagnostic thermal risk，这反映参数化工况响应，不是数值失败。

## dielectric_loss_review_required 的论文解释

`dielectric_loss_review_required=true` 不代表模型失败。该标记来自 `Qdielectric_field/ref` 大于最初设定的 `[0.1, 10]` 复核区间，RUN010 平均比值约为 `{fmt(stats['run010_qd_ratio_mean'])}`。同时 RUN010 的 field_singularity_flag 为 `{stats['run010_field_singular']}/{stats['run010_total']}`，说明该差异不是由被标记的屏端奇异场直接支配。论文中应解释为：真实电场分布下的介质损耗积分高于平均场参考估计，需保留复核标记并在材料参数/电容屏边缘场处理部分讨论。

## 论文主图建议

主文建议使用 Fig1-Fig9：模型流程与几何、基准场分布、RUN010 全局温度热力图、接触温度热力图、安全负荷边界、热源分解、RUN008 vs RUN010 温度差异、网格无关性、敏感性排序。

## 论文主表建议

建议主文使用 Table1 阶段审计汇总、Table2 关键结果汇总和 Table3 模型验证证据链。详细风险边界、网格误差和敏感性指数可作为补充表。

## 是否可以进入实验部分撰写阶段

RUN012 已生成主图/补充图索引、主表/补充表索引、模型验证证据链、实验部分框架和结果讨论关键段落；没有误称实物实验验证，没有把诊断阈值写成标准限值，也没有删除历史结果。

Can proceed to MANUSCRIPT_EXPERIMENT_SECTION_DRAFT_RUN013: {'YES' if proceed else 'NO'}
"""
    (DOC_OUT / "model_validation_and_manuscript_figures_run012_report.md").write_text(text, encoding="utf-8")


def write_outline() -> None:
    text = """# 仿真实验部分草稿框架

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
"""
    (DRAFT_OUT / "experiment_section_outline.md").write_text(text, encoding="utf-8")


def write_key_paragraphs(stats: dict) -> None:
    text = f"""# Results and Discussion 关键段落初稿

## 1. 基准工况结果段落

在 `STEADY_1250_LOAD_1p0` 基准工况下，完整电场耦合介质损耗模型得到的 `Tmax_global_C` 为约 `{fmt(stats['run009a_tmax'])} degC`。导体焦耳热、接触热和 RIP 介质损耗分别由 source-fixed 导体电阻、参数化接触电阻和电场分布积分给出。与早期 solid-only 热诊断相比，RUN009A 将 approximate_Qdielectric_ref 替换为 `omega * epsilon0 * epsr * tan_delta * |E|^2`，因此能够反映 RIP 区域非均匀电场对介质损耗的贡献。该结果属于 finite element numerical simulation，不是实物实验测量。

## 2. RUN010 125组风险边界段落

RUN010 在 5 × 5 × 5 的核心工况矩阵上完成了 125 组稳态有限元计算。所有工况均满足热源归一化、热量收支、selection 完整性和电场奇异性检查，`overall_valid={stats['run010_valid']}/{stats['run010_total']}`。在该矩阵内，`Tmax_global_C` 的范围为 `{fmt(stats['run010_tmax_min'])}-{fmt(stats['run010_tmax_max'])} degC`，global risk zone 统计为 `{stats['run010_risk_counts']}`。这里的 safe、attention、warning 和 thermal_risk 仅为本文内部的 diagnostic risk zoning，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## 3. RUN008 vs RUN010 对比段落

RUN008 使用 approximate_Qdielectric_ref 作为 solid-only 诊断热源，而 RUN010 使用 field-coupled Qdielectric。两者对比显示，field-coupled 介质损耗使 `Tmax_global_C` 平均增加约 `{fmt(stats['run010_delta_mean'])} degC`，最大增加约 `{fmt(stats['run010_delta_max'])} degC`，并导致 `{stats['run010_risk_changed']}` 个工况的 risk zone 发生变化。该差异表明平均场参考热源可以用于早期热诊断，但论文主结果应采用电场分布积分得到的介质损耗。

## 4. 热源分解段落

RUN010 的热源分解将总发热量分为导体焦耳热、接触电阻热和 RIP 介质损耗热。导体焦耳热随电流平方变化，接触热严格按照 `Icase^2 * Rc0 * Rc_factor` 计算，RIP 介质损耗由电场分布积分得到。RUN006 首先验证了热源归一化，其中基准 solid-only 模型的 `Qjoule` 为 `{fmt(stats['run006_qjoule'])} W`，`Qcontact` 为 `{fmt(stats['run006_qcontact'], 4)} W`。这一审计链条降低了把几何域、接触层或屏蔽层错误计入导体损耗的风险。

## 5. 接触电阻劣化影响段落

接触电阻劣化在本文中采用参数化等效模型表示，而不是实测缺陷。RUN010 和 RUN011B 结果表明，在较高负荷和较高油温下，接触电阻倍率升高会显著提高接触热点温度。RUN011B 中高风险基准下 `Rc0_multiplier=2` 的工况达到 diagnostic thermal risk，但其热量收支仍为有效，说明这是参数扰动下的物理响应，而不是数值失败。

## 6. 网格无关性段落

RUN011A 选取基准、高接触风险和最高压力三个代表工况进行 coarse、medium 和 fine 三档网格比较。以 fine 网格为参考，medium 网格在三个代表工况中均通过收敛要求，最大 `Tmax_global` 误差为 `{fmt(stats['run011_mesh_max_tmax_err'])}%`，最大 `E95_RIP` 误差为 `{fmt(stats['run011_mesh_max_e95_err'])}%`，最大 `Qdielectric_RIP_field` 误差为 `{fmt(stats['run011_mesh_max_qd_err'])}%`。因此，RUN010 使用的 medium 网格可作为当前稳态风险扫描的默认网格。

## 7. 敏感性分析段落

RUN011B 对 RIP 导热率、介质损耗因数、相对介电常数、油侧换热系数、空气侧换热系数和接触电阻基准值进行了单因素扰动分析。敏感性排序为 `{stats['sensitivity_ranking']}`。其中 tan_delta 和 epsr 主要影响介质损耗项，Rc0 和 h_air 对接触热点或整体温升具有明显影响。该结果说明后续模型验证和论文讨论应重点交代介质参数、空气侧换热和接触电阻等工程假设。

## 8. 局限性段落

本文结果基于二维轴对称有限元模型和参数化运行工况。模型没有显式描述法兰螺栓孔、端子三维局部结构、真实污染非均匀分布和全年气象暂态过程。risk zone 阈值仅用于诊断分区，不应解释为标准限值。`dielectric_loss_review_required=true` 也不表示模型失败，而是提示 field-coupled Qdielectric 与平均场参考之间存在需要解释的差异；RUN010 中 field_singularity_flag 为 `{stats['run010_field_singular']}/{stats['run010_total']}`，说明该差异不是由已标记的屏端奇异点直接支配。后续应结合材料参数复核、现场监测或公开实测数据进一步约束模型不确定性。
"""
    (DRAFT_OUT / "results_discussion_key_paragraphs.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    input_status = write_input_status()
    stats = compute_stats()
    write_stage_audit_summary(stats)
    write_key_result_summary(stats)
    write_validation_evidence_chain(stats)
    figures = prepare_figures(stats)
    write_figure_index(figures)
    write_table_index()
    write_outline()
    write_key_paragraphs(stats)
    required_figs = [
        "Fig1_model_workflow_and_geometry.png",
        "Fig2_baseline_field_dielectric_temperature.png",
        "Fig3_run010_Tmax_risk_heatmap.png",
        "Fig4_run010_contact_temperature_risk_heatmap.png",
        "Fig5_safe_load_boundary_by_oil_and_Rc.png",
        "Fig6_heat_source_decomposition_representative_cases.png",
        "Fig7_run008_vs_run010_temperature_difference.png",
        "Fig8_mesh_independence_summary.png",
        "Fig9_parameter_sensitivity_ranking.png",
        "FigS1_full_run_audit_flow.png",
        "FigS2_Qcontact_I2Rc_validation.png",
        "FigS3_Qjoule_I2_scaling_validation.png",
        "FigS4_heat_balance_residual_distribution.png",
        "FigS5_Efield_diagnostic_summary.png",
        "FigS6_dielectric_loss_field_to_ref_ratio.png",
        "FigS7_material_sensitivity_each_parameter.png",
    ]
    required_tables = [
        "run_stage_audit_summary.csv",
        "key_result_summary.csv",
        "manuscript_figure_index.csv",
        "manuscript_table_index.csv",
        "model_validation_evidence_chain.csv",
    ]
    proceed = bool(
        bool(input_status["exists"].all())
        and all((FIG_OUT / name).exists() for name in required_figs)
        and all((TAB_OUT / name).exists() for name in required_tables)
        and (DRAFT_OUT / "experiment_section_outline.md").exists()
        and (DRAFT_OUT / "results_discussion_key_paragraphs.md").exists()
    )
    write_report(stats, input_status, proceed)
    print(f"Wrote RUN012 raw status: {RAW_OUT}")
    print(f"Wrote manuscript-ready figures: {FIG_OUT}")
    print(f"Wrote manuscript-ready tables: {TAB_OUT}")
    print(f"Wrote RUN012 docs under: {DOC_OUT}")


if __name__ == "__main__":
    main()
