# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.

Case study for issue ChemE-as-Code/process-library#184 (acetylene, natural-gas partial
oxidation). Concept stage: design basis, balanced BFD/PFD, preliminary gate-to-gate LCI. Started
from library commit 57b916c (main) with cheme-as-code 0.8.0; agent session of 2026-10-28
(Claude Opus 5.5). Independent design: no published plant balance was copied. Every number below
is either a fact from a cited open source (in our own words), a result of `scripts/balance.py`
or of cheme, or ASSUMED.

## Source register

| # | source | locator | access / read | reuse | used for |
|---|---|---|---|---|---|
| S-1 | BASF SE, US8975460B2 (2015), Process for preparing acetylene by the Sachsse-Bartholome process, https://patents.google.com/patent/US8975460B2/en | description (background of the process) | full text read online | patent text public; facts only, own words | typical dry cracked gas (H2 56, CH4 5, C2H2 7.5, CO 26, CO2 3.5, higher hydrocarbons 1 vol%, rest N2/O2/Ar); flame about 1700 C; both feeds preheated to 600 C (D-004, D-005) |
| S-2 | BASF AG, US5824834A (1998), Process for the production of acetylene and synthesis gas, https://patents.google.com/patent/US5824834A/en | examples (comparative examples 1-2, examples 1-7) and the table of results; claims | full text read online (table columns partly garbled in the HTML; mapped by the example text) | facts only | O2/natural-gas ratios 0.58-0.75 and O/C 1.17-1.5 of the examples; acetylene-to-soot ratio 22 kg/kg (comparative example 2, 7.8 vol% C2H2); soot sludge 90 % water; process water 80 m3/d at 30 t/d C2H2 (comparative example 2); preheat 600 C; residence time a few ms (D-004..D-006) |
| S-3 | BASF SE, US11459281B2 (2022), Method for producing acetylene and syngas, https://patents.google.com/patent/US11459281B2/en | claim 1; description (soot removal); working examples (emission table, decompression table) | full text read online | facts only | quench to 80-90 C; ESP outlet about 1 mg/m3 soot; dissolved load of the quench water (comparative: C2H2 5.475, CO 0.789, CH4 0.162, benzene 0.138, butadiene 0.712 kg/t acetylene); 99.31 % depletion at 400 mbar(a), 75.8 C after decompression (D-006) |
| S-4 | BASF SE, US10059640B2 (2018), Apparatus and process for the preparation of acetylene and synthesis gas, https://patents.google.com/patent/US10059640B2/en | background; embodiments (degassing and stripping train, example values) | first ~80 % of the full text read online | facts only | NMP pre-wash and main wash sequence; rich solvent 7.5-8.5 bar, 125-135 C into the first column; columns at 1.0-1.5 bar; hot-stripper bottom 165-180 C; acetylene solubility 15-35 Nm3/m3 solvent; acetylene partial pressure kept at or below 1.4 bar (D-007, D-009) |
| S-5 | Pässler, P. et al., Acetylene, Ullmann's Encyclopedia of Industrial Chemistry, doi:10.1002/14356007.a01_097.pub4 | - | not read (licensed); route reference only | cite only | route identity; the source audit for specific consumptions is open (next stage) |
| S-6 | Zhang et al. (2022), Front. Chem. Sci. Eng., doi:10.1007/s11705-022-2210-y | LCI table of the natural-gas partial-oxidation acetylene stage | NOT read (publisher site in maintenance on 2026-10-28); only a search snippet seen | none | a lead for a later cross-check of consumptions and NMP loss; no value of it is used |
| S-7 | Detailed mechanism for natural-gas partial oxidation to acetylene, syngas and olefins, Processes 13(7) 2287 (MDPI, 2025), https://www.mdpi.com/2227-9717/13/7/2287 | - | not accessible (HTTP 403) | open access (CC BY) to be confirmed | a lead for a predictive burner model (next stage) |
| S-8 | NIST Chemistry WebBook, water, Antoine parameters (Bridgeman and Aldrich 1964) | water phase-change data | used | facts | water saturation in the quench, column, compressor and flash (scripts/balance.py) |
| S-9 | chemicals / thermo packages through `cheme chemistry thermo` (ATcT, CRC, Yaws, Poling 5th ed.) | per component in materials.yaml | used | open packages, facts | ideal-gas formation data, Cp fits |

