# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes. The
numbers live in `process/*.yaml` and `scripts/ngcc_balance.py`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#469 (coverage rank 58, `power-generation`).

Run record of this stage (2026-11-19): library branch `process/power-generation-1` from
`c241d8d7`; cheme-as-code 1.12.0 at core `0e85885` (pyDEXPI 2.1.0), Python 3.12; DWSIM not used.

## 1. Route and boundary memo

- **Product**: electricity, net of the plant's own use, at the high-voltage side of the
  generator step-up transformers (345 kV), registry grade `electricity/high-voltage`.
- **Route**: a natural-gas combined cycle (NGCC), 2x1: two gas turbine generators, two heat
  recovery steam generators (HRSGs), one steam turbine generator, a water-cooled condenser and a
  wet cooling tower (D-001). Rejected alternatives in D-001.
- **Boundary** (D-001): natural gas at the turbine fuel skids, ambient air, raw water and
  demineralised water in; net electricity, stack gas, deaerator vent, cooling tower evaporation
  and blowdown out. Inside: gas turbines, HRSGs with SCR, steam turbine, condenser, condensate
  and boiler feed pumps, circulating water system and cooling tower, transformers, all auxiliary
  loads. Outside: the gas pipeline and metering station, the raw water pretreatment and
  demineraliser, blowdown and wastewater treatment, the switchyard and the grid.
- **What crosses the boundary**: AIR, NG, DMW, RW (feeds); ELEC (product, energy); STACK,
  VENT, EVAP (emissions); BLOWDOWN (wastewater); AMBIENT (generator and transformer losses).
- **Normalisation**: per kWh of net electricity. 1 kWh takes 0.1285 kg of natural gas, 6,720 kJ
  on HHV.
- **Links to other library processes**: the SCR's ammonia from ammonia-1; the blowdown to the
  library's wastewater treatment (utility-wwtp) through the shared `wastewater` mapping. The
  electricity is not offered to other entries as their default supply (process.yaml header).

## 2. Source register

Read status: "read" = the cited locator was read in full text by this run. Facts are in our own
words and form; no table, figure or text is copied.

| id | source | locator | status | terms | used for |
|---|---|---|---|---|---|
| SRC-1 | Schmitt, T. et al. (2022) Cost and Performance Baseline for Fossil Energy Plants Volume 1: Bituminous Coal and Natural Gas to Electricity, Revision 4a, NETL, DOE/NETL-2023/4320, https://netl.doe.gov/projects/files/CostAndPerformanceBaselineForFossilEnergyPlantsVolume1BituminousCoalAndNaturalGasToElectricity_101422.pdf | Exhibit 2-2 (site, p. 34), Exhibit 2-6 (natural gas, p. 38), section 3.1.9.1 and Exhibit 3-7 (F-class, p. 79), section 5 intro and 5.1.1 to 5.1.4 (NGCC process areas, pp. 549-553), Exhibit 5-2 (F- vs H-class, pp. 551-552), Exhibits 5-5 and 5-6 (Case B31A assumptions, pp. 560-561), Exhibit 5-8 (stream table, p. 563), Exhibits 5-9 to 5-14 (performance, auxiliaries, emissions, carbon, sulfur and water balance, pp. 564-567), section 5.2.4.2 (generator efficiencies, p. 567), Exhibit 5-15 (heat and mass balance, p. 569), Exhibit 5-16 (energy balance, p. 571), section 5.2.5 (equipment list, pp. 571-574), Exhibit 5-19 (consumables, p. 579); section 4.2.4 and 4.3.4 (Cases B11A and B12A, PC), 5.3.4 (Case B32A, H-class) | read (PDF text extracted with pypdf 7.1.1; printed page numbers) | US government work; numbers used as facts with the citation | D-001 to D-012, the flowsheet, the equipment list, the LCI |
| SRC-2 | ATcT / CRC / Yaws / Poling 5th ed. via `cheme chemistry thermo` (the `chemicals` package 1.5.2) | printed records in process/materials.yaml | read (tool output) | single values with their source, not open data (ADR 0037) | the gas turbines' energy balance (D-005), heats of reaction |
| SRC-3 | U.S. EPA (2000) AP-42, Fifth Edition, Volume I, Section 3.1 Stationary Gas Turbines (April 2000), https://www.epa.gov/sites/default/files/2020-10/documents/c03s01.pdf | Table 3.1-2a, natural-gas-fired turbines, uncontrolled: methane 8.6E-03 lb/MMBtu (C), N2O 0.003 lb/MMBtu (E), HHV basis (footnote c) | read | US government work | D-011 CH4 and N2O |

