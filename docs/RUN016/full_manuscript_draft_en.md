# Title Options

1. Electro-Thermal Coupled Finite-Element Diagnostic Risk-Boundary Simulation of a 126 kV/1250 A RIP Condenser Transformer Bushing under Contact-Resistance Degradation
2. Numerical Screening of Contact-Resistance Degradation in a 126 kV/1250 A RIP Condenser Transformer Bushing Using Field-Coupled Electro-Thermal Finite-Element Simulation
3. Field-Coupled Dielectric-Loss and Contact-Degradation Effects in a 126 kV/1250 A RIP Condenser Transformer Bushing: A Finite-Element Diagnostic Risk-Boundary Study

# Abstract

This study develops a staged electro-thermal coupled finite-element model for a 126 kV/1250 A resin-impregnated paper (RIP) condenser transformer bushing under load, oil-temperature, and contact-resistance degradation conditions. The workflow normalizes conductor Joule heating and contact heating, introduces field-coupled RIP dielectric loss, and audits heat balance, by-ID selections, electric-field singularity, mesh convergence, and material/boundary sensitivity. The main RUN010 matrix contains 125 steady cases. Across this matrix, Tmax_global_C ranges from 67.397-134.974 degC, and Tmax_contact_C reaches 129.925 degC. The global diagnostic risk-zone counts are safe 119, attention 4, warning 2, and thermal-risk 0. The contact-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, and contact-risk 0. The field-coupled dielectric-loss review flag is retained because the field/reference ratio is 11.020, while field_singularity_flag is 0/125. Mesh verification gives 0.355% maximum medium-vs-fine Tmax error, and the sensitivity ranking is tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. The results are finite-element numerical screening evidence, not laboratory or field validation; the diagnostic risk zones are internal screening classes, not standard limits.

# Keywords

RIP condenser bushing; transformer bushing; electro-thermal coupling; finite-element simulation; contact-resistance degradation; field-coupled dielectric loss; diagnostic risk boundary; mesh convergence

# 1. Introduction

High-voltage transformer bushings provide the electrical and mechanical transition between grounded transformer tanks and energized conductors. For a 126 kV/1250 A resin-impregnated paper (RIP) condenser transformer bushing, the thermal margin is shaped by the rated-current path, the condenser-core electric field, the oil-side thermal environment, and the air-side cooling condition. The geometry and rated context of the BRFGL1-126/1250-4 bushing should be supported by the controlled drawing or catalog source [REF_BRFG_DRAWING], while the general bushing rating and standard-scope background should be linked to the appropriate IEC reference [REF_IEC_60137].

RIP condenser bushings are attractive because the condenser core can distribute the electric field through a graded screen structure, but this same structure makes the thermal problem inherently multi-source. Current-driven conductor loss, contact-resistance heating at current-carrying joints, field-dependent dielectric loss in the RIP core, transformer-oil temperature, air-side convection, and material properties all contribute to the steady temperature field. Previous bushing thermal and electro-thermal studies provide the basis for treating these effects with finite-element or coupled numerical models [REF_RIP_BUSHING_THERMAL; REF_CONDENSER_BUSHING_ELECTROSTATICS].

Two modeling choices are particularly important for diagnostic risk-boundary simulation. First, contact resistance should be represented as an equivalent parameter rather than as an unverified measured defect, because the actual internal connection state is usually not directly observable. Second, RIP dielectric loss should not be restricted to a spatially averaged reference field when a resolved electric-field solution is available. The field-coupled loss density, q_dielectric = omega epsilon0 epsr tan(delta)|E|^2, provides a direct route from the electrostatic solution to the thermal source term, but it also requires careful interpretation of dielectric parameters and screen-end field localization [REF_DIELECTRIC_LOSS_THEORY].

The present work therefore develops a staged finite-element numerical screening workflow for a 126 kV/1250 A RIP condenser bushing. The study does not claim physical experimental validation, field monitoring validation, or an external operating threshold. Instead, it constructs an auditable diagnostic risk-boundary model: RUN006 fixes conductor and contact heat-source normalization; RUN007-RUN008 test solid-only thermal behavior; RUN009 introduces field-coupled dielectric loss; RUN010 evaluates a 125-case operating matrix; and RUN011 checks mesh independence and parameter sensitivity. The diagnostic risk zones used later are internal screening classes and should not be interpreted as standard temperature limits, material lifetime thresholds, or operational guarantees [REF_RISK_DIAGNOSTIC_METHOD].

