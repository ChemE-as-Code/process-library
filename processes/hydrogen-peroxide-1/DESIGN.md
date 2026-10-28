# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Hydrogen peroxide by the anthraquinone autoxidation (AO) process, issue
ChemE-as-Code/process-library#170. Concept stage. Started 2026-10-28 from library commit
11d50ef, cheme-as-code 0.8.0 (pyDEXPI 2.1.0).

"BREF" below is the EU Best Available Techniques Reference Document for the Production of Large
Volume Organic Chemicals (Falcke et al. 2017, JRC, EUR 28882 EN, doi:10.2760/77304), chapter 12
"Hydrogen peroxide" (printed pages 547-583). It was read in full for this design (downloaded
PDF, text extracted locally, not stored). Every number taken from it is cited by section or
table and restated in our own words; no table is reproduced. EU publications may be reused
with attribution (Commission Decision 2011/833/EU).

## Source register

| source | locator | read | used for |
|---|---|---|---|
| LVOC BREF 2017, doi:10.2760/77304 | 12.2.2.1-12.2.2.6 (process steps), 12.3.1 (air), 12.3.2 + Table 12.3 (water), Table 12.4 (inputs), 12.3.4 + Table 12.5 (energy), 12.3.5 (water use), Table 12.6 (wastes), Tables 12.2, 12.7, 12.8 (VOC) | full text of ch. 12 | route, operating windows, every consumption and emission range below |
| NIST Chemistry WebBook (SRD 69) | standard enthalpies of formation of H2O2(l) -187.78 kJ/mol and H2O(l) -285.83 kJ/mol | values known, standard reference | heats of reaction HYD and HPD (D-005) |
| PubChem | CID 784 (H2O2), 6772 (2-ethylanthraquinone), 617218 (2-ethylanthrahydroquinone), 7247 (1,2,4-trimethylbenzene), 7957 (diisobutylcarbinol) | identity lookups | materials.yaml identities |
| Ullmann's, Hydrogen Peroxide, doi:10.1002/14356007.a13_443.pub3 | - | not read (licensed) | lead only |
| Campos-Martin et al. 2006, doi:10.1002/anie.200503779 | - | not read (licensed) | lead only (cited by the BREF as Fierro et al. 2006) |

No published plant "answer" or benchmark case was searched for or used.

## D-001 Route and boundary (2026-10-28)
Decision: Anthraquinone autoxidation process, the only industrial route (BREF 12.1, 12.2.1):
hydrogenation of an alkylanthraquinone working solution on Pd, autoxidation with air, water
extraction, crude purification, vacuum concentration, working-solution (WS) drying and
regeneration. Boundary: from hydrogen, air, demineralised water, WS make-ups and the reversion
agent at the battery limit to 50 wt% H2O2 at the product storage inlet. Hydrogen is a boundary
feed: library process `hydrogen-1` (or by-product H2 of `chlor-alkali-1`) can supply it; the
link is noted in `process.yaml` and `lca/lca.yaml`. Outside: product storage and
stabilisation, H2 supply and compression, cooling tower, steam boiler, demineralisation,
biological waste water treatment, off-site catalyst regeneration.
Reason: the case notes of the issue; the BREF names the AO process as the sole industrial route.
Rejected: direct synthesis from H2 and O2 and electrochemical routes (BREF 12.5, emerging, no
industrial scale); oxygen instead of air for the oxidation (BREF 12.4.1.1.5: a BAT option, but
needs an oxygen supply; a later case).
Assumptions: none beyond the boundary.

## D-002 Capacity and product (2026-10-28)
Decision: 50 kt/a H2O2 (100 %), 8000 h/a, i.e. 6250 kg/h H2O2 as 12 500 kg/h of a 50 wt%
solution; stabilisers (BREF Table 12.4 lists them without a quantity) and pH adjustment are not
modelled. ASSUMED.
Reason: a mid-size single train; the BREF lists European plants (Table 12.1) whose capacities
span this size. 50 wt% is the grade the BREF energy data refer to (Table 12.5 note 1) and lies
in the 50-70 wt% range of the issue. 70 wt% is a later case (more concentration energy).
Rejected: 70 wt% as the base (energy data not referenced to it).