## 3. Decisions

### D-001 Route: a 2x1 F-class natural-gas combined cycle (2026-11-19)
Decision: electricity from natural gas in a combined cycle of two F-class gas turbines, two
three-pressure reheat HRSGs and one reheat steam turbine, cooled by a wet cooling tower; the
configuration and operating point of SRC-1's Case B31A, without CO2 capture.
Reason: the coverage item asks for on-site and grid technologies; NGCC is the dominant
dispatchable fossil technology in new plants and the one with a complete, open, consistent design
point: SRC-1 gives the stream table, the auxiliary loads, the water balance, the stack emissions
and the consumables of one plant, which is what a Tier 2 entry needs to balance. The F-class
(SRC-1's reference frame for comparisons with its coal and capture cases, section 5.1.2.1) is
taken over the H-class because its steam conditions and HRSGs are the more widely built.
The 2017 F-class machine of Case B31A gives 59.4 % net (LHV), one point below the 60.4 % SRC-1
quotes for currently offered F-class 2x1 plants (Exhibit 5-2): the dataset sits that much above
the benchmark's specific gas use (benchmarks/power-generation.yaml), by this choice.
Rejected:
- H-class 2x1 (SRC-1 Case B32A: 992 MW net at 55.1 % HHV, section 5.3.4): a variant of the same
  route with larger, newer machines; a second case later.
- simple-cycle gas turbine (an F-class machine alone about 39.8 % LHV, SRC-1 Exhibit 5-2): a
  peaking plant, about two thirds of the combined cycle's efficiency.
- pulverised coal (SRC-1 Case B12A, supercritical: 650 MW at 40.2 % HHV, section 4.3.4) and other
  fuels: other feedstocks, other entries of the coverage item.
- CHP (combined heat and power): a second product needs an allocation decision and a heat
  customer; waste-incineration-1 and kraft-pulp-1 cover CHP cases.
- NGCC with CO2 capture (SRC-1 Cases B31B.90/.95): the capture plant is carbon-capture-1's scope;
  a later variant.
Assumptions: none beyond SRC-1's.

### D-002 Design point and capacity (2026-11-19)
Decision: one case, SRC-1's Case B31A at ISO ambient (15 degC, 101.3 kPa(a), 60 % RH, SRC-1
Exhibit 2-2) and base load: 477 MW from the gas turbines and 263 MW from the steam turbine
(Exhibit 5-9), 727 MW net. 7446 h a year at full load: SRC-1's 85 % capacity factor x 8760 h,
read as full-load hours (ASSUMED: SRC-1 does not split it into hours and part load).
Reason: a published, internally consistent design point; the operating hours matter only for
the per-year consumables (D-011).
Rejected: a size of our own (no open performance data for another size); part-load and ambient
cases (no open data at the same detail).

### D-003 Two trains as one step each (2026-11-19)
Decision: the two gas turbines are one step R101 and the two HRSGs one step H101, at the flows
of both trains, as SRC-1's stream table gives them (section 5.2.3).
Reason: the trains are identical (2 x 50 %); one step each keeps the PFD readable.
Rejected: two parallel trains with a splitter: twice the steps with no information gained.

### D-004 Fuel and combustion (2026-11-19)
Decision: the natural gas is SRC-1's (Exhibit 2-6): 93.1 % methane, 3.2 % ethane, 0.7 % propane,
0.4 % n-butane, 1.0 % CO2, 1.6 % N2 by volume, LHV 47,201 and HHV 52,295 kJ/kg, at the turbine
fuel skids at 2.96 MPa and 27 degC (no booster or let-down, section 5.1.1). The odorant
methanethiol (5.75e-6 mol%, 1.0 kg/h of sulfur, Exhibit 5-13) is left out of the balance; its SO2
is counted in the LCA (D-011). The hydrocarbons burn completely (`reactions.yaml`, conversion
1.0): SRC-1's exhaust (stream 3) carries none and about 1 ppmv CO (section 5.2.4.1).
Reason: the methanethiol is 0.003 % of the fuel's mass; CO, NOx, CH4 slip and N2O are ppm-level
and are counted by factors where they matter (the LCI), not in the mass balance.
Rejected: carrying CO and NO in the balance: the conversion step would need ASSUMED splits for
numbers that SRC-1 gives directly as stack rates.
Check: the calculated exhaust is 138,413 kmol/h and 3,927,398 kg/h (SRC-1: 138,406 and
3,927,398), within 0.0001 mole fraction of SRC-1's stream 3 for every component.

