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

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; NIST WebBook, PubChem and Wikipedia pages; the
open data tables packaged in the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | CS 272 248 B2, J. Pelyva et al. (Nitrokemia Ipartelepek), published 1991-01-15: simultaneous preparation of N-phosphonomethyliminodiacetic acid and C1-4 carboxylic acid chlorides, https://patents.google.com/patent/CS272248B2/en | Example 1: 180 g (3 mol) acetic acid, 137.3 g (1.0 mol) PCl3 added below 40 C, then 30 min at 40-50 C; the upper acetyl chloride layer separated for use (no yield, no purity); the lower phase 96 g, phosphorous acid with about 6 wt% HCl, 2 wt% acetyl chloride and 10 wt% acetic acid, diluted and used in a phosphonomethylation. Examples 2 and 3: the lower phase stripped, or re-treated with PCl3. Claim 1: PCl3 to acid 1:2.5 to 1:3.5 at 0-20 C. Description: lower phase typically 80-98 % phosphorous acid, 0-2 % acid, 1-5 % acyl chloride; phases separated by settling | read; patent, facts only | D-001, D-004, D-005, D-006 |
| SRC-2 | US 4 209 460 A, A. Ohorodnik, E. Auer, K. Gehrmann (Hoechst AG), 1980: Production of pure acetyl chloride, https://patents.google.com/patent/US4209460A/en | description: phosphorus compounds in acetyl chloride come from PCl3; acetyl chloride (bp 50.9 C) and PCl3 (75.9 C) are hard to separate by distillation at low PCl3 because their boiling and dew curves lie close; 1-20 L of chlorine per L turns the PCl3 into PCl5, which stays in the bottoms. Example 1 (no chlorine): a 2 m column of 50 mm packed with 8 mm saddles, reflux 1:1, 2.8 L/h of a crude with 125 ppm P, 2.32 L/h overhead with 9 ppm P. Examples 2 and 3: with 11-12.5 L chlorine per L, above 99 % acetyl chloride and below 1 ppm P. The crude came from another process (a phospholane synthesis) | read; patent, facts only | D-008 |
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
Modelled product (S10): 99.84 wt% acetyl chloride, 0.162 wt% PCl3 (about 366 ppm P) and 8 ppm
acetic acid by mass. **No open source states a purity or a yield for this route**: the 99.84 wt%
is the model's (D-007, D-008), with no dissolved HCl (L-6), and an ASSUMED upper bound. SRC-2's
column without chlorine reached 99.32 % from another crude. The product specification is an
open input.
Reason: no open market or plant figure was used; a few thousand tonnes a year is a plausible
size for a dedicated batch train of a fine acid chloride. The LCI is per kg and does not depend
on the scale; the batch size does (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 1459.91 kg of acetyl chloride (stream S10); the recipe
(`process/recipe.yaml`) has two unit procedures:
- REACT on R-101, one vessel over E101, R101 and D101 (`units`, core ADR 0057): nitrogen purge
  0.25 h, charge the acetic acid 0.5 h, warm 298 -> 313 K 0.54 h (from the jacket), dose the
  PCl3 2 h and post-reaction 0.49 h to 0.95 conversion of the PCl3 (both from R101's model),
  settle 1 h, drain the lower phase 0.5 h, transfer the upper phase 0.5 h: 5.781 h;
- DISTIL on C-101 with its column K-101 over ST101, K101, M102 and E102: receive 0.5 h, distil
  2.13 h (from ST101's boil-up), cool the residue 0.5 h, drain 0.5 h: 3.63 h.
R-101 is the bottleneck: cycle 5.781 h, 1370.0 batches in 7920 h; one batch takes 8.91 h from
the purge to the residue's drain. The flowsheet's flows are the recipe's year averages: 1459.91
kg x 1369.95 / 7920 h = 252.52 kg/h of S10 (no `cheme.recipe-basis` finding). The batch size
was found by fixed-point iteration, since the warming time depends on the vessel and so on the
batch (L-7).
Dosing time: the source doses dropwise in a flask; 2 h is ASSUMED for the plant (the jacket would
allow less, D-005, but a slower dose keeps the accumulation low, D-011).
Vessels (fill 0.8, H/D 1.2, enamelled, ASSUMED): R-101 2.5 m3 (the R10 preferred size, 71 % full
with 1.78 m3 at the end of the dosing, D 1.38 m), as the recipe sizes it from R101's model (core
ADR 0052). Its jacket (U 300 W/(m2 K), 4.90 m2 wetted at the charge) removes 13.37 kW against the
model's peak 9.85 kW, on cooling water entered at its log-mean equivalent: water in at 298.15 K
and out at 308.15 K against the mass at 313.15 K gives (15 - 5) / ln 3 = 9.10 K, so 304.05 K, not
the supply temperature (core takes the coolant as one temperature). The warming runs on a
tempered-water loop at 322/318 K (mean 320.15 K), below acetyl chloride's 324.15 K boiling point
(R101's MTT, D-011); the jacket is switched to cooling water before the dosing starts. C-101 and
K-101 are sized by hand (core's still has no vessel, L-4): about 2.5 m3 for 1.53 t (1.39 m3) of
upper phase.
Reason: core ADR 0051 puts the batch basis in one place; the dosing, post-reaction, warming and
distillation times come from the models, so a change of the rate law, the jacket or the boil-up
changes the cycle. The settling, draining and transfer times are ASSUMED concept values (SRC-1
gives none).

## D-004 Feeds and charge (2026-11-06)
Decision: 3 mol of acetic acid per mol of PCl3, SRC-1 Example 1's ratio (also the prior art of
SRC-3), with no excess of either. Acetic acid from acetic-acid-1, its glacial acid with 691 ppm
of water by mass (its product S21; its 50 ppm of propionic acid counted as acetic acid, which
would give 50 ppm of propionyl chloride); PCl3 100 % (its POCl3 and dissolved chlorine not
modelled). Per batch: 1207.6 kg of acetic acid (with 0.83 kg of water) and 919.9 kg of PCl3. The
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
acetyl chloride formed leaves with it, the vapour that passes the vent condenser (D-010).
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

## D-006 Phase split D101 and the balance method (2026-11-06)
Decision: the two phases settle in R-101 (D101, one more step of the REACT unit procedure). The
split is specified in scripts/balance.py, calibrated to SRC-1's lower phase. To the lower phase S7
go 99.5 % of the phosphorous acid (0.5 % entrained in the upper phase, ASSUMED), 95 % of the
acetic acid (ASSUMED: the acid prefers the polar phase), 5 % of the PCl3 (ASSUMED) and 0.8 % of
the acetyl chloride (the source's 2 wt% of 96 g, 1.92 g of the 235.5 g formed per mol of PCl3).
Result per batch: 593.4 kg of lower phase (87.50 wt% H3PO3, 10.11 wt% acetic acid, 2.01 wt%
acetyl chloride, 0.39 wt% PCl3), 88.6 g per mol of PCl3 against the source's 96 g, of which 5.8
g is HCl (90.2 g HCl-free); 1529.2 kg of upper phase (96.77 wt% acetyl chloride, 2.86 wt% PCl3).
The source's 6 wt% HCl in its lower phase is not reproduced (L-6, D-010).
Balance method: cheme propagates the semi-batch R101 with both outlets, the still ST101 (D-007),
the pass-through steps E101, E102, E103, the mixer M102 and the scrubber A101 (a conversion
step). scripts/balance.py gives what core has no model for (library ADR 0027). These are the feeds
S1 and S3 for 2000 t/a (linear in the feeds; the script scales the PCl3 by the ratio of the target
to S10), the phase split D101, the column K101's split (D-008) and the scrubber water S15. It also
gives the temperatures of the still's streams (bubble points by Raoult's law with the materials'
Antoine constants, as the still computes them), of the mixed residue S12 and of the adiabatic
scrubber's liquor S16, and the duties Q1 to Q6 (D-009). It follows the balance-output contract
(`scripts/check_balance_scripts.py`). The batch size and the feeds were converged together:
propagate, the script, the recipe's cycle, and again (L-7).
Reason: core has no liquid-liquid model that applies. Its NRTL extraction needs binary pairs,
and none is sourced for acetyl chloride, acetic acid and phosphorous acid. A semi-batch is one
liquid (L-2). The source's composition is the only data, so the split is calibrated to it rather
than predicted.
Rejected: the lower phase stripped of its volatiles (SRC-1, Example 2) or re-treated with PCl3
(Example 3) to recover the acetic acid and the acetyl chloride: variants; they would raise the
yield by up to 0.76 % (the acetyl chloride of S7) and give back about 60 kg of acetic acid a batch.

## D-007 Batch still ST101: one Rayleigh stage at atmospheric pressure (2026-11-06)
Decision: ST101 is core's batch still (`still:`, core ADR 0055): the upper phase S6 boiled at
101.325 kPa(a), Raoult's law with the NIST Antoine constants of acetyl chloride, PCl3, acetic acid
and water (SRC-5), phosphorous acid non-volatile, until acetyl chloride is 50 mol% of the residue
(`end: residue`, ASSUMED). Boil-up 75 kW net (the vapour that leaves as distillate: a 150 kW
reboiler at the column's reflux ratio 1, D-008), so the distillation takes 2.13 h. Result
(`cheme process stills`): 1529.2 kg of upper phase a batch give 1512.9 kg of distillate S8 and
16.3 kg of residue S9 (50 mol% acetyl chloride, 15.8 mol% PCl3, 17.6 mol% acetic acid, 16.6 mol%
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
still extrapolates it by up to 16 K at the end (`cheme.process-still-note`, info; the 50 mol%
end keeps it short of the pure PCl3 end at 349 K); the charge's heat-up from 313 to 324 K and the
residue's from 324 to 340 K are in the script's Q3 (D-009); dissolved HCl, which would leave
first as a lights cut (L-6).

## D-008 Column K101 on the still: rectification as a specified split; the PCl3 carry-over (2026-11-06; revisit with core#173)
Decision: the column on C-101 (about 10 theoretical stages, reflux ratio 1, ASSUMED after SRC-2's
2 m packed column at 1:1) is a specified split of ST101's distillate S8 in scripts/balance.py. To
the product S10 go 99 % of the acetyl chloride, 6 % of the PCl3 and 1 % of the acetic acid. The
rest, S11, is the column's hold-up and last cut returned to the pot, and leaves with the residue
(M102, cooled in E102, S13). The PCl3 share comes from SRC-2, Example 1: the column without
chlorine took 9 ppm P overhead from a 125 ppm feed with 83 % of the volume overhead, so 0.83 x 9 /
125 = 6 % of the phosphorus. That crude came from another process; the share is ASSUMED to carry
over to this one. Result: 252.53 kg/h of 99.84 wt% acetyl chloride with 0.162 wt% PCl3 (366 ppm
P), 9.17 kg/h back to the pot (70 wt% PCl3); the residue S13 is 11.99 kg/h (47 g per kg of product,
60 wt% PCl3) to hazardous-waste incineration, 4.5 % of the PCl3 fed. Overall yield **92.40 % of
theory** on the acetic acid and on the PCl3 (1 mol acetyl chloride per mol of acetic acid). This is
a model result: no source states one. It is an ASSUMED upper bound, since every loss not modelled
only lowers it: the acylation of H3PO3 (SRC-3), the moisture of the plant, the breathing of the
tanks, the HCl that would stay dissolved. Losses of the theory: 5.23 % unconverted (5 % of the PCl3
by the calibration, D-005; 0.23 % hydrolysed by the water), 0.76 % in the lower phase, 0.48 % in
the still residue, 0.93 % returned by the column, 0.20 % past the vent condenser.
Reason: core 1.8.0's still is one stage with no reflux (ADR 0055) and gives 97.3 wt% (D-007).
Core's Fenske-Underwood-Gilliland shortcut is for continuous columns, and a batch column at
constant reflux is the follow-up core#173, so the column's work is a stated split (as in
benzoyl-chloride-1). SRC-2 says why the PCl3 is the hard part: at low PCl3 contents the boiling
and dew curves of the pair lie close, and its column without chlorine removed 94 % of the P, not
enough for a low-phosphorus grade.
Option, not modelled: SRC-2's chlorine treatment of the crude (1-20 L of Cl2 per L, 10-15
preferred) before the distillation turns PCl3 into PCl5, which stays in the bottoms; it reached
below 1 ppm P. Here the crude holds 2.86 wt% PCl3 (about 6450 ppm P, 50 times SRC-2's 125 ppm),
so the chlorine need would have to be measured. PCl5 in a pot with acetic acid would also give acetyl
chloride, POCl3 and HCl. A variant (chlorine from chlor-alkali-1).
Rejected: the still alone as the product's purification (it would present a one-stage distillate
as the product at 97.3 wt%); a cut sequence of the one-stage still (`cuts:`): a first cut is no
purer in PCl3, which is the heavier component; recycling the residue and the column's return
(70 wt% PCl3) to the next batch's R-101: the obvious improvement, it would recover most of the
4.5 % of the PCl3, but it is a tear stream across batches (a variant).

## D-009 Utilities and heat (2026-11-06)
Decision (scripts/balance.py, year averages, ASSUMED unless sourced):
- Q1 1.79 kW of LP steam (via R-101's tempered-water loop): the acetic acid S1 warmed from 298 to
  313 K (123.3 kJ/(kmol K), SRC-4); about 19.3 kW over the 0.54 h of warming.
- Q2 1.27 kW from R-101 to cooling water: the heat of ACCL and HYD (3.25 kW), less the PCl3 dose
  warmed from 298 to 313 K (0.58 kW), less the acetyl chloride, PCl3 and acetic acid the vent gas
  evaporates at 313 K (1.20 kW), less the cold condensate E-103 returns, rewarmed (0.20 kW). The
  model's peak is 9.85 kW during the dosing (D-003). With the liquid-H3PO3 heat of reaction (+2.3
  kJ/mol, D-005) Q2 would be about -2.6 kW: R-101 would need heat instead, which its tempered-water
  loop provides; the sign is an open input.
- Q3 56.40 kW of LP steam 350 kPa(a) (412 K) to the still: the latent heat of the distillate S8
  times (1 + the reflux ratio 1), plus the charge heated from 313.15 to its 324.33 K bubble point
  and the residue on to 340.45 K; 150 kW while distilling.
- Q4 57.38 kW to cooling water: the column's condenser at the same reflux, and the product
  subcooled from 324.33 to 303.15 K.
- Q5 0.14 kW to cooling water: the residue S12 cooled from 340.45 to 303.15 K in the still before
  it is drained.
- Q6 1.28 kW to brine (258/263 K): the vent condenser E-103 (D-010).
- Electricity 5.2 kW: R-101's agitator 4 kW for 3.54 h of each 5.78 h cycle (2.5 kW, P1); the
  still's agitator and reflux pump (1.2 kW, P2); the scrubber's pump and fan (1.5 kW, P3).
Every energy flow of the batch is in the flowsheet and so in the LCI per kg (library ADR 0035).
Recorded exclusions, each with its estimate (ASSUMED orders, insulated surfaces at about 1
W/(m2 K)): the heat losses of R-101 (at 313 K, 15 K above the ambient: about 0.1 kW), of C-101 and
K-101 (at 324-340 K: about 0.4 kW while hot, below 1 % of Q3) and of the tempered-water loop; the
tracing of the crude phosphorous acid tank T-102 (at 313 K: about 0.1 kW); the scrubber's water
evaporated into the nitrogen (about 0.003 kmol/h, 0.04 kW, which cools the bleed a little); the
heats of mixing of PCl3 into acetic acid and of the phase separation, unknown: the span of the
heat of reaction (12.8 kJ/mol, D-005) bounds them at about 3.9 kW (L-11). Each mixed stream's temperature follows from its inlets: S12 from S9
and S11 (both at the pot's end temperature, 340.45 K), S16 from the adiabatic scrubber (D-010);
the upper and lower phases leave at R101's 313.15 K after the 1 h settle on the jacket.

## D-010 Vent, vent condenser and HCl scrubber (2026-11-06)
Decision: R-101's vent (S5) and the vents of C-101, K-101 and the tanks go through E-103, a vent
condenser on brine (gas out at 268.15 K, 10 K above the 258 K brine), to A-101, a packed water
scrubber with a bleed of 1 wt% HCl.
- The vapour load: the HCl (0.0080 kmol/h) and the batch's nitrogen (8 Nm3 a batch, 0.0617
  kmol/h; all of it taken through E-103) leave saturated with the upper phase's vapour at 313 K
  (Raoult: 67 kPa of acetyl chloride, 0.5 kPa of PCl3). That is an upper bound for the still's
  vent, which leaves its condenser cooler. E-103 condenses the acetyl chloride down to its 9.3 kPa
  at 268 K and all the acetic acid, and returns them to R-101. What passes, 0.0070 kmol/h (0.55
  kg/h, 0.213 % of the acetyl chloride formed), is R101's vent fraction of ACCL (D-005). The script
  prints the estimate, and the fraction is written by hand into the flowsheet (L-3). The PCl3 (3.6
  kPa at 268 K, above its partial pressure) passes E-103, 0.0010 kmol/h (0.14 kg/h). It is
  hydrolysed in the scrubber, which is not in the balance (its 0.11 kg/h of HCl would raise the
  bleed from 1.0 to about 1.2 wt%; recorded in lca.yaml's emission_exclusions).
- The scrubber A101 is a conversion step: the acetyl chloride vapour hydrolysed (AHYD, -48 kJ/mol
  with the chloride as a vapour, SRC-4), all HCl absorbed. 53.95 kg/h of process water make a
  bleed S16 of 54.79 kg/h (1.0 wt% HCl, 0.77 wt% acetic acid), 0.217 kg per kg of product, to
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

## D-011 Thermal screening, the rate-constant sensitivity and the release cases (2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054): adiabatic temperature rise of the
whole batch 21.4 K (with the exothermic bound of D-005); largest accumulation of the dosed PCl3
11.7 %, at the end of the dosing; MTSR at that moment 315.8 K, against an MTT of 324.15 K
(`hazard.mtt`: the normal boiling point of acetyl chloride, the product, which is most of the
liquid once the PCl3 is dosed; core's default, the lowest boiling point of the charge and the
dose, would be PCl3's 349.15 K, 25 K too high: L-5). The vented HCl and acetyl chloride add
nothing to the MTSR; with the vent blocked they pressurise the vessel, which the screening does
not assess (core note: a peak of 0.19 mmol/(s m3)).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
With MTSR below MTT the class is 1 or 2 if the TD24 lies above the MTSR (1 above the MTT, 2
between), and 5 if it lies below (TD24 < 315.8 K): core's `criticality()` and Stoessel test the
TD24 against the MTSR first (SRC-8). It needs the TD24.
Sensitivity (a scratch copy of the folder, only A divided, everything else as designed;
`cheme process propagate --fill`, `reactor-hazards`, `reactors`, `recipe`; not committed):

| k at 313 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 324.15 K | post-reaction to 0.95 | cycle | class without TD24 |
|---|---|---|---|---|---|---|
| 5.5e-4 (design) | 11.7 % | 315.8 K | 8.4 K below | 0.49 h | 5.78 h | 1, 2 or 5 |
| k/10 | 35.9 % | 321.1 K | 3.0 K below | 7.48 h | 12.77 h | 1, 2 or 5 |
| k/100 | 80.2 % | 330.5 K | 6.4 K above | 81.6 h | 86.93 h | 3, 4 or 5 |

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
with a blocked vent.
Release cases (not assessed, reasoning only; for the HAZOP of the next stage):
- (a) Water ingress into R-101. Sources: a leak of the cooling-water jacket (its supply pressure is
  above the vessel's, so it runs inward), of the tempered-water loop, or scrubber water sucked
  back through the vent line (HCl absorption pulls a vacuum when the gas flow stops). PCl3 and
  acetyl chloride hydrolyse violently (SRC-6). 1 kg of water gives 55.5 mol of HCl, about 1.43 m3
  at 313 K and 101 kPa, more than a whole batch's normal HCl (1.69 kg, 0.046 kmol), and 1.2 MJ
  with PCl3. Options to assess: anti-suck-back protection on the vent line (a nitrogen-padded
  seal pot, a vacuum breaker on nitrogen); jacket-leak detection (conductivity of the loop) or a
  non-aqueous heat-transfer fluid on R-101; the vent and the scrubber sized for the water case.
- (b) Loss of the scrubber water while R-101 doses: up to 30.8 m3/h of HCl at the start of the
  dosing, and the acetyl chloride vapour, to air. The PCl3 dosing should be interlocked on A-101's
  water flow and on HCl breakthrough at its outlet. Stopping the dosing stops the model's HCl,
  which comes with the water at the start. SRC-1's dissolved HCl (D-010) would keep degassing.
- (c) Loss of brine to E-103: the acetyl chloride the gas carries at 313 K, about 0.143 kmol/h as
  a year average and more while the nitrogen purges, goes to the scrubber. There it hydrolyses
  to HCl and acetic acid, 10 times the normal HCl and about 5.0 kW of heat. Brine flow and the gas
  outlet temperature of E-103 should be interlocked with the dosing.
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
Per kg of acetyl chloride, unallocated: acetic acid 0.827 kg (stoichiometric 0.765), PCl3 0.630 kg
(0.583), process water 0.214 kg, nitrogen 6.85 g, electricity 0.021 kWh, LP steam 0.230 kWh,
cooling water 0.233 kWh removed, brine 0.0051 kWh removed; out: crude phosphorous acid 0.406 kg,
still residue 0.047 kg, scrubber bleed 0.217 kg. `lca/inventory.csv` lists them allocated (x
0.711). Not counted: the scrubber's tail gas and the tanks' breathing (emission_exclusions).

## D-013 Dedicated train (2026-11-06)
Decision: R-101, C-101, K-101, E-103 and A-101 make only acetyl chloride, batch after batch: 1370
batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms. Acetyl chloride is also made continuously from acetic
anhydride and HCl (D-001); this entry is the batch case.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas | done in cheme, kinetics and conversion ASSUMED | D-005, D-011, core ADRs 0050, 0054 |
| batch recipe, cycle time, basis check, R-101's vessel, jacket and warming time | done in cheme | D-003, core ADRs 0051, 0052, 0057 |
| phase split D101 | specified split in a script, calibrated to SRC-1 | D-006, L-2 |
| batch still ST101 (one stage): distillate, residue, boil-up time, net latent heat | done in cheme, ideal liquid ASSUMED | D-007, core ADR 0055 |
| column K-101 (rectification with reflux) | specified split in a script | D-008, core#173 |
| vent condenser load and the vent's acetyl chloride | script estimate, written into the vent fraction | D-010, L-3 |
| scrubber hydrolysis | done in cheme (conversion step), heats in the script | D-010 |
| feeds for 2000 t/a, scrubber water, duties Q1 to Q6, mixed temperatures | script | D-006, D-009, D-010 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (cheme-as-code 1.8.0)

- `reactor: semibatch` with `batch.dosing` and `batch.target` (ADR 0050) and `batch.vent` with two
  components and a `fraction` (ADR 0054): two outlets, the vent's peak rate per m3 (`process
  reactors`) and per batch (`process recipe`), the vented gas left out of the MTSR (`process
  reactor-hazards`); `hazard.mtt` on the step.
- `still:` (ADR 0055): Raoult's law with Antoine `vapour_pressure` and `heat_of_vaporization` in
  materials.yaml, `nonvolatile`, `boilup` in kW, `end: residue`; `cheme process stills`.
- `process/recipe.yaml` (ADRs 0051, 0052, 0055, 0057): `dose`/`react` `from:` R101, `distil from:`
  ST101, `units: [E101, R101, D101]` and `units: [ST101, K101, M102, E102]` for one vessel over
  several steps, R-101's `vessel` sizing and `jacket` check, a `heat` operation with
  `temperatures` timed from the jacket.
- a conversion step (`reactor: conversion`) for the scrubber's hydrolysis; `lca.yaml`
  `consumables` with `per_batch` (ADR 0053), `allocation: shares` (the mass shares, L-12).
- Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
  dryer and the filter (no solids), the still's `cuts:` and `feed:` (D-008).

## Core limits hit (each a candidate core issue)

- L-1 (core#173): no batch rectification with reflux. One Rayleigh stage gives 97.3 wt% acetyl
  chloride with 2.6 wt% PCl3 (D-007); the column is a specified split in a script, and the still's
  `boilup` had to be entered as the net distillate rate (75 kW of a 150 kW reboiler at reflux ratio
  1), so `cheme process stills` reports the net latent heat, not the reboiler's duty.
- L-2: no liquid-liquid split for a reacting batch. A semi-batch is one homogeneous liquid, while
  the reaction mass forms two phases as it reacts, and core's NRTL extraction needs binary pairs
  that no open source gives for acetyl chloride, acetic acid and phosphorous acid. The settling
  D101 is a specified split in a script, calibrated to the source (D-006). Core could take a
  specified phase split (component fractions per outlet) as a separator that propagate solves,
  which would remove the script for it.
- L-3 (ADR 0054): the vent carries only components formed by the reactions, at a stated
  fraction, not the vapour of the liquid from its VLE, and there is no partial condenser on the
  vent. At 313 K acetyl chloride's vapour pressure (69 kPa) is two thirds of the pressure. The vent
  condenser's load, the evaporative cooling of R-101 and the acetyl chloride that passes E-103 are
  script estimates, and the latter is written by hand as the vent `fraction`. The balance-output
  contract does not check a step parameter, so a drift between the script's 0.002131 and the
  flowsheet's 0.00213 is caught only by this folder's test.
- L-4 (ADR 0055): the still extrapolates an Antoine fit beyond its range (acetyl chloride's ends at
  324.2 K, the still reaches 340.45 K; reported as a note only). It has no heat-up or sensible heat
  of its charge and residue (in the script's Q3), and it does not size its vessel, jacket or
  condenser: C-101 and K-101 are sized by hand.
- L-5: the default MTT is the lowest boiling point of the charge and the doses; it ignores the
  product formed in the liquid. Here the product, acetyl chloride (324.15 K), boils below both the
  charge (acetic acid, 391 K) and the dose (PCl3, 349 K), so the default would be 25 K too high;
  `hazard.mtt` was set by hand (as benzoyl-chloride-1's L-5).
- L-6 (ADR 0054): no solubility of the vented gas. The source's lower phase holds 6 wt% HCl (38.6
  kg a batch at this scale), the model none (all HCl formed is vented); the HCl dissolved in the
  product and the lights cut the still would take off are not represented. The model cannot carry
  dissolved HCl into the still anyway: HCl is supercritical at the still's temperatures, so it has
  no Antoine there.
- L-7 (as n-bromosuccinimide-1's L-6): core propagates from the feeds and cannot solve them for a
  product rate, and the batch size and the cycle depend on each other through the jacket's warming
  time; both were iterated by hand (propagate, the script, the recipe, again).
- L-8 (as p-toluenesulfonyl-chloride-1's L-3): a semi-batch is isothermal at one temperature. The
  source doses below 40 C and holds at 40-50 C; the model runs both at 313.15 K.
- L-9 (as benzoyl-chloride-1's L-7): an isothermal semi-batch reports its peak cooling duty and the
  heat released, but no year-average duty for its energy stream; Q2 comes from the script.
- L-10 (as benzoyl-chloride-1's L-9): an ideal liquid only; the still's basis is "not sourced".
- L-11: a semi-batch has one `heat_of_reaction` per reaction and no heat of mixing of a dosed
  liquid or of a phase separating (as p-toluenesulfonyl-chloride-1's L-2); here even the sign of
  the reaction heat depends on the state of the phosphorous acid (D-005).
- L-12: `cheme assess lca --write` writes a study's `allocation: {method: mass}` into the dataset
  without its `method` (mass is the default), and the library's `build_lci.py --strict` then
  warns that the study's 'mass' differs from the dataset's None and fails. The fix is open as
  process-library#322 (a missing method read as mass); until then the mass allocation is given as
  its shares (D-012). A core-side fix would write the method always.

## Open inputs
Kinetics, heat and sign of the reaction by reaction calorimetry with off-gas measurement; TD24 of
the reaction mass, the lower phase and the residue; the conversion and the phase split at plant
scale; the HCl balance (SRC-1's dissolved HCl); VLE of acetyl chloride with PCl3 and acetic acid;
the column's stages, reflux and the PCl3 it passes; the product specification (assay, P content,
HCl); the chlorine treatment (SRC-2) if a low-phosphorus grade is wanted; recycling the residue's
PCl3; the lower phase's stripping (SRC-1, Example 2); prices for the allocation; a TEA
(`operation.batch: {recipe: true}`).
