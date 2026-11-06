# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Iodomethane (methyl iodide) from methanol, red phosphorus and iodine, issue
ChemE-as-Code/process-library#163, a batch entry of core#158. Concept stage: design basis, batch
recipe, balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-06): library `main` at 7f2292c6 (core pin v1.9.0, 314642c). Templates:
`acetyl-chloride-1` (a PCl3 route to an acid chloride with phosphorous acid, a batch still and a
specified-split column; its folder scaffold was copied), `p-toluenesulfonyl-chloride-1` and
`benzoyl-chloride-1` (vent, still and column), `methylmagnesium-bromide-1` (a solid metal as a
reactant of a liquid semi-batch). Library ADR 0035: one dedicated train, campaigns out of scope
(D-015). The route scouting (session notes, 2026-11-05) had deferred this entry until core had a
batch still (core#165), which core 1.8.0 brought.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine translation; NIST WebBook, PubChem and Wikipedia pages;
the open data tables packaged in the `chemicals` Python package).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | CN 114195616 B: a preparation method of methyl iodide, https://patents.google.com/patent/CN114195616B/en | Examples 1-3: 36/32/28 kg red phosphorus (98.5-99 %), 144/120/110 kg methanol (99.5 %), 360 kg crude iodine (95-96 %); red phosphorus and methanol charged in portions through an inerted phosphorus tank (evacuated to about -0.02 MPa and refilled with nitrogen three times or more; charging them directly to the enamelled kettle risks a static ignition); the iodine placed in an iodine tank in the reflux return, dissolved by the condensate and carried into the kettle; stage 1 at 70-75 C kettle temperature, stage 2 at total reflux at 39-40 C (Ex. 1) or 42-45 C (Ex. 2, 3) for 6-8 h once the kettle temperature has fallen by 10-20 C, until the reflux runs colourless; graphite condensers with the outlet at 0-10 C; kettle limits 90 C and 120 kPa with an interlock that bypasses the iodine tank; the crude distilled off over 8-12 h up to 90 C into a kettle with sodium thiosulfate solution; two thiosulfate washes and two water washes (15 min stirring, 1-2 h settling each); drying over 40 kg calcium chloride and an 8 kg 4A molecular sieve column; distillation at 40-90 C; purity 99.5/99.7/99.6 %, water below 200/80/80 ppm, yield 95/96/95.6 % (no basis stated). The patent writes 10 CH3OH + 5 I2 + 2 P -> 10 CH3I + 2 H3PO4 + 2 H2O and names PI3 as the intermediate. Claims: methanol : red P : iodine 5-8 : 1-3 : 16-18 by mass, stage 2 for 20-24 h (the examples use about 4 : 1 : 10 and 6-8 h); no thiosulfate strength, wash volumes, residue treatment or iodine recovery are given | read; patent, facts only | D-001, D-003, D-004, D-005, D-007 to D-010, D-013 |
| SRC-2 | PubChem CID 6328, methyl iodide (HSDB), https://pubchem.ncbi.nlm.nih.gov/compound/6328 | water solubility 1.39e4 mg/L at 20 C; density 2.28 at 20 C; heat of vaporization 27.97 kJ/mol at 25 C; turns yellow to brown in light and moisture; manufacture from methanol, iodine and red phosphorus, from potassium iodide and dimethyl sulfate, from methanol and hydrogen iodide | read (PUG View) | D-001, D-008, D-012, materials |
| SRC-3 | PubChem CID 807, iodine (HSDB) | solubility 23 g/100 cm3 in methanol at 25 C; 14.6 g/100 g in bromoethane at 25 C | read (PUG View) | D-004 |
| SRC-4 | The `chemicals` 1.5.2 package (core's environment): its packaged CRC Handbook tables (`heat_capacity.CRC_standard_data`, `miscdata.CRC_organic_data`, `CRC_inorganic_data`), `phase_change.Hfus` | formation enthalpies: methanol (l) -239.2, iodomethane (l) -13.6 (g 14.4), phosphorous acid (cr) -964.4, phosphoric acid (l) -1271.7, water (l) -285.8, PI3 (cr) -45.6 kJ/mol, iodine and white phosphorus 0; iodine's gas -62.4 above its solid; liquid heat capacities methanol 81.1, iodomethane 126.0, water 75.3 J/(mol K), solid iodine 54.4, white phosphorus 23.8; densities methanol 791.42, iodomethane 2278.92, iodine 4933, phosphorous acid 1650 kg/m3; boiling points methanol 337.65 K, iodomethane 315.55 K; fusion of phosphorous acid 12.8 kJ/mol | open data package queried 2026-11-06; facts only. The CRC values come from the tables packaged in `chemicals`, not from the printed (licensed) handbook | materials, reactions, D-005 |
| SRC-5 | Wikipedia, Allotropes of phosphorus, https://en.wikipedia.org/wiki/Allotropes_of_phosphorus | red phosphorus: -17.6 kJ/mol (formation, against white phosphorus); made by heating white phosphorus to 300 C without air; bulk red phosphorus does not ignite in air below 240 C | read; CC BY-SA, facts only | D-005, D-014 |
| SRC-6 | NIST Chemistry WebBook, SRD 69: iodomethane (C74884), methanol (C67561), iodine (C7553562), water | Antoine constants: iodomethane 218-315.6 K and 315.6-521 K (Stull 1947), methanol 288.1-356.83 K (Ambrose and Sprake 1970), iodine 311.9-456 K (Stull 1947), water (Stull 1947); boiling points iodomethane 315.7 +/- 0.2 K, methanol 337.8 +/- 0.3 K; heats of vaporization iodomethane 28.41 kJ/mol at 315.8 K (Thompson and Linnett 1936), methanol 35.21 kJ/mol at 337.7 K (Majer and Svoboda 1985) | read | materials, D-007, D-010, D-012 |
| SRC-7 | PubChem CID 5462309, phosphorus (HSDB) | red phosphorus: density 2.34, insoluble in organic solvents | read (PUG View) | materials, D-004 |
| SRC-8 | Wikipedia, Azeotrope tables, https://en.wikipedia.org/wiki/Azeotrope_tables | iodomethane with ethanol: an azeotrope at 41.2 C with 96.8 wt% iodomethane; with formic acid at 42.1 C; no iodomethane-methanol row (the tables cite Lange's 10th and the CRC 44th editions) | read; CC BY-SA, facts only | D-010 (a lead that the methanol pair may form one) |
| SRC-9 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-006 |
| SRC-10 | processes/methanol-1, iodine-1, asu-1, methylmagnesium-bromide-1, acetyl-chloride-1 (this library) | methanol with 500 ppm water (its product); iodine flakes 99.8 wt% with 0.2 wt% water (its product S20); gaseous nitrogen; a solid metal as a pseudo-liquid reactant (methylmagnesium-bromide-1 D-005, L-4); the scaffold and the still-with-column pattern | library, internal | D-004, D-014 |
| SRC-11 | PubChem CIDs 24477 (sodium thiosulfate), 5284359 (calcium chloride) | identity (formula, InChIKey, ChEBI cross-reference) | read (PUG REST) | registry |
| SRC-12 | Ullmann's Encyclopedia of Industrial Chemistry, Iodine and Iodine Compounds (doi:10.1002/14356007.a14_381.pub2) | - | not read (licensed); named by iodine-1 and the route scouting as a lead | route lead only |

Searched and not found openly (2026-11-05/06): kinetics or calorimetry of red phosphorus and
iodine in methanol, a measured heat of reaction, a TD24 of the reaction mass or the residue, the
vapour-liquid equilibrium or an azeotrope of iodomethane with methanol (Horsley's Azeotropic Data
was found only as a title page), the liquid-liquid equilibrium of iodomethane, methanol and
water, the solubility of water in iodomethane, iodine's heat of solution in methanol, the basis of
the patent's yield, a plant's specific consumptions, prices and a market volume.

## D-001 Route and boundary (2026-11-06)
Decision: the red phosphorus route of SRC-1: 6 CH3OH + 2 P + 3 I2 -> 6 CH3I + 2 H3PO3 through PI3
formed in situ (D-004 on the by-product). Methanol and red phosphorus are charged to R-101 and
warmed to 313 K; the iodine is dosed into the slurry under the reflux condenser E-101 (D-004); the
crude iodomethane is distilled off the phosphorous acid residue in R-101 through E-101 into a
sodium thiosulfate solution in V-102 (D-007), washed twice with thiosulfate and twice with water
(D-008), dried over calcium chloride and a 4A sieve in A-103 (D-009) and distilled in C-104 with
its column K-104 (D-010). Every vent goes through the brine condenser E-102 to an activated-carbon
adsorber X-106 (D-012). One product on a dedicated train (D-015). Boundary feeds: methanol, red
phosphorus, iodine, thiosulfate solution, process water, electricity, LP steam, nitrogen, calcium
chloride, the sieve and activated carbon (per batch); returns: cooling water, chilled water,
brine; outputs: iodomethane, the phosphorous acid residue, the final still residue, the wash
liquors, the spent desiccants and carbon.
Reason: the route the issue and the scouting name (route (a)), with an open batch example of
amounts, temperatures, times, work-up and product quality. It exercises a dosed exothermic
semi-batch with a solid reactant under reflux, two batch stills and a column.
Rejected: methanol with aqueous HI (MeOH + HI -> CH3I + H2O, named by SRC-2 and the scouting): HI
has no library process yet (hydrogen-iodide-1 is pending on the continuous track), and the
reaction suits a continuous reactive distillation; a variant. Dimethyl sulfate with potassium
iodide (SRC-2, the patent's prior art): dimethyl sulfate's toxicity, rejected by the source too.
Links: methanol from methanol-1, iodine from iodine-1, nitrogen from asu-1. Red phosphorus, the
thiosulfate, calcium chloride, the sieve and activated carbon have no library producer (D-014).

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: 500 t/a of distilled iodomethane (63.131 kg/h year average), 7920 h/a, ASSUMED. Modelled
product (S25): 99.60 wt% iodomethane, 0.40 wt% methanol and 41 ppm water. **The purity is the
source's, not a prediction**: K104's methanol share is calibrated to SRC-1 Example 3's 99.6 %
(D-010). The water is the model's, inside SRC-1's below 80-200 ppm.
Reason: no open market or plant figure was used; a few hundred tonnes a year is a plausible size
for a dedicated batch train of an iodine fine chemical (the patent's kettle makes about 0.35 t a
batch). The LCI is per kg and does not depend on the scale; the batch size does (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 1401.58 kg of iodomethane (stream S25); the recipe
(`process/recipe.yaml`) has four unit procedures:
- REACT on R-101, one vessel over M101, H101, R101, ST101, E101 and H102 (`units`, core ADR 0057):
  nitrogen purge 0.5 h, charge methanol and red phosphorus 1.0 h, warm 298 -> 313 K 0.10 h (from
  the jacket), dose the iodine 10 h and post-react 0.37 h to 0.995 conversion of the iodine (both
  from R101's model), hold 1 h (sampling for the iodine colour), distil 7.73 h (from ST101's
  boil-up), cool the residue 1 h, drain 0.5 h: 22.20 h;
- WASH on V-102 over W101, D102 and D103: receive 0.5 h, two thiosulfate and two water washes of
  2.75 h each (15 min stirring, 2 h settling, 0.5 h to separate; SRC-1, Examples 2 and 3), transfer
  0.5 h: 12 h;
- DRY on A-103: percolate 2 h, transfer 0.5 h;
- DISTIL on C-104 over ST102, K104, M104, E105 and H103: receive 0.5 h, distil 6.75 h (from
  ST102's boil-up), cool 0.5 h, drain 0.5 h: 8.25 h.
R-101 is the bottleneck: cycle 22.201 h, 356.7 batches in 7920 h; one batch takes 43.45 h from the
purge to the final residue's drain. The flowsheet's flows are the recipe's year averages: 1401.58
kg x 356.7 / 7920 h = 63.13 kg/h of S25 (no `cheme.recipe-basis` finding). The batch size was
found by fixed-point iteration with the feeds, the vent fraction and the cycle (L-7).
Dosing time: SRC-1 gives none for its first stage; 10 h is ASSUMED, so that R-101's jacket on
chilled water removes the model's peak (25.38 kW) with room (35.73 kW at the charge's 3.67 m2) and
the accumulation stays low (D-006). Hold: SRC-1 holds 6-8 h at total reflux until the reflux runs
colourless; with the iodine dosed as a solid there is no iodine held up in a reflux loop (D-004),
so the post-reaction of the model and a 1 h hold for sampling are taken (ASSUMED).
Vessels (fill 0.8, H/D 1.2, enamelled, ASSUMED): R-101 1.6 m3 (R10 preferred size, 70 % full with
1.112 m3 at the end of the dosing, D 1.19 m), as the recipe sizes it from R101's model (core ADR
0052). Its jacket (U 300 W/(m2 K)) is checked on chilled water entered at its log-mean
equivalent: water in at 278.15 K and out at 283.15 K against the mass at 313.15 K gives (35 - 30)
/ ln(35/30) = 32.44 K, so 280.71 K, not the supply temperature (core takes the coolant as one
temperature). The warming and the distillations run on a pressurised hot-water loop at
363.15/358.15 K (mean 360.65 K): its supply is SRC-1's kettle limit of 90 C, so that no failure of
the loop's control can heat a kettle above it (D-006, D-011). V-102 about 2.5 m3, C-104 about 1.6
m3, sized by hand (core's still has no vessel, L-4).
Reason: core ADR 0051 puts the batch basis in one place; the dosing, post-reaction, warming and
distillation times come from the models. The washes' times are SRC-1's; the rest are ASSUMED.

## D-004 Feeds, the by-product, the iodine dose and the red phosphorus (2026-11-06)
Decision, ratios: SRC-1 Example 1's on a pure basis (143.3 kg methanol, 35.46 kg phosphorus, 342
kg iodine): 3.319 mol methanol and 0.8496 mol red phosphorus per mol of iodine. The methanol is
66 % above the 2 mol the reaction takes, the phosphorus 27 % above the 2/3 mol. Methanol from
methanol-1 (500 ppm water), iodine from iodine-1 (99.8 wt%, 0.2 wt% water), red phosphorus 100 %
(the patent's 98.5-99 %; impurities not modelled). Per batch: 1305 kg iodine, 546 kg methanol,
135 kg red phosphorus. The feeds' water (2.9 kg, 0.16 kmol a batch) is carried as an inert; its
hydrolysis of PI3 gives HI, which methanol takes back to iodomethane and water, so it changes no
iodine balance (not modelled).
Decision, by-product: **phosphorous acid (H3PO3), not the phosphoric acid (H3PO4) SRC-1 writes.**
SRC-1 itself names PI3 as the intermediate, and PI3 + 3 CH3OH -> 3 CH3I + H3PO3 gives phosphorous
acid. The patent's equation (10 CH3OH + 5 I2 + 2 P -> 10 CH3I + 2 H3PO4 + 2 H2O) balances, but
needs the phosphorous acid oxidised by a further iodine per phosphorus. With the red phosphorus
in excess at either stoichiometry (Example 1: 0.85 mol P per mol I2, against 0.67 needed for H3PO3
and 0.40 for H3PO4), the iodine is taken by the phosphorus first, so H3PO3 is taken. The choice
changes the phosphorus used (2/3 against 2/5 mol per mol I2), the heat (-180 against -165 kJ per
mol I2 by SRC-4) and the residue, not the iodomethane per iodine. Recorded as an open input.
Decision, the iodine dose: **the iodine is dosed as a solid through a closed solids feeder with a
nitrogen lock, at a constant rate over 10 h; it dissolves as it enters.** In SRC-1 the reflux
carries it in from an iodine tank in the condensate return. Rejected because: at 23 g per 100 cm3
of methanol (SRC-3) a batch's 1305 kg of iodine needs about 5.7 m3 of condensate, 0.57 m3/h over a
10 h dose, a boil-up of about 140 kW (methanol at 35.21 kJ/mol, SRC-6). That is several times what R-101's jacket gives below the
90 C limit (35 kW, D-007). It also couples the iodine's feed rate to the boil-up: a hotter kettle
boils more, which carries in more iodine, a self-accelerating loop that SRC-1 breaks only by an
interlock bypassing the iodine tank. A metered dose keeps the semi-batch feed-controlled, which
is the reason to dose (SRC-9). Core's semi-batch takes the dose as a liquid (its own volume
added, L-3).
Decision, red phosphorus: a solid reactant in the charge, `phase: solid` with its own volume
(2340 kg/m3, SRC-7) and a heat capacity, its pseudo-concentration in the rate law with an order
of 2/3 (the surface shrinking with the mass), as methylmagnesium-bromide-1 takes magnesium (its
D-005, L-4). It ran without a change to core. It is charged as a methanol slurry through an
inerted phosphorus tank (SRC-1: static ignition). The 27 % excess leaves with the residue (D-013).

## D-005 Reactor R-101: semi-batch, temperature, kinetics and heat of reaction (2026-11-06)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the charge S4 (methanol and red phosphorus
at 313.15 K), the iodine S5 (298.15 K) dosed over 10 h, then the post-reaction to 0.995 conversion
of the iodine (`batch.target`; 0.37 h from the model), isothermal at 313.15 K and atmospheric
pressure, with a vent for the iodomethane that passes E-102 (D-012). One reaction MEI
(`process/reactions.yaml`), the two steps 2 P + 3 I2 -> 2 PI3 and PI3 + 3 CH3OH -> 3 CH3I + H3PO3
lumped: rate first order in dissolved iodine and of order 2/3 in the phosphorus, zero order in
methanol, k = 4.1e-4 (m3/kmol)^(2/3)/s at 313 K (5.1e-4 at 316 K, Ea 60 kJ/mol), ASSUMED. k is
sized so that the iodine left accumulated at the end of the dosing reacts to 0.995 in well under
an hour (0.37 h): a fast reaction once PI3 forms. The patent's long total reflux is taken as the
return of the iodine held in its reflux loop (D-003, D-004).
Temperature: 313.15 K is SRC-1 Example 1's stage-2 temperature at total reflux (39-40 C), the
boiling point of the end mass (D-006). A semi-batch runs at one temperature (L-8). SRC-1's first
stage at 70-75 C (where methanol refluxes and dissolves the iodine) is not modelled: with the solid
dose there is no need to boil the methanol, and the lower temperature makes the accumulation
higher, which is conservative for the screening.
Heat of reaction: -540.0 kJ per 3 mol of iodine (-180 kJ/mol I2), from the CRC formation
enthalpies of SRC-4 with phosphorous acid as the crystal and red phosphorus at -17.6 kJ/mol
(SRC-5); with liquid phosphorous acid it is -514.4 kJ. The heats of solution of the iodine and of
the phosphorous acid in methanol are not counted (L-6); the iodine's dissolving is endothermic
(at most its fusion, 15.5 kJ/mol, D-011), so leaving it out does not make the screening
optimistic. Adiabatic rise of the whole batch: 520.1 K. **The reaction is strongly exothermic; the
low accumulation (2.28 %) is a consequence of the assumed rate law**, for reaction calorimetry
before basic engineering.
Side reactions not modelled: dimethyl ether from methanol over the acid (a gas that would load
the vent), the esterification of phosphorous acid by methanol, the oxidation of phosphorous acid
by iodine (SRC-1's equation), HI.

## D-006 Thermal screening, the MTT under reflux, the sensitivity, the vent and the release cases (2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054, 0058): dT_ad 520.1 K; largest
accumulation of the dosed iodine 2.28 %, at the end of the dosing; MTSR there 322.6 K, against an
MTT of 313.15 K (`hazard.mtt`), so the MTSR lies 9.4 K **above** the MTT
(`cheme.reactor-hazard-mtsr`, warning). MTSR over the batch (core 1.9.0): 313.1 K at the start,
317.8 K at 2.06 h, 319.4 K at 6.75 h, 322.6 K at the end of the dosing (10 h, X_ac 0.0228), 315.2 K
at 10.4 h.
The MTT and the reflux: R-101 runs at the boiling point of its end mass, as SRC-1 does at total
reflux (Example 1: 39-40 C; Examples 2 and 3, with less methanol, 42-45 C). `hazard.mtt` is that
measured reflux temperature, 313.15 K. Core's default would be the lowest normal boiling point of
the charge and the dose, methanol's 337.8 K (iodomethane, the product and a vent component, is
left out; scratch copy without `hazard.mtt`, 2026-11-06): 24.7 K too high, and with it the
screening would show the MTSR below the MTT (L-5). With T_p at the MTT, any accumulation takes a
cooling failure above it: the warning cannot be designed away at this temperature, since even
0.5 % accumulated iodine is 2.6 K (dT_ad x X_ac). So `cheme process reactor-hazards` exits 1 on this warning, by design. It is the reflux reactor's case: above the MTT
the mass boils, and the barrier is the condenser E-101, not a temperature margin (Stoessel's
class 3 reasoning, SRC-9). In a closed vessel the same heat would raise the pressure, which
SRC-1 caps at 120 kPa by an interlock; core screens neither the boil-off against a condenser nor a
pressure (L-9).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
With the MTSR above the MTT the class is 3 if the TD24 lies at or above the MTSR, 4 if it lies
between the MTT and the MTSR (313.15 K < TD24 < 322.6 K), and 5 if it lies at or below the MTT:
core's `criticality()` and Stoessel test the TD24 against the MTSR first (SRC-9).
Gas release at a cooling failure at the MTSR (ADR 0058): 3.385e-6 kmol/s, 0.32 m3/h at 322.6 K,
the vented share (0.6365 %) of the iodomethane the accumulated iodine forms; R-101's vent
capacity 20 m3/h (0.016 of it, `cheme.reactor-hazard-vent` info). The main reaction forms no gas.
Sensitivity (a scratch copy of the folder, only A divided, everything else as designed; `cheme
process propagate --fill`, `reactor-hazards`, `reactors`, `recipe`; not committed; the boil-off
by core's `solve_node` cooling profile and the rate law at the MTT):

| k at 313 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 313.15 K | post-reaction to 0.995 | cycle | gas at the MTSR | boil-off at the MTT (dose stopped / going on) | class without TD24 |
|---|---|---|---|---|---|---|---|---|
| 4.1e-4 (design) | 2.28 % | 322.6 K | 9.4 K above | 0.37 h | 22.20 h | 0.32 m3/h | 24.4 / 50.0 kW, 79 / 163 m3/h | 3, 4 or 5 |
| k/10 | 15.4 % | 378.7 K | 65.6 K above | 7.90 h | 29.73 h | 9.10 m3/h | 21.2 / 46.9 kW, 69 / 153 m3/h | 3, 4 or 5 |
| k/100 | 61.6 % | 604.0 K | 290.9 K above | 99.8 h | 121.6 h | 1.18e4 m3/h | 14.1 / 39.8 kW, 46 / 130 m3/h | 3, 4 or 5 |

Core's gas release is the vented iodomethane's share at the rate law at the MTSR; at k/100 the
MTSR of 604 K is an adiabatic figure the boiling mass never reaches, and its 1.18e4 m3/h means only
that core's gas release does not stop at the MTT (L-9). The boil-off column is the iodomethane
vapour a cooling failure at the worst moment gives at the MTT (28.41 kJ/mol, SRC-6; m3/h at 313
K): the accumulated iodine reacting at the rate law at 313.15 K, and, as an upper bound, with the
dose's heat added if the dosing is not stopped (the batch's iodine over 10 h at -180 kJ/mol).
Interpretation: at the design kinetics a cooling failure boils off about 24 kW of iodomethane with
the dosing stopped and about 50 kW if it goes on. E-101 on cooling water, with its own supply
independent of R-101's chilled water, is to be designed for 50 kW (it takes the still's start,
about 34 kW, anyway). Then the reflux holds a jacket failure, and the dosing interlock halves the
load. A slower reaction (k/10, k/100) accumulates more but releases its heat more slowly, so the
boil-off falls. The cycle shows it first: 29.7 h at k/10, 122 h at k/100, which rules that design
out. The hazard is the loss of both heat sinks, or a blocked vent with the condenser lost (D-012).
Vent capacity (ADR 0058): `hazard.vent_capacity: 20` m3/h at R-101's 101.3 kPa(a), ASSUMED: R-101's
vent line through E-101 and E-102 to the adsorber, sized for the nitrogen purge of R-101 and the
phosphorus tank (5 Nm3 in 0.5 h, 11.5 m3/h at 313 K) with room. It covers core's gas release at
the MTSR (0.32 m3/h), the vent's normal peak (0.17 m3/h, `cheme process recipe`) and the k/10 case
(9.1 m3/h).
**Design finding: the boil-off is for E-101 to condense, not for the vent.** 79 m3/h (dose
stopped) to 163 m3/h (dose going on) of iodomethane vapour is 4.0 to 8.1 times the vent capacity.
Release cases (not assessed, reasoning only; for the HAZOP of the next stage):
- (a) Loss of R-101's jacket cooling (chilled water) during the dosing: the boil-off above, to
  E-101. The dosing is to be interlocked on the chilled water's flow and temperature, on R-101's
  temperature and on E-101's cooling water.
