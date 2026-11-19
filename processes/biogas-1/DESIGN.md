# Design decisions

Biogas and biomethane, concept stage (issue ChemE-as-Code/process-library#462, coverage rank 55
`biogas`). One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in the YAML files and in `scripts/balance.py`; this file keeps the reasons.

## Source register

The sources read for this entry (SRC-1 to SRC-5), and one method reference that was not read and
gives no number (SRC-6, its bibliographic data checked on Crossref); facts and numbers are
restated in our own words with their locator. No table, figure or text is copied.

| id | source | access | what it gives here |
|---|---|---|---|
| SRC-1 | FNR, Fachagentur Nachwachsende Rohstoffe (ed.) (2010; English edition 2012) *Guide to Biogas: From production to use*, Guelzow; the GIZ copy on energypedia (energypedia.info, File:Guide_to_Biogas-_From_Production_to_Use.pdf) | free download; copyright of the publisher (facts only) | Table 2.3 (methane content of the gas of digestible carbohydrate, fat and protein); Table 2.6 (composition of biogas); Table 3.36 (emergency flares); section 5.1.3 (mesophilic range 37-43 C; little heat from the digestion); Tables 3.30 and 3.31 (insulation of digesters); Table 5.9 (toxicity of H2S); Table 6.2 (biological desulphurisation in the digester); section 6.1.3 and Table 6.7 (upgrading methods, water scrubbing described without design figures, section 6.1.3.2); section 8.1 with Tables 8.1 to 8.8: the model plants (section 8.1.3: the wastes delivered hygienised; two-stage digestion from 350 kWel), plant VII (500 kWel, manure and biowastes): substrates (Table 8.3, read from the plant's gas yield, D-002), their DM, VS, biogas yield and methane content (Table 8.2), the design rules (Table 8.4: organic loading, two-stage operation, agitator power, 6 months' digestate storage, 8000 h), the plant's volumes, retention time, gas yield and methane content (Table 8.7); plant X's 5 % of the biogas for digester heating and 2 % methane loss (Table 8.8), its gas processing by high-pressure water scrubbing (Table 8.5) |
| SRC-2 | Bauer, F.; Hulteberg, C.; Persson, T.; Tamm, D. (2013) *Biogas upgrading - Review of commercial technologies*, SGC Rapport 2013:270, Svenskt Gastekniskt Center, Malmoe; Lund University repository (lup.lub.lu.se, record 3512502) | open report (facts only) | section 2.3: membrane separation; section 2.3.1 (p. 30): the gas cleaned before compression, its water removed by cooling and condensation so that none condenses during compression, H2S on activated carbon, 6-20 bar(a), oil-lubricated compressors with oil separation; the three designs (iii: three stages with recycle), 99-99.5 % methane recovery for design (iii), water leaves with the CO2; section 2.3.3 (p. 33): 0.20-0.30 kWh/Nm3 raw biogas guaranteed by the manufacturers, the power mainly the compressor's; section 3.1: 98 % CH4 guaranteed by most membrane suppliers; section 3.2: power of the technologies (membranes by reference to 2.3.3), and (p. 52) the compressors' excess heat as a heat source for the digesters or the substrate; section 3.3: methane slip (membranes about 0.5 % with design iii, water scrubbers about 1 %, PSA 1.8-2 %, amine 0.1 %) |
| SRC-3 | Ungerank, M.; Baumgarten, G.; Priske, M.; Roegl, H. (Evonik Fibres, priority 2010-07-01) US 8 999 038 B2, *Process for separation of gases*, Google Patents | open patent | the three-stage cascade (feed stage, retentate stage, permeate stage, stage 2 permeate and stage 3 retentate recycled to the compressor); Examples 1 to 4: 50/50 CH4/CO2 at 25 bar and 20 C to 98.5 % CH4 (99.7 % in Example 4) with 0.5-1.0 % CH4 in the off-gas, total recycle 31-42 % of the feed at a mixed-gas selectivity of 45 |
| SRC-4 | Wagner, W.; Pruss, A. (2002) The IAPWS formulation 1995 for water, J. Phys. Chem. Ref. Data 31, 387, as implemented in the `chemicals` package 1.5.2 (Caleb Bell, MIT), `iapws95_Psat` | open formulation; package value, a single fact with its source (library ADR 0037) | the vapour pressure of water at 313.15 K (7.385 kPa), 303.15 K (4.247 kPa) and 283.15 K (1.228 kPa); the saturation temperature for the gas's dew point at 1600 kPa(a) (`iapws95_Tsat`); the heat of vaporisation of water by the Clausius-Clapeyron equation on the same formulation (`iapws95_dPsat_dT`, `iapws95_rhol_sat`, `iapws95_rhog_sat`): 2406 kJ/kg at 313.15 K, 2430 kJ/kg at 303.15 K, 2477 kJ/kg at 283.15 K (D-007, D-008) |
| SRC-5 | The `chemicals` 1.5.2 package (Caleb Bell, MIT) through `cheme chemistry thermo`: ideal-gas formation enthalpies from the Active Thermochemical Tables (method `ATCT_G`), standard entropies from the CRC Handbook table packaged as `heat_capacity.CRC_standard_data` (method `CRC`), ideal-gas heat capacity coefficients of Poling, Prausnitz and O'Connell, *The Properties of Gases and Liquids*, 5th ed. (`heat_capacity.Cp_data_Poling`), and critical temperatures, pressures and acentric factors from the NIST REFPROP values packaged as `miscdata.heos_data` (method `HEOS`) | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The CRC Handbook, Poling et al. (a licensed book), the ATcT and REFPROP were not read here | dHf_298, S_298, the five cp_R coefficients, Tc, Pc and omega of CH4, CO2, H2O, O2 and N2, printed in process/materials.yaml; used for the boiler's duty (D-008) and the chiller's and after-coolers' heat (D-007) |
| SRC-6 | Buswell, A. M.; Mueller, H. F. (1952) Mechanism of methane fermentation, Ind. Eng. Chem. 44(3), 550-552, doi:10.1021/ie50507a033 (title, authors, volume, issue and pages checked on Crossref, 2026-11-19) | method reference only, not read, no number taken: the stoichiometry is the element balance of complete degradation to CH4 and CO2, written out in our own form in process/reactions.yaml | the overall stoichiometry of complete anaerobic degradation of CnHaOb |

