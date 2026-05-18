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
