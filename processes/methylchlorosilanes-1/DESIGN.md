# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Methylchlorosilanes by the direct (Mueller-Rochow) process, issue
ChemE-as-Code/process-library#522, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD with the feeds solved for the rate, equipment list, hazard notes
and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` at c04ed69 with the core pin v1.13.0 (b97a833).
Core 1.13 solves conversion steps, component separators from a specified split, feeds for a
target by design specifications (core ADR 0070) and recycles at tear streams (ADR 0060): the
whole mass balance is core's. The heats are a script's, because the reactor has solid
reactants and dimethyldichlorosilane has no formation enthalpy in core's data (L-1, L-2).
Templates: `maleic-anhydride-1` (structure, a balance script beside core's models, the steam
export at share 0), `oxalyl-chloride-1` (the source register and the LCI conventions).
Requires cheme-as-code 1.13 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, Wikipedia and NIST WebBook pages, PubChem). Values
queried from the `chemicals` and `thermo` Python packages are not "read": SRC-7 names each
package method and the underlying work it comes from, which was not read here (library ADR
0037).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 500 724 A (General Electric), filed 1983-07-28, https://patents.google.com/patent/US4500724A/en | description, claims and Examples 1 to 4: fluid, stirred or fixed bed, 250 to 350 C (preferred 260 to 330 C, the examples about 300 C), 1 to 10 atm in a fluid bed; silicon of at least 98 % Si, below 700 um, mean 100 to 150 um preferred; copper 0.5 to 10 % of the silicon, zinc 0.01 to 0.5 part per part of copper, tin 200 to 3000 ppm of the copper; a rate constant after Voorhoeve with adsorption constants 6.8e-3 atm-1 (methyl chloride) and 0.4 atm-1 (silanes); selectivity as the T/D ratio (MeSiCl3 to Me2SiCl2) and the residue (boiling above 70 C); Example 3, a continuous fluid bed for 96 h at about 300 C: T/D 0.07 to 0.10, residue 4 to 5 %, about 2 % copper kept in the bed, Zn/Cu 0.08, Sn/Cu 0.001, the fines (2 to 50 um) recycled; the tables at 300 C: T/D 0.04 to 0.14, residue 0.6 to 6.4 % | read (Google Patents, characters 0 to 100 000 of 128 924); patent, facts only | D-001, D-003, D-004, D-006 |
| SRC-2 | US 2 563 557, rectification of methylchlorosilanes, https://patents.google.com/patent/US2563557 | description and example: four columns; column 1 at about 90 psig so that methyl chloride condenses with ordinary cooling water and its bottoms are free of it; example crude about 4 % methyl chloride, 8 % boiling below 66 C, 12 % MeSiCl3, 67 % Me2SiCl2, 9 % boiling above 70 C; column 2 takes the heavies at the bottom with about 1.6 % Me2SiCl2; column 3 the lights overhead (about 7 % MeSiCl3 in them), its bottoms about 83/17 Me2SiCl2/MeSiCl3; column 4 gives about 90 % MeSiCl3 overhead and 99.5 % Me2SiCl2 at the bottom (at most about 0.5 % MeSiCl3); reflux and plates not stated | read (Google Patents); patent, facts only | D-001, D-007, D-008 |
| SRC-3 | EP 1 957 504 B1 (Dow Corning), https://patents.google.com/patent/EP1957504B1/en | definitions and Examples 1 to 4: MeSiCl3 boils at 66.1 C and Me2SiCl2 at 70.1 C; 200 or more stages are needed to separate them conventionally; relative volatility 1.20 for a 50/50 mixture without an aid (1.31 with benzonitrile, 1.47 with methyl cyanoacetate) and 1.17 for a 10/90 mixture (1.30 with 25 wt% benzonitrile); a simulation at constant reboiler duty gives about twice the distillate with 33 wt% benzonitrile | read (Google Patents); patent, facts only | D-001, D-008 |
| SRC-4 | Wikipedia, Direct process, https://en.wikipedia.org/wiki/Direct_process (2026-11-19) | about 300 C and 2 to 5 bar in a fluidised bed; 90 to 98 % silicon and 30 to 90 % chloromethane conversion; copper as catalyst (about Cu3Si), tin and zinc as promoters; typical products Me2SiCl2 70 to 90 %, MeSiCl3 5 to 15 %, Me3SiCl 2 to 4 %, MeHSiCl2 1 to 4 %, Me2HSiCl 0.1 to 0.5 %; boiling points; about 1.4 Mt/a of Me2SiCl2 | read; CC BY-SA, facts only | D-001, D-003, D-004 |
| SRC-5 | Wikipedia, Dimethyldichlorosilane, https://en.wikipedia.org/wiki/Dimethyldichlorosilane (2026-11-19) | a flammable liquid, density 1.07 g/cm3, flash point -9 C, GHS H225, H315, H319, H335; hydrolyses to silicones and HCl; direct-process products Me2SiCl2 80 to 90 %, MeSiCl3 5 to 15 %, MeHSiCl2 3 to 5 %, Me3SiCl 3 to 5 % | read; CC BY-SA, facts only | D-004, D-011 |
| SRC-6 | US 2017/0305939 A1, method for the direct synthesis of methylchlorosilanes in fluidized-bed reactors, https://patents.google.com/patent/US20170305939A1/en | two fluid-bed reactors, 200 to 450 C (the first 300 to 350 C, the second 250 to 300 C), 1 to 5 bar; copper 0.1 to 10, zinc 0.01 to 1, tin 0.001 to 0.2 parts per 100 parts silicon; silicon d50 180 to 350 um; local temperature rises of up to several 100 K from the exotherm; laboratory Me2SiCl2 selectivities 71 to 78 % | read (Google Patents); patent, facts only | D-001, D-004, D-005 |
| SRC-7 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment), queried directly | gas formation enthalpies: ATCT_G (methyl chloride -82.62, ethane -83.78, ethylene +52.56 kJ/mol), CRC (MeSiCl3 -528.9, Me3SiCl -352.8, Me4Si -239.1), YAWS (MeHSiCl2 -402.0); none for Me2SiCl2; normal boiling points CRC_ORG; ideal-gas heat capacities: HEOS_FIT (methyl chloride, ethane, ethylene), WEBBOOK_SHOMATE (MeSiCl3, Me4Si, silicon and copper solid), LASTOVKA_SHAW (a group estimate: MeHSiCl2 and the disilane); liquid heat capacities ZABRANSKY_SPLINE_C, DADGOSTAR_SHAW; heats of vaporisation MORGAN_KOBAYASHI (a correlation), DIPPR_PERRY_8E, HEOS_FIT; vapour pressures (methyl chloride 577 kPa at 298 K); methyl chloride's flammable limits 7.6 and 19 vol% (IEC 60079-20-1 (2010) table packaged in `chemicals`); flash points (Serat DIPPR 2017) | open-source packages queried 2026-11-19; single values, facts only, with the package and method; the underlying works (ATcT, the CRC Handbook, Yaws, the NIST WebBook's Shomate fits, CoolProp's sources, Zabransky et al., Perry's 8th ed. / DIPPR 801, IEC 60079-20-1) were not read here; not open data (library ADR 0037) | materials, D-005, D-007 to D-011 |
| SRC-8 | NIST Chemistry WebBook, SRD 69, dichlorodimethylsilane (C75785), condensed-phase and phase-change data | liquid S 270.4 J/(mol K) and Cp 171.5 J/(mol K) at 298.15 K (Samorukov and Kostryukov 1971); heat of vaporisation 31.5 kJ/mol at 316 K (Jenkins and Chambers 1954); boiling points 342.5 to 345 K; no formation enthalpy listed | read | D-005 (the missing value), cross-check of SRC-7 |
| SRC-9 | PubChem CIDs 5461123 (silicon), 6398 (Me2SiCl2), 6399 (MeSiCl3), 6397 (Me3SiCl), 6376 (MeHSiCl2), 78276 (the disilane), 6324, 6325 | identity (formula, InChIKey, CAS, ChEBI cross-references) | read (PUG REST) | materials, registry |
| SRC-10 | processes/chloromethane-1, maleic-anhydride-1, tert-butyldimethylsilyl-chloride-1 (this library) | the methyl chloride product; the balance-script pattern and the steam export at share 0; the consumer of Me2SiCl2 | library, internal | D-003, D-012 |

Searched and not found openly (2026-11-19): a formation enthalpy of Me2SiCl2 or a heat of
reaction of the direct process with its source; a plant's methyl chloride conversion per pass,
superficial velocity, bed inventory or silicon productivity per unit of contact mass; a plant's
energy use or emissions; the MDPI review of the direct synthesis (AppliedChem 2023,
https://www.mdpi.com/2673-9623/3/1/7) refused the download (HTTP 403) and was not read.

## D-001 Route and boundary (2026-11-19)
Decision: the direct process: ground metallurgical silicon with methyl chloride over a copper
catalyst promoted with zinc and tin, in one fluidised bed fluidised by the methyl chloride
(SRC-1, SRC-4); the methyl chloride recovered in a pressure column on cooling water and
recycled; the crude distilled in three columns into Me2SiCl2, a MeSiCl3 cut, a light silanes cut
and a residue (SRC-2).
Boundary: gate to gate, from liquid methyl chloride, ground silicon, the copper make-up and the
utilities to the three silane products at storage, the wastes to treatment and the exported MP
steam. Milling of lump silicon is counted as an electricity allowance only (D-009).
Reason: the direct process is the base route of the silicones (SRC-4, SRC-5), and its open
sources read here cover the reactor (SRC-1, SRC-6), the product distribution (SRC-4, SRC-5) and
the distillation (SRC-2, SRC-3). Core 1.13 models every step as a conversion step or a
component separator, so the mass balance is core's.
Rejected:
- a stirred or fixed bed (SRC-1 claims both): the fluid bed is SRC-1's preferred continuous mode
  and SRC-4's industrial one; the choice changes the heat removal and the equipment, not the
  balance's form.
- two fluid beds in series (SRC-6: a hotter, more active first reactor feeding its contact mass
  to a cooler, more selective one): SRC-6 gives laboratory selectivities only; recorded as an
  improvement.
- extractive distillation of MeSiCl3/Me2SiCl2 with benzonitrile (SRC-3): raises the relative
  volatility from 1.17 to about 1.30 and roughly doubles the distillate at the same reboiler
  duty, but adds an aid to recover, and core has no model of it (L-4); kept as the main open
  improvement of C-403's 3.1 MW reboilers.
- the hydrolysis of Me2SiCl2 to siloxanes with the HCl returned to methyl chloride (the issue's
  optional step): a separate product (silicones) and a separate entry; the HCl loop with
  chloromethane-1 and hydrogen-chloride-1 is a follow-up.
- synthesis of methylchlorosilanes from organometallic reagents: no open source read here.
Assumptions: silicon modelled as pure Si (SRC-1: at least 98 %); its Fe, Al and Ca and the
zinc and tin promoters are not in the balance.

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: 60 000 t/a of Me2SiCl2 (stream S18) in 8000 h, 7500 kg/h, ASSUMED: one fluid-bed
train, about 4 % of SRC-4's world production. Product at least 99.5 wt% Me2SiCl2 with at most
0.5 wt% MeSiCl3 (SRC-2); modelled 99.51 wt%. Liquid at 313 K to storage under dry nitrogen.

## D-003 Methyl chloride feed and conversion per pass (2026-11-19)
Decision: liquid methyl chloride from chloromethane-1's storage (800 kPa(a), 298 K; its vapour
pressure is 577 kPa at 298 K, SRC-7) mixed with the recovered methyl chloride (S2) in V-101,
vaporised at 450 kPa(a) and superheated to 453 K on MP steam (E-101, ASSUMED), the bed's
fluidising gas. Half of the methyl chloride entering the bed converts per pass, ASSUMED inside
SRC-4's 30 to 90 %: the reactions consume 1.92347 mol of methyl chloride per mol of silicon fed
(scripts/balance.py from reactions.yaml), so the bed takes 6.9152 kg of methyl chloride per kg
of silicon, the design specification `mecl`, which solves the fresh methyl chloride S1
(7222 kg/h, 0.963 kg/kg of product). The loop is torn at S2 and converges in 3 Broyden
iterations together with the specifications.

## D-004 Reactor R201: conversion model and crude distribution (2026-11-19)
Decision: a conversion step on the silicon (`reactor: conversion`): 95 % of the silicon fed
converts (ASSUMED inside SRC-4's 90 to 98 %). The crude distribution is ASSUMED, in wt% of the
silanes: Me2SiCl2 84.0, MeSiCl3 7.0, Me3SiCl 3.0, MeHSiCl2 1.5, residue 4.5. It lies inside
SRC-4's and SRC-5's ranges, its T/D (0.083) and residue (4.5 %) inside SRC-1's continuous
fluid-bed Example 3 (0.07 to 0.10, 4 to 5 %). Me2HSiCl (SRC-4: 0.1 to 0.5 %) and SiCl4 are not
modelled. scripts/balance.py turns the distribution into the shares of the reacted silicon
(0.83679, 0.02471, 0.07100, 0.01676, 0.05074), times 0.95 the conversions of reactions.yaml.
Lumped by-product chemistry, ASSUMED (L-3): the methyl groups a silane does not keep leave as
ethane (with MeSiCl3 and the residue) or ethylene (with MeHSiCl2); Me3SiCl forms with an equal
amount of MeSiCl3; the residue is lumped as the disilane Me2Si2Cl4. The real off-gas holds
methane, hydrogen and other hydrocarbons, and carbon deposits on the contact mass.
Catalyst: copper 0.5 wt% of the silicon fed (10.3 kg/h), the low end of SRC-1's 0.5 to 10 %,
ASSUMED: the copper leaves only with the purged contact mass (D-006), so the bed's copper
content is set by the purge (here about 9 wt% of the spent mass). Zinc and tin (SRC-1's
Example 3: Zn/Cu 0.08, Sn/Cu 0.001) are not modelled (0.08 % and 0.0001 % of the silicon).
Conditions: 573 K (SRC-1's examples and SRC-4) and 400 kPa(a) (SRC-4: 2 to 5 bar).
Rejected: SRC-1's rate expression (Voorhoeve, with its adsorption constants) as a kinetic
model: core has no fluid-bed model with a solids inventory (L-3), and SRC-1 gives no rate
constant in absolute units read here.

## D-005 Reactor heat: R-201's cooling coils and the formation enthalpy of Me2SiCl2 (2026-11-19)
Decision: scripts/balance.py closes R-201's energy balance: the feed gas at 453 K and the solids
at 298 K in, every outlet at 573 K, formation enthalpies of SRC-7 and the silicon and copper as
solids (WEBBOOK_SHOMATE heat capacities). Q2 = 4635.7 kW, 239 kJ per mol of silicon reacted, to
cooling coils in the bed raising MP steam at 1500 kPa(a) (471 K; ASSUMED, a 100 K approach to
the bed). Without the coils the outlet would reach about 1250 K (scripts/balance.py): the bed
must be cooled continuously (D-011; SRC-6 notes local rises of several 100 K).
Me2SiCl2's gas formation enthalpy is ASSUMED: -440.9 kJ/mol, the mean of Me3SiCl's (-352.8) and
MeSiCl3's (-528.9, SRC-7), because neither `chemicals` nor the NIST WebBook (SRC-8) lists one
(L-2). The main reaction's heat is then -275.6 kJ/mol. The residue's heat per mol of silicon is
ASSUMED equal to it. The gas heat capacities of Me2SiCl2 and Me3SiCl are interpolated between
MeSiCl3 and Me4Si by the number of methyl groups (ASSUMED, instead of thermo's group estimate).
A 10 % error in Me2SiCl2's formation enthalpy (44 kJ/mol) moves Q2 by about 0.76 MW (16 % of
it, with the residue's heat tied to it): the reactor duty is the least certain number of the
entry.

## D-006 Cyclones and the spent contact mass (2026-11-19)
Decision: cyclones return the fines to the bed (SRC-1 recycles fines of 2 to 50 um); at steady
state the 5 % of the silicon that does not convert and all the copper leave as spent contact
mass and filter dust (CY202, a component separator: every solid to SPENT, 114 kg/h, ASSUMED),
cooled under nitrogen to treatment (D-012). The crude gas carries no solids in the model; a hot
scrubber with condensed crude takes the last dust before E-301 (not modelled).

## D-007 Crude condensation and methyl chloride recovery (2026-11-19)
Decision: E-301 cools the crude gas from 573 to 313 K on cooling water at 380 kPa(a); the
silanes condense, the methyl chloride and the hydrocarbons stay in the gas (ASSUMED; part of
the methyl chloride dissolves in the crude). V-302 separates them: the liquid is pumped and the
gas compressed by K-303 to 760 kPa(a) into C-302, which runs at 722 kPa(a), the 90 psig at
which SRC-2's first column condenses methyl chloride with ordinary cooling water (306.1 K,
SRC-7's vapour pressure). Hence the cooling water's narrow range, 298 to 303 K (ASSUMED).
C302 (component separator): the methyl chloride distillate takes 99 % of it, the vent from the
reflux drum 95 % of the ethane, 97 % of the ethylene and 0.4 % of the methyl chloride, the
bottoms (S12) every silane and 0.6 % of the methyl chloride (to the lights cut). ASSUMED splits
for SRC-2's statement that the bottoms are free of methyl chloride. Reflux 1.0 (ASSUMED).
The vent, 150 kg/h with 19 wt% methyl chloride, goes to the site's thermal oxidiser with
acid-gas scrubbing (a waste treatment, D-012).

## D-008 Distillation train (2026-11-19)
Decision: three columns after SRC-2's columns 2 to 4, at 200 kPa(a) at their tops (ASSUMED, so
that the condensers run on cooling water), component separators with ASSUMED splits for SRC-2's
cuts:
- C401 (heavies): the residue (the disilane and 0.15 % of the Me2SiCl2, about 3 wt% of the
  residue) at the bottom (SRC-2's column 2 carries about 1.6 % Me2SiCl2 in its bottoms);
  reflux 0.5.
- C402 (lights): everything boiling below MeSiCl3 overhead with 2 % of the MeSiCl3 and 0.2 % of
  the Me2SiCl2 (SRC-2: about 7 % MeSiCl3 in its column 3 overhead), 2 % of the Me3SiCl to the
  bottoms; reflux 15. The lights cut (470 kg/h: 56 wt% Me3SiCl, 29 % MeHSiCl2, 9 % methyl
  chloride) is a co-product; its own separation (Me3SiCl forms an azeotrope with SiCl4, not
  modelled) is outside the boundary.
- C403 (MeSiCl3/Me2SiCl2): an overhead of 89 wt% MeSiCl3 (SRC-2: about 90 %) and a bottoms of
  99.51 wt% Me2SiCl2 (SRC-2: 99.5 %), by splits ASSUMED for these purities (MeSiCl3 94 % and
  Me2SiCl2 0.86 % overhead). Relative volatility 1.17, SRC-3's value for a 10/90 mixture (the
  feed is 6.6 mol% MeSiCl3). scripts/balance.py: Underwood's minimum reflux 78.0 (saturated
  liquid feed), reflux 93.6 at 1.2 times it, Fenske's minimum 47.8 stages and 93 theoretical
  stages (Gilliland after Eduljee), boil-up 419 kmol/h. SRC-3 states 200 or more stages for a
  commercial split: a tighter MeSiCl3 specification or real-tray efficiencies would explain the
  difference (open input). Two shells in series, ASSUMED.
Rejected: stage models of the columns (no property package of core covers the chlorosilanes,
L-4); a benzonitrile extractive column (D-001).

## D-009 Utilities and heat: every energy flow (2026-11-19)
Decision: scripts/balance.py gives each duty and power:
- E-101 (Q1): 2019.1 kW of MP steam, the liquid at 302.1 K vaporised and superheated to 453 K.
- R-201 (Q2): 4635.7 kW raised as MP steam (D-005).
- E-301 (Q3): 1819.6 kW to cooling water.
- C-302 (Q4, Q5): condenser 1437.0 kW at reflux 1.0; reboiler 1007.3 kW of MP steam at the
  421.7 K bottom (Me2SiCl2's saturation at 722 kPa(a)), Q4 less Q5 closing the column's heat
  balance from its feeds (the condensate at 313 K, K-303's gas at 374 K) to its outlets.
- C-401 (Q6, Q7): condenser and residue cooler 772.9 kW; reboiler 541.4 kW of MP steam (the
  residue boils at about 456 K at 200 kPa(a), too hot for LP steam).
- C-402 (Q8, Q9): 481.4 kW of LP steam, 493.8 kW to cooling water.
- C-403 (Q10, Q11): 3077.9 kW of LP steam, 3246.4 kW to cooling water.
- P1: silicon milling, conveying and lock hoppers at 50 kWh/t of silicon (an allowance,
  ASSUMED; no open figure read) and the feed pump, 106.2 kW; P2: K-303 (104.5 kW shaft at an
  isentropic efficiency of 0.75) and C-302's pumps, 113.2 kW; P3: the train's pumps, 6.8 kW;
  pumps at 400 kPa, 0.60, a liquid density of 1000 kg/m3 (ASSUMED).
- The temperatures S2, S3, S12, S14 and S16 (saturation and mixing, SRC-7).
Per kg of Me2SiCl2: electricity 0.030 kWh, MP steam raised 0.618 kWh and drawn 0.476 kWh, LP
steam 0.475 kWh, cooling water 1.036 kWh. C-403 takes 43 % of the steam drawn. The plant could
run E-101 and the MP reboilers on its own steam; the flowsheet keeps the export and the draw
apart so that each terminal has one level and direction, as maleic-anhydride-1 does.
Utilities: MP steam 1500 kPa(a), LP steam 450 kPa(a), cooling water 298/303 K, all ASSUMED.

## D-010 Equipment sizes (2026-11-19)
Decision: only what the balance gives (equipment/equipment-list.yaml): R-201's inlet gas, about
0.94 m3/s at 573 K and 400 kPa(a), gives about 2 m of diameter at an ASSUMED superficial velocity
of 0.3 m/s (no open source on it read); the bed inventory and height are not sized (no
productivity per unit of contact mass in absolute units read, L-3). C-403's stages from D-008.

## D-011 Hazards (2026-11-19)
Screening notes for a later HAZOP (no study yet):
- Reactor exotherm: about 239 kJ per mol of silicon; without the cooling coils the gas would
  reach about 1250 K (D-005), and SRC-6 reports local rises of several 100 K. Loss of coolant,
  loss of fluidisation (hot spots, sintering) and a methyl chloride feed failure set the trips:
  bed temperature, coolant flow and the fluidising gas flow.
- Methyl chloride: a flammable gas (7.6 to 19 vol% in air, SRC-7) handled liquefied above its
  577 kPa vapour pressure at 298 K and as a gas at up to 760 kPa(a); C-302's vent carries it to
  the thermal oxidiser.
- Chlorosilanes: flammable liquids (Me2SiCl2 flash point -9 C, H225, SRC-5; the others' flash
  points 241 to 262 K, SRC-7) that hydrolyse with water to HCl (SRC-5): the plant is kept dry,
  tanks and hoppers under dry nitrogen, vents through scrubbers; a leak releases HCl.
- Silicon dust: combustible dust in the milling, the hoppers and the spent contact mass (cooled
  and passivated under nitrogen, D-006); explosion protection to be set at basic engineering.
- No reactor hazard screening of core applies: `cheme process reactor-hazards` screens batch and
  semi-batch reactors (L-6).

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `lca/lca.yaml` with `boundary: cradle-to-gate` so that the purchased inputs stay open
gaps, as maleic-anhydride-1. Allocation: `shares` equal to the mass shares of the three silane
products (Me2SiCl2 0.870075, the MeSiCl3 cut 0.075412, the light silanes cut 0.054513), the
exported MP steam at share 0 (no burden, no credit). The shares are written out instead of
`method: mass` so that the steam can carry share 0 in the same allocation.
Linked in lca/mappings.yaml: the methyl chloride to chloromethane-1's product (kg for kg) and the
MP and LP steam drawn as heat delivered (steam-heat). Gaps in lca/lca.yaml, each naming the
activity it should connect to: silicon (no library producer; carbothermic reduction of quartz),
copper, electricity and cooling water (the Atlas build links these two through the shared
lci/mappings.yaml), and the three waste treatments: the residue (incineration of a chlorinated
organosilicon liquid), the spent contact mass (copper recovery or landfill) and the vent (the
site's thermal oxidiser). No direct emission in normal operation: the vent is a waste treatment,
and fugitives, tank breathing and dust are recorded exclusions.
The consumer tert-butyldimethylsilyl-chloride-1 (feed:SILF) names Me2SiCl2 from the direct
process as its open gap; linking it to this entry is that entry's own change (a follow-up).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component and element balances | done in cheme | cheme validate / process streams / propagate |
| reactor R201 (conversion on the silicon) | done in cheme, distribution ASSUMED | D-004, core ADR 0059 |
| cyclones and four columns (component separators) | done in cheme, splits ASSUMED for sourced cuts | D-006 to D-008, core ADR 0070 |
| silicon for 60 000 t/a, fresh methyl chloride for the bed's ratio | done in cheme (design specifications) | D-002, D-003, core ADR 0070 |
| methyl chloride loop | done in cheme (tear S2, Broyden) | D-003, core ADR 0060 |
| reaction shares from the crude distribution, methyl chloride per silicon | script | D-003, D-004 |
| reactor heat Q2 (solids, Me2SiCl2's formation enthalpy ASSUMED) | script | D-005 |
| Q1, Q3 to Q11, P1 to P3, saturation and mixing temperatures | script | D-007 to D-009 |
| C-403 minimum reflux and stages (Underwood, Fenske, Gilliland) | script | D-008 |
| R-201 diameter | by hand from the gas flow | D-010 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.13.0)

- `reactor: conversion` with five parallel reactions on one solid key (silicon), two of them
  with two silicon atoms; `phase: solid` components.
- `recovery:` on CY202, C302 (three outlets), C401, C402 and C403 (component separators).
- `specs:` `rate` (annual target on S18, the copper following the silicon `with:` its ratio) and
  `mecl` (a mass ratio of S4's methyl chloride to S5's silicon), solved with the tear S2.
- `tears:` with `convergence` (ADR 0060); `cheme assess lca` with `allocation: shares` and waste
  `treatment`s.
- Not used: `cheme process props` and `simulate` (no package covers the chlorosilanes),
  `reactor-hazards` (batch only), `cheme chemistry thermo` for ideal-gas data (the reactor has
  no energy port, L-1).

## Core limits hit (each a candidate core issue)

- L-1: a conversion step's duty counts every inlet and outlet as an ideal gas: a gas-solid
  reactor with solid reactants (silicon, copper) cannot get its duty from core, so R201 has no
  energy port and its heat is the script's (D-005).
- L-2: no formation enthalpy of Me2SiCl2 in core's data sources (`chemicals` 1.5.2) or in the
  NIST WebBook: the main reaction's heat rests on an ASSUMED interpolation (D-005).
- L-3: no fluid-bed reactor model: no solids inventory, residence time, elutriation or contact-
  mass purge, and no rate law with adsorption terms (SRC-1's Voorhoeve form); the conversion,
  the distribution and the lumped by-product chemistry are inputs (D-004, D-010).
- L-4: no property package or column model for chlorosilanes: the four columns are fixed splits,
  and their duties and C-403's stages are the script's shortcut methods; an extractive variant
  (SRC-3) cannot be modelled (D-001, D-008).
- L-5: a stream's `phase` takes vapor, liquid or two-phase only: the silicon, copper and spent
  contact mass streams (S5, S6, S8) carry no phase.
- L-6: no hazard screening for a continuous reactor (`reactor-hazards` screens batch and
  semi-batch steps); the runaway estimate is the script's adiabatic outlet (D-011).

## Stage gates

`cheme check --no-write --stage concept`: every concept gate passes except `layout-plot-plan`
(no plot plan; out of scope of this entry, as in maleic-anhydride-1). The concept stage is not
signed off.

## Open inputs
A formation enthalpy of Me2SiCl2 (or a measured heat of the direct reaction); a plant's methyl
chloride conversion per pass, superficial velocity, bed inventory and productivity; the real
by-product gas (methane, hydrogen, carbon); the copper, zinc and tin make-up and the contact-mass
purge rate; Me2HSiCl and SiCl4; the stage count and specification of C-403 against SRC-3's 200
stages, and the benzonitrile extractive alternative; heat integration (the reactor's steam for
E-101 and the reboilers, C-403's condenser); the treatment of the residue (cleavage to
monosilanes) and the spent contact mass (copper recovery); the hydrolysis and HCl loop to
chloromethane-1; the receiving site of the steam; a TEA.
