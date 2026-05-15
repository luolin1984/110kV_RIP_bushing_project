# BRFGL1-126/1250-4 COMSOL Geometry Generation Report

## Purpose

This report records the regenerated COMSOL 2D axisymmetric geometry for the BRFGL1-126/1250-4 RIP dry condenser transformer bushing. The previous simplified straight-cylinder geometry has been replaced by three explicit geometry components:

- `comp_v1`: equivalent stepped-envelope geometry for fast electro-thermal computation.
- `comp_v2`: CAD-profile-driven shed and oil-transition geometry for paper figures and detailed environmental boundary studies.
- `comp_v2_cad_solid_preview`: CAD-profile-driven solid-only preview without surrounding air/oil domains, intended for visual comparison with `Drawing1.dxf`.

## Coordinate System

- COMSOL geometry type: 2D axisymmetric.
- r coordinate: COMSOL x coordinate.
- z coordinate: COMSOL y coordinate.
- z = 0: flange center/mid-plane.
- z > 0: air side.
- z < 0: oil side.
- The geometry may appear vertical in COMSOL; r and z are not swapped.

## BRFGL1 Drawing Dimensions Used

| Parameter | Value | Unit | Implementation |
|---|---:|---|---|
| Rated voltage | 126 | kV | `Um` |
| Rated current | 1250 | A | `I0` |
| Overall axial length L | 2245 | mm | `L_total` |
| Nominal creepage distance | 3906 | mm | `creepage_check`; not used as axial length |
| External insulation length L1 | 1150 | mm | `L1_ext` |
| External insulation diameter D2 | 270 | mm | `r_housing = 135 mm` |
| Oil immersed length L2 | 595 | mm | `oil_len` |
| CT length L3 | 200 | mm | `L3_ct`, metadata only |
| Flange length L4 | 200 | mm | `L4_flange` |
| Flange outer diameter D | 400 | mm | `r_flange = 200 mm` |
| Bolt circle D0 | 350 | mm | `bolt_circle_D0`, not explicitly modeled |
| Flange thickness H | 30 | mm | `flange_t` |
| Terminal dimension a1 | 40 | mm | `terminal_a1` |
| Conduit inner diameter d3 | 40 | mm | `r_hollow = 20 mm` |
| Oil-side core diameter D1 | 132 | mm | `r_rip = 66 mm` |

## CAD Source And Calibration

The CAD source provided by the user was:

- Original DWG: `/Users/luolin/Desktop/Drawing1.dwg`
- Converted DXF: `/Users/luolin/Downloads/Drawing1.dxf`

The project stores copies here:

- `data/raw_sources/manufacturer_catalogs/cad/BRFGL1-126-1250-4_Drawing1.dwg`
- `data/raw_sources/manufacturer_catalogs/cad/BRFGL1-126-1250-4_Drawing1.dxf`

The extraction workflow is implemented in `scripts/extract_cad_profile_dxf.py`. It reads the DXF with `ezdxf`, samples LINE and ARC entities, removes the high dimension leader, and extracts the upper-envelope profile.

The CAD drawing is a schematic manufacturer view, not a dimensionally uniform COMSOL r-z model. Therefore, the CAD is used as the shape source and is rescaled to the public BRFGL1 dimensions:

- oil-side CAD profile -> `z = -595..0 mm`, radius capped by `D1/2 = 66 mm`;
- air-side CAD profile -> `z = 0..1150 mm`, radius capped by `D2/2 = 135 mm`;
- flange and conductor dimensions remain governed by the explicit BRFGL1 parameters.

Generated CAD-driven profile files:

- `data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv`
- `data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv`
- `data/processed/cad_extract/Drawing1_cad_profile_extraction_check.png`

`comsol/build_geometry_brfgl1.java` reads these CSV files when building `comp_v2`.

For visual checking, `comp_v2_cad_solid_preview` reads the same CAD-derived CSV files but omits `surrounding_air_domain` and `surrounding_oil_domain`. This component should be used when comparing the COMSOL geometry with `Drawing1.dxf`; `comp_v2` should be used for later electro-thermal physics because it includes the external air and oil domains.

## Domain Partitioning

Both V1 and V2 include the required domain selections, with unique prefixes:

