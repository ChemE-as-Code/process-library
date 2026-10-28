# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes. The
numbers live in the YAML (`process/*.yaml`, `lca/lca.yaml`); `cheme process streams --md`
prints the stream table. Issue: ChemE-as-Code/process-library#169. Library and core at the start
of this run: library `11d50ef`, `cheme` as installed in this environment (cheme-as-code >= 0.8).

## Source register

All sources were read for this run in the parts cited; facts are restated in our own words, no
table, figure or text is reproduced.

| id | source | locator | access, terms | used for |
|---|---|---|---|---|
| BREF | European Commission JRC (2017), *Best Available Techniques (BAT) Reference Document for the Production of Large Volume Organic Chemicals*, EUR 28882 EN, https://eippcb.jrc.ec.europa.eu/sites/default/files/inline-files/JRC109279LvocBref.pdf | ch. 6: s. 6.2.3 pp. 338-339 (metal oxide process); s. 6.3.1.2 Tables 6.6 and 6.7 p. 344; s. 6.3.1.4 Table 6.9 p. 346; s. 6.3.2 p. 346; s. 6.3.3-6.3.4 Table 6.10 p. 347; s. 6.3.5 Table 6.11 p. 348; BAT 45 Table 13.2 p. 607 | open; EU reuse policy (Commission Decision 2011/833/EU), facts cited | route, yield, conversion, off-gas composition, emissions, steam and power ranges, wastes |
| EPA91 | US EPA (1991), *Locating and Estimating Air Emissions from Sources of Formaldehyde (Revised)*, EPA-450/4-91-012, https://www.epa.gov/sites/default/files/2020-11/documents/formaldehyde.pdf | pp. 10 and 17 of the report (PDF pp. 17 and 24): metal oxide process description | US government work, public domain | reactor feed 5-10 vol% methanol, O2 below 10.9 % in the feed, converter about 345 C, yield 91-93 %, product methanol about 0.8 % |
| ULL | Reuss, G. et al., *Formaldehyde*, Ullmann's Encyclopedia of Industrial Chemistry, doi:10.1002/14356007.a11_619 | not read in this run (no access) | licensed | route reference lead only; no value taken |
| NIST | NIST Chemistry WebBook, SRD 69 | water and methanol enthalpy of vaporisation at 298 K; saturated steam at 1500 kPa(a) | US government, facts | liquid-side enthalpies of the balance script |
| chemicals | `cheme chemistry thermo` (Python `chemicals`: ATcT formation enthalpies, CRC entropies, Poling 5th ed. heat capacities) | `process/materials.yaml` source fields | MIT package, facts | ideal-gas enthalpies, reaction heats |

## D-001 Route and boundary: metal oxide (Formox type) process, methanol as boundary feed (2026-10-28)
Decision: Formaldehyde by partial oxidation of methanol with excess air over an iron
molybdate catalyst, with off-gas recycle, absorption in water to formalin and catalytic
oxidation of the vent (ECS), as the case notes of the run ask. Gate-to-gate boundary: methanol,
air and process water in; formalin, treated off-gas, exported steam and the heat to cooling water
out; electricity in. Methanol is a boundary feed; in this library it is made by
`processes/methanol-1` (Grade AA), which has no LCI dataset yet. Product storage, ion exchange
(formic acid removal), boiler feed water preparation, the cooling tower and the tank farm are
outside the boundary.
Reason: the metal oxide route reaches a higher yield than the silver route (BREF s. 6.3.3,
Table 6.10: 91-94 % against 87-90 %) and needs no methanol distillation, because conversion is
above 99 % (BREF s. 6.2.3; EPA91 p. 10). It runs lean, below the lower explosion limit, so no
start-up venting (BREF s. 6.2.4.1; EPA91 p. 17).
Rejected: the silver catalyst routes (high and partial conversion), which run rich above the
upper explosion limit with an H2-containing off-gas burned for energy (BREF s. 6.2.2); their
selectivity data are not mixed into this model (issue note).
Assumptions: one reactor line; the BREF also names a turbocharger on the air as an energy
option (s. 6.3.4), left out.

## D-002 Capacity and product (2026-10-28)
Decision: 20 t/h formalin at 50.0 wt% HCHO (10 t/h HCHO, 80 000 t/a at 8000 h/a), methanol in
the product as it follows from the conversion (0.28 wt%), delivered at 333 K to heated tanks.
Reason: the BREF gives 37-60 wt% as the product range of the oxide process and 0.2-0.3 wt%
methanol as attainable (s. 6.2.3); 50 wt% sits in the 37-55 wt% range of the case notes and is
a common resin-grade strength. Strong formalin is kept warm against paraformaldehyde
precipitation (EPA91 p. 18: heated storage, about 54 C bulk temperature in its example). The
capacity is ASSUMED, a large single line; at this size two reactors in parallel are likely
(open input).
Rejected: 37 wt% (more water to carry; can be made by dilution downstream).
Assumptions: formalin represented as HCHO + CH3OH + H2O on the monomer basis; methylene glycol
and oligomers and formic acid (EPA91: 0.005 % in the absorber product, removed by ion exchange)
are not modelled.

