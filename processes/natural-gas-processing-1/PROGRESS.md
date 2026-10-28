# Progress

Newest first. One line per change: date, sheet or file, what, why.

| date | where | what | why |
|---|---|---|---|
| 2026-10-28 | process/flowsheet.yaml (S1, S8, S33), BFD, PFD, DESIGN.md D-015 | feed flows and compositions `given` with their basis (sourced composition, design specifications, ASSUMED parts named) | review R-02; `cheme maturity` now reaches calculation maturity "sourced", supporting the concept claim |
| 2026-10-28 | DESIGN.md D-016, section 5; process.yaml | cold-box refrigeration order-of-magnitude check; electricity caveat (chiller up to about 1.5 MW, up to +40 %) | review R-01 |
| 2026-10-28 | lca/lca.yaml (cutoff, location), lca/* (generated), DESIGN.md D-014, D-017; process.yaml | fugitive methane screening amount (519 t/a, ASSUMED) in `cutoff:`; location US | review R-03, R-05 |
| 2026-10-28 | lca/mappings.yaml, lca/lca.yaml, lca/* (generated) | feed:STEAM uses the shared `steam-heat` entry (kWh); allocation.deviation states why energy, not the price ratio | PR #224 CI: strict Atlas LCI build failed on the steam unit and the allocation hierarchy |
| 2026-10-28 | DESIGN.md, process.yaml, process/design-basis.yaml, PROGRESS.md | route/boundary memo, source register, decisions D-001..D-014, results, gated steps; manifest (internal, concept, unreviewed) and design basis | issue #181 concept stage |
| 2026-10-28 | lca/lca.yaml, lca/mappings.yaml, lca/* (generated) | preliminary gate-to-gate LCI per kg sales gas, energy allocation with the NGL, backgrounds missing, AP-42 1.4 heater emissions; inventory written | D-014 |
| 2026-10-28 | process/flowsheet.yaml (Q13) | demethaniser reboiler heat recorded as internal cold-box integration | boundary check (T401 had no energy stream) |
| 2026-10-28 | process/*.yaml, BFD, PFD, scripts/balance.py, equipment/equipment-list.yaml, plant.yaml | scaffold; sourced feed (Bullin and Krouskop 2009, Barnett well 2); balanced BFD/PFD (6 blocks, 19 steps, 34 material and 13 energy streams); PFD equipment list | D-001..D-013 |

## Responses to review 2026-10-28-pfd-lci-review

The review had no critical or high finding. Re-run after the changes: `cheme validate` 0 errors,
0 warnings; `cheme check` concept and basic process gates pass (pids-exist, design-review,
layout, datasheet and detail gates fail: out of scope, or need a new review); `cheme maturity`
calculation maturity **sourced**, supporting the concept claim (no `maturity-claim-exceeds`);
`cheme process streams` every block and step ok; `cheme assess lca --coverage` partial screening
carbon footprint, 18 gaps, mass balance closed, publishable.

- **CI (PR #224)**: strict Atlas LCI build failed on feed:STEAM (kWh mapped to per-kg `steam`)
  and on energy allocation without a deviation. Fixed: `lca/mappings.yaml` override to
  `steam-heat`, `allocation.deviation` in `lca/lca.yaml`; library tests pass locally (406).
  Commit e99bec1.
- **#1 (R-01, medium) closed**: cold-box refrigeration order-of-magnitude check, D-016 (deficit
  of order 0.3-2 MW, a propane chiller of up to about 1.5 MW electric); caveat in `process.yaml`
  validation notes and the electricity utility note, and in the DESIGN.md section 5
  sensitivity. Commit d0f6bee.
- **#2 (R-02, medium) closed**: S1, S8, S33 flows and compositions `given` with their basis and
  the ASSUMED parts named, D-015; `cheme maturity` passes `sourced-boundary`. Commit d0f6bee.
- **#3 (R-03, medium) closed**: ASSUMED screening amount of fugitive methane (0.1 % of methane
  processed, 519 t/a) in the `cutoff:` list of `lca/lca.yaml`, D-017 (about 0.020 kg CO2-eq per
  kg sales gas, stated in `process.yaml`). Commit d0f6bee.
- **#5 (R-05, low) closed**: `location: US`, LCI outputs regenerated. Commit d0f6bee.
- **#4 (R-04, low) open**: the Bukacek coefficient still needs a primary or handbook check; not
  verifiable from open material in this session.
- **#6 (R-06, low) open**: no open pipeline tariff sourced yet; stays an open input (DESIGN.md
  section 7).