Read but not used for numbers: Seruga, Krzywonos and Wilk (2018), *Molecules* 23, 3146 (CC BY
4.0): a full-scale thermophilic dry digestion of the organic fraction of MSW (rejected as the
basis, D-001). Not read (blocked or paywalled), so not used: Banks et al. (2011), the Ludlow
food-waste digester (Bioresource Technology 102, 612); Angelidaki et al. (2018), the review of
biogas upgrading (Biotechnology Advances 36, 452); the Waste Treatment BREF.

## Core and library models checked

- **Core's QSDsan integration** (core 0e85885, #254; core ADR 0065): `process/simulation.yaml`
  may name a project's own Python worker run in a separate QSDsan interpreter
  (`CHEME_QSDSAN_PYTHON`); core validates and stores the stream results. Core ships no
  biological model: the worker and its model are the project's. The library's QSDsan entry
  `wwtp-a2o` is an ASM2d activated-sludge waterline (seven reactors and a clarifier, no sludge
  line and no digester), and `utility-wwtp` is a Tier 1 LCI dataset. Neither provides an
  anaerobic digestion model (ADM1) to use (L-1).

## D-001 Route: wet co-digestion of slurry and biowastes, membrane upgrading to biomethane (2026-11-19)

Decision: the FNR model plant VII (cattle slurry with hygienised catering waste, grease trap
waste and biowaste; two-stage mesophilic wet digestion in stirred tanks) as the digestion, and
its biogas upgraded to grid-quality biomethane in a three-stage membrane unit (SRC-2 design iii,
SRC-3), instead of the plant's CHP engine. The digestate is stored and spread as fertiliser
(D-010).

Reason: plant VII is a complete, internally consistent design from one open source (substrates,
yields, volumes, retention and gas output, SRC-1 Tables 8.2 to 8.7), whose gas yield and methane
content the lumped model reproduces exactly (D-004); its feeds are wastes and a manure, so the
LCI needs no crop background. Upgrading gives a product, methane, that the library's consumers
already take (the coverage item's chemical; steam generation and hydrogen as consumers of
natural gas), and the membrane route has open performance data (SRC-2) and an open patent
(SRC-3).

Rejected:
- **CHP engine on site** (plant VII as built): the product would be electricity and heat, which
  the library does not trace by chemical; the coverage item names upgrading as a variant; the
  CHP is a later case (the same digestion, a different block).
