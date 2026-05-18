# RUN013 Manuscript Consistency Check

- No physical experiment misclaim: PASS
  - Drafts describe the work as finite-element numerical simulation and state that physical testing is not included.
- Diagnostic risk zoning is not written as an IEC/IEEE limit: PASS
  - Sections 4.3 and figure/table captions explicitly define the zones as internal diagnostic visualization classes.
- dielectric_loss_review_required is retained and explained: PASS
  - Retained for 125/125 RUN010 cases and discussed as a review flag, not a model failure.
- RUN008 solid-only result is not used as the final main result: PASS
  - RUN008 is only used as an approximate diagnostic comparator; RUN010 is the full field-coupled main matrix.
- Contact degradation is not claimed as a measured defect: PASS
  - The text defines it as a parameterized equivalent contact-resistance multiplier.
- Mesh independence is included: PASS
  - RUN011A medium-vs-fine pass=3/3; max Tmax error=0.355%.
- Sensitivity analysis is included: PASS
  - RUN011B ranking included: tan_delta_multiplier > epsr_RIP > Rc0_multiplier > h_air > k_RIP_multiplier > h_oil.
- 2D limitation is included: PASS
  - The drafts state the 2D axisymmetric approximation and omitted three-dimensional bolt/terminal details.
- Major numbers are evidence mapped: PASS
  - C1-C10 are recorded in manuscript_claim_to_evidence_map.csv.

Manuscript experiment section consistency status: PASS