## D-001 Route and boundary (2026-10-28)
Decision: Acetylene by partial oxidation of natural gas with oxygen in a BASF (Sachsse-Bartholome)
burner with direct water quench; soot removed in a cooling column, a wet ESP and a closed
quench-water circuit; the cracked gas compressed and washed with N-methyl-2-pyrrolidone (NMP);
the unabsorbed gas leaves as synthesis gas (co-product). The higher acetylenes and the
quench-water flash gas fire the feed preheater. Boundary: natural gas, oxygen (boundary feed; an
air separation unit such as processes/asu-1 makes it), NMP make-up, combustion air, power, MP
steam, cooling water in; acetylene (1.2 bar(a)), synthesis gas (11 bar(a)), soot sludge,
quench-water purge, solvent residue, flue gas out.
Reason: The route the issue names; it is the dominant hydrocarbon route, and every step of it
can be balanced with an explicit sourced composition model, without the carbide furnace (core
#370 refuses the carbothermal step) or solids handling (#365).
Rejected: calcium carbide hydrolysis (a different boundary: lime kiln, carbide furnace, carbide
lime residue); electric-arc pyrolysis (Hüls) and thermal cracking (Wulff); ethylene co-product
recovery from steam crackers; the oil-quench variant with heat recovery (the issue fixes a water
quench; noted as an option in D-006). Outside the boundary: the ASU, synthesis-gas conditioning
(CO2 removal, compression), acetylene drying, compression and storage, soot incineration.

## D-002 Capacity and operating hours (2026-10-28)
Decision: 6250 kg/h acetylene (50 kt/a at 8000 h), ASSUMED. The product stream is 6285 kg/h
(99.55 mol% C2H2).
Reason: No traceable published plant basis was read (issue: capacity missing); 50 kt/a is a
round world-scale order of magnitude. Each burner of the examples of S-2 makes 25-33 t/d, so
the capacity implies five to six parallel burners; the flowsheet models them as one equivalent
train (number of trains open). The LCI is per kg and does not depend on the capacity at this
stage.

## D-003 Feed specifications (2026-10-28)
Decision: natural gas CH4 98.0, CO2 0.5, N2 1.5 mol% at 400 kPa(a), 303 K; oxygen 99.5 mol% (Ar
0.5) at 400 kPa(a), 303 K. Both ASSUMED.
Reason: a lean pipeline gas keeps the burner model on methane, the basis of S-1/S-2. Ethane and
heavier change the oxygen demand and the soot (S-2 example 6 with C1-C4 gas); sulfur would need
removal before the preheater. To be fixed with the site (open input). The oxygen purity must be
matched with asu-1's GOX when the LCI is linked.

## D-004 Preheat (2026-10-28)
Decision: natural gas and oxygen preheated separately to 873 K (600 C) in a fired heater (H-101,
two coils), premixed in the mixing diffuser at 150-160 kPa(a).
Reason: 600 C is the preheat of the examples of S-2 and the typical value of S-1 and S-3.
Separate heating is required: the premixed gas would ignite early (S-2 and S-4 describe the
burner block channels that prevent flash-back). Duties: 14.8 MW (natural gas) and 5.5 MW
(oxygen), ideal gas (scripts/balance.py). The oxygen coil needs oxygen-service materials and
cleanliness (basic engineering).

## D-005 Burner model: sourced outlet composition (2026-10-28)
Decision: The burner R101 is a conversion reactor with seven lumped parallel reactions
(process/reactions.yaml): acetylene pyrolysis, partial oxidation to CO/H2, methane combustion,
hydrogen combustion, soot, diacetylene (lump of the higher acetylenes) and benzene (lump of the
aromatics). scripts/balance.py fixes the seven extents and the two feed rates so that (i) the
dry cracked gas has the typical composition of S-1, the 1 vol% higher hydrocarbons split 0.7
C4H2 / 0.3 C6H6 (ASSUMED), (ii) the acetylene-to-soot mass ratio is 22 (S-2 comparative example
2, the example closest in acetylene content, 7.8 vol%), (iii) the residual O2 is 0.1 vol% of the
dry gas (ASSUMED; S-2 reports 0.1-0.3 vol% O2 in its synthesis gas), and (iv) C, H and O balance.
cheme process propagate solves the reactor from these conversions and reproduces the script's
outlet (C2H2 0.055612 mole fraction in both).
Results and checks (not inputs):
- O2/natural gas 0.602 vol/vol, O/C 1.22: inside the 0.58-0.75 and 1.17-1.5 of S-2's examples
  (its comparative example 1 runs at 0.583 for 8.5 vol% C2H2).
- adiabatic outlet temperature 1970 K on ideal-gas data with soot as graphite (Cp 21 J/(mol K)
  ASSUMED, no heat loss): S-1 states about 1700 C (1973 K). The closeness is partly fortuitous
  (heat loss and the lumped Cp of C4H2/C6H6, held constant above 1000 K, are not resolved).
- 27.4 % of the feed carbon goes to acetylene, 26.8 % to the product.
- specific consumption 6.52 Nm3 natural gas and 3.92 Nm3 O2 per kg acetylene; 10.7 Nm3 syngas.
  The rates derived from S-2 comparative example 1 are about 5.2, 3.1 and 9.1 Nm3/kg at 8.5
  vol% C2H2: our basis (7.5 vol%, 98 % recovery) needs 13 % more gas per acetylene; consistent
  in direction, a source audit of S-5 is open.
- `cheme process reactors`: ln(Q/K) = -6.5 for 2 CH4 = C2H2 + 3 H2 at 1970 K: the outlet is short
  of the pyrolysis equilibrium; the acetylene is kinetically limited and frozen by the quench. An
  equilibrium or Gibbs model would be wrong for this burner (it predicts neither the soot nor
  the acetylene yield of a millisecond flame), which is why a sourced composition is used.
Rejected: invented kinetics; a Gibbs reactor; a selectivity model with unsourced selectivities.
Gated: core cannot evaluate the burner's energy balance (no data for solid carbon; C4H2 and C6H6
Cp fitted only to 1000 K): the adiabatic temperature is the script's. A predictive model needs
a detailed mechanism (S-7) and a reactor model for a premixed flame with quench (not in core).

