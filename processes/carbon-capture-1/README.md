# CO2 conditioning of a high-purity source

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of dense-phase CO2 at 15.3 MPa and 30 degC (99.95 mol% CO2), from the wet CO2 stripper vent of a natural-gas ammonia plant: water knockout, five-stage reciprocating compression with intercooling, triethylene glycol (TEG) drying and aftercooling, with a stand-alone cooling tower. This is the `high-purity` variant of the coverage entry `carbon-capture`. The separation of the CO2 belongs to the ammonia plant; amine post-combustion capture and direct air capture are not covered.

## How it is built

`lca/datasets/co2-conditioning-ammonia-stripper-vent.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance. The source is the ammonia case of the US NETL study *Cost of Capturing CO2 from Industrial Sources* (2023, section 5.1), facts in our own form, each with its exhibit in `parameters`.

| Item | Source | Value per t CO2 |
|---|---|---|
| Raw vent gas | NETL stream table (Exhibit 5-3) and the product's CO2 | 1012 kg (97.09 mol% CO2) |
| Electricity | NETL performance summary (Exhibit 5-4): compressor, circulating-water pumps, cooling-tower fans | 105.6 kWh |
| TEG make-up and spent TEG | NETL O&M (Exhibit 5-7), 312 gal/d; PubChem density | 1.0 kg |
| Cooling-tower make-up | NETL O&M (Exhibit 5-7), 46,000 gal/d | 131 kg |
| Evaporation and blowdown | the make-up split with 4 cycles of concentration (ASSUMED) | 98 and 33 kg |
| Condensate | water of the raw gas less water of the product | 12 kg |

The IPCC 2006 Guidelines set the frame. Volume 3, section 3.2 describes the regenerator off-gas as the stream that goes to urea, a liquid CO2 plant or the air. Volume 2, section 5.3 counts compression and dehydration as part of capture. Neither gives a conditioning energy, and Volume 2 gives no default for fugitive CO2 at the compression plant.

The two mixed streams are written as mole-ratio formulas in `generation.formulas`: `(CO2)9709(H2O)291` for the raw gas and `(CO2)1999H2O` for the product. That is how core's integer formula parser takes the sourced compositions into the element balance.

## Allocation and carbon

The raw gas carries no burden of the ammonia plant. It is the CO2 co-product cut before conditioning (docs/system-model.md section 2, step 4, rule `co2-cutoff`), and this dataset is its separate conditioning. The carbon is fossil and passes through to the product. The dataset gives no capture or avoided-emission credit; whether the CO2 is later emitted (urea use, IPCC 2006 V3 Box 3.2) or stored is the user's system.

## What is weak

- **One design case.** All numbers come from one conceptual cost study, with a vendor quote scaled to a 55.5 t/h US case. They are not measured plant data.
- **No independent benchmark.** Neither KPI has an open reference that states a value: both record `no_open_reference` in `benchmarks/carbon-capture.yaml`. The electricity is close to our own evaluation of the McCollum and Ogden (2006) compression model (104.8 kWh/t, 0.1 to 15 MPa) and to NETL's two 2023 cases (105.6 to 112.7 kWh/t, the dataset's own source). Both are only notes and the uncertainty spread, not a check. NETL's two water figures (131 to 164 kg/t) are likewise only the uncertainty spread.
- **Gaps in the source.** No TEG regenerator heat is stated: the case lists no fuel or steam. Fugitive CO2, CO2 dissolved in the condensate and the treatment chemicals are not stated either. They are TODO exclusions, not zeros.
- **Inlet water.** NETL's stream table gives 2.91 mol% water in the vent gas (above saturation at 21 degC and 0.16 MPa, so partly liquid), but its design inputs say 1 vol%. The dataset uses the stream table; at 1 vol% the condensate would be 3.9 instead of 12.1 kg/t.
- The reading of NETL's water consumable as the cooling-tower make-up, the 4 cycles of concentration and the equal masses of TEG make-up and spent TEG are ASSUMED.
- The delivery state is EOR pipeline pressure. A urea plant takes the CO2 at about 0.16 MPa and compresses it itself, and a merchant user takes it liquefied. Neither is this product.

## Linking

The product names the registry grade `carbon-dioxide/dense-153bara-99.95` (`process.yaml`). No existing process takes this dense-phase product:
- `co2-electrolysis-bpm-1` buys liquefied merchant CO2. Its `feed:CO2` is graded `carbon-dioxide/liquid` (the registry's `flow_grades`), so the build refuses this product for it by grade.
- `urea-1`'s `feed:CO2` is the raw gas at 160 kPa(a), before its own compressor, and `npk-fertilizers-1` and `e-fuels-1` take low-pressure CO2. None of them is linked to this product. Their CO2 stays a reported gap (`npk-fertilizers-1` and `e-fuels-1` by `atlas: false` in their mappings).

The TEG make-up links explicitly to `ethylene-glycol-1`'s `product:TEG` (`lca/mappings.yaml`). The raw vent gas is a reported gap: `ammonia-1` vents this stream and gives no CO2 co-product to link.

## Not counted yet (TODO)

Fugitive CO2, CO2 dissolved in the condensate and in the TEG regenerator vent, TEG regenerator heat, water treatment chemicals, and transport and storage beyond the pipeline inlet. The full list is in the dataset's `system_boundary.excluded`.
