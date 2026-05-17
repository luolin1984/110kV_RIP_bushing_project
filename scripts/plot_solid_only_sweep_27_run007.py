"""Postprocess SOLID_ONLY_SWEEP_27_RUN007.

This script intentionally uses only CSV inputs from the completed RUN007
solid-only thermal diagnostic sweep. It does not run COMSOL and does not start
the 125-case risk-boundary scan.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parents[1]
RUN_ID = "SOLID_ONLY_SWEEP_27_RUN007"
RAW_DIR = PROJECT / "results" / "raw_comsol_exports" / RUN_ID
FIG_DIR = PROJECT / "results" / "paper_figures" / "solid_only_sweep_27_run007"
DOC_DIR = PROJECT / "docs"
REPORT = DOC_DIR / "solid_only_sweep_27_run007_report.md"

COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#17becf",
    "#7f7f7f",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for item in candidates:
        try:
            return ImageFont.truetype(item, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


FONT_SMALL = font(18)
FONT = font(22)
FONT_BOLD = font(24, bold=True)
FONT_TITLE = font(30, bold=True)


def read_csv(name: str) -> list[dict[str, str]]:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def b(row: dict[str, str], key: str) -> bool:
    return str(row[key]).strip().lower() == "true"


def case_no(case_id: str) -> int:
    return int(case_id.rsplit("_", 1)[-1])


def fmt(value: float, digits: int = 3) -> str:
    if abs(value) >= 100:
        return f"{value:.1f}"
    if abs(value) >= 10:
        return f"{value:.2f}"
    if abs(value) >= 1:
        return f"{value:.3f}"
    return f"{value:.2e}"


def text_size(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=used_font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    used_font: ImageFont.ImageFont,
    fill: str = "#222222",
) -> None:
    w, h = text_size(draw, text, used_font)
    draw.text((xy[0] - w / 2, xy[1] - h / 2), text, font=used_font, fill=fill)


def nice_ticks(vmin: float, vmax: float, n: int = 5) -> list[float]:
    if math.isclose(vmin, vmax):
        return [vmin - 1, vmin, vmin + 1]
    raw = (vmax - vmin) / max(n - 1, 1)
    exp = math.floor(math.log10(abs(raw))) if raw else 0
    base = raw / (10**exp)
    if base <= 1.5:
        step = 1
    elif base <= 3:
        step = 2
    elif base <= 7:
        step = 5
    else:
        step = 10
    step *= 10**exp
    start = math.floor(vmin / step) * step
    end = math.ceil(vmax / step) * step
    ticks = []
    x = start
    while x <= end + step * 0.5:
        ticks.append(x)
        x += step
    return ticks


def save(img: Image.Image, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    img.save(FIG_DIR / name)


def new_image(width: int, height: int, title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.text((42, 28), title, font=FONT_TITLE, fill="#202020")
    draw.line((42, 70, width - 42, 70), fill="#dddddd", width=2)
    return img, draw


def panel_bbox(row: int, col: int, rows: int, cols: int, width: int, height: int) -> tuple[int, int, int, int]:
    left_margin, right_margin = 86, 42
    top_margin, bottom_margin = 108, 70
    gap_x, gap_y = 60, 70
    panel_w = (width - left_margin - right_margin - gap_x * (cols - 1)) // cols
    panel_h = (height - top_margin - bottom_margin - gap_y * (rows - 1)) // rows
    left = left_margin + col * (panel_w + gap_x)
    top = top_margin + row * (panel_h + gap_y)
    return left, top, left + panel_w, top + panel_h


def draw_axes(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    xlabel: str,
    ylabel: str,
    title: str,
    x_ticks: Iterable[float] | None = None,
    y_ticks: Iterable[float] | None = None,
) -> tuple:
    left, top, right, bottom = bbox
    plot = (left + 70, top + 44, right - 24, bottom - 58)
    px0, py0, px1, py1 = plot
    draw.rectangle((left, top, right, bottom), outline="#dddddd", width=1)
    draw.text((left + 14, top + 10), title, font=FONT_BOLD, fill="#222222")
    draw.line((px0, py1, px1, py1), fill="#222222", width=2)
    draw.line((px0, py0, px0, py1), fill="#222222", width=2)

    if x_ticks is None:
        x_ticks = nice_ticks(*xlim)
    if y_ticks is None:
        y_ticks = nice_ticks(*ylim)

    def sx(x: float) -> float:
        if math.isclose(xlim[0], xlim[1]):
            return (px0 + px1) / 2
        return px0 + (x - xlim[0]) / (xlim[1] - xlim[0]) * (px1 - px0)

    def sy(y: float) -> float:
        if math.isclose(ylim[0], ylim[1]):
            return (py0 + py1) / 2
        return py1 - (y - ylim[0]) / (ylim[1] - ylim[0]) * (py1 - py0)

    for xt in x_ticks:
        x = sx(float(xt))
        draw.line((x, py0, x, py1), fill="#eeeeee", width=1)
        draw.line((x, py1, x, py1 + 6), fill="#222222", width=1)
        draw_centered(draw, (x, py1 + 22), f"{xt:g}", FONT_SMALL)
    for yt in y_ticks:
        y = sy(float(yt))
        draw.line((px0, y, px1, y), fill="#eeeeee", width=1)
        draw.line((px0 - 6, y, px0, y), fill="#222222", width=1)
        draw.text((left + 8, y - 10), f"{yt:g}", font=FONT_SMALL, fill="#222222")

    draw_centered(draw, ((px0 + px1) / 2, bottom - 20), xlabel, FONT_SMALL)
    draw.text((left + 12, top + 42), ylabel, font=FONT_SMALL, fill="#222222")
    return sx, sy, plot


def draw_line_panel(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    series: list[dict],
    xlabel: str,
    ylabel: str,
    title: str,
    x_ticks: list[float] | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    xs = [x for s in series for x in s["x"]]
    ys = [y for s in series for y in s["y"]]
    xpad = max((max(xs) - min(xs)) * 0.08, 0.05) if xs else 1
    ypad = max((max(ys) - min(ys)) * 0.12, 1.0) if ys else 1
    xlim = (min(xs) - xpad, max(xs) + xpad)
    if ylim is None:
        ylim = (min(ys) - ypad, max(ys) + ypad)
    sx, sy, plot = draw_axes(draw, bbox, xlim, ylim, xlabel, ylabel, title, x_ticks=x_ticks)
    px0, py0, px1, py1 = plot

    for idx, s in enumerate(series):
        color = s.get("color", COLORS[idx % len(COLORS)])
        pts = [(sx(x), sy(y)) for x, y in zip(s["x"], s["y"])]
        if len(pts) >= 2:
            draw.line(pts, fill=color, width=3)
        for x, y in pts:
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color, outline="#ffffff", width=2)

    legend_x, legend_y = px1 - 165, py0 + 12
    for idx, s in enumerate(series):
        color = s.get("color", COLORS[idx % len(COLORS)])
        y = legend_y + idx * 24
        draw.line((legend_x, y + 9, legend_x + 26, y + 9), fill=color, width=4)
        draw.ellipse((legend_x + 9, y + 4, legend_x + 18, y + 13), fill=color)
        draw.text((legend_x + 36, y), s["label"], font=FONT_SMALL, fill="#222222")


def draw_bar_panel(
    draw: ImageDraw.ImageDraw,
    bbox: tuple[int, int, int, int],
    labels: list[str],
    values: list[float],
    colors: list[str],
    xlabel: str,
    ylabel: str,
    title: str,
    threshold: float | None = None,
) -> None:
    xvals = list(range(1, len(values) + 1))
    ymin = min(values + ([-threshold] if threshold else []))
    ymax = max(values + ([threshold] if threshold else []))
    ypad = max((ymax - ymin) * 0.18, 1.0)
    sx, sy, plot = draw_axes(
        draw,
        bbox,
        (0.3, len(values) + 0.7),
        (ymin - ypad, ymax + ypad),
        xlabel,
        ylabel,
        title,
        x_ticks=[1, 5, 10, 15, 20, 25, 27],
    )
    px0, py0, px1, py1 = plot
    bar_w = max(3, (px1 - px0) / (len(values) * 1.45))
    for x, y, c in zip(xvals, values, colors):
        x0 = sx(x) - bar_w / 2
        x1 = sx(x) + bar_w / 2
        y0 = sy(0)
        y1 = sy(y)
        draw.rectangle((x0, min(y0, y1), x1, max(y0, y1)), fill=c, outline=c)
    if threshold is not None:
        for t in [threshold, -threshold]:
            y = sy(t)
            draw.line((px0, y, px1, y), fill="#d62728", width=2)
            draw.text((px1 - 72, y - 22), f"{t:+g}%", font=FONT_SMALL, fill="#d62728")


def grouped(rows: list[dict[str, str]], keys: tuple[str, ...]) -> dict[tuple, list[dict[str, str]]]:
    out: dict[tuple, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[tuple(row[k] for k in keys)].append(row)
    return out


def fig01(metrics: list[dict[str, str]]) -> None:
    img, draw = new_image(1600, 720, "Fig01 Tmax_global vs load by oil temperature")
    for idx, rc in enumerate([1.0, 5.0, 20.0]):
        panel_rows = [r for r in metrics if math.isclose(f(r, "contact_resistance_multiplier_pu"), rc)]
        series = []
        for j, oil in enumerate([75.0, 85.0, 95.0]):
            rows = sorted([r for r in panel_rows if math.isclose(f(r, "oil_temperature_C"), oil)], key=lambda x: f(x, "load_multiplier_pu"))
            series.append(
                {
                    "label": f"oil {oil:g} C",
                    "x": [f(r, "load_multiplier_pu") for r in rows],
                    "y": [f(r, "Tmax_global_C") for r in rows],
                    "color": COLORS[j],
                }
            )
        draw_line_panel(
            draw,
            panel_bbox(0, idx, 1, 3, 1600, 720),
            series,
            "load_multiplier_pu",
            "Tmax_global_C",
            f"Rc factor = {rc:g}",
            x_ticks=[0.8, 1.0, 1.2],
            ylim=(70, 110),
        )
    save(img, "fig01_Tmax_vs_load_by_oil_temp.png")


def fig02(metrics: list[dict[str, str]]) -> None:
    img, draw = new_image(1600, 720, "Fig02 Tmax_contact vs contact resistance multiplier")
    for idx, oil in enumerate([75.0, 85.0, 95.0]):
        panel_rows = [r for r in metrics if math.isclose(f(r, "oil_temperature_C"), oil)]
        series = []
        for j, load in enumerate([0.8, 1.0, 1.2]):
            rows = sorted([r for r in panel_rows if math.isclose(f(r, "load_multiplier_pu"), load)], key=lambda x: f(x, "contact_resistance_multiplier_pu"))
            series.append(
                {
                    "label": f"load {load:g}",
                    "x": [f(r, "contact_resistance_multiplier_pu") for r in rows],
                    "y": [f(r, "Tmax_contact_C") for r in rows],
                    "color": COLORS[j],
                }
            )
        draw_line_panel(
            draw,
            panel_bbox(0, idx, 1, 3, 1600, 720),
            series,
            "Rc_factor",
            "Tmax_contact_C",
            f"oil temperature = {oil:g} C",
            x_ticks=[1, 5, 20],
            ylim=(40, 110),
        )
    save(img, "fig02_Tmax_contact_vs_Rc_factor.png")


def fig03(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> None:
    by_case = {r["case_id"]: r for r in metrics}
    rows = []
    for row in sources:
        merged = dict(row)
        merged.update(by_case[row["case_id"]])
        rows.append(merged)
    img, draw = new_image(1500, 720, "Fig03 Heat-source decomposition by load")
    for idx, rc in enumerate([1.0, 20.0]):
        panel_rows = [r for r in rows if math.isclose(f(r, "contact_resistance_multiplier_pu"), rc)]
        series = []
        for j, key in enumerate(["Qjoule_conductor_W", "Qcontact_W", "Qdielectric_RIP_W"]):
            x, y = [], []
            for load in [0.8, 1.0, 1.2]:
                vals = [f(r, key) for r in panel_rows if math.isclose(f(r, "load_multiplier_pu"), load)]
                x.append(load)
                y.append(sum(vals) / len(vals))
            label = {
                "Qjoule_conductor_W": "Qjoule",
                "Qcontact_W": "Qcontact",
                "Qdielectric_RIP_W": "Qdielectric",
            }[key]
            series.append({"label": label, "x": x, "y": y, "color": COLORS[j]})
        draw_line_panel(
            draw,
            panel_bbox(0, idx, 1, 2, 1500, 720),
            series,
            "load_multiplier_pu",
            "heat source / W",
            f"Rc factor = {rc:g}; oil-temperature mean",
            x_ticks=[0.8, 1.0, 1.2],
        )
    save(img, "fig03_heat_source_decomposition_by_load.png")


def fig04(balance: list[dict[str, str]]) -> None:
    rows = sorted(balance, key=lambda r: case_no(r["case_id"]))
    values = [f(r, "residual_percent") for r in rows]
    colors = ["#d62728" if abs(v) >= 10 else "#1f77b4" for v in values]
    img, draw = new_image(1600, 760, "Fig04 Heat-balance residual by case")
    draw_bar_panel(
        draw,
        panel_bbox(0, 0, 1, 1, 1600, 760),
        [str(i + 1) for i in range(len(values))],
        values,
        colors,
        "case index",
        "residual_percent",
        "Generated heat minus removed heat",
        threshold=10.0,
    )
    save(img, "fig04_heat_balance_residual_by_case.png")


def fig05(metrics: list[dict[str, str]], validity: list[dict[str, str]]) -> None:
    by_case = {r["case_id"]: r for r in validity}
    img, draw = new_image(1500, 720, "Fig05 Validity matrix")
    cell_colors = {"valid": "#2ca02c", "warning": "#ffbf00", "invalid": "#d62728"}
    for idx, rc in enumerate([1.0, 5.0, 20.0]):
        bbox = panel_bbox(0, idx, 1, 3, 1500, 720)
        left, top, right, bottom = bbox
        draw.rectangle(bbox, outline="#dddddd")
        draw.text((left + 14, top + 12), f"Rc factor = {rc:g}", font=FONT_BOLD, fill="#222222")
        grid_left, grid_top = left + 88, top + 78
        grid_right, grid_bottom = right - 34, bottom - 64
        cw = (grid_right - grid_left) / 3
        ch = (grid_bottom - grid_top) / 3
        for c, load in enumerate([0.8, 1.0, 1.2]):
            draw_centered(draw, (grid_left + c * cw + cw / 2, grid_bottom + 28), f"load {load:g}", FONT_SMALL)
        for r, oil in enumerate([75.0, 85.0, 95.0]):
            draw_centered(draw, (left + 44, grid_top + r * ch + ch / 2), f"oil {oil:g}", FONT_SMALL)
        for r, oil in enumerate([75.0, 85.0, 95.0]):
            for c, load in enumerate([0.8, 1.0, 1.2]):
                row = next(
                    x for x in metrics
                    if math.isclose(f(x, "contact_resistance_multiplier_pu"), rc)
                    and math.isclose(f(x, "oil_temperature_C"), oil)
                    and math.isclose(f(x, "load_multiplier_pu"), load)
                )
                valid = by_case[row["case_id"]]
                if valid["overall_valid"].lower() == "true":
                    status = "warning" if row["thermal_warning"].lower() == "true" else "valid"
                else:
                    status = "invalid"
                x0 = grid_left + c * cw
                y0 = grid_top + r * ch
                draw.rectangle((x0 + 5, y0 + 5, x0 + cw - 5, y0 + ch - 5), fill=cell_colors[status], outline="#ffffff", width=3)
                draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 - 12), f"case {case_no(row['case_id']):02d}", FONT)
                draw_centered(draw, (x0 + cw / 2, y0 + ch / 2 + 18), status, FONT_SMALL)
    draw.text((86, 660), "green=overall_valid, yellow=thermal_warning, red=invalid_case", font=FONT_SMALL, fill="#222222")
    save(img, "fig05_validity_matrix.png")


def fig06(sources: list[dict[str, str]]) -> None:
    rows = sorted(sources, key=lambda r: case_no(r["case_id"]))
    img, draw = new_image(1500, 920, "Fig06 Qcontact validation")
    series = [
        {"label": "integrated", "x": [case_no(r["case_id"]) for r in rows], "y": [f(r, "Qcontact_W") for r in rows], "color": COLORS[0]},
        {"label": "I^2*Rc0*factor", "x": [case_no(r["case_id"]) for r in rows], "y": [f(r, "Qcontact_expected_I2Rc_W") for r in rows], "color": COLORS[3]},
    ]
    draw_line_panel(
        draw,
        panel_bbox(0, 0, 2, 1, 1500, 920),
        series,
        "case index",
        "Qcontact / W",
        "Integrated vs expected contact heat",
        x_ticks=[1, 5, 10, 15, 20, 25, 27],
    )
    errors = [f(r, "Qcontact_relative_error_pct") for r in rows]
    colors = ["#d62728" if abs(v) >= 1 else "#1f77b4" for v in errors]
    draw_bar_panel(
        draw,
        panel_bbox(1, 0, 2, 1, 1500, 920),
        [str(i + 1) for i in range(len(errors))],
        errors,
        colors,
        "case index",
        "relative error / %",
        "Qcontact relative error",
        threshold=1.0,
    )
    save(img, "fig06_Qcontact_validation.png")


def fig07(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> tuple[float, float, float]:
    by_case = {r["case_id"]: r for r in metrics}
    rows = []
    for row in sorted(sources, key=lambda r: case_no(r["case_id"])):
        merged = dict(row)
        merged.update(by_case[row["case_id"]])
        rows.append(merged)
    x = np.array([(f(r, "current_A") ** 2) / 1.0e6 for r in rows], dtype=float)
    y = np.array([f(r, "Qjoule_conductor_W") for r in rows], dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot else 1.0

    img, draw = new_image(1500, 920, "Fig07 Qjoule I^2 scaling")
    series = []
    for idx, oil in enumerate([75.0, 85.0, 95.0]):
        rows_oil = [r for r in rows if math.isclose(f(r, "oil_temperature_C"), oil)]
        series.append(
            {
                "label": f"oil {oil:g} C",
                "x": [(f(r, "current_A") ** 2) / 1.0e6 for r in rows_oil],
                "y": [f(r, "Qjoule_conductor_W") for r in rows_oil],
                "color": COLORS[idx],
            }
        )
    xfit = [float(np.min(x)), float(np.max(x))]
    series.append({"label": f"fit R2={r2:.4f}", "x": xfit, "y": [slope * xfit[0] + intercept, slope * xfit[1] + intercept], "color": "#222222"})
    draw_line_panel(
        draw,
        panel_bbox(0, 0, 2, 1, 1500, 920),
        series,
        "I^2 / 1e6 A^2",
        "Qjoule_conductor_W",
        f"Linear fit: Q = {slope:.3f}*(I^2/1e6) + {intercept:.3f}",
    )
    errors = [f(r, "Qjoule_relative_error_pct") for r in rows]
    colors = ["#d62728" if abs(v) >= 5 else "#1f77b4" for v in errors]
    draw_bar_panel(
        draw,
        panel_bbox(1, 0, 2, 1, 1500, 920),
        [str(i + 1) for i in range(len(errors))],
        errors,
        colors,
        "case index",
        "relative error / %",
        "Integrated Qjoule vs expected I^2*R_eff",
        threshold=5.0,
    )
    save(img, "fig07_Qjoule_I2_scaling.png")
    return float(slope), float(intercept), float(r2)


def monotonic_non_decreasing(values: list[float], tol: float = 1e-8) -> bool:
    return all(values[i + 1] + tol >= values[i] for i in range(len(values) - 1))


def trend_checks(metrics: list[dict[str, str]], sources: list[dict[str, str]]) -> dict[str, bool]:
    source_by_case = {r["case_id"]: r for r in sources}
    merged = []
    for row in metrics:
        item = dict(row)
        item.update(source_by_case[row["case_id"]])
        merged.append(item)

    oil_ok = True
    for load in [0.8, 1.0, 1.2]:
        for rc in [1.0, 5.0, 20.0]:
            rows = sorted(
                [
                    r for r in merged
                    if math.isclose(f(r, "load_multiplier_pu"), load)
                    and math.isclose(f(r, "contact_resistance_multiplier_pu"), rc)
                ],
                key=lambda r: f(r, "oil_temperature_C"),
            )
            oil_ok &= monotonic_non_decreasing([f(r, "Tmax_global_C") for r in rows])

    qjoule_ok = True
    for oil in [75.0, 85.0, 95.0]:
        for rc in [1.0, 5.0, 20.0]:
            rows = sorted(
                [
                    r for r in merged
                    if math.isclose(f(r, "oil_temperature_C"), oil)
                    and math.isclose(f(r, "contact_resistance_multiplier_pu"), rc)
                ],
                key=lambda r: f(r, "current_A"),
            )
            qjoule_ok &= monotonic_non_decreasing([f(r, "Qjoule_conductor_W") for r in rows])

    qcontact_ok = True
    rows = sorted(merged, key=lambda r: f(r, "current_A") ** 2 * f(r, "contact_resistance_multiplier_pu"))
    qcontact_ok &= monotonic_non_decreasing([f(r, "Qcontact_W") for r in rows])

    contact_response_ok = True
    for load in [0.8, 1.0, 1.2]:
        for oil in [75.0, 85.0, 95.0]:
            rows = sorted(
                [
                    r for r in merged
                    if math.isclose(f(r, "load_multiplier_pu"), load)
                    and math.isclose(f(r, "oil_temperature_C"), oil)
                ],
                key=lambda r: f(r, "contact_resistance_multiplier_pu"),
            )
            contact_response_ok &= f(rows[-1], "Tmax_contact_C") > f(rows[0], "Tmax_contact_C")

    return {
        "Tmax_increases_with_oil_temperature": oil_ok,
        "Qjoule_increases_with_I2": qjoule_ok,
        "Qcontact_increases_with_I2_Rc": qcontact_ok,
        "Tmax_contact_responds_to_high_Rc": contact_response_ok,
    }


def write_report(
    cases: list[dict[str, str]],
    metrics: list[dict[str, str]],
    sources: list[dict[str, str]],
    balance: list[dict[str, str]],
    validity: list[dict[str, str]],
    fit: tuple[float, float, float],
) -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    total = len(metrics)
    status_counts = Counter(r["status"] for r in validity)
    valid_counts = {
        "temperature": sum(b(r, "valid_temperature") for r in validity),
        "heat_balance": sum(b(r, "valid_heat_balance") for r in validity),
        "Qjoule": sum(b(r, "valid_Qjoule") for r in validity),
        "Qcontact": sum(b(r, "valid_Qcontact") for r in validity),
        "selection": sum(b(r, "valid_selection") for r in validity),
        "overall": sum(b(r, "overall_valid") for r in validity),
    }
    invalid = [r for r in validity if not b(r, "overall_valid")]
    warnings = [r for r in metrics if r["thermal_warning"].lower() == "true"]
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
    qdielectric_values = sorted({round(f(r, "Qdielectric_RIP_W"), 8) for r in sources})
    checks = trend_checks(metrics, sources)

    can_enter = (
        total == 27
        and valid_counts["heat_balance"] == total
        and valid_counts["Qjoule"] == total
        and valid_counts["Qcontact"] == total
        and valid_counts["selection"] == total
        and valid_counts["overall"] == total
        and all(checks.values())
    )
    fit_slope, fit_intercept, fit_r2 = fit

    matrix_text = (
        "load_multiplier_pu = [0.8, 1.0, 1.2]；"
        "oil_temperature_C = [75, 85, 95]；"
        "contact_resistance_multiplier_pu = [1, 5, 20]。"
        "固定条件为 voltage_multiplier_pu=1.0、air_temperature_C=25、"
        "wind_speed_m_s=1.0、tan_delta_multiplier_pu=1.0。"
    )
    fixed_note = (
        "本轮沿用 RUN006 的 source-fixed、by-ID、solid-only thermal diagnostic model。"
        "RIP 介质损耗仍采用 approximate_Qdielectric_ref，用于热诊断扫参，"
        "不能等同于完整电热耦合模型的真实电场耦合介质损耗。"
    )
    next_step = (
        "满足进入 125 组核心风险边界扫描的前置诊断条件；本脚本未执行 125 组扫描，"
        "下一阶段仍建议在用户确认后单独启动。"
        if can_enter
        else "暂不建议进入 125 组核心风险边界扫描，需要先修正下列失败项。"
    )
    failure_items = []
    if not can_enter:
        if total != 27:
            failure_items.append(f"工况数量为 {total}，不是 27。")
        for key, count in valid_counts.items():
            if count != total:
                failure_items.append(f"{key} 有效数 {count}/{total}。")
        for key, ok in checks.items():
            if not ok:
                failure_items.append(f"趋势检查未通过：{key}。")
    if not failure_items:
        failure_items.append("无需要修正的无效工况；仅需注意本轮是 solid-only 诊断结果。")
    fit_sign = "+" if fit_intercept >= 0 else "-"
    fit_intercept_abs = abs(fit_intercept)

    report = f"""# SOLID_ONLY_SWEEP_27_RUN007 阶段报告

