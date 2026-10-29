---
topic: design
reviewed_commit: 7b43268b84322e841b7e6b1d25d2486468d32c47
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, scripts/dmf_balance.py, lca/]
reviewer: review-agent
reviewer_kind: agent
branch: case/dmf-1
merge: pending
basis:
  - {path: process/materials.yaml, revision: 7b43268b84322e841b7e6b1d25d2486468d32c47, relation: depends-on}
  - {path: process/reactions.yaml, revision: 7b43268b84322e841b7e6b1d25d2486468d32c47, relation: depends-on}
  - {path: runs/20261028-150803-design/report.md, revision: 7b43268b84322e841b7e6b1d25d2486468d32c47, relation: depends-on}
---

# Independent review: dmf-1 design basis, balanced BFD/PFD and preliminary gate-to-gate LCI

Issue ChemE-as-Code/process-library#127. An independent agent reviewed the work. It did not
write the design and did not change any design file.

## What was reviewed and how

- `git log --oneline origin/main..HEAD`: 4 commits (d698c25 scaffold, a8f0133 design, 82b3933
  LCI, 7b43268 run record). `git diff --name-only origin/main..HEAD`: every changed file is
  under `processes/dmf-1/`. Nothing outside the folder changed.
- I re-ran these commands myself at 7b43268:
  - `cheme validate`: 0 errors, 2 warnings (`pydexpi_composition_fractions` on S10 in BFD/PFD,
    D-011). There is also one info: `cheme.decision-unknown` D-023, which comes from a template
    comment in `checks/checks.yaml`, not from the design.
  - `cheme check`: every concept gate is ok. The basic and detail gates that fail are the
    expected ones at this stage (no P&ID, no layout, no datasheets, no design review yet).
  - `cheme maturity`: calculation maturity "none", while concept is claimed (warning
    `cheme.maturity-claim-exceeds`). The causes are that the feed flows are not "given with a
    source", the CAT_DEACT conversion is assumed, and the V-102/F-101/C-201/C-202 splits are
    specified values.
  - `cheme process streams`: every block and step balances (RXN, CATR, PUR, and K101 through
    C202).
  - `cheme process propagate --check`: clean.
  - `cheme assess lca --coverage`: partial screening, 11 gaps, each with a description. Mass,
    element and carbon-origin balances are closed. Publishable.
  - `cheme assess lca --check`: the written files are current.
- Hand checks of the balance (my own arithmetic from the stream table):
  - DMA per-pass conversion: 86.51 / 87.82 kmol/h = 98.5 %.
  - DMA:MeOH in the reactor feed: 3959 / 1721 kg/h = 2.30.
  - NaOMe: 29.7 kg/h = 0.75 wt% of the DMA.
  - Methanol balance: 69.3 kg/h in from the catalyst solution. Out: 17.6 consumed by
    CAT_DEACT, 44.4 in the purge, 4.5 in the vent, 2.6 in the cake and 0.2 in the product.
    It closes.
  - Filter cake: 99 % of the formate plus 25 wt% liquor, the liquor at the filtrate's
    DMF/MeOH ratio.
  - Overall mass: in 6547.30 kg/h, out 6547.29 kg/h.
  - Fossil carbon in: 3200.5 kg C/h.
  - CO compressor: about 200 kW for two intercooled stages with η = 0.75.
  - Column duties against latent heat × (1+R) × distillate.
  - Steam: 1.55 GJ/t, plausible beside SRC-4's ~2.5 GJ/t, which also includes trimethylamine
    removal.
  - Vent CO2 after oxidation: about 0.034 kg/kg.
  - Per kg DMF: DMA 0.624 kg against the stoichiometric 0.617; CO 0.407 kg against 0.383.
    These are plausible for this technology.
- The route and boundary match the case notes: one-step DMA + CO on NaOMe in methanol,
  catalyst removal, distillation, with DMA and CO as boundary feeds. The two-step methyl
  formate route is honestly left open (D-001).
