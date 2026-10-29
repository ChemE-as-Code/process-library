# Section tasks of the ammonia-1 run

Each job gets the role preamble (`implement.md`, `review.md`, `fix.md`, `signoff.md`, `merge.md`)
followed by its section's task below. Review jobs get the same section text with
"Review this section's PR" in front; fix jobs get it with "Fix the open findings of the newest
review of this section". The orchestrator adds nothing else except the branch name and, for fix
and re-review jobs, the round number.

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

## S3a / S3b / S3c P&IDs (branches stage/basic-pids-front, -mid, -loop)
Draft complete P&IDs (DEXPI 2.0.1, skills `pid-draft`, `pid-design-*`, `dexpi-xml`) from the
simulated PFD, `cheme validate` clean at error level, lists updated with every sheet:
- S3a (front): feed gas, desulphurisation, primary and secondary reforming, waste-heat recovery,
  HT/LT shift.
- S3b (mid): aMDEA CO2 removal, methanation, synthesis-gas compression.
- S3c (loop): synthesis loop, converter, refrigeration, ammonia separation and storage interface,
  purge-gas recovery, steam and BFW system and the main utilities headers.
Off-page connectors consistent across sheets; render and look at each sheet; gates pids-exist,
pids-valid, drawing-clean, process-basic, process-links.

## S4 control and lists (branch stage/basic-control-lists)
Equipment, line and instrument lists complete and linked to the P&IDs and the flowsheet (skill
`lists-sync`); regulatory loops (`control/loops.yaml`), startup/shutdown sequences
(`control/sequences.yaml`), interlocks and cause and effect (`control/cause-effect.yaml`),
narrative and control philosophy; `cheme control report` without findings; PFD current.

## S5 3D layout, MTO and class 4 estimate (branch stage/basic-layout)
3D layout (skills `layout-yaml`, `pipe-routing`, `structures-access`, `area-classification`):
every DN25 and larger process line routed, zones declared, gates layout-3d, lifting-study, mto;
MTO and class 4 estimate (`cheme assess mto`, `cheme assess estimate`, skill `mto-estimate`) and
TEA updated; enable the template gate `tea` as documented.

## S5r basic reviews and sign-off (on stage/basic-layout)
Two independent review jobs: a design review (topic `design`, the P&IDs, lists, control and
simulation of S2-S4) and a layout review (topic `layout`). Then the basic sign-off job and the
merge job.

## S6 HAZOP (branch stage/basic-hazop)
HAZOP of all P&IDs (skills `hazop-study`, `hazop-equipment-causes`, `hazop-assessment`,
`safeguard-crediting`): nodes, deviations, causes, consequences, safeguards, actions; rated with
`cheme safety hazop rate` against `safety/risk-matrix.yaml`; everything stays `status: proposed`
(AGENTS.md); `cheme safety hazop check` clean; actions closed or carried with an owner and reason.

## S7 datasheets (branch stage/detail-datasheets)
A datasheet for every equipment-list item (skill `datasheets`), sized from the simulation with
core's tools where they exist (`cheme datasheets draft`, `fill`), provenance on every value;
gate `datasheets`.

## S8 relief (branch stage/detail-relief)
Relief scenarios for every PSV and relief device on the P&IDs (skills `relief-scenarios`,
`pid-design-pressure-relief`): governing case and required capacity per device; what core cannot
size is stated; enable the template gate `relief-on-pid` for the devices.

## S9 detail gates (branch stage/detail-gates)
Take the detail-stage gates as far as they go (instrument list complete, utilities and small-bore
lines routed, cable trays and schedule with `cheme layout cables`, HVAC where buildings need it)
and report per gate whether it passes and why not.
