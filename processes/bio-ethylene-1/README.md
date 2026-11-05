# Bio-ethylene by catalytic dehydration of ethanol

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

This entry is a manifest and an LCI dataset only. It has no flowsheet and no simulation. The dataset is per tonne of polymer-grade ethylene, made from bought hydrated bio-ethanol over an alumina catalyst. The reactors are four adiabatic fixed beds in series with interheating and steam dilution, followed by quench, compression, caustic wash, drying and cryogenic purification.

## Route

Ethanol dehydration is the only industrial route to bio-ethylene. Braskem's 200 kt/a plant in Brazil, and the other plants and projects that the IEA-ETSAP and IRENA brief lists (Table 1), all use it. The brief says this process (ethanol-to-ethylene, ETE) has scarcely been used in recent decades, so few open data exist.

The process is continuous. The source designs a steady-state plant of 23.4 t/h with fixed beds in series (Arvidsson and Lundin 2011, sections 2.2 and 4.1.2), and the brief rates the industrial plants in kt/a. The dataset models the steam-diluted adiabatic design (Halcon SD, offered by Chematur). Isothermal multitubular reactors are not modelled. They are limited to about 370 degC by the heating fluid (source section 2.2.2.2).

## How it is built

`lca/datasets/bio-ethylene-ethanol-dehydration.yaml` is a hand-written **Tier 1** dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H, O and Na balance. The process data come from one open process model: Arvidsson and Lundin (2011), a Chalmers MSc thesis that simulates a stand-alone 200 kt/a plant in Aspen Plus after the Chematur design.

| Item | How | Source |
|---|---|---|
| Ethanol | the simulated flows: 43 875 kg/h of 93 wt% ethanol for 23 415 kg/h of ethylene, i.e. the source's yield of 0.57 kg/kg: 1.743 t/t, counted as ethanol | Tables 4.2 and 4.4, sections 4.2.5 and 4.3.2.2 |
| Ethanol not converted | feed minus what the eight reactions convert (99.5 % conversion, 99.1 % ethylene recovery would need only 1.686 t/t): 65 kg/t, to the effluent | sections 3.2.2 and 3.2.7, Table D1 |
| By-products | selectivities of Table D1. Ethane, propylene, butene, diethyl ether, acetaldehyde and unrecovered ethylene are fired in the furnace. CO, CH4 and H2 are vented. CO2 goes to the caustic wash. | Table D1, sections 2.2.5 and 2.2.7 |
| Dilution steam | 1:1 by weight with the hydrated feed: 1.87 t/t | section 2.2.1 |
| Fired heat | 15.9 MW of external fuel (HHV) at 80 % efficiency: 543 kWh/t absorbed | section 4.2.2, Table 4.6 |
| Electricity | 4.4 MW: 188 kWh/t | section 4.2, Table 4.4 |
| Refrigeration | 8.5 MW of cold at -25 degC: 363 kWh/t, not linked | section 4.2.2 |
| Direct CO2 | carbon of the fired by-products: 63 kg/t, biogenic | calculated |

The by-products fired in the furnace come to 21.7 kg/t. The source gives them as 7.5 MW at an HHV of 43.83 MJ/kg, which works out to about 26 kg/t. Its fuel figure includes that credit, so the dataset uses the source's 15.9 MW as given. No IPCC process-emission factor is used. The only direct CO2 is biogenic and comes from the calculated by-products.

## What is weak

- **Only a model; no plant data.** All process data come from one simulation study, not from a plant.
- **The source's yield and its reaction table disagree.** The simulated flows give 1.743 t of ethanol per t (0.57 kg/kg), but the reaction table (98.8 % selectivity, 99.5 % conversion, 99.1 % recovery) would need only 1.686 t/t. The source does not explain the 3.4 % difference. The dataset takes the simulated yield and sends the difference, as ethanol, to the effluent (ASSUMED; part of it may really be ethylene lost in the stripper vent). The value is 1.6 to 2.1 % above Haro et al. (2013) and close to the 1.74 t/t of the IEA-ETSAP and IRENA brief (`benchmarks/bio-based-chemicals.yaml`).
- **Electricity is probably low.** The 188 kWh/t leaves out the power of the -25 degC refrigeration, because the source assumes a refrigeration medium is available. Haro et al. give 353 to 397 kWh/t. The refrigeration duty is its own exchange, but it has no background, so it is a gap.
- **The fired heat is a pinch target, so it is a minimum.** It assumes feed-effluent heat exchange; without that exchange the furnace duty is 1.7 times higher.
- **Several reactions are corrected.** Four of the source's eight reactions do not balance as printed: those to ethane, propylene, butene (printed as butadiene) and CO2. The dataset uses the balanced forms, each marked ASSUMED in `parameters`. The table does not say what basis its selectivities are on. The dataset reads them as fractions of the converted ethanol. They set the by-products, the vent and the caustic, not the ethanol feed.
- **Steam and effluent are linked.** The dilution steam is taken as fresh, and all of it plus the reaction water goes to treatment. The source notes that the water may be recycled to the reactor, which would cut both. The steam is linked to the shared background by mass at 11 bar(a) saturated, so the extra enthalpy of 11.4 bar superheated steam is not counted.
- **Old data.** The data are from 2011 and from literature of 1981 to 2010. `valid_until` (reference year + 5) is 2016, so it has already lapsed.

## Carbon

The ethanol feed declares its carbon as 100 % biogenic (`carbon.biogenic_fraction`). That follows from the definition of the route, not from a supplier: the feed is linked to no producer yet. Fired and vented carbon are exported as non-fossil CO2, CH4 and CO.

## Linking

The product has the registry slug `ethylene`, the same as `ethylene-1`'s, and no Atlas process consumes it yet. Polyethylene would be its consumer, but it is not in the library.

Five exchanges are reported mapping gaps (`lca/mappings.yaml`):

- **Ethanol.** `ethanol-1` makes synthetic ethanol from fossil ethylene, so it is not the supplier. A bioethanol entry is planned.
- **NaOH.** It is counted as NaOH, while `chlor-alkali-1` sells 50 wt% solution per kg.
- **Refrigeration** at -25 degC.
- **Ethanol** in the effluent (unconverted, and the rest of the source's lower yield).
- **Spent caustic.**

## Not counted yet (TODO)

- Catalyst make-up and regeneration (coke burn-off)
- Molecular-sieve adsorbent
- Power of the refrigeration machine
- Cooling-water make-up and chemicals
- Furnace NOx and CO
- Caustic wash water
- Ethylene lost in the stripper vent

The full list is in the dataset's `system_boundary.excluded`.

## Sources

- Arvidsson, M., Lundin, B. (2011) *Process integration study of a biorefinery producing ethylene from lignocellulosic feedstock for a chemical cluster*. MSc thesis, Chalmers University of Technology. https://odr.chalmers.se/handle/20.500.12380/140886 (sections 2.2, 3.2, 4.1, 4.2, 4.2.2, 4.2.5, 4.3.2, Tables 4.2, 4.4 and 4.6, Appendix D).
- Haro, P., Ollero, P., Trippe, F. (2013) Technoeconomic assessment of potential processes for bio-ethylene production. *Fuel Processing Technology* 114:35-48, doi:10.1016/j.fuproc.2013.03.024. Accepted manuscript at idus.us.es (Tables 4 and 10). Used for the benchmarks only.
- IEA-ETSAP and IRENA (2013) *Production of Bio-ethylene*, Technology Brief I13 (route status; 1.74 t of hydrated ethanol per t; 99 % conversion and 97 % selectivity). Used for context and as a benchmark that is recorded but not bound.
