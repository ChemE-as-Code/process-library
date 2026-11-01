# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#165. Run of 2026-10-28 (concept: design basis, balanced
BFD/PFD, preliminary LCI). Starting point: library `main` at 11d50ef, cheme 0.8.0 (pyDEXPI
2.1.0), thermo 0.6.1, chemicals 1.5.2.

## Route and boundary memo

**Product.** High-purity isobutene (polymer grade, >= 99.9 wt%) for butyl rubber,
polyisobutene, methyl methacrylate or tert-butyl chemicals. A mixed C4 cut cannot give it by
distillation alone: isobutene and 1-butene boil less than 1 K apart. So isobutene is either
made on purpose or taken out of the C4 cut chemically and released again.

**Routes considered.**

| route | what it does | why not / why |
|---|---|---|
| **MTBE back-cracking (selected)** | MTBE (from isobutene in a C4 cut + methanol) is split again over an acid catalyst into isobutene + methanol; the methanol is recovered | the issue's route; yields the highest purity because the ether step is isobutene-selective; equilibrium-limited but endothermic, so high temperature drives it; open patent ranges exist |
| TBA dehydration | tert-butanol (from isobutene hydration or PO/TBA co-product) dehydrated to isobutene + water | similar purification task; TBA is less available as merchant feed; not asked for |
| Isobutane dehydrogenation (variant) | on-purpose from isobutane over Pt-Sn or Cr-oxide catalyst at ~820-900 K and low pressure, with H2 co-product | stated variant, not designed: needs a dehydrogenation reactor with regeneration, compression and cryogenic or absorption recovery; the product is an isobutene/isobutane mix that usually goes to MTBE or alkylation, so polymer-grade isobutene still needs an ether or acid-extraction purification step |
| Cold acid extraction (H2SO4) | isobutene absorbed in sulphuric acid and released | obsolete, acid waste; not considered further |

**Boundary.** Gate-to-gate plant from fresh MTBE at the battery limit to isobutene, methanol,
heavy ends, DME-rich vents and a wastewater purge at the battery limit. MTBE is a boundary feed:
no library process makes MTBE yet; its methanol would come from processes like methanol-1 of
this library (noted in the LCI as the background link). Utilities (steam, cooling water, power,
fired heat, demineralised water) are bought from the site; storage is outside.

## D-001 Route: gas-phase MTBE cracking over an acidic silica-alumina type catalyst (2026-10-28)
Decision: MTBE is cracked in the gas phase in a heated multitubular fixed-bed reactor over an
acidic, magnesium-doped amorphous silica-alumina type catalyst; downstream an isobutene column,
a water wash for methanol, a drying/DME column, a methanol column with MTBE recycle and a
methanol/water column for the wash water.
Reason: the run's task named this route (`runs/20261028-150003-design/task.md`); issue #165
leaves the route open and asks for isobutene separated from mixed C4 streams to be compared,
as a case, with on-purpose production; that comparison is not made here (I-09). US 8,633,345 B2 (Evonik Oxeno; description of the
cleavage, catalyst and work-up) describes gas-phase cleavage over such a catalyst with the same
sequence of separations (products column, methanol extraction with water, drying column for DME
and water, methanol column with MTBE recycle), and gives ranges for each step.
Rejected: liquid-phase cracking over an ion-exchange resin (lower temperature, lower
equilibrium conversion, resin stability limits); reactive distillation (cracking inside the
column) as a variant for later.
Assumptions: the catalyst is a generic "acidic silica-alumina type": no vendor catalyst or
activity data are used.

## D-002 Capacity and product (2026-10-28)
Decision: 50 kt/a isobutene, 8000 h/a, 6250 kg/h at the battery limit, 1500 kPa(a), 313 K;
product >= 99.9 wt% isobutene (the design reaches 99.97 wt%).
Reason: no traceable plant basis was available in open sources (issue note: capacity missing);
50 kt/a is a single train of the usual order of magnitude, chosen, not sourced. ASSUMED. The
purity target is the purity US 8,633,345 B2 states as achievable; its market specification
limits (methanol, water, linear butenes) are not copied, only the methanol (< 30 ppm) and water
targets are used as checks.