- Licences: I found no copied tables, figures or passages. Patent facts are restated with
  example and section locators. No licensed background values: `lca/factors.yaml` has no own
  factors, and every background is a declared `missing:` gap. The per-process overrides
  (steam-heat unit fix only) are in this folder's `lca/mappings.yaml`.

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | scripts/dmf_balance.py:123-128, DESIGN.md:66 (D-005), :121 (D-010) | R-101 cooler duty Q5, `product:CW` | The heat of reaction is taken for DMA(g) + CO(g) -> DMF(l), -109.9 kJ/mol. The fresh DMA is fed as a liquid, though (S1, 500 kPa(a), 298 K, dissolved in methanol in S5/S6), and the script only subtracts sensible feed heating. On a DMA(l) basis (SRC-5's own ΔvapH of 26.0 kJ/mol) the reaction releases about 84 kJ/mol. That makes the cooler about 625 kW lower: about 1800 kW, not 2429 kW (+35 %, outside the stated ±30 %). The cooling-water exchange would be about 0.78 kWh/kg, not 0.881 (-11 %). The "agreement within 3 %" with SRC-1's 27 kcal/mol in D-005 compares against a figure whose reference state the patent does not state. | medium | open | Use DMA(l) (or the actual dissolved state) as the reference state in `DH_R`, or justify the gas basis. Re-run the script, update Q5 and the CW total in `process/flowsheet.yaml`, rewrite the LCA outputs and correct D-005/D-010. |
| 2026-10-28-pfd-lci-review#2 | lca/results.csv:2 | baseline total, climate change | The generated `results.csv` writes `impact` = 0 kg CO2-eq for the baseline total, although every contribution is a gap. `results.md` says "no total", but a machine reader of the CSV gets a zero carbon footprint. This conflicts with the "gaps, never 0" rule of the brief. | medium | open | The file is generated, so do not edit it. Open a core issue so that `cheme assess lca --write` leaves the impact empty (or `n/a`) when no contribution has a burden. Until then, add a sentence to D-012 / `lca/README.md` that `results.csv`'s 0 is "no total", or leave `results.csv` out of the publication. |
| 2026-10-28-pfd-lci-review#3 | scripts/dmf_balance.py:64 | S2 CO feed, S8 vent | `co_feed = xi1 / YIELD_CO` sizes the whole feed gas (CO + N2 + H2), not the CO, at 1/0.95 of the DMF extent. The CO actually converted to DMF is then 86.51 / 90.61 = 95.5 %, not the 95 % cited from SRC-1. As a result the CO feed is about 0.5 % low (0.4074 against 0.4094 kg/kg) and the vent CO about 13 % low. | low | open | `co_feed = xi1 / YIELD_CO / (1 - sum(CO_IMPURITY.values()))`, then re-run and refill S2/S8 and the LCI. |
| 2026-10-28-pfd-lci-review#4 | process.yaml:36 | `maturity: concept` | `cheme maturity` supports no design maturity (warning `cheme.maturity-claim-exceeds`). The claim is the lowest value the schema allows, and the comment plus `validation.notes` say so plainly. The claim is honest, but the warning stays. | low | open | Keep the note. To lift the warning: give the capacity-derived feed flows a source (the design basis as `given` with `source: design-basis`, if the rules allow it), source or justify the CAT_DEACT conversion, and source the separator splits. |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md:22 (SRC-6), process/design-basis.yaml:25 | product specification | The product specification is cited to an Eastman sales specification that was read "via search summary" only. The design basis states the limits as data, with no page or table locator and no note that they are unverified. | low | open | Read the specification sheet and give its locator, or mark the limits as an ASSUMED industrial-grade target that SRC-6 has not verified. |
| 2026-10-28-pfd-lci-review#6 | process/design-basis.yaml:14 | DMA feed purity | "DMA >= 99.5 wt%" has no source and is not marked ASSUMED. Only the < 100 ppm water limit comes from SRC-1. D-004 says the DMA is modelled pure. | low | open | Mark it ASSUMED (or cite a source) and keep it consistent with D-004. |
| 2026-10-28-pfd-lci-review#7 | lca/lca.yaml:19 | data quality TiR | `year: 2026` gives a temporal representativeness of 1.0 (best). The reaction basis, though, comes from 1978-1982 patent examples, and the duties are short-cut estimates. The DQR overstates TiR. | low | open | Record the reference year of the key data (or override TiR with a reason) so that the DQR reflects the age of the data. |
| 2026-10-28-pfd-lci-review#8 | DESIGN.md:109 (D-009) | C-201 bottoms | D-009 justifies vacuum in C-202 by DMF's sensitivity near its normal boiling point with traces of base. Yet C-201 runs at atmospheric pressure with a bottoms temperature of 426 K (S15, 120 kPa(a)) and carries the salt fines and any residual base. The rationale is inconsistent. | low | open | Say why C-201 bottoms at the normal boiling point are acceptable (the catalyst is fully deactivated, short residence), or consider reduced pressure. Carry this to basic engineering. |
| 2026-10-28-pfd-lci-review#9 | process/flowsheet.yaml (S6, S10), DESIGN.md:133 (D-011) | core workarounds | P101 is declared `GeneratingFlow` with S6 copied ASSUMED from S5, and the S10 fractions sum to 1.0000011 (2 validate warnings). Both are documented core defects, not design errors. | low | open | Open or link the core issues (Pumping `step_method`, rounding in propagate), and revert the workaround when core is fixed. |

No critical or high findings. The mass, component and element balances close. The LCI is per
1 kg DMF and consistent with the flowsheet, has no zero-filled or licensed background, and lists
every background as a described gap. Nothing outside `processes/dmf-1/` changed.

Merge: pending. A human or a reviewer other than the author merges `case/dmf-1`. Findings #1
and #2 should be fixed or tracked before the LCI is used for any number.
