# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Numbers live in the YAML files (`process/`, `lca/`) and in `scripts/balance.py`; this file keeps
the reasons. Stream table: `cheme process streams --md` (generated, not copied here).

Run of 2026-10-28 (agent, issue ChemE-as-Code/process-library#176): library base commit
`11d50ef`, cheme-as-code 0.8.0 (pyDEXPI 2.1.0). Stage: concept. Nothing here is reviewed.

## Source register

| id | source | locator | read | use |
|---|---|---|---|---|
| BREF | Falcke et al. (2017) Best Available Techniques Reference Document for the Production of Large Volume Organic Chemicals, JRC109279, EUR 28882 EN, doi:10.2760/77304 (EU, reuse with attribution) | ch. 3 Lower olefins: §3.2.2.4 (fractionation schemes), Table 3.3 (once-through furnace yields, p. 133), §3.2.3.1 (decoking), Table 3.4 (furnace emissions to air), §3.3.1.4 (fugitive VOC), §3.3.4 (energy), §3.3.4.2 (steam/feed ratio), ch. 13 Table 13.1 (BAT-AELs NOx, CO) | full text read for these sections | furnace yields (D-005), emission factors (D-017), energy check (D-018) |
| IPCC | 2006 IPCC Guidelines for National GHG Inventories, Vol. 2, Ch. 2, Table 2.3 | natural gas, manufacturing industries: CH4 1 kg/TJ, N2O 0.1 kg/TJ | default values (known table, not re-fetched in this run) | CH4/N2O of the firebox, proxy (D-017) |
| ULL | Zimmermann, Walzl: Ethylene, Ullmann's, doi:10.1002/14356007.a10_045.pub2 | - | not read (lead from the issue) | none yet |
| OLE | skill `tech-petchem-olefins` (Speight 2011, ch. 11) | coil outlet 800-880 C, CGC discharge 17-35 bar | skill text | ranges for D-004, D-008 |
| CORE | `cheme chemistry library ethane_cracking`, `chemicals` package | ideal-gas formation data and Cp of all gas components | tool output | reactor duties, firebox balance |

No figure, table or text of a source is copied; values are restated with their locator.

## D-001 Route: ethane steam cracking (2026-10-28)
Decision: ethane feed, molecular components only.
Reason: the issue recommends a molecular ethane brief unless a traceable naphtha assay exists.
None was found in this run. Ethane needs no pseudocomponents (core #367 support for naphtha
assays is recent and cannot enter `simulation.yaml`), and core's reaction library has
`ethane_cracking`. The BREF gives sourced once-through yields for ethane.
Rejected: naphtha. It would need a sourced assay, a much larger yield slate (aromatics, fuel
oil) and pseudocomponents. It stays a later case (`ethylene-2`).
Consequence: propylene is a minor co-product (2.6 % of the ethylene) and there is no pyrolysis
fuel oil. The BREF gives no C7+ yield for ethane, so no fuel oil is invented. This deviates
from the issue's co-product list on purpose.

## D-002 Capacity, hours, product grades (ASSUMED)
1000 kt/a polymer-grade ethylene, 8000 h/a (125 t/h): a world-scale single cracker, chosen
here, not a client figure. Ethylene 99.95 mol% (ethane the only modelled impurity), propylene
99.5 mol%. The acetylene, CO, CO2, H2 and oxygenate limits of polymer grade are not modelled.

## D-003 Feed (ASSUMED)
Purity ethane: 96.8 mol% C2H6, 2.5 % C3H8, 0.5 % CH4, 0.2 % CO2, 3000 kPa(a), 40 C. No
pipeline specification was sourced. Sulphur and the DMDS doping are not modelled.

## D-004 Furnace conditions
Coil outlet 840 C (inside the 800-880 C range of OLE and core's 1073-1173 K library window),
200 kPa(a) (ASSUMED, inside the 150-250 kPa(a) window), dilution steam 0.30 kg/kg hydrocarbon
(ASSUMED). The BREF (§3.3.4.2) only says ethane runs below the 0.85 of liquid feeds.

## D-005 Furnace model: sourced once-through yields as a conversion model
Decision: H101 (ethane coils) uses ten formation reactions from ethane. Their conversions
(`process/reactions.yaml`) are computed by `scripts/balance.py` so that pure ethane gives the
BREF Table 3.3 ethane column: 70 % conversion; wt%: H2 4.3, CH4 4.2, C2H2 0.4, C2H4 56,
C2H6 30, propadiene 0.1, C3H6 1.0, C3H8 0.2, butadiene 1.6, butylenes 0.2, butane 0.2,
C5/C6 1.8. A separate coil H103 (block CRK3) cracks the recycled propane with three reactions
that reproduce the ethylene (40.9), propylene (11.5) and ethane (3.6 wt%) yields of the propane
column. Its conversion is 82 % instead of the BREF 95 %; the rest of the propane recycles.
Lumps: C5/C6 as benzene (pyrolysis gasoline), propadiene for MAPD, 1-butene for butylenes.
Because the lumps are hydrogen-poor, the hydrogen yield comes out at 4.39 instead of 4.3 wt%,
so that hydrogen balances.
Why separate coils: propane reactions are linear combinations of the ethane set (12 species,
2 elements: rank 10). In one step or block the balance check cannot find unique extents. Recycle
furnaces for C3 are also common practice. At recycle to extinction the propane ends up at the
same products either way.
Basis: a sourced conversion/yield model, not kinetics; no severity response. Coke, CO and the
steam-reforming side reactions are not modelled (no sourced yield).
Consequences (review 2026-10-28-pfd-lci-review#8): the propane of the fresh feed (2.5 mol%)
passes the ethane coils uncracked (propane rises across H101 because the ethane set also makes
some) and is cracked only in H103 after the C3 splitter. H103 reproduces only three BREF propane
yields; the remaining carbon goes to CH4 (25 wt%) with 0.3 wt% H2 and no C4+, so its H2 and
C4+ slate is not the BREF's. The effect is small: the propane coil sees 7.6 t/h of 225 t/h
hydrocarbon feed.

## D-006 Balance method
`scripts/balance.py` (run with `cheme run`) converges the ethane and propane recycles and the
firebox heat balance and writes the stream values. Separators and columns are specified splits.
Feeds, separator outlets and duties are typed into `process/flowsheet.yaml` as ASSUMED with the
script as source. Mixers, the furnace coils, the hydrogenation reactors and the firebox are
recalculated by `cheme process propagate --fill` (provenance calculated) and agree with the
script. `cheme process reactors` reproduces the script's duties: H101 372.2 MW, H103 9.5 MW,
H102 -586.6 MW (= coils + convection steam + 1.5 % casing loss). Temperatures and pressures
are design choices.

## D-007 Heat recovery, quench and dilution steam (ASSUMED)
TLE outlet 350 C; SHP steam at 11500 kPa(a), 520 C from BFW at 115 C. BFW preheat and
superheat happen in the convection section, evaporation in the TLE: 416 t/h, exported (D-015).
The quench tower cools to 40 C at 150 kPa(a); its heat goes to cooling water. The usual use of
quench water heat for reboiling and DSG preheat is not credited. All process water (quench,
CGC drums, dryer) returns to the stripper/DSG on MP steam (1800 kPa(a)) and makes 0.30 kg/kg
dilution steam at 800 kPa(a). 3 % is blown down and replaced by BFW. Dissolved oil and
hydrocarbons are not modelled.

## D-008 Cracked gas compression and drying (ASSUMED)
Five stages, 150 to 3600 kPa(a) (ratio 1.89 per stage, inside OLE's 17-35 bar(g)),
intercooling to 40 C, isentropic efficiency 0.78, ideal gas. The caustic tower sits after
stage 3. The knock-out drums remove water only (no hydrocarbon condensate). The dryers remove
all water. Regeneration gas and heat are not modelled.

## D-009 Caustic wash (ASSUMED)
CO2 + 2 NaOH -> Na2CO3 + H2O, complete. Fresh caustic 10 wt% at 3 mol NaOH per mol CO2. Spent
caustic goes to treatment outside the boundary. H2S, red oil and dissolved hydrocarbons are not
modelled. NaOH comes from the library's chlor-alkali-1 (boundary feed).
The 3:1 ratio has no source: it is an ASSUMED excess (one third of the NaOH leaves unused), and
the feed CO2 (0.2 mol%, D-003) is ASSUMED too. Together they set about 10 kg NaOH and 95 kg spent
caustic per t ethylene, so both LCI exchanges (feed:CAUSTIC, product:SPENTCAUSTIC) are flagged
in `lca/lca.yaml` as upper-bound assumptions (review #9).

## D-010 Separation sequence and splits (ASSUMED)
Front-end demethaniser (named in the BREF §3.2.2.4 as one of three schemes): all H2 and CH4
overhead with 0.3 % of the ethylene. A cold box gives 95 mol% H2 for the converters; the rest
goes to fuel. Deethaniser and depropaniser are sharp splits. The C2 splitter has a
pasteurisation vent (all H2/CH4 and 0.2 % of the ethylene, to fuel); its bottoms carry
1 mol% ethylene back to the furnace. The C3 splitter bottoms carry 5 mol% propylene. The
debutaniser gives crude C4 overhead and pyrolysis gasoline as bottoms.
Rejected for now: front-end deethaniser/depropaniser with front-end hydrogenation. It may save
energy (BREF §3.3.4.3) but needs a hydrogenation model of the full cracked gas.

## D-011 Acetylene and MAPD hydrogenation (ASSUMED)
Tail-end, adiabatic (declared in `process/simulation.yaml`). 80 % of the acetylene to
ethylene and 20 % to ethane; 90/10 for MAPD to propylene/propane. H2 is fed at 1.5 mol per mol
alkyne. No selectivity was sourced: these are placeholders to replace with catalyst data.

## D-012 Thermodynamics and the gated energy balance
No core property package covers C2+ hydrocarbons (`air-pr-chemsep`, `syngas-pr-vapor` only),
so `cheme process props` fills nothing. DWSIM simulation is not qualified for this mixture
(core #315), and the stream energy balances are "not evaluable" in `cheme process energy`.
Gated step: the energy closure of the separation train and an equilibrium-stage design of the
columns (relative volatilities, stages, reflux) wait for a qualified Peng-Robinson/SRK
package for light hydrocarbons in core (#315). The reactor and firebox energy closure is
evaluated by core on ideal-gas data (D-006). The LCI "energy closure 57.8 %" of
`cheme assess lca --balance` counts only utilities, not the fuels' LHV, and does not measure the
plant's heat balance.

## D-013 Fuel system and firebox (ASSUMED)
Tail gas (87 mol% H2), the C2 and C3 vents and a natural-gas make-up (95 % CH4) are burnt with
15 % excess air (3.2 vol% O2 dry). The stack is at 120 C and the casing loss is 1.5 % of the
LHV. The natural-gas make-up (9.6 t/h) closes the firebox heat balance. Fired duty is 611 MW
LHV = 17.6 GJ/t ethylene. There is no fuel gas export: the fuel gas co-product is used in the
furnaces.

## D-014 Refrigeration, columns, utility levels (ASSUMED)
Column duties are (R+1) x distillate x heat of vaporisation (thermo). Reflux ratios: deethaniser
1, C2 splitter 4, depropaniser 1, C3 splitter 15, debutaniser 1. The deethaniser,
depropaniser, C3 splitter and debutaniser reboilers run on LP steam 450 kPa(a). The C2
splitter (T502) and demethaniser (T401) reboilers are not modelled: in a real cracker they are
heated by condensing refrigerant or by cracked-gas chilling, but neither duty is in the
flowsheet and nothing is credited against the refrigeration load. Refrigeration loads are the
chilling train (70 % of the condensation at the propylene level), the demethaniser, deethaniser
and C2 splitter condensers, charged in full to K701. COP is 60 % of Carnot per level,
condensing at 40 C. Cooling water 25/35 C.
The condenser duties use the pure key component's latent heat (ethane for the deethaniser,
whose overhead is 67 mol% ethylene near its critical point; ethylene for the C2 splitter).
Upper bound (review 2026-10-28-pfd-lci-review#2): the refrigeration shaft power (Q402,
78.3 MW, about twice the CGC's 40.6 MW, whereas the CGC is normally the largest machine of an
ethane cracker) is therefore a conservative upper estimate, and so is feed:POWER
(0.87 kWh/kg). Crediting the T401/T502 reboilers and using mixture latent heats waits for
the qualified property package (D-012, core #315).

## D-015 Machine drives in the inventory
The CGC (40.6 MW) and refrigeration compressors (78.3 MW) are shown as electric motors
(feed:POWER) and the SHP steam as an export (product:HPS, 337 MW of steam enthalpy). A real
cracker drives them with SHP steam turbines, which would net most of the export against the
power. Keeping both gross exchanges makes the inventory transparent; the netting is a later
design choice.
Consequence for the LCI (review #3): the SHP export carries no burden. It is outside the mass
allocation, while the fuel that preheats and superheats it (convection duty Q102, 196 MW, about
32 % of the 611 MW fired) and that fuel's CO2 are allocated to the hydrocarbon products, and
the compressors are charged again as grid power. The CO2 and power per kg ethylene are
therefore both gross. This is stated next to the CO2 figure in `process.yaml` and in the
allocation `source:` of `lca/lca.yaml`. Open before the allocation is decided: a scenario that
nets HPS against POWER (steam-turbine drives) or credits the export by substitution.

## D-016 Preliminary gate-to-gate LCI
Functional unit 1 kg polymer-grade ethylene at the gate. Every foreground exchange comes from
the flowsheet (feeds, products, energy streams). Every background is left unmapped
(`missing:` names the activity to link: ethane from NGL fractionation, natural gas, grid
electricity HV, site MP/LP steam from utility-steam-ng-boiler, cooling water from
utility-cooling-tower, NaOH from chlor-alkali-1, wastewater treatment from utility-wwtp).
These are gaps, not zeros (ADR 0022). Mass allocation over ethylene, propylene, crude C4 and
pyrolysis gasoline is proposed (ethylene share 91.6 %). `lca/inventory.csv` is per functional
unit with the mass allocation applied to the inputs and emissions, while the co-products are
listed unallocated; `lca/dataset.yaml` (per hour) is the unallocated dataset (corrected after
review #1). `lca/mappings.yaml` holds no overrides yet.
Missing registry entries (for the consolidated chemicals PR): ethylene (polymer grade),
propylene (polymer grade), ethane, natural-gas, sodium-hydroxide, crude C4 / 1,3-butadiene,
pyrolysis-gasoline, nitrogen-oxides, carbon-monoxide, dinitrogen-monoxide.

## D-017 Emissions not carried by streams
Firebox: activity 2199.3 GJ/h LHV; flue gas 239.3 Nm3 dry at 3 % O2 per GJ (balance script).
NOx 100 mg/Nm3 is the upper end of the new-furnace BAT-AEL (BREF Table 13.1), giving
23.9 g/GJ. CO 50 mg/Nm3 is the upper end of the indicative 10-50 (Table 13.1 note 3), giving
12.0 g/GJ. Dust 7.1 mg/Nm3 is the upper end of Table 3.4, giving 1.7 g/GJ. CH4 1 g/GJ and N2O
0.1 g/GJ are IPCC defaults for natural gas, used as a proxy for the H2-rich fuel. A high-H2
fuel tends to raise NOx (BREF §3.3.1.1.1).
Open, not quantified: decoking (CO, CO2, dust), fugitive VOC (BREF: 30-1925 t/a per plant),
SO2 from sulphur doping, non-routine flaring, effluent loads. Each is declared in
`emission_exclusions` with its reason, not as negligible.

## D-018 Plausibility checks
- Ultimate ethylene yield 0.788 kg/kg fresh feed (S101, 95.8 wt% ethane), 0.82 kg/kg ethane.
- Fired fuel 17.6 GJ/t ethylene against the BREF's 13.5-16.2 GJ/t for the cracking section
  (§3.3.4, ethane and naphtha together). Ours is somewhat higher; it includes SHP superheat and
  BFW preheat.
- Shaft power 3.42 GJ/t (electric drives, CGC plus refrigeration). At a power-plant efficiency
  of 35-40 % this is 8.6-9.8 GJ/t primary, at or below the lower end of the BREF's
  9.8-12.5 GJ/t. The comparison is loose: the BREF range covers compression and separation
  including steam and refrigeration, ours is shaft power only, and the refrigeration part is
  an upper estimate (D-014).
- Furnace CO2 0.472 kg/kg ethylene unallocated; 0.433 kg/kg ethylene with mass allocation
  (91.6 %). Both include the fuel for the exported SHP steam (D-015).

## Open inputs and next stage
Sourced feed specification and capacity; sourced hydrogenation selectivities; a coke make and
decoking schedule; quench and dilution steam heat integration; drive choice (D-015); a
qualified property package (core #315) for columns and the energy balance. Next stage: basic
engineering of the separation train with simulated columns once core #315 allows. Before that:
link the LCI backgrounds (library processes first) and decide the allocation.
No stage sign-off (review #10): this case study is not taken to a concept sign-off in this
issue. The concept gate `layout-plot-plan` (and the basic and detail gates for P&IDs, layout,
lifting, MTO and datasheets) fail on purpose because the plot plan, P&IDs and layout are outside
its scope; `cheme check --stage concept --write` would be refused until a plot plan exists.
