# Review this section's PR: S8 of ammonia-1 (PR #262), round 1
Review topic for the record: `relief`.
Branch: stage/detail-relief (checked out). Earlier sections are merged on main.

## S8 relief (branch stage/detail-relief)
Relief scenarios for every PSV and relief device on the P&IDs (skills `relief-scenarios`,
`pid-design-pressure-relief`): governing case and required capacity per device; what core cannot
size is stated; enable the template gate `relief-on-pid` for the devices.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
