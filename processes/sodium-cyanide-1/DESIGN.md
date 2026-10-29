# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue ChemE-as-Code/process-library#150. Run of 2026-10-28: library at `cc5624f` (main) on
branch `case/sodium-cyanide-1`, cheme-as-code 0.8.0 (pyDEXPI 2.1.0). Stage: concept (design
basis, balanced BFD/PFD, preliminary gate-to-gate LCI). Every number below is in our own words
with its source; values without one are marked ASSUMED.

## Source register

| id | source | locator | read status | reuse | used for |
|---|---|---|---|---|---|
| SRC-1 | US 6,596,251 B2, *Hydrogen cyanide synthesis process* (Degussa, 2003), https://patents.google.com/patent/US6596251 | background; detailed description sections 1-3; Table 2 (runs 1-7) | full text read (web page) | patent, public document; facts only, restated | overall reaction and enthalpy; air-operated converter feed ratios and HCN yield (run 1); gauze type and temperatures; quench outlet range; ammonia scrubbing options; HCN absorption in water to 2-3 wt% and rectification to >99.5 wt%; specific output per gauze area |
| SRC-2 | US 4,847,062 A, *Process for production of sodium cyanide* (Du Pont, 1989), https://patents.google.com/patent/US4847062A/en | Example 1 (commercial converter gas, wt%); examples 2-8; Tables 1-3 | text read up to Table 3 (the last 22 % of the page, Table 4, not read) | patent, public document; facts only | by-product distribution of the converter gas (NH3, CH4, CO, CO2 per HCN); 50 wt% caustic; free-NaOH practice; crystalliser 70 C / 100 mm Hg; mother liquor NaCN/water ratio; cake moisture range; product impurity levels |
| SRC-3 | Ullmann's Encyclopedia, *Cyano Compounds, Inorganic*, doi:10.1002/14356007.a08_159.pub2 | - | NOT read in this run (licensed); named in the issue as the route reference lead | citation only | not used for any value |
| SRC-4 | `cheme chemistry thermo` (chemicals / thermo, offline): ATcT, CRC, TRC, HEOS data | process/materials.yaml `source:` per component | tool output | open packages | ideal-gas formation data and heat capacities to 1500 K |
| SRC-5 | `cheme chemistry library hcn_andrussow` | - | tool output | packaged | reaction stoichiometry and catalyst entry (model basis stoichiometry only) |

Searched without a usable number for this design: US EPA, *Inorganic Hydrogen Cyanide Listing
Background Document* (archive.epa.gov, scanned PDF without text); EPA cyanide NESHAP economic
impact analysis (only the contents were reachable); Western Australian EPA bulletins on the
Kwinana NaCN plant (capacities and emission permits, no consumption figures). An EU BREF chapter
on HCN/NaCN was not found in this run.

