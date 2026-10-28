# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/kraft_balance.py`; the stream table is
generated: `cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#180. "Per ADt" = per air-dry tonne of pulp (90 % dry solids).
BREF 2015 = JRC Best Available Techniques Reference Document for the Production of Pulp,
Paper and Board (Suhr et al. 2015, EUR 27235 EN, doi 10.2791/370629), chapter 3 (kraft).

Run record of this stage (2026-10-28): library branch `case/kraft-pulp-1` from `bb3178a`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0, CoolProp (in cheme's interpreter) for
the steam properties; DWSIM and Cantera not used. Core dependency issues named in #180
(core #364 electrolytes, #365 solids, #370 furnace energy) were not re-audited in that run.

Core audit (revision after review 2026-10-28-pfd-lci-review#2, 2026-10-28): core main at
`7bed468` (ChemE-as-Code/core, 2026-10-28T14:52Z); the issues live in the archived
repository ChemE-as-Code/core-archive and are all closed:
- **#364** (closed 2026-10-27, core PR #394): electrolyte thermodynamics for aqueous
  **NaCl-H2O only** (Pitzer, 273-373 K, up to 6 mol/kg); any other salt, acid or base, and
  any compound of an alkali metal in a phase or DWSIM route, is refused. White, green and
  black liquor (NaOH, Na2S, Na2CO3, Na2SO4, sodium organics at up to 80 % solids) remain
  outside it: D-007 stands.
- **#365** (closed 2026-10-27, core #395): `phase: solid` components, a slurry basis and a
  one-solute crystallizer or solid separation. It adds a mass basis, not thermodynamics for
  lime mud, dregs or smelt; the lumped kraft steps are already balanced by specified splits,
  so nothing changes here.
- **#370** (closed 2026-10-27, core #387): `cheme process furnace` for CaCO3 calcination in a
  lime kiln. It applies to K901/K902 and was run (D-009; needs the `cantera` extra, run from
  core `7bed468` in a temporary environment because the installed cheme 0.8.0 lacks it). The
  recovery boiler (organic combustion with smelt reduction) is outside it.

## 1. Route and boundary memo

- **Route**: kraft (sulfate) chemical pulping of softwood with full chemical recovery, the
  route of #180: continuous digester, brown stock washing and screening, two-stage oxygen
  delignification, ECF bleaching D0-EOP-D1 (outline, lumped), pulp drying machine, 7-effect
  evaporation with concentrator, recovery boiler, smelt dissolving, green liquor
  clarification, slaking and causticizing, white liquor and lime mud filtration, rotary lime
  kiln, extraction back-pressure turbine generator with condensing tail.
- **Boundary** (gate-to-gate): from screened softwood chips, purchased chemicals, natural gas,
  process water and air at the battery limit to baled market pulp at the drying machine.
  Outside: forestry, debarking and chipping (wood room) and the bark boiler; ClO2 generation;
  air separation; raw water treatment; effluent treatment (the bleach plant effluent leaves as
  a waste to the mill's biological plant); landfill; tall oil and turpentine recovery (D-001).
- **What crosses the boundary**: CHIPS, NAOH, O2, CLO2, H2O2, H2SO4, SALT, CAO, NG, AIR, FW
  (inputs); PULP (product); EEXP (net electricity export, co-product); WW (effluent to
  treatment); SW (dregs, grits, mud purge); STACK and VENT (to atmosphere); CW (heat rejected).
- **Feeds from other library processes** (boundary feeds, link noted for the LCI): oxygen
  (asu-1), NaOH (chlor-alkali-1), H2O2 (hydrogen-peroxide-1), H2SO4 (sulfuric-acid-1); ClO2
  would be made on site from sodium chlorate with methanol (methanol-1) or H2O2 as reductant.
- **Comparisons**: only with bleached softwood kraft market pulp of the same boundary (no
  wood room, no bark boiler, no effluent treatment, no by-product recovery).

## 2. Decisions

## D-001 Route, grade and boundary (2026-10-28)
Decision: bleached softwood kraft market pulp (Nordic spruce/pine type), boundary as in
section 1. Extractives are lumped with the black liquor and burnt; tall oil soap skimming,
turpentine recovery and NCG handling are not modelled.
Reason: #180 asks for a defined grade with an explicit chemical and energy recovery boundary;
market pulp gives an air-dry product basis without a paper machine (skill
tech-heavy-chem-kraft-pulping: a pulp dryer is not a paper machine).
Rejected: hardwood/eucalyptus (less lignin and black liquor, Tran and Vakkilainen); integrated
paper mill; tall oil and turpentine as co-products (would add allocation for ~1-2 % of the
mass; listed as an open item). Other pulping routes (review #9; general knowledge, not
re-sourced in this run):
- sulfite (acid or bisulfite): weaker pulp, and the Mg or Na base recovery is a different
  chemical cycle; a small share of world chemical pulp, mostly dissolving or speciality grades.
- soda or soda-AQ: sulfur-free, but slower delignification and weaker pulp on softwood; used
  for non-wood fibres and some hardwoods.
- mechanical, TMP or CTMP: about 90 % yield, but electricity-driven, lower strength and
  brightness stability; it has no chemical recovery cycle, which #180 asks for.
Kraft is the dominant chemical pulping route and the one #180 names, so it was chosen.
Assumptions: chips arrive debarked and screened; no wood room or bark boiler in the boundary.

## D-002 Capacity, product and hours (2026-10-28)
Decision: 1000 ADt/d (41,667 kg/h at 90 % dry, 37,500 kg/h fibre), 8400 h/a, generic site.
Reason: a normalisation basis for a per-kg inventory, not a mill claim (#180). Tran and
Vakkilainen use a 1000 t/d mill as their example. ASSUMED.

## D-003 Wood and its representation (2026-10-28)
Decision: dry wood 41 % cellulose, 28 % hemicellulose, 27 % lignin, 3.5 % extractives, 0.5 %
ash; chips at 50 % moisture. Lumped model components (process/materials.yaml): cellulose and
hemicellulose as C6H10O5, lignin as the coniferyl alcohol unit C10H12O3, extractives as
abietic acid C20H30O2, ash as SiO2.
Reason: typical softwood ranges; the lumped formulas make every element balance checkable.
ASSUMED: no species assay was read in this run (the USDA FPL note found, Tech. Note 235, is a
scanned 1952 text that could not be read; Pettersen 1984 not accessed).
Limitation (#180 asks to qualify it): this is a **bookkeeping representation, not a molecular
identity**. Lignin's methoxyl groups, the xylan share of softwood hemicellulose, K, Cl and
non-process elements are not represented. Check against BREF 2015 Table 3.12 (elemental
analysis of two Finnish softwood black liquors): our strong-liquor dry solids are C 38.0 %,
H 4.5 %, Na 20.1 %, S 4.5 % against C 31-32 %, H 3.1-3.3 %, Na 20.6-20.8 %, S 6.1-6.3 %. Sodium
fits; carbon and hydrogen are high (the lumped organics are too carbon rich, the real liquor
holds more oxygenated acids and K/Cl salts), sulfur is low (sulfidity 35 % and no organic
sulfur). The black liquor heating value is not predicted from it (D-011).

## D-004 Yields (2026-10-28)
Decision: kg retained per 100 kg dry wood - after cooking cellulose 37.6, hemicellulose 7.4,
lignin 2.0 (47.0 %, kappa ~28); after O2 delignification 37.6 / 7.0 / 1.0 (45.6 %, kappa
~15, 50 % delignification); bleached 37.2 / 6.8 / 0 (44.0 %). Wood use 2045 kg dry/ADt.
Reason: inside the usual softwood ranges (kappa as about 0.15 x lignin %, bleached yield
44-46 %; BREF 2015 sec. 3.2.2.1 gives 3-6 m3 wood per tonne of chemical pulp). ASSUMED.
Model: **specified yields (imposed conversion model)**; no kinetics are used or invented. The
dissolved material becomes sodium lignate, isosaccharinate (carbohydrate peeling) and resin
soap, each consuming one NaOH (process/reactions.yaml).

## D-005 White liquor and recovery cycle specification (2026-10-28)
Decision: effective alkali 19 % as NaOH on wood; sulfidity 35 %; causticity 81 %; reduction
92 %; active alkali 125 g/L as NaOH (mass fraction 0.1068). The cycle is closed in the
script by iterating the make-ups and the lime charge until the white liquor produced equals
the demand (residual Na and S below 1e-9 kmol/h).
Reason: Tran and Vakkilainen (2007): reduction efficiency typically above 90 %, causticizing
efficiency typically 80-83 %, Na2S passes the causticizers unchanged, strong liquor fired at
65 % or more, chemical recovery about 97 %. EA and sulfidity ASSUMED typical for softwood.
Result: 4411 kg white liquor/ADt to the digester (4685 incl. the O2 stage); 1689 kg black
liquor dry solids/ADt (Tran and Vakkilainen: ~1.5 t BLDS per t pulp for their mill example;
softwood is at the high end).

## D-006 Washing, O2 stage and sodium/sulfur make-up (2026-10-28)
Decision: wash presses discharge at 25 % consistency; 3 % of the dissolved solids are carried
out of brown stock washing, 6 % out of the post-O2 washer to bleaching (the washing loss).
O2 stage: 22 kg O2 and 22 kg NaOH-equivalent per ADt (BREF 2015 sec. 3.2.2.2: 20-25 kg each
for softwood), the alkali being the NaOH make-up first and white liquor (whose sulfide is
oxidised to sulfate, SULF_OX) for the rest. The O2-stage filtrate goes counter-currently to
brown stock washing. Make-ups equal the losses: Na2SO4 3.28 kg/ADt for sulfur, NaOH 2.94
kg/ADt (100 %) for the remaining sodium.
Reason: counter-current washing and make-up logic of the kraft cycle (tech skill; BREF 2015
sec. 3.2.2.2: S and Na in and out must balance). Carry-over fractions ASSUMED. The condensate
does not cover all wash water: 1.29 t/ADt hot process water is added at the post-O2 washer.
Sodium losses 3.9 kg Na/ADt (washing loss, dregs, mud purge, boiler dust).

## D-007 Evaporation and property methods (2026-10-28)
Decision: weak black liquor 15 % solids to 80 % (Tran and Vakkilainen: modern
high-solids concentrators 80-85 %; BREF 2015 sec. 3.2.2.6: 70-85 %); 9.15 t water/ADt
evaporated, steam economy 6.0 (ASSUMED, seven effects); the condensate is reused in
causticizing (dissolving tank 3.6 t, mud washing 0.6 t/ADt) and post-O2 washing (4.9 t/ADt).
No property package covers wood, black liquor, smelt or lime slurries: `property_method`
stays a placeholder and no stream enthalpy is calculated (no electrolyte route beyond aqueous
NaCl, core #364; no nonconventional solids). Foul condensate stripping (methanol, TRS) is not
modelled.

## D-008 Bleaching outline (2026-10-28)
Decision: ECF D0-EOP-D1 lumped in one step: 10 kg ClO2 (= 15.8 kg NaClO3 at the generator;
BREF Table 3.3: 15-50 kg NaClO3/ADt), 18 kg NaOH, 3 kg H2O2 (BREF: 2-30), 4 kg O2, 4 kg
H2SO4 per ADt; ClO2 water at 10 g/kg; effluent 18 m3/ADt (BREF 2015 sec. 3.3.8: a modern ECF
bleach plant with counter-current washing about 15-20 m3/ADt). The residual lignin is
oxidised (BL_CLO2, BL_H2O2; the EOP oxygen counted through BL_H2O2 and PER_DEC), the ClO2 not
used on lignin oxidises carbohydrate (CARB_OX, part of the 1.6 % bleaching yield loss), the
rest of the loss is peeled; the acid is neutralised. Chemical charges ASSUMED inside the BREF
ranges. Total NaOH 20.9 kg/ADt is below the BREF bleached-pulp range (25-50) because part of
the O2-stage alkali is white liquor. Not modelled: AOX, chlorate, chelating agents,
MgSO4, brightness.

## D-009 Recausticizing and lime kiln (2026-10-28)
Decision: dregs = wood ash + equal mass of green liquor (20.4 kg/ADt wet); grits 5 kg
CaCO3/ADt; lime mud purge 10 kg dry/ADt (BREF Table 3.17: 10-20 kg/ADt each for dregs/grits
and lime purge); white liquor filter cake 65 % solids; mud washed with 1.5 kg condensate/kg
and fed at 80 % solids; calcination 0.95; Ca make-up as purchased burnt lime 8.4 kg CaO/ADt
(BREF Table 3.3: 5-10 kg CaO/ADt). Kiln fuel 1.5 GJ/ADt natural gas (BREF 2015 sec.
3.2.2.6.2: 1.5-1.8 GJ/t pulp), LHV 50 MJ/kg as methane, air ratio 1.10. ASSUMED within the
ranges. The burner is its own step (K902) and only passes heat to the calcination (K901): see
D-012.
Furnace check (review #2; `process/furnaces.yaml`, `cheme process furnace` at core `7bed468`,
NASA Glenn thermochemistry): with the flowsheet's mud feed (S42), degree of calcination 0.95,
lime 523 K, off-gas 473 K, air ratio 1.10 and 15 % losses (ASSUMED), the solved fuel is
15.4 MW against the flowsheet's 17.4 MW (1.5 GJ/ADt). Calcination takes 8.1 MW and mud
moisture evaporation 2.9 MW. The 1.5 GJ/ADt closes the balance if about 24 % of the fuel is
lost, which is plausible for a long rotary mud kiln. The sourced 1.5 GJ/ADt is kept. Core flags
5.5 GJ/t lime at 15 % losses (6.2 GJ/t at 1.5 GJ/ADt) against its lime-BREF range of
6-9.2 GJ/t for long rotary kilns. That range is for limestone kilns, not mud reburning, so it
is only a reference here.

## D-010 Recovery boiler and emissions (2026-10-28)
Decision: organics burnt completely, residual alkali carbonated, sulfate reduced to the 0.92
reduction; air ratio 1.15; SO2 0.1 kg S/ADt, NOx 1.2 kg NO2/ADt, dust 0.3 kg/ADt (as Na2SO4)
after the ESP, all inside BREF 2015 Table 3.13 (SO2 <0.002-0.65 kg S/ADt, NOx 0.73-2.0,
particulates 0.02-1.6 kg/ADt); kiln NOx 0.4 kg/ADt ASSUMED (AP-42 sec. 10.2 gives about
0.5-1.0 kg/ADt from kiln and furnace for 1990 practice). Check: recovery boiler dry flue gas
about 7000 Nm3/ADt against 6000-9000 in BREF 2015 sec. 3.2.2.6. Not estimated, declared in
lca.yaml `emission_exclusions`: TRS, CO, VOC and NCG, kiln SO2 and dust, the dissolving tank
vent, the evaporator foul condensates.

## D-011 Steam, power and cooling (2026-10-28)
Decision: HP steam 3.5 kg per kg BLDS (Tran and Vakkilainen: about 3.5, range 2.5-3.8) at
8400 kPa(a), 753 K (their example unit: 84 bar, 480 C); 246 t/h, 16.6 GJ/ADt above
feedwater at 398 K (BREF 2015 sec. 3.2.2.6: process steam 13-18 GJ/ADt). Extraction
back-pressure turbine (MP 1300, LP 450 kPa(a)) with condensing tail at 10 kPa(a), isentropic
efficiency 0.80, generator 0.97, enthalpies IAPWS-IF97 (CoolProp). Process heat by consumer
(GJ/ADt, ASSUMED split): digester 1.8, O2 stage 0.5, bleaching 1.2, recovery boiler
auxiliaries 1.0 (MP); evaporation 3.2 (economy 6), dryer 3.06 (3.4 MJ per kg water
evaporated), deaeration and miscellaneous 0.8 (LP): 11.6 GJ/ADt in total (BREF 2015 sec.
3.2.2.3: 10-14 GJ/ADt; Table 3.5: 11.0 GJ/t for a modern market pulp mill; drying about 25 %).
Power use 650 kWh/ADt (ASSUMED split; BREF 600-800 kWh/ADt including the wood room and
effluent treatment, which are outside here). Generation 913 kWh/ADt (38.0 MW; 27.7 MW
back-pressure, 10.3 MW condensing; Tran and Vakkilainen: 25-35 MW for a 1000 t/d mill),
net export 263 kWh/ADt (BREF Table 3.5: modern market mills export). Cooling water 4.56
GJ/ADt (evaporator surface condenser, turbine condenser). Recovery boiler steam is the only
steam source: no bark or power boiler (D-001). Energy closure is not evaluable in core (no
stream enthalpies, D-007); the turbine balance closes in the script (losses 1.2 MW).
Steam basis (review #5): the 3.5 kg/kg applies to the **model** BLDS mass of the flowsheet
(1689 kg/ADt, lumped organics, D-003), not to a real-composition BLDS. A liquor with the
BREF Table 3.12 analysis carrying the same wood carbon would weigh about 2.0 t/ADt, and
3.5 kg/kg of that would give about 19 % more steam. The steam figure is therefore checked by
energy, not by mass: 1689 kg x 13-15 MJ/kg (Tran and Vakkilainen HHV range) = 22-25 GJ/ADt
fired, so 16.6 GJ/ADt of steam is about 66-75 % boiler efficiency on HHV, which is usual for
recovery boilers. It is also inside the BREF 13-18 GJ/ADt process-steam range.

## D-012 Biogenic and fossil carbon (2026-10-28)
Decision: CO2 with carbon from the wood is the component CO2B (biogenic), CO2 from natural gas
the component CO2 (fossil). Lime mud carbonate carbon is biogenic: it is the CO2 captured as
Na2CO3 in the smelt from black liquor combustion. No limestone enters (Ca make-up is
purchased CaO, whose calcination CO2 lies in its background). The kiln burner (K902) and the
calcination (K901) are separate steps so that core's carbon tracing does not mix fossil and
biogenic carbon in one reactive step. lca.yaml declares the chips' carbon biogenic.
Reason: #180 asks to keep biogenic and fossil CO2 apart in the LCI. The carbon of the
calcination CO2 is traced through the flowsheet to the wood: the smelt Na2CO3 is formed from
black liquor combustion CO2, and causticizing moves that carbon into CaCO3. **The
classification of recycled lime mud calcination CO2 as biogenic is a convention, ASSUMED
here** (review #3). Pulp and paper GHG guidance of the NCASI/WRI type is understood to treat
it this way, but no such document was read in this run and none is cited. Fossil-case
sensitivity: counted fossil, the calcination CO2 adds 0.172 kg CO2-eq per kg pulp, so the
fossil total would be 0.254 instead of 0.082 kg/kg. Cite the guidance (document, edition,
section) before publication.
Result per kg pulp: fossil CO2 0.0823 kg (kiln gas only), biogenic CO2 2.30 kg (recovery
boiler 2.13, kiln calcination 0.172, dissolved in the bleach effluent 0.0066 kg).
Characterisation (review #1): `carbon_accounting.trace_emissions: false` in lca.yaml. Each CO2
flow keeps the origin declared on its elementary flow (CO2 fossil, CO2B biogenic), and
results.md now shows 0.0823 kg CO2-eq/kg fossil. With tracing on, cheme 0.8.0 split every
CO2 emission by the plant-wide fossil share of the carbon pool (2.1 %) and reported
0.050 kg/kg. The warning `cheme.lca-carbon-origin` that comes with this setting is expected:
it compares the declared origin with that pool share. One known core limitation remains. The
product's carbon content is still split by the pool share, so results.md shows a "fossil
carbon content of the product" of 0.0084 kg C, and a biogenic withdrawal and a "PCF including
biogenic" that are about 2 % off. Physically, the pulp's 0.400 kg C is 100 % wood carbon. A
core finding to raise; lca/README.md carries the caveat.

## D-013 Stream conditions (2026-10-28)
Decision: temperatures and pressures are nominal ASSUMED values for the stream table only;
they enter no calculation.

## D-014 LCA scope and allocation (2026-10-28)
Decision: functional unit 1 kg air-dry pulp at the gate; boundary declared cradle-to-gate
with every background declared missing (the gate-to-gate foreground is the deliverable; as
soda-ash-1 D-010). The net electricity export is a co-product: allocation by substitution
(the displaced grid electricity, missing until the site country is chosen), dataset system
model substitution. Local mapping overrides in lca/mappings.yaml only (H2SO4, landfill;
process water kept out of the deionised-water entry).
Rejected: mass or economic allocation (no price; electricity has no mass); exergy (no sourced
exergy of the pulp in this run).
Energy closure in `cheme assess lca --coverage` (review #7): the reported 20.7 % does not
measure this plant's energy balance, so the check does not apply at this stage. cheme counts
only delivered energy carriers and declared product energy contents. Here that is 52.8 MW of
heat rejected to cooling water on one side and 10.9 MW of electricity exported on the other.
The two dominant energy carriers are not counted: the wood (about 2 t dry/ADt) and the pulp
have no `properties.energy`, and the black liquor heating value is not predicted (D-003,
D-011). The material streams also carry no enthalpy (D-007). The 20.7 % is therefore the
ratio of two unrelated terms, not a residual. The plant's energy is checked instead in the
script (turbine balance), against BREF ranges (D-011) and by the kiln furnace balance (D-009).
Basis of chemicals (review #8): feed:CLO2 is per kg of 10 g/kg solution and feed:H2SO4 per kg
of 93 wt% acid. lca.yaml and mappings.yaml state the conversion a background linked on a
100 % basis needs.

## 3. Reaction and model evidence

| step | model basis | evidence | status |
|---|---|---|---|
| R101 digester | imposed yields, 4 lumped reactions | yields ASSUMED in usual softwood ranges; EA/sulfidity ASSUMED | specified, not predictive |
| R301 O2 stage | imposed delignification 50 %, peeling, sulfide oxidation | BREF 3.2.2.2 O2 and alkali charges | specified |
| R401 bleaching | imposed lignin removal, charges | BREF Table 3.3 ranges | specified |
| B701 recovery boiler | complete combustion, reduction 0.92 | Tran and Vakkilainen (>90 %); BREF Table 3.13 emissions | specified (sourced range) |
| R802 causticizing | causticity 0.81 | Tran and Vakkilainen (80-83 %) | specified (sourced range) |
| K901/K902 kiln | calcination 0.95, fuel 1.5 GJ/ADt | BREF 3.2.2.6.2 | specified (sourced range) |
| washers, filters, evaporators | carry-over fractions, solids contents | ASSUMED | specified |

No kinetics, equilibrium or vendor data were used or invented. Heats of reaction are given
only for the inorganic reactions. CALC is checked (review #6): 178.32 kJ/mol at 298.15 K
from the NASA Glenn data in Cantera, computed by `cheme process furnace`. The recalled
CaCO3 value of -1207.6 kJ/mol did not reproduce the old +178.3 (it gives +179.0), and it is
replaced. The other heats of reaction are still recalled NBS values (ASSUMED). They enter no
balance, since no stream enthalpies are calculated (D-007).

## 4. Source register

| source | locator | read status | reuse | used for |
|---|---|---|---|---|
| JRC pulp and paper BREF 2015, doi 10.2791/370629 | sec. 3.2.2.1-3.2.2.3; Tables 3.3, 3.4, 3.5, 3.12, 3.13, 3.17; sec. 3.2.2.6, 3.2.2.6.2, 3.3.7, 3.3.8 | text of chapter 3 extracted and the cited passages read | EU reuse policy; facts cited, nothing copied | chemical charges, heat/power, kiln fuel, emissions, wastes, water, BL composition check |
| Tran and Vakkilainen (2007), ICEP 3, eucalyptus.com.br/icep03/200Tran.text.pdf.pdf | sections "Recovery of pulping chemicals", "Recovery of heat", large boiler example | read | facts cited | reduction, causticity, BL HHV 13-15 MJ/kg, steam/solids, power, 84 bar 480 C, solids 80-85 % |
| US EPA AP-42 sec. 10.2 (1990/1995) | process description; NOx statement | read | US public domain; cited | NOx order of magnitude only (old practice) |
| Ullmann's, Pulp, doi 10.1002/14356007.a18_545.pub4 | - | not accessed | - | reference lead (#180) |
| NBS tables (Wagman et al. 1982) | - | recalled values | facts | inorganic heats of reaction other than CALC (ASSUMED until checked) |
| NASA Glenn thermodynamic data (McBride, Gordon and Reno 1993, NASA TM-4513) via Cantera 3.2.0 in core `7bed468` | species CaCO3(calcite), CaO(s), CO2, CH4, H2O, air | computed by `cheme process furnace` | facts | CALC heat of reaction, lime kiln energy balance (D-009) |
| core-archive issues #364, #365, #370 (ChemE-as-Code) | closing comments, 2026-10-27 | read | - | core capability audit (header) |

## 5. Open inputs, gated steps and registry entries

Missing in shared files (for the consolidated PR; not edited here):
- `chemicals/chemicals.yaml`: softwood chips (wood, dry/wet basis, biogenic carbon), bleached
  kraft pulp (air-dry), sodium hydroxide (50 % solution), chlorine dioxide (water), hydrogen
  peroxide (50 %), sodium sulfate (saltcake), calcium oxide (quicklime), natural gas,
  pulp mill effluent.
- `taxonomy/families.yaml`: a pulp-and-paper family (ISIC 1701, NACE 17.11); process.yaml uses
  bio-based-chemicals meanwhile.
- `lci/mappings.yaml`: entries for softwood chips, NaOH 50 %, oxygen, ClO2 water, H2O2 50 %,
  sodium sulfate, quicklime, process (non-deionised) water, pulp effluent treatment.

Gated or open steps:
- **Energy closure**: no property package covers wood, black liquor, smelt or lime slurries
  (core #364 closed with NaCl-H2O only; nonconventional components). Duties are specific
  consumptions. The LCI "energy closure" of 20.7 % does not apply (D-014).
- **Black liquor representation**: lumped components (D-003); a qualified nonconventional
  representation (elemental analysis, HHV) is a core/method question of #180.
- **Furnace energy**: the lime kiln was run with `cheme process furnace` (D-009). The installed
  cheme 0.8.0 has no Cantera, so it was run from core `7bed468` in a temporary environment;
  `cheme validate` does not evaluate the furnace. The recovery boiler is out of the
  furnace's scope (solid-reaction furnace only).
- **Climate result**: fixed in the case (review #1, D-012). `trace_emissions: false` keeps
  the declared origin per CO2 flow, and results.csv shows 0.0823 kg CO2-eq/kg fossil. Still
  open in core (to raise there): with tracing on, CO2 emissions are split by the pool share,
  and the product's carbon content is always split by the pool share (results.md "fossil
  carbon content of the product" 0.0084 kg C, which should be 0).
- Wood composition and species assay; tall oil/turpentine recovery; NCG system and TRS; AOX
  and chlorate; foul condensate stripping; ClO2 generator; wood room and bark boiler.
- Elementary flow identities (pre-release issue 175): CO2B, Na2SO4 dust, H2O/N2/O2.
