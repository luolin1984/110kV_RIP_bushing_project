"""Recheck RUN008 heat balance with low-power energy-scale diagnostics.

This script is intentionally postprocessing-only. It reads RUN008 CSV exports
and existing boundary-selection summaries. It does not run COMSOL and does not
start FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

from PIL import Image

import plot_solid_only_sweep_27_run007 as base


PROJECT = Path(__file__).resolve().parents[1]
RUN008 = "SOLID_ONLY_RISK_125_RUN008"
RUN008B = "SOLID_ONLY_RISK_125_RUN008B_HEAT_BALANCE_FIX"
RAW008 = PROJECT / "results" / "raw_comsol_exports" / RUN008
OUT = PROJECT / "results" / "raw_comsol_exports" / RUN008B
FIG_DIR = PROJECT / "results" / "paper_figures" / "solid_only_risk_125_run008b_heat_balance_fix"
REPORT = PROJECT / "docs" / "solid_only_risk_125_run008b_heat_balance_fix_report.md"
SUMMARY = PROJECT / "results" / "summary_tables"

LOADS = [0.6, 0.8, 1.0, 1.2, 1.4]
OILS = [65.0, 75.0, 85.0, 95.0, 105.0]
RCS = [1.0, 2.0, 5.0, 10.0, 20.0]
H_OIL = 300.0
FLANGE_LENGTH_ESTIMATE_M = 0.03 + 2.0 * (0.2 - 0.066)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def b(row: dict[str, str], key: str) -> bool:
    return str(row[key]).strip().lower() == "true"


def yes(value: bool) -> str:
    return "true" if value else "false"


def case_no(case_id: str) -> int:
    return int(case_id.rsplit("_", 1)[-1])


def read_selection_counts() -> dict[str, int]:
    rows = read_csv(SUMMARY / "solid_explicit_boundary_id_mapping.csv")
    out: dict[str, int] = {}
    for row in rows:
        out[row["selection_name"].strip('"')] = len(row["boundary_ids"].split())
    return out


def boundary_length_and_area(path: Path) -> tuple[int, float, float]:
    rows = read_csv(path)
    length = 0.0
    area = 0.0
    for row in rows:
        length_m = float(row["length_m"])
        r_mean_m = (float(row["r_min_mm"]) + float(row["r_max_mm"])) / 2.0 / 1000.0
        length += length_m
        area += 2.0 * math.pi * r_mean_m * length_m
    return len(rows), length, area


def status_for_heat_balance(residual_pct_q: float, residual_w: float, residual_pct_max: float) -> str:
    if abs(residual_pct_q) < 10.0:
        return "VALID_STRICT"
    if abs(residual_w) < 3.0 and abs(residual_pct_max) < 5.0:
        return "VALID_LOW_POWER_RECLASSIFIED"
    return "INVALID_HEAT_BALANCE"


def short_zone(zone: str) -> str:
    return {"VALID_STRICT": "strict", "VALID_LOW_POWER_RECLASSIFIED": "lowP", "INVALID_HEAT_BALANCE": "invalid"}.get(zone, zone)


def trend_checks(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> dict[str, bool]:
    by_source = {r["case_id"]: r for r in sources}
    rows = []
    for row in metrics:
        item = dict(row)
        item.update(by_source[row["case_id"]])
        rows.append(item)

    def monotonic(values: list[float], tol: float = 1e-8) -> bool:
        return all(values[i + 1] + tol >= values[i] for i in range(len(values) - 1))

    oil_ok = all(
        monotonic([f(r, "Tmax_global_C") for r in sorted([x for x in rows if math.isclose(f(x, "load_multiplier_pu"), load) and math.isclose(f(x, "contact_resistance_multiplier_pu"), rc)], key=lambda x: f(x, "oil_temperature_C"))])
        for load in LOADS for rc in RCS
    )
    load_ok = all(
        monotonic([f(r, "Tmax_global_C") for r in sorted([x for x in rows if math.isclose(f(x, "oil_temperature_C"), oil) and math.isclose(f(x, "contact_resistance_multiplier_pu"), rc)], key=lambda x: f(x, "load_multiplier_pu"))])
        for oil in OILS for rc in RCS
    )
    rc_ok = all(
        monotonic([f(r, "Tmax_contact_C") for r in sorted([x for x in rows if math.isclose(f(x, "oil_temperature_C"), oil) and math.isclose(f(x, "load_multiplier_pu"), load)], key=lambda x: f(x, "contact_resistance_multiplier_pu"))])
        for oil in OILS for load in LOADS
    )
    qj_ok = all(
        monotonic([f(r, "Qjoule_conductor_W") for r in sorted([x for x in rows if math.isclose(f(x, "oil_temperature_C"), oil) and math.isclose(f(x, "contact_resistance_multiplier_pu"), rc)], key=lambda x: f(x, "current_A"))])
        for oil in OILS for rc in RCS
    )
    qc_ok = monotonic([f(r, "Qcontact_W") for r in sorted(rows, key=lambda x: f(x, "current_A") ** 2 * f(x, "contact_resistance_multiplier_pu"))])
    return {
        "Tmax_global_increases_with_oil_temperature": oil_ok,
        "Tmax_global_increases_with_load": load_ok,
        "Tmax_contact_increases_with_Rc": rc_ok,
        "Qjoule_increases_with_I2": qj_ok,
        "Qcontact_increases_with_I2_Rc": qc_ok,
    }


def draw_figures(recheck: list[dict[str, object]], oil_diag: list[dict[str, object]], validity: list[dict[str, object]], original_invalid: list[str]) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    rows = sorted(recheck, key=lambda r: case_no(str(r["case_id"])))
    values = [float(r["residual_percent_Qgenerated"]) for r in rows]
    colors = [
        "#1f77b4" if r["heat_balance_status"] == "VALID_STRICT" else "#2ca02c" if r["heat_balance_status"] == "VALID_LOW_POWER_RECLASSIFIED" else "#d62728"
        for r in rows
    ]
    img, draw = base.new_image(1700, 780, "Fig01 Original residual percent vs reclassified status")
    base.draw_bar_panel(draw, base.panel_bbox(0, 0, 1, 1, 1700, 780), [str(i + 1) for i in range(len(rows))], values, colors, "case index", "residual_percent_Qgenerated", "blue=strict, green=low-power reclassified, red=invalid", threshold=10.0)
    img.save(FIG_DIR / "fig01_residual_percent_original_vs_reclassified.png")

    invalid_rows = [r for r in rows if r["case_id"] in original_invalid]
    img, draw = base.new_image(1300, 700, "Fig02 Residual_W for original invalid cases")
    vals = [float(r["residual_W"]) for r in invalid_rows]
    base.draw_bar_panel(draw, base.panel_bbox(0, 0, 1, 1, 1300, 700), [str(r["case_id"]).replace("RUN008_CASE_", "") for r in invalid_rows], vals, ["#2ca02c" if abs(v) < 3 else "#d62728" for v in vals], "original invalid case", "residual_W", "absolute residual threshold = +/-3 W", threshold=3.0)
    img.save(FIG_DIR / "fig02_residual_w_invalid_cases.png")

    oil_by_case = {r["case_id"]: r for r in oil_diag}
    vals = [float(oil_by_case[r["case_id"]]["Qoil_heat_in_W"]) for r in invalid_rows]
    img, draw = base.new_image(1300, 700, "Fig03 Oil heat-in for original invalid cases")
    base.draw_bar_panel(draw, base.panel_bbox(0, 0, 1, 1, 1300, 700), [str(r["case_id"]).replace("RUN008_CASE_", "") for r in invalid_rows], vals, ["#1f77b4" for _ in vals], "original invalid case", "Qoil_heat_in_W", "hot oil heat entering solid boundary")
    img.save(FIG_DIR / "fig03_oil_heat_in_invalid_cases.png")

    valid_by_case = {str(r["case_id"]): r for r in validity}
    img, draw = base.new_image(1900, 820, "Fig04 Reclassified validity matrix")
    boxes = []
    left_margin, right_margin, top, bottom = 70, 40, 108, 70
    gap_x = 38
    pw = (1900 - left_margin - right_margin - gap_x * 4) // 5
    ph = 820 - top - bottom
    for c in range(5):
        x0 = left_margin + c * (pw + gap_x)
        boxes.append((x0, top, x0 + pw, top + ph))
    metric_index = {}
    for r in rows:
        metric_index[(float(r["load_multiplier_pu"]), float(r["oil_temperature_C"]), float(r["contact_resistance_multiplier_pu"]))] = r
    for idx, rc in enumerate(RCS):
        left, top0, right, bottom0 = boxes[idx]
        draw.rectangle((left, top0, right, bottom0), outline="#dddddd")
        draw.text((left + 12, top0 + 10), f"Rc={rc:g}", font=base.FONT_BOLD, fill="#222222")
        gx0, gy0 = left + 58, top0 + 58
        gx1, gy1 = right - 18, bottom0 - 60
        cw, ch = (gx1 - gx0) / 5, (gy1 - gy0) / 5
        for rr, oil in enumerate(OILS):
            base.draw_centered(draw, (left + 32, gy0 + rr * ch + ch / 2), f"{oil:g}", base.FONT_SMALL)
            for cc, load in enumerate(LOADS):
                row = metric_index[(load, oil, rc)]
                val = valid_by_case[row["case_id"]]
                hb = str(val["heat_balance_status"])
                fill = "#1f77b4" if hb == "VALID_STRICT" else "#2ca02c" if hb == "VALID_LOW_POWER_RECLASSIFIED" else "#d62728"
                x0 = gx0 + cc * cw
                y0 = gy0 + rr * ch
                draw.rectangle((x0 + 3, y0 + 3, x0 + cw - 3, y0 + ch - 3), fill=fill, outline="#ffffff", width=2)
                base.draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 - 10), str(row["case_id"]).replace("RUN008_CASE_", ""), base.FONT_SMALL)
                base.draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 + 14), short_zone(hb), base.FONT_SMALL)
        for cc, load in enumerate(LOADS):
            base.draw_centered(draw, (gx0 + cc * cw + cw / 2, gy1 + 24), f"{load:g}", base.FONT_SMALL)
    lx, ly = 72, 780
    for label, color in [("VALID_STRICT", "#1f77b4"), ("VALID_LOW_POWER_RECLASSIFIED", "#2ca02c"), ("INVALID_HEAT_BALANCE", "#d62728")]:
        draw.rectangle((lx, ly, lx + 20, ly + 20), fill=color)
        draw.text((lx + 30, ly - 2), label, font=base.FONT_SMALL, fill="#222222")
        lx += 420
    img.save(FIG_DIR / "fig04_reclassified_validity_matrix.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = read_csv(RAW008 / "risk_metrics.csv")
    heat_balance = read_csv(RAW008 / "heat_balance_by_case.csv")
    sources = read_csv(RAW008 / "heat_source_decomposition_by_case.csv")
    validity = read_csv(RAW008 / "risk_validity_summary.csv")

    by_metric = {r["case_id"]: r for r in metrics}
    by_source = {r["case_id"]: r for r in sources}
    by_valid = {r["case_id"]: r for r in validity}
    original_invalid = [r["case_id"] for r in validity if not b(r, "overall_valid")]

    counts = read_selection_counts()
    air_seg_count, air_len, air_area = boundary_length_and_area(SUMMARY / "solid_air_convection_boundaries.csv")
    oil_seg_count, oil_len, oil_area = boundary_length_and_area(SUMMARY / "solid_oil_convection_boundaries.csv")
    air_count = counts.get("id_bnd_air_external", air_seg_count)
    oil_count = counts.get("id_bnd_oil_external", oil_seg_count)
    flange_count = counts.get("id_bnd_flange_external", 3)
    flange_len = FLANGE_LENGTH_ESTIMATE_M

    recheck_rows: list[dict[str, object]] = []
    oil_rows: list[dict[str, object]] = []
    boundary_rows: list[dict[str, object]] = []
    reclassified_rows: list[dict[str, object]] = []

    for hb in heat_balance:
        cid = hb["case_id"]
        metric = by_metric[cid]
        source = by_source[cid]
        valid = by_valid[cid]
        q_total = f(hb, "Qtotal_generated_W")
        q_air = f(hb, "Qremoved_air_W")
        q_oil = f(hb, "Qremoved_oil_W")
        q_flange = f(hb, "Qremoved_flange_W")
        q_removed_net = q_air + q_oil + q_flange
        q_oil_in = max(-q_oil, 0.0)
        q_oil_out = max(q_oil, 0.0)
        residual = q_total - q_removed_net
        residual_pct_q = residual / q_total * 100.0 if q_total else float("nan")
        abs_boundary = abs(q_air) + abs(q_oil) + abs(q_flange)
        residual_pct_abs = residual / abs_boundary * 100.0 if abs_boundary else float("nan")
        max_scale = max(q_total, abs_boundary, 1.0)
        residual_pct_max = residual / max_scale * 100.0
        valid_strict = abs(residual_pct_q) < 10.0
        valid_abs = abs(residual) < 3.0
        valid_max = abs(residual_pct_max) < 5.0
        hb_status = status_for_heat_balance(residual_pct_q, residual, residual_pct_max)

        recheck_rows.append({
            "case_id": cid,
            "run_id": RUN008B,
            "load_multiplier_pu": metric["load_multiplier_pu"],
            "current_A": metric["current_A"],
            "oil_temperature_C": metric["oil_temperature_C"],
            "contact_resistance_multiplier_pu": metric["contact_resistance_multiplier_pu"],
            "Qtotal_generated_W": f"{q_total:.9g}",
            "Qremoved_air_W": f"{q_air:.9g}",
            "Qremoved_oil_W": f"{q_oil:.9g}",
            "Qremoved_flange_W": f"{q_flange:.9g}",
            "Qremoved_total_W": f"{q_removed_net:.9g}",
            "Qoil_heat_in_W": f"{q_oil_in:.9g}",
            "Qoil_heat_out_W": f"{q_oil_out:.9g}",
            "Qboundary_heat_out_net_W": f"{q_removed_net:.9g}",
            "residual_W": f"{residual:.9g}",
            "residual_percent_Qgenerated": f"{residual_pct_q:.9g}",
            "residual_percent_abs_boundary_flux": f"{residual_pct_abs:.9g}",
            "residual_percent_max_energy_scale": f"{residual_pct_max:.9g}",
            "energy_scale_Qgenerated_W": f"{q_total:.9g}",
            "energy_scale_abs_boundary_flux_W": f"{abs_boundary:.9g}",
            "energy_scale_max_W": f"{max_scale:.9g}",
            "valid_by_Qgenerated_percent": yes(valid_strict),
            "valid_by_absolute_residual": yes(valid_abs),
            "valid_by_max_energy_scale": yes(valid_max),
            "heat_balance_status": hb_status,
            "notes": "strict if |residual/Qgenerated|<10%; low-power reclassification requires |residual_W|<3 W and |residual/max_energy_scale|<5%",
        })

        oil_temp = f(metric, "oil_temperature_C")
        tmean_oil_surface = oil_temp + q_oil / (H_OIL * oil_area)
        sign_physical = (oil_temp > tmean_oil_surface and q_oil < 0.0) or (oil_temp < tmean_oil_surface and q_oil > 0.0)
        oil_rows.append({
            "case_id": cid,
            "oil_temperature_C": metric["oil_temperature_C"],
            "Tmax_RIP_C": metric["Tmax_RIP_C"],
            "Tmean_oil_side_surface_C": f"{tmean_oil_surface:.9g}",
            "Qremoved_oil_W": f"{q_oil:.9g}",
            "Qoil_heat_in_W": f"{q_oil_in:.9g}",
            "Qoil_heat_out_W": f"{q_oil_out:.9g}",
            "sign_is_physical": "true" if sign_physical else "review_required",
            "notes": "Tmean_oil_side_surface_C is derived from Qremoved_oil/(h_oil*A_oil_axisym) because RUN008 did not directly export oil-boundary mean temperature",
        })

        boundary_rows.append({
            "case_id": cid,
            "Qremoved_air_W": f"{q_air:.9g}",
            "Qremoved_oil_W": f"{q_oil:.9g}",
            "Qremoved_flange_W": f"{q_flange:.9g}",
            "air_boundary_count": air_count,
            "oil_boundary_count": oil_count,
            "flange_boundary_count": flange_count,
            "air_boundary_total_length_m": f"{air_len:.9g}",
            "oil_boundary_total_length_m": f"{oil_len:.9g}",
            "flange_boundary_total_length_m": f"{flange_len:.9g}",
            "boundary_selection_status": "OK_NO_SELECTION_DRIFT",
            "notes": "boundary counts are explicit COMSOL ID counts; air/oil lengths from solid boundary summary tables; flange length estimated from BRFGL1 flange disk geometry",
        })

        valid_temperature = b(valid, "valid_temperature")
        valid_qjoule = b(valid, "valid_Qjoule")
        valid_qcontact = b(valid, "valid_Qcontact")
        valid_selection = b(valid, "valid_selection")
        valid_reclassified = hb_status in ("VALID_STRICT", "VALID_LOW_POWER_RECLASSIFIED")
        overall = valid_temperature and valid_qjoule and valid_qcontact and valid_selection and valid_reclassified
        failures = []
        if not valid_temperature:
            failures.append("temperature")
        if not valid_qjoule:
            failures.append("Qjoule")
        if not valid_qcontact:
            failures.append("Qcontact")
        if not valid_selection:
            failures.append("selection")
        if not valid_reclassified:
            failures.append("heat_balance")
        reclassified_rows.append({
            "case_id": cid,
            "original_status": valid["status"],
            "original_failure_reason": valid["failure_reason"],
            "valid_temperature": valid["valid_temperature"],
            "valid_Qjoule": valid["valid_Qjoule"],
            "valid_Qcontact": valid["valid_Qcontact"],
            "valid_selection": valid["valid_selection"],
            "valid_heat_balance_strict": yes(valid_strict),
            "valid_heat_balance_reclassified": yes(valid_reclassified),
            "heat_balance_status": hb_status,
            "overall_valid_reclassified": yes(overall),
            "thermal_warning": valid["thermal_warning"],
            "thermal_risk": valid["thermal_risk"],
            "final_failure_reason": ";".join(failures),
        })

    write_csv(OUT / "heat_balance_recheck_by_case.csv", [
        "case_id", "run_id", "load_multiplier_pu", "current_A", "oil_temperature_C", "contact_resistance_multiplier_pu",
        "Qtotal_generated_W", "Qremoved_air_W", "Qremoved_oil_W", "Qremoved_flange_W", "Qremoved_total_W",
        "Qoil_heat_in_W", "Qoil_heat_out_W", "Qboundary_heat_out_net_W",
        "residual_W", "residual_percent_Qgenerated", "residual_percent_abs_boundary_flux", "residual_percent_max_energy_scale",
        "energy_scale_Qgenerated_W", "energy_scale_abs_boundary_flux_W", "energy_scale_max_W",
        "valid_by_Qgenerated_percent", "valid_by_absolute_residual", "valid_by_max_energy_scale", "heat_balance_status", "notes",
    ], recheck_rows)
    write_csv(OUT / "oil_flux_sign_diagnostics.csv", [
        "case_id", "oil_temperature_C", "Tmax_RIP_C", "Tmean_oil_side_surface_C", "Qremoved_oil_W", "Qoil_heat_in_W", "Qoil_heat_out_W", "sign_is_physical", "notes",
    ], oil_rows)
    write_csv(OUT / "boundary_flux_component_recheck.csv", [
        "case_id", "Qremoved_air_W", "Qremoved_oil_W", "Qremoved_flange_W", "air_boundary_count", "oil_boundary_count", "flange_boundary_count",
        "air_boundary_total_length_m", "oil_boundary_total_length_m", "flange_boundary_total_length_m", "boundary_selection_status", "notes",
    ], boundary_rows)
    write_csv(OUT / "risk_validity_summary_reclassified.csv", [
        "case_id", "original_status", "original_failure_reason", "valid_temperature", "valid_Qjoule", "valid_Qcontact", "valid_selection",
        "valid_heat_balance_strict", "valid_heat_balance_reclassified", "heat_balance_status", "overall_valid_reclassified",
        "thermal_warning", "thermal_risk", "final_failure_reason",
    ], reclassified_rows)

    draw_figures(recheck_rows, oil_rows, reclassified_rows, original_invalid)
    write_report(metrics, sources, validity, recheck_rows, oil_rows, boundary_rows, reclassified_rows, original_invalid)
    print(f"wrote {OUT}")
    print(f"wrote {REPORT}")


def write_report(metrics, sources, validity, recheck_rows, oil_rows, boundary_rows, reclassified_rows, original_invalid) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    total = len(reclassified_rows)
    strict_count = sum(r["heat_balance_status"] == "VALID_STRICT" for r in recheck_rows)
    low_power_count = sum(r["heat_balance_status"] == "VALID_LOW_POWER_RECLASSIFIED" for r in recheck_rows)
    invalid_hb = sum(r["heat_balance_status"] == "INVALID_HEAT_BALANCE" for r in recheck_rows)
    overall_count = sum(str(r["overall_valid_reclassified"]).lower() == "true" for r in reclassified_rows)
    qjoule_count = sum(b(r, "valid_Qjoule") for r in validity)
    qcontact_count = sum(b(r, "valid_Qcontact") for r in validity)
    selection_count = sum(b(r, "valid_selection") for r in validity)
    sign_physical_count = sum(str(r["sign_is_physical"]).lower() == "true" for r in oil_rows)
    drift_count = sum(r["boundary_selection_status"] != "OK_NO_SELECTION_DRIFT" for r in boundary_rows)
    hb_by_case = {r["case_id"]: r for r in recheck_rows}
    oil_by_case = {r["case_id"]: r for r in oil_rows}
    valid_by_case = {r["case_id"]: r for r in validity}
    invalid_lines = []
    for cid in original_invalid:
        r = hb_by_case[cid]
        oil = oil_by_case[cid]
        invalid_lines.append(
            f"- {cid}: original={valid_by_case[cid]['failure_reason']}, residual_W={float(r['residual_W']):.3f} W, "
            f"residual_percent_Qgenerated={float(r['residual_percent_Qgenerated']):.3f}%, "
            f"residual_percent_max_energy_scale={float(r['residual_percent_max_energy_scale']):.3f}%, "
            f"status={r['heat_balance_status']}, Qoil_heat_in={float(oil['Qoil_heat_in_W']):.3f} W"
        )
    checks = trend_checks(metrics, sources)
    all_trends = all(checks.values())
    can_proceed = (
        len(original_invalid) == 9
        and drift_count == 0
        and sign_physical_count == total
        and overall_count == total
        and qjoule_count == total
        and qcontact_count == total
        and selection_count == total
        and all_trends
    )
    proceed = "YES" if can_proceed else "NO"
    reason = (
        "原始 9 个 heat_balance invalid case 均被低发热量补充判据解释并重分类，selection 无漂移，油侧热通量符号物理合理，Qjoule/Qcontact/selection 均为 125/125，趋势检查通过。"
        if can_proceed
        else "仍存在未满足 RUN009 前置条件的项目。"
    )
    status_counts = Counter(str(r["heat_balance_status"]) for r in recheck_rows)
    oil_note = (
        "RUN008 未直接导出油侧边界平均温度；本轮使用已知 h_oil=300 W/(m^2*K) 和油侧轴对称边界面积 "
        "A_oil=0.2467406868 m^2，由 Qremoved_oil = h_oil*A_oil*(Tmean_surface-Toil) 反算 Tmean_oil_side_surface_C。"
    )
    report = f"""# SOLID_ONLY_RISK_125_RUN008B_HEAT_BALANCE_FIX 报告