## D-003 Methanol feed (2026-10-28)
Decision: pure methanol at 298 K and 400 kPa(a) from the tank farm.
Reason: Grade AA (water at most 0.1 wt%) as methanol-1 makes it; the BREF reports operators
using 97-99.9 vol% methanol, above 99 % preferred (s. 6.3.3). The water is neglected (< 12 kg/h).

## D-004 Reaction set and reactor model: sourced selectivity model, not kinetics (2026-10-28)
Decision: three reactions on the Fe-Mo catalyst: FORMOX (methanol to formaldehyde), HCHO_OX
(over-oxidation of formaldehyde to CO) and DME_FORM (dimethyl ether). R101 is a conversion
reactor with a per-pass methanol conversion and molar selectivities to HCHO, CO and DME
(`process/flowsheet.yaml`), derived in `scripts/formox_balance.py` from three plant targets:
- yield to formaldehyde in the product 93.0 % of the methanol fed: the BREF gives 91-94 % with
  1135-1151 kg methanol per t HCHO (Table 6.10); 93 % means 1147 kg/t, inside that range.
  EPA91 gives 91-93 % (p. 17); the BREF text of s. 6.2.3 gives 88-91 % of theoretical: the
  newer industry-amended Table 6.10 is used and the lower figure kept as a sensitivity;
- plant methanol conversion 99.3 % (BREF s. 6.2.3: above 99 mol%);
- DME 1.0 kmol/h ASSUMED, which gives about 2000 mg/Nm3 in the absorber off-gas (BREF
  Table 6.6: 6-10 000 mg/Nm3, DME the largest share of the TVOC).
The rest of the converted methanol becomes CO (5.7 % of the converted methanol). CO2 from the
reactor and formic acid are neglected.
Reason: the BREF names DME, CO and formic acid as the by-products (s. 6.2.3) and over-oxidation
to CO and CO2 as the main yield loss (s. 6.3.4). No open kinetics were taken; the selectivity
model is a labelled plant-level model and reproduces the open ranges.
Rejected: an equilibrium model (all reactions are far from equilibrium, `cheme process
reactors` ln(Q/K) of -37 for FORMOX) and invented kinetics.
Assumptions: the heat of FORMOX from the components' formation data is -150.3 kJ/mol at 298 K
(-148.7 kJ/mol at the reactor, `cheme process reactors`); the BREF quotes -159 kJ/mol
(s. 6.2.3). The formation data are used; the difference (6 %) is within the concept accuracy.
Note: BREF Table 6.6 lists 4 % CO2 in the absorber off-gas of older plants; at 93 % yield the
carbon not in the product cannot make more than about 2 % in the vent after full oxidation, so
that row is not consistent with Table 6.10 and is not used.

## D-005 Gas loop: reactor feed, recycle, temperatures and pressures (2026-10-28)
Decision: reactor inlet 8.5 mol% methanol and absorber off-gas 6.0 mol% O2; these fix the fresh
air (1200.7 kmol/h dry) and the recycle (71.2 % of the off-gas). The reactor inlet then holds
9.7 mol% O2. Blower 100.5 -> 150 kPa(a); reactor inlet 145, outlet 128, absorber inlet 124, top
112 kPa(a). Reactor outlet 553.15 K; the methanol is vaporised and the feed heated to 399 K
against the reaction gas (E-101), which leaves for the absorber at 403.15 K. Humid air: 1.0 mol%
water; the 0.04 % CO2 of air is neglected (about 1.5 % of the stack CO2).
Reason: EPA91 gives 5-10 vol% methanol in the feed and O2 below 10.9 % in the feed so that the
methanol stays below the lower explosion limit (pp. 10, 17); the BREF gives 5-7 % O2 in the
absorber off-gas (Table 6.6), atmospheric pressure and 270-430 C on the catalyst (s. 6.2.3), and
names the reaction gas as the usual heat source of the vaporiser (s. 6.2.3). The result,
2414 Nm3 vent gas per t HCHO, matches the BREF's 2300-2400 Nm3/t (Table 6.6), an independent check.
Rejected: steam-heated vaporisation (would import LP steam).
Assumptions: the feed enters the tubes at 399 K, below the catalyst window (543-703 K): it is
heated to reaction temperature on the hot oil in the inert-ring section at the tube inlet
(BREF s. 6.2.3). `cheme validate` warns (`cheme.process-catalyst`) on S6; the warning is accepted
for this reason, not silenced. Pressures and temperatures are ASSUMED.