- `v1_center_conductor`, `v2_center_conductor`
- `v1_inner_conduit_or_hollow_region`, `v2_inner_conduit_or_hollow_region`
- `v1_rip_capacitor_core`, `v2_rip_capacitor_core`
- `v1_condenser_screens`, `v2_condenser_screens`
- `v1_silicone_rubber_external_insulation`, `v2_silicone_rubber_external_insulation`
- `v1_air_side_sheds_or_equivalent_envelope`, `v2_air_side_sheds_or_equivalent_envelope`
- `v1_flange_grounded_metal`, `v2_flange_grounded_metal`
- `v1_oil_side_core`, `v2_oil_side_core`
- `v1_oil_side_shield_or_tapered_region`, `v2_oil_side_shield_or_tapered_region`
- `v1_terminal_connector_region`, `v2_terminal_connector_region`
- `v1_contact_resistance_heat_source_layer`, `v2_contact_resistance_heat_source_layer`
- `v1_surrounding_air_domain`, `v2_surrounding_air_domain`
- `v1_surrounding_oil_domain`, `v2_surrounding_oil_domain`

The preview component uses the `pv_` prefix, for example `pv_center_conductor` and `pv_air_side_sheds_or_equivalent_envelope`. The prefix is used because COMSOL requires globally unique selection tags when multiple geometry variants are stored in one model file.

## Condenser Screens

Explicit thin screen domains are created for `S00` through `S10`:

- `S00`: high-voltage screen, fixed 72.75 kV RMS.
- `S10`: grounded screen, fixed 0 V.
- `S01` to `S09`: floating screens. Their listed potential values are only initialization or postprocessing references and must not be imposed as fixed Dirichlet potentials.
- Maximum screen outer radius is 57.75 mm, below the oil-side core radius limit of 66 mm.

Screen selections follow the same prefix rule, for example `v1_screen_S00` and `v2_screen_S00`.
The solid-preview screen selections use `pv_screen_S00` through `pv_screen_S10`.

## Contact Resistance Region

The contact-resistance heat-source layer is now placed at the air-side terminal-to-center-conductor connection region:

- z range: 1150 mm to 1190 mm.
- radial range: 20 mm to 32 mm.
- parameterized volumetric source:

`Q_contact_vol = I0^2 * Rc0 * Rc_factor / V_contact`

This region has separate selections `v1_contact_resistance_heat_source_layer` and `v2_contact_resistance_heat_source_layer` for later `Tmax_contact` extraction.
The preview component uses `pv_contact_resistance_heat_source_layer` for visual inspection only.

## Outputs

- COMSOL geometry model: `comsol/BRFGL1-126-1250-4_geometry_axisym.mph`
- COMSOL geometry script: `comsol/build_geometry_brfgl1.java`
- Geometry run script: `comsol/run_build_geometry_brfgl1.sh`
- V1 geometry check figure: `results/paper_figures/brfgl1_geometry_v1_envelope_check.png`
- V2 CAD-driven geometry check figure: `results/paper_figures/brfgl1_geometry_v2_sheds_check.png`
- V2 CAD solid-only preview figure: `results/paper_figures/brfgl1_geometry_v2_cad_solid_preview.png`
- Legacy geometry figure alias: `results/paper_figures/brfgl1_geometry_check.png`
- Selection mapping table: `results/summary_tables/brfgl1_domain_boundary_selection_mapping.csv`
- Dimension checks: `results/summary_tables/brfgl1_geometry_dimension_checks.csv`
- COMSOL run log: `results/raw_comsol_exports/GEOMETRY_BRFGL1/comsol_batch.log`

## Dimension Check Summary

| Check | Required | Model | Status |
|---|---:|---:|---|
| Total axial length | 2245 mm | 2245 mm | PASS |
| Air-side length | 1650 mm | 1650 mm | PASS |
| Oil immersed length | 595 mm | 595 mm | PASS |
| External insulation max radius | 135 mm | 135 mm | PASS |
| Flange max radius | 200 mm | 200 mm | PASS |
| Oil-side core radius | 66 mm | 66 mm | PASS |
| Maximum condenser-screen outer radius | <= 66 mm | 57.75 mm | PASS |

COMSOL batch generation completed successfully on 2026-05-15. The model contains geometry only; electrostatic and heat-transfer physics should be attached in the next modeling step using the prefixed selections.

## Current Limitation

The DXF conversion contains only one layer and includes dimensions, circles, text, and the bushing outline together. The current extractor uses geometric filtering and known BRFGL1 dimensions to obtain a robust axisymmetric profile. This is adequate for a CAD-informed V2 model, but not a substitute for a fully cleaned manufacturer 2D section with separate layers for solids, dimensions, and hidden lines.
