---
topic: design
reviewed_commit: 7bd5670ccd8131bc8182c17d64b939997bcdda81
scope: [DESIGN.md, PROGRESS.md, process.yaml, checks/checks.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/reactions.yaml, process/reaction-evidence.yaml, process/simulation.yaml, process/simulation-run.json, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, estimate/, lca/, layout/equipment-placement.yaml, layout/plant-model.yaml, scripts/hda_balance.py, scripts/concept_sizing.py, scripts/purge_h2_recovery.py]
reviewer: review-agent
reviewer_kind: agent
branch: stage/hda-1-basic-simulation
merge: pending
---
# Review: design (simulation close-out of hda-1, S2, PR #326, re-review round 1)

Independent re-review of PR #326 (issue #302) at 7bd5670, after the fix commits 39cbca70,
76dd9487 and 7bd5670c that answer the panel's round-1 findings. The panel's findings had no
record of their own, so they are listed here as #1 to #17 with their resolution. Re-run by the
reviewer with core v1.4.1 at 7bd5670:

- `cheme validate`: 25 files, 0 errors, 5 warnings. All five are `pydexpi_composition_fractions`
  (S19 in the BFD and PFD; S20, S22 and S26 in the PFD), the shortcut-column sums of #18.
- `cheme check`: every concept gate passes, and so do process-basic, process-links, pids-valid,
  drawing-clean and **maturity-balanced** (now enabled in checks/checks.yaml). The failing basic
  and detail gates (pids-exist, design-review, layout-3d, lifting-study, mto, layout-review,
  electrical, datasheets) belong to later sections of runs/plan.md; design-review is answered by
  this record.
- `cheme maturity`: **calculation maturity balanced** (claim concept). Predictive fails on
  three requirements, each documented in D-021: `predictive.model-basis` (R101 is a specified
  conversion: no readable thermal HDA kinetics with units and range, and core has no homogeneous
  kinetic reactor), `predictive.property-regime` (core#315: Peng-Robinson not benchmarked for
  aromatics with H2/CH4) and `predictive.formation-data` (DWSIM's own formation data in R101B,
  0.79 kW against a 0.1 kW tolerance). The R101 conversion is "own source kept, not supported by
  the evidence": reaction-evidence O1 is recorded at its true derived pressure (4238 kPa(a)) and
  so does not match R-101. That is an honest record, not a relaxed gate.
- `cheme assess lca --balance`: matches the regenerated LCI summary (mass 15988.9 in,
  15989.6 kg/h out; C and H closed).
- `scripts/purge_h2_recovery.py` re-run: 184.0 kg/h recovered, net 1.874 MEUR/a before
  capital-related cost, incremental NPV +9.73 / +2.85 MEUR at 3.5 / 9.5 MEUR, break-even
  11.98 MEUR. The tail-gas compressor power (245 kW for 177 kmol/h from 130 to 450 kPa(a),
  k 1.3, efficiency 0.75) was recomputed by hand and holds.
- TEA selectivity scenarios: the scale factors were recomputed (net benzene 166.83 - 2 x 2.215
  = 162.40 kmol/h; 162.40 / 0.945 = 171.85; +5.02 kmol/h toluene = +462.6 kg/h, x 1.030;
  +10.1 kg/h H2, x 1.018). They hold. The credited case's 2.112 is 2.114 by hand, a rounding
  without effect.
- core#130 (shortcut-column fractions) and core#58 (DWSIM adiabatic equilibrium reactor) exist
  and are open.
- CI on the PR was pending at the time of review; Linux CI is the judge of fmt and goldens.

