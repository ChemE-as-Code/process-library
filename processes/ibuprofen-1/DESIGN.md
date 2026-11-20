# Design decisions: ibuprofen-1

Ibuprofen by the BHC three-step catalytic route, a batch plant at the concept stage (issue
[#508](https://github.com/ChemE-as-Code/process-library/issues/508)). Every value the files
carry is given with its source, or marked ASSUMED; the numbers live in the YAML files, this file
keeps the decisions and the reasons.

## Source register

| id | source | what it gives | read |
|---|---|---|---|
| SRC-1 | Elango et al. (Hoechst Celanese), US 4 981 995 A (1991), Method for producing ibuprofen, <https://patents.google.com/patent/US4981995A/en> | Example 1 (acylation: 254 g IBB, 385 g Ac2O, 1877 g HF, 80 C, 3 h, 85 % conversion, 81 % selectivity to IBAP; HF vented through a caustic scrubber); Example 2 (Pd/C hydrogenation in methanol, 30 C, 100 psig, 99.5 %, 96.6 %); Example 3A (Raney nickel, neat IBAP, 70 C, about 3 h, >99 % conversion, 98 % IBPE, 1.5 % IBPET); Examples 49, 50, 100 (carbonylation at 125 to 130 C and 2000 to 3100 psig CO; Example 49 at 2000 psig 96.6 % ibuprofen, Example 50 at 3100 psig 99.1 %; Example 100 without solvent, 8.43 mol IBPE with 775 mL of 26 % HCl, H3O+/H2O 0.173, H+/IBPE 0.75, PdCl2 and PPh3 at Pd:P:IBPE 1:12:15050, 2 h 35 min, 99 % conversion, 96.6 % ibuprofen, 1.0 % 3-IPPA, 0.0 % IBS, 0.8 % heavy ends); Example 106 (81 % of the Pd complex recovered, 16 % as metal); comparative example G (400 psig: 20 % ibuprofen); CO pressure range 500 to 5000 psig; background: the Boots process (GB 971,700, US 3,385,886) starts with the acylation of the arene with acetyl chloride over aluminium chloride, followed by "various series of subsequent reactions" | opened 2026-11-19, the examples named; the background, Examples 3A, 49, 50 and 100 re-read 2026-11-20 |
| SRC-2 | Hoechst Celanese, US 5 151 551 A (1992), Method for purification of ibuprofen comprising mixtures, <https://patents.google.com/patent/US5151551A/en> | Example 1 (700 g crude, about 90 %, in hexane, water washes at 60 C to pH >= 2.9, 30 wt% solution cooled at 0.3 C/min to 25 C, held 1 h, to 5 C, filtered at 10 C, washed with 5 C hexane, recrystallised at 40 wt%, dried at 50 C and 49 mm Hg: assay 99.7 %, Pd 2.6 ppm, TPP + TPPO 3.0 ppm); Example 2 (washes in heptane at 70 C, the solvent flashed, a 50 mm x 1.2 m packed column, lights to 130 C, the cut at 130 to 134 C and 0.3 to 0.7 mm Hg, assay 88.6 to 97.4 %, crystallisation from 25 wt% heptane: 99.8 %); no yields, no solubility data | opened 2026-11-19 |
| SRC-3 | US EPA (1997), Presidential Green Chemistry Challenge, Greener Synthetic Pathways Award (BHC Company), <https://19january2021snapshot.epa.gov/greenchemistry/presidential-green-chemistry-challenge-1997-greener-synthetic-pathways-award_.html> | Bishop, TX, 7.7 million lb/a, commercial since 1992; three catalytic steps instead of six stoichiometric; about 80 % atom utilisation (about 99 % with the recovered acetic acid); HF recovered and recycled at more than 99.9 % | opened 2026-11-19 |
| SRC-4 | thermo 0.6.1 and chemicals 1.5.2 (C. Bell and contributors, MIT), package values (library ADR 0037) | liquid molar volumes, heat capacities, vaporisation, fusion and formation enthalpies, normal boiling points, the vapour pressures of HF and of the C-401 lights, CO's compressibility (Peng-Robinson), identifiers; the method of each named where it is used (process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml). Underlying works, none read here: the CRC Handbook of Chemistry and Physics (chemicals' CRC, CRC_ORG, CRC_INORG tables: Hfl of isobutylbenzene, acetic anhydride, acetophenone and ethylbenzene; Tb of isobutylbenzene, acetic anhydride, acetic acid and HF); the Active Thermochemical Tables (ATCT_L, ATCT_G: Hfl of acetic acid and water, Hfg of CO); Perry's Chemical Engineers' Handbook, 8th ed., drawing on DIPPR 801 (DIPPR_PERRY_8E); the VDI Heat Atlas (VDI_TABULAR); Zabransky et al.'s heat capacity compilation (ZABRANSKY_*); CoolProp's equations of state (HEOS, HEOS_FIT); IAPWS (water's vapour pressure); HF's vapour pressure from thermo's own correlation 'Fit 2023'. Estimates, not data: JOBACK (Hfg of IBAP, 1-phenylethanol and 2-phenylpropionic acid, ibuprofen's Hfus), MORGAN_KOBAYASHI, DADGOSTAR_SHAW, MMSNM0, AMBROSE_WALTON | open-source package queried; single values, facts only; run 2026-11-19 and 2026-11-20 |

Not used: no open kinetics of the HF acylation, no open solubility of ibuprofen in hexane, no
open heat of reaction of any of the three steps was found in the time of this study.

## Decisions

**D-001 Route.** The BHC route of SRC-1: acylation of isobutylbenzene in anhydrous HF,
hydrogenation of the ketone, Pd-catalysed carbonylation of the alcohol. It is the industrial
route SRC-3 describes (three catalytic steps, acetic acid the only by-product, HF recycled),
and SRC-1 gives conditions and results for every step. Rejected:
- the Boots route (SRC-1's background: an acylation with acetyl chloride over aluminium
  chloride, then further reactions SRC-1 does not list): SRC-3 says the BHC process replaces a
  technology of six stoichiometric steps with less than 40 % atom utilisation and large volumes
  of aqueous salt wastes; no open source with its step data was read;
- Pd/C hydrogenation in methanol (SRC-1 Example 2): needs a solvent to remove again and gives
  96.6 % selectivity against Raney nickel's 98 % neat (Example 3A);
- carbonylation in a solvent (methyl ethyl ketone, Examples 49, 50, 106): Example 100 runs
  without one at 99 % conversion and 96.6 % to ibuprofen, the selectivity of Example 49 (2000
  psig; Example 50 at 3100 psig gives 99.1 %), so no solvent loop is needed;
- the heat treatment of SRC-2 Example 3 and the double crystallisation of Example 1: Example 2's
  sequence (washes, vacuum distillation, one crystallisation) removes the phosphines by
  distillation and needs one crystallisation (L-4).

**D-002 Capacity and hours.** 3500 t/a of dried ibuprofen, the order of SRC-3's Bishop plant
(7.7 Mlb/a, about 3490 t/a), 7920 h/a; ASSUMED. Whether Bishop runs batch or continuously is not
stated in the sources; this concept runs the examples' batch steps on one dedicated train
(library ADR 0035).

**D-003 Batch recipe.** process/recipe.yaml: eight unit procedures, one batch of 3977 kg every
9.0 h, 880 batches a year; the HF stripping/acid cuts and the washes/vacuum distillation are the
bottlenecks (9.0 h each, ASSUMED durations), the acylation takes its dosing and post-reaction
from R101's model (6.3 h in all), the hydrogenation and carbonylation their reaction times from
SRC-1 (3 h, 2 h 35 min), the crystallisation SRC-2's cooling rate. The recipe sizes R-101 at
80 m3 (47 m3 of batch) and D-401 at 16 m3. The flowsheet holds the recipe's year averages
(no cheme.recipe-basis finding).

**D-004 Feeds and ratios.** Set by eight design specifications of the flowsheet (core ADR 0070):
the capacity (IBB feed), 2 mol of acetic anhydride and 49.5 mol of HF per mol of IBB in the
batch (SRC-1 Example 1), hydrogen 5 % above its use (ASSUMED, vented), CO its use plus what
R-301's head space holds at the end of the reaction (ASSUMED 1.8 m3 of gas over 6.2 m3 of liquor
in an 8 m3 autoclave at 16.65 MPa and 403 K: 8.5 kmol a batch, 0.385 mol per mol of IBPE,
vented on let-down; the dissolved CO not counted, no recovery of the let-down gas), 0.75 mol
of HCl per mol of IBPE (SRC-1 Example 100) with a 33 wt% hydrochloric acid make-up (the spec
fixes the HCl, not the water: the charge is 31 wt% HCl with 3.3 mol of water per mol of IBPE,
a stronger acid than Example 100's 26 % with about 4.3 mol, from its 775 mL on 8.43 mol;
the example's conversion and selectivities are applied unchanged, ASSUMED), 3 kg of
wash water per kg of crude (SRC-2: about 1.5 kg per wash, two washes), 25 wt% ibuprofen in the
crystalliser feed (SRC-2 Example 2). Acetic anhydride 99.5 wt% (acetic-anhydride-1).

**D-005 Reactions, kinetics and heats.** process/reactions.yaml. The acylation's 19 % not
reported as IBAP is lumped as isomers (ISO, ASSUMED); the hydrogenation's 0.5 % not accounted
for is put on the over-reduction, the carbonylation's 1.6 % on the heavy ends (the ether of two
IBPE, ASSUMED). Only the acylation has rate laws (second order, ASSUMED, calibrated so that a
batch of Example 1 reaches 85 % in 3 h at 353 K, Ea 60 kJ/mol ASSUMED): R101 is a semi-batch
with the anhydride dosed over 1.5 h at 353 K instead of the example's all-in charge, so that the
dosing can be stopped; the reaction is slow against the dosing (up to 0.86 of the dosed
reactant accumulated, 2.3 h of post-reaction), so the heat release follows the kinetics, not
the feed rate: the exotherm is not dose-controlled (D-011). The hydrogenation and carbonylation are conversion steps
(L-2). Heats from formation enthalpies (SRC-4) and analogues (acetophenone, 1-phenylethanol,
2-phenylpropionic acid): acylation -19.9, hydrogenation -60.3, over-reduction -155.6,
carbonylation -125.6 kJ/mol, the ether 0 (ASSUMED).

