---
topic: design
reviewed_commit: 4b05909c04bb4ddae3c98b28f984cb13c207eb37
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/reactions.yaml, process/materials.yaml, process/simulation.yaml, scripts/balance.py, lca/lca.yaml, lca/mappings.yaml, lca/inventory.csv, lca/gaps.csv, lca/results.md, lca/dataset.yaml, equipment/equipment-list.yaml, PROGRESS.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/ethylene-1
merge: pending
---
# Review: design (concept BFD/PFD and preliminary gate-to-gate LCI), ethylene-1

Independent agent review of the ethane steam cracker case (issue #176), branch `case/ethylene-1`,
commits `0859ac6`..`4b05909` over `origin/main` (`11d50ef`). Nothing was changed in the design
files. The finding ids follow `reviews/README.md`; the task's labels R-01.. are given in the
finding text.

Re-run by the reviewer at `4b05909`:

- `cheme validate`: `17 file(s): 0 error(s), 0 warning(s)`; compared the BFD and PFD and 12 lists;
  no P&ID, so equipment, line and instrument cross-checks were skipped. Infos only: `cheme.decision-unknown`
  for `D-320` (this is the dryer tag, not a decision id) and `D-023` (a commented template example in
  `checks/checks.yaml`).
- `cheme check`: concept process gates ok (design-basis, concept-lists, process-concept,
  process-balances, assumptions-marked, process-links); basic `process-basic`, `process-links`,
  `pids-valid`, `drawing-clean` ok. Failing: `layout-plot-plan` [concept], `pids-exist`,
  `design-review` (until this record), `layout-3d`, `lifting-study`, `mto`, `layout-review`
  [basic], `layout-detail`, `electrical`, `hvac`, `datasheets` [detail]. P&IDs, layout and datasheets
  are outside this run's scope (task.md).
- `cheme maturity`: calculation maturity **none**; `sourced.boundary` FAIL (feed flows and
  compositions ASSUMED), `balanced.model-basis` FAIL (H102, T201, D210, T310, D320, V402, R501, R601
  unsourced); warning `cheme.maturity-claim-exceeds` (concept claimed, evidence supports none).
- `cheme process streams`: every block and step balance `ok` (CRK, CRK3, QW, CGC, CHL, C2F, C3F and
  all 26 steps); no STALE value.
- `cheme process propagate --check`: exit 0, no output (nothing to change).
- `cheme assess lca --coverage`: partial screening carbon footprint, 14 gaps (12 declared missing,
  NOx and CO outside the GWP method), balance at 5 %: mass, element and carbon-origin closed,
  energy closure 57.8 % (utilities only, explained in D-012); publishable.
- `git diff --name-only origin/main..HEAD`: every changed file is under `processes/ethylene-1/`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | - | process.yaml:54 (chemistry.outputs emission:CO2 note); DESIGN.md:151 D-016 ("the inventory itself is unallocated"), DESIGN.md:175 D-018 ("Furnace CO2 0.43 kg/kg ethylene, unallocated") | R-01: the headline CO2 figure is mislabelled. 0.433 kg CO2/kg ethylene is the **mass-allocated** value (ethylene share 91.6 %, `lca/results.md` Allocation table); the unallocated value is 59 056 kg/h / 125 000 kg/h = 0.472 kg/kg (0.473 kg CO2-eq with CH4/N2O, results.md row `none`). `lca/inventory.csv` is allocated too (feed:ETHANE 1.16133 = 158 554/125 000 x 0.9156; product:FLUE 6.0038 = 6.5575 x 0.9156), only `lca/dataset.yaml` (per hour) is unallocated. The Atlas manifest and DESIGN.md therefore state a gate-to-gate CO2 9 % lower than the gross figure while calling it gross. (The run report repeats the label, but run records are not edited.) | high | open | Relabel: "0.433 kg/kg ethylene, mass-allocated (91.6 %); 0.472 kg/kg unallocated" in process.yaml and D-018; correct D-016 to say that `inventory.csv` is per FU with mass allocation applied to inputs and emissions while co-products are listed unallocated, and `dataset.yaml` is the unallocated dataset. |
| 2026-10-28-pfd-lci-review#2 | PFD | T502, T401, K701 (Q401, Q402, Q501, Q503); scripts/balance.py:394-418 | R-02: the refrigeration duty and power are not internally consistent. D-014 says the C2 splitter and demethaniser reboilers are "heat-integrated", but neither reboiler duty exists in the flowsheet and nothing is credited against the refrigeration load (the C2 splitter condenser Q503 = 56.9 MW is charged in full to K701), so ~57 MW of reboiler heat appears from nowhere; the deethaniser condenser (Q501 = 39.0 MW) uses the latent heat of ethane for an overhead that is 67 mol% ethylene close to its critical point. Result: refrigeration shaft power 78.3 MW, about twice the CGC (40.6 MW), whereas in ethane crackers the CGC is normally the largest machine. This feeds feed:POWER (0.871 kWh/kg) and the 3.4 GJ/t of D-018. | medium | open | Add the T502/T401 reboiler duties as energy streams with their heat source (propylene refrigerant condensing, or cracked-gas chilling) and credit them against K701; use the mixture's latent heat (or flag as ASSUMED upper bound); re-check the CGC/refrigeration ratio, or state in D-014/D-018 that the refrigeration power is a conservative upper estimate. |
| 2026-10-28-pfd-lci-review#3 | - | lca/lca.yaml allocation; product:HPS; D-015 | R-03: the SHP steam export (2.47 kWh/kg, 337 MW, 416 t/h) carries no burden: it is outside the mass allocation and only a "missing" gap, while the fuel that superheats and preheats it (convection duty Q102 = 196 MW, ~32 % of the 611 MW fired) and its CO2 are allocated entirely to the hydrocarbon products, and the compressors are additionally charged as grid power (D-015). The per-kg CO2 and the power input are therefore both gross. D-015 discloses the drive choice, but neither `process.yaml` nor `lca/results.md`'s source text says that the CO2 per kg includes the fuel of an exported steam stream. | medium | open | State it next to the CO2 figure in process.yaml and in the lca.yaml allocation `source:`; add a scenario (steam-turbine drives netting HPS against POWER, or substitution of the HPS export) before the allocation is decided. |
| 2026-10-28-pfd-lci-review#4 | - | process.yaml:34-50 (maturity, validation.notes) | R-04: the manifest's honesty note is incomplete. `cheme maturity` gives calculation maturity **none** (sourced.boundary fails because capacity and feed are ASSUMED; balanced.model-basis fails for H102, T201, D210, T310, D320, V402, R501, R601) and warns `cheme.maturity-claim-exceeds`. `concept` is the lowest enum value, so the claim cannot be lowered, but the notes only quote `cheme validate: 0 errors, 0 warnings`, and the run report wrongly says the plant "does not reach balanced" as if it reached sourced. | medium | open | Add to validation.notes: "cheme maturity: calculation maturity none (sourced boundary: feed and capacity ASSUMED; unsourced splits and conversions); concept is claimed as the lowest manifest level, cheme.maturity-claim-exceeds acknowledged." |
| 2026-10-28-pfd-lci-review#5 | - | DESIGN.md D-018 | R-05: "Ultimate ethylene yield 0.788 kg/kg fresh ethane" is per kg of fresh **feed** (S101, 95.8 wt% ethane); per kg ethane it is 0.823 kg/kg (125 000 x 0.9995 mol basis / 151 900 kg/h ethane). Both are plausible for ethane cracking; the label is ambiguous and the run report says "per kg ethane". | low | open | Write "0.788 kg/kg fresh feed (0.82 kg/kg ethane)". |
| 2026-10-28-pfd-lci-review#6 | - | DESIGN.md D-018 | R-06: shaft power 3.42 GJ/t at 35-40 % power-plant efficiency is 8.6-9.8 GJ/t primary, not "about 9-10", so it sits at or below the lower end of the BREF 9.8-12.5 GJ/t, not "inside" it; and it compares electric-drive shaft power with a range that includes the separation's steam and refrigeration. | low | open | Correct the arithmetic and soften the comparison (see also #2). |
| 2026-10-28-pfd-lci-review#7 | - | lca/lca.yaml emission:CO2 `source:` | R-07: the source says the flue CO2 includes "the feed CO2". The feed CO2 (0.2 mol% of S101) is removed in T310 as Na2CO3 (extent CAUSTIC 10.44 kmol/h) and leaves in the spent caustic, not the flue gas. | low | open | Drop "and of the feed CO2" (or say it leaves with the spent caustic as carbonate). |
| 2026-10-28-pfd-lci-review#8 | - | process/reactions.yaml H103 set; H101 | R-08: (a) the fresh feed's propane (2.5 mol%) passes the ethane coils uncracked (propane rises across H101) and is cracked only in H103 via the C3 splitter; (b) H103 reproduces three BREF propane yields and puts the rest into CH4 (25 wt%) with only 0.3 wt% H2 and no C4+, at 82 % conversion. Disclosed in part in D-005; effect on the plant is small (7.6 t/h of 225 t/h hydrocarbon feed). | low | open | Add one sentence to D-005 on (a) and on the H2/C4+ slate of the propane coil. |
| 2026-10-28-pfd-lci-review#9 | - | D-009, S304/S305 | R-09: 3 mol NaOH per mol CO2 is ASSUMED without a source and leaves one third of the NaOH unused; together with the assumed 0.2 mol% feed CO2 it gives 10 kg NaOH and 95 kg spent caustic per t ethylene, both of which go straight into the LCI. | low | open | Source the ratio and the feed CO2, or flag the caustic and spent caustic exchanges as upper-bound assumptions in lca.yaml. |
| 2026-10-28-pfd-lci-review#10 | - | checks/checks.yaml gates | R-10: `cheme check` fails the concept gate `layout-plot-plan` (and basic/detail gates for P&IDs, layout, lifting, MTO, datasheets). They are outside this run's scope (task.md), but a concept sign-off would be refused while `layout-plot-plan` fails. | low | open | Either produce the plot plan at concept or record in DESIGN.md/STAGES.md that the case study is not taken to a concept sign-off; no change needed for this PR. |

## Previous findings
None: this is the first review record of ethylene-1 (`reviews/` held only README.md at 4b05909).

## Drawing
No P&ID in `pid/` (out of scope). The BFD and PFD are generated by `cheme process build`
(`kind: bfd|pfd`); `cheme validate` printed no `drawing <sheet>:` line for them and no
generated-sheet drift. `build/PFD.png` (full sheet, scale 1) was rendered and looked at as an
overview only: seven block frames in flow order, utility lines routed around the frames; labels
are not legible at that scale and no tile was read.

## Checked and fine
- Route and boundary: ethane cracking chosen and justified (D-001); the deviation from the issue's
  co-product list (no pyrolysis fuel oil) is stated and reasoned; furnaces, TLE, quench, 5-stage
  CGC with caustic wash after stage 3, drying, cold box, front-end demethaniser, deethaniser,
  tail-end acetylene and MAPD converters, C2/C3 splitters, debutaniser all present. Furnace CO2
  and NOx are in the LCI. Boundary feeds from other library processes (NaOH from chlor-alkali-1)
  are noted.
- Plant balance by hand: feeds 971 288 kg/h (ethane 158 554, NG 9 627, air 788 489, BFW 2 093,
  caustic 12 526) against products 971 290 kg/h. Water loop: 69 766 kg/h dilution steam out of
  D210 = quench 58 074 + KO 10 029 + 1 200 + dryer 464; blowdown 3.0 %. Dilution steam 0.30 kg/kg.
- Water content after quench and drums matches saturation at 40 C (y = 7.38 kPa / P: 0.0492 at
  150 kPa, 0.0073 at 1010 kPa, 0.0021 at 3600 kPa).
- Ethane conversion in H101 recomputed from S105/S106: 70.1 %. Ethane recycle 66 t/h consistent
  with 70 % per pass. Product slate per t ethylene (propylene 26 kg, crude C4 35 kg, pygas 31 kg,
  H2 to fuel 76 kg) plausible for ethane feed. Acetylene converter H2 = 1.5 mol/mol checked (S403).
- Firebox: fuel LHV recomputed 610.7 MW (stated 611 MW, 17.6 GJ/t); air gives 15 % excess, 3.16 %
  O2 dry; flue CO2 1 342 kmol/h = 59.1 t/h (matches dataset.yaml 59 056 kg/h). Coil duty
  372 MW consistent with ~174 MW cracking endotherm plus feed and steam heating; SHP steam 416 t/h
  consistent with Q102+Q103 = 337 MW from BFW 115 C to 11 500 kPa(a)/520 C.
- CGC power: an ideal-gas 5-stage check at ratio 1.89, eta 0.78 gives ~42 MW (stated 40.6 MW).
- Emission factors: NOx 100 mg/Nm3 x 239.3 Nm3/GJ = 23.9 g/GJ, CO 12.0 g/GJ; IPCC 2006 Vol. 2
  Table 2.3 natural gas CH4 1 kg/TJ, N2O 0.1 kg/TJ agree with the reviewer's knowledge of that
  table; BREF BAT-AEL 60-100 mg/Nm3 for new furnaces and 10-50 mg/Nm3 indicative CO agree likewise.
- LCI: functional unit 1 kg ethylene; every exchange carries its flowsheet stream ids or an
  estimate id; no zero-filled background and no licensed value (`lca/factors.yaml` only the
  open IPCC GWP values); every unmapped exchange is in `lca/gaps.csv` with a description of the
  background to link; `lca/mappings.yaml` is in the folder and empty on purpose; emission
  exclusions (SOx, decoking, fugitives, flaring, effluents) are declared with reasons, not as
  negligible. The zero emissions (H2, C2H4, C2H6) are flowsheet values after complete combustion,
  marked free.
- Sources and licences: values are restated with locators (BREF section/table, IPCC table); no
  table, figure or passage is copied; BREF Table 3.3 yields are used as input numbers with their
  locator, which the library rules allow. ASSUMED marked throughout design-basis.yaml and
  DESIGN.md; the energy gating on core #315 is stated precisely (D-012).
- Nothing outside `processes/ethylene-1/` changed; publication.status internal, validation
  unreviewed.

## Not checked
- The BREF LVOC 2017 Table 3.3 yields, Table 3.4 dust range and §3.3.4 energy ranges were not
  re-read against the document (no fetch in this review); only plausibility against general
  engineering knowledge was checked. Ullmann's was not read by the author either.
- Column designs, relative volatilities, stage counts and the separation train's energy balance:
  gated on a qualified light-hydrocarbon property package (core #315); not evaluable.
- `scripts/balance.py` was read only in the duty section (lines 370-420); the recycle and
  firebox convergence code was not audited line by line, its results were cross-checked by hand
  (above).
- The PFD drawing in detail (labels, crossings); the BFD was not rendered.
- P&IDs, layout, HAZOP, TEA, datasheets: out of the run's scope.