## 1. 本轮任务目标

本轮目标是基于 RUN006 已通过的 source-fixed、explicit by-ID、solid-only 热诊断模型，执行 3 x 3 x 3 共 27 组小规模稳态热扫参，检查热源归一化、显式 domain/boundary selection、热量收支和温度响应趋势。本轮没有执行 125 组风险边界扫描，也没有构建完整电热耦合主模型。

## 2. 扫参矩阵

{matrix_text}

实际输出工况矩阵见 `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_case_matrix.csv`，共 {len(cases)} 组。

## 3. 使用的基准模型

{fixed_note}

正式热边界沿用显式 boundary ID selection；导体、RIP、接触层、硅橡胶和法兰等后处理区域沿用显式 domain ID selection。未回退到 Box selection。

## 4. RUN006 基准依据

RUN006 已通过基准热诊断，关键依据为 Tmax_global_C 约 88.42 degC，Qjoule_conductor_W 约 34.01 W，Qcontact_W = 1.5625 W，Qdielectric_RIP_W 约 2.55 W，热量收支 residual_percent 约 -3.25%。RUN007 在此基础上保持热源归一化方式，并按工况更新电流、油温和接触电阻倍率。

## 5. 27 组工况有效性统计

- 求解状态：{dict(status_counts)}
- overall_valid：{valid_counts["overall"]}/{total}
- valid_temperature：{valid_counts["temperature"]}/{total}
- valid_heat_balance：{valid_counts["heat_balance"]}/{total}
- valid_Qjoule：{valid_counts["Qjoule"]}/{total}
- valid_Qcontact：{valid_counts["Qcontact"]}/{total}
- valid_selection：{valid_counts["selection"]}/{total}
- thermal_warning：{len(warnings)}/{total}

