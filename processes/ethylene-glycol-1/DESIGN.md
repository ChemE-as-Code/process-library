# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Case study for issue ChemE-as-Code/process-library#172. Started 2026-10-28 from library commit
11d50ef with cheme-as-code 0.8.0 (pyDEXPI 2.1.0). Stage: concept (design basis, balanced
BFD/PFD, preliminary gate-to-gate LCI). Out of scope: P&IDs, layout, HAZOP, TEA, datasheets.

## Source register

| id | source | locator | read status | reuse | used for |
|---|---|---|---|---|---|
| BREF | European Commission JRC (2017) *BAT Reference Document for the Production of Large Volume Organic Chemicals*, JRC109279, EUR 28882 EN. https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/JRC109279_LVOC_Bref.pdf | chapter 7, sections 7.2.1-7.3.6, printed pp. 361-377 (tables 7.2-7.6) | read in full for chapter 7 sections 7.2-7.3 in this run; 7.4 skimmed (no figures for energy) | EU Commission reuse policy (Decision 2011/833/EU): reuse with acknowledgement; only facts and ranges used, in our own words | route, operating windows, selectivity, purge, emissions, consumption ranges, residues (D-001, D-004 to D-006, D-010) |
| SHEH | Shehata et al. (2024) *A comparative study of mono ethylene glycol economic production via different techniques*, Sci. Rep. (open access, CC BY 4.0), doi:10.1038/s41598-024-77713-y, PMC11570614 | "Direct hydration" section, Tables 1, 3, 8 | read (first 100k characters) | CC BY 4.0; facts only | cross-check only: water:EO 10-25 mol/mol range named in its introduction, vacuum MEG column; its duties are internally inconsistent (feed heater 4.4 vs 44.5 MW between text and Table 8), so no value is taken from it |
| ASU | the library's asu-1 (processes/asu-1/process/design-basis.yaml, product GOXP) | products, GOX purity | read | own library | oxygen feed purity and link (D-003) |
| SHELL | Shell, OMEGA process web page (vendor) | product claims | search snippet only | vendor claim | cross-check of the MEG yield per t ethylene only (D-006) |
| ULL | Rebsdat, S.; Mayer, D., *Ethylene Glycol*, Ullmann's Encyclopedia, doi:10.1002/14356007.a10_101 | - | not read (licensed) | - | route lead named in the issue; no value used |

Not found open in this run: sourced rate constants of EO hydration (the consecutive-reaction
papers found, e.g. Melhem et al. on EO-water-glycol kinetics and a 2004 JKAU paper on the
analytical product distribution, were not reachable), open utility consumptions per tonne of
MEG, and a licensor heat and material balance. Those values are ASSUMED below.

## D-001 Route and boundary (2026-10-28)
Decision: Ethylene oxide by direct oxidation of ethylene with pipeline oxygen over a silver
catalyst, methane as ballast, EO absorbed in water and stripped, CO2 removed from a slip stream
by hot potassium carbonate, an inerts purge to fuel gas; glycols by thermal (uncatalysed)
hydration of the aqueous EO with excess water, water removal by multi-effect evaporation and a
vacuum drying column, MEG, DEG and TEG by vacuum distillation. A **glycols-only** plant: no
high-purity EO product, no EO storage. Boundary: ethylene, oxygen, methane and demineralised
water in; MEG, DEG, TEG, heavy glycols residue, purge gas, CO2 vent and water bleed out;
utilities MP steam, power and cooling water.
Reason: BREF 7.2.1 names direct O2 oxidation as the only EO route in EU use (air-based plants
superseded, chlorohydrin abandoned) and thermal hydrolysis as the only EG route in the EU in
2015; it lists glycols-only as one of three EO/EG configurations (7.2.2). Glycols-only keeps
the scope of #172 (ethylene glycol) and avoids EO purification and storage.
Rejected: ethylene carbonate route (Shell OMEGA and similar; BREF 7.2.1.2.2: higher MEG
selectivity, less water, used outside the EU): a distinct technology for a later case;
dimethyl oxalate (syngas) route (BREF 7.5.2): different feedstock; air-based EO: superseded;
EO as a purchased feed: the issue asks for the integrated route.
Assumptions: the organochlorine moderator, acetaldehyde/formaldehyde and organic acids are not
modelled (traces, D-006); the glycol bleed and salt purge of the EO absorbent are not modelled.

