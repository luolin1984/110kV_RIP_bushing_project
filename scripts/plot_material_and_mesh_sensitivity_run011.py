"""Postprocess MATERIAL_AND_MESH_SENSITIVITY_RUN011.

This script reads COMSOL CSV exports from RUN011A/RUN011B, computes mesh
convergence and one-factor-at-a-time sensitivity indices, creates diagnostic
figures, and writes the RUN011 stage report. It does not run COMSOL and does
not modify RUN010 or earlier raw exports.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
RUN_ID = "MATERIAL_AND_MESH_SENSITIVITY_RUN011"
RUN_ROOT = PROJECT / "results" / "raw_comsol_exports" / RUN_ID
RUN011A = RUN_ROOT / "RUN011A_MESH_INDEPENDENCE"
RUN011B = RUN_ROOT / "RUN011B_MATERIAL_BOUNDARY_SENSITIVITY"
FIG_DIR = PROJECT / "results" / "paper_figures" / "material_and_mesh_sensitivity_run011"
REPORT = PROJECT / "docs" / "material_and_mesh_sensitivity_run011_report.md"

MESH_LEVELS = ["coarse", "medium", "fine"]
MESH_THRESHOLDS = {
    "err_Tmax_global_pct": 1.0,
    "err_Tmax_RIP_pct": 1.0,
    "err_Tmax_contact_pct": 1.0,
    "err_E95_RIP_pct": 3.0,
    "err_Qdielectric_pct": 5.0,
}
ACCEPTED_HEAT = {"VALID_STRICT", "VALID_LOW_POWER_RECLASSIFIED"}
BASELINE_BY_PARAMETER = {
    "k_RIP_multiplier": 1.0,
    "tan_delta_multiplier": 1.0,
    "epsr_RIP": 4.2,
    "h_oil": 300.0,
    "h_air": 20.0,
    "Rc0_multiplier": 1.0,
}


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT_TITLE = font(34, True)
FONT_BOLD = font(24, True)
FONT = font(19)
FONT_SMALL = font(15)
FONT_TINY = font(12)


def canvas(title: str, w: int = 1800, h: int = 960):
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 76), fill="#111827")
    draw.text((32, 21), title, fill="white", font=FONT_TITLE)
    return img, draw


def save(img: Image.Image, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    img.save(FIG_DIR / name)


def text(draw, xy, s: str, fill="#111827", fnt=FONT) -> None:
    draw.text(xy, s, fill=fill, font=fnt)


def centered(draw, box, s: str, fill="#111827", fnt=FONT_SMALL) -> None:
    bbox = draw.textbbox((0, 0), s, font=fnt)
    x = (box[0] + box[2] - bbox[2] + bbox[0]) / 2
    y = (box[1] + box[3] - bbox[3] + bbox[1]) / 2
    draw.text((x, y), s, fill=fill, font=fnt)


def finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except Exception:
        return False


def pct_error(value: float, reference: float) -> float:
    if not finite(value) or not finite(reference) or abs(reference) < 1e-12:
        return float("nan")
    return abs(float(value) - float(reference)) / abs(float(reference)) * 100.0


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def risk_statuses(series: pd.Series) -> dict[str, int]:
    return {str(k): int(v) for k, v in series.value_counts().sort_index().items()}


def read_inputs():
    mesh_metrics = pd.read_csv(RUN011A / "mesh_metrics.csv")
    mesh_cases = pd.read_csv(RUN011A / "mesh_case_matrix.csv")
    sensitivity_metrics = pd.read_csv(RUN011B / "sensitivity_metrics.csv")
    sensitivity_cases = pd.read_csv(RUN011B / "sensitivity_case_matrix.csv")
    return mesh_metrics, mesh_cases, sensitivity_metrics, sensitivity_cases


def compute_mesh_summary(mesh_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for case_id, group in mesh_metrics.groupby("case_id"):
        fine = group[group["mesh_level"] == "fine"]
        if fine.empty:
            for _, row in group.iterrows():
                rows.append({
                    "case_id": case_id,
                    "mesh_level": row["mesh_level"],
                    "reference_mesh_level": "fine",
                    "err_Tmax_global_pct": float("nan"),
                    "err_Tmax_RIP_pct": float("nan"),
                    "err_Tmax_contact_pct": float("nan"),
                    "err_E95_RIP_pct": float("nan"),
                    "err_Qdielectric_pct": float("nan"),
                    "heat_balance_valid": False,
                    "field_singularity_flag": row.get("field_singularity_flag", True),
                    "medium_vs_fine_pass": False,
                    "status": "MISSING_FINE_REFERENCE",
                    "notes": "fine mesh reference is missing",
                })
            continue
        ref = fine.iloc[0]
        for _, row in group.iterrows():
            errors = {
                "err_Tmax_global_pct": pct_error(row["Tmax_global_C"], ref["Tmax_global_C"]),
                "err_Tmax_RIP_pct": pct_error(row["Tmax_RIP_C"], ref["Tmax_RIP_C"]),
                "err_Tmax_contact_pct": pct_error(row["Tmax_contact_C"], ref["Tmax_contact_C"]),
                "err_E95_RIP_pct": pct_error(row["E95_RIP_V_per_m"], ref["E95_RIP_V_per_m"]),
                "err_Qdielectric_pct": pct_error(row["Qdielectric_RIP_field_W"], ref["Qdielectric_RIP_field_W"]),
            }
            heat_valid = str(row["heat_balance_status"]) in ACCEPTED_HEAT
            singular = str(row["field_singularity_flag"]).lower() == "true"
            threshold_pass = all(errors[key] < threshold for key, threshold in MESH_THRESHOLDS.items())
            status_ok = str(row["status"]) in {"SOLVED_VALID", "SOLVED_THERMAL_WARNING", "SOLVED_THERMAL_RISK"}
            if row["mesh_level"] == "fine":
                medium_pass = True
                status = "REFERENCE_FINE"
                notes = "fine mesh used as convergence reference"
            elif row["mesh_level"] == "medium":
                medium_pass = bool(threshold_pass and heat_valid and not singular and status_ok)
                status = "PASS_MEDIUM_VS_FINE" if medium_pass else "FAIL_MEDIUM_VS_FINE"
                notes = "medium mesh compared against fine mesh"
            else:
                medium_pass = False
                status = "COARSE_DIAGNOSTIC_ONLY"
                notes = "coarse mesh is diagnostic and is not the acceptance basis"
            rows.append({
                "case_id": case_id,
                "mesh_level": row["mesh_level"],
                "reference_mesh_level": "fine",
                **errors,
                "heat_balance_valid": heat_valid,
                "field_singularity_flag": singular,
                "medium_vs_fine_pass": medium_pass,
                "status": status,
                "notes": notes,
            })
    out = pd.DataFrame(rows)
    out.to_csv(RUN011A / "mesh_convergence_summary.csv", index=False)
    return out


def sensitivity_index(value: float, base_value: float, parameter_value: float, parameter_base: float) -> float:
    if (
        not finite(value)
        or not finite(base_value)
        or not finite(parameter_value)
        or not finite(parameter_base)
        or abs(base_value) < 1e-12
        or abs(parameter_base) < 1e-12
        or abs(parameter_value - parameter_base) < 1e-12
    ):
        return float("nan")
    return ((float(value) - float(base_value)) / abs(float(base_value))) / (
        (float(parameter_value) - float(parameter_base)) / abs(float(parameter_base))
    )


def compute_sensitivity_summary(sens_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (base_case, parameter_name), group in sens_metrics.groupby(["base_case", "parameter_name"]):
        parameter_base = BASELINE_BY_PARAMETER[parameter_name]
        baseline_rows = group[(group["parameter_value"].astype(float) - parameter_base).abs() < 1e-9]
        if baseline_rows.empty:
            baseline = group.iloc[(group["parameter_value"].astype(float) - parameter_base).abs().argmin()]
        else:
            baseline = baseline_rows.iloc[0]
        for _, row in group.iterrows():
            parameter_value = float(row["parameter_value"])
            s_tmax = sensitivity_index(row["Tmax_global_C"], baseline["Tmax_global_C"], parameter_value, parameter_base)
            s_contact = sensitivity_index(row["Tmax_contact_C"], baseline["Tmax_contact_C"], parameter_value, parameter_base)
            s_qd = sensitivity_index(row["Qdielectric_RIP_field_W"], baseline["Qdielectric_RIP_field_W"], parameter_value, parameter_base)
            rows.append({
                "sensitivity_case_id": row["sensitivity_case_id"],
                "base_case": base_case,
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
                "parameter_multiplier": row["parameter_multiplier"],
                "baseline_value": parameter_base,
                "Tmax_global_baseline_C": baseline["Tmax_global_C"],
                "Tmax_global_delta_C": row["Tmax_global_C"] - baseline["Tmax_global_C"],
                "S_Tmax_global": s_tmax,
                "Tmax_contact_baseline_C": baseline["Tmax_contact_C"],
                "Tmax_contact_delta_C": row["Tmax_contact_C"] - baseline["Tmax_contact_C"],
                "S_Tmax_contact": s_contact,
                "Qdielectric_baseline_W": baseline["Qdielectric_RIP_field_W"],
                "Qdielectric_delta_W": row["Qdielectric_RIP_field_W"] - baseline["Qdielectric_RIP_field_W"],
                "S_Qdielectric": s_qd,
                "heat_balance_status": row["heat_balance_status"],
                "field_singularity_flag": row["field_singularity_flag"],
                "dielectric_loss_review_required": row["dielectric_loss_review_required"],
                "status": row["status"],
                "notes": "local normalized OFAT sensitivity; baseline rows have NaN sensitivity",
            })
    out = pd.DataFrame(rows)
    out.to_csv(RUN011B / "sensitivity_index_summary.csv", index=False)
    return out


def plot_polyline(draw, box, x_labels, series, y_label, colors):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d1d5db", width=2)
    all_vals = [v for _, vals in series for v in vals if finite(v)]
    if not all_vals:
        return
    ymin, ymax = min(all_vals), max(all_vals)
    pad = (ymax - ymin) * 0.14 if ymax > ymin else 1.0
    ymin -= pad
    ymax += pad
    left, right = x0 + 92, x1 - 34
    top, bottom = y0 + 58, y1 - 76
    draw.line((left, bottom, right, bottom), fill="#9ca3af", width=2)
    draw.line((left, top, left, bottom), fill="#9ca3af", width=2)
    for i, lab in enumerate(x_labels):
        x = left + i * (right - left) / max(1, len(x_labels) - 1)
        centered(draw, (x - 50, bottom + 16, x + 50, bottom + 44), str(lab), fnt=FONT_TINY)
    text(draw, (x0 + 18, y0 + 16), y_label, fill="#4b5563", fnt=FONT_SMALL)
    for si, (label, vals) in enumerate(series):
        pts = []
        for i, val in enumerate(vals):
            if not finite(val):
                continue
            x = left + i * (right - left) / max(1, len(x_labels) - 1)
            y = bottom - (float(val) - ymin) / (ymax - ymin) * (bottom - top)
            pts.append((x, y))
        if len(pts) >= 2:
            draw.line(pts, fill=colors[si % len(colors)], width=4)
        for x, y in pts:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=colors[si % len(colors)])
        text(draw, (right - 260, top + 6 + si * 25), label, fill=colors[si % len(colors)], fnt=FONT_TINY)


def plot_bar(draw, box, labels, values, title, threshold=None, colors=None):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d1d5db", width=2)
    vals = [float(v) for v in values if finite(v)]
    if not vals:
        return
    ymin = min(0.0, min(vals))
    ymax = max(0.0, max(vals))
    if threshold is not None:
        ymax = max(ymax, threshold)
        ymin = min(ymin, -threshold)
    pad = (ymax - ymin) * 0.14 if ymax > ymin else 1.0
    ymin -= pad
    ymax += pad
    left, right = x0 + 76, x1 - 26
    top, bottom = y0 + 62, y1 - 102
    zero = bottom - (0.0 - ymin) / (ymax - ymin) * (bottom - top)
    draw.line((left, zero, right, zero), fill="#9ca3af", width=2)
    if threshold is not None:
        for th in [threshold, -threshold]:
            yy = bottom - (th - ymin) / (ymax - ymin) * (bottom - top)
            draw.line((left, yy, right, yy), fill="#c53030", width=2)
    n = len(values)
    span = right - left
    bw = max(10, span / max(1, n) * 0.68)
    for i, (lab, val) in enumerate(zip(labels, values)):
        x = left + (i + 0.5) * span / n
        y = bottom - (float(val) - ymin) / (ymax - ymin) * (bottom - top) if finite(val) else zero
        color = colors[i % len(colors)] if colors else "#2563eb"
        draw.rectangle((x - bw / 2, min(y, zero), x + bw / 2, max(y, zero)), fill=color)
        centered(draw, (x - 55, bottom + 12, x + 55, bottom + 42), str(lab), fnt=FONT_TINY)
    text(draw, (x0 + 18, y0 + 16), title, fill="#4b5563", fnt=FONT_SMALL)


def create_figures(mesh_metrics: pd.DataFrame, mesh_summary: pd.DataFrame, sens_summary: pd.DataFrame) -> None:
    colors = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"]

    img, draw = canvas("RUN011A mesh convergence: Tmax")
    cases = list(mesh_metrics["case_id"].drop_duplicates())
    boxes = [(44 + i * 580, 118, 44 + i * 580 + 530, 860) for i in range(3)]
    for box, case_id in zip(boxes, cases):
        group = mesh_metrics[mesh_metrics["case_id"] == case_id].set_index("mesh_level").reindex(MESH_LEVELS)
        series = [
            ("Tmax_global", group["Tmax_global_C"].tolist()),
            ("Tmax_RIP", group["Tmax_RIP_C"].tolist()),
            ("Tmax_contact", group["Tmax_contact_C"].tolist()),
        ]
        plot_polyline(draw, box, MESH_LEVELS, series, case_id, colors)
    text(draw, (62, 900), "medium autoMeshSize=8 is the RUN010 default; fine mesh is the reference.", fnt=FONT_SMALL)
    save(img, "fig01_mesh_convergence_Tmax.png")

    img, draw = canvas("RUN011A mesh convergence: E95 and Qdielectric")
    boxes = [(70, 132, 850, 850), (950, 132, 1730, 850)]
    for box, col, title in [
        (boxes[0], "E95_RIP_V_per_m", "E95_RIP_V_per_m"),
        (boxes[1], "Qdielectric_RIP_field_W", "Qdielectric_RIP_field_W"),
    ]:
        series = []
        for case_id in cases:
            group = mesh_metrics[mesh_metrics["case_id"] == case_id].set_index("mesh_level").reindex(MESH_LEVELS)
            series.append((case_id.replace("CASE_", ""), group[col].tolist()))
        plot_polyline(draw, box, MESH_LEVELS, series, title, colors)
    save(img, "fig02_mesh_convergence_E95_Qdielectric.png")

    img, draw = canvas("RUN011A medium-vs-fine error summary")
    medium = mesh_summary[mesh_summary["mesh_level"] == "medium"].copy()
    labels = [x.replace("CASE_", "") for x in medium["case_id"]]
    metrics = list(MESH_THRESHOLDS.keys())
    panel_w = 520
    for i, metric in enumerate(metrics[:3]):
        plot_bar(draw, (50 + i * 570, 130, 50 + i * 570 + panel_w, 500), labels, medium[metric].tolist(), metric, threshold=MESH_THRESHOLDS[metric], colors=colors)
    for i, metric in enumerate(metrics[3:]):
        plot_bar(draw, (330 + i * 620, 560, 330 + i * 620 + 520, 900), labels, medium[metric].tolist(), metric, threshold=MESH_THRESHOLDS[metric], colors=colors)
    save(img, "fig03_mesh_error_summary.png")

    nonbase = sens_summary[sens_summary["parameter_value"].astype(float) != sens_summary["baseline_value"].astype(float)].copy()
    for filename, col, title in [
        ("fig04_sensitivity_Tmax_global.png", "S_Tmax_global", "RUN011B normalized sensitivity: Tmax_global"),
        ("fig05_sensitivity_Tmax_contact.png", "S_Tmax_contact", "RUN011B normalized sensitivity: Tmax_contact"),
        ("fig06_sensitivity_Qdielectric.png", "S_Qdielectric", "RUN011B normalized sensitivity: Qdielectric_field"),
    ]:
        img, draw = canvas(title)
        params = list(BASELINE_BY_PARAMETER.keys())
        boxes = [(65, 136, 850, 845), (950, 136, 1735, 845)]
        for box, base_case in zip(boxes, ["SENS_BASELINE", "SENS_HIGH_RISK"]):
            vals = []
            labels2 = []
            for param in params:
                subset = nonbase[(nonbase["base_case"] == base_case) & (nonbase["parameter_name"] == param)]
                finite_vals = [abs(float(v)) for v in subset[col] if finite(v)]
                vals.append(max(finite_vals) if finite_vals else float("nan"))
                labels2.append(param.replace("_multiplier", "").replace("tan_delta", "tan_d").replace("Rc0", "Rc0"))
            plot_bar(draw, box, labels2, vals, base_case + " max |S|", colors=colors)
        save(img, filename)

    ranking = (
        nonbase.groupby("parameter_name")[["S_Tmax_global", "S_Tmax_contact", "S_Qdielectric"]]
        .apply(lambda df: pd.Series({
            "max_abs_S_Tmax_global": df["S_Tmax_global"].abs().max(),
            "max_abs_S_Tmax_contact": df["S_Tmax_contact"].abs().max(),
            "max_abs_S_Qdielectric": df["S_Qdielectric"].abs().max(),
        }))
        .reset_index()
    )
    ranking["ranking_score"] = ranking[["max_abs_S_Tmax_global", "max_abs_S_Tmax_contact", "max_abs_S_Qdielectric"]].max(axis=1)
    ranking = ranking.sort_values("ranking_score", ascending=False)
    img, draw = canvas("RUN011B sensitivity ranking")
    plot_bar(
        draw,
        (120, 150, 1680, 860),
        ranking["parameter_name"].tolist(),
        ranking["ranking_score"].tolist(),
        "max(|S_Tmax_global|, |S_Tmax_contact|, |S_Qdielectric|)",
        colors=colors,
    )
    save(img, "fig07_sensitivity_ranking.png")


def build_report(mesh_metrics: pd.DataFrame, mesh_summary: pd.DataFrame, sens_metrics: pd.DataFrame, sens_summary: pd.DataFrame) -> None:
    medium = mesh_summary[mesh_summary["mesh_level"] == "medium"]
    mesh_pass = bool(len(medium) == 3 and medium["medium_vs_fine_pass"].all())
    mesh_fail_rows = medium[~medium["medium_vs_fine_pass"]]

    sens_heat_valid = sens_metrics["heat_balance_status"].astype(str).isin(ACCEPTED_HEAT).all()
    sens_singularity_ok = not bool_series(sens_metrics["field_singularity_flag"]).any()
    sens_status_ok = not sens_metrics["status"].astype(str).isin(["SOLVE_FAILED", "INVALID_CASE"]).any()
    sens_pass = bool(sens_heat_valid and sens_singularity_ok and sens_status_ok)

    proceed = mesh_pass and sens_pass
    ranking = (
        sens_summary[sens_summary["parameter_value"].astype(float) != sens_summary["baseline_value"].astype(float)]
        .groupby("parameter_name")[["S_Tmax_global", "S_Tmax_contact", "S_Qdielectric"]]
        .apply(lambda df: pd.Series({
            "max_abs_S_Tmax_global": df["S_Tmax_global"].abs().max(),
            "max_abs_S_Tmax_contact": df["S_Tmax_contact"].abs().max(),
            "max_abs_S_Qdielectric": df["S_Qdielectric"].abs().max(),
        }))
        .reset_index()
    )
    ranking["ranking_score"] = ranking[["max_abs_S_Tmax_global", "max_abs_S_Tmax_contact", "max_abs_S_Qdielectric"]].max(axis=1)
    ranking = ranking.sort_values("ranking_score", ascending=False)

    lines = []
    lines.append("# MATERIAL_AND_MESH_SENSITIVITY_RUN011 报告\n")
    lines.append("## 本轮任务目标\n")
    lines.append("本轮用于验证 RUN010 完整电场耦合介质损耗风险扫描的数值可靠性与参数稳健性，包含 RUN011A 网格无关性和 RUN011B 材料/边界单因素敏感性。RUN011 不是 SCI 最终结论，不包含全年气象、暂态仿真或新的 125 组风险边界扫描。\n")
    lines.append("## 与 RUN006-RUN010 的关系\n")
    lines.append("RUN011 继承 RUN006-RUN010 已验证的 source-fixed 导体/接触热归一化、explicit by-ID domain/boundary selection，以及 RUN009/RUN010 的 field-coupled dielectric loss: Qdielectric = omega * epsilon0 * epsr * tan_delta * |E|^2。\n")
    lines.append("## RUN011A 网格无关性设置\n")
    lines.append("- representative cases: CASE_A_BASELINE, CASE_B_HIGH_CONTACT, CASE_C_HIGHEST_PRESSURE\n")
    lines.append("- mesh levels: coarse(autoMeshSize=9), medium(autoMeshSize=8, RUN010 default), fine(autoMeshSize=6)\n")
    lines.append("- acceptance basis: medium-vs-fine errors for Tmax_global/Tmax_RIP/Tmax_contact < 1%, E95 < 3%, Qdielectric < 5%, heat balance valid, field_singularity_flag=false\n")
    lines.append("## RUN011A 结果统计\n")
    lines.append(f"- mesh solve rows: {len(mesh_metrics)}\n")
    lines.append(f"- medium-vs-fine pass: {int(medium['medium_vs_fine_pass'].sum())}/{len(medium)}\n")
    for _, row in medium.iterrows():
        lines.append(
            f"- {row['case_id']}: Tmax_global_err={row['err_Tmax_global_pct']:.3g}%, "
            f"Tmax_RIP_err={row['err_Tmax_RIP_pct']:.3g}%, Tmax_contact_err={row['err_Tmax_contact_pct']:.3g}%, "
            f"E95_err={row['err_E95_RIP_pct']:.3g}%, Qdielectric_err={row['err_Qdielectric_pct']:.3g}%, "
            f"status={row['status']}\n"
        )
    lines.append("## RUN011B 材料/边界敏感性设置\n")
    lines.append("- base cases: SENS_BASELINE(load=1.0, oil=85, Rc=1), SENS_HIGH_RISK(load=1.4, oil=105, Rc=20)\n")
    lines.append("- one-factor-at-a-time parameters: k_RIP_multiplier, tan_delta_multiplier, epsr_RIP, h_oil, h_air, Rc0_multiplier\n")
    lines.append("## RUN011B 结果统计\n")
    lines.append(f"- sensitivity solve rows: {len(sens_metrics)}\n")
    lines.append(f"- heat_balance valid: {int(sens_metrics['heat_balance_status'].astype(str).isin(ACCEPTED_HEAT).sum())}/{len(sens_metrics)}\n")
    lines.append(f"- field_singularity_flag true: {int(bool_series(sens_metrics['field_singularity_flag']).sum())}/{len(sens_metrics)}\n")
    lines.append(f"- status counts: {risk_statuses(sens_metrics['status'])}\n")
    lines.append(f"- dielectric_loss_review_required true: {int(bool_series(sens_metrics['dielectric_loss_review_required']).sum())}/{len(sens_metrics)}\n")
    lines.append("DIELECTRIC_LOSS_REVIEW_REQUIRED 标记被保留，用于提示 field/ref 介质损耗比值仍需在论文阶段解释；该标记本身不等价于模型失败，除非伴随电场奇异、热平衡失效或温度不合理。\n")
    lines.append("## 敏感性排序\n")
    for _, row in ranking.iterrows():
        lines.append(
            f"- {row['parameter_name']}: ranking_score={row['ranking_score']:.4g}, "
            f"max_abs_S_Tmax_global={row['max_abs_S_Tmax_global']:.4g}, "
            f"max_abs_S_Tmax_contact={row['max_abs_S_Tmax_contact']:.4g}, "
            f"max_abs_S_Qdielectric={row['max_abs_S_Qdielectric']:.4g}\n"
        )
    lines.append("## 是否存在无效工况\n")
    if mesh_pass and sens_pass:
        lines.append("RUN011A/RUN011B 未发现阻断性无效工况。若存在 thermal warning，应作为物理风险现象与数值失败区分。\n")
    else:
        lines.append("RUN011 发现未通过项，需要先修正后再进入 RUN012。\n")
        if not mesh_pass:
            lines.append(f"- mesh convergence failures: {mesh_fail_rows['case_id'].tolist()}\n")
        if not sens_pass:
            lines.append(f"- sensitivity heat valid={sens_heat_valid}, singularity_ok={sens_singularity_ok}, status_ok={sens_status_ok}\n")
    lines.append("## 下一步建议\n")
    if proceed:
        lines.append("RUN011 支持进入模型验证与论文图件整理阶段。下一阶段仍应保持 RUN010/RUN011 的审计轨迹，并在正式论文中说明诊断阈值不是 IEC/IEEE 标准限值或材料寿命阈值。\n")
    else:
        lines.append("暂不建议进入 RUN012。优先检查未通过网格工况的局部网格加密、电场屏端评价窗口、介质损耗积分和热边界收支。\n")
    lines.append(f"\nCan proceed to MODEL_VALIDATION_AND_MANUSCRIPT_FIGURES_RUN012: {'YES' if proceed else 'NO'}\n")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    mesh_metrics, _mesh_cases, sens_metrics, _sens_cases = read_inputs()
    mesh_summary = compute_mesh_summary(mesh_metrics)
    sens_summary = compute_sensitivity_summary(sens_metrics)
    create_figures(mesh_metrics, mesh_summary, sens_summary)
    build_report(mesh_metrics, mesh_summary, sens_metrics, sens_summary)
    print(f"Wrote RUN011 postprocess outputs under {RUN_ROOT}")
    print(f"Wrote figures under {FIG_DIR}")
    print(f"Wrote report: {REPORT}")


if __name__ == "__main__":
    main()
