# Polypropylene by bulk loop and gas-phase polymerisation

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

This entry has a manifest and an LCI dataset only. There is no flowsheet and no simulation. The basis is one tonne of polypropylene (PP) resin pellets, made from polymer-grade propylene with Ziegler-Natta catalysts in a continuous process.

## Route

The dataset is a mix of the two continuous routes that make most PP:

- **Bulk route:** polymerisation in liquid propylene in loop reactors (Spheripol type). A fluidised-bed gas-phase reactor follows for impact copolymers.
- **Gas-phase route:** a fluidised bed or stirred powder bed (Unipol, Novolen and Innovene types).

Why this route:

- The POL BREF (2007, section 3.2.5) names these two families as the processes now in use. The old solvent slurry process with alcohol wash is kept only for speciality grades such as capacitor film.
- The source report says that about 39 % of PP producers worldwide use Spheripol and about 16 % use Unipol. That share is quoted from a trade website and is not verified here.
- Both routes run continuously. Catalyst, monomer and hydrogen go in, and polymer comes out, without stopping (POL BREF sections 3.2.5.2.1 and 3.2.5.3.1).

The data mix is the source's own: about two-thirds bulk and one-third gas phase, by the production of its three plants.

## How it is built

`lca/datasets/polypropylene-bulk-gas-phase.yaml` is a hand-written **Tier 1** dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed balance of C, H, N and O.

| Item | Source | Standing |
|---|---|---|
| Propylene 1014 kg/t, nitrogen 64 kg/t, electricity 300 kWh/t (160 grid, 140 cogeneration), natural gas 34.0 m3/t | Franklin Associates for the American Chemistry Council (2021), Table 12 | weighted average of 3 US plants, 2015-2016, about 16 % of US production; a public report |
| Air emissions (NMVOC, PM2.5, NOx), wastes | same table | averages as reported |
| CH4, N2O, CO, SO2, NH3 and the process CO2 (10 kg/t) | same table | the report gives only the order of magnitude, to protect the producers' data |
| CO2 and water from burning natural gas | stoichiometry, natural gas taken as methane (ASSUMED) | about 67 kg CO2/t |
| Off-gas residual (9.6 kg/t) | closes the balance | modelled as propylene (ASSUMED) |

No IPCC 2006 process-emission factor applies. Volume 3, section 3.9.1 gives guidance for methanol, ethylene and propylene, ethylene dichloride, ethylene oxide, acrylonitrile and carbon black, and none for polymerisation.

The POL BREF gives no PP data of its own. Its section 3.3.5 says PP plants can be compared with PE plants. Process by process, it pairs gas-phase PP with LLDPE and bulk PP with a modern PE gas-phase plant. For energy it pairs suspension (bulk or slurry) PP with HDPE slurry, and it notes that PP monomer use differs slightly from the HDPE figures because propylene purity varies. On that basis `benchmarks/polyolefins.yaml` binds the propylene use to the BREF's HDPE monomer figures (Table 3.11, 1008 to 1066 kg/t). The value of 1014 kg/t falls inside that range. Against the LLDPE figures (Table 3.13, 1015 to 1043 kg/t), which match the BREF's process-by-process pairing, it sits 1 kg/t below the lower end. That lower end is the average of the best half of plants, so 1014 kg/t is a good-plant value, not an outlier. The check is independent of the dataset, because the dataset's numbers come from the US report and not from the BREF.

The direct energy cannot be bound as a KPI, because the fuel is counted in kg (docs/benchmarks.md). Worked out by hand, it is 300 kWh of electricity plus 24.4 kg × 50.01 MJ/kg of natural gas, which is about 640 kWh/t. That also falls inside the BREF's HDPE direct-energy figures (Table 3.11, 570 to 940 kWh/t) and its LLDPE ones (Table 3.13, 580 to 890 kWh/t).

## What is weak

- **Only three plants, all in the US.** The 140 kWh/t of cogeneration electricity is supplied here as grid electricity (ASSUMED). The report says most of its data providers named natural gas as the cogeneration fuel (report p. 14), and it describes the power as coming from the grid or from a nearby cogeneration plant (report p. 19). The library has no natural-gas CHP electricity dataset to link instead.
- **The natural gas is gross.** The report also counts 2.70 m3/t of natural gas as avoided, because vent gas is exported. That credit is left out (cut-off). The volume's reference state is not stated, and 0 °C is ASSUMED. The library's natural-gas proxy converts back at the same density, so the background still sees 34.0 m3.
- **The natural gas combustion counts CO2 and water only.** Its NOx, CO and other combustion emissions are a TODO. The report's Table 12 holds the plants' process emissions, flaring included, and it counts fuel burnt in boilers separately (report p. 24). So these emissions are most likely missing here, not double counted.
- **The process CO2 is flaring, and only an order of magnitude.** The report says the PP plants' process greenhouse gases come from flaring (report p. 24). The 10 kg/t is given only as an order of magnitude. Taking the flared gas as propylene is ASSUMED.
- **The reported emissions and wastes are far below the European PE figures.** The NMVOC (0.11 kg/t) is below the BREF's PE ranges (HDPE 0.65 to 5.75 kg/t, LLDPE 0.18 to 1.58 kg/t, Tables 3.11 and 3.13). The hazardous waste (0.13 kg/t in all) is also below them (HDPE 3.1 to 5.6 kg/t, LLDPE 0.8 to 6.9 kg/t). The BREF figures are from 1999 and for PE, so this is not a contradiction. Still, US reporting of these flows may be incomplete.
- **The off-gas residual is a model choice.** It also carries the propane of the feed, and its fate (fuel, flare or export) is not split. The residual is a gap with no link.
- **Some reported releases are TODO excludes and are not set to zero.** They are coarse particulates, aldehydes and the releases to water, which have no flow identity yet, and the 3 m3/t of water consumption, whose source and fate are not stated.
- **Catalysts and additives are not reported.** The BREF puts the catalyst left in the product below 100 g/t.
- **The data are dated.** `valid_until` is the reference year + 5, which is 2021, so it has already lapsed.

## Linking

The product has the registry slug `polypropylene`. No Atlas process uses it yet; plastic pyrolysis is the planned consumer (`coverage.yaml`).

Propylene is a reported mapping gap, because its supplier is not chosen (`lca/mappings.yaml`). `ethylene-1` makes polymer-grade propylene as a co-product, and a PDH route is the other candidate.

Nitrogen links to the gaseous site grade. Natural gas stays on its background mapping, as in `styrene-1`.

## Sources read

- **Franklin Associates (2021), the PP report for the ACC:** sections on technological scope and on PP production, and Table 12.
- **EU JRC POL BREF (2007):** sections 3.2.5 (PP processes), 3.3.3 (Table 3.11, HDPE), 3.3.4 (Table 3.13, LLDPE), 3.3.5 (PP) and 13.2 (BAT-AELs for polyolefins).
- **IPCC 2006 Guidelines, Volume 3, chapter 3:** section 3.9.1, the scope of the petrochemicals guidance.
- **PlasticsEurope eco-profile of PP (Boustead, 2005):**
  - The copy read was not hosted by PlasticsEurope, and plasticseurope.org refused the download.
  - It is cradle-to-gate only, with no polymerisation step separated out, so it is not used.
  - The newer PlasticsEurope eco-profile could not be retrieved.
