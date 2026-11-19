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
in this work (Google Patents machine text, the PubChem REST service). Property values queried
from the `chemicals` and `thermo` packages are single facts with their source (library ADR 0037):
SRC-5 names the package, the method or table and the underlying work of each value; those
works were not read here.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 2023/0416184 A1, Röhm GmbH (assignee on Google Patents: Roehm GmbH Darmstadt), priority 2020-10-23: Optimized process for synthesizing alkyl methacrylate by reducing unwanted byproducts, https://patents.google.com/patent/US20230416184A1/en | background: ACH from HCN and acetone in an exothermic reaction over a basic catalyst (an amine or an alkali hydroxide); the ACH-sulfo process as the process in view; the breakdown of ACH as the fundamental side reaction of the amidation: from the HCN it forms CO, which outgases, and the acetone formed is sulfonated (acetonedisulfonic acid); CO, acetone and sulfonated acetone among the by-products of amidation and conversion. Description: amidation in 98.0 to 100.0 wt% sulfuric acid at 70 to 130 C, molar H2SO4/ACH 1.6 to 3 in a first and 1.2 to 2.0 in a second loop reactor (ACH split about 75/25), conversion at 130 to 200 C for 2 to 30 min; the gas separator after the conversion releases an off-gas that is mainly CO from breakdown reactions, passed on to the esterification; esterification with methanol at 90 to 180 C, up to 7 bar(a), with the acid of the conversion as catalyst, MAA:alcohol 1:0.7 to 1:1.6, 10 to 30 wt% water, a cascade of tanks; at least two distillations, pure MMA of at least 99.9 wt%; the waste acid (essentially NH4HSO4, H2SO4 and water, 2 to 3 wt% TOC on average, the sulfonated acetone among it) goes to thermal regeneration in the gas phase above 900 C and the recovered acid back to the amidation, or alternatively to ammonium sulfate. Examples A1 to A3 (general procedure): 5000 kg/h ACH, about 95 C and 990 mbar(a) in the loop reactor, 155 C in the conversion, the gas separator at about 950 mbar(a), esterification at about 120 C and 50 to 150 mbar(g), 1700 kg/h water and 500 kg/h direct steam (16d); Table 1 (A2): 8100 kg/h H2SO4 (99.7 wt%), off-gas 50 m3/h and 65 m3/h in stream (9a), acetone in streams (8) + (9a) 26.5 kg/h, amide yield (methacrylamide + methacrylic acid) on ACH 94.7 % (93.0 % in A1 and A3), waste acid (11) 11 410 kg/h with 1.5 wt% TOC (2.3 and 2.4 in A1, A3); Table 2 (A2) stream 12: 0.8 wt% acetone; Table 4: MMA yield on ACH 91.6 % in A2 (90.1 to 91.6 % across A1 to A3, 91.1 % in B1); Example B1 stream 12: 87.9 wt% MMA and 5.3 wt% water | read (Google Patents); patent, facts only | D-001, D-004 to D-008, D-011 |
| SRC-2 | US 9,890,105 B2, Evonik Röhm GmbH, published 2018-02-13: Method for producing methylmethacrylate, https://patents.google.com/patent/US9890105B2/en | background: MMA mostly made from HCN and acetone via ACH, which gives large amounts of ammonium sulfate costly to treat; the C4 route (isobutylene or tert-butanol oxidised to methacrolein and methacrylic acid, then esterified) with gas-phase yields below 90 % (below 85 % reported for methacrolein from isobutylene); the ethylene route (ethylene and synthesis gas to propanal, with formaldehyde to methacrolein, then oxidation and esterification), operated by BASF at 40 000 t/a methacrylic acid and hard to use for large MMA volumes; the Asahi direct oxidative esterification of methacrolein, with high energy use at 1 to 2 bar(a) and 4 to 6 vol% product in the process gas | read (Google Patents); patent, facts only | D-001 |
| SRC-3 | Darabi Mahboub, Dubois, Cavani, Rostamizadeh, Patience (2018), Catalysis for the synthesis of methacrylic acid and methyl methacrylate, Chem. Soc. Rev. 47, 7703-7738, doi:10.1039/C8CS00117K | abstract as shown by search results: the ACH route is the dominant commercial process, its intermediates HCN and ACH are toxic; alternatives through isobutane, 2-methyl-1,3-propanediol and renewable feedstocks | abstract only (the full text was not reachable); route lead | D-001 |
| SRC-4 | processes/sulfuric-acid-1 (this library), DESIGN.md D-005 | double-contact plant, 99.7 % overall SO2 conversion (sourced ranges via core's sulfuric-acid skill there, ASSUMED within them); 98.5 wt% product acid | library, internal | D-003, D-008 |
| SRC-5 | The `chemicals` 1.5.2 package (core's environment), each value its default method: `ATCT_G` / `ATCT_L` (the Active Thermochemical Tables), `CRC` (the packaged CRC Handbook tables, `CRC_standard_data`), `YAWS` (the packaged table from Yaws' handbook, `Hfg_S0g_YAWS_data`), `WEBBOOK` (values of the NIST Chemistry WebBook packaged in `chemicals`); `iapws95_Psat` (the IAPWS-95 formulation for water); molar masses and boiling points (CRC tables); `cheme chemistry thermo --fit 298.15,1400` for the ideal-gas heat capacities (thermo 0.6.1, `TRCIG` from the TRC ideal-gas tables or `HEOS_FIT`, as materials.yaml names for each component) | formation enthalpies (kJ/mol): acetone (l) -248.4 CRC, (g) -216.07 ATCT_G; HCN (g) 129.29 ATCT_G; ACH (g) -133.0 YAWS (the package's only tabulated gas value, the other a Joback estimate; its liquid value, -120.9 CRC, lies above the gas value and is not used, D-004); methacrylamide (g) -157.7 and (s) -248.46 WEBBOOK; MMA (l) -385.6 and (g) -341.65 WEBBOOK; methanol (l) -238.4 ATCT_L, (g) -200.7 ATCT_G; H2SO4 (l) -814.0 CRC; NH4HSO4 (s) -1027.0 CRC; water (l) -285.825 ATCT_L, (g) -241.822 ATCT_G; SO2 (g) -296.8 CRC; SO3 (g) -395.7 CRC; CO (g) -110.525, CO2 (g) -393.474, CH4 (g) -74.534 ATCT_G; vapour pressure of water at 313.15 K 7.385 kPa (iapws95_Psat) | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying works (the CRC Handbook, Yaws' handbook, the Active Thermochemical Tables, the NIST Chemistry WebBook, the TRC tables, the IAPWS-95 release) were not read here | materials, D-004, D-008, D-009 |
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
unit's own losses are not modelled (open input 3); the yields of D-005 start at the ACH. The reactor is held at 303 K
(ASSUMED). Its cooling duty (Q1, 1.75 MW) comes from the gas-phase formation enthalpies of
SRC-5 (46.2 kJ/mol), ACH's being the YAWS value (Yaws' handbook as packaged, not read): the
package's liquid value of ACH (CRC) lies above that gas value, which is impossible, so it is
not used (L-1).

