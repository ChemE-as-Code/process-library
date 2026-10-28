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
  (BREF 7.2.1.1.1: 200-300 C, 15-25 bar); the mixed feed gas (333 K) is preheated to 483 K in
  the E-101 feed/effluent exchanger (step E100, 40 K approach to the effluent; energy in D-008);
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
  conversion, no catalyst; SHEH names 10-25 mol/mol); the mixed feed (aqueous EO 313 K, make-up
  303 K, recycle water 393 K) comes to about 384 K and is heated to 423 K in E-401 with MP steam
  (D-008); the recycle water keeps the 393 K of the collected condensate across the bleed
  splitter;
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
the residue is a lower bound. At the BREF lower bound (1.4 kg/t EO) it would be 55 kg/h,
1.1 g/kg MEG instead of 0.29 g/kg: still below 0.2 % of the product mass, so the inventory's
waste to incineration is understated but the product split and the allocation are not
materially affected (review 2026-10-28 #7).
Sensitivity (review 2026-10-28 #3; `python3 scripts/eg_balance.py build` prints it): the base
case sits at the optimistic end (relative rate 2.0 gives 92 wt% MEG, the top of the BREF
range; selectivity 85 % in 75-90 %). Rerunning the balance:

| relative rate | EO selectivity | C2H4 kg/kg MEG | MEG wt% of glycols | MEG mass share (allocation) | heavies kg/t EO | MP steam import GJ/t MEG |
|---|---|---|---|---|---|---|
| 2.0 (base) | 0.85 | 0.596 | 92.0 | 92.0 % | 0.37 | 3.95 |
| 3.0 | 0.85 | 0.623 | 88.5 | 88.6 % | 0.92 | 4.11 |
| 2.0 | 0.80 | 0.633 | 92.0 | 92.0 % | 0.37 | 2.64 |
| 3.0 | 0.80 | 0.662 | 88.5 | 88.6 % | 0.92 | 2.74 |

Ethylene per kg MEG rises by up to 11 % across these cases (1.51 t MEG/t C2H4 at 3.0 and 80 %,
below the vendor's 1.53-1.70), and the MEG share falls to 88.6 %. The steam import falls with
the selectivity because more combustion raises more steam in R-101. The relative rate is
still unsourced. The LCA carries only the base case: a foreground sensitivity in lca/lca.yaml
needs a second flowsheet case (`scenarios: case:`), left for when the rate is sourced.

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
Decision: duties are a lumped estimate in scripts/eg_balance.py, all ASSUMED (gas cp
40 kJ/(kmol K); liquid cp water 4.18, EO 2.0, MEG 2.4 kJ/(kg K); heat of mixing neglected).
- EO reactor and E-101 (revised after review 2026-10-28 #1): the E-101 feed/effluent exchanger
  heats the mixed feed gas from 333 to 483 K with the reactor effluent (64.5 MW, step E100 and
  energy stream Q24; effluent 523 to 371 K); the trim cooler takes the effluent to 313 K
  (24.8 MW to cooling water). Of the R-101 reaction heat (83.5 MW), 17.2 MW heats the gas from
  483 to 523 K across the reactor; the rest, **66.3 MW (about 101 t/h of 2800 kPa(a) steam)**,
  is raised on the shell. The first estimate (83.5 MW raised, feed at 333 K) held only for an
  isothermal reactor and left the feed heating unsupplied.
- R-101 steam is used inside the plant: EO stripper 36.7 MW, CO2 regenerator 11.5 MW at
  3.0 GJ/t CO2, and the first evaporator effect with the rest, 18.2 MW.
- Glycol reactor feed (revised after review #2): the mixed feed is heated from 384 to 423 K in
  E-401 with **MP steam, 15.2 MW** (Q23). MP steam is the conservative choice. A feed/effluent
  exchanger on the 478 K reactor effluent, or vapour from the first effect, could serve it, but
  the effluent heat above the evaporator temperature is already credited to the evaporators
  (the hydration heat, below), so using it here as well would count it twice.
- MP steam imported for the rest: first evaporator effect top-up 4.6 MW, glycol feed heater
  15.2 MW, MEG column 25.6 MW, drying column 7.6 MW, DEG 1.9 MW, TEG 0.06 MW:
  **54.9 MW = 3.95 GJ/t MEG (1.10 kWh/kg)**, 2.4 times the first estimate (22.5 MW,
  1.62 GJ/t).
- Evaporator economy 3.2 (four effects) with the hydration heat (23.4 MW) credited; reflux
  ratios 0.3 (drying), 1.2 (MEG), 2.0 (DEG, TEG); latent heats MEG 52, DEG 57, TEG 61 kJ/mol. Power 6.76 MW = 0.135 kWh/kg MEG: recycle
compressor 4.36 MW (1950 -> 2200 kPa(a), isentropic 0.75), lean absorbent pump 1.0 MW, glycol
feed pump 0.4 MW, auxiliaries 20 kWh/t MEG. Cooling water 170.9 MW = 3.42 kWh/kg MEG (the last
evaporator effect and the lean absorbent cooler dominate; the last-effect vapour is not used as
LP steam, a heat-integration opportunity the BREF names, 7.2.2.5).
Reason: no open per-tonne utility data found (BREF 7.3.4 declines to give energy ranges); a
transparent first estimate is better than none. BREF 7.3.4 confirms the qualitative picture:
the EO section is a net steam producer, the EG section a net consumer, the balance depends on
selectivity. Expected accuracy is poor (+/-50 %); the steam import is the difference of two
large numbers and the most uncertain LCI exchange (see the selectivity sensitivity in D-005:
2.6-4.1 GJ/t MEG).

## D-009 Lists (2026-10-28)
Decision: the equipment list carries the 17 PFD items (E-401 added after review 2026-10-28 #2)
with service and the balance values in
the notes; no line or instrument list entries (no P&ID at this stage). Several parallel EO
reactors and evaporator effects are listed as one item each.

## D-010 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml maps every terminal of the flowsheet: feeds (ethylene, oxygen, methane,
demineralised water), utilities (MP steam heat, electricity, cooling water), wastes (heavy
glycols to incineration, purge to combustion with energy recovery, bleed to biological
treatment) and the CO2 vent as emissions (CO2 fossil, CH4, C2H4); every background is declared
`missing:` with the activity it should connect to (a gap, never 0). Mass allocation between
MEG, DEG and TEG (MEG share 92.0 %), with the deviation from the price hierarchy declared (no
open glycol prices). Functional unit 1 kg MEG at the gate.
Consumables (revised after review 2026-10-28 #4, which found them excluded only in a comment):
the silver EO catalyst is counted as a consumable (`consumables: eo-catalyst`, 0.2 kg/t EO
ASSUMED inside the BREF 7.3.6.3 range of 0.12-0.8 kg/t EO, 62.6 t/a, 0.16 g/kg MEG; 15 wt% Ag
ASSUMED) with no background (a gap) and its disposal to silver recovery. A precious-metal
catalyst is never cut. The potassium carbonate make-up and the organochlorine moderator are
declared `cutoff:` entries with their reason. Their amounts are not known, so the 1 % rule
reports them as unchecked (`cheme.lca-cutoff-unchecked`). All three now reach the dataset's
limitations. Consequence: core takes no composition for a consumable from lca.yaml, so the
element and carbon-origin balances now report "not assessable" (they closed without the
catalyst). Counting the catalyst is the more honest choice; the balance check comes back once
core accepts a consumable composition (to report to core with D-006's item).
Result (cheme assess lca --inventory --write, --coverage), after the energy revision of D-008:
mass balance closed, element and carbon-origin balances not assessable (above); 12 gaps;
direct emissions only: 0.264 kg CO2-eq per kg MEG (mass-allocated; CO2 0.253, CH4 0.00036 kg);
ethylene has no GWP100 factor (a gap of the method). Unallocated per kg MEG: ethylene 0.596
kg, oxygen 0.591 kg, methane 0.010 kg, water 0.230 kg, MP steam 1.098 kWh (3.95 GJ/t; was
0.449 kWh before review #1/#2), power 0.135 kWh, cooling 3.42 kWh, silver catalyst 0.00016 kg;
DEG 0.0834 kg and TEG 0.0036 kg co-products; purge 0.0256 kg (about 2.2 kg CO2/kg when burnt,
corrected from 2.7 after review #5), CO2 vent 0.283 kg (CO2 0.275 kg), bleed 0.0305 kg, heavies
0.00029 kg.
Atlas build (scripts/build_lci.py --strict): no error for this process, 6 gaps reported
(ethylene, oxygen, methane, heavies, purge, C2H4 emission); lca/mappings.yaml only re-units the
steam exchange (`use: steam-heat`, as soda-ash-1).

## D-011 Open library items (2026-10-28)
Missing in chemicals/chemicals.yaml (for the consolidated PR): ethylene, ethylene-oxide,
ethylene-glycol (MEG, with a fibre-grade grade), diethylene-glycol, triethylene-glycol, and
possibly ethane, potassium-carbonate and a glycol heavies mixture. Missing in lci/mappings.yaml
technosphere: ethylene, the glycols as products, treatment of the glycol heavies residue,
combustion of a hydrocarbon purge gas; biosphere: ethylene to air (C2H4, fossil). Core: the
`_reactor_rules` selectivity bug (D-006); a consumable composition in lca.yaml for the element
balance (D-010).

## D-012 Review responses: concept gate scope and maturity claim (2026-10-28)
Decision (review 2026-10-28-pfd-lci-review #6, #8):
- The concept gate `layout-plot-plan` is marked `applies: false` in checks/checks.yaml with
  this reason: the layout is out of scope of the case (D-001), so no plot plan is planned. The
  concept stage can now pass `cheme check` on the gates that apply.
- The warning `cheme.maturity-claim-exceeds` (process.yaml `maturity: concept` while `cheme
  maturity` reaches no calculation level) is accepted. Concept is the lowest value the manifest
  schema allows; the evidence gap is stated in process.yaml `validation.notes`. Raising the
  level to "sourced" would need the feed flows given with a source, but they are the output of
  our own balance on assumed parameters, and calling them "given" would misstate them. To be
  named in the consolidated PR.
Reason: both are scope facts, not design defects; recording them keeps the gates and the claim
honest.