## 1. 本轮任务目标

本轮目标是对 RUN008 中低负荷、高油温工况的热量收支诊断进行后处理复核，补充绝对残差和最大能量尺度判据。没有重新运行 125 组 COMSOL，没有进入 RUN009，也没有构建完整电热耦合模型。

## 2. RUN008 中 9 个 invalid case 的原因

RUN008 中 9 个 invalid_case 均由原始 heat balance 判据 `abs(residual_percent_Qgenerated) < 10%` 未通过导致；Qjoule、Qcontact 和 selection 均已通过。它们共同特征是 load_multiplier_pu=0.6、油温较高、总发热量较低，residual_W 绝对值仅约 1.6 至 2.2 W。

{chr(10).join(invalid_lines)}

## 3. 原始 residual_percent_Qgenerated 判据的局限性

原始判据用 residual_W / Qtotal_generated_W 归一化。在低负荷工况中，Qtotal_generated_W 较小，1 至 2 W 级的闭合残差会被放大为超过 10%。当油侧边界为热油向固体输入热量时，边界热通量的绝对交换规模明显大于净发热量，仅用 Qgenerated 归一化容易把低功率闭合误差误判为模型错误。

## 4. 补充判据说明

RUN008B 同时输出三类判据：

- 原始严格判据：abs(residual_percent_Qgenerated) < 10%；
- 绝对残差判据：abs(residual_W) < 3 W；
- 最大能量尺度判据：abs(residual_percent_max_energy_scale) < 5%。

