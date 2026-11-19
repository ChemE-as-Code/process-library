# Design decisions: ibuprofen-1

Ibuprofen by the BHC three-step catalytic route, a batch plant at the concept stage (issue
[#508](https://github.com/ChemE-as-Code/process-library/issues/508)). Every value the files
carry is given with its source, or marked ASSUMED; the numbers live in the YAML files, this file
keeps the decisions and the reasons.

## Source register

| id | source | what it gives | read |
|---|---|---|---|
| SRC-1 | Elango et al. (Hoechst Celanese), US 4 981 995 A (1991), Method for producing ibuprofen, <https://patents.google.com/patent/US4981995A/en> | Example 1 (acylation: 254 g IBB, 385 g Ac2O, 1877 g HF, 80 C, 3 h, 85 % conversion, 81 % selectivity to IBAP; HF vented through a caustic scrubber); Example 2 (Pd/C hydrogenation in methanol, 30 C, 100 psig, 99.5 %, 96.6 %); Example 3A (Raney nickel, neat IBAP, 70 C, about 3 h, >99 % conversion, 98 % IBPE, 1.5 % IBPET); Examples 49, 50, 100 (carbonylation at 125 to 130 C and 2000 to 3100 psig CO; Example 100 without solvent in 26 % HCl, H+/IBPE 0.75, PdCl2 and PPh3 at Pd:P:IBPE 1:12:15050, 2 h 35 min, 99 % conversion, 96.6 % ibuprofen, 1.0 % 3-IPPA, 0.0 % IBS, 0.8 % heavy ends); Example 106 (81 % of the Pd complex recovered, 16 % as metal); comparative example G (400 psig: 20 % ibuprofen); CO pressure range 500 to 5000 psig | opened 2026-11-19, the examples named |
| SRC-2 | Hoechst Celanese, US 5 151 551 A (1992), Method for purification of ibuprofen comprising mixtures, <https://patents.google.com/patent/US5151551A/en> | Example 1 (700 g crude, about 90 %, in hexane, water washes at 60 C to pH >= 2.9, 30 wt% solution cooled at 0.3 C/min to 25 C, held 1 h, to 5 C, filtered at 10 C, washed with 5 C hexane, recrystallised at 40 wt%, dried at 50 C and 49 mm Hg: assay 99.7 %, Pd 2.6 ppm, TPP + TPPO 3.0 ppm); Example 2 (washes in heptane at 70 C, the solvent flashed, a 50 mm x 1.2 m packed column, lights to 130 C, the cut at 130 to 134 C and 0.3 to 0.7 mm Hg, assay 88.6 to 97.4 %, crystallisation from 25 wt% heptane: 99.8 %); no yields, no solubility data | opened 2026-11-19 |
| SRC-3 | US EPA (1997), Presidential Green Chemistry Challenge, Greener Synthetic Pathways Award (BHC Company), <https://19january2021snapshot.epa.gov/greenchemistry/presidential-green-chemistry-challenge-1997-greener-synthetic-pathways-award_.html> | Bishop, TX, 7.7 million lb/a, commercial since 1992; three catalytic steps instead of six stoichiometric; about 80 % atom utilisation (about 99 % with the recovered acetic acid); HF recovered and recycled at more than 99.9 % | opened 2026-11-19 |
| SRC-4 | thermo 0.6.1 and chemicals 1.5.2 (C. Bell and contributors, MIT), package values (library ADR 0037) | liquid molar volumes, heat capacities, vaporisation and formation enthalpies, HF's vapour pressure, identifiers; the method of each named where it is used (process/materials.yaml, process/reactions.yaml) | run 2026-11-19 |

Not used: no open kinetics of the HF acylation, no open solubility of ibuprofen in hexane, no
open heat of reaction of any of the three steps was found in the time of this study.

## Decisions

**D-001 Route.** The BHC route of SRC-1: acylation of isobutylbenzene in anhydrous HF,
hydrogenation of the ketone, Pd-catalysed carbonylation of the alcohol. It is the industrial
route SRC-3 describes (three catalytic steps, acetic acid the only by-product, HF recycled),
and SRC-1 gives conditions and results for every step. Rejected:
- the Boots route (six stoichiometric steps: Friedel-Crafts acylation with AlCl3, Darzens
  condensation with ethyl chloroacetate, hydrolysis and decarboxylation, oxime, nitrile,
  hydrolysis): SRC-3 names it the older technology with less than 40 % atom utilisation and
  large aqueous salt wastes; no open source with its step data was read;
- Pd/C hydrogenation in methanol (SRC-1 Example 2): needs a solvent to remove again and gives
  96.6 % selectivity against Raney nickel's 98 % neat (Example 3A);
- carbonylation in a solvent (methyl ethyl ketone, Examples 49, 50, 106): Example 100 runs
  without one at 99 % conversion and the same selectivity, so no solvent loop is needed;
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
batch (SRC-1 Example 1), hydrogen 5 % and CO 10 % above their use (ASSUMED, vented), 0.75 mol
of HCl per mol of IBPE (SRC-1 Example 100) with a 33 wt% hydrochloric acid make-up, 3 kg of
wash water per kg of crude (SRC-2: about 1.5 kg per wash, two washes), 25 wt% ibuprofen in the
crystalliser feed (SRC-2 Example 2). Acetic anhydride 99.5 wt% (acetic-anhydride-1).

**D-005 Reactions, kinetics and heats.** process/reactions.yaml. The acylation's 19 % not
reported as IBAP is lumped as isomers (ISO, ASSUMED); the hydrogenation's 0.5 % not accounted
for is put on the over-reduction, the carbonylation's 1.6 % on the heavy ends (the ether of two
IBPE, ASSUMED). Only the acylation has rate laws (second order, ASSUMED, calibrated so that a
batch of Example 1 reaches 85 % in 3 h at 353 K, Ea 60 kJ/mol ASSUMED): R101 is a semi-batch
with the anhydride dosed over 1.5 h at 353 K instead of the example's all-in charge, so that
the exotherm is dose-controlled. The hydrogenation and carbonylation are conversion steps
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
recycled; the melt washes (V-401) take 99.5 % of the HCl to the wastewater.

**D-008 Purification.** SRC-2 Example 2's sequence with Example 1's hexane: washes on the melt at
353 K (SRC-2 washes in the hydrocarbon solution; on the melt here, so no solvent is flashed
before the column, ASSUMED); the packed vacuum column C-401 takes the lights, the cut at 403 to
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
table, the latent heats of the components at ASSUMED reflux ratios (in each energy stream's
source). Power ASSUMED per section. Per kg of ibuprofen: 3.34 kWh of steam, 1.53 kWh to cooling
water, 1.63 kWh to brine, 0.21 kWh of electricity.

**D-010 LCI.** lca/lca.yaml: a gate-to-gate inventory per kg of dried ibuprofen with economic
allocation to the acetic acid co-product at ASSUMED relative prices (1 : 0.05, 97.8 % to
ibuprofen). Linked in the Atlas build: acetic anhydride (acetic-anhydride-1), hydrogen
(hydrogen-1), hydrochloric acid 33 wt% (hydrogen-chloride-1), the steam as heat, water,
electricity, cooling water and wastewater. Gaps: isobutylbenzene, HF, CO, hexane (no library
producer; no proxy linked), the brine's refrigeration, the HF scrubber, the vent's oxidation,
the residues' incineration and the catalysts (Raney nickel 8 kg, PdCl2 7.8 g and PPh3 4.75 kg per
batch, from SRC-1's loadings with ASSUMED losses).

**D-011 Hazards.** Anhydrous HF (toxic, corrosive; boils at 293 K) is the main hazard: R-101
works at about 800 kPa(a) (HF's vapour pressure 632 kPa(a) at 353 K, SRC-4) in Hastelloy C or
Monel, padded with nitrogen; its relief set pressure is ASSUMED at 950 kPa(g), where HF boils at
373.15 K, the MTT of the screening. Thermal screening (cheme process reactor-hazards): dT_ad
5.5 K (the HF dilutes the heat), accumulation up to 0.86 (a slow reaction under dosing), MTSR
357.7 K, 15 K below the MTT; no TD24, so no criticality class. The heat of the ketone's
complexation by HF is not counted (L-3): calorimetry must confirm the screening. The dosing is
interlocked with R-101's temperature, agitation and cooling. Hydrogen (R-201) and carbon
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
  semi-batch with a dosed gas at the examples' pressures, so neither is screened thermally and
  the recipe sizes neither vessel.
- **L-3** The ketone-HF complexation and HF's association are not counted in the heats.
- **L-4** No open solubility of ibuprofen in hexane was read: the crystallisation yield is
  imposed (80 %), the cake wash is not modelled, and the product (99.56 wt%) is below SRC-2's
  recrystallised 99.7 to 99.8 %.
- **L-5** The columns are component separators with ASSUMED recoveries, not stage models; the
  isomer lump ISO and 3-IPPA are not resolved by volatility.
- **L-6** Core 1.13.0's validator checks only the first `selectivity:` reactor of a flowsheet
  (the loop over steps rebinds the reaction lookup it uses), so R201 is written with reaction
  conversions (process/reactions.yaml) and R301 keeps its selectivities; to be reported to core.
