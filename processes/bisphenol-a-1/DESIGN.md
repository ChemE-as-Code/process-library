# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Bisphenol A from phenol and acetone, issue ChemE-as-Code/process-library#510. Concept stage:
design basis, balanced BFD/PFD with core's conversion, crystallizer and filter models and the
recycle solved by core, the duties core cannot calculate by hand, and a preliminary gate-to-gate
LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` at c04ed69, core pin b97a833 (cheme-as-code
1.13.0). Templates: `phthalic-anhydride-1` (continuous concept entry: source register, limits,
LCA layout), `biodiesel-1` (liquid-phase conversion steps with liquid heat capacities, recycle at
a tear with design specifications) and `oxalyl-chloride-1` (source register, LCA layout).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 391 997 A, General Electric, published 1983-07-05: Ion exchange catalyzed bisphenol process, https://patents.google.com/patent/US4391997A/en | description: phenol to acetone about 2:1 to 10:1, up to 30:1; 50-120 C (preferably 60-80 C); WHSV 0.05-15; acetone conversion 20-82 %; resin with 5-35 % of its acid sites modified by a mercapto group; the flow scheme: evaporation of acetone, water and phenol, adduct crystallization, centrifuge with a phenol wash, mother liquor (70-85 % phenol, 5-15 % p,p-bisphenol A, the rest by-products) partly cracked at 150-300 C over an aluminium alkoxide and partly isomerised over resin and recycled. Examples: three 25 mm jacketed tubes in series, Amberlite-118 with about 10 % of the sites neutralised by 2-mercaptoethylamine, phenol to acetone 10.7 (printed "10:7:1"), WHSV 7.3, acetone conversion about 69 %; Table I: at 60/70/80 C 95.40 wt% p,p-, 3.80 wt% o,p-bisphenol A and 0.80 wt% others in the products (the other profiles 94.09-95.17, 3.73-4.56 and 0.92-1.35) | read (Google Patents); patent, facts only | D-001, D-005, D-008, reactions |
| SRC-2 | US 5 723 688 A, Dow Chemical, published 1998-03-03 (family of EP 0 720 976): Process for preparing an adduct of a bisphenol with a phenolic compound, https://patents.google.com/patent/US5723688A/en | description: phenol to carbonyl 2:1-45:1 (preferably 4:1-14:1), 35-100 C (preferably 45-85 C), promoted sulfonated polystyrene resin in a fixed bed; the product mixture (10-27 wt% bisphenol, preferably 15-26; water 1-18 wt%, preferably 2-12; acetone 0.1-8 wt%) crystallised without a distillation at 25-75 C and 5-950 mbar (preferably 30-280 mbar), 0.1-24 h, cooled by evaporating water, acetone and some phenol; the adduct 1:1; wash 0.1-2.2 parts per part of adduct at 30-95 C with phenol polished on a strong-acid cation and a strong-base anion resin (40-120 C); phenol distilled from the melted adduct at 70-260 C (preferably 150-230 C) and 2-650 mbar (preferably 5-180 mbar). Example 1: reactor at 56 C; crystallizer feed 25.2 % bisphenol A, 6.9 % water, 1.2 % acetone at 65 C, crystallizer at about 40 C and 50 mbar; wash 1:0.6; product 0.12 % impurities, 5 APHA, against 0.32 % and 15 APHA with a distillation first (Example 2) | read (Google Patents); patent, facts only | D-001, D-004, D-005, D-007, D-009 |
| SRC-3 | US 6 960 697 B2, Mitsubishi Chemical, published 2005-11-01: System and method of producing bisphenol-A (BPA), https://patents.google.com/patent/US6960697B2/en | background: purification and recovery about half or more of the capital. Example 1 (simulated): 70 000 t/a (9112 kg/h), acetone conversion about 80 %, phenol to acetone 15 at the reactor; fixed-bed reactor about 200 m3 at about 77 m3/h, 75 C, 4.4 bar; DTB adduct crystallizer about 150 m3 at 84 m3/h, 51 C, about 95 % recovery; cooling duty 1.2 million kcal/h latent heat and 0.4 million kcal/h heat of fusion; filter liquid 76 325 kg/h, solid 15 161 kg/h | read (Google Patents); patent, facts only | D-002, D-005, D-007, equipment |
| SRC-4 | US 4 950 806 A, Mitsui Toatsu Chemicals, published 1990-08-21: Process for crystallizing adduct of bisphenol A with phenol, https://patents.google.com/patent/US4950806A/en | description: water added at 2-20 wt% of the phenol solution evaporates and takes the heat of cooling and crystallization; crystallizer at 20-100 mmHg; jacket on hot water at most 5 C above the contents against scale. Example 1: 40 % bisphenol A solution, 400 kg/h at 90 C, crystallizer at 50 mmHg and 50 C, water 40 kg/h, jacket 52 C; crystals 0.4 mm, 0.05 % by-products, 5 APHA | read (Google Patents); patent, facts only | D-007, equipment |
| SRC-5 | US 4 950 804 A, Mitsui Toatsu Chemicals, published 1990-08-21: Process for producing high-purity bisphenol A, https://patents.google.com/patent/US4950804A/en | description: hydrochloric acid catalyst, phenol to acetone 4:1-12:1 at 40-70 C, the product mixture distilled under vacuum to remove water, acetone and HCl. Example 1: product 54 % phenol, 35 % bisphenol A, 2 % by-products, 4 % water, 5 % HCl; dehydrochlorination at 70 mmHg and 120 C to 10 ppm HCl; crystallizer at 50 mmHg and 45 C, the water-phenol recycle through a weak-base resin (adduct 2 ppm HCl against 10 without) | read (Google Patents); patent, facts only | D-001 (rejected route) |
| SRC-6 | European Union (2010) Risk Assessment Report, 4,4'-isopropylidenediphenol (bisphenol-A), environment addendum of April 2008, EUR 24588 EN, https://publications.jrc.ec.europa.eu/repository/bitstream/JRC59980/lbna24588enn.pdf | section 1.2.1 (p. 5): commercial purity 99-99.8 %, phenol below 0.06 %, the isomers below 0.2 %, water below 0.2 %; Table 1.1 (p. 5): flash point about 207 C, autoflammability about 532 C, minimum explosive concentration 0.012 g/l (oxygen above 5 %); Table 2.1 (p. 6): EU use 1996-1999, 71.1 % polycarbonate, 25.0 % epoxy resins; Table 2.2 (p. 7): Western Europe 2005/2006 production 1 150 000 t/a, polycarbonate 865 000 t/a, epoxy resins 191 520 t/a; Table 3.2 (p. 10): releases of six production sites in 2006, to air 0.06 to 575 kg/a (dust or vapour) and to water after treatment 6.8 to 113 kg/a per site. Table 3.3 (p. 11) is on PVC additive sites, not bisphenol A production (the issue's reading of it was corrected) | read (PDF text extracted); EU publication, facts only | D-002, D-010 (hazards), D-014, benchmarks |
| SRC-7 | chemicals 1.5.2 and thermo 0.6.1 (the versions core pins; open source, MIT), used directly: formulas, CAS, molar masses and normal boiling points (`search_chemical`, `MW`, `Tb`: phenol CRC_ORG, acetone and water HEOS, bisphenol A YAWS, the o,p-isomer and the chroman JOBACK); formation enthalpies (`Hfs`: phenol and bisphenol A CRC; `Hfl`: acetone CRC, water ATCT_L; `Hfg`: bisphenol A YAWS, the o,p-isomer and the chroman JOBACK) and fusion enthalpies (`Hfus`: phenol CRC, bisphenol A JOBACK); liquid heat capacities (acetone and water HEOS_FIT; phenol and bisphenol A by chemicals' Rowlinson-Bondi method on the TRCIG and Joback ideal-gas heat capacities, Tc and omega IUPAC/PSRK and YAWS); vapour pressures (phenol WAGNER_MCGARRY) and heats of vaporization (phenol DIPPR_PERRY_8E, acetone and water HEOS_FIT) | values printed in materials.yaml, reactions.yaml and the hand calculations below | single values with their source, facts only, not open data (library ADR 0037); none of the works behind the packages' methods (the CRC Handbook, Yaws' handbook, Perry's / DIPPR 801, ATcT, CoolProp, Joback and Reid, Wagner and McGarry, Rowlinson-Bondi) was read: the values are taken as the packages hold them | materials, heats of reaction, latent heats |
| SRC-8 | processes/acetone-1 (this library) | process.yaml chemistry, lca/dataset.yaml: phenol (product:PHENOL) and acetone (product:ACETONE) from cumene, 1.59 kg phenol per kg acetone | library | D-003, D-014 |
| SRC-9 | PubChem compound 6623 (bisphenol A), https://pubchem.ncbi.nlm.nih.gov/compound/6623 (PUG REST synonyms and properties) | InChIKey IISBACLAFKSPIT-UHFFFAOYSA-N, formula C15H16O2, cross-reference CHEBI:33216 | read (2026-11-19); public data, facts only | registry entry |

No open source with a plant's utility consumption per tonne of bisphenol A was read in this
work (the EU LVOC BREF was not searched for one; Ullmann's is licensed and not read).

## D-001 Route and boundary (2026-11-19)
Decision: bisphenol A by condensation of phenol with acetone over a promoted sulfonated
polystyrene-divinylbenzene resin in staged fixed beds (SRC-1, SRC-2); the effluent crystallised
without a distillation as the 1:1 adduct with phenol by vacuum-evaporative cooling (SRC-2,
SRC-4); the adduct filtered and washed with polished phenol, melted and stripped of phenol under
vacuum (SRC-2); the mother liquor isomerised over resin and recycled, part of it purged to a
phenol-recovery (cracking) still (SRC-1); the crystallizer's condensate split in a column into
acetone and phenol back to the reactor and water to treatment. Continuous, one train. Boundary
feeds: phenol, acetone, demineralised water, electricity, LP and HP steam; outputs: bisphenol A
melt, the still's residue (tar), phenolic wastewater, heat to cooling water.
Reason: the issue's scope; SRC-2 states that resin catalysts are now the common choice because
the acid need not be removed, and its crystallization without a distillation gives a purer
product (0.12 % against 0.32 % impurities) in a simpler plant.
Rejected:
- The hydrochloric acid route (SRC-5, and SRC-2's background): the acid must be distilled off
  (dehydrochlorination under vacuum) and corrodes the plant; the HCl recovery and the corrosion
  make it the older route.
- A distillation of water, acetone and some phenol ahead of the crystallizer (SRC-1's flow
  scheme, SRC-2's Example 2, SRC-4): one more column and a less pure adduct (SRC-2).
- A second, aqueous or solvent crystallization of the product (SRC-1's crystallizer 50, SRC-3's
  acetone-water crystallizer) or melt crystallization: a higher grade for optical polycarbonate;
  kept as an option, the adduct route alone meets the commercial purity of SRC-6.
- The DTB crystallizer with acetone and water as solvents of SRC-3: an advanced variant; its
  sizes are used for scale only (D-005, D-007).
Links to other library processes: phenol and acetone from acetone-1 (cumene hydroperoxide
route, SRC-8). No library process consumes bisphenol A yet (polycarbonate, epoxy resins).

## D-002 Capacity and operating hours (2026-11-19)
Decision: 70 000 t/a of bisphenol A in 8000 h, 8750 kg/h, held by the design specification
`rate` (propagate varies the fresh acetone). Reason: SRC-3's simulated plant is 70 000 t/a, a
world-scale single train for the time; Western Europe made 1.15 Mt/a in 2005/2006 (SRC-6, Table
2.2). 8000 h ASSUMED.

## D-003 Feeds (2026-11-19)
Decision: fresh phenol (molten, 333 K) and acetone taken as pure, from a cumene-phenol plant
(acetone-1, SRC-8). The feed specifications (water, cresols, hydroxyacetone, mesityl oxide)
are open inputs; a real plant polishes the phenol (D-004) for exactly these traces.

## D-004 Phenol polishing (2026-11-19)
Decision: the fresh, stripped and recovered phenol are collected (T-101) and polished on a
strong-acid cation and a strong-base anion resin bed at 338 K (V-101) before they go to the
adduct wash and the reactor, as SRC-2's Figure 1 describes (IX101, a pass-through: the beds'
effect on traces is not modelled). The mother liquor's own polishing bed (SRC-2) is left out.

## D-005 Reactor (2026-11-19)
Decision: three fixed beds of a sulfonated polystyrene-divinylbenzene resin with about 10 % of
its acid sites promoted with 2-mercaptoethylamine (SRC-1), down-flow, 333 K in and 353 K out
(SRC-1's best profile, example 3: 60/70/80 C), phenol to acetone 10 mol/mol at the inlet
(design specification `ratio`, propagate varying the fresh phenol make-up; SRC-2 prefers 4-14,
SRC-1's examples 10.7). Conversion model (reactions.yaml): 69 % of the acetone per pass (SRC-1's
examples), split by SRC-1's Table I, example 3, into p,p-bisphenol A (94.868 % of the acetone
converted), the o,p-isomer (3.779 %) and the "others" (1.354 %, carried as the chroman of SRC-2's
impurity list, two acetone each). The laboratory selectivities and conversion are transferred
to the plant's feed, which also holds the recycled bisphenols and by-products: ASSUMED (the
recycled by-products' equilibrium with the isomer is not modelled). Size: about 157 m3 of bed
for 60.6 m3/h, SRC-3's 2.6 h space time; about 4.5 bar(g) (SRC-3: 4.4 bar).
Result (core's conversion-step duty, D-006): the reaction heat raises the feed by about 20 K,
so the beds run almost adiabatic and the interstage coolers take only 32 kW (Q2): the ascending
profile of SRC-1 comes from the reaction heat itself. The effluent holds 18.5 wt% bisphenol A,
inside SRC-2's 15-26 wt%.

## D-006 Heats of reaction and what core can and cannot calculate (2026-11-19)
Decision: liquid-basis heats of reaction from SRC-7's formation enthalpies: BPA_FORM -72.0
kJ/mol (bisphenol A and phenol as solids plus their fusion enthalpies; the fusion enthalpy of
bisphenol A is a Joback estimate), the isomer 2.36 kJ/mol less (gas-phase difference), the
by-product lump twice BPA_FORM (ASSUMED). Liquid heat capacities in materials.yaml (phenol and
bisphenol A by Rowlinson-Bondi, an estimate; the isomer equal to bisphenol A; the chroman
scaled). With them core calculates the duties of R101 (conversion step), R301 (adiabatic,
`process/simulation.yaml`), M301 (conversion step with the adduct's heat of fusion, D-009) and
X201 (crystallizer energy balance, D-007). Everything else (the feed heater, the columns and the
still) is a hand calculation (D-011): no property package of core covers bisphenol A, its
isomer or the adduct (`cheme process props --coverage`, L-3).

## D-007 Crystallizer and filter (2026-11-19)
Decision: the reactor effluent, with 1300 kg/h of demineralised water dosed, goes without a
distillation to one vacuum crystallizer at 318 K and about 5 kPa(a) (SRC-2: about 40 C and 50
mbar; SRC-4: 50 C and 50 mmHg), draft-tube type with its jacket at most 5 K above the contents
(SRC-4). Modelled in two steps because core's crystallizer evaporates only its solvent (L-2):
- FL201, the vapour space and the vacuum condenser: 85 % of the water, 95 % of the acetone and
  1 % of the phenol evaporate (ASSUMED) and are condensed (S12);
- X201, core's crystallizer: solute bisphenol A, solvent phenol, crystal the 1:1 adduct (a
  solvate with one phenol, which core takes as a hydrate of phenol), basis imposed yield 0.75
  (ASSUMED: the mother liquor then carries 6.0 wt% bisphenol A, inside SRC-1's 5-15 wt%; no open
  solubility of the adduct in phenol was read, L-1), spectators acetone, water, the isomer and
  the by-products. Energy: liquor heat capacity 2.07 kJ/(kg K) (materials.yaml), heat of
  crystallization -110.46 kJ per kg of adduct from SRC-3's example (0.4 million kcal/h for
  15 161 kg/h), the feed at the mixed temperature of S9 and S10 (350.99 K, hand calculation).
  Core's duty: 1.53 MW (Q4).
- Hand check of the evaporative cooling (the water dose's basis): the vapour of FL201 (2077.8
  kg/h water at 43.13 kJ/mol, 984.6 kg/h acetone at 29.82 kJ/mol, 467.5 kg/h phenol at 56.32
  kJ/mol, all at 318 K, SRC-7) carries 1599.9 kW of latent heat against the 1526.6 kW of Q4,
  4.8 % more (the vapour's own sensible cooling from 351 K is not in Q4). The crystallizer feed
  then holds 3.8 wt% water and 1.6 wt% acetone, inside SRC-2's 2-12 and 0.1-8 wt%.
- F201, core's filter with a displacement wash: all crystals to the cake (fines not modelled),
  cake liquid 0.25 kg/kg (ASSUMED), wash 0.6 kg of polished phenol per kg of adduct (SRC-2's
  Example 1; design specification `wash`, propagate varying the split of SP101), efficiency 0.8
  (ASSUMED): 2.1 % of the cake's mother liquor stays in it. The cake carries 3.09 t/h of phenol
  liquor with the 12.35 t/h of adduct.
Rejected: external cooling of the crystallizer through its wall (SRC-4: scale on a cooled wall);
a centrifuge (SRC-1) is equivalent at this level.

## D-008 Mother liquor, purge and condensate (2026-11-19)
Decision: the filtrate and the washings (52.6 t/h) are collected; 5 % is purged to a cracking
still C302 (ASSUMED share), the rest passes an isomerisation bed of resin R301 (SRC-1's stream
28), which turns 30 % of the o,p-isomer to p,p-bisphenol A (ASSUMED: SRC-1 gives no conversion),
and returns to the reactor feed. The still recovers 95 % of the purge's phenol overhead (ASSUMED)
and leaves the bisphenols and by-products as a residue (384 kg/h) to incineration; the cracking
of bisphenols back to phenol and isopropenylphenol that SRC-1 describes is not modelled (L-4),
which is conservative for the phenol and acetone use. The condensate column C401 (a column with a
phenol-water decanter, lumped) returns 99.5 % of the acetone and 98 % of the phenol with 3 % of
the water to the reactor (ASSUMED); the rest of the water, with about 0.5 wt% phenol, goes to
biological treatment. The loop's steady state: the mother liquor holds 88.1 wt% phenol, 6.0 wt%
bisphenol A, 2.1 wt% isomer and 2.9 wt% by-products; SRC-1 gives 70-85 % phenol, so the
by-products in this loop are on the low side (the purge share and the isomerisation are the open
inputs that set them).

## D-009 Melting and phenol stripping (2026-11-19)
Decision: the washed cake is melted on HP steam and heated to 453 K (M301, a conversion step
`ADDUCT_MELT`, kind phase-change, with the heat of fusion of D-007; core's duty 1.56 MW, Q6), and
the phenol is stripped in a vacuum column (about 3 kPa(a) at the top, 493 K at the bottom; SRC-2:
150-230 C, 5-180 mbar) to about 35 wt-ppm in the product (C301, recovery 99.995 %, ASSUMED). The
product: 8750 kg/h of 99.96 wt% bisphenol A (isomer 160 ppm, by-products 220 ppm), inside the
commercial 99-99.8 % and the impurity limits of SRC-6 (phenol below 0.06 %, isomers below 0.2 %).
The impurities taken into the adduct crystals themselves are not modelled (L-1): only those in
the cake's liquor reach the product, so the purity is an upper bound. Prilling or flaking is
outside the boundary (SRC-2).

## D-010 Recycle solution (2026-11-19)
Decision: two tears, S7 (the mixed reactor feed) and S5 (the wash phenol), and three design
specifications (rate, ratio, wash), solved together by `cheme process propagate` (Newton with
Broyden's update; tolerance abs 0.001 kg/h, rel 1e-7, below the flowsheet's). Every component
has an exit: water to the wastewater, acetone mostly recycled (0.5 % to the wastewater), phenol
to the product, the tar and the wastewater, the bisphenols and the by-products to the product
and the tar. The loop converges in 8 iterations, worst residual about 4e-6 kg/h.

## D-011 Hand-calculated duties and powers (2026-11-19)
With the liquid heat capacities of materials.yaml and SRC-7's latent heats (arithmetic in the
flowsheet's sources):
- Q1, feed heater: S7 from 321.79 K (mixed, hand) to 333.15 K, 414.2 kW (LP steam).
- Q7, Q8, phenol stripper: reflux ratio 0.2 (ASSUMED) on 70.97 kmol/h phenol at 53.57 kJ/mol
  (360 K, 3 kPa(a)), the bottoms heated 453 to 493 K, the overhead's sensible heat credited:
  reboiler 1123.2 kW (HP steam), condenser 1350.0 kW.
- Q10, Q11, cracking still at atmospheric pressure, reflux ratio 0.5 (ASSUMED): 686.7 kW and
  628.3 kW.
- Q12, Q13, condensate column, reflux ratio 2 (ASSUMED): 716.0 kW (LP steam) and 526.6 kW.
- Powers (ASSUMED allowances, no open figure read): crystallizer circulation, agitation and
  vacuum with the main liquor pumps 150 kW (Q3), filter 100 kW (Q5), stripper vacuum and melt
  pumps 80 kW (Q9).
- Steam levels: LP 450 kPa(a); HP 4000 kPa(a) (523.5 K) for the 493 K stripper bottoms (hot oil
  an alternative). No heat integration is attempted (the stripper's condenser at about 360 K
  could heat the feed: an open option).

## D-012 Equipment (2026-11-19)
First sizes in equipment/equipment-list.yaml: R-101 about 157 m3 of resin bed (SRC-3's space
time), X-201 about 103 m3 working (SRC-3's 1.8 h; SRC-2: 0.5-6 h). Column stages, filter area,
resin volumes of V-101 and R-301 and the tanks are not sized.

## D-013 Hazards (noted, not designed) (2026-11-19)
- Phenol is toxic and corrosive, also through the skin, and is handled molten (above 314 K):
  closed systems, heat tracing, nitrogen blanketing; acetone is highly flammable. Not quantified
  here (no safety data sheet read in this work).
- Bisphenol A dust in prilling and bagging (outside the boundary): SRC-6 gives a minimum
  explosive concentration of 0.012 g/l, a flash point of about 207 C and an autoflammability of
  about 532 C; the melt at 493 K is above the flash point (nitrogen blanketing of the melt tanks).
- The condensation is mildly exothermic: `cheme process reactor-hazards` (core 1.13.0) screens
  R101 with the whole feed as accumulation: dT_ad 31.6 K, MTSR 364.7 K from 333.1 K (BPA_FORM
  and DIANIN_FORM govern; the flowsheet's beds rise by 20 K at 69 % conversion), R301 0.1 K;
  M301 is a phase change and not screened. MTT, TD24 and the class stay open (info findings
  cheme.reactor-hazard-missing). Read for a liquid-full resin bed: a cooling failure cannot raise
  the liquor above about 365 K, below phenol's normal boiling point (455 K) and well below the
  stripper's own 493 K; the limit that matters is the resin's thermal stability (sulfonic acid
  groups and the promoter degrade at high temperature; no open limit read), so a high-temperature
  trip on the beds belongs to basic engineering.
- The vacuum equipment (crystallizer, stripper) can draw in air: oxygen in hot phenol and
  bisphenol A gives colour bodies, and acetone vapour with air is flammable; nitrogen breaks the
  vacuum.
- Resin: life, regeneration and make-up are open inputs; spent resin is a solid waste not
  counted (D-014).

## D-014 Preliminary gate-to-gate LCI (2026-11-19)
Decision: lca/lca.yaml, functional unit 1 kg of bisphenol A melt at the gate (S26); every
foreground exchange from the balanced flowsheet. In core's screening the backgrounds are
unmapped (`missing:` naming what each connects to). In the library's Atlas build
(build_lci.py) phenol and acetone link acetone-1's products (lca/mappings.yaml), the LP and HP
steam are counted as heat delivered (`steam-heat`), electricity, cooling water, demineralised
water and wastewater link through the shared lci/mappings.yaml by their chemical slugs; the tar
to incineration stays a gap. No emission to air or water is in the balance (the vacuum vents are
not designed): SRC-6's six production sites released, after treatment, 228.6 kg/a of bisphenol
A to water and up to 984.7 kg/a to air (four of the six as dust) in 2006; over the 1 150 000 t/a
of Western Europe (ASSUMED to be those sites' output) that is about 0.2 g/t to water and 0.86
g/t to air, recorded as emission exclusions, not as exchanges.
Inventory per kg of bisphenol A (`cheme assess lca --write`): phenol 0.8631 kg, acetone 0.2642
kg, demineralised water 0.1486 kg, electricity 0.0377 kWh, LP steam 0.129 kWh, HP steam 0.385
kWh; outputs: tar 0.0439 kg, wastewater 0.232 kg, heat to cooling water 0.464 kWh. Phenol and
acetone yields 95.5 % and 96.3 % of the stoichiometric 0.8245 and 0.2544 kg/kg; the losses are
the tar (no cracking modelled, L-4) and the wastewater. `cheme assess lca --balance` closes mass
and every element.
Excluded and listed: vacuum vents and tank breathing, the site effluent's bisphenol A, resin and
promoter make-up and spent resin, nitrogen blanketing; construction, transport, end of life.

## Method and dependency table
| what | how | where |
|---|---|---|
| mixers, splitters, component separators | `cheme process propagate --fill` (mixing, `split:`, `recovery:`) | S3 to S28 |
| reactor R101, isomeriser R301, melter M301 | conversion models; R101's and M301's duties from core's conversion-step model, R301 adiabatic | reactions.yaml, D-005, D-006, D-008, D-009 |
| crystallizer X201, filter F201 | core's imposed-yield crystallizer with its energy balance, core's filter with a displacement wash | D-007 |
| recycle | two tears and three design specifications in propagate | D-010 |
| heater, columns, still | hand calculation, liquid heat capacities of materials.yaml and SRC-7's latent heats, ASSUMED | D-011 |
| LCI | `cheme assess lca --write` | lca/, D-014 |

## Core features used (core 1.13.0)
- `reactor: conversion` with three parallel liquid-phase reactions on one key (R101), its duty
  from the liquid heat capacities (ADR 0059); `kind: phase-change` for the adduct's melting
  (M301), its declared heat in the conversion-step duty;
- `crystallizer:` with a solvate crystal (the adduct as the solute plus one solvent), an imposed
  yield, spectators and the energy balance; `solid_separation:` with a displacement `wash:` and
  a `wash_filtrate` outlet (ADR 0076);
- `tears:` and `specs:` (rate, ratio, a splitter's fraction) solved together (ADR 0060, 0070);
- `recovery:` on component separators; `process/simulation.yaml` `mode: adiabatic` for R301;
- `cheme process reactor-hazards`, `cheme process crystallizers`; `cheme assess lca` with
  `emission_exclusions`.

## Core limits hit (each a candidate core issue)
- L-1: no solubility data model for an adduct in a mixed liquor and no impurity uptake into the
  crystals: the yield is imposed, and the product's purity counts only the cake's liquor. A
  solid-liquid equilibrium of the adduct (bisphenol A, phenol, water, acetone, isomers) and a
  distribution coefficient for the isomer would let core predict both.
- L-2: core's crystallizer evaporates only its solvent: the water and acetone (spectators) that
  carry the evaporative cooling here must be flashed in a separate component separator (FL201),
  and the water dose that matches the latent heat to the crystallizer's duty is a hand check
  (D-007). An evaporation of named spectators, with their latent heats in the energy balance,
  would close it in the model.
- L-3: no property package covers bisphenol A, its isomer or the adduct: the liquid heat
  capacities are estimates (Rowlinson-Bondi on Joback), thermo's VDI_TABULAR liquid heat
  capacity of phenol (919 J/(mol K) at 338 K, about 4.8 times the corresponding-states value) was
  not used, and the columns, heater and still are hand calculations; a shortcut column on a
  component separator (as phthalic-anhydride-1's L-3) would give their duties.
- L-4: the cracking of the purge's bisphenols and by-products back to phenol and
  isopropenylphenol (SRC-1) is not representable without its reaction data; the still is a
  component separator and its residue holds the bisphenols, conservative for the yields.

## Calculation maturity (2026-11-19)
Not evaluated to a level: the conversions and selectivities are transferred from laboratory
examples, the yield, recoveries and splits are assumed, and the energy balance of the columns is
not evaluable in core (L-3). The process.yaml claim stays `concept`.

## Open inputs
Phenol and acetone specifications; the adduct's solubility in the mother liquor and the
isomer's uptake into the crystals; the resin's activity, life and promoter loss; the purge share,
the isomerisation and the cracking still's yields (and the mother liquor's by-product level
against SRC-1's 70-85 % phenol); filter data (cake liquid, wash efficiency); column stages and
reflux; heat integration (the stripper's condenser to the feed); the vacuum vents' treatment and
emissions (SRC-6's site data as a check); prices for a TEA; benchmark ranges for utilities.
