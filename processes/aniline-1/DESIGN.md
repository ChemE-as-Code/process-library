# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Aniline by gas-phase hydrogenation of nitrobenzene, issue ChemE-as-Code/process-library#148.
Concept stage, agent-drafted 2026-10-28, not reviewed. Numbers live in `process/*.yaml` and
the scripts; this file keeps the decisions and where each fact comes from.

## Run record (2026-10-28)

- Library: branch `case/aniline-1` from main `11d50ef`; cheme 0.8.0 (pyDEXPI 2.1.0), thermo
  0.6.1, chemicals 1.5.2; core main at `7bed468` (GitHub API, read only). Core's property
  coverage was not checked beyond what
  `cheme process props --coverage` and
  `cheme maturity` report today (D-012).
- Scope: design basis, balanced BFD/PFD, preliminary gate-to-gate LCI. Out of scope: P&IDs,
  layout, HAZOP, TEA, datasheets.

## Source register

| id | source | locator | read | reuse | used for |
|---|---|---|---|---|---|
| SRC-1 | US 2008/0234518 A1, Bayer MaterialScience AG, "Process for producing aromatic amines" (granted as US 9,067,864 B2), https://patents.google.com/patent/US20080234518A1/en | description (operating ranges), examples 1-5 | full text of the Google Patents page read in this run (machine summary), first 100 000 characters | patent: facts with citation | reactor type, inlet temperature, pressure, H2/NB and water ratios, catalyst, selectivity, catalyst loading, cycle time, heat recovery by steam raising, recycle and condensation scheme (D-003..D-005, D-011) |
| SRC-2 | US 9,233,910 B2, Bayer Intellectual Property GmbH, "Process for purifying aniline from gas phase hydrogenations", https://patents.google.com/patent/US9233910B2/en | detailed description (condensation temperatures and pressures), examples 1-4 (stream compositions, energy of the columns) | as SRC-1 | patent: facts with citation | by-products (benzene low boiler, diphenylamine high boiler, phenol), product purity 99.90 wt%, stripped water below 100 ppm aniline, residue to combustion, column energy as a plausibility check (D-004, D-007, D-008) |
| SRC-3 | PubChem CID 6115 (aniline), Solubility section (HSDB, citing Yalkowsky et al. 2010; ICSC) https://pubchem.ncbi.nlm.nih.gov/compound/6115 | Solubility | read in this run | facts | aniline in water 36 000 mg/L at 25 C (about 3.5 wt%); 3.4 g/100 mL at 20 C (ICSC) (D-007) |
| SRC-4 | thermo 0.6.1 / chemicals 1.5.2 (Caleb Bell, MIT licence) as packaged in cheme | `cheme chemistry thermo`; VaporPressure, EnthalpyVaporization, HeatCapacityLiquid, IAPWS-95 | used | open software | formation data, heat capacities, vapour pressures, heats of vaporisation, steam properties (D-006, D-013) |
| SRC-5 | Szargut, Morris, Steward (1988) Exergy analysis of thermal, chemical and metallurgical processes, Hemisphere | standard chemical exergy of the elements C, H2, N2 | values known, not re-read in this run | facts | aniline chemical exergy for the allocation (D-013) |
| SRC-6 | Kahl et al., Aniline, Ullmann's Encyclopedia (doi:10.1002/14356007.a02_303.pub2) | - | not read (licensed) | - | route reference lead only; no value taken |
| SRC-7 | hydrogen-1 (this library), process/flowsheet.yaml stream S17 | product stream | read | own data | hydrogen feed state and purity (D-002) |

No figure, table or text was copied; the values above are restated in our own words and units.
The held-out benchmark of the issue was not searched for.

## Basis table (sourced / proposed / missing)

