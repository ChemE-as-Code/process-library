---
topic: design
reviewed_commit: 38b2ae25c1b21cb5ae833b6251a9f3133ba11f7d
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/catalysts.yaml, lca/, scripts/aniline_balance.py, scripts/allocation_exergy.py, equipment/equipment-list.yaml, piping/line-list.yaml]
reviewer: review-agent
reviewer_kind: agent
branch: case/aniline-1
merge: pending
---

# Independent review: aniline-1 design basis, balanced BFD/PFD and preliminary gate-to-gate LCI

Issue ChemE-as-Code/process-library#148. This review covers the design agent's run
20261028-150043-design (commits d84b84b..38b2ae2 on `case/aniline-1`). It is a review only:
no design file was changed. Ids R-01... below are the record ids `2026-10-28-pfd-lci-review#1`...

## Re-run by the reviewer (HEAD 38b2ae2)

- `git diff --stat origin/main..HEAD -- ':(top)' ':(top,exclude)processes/aniline-1'`: empty.
  Nothing outside `processes/aniline-1/` changed (193 files, all inside the folder).
- `cheme validate`: 18 files, 0 errors, 0 warnings. Infos only: `decision-unknown` D-101 (the
  decanter tag D-101 read as a decision id, a false positive), D-023 (commented example in
  checks.yaml), catalyst poison not a component, loader cycle notes.
- `cheme check`: every concept gate except `layout-plot-plan` passes (layout out of scope);
  basic/detail gates fail on P&IDs, layout, datasheets, design review (this record), as expected
  for the run's scope.
- `cheme maturity`: calculation maturity none; `cheme.maturity-claim-exceeds` warning on the
  claim `concept` (the lowest value the manifest schema allows). Sourced level fails on the
  feed flows (design choices, `assumed`) and the reactor selectivity (`assumed`).
- `cheme process streams`: every block and step balance ok; RXN in 34 908.5 / out 34 908.1 kg/h;
  extents NB_HYD 269.05, BZ_FORM 0.539, DPA_FORM 0.135 kmol/h.
- `cheme process propagate --check`: exit 0, nothing stale.
- `cheme assess lca --coverage`: partial screening carbon footprint; 8 gaps, each with a
  description; mass balance closed; element balance not assessable (catalyst without
  composition); energy closure 32.4 % (energy exchanges only, explained in D-013).

## Independent checks of the numbers (hand calculations by the reviewer)

- Nitrobenzene 33 222 kg/h = 269.86 kmol/h = sum of the extents (269.05 + 0.54 + 2 x 0.135).
  Aniline to product 24 987.5 kg/h: overall molar yield 99.4 %; 1.329 kg NB / kg aniline
  against 1.322 stoichiometric. Plausible for the adiabatic Pd gas-phase process.
- Hydrogen: 810 kmol/h consumed + 14.9 kmol/h H2 in the purge = 825 kmol/h make-up (1686 kg/h);
  N2 in (0.83 kmol/h) = N2 in the purge. 0.0674 kg H2 / kg against 0.065 stoichiometric.
- Water formed 539.7 kmol/h (9 723 kg/h) = stripped water + product water + purge water.
  Ammonia formed 0.674 kmol/h = NH3 in S23 (0.12 wt%).
- Adiabatic rise 513 -> 729 K: about 18 200 kmol/h x ~31 kJ/(kmol K) x 216 K = 34 MW against
  the gas-phase reaction heat 269 kmol/h x 464.6 MJ/kmol = 34.7 MW. Consistent.
- K-101: 4.97 kmol/s, 400 -> 560 kPa(a), k about 1.39, efficiency 0.75: about 6.45 MW and 376 K
  outlet, matching Q1 6 484 kW and S4 376.5 K.
- V-101: water partial pressure 19.8 kPa (vapour pressure at 333 K 19.9 kPa x 0.993); aniline
  0.71 kPa (about 0.9 kPa x 0.786). The stated method reproduces.
- C-102 overhead 19.7 wt% aniline, close to the aniline-water heteroazeotrope; C-202 vapour
  402 kmol/h x ~45 MJ/kmol = 5.0 MW against Q5 4.75 MW (superheated feed). Plant energy:
  reaction heat (liquid basis, ~41.3 MW) + power 6.6 MW = 47.9 MW in; steam export 13.3 MW +
  cooling water 34.4 MW = 47.7 MW out. Closes as D-006 says.
- LCI: NB 33 222.3 + H2 1 686.2 = 34 908.5 kg/h in; aniline 25 000 + purge 70.4 + residue
  129.5 + water 9 708.2 = 34 908.1 kg/h out (0.001 %). Per kg aniline as D-013 states.
  Exergy allocation recomputed: steam 13 297 kWh/h x 1 278.9 kJ/kWh = 17.0 GJ/h against
  aniline 923 GJ/h: 1.81 %; 1 278.9 kJ per kWh (ratio 0.355) is consistent with saturated
  steam at 471 K raised from 378 K feed water.