Verdict: **approve**. No critical or high finding is open. The section's target holds:
calculation maturity is balanced and the gate maturity-balanced passes, and each requirement
that keeps the plant below predictive is documented with its core or simulator limit. The open
findings below are low.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-11-03-simulation-closeout#1 | DESIGN.md D-023 | I-07 PSA test | Panel (engineering): D-023 compared the PSA's gross benefit with the plant's LCOP gap; no capex or power; product recompression overstated. Now decided on the incremental test (`scripts/purge_h2_recovery.py`): power 257 kW (mostly the tail-gas compressor), tail-gas compressor capital from the package correlation, PSA package ASSUMED 2 to 8 MEUR with its reason (no readable correlation reached, sources tried listed), NPV +2.9 to +9.7 MEUR, break-even 12.0 MEUR. Recompression dropped and the boost quantified (2.8 kW). The PSA is recommended and I-07 stays open for the flowsheet change before S3, which the fix allowed. Re-run by the reviewer. | medium | closed 76dd9487 | - |
| 2026-11-03-simulation-closeout#2 | process/reactions.yaml, D-021, design-basis.yaml | selectivity bound | Panel (engineering): the equilibrium bounds the biphenyl make only. Now stated in D-021, design-basis.yaml, reactions.yaml and the evidence table; US 3,607,960 Example 1 (94.5 % at 85 % per pass, about 460 psig) recorded as reaction-evidence O2 with its locator and its higher conversion; TEA scenarios selectivity-0945 (902.9 EUR/t) and selectivity-0945-credited (884.7 EUR/t). Factors checked. | medium | closed 39cbca70 | - |
| 2026-11-03-simulation-closeout#3 | process/simulation.yaml, D-022 | energy audit includes R101B | Panel (engineering): D-022, the method table and process.yaml now state that the closure includes R101B's unterminated 17.4 kW, a model artefact; the warning is kept and the DWSIM limit tracked as core#58. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#4 | DESIGN.md D-022 | utility totals | Panel (engineering): both the raw run totals (hot 8320.3, cold 10229.3 kW) and the economics' totals (8449.6, 10360.4 kW) are given, with the C-201 and R101B differences; the arithmetic holds. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#5 | DESIGN.md LCI summary | stale LCI table | Panel (engineering): regenerated from the S2 inventory; per-kg values (1.23458, 0.044526, 0.02816, 0.251011) and the balance (15988.9/15989.6 kg/h) agree with the reviewer's `--balance` run. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#6 | process/flowsheet.yaml, D-022 | S26 benzene 99.899 mol% | Panel (engineering): the deviation is recorded in D-022 and in S21's source, not normalised by hand (the fix's first option). The margin rerun is left to the next C-202 rerun. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#7 | DESIGN.md LCI summary | 95/5 label | Panel (provenance): same table as #5; H2MU now labelled PSA grade 99.9/0.1 mol% (D-020). | low | superseded by 2026-11-03-simulation-closeout#5 | - |
| 2026-11-03-simulation-closeout#8 | lca/lca.yaml | flow sources | Panel (provenance): feed:POWER names P-102/Q12, product:CW names E-207/Q11, feed:TOLF cites D-020; the small-pumps cut-off no longer counts P-102. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#9 | process/flowsheet.yaml, D-020 | `given` flows on ASSUMED capacity | Panel (provenance): both source strings and D-020 say the capacity (I-04) and loop specifications (D-007) are ASSUMED and name it as a known limit of the sourced-boundary basis. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#10 | process/reactions.yaml | conversion transfer; "i.e." | Panel (provenance): the conversion source says it is adopted as R-101's design value with volume and residence time not designed to it; BIPH reversibility is worded "consistent with", as this design's inference. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#11 | DESIGN.md D-023 | H2 LHV | Panel (provenance): own calculation from the CODATA H2O(g) formation enthalpy (241.826 / 2.01588 = 119.96 MJ/kg), in D-023 and the script. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#12 | process.yaml | stale catalog text | Panel (integrity): the comment and validation.notes describe the S2 state (balanced reached; predictive fails on model-basis, property-regime, formation-data; D-020 feeds; D-021 reactor; optimistic selectivity); the Douglas wording is gone. See #20 for two small leftovers. | medium | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#13 | process/simulation.yaml, process/reactions.yaml | R101B isothermal; tracked item | Panel (integrity): the isothermal-against-adiabatic difference is stated in simulation.yaml, reactions.yaml and the script docstring; the failure was reproduced on core v1.4.1 with the exact error text in D-021 and is tracked as core#58 (open). See #19 for a wording error introduced by this fix. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#14 | process/design-basis.yaml | biphenyl purity | Panel (integrity): the purity line points to the 4.9 mol% toluene deviation of D-022, target unchanged. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#15 | DESIGN.md D-022 | #17 not reported as a core limit | Panel (integrity): reported as core#130 (open, with the observed sums and a reproducer), referenced in D-022, process.yaml and PROGRESS.md. The remaining warnings are #18. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#16 | process/reactions.yaml, D-021 | reactor configuration | Panel (integrity): the staged gas quench of the patent against R-101's single adiabatic vessel is in the conversion source, D-021 and reaction-evidence O1. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#17 | DESIGN.md D-022 | residual sign | Panel (integrity): quoted as printed, +0.833 kW. | low | closed 7bd5670c | - |
| 2026-11-03-simulation-closeout#18 | process/PFD.xml, process/BFD.xml | composition sums | The maturity part of 2026-11-03-concept-closeout#17 is done (balanced). What remains: S19, S20, S22 and S26 miss 1 by up to 1.7e-4 (`cheme validate`, 5 warnings). They are DWSIM shortcut-column output passed through by `simulate --fill`; not normalised by hand, which is right. Cause reported as core#130 (open). | low | open | rerun with rigorous C-201/C-202 models or a core fix of core#130; do not normalise by hand |
| 2026-11-03-simulation-closeout#19 | process/reactions.yaml:7-9 | R101B wording | New in the fix: the header says the isothermal R101B gives "about 0.4 K and slightly less biphenyl than the adiabatic outlet". BIPH is endothermic (+15.04 MJ/kmol), so the adiabatic outlet would be about 0.4 K cooler and give slightly less biphenyl; the isothermal model gives slightly more. The same line says "open item process-library issue", while D-021 tracks the limit as core#58. | low | open | reword to "slightly more biphenyl than an adiabatic outlet would give" and cite core#58 |
| 2026-11-03-simulation-closeout#20 | process.yaml | catalog leftovers | The description still says "benzene (99.9 mol%)" without noting the narrow miss of D-022 (99.899 mol% normalised), and the chemistry electricity note names only the recycle compressor and toluene pump, not the quench pump P-102 (Q12, D-022). Both are small; the catalog text is public. | low | open | add "(target; simulated 99.899 mol%, D-022)" and P-102 to the electricity note |

