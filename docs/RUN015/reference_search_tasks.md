# RUN015 Reference Search Tasks

These tasks are for manual follow-up or a later verified online/reference-manager workflow. No bibliography entry is fabricated in RUN015.

## [REF_BRFG_DRAWING]

- Search target: Verify the BRFGL1-126/1250-4 drawing/catalog source.
- Recommended keywords: `BRFGL1-126/1250-4 RIP bushing 126 kV 1250 A drawing, transformer bushing catalog BRFGL1`
- Acceptance criteria: A manufacturer-controlled drawing/catalog or project-authorized CAD file with model name and dimensions.
- Rejection criteria: Unlabeled images, copied screenshots without provenance, or dimensions not matching the selected model.
- Sentence to support: The numerical object was a BRFGL1-126/1250-4 RIP dry-type condenser transformer bushing rated at 126 kV and 1250 A.
- RUN015 status: LOCAL_FILE_FOUND_NEEDS_MANUFACTURER_METADATA_CONFIRMATION

## [REF_IEC_60137]

- Search target: Confirm IEC 60137 scope/rating language.
- Recommended keywords: `IEC 60137 insulated bushings scope rated voltage current transformer bushings`
- Acceptance criteria: Official IEC standard text or official IEC page; use only for scope/rating background.
- Rejection criteria: Secondary pages that quote limits without traceable clause context.
- Sentence to support: The bushing category and rating context should be linked to the appropriate IEC reference.
- RUN015 status: TRACEABILITY_RECORD_EXISTS_NEEDS_STANDARD_TEXT_CONFIRMATION

## [REF_RIP_BUSHING_THERMAL]

- Search target: Find peer-reviewed RIP/bushing thermal or electro-thermal modeling support.
- Recommended keywords: `RIP transformer bushing thermal finite element electro-thermal oil temperature load contact resistance`
- Acceptance criteria: Peer-reviewed paper on bushing thermal/FEM/electro-thermal modeling with relevant variables.
- Rejection criteria: Papers on unrelated cable joints or generic insulation without bushing thermal model.
- Sentence to support: Current-driven conductor loss, contact heating, dielectric loss, oil temperature, and air convection contribute to the steady temperature field.
- RUN015 status: LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION

## [REF_DIELECTRIC_LOSS_THEORY]

- Search target: Confirm dielectric-loss equation and RMS convention.
- Recommended keywords: `dielectric loss density omega epsilon0 epsr tan delta E squared RMS field`
- Acceptance criteria: Textbook, standard, or peer-reviewed source giving the harmonic dielectric-loss expression and conventions.
- Rejection criteria: Uncited web notes or formulas without unit/convention explanation.
- Sentence to support: The field-coupled loss density q_dielectric = omega epsilon0 epsr tan(delta)|E|^2 links the electrostatic field to the thermal source.
- RUN015 status: PARTIALLY_RESOLVED_WITH_LOCAL_PDFS_NEEDS_THEORY_REFERENCE_CONFIRMATION

## [REF_CONDENSER_BUSHING_ELECTROSTATICS]

- Search target: Support condenser screens and field grading treatment.
- Recommended keywords: `condenser bushing electrostatic finite element floating screen field grading RIP bushing`
- Acceptance criteria: Peer-reviewed bushing electrostatics/electro-thermal paper discussing screens or grading.
- Rejection criteria: Generic capacitor papers not connected to condenser bushings.
- Sentence to support: Condenser bushings use graded conductive screens to control electric-field distribution.
- RUN015 status: LOCAL_PDF_CANDIDATES_FOUND_NEEDS_CONTENT_AND_BIBLIOGRAPHIC_CONFIRMATION

## [REF_COMSOL_FLOATING_POTENTIAL]

- Search target: Locate official COMSOL floating-potential documentation.
- Recommended keywords: `COMSOL electrostatics floating potential zero net charge documentation`
- Acceptance criteria: Official COMSOL documentation page/manual section for Floating Potential and zero net charge.
- Rejection criteria: Forum posts or unofficial tutorials unless used only as secondary implementation hints.
- Sentence to support: Screens S01-S09 are treated as floating condenser screens with zero net charge in the full field-coupled model.
- RUN015 status: UNRESOLVED

## [REF_MESH_CONVERGENCE]

- Search target: Support finite-element mesh convergence verification wording.
- Recommended keywords: `finite element mesh convergence verification relative error fine mesh reference`
- Acceptance criteria: Numerical-method textbook, verification guideline, or peer-reviewed FEM convergence reference.
- Rejection criteria: Claims that convergence proves physical validation.
- Sentence to support: RUN011A compares coarse, medium, and fine meshes and uses the fine mesh as reference.
- RUN015 status: UNRESOLVED

## [REF_RISK_DIAGNOSTIC_METHOD]

- Search target: Support diagnostic risk zoning as screening, not standard limit.
- Recommended keywords: `diagnostic risk zoning screening matrix thermal risk assessment transformer bushing`
- Acceptance criteria: Risk-screening or diagnostic-threshold method reference that does not imply standard operating limits.
- Rejection criteria: Standards or papers that would be misread as defining the project's thresholds.
- Sentence to support: Diagnostic risk zones are internal screening classes, not IEC/IEEE limits or operating guarantees.
- RUN015 status: PARTIALLY_RESOLVED_WITH_LOCAL_APPLICATION_PDFS_NEEDS_METHOD_REFERENCE
