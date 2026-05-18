# Methods + Results Integrated Draft

## 3. Numerical Model and Simulation Setup

### 3.1 Geometry and bushing structure

The numerical object was a BRFGL1-126/1250-4 resin-impregnated paper (RIP) dry-type condenser transformer bushing rated at 126 kV and 1250 A. A two-dimensional axisymmetric finite-element model was established in the r-z coordinate system, with the air side located at positive z, the oil side located at negative z, and the grounded flange used as the central structural reference. The geometric dimensions and rated quantities are linked to the manufacturer drawing or catalog placeholder [REF_BRFG_DRAWING], and the bushing category and rating context should be supported by the relevant standard-scope citation [REF_IEC_60137].

The model separates the center conductor, terminal connector region, contact-resistance heat-source layer, RIP capacitor core, condenser screens, silicone-rubber external insulation, grounded flange metal, and oil-side shield or tapered region. The air-side external profile follows the CAD-constrained outline used in the project rather than a straight cylindrical simplification. The condenser screens are retained as named selections inside the RIP region, with S00 representing the high-voltage side and S10 representing the grounded screen. The modeling workflow, geometry abstraction, and audit path are summarized in Fig. 1.

The axisymmetric representation omits non-axisymmetric details such as flange bolt holes and local three-dimensional terminal features. This omission is a modeling limitation rather than a statement that these details are physically irrelevant. The present model is therefore intended for steady electro-thermal numerical screening and risk-boundary analysis, not for resolving local three-dimensional terminal or bolt stresses.

### 3.2 Material properties and boundary conditions

Materials are assigned to all solid regions used in the solver-oriented model, including the copper conductor, RIP capacitor core, aluminum condenser screens, silicone-rubber housing, flange metal, terminal connector, and contact heat-source layer. The parameter set combines public material information, drawing-based geometry, and documented engineering assumptions. The material choices and heat-transfer assumptions should be supported by public RIP-bushing thermal and material references [REF_RIP_BUSHING_THERMAL].

Air and transformer oil are not represented as volume fluid domains in the solver-oriented thermal model. Instead, they enter as external convective boundary conditions applied to explicitly identified solid boundaries. The air-side boundary covers the exposed external insulation and terminal surfaces, while the oil-side boundary covers immersed solid surfaces. Internal material interfaces, the symmetry axis, and internal flange contact interfaces are excluded from the convective boundary selections.

All formal material, heat-source, heat-transfer, and post-processing selections use explicit by-ID domain or boundary selections. This prevents coordinate-box drift and avoids reintroducing the selection ambiguity observed in early diagnostic stages. The stage audit table records this development path in Table 1, and the numerical quantities used later in the manuscript are indexed in Table 2.

### 3.3 Electro-thermal coupling formulation

The steady electro-thermal formulation combines conductor Joule heating, localized contact-resistance heating, and RIP dielectric loss. The conductor source follows the source-normalized I2R form, so that the integrated heat is consistent with the effective conductor resistance. The contact source is represented as a localized equivalent layer:

```text
Q_contact = I_case^2 R_c0 R_c_factor.
```

For the baseline contact multiplier R_c_factor = 1, the integrated contact heat is 1.5625 W. This term represents parameterized contact degradation and should not be interpreted as a measured defect.

The RIP dielectric-loss density is calculated from the electrostatic field solution:

```text
q_dielectric = omega epsilon_0 epsilon_r tan(delta) |E|^2.
```

This expression should be supported by a dielectric-loss theory reference [REF_DIELECTRIC_LOSS_THEORY]. The high-voltage boundary sets S00 to the phase-to-ground RMS voltage, while S10 and the flange are grounded. Screens S01-S09 are treated as floating condenser screens with zero net charge in the full field-coupled model, which requires support from condenser-bushing electrostatic modeling and COMSOL floating-potential documentation [REF_CONDENSER_BUSHING_ELECTROSTATICS; REF_COMSOL_FLOATING_POTENTIAL].

Because condenser-screen ends can create localized high-field values, the electric-field diagnostics include Emax_global, Emax_RIP, an edge-excluding RIP probe value, and E95_RIP. The 95th percentile and edge-excluding metrics are used to avoid interpreting a single numerical edge value as the dominant field indicator.

### 3.4 Operating condition matrix

