# Waste incineration with energy recovery

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of mixed municipal solid waste (MSW), burnt on a moving grate with a heat recovery boiler. A back-pressure turbine feeds a district-heating exchanger. Flue-gas cleaning is semi-wet with quicklime, plus SNCR with ammonia water, activated carbon and a bag filter.

## Route and operation

The route is the moving grate, the dominant industrial route. The WI BREF puts about 90 % of European MSW installations on grates (section 2.3.1, p. 37) and calls the grate the route of most modern MSW plants (Table 4.6, p. 316). These plants run continuously: BAT includes continuous rather than batch operation to keep start-ups and shutdowns few (section 4.1.2, p. 294). IPCC 2006 gives a separate emission factor class for continuous incinerators. Of the energy configurations, CHP is the one most European waste is burnt in: 184 of the 314 plants and 41 of 59 Mt/a in CEWEP's survey (Energy Report III, Table 2). The heat-oriented variant fits the coverage entry's link to steam and heat.

## How it is built

`lca/datasets/msw-incineration-grate-chp.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed balance of C, H, N and O. Each parameter names its document, section or table and page, or is marked ASSUMED with the reason.

- **The waste** enters by its ultimate analysis: water, fossil and biogenic carbon, hydrogen, oxygen, nitrogen, and mineral matter that carries the S, Cl and F. The values are the midpoints of the WI BREF's ranges for German municipal waste (Table 1.6). The fossil share of the carbon is the midpoint of the BREF's 33 to 50 % of the CO2 (section 3.2.1). Every waste exchange is free, as `docs/system-model.md` section 3 sets out (below).
- **Combustion** is stoichiometric. The combustion oxygen comes from ambient air (free), and all carbon is oxidised (IPCC oxidation factor 1). The dry flue gas at the 11 % O2 reference comes out at 4400 Nm3/t, inside the BREF's 4000 to 7000 Nm3/t (Table 4.6, typically 5200; the table does not state whether that is dry or at a reference O2).
- **Energy:** the LHV is 9 GJ/t (Table 2.10). It is multiplied by the BAT-AEEL midpoint for gross energy efficiency, 81.5 % (Table 5.2). The split into electricity and heat comes from the BREF's heat-oriented CHP example (Table 8.4: 5.8 MW electric, 26.2 MW heat). The plant's own use is then subtracted (Table 3.37 averages: 107 kWh of electricity and 505 kWh of heat per t). The result is a net export of **262 kWh electricity and 1163 kWh heat per t**.
- **Reagents and residues** are midpoints of the BREF's ranges: quicklime 8.5 kg/t, ammonia water 2.25 kg/t (NH3 0.56 kg), activated carbon 1.75 kg/t, natural gas for the support burners 12.25 m3/t, boiler ash 30 kg/t, FGC residue with fly ash 37.5 kg/t. Bottom ash is the mineral mass closed by difference: 295 kg/t dry, inside the BREF's 150 to 350 kg/t.
- **Air emissions:** the BAT-AEL midpoints (existing plants, daily or sampling-period averages, Tables 5.3 to 5.8) are multiplied by the calculated flue gas. This covers dust, HCl, HF (the upper bound), SO2, NOx, CO, NH3, TVOC, Hg and PCDD/F. N2O (50 g/t, Table 5.6) and CH4 (0.2 g/t, Table 5.3) are IPCC 2006 Vol. 5 ch. 5 defaults for continuous incinerators.

The result is 344 kg fossil CO2 and 451 kg biogenic CO2 per t. The fossil figure includes 24 kg from the support fuel. The total of 0.79 t/t is inside the BREF's 0.7 to 1.7 t/t.

## How the library models it (system model)

Under the library's cut-off model, waste sent to incineration with energy recovery leaves its producer without burden. The user of the recovered energy carries the treatment (`docs/system-model.md` section 3). So the waste is a free input here, and the **products are the net electricity and the net heat**. The dataset lists both and stays unallocated. The database allocates them by exergy (`lci/mappings.yaml` `allocation.waste-incineration-1`, rule `physical-exergy`). Electricity counts 3600 kJ/kWh. Heat delivered at 115 °C (condensing 1.7 bar(a) steam) counts 836 kJ/kWh. This gives shares of about 49 % to electricity and 51 % to heat. System-model section 2 allows energy or exergy for exported heat and never a credit.

**Note for the reviewer.** This convention differs from core's `Treatment` documentation and from the usual ecoinvent cut-off practice. There the waste producer carries the incineration and the recovered energy is burden-free. The dataset follows the library's own document. A library that switches to the other convention needs a treatment-service product, `product:msw`, carrying the burden, and burden-free energy. The waste input is already one closed block, so that change is local.

## What is weak

- **The waste is one average waste, not a model per fraction.** The coverage entry names the Doka (2003) approach, which models each waste fraction, and this is not that. The composition midpoints come from separate ranges (German waste, UBA 2001), not from one analysed waste. A Dulong-type estimate from them gives about 6.7 GJ/t LHV against the 9 GJ/t used for the energy, so carbon and energy are not fully consistent. The CO2 is at the low end of the BREF's range.
- **The energy split rests on one example plant** (FR53). Subtracting the average own heat use of 505 kWh/t is ASSUMED. Some plants' gross heat may already exclude it, and the FR53 example itself reports no internal heat use. It is probably on the high side: CEWEP's CHP plants report a weighted mean of 163 kWh/t of self-used heat (Energy Report III, Annex A). With that value the net heat would be about 1505 kWh/t instead of 1163, and the exergy shares would move to about 43 % electricity and 57 % heat. For comparison, CEWEP's surveyed CHP plants export a weighted mean of 338 kWh electricity and 938 kWh heat per t (`benchmarks/waste-treatment.yaml`). Both of this dataset's values lie inside CEWEP's min-max ranges, but those ranges are very wide.
- **BAT-AEL midpoints are permit levels, not measured means.** Real emissions are often lower. HF is the upper bound "< 1 mg/Nm3".
- Mercury is counted as the biosphere3 3.9 flow "Mercury II", which is the only mercury-to-air flow in that list. PCDD/F I-TEQ is counted as 2,3,7,8-TCDD. Dust is counted as PM2.5.
- The data are of the 2016 BREF data collection (operating year 2014). The composition dates from 2001. `valid_until` is 2019, so it has already lapsed.
- Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED elsewhere.

## Linking

- `feed:ammonia` (the NH3 of the ammonia water) links to `ammonia-1` (`lca/mappings.yaml`). The natural gas links by its factor, as `utility-steam-ng-boiler`'s does.
- The products carry no `inventory_key` (`process.yaml` header). With one, the build would offer this plant as the default Atlas electricity producer to every consumer of grid power. A study that wants the energy pins it with `link.dataset`.
- The quicklime links `lime-1` explicitly. The build reports four mapping gaps: activated carbon, bottom ash, boiler ash and FGC residue have no background entry yet.

## Not counted yet (TODO)

Metals other than Hg in the flue gas (their BAT-AELs are sums), process and quench water, grid power in outages, scrap recovered from the bottom ash and its unburnt carbon, treatment of the residues, diffuse emissions, transport of the waste. The full list is in the dataset's `system_boundary.excluded`.