- **Energy-crop plant X with water scrubbing** (SRC-1 Tables 8.5 and 8.8, the guide's only
  gas-processing plant): maize silage needs a crop-production background the library does not
  have (a gap the size of the feed), and SRC-1 describes water scrubbing without design figures
  (section 6.1.3.2).
- **Sewage sludge digestion at a WWTP**: no open, complete design was read; it would pair with
  utility-wwtp later.
- **Dry thermophilic digestion of MSW organics** (Seruga et al. 2018): a plug-flow dry process
  with sorting rejects and no VS data given; less suited to a closed lumped balance.
- **Water scrubbing, PSA, amine scrubbing** for the upgrading: similar power (SRC-2 section 3.2),
  but water scrubbing and PSA slip 1 % and 1.8-2 % of the methane (section 3.3) against
  membranes' 0.5 %; amine scrubbing needs about 0.55 kWh/Nm3 of heat at 120-150 C, which this
  plant would have to raise from biogas.

Assumptions: the wastes arrive hygienised (as SRC-1 assumes for plant VII, section 8.1.3), so
no pasteurisation unit is in the boundary.

## D-002 Capacity and operating hours (2026-11-19)

Decision: plant VII's substrates as they are, 22 100 t/a (4000 t cattle slurry, 8000 t catering
waste, 4600 t grease trap waste, 5500 t biowaste) over 8000 h, 2762.5 kg/h.

Reason: the source's design point. Table 8.3's columns do not survive text extraction cleanly;
the cattle slurry of plant VII was read as 4000 t because with it the four substrates' standard
yields (Table 8.2) sum exactly to the plant's 1 735 468 m3/a of Table 8.7.

Rejected: scaling the plant up: no open source gives the economics of scale used to pick
another size; the result per kg does not depend on it.

## D-003 Digesters: two stirred tanks, 3400 m3, 51 d, mesophilic (2026-11-19)

Decision: two equal concrete digesters, 1700 m3 gross each (plant VII's 3400 m3, Table 8.7;
two-stage operation for plants of 350 kWel and more, section 8.1.3), 19.0 m wide and 6 m high
(ASSUMED), stirred with 25 and 15 W/m3 installed (Table 8.4: 20-30 and 10-20), double-membrane
gas-storage roofs. The retention time on the flowsheet's feed is 51.3 d (source 51 d), the
mixture 18.2 % DM (source 18.2 %).

Reason: the source's design; the two stages are one conversion step in the flowsheet (R101),
because the lumped model has no kinetics to split the conversion between them (L-2).

## D-004 Digestion model: lumped volatile solids and Buswell's stoichiometry, calibrated per substrate (2026-11-19)

Decision: each substrate is water, ash (as SiO2) and volatile solids (DM and VS from SRC-1
Table 8.2). The VS are split into a digestible carbohydrate (CARB, C6H10O5), a digestible fat
(LIPID, triolein C57H104O6) and an inert remainder (RVS). The two digestible fractions per kg
VS are solved so that Buswell's stoichiometry (SRC-6) of their complete conversion gives that
substrate's standard biogas yield and methane content of Table 8.2 (two equations, two
unknowns, `scripts/balance.py`): cattle slurry 0.336 + 0.064, catering waste 0.414 + 0.234,
grease trap waste 0.130 + 0.618, biowaste 0.374 + 0.211 kg per kg VS. The digesters convert
CARB and LIPID completely (reactions AD_CARB, AD_LIP, conversion 1.0); RVS leaves with the
digestate.

Reason: core has no anaerobic digestion model (L-1). The lumps make the element balance close,
put the right gas on the right substrate, and reproduce plant VII's gas (216.93 Nm3/h dry,
1 735 468 m3/a, 0.00 % off) and methane content (60.68 against 60.7 %) without a fitted
parameter beyond the source's own yields. Carbohydrate gives 50 % methane, as Table 2.3 gives
for digestible carbohydrates; triolein gives 70 % (Table 2.3: 68 % for fat). The lumps' gas
yields are not Table 2.3's: complete conversion by Buswell gives 829 l/kg of C6H10O5 and 1443
l/kg of triolein (our arithmetic), against Table 2.3's 790 l/kg VS for digestible carbohydrates
and 1250 l/kg VS for digestible fat, 5 % and 15 % less. So the solved digestible fractions are
model quantities that carry each substrate's Table 8.2 yield, not the digestible share Table 2.3
would imply (that would be larger); the gas, the energy balance and the LCI depend only on the
Table 8.2 yields, not on the split between converted and inert VS.