**D-006 Components.** Molecular pseudo-components on an inventory basis (process/materials.yaml):
the ketone-HF complex, the Pd complex, the phosphine and the Raney nickel are not resolved; the
catalysts are consumables (D-010). H2, CO and HCl carry their ideal-gas heat capacities for the
conversion steps' duties.

**D-007 Separations of the reaction sections.** Component separators with ASSUMED recoveries:
C-101 strips 99.9 % of the HF (SRC-3), the 0.1 % to a caustic scrubber; C-102 (two columns,
lumped) cuts acetic acid (99 %, with 2 % of the anhydride), recycles 99 % of the IBB and 97.5 %
of the anhydride, sends 90 % of the by-product lump to the residue and 98 % of the IBAP on;
V-201 vents the hydrogen; V-301 vents the CO and decants 97 % of the acid phase, nine tenths
recycled; the melt washes (V-401) take 99.5 % of the HCl to the wastewater. The acetic
anhydride C-102 passes on (2.2 kg/h) is carried as inert through R-301's hot aqueous HCl and the
washes into C-401's lights; it would in fact hydrolyse there to about 2.6 kg/h of acetic acid
(stoichiometry), shared between the acid recycle, the wastewater and the lights: not modelled,
ASSUMED.

**D-008 Purification.** SRC-2 Example 2's sequence with Example 1's hexane: washes on the melt at
353 K (SRC-2 washes in the hydrocarbon solution; on the melt here, so no solvent is flashed
before the column, ASSUMED); the washed melt keeps 2 % of the water (5.7 wt%, 32 kg/h in S27),
which cannot condense on cooling water at 40 to 93 Pa, so the packed vacuum column C-401 takes
its lights in two stages (ASSUMED): first the water, the HCl, the IBB and the anhydride at about
15 kPa, where water boils at 327 K and condenses on cooling water (as SRC-2 flashes its solvent
and water at about 200 mm Hg before its column), then the rest of the lights at full vacuum; the cut at 403 to
407 K and 40 to 93 Pa and a residue with 3 % of the ibuprofen and 98 % of the heavy ends
(ASSUMED splits); the cut is dissolved in hexane to 25 wt% at 333 K and cooled to 278 K with an
ASSUMED 80 % yield (L-4), filtered (99.5 % of the crystals, 0.3 kg of liquor per kg, ASSUMED) and
dried at 323 K to 0.1 wt% hexane. C-402 recovers 99.5 % of the hexane; seven tenths of its
residue go back to the dissolver, three tenths to incineration. Product 99.56 wt% ibuprofen,
0.22 wt% 3-IPPA (model); 67.0 % of the IBB becomes product.

