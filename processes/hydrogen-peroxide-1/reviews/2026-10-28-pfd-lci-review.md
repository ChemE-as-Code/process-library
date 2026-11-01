---
topic: design
reviewed_commit: 9ab8b97846e487d293b3931384780b1c8ede9442
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, scripts/hp_balance.py, lca/, equipment/equipment-list.yaml, piping/line-list.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/hydrogen-peroxide-1
merge: pending
---
# Review: design (concept PFD and preliminary gate-to-gate LCI)

Independent review of the hydrogen peroxide (anthraquinone autoxidation) case study, issue #170,
branch `case/hydrogen-peroxide-1` (5 commits ahead of `origin/main`, scaffold to run record
20261028-145923-design). The reviewer did not write the design. Every command below was re-run
by the reviewer at the reviewed commit; the design run's report was not taken on trust.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | PFD | R-101, R-201, WS loop, Q06/Q07 (`scripts/hp_balance.py:219-220`, `process/flowsheet.yaml` S04A/S05/S13/S26) | The equipment duties contradict the stream temperatures. R-101 sends the whole heat of reaction (6393 kW, Q06) to cooling water, yet the working solution heats from 313 K (S04A) to 333 K (S05). At 710 t/h and roughly 1.8 kJ/(kg K), that 20 K rise needs about 7 MW, about the same as the reaction heat, so the hydrogenator as written is close to adiabatic and Q06 is counted twice. The WS then has to come back down from 328 K (S13) to 313 K (S26) before C-301 (about 5.4 MW), but no cooler or duty is shown for that. The ~0.7 MW of latent heat for the ~1.1 t/h of water evaporated in the WS dryer V-303 is not shown either. The plant's total cooling-water heat (1.23 kWh/kg in the LCI) is about right, since the loop is cyclic, but the duties per item would mislead equipment sizing and later heat integration. | medium | open | Choose one consistent basis: either isothermal reactors (S05 = S04A temperature) with the reaction heats on R-101/R-201, or adiabatic R-101 plus a WS cooler (new step and equipment item) between V-201 and C-301 carrying the loop's heat. Add the V-303 evaporation heat. Make the hand energy balance of the WS loop close in `hp_balance.py` and record it in D-010. |
| 2026-10-28-pfd-lci-review#2 | PFD | P-101, Q02 (`scripts/hp_balance.py:229`, D-010) | The pump power assumes an 800 kPa rise, but the stream table raises S04 from 101 to 500 kPa(a) (about 400 kPa). Q02 (242.5 kW, about 11 % of the electricity in the LCI) is therefore about twice what the streams imply, and nothing records why. | low | open | State the loop pressure drop that justifies 800 kPa (filters, hydrogenator bed, oxidiser head) and set the S04A pressure to match, or compute Q02 from the streams. |
| 2026-10-28-pfd-lci-review#3 | PFD | K-201 (D-007) | A single uncooled stage at pressure ratio 4.4 discharges at 496 K (223 C). An air compressor of this size would normally be intercooled, which takes roughly 10-15 % off Q01 (the largest electric load). D-007 names only the expander as an option. | low | open | Record the single stage as a deliberate simplification in D-007, or use two intercooled stages. |
| 2026-10-28-pfd-lci-review#4 | PFD | C-501, S20/S28 (D-010) | All organics in the crude (DIBC, TMB) leave with the bottoms product, none with the distillate. DIBC and TMB are steam-volatile, so most would normally go overhead at 10-12 kPa. The product organics (100 mg/kg) and their route to effluent are a guess presented without saying so. | low | open | Mark the organics split in C-501 as ASSUMED in D-010, or send them mostly to the distillate. |
| 2026-10-28-pfd-lci-review#5 | - | `process/design-basis.yaml` assumptions (heats of reaction) | "oxidation 77.5 kJ/mol" has no sign, while reactions.yaml and D-005 use -77.5 kJ/mol (exothermic). | low | open | Write -77.5 kJ/mol (released). |
| 2026-10-28-pfd-lci-review#6 | - | `lca/lca.yaml` emission:DIBC | The inventory lists emission:DIBC at 0 kg. The DIBC slip through the adsorbers is lumped into TMB (D-009), so a 0 row can be read as "no DIBC emitted". The note in `source:` explains it, but `inventory.csv` and `results.md` show only the 0. | low | open | Either drop the exchange until a case has DIBC slip, or split the 20 mg C/Nm3 between TMB and DIBC by the S15 ratio. |
| 2026-10-28-pfd-lci-review#7 | - | `lca/results.csv` | The generated CSV has a baseline climate-change total of 0 kg CO2-eq, while `results.md` correctly says "no total (every contribution a gap)". Anyone reading only the CSV sees zero impact. This comes from the cheme output format, not from the design. | low | open | Report it to cheme-as-code core (the total should be empty or "n/a" when every contribution is a gap). Until then, say in lca/README.md or D-013 that the CSV total is not a result. |

No critical or high findings.

## Previous findings
None: this is the first review of this process (`reviews/` held only README.md at 9ab8b97).

## Drawing
No P&ID exists (out of scope for this run). `cheme validate` printed no `drawing <sheet>:` line,
because the drawing lint runs on P&IDs only. BFD.xml and PFD.xml are generated by `cheme process
build` from the YAML, and `cheme impact` reports "nothing to review" (not stale). I rendered the
PFD once as a whole (`build/PFD.png`, scale 2): five blocks, all 18 steps, feeds on the left,
products on the right, long recycle lines underneath. I read it for completeness against the
flowsheet only; I did not check labels or tiles.

