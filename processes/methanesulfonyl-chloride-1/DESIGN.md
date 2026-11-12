# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Methanesulfonyl chloride (mesyl chloride, MsCl, CH3SO2Cl) by the reaction of methanesulfonic
acid with thionyl chloride, issue ChemE-as-Code/process-library#159. Concept stage: design basis,
batch recipe, balanced BFD/PFD with the thionyl chloride recycle, thermal and gas-release
screening with a rate sensitivity, and a preliminary gate-to-gate LCI. Out of scope here:
P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-12): library `main`, which pins cheme-as-code 1.11.0. An earlier route
scouting judged a continuous Tier 2 route credible and the batch variant not ready; core has
since gained what the batch needs: the semi-batch with a gas vent (core ADRs 0050, 0054), the
vent's vapour with a vent condenser (0062), the batch still with a rectifying column (0055,
0061), the charge's heat-up (0063), recycle tears (0060), the duties the models write (0059)
and the screening's gas release and vent capacity (0058).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
for this entry.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Hearst, P. J.; Noller, C. R. (1950) Methanesulfonyl chloride, Organic Syntheses 30, 58; Coll. Vol. 4, 571 (1963), doi:10.15227/orgsyn.030.0058 | Procedure: 1.5 mol methanesulfonic acid heated to 95 C, 2.0 mol thionyl chloride added over 4 h, 95 C kept during the addition and for 3.5 h after; vacuum distillation, most of the thionyl chloride distilling at room temperature; product at 64-66 C and 20 mmHg, 71-83 %. Note 2: the acid 95 % pure with 2 % water. Note 4: a Claisen head with a 10 cm Vigreux column. Note 5: no free flame, local overheating chars and decomposes the product; the heating bath not above 115 C at the end of the distillation. Note 6: 61-62 C at 18 mmHg. Discussion: the other preparations (chlorination of sulfur compounds such as dimethyl disulfide in water; sodium methanesulfonate with PCl5 or POCl3; the acid with PCl5) | read (orgsyn.org PDF); facts only | D-001, D-004, D-005, D-007, D-011 |
| SRC-2 | NIST Chemistry WebBook, SRD 69: thionyl chloride (C7719097), water (C7732185), methanesulfonic acid (C75752), https://webbook.nist.gov | thionyl chloride: Antoine constants 220.3-348.6 K (NIST's fit to Stull 1947), heat of vaporization 32.4 kJ/mol at 272 K (Dykyj et al. 1999); methanesulfonic acid: heat of vaporization 73.9 kJ/mol at 410 K (Stephenson and Malanowski 1987); water: Antoine constants | read; facts only | materials, D-007 |
| SRC-3 | PubChem CID 31297 (methanesulfonyl chloride) and CID 6395 (methanesulfonic acid), https://pubchem.ncbi.nlm.nih.gov | MsCl (HSDB, ICSC): bp 62 C at 18 mmHg and 161 C at 730 mmHg, freezing point -32 C, density 1.4805 at 18 C, vapour pressure 0.27 kPa at 20 C and 3.09 mmHg at 25 C, heat of vaporization 349 kJ/kg (temperature not stated), on heating to decomposition sulfur oxides and HCl; MSA (HSDB): bp 167 C at 10 mmHg, mp 20 C, density 1.4812 at 18 C, vapour pressure 4.28e-4 mmHg at 25 C; identity (formula, InChIKey) | read (PUG REST and PUG View); facts only | materials, D-007, D-011, registry |
| SRC-4 | Huebenett, F. (Merck Patent GmbH, 1981) EP 0 010 162 B1: Verfahren zur Herstellung von Alkansulfonsaeurechloriden, https://patents.google.com/patent/EP0010162B1/en | claim: alkanethiols or dialkyl disulfides with chlorine and water at -10 to +50 C (25-35 C preferred) in the product itself as the medium; continuous circulation driven by the HCl formed preferred, batch possible; Example 3: MsCl from dimethyl disulfide, 99.2 % of theory, 99.4 % by GC, with 30-31 % hydrochloric acid as by-product; prior art: batch chlorination in water (yields and purity unsatisfactory), a circulation process in concentrated hydrochloric acid | read (Google Patents text); patent, facts only | D-001 (route rejected) |
| SRC-5 | The `chemicals` 1.5.2 package (Bell, C. and contributors): its default standard formation enthalpies (`chemicals.reaction.Hfl`, `Hfg`: the CRC Handbook tables it bundles, ATcT for gaseous HCl and water), liquid heat capacities and densities (CRC tables it bundles), and the ideal-gas data `cheme chemistry thermo` prints; IAPWS-IF97 for the steam's saturation | per component in `process/materials.yaml` and per reaction in `process/reactions.yaml` | open package queried 2026-11-12/13; values computed by the package from its bundled tables, not taken from the printed (licensed) handbook | materials, D-005, D-009 |
| SRC-6 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR, MTT and the criticality classes (method, implemented in core's screening, ADRs 0050, 0058) | method reference, no data taken | D-011 |
| SRC-7 | processes/thionyl-chloride-1, chlor-alkali-1, asu-1 (this library) | thionyl chloride 99.7 wt%; caustic soda 50 wt%; gaseous nitrogen | library, internal | D-004, D-012 |
| SRC-8 | Noller, C. R.; Hearst, P. J. (1948) J. Am. Chem. Soc. 70, 3955 | - | not read (named by SRC-1 as the original of the thionyl chloride preparation) | lead only |
| SRC-9 | FR 2 575 468 A1 (methanesulfonyl chloride from gaseous feeds under light) | - | not read for this entry (named in the issue's literature notes, which saw only its introduction in machine translation) | lead only |

## D-001 Route and boundary (2026-11-12)

Decision: methanesulfonic acid (MSA) and thionyl chloride, CH3SO3H + SOCl2 -> CH3SO2Cl + SO2 +
HCl, in a semi-batch reactor: the acid charged and warmed to 95 C (368.15 K), the thionyl
chloride dosed over 4 h, both gases leaving as they form; the excess thionyl chloride distilled
off the crude as a forerun under vacuum and recycled; the product distilled at 4 kPa(a) over a
short column; the SO2 and HCl taken up in a caustic scrubber. Boundary: the batch train from the
feed tanks to the product receiver, with the scrubber and the caustic dilution; the feeds and
utilities cross it as purchased or site supplies.

Reason: it is the one route with an open, complete and checked procedure (SRC-1: amounts,
times, temperatures, the vacuum distillation, a yield and the limit on the heated wall) and it
uses a feed this library makes (thionyl-chloride-1). It is a batch route by nature: a liquid
dosed into a liquid with gas evolution at near-ambient pressure, followed by a batch
distillation, which is what this wave of entries exercises.

Rejected:
- Chlorination of dimethyl disulfide or methyl mercaptan with chlorine and water (SRC-4): open,
  high yield (99.2 % of theory in its Example 3) and very likely the larger industrial route, but
  its preferred form is continuous circulation in the product, it is strongly exothermic, it
  makes about 30 % hydrochloric acid as a co-product that needs its own market or treatment, and
  dimethyl disulfide has no library producer. A continuous Tier 2 entry on it is a separate
  case (recorded for a later entry, not this batch one).
- Methanesulfonic acid with phosgene (and a formamide catalyst), giving CO2 and HCl: phosgene-1
  exists in this library, but no open source with this acid's conditions was found and read
  (searched 2026-11-12); a batch phosgenation also adds a phosgene inventory to a small batch
  plant. Not chosen without a source.
- Sodium methanesulfonate with PCl5 or POCl3, the acid with PCl5 (SRC-1, Discussion): older
  laboratory routes with phosphorus wastes; no advantage at scale.
- Gas-phase sulfochlorination of methane with SO2 and Cl2 under light (SRC-9, not read): a
  continuous photochemical route, out of a batch entry's scope.

Assumptions: thionyl chloride from thionyl-chloride-1; methanesulfonic acid bought (no library
producer, D-012).

## D-002 Capacity, product and operating hours (2026-11-12)

Decision: 1000 t/a of distilled methanesulfonyl chloride, 7920 h/a (330 days of 24 h), on a
dedicated batch train (D-013). Product specification ASSUMED at least 99.5 wt% MsCl; modelled
99.95 wt% with 530 ppm thionyl chloride (D-007).

Reason: a fine-chemical scale of the order of the other batch entries (p-toluenesulfonyl-
chloride-1, acetyl-chloride-1); no open market or plant figure was used. No open source states a
purity for this route; 99.5 wt% is ASSUMED as a usual reagent grade.

## D-003 Batch basis, recipe and vessels (2026-11-12)

Decision: `process/recipe.yaml`: one batch makes 1203.4 kg of product; R-101 is the bottleneck
with a cycle of 9.531 h, 831 batches a year; one batch takes 13.29 h from the purge of R-101 to
the drained still. R-101: nitrogen purge 0.25 h, charge 0.5 h, warming on the jacket 0.75 h
(from the model, batch.heat_up), dosing 4 h, post-reaction 3.28 h to 0.99 conversion of the acid
(from the model), sampling 0.25 h, transfer 0.5 h. C-101: receive 0.5 h, evacuate 0.5 h, the
forerun 0.61 h and the product 1.65 h (boil-up times from the still's model at 120 kW), the
vacuum broken 0.5 h, the residue drained 0.5 h; C-101 is occupied 4.26 h of the 9.531 h cycle
(45 %). The flowsheet's flows are the recipe's year averages: batch size = 126.263 kg/h x 9.531 h,
so `cheme process recipe` reports no basis finding.

R-101 is sized by the recipe from the model: 1.10 m3 of batch at the end of the dosing in a
1.6 m3 vessel (69 % full, D 1.19 m), enamelled steel (thionyl chloride, HCl, SO2 and a strong
acid at 95 C). The vessel's metal is not entered (`metal_heat_capacity` left out): R-101 is not
cooled between batches (the crude leaves at 368.15 K and the next acid is charged within
0.75 h), so its metal ends each batch at the temperature it started from and takes no net heat;
the acid's heat-up from 298.15 K holds the batch's whole heat. The jacket's warming time is then
somewhat long (the warm vessel preheats the acid), a small conservative error in the cycle.

Assumptions: every duration not from a model ASSUMED; fill 0.8 and aspect ratio 1.2 usual for an
enamelled stirred vessel.

## D-004 Feeds and charge (2026-11-12)

Decision: methanesulfonic acid 99.5 wt% with 0.5 wt% water (ASSUMED anhydrous grade; SRC-1 used
a 95 % acid with 2 % water, whose water takes thionyl chloride); thionyl chloride dosed at 4/3
mol per mol of acid, the ratio of SRC-1 (2.0 mol on 1.5 mol), as fresh thionyl chloride
(thionyl-chloride-1, 99.7 wt%, modelled as pure) together with the recovered forerun. Per batch:
1043 kg acid, 1404 kg fresh thionyl chloride, 395 kg recycled forerun (78 wt% thionyl chloride,
22 wt% MsCl); 1.80 t dosed.

Reason: the source's ratio, with the excess recovered so that the fresh thionyl chloride per kg
of product is 1.167 kg against the stoichiometric 1.039 kg. The water of the source's acid would
cost 0.0268 mol of thionyl chloride per mol at 0.5 wt% (HYD); a wetter acid only consumes more.

Assumptions: the impurities of the thionyl chloride (sulfur chlorides, sulfuryl chloride) are not
modelled; scripts/balance.py sets the fresh feed so that the dose holds 4/3 mol per mol with the
recycle (D-006).

## D-005 Reactor R-101: semi-batch with an SO2/HCl vent, kinetics and heats (2026-11-12)

Decision: R101 is core's semi-batch (`reactor: semibatch`, isothermal at 368.15 K, the acid
charged at 298.15 K and warmed, `batch.heat_up`), dosing S4 at a constant rate over 4 h to 0.99
conversion of the acid, with two reactions:
- MSCL, CH3SO3H + SOCl2 -> CH3SO2Cl + SO2 + HCl, second order (first in each), k = 7.5e-5
  m3/(kmol s) at 368.15 K, Ea 60 kJ/mol, ASSUMED: sized so that the post-reaction after the 4 h
  dosing takes 3.3 h, about SRC-1's 3.5 h hold;
- HYD, SOCl2 + H2O -> SO2 + 2 HCl, a hundred times faster, ASSUMED (thionyl chloride takes
  water much faster than the acid).
SO2 and HCl leave the liquid as they form (`batch.vent`, fraction 1): no solubility data for a
Henry split were found, so none is kept dissolved. The vent carries the liquid's vapour
(`vent.vapour`: thionyl chloride and MsCl, Raoult, ideal liquid) through the vent condenser
E-102 at 263.15 K, whose condensate returns (D-010).

Heats: no open formation enthalpy of methanesulfonic acid or of MsCl was found, so MSCL's heat
cannot be derived; +65 kJ/mol (endothermic) is ASSUMED from two analogues computed with SRC-5's
formation enthalpies: one S-OH of liquid sulfuric acid to the S-Cl of sulfuryl chloride with
thionyl chloride, +66.6 kJ per S-OH, and acetic acid to acetyl chloride, +68.1 kJ/mol, each with
SO2 and HCl formed as gas. Most of the heat is the two gases' leaving; the reaction is driven by
their entropy. HYD's +50.3 kJ/mol is computed from the same data. The sign matters for the
hazard picture (D-011): an endothermic reaction cannot run away thermally, but its gas can.

Results (cheme process reactors): the acid is 86.8 % converted when the dosing ends; core's
accumulation of the dosed reactant is 0.297 then, of which the planned one-third excess is most
(0.396 mol thionyl chloride per mol of acid charged left, of which 0.13 still has acid to
react with). Per batch the vent takes 1177 kg: SO2 10.98 kmol, HCl 11.27 kmol, thionyl chloride
0.524 kmol and 0.001 kmol MsCl past E-102; the normal peak is 0.001682 kmol/s of SO2 and HCl at
1.1 h into the dosing (130.8 m3/h at E-102's 263.15 K outlet). The model's duty Q1, 41.60 kW year
average (heat into the batch): reaction 20.68, the doses warmed 3.78, the acid's heat-up 3.24, the
vapour the gas carries off 10.19 and the returning condensate re-warmed 3.72 kW.

Rejected: a Henry split (no data); taking the source's 71-83 % yield as a conversion (the losses
of a laboratory distillation of 1.5 mol are not a conversion); an exothermic sign (no basis).

## D-006 The balance method (2026-11-12)

Decision: `cheme process propagate --fill` computes the dose tank M101, the semi-batch R101 with
its vent, vapour and vent condenser, the stills ST101 and ST102 with the column, the forerun
splitter SP101, the residue mixer M103, the caustic dilution M102 and the scrubber A101 (a
conversion step), and writes the duties of R101 (Q1, Q2), the stills (Q3 to Q6) and the
scrubber (Q8). The thionyl chloride loop (T-101, R-101, C-101's forerun, T-102) is torn at the
recycle S3 and converged by propagate (Wegstein, core ADR 0060), never by hand.
`scripts/balance.py` gives what core does not compute: the feeds S1 and S2 for 1000 t/a and the
4/3 dose ratio with the recycle (the balance is linear in the feeds; a few passes of propagate
and the script converge it), the caustic S14 and its dilution water S15, the temperatures of the
distillate S9 and the residue S11 (bubble points at 4 kPa(a)), and the duties Q7, Q9 and Q10.
It cross-checks the dose ratio, the yield and the scrubber's model duty. The values it writes
are checked by the library's `scripts/check_balance_scripts.py` (library ADR 0027).

Results: S1 109.439 kg/h acid, S2 147.287 kg/h fresh thionyl chloride, S3 41.41 kg/h recycle,
S10 126.263 kg/h product; yield 97.2 % of theory on the acid and 89.0 % on the fresh thionyl
chloride. The yield on the acid is a model result and an ASSUMED upper bound: SRC-1 reports
71-83 % at 1.5 mol in the laboratory, and no open source gives a plant yield; the model loses
only the 1 % unconverted acid, the MsCl in the forerun purge and the residue.

## D-007 Batch still at 4 kPa(a): the stills' ends and the product (2026-11-12)

Decision: one batch still C-101 with its column K-101 (D-008) at 4 kPa(a), modelled as two
`still:` steps on the same charge: ST101 takes the forerun until thionyl chloride is 0.05 mol% of
the pot; ST102 takes the product until MsCl is 50 mol% of the residue. Raoult's law with the
vapour-pressure lines of materials.yaml (an ideal liquid, ASSUMED: no VLE data of these liquids
were found). Boil-up 120 kW on the jacket with the let-down steam (D-009); `still.heat_up` on
ST101.

Vapour pressures: thionyl chloride from NIST's Antoine line (SRC-2), used to 370 K; MsCl and
MSA have no open Antoine lines, so two-point Clausius-Clapeyron lines through PubChem's boiling
points (SRC-3) are ASSUMED: MsCl through 62 C at 18 mmHg and 161 C at 730 mmHg (it gives 20.8
mmHg at 65 C against SRC-1's 64-66 C at 20 mmHg, and 0.23 kPa at 20 C against the ICSC's 0.27
kPa; 2.4 mmHg at 25 C against 3.09 mmHg), MSA through 167 C at 10 mmHg and 4.28e-4 mmHg at 25 C.
The slope of the MsCl line, 45.2 kJ/mol, is its heat of vaporization at 345-365 K; HSDB's 349
kJ/kg (40.0 kJ/mol, temperature not stated) is 12 % lower and would give a smaller reboiler duty.

Why 4 kPa(a): the pot must stay below SRC-1's 115 C (388.15 K) limit for the heated wall (Note
5: local overheating chars and decomposes the product). At 4 kPa the forerun ends with the pot at
346 K and the product cut at 362 K, and the jacket's steam condenses at 382.44 K, below the
limit throughout. The forerun's thionyl chloride condenses at about 270 to 280 K on brine
(E-103); the product at 346 K on cooling water (E-104).

Results (cheme process stills, per batch): the charge 1665 kg (20 mol% thionyl chloride); the
forerun 438 kg (78.4 wt% thionyl chloride, 21.6 wt% MsCl), 0.61 h; the product 1203.4 kg, 99.95
wt% MsCl with 530 ppm thionyl chloride, recovering 99.0 % of the MsCl in the stripped crude, 1.65
h; the residue 22.7 kg (50 mol% each of MSA and MsCl). The purity is an upper bound of the
shortcut on an ideal liquid (the shortcut never exceeds a rigorous column in purity, core ADR
0061); no source states it.

The crude arrives at 368.15 K, far above its bubble point at 4 kPa(a) (301.8 K): as C-101 is
evacuated, it flashes thionyl chloride into E-103 until it reaches it. Core's still models no
flash of a charge above its bubble point (L-4): `still.heat_up` gives no heat-up, and the
crude's sensible heat down to its bubble point, Q10 4.02 kW year average, is a hand duty on the
brine (scripts/balance.py).

Rejected: atmospheric distillation (the product boils at 434 K, above the 388 K limit); a
continuous column (a batch entry; 2.6 t a batch).

## D-008 Column K-101, the forerun's recycle and the residue (2026-11-12)

Decision: K-101, a packed column of 8 theoretical stages (the still included), at a constant
reflux ratio of 1 for the forerun and 0.5 for the product, on core's batch rectification
(Diwekar's shortcut, `still.column`, ADR 0061), with the condensers on their own energy streams
(`condenser_port`). The forerun goes to the receiver T-102; nine tenths return to the dose tank
T-101 (S3), a tenth is purged with the residue (S12) so that impurities of the thionyl chloride
do not build up in the loop. The residue and the purge go to the waste drum D-101 and to
hazardous-waste incineration (S13, 55 g per kg of product). The residue drains at the still's end
temperature, 362 K, under nitrogen; it cools in the drum (its sensible heat to 298 K, about 0.06
kW year average, goes to air: excluded as negligible).

Reason: SRC-1 used only a 10 cm Vigreux column (a few stages): the forerun of a plant takes MsCl
with it (7.2 % of the MsCl charged), which the recycle brings back. 8 stages and the reflux
ratios are ASSUMED: they hold the product's thionyl chloride below 0.1 wt% at a modest boil-up
time. The purge share is ASSUMED (no impurity data).

Rejected: recycling the residue (it holds the unconverted acid and decomposition products of
the hot pot; with 22.7 kg a batch not worth the risk at concept stage).

## D-009 Utilities and heat (2026-11-12)

Decision:
- LP steam let down to 140 kPa(a), condensing at 382.44 K (IAPWS-IF97, SRC-5): R-101's jacket
  and heating loop (Q1) and C-101's jacket (Q3, Q5). Its temperature stays below the 388.15 K
  limit for the product's heated wall (SRC-1, Note 5). Q1 41.60 kW, Q3 7.64 kW, Q5 20.76 kW
  year averages, all from core's models.
- R-101's heating: the reaction is endothermic (D-005), so the batch needs heat throughout the
  dosing: from R101's conversion profile (core's semi-batch, by hand; tests/test_methanesulfonyl_chloride_1.py repeats it) the reaction
  and the dose's warming need 62.4 kW at 1.13 h into the dosing (51 kW on average over it), and
  the vapour's evaporation with the condensate's re-warming about 18 kW more over the dosing and
  the post-reaction (the model's terms 10.19 + 3.72 kW year average over the 7.28 h they run in
  the 9.531 h cycle). R-101's jacket gives only 14.9 kW at the charge (3.48 m2) to 20.6 kW full
  (4.8 m2) at U 300 W/(m2 K) and 14.3 K between the steam and the batch; a hotter steam is
  barred by the wall limit. So the batch is pumped through an external heater E-105 on the same
  steam, about 12 m2 for 80 kW at U 500 W/(m2 K), part of R-101's heating (no flowsheet step: its
  heat is in Q1). Core's recipe checks a jacket's cooling at the peak, not its heating (L-3):
  this check is by hand, and the recipe's warming time uses the jacket alone (conservative).
- Cooling water 298.15/308.15 K: the product condenser E-104 (Q6 20.76 kW, from the still's
  model), the product cooler E-101 (Q7 1.73 kW, the distillate from its bubble point 345.8 K to
  308.15 K, 10 K above the water's supply), the scrubber's cooler (Q8 101.28 kW from the
  conversion model: the neutralisation heats of D-010 less the gas's and liquor's warming, with
  the pump's and fan's power) and the caustic dilution cooler (Q9 11.25 kW: 50 wt% caustic
  diluted to 15 wt%, -20 kJ per mol NaOH ASSUMED, the order of the published integral heats of
  solution, less what warms the diluted caustic from 298.15 K to 308.15 K, where its cooler
  leaves it, 10 K above the water's supply). Every cooler keeps the 10 K minimum approach: the
  scrubber's liquor at 308.15 K leaves its cooler 10 K above the water's supply and returns to
  the column; the column's liquor rise sets the hot end.
- Refrigerated brine 253.15/258.15 K: the vent condenser E-102 (Q2 16.04 kW, from the vent model:
  condensation 9.69, the vapour cooled 3.91, the gas cooled 2.44 kW), the forerun condenser E-103
  (Q4 7.64 kW from the still's model) and the crude's flash into E-103 (Q10 4.02 kW). The brine
  stays 13 K above MsCl's freezing point (240.15 K, SRC-3), and thionyl chloride freezes far
  lower, so nothing freezes on the tubes.
- Power (ASSUMED from the recipe's times, year averages): P1 2.3 kW (R-101's agitator 1.5 kW,
  about 1 kW per m3 of vessel, the whole cycle, and E-105's pump 1.1 kW over the dosing and the
  post-reaction, 7.28 of the 9.531 h cycle: 1.5 + 1.1 x 0.76), P2 1.65 kW (C-101's agitator 1.1
  kW over its 4.26 h and a 4 kW dry vacuum pump over the evacuation and the two cuts, 2.76 h:
  1.1 x 0.45 + 4 x 0.29), P3 2.6 kW (the scrubber's pump 1.5 kW and fan 1.1 kW all year).
- Small flows left out, each with its number: the forerun warms from its condensing temperature
  (about 275 K) to 298 K in T-102 by ambient heat, about 0.2 kW; the residue's sensible heat in the
  drum, about 0.06 kW (D-008); heat losses of the vessels and lines, not estimated.

Per kg of product (lca/inventory.csv): steam heat 0.554 kWh, cooling water 1.069 kWh, brine
0.219 kWh, power 0.052 kWh.

## D-010 Vent, vent condenser and caustic scrubber (2026-11-12)

Decision: R-101's gas leaves saturated with the liquid's thionyl chloride and MsCl at 368.15 K
(`vent.vapour`) through E-102 on brine, gas out at 263.15 K (10 K above the brine's supply),
condensate back to R-101 (`vent.condenser`, `returns: vessel`); E-102 condenses 94 % of the
thionyl chloride vapour and nearly all the MsCl. The gas past it (S6: SO2 1.152, HCl 1.183,
thionyl chloride 0.055 kmol/h) goes with the vacuum pump's discharge and the tanks' breathing to
the scrubber A-101, a packed column with circulating 15 wt% caustic, cooled to 308.15 K. A101 is
a conversion step taking up everything: HCl to NaCl, SO2 to sodium sulfite (two NaOH, the
caustic in excess), thionyl chloride to sulfite and two chlorides, MsCl to the methanesulfonate.
Caustic 1.10 times what the gas takes, from chlor-alkali-1's 50 wt% diluted with process water
to 15 wt% (ASSUMED, a usual scrubbing strength that keeps the sulfite in solution); spent liquor
about 12.6 wt% sodium sulfite, 6.2 wt% sodium chloride and 1.2 wt% NaOH, 9.59 kg per kg of
product, to wastewater treatment (the sulfite oxidised there).

Heats (reactions.yaml NEU_*, ASSUMED orders of magnitude: an acid gas's heat of solution plus
about -56 kJ per mol of hydroxide neutralised; no open table of aqueous formation enthalpies was
read): -130 (HCl), -160 (SO2), -400 (thionyl chloride), -150 (MsCl) kJ/mol.

Toxic gas and the scrubber's failures (the reason the dosing is interlocked, D-014):
- loss of the scrubber's caustic (pump trip, empty tank) or its exhaustion sends SO2 and HCl to
  air at up to the normal peak: caustic flow and strength (conductivity) are permissives of the
  dosing, and the caustic for at least one whole batch (3.1 t of 50 wt%) is in T-201 before the
  dosing starts;
- loss of brine on E-102 sends thionyl chloride vapour (178 kPa over the pure liquid at 368 K) to
  the scrubber, where it hydrolyses to more SO2 and HCl and loads the caustic: brine flow and the
  gas outlet temperature are permissives;
- water ingress: the absorption of SO2 and HCl in caustic pulls a vacuum that could draw liquor
  back up the vent line into thionyl chloride, which reacts at once with gas release (each kg of
  water gives 5.0 m3 of SO2 and HCl at 368 K): a nitrogen-padded seal pot and a vacuum breaker on
  nitrogen on the vent line, no direct liquid path from A-101 to R-101. A jacket leak at 140
  kPa(a) steam also lets water into R-101 (D-014).

## D-011 Thermal and gas-release screening, the rate sensitivity (2026-11-12)

Decision: `cheme process reactor-hazards` with `hazard.mtt` 388.15 K and `hazard.vent_capacity`
400 m3/h (D-014); k/10 and k/100 on scratch copies of the folder (the rate constants of both
reactions divided, each copy propagated, its reactors, recipe and screening run); no TD24 (none
is estimated: only calorimetry gives one).

MTT: SRC-1 limits the heated wall to 115 C at the end of the distillation because overheating
decomposes the product (to sulfur oxides and HCl on full decomposition, SRC-3; no onset
temperature or TD24 is open). That limit is taken as the MTT. The reaction mass's own bubble
point at 101.3 kPa(a) never falls below 390.6 K over the base batch (its lowest at the end of
the dosing, 27 mol% thionyl chloride; Raoult with materials.yaml over core's profile of the
batch's content), above the MTT. Core's default MTT, the
normal boiling point of thionyl chloride (348.75 K), is one component's, below the batch
temperature; the mixture is not at its boiling point (L-2).

Results (base): T_p 368.15 K, dT_ad 0 K (both reactions endothermic: core gives MSCL's dT_ad as
-204 K), accumulation 0.297 at the end of the dosing, MTSR 368.15 K against the MTT 388.15 K.
Criticality without a TD24, as core's `criticality()` gives them for MTSR < MTT: class 1 if the
TD24 lies above 388.15 K, 2 if between 368.15 and 388.15 K, 5 if below 368.15 K. The gas
release at the MTSR is nil (a cooling failure does not raise the temperature, and the
screening's worst moment has nothing to react).

Rate sensitivity (scratch copies; k/10 is the base at about 329 K, k/100 at about 298 K for Ea
60 kJ/mol, so they also stand for a dosing into a batch that is too cold):

| case | accumulation at the end of the dosing | post-reaction to 0.99 | vent peak (SO2 + HCl) | E-102's energy per batch | content at the end of the dosing |
|---|---|---|---|---|---|
| k (base) | 0.297 | 3.28 h | 0.001682 kmol/s, 182.9 m3/h at 368 K | 153 kWh | bubble point 390.6 K (27 mol% thionyl chloride) |
| k/10 | 0.683 | 51.1 h | 0.000760 kmol/s, 82.6 m3/h | 555 kWh (3.6 x) | bubble point 375.6 K (45 mol%), below the MTT |
| k/100 | 0.935 | about 534 h | 0.000211 kmol/s, 22.9 m3/h | 1108 kWh (7.2 x) | bubble point 370.6 K (53 mol%), 2.4 K above T_p |

The bubble points are the lowest over each batch (at the end of the dosing), Raoult with
materials.yaml over core's profile of the content. So slower kinetics lower the vent's peak but
leave the thionyl chloride in the pot: at k/10 the cycle is not feasible, and at k/100 the batch
is within a few kelvin of boiling at 368 K and refluxes thionyl chloride through E-102; in both
the MTSR stays T_p (endothermic).
The endothermic reaction never heats itself; its hazard is the gas an accumulated dose releases
once it reacts (D-014).

## D-012 Preliminary gate-to-gate LCI (2026-11-12)

Decision: `lca/lca.yaml` with every exchange per kg of product from the flowsheet's year
averages, written by `cheme assess lca --write` after the last edit; the backgrounds unmapped
(`missing:` naming the activity) except the links in `lca/mappings.yaml`, kg for kg: thionyl
chloride to thionyl-chloride-1 (99.7 wt%, product:SOCL2, the grade the feed takes), caustic soda
50 wt% to chlor-alkali-1 (product:NAOH, per kg of solution), the nitrogen consumable to asu-1,
the steam as heat (shared steam-heat). Per batch, 11.3 kg of nitrogen (9 Nm3: R-101 purged with
two volumes, C-101 purged and its vacuum broken, the receivers blanketed), ASSUMED. No rinse: the
train is kept dry.

Methanesulfonic acid has no library producer: a gap with its proxy recorded, not linked (the
oxidation of dimethyl disulfide or methyl mercaptan, or methane with SO3 in oleum; 0.839 kg MSA
per kg of MsCl at the stoichiometric floor, 0.867 kg modelled). Process water, power, cooling
water, brine, the residue's incineration and the liquor's treatment are gaps naming their
library utilities. Per kg of product: 0.867 kg acid, 1.167 kg thionyl chloride, 2.583 kg caustic
50 wt%, 6.03 kg water, 9.4 g nitrogen; 0.055 kg residue, 9.59 kg spent liquor. The tail gas and
the tanks' breathing are declared exclusions. No allocation: one product.

## D-013 Dedicated train (2026-11-12)

Decision: one dedicated train (library ADR 0035): R-101 and C-101 serve only this product; no
campaign changeover or cleaning between products is counted.

## D-014 Vent capacity and the design findings (2026-11-12)

Decision: `hazard.vent_capacity` 400 m3/h at R-101's 368.15 K and 101.3 kPa(a), the design of
R-101's vent line, E-102 and A-101: the normal peak of SO2 and HCl, 182.9 m3/h, with the liquid's
vapour at its largest share over the batch (0.432 of the gas, cheme process reactors) is 322
m3/h, rounded up.

Cases against it:
- normal operation and the slower-kinetics cases (D-011): within it (k/10 82.6 m3/h);
- a cooling failure: nothing (endothermic);
- **design finding 1, an accumulated dose**: if the heating fails (steam lost, E-105 stopped)
  while the dosing goes on, the batch cools (the reaction and the cold dose both take heat), the
  reaction slows and the thionyl chloride accumulates; when the heating returns it reacts at
  once. A stoichiometric dose accumulated unreacted on the whole acid and warmed back to 368.15 K
  starts at about 0.0118 kmol/s of gas, 1280 m3/h, 3.2 times the vent; the content at the end of
  the k/10 dosing warmed to the base rate starts at about 680 m3/h, 1.7 times. Measures to assess
  in basic engineering: dosing permissive on R-101's temperature (above about 360 K), on the
  steam's flow and on the off-gas flow through E-102 (gas confirms the reaction, as an
  initiation check), a dose-rate limit, and a relief study for the blocked-vent and
  accumulated-dose cases;
- **design finding 2, water ingress**: the margin above the normal peak, 78 m3/h, is the gas of
  about 15 kg/h of water reaching the thionyl chloride; a jacket leak or a suck-back of caustic
  (D-010) can exceed it: jacket-leak detection (condensate conductivity) or a non-aqueous heating
  medium, and the anti-suck-back measures of D-010;
- **design finding 3, R-101's heating**: the jacket cannot hold the batch at 368 K against the
  endothermic dosing (D-009); without E-105 the batch cools and finding 1 follows in normal
  operation.

The TD24 of the crude and of the residue (MsCl, MSA and their decomposition at the hot wall) is
an open input for calorimetry (DSC/ARC), never estimated here.

## Method and dependency table

| result | method | inputs |
|---|---|---|
| R101's conversion, vent, vapour, E-102, Q1, Q2 | core semi-batch with vent, vapour and vent condenser (ADRs 0050, 0054, 0062, 0063) | ASSUMED rate laws and heats (D-005), materials' vapour pressures (SRC-2, SRC-3) |
| the forerun and product cuts, Q3 to Q6 | core batch still with column (ADRs 0055, 0061, 0063) | Raoult (ASSUMED ideal), 8 stages and reflux ratios ASSUMED (D-007, D-008) |
| the recycle S3 | core tear (ADR 0060) | the purge share ASSUMED |
| A101, Q8 | core conversion step | ASSUMED neutralisation heats (D-010) |
| feeds, caustic, S9 and S11 temperatures, Q7, Q9, Q10 | scripts/balance.py | capacity, ratios, D-009, D-010 |
| batch size, cycle, vessel, vent per batch | `cheme process recipe` (ADRs 0051, 0052, 0057) | durations ASSUMED (D-003) |
| screening and sensitivity | `cheme process reactor-hazards`, scratch copies | D-011, D-014 |
| R-101's heating demand | core's semi-batch profile, by hand | D-009 |

## Core features used (core 1.11.0)

- `reactor: semibatch` with `batch.dosing`, `target`, `heat: isothermal` and `heat_up: true`
  (ADRs 0050, 0063); `batch.vent` with `vapour:` and `condenser:` on its own energy stream Q2
  (ADRs 0054, 0062); `energy_port` so the model writes Q1 (ADR 0059).
- `hazard.mtt` and `hazard.vent_capacity` with their basis (ADR 0058).
- `still:` with `still.column` (constant reflux), `condenser_port`, `still.heat_up` and a
  `residue` end; two steps on one charge for the forerun and the product (ADRs 0055, 0061, 0063).
- `tears:` with Wegstein for the thionyl chloride recycle (ADR 0060).
- A conversion step for the scrubber that writes its duty Q8 (ADR 0059).
- `process/recipe.yaml` with a unit procedure over three steps (`units:`), model times
  (`from:`), vessel sizing and the jacket check (ADRs 0051, 0052, 0057); a per-batch consumable
  in lca.yaml (ADR 0053).

## Core limits hit (each a candidate core issue)

- L-1: no property package covers methanesulfonic acid and MsCl (no ideal-gas or formation data):
  the reactions' heats are given, not derived (`cheme process reactors` reports them missing).
- L-2: the screening's default MTT is the lowest normal boiling point of a component of the
  charge and the dose (thionyl chloride, 348.75 K), not the mixture's bubble point; here it lies
  below T_p and would report a boiling batch. And for an endothermic gas-forming reaction the
  screening's MTSR and gas release are nil: the release of a dose accumulated at a lower
  temperature (a heating failure) is not screened; it is a hand case here (D-014).
- L-3: the recipe checks a jacket's cooling at the model's peak but not its heating of an
  endothermic semi-batch; R-101's heating demand is computed by hand from the model's profile
  (D-009).
- L-4: the batch still models no flash of a charge above its bubble point at the still's
  pressure: the crude's flash into E-103 (Q10) is a hand duty.
- L-5: the scrubber is a conversion step (no absorption or electrolyte model), and a mixer has no
  heat of dilution: the caustic's dilution heat (Q9) is a hand estimate.

## Open inputs

- Kinetics and heat of the reaction (reaction calorimetry with off-gas measurement); the TD24 of
  the crude, the product and the residue (DSC/ARC).
- VLE of thionyl chloride, MsCl and MSA; the solubility of SO2 and HCl in the crude.
- Plant yield and purity (only a 1.5 mol laboratory example is open).
- The relief study of R-101 (D-014), the heating loop E-105's design, the scrubber's design.
- Methanesulfonic acid's background (no library producer).
