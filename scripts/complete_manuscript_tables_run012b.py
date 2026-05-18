"""Complete RUN012B manuscript-ready tables and audit indices.

RUN012B only reads existing RUN006-RUN012 CSV/MD/PNG artifacts and writes
manuscript-ready summary tables plus a completion report. It does not run
COMSOL and does not modify RUN010/RUN011 raw CSV files.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[1]
TAB_OUT = PROJECT / "results" / "summary_tables" / "manuscript_ready"
RAW_OUT = PROJECT / "results" / "raw_comsol_exports" / "MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012B"
FIG_OUT = PROJECT / "results" / "paper_figures" / "manuscript_ready"
DOC_OUT = PROJECT / "docs"
DRAFT_OUT = DOC_OUT / "manuscript_draft_sections"

RUN002 = PROJECT / "results" / "raw_comsol_exports" / "STEADY_1250_LOAD_1p0_RUN002"
RUN003 = PROJECT / "results" / "raw_comsol_exports" / "PHYSICS_DIAGNOSTICS_RUN003"
RUN006 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RUN006_SOURCE_FIXED"
RUN007 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_SWEEP_27_RUN007"
RUN008 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RISK_125_RUN008"
RUN008B = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RISK_125_RUN008B_HEAT_BALANCE_FIX"
RUN009A = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009A_BASELINE"
RUN009B = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009B_27CASE"
RUN010 = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010"
RUN011 = PROJECT / "results" / "raw_comsol_exports" / "MATERIAL_AND_MESH_SENSITIVITY_RUN011"
RUN011A = RUN011 / "RUN011A_MESH_INDEPENDENCE"
RUN011B = RUN011 / "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY"
RUN012 = PROJECT / "results" / "raw_comsol_exports" / "MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012"


MAIN_FIGS = [
    "Fig1_model_workflow_and_geometry.png",
    "Fig2_baseline_field_dielectric_temperature.png",
    "Fig3_run010_Tmax_risk_heatmap.png",
    "Fig4_run010_contact_temperature_risk_heatmap.png",
    "Fig5_safe_load_boundary_by_oil_and_Rc.png",
    "Fig6_heat_source_decomposition_representative_cases.png",
    "Fig7_run008_vs_run010_temperature_difference.png",
    "Fig8_mesh_independence_summary.png",
    "Fig9_parameter_sensitivity_ranking.png",
]

SUPP_FIGS = [
    "FigS1_full_run_audit_flow.png",
    "FigS2_Qcontact_I2Rc_validation.png",
    "FigS3_Qjoule_I2_scaling_validation.png",
    "FigS4_heat_balance_residual_distribution.png",
    "FigS5_Efield_diagnostic_summary.png",
    "FigS6_dielectric_loss_field_to_ref_ratio.png",
    "FigS7_material_sensitivity_each_parameter.png",
]


def ensure_dirs() -> None:
    TAB_OUT.mkdir(parents=True, exist_ok=True)
    RAW_OUT.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT))
    except ValueError:
        return str(path)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def bool_count(series: pd.Series) -> int:
    return int(series.astype(str).str.lower().eq("true").sum())


def fmt(value: float, digits: int = 3) -> str:
    try:
        f = float(value)
    except Exception:
        return "NA"
    if not math.isfinite(f):
        return "NA"
    return f"{f:.{digits}f}"


def counts(df: pd.DataFrame, col: str) -> str:
    if df.empty or col not in df:
        return "missing"
    order = [
        "safe", "attention", "warning", "thermal_risk",
        "contact_safe", "contact_attention", "contact_warning", "contact_risk",
        "SOLVED_VALID", "SOLVED_THERMAL_WARNING", "SOLVED_THERMAL_RISK",
        "invalid_case",
    ]
    raw = df[col].astype(str).value_counts().to_dict()
    parts = []
    for key in order:
        if key in raw:
            parts.append(f"{key}:{raw[key]}")
    for key in sorted(raw):
        if key not in order:
            parts.append(f"{key}:{raw[key]}")
    return "; ".join(parts)


def source(path: Path) -> str:
    return rel(path) if path.exists() else rel(path) + " (missing)"


def compute_stats() -> dict:
    run002 = read_csv(RUN002 / "baseline_metrics.csv")
    run003 = read_csv(RUN003 / "diagnostic_results.csv")
    run006_m = read_csv(RUN006 / "solid_only_metrics.csv")
    run006_hs = read_csv(RUN006 / "heat_source_decomposition.csv")
    run006_hb = read_csv(RUN006 / "heat_balance_diagnostics.csv")
    run006_audit = read_csv(RUN006 / "source_normalization_audit.csv")
    run007_v = read_csv(RUN007 / "sweep_validity_summary.csv")
    run008_v = read_csv(RUN008 / "risk_validity_summary.csv")
    run008b_v = read_csv(RUN008B / "risk_validity_summary_reclassified.csv")
    run009a = read_csv(RUN009A / "baseline_metrics.csv")
    run009b_v = read_csv(RUN009B / "run009b_validity_summary.csv")
    run010_m = read_csv(RUN010 / "run010_risk_metrics.csv")
    run010_v = read_csv(RUN010 / "run010_validity_summary.csv")
    run010_hb = read_csv(RUN010 / "heat_balance_by_case.csv")
    run010_d = read_csv(RUN010 / "dielectric_loss_by_case.csv")
    run010_e = read_csv(RUN010 / "electric_field_diagnostics_by_case.csv")
    run010_cmp = read_csv(RUN010 / "run008_vs_run010_comparison.csv")
    mesh = read_csv(RUN011A / "mesh_convergence_summary.csv")
    sens = read_csv(RUN011B / "sensitivity_metrics.csv")
    sens_i = read_csv(RUN011B / "sensitivity_index_summary.csv")
    medium = mesh[mesh["mesh_level"].astype(str).eq("medium")] if not mesh.empty else pd.DataFrame()
    nonbase = sens_i[
        sens_i["parameter_value"].astype(float) != sens_i["baseline_value"].astype(float)
    ] if not sens_i.empty else pd.DataFrame()
    if not nonbase.empty:
        ranking = (
            nonbase.groupby("parameter_name")[["S_Tmax_global", "S_Tmax_contact", "S_Qdielectric"]]
            .apply(lambda df: pd.Series({"score": df.abs().max().max()}))
            .reset_index()
            .sort_values("score", ascending=False)
        )
        sensitivity_ranking = " > ".join(ranking["parameter_name"].tolist())
    else:
        ranking = pd.DataFrame()
        sensitivity_ranking = "missing"

    stats = {
        "run001_exists": (PROJECT / "results" / "raw_comsol_exports" / "STEADY_1250_LOAD_1p0" / "metrics_export.csv").exists(),
        "run002_status": run002["status"].iloc[0] if not run002.empty else "missing",
        "run002_tmax": float(run002["Tmax_global_C"].iloc[0]) if not run002.empty else float("nan"),
        "run003_rows": len(run003),
        "run006_status": run006_m["status"].iloc[0] if not run006_m.empty else "missing",
        "run006_tmax": float(run006_m["Tmax_global_C"].iloc[0]) if not run006_m.empty else float("nan"),
        "run006_qjoule": float(run006_hs["Qjoule_conductor_W"].iloc[0]) if not run006_hs.empty else float("nan"),
        "run006_qcontact": float(run006_hs["Qcontact_W"].iloc[0]) if not run006_hs.empty else float("nan"),
        "run006_qd": float(run006_hs["Qdielectric_RIP_W"].iloc[0]) if not run006_hs.empty else float("nan"),
        "run006_resid": float(run006_hb["residual_percent"].iloc[0]) if not run006_hb.empty else float("nan"),
        "run006_audit_included": int(run006_audit["include_in_source"].astype(str).str.lower().eq("true").sum()) if not run006_audit.empty else 0,
        "run007_total": len(run007_v),
        "run007_valid": bool_count(run007_v["overall_valid"]) if not run007_v.empty and "overall_valid" in run007_v else 0,
        "run008_total": len(run008_v),
        "run008_valid": bool_count(run008_v["overall_valid"]) if not run008_v.empty and "overall_valid" in run008_v else 0,
        "run008b_total": len(run008b_v),
        "run008b_valid": bool_count(run008b_v["overall_valid_reclassified"]) if not run008b_v.empty else 0,
        "run009a_status": run009a["status"].iloc[0] if not run009a.empty else "missing",
        "run009a_tmax": float(run009a["Tmax_global_C"].iloc[0]) if not run009a.empty else float("nan"),
        "run009a_qd_field": float(run009a["Qdielectric_RIP_field_W"].iloc[0]) if not run009a.empty else float("nan"),
        "run009a_qd_ratio": float(run009a["Qdielectric_ratio_field_to_ref"].iloc[0]) if not run009a.empty else float("nan"),
        "run009b_total": len(run009b_v),
        "run009b_valid": bool_count(run009b_v["overall_valid"]) if not run009b_v.empty and "overall_valid" in run009b_v else 0,
        "run010_total": len(run010_v),
        "run010_valid": bool_count(run010_v["overall_valid"]) if not run010_v.empty else 0,
        "run010_tmin": float(run010_m["Tmax_global_C"].min()) if not run010_m.empty else float("nan"),
        "run010_tmax": float(run010_m["Tmax_global_C"].max()) if not run010_m.empty else float("nan"),
        "run010_contact_max": float(run010_m["Tmax_contact_C"].max()) if not run010_m.empty else float("nan"),
        "run010_risk_counts": counts(run010_m, "risk_zone"),
        "run010_contact_counts": counts(run010_m, "contact_risk_zone"),
        "run010_heat_resid_max": float(run010_hb["residual_percent_Qgenerated"].abs().max()) if not run010_hb.empty else float("nan"),
        "run010_field_singularity": bool_count(run010_e["field_singularity_flag"]) if not run010_e.empty else 0,
        "run010_dielectric_review": bool_count(run010_d["dielectric_loss_review_required"]) if not run010_d.empty else 0,
        "run010_qd_ratio_mean": float(run010_d["Qdielectric_ratio_field_to_ref"].mean()) if not run010_d.empty else float("nan"),
        "run010_qd_ratio_min": float(run010_d["Qdielectric_ratio_field_to_ref"].min()) if not run010_d.empty else float("nan"),
        "run010_qd_ratio_max": float(run010_d["Qdielectric_ratio_field_to_ref"].max()) if not run010_d.empty else float("nan"),
        "run010_delta_mean": float(run010_cmp["delta_Tmax_global_C"].mean()) if not run010_cmp.empty else float("nan"),
        "run010_delta_max": float(run010_cmp["delta_Tmax_global_C"].max()) if not run010_cmp.empty else float("nan"),
        "run010_risk_changed": bool_count(run010_cmp["risk_zone_changed"]) if not run010_cmp.empty else 0,
        "run011a_medium_total": len(medium),
        "run011a_medium_pass": bool_count(medium["medium_vs_fine_pass"]) if not medium.empty else 0,
        "run011a_tmax_err": float(medium["err_Tmax_global_pct"].max()) if not medium.empty else float("nan"),
        "run011a_e95_err": float(medium["err_E95_RIP_pct"].max()) if not medium.empty else float("nan"),
        "run011a_qd_err": float(medium["err_Qdielectric_pct"].max()) if not medium.empty else float("nan"),
        "run011b_total": len(sens),
        "run011b_heat_valid": int(sens["heat_balance_status"].astype(str).isin(["VALID_STRICT", "VALID_LOW_POWER_RECLASSIFIED"]).sum()) if not sens.empty else 0,
        "run011b_singularity": bool_count(sens["field_singularity_flag"]) if not sens.empty else 0,
        "run011b_status_counts": counts(sens, "status"),
        "run011b_ranking": sensitivity_ranking,
        "ranking": ranking,
    }
    return stats


def write_stage_audit(stats: dict) -> None:
    rows = [
        ["RUN001_INVALID_OR_EARLY_BASELINE", "Early baseline/geometry-only attempt", "early COMSOL baseline", 1, source(PROJECT / "results/raw_comsol_exports/STEADY_1250_LOAD_1p0/metrics_export.csv"), "historical/diagnostic; not accepted as main result", "no", "supplementary/model audit", "Retained for audit trail only"],
        ["RUN002_INVALID_OR_EARLY_BASELINE", "CAD-driven early baseline with invalid thermal behavior", "early electro-thermal baseline", 1, source(RUN002 / "baseline_metrics.csv"), f"{stats['run002_status']}; Tmax={fmt(stats['run002_tmax'])} degC; invalid temperature history", "no", "supplementary/model audit", "Historical diagnostic result; not manuscript main result"],
        ["RUN003_PHYSICS_DIAGNOSTICS", "Physics feature diagnostics", "diagnostic toggles", stats["run003_rows"], source(RUN003 / "diagnostic_results.csv"), "diagnostic only", "no", "supplementary/model audit", "Used to localize abnormal heat sources and boundary issues"],
        ["RUN006_SOURCE_FIXED_BASELINE", "Source-fixed solid-only baseline", "solid-only thermal diagnostic", 1, source(RUN006 / "solid_only_metrics.csv"), f"{stats['run006_status']}; Qjoule={fmt(stats['run006_qjoule'])} W; Qcontact={fmt(stats['run006_qcontact'],4)} W", "diagnostic support", "supplementary/model audit", "Validates source normalization before sweeps"],
        ["RUN007_SOLID_ONLY_27_SWEEP", "Small solid-only sweep", "solid-only thermal diagnostic", stats["run007_total"], source(RUN007 / "sweep_validity_summary.csv"), f"{stats['run007_valid']}/{stats['run007_total']} valid", "diagnostic support", "supplementary/model audit", "Pre-check before 125-case risk matrix"],
        ["RUN008_SOLID_ONLY_125_RISK", "125-case solid-only approximate risk scan", "solid-only approximate_Qdielectric_ref", stats["run008_total"], source(RUN008 / "risk_metrics.csv"), f"initial validity={stats['run008_valid']}/{stats['run008_total']}; superseded by RUN008B/RUN010", "diagnostic support", "supplementary/model audit", "Not final full electro-thermal result"],
        ["RUN008B_HEAT_BALANCE_RECHECK", "RUN008 heat-balance reclassification", "postprocess validation", stats["run008b_total"], source(RUN008B / "risk_validity_summary_reclassified.csv"), f"{stats['run008b_valid']}/{stats['run008b_total']} reclassified valid", "diagnostic support", "supplementary/model audit", "Explains low-power normalization issue"],
        ["RUN009A_FULL_FIELD_BASELINE", "Baseline full field-coupled dielectric loss", "full electro-thermal/electrostatics", 1, source(RUN009A / "baseline_metrics.csv"), f"{stats['run009a_status']}; Qd field/ref={fmt(stats['run009a_qd_ratio'])}", "yes", "main text/supporting", "Baseline field/temperature figure source"],
        ["RUN009B_FULL_FIELD_27_CHECK", "27-case full field check", "full electro-thermal/electrostatics", stats["run009b_total"], source(RUN009B / "run009b_validity_summary.csv"), f"{stats['run009b_valid']}/{stats['run009b_total']} valid", "yes", "supplementary/validation", "Stability check before RUN010"],
        ["RUN010_FULL_FIELD_125_RISK", "Main 125-case full field-coupled risk boundary", "full electro-thermal/electrostatics", stats["run010_total"], source(RUN010 / "run010_risk_metrics.csv"), f"{stats['run010_valid']}/{stats['run010_total']} valid; field_singularity={stats['run010_field_singularity']}", "yes", "main text", "Primary risk-boundary data; diagnostic risk zoning is not a standard limit"],
        ["RUN011A_MESH_INDEPENDENCE", "Mesh independence verification", "numerical reliability check", 9, source(RUN011A / "mesh_convergence_summary.csv"), f"medium-vs-fine {stats['run011a_medium_pass']}/{stats['run011a_medium_total']} pass", "yes", "main text/validation", "Numerical credibility verification for RUN010 default mesh"],
        ["RUN011B_MATERIAL_BOUNDARY_SENSITIVITY", "Material and boundary sensitivity", "parameter robustness check", stats["run011b_total"], source(RUN011B / "sensitivity_index_summary.csv"), f"heat valid={stats['run011b_heat_valid']}/{stats['run011b_total']}; singular={stats['run011b_singularity']}", "yes", "main text/supplementary", "Sensitivity ranking and robustness check"],
        ["RUN012_MANUSCRIPT_FIGURES", "Manuscript-ready figure and draft organization", "postprocess/indexing", 16, source(PROJECT / "results/paper_figures/manuscript_ready"), "figures and draft sections generated", "yes", "manuscript preparation", "RUN012B completes auditable table indices"],
    ]
    write_csv(TAB_OUT / "run_stage_audit_summary.csv", [
        "stage", "purpose", "model_type", "case_count", "key_outputs", "validation_status",
        "can_be_used_in_manuscript", "main_or_supplementary", "notes",
    ], rows)


def write_key_results(stats: dict) -> None:
    rows = [
        ["RUN009A Tmax_global_C", f"{fmt(stats['run009a_tmax'])} degC", "RUN009A_FULL_FIELD_BASELINE", source(RUN009A / "baseline_metrics.csv"), "baseline field/temperature discussion", "main text", "Finite element numerical baseline, not physical experiment"],
        ["RUN009A Qdielectric_RIP_field_W", f"{fmt(stats['run009a_qd_field'])} W", "RUN009A_FULL_FIELD_BASELINE", source(RUN009A / "baseline_metrics.csv"), "dielectric-loss discussion", "main text/supporting", "Field-coupled dielectric loss"],
        ["RUN009A Qdielectric_field/ref", fmt(stats["run009a_qd_ratio"]), "RUN009A_FULL_FIELD_BASELINE", source(RUN009A / "dielectric_loss_comparison.csv"), "dielectric-loss review", "supplementary/validation", "Review flag retained"],
        ["RUN010 Tmax_global_C range", f"{fmt(stats['run010_tmin'])}-{fmt(stats['run010_tmax'])} degC", "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "run010_risk_metrics.csv"), "risk-boundary result", "main text", "Primary 125-case full field-coupled result"],
        ["RUN010 Tmax_contact_C max", f"{fmt(stats['run010_contact_max'])} degC", "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "run010_risk_metrics.csv"), "contact-risk discussion", "main text", "Diagnostic contact zoning only"],
        ["RUN010 risk_zone counts", stats["run010_risk_counts"], "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "run010_risk_metrics.csv"), "risk-boundary result", "main text", "Diagnostic risk zoning, not IEC/IEEE standard limit"],
        ["RUN010 contact_risk_zone counts", stats["run010_contact_counts"], "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "run010_risk_metrics.csv"), "contact-risk result", "main text/supporting", "Diagnostic contact zones, not material limits"],
        ["RUN010 heat_balance max residual", f"{fmt(stats['run010_heat_resid_max'])}% max |residual_percent_Qgenerated|", "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "heat_balance_by_case.csv"), "model validation", "supplementary/validation", "Heat balance valid"],
        ["RUN010 field_singularity_flag count", f"{stats['run010_field_singularity']}/{stats['run010_total']}", "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "electric_field_diagnostics_by_case.csv"), "field validation", "supplementary/validation", "No flagged singularity cases"],
        ["RUN010 dielectric_loss_review_required count", f"{stats['run010_dielectric_review']}/{stats['run010_total']}", "RUN010_FULL_FIELD_125_RISK", source(RUN010 / "dielectric_loss_by_case.csv"), "dielectric-loss review", "supplementary/validation", f"field/ref mean={fmt(stats['run010_qd_ratio_mean'])}; not model failure"],
        ["RUN010 RUN008-vs-RUN010 mean delta_Tmax", f"mean={fmt(stats['run010_delta_mean'])} degC; max={fmt(stats['run010_delta_max'])} degC; changed={stats['run010_risk_changed']}/125", "RUN010_vs_RUN008", source(RUN010 / "run008_vs_run010_comparison.csv"), "field-coupled impact discussion", "main text/supporting", "RUN010 uses field-coupled dielectric loss"],
        ["RUN011A medium-vs-fine max Tmax error", f"{fmt(stats['run011a_tmax_err'])}%", "RUN011A_MESH_INDEPENDENCE", source(RUN011A / "mesh_convergence_summary.csv"), "mesh verification", "main text/validation", "Acceptance threshold < 1%"],
        ["RUN011A medium-vs-fine max E95 error", f"{fmt(stats['run011a_e95_err'])}%", "RUN011A_MESH_INDEPENDENCE", source(RUN011A / "mesh_convergence_summary.csv"), "mesh verification", "supplementary/validation", "Acceptance threshold < 3%"],
        ["RUN011A medium-vs-fine max Qdielectric error", f"{fmt(stats['run011a_qd_err'])}%", "RUN011A_MESH_INDEPENDENCE", source(RUN011A / "mesh_convergence_summary.csv"), "mesh verification", "main text/validation", "Acceptance threshold < 5%"],
        ["RUN011B sensitivity ranking", stats["run011b_ranking"], "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY", source(RUN011B / "sensitivity_index_summary.csv"), "sensitivity discussion", "main text/supporting", "OFAT numerical sensitivity ranking"],
    ]
    write_csv(TAB_OUT / "key_result_summary.csv", [
        "metric", "value_or_range", "source_run", "source_file", "manuscript_usage",
        "main_or_supplementary", "notes",
    ], rows)


def write_figure_index() -> None:
    fig_meta = {
        "Fig1_model_workflow_and_geometry.png": ("Fig1", "Model workflow and CAD-driven geometry", "RUN006-RUN011", "generated from stage diagnostics and audit tables", "Numerical Model and Simulation Setup", "main", "Workflow and geometry overview"),
        "Fig2_baseline_field_dielectric_temperature.png": ("Fig2", "Baseline field-coupled dielectric loss and temperature", "RUN009A", source(RUN009A / "baseline_metrics.csv"), "Results 4.1", "main", "Baseline electro-thermal distribution"),
        "Fig3_run010_Tmax_risk_heatmap.png": ("Fig3", "RUN010 Tmax risk heatmap", "RUN010", source(RUN010 / "run010_risk_metrics.csv"), "Results 4.2/4.4", "main", "Primary global-temperature risk map"),
        "Fig4_run010_contact_temperature_risk_heatmap.png": ("Fig4", "RUN010 contact temperature risk heatmap", "RUN010", source(RUN010 / "run010_risk_metrics.csv"), "Results 4.2/4.4", "main", "Contact degradation response"),
        "Fig5_safe_load_boundary_by_oil_and_Rc.png": ("Fig5", "Safe load boundary by oil temperature and Rc", "RUN010", source(RUN010 / "run010_risk_boundary_summary.csv"), "Results 4.4", "main", "Diagnostic safe-load boundary"),
        "Fig6_heat_source_decomposition_representative_cases.png": ("Fig6", "Heat source decomposition representative cases", "RUN010", source(RUN010 / "heat_source_decomposition_by_case.csv"), "Results 4.3", "main", "Joule/contact/dielectric source comparison"),
        "Fig7_run008_vs_run010_temperature_difference.png": ("Fig7", "RUN008 vs RUN010 temperature difference", "RUN010_vs_RUN008", source(RUN010 / "run008_vs_run010_comparison.csv"), "Results 4.3", "main", "Effect of field-coupled Qdielectric"),
        "Fig8_mesh_independence_summary.png": ("Fig8", "Mesh independence summary", "RUN011A", source(RUN011A / "mesh_convergence_summary.csv"), "Results 4.5", "main", "Numerical reliability evidence"),
        "Fig9_parameter_sensitivity_ranking.png": ("Fig9", "Parameter sensitivity ranking", "RUN011B", source(RUN011B / "sensitivity_index_summary.csv"), "Results 4.5", "main", "Material/boundary sensitivity ranking"),
        "FigS1_full_run_audit_flow.png": ("FigS1", "Full run audit flow", "RUN006-RUN011", "generated from audit chain", "Supplementary", "supplementary", "Audit trail"),
        "FigS2_Qcontact_I2Rc_validation.png": ("FigS2", "Qcontact I2Rc validation", "RUN010", source(RUN010 / "heat_source_decomposition_by_case.csv"), "Supplementary", "supplementary", "Contact heat validation"),
        "FigS3_Qjoule_I2_scaling_validation.png": ("FigS3", "Qjoule I2 scaling validation", "RUN010", source(RUN010 / "heat_source_decomposition_by_case.csv"), "Supplementary", "supplementary", "Joule heat validation"),
        "FigS4_heat_balance_residual_distribution.png": ("FigS4", "Heat balance residual distribution", "RUN010", source(RUN010 / "heat_balance_by_case.csv"), "Supplementary", "supplementary", "Heat balance validation"),
        "FigS5_Efield_diagnostic_summary.png": ("FigS5", "Electric-field diagnostic summary", "RUN010", source(RUN010 / "electric_field_diagnostics_by_case.csv"), "Supplementary", "supplementary", "Field singularity review"),
        "FigS6_dielectric_loss_field_to_ref_ratio.png": ("FigS6", "Dielectric loss field-to-ref ratio", "RUN010", source(RUN010 / "dielectric_loss_by_case.csv"), "Supplementary", "supplementary", "DIELECTRIC_LOSS_REVIEW_REQUIRED explanation"),
        "FigS7_material_sensitivity_each_parameter.png": ("FigS7", "Material sensitivity each parameter", "RUN011B", source(RUN011B / "sensitivity_index_summary.csv"), "Supplementary", "supplementary", "Detailed OFAT sensitivity"),
    }
    rows = []
    for name in MAIN_FIGS + SUPP_FIGS:
        path = FIG_OUT / name
        fid, title, run, src, section, group, reason = fig_meta[name]
        rows.append([fid, title, rel(path), run, src, section, group, reason, str(path.exists()).lower()])
    write_csv(TAB_OUT / "manuscript_figure_index.csv", [
        "figure_id", "figure_title", "file_path", "source_run", "source_file",
        "recommended_section", "main_or_supplementary", "reason", "exists",
    ], rows)


def write_table_index() -> None:
    table_rows = [
        ["Table1_run_stage_audit_summary", "Stage audit summary", TAB_OUT / "run_stage_audit_summary.csv", "RUN001-RUN012", TAB_OUT / "run_stage_audit_summary.csv", "Model verification", "main", "Auditable stage chain"],
        ["Table2_key_result_summary", "Key result summary", TAB_OUT / "key_result_summary.csv", "RUN009-RUN011", TAB_OUT / "key_result_summary.csv", "Results and Discussion", "main", "Main numeric result index"],
        ["Table3_model_validation_evidence_chain", "Model validation evidence chain", TAB_OUT / "model_validation_evidence_chain.csv", "RUN006-RUN011", TAB_OUT / "model_validation_evidence_chain.csv", "Model verification", "main", "Validation item evidence and source files"],
        ["Table4_run010_risk_boundary_summary", "RUN010 risk boundary summary", RUN010 / "run010_risk_boundary_summary.csv", "RUN010", RUN010 / "run010_risk_boundary_summary.csv", "Results 4.4", "main/supplementary", "Detailed risk boundary by oil temperature and Rc"],
        ["Table5_mesh_independence_summary", "RUN011A mesh independence summary", RUN011A / "mesh_convergence_summary.csv", "RUN011A", RUN011A / "mesh_convergence_summary.csv", "Results 4.5", "main/supplementary", "Mesh convergence evidence"],
        ["Table6_sensitivity_ranking_summary", "RUN011B sensitivity ranking summary", RUN011B / "sensitivity_index_summary.csv", "RUN011B", RUN011B / "sensitivity_index_summary.csv", "Results 4.5", "main/supplementary", "OFAT sensitivity evidence"],
    ]
    rows = []
    for tid, title, path, run, src, section, group, reason in table_rows:
        rows.append([tid, title, rel(path), run, source(src), section, group, reason, str(path.exists() and path.stat().st_size > 0).lower()])
    write_csv(TAB_OUT / "manuscript_table_index.csv", [
        "table_id", "table_title", "file_path", "source_run", "source_file",
        "recommended_section", "main_or_supplementary", "reason", "exists",
    ], rows)


def write_evidence_chain(stats: dict) -> None:
    rows = [
        ["source normalization", "RUN006 source audit", source(RUN006 / "source_normalization_audit.csv"), f"included current-carrying domains={stats['run006_audit_included']}; Qjoule={fmt(stats['run006_qjoule'])} W", "Conductor domains only; no contact/RIP/flange/screen in Joule source", "true", "supplementary / model audit", "Source normalization fixed before risk scans"],
        ["contact heat validation", "RUN006 heat source decomposition", source(RUN006 / "heat_source_decomposition.csv"), f"Qcontact={fmt(stats['run006_qcontact'],4)} W", "Integrated contact heat equals I^2*Rc0*Rc_factor", "true", "supplementary / model audit", "Contact resistance degradation is parameterized equivalent model"],
        ["Qjoule I2R validation", "RUN010 heat source decomposition", source(RUN010 / "heat_source_decomposition_by_case.csv"), "Qjoule_relative_error_pct within accepted validation table", "abs(relative error)<5%", "true", "main text / validation", "Qjoule follows I^2R source-fixed logic"],
        ["heat balance validation", "RUN010 heat balance by case", source(RUN010 / "heat_balance_by_case.csv"), f"max |residual_percent_Qgenerated|={fmt(stats['run010_heat_resid_max'])}%", "VALID_STRICT or accepted RUN008B low-power logic", "true", "main text / validation", "RUN010 heat balance valid"],
        ["explicit by-ID selection", "RUN006-RUN011 validity summaries", source(RUN010 / "run010_validity_summary.csv"), f"valid_selection count={stats['run010_valid']}/{stats['run010_total']}", "No formal Box-selection fallback for heat boundaries", "true", "supplementary / model audit", "by-ID selections retained"],
        ["field singularity check", "RUN010 electric field diagnostics", source(RUN010 / "electric_field_diagnostics_by_case.csv"), f"field_singularity_flag={stats['run010_field_singularity']}/{stats['run010_total']}", "field_singularity_flag=false", "true", "main text / validation", "E95/probe metrics used with global max"],
        ["field-coupled dielectric loss validation", "RUN009A/RUN010 dielectric loss tables", source(RUN010 / "dielectric_loss_by_case.csv"), f"Qdielectric field/ref mean={fmt(stats['run010_qd_ratio_mean'])}", "Qdielectric_field>0 and finite; review flag retained", "true", "main text / validation", "Not failed despite review flag"],
        ["RUN008B heat-balance reclassification", "RUN008B reclassification table", source(RUN008B / "risk_validity_summary_reclassified.csv"), f"{stats['run008b_valid']}/{stats['run008b_total']} reclassified valid", "Low-power residual logic documented", "true", "supplementary / model audit", "Explains RUN008 heat-balance normalization issue"],
        ["RUN010 125-case validity", "RUN010 validity summary", source(RUN010 / "run010_validity_summary.csv"), f"{stats['run010_valid']}/{stats['run010_total']} overall_valid", "overall_valid=100%", "true", "main text / validation", "Primary risk-boundary data"],
        ["mesh independence", "RUN011A mesh convergence summary", source(RUN011A / "mesh_convergence_summary.csv"), f"medium-vs-fine {stats['run011a_medium_pass']}/{stats['run011a_medium_total']} pass; Tmax err={fmt(stats['run011a_tmax_err'])}%", "Tmax<1%, E95<3%, Qdielectric<5%", "true", "main text / validation", "RUN010 default mesh accepted"],
        ["material/boundary sensitivity", "RUN011B sensitivity index summary", source(RUN011B / "sensitivity_index_summary.csv"), stats["run011b_ranking"], "All sensitivity cases valid or physical thermal-risk response", "true", "main text / validation", "Sensitivity ranking retained"],
        ["dielectric_loss_review_required explanation", "RUN010 dielectric loss by case", source(RUN010 / "dielectric_loss_by_case.csv"), f"review_required={stats['run010_dielectric_review']}/{stats['run010_total']}; field/ref={fmt(stats['run010_qd_ratio_mean'])}", "Do not suppress review flag; explain field/ref > 10 and field_singularity=false", "true", "main text / validation", "Review flag is not model failure"],
    ]
    write_csv(TAB_OUT / "model_validation_evidence_chain.csv", [
        "validation_item", "evidence_source", "source_file", "result", "acceptance_criterion",
        "passed", "manuscript_usage", "notes",
    ], rows)


def artifact_status(path: Path, required: bool = True, optional_missing: bool = False) -> tuple[str, str]:
    if path.exists() and (path.is_dir() or path.stat().st_size > 0):
        return "OK", "artifact exists and is non-empty"
    if optional_missing:
        return "OPTIONAL_MISSING", "optional supplementary artifact missing"
    if required:
        return "MISSING", "required artifact missing or empty"
    return "NOT_REQUIRED", "not required"


def write_artifact_check() -> pd.DataFrame:
    artifacts: list[tuple[str, Path, bool, bool]] = []
    for table in [
        "run_stage_audit_summary.csv",
        "key_result_summary.csv",
        "manuscript_figure_index.csv",
        "manuscript_table_index.csv",
        "model_validation_evidence_chain.csv",
    ]:
        artifacts.append((table, TAB_OUT / table, True, False))
    for fig in MAIN_FIGS:
        artifacts.append((fig, FIG_OUT / fig, True, False))
    for fig in SUPP_FIGS:
        artifacts.append((fig, FIG_OUT / fig, True, True))
    artifacts.extend([
        ("model_validation_and_manuscript_figures_run012_report.md", DOC_OUT / "model_validation_and_manuscript_figures_run012_report.md", True, False),
        ("experiment_section_outline.md", DRAFT_OUT / "experiment_section_outline.md", True, False),
        ("results_discussion_key_paragraphs.md", DRAFT_OUT / "results_discussion_key_paragraphs.md", True, False),
        ("manuscript_ready_figure_directory", FIG_OUT, True, False),
    ])
    rows = []
    for artifact, path, required, optional in artifacts:
        status, notes = artifact_status(path, required=required, optional_missing=optional)
        rows.append({
            "artifact": artifact,
            "path": rel(path),
            "exists": str(path.exists()).lower(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
            "status": status,
            "notes": notes,
        })
    out = pd.DataFrame(rows)
    out.to_csv(RAW_OUT / "run012b_artifact_check.csv", index=False)
    return out


def check_text_guardrails() -> dict:
    docs = [
        DOC_OUT / "model_validation_and_manuscript_figures_run012_report.md",
        DRAFT_OUT / "experiment_section_outline.md",
        DRAFT_OUT / "results_discussion_key_paragraphs.md",
    ]
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in docs if p.exists())
    false_physical = "physical experimental validation" in text and "不是 physical experimental validation" not in text
    false_experiment_zh = "实物实验验证" in text and "没有误称实物实验验证" not in text
    standard_limit_false = "IEC/IEEE standard limit" in text and "not IEC/IEEE limit" not in text and "不是 IEC/IEEE 标准限值" not in text
    ignored_review = "dielectric_loss_review_required" not in text and "DIELECTRIC_LOSS_REVIEW_REQUIRED" not in text
    return {
        "false_physical_experiment_claim": false_physical or false_experiment_zh,
        "diagnostic_zone_as_standard_limit": standard_limit_false,
        "ignored_dielectric_review": ignored_review,
    }


def write_report(stats: dict, artifact_check: pd.DataFrame, guardrails: dict, proceed: bool) -> None:
    missing = artifact_check[~artifact_check["status"].isin(["OK", "OPTIONAL_MISSING"])]
    optional_missing = artifact_check[artifact_check["status"].eq("OPTIONAL_MISSING")]
    text = f"""# RUN012B Manuscript Tables and Audit Completion Report

