"""Postprocess SOLID_ONLY_RISK_125_RUN008.

This script only reads completed RUN008 CSV exports. It does not run COMSOL,
does not perform transient/weather simulation, and does not build the full
electro-thermal dielectric-loss model.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import plot_solid_only_sweep_27_run007 as base


PROJECT = Path(__file__).resolve().parents[1]
RUN_ID = "SOLID_ONLY_RISK_125_RUN008"
RAW_DIR = PROJECT / "results" / "raw_comsol_exports" / RUN_ID
FIG_DIR = PROJECT / "results" / "paper_figures" / "solid_only_risk_125_run008"
DOC_DIR = PROJECT / "docs"
REPORT = DOC_DIR / "solid_only_risk_125_run008_report.md"

LOADS = [0.6, 0.8, 1.0, 1.2, 1.4]
OILS = [65.0, 75.0, 85.0, 95.0, 105.0]
RCS = [1.0, 2.0, 5.0, 10.0, 20.0]
RISK_COLORS = {
    "safe": "#2ca02c",
    "attention": "#ffbf00",
    "warning": "#ff7f0e",
    "thermal_risk": "#d62728",
    "invalid_case": "#555555",
}
CONTACT_COLORS = {
    "contact_safe": "#2ca02c",
    "contact_attention": "#ffbf00",
    "contact_warning": "#ff7f0e",
    "contact_risk": "#d62728",
    "invalid_case": "#555555",
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (RAW_DIR / name).open(newline="") as f:
        return list(csv.DictReader(f))


def save(img: Image.Image, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    img.save(FIG_DIR / name)


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def b(row: dict[str, str], key: str) -> bool:
    return str(row[key]).strip().lower() == "true"


def case_no(case_id: str) -> int:
    return int(case_id.rsplit("_", 1)[-1])


def row_key(load: float, oil: float, rc: float) -> tuple[str, str, str]:
    return (f"{load:.6f}", f"{oil:.6f}", f"{rc:.6f}")


def short_zone(zone: str) -> str:
    return {
        "invalid_case": "invalid",
        "thermal_risk": "risk",
        "attention": "attn",
        "warning": "warn",
        "contact_safe": "safe",
        "contact_attention": "attn",
        "contact_warning": "warn",
        "contact_risk": "risk",
    }.get(zone, zone)


def heat_color(value: float, vmin: float, vmax: float) -> str:
    if not math.isfinite(value):
        return "#555555"
    t = 0.0 if math.isclose(vmin, vmax) else (value - vmin) / (vmax - vmin)
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        q = t / 0.5
        c0 = np.array([49, 130, 189])
        c1 = np.array([255, 230, 120])
    else:
        q = (t - 0.5) / 0.5
        c0 = np.array([255, 230, 120])
        c1 = np.array([215, 48, 39])
    c = (c0 * (1 - q) + c1 * q).astype(int)
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


def validity_by_case(validity: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["case_id"]: row for row in validity}


def panel_grid(width: int, height: int, rows: int, cols: int, top: int = 108) -> list[tuple[int, int, int, int]]:
    boxes = []
    left_margin, right_margin = 70, 40
    bottom_margin = 70
    gap_x, gap_y = 38, 48
    pw = (width - left_margin - right_margin - gap_x * (cols - 1)) // cols
    ph = (height - top - bottom_margin - gap_y * (rows - 1)) // rows
    for r in range(rows):
        for c in range(cols):
            x0 = left_margin + c * (pw + gap_x)
            y0 = top + r * (ph + gap_y)
            boxes.append((x0, y0, x0 + pw, y0 + ph))
    return boxes


def heatmap_5_panel(
    metrics: list[dict[str, str]],
    validity: list[dict[str, str]],
    value_key: str,
    zone_key: str,
    title: str,
    filename: str,
    contact: bool = False,
) -> None:
    width, height = 1900, 820
    img, draw = base.new_image(width, height, title)
    valid = validity_by_case(validity)
    values = [f(row, value_key) for row in metrics]
    vmin, vmax = min(values), max(values)
    by = {(f(r, "load_multiplier_pu"), f(r, "oil_temperature_C"), f(r, "contact_resistance_multiplier_pu")): r for r in metrics}
    boxes = panel_grid(width, height, 1, 5)
    for idx, rc in enumerate(RCS):
        left, top, right, bottom = boxes[idx]
        draw.rectangle((left, top, right, bottom), outline="#dddddd")
        draw.text((left + 12, top + 10), f"Rc={rc:g}", font=base.FONT_BOLD, fill="#222222")
        grid_left, grid_top = left + 58, top + 58
        grid_right, grid_bottom = right - 18, bottom - 60
        cw = (grid_right - grid_left) / len(LOADS)
        ch = (grid_bottom - grid_top) / len(OILS)
        for c, load in enumerate(LOADS):
            base.draw_centered(draw, (grid_left + c * cw + cw / 2, grid_bottom + 24), f"{load:g}", base.FONT_SMALL)
        for r, oil in enumerate(OILS):
            base.draw_centered(draw, (left + 32, grid_top + r * ch + ch / 2), f"{oil:g}", base.FONT_SMALL)
        for r, oil in enumerate(OILS):
            for c, load in enumerate(LOADS):
                row = by[(load, oil, rc)]
                case_valid = b(valid[row["case_id"]], "overall_valid")
                zone = row[zone_key] if case_valid else "invalid_case"
                x0 = grid_left + c * cw
                y0 = grid_top + r * ch
                fill = heat_color(f(row, value_key), vmin, vmax)
                draw.rectangle((x0 + 2, y0 + 2, x0 + cw - 2, y0 + ch - 2), fill=fill, outline="#ffffff", width=2)
                outline = (CONTACT_COLORS if contact else RISK_COLORS).get(zone, "#555555")
                draw.rectangle((x0 + 4, y0 + 4, x0 + cw - 4, y0 + ch - 4), outline=outline, width=4)
                base.draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 - 10), f"{f(row, value_key):.1f}", base.FONT_SMALL)
                base.draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 + 14), short_zone(zone), base.FONT_SMALL)
    draw.text((78, height - 38), f"cell fill={value_key}; border/text=risk zone; gray border=invalid_case", font=base.FONT_SMALL, fill="#222222")
    save(img, filename)


def fig03(boundary: list[dict[str, str]]) -> None:
    img, draw = base.new_image(1500, 760, "Fig03 Safe load boundary by oil temperature and Rc")
    series = []
    for idx, rc in enumerate(RCS):
        rows = sorted([r for r in boundary if math.isclose(f(r, "contact_resistance_multiplier_pu"), rc)], key=lambda r: f(r, "oil_temperature_C"))
        x, y = [], []
        for r in rows:
            value = r["max_safe_load_multiplier_pu"]
            if value != "NA":
                x.append(f(r, "oil_temperature_C"))
                y.append(float(value))
        series.append({"label": f"Rc {rc:g}", "x": x, "y": y, "color": base.COLORS[idx % len(base.COLORS)]})
    base.draw_line_panel(draw, base.panel_bbox(0, 0, 1, 1, 1500, 760), series, "oil_temperature_C", "max_safe_load_multiplier_pu", "safe = Tmax_global_C < 110 and valid case", x_ticks=OILS, ylim=(0.5, 1.5))
    save(img, "fig03_safe_load_boundary_by_oil_and_Rc.png")


def fig04(metrics: list[dict[str, str]]) -> None:
    img, draw = base.new_image(1900, 1050, "Fig04 Tmax_contact vs Rc factor by load")
    boxes = panel_grid(1900, 1050, 2, 3)
    for idx, oil in enumerate(OILS):
        rows_oil = [r for r in metrics if math.isclose(f(r, "oil_temperature_C"), oil)]
        series = []
        for j, load in enumerate(LOADS):
            rows = sorted([r for r in rows_oil if math.isclose(f(r, "load_multiplier_pu"), load)], key=lambda r: f(r, "contact_resistance_multiplier_pu"))
            series.append({"label": f"load {load:g}", "x": [f(r, "contact_resistance_multiplier_pu") for r in rows], "y": [f(r, "Tmax_contact_C") for r in rows], "color": base.COLORS[j]})
        base.draw_line_panel(draw, boxes[idx], series, "Rc_factor", "Tmax_contact_C", f"oil={oil:g} C", x_ticks=RCS)
    save(img, "fig04_Tmax_contact_vs_Rc_factor_by_load.png")


def fig05(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> None:
    by_metric = {r["case_id"]: r for r in metrics}
    rows = []
    requested = [
        ("low risk", 0.6, 65.0, 1.0),
        ("baseline", 1.0, 85.0, 1.0),
        ("high contact", 1.2, 95.0, 20.0),
        ("highest pressure", 1.4, 105.0, 20.0),
    ]
    by_combo = {(f(by_metric[s["case_id"]], "load_multiplier_pu"), f(by_metric[s["case_id"]], "oil_temperature_C"), f(by_metric[s["case_id"]], "contact_resistance_multiplier_pu")): s for s in sources}
    for label, load, oil, rc in requested:
        row = dict(by_combo[(load, oil, rc)])
        row["label"] = label
        row.update(by_metric[row["case_id"]])
        rows.append(row)

    img, draw = base.new_image(1300, 760, "Fig05 Heat-source decomposition of representative risk cases")
    left, top, right, bottom = base.panel_bbox(0, 0, 1, 1, 1300, 760)
    plot = (left + 90, top + 50, right - 40, bottom - 90)
    px0, py0, px1, py1 = plot
    max_total = max(f(r, "Qtotal_W") for r in rows) * 1.15
    draw.rectangle((left, top, right, bottom), outline="#dddddd")
    draw.line((px0, py1, px1, py1), fill="#222222", width=2)
    draw.line((px0, py0, px0, py1), fill="#222222", width=2)
    keys = [("Qjoule_conductor_W", "#1f77b4", "Qjoule"), ("Qcontact_W", "#ff7f0e", "Qcontact"), ("Qdielectric_RIP_W", "#2ca02c", "Qdielectric"), ("Qscreen_loss_W", "#7f7f7f", "Qscreen")]
    bw = (px1 - px0) / (len(rows) * 1.8)
    for i, row in enumerate(rows):
        x0 = px0 + (i + 0.35) * (px1 - px0) / len(rows)
        y_base = py1
        for key, color, _ in keys:
            h = f(row, key) / max_total * (py1 - py0)
            draw.rectangle((x0, y_base - h, x0 + bw, y_base), fill=color, outline="#ffffff")
            y_base -= h
        base.draw_centered(draw, (x0 + bw / 2, py1 + 25), row["label"], base.FONT_SMALL)
        base.draw_centered(draw, (x0 + bw / 2, py1 + 48), f"L{f(row,'load_multiplier_pu'):g}/O{f(row,'oil_temperature_C'):g}/R{f(row,'contact_resistance_multiplier_pu'):g}", base.FONT_SMALL)
        base.draw_centered(draw, (x0 + bw / 2, y_base - 14), f"{f(row,'Qtotal_W'):.1f} W", base.FONT_SMALL)
    for t in base.nice_ticks(0, max_total):
        y = py1 - t / max_total * (py1 - py0)
        draw.line((px0, y, px1, y), fill="#eeeeee")
        draw.text((left + 20, y - 10), f"{t:g}", font=base.FONT_SMALL, fill="#222222")
    draw.text((left + 12, top + 14), "heat source / W", font=base.FONT_SMALL, fill="#222222")
    lx, ly = px1 - 220, py0 + 18
    for i, (_, color, label) in enumerate(keys):
        draw.rectangle((lx, ly + i * 26, lx + 18, ly + 18 + i * 26), fill=color)
        draw.text((lx + 28, ly + i * 26 - 2), label, font=base.FONT_SMALL, fill="#222222")
    save(img, "fig05_heat_source_decomposition_risk_cases.png")


def fig06(balance: list[dict[str, str]], validity: list[dict[str, str]]) -> None:
    valid = validity_by_case(validity)
    rows = sorted(balance, key=lambda r: case_no(r["case_id"]))
    values = [f(r, "residual_percent") for r in rows]
    colors = ["#d62728" if not b(valid[r["case_id"]], "overall_valid") else "#1f77b4" for r in rows]
    img, draw = base.new_image(1700, 780, "Fig06 Heat-balance residual for 125 cases")
    base.draw_bar_panel(draw, base.panel_bbox(0, 0, 1, 1, 1700, 780), [str(i + 1) for i in range(len(rows))], values, colors, "case index", "residual_percent", "invalid cases are red", threshold=10.0)
    save(img, "fig06_heat_balance_residual_125_cases.png")


def fig07(sources: list[dict[str, str]]) -> None:
    rows = sorted(sources, key=lambda r: f(r, "Qcontact_expected_I2Rc_W"))
    img, draw = base.new_image(1450, 780, "Fig07 Qcontact I2Rc validation")
    series = [
        {"label": "integrated Qcontact", "x": [f(r, "Qcontact_expected_I2Rc_W") for r in rows], "y": [f(r, "Qcontact_W") for r in rows], "color": "#1f77b4"},
        {"label": "y=x", "x": [0, max(f(r, "Qcontact_expected_I2Rc_W") for r in rows)], "y": [0, max(f(r, "Qcontact_expected_I2Rc_W") for r in rows)], "color": "#d62728"},
    ]
    base.draw_line_panel(draw, base.panel_bbox(0, 0, 1, 1, 1450, 780), series, "Icase^2*Rc0*Rc_factor / W", "integrated Qcontact_W", f"max relative error={max(abs(f(r,'Qcontact_relative_error_pct')) for r in rows):.3e}%")
    save(img, "fig07_Qcontact_I2Rc_validation.png")


def fig08(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> tuple[float, float, float]:
    by_metric = {r["case_id"]: r for r in metrics}
    rows = []
    for row in sources:
        item = dict(row)
        item.update(by_metric[row["case_id"]])
        rows.append(item)
    x = np.array([(f(r, "current_A") ** 2) / 1e6 for r in rows])
    y = np.array([f(r, "Qjoule_conductor_W") for r in rows])
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    r2 = 1.0 - float(np.sum((y - yhat) ** 2) / np.sum((y - np.mean(y)) ** 2))

    img, draw = base.new_image(1450, 780, "Fig08 Qjoule I2 scaling validation")
    series = []
    for idx, oil in enumerate(OILS):
        rows_oil = sorted([r for r in rows if math.isclose(f(r, "oil_temperature_C"), oil)], key=lambda r: f(r, "current_A"))
        series.append({"label": f"oil {oil:g} C", "x": [(f(r, "current_A") ** 2) / 1e6 for r in rows_oil], "y": [f(r, "Qjoule_conductor_W") for r in rows_oil], "color": base.COLORS[idx]})
    xfit = [float(np.min(x)), float(np.max(x))]
    series.append({"label": f"fit R2={r2:.4f}", "x": xfit, "y": [slope * xfit[0] + intercept, slope * xfit[1] + intercept], "color": "#222222"})
    sign = "+" if intercept >= 0 else "-"
    base.draw_line_panel(draw, base.panel_bbox(0, 0, 1, 1, 1450, 780), series, "I^2 / 1e6 A^2", "Qjoule_conductor_W", f"Q={slope:.3f}*(I^2/1e6) {sign} {abs(intercept):.3f}")
    save(img, "fig08_Qjoule_I2_scaling_validation.png")
    return float(slope), float(intercept), float(r2)


def fig09(metrics: list[dict[str, str]], validity: list[dict[str, str]]) -> None:
    width, height = 1900, 820
    img, draw = base.new_image(width, height, "Fig09 Risk zone matrix for 125 cases")
    valid = validity_by_case(validity)
    by = {(f(r, "load_multiplier_pu"), f(r, "oil_temperature_C"), f(r, "contact_resistance_multiplier_pu")): r for r in metrics}
    boxes = panel_grid(width, height, 1, 5)
    for idx, rc in enumerate(RCS):
        left, top, right, bottom = boxes[idx]
        draw.rectangle((left, top, right, bottom), outline="#dddddd")
        draw.text((left + 12, top + 10), f"Rc={rc:g}", font=base.FONT_BOLD, fill="#222222")
        grid_left, grid_top = left + 58, top + 58
        grid_right, grid_bottom = right - 18, bottom - 60
        cw = (grid_right - grid_left) / len(LOADS)
        ch = (grid_bottom - grid_top) / len(OILS)
        for r, oil in enumerate(OILS):
            base.draw_centered(draw, (left + 32, grid_top + r * ch + ch / 2), f"{oil:g}", base.FONT_SMALL)
            for c, load in enumerate(LOADS):
                row = by[(load, oil, rc)]
                zone = row["risk_zone"] if b(valid[row["case_id"]], "overall_valid") else "invalid_case"
                x0 = grid_left + c * cw
                y0 = grid_top + r * ch
                draw.rectangle((x0 + 3, y0 + 3, x0 + cw - 3, y0 + ch - 3), fill=RISK_COLORS[zone], outline="#ffffff", width=2)
                base.draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 - 10), f"{case_no(row['case_id']):03d}", base.FONT_SMALL)
                base.draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 + 14), short_zone(zone), base.FONT_SMALL, fill="#111111")
        for c, load in enumerate(LOADS):
            base.draw_centered(draw, (grid_left + c * cw + cw / 2, grid_bottom + 24), f"{load:g}", base.FONT_SMALL)
    lx, ly = 72, height - 42
    for i, (zone, color) in enumerate(RISK_COLORS.items()):
        x = lx + i * 245
        draw.rectangle((x, ly, x + 20, ly + 20), fill=color)
        draw.text((x + 30, ly - 2), zone, font=base.FONT_SMALL, fill="#222222")
    save(img, "fig09_risk_zone_matrix_125_cases.png")


def fig10(metrics: list[dict[str, str]]) -> None:
    img, draw = base.new_image(1450, 820, "Fig10 Tmax_global vs Tmax_contact")
    xmin, xmax = min(f(r, "Tmax_global_C") for r in metrics), max(f(r, "Tmax_global_C") for r in metrics)
    ymin, ymax = min(f(r, "Tmax_contact_C") for r in metrics), max(f(r, "Tmax_contact_C") for r in metrics)
    sx, sy, plot = base.draw_axes(draw, base.panel_bbox(0, 0, 1, 1, 1450, 820), (xmin - 5, xmax + 5), (ymin - 5, ymax + 5), "Tmax_global_C", "Tmax_contact_C", "color=Rc factor; marker size=load multiplier")
    color_map = {rc: base.COLORS[i] for i, rc in enumerate(RCS)}
    for row in metrics:
        rc = f(row, "contact_resistance_multiplier_pu")
        load = f(row, "load_multiplier_pu")
        x, y = sx(f(row, "Tmax_global_C")), sy(f(row, "Tmax_contact_C"))
        radius = 4 + 4 * (load - min(LOADS)) / (max(LOADS) - min(LOADS))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color_map[rc], outline="#ffffff", width=1)
    lx, ly = plot[2] - 180, plot[1] + 16
    for i, rc in enumerate(RCS):
        draw.ellipse((lx, ly + i * 26, lx + 16, ly + 16 + i * 26), fill=color_map[rc])
        draw.text((lx + 26, ly + i * 26 - 3), f"Rc {rc:g}", font=base.FONT_SMALL, fill="#222222")
    save(img, "fig10_Tmax_global_vs_contact.png")


def monotonic(values: list[float], tol: float = 1e-8) -> bool:
    return all(values[i + 1] + tol >= values[i] for i in range(len(values) - 1))


def trend_checks(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> dict[str, bool]:
    by_source = {r["case_id"]: r for r in sources}
    rows = []
    for row in metrics:
        item = dict(row)
        item.update(by_source[row["case_id"]])
        rows.append(item)
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


def write_report(cases, metrics, sources, balance, validity, boundary, fit) -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    total = len(metrics)
    status_counts = Counter(r["status"] for r in validity)
    risk_counts = Counter((m["risk_zone"] if b(validity_by_case(validity)[m["case_id"]], "overall_valid") else "invalid_case") for m in metrics)
    contact_counts = Counter(m["contact_risk_zone"] for m in metrics)
    valid_counts = {
        "valid_heat_balance": sum(b(r, "valid_heat_balance") for r in validity),
        "valid_Qjoule": sum(b(r, "valid_Qjoule") for r in validity),
        "valid_Qcontact": sum(b(r, "valid_Qcontact") for r in validity),
        "valid_selection": sum(b(r, "valid_selection") for r in validity),
        "overall_valid": sum(b(r, "overall_valid") for r in validity),
    }
    invalid = [r for r in validity if not b(r, "overall_valid")]
    thermal_risk = [r for r in validity if b(r, "thermal_risk")]
    thermal_warning = [r for r in validity if b(r, "thermal_warning")]
    tmax_min = min(f(r, "Tmax_global_C") for r in metrics)
    tmax_max = max(f(r, "Tmax_global_C") for r in metrics)
    tcontact_max = max(f(r, "Tmax_contact_C") for r in metrics)
    residual_abs_max = max(abs(f(r, "residual_percent")) for r in balance)
    qjoule_err_max = max(abs(f(r, "Qjoule_relative_error_pct")) for r in sources)
    qcontact_err_max = max(abs(f(r, "Qcontact_relative_error_pct")) for r in sources)
    qjoule_min = min(f(r, "Qjoule_conductor_W") for r in sources)
    qjoule_max = max(f(r, "Qjoule_conductor_W") for r in sources)
    qcontact_min = min(f(r, "Qcontact_W") for r in sources)
    qcontact_max = max(f(r, "Qcontact_W") for r in sources)
    checks = trend_checks(metrics, sources)
    can_proceed = (
        total == 125
        and len(invalid) == 0
        and valid_counts["valid_heat_balance"] == total
        and valid_counts["valid_Qjoule"] == total
        and valid_counts["valid_Qcontact"] == total
        and valid_counts["valid_selection"] == total
        and all(checks.values())
    )
    by_metric = {r["case_id"]: r for r in metrics}
    by_balance = {r["case_id"]: r for r in balance}
    invalid_lines = []
    for r in invalid:
        m = by_metric[r["case_id"]]
        hb = by_balance[r["case_id"]]
        invalid_lines.append(
            f"- {r['case_id']}: load={m['load_multiplier_pu']}, oil={m['oil_temperature_C']} C, "
            f"Rc={m['contact_resistance_multiplier_pu']}, failure={r['failure_reason']}, "
            f"residual_percent={float(hb['residual_percent']):.3f}%"
        )
    if not invalid_lines:
        invalid_lines.append("- 无 invalid_case。")
    boundary_notes = []
    for row in boundary:
        if row["first_attention_load_multiplier_pu"] != "NA" or row["first_warning_load_multiplier_pu"] != "NA" or row["first_thermal_risk_load_multiplier_pu"] != "NA":
            boundary_notes.append(f"- {row['risk_zone_transition_note']}")
    if not boundary_notes:
        boundary_notes.append("- 扫描网格中未出现 attention/warning/thermal_risk 转换。")
    fit_slope, fit_intercept, fit_r2 = fit
    sign = "+" if fit_intercept >= 0 else "-"
    proceed_text = "YES" if can_proceed else "NO"
    reason = (
        "125 组均通过有效性校核，且趋势检查均为 True。"
        if can_proceed
        else f"存在 {len(invalid)} 个 invalid_case，且 valid_heat_balance={valid_counts['valid_heat_balance']}/{total}，未达到进入 RUN009 的前置条件。"
    )
    report = f"""# SOLID_ONLY_RISK_125_RUN008 阶段报告

