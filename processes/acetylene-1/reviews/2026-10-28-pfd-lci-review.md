---
topic: design
reviewed_commit: 3e163e7f39afb312e9d00f0e2bea1898e181e3bb
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/materials.yaml, process/reactions.yaml, process/simulation.yaml, lca/, scripts/balance.py]
reviewer: review-agent
reviewer_kind: agent
branch: case/acetylene-1
merge: pending
---

# Independent review: acetylene-1 concept PFD and preliminary LCI (issue #184)

Scope: the concept case on `case/acetylene-1` (8 commits, `4807eb6..3e163e7`): design basis,
balanced BFD/PFD, burner and separator model, utilities, preliminary gate-to-gate LCI, Atlas
manifest. The design agent's run report (`runs/20261028-153534-design/report.md`) was read and
used only as a claim to check. I re-ran every number quoted below myself. I made no design
changes.

## What was re-run (at 3e163e7)

| command | result |
|---|---|
| `cheme validate` | 17 files, 0 errors, 0 warnings (infos only: `dexpi.load` cycles, a D-023 citation inside a commented example in `checks/checks.yaml`) |
| `cheme check` | every applicable concept gate passes (design basis, lists, process concept, balances, links, ASSUMED marking); `layout-plot-plan` fails (layout is out of scope for this case); the basic and detail gates fail as expected (no P&IDs, layout or datasheets); `design-review` fails until this record exists |
| `cheme maturity` | calculation maturity **none**; `cheme.maturity-claim-exceeds` warns on `maturity: concept` (feeds assumed, conversions and splits specified without a source, no simulation run) |
| `cheme process streams` | every block (PRE, REACT, SOOT, COMP, REC) and every step `ok` |
| `cheme process propagate --check` | no output: nothing stale, nothing to fill |
| `cheme assess lca --coverage` | partial screening carbon footprint, 15 gaps (10 unmapped backgrounds, each with a description of the activity it should link to; 5 emissions outside IPCC GWP100); boundary check clean; mass, element and carbon-origin balances closed; publishable |
| `cheme assess lca --check` | inventory, results, gaps, dataset and manifest current with `lca.yaml` |
| `git diff --name-only origin/main..HEAD` | every changed path is under `processes/acetylene-1/`; nothing in the library root changed |

## Hand checks (my own arithmetic from the stream table)

- **Route and boundary**: natural-gas partial oxidation with O2 in a BASF burner, water quench,
  soot removal, compression, NMP wash, synthesis-gas co-product. This matches issue #184 (water
  quench fixed by the issue). The rejected routes and the out-of-boundary items (ASU, syngas
  conditioning, acetylene compression and storage) are stated in D-001.
- **Feeds**: O2/NG = 1094 / 1818 kmol/h = 0.602; O/C = 1.23. Both are inside the US5824834A
  ranges quoted in D-005.
- **Burner**: soot 24.1 kmol/h C = 290 kg/h, which is 6377 kg/h C2H2 / 22 (the sourced ratio).
  The dry gas after the cooling column (S8) recomputes to H2 56.0, CO 26.0, C2H2 7.46, CH4 5.0,
  CO2 3.5 and higher hydrocarbons 1.0 vol%: this is the US8975460B2 composition the model is
  fitted to.
- **Recovery**: product 240.0 kmol/h C2H2 out of 244.9 kmol/h formed, i.e. 98.0 %. The
  absorber feed's C2H2 partial pressure is 0.0852 x 10.9 bar = 0.93 bar, below the 1.4 bar of
  US10059640B2. The solvent loading is about 19.4 Nm3/m3 (stated 20).
- **Water**: water entering the circuit (reaction water 20.0 t/h, less 3.0 t/h leaving with S9,
  plus 2.6 t/h condensate) equals water leaving (purge 17.0 t/h plus 2.6 t/h in the sludge).
  The gas leaving the quench and the cooling column is water-saturated at 353 K and 308 K.
