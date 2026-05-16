# RUN004 Heat Diagnostics Report

Date: 2026-05-15

RUN004 follows `任务说明9` where it does not conflict with the previous RUN002 correction. RUN002 is no longer treated as the old 674.88 degC invalid run; RUN004 is a new diagnostic attempt with solid-domain heat transfer and CAD outer-surface convection.

## Implemented

- Added `comsol/heat_balance_diagnostics.java`.
- Added segmented CAD convection boundary selections for air and oil surfaces.
- Exported `results/summary_tables/air_convection_boundaries.csv`.
- Exported `results/summary_tables/oil_convection_boundaries.csv`.
- Added strict non-overlapping thermal/postprocessing selections.
- Exported `results/summary_tables/domain_selection_integrity_check.csv`.
- Updated RUN004 baseline script paths to write under `STEADY_1250_LOAD_1p0_RUN004`.

## RUN004 outcome

RUN004 is not valid. `std_es` solved, but `std_ht` stalled and `std_cpl` became nonphysical/nonconvergent. The coupled log reported electric potential scale around `1.3e9 V`, so the run was stopped. No `validation_targets.csv` values were backfilled.

## Recommended next step

Create a solver-oriented solid-only component for RUN004 using the same CAD exterior profile but without surrounding air/oil domains in the mesh. The existing `comp_v2_cad_solid_preview` is the best starting point; it needs physics-ready selections and boundary operators rather than being only a visual preview.