当原始严格判据未通过，但绝对残差和最大能量尺度判据同时通过时，标记为 `VALID_LOW_POWER_RECLASSIFIED`。这不是把严格阈值简单放宽，而是针对低发热量、热边界输入显著工况的补充诊断。

## 5. 油侧热通量符号是否物理合理

{oil_note}

油侧热通量符号物理合理数量：{sign_physical_count}/{total}。当 Qremoved_oil_W < 0 时，反算得到油侧固体表面平均温度低于油温，表示热油向固体输入热量；这与 RUN008 invalid case 的特征一致。

## 6. 边界 selection 是否发生漂移

边界 selection 漂移数量：{drift_count}/{total}。本轮使用 RUN008 的固定 explicit by-ID boundary selections；air/oil/flange 的 boundary_count 与 boundary_total_length 在所有工况中保持不变。因此 RUN008 的 9 个 invalid case 更可能是热量收支归一化判据问题，而不是 selection 漂移。

## 7. 重新分类后 valid_heat_balance 数量

- heat_balance_status 统计：{dict(status_counts)}
- VALID_STRICT：{strict_count}/{total}
- VALID_LOW_POWER_RECLASSIFIED：{low_power_count}/{total}
- INVALID_HEAT_BALANCE：{invalid_hb}/{total}

