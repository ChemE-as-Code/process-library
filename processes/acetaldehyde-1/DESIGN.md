# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Acetaldehyde by the one-stage Wacker process, issue ChemE-as-Code/process-library#183. Run of
2026-10-28: design basis, balanced BFD/PFD and a preliminary gate-to-gate LCI. Library start
commit c692642, cheme-as-code 0.8.0 (pyDEXPI 2.1.0); no DWSIM simulation was run.

## Source register

All facts are restated in our own words; no table, figure or text was copied. "Read" means the
cited part was read for this run.

| id | source | locator | access / status | terms | used for |
|---|---|---|---|---|---|
| SRC-1 | Wikipedia, "Wacker process", https://en.wikipedia.org/wiki/Wacker_process (accessed 2026-10-28) | section "Industrial process" and its sub-sections one-stage / two-stage | open, read | CC BY-SA (facts only used) | one-stage conditions (about 130 C, 400 kPa, ethylene and O2 co-current through a reaction tower); ethylene fate per 100 mol fed; purification sequence (water extractive distillation, light ends CH3Cl/C2H5Cl/CO2 overhead); yield about 95 %. The article cites Ullmann's (SRC-2) for these |
| SRC-2 | Eckert, M. et al., Acetaldehyde, Ullmann's Encyclopedia of Industrial Chemistry, doi:10.1002/14356007.a01_031.pub2 | section 4.3.1 (direct oxidation of ethylene) per the issue | licensed; not read in this run | all rights reserved | primary source behind SRC-1; to be audited (open item O-1) |
| SRC-3 | US 4,237,073 (Hoechst AG, 1980), "Process for the manufacture of acetaldehyde", https://patents.google.com/patent/US4237073A/en | description (reactor 100-150 C, preferably 125-135 C, 3-4.5 bar abs; precondenser 105-115 C; coolers to 40-50 C; regenerator 165-180 C with direct steam; purge of CO2/inerts) and the comparative example (13 t/h acetaldehyde from 9 t/h ethylene and 5.3 t/h oxygen; 15 m3/h demineralised water to the reactor, 77.5 m3/h wash water, 1.5 m3/h extraction water, 1.5 t/h regeneration steam, 3 and 14 t/h steam to columns 1 and 2; 112.5 m3/h waste water with 0.28 % acids, 0.036 % aldehydes, 200 ppm organic chlorine) | open (US patent), read via Google Patents | US patent text, public | water, steam and waste-water rates and loads; plausibility check of feeds |
| SRC-4 | US 7,339,084 (2008), "Method for the production of acetaldehyde from ethylene and oxygen", https://patents.google.com/patent/US7339084B2/en | description: reaction at the boiling point set by pressure, 110-140 C; operating range 3.2-6.1 t/h ethylene | open, read | public | reactor temperature range |
| SRC-5 | US 5,557,014 (Catalytica, 1996), https://patents.google.com/patent/US5557014A/en | background on Wacker chemistry: one-stage vs two-stage; about 100-130 C; ~2 mol/L chloride; chlorinated organics up to a percent or more of the ethylene feed; titanium equipment | open, read (background only) | public | catalyst chemistry, by-product order of magnitude, materials |
| SRC-6 | NIST Chemistry WebBook, SRD 69, Henry's law data for CO2 (C124389) and ethylene (C74851) | Henry's law table | open, read | US government data | CO2 0.034 mol/(kg bar), 2400 K; ethylene 0.0047 mol/(kg bar), 1800 K |
| SRC-7 | chemicals 1.5.2 and thermo 0.6.1 packages of core's environment (open-source, MIT; the versions core pins), through `cheme chemistry thermo`: gas formation enthalpies from chemicals' Active Thermochemical Tables 1.112 data (`ATCT_G`: ethylene, ethane, O2, Ar, CO2, water, acetaldehyde, ethyl chloride, methyl chloride, HCl), from its packaged CRC Handbook table `heat_capacity.CRC_standard_data` (acetic acid, crotonaldehyde) and from its Yaws table `reaction.Hfg_S0g_YAWS_data` (2-chloroacetaldehyde); standard entropies from `heat_capacity.CRC_standard_data` (all but 2-chloroacetaldehyde and crotonaldehyde, which come from `YAWS`); the CRC values are from the CRC Handbook of Chemistry and Physics, 2014 edition as chemicals cites it, and the YAWS values from Yaws, Thermophysical Properties of Chemicals and Hydrocarbons, 2nd ed. (2014) as chemicals cites it; both are licensed books, not read here; ideal-gas cp from chemicals' `heat_capacity.Cp_data_Poling` polynomials (Poling, Prausnitz and O'Connell, The Properties of Gases and Liquids, 5th ed.; a licensed book, not read here: ethylene, ethane, O2, CO2, water, acetic acid, ethyl chloride, methyl chloride, HCl), fitted to thermo's TRCIG correlation (acetaldehyde, crotonaldehyde) or to thermo's JOBACK group-contribution estimate (2-chloroacetaldehyde); Ar as a monatomic ideal gas | printed per component in process/materials.yaml | package queried; the underlying works not read | open-source packages queried; single values, facts only; not open data (library ADR 0037) | heats of reaction, gas enthalpies |
| SRC-8 | ChemicalBook product page for acetaldehyde (m.chemicalbook.com, ProductDetail_EN_501192), as summarised by search | consumption of the one-step route: ~710 kg ethylene (99 %) and ~300 m3 oxygen (99 %) per t | secondary, not verified | n/a | plausibility only, not used as input |

