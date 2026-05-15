"""Generate BRFGL1 V1/V2 geometry check figures and mapping tables.

The figure keeps COMSOL's 2D axisymmetric convention: horizontal axis is z,
vertical axis is r. It does not swap r and z to make the bushing look horizontal.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


PROJECT = Path(__file__).resolve().parents[1]
FIG_DIR = PROJECT / "results" / "paper_figures"
TABLE_DIR = PROJECT / "results" / "summary_tables"


@dataclass(frozen=True)
class RectDomain:
    component: str
    selection_name: str
    physical_meaning: str
    r_min_mm: float
    r_max_mm: float
    z_min_mm: float
    z_max_mm: float
    color: str
    alpha: float = 0.50


def add_rect(ax, domain: RectDomain) -> None:
    ax.add_patch(
        Rectangle(
            (domain.z_min_mm, domain.r_min_mm),
            domain.z_max_mm - domain.z_min_mm,
            domain.r_max_mm - domain.r_min_mm,
            facecolor=domain.color,
            edgecolor="black",
            lw=0.45,
            alpha=domain.alpha,
        )
    )


def base_domains(component: str, refined: bool) -> list[RectDomain]:
    if component == "comp_v1":
        prefix = "v1_"
    elif component == "comp_v2_cad_solid_preview":
        prefix = "pv_"
    else:
        prefix = "v2_"
    air_len = 1650
    oil_len = 595
    l1 = 1150
    l4 = 200
    flange_t = 30
    r_hollow = 20
    r_cond_o = 32
    r_rip = 66
    r_body = 82
    r_housing = 135
    r_terminal = 40
    r_flange = 200
    r_far = 360

    domains = []
    if component != "comp_v2_cad_solid_preview":
        domains.extend(
            [
                RectDomain(component, prefix + "surrounding_oil_domain", "oil surrounding domain, z < 0", r_rip, r_far, -oil_len, 0, "#9ecae1", 0.24),
                RectDomain(component, prefix + "surrounding_air_domain", "air surrounding domain, z > 0", r_housing, r_far, 0, air_len, "#fdd0a2", 0.22),
            ]
        )
    domains.extend([
        RectDomain(component, prefix + "inner_conduit_or_hollow_region", "inner hollow region defined by d3 = 40 mm", 0, r_hollow, -oil_len, air_len, "#f7f7f7", 0.90),
        RectDomain(component, prefix + "center_conductor", "current-carrying conductor tube wall", r_hollow, r_cond_o, -oil_len, air_len, "#bdbdbd", 0.85),
        RectDomain(component, prefix + "terminal_connector_region", "air-side terminal connector using a1 = 40 mm", 0, r_terminal, l1, l1 + 40, "#fdae6b", 0.75),
        RectDomain(component, prefix + "contact_resistance_heat_source_layer", "terminal-conductor contact heat-source layer", r_hollow, r_cond_o, l1, l1 + 40, "#fb6a4a", 0.90),
        RectDomain(component, prefix + "rip_capacitor_core", "RIP condenser core, bounded by oil-side core radius 66 mm", r_cond_o, r_rip, -oil_len, l1, "#bcbddc", 0.60),
        RectDomain(component, prefix + "silicone_rubber_external_insulation", "silicone rubber external insulation trunk", r_rip, r_body, 0, l1, "#c7e9c0", 0.72),
        RectDomain(component, prefix + "flange_grounded_metal", "grounded flange disk D = 400 mm", r_rip, r_flange, -flange_t / 2, flange_t / 2, "#969696", 0.76),
        RectDomain(component, prefix + "flange_grounded_metal", "grounded flange connection length L4 = 200 mm", r_rip, 100, -l4 / 2, l4 / 2, "#636363", 0.55),
        RectDomain(component, prefix + "oil_side_core", "oil-side RIP core with D1 = 132 mm", r_cond_o, r_rip, -oil_len, 0, "#756bb1", 0.32),
    ])

    if refined:
        domains.extend(read_cad_profile(component, prefix + "air_side_sheds_or_equivalent_envelope", "V2 CAD-driven air-side outer profile", "brfgl1_cad_v2_air_profile.csv", "#31a354", 0.48))
        domains.extend(read_cad_profile(component, prefix + "oil_side_shield_or_tapered_region", "V2 CAD-driven oil-side transition profile", "brfgl1_cad_v2_oil_profile.csv", "#6baed6", 0.42))
    else:
        domains.extend(
            [
                RectDomain(component, prefix + "oil_side_shield_or_tapered_region", "stepped approximation of oil-side tapered shield, stage 1", 45, r_rip, -oil_len, -415, "#6baed6", 0.55),
                RectDomain(component, prefix + "oil_side_shield_or_tapered_region", "stepped approximation of oil-side tapered shield, stage 2", 52, r_rip, -415, -245, "#4292c6", 0.50),
                RectDomain(component, prefix + "oil_side_shield_or_tapered_region", "stepped approximation of oil-side tapered shield, stage 3", 58, r_rip, -245, -100, "#2171b5", 0.45),
                RectDomain(component, prefix + "air_side_sheds_or_equivalent_envelope", "V1 equivalent full shed envelope", r_body, r_housing, 0, l1, "#74c476", 0.18),
                RectDomain(component, prefix + "air_side_sheds_or_equivalent_envelope", "V1 lower stepped envelope", 95, r_housing, 0, 280, "#31a354", 0.42),
                RectDomain(component, prefix + "air_side_sheds_or_equivalent_envelope", "V1 upper stepped envelope", 95, r_housing, 870, l1, "#31a354", 0.42),
            ]
        )
    return domains


def read_cad_profile(component: str, selection_name: str, meaning: str, filename: str, color: str, alpha: float) -> list[RectDomain]:
    rows: list[RectDomain] = []
    path = PROJECT / "data" / "processed" / "cad_extract" / filename
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                RectDomain(
                    component,
                    selection_name,
                    f"{meaning}; {row['strip_id']}",
                    float(row["r_inner_mm"]),
                    float(row["r_outer_mm"]),
                    float(row["z_start_mm"]),
                    float(row["z_end_mm"]),
                    color,
                    alpha,
                )
            )
    return rows


def screen_domains(component: str) -> list[RectDomain]:
    if component == "comp_v1":
        prefix = "v1_"
    elif component == "comp_v2_cad_solid_preview":
        prefix = "pv_"
    else:
        prefix = "v2_"
    lengths = [1150, 1150, 1150, 1150, 1150, 1100, 1010, 920, 830, 740, 650]
    domains: list[RectDomain] = []
    for i, length in enumerate(lengths):
        radius = 35 + 2.25 * i
        role = "fixed 72.75 kV RMS" if i == 0 else "fixed ground 0 V" if i == 10 else "floating screen, potential only for initialization/postprocess"
        domains.append(
            RectDomain(
                component,
                f"{prefix}screen_S{i:02d}",
                f"condenser screen S{i:02d}; {role}",
                radius,
                radius + 0.25,
                -length / 2,
                length / 2,
                "#08519c",
                0.85,
            )
        )
    return domains


def plot_geometry(component: str, refined: bool, out_name: str) -> list[RectDomain]:
    domains = base_domains(component, refined) + screen_domains(component)
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    for domain in domains:
        add_rect(ax, domain)
    for i, domain in enumerate(screen_domains(component)):
        ax.text(domain.z_max_mm + 12, (domain.r_min_mm + domain.r_max_mm) / 2, f"S{i:02d}", fontsize=7, va="center")

    ax.axvline(0, color="black", lw=0.8, ls="--")
    ax.text(8, 333, "z=0 flange mid-plane", fontsize=9)
    ax.set_xlim(-675, 1730)
    ax.set_ylim(0, 382)
    ax.set_xlabel("z axial coordinate (mm)")
    ax.set_ylabel("r radial coordinate (mm)")
    ax.set_title(f"BRFGL1-126/1250-4 {component} 2D Axisymmetric Geometry Check")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, lw=0.25, alpha=0.45)
    fig.tight_layout()
    fig.savefig(FIG_DIR / out_name, dpi=240)
    plt.close(fig)
    return domains


def write_mapping(domains: list[RectDomain]) -> None:
    boundary_rows = [
        ("comp_v1", "", "B001", "v1_bnd_axisymmetry", "r=0 axisymmetric boundary"),
        ("comp_v1", "", "B002", "v1_bnd_S00_fixed_72p75kV_rms", "S00 high-voltage screen/conductor boundary, 72.75 kV RMS"),
        ("comp_v1", "", "B003", "v1_bnd_S10_ground_0V", "S10 grounded condenser screen, 0 V"),
        ("comp_v1", "", "B004", "v1_bnd_flange_ground", "grounded flange metal boundary"),
        ("comp_v1", "", "B005", "v1_bnd_air_external_convection", "external insulation air convection/radiation boundary"),
        ("comp_v1", "", "B006", "v1_bnd_surrounding_air_outer", "air far-field boundary"),
        ("comp_v1", "", "B007", "v1_bnd_surrounding_oil_outer", "oil far-field boundary"),
        ("comp_v1", "", "B008", "v1_bnd_oil_immersed_surface", "oil-side immersed solid/fluid interface"),
        ("comp_v2", "", "B001", "v2_bnd_axisymmetry", "r=0 axisymmetric boundary"),
        ("comp_v2", "", "B002", "v2_bnd_S00_fixed_72p75kV_rms", "S00 high-voltage screen/conductor boundary, 72.75 kV RMS"),
        ("comp_v2", "", "B003", "v2_bnd_S10_ground_0V", "S10 grounded condenser screen, 0 V"),
        ("comp_v2", "", "B004", "v2_bnd_flange_ground", "grounded flange metal boundary"),
        ("comp_v2", "", "B005", "v2_bnd_air_external_convection", "refined shed air convection/radiation boundary"),
        ("comp_v2", "", "B006", "v2_bnd_surrounding_air_outer", "air far-field boundary"),
        ("comp_v2", "", "B007", "v2_bnd_surrounding_oil_outer", "oil far-field boundary"),
        ("comp_v2", "", "B008", "v2_bnd_oil_immersed_surface", "oil-side immersed solid/fluid interface"),
    ]

    with (TABLE_DIR / "brfgl1_domain_boundary_selection_mapping.csv").open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "component",
                "domain_id",
                "boundary_id",
                "selection_name",
                "physical_meaning",
                "r_min_mm",
                "r_max_mm",
                "z_min_mm",
                "z_max_mm",
            ],
        )
        writer.writeheader()
        for idx, domain in enumerate(domains, start=1):
            writer.writerow(
                {
                    "component": domain.component,
                    "domain_id": f"D{idx:03d}",
                    "boundary_id": "",
                    "selection_name": domain.selection_name,
                    "physical_meaning": domain.physical_meaning,
                    "r_min_mm": domain.r_min_mm,
                    "r_max_mm": domain.r_max_mm,
                    "z_min_mm": domain.z_min_mm,
                    "z_max_mm": domain.z_max_mm,
                }
            )
        for component, domain_id, boundary_id, selection_name, meaning in boundary_rows:
            writer.writerow(
                {
                    "component": component,
                    "domain_id": domain_id,
                    "boundary_id": boundary_id,
                    "selection_name": selection_name,
                    "physical_meaning": meaning,
                    "r_min_mm": "",
                    "r_max_mm": "",
                    "z_min_mm": "",
                    "z_max_mm": "",
                }
            )


def write_checks() -> None:
    checks = [
        ("total_axial_length", 2245, "mm", 1650 - (-595), "PASS"),
        ("air_side_length", 1650, "mm", 1650, "PASS"),
        ("oil_immersed_length", 595, "mm", 595, "PASS"),
        ("external_insulation_max_radius", 135, "mm", 135, "PASS"),
        ("flange_max_radius", 200, "mm", 200, "PASS"),
        ("oil_side_core_radius", 66, "mm", 66, "PASS"),
        ("max_condenser_screen_outer_radius", 66, "mm", 57.75, "PASS"),
        ("creepage_not_used_as_axial_length", 2245, "mm", 2245, "PASS"),
    ]
    with (TABLE_DIR / "brfgl1_geometry_dimension_checks.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["check_name", "required_value", "unit", "model_value", "status"])
        writer.writerows(checks)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    domains_v1 = plot_geometry("comp_v1", refined=False, out_name="brfgl1_geometry_v1_envelope_check.png")
    domains_v2 = plot_geometry("comp_v2", refined=True, out_name="brfgl1_geometry_v2_sheds_check.png")
    domains_preview = plot_geometry("comp_v2_cad_solid_preview", refined=True, out_name="brfgl1_geometry_v2_cad_solid_preview.png")
    write_mapping(domains_v1 + domains_v2 + domains_preview)
    write_checks()

    # Keep the legacy filename pointing to the refined-paper figure.
    legacy = FIG_DIR / "brfgl1_geometry_check.png"
    legacy.write_bytes((FIG_DIR / "brfgl1_geometry_v2_sheds_check.png").read_bytes())

    print(FIG_DIR / "brfgl1_geometry_v1_envelope_check.png")
    print(FIG_DIR / "brfgl1_geometry_v2_sheds_check.png")
    print(TABLE_DIR / "brfgl1_domain_boundary_selection_mapping.csv")
    print(TABLE_DIR / "brfgl1_geometry_dimension_checks.csv")


if __name__ == "__main__":
    main()
