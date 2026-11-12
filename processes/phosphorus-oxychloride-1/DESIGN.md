# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Phosphorus oxychloride (POCl3), issue ChemE-as-Code/process-library#135. Concept stage: design
basis, balanced BFD/PFD and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout,
HAZOP, TEA, datasheets.

Starting point (2026-10-28): library `main` at cc5624f, cheme-as-code 0.8.0 (pyDEXPI 2.1.0).
The core issues on property/phase and reaction-energy qualification and on electrolytes
could not be opened from this session (`gh` cannot resolve them in ChemE-as-Code/core); their
state is taken from what cheme 0.8.0 does: `cheme process props --coverage` has no package for
any stream holding PCl3, POCl3, P4, Cl2 or the caustic liquor, so the gate is real for this case
(D-006).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage given was read
in this session (through the Google Patents text, which has no paragraph numbers).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US4183905A (1980) Producing phosphorus oxyhalide, https://patents.google.com/patent/US4183905 | description and claims 3-6: vertical column with two reaction zones and restricted back-mixing; upper zone about 40-95 C (preferably 50-90), lower zone about 30-50 C (preferably 35-40, example 40 C); cooling-water jacket, most intensive cooling where PCl3 meets the oxygen; 800-1000 BTU to remove per lb of PCl3 reacted; PCl3:O2 feed 8.56-7.15 by mass; excess O2 withdrawn overhead 0-20 % of stoichiometric (preferably 1-10 %), vented to a scrubber or reused; vapour with about 50 % or more PCl3 above the liquid can explode; example near-complete conversion (about 9.47 of 9.48 parts of feed leave as POCl3) | read; patent document (facts only) | D-005, D-011, heat of reaction cross-check |
| SRC-2 | US5183649A (1993) Production of phosphorus compounds, https://patents.google.com/patent/US5183649 | description and examples 1-4: P, Cl2 and O2 to PCl3/POCl3 in a liquid loop with gas separator; mixer inlet 30-80 C, reaction zone outlet 50-110 C; about atmospheric pressure (up to about 10 atm); circulating liquid as heat sink with coolers, loop temperature difference 10-50 C for products with 10 % or more POCl3; prior art with excess oxygen has a large vapour phase and an explosion risk; poly(phosphoryl chloride) by-product 1-10 % in its loop; product separated by fractional distillation, still bottoms recyclable | read; patent document (facts only) | D-005, D-008, D-011 |
| SRC-3 | CN115259114B (2023) Continuous production process of phosphorus trichloride, https://patents.google.com/patent/CN115259114B/en | disclosure items 1-8, example 1: molten yellow phosphorus held at 55-60 C under a water seal, phosphorus mud 0.2-0.5 wt%; P:Cl2 mass ratio 1:3.40-3.45 (slight P excess, against PCl5); reactor outlet 140-157 C under pressure, flash to PCl3 at 74-78 C; condenser outlet 30-35 C; tail-gas condenser on brine at -7 to -5 C, then water and alkali washing of the remaining gas; PCl3 99.5-99.8 wt%; 50 kt/a plant in example 1 | read; patent document (facts only) | D-003, D-004, D-007 |
| SRC-4 | Ullmann's Encyclopedia of Industrial Chemistry, Phosphorus Compounds, Inorganic, doi:10.1002/14356007.a19_527 | - | not read (licensed); listed by the issue as route reference lead | reference lead only |
| SRC-5 | PubChem CID 24813 (phosphoryl chloride), https://pubchem.ncbi.nlm.nih.gov/compound/24813 | identity | listed by the issue; identity only | component identity |
| SRC-6 | chemicals 1.5.2 and thermo 0.6.1 packages of core's environment (open-source, MIT; the versions core pins), through `cheme chemistry thermo` and `thermo.Chemical` in scripts/balance.py: the gas and liquid formation enthalpies of PCl3 and POCl3 and the standard entropies of every gas from chemicals' packaged CRC Handbook table `heat_capacity.CRC_standard_data` (from the CRC Handbook of Chemistry and Physics, 2014 edition as chemicals cites it; a licensed book, not read here); the gas formation enthalpies of Cl2, O2, Ar and water from its Active Thermochemical Tables 1.112 data (`ATCT_G`); white phosphorus's liquid formation enthalpy from its NIST WebBook data (`WEBBOOK`); the normal boiling points of white phosphorus, PCl3 and POCl3 from its packaged CRC inorganic table (`miscdata.CRC_inorganic_data`); ideal-gas cp from its `heat_capacity.Cp_data_Poling` polynomials (Poling, Prausnitz and O'Connell, The Properties of Gases and Liquids, 5th ed.; a licensed book, not read here: Cl2, O2) or fitted to thermo's WEBBOOK_SHOMATE (PCl3, POCl3) and HEOS_FIT (water) correlations; critical constants by the methods printed per component in process/materials.yaml; PCl3's vapour pressure and heat of vaporisation from thermo's VDI_PPDS correlation, whose coefficients thermo takes from the VDI Heat Atlas, 2nd ed. (Springer 2010; a licensed book, not read here); POCl3's vapour pressure from thermo's ANTOINE_WEBBOOK (NIST WebBook Antoine constants) and its heat of vaporisation by Clausius-Clapeyron from that; water's vapour pressure from IAPWS-95 | printed per component in process/materials.yaml; scripts/balance.py: liquid formation enthalpies PCl3(l) -319.7, POCl3(l) -597.1 kJ/mol, white P(l) +0.62 kJ/mol per atom; vapour pressures and heats of vaporisation of PCl3 and POCl3 | open-source packages queried; single values, facts only. PCl3's VDI_PPDS values are not open data; they are single facts from coefficients a package bundles, with their source named (library ADR 0037) | reaction heats, vent condensers, column duties |
| SRC-7 | processes/chlor-alkali-1 (this library) | process/flowsheet.yaml stream S42: dry chlorine, 400 kPa(a), 313 K, 99.19 wt% Cl2, 0.81 wt% O2 | library, internal | chlorine feed (D-003) |
| SRC-8 | processes/asu-1 (this library) | process/flowsheet.yaml streams S7/S8: GOX 99.71 mol% O2, 0.29 mol% Ar, pipeline at 31 bar(a) | library, internal | oxygen feed (D-003) |