The main contributions are as follows. First, the work establishes a CAD-constrained, explicit-selection, two-dimensional axisymmetric finite-element model for the selected 126 kV/1250 A RIP condenser bushing. Second, it replaces an average-field dielectric-loss reference with field-coupled dielectric-loss integration while retaining a transparent DIELECTRIC_LOSS_REVIEW_REQUIRED flag. Third, it quantifies how load multiplier, oil temperature, and contact-resistance multiplier reshape global and contact-region temperature indicators across a 125-case diagnostic matrix. Fourth, it locks each numerical claim to raw result files, manuscript figures, and tables so that subsequent manuscript assembly can separate confirmed simulation evidence from reference items that still need manual verification.

# 2. Literature Review

## 2.1 Thermal and electro-thermal modeling of transformer bushings

Transformer-bushing thermal analysis has been studied using thermal-network models, two-dimensional finite-element models, and three-dimensional electromagnetic-fluid-thermal models. These studies motivate the treatment of current loading, oil temperature, ambient cooling, and local hotspot formation as coupled numerical factors rather than independent scalar corrections [REF_RIP_BUSHING_THERMAL]. For the present 126 kV/1250 A bushing, this literature supports the use of finite-element numerical simulation as a screening tool, while also reminding readers that three-dimensional flow and local terminal details remain limitations when a two-dimensional axisymmetric model is used.

## 2.2 Contact-resistance degradation and localized heating

Current-carrying connections can become localized thermal sources when the equivalent contact resistance increases. Prior contact-degradation and current-carrying-defect studies motivate the use of a contact-resistance multiplier, but they do not allow this project to claim that a measured defect was reproduced. In this manuscript, contact degradation is therefore treated as a parameterized equivalent model. This boundary is important because the RUN010 matrix evaluates thermal response to assumed contact-resistance multipliers rather than to inspected or measured physical defects [REF_RIP_BUSHING_THERMAL; REF_RISK_DIAGNOSTIC_METHOD].

## 2.3 RIP dielectric response and field-coupled dielectric loss

The dielectric response of epoxy- or resin-impregnated paper depends on permittivity, loss tangent, temperature, frequency, and aging-related material state. A resolved electrostatic field can therefore change the spatial distribution of dielectric heat generation relative to an average-field reference. The present model uses the field-coupled dielectric-loss expression in the RIP region and reports both field-based and reference-based dielectric-loss values. The dielectric_loss_review_required flag is retained because the field/reference ratio exceeds the initial review interval; this is a transparent uncertainty marker rather than a failure of the numerical run [REF_DIELECTRIC_LOSS_THEORY].

## 2.4 Condenser screens and electrostatic field representation

Condenser bushings use graded conductive screens to control electric-field distribution. Modeling these screens requires a consistent electrostatic boundary strategy: the high-voltage and grounded screens can be assigned fixed potentials, while intermediate condenser screens should not be forced to arbitrary fixed values if the intended physics is floating charge balance. The present model therefore treats S00 as high voltage, S10 and the flange as grounded, and S01-S09 as floating condenser screens in the full field-coupled stage. The physical rationale should be supported by condenser-bushing electrostatics literature, and the implementation should be checked against official COMSOL floating-potential documentation [REF_CONDENSER_BUSHING_ELECTROSTATICS; REF_COMSOL_FLOATING_POTENTIAL].

## 2.5 Numerical verification, mesh convergence, and diagnostic risk zoning

Numerical risk-boundary studies require more than a solved temperature field. They need source-normalization checks, heat-balance checks, selection-integrity checks, electric-field singularity screening, mesh convergence evidence, and sensitivity analysis. RUN011A provides the mesh-convergence evidence used in the present work, while RUN011B identifies the most influential material and boundary assumptions. External mesh-convergence and diagnostic-risk-method references are still needed to support the general verification language and risk-zoning terminology [REF_MESH_CONVERGENCE; REF_RISK_DIAGNOSTIC_METHOD].