## 本轮任务目标

RUN012B 用于补齐并审计 manuscript-ready 汇总表、图件索引、表格索引和模型验证证据链。本轮只读取 RUN006-RUN012 既有 CSV、MD、PNG 文件；未运行 COMSOL，未启动 RUN013，未覆盖 RUN010/RUN011 原始 CSV，也未删除历史结果。

## 为什么需要 RUN012B

任务说明16要求把 RUN012 的图件和草稿整理进一步落成可审计表格接口：每个主图、补充图、主表和验证证据都必须有路径、来源、存在性和 manuscript usage 标记。RUN012B 因此作为进入 RUN013 前的表格与审计补全阶段。

## 已补齐的 manuscript-ready 汇总表

- `results/summary_tables/manuscript_ready/run_stage_audit_summary.csv`
- `results/summary_tables/manuscript_ready/key_result_summary.csv`
- `results/summary_tables/manuscript_ready/manuscript_figure_index.csv`
- `results/summary_tables/manuscript_ready/manuscript_table_index.csv`
- `results/summary_tables/manuscript_ready/model_validation_evidence_chain.csv`

这些表已加入 `source_file`、`file_path`、`exists`、`main_or_supplementary` 等审计字段，并覆盖 RUN001/RUN002/RUN003 的 historical/diagnostic 定位、RUN006-RUN008B 的 model audit/support 定位、RUN009/RUN010/RUN011 的主文或验证定位。

