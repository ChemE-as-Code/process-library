---
topic: design
reviewed_commit: 432d206a42807367ce3cd7cda551c9dc7b612040
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/simulation.yaml, process/BFD.xml, process/PFD.xml, scripts/sic_balance.py, equipment/equipment-list.yaml, piping/line-list.yaml, lca/, PROGRESS.md, runs/20261028-160349-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/silicon-carbide-1
merge: pending
---
# Review: design (concept BFD/PFD and preliminary LCI, silicon carbide by the Acheson process, issue #179)

An independent agent reviewed this. It did not write the design and changed no design files. I
reran every claim of the run report myself.

## Branch and scope

- `git log --oneline origin/main..HEAD` shows 4 commits: f4dc4fe scaffold, 7603cc8 design basis,
  materials, reactions, BFD/PFD, 89b8e7b LCI, DESIGN.md and manifest, 432d206 run record.
  `origin/main` has moved on since the branch point 7da4a74. The two-dot diff therefore shows
  other cases as deleted. The three-dot diff (`git diff --stat origin/main...HEAD`) touches only
  `processes/silicon-carbide-1/` (192 files, +64550, nothing removed). **Nothing outside the
  folder changed.**
- `cheme diff 7da4a74 --list` adds only BFD/PFD process-model items (sources, sinks, blocks,
  steps, streams, templates). Nothing is modified or removed. There are no P&IDs.
- The route and boundary match #179: Acheson batch resistance furnace, gate-to-gate from sand,
  coke and air to crushed crude crystalline SiC. Grain processing is outside the boundary. The
  furnace is not treated as an ideal or Gibbs gas reactor, and no kinetics are invented
  (D-001, D-007).

## Commands rerun

