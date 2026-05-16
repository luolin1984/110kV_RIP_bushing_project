"""Generate current-stage diagnostic and review figures for BRFGL1.

These figures are for model review only. They intentionally avoid final
paper-style risk curves or parameter-sweep conclusions while the heat baseline
is still under diagnosis.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


PROJECT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT / "results" / "paper_figures" / "stage_diagnostics"
DOC_DIR = PROJECT / "docs"
REPORT = DOC_DIR / "stage_diagnostics_plot_report.md"


plt.rcParams.update(
    {
        "font.family": "Times New Roman",
        "font.size": 9,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.linewidth": 0.3,
        "grid.alpha": 0.35,
        "legend.frameon": False,
        "figure.dpi": 120,
        "savefig.dpi": 320,
    }
)


@dataclass(frozen=True)
class Domain:
    name: str
    r0: float
    r1: float
    z0: float
    z1: float
    color: str
    label: str
    alpha: float = 0.62


generated: list[str] = []
not_generated: list[str] = []
warnings: list[str] = []
inputs_used: list[str] = []


def warn(message: str) -> None:
    warnings.append(message)
    print("warning:", message)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        warn(f"missing input: {path.relative_to(PROJECT)}")
        return []
    inputs_used.append(str(path.relative_to(PROJECT)))
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def savefig(name: str) -> None:
    path = OUT_DIR / name
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    generated.append(str(path.relative_to(PROJECT)))


def add_rect(ax, d: Domain, edge: str = "black", lw: float = 0.45) -> None:
    ax.add_patch(
        Rectangle(
            (d.z0, d.r0),
            d.z1 - d.z0,
            d.r1 - d.r0,
            facecolor=d.color,
            edgecolor=edge,
            lw=lw,
            alpha=d.alpha,
        )
    )


def format_axes(ax, title: str, xlim=(-650, 1700), ylim=(0, 380)) -> None:
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Axial coordinate z / mm")
    ax.set_ylabel("Radial coordinate r / mm")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axvline(0, color="0.25", lw=0.7, ls="--")


def profile_rows(kind: str) -> list[dict[str, str]]:
    return read_csv(PROJECT / "data" / "processed" / "cad_extract" / f"brfgl1_cad_v2_{kind}_profile.csv")


def profile_xy(kind: str) -> tuple[list[float], list[float]]:
    rows = profile_rows(kind)
    z: list[float] = []
    r: list[float] = []
    for row in rows:
        z.append(float(row["z_start_mm"]))
        r.append(float(row["r_outer_mm"]))
    if rows:
        z.append(float(rows[-1]["z_end_mm"]))
        r.append(float(rows[-1]["r_outer_mm"]))
    return z, r


def base_domains(v2: bool = True) -> list[Domain]:
    domains = [
        Domain("inner_hollow", 0, 20, -595, 1650, "#f2f2f2", "inner hollow", 0.95),
        Domain("center_conductor", 20, 32, -595, 1650, "#bdbdbd", "center conductor", 0.86),
        Domain("contact_layer", 20, 32, 1150, 1190, "#ef3b2c", "contact resistance layer", 0.9),
        Domain("terminal", 32, 40, 1150, 1190, "#fdae6b", "terminal connector", 0.78),
        Domain("rip_core", 32, 66, -595, 1150, "#bcbddc", "RIP capacitor core", 0.62),
        Domain("silicone_trunk", 66, 82, 15, 1150, "#a1d99b", "silicone trunk", 0.70),
        Domain("flange_disk", 66, 200, -15, 15, "#737373", "grounded flange", 0.72),
        Domain("flange_neck", 66, 100, -100, 100, "#969696", "flange neck", 0.58),
    ]
    if not v2:
        domains += [
            Domain("v1_shed_envelope", 82, 135, 0, 1150, "#31a354", "V1 shed envelope", 0.26),
            Domain("v1_oil_shield_1", 45, 66, -595, -415, "#6baed6", "V1 oil shield", 0.55),
            Domain("v1_oil_shield_2", 52, 66, -415, -245, "#4292c6", "V1 oil shield", 0.50),
            Domain("v1_oil_shield_3", 58, 66, -245, -100, "#2171b5", "V1 oil shield", 0.45),
        ]
    return domains


def cad_domains(kind: str, name: str, color: str, label: str) -> list[Domain]:
    out: list[Domain] = []
    for row in profile_rows(kind):
        out.append(
            Domain(
                row["strip_id"],
                float(row["r_inner_mm"]),
                float(row["r_outer_mm"]),
                float(row["z_start_mm"]),
                float(row["z_end_mm"]),
                color,
                label,
                0.46,
            )
        )
    return out


def screen_domains() -> list[Domain]:
    rows = read_csv(PROJECT / "data" / "processed" / "condenser_screens.csv")
    out: list[Domain] = []
    for row in rows:
        sid = row.get("screen_id", "")
        if not sid.startswith("S"):
            continue
        r = float(row["radius_mm"])
        z0 = float(row["z_start_mm"])
        z1 = float(row["z_end_mm"])
        out.append(Domain(sid, r, r + 0.35, z0, z1, "#08519c", sid, 0.92))
    return out


def draw_dimensions(ax) -> None:
    ax.annotate("L = 2245 mm", xy=(527.5, 342), ha="center", fontsize=8)
    ax.annotate("", xy=(-595, 330), xytext=(1650, 330), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.annotate("L1 = 1150 mm", xy=(575, 292), ha="center", fontsize=8)
    ax.annotate("", xy=(0, 282), xytext=(1150, 282), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.annotate("L2 = 595 mm", xy=(-297.5, 88), ha="center", fontsize=8)
    ax.annotate("", xy=(-595, 78), xytext=(0, 78), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(1180, 136, "D2/2 = 135 mm", fontsize=8, va="center")
    ax.text(-560, 68, "D1/2 = 66 mm", fontsize=8, va="center")
    ax.text(-90, 205, "D/2 = 200 mm", fontsize=8, va="center")


def fig01() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    for d in base_domains(True):
        add_rect(ax, d)
    for d in cad_domains("air", "air", "#31a354", "CAD air profile") + cad_domains("oil", "oil", "#6baed6", "CAD oil profile"):
        add_rect(ax, d)
    # Drawing constraints as reference envelope.
    ax.plot([-595, 0, 0, 1150, 1150, 1650], [66, 66, 135, 135, 40, 40], color="#d62728", lw=1.6, label="drawing constraint envelope")
    ax.plot([-100, -100, 100, 100], [0, 200, 200, 0], color="#d62728", lw=1.2, ls="--", label="flange radius constraint")
    draw_dimensions(ax)
    format_axes(ax, "BRFGL1 drawing constraints vs COMSOL V2 geometry")
    ax.legend(loc="upper right")
    ax.text(-620, 360, "Reconstructed from geometry_axisym.csv and CAD profile CSVs", fontsize=8)
    savefig("fig01_geometry_drawing_vs_comsol_v2.png")


def fig02() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.2), sharey=True)
    for ax, v2, title in [(axes[0], False, "V1: fast equivalent model"), (axes[1], True, "V2: CAD-profile-driven model")]:
        for d in base_domains(v2):
            add_rect(ax, d)
        if v2:
            for d in cad_domains("air", "air", "#31a354", "CAD air profile") + cad_domains("oil", "oil", "#6baed6", "CAD oil profile"):
                add_rect(ax, d)
        for s in screen_domains():
            add_rect(ax, s, edge="#08306b")
        format_axes(ax, title, xlim=(-650, 1700), ylim=(0, 230))
        ax.text(20, 210, "solid domains only shown for review", fontsize=8)
    savefig("fig02_v1_v2_geometry_comparison.png")


def gap_status() -> str:
    rows = read_csv(PROJECT / "results" / "summary_tables" / "profile_gap_check.csv")
    if rows and all(row.get("status") == "PASS_NO_GAPS" for row in rows):
        return "PASS_NO_GAPS"
    if rows:
        return "GAPS_REVIEW_REQUIRED"
    return "DATA_UNAVAILABLE"


def fig03() -> None:
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    for kind, color in [("air", "#238b45"), ("oil", "#2171b5")]:
        z, r = profile_xy(kind)
        if z:
            ax.step(z, r, where="post", lw=1.3, color=color, label=f"{kind} CAD profile")
            ax.scatter([z[0], z[-1]], [r[0], r[-1]], s=20, color=color)
            ax.text(z[len(z)//2], max(r) + 4, f"{kind}: z={z[0]:.0f}..{z[-1]:.0f} mm, rmax={max(r):.1f} mm", color=color, fontsize=8)
    status = gap_status()
    ax.text(0.03, 0.92, status, transform=ax.transAxes, fontsize=12, color="#238b45" if status == "PASS_NO_GAPS" else "#d62728", weight="bold")
    ax.set_title("CAD profile continuity check")
    ax.set_xlabel("Axial coordinate z / mm")
    ax.set_ylabel("Outer radius r / mm")
    ax.legend()
    savefig("fig03_cad_profile_gap_check.png")


def fig04() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    domains = base_domains(True) + cad_domains("air", "air", "#31a354", "silicone sheds") + cad_domains("oil", "oil", "#6baed6", "oil-side shield") + screen_domains()
    for d in domains:
        add_rect(ax, d)
    labels = [
        ("Cu conductor", 820, 28), ("RIP core", 260, 52), ("Silicone", 600, 75),
        ("CAD sheds", 640, 125), ("Flange", -20, 170), ("Contact", 1195, 30),
        ("Oil-side shield selection", -420, 54), ("Screens", -240, 59),
    ]
    for text, z, r in labels:
        ax.text(z, r, text, fontsize=8, bbox=dict(facecolor="white", alpha=0.72, edgecolor="none", pad=1.5))
    format_axes(ax, "Domain partition and material assignment")
    ax.text(-620, 355, "Oil-side core/shield are review selections where noted, not duplicate solid domains.", fontsize=8)
    savefig("fig04_domain_material_assignment.png")


def fig05() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    for d in base_domains(True):
        add_rect(ax, d, edge="0.55")
    for d in cad_domains("air", "air", "#d9f0d3", "air profile") + cad_domains("oil", "oil", "#deebf7", "oil profile"):
        add_rect(ax, d, edge="0.75", lw=0.2)
    # Heat source regions.
    for d in [Domain("joule_lower", 20, 32, -595, 1149, "#fdae6b", "Cu Joule heat", 0.85),
              Domain("joule_upper", 20, 32, 1191, 1650, "#fdae6b", "Cu Joule heat", 0.85),
              Domain("contact", 20, 32, 1150, 1190, "#de2d26", "contact heat", 0.95),
              Domain("rip", 32, 66, -595, 1150, "#9e9ac8", "RIP dielectric heat", 0.55)]:
        add_rect(ax, d, edge="black", lw=0.7)
    # Convection boundaries from CAD profile.
    for kind, color, label in [("air", "#238b45", "air convection"), ("oil", "#08519c", "oil convection")]:
        z, r = profile_xy(kind)
        if z:
            ax.step(z, r, where="post", color=color, lw=2.0, label=label)
    format_axes(ax, "Heat sources and segmented convection boundaries")
    ax.legend(loc="upper right")
    ax.text(-620, 360, "Diagnostic focus: source placement and external heat-removal boundaries.", fontsize=8)
    savefig("fig05_heat_sources_and_convection_boundaries.png")


def fig06() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    for d in base_domains(True) + cad_domains("air", "air", "#d9f0d3", "profile"):
        add_rect(ax, d, edge="0.75", lw=0.25)
    screens = screen_domains()
    for s in screens:
        if s.name == "S00":
            col = "#d7301f"
        elif s.name == "S10":
            col = "#252525"
        else:
            col = "#2b8cbe"
        add_rect(ax, Domain(s.name, s.r0, s.r1 + 1.2, s.z0, s.z1, col, s.name, 0.95), edge=col, lw=1.0)
        ax.text(s.z1 + 8, s.r1 + 1, s.name, fontsize=7, va="center")
    ax.plot([-100, 100], [200, 200], color="#252525", lw=2.0, label="Ground: flange")
    ax.plot([], [], color="#d7301f", lw=2.0, label="Fixed potential: S00 = 72.75 kV RMS")
    ax.plot([], [], color="#252525", lw=2.0, label="Ground: S10 and flange")
    ax.plot([], [], color="#2b8cbe", lw=2.0, label="Floating potential: S01-S09")
    format_axes(ax, "Electric boundary and floating-screen setup")
    ax.legend(loc="upper right")
    savefig("fig06_electric_boundary_and_floating_screens.png")


def baseline_metrics() -> dict[str, str]:
    rows = read_csv(PROJECT / "results" / "raw_comsol_exports" / "STEADY_1250_LOAD_1p0_RUN002" / "baseline_metrics.csv")
    return rows[0] if rows else {}


def as_float(row: dict[str, str], key: str) -> float | None:
    try:
        v = row.get(key, "")
        return float(v) if v not in ("", None) else None
    except ValueError:
        return None


def fig07() -> None:
    row = baseline_metrics()
    labels = ["Emax_global", "Emax_RIP", "Emax_screen_probe"]
    keys = ["Emax_global_V_per_m", "Emax_RIP_V_per_m", "Emax_screen_end_probe_V_per_m"]
    vals = [(as_float(row, k) or 0) / 1e6 for k in keys]
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.bar(labels, vals, color=["#969696", "#756bb1", "#2b8cbe"], width=0.55)
    ax.set_ylabel("Electric field / (kV/mm)")
    ax.set_title("Baseline electric-field diagnostic summary")
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals + [1]) * 0.03, f"{v:.2f}", ha="center", fontsize=9)
    ax.text(0.03, 0.88, "Diagnostic values only; probe/mesh review still required.", transform=ax.transAxes, fontsize=8)
    savefig("fig07_baseline_electric_field_summary.png")


def fig08() -> None:
    row = baseline_metrics()
    status = row.get("status", "missing")
    tmax = as_float(row, "Tmax_global_C")
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 0.18), 0.90, 0.68, transform=ax.transAxes, facecolor="#f7f7f7", edgecolor="0.3", lw=1.0))
    ax.text(0.10, 0.78, "RUN002 baseline temperature summary", transform=ax.transAxes, fontsize=14, weight="bold")
    ax.text(0.10, 0.62, f"current baseline_metrics.csv status: {status}", transform=ax.transAxes, fontsize=11)
    ax.text(0.10, 0.50, f"Tmax_global_C: {tmax:.3f} °C" if tmax is not None else "Tmax_global_C: unavailable", transform=ax.transAxes, fontsize=11)
    ax.text(0.10, 0.36, "Previous 674.88 °C invalid premise is superseded by current RUN002 files.", transform=ax.transAxes, fontsize=10, color="#b2182b")
    ax.text(0.10, 0.26, "Do not use this as final paper result; RUN004 and heat-balance checks remain unresolved.", transform=ax.transAxes, fontsize=9)
    savefig("fig08_run002_invalid_temperature_summary.png")


def diagnostic_rows() -> list[dict[str, str]]:
    return read_csv(PROJECT / "results" / "raw_comsol_exports" / "PHYSICS_DIAGNOSTICS_RUN003" / "diagnostic_results.csv")


def fig09() -> None:
    rows = diagnostic_rows()
    want = ["HT_FULL", "HT_NO_DIELECTRIC", "HT_CONSTANT_CU", "CPL_FULL", "CPL_NO_DIELECTRIC", "CPL_CONSTANT_CU"]
    data = [(r["case_id"], float(r["Tmax_global_C"])) for r in rows if r.get("case_id") in want and r.get("Tmax_global_C")]
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    labels, vals = zip(*data) if data else ([], [])
    ax.bar(range(len(vals)), vals, color="#9ecae1")
    ax.axhline(150, color="#d7301f", lw=1.2, ls="--", label="RUN004 acceptance reference 150 °C")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Tmax_global / °C")
    ax.set_title("RUN003 thermal diagnostic Tmax comparison")
    ax.text(0.02, 0.92, "Dielectric-loss off: little change; constant Cu loss: lower but still high.", transform=ax.transAxes, fontsize=8)
    ax.legend()
    savefig("fig09_physics_diagnostics_tmax_bar.png")


def fig10() -> None:
    rows = diagnostic_rows()
    want = ["ES_FULL", "ES_NO_FLOATING", "CPL_FULL", "CPL_NO_FLOATING"]
    data = [(r["case_id"], float(r["Emax_global_V_per_m"]) / 1e6) for r in rows if r.get("case_id") in want and r.get("Emax_global_V_per_m")]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    labels, vals = zip(*data) if data else ([], [])
    ax.bar(range(len(vals)), vals, color=["#969696", "#2b8cbe", "#969696", "#2b8cbe"][: len(vals)])
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Emax_global / (kV/mm)")
    ax.set_title("RUN003 electric-field diagnostic Emax comparison")
    ax.text(0.03, 0.90, "Floating-screen toggle changes Emax; values remain diagnostic.", transform=ax.transAxes, fontsize=8)
    savefig("fig10_physics_diagnostics_emax_bar.png")


def placeholder(name: str, title: str, lines: Iterable[str]) -> None:
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 0.12), 0.90, 0.76, transform=ax.transAxes, facecolor="#f7f7f7", edgecolor="0.35", lw=1.0))
    ax.text(0.10, 0.78, title, transform=ax.transAxes, fontsize=13, weight="bold")
    y = 0.62
    for line in lines:
        ax.text(0.10, y, line, transform=ax.transAxes, fontsize=10)
        y -= 0.12
    savefig(name)


def fig11() -> None:
    row = baseline_metrics()
    qcontact = as_float(row, "Qcontact_W")
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    labels = ["Qjoule", "Qcontact", "Qdielectric", "Qtotal"]
    vals = [math.nan, qcontact if qcontact is not None else math.nan, math.nan, math.nan]
    x = range(len(labels))
    ax.bar(x, [0 if math.isnan(v) else v for v in vals], color="#bdbdbd")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Power / W")
    ax.set_title("Heat-source decomposition status")
    for i, v in enumerate(vals):
        ax.text(i, 0.05 if math.isnan(v) else v + 0.05, "data unavailable" if math.isnan(v) else f"{v:.3g}", ha="center", fontsize=8, rotation=0)
    ax.text(0.03, 0.88, "Full heat-balance export is not available because RUN004 did not converge.", transform=ax.transAxes, fontsize=8)
    savefig("fig11_heat_source_decomposition.png")


def fig12() -> None:
    placeholder(
        "fig12_heat_balance_summary.png",
        "Heat-balance summary",
        [
            "Data unavailable: RUN004 did not reach a valid coupled solution.",
            "Required: Qjoule_total, Qcontact_total, Qdielectric_total.",
            "Required: heat_removed_air, heat_removed_oil, residual.",
            "Do not infer heat balance from incomplete runs.",
        ],
    )


def fig13() -> None:
    rows = read_csv(PROJECT / "results" / "summary_tables" / "domain_selection_integrity_check.csv")
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    domains = []
    for row in rows:
        try:
            domains.append(
                Domain(
                    row["selection_name"],
                    float(row["r_min_mm"]),
                    float(row["r_max_mm"]),
                    float(row["z_min_mm"]),
                    float(row["z_max_mm"]),
                    "#9ecae1" if "conductor" in row["selection_name"] else "#bcbddc" if "rip" in row["selection_name"] else "#fb6a4a" if "contact" in row["selection_name"] else "#bdbdbd",
                    row["selection_name"],
                    0.65,
                )
            )
        except Exception:
            continue
    for d in domains:
        add_rect(ax, d)
        ax.text((d.z0 + d.z1) / 2, (d.r0 + d.r1) / 2, d.name.replace("v2_", "").replace("_", "\n"), ha="center", va="center", fontsize=6)
    format_axes(ax, "Selection integrity check for Tmax postprocessing", xlim=(-650, 1700), ylim=(0, 220))
    ax.text(-620, 205, "Strict selections added to avoid identical conductor/RIP/contact Tmax caused by broad boxes.", fontsize=8)
    savefig("fig13_selection_integrity_check.png")


def write_report() -> None:
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage Diagnostics Plot Report",
        "",
        "Date: 2026-05-16",
        "",
        "## Goal",
        "",
        "This plotting pass generates current-stage review figures for geometry correctness, CAD-profile continuity, domain/material assignment, electric-boundary setup, and thermal anomaly diagnosis. These are not final SCI result figures.",
        "",
        "## Inputs Used",
        "",
    ]
    for item in sorted(set(inputs_used)):
        lines.append(f"- `{item}`")
    if not inputs_used:
        lines.append("- No input files were successfully read.")
    lines += ["", "## Generated Figures", ""]
    descriptions = {
        "fig01": "drawing constraints versus COMSOL V2 reconstructed geometry",
        "fig02": "V1 equivalent model versus V2 CAD-driven model",
        "fig03": "air/oil CAD profile continuity and gap status",
        "fig04": "domain partition and material-assignment review",
        "fig05": "heat-source regions and external convection boundaries",
        "fig06": "S00/S10/floating screen electric-boundary setup",
        "fig07": "baseline electric-field diagnostic values from RUN002 CSV",
        "fig08": "RUN002 temperature status summary using current files",
        "fig09": "RUN003 thermal diagnostic Tmax comparison",
        "fig10": "RUN003 electric-field diagnostic Emax comparison",
        "fig11": "heat-source decomposition availability check",
        "fig12": "heat-balance data availability placeholder",
        "fig13": "selection integrity review for Tmax postprocessing",
    }
    for item in generated:
        key = Path(item).name[:5]
        lines.append(f"- `{item}`: {descriptions.get(key, 'stage diagnostic figure')}.")
    if not_generated:
        lines += ["", "## Not Generated", ""]
        for item in not_generated:
            lines.append(f"- {item}")
    if warnings:
        lines += ["", "## Warnings", ""]
        for item in warnings:
            lines.append(f"- {item}")
    lines += [
        "",
        "## Current Model Issues",
        "",
        "- RUN002 in the current CSV is no longer the old 674.88 degC invalid result; it is recorded as `SOLVED` with `Tmax_global_C = 211.226442 degC`. It is still a diagnostic baseline rather than a final paper target.",
        "- RUN003 shows that disabling RIP dielectric loss barely changes Tmax, while constant copper loss lowers Tmax but remains high. The dominant problem is therefore more likely in heat boundary treatment, conductor-loss normalization, selection integrity, or thermal path setup than in dielectric loss alone.",
        "- RUN004 implemented solid-domain heat transfer and CAD segmented convection, but did not converge to a valid coupled solution. No RUN004 values should be backfilled into validation targets.",
        "- Heat-source decomposition and heat-balance figures remain incomplete because a valid converged RUN004 heat-balance export is not yet available.",
        "",
        "## Can the project enter a 27-case small sweep?",
        "",
        "No. The project should not enter the 27-case parameter sweep yet. The next COMSOL correction should build a solver-oriented solid-only component from the CAD solid preview, keep surrounding air/oil out of the thermal mesh, and rerun the heat-balance diagnostics until `Tmax`, heat-source totals, and convection removal are physically consistent.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    generated.append(str(REPORT.relative_to(PROJECT)))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    for fn in [fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08, fig09, fig10, fig11, fig12, fig13]:
        try:
            fn()
        except Exception as exc:
            name = fn.__name__
            not_generated.append(f"{name}: {exc}")
            warn(f"{name} failed: {exc}")
    write_report()
    print("\nStage diagnostics summary")
    print("generated:")
    for item in generated:
        print(" -", item)
    if not_generated:
        print("not generated:")
        for item in not_generated:
            print(" -", item)
    if warnings:
        print("warnings:")
        for item in warnings:
            print(" -", item)
    print("next: do not start parameter sweep until RUN004 heat balance is valid.")


if __name__ == "__main__":
    main()
