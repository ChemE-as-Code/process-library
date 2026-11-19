# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Methyl methacrylate (MMA) by the acetone cyanohydrin (ACH-sulfo) route with on-site sulfuric
acid regeneration, issue ChemE-as-Code/process-library#477, a Tier 2 continuous entry of the
library. Concept stage: design basis, balanced BFD/PFD with two recycles and three design
specifications, an independent balance script for what core cannot calculate, an equipment
list and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA,
datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 + #254).
Templates: `sodium-cyanide-1` (continuous, a balance script for the duties, steam export as an
upper bound) and `oxalyl-chloride-1` (recycle tears, the structure of this file). Requires
cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, the PubChem REST service, the open data tables
packaged in the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 2023/0416184 A1, Röhm GmbH (Evonik): Optimized process for synthesizing alkyl methacrylate by reducing unwanted byproducts, https://patents.google.com/patent/US20230416184A1/en | background: ACH from HCN and acetone in an exothermic reaction over a basic catalyst (an amine or an alkali hydroxide); the ACH-sulfo process as the process in view. Description: amidation in 98.0 to 100.0 wt% sulfuric acid at 70 to 130 C, molar H2SO4/ACH 1.6 to 3 in a first and 1.2 to 2.0 in a second loop reactor (ACH split about 75/25), conversion at 130 to 200 C for 2 to 30 min; esterification with methanol at 90 to 180 C, up to 7 bar(a), with the acid of the conversion as catalyst, MAA:alcohol 1:0.7 to 1:1.6, 10 to 30 wt% water, a cascade of tanks; at least two distillations, pure MMA of at least 99.9 wt%; the waste acid (essentially NH4HSO4, H2SO4 and water, 2 to 3 wt% TOC) goes to thermal regeneration in the gas phase above 900 C and the recovered acid back to the amidation, or alternatively to ammonium sulfate. Examples A1 to A3 (general procedure): 5000 kg/h ACH, about 95 C and 990 mbar(a) in the loop reactor, 155 C in the conversion, the gas separator at about 950 mbar(a), esterification at about 120 C and 50 to 150 mbar(g), 1700 kg/h water and 500 kg/h direct steam; Table 1: 8100 kg/h H2SO4 (99.7 wt% in A2), waste acid 11 410 kg/h in A2; Table 4: MMA yield on ACH 91.6 % in A2 (90.1 to 91.6 % across A1 to A3, 91.1 % in B1); Example B1 stream 12: 87.9 wt% MMA and 5.3 wt% water | read (Google Patents); patent, facts only | D-001, D-004 to D-008 |
| SRC-2 | US 9,890,105 B2, Evonik Röhm GmbH, published 2018-02-13: Method for producing methylmethacrylate, https://patents.google.com/patent/US9890105B2/en | background: MMA mostly made from HCN and acetone via ACH, which gives large amounts of ammonium sulfate costly to treat; the C4 route (isobutylene or tert-butanol oxidised to methacrolein and methacrylic acid, then esterified) with gas-phase yields below 90 % (below 85 % reported for methacrolein from isobutylene); the ethylene route (ethylene and synthesis gas to propanal, with formaldehyde to methacrolein, then oxidation and esterification), operated by BASF at 40 000 t/a methacrylic acid and hard to use for large MMA volumes; the Asahi direct oxidative esterification of methacrolein, with high energy use at 1 to 2 bar(a) and 4 to 6 vol% product in the process gas | read (Google Patents); patent, facts only | D-001 |
| SRC-3 | Darabi Mahboub, Dubois, Cavani, Rostamizadeh, Patience (2018), Catalysis for the synthesis of methacrylic acid and methyl methacrylate, Chem. Soc. Rev. 47, 7703-7738, doi:10.1039/C8CS00117K | abstract as shown by search results: the ACH route is the dominant commercial process, its intermediates HCN and ACH are toxic; alternatives through isobutane, 2-methyl-1,3-propanediol and renewable feedstocks | abstract only (the full text was not reachable); route lead | D-001 |
| SRC-4 | processes/sulfuric-acid-1 (this library), DESIGN.md D-005 | double-contact plant, 99.7 % overall SO2 conversion (sourced ranges via core's sulfuric-acid skill there, ASSUMED within them); 98.5 wt% product acid | library, internal | D-003, D-008 |
| SRC-5 | The `chemicals` 1.5.2 package (core's environment): CRC and ATcT formation enthalpies, molar masses, boiling points; `cheme chemistry thermo --fit 298.15,1400` for the ideal-gas heat capacities (thermo TRCIG / HEOS fits) | formation enthalpies (kJ/mol): acetone (l) -248.4, (g) -216.07; HCN (g) 129.29; ACH (g) -133.0 (its liquid value, -120.9, lies above the gas value and is not used); methacrylamide (g) -157.7; MMA (l) -385.6, (g) -341.65; methanol (l) -238.4, (g) -200.7; H2SO4 (l) -814.0; NH4HSO4 (s) -1027.0; water (l) -285.825, (g) -241.822; SO2 (g) -296.8; SO3 (g) -395.7; CO (g) -110.525; CO2 (g) -393.474; CH4 (g) -74.534 | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037) | materials, D-008, D-009 |
| SRC-6 | PubChem CIDs 6658 (methyl methacrylate), 768 (hydrogen cyanide) | formula, InChIKey, ChEBI cross-references | read (PUG REST) | registry |
| SRC-7 | Ullmann's Encyclopedia of Industrial Chemistry, Methacrylic Acid and Derivatives; Hydrogen Cyanide | - | not read (licensed); route and SAR lead only | - |

Searched and not found openly (2026-11-19): a measured heat of the amidation of ACH in
sulfuric acid or of the esterification in the acid, an open energy balance or fuel figure for
a spent-acid regeneration plant, the ACH synthesis yield and conditions in an open patent
example, and the full text of SRC-3.

## D-001 Route and boundary (2026-11-19)

Decision: the ACH-sulfo route with sulfuric acid regeneration (SAR) on site. Acetone and HCN to
ACH; amidation and conversion in sulfuric acid; esterification with methanol; distillation;
the spent acid and the organic purges decomposed in a furnace and the SO2 turned back into
sulfuric acid in a contact plant, recycled to the amidation.

Reason: the open sources read call it the main commercial route (SRC-2: MMA "mostly" made via
ACH; SRC-3 abstract: the dominant process), and SRC-1 gives one consistent, open set of acid
ratio, conditions and yield for it. Its feeds are library products: acetone (acetone-1),
methanol (methanol-1) and the sulfuric acid make-up (sulfuric-acid-1).

Rejected:
- C4 routes (isobutylene or tert-butanol over methacrolein and methacrylic acid, or the direct
  oxidative esterification of methacrolein): SRC-2 reports gas-phase yields below 90 % and
  high energy use; no open example with a full set of ratios and yields was read, and the
  library's isobutene-1 / tert-butanol-1 would be the feeds. A candidate for a second entry.
- Ethylene routes (propanal and formaldehyde to methacrolein, SRC-2; the methyl propionate
  and formaldehyde route, known as Alpha, not read here): SRC-2 states the propanal route runs
  at one site and is hard to scale; no open source with balances was read for either.
- ACH-sulfo with ammonium sulfate instead of SAR (SRC-1 names it as the alternative): it turns
  the acid into a large ammonium sulfate co-product (SRC-2) that needs ammonia and an
  evaporative crystalliser, and the scope of issue #477 asked for the regeneration.

Boundary: from the feeds at the battery limit to pure MMA in storage, MP steam to the site
header, the tail gas to the stack and the weak acid water to treatment. Not included: HCN
production (D-003), the stabiliser of MMA and of HCN, the catalyst of the ACH unit, tank
farms, flare, the wastewater treatment.

## D-002 Capacity, product and operating hours (2026-11-19)

12.5 t/h pure MMA, 8000 h/a, 100 kt/a: ASSUMED, a single train of the order of SRC-1
Example B1 (11.39 t/h). Product: MMA only in the model; SRC-1 gives at least 99.9 wt% MMA from
the last column with methacrylonitrile and acetone in the ppm range, which the model does not
carry (L-2).

## D-003 Feeds (2026-11-19)

Acetone, methanol and HCN are taken pure, HCN as liquid at 283 K (ASSUMED); the make-up acid is
the 98.5 wt% product of sulfuric-acid-1 (SRC-4); natural gas is methane (ASSUMED); air is dry,
21 mol% O2 with argon lumped into nitrogen; process water is demineralised (ASSUMED).

HCN: no library entry exports it. sodium-cyanide-1 makes HCN by the Andrussow process but
neutralises all of it on site; acrylonitrile (issue #460, not merged) gives HCN as a
co-product. The feed stays a gap in the LCI (D-012) until one of them exports it.

## D-004 ACH synthesis R-101 (2026-11-19)

A conversion reactor, HCN the key at conversion 1.0 and acetone equimolar (the rate spec
follower is rounded down by 1e-6 so HCN is never in excess), ASSUMED: SRC-1 says only that the
reaction is exothermic over a basic catalyst; no open yield or temperature was read. The ACH
unit's losses are carried by the lumped loss of R-201 (D-005). The reactor is held at 303 K
(ASSUMED). Its cooling duty (Q1, 1.75 MW) comes from the gas-phase formation enthalpies of
SRC-5 (46.2 kJ/mol): the liquid value of ACH in the package lies above its gas value, which is
impossible, so it is not used (L-1).

## D-005 Amidation and conversion R-201, gas separator V-201 (2026-11-19)

- Acid ratio: 1.4 mol H2SO4 per mol ACH at R-201 (spec `acid`), from SRC-1 Example A2
  (8100 kg/h H2SO4 for 5000 kg/h ACH), inside the 1.2 to 2.0 of the second reactor. The
  first/second reactor split and its higher first-stage ratio are lumped into one step.
- Acid strength: 98.5 wt% (the regenerated acid and the make-up), inside SRC-1's 98.0 to
  100.0 wt%; A2 used 99.7 wt%. The 1.5 wt% water also supplies the water of the loss path.
- Conditions: about 368 K in the loop reactor and 428 K in the conversion stage, the gas
  separator at 95 kPa(a) (SRC-1, Examples A1 to A3).
- Yield: AMID converts 92.5 % of the ACH to methacrylamide, ACH_DEC the remaining 7.5 % to
  acetone, CO and ammonium hydrogen sulfate (ACH + H2O + H2SO4 -> acetone + CO + NH4HSO4).
  With the complete esterification (D-006) and 99 % purification recovery (D-007) this gives
  0.925 x 0.99 = 91.6 % MMA on ACH, SRC-1 Example A2's yield. The split of the losses between
  the sections and the loss chemistry are ASSUMED: SRC-1 names acetone among the amidation's
  by-products and sulfonated acetone derivatives in the waste acid; CO as the fate of the
  HCN released is not read.
- The amide is written as methacrylamide (MAM), an isomer of ACH, so the amidation consumes no
  acid in the model; the acid is consumed in the esterification (D-006). The total acid demand
  is the same.
- V-201 sends the CO to the SAR furnace (recovery: CO 1.0).

## D-006 Esterification R-301 and crude stripping V-301 (2026-11-19)

- Methanol: 1.2 mol per mol amide at R-301 (spec `methanol`), ASSUMED inside SRC-1's 0.7 to
  1.6; the excess is recycled (tear S11, D-007).
- Water: 0.44 kg per kg ACH (S12), SRC-1 Example A2's 1700 kg/h water plus 500 kg/h direct
  steam per 5000 kg/h ACH, all taken as water; the direct steam's heat is not counted
  separately.
- Reaction: methacrylamide + methanol + H2SO4 -> MMA + NH4HSO4, complete (ASSUMED); the
  methacrylic acid and hydroxyisobutyrate side paths are in the lumped loss.
- Conditions: about 393 K and 115 kPa(a) (SRC-1: about 120 C, 50 to 150 mbar(g)).
- V-301 strips all the MMA, methanol and acetone and 15 % of the water (ASSUMED): 0.062 kg water
  per kg MMA in the crude against 0.060 in SRC-1 Example B1 (stream 12).
- The spent acid (S16) is 2.195 kg per kg ACH (H2SO4 21 wt%, NH4HSO4 62 wt%, water 17 wt%)
  against 2.282 in SRC-1 Example A2 (11 410 kg/h per 5000 kg/h ACH): within 4 %, a check of
  the acid ratio and the water. Its organics (SRC-1: 2 to 3 wt% TOC) are not modelled.

## D-007 Purification C-401/C-402 (2026-11-19)

One lumped step with recoveries (ASSUMED): 99 % of the MMA to the product, 95 % of the methanol
recycled to the esterification, the rest (water, acetone, 5 % of the methanol and 1 % of the
MMA) to the SAR furnace as a purge. SRC-1 describes at least two distillations and a light
heteroazeotrope partly recycled and partly discharged, and the product at 99.9 wt% or more.
No column is designed (L-3).

## D-008 Sulfuric acid regeneration: furnace F-501, gas cleaning C-501, contact plant (2026-11-19)

- Furnace F-501: the spent acid, the purge and the CO are decomposed and burned with natural
  gas; H2SO4 to SO2, water and oxygen, NH4HSO4 to SO2, N2 and water (the ammonium nitrogen to
  N2; NOx not modelled), the organics to CO2 and water, all complete. Outlet 1273 K (ASSUMED
  above SRC-1's 900 C) with 2 mol% O2 (wet, ASSUMED). The furnace is adiabatic with no air
  preheat (ASSUMED): scripts/mma_balance.py solves the natural gas (0.228 kg per kg MMA) and the
  combustion air from its energy and oxygen balances with the formation enthalpies of SRC-5
  (NH4HSO4 at its crystalline value, the spent acid at 298 K). Without heat loss and with the
  hot spent acid not credited, the fuel is a lower bound for the loss and an upper bound for
  the missing preheat; no open SAR fuel figure was read to compare.
- Gas cleaning C-501: quench, scrubbing, mist precipitation, cooling and drying lumped; all the
  water leaves as weak acid condensate (S24), the dissolved SO2 and acid are not modelled.
- Converter air (S27) for O2/SO2 = 1.0 at the converter inlet (ASSUMED); the SO2 blower K-502
  moves the dry gas.
- Converter R-502: 99.7 % overall SO2 conversion, the value of sulfuric-acid-1 (SRC-4), not
  read for a spent-acid plant; absorbers A-502 take all SO3 with process water (S29) to
  98.5 wt% acid; V-502 separates the acid (tear S5) from the tail gas (S32).
- The make-up (S4, spec `acid`) replaces the 0.3 % of the sulfur lost as SO2: 57 kg/h acid,
  4.6 g per kg MMA. The tail gas carries 2.9 g SO2 per kg MMA; whether that meets an
  emission limit is not checked (open input).
- Two blocks (SARF, SARC): the furnace reaction H2SO4 -> SO2 + H2O + 1/2 O2 is the contact
  plant's two reactions reversed, so a block holding all three has no unique extents; the
  split is also the plant's (hot end, cold end).

## D-009 Utilities and duties (2026-11-19)

All duties and powers come from scripts/mma_balance.py and are ASSUMED (D-008 for the
furnace):

| stream | what | basis |
|---|---|---|
| Q1 | R-101 cooling, 1.75 MW | gas-phase heat of ACH formation (SRC-5), 46.2 kJ/mol |
| Q2 | R-201 cooling, 0.87 MW | gas-phase ACH -> methacrylamide (SRC-5), 24.7 kJ/mol; LOWER BOUND: the heat of protonation and solution in the acid is not included, and the conversion stage's heating is not counted (L-1) |
| Q3 | V-301 steam, 2.43 MW | vaporisation of the crude S15 at the formation-enthalpy differences of SRC-5; the heat of esterification neglected |
| Q4, Q5 | C-401/C-402 steam 4.85 MW, cooling water 7.28 MW | reboil 2 x the crude's latent heat (ASSUMED); condensers the same plus the crude condenser |
| E-501 | waste heat boiler, 23.5 MW | furnace gas 1273 -> 623 K (ideal-gas heat capacities of materials.yaml); raises MP steam 1500 kPa(a) that supplies Q3 and Q4, the rest exported (Q9, 16.2 MW, an UPPER BOUND: no boiler or furnace loss) |
| Q7 | C-501 cooling water, 23.2 MW | gas 623 -> 313 K and all water condensed |
| Q8 | A-502 cooling water, 12.2 MW | heats of SO2 oxidation and SO3 absorption (SRC-5), all to cooling water; the converter's heat is taken as used for reheating the cleaned gas, none raised as steam (conservative for the steam export) |
| Q10, Q11, Q12 | power 0.27 + 1.39 + 0.50 MW | K-501 101.3 -> 115 kPa(a), K-502 95 -> 150 kPa(a) at 313 K, isentropic efficiency 0.75; 500 kW lump for pumps, agitators and vacuum |

Utilities: cooling water 298/308 K, MP steam 1500 kPa(a) (ASSUMED). Core writes no duty for
R101, R201 and A502 (no heat of reaction declared, L-1); `cheme.process-duty` lists them as info.
`simulation.yaml` declares F501, R502 and R301 adiabatic (the boundary check of the LCA).

## D-010 Recycles and design specifications (2026-11-19)

Two tears (core ADR 0060): the regenerated acid S5 and the recovered methanol S11, Wegstein,
tolerance 1e-6 kg/h abs, 1e-8 rel. Three specifications (core ADR 0070) solved with them:
`rate` varies the acetone S1 for 12 500 kg/h MMA with the HCN, the water feeds, the natural gas
and both air streams as followers at the script's ratios; `acid` varies the make-up S4 for
1.4 mol H2SO4 per mol ACH; `methanol` varies the fresh methanol S10 for 1.2 mol per mol amide.
Converged: acetone 7918.7 kg/h, make-up 57.0 kg/h, methanol 4081.4 kg/h, the same as the
script's closed-form balance.

## D-011 Hazards (2026-11-19)

Continuous plant, no batch or semi-batch step, so no recipe and no reactor-hazard screening
(`cheme process reactor-hazards` applies to batch and semi-batch steps). The design-relevant
hazards named for the next stage:
- HCN and ACH: acutely toxic; ACH decomposes back to acetone and HCN in base and on heating
  (SRC-3 abstract and SRC-1 call both intermediates toxic). Keep the liquid HCN and ACH
  inventories small, ACH stabilised with acid, detection and a scrubber on the vents.
- The amidation is exothermic and runs in near-100 % sulfuric acid; the ACH feed is dosed
  into the circulating acid (SRC-1: loop reactor with a high circulation ratio), so a loss of
  cooling or of circulation with the ACH still fed is the runaway case. Its heat is not
  sourced (Q2 is a lower bound): a calorimetric value is an open input before basic
  engineering.
- MMA polymerises exothermically; stabiliser and oxygen management in the columns and the
  storage are not designed.
- SO2/SO3 and hot concentrated acid in the SAR plant; natural gas firing of F-501.
- Flammable acetone, methanol and MMA.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml`: per kg MMA, every foreground exchange from the flowsheet, allocation shares
1/0 between the MMA and the exported steam (as sodium-cyanide-1: exergy allocation needs the
chemical exergy of MMA, not sourced yet; all burdens on the MMA, conservative). The Atlas
build links acetone-1, methanol-1 and sulfuric-acid-1 (`lca/mappings.yaml`, `dataset:`),
natural gas by mass and demineralised water through the shared entries, power and cooling
water by their default mappings. Gaps: liquid HCN (no producer, D-003) and the weak acid
condensate (no curated background for its treatment; the average municipal treatment would
not represent it). The tail gas CO2 (0.80 kg per kg MMA, fossil: natural gas and the burned
organics) and SO2 are elementary flows. Not estimated (emission exclusions): fugitive leaks,
furnace NOx and acid mist, process vents, storage.

Benchmarks (`benchmarks/oxygenates.yaml`): the MMA yield on acetone and the natural gas per kg
MMA, both `no_open_reference`: the only open yield figures are this dataset's own source
(SRC-1), which a check would pass by construction, and no open SAR fuel figure was found.

## D-013 Gates (2026-11-19)

The concept gates of the process (design basis, lists, materials and flowsheet, balances,
links, assumptions marked) pass; `layout-plot-plan` (concept) fails because no plot plan is
drawn, out of scope for this entry as for the other Tier 2 entries (e.g. ethylene-1,
acetic-acid-1). The concept stage is not signed off.

## Method and dependency table

| step | method | inputs | basis |
|---|---|---|---|
| R101 | conversion, HCN complete | ASSUMED (D-004) | assumed |
| R201 | conversion 0.925 / 0.075 on ACH | SRC-1 yield, ASSUMED split (D-005) | sourced yield, assumed split |
| R301 | conversion, amide complete | ASSUMED (D-006) | assumed |
| V201, V301, C401, C501, V502 | component recoveries | D-005 to D-008 | assumed, V301 checked against SRC-1 |
| F501 | conversion, all complete; fuel from an energy balance | SRC-5 enthalpies, script | assumed, standard thermochemistry |
| R502, A502 | conversion 0.997, 1.0 | SRC-4 | library value |
| specs, tears | core ADR 0070, 0060 | SRC-1 ratios | converged |
| duties | scripts/mma_balance.py | SRC-5 | assumed |

## Core features used (core 1.12.0)

Conversion reactors with several reactions on one key, component separators (`recovery:`),
recycle tears with Wegstein, design specifications with followers, BFD/PFD generation,
`cheme assess lca --write` with the boundary check.

## Core limits hit (each a candidate core issue)

- L-1: no property package for concentrated sulfuric acid with ammonium hydrogen sulfate,
  methacrylamide and organics, so core cannot write the duties of R101, R201, R301, V301 or
  the columns, nor check the furnace's energy balance (its inlets are liquids without
  ideal-gas data). The duties come from the script, on formation enthalpies only.
- L-2: the product's impurities (methacrylonitrile, acetone, methyl isobutyrate) cannot be
  followed without a by-product model; the model's product is pure MMA.
- L-3: no column model with sourced vapour-liquid equilibria for MMA/methanol/water/acetone
  (a heteroazeotropic system), so the purification is a recovery separator.
- L-4: `cheme process build` writes the mole fractions of the PFD's stream table to six
  significant figures, so S13's sum is 0.9999989 and pyDEXPI warns
  (`pydexpi_composition_fractions`); the calculated values in flowsheet.yaml sum to 1.

## Open inputs

1. A sourced heat of amidation and esterification in the acid (calorimetry), before basic
   engineering (D-009, D-011).
2. An open energy balance or fuel figure for a spent-acid regeneration furnace, its heat loss
   and air preheat (D-008).
3. The ACH synthesis yield, temperature and catalyst from an open source (D-004).
4. A library producer of HCN (D-003).
5. The SO2, NOx and acid mist emission levels against the applicable limits (D-008, D-012).
6. Exergy allocation of the steam export (D-012).
