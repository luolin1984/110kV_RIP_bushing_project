# Manuscript Claim Boundary Notes

The following claim boundaries must be preserved during submission-oriented editing.

1. The project is a finite-element numerical simulation and diagnostic screening workflow. It is not a physical experiment.
2. The diagnostic risk zoning used in RUN010 is not an IEC/IEEE standard limit, material lifetime threshold, operating rule, or safety guarantee.
3. The contact-resistance multiplier is a parameterized equivalent model. It is not a measured defect, inspected failure geometry, or asset-specific diagnosis.
4. The DIELECTRIC_LOSS_REVIEW_REQUIRED / dielectric_loss_review_required flag must remain visible. The field-coupled dielectric loss exceeds the average-field reference, and this difference is a review item rather than a failed run.
5. The model is two-dimensional and axisymmetric. Local 3D terminal, flange, and bolt effects are not explicitly resolved.
6. 2D axisymmetric limitation: the model is two-dimensional and axisymmetric. Local 3D terminal, flange, and bolt effects are not explicitly resolved.
7. no CFD limitation: air and oil are represented by boundary heat-transfer conditions. No CFD fluid-domain solution is included.
8. no transient limitation: the present results are steady-state. Transient overload, annual weather driving, and time-dependent thermal inertia are outside RUN010.
9. The local terminal/flange bolt geometry is not a full 3D resolved model.
10. no field/lab validation: no field-monitoring or laboratory validation has been completed yet.
11. The RUN010 risk boundary is a numerical screening result. It should not be written as an operational rule before external validation.

Any future Introduction, Abstract, Conclusion, or graphical abstract must be checked against these boundaries before use.