| item | value | status |
|---|---|---|
| capacity | 25 t/h aniline, 8400 h/a (210 kt/a) | proposed, ASSUMED (D-002) |
| nitrobenzene feed | pure, 313 K, 500 kPa(a) | proposed, ASSUMED; real impurities missing (D-002) |
| hydrogen feed | 99.9 mol% H2, 0.1 % N2, 2850 kPa(a), 313 K | sourced: hydrogen-1 S17 (SRC-7) |
| product | 99.95 wt% aniline, 0.05 wt% water | proposed; 99.90 wt% achieved in SRC-2 examples |
| reactor inlet | 513 K, 530 kPa(a) | proposed inside SRC-1 preferred ranges (200-300 C, 2-20 bar) |
| H2/NB at inlet | 60 mol/mol | proposed inside SRC-1 most preferred 50-90 |
| conversion | complete | sourced (SRC-1 examples: NB-free crude until breakthrough) |
| selectivity to aniline | 0.997 | sourced (SRC-1 example 3, average) |
| by-product split | 0.2 % benzene, 0.1 % diphenylamine (of NB) | ASSUMED (D-004) |
| separator / decanter | 333 K / 313 K, solubilities 3.6 wt% aniline in water, 5 wt% water in aniline | 3.6 sourced (SRC-3, 25 C); 5 wt% ASSUMED |
| columns | pressures, reflux, splits | ASSUMED (D-008) |
| kinetics, catalyst vendor data, utilities prices, site | - | missing |

## Method and dependency table

| calculation | method used | qualified by cheme? | gate |
|---|---|---|---|
| reactor outlet | cheme selectivity reactor (conversion model), element balance | yes (balance); model basis specified, not predictive | none for a concept balance |
| reactor energy | ideal-gas formation data, `cheme process reactors` (duty -0.8 kW: adiabatic) | yes, ideal gas | - |
| mixers, splitter, pass-throughs | `cheme process propagate --fill` | yes | - |
| V-101 vapour-liquid-liquid split | scripts/aniline_balance.py: vapour pressures (thermo) x activities from mutual solubilities | no | polar/activity-coefficient benchmark (core "#315"); `props --coverage`: no package covers aniline |
| decanter, columns | specified splits and duties from enthalpy balances (scripts/aniline_balance.py) | no | same; `cheme process simulate` also refuses P101 (TransportingFluids) |
| stream enthalpies, energy closure in core | not evaluable (no package) | no | same |
| LCI | `cheme assess lca` (gate-to-gate, backgrounds unmapped) | yes | backgrounds to link (D-013) |

## D-001 Route and boundary (2026-10-28)
Decision: Adiabatic gas-phase hydrogenation of nitrobenzene over a palladium fixed bed with a
large hydrogen recycle (the Bayer/Covestro type of process, SRC-1), condensation, three-phase
separation, decanting, dehydration and vacuum distillation of aniline, steam stripping of the
process water. Boundary: nitrobenzene and hydrogen are boundary feeds (nitrobenzene from a
benzene nitration plant, hydrogen from the library process hydrogen-1); products leave at the
battery limit: aniline to storage, purge to the fuel gas header, low boilers and residue to
incineration, process water to biological treatment, net MP steam to the site header.
Reason: the issue names gas-phase hydrogenation; the adiabatic Pd process is fully described in
open patents with operating ranges, selectivity and the work-up, so the concept rests on
sourced facts rather than guesses. The case notes ask for the feeds made by other library
processes to enter at the boundary.
Rejected: fluidised-bed Cu process (BASF type; no open source with operating data read in this
run); multitubular isothermal Cu or Ni fixed bed (same); liquid-phase hydrogenation (the issue
names the gas phase); nitration inside the boundary (separate case).
Assumptions: none beyond those listed in D-002..D-013.

## D-002 Capacity, feeds and product (2026-10-28)
Decision: 25 t/h aniline (600 t/d, 210 kt/a at 8400 h/a); aniline 99.95 wt%, water 0.05 wt%,
313 K, 300 kPa(a). Nitrobenzene pure, liquid, 313 K, 500 kPa(a). Hydrogen as hydrogen-1's product
S17: 99.9 mol% H2, 0.1 % N2, 2850 kPa(a), 313 K, let down into the loop.
Reason: a single-train world-scale size (ASSUMED, not a client figure); SRC-2's examples reach
99.90 wt% pure aniline, our target is a small margin above it. Linking the hydrogen state to
hydrogen-1 makes the interface explicit (issue: "map hydrogen as an explicit supply interface").
Rejected: a capacity from a named plant (no traceable open basis found).
Assumptions: ASSUMED capacity, hours and nitrobenzene purity; the nitration impurities
(dinitrobenzene, nitrophenols, benzene) are an open input: they matter for catalyst life and the
phenol content of the product (SRC-2).