The issue's handoff asked not to search for published "answers"; no benchmark plant figures
were looked for or used. The capacity is a concept choice, not a published plant.

## D-001 Route and boundary (2026-10-28)
Decision: POCl3 by liquid-phase oxidation of PCl3 with gaseous oxygen (SRC-1, SRC-2), the PCl3
made inside the boundary by chlorinating molten white phosphorus (SRC-3), followed by two-column
distillation and a caustic scrubber for the reactor vents. Boundary feeds: molten white
phosphorus, chlorine, oxygen, caustic soda 50 wt%, process water, electricity, LP steam; utility
returns: cooling water, chilled water. Wastes: distillation residue (incineration), spent
scrubber liquor (wastewater treatment), scrubbed vent gas (stack).
Reason: the case brief prescribes the oxidation route. PCl3 synthesis is put inside the boundary
because (a) both feeds of that step are on site: the chlorine of chlor-alkali-1 can be used as
delivered, its 0.8 wt% oxygen simply makes a little POCl3 that is product anyway, and (b) PCl3 is
a hazardous, moisture-sensitive intermediate that is in practice made next to its consumer
(SRC-2 makes both in one loop); the boundary then starts at elemental phosphorus, the common
precursor of all phosphorus chlorides, which a later library process (thermal phosphorus) can
supply.
Rejected: PCl3 as a purchased boundary feed (would hide the chlorine demand, 0.70 kg/kg, behind
an unmodelled intermediate); the one-loop P + Cl2 + O2 process of SRC-2 (gives PCl3/POCl3
mixtures and 1-10 % poly(phosphoryl chloride), more distillation and residue); oxidation of PCl3
with SO2Cl2 or with P4O10 (other POCl3 routes, not the brief's).
Links to other library processes: chlorine and caustic soda from chlor-alkali-1, oxygen from
asu-1, steam from utility-steam-ng-boiler, cooling water from utility-cooling-tower, chilled
water from utility-chiller. White phosphorus: no library process (electrothermal furnace).

## D-002 Capacity, product and operating hours (2026-10-28)
Decision: 4000 kg/h distilled POCl3 (32 kt/a at 8000 h/a, ASSUMED), to storage at 308 K.
Product target >= 99.9 wt% POCl3, <= 0.1 wt% PCl3 (ASSUMED); the balance gives 99.998 wt% and
21 ppm(wt) PCl3.
Reason: no traceable published plant basis was chosen (issue note); a few-ten-kt/a unit is a
plausible scale for a merchant phosphorus-chloride plant (SRC-3 describes a 50 kt/a PCl3 plant).
The LCI is per kg and does not depend on the scale.
Open: commercial grade specifications (Fe, As, colour, moisture) not modelled.

## D-003 Feed specifications (2026-10-28)
Decision: molten white phosphorus at 333 K, 400 kPa(a), modelled as pure P4 (SRC-3: held at
55-60 C under water, pumped at 0.4-0.6 MPa). Chlorine as delivered by chlor-alkali-1 (SRC-7),
not liquefied. Oxygen from asu-1's GOX pipeline (SRC-8), let down to 200 kPa(a).
Assumptions: the phosphorus is free of water (decanted); its arsenic, organic and inorganic
impurities (phosphorus mud, 0.2-0.5 wt% in SRC-3) are not modelled (open input: they leave as a
filter mud and, for arsenic, partly with the PCl3; LCI exclusion `phosphorus-mud`).

## D-004 PCl3 synthesis (R-101) (2026-10-28)
Decision: an agitated reactor-still holding boiling PCl3 (about 349 K, 115 kPa(a)) with a small
phosphorus heel; molten P4 and chlorine fed below the liquid; the reaction heat boils PCl3,
condensed in the reflux condenser E-101 on cooling water; PCl3 drawn off to V-101. Conversion
model: the P4 fed is converted completely at steady state (key P4, 1.0); chlorine fed with
0.05 % molar excess, which leaves with the vent (ASSUMED). 99 % of the O2 in the chlorine is
taken up as POCl3 (ASSUMED). Agitator allowance 11 kW (ASSUMED).
Reason: SRC-3 keeps a slight phosphorus excess to prevent PCl5 and reports its P:Cl2 ratio as
the stoichiometric 1:3.434; a conversion model with the phosphorus key reproduces that at
steady state without a modelled heel. A conventional boiling still is the simplest arrangement
that removes the heat by evaporation; SRC-3's pressurised microchannel reactor raising
130-150 C steam is an energy-recovery option for later (it would turn 2.4 MW of cooling-water
duty into low-pressure steam).
Rejected: chlorine excess (makes PCl5); liquefying the chlorine first (the O2 is harmless here).
Heat: 1281.3 kJ per mol P4 (liquid PCl3 from molten P4 and gaseous Cl2 at 298 K, SRC-6) plus
277.4 kJ per mol of the PCl3 oxidised by the chlorine's O2 gives 2443.2 kW to cooling water;
sensible heat of the feeds neglected (< 2 %). (Corrected from 2388.7 kW, which counted the
oxidation heat per mol O2 instead of per mol PCl3: review 2026-10-28-pfd-lci-review#2.)

## D-005 PCl3 oxidation (R-201) (2026-10-28)
Decision: liquid PCl3 oxidised with 5 % molar excess oxygen (inside the preferred 1-10 % of
SRC-1) in a loop reactor at 313-363 K and 130 kPa(a) (SRC-1 zones 30-95 C; SRC-2 50-110 C, about
atmospheric); the liquid circulates through the cooler E-201 (cooling water) with a 20 K rise
(inside SRC-2's 10-50 K). Conversion model, PCl3 conversion 99.5 % per pass (ASSUMED; SRC-1
aims at substantially complete conversion in one reactor); the unconverted PCl3 is recycled from
C-301.
Heat: 277.4 kJ per mol PCl3 (liquid phase, SRC-6), within the 255-320 kJ/mol implied by
SRC-1's 800-1000 BTU/lb; 1912.3 kW. Core's conversion reactor gives -1861.6 kW on its ideal-gas
basis (dHr -271.5 kJ/mol): the 2.7 % difference is the vaporisation terms that the ideal-gas
basis cannot carry.
Circulation: 382 t/h through E-201 (scripts/balance.py), pump power 36 kW, the largest
electricity user.
Not a kinetic model: residence time, oxygen mass transfer and reactor volume are not set (no
kinetics chosen; the reaction is described as very fast and exothermic in SRC-1).

## D-006 Balance method and what core can and cannot calculate (2026-10-28)
Decision: the reactors R101 and R201 and the mixers M201, M401 are solved by `cheme process
propagate --fill` (calculated, element balances and extents checked). The vent condensers
V101/V201, the columns C301/C302 and the scrubber T401 have their outlets from the independent
script scripts/balance.py (`cheme run scripts/balance.py`), entered as ASSUMED with that source:
Raoult's law with thermo vapour pressures for the vents, specified splits for the columns,
specified destruction for the scrubber; the PCl3 recycle is converged in the script.
Reason: no property package of core 0.8.0 covers PCl3, POCl3, white phosphorus, chlorine with
them, or the caustic liquor (`cheme process props --coverage`: every stream unsupported), and
DWSIM simulation needs a qualified package (the liquor needs electrolyte support). The energy
balance is therefore not evaluable in core (`cheme process energy`: not-evaluable for every
block); duties come from the script.
Result: the script's overall balance closes to 0.0065 kg/h on 4088 kg/h (molar-mass rounding);
every block and step closes in `cheme process streams`; phosphorus atoms close exactly; 99.44 %
of the phosphorus reaches the product (0.50 % residue, 0.06 % to the scrubber).

## D-007 Condensers and refrigeration (2026-10-28)
Decision: reflux condenser of R-101 and the column condensers on cooling water 298/308 K; vent
condensers E-102 and E-202 cool the vents to 283 K on chilled water 278/283 K.
Reason: 283 K keeps clear of the 274 K melting point of POCl3 (SRC-6), which rules out the
brine at -7 to -5 C that SRC-3 uses for its PCl3-only tail gas. The vent duties are tiny
(0.05 and 0.3 kW) because the non-condensable flows are small; the chloride carried to the
scrubber is 0.27 kg/h PCl3 and 2.0 kg/h POCl3.

## D-008 Distillation (2026-10-28)
Decision: C-301 light-ends column takes 99.5 % of the PCl3 overhead in a 50 mol% distillate
(36 kg/h) recycled to R-201, reflux ratio 3; C-302 takes the POCl3 overhead (product) and purges
0.5 % of its feed as residue to hazardous-waste incineration, reflux ratio 0.5. LP steam at
400 kPa(a) (417 K) on both reboilers, 38 K above the POCl3 boiling point. All splits and reflux
ratios ASSUMED; constant molar overflow; liquid cp 0.9 kJ/(kg K) ASSUMED (the thermo liquid heat
capacities of PCl3/POCl3 looked implausibly low and were not used). Heats of vaporisation: PCl3
from thermo's correlation (within 1-6 % of its own vapour pressure over 283-379 K); POCl3 from
the Clausius-Clapeyron slope of thermo's vapour pressure (34.6 kJ/mol at 378.9 K, 37.0 kJ/mol at
298 K), because thermo's POCl3 correlation (27.5 and 30.3 kJ/mol) is 20-26 % below both that
slope and the 38.6 kJ/mol at 298 K implied by the CRC formation enthalpies of materials.yaml
(gas -558.5, liquid -597.1 kJ/mol). The slope neglects vapour non-ideality and liquid volume and
stays about 4 % below the CRC value at 298 K; it is used because it is the same vapour pressure
as the vent condensers' (review 2026-10-28-pfd-lci-review#1; check printed by
scripts/balance.py). C-302 reboiler and condenser 376.4 kW (298.4 kW before the correction).
Reason: PCl3 (349 K) and POCl3 (379 K) are 30 K apart, an easy separation (SRC-2 separates the
chlorides by fractional distillation). Taking the product overhead leaves non-volatiles
(metal chlorides, polyphosphoryl chlorides of SRC-2) in a small residue; their amount is not
known, so the 0.5 % purge is a placeholder carried by POCl3.
Not calculated: stage numbers and column sizes (no VLE package).

