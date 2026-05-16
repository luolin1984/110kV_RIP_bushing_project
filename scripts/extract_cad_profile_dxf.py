"""Extract CAD-driven BRFGL1 V2 profile strips from Drawing1.dxf.

The manufacturer drawing is a schematic CAD view rather than a dimensionally
uniform r-z model. This script uses the DXF as the shape source and rescales the
oil side and air side separately to the public BRFGL1 drawing dimensions:

- oil side: z = -595..0 mm
- air external insulation: z = 0..1150 mm
- oil-side core radius limit: 66 mm
- air-side external insulation max radius: 135 mm

The output CSV files are consumed by comsol/build_geometry_brfgl1.java for the
CAD-driven V2 geometry.
"""

from __future__ import annotations

import csv
import math
import shutil
from pathlib import Path

import ezdxf
import matplotlib.pyplot as plt


PROJECT = Path(__file__).resolve().parents[1]
SRC_DXF = Path("/Users/luolin/Downloads/Drawing1.dxf")
RAW_CAD_DIR = PROJECT / "data" / "raw_sources" / "manufacturer_catalogs" / "cad"
OUT_DIR = PROJECT / "data" / "processed" / "cad_extract"


DXF_CENTER_Y = 2067.066709336857
DXF_AIR_START_X = 2164.021012376361
DXF_AIR_END_X = 2228.022534798311
DXF_OIL_START_X = 2052.021012376361
DXF_OIL_END_X = 2161.021012376361


def sample_line(x0: float, y0: float, x1: float, y1: float, step: float = 0.08) -> list[tuple[float, float]]:
    length = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(length / step))
    return [(x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * i / (n - 1)) for i in range(n)]


def collect_outline_points(doc: ezdxf.EzDxf) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    msp = doc.modelspace()
    for entity in msp:
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            # Discard the dimension leader above the real bushing outline.
            if max(start.y, end.y) > 2081.0:
                continue
            points.extend(sample_line(start.x, start.y, end.x, end.y))
        elif entity.dxftype() == "ARC":
            center = entity.dxf.center
            radius = entity.dxf.radius
            start = math.radians(entity.dxf.start_angle)
            end = math.radians(entity.dxf.end_angle)
            if end < start:
                end += 2 * math.pi
            for i in range(32):
                a = start + (end - start) * i / 31
                x = center.x + radius * math.cos(a)
                y = center.y + radius * math.sin(a)
                if y <= 2081.0:
                    points.append((x, y))
    return points


def upper_envelope(points: list[tuple[float, float]], x0: float, x1: float, bins: int) -> list[tuple[float, float, float]]:
    dx = (x1 - x0) / bins
    strips: list[tuple[float, float, float]] = []
    for i in range(bins):
        a = x0 + i * dx
        b = x0 + (i + 1) * dx
        ys = [y for x, y in points if a <= x < b and y >= DXF_CENTER_Y]
        if not ys:
            continue
        strips.append((a, b, max(ys)))
    return strips