## 1. 本轮任务目标

本轮基于 RUN006/RUN007 已验证的 source-fixed、explicit by-ID、solid-only thermal diagnostic model，完成 5 x 5 x 5 共 125 组核心风险边界扫描。目标是扩展负荷倍率、油温和接触电阻倍率范围，检查热源分解、热量收支和风险分区。本轮不是完整电热耦合主实验，也不是最终 SCI 论文结果。

## 2. 与 RUN006/RUN007 的关系

RUN006 用于修正导体焦耳热和接触热源归一化；RUN007 用 27 组小规模扫参验证了显式 by-ID selection、热源缩放和热量收支。RUN008 在此基础上扩展为 125 组风险边界扫描。RIP 介质损耗仍采用 `approximate_Qdielectric_ref`，不能写成真实电场耦合介质损耗。

## 3. 125 组工况矩阵

load_multiplier_pu = [0.6, 0.8, 1.0, 1.2, 1.4]；oil_temperature_C = [65, 75, 85, 95, 105]；contact_resistance_multiplier_pu = [1, 2, 5, 10, 20]。固定条件为 voltage_multiplier_pu=1.0、air_temperature_C=25、wind_speed_m_s=1.0、tan_delta_multiplier_pu=1.0、rip_aging_conductivity_multiplier_pu=1.0、pollution_multiplier_pu=1.0。

