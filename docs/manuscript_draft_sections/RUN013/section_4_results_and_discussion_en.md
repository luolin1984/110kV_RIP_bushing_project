# 4. Results and Discussion

## 4.1 Baseline electro-thermal field distribution

The baseline full electro-thermal calculation was carried out for STEADY_1250_LOAD_1p0 with a 1250 A current, 72.75 kV phase-to-ground RMS voltage, 85 degC oil temperature, 25 degC air temperature, and R_c_factor = 1. RUN009A returned SOLVED_VALID, with a global maximum temperature of 88.589 degC. The region-specific maxima were not identical: the conductor, RIP, contact layer, silicone housing, and flange reached 74.136 degC, 88.589 degC, 58.790 degC, 57.215 degC, and 46.906 degC, respectively. This separation confirms that the post-processing selections preserve physical region identity rather than returning a single duplicated maximum.

The corresponding heat-source decomposition gives 34.433 W of conductor Joule heat, 1.5625 W of contact heat, and 28.049 W of field-coupled RIP dielectric loss. The heat-balance residual is -1.902%, which falls within the accepted numerical audit range. Figure 2 summarizes the baseline potential/electric-field, dielectric-loss, and temperature evidence used in this discussion.

The field-coupled dielectric loss is higher than the earlier average-field reference. RUN009A gives a field-to-reference dielectric-loss ratio of 11.020; therefore, the DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained. This flag is not treated as model failure because the electric-field singularity check is not triggered, but it means that dielectric parameters and field localization should remain explicit uncertainty items in the manuscript.

## 4.2 Effects of load, oil temperature, and contact resistance

RUN010 extends the field-coupled formulation to 125 steady operating cases. All cases passed the overall validity checks, including heat balance, Joule heat normalization, contact heat normalization, dielectric-loss positivity, selection integrity, and electric-field singularity screening. Across the matrix, Tmax_global ranges from 67.397 degC to 134.974 degC, while the maximum contact-layer temperature reaches 129.925 degC.

The temperature trends are physically consistent. Increasing oil temperature shifts the whole thermal field upward because the oil-side boundary condition becomes warmer. Increasing load raises conductor Joule heat approximately with I^2 and also increases contact heat through the same current-squared dependence. Increasing the contact-resistance multiplier has its strongest effect on the contact-layer temperature, especially under high load and high oil-temperature conditions. Figures 3 and 4 show these coupled responses for the global and contact-region temperature indicators.

These trends should be interpreted as steady-state finite-element responses under a defined parameter matrix. They are not annual weather-driven results and do not include transient overload history. The matrix is nevertheless useful because it separates three engineering drivers: load current, transformer-oil thermal environment, and local current-carrying connection degradation.

## 4.3 Risk boundary analysis

The diagnostic risk zoning in RUN010 classifies the 125 cases as 119 safe, 4 attention, 2 warning, and 0 thermal-risk cases for the global temperature metric. For the contact-region metric, the counts are 115 contact-safe, 6 contact-attention, 4 contact-warning, and 0 contact-risk cases. No thermal-risk case is found within the RUN010 matrix, but several high-load and high-oil-temperature combinations approach the warning range.

The safe-load boundary decreases as oil temperature and contact-resistance multiplier increase. This behavior is expected: higher oil temperature reduces the available thermal margin, while contact degradation redirects a larger fraction of the heat to a localized region. Figure 5 presents the boundary in terms of load, oil temperature, and contact-resistance multiplier.

The risk-zone thresholds used here are diagnostic visualization thresholds. They are not IEC or IEEE standard limits, material lifetime thresholds, or guaranteed operating limits. Their purpose is to organize the numerical response and identify which parts of the parameter space deserve more detailed engineering review.

## 4.4 Field-coupled dielectric-loss contribution

RUN008 used an approximate dielectric-loss reference in the solid-only diagnostic model, whereas RUN010 uses the field-coupled loss term integrated from the electrostatic solution. The comparison between the two 125-case datasets shows that the field-coupled term increases Tmax_global by an average of 0.617 degC and a maximum of 2.816 degC. The risk zone changes in 2 of the 125 cases.