- Recycle aniline and water at the reactor inlet (S6): 29.6 kmol/h aniline and 825 kmol/h
  water for 269.9 kmol/h NB (see R-01, R-02).

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:119 | D-005, S3/S6/S13 | R-01: D-005 says the loop gas returns aniline equal to 5.5 % of the production. The flowsheet recycles 29.6 kmol/h (2 755 kg/h) aniline in S13/S3/S6, i.e. 11.0 % of the 25 t/h product (S13: 72 779 kg/h, x_ANL 0.001732, M 4.26 kg/kmol). That is still below SRC-1's upper limit of 15 % as restated, but twice the figure the text gives and above the "preferably 5 %" that D-005 cites as support. | medium | open | Correct the figure in D-005 to the flowsheet value (about 11 %), or change V-101's temperature/pressure if 5 % is the intent. Re-check the statement that the design follows SRC-1's preferred recycle. |
| 2026-10-28-pfd-lci-review#2 | DESIGN.md:123, DESIGN.md:156 | D-005, D-007, S6 | R-02: At the reactor inlet (S6) the water is 0.0454/0.0148 = 3.06 mol per mol NB. D-005 cites SRC-1's most preferred range as 4-25 mol water per mol nitro groups, and D-007 claims that 333 K "gives SRC-1's inlet water ratio". The ratio is below the cited range, so the decision text contradicts the stream table. | medium | open | Either state that 3 mol/mol is below the most preferred range and why that is acceptable, with the patent's broader range and its locator, or lower the separator temperature / raise the pressure until the ratio reaches 4. Correct D-007's sentence either way. |
| 2026-10-28-pfd-lci-review#3 | lca/lca.yaml:72 (flows) | E-103 boiler feed water | R-03: E-103 raises about 23.5 MW of 1500 kPa(a) steam, 13.3 MW of it exported (about 0.85 kg steam per kg aniline leaves the gate). The exergy allocation assumes boiler feed water at 378 K, but the inventory has no feed-water / demineralised-water input, no deaerator steam and no BFW pump power. These exchanges are not listed as gaps either. hydrogen-1, which D-013 names as the worked example, inventories its demineralised make-up water (feed:DMW). The LCI therefore omits a technosphere input silently, which the run's rules forbid (every unmapped background is a reported gap). | medium | open | Add a boiler feed water stream (or a utility) for the exported steam to the flowsheet, carry it into lca/lca.yaml as a flow with `missing:` and a description of the background (deionised water at the user), and either add the BFW pump to Q3 or state it inside the 150 kW lump. Alternatively, record in D-013 a library rule that makes the steam co-product carry its own feed water, with its source. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:129, process/flowsheet.yaml (S22, S23) | C-102, NH3 | R-04: All ammonia (11.5 kg/h) is sent with the stripped water S23 to biological treatment. A steam stripper at 101 kPa(a) and 373 K strips dissolved NH3 almost completely into the overhead. In the plant it would build up in the D-101/C-102 loop or leave through a vent, i.e. as an air emission or an off-gas to treatment, not with the bottoms. D-005 notes that part of the NH3 may stay in the gas, but not the stripper behaviour. The quantity is small (0.46 g/kg aniline). | low | open | Add to D-005/D-008 that the NH3 split in C-102 is ASSUMED and physically optimistic, and add an open LCI gap or an emission exclusion for the NH3 vent of the D-101/C-102 loop. |
| 2026-10-28-pfd-lci-review#5 | process/flowsheet.yaml (S3-S10 pressures), DESIGN.md:120 | K-101, loop pressure drop | R-05: Electricity (0.26 kWh/kg, 98 % of it K-101) is the second-largest LCI exchange after nitrobenzene. It follows directly from an ASSUMED loop pressure drop of 160 kPa: E-102 20+25, reactor 30, E-103 15, E-104 50, separator 10 kPa, a pressure ratio of 1.4. No source or sensitivity is given; E-104 alone at 50 kPa is high for a gas cooler-condenser. | low | open | State the pressure-drop basis in D-005 and give a sensitivity, e.g. 80 kPa loop drop, about half the circulator power, in D-013 or the LCA README so that a reader does not take 0.26 kWh/kg as a design result. |
| 2026-10-28-pfd-lci-review#6 | DESIGN.md:22 | SRC-1, SRC-2, SRC-5 | R-06: The locators are coarse ("description (operating ranges)", "examples 1-5") without paragraph numbers. SRC-1 and SRC-2 were read as a "machine summary" of the Google Patents page, and SRC-5 was "not re-read". The key sourced values (selectivity 0.997 from example 3, the H2/NB and water ranges, catalyst loading, Pd content) cannot be traced to a paragraph, and R-02 suggests at least one restated range needs checking. | low | open | Give paragraph numbers ([00xx]) or claim numbers for each fact taken from SRC-1/SRC-2. Have a human verify example 3's selectivity and the water-ratio range against the patent text. Give the Szargut table locator (element exergies) or a re-read open source. |
| 2026-10-28-pfd-lci-review#7 | lca/lca.yaml:121 (consumables, disposal) | catalyst disposal | R-07: The catalyst disposal carries a `missing:` text ("precious-metal refining of spent catalyst not mapped yet"). The inventory nevertheless maps it `free` (recyclable under cut-off) and it is not in gaps.csv. D-013 says "catalyst and its disposal" carry `missing:`. Under the cut-off system model the burden-free outflow is correct, but the text says otherwise. | low | open | Remove the disposal `missing:` (state that the recyclable outflow is burden-free under cut-off), or keep the refining as a declared gap if the study wants it. Align D-013's wording. |
| 2026-10-28-pfd-lci-review#8 | process.yaml:35 | maturity / validation.notes | R-08: `maturity: concept` is the lowest manifest value and D-012 explains why. However `validation.notes` does not say that `cheme maturity` reports calculation maturity "none" and the warning `cheme.maturity-claim-exceeds`. Only a YAML comment says it, and comments do not reach the Atlas. In `cheme maturity`'s model basis, V101, D101, C201, C202 and C102 show as "predictive, sourced" (a core default for steps without a model). Their outlets are actually assumed values from the unqualified script, as D-006 and the method table state correctly. | low | open | Add one sentence to `validation.notes`: calculation maturity none, claim exceeds evidence, reasons as in D-012. Report the default "predictive, sourced" label of model-less separators to core, or declare the separators' model basis as specified/assumed if the schema allows it. |

