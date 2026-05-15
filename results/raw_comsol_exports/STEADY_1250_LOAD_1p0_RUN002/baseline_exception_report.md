# STEADY_1250_LOAD_1p0 RUN002 exception report

- status: INVALID_TEMPERATURE_RANGE
- note: RUN002 CAD-driven baseline; Tmax_global_C outside physical acceptance range [-60, 250] C
- action: do not backfill validation targets as valid baseline values.
- diagnostic basis: RUN003 showed `std_es`, `std_ht`, and `std_cpl` can solve after material coverage and field-dependent heat-source expression fixes.
- rejected value: `Tmax_global_C = 674.882292 degC`.
- next correction: check conductor Joule heat normalization, heat-source domain selections, postprocessing selections, and convection boundary selections.