### D-005 Gas turbines as a conversion step: their power from core's energy balance (2026-11-19)
Decision: R101 lumps the compressors, dry low-NOx combustors, expanders and generators of both
machines into one conversion step from the ambient air S1 and the fuel S2 to the exhaust S3 at
625 degC (SRC-1 section 5.2.3, stream 3). Core's conversion-step model writes its duty from the
ideal-gas formation enthalpies and heat capacities of `materials.yaml` (core ADR 0059): what
leaves the machine as work and loss, 483.9 MW. `energy_port: power` makes Q1 that duty less the
generator loss Q2 = 477 MW x (1/0.985 - 1) = 7.26 MW (SRC-1 section 5.2.4.2: 98.5 % generator
efficiency), so Q1 = 476.6 MW.
Reason: this is the one place where core can calculate the gas turbine, and it does so from
first principles: the energy balance of a machine whose inlet and outlet states are known. SRC-1's
own figure is 477 / 0.985 = 484.3 MW of shaft work (0.08 % more); `scripts/ngcc_balance.py`
reproduces core's figure from the same data as a cross-check.
Rejected: giving the gas turbine power as NETL's 477 MW: it would hide the energy balance
behind a quoted number. A compressor/combustor/expander model with pressure ratio, isentropic
efficiencies and blade cooling: core has none (L-1), and SRC-1 does not state the 2017 F-class
machine's pressure ratio or efficiencies (its 18.5 is the 2008 machine's, Exhibit 3-7).
Assumptions: the machine's ambient heat loss is in Q1 (SRC-1 Exhibit 5-16 gives 33 GJ/h of
ambient losses for the whole plant, not by item); the exhaust temperature is SRC-1's.

### D-006 HRSG and the water/steam loop on SRC-1's stream table (2026-11-19)
Decision: the HRSGs H101 heat the condensate and the cold reheat into HP steam (16.5 MPa,
585 degC), hot reheat (3.51 MPa, 584 degC, with 75,339 kg/h of IP steam) and LP steam (0.51 MPa,
281 degC), at SRC-1's flows (Exhibit 5-8 streams 5 to 10). The SCR sits in H101 (between the HP
and IP sections, section 5.1.4); the boiler feed pumps, with their interstage bleed for the IP
and LP feedwater, are its energy stream Q7. The gas leaves at 83 degC (stream 4) unchanged in
composition (the SCR's ammonia and the NOx it removes are in the LCI, D-011). The loop is closed
on the turbine's exhaust: the condensate equals stream 10 (633,792 kg/h); SRC-1's stream 11
carries 790 kg/h more, the gland-seal and air-ejector flows its exhibits do not show.
Reason: no core model or property package covers water and steam (L-2), so the loop's states
are SRC-1's; only its flows enter the balance.
Check (scripts/ngcc_balance.py, ideal-gas data for the gas, SRC-1's enthalpies for the water):
the exhaust gives up 661.8 MW from 625 to 83 degC; the water and steam gain 656.7 MW plus the
feed pumps' 4.8 MW, 0.04 % less (the HRSGs' ambient loss and the rounding of the enthalpies).

### D-007 Steam turbine generator from SRC-1's stream enthalpies (2026-11-19)
Decision: the steam turbine X201's shaft work is the sum of its sections' enthalpy drops on
SRC-1's stream table (HP 56.1, IP 87.7, LP 122.4 MW: 266.2 MW), its power that times 0.987 (SRC-1
section 5.2.4.2): 262.7 MW (Q3; SRC-1: 263 MW), its generator loss 3.46 MW (Q4).
Reason: SRC-1's enthalpies are the vendor-backed result of a full steam cycle model; core cannot
calculate a steam expansion (L-2).
Rejected: isentropic efficiencies of our own on IAPWS: they would be ASSUMED and reproduce
SRC-1's numbers less well.