Not found in open sources in this run: ethylene conversion per pass, cycle-gas composition and
purge rate, oxygen purity, catalyst losses, electricity consumption, column stages and reflux.

## D-001 Route and boundary (2026-10-28)
Decision: one-stage Wacker (Hoechst-Wacker) process: ethylene and 99.5 % oxygen react together
in the aqueous PdCl2/CuCl2/HCl catalyst solution; crude acetaldehyde is recovered by cooling and
water scrubbing and purified in two columns (SRC-1, SRC-3). Boundary feeds: ethylene (no
library process yet; a steam cracker), oxygen (processes/asu-1 can supply it), hydrochloric acid
30 wt% (processes/chlor-alkali-1 makes chlorine and hydrogen, not HCl yet), demineralised and
process water, MP/LP steam, power and cooling water. Purge, light ends and the side draw go to a
thermal oxidiser / incinerator, and the waste water to biological treatment, all outside the
boundary.
Reason: the case notes prescribe this route; it is the dominant ethylene-based route and the
only one for which an open plant-scale example (SRC-3) was found.
Rejected: the two-stage process with air (SRC-1: same yield, more reactors and piping; oxygen
supply makes the one-stage process the simpler balance); ethanol dehydrogenation/oxidation and
acetylene hydration (issue scope notes; kept for a later route comparison, open item O-6).
Assumptions: oxygen arrives at 600 kPa(a); its compression belongs to the supplier.

## D-002 Capacity, hours and product (2026-10-28)
Decision: 100 kt/a acetaldehyde, 8000 h/a, 12 500 kg/h of 99.9 wt% product (rest water) at
300 kPa(a), 303 K. ASSUMED.
Reason: a single train close to the 13 t/h of the SRC-3 example, so its specific water and
steam rates scale with little extrapolation. No client figure exists.
Assumptions: product specification of 99.9 wt% with only water as impurity is ASSUMED (product
quality per SRC-2 section 5 not audited, O-1).

## D-003 Feed specifications (2026-10-28)
Decision: ethylene 99.9 mol% with 0.1 mol% ethane; oxygen 99.5 mol% with argon standing for all
inerts; hydrochloric acid 30 wt%. All ASSUMED; feeds at 600 kPa(a), 298 K.
Reason: typical commercial grades; the inerts set the purge.

## D-004 Reaction model (2026-10-28)
Decision: a selectivity (conversion) reactor in cheme (step R101): ethylene conversion per pass
35 % (ASSUMED, unsourced) and molar selectivities per mol ethylene converted derived from the
ethylene fate reported for the industrial process (SRC-1, citing SRC-2): per 100 mol fed about
95 acetaldehyde, 1.9 chlorinated aldehydes, 1.1 unconverted ethylene, 0.8 CO2 (as ethylene
burnt), 0.7 acetic acid, the rest minor. Our split (ASSUMED): chlorinated aldehydes 1.6 (lumped
as 2-chloroacetaldehyde) plus 0.3 that we count as acetaldehyde formed but lost downstream, so
95.3 acetaldehyde formed; minor products crotonaldehyde 0.25 (as C2), chloroethane 0.15,
chloromethane 0.10. Reactions R1-R7 in process/reactions.yaml; R4 and R6 are lumped overall
stoichiometries, R7 the aldol condensation. The HCl make-up equals the chlorine leaving in R4-R6
(16.3 kg HCl per t product).
Reason: no open kinetics; the reported fate is the best open evidence and cheme's selectivity
model reproduces it with closed element balances.
Rejected: kinetic model (none sourced; never invented); treating the 1.9 % chlorinated
aldehydes fully as waste-water load (contradicts the 200 mg/kg organic Cl of SRC-3, D-008).
Assumptions: the per-pass conversion only sets the recycle flow (cycle gas 1372 kmol/h), not
the yield; the catalyst solution is not a stream (D-010). Product yield on fresh ethylene after
downstream losses: 94.1 mol%.
Evidence gap (O-2): per-pass conversion, the real by-product spectrum (oxalic acid, chloral,
chloroacetic acids are not modelled) and their split between catalyst solution, regenerator and
products.

