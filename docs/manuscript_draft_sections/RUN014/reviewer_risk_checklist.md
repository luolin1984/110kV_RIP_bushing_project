# Reviewer Risk Checklist

| risk_item | severity | where_addressed | mitigation_sentence | still_needs_external_reference | notes |
|---|---|---|---|---|---|
| 2D axisymmetric model limitation | medium | 3.1; 4.7 | The model is explicitly described as two-dimensional and axisymmetric, with non-axisymmetric terminal and bolt details excluded. | yes | Use as a limitation, not as a flaw hidden from readers. |
| no physical experimental validation | high | 4.7 | The package states that the risk boundary has not yet been validated against field monitoring or laboratory measurement data. | yes | Avoid any wording implying laboratory confirmation. |
| diagnostic risk zones are not standard limits | high | 4.3; captions | Risk zones are defined as internal diagnostic visualization classes, not IEC/IEEE limits or material lifetime thresholds. | yes | Needs diagnostic-risk-method reference. |
| dielectric_loss_review_required retained | medium | 3.5; 4.1; 4.4 | The review flag is retained and interpreted as an uncertainty marker rather than a numerical failure. | no | Evidence is internal RUN009A/RUN010. |
| field-coupled dielectric loss/ref ratio slightly above review interval | medium | 4.1; 4.4 | The field/reference ratio is reported as 11.020 and discussed together with field_singularity_flag=false. | yes | Needs dielectric-loss and field-modeling support. |
| contact degradation is parameterized | medium | 3.3; 4.5 | Contact degradation is described as an equivalent multiplier, not a measured defect geometry. | yes | May need contact-resistance degradation literature. |
| material parameters partly assumed or public-data based | medium | 3.2; 4.6 | The text states that material and heat-transfer parameters combine public data and documented assumptions. | yes | Tie to source_traceability and parameter assumptions. |
| no fluid-domain CFD | medium | 3.2; 4.7 | Air and oil are represented through convective boundary conditions rather than resolved fluid domains. | yes | Preempt reviewer asking for CFD. |
| no transient overload simulation | medium | 4.7 | The text limits the results to steady operating cases and excludes transient overload history. | yes | Could become future work. |
| no full 3D terminal/flange bolt geometry | medium | 3.1; 4.7 | The axisymmetric model excludes flange bolt holes and local three-dimensional terminal structures. | yes | Consider 3D local submodel in future work. |
| risk boundary not yet validated by field monitoring | high | 4.7 | The text states that RUN010 should not be treated as a final operational rule before external validation. | yes | Important before submission claims. |