## D-005 Amidation and conversion R-201, gas separator V-201 (2026-11-19)

- Acid ratio: 1.4 mol H2SO4 per mol ACH at R-201 (spec `acid`), from SRC-1 Example A2
  (8100 kg/h H2SO4 for 5000 kg/h ACH), inside the 1.2 to 2.0 of the second reactor. The
  first/second reactor split and its higher first-stage ratio are lumped into one step.
- Acid strength: 98.5 wt% (the regenerated acid and the make-up), inside SRC-1's 98.0 to
  100.0 wt%; A2 used 99.7 wt%. The 1.5 wt% water also supplies the water of the loss path.
- Conditions: about 368 K in the loop reactor and 428 K in the conversion stage, the gas
  separator at 95 kPa(a) (SRC-1, Examples A1 to A3).
- Yield: AMID converts 94.7 % of the ACH to the amide, SRC-1 Example A2's amide yield
  (methacrylamide plus methacrylic acid on ACH, Table 1; the acid is lumped with the amide).
  ACH_DEC breaks down the other 5.3 %: SRC-1 names the breakdown of ACH as the amidation's
  fundamental side reaction, its HCN forming CO, which outgases (the gas separator's off-gas is
  mainly CO), and its acetone being sulfonated (acetonedisulfonic acid). The lumped
  stoichiometry ACH + H2O + H2SO4 -> acetone + CO + NH4HSO4 is ASSUMED (the sulfonation is not
  written: the sulfonated acetone is carried as acetone in the spent acid, D-006). Checks
  against Example A2: the CO is 70 Nm3/h per 5000 kg/h ACH against the 50 and 65 m3/h of
  off-gas reported (Table 1, reference state not stated); the free acetone is the source's
  (D-006); the spent acid's organic carbon is close to the source's TOC (D-006).