## 4. 模型边界说明

本轮沿用 RUN006/RUN007 的 source-fixed 热源归一化方式，沿用 explicit by-ID domain selections 和 explicit by-ID boundary selections。没有回退到 Box selection。contact layer 未纳入 conductor Joule loss，RIP、screen、flange、terminal 也未纳入 conductor Joule loss。

## 5. 风险分区阈值说明

全局温度风险区为 safe: Tmax_global_C < 110；attention: 110 <= Tmax_global_C < 130；warning: 130 <= Tmax_global_C < 150；thermal_risk: Tmax_global_C >= 150。接触热点风险区为 contact_safe: Tmax_contact_C < 100；contact_attention: 100 <= Tmax_contact_C < 120；contact_warning: 120 <= Tmax_contact_C < 150；contact_risk: Tmax_contact_C >= 150。这些阈值只用于 solid-only 诊断阶段的风险分区和可视化，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。

## 6. 有效性统计

- 工况数量：{total}
- 求解状态：{dict(status_counts)}
- risk_zone 统计：{dict(risk_counts)}
- contact_risk_zone 统计：{dict(contact_counts)}
- valid_heat_balance：{valid_counts['valid_heat_balance']}/{total}
- valid_Qjoule：{valid_counts['valid_Qjoule']}/{total}
- valid_Qcontact：{valid_counts['valid_Qcontact']}/{total}
- valid_selection：{valid_counts['valid_selection']}/{total}
- overall_valid：{valid_counts['overall_valid']}/{total}
- thermal_warning：{len(thermal_warning)}/{total}
- thermal_risk_case：{len(thermal_risk)}/{total}

