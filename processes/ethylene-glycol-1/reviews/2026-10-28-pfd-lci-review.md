---
topic: design
reviewed_commit: a747a45530890f50751344b3e80c37821947d6a1
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, scripts/eg_balance.py, equipment/equipment-list.yaml, lca/lca.yaml, lca/mappings.yaml, runs/20261028-145843-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/ethylene-glycol-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI, issue #172)

Independent review of the ethylene-glycol-1 case study (glycols-only EO/EG plant, O2-based EO
reactor, thermal hydration, 50 t/h MEG) at commit a747a45 on `case/ethylene-glycol-1`
(5 commits over origin/main, all inside `processes/ethylene-glycol-1/`: `git diff --name-only
origin/main..HEAD` lists nothing outside the folder). The reviewer did not author the design and
changed no design file.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | PFD | R-101, E-101, Q1-Q4, feed:MPS | **EO loop energy does not close; the steam R-101 raises is overstated.** `scripts/eg_balance.py:302` sets the steam raised to the full reaction heat (83.5 MW), which holds only for an isothermal reactor. The flowsheet gives the reactor feed S5 at 333.15 K (`process/flowsheet.yaml` S5) and the outlet S6 at 523.15 K. With the script's own cp (40 kJ/kmol K, `eg_balance.py:55`) and 38,690 kmol/h, heating the gas from 333 to 523 K takes about 82 MW, and nothing supplies it. E-101 is listed as "feed/effluent exchanger and trim cooler" (`equipment/equipment-list.yaml:9`), but the flowsheet and script model only the trim cooler (373 to 313 K). The 523 to 373 K effluent heat (about 64 MW) has no destination in the flowsheet. If the implied interchanger heats the feed to about 483 K, the gas still rises about 40 K across the reactor, which takes about 17 MW of the reaction heat. Steam raised would then be about 66 MW, and the MP steam import would rise from 22.5 MW to about 40 MW. The LCI exchange feed:MPS (0.449 kWh/kg MEG, "1.62 GJ/t" in D-008, report and results) is therefore biased low by more than the stated +/-50 %. | high | open | Model the feed side of the E-101 interchanger: give S5 the interchanger outlet temperature as an ASSUMED value, or add a feed-heating step. Then set the steam raised to the reaction heat minus n·cp·(T_out - T_in, reactor). Re-run `eg_balance.py build`, update Q1-Q8, D-008, the LCI (`cheme assess lca --inventory --write`) and process.yaml. |
| 2026-10-28-pfd-lci-review#2 | PFD | M401, SP501, R-401 feed (S13, S23, S24, S30) | **Glycol reactor feed heating is missing from the energy estimate.** Aqueous EO (S13, 313 K, 44 t/h) mixes with recycle water (S23, 403 K, about 315 t/h). The mixture comes to about 397 K, yet the reactor feed S24 is given at 423 K, and no heater or energy stream supplies the difference (about 10.6 MW). The recycle water also rises from 393 K (S30) to 403 K (S23) across the splitter SP501, a step that can carry no duty (about 3.8 MW). The adiabatic hydration heat (23.4 MW) is credited in full against the evaporator steam (`eg_balance.py:326`), but the preheat that the 423 K inlet needs is not charged. Together with #1, the steam import is understated by a factor of roughly 2 to 2.5 (about 50 MW, or 3.6-3.9 GJ/t MEG, instead of 22.5 MW). | medium | open | Add the feed heater duty (M401 to R401, or a heater step) and make the SP501 outlet temperature equal its inlet. Decide in D-008 which heat source serves the preheat (MP steam, or vapour from the first evaporator effect, which lowers the economy) and charge it. Re-run the balance and the LCI. |
| 2026-10-28-pfd-lci-review#3 | PFD | R-401 split, allocation | **The key product-split parameter is unsourced, and the case sits at the optimistic end.** The rate of EO with glycols relative to water (2.0 per mol, D-005) is ASSUMED "not from a source read in this run". It sets the crude-glycol MEG share at 92.0 wt%, the top of the BREF 75-92 wt% range. That share drives the mass allocation (MEG 92.0 %) and the ethylene use per kg MEG: 1.68 t MEG/t C2H4, near the top of the vendor's 1.53-1.70 range. EO selectivity is also high in its range (85 % of 75-90 %). The disclosure is honest, but no sensitivity is given, so the inventory reads as a best case. | medium | open | Source the relative rate (open kinetics of EO hydration), or add a sensitivity to D-005 and lca/lca.yaml scenarios (for example ratio 2-3 and EO selectivity 80 %), showing the effect on ethylene per kg MEG and on the MEG share. |
| 2026-10-28-pfd-lci-review#4 | - | lca/lca.yaml consumables | **Consumables are excluded only in a YAML comment.** The silver catalyst (about 0.16 g/kg MEG), the potassium carbonate make-up and the organochlorine moderator are left out in a comment at the end of lca/lca.yaml. They are not declared exclusions or cut-offs, so `cheme assess lca --coverage` lists no limitation for them and the dataset does not show them to a user. | medium | open | Declare them as cut-offs or exclusions in the data (with amounts in kg per functional unit where known, so the 1 % rule can be checked), or as gaps with a `missing:` description, so they reach the dataset's limitations. |
| 2026-10-28-pfd-lci-review#5 | - | lca/lca.yaml product:PURGE | **The purge gap description gives the wrong CO2 factor.** It says the purge yields "about 2.7 kg CO2 per kg purge by carbon balance". From the stated composition (S16: 34.7 wt% C2H4, 37.7 wt% CH4, 1.25 wt% C2H6, 3.6 wt% CO2), carbon is 0.599 kg/kg, which gives 2.20 kg CO2/kg. Whoever maps this background later would overstate the purge combustion by about 23 %. | low | open | Correct the text to about 2.2 kg CO2 per kg purge. |
| 2026-10-28-pfd-lci-review#6 | - | process.yaml:35 | **The manifest claims a maturity the evidence does not reach.** `maturity: concept` while `cheme maturity` reports calculation maturity none and the warning `cheme.maturity-claim-exceeds`. `validation.notes` states this openly, and concept is the lowest value in the schema enum, so a reader is not misled. The warning still stands. | low | open | Keep the disclosure and record the situation as an accepted warning with its reason (or raise the evidence to "sourced" by giving feed flows with a source). Mention it in the consolidated PR. |
| 2026-10-28-pfd-lci-review#7 | - | product:HVY | **The heavy glycols residue is below the BREF range.** It is 0.37 kg/t EO against the BREF range of 1.4-21 kg/t EO. D-005 calls it a lower bound because the EO section's glycol bleed is not modelled, but the inventory's waste to incineration is understated accordingly. | low | open | Add the absorbent glycol bleed as an ASSUMED stream, or carry the BREF lower bound as a sensitivity. |
| 2026-10-28-pfd-lci-review#8 | - | checks/checks.yaml | **The concept gate cannot pass in this case.** The concept-stage gate `layout-plot-plan` fails, while D-001 declares layout out of scope, so the concept stage cannot pass `cheme check` as configured. The run report says so. | low | open | Record the scope decision on the gate (stage or `n/a` reason) when the case is consolidated, or plan the plot plan. |

