# 3. Numerical Model and Simulation Setup

## 3.1 Geometry and bushing structure

The numerical object was a BRFGL1-126/1250-4 resin-impregnated paper (RIP) dry-type condenser transformer bushing rated at 126 kV and 1250 A. A two-dimensional axisymmetric model was established in the r-z coordinate system, with the axial coordinate defined such that the air side is located at positive z, the oil side is located at negative z, and the grounded flange is used as the central structural reference. This representation follows the rotationally symmetric part of the bushing structure and provides a controlled basis for electrostatic and steady thermal calculations.

The model separates the main conductor, terminal connector region, contact-resistance heat-source layer, RIP capacitor core, condenser screens, silicone-rubber external insulation, grounded flange metal, and oil-side shield or tapered region. The external air-side profile was constrained by the available BRFGL1 drawing/CAD-derived outline rather than by a single straight cylinder, so that the air-side insulation envelope and the shed-equivalent outer contour are retained for heat-transfer and figure-review purposes. The condenser screens were generated as named, parameterized selections inside the RIP core, with S00 representing the high-voltage screen or conductor side and S10 representing the grounded screen.

The two-dimensional model deliberately omits non-axisymmetric details such as flange bolt holes and local three-dimensional terminal features. These features are not ignored physically; rather, they are outside the scope of the axisymmetric finite-element representation used for the present steady electro-thermal risk scan. Their omission should be considered when interpreting highly localized terminal or flange effects. Suggested citation positions for this paragraph are the manufacturer drawing or catalog entry used for BRFGL1 dimensions and the applicable IEC 60137 scope statement.

## 3.2 Material parameters and boundary conditions

Materials were assigned to all solid regions used in the solver-oriented model, including the copper conductor, RIP capacitor core, aluminum condenser screens, silicone-rubber housing, flange metal, terminal connector, and contact heat-source layer. The material set was assembled from public material references, manufacturer/drawing information, and explicitly documented engineering assumptions. Parameters with higher uncertainty, especially RIP dielectric properties, heat-transfer coefficients, and contact resistance, were later examined in the RUN011 material and boundary sensitivity analysis.

Air and transformer oil were not modeled as volume fluid domains in the solver-oriented thermal model. Instead, they were imposed as external convective boundary conditions on explicitly identified air-side and oil-side solid surfaces. This choice avoids artificial solid/fluid overlap and keeps the thermal audit focused on heat generation, heat removal, and region-specific maximum temperatures. The air-side boundary includes the exposed external insulation and terminal surfaces, while the oil-side boundary includes the immersed solid surfaces. Internal material interfaces, the symmetry axis, and internal flange contact interfaces are excluded from the convection selections.

All formal material and boundary assignments used explicit by-ID domain and boundary selections. This was adopted after early geometry-only and coordinate-box selection tests showed that source normalization and boundary drift can dominate the thermal response if selections are ambiguous. The by-ID interface therefore became part of the numerical verification chain rather than a plotting convenience. Source and assumption details are recorded in the project traceability documents and in the manuscript-ready validation tables.

## 3.3 Electro-thermal coupling formulation

The steady electro-thermal model combines conductor Joule heating, contact-resistance heating, and field-coupled dielectric loss in the RIP region. The conductor heat source follows the source-normalized form based on the effective conductor resistance, so that the integrated Joule heat is consistent with I^2R. The contact heat source is treated as a localized equivalent layer and is constrained by

```text
Q_contact = I_case^2 R_c0 R_c_factor.
```

For the baseline case with R_c_factor = 1, the integrated contact heat is therefore 1.5625 W. This contact model should be interpreted as a parameterized equivalent degradation model rather than as a measured defect.

The RIP dielectric loss is calculated from the electric-field solution rather than from an average-field reference heat source:

```text
q_dielectric = omega epsilon_0 epsilon_r tan(delta) |E|^2.
```

The electrostatic boundary conditions set S00 to the phase-to-ground RMS voltage, set S10 and the flange to ground, and treat S01-S09 as floating-potential screens with zero net charge in the full field-coupled model. Because screen ends can introduce numerical field spikes, the electric-field diagnostics include the global maximum, the RIP-domain maximum, an edge-excluding RIP probe value, and the 95th percentile RIP field. The latter two indicators are used to prevent a single-point edge value from controlling the dielectric-loss interpretation.

The thermal problem is solved as a steady heat-conduction equation with volumetric sources from the conductor, contact layer, and RIP dielectric loss, and convective or flange heat-removal terms on the verified external boundaries. The field-coupled dielectric-loss term is transferred to the thermal model after the electrostatic field calculation. This formulation is a finite-element numerical simulation workflow, not a physical experimental validation.

## 3.4 Operating condition matrix

The main risk scan is RUN010, a 5 x 5 x 5 steady matrix with 125 operating cases. The varied parameters are load multiplier [0.6, 0.8, 1.0, 1.2, 1.4], oil temperature [65, 75, 85, 95, 105] degC, and contact-resistance multiplier [1, 2, 5, 10, 20]. The voltage multiplier, air temperature, wind speed, dielectric-loss tangent multiplier, RIP aging-conductivity multiplier, and pollution multiplier are fixed in RUN010. The fixed-voltage setting allows the field-coupled dielectric-loss term to be isolated from the thermal effects of load, oil temperature, and contact degradation.

The model development sequence is important for interpreting the matrix. RUN006 first fixed the conductor and contact heat-source normalization in a solid-only thermal diagnostic model. RUN007 and RUN008 then checked 27-case and 125-case solid-only behavior using an approximate dielectric-loss reference. RUN009 replaced that reference with field-coupled dielectric loss and confirmed the baseline and 27-case behavior. RUN010 is therefore the first 125-case matrix using the full field-coupled dielectric-loss term, while RUN011 checks mesh independence and material/boundary robustness.

## 3.5 Numerical verification strategy

The verification strategy was organized as an audit chain rather than as a single end-point calculation. First, source normalization was checked so that conductor Joule heating followed I^2R and contact heating followed I^2R_c. Second, heat-balance diagnostics were exported for each case, with a strict residual criterion and a low-power reclassification rule used only when the absolute residual was small relative to the relevant energy scale. Third, explicit by-ID domain and boundary selections were used for materials, heat sources, heat-transfer boundaries, and post-processing maxima.

The full field-coupled stage added electric-field diagnostics and dielectric-loss review flags. In RUN010, 125/125 cases were overall valid, 0 cases had a field-singularity flag, and 125/125 cases retained the dielectric-loss review flag because the field-integrated RIP loss was higher than the earlier average-field reference. This review flag is reported as a model-interpretation item, not as a numerical failure.

Finally, RUN011A compared coarse, medium, and fine meshes for representative cases. The medium mesh passed against the fine reference in 3/3 comparisons, with maximum medium-versus-fine errors of 0.355% for global maximum temperature, 0.002% for E95_RIP, and 0.002% for RIP dielectric loss. RUN011B then performed one-factor sensitivity checks, ranking the most influential parameters as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. These steps verify numerical stability and parameter robustness, but they do not replace future comparison with physical measurements.
