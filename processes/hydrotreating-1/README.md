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

`lca/datasets/gas-oil-hydrodesulfurisation.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H, O and S balance. The sources are the REF BREF (Barthe et al. 2015, sections 2.13 and 3.13.1) and IPCC 2006 Vol. 2, chapter 1. Facts are recorded in our own form, each with its table in `parameters`.

- **Model formulas.** Gas oil is a mixture, so the feed and product are lumped into one formula each, C1000H1795S4 and C1000H1829. Both are ASSUMED. The feed formula gives 0.92 wt-% S, near the midpoint of the BREF's 0.05 to 1.8 % for diesel hydrotreatment. The BREF gives that range for vacuum gas oil feeds; applying it to straight-run gas oil is ASSUMED. The product's carbon fraction, 0.867, lies within IPCC's gas/diesel oil range. The model reaction takes 21 H2 per formula unit: 3.04 kg H2 per t feed, the BREF's 0.3 % H2 for distillates. All the feed sulfur leaves as H2S, 9.8 kg per t product.
- **Utilities** come from Table 3.63, distillate row, per t feed: electricity is the midpoint (15 kWh/t), steam the midpoint (105 kg/t, by mass) and cooling water the midpoint (2.5 m3/t at 10 K, about 29 kWh/t of heat rejected). Wash water is the midpoint (35 kg/t), and sour water is set equal to it. Catalyst use is 46 t/Mt (Table 3.64).
- **Fuel** is the lower bound of Table 3.63, 300 MJ/t. Both middle-distillate units of Table 3.65 burn less (about 247 and 275 MJ/t), so the bound is the value that the two tables come closest to sharing. The fuel is burnt as methane, which gives CO2 stoichiometrically, and Table 3.65 gives NOx, SO2 and CO as the midpoints of its two units.
- **Hydrogen** links to `hydrogen-1` (`lca/mappings.yaml`).

## What is weak

- **The yields are not sourced.** The model gives all the feed carbon to the product. Light ends and wild naphtha are not quantified in the source. They are TODO excludes, not zeros.
- **The hydrogen is probably low for 10 mg/kg.** The 0.3 % is the BREF's typical distillate figure from 1991 and 1999 data, before 10 mg/kg diesel. The BREF's own Table 3.62 lists about 4 kg/t for high-sulfur gas oil to 0.2 % S, and an operating diesel hydrotreater (Tian et al. 2022, mixed feed, 40 mg/kg) takes 7.9 kg/t of make-up gas. All make-up hydrogen counts as consumed, and purge losses are not separated out. The 1 to 15 kg/t range is wide (gsd2 3.9).
- **The data are old.** Table 3.63 rests on 1991 and 1999 sources, before the 10 mg/kg limit, and Table 3.65 on two units, one of which reports limit values. `valid_until` is 2015, already lapsed.
- **Benchmarks are only partly independent.** Hydrogen is checked against the independent Tian et al. (2022) unit; it is outside and explained in `benchmarks/refining.yaml`. Electricity is checked against the same BREF table it comes from. Heater CO2 is outside the two Table 3.65 units' 13 to 15 kg/t and is explained there.
- **Simplified fuel.** Refinery fuel gas is taken as pure methane. IPCC's refinery-gas factor is about 5 % higher.
- Midpoints of ranges are our choice; the source does not recommend them.
- Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED values elsewhere.

## Linking

The product has the registry slug `diesel`, and the feed has `gas-oil`, which links the straight-run gas oil of `refinery-distillation-1` explicitly. The H2S output (`hydrogen-sulfide`) goes to sulfur recovery; it stays a gap until the cut-off rule for acid gas sent to `sulfur-recovery-1` is decided. Steam is by mass on the shared background entry (as `cumene-1`). Fuel is natural gas by mass, not linked to an Atlas producer (as `styrene-1`).

## Not counted yet (TODO)

Light ends and wild naphtha, hydrogen purge losses, feed nitrogen and its NH3, species dissolved in the sour water, fugitive emissions and drier adsorbents. The full list is in the dataset's `system_boundary.excluded`.
