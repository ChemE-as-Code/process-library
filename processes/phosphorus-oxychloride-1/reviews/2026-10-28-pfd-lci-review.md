---
topic: design
reviewed_commit: f45ad0859afb9c6b6fef8361a580a3936bad4265
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/BFD.xml, process/PFD.xml, scripts/balance.py, lca/lca.yaml, lca/mappings.yaml, lca/inventory.csv, lca/gaps.csv, equipment/equipment-list.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/phosphorus-oxychloride-1
merge: pending
---
# Review: design (concept BFD/PFD and preliminary gate-to-gate LCI, issue #135)

Independent review of the design session `runs/20261028-162025-design` (commits 18984a9..f45ad08).
Every command below was re-run by the reviewer at f45ad08; the run report was not relied on.

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | PFD | C-301, C-302 reboilers and condensers (Q5-Q8), LCI feed:LPS | R-01: `scripts/balance.py` takes the heats of vaporisation from `thermo` `Chemical.Hvap` (lines 75-77, 144-150). For POCl3 this value is about 20-26 % too low: thermo gives 27.5 kJ/mol at 378.9 K and 30.3 kJ/mol at 298 K, while thermo's own vapour pressure gives 34.6 kJ/mol near the boiling point (Clausius-Clapeyron over 370-388 K, reviewer check `build/review_hvap.py`), and the formation enthalpies the same case uses (materials.yaml, POCl3 gas -558.5 against liquid -597.1 kJ/mol, CRC) give 38.6 kJ/mol at 298 K. PCl3 is consistent (29.7 against 30.7 kJ/mol). C-302 carries nearly all of the steam: its 298.4 kW reboiler/condenser duty would be about 376 kW. LP steam would rise from 0.0907 to about 0.110 kWh/kg POCl3 (+20 %), and the column condenser duty to cooling water by a similar amount. Steam is the plant's main fossil energy input, so the LCI understates it. D-008 checked the liquid cp against thermo and rejected it, but did not check Hvap. | medium | open | Use a POCl3 heat of vaporisation consistent with the vapour pressure or the CRC formation enthalpies (with its source) in `scripts/balance.py`, re-run it, update Q5-Q8, D-008 and the LCI (`cheme assess lca --inventory --write`), and record the check in D-008. |
| 2026-10-28-pfd-lci-review#2 | PFD | R-101 duty Q1, D-004 | R-02: `scripts/balance.py:111` computes the R-101 heat as `p4 * DH_R1 + o2_r1 * DH_R2`. Here `o2_r1` is kmol O2, but `DH_R2` is per kmol PCl3 (`PCl3 + 1/2 O2`), so the heat of the POCl3 formed in R-101 is halved. Check: 6.5584 kmol/h P4 x 1281.3 MJ/kmol plus 1.4138 kmol/h PCl3 x 277.4 MJ/kmol gives 2443 kW, not the 2388.7 kW in Q1, D-004 and process.yaml. Cooling water is about 54 kW low (+0.014 kWh/kg, about 1 % of product:CW). The mass balance is not affected. | low | open | Use `2 * o2_r1 * DH_R2` (or the extent in PCl3), re-run, update Q1, D-004 and the LCI. |
| 2026-10-28-pfd-lci-review#3 | - | lca/lca.yaml feed:NAOH, lca/gaps.csv | R-03: the amount 3.87 g/kg is the mass of the 50 wt% solution (S20), i.e. 1.93 g NaOH (100 %). The `missing:` text names "sodium hydroxide 50 wt% in water" but does not say that the quantity is per kg of solution. Most background activities are given per kg NaOH (100 %), so a later mapping could double-count by a factor of 2. | low | open | State in the `missing:`/`source:` text that the amount is kg of 50 wt% solution (1.93 g NaOH as 100 %), or enter it on a 100 % basis. |
| 2026-10-28-pfd-lci-review#4 | - | lca/lca.yaml functional_unit; emission_exclusions phosphorus-mud | R-04: two small inconsistencies with the sources. (a) The functional unit gives 99.99 wt% POCl3, while D-002 and the design basis give 99.998 wt% (21 ppm PCl3). (b) The phosphorus-mud exclusion says "about 0.4 % of the P feed in CN115259114B", but SRC-3 and D-003 give 0.2-0.5 wt% phosphorus mud, with no 0.4 % and no "of the P feed" basis. The same sentence also names the melt-tank wash water twice. | low | open | Align the purity with D-002; restate the mud range exactly as in D-003 (0.2-0.5 wt%), or mark 0.4 % as ASSUMED. |
| 2026-10-28-pfd-lci-review#5 | - | checks/checks.yaml:76; branch base | R-05: housekeeping. (a) `cheme validate` reports info `cheme.decision-unknown [D-023]`: the template's checks.yaml cites a D-023 that this DESIGN.md does not have (a scaffold leftover, also noted by the author). (b) The branch forks from cc5624f, and origin/main has moved on (thf-1 and acetic-acid-1 merged), so `git diff origin/main..HEAD` shows thf-1 files as deleted. Against the merge base, only `processes/phosphorus-oxychloride-1/` changed (190 files, all additions). | low | open | Drop or reword the D-023 reference in checks.yaml; merge or rebase origin/main before opening the PR so that the PR diff contains only this folder. |

## Previous findings

None: this is the first review record of this process (`reviews/` held only README.md at f45ad08).