**D-009 Energy.** MP steam 1100 kPa(a), cooling water 298/308 K, brine 263/268 K (ASSUMED).
cheme writes the duties of R101 (the reaction to cooling water, the heat-up to steam), R201, R301
(net of the charge's heat-up) and CR401; the dryer's from core's dryer model (cheme process
crystallizers); the columns' reboilers and condensers are hand arithmetic from the stream
table, the latent heats of the components at ASSUMED reflux ratios, each column's two duties
closing its energy balance with the sensible heats of its feed and products (in each energy
stream's source; C-101's feed at 353 K flashes about 39 % of its HF at 150 kPa, so its reboiler
takes 474 kW and its condenser 671 kW). The other sensible heats are counted where they exceed
about 5 kW: the wash water heated to 353 K (Q17, 102.5 kW), the carbonylated mass cooled before
let-down (Q18, 25.7 kW), the dissolver (Q19, 22.1 kW) and the dose (Q20, 9.2 kW, tempered water
on steam). Left out, each a heat given up to the surroundings in a mixer or tank (ASSUMED, no
utility): the acid purge and wash water cooling in M502 to 343 K (18.0 kW), and M101, M301, M403,
SP402 and M404 (3.2, 4.0, 3.9, 0.7 and 2.9 kW). Power ASSUMED per section. Core's
conversion model puts a step's power into its cooling duty, so Q7 holds P2's 8 kW and Q9 P3's
29 kW, the CO compressor's 19.6 kW among them, though that heat leaves in the compressor's
after-cooler to the same cooling water; core's semi-batch and dryer models do not, so R-101's
agitator heat (part of P1's 30 kW) is not in Q1 and the dryer's power not in Q13 (ASSUMED, not
counted). Per kg of ibuprofen: 3.31 kWh of steam, 1.71 kWh to cooling water, 1.74 kWh to
brine, 0.22 kWh of electricity.

**D-010 LCI.** lca/lca.yaml: a gate-to-gate inventory per kg of dried ibuprofen with economic
allocation to the acetic acid co-product at ASSUMED relative prices (1 : 0.05, 97.8 % to
ibuprofen). Linked in the Atlas build: acetic anhydride (acetic-anhydride-1), hydrogen
(hydrogen-1), hydrochloric acid 33 wt% (hydrogen-chloride-1), the steam as heat, water,
electricity, cooling water and wastewater. Gaps: isobutylbenzene, HF, CO, hexane (no library
producer; no proxy linked), the brine's refrigeration, the HF scrubber, the vent's oxidation (0.094 kg of CO2 per kg of ibuprofen from its CO),
the residues' incineration and the catalysts (Raney nickel 8 kg, PdCl2 7.8 g and PPh3 4.75 kg per
batch, from SRC-1's loadings with ASSUMED losses).

**D-011 Hazards.** Anhydrous HF (toxic, corrosive; boils at 293 K) is the main hazard: R-101
works at about 800 kPa(a) (HF's vapour pressure 632 kPa(a) at 353 K, SRC-4) in Hastelloy C or
Monel, padded with nitrogen (168 kPa at 353 K); its relief set pressure is ASSUMED at 950
kPa(g), 1051 kPa(a), which HF's vapour pressure and the pad, compressed with the temperature,
reach at 365.8 K, the MTT of the screening (pure HF's vapour pressure, the lower basis; no
venting of the pad credited). Thermal screening (cheme process reactor-hazards): dT_ad
5.5 K (the HF dilutes the heat), accumulation up to 0.86 (a slow reaction under dosing), MTSR
357.7 K, 8 K below the MTT; no TD24, so no criticality class. The heat of the ketone's
complexation by HF is not counted (L-3): calorimetry must confirm the screening. The dosing is
interlocked with R-101's temperature, agitation and cooling. The hydrogenation and the carbonylation
are not screened by core (L-2); by hand from the year averages, their full reaction heat over
the charge's heat capacity gives an adiabatic rise of about 190 K for R-201 (43.4 kW over
0.228 kW/K) and 200 K for R-301 (82.9 kW over 0.414 kW/K). Both gases are fed on demand
(ASSUMED): with the feed stopped, the gas in the head space alone can react about 5 % of the
IBAP in R-201 (1.15 kmol of hydrogen against 23 kmol used a batch, about 10 K) but about 40 %
of the IBPE in R-301 (8.5 kmol of CO against 21.4 kmol, about 80 K, less as the pressure and
the rate fall). So the gas feeds are tripped on high temperature and loss of cooling (ASSUMED),
and R-301's carbonylation needs calorimetry before the design goes on. Hydrogen (R-201) and carbon
monoxide at 16.6 MPa (R-301, toxic and flammable) need gas detection, a high-pressure relief to
the thermal oxidiser and a CO-rated enclosure; hexane (CR-401 to T-402) is handled under
nitrogen. Raney nickel is pyrophoric when dry: kept under water. No HAZOP yet.

## Core features used and limits

Core 1.13.0: reactor: semibatch with thermal screening; conversion steps by reaction
conversions and by selectivities; component separators (recovery:); a crystalliser with an
imposed yield and spectators; a filter; a dryer with its energy and drying rate; five tear
streams and eight design specifications solved together; the batch recipe with vessel sizing.

- **L-1** No property package covers these liquids (HF with aromatics, aqueous HCl with the
  acids): duties are lumped heat capacities, latent heats and formation enthalpies.
- **L-2** The hydrogenation and the carbonylation are conversion steps: no gas-liquid
  semi-batch with a dosed gas at the examples' pressures, so neither is screened thermally by
  core (the hand sizes in D-011) and the recipe sizes neither vessel.
- **L-3** The ketone-HF complexation and HF's association are not counted in the heats.
- **L-4** No open solubility of ibuprofen in hexane was read: the crystallisation yield is
  imposed (80 %), the cake wash is not modelled, and the product (99.56 wt%) is below SRC-2's
  recrystallised 99.7 to 99.8 %.
- **L-5** The columns are component separators with ASSUMED recoveries, not stage models; the
  isomer lump ISO and 3-IPPA are not resolved by volatility.
- **L-6** Core 1.13.0's validator checks only the first `selectivity:` reactor of a flowsheet
  (the loop over steps rebinds the reaction lookup it uses), so R201 is written with reaction
  conversions (process/reactions.yaml) and R301 keeps its selectivities; reported to core as
  [ChemE-as-Code/core#336](https://github.com/ChemE-as-Code/core/issues/336).