## D-002 Capacity, operating hours and product grade (2026-10-28)
Decision: 50 t/h MEG at the MEG column top (1200 t/d, 400 kt/a at 8000 h/a), ASSUMED. MEG
99.90 wt%, DEG 0.06 wt%, water 0.04 wt% (ASSUMED design grade aiming at fibre grade). Generic
site, country not chosen.
Reason: a per-unit-product normalisation for the inventory (issue #172 notes), in the size
range of world-scale EO/EG units; the inventory per kg does not depend on it in this linear
model.
Rejected: a published plant capacity: none traceable in open sources read.

## D-003 Feeds and library links (2026-10-28)
Decision: oxygen is the library's asu-1 GOX (99.5 mol% O2, the rest counted as argon, delivered
at 2400 kPa(a) after letdown from 30 barg); ethylene polymer grade 99.95 mol% with 0.05 % ethane
(ASSUMED; sulfur and acetylene below catalyst limits, not modelled), delivered at 2400 kPa(a);
methane ballast as pure CH4 (natural gas impurities neglected); demineralised make-up water.
Reason: issue case notes: ethylene and oxygen are boundary feeds; asu-1 makes oxygen at that
purity. No olefins (steam cracker) process exists in the library yet: ethylene is a plain
boundary feed. BREF 7.2.2.1 requires very pure ethylene and oxygen.

## D-004 EO section: reactor, absorption, CO2 removal, purge (2026-10-28)
Decision (all ASSUMED inside the cited ranges):
- reactor inlet 30 mol% C2H4, 8 mol% O2, 1 mol% CO2, methane the balance (with the
  accumulated argon, 7.9 mol%, and ethane, 0.9 mol%); 2200 kPa(a) inlet, outlet 523 K
  (BREF 7.2.1.1.1: 200-300 C, 15-25 bar);
- per-pass ethylene conversion 9 % and EO selectivity 85 mol% (BREF 7.2.1.1.1: 8-10 % and
  75-90 % for the O2 process); in the model each reaction converts a fixed fraction of the inlet
  ethylene (EOX 0.0765, COMB 0.0135, process/reactions.yaml), the rest of the ethylene recycles;
- EO fully absorbed in water (rich absorbent 3 wt% EO), dissolved CO2, C2H4 and CH4 (0.03,
  0.015, 0.008 kmol per kmol EO) stripped and returned to the loop; the stripper overhead
  (85 wt% EO) goes to the glycol reactor after the light-gas stripper;
- inerts purge 0.15 % of the recycle gas after the compressor (BREF 7.2.2.1: 0.1-0.2 %), to the
  fuel gas header;
- CO2 removal: 49.6 % of the recycle gas through hot potassium carbonate, 90 % of its CO2
  absorbed (BREF 7.2.2.3 describes the absorption/atmospheric stripping); the regenerator
  overhead is vented without oxidation in the base case (BREF 7.3.1.2 allows thermal/catalytic
  oxidation or sale);
- loop water: absorber off-gas saturated at 308 K, 2000 kPa(a) (0.28 mol%).
Reason: the BREF ranges are the open, sourced basis; the inlet composition is a common
methane-ballast operating point consistent with the BREF statement that methane allows higher
oxygen levels (7.2.2.1); not a licensor value.
Rejected: nitrogen ballast (BREF: methane used by all EU sites).
Check against the BREF (Table 7.6, 7.3.6.1): ethylene 761 kg/t EO (range 700-850), oxygen
755 kg/t EO (600-1100), CO2 351 kg/t EO (0.22-0.86 t/t for 90-70 % selectivity).

## D-005 Glycol section: reaction, evaporation, purification (2026-10-28)
Decision (ASSUMED):
- water:EO 20 mol/mol at the glycol reactor inlet, full EO conversion, adiabatic pipe reactor
  at 3000 kPa(a), 423 K inlet, about 478 K outlet (BREF 7.2.2.5: 150-250 C, 10-40 barg, full
  conversion, no catalyst; SHEH names 10-25 mol/mol);
- product split from a consecutive-reaction model (EO + water -> MEG, EO + MEG -> DEG, EO + DEG
  -> TEG, EO + TEG -> heavies, second order, integrated to full EO conversion in
  scripts/eg_balance.py) with the rate of EO with any glycol taken as 2.0 times its rate with
  water per mole (ASSUMED, not from a source read in this run; to be replaced by sourced
  kinetics). Result: 92.0 wt% MEG, 7.65 wt% DEG, 0.35 wt% TEG in the glycols, at the top of the
  BREF range for commercial crude glycols (7.2.1.2.1 and 7.2.2.5: 75-92 wt% MEG);
  selectivities per mol EO: MEG 0.9067, DEG 0.0444, TEG 0.00145, heavies 0.000036;