## Previous findings
| id | finding | severity | status | evidence |
|---|---|---|---|---|
| 2026-10-27-pfd-lci-review#4 | Douglas reactor-basis values recalled, not read | medium | closed ef36c348 | D-021: no model value rests on Douglas any more; conversion 0.75 from US 3,291,849 (verified at its locator by the panel), window from US 3,291,849 and US 3,607,960, biphenyl by equilibrium on the given formation data; what no readable source covers is stated (the Douglas book, Speight's range, the selectivity at R-101's conversion). I-06 answered. |
| 2026-10-27-pfd-lci-review#9 | fuel-gas credit methods side by side | low | open | carried (I-11): needs linked LCA backgrounds, the LCA practitioner's decision |
| 2026-11-03-concept-closeout#5 | H-101 bare-module factor 2.5 without a read source | low | open | carried to the class 4 estimate (S5); core#129 |
| 2026-11-03-concept-closeout#16 | EUA price from a secondary report | low | open | carried to the next TEA revision |
| 2026-11-03-concept-closeout#18 | ammonia-1 attributes the ISO 6976 methane value to NIST | low | open | outside this PR (processes/ammonia-1); tracked as process-library#321 |
| 2026-11-03-concept-closeout#17 | maturity and composition sums | low | superseded by 2026-11-03-simulation-closeout#18 | maturity part done: calculation maturity balanced, gate maturity-balanced passes (D-020, D-021); the composition sums remain as #18 (core#130) |
