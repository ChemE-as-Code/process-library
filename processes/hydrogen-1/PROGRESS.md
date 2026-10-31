# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-30 | process/simulation.yaml, DESIGN.md D-015 | DWSIM inputs for the first simulation. The file holds the PR property package with its `method_selection` facts and a recorded substitution, specs with their sources for the 13 of the 17 simulated steps that need them, the tear S2, and H301, E305 and STM left out with reasons. R201 runs at its adiabatic outlet temperature (core #58), and its duty is the check. **Not run** (no DWSIM or Docker on this machine). Offline checks: `cheme validate` 0 errors; `cheme process simulate --check` translates and stops at `sim-unavailable` (cheme 1.1.0 and 1.2.0); maturity `predictive.simulation-spec` and `property-package` ok; no stream value written; lca/ not regenerated (D-015) | prepare hydrogen-1 for its first DWSIM run |
| 2026-10-27 | lca/lca.yaml, lca/*, scripts/allocation_exergy.py, DESIGN.md D-013 | exergy allocation H2/export steam (H2 90.1 %, 9.11 kg CO2-eq/kg H2 direct, 10.10 unallocated) with `allocation.deviation`; combustion emission estimate H301-firing (CH4, N2O, CO, NOx) | PR #190 CI: the library LCI build refused `allocation: none` for a two-product dataset; review 2026-10-27-pfd-lci-review #1, #2, #6 (commit 54d6397) |

## Responses to review 2026-10-27-pfd-lci-review

- **#1 (medium, allocation / headline): closed in 54d6397.** `lca.yaml` allocates by exergy
  (H2 121 243.5 kJ/kg, steam 1 256.6 kJ/kg, `scripts/allocation_exergy.py`), the deviation
  from the hierarchy stated; `results.md` now headlines 9.11 kg CO2-eq (exergy-allocated) with
  `none` (10.10) and `mass` in the comparison; `lca/README.md` opens with how to read the
  number; D-013 gives the reason. System expansion stays a later substitution variant.
- **#2 (medium, zero-valued combustibles): closed in 54d6397.** `emission_estimates`
  H301-firing (IPCC 2006 Tier 1 CH4/N2O, EMEP/EEA 2019 Tier 1 CO/NOx for natural gas, ASSUMED
  for the tail gas) replaces the zero CH4 and CO and adds N2O and NOx;
  `cheme.lci-emissions-incomplete` is gone. C2H6, C3H8 and H2 remain at the balance's zero (the
  reactor solver writes them), labelled in `lca.yaml` and README as the complete-combustion
  assumption, not a determined value. The CO/NOx guidebook values need checking against the
  table (not re-read in this run).
- **#6 (low, condensate/deaerator vent): closed in 54d6397.** Added to the LCI open items
  (`lca/README.md`) and D-013.
- **#3, #4, #5, #7, #8 (low): left open.** #3 and #7 need library changes outside this
  folder (a maturity level below `concept`; `natural-gas` in `chemicals/chemicals.yaml`); #4 and
  #5 are text/benchmark work for the next stage; #8 needs no action at concept.

## Change log (continued)

| date | where | what | why |
|---|---|---|---|
| 2026-10-27 | lca/ | preliminary gate-to-gate LCI per kg H2 (lca.yaml, inventory.csv, dataset.yaml, gaps.csv, README.md); backgrounds unmapped with the activity each should link to; CO2 split feedstock 8.47 / trim fuel 1.63 kg/kg | scope item 4 of issue #117 (D-013) |
| 2026-10-27 | process/, equipment/, scripts/h2_balance.py, DESIGN.md, process.yaml, plant.yaml | design basis, materials, reactions, catalysts, balanced BFD/PFD (6 blocks, 25 steps, 46 streams), equipment list; D-001 to D-014 | concept stage of issue #117: route, boundary and a closed mass/element balance |
| 2026-10-27 | (all) | scaffold from `cheme init` and the process.yaml template | start of hydrogen-1 |