## D-001 Route and boundary (2026-10-28)
Decision: Solid sodium cyanide from HCN made by the Andrussow process (methane, ammonia and air
over Pt/Rh gauze), with ammonia recovery and recycle, HCN absorption in water and refining to
liquid HCN, neutralisation with caustic soda, evaporative crystallisation, drying and
briquetting. The tail gas (H2, CO, N2) is burned in a boiler inside the boundary so that the
plant's own emissions to air are explicit. Boundary feeds: natural gas (site grid), liquid
ammonia (library process ammonia-1), 50 wt% caustic soda (library process chlor-alkali-1), air.
Boundary products: solid NaCN, exported MP steam, flue gas, process water to cyanide
destruction/wastewater treatment (outside). Utilities: power, cooling water, chilled water.
Reason: the issue's case notes fix the route (Andrussow, caustic neutralisation, ammonia and
caustic as boundary feeds, containment and emissions explicit). Refining HCN before the
neutralisation (rather than absorbing the whole converter gas in caustic, as SRC-2 does) keeps
CO2 out of the caustic, so the product carries no co-crystallised carbonate and the balance needs
no carbonate chemistry (core #364).
Rejected: BMA (Degussa) methane-ammonia process without air (endothermic, externally fired; not
the route of the issue); Shawinigan process; HCN as a by-product of acrylonitrile (feed origin
then belongs to another process); direct absorption of the converter gas in caustic (SRC-2:
carbonate and formate in the product, a modelled electrolyte system needed); NaCN solution as
the product (the issue leaves solid or solution open; solid chosen as the traded form for
mining, solution would remove the crystalliser and dryer).
Assumptions: purchased natural gas modelled as methane; no HCN storage (liquid HCN goes
directly to the neutraliser).

## D-002 Capacity and product (2026-10-28)
Decision: 6.25 t/h solid product (150 t/d, 50 kt/a at 8000 h), 98.0 wt% NaCN, 1.0 wt% free
NaOH, 1.0 wt% water.
Reason: a single-train size of the order of the larger published NaCN plants (the Kwinana solid
plant reported output up to about 39 kt/a, WA EPA performance review 2013-2018); free NaOH is
kept in cyanide liquors to suppress HCN release and polymerisation (SRC-2 keeps 0.1-3 wt% free
NaOH in the absorber liquor).
Rejected: a published plant's exact basis (none available as an open source).
Assumptions: ASSUMED capacity, purity and hours; the carbonate and formate a real product holds
(SRC-2 examples: 2-4 % Na2CO3, 0.4-1.9 % formate with impure HCN) are not modelled; with refined
HCN they are expected to be lower.

## D-003 Feed states (2026-10-28)
Decision: natural gas as pure methane at 400 kPa(a); anhydrous liquid ammonia at 1100 kPa(a),
298 K; dry air 21/79 mol% O2/N2 with argon lumped into nitrogen; 50 wt% caustic at 313 K.
Reason: simplest states consistent with the library's ammonia and chlor-alkali products; SRC-2
uses 50 wt% caustic.
Assumptions: ASSUMED. Ethane and heavier hydrocarbons in a real natural gas form nitriles and
soot on the gauze (SRC-1 defines a natural gas with at least 88 vol% methane and ethane); not
modelled. Argon (about 0.9 mol% of air) is counted as nitrogen.

## D-004 Converter model (2026-10-28)
Decision: an adiabatic conversion reactor R-101 with five reactions: the Andrussow reaction
CH4 + NH3 + 1.5 O2 -> HCN + 3 H2O; ammonia decomposition to N2 and H2; CO formation from methane
(written as reforming); complete combustion of methane to CO2; hydrogen oxidation. Converter
feed ratios O2/NH3 = 1.15 and CH4/NH3 = 0.98 mol/mol and the HCN yield of 62.9 % on the NH3 fed
are those of the air-only run 1 of SRC-1 Table 2 (gauze at about 994 C in that laboratory
reactor, 7.6 vol% HCN in the reaction gas). The other conversions are fitted in
scripts/nacn_balance.py so that the outlet holds NH3, CH4, CO and CO2 in the mole ratios to HCN
of the commercial converter gas of SRC-2 Example 1 (NH3/HCN 0.311, CH4/HCN 0.018, CO2/HCN 0.100;
CO closes the carbon balance and lands within 10 % of that example's CO/HCN), with 99.9 % of the
oxygen consumed (SRC-1: oxygen conversion practically complete).
Result (cheme process propagate, calculated): converter gas 7.47 mol% HCN, 2.32 % NH3, 22.5 %
H2O, 11.1 % H2, 3.28 % CO, 0.75 % CO2, 0.14 % CH4, 52.4 % N2 (SRC-2 Example 1 converts to
7.5 % HCN, 2.3 % NH3, 22.3 % H2O, 14.3 % H2, 3.6 % CO; SRC-1 reports 6-8 vol% HCN in air
operation). With the unheated feed (349 K) the adiabatic outlet is 1429 K; cheme process
reactors gives a duty of 0.06 kW for R-101 at that temperature (energy balance closed on the
ideal-gas data of materials.yaml). This lies inside the 950-1200 C reaction range of SRC-1 and
above the 980-1050 C named there for air operation: heat losses of real converters are not
modelled. Every reaction is short of equilibrium at the outlet (ln(Q/K) from -9 to -51), so the
conversions are thermodynamically reachable.
Rejected: an equilibrium or Gibbs reactor (HCN is far from equilibrium; the Andrussow yield is
kinetic and mass-transfer controlled on the gauze); kinetics (no open rate law qualified for the
gauze; none invented).
Assumptions: the conversions other than the HCN yield are ASSUMED fits; the lumped CO path is
not a mechanism. `cheme validate` warns (`cheme.process-catalyst`, R101/S5) that the cold
converter inlet (349 K) lies outside the gauze temperature window: the window applies to the
gauze, not the feed gas. This is a known warning, left visible: no gate covers the rule, so
there is no gate acceptance to record, and no reviewer has accepted it (review
2026-10-28-pfd-lci-review#6).

## D-005 Feed preparation and pressures (2026-10-28)
Decision: air compressed to 180 kPa(a) by K-101 (isentropic efficiency 0.75, ASSUMED, outlet
369 K, 0.63 MW); liquid ammonia vaporised in E-001; methane, ammonia (fresh and recycled) and air
mixed in M-101 without preheat (349 K); converter 170/160 kPa(a); the waste heat boiler E-101
cools the gas to 523 K (inside the 100-400 C quench range of the Andrussow patents; SRC-1 names
150-200 C at the boiler outlet). Pressure drops ASSUMED.
Reason: SRC-1 teaches a preheat at most 200 C for its process and 200-400 C in older practice;
no preheat is the simplest case and the adiabatic temperature is already high (D-004).
Inherent safety: the mixed feed lies inside the flammable range of methane and ammonia in air;
flashback protection, ratio trips and relief are basic-engineering items, not designed here.

## D-006 Ammonia recovery and recycle (2026-10-28)
Decision: unconverted ammonia is absorbed in an ammonium phosphate solution and stripped, and the
ammonia is rectified and recycled to the converter (C-101, one lumped PFD step). 99 % of the
converter NH3 is recycled, 0.5 % leaves with the process water S10, 0.5 % slips to the HCN
absorber. The gas leaves C-101 saturated with water at 333 K. Stripping steam 10 kg LP steam per
kg NH3 recovered (3.8 MW).
Reason: SRC-1 names both options (dilute sulfuric acid giving ammonium sulfate, or a phosphate
solution with ammonia recycle); the recycle raises the overall ammonia yield to 78 % (0.437 kg
NH3 per kg product against 0.341 kg stoichiometric) and avoids an ammonium sulfate by-product.
Rejected: sulfuric acid scrubbing (an ammonium sulfate co-product to allocate, more ammonia).
Assumptions: recovery split and the steam rate are ASSUMED (no open source read gives them);
phosphate make-up is not quantified (open input); the phosphate loop is inside the lumped step.

## D-007 HCN absorption and refining (2026-10-28)
Decision: HCN is absorbed in chilled lean water (278 K) in C-201 to a rich water with 2.5 wt% HCN
(SRC-1: 2-3 wt% in the absorber sump in air operation), 99.9 % recovery; the tail gas leaves at
283 K saturated. C-202 strips and rectifies to liquid HCN with 99.5 wt% HCN (SRC-1: above
99.5 wt%). The bottoms pass a feed/bottoms interchanger (10 K approach) and the lean water
chiller E-202; 2.65 % of them are purged (S16) to remove the net condensed water. 0.05 % of the
converter HCN and the ammonia slip leave with the purge (about 470 ppm(wt) HCN).
Reason: the standard recovery scheme named in SRC-1; refined HCN gives a clean neutralisation.
Assumptions: recovery, purge loss, temperatures and duties ASSUMED; the acid stabiliser added
against HCN polymerisation (SO2, H3PO4 or H2SO4 in practice) is not quantified (open input).
Duties: reboiler = interchanger loss + HCN boil-up at reflux ratio 1 (enthalpy of vaporisation
of HCN 25.2 kJ/mol, ASSUMED near the NIST value); heat of absorption of HCN taken equal to its
condensation.

## D-008 Neutralisation, crystallisation and drying (2026-10-28)
Decision: liquid HCN reacts completely with 50 wt% caustic in R-401 at 343 K (NaOH for the HCN
plus the product's free NaOH), giving 45.3 wt% NaCN solution. A vacuum evaporative crystalliser
(343 K, 13.3 kPa(a): 70 C and 100 mm Hg of SRC-2 examples 6-7) evaporates 7.0 t/h of water with
LP steam (single effect); the mother liquor holds 0.80 kg NaCN per kg water (the filtrate of
SRC-2 Table 2), the centrifuge cake 10 wt% liquor (SRC-2: 8-21 wt% liquid in wet crystals), and
all filtrate returns to the crystalliser, so the free NaOH leaves with the cake liquor. An
indirect steam vacuum dryer (efficiency 0.8) dries the cake to 1 wt% water; the vapours are
condensed (E-401) and go to wastewater treatment.
Reason: SRC-2's wet process conditions; recycle of all filtrate avoids a NaCN-bearing purge.
Rejected: cheme's crystallizer model, which refuses the free NaOH (one solute and one solvent
only; cheme.process-propagate-crystallizer) - the outlets are the script's values instead (D-011).
Assumptions: heat of neutralisation about 12 kJ/mol HCN (ASSUMED, weak acid); NaCN hydrolysis to
formate and ammonia in the hot liquor not modelled (its NH3/HCN traces in the vacuum vent are an
emission gap); a multiple-effect or MVR crystalliser would cut the 4.5 MW steam (open).
Known inconsistency (review 2026-10-28-pfd-lci-review#3, open): the R-401 product holds about
0.84 kg NaCN per kg water at 343 K, above the 0.80 kg/kg of the mother liquor. The liquor value
is a filtrate that carries the accumulated free NaOH, which probably lowers the NaCN solubility
(common ion), so the R-401 product with less NaOH may still be undersaturated. No sourced NaCN
solubility against temperature and NaOH is available to show it (open input). Until it is,
basic engineering is to keep R-401 and its line to CR-401 above 343 K (heat-traced) or dilute
the caustic; the balance is not changed.

## D-009 Tail gas boiler (2026-10-28)
Decision: the tail gas (16 mol% H2, 4.8 mol% CO, 0.2 mol% CH4, 0.01 mol% HCN; LHV 17.3 MW) burns
completely with 15 % excess air in B-301; flue gas at 423 K to the stack; 15.4 MW MP steam.
Reason: SRC-1 notes the tail gas hydrogen is too dilute (below 18 vol%) to recover economically;
burning it for steam is the usual use and makes the stack the plant's single emission point to air.
Assumptions: complete combustion, stack temperature ASSUMED; boiler efficiency ASSUMED 89 % of
the tail gas LHV (the stack loss only: no radiation or blowdown loss), so the B-301 steam is an
upper bound (review 2026-10-28-pfd-lci-review#1; a real boiler loses a further 1-3 %); NOx and CO are
not estimated (emission gap in lca/lca.yaml); cheme cannot check the B-301 duty because the
heat-capacity fits start at 298 K and the tail gas is at 283 K.

## D-010 Utilities and energy (2026-10-28)
Decision: E-101 raises 15.2 MW and B-301 15.4 MW of saturated MP steam at 1500 kPa(a); the plant
uses 12.9 MW let down to LP (E-001 0.9, C-101 3.8, C-202 3.3, CR-401 4.5, DR-401 0.2 MW) and
exports 17.8 MW (2.85 kWh per kg product). Power 1.03 MW (K-101 0.63 MW, the rest a 0.4 MW
ASSUMED lump). Cooling water 298/308 K, 17.7 MW; chilled water 275/283 K, 4.8 MW.
The steam export is an UPPER BOUND (review 2026-10-28-pfd-lci-review#1): the converter is
adiabatic, 1429 K against about 1267 K at the sourced gauze of SRC-1 run 1 (D-004); E-101 cools
1429 -> 523 K with no loss (15.2 MW), and B-301 has no radiation or blowdown loss (D-009).
Scaling the E-101 duty to a 1267 K outlet gives roughly 2.5-3 MW less steam, so the export is
probably 15-20 % lower. The NaCN burden is not affected while the allocation shares are 1/0
(D-012), but the export must be corrected (converter heat loss as an R-101 duty, boiler losses)
before an energy or exergy allocation is applied.
The power of 1.03 MW does not include the chillers (review 2026-10-28-pfd-lci-review#4): the
4.8 MW of chilled water needs roughly 0.8-1.2 MW of compressor power at a COP of 4-6
(ASSUMED range), about as much again. That power belongs to the chilled-water background
(product:CHW in lca/lca.yaml), so 0.164 kWh per kg is the plant's own electricity, not its
whole electricity demand.
Assumptions: all duties are estimates of scripts/nacn_balance.py (simple sensible and latent
heats); steam levels, approaches and the power lump ASSUMED; no heat integration beyond the
interchanger of C-202.

## D-011 Model basis and gated steps (2026-10-28)
Decision: cheme calculates the mixer, pass-through, splitter, neutraliser, converter and boiler
outlets (propagate) and checks every block's mass, component and element balance (validate:
0 errors); the C-101, C-201, C-202, crystalliser and dryer outlets and all duties are given as
ASSUMED from scripts/nacn_balance.py.
Gated steps, by the cheme 0.8.0 messages: (a) no property package covers the converter gas with
HCN at 1429 K (syngas-pr-vapor has no HCN), the aqueous HCN/NH3/water absorption, or the
NaCN/NaOH electrolyte (core electrolyte/speciation and polar benchmarks, issue #150 names core
#364 and #315); `cheme process props`/`simulate` are therefore not run and energy closure of the
separations is not evaluable in core; (b) cheme's crystallizer model (solids, core #365) handles
one solute in one solvent and refuses the free NaOH of the liquor. The state of core #364/#365
could not be read from this environment (gh: issue not resolvable); the refusal in (b) is the
evidence for this route. `cheme maturity`: calculation maturity none (feeds assumed, specified
separations), as for the other concept cases.

## D-012 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml, functional unit 1 kg solid product (NACN) at the gate; every foreground
exchange from the flowsheet; backgrounds unmapped (`missing:` with the activity each should link
to); stack CO2 an elementary fossil emission; the zero-flow stack components (CO, CH4, H2, HCN,
NH3) mapped so that a later non-zero value is characterised. Allocation shares 1/0 (all burdens
on NaCN) instead of exergy, because the chemical exergy of NaCN is not sourced yet (stated in
`allocation.deviation`). Pt/Rh gauze as an ASSUMED consumable (50 kg twice a year), never cut.
Emission gaps declared: fugitive leaks, boiler NOx/CO, crystalliser vent and dryer dust,
flaring, storage.
Result per kg product: natural gas 0.501 kg, ammonia 0.437 kg, 50 % caustic 1.620 kg, power
0.164 kWh, process air 5.03 kg and combustion air 3.16 kg (free); MP steam export 2.85 kWh
(co-product), cooling water 2.84 kWh, chilled water 0.766 kWh, process water 2.22 kg to
treatment, flue gas 7.53 kg with 0.493 kg fossil CO2. Mass closes (10.747 kg in and out), and by
hand carbon (0.3748 kg C) and nitrogen (0.3598 kg N) close against the flowsheet; cheme reports
the element balance as not assessable only because the consumables have no composition.
Supplies outside the flowsheet (review 2026-10-28-pfd-lci-review#2), each a consumable with
`missing:` so that it shows as a gap: boiler feed water, the phosphate make-up of C-101 and the
HCN stabiliser acid. Steam convention: the exported MP steam is an energy co-product
(product:MPSX, kWh) and its condensate is not returned, so the plant supplies the water of
the export (bfw-export, 27.2 t/h, leaving with the steam) and the make-up for its own
blowdown and condensate losses (bfw-makeup, 3.4 t/h, to drains), 4.90 kg per kg product
together, from the steam duties at 2352 kJ/kg (feed water at 378 K). Phosphoric acid
(20 t/a) and the stabiliser (27 t/a as H2SO4, about 0.1 wt% on the HCN, retained in the
product as sodium sulfate) are ASSUMED placeholders with a very wide uncertainty, recorded so
that the gap is visible. With the feed water the mass balance closes at 15.65 kg in and out.
The gauze consumable counts the whole charge each campaign; when it is mapped, the net
Pt/Rh loss is to be modelled instead (review 2026-10-28-pfd-lci-review#5).
Energy closure (review 2026-10-28-pfd-lci-review#7): `cheme assess lca` reports 75.6 %. Its
energy ledger counts only electricity (1028 kW) and heat rejected to cooling and chilled water
(22 509 kW) against the steam exported (17 796 kW), and leaves out the enthalpy of the material
streams. The feeds' chemical energy, the heat of the exothermic Andrussow reactions and the
heating value of the tail gas burned in B-301, which raise the steam and cause most of the
heat rejected, are therefore not in it. The missing quarter is a limit of the ledger, not a
loss in the balance. The energy balance of R-101 closes in cheme (D-004); that of the
separations cannot be evaluated in core (D-011).

## Open inputs, missing registry entries and next stage

Open inputs (each ASSUMED now): a licensor or open plant basis for the converter (gauze area,
heat loss, preheat, pressure, platinum loss per kg HCN, gauze campaign); ammonia recovery split
and stripping steam; phosphate and HCN-stabiliser acid make-up; HCN absorber/stripper recoveries
and the purge's HCN content; heat of neutralisation and of crystallisation; NaCN solubility
against temperature with NaOH present; NaCN hydrolysis (formate, vent NH3/HCN); tail gas boiler
NOx and CO factors; the chemical exergy of NaCN (for exergy allocation of the exported steam);
Ullmann's chapter (SRC-3) not read.

Missing in the shared chemicals registry (`chemicals/chemicals.yaml`, for the consolidated
PR): `sodium-cyanide` (main product, solid 98 wt%; possibly a solution grade), `hydrogen-cyanide`
(intermediate), `ammonia` (feed from ammonia-1), `sodium-hydroxide` (feed, 50 wt% solution
grade, from chlor-alkali-1); for the consumable `platinum` and `rhodium` (gauze). Present and
used: methane, air, carbon-dioxide, steam, electricity, cooling-water, chilled-water, wastewater.

Recommended next stage: (1) source the converter basis and the downstream recoveries (Ullmann
SRC-3, open literature on Andrussow reactors, the EPA cyanide NESHAP background), (2) check the
core electrolyte and solids support for NaCN/NaOH/water and, when qualified, replace the script
values of C-201/C-202/CR-401 by cheme models (`process props`, `simulate`, the crystallizer with
a second solute), (3) source the boiler emission factors and the NaCN exergy and map the LCI
backgrounds (ammonia-1 and chlor-alkali-1 datasets pinned explicitly), (4) then P&IDs and HAZOP
(HCN toxicity, flammable converter feed, HCN polymerisation).
