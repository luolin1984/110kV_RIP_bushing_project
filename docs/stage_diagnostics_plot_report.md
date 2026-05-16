# Stage Diagnostics Plot Report

Date: 2026-05-16

## Goal

This plotting pass generates current-stage review figures for geometry correctness, CAD-profile continuity, domain/material assignment, electric-boundary setup, and thermal anomaly diagnosis. These are not final SCI result figures.

## Inputs Used

- `data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv`
- `data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv`
- `data/processed/condenser_screens.csv`
- `results/raw_comsol_exports/PHYSICS_DIAGNOSTICS_RUN003/diagnostic_results.csv`
- `results/raw_comsol_exports/STEADY_1250_LOAD_1p0_RUN002/baseline_metrics.csv`
- `results/summary_tables/domain_selection_integrity_check.csv`
- `results/summary_tables/profile_gap_check.csv`

## Generated Figures

- `results/paper_figures/stage_diagnostics/fig01_geometry_drawing_vs_comsol_v2.png`: drawing constraints versus COMSOL V2 reconstructed geometry.
- `results/paper_figures/stage_diagnostics/fig02_v1_v2_geometry_comparison.png`: V1 equivalent model versus V2 CAD-driven model.
- `results/paper_figures/stage_diagnostics/fig03_cad_profile_gap_check.png`: air/oil CAD profile continuity and gap status.
- `results/paper_figures/stage_diagnostics/fig04_domain_material_assignment.png`: domain partition and material-assignment review.
- `results/paper_figures/stage_diagnostics/fig05_heat_sources_and_convection_boundaries.png`: heat-source regions and external convection boundaries.
- `results/paper_figures/stage_diagnostics/fig06_electric_boundary_and_floating_screens.png`: S00/S10/floating screen electric-boundary setup.
- `results/paper_figures/stage_diagnostics/fig07_baseline_electric_field_summary.png`: baseline electric-field diagnostic values from RUN002 CSV.
- `results/paper_figures/stage_diagnostics/fig08_run002_invalid_temperature_summary.png`: RUN002 temperature status summary using current files.
- `results/paper_figures/stage_diagnostics/fig09_physics_diagnostics_tmax_bar.png`: RUN003 thermal diagnostic Tmax comparison.
- `results/paper_figures/stage_diagnostics/fig10_physics_diagnostics_emax_bar.png`: RUN003 electric-field diagnostic Emax comparison.
- `results/paper_figures/stage_diagnostics/fig11_heat_source_decomposition.png`: heat-source decomposition availability check.
- `results/paper_figures/stage_diagnostics/fig12_heat_balance_summary.png`: heat-balance data availability placeholder.
- `results/paper_figures/stage_diagnostics/fig13_selection_integrity_check.png`: selection integrity review for Tmax postprocessing.

## Current Model Issues

- RUN002 in the current CSV is no longer the old 674.88 degC invalid result; it is recorded as `SOLVED` with `Tmax_global_C = 211.226442 degC`. It is still a diagnostic baseline rather than a final paper target.
- RUN003 shows that disabling RIP dielectric loss barely changes Tmax, while constant copper loss lowers Tmax but remains high. The dominant problem is therefore more likely in heat boundary treatment, conductor-loss normalization, selection integrity, or thermal path setup than in dielectric loss alone.
- RUN004 implemented solid-domain heat transfer and CAD segmented convection, but did not converge to a valid coupled solution. No RUN004 values should be backfilled into validation targets.
- Heat-source decomposition and heat-balance figures remain incomplete because a valid converged RUN004 heat-balance export is not yet available.

## Can the project enter a 27-case small sweep?

No. The project should not enter the 27-case parameter sweep yet. The next COMSOL correction should build a solver-oriented solid-only component from the CAD solid preview, keep surrounding air/oil out of the thermal mesh, and rerun the heat-balance diagnostics until `Tmax`, heat-source totals, and convection removal are physically consistent.
