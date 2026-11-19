# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes. Carbon
dioxide by direct air capture (DAC) with aqueous KOH and a calcium caustic recovery loop, issue
ChemE-as-Code/process-library#518, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD from a closed-form steady-state balance, equipment list,
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout (the concept gate
`layout-plot-plan` stays open on purpose, as in biodiesel-1), HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin v1.13.0 (b97a833). The issue
proposed the id `carbon-capture-2`; the entry is `direct-air-capture-1`, the id the work was
assigned under (the product, CO2 from air, names it better than a variant number of
carbon-capture-1, which conditions a point-source vent). Templates: `biodiesel-1` (a continuous
Tier 2 entry: structure, LCA), `kraft-pulp-1` (a calcium causticising loop closed by a balance
script, ADR 0027). Requires cheme-as-code 1.13 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied (no table, figure or text). "Read" means
the passage named was read in this work (PDF text extracted and read). Page numbers of SRC-1 are
the journal's; SRC-2's are its exhibits and sections.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Keith, D. W.; Holmes, G.; St. Angelo, D.; Heidel, K. (2018) A Process for Capturing CO2 from the Atmosphere. Joule 2, 1573-1594, doi:10.1016/j.joule.2018.05.006; copy https://www.jefftk.com/keith2018.pdf | p. 1574 and Fig. 1: two loops, liquor about 1.0 M OH-, 0.5 M CO3--, 2.0 M K+; the four reactions with enthalpies per mol C (contactor -95.8, pellet reactor -5.8, calciner +178.3, slaker -63.9 kJ/mol). Fig. 2: air 251 000 t/h with 0.060 % CO2, 23.00 % O2, 75.96 % N2, 0.98 % H2O (mass); liquor 2.00 K+, 1.10 OH-, 0.45 CO3-- and a stream at 2.01 / 0.68 / 0.66 mol/L; oxidant 58.5 t/h at 95.60 % O2, 4.40 % N2; calciner gas 13.4 t/h CH4, 670 GJ/h; pellets 300 t/h CaCO3 with 5.4 t/h K2CO3; CaO stream with 24.7 t/h CaO and 186 t/h Ca(OH)2 after the slaker; product 171 t/h, 97.12 % CO2, 1.36 % O2, 1.51 % N2, 0.01 % H2O at 151 bar; 112 t-CO2/h captured; a cooling water exchanger (supply and return) drawn in the air contactor basin. Table 1: contactor 1.3 mm/s, 1.4 m/s, 210 m2/m3, 9.7 Pa/m, 7 m, fans 61 and pumping 21 kWh/t, 74.5 % captured, 22 t/(m2 a); pellet reactor 1.65 cm/s, 4.5 m bed, 20 kg Ca/(m2 h), 90 % Ca retention, 27 kWh/t; calciner 710 kg/m3, 900 C, 98 %, 4.05 GJ/t; slaker 11 % pellet water carry-over, 300 C, 77 kWh/t produced and 32 kWh/t consumed, 85 % conversion; ASU 238 kWh/t-O2 at 120 kPa; absorber 90 %, 1 kPa; compressor 132 kWh/t; the table's note: energy per t of CO2 processed by the unit. p. 1578: 30 % lime slurry, lime the limiting reagent, about 10 % of Ca as fines. p. 1580: CaO at 674 C, pellets at 300 C, 4.07 GJ/t-CaO = 5.25 GJ/t-CO2 from calcination, about 78 % thermal efficiency; steam slaking at 300 C. p. 1581: four-stage centrifugal compressor with glycol dehydration to 15 MPa; 4.7 t water per t CO2 at 20 C and 64 % RH; 1 % of the circulating Ca purged per cycle. p. 1584: airborne KOH at the pilot contactor's outflow below 0.6 mg/m3 of air. Table 2: scenarios A to D (A gas only 8.81 GJ/t; C 5.25 GJ/t and 366 kWh/t at 15 MPa), 90 % utilisation | read in full (PDF text); CC BY-NC-ND 4.0: facts and numbers only, in our own form, no figure or table reproduced | D-001 to D-010 |
| SRC-2 | NETL (2022) Direct Air Capture Case Studies: Solvent System. DOE/NETL-2021/2864, National Energy Technology Laboratory, https://netl.doe.gov/projects/files/DirectAirCaptureCaseStudiesSolventSystem_083122.pdf | Exhibit 3-2: ISO ambient, 403.9 ppmv CO2. Exhibit 5-2: Case 1 903 970 t/a net, 909 225 t/a gross from air, 85 % capacity factor, natural gas 25 613 kg/h (calciner 15 981, NGCC 9 632), 78 MW gross, 65.1 MW auxiliaries, 13.2 MW net, NGCC flue gas CO2 captured 187 131 t/a (the case summary, PDF p. 9: by an absorber on a slip stream of the contactors' KOH). Exhibit 5-5 carbon balance (contactor inlet 44 744 kg C/h, calciner natural gas 11 543, product 51 447, CO2 dryer vent 13, pellet solids 652, fines 81, seed 470). Exhibit 5-6 sulfur balance: 0.2 kg/h of sulfur in the calciner's gas, out through the CO2 dryer vent. Exhibit 5-7 water (contactor make-up 14 m3/min, pellet washer 10 m3/min). Section 5.1.1: KOH slip from the contactors possible, not quantified; the calciner's SO2 taken to leave through the CO2 dryer vent. Section 5.2 account 15: 277 contactors, 178 pellet reactors of 22 t/d, two slakers, two calciners, ASU 1700 t/d at 95 %. Exhibit 5-11: KOH 69.8 ton/d, CaCO3 104 ton/d (US short tons), solids to disposal 227 ton/d (KOH, H2O, CaCO3, K2CO3) | read (PDF text of sections 3 to 5); US government report, facts only | D-001, D-005, D-010, cross-checks |
| SRC-3 | processes/asu-1, carbon-capture-1, kraft-pulp-1, biodiesel-1 (this library) | asu-1's GOX product; carbon-capture-1's CO2 grade; kraft-pulp-1's balance-script pattern; biodiesel-1's structure | library, internal | D-008, D-011 |

