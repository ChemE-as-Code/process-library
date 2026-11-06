# tert-Butanol by direct hydration of isobutene

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of tert-butanol (TBA), from isobutene and water over a strongly acidic ion-exchange resin in continuous fixed-bed reactors, with distillative work-up (issue #155).

## Route

The LVOC BREF (2017, section 2.1.2.1.8, p. 19) names three routes: direct hydration of isobutene, indirect hydration with sulfuric acid, and TBA as the co-product of propylene oxide from isobutane peroxidation (PO/TBA). It gives no figures. This entry models direct hydration. The Oxeno patent US 7,179,948 B2 describes the process: two to four fixed-bed resin reactors in series at 35 to 70 °C, water fed between the stages, and a column that takes the C4 overhead and leaves aqueous TBA as bottoms. It runs continuously, as do the plants in US 4,180,688 A and US 4,307,257 A. PO/TBA is not covered. Its TBA is a co-product, so it belongs with a propylene oxide entry.

## How it is built

`lca/datasets/tert-butanol-isobutene-hydration.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Tier 1 would need sourced electricity and heat, and no open source gives either for this process. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance.

| Item | Source | Standing |
|---|---|---|
| Isobutene, water | stoichiometry C4H8 + H2O -> C4H10O, plus the dimer | 0.7638 t isobutene and 0.2430 t water per t; losses not counted, so a lower view |
| Isobutene dimer | US 4,180,688 A (Nippon Oil, 1979), Example 4: 17.05 kg/h dimer per 2.48 t/h TBA from two 15 m3 reactors in series, 6.9 kg/t | the plant-scale, two-stage example with a C4 raffinate feed (the patent's laboratory Examples 1 and 2 give 0.46 and 1.9 kg/t); taken for a pure isobutene feed (ASSUMED), modelled as C8H16 |
| Electricity | none read | core's Tier 0 default, 333 kWh/t (ASSUMED, a dated site average), TODO |
| Heat | none read | core's Tier 0 default, 556 kWh/t of heat from fossil fuel (ASSUMED, dated), TODO; mapped to natural-gas heat |

The dataset's selectivity is 99.10 mol%. Examples 1 to 4 of US 4,307,257 A (Sumitomo, 1981), a patent the dataset does not use, give 97.3 to 99.8 %, so the value is within that range (`benchmarks/oxygenates.yaml`). No energy KPI has an open reference; the searches are recorded there.

## What is weak

- **The energy figures are defaults, not tert-butanol data.** They are a German site average of 2000, not confirmed in an open copy of their source. Working dilute aqueous TBA up to the azeotrope or to dry TBA can need much more heat. The BREF calls the process endothermic but gives no figure. The hydration itself is exothermic (US 4,180,688 A, Example 3, removes the reaction heat with cooling water), so the heat need is the work-up.
- **Feeds are a lower bound.** Isobutene lost to vents, flare and effluent is a TODO exclusion, because no open figure was found. The same goes for wastewater, make-up water, cooling water and resin replacement.
- **Feed basis.** Industrial plants mostly hydrate the isobutene in a C4 raffinate (US 7,179,948 B2 prefers raffinate I). The other C4s pass through to the overhead. The dataset counts only the isobutene consumed and links it to `isobutene-1`'s high-purity isobutene. US 7,179,948 B2 allows pure isobutene as a feed, but the burden of isobutene in a raffinate is different.
- **Product.** TBA is counted as the substance. The water of a commercial azeotrope grade, and the drying to anhydrous TBA, are not counted.
- The sources are patents of 1979 to 2007. `valid_until` is the reference year + 5, 2012, so it has already lapsed.

## Linking

The product has the new registry slug `tert-butanol` (CAS 75-65-0; identity checked in the `chemicals` package, PubChem and ChEBI). `feed:isobutene` links explicitly to `isobutene-1` (`lca/mappings.yaml`). `feed:heat` uses the shared `heat-natural-gas` entry. The diisobutene residue is a reported gap: it has no registry slug.

## Not counted yet (TODO)

Isobutene losses, wastewater, make-up water, cooling water, resin replacement, drying beyond the azeotrope, the PO/TBA and sulfuric-acid routes. The full list is in the dataset's `system_boundary.excluded`.
