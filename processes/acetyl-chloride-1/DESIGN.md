# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Acetyl chloride from acetic acid and phosphorus trichloride, issue
ChemE-as-Code/process-library#142, a batch entry of core#158. Concept stage: design basis, batch
recipe, balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-06): library `main` at b8043f4c (core pin v1.8.0, 4e8fd80); cheme-as-code
1.8.0: `reactor: semibatch` with `batch.vent` (core ADRs 0050, 0054), the batch still `still:`
(ADR 0055), `process/recipe.yaml` with vessel, jacket, `distil from:` and `units:` over several
steps (ADRs 0051, 0052, 0055, 0057), per-batch LCA consumables (ADR 0053). Library ADR 0035: one
dedicated train, campaigns out of scope (D-013). Templates: `benzoyl-chloride-1` (vent, still and
a specified-split column) and `p-toluenesulfonyl-chloride-1`.

Core pin v1.9.0 (2026-11-06, 314642c): the models write the duties of their energy streams (core
ADR 0059), so R101's Q2 and the still's net boil-up Q3 are now `calculated` by `cheme process
propagate --fill`. The still's reboiler keeps its reflux share and its heat-up on their own
streams, Q7 and Q8, and R-101's typed Q2 was found to deduct a vapour that never left R-101
(D-009, D-014). The semi-batch screening gives the MTSR over the batch and the gas released at
a cooling failure against R-101's vent capacity, 50 m3/h (ADR 0058, D-011, D-014). Requires
cheme-as-code 1.9 (plant.yaml). No recycle is modelled (the residue's recycle is a variant,
D-008), so the tears of ADR 0060 are not used.

