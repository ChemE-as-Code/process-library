# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Titanium dioxide by the chloride process, issue ChemE-as-Code/process-library#463, coverage rank
57 (`titanium-dioxide`). Concept stage: design basis, balanced BFD/PFD with the chlorine recycle
converged by core, an energy balance script, equipment list and a preliminary gate-to-gate LCI.
Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets; the hazards are screened, not designed
(D-014).

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 and #254). Core
features used: component separators with specified recoveries (core ADR 0070), recycle tears
(ADR 0060) solved together with design specifications (ADR 0070), conversion reactors with
solid components. Templates: `phosgene-1` (chlorine, CO, caustic scrubber and thermal oxidiser)
and `oxalyl-chloride-1` (source register, structure). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | European Commission, Joint Research Centre, European IPPC Bureau (2007): Reference Document on Best Available Techniques for the Manufacture of Large Volume Inorganic Chemicals - Solids and Others industry (LVIC-S BREF), https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/lvic-s_bref_0907.pdf | chapter 3: 3.1 (Tables 3.3-3.5, world and EU capacities by route), 3.2.2.1-3.2.2.17 (chloride process description, pp. 108-114), 3.2.3.2 (Tables 3.8-3.15: feedstock TiO2, chlorine, coke, lime, oil, oxygen, abrasives, caustic per t), 3.2.3.3 (Table 3.16 energy, Table 3.17 water), 3.2.3.4-3.2.3.6 (Tables 3.18-3.28 emissions and wastes), 3.2.4.1.4 and 3.2.4.2 (pp. 129-131: chlorine inventory, oxidiser fuel), 3.3.2 (sulphate process description, pp. 142-148), 3.4.2.7 (p. 189: containment), 3.5.1 (p. 199: BAT for the chloride route) | read (PDF text); EU publication, reuse with acknowledgement; only facts and figures taken, restated | D-001 to D-014, benchmarks |
| SRC-2 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment), printed by `cheme chemistry thermo` and read by scripts/energy_balance.py. Underlying works: the CRC Handbook of Chemistry and Physics (the CRC tables packaged in `chemicals`: `heat_capacity.CRC_standard_data`, `phase_change.Hvap_data_CRC`; method CRC), the Active Thermochemical Tables (ATcT), the NIST Chemistry WebBook (method WEBBOOK and the WEBBOOK_SHOMATE heat capacities), the NIST-JANAF Thermochemical Tables (JANAF, JANAF_FIT), the TRC ideal-gas heat capacity tables (TRCIG), CoolProp's reference equations of state (HEOS, HEOS_FIT), Matthews' critical constants (MATTHEWS) and Yaws' acentric factors (YAWS), IEC 60079-20-1 (2010) for the flammability limits | formation enthalpies: rutile, FeO, quartz, FeCl2(s), CaO, Ca(OH)2, CaCl2 (CRC), Fe(OH)2 and FeCl2(g) (WEBBOOK), TiCl4 (l, g: CRC), the gases (ATcT, CRC); heat capacities: the solids (WEBBOOK_SHOMATE; graphite JANAF_FIT), FeCl2 gas (JANAF), the gases (TRCIG, JANAF, HEOS fits in materials.yaml), liquid TiCl4 and water (thermo defaults; water HEOS_FIT); TiCl4 Tb and heat of vaporization (CRC), vapour pressure, Tc, Pc (MATTHEWS), omega (YAWS); FeCl2 Tm, Tb; CO lower and upper flammability limits in air (IEC 60079-20-1). The values sit in materials.yaml, reactions.yaml and the script | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying handbooks and tables were not read here; no table or coefficient set copied | L-1, D-004, D-006, D-010, D-011, D-014, materials |
| SRC-3 | processes/chlor-alkali-1, asu-1, lime-1 (this library) | dry chlorine (its stream S42) and 50 wt% caustic; GOX (99.7 mol% O2, Ar); quicklime counted as CaO | library data, CC BY 4.0 | feeds, LCA links |
| SRC-4 | Ullmann's Encyclopedia of Industrial Chemistry, Pigments, Inorganic: titanium dioxide | - | not read (licensed); cited by SRC-1 for the world figures | not used |