Rejected: ADM1 in a QSDsan worker (core ADR 0065): it needs the substrates' COD fractions,
kinetics and a dynamic run that no open source read here gives for these substrates, and a
separate numerical environment; for a concept balance it would add parameters, not evidence
(L-1). A protein lump: no source read gives the substrates' protein, and the nitrogen would
need ammonia speciation that core does not model (L-3).

Assumptions: the standard yields are reached in the plant (they are KTBL planning values for
practice, SRC-1 section 8.1.2); 60.6 % of the VS fed is converted, a model result.

## D-005 Temperatures and pressures (2026-11-19)

Decision: substrates and air at 283.15 K (an annual mean, ASSUMED); digesters at 313.15 K
(40 C, inside SRC-1's mesophilic 37-43 C, section 5.1.3); gas space 102.0 kPa(a) (ASSUMED);
the biogas leaves saturated with water at 313.15 K (7.24 mol%, SRC-4; SRC-1 Table 2.6 gives
2-7 vol.% at 20-40 C), so V101 sends 0.619 % of the digester's water to the gas.

## D-006 Membrane upgrading: 99.5 % recovery, 98 mol% product (2026-11-19)

Decision: one component separator M301 for the three-stage unit: 99.5 % of the methane to the
product (SRC-2 sections 2.3.4 and 3.3, design iii; SRC-3's examples give 0.5-1 % CH4 in the
off-gas), CO2 to the product such that it holds 98.0 mol% CH4 (SRC-2 section 3.1; 3.13 % of
the CO2), all water to the permeate (SRC-2 section 2.3.1). Feed at 1600 kPa(a) (ASSUMED, inside
6-20 bar(a)); product at 1550 kPa(a) (ASSUMED) to the grid injection station, whose metering,
odorisation, Wobbe adjustment and any further compression are outside the boundary. The
off-gas is vented without post-oxidation: 0.00476 kg CH4 per kg of biomethane, 40 % of the
screening footprint (D-012).

Rejected: modelling the three stages and the recycle explicitly: core's component separator
takes a split, not permeances; with fixed splits per stage the recycle adds no information
(L-5). A regenerative thermal oxidiser on the off-gas: a later case, if a permit demands it
(SRC-2 section 2.3.4).

## D-007 Gas cleaning and compression (2026-11-19)

Decision: as SRC-2 section 2.3.1 describes, the gas is cleaned before compression. A gas chiller
E-300 (chilled water from a packaged refrigeration unit, ASSUMED) cools the biogas from 313.15 to
283.15 K (ASSUMED) at 101.5 kPa(a), and the separator V-300 drains the condensate (10.2 kg/h,
84.3 % of the water in the gas, SRC-4) to the digestate store. An activated-carbon filter A-301
then takes the H2S, which the balance passes unchanged (no sulphur in the model, L-3). The
oil-injected compressor C-301 takes the gas to 1600 kPa(a), and an air after-cooler E-301 cools
it to 303.15 K (ASSUMED). Its separator V-301 drains the water that saturates out at 1600 kPa(a)
(1.5 kg/h) to the store. The chiller takes 9.81 kW from the gas (Q3: the gas cooled as ideal
gas, SRC-5, and its condensate's heat of vaporisation, SRC-4); its refrigeration unit takes
3.27 kW of electricity at a coefficient of performance of 3.0 (W3, ASSUMED). The after-coolers
and the compressor's oil cooler reject 47.46 kW to the air (Q2). This is the whole upgrading power
W2 (ASSUMED to end there; the share of any permeate vacuum pump is in it), less the 1.74 kW the
gas gains from 283.15 to 303.15 K, plus the 1.00 kW condensation heat at 1600 kPa(a).

Reason: the water is removed before compression so that it does not condense in the compressor
(SRC-2 section 2.3.1). After the chiller the gas holds 1.21 mol% water, a dew point of 59 C at
1600 kPa(a) (SRC-4). The compressor's outlet is at 80 C (S16, ASSUMED), above that dew point, so
no water condenses in the machine or in its oil.

Rejected: biological desulphurisation by air dosing into the digester (SRC-1 Table 6.2): it puts
nitrogen into the biogas, which membranes do not remove (SRC-2 section 3.1), and would dilute
the product. Drying only after compression (the after-cooler alone): the saturated gas from the
digesters (7.24 mol% water) would have a dew point of about 103 C at 1600 kPa(a) (SRC-4), above
the compressor's outlet, so water would condense in the oil-injected compressor. Cooling with
ambient air before compression: on a summer day the gas would leave at about 35 C (ASSUMED), its
dew point at 1600 kPa(a) about 96 C (SRC-4), still above the compressor's outlet.

## D-008 Digester heating by a biogas boiler (2026-11-19)

Decision: the digesters' heat comes from a hot-water boiler B-101 firing part of the raw biogas
(splitter X101). Demand: the substrate warmed by 30 K as water (4.18 kJ/(kg K), ASSUMED), 96.23
kW; the two tanks' losses, 30.47 kW, through walls and floors at U = 0.35 W/(m2 K) (10 cm
of mineral fibre at 0.035 W/(m K), SRC-1 Tables 3.30 and 3.31) and roofs at 1.0 W/(m2 K)
(ASSUMED), 30 K to ambient; and the heat of vaporisation of the water that leaves saturated in
the biogas, 13.61 kg/h at 2406 kJ/kg (SRC-4), 9.10 kW: 135.79 kW. The boiler burns the biogas
completely with 15 % excess air, its flue gas at 423.15 K (ASSUMED), 93.3 % on LHV; the
script's split, 11.12 % of the biogas, makes core's conversion duty of B101 (Q1, 135.79 kW)
equal to the demand. The heat of the digestion itself is neglected (SRC-1 section 5.1.3: very
little heat); it would lower the demand.

Reason: an upgrading plant has no CHP waste heat. SRC-1 gives 5 % of the biogas for digester
heating for plant X (Table 8.8), a plant of energy crops at 30.6 % DM; plant VII's wetter
mixture (18.2 % DM) needs more heat per m3 of gas.

Rejected: heating with the membrane off-gas (0.5 % of the methane, about 6 kW, too lean to burn
alone) or with grid natural gas (fossil carbon in a biogenic product).

Not taken in this base case (open, a later case): heat recovery. The digestate leaves the
digesters at 313.15 K and cools in the store to 288.15 K, giving about 72 kW to ambient (D-010);
a digestate-to-substrate exchanger could return part of it to the 283.15 K substrate, at the
cost of a slurry-to-slurry exchanger. The compressor's oil cooler and after-coolers reject
47.46 kW (Q2, D-007), which SRC-2 (section 3.2, p. 52) names as a heat source for the digesters
or the substrate. Together they could cover much of the 135.79 kW and cut the boiler's share of
the biogas. The base case keeps one heat source and no heat integration, so the boiler's share
is an upper bound.

## D-009 Electricity (2026-11-19)

Decision: the upgrading at 0.25 kWh/Nm3 of raw biogas (SRC-2 section 2.3.3, the middle of
0.20-0.30), 48.21 kW, on C-301 (compressor with the recycle and any permeate vacuum); the gas
chiller's refrigeration unit, 3.27 kW (D-007; counted separately because SRC-2 does not say that
the 0.20-0.30 kWh/Nm3 includes the gas cleaning); the digestion's agitators at the installed 25
and 15 W/m3 (SRC-1 Table 8.4) running half the time (ASSUMED), plus 5 kW for the intake pit,
feed and transfer pumps (ASSUMED), 39.0 kW. 1.028 kWh per kg of biomethane in all.