Core pin v1.10.0 (2026-11-06, c55e9c7): the still carries its column (core ADR 0061), so the
specified split K101, its return stream S11, the mixer M102 and the reboiler's typed reflux share
Q7 go; the still's 10 stages at reflux ratio 1 give 99.43 wt% acetyl chloride at 98.19 %
recovery and pass 19.2 % of the charge's PCl3, where the split assumed 6 %. The still heats its
own charge (`still.heat_up`, ADR 0063: the typed Q8 goes), writes its condenser's duty on Q4
(`still.condenser_port`), and the product's subcooling moves to a cooler of its own, E104 (Q9).
The vent's vapour and condenser (ADR 0062) were run on a scratch copy and not adopted: they
model the HCl's vapour, not the head space's and the nitrogen's, which carry most of it here.
Requires cheme-as-code 1.10 (plant.yaml). D-015.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; NIST WebBook, PubChem and Wikipedia pages; the
open data tables packaged in the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | CS 272 248 B2, J. Pelyva et al. (Nitrokemia Ipartelepek), published 1991-01-15: simultaneous preparation of N-phosphonomethyliminodiacetic acid and C1-4 carboxylic acid chlorides, https://patents.google.com/patent/CS272248B2/en | Example 1: 180 g (3 mol) acetic acid, 137.3 g (1.0 mol) PCl3 added below 40 C, then 30 min at 40-50 C; the upper acetyl chloride layer separated for use (no yield, no purity); the lower phase 96 g, phosphorous acid with about 6 wt% HCl, 2 wt% acetyl chloride and 10 wt% acetic acid, diluted and used in a phosphonomethylation. Examples 2 and 3: the lower phase stripped, or re-treated with PCl3. Claim 1: PCl3 to acid 1:2.5 to 1:3.5 at 0-20 C. Description: lower phase typically 80-98 % phosphorous acid, 0-2 % acid, 1-5 % acyl chloride; phases separated by settling | read; patent, facts only | D-001, D-004, D-005, D-006 |
| SRC-2 | US 4 209 460 A, A. Ohorodnik, E. Auer, K. Gehrmann (Hoechst AG), 1980: Production of pure acetyl chloride, https://patents.google.com/patent/US4209460A/en | description: commercial acetyl chloride is about 98 % pure, many uses need at least 99 %, and some fields not more than 1 ppm P (read 2026-11-06 for D-015); phosphorus compounds in acetyl chloride come from PCl3; acetyl chloride (bp 50.9 C) and PCl3 (75.9 C) are hard to separate by distillation at low PCl3 because their boiling and dew curves lie close; 1-20 L of chlorine per L turns the PCl3 into PCl5, which stays in the bottoms. Example 1 (no chlorine): a 2 m column of 50 mm packed with 8 mm saddles, reflux 1:1, 2.8 L/h of a crude with 125 ppm P, 2.32 L/h overhead with 9 ppm P. Examples 2 and 3: with 11-12.5 L chlorine per L, above 99 % acetyl chloride and below 1 ppm P. The crude came from another process (a phospholane synthesis) | read; patent, facts only | D-002, D-008, D-015 |
| SRC-3 | US 4 060 546 A, B. Blaser, H.-G. Germscheid, K.-H. Worms (Henkel), 1977 (priority 1961): acylation products of phosphorous acid, https://patents.google.com/patent/US4060546A/en | background: PCl3 and anhydrous acetic acid in a 1:3 ratio as prior art; the invention reacts PCl3 with acetic acid and water to phosphonic acids with two P atoms per molecule, acetyl chloride distilling off | read; patent, facts only | D-004, D-005 (side reaction not modelled) |
| SRC-4 | The `chemicals` 1.5.2 package (core's environment): its packaged CRC Handbook tables (`heat_capacity.CRC_standard_data`: standard formation enthalpies and liquid heat capacities; `miscdata.CRC_organic_data`, `CRC_inorganic_data`: densities, boiling and melting points), `phase_change.Hfus` | acetic acid (l) -484.3 kJ/mol, cp 123.3 J/(mol K), 1044.6 kg/m3; acetyl chloride (l) -272.9, 117.0, 1105.1, Tb 324.15 K; PCl3 (l) -319.7, 1574 kg/m3, Tb 349.15 K, heat of vaporization 30.5 kJ/mol at Tb; phosphorous acid (cr) -964.4, 1650 kg/m3, Tm 347.55 K, fusion 12.8 kJ/mol; water (l) -285.8; HCl (g) -92.3 and cp 29.1 | open data package queried 2026-11-06; facts only. The CRC values come from the tables packaged in `chemicals`, not from the printed (licensed) handbook | materials, reactions, D-005, D-009 |
| SRC-5 | NIST Chemistry WebBook, SRD 69: acetyl chloride (C75365), acetic acid (C64197), PCl3 (C7719122), water | Antoine constants (acetyl chloride 266.9-324.2 K and acetic acid 290.3-391.0 K, McDonald, Shrader et al. 1959; PCl3 221.6-347.3 K and water, Stull 1947); acetyl chloride Tb 325 +/- 2 K (mean of 10), heat of vaporization 30.1 kJ/mol at 323.9 K, liquid cp 117.2 J/(mol K), formation enthalpy -272.0 to -275.2 kJ/mol; acetic acid heat of vaporization 40.3 kJ/mol at 340 K | read | materials, D-007 |
| SRC-6 | PubChem CIDs 6367 (acetyl chloride), 24387 (PCl3), 407 (phosphonic acid) | identity (formula, InChIKey, ChEBI cross-reference); HSDB: acetyl chloride and PCl3 react violently with water to the acid and HCl | read (PUG REST) | registry, reactions |
| SRC-7 | Wikipedia, Phosphorous acid, https://en.wikipedia.org/wiki/Phosphorous_acid | mp 73.6 C; on heating to about 200 C it disproportionates to phosphoric acid and phosphine; made industrially by hydrolysing PCl3 | read; CC BY-SA, facts only | D-007 (heating limit), D-012 |
| SRC-8 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-9 | processes/acetic-acid-1, asu-1, phosphorus-oxychloride-1, chlor-alkali-1 (this library) | glacial acetic acid with 691 ppm water (its product S21); gaseous nitrogen; PCl3 from P4 and Cl2 as an internal block of phosphorus-oxychloride-1 (not exported); chlorine | library, internal | D-004, D-012 |
| SRC-10 | Ullmann's Encyclopedia of Industrial Chemistry, Acetic Acid (doi:10.1002/14356007.a01_045) | - | not read (licensed); named by the route scouting as describing the acetic anhydride + HCl route | route lead only |

Searched and not found openly (2026-11-05/06): kinetics or calorimetry of acetic acid with PCl3, a
measured heat of reaction, the yield and purity of acetyl chloride on this route at plant scale,
a TD24 of the reaction mass, liquid-liquid data of acetyl chloride with phosphorous acid, the
solubility of HCl in the two phases, VLE data of acetyl chloride with PCl3, a measured liquid
heat capacity of PCl3 or of liquid phosphorous acid, a plant's specific consumptions and prices.

## D-001 Route and boundary (2026-11-06)
Decision: the PCl3 route of SRC-1, Example 1: 3 CH3COOH + PCl3 -> 3 CH3COCl + H3PO3, PCl3 dosed
into acetic acid at 313 K, the mixture settled into an upper acetyl chloride phase and a lower
phosphorous acid phase, the upper phase distilled at atmospheric pressure in a batch still with
a short column; the HCl the acid's water gives vented through a brine condenser to a water
scrubber; one product on a dedicated train (D-013). Boundary feeds: acetic acid, PCl3, process
water, electricity, LP steam, nitrogen (per batch); returns: cooling water, brine; outputs:
acetyl chloride, crude phosphorous acid (a co-product), the still residue to hazardous-waste
incineration, the scrubber bleed to neutralisation.
Reason: the route the issue and the scouting recommend for a batch entry, the classic batch
preparation with an open example (amounts, temperatures, times, the lower phase). It exercises a
dosed semi-batch with a vent, a phase split in the same vessel (recipe `units`) and core's
batch still.
Rejected: acetic anhydride with HCl (the industrial route per the scouting and SRC-10, not read;
US 5 672 749 A absorbs HCl in a circulating Ac2O/AcOH stream in a column): semi-continuous, a gas
dose with reactive distillation; a variant on the continuous track. Acetic acid with phosgene
(US 2 013 988 A, scouting): gas-liquid at about 110 C with the product evaporated as it forms;
a variant. Acetic acid with thionyl chloride (thionyl-chloride-1): another route.
Links: acetic acid from acetic-acid-1, nitrogen from asu-1. PCl3 has no exported library
producer (D-012). chlor-alkali-1 is named only in the gap text of the PCl3 proxy.

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: 2000 t/a of distilled acetyl chloride (252.525 kg/h year average), 7920 h/a, ASSUMED.
Product specification (since 2026-11-06, D-015): at least 99.0 wt% acetyl chloride, after SRC-2
(commercial grade about 98 %, at least 99 % for many uses); no phosphorus limit is set (a
low-phosphorus grade, below 1 ppm P in SRC-2, needs a chlorine treatment, D-008). Modelled
product (S10, core 1.10.0's column, D-015): 99.43 wt% acetyl chloride, 0.573 wt% PCl3 (about
1293 ppm P) and 2 ppm acetic acid by mass. **No open source states a purity or a yield for this
route**: the 99.43 wt% is the model's on an ideal liquid (D-007, D-015), with no dissolved HCl
(L-6). SRC-2's column without chlorine reached 99.32 % from another crude. Until core 1.10.0 the
column's specified split gave 99.84 wt% with 0.162 wt% PCl3 (366 ppm P), on the 6 % PCl3 share
D-015 replaces.
Reason: no open market or plant figure was used; a few thousand tonnes a year is a plausible
size for a dedicated batch train of a fine acid chloride. The LCI is per kg and does not depend
on the scale; the batch size does (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 1459.9 kg of acetyl chloride (stream S10); the recipe
(`process/recipe.yaml`) has two unit procedures:
- REACT on R-101, one vessel over E101, R101 and D101 (`units`, core ADR 0057): nitrogen purge
  0.25 h, charge the acetic acid 0.5 h, warm 298 -> 313 K 0.54 h (from the jacket), dose the
  PCl3 2 h and post-reaction 0.49 h to 0.95 conversion of the PCl3 (both from R101's model),
  settle 1 h, drain the lower phase 0.5 h, transfer the upper phase 0.5 h: 5.781 h;
- DISTIL on C-101 with its column K-101 over ST101 (the still and its column, D-015) and E102:
  receive 0.5 h, distil 2.07 h (from ST101's boil-up at reflux ratio 1), cool the residue 0.5 h,
  drain 0.5 h: 3.57 h (3.63 h with the 1.9.0 one-stage still at 75 kW net).
R-101 is the bottleneck: cycle 5.781 h, 1370.0 batches in 7920 h; one batch takes 8.85 h from
the purge to the residue's drain. The flowsheet's flows are the recipe's year averages: 1459.9
kg x 1369.99 / 7920 h = 252.53 kg/h of S10 against the flowsheet's 252.52 kg/h (no
`cheme.recipe-basis` finding). The batch size
was found by fixed-point iteration, since the warming time depends on the vessel and so on the
batch (L-7).
Dosing time: the source doses dropwise in a flask; 2 h is ASSUMED for the plant (the jacket would
allow less, D-005, but a slower dose keeps the accumulation low, D-011).
Vessels (fill 0.8, H/D 1.2, enamelled, ASSUMED): R-101 2.5 m3 (the R10 preferred size, 71 % full
with 1.78 m3 at the end of the dosing, D 1.38 m), as the recipe sizes it from R101's model (core
ADR 0052). Its jacket (U 300 W/(m2 K), 4.89 m2 wetted at the charge) removes 13.36 kW against the
model's peak 9.84 kW, on cooling water entered at its log-mean equivalent: water in at 298.15 K
and out at 308.15 K against the mass at 313.15 K gives (15 - 5) / ln 3 = 9.10 K, so 304.05 K, not
the supply temperature (core takes the coolant as one temperature). The warming runs on a
tempered-water loop at 322/318 K (mean 320.15 K), below acetyl chloride's 324.15 K boiling point
(R101's MTT, D-011); the jacket is switched to cooling water before the dosing starts. C-101 and
K-101 are sized by hand (core sizes neither the still's vessel nor its column, L-4): about 2.5 m3
for 1.53 t (1.39 m3) of upper phase.
Reason: core ADR 0051 puts the batch basis in one place; the dosing, post-reaction, warming and
distillation times come from the models, so a change of the rate law, the jacket or the boil-up
changes the cycle. The settling, draining and transfer times are ASSUMED concept values (SRC-1
gives none).

## D-004 Feeds and charge (2026-11-06)
Decision: 3 mol of acetic acid per mol of PCl3, SRC-1 Example 1's ratio (also the prior art of
SRC-3), with no excess of either. Acetic acid from acetic-acid-1, its glacial acid with 691 ppm
of water by mass (its product S21; its 50 ppm of propionic acid counted as acetic acid, which
would give 50 ppm of propionyl chloride); PCl3 100 % (its POCl3 and dissolved chlorine not
modelled). Per batch: 1206.4 kg of acetic acid (with 0.83 kg of water) and 918.9 kg of PCl3 (1207.6 and
919.9 kg until core 1.10.0: the product now holds more PCl3, D-015). The
feeds are scaled by scripts/balance.py for 2000 t/a.
Reason: the source's ratio; SRC-1's claim allows 1:2.5 to 1:3.5. An excess of acid would leave
more acetic acid in the product and the lower phase, an excess of PCl3 more PCl3 in the product
(D-008); neither is tested here.

## D-005 Reactor R-101: semi-batch with an HCl vent, kinetics, conversion and heat of reaction (2026-11-06)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the acetic acid S2 at 313.15 K, the PCl3
S3 (298.15 K) dosed at a constant rate over 2 h, then the post-reaction to 0.95 conversion of
the PCl3 (`batch.target`; 0.49 h from the model), isothermal at 313.15 K and atmospheric
pressure. Reactions (`process/reactions.yaml`):
- ACCL, 3 CH3COOH + PCl3 -> 3 CH3COCl + H3PO3, rate first order in acetic acid and in PCl3,
  k = 5.5e-4 m3/(kmol s) at 313 K (Ea 50 kJ/mol), ASSUMED;
- HYD, PCl3 + 3 H2O -> H3PO3 + 3 HCl, the water of the acetic acid, fast (k 0.1 m3/(kmol s)),
  ASSUMED: it uses 0.23 % of the PCl3 at the start of the dosing.
`batch.vent: {stream: S5, components: [HCL, ACCL], fraction: {ACCL: 0.00213}}` (core ADR 0054):
all the HCl leaves the liquid as it forms (ASSUMED, none dissolved, L-6), and 0.213 % of the
acetyl chloride formed leaves with it, the vapour that passes the vent condenser, an upper
bound (0.099 % per source; D-010, D-014).
Temperature: 313.15 K is the top of SRC-1's dosing range (below 40 C) and the bottom of its hold
(40-50 C). A semi-batch runs at one temperature (L-8), and a hold at 323 K would sit 1 K below
acetyl chloride's boiling point.
Conversion: 0.95 of the PCl3, ASSUMED and calibrated to SRC-1's lower phase. At 1:3 the
unreacted share of the PCl3 leaves the same share of the acetic acid. With 0.95, and 95 % of the
acetic acid left settling into the lower phase (D-006), the lower phase holds 10.1 wt% acetic
acid against the source's 10.6 wt% on an HCl-free basis. Its H3PO3, 0.95 mol per mol of PCl3 (at
87.5 wt%), matches the source's (87.2 wt%, HCl-free). k was then sized so that the post-reaction
to 0.95 takes about the source's 30 min hold. The 5 % of the PCl3 left over is the P carry-over
of D-008.
Heat of reaction: -10.5 kJ per mol PCl3 for ACCL, from the CRC formation enthalpies of SRC-4,
with phosphorous acid as the crystal; with the liquid (fusion 12.8 kJ/mol) it is +2.3 kJ/mol.
**The sign is uncertain**: the lower phase is a concentrated solution, and neither its heat of
solution nor the heat of mixing of PCl3 with acetic acid is known. The exothermic bound is
taken, so that the screening is not optimistic (D-011). HYD: -64.2 kJ/mol with HCl as a gas.
Side reactions not modelled: the acylation of phosphorous acid by acetyl chloride to phosphonic
acids with two P atoms (SRC-3), which would cost acetyl chloride and give HCl; the equilibrium of
acetyl chloride and acetic acid with acetic anhydride and HCl; the mixed P-Cl and P-O-acetyl
intermediates, which the true "PCl3" carry-over consists of in part.
Reason: no open kinetics or calorimetry exists (searched 2026-11-05/06). The second-order law
makes both reactants run down together at the 1:3 ratio, so the rate slows towards the end of
the dosing, where the accumulation peaks (11.7 %, D-011). **The low accumulation is a
consequence of the assumed rate law**, and the conversion of the calibration; both are for
reaction calorimetry with off-gas measurement before basic engineering. The two liquid phases
form during the reaction (the H3PO3 phase separates). The model's kinetics are
pseudo-homogeneous (L-2).
Off-gas (`cheme process recipe`): 4.87 kg per batch (1.69 kg HCl, 3.18 kg acetyl chloride
vapour), peak 30.8 m3/h at 313 K 0.02 h into the dosing, while the water of the charge reacts.
R-101's vent capacity (50 m3/h) and the gas released at a cooling failure: D-014.

## D-006 Phase split D101 and the balance method (2026-11-06)
Decision: the two phases settle in R-101 (D101, one more step of the REACT unit procedure). The
split is specified in scripts/balance.py, calibrated to SRC-1's lower phase. To the lower phase S7
go 99.5 % of the phosphorous acid (0.5 % entrained in the upper phase, ASSUMED), 95 % of the
acetic acid (ASSUMED: the acid prefers the polar phase), 5 % of the PCl3 (ASSUMED) and 0.8 % of
the acetyl chloride (the source's 2 wt% of 96 g, 1.92 g of the 235.5 g formed per mol of PCl3).
Result per batch: 592.8 kg of lower phase (87.50 wt% H3PO3, 10.11 wt% acetic acid, 2.01 wt%
acetyl chloride, 0.39 wt% PCl3), 88.6 g per mol of PCl3 against the source's 96 g, of which 5.8
g is HCl (90.2 g HCl-free); 1527.7 kg of upper phase (96.77 wt% acetyl chloride, 2.86 wt% PCl3).
The source's 6 wt% HCl in its lower phase is not reproduced (L-6, D-010).
Balance method: cheme propagates the semi-batch R101 with both outlets, the still ST101 with its
column (D-007, D-015), the pass-through steps E101, E102, E103, E104 and the scrubber A101 (a
conversion step). scripts/balance.py gives what core has no model for (library ADR 0027). These
are the feeds S1 and S3 for 2000 t/a (linear in the feeds; the script scales the PCl3 by the
ratio of the target to S10), the phase split D101 and the scrubber water S15. It also gives the
temperatures of the still's streams (bubble points by Raoult's law with the materials' Antoine
constants, as the still computes them) and of the adiabatic scrubber's liquor S16, and the
duties Q1, Q5, Q6 and Q9 (D-009). Propagate writes R101's Q2 (ADR 0059) and the still's reboiler
Q3 and condenser Q4 (ADRs 0061, 0063) from those models, and the script prints its own values of
the three as a cross-check only (D-014, D-015). Until core 1.10.0 it also gave the column's split
K101, the mixed residue S12 and the duties Q4, Q7 and Q8. It follows the balance-output contract
(`scripts/check_balance_scripts.py`). The batch size and the feeds were converged together:
propagate, the script, the recipe's cycle, and again (L-7).
Reason: core has no liquid-liquid model that applies. Its NRTL extraction needs binary pairs,
and none is sourced for acetyl chloride, acetic acid and phosphorous acid. A semi-batch is one
liquid (L-2). The source's composition is the only data, so the split is calibrated to it rather
than predicted.
Rejected: the lower phase stripped of its volatiles (SRC-1, Example 2) or re-treated with PCl3
(Example 3) to recover the acetic acid and the acetyl chloride: variants; they would raise the
yield by up to 0.76 % (the acetyl chloride of S7) and give back about 60 kg of acetic acid a batch.

## D-007 Batch still ST101 at atmospheric pressure: one Rayleigh stage is not the product (2026-11-06; the column on it since core 1.10.0, D-015)
Decision: ST101 is core's batch still (`still:`, core ADR 0055): the upper phase S6 boiled at
101.325 kPa(a), Raoult's law with the NIST Antoine constants of acetyl chloride, PCl3, acetic acid
and water (SRC-5), phosphorous acid non-volatile, until acetyl chloride is 50 mol% of the residue
(`end: residue`, ASSUMED). The reboiler gives 150 kW. Until core 1.10.0 the boil-up was entered
as the 75 kW net that leaves as distillate at the column's reflux ratio 1 (D-008), and the
distillation took 2.13 h; since core 1.10.0 the column is on the still and the boil-up is the
reboiler's 150 kW (D-015). The one stage alone (`cheme process stills`, core 1.9.0): 1529.2 kg
of upper phase a batch gave 1512.9 kg of distillate S8 and 16.3 kg of residue S9 (50 mol% acetyl chloride, 15.8 mol% PCl3, 17.6 mol% acetic acid, 16.6 mol%
phosphorous acid), the still from 324.33 to 340.45 K. Heated with LP steam at 412 K, below the
473 K at which phosphorous acid disproportionates to phosphoric acid and phosphine (SRC-7; the
still holds 0.17 wt% of it).
Purity of one stage: **one Rayleigh stage does not reach a credible purity**. The distillate is
97.31 wt% acetyl chloride with 2.61 wt% PCl3, and 90.5 % of the PCl3 of the charge goes over. At
the still's temperatures PCl3's vapour pressure is about 0.4 of acetyl chloride's, so one stage
separates it poorly. The acetic acid (0.07 wt% in the distillate) goes mostly with the lower
phase (D-006). The product needs the column (D-008).
The volatility is declared `assumed` (core reports the basis not sourced): no VLE data of the
pairs were found.
Not modelled (core limits L-4, L-10): acetyl chloride's NIST Antoine fit ends at 324.2 K, so the
still extrapolates it by up to 16 K at the end of the one stage (12 K with the column, to
335.9 K, D-015; `cheme.process-still-note`, info; the 50 mol% end keeps it short of the pure
PCl3 end at 349 K); dissolved HCl, which would leave first as a lights cut (L-6). The charge's
heat-up from 313 to 324 K was the script's Q8 until core 1.10.0 and is now the model's
(`still.heat_up`, D-015).

## D-008 Column K-101 on the still and the PCl3 carry-over (2026-11-06; the column modelled since core 1.10.0, D-015)
Superseded in its model by D-015: since core 1.10.0 the column is core's batch rectification on
ST101 (10 stages, reflux ratio 1), and the split below, its return stream S11 and the mixer M102
are gone. Its PCl3 share is kept here as the record of what D-015 replaced.
Decision until core 1.10.0: the column on C-101 (about 10 theoretical stages, reflux ratio 1,
ASSUMED after SRC-2's 2 m packed column at 1:1) was a specified split of ST101's distillate S8 in
scripts/balance.py. To
the product S10 go 99 % of the acetyl chloride, 6 % of the PCl3 and 1 % of the acetic acid. The
rest, S11, is the column's hold-up and last cut returned to the pot, and leaves with the residue
(M102, cooled in E102, S13). The PCl3 share comes from SRC-2, Example 1: the column without
chlorine took 9 ppm P overhead from a 125 ppm feed with 83 % of the volume overhead, so 0.83 x 9 /
125 = 6 % of the phosphorus. That crude came from another process; the share is ASSUMED to carry
over to this one. Result then: 252.53 kg/h of 99.84 wt% acetyl chloride with 0.162 wt% PCl3 (366
ppm P), 9.17 kg/h back to the pot (70 wt% PCl3); the residue S13 11.99 kg/h (47 g per kg, 60 wt%
PCl3), 4.5 % of the PCl3 fed; yield 92.40 % of theory.
Result since core 1.10.0 (D-015): 252.52 kg/h of 99.43 wt% acetyl chloride with 0.573 wt% PCl3
(1293 ppm P), 19.2 % of the charge's PCl3 overhead; the residue S13 is 11.73 kg/h (46 g per kg of
product, 52 wt% PCl3, 39 wt% acetyl chloride) to hazardous-waste incineration, 3.8 % of the PCl3
fed. Overall yield **92.11 % of theory** on the acetic acid and on the PCl3 (1 mol acetyl chloride
per mol of acetic acid). This is a model result: no source states one. It is an ASSUMED upper
bound, since every loss not modelled only lowers it: the acylation of H3PO3 (SRC-3), the moisture
of the plant, the breathing of the tanks, the HCl that would stay dissolved. Losses of the
theory: 5.23 % unconverted (5 % of the PCl3 by the calibration, D-005; 0.23 % hydrolysed by the
water), 0.76 % in the lower phase, 1.70 % in the still residue (the column holds no hold-up and
returns nothing: the residue takes the 50 mol% acetyl chloride of the end), 0.20 % past the vent
condenser.
Reason then: core 1.8.0's still is one stage with no reflux (ADR 0055) and gives 97.3 wt% (D-007).
Core's Fenske-Underwood-Gilliland shortcut was for continuous columns, and a batch column at
constant reflux was the follow-up core#173, so the column's work was a stated split (as in
benzoyl-chloride-1). SRC-2 says why the PCl3 is the hard part: at low PCl3 contents the boiling
and dew curves of the pair lie close, and its column without chlorine removed 94 % of the P, not
enough for a low-phosphorus grade.
Option, not modelled: SRC-2's chlorine treatment of the crude (1-20 L of Cl2 per L, 10-15
preferred) before the distillation turns PCl3 into PCl5, which stays in the bottoms; it reached
below 1 ppm P. Here the crude holds 2.86 wt% PCl3 (about 6450 ppm P, 50 times SRC-2's 125 ppm),
so the chlorine need would have to be measured: the stoichiometric chlorine to PCl5 is about
5.2 L (STP) per L of crude, inside SRC-2's range, but SRC-2's 11-12.5 L per L on its 125 ppm crude
is a large excess. With the column's 19.2 % carry-over (D-015) the product holds 1293 ppm P,
about 10 times SRC-2's crude: the chlorine question is sharper than the 6 % split made it. A
higher reflux is the other lever: at reflux ratio 2 the same column gives 99.92 wt% with 185 ppm
P (D-015), still far from 1 ppm. PCl5 in a pot with acetic acid would also give acetyl chloride,
POCl3 and HCl. A variant (chlorine from chlor-alkali-1).
Rejected: the still alone as the product's purification (it would present a one-stage distillate
as the product at 97.3 wt%); a cut sequence of the one-stage still (`cuts:`): a first cut is no
purer in PCl3, which is the heavier component; recycling the residue and the column's return
(70 wt% PCl3) to the next batch's R-101: the obvious improvement, it would recover most of the
4.5 % of the PCl3 (3.8 % since D-015, the residue alone), but it is a tear stream across batches
(a variant).

