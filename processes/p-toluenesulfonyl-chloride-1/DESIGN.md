# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
p-Toluenesulfonyl chloride (p-TsCl, tosyl chloride) by the salt-modified chlorosulfonation of
toluene, issue ChemE-as-Code/process-library#162. Concept stage: design basis, batch recipe,
balanced BFD/PFD, thermal screening with a rate sensitivity and a preliminary gate-to-gate LCI.
Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at a8f53ee4, which pins cheme-as-code 1.8.0
(4e8fd80): gas evolution through a batch vent (core ADR 0054), the batch still (0055),
precipitation from a mixed liquor (0056), the dryer and recipe units over several steps (0057),
on top of the semi-batch and the recipe of 1.7.0 (core ADRs 0050 to 0053). The NBS pilot
(`n-bromosuccinimide-1`) and `phosphorus-tribromide-1` are the templates.
Core pin raised to cheme-as-code 1.9.0 (314642c) on 2026-11-06: the semi-batch screening's
default MTT and gas release at the MTSR (core ADR 0058) and the duties the models write (ADR
0059) are used (D-014); recycle tears (ADR 0060) are not: the flowsheet has no recycle.
Core pin raised to cheme-as-code 1.10.0 (c55e9c7) on 2026-11-06: the quench dose's heat of
solution (ADR 0063) replaces the hand dilution stream Q10; the vent's vapour (ADR 0062) was run
on a scratch copy and not adopted, the batch column (ADR 0061) has no use here (D-015).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine translation of the original; no paragraph numbers, so
the locator is the part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | DE1912956A1, G. Schaeffer and J. Otten (Farbwerke Hoechst), filed 1969, published 1970: Verfahren zur Herstellung von p-Toluolsulfochlorid, https://patents.google.com/patent/DE1912956A1/en (family US3686300A, GB1268976A) | claim: per mol toluene 1-2 mol ClSO3H and 0.1-1 mol of an alkali, alkaline-earth or ammonium salt, toluene at 60-90 C, cooled to 30-40 C, at least 1 mol more ClSO3H. Example 1: 1.5 mol ClSO3H, 0.45 mol NH4Cl added in portions (HCl escapes, warms to about 50 C), 1 mol toluene over 2-3 h at about 60-70 C, cooled to about 35 C, 1.5 mol ClSO3H in 5-10 min, about 1 h at 35 C, poured onto ice water, worked up by solvent extraction and distillation: 84-85 % of theory, freezing point 62 C, p-content 90 %, 77 % of theory as the para compound. Example 2: similar, 72-74 % para. Description: higher temperature gives about 1 % higher-boiling products, lower temperature more ortho; the crude solid can be washed and used directly. Prior art: classic sulfuric acid sulfonation and isomer separation; direct cold chlorosulfonation gives an o/p mixture; a continuous process (DE 1 172 258) with 89 % of an isomer mixture of about 69 % para | read; patent, facts only | D-001, D-004, D-005 |
| SRC-2 | PL73685B2, Osrodek Badawczo-Rozwojowy Przemyslu Barwnikow, filed 1971: Sposob wytwarzania p-toluenosulfochlorku, https://patents.google.com/patent/PL73685B2/en | example: sulfuric acid sulfonation at 90-110 C, isomerisation at 150 C, ClSO3H at 20 C for 4 h; poured onto crushed ice, the crystals filtered, washed three times with ice water and pressed (about 10 % water if used wet), else washed with alcohol and vacuum-dried at 30-40 C; yield above 80 %, mp 67-69 C, stated free of the ortho isomer | read; patent, facts only | D-007, D-008 (work-up); route rejected (D-001) |
| SRC-3 | CN105503671A, Zhejiang Jiahua Energy Chemical and Jiaxing University, 2015/2016 (deemed withdrawn): Preparation method of p-toluene sulfonyl chloride, https://patents.google.com/patent/CN105503671A/en | p-TsOH in chloroform with an ionic liquid, ClSO3H at 25 C, water quench, phase split, solvent distilled; 0.1 mol examples, 80.8-88.2 % | read; patent, facts only | D-001 (variant, rejected) |
| SRC-4 | PubChem CID 7397, 4-Methylbenzenesulfonyl chloride, https://pubchem.ncbi.nlm.nih.gov/compound/7397 | identity (C7H7ClO2S, InChIKey YYROPELSRYBVMQ-UHFFFAOYSA-N, CAS 98-59-9); HSDB: mp 69-71 C, bp 146 C at 15 mmHg, density 1.33 g/cm3, insoluble in water, solubility in water: reaction | read (PUG REST and PUG View) | D-007, materials, registry |
| SRC-5 | PubChem CID 24638 (chlorosulfonic acid), CID 25517 (ammonium chloride), CID 8623 (o-TsCl) | identity (formula, InChIKey, CAS) | read (PUG REST) | registry, materials |
| SRC-6 | Wikipedia, Chlorosulfuric acid, https://en.wikipedia.org/wiki/Chlorosulfuric_acid | density 1.753 g/cm3; reacts violently with water to H2SO4 and HCl; made industrially from HCl and SO3 dissolved in sulfuric acid; used for the chlorosulfonation of toluene (saccharin route) | read; CC BY-SA, facts only | materials, D-005, D-012 (proxy) |
| SRC-7 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADRs 0050, 0054) | method reference, no data taken | D-011 |
| SRC-8 | processes/btx-1, chlor-alkali-1, asu-1 (this library) | toluene (a co-product of reformate extraction), caustic soda 50 wt%, gaseous nitrogen | library, internal | feed links (D-004, D-012) |
| SRC-9 | Ullmann's Encyclopedia of Industrial Chemistry: Benzenesulfonic Acids and Their Derivatives (doi:10.1002/14356007.a03_507) and Chlorosulfuric Acid (doi:10.1002/14356007.a07_017.pub2) | - | not read (licensed); named by the route scouting and by Wikipedia | leads only, nothing taken |
| SRC-10 | Harding, V. J. (1921) J. Chem. Soc., Trans. 119, 1261: the sulphonation of toluene with chlorosulphonic acid | - | not read (title and metadata only; named by SRC-1 as giving a favourable p:o ratio at higher temperature) | lead only |
| SRC-11 | Property data of core's environment and the NIST WebBook: the `chemicals` 1.5.2 package (its packaged CRC Handbook tables: `chemicals.miscdata.CRC_inorganic_data` and `CRC_organic_data` for densities and boiling points, `chemicals.heat_capacity.CRC_standard_data` for heat capacities; `chemicals.phase_change.Tb`), CoolProp's IAPWS water (saturation, latent heat, viscosity, heat capacity), and the NIST Chemistry WebBook, SRD 69 (https://webbook.nist.gov: toluene and NH4Cl condensed-phase data, toluene and HCl phase-change data) | per component in `process/materials.yaml`; the dryer's latent heats (D-008); LP steam saturation; the wash filtrates' viscosity (D-007) | open data packages queried and WebBook pages read (2026-11-05); facts only. The CRC values come from the tables packaged in `chemicals`, not from the printed (licensed) handbook | materials, D-007, D-008, D-009 |

Searched and not found openly (2026-11-05): kinetics or reaction calorimetry of the
chlorosulfonation of toluene, a sourced formation enthalpy of liquid chlorosulfonic acid or a
heat of its hydrolysis (a wiki gives -555.2 kJ/mol without a source, a Joback estimate -665
kJ/mol: neither is used), the solubility of p-TsCl in water or in a sulfuric/hydrochloric acid
liquor, its hydrolysis rate as a solid, a plant's specific consumptions and a market volume. The
route scouting also named CN1436773A (ClSO3H with POCl3 and an ammonium salt, solvent
crystallisation); it was not re-read and is not used.

## D-001 Route and boundary (2026-11-05)
Decision: the salt-modified chlorosulfonation of SRC-1, Example 1, on a dedicated train (D-013):
- R-101: NH4Cl + ClSO3H -> NH4SO3Cl + HCl (the salt taken up, ASSUMED product), then
  C7H8 + ClSO3H -> CH3C6H4SO3H + HCl at 338 K, 90 % para and 10 % ortho;
- R-101, after cooling to 308 K: CH3C6H4SO3H + ClSO3H -> CH3C6H4SO2Cl + H2SO4 with the second
  acid portion;
- Q-101: the mass dosed into a water heel (the drown-out quench): ClSO3H + H2O -> H2SO4 + HCl,
  NH4SO3Cl + H2O -> NH4HSO4 + HCl, a little TsCl hydrolysed back to TsOH; p-TsCl precipitates;
- F-101 / DR-101: filtration, two reslurry washes with ice water, vacuum drying at 308 K;
- T-201: the HCl of both vents neutralised with caustic soda.
Boundary feeds: chlorosulfonic acid, ammonium chloride, toluene, caustic soda 50 wt%, process
water, electricity, LP steam; returns: cooling water, chilled brine; outputs: dried p-TsCl, waste
acid to neutralisation, spent scrubber liquor.
Reason: the issue names this route; SRC-1 is the most complete open description of a batch with
a sourced para share, yield and work-up order, and it is the gas-evolving, dosed, quenched and
precipitated batch the 1.8.0 features (vent, spectators, dryer, recipe units) are for.
Rejected:
- the cold direct chlorosulfonation without salt (SRC-1 prior art: an o/p mixture needing an
  isomer separation);
- the sulfuric acid sulfonation with isomerisation at 150 C before the chlorination (SRC-2): a
  product free of the ortho isomer, but three temperature stages and 5 parts of acid per part of
  toluene; a candidate variant;
- chlorination of purchased TsOH in chloroform (SRC-3): avoids the isomers but needs an
  extraction and a solvent strip; a variant once a TsOH entry exists;
- HCl recovery as hydrochloric acid instead of the caustic scrubber: the industrial choice where
  the acid can be sold, but a co-product needs an allocation this concept does not have data for;
  a variant.
Links: toluene from btx-1, caustic soda from chlor-alkali-1, nitrogen from asu-1. No library
process makes chlorosulfonic acid (SO3 + HCl; sulfuric-acid-1's SO3 is internal) or ammonium
chloride.

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 1000 t/a dried p-TsCl, 7920 h/a (330 days of 24 h), ASSUMED. Modelled product: 99.7
wt% p-TsCl, 0.2 wt% water, 0.06 wt% H2SO4, 0.02 wt% NH4HSO4, toluenesulfonic acids and o-TsCl
below 0.01 wt% each (D-007, D-008). **The 99.7 wt% is an upper bound, not a specification**:
the cake's retention of the o-TsCl oil is not modelled (L-4), and the only source's crude (SRC-1,
not washed free of the oil) is 90 % para. The product specification is an open input.
Reason: no open market or plant figure was found; p-TsCl is a fine-chemical reagent and
intermediate (tosylates, sulfonamides), larger than NBS (500 t/a) but still a batch product. The
LCI is per kg and does not depend on the scale; the batch size does (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-05)
Decision: one batch makes 1748.95 kg of dried p-TsCl (stream S24); the recipe
(`process/recipe.yaml`) has four unit procedures:
- CHLOROSULFONATE on R-101, one vessel over E101, R101 and R102 (`units`, core ADR 0057):
  nitrogen purge 0.25 h, first acid charge 0.5 h, heat 298 -> 338 K 0.21 h (from the jacket),
  dose 7.0 h (salt 1 h, then toluene 6 h) and post-reaction 0.07 h to 0.99 conversion of the
  toluene (both from R101's model), cool 338 -> 308 K 0.65 h (jacket), second acid portion
  0.17 h and hold 1 h (SRC-1), transfer 4 h (the mass dosed into Q-101, as long as Q101's
  dosing): 13.85 h;
- QUENCH on Q-101 over E102, Q101 and CR101: dose 4 h and post-reaction 0.02 h (Q101's model),
  precipitation hold 1 h, slurry transfer 1 h, rinse 0.5 h, next heel 0.5 h, heel cooled
  298 -> 288 K 0.53 h (jacket): 7.55 h;
- FILTER on F-101 over F101, W101, F102, W102 and F103: filtrations 5.59 h, 1.34 h and 1.39 h
  (Ruth, from the filters' filtration data), two reslurry washes 0.5 h each, discharge 0.5 h,
  rinse 0.5 h: 10.33 h;
- DRY on DR-101: receive 0.5 h, dry 11.50 h (D101's drying rate on 15 m2), discharge 0.5 h:
  12.50 h.
R-101 is the bottleneck: cycle 13.85 h, 571.8 batches in 7920 h; one batch takes 36.7 h from
the purge to the dryer's discharge. The flowsheet's flows are the recipe's year averages:
1748.95 kg x 571.8 / 7920 h = 126.26 kg/h of S24 (no `cheme.recipe-basis` finding). The batch
size was found by fixed-point iteration (the heating and cooling times depend on the vessel, so
on the batch: lesson L-6).
Dosing times: the patent's 2-3 h of toluene is a laboratory figure. At plant scale the jacket
sets it: with 2.5 h R101's peak duty was 1.7 times what R-101's jacket removes at the charge, so
the salt is added over 1 h and the toluene over 6 h; the jacket (U 300 W/(m2 K) enamelled, 4.92
m2 wetted at the charge, cooling water at 298 K) removes 59.0 kW against the model's peak 50.3
kW. The quench is dosed over 4 h on brine at 258 K: the jacket (23.4 m2 at the charge) removes
210 kW against the model's peak of 190.5 kW (`cheme process recipe`, core 1.10.0): the reactions'
135 kW and the dosed acids' heat of solution, 16.03 kW as a year average (57694 kJ/h), 799 MJ a
batch (x 13.85 h) released at the dose's rate over the 4 h: 799000 kJ / 14400 s = 55.5 kW. Until
core 1.10.0 that share was added to the model's 135 kW by hand (D-009, D-014); the model now
takes it (D-015).
Vessels (fill 0.8, H/D 1.2 enamelled, 1.0 for the Nutsche, ASSUMED): R-101 4 m3, given and not
sized (core sizes it from R101's model alone, 2.04 m3, while R102's second acid portion adds
1.16 m3 in the same vessel: 3.11 m3 of reaction mass, 78 % of 4 m3; L-1); Q-101 20 m3 (14.95 m3
of slurry, 75 %); F-101 20 m3 (sized by the slurry it takes in, D 2.94 m; its plate the filter
area); DR-101 4 m3 (2.06 m3 of wet cake, 52 %), heated area 15 m2 (jacket and shaft of a paddle
dryer, ASSUMED).
Reason: core ADR 0051 puts the batch basis in one place, so the balance, the LCI per kg and a
later TEA share it; the dosing, reaction, heating, cooling, filtration and drying times come
from the models, so a change of the kinetics, the jacket, the cake or the drying rate changes
the cycle. A filter-dryer in one vessel (NBS's choice) was tried first: with 15 m3 of slurry and
a drying time of 14.4 h on its jacket alone it was the bottleneck even in two units; a separate
paddle dryer with a heated shaft keeps R-101 the bottleneck with one Nutsche and one dryer.

## D-004 Feeds and charge (2026-11-05)
Decision: per mol of toluene 1.5 mol ClSO3H in the charge, 0.45 mol NH4Cl, 1.5 mol ClSO3H in
the second portion (SRC-1, Example 1), all 100 % in the model. The feeds are these ratios
scaled to 0.8385 kmol/h of toluene, the toluene that gives 126.263 kg/h of S24 at the model's
yield (every outlet scales linearly with the feeds at fixed times). Toluene from btx-1 (dry),
chlorosulfonic acid and ammonium chloride merchant, technical grade (their impurities, free
SO3, H2SO4 and HCl, are not modelled).
Reason: the patent's example is the only open source with a para share and a yield for this
salt-modified route; SRC-2's different route uses about 4 mol of acid per mol of toluene (5
parts by mass per part), so the 3 mol here is not unusually lean.

## D-005 Reaction models, kinetics and heats (2026-11-05)
Decision:
- R101 is `reactor: semibatch` (core ADR 0050) at 338.15 K, isothermal: the acid charge S2, the
  salt S3 dosed over 1 h from 0, toluene S4 over 6 h from 1 h, then the post-reaction to 0.99
  conversion of the toluene (`batch.target`; 0.07 h). `batch.vent` takes the HCl out as it
  forms (all of it: little HCl dissolves in the hot acid, ASSUMED). Rate laws, ASSUMED: SALT
  second order in NH4Cl and ClSO3H, k 0.01 m3/(kmol s) at 338 K; SULP and SULO second order in
  toluene and ClSO3H, together k 6.0e-3 m3/(kmol s) at 338 K split 90 : 10 (the patent's
  p-content), Ea 50 kJ/mol. The acid's excess for the sulfonation is small (1.05 mol per mol
  toluene after the salt), so the rate slows at the end of the dosing; that is where the
  accumulation peaks (D-011).
- R102 is a conversion step in the same vessel: 90 % of each sulfonic acid to its sulfonyl
  chloride with the second acid portion, ASSUMED. The rest stays as TsOH and goes to the waste
  acid. 90 % gives 89.1 % of the toluene as sulfonyl chlorides in the mass (0.99 x 0.9), 88.5 %
  after the quench's hydrolysis, and 78.8 % as dried, washed para product.
  **The modelled yield is above the source's.** SRC-1's crude is 84-85 % of theory with 90 %
  para, 77 % of theory as the para compound, and that crude has not been washed or filtered.
  The 78.8 % here is after filtration and washing. It assumes that SRC-1's figures are after
  its own solvent extraction and distillation, with their losses, and that the in-mass
  conversion is higher than the isolated crude. Nothing measures that: it is an ASSUMED better
  conversion, not a sourced one.
  Calibrated to the source instead, the conversion would be about 0.87 (0.99 x 0.9 x c x 0.9932
  = 0.77 para in the quenched mass) and the dried para product about 76 %. Every feed, waste and
  utility per kg would then rise by about 3.5 % (0.788 / 0.761). This sensitivity is not
  modelled. The second stage's conversion is an open input.
- Q101 is a second vented semi-batch at 288.15 K: the water heel S10 charged, the mass S8 (at
  308 K) dosed over 4 h, then the post-reaction to 0.9999 conversion of the ClSO3H (0.02 h).
  HYD and AMH second order in the chloride and water, k 1e-3 m3/(kmol s) at 288 K (fast, about
  0.05 1/s in the heel); TSHP and TSHO an effective slow hydrolysis of the sulfonyl chlorides
  (k c_H2O about 1e-6 1/s), ASSUMED: the model carries TsCl dissolved, while it is a solid and an
  oil in the cold liquor; it loses 0.68 % of the p-TsCl. 10 % of the HCl formed leaves by the
  vent, 90 % stays dissolved in the dilute acid (ASSUMED, D-006).
- Heats, ASSUMED (no open calorimetry or formation enthalpy of liquid ClSO3H, searched
  2026-11-05): SALT -20 kJ/mol (the patent's charge warms to about 50 C as the salt goes in);
  SULP and SULO -100 kJ/mol with HCl formed as a gas (an aromatic sulfonation by SO3 is commonly
  put at about -170 kJ/mol; chlorosulfonic acid, the adduct of SO3 and HCl, brings less);
  CHLP and CHLO -10 kJ/mol (the patent adds the second portion in 5-10 min); HYD -180 kJ/mol and
  AMH -80 kJ/mol as effective values to the dilute liquor (the hydrolysis, taken as about -30
  kJ/mol, the dilution of the H2SO4 formed, about -75, and the dissolution of the HCl that stays,
  about -75 kJ/mol); TSHP and TSHO -60 kJ/mol.
Reason: every rate law is a placeholder for reaction calorimetry; the fast laws make the dosed
steps dosing-controlled, which a plant with a dosing interlock would aim for. The second stage
is a conversion step because one recipe vessel may hold only one batch or semi-batch step, and
a semi-batch runs at one temperature (L-3).
**The low accumulation in D-011 is a consequence of the assumed rate laws** and must be
confirmed by reaction calorimetry before basic engineering.

## D-006 The quench (2026-11-05)
Decision: about 2.5 kg of water per kg of reaction mass (866 kg/h; 12.0 t a batch) in Q-101,
cooled to 288 K on brine; the mass dosed into it over 4 h, held at 288 K (above o-TsCl's
melting point of about 10 C, so the ortho isomer stays an oil, D-007). The liquor ends at about
10.6 wt% H2SO4, 2.6 wt% HCl and 3.6 wt% NH4HSO4. 10 % of the HCl formed in the quench is vented
(ASSUMED; core has no HCl solubility in the acid, the vent fraction stands in for it, L-5).
Reason: SRC-1 and SRC-2 quench onto ice or ice water but give no water ratio for SRC-1; SRC-2's
example uses about 2 parts of ice per part of mass (6500 parts of ice for 3200 parts of toluene,
sulfuric and chlorosulfonic acid). Ice is not modelled: the heel is cooled
water and the brine jacket takes the heat (core has no ice-melting sink in the semi-batch). The
"reverse" quench (mass into water) keeps the water in excess at all times, the safe order for a
violent hydrolysis.

## D-007 Precipitation, ortho isomer, filtration, washes and the scrubber (2026-11-05)
Decision:
- CR101 (in Q-101) is `crystallizer: basis: solubility` for PTSCL in water, crystal PTSCL_S, at
  288 K, with every other solute of the liquor a spectator (core ADR 0056): H2SO4, HCl, NH4HSO4,
  the toluenesulfonic acids, o-TsCl, toluene and the traces of ClSO3H, NH4SO3Cl and NH4Cl.
  Solubility 0.5 g per kg water, `measured_in: pure_solvent`, ASSUMED (SRC-4: insoluble and
  reactive; no measured value), with `salting_out` coefficients of 0 for every spectator
  (ASSUMED: no data; strong acids would rather salt an aromatic out, so 0 overstates the loss).
  0.33 % of the p-TsCl stays dissolved.
- The ortho isomer o-TsCl (mp about 10 C) is carried as a liquid spectator: it divides between
  cake and filtrate with the liquor, and the two washes carry it on. The model's product holds
  0.007 wt% of it. This is a lower bound, so the product's 99.7 wt% assay is an upper bound
  (D-002): the oil wets the crystals and a real cake keeps more of
  it (SRC-1's crude, not washed free, has 10 % ortho; SRC-2 calls its product free of ortho after
  the isomerisation, which this route does not have). The crystallizer takes one crystallizing
  solute and no second liquid phase (L-4).
- F101, F102, F103: specified splits, 99.8 % of the solid to the cake, 0.3 kg of liquor per kg of
  solid, ASSUMED; Ruth filtration times from ASSUMED cake data (specific cake resistance 1e10
  m/kg, medium 1e10 1/m, 200 kPa of nitrogen; the liquor 1.6 mPa s and 1100 kg/m3 at 288 K, the
  wash filtrates 1.45 and 1.5 mPa s, water's at their temperatures (SRC-11), on the Nutsche's
  plate.
- W101, W102: two reslurry washes with 2 kg of ice water per kg of solid. The process water S31
  is chilled from 298 to 278 K in the wash water tank T-101 on brine (E103, Q9) and split
  equally to the two washes (SP201). Each wash is a crystallizer fed by the cake and the water,
  its crystals dissolving to saturation, then filtered. The washes are adiabatic (D-009), so
  their temperatures are the mixes of their inlets, with the liquid heat capacities of
  `process/materials.yaml`: W101 280.24 K (the cake S14 at 288.15 K, 281.2 kJ/(K h), with
  1063.8 kJ/(K h) of water at 278.15 K), W102 278.61 K (S18 at 280.24 K, 301.1 kJ/(K h)). The
  solubility is the same at either temperature, so the balance does not depend on it. They take the H2SO4 in the cake liquor from 11.8 wt% to 0.2 wt% (0.06 wt% in the
  dried product). SRC-2 washes three times with ice water; two reslurry washes are ASSUMED to
  do the same work.
- T-201 (S101): the vents S5 and S11 to a caustic scrubber, 0.999 of the HCl neutralised
  (ASSUMED), 50 wt% caustic at 1.05 mol NaOH per mol HCl and water to a 20 wt% NaCl liquor; per
  batch 657 kg of HCl (609 kg from R-101, 48 kg from Q-101), the peak 145 m3/h at 338 K while
  the salt goes into R-101 (`cheme process recipe`), about 53 m3/h during the toluene dosing
  (11.6 kmol of toluene a batch over 6 h, by hand).
Reason: the solubility, the basis of the precipitation and of the wash losses, sits in the
flowsheet; the washes are the sources' cold-water washes; the scrubber is sized from the vents'
calculated rates rather than a guess.
Losses of the para compound, of the p-TsOH formed: 10 % not converted in R102 (to the waste
acid), 0.68 % hydrolysed in the quench, 0.33 % dissolved in the mother liquor, 0.20 % dissolved
in the washes, 0.59 % through the filters as solid (ASSUMED recovery).

## D-008 Drying and product (2026-11-05)
Decision: vacuum drying at 308 K in the paddle dryer DR-101 to 0.2 wt% volatiles (ASSUMED; core's
`dryer:` D101, its volatiles water, HCl and toluene in their inlet ratio); the salts, acids and
o-TsCl of the cake liquor dry onto the crystals. Energy: the wet cake 1.5 kJ/(kg K), latent
heats water 2418 kJ/kg at 308 K (steam tables), HCl 443 kJ/kg (16.15 kJ/mol at its boiling
point, NIST WebBook; its desorption from water is not counted) and toluene 412 kJ/kg (38.0
kJ/mol, NIST WebBook; SRC-11), the dryer's metal 2500 kJ/K (about 5 t of steel, ASSUMED) heated
each batch from the cake's 278.6 K (S22), 70 % efficiency. The vapour is condensed in the
vacuum condenser on brine (Q8, D-009). Drying rate 3 kg/(m2 h) on 15 m2 (ASSUMED, below NBS's 5 at
333 K for the smaller temperature difference), wet-cake density 1100 kg/m3 (ASSUMED from the
crystal density 1.33 g/cm3, SRC-4). 517 kg of water per batch, 11.5 h. The product is cooled in
DR-101 and leaves at 298 K.
Reason: SRC-2 dries at 30-40 C under vacuum; p-TsCl melts at 67-71 C and hydrolyses when wet and
warm, so a low drying temperature and a low residual moisture go together.

## D-009 Utilities and heat (2026-11-05)
Decision (year averages; Q2, Q3 and Q5 written by `cheme process propagate --fill` from the
models, core ADR 0059, D-014; the others hand arithmetic given in the flowsheet's sources):
- LP steam 350 kPa(a): R-101's heat-up Q1 2.10 kW; the dryer Q6 40.84 kW (core's dryer model:
  evaporation 90.3 MJ/h, the cake 7.3, the vessel 5.3, over 70 %);
- cooling water 298/308 K: the heat of sulfonation Q2 23.34 kW (R101's model: its reactions
  release 25.15 kW, 90.6 MJ/h, less 1.82 kW warming the doses S3 and S4 to 338 K; the hand value
  of 1.8.0 agreed); the cool-down and the second portion Q3 3.76 kW (R102's
  model: CHLP and CHLO 2.08 kW at their heat's 298.15 K, and 1.69 kW of sensible heat, S6 from
  338 K and S7 from 298 K brought to 298.15 K and S8 from it to 308 K; the hand value, 3.72 kW,
  took the heat of reaction at 308 K with the reactants' heat capacity, 1.2 % lower, and is
  dropped); the scrubber Q7 49.87 kW. Q7 is NEUT at -132 kJ/mol
  (neutralisation and the HCl's dissolution), less the liquor's 10 K rise, plus the dilution of
  the 50 wt% caustic (-15 kJ/mol NaOH, 5.7 kW) and the vent gas cooled from 334.5 K (0.3 kW).
  The caustic's dilution heat is an ASSUMED order of magnitude: no open table of NaOH's integral
  heats of solution was read. It is to be confirmed (open input);
- chilled brine 258/263 K:
  - the heel Q4 10.07 kW;
  - the quench Q5, 54.95 kW on Q-101's jacket, Q101's model (core 1.10.0, D-015): 36.51 kW from
    its reactions, 2.41 kW the mass S8 cooled from 308 to 288 K and 16.03 kW the dose's heat of
    solution (term `solution`), the dilution of the H2SO4 and sulfonic acids dosed with the mass
    (0.747 kmol/h x -75 kJ/mol and 0.083 x -20, ASSUMED, D-005). Until core 1.8.0 one hand-typed
    Q5 held all of it; under 1.9.0 the dilution was the hand stream Q10 beside the model's Q5
    (D-014, L-2);
  - DR-101's vacuum condenser Q8 25.52 kW: the dryer's 37.35 kg/h of water vapour condensed
    (2418 kJ/kg) and the condensate cooled from 308 to 298 K. It is on brine because condensing
    at the dryer's vacuum (5.6 kPa at 308 K, 3.2 kPa at 298 K) needs a coolant colder than the
    298 K cooling water;
  - the wash water chilled from 298 to 278 K in T-101, Q9 11.82 kW (508.36 kg/h, E103);
- electricity 24.4 kW: R-101 agitator 3 kW, Q-101 agitator 11 kW at 55 % occupancy (6 kW),
  Nutsche agitator 4 kW at 73 % and paddle drive 7.5 kW plus vacuum pump 3 kW at 90 % (12.4 kW),
  scrubber pump and fan 3 kW. All ASSUMED.
The crystallizers CR101, W101 and W102 are adiabatic (`process/simulation.yaml`): the heat of
crystallisation of p-TsCl is small and not known openly. The temperatures of the washes and of
the waste acid S26 (285.33 K) are therefore the mixes of their inlets (D-007). The vent mix S27
is 334.53 K.
Every energy flow of the batch is in the flowsheet and so in the LCI per kg (library ADR 0035):
the dilution heat is in Q5, to the brine terminal, so product:BRINE counts it.
Still left out: the heat losses and gains of the vessels and tanks, and the heats of
crystallisation.
During R101's toluene dosing the jacket removes up to 50 kW (the model's peak). During the
quench it removes up to 190.5 kW, the model's peak with the dose's heat of solution (55.5 kW of
it over the 4 h of dosing; D-003, D-015).

## D-010 Wastes (2026-11-05)
Decision: the mother liquor, the wash filtrates and the dryer condensate (12.6 kg per kg
product: 8 wt% H2SO4, 2 wt% HCl, 2.7 wt% NH4HSO4, 0.9 wt% toluenesulfonic acids, 0.9 wt% of the
o-TsCl oil) go to neutralisation and the site wastewater treatment; the spent scrubber liquor
(3.0 kg per kg, 20 wt% NaCl) to the wastewater treatment. Neither acid nor HCl is recovered.
Reason: SRC-1's and SRC-2's work-ups end in a dilute waste acid; recovering it (concentration,
or an ortho-TsCl recovery for saccharin) is outside this concept. The waste acid is the largest
burden of the route and the first thing a TEA or LCA will look at.

## D-011 Thermal screening and the rate sensitivity (2026-11-05)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054, 0058):
- R101 (sulfonation): T_p 338.15 K, adiabatic rise of the whole batch 238 K (the content is a
  little acid with a low heat capacity, and the vented HCl adds none); largest accumulation of
  the dosed toluene 1.69 % at the end of the dosing (the acid's small excess runs low); MTSR at
  the worst moment 343.6 K, against an MTT of 383.75 K (toluene's normal boiling point, the lowest
  of what stays in the liquid; core 1.9.0's default, which leaves the vent's HCl out, D-014). The
  MTSR over the batch rises from 338.5 K after 1.4 h to 343.6 K at the end of the dosing (7 h),
  set by SULP (SALT alone 338.3 K). The vent's peak HCl rate in operation is 0.71 mmol/(s m3) at
  the salt's addition (144.9 m3/h, `cheme process recipe`). Core takes the gas release of a
  cooling failure only at the moment of the highest MTSR, the end of the toluene dosing (25200
  s): the accumulated toluene releases 0.594 mol/s of HCl, 60.3 m3/h at 343.6 K, 0.40 of the
  vent capacity of 150 m3/h (`hazard.vent_capacity`, D-014); SULP run to completion from that
  moment forms 0.197 kmol (5.5 m3). It is not the largest release of the batch: core's
  `stirred_tank.vent_gas_rate` at every point of R101's cooling profile, at that point's MTSR and
  per batch (13.85 h of the flowsheet's flows, as core scales it), gives the most at the end of
  the salt addition (3600 s), from SALT's accumulated NH4Cl: 145.5 m3/h at 338.3 K, 0.97 of the
  vent, about 3 % margin (a cooling failure there releases about the normal peak, since the
  salt's HCl leaves as it forms). The pressure of a blocked vent is still not screened.
- Q101 (quench): T_p 288.15 K, dT_ad 39.1 K (HYD's 24.9 K and 14.2 K of the dosed acids' heat of
  solution, core 1.10.0, D-015), accumulation of ClSO3H 0.16 %, MTSR 298.2 K (it
  includes the hydrolysis potential of the TsCl in the liquor, which hardly reacts: TSHP alone
  298.2 K, HYD alone 288.2 K), against an MTT of 373.12 K (water, core's default). The default,
  every reaction counted, is kept: `hazard.reactions` is not used, since the TsCl's hydrolysis is
  a real heat on a cooling failure, and counting it is the conservative side. Gas release at
  core's worst moment (14404 s, just after the dosing) 0.134 mol/s, 11.8 m3/h of HCl at 298.2 K,
  0.08 of the 150 m3/h header (D-014); at the end of the dosing (14400 s), with the accumulated
  ClSO3H, 14.1 m3/h, 0.09 of it, the largest over the batch (`vent_gas_rate` over the cooling
  profile, as for R101). Both are the ASSUMED 10 % vented share of the HCl formed
  (`batch.vent.fraction`, D-006: the split of normal operation at 288 K, not known for a cooling
  failure). With all the HCl formed leaving, the release is about 118 m3/h at core's worst
  moment and about 141 m3/h at the end of the dosing, 0.79 to 0.94 of the header. The
  dilution heat adds 14.2 K to dT_ad (the hand estimate of 1.9.0 said about 11 K, D-015) but
  nothing to the accumulation or the MTSR (it is released as the mass mixes in).
- No TD24 is known for the reaction mass, the sulfonyl chlorides or the wet cake (never
  estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
Sensitivity (a scratch copy with every rate constant of R101 and Q101 divided by 10 and by 100;
nothing else changed; not committed):

| case | R101 accumulation | R101 MTSR | R101 post-reaction | R101 HCl at core's worst moment | R101 largest HCl over the batch | Q101 accumulation | Q101 MTSR | Q101 HCl at the end of the dosing (core's worst moment) | cycle, batches/a at the same batch |
|---|---|---|---|---|---|---|---|---|---|
| k (design) | 1.69 % | 343.6 K | 0.07 h | 60.3 m3/h | 145.5 m3/h, 0.97 (end of the salt, 338.3 K) | 0.16 % | 298.2 K | 14.1 m3/h (11.8 at 14404 s) | 13.85 h, 572 |
| k/10 | 7.64 % | 362.4 K | 2.1 h | 132.7 m3/h | 150.2 m3/h, 1.00 (end of the salt, 339.2 K) | 1.59 % | 298.2 K | 14.0 m3/h (1.0 at 14999 s) | 15.88 h, 499 |
| k/100 | 27.1 % | 420.1 K | 26.6 h | 1302 m3/h | 1302 m3/h, 8.7 (end of the toluene; end of the salt 195 m3/h, 1.30) | 15.4 % | 298.2 K | 13.5 m3/h (0.10 at 25593 s) | 40.4 h, 196 |

MTT 383.75 K (R101) and 373.12 K (Q101) in every case. The gas release columns were added on
core 1.9.0 (scratch copies again, 2026-11-06; the other columns reproduce): m3/h of HCl at
101.3 kPa(a), per batch (the same 13.85 h of flows in every case), against the vent capacity of
150 m3/h (D-014). Core gives the release only at its worst moment, the moment of the highest
MTSR (R101: the end of the toluene dosing, 25200 s, in every case); the largest over the batch
is core's `stirred_tank.vent_gas_rate` at every point of the cooling profile, at that point's
MTSR, with its ratio to the vent. Q101's values are the ASSUMED 10 % vented share (about ten
times as much if all the HCl formed left, D-006). Without a TD24 there is no class; on
MTSR against MTT alone, R101 at k and k/10 lies below the MTT (Stoessel class 1 or 2, depending
on where the MTT lies against MTD24), at k/100 above it (class 3, 4 or 5): toluene would boil
in a cooling failure. Q101 stays below the MTT in every case: the large water heel, not the
dosing, keeps the quench safe on this screening; its real risks are local boiling and HCl
release at the dosing point and a blocked vent, which the screening does not cover. Core's
worst moment for Q101 is set by the flat TSHP MTSR (298.2 K in every case) and moves after the
post-reaction at k/10 (14999 s) and k/100 (25593 s), once the accumulated ClSO3H has hydrolysed:
its gas value there (1.0 and 0.10 m3/h) is only the slow TsCl hydrolysis and leaves the
accumulated ClSO3H out. At the end of the dosing, with 0.16, 1.59 and 15.4 % of the ClSO3H
accumulated, a cooling failure gives 14.1, 14.0 and 13.5 m3/h: the release does not shrink with
slower kinetics.
Interpretation: R101 is dosing-controlled only if the sulfonation is fast; a ten times slower
rate is still tolerable thermally but lengthens the cycle by 2 h, and a cooling failure at the
end of the salt addition then releases 150.2 m3/h, the vent's capacity (132.7 m3/h at core's
worst moment); even at the design rates that moment uses 0.97 of the vent; a hundred times
slower one makes the design unsafe and the cycle impractical, and its 1302 m3/h of HCl is 8.7
times the vent (design finding, D-014). Calorimetry (heat of reaction, heat-flow profile,
accumulation, gas release rate, TD24 of the mass and the product) decides this before basic
engineering. Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of dried p-TsCl from the flowsheet's year averages;
toluene linked to btx-1 (a co-product of its reformate extraction, by that dataset's mass
allocation; hda-1 left its toluene to the shared background instead, this entry takes the
library producer), caustic soda to chlor-alkali-1, the nitrogen consumable to asu-1's gaseous
nitrogen (`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other background a gap
with the activity it should connect to. Chlorosulfonic acid has no library producer and no
shared vocabulary entry: its proxy, SO3 + HCl in their stoichiometric 0.687 and 0.313 kg per kg
(SRC-6: the industrial route), is recorded in lca.yaml and here and not linked, since
sulfuric-acid-1's SO3 is internal to it and a stoichiometric proxy would leave out the oleum
handling (CONTRIBUTING, "Gaps": a correct gap rather than a doubtful link). Ammonium chloride is
a gap as well.
Per batch, not in the flowsheet (core ADR 0053, library ADR 0035): nitrogen 175 kg (about 140
Nm3: R-101's purge, F-101 pressed for three filtrations, DR-101's vacuum broken twice; ASSUMED),
0.100 kg per kg; rinses of Q-101 and F-101, 2 x 1 m3 (ASSUMED), 1.14 kg per kg, to the
wastewater treatment. R-101 is not rinsed: it is kept dry.
Per kg p-TsCl: chlorosulfonic acid 2.32 kg, toluene 0.612 kg, ammonium chloride 0.160 kg,
caustic soda 50 wt% 0.871 kg, water 12.66 kg (plus 1.14 kg of rinses), electricity 0.193 kWh,
LP steam 0.340 kWh, cooling water 0.610 kWh removed, brine 0.811 kWh removed (of it 0.435 kWh
the quench Q5, with 0.127 kWh of the dosed acids' dilution heat, 0.202 kWh the dryer's vacuum
condenser Q8 and 0.094 kWh the wash water's chilling Q9), waste acid 12.6 kg,
scrubber liquor 3.02 kg. Not counted: the scrubbed vent's traces, the toluene vapour the HCl
strips from R-101 (core 1.10.0's vent vapour on a scratch copy: about 0.29 g per kg, D-015),
the dryer's vacuum vent (emission_exclusions).

## D-013 Dedicated train (2026-11-05)
Decision: R-101, Q-101, F-101, DR-101 and T-201 make only p-TsCl, batch after batch: 571.8
batches in 7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, shared tank farms and acid recovery. p-TsCl is often made on
multipurpose plants, or alongside the ortho isomer for saccharin: there the burden per kg differs.

## D-014 Core 1.9.0: duties from the models, the dilution heat apart, the vent capacity (2026-11-06)
Decision, on the core pin's rise to 1.9.0 (314642c):
- **Duties from the models (core ADR 0059).** R101, R102 and Q101 name their cooling stream
  (`energy_port: q`), and `cheme process propagate --fill` writes Q2, Q3 and Q5 as `calculated`.
  Under 1.9.0 the hand values were `cheme.process-duty` warnings at R102 (Q3 3.719 against the
  model's 3.763 kW) and Q101 (Q5 54.948 against 38.920 kW); Q2 agreed (23.339 kW). Q3's model is
  the better value (a Hess path at the heat's own 298.15 K, D-009), so the hand value is dropped:
  Q3 3.719 -> 3.763 kW. Q5's hand value held a heat the model leaves out, the dilution of the
  acids dosed into the heel (lesson L-2, kept from the review of #391): it is split. Q5 is now
  the model's 38.920 kW; the dilution, 16.026 kW, is its own stream Q10 (ASSUMED, its arithmetic
  in the source) from Q101's second energy port to the brine terminal. Both reach the LCI:
  product:BRINE stays 0.811 kWh/kg (102.363 -> 102.361 kW, the model's rounding), product:CW
  0.609 -> 0.610 kWh/kg (76.928 -> 76.972 kW, Q3's rise). (Superseded under core 1.10.0 by
  D-015: Q10 is gone, Q101's model writes the dilution into Q5.) Q7 (the scrubber) stays hand
  arithmetic: its model lacks NaCl's and NaOH's heat capacities, and the HCl goes from the vent
  gas into the liquor, a phase change the conversion duty does not take (`cheme.process-duty`
  info); Q1, Q4 and Q9 are pass-through steps and Q8 the dryer's condenser, none of them a model.
- **Default MTT (core ADR 0058).** `hazard.mtt` is dropped from R101 and Q101: core's default now
  leaves a vent component out, which is what the hand value stood for, and gives the same 383.75
  K (toluene) and 373.12 K (water).
- **Vent capacity (core ADR 0058).** `hazard.vent_capacity: 150` m3/h on R101 and Q101,
  ASSUMED: R-101's vent line and the scrubber T-201 are sized for the recipe's normal peak,
  144.9 m3/h of HCl at 338 K while the salt goes in, rounded up (no vent sizing yet: there is no
  P&ID). Q-101's vent joins the same header; while Q-101 doses, R-101 is emptying into it and
  gives off no gas, so the header's 150 m3/h is Q-101's. Core takes the gas release only at the
  moment of the highest MTSR: 60.3 m3/h for R101 (0.40 of it, the end of the toluene dosing) and
  11.8 m3/h for Q101 (0.08), within the vent (`cheme.reactor-hazard-vent`, info). The largest
  cooling-failure release over the batch (D-011) is R101's at the end of the salt addition,
  145.5 m3/h (0.97), and Q101's at the end of the dosing, 14.1 m3/h (0.09). Q101's values are the
  ASSUMED 10 % vented share of the HCl formed (`batch.vent.fraction`, D-006); with all of it
  leaving, about 118 m3/h at core's worst moment and 141 m3/h at the end of the dosing, 0.79 to
  0.94 of the shared header.
- **`hazard.reactions` not used.** SULP sets R101's MTSR, the main reaction; in Q101 the TsCl's
  hydrolysis sets it, a real heat and the conservative choice (D-011).
- **Design finding: the vent has about 3 % margin at the design rates, is at its capacity at
  k/10 and is exceeded at k/100.** The vent sized for normal operation (144.9 m3/h) holds a
  cooling failure at the end of R-101's salt addition at the design rate laws with about 3 %
  margin (145.5 m3/h, 0.97), is at its capacity at k/10 (150.2 m3/h, 1.00) and is exceeded at
  k/100 (1302 m3/h at the end of the toluene dosing, 8.7 times; D-011). The capacity is kept at
  150 m3/h with this statement rather than raised: nothing yet sizes a larger vent, and a larger
  number would only move the finding. Since the rates are ASSUMED, basic
  engineering needs: (1) reaction calorimetry with the gas release rate (D-005, D-011); (2) the
  toluene dosing interlocked to stop on a cooling failure, a high temperature, the agitator's
  stop and a high vent flow, since the screened MTSR and gas release assume the dosing stops at
  the worst moment; (3) R-101's emergency relief (a bursting disc to a catch tank and the
  scrubber) sized by a DIERS two-phase method from that calorimetry for a gassy runaway, not
  from the normal vent; (4) the next batch's salt addition in R-101 (145 m3/h) held while Q-101
  is in an upset, so the shared header carries one vessel's gas at a time: Q-101's release with
  all the HCl formed leaving is up to about 141 m3/h (0.94 of the header), so the header has no
  room for both; (5) the salt addition in R-101 interlocked to stop the salt feed (no further
  portion) on a loss of cooling, a high temperature, the agitator's stop and a high vent flow,
  since the largest release of a cooling failure comes from the NH4Cl accumulated at the end of
  the addition (0.97 of the vent at k, 1.00 at k/10).
Rejected: keeping Q5 as one hand value (the warning would stay, and the model's part would not
follow its inputs); adding the dilution as a heat of reaction (it is no reaction, and it would
enter dT_ad and the MTSR as a reaction heat rather than a mixing heat released as the mass mixes
in); a vent capacity larger than the normal design (nothing in this entry sizes one; the
interlocks (2) and (5) and the relief (3) from calorimetry are the measures instead).
Not applicable: recycle tears (core ADR 0060), as no stream returns.

## D-015 Core 1.10.0: the quench's dilution heat from the model, the vent's vapour not adopted (2026-11-06)
Decision, on the core pin's rise to 1.10.0 (c55e9c7):
- **The dosed acids' heat of solution (core ADR 0063) replaces the hand stream Q10.** Q101's
  dose S8 gives `heat_of_solution: {H2SO4: -75000, PTSA: -20000, OTSA: -20000}` kJ/kmol,
  ASSUMED, the same effective integral heats of dilution to the liquor's about 10.6 wt% H2SO4
  that D-005 and Q10's hand arithmetic used (no open calorimetry of this liquor). Q10 (16.026
  kW, assumed), Q101's port `dil`, the block port `chw_dil` and the brine port `q101dil` are
  removed. The model releases the heat at the dose's rate, so:
  - **duty**: `cheme process propagate --fill` writes Q5 54.946 kW (was 38.920): reactions
    36.514, the dose cooled 2.406 and the term `solution` 16.026 kW. It equals 1.9.0's Q5 + Q10
    (38.920 + 16.026) and the hand Q5 of 1.8.0 (54.948 kW, the 0.002 kW its rounding);
    product:BRINE stays 0.811 kWh/kg (102.361 kW), of it Q5 0.435 kWh/kg;
  - **jacket check**: Q-101's peak cooling duty is 190.5 kW (12.74 kW/m3, was 135 kW and 9.03
    kW/m3) against the 210.3 kW the brine jacket removes at the charge, `cheme process recipe`,
    no `cheme.recipe-jacket` finding: the 55.5 kW added by hand in D-003 is now the model's, and
    the 4 h dosing stays;
  - **dT_ad**: Q101's rises from 24.9 to 39.1 K (`heat_of_solution` 14.2 K, a note in
    `cheme process reactor-hazards`); the MTSR (298.2 K), the accumulation and the gas release
    are unchanged, since the heat is released as the mass mixes in and nothing of it accumulates.
  - **The model disagrees with the hand estimate of dT_ad, and the model is right.** D-011 said
    the dilution "adds about 11 K". Core's dT_ad of 24.9 K is HYD's alone (the largest reaction
    run to completion, 0.5609 kmol/h x 180 MJ/kmol = 100965 kJ/h); the hand value scaled it by
    the dilution's share of all four reactions' heat (57694 / 131451 kJ/h x 24.9 K = 10.9 K)
    instead of HYD's (57694 / 100965 x 24.9 K = 14.2 K). Both heats are over the same heat
    capacity of the whole batch, so 14.2 K is the consistent value; D-011 is corrected. It moves
    no conclusion: 39.1 K is still far below the 85 K from T_p to the MTT (373.1 K), and the
    MTSR, which sets the class, does not take it. (Core's dT_ad is the largest single reaction
    by convention; Q101's four reactions consume different reactants, so their sum, 43.3 K, plus
    the 14.2 K would be the batch's whole potential, 57.5 K, still below the 85 K.)
  Reason: the feature models the step at least as credibly as the hand stream (the same
  ASSUMED heats, now released at the dose's rate and counted where the hand value was not: the
  model's peak, the jacket check and dT_ad), and it reproduces the hand duty to 0.002 kW. The
  heats themselves stay an open input (calorimetry of the quench).
- **The vent's vapour (core ADR 0062) is not adopted on R101 or Q101; L-5 is quantified, not
  closed.** On a scratch copy (not committed) R101 got `vent.vapour: {components: [TOL]}` with
  toluene's Antoine constants (the NIST WebBook's fit, a 4.07827, b 1343.943, c -53.773, log10
  bar, 308.5-384.7 K, SRC-11, the page not re-read in this session; chemicals 1.5.2's packaged
  Poling constants give the same 22.5 kPa at 338 K) and a heat of vaporization of 35.9 kJ/mol at 338 K
  (ASSUMED: Watson from the WebBook's 38.0 kJ/mol at 298 K; chemicals 1.5.2's packaged Perry
  correlation gives 35.96). The toluene carried off is 0.000397 kmol/h (0.29 g per kg product),
  0.033 mol% of the vent's 1.207 kmol/h of HCl; it changes Q2 by -0.015 kW (23.339 -> 23.324,
  the vapour's latent heat 0.004 kW and a little less toluene reacting), the MTSR by -0.03 K and
  the gas release at the MTSR from 60.28 to 60.34 m3/h (vapour share 0.003). The toluene stays
  so low because the sulfonation keeps its accumulation at most 1.7 %. It does not matter for
  the scrubber's load or the heats. Adopting it would carry toluene into the scrubber T-201, a
  conversion step with one outlet, so the balance would put it in the liquor instead of the
  scrubbed gas (the emission it is). The chlorosulfonic acid's own vapour, likely the larger
  condensable over a liquid that is mostly ClSO3H at 338 K, cannot be modelled: no open vapour
  pressure was found (none in chemicals 1.5.2's packaged tables either; searched 2026-11-06).
  Q101's water vapour is by hand 1.6 % of its vent gas (Raoult over x_H2O 0.93 at 288 K, 1.705
  kPa, CoolProp's IAPWS water), irrelevant to the aqueous scrubber. `vent.henry` is not used for
  the quench's HCl: HCl is a strong electrolyte in the dilute liquor, its partial pressure is not
  linear in its mole fraction, and no sourced constant for this liquor was read; the ASSUMED 10 %
  `fraction` (conservative for the vent, D-006) stays. No vent condenser: nothing to condense.
- **Not used**: `still.column` and `purity` (ADR 0061): there is no distillation; `batch.heat_up`
  on R101: the acid's heat-up is E101 on LP steam (Q1) while R101's energy port is the cooling
  water of the sulfonation, so one duty stream cannot hold both utilities; `vessel.
  metal_heat_capacity`: no vessel masses are known, and R-101's metal would lengthen its heat-up
  and cool-down, the bottleneck's cycle and so the batch size (L-6's fixed point): an open input
  for basic engineering, the metal stays out of the jacket times (D-003).
Rejected: keeping Q10 (a hand copy of what the model now holds, and the jacket margin and dT_ad
by hand); adopting the vent vapour for a 0.03 mol% effect that would put the toluene in the
wrong outlet.

## Core features used (cheme-as-code 1.10.0)

Core 1.10.0 part:

| feature | where | ADR |
|---|---|---|
| a dose's `heat_of_solution`: in the semi-batch's duty (term `solution`), its peak cooling duty and the recipe's jacket check, and in dT_ad (not the MTSR) | Q101's dose S8 (the acids' dilution heat; Q5 54.946 kW, the jacket's 190.5 kW peak, dT_ad 39.1 K), D-015 | 0063 |

Tried on a scratch copy and not adopted (D-015): `batch.vent.vapour` on R101 (toluene 0.033
mol% of the vent). Not used: `still.column`, `purity`, `still.condenser_port` (ADR 0061, no
distillation); `vent.condenser`, `vent.henry` (ADR 0062); `batch.heat_up`, `still.heat_up`,
`vessel.metal_heat_capacity` (ADR 0063).

From core 1.9.0 and before:

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with two sequential doses (`start`) and a `target` | R101 (salt, then toluene), Q101 (the mass into the heel) | 0050 |
| `batch.vent` with `fraction` | R101 (all HCl), Q101 (10 % of the HCl) | 0054 |
| recipe vent report (peak kmol/s, m3/h, kg per batch) | the scrubber load, D-007 | 0054 |
| the screening of a vented semi-batch; the default MTT of what boils, the vent's HCl left out (1.9.0) | R101, Q101, D-011, D-014 | 0050, 0054, 0058 |
| each reaction's MTSR, the MTSR over the batch, the gas release at the MTSR against `hazard.vent_capacity` (1.9.0) | R101, Q101, D-011, D-014 | 0058 |
| duties written by the models at `energy_port` (1.9.0): an isothermal semi-batch, a conversion step | Q2 (R101), Q3 (R102), Q5 (Q101), D-009, D-014 | 0059 |
| `crystallizer.spectators` with `measured_in: pure_solvent` and `salting_out` | CR101, W101, W102 | 0056 |
| several crystallizer inlets (a reslurry wash) | W101, W102 | 0056 |
| `solid_separation.filtration` and recipe `filter` `from:` | F101, F102, F103 | 0057 |
| `dryer:` with energy, drying rate, cake density; recipe `dry` `from:`; `vessel.heated_area` | D101 | 0057 |
| recipe `units:` (one vessel over several steps) | R-101 (E101, R101, R102), Q-101 (E102, Q101, CR101), F-101 (five steps) | 0057 |
| vessel sizing and jacket check, `heat`/`cool` times from the jacket | R-101, Q-101 | 0052 |
| per-batch LCA consumables | nitrogen, rinses | 0053 |
Not used: the batch still (ADR 0055): there is no distillation in this route; `dosing.absorbed`:
nothing is dosed as a gas; `hazard.reactions` (D-014); recycle `tears:` (ADR 0060): no recycle.

## Core limits hit (for core issues)

- L-1: a recipe vessel over `units` holding a batch step is sized from that step's model alone.
  R102, a conversion step after R101 in the same vessel, adds the second acid portion (1.16 m3
  a batch), so the sized 3.15 m3 would have held 3.11 m3 at 99 %. R-101's volume is given (4 m3)
  and the check passes against R101's 2.04 m3 only. Core should size a `units` vessel from the
  largest content of any of its steps (as it already does for a dryer's vessel), and check the
  jacket against every step's duty.
- L-2 (resolved in core 1.10.0): the semi-batch counted no heat of dilution or mixing of a dosed
  liquid: the H2SO4 and the sulfonic acids dosed into the quench heel release about 58 MJ per
  hour of flows (30 % of the quench's heat), which was missing from the model's duty, the jacket
  check and dT_ad; under 1.9.0 it was the hand stream Q10 and a hand jacket margin (D-003,
  D-009, D-014). Core 1.10.0's `dosing.heat_of_solution` (ADR 0063) takes it into Q5, the peak
  cooling duty and dT_ad (D-015). Left: one integral heat per component, constant over the
  dosing (the real heat of dilution falls as the liquor gets more dilute), and the heats
  themselves are ASSUMED.
- L-3: one recipe vessel may hold only one batch or semi-batch step, and a semi-batch is
  isothermal at one temperature. The patent's second stage (cool to 35 C, add acid, hold 1 h,
  an equilibrium the excess acid drives) is therefore a conversion step with an ASSUMED
  conversion, not a rate model, and the cool-down between the stages is a recipe operation
  outside both models. Core would need either a temperature programme in one batch, or several
  batch steps in one vessel run in sequence. Related: a `transfer` that is the next vessel's
  dosing cannot take `from:` that dosing; R-101's 4 h transfer is written by hand to match
  Q101's dosing.
- L-4: the crystallizer takes one crystallizing solute and has no second liquid phase. The
  ortho isomer, an oil in the quench, is a spectator that divides with the aqueous liquor, so
  the product's ortho content (0.007 wt%) is a lower bound (D-007); an oil phase wetting the
  cake, or a second crystallizing isomer, cannot be expressed. Its hydrolysis is a homogeneous
  rate on a dissolved pseudo-component.
- L-5: the vent has no solubility (Henry) model: the 10 % of the quench's HCl that leaves is a
  vent `fraction`, not a result, and the toluene and water vapour the HCl strips is not in the
  off-gas (ADR 0054's known limits). The scrubber's load is right for HCl, not for its vapours.
  Partly addressed by core 1.10.0 (ADR 0062), not adopted (D-015): the vent's vapour, run on a
  scratch copy, puts R-101's toluene at 0.033 mol% of the off-gas (0.29 g per kg product) and
  Q-101's water at about 1.6 % by hand, so the scrubber's load stands; the chlorosulfonic acid's
  vapour has no open vapour pressure, and the scrubber, a conversion step with one outlet, has
  no gas outlet for what passes it. The quench's HCl split stays a `fraction`: `vent.henry`
  needs a sourced constant, and HCl in the dilute acid is no Henry's-law gas.
- L-6 (as NBS L-6): core propagates from the feeds and does not solve them for a product rate,
  and the batch size and the cycle depend on each other through the jacket's heating and cooling
  times; both were iterated by hand (scaling the feeds, then a fixed point of batch size =
  rate x cycle). A `batch_size: from: cycle` or a product-rate target would remove this.
- L-7: there is no ice (a melting sink) in the quench, and no liquor enthalpy for the acid: the
  heel is cooled water on a brine jacket (D-006). Partly resolved in core 1.9.0: the semi-batch
  and conversion duties Q2, Q3 and Q5 now come from the models (ADR 0059, D-014); the heat-ups,
  the coolers, the dryer's condenser and the scrubber are still hand arithmetic (D-009); the
  dilution heat is the model's since core 1.10.0 (L-2, D-015).
- L-8 (resolved in core 1.9.0): until 1.8.0 the screening gave no gas rate at a cooling failure
  and no comparison with the vent (D-011 named only the vent's normal peak). Core 1.9.0 reports
  the gas release at the MTSR against `hazard.vent_capacity` (ADR 0058, D-014); the pressure of
  a blocked vent is still not screened (no head space or relief model). Core takes that release
  only at the moment of the highest MTSR, not the largest over the batch: R101's largest, at the
  end of the salt addition, and Q101's, at the end of the dosing, come from `vent_gas_rate` over
  the cooling profile (D-011), and the test checks them.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batches R101, Q101: composition, vent, accumulation, MTSR, peak cooling, gas release at the MTSR | done in cheme, kinetics ASSUMED | D-005, D-011, D-014, `cheme process reactors`, `reactor-hazards` |
| duties Q2, Q3, Q5 (Q5 with the dosed acids' heat of solution) | done in cheme (the models' duties, core ADRs 0059, 0063), heats ASSUMED | D-009, D-014, D-015 |
| second stage R102, scrubber S101 | conversion steps, conversions ASSUMED | D-005, D-007 |
| batch recipe, cycle time, basis check, vessels, jackets, vent loads | done in cheme | D-003, `cheme process recipe` |
| precipitation and wash losses | done in cheme: crystallizers with spectators, solubility ASSUMED, no salting-out | D-007, core ADR 0056 |
| ortho isomer | spectator in the liquor (a lower bound in the product) | D-007, L-4 |
| filtration | specified split in cheme; time by Ruth, cake data ASSUMED | D-007, core ADR 0057 |
| drying: outlets, duty Q6, drying time | done in cheme, moisture and rate ASSUMED | D-008, core ADR 0057 |
| feeds for 1000 t/a, the other duties (Q1, Q4, Q7, Q8, Q9) | hand (ratios scaled; arithmetic in the sources) | D-004, D-009, L-6, L-7 |
| per-batch exchanges (nitrogen, rinses) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Open inputs
Kinetics, heats of reaction and the gas release rate (calorimetry), TD24 of the reaction mass and
the product; the gas release rate of a runaway and R-101's emergency relief (D-014); the second stage's conversion against time and temperature; the solubility of
p-TsCl in the acid liquor; how much of the ortho oil the cake keeps (the product's o-TsCl
content and its assay, D-002); the heat of dilution of the 50 wt% caustic (D-009); the heats of dilution of the acids dosed into the quench (D-015); the vessels' metal for the jacket times (D-015); chlorosulfonic acid's vapour pressure near 338 K, for the vent's vapour (L-5); filtration and wash data and the drying rate from trials; the HCl's split between
vent and liquor in the quench, in operation and at a cooling failure (the screened Q101 release
counts the ASSUMED 10 %, all of it would be up to 141 m3/h, D-011, D-014); the product specification (assay, o-TsCl, TsOH, acidity, water);
acid and HCl recovery (D-010); a TEA (`operation.batch: {recipe: true}`).