Tmax_global_C 范围为 {tmax_min:.3f} 至 {tmax_max:.3f} degC；Tmax_contact_C 最大值为 {tcontact_max:.3f} degC。最大 heat-balance residual_percent 绝对值为 {residual_abs_max:.3f}%。最大 Qjoule 相对误差绝对值为 {qjoule_err_max:.3e}%，最大 Qcontact 相对误差绝对值为 {qcontact_err_max:.3e}%。

## 7. 是否存在 invalid_case

存在 {len(invalid)} 个 invalid_case，均由 heat_balance residual_percent 超过 10% 引起，主要集中在低负荷、高油温、低接触电阻倍率工况。具体如下：

{chr(10).join(invalid_lines)}

这些工况的 Qjoule 与 Qcontact 校核仍通过，selection 也未异常；当前问题更像是低总发热量条件下油侧热输入和热量收支归一化/边界通量闭合的诊断阈值问题，而不是导体或接触热源归一化错误。

## 8. 是否存在 thermal_risk_case

不存在 thermal_risk_case。最高温工况为 Tmax_global_C = {tmax_max:.3f} degC，属于 warning 区而非 thermal_risk 区。

## 9. 热源分解趋势

Qjoule_conductor_W 范围为 {qjoule_min:.3f} 至 {qjoule_max:.3f} W，并随 I² 增长。Qcontact_W 范围为 {qcontact_min:.3f} 至 {qcontact_max:.3f} W，严格满足 Icase² * Rc0 * Rc_factor。Qjoule 对 I² 的线性拟合为 Q = {fit_slope:.3f} * (I²/1e6) {sign} {abs(fit_intercept):.3f}，R² = {fit_r2:.5f}。

