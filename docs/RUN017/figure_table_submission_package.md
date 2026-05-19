# Figure and Table Submission Package

## Main Figures

### Fig. 1
- caption: Fig. 1. Model workflow and CAD-constrained axisymmetric geometry. The workflow links geometry construction, explicit domain/boundary selection, source normalization, full field-coupled dielectric-loss calculation, 125-case risk scanning, mesh independence, and material/boundary sensitivity. The geometry panel summarizes the axisymmetric representation of the BRFGL1-126/1250-4 bushing, including the air-side external insulation, flange, oil-side region, RIP core, condenser screens, center conductor, and contact heat-source layer.
- source file path: `results/paper_figures/manuscript_ready/Fig1_model_workflow_and_geometry.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 3.1 - The modeling workflow, geometry abstraction, and audit path are summarized in Fig. 1.

### Fig. 2
- caption: Fig. 2. Baseline electro-thermal field distribution for STEADY_1250_LOAD_1p0. The panels report the baseline potential/electric-field indicators, RIP dielectric-loss density, and steady temperature response from RUN009A. The calculation uses field-coupled dielectric loss and explicit by-ID selections.
- source file path: `results/paper_figures/manuscript_ready/Fig2_baseline_field_dielectric_temperature.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.1 - The baseline potential, electric-field, dielectric-loss, and temperature indicators are shown in Fig. 2.

### Fig. 3
- caption: Fig. 3. RUN010 global maximum-temperature heatmap. Global maximum temperature is shown over the 5 x 5 x 5 load, oil-temperature, and contact-resistance matrix. The diagnostic safe, attention, warning, and thermal-risk zones are visualization classes only and are not IEC/IEEE limits.
- source file path: `results/paper_figures/manuscript_ready/Fig3_run010_Tmax_risk_heatmap.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.2 - Fig. 3 presents the global temperature response.

### Fig. 4
- caption: Fig. 4. RUN010 contact-region maximum-temperature heatmap. Contact-layer temperature is shown over the same operating matrix to highlight the local response to the contact-resistance multiplier.
- source file path: `results/paper_figures/manuscript_ready/Fig4_run010_contact_temperature_risk_heatmap.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.2 - Fig. 4 presents the corresponding contact-region response.

### Fig. 5
- caption: Fig. 5. Diagnostic safe-load boundary by oil temperature and contact-resistance multiplier. The boundary summarizes the highest load multiplier remaining in the diagnostic safe zone for each oil-temperature and contact-resistance pair.
- source file path: `results/paper_figures/manuscript_ready/Fig5_safe_load_boundary_by_oil_and_Rc.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.3 - The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4.

### Fig. 6
- caption: Fig. 6. Heat-source decomposition for representative RUN010 cases. Conductor Joule heat, contact heat, and RIP dielectric loss are compared for low-risk, baseline, high-contact-risk, and highest-pressure operating cases.
- source file path: `results/paper_figures/manuscript_ready/Fig6_heat_source_decomposition_representative_cases.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.2 - The heat-source response underlying these trends is summarized for representative cases in Fig. 6.

### Fig. 7
- caption: Fig. 7. Difference between RUN008 approximate and RUN010 field-coupled dielectric-loss models. The figure reports the temperature change after replacing approximate_Qdielectric_ref with field-coupled dielectric loss from the electrostatic solution.
- source file path: `results/paper_figures/manuscript_ready/Fig7_run008_vs_run010_temperature_difference.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.4 - The risk zone changes in 2 of the 125 cases, as shown in Fig. 7.

### Fig. 8
- caption: Fig. 8. Mesh-independence summary. Coarse, medium, and fine meshes are compared for representative cases, with the fine mesh used as the reference and the medium mesh used for the main risk scan.
- source file path: `results/paper_figures/manuscript_ready/Fig8_mesh_independence_summary.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.6 - The mesh-independence results are shown in Fig. 8 and summarized in Table 5.

### Fig. 9
- caption: Fig. 9. Material and boundary sensitivity ranking. One-factor sensitivity indices identify the dominant uncertainty sources affecting maximum temperature and dielectric-loss-related outputs.
- source file path: `results/paper_figures/manuscript_ready/Fig9_parameter_sensitivity_ranking.png`
- main/supplementary status: main
- exists according to index: true
- manuscript section callout: 4.6 - The sensitivity ranking is shown in Fig. 9 and summarized in Table 6.

## Main Tables