## D-006 Quench, soot removal and the water circuit (2026-10-28)
Decision: water quench to 353 K, 120 kPa(a) (S-3 claim 1: 80-90 C), gas saturated with water;
70 % of the soot to the quench water, 29.5 % to the cooling column (353 -> 308 K), 0.5 % to the
wet ESP (ASSUMED splits; S-3: about 1 mg/m3 after the ESP, taken as zero). The circuit is closed:
quench, column and ESP water and the compressor condensate are collected, degassed at 400
mbar(a) (V-102: 99.31 % of the dissolved hydrocarbons to the fired heater, S-3), freed of soot
(V-101: all soot as a 10 wt% sludge, S-2) and cooled to 303 K (E-101); the net reaction water
leaves as a purge. The dissolved load is the comparative load of S-3 (butadiene omitted: no
component; 0.71 kg/t, ASSUMED negligible for the balance).
Results: quench water 1146 t/h, column water 528 t/h, ESP 10 t/h (ASSUMED); purge 17.0 t/h =
2.72 kg/kg acetylene (S-2 comparative example 2: 80 m3/d at 30 t/d = 2.67 m3/t, a check, not an
input); sludge 2.90 t/h = 0.46 kg/kg (S-2: 13.2 t/d at 30 t/d = 0.44); circuit cooler 91.6 MW.
Reason: The closed, degassed circuit avoids the open cooling-tower stripping of the older
design (S-3 comparative: 5.5 kg acetylene per t to air). The water energy balance is computed
in scripts/balance.py (liquid water Cp 75.3 J/(mol K), latent heat 44.0 kJ/mol at 298 K): core
has no package for this water with soot.
Open option: the quench heat (91.6 MW, 82 % of all cooling) is rejected to cooling water at
303-353 K; an oil quench with steam raising or the use of the 350 K circuit water for heating
would cut it (heat-integration study, next stage).