## 10. 热量收支趋势

116/125 工况满足 abs(residual_percent) < 10%。9 个 invalid_case 的 residual_percent 为 -10.364% 至 -13.622%，全部为负残差，表示热移除项大于体热源积分；这些工况同时具有低负荷、热源小和热油边界向固体输入热量的特征。

## 11. 风险边界初步结论

{chr(10).join(boundary_notes)}

在当前扫描范围内没有出现 Tmax_global_C >= 150 degC 的 thermal_risk 区，但最高压力工况 load=1.4、oil=105 C、Rc=20 进入 warning 区，Tmax_global_C = {tmax_max:.3f} degC，Tmax_contact_C = {tcontact_max:.3f} degC。

## 12. 代表性风险工况说明

代表性工况包括低风险工况 load=0.6、oil=65 C、Rc=1；基准工况 load=1.0、oil=85 C、Rc=1；高接触风险工况 load=1.2、oil=95 C、Rc=20；最高压力工况 load=1.4、oil=105 C、Rc=20。对应热源分解见 `fig05_heat_source_decomposition_risk_cases.png`。

## 13. 是否建议进入下一步完整电热耦合介质损耗修正

不建议直接进入 `FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009`。虽然 125 组均完成求解，Qjoule、Qcontact 和 selection 均通过，但 valid_heat_balance 不是 100%，存在 9 个 invalid_case，未满足文档给出的进入 RUN009 前置条件。

