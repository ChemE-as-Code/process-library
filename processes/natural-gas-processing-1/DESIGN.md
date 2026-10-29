# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Natural gas processing, issue ChemE-as-Code/process-library#181. Concept stage, agent run of
2026-10-28 with cheme 0.8.0 (pyDEXPI 2.1.0) on library commit cc25cf3. Every number in the
flowsheet comes from `scripts/balance.py` (run with `cheme run scripts/balance.py`); this file
keeps the decisions and their sources, not a second copy of the stream table
(`cheme process streams`).

## 1. Route and boundary memo

**Product first.** The plant makes pipeline sales gas (main product) and a C2+ natural gas
liquid (co-product) from a raw shale gas. The issue asks for one molecular feed and one treating
train; the case notes fix the spine: inlet separation, amine acid gas removal, TEG dehydration,
turbo-expander NGL recovery, sales gas compression, sulfur recovery only if the sourced feed has
H2S.

**Feed.** Bullin and Krouskop (2009) give open, well-by-well compositions of six US shale plays
(Tables 1-6). Barnett well 2 (Table 1: 81.2 % C1, 11.8 % C2, 5.2 % C3, 0.3 % CO2, 1.5 % N2) was
chosen because it is rich enough that ethane and propane recovery is the point of the plant, it
carries CO2 (which must come out ahead of the cryogenic section) and the paper says the Barnett
plants combine compression, amine CO2 treating, cryogenic separation and fractionation (p. 3),
i.e. exactly the requested line-up. Marcellus well 3 (0.9 % CO2) was the alternative; New
Albany/Antrim/Haynesville gases are lean (no NGL case) and the paper notes Haynesville carries
H2S traces handled by scavengers. The source normalises to the reported compounds: H2S, C4+,
water, mercury and helium are not reported.

**Line-up and why each unit is there** (skill `tech-gas-processing`):

| unit | present because |
|---|---|
| V-101 inlet separator / slug catcher | free water arrives with gathered gas; no condensate (no C4+ reported) so no stabiliser |
| MDEA absorber/regenerator (T-201, V-202, T-202) | CO2 freezes in a demethaniser; removal depth is set by the cold section, not by the 2-3 % sales limit |
| TEG contactor and still (T-301, V-302, T-302) | bulk dehydration to the 7 lb/MMscf pipeline value (case notes) |
| molecular sieve driers (A-303) | glycol drying is not enough before cryogenic temperatures: the expander section needs ppm-level water (Bullin and Krouskop p. 2; skill `tech-gas-dehydration`) |
| cold box, cold separator, turbo-expander, demethaniser (E-401, V-401, K-401, T-401) | ethane and propane recovery (GSP-type) |
| booster C-401 and residue compressor K-501 | the feed is let down to demethaniser pressure; the residue must be recompressed |
| fuel gas header and fired heaters (M601, H-601) | TEG reboiler and regeneration gas heater fire the flash gases and a residue draw |

Absent, with reason: sulfur recovery and tail gas treating (no H2S in the sourced feed, D-002);
mercury guard bed (no mercury analysis; to be asked, D-005); nitrogen rejection (1.5 % N2 gives
1.8 % in the sales gas, inside a typical 4-5 % inert limit); condensate stabilisation and NGL
fractionation (no C4+; fractionation is outside the boundary).

**Boundary (D-001).** Raw gas at the plant inlet flange to sales gas and NGL at their pipelines,
acid gas, still vent and flue gas to air, produced water to disposal. Field gathering and inlet
compression, NGL fractionation, utility generation (power, steam, cooling water) and storage are
outside; utilities enter as energy terminals.

## 2. Source register

