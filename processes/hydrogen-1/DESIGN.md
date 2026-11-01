# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Numbers live in the YAML (`process/design-basis.yaml`, `process/flowsheet.yaml`); the stream
table is `cheme process streams` (generated). Issue: ChemE-as-Code/process-library#117.

Starting point of this run (2026-10-27): library branch `case/hydrogen-1` from `79a7cd4`,
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15, CoolProp and thermo in cheme's interpreter.
Core dependencies named in the issue, as they stand for this route: core's electrochemical
cell is not needed (no electrolysis); core's adsorption model has no PSA cycle model,
so the PSA is a specified split (D-008); the core issue on property qualification is open for
water-bearing synthesis gas, steam and flue gas, so the flashes, enthalpies and duties are
specified values from an independent script (D-006, D-011).

## D-001 Route and boundary (2026-10-27)
Decision: natural-gas steam methane reforming in a top-fired tubular reformer, feed
hydrodesulfurisation with ZnO guard beds, process gas waste heat boiler, adiabatic
high-temperature shift, cooling with process condensate separation, hydrogen PSA. The PSA
tail gas fires the reformer together with trim natural gas; the convection section and the
waste heat boiler raise 4.3 MPa steam, of which the surplus over the process steam is exported.
Boundary (gate-to-gate): natural gas at 4000 kPa(a), demineralised water, combustion air,
electric power and cooling water in; hydrogen, export steam, flue gas and boiler blowdown out.
The process condensate is recycled to the steam system inside the boundary.
Reason: the case notes of the issue (SMR, HT shift, PSA, tail gas as fuel, steam export); the
usual configuration of a stand-alone hydrogen plant with PSA (skill
`tech-refining-hydrogen-and-sulfur`: a PSA plant shows only HT shift; LT shift, solvent CO2
removal and methanation are replaced by the PSA).
Rejected: LT shift (adds CO conversion but the PSA removes CO anyway; a later option for
efficiency); CO2 capture (not in scope; the flue gas carries all CO2, which keeps the
feedstock/fuel split visible in the LCI); pre-reformer (D-007); product compression (delivery
at PSA pressure).
Assumptions: demineralised water treatment, cooling tower, the hydrogen header and the steam
header are outside the boundary.

## D-002 Capacity and product (2026-10-27)
Decision: 100 000 Nm3/h (0 C, 101.325 kPa) of product gas, 99.9 mol% H2, remainder N2, at
2850 kPa(a) and 313 K, net of the recycle to the hydrogenator: 9 110 kg/h.
Reason: a large single-train size, chosen for this study. ASSUMED, no client figure.
Rejected: 99.99+ mol% purity (a lower PSA recovery for a fuel-cell grade; no grade chosen).
Assumptions: CO and CO2 in the product at ppm level, not modelled.

## D-003 Reaction and reactor models; evidence (2026-10-27)
Decision: reactions in `process/reactions.yaml`: SMR (CH4 + H2O <=> CO + 3 H2) and WGS
(CO + H2O <=> CO2 + H2) from the core reaction library (`cheme chemistry library
steam_reforming`, `ht_shift`; their sources: Ullmann's Encyclopedia, article on the product;
Twigg (ed.), Catalyst Handbook, 2nd ed., 1989), reforming of ethane and propane written here,
and complete combustion of CH4, C2H6, C3H8, H2 and CO in the furnace. Reactor models:
- R102 reformer tubes: `reactor: equilibrium`, ideal gas, at the outlet 1143.15 K and
  3200 kPa(a), `approach: -10` (K evaluated 10 K colder, i.e. short of equilibrium for the
  endothermic reforming). Ethane and propane: residues at equilibrium are 1.8 ppm and 0.3 ppb.
- R201 HT shift: `reactor: equilibrium`, ideal gas, WGS only, `approach: 10` (K 10 K hotter),
  adiabatic: the outlet temperature 691.77 K is solved by the script (D-006); cheme gives a
  duty of 0.03 kW at it.
- H301 furnace: `reactor: conversion`, every combustible converted completely.
Model basis label: **equilibrium (ideal gas) with an assumed approach**, a sourced
thermodynamic model, not kinetics. Thermochemistry: ATcT formation enthalpies, CRC entropies,
heat capacities fitted to thermo TRCIG/HEOS 280-1500 K (`cheme chemistry thermo --fit`, max
deviation 1.1 %), recorded per component in `process/materials.yaml`.
Reason: steam reforming at 1100-1200 K on nickel and HT shift on Fe-Cr operate close to
equilibrium in industrial reactors; the approach temperature is the usual way to express the
distance. No rate law or catalyst data was taken from any source (none was read in this run).
Rejected: kinetics (no sourced rate law for a commercial catalyst; not needed for a balance);
Gibbs reactor (same answer, the named reactions make the extents reportable); fugacity
corrections (Peng-Robinson for 3.2 MPa and 1143 K changes little; open check).
Assumptions (ASSUMED): both approaches; carbon formation is not checked (S/C 3.0 is chosen to
stay clear of it: an open check at basic engineering); catalyst windows from the library
(`process/catalysts.yaml`) are typical ranges to confirm with a vendor. No reaction-evidence
file (`process/reaction-evidence.yaml`) was compiled: the route is the textbook route, and the
issue's literature notes concern the electrolysis comparison; an evidence search with
reported methane slips and shift approaches is the first item of the next stage.

