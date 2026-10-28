# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Iodine from natural iodide brine, issue ChemE-as-Code/process-library#145. Concept stage,
agent-drafted 2026-10-28, not reviewed. Numbers live in `process/*.yaml`, `lca/lca.yaml` and
`scripts/iodine_balance.py`; this file keeps the decisions and where each fact comes from.

## Run record (2026-10-28)

- Library: branch `case/iodine-1` from main `cc5624f`; cheme 0.8.0 (pyDEXPI 2.1.0); core
  checkout at `47c8fa39`. The core issues named in #145 (#364 electrolytes, #365 solids, #369
  extraction) are not reachable as `ChemE-as-Code/core#...` with `gh` (pre-release tracker);
  their state was checked only through what this core supports today: `cheme process
  electrolyte` covers aqueous NaCl only (no iodide, iodine, HI or acid liquors), `cheme process
  props --coverage` has no package for these streams, `cheme process simulate` was not used
  (D-007).
- Scope: route memo, design basis, balanced BFD/PFD, preliminary gate-to-gate LCI. Out of
  scope: P&IDs (none drawn; `pid/` holds only its README), layout, HAZOP, TEA, datasheets.

## Source register

| id | source | locator | read | reuse | used for |
|---|---|---|---|---|---|
| SRC-1 | Oklahoma Geological Survey, "Iodine" research page, https://www.ou.edu/ogs/research/minerals/iodine | sections on occurrence, production method, reinjection | read in this run (web page) | facts with citation | brine iodine above 300 ppm on average (Woodward trench, wells 7000-13000 ft); recovery by redox reactions in series of blow-out towers since 1977; product about 98 % as flake or prill; spent brine reinjected into the producing formation (D-001, D-003, D-009) |
| SRC-2 | US Bureau of Mines, Minerals Yearbook 1987, iodine chapter (p. 466 of the volume), https://search.library.wisc.edu/digital/APCUAWIWNUXSEF9A | Woodward brine paragraph | search-result extract read, not the full chapter | public-domain US government work | Woodward (Morrowan Formation, about 7500 ft) brine iodine averaging 300 ppm by weight (D-003) |
| SRC-3 | US 2013/0243684 A1, "Systems, methods, and apparatus for iodine removal from high volume dilute brine", https://patents.google.com/patent/US20130243684 | Background of the invention | Google Patents text read (machine summary) | patent: facts with citation | blow-out as the reference process for brines of about 300 mg/L and more; H2S removal, acidification, chlorination, air stripping, absorber with HI/H2SO4 and SO2, chlorinated slip-stream precipitating iodine, filtering, melting under concentrated H2SO4; lime before reinjection; at 90 % recovery about 30 mg/L iodine returned (D-001, D-004..D-006, D-009) |
| SRC-4 | US 4,282,324 A (Cetus, 1981), "Method for producing iodine", https://patents.google.com/patent/US4282324A/en | Background (conventional Michigan brine process) | read (machine summary) | patent: facts with citation | sequence clarification, H2SO4 acidification, slight chlorine excess, counter-current denuding tower, HI/H2SO4 absorption with SO2, partial bleed to a chlorination reactor, settling and filtering, melting under H2SO4 (D-004..D-006) |
| SRC-5 | US 1,897,031 A (Dow, 1933), "Recovering iodine from natural waters and the like", https://patents.google.com/patent/US1897031A/en | description and claims 1-6 | read (machine summary of OCR text) | patent (expired): facts with citation | acidification with H2SO4 to about pH 3 (the highest pH for complete liberation); chlorine equivalent to the iodine, controlled by oxidation potential (about 0.50-0.54 V at the end point); counter-current tower blowing removes 90-100 % of the free iodine without excessive air (D-004, D-005) |
| SRC-6 | US 9,994,448 B2 (2018), "Iodine extraction processes", https://patents.google.com/patent/US9994448B2/en | Background and definitions | read (machine summary) | patent: facts with citation | natural brines typically about 100 ppm iodine (the Oklahoma brines are richer); blow-out leaves acidified brine of pH 1-3 needing neutralisation (sodium hydroxide named) (D-004, D-009) |
| SRC-7 | chlor-alkali-1, sulfuric-acid-1 (this library), process/flowsheet.yaml products | CL2 (dry gas, 400 kPa(a)), NAOH (50 wt%), ACID (98.5 wt%) | read | own data | feed states and grades (D-002) |
| SRC-8 | NBS tables of chemical thermodynamic properties (Wagman et al. 1982, J. Phys. Chem. Ref. Data 11 Suppl. 2) | standard enthalpies of formation of the ions | values recalled, not re-read in this run | facts | heats of reaction in process/reactions.yaml, ASSUMED until checked (D-007) |
| SRC-9 | Iodine and Iodine Compounds, Ullmann's Encyclopedia (doi:10.1002/14356007.a14_381.pub2) | - | not read (licensed) | - | route reference lead only; no value taken |
| SRC-11 | Sander, R., Compilation of Henry's law constants (version 5.0.0), Atmos. Chem. Phys. 23 (2023) 10901-12440, doi:10.5194/acp-23-10901-2023; https://www.henrys-law.org/henry/casrn/7553-56-2 | iodine entry (CAS 7553-56-2) | web page read in this run | CC BY 4.0: facts with citation | Henry solubility of I2 at 298 K and its temperature dependence for the air ratio check (D-005) |
| SRC-10 | US EPA, "Identification and description of mineral processing sectors and waste streams: iodine" (archive.epa.gov ... id4-iod.pdf) | - | fetched, scanned image without text: not read | - | none; candidate source for waste streams in the next stage |

