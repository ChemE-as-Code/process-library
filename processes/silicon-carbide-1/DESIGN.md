# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/sic_balance.py`; the stream table is
generated: `cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#179.

Run record of this stage (2026-10-28): library branch `case/silicon-carbide-1` from `7da4a74`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core dependencies as stated
in #179 and its last comment (not re-audited against core main in this run): core #370 is
implemented for limestone calcination only (core #387, `cheme process furnace`); its schema
accepts `reaction: calcination-caco3` only, so carbothermal SiC has no furnace energy basis in
core and this case uses a labelled specific-energy basis (D-004). Core #365 (solids and solid
separations) is not used: the sorting of the ingot is a specified split (D-006).

## 1. Route and boundary memo

- **Route**: Acheson process. Silica sand and petroleum coke, mixed with the unreacted mix of
  earlier runs, are piled around a graphite resistor core in a batch electric resistance
  furnace; SiO2 + 3 C -> SiC + 2 CO proceeds through SiO and CO gas (Lima and Tenorio 2011,
  section 1). The CO, the coke volatiles, the coke sulfur and escaping SiO burn partly with air
  over the charge. After cooling, the ingot is broken and sorted by zone: crude crystalline
  (alpha) SiC from the core region, a lower-grade metallurgical fraction, and unreacted mix that
  goes back into the next charge. The crude SiC is crushed and screened.
- **Alternatives not compared numerically**: ESK-type large outdoor furnaces with gas
  collection (same chemistry, the CO used as fuel); the Lely and PVT sublimation routes and CVD
  for semiconductor SiC (other products, other scale); recycling routes such as RECOSiC
  (Fraunhofer IKTS 2023). The Acheson route is the one the issue asks for and the one by which
  practically all abrasive and refractory SiC is made.
- **Boundary** (gate-to-gate): from silica sand, petroleum coke and air at the battery limit to
  crushed crude crystalline SiC at the crusher outlet. Inside: charge mixing and loading,
  Acheson furnaces with transformers, gas burn-off at the charge surface and hood, ingot
  cooling, breaking and sorting, recycle of the unreacted mix with a purge, crushing and
  screening with a bag filter. Outside: sand and coke production and transport, power
  generation, cooling tower, grain processing (acid/alkali washing, magnetic separation, drying,
  sizing into grits), furnace construction and graphite core manufacture, landfill.
- **What crosses the boundary**: SAND, COKE, AIR (raw materials); SIC (product), MET
  (metallurgical-grade co-product); WASTE (purged mix, solid waste); VENT (flue gas), DUST
  (crusher exhaust); POWER, CW, AMB (heat to ambient air, no utility system).
- **Comparisons**: only with Acheson data of the same boundary (crude SiC before grain
  processing). The IPCC/EPA factors are per t of SiC produced; they are used as cross-checks,
  not as inputs, except the CH4 slip (D-006).

## 2. Decisions

## D-001 Route and boundary (2026-10-28)
Decision: Acheson batch resistance furnace route, boundary as in section 1, product crushed crude
crystalline SiC.
Reason: the route of issue #179; practically all bulk SiC is made this way. Grain processing is
product-specific (grit sizes, purity grades) and is left outside so the inventory can feed
several downstream grades.
Rejected: including the wet grain processing (the US plant of EPA 2009 dries its product with
natural gas, section 2.2) without data on it; sublimation and CVD routes (different products).
Assumptions: the graphite core is reused from batch to batch; its make-up is inside the coke
feed (ASSUMED). No salt or sawdust in the charge (historical additives; ASSUMED absent in a
modern charge, to be checked).

## D-002 Capacity, product grade and hours (2026-10-28)
Decision: 5000 kg/h crushed crude crystalline SiC (40 kt/a at 8000 h/a), grade SiC 98.0 wt%,
SiO2 0.8, free C 0.7, oxide impurities 0.5 (ASSUMED). Generic site, country not chosen.
Reason: a normalisation basis for the inventory, not a commercial plant claim (#179 scope
notes). The grade sits inside the 97-99 % SiC that Lima and Tenorio (2011, Fig. 5) report for
the crystalline product of a pilot Acheson furnace; for scale, EPA (2009, section 1) reports
35 kt/a abrasive-grade plus 35 kt/a metallurgical-grade SiC from the one US plant in 2006.
Assumptions: ASSUMED capacity, grade and hours.

## D-003 Batch operation as a time average (2026-10-28)
Decision: the furnaces are batch units in rotation; the flowsheet carries the time-averaged
flows per hour. The heating and cooling phases are steps of one furnace (R101 and H101).
Reason: the LCI per kg and the balance do not depend on the cycle schedule; a batch schedule
(furnace count, power per furnace, cycle) is a later design step.
Assumptions: ASSUMED order of magnitude 30 furnace beds of about 10 MW, heating 1.5-2 days,
full cycle about 10 days (equipment list, R-101); the Lima and Tenorio pilot furnace (6 x 4 x
2 m, 1 MVA) ran about 10 h with about 6000 kWh per test (section 2), which shows the scale
dependence. Mean contents temperature at power-off 1800 K and 323 K when broken (ASSUMED).

## D-004 Furnace energy: labelled specific-energy basis (2026-10-28)
Decision: furnace electricity 7.5 kWh per kg crude SiC (crystalline + metallurgical, 6250 kg/h),
46.9 MW time average.
Reason: `cheme process furnace` refuses carbothermal SiC (only `calcination-caco3`; core #387),
so no predictive furnace energy balance exists in core. The value is inside the 6.3-9.02 kWh/kg
reported for European plants (Mehrwald 1992, quoted by Lima and Tenorio 2011, section 1) and
close to the about 7.15 MWh/t that Fraunhofer IKTS (2023) gives for conventional Acheson
production; the pilot furnace of Lima and Tenorio used 8.9-9.5 kWh/kg (Fig. 4).
Check (scripts/sic_balance.py, lumped): the reaction enthalpy at 298 K (RX1 618 kJ/mol, about
4.3 kWh per kg SiC formed; RX2 700 kJ/mol) takes 26.0 MW (55 % of the power); the sensible heat
of the contents at power-off 11.8 MW (25 %, mean cp 1.3 kJ/(kg K) ASSUMED); the rest, 9.1 MW
(19 %), is the off-gas sensible heat and the furnace losses during heating plus transformer
losses. Lima and Tenorio quote about 6.5 kWh/kg as the thermodynamic requirement (section 1).
Rejected: a per-kg-SiC-formed basis (it would hide the metallurgical grade's share of the
energy); predicting the energy from a furnace heat-transfer model (no qualified model in core;
#179 asks not to treat the furnace as an ideal gas reactor).
Assumptions: ASSUMED 7.5 kWh/kg; transformer and bus-bar losses 2 % of the furnace power to
cooling water (ASSUMED).

## D-005 Raw materials (2026-10-28)
Decision: silica sand 98.5 wt% SiO2, 0.5 oxide impurities (lumped as Al2O3), 1.0 moisture;
green petroleum coke 85.5 wt% fixed C, 8.0 volatile matter (lumped as CH4), 1.5 S, 0.5 ash
(as Al2O3), 4.5 moisture (all ASSUMED, no supplier assay).
Reason: green petroleum coke is the usual reductant, low in ash (about 0.2 wt%) with sulfur up
to several wt% (Lima and Tenorio 2011, section 1, citing Narciso-Romero et al. 1999); EPA (2009,
section 5.2) uses a coke carbon content of 90-95 % by default. Our 85.5 % fixed C plus 6 % C in
the volatiles gives 91.5 % total carbon. Volatiles as CH4 is the simplest carrier that lets the
IPCC CH4 factor be reproduced (D-006).
Assumptions: the coke sulfur (1.5 wt%, a low-sulfur grade) sets the SO2 emission one to one; a
3 wt% coke doubles it. Lumping all oxides as Al2O3 and all volatiles as CH4 is a balance device.

## D-006 Material balance model (2026-10-28)
Decision: an independent sequential balance (scripts/sic_balance.py) with imposed yields and
splits, closed over the recycle loop; the PFD carries its values as ASSUMED. Parameters:
- product slate: 0.25 kg metallurgical-grade SiC (88 wt% SiC) per kg crude crystalline SiC;
- unreacted mix sorted from the ingot: 3.0 kg/kg recycled, 5 % of it purged; recycle
  composition 4 wt% SiC, carbon factor C/(C+SiO2) 0.39 (Lima and Tenorio report 38-39 % for
  their charges, Fig. 3, and an optimum near 37-38 % from the Nagamori model, Fig. 1; the
  stoichiometric value is 37.5 %); the oxide impurities close through the purge (5.7 wt% in the
  recycle at steady state);
- SiO escaping the charge 0.005 kmol per kmol SiC formed, burnt to silica fume;
- burn-off over the charge: 70 % of the CO burnt, CH4 slip at the IPCC 2006 Tier 1 default
  11.6 kg CH4/t SiC (EPA 2009, Table 4), all sulfur to SO2, air at twice the burn-off
  stoichiometry (hood dilution air not modelled);
- crusher dust 0.2 kg/t after the bag filter.
Result: SiC formed 6033 kg/h (150.5 kmol/h); charge 31.6 t/h, of which SiC formed is 19 %;
per kg crude crystalline SiC (unallocated): sand 1.954 kg, coke 1.361 kg,
purge 0.158 kg, CO2 2.12 kg, CO 0.507 kg, CH4 0.014 kg, SO2 0.041 kg, silica fume 9 g,
electricity 9.63 kWh.
Cross-checks (scripts/sic_balance.py prints them): coke 1.13 kg per kg SiC formed against the
1.14 that the IPCC defaults imply (2.62 t CO2/t SiC over 2.30 t CO2/t coke); CO2 if all gas
carbon were oxidised 2.45 kg/kg SiC against the IPCC 2.62 (-7 %); coke carbon retained in SiC 29 % against "about 35 %" (EPA 2009,
section 2.1).
Rejected: copying the IPCC factors as the inventory (they are country-inventory defaults with
+/-10 % uncertainty and do not split CO from CO2); a Gibbs reactor (#179: a heterogeneous
furnace with steep temperature zones is not an equilibrium reactor).
Assumptions: every parameter above is ASSUMED except where a source is named; the
metallurgical ratio is the most uncertain (the US plant of EPA 2009 reported equal tonnages of
abrasive and metallurgical grade, but its metallurgical grade may include crushed fines).
Review response (2026-10-28-pfd-lci-review#4): two comparisons that rested on search summaries
without a locator (a CO-per-coke factor attributed to the IPCC 1996 guidelines, and a 15 %
conversion attributed to an unnamed hot-model study) were removed rather than kept unaudited;
neither was an input.

## D-007 Reaction and thermodynamic model basis (2026-10-28)
Decision: reactions in process/reactions.yaml as specified conversions (a sourced-range
conversion model): RX1 SiO2 + 3 C -> SiC + 2 CO and RX2 SiO2 + C -> SiO + CO in R101; COX, CH4X,
SOX and SIOX in the burn-off B101. Heats of reaction from NIST-JANAF formation enthalpies (Chase
1998; values recalled, to be checked, so ASSUMED). No property package: no benchmarked package
covers solids or a 1000 K gas with SiO and sulfur (`cheme process props --coverage`); the
flowsheet is not simulated (process/simulation.yaml holds no specs; B101 is not adiabatic, D-008).
Reason: the literature describes the mechanism (SiO2 + C -> SiO + CO, then SiO + 2 C -> SiC +
CO, with beta-SiC from about 1700 C and alpha-SiC from about 2100 C; Lima and Tenorio 2011,
section 1) but gives no kinetics usable at furnace scale; #179 forbids invented kinetics.
Evidence status: conversions, yields and splits are design specifications, cross-checked
against coke-use and emission factors (D-006); no observation of the Acheson ingot zones
(yield per zone, grade per zone) has been read in this run.

## D-008 Utilities and duties (2026-10-28)
Decision: electricity for the furnaces (Q1, D-004), auxiliaries 0.15 kWh/kg (mixing, loading,
handling, hood fans; Q3) and crushing and screening 0.10 kWh/kg (Q4), all ASSUMED; cooling water
for transformer and bus-bar losses (Q2, 2 % of furnace power, ASSUMED); the ingot cools in the
open air (Q5, 11.8 MW to ambient, no fans, no utility system). No steam, no fuel. The furnace
transformers are fed from the grid above 24 kV (ASSUMED; lca/mappings.yaml uses the
high-voltage entry). The ingot is broken and sorted at 323 K, and the sorted and crushed
streams (S9-S13) stay at 323 K: sorting has no energy stream, so it does not cool them
(review R-06; crushing heat neglected).
Burn-off energy (review 2026-10-28-pfd-lci-review#3): B101 is not adiabatic. The burn-off
releases 23.6 MW (COX, CH4X, SOX, SIOX at 298 K from the D-007 formation enthalpies) and S5
brings 2.3 MW (1000 K, mean 1.25 kJ/(kg K), ASSUMED); S7 carries 4.9 MW at 600 K (mean 1.05
kJ/(kg K), ASSUMED); the remaining 21.0 MW leave to ambient as Q6 (scripts/sic_balance.py).
Adiabatic, S7 would leave at roughly 1600-1900 K. Physically Q6 stands for radiation from the
burning charge surface plus the heating of hood dilution air, which is not modelled; so the
S7 flow and temperature (and line FG-101) are a burn-off balance, NOT a stack, duct or fan
sizing basis. A hood design needs the dilution ratio as an input (open item).
Reason: the Acheson plant is an electrical plant; the only fired equipment of the US plant is
the product dryer of the grain processing (EPA 2009, section 2.2), outside the boundary.

## D-009 Lists (2026-10-28)
Decision: the equipment list holds the five items the PFD links (M-101, R-101, B-101, Z-101,
Z-201); the line list only the two gas ducts (solids move by conveyor, crane and mobile plant).
No instruments at this stage. No P&ID (out of scope); the template's DEXPI reference sheet was
not present in pid/.

## D-010 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg crushed crude crystalline SiC at the gate; every foreground
exchange from the balanced flowsheet; mass allocation between crude SiC and metallurgical SiC
(0.80/0.20); every background declared `missing:` with the activity it should link to;
`boundary: cradle-to-gate` (as soda-ash-1, so the feeds are not mapped free).
Reason: both products come from the same batch and are mostly SiC; no prices are recorded, so
economic allocation (more burden on the crude crystalline grade) is the open alternative.
Emissions estimated: CO2, CO, CH4, SO2, silica fume, SiC dust. Declared exclusion
(`emission_exclusions: furnace-pollutants`): NOx, H2S and COS, PAH and other organics of the
green coke, metals in the dust; no abatement of the flue gas is modelled (open furnaces; a
covered furnace with gas collection would change CO and SO2).
Result (per kg crude SiC, after allocation; lca/inventory.csv): sand 1.563 kg, coke 1.089 kg,
electricity 7.70 kWh, cooling water 0.15 kWh, purged mix 0.126 kg to landfill; to air CO2
1.695 kg, CO 0.406 kg, CH4 11.2 g, SO2 32.6 g, SiO2 fume 7.2 g, SiC dust 0.16 g; co-product
0.25 kg metallurgical SiC. `cheme assess lca --balance`: mass, every element (Al, C, H, N, O, S,
Si) and carbon by origin closed (residuals below 0.001 %); energy closure not evaluable (the
chemical energy of the products is not counted). `--coverage`: partial screening carbon
footprint, 9 gaps (5 unmapped backgrounds; CO, SO2, SiO2 and SiC outside the climate method).
What the climate number is (review 2026-10-28-pfd-lci-review#1): the 2.03 kg CO2-eq/kg and its
interval are the DIRECT (scope 1) furnace CO2 and CH4 only, not a carbon footprint; the
electricity (7.70 kWh/kg, the largest exchange), coke, sand, cooling water and landfill are
gaps. Said in the lca.yaml goal and in process.yaml validation.notes.
Fossil CO (review #2): the method (IPCC 2021 GWP100 of the packaged profile) gives CO no
factor, so it stays a gap rather than receiving a project factor. Counted by its atmospheric
oxidation to CO2 (44.01/28.01 = 1.571 kg CO2 per kg CO, stoichiometry), the 0.406 kg CO per kg
would add 0.64 kg CO2-eq, giving 2.67 kg CO2-eq/kg for the direct emission; the design's gas
carbon as CO2 (2.45 kg/kg SiC formed) sits 7 % below the IPCC Tier 1 default (D-006), not 31 %.
Allocation is written as `method: shares` (SIC 0.80, MET 0.20: the mass of S12 and S10), with
`allocation.deviation` stating why the WBCSD price ratio is not applied (no sourced prices);
same numbers as `mass`, but the generated dataset then carries its method, which the library's
Atlas build requires (CI of PR 225).
Open: CPC subclass of the dataset (not guessed); subcompartments of the emissions; a carbon
check of the purged mix (35 wt% C) in the landfill dataset.

## 3. Source register

| source | locator | read | use |
|---|---|---|---|
| Lima, T. C. F.; Tenorio, J. A. S. (2011) Rem: Revista Escola de Minas 64(3) 341-345, http://www.redalyc.org/articulo.oa?id=56419948013 | section 1 (p. 342): mechanism, phases, coke ash/sulfur, 6.5 kWh/kg thermodynamic, 6.3-9.02 kWh/kg European plants (Mehrwald 1992), world output about 750 kt/a (EIPPCB 2006); Fig. 1 (Nagamori model), section 2 (pilot furnace), Figs. 3-5 (carbon factor, kWh/kg, SiC content) | full text read | D-002, D-004, D-005, D-006, D-007 |
| U.S. EPA (2009) TSD Silicon Carbide Production Sector (proposed GHG reporting rule) | section 1 (US output 2006), 2.1 (35 % of carbon in SiC; CH4 from coke volatiles), 2.2 (natural-gas product dryer), 5.1 Table 4 (IPCC Tier 1: 2.62 t CO2/t, 0.0116 t CH4/t; +/-10 %), 5.2 (coke C 90-95 %), 5.3 (four furnace stacks) | full text read | D-002, D-005, D-006, D-008 |
| IPCC (2006) Guidelines Vol. 3 ch. 3.6 | default factors, read through EPA 2009 | not read directly | D-006 |
| Fraunhofer IKTS (2023-06-01) press release "Energy-efficient and low in emissions: silicon carbide recycling with RECOSiC" | conventional Acheson: 7.15 MWh/t electricity, about 2.4 t CO2/t from the carbothermal reduction and 1.8 t from the energy, about 2500 C, furnace runs for days | press release read | D-004 cross-check |
| Ullmann's: Silicon Carbide, doi:10.1002/14356007.a23_749.pub2 | production sections | not audited | lead for the next stage |
| NIST-JANAF Thermochemical Tables (Chase 1998) | formation enthalpies of SiO2, SiC, CO, SiO, CH4, CO2, SO2, H2O | recalled, to be checked | D-007 |

No text, table or figure of these sources is reproduced; facts are restated in our own words.

## 4. Registry entries missing in `chemicals/chemicals.yaml` (for the consolidated PR)

- `silicon-carbide` with grades for crude crystalline SiC (98 wt%) and metallurgical-grade SiC
  (about 88 wt%): product:SIC, product:MET.
- `silica-sand` (or `silica` with a sand grade): feed:SAND.
- `petroleum-coke` (green, by mass): feed:COKE.
- `carbon-monoxide`, `sulfur-dioxide`: emissions named in the manifest notes.
- Shared `lci/mappings.yaml` technosphere entries: silica sand (market for silica sand, per kg)
  and petroleum coke by mass (the existing `coke` entry is metallurgical coke); the elementary
  crosswalk lacks silica fume and SiC dust as particulate emissions.
- Family: `inorganic-chemicals` is used (ISIC 2011); a carbides or abrasives family could be
  considered.

## 5. Open inputs and gated steps

- **Gated (core)**: predictive furnace energy for carbothermal SiC (core #370 implemented for
  CaCO3 calcination only, core #387; `reaction` accepts `calcination-caco3` only) -> labelled
  specific-energy basis (D-004). Energy closure of blocks needs stream enthalpies of solids and
  of the hot furnace gas: no benchmarked property package, so `balanced.energy-closure` stays
  missing. Ingot sorting as a predicted solid separation (core #365) is not attempted.
- **Calculation maturity**: `cheme maturity` reports none: feed flows and the specified
  conversions and splits are ASSUMED, not given with a source (sourced.boundary,
  balanced.model-basis fail; every balance closes). The manifest keeps the lowest claim,
  concept, as soda-ash-1 does.
- **Open inputs**: furnace zone yields and grades (crystalline / metallurgical / unreacted),
  metallurgical ratio, recycle and purge ratios; coke assay (S, volatiles); sand assay; specific
  energy for the chosen furnace size; CO burn-off and gas collection; NOx, H2S/COS, PAH and dust
  emission factors (the LVIC-S BREF 2007 SiC section and Norwegian plant permits are the next
  sources to audit); furnace count, power and cycle; product prices for economic allocation.
- **Recommended next stage**: audit the LVIC-S BREF SiC section and Ullmann's production
  chapter for zone yields, energy and emission ranges (exact locators), replace the ASSUMED
  parameters where a source supports them, add `process/reaction-evidence.yaml`, then link the
  backgrounds (electricity, sand, coke, landfill) for a screening carbon footprint.
