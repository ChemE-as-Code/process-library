# Cumene by zeolite alkylation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of cumene, from benzene and propylene on zeolite with transalkylation.

## How it is built

`lca/datasets/cumene-zeolite-alkylation.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Tier 1 needs yield, electricity and heat each from a source; here electricity has none and the heat is one licensor's net figure. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance.

| Item | Source | Standing |
|---|---|---|
| Benzene, net steam | Versalis licensing brochure (2018), PDF p. 3 | a licensor's figures, not verified plant data |
| Propylene | stoichiometry with the benzene | 0.3519 t/t, which rounds to the brochure's 0.352 |
| Benzene, propylene and cumene to air | US EPA dataset, doi:10.23719/1503030, sheet "Cumene - Allocated" | facility-level reporting for the US in 2011, 8 facilities reporting production and 7 or 8 per flow; the file calls itself demonstrative and not fully vetted |
| Electricity | none read | core's Tier 0 default, 333 kWh/t (ASSUMED, dated site average, not specific to cumene), with a TODO |
| Heavy ends | closes the balance | modelled as triisopropylbenzene (ASSUMED) |

The LVOC BREF does not treat cumene as an illustrative process. Its section 2.1.1.5 is an outline with a 99 % yield for zeolites and no utility data. The dataset's overall yield is 99.7 %, the licensor's figure, so it sits above the BREF's value (`benchmarks/aromatics.yaml`).

## What is weak

- **The net steam of 0.2 t/t is not a cut-off value.** It is HP import less LP export, so it embeds a credit for exported steam, which docs/system-model.md section 2 does not allow. This is a recorded deviation (dataset `modelling`): gross import and export are not stated, so it cannot be corrected. The brochure says a downstream phenol plant uses the export, and the pressures are not stated.
- **Energy may be understated.** The EPA sheet's fuel inputs add up to about 2.5 MJ per kg of cumene, while 0.2 t of steam is far less. The EPA total is facility-wide and is not used here, so neither figure confirms the other.
- The emissions come from sites that also report phenol-chain substances, so they are not this process alone. The dataset uses the workbook's "Allocated" sheet (process allocation by metadata). Its "Baseline" sheet, without allocation, gives 4.3e-06 benzene, 5.9e-06 propylene and 1.0e-05 cumene kg/kg, against 5.9e-06, 7.8e-06 and 1.9e-05 used here.
- Benzene and steam are a licensor's figures, not verified plant data. `valid_until` is the reference year + 5, 2023, so it has already lapsed.

## Linking

The product has the registry slug `cumene`. `acetone-1` buys cumene but does not link to this dataset yet: its exchange `feed:CUM` names no slug, so it stays a reported gap until its own `lca/mappings.yaml` names this dataset.

## Not counted yet (TODO)

Oily water and vacuum vents, catalyst, other facility releases, fuel beyond the steam, propane in the feed, the SPA and AlCl3 routes. The full list is in the dataset's `system_boundary.excluded`.
