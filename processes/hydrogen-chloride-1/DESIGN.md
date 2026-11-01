# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/balance.py`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#137.

Run record of this stage (2026-10-28): library branch `case/hydrogen-chloride-1` from `11d50ef`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Electrolytes as installed:
`cheme process methods` lists ENRTL-PR and PITZER-RKS as unsupported and the electrolyte route as
NaCl-H2O only (issue #137 comment), so **HCl-water is not supported** by any
phase, property or simulation route of this cheme. No property package covers Cl2 or HCl gas
either (`air-pr-chemsep`, `syngas-pr-vapor`). Both gates are recorded in section 6.

## 1. Route and boundary memo

- **Route** (issue #137 case notes): direct synthesis H2 + Cl2 -> 2 HCl in a burner, the HCl gas
  absorbed in water to 33 wt-% hydrochloric acid in a water-cooled graphite falling-film
  absorber, the absorber tail gas scrubbed with the absorption water, the reaction heat
  recovered as steam. Rejected routes: HCl recovered as a by-product of organic chlorinations
  (EDC/VCM, isocyanates, chloromethanes; most of the world's HCl, Wikipedia "Hydrochloric
  acid", section Industrial market: about 3 of 20 Mt/a by direct synthesis) and the salt/
  sulfuric acid (Mannheim) route: the issue asks for the synthesis burner, and by-product HCl
  belongs to the organic process that makes it.
- **Product form** (issue: settle anhydrous vs aqueous): aqueous hydrochloric acid 33 wt-%
  (D-002). Anhydrous HCl would need desorption/drying after absorption; out of scope.
- **Boundary of this case: saleable acid** (D-001). From chlorine and hydrogen gas at the
  fence (made by chlor-alkali-1, D-003), demineralised water, electricity and cooling water to
  33 wt-% acid at 2.5 bar(a) to storage, steam exported at 1000 kPa(a) and the scrubber vent.
  Inside: synthesis burner and steam-raising furnace (R-101, steam drum and BFW pump in its
  package), falling-film absorber (C-201), tail gas scrubber (C-202), product pump (P-201).
  Outside: chlorine and hydrogen production and their compression or drying, acid storage and
  loading, the emergency absorption (caustic) system, BFW treatment, cooling water system.
- **What crosses the boundary**: CL2, H2, DMW (raw materials), POWER (utility in), HCLACID
  (product), STEAM (co-product, energy), VENT (emission), CW (utility out).
- **Normalisation**: per kg of HCl (100 %) contained in the acid; the acid stream is 3.03 kg per
  kg HCl.
- **Link to other library processes**: CL2 and H2 are chlor-alkali-1's products S42 and S44
  with their states; this unit uses 25.7 % of its chlorine (3 209 of 12 500 kg/h) and 28.2 %
  of its hydrogen (104 of 368 kg/h). The two are not integrated: chlor-alkali-1 stays the
  producer, this case consumes (issue: link rather than silently integrate). chlor-alkali-1
  itself buys 32 wt-% HCl for its brine (feed:HCL there): a linked study must not count that
  acid twice if it comes from this unit.

## 2. Source register

Read status: "read" = the cited locator was read in full text by this run; "metadata" = only
the identity was checked. Facts are in our own words; nothing copied.

| id | source | locator | status | terms | used for |
|---|---|---|---|---|---|
| SRC-1 | NIST-JANAF Thermochemical Tables, 4th ed. (Chase 1998), https://janaf.nist.gov/tables/Cl-026.html and H-064 | table Cl-026 (HCl, g), H-064 (H2O, g): dHf 298.15 K | identity and dHf values checked (via search summary) | US government data | heats of reaction (process/reactions.yaml) |
| SRC-2 | ATcT / CRC / Poling 5th ed. via `cheme chemistry thermo` (`chemicals` package) | printed records in process/materials.yaml | read (tool output) | data facts | ideal-gas data, equilibrium constant, furnace duty |
| SRC-3 | US 9 415 364 B2, "Facility and reactor for directly synthesizing hydrochloric acid from hydrogen and chlorine with heat recovery", https://patents.google.com/patent/US9415364B2/en | Background (reaction heat about 92 kJ/mol HCl, flame 2500-3000 degC, steam targets 7-16 bar, graphite limited to about 3.5 bar steam, acid up to 38 %); Description (gas about 250 degC leaving the convection section, reactor gas about 0.5 bar) | read (first 100 000 characters of the Google Patents text) | patent text: facts only | D-007 furnace outlet and steam level |
| SRC-4 | US 2004/0175323 A1 (SGL Carbon), https://patents.google.com/patent/US20040175323A1/en | [0015]: prior art EP 0 362 666 B1 runs 2-15 vol-% excess hydrogen in the off-gas to avoid chlorine break-through | read | patent text: facts only | D-004 hydrogen excess range |
| SRC-5 | Wikipedia, "Hydrochloric acid", https://en.wikipedia.org/wiki/Hydrochloric_acid | sections Production and Industrial market; physical properties table | read | CC BY-SA: facts only | product grade (bulk 30-35 %, up to 38 %), density of 32-34 % acid, world production split |
| SRC-6 | Parker, V. B. (1965) Thermal Properties of Aqueous Uni-Univalent Electrolytes, NSRDS-NBS 2, US GPO: heat of solution at infinite dilution (as tabulated by Purdue Science Express "Enthalpy of Solution Reference") and integral heats of dilution pp. 10-19 (as tabulated in Wikipedia "Heat of dilution", https://en.wikipedia.org/wiki/Heat_of_dilution) | HCl(g) to infinite dilution -74.84 kJ/mol; heat released on dilution to infinity from 1 and 10 mol water per mol HCl: 48.83 and 5.841 kJ/mol | infinite-dilution value from a search summary (Purdue PDF 404 on fetch); dilution values read on the Wikipedia page | US government data | consistency check for D-009 |
| SRC-7 | Ullmann's Encyclopedia, "Hydrochloric Acid", doi:10.1002/14356007.a13_283 | none | metadata (issue #137 lead) | licensed | route identity only; no number taken |
| SRC-8 | chlor-alkali-1 (this library), process/flowsheet.yaml streams S42, S44 | stream states | read | CC BY 4.0 (own) | D-003 feed states |
| SRC-9 | IAPWS-IF97 steam properties | saturation at 1000 kPa(a) (453.0 K, h'' 2777.1 kJ/kg), water at 378 K (441 kJ/kg), psat 303/313 K | values from the standard as commonly tabulated | open standard | D-007, D-008 |
| SRC-10 | vendor white papers (SGL Carbon HCl synthesis units) | none | not readable (encrypted PDF) | vendor | not used |
| SRC-11 | EPA AP-42 section 8.6 Hydrochloric Acid | Table 8.6-1 | PDF not readable in this environment | US government | not used; to read for vent emission factors (open input) |

Not found in open sources by this run: the hydrogen excess actually used in modern units
(only the 2-15 % prior-art range), the integral heat of solution of HCl near 4 mol water per mol
HCl, steam yield per t HCl, absorber recovery and vent HCl concentration.

## 3. Reaction and model evidence

- **Chemistry.** H2 + Cl2 -> 2 HCl, dHr = -184.6 kJ per kmol extent (SRC-1; ATcT gives
  -184.3); the O2 of the chlorine (1.8 vol-% in chlor-alkali-1's gas) burns to water,
  2 H2 + O2 -> 2 H2O, -483.7 kJ (SRC-1). Both are in `process/reactions.yaml`.
- **Model basis: equilibrium limit, not kinetics** (D-005). The hydrogen-chlorine flame is a
  radical chain reaction at 2500-3000 degC (SRC-3), far faster than the gas residence time in the
  furnace; the composition leaving the furnace is therefore set by equilibrium as the gas
  cools. From the ideal-gas data (SRC-2), ln K = 44.70 (K = 2.6e19) for H2 + Cl2 = 2 HCl and
  ln K = 100.2 for the water reaction at 523 K (`scripts/balance.py`); with the 10 % hydrogen
  excess the equilibrium Cl2 mole fraction is 7e-19, so Cl2 and O2 conversions of 1.0 are the
  equilibrium result, written as a conversion reactor because cheme's equilibrium reactor does
  not converge with K this large (200 Newton steps, recorded below). No rate law is used or
  needed; none is invented. Free chlorine of order 1 ppm in real product acid (vendor and
  analyser literature found by search) comes from non-ideal mixing and is not modelled.
- **Cross-check by cheme.** `cheme process reactors` gives the R101 duty on the elements basis:
  -2 267.9 kW (heat released from feeds at their temperatures to the outlet at 523.15 K), equal
  to the independent script's 2 427.6 kW reaction heat at 298 K + 23.7 kW feed sensible heat -
  183.4 kW outlet sensible heat.
- **Absorption**: specified-value model (C201: 99.5 % of the HCl absorbed; C202: vent at
  10 mg/Nm3 HCl), not predicted. HCl-water VLE and heats of solution need an electrolyte model
  (unsupported for HCl); the 33 wt-% product is far above the 20.2 wt-% azeotrope
  (SRC-5), so it is made by isothermal (cooled) absorption, as SRC-3 describes, not by
  adiabatic absorption with boil-off.

## 4. Decisions

## D-001 Boundary: saleable 33 wt-% acid, steam export, no storage (2026-10-28)
Decision: the boundary of section 1. Reason: the issue asks for synthesis, absorption, tail-gas
scrubbing and heat recovery with chlorine and hydrogen as boundary feeds. Rejected: including
acid storage and the emergency caustic absorber (start-up and upsets only, no routine flows).
Assumptions: the steam system (drum, BFW pump) belongs to the furnace package.

## D-002 Capacity and product: 10 t/h of 33.0 wt-% acid, 8000 h/a (2026-10-28)
Decision: 10 000 kg/h acid = 3 300 kg/h HCl = 26.4 kt/a HCl (100 %). ASSUMED: no published
plant basis was chosen (issue #137: capacity missing); the size is a single synthesis unit
using about a quarter of chlor-alkali-1's chlorine. 33 wt-% lies inside the bulk grade range of
30-35 % (SRC-5) and the issue's 32-36 %. The per-kg inventory does not depend on the size.

## D-003 Feeds: chlor-alkali-1's chlorine and hydrogen as delivered (2026-10-28)
Decision: S1 has chlor-alkali-1 S42's state (99.19 wt-% Cl2, 0.81 wt-% O2, 400 kPa(a),
313 K); S2 has S44's (67.9 wt-% H2, 32.1 wt-% water vapour, 140 kPa(a), 337 K). The values are
ASSUMED in chlor-alkali-1, so they are `assumed` here too, never `given`. Reason: the case notes
link the feeds to chlor-alkali-1. Real cell gases also carry N2, CO2 and traces (not in
chlor-alkali-1's balance); they would pass to the vent. The water of the wet hydrogen ends up in
the acid, which lowers the demineralised water need; a drier hydrogen changes only S7.

## D-004 Hydrogen excess 10 mol-% (2026-10-28)
Decision: H2 fed = 1.10 x (Cl2 + 2 O2). ASSUMED inside the 2-15 vol-% excess-hydrogen range of
SRC-4 [0015]; the excess guarantees chlorine-free gas (no free Cl2 in acid or vent). It sets the
vent (9.5 kg/h H2, 2.9 g/kg HCl) and the hydrogen use; to be fixed with the burner supplier.

## D-005 R101: complete conversion of Cl2 and O2 at the equilibrium limit (2026-10-28)
Decision: conversion reactor, Cl2 and O2 conversion 1.0, justified by section 3. Rejected:
cheme's equilibrium reactor (`reactor: equilibrium`, outlet 523.15 K): `cheme process propagate`
stopped with "no convergence in 200 Newton steps" for K of order 1e19/1e40; a core finding to
report, not a design one. Rejected: inventing a burner efficiency below 100 %.

## D-006 Balance method: independent script for the absorption section (2026-10-28)
Decision: `scripts/balance.py` (run `cheme run scripts/balance.py`) gives the flows and
compositions of S1, S2, S4-S9 and the duties Q1-Q4, entered as `assumed` with
`source: scripts/balance.py`; S3 is calculated by cheme (propagate) and agrees with the script
(3 388.2 kg/h; HCl 0.9740, H2O 0.0232, H2 0.0028 by mass). Reason: cheme cannot solve the
absorber or the scrubber (electrolyte). The script closes mass (10 013.0 kg/h) and Cl, H
and O; cheme validate confirms every block, step and element balance.

## D-007 Furnace outlet 523 K, steam 1000 kPa(a), 3 % heat loss (2026-10-28)
Decision: the furnace gas leaves the steam-raising section at 250 degC (SRC-3, Description);
steam is raised at 1000 kPa(a) saturated (inside SRC-3's 7-16 bar, and chlor-alkali-1's MP steam
level, so it could serve that plant's evaporator) from BFW at 378 K (ASSUMED deaerator
temperature); heat loss 3 % of the reaction heat (ASSUMED). Result: Q1 = 2 195 kW, 3 383 kg/h
steam = 1.03 t per t HCl. Rejected: a graphite furnace raising hot water or low-pressure steam
only (SRC-3: graphite limits steam to about 3.5 bar); the metallic furnace keeps its process-side
walls above the acid dew point (SRC-3), which is a materials question for basic engineering.

## D-008 Absorption: isothermal falling film, scrubber with all absorption water (2026-10-28)
Decision: C201 absorbs 99.5 % of the HCl (ASSUMED) into weak acid from C202 and delivers
33 wt-% acid at 313 K, 120 kPa(a); its tail gas leaves at 313 K saturated with water (psat
7.385 kPa over the weak acid, taken as water, SRC-9). C202 receives all 6 625 kg/h of
demineralised water (298 K, 300 kPa(a)) and vents at 303 K, 105 kPa(a), water-saturated, with
10 mg/Nm3 HCl (ASSUMED, a common emission-limit order of magnitude; no BAT-AEL for HCl synthesis
was read). P201 pumps the acid to 250 kPa(a). All ASSUMED, to be replaced by an absorber model
or vendor data.

## D-009 Heat of solution of HCl to 33 wt-% acid: -61.4 kJ/mol, ASSUMED (2026-10-28)
Decision: the integral enthalpy of solution of HCl(g) in water to the product (4.11 mol water
per mol HCl) is taken as -61.4 kJ/mol at 298 K; acid heat capacity 2.55 kJ/(kg K). Both
ASSUMED: interpolated from recalled NBS Circular 500 integral heats (about -61 kJ/mol at 4 mol
water, -64 at 5), not read at source in this run. Consistency check with Parker 1965 (SRC-6):
the integral heat of solution to n mol water is -74.84 kJ/mol plus the heat of dilution from n
to infinity, i.e. -26.0 kJ/mol at n = 1 and -69.0 kJ/mol at n = 10; the recalled values for
n = 4-5 lie between and follow the same curve, but SRC-6 has no point at n = 4.11, so the value
stays ASSUMED. The heat of solution is 1 544 of the 1 672 kW
absorber duty (Q3), so a 10 % error moves Q3 by 9 %. Gate: core's electrolyte support (no HCl-water enthalpy).

## D-010 Cooling water 25/35 degC (2026-10-28)
ASSUMED, as chlor-alkali-1. Only C201 is cooled (Q3 = 1 672 kW = 0.507 kWh/kg HCl).

## D-011 Electric power (2026-10-28)
Decision: Q4 product pump 0.62 kW (130 kPa, 1 160 kg/m3 (SRC-5: 32-34 % acid 1.159-1.169 kg/l),
efficiency 0.5); Q2 BFW pump 1.98 kW (1 000 kPa rise, efficiency 0.5) plus 3 kW for instruments,
burner management and analysers. All ASSUMED; 5.6 kW in total (1.7 kWh/t HCl). No blower: the
feed pressures drive the gas through the unit to the vent (SRC-3: reactor gas about 0.5 bar(g)).

## D-012 Equipment list: PFD items only (2026-10-28)
R-101, C-201, C-202, P-201 with service, ASSUMED design conditions and materials (graphite
absorber, lined scrubber and pump, steel furnace with hot walls). The line and instrument lists
stay empty until the P&IDs (out of scope of this run).

## D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: `lca/lca.yaml`, functional unit 1 kg HCl in the 33 wt-% acid (3.0303 kg acid). Every
background is declared `missing:` with the activity it should connect to (chlor-alkali-1's
dataset for chlorine and hydrogen, demineralised water, grid electricity, cooling water), so
each is a gap, never 0. Allocation: shares 1/0 between acid and exported steam under cut-off,
as nitric-acid-1 (its decision 14): energy allocation would put everything on the steam (the acid
has no energy content) and the acid's exergy cannot be calculated; substitution by
natural-gas boiler steam is kept for comparison (missing). Emissions: the vent (H2, HCl, water)
to air; the furnace burns no air and no carbon, so no combustion emission exists (declared
exclusion); start-up and upset venting, tank breathing (outside) and leaks are declared
exclusions without amounts. `lca/mappings.yaml` has no overrides: the feeds' registry
`inventory_key`s are left out of process.yaml, because the Atlas build would otherwise link the
wet hydrogen by wet-gas mass to a hydrogen producer (47 % too much H2) and demineralised water
to raw water.

## 5. Results of this stage

- `cheme validate`: 0 errors, 0 warnings. `cheme process streams`: blocks SYN (3 388.2 kg/h)
  and ABS (10 013.0 kg/h) and steps R101, C201, C202, P201 balance; extents HCL_SYN 45.254 and
  H2_OX 0.821 kmol/h.
- Per kg HCl: chlorine gas 0.980 kg (0.972 kg Cl2, the stoichiometric 0.9724 plus a 0.3 mg/kg vent
  loss), wet hydrogen 0.0464 kg (0.0315 kg H2), demineralised water 2.008 kg, electricity
  0.0017 kWh, cooling 0.507 kWh, steam exported 0.665 kWh (1.03 kg at 1000 kPa(a)), vent 3.9 g
  (2.87 g H2, 0.33 mg HCl, water).
- LCI (`cheme assess lca --inventory --write`, `--coverage`, `--balance`): mass and Cl/H/O
  close to 0.00 %; classification "partial screening carbon footprint" with 7 gaps (CL2, H2,
  DMW, POWER, CW, and H2 and HCl to air without a climate factor); the library build
  (`scripts/build_lci.py --strict`) reports 4 gaps for this process (CL2, H2, DMW unlinked; HCl
  to air without a biosphere identity) and no error. The `--balance` "energy closure 130.9 %"
  counts electricity, steam and cooling only; the reaction and absorption heat of the feeds is
  not counted there, so it is not an energy-balance finding.

## 6. Methods, dependencies and gated steps

| step | method here | status | gate |
|---|---|---|---|
| furnace composition | conversion 1.0 = equilibrium limit (section 3) | calculated by cheme | equilibrium reactor does not converge at K 1e19 (core finding, not filed by this run) |
| furnace duty and steam | cheme reactor duty (ideal gas) less 3 % loss | calculated + ASSUMED loss | none for the gas side |
| absorber, scrubber | specified values (script) | ASSUMED | core's electrolyte support: HCl-water VLE, heat of solution, acid enthalpy unsupported |
| stream properties, energy balances | not filled | not evaluable | no package for Cl2/HCl gas or HCl-water (`cheme process props --coverage`) |
| simulation | none | not run | DWSIM route refuses electrolytes (issue #137 comment) |
| LCI | foreground from the flowsheet | written | backgrounds missing; registry entries missing (section 7) |

## 7. Open inputs and library items

- Open inputs: hydrogen excess and burner design (supplier), absorber recovery and vent HCl
  (supplier or an electrolyte absorber model), integral heat of solution at source (NBS tables),
  steam yield of a real unit, heat loss, real chlorine/hydrogen impurities (N2, CO2), site and
  capacity, emission factors for start-up venting (AP-42 8.6 to read).
- Missing in `chemicals/chemicals.yaml` (consolidated PR later): `chlorine`, `hydrogen-chloride`
  (and a grade such as `hydrochloric-acid/33` for the solution). Missing in `lci/mappings.yaml`:
  a `chlorine` technosphere entry (or prefer_atlas to chlor-alkali-1), a wet-hydrogen proxy by
  mass of wet gas, a demineralised-water entry (#45), a biosphere identity for hydrogen chloride
  to air, and (for the crosswalk of core) H2 and HCl to air.
- Next stage: basic engineering after review of this concept: source the burner and absorber
  data, replace D-009 when core supports HCl-water, then the P&IDs (pid-draft) and the LCI
  backgrounds (link chlor-alkali-1's dataset).
