# Review this section's PR: S4 of ammonia-1 (PR #255), round 1
Review topic for the record: `control-lists`.
Branch: stage/basic-control-lists (checked out). Earlier sections are merged on main.

## S4 control and lists (branch stage/basic-control-lists)
Equipment, line and instrument lists complete and linked to the P&IDs and the flowsheet (skill
`lists-sync`); regulatory loops (`control/loops.yaml`), startup/shutdown sequences
(`control/sequences.yaml`), interlocks and cause and effect (`control/cause-effect.yaml`),
narrative and control philosophy; `cheme control report` without findings; PFD current.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