## Previous findings
None: this is the first review of this process (reviews/ held only README.md).

## Drawing
No P&ID in scope. The BFD and PFD are generated (`cheme process build`) and were not read tile by
tile. `cheme validate` printed no `drawing` count line for them, and `drawing-clean` is ok.

## Re-run results (by the reviewer, at a747a45)
- `cheme validate`: 17 files, 0 errors, 0 warnings. Infos only: `decision-unknown` D-023 and D-012,
  both in commented template examples of checks.yaml and cause-effect.yaml, so not findings; and
  the loader's port cycles. Compared: BFD and PFD plus 12 lists. No P&ID, so the equipment, line
  and instrument lists were not compared against P&IDs.
- `cheme check`: concept gates design-basis, concept-lists, process-concept, process-balances,
  assumptions-marked and process-links-concept are ok; layout-plot-plan fails (#8). Basic and
  detail gates fail as expected out of scope (pids-exist, design-review, layout-*, datasheets).
- `cheme maturity`: calculation maturity none, design maturity claimed concept, warning
  `cheme.maturity-claim-exceeds` (#6). Feeds are assumed, not given with a source; reactors and
  separators are specified; there is no simulation run.
- `cheme process streams`: every step balance ok. R101 extents EOX 887.746 and COMB 156.656
  kmol/h; R401 HYD1 845.663, HYD2 40.733, HYD3 1.316 and HYD4 0.0314 kmol/h, equal to D-006.
- `cheme process propagate --check`: no output (nothing to fill, no conflict).
- `cheme assess lca --coverage`: partial screening carbon footprint. 11 gaps, each with a
  `missing:` description of the activity to connect. The ethylene emission is outside the IPCC
  method. Mass, element and carbon-origin balances closed. Publishable. DQR 2.33.
- `cheme diff origin/main --list`: every item is added (new BFD/PFD sheets, sources, sinks,
  steps, components). No item is removed or modified outside the folder.

## Checked and fine
- **Route and boundary** match #172: integrated O2-based EO and thermal hydration, glycols-only.
  The carbonate route, the DMO route and an EO purchase are rejected with reasons (D-001).
- **EO loop stoichiometry checked by hand.** At 85 % selectivity the stoichiometry gives
  ethylene 0.749 t/t EO plus purge loss, which matches the 761 kg/t. Oxygen
  (0.5 + 3 x 0.176 mol/mol EO) gives 0.749 t/t, which matches 755. CO2 is 0.353 t/t
  (351 stated). All are inside the BREF Table 7.6 / 7.3.6.1 ranges quoted in D-004. The reactor
  inlet converted to mole fractions is 30.0 % C2H4, 8.0 % O2, 1.0 % CO2, 51.9 % CH4,
  7.9 % Ar and 0.9 % C2H6, as stated.
- **Purge closes the inerts.** Ar in 184 kg/h equals Ar in the purge, 184 kg/h. CH4 in
  502.9 kg/h equals purge 483 kg/h plus vent 19.6 kg/h.
- **Glycol section.** Water:EO is 20.0 at S24, and an adiabatic rise of about 54 K
  (423 to 478 K) matches 23.4 MW. MEG per t ethylene of 1.68 checks:
  1.314 t EO x 0.9067 x 62/44.
- **Water balance per kg MEG.** Make-up 0.230 kg plus combustion water about 0.11 kg covers
  hydration consumption of 0.305 kg plus the bleed of 0.0305 kg.
- **Reaction heats.** -105 kJ/mol for EO and -1323 kJ/mol for combustion agree with
  formation enthalpies. -95 kJ/mol hydration is plausible for the aqueous phase (ASSUMED).
  R-101 heat of 83.5 MW = 887.7 x 105 + 156.7 x 1323 kJ/h.
- **Compressor power** 4.36 MW is reproduced by hand: 38.7 kmol/h x 10^3, ratio 1.13,
  kappa 1.25, efficiency 0.75. **MEG column reboiler** 25.6 MW equals 806 kmol/h x 2.2 x
  52 kJ/mol.
- **LCI.** Per kg MEG with mass allocation 92.0 %. Feeds, utilities and wastes are all
  declared `missing:` with a description, and nothing is zero-filled. No licensed (ecoinvent)
  values. `lca/mappings.yaml` holds only the steam unit override. Emission exclusions are
  declared with BREF locators.
- **Sources** carry locators: BREF chapter and section, page numbers in reactions.yaml, and a
  source register in DESIGN.md with read status and reuse terms. The licensed reference
  (Ullmann) is marked not read and no value is used.
- **Third-party content.** No tables, figures or passages copied: ranges and facts are restated
  in the case's own words and cited.
- **Honesty of the record.** process.yaml (`validation.status: unreviewed`, notes on the
  maturity gap) and the run report disclose the open gated steps (kinetics, energy
  closure) and the core `_reactor_rules` bug and its workaround.

## Not checked
- Rendered BFD/PFD drawings (generated; no tile sweep).
- `scripts/eg_balance.py` was read for the energy section only; the recycle iteration was not
  re-run (`eg_balance.py build`). The stream table was checked through `cheme process streams`
  and the hand balances above.
- Thermodynamic consistency of the assumed temperatures and pressures (no property package
  covers these streams). Absorber and stripper duties beyond order of magnitude.
- The BREF figures themselves were not re-read against the PDF in this review; the cited ranges
  were taken as stated and only checked for internal consistency.
- Atlas build (`scripts/build_lci.py --strict`) was not re-run.
