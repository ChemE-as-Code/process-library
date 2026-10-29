# Design decisions

Acetic anhydride by the ketene route, issue ChemE-as-Code/process-library#131. Concept stage:
route and boundary, design basis, balanced BFD/PFD, preliminary gate-to-gate LCI. One entry per
decision: what was decided, why, what was rejected, what it assumes. The numbers live in the
YAML files (`process/*.yaml`, `lca/lca.yaml`) and `scripts/ac2o_balance.py`; this file keeps the
reasons. Run of 2026-10-28 (library commit 11d50ef, cheme-as-code 0.8.0, pyDEXPI 2.1.0).

## Source register

Facts are restated in our own words; no table, figure or text is copied.

| id | source | locator | read | used for |
|---|---|---|---|---|
| SRC-1 | Hoechst AG, US 4,455,439 (1984) "Process for the preparation of ketene", https://patents.google.com/patent/US4455439A/en | Example and Comparison Example; description (prior art) | full text read (Google Patents) | cracking at 700 C, furnace outlet 358 mbar, 3.6 t/h acid; conversion 84 %, ketene 92 % of acid reacted (77 % of acid fed); condensate 38 wt% acetic acid; condensers on cooling water then -10 C brine, crude ketene at -5 C / 266 mbar; gas velocity 30-80 m/s; TEP catalyst and NH3 injection after the coil (no rates given); by-products CH4, CO2, CO, ethylene, allene (no amounts); nickel-free coil alloys |
| SRC-2 | Celanese, US 8,653,303 B2 (2014) "Processes for preparing acetic anhydride", https://patents.google.com/patent/US8653303B2/en | sections on ketene, Primary Reaction, Conversion of Unreacted Ketene; Tables 1-3 | full text read (Google Patents) | TEP 0.1-0.5 wt% of the feed; absorber top 3-100 kPa, overhead 35-55 C; reaction heat stated as -63 kJ/mol; crude anhydride preferably >= 85 wt%, acid 0.1-20 wt%; vent ketene 0.1-10 wt%; liquid circulation about 100 kg per kg ketene; decomposition gas burned for fuel, e.g. in the cracking furnaces |
| SRC-3 | Padmanabhan, N., Deshpande, P.K., Kuloor, N.R. (1968) "Catalytic cracking of acetic acid to acetic anhydride", I&EC Process Des. Dev. 7(4) 511-516 | abstract (IISc ePrints record) | abstract only | TEP a better catalyst than silica gel; best ketene yield at 750 C and 100 mmHg; first-order kinetics measured (not used: no rate law taken) |
| SRC-4 | Ullmann's Encyclopedia, "Acetic Anhydride and Mixed Fatty Acid Anhydrides", doi:10.1002/14356007.a01_065 | - | not read (licensed) | route reference lead only (issue #131) |
| SRC-5 | `chemicals` / `thermo` packages (Bell et al.), via `cheme chemistry thermo` and `cheme run` | ATcT/CRC formation enthalpies, TRC ideal-gas Cp, liquid Cp, Hvap, vapour pressure correlations | used | materials.yaml data, heats of reaction, script enthalpies |

Not used: Intratec's acetic anhydride cost-report page (commercial; only its public summary was
seen) and a 2008 dilute-acid recovery abstract (Chemical Industry and Engineering, Tianjin), which
confirm extraction plus azeotropic dehydration (butyl acetate entrainer) as the usual recovery but
give no number we use.