## D-005 Reactor conditions and energy (2026-10-28)
Decision: 403 K, 400 kPa(a) at the top, feed gas at 500 kPa(a) (liquid head); boiling-cooled:
the heat of reaction (19.2 MW, R1 -217.9 kJ/mol on an ideal-gas basis) evaporates water, and the
precondenser E-101 (to 383 K) returns the condensate S09 (10.7 t/h) that closes the reactor's
energy balance in scripts/acet_balance.py.
Reason: conditions from SRC-1, SRC-3 (125-135 C, 3-4.5 bar abs) and SRC-4 (110-140 C).
Assumptions: heat of solution of HCl and the catalyst-solution enthalpy are neglected; regenerator
steam enters as vapour at 453 K; ideal-gas enthalpies with water and organics liquid enthalpies
from rounded heats of vaporisation (script header).

## D-006 Balance method and water/steam basis (2026-10-28)
Decision: an independent script, scripts/acet_balance.py (`cheme run scripts/acet_balance.py`),
solves the cycle-gas loop, the separators and the duties; its values enter the flowsheet as
ASSUMED with the decision ids; cheme calculates the reactor outlet, mixers, pass-through steps
and the purge splitter and checks every balance. Water and steam rates are those of the SRC-3
comparative example scaled by 12.5/13: reactor make-up 14.4 t/h, wash water 74.5 t/h, extraction
water 1.44 t/h, regeneration steam 1.44 t/h, live steam 2.88 and 13.46 t/h.
Reason: no property package of cheme covers this system (props --coverage refuses acetaldehyde);
the patent is the only open plant-scale data.
Check against SRC-3 (scaled per t product): ethylene 677 vs 692 kg/t, oxygen 410 vs 408 kg/t,
waste water 8.69 vs 8.65 m3/t. Our ethylene is lower because SRC-1's 95 % yield is newer than
the 1980 example (SRC-4 reports a later yield gain).

## D-007 Gas cooling, scrubbing and cycle gas (2026-10-28)
Decision: E-102 cools to 318 K and condenses 30 % of the acetaldehyde, all acetic acid,
chlorinated aldehyde and crotonaldehyde and water to saturation (ASSUMED); the scrubber C-101
leaves 0.05 mol% acetaldehyde in the cycle gas (ASSUMED) and absorbs chloroethane and
chloromethane fully (ASSUMED, optimistic); CO2 and ethylene dissolve in the crude by Henry's law
at 313 K and 370 kPa (SRC-6). Cycle gas 8 mol% O2 (ASSUMED, below the limiting oxygen
concentration of ethylene). The purge (0.513 % of the cycle gas, 248 kg/h) follows from the
inert balance with 1.1 % of the ethylene lost unconverted.
Result: cycle gas 40 % C2H4, 35 % CO2, 11 % Ar, 4 % C2H6, 8 % O2 (mol); 53 % of the CO2 formed
leaves dissolved in the crude (to the light ends), the rest in the purge.
Open (O-3): real plants may run with a larger purge or CO2 removal and a richer ethylene cycle
gas; the composition here is a consequence of the assumed losses, not plant data.