No figure, table or text was copied; the facts above are restated in our own words and units.
The held-out benchmark of the issue was not searched for.

## Basis table (sourced / proposed / missing)

| item | value | status |
|---|---|---|
| capacity | 125 kg/h iodine, 8000 h/a (1000 t/a) | proposed, ASSUMED (D-002) |
| brine iodine | 300 mg/kg as iodide | sourced (SRC-1, SRC-2, SRC-3) |
| brine salinity, alkalinity, temperature | 10 wt% NaCl, 2 meq/kg as NaHCO3, 313 K | ASSUMED (D-003); no open analysis found: missing |
| brine H2S, oil, solids, bromide, ammonium, organics | - | missing; removed at the wellhead or not modelled (D-003) |
| acidification | pH about 2.4 (ideal estimate) | proposed inside SRC-5 (pH 3 limit) and SRC-6 (pH 1-3) |
| chlorine | 5 % over stoichiometry, 98 % iodide oxidised | proposed: slight excess (SRC-4), redox end point (SRC-5); numbers ASSUMED |
| blowing-out | 92 % of free iodine, 130 Nm3/m3 | 92 % inside SRC-5's 90-100 %; air ratio ASSUMED; the sourced fresh-water Henry constant (SRC-11) gives only an upper bound of the stripping factor, chloride complexation open (D-005); gated sizing (D-007) |
| absorber | 99.5 % absorbed, 2 % SO2 excess, bleed 10 wt% HI | scheme sourced (SRC-3, SRC-4); numbers ASSUMED |
| precipitation and filter | 99.5 % HI oxidised, 99 % precipitated, cake 10 wt% liquor | scheme sourced (SRC-3, SRC-4); numbers ASSUMED |
| melting | under 98.5 wt% H2SO4, 0.2 kg/kg | scheme sourced (SRC-3, SRC-4); amount ASSUMED |
| overall recovery | 90.0 %, 29.8 mg/kg iodine left | calculated from the ASSUMED yields, which were chosen within sourced ranges so that the recovery equals SRC-3's 90 % (calibrated, not a check; D-006) |
| product | 99.8 wt% I2 | ASSUMED (SRC-1 quotes about 98 % for Oklahoma flake/prill) |
| neutralisation, reinjection | caustic to neutral, 3100 kPa(a) | reinjection sourced (SRC-1); caustic named in SRC-6; pressure ASSUMED |
| kinetics, tower sizes, vendor data, utility prices, site | - | missing |

## Method and dependency table

