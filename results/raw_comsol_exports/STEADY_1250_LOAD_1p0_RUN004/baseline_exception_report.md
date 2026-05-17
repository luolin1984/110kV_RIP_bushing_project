# STEADY_1250_LOAD_1p0 RUN004 exception report

- status: SOLVE_STALLED_NONCONVERGED
- accepted_as_validation_target: false
- action: do not backfill `validation_targets.csv`.

## What was attempted

RUN004 implemented the task-9 thermal correction path:

- heat transfer was restricted to `v2_thermal_solid_domains`;
- surrounding air and oil domains were not used as heat-transfer domains;
- air and oil convection were moved from broad box selections to CAD-strip outer-surface boundary selections;
- non-overlapping conductor/RIP/contact/flange/silicone postprocessing selections were added;
- mesh was coarsened to `autoMeshSize(9)` for diagnostic speed.

## Solver outcome

`std_es` solved. The standalone thermal run `std_ht` repeatedly stalled near the final linear-solver stage. The coupled run `std_cpl` then became nonphysical/nonconvergent, with the electric-potential scale reported in the COMSOL log around `1.3e9 V`, far above the 72.75 kV RMS baseline.

Because RUN004 did not reach a valid coupled solution and did not satisfy `Tmax_global_C < 150 degC`, no thermal or electric-field values from this run are valid baseline targets.

## Next correction

Use the solid-only preview component or a new solver-oriented V2 component without surrounding air/oil domains for the RUN004 heat solve. Keep the CAD-strip boundary CSVs as the audit trail, but reduce the actual thermal mesh to bushing solids only before rerunning.