This comparison indicates that the approximate reference heat source was suitable for early source-normalization and heat-balance diagnostics, but it should not be used as the main electro-thermal result once the electric-field solution is available. The full field-coupled model captures the spatial non-uniformity of the RIP dielectric loss and therefore provides a more defensible basis for risk-boundary analysis. Figure 7 shows the RUN008-to-RUN010 temperature differences, while supplementary dielectric-loss plots document the field-to-reference ratio.

The retained DIELECTRIC_LOSS_REVIEW_REQUIRED flag is important for transparent interpretation. The ratio between field-coupled and reference dielectric loss is slightly above the pre-defined review interval, but RUN010 reports 0 field-singularity cases. The observed dielectric-loss increase should therefore be discussed as a consequence of the resolved field distribution and parameter assumptions, not silently discarded.

## 4.5 Heat-source decomposition and contact degradation

The RUN010 heat-source decomposition separates conductor Joule heat, contact heat, and RIP dielectric loss. The conductor term follows the expected I^2 scaling, and the contact term follows I^2R_c by construction and by exported validation. This separation is essential because early diagnostic runs showed that an incorrect source selection can inflate the heat generation by including non-conductor regions or the contact layer in the conductor loss.

Contact resistance degradation is represented through a multiplier on the equivalent contact resistance. It is not a measured defect geometry or a claim about a specific failed bushing. Under this parameterization, high contact-resistance multipliers mainly raise Tmax_contact, while the global maximum may still be governed by the RIP/oil-side thermal environment in some cases. Figure 6 and supplementary validation figures show the source decomposition and the I^2R_c and I^2R checks.

The results therefore support a diagnostic interpretation: local current-carrying connection degradation can become thermally important even when the global temperature remains below the thermal-risk threshold. This is useful for screening, but it should be combined with field measurements or inspection data before being used for asset-specific decisions.

## 4.6 Mesh independence and sensitivity

RUN011A provides the mesh-independence evidence for the present steady risk scan. Using the fine mesh as reference, the medium mesh passes all representative cases, with maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. These small differences support the use of the medium mesh for the 125-case matrix, while the coarse mesh remains diagnostic only.

RUN011B shows that the most influential parameters in the one-factor sensitivity study are tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. The ranking is physically reasonable because tan(delta) and relative permittivity directly affect the dielectric-loss term, the baseline contact resistance controls localized contact heating, and the air-side heat-transfer coefficient influences the external heat-removal path. Figures 8 and 9 summarize the mesh and sensitivity evidence.

The sensitivity results also define where additional experimental or manufacturer-specific information would be most valuable. Better constraints on RIP dielectric loss tangent, relative permittivity, contact resistance, and air-side convection would reduce uncertainty in the predicted thermal margin more effectively than refining already weakly influential parameters.

## 4.7 Engineering implications and limitations

The simulation chain suggests that oil temperature, load current, contact degradation, and dielectric parameters jointly define the thermal margin of the 126 kV/1250 A RIP condenser bushing. High oil temperature reduces the baseline heat-removal capacity, high load increases both conductor and contact heating, and contact degradation creates a localized hotspot response. The field-coupled dielectric-loss term mainly affects the RIP region and remains an explicit review item because it exceeds the earlier average-field reference.

Several limitations should be kept in view. The model is two-dimensional and axisymmetric; it does not explicitly represent flange bolt holes, detailed three-dimensional terminal geometry, non-uniform contamination patterns, solid-fluid flow, or transient overload history. Air and oil are represented through convective boundary conditions rather than resolved fluid domains. The diagnostic risk zones are internal visualization classes, not standard limits or material lifetime criteria.

For these reasons, RUN010 should be treated as a validated numerical risk-boundary scan rather than as the final SCI conclusion. The next scientific step should combine material-parameter refinement, additional mesh or local-geometry checks where needed, and comparison with monitoring or publicly available measurement data before drawing field-operational conclusions.