## D-004 Natural gas (2026-10-27)
Decision: one natural gas for feedstock and trim fuel, 93.0 CH4 / 3.5 C2H6 / 0.7 C3H8 /
1.3 CO2 / 1.5 N2 mol%, dry, at 4000 kPa(a), 288 K. Two feed terminals (NG feedstock, NGF
trim fuel) so that the inventory keeps feedstock and fuel apart (D-013).
Reason: a generic lean pipeline gas; ASSUMED, not a specific grid or field analysis.
Rejected: a sourced grid specification (none read in this run; an open input).
Assumptions: sulfur species (H2S, mercaptans, odorant) are present at ppm level and removed in
R-101; they are not components (their mass is below the balance tolerance), so R-101 is a
pass-through in the balance. The sulfur content, the ZnO consumption and spent-sorbent
disposal are open inputs (LCI consumable gap, D-013). Higher hydrocarbons above C3 and
oxygen: none.

## D-005 Desulfurisation and recycle hydrogen (2026-10-27)
Decision: natural gas plus 0.03 kmol product hydrogen per kmol natural gas, preheated to
643 K in the convection section (E-101), hydrogenator and ZnO beds (R-101). The recycle is
taken after the PSA (SPL301, split 0.01128) and compressed by K-101 (2850 -> 4100 kPa(a)).
Reason: hydrogenation of organic sulfur needs hydrogen; a few per cent of the feed is the usual
order (ASSUMED).
Rejected: a hydrogen-free ZnO-only bed (cannot remove organic sulfur).
Assumptions: no heat of reaction in R-101; the recycle stays in the boundary (the product
rate of D-002 is net).