## 2.6 Gap addressed by the present study

Existing bushing studies provide strong foundations for thermal modeling, electro-thermal coupling, dielectric response, and contact-defect diagnosis, but the manuscript-ready gap addressed here is narrower: an auditable, source-normalized, field-coupled finite-element screening workflow for a 126 kV/1250 A RIP condenser transformer bushing, with each numerical conclusion locked to raw result files and each literature-dependent statement retained as a reference placeholder until manually confirmed. This structure is intended to make the manuscript safer to assemble, not to overstate the simulation as a measured or field-confirmed operating rule.

# 3. Numerical Model and Simulation Setup

## 3.1 Geometry and bushing structure

The numerical object was a BRFGL1-126/1250-4 resin-impregnated paper (RIP) dry-type condenser transformer bushing rated at 126 kV and 1250 A. A two-dimensional axisymmetric finite-element model was established in the r-z coordinate system, with the air side located at positive z, the oil side located at negative z, and the grounded flange used as the central structural reference. The geometric dimensions and rated quantities are linked to the manufacturer drawing or catalog placeholder [REF_BRFG_DRAWING], and the bushing category and rating context should be supported by the relevant standard-scope citation [REF_IEC_60137].

The model separates the center conductor, terminal connector region, contact-resistance heat-source layer, RIP capacitor core, condenser screens, silicone-rubber external insulation, grounded flange metal, and oil-side shield or tapered region. The air-side external profile follows the CAD-constrained outline used in the project rather than a straight cylindrical simplification. The condenser screens are retained as named selections inside the RIP region, with S00 representing the high-voltage side and S10 representing the grounded screen. The modeling workflow, geometry abstraction, and audit path are summarized in Fig. 1.

The axisymmetric representation omits non-axisymmetric details such as flange bolt holes and local three-dimensional terminal features. This omission is a modeling limitation rather than a statement that these details are physically irrelevant. The present model is therefore intended for steady electro-thermal numerical screening and risk-boundary analysis, not for resolving local three-dimensional terminal or bolt stresses.

## 3.2 Material properties and boundary conditions

Materials are assigned to all solid regions used in the solver-oriented model, including the copper conductor, RIP capacitor core, aluminum condenser screens, silicone-rubber housing, flange metal, terminal connector, and contact heat-source layer. The parameter set combines public material information, drawing-based geometry, and documented engineering assumptions. The material choices and heat-transfer assumptions should be supported by public RIP-bushing thermal and material references [REF_RIP_BUSHING_THERMAL].

Air and transformer oil are not represented as volume fluid domains in the solver-oriented thermal model. Instead, they enter as external convective boundary conditions applied to explicitly identified solid boundaries. The air-side boundary covers the exposed external insulation and terminal surfaces, while the oil-side boundary covers immersed solid surfaces. Internal material interfaces, the symmetry axis, and internal flange contact interfaces are excluded from the convective boundary selections.

All formal material, heat-source, heat-transfer, and post-processing selections use explicit by-ID domain or boundary selections. This prevents coordinate-box drift and avoids reintroducing the selection ambiguity observed in early diagnostic stages. The stage audit table records this development path in Table 1, and the numerical quantities used later in the manuscript are indexed in Table 2.

## 3.3 Electro-thermal coupling formulation

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

## 3.4 Operating condition matrix

The main risk scan is RUN010, a 5 x 5 x 5 steady operating matrix with 125 cases. The varied parameters are load multiplier [0.6, 0.8, 1.0, 1.2, 1.4], oil temperature [65, 75, 85, 95, 105] degC, and contact-resistance multiplier [1, 2, 5, 10, 20]. Voltage multiplier, air temperature, wind speed, dielectric-loss tangent multiplier, RIP aging-conductivity multiplier, and pollution multiplier are fixed in RUN010. This design isolates the thermal effects of load, oil temperature, and contact degradation while retaining field-coupled dielectric loss under a fixed voltage level.

The model sequence is part of the method. RUN006 corrected conductor and contact heat-source normalization, RUN007 and RUN008 checked solid-only behavior with an approximate dielectric-loss reference, RUN009 introduced field-coupled dielectric loss for the baseline and 27-case checks, and RUN010 extended the full field-coupled model to the 125-case risk matrix. RUN011 then evaluated mesh independence and material/boundary sensitivity. The validation evidence chain is summarized in Table 3.