Searched and not found openly (2026-11-19): an open stream-level balance of a solid-sorbent
(TVSA) DAC plant read in this work, liquor density data for KOH-K2CO3 at these concentrations
(read here), and a quantified KOH aerosol loss.

## D-001 Route and boundary (2026-11-19)
Decision: liquid-solvent DAC of SRC-1: aqueous KOH in cross-flow air contactors, causticisation
with slaked lime in fluidised pellet reactors (CaCO3 grown on seed pellets), a steam slaker that
dries the pellets and slakes the hot quicklime, an oxy-fired circulating fluidised bed calciner at
900 C on natural gas and 95.6 wt% oxygen, CO2 compressed to 15 MPa and glycol-dried. The
energy configuration is SRC-1's scenario C: natural gas to the calciner only, grid electricity.

Rejected alternatives:
- SRC-1 scenario A / SRC-2 Case 1, gas only with an on-site gas turbine (or NGCC) whose flue gas
  CO2 is taken by an absorber on the same liquor: 8.81 GJ of gas per t and no grid power. It adds
  a power island (gas turbine, HRSG, steam turbine) and a flue-gas absorber; the library keeps
  power generation in its own entries (power-generation-1), so the plant takes grid power here.
  SRC-2's figures are kept as cross-checks (D-002, D-005).
- SRC-1 scenario D (0.1 MPa product, zero-cost oxygen): not a deliverable product.
- Solid-sorbent DAC (amine-functionalised sorbents, temperature-vacuum swing): no open
  stream-level balance was read in this work; left for its own entry.
- Electrochemical or bipolar-membrane regeneration of the carbonate liquor: no open plant-scale
  balance read; co2-electrolysis-bpm-1 covers a related cell.