## Previous findings

None: first review of this process folder (no earlier records in reviews/).

## Drawing

No P&ID in scope (out of scope of the run; `pid/` holds only a README). The BFD and PFD are
generated by `cheme process build`, and `cheme validate` reports no `cheme.generated-edited` and
no drawing finding on them. They were not rendered or inspected visually in this review.

## Checked and fine

- Route and boundary match the issue: gas-phase hydrogenation, condensation, water
  separation, aniline distillation. Nitrobenzene and hydrogen enter as boundary feeds, the
  hydrogen-1 link is noted (S17 state), and the wastewater with its aniline content is noted.
  Rejected alternatives (fluid-bed Cu, liquid phase, nitration inside) are recorded.
- Mass, component and element balances close (cheme). Plant energy closes in the script within
  0.3 %, and the reviewer's hand balance agrees.
- Plausibility for the technology: reactor 513 -> 729 K (below the 500 C limit cited), 5 bar,
  H2/NB 60, selectivity 99.7 %, NB 1.329 kg/kg, H2 0.067 kg/kg, process water 0.39 kg/kg,
  column steam 0.41 kWh/kg, steam export 0.53 kWh/kg, product 99.95 wt%, stripped water 50 ppm
  aniline. All are in the expected range for an adiabatic Pd gas-phase plant.
- Key values carry `source:`/`provenance:`; estimates are marked ASSUMED (design basis, stream
  provenance `assumed` with the script and decision, selectivity `assumed` with the sourced
  and assumed parts separated). The basis table separates sourced, proposed and missing values.
- No third-party tables, figures or passages copied: DESIGN.md, process.yaml, narrative and LCA
  texts restate facts in the agent's own words with citations. Ullmann's (licensed) is listed
  as "not read, no value taken". No licensed (e.g. ecoinvent) value or factor appears.
- LCI per functional unit (1 kg aniline), every foreground exchange tied to a stream or energy
  stream id. Every technosphere background is `missing:` with a description of the activity to
  connect, no zero fill, gaps.csv lists the 8 gaps. Per-process override (`feed:H2F
  atlas: false`) is in this folder's `lca/mappings.yaml`, with its reason. The emission
  exclusions are declared as open gaps, not as negligible. The allocation deviation is recorded.
- process.yaml: `publication.status: internal`, `validation.status: unreviewed`, honest
  description of what is assumed and gated. The missing chemicals registry entries are listed
  for the consolidated PR.
- No file outside `processes/aniline-1/` changed.

## Not checked

- The cited patents were not re-read by the reviewer (no web access used in this review).
  Patent facts were checked for internal consistency only (see R-02, R-06).
- The BFD/PFD were not rendered or looked at.
- scripts/aniline_balance.py was not re-run. Its outputs were checked by hand balances and
  `cheme process streams` only.
- The library LCI build (`scripts/build_lci.py --strict`) was not re-run.
- Turndown (50 %, ASSUMED, "not checked yet") and start-up cases.