### D-008 Condenser and make-up (2026-11-19)
Decision: the surface condenser E201 at 50.8 mm Hg (6.77 kPa(a), SRC-1 Exhibit 5-5) condenses the
LP exhaust to 38 degC: 390.4 MW to the cooling water (Q5; SRC-1 Exhibit 5-9: 1,406 GJ/h =
390.6 MW). Its integrated deaerator (SRC-1 p. 573) takes the demineralised make-up S13 (2,804
lb/h = 1,271.9 kg/h, Exhibits 5-14 and 5-15) and vents the same mass S14 (Exhibit 5-14); the vent
is put at the condensate temperature (ASSUMED: SRC-1 Exhibit 5-16 gives it 0.2 GJ/h, which a
38 degC liquid-like enthalpy matches) and at atmospheric pressure. The demineraliser is outside
the boundary: the make-up is a feed (DMW).
Reason: the condenser duty is the steam loop's heat sink and follows from SRC-1's enthalpies.

### D-009 Cooling tower on SRC-1's water balance (2026-11-19)
Decision: the plant's own mechanical-draft wet cooling tower CT301 is inside the boundary, with
its circulating water pumps and fans (Q8 = 2,820 + 1,460 kW, Exhibit 5-10). Its water is SRC-1's
water balance (Exhibit 5-14): evaporation 2,245 gpm and blowdown 651 gpm, at 999.1 kg/m3
(ASSUMED, water at 15 degC), so 509.4 t/h to air and 147.7 t/h to treatment; the make-up S20 is
their sum (657.2 t/h; the exhibit's withdrawal 2,897 gpm is 0.23 t/h more, rounding). The
blowdown's dissolved solids and the tower's chemicals are not modelled. The condenser is its only
heat load in the flowsheet; SRC-1's tower also takes 26 GJ/h of other cooling loads (Exhibit
5-16, closed-cycle cooling of the generators and lube oil) that the flowsheet does not carry, but
its water balance is the tower's whole.
Reason: NETL's net output already pays for the tower's pumps and fans, so linking the library's
utility-cooling-tower to the condenser duty would count them twice.
Rejected: `cooling_water` as a utility linked to utility-cooling-tower (double counting, above).

### D-010 Auxiliary loads and the net export (2026-11-19)
Decision: the auxiliary loads are SRC-1's (Exhibit 5-10, 13,562 kW in all): condensate pumps
150 kW (Q6), boiler feed pumps 4,830 kW (Q7), circulating water pumps and cooling tower fans
4,280 kW (Q8), the rest of the balance of plant 2,052 kW (Q9: gas and steam turbine auxiliaries,
ground water pumps, SCR, controls, lighting and HVAC) and transformer losses 2,250 kW (Q10). The
bus T901 takes Q1 and Q3 and gives them out; the net export Q11 is its balance by hand:
476,622.0 + 262,744.3 - 13,562 = 725,804.3 kW (SRC-1: 727 MW). The test file checks it, so a
change of Q1 that `cheme process propagate --check` reports also fails the tests until Q11 is
updated.
Reason: core has no electrical model; the bus is an energy-only step whose balance core does not
evaluate (L-3), so the test keeps it closed.
Net efficiency: 725.8 / 1,354.9 = 53.57 % (HHV; SRC-1 53.6 %), 59.35 % (LHV; SRC-1 59.4 %).

### D-011 Preliminary LCI (2026-11-19)
Decision: a gate-to-gate inventory per kWh of net electricity (`lca/lca.yaml`):
- the balance's exchanges: natural gas, air (free), raw and demineralised water, the stack gas
  (fossil CO2 0.3425 kg/kWh; SRC-1 Exhibit 5-11: 342 kg/MWh net), the vent, the cooling tower's
  evaporation (water vapour, free; the water is counted where it is taken) and its blowdown to
  treatment; the generator and transformer losses are heat to the surroundings (free);
- emissions the balance does not carry, as a combustion estimate on the fuel's HHV input
  (4,877.66 GJ/h): NOx 1.542, CO 0.7985, SO2 0.4130 and particulates 0.7985 g/GJ from SRC-1's
  own stack rates (Exhibit 5-11, t/a at an 85 % capacity factor, divided by 7446 h; they include
  the DLN burners and the SCR), CH4 3.697 and N2O 1.290 g/GJ from AP-42 Table 3.1-2a (SRC-3,
  uncontrolled natural-gas turbines; SRC-1 gives none). Particulates stay a flow-identity gap
  (no size split in either source, as ethylene-1);