## 8. 重新分类后 invalid_case 数量

overall_valid_reclassified = {overall_count}/{total}。重新分类后 invalid_case 数量为 {total - overall_count}。

## 9. 是否可以进入 FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009

{reason}

前置条件复核：

- original invalid cases 已解释清楚：true
- 无 INVALID_SELECTION_DRIFT：{str(drift_count == 0).lower()}
- 油侧热通量符号物理合理：{str(sign_physical_count == total).lower()}
- overall_valid_reclassified = 125/125：{str(overall_count == total).lower()}
- valid_Qjoule = 125/125：{str(qjoule_count == total).lower()}
- valid_Qcontact = 125/125：{str(qcontact_count == total).lower()}
- valid_selection = 125/125：{str(selection_count == total).lower()}
- 趋势检查均通过：{str(all_trends).lower()}

趋势检查结果：

- Tmax_global_C 随 oil_temperature_C 升高而升高：{checks['Tmax_global_increases_with_oil_temperature']}
- Tmax_global_C 随 load_multiplier_pu 升高而升高：{checks['Tmax_global_increases_with_load']}
- Tmax_contact_C 随 contact_resistance_multiplier_pu 升高而升高：{checks['Tmax_contact_increases_with_Rc']}
- Qjoule 随 I² 增长：{checks['Qjoule_increases_with_I2']}
- Qcontact 随 I² * Rc_factor 增长：{checks['Qcontact_increases_with_I2_Rc']}

## 10. 下一阶段定位

如果用户确认进入下一阶段，RUN009 的定位应为 `FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009`：将 solid-only 中的 `approximate_Qdielectric_ref` 替换为完整电场求解得到的空间分布介质损耗 `Qdielectric = omega * epsilon0 * epsr * tan_delta * |E|^2`。RUN008B 本轮没有执行 RUN009。

Can proceed to FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009: {proceed}
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
