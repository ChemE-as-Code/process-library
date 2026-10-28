---
topic: design
reviewed_commit: 44cc3136d7cb627208077371f5b965aa67ed48c2
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, scripts/balance.py, equipment/equipment-list.yaml, lca/]
reviewer: review-agent
reviewer_kind: agent
branch: case/phosgene-1
merge: pending
---

# Independent review: phosgene-1 concept PFD and preliminary LCI (issue #164)

Reviewer: an independent agent that did not write the design. Branch `case/phosgene-1`, five
commits on `origin/main` (2b1a09f..44cc313), 191 files, all under `processes/phosgene-1/`
(`git diff --name-only origin/main..HEAD` shows nothing outside the folder). No design file
was changed by this review.

## Commands re-run (on 44cc313)

| command | result |
|---|---|
| `cheme validate` | 17 files, 0 errors, 0 warnings; info only (`decision-unknown D-023` is the template's example comment in checks/checks.yaml, not a design reference) |
| `cheme check` | every concept gate passes except `layout-plot-plan` (layout is outside the issue scope); basic/detail gates fail as expected (no P&IDs, layout, datasheets; `design-review` closes with this record) |
| `cheme maturity` | calculation maturity none: `sourced-boundary` fails (feeds assumed), `balanced-model-basis` fails (R101, T201, X301 conversions assumed); warning `maturity-claim-exceeds` on process.yaml:35 |
| `cheme process streams` | every block and step balance ok; extents R101 176.281 kmol/h, T201 0.925 kmol/h, X301 8.814 kmol/h |
| `cheme process propagate --check` | no deviation reported |
| `cheme assess lca --coverage` | partial screening carbon footprint; 12 gaps (8 unmapped exchanges, 4 uncharacterised emissions), each with a description; mass, element and carbon-origin balances closed |

## What was checked and found sound

- **Route and boundary** match issue #164: CO + Cl2 over activated carbon, condensation,
  caustic scrubbing, thermal oxidation; captive, no storage; chloroformate/isocyanate use
  outside (D-001).
- **Balances recomputed by hand** (independent of scripts/balance.py):
  - Cl2 12 505.6 kg/h (0.1 mol% O2) = 176.29 kmol/h Cl2; 99.995 % converted = 176.28 kmol/h
    COCl2; CO 1.05 x Cl2 = 185.10 kmol/h = 5195 kg/h. Matches S1, S2 and the extent.
  - Reaction heat: dHf(COCl2,g) - dHf(CO) = -108.6 kJ/mol, so about 5.31 MW at 298 K, minus
    the feed's sensible heat to 353 K, gives about 5.18 MW (Q1 5180.8 kW). ln K at 353 K
    from dGr(298) = -67.7 kJ/mol and dSr = -137 J/(mol K) is 20.5 (D-005 states 20.4).
  - Condensers: Clausius-Clapeyron from the normal boiling point gives about 263 kPa phosgene
    vapour pressure at 308 K. That leaves about 32 kmol/h phosgene uncondensed after E-102,
    so E-102 is about 1.07 MW (Q2 1078.5 kW) and E-103 about 0.48 MW (Q3 482 kW). The vent's
    9 mol% phosgene equals 30.6/340 kPa. Product Cl2 is 35 ppm(wt).
  - Scrubber: 4 x 0.925 kmol/h NaOH x 1.5 = 222 kg/h NaOH = 444 kg/h of 50 wt% (S20); 18 wt%
    in S22.
  - Oxidiser: 8.81 kmol/h CO x 283 kJ/mol = 0.69 MW, which heats 2796 kg/h of flue gas by
    about 800 K (1123 K is consistent). CO2 is 388 kg/h = 22.4 g/kg.
  - Per kg: CW (5180.8 + 1078.5)/17 346 = 0.361 kWh; brine 0.0278 kWh; power 19.2 kW =
    1.11 Wh. Carbon: 2223 kg C/h in = 2106 product + 11 liquor + 106 flue gas.
- **Plausibility for the technology**: 5 % CO excess, 2-5 bar(a), outlet below 100 C, boiling
  water coolant and < 50 ppm Cl2 all lie inside the cited patent ranges (SRC-2). A 99.47 %
  yield on Cl2, with the loss to caustic destruction, is plausible for a design without vent
  phosgene recovery, and DESIGN.md says so.
- **Sources and licences**: facts restated in own words with a source register; no tables,
  figures or passages copied (spot-checked DESIGN.md, narrative, lca/README.md, results.md);
  sources not read (Mitchell 2012, Ullmann, LVOC BREF) are declared as not read and not used
  for numbers; ASSUMED values marked in design-basis.yaml, flowsheet provenance and DESIGN.md.
- **LCI**: per 1 kg liquid phosgene (S7); mass in = mass out (21 461.2 kg/h); no zero-filled
  and no licensed background values (every background is `missing:` with the activity it
  should connect to); lca/mappings.yaml exists and is empty on purpose, with the reason.
- **process.yaml**: `maturity: concept` is the lowest value the schema allows, and the notes
  say that `cheme maturity` reaches no level and that the design is not reviewed. That is
  honest; the `maturity-claim-exceeds` warning cannot be cleared by lowering the claim.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#R-01 | process/flowsheet.yaml:357, scripts/balance.py:138, DESIGN.md:115 | T-201, S24, S23 | The spent liquor is set to 313 K (`T_EFF = 313.15`, sourced only as "D-008"). D-008 neither states nor justifies that value and says the heat of neutralisation "leaves with the liquor (no cooler)". COCl2(g) + 4 NaOH(aq) -> Na2CO3 + 2 NaCl + 2 H2O(l) releases about 444 kJ/mol (aqueous formation enthalpies), so 0.925 kmol/h gives about 114 kW. With no cooler, 1319 kg/h of liquor (cp about 3.6 kJ/(kg K)) heats up by about 80 K to roughly 380 K, at or above its boiling point at 120 kPa. The stated 313 K is not reachable as designed: either a liquor cooler of about 0.1 MW is missing (and its cooling water, about 0.006 kWh/kg, about +2 % of product:CW), or the scrubber runs near boiling, which changes the water content of S23 and the flow of S24. The mass balance and the LCI hardly change, but the scrubber description is physically inconsistent. | medium | open | Add a circulating-liquor cooler to T-201 (duty from the reaction enthalpy, its cooling water in Q-streams and product:CW), or give the outlet temperature from an energy estimate in balance.py; state the estimate in D-008 and mark it ASSUMED |
| 2026-10-28-pfd-lci-review#R-02 | lca/lca.yaml:84, DESIGN.md:173 | LCI, R-101 catalyst | D-012 says catalyst (activated carbon) replacement is "excluded and listed", but lca/lca.yaml has no exchange or exclusion for it, so it appears in neither gaps.csv, the coverage limitations nor dataset.yaml. A consumable of the reactor is missing from the inventory without a trace in the published dataset (the run report admits it). Its magnitude is probably small, but every omitted input should be a listed gap. | medium | open | Add a flow `feed:CATALYST` (activated carbon, amount unknown) with `missing:` and a description, or an exclusion entry with the reason, so that it shows in gaps.csv / the coverage; re-run `cheme assess lca --inventory --write` |
| 2026-10-28-pfd-lci-review#R-03 | DESIGN.md:148, lca/lca.yaml:84 | D-011 containment extraction | D-011 sends the extracted air of the containment enclosure to T-201. Neither the balance (S8 -> S23 -> X301), the power (D-010: no extraction fan) nor the LCI includes it, and it is not stated whether the extraction runs continuously or only in an emergency. If it runs continuously, its air flow would far exceed the 270 kg/h vent, dilute the CO below self-sustaining combustion (so support fuel would be needed) and dominate the scrubber and oxidiser sizing and the power. | low | open | State in D-011 whether the extraction is continuous or emergency-only; if continuous, record it as an open item and an LCI exclusion (fan power, support fuel) |
| 2026-10-28-pfd-lci-review#R-04 | lca/lca.yaml:85-86 | emission exclusions oxidiser-nox, fugitive-phosgene | The exclusions have no amount, so the cut-off criterion cannot be checked (`cheme.lca-cutoff-unchecked`, info). Thermal NOx at 1123 K with 15 mol% O2 in the flue gas is unlikely to be negligible for acidification categories later. | low | open | Give an order-of-magnitude upper bound (kg per year, ASSUMED, with a basis) for each, or state why the 1 % mass rule is met |
| 2026-10-28-pfd-lci-review#R-05 | DESIGN.md:18 | SRC-2 locator | EP1640341A2 is cited by "description and claims (Google Patents text, no paragraph numbers)". That locator is too coarse to trace the individual figures (CO excess, pressure, coolant pressure, < 50 ppm Cl2) back to the patent. | low | open | Cite the paragraph numbers [00xx] or claim numbers of the EPO publication for each figure used |

No critical or high finding.

## Not reviewed / limits

- No P&IDs, layout, HAZOP, datasheets or TEA exist (outside the issue scope).
- The condenser and scrubber energies cannot be cross-checked in core (core #315, #364); the
  condenser duties were checked by hand above, the scrubber energy gave R-01.
- CO dissolved in the liquid phosgene and CCl4 formation are not modelled; both are disclosed
  in D-005 as open items and were not raised again.
- Merge: pending. A human merges `case/phosgene-1`; the medium and low findings may be closed
  on the branch or carried forward.
