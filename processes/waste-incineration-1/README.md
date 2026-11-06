# Waste incineration with energy recovery

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of mixed municipal solid waste (MSW), burnt on a moving grate with a heat recovery boiler. A back-pressure turbine sends its 1.7 bar(a) exhaust steam to a district-heating exchanger, which is outside the boundary. Flue-gas cleaning is semi-wet with quicklime, plus SNCR with ammonia water, activated carbon and a bag filter.

## Route and operation

The route is the moving grate, the dominant industrial route. The WI BREF puts about 90 % of European MSW installations on grates (section 2.3.1, p. 37) and calls the grate the route of most modern MSW plants (Table 4.6, p. 316). These plants run continuously: BAT includes continuous rather than batch operation to keep start-ups and shutdowns few (section 4.1.2, p. 294). For continuous MSW incineration, IPCC 2006 Vol. 5 (section 5.4.2) sends the CH4 factor to the stationary-combustion factors of Vol. 2. Of the energy configurations, CHP is the one most European waste is burnt in: 184 of the 314 plants and 41 of 59 Mt/a in CEWEP's survey (Energy Report III, Table 2). The heat-oriented variant fits the coverage entry's link to steam and heat.

## How it is built

`lca/datasets/msw-incineration-grate-chp.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed balance of C, H, N and O. Each parameter names its document, section or table and page, or is marked ASSUMED with the reason.

- **The waste** enters by its ultimate analysis: water, fossil and biogenic carbon, hydrogen, oxygen, nitrogen, and mineral matter that carries the S, Cl and F. The values are the midpoints of the WI BREF's ranges for German municipal waste (Table 1.6), except carbon. The carbon is set to 37.8 % of the dry solids, inside the BREF's 18 to 40 %, so that the composition's LHV equals the 9 GJ/t energy basis (below). That LHV comes from the HHV correlation of Channiwala and Parikh (2002) less the latent heat of the water (ASSUMED closure). At the carbon midpoint of 29 %, the composition would give only 6.6 GJ/t, and the energy exported would exceed the heating value of the inventoried waste. The fossil share of the carbon is the midpoint of the BREF's 33 to 50 % of the CO2 (section 3.2.1). Every waste exchange is free, as `docs/system-model.md` section 3 sets out (below).
- **Combustion** is stoichiometric. The combustion oxygen comes from ambient air (free), and all carbon is oxidised (IPCC oxidation factor 1). The dry flue gas at the 11 % O2 reference comes out at 5600 Nm3/t, inside the BREF's 4000 to 7000 Nm3/t (Table 4.6, typically 5200; the table does not state whether that is dry or at a reference O2).
- **Energy:** the LHV is 9 GJ/t (Table 2.10). It is multiplied by the BAT-AEEL midpoint for gross energy efficiency, 81.5 % (Table 5.2). The split into electricity and heat comes from the BREF's heat-oriented CHP example (Table 8.4: 5.8 MW electric, 26.2 MW heat). The plant's own use is then subtracted (Table 3.37 averages: 107 kWh of electricity and 505 kWh of heat per t). The result is a net export of **262 kWh electricity and 1163 kWh heat per t**. The energy balance holds: the gross output of 7.34 GJ/t is below the 9.0 GJ/t of the waste plus 0.44 GJ/t of support gas (77.7 % on both). The generator script checks this.
- **Reagents and residues** are midpoints of the BREF's ranges: quicklime 8.5 kg/t, ammonia water 2.25 kg/t (NH3 0.56 kg), activated carbon 1.75 kg/t, natural gas for the support burners 12.25 m3/t, boiler ash 30 kg/t, FGC residue with fly ash 37.5 kg/t. Bottom ash is the mineral mass closed by difference: 232 kg/t dry, inside the BREF's 150 to 350 kg/t.
- **Air emissions:** the BAT-AEL midpoints (existing plants, daily or sampling-period averages, Tables 5.3 to 5.8) are multiplied by the calculated flue gas. This covers dust, HCl, HF (the upper bound), SO2, NOx, CO, NH3, TVOC, Hg and PCDD/F. NH3 uses the 2 to 15 mg/Nm3 range of an existing plant with SNCR and no wet abatement (Table 5.6, footnote 3). N2O is 50 g/t, the IPCC 2006 Vol. 5 default for continuous incinerators (Table 5.6). CH4 is 30 kg/TJ, which is 0.27 kg/t. That is the stationary-combustion factor for municipal wastes (IPCC 2006 Vol. 2, ch. 2, Table 2.2), which Vol. 5 names as good practice for continuous MSW incineration. Vol. 5's own Table 5.3 is for semi-continuous and batch units.

The result is 439 kg fossil CO2 and 587 kg biogenic CO2 per t. The fossil figure includes 24 kg from the support fuel. The total of 1.03 t/t is inside the BREF's 0.7 to 1.7 t/t.

## How the library models it (system model)

Under the library's cut-off model, waste sent to incineration with energy recovery leaves its producer without burden. The user of the recovered energy carries the treatment (`docs/system-model.md` section 3). So the waste is a free input here, and the **products are the net electricity and the net heat**. The dataset lists both and stays unallocated. The database allocates them by exergy (`lci/mappings.yaml` `allocation.waste-incineration-1`, rule `deviation`: CHP heat and power are not the products of one separation, the case that rule `physical-exergy` names). Electricity counts 3600 kJ/kWh. The heat leaves the boundary as condensing 1.7 bar(a) steam at 115 °C and counts 836 kJ/kWh. This gives shares of about 49 % to electricity and 51 % to heat. The district-heating exchanger and network are outside the boundary. Delivered as network water at, for example, 90/50 °C, the same heat would count about 470 kJ/kWh, and electricity would take about 63 % instead of 49 %. System-model section 2 allows energy or exergy for exported heat and never a credit.

**Convention.** Core's `Treatment` documentation and the usual ecoinvent cut-off practice use the other convention: the waste producer carries the incineration, and the recovered energy is burden-free. This dataset follows the library's `docs/system-model.md`. Under the other convention the dataset would need a treatment-service product, `product:msw`, carrying the burden, with burden-free energy. The waste input is already one closed block, so that change would stay local. Reconciling the two conventions is open (see the pull request).

## What is weak

- **The waste is one average waste, not a model per fraction.** The coverage entry names the Doka (2003) approach, which models each waste fraction, and this is not that. The composition comes from separate ranges (German waste, UBA 2001), not from one analysed waste. Carbon is closed on the European average LHV (9 GJ/t) by a correlation, ASSUMED, and sits near the top of its range. With all midpoints the waste would have 6.6 GJ/t, and fossil CO2 would be 344 instead of 439 kg/t. Every emission computed from the flue gas would be about 21 % lower.
- **The energy split rests on one example plant** (FR53). Subtracting the average own heat use of 505 kWh/t is ASSUMED. Some plants' gross heat may already exclude it, and the FR53 example itself reports no internal heat use. It is probably on the high side: CEWEP's CHP plants report a weighted mean of 163 kWh/t of self-used heat (Energy Report III, Annex A). With that value the net heat would be about 1505 kWh/t instead of 1163, and the exergy shares would move to about 43 % electricity and 57 % heat. For comparison, CEWEP's surveyed CHP plants export a weighted mean of 338 kWh electricity and 938 kWh heat per t (`benchmarks/waste-treatment.yaml`). Both of this dataset's values lie inside CEWEP's min-max ranges, but those ranges are very wide.
- **BAT-AEL midpoints are permit levels, not measured means.** Real emissions are often lower. HF is the upper bound "< 1 mg/Nm3". CH4 is counted fossil (ASSUMED). About 58 % of the waste carbon is biogenic, so this is the higher-impact choice.
- Mercury is counted as the biosphere3 3.9 flow "Mercury II", which is the only mercury-to-air flow in that list. PCDD/F I-TEQ is counted as 2,3,7,8-TCDD. Dust is counted as PM2.5.
- The data are of the 2016 BREF data collection (operating year 2014). The composition dates from 2001. `valid_until` is 2019, so it has already lapsed.
- Uncertainty is `gsd2 = sqrt(high / low)` where the source gives a range (our convention), and ASSUMED elsewhere.

## Linking

- `feed:ammonia` (the NH3 of the ammonia water) links to `ammonia-1` (`lca/mappings.yaml`). The natural gas links by its factor, as `utility-steam-ng-boiler`'s does.
- The products carry no `inventory_key` (`process.yaml` header). With one, the build would offer this plant as the default Atlas electricity producer to every consumer of grid power. A study that wants the energy pins it with `link.dataset`.
- The quicklime links `lime-1` explicitly. The build reports four mapping gaps: activated carbon, bottom ash, boiler ash and FGC residue have no background entry yet.

## Not counted yet (TODO)

Metals other than Hg in the flue gas (their BAT-AELs are sums), process and quench water, grid power in outages, scrap recovered from the bottom ash and its unburnt carbon, treatment of the residues, diffuse emissions, transport of the waste. The full list is in the dataset's `system_boundary.excluded`.