## Drawing

No P&ID exists (out of scope; the template's reference sheet was removed, `pid/` holds only README.md), so there are no `drawing <sheet>:` lines. The BFD and PFD are generated by `cheme process build` (`cheme check` gate `process-balances`: BFD current; `cheme impact`: nothing to review). The gate `drawing-clean` is ok. The PFD was rendered (`build/PFD.png`) and read as a whole: all 4 blocks, 10 steps, boundary feeds, products and utility returns are present and connected as in flowsheet.yaml. Cosmetic only: the mixer M201 is drawn with an exchanger-like symbol (generator's choice, not a finding).

## Checked and fine

- **Commands re-run at f45ad08:** `cheme validate`: 16 files, 0 errors, 0 warnings (infos: D-023, port cycles). `cheme check`: concept gates 6 ok, 1 fail (`layout-plot-plan`, out of scope). Basic and detail failures are P&IDs, layout, datasheets and this design review, all out of scope for this run. `cheme maturity`: calculation maturity none, warning `cheme.maturity-claim-exceeds` for the `concept` claim. `cheme process streams`: all 4 blocks and 10 steps close, extents consistent. `cheme process propagate --check`: no deviations reported. `cheme assess lca --coverage`: partial, 14 gaps (11 unmapped backgrounds, 3 uncharacterised chloride emissions), mass and element balance closed.
- **Scope and boundary:** the route matches the issue's case notes: PCl3 is oxidised with O2, and PCl3 is made from white phosphorus and chlorine inside the boundary, with a reason given (D-001). Distillation is included. Feeds made by other library processes (chlor-alkali-1 Cl2 and NaOH, asu-1 O2) enter as boundary feeds with the link noted. Nothing outside `processes/phosphorus-oxychloride-1/` changed against the merge base.
- **Stoichiometry and yields (reviewer hand check):** P need is 30.974/153.33 = 0.2020 kg/kg; divided by the 99.44 % P yield this gives 0.2031 kg/kg (matches feed:P4). Cl2 is 1.5 x 70.906/153.33 = 0.6937 kg/kg; with the yield, the 99.19 wt% purity and the 0.05 % excess this gives 0.7036 (matches). O2 is about 0.105 kg/kg with 5 % excess, less the O2 carried in the chlorine (matches 0.1046). Phosphorus atoms close in the script.
- **Reaction heats:** -1281.3 kJ/mol P4 (4 x -319.7 - 4 x 0.62) and -277.4 kJ/mol PCl3 (-597.1 + 319.7) are correct for the liquid chlorides. 277.4 kJ/mol lies inside the 255-320 kJ/mol implied by US4183905's 800-1000 BTU/lb. The 2.7 % gap to core's ideal-gas -271.5 kJ/mol equals the difference of the two heats of vaporisation (38.6 - 32.7 kJ/mol), as D-005 says. Total exothermic chemistry is about 1.08 kWh/kg POCl3, consistent with the 1.17 kWh/kg to cooling water.
- **Utilities plausible for the technology:** electricity 12.9 Wh/kg (loop pump 382 t/h x 300 kPa / 0.55 is about 36 kW; checked). Product cooler 70.75 kW with cp 0.9 kJ/(kg K), which is close to the real POCl3 liquid cp of about 0.9. Chilled-water approach at the vent condensers is OK (283 K outlet against 278 K supply). Steam: see #1.
- **Source spot check:** US4183905 was re-read by the reviewer. The 800-1000 BTU/lb, the 0-20 % (preferably 1-10 %) excess O2, the zone temperatures, the 8.56-7.15 feed ratio and the about 50 % PCl3 vapour explosion statement are as summarised in SRC-1. The facts are restated in the case's own words; no tables, figures or passages are copied. Ullmann's is listed as not read (licensed) and not used.
- **ASSUMED marking:** every stream value is `assumed` with a source (script and decision id) or `calculated` by propagate. The design-basis assumptions are marked ASSUMED, and the `assumptions-marked` gate is ok.
- **LCI:** the functional unit is 1 kg POCl3 at S14. Every foreground exchange is traceable to a stream or energy stream. Inventory mass in 1.022096 kg and out 1.022094 kg per kg, consistent with the flowsheet. No zero-filled and no licensed background values: every background is `missing:` with a description of the activity to connect to, and these appear in `lca/gaps.csv`. `lca/mappings.yaml` is in the folder and empty on purpose (D-012). Exclusions are listed with reasons.
- **process.yaml:** `publication.status: internal`, `validation.status: unreviewed`, `maturity: concept` with an explicit note that `cheme maturity` reaches no level. `concept` is the lowest value the schema allows, so the claim is as honest as the manifest permits. Key values carry decision ids and references.

## Not checked

- CN115259114B and US5183649 locators were not re-read; only US4183905 was spot-checked.
- The chlor-alkali-1 S42 and asu-1 S7/S8 compositions were not compared against those folders.
- Equipment list entries were not reviewed item by item against the PFD (beyond the passing `process-links` gate).
- No VLE check of the columns or vent condensers was possible: there is no qualified property package (core #315/#364), as D-006 states. Column stage counts, sizes, R-201 kinetics and mass transfer do not exist and so were not reviewed.
- Safety (D-011) was read only as a carried-forward list; no hazard study is in scope.

Merge pending: the branch is not merged. No critical or high finding is open.