| calculation | method used | qualified by cheme? | gate |
|---|---|---|---|
| R-101, T-202, R-301, R-401 outlets | conversion model (specified conversions, process/reactions.yaml), element balances checked by cheme | yes (balance and extents); conversions specified, not predicted | none for a concept balance |
| T-201 blowing-out split, F-301, M-301 (step M301 included: specified, script values for S19/S20, although `cheme maturity` infers "equilibrium-stage, predictive, sourced" from its DEXPI class SeparatingByPhaseSeparation; a core inference to report) | specified splits (scripts/iodine_balance.py) | no (specified stream values) | an I2/Cl2/CO2 vapour-liquid model in acid chloride brine needs electrolyte support (core #364) |
| recycles (air loop, filtrate, spent acid) | successive substitution in scripts/iodine_balance.py; splitter and pass-throughs by `cheme process propagate --fill` | balances yes | - |
| solids (I2 crystals, cake, melt) | I2 carried as one component; state in the stream title | no | solids support (core #365) |
| stream enthalpies, energy closure | duties from hand enthalpy estimates (D-008); `cheme process energy`: not evaluable | no | no property package for these liquors (core #364); reactors declared adiabatic |
| LCI | `cheme assess lca` (gate-to-gate, backgrounds unmapped) | yes; mass and element balance closed | backgrounds to link (D-011) |
| solvent extraction / ion exchange alternatives | not used | - | core #369 only matters if extraction is chosen (D-001) |

## D-001 Route and boundary (2026-10-28)
Decision: iodine from a natural iodide brine (formation water of a deep brine field, Oklahoma
type) by the blowing-out process: acidification, chlorine oxidation, air blowing-out, absorption
with SO2 into HI/H2SO4, chlorine precipitation, filtration, melting under sulfuric acid,
flaking. Boundary: brine at the plant battery limit (wellfield, wellhead degassing/de-oiling
outside), spent brine to the reinjection wells (outside), chlorine and caustic from chlor-alkali-1,
sulfuric acid from sulfuric-acid-1, SO2 purchased, utilities from the site.
Reason: the brine route has an open, consistent process description in several patents
(SRC-3..SRC-6) and a sourced feed iodine content (SRC-1, SRC-2), and maps directly onto the case
notes' steps (oxidation, blowing-out, absorption, reduction, crystallisation). The case notes
ask for the sourced one of caliche or brine; brine is the one whose feed composition (iodine)
is sourced here.
Rejected: (1) caliche (Chile): iodate leaching, bisulfite reduction and iodate/iodide
comproportionation; heap leach and solution compositions not found in open primary sources in
this run, and the solids/heap system is further from what core models. (2) Ion-exchange or
activated-carbon recovery of brine iodine (SRC-5 uses charcoal): suited to dilute brines; the
Oklahoma brines at about 300 mg/kg are the reference case for blowing-out (SRC-3). (3) Solvent
extraction (core #369): not needed for this route.
Assumptions: the brine is degassed and de-oiled at the wellhead; H2S removal (SRC-3 names it)
is outside the boundary or unnecessary for a sweet brine (open input).

## D-002 Capacity, feeds and product (2026-10-28)
Decision: 125 kg/h iodine flakes, 8000 h/a (1000 t/a), 99.8 wt% I2 with the impurities lumped
as water. Chlorine as chlor-alkali-1 product CL2 (dry gas, 400 kPa(a)); caustic 50 wt% as
chlor-alkali-1 NAOH; sulfuric acid 98.5 wt% as sulfuric-acid-1 ACID (SRC-7); SO2 as purchased
liquid (no library producer; sulfur burning as in sulfuric-acid-1 is the usual source).
Reason: a normalisation basis of the order of one brine plant, not a commercial claim; the
product grade is the usual commercial minimum for refined iodine (ASSUMED), above the about 98 %
SRC-1 quotes for Oklahoma flake/prill. Downstream library uses: hydrogen iodide (#149),
iodomethane (#163).
Assumptions: capacity, hours, purity ASSUMED.

## D-003 Brine composition (2026-10-28)
Decision: 300 mg/kg iodine as iodide (carried as NaI), 10 wt% NaCl, alkalinity 2 meq/kg (as
NaHCO3), 313.15 K, 300 kPa(a) at the battery limit.
Reason: 300 ppm is the sourced average of the Woodward trench brines (SRC-1, SRC-2) and the
threshold above which SRC-3 calls blowing-out the reference. No open analysis of these brines'
salinity, alkalinity or temperature was found: they are ASSUMED (formation waters at this depth
are typically saline and warm). The alkalinity matters for the acid demand and makes the plant's
only CO2 emission.
Rejected: a seawater-type or Japanese gas-field brine (about 100 ppm, SRC-6): no sourced
composition of a specific field obtained.
Assumptions: NaCl, alkalinity and temperature ASSUMED; bromide, ammonium, organics, metals not
modelled (bromide would consume chlorine and be co-stripped: open input).

## D-004 Acidification and chlorination (R-101) (2026-10-28)
Decision: the brine is acidified only by the plant's recycled acid liquors (filtrate S16 and
spent melter acid S19: HCl, H2SO4 and residual HI) and chlorinated with 5 % chlorine over the
iodide (plus recycled HI) stoichiometry; 98 % of the iodide oxidised (OXI, OXH1); the alkalinity
is neutralised completely (ALK).
Reason: SRC-5 sets pH 3 as the upper limit for complete liberation and controls chlorine by
oxidation potential; SRC-4 says a slight excess; SRC-6 reports blow-out effluent at pH 1-3. The
recycled acids give 3.8 mmol free H+/kg, pH about 2.4 (ideal, scripts/iodine_balance.py), so no
separate fresh acid is needed at this brine iodine level; fresh acid enters only through the
melter (D-006). A brine with more alkalinity or less iodine would need fresh acid here (open).
Rejected: dosing fresh H2SO4 to the brine head (not needed by this balance; kept as the
operating fallback).
Assumptions: excess chlorine ASSUMED to stay as Cl2 and be stripped (not hydrolysed or consumed
by brine reductants); 2 % unoxidised iodide ASSUMED; over-chlorination to iodate/ICl not
modelled.

## D-005 Blowing-out and absorption (T-201, T-202, K-201) (2026-10-28)
Decision: a packed blowing-out tower strips 92 % of the dissolved iodine, all of the excess
chlorine and all CO2 into 130 Nm3 dry air per m3 brine (56 000 Nm3/h), saturated with water at
313 K (6.8 mol%). The air circulates in a closed loop through the absorber and the fan K-201;
5 % of the absorber exit gas is purged to the vent and replaced by dry make-up air. The absorber
takes up 99.5 % of the iodine into a circulating HI/H2SO4 liquor with 2 % excess SO2 (ABS) and
reduces the chlorine slip completely (CLSA); a bleed at 10 wt% HI goes to precipitation.
Reason: tower blowing and the HI/H2SO4-SO2 absorber with bleed are the sourced scheme (SRC-3,
SRC-4); 92 % lies in SRC-5's 90-100 %. Air ratio check (SRC-11): iodine's Henry solubility
about 3.0e-2 mol/(m3 Pa) at 298 K with d ln H/d(1/T) about 4400 K gives 1.5e-2 at 313 K, a
dimensionless gas/liquid ratio of about 0.026, and with 130 Nm3/m3 (144 m3/m3 at 313 K and
105 kPa(a)) a stripping factor of about 3.7 in fresh water. This is an upper bound, not a
confirmation: salting-out raises the volatility, but two effects lower the free I2 and so the
stripping factor, the I3- complex with the residual iodide and the chloride complex I2Cl- in a
brine with about 1.9 mol/kg chloride. The I2Cl- formation constant is not sourced in this run;
if it is of the order of 1-2 kg/mol (the 2026-10-28 review's estimate, to be verified) the
stripping factor falls to about 1, and a factor near 1 cannot give 92 % at any number of
stages. The air ratio is therefore an open, ASSUMED value: its sizing is gated with T-201
(D-007). Sensitivity: at twice the air ratio K-201 needs about 200 kW at the same 4 kPa rise
(more with the higher tower pressure drop), adding about 0.8 kWh/kg to the 4.8 kWh/kg of
power (+17 %). The closed loop keeps the iodine and chlorine emissions small; the purge
carries out the CO2 and water.
Open check (T-202): 30 m3/h of absorbent in a tower of roughly 3 m diameter for about
62 000 m3/h of loop gas is a wetting rate of about 4 m3/(m2 h), below the usual minimum for
random packings. When T-202 is sized, raise the circulation (P-202 power, 4 kW, scales with
it) or choose a packing or contactor suited to low liquid rates; the balance is unaffected.
Rejected: once-through air (larger iodine slip to air); activated carbon adsorption (SRC-5)
for this concentration.
Assumptions: stripping fraction, air ratio, purge fraction, absorption fraction, SO2 excess,
bleed strength, isothermal loop at 313 K, no water exchange in the absorber: all ASSUMED.

## D-006 Balance method, precipitation, filtration and melting (2026-10-28)
Decision: an independent sequential balance, `scripts/iodine_balance.py` (run with `cheme run`),
solves the plant at 1 t/h brine with the recycles by successive substitution and scales it to
the product rate (the plant is linear in the brine flow). Its results are given in
process/flowsheet.yaml as ASSUMED values; `cheme process propagate --fill` fills the splitter
and pass-through streams; cheme checks every step's mass and element balance. R-301 oxidises
99.5 % of the bleed's HI with chlorine (OXH2) and all excess SO2 first (CLSB); 99 % of the
iodine precipitates; the filter cake holds 10 wt% mother liquor; filtrate returns to the brine
head (recovering its dissolved iodine and HI). The cake is melted under 98.5 wt% sulfuric acid
(0.2 kg H2SO4/kg iodine), which takes up the water and acids of the cake; the spent acid
returns to the brine head as its acid make-up.
Reason: the scheme is sourced (SRC-3, SRC-4); returning the acid liquors to the brine head
closes the acid and iodine loops (no liquid waste besides the spent brine).
Result: overall recovery 90.0 %, 29.8 mg/kg iodine in the spent brine. This is calibrated, not
a check: the yields (98 % x 92 % x 99.5 % x 99.5 % x 99 %, with the recycles) were chosen within
sourced ranges so that the overall recovery equals the 90 % that SRC-3 states, and the
29.8 mg/kg then follows from 300 mg/kg x (1 - 0.90). Plant in 466 939.4 kg/h = out
466 939.4 kg/h.
Assumptions: all yields, cake moisture and acid ratio ASSUMED; the iodine solubility in the
mother liquor (triiodide) is represented by the 1 % that stays dissolved; melter vent (HCl,
iodine vapour) not modelled (LCI exclusion).

## D-007 Thermodynamic and reaction model basis (2026-10-28)
Decision: liquors are carried as neutral molecules in water (NaI, NaCl, HI, HCl, H2SO4, Na2SO4,
NaHCO3, NaOH, I2, Cl2, SO2, CO2): an inventory basis, not a speciation. All reactions are
fast ionic redox or neutralisation reactions run to an end point, modelled by specified
conversions (a conversion model with sourced ranges where sources exist); no kinetics. Heats of
reaction from NBS formation enthalpies of the ions (SRC-8, recalled, ASSUMED until checked).
No property package; energy closure not evaluated in core.
Reason: core supports no electrolyte system beyond aqueous NaCl (`cheme process electrolyte`)
and no solids (core #364, #365, as of core `47c8fa39`); I-/I2/I3-, Cl2/HOCl and HSO4-
equilibria would be needed for a predictive model.
Rejected: forcing an equation-of-state package on these streams (outside any validated range).
Gated step: a predictive T-201/T-202 model (stripping fraction and air ratio, with the I3- and
I2Cl- complexes, D-005) and the energy balance wait for electrolyte support (core #364) and
solids (core #365); until then the specified values stand, labelled.

## D-008 Conditions, duties and utilities (2026-10-28)
Decision: the brine section runs at 313 K (brine temperature); towers near atmospheric
(T-201 104-106 kPa(a), T-202 102-104); chlorine at 400 kPa(a). Power: K-201 100.3 kW (4 kPa
rise, efficiency 0.70), P-401 479.7 kW (3000 kPa rise, 0.75), P-202 4.2 kW (30 m3/h, 300 kPa,
0.60), recovery drives 15 kW lumped. LP steam 450 kPa(a) to the melter 8.1 kW (heating the cake
to 393 K, fusion of iodine about 61 kJ/kg, heating the acid, with 50 % losses); flaker 2.8 kW to
cooling water 298/308 K. Reactors adiabatic (process/simulation.yaml): reaction heats are below
0.1 K in the brine and about 6 K in R-301.
Reason: concept estimates from hand enthalpy balances (scripts/iodine_balance.py); the
reinjection pump dominates the power (80 %) and its pressure is the least known value.
Assumptions: every pressure, efficiency and duty ASSUMED; wellfield lifting power is outside the
boundary (in the brine background, D-011).

## D-009 Spent brine neutralisation and reinjection (2026-10-28)
Decision: the stripped brine's strong acid (H2SO4, HCl, traces of HI) is neutralised with 50 wt%
caustic to neutral (NEU1-3, 71 kg/h NaOH) and pumped back into the formation (SRC-1).
Reason: SRC-6 names sodium hydroxide for neutralising the acid effluent and chlor-alkali-1 makes
it; SRC-3 names lime. Caustic avoids gypsum in a sulfate-bearing brine near the injection wells.
Rejected: lime (cheaper; CaSO4 scaling risk, open comparison).
Assumptions: dissolved iodine left as I2 in the inventory (in reality it disproportionates to
iodide/iodate at neutral pH; same element balance); the injection pressure is ASSUMED.

## D-010 Lists (2026-10-28)
Decision: equipment list with the 11 items the PFD links (R-101, T-201, T-202, P-202, K-201,
R-301, F-301, M-301, X-301, R-401, P-401), ASSUMED design conditions (operating + 10 %, at least
+2 bar; +25 K over the operating temperature, or over the heating medium where that is hotter:
M-301 at 175 °C against its 450 kPa(a) steam jacket) and first-choice non-metallic or lined materials for wet chlorine and acid
iodide liquors. No line or instrument list (no P&ID at this stage). P-401 uses the DEXPI class
TransportingFluids: `cheme process build` (core 0.8.0) fails on the class Pumping (its pyDEXPI
method field is a Union; core finding, to be reported).

## D-011 Preliminary gate-to-gate LCI (2026-10-28)
Decision: `lca/lca.yaml` with functional unit 1 kg iodine flakes at the gate, gate-to-gate,
case design, no allocation (single product). Every foreground exchange comes from the balanced
flowsheet. Backgrounds are left unmapped; each `missing:` names the activity to connect, so the
published gap list (gaps.csv, dataset) says what each gap needs: brine
wellfield, chlorine and caustic (chlor-alkali-1), sulfuric acid (sulfuric-acid-1), SO2,
process water, electricity, LP steam, cooling water, reinjection. Make-up air free; vent N2, O2
and water vapour free; vent CO2 elementary (air, fossil: geogenic carbon of the formation's
bicarbonate, ASSUMED via the alkalinity); vent iodine elementary (air), uncharacterised by the
climate method (a reported gap). Spent brine classified as waste for reinjection, not as an
emission to water, because it returns to the formation.
Result (per kg iodine): brine 3695.5 kg, chlorine 0.614 kg, SO2 0.281 kg, sulfuric acid
(98.5 wt%) 0.203 kg, caustic (50 wt%) 1.137 kg, process water 8.90 kg, air 28.9 kg, power
4.79 kWh, LP steam 0.065 kWh; spent brine 3704.0 kg, vent 30.5 kg (CO2 0.325 kg, I2 0.25 g),
cooling water 0.022 kWh. `cheme assess lca --balance`: mass and every element closed (largest
residual S 0.01 %), carbon origin closed. Result class: partial screening (10 exchanges
without background, the iodine emission outside the method).
Excluded (open gaps, not negligible by evidence): equipment leaks, the melter vent, storage and
unloading vents; construction, transport and end of life are outside this preliminary LCI.

## D-012 Maturity claim (2026-10-28)
Decision: claim `concept` (the manifest's lowest level); `cheme maturity` supports none, because
the feed flows are design choices (ASSUMED) and every reactor/separator rests on specified
values. Same situation as aniline-1 and chlor-alkali-1. Raising it needs a sourced brine
analysis and sourced or predicted yields (D-007 gate).

## Missing entries of the chemicals registry (for the consolidated PR)

`chemicals/chemicals.yaml` has no entry for: iodine (main product, CAS 7553-56-2, a flake grade
99.8 wt%), chlorine (CAS 7782-50-5), sodium hydroxide (50 wt% solution), sulfuric acid
(98.5 wt%), sulfur dioxide (CAS 7446-09-5, liquid), and natural iodide brine / spent brine (if
the Atlas is to list them). Existing slugs used: water, wastewater, electricity, steam,
cooling-water.
