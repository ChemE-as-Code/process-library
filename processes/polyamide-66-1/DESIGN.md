# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Polyamide 66 (nylon 6,6) by batch melt polycondensation of AH salt in an autoclave, issue
ChemE-as-Code/process-library#521 (proposed there as `nylon-66-1`; the folder is named after the
registry's product slug `polyamide-66`). A batch entry of the library and the first consumer of
`adipic-acid-1` as a polymer. Concept stage: design basis, batch recipe, balanced BFD/PFD,
thermal screening and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP,
TEA, datasheets.

Starting point (2026-11-19): library `main` at c04ed69 with the core pin v1.13.0 (b97a833).
Core models what the route needs at the concept stage: a semi-batch with a dosed liquid and its
thermal screening (core ADR 0050), a conversion step with its duty (ADR 0059), component
separators with a specified split and design specifications (ADR 0070), the batch recipe over
one-vessel unit procedures (ADRs 0051, 0052, 0057). Library ADR 0035: one dedicated train,
campaigns out of scope (D-013). Templates: `salicylic-acid-1` and `oxalyl-chloride-1` (batch
structure, semi-batch screening, recipe, balance script), `polystyrene-1` (polymer per repeat
unit, hot oil, nitrogen). Requires cheme-as-code 1.13 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (the PDF text extracted, the Wikipedia wikitext). The `chemicals` and `thermo`
Python packages (SRC-5) were queried for single values, facts only with their source; the works
behind them were not read and are named in each row (library ADR 0037).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | European Commission JRC/EIPPCB (2006) Reference Document on Best Available Techniques in the Production of Polymers (POL BREF), https://aida.ineris.fr/sites/aida/files/documents-bref/pol_bref_1006.pdf (INERIS AIDA mirror) | section 9.2.2.1: the AH (66, nylon) salt from hexamethylenediamine and adipic acid as a 52 to 53 % solution, kept under nitrogen; PA66 made continuously or in batches, optionally post-condensed in the solid state. 9.2.2.2 (continuous): the salt at 52 % and 65 C concentrated at about 110 C to 72 %, preheated to 212 C, a tubular reactor at about 18 bar in about three zones of 212 to 250 C, the water removed as steam stripping some diamine that is made up, a flasher to 280 C and 1 bar, a finisher at 285 C, strands quenched and cut, pellets dried under nitrogen; condensates to the wastewater, vents through a scrubber. 9.2.2.3 (batch): autoclaves on a cycle at rising temperature; the 52 to 53 % solution with additives (antifoam, a monocarboxylic acid as molecular weight regulator, lubricants, delustrants); first part of the water evaporated (e.g. to 70 %), then the temperature and pressure rise, the water bled off as steam by a valve holding the pressure constant; at about 275 C the pressure is let down to atmospheric under software control; finished slightly above atmospheric or under vacuum; the autoclave pressurised and the melt extruded, quenched and cut; batch suits speciality grades and PA66/6 copolymers; vapours condensed to the wastewater; emissions during filling, nitrogen flushing and depressurisation washed in a scrubber. 9.3.3.3: the reaction water and the solution water (about 1.2 t per t of salt; the model's 1.06 t/t follows from 9.2.2.1's 52 % solution, D-010) carry diamine, cyclopentanone and ammonia; biological treatment with nitrification and denitrification. 9.3.3.4: the diathermic oil heaters' combustion fumes. Table 9.3 (PA66 continuous / batch): total energy 5700 to 7500 / 5050 to 7250 MJ/t, water 130 to 150 / 140 to 160 t/t, AH salt 1.162 to 1.163 / 1.165 to 1.167 t/t, VOC to air 10 to 30 / 15 to 40 g/t, COD before treatment 4500 to 6000 / 5300 to 7300 g/t, polymer waste 0 to 0.1 / 0 to 0.2 kg/t. Table 9.8 (batch PA66, APME): total energy 3300 to 7700 MJ/t, AH salt 1.16 to 1.18 t/t, COD 3045 to 14100 g/t, VOC 15 to 70 g/t | read (PDF text); EU publication, facts only | D-001 to D-007, D-009, D-010, D-012 |
| SRC-2 | Nisoli, A.; Doherty, M. F.; Malone, M. F. (2004) Feasible Regions for Step-Growth Melt Polycondensation Systems. Ind. Eng. Chem. Res. 43(2), 428-440, doi:10.1021/ie030220w; author-hosted copy https://sites.chemengr.ucsb.edu/~ceweb/faculty/doherty/pdfs/116md.pdf | nylon 6,6 amidation A + C <-> L + W with Steppan et al.'s activity-based rate and equilibrium constants in mole fractions: E_app 21.4 kcal/mol, k0, K0 and dH_app functions of the water and carboxyl mole fractions; Table 1: a prepolymer of Mn 6200 with 3.5 wt% water at 553.15 K has a water mole fraction of 0.1826, K0 1418, dH_app -7870 cal/mol, K 422.5; melt density assumed 1 g/cm3 (Van Krevelen's amorphous 1.07 g/cm3 and about 10 % expansion on melting); Steppan's degradation forms ammonia and CO2 and cross-links; evaporation limited by liquid-phase mass transfer | read (PDF text); ACS journal article, author-hosted copy, its re-use terms not stated: facts only, nothing reproduced | D-006, D-011, L-1 |
| SRC-3 | Wikipedia, Nylon 66 (https://en.wikipedia.org/wiki/Nylon_66, wikitext read 2026-11-19) | equivalent amounts of the diamine and the acid combined in water to the salt, then heated in batches or continuously (citing Carothers, US 2 130 523); melting point 264 C; density 1.140 g/mL (a moulding grade); CAS 32131-17-2 | read; CC BY-SA, facts only | D-001, D-006, registry |
| SRC-4 | Wikipedia, Hexamethylenediamine and Adipic acid (wikitext read 2026-11-19) | the diamine: density 0.84 g/mL, melting point 39 to 42 C, boiling point 477.7 K, flash point 80 C, explosive limits 0.7 to 6.3 %, corrosive (GHS danger), LD50 oral rat 750 mg/kg; the acid: density 1.360 g/cm3, solubility in water 14, 24 and 1600 g/L at 10, 25 and 100 C, melting point 152.1 C | read; CC BY-SA, facts only | D-004, D-005, D-011, materials |
| SRC-5 | the `chemicals` 1.5.2 and `thermo` 0.6.1 Python packages (Caleb Bell), queried for single values | chemicals: the diamine's normal boiling point 470.15 K (method CRC_ORG, the CRC Handbook's organic table as packaged) and melting point 314.15 K (OPEN_NTBKM, the Open Notebook melting point set), the acid's melting point 426.15 K (OPEN_NTBKM) and normal boiling point 610.65 K (CRC_ORG), water's boiling point and saturation (HEOS: IAPWS-95; iapws95_Tsat 412.01 K at 350 kPa(a), 478.88 K at 1750 kPa(a); iapws95_Psat 5946 kPa at 548.15 K) and water's specific enthalpies by IAPWS-95 (iapws95_properties: liquid at 313.15 K and 101.325 kPa 167.62 kJ/kg, liquid at 383.15 K and 1750 kPa 462.58, vapour at 383.15 K and 101.325 kPa 2696.18, vapour at 548.15 K and 101.325 kPa 3024.34). thermo: water's latent heat 40 649.7 J/mol at 373.15 K and liquid heat capacity 75.44 J/(mol K) at 338.15 K (HEOS_FIT, thermo's fit to IAPWS-95); the diamine's latent heat 41 968.0 J/mol at 548.15 K (MORGAN_KOBAYASHI, an estimation method) and liquid heat capacity 256.1 J/(mol K) at 338.15 K (DADGOSTAR_SHAW, an estimation method); the acid's solid heat capacity 175.4 J/(mol K) at 298.15 K (LASTOVKA_S, an estimation method). The underlying works (IAPWS-95, the CRC Handbook, the estimation papers) were not read | queried; MIT-licensed packages, single facts (library ADR 0037) | materials, D-009, scripts/balance.py |
| SRC-6 | PubChem PUG REST and EBI OLS (ChEBI), queried 2026-11-19 | hexane-1,6-diamine CID 16402, C6H16N2, InChIKey NAQMVNRVTILPCV-UHFFFAOYSA-N, CHEBI:39618; the AH salt CAS 3323-53-3 is CID 197024 (C12H26N2O4, hexane-1,6-diamine;hexanedioic acid); CAS 32131-17-2 has PubChem Substance records and no compound; no ChEBI entry for nylon 6,6 | queried; public databases, identifiers only | registry, materials |
| SRC-7 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | method: accumulation, MTSR, MTT of a semi-batch (core's screening implements it) | method reference, not read for data | D-011 |

## D-001 Route and boundary (2026-11-19)

**Decided.** Polyamide 66 by melt polycondensation of the aqueous AH salt in a **batch
autoclave**, the cycle of SRC-1 section 9.2.2.3, with the salt made on site from adipic acid
(adipic-acid-1) and bought-in hexamethylenediamine (issue #521's scope). Boundary: from the
acid, the diamine, water, nitrogen and utilities at the battery limit to pellets to the silos and
the condensate to the site's wastewater treatment. The pellets' drying under nitrogen in the
silos, the solid-state post-condensation and the additives are outside (D-007).

**Rejected.**
- *Continuous polymerisation* (SRC-1 9.2.2.2: concentrator, preheaters, a three-zone tubular
  reactor at about 18 bar, flasher, finisher): the BREF's route for bulk standard grades and
  direct spinning, and a little more energy-efficient at the top of its range (Table 9.3). It
  is not a batch process; the library's batch train (ADR 0035) and the issue's teaching case,
  a vessel with simultaneous reaction and vapour removal on a scheduled cycle, favour the
  autoclave. A continuous entry is a later `polyamide-66-2`.
- *Solid salt route* (the original practice SRC-3 describes, the salt isolated and then heated):
  the BREF's plants use the 52 to 53 % solution; isolating the crystals adds a crystalliser,
  a centrifuge and a dryer for nothing the autoclave needs.
- *Polyamide 6 from caprolactam* (SRC-1 9.2.1): another product (the caprolactam branch).
- *Buying the salt solution*: the issue asks for the acid from adipic-acid-1; making the salt
  on site is what closes the value chain and gives the exothermic dosing step its screening.

## D-002 Capacity, product and operating hours (2026-11-19)

8000 t/a of pellets (ASSUMED): one autoclave train for speciality grades, which SRC-1 names as
the batch process's use. 7920 h/a (330 days, ASSUMED). The pellets are modelled as 99.22 wt%
polymer (repeat units), 0.58 wt% unlinked chain ends counted as salt and 0.2 wt% water (D-006).
No additives: SRC-1 lists them (molecular weight regulator, antifoam, delustrant) without
amounts.

## D-003 Batch basis, recipe and vessels (2026-11-19)

`process/recipe.yaml`: one batch of 5303.03 kg of pellets every 5.25 h, 1508.6 batches a year,
the autoclave R-201 the bottleneck (100 % utilised), the dissolver R-101 occupied 3.63 h (69 %).
The autoclave's phase times are ASSUMED (charge 0.5 h, concentration 1.0 h, polycondensation
with the steam bleed 1.5 h, depressurisation 1.0 h, finishing 0.5 h, extrusion 0.75 h): SRC-1
names the phases and the final temperature but gives no times, and no open source read gives
them. The dissolver's dosing and post-reaction take their times from R101's model. The recipe
sizes R-101 (16 m3, 67 % full); R-201 is sized by hand at 16 m3 from the 52 wt% charge (about
11.8 t a batch at an ASSUMED 1100 kg/m3, 10.7 m3), because core sizes no vessel over separators
and a conversion step (L-4). The salt tank T-102 between them holds the solution under nitrogen
and is no flowsheet step.

## D-004 Feeds and charge (2026-11-19)

One design specification (`rate`, core ADR 0070) varies the acid S1 for 8000 t/a of pellets
(S11); the water S2 and the diamine S4 follow at fixed mass ratios:
- water 1.652875 kg per kg of acid, so that the solution S5 is 52.0 wt% salt (SRC-1: 52 to
  53 %);
- diamine 0.799344 kg per kg of acid, 1.005247 mol per mol: the stoichiometric diamine and the
  diamine the steam strips (D-010), 2.69 kg per t of pellets, as SRC-1 says the stripped diamine
  is made up. Plants adjust the salt's balance by pH; the excess here is the loss, not a
  target.
The acid is charged as crystals at 298.15 K; the diamine molten at 333.15 K (it melts at
314.15 K, SRC-5), from a heated, nitrogen-blanketed tank (ASSUMED; it is also traded as an
aqueous solution, which would only shift water from S2 to S4). Per kg of pellets: 0.644 kg acid,
0.515 kg diamine, 1.064 kg water. The salt used, 1.156 kg per kg, is below the stoichiometric
1.159 because 0.58 % of the pellets are counted as salt (unlinked ends); the acid and diamine
together, 1.159 kg per kg, are about 0.6 % below SRC-1's 1.165 to 1.167 t/t, which carries the
plants' yield losses (off-grade, purges, start-ups) that this model does not.

## D-005 Neutraliser R101: semi-batch, kinetics and heat (2026-11-19)

The diamine is dosed at a constant rate over 2 h (ASSUMED) into the acid slurry at 338.15 K
(SRC-1: the solution kept at 65 C), isothermal, held until 0.99999 of the acid is neutralised
(`reactor: semibatch`). The acid's solubility (24 g/L at 25 C, 1600 g/L at 100 C, SRC-4) means
the slurry dissolves as the salt forms; core carries it pseudo-homogeneously (L-2). No open
kinetics or calorimetry of the neutralisation was found (searched 2026-11-19): the rate is an
ASSUMED fast second-order law (1 m3/(kmol s) at 338.15 K, 20 kJ/mol), so the dosing controls
the heat; the heat of reaction is ASSUMED -100 kJ per mol of salt (two acid-amine proton
transfers at about -50 kJ/mol), set high so that the screening is not optimistic. The acid's
heat of dissolution is not counted (no value read). Core writes the duty to cooling water, Q1
122.0 kW year average (the neutralisation less the dosed diamine's warming). The warming of the
slurry from 298.15 to 338.15 K on LP steam, Q2 58.7 kW, comes from scripts/balance.py.

## D-006 Autoclave: concentration X201, polycondensation R201, steam bleed X202 (2026-11-19)

The autoclave's cycle (SRC-1 9.2.2.3) is three steps in one vessel:
- **X201**, the concentration: 53.71 % of the solution's water evaporated, so that the salt is
  70.0 wt% (SRC-1's example), at about 383 K (the continuous concentrator's 110 C, SRC-1
  9.2.2.2; the salt's boiling-point rise not modelled). A component separator with a specified
  split (`recovery`), the diamine bound as salt kept in the liquid (ASSUMED).
- **R201**, the polycondensation, a conversion step (POLY: salt -> repeat unit + 2 water): the
  mass heated on hot oil from 383.15 to 548.15 K (SRC-1: about 275 C) while the steam is bled at
  a constant 1750 kPa(a) (ASSUMED: SRC-1 gives no batch pressure; the continuous reactor runs at
  about 18 bar, and the saturation temperature of water at 1750 kPa(a), 478.9 K by IAPWS-95,
  is just below the continuous reactor's 485 to 523 K, so the bleed starts as the mass heats
  past it). Conversion 0.995 of the salt's amide links
  (ASSUMED: a number-average degree of polymerisation of 200 structural units by Carothers'
  relation, Mn about 22 600 g/mol; no open target molar mass of a moulding or fibre grade was
  read; the finishing sets it in the plant). The unlinked 0.5 % stay as salt, the model's
  stand-in for the chain ends. Heat of reaction: SRC-2's apparent amidation enthalpy at its
  example point, -7870 cal/mol of links, two links per repeat unit, -65.9 kJ/mol, ASSUMED to
  hold for the salt, whose dissociation to free amine and acid is not counted (no open value).
  It is the most exothermic end of what SRC-2 gives: its eq. 24 (p. 430) makes the apparent
  enthalpy a function of the water mole fraction, most negative (about -7.9 kcal/mol) near
  x_W 0.2, zero at x_W 0.536 and endothermic above; at R201's inlet S7 (x_W 0.61 on SRC-2's
  basis of amine and carboxyl ends, links and water) it gives +3.2 kcal/mol. The step's net heat
  depends on how the links form as the water leaves: our average of eq. 24 over x_W falling
  evenly from 0.61 to 0 is -5.0 kcal/mol, which would raise Q4 by about 30 kW; a net heat of
  zero by 81 kW; eq. 24's inlet value held throughout (an extrapolation of a fit to prepolymer
  melts) by about 114 kW, 13 % of the hot oil. The value is kept because it is the conservative
  one for the thermal screening (R201's dT_ad of 73.1 K, D-011); for the hot oil it errs low.
  Core writes Q4 88.8 kW: the mass's sensible heat at the materials' heat capacities (183.8 kW)
  less the heat of reaction (81.0 kW) and less the autoclave agitator's 14 kW (P2), whose work
  ends as heat in the mass (core credits a step's other energy streams against its duty).
- **X202**, the steam bleed, depressurisation and finishing: 99.69 % of the water leaves, so
  that the melt holds 0.2 wt% water (ASSUMED; SRC-1 finishes slightly above atmospheric or under
  vacuum and gives no residual water), with all the free diamine (SRC-1 9.2.2.2 and 9.3.3.3: the
  steam strips diamine).
The evaporation heats come from scripts/balance.py, with water's enthalpies by IAPWS-95 (SRC-5)
at the vapours' declared states: Q3 438.6 kW (the solution warmed from 338 to 383 K and 577.4
kg/h of water taken from liquid at 383.15 K to vapour at 383.15 K and 101.325 kPa) and Q5
340.8 kW (657.9 kg/h of water and the diamine to S9's vapour at 548.15 K and 101.325 kPa). R201
heats S9's water as liquid at the constant 75.4 kJ/(kmol K) (Q4), so Q5 is the water's IAPWS-95
enthalpy change from liquid at 383.15 K to S9's state, 2562 kJ/kg, less that liquid heating;
Q3 + Q4 + Q5 carry the water's real path. A latent heat at 548.15 K would not do: it ends at
saturated vapour at 5946 kPa, 239 kJ/kg below vapour at 101.325 kPa, and the constant heat
capacity heats the liquid 58 kJ/kg less than IAPWS-95; together 54 kW too little in Q5 and Q6,
as this entry's first version had. The
bleed valve's let-down is isenthalpic, so the steam leaves the autoclave with S9's enthalpy;
vapour at the 1750 kPa(a) bleed pressure and 548.15 K would be 51 kJ/kg lower (9 kW). Why not core's models: no step-growth model with the end-group
equilibrium and vapour removal together (L-1); a still would need the vapour pressures of water
over the salt solution and the melt (no open data read) and gives no reaction (L-1). PA66's melt
heat capacity, 2.6 kJ/(kg K), is ASSUMED (no open measured value read); the salt's is the sum of
the acid's and the diamine's (ASSUMED). SRC-2's model (k_app, K_app as functions of the water
and carboxyl mole fractions) is the basis for a kinetic autoclave model once core can integrate
it with the water removal (L-1).

## D-007 Extrusion, quench and pellets (2026-11-19)

The finished melt is pressed out with nitrogen through a die as strands, quenched in water and
cut (SRC-1). E301 is a pass-through step: the melt cooled from 548.15 to 323.15 K (ASSUMED
pellet temperature), Q7 164.0 kW to the quench water and from it to cooling water
(scripts/balance.py); the heat of crystallisation is not counted (no open value, L-3). The
quench water's make-up and purge, the pellets' surface water and their drying under nitrogen to
a moisture specification (SRC-1) are not modelled: the pellets leave at the melt's 0.2 wt%.
Power for the cutter, the quench water pump, the centrifugal surface dryer (X-301: the strands'
surface water spun off, inside the boundary, unlike the drying under nitrogen in the silos) and
the conveying: 40 kW year average (ASSUMED). The heat of crystallisation goes to the quench water
and cooling water (Q7), not to the delivered heat (D-009).

## D-008 Separation (2026-11-19)

No separation beyond the autoclave's vapour removal (D-006) and the condenser (D-009): the salt
is not purified (no carbon treatment or filtration modelled, ASSUMED clean feeds), the
condensate is not stripped of its diamine (D-010).

## D-009 Utilities and heat (2026-11-19)

- Hot oil 593/573 K (ASSUMED, 45 K above the mass's 548 K) from a natural-gas-fired heater
  (SRC-1 9.3.3.4 names the diathermic oil heaters' fumes): Q3 + Q4 + Q5 = 868.2 kW, 0.859 kWh
  (3.09 MJ) per kg of pellets.
- LP steam 350 kPa(a) for the dissolver's warming: Q2 58.7 kW, 0.058 kWh/kg.
- Cooling water 298/308 K: Q1 122.0 kW (neutralisation), Q6 926.2 kW (the condenser E-201: the
  vapours of X201 at 383.15 K and of X202 at 548.15 K, both at 101.325 kPa, condensed and the
  condensate cooled to 313.15 K, water by IAPWS-95) and Q7 164.0 kW (strand quench), 1.200
  kWh/kg.
- Power 60 kW year average (ASSUMED: dissolver agitator 5 (P1), autoclave agitator 14 (P2),
  condensate pump 1 (P4), pelletising line 40 (P3)), 0.059 kWh/kg. The agitators' work ends as
  heat in their masses: core credits P2 against R201's hot-oil duty Q4 (D-006); R101's
  semi-batch duty Q1 does not net P1 (5 kW, under 5 % of Q1). The condensate pump is on E-201, so
  its power heats no mass in the model.
Total delivered heat and power, 3.52 MJ/kg (hot oil 3.09, LP steam 0.21, power 0.21), lie inside
SRC-1 Table 9.8's batch PA66 range (3.3 to 7.7 GJ/t), 0.22 GJ/t above its lower end, and below
Table 9.3's batch range (5.05 to 7.25 GJ/t). SRC-1 states the basis of neither table's total
(whether fuel and power are counted as primary energy, and whether site services are in); the
gap to Table 9.3 is not explained by this model. Not counted, each of which would only raise the
delivered heat: the vessels' steel heated each batch (every 10 t of steel at an ASSUMED 0.5
kJ/(kg K) cycling over the autoclave's 165 K adds about 0.16 MJ/kg; R-201's steel mass is not
estimated, L-4), the heat losses of the vessels and the hot-oil circuit (not estimated), the
hot-oil heater's efficiency (in the background, D-012) and the acid's heat of dissolution (no
value read, D-005; it would shift Q1 and Q2). PA66's heat of crystallisation (D-007, L-3) is
released in the quench water and adds to Q7 only. No heat integration: the condenser's 926 kW at
up to 548 K could raise steam or warm the next charge (open input).

## D-010 Wastes and emissions (2026-11-19)

The process condensate (1.223 kg/kg, 1.058 t per t of the salt used) is the solution water of
the 52 wt% salt (0.923 t per t of salt) and the reaction water (2 mol per mol of salt, 0.137 t/t).
SRC-1 9.3.3.3 gives about 1.2 t per t of salt for the two together; at its own 52 to 53 %
solution (9.2.2.1) the stoichiometry gives 1.02 to 1.06 t/t, so the BREF's figure probably
includes water this model does not carry (rinses, flushes, a more dilute charge: not stated).
Not modelled; 0.14 t/t more water would add about 0.16 kg per kg of pellets to evaporate, of the
order of 0.4 MJ/kg of hot oil. The condensate carries the stripped diamine. Its amount is set from SRC-1
Table 9.3: the batch process's COD before treatment, 5300 to 7300 g/t, mid 6300 g/t, taken as
diamine at its theoretical oxygen demand to CO2, water and ammonia (8.5 mol O2 per mol, 2.34 g
O2 per g), 2.69 kg of diamine per t of pellets (ASSUMED: SRC-1 also names cyclopentanone and
ammonia). It goes to biological treatment with nitrification and denitrification (SRC-1
9.3.3.3). The vents (tanks, the autoclave's purge and let-down, the condensate tank) go through
a water scrubber to air (SRC-1); their VOC (Table 9.3: 15 to 40 g/t) is not taken up as an
emission yet (lca/lca.yaml emission_exclusions). The nitrogen leaves with the vents.

## D-011 Thermal screening (2026-11-19)

`cheme process reactor-hazards` (core's Stoessel screening, SRC-7):
- **R101** (neutraliser): T_p 338.15 K, adiabatic rise 69.3 K, largest accumulation of the dosed
  diamine 0.87 % at the end of the dosing, MTSR 338.6 K against an MTT of 373.15 K (the normal
  boiling point of water, a lower bound of the salt solution's; R-101 vented under its nitrogen
  blanket to the scrubber). The fast assumed rate keeps the accumulation small; a slower real
  rate would raise it: the rate and heat need calorimetry (open input). No TD24, no class.
- **R201** (polycondensation): the mass is at its boiling point by design (the steam bleed), so
  a cooling failure is not the scenario; the hazards are the pressure and the heating medium.
  MTT ASSUMED 573.15 K, 15 K above the continuous finisher's 285 C (SRC-1 9.2.2.2), above which
  the melt degrades (SRC-2: Steppan's degradation forms ammonia, CO2 and cross-links). MTSR
  548.5 K (the 0.5 % of unlinked ends). Two scenarios govern, neither a runaway:
  - the bleed valve failing closed while the hot oil heats (overpressure): relief sizing is a
    basic-stage task (open input);
  - the hot oil overheating the mass: the oil is supplied at 593.15 K, 20 K above the MTT, so a
    hot-oil temperature or flow control failing open, above all in the finishing, when the
    water is gone and no longer holds the mass at its boiling point, can take the melt above the
    MTT. Safeguard required: a high-temperature trip on the mass (and the hot-oil supply) that
    closes R-201's hot-oil supply below the MTT; its set point and the cause-and-effect entry
    are basic-stage work (open input; control/cause-effect.yaml has no interlocks yet).
  R-201's design temperature is set at 623.15 K (ASSUMED: the hot oil's 593.15 K supply, which
  its jacket and coils see in normal operation, plus a 30 K margin), above the MTT, so that the
  vessel is not the limit when the trip acts.
- The diamine: corrosive, flash point 80 C, explosive limits 0.7 to 6.3 % (SRC-4): its tank and
  the dissolver are nitrogen-blanketed and kept at 333 to 338 K, below the flash point.
- R101's dosing: a trip that stops the diamine on high temperature or a stopped agitator (the
  usual semi-batch safeguard against accumulation) is not yet defined; it is basic-stage work
  with the cause-and-effect list (open input).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml`, written with `cheme assess lca --write`: per kg of pellets, the flowsheet's
year averages. The entry's own lca/mappings.yaml links the acid to `adipic-acid-1` (the dataset
with catalytic N2O decomposition), the nitrogen (a consumable, 70 kg a batch ASSUMED, lca.yaml)
to `asu-1`, the hot oil as heat from natural gas (as polystyrene-1) and the LP steam as heat.
The library's shared lci/mappings.yaml links the water (market for water, deionised, with
demineralised-water-1 as the Atlas producer), the power (medium-voltage electricity), the
cooling water (utility-cooling-tower) and the condensate (utility-wwtp) in the Atlas build. Gaps
of the Atlas build (`build_lci.py --strict`): the diamine (no library producer: an adiponitrile
hydrogenation entry is the next step of the chain) and the nitrogen's disposal with the vents.
The screening LCA of core (lca/gaps.csv, with the packaged factors only) has no factor for most
of these exchanges and lists them as missing there. ISIC 2013. No rinses: the autoclave is not washed between batches of one grade (D-013).

## D-013 Dedicated train (2026-11-19)

Library ADR 0035: one dedicated train of R-101 and R-201 making one grade. SRC-1's batch plants
run several autoclaves in sequence and change grades and copolymers between campaigns; neither
is modelled.

## Method and dependency table

| quantity | method | depends on |
|---|---|---|
| feeds S1, S2, S4 | design specification `rate` (core ADR 0070) | 8000 t/a, 52 wt% salt, the stripped diamine (D-002, D-004, D-010) |
| salt solution S5, Q1 | semi-batch R101 (core) | NEUT's ASSUMED rate and heat (D-005) |
| S6, S7 | component separator X201 | the 70 wt% target (SRC-1, D-006) |
| S8, Q4 | conversion step R201 (core) | conversion 0.995, the heat of POLY (D-006) |
| S9, S10 | component separator X202 | 0.2 wt% water, all free diamine (D-006) |
| Q2, Q3, Q5, Q6, Q7 | scripts/balance.py (library ADR 0027) | streams, materials' heat capacities, SRC-5 latent heats (D-005 to D-009) |
| batch, cycle, R-101 | recipe (core) | ASSUMED phase times (D-003) |
| MTSRs | reactor-hazards (core) | D-005, D-006, D-011 |

## Core features used (core 1.13.0)

Semi-batch with a dosed liquid and its duty (ADRs 0050, 0059, 0063); conversion step duty
(ADR 0059); component separators and a design specification (ADR 0070); recipe with unit
procedures over several steps and `from:` times (ADRs 0051, 0052, 0057); reactor-hazard
screening of the semi-batch and the conversion step; LCA with consumables per batch (ADR 0053).

## Core limits hit (each a candidate core issue)

- **L-1** No step-growth polymerisation model: core cannot integrate an equilibrium-limited
  polycondensation with the water's removal in one vessel (SRC-2's activity-based k_app and
  K_app, the end groups as components, a vapour-removal rate). The autoclave is split into two
  specified separators and a conversion step with an ASSUMED conversion; the molar mass is not
  predicted. A batch reactor with a vent of a formed volatile driven by pressure (the steam
  bleed) would be the core feature.
- **L-2** A dissolving solid reactant is carried as a liquid in the semi-batch (the acid's
  solubility not checked).
- **L-3** One constant heat capacity per component and no heat of fusion/crystallisation: the
  melt's sensible heat and the pellets' crystallisation heat (Q7) are approximate.
- **L-4** Core sizes no vessel over separators and a conversion step: R-201 is sized by hand,
  and its jacket and the hot oil's heat-transfer time are not checked against the 1.5 h phase.
- **L-5** No property package for the salt, the polymer or the diamine (`property_method` a
  placeholder): no stream density, enthalpy or phase is calculated.

## Open inputs

- Calorimetry of the neutralisation (heat, rate) and of the salt's polycondensation; the
  decomposition onset of the melt (TD24).
- The autoclave's phase times, bleed pressure, finishing pressure and residual water from a
  licensor or plant data; the target molar mass of the grade.
- Relief of R-201 (bleed valve fails closed with the heating on) and R-101.
- R-201's high-temperature trip on the hot oil below the MTT, and R-101's dosing trip on high
  temperature or a stopped agitator, with their cause-and-effect entries (D-011).
- Heat recovery from the condenser E-201; the pellets' drying under nitrogen and the quench
  water loop.
- A library producer of hexamethylenediamine (adiponitrile hydrogenation).
