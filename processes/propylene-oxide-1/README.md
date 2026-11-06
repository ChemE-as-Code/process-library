# Propylene oxide by the chlorohydrin process with lime

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

This folder holds a manifest and an LCI dataset only. There is no flowsheet and no simulation. The basis is one tonne of propylene oxide (PO). Propylene and chlorine react in water to form propylene chlorohydrin and HCl. Milk of lime then turns the chlorohydrin into PO and neutralises the acid to calcium chloride. PO is steam-stripped from the brine and distilled. The plant runs continuously: propylene, chlorine and water are fed to the hypochlorination tower, whose temperature is held by controlling the feed flows, and the chlorohydrin solution is drawn off the top to the saponifier (ANL/CNSV-9, p. 150 to 151).

## How it is built

`lca/datasets/propylene-oxide-chlorohydrin-lime.yaml` is a hand-written **Tier 0** dataset, a stoichiometric screening. Tier 1 would need electricity and heat sourced for this process. The only open figures found are the IEA's averages for all Western European propylene oxide, whose route is not named, so the dataset stays at Tier 0. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed element balance (C, H, O, Cl, Ca).

| Item | Source | Standing |
|---|---|---|
| Propylene, chlorine | stoichiometry, plus 1,2-dichloropropane (DCP) at 0.15 t/t, the midpoint of the 0.1 to 0.2 t/t in US 4,560,451 (1985) | 0.780 t propylene and 1.315 t chlorine per t |
| Lime | ANL/CNSV-9 (1980), Fig. 4.58: 1.09 lb per lb PO, from 1976 data | read as quicklime (ASSUMED); 1.13 times the stoichiometric need, and the excess is an output |
| Effluent | LVOC BREF (2017), section 2.1.2.8: about 40 t/t | US 4,560,451 gives 43 t |
| Calcium chloride | stoichiometry, 1 mol per mol PO: 1.91 t/t | both sources give about 2 t |
| Electricity | IEA information paper (Saygin et al. 2009), Table 13: Western European average for propylene oxide, route not named | 1.0 GJ/t, 278 kWh/t (applying it to this route is ASSUMED) |
| Steam | the same table | 18.0 GJ/t, 5000 kWh/t (ASSUMED to apply; heating the 40 t of brine from the tower's 50 °C to 100 °C alone takes 8.4 GJ/t) |

The LVOC BREF covers the chlorohydrin process in outline only, and says it is not considered further. It names the large effluent and salt load, and the electricity used to make the chlorine upstream. Table 2.5 puts the effluent before biological treatment in its highest classes for COD (above 10 kg/t) and AOX (above 100 g/t). Those are lower bounds, so they are TODO items and are not entered as values.

## What is weak

- **The energy is not specific to this route.** The electricity and steam are the IEA's estimated current averages for Western European propylene oxide (Table 13, "industrial sources"), 1.0 and 18.0 GJ/t. The paper does not name the route, and the LVOC BREF (section 2.1.2.8) names co-production with styrene, the chlorohydrin process (in one Member State) and epoxidation with hydrogen peroxide, so applying the figures here is ASSUMED. The steam is about twice the sensible heat of the brine alone (8.4 GJ/t), which leaves room for PO distillation and losses; US 4,560,451 calls the energy for complete stripping of the brine very large. ANL (1980), Fig. 4.58, gives one process-energy input of 18,700 Btu per lb PO and labels it electricity. That is about 43 MJ per kg of primary energy at the report's 33 % generating efficiency (p. 71), or about 3,990 kWh/t delivered if read literally. The same figure shows no steam input, although the text describes steam heating and stripping (p. 151), and other figures in the report show steam separately. So the value is taken to cover all utilities and is not used. It is recorded as the electricity KPI (out of range, explained). Read as all utilities in primary terms, it is about twice the IEA averages in primary terms (22 GJ/t at the paper's 90 % steam and 40 % power efficiencies).
- **The feeds mix sources from different eras.** ANL's 1976 figures, 0.94 t propylene and 1.59 t chlorine per t, imply about 0.58 t of by-product. The dataset uses the patent's lower 0.1 to 0.2 t/t DCP. Its lime figure still comes from ANL. The KPIs show both readings (`benchmarks/oxygenates.yaml`).
- Dichloro-diisopropyl ether is counted as DCP. The fate of the DCP (sale or incineration) is not stated, so it stays an output with no allocation.
- Calcium chloride is modelled as passing biological treatment unchanged. It goes to surface water as dissolved solids, the same flow that chlor-alkali-1's NaCl uses.
- Reading "lime" as CaO is an assumption. Read as Ca(OH)2, it would fall short of the 1 mol per mol PO that the chlorohydrin and the HCl need.
- The reference year is 1985, so `valid_until` (1990) has long lapsed. Sources: US 1976 to 1985 and EU 2017.
- Uncertainty: `gsd2 = sqrt(high / low)` where the sources give a range (our convention), ASSUMED values elsewhere.

## Linking

The product has the registry slug `propylene-oxide`. Chlorine links to `chlor-alkali-1` (`lca/mappings.yaml`). Propylene is a reported mapping gap because its supplier is not chosen; `ethylene-1` and `propylene-pdh-1` are candidates. Lime links `lime-1` explicitly. The lime residue has no shared entry, so it is a gap too.

## Not counted yet (TODO)

COD and AOX of the effluent, the vent purge and its caustic scrubber, fugitive emissions to air, the ether as a separate by-product, energy figures for this route itself, and the caustic (cell-liquor) variant with brine recycle. The full list is in the dataset's `system_boundary.excluded`.
