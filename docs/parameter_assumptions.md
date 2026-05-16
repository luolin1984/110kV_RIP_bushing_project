# Parameter Assumptions

This document records parameters that are not direct solved results. It distinguishes drawing dimensions, CAD-derived profile assumptions, and physics assumptions that still require sensitivity checks or later replacement by stronger sources.

## Drawing Dimensions Used Directly

| Parameter | Value | Unit | Rationale | Source |
| --- | ---: | --- | --- | --- |
| Highest voltage for equipment `Um` | 126 | kV | Selected BRFGL1 model class | BRFGL1 drawing / ratings file |
| Rated current `I0` | 1250 | A | Selected BRFGL1 model | BRFGL1 drawing / ratings file |
| Overall axial length `L_total` | 2245 | mm | Total bushing length | BRFGL1 drawing |
| Nominal creepage distance `creepage_check` | 3906 | mm | Recorded for checking only, not used as axial length | BRFGL1 drawing |
| External insulation length `L1_ext` | 1150 | mm | Air-side external insulation section | BRFGL1 drawing |
| Oil immersed length `oil_len` | 595 | mm | z<0 oil-side length | BRFGL1 drawing |
| Air-side equivalent length `air_len` | 1650 | mm | `L_total - oil_len` | Derived from BRFGL1 drawing |
| CT length `L3_ct` | 200 | mm | Metadata only in current axisymmetric model | BRFGL1 drawing |
| Flange length `L4_flange` | 200 | mm | Grounded flange connection region | BRFGL1 drawing |
| Flange radius `r_flange` | 200 | mm | D/2 from D=400 mm | BRFGL1 drawing |
| Bolt circle `bolt_circle_D0` | 350 | mm | Metadata only; bolt holes not modeled in 2D axisymmetry | BRFGL1 drawing |
| Flange thickness `flange_t` | 30 | mm | Grounded flange disk thickness | BRFGL1 drawing |
| Terminal dimension `terminal_a1` | 40 | mm | Air-side terminal connector region | BRFGL1 drawing |
| Inner conduit radius `r_hollow` | 20 | mm | d3/2 from d3=40 mm | BRFGL1 drawing |
| Oil-side core radius `r_rip` | 66 | mm | D1/2 from D1=132 mm | BRFGL1 drawing |
| External insulation max radius `r_housing` | 135 | mm | D2/2 from D2=270 mm | BRFGL1 drawing |

## CAD-Derived Geometry Assumptions

| Parameter or file | Value / treatment | Unit | Rationale | Source |
| --- | --- | --- | --- | --- |
| `Drawing1.dwg` | Original user CAD file | N/A | Manufacturer/profile shape source | User-provided CAD |
| `Drawing1.dxf` | Converted DXF, AutoCAD 2004 | N/A | Parsed using `ezdxf` | User conversion |
| Air-side CAD profile | Rescaled to z=0..1150 and r<=135 | mm | DXF is schematic and single-layer, so profile is used as shape source only | `brfgl1_cad_v2_air_profile.csv` |
| Oil-side CAD profile | Rescaled to z=-595..0 and r<=66 | mm | Uses CAD upper envelope and BRFGL1 drawing dimensions | `brfgl1_cad_v2_oil_profile.csv` |
| CAD extraction method | LINE/ARC sampling, high dimension leader removed, upper envelope extracted | N/A | Separates outline from dimensions in a single-layer DXF | `scripts/extract_cad_profile_dxf.py` |
| `comp_v2_cad_solid_preview` | No surrounding air/oil domains | N/A | Visual review against CAD only | `build_geometry_brfgl1.java` |

## Engineering Geometry Assumptions

| Parameter | Value | Unit | Rationale | Source |
| --- | ---: | --- | --- | --- |
| Conductor outer radius `r_conductor_outer` | 32 | mm | Provides finite tube wall around d3 inner hollow and leaves screen stack inside D1/2 | Engineering assumption |
| Silicone trunk radius `r_body` | 82 | mm | Inner trunk used beneath CAD-derived shed strips | Engineering assumption constrained by CAD/D2 |
| Air-side terminal radius `r_terminal` | 40 | mm | Equivalent terminal connector radius from a1 | Engineering assumption |
| Flange neck radius `r_flange_neck` | 100 | mm | Axisymmetric approximation of flange connection | Engineering assumption |
| Far-field radius `r_far` | 360 | mm | Surrounding air/oil computation domain extent | Engineering assumption; sensitivity if boundary effects appear |
| Screen numerical thickness `screen_th` | 0.25 | mm | Thin-domain representation for explicit screen selections | Numerical modeling assumption |

## Physics Assumptions To Revisit

| Parameter | Current value | Unit | Rationale | Status |
| --- | ---: | --- | --- | --- |
| Nominal contact resistance `Rc0` | 1e-6 | ohm | Initial contact heat-source parameter | Requires sensitivity/calibration |
| Contact multiplier `Rc_factor` | 1 | pu | Deterioration multiplier placeholder | To be swept |
| Contact heat source | `I0^2*Rc0*Rc_factor/V_contact` | W/m^3 | Volumetric heat source in terminal-conductor connection | Implement in physics stage |
| S00 voltage | 72.75 | kV RMS | Phase-to-ground RMS for 126 kV class | Use as fixed high-voltage boundary |
| S01-S09 potentials | Initial values only | kV | Floating screens; not fixed Dirichlet voltages | Must preserve in physics setup |
| S10 voltage | 0 | V | Grounded screen/flange | Use as ground boundary |

## Review Notes

The CAD-derived V2 geometry is suitable for structural review and as the next physics baseline. It is not a direct, layer-clean CAD import; if a cleaned sectional DXF with separate solid/dimension layers becomes available, `extract_cad_profile_dxf.py` should be rerun or replaced with a layer-aware extractor.
