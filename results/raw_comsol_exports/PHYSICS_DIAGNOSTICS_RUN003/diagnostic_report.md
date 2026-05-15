# Physics Diagnostics RUN003

This run separates `std_es`, `std_ht`, and `std_cpl`, then disables one suspect feature group at a time.

The machine-readable summary is `diagnostic_results.csv`. Per-case exception stacks are written as `*_exception.txt` when a case fails.

Diagnostic toggles:

- `disable_floating`: disables S01-S09 floating-potential screen boundaries.
- `disable_dielectric`: disables RIP dielectric heat source using `es.normE`.
- `disable_convection`: disables air and oil convection boundary features.
- `constant_copper_loss`: replaces temperature-dependent copper Joule heat with a constant 20 degC expression.

CSV path: /Users/luolin/Documents/New project/110kV_RIP_bushing_project/results/raw_comsol_exports/PHYSICS_DIAGNOSTICS_RUN003/diagnostic_results.csv

## Result summary

- `ES_FULL` and `ES_NO_FLOATING` both solved. Floating-potential screens are not the solver blocker.
- `HT_FULL` solved after moving field-dependent heat-source expressions from global parameters into HeatSource features.
- `CPL_FULL` solved, with `Tmax_global_C = 673.330613 degC`.
- `CPL_NO_DIELECTRIC` only reduced Tmax to `667.703128 degC`, so RIP dielectric loss is not the dominant cause of the excessive temperature.
- `CPL_CONSTANT_CU` reduced Tmax to `443.782223 degC`, so temperature-dependent copper loss amplification is a major contributor.
- `CPL_NO_CONVECTION` produced a nonphysical negative extreme temperature and is only a boundary-condition diagnostic, not a valid operating case.
- `CPL_ALL_SUSPECTS_OFF` failed because removing convection makes the coupled thermal problem ill-conditioned/nonphysical.

## Diagnosis

The original solver failure was caused by two script issues:

1. Some domains had no fallback material, so `epsilonr` and `k` were undefined.
2. `Qjoule_cu` and `Qdielectric_rip` were defined as global parameters even though they contained field variables `T` and `es.normE`.

Both issues are now fixed in `build_physics_brfgl1.java`. The remaining issue is not a solver failure but a thermal-magnitude problem: the coupled baseline solves but is rejected as thermally unphysical.