- The rest of the way to SRC-1 Example A2's 91.6 % MMA on ACH (Table 4), 91.6 / 94.7 = 96.7 %,
  is lost in the esterification and the work-up: 97.7 % of the amide esterified (D-006) and
  99 % purification recovery (D-007), 0.947 x 0.977 x 0.99 = 91.6 %. That split is ASSUMED.
- The amide is written as methacrylamide (MAM), an isomer of ACH, so the amidation consumes no
  acid in the model; the acid is consumed in the esterification (D-006). The total acid demand
  is the same.
- V-201 sends the CO to the SAR furnace (recovery: CO 1.0). SRC-1 passes the separator's
  off-gas on to the esterification; its final fate there was not read, so the direct route to
  F-501 is ASSUMED.

## D-006 Esterification R-301 and crude stripping V-301 (2026-11-19)

- Methanol: 1.2 mol per mol amide at R-301 (spec `methanol`), ASSUMED inside SRC-1's 0.7 to
  1.6; the excess is recycled (tear S11, D-007).
- Water: 0.44 kg per kg ACH (S12), SRC-1 Example A2's 1700 kg/h water plus 500 kg/h direct
  steam per 5000 kg/h ACH, all taken as water. Not in any duty, sized by the script only
  (ideal-gas steam, ASSUMED liquid heat capacities): the direct steam's heat, about 0.89 MW
  (1160 kg/h), and the heating of the water and fresh methanol feeds from 298 to 393 K at M-301,
  about 0.85 MW. The two overlap (the direct steam supplies part of that heating and of the
  stripping heat Q3), and the heat of diluting the amide liquor in the water, which is
  exothermic and works the other way, is not sized. Counted against E-501's steam, the direct
  steam would lower the export Q9 by up to about 0.9 MW (5 %), inside its stated upper bound.
- Reaction: methacrylamide + methanol + H2SO4 -> MMA + NH4HSO4 at 97.7 % of the amide
  (ASSUMED, D-005). The unconverted amide, which also stands for the methacrylic acid and
  hydroxyisobutyrate side products, stays in the spent acid and is burned in F-501.
- Conditions: about 393 K and 115 kPa(a) (SRC-1: about 120 C, 50 to 150 mbar(g)).
- V-301 strips all the MMA and methanol and 15 % of the water (ASSUMED): 0.062 kg water per kg
  MMA in the crude against 0.060 in SRC-1 Example B1 (stream 12). Of the breakdown's acetone it
  strips 14.7 % as free acetone, SRC-1 Example A2's 26.5 kg/h in streams (8) + (9a) per
  5000 kg/h ACH (Table 1) against the model's 5.3 % of the ACH broken down; the rest is
  sulfonated in the source and stays in the spent acid, carried as acetone (ASSUMED: the acid
  and water of the sulfonation and its heat not modelled). The crude S15 then holds 0.43 wt%
  acetone, against 0.8 wt% in Example A2 (Table 2, stream 12, which also carries the acetone
  of the recycles).
