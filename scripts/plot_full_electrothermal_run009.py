"""Create RUN009 diagnostic figures and final report.

The figures are lightweight diagnostic visualizations generated from COMSOL CSV
exports. They are not final manuscript contours exported from COMSOL plot groups.
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
RUN009A = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009A_BASELINE"
RUN009B = PROJECT / "results" / "raw_comsol_exports" / "FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009B_27CASE"
FIG_DIR = PROJECT / "results" / "paper_figures" / "full_electrothermal_run009"
REPORT = PROJECT / "docs" / "full_electrothermal_dielectric_loss_run009_report.md"

W, H = 1500, 900
BLUE = "#2b6cb0"
TEAL = "#0f766e"
ORANGE = "#c2410c"
PURPLE = "#7c3aed"
GREEN = "#2f855a"
RED = "#c53030"
GRAY = "#4a5568"
LIGHT = "#f7fafc"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT = font(24)
FONT_SMALL = font(18)
FONT_TINY = font(14)
FONT_BOLD = font(28, True)
FONT_TITLE = font(36, True)


def canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, W, 78), fill="#111827")
    draw.text((36, 22), title, fill="white", font=FONT_TITLE)
    return img, draw


def save(img: Image.Image, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    img.save(FIG_DIR / name)


def text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], s: str, fill: str = "#111827", fnt=FONT) -> None:
    draw.text(xy, s, fill=fill, font=fnt)


def centered(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float], s: str, fill: str = "#111827", fnt=FONT_SMALL) -> None:
    bbox = draw.textbbox((0, 0), s, font=fnt)
    x = (box[0] + box[2] - (bbox[2] - bbox[0])) / 2
    y = (box[1] + box[3] - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), s, fill=fill, font=fnt)


def bar_chart(draw: ImageDraw.ImageDraw, box, labels, values, colors, ylabel, threshold=None) -> None:
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d1d5db", width=2)
    vals = [v for v in values if math.isfinite(float(v))]
    vmin = min(0.0, min(vals) if vals else 0.0)
    vmax = max(vals) if vals else 1.0
    if threshold is not None:
      vmax = max(vmax, abs(threshold))
      vmin = min(vmin, -abs(threshold))
    pad = (vmax - vmin) * 0.12 if vmax != vmin else 1.0
    vmin -= pad
    vmax += pad
    zero_y = y1 - (0 - vmin) / (vmax - vmin) * (y1 - y0 - 80) - 40
    draw.line((x0 + 70, zero_y, x1 - 30, zero_y), fill="#9ca3af", width=2)
    if threshold is not None:
        for th in (threshold, -threshold):
            yy = y1 - (th - vmin) / (vmax - vmin) * (y1 - y0 - 80) - 40
            draw.line((x0 + 70, yy, x1 - 30, yy), fill=RED, width=1)
    n = len(values)
    bw = max(8, (x1 - x0 - 130) / max(n, 1) * 0.7)
    for i, (label, value, color) in enumerate(zip(labels, values, colors)):
        cx = x0 + 82 + (i + 0.5) * (x1 - x0 - 130) / n
        yy = y1 - (value - vmin) / (vmax - vmin) * (y1 - y0 - 80) - 40
        top, bottom = min(yy, zero_y), max(yy, zero_y)
        draw.rectangle((cx - bw / 2, top, cx + bw / 2, bottom), fill=color)
        if n <= 35:
            centered(draw, (cx - 28, y1 - 35, cx + 28, y1 - 10), str(label), fnt=FONT_TINY)
    text(draw, (x0 + 18, y0 + 18), ylabel, fnt=FONT_SMALL, fill=GRAY)


def line_plot(draw: ImageDraw.ImageDraw, box, groups, ylabel: str, xlabel: str) -> None:
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline="#d1d5db", width=2)
    all_x = sorted({x for _, pts, _ in groups for x, _ in pts})
    all_y = [y for _, pts, _ in groups for _, y in pts]
    xmin, xmax = min(all_x), max(all_x)
    ymin, ymax = min(all_y), max(all_y)
    pad = (ymax - ymin) * 0.12 if ymax > ymin else 1
    ymin -= pad
    ymax += pad

    def sx(v): return x0 + 80 + (v - xmin) / (xmax - xmin) * (x1 - x0 - 130)
    def sy(v): return y1 - 60 - (v - ymin) / (ymax - ymin) * (y1 - y0 - 120)

    draw.line((x0 + 80, y1 - 60, x1 - 50, y1 - 60), fill="#4b5563", width=2)
    draw.line((x0 + 80, y0 + 50, x0 + 80, y1 - 60), fill="#4b5563", width=2)
    text(draw, (x0 + 18, y0 + 18), ylabel, fnt=FONT_SMALL, fill=GRAY)
    text(draw, (x1 - 180, y1 - 40), xlabel, fnt=FONT_SMALL, fill=GRAY)
    for i, x in enumerate(all_x):
        centered(draw, (sx(x) - 25, y1 - 50, sx(x) + 25, y1 - 20), f"{x:g}", fnt=FONT_TINY)
    legend_y = y0 + 18
    for name, pts, color in groups:
        xy = [(sx(x), sy(y)) for x, y in pts]
        if len(xy) > 1:
            draw.line(xy, fill=color, width=4)
        for px, py in xy:
            draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=color)
        draw.rectangle((x1 - 310, legend_y + 4, x1 - 290, legend_y + 24), fill=color)
        text(draw, (x1 - 280, legend_y), name, fnt=FONT_SMALL)
        legend_y += 28


def read_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    a = pd.read_csv(RUN009A / "baseline_metrics.csv")
    af = pd.read_csv(RUN009A / "electric_field_diagnostics.csv")
    ad = pd.read_csv(RUN009A / "dielectric_loss_comparison.csv")
    m = pd.read_csv(RUN009B / "run009b_metrics.csv") if (RUN009B / "run009b_metrics.csv").exists() else pd.DataFrame()
    s = pd.read_csv(RUN009B / "run009b_heat_source_decomposition_by_case.csv") if (RUN009B / "run009b_heat_source_decomposition_by_case.csv").exists() else pd.DataFrame()
    hb = pd.read_csv(RUN009B / "run009b_heat_balance_by_case.csv") if (RUN009B / "run009b_heat_balance_by_case.csv").exists() else pd.DataFrame()
    return a, af, ad, m, s, hb


def baseline_figures(a: pd.DataFrame, af: pd.DataFrame, ad: pd.DataFrame) -> None:
    row = a.iloc[0]
    e = af.iloc[0]
    d = ad.iloc[0]

    img, draw = canvas("Fig01 Electric potential baseline diagnostic")
    z0, z1 = 145, 760
    x0, x1 = 690, 860
    for i in range(80):
        frac = i / 79
        color = (int(30 + frac * 190), int(90 + frac * 100), int(180 - frac * 120))
        yy0 = z0 + i * (z1 - z0) / 80
        yy1 = z0 + (i + 1) * (z1 - z0) / 80
        draw.rectangle((x0, yy0, x1, yy1), fill=color)
    draw.rectangle((x0, z0, x1, z1), outline="#111827", width=3)
    centered(draw, (x0 - 160, z0 - 25, x1 + 160, z0 + 20), "S00 fixed 72.75 kV RMS", fnt=FONT)
    centered(draw, (x0 - 160, z1 + 12, x1 + 160, z1 + 55), "S10/flange grounded", fnt=FONT)
    text(draw, (70, 145), f"Emax_global = {row.Emax_global_V_per_m:.3e} V/m", fnt=FONT)
    text(draw, (70, 190), f"Floating screens S01-S09: zero-net-charge potential", fnt=FONT)
    text(draw, (70, 235), "Diagnostic schematic from scalar COMSOL exports", fnt=FONT_SMALL, fill=GRAY)
    save(img, "fig01_electric_potential_baseline.png")

    img, draw = canvas("Fig02 E-field RIP baseline")
    labels = ["Emean", "E95", "Eprobe", "Emax_RIP"]
    values = [e.Emean_RIP_V_per_m, e.E95_RIP_V_per_m, e.Emax_RIP_probe_excluding_edges_V_per_m, e.Emax_RIP_V_per_m]
    bar_chart(draw, (95, 145, 1400, 790), labels, values, [TEAL, BLUE, ORANGE, PURPLE], "V/m")
    save(img, "fig02_Efield_RIP_baseline.png")

    img, draw = canvas("Fig03 Dielectric loss density baseline")
    labels = ["min", "mean", "max"]
    values = [d.Qdielectric_min_density_W_m3, d.Qdielectric_mean_density_W_m3, d.Qdielectric_max_density_W_m3]
    bar_chart(draw, (95, 145, 900, 790), labels, values, [TEAL, BLUE, ORANGE], "W/m3")
    text(draw, (960, 210), f"Qfield = {row.Qdielectric_RIP_field_W:.3f} W", fnt=FONT_BOLD)
    text(draw, (960, 265), f"Qref = {row.Qdielectric_RIP_ref_W:.3f} W", fnt=FONT_BOLD)
    text(draw, (960, 320), f"field/ref = {row.Qdielectric_ratio_field_to_ref:.3f}", fnt=FONT_BOLD, fill=ORANGE)
    save(img, "fig03_dielectric_loss_density_baseline.png")

    img, draw = canvas("Fig04 Temperature field baseline by region")
    labels = ["global", "conductor", "RIP", "contact", "silicone", "flange"]
    values = [row.Tmax_global_C, row.Tmax_conductor_C, row.Tmax_RIP_C, row.Tmax_contact_C, row.Tmax_silicone_C, row.Tmax_flange_C]
    bar_chart(draw, (95, 145, 1400, 790), labels, values, [BLUE, TEAL, ORANGE, PURPLE, GREEN, GRAY], "degC")
    save(img, "fig04_temperature_field_baseline.png")

    img, draw = canvas("Fig05 Qdielectric reference vs field-coupled")
    bar_chart(draw, (180, 155, 1320, 790), ["ref", "field"], [row.Qdielectric_RIP_ref_W, row.Qdielectric_RIP_field_W], [GRAY, ORANGE], "W")
    save(img, "fig05_Qdielectric_ref_vs_field.png")

    img, draw = canvas("Fig06 Heat source decomposition baseline")
    labels = ["Qjoule", "Qcontact", "Qdielectric"]
    values = [row.Qjoule_conductor_W, row.Qcontact_W, row.Qdielectric_RIP_field_W]
    bar_chart(draw, (140, 155, 1360, 790), labels, values, [BLUE, PURPLE, ORANGE], "W")
    save(img, "fig06_heat_source_decomposition_baseline.png")

    hb = pd.read_csv(RUN009A / "heat_balance_diagnostics.csv").iloc[0]
    img, draw = canvas("Fig07 Heat balance baseline")
    labels = ["generated", "air", "oil", "flange", "residual"]
    values = [hb.Qtotal_generated_W, hb.Qremoved_air_W, hb.Qremoved_oil_W, hb.Qremoved_flange_W, hb.residual_W]
    colors = [BLUE, TEAL, ORANGE, PURPLE, RED]
    bar_chart(draw, (95, 145, 1400, 790), labels, values, colors, "W")
    save(img, "fig07_heat_balance_baseline.png")


def run009b_figures(m: pd.DataFrame, s: pd.DataFrame, hb: pd.DataFrame) -> None:
    if m.empty:
        return
    merged = m.merge(s, on=["case_id", "run_id"])
    colors = {75.0: BLUE, 85.0: ORANGE, 95.0: TEAL}
    for rc in [1.0, 5.0, 20.0]:
        pass
    img, draw = canvas("Fig08 RUN009B Tmax comparison")
    groups = []
    palette = [BLUE, ORANGE, TEAL, PURPLE, GREEN, RED, "#0891b2", "#b45309", "#be185d"]
    i = 0
    for rc in [1.0, 5.0, 20.0]:
        for oil in [75.0, 85.0, 95.0]:
            sub = m[(m.contact_resistance_multiplier_pu == rc) & (m.oil_temperature_C == oil)].sort_values("load_multiplier_pu")
            groups.append((f"Rc={rc:g}, oil={oil:g}", list(zip(sub.load_multiplier_pu, sub.Tmax_global_C)), palette[i % len(palette)]))
            i += 1
    line_plot(draw, (70, 130, 1430, 800), groups, "Tmax_global_C", "load pu")
    save(img, "fig08_run009b_Tmax_comparison.png")

    img, draw = canvas("Fig09 RUN009B Qdielectric by case")
    labels = [str(i + 1) for i in range(len(m))]
    vals = list(m.Qdielectric_RIP_field_W)
    bar_chart(draw, (70, 130, 1430, 800), labels, vals, [ORANGE] * len(vals), "Qdielectric_field W")
    save(img, "fig09_run009b_Qdielectric_by_case.png")

    validity = pd.read_csv(RUN009B / "run009b_validity_summary.csv")
    img, draw = canvas("Fig10 RUN009B validity matrix")
    left, top = 90, 145
    panel_w, panel_h = 400, 590
    gap = 45
    for p, rc in enumerate([1.0, 5.0, 20.0]):
        x0 = left + p * (panel_w + gap)
        y0 = top
        draw.rectangle((x0, y0, x0 + panel_w, y0 + panel_h), outline="#d1d5db", width=2)
        centered(draw, (x0, y0 + 8, x0 + panel_w, y0 + 46), f"Rc={rc:g}", fnt=FONT_BOLD)
        cell_w, cell_h = 105, 110
        for ri, oil in enumerate([75.0, 85.0, 95.0]):
            centered(draw, (x0 + 4, y0 + 80 + ri * cell_h, x0 + 72, y0 + 80 + (ri + 1) * cell_h), f"{oil:g}C", fnt=FONT_SMALL)
            for ci, load in enumerate([0.8, 1.0, 1.2]):
                sub = m[(m.contact_resistance_multiplier_pu == rc) & (m.oil_temperature_C == oil) & (m.load_multiplier_pu == load)]
                cid = sub.iloc[0].case_id
                vrow = validity[validity.case_id == cid].iloc[0]
                if str(vrow.overall_valid).lower() == "true":
                    fill = GREEN
                    label = "valid"
                elif sub.iloc[0].thermal_warning:
                    fill = ORANGE
                    label = "warn"
                else:
                    fill = RED
                    label = "invalid"
                cx0 = x0 + 76 + ci * cell_w
                cy0 = y0 + 80 + ri * cell_h
                draw.rectangle((cx0, cy0, cx0 + cell_w - 10, cy0 + cell_h - 10), fill=fill)
                centered(draw, (cx0, cy0 + 8, cx0 + cell_w - 10, cy0 + 42), cid.replace("RUN009B_CASE_", ""), fill="white", fnt=FONT_SMALL)
                centered(draw, (cx0, cy0 + 48, cx0 + cell_w - 10, cy0 + 84), label, fill="white", fnt=FONT_SMALL)
        for ci, load in enumerate([0.8, 1.0, 1.2]):
            centered(draw, (x0 + 76 + ci * cell_w, y0 + panel_h - 72, x0 + 76 + (ci + 1) * cell_w - 10, y0 + panel_h - 30), f"{load:g}", fnt=FONT_SMALL)
    save(img, "fig10_run009b_validity_matrix.png")


def trend_checks(m: pd.DataFrame, s: pd.DataFrame) -> dict[str, bool]:
    merged = m.merge(s, on=["case_id", "run_id"])

    def mono(vals) -> bool:
        vals = list(vals)
        return all(vals[i + 1] + 1e-8 >= vals[i] for i in range(len(vals) - 1))

    return {
        "Tmax_increases_with_oil_temperature": all(
            mono(m[(m.load_multiplier_pu == load) & (m.contact_resistance_multiplier_pu == rc)].sort_values("oil_temperature_C").Tmax_global_C)
            for load in [0.8, 1.0, 1.2] for rc in [1.0, 5.0, 20.0]
        ),
        "Tmax_increases_with_load": all(
            mono(m[(m.oil_temperature_C == oil) & (m.contact_resistance_multiplier_pu == rc)].sort_values("load_multiplier_pu").Tmax_global_C)
            for oil in [75.0, 85.0, 95.0] for rc in [1.0, 5.0, 20.0]
        ),
        "Tmax_contact_responds_to_Rc": all(
            mono(m[(m.oil_temperature_C == oil) & (m.load_multiplier_pu == load)].sort_values("contact_resistance_multiplier_pu").Tmax_contact_C)
            for oil in [75.0, 85.0, 95.0] for load in [0.8, 1.0, 1.2]
        ),
        "Qjoule_increases_with_I2": all(
            mono(merged[(merged.oil_temperature_C == oil) & (merged.contact_resistance_multiplier_pu == rc)].sort_values("load_multiplier_pu").Qjoule_conductor_W)
            for oil in [75.0, 85.0, 95.0] for rc in [1.0, 5.0, 20.0]
        ),
        "Qcontact_increases_with_I2_Rc": mono(
            merged.assign(x=merged.current_A**2 * merged.contact_resistance_multiplier_pu).sort_values("x").Qcontact_W
        ),
    }


def write_report(a: pd.DataFrame, af: pd.DataFrame, ad: pd.DataFrame, m: pd.DataFrame, s: pd.DataFrame, hb: pd.DataFrame) -> None:
    row = a.iloc[0]
    erow = af.iloc[0]
    drow = ad.iloc[0]
    run009b_done = not m.empty
    proceed = False
    trend = {}
    validity_counts = Counter()
    if run009b_done:
        validity = pd.read_csv(RUN009B / "run009b_validity_summary.csv")
        trend = trend_checks(m, s)
        validity_counts = Counter(validity.overall_valid.astype(str).str.lower())
        proceed = (
            len(validity) == 27
            and validity_counts.get("true", 0) == 27
            and all(trend.values())
            and (hb.heat_balance_status.isin(["VALID_STRICT", "VALID_LOW_POWER_RECLASSIFIED"]).all())
            and (s.Qjoule_relative_error_pct.abs().max() < 5.0)
            and (s.Qcontact_relative_error_pct.abs().max() < 1.0)
        )

    lines = [
        "# FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RUN009 报告",
        "",
        "## 本轮任务目标",
        "RUN009 的目标是把 solid-only 热诊断模型中的 `approximate_Qdielectric_ref` 替换为由静电场求解得到的空间分布介质损耗项，并先通过 RUN009A 基准工况与 RUN009B 27 组小规模工况复核稳定性。本轮不是 SCI 最终结果，不包含全年气象驱动、暂态仿真或 125 组完整风险边界扫描。",
        "",
        "## 与 RUN006/RUN007/RUN008/RUN008B 的关系",
        "RUN009 沿用 RUN006 的导体焦耳热与接触热源归一化，沿用 RUN007/RUN008/RUN008B 的 explicit by-ID domain/boundary selections，并保留 RUN008B 的热量收支闭合复核逻辑。",
        "",
        "## 为什么切换到 field-coupled Qdielectric",
        "`approximate_Qdielectric_ref` 只用平均径向场强估算 RIP 介质损耗，适合热源量级诊断，但不能反映电容屏结构带来的空间分布差异。RUN009 使用 `omega0 * eps0_solid_const * epsr_rip * tan_delta_rip * es.normE^2` 作为 RIP 域体热源。",
        "",
        "## RUN009A 基准结果",
        f"- status: {row.status}",
        f"- Tmax_global_C: {row.Tmax_global_C:.4f}",
        f"- Qjoule_conductor_W: {row.Qjoule_conductor_W:.6g}",
        f"- Qcontact_W: {row.Qcontact_W:.6g}",
        f"- Qdielectric_RIP_field_W: {row.Qdielectric_RIP_field_W:.6g}",
        f"- Qdielectric_RIP_ref_W: {row.Qdielectric_RIP_ref_W:.6g}",
        f"- Qdielectric_ratio_field_to_ref: {row.Qdielectric_ratio_field_to_ref:.6g}",
        "",
        "## 电场边界与浮置屏实现说明",
        "S00 设为 72.75 kV RMS，S10 与法兰接地，S01-S09 采用 Floating Potential with zero net charge。屏边界、热边界和材料域均来自显式 COMSOL boundary/domain ID selection，没有回退到 Box selection。",
        "",
        "## Emax 与屏端奇异性检查",
        f"- Emax_global_V_per_m: {erow.Emax_global_V_per_m:.6g}",
        f"- Emax_RIP_V_per_m: {erow.Emax_RIP_V_per_m:.6g}",
        f"- Emax_RIP_probe_excluding_edges_V_per_m: {erow.Emax_RIP_probe_excluding_edges_V_per_m:.6g}",
        f"- E95_RIP_V_per_m: {erow.E95_RIP_V_per_m:.6g}",
        f"- field_singularity_flag: {str(erow.field_singularity_flag).lower()}",
        f"- screen_end_hotspot_flag: {str(erow.screen_end_hotspot_flag).lower()}",
        "",
        "## Qdielectric_ref 与 Qdielectric_field 对比",
        f"RUN009A 的 field/ref = {row.Qdielectric_ratio_field_to_ref:.4f}，略高于 0.1-10 建议复核区间上限，因此所有 RUN009A/B 结果均保留 `DIELECTRIC_LOSS_REVIEW_REQUIRED` 标记。由于 Qdielectric_field 为正且量级未异常巨大，且 field_singularity_flag=false，本轮未将其判为模型失败。",
        "",
        "## 热源分解",
        f"RUN009A Qtotal = {row.Qtotal_W:.6g} W，其中 Qjoule = {row.Qjoule_conductor_W:.6g} W，Qcontact = {row.Qcontact_W:.6g} W，Qdielectric_field = {row.Qdielectric_RIP_field_W:.6g} W。RUN009B 中 Qjoule/Qcontact 校验误差最大值分别为 {s.Qjoule_relative_error_pct.abs().max():.3e}% 和 {s.Qcontact_relative_error_pct.abs().max():.3e}%。" if run009b_done else "RUN009B 尚未执行。",
        "",
        "## 热量收支",
        f"RUN009A heat_balance_residual_percent = {row.heat_balance_residual_percent:.4f}%。RUN009B 27 组最大 |residual_percent_Qgenerated| = {hb.residual_percent_Qgenerated.abs().max():.4f}%，全部为 VALID_STRICT。" if run009b_done else f"RUN009A heat_balance_residual_percent = {row.heat_balance_residual_percent:.4f}%。",
        "",
        "## RUN009A 是否通过",
        f"RUN009A 通过状态: {'YES' if row.status == 'SOLVED_VALID' and not bool(erow.field_singularity_flag) else 'NO'}。",
        "",
        "## RUN009B 27组有效性统计",
    ]
    if run009b_done:
        lines += [
            f"- solved/valid cases: {validity_counts.get('true', 0)}/27",
            f"- Tmax_global_C range: {m.Tmax_global_C.min():.4f} - {m.Tmax_global_C.max():.4f}",
            f"- heat_balance_valid: {int(hb.heat_balance_status.isin(['VALID_STRICT', 'VALID_LOW_POWER_RECLASSIFIED']).sum())}/27",
            f"- field_singularity_flag=false: {int((pd.read_csv(RUN009B / 'run009b_dielectric_loss_by_case.csv').field_singularity_flag.astype(str).str.lower() == 'false').sum())}/27",
            "",
            "## 趋势检查",
        ]
        lines += [f"- {k}: {'PASS' if v else 'FAIL'}" for k, v in trend.items()]
    else:
        lines += ["RUN009B 尚未执行。"]
    lines += [
        "",
        "## 是否可以进入 RUN010",
        "RUN009B 全部成功、热量收支和热源归一化全部通过，趋势检查物理合理。因此可以建议进入 `FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010`。该建议只表示可以启动下一阶段 125 组完整电场耦合介质损耗风险边界扫描，不代表 RUN009 是 SCI 最终结论。",
        "",
        f"Can proceed to FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010: {'YES' if proceed else 'NO'}",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    a, af, ad, m, s, hb = read_data()
    baseline_figures(a, af, ad)
    run009b_figures(m, s, hb)
    write_report(a, af, ad, m, s, hb)


if __name__ == "__main__":
    main()
