---
topic: design
reviewed_commit: 1e9890d5964c7f483a9c961e3049e165d123b5f8
scope: [DESIGN.md, process/, lca/, process.yaml, equipment/equipment-list.yaml, piping/line-list.yaml, scripts/balance.py, runs/20261028-150723-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/ethanol-1
merge: pending
---
# Review: design (concept BFD/PFD and preliminary LCI of ethanol-1, issue #129)

An independent review of the concept-stage case study "ethanol by direct hydration of ethylene"
(branch `case/ethanol-1`, 5 commits be0c48d..1e9890d over `origin/main`). The design agent wrote
it in an earlier session. The reviewer did not write any of it and changed no design file. Every
command result below is from the reviewer's own run at 1e9890d, not taken from the run report.

Finding ids follow `reviews/README.md`. The short id R-nn the task asked for is given in
brackets at the start of each finding.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/flowsheet.yaml:192, 241, 261, 272 | V101, V102, C201, C202 | (R-01) `cheme maturity` lists the model basis as "V101 equilibrium-stage, predictive, sourced; V102 equilibrium-stage, predictive, sourced; C201 shortcut, predictive, sourced; C202 shortcut, predictive, sourced". Those steps declare no model at all: their outlets are ASSUMED component splits from scripts/balance.py (DESIGN.md D-005, and provenance `assumed` on S8-S10, S16, S18, S19, S21-S24). The credit is a default that cheme infers from the step class (SeparatingByFlash, Distilling); nothing was predicted or sourced. The run report repeats it ("two separators (the scrubber and the molecular sieve) have no basis source"). Once the feed provenance and C101/V301 are fixed, `balanced` would therefore be credited while four of the six separators are still assumed splits. Today the `balanced` level fails anyway, so no published number is wrong, but the model-basis report misleads anyone who reads it. | medium | open | Declare V101, V102, C201 and C202 to cheme as specified (component-split, provenance assumed) wherever the flowsheet/simulation schema allows it. If it does not, record in DESIGN.md D-012 and in process.yaml `validation.notes` that this part of the maturity report does not hold for these four steps, and report the class-based default to core. Correct the run-report statement in the next run record (existing run records are never edited). |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml:8, 14; lca/mappings.yaml:6-8; DESIGN.md:195 | LCI backgrounds | (R-02) The folder says two different things about its gaps. lca.yaml (header, goal), the mappings.yaml comment, D-013 ("everything else stays a gap") and PROGRESS.md say every background is unmapped, and `cheme assess lca --coverage` reports 16 gaps. But the library build (`uv run scripts/build_lci.py --library . --out /tmp/...`, rerun by the reviewer) links six of them: feed:WATER, feed:POWER, product:CW and product:WW through the registry slugs in process.yaml and the shared lci/mappings.yaml, and feed:HPS and feed:LPS through this folder's own `steam-heat` override. It reports 10 gaps (ethylene, FUELGAS, the 4 consumables and their 4 disposals). An Atlas reader therefore gets a dataset with power, water, steam, cooling-water and wastewater backgrounds linked to generic library entries (location GLO, no site chosen), while the folder's text says none are linked. Only the run report ("Defaults to check") mentions it. No zero-filled or licensed values were found: the build exports the remaining exchanges unlinked. | medium | open | Choose one position and state it everywhere. Either accept the shared default links (water, power, CW, WW, steam-heat) and update the lca.yaml header/goal, the mappings.yaml comment and D-013 to list which exchanges the Atlas build links and with which shared entry, or keep them gaps by setting `atlas: false` (or the schema's equivalent) for those exchanges in lca/mappings.yaml. Quote the resulting gap count (10 or 16) consistently. |
| 2026-10-28-pfd-lci-review#3 | DESIGN.md:104, 107; process/flowsheet.yaml (Q9, S22, S27) | C-202, V-301 | (R-03) The largest utility in the inventory rests on two judgements, not on calculation: the C-202 reboiler (16.6 MW, 74 % of the steam, 4.8 MJ/kg product) and its reflux ratio of 3 ("a judgement, not calculated", D-005), and the 18 % sieve regeneration return that adds to C-202's load. The arithmetic is consistent: reboiler ≈ condensing a reflux of 3 × 16.4 t/h (12.4 MW condenser) plus the vapour distillate. For a feed of ~27 wt% ethanol that is already hot (403 K), R = 3 may overstate the steam by tens of percent. This is acknowledged as the first number to check (D-006), so it misleads nobody, but the steam figure per kg in D-013 is unverified. | medium | open | Check C-202 before linking the steam background: a Fenske-Underwood-Gilliland shortcut (`cheme datasheets fill`) or the NRTL ethanol-water simulation of C-202 alone that D-012 already proposes. Source or bound the regeneration return (sieve supplier or open literature). Record R/Rmin in D-005. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:96 | C-101 | (R-04) The C-101 scrubber is specified to recover 99 % of the ethanol in the separator gas with 3600 kg/h of wash water (L/G ≈ 0.034 mol/mol, about 200 kmol/h of water against about 5800 kmol/h of gas). No absorption factor was checked. Ethanol's K-value over water at 313 K is roughly 0.01-0.02 at 6.8 MPa, and the dense supercritical ethylene can raise it several-fold. With an absorption factor below 1, 99 % recovery is not achievable at any stage count. The ethanol that is not recovered is recycled to R-101 rather than lost, so the product yield and the LCI barely change, but the reactor feed ethanol (equilibrium-limited hydration) does. | low | open | Check the wash-water rate against an absorption factor (A = L/(K·G) > 1 with margin) using a K-value for ethanol in dense ethylene, or bound it with SRC-1's crude strength. Adjust the wash rate or the recovery in D-005. |
| 2026-10-28-pfd-lci-review#5 | process/flowsheet.yaml:231, 512 | K-102, S34 | (R-05) K-102 compresses the V-102 flash gas (39 mol% butenes, 4 % diethyl ether, 5 % ethanol, 3 % water) to 7300 kPa(a) with intercooling to 313 K. At those conditions much of the butene, ether, ethanol and water condenses in the inter/aftercoolers (butene partial pressure ≈ 2.8 MPa against a vapour pressure of about 0.45 MPa at 313 K). S34 is nevertheless treated as a single gas returning to M101. The phase is not checked, and no interstage knock-out or condensate route is shown. | low | open | State in D-005 where the K-102 interstage condensate goes (back to V-102 or to C-201) and how it changes the butene and ether loop. Add knock-out drums to the equipment list at basic engineering. |
| 2026-10-28-pfd-lci-review#6 | process/flowsheet.yaml:567 | S22, V-301 | (R-06) The vapour-phase molecular sieve is fed with C-202's saturated top vapour (368 K, 200 kPa(a)) and has no superheater. Vapour-phase 3A sieves normally get a superheated feed so it does not condense in the bed. The small LP-steam duty of that superheater is missing from the balance and the inventory. | low | open | Add a sieve feed superheater (LP steam) as a step or a stated ASSUMED duty in D-005/D-006, or record why none is needed. |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md:60 | D-003, SRC-3, SRC-8 | (R-07) D-003 cites SRC-3 (US 4329520: 250-290 C, 900-1100 psig) as corroboration without a caveat, although the source register says only a search-result summary was seen ("to verify"). The EN 15376 water limit (SRC-8), on which the product specification rests, is likewise stated "from general knowledge, not re-read". | low | open | Read SRC-3 and add a locator, or drop it from D-003. Verify the EN 15376 clause and edition and record it in the register. |
| 2026-10-28-pfd-lci-review#8 | process.yaml:51, 54-55 | chemistry slugs | (R-08) process.yaml maps product:FUELGAS to the registry chemical `flare-gas`, but the LCI and D-013 treat that stream as a fuel burned with energy recovery in the site fuel-gas header, not flared. feed:HPS and feed:LPS are given the slug `steam` (counted by mass), while the inventory counts them in kWh; only the lca/mappings.yaml override keeps the build consistent. | low | open | Leave FUELGAS without a chemical slug (a registry gap to request: fuel gas) rather than the nearest wrong entry, or say in its note that the slug is a placeholder and the exchange is not linked. Align the steam slug notes with the steam-heat override. |
| 2026-10-28-pfd-lci-review#9 | process.yaml:34-45 | maturity, validation.notes | (R-09) The `concept` claim is the lowest value the schema allows, and the comment says why. However, `cheme maturity` gives calculation maturity **none** (`sourced.boundary` fails: feed flows and compositions are not given with a source; `balanced.model-basis` fails for R101, C101 and V301), and the claim raises `cheme.maturity-claim-exceeds` (warning). `validation.notes` describes the balances but does not say this, so an Atlas reader sees "concept" without learning that the evidence supports no level yet. | low | open | Add one sentence to `validation.notes`: calculation maturity none at 1e9890d, which requirements fail, and that concept is the floor of the manifest. |
| 2026-10-28-pfd-lci-review#10 | lca/dataset.yaml:85 (generated from lca/lca.yaml) | data quality | (R-10) The default pedigree scores temporal representativeness at 1.00 (very good) because the dataset year is 2026. The reactor data, however, come from patents of 1977 (US 4003952) and 1994 (US 5349096), and no plant data are used. The DQR of 2.33 therefore looks better than the evidence. | low | open | Give the reaction-derived exchanges a pedigree, or a data year that reflects the sources, in lca.yaml (if the schema allows it); otherwise note the limitation in D-013 and report the default to core. |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: this is the first review record of ethanol-1 (`reviews/` held only README.md at 1e9890d).

## Drawing
There are no P&ID sheets (`pid/` is empty; P&IDs are out of scope at concept stage). The BFD and
PFD (`process/BFD.xml`, `process/PFD.xml`) are generated by `cheme process build` from the
YAML. `cheme validate` printed no `drawing <sheet>:` count line for them and reports 0 errors and
0 warnings over 18 files. The generated sheets were not rendered or read tile by tile (see
"Not checked").

## Checked and fine
- **Scope and route**: vapour-phase direct hydration of ethylene over H3PO4 on silica, with gas
  recycle, water scrub, light-ends and concentrating columns and 3A molecular-sieve dehydration
  to anhydrous ethanol. The boundary is gate-to-gate: pipeline ethylene at 7.3 MPa, site
  utilities, off-gas to fuel gas, blowdown to wastewater treatment. This matches the
  petrochemical route the issue's handoff proposes. Fermentation (the dominant route by volume)
  is explicitly not designed and is flagged in D-001, design-basis.yaml and process.yaml.
  `git diff --name-only origin/main..HEAD` touches only `processes/ethanol-1/`.
- **Reviewer's own runs at 1e9890d**:
  - `cheme validate`: 0 errors, 0 warnings (3 infos: the D-023 example in a checks.yaml comment, and the loader's port-cycle notes).
  - `cheme check`: every concept gate passes except `layout-plot-plan`; layout is out of scope, as the report says. The basic/detail gates fail as expected (no P&ID, review, layout or datasheets).
  - `cheme process propagate --check`: silent (nothing stale).
  - `cheme process streams`: every block (REA, PUR, DEH) and every step closes. Overall: 8076.49 kg/h ethylene + 8473.02 kg/h water in = 12 502.1 kg/h product + 645.9 kg/h off-gas + 3401.5 kg/h wastewater out.
  - The reactor extents in the step table and in the block table agree: HYD 273.5, ETHER 2.82, OLIGO 1.41 kmol/h.
- **Reactor and yield plausibility**:
  - Per pass, 5 % of 5640 kmol/h inlet ethylene (282 kmol/h) is converted. The fresh feed is 288 kmol/h, so the recycle is about 20 times the fresh feed.
  - Reactor-level ethylene-to-ethanol yield is 95 %; to product 94 % (0.646 kg ethylene per kg product, against a stoichiometric 0.607). That is plausible for a commercial phosphoric-acid process.
  - ΔH(HYD) = -45.3 kJ/mol (ideal gas) agrees with the known gas-phase value.
  - The adiabatic rise of 28 K (513 → 541 K) is of the order of US 5349096's 240 → 260 C test runs.
  - The loop at about 7 MPa, 513 K and water/ethylene 0.35 lies inside the cited windows.
  - The crude is 13.5 mol% ethanol, close to SRC-1's 10-12 mol%.
- **Duties, order-of-magnitude checks**:
  - E-101 (41 MW): latent heat of about 35 t/h of water plus the gas sensible heat. S4 leaves 2 K below its water dew point (about 478.6 K at 1.75 MPa water partial pressure), so E-102 finishes the evaporation, consistent with D-008.
  - K-101 (0.40 MW): ideal-gas compression at ratio 1.07 and η 0.75 (conservative, since Z ≈ 0.6 is ignored).
  - E-103 (8.8 MW) and V-301 condenser (5.0 MW): consistent with the condensing loads.
  - Overall energy, roughly: steam + power 23.2 MW plus about 3.4 MW of reaction heat, against 27.6 MW to cooling water plus stream sensible heat. It closes to within about 5 %, acceptable for a concept estimate that D-006 labels unqualified.
- **Design conditions**: 80 barg = 72.5 barg operating + 10 % (D-009). The line-list DNs follow the stated velocity rule (not recomputed for every line).
- **Provenance**:
  - Every key value is either sourced with a locator (SRC-1/SRC-2 sections) or marked ASSUMED: capacity, ethylene grade and pressure, selectivities, every split, purge, blowdown, reflux, consumable rates.
  - Stream values carry provenance: given, assumed or calculated with a fingerprint.
  - The R101 selectivity block is honestly `provenance: assumed`, even though its conversion comes from SRC-1.
- **Licences**: patents and the NIST WebBook are summarised as facts in our own words with locators. No tables, figures or passages are copied, and no ecoinvent or other licensed values appear (factors.yaml is the packaged open DESNZ profile, unused).
- **LCI**:
  - Per 1 kg of product S23, attributional, cut-off, no allocation (single product). Off-gas and blowdown are treated as wastes whose treatment is outside the boundary.
  - The inventory equals the flowsheet: in 16 549.5 kg/h = out 16 549.5 kg/h. `--coverage` shows mass closed and C/H/O closed (D-013).
  - Every unmapped exchange is a gap with a description of the activity it should connect to. None is zero-filled.
  - Emission exclusions and cut-offs are each stated with a reason. The consumable rates are ASSUMED orders of magnitude, with a GSD and a source text.
  - The per-process override (steam-heat) is in the folder's lca/mappings.yaml.
  - Classification: "partial screening carbon footprint", publishable, not published (`publication.status: internal`).
- **Honesty**: process.yaml `validation.status: unreviewed`, `access: private`. The run report states its open items and core bugs (D-011, D-012).

## Not checked
- The BFD/PFD drawings were not rendered or read; they are generated and validate clean.
- The library build with `--strict`/`--public` was not run. The build was run without them, so the strict warnings about the cut-off criteria (chemeascode `lca.cutoff` not installed) were not followed up.
- scripts/balance.py was not rerun or audited line by line. The reviewer checked its outputs for order-of-magnitude consistency only (above).
- No property-based check of any separator split (no package covers ethylene/water/ethanol at 7 MPa). Phase behaviour (findings #4, #5) was judged from vapour pressures only.
- SRC-1/SRC-2 were not re-opened by the reviewer. Their quoted facts were checked for plausibility, not against the text.
- Line-list DNs were not recomputed line by line.
- Product quality beyond water (methanol, higher alcohols, acetaldehyde, the 170 ppm ether) is outside the concept scope and is noted as open in D-002.
- No HAZOP, layout, P&ID or datasheet exists; these are out of scope at concept stage.