- (b) Loss of E-101's cooling water while R-101 boils (at the end of the dosing, or in the
  distillation): iodomethane vapour to E-102 (0.23 kW year average) and the adsorber, neither
  sized for it. The still's heat at 15 kW would be 1.9 kmol/h of vapour (49 m3/h). The hot-water
  loop and the dosing are to be interlocked on E-101's cooling water and gas outlet temperature.
- (c) Failure of the jacket changeover: the hot-water loop (360.65 K mean) on R-101 during the
  dosing heats the mass towards its supply temperature. At the charge's 3.67 m2, 300 W/(m2 K) x
  3.67 m2 x (360.65 - 313.15) K = 52 kW, with the reaction's 24 kW, 77 kW of boil-off beyond
  E-101's 50 kW. The loop's supply at 363.15 K caps the temperature (the patent's limit), not the
  boil-off: a dosing permissive on the jacket in cooling mode, and an independent
  high-temperature trip on R-101 that isolates the loop.
- (d) A blocked vent with E-101 working: no gas forms (the reaction forms none at the design
  kinetics), so only the boil-off beyond E-101 pressurises R-101. SRC-1 caps the kettle at 120
  kPa with an interlock; a relief device to a catch tank and the adsorber is to be sized for case
  (c).
- (e) Red phosphorus: a static ignition of the methanol-phosphorus slurry while charging (SRC-1);
  the residue holds the excess red phosphorus (27 % of the charge) wet with methanol and
  phosphorous acid, which is not to be dried or heated in air (red phosphorus ignites above 240 C,
  SRC-5; phosphorous acid disproportionates to phosphine on strong heating). The hot-water loop
  at 363 K stays far below both.
- (f) Iodomethane is toxic and volatile (64.7 kPa at 303 K, SRC-6): every vent goes through E-102
  and the adsorber (D-012). A loss of brine to E-102 sends about 0.68 kmol a batch of iodomethane
  vapour to the carbon instead of 0.065.
Screening values only, not a reaction-hazard assessment.

## D-007 Still ST101: the crude distilled off the residue in R-101 (2026-11-06)
Decision: ST101 is core's batch still (`still:`, core ADR 0055) in R-101: the reaction mass S6 boiled
at 101.325 kPa(a), phosphorous acid and the red phosphorus non-volatile, until iodomethane is 1.2
mol% of the residue (`end: residue`, ASSUMED). The volatility is a **constant relative
volatility** to methanol: iodomethane 6, water 0.25, iodine 0.009 (ASSUMED). Water and iodine are
at their ideal ratios at 340 K (by the NIST Antoine constants, SRC-6). Iodomethane is at about
three times its ideal ratio (2.13 at 330 K, 1.70 at 350 K) for its positive deviation in the polar
residue, not measured. Boil-up 15 kW, the mean R-101's jacket gives on the hot-water loop: about
34 kW at the start (300 W/(m2 K) x 3.67 m2 x 31 K), a few kW at the end. The distillation takes
7.73 h; SRC-1 takes 8-12 h. Result (`cheme process stills`): 1977 kg of reaction mass a batch give
1547 kg of crude S8 (92.3 wt% iodomethane, 7.7 wt% methanol) and 431 kg of residue (40.3 mol%
methanol, 44.1 mol% phosphorous acid, 12.4 mol% phosphorus, 1.2 mol% iodomethane), with 1.40 % of
the iodine fed (D-013). The residue's bubble point by Raoult's law is then 357.1 K, below the loop's
363.15 K supply.
Reason: with Raoult's law the phosphorous acid and the suspended phosphorus dilute the liquid,
which core counts in its mole fractions (L-2). At 353 K the residue would still hold 16.6 mol%
iodomethane, 13 % of what is formed, a yield the source's 95-96 % rules out. The patent heats to
90 C, and phosphorous acid binds methanol, so methanol stays in the residue while iodomethane
leaves: a constant relative volatility above the ideal ratio represents that; its value is the
open input. Core gives no temperatures with a constant relative volatility; the stills'
temperatures S8 and S9 are the script's Raoult bubble points (an estimate) and the heat-up Q4
uses them (D-011). Rejected: ending the still at a temperature (the ideal liquid's residue keeps
too much iodomethane, above); distilling to the patent's 90 C (the loop would have to be hotter
than the kettle's limit).

## D-008 The washes D102 and D103 (2026-11-06)
Decision: the crude S10 (condensed at 303 K in E-101) runs into the thiosulfate solution S13 in
V-102. W101, a conversion step, reduces its iodine (THIO, I2 + 2 Na2S2O3 -> 2 NaI + Na2S4O6,
conversion 1). D102 is the two thiosulfate washes and D103 the two water washes, each a specified
split in scripts/balance.py over two equal contacts. In each contact methanol is shared at a
distribution of 5 (mass fractions, aqueous over organic, ASSUMED: no LLE data found). Iodomethane
dissolves in the aqueous phase at 13.9 g per kg of its water (SRC-2, 20 C; a lower bound with
methanol in that phase). The organic leaves saturated with 0.1 wt% water (ASSUMED). The salts stay
aqueous. Amounts (ASSUMED, SRC-1 gives none): 0.20 kg of 5 wt% thiosulfate solution and 0.40 kg of
water per kg of crude, 309 kg and 619 kg a batch. The thiosulfate is 272 times the iodine's need:
the crude holds little iodine at 0.995 conversion. Its amount is set by the washing, not by the
iodine.
Result: methanol in the crude 7.67 -> 2.96 -> 0.66 wt%; wash liquors 47.25 kg/h (0.75 kg per kg of
product) with 0.88 % of the iodine fed as dissolved iodomethane. Temperatures from the inlets'
mixing (adiabatic): S14 306.96 K (the crude at 303.15 K, the solution at 298.15 K, the iodine's
reduction at -30 kJ/mol, ASSUMED, and the methanol taken into water at -7.3 kJ/mol, ASSUMED order
of its dilute heat of mixing); S18 303.23 K.
Reason: core's NRTL extraction needs binary pairs, and none is sourced for iodomethane, methanol
and water (L-2). Iodomethane is the lower phase (2.28 g/cm3, SRC-2).

## D-009 Drying A-103 (2026-11-06)
Decision: X101 is a specified split: the washed crude's 0.1 wt% water down to 100 ppm (ASSUMED,
inside SRC-1's product water of below 80-200 ppm), 1.28 kg a batch, to the spent desiccants
(S21). The calcium chloride takes it to 300 ppm and the sieve the rest (ASSUMED). Per batch 3.3 kg
of calcium chloride (at 0.3 kg of water per kg before the bed is replaced) and 2.9 kg of sieve (at
0.1 kg per kg, replaced, not regenerated, so no regeneration heat) are `lca.yaml` consumables with
their disposal. SRC-1's bed is 40 kg of calcium chloride and an 8 kg sieve column for 360 kg of
iodine; how often it is renewed is not stated. The water's uptake as calcium chloride's hydrate
(-16 kJ/mol, ASSUMED order) warms the crude to 304.12 K. Methanol taken up by the calcium chloride
(which binds alcohols) is not modelled.
Reason: core's `dryer:` dries a solid cake to a residual moisture (ADR 0057); a liquid dried over
a desiccant is an adsorption, a specified split (L-2).

## D-010 Final distillation ST102 with its column K104: a single stage does not reach the purity (2026-11-06; revisit with core#173)
Decision: ST102 is core's batch still on Raoult's law with the NIST Antoine constants (an ideal
liquid, ASSUMED), until iodomethane is 50 mol% of the residue, boil-up 12 kW net (a 36 kW reboiler
on C-104's jacket at the column's reflux ratio 2). The column K104 on it is a specified split of
the still's distillate S22 in scripts/balance.py: 99 % of the iodomethane and all the water to the
product (ASSUMED; iodomethane and water boil together, an upper bound for the water), and the
methanol's share calibrated so that the product holds SRC-1 Example 3's 99.6 % (0.654 of the
methanol). The rest returns to the pot (S27) and leaves with the residue to incineration (S26, 16
g per kg of product). The distillation takes 6.75 h.
Purity of one stage: **one Rayleigh stage does not reach the source's purity**. Even on the ideal
liquid, the distillate S22 is 99.40 wt% iodomethane with 0.60 wt% methanol, below SRC-1's 99.5-99.7
%. The ideal liquid is optimistic: alcohols and iodoalkanes form azeotropes (iodomethane with
ethanol at 41.2 C and 96.8 wt%, SRC-8; no methanol row was found), and near pure iodomethane
methanol is then more volatile than the ideal liquid says. The product needs the column, the
patent's "molecular sieve rectifying column", and the washes, which take the methanol out. Its
stages and reflux are to be set with VLE data.
Reason: core's still is one stage with no reflux (ADR 0055, core#173), so the column's work is a
stated split, as in acetyl-chloride-1 and benzoyl-chloride-1. The 99.6 % is the source's, so the
product's purity is no headline the model predicts.
Rejected: the still alone (99.40 wt%); a cut sequence (`cuts:`) of the one-stage still: on the
ideal liquid methanol is the heavier component, so a first cut is no purer in it; recycling the
final residue and the column's return (50 mol% iodomethane, 1.28 % of the iodine) to the next
batch's wash, the obvious improvement but a tear across batches (a variant).

## D-011 Utilities and heat: every energy flow (2026-11-06)
Decision (year averages; Q2, Q3 and Q8 from core's models, the rest from scripts/balance.py,
ASSUMED unless sourced):
- Q1 0.28 kW of LP steam via the hot-water loop: the charge S3 warmed from 298.15 to 313.15 K.
- Q2 11.45 kW from R-101's jacket to chilled water: the heat of MEI (11.50 kW) less the iodine
  warmed from 298.15 to 313.15 K (0.05 kW), written by R101's semi-batch model (`calculated`,
  `energy_port: q`, ADR 0059); the script gives the same terms as a cross-check. Peak 25.38 kW
  during the dosing (D-003). At the end of the dosing the mass reaches its boiling point and E-101
  takes part of it as reflux on cooling water: Q2 on chilled water is then an upper bound and Q5
  a lower one, by an unknown split of at most Q2.