- **Duties**:
  - E-101 heat: 472 kg/s x 4.18 x 46 K is about 91 MW; the flowsheet uses 91.6 MW.
  - Quench energy: the water takes up about 77 MW (liquid heating plus 18.6 t/h evaporated). Cooling the gas from 1970 K to 353 K releases about 70-78 MW. Consistent within the Cp uncertainty.
  - Preheats: 8.26 kg/s CH4 heated by 570 K at a mean Cp of about 3.1 kJ/(kg K) is about 14.6 MW. The oxygen preheat is about 5.5 MW.
  - Compressor: 3 stages, ratio 2.19 per stage, k about 1.38, efficiency 0.78. This gives about 8.6-9.0 MW electric and a discharge of about 407 K; the flowsheet has 8.83 MW and 404.5 K.
  - E-302: the solvent's sensible heat (7.5 MW) plus the heat of absorption (about 2 MW) is about 9.6 MW, as `balance.py` computes.
- **Fired heater**:
  - Off-gas LHV: C4H2 22.85 kmol/h x 2288 kJ/mol is about 14.6 MW and C6H6 about 8.5 MW. With the C2H2 in the off-gas and the flash gas, the total is about 24.4 MW, as D-011 states.
  - Combustion air: 241.8 kmol/h O2, which is 1.15 x the stoichiometric demand.
  - Flue-gas CO2: about 170 kmol/h, i.e. 7.5 t/h = 1.20 kg per kg of product.
- **Allocation**: the LHVs recompute to 22.53 MJ/kg for the syngas and 83.8 MW for the
  acetylene against 226.3 MW for the syngas, i.e. a 27.0 % share for acetylene.
- **Plausibility against general knowledge of the BASF process**:
  - Consumptions of about 6.5 Nm3 natural gas, 3.9 Nm3 O2 and 10.7 Nm3 syngas per kg C2H2.
  - Carbon yield to acetylene of about 27 %.
  - Soot of about 46 g/kg.
  - Syngas H2/CO of about 2.

  All are in the expected range for the technology. The natural-gas and O2 figures sit at the
  high end (see R-01).
- **LCI**:
  - Per functional unit: 1 kg of stream S18. It traces to the flowsheet stream by stream.
  - Unallocated mass balance per FU: inputs 15.659 kg, outputs 15.658 kg.
  - Completeness: no zero-filled exchange and no licensed background value. Every unmapped background is a `missing:` gap with a description.
  - Overrides: the one per-process override (`feed:STEAM` to `steam-heat`) sits in the folder's `lca/mappings.yaml`, with its reason.
  - Sources: every flow cites its stream and decision.
- **Sources and licences**:
  - The source register in DESIGN.md states for each source what was read and what was not. Ullmann and Zhang 2022 are cited as "not read, no value used".
  - The values taken from the patents are facts, restated in our own words, with locators (example, claim, table).
  - Nothing third-party was copied: no figures, drawings or passages. The tables in DESIGN.md are the design's own.
  - I did not re-open the patents online: the patent facts (for example the 22 kg/kg soot ratio, the 99.31 % depletion) were checked for internal consistency only.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:88-91; process.yaml:44-48 | specific consumption | **R-01** D-005 compares 6.52 Nm3 NG, 3.92 Nm3 O2 and 10.7 Nm3 syngas per kg with about 5.2, 3.1 and 9.1 derived from US5824834A comparative example 1. It says the basis "needs 13 % more gas per acetylene; consistent in direction". The actual differences are +25 % NG, +26 % O2 and +18 % syngas. The 7.5 vs 8.5 vol% C2H2 explains about 13 % and the 98 % recovery about 2 %, so roughly 8-10 % stays unexplained. Natural gas and oxygen are the two largest LCI inputs, and process.yaml's validation notes say the ratios "agree" with the patents | medium | open | state the full deviation per quantity in D-005, attribute the explained part (C2H2 content, recovery) and carry the remainder into the open source audit (S-5, S-6); qualify "agree" in process.yaml `validation.notes` accordingly |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml:114-117 | R-101 emissions | **R-02** `cheme assess lca --coverage` warns `cheme.lci-emissions-incomplete [R-101]`: the burner is typed as a combustion furnace and has neither an emission estimate nor a declared exclusion. All its products leave in the cracked gas (S6) and nothing goes to air in normal operation, but the inventory does not say so | low | open | add an `emission_exclusions` entry for R-101 (method combustion, reason: no direct air emission, all combustion products in S6 and accounted downstream; start-up and trip venting out of scope) |