Searched and not found openly in this work (2026-11-19): kinetics of the carbochlorination or of
the TiCl4 oxidation usable for a reactor model, an open heat balance of a chlorinator or an
oxidiser, the CO/CO2 ratio of a plant's chlorinator gas, the vanadium content of a feedstock, the
compositions of commercial slags and synthetic rutiles beyond their TiO2 content, prices.

## D-001 Route and boundary (2026-11-19)
Decision: the **chloride process** (SRC-1 3.2), continuous, with the **direct chlorine recycle**
(3.2.2.12):
- R101: TiO2 + 2 Cl2 + 3/2 C -> TiCl4 + CO + 1/2 CO2 (SRC-1 3.2.2.2, the BREF's equation per mol
  TiO2) in a fluidised bed at 1273 K; FeO + Cl2 + C -> FeCl2 + CO for the impurities; the O2 that
  enters with the chlorine burns coke, C + O2 -> CO2;
- E101/S101: quench with cold TiCl4 and cyclone for the blow-over and metal chlorides (3.2.2.3);
- E102/E103/V101: TiCl4 condensation (3.2.2.5); T101: distillation, the vanadium complexed with
  oil and left in the sludge (3.2.2.7-3.2.2.8);
- E201-E203, R201: TiCl4 vaporised and preheated, oxygen preheated, TiCl4 + O2 -> TiO2 + 2 Cl2
  (3.2.2.9); E204, F201: cooled and collected in a bag filter, the chlorine returned (3.2.2.10);
- R301/V301, X301: the condenser off-gas scrubbed with water and caustic and its CO burnt in a
  thermal oxidiser (3.2.2.14);
- M401, R401, F401: blow-over, still sludge and scrubber liquor neutralised with lime and
  filtered, the cake landfilled, the filtrate discharged (3.2.2.4, 3.2.2.15).

Why the chloride route: it can be modelled and sourced at Tier 2 with what core has. Its
chemistry is a few stoichiometric reactions of species with formation data (TiO2, TiCl4, Cl2,
CO, CO2, FeO, FeCl2), core converges its chlorine loop with the design specifications, and the
BREF gives per-tonne consumptions for every main input (Tables 3.8-3.15) against which the
balance is checked (D-012). Coverage lists both routes as market-mix variants; the roadmap note
names no preferred one. The chloride route is 55 % of world capacity (SRC-1 3.1.3) and links the
library's chlorine (chlor-alkali-1) and oxygen (asu-1).

Rejected: the **sulphate process** (SRC-1 3.3): batch digestion of ilmenite or slag with 80-95 %
sulphuric acid, reduction with scrap iron, clarification, copperas (FeSO4.7H2O) crystallisation,
batch hydrolysis of TiOSO4 with seeding, washing and bleaching, calcination in a rotary kiln, and
the strong and weak acid either reconcentrated or neutralised. Rejected for now because its
modelling needs what core and the open sources do not give: no formation or heat-capacity data
for titanyl sulphate and its hydrolysate in the packages, a hydrolysis yield and a seeding recipe
that the BREF only describes, the solubility of FeSO4 in the acid liquor for the copperas step,
and a digestion cake whose composition varies with the ore. It stays the second variant of rank
57 (to be a `titanium-dioxide-2` with sulfuric-acid-1 as its acid supplier). Also rejected: the
older absorption/desorption chlorine recovery in TiCl4 (3.2.2.11), no longer used in the EU
(3.2.3.3.1).

