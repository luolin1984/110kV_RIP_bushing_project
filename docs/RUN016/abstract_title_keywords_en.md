# Abstract, Title Options, and Keywords

## Title Options

1. Electro-Thermal Coupled Finite-Element Diagnostic Risk-Boundary Simulation of a 126 kV/1250 A RIP Condenser Transformer Bushing under Contact-Resistance Degradation
2. Numerical Screening of Contact-Resistance Degradation in a 126 kV/1250 A RIP Condenser Transformer Bushing Using Field-Coupled Electro-Thermal Finite-Element Simulation
3. Field-Coupled Dielectric-Loss and Contact-Degradation Effects in a 126 kV/1250 A RIP Condenser Transformer Bushing: A Finite-Element Diagnostic Risk-Boundary Study

## Recommended Title

Electro-Thermal Coupled Finite-Element Diagnostic Risk-Boundary Simulation of a 126 kV/1250 A RIP Condenser Transformer Bushing under Contact-Resistance Degradation

## Abstract

This study develops a staged electro-thermal coupled finite-element model for a 126 kV/1250 A resin-impregnated paper (RIP) condenser transformer bushing under load, oil-temperature, and contact-resistance degradation conditions. The workflow normalizes conductor Joule heating and contact heating, introduces field-coupled RIP dielectric loss, and audits heat balance, by-ID selections, electric-field singularity, mesh convergence, and material/boundary sensitivity. The main RUN010 matrix contains 125 steady cases. Across this matrix, Tmax_global_C ranges from 67.397-134.974 degC, and Tmax_contact_C reaches 129.925 degC. The global diagnostic risk-zone counts are safe 119, attention 4, warning 2, and thermal-risk 0. The contact-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, and contact-risk 0. The field-coupled dielectric-loss review flag is retained because the field/reference ratio is 11.020, while field_singularity_flag is 0/125. Mesh verification gives 0.355% maximum medium-vs-fine Tmax error, and the sensitivity ranking is tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. The results are finite-element numerical screening evidence, not laboratory or field validation; the diagnostic risk zones are internal screening classes, not standard limits.

## Keywords

RIP condenser bushing; transformer bushing; electro-thermal coupling; finite-element simulation; contact-resistance degradation; field-coupled dielectric loss; diagnostic risk boundary; mesh convergence

## Novelty Bullets

- Establishes a CAD-constrained, by-ID selection, finite-element numerical screening workflow for a 126 kV/1250 A RIP condenser transformer bushing.
- Replaces an approximate dielectric-loss reference with field-coupled RIP dielectric-loss integration while preserving the dielectric-loss review flag.
- Quantifies load, oil-temperature, and contact-resistance multiplier effects across the 125-case RUN010 matrix.
- Locks numeric claims to raw evidence tables, figure/table callouts, and reference placeholders before full manuscript formatting.

## Claim-Boundary Note

This draft presents finite-element numerical screening results. It does not claim laboratory validation, field-monitoring validation, standard-limit compliance, or measured contact-defect reproduction. Diagnostic risk zones are internal screening classes.