## D-006 Balance method: what cheme calculates and what the script gives (2026-10-27)
Decision: an independent balance script, `scripts/h2_balance.py` (run with `cheme run`),
calculates the plant from the design basis: the reformer and shift equilibria with the
ideal-gas data of `process/materials.yaml`, the adiabatic shift temperature, water-only
condensation (Raoult's law with the IAPWS saturation pressure, latent heat from CoolProp),
the PSA split, the furnace (trim fuel that closes the radiant balance), the convection
section duties and the steam system (IAPWS-IF97 enthalpies of water and steam). The
flowsheet gives the boundary feed rates, the separator, PSA and steam drum outlets, the
shift outlet temperature and all duties as `assumed` with the source "scripts/h2_balance.py".
cheme calculates the rest (`cheme process propagate --fill`): the reformer, shift and furnace
outlets and every mixer, splitter, exchanger and machine stream.
Reason: core has no property package for water-bearing synthesis gas, steam or flue gas
(the packaged `syngas-pr-vapor` excludes water; `air-pr-chemsep` stops at 315 K), and no
flash with water; `cheme process simulate` would need an unqualified DWSIM
package for the same mixtures.
Checks (2026-10-27): cheme's equilibrium outlets agree with the script to five significant
figures (CH4 in S9 0.0400201 vs 0.0400217; CO in S11 0.0239751 vs 0.0239757); the PSA and
separator balances close within the tolerance with cheme's values; cheme process reactors
gives R102 102 026 kW (script 102 025 kW), H301 -102 025 kW (the radiant balance, script
closes it by construction) and R201 0.03 kW (adiabatic).
Assumptions: ideal-gas enthalpies for steam at 4.3 MPa in the mixing of process steam with
the feed (a few per cent off the real enthalpy); dissolved gases in the condensate neglected;
no heat losses.

## D-007 Reformer and shift conditions (2026-10-27)
Decision: steam-to-carbon 3.0 (on hydrocarbon carbon); reformer inlet 893 K / 3500 kPa(a),
outlet 1143 K / 3200 kPa(a); waste heat boiler to 623 K; HT shift adiabatic from 623 K at
3150 -> 3050 kPa(a); cooling to 313 K and separation at 2950 kPa(a). No pre-reformer.
Result (calculated): methane slip 6.1 mol% dry at the reformer outlet; CO 2.4 mol% wet after
the shift; PSA feed 74.0 mol% H2.
Reason: typical values for a PSA hydrogen plant; ASSUMED. A pre-reformer pays where the gas is
rich in higher hydrocarbons or where the reformer must be relieved; with 4.9 mol% C2+ it is
an option for basic engineering, not needed for the balance (the case notes make it optional).
Rejected: S/C 2.5 (less steam, more carbon-formation risk), outlet 1173 K (lower slip, higher
tube temperatures): sensitivities for the next stage.
Assumptions: all ASSUMED; the reformer and shift catalyst windows of the library are met
(893-1143 K, 3.2-3.5 MPa inside 723-1223 K, 1.5-4 MPa; 623-692 K inside 583-773 K).

## D-008 PSA as a specified split (2026-10-27)
Decision: U-301 recovers 0.88 of the hydrogen of its feed into a 99.9 mol% product (rest N2);
all CH4, CO, CO2, water and the remaining N2 and H2 leave in the tail gas at 130 kPa(a).
Reason: core has no PSA cycle model (`performance: external` with a cited
or vendor recovery). 0.88 is an ASSUMED value inside the range usually quoted for
multi-bed hydrogen PSA; no source was read in this run, so it must be replaced by a vendor
or cited model value (open input).
Rejected: `process/adsorption.yaml` with `performance: external` in this run: its
recovery and utilities need a citation this run does not have.
Assumptions: no PSA power (pressure-driven), no product slip of CO/CO2.

## D-009 Furnace and fuel (2026-10-27)
Decision: the PSA tail gas plus trim natural gas, burned completely with 10 % excess air
(dry, ambient, no air preheat); flue gas leaves the radiant section at 1273 K (bridgewall)
and the stack at 423 K. The trim natural gas (5 619 kg/h, 73 MW LHV, a third of the fired 219 MW LHV;
the tail gas brings 145 MW) is what
closes the radiant balance: fuel + air enthalpy in = reformer absorbed duty + flue gas
enthalpy out.
Reason: ASSUMED typical values; tail gas firing is the case note. Without air preheat the
convection section has a large surplus, which becomes export steam.
Rejected: combustion air preheat (less trim fuel and less export steam; a basic-engineering
trade-off with the steam value), casing heat losses (not counted: about 1-2 % of the fired
duty would add trim fuel; ASSUMED neglect).
Assumptions: NOx, CO, unburnt hydrocarbons, N2O and particulates are not stream components;
they belong in `emission_estimates` of the LCA with sourced factors (open, D-013).

## D-010 Steam system and heat recovery (2026-10-27)
Decision: one steam level: drum 4500 kPa(a), superheated steam 4300 kPa(a) / 673 K (process
steam and export). Boiler feed water: demineralised make-up (298 K) and the process
condensate mixed at 300 kPa(a), pumped to 5000 kPa(a), heated in the economizer coil E-402
(flue gas 553 -> 423 K, 303 -> 345 K) and then in E-201 against the shifted gas (345 ->
503 K); boiling and superheat in the waste heat boiler E-104 and the convection coil;
blowdown 1 % of the feed water. The shifted gas is trimmed to 313 K with cooling water
(E-202, 298/308 K).
Reason: the coil order makes every exchanger feasible on temperature (cold ends: E-402 flue
423 K vs water 303 K; E-201 gas 428 K vs water 345 K; hot ends: flue 553 K vs water 345 K,
gas 692 K vs water 503 K). A pinch analysis is not done (open, `heat-integration`).
Rejected: deaerator steam and vent, a condensate stripper and low-pressure steam (not
modelled; the stripper steam and its vent belong in the next stage); demineralised water
preheat against the shifted gas (would lower the cooling water duty).
Assumptions: process condensate is clean enough to recycle after stripping (dissolved CO2,
methanol and ammonia traces not modelled).

## D-011 Balance status, energy and gated steps (2026-10-27)
Status: `cheme validate` 0 errors, 0 warnings; every block and step balances in mass,
components and elements (`cheme process streams`). Energy: the reactor and furnace duties are
cheme's own (D-006); the block energy balances are `not-evaluable` in `cheme process energy`
because no stream has an enthalpy (`cheme process props` covers none of the water-bearing or
hot streams).
Gated steps:
- stream enthalpies, flashes and a predictive heat and material balance: core's property-package qualification (a property
  package qualified for H2/CO/CO2/CH4/N2/H2O vapour and liquid water, and for flue gas);
- PSA performance: core's adsorption model with a cited or vendor recovery;
- core bug found: `cheme process build` 0.8.0 fails (`TypeError: 'typing.Union' object is not
  iterable`) on the step classes `Pumping` and `GeneratingSteam`, whose `method` is a Union in
  pyDEXPI 2.1.0; P401 is therefore `GeneratingFlow` and the steam steps `Evaporating`.