## D-008 Distillation (2026-10-28)
Decision: C-201 light-ends column at 200 kPa(a) with 1.44 t/h extraction water and live steam
(SRC-1, SRC-3): overhead all dissolved CO2, ethylene, chloroethane, chloromethane, 0.2 % of the
acetaldehyde (ASSUMED) and water to saturation. C-202 acetaldehyde column at 270-300 kPa(a) with
live steam: 99.9 wt% acetaldehyde overhead; side draw of all crotonaldehyde and the chlorinated
aldehyde not in the waste water, at 40 wt% organics, 10 wt% acetaldehyde, 50 wt% water
(ASSUMED); bottoms waste water with all acetic acid, 200 mg/kg organic chlorine and 360 mg/kg
aldehyde (SRC-3 comparative example). A feed/effluent exchanger E-201 recovers 8.5 MW from the
waste water (ASSUMED, crude to 383 K). Condenser duties by enthalpy balances of the live steam:
0.39 MW (C-201) and 7.2 MW (C-202, implying a reflux ratio of about 2.5).
Open (O-4): SRC-3's waste water carries 0.28 % acids (about 2.4 times our acetic acid): other
acids (chloroacetic, formic, oxalic) are not modelled, so the COD load is understated. The side
draw route (incineration vs crotonaldehyde recovery) is a choice to confirm.

## D-009 Utilities and drives (2026-10-28)
Decision: cooling water 298/308 K; MP steam 1000 kPa(a) (regenerator needs 165-180 C, SRC-3) and
LP steam 450 kPa(a), both injected live; electric drives. Cycle-gas compressor 370 -> 520 kPa(a)
at isentropic efficiency 0.75 (461 kW); pumps from flows and heads at efficiency 0.70 (74 kW);
total 535 kW = 42.8 kWh/t. All ASSUMED.
Result per t product: LP steam 1.31 t, MP steam 0.115 t, cooling water heat 2.59 MWh (32.4 MW).

## D-010 Catalyst (2026-10-28)
Decision: the catalyst solution (SRC-3 example: about 100 t water, 100 kmol Cu chlorides and
60 kg PdCl2 at 13 t/h) is inventory inside the reactor and regenerator, not a stream. Pd and Cu
losses and catalyst change-outs are not quantified: no open source found.
Open (O-5): Pd and CuCl2 make-up are a missing LCI exchange (not set to zero; an open
item of the inventory, D-011).

## D-011 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml, functional unit 1 kg acetaldehyde (PROD) at the gate; every exchange from
the balanced flowsheet with its stream ids; every background `missing:` with the activity it
should link to; purge, light ends, side draw and waste water as wastes to treatment (not direct
emissions); no allocation (single product). lca/mappings.yaml keeps oxygen and the live steam
off the Atlas build until a supplier is chosen.
Result (cheme assess lca --inventory/--coverage): per kg product: ethylene 0.6765 kg, oxygen
0.4096 kg, HCl 30 % 0.0542 kg, demineralised water 1.269 kg, process water 5.962 kg, LP steam
1.308 kg, MP steam 0.1154 kg, electricity 0.0428 kWh, cooling-water heat 2.591 kWh; purge
0.0198 kg, light ends 0.0164 kg, side draw 0.0713 kg, waste water 8.687 kg. Inputs 9.7941 kg =
outputs 9.7941 kg (difference below 1e-5 kg); cheme reports mass, element and carbon-origin
balances closed; 13 gaps (every background); DQR 2.33.
Missing chemicals-registry entries (for the consolidated PR): acetaldehyde, ethylene,
hydrochloric acid (or hydrogen chloride), acetic acid, crotonaldehyde, chloroacetaldehyde,
chloroethane, chloromethane, ethane.
Not in the inventory: catalyst make-up (D-010), fugitive and tank-breathing losses (declared
emission exclusions), construction.

## D-012 Lists (2026-10-28)
Decision: equipment and line lists hold the PFD's items with concept design conditions (highest
operating value + 10 %, at least + 2 bar, and + 25 K) and velocity-based first DNs, all ASSUMED.
Materials: reaction section titanium or lined steel (the chloride catalyst solution is extremely
corrosive, SRC-5), stainless steel downstream; to confirm.

## Gated steps and open items
- Energy closure, predictive scrubber and columns: no benchmarked property package for aqueous
  acetaldehyde / acetic acid / chlorinated aldehydes (`cheme process props --coverage` refuses
  every stream with acetaldehyde). The catalyst solution is an
  electrolyte. The current state of both in core was not checked.
- cheme maturity: calculation maturity none (feed flows are script results, not given with a
  source; R101, V101, V102, C101, C201, C202 specified, not sourced models).
- O-1 audit Ullmann's sections 4.3.1 and 5 (SRC-2) for conditions, by-products and product
  specification; O-2 per-pass conversion and by-product spectrum; O-3 cycle-gas composition and
  purge; O-4 waste-water acids/COD and side-draw route; O-5 catalyst losses; O-6 route comparison
  with the ethanol routes.
