---
topic: design
reviewed_commit: ff431c61c241c157c4bbfef9d93e180b801607d3
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, lca/, scripts/balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/hydrazine-1
merge: pending
---
# Review: design (concept PFD and preliminary LCI, issue #141)

Independent review of the hydrazine hydrate (peroxide, PCUK methyl ethyl ketazine) case as
committed at `ff431c6`. I did not write the design and changed no design file. Every command
below was re-run by me; the run report was not taken on trust.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | PFD | C-401, Q05; lca/inventory.csv feed:MPS | The hydrolysis column steam (2 627 kW, `process/flowsheet.yaml` Q05) is a hand estimate that DESIGN.md D-010 itself calls a lower bound: the endothermic hydrolysis heat is left out, and it assumes reflux 1 for a 40-50 tray reactive distillation column. It still enters the LCI as a single central value (feed:MPS 6.21 kWh/kg) marked only `assumed`. Hydrolysis plus concentration come to about 4.8 t steam per t hydrate here. Only the reader of D-010 learns that the true value is higher. | medium | open | State the lower-bound character next to the exchange (the `source:` of feed:MPS in `lca/lca.yaml`, process.yaml notes), and add a high-steam scenario (e.g. C-401 at reflux 2-3 plus a hydrolysis heat estimate) until I-02 lets the column be simulated. |
| 2026-10-28-pfd-lci-review#2 | PFD | R-101, V-101, S07 | The reactor and decanter vent is oxygen-rich. The DECOMP reaction gives an off-gas of about 59 mol% O2 (S07), which also carries MEK (vapour pressure about 35 kPa at 323 K) and NH3. Neither DESIGN.md nor the design basis records an inerting or nitrogen-sweep decision, or the flammability of the headspace ahead of the lumped vent condenser. A nitrogen sweep, the usual answer, would add an N2 feed and change the vent mass and the MEK/NH3 losses in the LCI. | medium | open | Add a decision (DESIGN.md, linked to I-04): inert the headspace (N2 sweep to keep O2 below the limiting oxygen concentration) or justify why not. If a sweep is chosen, add it as a feed and rebalance S07. |
| 2026-10-28-pfd-lci-review#3 | PFD | R101 selectivity (D-004) | The azine yield of 0.85 mol/mol H2O2 was chosen between the batch examples (81-82 %, S1) and "up to about 90 %". The only continuous example (S2 Ex. 1, which I re-checked: 3 900 kg/h azine per 1 000 kg/h H2O2) implies about 95 % if the azine is pure. H2O2 is likely the largest background burden, and each point of yield moves H2O2 demand by about 1.2 %, so the choice may overstate H2O2 use by up to about 10 %. The choice is disclosed, but no scenario carries it. | low | open | Keep 0.85 if wanted, but add a yield scenario (0.81 / 0.95) to `lca/lca.yaml` or to process.yaml notes, and close I-01 with Hayashi et al. 1976. |
| 2026-10-28-pfd-lci-review#4 | - | lca/inventory.csv feed:H2O2 | feed:H2O2 is 1.147 kg of **70 wt% solution** per kg hydrate, i.e. 0.803 kg H2O2 (100 %). Common background datasets are stated per kg of H2O2 (100 %, "in solution"). The `missing:` text names "70 wt% in water" but does not say that the quantity is the solution mass, so a later mapping risks an error of a factor of 0.7. | low | open | Say in the `missing:`/`source:` text that the quantity is the solution mass (0.803 kg H2O2 100 %) and that the mapping must convert. |
| 2026-10-28-pfd-lci-review#5 | PFD | Q08 (D-010) | The R-101 heat of reaction uses NH3(g) for all ammonia, but the fresh ammonia (S02, 1 444 kg/h) enters as a liquid. The heat of dissolving NH3 and the recycle vapour (S23) in the working solution is not counted either. The phrase "lower bound" for Q08 is therefore not shown to hold: the liquid feed lowers the exotherm by about 0.5 MW and dissolution raises it. | low | open | Restate the Q08 estimate with the feed phase of each NH3 stream, or call it an order-of-magnitude estimate instead of a lower bound. |
| 2026-10-28-pfd-lci-review#6 | - | process.yaml:304 `maturity: concept` | `cheme maturity` gives calculation maturity "none" and warns `cheme.maturity-claim-exceeds`. The schema has no level below `concept`, and process.yaml says so honestly (comment and `validation.notes`), so the claim does not mislead. The warning still stands. | low | open | A human accepts the warning for the concept case. Alternatively, give the feed basis provenance (capacity choice) and sourced separator specifications so that `sourced` is reached. |
| 2026-10-28-pfd-lci-review#7 | - | DESIGN.md S5 | The NIST formation enthalpies are recorded as "values as commonly tabulated, not re-fetched in this run". The values I checked against general knowledge (H2O2(l) -187.8, H2O(l) -285.83, NH3(g) -45.9, N2H4(l) +50.6 kJ/mol) are right. The locator is only the WebBook home page, so a reader cannot trace each value. | low | open | Re-fetch each species page and give its URL or CAS-based locator in the source register. |
| 2026-10-28-pfd-lci-review#8 | - | equipment/equipment-list.yaml R-101 notes | The note on H2O2 materials (passivated stainless steel) points to "open item I-06", but I-06 is the 2-butanol bleed decision. No open item covers materials of construction. | low | open | Point the note to a new open item (materials for H2O2/hydrazine service), or drop the reference. |
| 2026-10-28-pfd-lci-review#9 | - | lca/results.csv | The generated results.csv has a `total` row with impact `0` for climate change, although every contribution is a gap and results.md says "no total". A reader of the CSV alone sees a zero footprint. This is generated by `cheme assess lca --write` (thf-1 on main shows the same) and must not be hand-edited. | low | open | Report it to cheme-as-code: write an empty total with status "gaps". Until then, note it in process.yaml `lca.notes`. |