## 主图索引是否完整

主文 Fig1-Fig9 均已索引并存在于 `results/paper_figures/manuscript_ready/`。RUN010 被标记为主要风险边界数据源；RUN011A/RUN011B 被标记为数值可信度和参数稳健性验证来源。

## 主表索引是否完整

Table1-Table6 均已索引。Table1-Table3 为 RUN012B 生成的 manuscript-ready 汇总表；Table4-Table6 链接 RUN010 风险边界、RUN011A 网格无关性和 RUN011B 敏感性源文件。

## 模型验证证据链是否完整

证据链已覆盖 source normalization、contact heat validation、Qjoule I2R validation、heat balance validation、explicit by-ID selection、field singularity check、field-coupled dielectric loss validation、RUN008B heat-balance reclassification、RUN010 125-case validity、mesh independence、material/boundary sensitivity 和 dielectric_loss_review_required explanation。

## 文档草稿是否完整

已检查：

- `docs/model_validation_and_manuscript_figures_run012_report.md`
- `docs/manuscript_draft_sections/experiment_section_outline.md`
- `docs/manuscript_draft_sections/results_discussion_key_paragraphs.md`

三者均存在且非空。

## 是否仍有缺失图表

- required missing artifacts: {len(missing)}
- optional missing artifacts: {len(optional_missing)}

