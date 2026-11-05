# Gas oil hydrodesulfurisation to ultra-low-sulfur diesel

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of desulfurised gas oil (diesel blendstock at about 10 mg/kg S), from straight-run gas oil and hydrogen over a fixed-bed CoMo/alumina catalyst.

## Why this route

Hydrotreating covers many units: naphtha, kerosene, gas oil, FCC feed and residue. This entry takes the distillate (gas oil) hydrodesulfuriser, because diesel sulfur limits make it a unit every EU refinery runs, and the REF BREF gives its utilities as a separate row. It is a continuous fixed-bed unit with recycle gas. Catalyst is changed or regenerated off site every year or so, which is maintenance, not batch operation (REF BREF sections 2.13 and 3.13.1). Naphtha, FCC feed and residue hydrotreating are not covered.

## How it is built

`lca/datasets/gas-oil-hydrodesulfurisation.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H, O and S balance. The sources are the REF BREF (Barthe et al. 2015, sections 2.13 and 3.13.1), the Johan Sverdrup crude assay that `refinery-distillation-1` uses, Tian et al. (2022, Processes 10:2055, CC BY), PRELIM v1.0 (Table 8) and IPCC 2006 Vol. 2, chapter 1. Facts are recorded in our own form, each with its table in `parameters`.

- **Model formulas.** Gas oil is a mixture, so the feed and product are lumped into one formula each, C470H848S and C470H897. Both are ASSUMED. The feed formula gives 0.49 wt-% S, the assay's 230 to 375 degC gas oil cut, the nearest the sheet gives to the linked crude unit's 240 to 360 degC gas oil. The product carries 13.8 wt-% H, PRELIM's hydrogen content of hydrotreated diesel, and its carbon fraction, 0.862, lies within IPCC's gas/diesel oil range. The model reaction takes 25.5 H2 per formula unit: 7.87 kg H2 per t feed (see Hydrogen). All the feed sulfur leaves as H2S, 5.2 kg per t product.
- **Hydrogen** is the make-up hydrogen of one operating diesel hydrotreater to 40 mg/kg S, 7.9 kg per t feed (Tian et al. 2022, Tables 2 and 3, our conversion). That unit's main feed carries 1.49 wt-% S, and it also treats a 2.6 wt-% S stream and naphtha-range feed, so for this straight-run feed it is an upper view. The BREF's typical 0.3 % H2 on feed for distillates (3 kg/t, data of 1991 and 1999) is a lower view for 10 mg/kg diesel. All make-up hydrogen counts as consumed. Hydrogen links to `hydrogen-1` (`lca/mappings.yaml`).
- **Utilities** come from Table 3.63, distillate row, per t feed: electricity is the midpoint (15 kWh/t), steam the midpoint (105 kg/t, by mass) and cooling water the midpoint (2.5 m3/t at 10 K, about 29 kWh/t of heat rejected). Wash water is the midpoint (35 kg/t), and sour water is set equal to it. The steam is counted outside the element balance; as the sourced sour water is less than the steam, the steam is taken to return as condensate (ASSUMED). Catalyst use is 46 t/Mt (Table 3.64).
- **Fuel** is the midpoint of Table 3.63, 400 MJ/t, like the other utilities. The fuel is burnt as methane, which gives CO2 stoichiometrically (21.9 kg/t feed), and Table 3.65 gives NOx, SO2 and CO as the midpoints of its two units.

## What is weak

- **The yields are not sourced.** The model gives all the feed carbon to the product. Light ends and wild naphtha are not quantified in the source. They are TODO excludes, not zeros.
- **The hydrogen is one unit's.** It is an operating unit with a harder feed than straight-run gas oil, so it is probably high for this feed, while the BREF's 0.3 % is low for 10 mg/kg. No open source for deep HDS of straight-run gas oil alone was found. Purge losses are not separated out (gsd2 3.9, the BREF's 1 to 15 kg/t range).
- **The data are old.** Table 3.63 rests on 1991 and 1999 sources, before the 10 mg/kg limit, and Table 3.65 on two units, one of which reports limit values. `valid_until` is 2015, already lapsed.
- **Benchmarks are only partly independent.** Hydrogen is checked against the BREF's distillate range, 1 to 15 kg/t, which the dataset no longer takes its hydrogen from; it is inside. Heater CO2 is outside the two Table 3.65 units' 13 to 15 kg/t, because both units burn less than the whole Table 3.63 range; it is explained in `benchmarks/refining.yaml`. Electricity has no independent reference (`no_open_reference`), since the only open range is the BREF table it comes from.
- **Simplified fuel.** Refinery fuel gas is taken as pure methane. IPCC's refinery-gas factor is about 5 % higher.
- Midpoints of ranges are our choice; the source does not recommend them.
- Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED values elsewhere.

## Heater fuel across the refining entries

The six refining entries count heater fuel in three ways, each stated in its `lca/mappings.yaml`: `refinery-distillation-1` books refinery gas in kWh with IPCC's refinery gas factors in the dataset and leaves the fuel a gap (no producer); `catalytic-reforming-1` and `fcc-1` map the fuel in kWh to the shared natural-gas heat entry, whose combustion is in the background; this entry, `hydrocracking-1` and `sulfur-recovery-1` burn it as methane in the dataset and take natural gas by mass. A single family rule (one refinery fuel gas entry) is not decided yet, so direct CO2 per t is not comparable across the six entries without that note.

## Linking

The product has the registry slug `diesel`, and the feed has `gas-oil`, which links the straight-run gas oil of `refinery-distillation-1` explicitly; the feed sulfur is the assay's, so the link carries the same crude. The H2S output (`hydrogen-sulfide`) goes to sulfur recovery; it stays a gap until the cut-off rule for acid gas sent to `sulfur-recovery-1` is decided. Steam is by mass on the shared background entry (as `cumene-1`). Fuel is natural gas by mass, not linked to an Atlas producer (as `styrene-1`).

## Not counted yet (TODO)

Light ends and wild naphtha, hydrogen purge losses, feed nitrogen and its NH3, species dissolved in the sour water, fugitive emissions and drier adsorbents. The full list is in the dataset's `system_boundary.excluded`.