## Previous findings
None: this is the first review record of hydrazine-1 (`ls reviews/` at ff431c6 shows only
README.md).

## Drawing
No P&ID exists at this stage (`pid/` is empty; the gate `pids-exist` fails, as expected at concept).
`cheme validate` prints no `drawing <sheet>:` line, because the drawing lint runs on P&IDs only.
BFD.xml and PFD.xml are generated from `process/*.yaml` (`process-basic` gate ok: current, no
stale values). I did not render or read them in tiles (see Not checked).

## Checked and fine
- **Branch content**: `git diff --stat origin/main...HEAD` (merge base cc5624f) changes only
  files under `processes/hydrazine-1/` (190 files). The two-dot diff against `origin/main` also
  shows thf-1 deletions. That is only because main has advanced since (thf-1 merged in cbdf84a),
  not a change on this branch. The branch needs a merge from main before it goes in.
- **Re-run**: `cheme validate`: 16 files, 0 errors, 0 warnings. It compared 2 sheets
  (BFD, PFD) and 12 lists. Skipped: lists vs P&IDs, since there are no P&IDs. The only infos
  are `cheme.decision-unknown` D-023, from a commented template example in checks.yaml, and
  loader cycles. `cheme check`: every concept/basic process gate is ok. Failing gates:
  `layout-plot-plan`, `pids-exist`, `design-review` (this record), and the layout,
  lifting, mto, electrical, hvac and datasheet gates, all outside a concept PFD/LCI scope and
  as the run report says. `cheme maturity`: calculation maturity none, review status
  unreviewed (#6). `cheme process propagate --check`: no output (nothing stale, nothing to
  fill). `cheme process streams`: all 4 blocks and 11 steps close. Extents: AZINE 40.14,
  BUTANOL 1.42, DECOMP 2.13, AMIDATION 1.60, HYDROLYSIS 39.94, ISOMERISATION 0.20 kmol/h, as
  DESIGN.md says.
- **Route and boundary**: peroxide/PCUK MEK-ketazine route as issue #141 asks. H2O2 and NH3 are
  boundary feeds. Product is 64.0 wt% N2H4 (= N2H4·H2O, 32.046/50.06). Anhydrous hydrazine is
  excluded, and the boundary memo says so.