## D-009 Vent scrubbing (2026-10-28)
Decision: the two vents (25 kg/h together: O2, Ar, Cl2 and chloride vapour) pass a packed
caustic scrubber with 18 wt% NaOH at 1.5 x the stoichiometric demand; PCl3, POCl3 and Cl2 are
destroyed to 99.99 % (ASSUMED) as Na2HPO3, Na3PO4, NaCl and NaOCl; the gas leaves
water-saturated at 303 K to a stack. Spent liquor (46 kg/h) to wastewater treatment.
Reason: SRC-1 vents the excess oxygen to a scrubber; SRC-3 washes its tail gas with water and
alkali. Caustic in one stage avoids an HCl/phosphorous-acid wash water.
Heat of hydrolysis and neutralisation not counted (small flows; liquor temperature 313 K
ASSUMED).

## D-010 Pressure profile and power (2026-10-28)
Decision: reactors near atmospheric pressure (115-130 kPa(a)), columns 110-125 kPa(a), vents
110 kPa(a), stack 105 kPa(a). Pumps 300 kPa differential at 0.55 wire-to-water efficiency
(ASSUMED): P-101, P-201 (loop), P-202, P-301, P-302, P-303, P-401 (20 m3/h); R-101 agitator
11 kW (ASSUMED). Total 51.6 kW = 12.9 Wh/kg POCl3. Oxygen and chlorine arrive under pressure
(no compressor).