Plausibility (script, 2026-10-27): natural gas 455 MW LHV in (feedstock 382 MW, trim fuel
73 MW), 180 MJ LHV per kg of product; hydrogen 299 MW LHV out; export steam 10.5 kg per kg
of product; CO2 10.1 kg per kg (8.48 from the feedstock carbon, 1.63 from the trim fuel);
carbon in = carbon out (2 090.6 kmol/h). Not compared with a published benchmark in this run.

## D-012 Machines and design conditions (2026-10-27)
Decision: electric drives; isentropic efficiency 0.75 (K-101), 0.70 (fans K-301, K-302 and pump
P-401); fan pressure rise 5 kPa (FD) and 4 kPa (ID). Equipment design pressure: operating
+ 10 % (at least + 2 bar), design temperature + 25 K (+ 50 K for fired and hot-gas items).
Reason: ASSUMED concept values.

## D-013 Preliminary gate-to-gate LCI (2026-10-27)
See `lca/README.md` and `lca/lca.yaml`. Functional unit 1 kg of hydrogen product (S17) at the
gate. Every foreground exchange comes from the balanced flowsheet: feeds NG, NGF, DMW, AIR,
POWER; products H2, STEAMX, FLUE (emission), BD (wastewater), CW (heat to cooling water).
CO2 is kept apart by origin of its carbon through the two natural gas terminals: the
feedstock carbon (process CO2: reforming and shift, released when the tail gas burns) and
the trim fuel carbon (combustion CO2). Backgrounds are deliberately unmapped (`missing:`
with the activity they should connect to), so the result is a gap list, not a footprint.
Allocation (revised 2026-10-27 after review 2026-10-27-pfd-lci-review#1 and the library
build's refusal of `none` for a multi-output dataset): **exergy** between H2 and export steam,
H2 121 243.5 kJ/kg (physical 4 128.4 at 313 K / 2.85 MPa + chemical 117 115.1) and steam
1 256.6 kJ/kg (673 K / 4.3 MPa against liquid water at 298.15 K), `scripts/allocation_exergy.py`
(CoolProp; standard chemical exergies of Szargut et al. 1988). H2 carries 90.1 %. Why exergy:
the library allocates exported steam by energy or exergy in the cut-off build, never by credit
(docs/system-model.md section 2), and the steam has no heating value, so energy (LHV) would give
it nothing; mass (H2 8.7 %) has no physical meaning here. This departs from the hierarchy's
curated rules (H2 and steam are not products of one separation; no sourced prices for the WBCSD
ratio), which `allocation.deviation` states. System expansion by steam from a natural-gas
boiler stays the comparison for a later substitution variant. Combustion emissions of H-301:
the `emission_estimates` entry H301-firing (Tier 1 factors for natural gas, ASSUMED to apply to
the tail-gas firing too) replaces the balance's zero for CH4 and CO and adds N2O and NOx
(review #2).
Result (2026-10-27, `cheme assess lca --inventory --write`, `--coverage`, `--balance`): per kg
H2: natural gas 3.217 kg feedstock + 0.617 kg trim fuel, demineralised water 15.66 kg, air
30.89 kg, electricity 0.164 kWh; export steam 10.55 kg, blowdown 0.210 kg, heat to cooling
water 3.30 kWh; fossil CO2 10.10 kg at the stack (8.47 feedstock carbon, 1.63 trim-fuel
carbon). Mass and element balances closed (C residual -0.01 %). Classification: partial
screening (6 technosphere gaps by design); the 10.10 kg CO2-eq in results.md is the direct
stack CO2 only. After the exergy allocation (above) the result is 9.11 kg CO2-eq per kg H2
(direct stack CO2 9.10 + CH4/N2O of the estimate), still not a footprint. Open: burner-specific
combustion factors and PM, consumables (catalysts, ZnO, adsorbents), construction, and the
deaerator / condensate stripper vent and its steam (review #6, D-010).

## D-014 Library registry items missing (2026-10-27)
`chemicals/chemicals.yaml` has no entries for natural gas, carbon monoxide, ethane, propane
or demineralised water (argon exists); process.yaml therefore lists the natural gas under methane.
To be added in the consolidated registry PR (not in this folder).

## D-015 DWSIM simulation inputs prepared, not run (2026-10-30)
Decision: `process/simulation.yaml` now holds the full input of the first DWSIM simulation
(`cheme process simulate`, DWSIM 9.0.5 through core), modelled on ammonia-1's simulation
decisions. It was **not run**: the machine that wrote it has neither Docker nor a DWSIM
install. What was checked offline: the file loads against `cheme/simulation/v1`, `cheme
validate` reports no error, and the translation into the simulator model succeeds with
cheme 1.1.0, 1.2.0 and 1.2.1 (the version library CI now pins): `cheme process simulate --check` stops
only at `sim-unavailable`, after the translation. `cheme maturity` now passes
`predictive.simulation-spec` and `predictive.property-package` (both failed or were missing
before). The `property-package` pass is **not earned yet**: it rests on the PR substitution
below, which nobody has accepted; core reads `method_selection.substitution` as an accepted
substitution. It counts only once the owner or a reviewer accepts it and the acceptance is
recorded here and in the substitution text. It fails `predictive.coverage` (three parts left out, below) and
`predictive.model-basis`, because U-301 is a specified split (D-008), which caps the level at
balanced. No stream value was written.
Scope (17 units, 25 material streams of which 5 are feeds S1, S6, S20, S22, S25, and 9 energy
streams in the translated model, read with core's `translate.translation()` under cheme 1.1.0 and again under 1.2.1):
- simulated: FPT (M101, E101, R101 as a heater with zero duty, D-005), REF (M102, E102, R102
  equilibrium reactor with its approach of -10 K, E104), SFT (R201, E201, E202, V201 flash), PSA
  (U301 component separator, SPL301, K101), and of FUR the fuel mixer M301 and the fans K301,
  K302. The hydrogenator recycle is torn at S2; its flowsheet values are the first guess.
- left out (`exclude`): **H301** (radiant section): its radiant heat Q4 is R-102's duty, core
  refuses an energy stream shared by two units, and the trim fuel that closes the radiant
  balance (D-009) would need an adjust core does not offer. **E305** (convection section): one
  cooler with four energy streams to the coils E101, E102, E402 and D401, where a DWSIM cooler
  takes one. **STM** (steam system): a pure-water package balance whose steam flow follows from
  the boiler duties (an adjust); the process steam S6 enters as a feed with its flowsheet
  values, the process condensate S15 leaves as a product.
Specs: every outlet temperature, duty, pressure drop and efficiency repeats D-005, D-007,
D-008, D-010 or D-012 (source given per spec, all ASSUMED). DWSIM mixers take no pressure
drop, so the 50 kPa the flowsheet gives M-102 is put on E-102 (350 kPa). E-201 is set by its
duty, the 36 573.5 kW that heats the boiler feed water from 345 to 503 K (Q8 of
scripts/h2_balance.py, IAPWS-IF97, D-010), so the gas outlet temperature (428.33 K in the
concept balance) becomes the check. U-301 is a specified split (D-008): H2 0.88 and N2
0.176966 to the product (the N2 fraction gives 99.9 mol% H2 on the concept balance's PSA feed),
everything else to the tail gas; `basis_source` and `operating_basis` name D-008.
Property package: Peng-Robinson (DWSIM's PR with its own kij), recorded as a substitution.
Selection facts: 43 bar(a) (process steam S6, the highest pressure simulated), polar (water),
no electrolytes, no pseudocomponents, no liquid-liquid split, no association, and no
interaction parameters (`cheme process phase` finds ChemSep PR kij for water/CO2 only, none
for water with H2, CH4, CO or N2; DWSIM's own set was not inspected, so the conservative
answer). The tree then recommends PSRK or PR/RKS with modified Huron-Vidal mixing rules; the
DWSIM route runs none of them and methods.yml names PR as the executable substitute of PR-MHV2
(it loses the excess-Gibbs-energy mixing rule), as ammonia-1 does for the same gas. PR rather than
SRK (RKS, the substitute methods.yml names for PSRK): core's SRK claim holds no mixture,
because DWSIM 9.0.5's SRK database has no kij even for the nitrogen, oxygen and argon pairs,
while PR carries DWSIM's database kij and its claim covers those mixtures (methods.yml PR and
SRK notes); whether DWSIM's PR set holds kij for the water pairs here was not inspected. Core
claims PR only for N2, O2 and Ar (methods.yml; the core issue on property qualification is open), so the results for this
mixture are not qualified. The substitution is the agent's proposal and needs the owner's or a
reviewer's acceptance (not given as of 2026-11-01; the acceptance, with who gave it, goes into
this decision and the substitution text).
HT shift R-201 (core #58): DWSIM 9.0.5's equilibrium reactor in adiabatic mode fails its flash
(reproduced through core v1.0.0 on ammonia-1's HT shift bed; the issue is open, and core 1.1.0,
1.2.0 and 1.2.1 contain no fix). R-201 is therefore run with `mode: outlet_temperature` at the
concept balance's adiabatic outlet, 691.77 K (S11, scripts/h2_balance.py), and its simulated
duty is the check of the adiabatic assumption: it should be near zero (ammonia-1's beds gave
0.4 to 2.6 % of their reaction heat). Criterion, fixed before the run (ASSUMED, from that
ammonia-1 range): the check passes if |Q_R201| is at most 3 % of the WGS reaction heat of the
simulated S10 to S11 extent (extent times |dH_WGS| at the bed temperature, from the run's
streams). If it is exceeded, the run's R-201 outlet is not used: the outlet temperature spec
is re-solved until the simulated duty is zero (within the 3 %), the new temperature and the
deviation from 691.77 K are recorded in a new decision, and only then are stream values
filled. The equilibrium itself stays DWSIM's (WGS, approach
+10 K, ln K from DWSIM's Gibbs energies of formation: reactions.yaml gives no
`equilibrium_constant`). Rejected: a conversion reactor at the concept conversion, run
adiabatic (conversion reactors run adiabatic in ammonia-1). It would need `reactor:
conversion` and a conversion on the flowsheet step, replacing a predictive equilibrium by a
specified conversion (ADR 0030 then checks only that conversion). Also rejected: waiting for
the core fix.
Side effect of the workaround: R201 is no longer declared `mode: adiabatic`, so the LCA
boundary check (`cheme assess lca`) reports `boundary-utility-unassigned` for R201, though
R-201 is adiabatic and has no utility. lca/ was regenerated with cheme 1.1.0 (`cheme assess
lca --write`, commit d0c03dc), as ammonia-1 did under D-024, and its run manifest again with
cheme 1.2.1 (386c7f0; `cheme assess lca --check` passes on 1.2.1): `lca/results.md` now headlines an incomplete
boundary with R201 as its only gap, and the run manifest fingerprints the new
simulation.yaml, so the catalog does not withhold the LCA as `stale-run-manifest`. The
impacts (results.csv) are unchanged. To settle (owner): accept the flag as ammonia-1 did, or
ask core for a way to declare a reactor adiabatic while it is simulated at a fixed outlet
temperature.
What the first run should show (pre-run expectations, not results):
- pressure deviations by construction: S7 3850 vs 3800 kPa(a) (mixer); a component separator
  leaves both outlets at its inlet pressure, so S16, S17, S18 (2850) and S19, S21 (130 kPa(a))
  come out at 2950 kPa(a). The flowsheet values are the real conditions and stay. A let-down
  valve on the tail gas and the product would remove the deviation; that is a flowsheet change
  for later. K-101 then compresses from 2950 kPa(a), and S2's temperature and Q1 fall slightly.
- V-201: a Peng-Robinson flash of the S13 composition at 313.15 K and 2950 kPa(a) in thermo
  (`cheme process phase`, ChemSep kij, five water and CO pairs at zero), run as a pre-check and
  not with DWSIM, gives 0.2613 mol% water in the gas (script 0.2503 mol%, Raoult/IAPWS) and
  about 100 ppm CO2 in the condensate (D-010 neglects it). Both are inside the 0.001
  composition tolerance. DWSIM's kij differ, so the run decides.
- R-102 and R-201 duties against Q4 (102 025 kW) and about 0. S9 and S11 against the ideal-gas
  equilibria of `cheme process propagate` (PR fugacity at 3.2 MPa and 1143 K; small expected).
- `--fill` writes no stream value: every simulated stream already holds an assumed
  (scripts/h2_balance.py) or `cheme process propagate` value, and simulate never overwrites
  those. The run is recorded in process/simulation-run.json and every disagreement is a
  `sim-deviation`. Replacing the script values by simulated ones is a later decision, made
  once the deviations have been reviewed.
Open: H301, E305 and STM in the simulation (convection coils as two-stream exchangers on the
flue gas, as ammonia-1 did; an adjust or a fixed fuel for the radiant balance); property
qualification for water-bearing syngas (open core issue); a sourced PSA recovery (D-008); DWSIM's
own PR kij for water pairs, to be read from the saved flowsheet (`--save`).
## D-016 First DWSIM run: converged, simulated values replace the concept balance (2026-11-01)
Decision: the model of D-015 was run with `cheme process simulate` (cheme-as-code 1.2.1, the
version library CI pins; DWSIM 9.0.5.0 in the `cheme-dwsim:9.0.5` Docker image; Peng-Robinson).
It converged on the first attempt: the tear S2 closed in 5 iterations from its flowsheet values,
and again with S2 emptied (no `guesses:` needed). Run record: process/simulation-run.json. The
simulated values are filled as `calculated` (`origin: simulated`) in 28 streams. Before that,
the concept-balance values (scripts/h2_balance.py, D-006) and the `cheme process propagate`
values that the simulation now calculates were removed, so that `--fill` could write them:
temperatures of S2, S3, S7, S11, S12, S23, S26; flows and compositions of S2 to S5, S7 to S19,
S21, S23, S26; the duties Q1 to Q5 and Q9 to Q11. Kept, because they are design choices that
the specs reproduce or real conditions the model cannot represent: the design-basis
temperatures and pressures (S4, S8, S9, S10, S13 to S19), the composition of S16 (99.9 mol%,
D-002; the U-301 split reproduces it), and Q8 (E-201's duty spec, which feeds the excluded
E-401).
Only change to the specs: **R-201 outlet temperature 691.77 -> 689.92 K.** At the concept
balance's 691.77 K the bed needed +206.8 kW in DWSIM (WGS extent 595.5 kmol/h). The WGS heat at
690 K is 37.9 MJ/kmol (ideal gas; thermo 0.6.1 formation enthalpies and heat capacities through
cheme's interpreter), so the reaction heat is 6.27 MW and the duty is 3.3 % of it. That is above
the 3 % criterion D-015 fixed before the run. As D-015 prescribes, the temperature was re-solved
to zero duty by secant: 689.00 K gave -103.5 kW, 689.92 K gives -0.45 kW (0.007 %). The bed is
therefore simulated as adiabatic at DWSIM's own equilibrium (approach +10 K). The 1.85 K
difference comes from Peng-Robinson's enthalpies at 3.1 MPa against the script's ideal-gas
enthalpies. It is recorded here and in the spec's source.
The run forced these changes on the excluded steam system (STM), so that the balances still
close. While S15 and S19 kept the script values, `cheme validate` had 4 balance errors (V201,
U301, SFT, PSA).
- **Process condensate S15** is simulated: 49,306.7 kg/h with 0.212 mol% CO2 (254.5 kg/h of
  dissolved gases, 99.4 mol% CO2). D-010 had taken it as pure water. Its template is now
  `process_gas`.
- **Deaerator vent S35** (new): M-401 / V-402 gets a `vent` port, block STM a `vent` port, and
  there is a new product terminal DAV (an emission). The deaerator strips all dissolved gases of
  S15 to air (ASSUMED, like ammonia-1's condensate stripper in its D-024; water vapour and
  stripping steam not counted). Its values are computed by hand from the simulated S15 and
  marked ASSUMED with that source. lca/lca.yaml maps product:DAV as an emission, with the
  stack's elementary flows.
- **S28** (boiler feed water) keeps the script's 191,622 kg/h, now ASSUMED, because M-401 is no
  longer a plain mixer. **S27** (make-up water) is S28 less the water of the simulated S15:
  142,569.83 kg/h (script 142,669.53).
- The furnace side was re-propagated: S24 and S25 (H301 and E305 are excluded) follow from the
  simulated fuel S21, and K-302 is simulated on the new S25.

Simulated values against the concept balance. The reference is scripts/h2_balance.py, except
for the S9 and S11 compositions, which come from `cheme process propagate` (ideal-gas
equilibria). Deviation = (sim - script) / script.

| quantity | script / propagate | DWSIM (PR) | deviation | main reason |
|---|---|---|---|---|
| H2 product S17, kg/h | 9,109.92 | 9,077.70 | -0.35 % | more CH4 slip in R-102 (next rows); PSA recovery fixed at 0.88 |
| H2 product S17, Nm3/h (273.15 K) | 100,000 | about 99,640 | -0.36 % | as above |
| R-102 duty Q4, kW | 102,025.1 | 102,294.7 | +0.26 % | PR enthalpies against ideal gas |
| S9 CH4, mol fraction | 0.040020 | 0.040676 | +1.6 % | DWSIM's ln K from its own Gibbs energies and PR fugacities at 3.2 MPa, against the ideal-gas equilibrium |
| S11 CO, mol fraction | 0.023975 | 0.023431 | -2.3 % | R-201 is 1.85 K colder (more shift), and DWSIM's ln K |
| R-201 outlet S11, K | 691.77 | 689.92 | -0.27 % | re-solved to zero duty (above) |
| WHB duty Q5 (E-104), kW | 50,537.1 | 50,896.3 | +0.71 % | PR enthalpies of the wet gas |
| feed preheat Q2 (E-101), kW | 7,792.8 | 8,096.3 | +3.9 % | real-gas heat capacity of the natural gas at 3.9 to 4.0 MPa; inlet S3 0.75 K colder |
| mixed feed preheat Q3 (E-102), kW | 19,789.8 | 20,957.5 | +5.9 % | the steam's real-gas enthalpy at 3.8 MPa: after M-102, S7 is 656.75 K against 663.03 K, because PR mixes the 4.3 MPa steam colder than the script's ideal-gas mixing |
| E-202 duty Q9, kW | 30,071.1 | 31,046.3 | +3.2 % | water condensation in PR against the script's Raoult/IAPWS knock-out; S12 1.5 K colder |
| S12 (after E-201), K | 428.33 | 426.81 | -0.35 % | the same duty Q8 on PR enthalpies |
| PSA feed S14, kg/h | 74,072.1 | 73,717.5 | -0.48 % | more water and CO2 to the condensate |
| S14 water, mol% | 0.2503 | 0.2630 | +5.1 % | PR flash with DWSIM's kij; the thermo pre-check of D-015 gave 0.2613 |
| condensate S15, kg/h | 48,952.4 | 49,306.7 | +0.72 % | dissolved CO2 (254 kg/h; D-010 neglected it) and more condensed water |
| tail gas S19, kg/h | 64,858.3 | 64,536.3 | -0.50 % | follows S14 |
| K-101 power Q1, kW | 18.8 | 17.07 | -9.2 % | K-101 compresses from 2950, not 2850 kPa(a) (component separator outlet pressure, below); S2 354.7 against 359.1 K |
| K-301 / K-302 power, kW | 448.1 / 669.3 | 444.7 / 665.0 | -0.8 / -0.6 % | PR against the script's ideal-gas fan model |
| climate change, kg CO2-eq/kg H2 (exergy allocated) | 9.109 | 9.138 | +0.3 % | less product from the same feed; the vent's CO2 was already in the stack total |

Pressure deviations kept on purpose (`sim-deviation` warnings of `--check`, as D-015 expected):
- S7 is 3850 against 3800 kPa(a), because DWSIM mixers take no pressure drop (the 50 kPa is on
  E-102).
- S16, S17, S18 (2850 kPa(a)) and S19, S21 (130 kPa(a)) come out at 2950 kPa(a), because a
  component separator leaves its outlets at its inlet pressure.

The flowsheet values are the real conditions and stay. Let-down valves on the PSA product and
tail gas would remove the deviation (open).
Energy audit (run record): R-102 and R-201 close on the heat-of-formation basis (residuals
0.0002 and 0 kW). The plant closure is `unsupported` because U-301 is a component separator:
core has not established the sign of its energy imbalance. `sim-formation-data` reports the
project's formation enthalpies within the data tolerance (13.4 kW of 693 kW for R-102, 6.5 of
68.1 kW for R-201). Utilities of the simulated part: hot 131.3 MW, cold 118.5 MW, power 1.13 MW.
**Property package: not qualified.** Core benchmarks Peng-Robinson only for N2/O2/Ar mixtures
(and NRTL only for ethanol-water). Nothing in this flowsheet is inside a qualified range: not the
water-bearing synthesis gas, not the steam at 4.3 MPa, not the V-201 condensate. The core issue
on property-package qualification is open, so `cheme maturity` fails
`predictive.property-regime`. The PR substitution (D-015) is still the agent's proposal and has
not been accepted by the owner or a reviewer. The dissolved CO2 shows the spread:
- DWSIM's PR gives 0.212 mol% CO2 in the condensate.
- The thermo/ChemSep PR pre-check of D-015 gave about 0.01 mol%.
- A Henry's-law estimate gives about 0.14 mol%, closer to DWSIM. Its constant was not sourced in
  this run, so the estimate is ASSUMED.

The vent S35 and the condensate are therefore uncertain by more than a factor of 1.5.
Not re-closed: the excluded parts still rest on the concept balance and are now inconsistent
with the simulated duties by these amounts:
- the convection section E-305 gives the coils E-101 and E-102 1.47 MW more than in the script;
- the WHB raises steam on 0.36 MW more, so Q6, Q7, the steam flow S32 and the export steam S33
  are not re-derived;
- the trim fuel S20 closes the radiant balance at Q4 = 102,025 kW (D-009) and is 270 kW short of
  the simulated Q4;
- the simulated fuel S21 is 0.46 % lighter.

Re-closing these needs H301, E305 and STM in the simulation. The product is 0.36 % below the
100,000 Nm3/h of the design basis; the feed was not rescaled.
Maturity (`cheme maturity`, 1.2.1):
- pass: `predictive.run-record`, `current`, `converged`, `solver`, `balances`, `exchangers`,
  `formation-data`;
- fail: `predictive.coverage` (H301, E305, STM excluded), `model-basis` (U301, H301, D401
  specified), `property-regime`, and the earlier `sourced.boundary` and `balanced.model-basis`;
- unsupported: `energy-closure`.

Rejected:
- rescaling the natural gas feed so the product meets 100,000 Nm3/h: a design-basis choice for
  the owner, not a simulation fix;
- editing assumed values to silence the pressure deviations;
- keeping S15 and S19 at the script values: this breaks the V-201 and U-301 balances;
- leaving the dissolved CO2 in the boiler water: it would end up in the steam drum, whose
  outlets are pure water by D-010.

Open:
- accept or replace the PR substitution (owner);
- rescale the feed to the design capacity, or accept 99,640 Nm3/h;
- let-down valves after U-301;
- simulate H301, E305 and STM (convection coils as two-stream exchangers, as ammonia-1 does) and
  re-close the furnace and steam balances;
- a sourced check of the CO2 solubility at V-201;
- `cheme process props` covers none of the water-bearing streams.