- the SCR's 19 wt% aqueous ammonia (SRC-1 Exhibit 5-19: 3.45 short tons a day at full load) as
  two consumables: its NH3 (184,493 kg/a, linked to ammonia-1) and its water (786,523 kg/a,
  deionised water);
- allocation: none (one product).
The Atlas links (`lca/mappings.yaml`): natural gas by the shared `natural-gas` entry (kg, taken
as methane, `atlas: false` as utility-steam-ng-boiler and hydrogen-1), the demineralised water and
the ammonia's water to `water` (deionised), the blowdown to `wastewater` (the library's
utility-wwtp with prefer_atlas), the ammonia to ammonia-1. The raw water (feed:RW) stays a gap:
the shared vocabulary has no raw water entry, and a resource flow is a shared-file decision.
Excluded and recorded (`emission_exclusions`): the SCR's ammonia slip (SRC-1 gives only the
10 ppmv design limit at the end of the catalyst's life), start-ups and part load, fugitive gas,
the blowdown's dissolved solids. Not counted (TODO): the SCR catalyst's replacement (SRC-1
Exhibit 5-19: 3.10 ft3 a day after an initial 5,649 ft3), the water treatment chemicals (6.23
tons a day), lube oil, construction and decommissioning.
Reason: the CO2 and the fuel dominate an NGCC's footprint; the criteria pollutants come from the
same source as the design, so they belong to this plant's burners and SCR.
Rejected: AP-42 or IPCC defaults for NOx and CO: they describe other (uncontrolled or average)
turbines than SRC-1's DLN plus SCR.

### D-012 Equipment list (2026-11-19)
Decision: the PFD's main items with SRC-1's ratings in our own words (`equipment/equipment-list.yaml`).
No sizing of our own; SRC-1's design conditions carry its 10 % contingency on flows and duties.
The balance-of-plant items SRC-1 lists (water treatment, fire water, air compressors, auxiliary
boiler, switchgear, DCS) are not separate steps and are left out.

### D-013 Hazards at the concept stage (2026-11-19)
Decision: no reactor hazard screening: the process is continuous combustion with no
accumulating reactant (core's `reactor-hazards` screens batch and semi-batch reactors). The
hazards to carry to basic engineering are recorded: natural gas at 2.96 MPa in the turbine
enclosures and fuel skids (fire, explosion; gas detection and enclosure ventilation), an
explosive atmosphere in the HRSG after a flame-out or a failed start (purge before ignition),
steam at 16.5 MPa and 585 degC (relief, pipe rupture), hydrogen-cooled generators, the aqueous
ammonia storage for the SCR (toxic release), and Legionella in the wet cooling tower.
Reason: a concept entry names its hazards; their safeguards come with the P&IDs and a HAZOP.

## 4. Core features used and limits

Core features: conversion step with ideal-gas energy balance and `energy_port` (ADR 0059) for the
gas turbines; `cheme process propagate --fill`; `cheme assess lca` with emission estimates and
consumables; the balance-output contract of the library (ADR 0027) for scripts/ngcc_balance.py.

| id | limit | effect here | what would lift it |
|---|---|---|---|
| L-1 | No gas turbine model (compressor and expander with pressure ratio, isentropic efficiencies, cooling air, firing temperature) | the gas turbines are a lumped conversion step; their power follows from the given exhaust temperature, not from the machine | a turbomachinery model in core with vendor-independent defaults |
| L-2 | No property package for water and steam, no steam turbine or HRSG model (pinch, approach, sections) | the loop's states, the steam turbine's power and the condenser duty are SRC-1's enthalpies via the script, not calculated by core | an IAPWS-IF97 package and a Rankine-cycle model in core |
| L-3 | Energy-only steps (the electrical bus T901, the auxiliaries U901, the generators' losses) are not energy-balanced by `cheme validate` | the bus's closure is checked by tests/test_power_generation_1.py instead | an energy balance rule for nodes without material streams |
| L-4 | No part-load, ambient or degradation model | one design point at ISO and base load | performance curves from an open source |

## 5. Open items

- A second case at another ambient temperature or part load, once an open source gives one.
- The H-class variant (SRC-1 Case B32A) and the capture variants (B31B.90/.95, with carbon-capture-1).
- A raw water entry in the shared LCI vocabulary (feed:RW is a gap).
- The SCR catalyst and the water treatment chemicals in the LCI.
