# Design decisions: urea-1 (urea by CO2 stripping)

Issue ChemE-as-Code/process-library#120. Concept stage. One entry per decision: what was
decided, why, what was rejected, and what it assumes. Numbers live in `process/*.yaml`,
`scripts/urea_balance.py` and `lca/`; this file keeps the decisions and their sources.

Run context (2026-10-27): library `main` at 79a7cd4 (branch `case/urea-1`), cheme-as-code
0.8.0 (pyDEXPI 2.1.0). Core issues checked at start: property qualification open; electrolytes closed (merged scope
excludes NH3/NH4+ weak-electrolyte speciation, and `cheme process methods` 0.8.0 still lists
the electrolyte regime as unsupported); solids closed (not needed for this scope).

## Source register

| id | source | locator | read status | reuse terms | used for |
|---|---|---|---|---|---|
| BREF | European Commission JRC (2007), *Reference Document on BAT for the Manufacture of Large Volume Inorganic Chemicals: Ammonia, Acids and Fertilisers* (LVIC-AAF), chapter 8. [PDF](https://bureau-industrial-transformation.jrc.ec.europa.eu/sites/default/files/2022-03/LVIC-AAF.pdf) | §8.2.1 and Table 8.2 (printed pp. 324–325); Tables 8.3–8.10 (pp. 327–335); Table 8.11 (p. 336); Table 8.14 (p. 339); §8.5 and Table 8.20 (p. 362) | read (text extracted locally; nothing copied into the repository) | EU reuse policy (Commission Decision 2011/833/EU): facts reused with attribution; no tables reproduced here | synthesis conditions, conversion range, side reactions, consumption benchmarks, emission levels, BAT levels |
| ULL | Meessen, J.H., *Urea*, Ullmann's Encyclopedia of Industrial Chemistry, [doi:10.1002/14356007.a27_333.pub2](https://doi.org/10.1002/14356007.a27_333.pub2) | — | identity verified (issue #120); not read in this run | licensed: no content may be copied | none numerically; the audit is open (O-3) |
| CIT | Meessen (2014), *Urea synthesis*, Chem. Ing. Tech. 86:2180–2189, [doi:10.1002/cite.201400064](https://doi.org/10.1002/cite.201400064) | abstract | abstract only (per issue #120) | licensed | none numerically; the audit is open (O-3) |
| SKILL | `tech-petchem-ammonia-and-urea` skill (after Speight 2011, ch. 8) | urea rows | read | library skill | cross-check only: the 140–155 bar, 182–190 °C rows; the stoichiometric 567/733 kg/t |

No vendor or licensor data, and no licensed database values, are used.

## Basis table

| item | value | status |
|---|---|---|
| route | CO2 stripping, total recycle, LP recirculation, vacuum evaporation, prilling | decided (D-001) |
| capacity | 2000 t/d prilled urea, 8000 h/a | ASSUMED (D-002) |
| product | urea 98.9 / biuret 0.8 / water 0.3 wt%, total N 46.5 wt% | ASSUMED (D-003); BREF §8.2.1 gives biuret ≤ 1.2 % for fertiliser |
| NH3 feed | liquid, 2200 kPa(a), 293 K, pure | ASSUMED (D-004) |
| CO2 feed | 98.5 % CO2, 0.5 % H2O, 1.0 % inerts as N2; 160 kPa(a), 313 K; + air to 0.6 mol% O2 | ASSUMED (D-004) |
| reactor | 14 000 kPa(a), 453 K, N/C 2.8 | sourced (BREF Table 8.14), as a design choice |
| H2O/CO2 at reactor inlet | 0.45 | ASSUMED (D-005) |
| CO2 conversion per pass | 0.58 | ASSUMED within BREF §8.2.1's 50–80 % (D-005) |
| stripper retention NH3/CO2/H2O | 0.15 / 0.12 / 0.85 | ASSUMED (D-006) |
| LP rectifier | 300 kPa(a) | sourced (BREF Table 8.14) |
| process condensate | 6 % NH3, 4 % CO2, 1 % urea (wt) | ASSUMED after the BREF Table 8.8 remark (D-006) |
| treated condensate | 1 ppm(wt) NH3 and urea | BAT for new plants (BREF Table 8.20) |
| LP absorber vent NH3 | 70 g/t | BREF Table 8.10 (CO2 stripping, LP scrubber) |
| prilling exhaust | dust 35, NH3 30 mg/Nm3 after water scrubbing | ASSUMED inside the BAT ranges 15–55 and 3–35 (BREF §8.5) (D-009) |
| MP steam | 0.8 t/t at 24 bar | BREF Table 8.5 (CO2 stripping, electric CO2 compression) (D-010) |
| power, cooling water | hand estimates: 96 kWh/t, 45 m3/t | calculated (D-010); BREF Tables 8.6/8.4 report 110 kWh/t and 60 m3/t |

## D-001 Route and boundary: CO2-stripping total recycle to prilled urea (2026-10-27)
Decision: Synthesis by high-pressure CO2 stripping with total recycle: HP stripper, HP carbamate
condenser (raising LP steam), reactor, HP scrubber; LP recirculation (rectifier, LP carbamate
condenser and absorber, HP carbamate pump); two-stage vacuum evaporation to melt; forced-draft
prilling with a wet exhaust scrubber; process condensate treatment (desorber, hydrolyser,
desorber). Liquid NH3 and gaseous CO2 are boundary feeds from an ammonia plant outside the
boundary. Ammonia storage, urea product cooling, screening, storage and the utility plants are
outside. The boundary ends at the prilling tower outlet.
Reason: the case notes fix CO2 stripping with LP recirculation, evaporation and a finishing
step. BREF §8.4.2 (p. 340) calls CO2 stripping the most frequent plant type, and §8.5 makes
total-recycle stripping BAT for new plants. The issue's handoff wants explicit NH3/CO2
boundaries. The melt section and finishing are separate blocks (SYN/REC/EVA/PCT vs FIN), so a
melt-only boundary can be taken later without redesign.
Rejected: NH3 stripping and ACES/IDR (BREF §8.4.3–8.4.4): not the case route. Conventional
total recycle: not BAT for new plants. Vacuum crystallisation instead of evaporation (the
BREF Table 8.14 example has it): needs a solid-liquid basis; evaporation is the common
fertiliser route.
Assumptions: the drawing is generic. It does not reproduce any licensor's equipment
arrangement or performance (e.g. pool condenser/reactor variants).

## D-002 Capacity and operating hours (2026-10-27)
Decision: 2000 t/d prilled urea (83.33 t/h), 8000 h/a, turndown 60 % (not checked). Site not
chosen.
Reason: a single-train world-scale size. It is a chosen figure, not a client or licensor
figure: ASSUMED.

## D-003 Product grade and finishing: prilling (2026-10-27)
Decision: fertiliser prills, 98.9 wt% urea, 0.8 % biuret, 0.3 % water (total N 46.5 %).
Finishing by prilling in a forced-draft tower with water scrubbing of the exhaust.
Reason: the case notes ask for a stated choice. Prilling needs no formaldehyde/UF additive (no
extra raw material or registry entry) and its heat balance is simple. Biuret 0.8 % stays below
the 1.2 % BREF §8.2.1 names for fertiliser urea.
Rejected: fluid-bed granulation. It is the usual choice for new plants (larger, harder
granules; lower raw dust, BREF Table 8.10). It needs a granulation additive, about 96–97 %
feed melt and more fan power. It is the first alternative to study, as a separate FIN case.
Assumptions: product cooling, screening and anti-caking outside the boundary.

## D-004 Feeds (2026-10-27)
Decision: NH3 liquid 100 % at 2200 kPa(a)/293 K. CO2 98.5 mol% with 0.5 % water and 1.0 %
inerts (lumped as N2) at 160 kPa(a)/313 K. Passivation air dosed to 0.6 mol% O2 in the CO2
(corrosion protection of the stainless HP loop). Ar of air lumped into N2.
Reason: no ammonia plant interface exists yet (issue #86). The values are typical forms of an
ammonia-plant CO2 removal and warm ammonia product: ASSUMED. Per the issue, captured CO2 is
not assumed free or pressure-ready: it is compressed in the plant (K-101) and its supply
burden stays an open background.
Assumptions: no H2 combustion step for H2 in the CO2; no water knock-out of the CO2 modelled
(lumped in the 0.5 % water); oil and water in the ammonia not modelled.
Hazard (added 2026-10-27 after review R-03): CO2 from an ammonia plant's CO2 removal normally
carries some H2 (and CH4), which the model lumps into the N2. With passivation air dosed in to
0.6 mol% O2, the inerts that collect in the HP scrubber and LP absorber vents can form
flammable H2/O2 mixtures, a known cause of urea-plant explosions. The concept flowsheet does
not change, but basic engineering and the HAZOP must settle the H2 content of the CO2, whether
H2 is removed (catalytic combustion in the CO2) and the vent-gas safeguards (open input O-8).

## D-005 Reaction and reactor model: sourced conditions, conversion model (2026-10-27)
Decision: `process/reactions.yaml` holds UREA_SYN (2 NH3 + CO2 → urea + H2O, the sum of
carbamate formation and dehydration), BIURET (2 urea → biuret + NH3) and HYDROLYSIS (urea +
H2O → 2 NH3 + CO2). R-101 is a conversion reactor: CO2 conversion 0.58 per pass at the inlet
N/C 2.8 and H2O/CO2 0.45, 14 MPa, 453 K. Unconverted ammonium carbamate is carried as its
NH3 + CO2 equivalent: carbamate is not a component.

Reaction/model evidence:

| item | evidence | source | use here |
|---|---|---|---|
| two-step mechanism, liquid phase, both equilibria | qualitative | BREF §8.2.1 (p. 324) | reaction set |
| conversion on CO2 50–80 %; rises with T and N/C, falls with H2O/CO2 | range | BREF §8.2.1 (p. 324) | 0.58 chosen inside it (ASSUMED) |
| 140–250 bar, 180–210 °C, N/C 2.8–4, 20–30 min | ranges | BREF Table 8.2 (p. 324) | bounds |
| CO2 stripping example: N/C 2.8, 180 °C, 140 bar; LP 3 bar | example plant | BREF Table 8.14 (p. 339) | design conditions |
| biuret and isocyanic acid side reactions; hydrolysis | qualitative | BREF §8.2.1 | BIURET, HYDROLYSIS |
| NH3 567 / CO2 733 kg/t for CO2 stripping | reported consumption | BREF Table 8.3 (p. 327) | check: balance gives 565.3 / 731.8 |

Reason: the conversion is a sourced range, labelled as a conversion model. No equilibrium
constant, activity model or kinetics of the NH3-CO2-H2O-urea system is used or invented. As
the issue notes, a stoichiometric reaction in a neutral-fluid flash is not a qualified
speciation model.
Rejected: a liquid-phase equilibrium reactor (`phase: liquid`, `equilibrium_constant`). That
needs a sourced K on a declared basis with activity coefficients for an electrolyte system,
which core cannot qualify (D-008). Ullmann/CIT equilibrium correlations are not audited (O-3).
Assumptions: H2O/CO2 0.45 is a typical recycle water level. Like N/C it is a free
specification of the loop inventory (the balance does not fix either), so both are stated
inputs.

## D-006 Mass balance method: provenance script with specified separations (2026-10-27)
Decision: `scripts/urea_balance.py` (run with `cheme run`) solves the recycle balance. The
reactor follows from N/C, H2O/CO2 and the conversion. The stripper splits by the retention
fractions 0.15 NH3 / 0.12 CO2 / 0.85 H2O. The LP rectifier leaves a 70 wt% urea solution
whose NH3/CO2 make a process condensate of 6/4/1 wt% NH3/CO2/urea. The absorber water closes
the loop water balance. Desorber overheads carry 1 kg water per kg NH3+CO2. The hydrolyser
leaves 1 ppm urea and desorber 2 1 ppm NH3. The treated water feeds the LP absorber and the
prilling scrubber, and the rest leaves to battery limit. Separator outlets are pasted into the
flowsheet as `assumed`. `cheme process propagate --fill` calculates the reactor, hydrolyser,
mixer, compressor, pump and splitter outlets.
Reason: no property package can predict these separations (D-008). Specified splits in a
script that closes every recycle exactly give a balanced PFD at the declared target.
`cheme validate`/`cheme process streams`: all 5 blocks and 22 steps close, reaction extents
UREA_SYN 1391.6 kmol/h, BIURET 6.47 kmol/h, HYDROLYSIS 5.99 kmol/h. The HP loop closure
residual is below 0.01 kg/h.
Results worth noting: stripped solution 58 wt% urea, 7.0 % NH3, 8.8 % CO2; reactor feed
239.5 t/h; process condensate 36.0 t/h (0.43 t/t, cf. 0.3 t/t reaction water plus extra
sources up to about 0.5 m3/t in BREF Tables 8.8/8.9); treated condensate exported 18.7 t/h.
Rejected: tuning the splits to licensor figures (none available, and none used).
Assumptions: all retention fractions and compositions above are ASSUMED. The vacuum system,
start-up/shut-down and flushing water are not in the balance.

## D-007 Evaporation, biuret and prilling heat balance (2026-10-27)
Decision: E-301 to 95 wt% at 33 kPa(a)/403 K; E-302 to melt at 3 kPa(a)/413 K, with all
biuret formation lumped in E-302 (6.47 kmol/h). The melt carries 0.4 % water and the NH3 the
prilling exhaust releases. The prilling air follows from a heat balance: the melt cools from
413 K, solidifies (fusion about 14 kJ/mol, ASSUMED) and leaves at 343 K. The air (0.015 kg/kg
humidity) warms 303 → 343 K, giving 8.0 MW, 706.5 t/h air, 554 kNm3/h, about 6650 Nm3/t
urea. That is 1.6-1.8 times the 300–350 kNm3/h prilling exhaust in BREF Table 8.10. The plant
capacity behind the BREF figure has not been checked, so the two cannot be compared per
tonne yet. Per tonne, the exhaust emissions scale with this air flow (O-5; corrected
2026-10-27 after review R-05, which found that "same order" overstated the agreement). Half of the heat the air took up turns
into evaporation in the wet scrubber (ASSUMED), so the scrubber takes 6.07 t/h treated water.
The liquor (45 wt% urea) returns to E-301.
Assumptions: fusion enthalpy and heat capacities are approximate (ASSUMED); the scrubber
evaporation share is the largest uncertainty in the water balance (O-5).

## D-008 Thermodynamic model and the gated step (2026-10-27)
Decision: no property package is used (`materials.yaml` property method stays a placeholder);
`cheme process props`/`simulate` are not run.
Reason: the HP and LP liquids are concentrated aqueous electrolyte solutions (NH4+, carbamate,
bicarbonate) with urea, and the finishing has a solid. `cheme process methods` (0.8.0)
reports the electrolyte regime unsupported for phase and simulation. Core's merged electrolyte scope
excludes NH3/NH4+ weak-electrolyte speciation and electrolyte VLE. The core issue on the whole-flowsheet
energy basis and polar/activity benchmark is open.
**Gated steps:** (1) a predictive HP loop (carbamate speciation and VLE in stripper,
condenser, reactor and scrubber) needs an NH3-CO2-H2O-urea electrolyte/activity model in core
(the follow-up of the electrolyte issue under #81/#137) with a benchmark of this system; (2) energy closure of
the blocks needs absolute enthalpies of these liquids. Until then the PFD stays at
"balanced with specified separations", and `cheme maturity` reaches no level (the sourced
level fails on the assumed feeds; balanced.model-basis on the unsourced specified values).

## D-009 Emissions to air and water (2026-10-27)
Decision: LP absorber vent NH3 70 g/t (BREF Table 8.10, CO2 stripping LP scrubber), CO2 half
of that by mole (ASSUMED), saturated with water. Prilling exhaust raw dust 100 mg/Nm3 (inside
the BREF raw range 60–130) and raw NH3 35 mg/Nm3, water-scrubbed to 35 and 30 mg/Nm3 (inside
the BAT 15–55 / 3–35 mg/Nm3 of BREF §8.5). Result: 0.27 g NH3, 0.23 g urea dust and 0.09 g
CO2 per kg urea to air. Treated condensate at 1 ppm NH3/urea (BREF Table 8.20) is re-used as
boiler feed water, so no wastewater leaves.
Rejected: acidic scrubbing (BREF §8.5 prefers it when the liquor can be re-used). It makes
ammonium sulphate and needs a sulphuric acid feed and an outlet for the salt; to be revisited
with granulation.
Assumptions: fugitive NH3 not estimated. BREF Table 8.11 gives about 10–12 t/a for Dutch
plants, about 0.02 g/kg here (excluded with reason in `lca/lca.yaml`).

## D-010 Utilities and duties (2026-10-27)
Decision: electric CO2 compressor. MP steam 2400 kPa(a) at the BREF Table 8.5 total of 0.8 t/t
(34.0 MW): E-302 2.6 MW (evaporation × 2300 kJ/kg), R-401 1.0 MW net (ASSUMED), and the HP
stripper the rest (30.4 MW). LP steam 450 kPa(a) is raised in E-102 and used in C-201
(12.1 MW), E-301 (19.0 MW) and C-402 (4.2 MW); net LP import/export zero (ASSUMED). These are
energy streams from E-102 to the consumers. E-102 condensation heat not assigned (corrected
2026-10-27 after review R-01): `scripts/urea_balance.py` already subtracts the dehydration
heat (28 MJ/kmol × U) from E-102's potential, and that still leaves 59.4 MW, 24.2 MW more than
the 35.2 MW of LP steam raised. Part of the surplus heats the reactor feeds, which the script
does not count: the NH3 from 293 K to about 450 K (about 10 MW) and the recycle carbamate
(about 4 MW), both rough estimates from the review (ASSUMED). That leaves about 10-24 MW
(0.12-0.29 kWh/kg urea) that is neither exported as LP steam nor rejected to cooling water,
and no exchange of the LCI carries it (`cheme.boundary-utility-unassigned` for R101). This is
an open energy item (O-4): it may become an LP steam export or more cooling duty. C-401 is
heated by C-402's overhead (the same warning for C401). Hand
estimates: carbamate decomposition/formation 120 MJ/kmol CO2 (ASSUMED, below the about
160 MJ/kmol of solid carbamate from formation enthalpies), water 2300 kJ/kg. Power: K-101
6.86 MW (4 intercooled stages, η 0.78), P-101 0.42 MW, P-102 0.21 MW, prilling fan 0.52 MW
(2 kPa, η 0.7): 96 kWh/t against 110 kWh/t in BREF Table 8.6 (missing: vacuum, condensate,
scrubber and cooling pumps). Cooling water: K-101 6.2, E-201 16.0, E-303 21.5 MW: 45 m3/t at
10 K against 60 m3/t in BREF Table 8.4 (missing: product cooling, HP scrubber tempered water,
vacuum condensers of ejector steam, lube oil).
Reason: an electric CO2 compressor makes steam and power separate exchanges for the LCI (BREF
reports both configurations). The steam total is the one sourced energy figure; the split and
the other duties are labelled estimates.
Assumptions: the LCI inherits the low power and cooling water estimates. They are open inputs
for the energy basis (O-4).

## D-011 LCI scope (2026-10-27)
Decision: preliminary gate-to-gate inventory per 1 kg prilled urea (`lca/lca.yaml`, `boundary:
cradle-to-gate` as the study's target, with every background `missing:`). Allocation none: one
product; the treated condensate is a recyclable (cut-off, burden-free, no credit). The feed CO2
is fossil process CO2 from the ammonia plant, carries its own supply burden (cut-off) and gets
no consumption credit. The 0.2 kg fossil C per kg urea is released at field application,
outside the boundary: reported, not credited. Emissions characterised by CAS: NH3 and urea
dust to air (no climate factor: gaps by method), CO2 fossil to air. Air components and water
vapour free.
Reason: the run's scope is the foreground; backgrounds are linked later by the consolidated
library work. Per the issue, no CO2-consumption credit is combined with an upstream capture
credit.
Results: each inventory exchange equals its flowsheet stream (S1, S3, S4, S50 in; S51, S31,
S54, S45 out; power = Q1–Q4, MP steam = Q5–Q7, cooling water = Q11–Q13). Material in
816 309.6 kg/h, out 816 308.1 kg/h (+1.5 kg/h, 0.0002 %). `cheme assess lca --balance` closes
mass, C, H, N, O and carbon origin (residual below 0.001 %); `--coverage` classifies the (empty) impact result as a partial screening
carbon footprint with 5 declared background gaps. It is not an impact result.

## D-012 Equipment design values (2026-10-27)
Decision: equipment list with ASSUMED design pressures per level (HP 160 barg, LP 6 barg,
vacuum section 3.5 barg/full vacuum, hydrolyser 22 barg) and design temperatures of about the
operating maximum + 25 K. Carbamate-service materials are named as urea-grade austenitic or
duplex stainless steel and left as an open input.
Reason: carbamate corrosion governs the material and the passivation air (skill
`tech-petchem-ammonia-and-urea`); the selection is a licensor/materials-engineering decision.

## D-013 LCI dataset kept out of the Atlas build until its links are mapped (2026-10-27)
Decision: `lca/dataset.yaml` is still written by `cheme assess lca --write`, but it is not
committed (folder `.gitignore`). `lca/inventory.csv`, `gaps.csv` and `results.*` stay
committed as the preliminary LCI.
Reason: the library CI (`scripts/build_lci.py --strict` and the tests that build the whole
library) reads every committed `processes/*/lca/dataset.yaml` and refuses an exchange that has
no curated link in `lci/mappings.yaml`. This dataset has five: feed:NH3 (no ammonia entry),
feed:CO2 (no `carbon-dioxide` entry), feed:MPS (the registry's `steam` is counted in kg, the
exchange in kWh of heat), emission:BIURET (a free 0 kg emission, not a curated pass-through)
and emission:UREA (no biosphere3 identity). Each one is a library mapping decision in
`lci/mappings.yaml`, outside this folder and outside the scope of this case (D-011: backgrounds
are linked later by the consolidated library work). Making up activity links here instead
would hide the gaps the LCI declares.
To undo: add the mappings in a library PR (ammonia and CO2 feed gas with O-1 and O-6, MP steam
per kWh or the steam in kg, the urea dust flow, biuret dropped or curated), remove the
`.gitignore` line and commit the dataset.

## Open inputs
- O-1 Ammonia plant interface (issue #86): NH3 and CO2 conditions, CO2 impurities (H2, see
  O-8), and
  the LCI datasets the urea feeds link to.
- O-2 Site and country: grid, steam and cooling-water backgrounds.
- O-3 Numerical audit of Ullmann (ULL) and CIT for equilibrium correlations, typical
  stripper efficiency and condensate amounts; replace the ASSUMED conversion, retention
  fractions and H2O/CO2 with sourced values.
- O-4 A complete energy basis (minor drives, coolers, vacuum system) against the BREF
  benchmarks; the stripper steam split; the 10-24 MW of R-101/E-102 heat not assigned (feed
  preheat terms in the script, then LP steam export or cooling water, D-010) and C-401's
  heating, with their effect on the LCI.
- O-5 Prilling scrubber evaporation and the plant water balance; product cooling. The
  exhaust S54 at 318 K (25 K below 343 K, about 5 MW of evaporation) does not match the
  assumed half of 8.0 MW (4 MW, about 20 K): settle both together (review R-05). Also, the
  air flow per tonne against an open source of known capacity.
- O-6 Registry entries (shared files, consolidated PR): `urea` (with a grade for prilled
  fertiliser urea, 46 % N), `ammonia` (liquid anhydrous); optionally `biuret`. CPC class of
  the dataset not given (unverified).
- O-7 Core: `cheme process build` 0.8.0 fails on the DEXPI step class `Pumping` (its
  `method` field is a typing Union that `step_method` cannot iterate); the pumps use
  `GeneratingFlow`. `cheme process propagate` writes compositions to 6 digits, so S11 sums
  to 0.999999 and the PFD shows one `pydexpi_composition_fractions` warning.
- O-8 H2 in the CO2 feed and the vent-gas hazard (D-004): the H2 (and CH4) content of the CO2,
  whether H2 is removed by catalytic combustion, and the safeguards against flammable H2/O2
  mixtures in the HP scrubber and LP absorber vents. For basic engineering and the HAZOP.