Boundary: from the feedstock, coke, chlorine and oxygen at the battery limit to the raw TiO2 from
the bag filter. The finishing plant (wet milling, inorganic coating, filtration, drying,
micronising, packing) is outside (D-002). Feedstock drying is not needed (3.2.2.1); ore
beneficiation is upstream (the feedstock's own burden, D-013).

## D-002 Capacity and product (2026-11-19)
Decision: 12 500 kg/h raw TiO2, 100 kt/a at 8000 h (ASSUMED), inside the 55-150 kt/a of the five EU
chloride sites (SRC-1 Table 3.5). Product: TiO2 only; the pigment properties (rutile content,
crystal size, the Al co-oxidised from AlCl3 to stabilise the rutile) are not modelled (L-3).
Finishing is outside the boundary because its inputs are product-grade specific; the BREF puts
its energy at 2.6 GJ electricity, 6.9 GJ steam and 5.7 GJ gas per t (Table 3.16, 1999 averages),
which a cradle-to-gate pigment study must add.

## D-003 Feedstock (2026-11-19)
Decision: a blend of titanium slag (86-87 wt% TiO2) and synthetic rutile (90-93 wt%), SRC-1
Table 3.7, at 88 wt% TiO2 (ASSUMED); the other 12 wt% lumped as 8 wt% chlorinatable oxides
(written as FeO: iron, and the Mn, Mg, Al, V oxides that chlorinate with it) and 4 wt%
non-chlorinating inerts (written as SiO2: silica, zircon). The split is ASSUMED: SRC-1 gives the
TiO2 contents only. It sets the make-up chlorine (D-006) and the lime (D-010), both of which land
inside the BREF ranges.

## D-004 Chlorinator R-101 (2026-11-19)
Decision: conversion model at 1273 K (SRC-1 3.2.2.2), 150 kPa(a) freeboard (ASSUMED).
- 95 % of the TiO2 entering the bed chlorinated (ASSUMED), the rest blown over: the feedstock
  then holds 1.069 t TiO2 per t of product, near the BREF mean of 1.075 t (Table 3.8, range
  0.975-1.145).
- The chlorinatable oxides chlorinated completely; FeCl2 stands for all metal chlorides.
- The CO/CO2 ratio is the BREF equation's 2:1; a plant's ratio depends on temperature and the
  coke (not sourced, L-3).
- The heat balance closes with a small surplus: scripts/energy_balance.py gives 0.20 MW lost
  through the shell (Q1) with the feeds at their temperatures and the outlet at 1273 K. The
  metal chlorides leave the bed as vapour (FeCl2: melting point 950 K, boiling point 1296 K,
  partial pressure in S6 about 5 kPa; BREF 3.2.2.3 has them leave with the TiCl4 vapours and
  condense on cooling), which takes 0.85 MW of the bed's heat; counted as solid, the surplus
  would read 1.04 MW. The bed is autothermal with little margin; a real plant trims it with
  the oxygen in the chlorine and the coke ratio, and the margin depends on the CO/CO2 ratio
  (L-3).

## D-005 Coke (2026-11-19)
Decision: calcined petroleum coke carried as carbon only (ASSUMED; its sulfur, ash and
volatiles are not modelled, L-3). Design specification `coke-excess`: 15 % of the coke carbon
leaves the bed unreacted with the blow-over (ASSUMED; SRC-1 3.2.3.2.1: higher fluidisation
velocities blow over ore and coke). Result: 316 kg coke per t, inside the BREF's 285-429 kg/t
(mean 366, Table 3.10). The O2 entering with the chlorine (the oxidiser's excess and the make-up
chlorine's 0.8 wt%) burns coke to CO2 (ASSUMED complete).

## D-006 Chlorine, quench, condensation and still (2026-11-19)
Decisions:
- Design specification `chlorine-slip`: 0.2 % of the chlorine fed to the bed leaves it unreacted
  (ASSUMED); the make-up S3 from chlor-alkali-1 then closes the chlorine balance: 128 kg/t,
  inside the BREF's 114-300 kg/t (mean 201, Table 3.9; the variation follows the impurities).
- Quench E-101 to 473 K with cold TiCl4 (ASSUMED temperature: below the condensation of the metal
  chlorides, above the TiCl4 dew point); cyclone S-101 separates 99.5 % of the solids, 0.2 % of
  the TiCl4 adhering to them (ASSUMED). E-101 is a direct spray quench, not a cooler: crude
  TiCl4 condensate (308 K, from E-102/V-101) is sprayed in and evaporates. Its outlet at 473 K
  is above the TiCl4 dew point (386 K at 145 kPa(a) for the net gas, 409 K with the evaporated
  spray, scripts/energy_balance.py), so no liquid is left and E-101 rejects no heat itself.
  The 7.87 MW it takes from the gas evaporates about 94 t/h (498 kmol/h) of circulating TiCl4,
  which E-102 condenses again: the quench heat leaves in E-102. The circulation is an internal
  loop of E-101, E-102 and V-101 and is not drawn as a stream; S7 and S9 carry the net flows
  (ASSUMED simplification), and E-102's real TiCl4 load is about four times S9's.
- Condensation: E-102 to 308 K on cooling water (10.76 MW: the quench heat and the condensation
  of S9), E-103 to 263 K on brine (243 K supply). The
  separator V-101 recovers 99.7 % of the TiCl4, the equilibrium of Raoult's law over pure TiCl4
  at 263 K and 130 kPa(a) with the permanent gases insoluble (the script prints it). The cold
  TiCl4 jet scrubber of SRC-1 3.2.2.5 would recover more; not credited.
- Still T-101 at atmospheric pressure: 99 % of the TiCl4 distilled (ASSUMED), reflux ratio 1.0
  (ASSUMED); the bottoms (1 % of the TiCl4, the fines, the vanadium-oil complex) to the
  neutraliser. SRC-1 3.2.2.8 recycles the sludge to the solids separation; here it goes to R-401
  directly (ASSUMED, the same end). Oil 5 kg/t is an LCA consumable (Table 3.12).

## D-007 Oxidation train (2026-11-19)
Decisions:
- TiCl4 vaporised on HP steam (4000 kPa(a), 523.5 K) to 493 K at 280 kPa(a), superheated to 723 K
  in a fired heater; oxygen preheated to 1273 K in a fired heater (temperatures ASSUMED; SRC-1
  3.2.2.9: both preheated before mixing, the heat input from toluene burning or a plasma arc).
  Natural gas replaces the toluene (ASSUMED, a fuel the library links).
- Design specification `oxygen-excess`: 15 % O2 over the TiO2 formed (ASSUMED), consistent with
  the BREF mean of 467 kg O2/t against 401 kg/t stoichiometric (Table 3.13); the result is
  462 kg/t.
- 99.8 % of the TiCl4 oxidised per pass (ASSUMED); the rest returns with the chlorine.
- R-201 adiabatic: scripts/energy_balance.py gives an outlet of 1997 K, inside the BREF's
  900-2000 C.
- E-204 cools the suspension to 423 K on cooling water (3.2.2.10: indirect water cooling,
  scoured with sand or salt: 49 and 16 kg/t, Table 3.14, LCA consumables). F-201 collects
  99.99 % of the TiO2; the gas (Cl2 with the O2 excess) returns at 200 kPa(a) to M-101 (the
  oxidiser runs above the chlorinator pressure, 3.2.2.12).

## D-008 Off-gas scrubber (2026-11-19)
Decision: one lumped scrubber T-301 (flowsheet steps R301 and V301; the BREF's water and caustic
stages): the TiCl4 left in the off-gas hydrolyses and its HCl is neutralised in the same step
(reaction HYD_NAOH, L-4), the chlorine slip absorbed in caustic to
hypochlorite, each at the conversion in reactions.yaml (ASSUMED); caustic 50 wt% (chlor-alkali-1)
at 1.5 times what it consumes (design specification `caustic-excess`), diluted with twice its
mass of water. Result: 31 kg of 50 wt% caustic per t (15.6 kg NaOH), inside the BREF's 7-178
kg/t (Table 3.15). The BREF also describes selling 28 % hydrochloric acid from the water stage;
not modelled. The model carries no HCl at all: the TiCl4 slip is hydrolysed and neutralised in
one step, so the off-gas, the stack (S37) and the LCI's HCl emission are zero; the small HCl
residue the BREF reports in the scrubbed gas (3.2.3.4.2, Table 3.19: 35 mg/Nm3) is not resolved.

## D-009 Thermal oxidiser X-301 (2026-11-19)
Decision: the CO-rich scrubbed gas (63 mol% CO) burnt with air without support fuel, adiabatic,
outlet 1123 K (ASSUMED), 99.9 % CO destruction (ASSUMED); scripts/energy_balance.py solves the
air (46.3 t/h) and the fan power (5 kPa, fan 0.65, motor 0.95, ASSUMED). SRC-1 3.2.3.4.2: all
EU sites have thermal oxidisers for CO and COS and recover the heat as steam; the waste-heat
boiler is left out of the design case (open: it would export about 10 MW of steam, a credit
under substitution only). CO2 to air: 0.98 kg per kg TiO2, all fossil (the coke), against the
BREF's 923 kg/t mean from chlorination (Table 3.19, range 56-1790).
The same BREF passage (3.2.3.4.2, p. 119; again 3.2.4.2, p. 131) says natural gas is used for
burning the COS and CO, with NOx, CO2 and SO2 emissions. This design burns the gas without
support fuel because at 63 mol% CO it sustains its own combustion and the air rate reaches
1123 K (ASSUMED; not checked against a flammability or flame-stability limit). The pilot,
start-up and support gas of a real oxidiser is not counted: the fired heat of D-011 and the
LCI leave it out, which is one reason why the fired heat lies below the BREF's minimum (D-011,
D-012). Open input: the oxidiser's support-fuel rate.

## D-010 Waste neutralisation (2026-11-19)
Decision: the blow-over (unreacted ore and coke, silica, metal chlorides), the still sludge and
the scrubber liquor neutralised with a 20 wt% lime slurry at 1.1 times what the metal chlorides
and the TiCl4 consume (design specification `lime-excess`, ASSUMED), the metals precipitated as
hydroxides (Fe(OH)2 stands for all), and filtered (SRC-1 3.2.2.4, 3.2.2.15). The cake keeps 15 %
of the liquor (ASSUMED). Results: lime 102 kg/t, 1.28 t/h (BREF 91-220, mean 137, Table 3.11);
wet cake 396 kg/t to landfill (BREF 99-660, mean 397, Table 3.28), of which 295 kg/t
undissolved solids (unreacted ore and coke, silica, hydroxides, excess lime), 70 kg/t water
and 31 kg/t dissolved salts of the retained liquor; filtrate 569 kg/t with CaCl2 and NaCl.
Heat (scripts/energy_balance.py): the slaker M-401 runs adiabatic, the slaking heat (0.41 MW)
taking the slurry S42 to 366 K, below boiling. The neutraliser R-401 takes the hot blow-over
(473 K), the still bottoms with liquid TiCl4 (413 K), the liquor and the hot slurry, and the
heat of HYD_LIME and FECL_LIME; uncooled it would heat its slurry by about 110 K, past boiling.
A cooling-water coil holds it at 323 K (ASSUMED): Q11, 0.75 MW. The heat of solution of the
CaCl2 is not counted (no aqueous data in the packages, SRC-2) and would add to Q11; open for
basic engineering, as is the vapour of the hot slaker (water).
Rejected: roasting the chlorides to HCl and oxides, or selling FeCl2 (3.2.2.15, 7.4), which only
some sites do.

## D-011 Utilities and energy (2026-11-19)
Decisions:
- Heat duties from scripts/energy_balance.py (L-1): condenser 10.76 MW (with the 7.87 MW quench
  heat, D-006), still condenser 3.11 MW, product cooler 10.6 MW and neutraliser 0.75 MW on
  cooling water (25/35 C; 2.02 kWh/kg TiO2 in all); after-condenser 0.46 MW on brine; still
  reboiler 4.05 MW and vaporiser 1.93 MW on HP steam (1.72 GJ/t); fired preheaters 2.67 MW
  absorbed (0.77 GJ/t).
- Against the BREF (Table 3.16, 1999 site data up to oxidation): steam 1.72 GJ/t lies between the
  minimum 1.3 and the average 2.4 GJ/t. The fired heat, 0.77 GJ/t, lies below the minimum of
  1.3 GJ/t (average 3.2), and the minimum excludes the old indirect chlorine recycling (the
  table's footnote puts that into the average and maximum only). Reasons on this side: the
  fired duty is the heat absorbed, with no furnace efficiency (the LCA's fired-heat entry counts
  the heat absorbed); the thermal oxidiser's natural gas (D-009) is not counted; no feedstock
  drying (D-001); the plant's losses are not counted. The fired heat is therefore a lower bound,
  not a site figure.
- Electricity from the BREF (Table 3.16, 1999 site averages): 2.3 GJ/t for ore preparation to
  oxidation (P1, 7.99 MW) and 1.7 GJ/t for effluent treatment (P2, 5.90 MW), given as sourced
  lumps; plus the air fan (P3). Total 1.12 kWh per kg TiO2.
- Pressures: chlorinator 150 kPa(a), oxidiser 250 kPa(a), recycle 200 kPa(a) (ASSUMED profile
  for the direct recycle).

## D-012 Checks against the BREF ranges (2026-11-19)
Per t of raw TiO2, from the propagated flowsheet against SRC-1 (the BREF counts per t of
finished pigment, slightly more than TiO2: our values are a little high by that basis):

| quantity | this design | BREF LVIC-S (1999, EU chloride sites) |
|---|---|---|
| TiO2 in the feedstock | 1069 kg | mean 1075, 975-1145 (Table 3.8) |
| make-up chlorine | 128 kg | mean 201, 114-300 (Table 3.9) |
| coke | 316 kg | mean 366, 285-429 (Table 3.10) |
| oxygen | 462 kg | mean 467, 395-573 (Table 3.13) |
| lime | 102 kg | mean 137, 91-220 (Table 3.11) |
| NaOH (100 %) | 15.6 kg | mean 104, 7-178 (Table 3.15) |
| CO2 to air | 982 kg | mean 923, 56-1790 (Table 3.19) |
| solid waste (wet cake; 295 kg undissolved solids) | 396 kg | mean 397, 99-660 (Table 3.28; its moisture basis not stated) |
| fired heat (gas) up to oxidation | 0.77 GJ | mean 3.2, 1.3-6.6 (Table 3.16): below, a lower bound (D-011) |
| steam up to oxidation | 1.72 GJ | mean 2.4, 1.3-7.6 (Table 3.16) |

The BREF's values are site averages, not independent of the choices above (D-003 to D-010 aim at
them); they show that the assumptions are plausible, not that the model predicts. The fired
heat is the one value outside its range (D-011).

## D-013 Preliminary gate-to-gate LCI (2026-11-19)
Decision: the inventory per kg of raw TiO2 (lca/lca.yaml), with the chlorine and caustic linked
to chlor-alkali-1, the oxygen to asu-1, the lime to lime-1, power, HP steam heat, fired heat,
cooling water, water and the rock salt to shared entries. Gaps (no library producer, never
mapped to a guess): the titanium feedstock (slag or synthetic rutile: the upgrading of ilmenite
is the main upstream burden of the chloride route, SRC-1 3.2.2.1), the calcined petroleum coke,
the still oil, the scouring sand, the brine refrigeration, the landfilled cake and the
discharged filtrate, and the disposal of the three consumables (the still oil and the scouring
sand with the cake to landfill, the dissolved salt with the filtrate). Emission exclusions
recorded in lca.yaml: COS/SO2 from the coke's sulfur, NOx, dust from raw material handling and
fugitive chlorine (no P&ID yet). No allocation: one product.

## D-014 Hazard screening (2026-11-19)
Decision (noted, not designed): the hazards the flowsheet carries are named here with their
size, so that basic engineering and the HAZOP start from them; release cases, detection,
emergency isolation, relief, the Seveso classification and the layout are out of scope.
- **Chlorine.** SRC-1 3.2.2.1 (pp. 109-110) and 3.2.4.1.4 (p. 129): the hazardous nature of
  chlorine is the main property that shapes the chloride process; the black end is totally
  enclosed and of high integrity, the plants fall under the Seveso II Directive, and a minimum
  chlorine inventory is the goal (also BAT, 3.5.1). Here: 23 t/h of recycle gas (93 mol% Cl2)
  at 200 kPa(a) from F-201 to M-101 (S4) and 1.6 t/h of make-up chlorine by pipeline from
  chlor-alkali-1 (S3; no chlorine storage inside the boundary, ASSUMED). The inventory is set by
  the loop's volume, not sized here.
- **TiCl4.** About 30 t/h of liquid TiCl4 (S12, S14) plus the quench circulation (about 94 t/h,
  D-006). TiCl4 hydrolyses with water to HCl and TiO2 (the scrubber chemistry of D-008), so a
  release into moist air gives an HCl and TiO2 cloud; SRC-1 3.4.2.7 (p. 189) names chlorine,
  TiCl4, CO and COS as needing high-integrity containment.
- **CO.** The condenser off-gas S13 is 62.6 mol% CO with 0.24 mol% Cl2 (S33 after the scrubber:
  62.9 mol% CO) on its way to X-301. CO is toxic and flammable in air between 10.9 and 74 vol%
  (SRC-2: chemicals 1.5.2, method IEC 60079-20-1); the off-gas is above the upper limit as it
  stands but passes through the flammable range when it mixes with air (in X-301 by design, in
  a leak otherwise). SRC-1 3.4.2.7: CO and COS are invisible toxic gases that need special
  precautions.
- **Hot oxygen.** Oxygen preheated to 1273 K in a fired coil (E-203) and the oxidiser R-201 at
  1997 K: oxygen service at high temperature, a materials and ignition hazard (metal burning in
  oxygen, coil failure into a fired box). The materials and the design of E-203 and R-201 are
  open inputs.
- **NORM.** Some feedstocks carry naturally occurring radioactive material (SRC-1 3.2.2.1,
  p. 109): ore handling and some wastes (here the filter cake) may need an exposure assessment
  under the Euratom rules. The feedstock analysis is an open input (D-003).
- **Thermal screening.** `cheme process reactor-hazards` screens a cooled liquid-phase reactor's
  runaway after a cooling failure; none of the reactors is that. R-101 and R-201 run at their
  adiabatic temperature by design (gas-solid and gas phase, no cooling to lose); X-301 is an
  adiabatic burner. The one cooled step is the neutraliser R-401 (D-010): without its cooling
  coil its slurry would heat by about 110 K and boil; the heat comes from fast neutralisation
  and hydrolysis of what the feeds bring, so it stops when the feeds stop (no accumulation),
  and the hazard is steam, HCl and TiCl4 fume from the tank. Not run through the tool.

## Method and dependency table

| result | method | inputs |
|---|---|---|
| every flow and composition, the recycle S4, the six design specifications | core `cheme process propagate --fill` (conversion reactors, recoveries, tears with specs) | materials.yaml, reactions.yaml, the feeds' compositions, D-003 to D-010 |
| S5, S19 temperatures, S35 air, Q1-Q10, P3 | scripts/energy_balance.py (balance-output contract, library ADR 0027) | the propagated flows; SRC-2 data |
| P1, P2 | SRC-1 Table 3.16 x 12.5 t/h | - |
| LCI | core `cheme assess lca --write` | lca/lca.yaml, lca/mappings.yaml |

## Core features used (core 1.12.0)

- Component separators with `recovery:` (cyclone, condenser separator, still, bag filter,
  scrubber separator, filter press), conversion reactors with solid components, the recycle tear
  converged together with six design specifications (Broyden), the generated BFD/PFD, the LCA
  with Atlas producer links.

## Core limits hit (each a candidate core issue)

- **L-1: no condensed-phase enthalpy in a flowsheet step.** Solid components and a liquid TiCl4
  have no `ideal_gas` data, so propagate cannot give a reactor's or a cooler's duty and there is
  no field for a solid's formation enthalpy and heat capacity in materials.yaml; `cheme process
  furnace` covers calcination only. The duties come from a script on the chemicals/thermo data.
  A core extension: `condensed:` formation and Cp data per component, and the conversion-duty
  model (core ADR 0059) for steps with solids and liquids.
- **L-2: propagate writes every inlet component into the outlet composition, also at zero.** The
  templates had to list every component a stream might carry, and the flue gas carries ten
  zero-amount emission exchanges (C, FeO, FeCl2, SiO2, TiO2, TiCl4, HCl, NaCl, NaOCl, NaOH) that the
  LCI build lists as gaps without effect (a free emission would need a shared pass-through
  decision).
- **L-3: what the model does not resolve.** The CO/CO2 ratio of the chlorinator, the metal
  chloride spectrum (lumped as FeCl2), vanadium removal, the coke's sulfur (COS, SO2), the
  solubility of Cl2, CO2 and CO in TiCl4, the water saturation of the scrubbed gas, the pigment
  properties, the AlCl3 co-oxidation.
- **L-4: conversions apply to a step's inlet only.** A product formed in a step (HCl from the
  hydrolysed TiCl4) is not converted further in the same step, so hydrolysis and neutralisation
  are written as single combined reactions (HYD_NAOH, HYD_LIME).
- **L-5: a design specification's initial value matters.** A caustic or lime spec started below
  what the first loop pass consumes stops the whole solve ("conversions not applied"); the
  initial values are set above the solution.

## Open inputs

- The feedstock's impurity spectrum and the coke's analysis (sulfur, ash, volatiles).
- A waste-heat boiler on X-301 and its steam use (D-009).
- The oxidiser's heat source (natural gas preheat as here, toluene, plasma) and the AlCl3 dosing.
- The thermal oxidiser's support and pilot fuel (D-009).
- The materials of construction (equipment list: the usual service choices named there are to be
  confirmed), including the oxygen-service and high-temperature materials of E-203 and R-201
  (D-014).
- The hazard studies of D-014: release cases, the Seveso classification, the NORM assessment.
- The finishing plant (D-002) and the sulphate route as a second variant (D-001).