| 2026-10-28-pfd-lci-review#3 | scripts/balance.py:316-317; DESIGN.md:176-178 | T-303 / T-304 duties | **R-03** The T-303 duty (1.67 MW) covers only desorption, yet the semi-lean solvent S19 leaves T-303 at 418 K, 15 K above its feed S25 (403 K). That is about 2.9 MW of sensible heat T-303 does not supply. The T-304 heat is computed from 403 K instead of 418 K, which over-states it by the same amount. The total steam plus convection heat (9.7 MW) is right; the split between the two columns and their stream temperatures is inconsistent | low | open | either take T-304's sensible heat from S19's 418 K and add the 403 to 418 K heating to T-303, or set S19 to 403 K; update D-012 |
| 2026-10-28-pfd-lci-review#4 | scripts/balance.py:325 | solvent pump power | **R-04** `p_solv` counts only the lean-solvent pump (to 11 bar). The rich solvent also needs pumping, from T-302 (130 kPa) to E-301/T-303 (800 kPa, S17 to S25), about 63 kW hydraulic, about 0.09 MW electric. The electricity is under-stated by about 1 % | low | open | add the rich-solvent pump to Q2 (or state it as an omission in D-012) |
| 2026-10-28-pfd-lci-review#5 | process.yaml:36-54 | maturity claim | **R-05** `maturity: concept` is the lowest value the schema allows, so the claim is as low as it can be. But `cheme maturity` reports calculation maturity none and `cheme.maturity-claim-exceeds`. DESIGN.md says so; the Atlas manifest's `validation.notes` does not, and only the manifest reaches Atlas readers | low | open | add one sentence to `validation.notes`: calculation maturity none per `cheme maturity` (feeds assumed, conversions and splits specified without a source, no simulation run) |
| 2026-10-28-pfd-lci-review#6 | process/design-basis.yaml:30, 51 | references, wording | **R-06** The synthesis-gas note cites D-009, but the syngas decision is D-008. Assumption line 51 reads "reaches the product to product" | low | open | cite D-008; delete the duplicated words |
| 2026-10-28-pfd-lci-review#7 | lca/inventory.csv; lca/README.md | allocated per-kg table | **R-07** `inventory.csv` and `results.md` list inputs, wastes and emissions energy-allocated (27.0 %, e.g. NG 1.278 kg/kg), next to the co-product syngas at its unallocated 5.757 kg. As printed, the per-FU table does not balance by mass, and a reader can take 1.28 kg NG/kg as the plant's consumption (the unallocated figure is 4.73). D-013 explains this, but the lca folder does not | low | open | state in `lca/README.md` (and in the D-013 pointer to the files) that the per-kg quantities are allocated, and name where the unallocated per-kg values are (D-013, `dataset.yaml` per hour) |

No critical or high finding. The balances close, the LCI is consistent with the flowsheet and
leaves no unmapped background without a described gap, and every key value is either sourced or
marked ASSUMED.

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: this is the first review of acetylene-1.

## Not reviewed
- P&IDs, layout, datasheets, control and safety files: they do not exist yet or are template
  stubs at this stage.
- The patent facts were not re-read at their sources (see above). The source audit of Ullmann
  (S-5) and Zhang 2022 (S-6) is an open item in DESIGN.md, not a review finding.
