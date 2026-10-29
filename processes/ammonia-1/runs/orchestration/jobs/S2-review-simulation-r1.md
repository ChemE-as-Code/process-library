# Review this section's PR: S2 of ammonia-1 (PR #244), round 1
Review topic for the record: `simulation`.
Branch: stage/basic-simulation (checked out). Earlier sections are merged on main.

## S2 process simulation (branch stage/basic-simulation)
Build the DWSIM model of the whole plant through core (skill `process-simulation`,
`process/simulation.yaml`, `cheme process simulate`), before any P&ID.
- First check that DWSIM starts (`cheme process methods`, a `cheme process simulate --check`);
  if it cannot be started, stop with `STATUS: BLOCKED: DWSIM` and change nothing.
- Choose the thermodynamic model with the skill `thermodynamic-model-selection` (cubic EOS for
  the syngas and the synthesis loop) and record the method-selection facts. State what the aMDEA
  CO2 removal needs; if DWSIM or core cannot represent it, keep it a specified block and say so.
- Every case of the design basis; recycles (synthesis loop, purge recovery, steam system)
  converged; solver, property package and versions recorded.
- Simulated values replace the balance script's specified ones where the simulation covers them,
  as `calculated` (`--fill`), never overwriting given or assumed values; deviations are findings
  in DESIGN.md, not edits.
- Close the energy audit (core's energy check on the converged run).
- Enable the template gate `maturity-balanced` (as the template documents it) and report
  `cheme maturity`. If core#315 keeps the plant below `predictive`, state exactly which
  requirement is unsupported; do not work around it.



At the very end, before the VERDICT line, add one line exactly like `FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings new in this review (not carried ones).