| command | result |
|---|---|
| `cheme validate` | 17 files, 0 errors, 0 warnings. Info only: `cheme.decision-unknown` for D-023 (checks/checks.yaml:76) and D-012 (control/cause-effect.yaml:13), both in commented template examples; DEXPI loader cycles. Compared 2 sheets (BFD, PFD) and 12 lists. The list-vs-P&ID cross-checks were skipped because there is no P&ID. |
| `cheme check` | Every concept gate passes except `layout-plot-plan`, which is out of scope. The basic and detail gates fail as expected for a concept case: `pids-exist`, `design-review` (this record), layout, mto, datasheets. |
| `cheme maturity` | Calculation maturity `none`, with a `cheme.maturity-claim-exceeds` warning (claims `concept`). `sourced.boundary` fails: the S1, S2 and S6 flows and compositions are assumed. `balanced.model-basis` fails: the RX1/RX2 and burn-off conversions and the Z101 split are unsourced. All balances are evaluable and closed. |
| `cheme process streams` | 4 blocks and 7 steps balance. Extents: RX1 150.45, RX2 0.75, COX 211.16, CH4X 29.57, SOX 3.18, SIOX 0.75 kmol/h. |
| `cheme process propagate --check` | Clean, no output. |
| `cheme assess lca --coverage` | Partial screening carbon footprint with 9 gaps: 5 `missing:` backgrounds (SAND, COKE, POWER, WASTE, CW) and 4 elementary flows outside the method (CO, SO2, SiO2, SiC). The mass, element (Al, C, H, N, O, S, Si) and carbon-origin balances close. |
| `cheme assess lca --check` | Every lca/ output is current. |
| `cheme run scripts/sic_balance.py` | Reproduces every stream, duty and per-kg figure of `flowsheet.yaml`, DESIGN.md D-006 and the run report. |

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | R-01: lca/results.md:14, lca/results.csv; process.yaml:34-45 | LCA headline | The only number the LCA reports is 2.03 kg CO2-eq per kg crude SiC, with a 95 % interval of 1.46-2.93. That is the direct furnace CO2 and CH4 alone. The dominant exchange, 7.7 kWh electricity per kg, is a gap. At any plausible grid intensity it adds a comparable or larger amount (about 2-5 kg CO2-eq/kg). Coke, sand and landfill are also gaps. The files do say "partial screening" and "with gaps", but `process.yaml` has `lca: {source: auto}`, so a catalogue reader can take 2.03 and its interval as the cradle-to-gate footprint (the declared boundary). Nothing says in plain words that it is the direct process emission only. This is the same issue as soda-ash-1 R-01. | medium | open | Say in `process.yaml` `validation.notes` and in the `lca.yaml` goal that the reported value is the direct (scope-1) furnace emission only, not a carbon footprint, and that the interval covers only those amounts. Alternatively, keep the LCA out of the catalogue until at least electricity is mapped. |
| 2026-10-28-pfd-lci-review#2 | R-02: lca/lca.yaml (`emission:CO`); lca/results.md "Outside the methods" | CO in the climate result | 0.406 kg CO per kg crude SiC (30 % of the furnace CO, unburnt) is counted as "outside the method", so it adds nothing. Fossil CO oxidises to CO2 in the atmosphere. The IPCC/EPA factor that the author uses as a cross-check (2.62 t CO2/t SiC) counts all gas carbon as CO2, and common LCIA implementations give fossil CO about 1.57 kg CO2-eq/kg. Counted that way, the direct climate result is 2.67, not 2.03 kg CO2-eq/kg (+31 %). A reader who compares 2.03 with 2.62 would think the design emits less than the IPCC default. In fact it matches the default within the -7 % that D-006 states. | medium | open | Characterise fossil CO by its oxidation (1.57 kg CO2-eq/kg, with source), or report CO's CO2 equivalent beside the headline and state in D-010 why it is excluded. |
| 2026-10-28-pfd-lci-review#3 | R-03: process/simulation.yaml:10; process/flowsheet.yaml:259 (S7); piping/line-list.yaml FG-101 | B-101 burn-off energy and flue gas | `simulation.yaml` declares B101 adiabatic, but its streams cannot be adiabatic. The burn-off releases about 23.6 MW (COX 16.6, CH4X 6.6, SOX 0.26, SIOX 0.17 MW, from the extents and the stated heats of reaction), and S5 brings about 2 MW of sensible heat at 1000 K. Heating the 55.9 t/h of S7 from 298 to the assumed 600 K takes only about 5 MW. With the modelled air (twice stoichiometric), an adiabatic outlet would be about 1600-1700 K. Reaching 600 K needs either about 20 MW of loss (radiation from the open charge) or roughly five times the gas flow through hood dilution air, which "is not modelled". The flue flow and temperature on the PFD and in the line list FG-101 (55.9 t/h at about 600 K) are therefore not a consistent stack condition. Stack duct and fan sizing from them would be wrong by several times. The LCI is not affected, because air, N2 and O2 are free and the emission masses do not depend on it. | medium | open | Either add the hood dilution air as a stream (ASSUMED ratio) so that S7 reaches 600 K, or declare B101's heat loss to ambient as an energy stream to AMB instead of `adiabatic`. Alternatively, state the adiabatic outlet temperature and drop the 600 K. Correct the FG-101 note. |
| 2026-10-28-pfd-lci-review#4 | R-04: DESIGN.md:123, :130, :198; process/reactions.yaml:31 | unaudited cross-check sources | Two cross-checks rest on search-engine summaries with no locator. (1) The IPCC 1996 Norwegian factor of 0.4 t CO per t coke is cited in the COX conversion source and in D-006, with the locator "to confirm". (2) An "IISc hot-model study" reporting about 15 % conversion is quoted in D-006 but appears neither in the source register nor in `process.yaml` `references:` (no author, year or URL). Both are labelled as such and are not inputs, so they do not mislead, but the task requires facts to cite a source with a locator. | low | open | Read IPCC 1996 Reference Manual ch. 2 and give the page or table, or drop the comparison. Give the IISc study a full reference and locator, or remove it. |
| 2026-10-28-pfd-lci-review#5 | R-05: process.yaml:34-45 | maturity / validation notes | `cheme maturity` gives calculation maturity `none` and warns `maturity-claim-exceeds`. `concept` is the lowest value the manifest schema allows (schemas/process.schema.json), and DESIGN.md section 5 states the situation. The `validation.notes` that the Atlas shows do not say it. | low | open | Add one sentence to `validation.notes`: `cheme maturity` supports no level until the feeds, conversions and sorting split are given with sources. |
| 2026-10-28-pfd-lci-review#6 | R-06: process/flowsheet.yaml S8B, S9, S10, S10B; scripts/sic_balance.py | cooling end point | H101 cools the contents to 323 K (Q5 is computed to 323 K). Every outlet of Z101 is then at 298.15 K, with no energy stream on Z101. The sorting step thus cools the material by 25 K for free (about 0.2 MW). The effect is negligible and does not reach the LCI (AMB is free), but a balance-by-step reader sees an inconsistency. | low | open | Set the Z101 outlets to 323.15 K, or compute Q5 down to 298.15 K. |
| 2026-10-28-pfd-lci-review#7 | R-07: runs/20261028-160349-design/report.md ("Two process slips") | working rules | The run report admits two slips. (1) One edit to `flowsheet.yaml` was made with a Python heredoc, which AGENTS.md forbids. I reran the balance script and `cheme process streams`, and the committed file is consistent, so there is no damage to the design. (2) A scratch file `/Users/arturschweidtmann/Developer/test/wt/sc-schema.json` still exists outside the repository. It is not in git and has no effect on the branch. | low | open | Delete the stray file by hand. Future runs should use Edit/Write only. Nothing to change on the branch. |