## D-007 Compression (2026-10-28)
Decision: three intercooled stages 1.05 -> 11 bar(a), isentropic efficiency 0.78, motor 0.96,
intercooling to 313 K, one knock-out drum for all condensate (ASSUMED). Power 8.83 MW electric,
discharge 404 K.
Reason: the NMP absorption needs pressure; the absorber feed holds 8.5 % acetylene, i.e. 0.94
bar acetylene partial pressure at 11 bar(a), below the 1.4 bar that S-4 names as the limit
without extra safety measures. The pressure itself is not from a read source (open input).

## D-008 Synthesis gas co-product (2026-10-28)
Decision: the absorber overhead (61.1 % H2, 28.4 % CO, 5.5 % CH4, 3.8 % CO2, 0.04 % C2H2, 0.1 % O2)
leaves at 1070 kPa(a) as a co-product, 5.76 kg (10.7 Nm3) per kg acetylene, H2/CO 2.15; for
methanol or oxo users (S-2 describes the synthesis gas as a product). No conditioning in the
boundary. The O2 traces and the CO2 are for the user to remove (open specification).

## D-009 Acetylene recovery with NMP (2026-10-28)
Decision: one absorber T-301 for the pre-wash and the main wash (S-4: a small pre-wash solvent
flow takes the aromatics and higher acetylenes, a much larger main wash the acetylene), degasser
T-302 (gas recycled to the compressor suction), lean/rich interchanger, acetylene stripper T-303,
hot stripper T-304 with solvent regeneration. Splits (ASSUMED, scripts/balance.py):

| component | to syngas in T-301 | released in T-302 (of absorbed) | to product in T-303 (of remaining) |
|---|---|---|---|
| H2, CO, CH4, N2, Ar, O2 | 0.99-0.999 | 1.0 | - |
| CO2 | 0.85 | 0.95 | 0.60 |
| C2H2 | 0.004 | 0.15 | 0.99 |
| C4H2, C6H6, H2O | 0 | 0 | 0 (all to T-304 off-gas) |

