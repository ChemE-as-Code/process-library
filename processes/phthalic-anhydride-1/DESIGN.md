# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Phthalic anhydride by gas-phase oxidation of o-xylene, issue
ChemE-as-Code/process-library#480. Concept stage: design basis, balanced BFD/PFD with core's
conversion models for the reactor and the oxidiser, the duties core cannot calculate by hand,
and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` at c241d8d, core pin 0e85885 (cheme-as-code 1.12.0).
Templates: `phosgene-1` (multitubular gas-phase reactor, condensation, thermal oxidiser) and
`oxalyl-chloride-1` (source register, limits, LCA layout).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US EPA (1983, reformatted 1995) AP-42, Compilation of Air Pollutant Emission Factors, 5th ed., Vol. I, section 6.5 Phthalic anhydride, https://www.epa.gov/sites/default/files/2020-10/documents/c06s05.pdf | 6.5.1: o-xylene (or naphthalene) oxidised with air over vanadium pentoxide in fixed-bed tubular reactors at 340-385 C, small SO2 additions keep the catalyst active, molten salt removes the heat to a steam system; about 1.0 lb PA per lb o-xylene; switch condensers alternately cooled and heated; pre-treatment dehydrates phthalic acid and drives off water, maleic anhydride and benzoic acid; vacuum distillation to 99.8 wt%; liquid PA stored at 150 C under dry nitrogen; maleic anhydride the only by-product recovered. 6.5.2: the condenser vent is the main source (particulates, SO2, CO; CO over half); water scrubber with thermal incinerator 96 %, thermal incinerator alone about 95 % for o-xylene plants; pre-treatment and distillation vents go to the same devices. Table 6.5-1 (rating B): main process stream uncontrolled particulate 69 kg/Mg (PA, maleic anhydride, benzoic acid), SO2 4.7, CO 151; with thermal incinerator 4, 4.7 and 8; pre-treatment 6.4 and distillation 45 kg/Mg uncontrolled particulate | read (US government work, public domain); facts only | D-001, D-005, D-007, D-009, D-012, benchmark |
| SRC-2 | US 8 859 459 B2, BASF SE, published 2014-10-14: Multilayer catalyst for preparing phthalic anhydride and process for preparing phthalic anhydride, https://patents.google.com/patent/US8859459B2/en | description: the oxidation over V2O5/TiO2 run at about 4 Nm3/h air per tube and loadings up to 100 g/Nm3, tubes in a salt melt; fill heights of 250-350 cm; examples in a 25 mm tube with four catalyst layers, hot spots kept below 450 C | read (Google Patents); patent, facts only | D-002, D-004, D-005, equipment |
| SRC-3 | US 7 592 293 B2, Süd-Chemie AG, published 2009-09-22: Method for producing a multi-layer catalyst for obtaining phthalic anhydride, https://patents.google.com/patent/US7592293B2/en | description: shell-and-tube reactor, salt melt (preferably NaNO2/KNO3 eutectic) whose heat can raise steam; 300-450 C (preferably 340-400 C), 0.1-2.5 bar gauge (preferably 0.3-1.5), 30-150 g/Nm3, tubes about 2.5-3.5 m; examples at about 1450 mbar total pressure, 25 mm tubes, 4 Nm3/h | read (Google Patents, first 100 000 characters); patent, facts only | D-004, D-005, D-010 |
| SRC-4 | EP 0 574 855 A2, Air Products and Chemicals, published 1993-12-22 (withdrawn): Elevated pressure phthalic anhydride process, https://patents.google.com/patent/EP0574855A2/en | background: conventional loadings 40-130 g/Nm3; reactor exit about 700-720 F at about 20-30 psia; selectivity to PA only about 78 % at virtually complete conversion, about 3.5 % maleic anhydride and 18.5 % CO2 and water; PA 0.6-2.0 vol% in the effluent; switch condensers as much as 20-30 % of the capital; recovery 95 % plus | read (Google Patents); patent, facts only | D-004, D-005, D-007 |
| SRC-5 | US 5 730 844 A, Exxon Chemical Patents, published 1998-03-24: Liquid phthalic anhydride recovery process using a rectification tower with benzoic acid control, https://patents.google.com/patent/US5730844A/en | background and description: reactor gas cooled near PA's solidification point (131 C), condensed liquid separated, switch condensers cycling on cold and hot (steam-heated) oil, cycles about 3-6 h; impurities leave mostly with the gas to the waste-gas incinerators; acid from absorbed water reconverted by heating the crude at 250-280 C under slight vacuum; light ends and a second column to about 99.7 wt% product | read (Google Patents, first 100 000 characters); patent, facts only | D-007, D-009 |
| SRC-6 | Jara, J. A.; Garea, A.; Irabien, J. A. (2005) Simulation of o-xylene oxidation into phthalic anhydride: rigorous multitubular catalytic reactor modelling and exportation into the process flowsheet. ESCAPE-15 (Puigjaner, Espuña eds.), paper MS-087, https://skoge.folk.ntnu.no/prost/proceedings/escape15/papers/MS-087.pdf | sections 2-4: reaction network (o-tolualdehyde, o-toluic acid, phthalide, PA, maleic and methylmaleic anhydride, benzoic acid, CO, CO2); plant sections (molten-salt multitubular reactor, after-cooler, switch condensers with a buffer tank, stripping and rectification columns); graded catalyst giving 1.10 kg PA per kg o-xylene; 13 500 tubes of 3.5 m for 4950 kg/h | read (proceedings paper openly posted; © Elsevier, facts only) | D-001, D-002, D-005, D-009 |
| SRC-7 | US 4 036 783 A, BASF, published 1977-07-19: Supported catalyst containing vanadium and titanium, https://patents.google.com/patent/US4036783A/en | Examples 1, 3, 4: o-xylene over V2O5/TiO2 in a 25 mm, 3 m tube at 370-380 C, 113.5-115 wt% PA on o-xylene (Example 4: 272 g/h o-xylene in 4000 l/h air at 375 C) | read (Google Patents); patent, facts only | D-005 |
| SRC-8 | chemicals 1.5.2 and thermo 0.6.1 (the versions core pins; open-source, MIT), through `cheme chemistry thermo` and the packages directly: gas formation enthalpies from chemicals' packaged CRC and ATcT tables (`Hfg`: CRC for o-xylene, PA, MA, benzoic acid; ATCT_G for the gases); entropies from the packaged CRC, WebBook and Yaws tables (`S0g`); critical constants (HEOS, Yaws, PSRK); ideal-gas cp fitted to thermo's TRCIG and HEOS_FIT correlations; for PA and MA, which have no ideal-gas heat capacity in thermo, the Joback group contribution (Joback and Reid 1987, not read here) evaluated by `thermo.group_contribution.Joback.Cpig_coeffs` with the groups assigned by hand; PA's vapour pressure and heat of vaporization from thermo's DIPPR_PERRY_8E coefficients (Perry's Handbook, 8th ed., from DIPPR 801; a licensed book, not read here), o-xylene's from HEOS_FIT; sublimation enthalpies (PA 88.7, MA 70.0, benzoic acid 90.0 kJ/mol) from thermo's WEBBOOK_HSUB (NIST Chemistry WebBook); PA's liquid heat capacity by the Rowlinson-Bondi corresponding-states method of chemicals on the Joback cp (Tc 791 K, omega 0.708, Yaws) | printed per component in process/materials.yaml and in the hand calculations below | single values with their source, facts only, not open data (library ADR 0037); the handbooks behind them were not read | ideal-gas data, heats of reaction, vapour pressures, latent heats |
| SRC-9 | processes/btx-1 (this library) | process.yaml chemistry: mixed xylenes (with ethylbenzene) as a co-product; no o-xylene | library | D-003, D-012 |
| SRC-10 | processes/phthalimide-1 (this library) | process.yaml chemistry and lca/mappings.yaml: molten phthalic anhydride bought in, a gap "no library process makes it" | library | D-001 (consumer link) |
| SRC-11 | US 3 965 126 A (1976): Recovering maleic anhydride from the effluent from the production of phthalic anhydride | as summarised by a web search only: the water wash of PA off-gas holds maleic acid with benzoic, citraconic and toluic acids | not read in full; lead only | D-001 (rejected MA recovery), D-005 (benzoic acid present) |

No open source with a plant's utility consumption per tonne of PA was read in this work (the
EU LVOC BREF was not searched for one; Ullmann's is licensed and not read).

## D-001 Route and boundary (2026-11-19)
Decision: Phthalic anhydride (PA) by gas-phase oxidation of o-xylene with air over a V2O5/TiO2
catalyst in a multitubular fixed-bed reactor cooled by circulating molten salt that raises HP
steam (SRC-1, SRC-2, SRC-3), the gas cooled in a steam-raising gas cooler and the crude PA
desublimed in switch condensers (SRC-1, SRC-5, SRC-6), thermal pre-treatment of the crude melt
and two vacuum columns (light ends, pure PA) (SRC-1, SRC-5, SRC-6); the off-gas burnt in a
regenerative thermal oxidiser (SRC-1, 6.5.2). Continuous, one reactor line. Boundary feeds:
o-xylene, air, electricity, HP steam from the plant's own header; outputs: PA melt to the
tanks, light ends and residue to incineration, flue gas, HP and LP steam exported, heat to
cooling water.
Reason: the issue's scope; every source read names this as the industrial route, and AP-42
states that new capacity uses o-xylene (SRC-1, 6.5.1).
Rejected:
- Naphthalene in a fluidised bed (SRC-1: the same chemistry, a lower feed utilisation, catalyst
  handling and recovery; a fluid bed's cooling tubes instead of salt) and mixed
  naphthalene/o-xylene feeds (SRC-2's examples): o-xylene is the cheaper, cleaner feed.
- Liquid-phase oxidation and the elevated-pressure process of SRC-4 (a continuous condenser
  instead of switch condensers, pressure above 200 psia): not industrial practice in any source
  read.
- Liquid-phase PA recovery with a rectification tower (SRC-5's invention) in place of switch
  condensers: kept as a basic-engineering option.
- Maleic anhydride recovery from a water scrubber on the off-gas (SRC-1: the only by-product
  recovered; SRC-11): a second product and a separate train; here the off-gas goes straight to
  the oxidiser.
Links to other library processes: phthalimide-1 consumes molten PA and records it as a gap
(SRC-10); this entry is a producer for it (its own mappings are not changed here). No library
process makes o-xylene (D-003).

## D-002 Capacity and operating hours (2026-11-19)
Decision: one reactor of 15 000 tubes (ASSUMED), each at 4 Nm3/h of air (SRC-2) and 80 g/Nm3 of
o-xylene (D-004): 4800 kg/h o-xylene, 5055 kg/h PA (S13), about 40.4 kt/a at 8000 h/a
(ASSUMED). The product is the PA melt at 433 K to tanks kept near 150 C under dry nitrogen
(SRC-1); flaking and bagging are outside the boundary.
Reason: a reactor size of the order SRC-6 models (13 500 tubes for 4950 kg/h); no client or
published plant basis is used. Per-kg normalisation makes the LCI independent of scale.

## D-003 Feed (2026-11-19)
Decision: o-xylene taken as pure at 303 K, 400 kPa(a) (ASSUMED); its commercial specification
(m- and p-xylene, ethylbenzene, sulfur) is an open input. Air dry, N2/O2/Ar 78.12/20.95/0.93
mol% (CO2 lumped into N2), humidity not counted (ASSUMED).
Link: processes/btx-1 exports mixed xylenes with ethylbenzene, not o-xylene (SRC-9), so the feed
stays a gap in the LCI with the proxy of D-012.

## D-004 Air and o-xylene loading (2026-11-19)
Decision: 60 000 Nm3/h of air (15 000 x 4 Nm3/h, SRC-2) at 80 g/Nm3 o-xylene (ASSUMED): inside
SRC-2's "up to 100 g/Nm3", SRC-3's 30-150 g/Nm3 and SRC-4's conventional 40-130 g/Nm3. Air
2676.90 kmol/h (22.414 Nm3/kmol), 77 520.5 kg/h (28.959 kg/kmol).
Hazard: this loading is above the lower flammable limit of o-xylene in air; plants of this kind
run inside the flammable range at the reactor inlet, so the evaporator M-101, the inlet hood
and the ducts are designed for a deflagration (pressure resistance or bursting discs) and the
loading is interlocked with the air flow (D-011).

## D-005 Reactor model (2026-11-19)
Decision: R101 is a conversion reactor (core): of the o-xylene fed, 79.0 % to PA, 3.5 % to
maleic anhydride, 0.5 % to benzoic acid, 9.4 % burnt to CO2 and 7.5 % to CO; 99.9 % converted
(all ASSUMED within the sources). Inlet 433.15 K, 145 kPa(a); outlet 643.15 K, 125 kPa(a), 10 K
above a salt bath of about 633 K (SRC-1: 340-385 C; SRC-3: preferably 340-400 C, 0.3-1.5 bar
gauge).
Reason: the PA share gives 1.102 kg PA per kg o-xylene in the reactor gas, at SRC-6's 1.10 kg/kg
for a graded bed and near SRC-4's 78 % selectivity (1.088 kg/kg); SRC-7's laboratory tubes give
113.5-115 wt% and SRC-2's promoted catalysts with naphthalene co-feed about 110-111 wt%, so the
design is at the conservative end. The maleic anhydride share is SRC-4's 3.5 % read as mol% of
the feed (ASSUMED reading). The benzoic acid share is ASSUMED (named as a by-product by SRC-1 and
SRC-6, no share found). The CO share is set so that the switch-condenser off-gas carries
150.3 kg CO per t of product, AP-42's uncontrolled 151 kg/Mg (SRC-1, Table 6.5-1); CO2 takes
the rest. Intermediates (o-tolualdehyde, phthalide, o-toluic acid) are left out: SRC-2's
products hold at most 0.11 wt% phthalide.
No SO2 is dosed: SRC-1 reports it for the catalysts of its time; SRC-2's and SRC-3's examples run
without it (emission exclusion in lca.yaml).
Heat: core's conversion-step model gives -14 294.6 kW of enthalpy change with heats of reaction
from the formation enthalpies at 298.15 K (PA -1116.0, MA -2958.6, benzoic acid -1190.2, CO2
route -4376.0, CO route -2112.4 kJ/mol); with the salt pump's 150 kW the salt passes
14 444.6 kW to the steam generator (Q3, calculated). Hand check: the same 14 294.6 kW
(scratch calculation, ideal gas of materials.yaml).
Not modelled: the hot spot (SRC-2 keeps it below 450 C), the catalyst layers, tube pressure
drop, catalyst ageing (SRC-1: CO and by-products rise with catalyst age).

## D-006 Feed preparation and what core can and cannot calculate (2026-11-19)
Decision: the blower K101 compresses the air to 155 kPa(a) (346.28 K, D-010), E101 heats it on HP
steam to 469.57 K so that the liquid o-xylene (303 K) sprayed into it evaporates and the mixture
reaches 433.15 K: E101 2695.1 kW (Q2), ideal-gas cp of materials.yaml, o-xylene liquid at its
heat of vaporization at 298 K (43.42 kJ/mol, HEOS_FIT) and liquid cp 188.95 J/(mol K)
(thermo).
Core calculates: the mixer M101's flow and composition, R101 and X301 (conversion models, R101's
duty, X301 adiabatic), the component separators SC101, C201, C202 (`recovery:`), and every
element balance. Core does not calculate: the duties of the pass-through exchangers E101, E102
and T201, the switch condensers and the columns (no property package covers PA or MA, `cheme
process props --coverage`; L-2): these are the hand calculations of D-006 to D-009, given as
ASSUMED with their arithmetic in the flowsheet's sources.

## D-007 Gas cooler and switch condensers (2026-11-19)
Decision: E102 cools the product gas from 643.15 to 443.15 K raising LP steam (5037.4 kW, Q5),
above the PA dew point (419.6 K at its 1.56 kPa partial pressure, DIPPR); SRC-5 cools nearer
the solidification point and separates a liquid first, which is not modelled. The switch
condensers SC101 recover 97 % of the PA, 10 % of the maleic anhydride and 50 % of the benzoic
acid as crude (ASSUMED), the gas leaving at 333 K.
Reason: 97 % is inside SRC-4's "95 % plus" and makes the off-gas carry 61.8 kg of PA, maleic
anhydride and benzoic acid per t of product, against AP-42's uncontrolled 69 kg/Mg (SRC-1). The
equilibrium limit at 333 K, with PA's DIPPR vapour pressure extrapolated below its melting point
(15 Pa), would be about 1.1 % of the PA (55 kg/h); the solid's lower sublimation pressure would
allow less: modern condensers recover more than this design takes (a sensitivity, not a claim).
Duties: cooling phase 4047.6 kW (Q6) = gas 443.15 to 333.15 K and the crude desublimed at its
sublimation enthalpy (SRC-8) 3507.6 kW, plus 540 kW for the condensers' metal and oil cooled back
after each melt-out (ASSUMED, as the melt-out's swing); melt-out 1080 kW of HP steam through the
hot oil (Q7) = 2 x (34.65 kmol/h crude PA x (27.7 kJ/mol fusion, from 88.7 - 61.0 kJ/mol
sublimation less vaporization at 405 K) plus its warming 333 to 433 K) = 2 x 540 kW, the factor
2 for the metal and oil (ASSUMED). The cyclic operation (several units, 3-6 h cycles, SRC-5) is
represented by its time average (L-1).

## D-008 Steam (2026-11-19)
Decision: the salt bath raises saturated HP steam at 6000 kPa(a) (548.7 K) (ASSUMED level) from
Q3, about 22 t/h from boiler feed water at 378 K; the gas cooler E102 and the PA column's
condenser raise LP steam at 400 kPa(a) (Q5 5037.4 kW, Q11 1220.3 kW). The plant takes HP steam
back for E101, the melt-out, the pre-treatment and the PA column's reboiler (Q2, Q7, Q8, Q10:
5148.4 kW). Per kg of PA: 2.857 kWh HP and 1.238 kWh LP exported gross, 1.018 kWh HP taken back,
a net export of 3.08 kWh.
Reason: SRC-1 and SRC-3 state that the salt's heat raises steam; the level is set so that HP
steam can heat the pre-treatment at 523 K and the PA reboiler near 470 K. Steam raising from the
oxidiser's flue gas (494 K) is an open option.

## D-009 Purification and off-gas treatment (2026-11-19)
Decision:
- T201 holds the crude at 523.15 K (SRC-5: 250-280 C) to dehydrate phthalic acid: 254.0 kW of HP
  steam (Q8), the crude PA warmed 433.15 to 523.15 K at 26.39 kJ/mol (liquid cp, SRC-8); phthalic
  acid and the water the crude takes up are not modelled (L-1), the pre-treatment vapours are an
  emission exclusion.
- C201 (light-ends column, about 20 kPa(a)): 99.9 % of the maleic anhydride, 97 % of the benzoic
  acid and 0.5 % of the PA overhead (ASSUMED); reflux ratio 5, condenser 43.3 kW to tempered
  water (Q9); the boil-up from the pre-treated feed's heat, no reboiler.
- C202 (pure-PA column, 10 kPa(a) top, PA boiling at 470.2 K): 99 % of the PA overhead, 1 % with
  the residue (standing for the tars, not modelled; ASSUMED); reflux ratio 1 (ASSUMED); reboiler
  1119.3 kW = 2 x 34.13 kmol/h x 59.0 kJ/mol (Q10); condenser 1220.3 kW raising LP steam, with
  the product subcooled to 433.15 K (Q11). Product 99.99 wt% PA (SRC-1: 99.8 wt%; SRC-5:
  about 99.7 wt%).
- Light ends and residue (105.6 kg/h, 0.021 kg/kg) go molten to an outside hazardous-waste
  incinerator.
- X301, a regenerative thermal oxidiser, destroys 95 % of the CO, PA, maleic anhydride, benzoic
  acid and o-xylene (SRC-1: a thermal incinerator alone about 95 % on o-xylene plants; Table
  6.5-1: CO 151 to 8 kg/Mg); adiabatic, the outlet at 494.10 K (the off-gas's own combustibles
  raise it 161 K; core: duty -0.06 kW, `cheme process reactors`). Its ceramic beds recover the
  heat that lets it run without support fuel (ASSUMED); start-up fuel and NOx are excluded.
Emissions per kg of PA (stream S16): CO2 0.705 kg (fossil), CO 7.5 g, PA 1.6 g, maleic anhydride
1.4 g, benzoic acid 0.14 g, o-xylene 0.05 g. Against SRC-1's controlled factors (CO 8,
particulate 4 kg/Mg): CO 7.5 and PA + MA + benzoic acid 3.1 kg/t.
Rejected: a water scrubber ahead of the oxidiser (SRC-1: 96 % together) with maleic acid
recovery (D-001); a catalytic oxidiser (needs preheat to its light-off temperature).

## D-010 Pressure profile and power (2026-11-19)
Decision: blower 101.3 to 155 kPa(a) (isentropic 0.80, motor 0.95: 77 520.5 kg/h x 1.0052
kJ/(kg K) x 48.13 K / 3600 = 1041.7 kW shaft, 1096.6 kW electric, Q1); preheater 152, reactor
inlet 145 and outlet 125 (SRC-3's examples at about 1450 mbar), gas cooler 120, switch
condensers 110, oxidiser to the stack at atmospheric pressure: no off-gas fan. Salt pump 150 kW
(Q4) and the vacuum systems with the melt pumps 60 kW (Q12): ASSUMED allowances. Electricity
0.258 kWh per kg of PA.

## D-011 Hazards (noted, not designed) (2026-11-19)
- Flammable reactor feed: 80 g/Nm3 is inside the flammable range of o-xylene in air (D-004).
  Evaporator, inlet hood and ducts with bursting discs or pressure resistance, the loading
  interlocked with the air flow and the salt temperature, the o-xylene cut off on a low air flow.
- Reactor runaway: the reaction is strongly exothermic (14.3 MW on 4.8 t/h of feed) and the hot
  spot is sensitive to the salt temperature and the loading (SRC-2 keeps it below 450 C; above
  465 C its comparison catalyst became unstable). Salt temperature control, hot-spot
  thermocouples in selected tubes, o-xylene trip on high hot-spot temperature.
- Molten salt (nitrite/nitrate, SRC-3) with organics: a tube leak can react violently; salt
  inventory and leak detection belong to basic engineering.
- PA dust and melt: combustible dust in flaking and bagging (outside), burns from the 433-523 K
  melt; the product tanks are blanketed with dry nitrogen against fire and hydrolysis (SRC-1).
- The flowsheet is continuous with no dosed batch step, so `cheme process reactor-hazards`
  (semi-batch accumulation screening) does not apply.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
Decision: lca/lca.yaml, functional unit 1 kg of PA melt at the gate (S13); every foreground
exchange from the balanced flowsheet; the backgrounds unmapped (`missing:` with the activity each
should connect to) except the HP steam taken back, linked as heat from steam (lca/mappings.yaml).
The plant's emissions are elementary flows to air (non-urban high stack, ASSUMED). The exported
HP and LP steam are co-products with shares 0 (all burdens to PA, conservative), as in
sulfuric-acid-1 and nitric-acid-1; a substitution study would credit the net 3.08 kWh/kg.
Inventory per kg of PA (`cheme assess lca --write`): o-xylene 0.9495 kg, air 15.33 kg (free),
electricity 0.258 kWh, HP steam 1.018 kWh; outputs: HP steam 2.857 kWh, LP steam 1.238 kWh,
heat to cooling water 0.809 kWh, waste to incineration 0.0209 kg, flue gas 15.26 kg (CO2 0.705
kg). `cheme assess lca --balance` closes mass and every element (largest residual 0.00 %).
Proxy recorded, not linked: o-xylene from the xylene splitter of an aromatics complex, whose
burdens are those of btx-1's mixed xylenes plus the splitter's reboiler heat (no estimate proxy
is added to the shared lci/mappings.yaml in this change, since that file is shared vocabulary
with its own PR, CONTRIBUTING "Shared vocabulary").
Excluded and listed: SO2 dosing, oxidiser NOx and start-up fuel, the purification and tank
vents (AP-42's uncontrolled 6.4 and 45 kg/Mg would add about 2.6 kg/Mg after 95 %), catalyst
replacement; construction, transport, end of life; nitrogen blanketing.
Climate change in the screening (DESNZ/IPCC factors of core): 0.705 kg CO2-eq per kg, the
plant's own CO2 only; every purchased input is a gap, so this is no footprint of PA.

## Method and dependency table
| what | how | where |
|---|---|---|
| mixer, separators | `cheme process propagate --fill` (mixing, `recovery:`) | S5, S8 to S15 |
| reactor R101 | conversion model; duty from core's conversion-step model (Q3) | reactions.yaml, D-005 |
| oxidiser X301 | conversion model, adiabatic (simulation.yaml), duty checked by `cheme process reactors` | D-009 |
| exchangers, condensers, columns | hand calculation, ideal gas of materials.yaml, SRC-8 latent heats, ASSUMED | D-006 to D-009 |
| LCI | `cheme assess lca --write` | lca/, D-012 |

## Core features used (core 1.12.0)
- `reactor: conversion` with five parallel reactions on one key (R101) and five on different keys
  (X301); the conversion-step duty on R101's energy stream at its `energy_port` with another
  energy stream in (the salt pump), ADR 0059.
- `recovery:` on component separators (SC101, C201, C202), so that propagate carries every flow.
- `process/simulation.yaml` `mode: adiabatic` for X301, checked by `cheme process reactors`.
- `cheme chemistry thermo` for the ideal-gas data; `cheme assess lca` with `allocation: shares`,
  `substitution`, `emission_exclusions`.

## Core limits hit (each a candidate core issue)
- L-1: no desublimation or cyclic (switch) condenser: SC101 is a component separator with an
  ASSUMED recovery and its duties are by hand; a gas-solid equilibrium with a sublimation
  pressure and a time-averaged cycle would let core predict the off-gas loss. Phthalic acid
  formation with water and its dehydration in the pre-treatment are not representable either
  without a solid/melt reaction model.
- L-2: no property package covers PA or MA (`cheme process props --coverage`): thermo has no
  ideal-gas cp for either, and its Joback SMARTS counts the anhydride ring as two esters (wrong
  groups); materials.yaml carries the Joback cp with the groups assigned by hand. So core cannot
  calculate the duties of E101, E102, T201 or the columns.
- L-3: a component separator has no energy model: the columns' reboilers and condensers are
  hand calculations (reflux ratio x distillate x latent heat); a shortcut column (Fenske,
  Underwood, Gilliland) on a component separator would give them.
- L-4: a mixer's outlet with rounding in propagate's written fractions can sum to 1.000001 and
  trip pyDEXPI's fraction check on the built sheets (seen on S15 with an earlier recovery; the
  benzoic acid split was moved from 0.98 to 0.97, which does not change any reported number
  beyond 0.1 kg/h).

## Calculation maturity (2026-11-19)
Not evaluated to a level: the feeds and conversions are assumed (no owner-given or sourced feed),
and the energy balance of the exchangers and columns is not evaluable in core (L-2, L-3). The
process.yaml claim stays `concept`.

## Open inputs
o-Xylene specification; a sourced selectivity set for a named catalyst (by-products, CO/CO2
split, ageing); the switch condensers' recovery and cycle; the columns' stages, reflux and
residue; the steam level; the oxidiser's destruction efficiency and fuel (BAT-AEL from an open
source); catalyst mass and life; the flammability and hot-spot protection (HAZOP); prices for a
TEA; benchmark ranges for utilities.
