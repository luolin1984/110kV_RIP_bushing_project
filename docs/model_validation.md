# Model Validation

This document tracks validation and review targets for the BRFGL1-126/1250-4 RIP dry condenser transformer bushing model.

## Current Stage

The project is currently at the geometry-validation stage. The previous first-pass electro-thermal run is retained only as a script-execution test because its thermal result was unphysical. Production electro-thermal validation should be performed after physics are rebuilt on the current CAD-driven geometry.

## Geometry Validation

| Target | Simulation or file output | Reference | Acceptance criterion | Status |
| --- | --- | --- | --- | --- |
| Coordinate system | `BRFGL1-126-1250-4_geometry_axisym.mph` | Task 8 and user requirements | 2D axisymmetric r-z; z=0 at flange mid-plane; z>0 air side; z<0 oil side | PASS |
| Total axial length | `brfgl1_geometry_dimension_checks.csv` | BRFGL1 drawing dimension L | 2245 mm | PASS |
| Air-side equivalent length | `brfgl1_geometry_dimension_checks.csv` | L - L2 | 1650 mm | PASS |
| Oil immersed length | `brfgl1_geometry_dimension_checks.csv` | L2 | 595 mm | PASS |
| External insulation max radius | `brfgl1_geometry_dimension_checks.csv` | D2/2 | 135 mm | PASS |
| Flange max radius | `brfgl1_geometry_dimension_checks.csv` | D/2 | 200 mm | PASS |
| Oil-side core radius | `brfgl1_geometry_dimension_checks.csv` | D1/2 | 66 mm | PASS |
| Condenser-screen radius limit | `brfgl1_geometry_dimension_checks.csv` | Screen radius <= 66 mm | Maximum 57.75 mm | PASS |
| CAD profile extraction | `Drawing1_cad_profile_extraction_check.png` | `Drawing1.dxf` | Air/oil profiles extracted and rescaled to BRFGL1 dimensions | REVIEW |
| Solid-only visual comparison | `comp_v2_cad_solid_preview`; `brfgl1_geometry_v2_cad_solid_preview.png` | `Drawing1.dxf` | No surrounding air/oil domains; suitable for visual structure review | REVIEW |

## Electrical Validation Pending

| Target | Simulation output | Reference | Acceptance criterion | Status |
| --- | --- | --- | --- | --- |
| S00 high-voltage condition | `v2_screen_S00` or `v2_bnd_S00_fixed_72p75kV_rms` | `condenser_screens.csv` | Fixed 72.75 kV RMS | Pending physics rebuild |
| S10 ground condition | `v2_screen_S10` or `v2_bnd_S10_ground_0V` | `condenser_screens.csv` | Fixed 0 V | Pending physics rebuild |
| Floating screen treatment | S01-S09 selections | `condenser_screens.csv` | Floating potential or zero charge, not fixed voltage | Pending physics rebuild |
| Maximum electric field | COMSOL postprocessing | Literature / design margin | TBD after field solve | Pending |

## Thermal Validation Pending

| Target | Simulation output | Reference | Acceptance criterion | Status |
| --- | --- | --- | --- | --- |
| Contact hot spot | `v2_contact_resistance_heat_source_layer` | Contact resistance model | Extract `Tmax_contact` | Pending physics rebuild |
| RIP hot spot | `v2_rip_capacitor_core` | Literature trend | Physically plausible temperature and location | Pending |
| Surface temperature rise | External insulation boundaries | Literature [9], [11] | Surface temperature difference trend under contact deterioration | Pending |
| Boundary-condition sanity | Air/oil convection boundaries | Heat-transfer references | No fixed-temperature overconstraint causing unphysical Tmax | Pending |

## Validation Rule

Do not use the initial `STEADY_1250_LOAD_1p0` thermal maxima as model validation. They came from the old first-pass model and were marked unphysical. New validation must be run on the current CAD-driven geometry, preferably `comp_v2`.