Solvent: 339 t/h lean NMP with 3 wt% water (ASSUMED) for a loading of 20 Nm3 acetylene per m3
(inside S-4's 15-35); temperatures and pressures of S-4 (rich 403 K into T-303, T-304 bottom
443 K). NMP make-up 2 g/kg acetylene (ASSUMED: no open figure read; S-6 may give one): 5 % lost
with the syngas, 5 % burnt with the off-gas, 90 % as residue to incineration.
Results: product 99.55 mol% C2H2 (0.25 % CO2, 0.2 % H2O); of the acetylene formed 98.0 % to
product, 0.5 % with the syngas, 1.0 % with the off-gas, 0.5 % in the quench water (flash gas);
recycle 2.1 t/h (60 % C2H2).
Gated: no qualified property model for NMP with acetylene (core #315); the splits are specified,
not predicted. Diacetylene in the off-gas (40 mol%, diluted by 38 % water vapour) is
deflagration-prone (S-4): its handling is a safety item for basic engineering.

## D-010 Pressure profile (2026-10-28)
Decision: feeds 400 kPa(a), burner 150-160, quench 120, column 115, ESP 110, compressor suction
105, absorber 1090-1070, degasser 130, strippers 120-140 kPa(a); circuit water pumped to 500
kPa(a). All ASSUMED; no hydraulic calculation.

## D-011 Fired heater and off-gas firing (2026-10-28)
Decision: H-101 burns the T-304 off-gas (24.4 MW LHV with the flash gas) plus natural gas as
support fuel at 10 % of the firing (ASSUMED, flame stability), 27.1 MW LHV, 15 % excess air,
99.95 % burnout of every fuel (ASSUMED), stack 433 K. It delivers 85 % of the LHV (ASSUMED):
the two preheats and 2.77 MW to the hot stripper (convection-section steam, Q12).
Check: `cheme process reactors` gives the firebox duty as 25.8 MW from the inlets to the 433 K
flue on ideal-gas data; the 23.0 MW used leaves 2.7 MW (10 %) as casing and radiation loss.
Emissions in the flue (S46): 1.19 kg CO2 per kg acetylene (unallocated) and traces of unburnt
hydrocarbons; NOx not estimated (lca.yaml exclusion).

## D-012 Utilities (2026-10-28)
Decision: electricity 9.55 MW (compressor 8.83, circuit pumps 0.26, solvent pumps 0.13, ESP 0.15
and vacuum pump 0.12 as ASSUMED allowances, air fan 0.06); MP steam 12 bar(a) 6.92 MW (T-303 1.67:
desorption 25 kJ/mol ASSUMED; T-304 5.25 net of Q12: solvent 403 -> 443 K with Cp 2.0 kJ/(kg K)
ASSUMED, desorption and evaporation of the off-gas water); cooling water 25/35 C 111.4 MW (E-101
91.6, compressor 10.2, lean cooler 9.6).
Per kg acetylene (product stream, unallocated): 1.52 kWh electricity, 1.10 kWh (3.96 MJ) steam,
17.7 kWh heat to cooling water.

## D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml after asu-1 and phosgene-1: functional unit 1 kg acetylene gas at the
gate (S18); every feed, utility and waste exchange taken from the balanced flowsheet with its
stream id; backgrounds deliberately unmapped (`missing:` with the activity each should connect
to: a gap, never zero, no licensed values); the flue gas mapped to elementary flows (CO2 and CH4
fossil). Boundary key cradle-to-gate so that feeds stay gaps. Allocation for the per-kg view:
energy (LHV), properties given in lca.yaml: acetylene 47.97 MJ/kg, syngas 22.52 MJ/kg, i.e.
27.0 % of the burdens to acetylene (mass would give 14.8 %; economic allocation, which S-6
reportedly uses, would give much more: the choice moves the result by a factor of two or more
and must be decided with the study's goal; dataset.yaml stays unallocated).
Unallocated inventory per kg acetylene: natural gas 4.733 kg, oxygen 5.576 kg, support natural
gas 0.032 kg, NMP 0.0020 kg, air 5.32 kg; electricity 1.520 kWh, MP steam 1.101 kWh, heat to
cooling water 17.73 kWh; co-product syngas 5.757 kg; purge water 2.704 kg, soot sludge 0.461 kg
(0.046 kg carbon), solvent residue 0.0018 kg; to air CO2 1.194 kg, CH4 16 mg, C2H2 8 mg, C4H2
91 mg, C6H6 61 mg, CO 0.4 mg, NMP 0.05 mg. (lca/inventory.csv lists the energy-allocated values,
27.0 % of these.)
Results: `cheme assess lca --balance`: mass closed (+0.99 kg/h of 98 416 kg/h), C, H, N, O, Ar
closed (all 0.00 %), carbon origin closed (fossil in 21 663 kg C/h = products 19 318 +
outputs 297 + emissions 2 049). Core's energy closure line (0.0 %) counts only the utilities,
not fuels and products; an independent first-law check on LHV (natural gas 397.2 + support 2.7 +
power 9.6 + steam 6.9 MW in; acetylene 83.8 + syngas 226.3 + soot 2.6 + cooling 111.4 + flue and
casing 4.1 MW out) closes within about 0.3 % once the latent heat of the 19.6 t/h reaction water
condensed in the quench (13.2 MW) is counted. `--coverage`: partial screening carbon footprint,
15 gaps (10 unmapped backgrounds; C2H2, C4H2, C6H6, CO, NMP outside the GWP method), boundary
check clean, publishable. No impact numbers are claimed.
Exclusions (lca.yaml): heater NOx; fugitive hydrocarbons (no P&ID); air emissions from the
soot separator's open surfaces. Construction, transport, end of life not included.
Atlas build: lca/mappings.yaml holds one override, a unit correction: feed:STEAM (kWh) takes the
shared `steam-heat` entry, as hda-1 and others do, because the slug `steam` is counted in kg.
Electricity, cooling water and wastewater link by their registry slugs in the Atlas build; every
other exchange stays a reported gap. The library's `scripts/build_lci.py --strict` run over the
whole library passes (exit 0), with acetylene-1's 10 mapping gaps (natural gas, support gas, oxygen, NMP, sludge and residue
treatment; C2H2, C4H2, C6H6 and NMP to air without a biosphere identity) exported unlinked (unpublished
process). The allocation records a `deviation`: no sourced prices yet for the library's
price-ratio step.

## D-014 Missing shared entries (for the consolidated library PR) (2026-10-28)
Not edited here (outside this folder):
- chemicals/chemicals.yaml: acetylene (74-86-2; grades e.g. dissolved / pipeline gas),
  natural-gas (mixture), synthesis-gas (mixture), carbon-monoxide (630-08-0),
  n-methyl-2-pyrrolidone (872-50-4), carbon-black / soot (1333-86-4), diacetylene (460-12-8,
  emission only). Then process.yaml lists the main product, the co-product and the feeds.
- taxonomy/families.yaml: no acetylene family; the case uses olefins and syngas. An
  "acetylene-and-derivatives" family (or a note on olefins) would place it correctly.
- lci/mappings.yaml vocabulary: natural gas high and low pressure, NMP, incineration of soot
  sludge, incineration of spent nitrogen-containing solvent, MP steam from the site boiler.
- elementary-flow crosswalk (core): acetylene, 1,3-butadiyne, benzene and NMP to air; EF 3.1
  UUIDs for CH4, CO, CO2 (a core TODO).

## Calculation maturity (2026-10-28)
`cheme maturity`: calculation maturity none; design maturity claimed concept, which the evidence
does not yet support (as for phosgene-1): feed flows and compositions are assumed, the burner
conversions are derived from sourced compositions but carry assumed choices (C4H2/C6H6 split,
residual O2), the separators are specified splits, and no simulation run exists. The concept
gates of `cheme check` pass (design basis, lists, process concept, balances, links, ASSUMED
marking); layout-plot-plan fails (out of scope).

## Method and dependency table (2026-10-28)

| step | method used | core capability | status |
|---|---|---|---|
| burner mass balance | conversion reactor from a sourced composition (D-005) | conversion reactor | done in core |
| burner energy | adiabatic temperature in scripts/balance.py | needs condensed-phase carbon and C4H2/C6H6 Cp to 2000 K | gated (data range; not core #370, which covers lime kilns) |
| quench, cooling column, water circuit | specified outlets, energy in the script | no package for water with soot / dissolved gases (core #315) | gated |
| soot as a solid | `phase: solid` pseudo-component, mass only | core #365 solids basis | sufficient for balances; no solid separation model needed at concept |
| NMP absorption and stripping | specified splits (D-009) | no qualified NMP / acetylene property model (core #315, polar/activity benchmark) | gated |
| compression, preheat, duties | ideal gas in the script | DWSIM route not qualified for this mixture | gated |
| fired heater | conversion reactor; duty checked by `cheme process reactors` | available | done |
| LCI | `cheme assess lca` | available | done (backgrounds unmapped by design) |

## Open inputs and gated steps
- Capacity, site, number of burner trains; natural-gas composition; oxygen purity and pressure
  from asu-1; acetylene and syngas specifications and delivery pressures.
- Source audit of S-5 (and S-6 once reachable) for specific natural-gas, oxygen, power and steam
  consumption, soot and NMP loss, with exact table locators.
- Compression pressure, NMP splits, loading, water content and loss; desorption heat; electric
  allowances (ESP, vacuum); fired-heater efficiency and support-fuel share; NOx factor.
- Gated in core: burner energy (data for solid carbon, Cp of C4H2/C6H6 above 1000 K); property
  packages for the quench water and the NMP section (core #315); predictive burner kinetics.
- Heat recovery from the quench (91.6 MW to cooling water) not studied.