- Q3 5.22 kW of LP steam: ST101's net boil-up (the latent heat of the crude S8), from the still's
  model (`energy_port: steam`); Q4 0.69 kW: the reaction mass heated from 313.15 K to its bubble
  point (329.55 K) and the residue on to 357.14 K, which the still model does not hold (L-4).
- Q5 5.74 kW to cooling water: E-101 condensing the crude S8 and cooling it to 303.15 K.
- Q6 0.37 kW to cooling water: the residue cooled from 357.14 to 313.15 K in R-101.
- Q7 0.23 kW to brine: E-102, the vents' iodomethane condensed from 303 to 268 K (D-012).
- Q8 3.65 kW of LP steam: ST102's net boil-up from the still's model; Q13 7.30 kW: the column's
  reflux share (the reflux ratio 2 times the same latent heat), which the one-stage still does not
  hold (core#173); Q9 0.19 kW: the dried crude heated from 304.12 K to its bubble point 316.12 K and
  the residue on to 326.99 K.
- Q10 11.15 kW to cooling water: K-104's condenser at the reflux ratio 2 and the product cooled to
  303.15 K; Q11 0.31 kW to brine: the product subcooled to 283.15 K (SRC-1: condensers at 0-10 C);
  Q12 0.008 kW to cooling water: the final residue with the column's return cooled to 303.15 K.
- Electricity 5.44 kW (0.086 kWh/kg): R-101's 3 kW agitator and its 0.75 kW loop pump for 21.20 h
  of each 22.20 h cycle and the 0.75 kW iodine feeder during the dosing (3.92 kW, P1); V-102's 1.5
  kW agitator for 1 h and a 1.1 kW pump for 3 h a batch (0.22 kW, P2); C-104's 1.5 kW agitator and
  0.75 kW loop pump for 7.25 h, a 1.1 kW pump for 1.5 h a batch and the 0.5 kW vent fan all the time
  (1.31 kW, P3).
Every energy flow of the batch is in the flowsheet and so in the LCI per kg (library ADR 0035):
LP steam 0.2746 kWh, cooling water 0.2735 kWh, chilled water 0.1813 kWh and brine 0.0086 kWh
removed, electricity 0.0862 kWh. The refrigeration's own electricity is the chilled water's and
the brine's background (gaps, D-014).
Recorded exclusions, each with its estimate (ASSUMED orders, insulated surfaces at about 1 W/(m2
K)): the heat losses of R-101, C-104 and the hot-water loops (at 313-360 K, 15-60 K above the
ambient, about 0.1 to 0.4 kW each while hot, below 5 % of the stills' duties); the iodine's heat
of solution in methanol, endothermic and unknown, at most its fusion (15.5 kJ/mol, SRC-4): 1.0 kW,
9 % of Q2, left out on the safe side; phosphorous acid's heat of solution, between the crystal's
and the liquid's heats of reaction (25.6 kJ per 3 mol of iodine, D-005): 0.55 kW, 4.8 % of Q2; the
heat of mixing of iodomethane and methanol in E-101's condensate (not known); the washes', the
iodine's reduction's and the dryer's heats are counted, in the adiabatic temperatures of S14, S18
and S20 (D-008, D-009). Each mixed stream's temperature follows from its inlets: S14 and S18 from
the adiabatic washes, S20 from the dryer, S28 from S23 and S27 (both at the pot's end temperature).

## D-012 Vents, the vent condenser E-102 and the adsorber X-106 (2026-11-06)
Decision: every vent of the train (R-101 through E-101, V-102, A-103, C-104 with K-104, the product
tank T-107) goes through E-102 on brine (gas out at 268.15 K, 10 K above the 258 K brine) to the
activated-carbon adsorber X-106. Per batch (scripts/balance.py): the wet nitrogen (5 of the
batch's 10 Nm3: the blankets of V-102, A-103, C-104 and the tanks; the 5 Nm3 that purge R-101 and
the phosphorus tank before the charge are dry) and the head spaces the batch's liquids displace
(3.99 m3: the crude, the thiosulfate and the wash water into V-102, the washed crude into A-103,
the dried crude into C-104, the product into T-107, and R-101's rise in volume over the dosing),
0.384 kmol of gas saturated with iodomethane at 303 K (64.7 kPa, SRC-6). E-102 condenses it down
to 14.7 kPa at 268 K, from 0.678 to 0.065 kmol a batch, and returns the condensate. Q7 0.23 kW (the
dry purge's cooling included). The 0.065 kmol (9.2 kg) a batch that pass E-102 are written as
R101's vent fraction, 0.6365 % of the iodomethane formed (R-101's and the work-up's vents lumped
on R101, L-3), to the adsorber. Activated carbon at 0.2 kg of iodomethane per kg (ASSUMED): 46 kg a
batch (0.033 kg per kg of product), an `lca.yaml` consumable with its disposal to incineration
(or regeneration with recovery, a variant). The adsorber's outlet to air is an emission exclusion.
Reason: iodomethane's vapour pressure is high even at 303 K. A brine condenser recovers 90 % of
what the vents carry, and the carbon takes the rest. A 0.6 % yield loss to the carbon is the cost
of the nitrogen and the displacements; recovering it from the carbon is a variant.

## D-013 The iodine's fate, the residue and iodine recovery (2026-11-06)
Decision, the iodine balance (scripts/balance.py, shares of the iodine fed, closing to 0.0001 %):
product 95.81 %; ST101's residue 1.40 % (iodomethane and unreacted iodine); the final residue and
the column's return 1.28 %; the wash liquors 0.88 % (dissolved iodomethane) and 0.004 % (iodide);
the adsorber 0.63 %. **Yield 95.81 % of theory on the iodine**: a model result, inside SRC-1's 95,
96 and 95.6 % (no basis stated). It is an ASSUMED upper bound: every loss not modelled lowers it
(dimethyl ether, HI, iodine held on the phosphorus, the tanks' breathing), and the residue's share
rests on the relative volatility of D-007. On methanol the yield is 58 % (66 % excess, D-004).
The residue S11 (0.31 kg per kg of product): phosphorous acid with methanol, the red phosphorus
excess and 1.4 % of the iodine. SRC-1 says nothing about it. It goes to a hazardous-waste
treatment (an LCI gap, D-014); recovering its methanol and iodine and using the phosphorous acid
are variants.
Iodine recovery: **a gap**. About 4.2 % of the iodine fed leaves with the residues, the wash
liquors and the carbon. Recovery (the iodide oxidised back to iodine, as iodine-1 does from
brine) is not described by SRC-1 and not modelled; the wash liquors are not stripped of their
iodomethane (an emission exclusion).

## D-014 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of iodomethane from the flowsheet's year averages.
Linked (`lca/mappings.yaml`): methanol to methanol-1, iodine to iodine-1, the nitrogen consumable
to asu-1, the LP steam counted as heat (kWh); every other background is a gap with the activity it
should connect to. One product: no allocation (the residues are wastes).
Proxies (gaps, not links): red phosphorus by heating white phosphorus to about 300 C without air
(SRC-5), 1 kg of white phosphorus per kg, which has no library producer either; sodium
thiosulfate from sodium sulfite and sulfur; calcium chloride, zeolite 4A and activated carbon as
purchased materials.
Per kg of iodomethane: iodine 0.931 kg (stoichiometric 0.896 of iodine-1's product), methanol 0.390
kg (0.226), red phosphorus 0.0964 kg (0.0727), thiosulfate solution 0.221 kg, process water 0.441
kg, nitrogen 8.9 g, calcium chloride 2.4 g, sieve 2.1 g, activated carbon 32.8 g, electricity 0.086
kWh, LP steam 0.275 kWh; removed: cooling water 0.274 kWh, chilled water 0.181 kWh, brine 0.0086
kWh; out: residue 0.307 kg, final residue 0.016 kg, wash liquors 0.748 kg, the spent desiccants and
carbon. Not counted: the adsorber's outlet and the wash liquors' iodomethane to air
(emission_exclusions).

## D-015 Dedicated train (2026-11-06)
Decision: R-101, V-102, A-103, C-104, K-104 and the vent system make only iodomethane, batch after
batch: 356.7 batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002). Out of scope, so not LCI gaps:
changeover cleaning, the idle time of a multipurpose train, shared tank farms.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with a solid reactant and a vent: composition, accumulation, MTSR over the batch, peak cooling, year-average duty Q2 | done in cheme, kinetics ASSUMED | D-004, D-005, D-006, core ADRs 0050, 0054, 0058, 0059 |
| boil-off at the MTT against E-101 and the vent | script (core's cooling profile and the rate law), a design finding | D-006, L-9 |
| batch recipe, cycle time, basis check, R-101's vessel, jacket and warming time | done in cheme | D-003, core ADRs 0051, 0052, 0057 |
| still ST101 off the residue | done in cheme, relative volatilities ASSUMED | D-007, core ADR 0055 |
| iodine's reduction W101 | done in cheme (conversion step) | D-008 |
| washes D102, D103 and drying X101 | specified splits in a script | D-008, D-009, L-2 |
| still ST102 (one stage) | done in cheme, ideal liquid ASSUMED | D-010 |
| column K104 | specified split in a script, calibrated to the source's purity | D-010, core#173 |
| vent condenser load and the vent fraction | script, written into Q7 and the vent fraction | D-012, L-3 |
| feeds for 500 t/a, wash liquids, duties other than Q2, Q3, Q8, mixed temperatures, powers | script | D-008 to D-012 |
| per-batch nitrogen, desiccants, carbon | done in cheme, amounts ASSUMED | D-009, D-012, D-014, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-014 |

## Core features used (core 1.9.0)

Built on cheme-as-code 1.9.0 (314642c), the library's pin.

- `reactor: semibatch` with `batch.dosing` and `batch.target` (ADR 0050), a solid reactant
  (`phase: solid` with a liquid molar volume, in the rate law as a pseudo-concentration) and
  `batch.vent` with a `fraction` of a product (ADR 0054); `hazard.mtt` and `hazard.vent_capacity`
  on the step.
- The semi-batch screening of 1.9.0 (ADR 0058): `mtsr_profile`, `gas_release` against
  `hazard.vent_capacity`, the default MTT that leaves the vent component out (checked in a scratch
  copy: methanol's 337.8 K, so `hazard.mtt` stays, L-5); core's `solve_node` cooling profile for
  the boil-off at the MTT (D-006).
- The models' duties (ADR 0059): R101's Q2 by `energy_port: q`, the stills' net boil-ups Q3 and Q8
  by `energy_port: steam`, all `calculated` by `propagate --fill`; the heat the models leave out
  (the stills' heat-up Q4, Q9, the column's reflux share Q13) on its own assumed streams.
- `still:` twice (ADR 0055): ST101 with a constant relative volatility and `nonvolatile` (a
  dissolved acid and a suspended solid), ST102 on Raoult's law with Antoine `vapour_pressure` and
  `heat_of_vaporization`; `boilup` in kW, `end: residue`; `cheme process stills`.
- `process/recipe.yaml` (ADRs 0051, 0052, 0055, 0057): `dose`/`react` `from:` R101, `distil
  from:` ST101 and ST102, `units:` over several steps of one vessel (R-101: a mixer, a heater, the
  semi-batch, a still, a condenser and a cooler), R-101's `vessel` sizing and `jacket` check, a
  `heat` operation timed from the jacket; the script reads the recipe through core's
  `recipe.evaluate` for the powers.
- A conversion step (`reactor: conversion`) for the thiosulfate's reduction; `lca.yaml`
  `consumables` with `per_batch` and `disposal` (ADR 0053).
- Not used: `tears:` (ADR 0060; no recycle is modelled, the final residue's recycle is a variant,
  D-010), `hazard.reactions` (one reaction), `dosing.absorbed` (no gas is dosed), the
  crystallizer, `dryer:` and the filter (no solid product; the liquid's drying is no cake dryer,
  D-009), the still's `cuts:` and `feed:` (D-010).

## Core limits hit (each a candidate core issue)

- L-1 (core#173): no batch rectification with reflux. One Rayleigh stage gives 99.40 wt%, below the
  source's 99.5-99.7 % (D-010); the column is a specified split, and the still's `boilup` is the
  net distillate, with the reflux share on its own stream Q13.
- L-2: no separation models for the work-up's liquids. The washes need a liquid-liquid split
  without sourced NRTL pairs, the drying of a liquid over a desiccant is no cake dryer, and the
  batch still counts a suspended solid (the red phosphorus) and a dissolved non-volatile in the
  liquid's mole fractions, with no activity coefficients. On Raoult's law ST101 would leave 13 %
  of the iodomethane in the residue (D-007), so a constant relative volatility had to be assumed;
  with it the still gives no temperatures. A specified phase split as a separator that propagate
  solves, solids left out of a still's liquid, and activity coefficients in the still would remove
  most of the script.
- L-3 (ADR 0054): the vent carries only components a reaction forms, at a stated fraction, and one
  step's vent only; the work-up's vents (V-102, A-103, C-104, T-107) are lumped on R101's, the
  fraction written by hand from the script (the balance-output contract does not check a step
  parameter; this folder's test does). A dose is taken as a liquid: a solid dose (the iodine)
  adds its own volume and dissolves at once.
- L-4 (ADR 0055): the still has no heat-up or sensible heat (the script's Q4, Q9) and does not size
  its vessel, jacket or condenser; a boil-up that the jacket's falling driving force limits is one
  constant mean (D-007).
- L-5 (ADR 0058): the default MTT is the lowest boiling point of the charge and the doses; it leaves
  the vented product out and does not follow the liquid as the product forms. Here it is
  methanol's 337.8 K, 24.7 K above the end mass's boiling point (313.15 K, SRC-1), and the
  screening would put the MTSR below it; `hazard.mtt` is set by hand.
- L-6: a semi-batch has one `heat_of_reaction` per reaction and no heat of solution of a dosed
  solid or of a dissolving product (as acetyl-chloride-1's L-11): the iodine's and the phosphorous
  acid's are exclusions (D-011).
- L-7 (as acetyl-chloride-1's L-7): core propagates from the feeds and cannot solve them for a
  product rate; the batch size, the feeds, the vent fraction and the cycle were iterated by hand
  (the script, propagate, the recipe, again).
- L-8 (as acetyl-chloride-1's L-8): a semi-batch is isothermal at one temperature. The source's
  reflux reactor falls from 70-75 C to 39-45 C as the iodomethane forms; the model runs at 313.15 K.
- L-9: **no reflux reactor in the screening (the closed/reflux question).** Core compares the MTSR
  with one MTT and the gas the reactions form with the vent capacity. A reactor at reflux has its
  process temperature at the MTT, so `cheme.reactor-hazard-mtsr` warns for any accumulation. Its
  barrier is the condenser's capacity against the boil-off at the MTT, which core does not compute
  (the script does, D-006). Its gas release does not stop at the MTT (1.18e4 m3/h at k/100's
  adiabatic 604 K). A closed vessel's pressure rise is not screened either. A `hazard.reflux:
  {condenser_capacity}` that caps the MTSR at the MTT and compares the boil-off with it, and a
  pressure for the closed case, would cover it.
- L-10 (as acetyl-chloride-1's L-10): an ideal liquid only; ST102's basis is "not sourced", and no
  azeotrope can be represented (D-010).

## Open inputs
Kinetics and heat of reaction by reaction calorimetry (the iodine's accumulation, the heat of
solution of the iodine); TD24 of the reaction mass and the residue; the by-product (phosphorous or
phosphoric acid) by analysis of the residue; the VLE of iodomethane with methanol (an azeotrope?)
and the relative volatility in the residue; the LLE of the washes and the wash volumes; the
column's stages and reflux; the product specification (assay, methanol, water, stabiliser); the
residue's treatment and the iodine's recovery; E-101's design duty for the boil-off, the relief of
R-101 and the vent system's sizing; the adsorber's capacity and breakthrough; prices and a TEA
(`operation.batch: {recipe: true}`).