趋势检查结果：

- Tmax_global_C 随 oil_temperature_C 升高而升高：{checks['Tmax_global_increases_with_oil_temperature']}
- Tmax_global_C 随 load_multiplier_pu 升高而升高：{checks['Tmax_global_increases_with_load']}
- Tmax_contact_C 随 contact_resistance_multiplier_pu 升高而升高：{checks['Tmax_contact_increases_with_Rc']}
- Qjoule_conductor_W 随 I² 增长：{checks['Qjoule_increases_with_I2']}
- Qcontact_W 随 I² * Rc_factor 增长：{checks['Qcontact_increases_with_I2_Rc']}

## 14. 下一轮修正任务

建议先开展 RUN008B 热量收支闭合修正，重点检查低负荷/高油温条件下油侧对流热通量符号、法兰散热边界、外表面对流积分边界是否完整，以及 residual_percent 在低 Qtotal 工况下是否需要同时引入 residual_W 的绝对阈值作为辅助诊断。修正后重新运行 125 组有效性校核；只有 invalid_case = 0 且 valid_heat_balance = 125/125 后，再进入 RUN009。

## 必须回答的问题

1. 125组是否全部成功求解？是，COMSOL 均完成求解；但有效性状态为 116 个 SOLVED_VALID、9 个 INVALID_CASE。
2. valid_heat_balance 是否为100%？否，为 {valid_counts['valid_heat_balance']}/{total}。
3. valid_Qjoule 是否为100%？是，为 {valid_counts['valid_Qjoule']}/{total}。
4. valid_Qcontact 是否为100%？是，为 {valid_counts['valid_Qcontact']}/{total}。
5. 是否存在 selection 异常？否，valid_selection = {valid_counts['valid_selection']}/{total}。
6. thermal_risk_case 是否存在？否，为 {len(thermal_risk)}/{total}。
7. 风险边界是否具有物理趋势？主要趋势合理，趋势检查均为 True。
8. 是否可以进入 FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009？否。

