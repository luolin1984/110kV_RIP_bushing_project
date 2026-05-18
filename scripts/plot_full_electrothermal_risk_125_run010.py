"""Postprocess FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010.

This script reads completed RUN010 CSV exports, compares them with RUN008
solid-only approximate dielectric-loss exports, and creates diagnostic figures
and a stage report. It does not run COMSOL and does not alter RUN008/RUN009 CSVs.
"""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
RUN010 = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010"
RUN008 = PROJECT / "results" / "raw_comsol_exports" / "SOLID_ONLY_RISK_125_RUN008"
FIG_DIR = PROJECT / "results" / "paper_figures" / "full_electrothermal_risk_125_run010"
REPORT = PROJECT / "docs" / "full_electrothermal_dielectric_loss_risk_125_run010_report.md"
COMPARISON = RUN010 / "run008_vs_run010_comparison.csv"

LOADS = [0.6, 0.8, 1.0, 1.2, 1.4]
OILS = [65.0, 75.0, 85.0, 95.0, 105.0]
RCS = [1.0, 2.0, 5.0, 10.0, 20.0]
RISK_ORDER = ["safe", "attention", "warning", "thermal_risk", "invalid_case"]
RISK_COLORS = {
    "safe": "#2f855a",
    "attention": "#d69e2e",
    "warning": "#dd6b20",
    "thermal_risk": "#c53030",
    "invalid_case": "#4a5568",
}
CONTACT_COLORS = {
    "contact_safe": "#2f855a",
    "contact_attention": "#d69e2e",
    "contact_warning": "#dd6b20",
    "contact_risk": "#c53030",
    "invalid_case": "#4a5568",
}


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


FONT_TITLE = font(36, True)
FONT_BOLD = font(26, True)
FONT = font(21)
FONT_SMALL = font(17)
FONT_TINY = font(13)


def canvas(title: str, w: int = 1900, h: int = 980):
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 78), fill="#111827")
    draw.text((34, 22), title, fill="white", font=FONT_TITLE)
    return img, draw