## 3.5 Numerical verification strategy

The numerical verification strategy combines source normalization, heat-balance checks, explicit selection integrity, field-singularity screening, mesh convergence, and parameter sensitivity. RUN010 reports 125/125 overall valid cases, 125/125 valid heat-balance cases, 125/125 valid Joule/contact/dielectric-loss cases, and 0/125 field-singularity cases. The heat-balance residual remains within the accepted range, and all region-specific maxima are extracted from non-overlapping selections.

The field-coupled dielectric-loss review flag is intentionally retained. RUN010 reports dielectric_loss_review_required in 125/125 cases because the field-integrated RIP dielectric loss is higher than the earlier average-field reference, with a representative field/reference ratio of 11.020. This review flag is not a numerical failure, but it is a transparent uncertainty marker that should remain visible in the manuscript.

RUN011A compares coarse, medium, and fine meshes in representative cases. Using the fine mesh as the reference, the medium mesh passes all three representative comparisons, with maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. Mesh-convergence criteria should be supported by a finite-element verification citation [REF_MESH_CONVERGENCE]. RUN011B ranks the one-factor sensitivity as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. The mesh and sensitivity evidence are listed in Table 5 and Table 6.

# 4. Results and Discussion

## 4.1 Baseline electro-thermal field distribution

The baseline full electro-thermal calculation uses STEADY_1250_LOAD_1p0 with 1250 A current, 72.75 kV phase-to-ground RMS voltage, 85 degC oil temperature, 25 degC air temperature, and R_c_factor = 1. RUN009A is solved as valid and gives a global maximum temperature of 88.589 degC. The conductor, RIP, contact layer, silicone housing, and flange maxima are 74.136 degC, 88.589 degC, 58.790 degC, 57.215 degC, and 46.906 degC, respectively. The region-specific values are not identical, which confirms that the post-processing selections preserve physical region identity. The baseline potential, electric-field, dielectric-loss, and temperature indicators are shown in Fig. 2.

The heat-source decomposition gives 34.433 W of conductor Joule heat, 1.5625 W of contact heat, and 28.049 W of field-coupled RIP dielectric loss. The baseline heat-balance residual is -1.902%, which satisfies the numerical audit criterion. The key result summary in Table 2 provides the numeric source for the baseline and subsequent RUN010 discussion. The RUN010 heat balance max residual is 2.678%.

Evidence-lock summary: RUN010 reports 0/125 field_singularity_flag cases and 125/125 dielectric_loss_review_required cases; RUN010 contact risk-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0.

The field-coupled dielectric loss is higher than the approximate dielectric-loss reference used during early solid-only diagnostics. The field/reference ratio is 11.020, so the DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained. Because field_singularity_flag is false, this flag is interpreted as a dielectric-parameter and field-distribution review item rather than as a model failure.

## 4.2 Effects of load, oil temperature, and contact resistance

RUN010 extends the field-coupled formulation to 125 steady operating cases. Across the matrix, Tmax_global ranges from 67.397 degC to 134.974 degC, while Tmax_contact reaches a maximum of 129.925 degC. Fig. 3 presents the global temperature response, and Fig. 4 presents the corresponding contact-region response.

The trends are physically consistent. Increasing oil temperature raises the thermal baseline because the oil-side boundary becomes warmer. Increasing load raises conductor Joule heat approximately with I2 and also increases contact heat through the same current-squared dependence. Increasing the contact-resistance multiplier primarily affects the contact-layer maximum temperature, especially in high-load and high-oil-temperature cases.

The heat-source response underlying these trends is summarized for representative cases in Fig. 6. This decomposition is useful because it separates the current-driven conductor term, the contact-resistance term, and the voltage-driven field-coupled dielectric-loss contribution.

## 4.3 Diagnostic risk boundary analysis

The RUN010 global diagnostic risk-zone counts are 119 safe, 4 attention, 2 warning, and 0 thermal-risk cases. For the contact-region metric, the counts are 115 contact-safe, 6 contact-attention, 4 contact-warning, and 0 contact-risk cases. The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4.