## D-009 Utilities and heat (2026-11-06, model duties 2026-11-06, the still's column 2026-11-06)
Decision (year averages; Q2, Q3 and Q4 from core's models, the rest from scripts/balance.py,
ASSUMED unless sourced):
- Q1 1.79 kW of LP steam (via R-101's tempered-water loop): the acetic acid S1 warmed from 298 to
  313 K (123.3 kJ/(kmol K), SRC-4); about 19.3 kW over the 0.54 h of warming.
- Q2 2.67 kW from R-101 to cooling water: the heat of ACCL and HYD (3.2471 kW) less the PCl3 dose
  warmed from 298 to 313 K (0.5788 kW). Since core 1.9.0 R101's semi-batch model writes it
  (2.66833 kW since D-015's feeds, 2.67099 kW before; `calculated`, `energy_port: q`, ADR 0059);
  scripts/balance.py gives the same two terms as a cross-check. Until then the typed Q2 was 1.27 kW: it also deducted the latent heat
  of the vapour the whole vent gas carries to E-103 and its condensate rewarmed (1.40 kW), as if
  the batch's nitrogen swept the reacting mass. It does not, so that deduction is dropped (D-014).
  The model's peak is 9.84 kW during the dosing (D-003). With the liquid-H3PO3 heat of reaction
  (+2.3 kJ/mol, D-005) Q2 would be about -1.2 kW: R-101 would need heat instead, which its
  tempered-water loop provides (core would then warn that the model's heat flows against Q2);
  the sign is an open input.
- Q3, the still's reboiler, 54.88 kW of LP steam 350 kPa(a) (412 K) to C-101's jacket; 150 kW
  while distilling. Core's still model with its column writes it (ADRs 0061, 0063; ST101's
  `energy_port: steam`, `calculated`): the boil-up, (R + 1) = 2 times the distillate's latent
  heat, 53.6670 kW, and the charge heated from 313.15 K to its 324.33 K bubble point
  (`still.heat_up`), 1.2096 kW (D-015). Until core 1.10.0 it was three streams, the model's net
  boil-up Q3 27.5838 kW and the script's reflux share Q7 27.5838 kW and heat-up Q8 1.2282 kW,
  together 56.3958 kW (D-014).
- Q4 53.67 kW to cooling water: K-101's total condenser, the boil-up's latent heat (core's still
  model on `still.condenser_port`, ADR 0061, D-015). Until core 1.10.0 a script value of 57.38 kW
  that also held the product's subcooling.
- Q9 2.17 kW to cooling water: the product cooler E104, the distillate S8 subcooled from its
  323.99 K bubble point (at its mean composition) to 303.15 K (D-015).
- Q5 0.13 kW to cooling water: the residue S9 cooled from 335.89 to 303.15 K in the still before
  it is drained (0.14 kW from 340.45 K until core 1.10.0).
- Q6 0.35 kW to brine (258/263 K): the vent condenser E-103 (D-010), its load per source: R-101's
  gas off the reacting mass saturated with the upper phase's vapour at 313 K (0.17 kW, an upper
  bound), the still's and the receivers' nitrogen saturated over the product at 303 K (0.17 kW),
  R-101's dry purge (0.01 kW). Until core 1.9.0 it was 1.28 kW, all of the batch's gas taken
  saturated at 313 K, on the premise of the 1.8.0 Q2 (D-014).
- Electricity 5.19 kW (0.0206 kWh/kg): R-101's agitator 4 kW for 3.53 h of each 5.78 h cycle
  (2.44 kW, P1); the still's agitator 2 kW for 2.57 h (the distillation, 2.07 h, and the residue's
  cooling) and its reflux pump 1 kW for 2.07 h, 7.20 kWh a cycle (1.25 kW, P2; 1.28 kW with the
  2.13 h distillation until core 1.10.0); the scrubber's pump and fan (1.5 kW, P3).