## D-010 Digestate handling (2026-11-19)

Decision: the whole digestate (2499 kg/h, 12.0 wt% DM in the model) is stored for six months
plus 10 % in a gas-tight covered tank (SRC-1 Table 8.4; 11 000 m3 on the model's flow, plant
VII has 11 400 m3, Table 8.7) and spread on farmland. The store's gas joins the biogas, so the
residual gas is counted in the digesters' complete conversion (D-004). The store's walls are
not insulated (ASSUMED): the digestate cools from 313.15 K to about 288.15 K (S10, ASSUMED) and
gives about 72 kW to ambient (as water, 4.18 kJ/(kg K), D-008). This heat uses no utility and
emits nothing, so it is outside the energy streams; its recovery is open (D-008).

Rejected: separation into a solid and a liquid fraction (screw press) and drying: no open source
read gives the split for this mixture; the farm takes whole digestate.

## D-011 Hazards (concept)

The digesters, the store and the gas line hold a flammable gas (methane, 60.7 mol%) with H2S,
which is toxic (SRC-1 Table 5.9), at near-atmospheric pressure under membrane
roofs: over- and underpressure protection on each roof, an emergency flare for the gas the
upgrading cannot take (SRC-1 Table 3.36), hazardous-area zoning around the roofs, the
compressor and the membrane unit, gas detection (CH4, H2S) in enclosed rooms; the boiler with
flame supervision. The membrane off-gas (S20, 145 kg/h, about 75 Nm3/h) is 98.5 mol% CO2 with
0.78 mol% CH4, below methane's lower flammable limit: its hazard is CO2, an asphyxiant and toxic
at high concentration, and heavier than air, so it collects in pits, the intake pit, trenches
and enclosures. The vent discharges at height, above the roofs and away from occupied, enclosed
and low-lying areas (ASSUMED; height and dispersion to be set in basic engineering), and CO2
detection is added where people may be exposed (the compressor and membrane housing, the
intake-pit building), with the confined-space rules for pits and tanks. No exothermic batch
step: no reactor-hazard screening applies. Methane leaks from the roofs are not estimated (L-4).