These risk zones are internal diagnostic visualization classes. They are not IEC or IEEE standard limits, material lifetime thresholds, or guaranteed operating limits. A diagnostic-risk-method reference should be added to support the general concept of using risk classes for numerical screening while preserving this distinction [REF_RISK_DIAGNOSTIC_METHOD].

## 4.4 Contribution of field-coupled dielectric loss

RUN008 used an approximate dielectric-loss reference in the solid-only diagnostic model, whereas RUN010 uses the field-coupled loss integrated from the electrostatic solution. Replacing the reference loss with the field-coupled term increases Tmax_global by an average of 0.617 degC and a maximum of 2.816 degC. The risk zone changes in 2 of the 125 cases, as shown in Fig. 7.

This comparison supports a staged modeling interpretation. The approximate dielectric-loss reference was sufficient for early source-normalization and heat-balance debugging, but the full field-coupled model is more appropriate for the main risk matrix because it retains the spatial non-uniformity of the RIP electric field. The retained dielectric-loss review flag also prevents the field/reference difference from being hidden.

## 4.5 Heat-source decomposition and contact degradation

The heat-source decomposition confirms that conductor Joule heat follows the expected I2 scaling and that contact heat follows I2Rc. The supplementary validation figures report the contact I2Rc check and the Joule I2 scaling check, while Fig. 6 provides the representative-case decomposition used in the main text.

Contact-resistance degradation is modeled through the contact-resistance multiplier. It is a parameterized equivalent representation, not a measured defect geometry and not a claim about a specific failed bushing. Under this parameterization, high contact-resistance multipliers mainly raise Tmax_contact, although the global maximum can remain governed by the RIP/oil-side thermal environment in some parts of the matrix.

## 4.6 Mesh independence and parameter sensitivity

RUN011A supports the medium mesh used in the main risk scan. Relative to the fine mesh, the medium mesh has maximum errors of 0.355% for Tmax_global, 0.002% for E95_RIP, and 0.002% for field-coupled RIP dielectric loss. The mesh-independence results are shown in Fig. 8 and summarized in Table 5.

RUN011B identifies the leading one-factor sensitivity order as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil. This ranking is physically reasonable because dielectric loss is directly controlled by tan(delta) and relative permittivity, while contact resistance and air-side heat transfer influence localized heating and heat removal. The sensitivity ranking is shown in Fig. 9 and summarized in Table 6.

## 4.7 Engineering implications and limitations

The numerical results indicate that oil temperature, load current, contact-resistance degradation, and dielectric parameters jointly define the thermal margin of the 126 kV/1250 A RIP condenser bushing. High oil temperature reduces the margin available to the oil-side heat-removal path, high load increases current-driven heat sources, and contact degradation creates a localized hotspot response.

Several limitations remain. The model is two-dimensional and axisymmetric, so it does not explicitly resolve flange bolt holes, local three-dimensional terminal structures, non-uniform contamination, full solid-fluid flow, or transient overload history. Air and oil are represented through convective boundary conditions rather than CFD domains. The risk zones are diagnostic classes rather than standard limits. The risk boundary has not yet been validated against field monitoring or laboratory measurement data.

For these reasons, RUN010 should be treated as a validated finite-element numerical risk-boundary scan, not as a final operational rule. The next manuscript-development step should add externally verifiable references for geometry, standards, material properties, electrostatics, dielectric-loss theory, mesh convergence, and diagnostic-risk terminology before moving into the Introduction and literature review.

# 5. Limitations and Future Work

The present manuscript is based on a finite-element numerical screening workflow. The most important limitation is the two-dimensional axisymmetric representation. It captures the axisymmetric current path, RIP core, condenser screens, external insulation envelope, flange region, and oil-side region, but it does not explicitly resolve local three-dimensional terminal details, flange bolt holes, or asymmetric connection features.

Air and oil are represented through boundary heat-transfer conditions rather than resolved CFD fluid domains. This choice keeps the heat-balance audit transparent, but it also means that local oil-flow, air-flow, and buoyancy effects are not directly solved. The present matrix is also steady-state; transient overload history, annual weather sequences, and time-dependent thermal inertia are outside RUN010.