- A conventional lime kiln and water slaking as in kraft recausticising (kraft-pulp-1): SRC-1
  p. 1580 credits the pellets' low water and the oxy-fired CFB with a higher thermal efficiency
  and a pure CO2 off-gas; an air-fired kiln would dilute the CO2 with nitrogen.

Boundary: gate to gate, from air, natural gas, oxygen, KOH, CaCO3 seed and process water to the
CO2 product at 15.1 MPa, the depleted air, the filter cake purge, the liquor bleed and the
condensate, with grid power; the CO2 train's cooling goes to the contactor basins (D-009). Outside: the air separation unit (oxygen bought, D-011), CO2 transport
and storage, water treatment, the slaker's steam cycle (D-006) and the heat recovery of the
calciner's off-gas (D-007).

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: the air flow of SRC-1 Fig. 2, 251 000 t/h, with 74.5 % of its CO2 captured: 112.2 t/h
(SRC-1 Fig. 2 states 112 t-CO2/h). 7884 h/a, the 90 % utilisation SRC-1 Table 2 assumes
(ASSUMED for this plant): 885 kt/a from the air, 1.17 Mt/a of product. SRC-2 Case 1 captures
909 kt/a gross from the air at 85 %, the same scale. Product: 148.5 t/h of 97.0 wt% CO2 at
15.1 MPa (D-008).

## D-003 Contactor and liquor loop (2026-11-19)
Decision: 74.5 % of the air's CO2 captured (SRC-1 Table 1) by CO2 + 2 KOH -> K2CO3 + H2O; 4.7 t of
water evaporated per t of CO2 captured at 20 C and 64 % RH (SRC-1 p. 1581). The lean liquor
returned to the contactors holds 1.10 mol/L KOH and 0.45 mol/L K2CO3 (SRC-1 Fig. 2) at a density
of 1.10 kg/L (ASSUMED, no density read); it is circulated for a carbonate swing of 0.21 mol/L,
our reading of SRC-1 Fig. 2's second liquor stream (0.66 mol/L carbonate) as the pellet reactor's
feed (ASSUMED reading): 12 140 m3/h. The rich liquor leaves at 21 C (SRC-1 Fig. 2), the lean
liquor returns at about 23 C (D-004). The circulation over the packing within the contactors'
basins is internal to C-101 and not a stream. The liquor is an inventory of dissolved KOH and
K2CO3, not a speciation (L-1). The two loops are closed by stoichiometry in
scripts/dac_balance.py (core has no electrolyte or crystallisation model to iterate them): at
steady state the calcium precipitated equals the carbonate captured less the carbonate that
leaves with the purge and the bleed.

Energy (revised 2026-11-20 after review; hand balance printed by scripts/dac_balance.py): the air
takes up the absorption heat (2549 kmol/h x 95.8 kJ/mol = 67.8 MW), the fans' and pumps' power
(9.2 MW), the heat the lean liquor brings from the pellet reactor together with the evaporated
liquid's own heat (39.7 MW) and the CO2 train's cooling (Q1, 38.7 MW, D-009): 155.4 MW. With the
527 t/h evaporated (0.00990 to 0.01202 kg water per kg dry air) the depleted air (S10) leaves at
about 17 C, from moist-air enthalpies with round constants (dry air 1.006 and vapour 1.86
kJ/(kg K), 2501 kJ/kg at 0 C, ASSUMED). That is close to saturation: at 16.96 C the saturation
humidity is 0.01210 kg/kg (water vapour pressure 1.933 kPa, IAPWS-95 by the package chemicals
1.5.2, `iapws95_Psat`), so about 99 % RH. The first version gave the air 19 C (SRC-1 Fig. 2); with
this evaporation that needs about 300 MW, which nothing in this plant supplies (SRC-1's plant
rejects heat into its contactor basin through a cooling water exchanger, Fig. 2, and its scenario
A has a power island). Without Q1 in the basins the air could not take up 4.7 t/t at all (it would
leave supersaturated): SRC-1's 4.7 t/t at 20 C and 64 % RH is at the limit of the heat this plant
rejects to its contactors, and a plant that rejects less heat there evaporates less (L-3). The
water the CO2 train's cooling evaporates is part of the contactors' evaporation, counted once: no
cooling tower.

