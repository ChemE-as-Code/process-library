# Vinyl chloride monomer by the balanced EDC process

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

This entry is a manifest and an LCI dataset only. It has no flowsheet and no simulation. The basis is one tonne of VCM. Ethylene is chlorinated directly with chlorine and oxychlorinated with the recycled HCl and oxygen. The EDC is purified and cracked thermally to VCM and HCl, and all of the HCl goes back to oxychlorination, so no EDC or HCl crosses the boundary.

## Why this route

The LVOC BREF (section 11.2.2) says about 90 % of the world's plants run this balanced process. It is also the IPCC 2006 default for EDC/VCM (Table 3.11). The dataset assumes oxygen-based oxychlorination: about two thirds of the EU installations in the BREF data collection use pure oxygen, and nearly all built since 1990 do (section 11.4.1.1.2). Thermal cracking is the only cracking route used in Europe. The plants are large and highly automated (section 11.1), and all the reaction and separation steps run continuously. The periodic steps are furnace decoking, as seldom as once every one or two years (section 11.2.3.1), and, for fixed-bed oxychlorination only, the replacement of the catalyst charge (section 11.3.6); fluidised beds lose catalyst continuously.

Routes not modelled:
- air-based oxychlorination;
- unbalanced units that import or export EDC or HCl (`hydrogen-chloride-1` would supply HCl to these; a balanced unit needs none);
- the acetylene route, which the BREF says Chinese plants still use;
- the emerging ethane and Deacon routes (section 11.5).

## How it is built

`lca/datasets/vcm-balanced-oxygen.yaml` is a hand-written Tier 1 dataset. Every amount is the `formula` of its `parameters`, and `generation.balance` records the closed C, H, Cl and O balance.

| Item | Source | How |
|---|---|---|
| Ethylene, chlorine | LVOC BREF Table 11.12 | given: 465 kg/t (midpoint of 0.46 to 0.47) and 590 kg/t (one value) |
| Residues | chlorine balance | the chlorine above stoichiometry, modelled as 1,1,2-trichloroethane: 28.5 kg/t |
| Oxygen | stoichiometry | VCM, residues and vent CO2: 139 kg/t |
| Vent CO2 | IPCC 2006 Table 3.17 | 8.3 kg/t from deep oxidation in oxychlorination |
| Unconverted ethylene | ethylene balance | the rest, 7.5 kg/t, burnt in the vent treatment (ASSUMED) |
| Fuel, steam, electricity | LVOC BREF Table 11.13 | midpoints: 3.8 GJ/t natural gas, 1.0 GJ/t steam, 160 kWh/t |
| Furnace NOx and CO | LVOC BREF Table 11.2 | median concentrations times our calculated dry flue gas of methane at 3 % O2 |
| Combustion CH4 | IPCC 2006, p. 3.77 | 5 g/GJ of natural gas |
| Fugitive EDC and VCM | LVOC BREF Table 11.7 | medians, 8 and 7 g/t |
| Effluent, coke, spent catalyst, sludge | LVOC BREF 11.3.2 and 11.3.6 | midpoints |

Direct CO2 comes out at 0.240 t/t. That is below the IPCC default of 0.294 t/t, which averages older plants, and above the EU ETS mean of the 10 % best plants, 0.171 t/t. Oxygen (0.139 kg/kg) and residues (28.5 kg/t) fall inside the BREF's ranges (`benchmarks/chlorinated-organics.yaml`). Those two are calculated, not transcribed, but they come from the same document as the feeds. So they check the model's closure; they are not independent data.

## What is weak

- **All excess chlorine goes to the residues.** This is a modelling choice. Real plants also lose chlorine as HCl or NaCl in scrubber effluents, or sell hydrochloric acid. Many sites burn the residues on site and recycle the recovered HCl to oxychlorination (section 11.2.2.6). Our reading is that the source's 0.59 kg/kg is the plants' net chlorine use, so that recovery is already inside it: modelling it would move the excess chlorine from the organic residues to scrubber effluents, and would leave the chlorine feed unchanged. Here the residues are an output to treatment.
- **The vent treatment's emissions are not counted.** The source gives concentrations (HCl, Cl2, PCDD/F, VOC) but no flows. The ethylene burnt there is a balance residual.
- **Steam is gross.** The 0.43 to 3.5 GJ/t of heat recovery in the same section is not credited.
- **Electricity may be high.** The source says oxygen-based plants use less, but the dataset takes the midpoint of all plants.
- **Several consumables are missing.** Sodium hydroxide, ferric chloride, hydrogen and nitrogen are named by the source but not quantified, so they are TODO.
- **Some choices are ours.** Midpoints and medians are not recommended by the source. Pure methane as the fuel is ASSUMED, as is the LHV basis of the fuel range.
- **The data are dated.** The BREF data collection is about 2010 to 2014, and the IPCC factors rest on the 2003 BREF. `valid_until` is the reference year + 5, 2018, so it has already lapsed.

## Linking

- The product has the registry slug `vinyl-chloride`. A PVC entry would consume it, but none exists yet.
- Ethylene links to `ethylene-1`, chlorine to `chlor-alkali-1` and oxygen to `asu-1` GOX (`lca/mappings.yaml`).
- Residues, coke, sludge and catalyst are reported mapping gaps, because the library has no hazardous-waste treatment entry yet.

## Not counted yet (TODO)

Heat recovery, on-site residue incineration with HCl recovery, the vent treatment's emissions, washing and scrubbing chemicals, the effluent's pollutants and other chlorine losses. The full list is in the dataset's `system_boundary.excluded`.
