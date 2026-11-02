---
topic: design
reviewed_commit: 82095d2419097d2d3dc9484c45f70f53437c8ec1
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, scripts/urea_balance.py, equipment/equipment-list.yaml, lca/lca.yaml, lca/inventory.csv, lca/gaps.csv]
reviewer: review-agent
reviewer_kind: agent
branch: case/urea-1
merge: pending
---

# Independent review: urea-1 concept PFD and preliminary LCI (issue #120)

The author of `case/urea-1` (a design agent in an earlier session) did not write this review.
It covers the design basis, the balanced concept flowsheet, the balance script, the equipment
list, the preliminary gate-to-gate LCI and the Atlas manifest at 82095d2. I changed no design
file.

## What was re-run (not taken from the run report)

| command | result at 82095d2 |
|---|---|
| `git diff --name-only origin/main..HEAD` | 189 files, all under `processes/urea-1/`; nothing outside changed |
| `cheme validate` | 16 files, 0 errors, 1 warning (`pydexpi_composition_fractions` S11 sums to 0.999999: the 6-digit write of propagate, O-7); info `cheme.decision-unknown` D-023 from the template `checks/checks.yaml:76` |
| `cheme check` | concept gates: 6 ok, `layout-plot-plan` FAIL (out of this run's scope); basic/detail gates fail on missing P&IDs, layout, datasheets and this review, as expected at concept |
| `cheme maturity` | `level: none`; fails `sourced-boundary` (assumed feeds) and `balanced-model-basis` (unsourced specified separations); warning `cheme.maturity-claim-exceeds` on `process.yaml:35` |
| `cheme process streams` | all 5 blocks and 22 steps balance |
| `cheme process propagate --check` | no output: no stale or missing calculated value |
| `cheme assess lca --coverage` | partial screening carbon footprint; 7 gaps (5 declared `missing:` backgrounds, NH3 and urea dust outside GWP100); mass, element and carbon-origin balances closed; warnings `boundary-utility-unassigned` for R101 and C401 |
| `cheme run scripts/urea_balance.py` (prints only) | reproduces the flowsheet: U = 1391.6 kmol/h, HP-loop residual < 0.001 kmol/h, N/C 2.800, H2O/CO2 0.450, 565.3 kg NH3 and 731.8 kg CO2 per t, 96.1 kWh/t, 34.0 MW MP steam, 45.2 m3/t cooling water; "E102 potential 59385 kW" against an LP demand of 35235 kW |

## Checks and what they showed

- **Scope and route.** CO2 stripping with total recycle, LP recirculation, two-stage vacuum
  evaporation and prilling, with NH3 and CO2 as boundary feeds from an ammonia plant outside
  the boundary. This matches issue #120. The boundary (prilling tower outlet) and the
  exclusions (storage, product cooling, utility plants) are stated in D-001 and in the LCI.
- **Balances (hand check).** Urea formed = product urea 1372.2 + 2 × biuret 6.47 + hydrolysed
  5.99 + dust 0.3 = 1391.5 kmol/h, against 1391.6 in the flowsheet. Stoichiometric NH3 for the
  98.9/0.8 wt% grade is 564.8 kg/t; the flowsheet's 565.3 kg/t leaves 0.5 kg/t of N losses,
  which is consistent with the vent, exhaust and dust emissions. The water balance closes:
  reaction water 25.07 t/h − hydrolysis 0.11 + CO2-feed water 0.13 = condensate 18.71 + net
  to air 6.13 + product moisture 0.25 t/h. Total N is 46.5 wt%. Treated condensate is
  0.225 t/t; process condensate 0.43 t/t.
- **Plausibility for the technology.** The reactor conditions (140 bar, 180 °C, N/C 2.8), the
  CO2 conversion of 0.58 per pass, the stripped solution (58 wt% urea, 7.0 % NH3, 8.8 % CO2),
  0.8 t/t MP steam, 96 kWh/t power, 45 m3/t cooling water and the K-101, P-101 and P-102 powers
  are all in the expected range for a CO2-stripping plant, and the design flags power and
  cooling water as low against the BREF benchmarks. I checked the stripper duty roughly:
  720 kmol/h of carbamate decomposed × 120 MJ/kmol is about 24 MW, plus NH3 and water
  evaporation, against the 30.4 MW the stripper gets as the remainder of the steam total.
  That is consistent at concept accuracy.
- **Sources and ASSUMED.** Every key value is either cited (BREF chapter, table and printed
  page) or marked ASSUMED with a D-entry. No unsourced figure is presented as data. I found no
  licensor names, vendor data or licensed-database values in the design files. The BREF is
  cited fact by fact, with no tables or passages reproduced. The licensed sources (Ullmann,
  CIT) are recorded as not audited.
- **LCI.** The LCI is per 1 kg of prilled urea, and every exchange equals its flowsheet stream
  or energy stream. Material in and out agree to within 0.0002 %. Every background is
  `missing:` with a description; nothing is zero-filled, and `factors: []` uses only the
  packaged open profile. Treated condensate is cut off as recyclable, and no CO2 uptake credit
  is given (correct under the issue's rule).
- **Manifest.** `publication.status: internal` and `validation.status: unreviewed`. The notes
  are frank about the conversion model, the specified separations, the incomplete utilities and
  the unmapped backgrounds.

## Findings

Numbering R-01 … R-08 follows the order below (the id column uses the library format).

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#1 | DESIGN.md:188, scripts/urea_balance.py:259 | E-102 / R-101 energy | R-01. D-010 says that E-102's condensation heat "beyond the 35.2 MW stays in the reactor to drive the dehydration (autothermal R-101)". The script's own estimate `q_e102_pot` already subtracts the dehydration (28 MJ/kmol × U), and it still leaves 59.4 − 35.2 = 24.2 MW (0.29 kWh/kg urea, 55 % of the inventoried cooling duty) that is neither exported as LP steam nor rejected to cooling water. Part of it heats the feeds (NH3 293 → ~450 K, about 10 MW; recycle carbamate about 4 MW), but those terms are not in the script either. The explanation in D-010 does not match the calculation, and the LCI may be missing an LP steam export or cooling duty of this size (`boundary-utility-unassigned` R101). | medium | open | Correct the D-010 text. Either add the feed-preheat terms to the script and show the residual, or state the unassigned heat (about 10–24 MW) as an open energy item under O-4, with its possible LCI effect (LP steam export or cooling water). |
| 2026-10-27-pfd-lci-review#2 | lca/lca.yaml:39-47 | feed:POWER, product:CW, R101, C401 | R-02. DESIGN D-010 and `process.yaml` say that power (96 vs 110 kWh/t) and cooling water (45 vs 60 m3/t) leave out the vacuum system, condensate, scrubber and cooling pumps, HP scrubber tempered water, vacuum condensers and lube oil. The coverage also reports R101 and C401 as utilities in no exchange. `lca/` does not say any of this: the `source:` texts and `gaps.csv` list only the missing backgrounds. A reader of the LCI alone takes 0.096 kWh/kg and 0.524 kWh/kg as complete foreground values. | medium | open | State in the `source:` of feed:POWER and product:CW (or as a documented cut-off) that the quantity is a known underestimate, by how much against BREF Tables 8.6/8.4, and why. Mention the R101/C401 unassigned heat in `lca/` as well. |
| 2026-10-27-pfd-lci-review#3 | process/design-basis.yaml:23, DESIGN.md:89 | CO2 feed, passivation air, HP scrubber vent | R-03. The CO2 from an ammonia plant normally carries H2 (and some CH4). With 0.6 mol% O2 of passivation air dosed in, the HP scrubber and LP vents can form flammable H2/O2 mixtures, a known urea-plant explosion hazard. The basis lumps the inerts as N2 and calls H2 removal "a basic-engineering choice" without naming the hazard. O-1 lists H2 only as an interface value. | medium | open | Name the hazard in D-004 and add an open input (H2 content of the CO2, H2 removal or vent-gas safeguards) for basic engineering and the HAZOP. The flowsheet does not need to change now. |
| 2026-10-27-pfd-lci-review#4 | lca/lca.yaml:63 | emission-excluded:fugitive-nh3 | R-04. The exclusion compares fugitives with "the 0.77 g/kg of the vent and exhaust". The inventory has 0.27 g/kg NH3 (0.50 g/kg NH3 + urea dust, 0.59 g/kg with CO2). The 0.77 matches no inventory figure. The conclusion (fugitives are small) holds either way. | low | open | Correct the figure to 0.27 g/kg NH3, and give the cut-off an amount in kg so that the 1 % rule can be checked (`lca-cutoff-unchecked`). |
| 2026-10-27-pfd-lci-review#5 | DESIGN.md:147-151, process/flowsheet.yaml (S54) | T-501 / C-501 | R-05. The prilling exhaust is 554 kNm3/h against the 300–350 kNm3/h quoted from BREF Table 8.10 ("same order"; it is 1.6–1.8×). The emissions are concentration × air flow, so per tonne they scale with this. The scrubber is also inconsistent: half of the 8.0 MW (4 MW, about 6 t/h of water) would cool the exhaust about 20 K, but S54 is at 318 K (25 K below 343 K, about 5 MW). | low | open | State the capacity basis of the BREF figure (or compare in Nm3/t), and make the S54 temperature consistent with the assumed evaporation share (O-5). |
| 2026-10-27-pfd-lci-review#6 | lca/lca.yaml:33, lca/inventory.csv | feed:CO2 | R-06. feed:CO2 is the whole impure feed gas, 0.738 kg/kg (98.5 mol% CO2 with H2O and N2), while the text and the BREF comparison speak of 0.7318 kg CO2. A CO2 background linked later would be applied to 0.86 % more mass than the CO2. | low | open | Say "CO2 feed gas (98.5 mol%)" in the title and `missing:` text, or link the background per kg of contained CO2. |
| 2026-10-27-pfd-lci-review#7 | process/reactions.yaml:21 | UREA_SYN | R-07. The Ullmann article (doi:10.1002/14356007.a27_333.pub2) is listed under `sources` of UREA_SYN, but DESIGN.md's source register says it was not read and is used "none numerically". The citation suggests support the article was never checked for. | low | open | Remove it from `sources` until the O-3 audit, or annotate it "identity only, not read". |
| 2026-10-27-pfd-lci-review#8 | process.yaml:35 | maturity | R-08. The manifest claims `concept`; `cheme maturity` reports level none (`cheme.maturity-claim-exceeds`). `concept` is the lowest value in the schema, and DESIGN D-008 and the run report explain the situation. The manifest's own `validation.notes` does not say that the maturity check reaches no level, though. | low | open | Add one sentence to `validation.notes` saying that `cheme maturity` reaches no level (assumed feeds, unsourced specified separations), so `concept` is the schema floor, not an evidenced level. |

Not raised as findings (known and recorded by the author): the S11 composition rounding
warning and the `Pumping` step workaround (O-7, core); the template's D-023 reference in
`checks/checks.yaml:76` (info, not from this run); the missing registry entries for urea and
ammonia (O-6); the gated predictive HP loop and energy closure (D-008).

## Previous findings

None: this is the first review of `processes/urea-1/`.

## Verdict

No critical or high findings. The balance closes, the numbers are plausible for CO2 stripping,
values are sourced or marked ASSUMED, nothing third-party is copied, and the LCI matches the
flowsheet per kg of urea, with every background left as a described gap. The medium findings
(R-01 to R-03) concern the energy-basis text, how complete the LCI utilities are, and an
unnamed vent hazard. They should be fixed before the case is published but do not block the
merge. Merge: pending (by a human or the reviewer, not the author).
