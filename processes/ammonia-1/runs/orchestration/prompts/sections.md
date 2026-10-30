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

## S5b basic close-out (on stage/basic-layout, PR #257; added 2026-10-30, interventions O-032)
S5 stopped after three review rounds with the high finding `2026-10-29-design#1` open and two
basic gates failing (`lifting-study`, `maturity-balanced`). Close them by engineering work, never
by accepting, relaxing or moving a gate. Read the review records in `reviews/` (newest `design`
and `layout`), `PROGRESS.md` and `build/pr-comment.md` first.
1. **maturity-balanced** (skills `process-design`, `reaction-evidence-search`, `reactions`,
   `process-simulation`): give the natural-gas feed flow and composition with provenance `given`
   and a published source; give each reactor's model basis (R-100, R-102A, H-101 and any other
   step `cheme maturity` names) from published sources: a sourced conversion or approach to
   equilibrium, or observations in `process/reaction-evidence.yaml` that cover it, or a declared
   equilibrium/Gibbs model whose data are given. Look sources up online; record each fact with
   URL/DOI and locator in our own words. Where a sourced value differs from the current one,
   change it, rerun `cheme process simulate --fill` and carry the effects (stream table, PFD,
   duties used by datasheets, TEA). Run `cheme maturity` until it reaches `balanced`, or say
   exactly which requirement no published source covers.
2. **lifting-study** (skills `layout-yaml`, `structures-access`, `pipe-routing`): run
   `cheme layout lifting`; resolve every lane by design: crane pads within reach, laydowns,
   moving or re-pinning lines that block a lane, relocating items where the plot plan allows, a
   crane chart that carries the lift. Do not accept findings. If lanes remain that only an
   erection-sequence acceptance can clear, list them in `build/lifting-acceptance-proposal.md`
   (item, blocking object, the lifting plan's reason) for the owner and do not write them into
   any accepted list.
3. **Class 4 estimate** (skill `mto-estimate`, `tea`): replace the example values of
   `estimate/rates.yaml` with published, sourced rates and factors (cost index with year and
   source, bulk unit rates, installation factors), each with status and source; equipment
   costs from sized items (for the major items you may run `cheme datasheets draft`/`fill`
   here; S7 completes the datasheets). State the class, its accuracy range and what is
   ASSUMED. Rebuild the take-off and estimate, update the TEA.
4. Close or answer the other open review findings where quick; carry the rest with a reason.
Rebuild layout, MTO and estimate; `cheme validate` 0 errors; `cheme check --stage basic` and
report each gate. End with STATUS: DONE when both gates pass, else BLOCKED with the exact
remaining requirement. The reviews after this job are the S5r reviews (topics `design`, `layout`).

## S5c basic close-out with the owner's decisions (on stage/basic-layout, PR #257; interventions I-006)
The branch now holds S5, S5b, S6-S8 (via main) and S9 (#264 merged into it). The owner (a
human, the project owner) decided on 2026-10-30, recorded as I-006 in `runs/interventions.md`:
- **Lifting:** the owner accepts the 8 lanes H-101, E-104, E-402, K-501, E-501, E-502, E-505,
  E-504 with the lifting plan's reason in `build/lifting-acceptance-proposal.md` (regenerate it
  if missing). Record the acceptance the way `cheme layout lifting` documents, with accepted_by
  `owner (I-006, 2026-10-30)` and the reason. The other lanes (cable trays over K-101, K-102,
  K-103, K-701 added in S9, and any other) are **not** accepted: clear them by design (tray route
  or elevation, crane pad on the free side, lift lane); if core cannot do it (core#73), stop and
  say so precisely.
- **Buried cooling-water road crossings:** the owner accepts the 4 `cheme.layout-headroom`
  findings of the buried DN 1400 headers under roads R-5/R-6 (reason: buried crossing in a sleeve
  under the road; core#70), accepted_by `owner (I-006, 2026-10-30)`.
- **Feed specification:** this is a paper case study; the owner approves a *representative*
  feed specification. Give the natural gas (S1), process and combustion air (S12, S61) and
  water feeds (S26, S70) a representative composition and conditions with provenance `given`
  and a published source (a representative pipeline natural gas, standard dry air, demineralised
  water), with the owner's approval (I-006) named in the source note; flows follow from the
  design capacity in the design basis (say so in the source). If the composition changes the
  gas, rerun `cheme process simulate --fill` and carry the effects. S5b saw the boiler duty jump
  130 -> 197.5 MW with the EBTF gas and reverted (D-034): find and explain the cause before
  accepting a change of that size; if you cannot, choose a representative published lean gas
  close to the current one.
- **Furnace H-101 model basis:** give the fuel combustion a sourced model basis (complete
  combustion of the fuel with excess air is standard design practice: cite a published source
  for it) so `maturity-balanced` passes; likewise any other step `cheme maturity` names.
- **Risk matrix:** the owner allows an assumed matrix. Replace the example 4x4 in
  `safety/risk-matrix.yaml` with a project matrix close to industry practice (e.g. 5x5,
  order-of-magnitude frequency bands per year, severity for people, environment, asset,
  reputation), written in our own words with the published practice it follows cited, marked
  ASSUMED, `example: false`, accepted_by `owner (I-006, 2026-10-30), assumed for the paper case`.
  Re-rate the HAZOP with `cheme safety hazop rate --write`; HAZOP entries stay `status: proposed`.
- **Estimate:** look up online a published cost index (CEPCI, value and year), published bulk
  unit rates and installation/factor-method factors (open literature, textbooks, public cost
  guides), each in `estimate/rates.yaml` with status, source (URL/DOI, locator) and year, in our
  own words. Equipment costs from the sized datasheets. Bring the estimate to class 4 (state the
  accuracy range and what is ASSUMED), rebuild `cheme assess estimate --write`, update the TEA.
- **Datasheets:** fill the main dimensions the detail gate `datasheets` reports missing
  (`cheme datasheets fill`, sized from the simulation, provenance on every value).
Then: rebuild layout, MTO, estimate; `cheme validate` 0 errors; `cheme check` (all stages) and
`cheme maturity`, report each gate. STATUS: DONE when every basic gate except the two review
gates passes, else BLOCKED with the exact remaining requirement. The reviews after this job are
the basic reviews (topics `design`, `layout`), then the basic sign-off and merge.

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
