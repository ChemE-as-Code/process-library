# Your section: S2 process simulation of ammonia-1, continuation (round 2)
Branch: stage/basic-simulation (checked out). The first S2 session ended BLOCKED on core#57 (a
multi-recycle loop never converged through core v1.0.0). core#57 is fixed in core **v1.0.1**
(`cheme --version` shows 1.0.1; tear iteration with Anderson acceleration, ADR 0033), and the
DEXPI-class `Pumping` crash (core#59) too. Read DESIGN.md D-024/D-025 and PROGRESS.md first: they
say what the first session did, what stayed on the concept model (SYN, PGR, the steam system)
and keep a DWSIM-ready description of the loop and purge-recovery model.

Finish S2 on v1.0.1:
- Model the synthesis loop, the product flash and refrigeration, and the purge recovery in
  `process/simulation.yaml` / the flowsheet as DESIGN.md D-024 describes, and converge the whole
  plant with `cheme process simulate` (every design-basis case); if a part still cannot be
  represented, keep it specified and say exactly why.
- Retune what the first session recorded as deviations where the simulation now covers them
  (e.g. the converter H2/N2 through the process air), as decisions in DESIGN.md, never by
  editing simulated values; the P301 pump may now be a Pumping step (core#59).
- Replace the loop's ASSUMED concept values with `calculated` ones (`--fill`) where covered;
  never overwrite given or assumed values; deviations stay findings.
- Energy audit as far as core supports it (core#60 open: plant closure with component
  separators); `cheme maturity` reported with the exact unsupported requirements (core#315,
  the unsourced feed R-03).
Then the PR body for the whole section (both sessions) in `build/pr-body.md`.

## S2 targets (unchanged, from plan.md)
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