## D-001 Route and boundary (2026-10-28)
Decision: the ketene route as the issue prescribes: acetic acid cracked to ketene and water
(fired tubular furnace, vacuum, triethyl phosphate), NH3 neutralisation, condensation of water
and unconverted acid as dilute acid, reactive absorption of ketene in acetic acid
(CH2CO + CH3COOH -> Ac2O), two-column distillation, recovery of the dilute acid and recycle.
Boundary: glacial acetic acid, TEP, ammonia, natural gas and air in; anhydride, residue,
wastewater, flue gas, utilities out. The absorber vent gas is burned in the cracking furnace
inside the boundary (SRC-2 names this use), so its CO2 is a foreground emission.
Rejected: methyl acetate carbonylation (Tennessee Eastman / BP route; the other industrial
route, issue #131 asks not to blend their data); the acetaldehyde oxidation route (obsolete).
Not compared quantitatively in this run: no route-evidence file (`process/reaction-evidence.yaml`)
yet; the route is fixed by the issue.

## D-002 Capacity and product (2026-10-28)
Decision: 50 kt/a acetic anhydride at 8000 h/a (6250 kg/h), 99.5 wt% anhydride with 0.5 wt%
acetic acid. ASSUMED: a mid-size single-train plant, chosen, not a client or published plant
figure; the product purity is a margin above a common commercial minimum, to be fixed against a
customer specification (I-01).

## D-003 Acetic acid as a boundary feed (2026-10-28)
Decision: fresh glacial acid at 303 K / 300 kPa(a), taken as pure. It is usually made by
methanol carbonylation; the library has methanol-1 (methanol) but no acetic acid process, so the
LCI gives a gap with that description. ASSUMED purity (water, formic and propionic acid traces
not modelled).

## D-004 Units and recycles (2026-10-28)
Decision: two recycles: recovered glacial acid (S21) to the cracker feed and the acid column
distillate (S25) to the absorbers. Fresh acid is split (SP101) between the cracker and the
absorbers: the absorbers take the acid consumed by ketene absorption plus the acid leaving with
the product. Vent to the furnace burners; no flare in the normal balance.

## D-005 Cracking model (2026-10-28)
Decision: conversion reactor R101 with the SRC-1 example values: acetic acid conversion 0.84
per pass, 0.92 kmol ketene per kmol acid converted, at 700 C and 36 kPa(a) at the coil outlet.
The remaining 8 % of the converted acid is split equally (ASSUMED) between acid decomposition
(CH3COOH -> CH4 + CO2) and ketene decomposition (2 CH2CO -> C2H4 + 2 CO); SRC-1 names these
products without amounts. The ketene yield is taken as the net yield after the condensers
(SRC-1 measures ketene and condensate after them), so the back-reaction of ketene with water in
the condensers is inside the 92 %; the model's dilute acid (39.5 wt% acid) is close to SRC-1's
38 wt%. TEP 0.2 wt% of the cracker feed (SRC-2 range 0.1-0.5 wt%); NH3 2 mol per mol P
(ASSUMED: enough for diammonium phosphate). TEP and NH3 are carried as inert components to the
dilute acid and the wastewater: in reality TEP decomposes to phosphoric acid (and ethylene) and
forms ammonium phosphates; the lumping keeps the element balance and is a simplification. Coke
and allene are not modelled (coke burnt off in decoking, LCI cutoff).
Rejected: a kinetic model from SRC-3 (abstract only, constants not read) and any invented rate
law. Sourced conversion model at the concept stage, not kinetics.

## D-006 Independent balance and condensation (2026-10-28)
Decision: `scripts/ac2o_balance.py` (run with `cheme run`) solves the balance from the product
backwards and gives every value cheme cannot calculate: feed flows, separator, column and
acid-recovery outlets, recycle streams, temperatures, pressures and duties, entered as ASSUMED
with the script as source. Enthalpies on formation basis: ideal gas (materials.yaml data) for
vapours, liquid formation enthalpies (CRC via `chemicals`) plus `thermo` liquid heat capacities
for liquids; acetic acid vaporisation in E-101 at the latent heat to the associated vapour
(about 24 kJ/mol), the dimer dissociation (to the ideal monomer gas) falling to the furnace. The
condenser train (E-102) cools the cracked gas to -5 C at 27 kPa(a) (SRC-1); the ketene gas is
taken dry (ASSUMED). The brine share is the sensible cooling below 35 C plus 20 % of the
condensation heat: an estimate from the water and acid partial pressures at 35 C and 30 kPa(a)
(about 18 % of the gas is still condensable vapour there). cheme recalculates the reactors,
mixers and pass-through steps from the same specifications and agrees with the script
(e.g. flue gas CO2 0.105929 mole fraction in both).

## D-007 Absorption (2026-10-28)
Decision: T-301 as a conversion reactor: 99 % of the ketene is absorbed (1 % leaves with the
vent, within SRC-2's 0.1-10 wt% of the vent), 99 % of the absorbed ketene forms anhydride and 1 %
heavy ends, lumped as dehydroacetic acid (4 CH2CO -> C8H8O4): all ASSUMED. Crude 88 wt%
anhydride (SRC-2: >= 85 wt% preferred), 45 C and 25-27 kPa(a) (SRC-2: 35-55 C). Acid and
anhydride vapour in the vent is neglected (ASSUMED; SRC-2 reports 10-60 wt% in an unscrubbed
vent, so a scrubber or the liquid-ring seal fluid must return it; I-03). Circulation pumps:
100 kg liquid per kg ketene (SRC-2), 300 kPa rise, efficiency 0.65. Vent liquid-ring pump
25 -> 120 kPa(a), isothermal efficiency 0.35 (ASSUMED). The heat of absorption follows from
formation enthalpies (about -92 kJ/mol on the liquid basis); SRC-2 states -63 kJ/mol: a
conflict left open (I-04); the cooling-water duty is the larger, conservative value.

## D-008 Distillation (2026-10-28)
Decision: C-201 takes acetic acid overhead (98 wt%, recycled to the absorbers) at reflux ratio
3; C-202 takes the product overhead at reflux ratio 1 and leaves a residue of 50 wt% anhydride
and 50 wt% heavy ends. Both atmospheric, reboilers on MP steam. Duties from (R+1)·D·latent heat
and the enthalpy balance of each column, product cooled to 40 C in the condenser duty. All
ASSUMED; no stage design (relative volatility of acid/anhydride and anhydride stability under
vacuum to be checked at basic engineering).

## D-009 Dilute acid recovery (2026-10-28)
Decision: one lumped step C-401 for solvent extraction plus azeotropic dehydration: 99 % of the
dilute acid's acid recovered at 99.8 wt% and recycled, the rest to the wastewater with the
catalyst residues. LP steam 3.0 MJ per kg water in the dilute acid (ASSUMED: of the order of
water's latent heat plus entrainer evaporation; extraction first lowers it). Solvent make-up is
a cutoff of about 1 kg/h (ASSUMED). This is the largest unsourced energy number of the plant
(I-02).

## D-010 Furnace firebox (2026-10-28)
Decision: firebox H101 burns natural gas (taken as methane) and the vent gas completely with
15 % excess air; stack 443 K, radiation loss 2 % of the fired LHV (ASSUMED). The natural gas
follows from the coil duty: about 30 % of the fired heat comes from the vent gas; LHV
efficiency 0.915 results (high for a fired heater; a hotter stack raises the gas demand, I-05).
NOx, CO and unburnt hydrocarbons are not estimated (I-05).

## D-011 Utilities (2026-10-28)
Decision: cooling water 25/35 C, brine -10 C (SRC-1), LP steam 450 kPa(a), MP steam
1500 kPa(a), electric drives; ASSUMED levels. Small pumps (feed, reflux, distillate, transfer;
about 25 kW together) are not in the flowsheet's power feed: an LCI cutoff.

## D-012 Core findings met in this run (2026-10-28)
- `cheme validate` (0.8.0) `_reactor_rules` rebinds the name `declared` (the reaction table) to
  a list inside the selectivity check, so every reactor step after the first step with a
  `selectivity:` loses its reactions ("the key KET is a reactant of none of its reactions").
  Worked around: T301 gives per-reaction conversions (0.9801 and 0.0099 of the inlet ketene),
  which give the same extents as the intended selectivity. To report to core.
- `cheme process propagate` writes zero mole fractions for every template component of a
  reactor or mixer outlet, so the outlet template must hold all inlet components (flue_gas holds
  the unburnt fuel components at 0).
- The block balance of CRK reports extents fitted over all seven reactions of its steps (a
  non-unique fit, e.g. DECARB 0); the step extents are the meaningful ones.
- No property package covers acetic acid, ketene, anhydride or water (core #315), so
  `cheme process energy` finds no balance evaluable and `props --fill`/`simulate` cannot run;
  energy closure is in the script only (gated step).
- `cheme assess lca --write` writes a total of the characterised foreground only (the direct
  CO2) beside 11 gaps; process.yaml keeps `lca.source: none` so the catalog does not publish it
  as a footprint (as hda-1, D-011 there).

## D-013 Lists (2026-10-28)
Decision: equipment list of the PFD items (11) and one line per physical PFD stream (23).
Vacuum equipment full vacuum / 3.5 barg; design temperature + 25 K; SS316L for acid, ketene
and anhydride service; nickel-free alloy for the cracking coil (SRC-1). Line DN from velocity
(vacuum gas 20 m/s, cracked gas 30 m/s, liquids 1.5 m/s). All ASSUMED.

## D-014 Preliminary LCI: gate-to-gate foreground, every background a gap (2026-10-28)
Decision: `lca/lca.yaml` with functional unit 1 kg acetic anhydride (product AC2O), design
case; every foreground exchange from the flowsheet. No background linked: every feed, utility
and waste treatment is `missing:` with the activity it should connect to (11 gaps); no per-process
mapping overrides (`lca/mappings.yaml` lists the candidates). Single product, no allocation
(the residue and wastewater are wastes). Direct CO2 of the firebox is a foreground emission,
origin fossil (ASSUMED: acetic acid from natural-gas methanol; bio-based acid would make the
vent carbon biogenic). Furnace pollutants and fugitive emissions are declared exclusions, not
zeros. No construction inventory.
Library LCI build (`uv run scripts/build_lci.py --library . --out build/lci-check --strict`,
2026-10-28): no error for this process, 10 gaps reported (feed:AA, TEP, NH3, NG, LPS, MPS,
product:RESIDUE, BRINE, emission:C2H4, KET); its only warning is the scratch environment's
missing core extra (cut-off check), shared by every process. Two things were changed for it:
steam has no `inventory_key` in process.yaml (the slug `steam` is per kg, the inventory per kWh:
a unit error otherwise), and the zero-amount CO, C2H4 and ketene emissions are elementary, not
`free` (a free emission must be curated in the shared `pass_through`). product:CW and product:WW
are linked by the shared vocabulary through their registry slugs (cooling-water, wastewater) in
the Atlas build, although `lca/lca.yaml` keeps them `missing:`.

## Open inputs and issues
- I-01 Product specification (purity, colour, permanganate time) and capacity: owner input.
- I-02 Dilute acid recovery: extraction solvent, entrainer, stages and steam demand (D-009) are
  unsourced; the 3.0 MJ/kg water is the largest assumed energy number.
- I-03 Absorber vent acid/anhydride vapour and the vent scrubbing (D-007).
- I-04 Heat of absorption: formation-enthalpy value (-92 kJ/mol) against SRC-2's -63 kJ/mol.
- I-05 Furnace efficiency, stack temperature and combustion emission factors (NOx, CO) from a
  cited guidebook (D-010).
- I-06 Fugitive emissions need P&ID component counts.
- I-07 Cracking by-product split, coke yield and the yield/pressure trade-off (SRC-1, SRC-3)
  need a reaction-evidence file (`process/reaction-evidence.yaml`) before a predictive model.
- Registry entries missing in `chemicals/chemicals.yaml` (consolidated PR): acetic-acid,
  acetic-anhydride, ammonia, triethyl-phosphate, carbon-monoxide, ethylene, ketene; and in
  `lci/mappings.yaml`: acetic acid, triethyl phosphate, refrigeration at -10 C (brine),
  hazardous liquid organic waste incineration. A benchmark entry for the family `oxygenates`
  (`benchmarks/`) is not written (outside this folder).
