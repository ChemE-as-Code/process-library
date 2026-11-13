# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Copper(I) chloride (cuprous chloride, CuCl) by the wet chlorination of copper in a sodium
chloride brine and precipitation by dilution, issue ChemE-as-Code/process-library#143. Concept
stage: design basis, batch recipe, balanced BFD/PFD with two converged recycles, thermal
screening with a rate sensitivity and a preliminary gate-to-gate LCI. Out of scope here: P&IDs,
layout, HAZOP, TEA, datasheets.

Starting point (2026-11-06): library `main` at 7f2292c6, which pins cheme-as-code 1.9.0
(314642c). The NBS pilot (`n-bromosuccinimide-1`), `carbon-tetrabromide-1` (precipitation and a
filter-dryer over several steps), `p-toluenesulfonyl-chloride-1` (crystallizers with spectators,
model duties, the vent capacity) and `sodium-azide-1` (recycle tears) are the templates.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents' text of the document; no paragraph numbers, so the locator is
the part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US3030178A, Schering AG, 1962: continuous production of cuprous chloride, https://patents.google.com/patent/US3030178A/en | description and Example 1: a vertical tube filled with scrap copper, fed at the top with a brine of 300 g/L NaCl and 0.5 g/L HCl; chlorine (with some air) fed 1.1 m below the surface, absorbed in the tube; the lower part held just below the boil reduces the copper(II) to copper(I) on the metal; the outflow is colourless and holds about 155 g/L CuCl, which does not crystallise at room temperature; stabilised with a little sodium sulfite; CuCl can be precipitated by adding water; the chloride liquors can be reused; fresh copper added every 30-60 min; claims 1-6 | read; patent, facts only | D-001, D-004, D-005, D-006 |
| SRC-2 | US3121609A, Buckland and Rolland (American Cyanamid), 1964: process for preparing cuprous chloride, https://patents.google.com/patent/US3121609A/en | description: copper oxidised with air in acidified ammonium chloride at 80-100 C, then reduced with more copper under nitrogen; CuCl recovered by diluting with 1-15, preferably 5-10, volumes of (cold) water, filtered, washed and dried; Examples 1 and 3 dilute with seven volumes; about 1 % CuCl2 added speeds the start; no yields | read (OCR text, some numbers garbled); patent, facts only | D-001 (variant), D-006 |
| SRC-3 | US4582579A, Hughes Aircraft, 1986: method for preparing cupric-ion-free cuprous chloride, https://patents.google.com/patent/US4582579A/en | description: CuCl2 0.5-1.2 mol/L in about 12 N HCl reduced by copper at 40-55 C under nitrogen; 98-99.5 % of the stoichiometric copper, or a separate pre-reaction with about a 50 % excess of copper turnings, until 0.5-2 % of the copper(II) is left; background: the conventional finish dilutes with deoxygenated water, washes with chilled deoxygenated water and vacuum-dries; the supernatant siphoned off the precipitate; CuCl very soluble in HCl, slightly in water; green impurities are copper(II) | read; patent, facts only | D-004, D-005, D-006, D-008 |
| SRC-4 | CN1696062A, 2005: method for producing cuprous chloride from spent copper chloride etching solution, https://patents.google.com/patent/CN1696062A/en | claim 1 and Examples 1-4: SO2 reduction at 70-80 C, the crystals washed with dilute HCl of pH 1-2.5, then with ethanol, dried at 80-110 C; product at least 98 wt% CuCl, at most 1 % copper(II) salts; mother liquor and washes neutralised to a copper sludge, the ethanol recovered by distillation | read (machine translation); patent, facts only | D-002 (specification), D-007, D-008, D-010 |
| SRC-5 | US4308239A, 1981: obtaining copper(I) chloride from ores with acetonitrile, https://patents.google.com/patent/US4308239A/en | description: CuCl dissolves about 0.24 g/L in water at 25 C and only about 1 g/L with 10 g/L of excess chloride (as NiCl2) at 20 C; Table III: 0.4 mol/L CuCl in 2.0 mol/L NaCl with 0.5 mol/L HCl at 25 C (a solution, so the solubility there is at least 0.4 mol/L); oxygen slowly oxidises copper(I), the work was done under nitrogen | read; patent, facts only | D-006, D-011 |
| SRC-6 | Wikipedia, Copper(I) chloride, https://en.wikipedia.org/wiki/Copper(I)_chloride | infobox (citing the CRC Handbook): 0.0047 g/100 mL in water at 20 C, Ksp 1.72e-7, density 4.14 g/cm3, mp 423 C; text: soluble in concentrated HCl as a chloro complex; slowly disproportionates in water; air oxidation gives basic copper(II) chloride, why samples turn green | read; CC BY-SA, facts only | D-006, D-008, D-011 |
| SRC-7 | PubChem CID 62652, copper(I) chloride; CID 23978 (copper), CID 24014 (copper(II) chloride) | identity (formula, CAS, InChIKey) | read (PUG REST) | registry, materials |
| SRC-8 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADRs 0050, 0058) | method reference, no data taken | D-011 |
| SRC-9 | processes/chlor-alkali-1, hydrogen-chloride-1, ethanol-1, asu-1 (this library) | dry chlorine gas, hydrochloric acid 33 wt%, anhydrous ethanol, gaseous nitrogen | library, internal | feed links (D-004, D-012) |
| SRC-10 | Property data of core's environment: the `chemicals` 1.5.2 package (open-source, MIT; the version core pins; its packaged CRC Handbook tables: `chemicals.heat_capacity.CRC_standard_data` for standard enthalpies of formation and heat capacities, `chemicals.miscdata.CRC_inorganic_data` and `CRC_organic_data` for densities and boiling points, `chemicals.phase_change.Hvap_data_CRC` for heats of vaporisation, `chemicals.Tb`; `chemicals.safety` `T_flash`, `LFL` and `T_autoignition` for ethanol, from its tables of IEC 60079-20-1 (2010) and NFPA 497 (2008), licensed standards not read here), and CoolProp's IAPWS water (latent heat at 333 K, saturation of LP steam, viscosity) | per component in `process/materials.yaml`; the heats of reaction (`process/reactions.yaml`); the dryer's latent heats (D-008); ethanol's flash point 285.15 K, LFL 3.1 vol%, autoignition 673 K (D-011) | open-source packages queried (2026-11-06); single values, facts only; not open data (library ADR 0037). The CRC values come from the tables packaged in `chemicals`, not from the printed handbook (the CRC Handbook of Chemistry and Physics, 2014 edition as chemicals cites it; a licensed book, not read here) | materials, D-005, D-008, D-009, D-011 |
| SRC-11 | Ullmann's Encyclopedia of Industrial Chemistry, Copper Compounds (doi:10.1002/14356007.a07_567) | - | not read (licensed); named by the route scouting and by Wikipedia as the source of the industrial routes | lead only, nothing taken |
| SRC-12 | Fritz, J. J. (1980) Chloride complexes of copper(I) chloride in aqueous solution, J. Phys. Chem. 84, 2241; Kale, Tamhankar and Chaudhari (1979) J. Chem. Eng. Data 24, 110 (CuCl in HCl) | - | not read (paywalled; titles and metadata only) | leads for the solubility (open input, D-006) |
| SRC-13 | GB1284110A, Norddeutsche Affinerie, 1972 | abstract: copper and chlorine in a CuCl melt, continuous | abstract only | D-001 (rejected route) |