No laboratory, field-monitoring, or physical prototype validation has been completed in the current project stage. The RUN010 risk boundary is therefore a numerical screening result, not an operational rule. The diagnostic risk zones are internal screening classes and not standard limits, material lifetime thresholds, or safety guarantees. The contact-resistance multiplier is a parameterized equivalent model, not a measured defect or asset-specific diagnosis.

The field-coupled dielectric-loss calculation remains transparent about uncertainty. DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required is retained because the field-integrated RIP dielectric loss exceeds the average-field reference. Future work should verify dielectric parameters, field interpretation, contact-resistance assumptions, and convective heat-transfer coefficients against stronger material data, manufacturer data, monitoring records, or targeted experiments. Reference placeholders also remain unresolved or partially resolved and require manual verification before submission.


# 6. Conclusions

1. A staged finite-element numerical screening workflow was assembled for a 126 kV/1250 A RIP condenser transformer bushing, with source normalization, by-ID selections, heat-balance checks, field diagnostics, mesh convergence, and parameter sensitivity retained as audit steps.
2. The RUN009A baseline gives 88.589 degC global maximum temperature and 28.049 W field-coupled RIP dielectric loss, with a field/reference ratio of 11.020. The DIELECTRIC_LOSS_REVIEW_REQUIRED flag is retained and interpreted as a review item rather than a failed run.
3. In the RUN010 125-case matrix, Tmax_global_C ranges from 67.397-134.974 degC and Tmax_contact_C reaches 129.925 degC.
4. RUN010 global diagnostic risk-zone counts are safe 119, attention 4, warning 2, thermal-risk 0, while contact-zone counts are contact_safe 115, contact_attention 6, contact_warning 4, contact-risk 0. These classes are diagnostic screening categories, not standard limits.
5. Replacing the approximate dielectric-loss reference with field-coupled dielectric loss changes Tmax_global by 0.617 degC mean delta_Tmax and 2.816 degC max delta_Tmax, with 2/125 changed risk zones.
6. RUN011A supports the medium mesh with 0.355% max Tmax mesh error, 0.002% max E95 mesh error, and 0.002% max Qdielectric mesh error.
7. RUN011B ranks sensitivity as tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil, indicating that dielectric parameters, contact resistance, and air-side heat transfer deserve priority in future verification.


# References Placeholder List

No formal bibliography is fabricated in this draft. Each placeholder below must be resolved or manually confirmed before submission.

| placeholder | source_status | confidence | required action |
|---|---|---|---|
| [REF_BRFG_DRAWING] | LOCAL_FILE_FOUND_NEEDS_MANUFACTURER_METADATA_CONFIRMATION | medium | manual verification required before submission |
| [REF_IEC_60137] | TRACEABILITY_RECORD_EXISTS_NEEDS_STANDARD_TEXT_CONFIRMATION | medium-low | manual verification required before submission |
| [REF_RIP_BUSHING_THERMAL] | LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION | medium | manual verification required before submission |
| [REF_DIELECTRIC_LOSS_THEORY] | PARTIALLY_RESOLVED_WITH_LOCAL_PDFS_NEEDS_THEORY_REFERENCE_CONFIRMATION | medium-low | manual verification required before submission |
| [REF_CONDENSER_BUSHING_ELECTROSTATICS] | LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION | medium | manual verification required before submission |
| [REF_COMSOL_FLOATING_POTENTIAL] | UNRESOLVED | low | manual verification required before submission |
| [REF_MESH_CONVERGENCE] | UNRESOLVED | low | manual verification required before submission |
| [REF_RISK_DIAGNOSTIC_METHOD] | PARTIALLY_RESOLVED_WITH_LOCAL_APPLICATION_PDFS_NEEDS_METHOD_REFERENCE | medium-low | manual verification required before submission |

# Figure Captions

**Fig. 1. Model workflow and CAD-constrained axisymmetric geometry.** The workflow links geometry construction, explicit domain/boundary selection, source normalization, full field-coupled dielectric-loss calculation, 125-case risk scanning, mesh independence, and material/boundary sensitivity. The geometry panel summarizes the axisymmetric representation of the BRFGL1-126/1250-4 bushing, including the air-side external insulation, flange, oil-side region, RIP core, condenser screens, center conductor, and contact heat-source layer.

