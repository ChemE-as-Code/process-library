---
topic: design
reviewed_commit: 581976e6fae81587d50bc8bada0ddf002aa6eb61
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, lca/, scripts/balance.py, equipment/equipment-list.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/formic-acid-1
merge: pending
---

# Independent review: formic-acid-1 concept PFD and preliminary LCI (issue #185)

Reviewer: an independent agent session that did not write the design. Stage reviewed: concept
(design basis, balanced BFD/PFD, preliminary gate-to-gate LCI). P&IDs, layout, HAZOP, TEA and
datasheets are outside the issue's scope and were not reviewed. No design file was changed.

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only $(git merge-base origin/main HEAD)..HEAD` | 191 files, all under `processes/formic-acid-1/`; nothing outside the folder changed (the plain `origin/main..HEAD` diff also lists other processes only because main moved on since the branch point) |
| `cheme validate` | 17 files, 0 errors, 0 warnings; infos only (dexpi.load cycles, D-023 cited in a template comment of `checks/checks.yaml`) |
| `cheme check` | every concept gate ok except `layout-plot-plan` (out of scope); basic/detail gates fail on P&IDs, layout, datasheets and the design review (expected at this stage) |
| `cheme maturity` | calculation maturity none; `cheme.maturity-claim-exceeds` warning for `maturity: concept` (sourced-boundary: feeds assumed; model basis: R101/R201/X101 conversions partly assumed) |
| `cheme process streams` | every block (CARB, HYD, DEHY, VENT) and all 17 steps balance; largest residual 0.01 kg/h (CARB, V101) |
| `cheme process propagate --check` | no output: nothing stale, nothing to fill |
| `cheme assess lca --coverage` | partial screening carbon footprint; mass, element and carbon-origin balances closed; 11 gaps (8 unmapped backgrounds, each with a description; 3 uncharacterised emissions); publishable |

## Hand checks of the balance (reviewer's own arithmetic from the stream table)

- Product S28: 6250 kg/h at 85 wt% = 5312.5 kg/h HCOOH = 115.4 kmol/h; hydrolysis extent 115.43 kmol/h. Consistent.
- CO: S1 3552.9 kg/h, 125.6 kmol/h CO; carbonylation extent 115.5 kmol/h = 92.0 % CO yield (SRC-1 Example 1); vent CO 10.0 kmol/h. Consistent.
- Water: 115.4 kmol/h reacted (2079 kg/h) + 937.5 kg/h in the product = 3017 kg/h = S17. Consistent; LCI 0.483 kg/kg.
- CO2: 10.01 + 2 x 0.10 + 0.06 = 10.28 kmol/h = 452 kg/h = 72.4 g/kg. Consistent with the LCI.
- Hydrolyser: S18 water/MF = 0.5525/0.3684 = 1.50; 399 kmol/h MF (24.0 t/h), 28.9 % converted; outlet Q = 0.179 against Kx 0.20 (ln Q/K = -0.11, as stated); recycled ester 17.0 t/h MF = 3.2 t/t HCOOH, inside SRC-3's 3-4 t/t.
- Formic acid loop: S25 48.9 wt% (8344 kg/h HCOOH); C-301 77 wt% bottoms and 0.5 wt% water distillate; C-302 lever rule 85/77/66 gives 6250 / 4545 kg/h. Consistent.
- Catalyst: make-up 0.0805 kmol/h NaOMe = destroyed 0.0222 + purged 0.0584. Consistent.
- Machines: K-101 three intercooled stages, ratio 2.84 each, ideal gas, 0.75 / 0.95 gives about 450-470 kW; P-101 hydraulic 19.5 kW gives 34 kW at 0.60 / 0.95. Consistent.
- Pressure-swing scheme: 49 wt% feed lies on the water side of both azeotropes (about 80 wt% at 2.03 bar(a), about 60-64 wt% at 0.07-0.13 bar(a), SRC-2/SRC-3); C-301 water overhead to 77 wt% bottoms, C-302 acid-side feed giving acid-rich distillate and near-azeotropic bottoms. Directionally correct and as described in SRC-2/SRC-3.
- Utilities: 22.7 MW LP steam = 3.64 kWh/kg (13.1 MJ/kg, about 6 t steam/t at 450 kPa(a)), stated as 1.5 x the prior-art figure quoted in SRC-2 and attributed to no heat integration. Plausible for an unintegrated concept; see R-01 for the C-301 reflux.

## Scope, sources, licences

- Route and boundary match issue #185 (methanol carbonylation + methyl formate hydrolysis, concentration to a commercial grade, gate-to-gate LCI). The choice of pressure-swing distillation over amide extraction is reasoned (D-004).
- Every key value is either given with a source (carbonylation conversion, Kx) or marked ASSUMED with its derivation (capacity, splits, reflux, purge, heats of reaction, oxidiser). The source register gives locators (patent sections, examples) and states what was and was not read; Ullmann (licensed) is listed as not read and not used.
- No third-party tables, figures or passages found: patent facts are restated as numbers in our own words. The SRC-3 azeotrope compositions are individual facts with the source, not a reproduced table.
- LCI: per functional unit (1 kg 85 wt% acid, S28); inputs 1.3009 kg = outputs 1.3009 kg; no zero-filled backgrounds (all `missing:` with a description of the activity to connect); no licensed values; `lca/mappings.yaml` empty with the reason (D-013). Emission exclusions are reasoned.
- process.yaml: `maturity: concept` (the lowest value of the enum), `validation: unreviewed`, notes state assumed basis and gated energy closure (but see R-04).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 (R-01) | DESIGN.md D-011; scripts/balance.py | C-301 reflux, Q15 | The shortcut duty of C-301 (7.8 MW, 34 % of the LP steam and so of the LCI's 3.64 kWh/kg) uses an ASSUMED reflux ratio of 1.0 with no check against the minimum reflux. Water / formic acid has a low relative volatility, falling towards 1 as the bottoms approach the azeotrope (77 wt% bottoms against the about 80 wt% azeotrope at 2.03 bar(a)), so R = 1.0 may be below R_min. The 1.5x-prior-art cross-check of D-011 is read as "conservative", but the C-301 term could also be underestimated: the total steam figure is uncertain in both directions, not a conservative bound. | medium | open | Estimate R_min for C-301 (Underwood with a relative volatility from the SRC-3 azeotrope data or the Thermo vapour pressures, or a stated literature range) and set R >= 1.2 R_min, or record in D-011 and the LCI source that the C-301 duty is not bounded and why. |
| 2026-10-28-pfd-lci-review#2 (R-02) | scripts/balance.py:212-213; DESIGN.md D-011; flowsheet S18/S19 | E-201, Q9 | Inconsistent preheat basis: D-011 and streams S18/S19 give 340 -> 393 K, balance.py computes Q9 from 330 -> 393 K (63 K). At 340 K and cp 3.0 the duty is 1.70 MW, not 2.02 MW (0.32 MW, 1.4 % of the steam). | low | open | Align the script with the stream temperature (or the stream with the script), rerun, update Q9, the LPS total and the LCI. |
| 2026-10-28-pfd-lci-review#3 (R-03) | DESIGN.md D-007; flowsheet S9/S10 | V-101, C-101 | Dissolved CO in the V-101 liquid at 4450 kPa(a) is neglected. With a CO solubility in methanol of the order of 3e-4 mol fraction per atm near ambient (general knowledge, reviewer's estimate), about 5 kmol/h CO, half the vent CO, would leave with S10 and be released at the C-101 condenser. The total CO not converted (and so the LCI CO2) is unchanged if that vent also goes to X-101, but the split between S9 and the C-101 vent, the oxidiser feed and the column-vents exclusion are not representative. | low | open | Quantify the dissolved CO in D-007 (sourced Henry constant or ASSUMED order of magnitude), and either add a C-101 vent stream to X-101 or state the size of the excluded column vent. |
| 2026-10-28-pfd-lci-review#4 (R-04) | process.yaml:38-60 | maturity, validation notes | `cheme maturity` reports calculation maturity none and warns `cheme.maturity-claim-exceeds` for `concept`. `concept` is the lowest value the schema allows and DESIGN.md D-014 says so, but process.yaml, the file a library reader sees, does not mention it. | low | open | Add one sentence to `validation.notes`: cheme maturity reaches no calculation level (feeds and two conversions assumed), so `concept` is claimed as the lowest level, not as evidence-backed. |
| 2026-10-28-pfd-lci-review#5 (R-05) | DESIGN.md source register SRC-4; process/reactions.yaml HYD sources | SRC-4 | SRC-4 is quoted as "ester/water 1.5-10 mol/mol" (register) and "MF/water 1.5-10 mol/mol" (reactions.yaml), while the design runs water/MF 1.5. Either the search snippet's direction was copied the wrong way round or SRC-4's range does not cover the design. The full text was not read, and SRC-4 also carries the 95 % approach to equilibrium that sets the hydrolysis conversion. | low | open | Read the US4299981 full text, correct the ratio's direction and give a locator for the 95 % approach; until then mark the 95 % approach ASSUMED, with SRC-4 as an unverified lead. |
| 2026-10-28-pfd-lci-review#6 (R-06) | DESIGN.md D-012 | CO per kg | "CO 0.568 kg (theoretical 0.517 kg at 92 % yield on the 99 mol% gas)" reads as if 0.517 kg were the amount at 92 % yield. 0.517 kg is the stoichiometric CO at 100 % yield; 0.568 kg follows from 92 % yield and 99 mol% purity. | low | open | Reword: "stoichiometric 0.517 kg CO; 0.568 kg of 99 mol% gas at 92 % CO yield". |
| 2026-10-28-pfd-lci-review#7 (R-07) | lca/lca.yaml emission_exclusions | cut-off | All four exclusions have no amount, so the 1 % mass cut-off cannot be checked (`cheme.lca-cutoff-unchecked`). At least the column vents (R-03) and decomposition CO can be bounded with an order-of-magnitude estimate. | low | open | Give an ASSUMED kg/FU estimate (or upper bound) for each exclusion that can be bounded, with its basis. |

No critical or high findings. Mass, component, element and LCI balances close; the numbers are plausible for the technology and consistent with the cited patent facts; no third-party content or licensed values were found; nothing outside `processes/formic-acid-1/` changed.

## Previous findings
None (first review of this process).

## Merge
`merge: pending`. No open critical or high finding blocks the merge; the medium finding R-01 and
the low findings may be closed in a follow-up on the branch or carried forward to the next stage.
The merge is for a human or the reviewer, not the author.
