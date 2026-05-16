# Solid-only RUN005 heat balance

- status: SOLVED_INVALID_TEMPERATURE
- Tmax_global_C: 176.187367
- Qjoule_total_W: 1152.08385
- Qcontact_total_W: 910.629620
- Qdielectric_total_W: 4.70694070
- heat_removed_air_W: 231.612911
- heat_removed_oil_W: 1670.36967
- residual_heat_balance_W: 165.437831

This is a solver-oriented solid-only diagnostic model. RIP dielectric loss uses `Qdielectric_rip_ref` for thermal stability; electrostatic field values are exported for review but are not final validation targets.