Searched and not found openly (2026-11-05/06): kinetics or calorimetry of the chlorination of
copper in a brine, a table of CuCl's solubility in NaCl solutions against chloride and
temperature (the measured data, SRC-12, are paywalled), the heats of solution of the copper(I)
chloro complexes, a plant's specific consumptions and a market volume.

## D-001 Route and boundary (2026-11-06)
Decision: the wet chlorination of copper in a sodium chloride brine (SRC-1), run as a batch on a
dedicated train (D-013):
- T-100: a brine of about 300 g/L NaCl and 0.5 g/L HCl (SRC-1's feed brine) made up from salt,
  water, 33 wt% hydrochloric acid and a tenth of the decanted mother liquor;
- R-101: the brine charged over copper (fresh copper and the heel kept from the last batch),
  heated to 353 K, chlorine dosed below the surface and absorbed:
  Cu + Cl2 -> CuCl2, then CuCl2 + Cu -> 2 CuCl on the excess copper, net 2 Cu + Cl2 -> 2 CuCl,
  the CuCl held dissolved as chloro complexes; the liquor cooled to 308 K and drawn off through
  the bottom strainer, the heel staying;
- P-101: the liquor run into about 7 volumes of deoxygenated water (SRC-2): CuCl precipitates,
  settles, and the clear liquor is decanted (SRC-3);
- F-101: the thickened slurry filtered, reslurry-washed with dilute hydrochloric acid of pH 1,
  displacement-washed with ethanol (SRC-4) and vacuum-dried at 333 K under nitrogen.
Boundary feeds: copper, chlorine, sodium chloride, hydrochloric acid 33 wt%, ethanol, process
water, electricity, LP steam, nitrogen (per batch); returns: cooling water, chilled water;
outputs: dried CuCl, a copper-bearing brine to copper recovery and wastewater treatment, spent
ethanol to solvent recovery.
Reason: the scouting (issue #143) recommends this route for a batch entry; SRC-1 is the only open
description with a brine, a copper(I) concentration and the dilution step; the patents that
describe batch reductions (SRC-2, SRC-3) and the work-up (SRC-3, SRC-4) fill in the batch and the
isolation. Chlorine links the library's chlor-alkali-1.
Rejected:
- copper and chlorine in a CuCl melt at 450-900 C (SRC-13, Wikipedia): the large-tonnage
  catalyst route, but continuous and molten, not a batch entry;
- copper oxidised by air in acidified ammonium chloride (SRC-2): a gas dose of air leaves
  nitrogen and unreacted oxygen to a vent that no reaction forms a gas for (core's vent takes only
  formed gases, L-3); a variant; its much higher CuCl loading would cut the dilution loss (D-006);
- CuCl2 in 12 N HCl reduced by copper (SRC-3): needs purchased CuCl2 (no library producer) and
  loses its HCl to the mother liquor;
- reduction of a copper(II) salt by SO2 or sulfite (SRC-4, scouting): a sulfate/sulfite route with
  its own wastes; a variant once an SO2 entry is linked;
- copper recovery from the mother liquor inside the boundary (cementation on iron, or the liquor
  recycled after evaporation): see D-006 and D-010.

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: 300 t/a dried CuCl, 7920 h/a (330 days of 24 h), ASSUMED. Modelled product: 99.79 wt%
CuCl, 0.16 wt% ethanol, 0.04 wt% water, NaCl and copper(II) below 0.01 wt% each (D-007, D-008).
**The 99.8 wt% is an ASSUMED upper bound, not a specification**: the model has no oxidation of
CuCl by air or water (D-011), no inclusion of brine in the crystals and no fines of copper metal
(they are taken by the bag filter, D-004). The only open specification (SRC-4) is at least 98 wt%
CuCl and at most 1 % copper(II); the product specification is an open input.
Reason: no open market or plant figure was found; CuCl is a catalyst and reagent (organic
synthesis, acrylonitrile and silicone catalysts, the fungicide copper oxychloride) and the wet
batch route serves the smaller grades. The LCI is per kg and does not depend on the scale; the
batch size does (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 355.0 kg of dried CuCl (stream S29); the recipe
(`process/recipe.yaml`) has three unit procedures:
- CHLORINATE on R-101, one vessel over M101, E101, R101, E102 and SS101 (`units`, core ADR
  0057): nitrogen purge 0.25 h, charge 0.5 h, heat 294.9 -> 353.15 K 0.83 h (from the jacket),
  chlorine dosed 3 h and post-reaction 1 h (R101's model), cool 353.15 -> 308.15 K 2.79 h
  (jacket), draw-off through the strainer 1 h: 9.37 h;
- PRECIPITATE on P-101 over CR101 and DC101: receive the liquor and hold 1 h, decant and send
  the thickened slurry 1 h, rinse 0.5 h, the next dilution water 0.5 h, its sparging with
  nitrogen 0.5 h: 3.5 h;
- ISOLATE on F-101 over F101, W101, F102, M103, F103 and D101: filtrations 0.54, 0.45 and 0.23 h
  (Ruth, from the filters' filtration data), the acid reslurry 0.5 h, the ethanol 0.25 h, drying
  4.62 h (D101's drying rate on 2.5 m2), discharge 1 h: 7.59 h.
R-101 is the bottleneck: cycle 9.37 h, 846 batches in 7920 h; one batch takes 16.95 h from the
purge to the discharge. The flowsheet's flows are the recipe's year averages: 355.0 kg x 845.6 / 7920 h = 37.90 kg/h of S29 (no `cheme.recipe-basis` finding). The feeds were scaled by hand to
that rate and the batch size set to rate x cycle (L-7).
Vessels (fill 0.8, H/D 1.2, 1.0 for the filter-dryer, ASSUMED): R-101 5 m3 as core sizes it
from R101's model (3.64 m3 at the end of the dosing, 73 %); its jacket (U 300 W/(m2 K)
glass-lined, 10.6 m2 wetted at the charge) removes 158 kW against the model's peak 57.8 kW, on
the cooling water's log-mean temperature: water at 298/308 K against the liquor at 353.15 K
gives (55 - 45) / ln(55/45) = 49.83 K, so the coolant temperature entered is 303.32 K, not the
supply's 298.15 K. The cool-down to 308 K takes its time from the same constant 303.32 K; near
308 K the return water cannot stay at 308 K, so that time is optimistic at its end (L-6). P-101
40 m3, given (core sizes no vessel for a crystallizer): one batch's slurry is 28.5 m3 (the model's ideal-mixing volume of S13 x 9.37 h), 71 %. F-101 1 m3, as core sizes it from the largest
batch content of its steps (0.78 m3, the thickened slurry), heated area 2.5 m2 (jacket and a
heated agitator, ASSUMED).
Reason: core ADR 0051 puts the batch basis in one place; the dosing, reaction, heating, cooling,
filtration and drying times come from the models, so a change of the kinetics, the jacket, the
cake or the drying rate changes the cycle. Settling and decanting in P-101 (DC101) keeps the
filter-dryer at 1 m3: without it F-101 would take the whole 28 m3 of slurry.
Dosing time: 3 h ASSUMED for the absorption of the chlorine (about 22.4 m3/h of gas at 353 K into
3.6 m3); the jacket would allow a faster dosing (peak 57.8 kW against 158 kW; `cheme process
recipe`: 3.643 m3, 57.77 kW, 157.9 kW, 10.6 m2).

## D-004 Feeds, charge and the recycles (2026-11-06)
Decision: per batch 164.1 kg of chlorine, 293.1 kg of fresh copper, 907 kg of salt, 10.5 kg of
33 wt% hydrochloric acid (brine and wash), 186 kg of ethanol and 25.7 t of process water (of it 24.8 t of dilution water). The feeds are the sources' ratios scaled to 37.90 kg/h of S29 (every
outlet scales with them):
- brine S4: 0.249 kg of NaCl per kg of NaCl and water (about 296 g/L at a density of 1.19 kg/L,
  SRC-1's 300 g/L), 0.47 g/L HCl (SRC-1's 0.5 g/L);
- copper: the fresh copper S5 is the copper consumed (2 mol per mol of chlorine less the copper(II)
  left) and the fines; the heel S6 is what R-101's strainer keeps, 99.8 % of the copper left, wet
  with 0.1 kg of liquor per kg; it converges at 0.251 kmol per hour of flows, 51 % of the 0.492
  kmol of copper consumed (SRC-3's pre-reaction runs with a 50 % excess of copper). The 0.2 % that
  passes as fines is taken by the bag filter X-101 (SS102) and goes with the copper-bearing
  effluent;
- the recycles: the heel S6 and a tenth of the decanted mother liquor S17, which makes up most of
  the next brine's water (290 of 324 kg/h) and returns its NaCl, HCl and dissolved copper (SRC-1:
  the chloride liquors can be reused). Both are core's tears (`tears:`, core ADR 0060),
  converged by Wegstein's method in 66 iterations to 1e-6 kg/h; no recycle is converged by hand.
  The split is ASSUMED: more than a tenth would bring more water than the brine can take (the
  rest is the dilution water, which must leave).
Reason: the patents' ratios; chlorine, the acid and the ethanol from the library (SRC-9). Copper
(cathode granules or clean scrap) and the salt are merchant; no library process makes them
(D-012).
The fresh feeds hold the converged loop at the stated rate; core has no design specification on a
feed (L-7), so they were set by hand.

## D-005 Reaction model, kinetics and heats (2026-11-06)
Decision:
- R101 is `reactor: semibatch` (core ADR 0050) at 353.15 K, isothermal: the charge S7A (brine,
  copper, heel) and the chlorine S8 dosed over 3 h from 0, absorbed whole (`dosing.absorbed: 1`,
  core ADR 0054), then a 1 h post-reaction (`batch.time`). Reactions: CHL, Cu + Cl2 -> CuCl2, and
  COMP, CuCl2 + Cu -> 2 CuCl. The oxidation of the dissolved copper(I) by chlorine, 2 CuCl + Cl2
  -> 2 CuCl2, is CHL less COMP, so it is not a third reaction: the balance cannot fit the extents
  of linearly dependent reactions (`cheme.process-balance`, "runs backwards", found with it in).
  CHL carries the chlorine's heat to the copper(II) stage only. On a cooling failure the
  accumulated chlorine reacts with the copper to CuCl2 (-220.1 kJ/mol), and the excess copper then
  reduces that CuCl2 and the CuCl2 already present (COMP, -54.3 kJ/mol more). Core's screening
  takes each reaction alone (the largest), so that follow-on heat is missing from its MTSR and
  dT_ad; it is not conservative. The network value is given by hand in D-011 (L-2).
- Copper metal has no place in a liquid semi-batch: it is the solid CU, and the rate laws take its
  amount per m3 of the content as if dissolved (an effective rate of its surface, L-1).
- Rate laws, ASSUMED (no open kinetics, searched 2026-11-06): CHL second order in copper and
  chlorine, k 0.02 m3/(kmol s) at 353 K, Ea 40 kJ/mol; COMP second order in CuCl2 and copper, k
  1e-3 m3/(kmol s) at 353 K, Ea 50 kJ/mol, set so that 0.52 % of the copper is left as copper(II)
  after the post-reaction (SRC-3 leaves 0.5-2 % after its copper step).
- Heats: Hess sums of standard enthalpies of formation at 298.15 K (SRC-10): CuCl -137.2, CuCl2
  -220.1 kJ/mol (solids), chlorine as the gas dosed (core ADR 0054: the dosed gas as a gas, so its
  absorption is inside the heat): CHL -220.1 kJ/mol, COMP -54.3 kJ/mol, net -274.4 kJ/mol of
  chlorine. The heats of solution of CuCl2 and of the copper(I) chloro complexes in the brine are
  not known openly and are left out (ASSUMED 0; at +-10 kJ/mol of CuCl formed, +-1.4 kW against
  Q2's 18.7 kW, sign unknown).
Reason: every rate law is a placeholder for reaction calorimetry; fast laws make the dosing
chlorine-controlled, which a plant with a dosing interlock aims for.
**The low accumulation in D-011 is a consequence of the assumed rate laws** and must be confirmed
by reaction calorimetry before basic engineering.

## D-006 The dilution precipitation and the solubility of CuCl (2026-11-06)
Decision:
- CR101 (in P-101) is `crystallizer: basis: solubility` for CUCL in water, crystal CUCL_S, with
  NaCl, HCl, CuCl2 and dissolved chlorine as spectators (core ADR 0056), its two inlets the liquor
  S11A at 308.15 K and the dilution water S12 at 298.15 K, adiabatic: 299.32 K, the mix of their
  heat capacities (process/materials.yaml).
- Solubility, `measured_in: mother_liquor`, 3.79 g per kg of liquor, ASSUMED: no open table of
  CuCl in NaCl solutions was found (SRC-12 paywalled). It comes from a power law in the chloride
  not bound to copper(I), m (NaCl, HCl and 2 x CuCl2, mol per kg of water), s = 1.0 g/L x
  (m/0.282)^1.686, through two open points of SRC-5: about 1 g/L at 0.282 mol/L of excess
  chloride (20 C) and at least 39.6 g/L (0.4 mol/L) in 2.5 mol/L of NaCl and HCl (25 C). The
  exponent, near 2, is what copper(I)'s complexes with two and three chlorides give.
  **Against SRC-1 the law overpredicts at the brine's chloride level.** On the law's own basis
  the R-101 liquor S11A has m = (1.8349 + 0.0046 + 2 x 0.0026) kmol / 0.32323 t of water = 5.71
  mol/kg, where the law gives s = (5.71/0.282)^1.686 = 159 g per kg of liquor. SRC-1's 155 g/L,
  dissolved at room temperature, is about 124 g/kg at the model's density of S11A (1.25 kg/L,
  ideal mixing) and about 119 g/kg at 1.3 kg/L (ASSUMED range; SRC-1 gives no density). So the
  law is 28-34 % high there, at twice its upper fit point; SRC-1 does not validate it. CR101's
  liquor (m = 0.621 mol/kg) lies inside the fit range (0.28-2.5), where this overprediction does
  not apply. Both fit points are per litre and the law is applied per kg of water: refitted with
  the points per kg of water (water 0.99 and 0.95 kg/L at the two points, ASSUMED) it gives 3.63
  instead of 3.79 g/kg at CR101's liquor, 4 % less, within the solubility's uncertainty. The
  mother liquor S15 has m = 0.621 mol/kg. g/L is read as g per
  kg of liquor (a dilute liquor). No temperature dependence is taken (the points are at 20 and
  25 C, the liquor at 299.3 K). The law is evaluated at the solved liquor composition by hand
  and its value typed in; core checks neither (L-4), the test does.
- The dilution, about 7 volumes of water per volume of liquor (6.9 on the model's volume of S11A;
  SRC-2: 1-15, preferably 5-10, seven in its examples), deoxygenated by sparging with nitrogen
  (SRC-3, SRC-5).
- **The loss.** Only 76.5 % of the CuCl in the liquor precipitates; 22.1 % of the copper fed
  leaves dissolved (21.6 % as CuCl, 0.5 % as copper(II)), 22.3 % in all with the crystals and
  fines, with the brine. A larger dilution helps slowly: with s growing as m^1.69 and the
  volume as 1/m, the dissolved share falls as m^0.69 (10 volumes instead of 7 would leave about 19 % of
  the liquor's CuCl dissolved instead of 23.5 %). The loss
  follows from the brine's low CuCl/NaCl ratio (SRC-1's 155 g/L in 300 g/L NaCl); SRC-2's ammonium
  chloride liquor (its Example 1) holds about 3.5 times as much copper(I) per chloride and, with the
  same solubility law, would lose about a third as much (a variant, D-001).
- DC101: the crystals (4.14 g/cm3) settle during the hold; the clear liquor is decanted down to a
  slurry of 2 kg of liquor per kg of CuCl (ASSUMED), as SRC-3 siphons off its supernatant. The
  fines that stay suspended are not modelled.
Reason: the solubility, the basis of the precipitation and its loss, sits in the flowsheet as a
sourced estimate; the dilution and the deoxygenation are the sources'.
Rejected: a pure-water solubility with a Setschenow `salting_out` coefficient (core's log-linear
form): through SRC-5's two points it would need a fictitious pure-water value of 0.63 g/L, against
the measured 0.047-0.24 g/L (SRC-5, SRC-6), and would not fit SRC-1's point.

## D-007 Filtration and washes (2026-11-06)
Decision:
- F101, F102, F103: specified splits, 100 % (F101), 99.8 % (F102) and 99.9 % (F103) of the solid
  to the cake, 0.15 (aqueous) and 0.10 (ethanol) kg of liquid per kg of solid, ASSUMED; Ruth
  filtration times from ASSUMED cake data (specific cake resistance 3e9 m/kg for a dense
  crystalline salt, medium 1e10 1/m, 200 kPa of nitrogen; viscosities about water's, CoolProp's
  IAPWS water, SRC-10). F101 keeps all the solid: fines that passed its cloth into the recycled
  liquor would accumulate in the heel's loop (core's crystallizer cannot dissolve a solid that
  enters the brine, L-5); in the plant they would redissolve in the next brine.
- W101: a reslurry wash with dilute hydrochloric acid of 0.1 mol/L (pH 1; SRC-4 washes at pH
  1-2.5), about 1.6 kg per kg of CuCl, made up in T-103 from process water and 33 wt% acid (its
  heat of dilution, -17.5 kJ/mol ASSUMED, warms it to 298.57 K). It is a crystallizer: the cake
  S32 and the acid S20, adiabatic at 298.68 K; the CuCl dissolves to the solubility at the wash
  liquor's 0.144 mol/kg of excess chloride, 0.32 g per kg (the D-006 law taken below its lowest
  point, between the pure-water values of SRC-5, SRC-6 and that point). The acid keeps copper(II)
  and the basic salts in solution and displaces the brine (NaCl 3.5 -> 0.30 wt% of the cake's liquid).
- M103/F103: a displacement wash with 0.53 kg of ethanol per kg of CuCl (SRC-4), ASSUMED; the
  ethanol takes the water out of the cake so that it dries fast and cool, which keeps the wet CuCl
  from oxidising (D-011). CuCl is taken as insoluble in ethanol (no dissolution modelled; a
  mixer, L-5). The ethanol mixes with the cake's water with a heat of mixing of -0.6 kJ per mol
  of liquid (ASSUMED order of the ethanol-water excess enthalpy, 0.12 kW): 303.33 K.
Losses of copper (of the fresh copper S5, net of the tenth of the liquor recycled): 21.6 %
dissolved as CuCl with the effluent S30, 0.5 % as copper(II), 0.16 % as crystals through F102 (to
the effluent) and 0.08 % through F103 (to the spent ethanol), 0.10 % as fines from the bag filter;
the yield on copper is 77.6 % (CuCl in S29 per copper in S5), 77.3 % on chlorine.

## D-008 Drying and product (2026-11-06)
Decision: vacuum drying at 333 K under nitrogen in F-101 to 0.2 wt% volatiles (ASSUMED; core's
`dryer:` D101, its volatiles water, ethanol and HCl in their inlet ratio). Energy: the wet cake
0.8 kJ/(kg K) (CuCl's 0.49 with its liquid), latent heats at 333 K water 2358 kJ/kg (CoolProp's
IAPWS water), ethanol 866 kJ/kg (39.9 kJ/mol between chemicals' CRC values at 298 K and the
boiling point), HCl 443 kJ/kg (SRC-10); F-101's metal 2000 kJ/K (about 4 t of steel with the
agitator, ASSUMED) heated each batch from the cake's 303.3 K; 70 % efficiency; hot water at 343 K
from LP steam. Drying rate 3 kg/(m2 h) on 2.5 m2 (ASSUMED), cake density 2400 kg/m3 (CuCl 4.14
g/cm3 with its liquid and voids, ASSUMED). 34.7 kg of vapour a batch, 4.62 h. The vapour is
condensed on chilled water (Q6). The product is cooled in F-101 to 303 K on cooling water (Q7)
and discharged under nitrogen.
**Temperature limit: the wet product stays below 343 K, and so does the heating water (343 K).**
Wet CuCl oxidises in air and turns green (SRC-3, SRC-6); warm and moist, faster (ASSUMED limit,
no open number). SRC-4 dries at 80-110 C for 15-25 min, a short exposure, and SRC-3 vacuum-dries;
a longer vacuum drying is kept cooler.
Reason: the ethanol-wet cake dries at a low temperature, as SRC-4's sequence intends.

## D-009 Utilities and heat (2026-11-06)
Decision (year averages; Q2 written by `cheme process propagate --fill` from R101's model, core
ADR 0059; Q5 the dryer's model, compared at its port; the others hand arithmetic given in the
flowsheet's sources):
- LP steam 350 kPa(a): R-101's heat-up Q1 23.76 kW (the charge from 294.87 to 353.15 K, the
  copper and the heel with it); the dryer Q5 4.68 kW (core's dryer model: evaporation 4.43 MJ/h, the cake 0.99, the vessel 6.37, over 70 %);
- cooling water 298/308 K: the heat of chlorination Q2 18.67 kW (R101's model: the reactions' heat
  less the chlorine warmed to 353 K); the liquor's cool-down in R-101 to 308 K, Q3 18.49 kW (S9, 1479 kJ/(K h) x 45 K); the product and F-101's metal cooled from 333 to 303 K before the
  discharge, Q7 1.94 kW (of it 1.78 kW the metal: 2000 kJ/K x 30 K a batch of 9.37 h);
- chilled water 280/285 K: the filter-dryer's vacuum condenser Q6 1.35 kW (the vapour S28
  condensed at the dryer's latent heats and the condensate cooled to 290 K); on chilled water,
  since the ethanol and water vapour condense under the dryer's vacuum;
- electricity 11.52 kW: R-101's agitator 4 kW at 100 % and the vent scrubber's pump and fan 2.2 kW,
  P-101's 7.5 kW agitator at 37.4 % (2.80 kW), F-101's 2.2 kW agitator at 81 % and its 1.5 kW
  vacuum pump over the drying (2.52 kW). All ASSUMED.
Every temperature assumed for a mixed stream is the mix of its inlets (the components' liquid
heat capacities of `process/materials.yaml`, the test checks each): the brine S4 294.74 K (the
recycled liquor at 299.32 K, the salt's heat of solution, +3.88 kJ/mol ASSUMED, and the acid's
heat of dilution, -17.5 kJ/mol ASSUMED), the charge S7 294.87 K, the precipitation 299.32 K, the
acid 298.57 K, the acid wash 298.68 K, the ethanol wash 303.33 K (with its heat of mixing), the
effluent S30 299.31 K and the spent ethanol S31 301.41 K.
Every energy flow of the batch is in the flowsheet and so in the LCI per kg (library ADR 0035).
Counted within the streams' temperatures rather than as streams: the salt's heat of solution
(+1.79 kW: 1.656 kmol/h x 3.88 MJ/kmol, it cools the brine), the acids' heats of dilution
(0.02 kW and 0.03 kW) and the ethanol's heat of mixing (0.12 kW). Left out, with their numbers:
the heats of solution of the copper chloro complexes and of the precipitation (D-005; at +-10
kJ/mol, +-1.4 kW in R101 and +-1.1 kW in P-101, with an unknown sign), the heat losses of the
vessels (no insulation design yet), and the M202 mixing heat of the two ethanol-rich streams
(below 0.01 kW).

## D-010 Wastes (2026-11-06)
Decision: the copper-bearing brine S30 (75.0 kg per kg of product: 3.4 wt% NaCl, 0.37 wt% CuCl
dissolved, 0.011 wt% CuCl2 and the copper fines; 22.3 % of the copper fed) goes to copper recovery
and the site wastewater treatment, with the rinse of P-101; the spent ethanol S31 (0.67 kg per kg,
78 wt% ethanol) to solvent recovery.
Reason: SRC-4 neutralises its mother liquor and washes to a copper sludge for recycling and
recovers its ethanol by distillation; both are outside this concept's boundary (D-012). The
copper in the brine is the first thing to recover: cementation on iron or neutralisation
returns it as a sludge to a smelter (a variant: inside the boundary with its own feed, iron or
caustic, and a sludge; or the brine recycled after evaporating the dilution water, about 26 t a
batch, which the energy rules out at this scale). The yield on copper (77.6 %) is that of a plant
without that recovery.

## D-011 Thermal screening, the rate sensitivity and the hazards of chlorine, of air and of the ethanol (2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0058):
- R101: T_p 353.15 K; core's adiabatic rise of the whole batch 36.9 K (CHL run to completion of
  the chlorine; with COMP after it, the net 274.4 kJ/mol of chlorine over the content's heat
  capacity, 45.8 K by hand: core takes each reaction alone, L-2); largest accumulation of the
  dosed chlorine 0.63 % at the end of the dosing; MTSR 354.2 K at the worst moment (10811 s, just
  after the dosing), against an MTT of 373.1 K (water's normal boiling point, core's default,
  the dissolved chlorine and HCl left out; the brine itself boils about 8 K higher, so the MTT is
  conservative). The MTSR over the batch rises from 353.6 K after 0.8 h to 354.2 K at the end of
  the dosing, set by COMP on the copper(II) present (CHL alone 353.4 K).
- **Core's MTSR takes each reaction alone, so it is low.** Core gives a semi-batch's
  cooling-failure temperature as T + max_j(-dHr_j xi_j)/C: the largest reaction, not the sum.
  When CHL is the largest, the accumulated chlorine counts only to CuCl2 (-220.1 kJ/mol). The
  heat of COMP that the excess copper then releases is left out (-54.3 kJ/mol per CuCl2, on the
  CuCl2 formed and on the CuCl2 already accumulated). The network MTSR, by hand from core's own
  cooling profile (`solve_node`'s `cooling_profile`, the moles in R101 then):
  T + (274.4 kJ/mol x n_Cl2 + 54.3 kJ/mol x n_CuCl2) / C. It holds as long as the copper covers
  2 n_Cl2 + n_CuCl2, which it does in every case. The worst moment is the end of the dosing
  (10800 s) in every case, with C = 1479 kJ/(K h) and per hour of flows:
  - design: n_Cl2 0.00155, n_CuCl2 0.02725 kmol; (425 + 1480) / 1479 = 1.29 K, so **354.4 K**
    (copper 0.279 kmol against 0.030 needed);
  - k/10: n_Cl2 0.01054, n_CuCl2 0.12824 kmol; (2892 + 6963) / 1479 = 6.66 K, so **359.8 K**
    (copper 0.398 against 0.149);
  - k/100: n_Cl2 0.0695, n_CuCl2 0.1655 kmol; (19071 + 8986) / 1478 = 18.98 K, so **372.1 K**
    (copper 0.553 against 0.304).
  A second integration of the same rate laws, made during the agent review of the pull request
  (not an independent human review), gave 354.4, 359.8 and 372.3 K.
- No TD24 is known for the brine or the product (never estimated): no class
  (`cheme.reactor-hazard-missing`, info). By core's `criticality()`, with MTSR below MTT the
  classes still possible are 1 (TD24 above the MTT, 373.1 K), 2 (TD24 between the MTSR and the
  MTT) and 5 (TD24 below the MTSR, 354.2 K); class 3 and 4 need MTSR at or above MTT. An
  inorganic brine without a decomposing component makes class 1 likely, but that needs the TD24.
Sensitivity (scratch copies with both rate constants divided by 10 and by 100, the charge held at
the design's converged heel and recycled liquor; not committed):

| case | accumulation of Cl2 | MTSR (core, each reaction alone) | MTT | MTSR (network, by hand) | Cu(II) left after the 1 h post-reaction | Cl2 left unreacted |
|---|---|---|---|---|---|---|
| k (design) | 0.63 % | 354.2 K | 373.1 K | 354.4 K | 0.52 % of the copper | none |
| k/10 | 4.26 % | 357.9 K | 373.1 K | 359.8 K | 24 % | none |
| k/100 | 28.1 % | 363.5 K | 373.1 K | 372.1 K | 78 % | 17 kg a batch (1.84 kg/h of flows) |

On the network basis the MTSR stays below the MTT in every case, so the classes possible stay 1,
2 or 5. But **at k/100 it reaches 372.1 K, 1.0 K below water's boiling point**, and a slightly
slower rate would cross it (class 3 or 4 then possible). The large water content keeps the rise
small only while the rates are about as fast as assumed. With the tears free (the loop converged
again), slower rates let the heel grow: at k/100 R-101 needs 8 m3; the product falls with the
copper(II) left. The MTT stays at water's normal boiling point (core's default, no `hazard.mtt`).
The brine boils higher (about 8 K, ASSUMED, not sourced), which would give about 9 K of margin at
k/100, but no source for the boiling point of this liquor was found, so that margin is not taken.
**Safety requirement (recorded, for the basic engineering and the HAZOP):** the chlorine dosing
stops on a sign of accumulation, not only on a cooling failure. The signs are the reaction heat
falling behind the dose (the jacket's heat flow, or the reactor-jacket temperature difference,
against the dosed chlorine's expected heat), a redox potential that stays low, or chlorine in the
vent. Dosing resumes only once the accumulated chlorine has reacted. Reaction calorimetry must
confirm the rates (D-005) before this margin is relied on. Interpretation: at the assumed rates
the thermal risk is small on this screening; at slower rates it is held only by that dosing
interlock. The other risks are chemical:
- **Chlorine accumulation.** At k/100 the model holds 28 % of the dose, 46 kg, dissolved in 3.6
  m3 (13 g/L): far more than a hot brine dissolves (no open value; chlorine's solubility falls
  with temperature and salt). It would break through as gas. Core's absorbed dose takes the gas
  up whole and screens no desorption (L-3), so the gas release is by hand: the whole chlorine
  feed, 54.7 kg/h, about 22.4 m3/h at 353 K, to R-101's vent. The vent scrubber T-201 is therefore
  sized for the whole feed (ASSUMED 30 m3/h), and the dosing trips on a cooling failure, the
  agitator's stop, a high temperature, a high chlorine in the vent (an analyser) and a loss of the
  scrubber (its circulation, its caustic strength, its fan). Loss of the scrubber during the
  dosing would release chlorine to air: the trip closes the chlorine valve first. Water ingress
  is no hazard in this aqueous route, but brine sucked back into the dry chlorine line (on a loss
  of chlorine pressure) corrodes it: a check valve, a nitrogen purge of the dip pipe and a low
  pressure trip. R-101 has no `batch.vent` in the model (nothing forms a gas), so core gives no
  gas release and needs no `hazard.vent_capacity`.
- **The end point.** A slower reduction leaves copper(II) (24 % at k/10), green product and lost
  copper: the post-reaction is held until the liquor is colourless (SRC-1) or its redox potential
  says so, not for a fixed hour.
- **Oxidation by air.** Copper(I) is oxidised by oxygen in solution and as a wet solid to green
  basic copper(II) chloride (SRC-5, SRC-6); the design keeps air out: nitrogen in R-101, the
  dilution water sparged with nitrogen (SRC-3, SRC-5), the filter-dryer pressed and dried under
  nitrogen, the acid wash (copper(II) stays dissolved), the ethanol wash, a dryer below 343 K and
  a discharge under nitrogen into sealed packing (SRC-4). Not modelled: none of it changes the
  balance, so the assay is an upper bound (D-002). Without the sparging the 24.8 t of water a
  batch would bring about 0.2 kg of oxygen (8 mg/L, ASSUMED), enough to oxidise about 2.4 kg of
  CuCl to copper(II) (0.7 % of a batch).
- **Ethanol in F-101 and T-105 (flammable atmosphere).** Each batch puts 186 kg of anhydrous
  ethanol (S24) into F-101. About 159 kg leave with the wash filtrate, 27.6 kg are evaporated in
  the dryer (27.0 kg condensed on Q6, 0.55 kg left in the product), and all of it goes to T-105.
  Ethanol's flash point is 285 K, its lower flammable limit 3.1 vol% and its autoignition
  temperature 673 K (chemicals 1.5.2, `chemicals.safety`, SRC-10). The displacement wash at 303 K,
  the nitrogen pressing at 200 kPa, the vacuum drying at 333 K on 343 K water and the condensate
  all run above the flash point, so a flammable mixture forms wherever air gets in. The
  safeguards below are requirements for basic engineering, every number ASSUMED:
  - nitrogen inerting of F-101, its condenser and T-105 as a flammability safeguard (not only
    against oxidising CuCl): purged before the ethanol enters, the oxygen held below 5 vol%
    (ASSUMED, well below ethanol's limiting oxygen concentration in nitrogen, which is to be
    taken from a sourced value) and measured by an oxygen analyser on F-101's gas space, which
    stops the ethanol feed and the heating when it is high;
  - the vacuum broken with nitrogen only, never with air;
  - discharge only after the dryer's end point (at most 0.2 wt% volatiles, D-008) and the cooling
    to 303 K, confirmed by the vacuum's pressure and the condensate rate, and under nitrogen;
  - the vacuum pump's exhaust (nitrogen with the ethanol the condenser does not hold, not
    estimated, `emission_exclusions` dryer-vent) routed to a safe place: a vent stack outside the
    building with a flame arrester, or the site's VOC treatment (open input), not to the caustic
    scrubber T-201, which does not take up ethanol;
  - earthing and bonding of F-101, T-105 and the ethanol lines; an ethanol-rated vacuum pump.
  F-101, its condenser, the vacuum pump and T-105 need a hazardous-area zone (likely zone 1
  inside and around their openings, zone 2 around them, ASSUMED). That is an open input for the
  area-classification step (skill `area-classification`, `layout/zones.yaml`).
Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of dried CuCl from the flowsheet's year averages;
chlorine linked to chlor-alkali-1, hydrochloric acid 33 wt% to hydrogen-chloride-1 (by mass of the
acid, as both count it), ethanol to ethanol-1, the nitrogen consumable to asu-1's gaseous nitrogen
(`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other background a gap with the
activity it should connect to. Copper and sodium chloride have no library producer and no shared
vocabulary entry: their proxies (copper cathode, global market; vacuum salt) are recorded in
lca.yaml and here, not linked (CONTRIBUTING, "Gaps": a correct gap rather than a doubtful link).
Copper is the main burden of the product and stays a gap, so the dataset is preliminary.
Per batch, not in the flowsheet (core ADR 0053, library ADR 0035): nitrogen 66 kg (about 53 Nm3:
R-101's purge, the dilution water's sparging, F-101's pressing, the vacuum break and the
discharge; ASSUMED), 0.186 kg per kg; the rinse of P-101, 1 m3 (ASSUMED), 2.82 kg per kg, to the
copper-bearing effluent.
Per kg CuCl: copper 0.826 kg, chlorine 0.462 kg, sodium chloride 2.55 kg, hydrochloric acid 33 wt%
0.0296 kg, ethanol 0.525 kg, water 72.3 kg (plus 2.82 kg of rinse), electricity 0.304 kWh, LP
steam 0.750 kWh, cooling water 1.032 kWh removed, chilled water 0.036 kWh removed, copper-bearing
brine 75.0 kg, spent ethanol 0.674 kg. Not counted: the vent scrubber's traces and caustic, the
spent ethanol tank's breathing (0.4 g of ethanol per kg) and the dryer's vacuum vent
(emission_exclusions).

## D-013 Dedicated train (2026-11-06)
Decision: T-100, R-101, X-101, P-101, F-101 and the tanks make only CuCl, batch after batch: 846 batches in 7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002). Out of scope, so not LCI gaps: the
changeover cleaning between campaigns of other products and the idle time of a multipurpose
train.

## Core features used (cheme-as-code 1.9.0)

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with a dose and a post-reaction `time` | R101 (the chlorine into the brine over copper) | 0050 |
| `dosing.absorbed` (a gas dose taken up whole) | R101's chlorine; the MTT leaves it out | 0054, 0058 |
| the screening of a semi-batch: the default MTT of what boils (dissolved HCl, dosed chlorine left out), each reaction's MTSR, the MTSR over the batch | R101, D-011 | 0050, 0058 |
| the model's duty at `energy_port` | Q2 (R101) | 0059 |
| `tears:` and `convergence:` | the copper heel S6 and the recycled mother liquor S17 | 0060 |
| `crystallizer.spectators` with `solubility.measured_in: mother_liquor`, `kg/kg_liquor` | CR101 (the dilution precipitation), W101 (the acid reslurry wash) | 0056 |
| several crystallizer inlets (the liquor and the dilution water; the cake and the wash) | CR101, W101 | 0056 |
| `solid_separation.filtration` and recipe `filter` `from:` | F101, F102, F103 | 0057 |
| `dryer:` with energy, drying rate, cake density; recipe `dry` `from:`; `vessel.heated_area`; the duty compared at its port | D101 | 0057 |
| recipe `units:` (one vessel over several steps) | R-101 (M101, E101, R101, E102, SS101), P-101 (CR101, DC101), F-101 (six steps) | 0057 |
| vessel sizing and jacket check, `heat`/`cool` times from the jacket | R-101, F-101 | 0052 |
| per-batch LCA consumables | nitrogen, the rinse | 0053 |
Not used: `batch.vent` and `hazard.vent_capacity` (no reaction forms a gas; D-011); the batch
still (no distillation); `hazard.reactions` (every reaction counts, the conservative default);
`kind: phase-change` (the precipitation is core's crystallizer, not a reaction).

## Core limits hit (for core issues)

- L-1: **no solid reactant.** A semi-batch is liquid only: copper metal is a `phase: solid`
  component whose amount per m3 of the content drives a rate law as if dissolved. There is no
  surface area, particle size or mass transfer, and the metal's volume counts in the liquid's.
  An effective surface rate (a specific area per kg of solid in the rate law) would express the
  heel.
- L-2: **dT_ad and MTSR of a reaction network.** Core gives each reaction's rise run to
  completion alone and takes the largest (36.9 K for CHL); the network's net heat (CHL then COMP
  on the copper(II) formed, 274.4 kJ/mol of chlorine) gives 45.8 K by hand. Core's semi-batch
  MTSR, like its dT_ad, takes each reaction alone (T + max_j(-dHr_j xi_j)/C), so a consecutive
  reaction on the product of the dosed one is missing from both. Here it misses COMP's heat on
  the CuCl2 that the accumulated chlorine forms and on the CuCl2 already there. Core gives
  354.2 / 357.9 / 363.5 K at k, k/10 and k/100; the network gives 354.4 / 359.8 / 372.1 K by hand
  (D-011), so at k/100 core's MTSR is 8.6 K low and 1.0 K short of the MTT. For the core issue: the
  potential should be the network's (the heat released by running every reaction to the end
  state of what is in the vessel), not the largest single reaction's. The direct reaction and the oxidation of copper(I) cannot both be written either: the
  balance cannot fit linearly dependent reactions (D-005).
- L-3: **a gas dose has no solubility.** `absorbed: 1` takes the chlorine up whatever the
  liquid's chlorine content; there is no gas-liquid equilibrium, so an accumulated dose above
  its solubility (13 g/L at k/100) stays dissolved in the model, and its breakthrough on a cooling
  failure is not screened (ADR 0058's known limit, core#178 item 5). A vent that carries only a
  passing or desorbing gas is not possible either: `batch.vent.components` must be formed by a
  reaction (a warning otherwise), which is why the air route (oxygen in, nitrogen out) was
  rejected (D-001).
- L-4: **a liquor-measured solubility at one composition.** CR101's and W101's solubilities hold
  at the liquor composition they were evaluated at; core does not check that the solved mother
  liquor (after the recycle) is still there, and its only composition dependence is the
  log-linear Setschenow form, which cannot carry a power law in the chloride (copper(I)'s
  chloro complexes). A solubility as a function of a spectator's molality (a table or a power
  law) would let the recycle and the dilution move it.
- L-5: **no dissolution of a solid entering a brine.** A crystal that reaches a liquor where it is
  far below saturation (fines in the recycled mother liquor) passes as a solid; so F101 is set to
  keep all its solid. An ethanol wash is a mixer: no crystallizer with a non-aqueous solvent and
  water as a spectator was needed, but a wash's displacement efficiency is not modelled.
- L-6: **one coolant temperature for the duty check and the cool-down.** The jacket check takes
  the log-mean coolant temperature at the reaction (303.32 K), and the cool-down to 308 K takes
  its time from the same constant value, which cannot hold near 308 K (the return would exceed
  the process); the cool time (2.79 h) is optimistic. A coolant with supply and return (or a
  flow) would give both.
- L-7: **no design specification on a feed.** The fresh copper, salt, water and acid that hold
  the converged recycles at the product rate, and the batch size that equals rate x cycle, were
  set by hand (core#181 part 2).
- L-8: **no vessel for a non-batch unit procedure.** P-101 (a crystallizer and a settler) gets
  no volume from core (`cheme.recipe-reference` if a vessel is asked for); its 40 m3 is given
  from one batch's slurry by hand.
- L-9: **heats of solution and mixing.** The salt's heat of solution, the acid's dilution and the
  ethanol's mixing heat are in hand temperatures, not in a mixer's model; the heats of solution
  of the dosed gas and the copper complexes are left out (ADR 0054, 0059 known limits).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R101: composition, accumulation, MTSR, peak cooling | done in cheme, kinetics ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| recycles (heel, mother liquor) | done in cheme (tears, Wegstein) | D-004, core ADR 0060 |
| duty Q2 | done in cheme (the model's duty) | D-009, core ADR 0059 |
| precipitation and the acid wash | done in cheme: crystallizers with spectators, the solubility ASSUMED from a sourced fit | D-006, D-007, core ADR 0056 |
| settling, filtration | specified splits in cheme; filtration times by Ruth, cake data ASSUMED | D-006, D-007, core ADR 0057 |
| drying: outlets, duty Q5, drying time | done in cheme, moisture and rate ASSUMED | D-008, core ADR 0057 |
| batch recipe, cycle time, basis check, vessels, jacket | done in cheme | D-003, `cheme process recipe` |
| feeds for 300 t/a, the other duties (Q1, Q3, Q6, Q7), the mixed temperatures, the solubilities' values | hand (ratios scaled; arithmetic in the sources) | D-004, D-006, D-009, L-4, L-7 |
| per-batch exchanges (nitrogen, rinse) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, copper and salt unmapped | D-012 |

## Open inputs
Kinetics and heats of reaction in the brine (calorimetry), the chlorine's solubility in the hot
brine and its breakthrough rate, TD24 of the brine, the boiling point of the R-101 liquor (a
sourced `hazard.mtt`), the dosing's accumulation interlock (D-011); the ethanol's limiting
oxygen concentration, the vacuum exhaust's destination and the hazardous-area classification
of F-101, its condenser, the vacuum pump and T-105 (D-011); the solubility of CuCl in NaCl solutions
against chloride and temperature (SRC-12), and so the dilution loss; the heats of solution of the
chloro complexes; settling, filtration and wash data and the drying rate from trials; the
product specification (assay, copper(II), moisture, oxidation in storage); copper recovery from
the effluent (D-010); a TEA (`operation.batch: {recipe: true}`).
