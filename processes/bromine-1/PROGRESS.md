# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | lca/mappings.yaml, scripts/balance.py, process/flowsheet.yaml (S17), BFD, PFD, DESIGN.md (D-001, D-004, D-006, D-009, D-011, sections 5 and 8), process.yaml, equipment list (T-107), lca/ outputs | revision after the review 2026-10-28-pfd-lci-review: CI fix (feed:LPS kept out of the Atlas link), R-01, R-02, R-03, R-05 closed (see Responses below) | PR #232 CI failure; independent review |
| 2026-10-28 | DESIGN.md, process/design-basis.yaml, process.yaml | route/boundary memo, source register, reaction and model evidence, decisions D-001..D-013, checks against the sources, gated steps, open inputs; design basis; Atlas manifest (internal, concept, unreviewed) | issue #136 scope: design basis and honest maturity |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, process/simulation.yaml | preliminary gate-to-gate LCI per kg Br2, every background a gap with its target activity; inventory written (mass and element balance closed); C101/T107 adiabatic (live steam heating) | issue #136 scope item 4 |
| 2026-10-28 | process/*.yaml, scripts/balance.py, BFD, PFD, equipment list | balanced concept flowsheet: steaming-out of a Smackover-type brine, condensation, separation, chlorine stripping, H2SO4 drying, lime neutralisation; 3 750 kg/h Br2 | issue #136 scope items 2-3 |
| 2026-10-28 | all | scaffold from cheme init and the process template | start of the case |

## Responses to review 2026-10-28-pfd-lci-review

- **CI (PR #232, library tooling tests)**: the strict Atlas build warned "feed:LPS: several
  Atlas producers" (ammonia-1, hydrogen-1, utility-steam-ng-boiler). `lca/mappings.yaml` now
  gives feed:LPS `atlas: false` with the reason: no LP steam grade and no chosen site boiler.
  The bromine-1 warning is gone from the local build. Commit 8971013.
- **2026-10-28-pfd-lci-review#1 (R-01, medium), closed**: T-107 is a closed tank at
  120 kPa(a), above the brine's boiling pressure, so there is no flash. `scripts/balance.py` now
  computes S17 from S15 plus the lime neutralisation heat: 128.4 kJ/mol from the NBS formation
  enthalpies, 225 kW net, +0.30 K, giving 382.89 K instead of the unsourced 375 K. Recorded in
  D-009. Commit f8e4bda.
- **2026-10-28-pfd-lci-review#2 (R-02, medium), closed**: S17 now leaves at the T-107 pressure,
  120 kPa(a), instead of 300 kPa(a). The transfer pump to the injection header is part of the
  reinjection system outside the boundary: D-001, D-009, D-011 (with its 50-60 kW and the
  0.047 kWh/kg it would give), the `product:TAILB` gap text and the T-107 notes. Commit f8e4bda.
- **2026-10-28-pfd-lci-review#3 (R-03, medium), closed**: `validation.notes` in process.yaml
  now states the calculation maturity none and that the concept claim exceeds the evidence.
  DESIGN.md section 5 is corrected, and section 8 lists a lower manifest level as a library
  item. Commit 9740287. The LCI dataset and manifest hashes were refreshed in the commit that
  adds these responses.
- **2026-10-28-pfd-lci-review#5 (R-05, low), closed**: D-004 now gives the derived Na
  (85.5 g/kg; 5.36 mol NaCl and 1.08 mol CaCl2 per kg water) and the possible nearness to
  halite saturation (O-1, O-2). D-006 gives the steam sensitivity to the brine cp: 0.21 kg/kg
  Br2 per 0.1 kJ/kg K. Commit 4c4fa45.
- **2026-10-28-pfd-lci-review#4 (R-04, low), left open**: it needs the NBS tables re-read with
  table and entry locators (O-5). No copy of the source was available in this run, and a locator
  given without re-reading would be invented.
- **2026-10-28-pfd-lci-review#6 (R-06, low), left open**: the vent, leak and non-routine
  amounts need the vent scrubber and the P&IDs, and any number given now would be a guess
  without a basis. The bromine resource exchange waits for a brine-extraction background
  (section 8).
