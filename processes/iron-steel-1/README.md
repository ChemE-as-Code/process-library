# Crude steel by the integrated BF-BOF route

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

Manifest and LCI dataset only, with no flowsheet and no simulation. Per tonne of crude steel (liquid steel cast into semis) from an integrated works: coke ovens, sinter plant, blast furnace and basic oxygen furnace (BOF) steel plant with continuous casting.

## How it is built

`lca/datasets/iron-steel-bf-bof-integrated.yaml` is a hand-written Tier 1 dataset: every amount is the `formula` of its `parameters`. The parameters are facts of two open sources, each with its table:

- the EU Iron and Steel BREF (Remus et al. 2013, EUR 25521 EN, doi:10.2791/97469): the per-tonne input and output tables of the sinter plant (Tables 3.2, 3.4), coke ovens (Table 5.2), blast furnace (Tables 6.1 to 6.6) and BOF plant (Tables 7.3, 7.4), for EU plants in 2004 and 2005;
- the IPCC 2006 Guidelines, Vol. 3, ch. 4: the Tier 2 carbon contents (Table 4.3) for the CO2, the Tier 1 CH4 factors (Table 4.2) and the coke heating value.

The plants are chained per t of liquid steel: 859.5 kg hot metal per t (BOF table), 1088 kg sinter and 359 kg coke per t hot metal (BF weighted averages), the sinter's solid fuel taken as coke breeze. That gives 935 kg sinter and 351 kg coke per t of steel, hence 451 kg coking coal. Weighted averages are used where the BREF gives them (blast furnace, sinter inputs) and the midpoints of its ranges elsewhere. Midpoints are our choice, the source does not recommend them.

**CO2** is a carbon balance over the whole works, IPCC Tier 2 style (Equation 4.9 with the coke plant added). The carbon in is that of the coking coal, injected coal and oil, natural gas, limestone, dolomite and scrap. Subtracted are the carbon in the steel, the tar and light oil, and the CO and CH4 emitted. Every process gas is taken as burnt at the works, the IPCC Tier 1 assumption, so its CO2 is counted here. The result is 1645 kg CO2 per t. The IPCC Tier 1 BOF factor is 1460 kg/t (world data of 2003), but it covers the blast furnace and converter only: the IPCC adds coke and sinter with factors of their own. With those added at this dataset's coke and sinter per t, the Tier 1 sum is about 1840 kg/t. The per-plant direct CO2 of Pardo et al. (2012, JRC) comes to about 1690 kg/t (our arithmetic for both; see `benchmarks/iron-steel.yaml`).

**Operation.** Oxygen steelmaking is a batch process: each charge of hot metal is blown until it reaches the grade (BREF section 7.3.8, p. 411). The coke ovens are also charged and pushed oven by oven. The sinter strand and the blast furnace run continuously, and the BREF data are yearly means per tonne. The dataset is therefore a time average of the integrated works, not a model of one heat.

## What is weak

- **Exported energy is not counted.** The works makes more process gas than its four plants use. The surplus goes to the site power plant, stoves and rolling mills, and BF top-gas turbines and BOF waste-heat boilers make power and steam. None of this is quantified as an output, and none is credited. The purchased electricity, 143 kWh/t, is the sum of the four plants' consumption (gross), while the gases' CO2 is all counted. Both make this an upper view for steel.
- **By-products are not allocated.** BF slag (243 kg/t), steelmaking slags (159 kg/t), coal tar, light oil and sulphur are outputs that carry no burden, so all burdens fall on the steel. This is a deviation from docs/system-model.md section 2, recorded in the dataset's `modelling`: no open prices and no curated rule exist yet.
- **Element balance.** Ores, coals, fluxes, slags and steel are mixtures without a formula in the registry, so `generation.balance` closes only for nitrogen and argon. Those are the inert gases fed and released to air. It says nothing about iron, carbon or calcium, and core warns for the mass outside it (`cheme.lci-mass-outside-balance`). The carbon is balanced in the CO2 formula instead.
- **Emissions are incomplete.** Heavy metals, PAH, PCDD/F and PCB are given per tonne in the BREF but are not exchanges yet, since no flow identity has been chosen. Hot stove and power plant stack emissions are left out (the BREF gives only concentrations), as are diffuse dust and fugitive VOC. Process residues are left out too: dusts, sludges and mill scale are partly recycled to the sinter plant, and the split is not given.
- **Assumed choices.** The flux mixes count as limestone. The converter dolomite counts as raw. All scrap carries the IPCC scrap-iron carbon content. All coke is made on site. Sulphur recovery is chosen among the BREF's three desulphurisation routes. Oxygen and nitrogen volumes are read as Nm3.
- Midpoints of min-max ranges across plants are not averages. Some ranges span more than a factor of ten (CO and dust of the sinter strand, CO of the converter).
- The data are EU plants of 2004 and 2005. `valid_until` is the reference year + 5, 2009, so it has already lapsed.
- Uncertainty: `gsd2 = sqrt(high / low)` where the source gives a range (our convention, capped at 3 for ranges that start near zero), ASSUMED values elsewhere.

## Linking

The product has the registry slug `crude-steel`, not `steel`. That keeps it apart from fabricated steel, such as the sections `asu-1` builds with. Oxygen and nitrogen link the Atlas producer `asu-1` (GOX and GAN) explicitly, burnt lime links `lime-1`, and natural gas links the shared background (`lca/mappings.yaml`). Ores, pellets, coals, oil, dolomite, scrap, ferroalloys, argon and the by-product outputs are reported mapping gaps: their backgrounds are not chosen yet.

## Not counted yet (TODO)

Exported process gas, power and steam; hot stove and power plant stack emissions; heavy metals, PAH, PCDD/F and PCB; diffuse and fugitive emissions; recycled and landfilled residues; water intake and the BF, BOF and casting waste water; other BF injectants; ammonia from the coke oven gas; the pellet plant; hot rolling. The full list is in the dataset's `system_boundary.excluded`.