## D-012 LCI: cut-off, burden-free wastes, the digestate a recyclable (2026-11-19)

Decision: a preliminary gate-to-gate inventory of the plant's foreground per kg of biomethane
(lca/lca.yaml), cut-off; the screening footprint below adds the cradle-to-gate burden of the
purchased electricity to it. The `boundary` key of lca/lca.yaml is `cradle-to-gate` only so that
core keeps the electricity an open link (its `gate-to-gate` maps every feed free).
The substrates (wastes and a manure) enter burden-free; their collection and hygienisation
belong to their producers. The digestate leaves as a recyclable (its nutrients re-used as
fertiliser), burden-free; core warns that an ordinary by-product above 1 % of the output would
need allocation, and the digestate is the output of a biowaste treatment, which ecoinvent's
cut-off also cuts off. The plant's own emissions are characterised directly: methane and CO2
biogenic (all carbon of the substrates is biogenic, `carbon_accounting`). The electricity is
linked to the library's shared entry `electricity` in the Atlas build (lca/mappings.yaml) and
screened in core with the packaged DESNZ 2026 UK factor as a proxy for the undecided site's
grid. The functional unit is 1 kg of biomethane at 98.0 mol% CH4, 0.947 kg CH4 per kg and 47.4
MJ LHV per kg (S19; 1158.0 kW LHV for 87.99 kg/h). Screening carbon footprint 0.32 kg CO2-eq
per kg of biomethane (6.7 g per MJ LHV): 60 % electricity, 40 % the methane slip. It mixes
characterisation methods (core warns, cheme.lca-method-mix): the DESNZ electricity factor rests
on the AR4/AR5 GWPs, the methane on AR6 GWP100 = 27; the result is a screening figure. It is a
lower bound for the plant's own methane: fugitive leaks are excluded (L-4). A leak equal to the
membranes' slip (4.76 g CH4 per kg) would add 0.13 kg CO2-eq per kg, 40 % of the result; each
1 % of the boiler's methane left unburnt would add 0.03 kg CO2-eq per kg (our arithmetic on the
model's streams).

Rejected: crediting the digestate as mineral fertiliser (substitution): the model has no
nitrogen, phosphorus or potassium (L-3).

Open: the water the wastes bring is not a water withdrawal (core warns, cheme.lca-water-resource);
digester leaks, the boiler's CO and NOx and the spent activated carbon are declared exclusions.

## Core limits

- **L-1** No anaerobic digestion model in core. Core's QSDsan integration (ADR 0065) runs a
  project's own worker; the library has no ADM1 worker, and `wwtp-a2o` covers an activated-sludge
  waterline only. The digestion is a conversion reactor on lumped, calibrated components (D-004).
- **L-2** No kinetics: the conversion does not respond to retention time, temperature or
  loading; the two digester stages are one step (D-003).
- **L-3** No property package or speciation for slurries: no nitrogen (ammonia, ammonium),
  sulphur (H2S), phosphorus or potassium; no CO2 dissolved in the digestate; no enthalpy of the
  slurries, so the substrate's heat-up is the script's (D-008).
- **L-4** Fugitive methane (roof leaks, pressure relief, flaring) is not estimated.
- **L-5** The membrane unit is one component separator with a split; core has no gas-permeation
  model (permeances, stage cuts, recycle), so pressure and membrane area do not change the split
  (D-006).
- **L-6** The boiler's duty is core's conversion-step duty on ideal-gas enthalpies; its losses
  besides the flue gas (radiation, blow-down) are not counted.
