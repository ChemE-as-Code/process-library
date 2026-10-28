---
topic: design
reviewed_commit: a6f61ad8f68e4ebbea05fbd2e5ff9ea8cdb2fc1b
scope: [DESIGN.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, piping/line-list.yaml, lca/, process.yaml, scripts/bayer_balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/alumina-1
merge: pending
---

# Alumina-1 (Bayer process) concept design and preliminary LCI: independent review

Branch `case/alumina-1` (issue #178), 6 commits from the merge base with `origin/main`
(3c32ac6..a6f61ad). I am an independent agent and did not write this design. I reviewed the
design files and the LCI and changed none of them. The design is at concept stage, so P&IDs,
layout, datasheets, HAZOP and TEA are out of scope.

Finding ids are `2026-10-28-pfd-lci-review#n`. In the run task's numbering, R-01 is #1, R-02 is
#2, and so on.

## What was re-run (not taken from the run report)

| command | result |
|---|---|
| `git diff --name-only $(git merge-base origin/main HEAD)..HEAD` | all 192 changed paths are under `processes/alumina-1/`. A plain `origin/main..HEAD` diff also shows deletions of other cases because main has moved on since the branch point; those deletions are not changes made on this branch |
| `cheme validate` | 17 files, 0 errors, 0 warnings. The infos are `decision-unknown` D-012/D-023 (from commented template lines in `control/cause-effect.yaml` and `checks/checks.yaml`, harmless) and the usual dexpi.load cycles |
| `cheme check` | every concept gate except `layout-plot-plan` passes (layout is out of scope). Basic gates fail on the missing P&IDs and layout and on this review, which is expected |
| `cheme maturity` | calculation maturity none; `cheme.maturity-claim-exceeds` warning on `maturity: concept` (see #5) |
| `cheme process streams` | 6 blocks and 19 steps close; extents SLAKE 115.9, DESIL 3.49, TCA 38.6, DIG 2507.8, PREC 2427.4, CALC 1213.7, SODA 8.07, COMB 436.3 kmol/h |
| `cheme process propagate --check` | exit 0, nothing stale |
| `cheme assess lca --coverage` | partial screening carbon footprint; 10 gaps, each `missing:` with a description of the activity to connect; mass, element and carbon-origin balances closed; DQR 2.33 |
| `cheme impact` | nothing to review |

## Hand checks of the numbers

- **Alumina recovery.** The dry bauxite is 274 169 x 0.90 = 246 752 kg/h, with 54.69 % Al2O3, so
  134.9 t/h Al2O3 goes in. The product carries 125 000 x 0.99 = 123.75 t/h Al2O3, which is
  1213.7 kmol/h and equals the CALC extent. Recovery is therefore 91.7 %, plausible for a
  gibbsitic ore, with losses to DSP, TCA, undigested diaspore and the residue liquor. The PREC
  extent (2427.4 kmol/h) is exactly 2 x CALC, so the seed inventory is at steady state. The
  difference DIG - PREC = 80.4 kmol/h is accounted for by TCA (77.3 kmol/h NaAlO2) plus the
  aluminate in the cake liquor.
- **Specific consumptions against the cited facts.** Wet bauxite is 2.19 t/t (1.97 t/t dry).
  That is below the IAI 2019 global average of 2.685 t/t, which is consistent with a
  54.7 %-Al2O3, 0.76 %-SiO2 ore. Lime is 52 kg/t (IAI s. 3.11.2.3), electricity 152 kWh/t
  (547 MJ/t, IAI Table 4), and natural gas 56 kg/t, i.e. 2.80 GJ/t LHV at 50 MJ/kg, against
  about 2.72 GJ/t from ICSOBA 2017 AA22. Fossil CO2 is 56 x 44/16 = 154 kg/t, which matches
  `emission:CO2`.
- **Sodium.** The DSP takes 3.486 x 8 = 27.9 kmol/h Na, or 1115 kg/h as NaOH. The product's
  0.40 % Na2O is 500 kg/h, or 645 kg/h as NaOH. The cake liquor (0.05 % NaOH and 0.27 % NaAlO2
  of 94.8 t/h) is about 170 kg/h as NaOH. The total of about 1930 kg/h matches the make-up of
  1935 kg/h NaOH (S5, 3870 kg/h of 50 % solution).
- **Liquor productivity.** Spent liquor is 2006 t/h at 1.30 kg/L, or 1543 m3/h. 125 t/h of
  alumina from that is 81 g/L, which equals 250 g/L x (0.70 - 0.38). That is a typical yield
  for seeded precipitation, and 12.3 m3/t is a typical circulation.
- **Calciner gas.** CH4 436.3 kmol/h needs 872.7 kmol/h O2 stoichiometrically; with 1.15 excess
  that is 1003.6 kmol/h. The air (S35, 138.8 t/h at 23.2 wt% O2) checks, and the flue gas O2 of
  4.19 t/h (131 kmol/h) is 0.15 x stoichiometric. Flue gas H2O is 0.778 kg/kg: hydrate water
  0.53, cake water 0.13 and combustion water 0.126.
- **Heats of reaction** (reactions.yaml, from the formation enthalpies stated there). DIG:
  (-240.12 - 1502.5) - (-1293.1 - 470.11) = +20.59 kJ/mol. CALC: -1675.7 + 3(-241.82) +
  2(1293.1) = +185.04 kJ/mol, i.e. 1.815 GJ/t Al2O3. SLAKE: -64.27 kJ/mol. The arithmetic is
  right, and the values agree with what I know of the NBS tables and Robie and Hemingway (see #4
  on their locators).
- **Duties.** I checked E-401 at 2.219 Mt/h x 3.35 x 22 K = 45.4 MW, of which 70 % (31.8 MW, Q8)
  is recovered and 13.6 MW (Q5) goes to cooling water. R-401 is about 33 MW of sensible heat
  plus 13.9 MW of precipitation heat, giving 46.9 MW (Q6). E-501 evaporates 52.9 t/h of water
  at an economy of 3, which needs 10.3 MW (Q3). All of these are consistent. For E-101, see #3.
- **LCI.** The inventory is per 1 kg ALU. Inputs total 3.5767 kg and outputs 3.5767 kg. There
  is no zero-filled background and no licensed value: all 10 backgrounds are `missing:`, each
  with a description, listed in `lca/gaps.csv`. The per-process overrides (NG by mass, MPS/LPS
  as heat delivered) are in `lca/mappings.yaml`. Air, N2, O2 and H2O are free, and the calciner
  pollutants and tank vents are declared exclusions rather than zeros.
- **Licences.** Bauxite assay numbers are cited as facts from Zainudeen et al. (2023, CC BY 4.0),
  and single facts from the IAI report are cited with section locators. I found no copied
  tables, figures or passages, and no ecoinvent or other licensed values.
- **Route and boundary.** These match issue #178: a Bayer gate-to-gate case per kg of
  smelter-grade alumina, with smelting, mining, lime burning, caustic production and utilities
  outside the boundary.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | lca/lca.yaml:52-63, lca/lca.yaml:39-41, process.yaml:12-28 | feed:MPS, feed:LPS, feed:NAOH | DESIGN.md D-007 says the steam heat (2.42 GJ/t, 0.67 kWh/kg) is "likely LOW": steam is 0.9 times the calciner energy, where the author's own source says about 1.6 times, and total delivered energy is 5.8 GJ/t. D-005 says the caustic make-up (15.5 kg NaOH/t) is "a lower bound and likely well below refinery practice". Neither caveat reaches the LCI or the manifest. The `source:` fields of these flows in lca.yaml (and so dataset.yaml), and the process.yaml summary, description and validation notes, give the values without the known low bias. The symmetric default uncertainty (gsd2 1.5) also ignores the bias. Once backgrounds are mapped, steam heat is the second-largest climate driver, so a dataset user would get an understated footprint without any warning. The balance and gaps are not affected, and D-005/D-007 are explicit, so this is medium | add the caveat to the three `source:` texts in lca.yaml and to the process.yaml description and validation notes, and regenerate the LCA outputs. Optionally, add a sensitivity scenario with steam scaled to the sourced 1.6x-calciner split and a higher caustic make-up, both marked ASSUMED |
| 2026-10-28-pfd-lci-review#2 | DESIGN.md D-008, D-004, D-007; process.yaml references | calciner energy, digestion temperature, energy split | The two ICSOBA papers that set the calciner specific energy (the largest direct fossil input) and the steam-to-calciner cross-check were read at abstract level only ("PDF text not extractable"). The locator is just "abstract", with no page or table. The value is plausible for gas suspension calciners, but it rests on an unread source | read the papers (or an open equivalent such as the non-ferrous metals BREF alumina chapter), then give a page or table locator, or say "abstract" in the `source:` text of the NG flow |
| 2026-10-28-pfd-lci-review#3 | scripts/bayer_balance.py:390-397; process/flowsheet.yaml S8, Q2 | E-101 / S8 / S4 | Q2 (E-101, LP steam) is sized to bring the whole mill feed to 373 K: the spent liquor, plus the bauxite from 298 K, plus the milk of lime and make-up "from ambient". But S8 (E-101 outlet) is given at 373.15 K, so the heat for the bauxite (about 7.0 MW; the terms 71.1 + 7.0 + 4.0 for the milk + 0.3 for the make-up add up to Q2 + Q8 + Q9) appears in E-101's duty while the stream temperature says it is not in the liquor. S4 (milk of lime) is at 353 K, yet it is counted from 298 K, which overstates the heat by about 2.9 MW. The supplies to E-101 (Q8 + Q9 + Q2 = 82.3 MW) exceed the liquor's sensible change S7 -> S8 (2.01 Mt/h x 3.35 x 38 K = 71.1 MW). The net LP steam error is a few MW, or under 5 % of the steam, and it points the opposite way to #1 | either raise the S8 temperature to the value that brings the mill discharge to 373 K, or move the bauxite heating term to G-101 in the script's text. Count S4 from 353 K. State the result in D-007 |
| 2026-10-28-pfd-lci-review#4 | process/reactions.yaml:5-9, DESIGN.md section 6 | formation enthalpies | The heats of reaction are "recalled, not checked" against NBS / Robie and Hemingway, with no table or page locator. My spot check found the arithmetic correct and the values consistent with those tables. Even so, a published source register should not list "recalled" sources | check the five values against the tables, then give the locators and drop "recalled" |
| 2026-10-28-pfd-lci-review#5 | process.yaml:33-36 | maturity | `cheme maturity` warns `maturity-claim-exceeds`: the evidence supports no design maturity, and `concept` is claimed. The comment explains this honestly (concept is the manifest's lowest level, and the feeds are ASSUMED), and `validation.status: unreviewed`. Nothing misleads, but the warning stays | keep it, or, if the schema allows, record the claim/evidence gap in `validation.notes` explicitly (it is already partly there) |
| 2026-10-28-pfd-lci-review#6 | process/flowsheet.yaml:324-337 | steps M501 / T501 | Step `M501` (caustic make-up tank) links to tag T-501, and step `T501` (hot water tank) links to tag T-502. The links and the line list are correct, but a step id that spells another item's tag invites mistakes when the P&IDs are drawn. The lca.yaml `liquor-tanks` exclusion lists T-501 and T-502 correctly | rename step T501 to T502 (or M502) when the flowsheet is next touched |
| 2026-10-28-pfd-lci-review#7 | lca/lca.yaml:88-101 | emission exclusions | `cheme assess lca` reports `lca-cutoff-unchecked`: the calciner pollutants and the tank-vent exclusion have no amount in kg, so the 1 % cut-off cannot be checked. The NOx, SO2 and dust of a gas suspension calciner are small by mass, but they matter for non-climate categories later | when D-010's open item is worked, give the order-of-magnitude amounts (`cutoff: per_year, unit kg`) from a cited source |

## What is good

- The balance is independent (`scripts/bayer_balance.py`) and closes on mass, components and
  elements, and the liquor recycle is converged.
- Assumptions are declared consistently: the design basis and every reaction and flow carry
  ASSUMED or a source.
- The bauxite normative mineralogy is cross-checked against the assay LOI (29.60 vs 29.69 wt%),
  and the Sangaredi column was rejected with a reason.
- The gaps are honest, with no zero filling. The author flagged the two weak numbers (steam and
  caustic) in DESIGN.md.

## Verdict

There are no critical or high findings. The balance closes, the LCI is per functional unit and
consistent with the flowsheet, and every background gap is declared. #1 (medium) should be
closed before the dataset is published to the Atlas. Merge is pending: a human or the reviewer
merges, not the author.