## D-003 Reactor (2026-10-28)
Decision: one adiabatic fixed bed of Pd-V-Pb on alpha-alumina (catalyst PD_AL2O3), inlet 513 K,
530 kPa(a), outlet 729 K, 500 kPa(a), no internal cooling; the reaction heat leaves with the
effluent and raises MP steam in E-103 (SRC-1: steam raising from the product gas).
Reason: SRC-1 preferred inlet 200-300 C, pressure 2-10 bar (most preferred), maximum catalyst
temperature 500 C (most preferred): the calculated outlet, 456 C, is inside. One bed keeps the
concept simple; SRC-1 prefers several beds in series with interstage steam raising.
Rejected: reactors in series with fresh nitrobenzene between them (lower recycle, lower peak
temperature; a basic-engineering optimisation).
Assumptions: ASSUMED one bed; no hot spot, ageing or end-of-run breakthrough modelled.

## D-004 Reactions and selectivity (2026-10-28)
Decision: main reaction NB + 3 H2 -> aniline + 2 H2O; by-products lumped as benzene
(NB + 4 H2 -> benzene + NH3 + 2 H2O) and diphenylamine (2 NB + 6 H2 -> DPA + NH3 + 4 H2O).
Complete conversion; per kmol NB converted 0.997 kmol aniline, 0.002 benzene, 0.0005 DPA.
Reason: 0.997 is the average aniline selectivity of SRC-1 example 3, and the crude is free of
nitrobenzene until breakthrough (examples 1-3). SRC-2 names benzene as the typical low boiler
and diphenylamine as the typical high boiler of gas-phase crude aniline, and its crude carries
more low than high boilers, hence the 2:1 split.
Rejected: kinetics (no rate law for this catalyst read in this run; none invented);
cyclohexylamine, cyclohexanol/-one and phenol as separate by-products (no open split).
Assumptions: ASSUMED split of the 0.3 % loss and the reaction paths of the lumps. Heats of
reaction (ideal gas, 298 K) from the formation data: -464.6 MJ/kmol (main), which is about
-553 MJ/kmol from liquid nitrobenzene to liquid aniline and water. ln K at 729 K is about 70:
no equilibrium limit.

