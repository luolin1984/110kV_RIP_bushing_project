# COMSOL Baseline Run Report: STEADY_1250_LOAD_1p0

## Status

The first 2D axisymmetric baseline COMSOL Java script was generated and executed for `STEADY_1250_LOAD_1p0`.

This report is now a historical record of the initial script-execution test. It does not describe the current geometry baseline. The current geometry baseline has been regenerated from BRFGL1 dimensions and CAD-derived profiles; see `docs/brfgl1_geometry_generation_report.md`.

Selected model:

- Main model: `BRFGL1-126/1250-4`
- Current-carrying mode: direct current carrying
- Alternative model not used in this baseline: `BRFGL2-126/1250-4`, cable current carrying

Generated model files:

- `comsol/build_model.java`
- `comsol/run_steady_1250_load_1p0.sh`
- `comsol/BRFGL1-126-1250-4_base_model_2d_axisym_STEADY_1250_LOAD_1p0.mph`

Raw run outputs:

- `results/raw_comsol_exports/STEADY_1250_LOAD_1p0/comsol_batch.log`
- `results/raw_comsol_exports/STEADY_1250_LOAD_1p0/run_stdout.log`
- `results/raw_comsol_exports/STEADY_1250_LOAD_1p0/metrics_export.csv`

## Solver Progress

The script completed the required first-pass sequence:

1. Electric-field independent stationary solve: completed.
2. Thermal independent stationary solve: completed.
3. Coupled electro-thermal stationary solve: completed.

Mesh summary from the COMSOL log:

- Mesh vertices: 26
- Mesh elements: 337
- Degrees of freedom, electric solve: 1842
- Degrees of freedom, thermal solve: 1842 plus 1012 internal DOFs
- Degrees of freedom, coupled solve: 3684 plus 1012 internal DOFs

This is a coarse first-pass mesh and is not a mesh-independent result.

## Modeling Implemented

The generated model includes:

- 2D axisymmetric geometry
- copper conductor
- RIP capacitor core
- simplified silicone-rubber housing
- flange region
- oil-side and air-side domains
- contact heat-source layer
- Electrostatics physics
- Heat Transfer physics
- conductor Joule heat with copper temperature coefficient
- RIP dielectric loss using first-pass average radial field
- contact heat source using `Q_contact = I^2 * Rc0 * Rc_factor`

For robustness, the first-pass model does not mesh S01-S09 as 0.05 mm foil domains. S00/S10 are represented by HV/ground boundaries, while floating screen implementation is deferred to the refined model.

## Important Caveat

The first run is a successful script/model execution test, but not yet a physically valid thermal calibration run.

The exported thermal maxima from `dset3` are unphysical, exceeding 1e6 degC. This indicates that the current heat-transfer boundary/domain selections or temperature boundary interpretation need correction before thermal results are used.

Therefore:

- `Tmax_conductor_baseline` and `Tmax_RIP_baseline` in `validation_targets.csv` were reset to `to_be_recalibrated_run001_unphysical_temperature`.
- `Emax_RIP_baseline` was backfilled only as an approximate average radial field, `1.7509 kV/mm`, not a local screen-end maximum.
- `Qdielectric_total_baseline` remains a first-pass analytical/COMSOL parameter value and should be recalibrated once field-dependent dielectric loss is implemented.

## Next Fixes Before 27-Case Scan

1. Replace broad box selections with explicit named domain/boundary selections after geometry finalization.
2. Re-implement air/oil heat boundaries as validated convection boundaries rather than broad fixed-temperature boundaries.
3. Add field-dependent dielectric heat using the electric solution, not only average radial field.
4. Implement S01-S09 as floating-potential or zero-charge boundaries without thin-domain meshing.
5. Run a 3-level mesh check before accepting `Tmax` and `Emax`.

The 27-case scan should wait until the baseline thermal field is physically credible.

## Geometry Update After This Run

After this initial baseline run, the geometry workflow was replaced by a dedicated geometry-only model:

- `comsol/build_geometry_brfgl1.java`
- `comsol/run_build_geometry_brfgl1.sh`
- `comsol/BRFGL1-126-1250-4_geometry_axisym.mph`

The new geometry model contains:

- `comp_v1`: equivalent stepped-envelope geometry for fast electro-thermal computation.
- `comp_v2`: CAD-profile-driven geometry with surrounding air and oil domains for later simulation.
- `comp_v2_cad_solid_preview`: CAD-profile-driven solid-only preview for comparison with `Drawing1.dxf`.

The CAD-driven V2 profile is extracted from:

- `data/raw_sources/manufacturer_catalogs/cad/BRFGL1-126-1250-4_Drawing1.dxf`
- `data/processed/cad_extract/brfgl1_cad_v2_air_profile.csv`
- `data/processed/cad_extract/brfgl1_cad_v2_oil_profile.csv`

Therefore, future electro-thermal physics should be attached to the current geometry selections, preferably `v2_*` selections for the CAD-driven simulation model. The old `BRFGL1-126-1250-4_base_model_2d_axisym_STEADY_1250_LOAD_1p0.mph` should not be used for production results until it is rebuilt on the current geometry.
