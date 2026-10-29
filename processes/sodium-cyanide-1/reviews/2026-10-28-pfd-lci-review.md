---
topic: design
reviewed_commit: 0000a06f60b70f4aca87b97208ff4d2d75cbb468
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/catalysts.yaml, lca/lca.yaml, lca/mappings.yaml, scripts/nacn_balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/sodium-cyanide-1
merge: pending
---

# Independent design and LCI review: sodium-cyanide-1 (concept BFD/PFD, preliminary LCI)

Issue ChemE-as-Code/process-library#150. Branch `case/sodium-cyanide-1` at `0000a06`, 6 commits
on top of `cc5624f` (main). I did not write this design. No design file was changed by this
review.

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only $(git merge-base origin/main HEAD)..HEAD` | only `processes/sodium-cyanide-1/` changed (the two-dot diff against today's `origin/main` also shows `thf-1`, but that is main moving on after the branch point, not a change of this branch) |
| `cheme validate` | 18 files, 0 errors, 1 warning (`cheme.process-catalyst` R101/S5: the 349 K feed is outside the gauze window; see R-06) |
| `cheme check` | concept gates pass except `layout-plot-plan` (no layout, out of scope for this run); basic gates fail on P&IDs, design review, layout, datasheets as expected at concept |
| `cheme maturity` | calculation maturity none; `cheme.maturity-claim-exceeds` warning on `maturity: concept` |
| `cheme process streams` | every block and step balances in mass; reaction extents consistent between the RXN block and step R101 |
| `cheme process propagate --check` | clean, no stale calculated value |
| `cheme assess lca --coverage` | partial screening carbon footprint, 12 gaps (8 unmapped backgrounds, 4 zero-flow trace emissions uncharacterised by GWP100); mass closes, element balance not assessable (gauze), energy closure 75.6 % |

## Checks against the issue and the sources

- **Route and boundary** match the issue: Andrussow HCN (CH4, NH3, air over Pt/Rh), caustic
  neutralisation, ammonia (ammonia-1) and caustic (chlor-alkali-1) as boundary feeds, emissions
  explicit through a tail gas boiler. Rejected routes (BMA, Shawinigan, AN by-product, direct
  caustic absorption) are stated with reasons (D-001).
- **Sourced converter basis verified against the source**: US 6,596,251 B2 Table 2 run 1 gives
  O2/NH3 1.15, CH4/NH3 0.98, HCN yield 62.9 % on NH3, gauze 994 C, 7.6 vol% HCN, and a specific
  output of about 303 kg HCN/(h m2); the background gives 2-3 wt% HCN in the absorber sump.
  DESIGN.md D-004/D-007 and the gauze area estimate in lca.yaml reproduce these correctly.
- **Balances recomputed by hand** from the stream table: converter NH3 199.0 kmol/h (fresh
  160.5 + recycle 38.5), HCN 125.17 kmol/h = 62.9 % of NH3 fed; NH3/HCN at the outlet 0.311;
  recycle = 99 % of outlet NH3. HCN: 125.17 made, 0.125 to the tail gas (0.1 %), 0.063 to the
  purge (0.05 %), 124.98 to R-401 = NaCN in the product (0.98 x 6250 kg/h / 49.0). NaOH excess
  1.57 kmol/h = 1.0 wt% of the product. Water out of R-401 = crystalliser + dryer vapour +
  product water. Cake: 10 wt% liquor at 0.80 kg NaCN/kg water. Carbon: 0.3748 kg C/kg in the
  methane = 0.2402 in NaCN + 0.1346 as 0.493 kg CO2 at the stack. All close.
- **Plausibility per kg product**: NH3 0.437 kg (78 % overall yield, 0.347 stoichiometric for
  pure NaCN), methane 0.50 kg (HCN yield on CH4 about 64 %), NaOH 0.81 kg (100 % basis),
  converter gas 7.5 % HCN / 22.5 % H2O / 11 % H2: all in the usual range of air-operated
  Andrussow plants. K-101 0.63 MW reproduces with an isentropic efficiency of 0.75 to 180 kPa(a).
  Crystalliser 4.54 MW = 7.0 t/h water x latent heat; E-202 3.12 MW = 134 t/h x 4.18 x 20 K;
  neutralisation 0.43 MW at about 12 kJ/mol. The steam figures are high: see R-01.
- **Sources and licences**: facts only, restated in own words with locators (patent, table/run,
  example); Ullmann's named but not used for any value. No copied table, figure or passage found.
  Values without a source are marked ASSUMED in the design basis, the flowsheet provenance and
  DESIGN.md.
- **LCI**: per 1 kg product (FU), every foreground exchange equals the flowsheet stream divided by
  6250 kg/h; mass in = mass out (10.747 kg); every background `missing:` with the activity to link
  to; no zero-filled or licensed values; overrides in the folder's `lca/mappings.yaml`; the
  allocation deviation (shares 1/0 instead of exergy) is stated with its reason.
- **process.yaml** is honest: `maturity: concept` is the lowest value of the schema enum and the
  comment and `validation.notes` say calculation maturity none and `status: unreviewed`.

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/flowsheet.yaml:405, :633-634; DESIGN.md:80-87, :150-166 | R-101, E-101, B-301, Q8/Q9, product:MPSX | The steam balance is an upper bound shown as a design value. At exactly the feed ratios and yield of SRC-1 run 1 the source's gauze ran at 994 C (1267 K); the adiabatic model gives 1429 K, 162 K hotter, because heat losses are not modelled (D-004 says this). E-101 then recovers all sensible heat 1429 -> 523 K with no loss (15.2 MW), and B-301 turns 89 % of the tail gas LHV into steam with no radiation or blowdown loss (15.4 MW). Rough scaling of the E-101 duty to a 1267 K outlet gives about 2.5-3 MW less steam, so the export of 17.8 MW (2.85 kWh/kg) is probably 15-20 % too high. The NaCN burden is not affected now (shares 1/0), but the steam co-product flow is, and so is any later exergy or energy allocation, which DESIGN.md names as the intended method. | medium | open | Either fix the converter outlet at the sourced gauze temperature with the loss as an R-101 heat duty, or keep 1429 K and state in D-010, lca.yaml (product:MPSX) and process.yaml that the steam export is an upper bound with no converter, WHB or boiler losses; add an ASSUMED boiler efficiency to B-301. |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml:44-116; DESIGN.md:201-207 | LCI inputs | Inputs that exist but have no exchange in the LCI, so `cheme assess lca` cannot list them as gaps: (a) boiler feed water and its treatment for about 30 MW of steam raised. The exported steam (about 27 t/h) leaves only as an energy stream (kWh), so its water never enters the inventory and the mass closure leaves it out; (b) phosphate make-up of the C-101 ammonia recovery loop; (c) the acid stabiliser of the HCN refining (SO2, H3PO4 or H2SO4). DESIGN.md lists (b) and (c) as open inputs, but the LCI shows neither as missing nor as a cut-off flow. The task requires every unmapped background to be listed as a gap with a description. | medium | open | Add each one to lca/lca.yaml as an exchange with `missing:` and a description (amount ASSUMED or estimated), or as a cut-off/exclusion entry with the reason, so that each shows in gaps.csv. Name the convention for steam (energy stream, BFW outside or inside) in D-012. |
| 2026-10-28-pfd-lci-review#3 | process/flowsheet.yaml:537; DESIGN.md:135-141 | R-401, S21, CR-401 | The neutraliser product holds 45.3 wt% NaCN, about 0.84 kg NaCN per kg water at 343 K. The design's own mother-liquor solubility at the same temperature is 0.80 kg/kg (D-008, from SRC-2). The R-401 product and its transfer line to CR-401 would therefore be supersaturated and could deposit solids. The common-ion effect of the free NaOH, which collects in the liquor, may explain the lower liquor value, but the design does not say so. | low | open | Say why the R-401 product stays in solution (temperature, NaOH effect), or run R-401 hotter or with more dilute caustic. The NaCN solubility is already an open input. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:159-163; process.yaml:63-65 | power, chilled water | "Power 1.03 MW" leaves out the refrigeration power of the 4.8 MW chilled-water duty. At a typical COP of 4-6 that is about 0.8-1.2 MW, the same size as the plant's whole stated power demand. It is correctly a gap (product:CHW `missing:`), but a reader of D-010 or of the process.yaml utilities would take 0.164 kWh/kg as the plant's electricity demand. | low | open | State in D-010 and in the chilled-water note that the chiller power is outside the 1.03 MW and is carried by the CHW background. |
| 2026-10-28-pfd-lci-review#5 | lca/lca.yaml:117-138 | consumable:pt-rh-gauze | The exchange counts the whole 50 kg gauze charge as consumed twice a year (2e-6 kg/kg) and also sends it to refining. The metal is refined and returned, and what drives the burden is the irrecoverable Pt/Rh loss per kg HCN. Mapped as it stands, this exchange would charge the full primary production of the charge every campaign. | low | open | When it is mapped, model the net metal loss (or the charge with the refined metal returned) and give the gauze a composition, which also makes the element balance assessable. Keep it as a gap until then. |
| 2026-10-28-pfd-lci-review#6 | process/flowsheet.yaml:189; checks/checks.yaml | R101/S5 | D-004 calls the `cheme.process-catalyst` warning (349 K feed outside the 1223-1473 K gauze window) "accepted", but no acceptance is recorded, so it remains a live warning in `cheme validate`. The reasoning is sound: the window applies to the gauze, not to the feed gas. | low | open | Record the acceptance by its finding id with the reason and D-004 in checks/checks.yaml `accept:`, or reword D-004 to "known warning". |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md:183-197 | LCI energy closure | `cheme assess lca` reports an energy closure of 75.6 %. D-012 reports the mass, carbon and nitrogen closure but not this figure, nor which energy terms the tool leaves out (no losses are modelled, separation enthalpies are not evaluable in core). | low | open | State the energy closure in D-012 with a one-line explanation of the missing quarter. |

No critical or high findings. The balances close, the sourced converter basis matches its
source, the LCI is per functional unit and consistent with the flowsheet with every background
an explicit gap, and nothing outside the folder changed.

## Previous findings

None: this is the first review record of sodium-cyanide-1 (`reviews/` at 0000a06 holds only
README.md), so no earlier finding is carried forward.

## Not reviewed

P&IDs, layout, datasheets, HAZOP: none exist at concept stage. The generated BFD/PFD XML were not
rendered; `cheme check` reports the BFD as current and `cheme validate` shows no error on either.
The library-level tests (`pytest`) were not run by this review.