- **Balance and stoichiometry, hand-checked**: the reactions are element-balanced (AZINE,
  BUTANOL with N2 release, DECOMP, AMIDATION, HYDROLYSIS, ISOMERISATION). H2O2 47.2 kmol/h
  (1 606 kg/h, 2 294.8 kg/h at 70 %); 0.85/0.03/0.045 per kmol H2O2 reproduce the extents.
  NH3 demand 2×40.14 + 2×1.42 + 1.60 = 84.7 kmol/h, against 84.8 fed. N2H4 39.94 kmol/h =
  1 280 kg/h = 2 000 kg/h × 0.64. Inlet ratios from S05: MEK/H2O2 2.20, NH3/H2O2 2.50.
  Hydrolysis water/azine 10.46 (S44). S47 is 30.0 wt% hydrate (19.2 % N2H4), so C-402 removes
  4 665 kg/h of water. The hydrolysis loop water balance closes (7 564 kg/h in = 1 439
  consumed + 712 + 28 + 5 385). Working solution 17 670 kg/h = 11 × 1 606 (S2 Ex. 1).
  Boundary 6 888.4 kg/h in = out.
- **Plausibility**: H2O2 1.255 and NH3 1.128 kg per kg N2H4 (stoichiometric 1.061/1.063). MEK
  make-up 0.093 kg/kg H2O2 against 0.100 in S2 Ex. 1. Steam about 13 kg/kg hydrate, 55 % of it
  regeneration. The regeneration figure is about 2.7× the bare latent heat of the 5.15 t/h
  C-201 overhead, so it is not understated. The heat of reaction −241.5 kJ/mol
  (H2O2 + 2 NH3(g) → N2H4(l) + 2 H2O(l)) checks against the stated formation enthalpies. The
  energy streams are consistent unit by unit (reboilers 16 405 kW, condensers and cooling
  18 894 kW, the difference being the R-101 exotherm and the sensible heat of the products).
- **Sources**: I re-fetched US 6,605,265 Ex. 1 myself. H2O2 1 000 kg/h (from 70 %), NH3 1 000,
  MEK 100, acetic acid 60, Na2HPO4 3, working solution 11 000, azine 3 900 kg/h, column head
  0.9 bar(a), base 180 °C and reboiler steam 10 500 kg/h at 18 bar(a) all match DESIGN.md S2.
  The patent says the EDTA stabiliser and, in Ex. 2, the preheater are on the same steam, which
  is consistent with D-010 not adding the E-201 duty. Every key value is either sourced
  (patent section or example) or marked ASSUMED, in the flowsheet provenance, the design basis
  and the decisions. Ullmann's (licensed) stays a lead and was not read.
- **Third-party content**: none copied. Patent facts are restated in our own words. The ASCII
  block diagram and the route table are the author's own. Wikipedia (CC BY-SA) is used for
  facts only.
- **LCI**: functional unit 1 kg HH (64 wt% N2H4). Inventory inputs 3.44422 kg = outputs
  3.44422 kg. `cheme assess lca --coverage`: mass, element and carbon-origin balances closed;
  16 gaps (14 backgrounds `missing:` with a description of the activity, plus NH3 and MEK
  uncharacterised in GWP100), none zero-filled (except #9). No licensed background value. The
  steam override is in the folder's `lca/mappings.yaml` (`steam-heat`, which exists in the
  shared `lci/mappings.yaml`). The exclusions are listed with reasons and not claimed
  negligible. `process.yaml` has `lca.source: none` and claims no impact.
- **process.yaml**: `publication.status: internal`, `validation.status: unreviewed`, and the
  maturity disclosure is honest (#6). The references match the source register.

## Not checked
- The BFD/PFD drawings were not rendered or read in tiles. They are generated and current per
  `process-basic`; their layout and legibility were not judged.
- `scripts/balance.py` was not re-run or read line by line. Its outputs were checked through
  the stream table and the hand balances above.
- Sources S1, S3, S4, S9 and the Wikipedia page were not re-fetched. Only S2 Ex. 1 (the
  largest LCI driver) was. The NIST values were checked against general knowledge only (#7).
- Column duties other than the regeneration were not recalculated beyond order-of-magnitude
  checks. No property package covers the mixture (D-011), so they cannot be verified by
  simulation.
- The library-level LCI build (`scripts/build_lci.py --strict`) and the test suite were not
  re-run.
- Safety (relief, HAZOP, hydrazine and H2O2 hazards) beyond #2, layout, datasheets and cost
  are outside the concept scope.
