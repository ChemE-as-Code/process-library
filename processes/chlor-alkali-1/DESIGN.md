# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/balance.py`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#121.

Run record of this stage (2026-10-27): library branch `case/chlor-alkali-1` from `79a7cd4`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core#366 (electrochemical
cell, merged as core PR #396) is in this cheme: `process/cells.yaml` and `cheme process cell`
are used. Core PR #394 (`cheme process electrolyte`, Pitzer brine properties) is **not** in the
installed 0.8.0 (`No such command 'electrolyte'`), so the water activity of the brine is an
estimate (D-007). Core#364 (electrolyte/caustic thermodynamics) remains the gate for stream
enthalpies.

"BREF" below is: European Commission JRC (2014), *Best Available Techniques (BAT) Reference
Document for the Production of Chlor-alkali*, DOI 10.2791/13138, read in full text for the
locations cited (facts and numbers only, in our own words; no tables or text copied).

## 1. Route and boundary memo

- **Route**: membrane-cell electrolysis of sodium chloride brine with brine recirculation
  (issue #121: membrane, not mercury or diaphragm). 2 NaCl + 2 H2O -> Cl2 + H2 + 2 NaOH,
  driven by direct current; one electrochemical step, three products in fixed ratio.
- **Boundary of this case: saleable products** (D-001). From rock salt, water, chemicals,
  electricity and steam to dry compressed chlorine gas (400 kPa(a)), 50 wt-% caustic soda and
  wet low-pressure hydrogen. Inside: salt saturation, primary purification (precipitation,
  filtration), secondary purification (chelating ion exchange), feed-brine acidification and
  heating, transformer-rectifiers, electrolysers, catholyte loop, depleted-brine dechlorination
  (vacuum and sulfite), brine purge, wet chlorine cooling, sulfuric-acid drying and
  compression, hydrogen cooling and blower, double-effect caustic evaporation and cooling.
  Outside: chlorine liquefaction and storage, the chlorine absorption (hypochlorite) unit
  (start-up and upsets only), HCl synthesis, hydrogen drying and compression, storage,
  effluent treatment, utility generation.
- **Cell-room boundary** (the issue's second boundary) is a subset: block ELY alone (feed
  brine and DM water in; anolyte, wet Cl2, wet H2 and 32 wt-% caustic out; DC 2 351 kWh/t Cl2).
  Its electricity and steam intensities are **not** comparable with the saleable-product
  figures (2 600 kWh and 0.98 t steam per t Cl2): the issue's guardrail.
- **What crosses the boundary**: SALT, WATER, DMW, NA2CO3, HCL, NA2SO3, H2SO4 (raw
  materials), POWER, MPS (utilities in), CL2, NAOH, H2 (co-products), SPENT (by-product),
  WW (wastewater), SLUDGE (solid waste), VENT (emission), CW, CHW (utilities out).
- **Normalisation**: per unit of contained Cl2 (issue #121), NaOH on a 100 % basis, H2
  separately; the dataset is unallocated, the study allocates by the mass of the contained
  products (D-013).

## 2. Decisions

## D-001 Boundary: saleable products, gas chlorine, no liquefaction (2026-10-27)
Decision: the boundary of section 1; chlorine leaves as dry gas at 400 kPa(a) to an adjacent
consumer. Reason: the issue asks for an explicit product boundary and leaves liquefaction
open; a pipeline consumer (e.g. EDC) is the common integrated case and avoids the
refrigeration and tail-gas system whose data we do not have. Rejected: liquid chlorine
(adds about 50 kWh/t Cl2 liquefaction, BREF Table 3.12, and a tail gas with the O2); a
cell-room-only boundary (does not give saleable products). Assumptions: the consumer takes
Cl2 with 1.8 vol-% O2.

## D-002 Capacity and product states (2026-10-27)
Decision: 100 kt/a contained Cl2 at 8000 h/a = 12 500 kg/h; 50 wt-% caustic to storage;
hydrogen wet at 140 kPa(a). Reason: a mid-size single-site membrane plant; numbers chosen,
not a client figure (ASSUMED). Caustic 50 wt-% is the commercial grade (BREF 3.3.4.4).

## D-003 Salt: rock salt with brine recirculation (2026-10-27)
Decision: rock salt NaCl 98.8, CaSO4 0.15, MgCl2 0.05, insolubles (as SiO2) 0.5, moisture 0.5
wt-% (ASSUMED analysis). Reason: rock salt needs the full purification train the issue asks
for; vacuum salt would make primary purification optional (BREF 3.3.2). Rejected: vacuum salt
and solution-mined brine (open alternatives); once-through brine. Assumptions: no bromide,
iodide, Sr, Ba, Fe, Al or organics in the model; a real analysis is an open input.

## D-004 Cell technology and performance (specified, not predicted) (2026-10-27)
Decision: bipolar zero-gap membrane cells, 6.0 kA/m2, 3.0 V, 90 degC, catholyte 32 wt-% NaOH,
anolyte 200 g/l NaCl: the conditions BREF 4.3.2.3.2 gives for high-performance membranes.
Current efficiency 0.965 for the overall reaction (ASSUMED inside BREF 2.4.1, loss 3-7 % to
caustic, and 4.3.2.3.2, > 95 %); the remaining 3.5 % of the current forms O2 at the anode from
back-migrated hydroxide (side reaction WATER_SPLIT, net 2 H2O -> 2 H2 + O2), which gives
1.8 vol-% O2 in the chlorine, inside BREF 2.4.1 (0.5-2.0 vol-%). 605 elements of 2.7 m2 in
one DC circuit (ASSUMED; the split into electrolysers is a vendor input). One circuit would
run at about 1.8 kV DC and 16.2 kA; plants of this size usually split the cell room into
several electrolysers, each with its own rectifier. The number of electrolysers and
rectifiers (T-301) is open; it changes the equipment count, not the per-kg figures (review
2026-10-27-pfd-lci-review#9). Checked by
`cheme process cell`: Cl2 12 502 kg/h formed, NaOH 14 104 kg/h, H2 368 kg/h, DC 29 382 kW,
thermoneutral voltage 2.310 V, isothermal heat 7 041 kW. Rejected: anolyte acidification with
HCl (would raise the Cl2 efficiency above the NaOH efficiency; needs vendor data); a
polarisation model (not supported, no data). Assumptions: hypochlorite and chlorate
formation and chloride transfer to the caustic (~50 mg/l, BREF 2.4.1) are neglected; one
efficiency for Cl2 and NaOH (cheme's limitation, documented in core).

## D-005 Brine circuit, purification, dechlorination and purge (2026-10-27)
Decision: feed brine 26 wt-% NaCl (about 310 g/l, BREF 2.5.2: 310-315 g/l) and 6 g/kg Na2SO4
(about 7 g/l, inside BREF Table 2.4: < 4-8 g/l, vendor limit open); depleted brine 17.7 wt-%
(200 g/l). Water transported through the membrane 4.0 mol per mol Na+ (BREF 2.4.1: 3.5-4.5).
Ca precipitated with soda ash (stoichiometric + 0.5 g/kg excess, ASSUMED), Mg with the
plant's own caustic (stoichiometric + 0.3 g/kg, ASSUMED); filter cake 50 wt-% solids
(ASSUMED); chelating ion exchange regenerated with 1.0 kg HCl/t Cl2 and equimolar NaOH and
0.15 t DM rinse water/t Cl2 (ASSUMED). The feed brine is acidified with HCl to neutralise the
excess carbonate (CO2 vented) and hydroxide. Depleted brine (0.7 g/l dissolved Cl2, BREF
2.5.4: 0.4-1 g/l) plus the chlorine-water condensate is acidified to pH ~2 with 0.010 mol
HCl/kg (BREF 2.5.4: pH 2-2.5), stripped at 55 kPa(a) to 20 mg/kg (BREF 2.5.4: 50-60 kPa,
10-30 mg/l), the recovered chlorine returns to the wet chlorine header; the residue is
destroyed with stoichiometric Na2SO3 and the acid neutralised with caustic. Sulfate is
controlled by a purge of dechlorinated brine (4.25 % of it, 0.33 t/t Cl2), set so that the
feed brine holds 6 g/kg Na2SO4. Process condensate from the evaporator and the hydrogen
condensate go to the saturator (BREF 4.3.2.2.3). Rejected: BaCl2 (toxic, BREF Table 3.6),
nanofiltration (an option to lower the purge and the salt loss; next stage). Assumptions: the
four treatment steps are adiabatic (simulation.yaml): their heats are small.

## D-006 Balance method: independent script, cheme checks (2026-10-27)
Decision: all flows, compositions and duties come from `scripts/balance.py` (`cheme run
scripts/balance.py`), a specified-split model: cell from Faraday's law, a Newton solve of the
brine loop for salt, make-up water and purge fraction, a recycle of the stripped chlorine and
an outer loop on the chlorine formed. The values are written into `process/flowsheet.yaml`
as ASSUMED with the script as source. cheme checks them: every block and step closes in mass
and, where reactions are named, in elements and extents (`cheme process streams`); the cell
is recomputed by `cheme process cell` and agrees (extents 176.317 kmol/h, Q2 = cell power).
Duties outside the cell use constant heat capacities (brine 3.3, 32 % caustic 3.5, 50 %
caustic 3.2, water 4.18 kJ/(kg K)) and latent heats of water (IAPWS), ASSUMED; heats of
dilution of NaOH are left out. Rejected: DWSIM (no electrolyte package, core#364). Gated:
energy closure of every step (`cheme process energy`: not evaluable, no stream enthalpies);
the evaporator duty and the cell heat split.

## D-007 Temperatures, pressures and gas saturation (2026-10-27)
Decision: saturated brine 55 degC, feed brine 70 degC, cells 90 degC; anode gas 115, cathode gas
117 kPa(a) (ASSUMED). Wet chlorine leaves saturated with water over the depleted brine: water
activity 0.876 from an osmotic coefficient of 1.0 at 3.7 mol/kg (ASSUMED) and 70.18 kPa
vapour pressure of water at 90 degC (IAPWS) -> 22.8 wt-% water, 290 kg condensate per t Cl2
(BREF 4.3.2.2.3 reports about 200 kg/t when cooling from 85 degC, consistent with the lower
temperature). Hydrogen leaves with 28 kPa water partial pressure over 32 wt-% caustic
(ASSUMED; no NaOH activity model) -> 69 kg condensate per t Cl2 at 35 degC, inside BREF
4.3.2.2.3 (50-100 kg/t). Chlorine-water condensate holds 7 g/kg Cl2 (ASSUMED). Gated: brine
water activity by `cheme process electrolyte` once the installed cheme has core PR #394.

## D-008 Chlorine and hydrogen treatment (2026-10-27)
Decision: wet chlorine cooled to 40 degC on cooling water and 20 degC on chilled water (above
the 15 degC hydrate limit, BREF 4.3.4), dried with 98 wt-% sulfuric acid leaving at 75 wt-%
(ASSUMED; 18.7 kg H2SO4/t Cl2, BREF Table 3.7 range 3.5-51), compressed in two intercooled
stages to 410 kPa(a) at isentropic efficiency 0.75 (discharge 114 degC, below the 120 degC limit
of BREF 4.3.4) and cooled to 40 degC. Hydrogen cooled to 35 degC and blown to 140 kPa(a)
(efficiency 0.70). Spent acid goes to off-site use (BREF 4.3.4: most EU plants report no
sulfuric acid waste). No Cl2 or H2 vented in normal operation. Rejected: chlorine
liquefaction (D-001). Open: dry-chlorine water specification, compressor type.

## D-009 Electricity (2026-10-27)
Decision: transformer-rectifier efficiency 0.97 (ASSUMED): 30 290 kW AC for 29 382 kW DC,
2 423 kWh AC/t Cl2, inside BREF Table 3.10 (bipolar 2 279-2 865). All other consumers: 177
kWh/t Cl2, the BREF Table 3.12 median for all electrical equipment except cells and
liquefaction; the calculated compressor (246 kW) and blower (45 kW) are part of it, the rest
(1 922 kW) covers pumps, agitators, fans, vacuum and the chiller (ASSUMED). Total 2.60
kWh/kg Cl2.

## D-010 Steam, cooling and caustic evaporation (2026-10-27)
Decision: MP steam 1000 kPa(a) (BREF Table 3.11 median 10 bar); double-effect falling-film
evaporation 32 -> 50 wt-% with steam economy 1.8 (ASSUMED): 8.75 t/h steam = 0.625 t/t NaOH
(BREF Table 3.11, membrane: 0.46-1.5, median 0.70). Feed brine heating 55 -> 70 degC: 3.5 t/h
= 0.28 t/t Cl2 (BREF Table 3.12: 0.08-1.27, median 0.23). Cooling water 25/35 degC, chilled
water 8/15 degC (ASSUMED). The cell's isothermal heat (7.04 MW) leaves with the products:
2.62 MW heats the feed brine 70 -> 90 degC, 0.71 MW the DM water, 3.00 MW evaporates the water
in the cell gases; the remaining 0.72 MW is the catholyte cooler E-302 (scripts/balance.py).

## D-011 Materials (screening only) (2026-10-27)
Decision: wet chlorine and chlorine water titanium or lined; dry chlorine carbon steel
below 120 degC; caustic above about 40 wt-% and hot caustic nickel; strong sulfuric acid
lined steel (the service split of the skill tech-heavy-chem-chlor-alkali). ASSUMED, for the
equipment list only; a materials engineer decides.

## D-012 Equipment design conditions (2026-10-27)
Decision: concept design pressure and temperature in the equipment list: operating + 10 % (at
least + 2 bar g) and + 25 K (ASSUMED rule); no sizes, no datasheets at this stage.

## D-013 Preliminary gate-to-gate LCI, mass allocation on contained products (2026-10-27, revised 2026-10-27)
Decision: `lca/lca.yaml`: functional unit 1 kg of contained Cl2 in the dry gas product
(1.008185 kg of product gas), gate-to-gate, case design, every foreground exchange of the
flowsheet. `lca/dataset.yaml` stays unallocated. The study allocates by the mass of the
contained products, Cl2 : NaOH (100 %) : dry H2 = 1 : 1.120 : 0.0295 kg, given as `shares`
(Cl2 46.53 %, NaOH 52.10 %, H2 1.37 %) with an `allocation.deviation`. Reason: the library
build cannot export `none` for a multi-output dataset (CI of PR #194); the hierarchy's price
ratio (ADR 0007, step 3) needs prices we have not sourced; and core's `mass` method weighs the
product streams including the water of the 50 wt-% caustic and the wet hydrogen (it gives Cl2
30.6 % instead of 46.5 %, review 2026-10-27-pfd-lci-review#1). Any later mass allocation must
use the contained products, never product-stream mass. Rejected: `none` (not exportable);
`mass` (counts solvent water); economic (no sourced prices); substitution (no open
substitutes). A later study may choose another basis (the electrochemical unit, economic) and
must not credit H2 a second time upstream (issue #121). CO2 from soda-ash neutralisation is an
elementary flow (air, fossil origin) characterised directly; NaCl and Na2SO4 are elementary
flows to fresh surface water (`elementary: {compartment: water, subcompartment: fresh-surface}`;
before 2026-10-27 `missing:`, which left them labelled as air emissions in the dataset). No open
characterisation is packaged for them, so they stay uncharacterised in the results; the library
build links them as dissolved solids by mass (lci/mappings.yaml biosphere). Every background is declared `missing:` with the
activity it should link to (no values from licensed databases, no 0). Brine purge and resin
effluent are discharged after dechlorination and neutralisation: their NaCl and Na2SO4 are
emissions to fresh water; CO2 from soda-ash neutralisation is mineral (counted as fossil).
Spent acid is a recyclable (re-use) under cut-off. Declared exclusions: non-routine Cl2/H2
vents, tank breathing, fugitive leaks and effluent traces (chlorate, free chlorine, bromate,
AOX, metals), with the BREF ranges as orders of magnitude. Construction, transport and end of
life are outside this inventory.

## 3. Reaction and model evidence

| model element | basis | status |
|---|---|---|
| Overall cell reaction, n = 2 | stoichiometry; Faraday constant (CODATA 2018) | exact |
| Heat of reaction 445.79 kJ/mol | CODATA Key Values (Cox et al. 1989), aqueous ions at infinite dilution; U_tn 2.310 V | sourced; no heats of dilution (core#364) |
| Cell voltage 3.0 V at 6.0 kA/m2, 90 degC | BREF 4.3.2.3.2 | sourced point value, specified (not predicted) |
| Current efficiency 0.965, rest to O2 | BREF 2.4.1 (loss 3-7 %, O2 0.5-2.0 vol-%), 4.3.2.3.2 (> 95 %) | ASSUMED inside sourced ranges |
| Water transport 4.0 mol/mol Na+ | BREF 2.4.1 (3.5-4.5) | sourced range, midpoint chosen |
| Precipitation, neutralisation, sulfite dechlorination | stoichiometry (BREF 2.5.3, Table 3.6 for their use) | complete conversion, specified |
| Vacuum dechlorination | BREF 2.5.4 (pH 2-2.5, 50-60 kPa, 10-30 mg/l residual) | specified split |
| Drying, condensation, evaporation | water vapour pressure (IAPWS), acid strengths ASSUMED | specified splits |

No kinetics are needed or invented: the cell is electrochemically driven at a specified
current; the treatment reactions are fast ionic reactions modelled as complete.
Plausibility against BREF Chapter 3 (EU plants 2008-2011, a range check, not validation):
salt 1.71 t/t Cl2 (Table 3.2: 1.61-2.34; stoichiometric 1.65), AC for electrolysis 2 423 kWh/t
(Table 3.10 bipolar 2 279-2 865), auxiliaries 177 kWh/t (Table 3.12 median), steam 0.625 t/t NaOH
(Table 3.11 median 0.70), HCl 10.9, Na2CO3 7.7, Na2SO3 0.28, NaOH (internal) 8.5, H2SO4 18.7
kg/t (Table 3.7 ranges 5.8-56, 0.3-39, 0.02-4.2, 7.1-55, 3.5-51), purge 0.33 m3/t (Table 3.5
median 0.33), filter cake 21.9 kg/t (Table 3.2 rock salt 15-45), sulfate 2.0 kg SO4/t (Table 3.2:
0.065-7.4).

## 4. Source register

| source | locator | access | reuse | used for |
|---|---|---|---|---|
| EU JRC (2014) Chlor-alkali BREF, DOI 10.2791/13138, https://publications.jrc.ec.europa.eu/repository/bitstream/JRC91156/cak_bref_102014.pdf | 2.4.1; 2.5.2; 2.5.3.3 Table 2.4; 2.5.4; 3.3 Tables 3.2-3.7, 3.10-3.12; 4.3.2.2.3; 4.3.2.3.2; 4.3.4 | full text read (PDF) | EU publication, reuse with acknowledgement; facts only, our own wording | cell conditions, brine limits, dechlorination, consumption ranges |
| Schmittinger et al. (2011) Chlorine, Ullmann's, DOI 10.1002/14356007.a06_399.pub3 | sections 7, 11, 13 (issue notes) | not read in this run | licensed; not used for numbers | background reading only; not in `process.yaml` references (nothing rests on it) |
| Cox, Wagman, Medvedev (1989) CODATA Key Values for Thermodynamics | H2O(l), Na+, Cl-, OH- (aq) | standard values | facts | heats of reaction |
| IAPWS-IF97 saturation properties | water at 20, 35, 40, 90 degC; 1000 kPa | standard values | facts | gas saturation, latent heats |
| skill tech-heavy-chem-chlor-alkali (Speight 2002; Ray and Das 2020) | units in flow order, materials split | library skill | summary | unit sequence, D-011 |

## 5. Methods and core dependencies

| step | method | status |
|---|---|---|
| mass, component, element balances | cheme validate / process streams | done, all 7 blocks and 22 steps close |
| cell balance | cheme process cell (core#366, PR #396) | done; specified performance |
| brine properties (water activity, vapour pressure, heats of dilution) | `cheme process electrolyte` (core PR #394) | **gated**: not in installed cheme 0.8.0; estimate used (D-007) |
| caustic (NaOH-H2O) properties, Cl2 solubility, salt saturation | core#364 | **gated**: unsupported; specified values (D-006, D-007) |
| energy closure outside the cell | cheme process energy | **gated** by core#364: not evaluable (no stream enthalpies) |
| DWSIM simulation | cheme process simulate | not applicable (no electrolyte package) |
| LCI | cheme assess lca --inventory / --coverage | done; partial (all backgrounds unmapped by design) |

`cheme maturity` reports level none (the manifest claims concept, its lowest level): feed
flows are design choices, not sourced data, and the treatment steps are specified values.

## 6. LCI summary (unallocated, per kg contained Cl2)

The figures below are the unallocated plant inventory divided by the Cl2 output.
`lca/inventory.csv` and `lca/results.md` carry Cl2's allocated share (46.5 %, D-013): e.g.
rock salt 0.796 kg instead of 1.711 kg.

Inputs: rock salt 1.711 kg, process water 0.930 kg, DM water 1.124 kg, soda ash 7.70 g, HCl
32 wt-% 33.9 g (10.9 g HCl), Na2SO3 0.28 g, H2SO4 98 wt-% 19.1 g, electricity 2.600 kWh, MP
steam 0.549 kWh (0.98 kg steam). Outputs: Cl2 gas 1.008 kg (1 kg Cl2), caustic 50 wt-% 2.240
kg (1.120 kg NaOH), hydrogen gas 43.4 g (29.5 g H2), spent acid 24.8 g, wastewater 0.486 kg
(NaCl 57.4 g, Na2SO4 2.9 g), filter cake 21.9 g, CO2 2.36 g, cooling-water heat 0.865 kWh,
chilled-water heat 0.012 kWh. Mass, element and carbon balances close (`cheme assess lca
--coverage`); in 3.795 kg = out 3.795 kg per kg product gas, the flowsheet's 47 830 kg/h
over 12 602 kg/h. Classification: partial (14 gaps: every background declared missing).
The only characterised exchange is the mineral CO2 (1.1 g CO2-eq per kg Cl2 after
allocation). The climate figure in `lca/results.md` is therefore that CO2 alone, not a
carbon footprint of chlorine: electricity, steam and all raw materials are gaps. The `mass`
row of its allocation comparison (Cl2 30.6 %) is core's stream-mass basis and must not be
used (D-013).

The line list stays empty at this stage: the PFD carries stream numbers, not line numbers;
lines and nominal diameters come with the P&IDs (next stage).

## 7. Open inputs and library items

- Salt analysis (Ca, Mg, SO4, Br, I, Sr, Ba, Fe, Al, insolubles) and the membrane vendor's
  brine specification; cell vendor data (voltage curve, efficiency, element area, ageing).
- Site: grid mix, steam source, cooling water temperature; consumer pressures and purities.
- Dry chlorine water specification and spent-acid strength; chilled-water level.
- Chemicals registry (`chemicals/chemicals.yaml`, consolidated PR later): missing
  **chlorine**, **sodium-hydroxide** (50 wt-% grade), **sodium-chloride** (rock salt),
  **hydrochloric-acid** (32 wt-%), **sulfuric-acid** (98 wt-%), **sodium-carbonate**,
  **sodium-sulfite**, **sodium-sulfate**, **demineralised-water** (or a grade of water) and
  **brine-sludge**; present and used: water, hydrogen, carbon-dioxide, electricity, steam,
  cooling-water, chilled-water, wastewater.
- **LCI database mappings (`lci/mappings.yaml`, library PR, blocks CI of PR #194).** Since the
  allocation is exportable (D-013), the strict library build (`scripts/build_lci.py --strict`,
  tests `test_jsonld_identifiers` and `test_the_library_builds_strict_with_the_utilities`)
  reads `lca/dataset.yaml` and needs curated entries that this folder cannot add: technosphere
  mappings for feed:SALT, DMW, NA2CO3, HCL, NA2SO3, H2SO4, product:SPENT and SLUDGE (with the
  registry entries above); feed:MPS in kWh (the `steam` mapping is in kg); biosphere flows for
  emission:NaCl and Na2SO4 to water; `pass_through` decisions for the zero-amount free
  emissions CaCO3, CaSO4, Cl2, H2, HCl, MgCl2, MgOH2, Na2CO3, Na2SO3, NaOH and SiO2.
  Before this change these errors were hidden because the build stopped at `allocation: none`.
- cheme-as-code: (a) the `mass` allocation weighs product streams including solvent water
  (Cl2 30.6 % here instead of 46.5 %); a contained-component basis is needed (review #1).
  (b) `cheme maturity` classes C401 (class `SeparatingByFlash`, chosen as the closest DEXPI
  2.0.1 class for a vacuum stripper; `Stripping` and `Desorbing` are not DEXPI classes) as
  "equilibrium-stage, predictive, sourced", although its outlet is a specified split (D-005,
  review #5).
- A stray untracked file `build_fs_schema.json` was written at the worktree root by this run
  (a schema dump); it is outside the process folder, not committed, and can be deleted.