Every energy flow of the batch is in the flowsheet and so in the LCI per kg (library ADR 0035).
Recorded exclusions, each with its estimate (ASSUMED orders, insulated surfaces at about 1
W/(m2 K)): the heat losses of R-101 (at 313 K, 15 K above the ambient: about 0.1 kW), of C-101 and
K-101 (at 324-336 K: about 0.4 kW while hot, below 1 % of the reboiler's Q3) and of the
tempered-water loop; the still's content heated from its first bubble point to its 335.89 K end
as it boils down, which core's `heat_up` leaves out (about 0.15 kW, 0.86 kWh a batch: the
content's heat capacity at 118 kJ/(kmol K) over the 39 points of the still's profile, `cheme
process stills --json`, D-015); R-101's own evaporative cooling, which the model leaves out of Q2: the
vapour the HCl and the head space displaced by the dose carry off the reacting mass to E-103,
and its condensate rewarmed, at most 0.19 kW (7 % of Q2, taken saturated over the upper phase at
313 K). Less in fact for the HCl's share (86 % of that gas), which forms in the first minutes
over nearly pure acetic acid (4.7 kPa instead of 68 kPa); the head space's share (14 %, about
0.03 kW) leaves over the whole dosing while the liquid's vapour pressure rises towards the upper
phase's, so the bound is not narrowed further. Heat counted twice: Q6's 0.17 kW from R-101's gas
is that evaporation, which Q2 also holds, and Q6's 0.17 kW from the still's and receivers'
nitrogen is vapour Q4 takes as condensed in K-101. The heat the utilities remove is high by at
most 0.34 kW (0.6 % of the 58.98 kW to cooling water and brine; 60.54 kW until core 1.10.0,
D-014, D-015); the
tracing of the crude phosphorous acid tank T-102 (at 313 K: about 0.1 kW); the scrubber's water
evaporated into the nitrogen (about 0.003 kmol/h, 0.04 kW, which cools the bleed a little); the
heats of mixing of PCl3 into acetic acid and of the phase separation, unknown: the span of the
heat of reaction (12.8 kJ/mol, D-005) bounds them at about 3.9 kW (L-11). S16's temperature
follows from the adiabatic scrubber (D-010); the upper and lower phases leave at R101's 313.15 K
after the 1 h settle on the jacket.