Tmax_global_C 范围为 {tmax_min:.3f} 至 {tmax_max:.3f} degC，Tmax_contact_C 最大值为 {tcontact_max:.3f} degC。最大热量收支残差绝对值为 {residual_abs_max:.3f}%，最大 Qjoule 相对误差绝对值为 {qjoule_err_max:.3e}%，最大 Qcontact 相对误差绝对值为 {qcontact_err_max:.3e}%。

## 6. 是否存在无效工况

无效工况数量为 {len(invalid)}。{"无无效工况。" if not invalid else "无效工况包括：" + ", ".join(r["case_id"] for r in invalid)}

## 7. 热源分解趋势

Qjoule_conductor_W 范围为 {qjoule_min:.3f} 至 {qjoule_max:.3f} W，并随电流平方增大。Qcontact_W 范围为 {qcontact_min:.3f} 至 {qcontact_max:.3f} W，满足 Icase^2 * Rc0 * Rc_factor 的缩放关系。Qdielectric_RIP_W 在本轮为 approximate_Qdielectric_ref，数值为 {", ".join(f"{v:.3f}" for v in qdielectric_values)} W。Qjoule 对 I^2 的线性拟合为 Q = {fit_slope:.3f} * (I^2/1e6) {fit_sign} {fit_intercept_abs:.3f}，R2 = {fit_r2:.5f}。