## D-004 Pellet reactor, washing and lime slurry (2026-11-19)
Decision: the rich liquor causticised with a 30 wt% Ca(OH)2 slurry (SRC-1 p. 1578); the lime is
the limiting reagent and all of it reacts (ASSUMED complete); the 15 % of the CaO not slaked in
the slaker slakes in the slurry. About 10 % of the calcium leaves the bed as fines (SRC-1
p. 1578); they are filtered and joined to the pellets (SRC-1 Fig. 2 treats them so), so the model
has one pellet stream. Washed pellets carry 1.8 kg K2CO3 per 100 kg CaCO3 (SRC-1 Fig. 2: 5.4 on
300 t/h) and 11 wt% water (SRC-1 Table 1); the K2CO3 passes the calciner and returns with the
lime. The make-up water enters at the pellet washers (S2) and closes the loop's water balance;
the slurry water (S4) is fresh water too. SRC-1 Fig. 2's lime slurry carries dilute liquor; the
filtrate's return is not modelled (L-2). Energy (hand balance, round heat capacities ASSUMED,
scripts/dac_balance.py): the causticisation (2541 kmol/h x 5.8 kJ/mol = 4.1 MW), the slaking of
the CaO left (381 kmol/h x 63.9 kJ/mol = 6.8 MW) and the warm slurry (60 C, ASSUMED) raise the
outlets from the rich liquor's 21 C to about 23 C; the lean liquor carries 28.3 MW of it to the
contactors (D-003).

## D-005 Make-ups, purge and bleed (2026-11-19, revised 2026-11-20)
Decision: KOH 0.01792 and CaCO3 seed 0.02670 t per t of CO2 taken up by the liquor: SRC-2's
consumables (69.8 and 104 short tons a day, Exhibit 5-11, at 100 % capacity: 2.638 and 3.931 t/h)
over the CO2 its KOH liquor takes up, 147.2 t/h: 909 225 t/a from the air and 187 131 t/a from the
NGCC flue gas, whose absorber runs on a slip stream of the contactors' KOH (Exhibit 5-2 and the
case summary), at 85 % of 8760 h. Exhibit 5-5 gives about the same calcium-loop throughput
(product carbon 51 447 less the calciner gas's 11 543 kg C/h: 146.2 t CO2/h). Here the liquor takes
up the air's CO2 only, so the rates apply to the 112.2 t/h captured (ASSUMED proportional): 2.01
t/h of KOH and 3.00 t/h of seed. The seed is 1.15 % of the circulating calcium, against SRC-1
p. 1581's purge of 1 % a cycle. The first version divided by the air's CO2 alone (122.1 t/h) and
was 20 % high (review of 2026-11-20). The KOH loss is tied to the liquor's throughput, not to the
air flow: SRC-1 p. 1584 measured airborne KOH below 0.6 mg/m3 at the pilot contactor's outflow,
which on this plant's air (about 2.1 million m3/h at an ASSUMED 1.2 kg/m3) is below 0.13 t/h, a
few per cent of the make-up, so drift is not the main loss; it is not modelled as an emission
(L-6).

The seed's calcium leaves as CaCO3 in a drained filter cake holding 30 wt% lean liquor (ASSUMED):
4.28 t/h (S22). Its liquor carries only 0.14 t/h of potassium salts; the rest of the make-up's
potassium leaves as a bleed of lean liquor to treatment (S23, 18.4 t/h at 11.3 wt% KOH and K2CO3;
the route ASSUMED, L-6). The first version put all of the make-up's potassium in the cake with 30
wt% water, about 50 wt% salts in the cake's liquid against 11 wt% in the liquor, which a cake
drained from the liquor cannot hold. SRC-2 lists KOH and K2CO3 in its 227 short tons a day of
solids to disposal (8.6 t/h with the seed, Exhibit 5-11) without saying how a cake holds them;
this entry's cake and bleed depart from that. SRC-2 does not say how the KOH is lost (section
5.1.1: slip possible, not quantified).