def save(img: Image.Image, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    img.save(FIG_DIR / name)


def centered(draw, box, s: str, fill="#111827", fnt=FONT_SMALL) -> None:
    bbox = draw.textbbox((0, 0), s, font=fnt)
    x = (box[0] + box[2] - bbox[2] + bbox[0]) / 2
    y = (box[1] + box[3] - bbox[3] + bbox[1]) / 2
    draw.text((x, y), s, fill=fill, font=fnt)


def text(draw, xy, s: str, fill="#111827", fnt=FONT) -> None:
    draw.text(xy, s, fill=fill, font=fnt)


def heat_color(value: float, vmin: float, vmax: float) -> str:
    if not math.isfinite(value):
        return "#4a5568"
    if math.isclose(vmin, vmax):
        t = 0.55
    else:
        t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    if t < 0.5:
        q = t / 0.5
        c0 = (49, 130, 189)
        c1 = (255, 230, 120)
    else:
        q = (t - 0.5) / 0.5
        c0 = (255, 230, 120)
        c1 = (215, 48, 39)
    c = tuple(round(c0[i] * (1 - q) + c1[i] * q) for i in range(3))
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


def short_zone(zone: str) -> str:
    return {
        "invalid_case": "invalid",
        "thermal_risk": "risk",
        "attention": "attn",
        "warning": "warn",
        "safe": "safe",
        "contact_safe": "safe",
        "contact_attention": "attn",
        "contact_warning": "warn",
        "contact_risk": "risk",
    }.get(str(zone), str(zone))


def read_run010():
    metrics = pd.read_csv(RUN010 / "run010_risk_metrics.csv")
    fields = pd.read_csv(RUN010 / "electric_field_diagnostics_by_case.csv")
    dielectric = pd.read_csv(RUN010 / "dielectric_loss_by_case.csv")
    sources = pd.read_csv(RUN010 / "heat_source_decomposition_by_case.csv")
    balance = pd.read_csv(RUN010 / "heat_balance_by_case.csv")
    validity = pd.read_csv(RUN010 / "run010_validity_summary.csv")
    boundary = pd.read_csv(RUN010 / "run010_risk_boundary_summary.csv")
    return metrics, fields, dielectric, sources, balance, validity, boundary


def make_comparison(metrics: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    run008_metrics = pd.read_csv(RUN008 / "risk_metrics.csv")
    run008_sources = pd.read_csv(RUN008 / "heat_source_decomposition_by_case.csv")
    old = run008_metrics.merge(run008_sources[["case_id", "Qdielectric_RIP_W"]], on="case_id", how="left")
    old = old.rename(columns={
        "case_id": "case_id_run008",
        "Tmax_global_C": "Tmax_global_RUN008_C",
        "Tmax_RIP_C": "Tmax_RIP_RUN008_C",
        "risk_zone": "risk_zone_RUN008",
        "Qdielectric_RIP_W": "Qdielectric_RUN008_ref_W",
    })
    new = metrics.copy()
    if "Qdielectric_RIP_field_W" not in new.columns:
        new = new.merge(sources[["case_id", "Qdielectric_RIP_field_W"]], on="case_id", how="left")
    merged = new.merge(
        old[[
            "load_multiplier_pu",
            "oil_temperature_C",
            "contact_resistance_multiplier_pu",
            "Tmax_global_RUN008_C",
            "Tmax_RIP_RUN008_C",
            "Qdielectric_RUN008_ref_W",
            "risk_zone_RUN008",
        ]],
        on=["load_multiplier_pu", "oil_temperature_C", "contact_resistance_multiplier_pu"],
        how="left",
    )
    out = pd.DataFrame({
        "case_id": merged["case_id"],
        "load_multiplier_pu": merged["load_multiplier_pu"],
        "oil_temperature_C": merged["oil_temperature_C"],
        "contact_resistance_multiplier_pu": merged["contact_resistance_multiplier_pu"],
        "Tmax_global_RUN008_C": merged["Tmax_global_RUN008_C"],
        "Tmax_global_RUN010_C": merged["Tmax_global_C"],
        "delta_Tmax_global_C": merged["Tmax_global_C"] - merged["Tmax_global_RUN008_C"],
        "Tmax_RIP_RUN008_C": merged["Tmax_RIP_RUN008_C"],
        "Tmax_RIP_RUN010_C": merged["Tmax_RIP_C"],
        "delta_Tmax_RIP_C": merged["Tmax_RIP_C"] - merged["Tmax_RIP_RUN008_C"],
        "Qdielectric_RUN008_ref_W": merged["Qdielectric_RUN008_ref_W"],
        "Qdielectric_RUN010_field_W": merged["Qdielectric_RIP_field_W"],
        "Qdielectric_ratio_field_to_ref": merged["Qdielectric_ratio_field_to_ref"],
        "risk_zone_RUN008": merged["risk_zone_RUN008"],
        "risk_zone_RUN010": merged["risk_zone"],
        "risk_zone_changed": merged["risk_zone_RUN008"].astype(str) != merged["risk_zone"].astype(str),
        "notes": "RUN010 uses field-coupled dielectric loss; RUN008 uses approximate_Qdielectric_ref",
    })
    out.to_csv(COMPARISON, index=False)
    return out


def panel_boxes(n: int, w=1900, h=980, top=125):
    gap = 30
    left = 58
    right = 42
    pw = (w - left - right - gap * (n - 1)) / n
    return [(left + i * (pw + gap), top, left + i * (pw + gap) + pw, h - 95) for i in range(n)]


def heatmap_by_rc(metrics: pd.DataFrame, value_col: str, zone_col: str, title: str, filename: str,
                  contact: bool = False, value_fmt: str = ".1f") -> None:
    img, draw = canvas(title)
    vals = metrics[value_col].astype(float)
    vmin, vmax = vals.min(), vals.max()
    boxes = panel_boxes(5)
    for box, rc in zip(boxes, RCS):
        x0, y0, x1, y1 = box
        draw.rectangle(box, outline="#d1d5db", width=2)
        centered(draw, (x0, y0 + 8, x1, y0 + 45), f"Rc={rc:g}", fnt=FONT_BOLD)
        gx0, gy0 = x0 + 58, y0 + 70
        gx1, gy1 = x1 - 18, y1 - 70
        cw = (gx1 - gx0) / len(LOADS)
        ch = (gy1 - gy0) / len(OILS)
        for ri, oil in enumerate(OILS):
            centered(draw, (x0 + 8, gy0 + ri * ch, x0 + 55, gy0 + (ri + 1) * ch), f"{oil:g}", fnt=FONT_TINY)
        for ci, load in enumerate(LOADS):
            centered(draw, (gx0 + ci * cw, gy1 + 18, gx0 + (ci + 1) * cw, gy1 + 45), f"{load:g}", fnt=FONT_TINY)
        for ri, oil in enumerate(OILS):
            for ci, load in enumerate(LOADS):
                row = metrics[
                    (metrics.contact_resistance_multiplier_pu == rc)
                    & (metrics.oil_temperature_C == oil)
                    & (metrics.load_multiplier_pu == load)
                ].iloc[0]
                val = float(row[value_col])
                zone = str(row[zone_col])
                colors = CONTACT_COLORS if contact else RISK_COLORS
                cx0, cy0 = gx0 + ci * cw, gy0 + ri * ch
                draw.rectangle((cx0 + 2, cy0 + 2, cx0 + cw - 2, cy0 + ch - 2),
                               fill=heat_color(val, vmin, vmax), outline="white", width=2)
                draw.rectangle((cx0 + 5, cy0 + 5, cx0 + cw - 5, cy0 + ch - 5),
                               outline=colors.get(zone, "#4a5568"), width=4)
                centered(draw, (cx0, cy0 + 8, cx0 + cw, cy0 + ch / 2), format(val, value_fmt), fnt=FONT_TINY)
                centered(draw, (cx0, cy0 + ch / 2 - 4, cx0 + cw, cy0 + ch - 8), short_zone(zone), fnt=FONT_TINY)
    text(draw, (80, 910), f"Rows: oil_temperature_C; columns: load_multiplier_pu; fill: {value_col}; border: risk zone", fnt=FONT_SMALL)
    save(img, filename)


def bar_chart(draw, box, labels, values, colors, ylabel: str, threshold=None):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d1d5db", width=2)
    vals = [float(v) for v in values if math.isfinite(float(v))]
    vmin = min(0.0, min(vals) if vals else 0.0)
    vmax = max(vals) if vals else 1.0
    if threshold is not None:
        vmax = max(vmax, abs(threshold))
        vmin = min(vmin, -abs(threshold))
    pad = (vmax - vmin) * 0.12 if vmax != vmin else 1.0
    vmin -= pad
    vmax += pad
    zero = y1 - 56 - (0.0 - vmin) / (vmax - vmin) * (y1 - y0 - 115)
    draw.line((x0 + 70, zero, x1 - 35, zero), fill="#9ca3af", width=2)
    if threshold is not None:
        for th in [threshold, -threshold]:
            yy = y1 - 56 - (th - vmin) / (vmax - vmin) * (y1 - y0 - 115)
            draw.line((x0 + 70, yy, x1 - 35, yy), fill="#c53030", width=1)
    n = len(values)
    span = x1 - x0 - 120
    bw = max(5, span / max(n, 1) * 0.7)
    for i, (label, value, color) in enumerate(zip(labels, values, colors)):
        cx = x0 + 82 + (i + 0.5) * span / n
        yy = y1 - 56 - (value - vmin) / (vmax - vmin) * (y1 - y0 - 115)
        draw.rectangle((cx - bw / 2, min(yy, zero), cx + bw / 2, max(yy, zero)), fill=color)
        if n <= 40:
            centered(draw, (cx - 35, y1 - 42, cx + 35, y1 - 10), str(label), fnt=FONT_TINY)
    text(draw, (x0 + 15, y0 + 15), ylabel, fnt=FONT_SMALL, fill="#4a5568")


def line_plot(draw, box, groups, ylabel: str, xlabel: str, ylim=None):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d1d5db", width=2)
    xs = sorted({x for _, pts, _ in groups for x, _ in pts})
    ys = [y for _, pts, _ in groups for _, y in pts]
    xmin, xmax = min(xs), max(xs)
    if ylim:
        ymin, ymax = ylim
    else:
        ymin, ymax = min(ys), max(ys)
        pad = (ymax - ymin) * 0.12 if ymax > ymin else 1
        ymin -= pad
        ymax += pad

    def sx(v): return x0 + 80 + (v - xmin) / (xmax - xmin) * (x1 - x0 - 150)
    def sy(v): return y1 - 65 - (v - ymin) / (ymax - ymin) * (y1 - y0 - 130)

    draw.line((x0 + 80, y1 - 65, x1 - 70, y1 - 65), fill="#4a5568", width=2)
    draw.line((x0 + 80, y0 + 55, x0 + 80, y1 - 65), fill="#4a5568", width=2)
    text(draw, (x0 + 14, y0 + 15), ylabel, fnt=FONT_SMALL, fill="#4a5568")
    text(draw, (x1 - 175, y1 - 45), xlabel, fnt=FONT_SMALL, fill="#4a5568")
    legend_y = y0 + 20
    for name, pts, color in groups:
        xy = [(sx(x), sy(y)) for x, y in pts]
        if len(xy) > 1:
            draw.line(xy, fill=color, width=4)
        for px, py in xy:
            draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=color)
        draw.rectangle((x1 - 320, legend_y + 5, x1 - 300, legend_y + 25), fill=color)
        text(draw, (x1 - 290, legend_y), name, fnt=FONT_SMALL)
        legend_y += 27
    for x in xs:
        centered(draw, (sx(x) - 28, y1 - 55, sx(x) + 28, y1 - 28), f"{x:g}", fnt=FONT_TINY)


def fig03_boundary(boundary: pd.DataFrame):
    img, draw = canvas("Fig03 Safe load boundary by oil and Rc RUN010", 1500, 850)
    colors = ["#2b6cb0", "#c2410c", "#0f766e", "#7c3aed", "#2f855a"]
    groups = []
    for i, rc in enumerate(RCS):
        sub = boundary[boundary.contact_resistance_multiplier_pu == rc].sort_values("oil_temperature_C")
        pts = []
        for _, row in sub.iterrows():
            val = row.max_safe_load_multiplier_pu
            if isinstance(val, str) and val == "NA":
                continue
            if pd.isna(val):
                continue
            pts.append((float(row.oil_temperature_C), float(val)))
        groups.append((f"Rc={rc:g}", pts, colors[i]))
    line_plot(draw, (70, 120, 1430, 765), groups, "max_safe_load_multiplier_pu", "oil_temperature_C", (0.5, 1.5))
    save(img, "fig03_safe_load_boundary_by_oil_and_Rc_RUN010.png")


def fig06_sources(metrics: pd.DataFrame, sources: pd.DataFrame):
    merged = metrics.merge(sources, on="case_id", suffixes=("", "_src"))
    reps = [
        ("low risk", 0.6, 65.0, 1.0),
        ("baseline", 1.0, 85.0, 1.0),
        ("high contact", 1.2, 95.0, 20.0),
        ("highest pressure", 1.4, 105.0, 20.0),
    ]
    rows = []
    for label, load, oil, rc in reps:
        row = merged[
            (merged.load_multiplier_pu == load)
            & (merged.oil_temperature_C == oil)
            & (merged.contact_resistance_multiplier_pu == rc)
        ].iloc[0].copy()
        row["label"] = label
        rows.append(row)
    img, draw = canvas("Fig06 Heat source decomposition representative cases RUN010", 1500, 850)
    x0, y0, x1, y1 = 90, 150, 1410, 760
    draw.rectangle((x0, y0, x1, y1), outline="#d1d5db", width=2)
    maxv = max(float(r.Qtotal_W) for r in rows) * 1.15
    keys = [
        ("Qjoule_conductor_W", "#2b6cb0", "Qjoule"),
        ("Qcontact_W", "#c2410c", "Qcontact"),
        ("Qdielectric_RIP_field_W", "#0f766e", "Qdielectric"),
    ]
    bw = 54
    group_w = (x1 - x0 - 160) / len(rows)
    for gi, row in enumerate(rows):
        gx = x0 + 95 + gi * group_w
        accum = 0
        for key, color, label in keys:
            h = float(row[key]) / maxv * (y1 - y0 - 120)
            draw.rectangle((gx, y1 - 70 - accum - h, gx + bw, y1 - 70 - accum), fill=color)
            accum += h
        centered(draw, (gx - 60, y1 - 60, gx + bw + 60, y1 - 8), str(row["label"]), fnt=FONT_TINY)
        centered(draw, (gx - 50, y1 - 92, gx + bw + 50, y1 - 68), f"{float(row.Qtotal_W):.1f} W", fnt=FONT_TINY)
    ly = y0 + 25
    for key, color, label in keys:
        draw.rectangle((x1 - 280, ly, x1 - 255, ly + 22), fill=color)
        text(draw, (x1 - 245, ly - 2), label, fnt=FONT_SMALL)
        ly += 32
    save(img, "fig06_heat_source_decomposition_representative_cases_RUN010.png")


def fig07_residual(balance: pd.DataFrame):
    img, draw = canvas("Fig07 Heat balance residual 125 cases RUN010", 1900, 850)
    values = list(balance.residual_percent_Qgenerated)
    labels = [str(i + 1) for i in range(len(values))]
    colors = ["#2b6cb0" if abs(v) < 10 else "#c53030" for v in values]
    bar_chart(draw, (70, 130, 1830, 770), labels, values, colors, "residual_percent_Qgenerated", threshold=10)
    save(img, "fig07_heat_balance_residual_125_cases_RUN010.png")


def fig08_qcontact(sources: pd.DataFrame):
    img, draw = canvas("Fig08 Qcontact I2Rc validation RUN010", 1500, 850)
    vals = list(sources.Qcontact_relative_error_pct)
    labels = [str(i + 1) for i in range(len(vals))]
    colors = ["#2f855a" if abs(v) < 1 else "#c53030" for v in vals]
    bar_chart(draw, (70, 130, 1430, 770), labels, vals, colors, "Qcontact relative error (%)", threshold=1)
    save(img, "fig08_Qcontact_I2Rc_validation_RUN010.png")


def fig09_qjoule(metrics: pd.DataFrame, sources: pd.DataFrame):
    merged = metrics.copy()
    if "Qjoule_conductor_W" not in merged.columns:
        merged = merged.merge(sources[["case_id", "Qjoule_conductor_W"]], on="case_id", how="left")
    img, draw = canvas("Fig09 Qjoule I2 scaling validation RUN010", 1500, 850)
    groups = []
    colors = ["#2b6cb0", "#c2410c", "#0f766e", "#7c3aed", "#2f855a"]
    for i, rc in enumerate(RCS):
        sub = merged[(merged.contact_resistance_multiplier_pu == rc) & (merged.oil_temperature_C == 85.0)].sort_values("current_A")
        pts = list(zip((sub.current_A ** 2) / 1e6, sub.Qjoule_conductor_W))
        groups.append((f"Rc={rc:g}, oil=85", pts, colors[i]))
    line_plot(draw, (70, 130, 1430, 770), groups, "Qjoule_conductor_W", "I^2 / 1e6")
    save(img, "fig09_Qjoule_I2_scaling_validation_RUN010.png")


def fig10_risk_matrix(metrics: pd.DataFrame):
    img, draw = canvas("Fig10 Risk zone matrix 125 cases RUN010")
    boxes = panel_boxes(5)
    for box, rc in zip(boxes, RCS):
        x0, y0, x1, y1 = box
        draw.rectangle(box, outline="#d1d5db", width=2)
        centered(draw, (x0, y0 + 8, x1, y0 + 45), f"Rc={rc:g}", fnt=FONT_BOLD)
        gx0, gy0 = x0 + 58, y0 + 70
        gx1, gy1 = x1 - 18, y1 - 70
        cw = (gx1 - gx0) / len(LOADS)
        ch = (gy1 - gy0) / len(OILS)
        for ri, oil in enumerate(OILS):
            centered(draw, (x0 + 8, gy0 + ri * ch, x0 + 55, gy0 + (ri + 1) * ch), f"{oil:g}", fnt=FONT_TINY)
        for ci, load in enumerate(LOADS):
            centered(draw, (gx0 + ci * cw, gy1 + 18, gx0 + (ci + 1) * cw, gy1 + 45), f"{load:g}", fnt=FONT_TINY)
        for ri, oil in enumerate(OILS):
            for ci, load in enumerate(LOADS):
                row = metrics[(metrics.contact_resistance_multiplier_pu == rc) & (metrics.oil_temperature_C == oil) & (metrics.load_multiplier_pu == load)].iloc[0]
                zone = str(row.risk_zone)
                cx0, cy0 = gx0 + ci * cw, gy0 + ri * ch
                draw.rectangle((cx0 + 3, cy0 + 3, cx0 + cw - 3, cy0 + ch - 3), fill=RISK_COLORS.get(zone, "#4a5568"))
                centered(draw, (cx0, cy0 + 8, cx0 + cw, cy0 + ch / 2), row.case_id.replace("RUN010_CASE_", ""), fill="white", fnt=FONT_TINY)
                centered(draw, (cx0, cy0 + ch / 2 - 5, cx0 + cw, cy0 + ch - 8), short_zone(zone), fill="white", fnt=FONT_TINY)
    save(img, "fig10_risk_zone_matrix_125_cases_RUN010.png")


def fig11_delta(comparison: pd.DataFrame):
    temp = comparison.rename(columns={"delta_Tmax_global_C": "value", "risk_zone_RUN010": "risk_zone"}).copy()
    heatmap_by_rc(temp, "value", "risk_zone", "Fig11 RUN008 vs RUN010 Tmax delta heatmap", "fig11_RUN008_vs_RUN010_Tmax_delta_heatmap.png", value_fmt=".1f")


def fig12_zone_change(comparison: pd.DataFrame):
    img, draw = canvas("Fig12 RUN008 vs RUN010 risk zone change")
    boxes = panel_boxes(5)
    for box, rc in zip(boxes, RCS):
        x0, y0, x1, y1 = box
        draw.rectangle(box, outline="#d1d5db", width=2)
        centered(draw, (x0, y0 + 8, x1, y0 + 45), f"Rc={rc:g}", fnt=FONT_BOLD)
        gx0, gy0 = x0 + 58, y0 + 70
        gx1, gy1 = x1 - 18, y1 - 70
        cw = (gx1 - gx0) / len(LOADS)
        ch = (gy1 - gy0) / len(OILS)
        for ri, oil in enumerate(OILS):
            for ci, load in enumerate(LOADS):
                row = comparison[(comparison.contact_resistance_multiplier_pu == rc) & (comparison.oil_temperature_C == oil) & (comparison.load_multiplier_pu == load)].iloc[0]
                changed = bool(row.risk_zone_changed)
                fill = "#c53030" if changed else "#2f855a"
                cx0, cy0 = gx0 + ci * cw, gy0 + ri * ch
                draw.rectangle((cx0 + 3, cy0 + 3, cx0 + cw - 3, cy0 + ch - 3), fill=fill)
                centered(draw, (cx0, cy0 + 8, cx0 + cw, cy0 + ch / 2), row.case_id.replace("RUN010_CASE_", ""), fill="white", fnt=FONT_TINY)
                centered(draw, (cx0, cy0 + ch / 2 - 5, cx0 + cw, cy0 + ch - 8), "changed" if changed else "same", fill="white", fnt=FONT_TINY)
        for ri, oil in enumerate(OILS):
            centered(draw, (x0 + 8, gy0 + ri * ch, x0 + 55, gy0 + (ri + 1) * ch), f"{oil:g}", fnt=FONT_TINY)
        for ci, load in enumerate(LOADS):
            centered(draw, (gx0 + ci * cw, gy1 + 18, gx0 + (ci + 1) * cw, gy1 + 45), f"{load:g}", fnt=FONT_TINY)
    save(img, "fig12_RUN008_vs_RUN010_risk_zone_change.png")


def fig13_field(fields: pd.DataFrame, dielectric: pd.DataFrame):
    img, draw = canvas("Fig13 E-field diagnostic summary RUN010", 1500, 850)
    labels = ["Emean", "E95", "Eprobe", "Emax_RIP", "Emax_global"]
    values = [
        fields.Emean_RIP_V_per_m.mean(),
        fields.E95_RIP_V_per_m.mean(),
        fields.Emax_RIP_probe_excluding_edges_V_per_m.mean(),
        fields.Emax_RIP_V_per_m.mean(),
        fields.Emax_global_V_per_m.mean(),
    ]
    bar_chart(draw, (85, 140, 930, 770), labels, values, ["#0f766e", "#2b6cb0", "#c2410c", "#7c3aed", "#2f855a"], "V/m")
    text(draw, (990, 220), f"field_singularity_flag=true: {(fields.field_singularity_flag.astype(str).str.lower() == 'true').sum()}/125", fnt=FONT_BOLD)
    text(draw, (990, 280), f"screen_end_hotspot_flag=true: {(fields.screen_end_hotspot_flag.astype(str).str.lower() == 'true').sum()}/125", fnt=FONT_BOLD)
    text(draw, (990, 340), f"dielectric review=true: {(dielectric.dielectric_loss_review_required.astype(str).str.lower() == 'true').sum()}/125", fnt=FONT_BOLD)
    save(img, "fig13_Efield_diagnostic_summary_RUN010.png")


def trend_checks(metrics: pd.DataFrame, sources: pd.DataFrame) -> dict[str, bool]:
    merged = metrics.copy()
    needed = ["Qjoule_conductor_W", "Qcontact_W"]
    missing = [col for col in needed if col not in merged.columns]
    if missing:
        merged = merged.merge(sources[["case_id"] + missing], on="case_id", how="left")

    def mono(vals) -> bool:
        vals = list(vals)
        return all(vals[i + 1] + 1e-8 >= vals[i] for i in range(len(vals) - 1))

    return {
        "Tmax_global_increases_with_oil_temperature": all(
            mono(metrics[(metrics.load_multiplier_pu == load) & (metrics.contact_resistance_multiplier_pu == rc)].sort_values("oil_temperature_C").Tmax_global_C)
            for load in LOADS for rc in RCS
        ),
        "Tmax_global_increases_with_load": all(
            mono(metrics[(metrics.oil_temperature_C == oil) & (metrics.contact_resistance_multiplier_pu == rc)].sort_values("load_multiplier_pu").Tmax_global_C)
            for oil in OILS for rc in RCS
        ),
        "Tmax_contact_increases_with_Rc_factor": all(
            mono(metrics[(metrics.oil_temperature_C == oil) & (metrics.load_multiplier_pu == load)].sort_values("contact_resistance_multiplier_pu").Tmax_contact_C)
            for oil in OILS for load in LOADS
        ),
        "Qjoule_increases_with_I2": all(
            mono(merged[(merged.oil_temperature_C == oil) & (merged.contact_resistance_multiplier_pu == rc)].sort_values("load_multiplier_pu").Qjoule_conductor_W)
            for oil in OILS for rc in RCS
        ),
        "Qcontact_increases_with_I2Rc": mono(
            merged.assign(x=merged.current_A**2 * merged.contact_resistance_multiplier_pu).sort_values("x").Qcontact_W
        ),
    }


def write_report(metrics, fields, dielectric, sources, balance, validity, boundary, comparison):
    trends = trend_checks(metrics, sources)
    valid_counts = {col: Counter(validity[col].astype(str).str.lower()) for col in [
        "overall_valid", "valid_heat_balance", "valid_Qjoule", "valid_Qcontact", "valid_Qdielectric",
        "valid_selection", "field_singularity_flag", "thermal_risk",
    ]}
    all_pass = (
        len(validity) == 125
        and valid_counts["overall_valid"].get("true", 0) == 125
        and valid_counts["valid_heat_balance"].get("true", 0) == 125
        and valid_counts["valid_Qjoule"].get("true", 0) == 125
        and valid_counts["valid_Qcontact"].get("true", 0) == 125
        and valid_counts["valid_Qdielectric"].get("true", 0) == 125
        and valid_counts["valid_selection"].get("true", 0) == 125
        and valid_counts["field_singularity_flag"].get("false", 0) == 125
        and all(trends.values())
    )
    risk_counts = Counter(metrics.risk_zone.astype(str))
    contact_counts = Counter(metrics.contact_risk_zone.astype(str))
    changed = int(comparison.risk_zone_changed.astype(bool).sum())
    lines = [
        "# FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010 报告",
        "",
        "## 本轮任务目标",
        "RUN010 在 RUN008 相同 125 组核心矩阵上使用完整电场耦合介质损耗项，检查更宽工况下热源、热量收支、电场诊断和风险边界是否稳定。本轮仍不是 SCI 最终结论。",
        "",
        "## 与 RUN006-RUN009 的关系",
        "RUN010 沿用 RUN006 的 source-fixed 导体/接触热源归一化，沿用 RUN007/RUN008B 的 explicit by-ID domain/boundary selections，并在 RUN009A/B 已通过的完整电场耦合介质损耗模型上扩展到 125 组。",
        "",
        "## RUN010 与 RUN008 的区别",
        "RUN008 使用 solid-only thermal diagnostic model，并以 `approximate_Qdielectric_ref` 作为 RIP 介质损耗热源。RUN010 使用 `omega0 * eps0_solid_const * epsr_rip * tan_delta_rip * es.normE^2`，由静电场分布直接给出 RIP 介质损耗。",
        "",
        "## 125组有效性统计",
        f"- total cases: {len(validity)}",
        f"- overall_valid: {valid_counts['overall_valid'].get('true', 0)}/125",
        f"- valid_heat_balance: {valid_counts['valid_heat_balance'].get('true', 0)}/125",
        f"- valid_Qjoule: {valid_counts['valid_Qjoule'].get('true', 0)}/125",
        f"- valid_Qcontact: {valid_counts['valid_Qcontact'].get('true', 0)}/125",
        f"- valid_Qdielectric: {valid_counts['valid_Qdielectric'].get('true', 0)}/125",
        f"- valid_selection: {valid_counts['valid_selection'].get('true', 0)}/125",
        "",
        "## field_singularity_flag 统计",
        f"- field_singularity_flag=true: {valid_counts['field_singularity_flag'].get('true', 0)}/125",
        f"- field_singularity_flag=false: {valid_counts['field_singularity_flag'].get('false', 0)}/125",
        "",
        "## dielectric_loss_review_required 统计",
        f"- dielectric_loss_review_required=true: {(validity.dielectric_loss_review_required.astype(str).str.lower() == 'true').sum()}/125",
        "该标记来自 Qdielectric_field/ref 超出 [0.1,10]，保留为复核标记，不等于模型失败。",
        "",
        "## 热源分解趋势",
        f"- Qjoule relative error max: {sources.Qjoule_relative_error_pct.abs().max():.3e}%",
        f"- Qcontact relative error max: {sources.Qcontact_relative_error_pct.abs().max():.3e}%",
        f"- Qdielectric_field range: {sources.Qdielectric_RIP_field_W.min():.4f} - {sources.Qdielectric_RIP_field_W.max():.4f} W",
        "",
        "## 热量收支趋势",
        f"- max |residual_percent_Qgenerated|: {balance.residual_percent_Qgenerated.abs().max():.4f}%",
        f"- heat_balance_status counts: {dict(Counter(balance.heat_balance_status.astype(str)))}",
        "",
        "## 风险分区结果",
        f"- global risk_zone counts: {dict(risk_counts)}",
        f"- contact_risk_zone counts: {dict(contact_counts)}",
        "这些阈值仅用于诊断阶段的风险分区和可视化，不是 IEC/IEEE 标准限值、材料极限或寿命阈值。",
        "",
        "## RUN008 vs RUN010 风险边界差异",
        f"- risk_zone_changed cases: {changed}/125",
        f"- delta_Tmax_global_C range: {comparison.delta_Tmax_global_C.min():.4f} - {comparison.delta_Tmax_global_C.max():.4f}",
        f"- mean delta_Tmax_global_C: {comparison.delta_Tmax_global_C.mean():.4f}",
        "",
        "## thermal_risk_case 与 invalid_case",
        f"- thermal_risk_case: {int((metrics.risk_zone == 'thermal_risk').sum())}/125",
        f"- invalid_case: {int((validity.overall_valid.astype(str).str.lower() != 'true').sum())}/125",
        "",
        "## 趋势检查",
    ]
    lines += [f"- {k}: {'PASS' if v else 'FAIL'}" for k, v in trends.items()]
    lines += [
        "",
        "## 是否建议进入下一阶段",
        "只有当 125 组全部有效、热源归一化、电场奇异性、热量收支和趋势检查全部通过时，才建议进入材料参数敏感性或网格无关性验证。",
        "",
        f"Can proceed to MATERIAL_AND_MESH_SENSITIVITY_RUN011: {'YES' if all_pass else 'NO'}",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    metrics, fields, dielectric, sources, balance, validity, boundary = read_run010()
    comparison = make_comparison(metrics, sources)

    heatmap_by_rc(metrics, "Tmax_global_C", "risk_zone", "Fig01 Tmax heatmap load-oil by Rc RUN010", "fig01_Tmax_heatmap_load_oil_by_Rc_RUN010.png")
    heatmap_by_rc(metrics, "Tmax_contact_C", "contact_risk_zone", "Fig02 Tmax contact heatmap load-oil by Rc RUN010", "fig02_Tmax_contact_heatmap_load_oil_by_Rc_RUN010.png", contact=True)
    fig03_boundary(boundary)
    heatmap_by_rc(metrics, "Qdielectric_RIP_field_W", "risk_zone", "Fig04 Qdielectric field heatmap load-oil by Rc", "fig04_Qdielectric_field_heatmap_load_oil_by_Rc.png", value_fmt=".2f")
    heatmap_by_rc(metrics, "Qdielectric_ratio_field_to_ref", "risk_zone", "Fig05 Qdielectric ratio field-to-ref", "fig05_Qdielectric_ratio_field_to_ref.png", value_fmt=".2f")
    fig06_sources(metrics, sources)
    fig07_residual(balance)
    fig08_qcontact(sources)
    fig09_qjoule(metrics, sources)
    fig10_risk_matrix(metrics)
    fig11_delta(comparison)
    fig12_zone_change(comparison)
    fig13_field(fields, dielectric)
    write_report(metrics, fields, dielectric, sources, balance, validity, boundary, comparison)


if __name__ == "__main__":
    main()