## D-005 Hydrogen loop (2026-10-28)
Decision: H2/NB 60 mol/mol at the reactor inlet; the loop gas carries water (about 3 mol per mol
NB at the inlet) and some aniline (5.5 % of the production) back to the reactor; a purge holds
N2 at 5 mol% in the separator gas (purge fraction 0.00097, 70 kg/h). Recycle circulator K-101
400 -> 560 kPa(a). Liquid nitrobenzene is sprayed into the recycle gas preheated to 556 K in
E-102 and evaporates in it (V-102), giving 513 K.
Reason: SRC-1 most preferred 50-90 mol H2 per mol nitro groups and 4-25 mol water; a recycle of
amine below 15 % (preferably 5 %) of production; N2 may replace part of the hydrogen and helps
selectivity. 60 lowers the circulator power against 90 while keeping the outlet below 500 C.
Rejected: evaporating nitrobenzene into the make-up hydrogen alone (SRC-1's arrangement):
with 3 mol H2 per mol NB its dew point at 5 bar is near 510 K, which would need HP steam.
Assumptions: ASSUMED ratio, inert level and pressure drops; H2 and N2 not dissolved in the
liquids; all ammonia dissolved in the aqueous phase (in reality part of it stays in the gas
and leaves with the purge or the stripper overhead: open).

## D-006 Balance method (2026-10-28)
Decision: an independent balance script, scripts/aniline_balance.py (run with `cheme run`),
solves the recycle loop, the separator, the decanter loop and the columns, and the duties;
its outlets are entered in process/flowsheet.yaml as `assumed` with the script as source.
cheme calculates the reactor outlet (selectivity reactor), the mixers, the splitter and the
pass-through streams (`cheme process propagate --fill`) and checks every balance.
Reason: core has no qualified property package for aniline, nitrobenzene and water (polar,
liquid-liquid; `cheme process props --coverage`), so it cannot flash or simulate these units
(the issue's core "#315" gate). The script uses the same formation and heat-capacity data as
materials.yaml, so its reactor outlet temperature reproduces cheme's adiabatic duty (-0.8 kW).
Results: mass in 34 908.5, out 34 908.1 kg/h (molar masses of thermo vs elements); C, H, N, O
close to 1e-5 kmol/h; plant energy closes to 99.7 % (residual 152 kW = the pump work, not
converted to heat). Column energy 10.2 MW for 25 t/h (0.41 kWh/kg) is inside the range of
SRC-2's examples scaled to 25 t/h (0.27-0.46 kWh/kg).
Assumptions: ideal gas; liquid enthalpy = ideal gas minus heat of vaporisation (no heat of
mixing); nitrobenzene liquid at 313 K extrapolated with thermo's liquid heat capacity below the
Joback range (327 K).

## D-007 Separator and decanter (2026-10-28)
Decision: V-101 at 333.15 K, 410 kPa(a): vapour partial pressures = pure-component vapour
pressure x activity; water activity 0.993 and aniline activity 0.786 from the mutual
solubilities (Raoult's law for each phase's solvent), benzene by Raoult's law in the organic
phase. D-101 at 313.15 K: organic phase 5 wt% water, aqueous phase 3.6 wt% aniline. The
condensate is cooled from 333 to 313 K on its way (Q12, 0.48 MW).
Reason: SRC-2 condenses in steps at 25-90 C and 2-10 bar; 333 K gives SRC-1's inlet water ratio.
3.6 wt% is the aniline solubility at 25 C (SRC-3).
Assumptions: ASSUMED 5 wt% water in aniline (not sourced in this run) and the activity
approximation; to be replaced by a sourced NRTL/UNIQUAC set once core qualifies one.

## D-008 Work-up columns (2026-10-28)
Decision: C-201 dehydration column (top 60 kPa(a), heteroazeotrope overhead to D-101, low-boiler
draw of all benzene with its own mass of aniline to incineration, dry crude aniline bottoms at
70 kPa(a), 444 K); C-202 aniline column (top 20 kPa(a), 404 K, reflux ratio 0.5; bottoms 50 wt%
diphenylamine to incineration); C-102 process water stripper at 101.3 kPa(a) (azeotrope
overhead to D-101, bottoms 50 ppm(wt) aniline, cooled to 313 K). Condenser duties of C-201 and
C-102 carry a 30 % reflux margin.
Reason: SRC-2 describes the decanting, a water stripper giving an aniline-water azeotrope and a
stripped water below 100 ppm aniline, and residue combustion; pure aniline by distillation
overhead from the high boilers. Vacuum keeps the reboilers on 1500 kPa(a) steam.
Rejected: SRC-2's single combined column with side draws (an optimisation for basic
engineering); alkaline treatment against phenol (phenol not modelled).
Assumptions: ASSUMED pressures, reflux, splits and margins; stages not sized.

## D-009 Utilities and heat recovery (2026-10-28)
Decision: E-103 raises saturated steam at 1500 kPa(a) (23.5 MW); it feeds the C-201 and C-202
reboilers and, let down, the C-102 reboiler (10.2 MW together); 13.3 MW are exported. Cooling
water 298/308 K for E-104, the decanter cooler, the condensers and the water cooler (34.4 MW).
Electric drives: K-101 6.48 MW (isentropic efficiency 0.75), P-101 2 kW, column pumps and the
vacuum pump 150 kW lumped.
Reason: SRC-1 recovers the reaction heat as steam; using it for the reboilers avoids imported
steam. E-102 hot inlet 30 K above its cold outlet.
Rejected: LP steam raising in E-104 or feed/bottoms exchange on C-102 (open heat-integration
items, would cut cooling water and raise export).
Assumptions: ASSUMED levels, efficiencies and the 150 kW lump; no start-up heater.

## D-010 Lists (2026-10-28)
Decision: equipment and line lists hold the PFD items only; design pressure = highest operating
+ 10 % (at least + 2 bar), design temperature + 25 K (R-101 525 C for a hot-spot margin);
line sizes from velocity (gas 20 m/s below 10 bar, liquid 1.5 m/s). Loop lines DN1400-DN2000
follow from the H2/NB ratio at 4-5 bar.
Assumptions: ASSUMED rules; datasheets come at basic engineering.

## D-011 Catalyst inventory (2026-10-28)
Decision: about 22 t catalyst (33.2 t/h NB at SRC-1 example 3's average loading of about 1.5 g
NB per g catalyst and hour), regenerated in situ every 1100-1500 h (SRC-1), replaced every 4
years (ASSUMED), Pd about 0.9 mass% recovered by a refiner.
Assumptions: ASSUMED life and the transfer of the laboratory loading to the plant bed.

## D-012 Maturity claim (2026-10-28)
Decision: process.yaml claims `concept`, the lowest manifest level; `cheme maturity` supports
none: the feed flows are design choices (ASSUMED), and the reactor's selectivity specification
mixes a sourced aniline selectivity with an ASSUMED by-product split, so it stays `assumed`.
The predictive and engineering levels are gated by the missing property package (no package
covers aniline: `props --coverage`), `cheme process simulate` (which also refuses P101's class
TransportingFluids), datasheets and P&IDs. The concept gate fails only on the plot plan
(layout out of scope).
Note for core: `cheme process build` crashes on a step of class Pumping (pyDEXPI 2.1.0 annotates
its `method` as a Union, which `step_method` cannot list); P101 uses TransportingFluids.

## D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml, functional unit 1 kg aniline at the gate, boundary gate-to-gate,
system model cut-off. Every technosphere exchange (nitrobenzene, hydrogen, power, cooling water,
purge, residue, process water, catalyst and its disposal) carries `missing:` with the background
activity to link later; no factor and no value from a licensed database is used. Allocation by
exergy between aniline (36 931 kJ/kg, chemical exergy) and the exported MP steam (1279 kJ per
kWh of heat), from scripts/allocation_exergy.py: aniline carries 98.19 %, the steam 1.81 %;
shares 1/0 and no allocation are kept in the comparison. The purge (0.3 % of the output mass,
0.4 % of the aniline's heating value) is classified a waste for thermal treatment, not a
co-product. Fugitive leaks, catalyst regeneration and flaring are declared emission exclusions
as open gaps (not as negligible).
Reason: the library rule for exported steam (energy or exergy, never a credit); hydrogen-1 is
the worked example of an unmapped preliminary LCI (ADR 0022: an unmapped exchange of an
internal process is a reported gap).
Results (unallocated per kg aniline): nitrobenzene 1.329 kg, hydrogen 0.0674 kg, electricity
0.265 kWh, heat to cooling water 1.377 kWh, MP steam export 0.532 kWh, process water 0.388 kg
(50 ppm aniline, about 0.12 wt% NH3), residue and low boilers 5.2 g, purge 2.8 g, catalyst
0.026 g. cheme: mass balance closed; element balance not assessable (the catalyst consumable
has no composition in the lca schema); its "energy closure 32 %" compares the energy exchanges
only (power in, cooling water and steam out) and does not see the reaction heat, which the
script's plant energy balance closes (D-006).
Library build (`scripts/build_lci.py --strict`, run locally): aniline-1 reports 4 gaps
(feed:NBF, product:FUELGAS, product:RESIDUE, consumable:hydrogenation-catalyst: no registry slug
or mapping) and no warning of its own beyond the cut-off check that needs core installed (as
for every process). Two side effects were removed: (1) by the slug hydrogen the build linked
feed:H2F to chlor-alkali-1, the first Atlas producer, not hydrogen-1: lca/mappings.yaml sets
`atlas: false` until the link to hydrogen-1 is pinned on purpose; (2) with the slug steam the
export made aniline-1 the first Atlas steam producer, refused for hda-1's and soda-ash-1's HP
steam (whose links it displaced): process.yaml lists the steam co-product without an
inventory_key. The Atlas build still maps feed:POWER, product:CW and product:WW by their
registry slugs through the shared vocabulary; this folder's lca.yaml keeps them `missing:`.
Assumptions: the flows are concept estimates; geography generic (GLO).

## Missing entries of the chemicals registry (for the consolidated PR)
aniline (C6H7N, 62-53-3, main product), nitrobenzene (C6H5NO2, 98-95-3, feedstock), benzene
(71-43-2), diphenylamine (122-39-4), ammonia (7664-41-7) as by-product constituents; an MP
steam grade at 1500 kPa(a) saturated (the registry's `steam/mp-11bara` differs).