| # | source | locator | read | reuse | used for |
|---|---|---|---|---|---|
| S-1 | Bullin, K., Krouskop, P. (2009) Composition variety complicates processing plans for US shale gas, Oil & Gas Journal 107(10); open copy https://www.bre.com/PDF/Composition-Variety-Complicates-Processing-Plans-for-US-Shale-Gas.pdf | Table 1 (p. 3) Barnett compositions, wells 1-4; p. 3 Barnett plant capacities and line-up; p. 2 dehydration and acid gas text | full text read | facts only (composition values cited, table not copied) | feed composition (D-003), capacity range (D-002), line-up |
| S-2 | US EPA Natural Gas STAR, Lessons Learned "Optimize glycol circulation and install flash tank separators in glycol dehydrators", https://19january2021snapshot.epa.gov/sites/static/files/2016-06/documents/ll_flashtanks3.pdf | p. 2 (flash tank captures about 90 % of the methane); p. 3 (2-5 US gal TEG per lb water, rule of thumb 3); p. 6 Exhibit 6 (TEG absorbs about 1 scf gas per gal) | read | US government work; facts cited | TEG circulation, absorbed gas, flash recovery (D-008) |
| S-3 | US EPA AP-42 section 1.4 Natural Gas Combustion, https://www.epa.gov/sites/default/files/2020-09/documents/1.4_natural_gas_combustion.pdf | Table 1.4-1 (small boilers <100 MMBtu/h, uncontrolled NOx 100, CO 84 lb/10^6 scf); Table 1.4-2 (CH4 2.3, N2O 2.2, PM total 7.6, VOC 5.5 lb/10^6 scf); basis 1020 Btu/scf HHV | tables read | US government work | combustion emission estimate (D-014) |
| S-4 | US EPA AP-42 section 5.3 Natural Gas Processing (1995), https://gaftp.epa.gov/ap42/ch05/s03/final/c05s03_1995.pdf | sections 5.3.1-5.3.2 | summary only | US government work | emission sources of a gas plant (acid gas, glycol still, compressor drivers, leaks) (D-014) |
| S-5 | US 11 473 837 B2, Background, https://patents.google.com/patent/US11473837B2/en | Background: GSP limited to about 90-96 % ethane and 90-99 % propane recovery | summary of the Background only | patent text not copied | recovery basis (D-009) |
| S-6 | Wikipedia "Natural-gas processing", https://en.wikipedia.org/wiki/Natural-gas_processing | section Natural gas quality standards (US: 7 lb water/MMscf, CO2 2-3 %, H2S 0.25 grain/100 scf, about 1035 Btu/scf +-5 %); section NGL fractionation train (example demethaniser at about 20 bar, overhead about -98 degC) | read | discovery source only (CC BY-SA text not copied) | sales gas specification and plausibility of the demethaniser conditions (D-009, D-010); to be replaced by a receiving-pipeline tariff |
| S-7 | Ullmann's Encyclopedia, Natural Gas, doi:10.1002/14356007.a17_073 | - | not read (identity from the issue) | licensed | route identity only |
| S-8 | Wagner and Pruss (1993), IAPWS saturation pressure of water | equation as coded in scripts/balance.py | from memory, standard form | facts | water saturation pressure |
| S-9 | Bukacek water content correlation of lean sweet natural gas (IGT Research Bulletin 8) | form W = 47484 pv/p + B, log10 B = -3083.87/(459.6 + t) + 6.69449 (lb/MMscf, psia, degF); validity 60-460 degF, 15-10 000 psia | **primary not read**. The B-term constants and units are confirmed by a secondary open copy (https://www.memoireonline.com/09/19/10886/m_Optimisation-d-un-procede-de-traitement-de-gaz-naturel7.html) and the validity range by PetroSkills (https://www.petroskills.com/blog/lean-sweet-natural-gas-water-content-correlation~n4520, which also says it needs the Wagner-Pruss vapour pressure); the 47484 coefficient is quoted from memory, to verify | facts | water content of saturated gas (D-004), used inside its range (104-113 degF, 860-870 psia); check: 60 lb/MMscf at 100 degF and 1000 psia, consistent with the usual McKetta-Wehe value |
| S-10 | `chemicals` package via `cheme chemistry thermo` (ATcT formation enthalpies, Poling 5th ed. cp) | process/materials.yaml | tool output | open (MIT) | heating values, ideal-gas heat capacities |

No benchmark answers were searched for; the design is independent.

## 3. Reaction and model evidence

The plant is a separation plant. Its only reactions are the complete combustion of fuel gas in
H-601 (`process/reactions.yaml`: CH4, C2H6, C3H8 to CO2 and H2O, conversion 1.0, heats from the
ATcT formation enthalpies); `cheme process streams` closes this step as a reactive balance
(extents CH4 4.945, C2H6 0.296, C3H8 0.114 kmol/h). Incomplete combustion products are not in
the balance but estimated in the LCI from AP-42 (S-3).

CO2 absorption in aqueous MDEA is reactive chemistry (carbamate-free acid-base reaction for a
tertiary amine). It is represented as a **specified split** (CO2 to 50 ppmv, ASSUMED loadings),
not as equilibrium or rate chemistry: no sourced VLE/speciation model for MDEA-CO2-water is used
and core cannot evaluate electrolyte speciation (core#364). The NGL recovery, TEG drying and
mole sieve are likewise **specified recoveries/splits** (sourced where the register says so,
ASSUMED otherwise), not predicted. No kinetics or vendor data are used.

## 4. Decisions

## D-001 Boundary: inlet flange to sales gas and NGL pipelines (2026-10-28)
Decision: as in section 1. No storage, no fractionation, no utility generation.
Reason: the issue asks for one treating train with a defined feed and product.
Rejected: including NGL fractionation (needs C4+ data the source does not give).

## D-002 Capacity 100 MMscf/d, 8000 h/a; no sulfur recovery (2026-10-28)
Decision: 100 MMscf/d raw gas, dry basis at 60 degF and 14.696 psia (4980.3 kmol/h, 96.7 t/h);
8000 h/a. No Claus unit.
Reason: inside the 35-1000 MMscf/d of the Barnett plants listed by S-1 (p. 3); the paper also
says the industry added the equivalent of a 100 MMscf/d cryogenic plant every three months.
The sourced feed reports no H2S.
Assumptions: capacity and hours ASSUMED; site a generic Barnett-type location (Texas), not chosen.

## D-003 Feed composition: Barnett well 2 of Bullin and Krouskop (2009) (2026-10-28)
Decision: dry composition 81.2 / 11.8 / 5.2 / 0.3 / 1.5 mol-% C1 / C2 / C3 / CO2 / N2 (S-1,
Table 1, well 2).
Reason: rich, CO2-bearing, sweet; matches the requested line-up (section 1).
Assumptions: unreported species (H2S, C4+, Hg, He, O2) taken as absent. This is the main
limitation of the feed: a real rich Barnett gas carries some C4+, which would add a condensate
stabiliser and change the NGL.

## D-004 Inlet state and water (2026-10-28)
Decision: 6000 kPa(a), 313.15 K at the inlet (ASSUMED, after field compression); gas saturated
with water (Bukacek, S-9: 75 lb/MMscf, 142 kg/h) plus 1 bbl free water per MMscf (662 kg/h,
ASSUMED). V-101 removes all free water; no hydrocarbon liquid.
Rejected: a low-pressure inlet with inlet compression (would move power into the plant; not
specified by any source).

## D-005 Mercury (2026-10-28)
Decision: no mercury guard bed in this concept.
Reason: S-1 gives no mercury analysis. The brazed aluminium cold box E-401 needs one if mercury is
present (skill `tech-gas-processing`). Open input: ask for the mercury analysis.

## D-006 Balance method: specified-split script (2026-10-28)
Decision: `scripts/balance.py` computes every stream from the feed, the sourced and ASSUMED
recoveries and removal depths (D-007..D-011) and ideal-gas heat capacities; the flowsheet carries
its values as `assumed` with source `scripts/balance.py`. cheme checks every block and step
balance (all within 1 kg/h + 0.5 %) and the element balance of H-601.
Reason: no benchmarked property package covers the mixtures (D-012), so `cheme process simulate`
and `props --fill` cannot be used credibly; `propagate` handles only the splitter, mixer and
combustion step (checked: `cheme process propagate --check` passes).

## D-007 Acid gas removal: MDEA 45 wt-%, CO2 to 50 ppmv, acid gas vented (2026-10-28)
Decision: lean MDEA 45 wt-%, lean/rich loading 0.005/0.25 mol CO2/mol (ASSUMED); CO2 in the sweet
gas 50 ppmv (ASSUMED, the usual depth ahead of an ethane-recovery expander plant, skill
`tech-gas-acid-gas-removal`); 0.02 % of each hydrocarbon co-absorbed (ASSUMED), 90 % of it and
3 % of the CO2 released in the rich flash drum at 600 kPa(a) to fuel (ASSUMED); acid gas leaves
the condenser water-saturated at 323 K, 170 kPa(a) and is vented (no H2S: no thermal oxidiser
or sulfur recovery). Reboiler on LP steam 450 kPa(a), 1.0 lb steam per US gal lean amine
(ASSUMED practitioner rule; no open primary source found) = 1.08 MW, 6.0 GJ/t CO2 (high because
at 0.3 % CO2 the duty is set by circulation, not by CO2 load). Condenser and lean cooler reject
the reboiler duty plus pump work to cooling water. Demineralised make-up water replaces the
water the sweet gas and the acid gas carry away (61 kg/h).
Rejected: MEA (higher regeneration energy and degradation), membranes (CO2 too low).
Open: MDEA losses (consumable, 15 t/a ASSUMED rule of thumb) and the amine VLE.

## D-008 Dehydration: TEG to 7 lb/MMscf, then molecular sieve (2026-10-28)
Decision: TEG contactor dries to 7 lb/MMscf (S-6); 3 US gal TEG per lb water removed (S-2, p. 3)
= 1121 gal/h (4.75 t/h at 1120 kg/m3 ASSUMED); lean TEG 99.0 wt-% (ASSUMED); 1 scf gas absorbed
per gal TEG (S-2, Exhibit 6), 90 % of it recovered in the flash tank to fuel (S-2, p. 2; applied
to all light components, ASSUMED beyond methane), the rest leaves with the still vent. Electric
lean TEG pump (no energy-exchange pump, so no pump gas). Reboiler duty: rich TEG heated from
423 to 477 K plus vaporisation of the removed water, x1.25 for reflux and losses (ASSUMED) =
0.37 MW, fired. Molecular sieve (two-bed TSA, zeolite 4A ASSUMED) removes the remaining water
(13 kg/h); regeneration with 8 % of the gas heated to 561 K during half the cycle (ASSUMED) =
0.66 MW fired, the same duty rejected in the regeneration gas cooler; regeneration gas loop
internal to A-303. Adsorbent 40 t replaced every 4 years (ASSUMED).
Note: core can now calculate a TSA bed with sourced isotherms (core PR #398); none are bundled
for natural gas and none were sourced here, so the split stays specified.

## D-009 NGL recovery: GSP-type expander plant, 90 % C2 and 98 % C3 (2026-10-28)
Decision: ethane recovery 90 % and propane 98 % of the cold-box feed, inside the GSP range of
S-5 (90-96 % C2, 90-99 % C3; lower end for ethane, ASSUMED); 60 % of the residual CO2 to the
NGL (ASSUMED); NGL C1/C2 0.02 mol/mol (ASSUMED). Feed chilled to 238 K at 5800 kPa(a); cold
separator liquid fractions ASSUMED (C1 4 %, C2 25 %, C3 60 %, CO2 20 %, N2 1 %); expander to
2200 kPa(a) (demethaniser pressure, comparable to the example of S-6), isentropic 0.85
(ASSUMED); ideal-gas expander outlet 197 K and 1.79 MW (a real-gas calculation would give a
colder outlet; D-012). Demethaniser overhead 173 K, bottoms 283 K (ASSUMED). The side and bottom
reboilers take their heat from the inlet gas in E-401 (Q13, duty not calculated); no external
refrigeration (ASSUMED: the feed is rich, a propane chiller may be needed; to check with a
qualified simulation). NGL pumped to 7000 kPa(a).
Result: overall recovery from the raw gas 89.96 % C2 and 97.95 % C3 (the small difference is
the co-absorption and TEG losses).

## D-010 Residue compression, cooling water and auxiliaries (2026-10-28)
Decision: booster C-401 on the expander shaft (mechanical efficiency 0.97, isentropic 0.80,
ASSUMED) to 3353 kPa(a); electric-motor residue compressor K-501 to 7050 kPa(a) (isentropic
0.80, motor 0.96, ideal gas, ASSUMED): 3.52 MW shaft, 3.67 MW electric, discharge 425 K, single
stage; aftercooler to 313 K on cooling water (5.08 MW). Sales gas at 7000 kPa(a) (ASSUMED
delivery pressure). Cooling water 30/40 degC (ASSUMED, warm climate). Site auxiliaries 150 kW
(ASSUMED). Pumps eta 0.70, motors 0.95 (ASSUMED).
Rejected (for now): gas-turbine drive of K-501 (common in gas plants; would move 3.7 MW of power
into roughly 10-12 MW of fuel and its emissions; a scenario for the next stage) and air coolers
(would move cooling-water duty into fan power).

## D-011 Fuel gas and fired heaters (2026-10-28)
Decision: the amine and TEG flash gases (60 kg/h) and a residue-gas draw after the booster
(55 kg/h, 0.080 % of the residue gas) fire H-601 (TEG reboiler firebox and regeneration gas
heater, one tag at concept stage); 80 % efficiency on LHV and 15 % excess dry air (ASSUMED),
complete combustion, flue gas at 473 K. Fuel LHV 40.3 MJ/kg (it carries the flash CO2).

## D-012 Thermodynamic models: no qualified package; ideal-gas estimates (2026-10-28)
Decision: no property method is applied to the streams (`property_method: placeholder`).
Evidence: `cheme process props --coverage` reports no package for any stream: air-pr-chemsep
covers N2/O2/Ar only, syngas-pr-vapor lacks ethane, propane and water; `cheme process methods`
claims DWSIM Peng-Robinson only for N2/O2/Ar. The right methods for this plant (skill
`thermodynamic-model-selection`) would be Peng-Robinson or GERG-2008 for the hydrocarbon
sections with sourced binary parameters, an electrolyte model for MDEA-CO2-water (core#364) and
a polar/association model for TEG-water (core#315 polar benchmark). Consequence: the cold-box
energy balance, the expander and compressor duties, the TEG and amine heats are ideal-gas or
rule-of-thumb estimates, and energy closure is not evaluated (gated, section 6).

## D-013 Equipment list: PFD items only; line list empty (2026-10-28)
Decision: the 17 tags of the PFD steps with service, ASSUMED design pressure/temperature
placeholders and material notes; packages (regenerators, mole sieve skid) kept as one tag. The
line list stays empty until P&IDs exist (P&IDs, layout, HAZOP, datasheets out of scope).

## D-014 Preliminary gate-to-gate LCI (2026-10-28)
Decision: `lca/lca.yaml`, functional unit 1 kg sales gas at the gate, cut-off system model,
**energy allocation** between sales gas and NGL by LHV (48.43 and 47.03 MJ/kg from the ATcT
formation enthalpies; sales gas share 72.2 %; mass allocation gives 71.6 %, no allocation
100 %). Every background is declared `missing:` with the activity it should connect to (raw gas
production, grid electricity, LP steam, cooling water, demineralised water, produced water
disposal, MDEA, TEG, zeolite and their disposal): gaps, never 0, no licensed values. Emission
products (acid gas, still vent, flue gas) are split into elementary emissions: CO2, CH4, C2H6,
C3H8 fossil to air; H2O, N2, O2 free. AP-42 1.4 (S-3) factors for small uncontrolled boilers
estimate NOx, CO, CH4, N2O, PM and VOC of H-601 (a proxy for direct-fired heaters; SO2 left out,
the fuel has no sulfur); PM and NMVOC have no CAS-identified flow yet and are gaps. Excluded with
reason: equipment leaks (no P&ID take-off; a material methane source in gas plants), non-routine
releases (blowdowns, flaring), tanks (none), effluent composition. Process overrides in
`lca/mappings.yaml`: only feed:STEAM, counted as heat delivered in kWh, uses the shared
`steam-heat` entry (the per-kg `steam` slug failed the strict Atlas build of PR #224); the other
candidates are listed there. `allocation.deviation` records why energy is used instead of the
WBCSD price ratio (no sourced prices). Location US (review R-05; the design and the named
backgrounds are US). Construction, transport and end of life are outside.

## D-015 Feed boundary values are design specifications, given with their basis (2026-10-28)
Decision: the flows and compositions of the three feeds (S1 raw gas, S8 make-up water, S33
combustion air) carry `provenance: given`, each source naming what is sourced and what is a
design specification. S1: the dry composition is sourced (S-1, Table 1, well 2), the water
content is calculated with the Bukacek correlation (S-9) plus 1 bbl/MMscf free water (ASSUMED,
D-004), the flow is the design-basis capacity (D-002, a specification chosen inside the range
of S-1). S8: the make-up rate is specified to keep the amine-loop water inventory constant
(D-007). S33: 15 % excess dry air of 21/79 O2/N2 (D-011, ASSUMED simplification).
Reason: review R-02. The library records design specifications as given with their source
(as asu-1 does for its design air); writing `assumed` hid the sourced composition and made
`cheme maturity` fail `sourced-boundary`. The ASSUMED parts stay named in each source.

## D-016 Cold-box refrigeration: order-of-magnitude check (2026-10-28)
Decision: no propane chiller is added to the balance at this stage; the possible
under-estimate of electricity is stated in `process.yaml` and section 5.
Check (review R-01; rounded values, ASSUMED, to verify with a qualified real-gas simulation):
the cold box must take the C2/C3 that leave as NGL from gas at 313 K to liquid at 283 K and
the residue gas back to a 5 K warm-end approach. Gas cooling 313-283 K of 529 kmol/h C2 and
255 kmol/h C3 (ideal-gas cp about 53 and 74 kJ/kmol K) is about 0.4 MW; condensation at
283 K (heat of vaporisation about 7.5 MJ/kmol for ethane, close to its 305 K critical point,
and about 16 MJ/kmol for propane; rounded saturation values) about 2.2 MW; the warm-end
approach of 4170 kmol/h residue gas about 0.2 MW: about 2.8 MW in total. Available: the
expander work, 1.79 MW (ideal gas, D-009), and the real-gas enthalpy departure of the gas
expanded from 5800 to 2200 kPa(a) (of order 0.4-0.7 MW for methane-rich gas near 313 K).
Deficit: about 0.3-0.6 MW at these values, up to about 2 MW with less favourable property
values. A propane chiller near 238 K (COP about 1.5, ASSUMED) would then need up to about
1.5 MW electric, i.e. up to +40 % of the 3.99 MW in the balance. Consistent with D-009's
open question; a rich gas at 90 % ethane recovery often has one.

## D-017 Fugitive methane: screening amount for the cut-off check (2026-10-28)
Decision: the equipment-leak exclusion keeps its reason (no P&ID component count) and the
`cutoff:` list of `lca/lca.yaml` records an ASSUMED screening amount: 0.1 % of the methane
processed, 64.9 kg/h, 519 t/a, the upper end of the 0.05-0.1 % the review suggested (R-03).
It is not added to the inventory. Bound: Alvarez et al. (2018, Science 361, 186-188) give the
whole US oil and gas supply chain as 13 +- 2 Tg/a of methane, 2.3 % of gross production, of
which processing is a minor segment; the segment value was not read here. At GWP100 29.8 the
screening amount is about 0.020 kg CO2-eq per kg sales gas (allocated), about twice the 0.0105
of the inventory: the direct GHG figure must not be read as complete. Replace by component
counts and the EPA leak protocol factors once P&IDs exist.

## 5. Results of this stage

Balances (`cheme process streams`, `cheme validate`: 0 errors, 0 warnings): all 6 blocks and 19
steps close within tolerance; plant in = out = 99 395.5 kg/h (raw gas 97 518.9, make-up water
60.9, combustion air 1 815.7). Products: sales gas 68 709.5 kg/h (83.7 MMscf/d; 96.7 % CH4,
1.4 % C2H6, 0.12 % C3H8, 1.8 % N2, 20 ppmv CO2; HHV about 1003 Btu/scf, inside 1035 +-5 %); NGL
27 258.5 kg/h (58.3 wt-% C2H6, 41.0 wt-% C3H8). Utilities: electricity 3986 kW (K-501 3672 kW),
LP steam 1078 kW, cooling water 6850 kW, fired heat 1027 kW (internal fuel 115 kg/h).

LCI (`cheme assess lca --inventory --write`, `--coverage`, `--balance`), per kg sales gas,
energy-allocated (72.2 %): raw gas 1.0245 kg, electricity 0.0419 kWh, LP steam 0.0113 kWh,
cooling water 0.0720 kWh, demineralised water 0.64 g, produced water 7.1 g, CO2 9.51 g (6.6 g
reservoir CO2 + 2.9 g combustion), CH4 0.032 g, C2H6 0.0087 g, C3H8 0.0056 g, NOx 2.3 mg, CO
1.9 mg; co-product NGL 0.397 kg. Mass balance of the LCI dataset closes (99 400.4 kg/h in and out
including 4.9 kg/h consumables; residual -0.015 kg/h) and so do C, H, N and O over the exchanges
with a composition; the element balance is reported "not assessable" only because the three
consumables have no composition in the dataset. Energy closure is 0 % (the products' enthalpy is
not counted; D-012). Classification: partial screening carbon footprint; direct (foreground)
GHG 0.0105 kg CO2-eq per kg sales gas (IPCC 2021 GWP100; 0.0145 unallocated), with 18 gaps.
Sensitivity of the largest gaps: each 0.1 kg CO2-eq/kWh of grid factor adds 0.0042 kg CO2-eq/kg
(power already outweighs the direct emissions at any grid factor above about 0.25 kg/kWh); each
0.1 kg CO2-eq/kWh of steam heat adds 0.0011; each 1 g CO2-eq per kg raw gas upstream adds 1.02 g.
Fugitive methane (excluded; screening amount 519 t/a, D-017) could add about 0.020 kg CO2-eq
per kg, roughly twice the direct GHG above, and must be estimated with the P&IDs. Electricity
is probably under-estimated: a propane chiller of up to about 1.5 MW electric (D-016) would
raise it by up to 40 %, i.e. up to 0.016 kWh more per kg sales gas (allocated).

`cheme check`: every concept and basic process gate passes (design-basis, concept-lists,
process-concept, process-balances, process-links, process-basic, assumptions-marked); the
concept gate layout-plot-plan fails (layout out of scope); P&ID, review, layout, datasheet
gates fail (out of scope). `cheme maturity`: see PROGRESS.md for the result after D-015
(feed boundary given); unit splits stay specified and partly unsourced, no simulation; the
manifest claims concept, the lowest level, and says so.

## 6. Methods, dependencies and gated steps

| step | status | gate |
|---|---|---|
| mass, component and element balances | done in cheme (validate, streams, propagate --check) | - |
| stream enthalpies, phases, energy closure | **gated**: no benchmarked package for C1-C3/CO2/N2/H2O (props --coverage), DWSIM PR claimed for N2/O2/Ar only | core#315 (qualify the actual mixture and range) |
| amine CO2 VLE / speciation | **gated** | core#364 (electrolyte support); a sourced MDEA model is a process input |
| TEG-water dehydration equilibrium | **gated** | core#315 (polar/activity benchmark) |
| mole sieve TSA | possible now in core (PR #398) with sourced natural-gas isotherms; none sourced | process input |
| predictive demethaniser / expander | after a qualified PR/GERG package; would replace the ASSUMED V-401 split, temperatures and duties | core#315 |
| C4+ characterisation | not needed for this feed (none reported); core#367 assay support covers naphtha only | - |

## 7. Open inputs and library items

Open inputs: full feed analysis (C4+, H2S, mercury, water, helium); receiving pipeline tariff
(specification and delivery pressure); NGL specification; site and grid; MDEA and TEG losses;
mole sieve sizing and isotherms; whether a propane chiller is needed; driver choice for K-501
(electric vs gas turbine); air vs water cooling.

Missing in the shared registry (for the consolidated PR; no edit made here): `natural-gas`
(raw/unprocessed and pipeline-quality grades), `natural-gas-liquids` (or `ethane`, `propane`),
`methyldiethanolamine`, `triethylene-glycol`, a zeolite molecular sieve, demineralised water,
an LP grade of `steam` (450 kPa(a)), produced water; no taxonomy family for natural gas
processing (`fuels` used). The Atlas mapping candidates are listed in `lca/mappings.yaml`.