The main risk scan is RUN010, a 5 x 5 x 5 steady operating matrix with 125 cases. The varied parameters are load multiplier [0.6, 0.8, 1.0, 1.2, 1.4], oil temperature [65, 75, 85, 95, 105] degC, and contact-resistance multiplier [1, 2, 5, 10, 20]. Voltage multiplier, air temperature, wind speed, dielectric-loss tangent multiplier, RIP aging-conductivity multiplier, and pollution multiplier are fixed in RUN010. This design isolates the thermal effects of load, oil temperature, and contact degradation while retaining field-coupled dielectric loss under a fixed voltage level.

The model sequence is part of the method. RUN006 corrected conductor and contact heat-source normalization, RUN007 and RUN008 checked solid-only behavior with an approximate dielectric-loss reference, RUN009 introduced field-coupled dielectric loss for the baseline and 27-case checks, and RUN010 extended the full field-coupled model to the 125-case risk matrix. RUN011 then evaluated mesh independence and material/boundary sensitivity. The validation evidence chain is summarized in Table 3.

### 3.5 Numerical verification strategy

The numerical verification strategy combines source normalization, heat-balance checks, explicit selection integrity, field-singularity screening, mesh convergence, and parameter sensitivity. RUN010 reports 125/125 overall valid cases, 125/125 valid heat-balance cases, 125/125 valid Joule/contact/dielectric-loss cases, and 0/125 field-singularity cases. The heat-balance residual remains within the accepted range, and all region-specific maxima are extracted from non-overlapping selections.

The field-coupled dielectric-loss review flag is intentionally retained. RUN010 reports dielectric_loss_review_required in 125/125 cases because the field-integrated RIP dielectric loss is higher than the earlier average-field reference, with a representative field/reference ratio of 11.020. This review flag is not a numerical failure, but it is a transparent uncertainty marker that should remain visible in the manuscript.

RUN011A compares coarse, medium, and fine meshes in representative cases. Using the fine mesh as the reference, the medium mesh passes all three representative comparisons, with maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. Mesh-convergence criteria should be supported by a finite-element verification citation [REF_MESH_CONVERGENCE]. RUN011B ranks the one-factor sensitivity as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. The mesh and sensitivity evidence are listed in Table 5 and Table 6.

## 4. Results and Discussion

### 4.1 Baseline electro-thermal field distribution

The baseline full electro-thermal calculation uses STEADY_1250_LOAD_1p0 with 1250 A current, 72.75 kV phase-to-ground RMS voltage, 85 degC oil temperature, 25 degC air temperature, and R_c_factor = 1. RUN009A is solved as valid and gives a global maximum temperature of 88.589 degC. The conductor, RIP, contact layer, silicone housing, and flange maxima are 74.136 degC, 88.589 degC, 58.790 degC, 57.215 degC, and 46.906 degC, respectively. The region-specific values are not identical, which confirms that the post-processing selections preserve physical region identity. The baseline potential, electric-field, dielectric-loss, and temperature indicators are shown in Fig. 2.

The heat-source decomposition gives 34.433 W of conductor Joule heat, 1.5625 W of contact heat, and 28.049 W of field-coupled RIP dielectric loss. The baseline heat-balance residual is -1.902%, which satisfies the numerical audit criterion. The key result summary in Table 2 provides the numeric source for the baseline and subsequent RUN010 discussion.

The field-coupled dielectric loss is higher than the approximate dielectric-loss reference used during early solid-only diagnostics. The field/reference ratio is 11.020, so the DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained. Because field_singularity_flag is false, this flag is interpreted as a dielectric-parameter and field-distribution review item rather than as a model failure.

### 4.2 Effects of load, oil temperature, and contact resistance

RUN010 extends the field-coupled formulation to 125 steady operating cases. Across the matrix, Tmax_global ranges from 67.397 degC to 134.974 degC, while Tmax_contact reaches a maximum of 129.925 degC. Fig. 3 presents the global temperature response, and Fig. 4 presents the corresponding contact-region response.

The trends are physically consistent. Increasing oil temperature raises the thermal baseline because the oil-side boundary becomes warmer. Increasing load raises conductor Joule heat approximately with I2 and also increases contact heat through the same current-squared dependence. Increasing the contact-resistance multiplier primarily affects the contact-layer maximum temperature, especially in high-load and high-oil-temperature cases.

