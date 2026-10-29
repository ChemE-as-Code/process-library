# Your section: S1 concept close-out of ammonia-1
Branch: stage/concept-closeout (checked out).

## S1 concept close-out (branch stage/concept-closeout; ends with the concept sign-off)
Close the concept stage of ammonia-1.
- Run `cheme skills status`; update outdated bundled skills that are not locally modified
  (`cheme skills update`), and say which.
- Close or carry, each with a reason, the open findings R-01..R-05 of
  `reviews/2026-10-27-pfd-lci-review.md` (R-03: the natural-gas composition and supply pressure;
  source them from an open, citable reference for the brief's site or, if none exists, keep them
  ASSUMED with the reason and the effect on `cheme maturity`).
- Resolve the open inputs I-01..I-10 in DESIGN.md, or keep each ASSUMED with a reason.
- Rebuild the BFD/PFD with this core (`cheme process build`) so no generated-version finding is left.
- Plot plan: `layout/site-plan.yaml` and `layout/equipment-placement.yaml` for the 44 items with
  areas, roads, racks and the spacing criteria as `separations:` (skill `layout-yaml`), gate
  `layout-plot-plan`.
- Economics: the decision the next stage needs, an AACE class 5 capital estimate, sourced prices
  of the main feeds and products, and a screening TEA with the dominant premises
  (`estimate/tea.yaml`, skill `tea`).
- All concept gates must pass. Do not sign off yourself: the review and sign-off jobs follow.