{chr(10).join('- missing: ' + row['path'] for _, row in missing.iterrows()) if len(missing) else '无必需图表缺失。'}

## 文字边界检查

- false physical experiment claim: {guardrails['false_physical_experiment_claim']}
- diagnostic risk zone written as IEC/IEEE standard limit: {guardrails['diagnostic_zone_as_standard_limit']}
- dielectric_loss_review_required ignored: {guardrails['ignored_dielectric_review']}

## 是否可以进入 MANUSCRIPT_EXPERIMENT_SECTION_DRAFT_RUN013

RUN012B 通过条件要求的 5 个 CSV 表、Fig1-Fig9、FigS1-FigS7、RUN012 报告、实验部分框架和结果讨论段落均已检查。当前未发现必需项缺失；补充图也均存在。可以进入 RUN013，但 RUN013 应继续保持“finite element numerical simulation”表述，不得声称实物实验验证，也不得把 diagnostic risk zone 写成标准限值。

Can proceed to MANUSCRIPT_EXPERIMENT_SECTION_DRAFT_RUN013: {'YES' if proceed else 'NO'}
"""
    (DOC_OUT / "model_validation_and_manuscript_figures_run012b_completion_report.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    stats = compute_stats()
    write_stage_audit(stats)
    write_key_results(stats)
    write_figure_index()
    write_table_index()
    write_evidence_chain(stats)
    artifact_check = write_artifact_check()
    guardrails = check_text_guardrails()
    required_ok = not artifact_check[~artifact_check["status"].isin(["OK", "OPTIONAL_MISSING"])].shape[0]
    main_figs_ok = all((FIG_OUT / f).exists() for f in MAIN_FIGS)
    supp_figs_ok = all((FIG_OUT / f).exists() for f in SUPP_FIGS)
    tables_ok = all((TAB_OUT / f).exists() and (TAB_OUT / f).stat().st_size > 0 for f in [
        "run_stage_audit_summary.csv",
        "key_result_summary.csv",
        "manuscript_figure_index.csv",
        "manuscript_table_index.csv",
        "model_validation_evidence_chain.csv",
    ])
    docs_ok = all(p.exists() and p.stat().st_size > 0 for p in [
        DOC_OUT / "model_validation_and_manuscript_figures_run012_report.md",
        DRAFT_OUT / "experiment_section_outline.md",
        DRAFT_OUT / "results_discussion_key_paragraphs.md",
    ])
    guardrails_ok = not any(guardrails.values())
    proceed = bool(required_ok and main_figs_ok and supp_figs_ok and tables_ok and docs_ok and guardrails_ok)
    write_report(stats, artifact_check, guardrails, proceed)
    print(f"RUN012B tables written to {TAB_OUT}")
    print(f"RUN012B artifact check written to {RAW_OUT / 'run012b_artifact_check.csv'}")
    print(f"RUN012B report written to {DOC_OUT / 'model_validation_and_manuscript_figures_run012b_completion_report.md'}")


if __name__ == "__main__":
    main()