## D-011 Safety notes carried forward (2026-10-28)
Not a hazard study. Points the basic design must address: (a) PCl3 vapour with oxygen can
explode (SRC-1: vapour with about 50 % or more PCl3 above the liquid; SRC-2: excess-oxygen
processes with a large vapour phase): R-201 keeps a small vapour space, oxygen fed under the
liquid in the loop, vapour-space composition to be checked; (b) PCl3, POCl3 and white phosphorus
react violently with water and release HCl: dry nitrogen padding, vents to T-401; (c) white
phosphorus is pyrophoric: kept molten under water, transferred without air; (d) chlorine
inventory kept to the pipeline. Fugitive emissions and storage are not counted (LCI exclusions).

## D-012 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml, functional unit 1 kg distilled POCl3 at the gate (stream S14),
attributional, cut-off, design case. Every foreground exchange from the balanced flowsheet:
P4 0.2031 kg, Cl2 feed 0.7036 kg, O2 feed 0.1046 kg, NaOH 50 wt% 3.87 g, process water 6.88 g,
electricity 12.9 Wh, LP steam 90.7 Wh (0.327 MJ), cooling water 1.170 kWh rejected, chilled
water 0.09 Wh; residue 5.03 g (incineration), spent liquor 11.5 g (wastewater), scrubbed vent
5.52 g with Cl2 3.5e-8 kg, PCl3 7.7e-9 kg, POCl3 5.0e-8 kg as elementary emissions to air
(O2, Ar, H2O free). Every background is left unmapped (`missing:` with the activity it should
connect to); no licensed database values. The boundary key stays cradle-to-gate so that the
purchased inputs remain gaps instead of being mapped free (as phosgene-1 does).
Check: the inventory's mass inputs (1.022096 kg) and outputs (1.022094 kg) per kg POCl3 match
the flowsheet (difference 1.6e-6 kg/kg, the script's rounding).
Result: classification partial (11 gaps, no climate total); the three chloride emissions have no
GWP100 factor (reported, not zero).
Exclusions: fugitive chlorides, storage breathing, phosphorus mud and melt-tank water (no amount
yet).

## D-013 Missing shared entries (for the consolidated library PR) (2026-10-28)
Not edited here (case brief): chemicals/chemicals.yaml lacks `phosphorus` (white phosphorus,
P4, CAS 12185-10-3 / 7723-14-0), `chlorine`, `sodium-hydroxide` (50 wt% solution grade),
`phosphorus-trichloride` (intermediate) and `phosphorus-oxychloride` (main product, CAS
10025-87-3); lci/mappings.yaml has no technosphere entries for these, for chilled water, for
hazardous-waste incineration of chlorinated liquids, and no biosphere identity for Cl2, PCl3 or
POCl3 to air. The disodium phosphite component has no CAS in materials.yaml (not verified in
this session). The families taxonomy has no phosphorus-chemicals family; `inorganic-chemicals`
is used.

## Calculation maturity (2026-10-28)
`cheme maturity`: calculation maturity none; the claim `concept` (the lowest level of the
manifest) is kept, as for phosgene-1, and the warning is accepted: feeds and conversions are
assumed rather than given with a source, the condensers, columns and scrubber are specified
values, and no simulation is possible (D-006).

## Open inputs and gated steps
- Gated: property package for PCl3/POCl3/P4/Cl2 (VLE, liquid enthalpies) to
  simulate the vent condensers and columns, close the energy balance in core and size the
  columns; until then scripts/balance.py.
- Gated: caustic liquor (NaCl, Na3PO4, Na2HPO3, NaOCl, NaOH) for the scrubber.
- Open inputs: phosphorus impurity and water content (D-003); commercial POCl3 specification
  (D-002); residue amount and composition (D-008); R-201 kinetics and mass transfer (D-005);
  heat recovery from R-101 as steam (D-004); LCI backgrounds (D-012).
