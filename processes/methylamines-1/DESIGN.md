# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml`; the stream table is generated: `cheme process streams
--md` (provenance letter per value). Issues: ChemE-as-Code/process-library#171 (methylamine) and
#166 (dimethylamine), designed as one co-production plant.

Run record of this stage (2026-10-28): library branch `case/methylamines-1` from `11d50ef`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; thermo 0.6.1, chemicals 1.5.2 and scipy in
cheme's interpreter; DWSIM not used. The core issues named in #171 (property/phase and
reaction-energy qualification, electrolytes) could not be read from this session
(`gh` cannot resolve them): their state is not checked here, and the gated steps below are
stated against what cheme 0.8.0 reports (`cheme maturity`, `cheme process methods`).

## 1. Route and boundary memo

- **Route**: vapour-phase amination of methanol with ammonia over an amorphous silica-alumina
  dehydration catalyst. The three methylamines form in sequence (NH3 -> MMA -> DMA -> TMA) and
  interconvert by transmethylation; on amorphous catalysts the outlet comes close to chemical
  equilibrium, which favours TMA, while the market wants mostly DMA (Corbin et al. 1997,
  abstract; US 4,485,261 A, background). The plant therefore recycles ammonia, TMA and the MMA
  not sold to the converter and sets its product slate by those recycles.
- **Alternatives not taken**: shape-selective zeolite catalysts (mordenite, chabazite) that
  suppress TMA and give a non-equilibrium distribution (US 7,435,855 B2; US 6,232,502) need a
  sourced selectivity model, not an equilibrium; dimethyl ether as a co-feed; the two-step
  process of US 4,485,261 A. All are later variants (separate branches), not this case.
- **Boundary**: from liquid methanol and liquid anhydrous ammonia at the battery limit to the
  three anhydrous amines to storage. Inside: feed drum and pumps, vaporiser, feed/effluent
  exchanger, adiabatic converter, effluent condenser, ammonia column, TMA extractive distillation
  with water, dehydration column, MMA/DMA column, methanol recovery column and the extraction
  water loop. Outside: methanol and ammonia production (methanol-1, ammonia-1 in this library:
  boundary feeds, never double counted here), storage and loading, dilution to the 40 wt%
  aqueous grades, steam and cooling-water systems, wastewater treatment, flare.
- **What crosses the boundary** (flowsheet terminals): MEOH, NH3F (raw materials); DMAP, MMAP,
  TMAP (products); WW (wastewater); POWER, MPS, LPS (utilities in), CW (heat rejected).
- **Co-production of #171 and #166**: one plant, one inventory; the two issues' products are
  co-products allocated by mass (D-014). A separate "MMA plant" and "DMA plant" would double
  count the shared converter and train.

## 2. Source register

Read status: "summary read" = the page was fetched and summarised in our own words in this
session; no text, table or figure is copied. Reuse: facts and numbers only, with the locator.

| id | source | locator | read status | used for |
|---|---|---|---|---|
| SR-1 | Corbin, Schwarz, Sonnichsen (1997) Methylamines synthesis: a review. Catal. Today 37, 71-102, doi:10.1016/S0920-5861(97)00003-5 | abstract (bibliographic record) | abstract only; full text not read | route context: equilibrium favours TMA, demand is DMA (D-001) |
| SR-2 | US 4,485,261 A, Process for producing methylamines | background (equilibrium at 400 C, N/C 2.0: MMA 0.288, DMA 0.279, TMA 0.433, basis not stated); prior art (DMA 0.270, TMA 0.445 by weight, 400 C, 20 atm); section 3 (four- and three-column separation trains); comparative example 1 (silica-alumina, 400 C, 20 atm) | summary read | equilibrium check (D-005), separation sequence (D-008), N/C (D-004) |
| SR-3 | US 4,283,254 A, Methylamines purification by distillation and purge | background (silica-alumina, 350-450 C, 200-350 psig; NH3 first by pressure distillation; reaction water purged); detailed description (higher-amine purge 0.1-5 % of a column feed) | summary read | converter window (D-004), by-product purge (cutoff) |
| SR-4 | US 3,387,032 A, Process for the manufacture of methylamines | description (200-500 C broad, 350-450 C and 150-300 psig preferred); example 1 (silica gel with 10-15 wt% alumina); claims 3-5 (recycle of MMA, DMA, TMA with excess NH3) | summary read; example tables poorly legible (OCR) | catalyst (SIAL), window (D-004), recycle (D-007) |
| SR-5 | US 7,435,855 B2, Process for the continuous synthesis of methylamines (zeolite) | description: 250-450 C, 5-50 bar, N/C 0.6-4.0, methanol conversion 85-99 %; examples 97.5-99.6 % conversion; coke regeneration by burn-off 350-650 C | summary read (first 100 k characters) | plausibility of conversion (D-005), N/C range (D-004), catalyst regeneration (LCI exclusions) |
| SR-6 | US 7,309,403 B2, Method for avoiding corrosion | abstract, detailed description and claim 1: column 1 NH3 overhead as an azeotrope with TMA, recycled; column 2 TMA overhead by extractive distillation with water fed above the feed; column 3 MMA + DMA overhead, water, methanol and by-products to the bottoms; column 4 MMA overhead, DMA bottoms; claims 2-3 optional column 5 methanol recovery from column 3 water; claims 1, 4-6 and summary: aqueous NaOH/KOH (about 25 %) preferably to the column 3 feed, amount only "enough to leave free alkali in the column 3 bottoms", against corrosion by CO2, carbamate and formic acid | description read 2026-10-28 (Google Patents text, after review #5) | separation sequence (D-008), caustic dosing (cutoff) |
| SR-7 | US 2,206,584 A | background, first column, about printed lines 15-35 (OCR): NH3 and TMA form a constant-boiling mixture, so distilling off NH3 takes TMA with it; acceptable because that NH3 is returned to the reactor; no composition, pressure or temperature of the mixture given | description read 2026-10-28 (OCR text, legible in this passage; after review #5) | TMA recycle with NH3 (D-007) |
| SR-8 | CN 1229328 C | summary: NH3, TMA (with water injection, high reflux), dewatering and MMA/DMA columns | search summary only | high reflux in C-102 (D-008) |
| SR-9 | chemicals 1.5.2 / thermo 0.6.1 (ATcT formation enthalpies, CRC entropies, Poling heat capacities, vapour pressures, heats of vaporisation) | `cheme chemistry thermo`, `thermo.Chemical` | used in this session | materials.yaml, equilibrium, duties |

Not found in open sources in this session (open inputs): the NH3-TMA azeotrope composition
at column pressure, converter space velocity and catalyst life, column stage counts and reflux
ratios, specific steam and power consumptions of a real plant, wastewater composition, by-product
yields (DME, higher amines, CO/H2). Ullmann's "Amines, Aliphatic" (doi:10.1002/14356007.a02_001.pub2)
is the obvious next reference; it was not accessible here.

## 3. Decisions

## D-001 Route and boundary: silica-alumina amination with recycle, feeds from methanol-1 and ammonia-1 (2026-10-28)
Decision: the classical equilibrium route on amorphous silica-alumina, boundary as in section 1.
Reason: the route the issue names (methanol + ammonia over an acid catalyst, recycle of the
unwanted amines, NH3 / TMA-extractive / MMA / DMA columns), with open patent sources for its
conditions and an equilibrium model that cheme can evaluate.
Rejected: zeolite (shape-selective) catalysts: no sourced selectivity model; a separate MMA or
DMA plant (double counting).
Assumptions: methanol and ammonia arrive pure; storage outside.

## D-002 Capacity and product slate: 8 t/h, MMA/DMA/TMA 25/55/20 wt% (2026-10-28)
Decision: net 2.0 t/h MMA, 4.4 t/h DMA, 1.6 t/h TMA (64 kt/a at 8000 h/a), all anhydrous.
Reason: a mid-size single train; DMA-led slate because DMA is the main demand (SR-1); the slate
is a design choice made possible by the MMA and TMA recycles.
Rejected: the equilibrium slate without recycle (about 33/30/37 wt% at 400 C, D-005).
Assumptions: ASSUMED, not a market study or client figure. Products pure in the model (D-008).
The "DMA is the main demand" reason rests on the abstract of SR-1 only (full text not read; review
#5): unverified.

## D-003 Feeds (2026-10-28)
Decision: liquid methanol at 300 kPa(a), 303 K; liquid anhydrous ammonia at 1500 kPa(a), 298 K;
both pure. Flows stoichiometric: one ammonia per amine and one methanol per methyl group of the
slate, plus the methanol lost in the wastewater.
Reason: storage-side conditions for liquid feeds. ASSUMED.

## D-004 Converter conditions: adiabatic, inlet 625 K, outlet 713 K, 2.2/2.0 MPa(a), N/C 2.0 (2026-10-28)
Decision: one adiabatic fixed bed; outlet 440 C; feed N/C (mol N / mol methyl carbon) 2.0.
Reason: inside the sourced window 350-450 C and 150-350 psig (SR-3, SR-4); the adiabatic energy
balance (scripts/mass_balance.py) gives an inlet of 625 K (352 C), also inside the window. A first
try at 693 K outlet gave an inlet of 605 K, below the window (`cheme.process-catalyst`), and was
rejected. N/C 2.0 is the condition of the sourced equilibrium point (SR-2) and inside the ranges of
SR-5.
Rejected: a tubular cooled reactor (no source for its design here).
Assumptions: ASSUMED; the pressure has no effect on the equilibrium (the three reactions conserve
moles), so it only sets the condensation of the effluent with cooling water.

## D-005 Reaction model: ideal-gas equilibrium of three methylations; no by-products (2026-10-28)
Decision: `reactor: equilibrium` with MMA_SYN, DMA_SYN, TMA_SYN at the outlet temperature, ideal
gas, data of process/materials.yaml. cheme solves R-101 (`cheme process propagate`); the balance
script solves the same equilibrium and agrees with cheme to six digits (S7 vs S8).
Reason: amorphous silica-alumina gives a near-equilibrium distribution (SR-2, SR-3); no kinetics
are invented.
Check against the source: at 400 C and N/C 2.0 from methanol and ammonia only, the model gives
mass fractions among the amines MMA 0.326, DMA 0.302, TMA 0.372 (mole 0.447/0.285/0.268) and a
methanol conversion of 99.1 %; SR-2 reports 0.288/0.279/0.433 as thermodynamically calculated
equilibrium ratios at 400 C and N/C 2.0 (Background of the Invention, paragraph beginning "However,
the final ratios of formation ..."; Google Patents text, no column/line numbers). Basis (checked
after review 2026-10-28-pfd-lci-review#4, page re-read 2026-10-28): the patent does **not** state
whether these are weight or mole fractions. The only explicit basis in the document is in its prior
art paragraph: a conventional catalyst at 400 C, 20 atm, equal amounts of ammonia and methanol
gives DMA 0.270 and TMA 0.445 "based on the total weight of the three amines", said to almost equal
the equilibrium values. Since those weight-basis ratios lie close to 0.279/0.433, the benchmark is
read as weight fractions: ASSUMED, an inference, not a statement of the source. On that reading the
model under-predicts TMA by about 6 points; if the basis were molar, the model's mole fractions
(TMA 0.268) would miss by about 16 points and the recycle flows and steam would be much further
off. The benchmark therefore stays weak until a second open source with a stated basis is found
(O-1). Likely causes: the formation data of DMA
and TMA (ATcT vs other compilations differ by a few kJ/mol) and ideal-gas behaviour. Effect: the
per-pass distribution and so the recycle flows and duties are uncertain by that much; the net
feeds and products (stoichiometric) are not affected. To resolve: fit an approach or the formation
data to sourced equilibrium data over a temperature range (O-1).
Per pass in the design case: methanol conversion 98.9 %, outlet amines 35.6/31.7/32.6 wt%.
Not modelled: dimethyl ether (formed and consumed on the catalyst), higher amines, decomposition to
CO/H2/CH4, coke. ASSUMED absent.

## D-006 Balance method: scripts/mass_balance.py, values ASSUMED (2026-10-28)
Decision: an independent script solves the recycle loop (least squares on the steady-state
recycles at the specified N/C), the sharp-split columns and concept duties; its column outlets,
recycles and duties enter the flowsheet as `assumed`; cheme calculates the converter outlet, the
mixer, the condenser and the splitters.
Reason: cheme 0.8.0 does not solve columns and has no qualified property package for this polar,
associating, azeotropic system (`cheme process props --coverage`: none applies); DWSIM is not run
(no benchmarked package, D-011 gated step).
Enthalpy model: ideal gas (Poling cp) minus the heat of vaporisation of each component
(thermo 0.6.1), no mixing or solution enthalpy (amine-water mixing is strongly exothermic: not
counted); bubble points by Raoult's law. Duties +/-30 % at best. Energy cross-check (restated after
review 2026-10-28-pfd-lci-review#8): steam 35.8 MW plus the gas-phase heat of reaction (extents x
formation-enthalpy heats, about 2.5 MW) is close to the heat rejected to cooling water, 38.3 MW, but
the bases differ: feeds enter and products and water leave liquid, so the consistent heat of
reaction is the liquid-basis one, roughly 3.4 MW (reviewer estimate from heats of vaporisation, not
recalculated here), and the wastewater S23 leaves at 393 K carrying about 0.7 MW that is in no duty.
On a consistent basis heat in (35.8 + 3.4) and heat out (38.3 + 0.7) still agree within about
0.2 MW, but the earlier 0.1 MW agreement was fortuitous and the check is no better than the +/-30 %
duties. Open: a wastewater cooler to biological-treatment temperature (about 0.7 MW, about 2 % more
cooling water in the LCI) is not yet in the flowsheet (O-3).
Maturity: the boundary feeds S1 and S2 are `given` as the design specification of this study (the
capacity and slate of D-002 and the pure feeds of D-003, themselves ASSUMED choices, with the
stoichiometric flows that follow from them), so `cheme maturity` reaches **balanced** and writes
checks/maturity.json; the claim `concept` stays inside that cap. (Before review #2 the feeds were
`assumed`, the evaluation reached no level, and the run report of 20261028-145903-design wrongly
said it stopped at balanced.)

## D-007 Recycles (2026-10-28)
Decision: all ammonia and the whole TMA recycle leave the ammonia column overhead (S10, TMA 5.5
mol%); the MMA beyond the product rate is split off the MMA/DMA column distillate (SPM); the
unconverted methanol returns from C-105.
Reason: NH3 and TMA form a constant-boiling mixture and are recycled together (SR-7; SR-2 section 3,
three-column train); the TMA product is then taken in the extractive column. Recycles in the design
case: NH3 842.6, TMA 49.5, MMA 94.8, methanol 3.9 kmol/h; converter feed 34.5 t/h.
Assumptions: the azeotrope composition at 1900 kPa(a) is not sourced (O-2; SR-7 and SR-6 confirm
that the mixture exists and is recycled, neither gives its composition): a distillate with 5.5
mol% TMA is assumed feasible.

## D-008 Separation train: five sharp-split columns (2026-10-28)
Decision: C-101 ammonia column (1900 kPa(a), R = 1.0); C-102 TMA extractive distillation with
water (500 kPa(a), R = 3, 1 kg water per kg feed, from C-105 bottoms); C-103 dehydration (600
kPa(a), R = 1.0: MMA + DMA overhead, water and methanol bottoms); C-104 MMA/DMA (600 kPa(a), R = 4);
C-105 methanol recovery (150 kPa(a), R = 1.5, bottoms 100 ppm(wt) methanol); the net reaction
water leaves as wastewater (SPW).
Reason: the sequence of SR-2 section 3 (four-column train) and SR-6, plus methanol recovery from the
water. Column pressures let every condenser use cooling water (top bubble point >= 315 K). Where a
column's feed is hotter than its bottoms (C-102, C-105) a minimum boil-up of 0.1 kmol per kmol
bottoms is assumed and the condenser takes the rest of the column energy balance.
Rejected: MMA column before dehydration (first draft): the MMA/DMA split on the wet stream needs
more boil-up.
Assumptions: all ASSUMED; sharp splits, products pure; no caustic dosing (SR-6 doses aqueous
NaOH/KOH to the dehydration-column feed but gives no rate: kept a cut-off flow), no higher-amine
purge (SR-3), no stage counts (O-3). After review #5 the sequence was checked against the read
description of SR-6 (columns 1-5 match C-101..C-105); C-102's high reflux still rests on SR-8, a
search summary only, and is unverified.

## D-009 Utilities (2026-10-28)
Decision: MP steam 1500 kPa(a) (471 K) to E-101, C-101, C-103; LP steam 450 kPa(a) (421 K) to
C-102, C-104, C-105; cooling water 25/35 C to E-103 and all condensers; no heat integration beyond
E-102.
Reason: each reboiler's bottoms bubble point plus at least 10 K (C-101 405 K, C-103 435 K: MP; C-102
382 K, C-104 335 K, C-105 393 K: LP). E-101 vaporises the feed to 453 K.
Open: the effluent condenses between about 400 and 313 K while the NH3-rich feed boils near 330-350
K at 2.4 MPa: integrating the two (and the C-101 condenser) could cut both steam and cooling water
substantially. The steam figures of the LCI are therefore an upper estimate (heat-integration
skill at the next stage).

## D-010 Drives (2026-10-28)
Decision: electric pumps; P-101 stands for the feed and recycle pumps, hydraulic power / 0.6.
Power 26 kW. ASSUMED. Reflux and bottoms pumps are not counted (small; O-3).

## D-011 cheme-as-code issues met (2026-10-28)
- `cheme process build` fails with "'typing.Union' object is not iterable" for steps of class
  `Pumping` or `SupplyingThermalEnergy`: their pyDEXPI `method` field is a union type that
  `step_method` iterates. Workaround: P-101 is a generic `ProcessStep` (so its outlet S4 is given,
  not propagated) and E-101 is `Evaporating`. To report to core.
- No property package covers the system (`cheme process props --coverage`); predictive simulation
  is the gated step (section 5).
- `cheme maturity` lists C-101..C-105 as "shortcut, predictive, sourced" and passes
  `balanced.model-basis`, although the columns have no model: their outlets are ASSUMED sharp-split
  stream values from scripts/mass_balance.py (D-006, D-008). Read the model-basis lines of that
  report as overstated for the columns. To report to core (review 2026-10-28-pfd-lci-review#7).

## D-012 Equipment list at concept stage (2026-10-28)
Decision: one item per PFD step with design pressure = highest operating + 10 % (at least + 2 bar)
and design temperature + 25 K, ASSUMED. Materials CS as placeholders; hot ammonia above about 300 C
(R-101, E-102: nitriding) and amine-water corrosion need a materials review. No line list or
instruments yet (no P&ID in scope).

## D-013 Registry and vocabulary entries missing (2026-10-28)
`chemicals/chemicals.yaml` has no `methanol`, `ammonia`, `methylamine`, `dimethylamine`,
`trimethylamine`; `lci/mappings.yaml` has no `methanol` technosphere entry (ammonia and steam-heat
exist). Since the review 2026-10-28-pfd-lci-review#1, process.yaml lists only registered flows in
`chemistry` (steam, electricity, cooling water, wastewater) and names the five unregistered
chemicals with their inventory keys in `validation.notes`, as ammonia-1 does, so that the library
catalog build (and CI) passes; they go back into `chemistry` with the registry PR. lca/mappings.yaml
maps only feed:NH3F, feed:MPS, feed:LPS to existing entries. To add in the consolidated PR: the five
chemicals (CAS 67-56-1, 7664-41-7, 74-89-5, 124-40-3, 75-50-3; products anhydrous, liquefied) and a
`methanol` technosphere entry. The family is `nitrogen-organics`.

## D-014 Preliminary LCI: per kg DMA, mass allocation, backgrounds unmapped (2026-10-28)
Decision: functional unit 1 kg anhydrous DMA at the gate; co-products MMA and TMA; mass allocation;
cut-off system model; every background left `missing:` with a description of the activity it
should connect to; scope declared cradle-to-gate so that the gaps are reported (the quantified
part is gate-to-gate). No direct emissions to air in the model (no vents, no fired unit; leaks not
estimated without a P&ID). The silica-alumina catalyst, caustic dosing and the higher-amine purge
are listed as cut-off flows with unknown amounts.
Reason: the amines come from one converter and train with the slate set by recycles; mass is the
simple physical basis; prices were not sourced for an economic comparison.
Result (lca/inventory.csv, per kg DMA, allocated): methanol 1.365 kg, ammonia 0.402 kg, power
0.0033 kWh, MP steam 3.47 kWh, LP steam 1.00 kWh, heat to cooling water 4.78 kWh, wastewater
0.768 kg; co-products 0.455 kg MMA and 0.364 kg TMA per kg DMA. Balance (cheme assess lca
--balance, per hour): mass 14140.2 in / 14140.0 out kg (+0.00 %), C, H, N, O closed. Coverage:
"partial screening", 7 gaps, no impact claimed.
Separate product cases (issue #171 asks to keep them when co-producing with #166; review
2026-10-28-pfd-lci-review#3): under mass allocation every product carries the same burden per kg,
so the inventory per kg anhydrous MMA (#171) and per kg anhydrous TMA is identical to the per kg
DMA one above (methanol 1.365 kg, ammonia 0.402 kg, and so on). The DMA functional unit is the
reporting choice, not a preference between the products; an economic or other non-mass
allocation would separate the cases and is then to be added as a scenario per product.
Results: every exchange is a gap, so there is no total; the `0` that `cheme assess lca --write`
puts in the total row of lca/results.csv and in the allocation table of lca/results.md means
"no total", not a zero footprint (review #6; reported to core as a tool issue).

## 4. Open inputs

- O-1 Equilibrium data: sourced equilibrium distributions over 350-450 C and N/C 1-4 (Ullmann,
  Corbin et al. full text) to fit or confirm the model (D-005).
- O-2 NH3-TMA (and TMA-MMA, TMA-DMA) azeotrope compositions at column pressure (D-007).
- O-3 Column stages, reflux ratios, extraction water ratio, pump list (D-008, D-010).
- O-4 Catalyst: space velocity, volume, life, regeneration (D-004, LCI cut-off).
- O-5 By-products: DME, higher amines, decomposition gases and the vent they need (D-005).
- O-6 Caustic dosing amount and wastewater composition (amines, NaOH, COD) (D-008, D-014).
- O-7 Product specifications (anhydrous grades, water and other-amine limits) (D-002).
- O-8 Market prices for an economic allocation comparison (D-014).

## 5. Method and dependency table

| step | status in cheme 0.8.0 | used here |
|---|---|---|
| element and mass balances of every block and step | supported | closed (cheme validate, process streams) |
| ideal-gas equilibrium reactor | supported (`reactor: equilibrium`) | R-101, agrees with the script |
| vapour-liquid equilibrium / columns of NH3-amines-methanol-water | no benchmarked package (polar / activity-coefficient benchmark) | sharp splits, ASSUMED |
| stream enthalpies, energy closure of blocks | not qualified for this system | script estimate (D-006); `balanced.energy-closure` MISS |
| DWSIM predictive simulation | needs a supported package (e.g. NRTL with sourced pairs) | not run; `predictive` level fails |
| aqueous speciation (amines are weak bases) | electrolyte support limited to NaCl | not needed at this stage (no pH-dependent step modelled) |

## 6. Recommended next stage

1. Source O-1 and O-2 (Ullmann, the Corbin review full text) and refit the equilibrium (approach or
   formation data) to the published distributions; rerun scripts/mass_balance.py.
2. Heat integration (feed vaporisation against the effluent condenser and C-101): pinch targets,
   then update the LCI steam figures.
3. Method selection for the separation (NRTL/UNIQUAC with sourced binary pairs for NH3, MMA, DMA,
   TMA, methanol, water; `cheme process phase`), then shortcut or rigorous columns in DWSIM once a
   package is supported.
4. The consolidated registry PR (D-013), then map the backgrounds (methanol-1 and ammonia-1
   datasets, steam, power, cooling water, wastewater treatment).
Acceptance checks: equilibrium within the sourced data's spread; balances closed (cheme validate
0 errors); LCI mass balance closed; every gap described.
