# Review this section's PR: S9 of ammonia-1 (PR #264), round 1
Review topic for the record: `detail-gates`.
This PR is stacked on `stage/basic-layout` (open): on `VERDICT: approve` do **not** merge.
Branch: stage/detail-gates (checked out), stacked on `stage/basic-layout` (open PR, waiting for the owner's decisions: lifting acceptance, feed specification, risk matrix, estimate rates); its PR's base is `stage/basic-layout`. S6-S8 are merged on main and in `stage/basic-layout`.

## S9 detail gates (branch stage/detail-gates)
Take the detail-stage gates as far as they go (instrument list complete, utilities and small-bore
lines routed, cable trays and schedule with `cheme layout cables`, HVAC where buildings need it)
and report per gate whether it passes and why not.


At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