### Table 1
- caption: Table 1. Stage audit summary from RUN001 to RUN012B. This table records the purpose, model type, case count, key outputs, validation status, and manuscript role of each modeling stage.
- source file path: `results/summary_tables/manuscript_ready/run_stage_audit_summary.csv`
- main/supplementary status: main
- manuscript section callout: 3.2 - The stage audit table records this development path in Table 1.

### Table 2
- caption: Table 2. Key numerical result summary for manuscript use. This table lists the main quantitative values used in the text, including baseline temperature, dielectric loss, RUN010 temperature ranges, risk-zone counts, RUN008-RUN010 differences, mesh errors, and sensitivity ranking.
- source file path: `results/summary_tables/manuscript_ready/key_result_summary.csv`
- main/supplementary status: main
- manuscript section callout: 3.2 - The numerical quantities used later in the manuscript are indexed in Table 2.

### Table 3
- caption: Table 3. Model validation evidence chain. This table maps each validation item to the relevant run, evidence file, pass criterion, and manuscript interpretation.
- source file path: `results/summary_tables/manuscript_ready/model_validation_evidence_chain.csv`
- main/supplementary status: main
- manuscript section callout: 3.4 - The validation evidence chain is summarized in Table 3.

### Table 4
- caption: Table 4. RUN010 diagnostic risk-boundary summary. This table reports the maximum safe load and transition loads for each oil-temperature and contact-resistance multiplier combination. The thresholds are diagnostic visualization classes only.
- source file path: `results/raw_comsol_exports/FULL_ELECTROTHERMAL_DIELECTRIC_LOSS_RISK_125_RUN010/run010_risk_boundary_summary.csv`
- main/supplementary status: main/supplementary
- manuscript section callout: 4.3 - The diagnostic safe-load boundary decreases as oil temperature and contact-resistance multiplier increase, as shown in Fig. 5 and Table 4.

### Table 5
- caption: Table 5. RUN011A mesh-independence summary. This table compares coarse, medium, and fine meshes for representative cases and reports temperature, electric-field, dielectric-loss, heat-balance, and singularity-check metrics.
- source file path: `results/raw_comsol_exports/MATERIAL_AND_MESH_SENSITIVITY_RUN011/RUN011A_MESH_INDEPENDENCE/mesh_convergence_summary.csv`
- main/supplementary status: main/supplementary
- manuscript section callout: 4.6 - The mesh-independence results are shown in Fig. 8 and summarized in Table 5.

### Table 6
- caption: Table 6. RUN011B material and boundary sensitivity summary. This table reports one-factor perturbation results and sensitivity indices for RIP thermal, dielectric, contact-resistance, and heat-transfer parameters.
- source file path: `results/raw_comsol_exports/MATERIAL_AND_MESH_SENSITIVITY_RUN011/RUN011B_MATERIAL_BOUNDARY_SENSITIVITY/sensitivity_index_summary.csv`
- main/supplementary status: main/supplementary
- manuscript section callout: 4.6 - The sensitivity ranking is shown in Fig. 9 and summarized in Table 6.

## Supplementary Figures

### Fig. S1
- caption/usage: Full run audit flow
- source file path: `results/paper_figures/manuscript_ready/FigS1_full_run_audit_flow.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true

### Fig. S2
- caption/usage: Qcontact I2Rc validation
- source file path: `results/paper_figures/manuscript_ready/FigS2_Qcontact_I2Rc_validation.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true

### Fig. S3
- caption/usage: Qjoule I2 scaling validation
- source file path: `results/paper_figures/manuscript_ready/FigS3_Qjoule_I2_scaling_validation.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true

### Fig. S4
- caption/usage: Heat balance residual distribution
- source file path: `results/paper_figures/manuscript_ready/FigS4_heat_balance_residual_distribution.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true

### Fig. S5
- caption/usage: Electric-field diagnostic summary
- source file path: `results/paper_figures/manuscript_ready/FigS5_Efield_diagnostic_summary.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true

### Fig. S6
- caption/usage: Dielectric loss field-to-ref ratio
- source file path: `results/paper_figures/manuscript_ready/FigS6_dielectric_loss_field_to_ref_ratio.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true

### Fig. S7
- caption/usage: Material sensitivity each parameter
- source file path: `results/paper_figures/manuscript_ready/FigS7_material_sensitivity_each_parameter.png`
- supplementary routing: Supplementary Figure Routing Note
- exists according to index: true
