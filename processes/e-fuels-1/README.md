# Fischer-Tropsch e-fuel from CO2 and hydrogen

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of blended Fischer-Tropsch liquid fuel, made from hydrogen and captured CO2 by reverse water-gas shift (RWGS), cobalt low-temperature FT synthesis and wax hydrocracking. Hydrogen and CO2 arrive at the gate: electrolysis and CO2 capture are outside the boundary.

## How it is built

`lca/datasets/fischer-tropsch-fuel-rwgs-co2-h2.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H and O balance.

All flows come from one open process simulation: König, Baucks, Dietrich and Wörner (2015, Energy 91:833), read in its accepted manuscript on DLR elib. Its plant takes 100 MW (LHV) of hydrogen and makes 5.5 t/h of liquid fuel. The dataset scales that plant to 1 t of fuel.

| Item | Per t fuel | How |
|---|---|---|
| Hydrogen, at 2.5 MPa | 547 kg | source flow, hydrocracker hydrogen included |
| CO2, at 0.1 MPa | 4164 kg | source flow |
| Electricity, plant utilities | 885 kWh | recovered from the source's PtL efficiency (43.3 %) less the electrolyser's AC power |
| External heat | none | the source's pinch analysis covers the heating demand from the process; the RWGS is fired with the plant's own fuel gas |
| Reaction water to treatment | 3002 kg | closes the source's plant mass balance |
| CO2 in the burner flue gas | 1063 kg | feed carbon not in the fuel (carbon balance) |
| Water vapour in the flue gas | 514 kg | hydrogen balance |
| Combustion oxygen (free, from air) | 868 kg | oxygen balance; the source's burner air carries about 18 % more |

## What is weak

- **One simulation, no plant.** No RWGS-FT plant runs at this scale. The numbers are a 2015 design with an equilibrium RWGS at 900 °C. An independent design, Zang et al. (2021), feeds 63 % more CO2 and about 16 % more fresh hydrogen per kg of fuel (its Table 2, LHV basis), and converts 45.5 % of the CO2 carbon against 73.7 % here. All four KPIs in `benchmarks/synthetic-fuels.yaml` are outside Zang's values, and the reason is recorded for each. The comparison shows how far two designs lie apart. It does not validate this dataset.
- **The product is one blend.** The source reports gasoline, kerosene and diesel cuts, but not as numbers that could be read here. The dataset keeps the cuts as one product, as Zang et al. do for their stand-alone plant. Splitting it would need the cuts and an allocation (energy, hierarchy step 2).
- **The model fuel is ASSUMED.** n-Dodecane (C12H26) stands for the product. It sets the carbon left for the burner and the split of water between effluent and flue gas. With it the carbon conversion comes out at 74.5 %, against the source's 73.7 %.
- **The electricity is recovered, not read.** The source states no utility power. 4.87 MW follows from its efficiency definition (eq. 9) with the stated 150.1 MW AC to the electrolyser. The efficiency is rounded, so the value could lie anywhere from 4.68 to 5.04 MW. The source's "utility losses of 2.1 %" would give about 3.3 MW instead, but that does not reproduce the stated 43.3 %. The two loads the source names (1.1 MW cooling-water pumping, 0.5 MW refrigeration) plus a rough estimate of our own for the CO2 and recycle compressors (about 3 MW) come to about 4.6 MW, close to the 4.87 MW used.
- **Excess steam is not exported.** The source has 25.7 MW of surplus steam. The dataset counts neither a co-product nor a credit for it. If a site uses it, it becomes a co-product to allocate (docs/system-model.md, section 2).
- **CO2 origin is ASSUMED fossil.** The feed is taken as captured from a fossil point source (`co2_source: fossil-point-source`), so the burner CO2 is fossil, and so is the carbon in the fuel. A biogenic or direct-air-capture feed changes both, and the feed then needs that supplier's dataset.
- The source is from 2015. `valid_until` is the reference year + 5, 2020, so it has already lapsed.

## Linking

The product has the new registry slug `fischer-tropsch-fuel` (a mixture without a composition). Hydrogen and CO2 are reported gaps on purpose, as the key comments in `lca/mappings.yaml` explain. Their keys are not registry slugs, so the build does not link the merchant-hydrogen or liquid-CO2 background. `hydrogen-1` is the SMR variant and is not the supplier. An electrolysis entry and a CO2 capture entry are the candidates, each to be linked explicitly. Electricity links the site's medium-voltage grid, and wastewater links the shared wastewater entry.

## Not counted yet (TODO)

Catalysts (nickel RWGS, cobalt FT, hydrocracking; cobalt is a critical metal and is never cut), CO, CH4 and NOx in the flue gas, oxygenates in the FT water, cooling-water make-up, product fractionation, hydrogen compression from a lower supply pressure, CO2 capture and purification. The full list is in the dataset's `system_boundary.excluded`.