- The spent acid (S16) is 2.247 kg per kg ACH (H2SO4 22 wt%, NH4HSO4 59 wt%, water 17 wt%, the
  sulfonated acetone and the unconverted amide 2.3 wt%) against 2.282 in SRC-1 Example A2
  (11 410 kg/h per 5000 kg/h ACH): within 2 %, a check of the acid ratio and the water. Its
  organics carry 1.40 wt% carbon against the 1.5 wt% TOC of Example A2 (Table 1; 2 to 3 wt% on
  average in SRC-1's description).

## D-007 Purification C-401/C-402 (2026-11-19)

One lumped step with recoveries (ASSUMED): 99 % of the MMA to the product, 95 % of the methanol
recycled to the esterification, the rest (water, acetone, 5 % of the methanol and 1 % of the
MMA) to the SAR furnace as a purge. SRC-1 describes at least two distillations and a light
heteroazeotrope partly recycled and partly discharged, and the product at 99.9 wt% or more.
No column is designed (L-3).

## D-008 Sulfuric acid regeneration: furnace F-501, gas cleaning C-501, contact plant (2026-11-19)

- Furnace F-501: the spent acid, the purge and the CO are decomposed and burned with natural
  gas; H2SO4 to SO2, water and oxygen, NH4HSO4 to SO2, N2 and water (the ammonium nitrogen to
  N2; NOx not modelled), the organics (the purge's, and the sulfonated acetone and the
  unconverted amide of the spent acid) to CO2, water and N2, all complete. Outlet 1273 K
  (ASSUMED above SRC-1's 900 C) with 2 mol% O2 (wet, ASSUMED). The furnace is adiabatic with no
  air preheat (ASSUMED): scripts/mma_balance.py solves the natural gas (0.228 kg per kg MMA,
  39.5 MW on its lower heating value from SRC-5) and the combustion air from its energy and
  oxygen balances with the formation enthalpies of SRC-5 (NH4HSO4 and the amide at their solid
  values, the spent acid at 298 K). The fuel is an approximation, not a bound: a heat loss (not
  modelled) would raise it, while the spent acid enters at 393 K and its sensible heat, about
  1.0 MW at an ASSUMED 1.5 kJ/(kg K) (2.6 % of the fuel), is not credited, and the heats of
  solution of the acid and the salt are neglected. No open SAR fuel figure was read to compare.
- Gas cleaning C-501: quench, scrubbing, mist precipitation, cooling and drying lumped. The gas
  leaves the coolers at 313 K and 95 kPa(a) saturated with water (7.385 kPa, SRC-5), so it
  carries 200.9 kmol/h (3.62 t/h) of water into the drying tower. The drying acid takes it up
  and, through the common acid circuit of the drying tower and the absorbers (one 98.5 wt% acid
  header, as in sulfuric-acid-1, SRC-4), supplies 97.5 % of the absorbers' water: in the model
  the stream S33 from C-501 to A-502, so the process water S29 is only the rest, 92 kg/h. The
  other water condenses as weak acid water (S24, 15.8 t/h); its dissolved SO2 and acid are not
  modelled.
- The water balance limits the gas cooling: the water the drying acid takes up grows with the
  gas temperature at the drying tower, and above about 313.6 K the gas brings more water than
  the 98.5 wt% acid can hold. At the ASSUMED 313 K the margin is small, and humid converter air
  dried in the same acid would use it up (the air is taken dry, D-003). The cooler outlet
  temperature and the drying of the converter air are open inputs (open input 7).
- Converter air (S27) for O2/SO2 = 1.0 at the converter inlet (ASSUMED); the SO2 blower K-502
  moves the dry gas.
- Converter R-502: 99.7 % overall SO2 conversion, the value of sulfuric-acid-1 (SRC-4), not
  read for a spent-acid plant; absorbers A-502 take all SO3 with the water of the drying acid
  (S33) and process water (S29) to 98.5 wt% acid; V-502 separates the acid (tear S5) from the
  tail gas (S32).
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
| Q2 | R-201 cooling, 0.89 MW | gas-phase ACH -> methacrylamide (SRC-5), 24.7 kJ/mol; LOWER BOUND: the heat of protonation and solution in the acid is not included. The conversion stage's heating, 368 -> 428 K of about 30.6 t/h (about 0.77 MW at an ASSUMED 1.5 kJ/(kg K)), is not counted (L-1) |
| Q3 | V-301 steam, 2.39 MW | vaporisation of the crude S15 at the formation-enthalpy differences of SRC-5; the heat of esterification neglected; the direct steam and the feed heating sized in D-006, not counted |
| Q4, Q5 | C-401/C-402 steam 4.77 MW, cooling water 7.16 MW | reboil 2 x the crude's latent heat (ASSUMED); condensers the same plus the crude condenser |
| E-501 | waste heat boiler, 23.4 MW | furnace gas 1273 -> 623 K (ideal-gas heat capacities of materials.yaml); raises MP steam 1500 kPa(a) that supplies Q3 and Q4, the rest exported (Q9, 16.3 MW, an UPPER BOUND: no boiler or furnace loss, the direct steam of D-006 not counted) |
| Q7 | C-501 cooling water, 20.7 MW | gas 623 -> 313 K and the water condensed down to saturation at 313 K and 95 kPa(a) (S24, D-008) |
| Q8 | A-502 cooling water, 16.1 MW | heats of SO2 oxidation and SO3 absorption (SRC-5, 12.2 MW), the drying acid's uptake of the gas's water (S33, 2.5 MW) and K-502's compression heat (1.39 MW), all to cooling water; the tail gas leaves 30 K warmer than S26 and that heat is not credited. The converter's heat is taken as used for reheating the cleaned gas in the gas-gas exchangers, none raised as steam (conservative for the steam export) |
| Q10, Q11, Q12 | power 0.27 + 1.39 + 0.50 MW | K-501 101.3 -> 115 kPa(a), discharge about 40 C; K-502 95 -> 150 kPa(a) from 313 K, discharge about 95 C (368 K); isentropic efficiency 0.75; 500 kW lump for pumps, agitators and vacuum |

Utilities: cooling water 298/308 K, MP steam 1500 kPa(a) (ASSUMED). Core writes no duty for
R101, R201 and A502 (no heat of reaction declared, L-1); `cheme.process-duty` lists them as info.
`simulation.yaml` declares F501, R502 and R301 adiabatic (the boundary check of the LCA): no
utility crosses there. The declarations do not close on the stream temperatures, which core
cannot check (energy not evaluable, L-1): the gas-gas exchangers of the contact plant, about
10.0 MW that the converter gas gives to the cleaned gas (S26 at 313 K to S28 at 693 K, the
first bed inlet), are lumped between the steps K502 and R502 and drawn as no step of their own.

## D-010 Recycles and design specifications (2026-11-19)

Two tears (core ADR 0060): the regenerated acid S5 and the recovered methanol S11, Wegstein,
tolerance 1e-6 kg/h abs, 1e-8 rel. Three specifications (core ADR 0070) solved with them:
`rate` varies the acetone S1 for 12 500 kg/h MMA with the HCN, the water feeds, the natural gas
and both air streams as followers at the script's ratios; `acid` varies the make-up S4 for
1.4 mol H2SO4 per mol ACH; `methanol` varies the fresh methanol S10 for 1.2 mol per mol amide.
Converged: acetone 7916.8 kg/h, make-up 57.0 kg/h, methanol 4087.1 kg/h, the same as the
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
- Carbon monoxide: the gas separator V-201 releases the CO of the ACH breakdown (SRC-1: its
  off-gas is mainly CO), 202 kg/h at 428 K and 95 kPa(a) in S8 to F-501; toxic and flammable.
  Gas detection at V-201 and along the line, a leak-tight line, and a furnace trip that
  isolates S8 and sends it to a safe disposal.
- SO2/SO3 and hot concentrated acid in the SAR plant; natural gas firing of F-501.
- Flammable acetone, methanol and MMA.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml`: per kg MMA, every foreground exchange from the flowsheet, allocation shares
1/0 between the MMA and the exported steam (as sodium-cyanide-1: exergy allocation needs the
chemical exergy of MMA, not sourced yet; all burdens on the MMA, conservative). The Atlas
build links acetone-1, methanol-1 and sulfuric-acid-1 (`lca/mappings.yaml`, `dataset:`),
natural gas by mass and demineralised water through the shared entries, power and cooling
water by their default mappings. The weak acid condensate links by its slug to the library's
utility-wwtp (biological treatment), which does not count its neutralisation: an
understatement, to be replaced by a neutralisation background. Gaps: liquid HCN (no producer,
D-003), and the biosphere identities of seven tail-gas components whose flow is zero in this
design (acetone, ACH, NH4HSO4, H2SO4, HCN, methacrylamide, MMA). The tail gas CO2 (0.80 kg per kg MMA, fossil: natural gas and the burned
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
| R201 | conversion 0.947 / 0.053 on ACH | SRC-1 amide yield (D-005) | sourced, lumped stoichiometry assumed |
| R301 | conversion 0.977 of the amide | the rest of SRC-1's 91.6 % with C401, ASSUMED split (D-005, D-006) | assumed |
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
  significant figures, so a stream's sum can fall short of 1 by about 1e-6 and pyDEXPI then
  warns (`pydexpi_composition_fractions`; S13 did in the first build, no stream does in the
  current one); the calculated values in flowsheet.yaml sum to 1.

## Open inputs

1. A sourced heat of amidation and esterification in the acid (calorimetry), before basic
   engineering (D-009, D-011).
2. An open energy balance or fuel figure for a spent-acid regeneration furnace, its heat loss
   and air preheat (D-008).
3. The ACH synthesis yield, temperature and catalyst from an open source (D-004).
4. A library producer of HCN (D-003).
5. The SO2, NOx and acid mist emission levels against the applicable limits (D-008, D-012).
6. Exergy allocation of the steam export (D-012).
7. The gas cooling temperature at C-501 and the drying of the converter air against the SAR
   plant's water balance (D-008).
