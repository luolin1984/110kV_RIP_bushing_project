# Validation Update Report

Date: 2026-05-15

## RUN002 status

`STEADY_1250_LOAD_1p0` was rerun with the CAD-driven BRFGL1-126/1250-4 geometry and separated COMSOL scripts. After the heat-magnitude corrections, RUN002 is now accepted as a provisional thermal baseline.

- Geometry generation: completed.
- Profile gap check: passed, no remaining air/oil CAD profile gaps.
- Geometry overlap check: passed for the required non-overlap items; `oil_side_core` and `oil_side_shield_or_tapered_region` are retained as selections, not duplicate solid domains.
- Physics model generation: completed.
- Mesh generation during baseline run: completed.
- Solver status: `SOLVED`.
- Thermal acceptance: accepted within the configured physical range `[-60, 250] degC`.

The earlier `674.882292 degC` result is superseded. The main correction was to tighten thermal/material domain coverage so air and oil material selections no longer overwrite solid insulation domains, add explicit far-field air/oil temperature boundaries, and use a provisional RIP through-thickness thermal conductivity of `0.20 W/(m*K)` pending sensitivity analysis.

## RUN002 metrics

Latest file: `results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN002/baseline_metrics.csv`

- `Tmax_global_C`: `211.226442 degC`
- `Tmax_conductor_C`: `211.226442 degC`
- `Tmax_RIP_C`: `206.461446 degC`
- `Tmax_contact_C`: `211.226442 degC`
- `Emax_global_V_per_m`: `5.05545924e7`
- `Emax_RIP_V_per_m`: `2.95504965e7`
- `Emax_screen_end_probe_V_per_m`: `2.95504965e7`
- `Qcontact_W`: `1.5625`

## Files produced

- `results/summary_tables/profile_gap_check.csv`
- `results/summary_tables/geometry_overlap_check.csv`
- `results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN002/baseline_metrics.csv`
- `results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN002/baseline_exception_report.md`
- `comsol/BRFGL1-126-1250-4_geometry_axisym.mph`
- `comsol/BRFGL1-126-1250-4_physics_baseline.mph`
- `comsol/BRFGL1-126-1250-4_baseline_STEADY_1250_LOAD_1p0_RUN002.mph`
- `results/raw_comsol_exports/PHYSICS_DIAGNOSTICS_RUN003/diagnostic_results.csv`

## Validation table action

`validation_targets.csv` keeps the previous invalid RUN001 records as an audit trail. The RUN002 thermal rows are now backfilled as provisional valid baseline targets:

- `VT_BASE_TMAX_CONDUCTOR_RUN002 = 211.226442 degC`
- `VT_BASE_TMAX_RIP_RUN002 = 206.461446 degC`

`VT_BASE_EMAX_RUN002` is retained as diagnostic only. The current value is `29.5504965 kV/mm`, converted from `2.95504965e7 V/m`, but it still needs screen-end probe placement review and mesh-convergence confirmation before being used as a final validation target.

## Diagnostic findings

RUN003 separated the physics into diagnostic cases:

- `std_es` solves with and without floating screens. Floating Potential is not the blocking feature.
- `std_ht` solves after heat-source expressions are moved out of global parameters. The earlier failures were caused by `T` and `es.normE` being evaluated in global-parameter context.
- `std_cpl` solves for full coupling and one-feature-off variants.
- Turning off convection creates a nonphysical thermal problem and gives negative extreme temperatures in some diagnostic cases.

The later heat-magnitude correction showed that the dominant issue was not the analytic Joule heat formula itself, but overly broad material/domain coverage and incomplete external thermal boundary treatment.

## Remaining checks

Before manuscript use, keep these checks open:

1. Run medium/fine mesh convergence for `Tmax_conductor`, `Tmax_RIP`, and probe-based `Emax`.
2. Sweep RIP thermal conductivity around `0.10-0.25 W/(m*K)` and keep the final value traceable to a material source or calibration.
3. Review `v2_center_conductor`, `v2_contact_resistance_heat_source_layer`, and `v2_rip_capacitor_core` postprocessing selections because conductor/contact maxima are still colocated.
4. Review screen-end electric-field probes so local singularities are not used as validation maxima.

## RUN004 note

RUN004 was attempted after task-9 corrections. It uses solid-domain heat transfer, segmented CAD outer-surface convection selections, strict non-overlapping postprocessing selections, and a coarser diagnostic mesh. The run did not converge to a valid coupled solution: `std_es` solved, `std_ht` stalled, and `std_cpl` became nonphysical/nonconvergent with the electric-potential scale reaching about `1.3e9 V` in the COMSOL log.

No RUN004 values were backfilled into `validation_targets.csv`. See `docs/run004_heat_diagnostics_report.md` and `results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN004/baseline_exception_report.md`.