## D-010 Vent, vent condenser and HCl scrubber (2026-11-06)
Decision: R-101's vent (S5) and the vents of C-101, K-101 and the tanks go through E-103, a vent
condenser on brine (gas out at 268.15 K, 10 K above the 258 K brine), to A-101, a packed water
scrubber with a bleed of 1 wt% HCl.
- The vapour load, per source (since core 1.9.0, D-014). E-103 takes the HCl (0.0080 kmol/h)
  and the batch's nitrogen (8 Nm3 a batch, 0.0617 kmol/h). Only the HCl and the head space the
  dose displaces (0.0093 kmol/h, 13 % of the inert) leave the reacting mass, taken saturated
  with the upper phase's vapour at 313 K (Raoult: 67 kPa of acetyl chloride, 0.5 kPa of PCl3),
  an upper bound. The still's and the receivers' 3 Nm3 (0.0232 kmol/h) leave K-101's condenser
  and the receivers saturated over the product at 303 K (47 kPa, ASSUMED: the product's
  temperature). R-101's 5 Nm3 purge (0.0386 kmol/h) runs on the dry vessel before the charge and
  carries no vapour. E-103 condenses the acetyl chloride down to its 9.3 kPa at 268 K and all
  the acetic acid, and returns them to R-101: Q6 0.35 kW (0.17 kW from R-101's gas, 0.17 kW from
  the still's nitrogen, 0.01 kW the dry purge cooled). Until core 1.9.0 all of the inert was
  taken saturated at 313 K, which gave 1.28 kW. Core 1.10.0's vent vapour and condenser were
  tried on it and not adopted (D-015).
- R101's vent fraction keeps the 1.8.0 upper bound: all of the inert saturated at 268 K, the dry
  purge too, 0.0070 kmol/h (0.55 kg/h, 0.213 % of the acetyl chloride formed) past E-103, written by
  hand into the flowsheet (D-005, L-3). Per source, without the purge, it is 0.0033 kmol/h
  (0.099 %); the script prints both. The bound is kept, not re-converged: it overstates the
  acetyl chloride lost by 0.29 kg/h (0.12 % of the product), so the LCI's feeds per kg are high
  by about as much, and lowering it would move every stream, the batch and the 1.8.0 comparisons
  of D-014 for that. The PCl3 (3.6 kPa at 268 K, above its partial pressure) passes E-103, on
  the same upper bound 0.0010 kmol/h (0.14 kg/h). It is
  hydrolysed in the scrubber, which is not in the balance (its 0.11 kg/h of HCl would raise the
  bleed from 1.0 to about 1.2 wt%; recorded in lca.yaml's emission_exclusions).
- The scrubber A101 is a conversion step: the acetyl chloride vapour hydrolysed (AHYD, -48 kJ/mol
  with the chloride as a vapour, SRC-4), all HCl absorbed. 53.90 kg/h of process water make a
  bleed S16 of 54.74 kg/h (1.0 wt% HCl, 0.77 wt% acetic acid), 0.217 kg per kg of product, to
  neutralisation. Adiabatic: the HCl's heat of solution (-75 kJ/mol, ASSUMED order of the integral
  heat to a dilute acid) and the hydrolysis warm the water from 298.15 to 304.57 K.
Reason: at 313 K acetyl chloride's vapour pressure is 69 kPa (SRC-5), so any gas leaving R-101
carries more acetyl chloride than gas. A condenser at cooling-water temperature (308 K: 57 kPa)
would recover little, and one on brine recovers 95 % of it. A water scrubber suits a small HCl
load; the bleed is too weak to sell (benzoyl-chloride-1 makes 30 wt% acid from a large load).
**The model's HCl is a lower bound.** It comes only from the acid's water (1.69 kg a batch).
SRC-1's lower phase holds 6 wt% HCl, 5.76 g per mol of PCl3, which would be 38.6 kg a batch. Its
origin (P-Cl and acetyl intermediates, moisture) is not modelled, and core has no HCl solubility
(L-6). The scrubber and the vent line are therefore to be sized for SRC-1's HCl and the upsets of
D-011, not for the model's normal load.

## D-011 Thermal screening, the rate-constant sensitivity and the release cases (2026-11-06, core 1.9.0 2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054, 0058): adiabatic temperature rise of the
whole batch 21.4 K (with the exothermic bound of D-005); largest accumulation of the dosed PCl3
11.7 %, at the end of the dosing; MTSR at that moment 315.8 K, against an MTT of 324.15 K
(`hazard.mtt`: the normal boiling point of acetyl chloride, the product, which is most of the
liquid once the PCl3 is dosed; core's default, the lowest boiling point of the charge and the
dose, would be PCl3's 349.15 K, 25 K too high; core 1.9.0's default leaves the vented HCl and
acetyl chloride out but still takes no product, and gives the same 349.15 K: L-5). The vented HCl
and acetyl chloride add nothing to the MTSR; with the vent blocked they pressurise the vessel,
which the screening does not assess (core note: a peak of 1.87e-4 kmol/(s m3), 0.19 mol/(s m3):
0.33 mol/s or about 31 m3/h for the 1.78 m3 batch, 0.02 h into the dosing).
MTSR over the batch (core 1.9.0, ADR 0058): 313.1 K at the start, 313.7 K at 0.50 h, 314.0 K at
1.01 h, 314.5 K at 1.50 h, 315.8 K at the end of the dosing (2.0 h, X_ac 0.117), back to 314.3 K
at 2.49 h. ACCL sets it (dT_ad 21.4 K); HYD alone gives 0.3 K (313.5 K), so `hazard.reactions` is
not needed. Gas released at a cooling failure at the MTSR: 4.35e-6 kmol/s, 0.41 m3/h at 315.8 K
(the worst moment's content, per batch of the recipe), against R-101's vent capacity of 50 m3/h
(0.008 of it, `cheme.reactor-hazard-vent` info). The main reaction forms no gas: that rate is
the vented share of the acetyl chloride (0.213 %), whose 0.005 kmol from the accumulated PCl3 is
vapour. The largest release over the batch is at 69 s, 31.2 m3/h of HCl at 313.4 K, while the
acid's water hydrolyses the first PCl3 (core's `vent_gas_rate` at every point of the cooling
profile, at that point's MTSR; D-014).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
With MTSR below MTT the class is 1 or 2 if the TD24 lies above the MTSR (1 above the MTT, 2
between), and 5 if it lies below (TD24 < 315.8 K): core's `criticality()` and Stoessel test the
TD24 against the MTSR first (SRC-8). It needs the TD24.
Sensitivity (a scratch copy of the folder, only A divided, everything else as designed;
`cheme process propagate --fill`, `reactor-hazards`, `reactors`, `recipe`; not committed):

| k at 313 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 324.15 K | post-reaction to 0.95 | cycle | gas at the MTSR | largest gas release over the batch, of 50 m3/h | class without TD24 |
|---|---|---|---|---|---|---|---|---|
| 5.5e-4 (design) | 11.7 % | 315.8 K | 8.4 K below | 0.49 h | 5.78 h | 0.41 m3/h | 31.2 m3/h at 69 s, 0.62 | 1, 2 or 5 |
| k/10 | 35.9 % | 321.1 K | 3.0 K below | 7.48 h | 12.77 h | 0.53 m3/h | 37.2 m3/h at 62 s, 0.74 | 1, 2 or 5 |
| k/100 | 80.2 % | 330.5 K | 6.4 K above | 81.6 h | 86.93 h | 0.46 m3/h | 37.9 m3/h at 65 s, 0.76 | 3, 4 or 5 |

The gas columns were rerun with core 1.9.0 on 2026-11-06 (same scratch copies, the ACCL rate's A
divided). The largest release is the water's HCl in the first minute of the dosing in every
case; a slower main reaction leaves more PCl3 for the water, so it rises. None of them counts
the acetyl chloride that boils above the MTT at k/100 (D-014).

Interpretation: the margin is small because the MTT is low. R101 runs 11 K below the boiling point
of its own product. Even a slow reaction gives little temperature rise (dT_ad 21.4 K), but at
k/100 a cooling failure would boil acetyl chloride: an evaporative barrier in a vented vessel,
which then loads E-103 and the scrubber with acetyl chloride vapour: about 0.67 kmol (53 kg) a
batch, the 36 % of the accumulated heat that is left above the MTT (80.2 % x 6.70 kmol x 10.5
MJ/kmol = 56.4 MJ, of which 11 K x 3.29 MJ/K warm the mass to 324 K, the rest at 30.1 MJ/kmol).
At k/100 the cycle (87 h) already rules the design
out. At k/10 the cycle more than doubles and the MTSR is 3 K below the MTT. If the reaction is
in fact endothermic (D-005), there is no thermal runaway of the main reaction at all. The water
cases below are then the hazard that sizes the protection. Open for the next stage: reaction
calorimetry with off-gas measurement (heat and sign of the reaction, accumulation, the HCl
profile), the TD24 of the reaction mass, the lower phase and the residue, and the gas generation
with a blocked vent (the vent capacity and the cases beyond it: D-014).
Release cases (not assessed, reasoning only; for the HAZOP of the next stage):
- (a) Water ingress into R-101. Sources: a leak of the cooling-water jacket (its supply pressure is
  above the vessel's, so it runs inward), of the tempered-water loop, or scrubber water sucked
  back through the vent line (HCl absorption pulls a vacuum when the gas flow stops). PCl3 and
  acetyl chloride hydrolyse violently (SRC-6). 1 kg of water gives 55.5 mol of HCl, about 1.43 m3
  at 313 K and 101 kPa, more than a whole batch's normal HCl (1.69 kg, 0.046 kmol), and 1.2 MJ
  with PCl3. Options to assess: anti-suck-back protection on the vent line (a nitrogen-padded
  seal pot, a vacuum breaker on nitrogen); jacket-leak detection (conductivity of the loop) or a
  non-aqueous heat-transfer fluid on R-101; the vent and the scrubber sized for the water case.
  R-101's vent capacity of 50 m3/h passes the HCl of about 13 kg/h of water at the start of the
  dosing (on top of the 31.2 m3/h then) and 35 kg/h otherwise; a suck-back of scrubber liquor
  far exceeds it (D-014).
- (b) Loss of the scrubber water while R-101 doses: up to 30.8 m3/h of HCl at the start of the
  dosing, and the acetyl chloride vapour, to air. The PCl3 dosing should be interlocked on A-101's
  water flow and on HCl breakthrough at its outlet. Stopping the dosing stops the model's HCl,
  which comes with the water at the start. SRC-1's dissolved HCl (D-010) would keep degassing.
- (c) Loss of brine to E-103: the acetyl chloride the vent gas carries, about 0.039 kmol/h as a
  year average per source (0.143 kmol/h with all of the inert saturated at 313 K, D-010) and
  more at the start of the dosing, while the HCl peaks, goes to the scrubber. There it
  hydrolyses to HCl and acetic acid, about 3 (10) times the normal HCl and about 1.5 (5.0) kW
  of heat. Brine flow and the gas
  outlet temperature of E-103 should be interlocked with the dosing.
- (d) Failure of the warming loop's temperature control, or of the jacket changeover. R-101 is
  warmed by a tempered-water loop at 322/318 K heated by LP steam at 412 K (D-003, D-009), only
  4 K below the MTT at its mean and 11 K above the process temperature. If the loop's steam valve
  fails open, or the jacket is not switched to cooling water before the dosing (D-003), the mass
  heats towards the steam temperature without any reaction. It boils acetyl chloride at 324 K,
  and once that is gone PCl3 at 349 K, with the PCl3 the dosing has accumulated, into E-103 and
  A-101. This is case (c) without a bound: the jacket at full steam temperature delivers about
  300 W/(m2 K) x 4.9 m2 x (412 - 324) K = 129 kW (the area at the charge, so a lower bound; a
  loop that is not pressurised and boils at 373 K still gives about 72 kW). At 30.1 kJ/mol that
  is about 15 kmol/h (1.2 t/h) of acetyl chloride vapour, some 100 times the upper bound of case
  (c), 0.143 kmol/h, for which E-103 (0.35 kW year average) and A-101 are not sized; the batch's acetyl chloride would boil
  off in about an hour. At 324 K that vapour is about 410 m3/h (229 m3/h for the loop at 373 K),
  8.2 (4.6) times R-101's vent capacity of 50 m3/h (D-014). Options to assess: a high-temperature limit on the loop's supply that
  trips the steam valve (independent of the loop's controller); the loop's supply capped below
  the MTT by design (a steam pressure or a hot-water source whose temperature cannot exceed
  324 K); a dosing permissive on the jacket in cooling mode and on R-101's temperature; a
  high-temperature trip on R-101 that isolates the steam and stops the dosing.
Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of acetyl chloride from the flowsheet's year
averages. Acetic acid is linked to acetic-acid-1 (glacial acid by methanol carbonylation), the
nitrogen consumable to asu-1's gaseous nitrogen (`lca/mappings.yaml`), the LP steam counted as
heat (kWh); every other background is a gap with the activity it should connect to. The nitrogen
per batch (8 Nm3, 10.0 kg, ASSUMED: R-101's 2.5 m3 purged with two volumes, the still and the
receivers purged and blanketed) is an `lca.yaml` consumable `per_batch` (core ADR 0053, library
ADR 0035). No water rinse: the train is kept dry (both chlorides react violently with water).
PCl3 proxy (a gap, not a link): P4 + 6 Cl2 -> 4 PCl3, 0.226 kg P and 0.774 kg Cl2 per kg,
stoichiometric; its main burdens would be white phosphorus (no library producer) and chlorine
(chlor-alkali-1). phosphorus-oxychloride-1 models that step as its internal block PCL3 and does
not export it. A correct gap is kept rather than a doubtful link (library ADR 0026); exporting
PCl3 from that entry would close it.
Allocation: mass, between the acetyl chloride and the crude phosphorous acid (lca.yaml
`allocation`, agent proposal): 71.1 % to the acetyl chloride. The crude acid is a co-product: SRC-1
uses its lower phase as it is, diluted, as the phosphorus source of a phosphonomethylation, and
phosphorous acid is a traded chemical (SRC-7). The library hierarchy (docs/system-model.md) has no
physical relationship here, so the WBCSD rule applies. Both are chemical intermediates of a
similar price per kg, ASSUMED (no prices sourced): a ratio below 5 gives mass. With a sourced ratio
above 5 the rule gives economic allocation, and all burdens to the acetyl chloride is the
conservative bound. The mass allocation is written as `method: shares` with the mass shares of
S10 and S7 (0.711 and 0.289; a test keeps them equal to the flowsheet's), because core writes a
mass default without its method and the library's strict LCI build then warns (L-12).
Per kg of acetyl chloride, unallocated: acetic acid 0.826 kg (stoichiometric 0.765; 0.827 until
core 1.10.0), PCl3 0.629 kg (0.583; 0.630), process water 0.213 kg, nitrogen 6.85 g, electricity
0.021 kWh, LP steam 0.224 kWh (0.230 until core 1.10.0, D-015), cooling water 0.232 kWh removed
(0.233 until core 1.9.0 and 0.238 until core 1.10.0, D-014, D-015), brine 0.0014 kWh removed
(0.0051 until core 1.9.0, D-014); out: crude phosphorous acid 0.406 kg, still residue 0.046 kg,
scrubber bleed 0.217 kg. `lca/inventory.csv` lists them allocated (x
0.711). Not counted: the scrubber's tail gas and the tanks' breathing (emission_exclusions).

## D-013 Dedicated train (2026-11-06)
Decision: R-101, C-101, K-101, E-103 and A-101 make only acetyl chloride, batch after batch: 1370
batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms. Acetyl chloride is also made continuously from acetic
anhydride and HCl (D-001); this entry is the batch case.

## D-014 Core 1.9.0: duties from the models, the still's reflux and heat-up apart, R-101's vent capacity (2026-11-06)
Decision, on the core pin's rise to 1.9.0 (314642c), for the three findings core 1.9.0 reported
(two `cheme.process-duty` warnings and a `cheme.reactor-hazard-vent` warning):
- **R101's duty Q2 from the model (ADR 0059).** The typed Q2, 1.2696 kW, against the semi-batch
  model's 2.67099 kW. The model's value is the heat of ACCL and HYD over the batch (3.2503 kW)
  less the PCl3 dose warmed from 298.15 to 313.15 K (0.5793 kW), the script's own first two
  terms. The hand value also deducted 1.4014 kW: the latent heat of the vapour that all of
  E-103's inert carries, saturated with the upper phase's vapour at 313 K (1.2028 kW), and that
  vapour's condensate returned cold and rewarmed (0.1986 kW), as R-101's evaporative cooling.
  But 88.5 % of that inert is the batch's nitrogen, and almost none of it passes over the
  reacting mass. R-101's purge runs on the dry vessel before the charge (the recipe's `inert`
  step), its blanket is static, and the still's and the receivers' nitrogen vents from C-101,
  K-101 and T-101. The gas that leaves the reacting mass is the HCl and the head space the dose
  displaces, 0.0093 kmol/h (13.4 % of the inert). Its vapour and condensate take at most 0.187 kW, 7.0 % of
  the model's Q2 (saturated over the upper phase at 313 K). Less in fact for the HCl's 86 %,
  which forms in the first minutes over nearly pure acetic acid (4.7 kPa instead of 68 kPa), but
  not for the head space's 14 % (about 0.03 kW), which leaves over the whole dosing as the
  liquid turns into acetyl chloride; the bound is kept as it is. So the hand value was wrong by
  about 1.2 kW, and the model's value is kept: the typed duty is dropped, `energy_port: q` names
  Q2, and `cheme process propagate --fill` writes 2.67099 kW (`calculated`). R-101's own
  evaporative cooling is a recorded exclusion with that bound (D-009). It is not split onto a
  stream: it would be heat leaving R-101 with the vapour, not with the jacket, and core's one
  duty per node puts the model's net heat on Q2.
- **E-103's load Q6 per source, on Q2's premise (review of #393).** The typed Q6, 1.2826 kW,
  took the same vapour of all the inert, saturated at 313 K: in 1.8.0 its latent heat was
  balanced by the deduction from Q2, and without that deduction it had no source. Q6 is now
  taken per source (D-010): R-101's gas off the reacting mass at 313 K, 0.1713 kW (the vapour
  of the 0.187 kW bound, condensed and cooled to 268 K); the still's and receivers'
  3 Nm3 a batch saturated over the product at 303 K, 0.1685 kW; R-101's 5 Nm3 purge dry from
  298 K, 0.0094 kW. Together 0.3492 kW, so the 1.4014 kW rise of Q2 comes with a 0.9334 kW cut of
  Q6. What is still counted twice: R-101's 0.17 kW (in Q2 and in Q6) and the still's 0.17 kW
  (in Q4, which takes the whole boil-up as condensed in K-101, and in Q6), at most 0.34 kW, 0.6 %
  of the 60.54 kW to cooling water and brine (D-009). R101's vent fraction keeps the upper bound
  of all the inert saturated (0.213 % instead of 0.099 % per source, 0.29 kg/h of acetyl
  chloride, 0.12 % of the product; D-010), not re-converged.
- **The still's net boil-up Q3 from the model, the reflux and the heat-up apart (ADR 0059).**
  The typed Q3, 56.3958 kW, against the still model's 27.5838 kW. That is no error: the hand
  reboiler held the boil-up the column returns as reflux (the reflux ratio 1 times the
  distillate's latent heat, 27.5838 kW) and the charge's and residue's heat-up (1.2282 kW),
  neither of which the one-stage still holds (L-1, L-4). The duty is split. Q3 is the model's
  net boil-up (`energy_port: steam`, `calculated`). Q7 27.5838 kW (the reflux share) and Q8
  1.2282 kW (the heat-up) are their own assumed streams from LPS, both from scripts/balance.py.
  The three together are the 56.3958 kW reboiler, so the LCI's steam is unchanged.
  Rejected: entering the still's `boilup` as the reboiler's 150 kW (the model would distil in
  half the time, about 1.06 h, and take the reflux for distillate); the reflux share on K101
  (the steam heats the still's jacket, not the column). Superseded by D-015: with core 1.10.0's
  column the reboiler is one model duty again, Q7 and Q8 are gone.
- **LCI.** Per kg of acetyl chloride: cooling water 58.792 -> 60.194 kW, 0.2328 -> 0.2384 kWh
  removed (Q2's rise); brine 1.2826 -> 0.3492 kW, 0.0051 -> 0.0014 kWh removed (Q6 per source);
  LP steam 58.184 kW, 0.2304 kWh, and electricity 0.0207 kWh unchanged.
- **The MTT stays given (ADR 0058).** Core 1.9.0's default leaves the vented HCl and acetyl
  chloride out, but the product is no candidate, so it gives PCl3's 349.15 K (scratch copy
  without `hazard.mtt`, 2026-11-06). `hazard.mtt: 324.15` stays (L-5).
- **`hazard.reactions` not used.** ACCL sets the MTSR (315.8 K); HYD alone gives 313.5 K. The
  default, every reaction with the largest run to completion, is the main reaction (D-011).
- **Vent capacity (ADR 0058).** `hazard.vent_capacity: 50` m3/h at R-101's 101.3 kPa(a), ASSUMED.
  It is the design of R-101's vent line, E-103 and A-101 that D-010 asks for: sized for SRC-1's
  HCl and not for the model's normal load alone. The basis is the model's normal peak, 30.8
  m3/h of HCl at 313 K at the start of the dosing (`cheme process recipe`), plus SRC-1's 38.6 kg
  of HCl a batch released evenly over the 2 h dosing (1.059 kmol, 13.6 m3/h at 313 K). That is
  44.4 m3/h, rounded up to 50 (no vent sizing yet: there is no P&ID). Against a cooling failure
  (`cheme process reactor-hazards`; core's `vent_gas_rate` over the cooling profile; D-011's
  table), the gas released is 0.41 m3/h at the MTSR (0.008 of it, `cheme.reactor-hazard-vent`
  info) and 31.2 m3/h at 69 s, the largest over the batch (0.62). At k/10 the largest is 37.2
  m3/h (0.74), at k/100 37.9 m3/h (0.76). Core compares the vent's components only. The gas
  leaving R-101 also carries the liquid's vapour: about 5 % at the HCl peak (acetic acid at 4.7
  kPa), up to two thirds at the end of the dosing, where the gas is small. The line from R-101 to
  E-103 is sized for about 53 m3/h (for example DN50, about 6.8 m/s), ASSUMED.
- **Design finding: the vent covers every cooling failure core screens, but not the boiling and
  water cases.** These are open for the relief study and the HAZOP of the next stage:
  (1) At k/100 the MTSR (330.5 K) lies above the MTT, and the acetyl chloride boils, which
  core's gas release does not count. Once the mass reaches 324.15 K, at most 0.65 kmol/h of
  vapour boils off (17.3 m3/h at 324 K: ACCL's rate law at 324.15 K with the worst moment's
  content, 5.45 kW at 30.1 kJ/mol; scratch copy, 2026-11-06). That is within the vent, but 15.6
  times E-103's year-average 0.35 kW (4.2 times the 1.28 kW upper bound of D-010), so the vapour would reach A-101 as in release case (c).
  E-103 is to be sized for it, or the dosing rate set from calorimetry.
  (2) Release case (d), the warming loop's steam valve open: about 410 m3/h of acetyl chloride
  vapour at 324 K (229 m3/h for a loop at 373 K), 8.2 (4.6) times the vent capacity (D-011). It
  must be prevented (an independent high-temperature trip on the loop's steam and on R-101, the
  loop's supply capped below the MTT), not vented.
  (3) Release case (a), water ingress: 1.43 m3 of HCl per kg of water at once. The vent passes
  a jacket leak of about 13 kg/h of water at the start of the dosing (35 kg/h otherwise). A
  suck-back of scrubber liquor far exceeds it: the anti-suck-back protection is the safeguard.
  (4) A blocked vent: at the design kinetics the main reaction forms no gas, and the mass at its
  MTSR (315.8 K) stays below its boiling point. So a blocked vent pressurises R-101 through the
  water and boiling cases above, and through the HCl the dosing forms. R-101 needs a relief
  device (a rupture disc to a catch tank or the scrubber) sized for them, and the PCl3 dosing
  interlocked on R-101's pressure and on the vent flow (D-011).
  The flowsheet keeps 50 m3/h, the design case's basis, until the relief study sizes the vent.
  Reasoning only, not a relief sizing.

## D-015 Core 1.10.0: the column on the still, its heat-up and condenser; the vent's vapour tried and not adopted (2026-11-06)
Decision, on the core pin's rise to 1.10.0 (c55e9c7), feature by feature, adopted only where the
model is at least as credible as the hand value it replaces:
- **The column K-101 on the still (ADR 0061), adopted.** ST101 takes `still.column: {stages: 10,
  reflux: constant, ratio: 1}`, its `boilup` is the reboiler's 150 kW (no longer the 75 kW net),
  and its end stays at 50 mol% acetyl chloride in the residue (D-007). Basis: SRC-2 Example 1's
  column, 2 m packed with 8 mm saddles at reflux 1:1; the 10 theoretical stages (the still
  included) are ASSUMED at about 0.2 m of packing a stage. The specified split K101, its return
  S11 to the pot, the mixer M102 and the typed reflux share Q7 go; the still's distillate S8 is
  the product, subcooled in a cooler of its own, E104 (Q9, the script's), to S10, because the
  model's condenser is a total condenser without subcooling (ADR 0061).
- **Result** (`cheme process stills`, per batch): 1527.7 kg of upper phase give 1459.9 kg of
  product, 99.43 wt% acetyl chloride, 0.573 wt% PCl3 (1293 ppm P) and 2 ppm acetic acid,
  recovering 98.19 % of the charge's acetyl chloride, 19.2 % of its PCl3 and 0.1 % of its acetic
  acid; 67.8 kg of residue (50 mol% acetyl chloride, 37.7 mol% PCl3, 7.7 mol% acetic acid,
  4.7 mol% phosphorous acid); the still from 324.33 to 335.89 K; 2.07 h of boil-up at 150 kW,
  310.3 kWh a batch, and 7.0 kWh of heat-up. Year averages: the reboiler Q3 54.88 kW (boil-up
  53.67, heat-up 1.21), the condenser Q4 53.67 kW, the product cooler Q9 2.17 kW. Before (core
  1.9.0, the split of D-008): 99.84 wt% with 6 % of the PCl3 over, the reboiler Q3 + Q7 + Q8
  56.40 kW, Q4 57.38 kW with the subcooling. The product meets the specification of at least
  99.0 wt% (D-002) with 0.43 points to spare; the yield falls from 92.40 to 92.11 % of theory,
  and the feeds for 2000 t/a by 0.1 % (the product carries more PCl3).
- **The model against the hand value and the source.** The model passes 19.2 % of the PCl3, the
  split 6 %. The split came from SRC-2 Example 1, a column fed continuously with another crude
  of 125 ppm P (0.055 wt% PCl3), 83 % of it taken overhead. Run on that crude as a batch (a
  scratch copy: 0.0554 wt% PCl3 in acetyl chloride, 10 stages, reflux 1, to 83 wt% distilled),
  the model passes 5.2 % of the PCl3 with 7.8 ppm P overhead, against the source's 6 % and
  9 ppm. So the model agrees with the source where the source applies. The difference is this
  crude, 2.86 wt% PCl3 (52 times SRC-2's), distilled to 96.5 % of the charge: the pot grows
  PCl3-rich as it boils down, and the last of the cut carries most of the PCl3. The split's 6 %
  was the error, not the model; its product purity, 99.84 wt%, was optimistic. Two caveats stay:
  an ideal liquid (L-10; SRC-2's close boiling and dew curves at low PCl3 would make the
  separation harder than Raoult's law) and Gilliland's correlation, which errs on the safe side
  (ADR 0061: never purer than a rigorous column).
- **Stages, reflux and end compared** (scratch copies at the charge's composition, 2026-11-06;
  the design row as committed):

| column and end | product wt% acetyl chloride | wt% PCl3 (ppm P) | recovery of acetyl chloride | of PCl3 | still's end | reboiler, year average |
|---|---|---|---|---|---|---|
| 10 stages, reflux 1, residue 50 mol% (design) | 99.43 | 0.573 (1293) | 98.19 % | 19.2 % | 335.9 K | 54.9 kW |
| 6 stages, reflux 1, residue 50 mol% | 98.79 | 1.213 (2736) | 98.56 % | 41.0 % | 336.5 K | about 55 kW |
| 10 stages, reflux 2, residue 50 mol% | 99.92 | 0.082 (185) | 97.91 % | 2.7 % | 335.6 K | 81.3 kW |
| 10 stages, reflux 1, purity end 99.0 wt% | 99.00 | 0.998 (2252) | 99.43 % | 34.0 % | 344.5 K | 55.7 kW |
| 10 stages, reflux 1, purity end 99.5 wt% | 99.50 | 0.500 (1128) | 97.63 % | 16.6 % | 334.1 K | 54.6 kW |
| 10 stages, constant distillate 0.999 mol ACCL to reflux 4, residue 50 mol% | 99.82 | 0.176 (397) | 97.96 % | 5.9 % | 335.6 K | 60.5 kW |
| 10 stages, constant distillate 0.999 mol ACCL to reflux 4, product cut to 99.8 wt%, an off-cut to 5 mol% in the residue (core's examples/process-batch-rectification) | 99.80 | 0.200 (451) | 99.40 % (off-cut 0.50 %) | 6.7 % (off-cut 11.8 %) | 344.8 K at the product's end, 353.4 K at the off-cut's | 63.5 kW |

  Kept: 10 stages at reflux 1, SRC-2's column and reflux; at 6 stages the product misses the
  specification. Rejected: a purity end at the specification (99.0 wt%): no margin for the ideal
  liquid, the still 9 K hotter and 20 K past the end of acetyl chloride's Antoine fit, a third
  of the PCl3 in the product; a purity end at 99.5 wt%: 0.6 points less recovery for 0.07 points
  of purity; reflux 2: 99.92 wt% at 1.5 times the reboiler's steam, the lever for a low-phosphorus
  grade if one is specified (still 185 ppm P: below 1 ppm needs SRC-2's chlorine, D-008). The
  core author's scratch run (ADR 0061: 99.43 wt% at 98.19 %) is reproduced.
- **Constant distillate compared** (review of #408; `reflux: constant_distillate`, `distillate:
  {key: ACCL, mole_fraction: 0.999}`, `maximum_ratio: 4`, the policy of core's
  examples/process-batch-rectification, whose charge is this upper phase; scratch copies
  2026-11-06, the last two rows of the table). The reflux rises from 0.80 to 4, at 4 from 94.6 %
  of the charge distilled. With this flowsheet's end (50 mol% acetyl chloride in the residue) the
  product is 99.82 wt% (397 ppm P) at 97.96 % recovery, 0.23 points less than at reflux 1, for
  2.29 h of boil-up instead of 2.07 h and a reboiler of 60.5 kW instead of 54.9 kW (+10 %). With
  the example's cuts (core's result reproduced: 99.8 wt% at 99.4 %) it recovers 1.2 points more
  into the product, for 2.40 h of boil-up and 63.5 kW (+16 %), and leaves an off-cut of 12.6 kg
  a batch (59 wt% acetyl chloride, 41 wt% PCl3) and 42.7 kg of residue at 5 mol% acetyl
  chloride. Kept: constant reflux 1. (1) The specification is 99.0 wt% (D-002); both policies
  meet it, neither reaches a low-phosphorus grade (397 and 451 ppm P against SRC-2's 1 ppm, which
  needs its chlorine, D-008), so the extra purity has no grade to serve and costs 10 to 16 % more
  steam. (2) SRC-2, the only source of this column, ran it at a constant 1:1; a reflux rising to
  4 on the head's composition is not sourced for it, and its control (an on-line analysis or the
  head temperature, to hold 0.999 mol fraction of acetyl chloride where, by SRC-2, its boiling
  and dew curves lie close to PCl3's) would be ASSUMED. (3) The example's higher recovery
  needs the off-cut: 41 wt% PCl3 and 59 wt% acetyl chloride with nowhere to go in this
  flowsheet, as no recycle to the next charge or to R-101 is modelled (D-008: the residue's
  recycle is a variant, ADR 0060's `tears:` not used); sent to the residue's disposal, the
  recovery is that of the 99.8 wt% cut, and R-101's feeds would fall by about 0.9 % (1472.4
  against 1459.9 kg of product a batch) while its 7.4 kg of acetyl chloride a batch are thrown away. (4) Its end at 5 mol% takes the still
  to 353.4 K, 29 K past the end of acetyl chloride's Antoine fit (324.2 K) and 6 K past PCl3's
  (347.3 K); D-007 ends at 50 mol% to stay within about 10 K, and the purity end at 99.0 wt%
  was rejected above for 20 K. Constant distillate with the residue end is the cheaper lever
  for a purer grade than reflux 2 (99.82 wt% at 60.5 kW against 99.92 wt% at 81.3 kW), the
  first option if a buyer's grade above 99.5 wt% is specified.
- **The charge's heat-up (`still.heat_up`, ADR 0063), adopted.** The model heats the charge from
  313.15 K to its 324.33 K bubble point, 1.2096 kW in Q3 (7.0 kWh a batch), against the script's
  Q8 1.2282 kW, which also held the one-stage residue's rise to 340.45 K (0.0174 kW). Q8 goes.
  Neither held the content's rise from its first to its last bubble point while it boils down:
  about 0.15 kW from the still's profile, a recorded exclusion (D-009).
- **The condenser on Q4 (`still.condenser_port`), adopted.** Q4 is the model's 53.67 kW,
  `calculated`; the product's subcooling, 2.17 kW, is Q9 on E104.
- **The vent's vapour and condenser (ADR 0062), tried and not adopted.** On a scratch copy
  (`vent: {components: [HCL], vapour: {components: [ACCL, ACOH, PCL3, H2O]}, condenser:
  {temperature: 268.15}}`, its duty on a new stream to brine): the vent past E-103 carries
  2.05e-5 kmol/h of acetyl chloride, 0.0006 % of the 3.29 kmol/h formed (ADR 0062's 0.0019 %
  divides by the reaction's extent), against the per-source 0.099 % and the flowsheet's upper
  bound 0.213 % (D-010); the condenser's duty is 0.0049 kW against Q6's 0.35 kW per source, and
  R-101's evaporative cooling 0.0053 kW against the 0.19 kW bound (D-009). The model is right for
  what it holds, the HCl R101 forms: it forms in the first minutes over the acetic acid (4.7 kPa),
  so its own share of the script's 0.17 kW from R-101's gas is about 0.15 kW too high. But the gas
  that carries most of the vapour is not R101's HCl: the head space the dose displaces, the
  nitrogen of the head space the rising vapour pressure expels, and the still's and the
  receivers' nitrogen, none of which core models (ADR 0062's follow-up). The head space's
  nitrogen was underestimated here too: from 1.33 m3 over the charge at 4.7 kPa of vapour to
  0.72 m3 at the end with the liquid's vapour at 0.491 of the pressure (the model's), about
  0.035 kmol a batch leaves, where the script counts the 0.0075 kmol the dose's volume displaces.
  The other 0.027 kmol a batch (0.0047 kmol/h) carry at most 0.0098 kmol/h of vapour (saturated
  over the upper phase): up to 0.09 kW more on E-103 and 0.0005 kmol/h more acetyl chloride past
  it (per source 0.114 % instead of 0.099 %, still inside the 0.213 % bound). The two errors of
  the script's Q6 point in opposite directions (-0.15 and up to +0.09 kW); Q6 stays 0.35 kW and
  the vent fraction its upper bound. Adopting the model would cut the vent's acetyl chloride by a
  factor of 160 (340 against the bound) and E-103's duty by 70 against the per-source estimate, and remove the vented
  acetyl chloride from the gas release at the MTSR (0.41 m3/h now, about zero with `vapour`;
  the vapour share of the gas there 0.51): less credible than the hand values. L-3 stays open.
- **Not used** (Core features used): `vent.henry` (no sourced Henry constant of HCl, L-6), a
  dose's `heat_of_solution` (none sourced, L-11), `batch.heat_up` (E101 warms the charge on its
  own stream from the tempered-water loop), `vessel.metal_heat_capacity` (no vessel mass sourced).
- **Unchanged:** R101 and its screening (dT_ad 21.4 K, accumulation 11.7 %, MTSR 315.8 K, the
  gas release 0.41 m3/h at the MTSR and 31.2 m3/h at 69 s), the cycle (5.781 h, R-101 the
  bottleneck), the batch size (1459.9 kg). DISTIL takes 3.57 h instead of 3.63 h; one batch
  8.85 h.
- **LCI** per kg of acetyl chloride: LP steam 0.2304 -> 0.2244 kWh (58.18 -> 56.66 kW: the
  reboiler at the model's reflux and the model's heat-up); cooling water 0.2384 -> 0.2322 kWh
  removed (60.19 -> 58.64 kW: Q4 without the subcooling, now Q9, and the smaller Q5);
  electricity 0.0207 -> 0.0206 kWh (P2 on the 2.07 h distillation); the still residue 0.047 ->
  0.046 kg; PCl3 0.630 -> 0.629 kg, acetic acid 0.827 -> 0.826 kg; brine 0.0014 kWh unchanged.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas, year-average duty Q2 | done in cheme, kinetics and conversion ASSUMED | D-005, D-009, D-011, core ADRs 0050, 0054, 0059 |
| MTSR over the batch, gas release at the MTSR and over the batch against the vent capacity | done in cheme (the largest over the batch with core's `vent_gas_rate`), vent capacity ASSUMED; boiling and water cases beyond it a design finding | D-011, D-014, core ADR 0058 |
| R-101's own evaporative cooling (not in Q2) | script bound, a recorded exclusion | D-009, D-014 |
| batch recipe, cycle time, basis check, R-101's vessel, jacket and warming time | done in cheme | D-003, core ADRs 0051, 0052, 0057 |
| phase split D101 | specified split in a script, calibrated to SRC-1 | D-006, L-2 |
| batch still ST101 with its column K-101 (10 stages, reflux ratio 1): product purity and recovery, residue, boil-up time, the reboiler Q3 (with the charge's heat-up) and the condenser Q4 | done in cheme (Diwekar's shortcut), stages and reflux and the ideal liquid ASSUMED | D-007, D-008, D-009, D-015, core ADRs 0055, 0059, 0061, 0063 |
| vent condenser load (per source) and the vent's acetyl chloride (an upper bound) | script estimate, written into Q6 and the vent fraction; core's vent vapour tried, not adopted | D-010, D-014, D-015, L-3 |
| scrubber hydrolysis | done in cheme (conversion step), heats in the script | D-010 |
| feeds for 2000 t/a, scrubber water, duties Q1, Q5, Q6 and the product cooler Q9, the still's stream temperatures | script | D-006, D-009, D-010, D-015 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.10.0)

Built on cheme-as-code 1.8.0, pinned to 1.9.0 since 2026-11-06 (D-014) and to 1.10.0 since
2026-11-06 (D-015).

- `reactor: semibatch` with `batch.dosing` and `batch.target` (ADR 0050) and `batch.vent` with two
  components and a `fraction` (ADR 0054): two outlets, the vent's peak rate per m3 (`process
  reactors`) and per batch (`process recipe`), the vented gas left out of the MTSR (`process
  reactor-hazards`); `hazard.mtt` on the step.
- `still:` (ADR 0055): Raoult's law with Antoine `vapour_pressure` and `heat_of_vaporization` in
  materials.yaml, `nonvolatile`, `boilup` in kW (the reboiler's, since 1.10.0), `end: residue`;
  `cheme process stills`.
- `process/recipe.yaml` (ADRs 0051, 0052, 0055, 0057): `dose`/`react` `from:` R101, `distil from:`
  ST101, `units: [E101, R101, D101]` and `units: [ST101, E102]` (until 1.10.0 with K101 and
  M102) for one vessel over several steps, R-101's `vessel` sizing and `jacket` check, a `heat` operation with
  `temperatures` timed from the jacket.
- a conversion step (`reactor: conversion`) for the scrubber's hydrolysis; `lca.yaml`
  `consumables` with `per_batch` (ADR 0053), `allocation: shares` (the mass shares, L-12).
- 1.9.0: the models' duties (ADR 0059): R101's Q2 by `energy_port: q` and ST101's net boil-up
  Q3 by `energy_port: steam`, both written `calculated` by `propagate --fill` (the typed reflux
  share Q7 and heat-up Q8 beside Q3 until 1.10.0; D-009, D-014); the semi-batch screening (ADR 0058):
  `mtsr_profile`, `per_reaction`, `gas_release` and `hazard.vent_capacity`, and
  `stirred_tank.vent_gas_rate` over the cooling profile for the largest release over the batch
  (D-011, D-014).
- 1.10.0 (D-015): the batch rectification `still.column` (ADR 0061: `stages: 10`, `reflux:
  constant`, `ratio: 1`; Diwekar's shortcut on Fenske-Underwood-Gilliland at each point of the
  still's path), which replaces the specified split K101, its return S11, the mixer M102 and the
  typed reflux share Q7; `still.condenser_port` (the condenser's duty on Q4, `calculated`); the
  charge's heat-up `still.heat_up` (ADR 0063), which replaces the typed Q8; `cheme process
  stills` with the cut's mass fractions, recoveries, the reflux and the duty's terms.
- Tried in 1.10.0 and not adopted (D-015): `batch.vent.vapour` and `batch.vent.condenser` (ADR
  0062), which carry the HCl's vapour but not that of the head space and nitrogen, so they would
  cut the vent's acetyl chloride from 0.213 % to 0.0006 % and E-103's load from 0.35 to 0.005 kW
  against the per-source estimate; the still's `end: purity` (ADR 0061), `reflux:
  constant_distillate` (with `distillate` and `maximum_ratio`) and the still's `cuts:` with a
  product and an off-cut (core's examples/process-batch-rectification), compared on scratch
  copies and not chosen.
- Not used in 1.10.0, no source or not applicable: `batch.vent.henry` (no sourced Henry constant
  of HCl in these liquids, L-6); a dose's `heat_of_solution` (none sourced for PCl3 in acetic
  acid, D-005, L-11); `batch.heat_up` (the acetic acid is warmed on its own step E101 by the
  tempered-water loop, Q1, while R101's duty goes to cooling water: one net model duty would mix
  the two); `vessel.metal_heat_capacity` (no mass of the enamelled R-101 or C-101 sourced; it
  would lengthen R-101's warming and the cycle, an input for basic engineering).
- Not used: `tears:` (ADR 0060; no recycle is modelled, the residue's recycle is a variant,
  D-008), `hazard.reactions` (the default counts the main reaction, D-014), the default MTT
  (still not the product's boiling point, L-5).
- Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
  dryer and the filter (no solids), the still's `feed:` (D-008).

## Core limits hit (each a candidate core issue)

- L-1 (resolved in core 1.10.0, ADR 0061, core#173): no batch rectification with reflux. One
  Rayleigh stage gives 97.3 wt% acetyl chloride with 2.6 wt% PCl3 (D-007); the column was a
  specified split in a script, and the still's `boilup` had to be entered as the net distillate
  rate (75 kW of a 150 kW reboiler at reflux ratio 1). Core 1.9.0 wrote that net latent heat on
  Q3 (ADR 0059) beside a typed reflux share Q7 and a script condenser Q4. Core 1.10.0's
  `still.column` integrates the column on the still and writes the reboiler and the condenser
  (D-015). What remains of it: a shortcut on an ideal liquid (L-10), no hold-up, no total-reflux
  start-up, and the column not sized.
- L-2: no liquid-liquid split for a reacting batch. A semi-batch is one homogeneous liquid, while
  the reaction mass forms two phases as it reacts, and core's NRTL extraction needs binary pairs
  that no open source gives for acetyl chloride, acetic acid and phosphorous acid. The settling
  D101 is a specified split in a script, calibrated to the source (D-006). Core could take a
  specified phase split (component fractions per outlet) as a separator that propagate solves,
  which would remove the script for it.
- L-3 (ADR 0054; still open in core 1.10.0, ADR 0062): the vent carries only components formed by
  the reactions, at a stated fraction, not the vapour of the liquid from its VLE, and there is no partial condenser on the
  vent. At 313 K acetyl chloride's vapour pressure (69 kPa) is two thirds of the pressure. The vent
  condenser's load, the evaporative cooling of R-101 and the acetyl chloride that passes E-103 are
  script estimates, and the latter is written by hand as the vent `fraction`. The balance-output
  contract does not check a step parameter, so a drift between the script's 0.002131 and the
  flowsheet's 0.00213 is caught only by this folder's test. Still so in core 1.9.0: the
  semi-batch's model duty (ADR 0059) has no latent heat of a vapour the vent gas carries, so
  R-101's own evaporative cooling is a script bound (at most 0.19 kW, 7 % of Q2) and a recorded
  exclusion, which Q6 counts again (D-009, D-014); core's gas release counts the vent's components only, not the
  liquid's vapour in the vent line, nor what boils above the MTT (D-014). Core 1.10.0 adds the
  vent's vapour and a partial vent condenser (ADR 0062), but the gas that carries the vapour is
  then only the HCl R101 forms (0.008 kmol/h, in the first minutes over the acetic acid); the
  head space the dose displaces and the vapour pressure's rise expels, and the still's and the
  receivers' nitrogen, carry most of it here and are not modelled. The features were not
  adopted (D-015); a head space and inert sweep in the vent is the core follow-up (ADR 0062).
- L-4 (ADR 0055; the heat-up resolved in core 1.10.0, ADR 0063): the still extrapolates an
  Antoine fit beyond its range (acetyl chloride's ends at 324.2 K, the still reaches 335.89 K
  with the column, 340.45 K with one stage; reported as a note only). Until core 1.10.0 it had no
  heat-up of its charge (the script's Q8); `still.heat_up` now holds it, though not the content's
  rise from its first to its last bubble point (about 0.15 kW, D-009). It does not size its
  vessel, jacket, column or condenser: C-101 and K-101 are sized by hand.
- L-5: the default MTT is the lowest boiling point of the charge and the doses; it ignores the
  product formed in the liquid. Here the product, acetyl chloride (324.15 K), boils below both the
  charge (acetic acid, 391 K) and the dose (PCl3, 349 K), so the default would be 25 K too high;
  `hazard.mtt` was set by hand (as benzoyl-chloride-1's L-5). Still so in core 1.9.0: ADR 0058
  leaves vent and dissolved gases out of the default, but the products are no candidates (its
  known limitations); the default stays PCl3's 349.15 K (D-014).
- L-6 (ADR 0054; still open in core 1.10.0): no solubility of the vented gas. Core 1.10.0's
  `vent.henry` (ADR 0062) needs a Henry constant of HCl in these liquids, and none was found
  (searched 2026-11-05/06); it would also not degas the HCl the source's lower phase holds. The source's lower phase holds 6 wt% HCl (38.6
  kg a batch at this scale), the model none (all HCl formed is vented); the HCl dissolved in the
  product and the lights cut the still would take off are not represented. The model cannot carry
  dissolved HCl into the still anyway: HCl is supercritical at the still's temperatures, so it has
  no Antoine there.
- L-7 (as n-bromosuccinimide-1's L-6): core propagates from the feeds and cannot solve them for a
  product rate, and the batch size and the cycle depend on each other through the jacket's warming
  time; both were iterated by hand (propagate, the script, the recipe, again).
- L-8 (as p-toluenesulfonyl-chloride-1's L-3): a semi-batch is isothermal at one temperature. The
  source doses below 40 C and holds at 40-50 C; the model runs both at 313.15 K.
- L-9 (resolved in core 1.9.0, ADR 0059; as benzoyl-chloride-1's L-7): an isothermal semi-batch
  reported its peak cooling duty and the heat released, but no year-average duty for its energy
  stream, so Q2 came from the script. Core 1.9.0 writes it (2.67099 kW), and the still's net
  boil-up Q3 likewise (27.5838 kW). Its comparison with the typed values showed that the hand Q2
  had deducted a vapour that does not leave the reacting mass (D-014).
- L-10 (as benzoyl-chloride-1's L-9): an ideal liquid only; the still's basis is "not sourced".
  It matters more with the column (D-015): SRC-2 says the boiling and dew curves of acetyl
  chloride and PCl3 lie close at low PCl3, which an ideal liquid (PCl3 at about 0.4 of acetyl
  chloride's vapour pressure) does not show, so the model may separate the last PCl3 better
  than the plant; Gilliland's correlation errs the other way (ADR 0061).
- L-11 (open; core 1.10.0 adds the means, not the data): a semi-batch has one `heat_of_reaction`
  per reaction; core 1.10.0's `dosing.heat_of_solution` (ADR 0063) takes a dose's heat of
  mixing, but none is sourced for PCl3 in acetic acid, and the heat of the phase separating has
  no term (as p-toluenesulfonyl-chloride-1's L-2); here even the sign of the reaction heat
  depends on the state of the phosphorous acid (D-005).
- L-12: `cheme assess lca --write` writes a study's `allocation: {method: mass}` into the dataset
  without its `method` (mass is the default), and the library's `build_lci.py --strict` then
  warns that the study's 'mass' differs from the dataset's None and fails. The fix is open as
  process-library#322 (a missing method read as mass); until then the mass allocation is given as
  its shares (D-012). A core-side fix would write the method always.

## Open inputs
Kinetics, heat and sign of the reaction by reaction calorimetry with off-gas measurement; TD24 of
the reaction mass, the lower phase and the residue; the conversion and the phase split at plant
scale; the HCl balance (SRC-1's dissolved HCl); VLE of acetyl chloride with PCl3 and acetic acid
(it sets the PCl3 the column passes, D-015, L-10); the column's packed height and HETP, its
reflux and the PCl3 it passes, measured; the product's phosphorus and HCl specification (the
assay is set at 99.0 wt%, D-002); the chlorine treatment (SRC-2) or a higher reflux if a
low-phosphorus grade is wanted; the masses of R-101 and C-101 for their metal's heat; recycling the residue's
PCl3; the lower phase's stripping (SRC-1, Example 2); prices for the allocation; a TEA
(`operation.batch: {recipe: true}`); R-101's relief device and blocked-vent case, the vent's
capacity against the boiling and water cases, E-103's design duty for the k/100 boil-off, and
the vent line's hydraulics with the liquid's vapour (D-014).