## D-003 Hydrogenation section (2026-10-28)
Decision: fixed-bed Pd-on-alumina hydrogenator with co-current H2 and WS and a cooled WS
recycle, 333 K, 400 kPa(a), no H2 recycle compressor; gas separator with a vent to atmosphere;
safety filter before the oxidiser. H2 at the battery limit pure, 500 kPa(a), 313 K. ASSUMED.
Reason: BREF 12.2.2.2: pressures up to 5 bar, temperature below 100 C (50-70 C in one cited
design), fixed beds give almost complete H2 conversion and need no catalyst filtration; the
safety filter keeps Pd out of the oxidiser (12.2.2.3). Vent to atmosphere as most plants do
(12.3.1.2).
Rejected: slurry (Pd black or supported) reactors with catalyst filtration; H2 recycle.

## D-004 Working solution (2026-10-28)
Decision: 2-ethylanthraquinone (EAQ) 14.0 wt% (about 130 kg/m3) in a 60:40 (mass) mixture of
1,2,4-trimethylbenzene (TMB, standing for the C9-C11 aromatic cut) and diisobutylcarbinol
(DIBC), 0.15 wt% water, density 930 kg/m3. 'Anthra' system: tetrahydroanthraquinone, epoxide,
anthrones and other degradation products are not modelled; the degraded quinone is carried as
EAQ in the reversion purge. ASSUMED.
Reason: the BREF names EAQ as a common working compound and both solvent types as used
(12.2.2.1, 12.3.3 a); the solvent mixture is always aromatic + polar (12.2.2.1). The
concentration and solvent ratio are our choices (no open source read gives them); with 45 %
conversion they give a WS productivity of 8.2 kg H2O2/m3.
Rejected: tris(2-ethylhexyl) phosphate or tetrabutylurea as polar solvent (more elements for the
same purpose); an 'all-tetra' system (needs tetra and epoxide chemistry without data).

## D-005 Reaction model (2026-10-28)
Decision: conversion reactors (process/reactions.yaml), calculated by cheme: HYD
(EAQ + H2 -> EAHQ, 45 % of EAQ per pass), HPD (residual H2O2 in the recycled WS + H2 -> 2 H2O,
complete, on the Pd catalyst) and OXD (EAHQ + O2 -> EAQ + H2O2, complete). 1 % of the H2 feed
leaves unreacted with the vent. Heats of reaction: OXD -77.5 kJ/mol (BREF 12.3.4 d: 75-80
kJ/mol, midpoint); HYD -110.3 kJ/mol derived by Hess's law from the overall reaction
H2 + O2 -> H2O2(l) (-187.78 kJ/mol, NIST) minus OXD; HPD -383.88 kJ/mol from NIST formation
enthalpies. No kinetics: none are used, so no reactor size is given. ASSUMED conversions.
Reason: BREF 12.2.2.2 keeps the hydrogenation below 60 % of the total quinone to limit
by-products; autoxidation is fast and uncatalysed (12.2.2.3); the BREF reports a 99.99 % molar
selectivity on the quinone (12.3.6 b), so the quinone loss is a make-up, not a side reaction.
Result: H2 63.5 kg/t H2O2 against 59.3 kg/t stoichiometric, inside the BREF 60-70 kg/t
(Table 12.4). H2O2 decomposition in the oxidiser, extractor and concentrator is not modelled
(open input; it would raise the H2 and air use by the same fraction).
Rejected: equilibrium or kinetic reactor models (no open kinetic data read; the issue forbids
invented kinetics).

## D-006 Balance method and gated steps (2026-10-28)
Decision: the separator outlets and all duties come from `scripts/hp_balance.py` (standard
library, run by `cheme run scripts/hp_balance.py`), entered in `process/flowsheet.yaml` as
ASSUMED; cheme calculates the reactor outlets, mixers and pass-through steps (`cheme process
propagate --fill`) and checks the mass, component and element balances of every block and step.
Gated steps (core): (1) energy balances: `cheme process energy` reports every block
not-evaluable, since no benchmarked property package covers the WS, aqueous H2O2 or the
quinones (only the air streams S08-S10 are inside air-pr-chemsep) - core #315; (2) the
extraction C-301 is a specified split: `cheme process extract` is qualified only for the
water/1-propanol/n-butyl acetate system, and EAQ/TMB/DIBC/H2O2/water has no sourced NRTL set
here - core #369 (an unqualified calculation would also need parameters we do not have);
(3) `cheme process build` of cheme 0.8.0 fails with a TypeError in `step_method` for a step of
class `Pumping` (its `method` field is an optional enum); P-101 uses `TransportingFluids`
instead - to report to core.
Reason: a balanced, traceable concept flowsheet without claiming predictive simulation.

