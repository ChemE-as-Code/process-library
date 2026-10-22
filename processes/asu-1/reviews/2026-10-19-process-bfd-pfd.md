---
topic: process-bfd-pfd
reviewed_commit: acc8766
scope: [process/materials.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, checks/checks.yaml]
reviewer: Claude (plantcode 0.5 integration session)
reviewer_kind: self
date: 2026-10-19
branch: process-bfd-pfd
merge: pending
notes: Record of the BFD/PFD work with plantcode 0.5; a human should approve it before it counts for a sign-off.
---

# Review: BFD, PFD, stream table and properties (plantcode 0.5)

Branch `process-bfd-pfd`, commits be2f92e..acc8766 and the commit adding this record. Self-review by
the agent that integrated plantcode 0.5; not independent.

## What was added

- `process/materials.yaml`: N2, O2, AR, H2O, CO2; templates `air` (with H2O, CO2) and `dry`; the
  property method recorded by `plantcode process props --fill` (Peng-Robinson, ChemSep kij,
  COSTALD liquid density, thermo 0.6.1 / chemicals 1.5.2, validated range N2/O2/Ar 77-315 K).
- `process/flowsheet.yaml`, seeded from DESIGN.md section 3: feeds AIR, products GOXP, GANP, LOX,
  LIN, VENT; blocks MAC, PUR, CB, PRD; 12 steps (K1101 ... K4102) with delegated ports; 24 streams
  with per-value provenance and sources (DESIGN.md 3, D-001, D-004).
- Generated `process/BFD.xml` (4 blocks, 14 streams) and `process/PFD.xml` (12 steps, 24 streams),
  declared in `plant.yaml` as kind `bfd` / `pfd`.
- Links: every block and step to its equipment, every material stream to its line (with sheet
  scope), key streams to instruments (FIC-1101, AIA-2102, FI-4148, FQI-4149, AIA-3105, FIC-4105).
  0 unresolved.
- Gates: `process-links-concept` (warning), `process-balances` (concept: mass balance errors and
  outdated sheets fail), `process-links` and `process-calculated-current` (basic).
- 2026-10-19: CO2-free dry-air composition (ASSUMED) on S4, S5, S5B, S6, so their properties and
  KT3101's component balance are evaluable.

## Balance results (case design, tolerance 1 kg/h + 0.5 %)

| block / step | in kg/h | out kg/h | status |
|---|---|---|---|
| MAC | 129720 | 129720 | ok (components not evaluable) |
| PUR | 114620 | 114620 | ok (components not evaluable) |
| CB | 98000 | 97840 | ok (160 kg/h = 0.16 %; components not evaluable) |
| PRD | 33370 | 33370 | ok |
| K1101, C1101, C1102, V2101, E2101, X3101 | | | ok, mass only |
| KT3101, K4101, K4102 | | | ok, mass and components |
| E3101, C3101, C3102 | | | not evaluable: no flows for S13, S14, S15, S16 |

## Property results (`plantcode process props --fill`)

| stream | phase | M kg/kmol | rho kg/m3 | h kJ/kmol |
|---|---|---|---|---|
| S4 dry air 5.6 bar(a), 15 C | vapor | 28.96 | 6.794 | -339.3 |
| S5 HP column feed 5.5 bar(a), -173 C | vapor | 28.96 | 21.94 | -6024 |
| S6 Lachmann air 1.35 bar(a), -178 C | vapor | 28.96 | 5.112 | -5962 |
| S7 GOX 1.15 bar(a), 25 C | vapor | 32.03 | 1.488 | -10.9 |
| S8 GOX 31 bar(a), 40 C | vapor | 32.03 | 38.95 | 178.9 |
| S9 GAN 5.2 bar(a), 25 C | vapor | 28.01 | 5.890 | -39.7 |
| S9B GAN 9 bar(a), 40 C | vapor | 28.01 | 9.709 | 375.4 |
| S17 waste N2 1.15 bar(a), 25 C | vapor | 28.24 | 1.311 | -8.9 |

Refused, nothing written: S1 (CO2 is outside the supported mixture), S10 and S11 (phase given as
liquid, but vapour at the stated temperature and pressure).

`plantcode validate`: 0 errors; no process warnings (the 72 warnings are the earlier P&ID drawing,
interlock and title-block findings). `plantcode check`: every gate passes.

## Findings and open points

| # | item | finding | severity | proposed action |
|---|---|---|---|---|
| 1 | S10 LOX, S11 LIN | DESIGN.md 3 gives LOX at -180 C / 1.3 bar(a) and LIN at -178 C / 5.2 bar(a): both above saturation (99.5 % O2 at 130 kPa boils near 92.6 K = -180.6 C; N2 at 520 kPa near 94.5 K), so the products would be vapour. | medium | Correct DESIGN.md 3 (e.g. LOX subcooled to about -183 C, LIN to about -180 C, or other pressures), then `props --fill`. |
| 2 | S5 | HP column feed at -173 C / 5.5 bar(a) is vapour, but only a few kelvin above its dew point. | low | Confirm the main exchanger outlet temperature with the cold box vendor. |
| 3 | S13-S16 | Cold-box internal streams have no flows, so E3101, C3101 and C3102 balances are not evaluable. | low | Add flows from the column simulation when available. |
| 4 | S1-S3, S12A-S12E | No composition (S1 has CO2, outside the property method), so component balances of MAC, PUR, CB stay not evaluable. | low | Add assumed compositions if component balances are needed; S1 stays without properties. |
| 5 | BFD | Streams are drawn one per connection; aggregation of parallel streams is not available. | info | Revisit with a later plantcode. |
