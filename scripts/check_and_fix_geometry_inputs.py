"""Check/fix CAD profile continuity and geometry overlap assumptions."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
CAD_DIR = PROJECT / "data" / "processed" / "cad_extract"
SUMMARY_DIR = PROJECT / "results" / "summary_tables"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fix_profile(filename: str, prefix: str, z_min: float, z_max: float) -> list[dict[str, str]]:
    path = CAD_DIR / filename
    rows = read_rows(path)
    original = rows[:]
    rows.sort(key=lambda r: float(r["z_start_mm"]))
    fixed: list[dict[str, str]] = []
    report: list[dict[str, str]] = []
    cursor = z_min
    filler_idx = 0
    tol = 1e-3
    for row in rows:
        z0 = float(row["z_start_mm"])
        z1 = float(row["z_end_mm"])
        if z0 > cursor + tol:
            filler = row.copy()
            filler["strip_id"] = f"{prefix}_fill_{filler_idx:03d}"
            filler["z_start_mm"] = f"{cursor:.3f}"
            filler["z_end_mm"] = f"{z0:.3f}"
            filler["r_inner_mm"] = row["r_inner_mm"]
            filler["r_outer_mm"] = row["r_inner_mm"]
            filler["cad_x_start"] = ""
            filler["cad_x_end"] = ""
            filler["cad_y_envelope"] = ""
            filler["source"] = f"auto-filled zero-thickness profile continuity row for {filename}"
            fixed.append(filler)
            report.append(
                {
                    "profile": filename,
                    "gap_start_mm": f"{cursor:.3f}",
                    "gap_end_mm": f"{z0:.3f}",
                    "gap_width_mm": f"{z0 - cursor:.3f}",
                    "action": "filled_with_zero_thickness_continuity_row",
                    "status": "FIXED",
                }
            )
            filler_idx += 1
        fixed.append(row)
        cursor = max(cursor, z1)
    if cursor < z_max - tol:
        row = rows[-1].copy()
        row["strip_id"] = f"{prefix}_fill_{filler_idx:03d}"
        row["z_start_mm"] = f"{cursor:.3f}"
        row["z_end_mm"] = f"{z_max:.3f}"
        row["r_outer_mm"] = row["r_inner_mm"]
        row["cad_x_start"] = ""
        row["cad_x_end"] = ""
        row["cad_y_envelope"] = ""
        row["source"] = f"auto-filled zero-thickness profile continuity row for {filename}"
        fixed.append(row)
        report.append(
            {
                "profile": filename,
                "gap_start_mm": f"{cursor:.3f}",
                "gap_end_mm": f"{z_max:.3f}",
                "gap_width_mm": f"{z_max - cursor:.3f}",
                "action": "filled_with_zero_thickness_continuity_row",
                "status": "FIXED",
            }
        )

    if fixed != original:
        backup = path.with_suffix(path.suffix + ".bak_before_gap_fill")
        if not backup.exists():
            write_rows(backup, original)
        write_rows(path, fixed)
    if not report:
        report.append(
            {
                "profile": filename,
                "gap_start_mm": "",
                "gap_end_mm": "",
                "gap_width_mm": "0",
                "action": "none",
                "status": "PASS_NO_GAPS",
            }
        )
    return report


def rect_overlap(a, b) -> float:
    r = max(0.0, min(a["r1"], b["r1"]) - max(a["r0"], b["r0"]))
    z = max(0.0, min(a["z1"], b["z1"]) - max(a["z0"], b["z0"]))
    return r * z


def geometry_overlap_report() -> list[dict[str, str]]:
    # Planned solid entity extents after removing duplicate oil_side_core and
    # representing oil-side shield/core as selections on RIP instead of entities.
    rects = [
        {"name": "rip_capacitor_core", "r0": 32, "r1": 66, "z0": -595, "z1": 1150, "material": "RIP"},
        {"name": "silicone_housing", "r0": 66, "r1": 82, "z0": 100, "z1": 1150, "material": "silicone"},
        {"name": "flange_disk", "r0": 66, "r1": 200, "z0": -15, "z1": 15, "material": "metal"},
        {"name": "flange_neck", "r0": 66, "r1": 100, "z0": -100, "z1": 100, "material": "metal"},
        {"name": "center_conductor_main", "r0": 20, "r1": 32, "z0": -595, "z1": 1150, "material": "copper"},
        {"name": "contact_resistance_heat_source_layer", "r0": 20, "r1": 32, "z0": 1150, "z1": 1190, "material": "copper_contact"},
        {"name": "center_conductor_upper", "r0": 20, "r1": 32, "z0": 1190, "z1": 1650, "material": "copper"},
        {"name": "inner_hollow", "r0": 0, "r1": 20, "z0": -595, "z1": 1650, "material": "void"},
        {"name": "terminal", "r0": 32, "r1": 40, "z0": 1150, "z1": 1190, "material": "metal"},
    ]
    allowed_touch_or_embedded = {
        tuple(sorted(("flange_disk", "flange_neck"))): "same grounded flange part",
        tuple(sorted(("terminal", "contact_resistance_heat_source_layer"))): "shared contact-height interval but adjacent radial regions",
    }
    out: list[dict[str, str]] = []
    for i, a in enumerate(rects):
        for b in rects[i + 1 :]:
            area = rect_overlap(a, b)
            key = tuple(sorted((a["name"], b["name"])))
            if area > 1e-9:
                allowed = key in allowed_touch_or_embedded
                out.append(
                    {
                        "entity_a": a["name"],
                        "entity_b": b["name"],
                        "overlap_area_mm2": f"{area:.6f}",
                        "status": "ALLOWED" if allowed else "REVIEW",
                        "note": allowed_touch_or_embedded.get(key, "potential duplicate entity; avoid assigning conflicting materials"),
                    }
                )
    checked = {
        ("rip_capacitor_core", "oil_side_core_selection"),
        ("rip_capacitor_core", "oil_side_shield_selection"),
    }
    for a, b in checked:
        out.append(
            {
                "entity_a": a,
                "entity_b": b,
                "overlap_area_mm2": "0",
                "status": "PASS_SELECTION_ONLY",
                "note": f"{b} is a selection on RIP, not a duplicate geometry entity",
            }
        )
    return out


def main() -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    reports = []
    reports.extend(fix_profile("brfgl1_cad_v2_air_profile.csv", "air", 0.0, 1150.0))
    reports.extend(fix_profile("brfgl1_cad_v2_oil_profile.csv", "oil", -595.0, 0.0))
    with (SUMMARY_DIR / "profile_gap_check.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["profile", "gap_start_mm", "gap_end_mm", "gap_width_mm", "action", "status"])
        writer.writeheader()
        writer.writerows(reports)

    overlap = geometry_overlap_report()
    with (SUMMARY_DIR / "geometry_overlap_check.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["entity_a", "entity_b", "overlap_area_mm2", "status", "note"])
        writer.writeheader()
        writer.writerows(overlap)

    print(SUMMARY_DIR / "profile_gap_check.csv")
    print(SUMMARY_DIR / "geometry_overlap_check.csv")


if __name__ == "__main__":
    main()
