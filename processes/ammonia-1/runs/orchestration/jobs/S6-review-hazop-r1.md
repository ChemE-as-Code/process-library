# Review this section's PR: S6 of ammonia-1 (PR #38), round 1
Review topic for the record: `hazop`.
Branch: stage/basic-hazop (checked out). Earlier sections are merged on main.

## S6 HAZOP (branch stage/basic-hazop)
HAZOP of all P&IDs (skills `hazop-study`, `hazop-equipment-causes`, `hazop-assessment`,
`safeguard-crediting`): nodes, deviations, causes, consequences, safeguards, actions; rated with
`cheme safety hazop rate` against `safety/risk-matrix.yaml`; everything stays `status: proposed`
(AGENTS.md); `cheme safety hazop check` clean; actions closed or carried with an owner and reason.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