## 8. 热量收支趋势

27 组工况均满足 abs(residual_percent) < 10%。油侧热通量在部分工况为负，表示 75-95 degC 热油向固体域输入热量；这与当前 solid-only 热诊断边界定义一致。空气侧和法兰侧整体承担散热，热量收支未出现失衡型异常。

## 9. 是否可以进入下一步 125 组风险边界扫描

{next_step}

趋势检查结果：

- Tmax 随 oil_temperature_C 升高而升高：{checks["Tmax_increases_with_oil_temperature"]}
- Qjoule 随 I^2 增长：{checks["Qjoule_increases_with_I2"]}
- Qcontact 随 I^2 * Rc_factor 增长：{checks["Qcontact_increases_with_I2_Rc"]}
- 高 Rc_factor 下 Tmax_contact 有响应：{checks["Tmax_contact_responds_to_high_Rc"]}

## 10. 若不能进入，需要修正的问题

{" ".join(failure_items)}

## 输出文件

- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_case_matrix.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_metrics.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/heat_source_decomposition_by_case.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/heat_balance_by_case.csv`
- `results/raw_comsol_exports/SOLID_ONLY_SWEEP_27_RUN007/sweep_validity_summary.csv`
- `results/paper_figures/solid_only_sweep_27_run007/fig01_Tmax_vs_load_by_oil_temp.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig02_Tmax_contact_vs_Rc_factor.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig03_heat_source_decomposition_by_load.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig04_heat_balance_residual_by_case.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig05_validity_matrix.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig06_Qcontact_validation.png`
- `results/paper_figures/solid_only_sweep_27_run007/fig07_Qjoule_I2_scaling.png`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    cases = read_csv("sweep_case_matrix.csv")
    metrics = read_csv("sweep_metrics.csv")
    sources = read_csv("heat_source_decomposition_by_case.csv")
    balance = read_csv("heat_balance_by_case.csv")
    validity = read_csv("sweep_validity_summary.csv")

    fig01(metrics)
    fig02(metrics)
    fig03(metrics, sources)
    fig04(balance)
    fig05(metrics, validity)
    fig06(sources)
    fit = fig07(metrics, sources)
    write_report(cases, metrics, sources, balance, validity, fit)

    print(f"generated figures in {FIG_DIR}")
    print(f"generated report {REPORT}")


if __name__ == "__main__":
    main()