## D-007 Oxidation and air (2026-10-28)
Decision: dry air (CO2 and traces counted as N2), 30 % O2 excess, one-stage compression to
450 kPa(a) at isentropic efficiency 0.80, aftercooler to 313 K, co-current bubble-column
oxidiser at 328 K and 350 kPa(a); off-gas water and solvent mole fractions at the oxidiser
outlet 1.8 %, 0.20 % (TMB) and 0.01 % (DIBC), estimated from vapour pressures (Raoult), ASSUMED.
Reason: BREF 12.2.2.3: 20-40 % excess, 40-70 C, atmospheric to 10 bar, bubble columns. Result:
4215 Nm3 air/t, inside the BREF 3300-4600 Nm3/t (Table 12.4 note 1); off-gas 22 500 Nm3/h,
inside the range of plants in Table 12.8; air compression 1.08 GJ/t electric, below the 1.4 GJ/t
of Table 12.5 (lower pressure ratio, no expander).
Rejected: an off-gas expander (BREF 12.3.4 d, recovers 75-80 % of the extra compression work at
higher pressure): a basic-engineering option.

## D-008 Extraction, purification and WS drying (2026-10-28)
Decision: sieve-tray extraction with demineralised water plus the concentrator distillate:
97 % of the H2O2 to a 40 wt% crude with 1500 mg/kg DIBC and 100 mg/kg TMB dissolved; raffinate
0.30 wt% water; solvent wash removes 95 % of the crude's organics back to the WS tank; vacuum
dryer removes the raffinate water down to the WS specification, the removed water carries
0.5 wt% H2O2. ASSUMED.
Reason: BREF 12.2.2.4 (crude 20-50 wt%, solvent washing, coalescers, WS drying) and 12.3.1.5.
Unextracted H2O2 returns to the hydrogenator and is destroyed there (D-005). Result:
demineralised water 1.19 t/t, inside the BREF 1-2 m3/t (Table 12.4, 12.3.5).
Open: the extraction recovery and the crude's organics need an equilibrium-stage calculation
with sourced parameters (core #369).

## D-009 Off-gas and vent treatment (2026-10-28)
Decision: off-gas condenser to 308 K and knock-out (condensate back to the WS tank), then
activated carbon to 20 mg C/Nm3 (expressed as TMB), steam regeneration at 5 kg steam/kg solvent;
desorbed solvent back to the WS tank, aqueous condensate to waste water. Hydrogenation vent
VOC 100 g C/h. ASSUMED.
Reason: BREF 12.2.2.3 and 12.3.1.1 (condenser + adsorber, regenerative), Table 12.8 (plant
outlet averages of a few to about 65 mg C/Nm3), 12.3.2 c (4-6 kg steam/kg solvent), Table 12.2
(vent VOC loads up to about 200-330 g C/h). Latent heats for the condenser duty: water 2400,
TMB 398, DIBC 380 kJ/kg (rounded, ASSUMED).

## D-010 Concentration and utilities (2026-10-28)
Decision: vacuum column at 10-12 kPa(a), feed 40 wt%, bottoms product 50 wt% at 333 K, reflux
ratio 0.3, distillate 0.05 wt% H2O2 recycled to the extraction; reboiler on LP steam 350 kPa(a)
(saturated, 411 K), no vapour recompression; product cooled to 303 K. Cooling water 25/35 C.
Electric drives: WS pumps (764 m3/h, 800 kPa rise, efficiency 0.70), 10 kWh/t for the
extraction water, crude and product pumps, 5 kWh/t for the vacuum pump; 0.1 t/t direct steam
for the WS dryer ejector. ASSUMED.
Reason: BREF 12.2.2.6 (vacuum distillation, distillate recycled), 12.3.4. Result: reboiler
1.71 GJ/t, above the BREF net distillation range 0.3-1.5 GJ/t (Table 12.5), because no heat
recovery is assumed; total energy about 3.6 GJ/t (electricity 355 kWh/t, steam about 2.3 GJ/t),
inside the BREF 2.9-5.7 GJ/t net (Table 12.5). Vapour recompression is the main energy option
(BREF 12.4.3.1) for basic engineering.

## D-011 Make-ups, reversion, effluents and consumables (2026-10-28)
Decision: reversion on activated alumina (no caustic reversion, so no caustic tar): 6 kg/t
alumina, leaving as 9 kg/t spent agent with 1.0 kg/t degraded quinone (carried as EAQ) and
2.0 kg/t solvent; quinone make-up 1.0 kg/t; solvent make-up 2.5 kg/t (what leaves: spent
alumina, waste water, off-gas, vent, product). Dissolved organics in aqueous effluents at
600 mg/kg DIBC and 57 mg/kg TMB (approximate water solubilities, ASSUMED). Outside the
flowsheet (consumables in lca/lca.yaml): Pd catalyst losses, nitric acid, sodium hydroxide,
activated carbon, ion-exchange resin, product stabilisers.
Reason: BREF Table 12.4 (quinone 0.5-2.5, data collection 0.7-1.6 kg/t; solvents 2-5 kg/t;
reversion agent 4-20 kg/t; NaOH 1.5-4 kg/t; nitric acid 2.5-7 kg/t), Table 12.6 (spent
reversion agent typically 7-10 kg/t; spent adsorbent 0.01-0.34 kg/t; resins 0.005-0.027 kg/t),
12.3.3 b (Pd losses 0.1-0.3 g/t for fixed beds), 12.3.2 b (TOC 0.01-0.8 kg/t with solids
reversion). Result: waste water 0.41 t/t with 0.15 kg TOC/t, inside the BREF ranges (Table
12.3: 0.1-3 m3/t; 12.3.2 b).
Open: fugitive and storage VOC losses (BREF 12.3.1.6-7: possibly large, no number) are not in
the flowsheet; the solvent balance closes on the modelled outlets only.

## D-012 Lists (2026-10-28)
Decision: equipment and line lists hold the PFD items only; design pressure the highest
operating pressure + 10 % (at least + 2 bar), design temperature + 25 K; line sizes from
velocity (liquid 2 m/s, gas 15-20 m/s). Materials: stainless steel or aluminium in H2O2
service, carbon steel in WS-only service, ASSUMED (open input for basic engineering). No P&ID.

## D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg of the 50 wt% product (PROD) at the gate (= 0.5 kg H2O2 100 %;
per kg H2O2 100 % multiply by 2). Every foreground exchange comes from the flowsheet streams;
consumables outside the flowsheet are ASSUMED from the BREF ranges (D-011). All backgrounds are
left unmapped (`missing:` with the activity each should connect to): the result is an inventory
with gaps, not an impact. Ambient air and atmospheric N2/O2/Ar/H2O returned are free; the
off-gas and vent are emissions to air (VOC as TMB and DIBC, H2), the aqueous effluent goes to
treatment outside the boundary. See lca/lca.yaml.
Result (`cheme assess lca --inventory --write`, `--coverage`, `--balance`), per kg of 50 wt%
product: H2 0.0318 kg (S01), demineralised water 0.596 kg (S29), direct LP steam 0.117 kg
(S17+S31), quinone 0.0005 kg, solvents 0.00125 kg, alumina 0.003 kg, electricity 0.177 kWh
(Q01-Q04), LP steam heat 0.237 kWh (Q05), heat to cooling water 1.23 kWh (Q06-Q11); outputs
off-gas 2.26 kg (with 4.9e-5 kg VOC as TMB), vent H2 3.2e-4 kg, waste water 0.205 kg, spent
alumina 0.0045 kg; consumables (ASSUMED, BREF ranges) HNO3 0.002, NaOH 0.001, activated carbon
5e-5, resin 7.5e-6, Pd 1e-7 kg. The dataset closes in mass (43 433 kg/h in and out) and in every
element of the flowsheet exchanges (Al, Ar, C, H, N, O within 0.01 %; consumables have no
composition, so cheme reports the element balance "not assessable" for them). Classification:
partial (23 gaps, every background missing); DQR 2.33. The library LCI build
(`scripts/build_lci.py --strict`) reports 15 gaps for this process and no error; its only
remaining warning (cut-off criteria not checked) comes from the missing core extra in the
library environment and appears for every process.
Overrides (lca/mappings.yaml, ADR 0022): feed:LPS counted as heat (kWh, `steam-heat`);
feed:H2 and feed:STEAMD `atlas: false` until a person chooses the supplier (the build would
otherwise pick chlor-alkali-1 for H2 and ammonia-1 for steam by itself).
Missing in the shared registry (`chemicals/chemicals.yaml`, for the consolidated PR):
hydrogen-peroxide (with a 50 wt% grade), 2-ethylanthraquinone, the C9 aromatic solvent
(trimethylbenzene), diisobutylcarbinol, activated alumina, demineralised water (grade of
water), nitric acid, sodium hydroxide, activated carbon, ion-exchange resin, palladium catalyst;
biosphere identities for 1,2,4-trimethylbenzene and diisobutylcarbinol emissions to air, and
for hydrogen to air (not in core's crosswalk).