## D-006 Steam slaker (2026-11-19)
Decision: 85 % of the CaO slaked (SRC-1 Table 1) at 300 C; the pellets leave dry at 300 C to the
calciner (SRC-1 p. 1580). The pellet moisture (32.6 t/h) covers most of the slaking water; the
rest, 6.3 t/h, is fed as water (S8, ASSUMED as liquid water; SRC-1 fluidises with recirculated
steam). SRC-1 recovers the slaking heat as 77 kWh/t of power; the steam cycle is outside the
boundary and not credited (L-5), so the power import is higher than SRC-1's by that amount.
Energy (revised 2026-11-20 after review; hand balance, round heat capacities ASSUMED,
scripts/dac_balance.py): the slaking (2160 kmol/h x 63.9 kJ/mol = 38.3 MW) and the hot lime at
674 C (24.9 MW) less the pellets dried and heated to 300 C (19.2 MW) and the lime leaving at 300 C
(18.1 MW) leave a surplus of 25.7 MW, the energy stream Q3 to the free terminal AMBIENT. SRC-1
raises steam with it; here it is neither used nor credited.

## D-007 Calciner (2026-11-19)
Decision: 98 % of the CaCO3 calcined at 900 C (SRC-1 Table 1); 5.25 GJ (LHV) of natural gas per t
of CO2 calcined (SRC-1 p. 1580), the gas taken as methane at 50.0 GJ/t (SRC-1 Fig. 2: 670 GJ/h for
13.4 t/h): 11.74 t/h. Oxidant 4.37 t per t of CH4 at 95.6 wt% O2 and 4.4 wt% N2 (SRC-1 Fig. 2),
about 4.6 % excess O2. Complete combustion (ASSUMED). The fired heat (163.1 MW) and the pellets'
heat at 300 C (19.2 MW) less the calcination (125.9 MW), the hot lime to the slaker at 674 C
(24.9 MW) and the off-gas at 373 K (3.7 MW) leave 27.8 MW: the off-gas heat recovered to the oxygen
and steam, and losses (77 % of the fired heat goes to the calcination, SRC-1 p. 1580 states about
78 %). It is one lumped energy stream (Q2) to a free terminal, not split (L-4); round heat
capacities ASSUMED (scripts/dac_balance.py). Revised 2026-11-20: the first version's 37.2 MW was
the fired heat less the calcination alone and so also counted the hot lime's heat, which the
slaker's balance carries (D-006).

## D-008 CO2 compression and drying (2026-11-19)
Decision: the off-gas (assumed at 373 K after the calciner's heat recovery) cooled, compressed in
four stages to 15.1 MPa and dried with glycol (SRC-1 p. 1581) to 0.01 wt% water (SRC-1 Fig. 2);
the rest of the water knocked out (S21, 26.4 t/h). No CO2 is lost in the train (ASSUMED), and
the calciner gas's sulfur, NOx and CO stay in the product (ASSUMED): a departure from SRC-2, whose
CO2 dryer vent releases 13 kg C/h (Exhibit 5-5) and the calciner gas's sulfur, 0.2 kg/h as S, about
0.4 kg/h as SO2 (Exhibit 5-6), to air. The
product, 97.0 wt% CO2 (95.6 mol%) with the oxidant's N2 and the excess O2, is a registry grade of
its own (carbon-dioxide/dense-151bara-97), not carbon-capture-1's 99.95 mol% pipeline grade; a
consumer that needs that grade would add a purification (not designed).

## D-009 Power and cooling (2026-11-19, revised 2026-11-20)
Decision: power from SRC-1 Table 1's specific consumptions: fans 61 and contactor pumping 21 kWh
per t captured, pellet reactor 27 kWh/t captured, slaker 32 kWh/t calcined, compressor 132 kWh per
t of CO2 in the product (the table's note: per t of CO2 processed by the unit; the first version
applied it per t of product gas, 3 % high): 34.8 MW, 310 kWh per t of air CO2. SRC-1 scenario C
states 366 kWh/t; the difference
is mainly the ASU's power (here in the bought oxygen, about 238 kWh/t-O2 x 0.457 t = 109 kWh/t),
less the 77 kWh/t from the slaking heat not credited here, and balance-of-plant loads not itemised
in SRC-1 Table 1. The CO2 train's cooling, 38.7 MW, a hand estimate (Q1's source, printed by
scripts/dac_balance.py): the compression work (19.0 MW), the condensation of the combustion water
(17.6 MW) and the gas cooled from 373 to 313 K (2.1 MW), with round properties (ASSUMED); the first
version stated 39.19 MW for parts that added to 39.25 MW. It goes through a closed cooling-water
circuit (about 25/35 C, ASSUMED) to exchangers in the contactor basins, our reading of the cooling
water exchanger SRC-1 Fig. 2 draws in the air contactor basin, and the air takes it up with the
evaporation (D-003); no cooling tower. The liquor at 21 to 23 C leaves an approach of only a few K
at the circuit's cold end, to be checked in basic engineering.