**Fig. 2. Baseline electro-thermal field distribution for STEADY_1250_LOAD_1p0.** The panels report the baseline potential/electric-field indicators, RIP dielectric-loss density, and steady temperature response from RUN009A. The calculation uses field-coupled dielectric loss and explicit by-ID selections.

**Fig. 3. RUN010 global maximum-temperature heatmap.** Global maximum temperature is shown over the 5 x 5 x 5 load, oil-temperature, and contact-resistance matrix. The diagnostic safe, attention, warning, and thermal-risk zones are visualization classes only and are not IEC/IEEE limits.

**Fig. 4. RUN010 contact-region maximum-temperature heatmap.** Contact-layer temperature is shown over the same operating matrix to highlight the local response to the contact-resistance multiplier.

**Fig. 5. Diagnostic safe-load boundary by oil temperature and contact-resistance multiplier.** The boundary summarizes the highest load multiplier remaining in the diagnostic safe zone for each oil-temperature and contact-resistance pair.

**Fig. 6. Heat-source decomposition for representative RUN010 cases.** Conductor Joule heat, contact heat, and RIP dielectric loss are compared for low-risk, baseline, high-contact-risk, and highest-pressure operating cases.

**Fig. 7. Difference between RUN008 approximate and RUN010 field-coupled dielectric-loss models.** The figure reports the temperature change after replacing approximate_Qdielectric_ref with field-coupled dielectric loss from the electrostatic solution.

**Fig. 8. Mesh-independence summary.** Coarse, medium, and fine meshes are compared for representative cases, with the fine mesh used as the reference and the medium mesh used for the main risk scan.

**Fig. 9. Material and boundary sensitivity ranking.** One-factor sensitivity indices identify the dominant uncertainty sources affecting maximum temperature and dielectric-loss-related outputs.

# Table Captions

**Table 1. Stage audit summary from RUN001 to RUN012B.** This table records the purpose, model type, case count, key outputs, validation status, and manuscript role of each modeling stage.

**Table 2. Key numerical result summary for manuscript use.** This table lists the main quantitative values used in the text, including baseline temperature, dielectric loss, RUN010 temperature ranges, risk-zone counts, RUN008-RUN010 differences, mesh errors, and sensitivity ranking.

**Table 3. Model validation evidence chain.** This table maps each validation item to the relevant run, evidence file, pass criterion, and manuscript interpretation.

**Table 4. RUN010 diagnostic risk-boundary summary.** This table reports the maximum safe load and transition loads for each oil-temperature and contact-resistance multiplier combination. The thresholds are diagnostic visualization classes only.

**Table 5. RUN011A mesh-independence summary.** This table compares coarse, medium, and fine meshes for representative cases and reports temperature, electric-field, dielectric-loss, heat-balance, and singularity-check metrics.

**Table 6. RUN011B material and boundary sensitivity summary.** This table reports one-factor perturbation results and sensitivity indices for RIP thermal, dielectric, contact-resistance, and heat-transfer parameters.

# Supplementary Material Note

The following supplementary figures are routed as validation and audit material rather than as main conclusions:

- Fig. S1: Full run audit flow. Source: `results/paper_figures/manuscript_ready/FigS1_full_run_audit_flow.png`.
- Fig. S2: Qcontact I2Rc validation. Source: `results/paper_figures/manuscript_ready/FigS2_Qcontact_I2Rc_validation.png`.
- Fig. S3: Qjoule I2 scaling validation. Source: `results/paper_figures/manuscript_ready/FigS3_Qjoule_I2_scaling_validation.png`.
- Fig. S4: Heat balance residual distribution. Source: `results/paper_figures/manuscript_ready/FigS4_heat_balance_residual_distribution.png`.
- Fig. S5: Electric-field diagnostic summary. Source: `results/paper_figures/manuscript_ready/FigS5_Efield_diagnostic_summary.png`.
- Fig. S6: Dielectric loss field-to-ref ratio. Source: `results/paper_figures/manuscript_ready/FigS6_dielectric_loss_field_to_ref_ratio.png`.
- Fig. S7: Material sensitivity each parameter. Source: `results/paper_figures/manuscript_ready/FigS7_material_sensitivity_each_parameter.png`.