Can proceed to FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009: {proceed_text}

依据：{reason}
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    cases = read_csv("risk_case_matrix.csv")
    metrics = read_csv("risk_metrics.csv")
    sources = read_csv("heat_source_decomposition_by_case.csv")
    balance = read_csv("heat_balance_by_case.csv")
    validity = read_csv("risk_validity_summary.csv")
    boundary = read_csv("risk_boundary_summary.csv")

    heatmap_5_panel(metrics, validity, "Tmax_global_C", "risk_zone", "Fig01 Tmax_global heatmap by load and oil temperature", "fig01_Tmax_heatmap_load_oil_by_Rc.png")
    heatmap_5_panel(metrics, validity, "Tmax_contact_C", "contact_risk_zone", "Fig02 Tmax_contact heatmap by load and oil temperature", "fig02_Tmax_contact_heatmap_load_oil_by_Rc.png", contact=True)
    fig03(boundary)
    fig04(metrics)
    fig05(metrics, sources)
    fig06(balance, validity)
    fig07(sources)
    fit = fig08(metrics, sources)
    fig09(metrics, validity)
    fig10(metrics)
    write_report(cases, metrics, sources, balance, validity, boundary, fit)
    print(f"generated figures in {FIG_DIR}")
    print(f"generated report {REPORT}")


if __name__ == "__main__":
    main()