## D-006 Absorber and its balance (2026-10-28)
Decision: the absorber outlets are set by the balance script: off-gas at 303.15 K / 112 kPa(a),
saturated with water (Antoine, pure water: 3.8 mol%), with 300 mg/Nm3 formaldehyde and
1000 mg/Nm3 methanol (BREF Table 6.6: 150-700 and 500-2000 mg/Nm3); no N2, O2, Ar, CO or DME
dissolves; the formalin leaves at 333.15 K; the process water closes the water balance for
50 wt% (3.71 t/h). The cooling duty (13.1 MW) is the enthalpy balance with ideal-gas enthalpies
for the gas, the vaporisation enthalpies of water (44.0 kJ/mol) and methanol (37.4 kJ/mol) at
298 K (NIST), an ASSUMED heat of solution of gaseous formaldehyde in water of 62 kJ/mol and an
ASSUMED liquid heat capacity of 3.3 kJ/(kg K).
Reason: no property method of core covers formaldehyde in water (chemical solution as methylene
glycol and oligomers), so the absorber cannot be simulated (D-009). The heat of solution is the
largest single term (about 5.7 MW): it must be sourced before the cooling-water figure is
relied on.
Assumptions: rinse and ion-exchange regeneration waters (BREF s. 6.3.2: discontinuous) are not
in the design case.

## D-007 Utilities, machines and steam level (2026-10-28)
Decision: electric drives; blower isentropic efficiency 0.75 and motor 0.95 (1.61 MW electric);
pumps 80 kW ASSUMED lump. Reactor heat goes through a boiling hot-oil loop (natural
circulation, no pump counted) to a steam generator; steam is raised at 1500 kPa(a) (saturation
471.4 K) and exported, with the ECS steam. Cooling water 298/308 K.
Reason: electricity of the oxide process is 80-190 kWh/t HCHO (BREF Table 6.10); the design
gives 169 kWh/t, inside it. Net steam export of the oxide process is about 2.0 t/t HCHO
(Table 6.10); the design's 11.2 MW of steam duty is about 1.7 t/t at about 2350 kJ/kg
(BFW at 378 K to saturated steam at 1500 kPa(a)), plausible since the vaporiser uses process
heat and the ECS heat is small at 93 % yield.
Assumptions: steam level, efficiencies and the pump lump ASSUMED; hot-oil and steam-system
losses neglected.

## D-008 Emission control system (2026-10-28)
Decision: the vent (28.8 % of the off-gas) is oxidised over a noble-metal catalyst with steam
recovery. CO 99.8 %, HCHO and methanol 99.5 %, DME 99.0 % converted (ASSUMED); preheater,
oxidiser and steam generator lumped in R301, stack at 423.15 K.
Reason: BAT 45 (b) for the oxide process is a catalytic oxidiser with energy recovery (BREF
13.5.1). The result is HCHO 1.5 mg/Nm3 (BAT-AEL 2-5), TVOC about 13 mg C/Nm3 (BAT-AEL
< 5-30) and CO 48 mg/Nm3 (plants report 1-250 mg/Nm3, Table 6.7).
Assumptions: NOx formed in the oxidiser (Table 6.7: < 10 to 250 mg/Nm3 where reported) is not
in the flowsheet (no nitrogen chemistry); it is listed as an open emission in the LCI (D-010).

## D-009 Property methods and energy closure (2026-10-28)
Decision: no property package is set. `cheme process props --coverage` covers no stream (O2,
water, methanol and formaldehyde are outside both packaged property packages), and `cheme
process methods` lists no qualified activity-coefficient or chemical-solution model for
formaldehyde-water-methanol. The energy balances are therefore not evaluable in core (`cheme
process energy`); the reactor duties are (ideal gas, from the formation data) and match the
script.
Gated step: an energy-closed, simulated absorber and gas loop needs a qualified model for
aqueous formaldehyde (chemical theory of methylene glycol and poly(oxymethylene) glycols, or a
qualified NRTL/UNIFAC with formaldehyde) and an ideal-gas or EOS package for the
N2/O2/H2O/CH3OH/HCHO/CO/DME gas: core #315 (polar / activity-coefficient benchmark and
whole-flowsheet energy basis); core #364 (electrolytes/speciation) does not apply, formalin is
not an electrolyte.

## D-010 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg formalin 50 wt% at the gate (0.5 kg HCHO); every foreground
exchange from the balanced flowsheet; backgrounds unmapped (gaps), each with the activity it
should link to. The exported steam is a co-product, mapped as a gap with the avoided-steam
substitution not decided (the allocation is the LCA practitioner's decision). Details and the
results are in `lca/lca.yaml` and below (LCI section).

## D-011 Lists (2026-10-28)
Decision: equipment and line lists hold the items of the PFD; design pressure 3.5 barg for the
gas loop and 15 barg for the steam sides, design temperatures operating + 25 K; line sizes from
20 m/s gas and 1.5 m/s liquid velocity. All ASSUMED concept values.