def write_profile(path: Path, rows: list[dict[str, float | str]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "strip_id",
                "z_start_mm",
                "z_end_mm",
                "r_inner_mm",
                "r_outer_mm",
                "cad_x_start",
                "cad_x_end",
                "cad_y_envelope",
                "source",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_profiles(points: list[tuple[float, float]]) -> tuple[list[dict[str, float | str]], list[dict[str, float | str]]]:
    air_rows: list[dict[str, float | str]] = []
    for idx, (x0, x1, y) in enumerate(upper_envelope(points, DXF_AIR_START_X, DXF_AIR_END_X, 72)):
        z0 = (x0 - DXF_AIR_START_X) / (DXF_AIR_END_X - DXF_AIR_START_X) * 1150.0
        z1 = (x1 - DXF_AIR_START_X) / (DXF_AIR_END_X - DXF_AIR_START_X) * 1150.0
        # In the CAD view, y-center to shed tip is about 10 drawing units.
        # Scale that to 135 mm and clamp the trunk lower bound to 82 mm.
        r = max(82.0, min(135.0, (y - DXF_CENTER_Y) * 13.5))
        if r <= 82.2:
            continue
        air_rows.append(
            {
                "strip_id": f"air_{idx:03d}",
                "z_start_mm": round(z0, 3),
                "z_end_mm": round(z1, 3),
                "r_inner_mm": 82.0,
                "r_outer_mm": round(r, 3),
                "cad_x_start": round(x0, 6),
                "cad_x_end": round(x1, 6),
                "cad_y_envelope": round(y, 6),
                "source": "Drawing1.dxf upper envelope rescaled to L1=1150 mm and D2/2=135 mm",
            }
        )

    oil_rows: list[dict[str, float | str]] = []
    for idx, (x0, x1, y) in enumerate(upper_envelope(points, DXF_OIL_START_X, DXF_OIL_END_X, 36)):
        z0 = -595.0 + (x0 - DXF_OIL_START_X) / (DXF_OIL_END_X - DXF_OIL_START_X) * 595.0
        z1 = -595.0 + (x1 - DXF_OIL_START_X) / (DXF_OIL_END_X - DXF_OIL_START_X) * 595.0
        # Scale y-center to the known oil-side core radius. Negative/terminal
        # detail is ignored; the conductive tube and hollow are modeled separately.
        r = max(32.0, min(66.0, (y - DXF_CENTER_Y) * 13.2))
        if r <= 32.2:
            continue
        oil_rows.append(
            {
                "strip_id": f"oil_{idx:03d}",
                "z_start_mm": round(z0, 3),
                "z_end_mm": round(z1, 3),
                "r_inner_mm": 32.0,
                "r_outer_mm": round(r, 3),
                "cad_x_start": round(x0, 6),
                "cad_x_end": round(x1, 6),
                "cad_y_envelope": round(y, 6),
                "source": "Drawing1.dxf upper envelope rescaled to L2=595 mm and D1/2=66 mm",
            }
        )
    return air_rows, oil_rows


def plot_profiles(points: list[tuple[float, float]], air_rows, oil_rows) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), dpi=220)
    xs, ys = zip(*points)
    axes[0].scatter(xs, ys, s=0.5, color="#252525")
    axes[0].axhline(DXF_CENTER_Y, color="#d62728", lw=0.8)
    axes[0].axvline(DXF_AIR_START_X, color="#2ca02c", lw=0.8)
    axes[0].axvline(DXF_AIR_END_X, color="#2ca02c", lw=0.8)
    axes[0].axvline(DXF_OIL_START_X, color="#1f77b4", lw=0.8)
    axes[0].axvline(DXF_OIL_END_X, color="#1f77b4", lw=0.8)
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].set_title("DXF sampled outline points and calibration landmarks")
    axes[0].grid(True, lw=0.25)

    for row in oil_rows:
        axes[1].fill_between(
            [row["z_start_mm"], row["z_end_mm"]],
            [row["r_inner_mm"], row["r_inner_mm"]],
            [row["r_outer_mm"], row["r_outer_mm"]],
            color="#6baed6",
            alpha=0.35,
        )
    for row in air_rows:
        axes[1].fill_between(
            [row["z_start_mm"], row["z_end_mm"]],
            [row["r_inner_mm"], row["r_inner_mm"]],
            [row["r_outer_mm"], row["r_outer_mm"]],
            color="#31a354",
            alpha=0.35,
        )
    axes[1].set_xlim(-620, 1180)
    axes[1].set_ylim(0, 145)
    axes[1].set_aspect("equal", adjustable="box")
    axes[1].set_xlabel("z axial coordinate (mm)")
    axes[1].set_ylabel("r radial coordinate (mm)")
    axes[1].set_title("CAD-driven V2 profile strips after BRFGL1 dimension calibration")
    axes[1].grid(True, lw=0.25)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "Drawing1_cad_profile_extraction_check.png")
    plt.close(fig)


def main() -> None:
    RAW_CAD_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_DXF, RAW_CAD_DIR / "BRFGL1-126-1250-4_Drawing1.dxf")

    doc = ezdxf.readfile(SRC_DXF)
    points = collect_outline_points(doc)
    air_rows, oil_rows = build_profiles(points)
    write_profile(OUT_DIR / "brfgl1_cad_v2_air_profile.csv", air_rows)
    write_profile(OUT_DIR / "brfgl1_cad_v2_oil_profile.csv", oil_rows)
    plot_profiles(points, air_rows, oil_rows)

    print(OUT_DIR / "brfgl1_cad_v2_air_profile.csv")
    print(OUT_DIR / "brfgl1_cad_v2_oil_profile.csv")
    print(OUT_DIR / "Drawing1_cad_profile_extraction_check.png")


if __name__ == "__main__":
    main()