## Checked and fine
- **Scope**: only files under `processes/hydrogen-peroxide-1/` changed (`git diff --name-only
  origin/main..HEAD` outside the folder: 0 files). The route (AO process: Pd hydrogenation, air
  autoxidation, water extraction, purification, vacuum concentration, WS drying and regeneration)
  and the boundary (H2 as a boundary feed linked to hydrogen-1 / chlor-alkali-1, product 50 wt%
  within the 50-70 wt% of the case notes) match the case notes of issue #170.
- **cheme validate**: 16 files, 0 errors, 0 warnings. Infos only: the D-023 example comment in
  checks.yaml from the template, and the DEXPI loader's port cycles. Sheets compared: BFD, PFD.
  Not compared: the P&ID cross-checks of the lists (no P&ID).
- **cheme check**: all concept gates ok (design-basis, concept-lists, process-concept,
  process-balances, assumptions-marked). The basic/detail gates that fail (pids-exist,
  design-review, layout-*, mto, datasheets, ...) are outside this run's scope. design-review
  fails only because no record existed; this record addresses that.
- **cheme maturity**: calculation maturity none, claimed design maturity concept, which gives
  `cheme.maturity-claim-exceeds` (warning). `concept` is the lowest value of the
  `process.schema.json` enum, and process.yaml says outright that maturity reaches no level and
  why (assumed feeds and separator specifications, energy closure not evaluable, unreviewed). I
  judge the claim honest, consistent with the other library processes.
- **cheme process propagate --check**: exit 0, nothing stale. **cheme process streams**: every
  block (HYD, OXI, EXT, CON, WSR) and all 18 steps balance in mass. The extents are consistent:
  HYD 189.43, HPD 5.52, OXD 189.43 kmol/h.
- **Hand checks of the key numbers** (reviewer's own arithmetic from the stream table):
  - H2: (189.43 + 5.52) kmol/h × 2.016 + 1 % vent = 397 kg/h = 63.5 kg/t (stoichiometric 59.3).
  - Air: O2 246.3 kmol/h for 189.4 needed, i.e. 30 % excess; 4212 Nm3/t; off-gas about 5.7 vol% O2.
  - WS productivity 8.4 kg H2O2/m3; EAQ 421 kmol/h × 45 % = 189 kmol/h.
  - K-201: T2 496 K, 1881 kW.
  - C-501: vapour 1.3 × 3105 kg/h, 2669 kW condenser and 2963 kW reboiler.
  - Electricity 355 kWh/t; steam about 2.3 GJ/t; total about 3.6 GJ/t.
  - Reaction heats from the NIST formation enthalpies: HPD -383.88, HYD -110.3 kJ/mol.
  - Extraction 97.0 % to 40 wt% crude; water balance over C-301 closes.
  - Solvent outlets sum to the 15.63 kg/h make-up; waste water 0.41 t/t with 0.155 kg C/t.
  - All of these are plausible for the AO process and lie inside the BREF ranges the design
    cites. The reboiler above the BREF range is disclosed with its reason (D-010).
- **Provenance**: every feed, separator outlet and duty in flowsheet.yaml carries `provenance:
  assumed` with a D-xxx or `hp_balance.py` source (144 assumed values, 163 `source:` fields). The
  design basis marks its values ASSUMED. The conversions are labelled assumed with the BREF limit
  they respect. No kinetics were invented (D-005). Leads that were not read (Ullmann's,
  Campos-Martin) are listed as not read.
- **Licences**: DESIGN.md cites the BREF by section and table and restates each number in its own
  words. No table, figure or passage is reproduced. EU reuse is recorded (Decision 2011/833/EU).
  No licensed database value is anywhere in lca/ (`factors.yaml` has no factors; it includes only
  the packaged open desnz profile).
- **LCI**:
  - Functional unit 1 kg of 50 wt% product (PROD).
  - Every foreground exchange is taken from a flowsheet stream.
  - Mass closes: 43 432.96 kg/h in and out per `manifest.json`. The flowsheet streams give
    43 394.75 kg/h in = out (my sum), and the ASSUMED consumables add 38.2 kg/h.
  - The off-gas aggregate is counted through its emission:* components, not twice.
  - The consumable rates per year convert correctly per FU (e.g. HNO3 4 kg/t H2O2 = 0.002 kg/kg).
  - `cheme assess lca --coverage`: partial, 23 gaps. Every background is `missing:` with a
    description of the activity to link, and nothing is zero-filled. The uncharacterised
    emissions (H2, TMB, DIBC) are reported as gaps.
  - Per-process overrides are in this folder's `lca/mappings.yaml` (LPS as heat; H2 and STEAMD
    `atlas: false` with reasons). The shared `lci/mappings.yaml` is untouched.
  - Facts cite the BREF with a section/table locator.
- **process.yaml**: `publication.status: internal`, `validation.status: unreviewed`, references
  with DOIs, and the missing registry entries named.

## Not checked
- I did not check the BREF locators and ranges against the document itself (I had no copy). They
  were checked only for plausibility against general knowledge of the AO process.
- Energy balances in cheme (not evaluable) and the extraction equilibrium:
  both are gated in core, as D-006 states.
- `scripts/build_lci.py --strict` of the library (not re-run; the design report says it exits 1
  for an environment reason common to all processes).
- The equipment and line list design data (design pressures, temperatures, line sizes from
  D-012), beyond `cheme validate`'s process-link check.
- H2O2 decomposition losses, fugitive/storage VOC and process safety: declared open (D-005,
  D-011), and no HAZOP is in scope.
- Labels and drawing quality of the generated BFD/PFD (only the whole PFD was viewed).