The heat-source response underlying these trends is summarized for representative cases in Fig. 6. This decomposition is useful because it separates the current-driven conductor term, the contact-resistance term, and the voltage-driven field-coupled dielectric-loss contribution.

### 4.3 Diagnostic risk boundary analysis

The RUN010 global diagnostic risk-zone counts are 119 safe, 4 attention, 2 warning, and 0 thermal-risk cases. For the contact-region metric, the counts are 115 contact-safe, 6 contact-attention, 4 contact-warning, and 0 contact-risk cases. The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4.

These risk zones are internal diagnostic visualization classes. They are not IEC or IEEE standard limits, material lifetime thresholds, or guaranteed operating limits. A diagnostic-risk-method reference should be added to support the general concept of using risk classes for numerical screening while preserving this distinction [REF_RISK_DIAGNOSTIC_METHOD].

### 4.4 Contribution of field-coupled dielectric loss

RUN008 used an approximate dielectric-loss reference in the solid-only diagnostic model, whereas RUN010 uses the field-coupled loss integrated from the electrostatic solution. Replacing the reference loss with the field-coupled term increases Tmax_global by an average of 0.617 degC and a maximum of 2.816 degC. The risk zone changes in 2 of the 125 cases, as shown in Fig. 7.

This comparison supports a staged modeling interpretation. The approximate dielectric-loss reference was sufficient for early source-normalization and heat-balance debugging, but the full field-coupled model is more appropriate for the main risk matrix because it retains the spatial non-uniformity of the RIP electric field. The retained dielectric-loss review flag also prevents the field/reference difference from being hidden.

### 4.5 Heat-source decomposition and contact degradation

The heat-source decomposition confirms that conductor Joule heat follows the expected I2 scaling and that contact heat follows I2Rc. The supplementary validation figures report the contact I2Rc check and the Joule I2 scaling check, while Fig. 6 provides the representative-case decomposition used in the main text.

Contact-resistance degradation is modeled through the contact-resistance multiplier. It is a parameterized equivalent representation, not a measured defect geometry and not a claim about a specific failed bushing. Under this parameterization, high contact-resistance multipliers mainly raise Tmax_contact, although the global maximum can remain governed by the RIP/oil-side thermal environment in some parts of the matrix.

### 4.6 Mesh independence and parameter sensitivity

RUN011A supports the medium mesh used in the main risk scan. Relative to the fine mesh, the medium mesh has maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. The mesh-independence results are shown in Fig. 8 and summarized in Table 5.

RUN011B identifies the leading one-factor sensitivity order as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. This ranking is physically reasonable because dielectric loss is directly controlled by tan(delta) and relative permittivity, while contact resistance and air-side heat transfer influence localized heating and heat removal. The sensitivity ranking is shown in Fig. 9 and summarized in Table 6.

### 4.7 Engineering implications and limitations

The numerical results indicate that oil temperature, load current, contact-resistance degradation, and dielectric parameters jointly define the thermal margin of the 126 kV/1250 A RIP condenser bushing. High oil temperature reduces the margin available to the oil-side heat-removal path, high load increases current-driven heat sources, and contact degradation creates a localized hotspot response.

Several limitations remain. The model is two-dimensional and axisymmetric, so it does not explicitly resolve flange bolt holes, local three-dimensional terminal structures, non-uniform contamination, full solid-fluid flow, or transient overload history. Air and oil are represented through convective boundary conditions rather than CFD domains. The risk zones are diagnostic classes rather than standard limits. The risk boundary has not yet been validated against field monitoring or laboratory measurement data.

For these reasons, RUN010 should be treated as a validated finite-element numerical risk-boundary scan, not as a final operational rule. The next manuscript-development step should add externally verifiable references for geometry, standards, material properties, electrostatics, dielectric-loss theory, mesh convergence, and diagnostic-risk terminology before moving into the Introduction and literature review.

## Supplementary Figure Routing Note

Supplementary Fig. S1 documents the full run audit flow. Supplementary Fig. S2 verifies Qcontact against I2Rc, and Supplementary Fig. S3 verifies Qjoule against I2 scaling. Supplementary Fig. S4 reports the heat-balance residual distribution, Supplementary Fig. S5 summarizes the electric-field diagnostic checks, Supplementary Fig. S6 documents the field-to-reference dielectric-loss ratio, and Supplementary Fig. S7 gives detailed material-sensitivity responses.