No critical or high finding. I checked the balance, the LCI, the honesty of the claims and the
licensing, and nothing misleads a reader to the point of a wrong conclusion, provided the
"partial" label is read. R-01 and R-02 are about the presentation of the climate number.

## Previous findings

None. This is the first review record of `processes/silicon-carbide-1/`; `reviews/` held only
README.md.

## Drawing

No P&ID exists. The BFD and PFD are generated by `cheme process build` from the YAML, and
`cheme validate` reports no drawing-rule findings for them (no `drawing <sheet>:` count lines;
the drawing rules apply to P&IDs). I read the PFD in `build/PFD.png` in full. Every step,
stream id, terminal and energy stream is shown and labelled. The automatic layout is not pinned:
S6 (air) and the energy lines Q1/Q3/Q4 run through the PRP and FUR block frames and cross
several streams. That is acceptable for a generated concept PFD, and `cheme process layout
--pin` can tidy it later. I did not read the BFD tile by tile.

## Checked and fine

- **Balances** (hand check plus `streams` plus script). The overall mass is 62919.6 kg/h in and
  out. Each step closes: M101 (9768.6 + 6804.9 + 15000 = 31573.5), R101 (9533.0 + 22040.5),
  B101 (9533.0 + 46346.1 = 55879.1), Z101 (5001 + 1250 + 15789.5), X101 (15000 + 789.5), Z201.
  The element balances and the LCI carbon by origin close to below 0.001 %. Carbon by hand:
  coke fixed C 5818 kg/h = RX1 5423 + RX2 9 + free C in crude 35, metallurgical 75 and purge
  278. Si by hand: 160.2 kmol/h in sand = SiC 150.5 + fume 0.75 + SiO2 in the products and
  purge 8.9.
- **Burn-off stoichiometry.** The air O2 (336.6 kmol/h) is exactly twice the demand of 70 % CO,
  87 % CH4, all S and all SiO (168.3 kmol/h). The S7 O2 fraction 0.0964 follows from that. SO2
  204 kg/h equals 1.5 % S of the coke, one to one. Moisture of 404 kg/h passes to S5.