- four-effect evaporator to 15 wt% water, vacuum drying column; 0.1 wt% MEG carried into the
  recycle water; 0.5 % of the recycle water bled to waste water (aldehyde purge, BREF 7.2.2.5,
  7.3.2.2);
- MEG column bottoms 0.2 wt% MEG; DEG column loses 0.05 % of its DEG to the bottoms, DEG product
  0.2 wt% TEG; TEG column loses 5 % of its TEG to the heavies, TEG product 0.5 wt% heavies.
Result: heavy glycols residue 15 kg/h (0.37 kg/t EO), below the BREF range of 1.4-21 kg/t EO
(7.3.6.4), which also counts the EO plant's glycol purges that this model leaves out (D-001):
the residue is a lower bound.

## D-006 Balance method, emissions and a core issue met (2026-10-28)
Decision: an independent sequential balance, `python3 scripts/eg_balance.py build`, solves
the recycle loop (fixed-point iteration, the inerts converge slowly with a 0.15 % purge), the
glycol water recycle and the purification, scales linearly to 50 t/h MEG and writes the stream
table that process/flowsheet.yaml carries with provenance `assumed`. Overall closure 0.04 kg/h
of 71.3 t/h. cheme validates every block and step balance (tolerance 1 kg/h + 0.5 %) and the
reactors by elements and extents (cheme process streams: R-101 extents EOX 887.7, COMB
156.7 kmol/h; R-401 HYD1 845.7, HYD2 40.7, HYD3 1.32, HYD4 0.03 kmol/h, equal to the script's).
Emissions: CO2 vent carries 0.5 kg CH4 and 0.5 kg C2H4 per t EO (ASSUMED, inside BREF Table
7.4 before treatment: CH4 0.03-1.45, NMVOC 0.07-1.35 kg/t EO); EO from vents, fugitive
emissions and trace by-products are not estimated (lca.yaml emission_exclusions).
Cross-check: 1.68 t MEG per t ethylene, inside the 1.53-1.70 t/t that Shell states for
conventional plants (SHELL, vendor claim, cross-check only).
Core issue met: with a `selectivity:` block on both reactors, `cheme validate` reported that the
second reactor's reactions form nothing. In chemeascode/domains/process/model.py
`_reactor_rules`, the selectivity check overwrites the dict `declared` (reaction id -> reaction)
with a list, so every later step sees no reactions. Work-around: R-101 takes per-reaction
conversions of its key (process/reactions.yaml), R-401 keeps `selectivity:`. To report to core.

## D-007 Thermodynamic and reaction model basis; gated steps (2026-10-28)
Decision: no property package and no simulation at this stage. The reactors are conversion
models (R-101: sourced-range conversion and selectivity; R-401: full conversion with the
modelled split), not kinetics. Reaction heats: EO formation -105 kJ/mol and total combustion
-1323 kJ/mol of ethylene (gas, BREF 7.2.1.1.1); hydration -95 kJ/mol per step ASSUMED (from
standard formation enthalpies recalled, to be checked against a sourced table). Normal boiling
points in materials.yaml are rounded values to be checked.
Reason: the loop gas (CH4-C2H4-O2-Ar-CO2 with EO) needs an equation of state with qualified
binary parameters; the EO-water-glycol liquids are strongly non-ideal (activity-coefficient
model with sourced NRTL/UNIQUAC pairs). Core's benchmarked packages cover air and syngas
mixtures only; the polar/activity-coefficient benchmark and liquid-reactor energy verification
are open in core #315 (pre-release issue 315), so `cheme process props` and `cheme process
simulate` cannot qualify these streams. Gated steps: (1) stream enthalpies and energy closure
of blocks and steps; (2) a predictive simulation of the absorber, strippers, evaporators and
glycol columns (DWSIM with a recorded method selection); (3) R-101 energy balance from the
simulator (DWSIM also refuses R-101 as written: one conversion reactor with four energy streams,
`cheme maturity`).

## D-008 Energy estimate and steam integration (2026-10-28)
Decision: duties are a lumped estimate in scripts/eg_balance.py, all ASSUMED: reaction heat of
R-101 raised as 2800 kPa(a) steam (83.5 MW, about 127 t/h) and used inside the plant (EO
stripper 36.7 MW, CO2 regenerator 11.5 MW at 3.0 GJ/t CO2, first evaporator effect 22.7 MW,
MEG column 12.6 MW); MP steam imported for the rest (MEG column 12.9 MW, drying column 7.6 MW,
DEG 1.9 MW, TEG 0.06 MW): **22.5 MW = 1.62 GJ/t MEG**. Evaporator economy 3.2 (four effects)
with the hydration heat (23.4 MW) credited; reflux ratios 0.3 (drying), 1.2 (MEG), 2.0 (DEG,
TEG); latent heats MEG 52, DEG 57, TEG 61 kJ/mol. Power 6.76 MW = 0.135 kWh/kg MEG: recycle
compressor 4.36 MW (1950 -> 2200 kPa(a), isentropic 0.75), lean absorbent pump 1.0 MW, glycol
feed pump 0.4 MW, auxiliaries 20 kWh/t MEG. Cooling water 171.6 MW = 3.43 kWh/kg MEG (the last
evaporator effect and the lean absorbent cooler dominate; the last-effect vapour is not used as
LP steam, a heat-integration opportunity the BREF names, 7.2.2.5).
Reason: no open per-tonne utility data found (BREF 7.3.4 declines to give energy ranges); a
transparent first estimate is better than none. BREF 7.3.4 confirms the qualitative picture:
the EO section is a net steam producer, the EG section a net consumer, the balance depends on
selectivity. Expected accuracy is poor (+/-50 %); the steam import is the difference of two
large numbers and the most uncertain LCI exchange.

## D-009 Lists (2026-10-28)
Decision: the equipment list carries the 16 PFD items with service and the balance values in
the notes; no line or instrument list entries (no P&ID at this stage). Several parallel EO
reactors and evaporator effects are listed as one item each.

## D-010 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml maps every terminal of the flowsheet: feeds (ethylene, oxygen, methane,
demineralised water), utilities (MP steam heat, electricity, cooling water), wastes (heavy
glycols to incineration, purge to combustion with energy recovery, bleed to biological
treatment) and the CO2 vent as emissions (CO2 fossil, CH4, C2H4); every background is declared
`missing:` with the activity it should connect to (a gap, never 0). Mass allocation between
MEG, DEG and TEG (MEG share 92.0 %), with the deviation from the price hierarchy declared (no
open glycol prices). Functional unit 1 kg MEG at the gate. The EO catalyst (about 0.2 kg/t EO,
BREF 7.3.6.3 range 0.12-0.8), potassium carbonate make-up and moderator are open consumables,
left out until compositions are known (otherwise the element balance is not assessable).
Result (cheme assess lca --inventory --write, --coverage): mass, element and carbon-origin
balances closed; 11 gaps; direct emissions only: 0.264 kg CO2-eq per kg MEG (mass-allocated;
CO2 0.253, CH4 0.00036 kg); ethylene has no GWP100 factor (a gap of the method). Unallocated
per kg MEG: ethylene 0.596 kg, oxygen 0.591 kg, methane 0.010 kg, water 0.230 kg, MP steam
0.449 kWh, power 0.135 kWh, cooling 3.43 kWh; DEG 0.0834 kg and TEG 0.0036 kg co-products;
purge 0.0256 kg, CO2 vent 0.283 kg (CO2 0.275 kg), bleed 0.0305 kg, heavies 0.00029 kg.
Atlas build (scripts/build_lci.py --strict): no error for this process, 6 gaps reported
(ethylene, oxygen, methane, heavies, purge, C2H4 emission); lca/mappings.yaml only re-units the
steam exchange (`use: steam-heat`, as soda-ash-1).

## D-011 Open library items (2026-10-28)
Missing in chemicals/chemicals.yaml (for the consolidated PR): ethylene, ethylene-oxide,
ethylene-glycol (MEG, with a fibre-grade grade), diethylene-glycol, triethylene-glycol, and
possibly ethane, potassium-carbonate and a glycol heavies mixture. Missing in lci/mappings.yaml
technosphere: ethylene, the glycols as products, treatment of the glycol heavies residue,
combustion of a hydrocarbon purge gas; biosphere: ethylene to air (C2H4, fossil). Core: the
`_reactor_rules` selectivity bug (D-006).