## D-003 Feeds (2026-10-28)
Decision: fresh MTBE is pure MTBE at 300 kPa(a), 303 K; demineralised water for the wash loop.
Reason: a molecularly defined feed (issue scope note). Technical MTBE carries about 1 wt%
methanol, plus MSBE, TBA, C8, C5 and water (US 8,633,345 B2, its table of technical MTBE). MSBE
cracks to linear butenes, which limit the product purity; the patent's main concern is removing
those medium boilers. Not modelled: ASSUMED pure feed. Consequence: the real plant needs a
feed column that removes MSBE and C5 (the patent's columns with high reflux); this design's
C-101 only removes the C8 heavies (D-007) and so understates that column's duty.

## D-004 Reactor and operating conditions (2026-10-28)
Decision: reactor outlet 553.15 K (280 C), inlet 900 kPa(a), outlet 750 kPa(a); heated tubes
(isothermal at the inlet temperature); feed superheated to 523 K against the effluent (E-101,
30 K approach) and to 553 K in the fired hot-oil heater H-101, which also supplies the heat of
reaction.
Reason: US 8,633,345 B2 gives 150-500 C (preferred 200-400 C), 0.05-2 MPa (preferred 0.5-0.7
MPa) and an endothermic reaction; its lab example ran at 280 C / 0.7 MPa and its Example 2 at
305 C / 0.85 MPa. 280 C and 0.9/0.75 MPa sit inside those ranges, so the condensed effluent
can feed the 650 kPa(a) isobutene column. ASSUMED. Column pressures: C-201 650 kPa(a) (Example
2), C-301 100 kPa(a) (Example 2), C-101 1000 kPa(a) so its vapour overhead flows to the
reactor (the patent's high-boiler column runs at 0.95 MPa), C-402 150 kPa(a), C-403 900 kPa(a)
(inside 0.1-2.0 MPa). ASSUMED.

## D-005 Reaction model: conversion with selectivities, not kinetics (2026-10-28)
Decision: `process/reactions.yaml` holds CRACK (MTBE <=> IB + MeOH), DMEF (2 MeOH -> DME +
H2O) and DIM (2 IB -> C8). R-101 is a conversion reactor: MTBE conversion 0.90 per pass; per
kmol MTBE converted 0.010 kmol DME and 0.001 kmol C8 (so 0.998 kmol isobutene and 0.98 kmol
methanol leave). cheme solves the outlet (S8) from these; the extents are CRACK 112.27, DMEF
1.12, DIM 0.11 kmol/h.
Reason (evidence, our wording):
- Conversion: US 8,633,345 B2 gives 40-99 % per pass, preferably 85-95 %; its Example 2 reports
  about 94 %, its lab example 98 %. 0.90 is a mid value of the preferred range. ASSUMED.
- DME: the patent says DME selectivity should stay below 4 % (at most 10 %). In its Example 2
  reactor effluent (Table 11) the DME/isobutene molar ratio is about 0.010; we take 0.010 kmol
  DME per kmol MTBE converted (2 % of the methanol). ASSUMED, of the order of that example.
- C8: Example 2's reactor effluent (Table 11) reports no C8; the lab cleavage of Example 1
  (Table 6) has about 0.06 wt% C8 in the effluent, a C8/isobutene molar ratio of about 0.0005;
  we take 0.001 (conservative). ASSUMED. (Locator corrected after review
  2026-10-28-pfd-lci-review#1.) TBA (from water + isobutene), isoprene, dimethoxymethane and
  linear butenes from MSBE are not modelled (pure feed, D-003).
- Equilibrium: from the ideal-gas data of `process/materials.yaml`, cheme gives ln K = 6.81 at
  553 K for CRACK (bar basis) and ln(Q/K) = -3.34 at the outlet: far from equilibrium. A pure
  MTBE feed would reach about 0.995 conversion at equilibrium at 7.5 bar, so 0.90 is
  catalyst-limited, not equilibrium-limited. Heat of reaction +65.4 MJ/kmol at 298 K (+63.5 at
  553 K) from formation enthalpies (chemicals: CRC/ATcT).
- No rate law: no open kinetic data for this catalyst were found; no kinetics are invented.
  Catalyst mass is not sized (WHSV 1-3 1/h preferred in the patent would mean ~4-11 t).
Rejected: an equilibrium reactor (would overstate the conversion of a real catalyst bed).

## D-006 Balance method: independent script, specified splits, shortcut duties (2026-10-28)
Decision: `scripts/ib_balance.py` (run with `cheme run`) solves the plant for 1 kmol/h fresh
MTBE with component split specifications (D-007), iterates the MTBE and wash-water recycles to
1e-14, and scales to 6250 kg/h product. Its column, wash and vent outlets, the feed flows and
all duties are written into `process/flowsheet.yaml` as ASSUMED with the script as source;
mixers, splitters, pass-through steps and the reactor are calculated by `cheme process
propagate --fill` and agree with the script (reactor outlet identical to 6 digits). Duties:
ideal-gas enthalpies from the materials' cp polynomials (feed/effluent exchanger, superheater,
reactor, effluent cooling), pure-component latent heats, liquid heat capacities and ideal
Raoult bubble points from thermo/chemicals (columns: condenser (R+1)·D·lambda_top, reboiler
from the column energy balance on saturated liquids; coolers). cheme's ideal-gas reactor duty
(`cheme process reactors`: 1970.08 kW) reproduces the script's 1970.1 kW.
Reason: core has no property package qualified for MTBE / methanol / water / C4 (`cheme process
props --coverage`: every stream unsupported; `cheme process methods`: NRTL/UNIQUAC/UNIFAC only
as substitutes, no benchmark), so neither `props --fill` nor `simulate --fill` can be used
(polar/activity-coefficient benchmark). Ideal Raoult misses the MTBE/methanol and
C4/methanol azeotropes: temperatures and latent heats are approximate, duties perhaps
+/-30 %. Not a rigorous simulation; accuracy not stated.
Gated step: predictive simulation and enthalpy-based energy closure of every block wait for a
qualified activity-coefficient package for this system.

## D-007 Separation specifications (2026-10-28)
Decision (all ASSUMED unless a patent value is named; patent = US 8,633,345 B2):
- C-101 MTBE column, 1000 kPa(a), R 0.5: all C8 to the bottoms with MTBE at 60 wt% (the
  patent's high-boiler column bottoms in Example 2 are about 62 % MTBE); vapour overhead to the
  reactor. R 0.5 is ours (only C8 to remove, D-003); the patent's 4.2 serves an MSBE split.
- C-201 isobutene column, 650 kPa(a), R 0.7 (patent Example 2): overhead 99.8 % of the
  isobutene, all DME, 30 % of the water, 0.1 % of the MTBE and methanol at 2.5 wt% of the
  distillate (the patent notes that isobutene takes methanol overhead as an azeotrope; the 2.5
  wt% is our estimate).
- C-301 methanol column, 100 kPa(a), R 1.9 (patent Example 2): overhead all MTBE, C8 and C4
  with methanol at 14 wt% (near the MTBE/methanol azeotrope; our estimate), recycled to V-101;
  bottoms methanol with all the water (99.6 wt% methanol; patent example about 99 wt%).
- C-401 water wash, 313 K, 880 kPa(a): 0.15 kg water per kg crude isobutene; 99.9 % of the
  methanol and 30 % of the DME extracted; 0.2 wt% isobutene dissolved in the extract; raffinate
  water-saturated at 0.08 wt%. The patent's 4-16 theoretical stages and 15-50 C bracket this;
  its target is < 30 ppm methanol in the washed isobutene (ours: 26 ppm in the product).
- C-402 methanol/water column, 150 kPa(a), R 1.5: 99 wt% methanol overhead, 100 ppm(w)
  methanol in the water bottoms; dissolved C4 and DME vented to fuel gas.
- C-403 drying/DME column, 900 kPa(a), R 30 (patent: reflux below 40 preferred): 99 % of the
  DME overhead as vapour distillate with an equal mass of isobutene (loss), 99 % of the water
  decanted from the reflux drum and returned to the wash loop; isobutene as bottoms.
- Wash-water loop: 5 % of the regenerated water purged to wastewater, make-up demineralised
  water closes the loop.
Result: 99.97 wt% isobutene (MTBE 176, DME 58, methanol 26, water 8 ppm(w)); methanol
co-product 99.55 wt%; isobutene yield on MTBE 99.0 mol% (111.37 kmol/h isobutene in the
product from 112.49 kmol/h fresh MTBE; 1.587 kg MTBE per kg product).

## D-008 Co-products and residues (2026-10-28)
Decision: recovered methanol (3541 kg/h) leaves as a co-product (back to an MTBE synthesis or
sale); C-101 bottoms (31.5 kg/h, C8 and MTBE) go to the site fuel oil system; the C-402 and
C-403 vents (89.1 kg/h, DME and isobutene) to the site fuel gas header; the wash-water purge
(48.8 kg/h, 100 mg/kg methanol) to the site wastewater treatment.
Reason: the usual destinations; recovering DME as a product is possible but too small here.

## D-009 Utilities (2026-10-28)
Decision: MP steam 1500 kPa(a) for C-101 (2013 kW); LP steam 450 kPa(a) for C-201 (1423 kW),
C-301 (232 kW), C-402 (210 kW), C-403 (383 kW); fired heat (natural gas, hot oil) 2192 kW
absorbed (superheat 222 kW, reaction 1970 kW); cooling water 25/35 C, 5300 kW in total;
electric pumps 15.8 kW (V·dP/0.6 over nine pumps, lumped on the P101 step) and the heater's
combustion-air fan and hot-oil circulation pump 30 kW (Q18, ASSUMED order of magnitude, not
sized). Per kg isobutene (before allocation): MP steam 1.16 MJ, LP steam 1.29 MJ, fired heat
1.26 MJ, cooling 3.05 MJ, power 0.0073 kWh. All ASSUMED levels and estimates.
Reason: the reboilers sit at 337-436 K; only C-101 (436 K) needs MP steam: LP steam condenses
at 420.8 K, a 27 K approach to C-201's 394 K bottoms, above the 10 K minimum approach, so C-201
and the rest take LP (corrected after review 2026-10-28-pfd-lci-review#2). The reactor at
553 K needs a fired or hot-oil heat source; superheated HP steam is too cold. The fan and
hot-oil power was first a cut-off; at about twice the pump power it is counted in feed:POWER
instead (review 2026-10-28-pfd-lci-review#3). Heat integration (e.g. C-201 condenser or E-102 heat into C-301/C-402 reboilers) is
not done: an open improvement.

## D-010 Equipment design data (2026-10-28)
Decision: design pressure = highest operating pressure + 10 % (at least + 2 bar), design
temperature = highest operating temperature + 25 K; carbon steel throughout (no wet
chloride, no hydrogen; acid catalyst confined to the reactor tubes). ASSUMED concept rules.

## D-011 LCI: foreground inventory, mass allocation, every background a gap (2026-10-28)
Decision: `lca/lca.yaml` (functional unit 1 kg isobutene at the gate, design case): every
foreground exchange from the balanced flowsheet with its stream or duty id; all backgrounds
`missing:` with a description of the activity they should connect to (8 gaps); mass
allocation between isobutene, methanol, heavy ends and vents (isobutene share 63.1 %), energy
(LHV from formation enthalpies) and substitution computed for comparison; cut-off system model
in the dataset; `process.yaml` `lca.source: none` so no all-gap 0 reaches the catalog.
`lca/mappings.yaml` only fixes units (steam and fired heat in kWh, wastewater in kg), as hda-1
does; MTBE, methanol, heavy ends and vents stay unmapped (ADR 0022).
Reason: the task asks for a foreground LCI with backgrounds unmapped. Mass allocation because
the cracking splits the MTBE molecule into two chemical feedstocks (ISO 14044 step 2, physical
relation); an agent proposal for the LCA practitioner to confirm. The fired heater's combustion
is inside the heat background (no double count); the vents' and heavy ends' combustion belongs
to their user.
Emissions: no direct process emission to air leaves this boundary (all vents go to fuel);
fugitive VOC (isobutene, MTBE, methanol, DME) not estimated until P&ID component counts exist
(I-05); the only emission to water is the purge to treatment.
Check: inventory mass balance (unallocated, kg/h): in 9915.89 MTBE + 44.40 water = 9960.29;
out 6250.00 + 3540.87 + 31.49 + 89.15 + 48.78 = 9960.29. `cheme assess lca --coverage`: mass,
element and carbon-origin balances closed.

## Source register

| source | locator | access | use | reuse |
|---|---|---|---|---|
| US 8,633,345 B2, Evonik Oxeno (2014), "Process for preparing isobutene by cleaving MTBE-containing mixtures", https://patents.google.com/patent/US8633345B2/en | description of the cleavage (temperature, pressure, WHSV, conversion, catalyst composition); work-up (water extraction, drying column, methanol column); Example 1 (lab cleavage, Table 6); Example 2 (column pressures and reflux ratios, Tables 9-12); technical MTBE (Table 2) | read (full text, Google Patents) | ranges for D-001, D-004, D-005, D-007; facts in our own words, no table copied | patent text is public; facts only |
| Ullmann's Encyclopedia of Industrial Chemistry, Butenes, doi:10.1002/14356007.a04_483.pub3 | chapter (route context) | metadata only (issue #165 note), not audited | route context only; no numbers used | licensed: no content |
| chemicals 1.5.2 / thermo 0.6.1 (C. Bell, MIT) | `cheme chemistry thermo`; EnthalpyVaporization, HeatCapacityLiquid, VaporPressure | software | formation data, cp, latent heats, bubble points | MIT; values with their database tags in materials.yaml |
| Cox, Wagman, Medvedev (1989) CODATA Key Values | CO2(g), H2O(g) formation enthalpies | book | LHVs in lca.yaml | facts |

## Open inputs and issues

- I-01 Capacity and site: 50 kt/a and a generic site are ASSUMED; a traceable plant basis
  (sourced capacity, MTBE assay) would lift the maturity check `sourced-boundary`.
- I-02 Property method: no qualified package for MTBE/methanol/water/C4; the
  column temperatures, the azeotrope-limited splits (2.5 wt% methanol over C-201, 14 wt% in
  the C-301 recycle) and all duties must be rechecked with NRTL/UNIQUAC and sourced binary
  parameters, and the wash with liquid-liquid equilibrium data.
- I-03 Catalyst: life, charge and deactivation (the patent raises the inlet temperature as
  the catalyst ages) not sourced; catalyst cut off in the LCI (~3 t/a, ASSUMED).
- I-04 Technical MTBE impurities (MSBE, TBA, C5, methanol, water) not modelled (D-003); with
  them C-101 becomes the patent's high-reflux medium/high-boiler column and the duty rises.
- I-05 Fugitive emissions: not estimated until the P&IDs give component counts.
- I-06 Heat integration not done (D-009).
- I-07 Registry entries missing (shared `chemicals/chemicals.yaml`, for the consolidated PR):
  isobutene, methyl-tert-butyl-ether, methanol, dimethyl-ether, diisobutene (C8), and fuel
  gas / heavy fuel oil if co-products are to be linked; shared `lci/mappings.yaml` has no MTBE
  or methanol technosphere entry.
- I-08 Atlas LCI build (`scripts/build_lci.py`) not run locally (openpyxl missing in this
  environment): the overrides in `lca/mappings.yaml` are checked by name only.
- I-09 Route alternatives of issue #165: isobutene separated from mixed C4 streams (e.g. a
  raffinate-1 route through MTBE or TBA, or direct separation, which plain distillation cannot
  do) compared as a case with on-purpose production (MTBE cracking, isobutane
  dehydrogenation) is not made; this case designs MTBE cracking only (D-001).