- **Plausibility against the technology and the cited facts.** Furnace electricity is
  7.5 kWh per kg crude product (crystalline plus metallurgical), which is 7.77 kWh per kg SiC
  formed and 9.63 kWh per kg crude crystalline product before allocation. That sits inside the
  6.3-9.02 kWh/kg of European plants and near Fraunhofer's 7.15 MWh/t. Coke use is 1.13 kg per
  kg SiC formed, against 1.14 implied by the IPCC defaults. The CH4 slip is 11.6 kg/t SiC and
  10.3 kg/t coke, consistent with both IPCC Tier 1 defaults (11.6 kg/t SiC, 10.2 kg/t coke).
  Total gas carbon as CO2 is 2.45 t/t SiC, against IPCC 2.62. Carbon retained in SiC is 29 %
  versus about 35 % in EPA 2009. Sand is 1.62 kg SiO2 per kg SiC formed (stoichiometric 1.50).
  The charge carbon factor is 0.383 (stoichiometric 0.375, Lima and Tenorio 38-39 %). SiC
  formed per charge is 19 %. The specific energy and the slate all sit within the stated
  ranges.
- **Thermochemistry.** The formation enthalpies in `reactions.yaml` (SiO2 quartz -910.9, SiC
  -71.6, CO -110.5, SiO(g) -100.4, CH4 -74.9, CO2 -393.5, SO2 -296.8, H2O(g) -241.8 kJ/mol)
  agree with the NIST-JANAF values as I know them. The heats of reaction follow from them
  arithmetically (RX1 618.3, RX2 700.0, SIOX -810.5 kJ/mol). The furnace energy split in D-004
  (reaction 26.0 MW, contents 11.8 MW, residual 9.1 MW) is reproduced. They are still correctly
  marked ASSUMED until checked against the tables.
- **Sources and ASSUMED marking.** Every stream value has `provenance: assumed` with a decision
  reference. The design basis marks every engineering choice ASSUMED. The source register
  states for each source what was read and what was not (Ullmann's, IPCC 2006 directly).
- **Licensing.** No table, figure or passage of the sources is reproduced. Facts are restated in
  our own words with section or figure locators, and the PFD/BFD are generated from our own
  YAML.
- **LCI.** The LCI is per functional unit (1 kg SIC) with mass allocation 0.80/0.20, and the
  unallocated values are also shown in results.md. It is consistent with the flowsheet: every
  plant value equals the stream or duty value, and the per-kg value equals plant value / 5000
  × 0.8. There are no zero-filled backgrounds and no licensed background values: every
  background is `missing:` with a description of the activity to connect, and every one appears
  in `lca/gaps.csv`. The process overrides (POWER to `electricity-high-voltage`, WASTE to
  `inert-waste-landfill`, both present in the shared `lci/mappings.yaml`) are in the folder's
  `lca/mappings.yaml`. The deliberately unmapped SAND, COKE, SIC and MET are listed there with
  reasons. Excluded pollutants (NOx, H2S/COS, PAH, metals) are declared as an
  `emission_exclusions` entry, not silently 0. The carbon-rich purge (35 wt% C) is flagged in
  the WASTE gap text.
- **process.yaml** is internal, concept, unreviewed. Its notes are candid about assumed yields,
  the specific-energy basis and the unmapped backgrounds (but see R-05).

## Not checked

- I did not read the cited sources (Lima and Tenorio 2011, EPA 2009 TSD, Fraunhofer IKTS 2023)
  against the quoted locators. The figures I compared (IPCC Tier 1 factors, JANAF enthalpies,
  European kWh/kg range) are consistent with general engineering knowledge.
- I did not check the composition of the metallurgical grade (88 wt% SiC) or the 0.25 kg/kg
  slate, the 3.0 kg/kg recycle or the 5 % purge against any Acheson zone data. The author
  states that none was read (D-006, D-007).
- BFD tiles; P&IDs, layout, datasheets and control: none exist, and all are out of scope for
  this concept case.
- I did not check the Atlas build (`build_lci.py`) of this folder's dataset.