## D-010 Equipment (2026-11-19)
Decision: one tag per step with the counts and sizes of SRC-1 and SRC-2 scaled
(equipment/equipment-list.yaml): contactor inlet area about 40 200 m2 from SRC-1's 22 t/(m2 a);
pellet reactor bed area about 5 090 m2 from 20 kg Ca/(m2 h); two slakers and two calciners as
SRC-2; a four-stage CO2 compressor. Design pressures, temperatures and materials are left to
basic engineering.

## D-011 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `lca/lca.yaml` per kg of CO2 product S20. The air is a resource: its CO2 is `Carbon
dioxide, in air` (non-fossil), the CO2 left in the depleted air returns as non-fossil CO2
(`trace_emissions: false`, since the plant mixes air carbon and the fuel's fossil carbon in one
product); the product's carbon is declared 77.6 % from the air (2541.35 of 3273.34 kmol/h; the
seed's carbon leaves with the purge), so the fuel's CO2 is fossil carbon in the product, not an
emission. The purge's carbon is declared 1.7 % from the air (the K2CO3 of its cake liquor, 6.3 of
365.8 kg C/h; the rest is the seed's fossil carbonate) and the bleed's 100 %. Revised 2026-11-20:
the first version declared neither, so core gave the purge the pool's 96 % biogenic share and the
stated PCF claimed 1.3 % more removal than the inventory's net uptake of air CO2; now the PCF
including biogenic CO2 equals that net uptake. Links (lca/mappings.yaml): the oxygen to asu-1's
GOX (99.5 mol% at 30 barg, a higher-purity and higher-pressure proxy for a dedicated low-pressure
ASU), natural gas, KOH (100 %), crushed limestone for the seed, the purge to inert-waste landfill
(ASSUMED inert; the cake's alkaline liquor may need a residual-material landfill), the process
water to the shared water entry (a conservative proxy: demineralised water, which the Atlas build
takes from demineralised-water-1's market), and the condensate and the liquor bleed to the shared
wastewater entry (treatment by mass; the bleed's neutralisation is not represented). Revised
2026-11-20: the first version called the process water and the condensate gaps, but the shared
water entry linked both, the condensate as deionised water consumed; each now has an explicit
mapping. Power links to the library default in the Atlas build; there is no cooling-water
utility (D-009).
No net-removal figure is claimed: storage, transport and the backgrounds are not assessed, and the
calciner's fuel is fossil.

## D-012 Hazards (2026-11-19)
Potassium hydroxide liquor (about 11 wt% KOH and K2CO3) is corrosive to skin and eyes, and
contactor drift or aerosol could carry it (SRC-2 section 5.1.1: possible, not quantified);
quicklime and slaked lime are corrosive dusts and quicklime reacts exothermically with water
(the slaker and the lime handling); the calciner is an oxy-fuel natural gas burner at 900 C
(oxygen-enriched atmosphere, flammable gas, hot solids at 674 to 900 C); the product is CO2 at
15 MPa (asphyxiant, dense-phase release and cooling on expansion); the depleted air and the
compressor area need CO2 and O2 monitoring. No exothermic batch reaction: no runaway screening
applies (continuous plant). Hazards for the next stage: oxygen service of the calciner's supply,
the slaker's steam and hot lime, high-pressure CO2, and caustic handling. No HAZOP at this stage.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme (checked) | cheme validate, process streams, propagate --check |
| loops (liquor, calcium) | by script: closed-form steady state | scripts/dac_balance.py, ADR 0027, D-003 |
| conversions, capture, carry-overs | sourced (SRC-1) or ASSUMED | D-003 to D-008 |
| power | by hand: SRC-1 specific consumptions | D-009 |
| energy: contactor air outlet, pellet reactor outlet, slaker surplus, calciner heat, CO2 train cooling | by hand: energy printout of scripts/dac_balance.py, round heat capacities | D-003, D-004, D-006, D-007, D-009 |
| stream properties, conversion duties | not done: no package covers the electrolyte and solids | L-1, L-4 |
| LCI inventory | done, most backgrounds linked in the Atlas build | D-011 |

## Core features used (core 1.13.0)

- Reacting steps with several reactions and outlets checked by extents (C101, R201, SL301,
  F401) and a step `conversion:` override (R201's SLAKE).
- Balance-script provenance (library ADR 0027) for every material stream.
- `cheme assess lca` with `resource: true` for the air, an elementary resource `in-air` mapping,
  `carbon_accounting` with a declared product biogenic fraction and `trace_emissions: false`,
  and emission exclusions.

## Core limits hit (each a candidate core issue)

- L-1: no aqueous electrolyte model for KOH-K2CO3 (activities, density, vapour pressure of the
  liquor) and no solids handling in the thermo flash: the liquor is an inventory of neutral
  KOH and K2CO3, its density ASSUMED, and `cheme process props` covers no stream.
- L-2: no reactive crystallisation (pellet growth, fines, calcium retention) and no recycle of a
  filtrate: the pellet reactor is a complete conversion with specified carry-overs, and the
  loops are closed in a script rather than as tears of `propagate`, which needs a purge or
  make-up specification per recycled species that the closed calcium and potassium loops lack.
- L-3: no gas-liquid mass-transfer model for a cross-flow packed contactor: the 74.5 % capture
  and the 4.7 t/t evaporation are SRC-1's, not predicted from the packing, air velocity and
  ambient humidity; the evaporation is only checked against the heat the contactors take up
  (D-003).
- L-4: no energy balance on solids reactors or on the liquor: the calciner's fuel is a specific
  energy from SRC-1, its remaining heat one lumped stream (Q2), and core computes no duty for the
  contactor, the pellet reactor or the slaker. Their heat is balanced by hand in the energy
  printout of scripts/dac_balance.py with round heat capacities (D-003, D-004, D-006, D-007): it
  gives the lean liquor's and the depleted air's temperatures and the slaker's surplus (Q3).
  `cheme process furnace` covers lime kilns and calciners and could take F401 in a next stage.
- L-5: the slaker's heat recovery to power (77 kWh/t in SRC-1) is not modelled: its 25.7 MW
  surplus (Q3) goes to a free terminal.
- L-6: the KOH loss route (aerosol, drift, entrainment) is not modelled: the make-up's potassium
  leaves with the cake's liquor and a liquor bleed (D-005); contactor drift, which SRC-1's
  measurement bounds to a few per cent of the make-up, is not an emission here.

## Open inputs
A liquor density and speciation model; the pellet reactor's retention and the fines' route from
a pilot; the KOH loss route and rate; the bleed's treatment; the approach of the cooling-water
circuit in the contactor basins; the ASU design or a merchant oxygen grade at 95 %; the site's
climate (evaporation) and power mix; a TEA (SRC-1 Table 2, SRC-2 section 5.3 give costs); CO2
purification to a pipeline grade; P&IDs, layout, HAZOP.
