---
topic: design
reviewed_commit: a581b3658ab788833f9c1be719cafba0739480e6
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, equipment/equipment-list.yaml, lca/, scripts/balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/chloromethane-1
merge: pending
---

# Design review: chloromethane-1 concept PFD and preliminary LCI (issue #151)

Independent review by an agent that did not write the design. The design files were not
changed. Reviewed commit `a581b36` on `case/chloromethane-1`.

## What was checked and how

- Branch content: `git log --oneline origin/main..HEAD` (4 commits: scaffold, basis/PFD, LCI,
  run record). `git diff --name-only origin/main...HEAD` (against the merge base `cc5624f`)
  lists files under `processes/chloromethane-1/` only: nothing outside the folder changed. The
  plain two-dot diff also shows `processes/thf-1/` as deleted, but only because `origin/main`
  merged thf-1 (#213) after this branch started. The branch does not touch thf-1, and since the
  two folders are separate the merge should not conflict.
- Re-run here (the run report's numbers were not taken on trust):
  - `cheme validate`: 16 files, 0 errors, 0 warnings. Three infos: two loader cycle notes, and
    `decision-unknown D-023`, which comes from a commented example in the template's
    `checks/checks.yaml`, not from this design.
  - `cheme check`: every concept gate passes except `layout-plot-plan`. Basic-stage gates fail
    as expected for a concept case: no P&IDs, no layout, no datasheets, and before this record
    no design review.
  - `cheme maturity`: calculation maturity none. Warning `cheme.maturity-claim-exceeds` on
    `process.yaml:41` (see #5).
  - `cheme process streams`: all 4 blocks and 12 steps balanced. Extents 248.8 kmol/h
    (hydrochlorination) and 1.51 kmol/h (DME).
  - `cheme process propagate --check`: clean, nothing stale.
  - `cheme assess lca --coverage`: mass, element and carbon-origin balances closed. 9 gaps,
    each with a description of the activity it should link to. Result "partial screening
    carbon footprint", no total claimed. Publishable.
- Hand checks of plausibility (general engineering knowledge, rounded ideal-gas data):
  - Methanol 0.646 kg/kg against a stoichiometric 0.635 (CH3Cl yield on methanol 98.2-98.3 %).
    Losses: DME about 1.2 %, CH3Cl in the purge and spent acid about 0.5 %. This closes to the
    fresh feed.
  - HCl 0.823 kg/kg against a stoichiometric 0.722. The excess leaves as about 21 wt% acid,
    near the HCl-water azeotrope, so the excess is intrinsic to the chosen boundary (I-04).
  - Dilute acid 0.447 kg/kg × 0.79 water = 0.353 kg, against 0.357 kg of reaction water per
    kg product: consistent.
  - DME in the spent acid (861 kg/h × 8 %) = 69 kg/h, against 1.51 kmol/h × 46 = 70 kg/h:
    consistent.
  - Reactor heat: ΔHr(298, gas) about −30 kJ/mol × 248.8 kmol/h ≈ 2.1 MW released, minus about
    0.5 MW of sensible heat from 523 to 613 K, leaves about 1.6 MW, against the modelled
    1.51 MW. Plausible.
  - Compressor: 5.5:1 in two intercooled stages, η 0.75, for about 262 kmol/h gives about
    0.5 MW, matching the modelled 495 kW.
  - Overall energy, on a liquid-methanol / liquid-product basis: reaction (about −56 kJ/mol)
    plus HCl absorption plus steam plus power ≈ 8.4 MW, against 8.1 MW to cooling water.
    Closes within the hand-estimate accuracy (but see #3).
  - LCI: mass in 1.5209 kg = out 1.5209 kg per kg product. 100 kt/a is a plausible
    single-train scale.
- Sources:
  - US 4,794,204 (S1) was fetched and the cited facts compared. They match: alumina process
    350-400 C, crude gas methanol < 0.03 %, DME 0.3-2 %, HCl < 2 %, water about 0.1 %, drying
    acid ≥ 80 % (95 % most used), spent acid about 80 % with 5-10 % DME, quench acid 20-25 %
    HCl.
  - Schmidt et al. 2014 (S2) could not be opened here (publisher returned HTTP 405), so its
    97.6 % / 98.8 % is unverified by this review. It is cited with a locator (abstract) and
    kept `assumed` for the transfer to an industrial bed.
- Third-party content: the source register and the decisions state facts in the design's own
  words with locators. No tables, figures or passages are copied, and no licensed values are
  used (Ullmann is listed as not read, and the LCI has no background factors).
- LCI structure:
  - per 1 kg CH3Cl (S17), single product, no allocation;
  - every background is `missing:` with a description, none zero-filled;
  - the two per-process overrides (steam in kWh, anhydrous HCl kept from linking to aqueous
    acid) are in `lca/mappings.yaml`, each with a reason;
  - exclusions are declared without an amount and the tool reports them as unchecked.
- `process.yaml` is honest:
  - `publication.status: internal` and `validation.status: unreviewed`;
  - the notes say `cheme maturity` reaches no level and that the LCI has no impact result.
- Route and boundary match the issue: gas-phase methanol hydrochlorination, with the methane
  chlorination route deliberately kept apart. The issue left route, capacity and boundary to
  be scoped, and DESIGN.md D-001/D-002 scopes them, ASSUMED where unsourced.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | - | process/flowsheet.yaml:342 (S07), DESIGN.md:124 (D-006), DESIGN.md:148 (D-008) | R-01. The crude gas after the quench holds 2.6 mol% water (water activity 0.7 over 21 % acid at 313 K, ASSUMED). The cited source S1, whose facts DESIGN.md's own register lists, gives about 0.1 % water in the cooled crude gas and 0.1-0.2 % in its plant embodiment, where the graphite cooler condenses 35-40 % HCl (much lower water activity). The design is 13-26 times above its own source, and D-006 does not discuss the difference. D-008 then calls the resulting 80.5 % spent acid a consistency check with S1, but the check works only because of the 2.6 mol% water: with S1's water content the spent acid at the same DME-limited acid rate would be about 95 %. The 80 % agreement is therefore not independent support. It does not break the balance or the LCI: the acid feed is set by the DME limit, and the spent acid mass would drop from 0.069 to about 0.06 kg/kg. | medium | open | State the contradiction in D-006 and either justify 2.6 mol% (313 K with no stronger final condensate) or follow S1 (graphite cooler condensate 35-40 % HCl, about 0.15 % water) and re-run `scripts/balance.py`. Reword D-008's check so it does not claim agreement with S1 that rests on the assumed water content. |
| 2026-10-28-pfd-lci-review#2 | - | DESIGN.md:118 (D-005) | R-02. D-005 says the 340 C outlet is "inside S1's 300-400 C". S1 (and the register row at DESIGN.md:57, and process.yaml references) gives 350-400 C for the alumina process, so 340 C is just below S1's range. It is inside S6's 300-390 C and is S2's data point, so the choice itself holds. | low | open | Correct the quoted range to 350-400 C and base the claim on S2/S6, or say that 340 C is slightly below S1's range. |
| 2026-10-28-pfd-lci-review#3 | - | process/flowsheet.yaml:373 (S10), scripts/balance.py:230-233 | R-03. C202 heats its feed from 313 to 383 K (about 395 kW of the 541 kW LP steam), and S10 leaves at 313.15 K "after a product cooler, lumped into C202". That cooler's duty is in no energy stream: Q13 is only the overhead condenser. About 0.03 kWh/kg of cooling water (5 % of 0.649) is therefore missing from the LCI. Alternatively, a feed/bottoms interchanger, the usual arrangement, would cut the LP steam by about 12 %. | low | open | Either add the bottoms-cooler duty to Q13 or a new CW stream, or model a feed/bottoms interchanger and reduce Q05, then regenerate the LCI. |
| 2026-10-28-pfd-lci-review#4 | - | DESIGN.md:104 (D-004) | R-04. The modelled DME is 1.33 times its equilibrium quotient at the reactor outlet: a state the reaction cannot reach from the methanol side. D-004 records this openly and argues it is conservative (DME is cleaved back by HCl). Acceptable at concept on one data point, but the selectivity basis remains the weakest link of the reactor model. | low | open | At basic stage (I-03), take the DME selectivity from the full text of S2/S7 or cap it at equilibrium. No change needed for this stage. |
| 2026-10-28-pfd-lci-review#5 | - | process.yaml:41 | R-05. `cheme maturity` warns `maturity-claim-exceeds`: the evidence supports no design maturity, and `concept` is claimed. The schema has no level below `concept`, and the comment and `validation.notes` state honestly that no level is reached, so a reader is not misled. | low | open | Keep `concept` (schema floor) with the existing note, or accept the warning explicitly. Raising the evidence needs sourced feed specs and separator splits (cheme maturity, `sourced` requirements). |
| 2026-10-28-pfd-lci-review#6 | - | DESIGN.md:57 (S1 locator) | R-06. S1's locator is "Description, first paragraphs ... sections located, no column numbers", and S2 is cited from an abstract. These are acceptable locators for a concept study, but the S1 facts carry all the checks (D-006, D-008), and a reader cannot find them quickly. | low | open | Add the column/line numbers of US 4,794,204 for the crude-gas, drying-acid and plant-embodiment facts. |

## Previous findings
None: this is the first review of chloromethane-1.

## Conclusion

The concept PFD is balanced, the numbers are plausible for alumina-catalysed gas-phase
hydrochlorination, and every key value is sourced or marked ASSUMED. The LCI is per functional
unit, consistent with the flowsheet, and has no zero-filled or licensed background values.
Every background is listed as a gap with a description. No critical or high findings. One
medium finding (#1: the crude-gas water content contradicts the cited source, and the "check"
built on it is not independent) and five low ones should be fixed in a follow-up. They do not
block the merge. Merge pending: by a human, not the author.
