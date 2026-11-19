# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Salicylic acid by the one-stage Kolbe-Schmitt carboxylation of dry sodium phenoxide, issue
ChemE-as-Code/process-library#507, a batch entry of the library and the salicylic acid feed of
`acetylsalicylic-acid-1` (in progress). Concept stage: design basis, batch recipe, balanced
BFD/PFD, thermal screening and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout,
HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Core models what the route needs: semi-batches with a dosed gas that is partly taken up and a
vent (core ADRs 0050, 0054, 0063), the dryer and recipe units over several steps (ADR 0057), the
crystallizer with spectator solutes (ADR 0056), recycles with tear streams (ADR 0060), design
specifications and component separators (ADR 0070), the models' duties (ADR 0059) and the batch
recipe (ADRs 0051, 0052). Library ADR 0035: one dedicated train, campaigns out of scope (D-013).
Templates: `oxalyl-chloride-1` (structure, gas dosing, thermal screening), `n-bromosuccinimide-1`
and `paracetamol-1` (crystallizer, filters, dryer). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, the PMC full text, the Wikipedia page). The
`chemicals` and `thermo` Python packages (SRC-4, SRC-5) were queried for single values, facts
only with their source; the licensed works behind them were not read and are named in each row
(library ADR 0037).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 376 867 A, G. Jansen and P. Wolff, filed 1981-07-07, granted 1983-03-15: Chemical process, https://patents.google.com/patent/US4376867A/en | background: the conventional process takes up CO2 below about 140 C to sodium phenyl carbonate and rearranges it at 150 to 160 C, the unreacted phenol (about 10 to 15 % of the charge) is stripped and recycled; the crude salicylate is dissolved, carbon-treated and precipitated with sulfuric or hydrochloric acid and centrifuged; about 1 t of sodium salicylate in 8 to 10 t of water acidified at 50 to 60 C gives 99.5 % pure acid at about 85 % yield, a second, impure crop at about 25 C recycled brings it to about 95 %; the conventional crude holds 5 to 10 mol% 4-hydroxybenzoic acid. Claims 1 to 6: phenol with aqueous NaOH, the water removed above about 175 C, CO2 at above about 175 C (180 to 220 C) in one stage, a mixer-kneader. Description: phenol about 1:1 with NaOH, a small phenol excess of about 1 to 10 % preferred, below 25 %; NaOH 25 to 55 %; water removed at ambient, then 5 to 100 mm Hg above 165 C; stoichiometric amounts of CO2 fed, absorbed at once even under vacuum (10 to 200 mm Hg in the first part), the pressure rising to 4 to 6 bar and held 0.5 to 4 h; no excess CO2, vent or head-space quantity stated; the absorption is exothermic (no value); the conversion about 85 to 88 % at 165 and 200 C; the kneader of US 3 880 407 (Heinz List). Example I: 23.2 mol phenol, 23.0 mol NaOH as a 40 % solution, dried at ambient, then 30 mm Hg to 190 C; CO2 at 5 mol/h, under vacuum in the first half, 5 bar after 5 h held 1 h; cooled to 100 C, filled with water to a concentrated stock solution (no water quantity or temperature given); 20.4 mol salicylic acid (88 % on phenol), 0.054 mol 4-hydroxybenzoic and 0.026 mol 4-hydroxyisophthalic acid, 1.42 mol phenol. Example 3, runs at 140 to 243 C: by-products have a minimum about 180 to 210 C; incomplete drying (run 3-5) 60 %, 237 to 243 C (run 3-7) 31 % conversion | read (Google Patents); patent, facts only | D-001, D-004 to D-008 |
| SRC-2 | Mohammad, O.; Onwudili, J. A.; Yuan, Q. (2024) Molecules 29(11), 2527, doi:10.3390/molecules29112527, https://pmc.ncbi.nlm.nih.gov/articles/PMC11174078/ | sodium phenoxide suspended in toluene with added phenol (2:1), 225 C, 30 bar CO2, 2 h, 1000 rpm: 92.68 % molar yield of salicylic acid (0.3 g scale); the conventional gas-solid reaction described as slow with poor heat and mass transfer and a hygroscopic phenoxide; work-up with HCl; phenol recovery by distillation or water extraction named, not shown | read; CC BY 4.0, facts only | D-001, D-008 |
| SRC-3 | Wikipedia, Salicylic acid, https://en.wikipedia.org/wiki/Salicylic_acid | solubility in water 1.24, 2.48, 4.14, 17.41 and 77.79 g/L at 0, 25, 40, 75 and 100 C; melting point 158.6 C; density 1.443 g/cm3; pKa 2.97; sublimes at 76 C; decarboxylates slowly to phenol and CO2 at 200 to 230 C; made from sodium phenolate and CO2 (100 atm, 115 C), acidified with sulfuric acid; H302, H318 | read (first part of the page); CC BY-SA, facts only | D-005, D-007, D-008, D-011 |
| SRC-4 | The `chemicals` 1.5.2 package (core's environment): the CRC Handbook tables it packages (`CRC_standard_data`, `CRC_organic_data`, `CRC_inorganic_data`; underlying work: CRC Handbook of Chemistry and Physics), its ATcT formation enthalpies (Active Thermochemical Tables), its ideal-gas heat capacities from Poling, Prausnitz and O'Connell, The Properties of Gases and Liquids, 5th ed., and `iapws95_Tsat`, `iapws95_Psat` (IAPWS-95) | CRC: formation enthalpies phenol (s) -165.1, salicylic acid (s) -589.9, CO2 (g) -393.5 kJ/mol (the acids' reaction, D-005); no entry for sodium phenoxide or sodium salicylate; sodium phenolate melts at 657.15 K, phenol at 314.04 K and boils at 454.95 K; densities and heat capacities of materials.yaml; CO2's S_298. ATcT: CO2's ideal-gas dHf_298 -393.474 kJ/mol (materials.yaml). Poling et al.: CO2's ideal-gas cp polynomial (materials.yaml, as other library entries carry it). IAPWS-95: steam saturation 524.97 K at 4100 kPa and 412.01 K at 350 kPa, water's vapour pressure 19.9 kPa at 333.15 K | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037); the printed handbook, the ATcT and Poling et al. were not read | materials, reactions, D-005, D-009 |
| SRC-5 | The `thermo` 0.6.1 package: method DIPPR_PERRY_8E (underlying work: Perry's Chemical Engineers' Handbook, 8th ed., drawing on DIPPR 801), method HEOS_FIT (a fit to IAPWS-95), method CRC_INORG_L_CONST (CRC Handbook), the ROWLINSON_POLING corresponding-states estimate | DIPPR_PERRY_8E: phenol's liquid density 1023.8 kg/m3 at 353.15 K and latent heats 486.6 kJ/kg at 463.15 K, 588.2 at 333.15 K; HEOS_FIT: water's latent heats 2256.4 kJ/kg at 373.15 K, 2357.7 at 333.15 K; CRC_INORG_L_CONST: sulfuric acid's liquid density 1830 kg/m3; ROWLINSON_POLING: phenol's liquid heat capacity 197.5 kJ/(kmol K) at 353.15 K | open-source package queried 2026-11-19; single values, facts only, with the method named; not open data (library ADR 0037); Perry's, DIPPR 801 and the CRC Handbook were not read | materials, D-006, D-008, scripts/balance.py |
| SRC-6 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-7 | processes/acetone-1, chlor-alkali-1, carbon-capture-1, sulfuric-acid-1 (this library) | phenol, caustic soda 50 wt%, captured dense-phase CO2, sulfuric acid 98.5 wt% | library, internal | D-004, D-012 |

Searched and not found openly (2026-11-19): kinetics or calorimetry of the carboxylation of
sodium phenoxide or of its neutralisation, a formation enthalpy of sodium phenoxide or sodium
salicylate, a TD24 of the dry phenoxide or the crude, the solubility of salicylic acid in sodium
sulfate solutions, a drying rate of a phenoxide kneader, the phenol recovery and the specific
consumptions of a plant.

## D-001 Route and boundary (2026-11-19)
Decision: the one-stage Kolbe-Schmitt carboxylation of SRC-1, as a batch plant:
- R101: phenol (fresh and recovered) neutralised with caustic soda dosed into it, PhOH + NaOH ->
  PhONa + H2O;
- D101: the phenoxide solution dried to a powder in a kneader-reactor, at ambient pressure,
  then at 4 kPa(a) to 463 K;
- R102: CO2 dosed into the dry phenoxide at 463 K, PhONa + CO2 -> sodium salicylate in one step,
  the para acids a small by-product;
- R201: the crude taken up in water and acidified with sulfuric acid at 328 K, 2 NaSal + H2SO4
  -> 2 SA + Na2SO4, the unreacted phenoxide freed as phenol;
- CR201, F201, W201, F203, D201: the first crop crystallised at 328 K, centrifuged, washed with
  water, dried at 333 K; CR202, F202: the mother liquor cooled to 298 K for a second crop that
  goes back to R201;
- M301, X301: the liquors and the condensates collected, 95 % of their phenol recovered for the
  next charge.
Boundary: gate to gate, from phenol, caustic soda, CO2, sulfuric acid and water to the dried
product, the sodium sulfate liquor and the vented CO2.
Reason: SRC-1 is the one open source read with plant-like quantities for every step of the
Kolbe-Schmitt route (the charge ratio, the caustic strength, the drying, the CO2 dose and its
pressure and times, the temperature, the yield, the by-products and the unreacted phenol) and,
in its background, the plant's acidification with the water ratio, temperature and the two
crops. Its one-stage carboxylation above 175 C gives under 0.5 % of non-salicylic acids against
5 to 10 % of the conventional two-stage process, so the work-up needs no sublimation.
Rejected:
- the conventional two-stage process (SRC-1 background, runs A and B): CO2 taken up below
  140 C, then rearranged at 150 to 160 C, 10 to 24 h, 9 to 10 % 4-hydroxybenzoic acid and a
  further 10 % loss to reach 99.5 % purity; worse on every count SRC-1 gives;
- the high-pressure Schmitt variant (SRC-3: 100 atm, 115 C; SRC-2: up to 79 % after 8 h at
  125 C and 82 to 138 bar): no open source with plant quantities read, and the pressure costs
  vessel and compression;
- the suspension Kolbe-Schmitt in toluene with added phenol (SRC-2: 92.68 % at 225 C, 30 bar,
  2 h): a 0.3 g laboratory result, a solvent to recover, 30 bar, and no work-up beyond HCl at
  laboratory scale; a candidate for a later entry once scaled;
- the 4:1 phenol slurry of UK 949 988 (SRC-1 run C): SRC-1 reports it complicated with no
  by-product benefit; not read in the original.

## D-002 Capacity, product and operating hours (2026-11-19)
1000 t/a of dried salicylic acid in 7920 h (330 days), ASSUMED: about the salicylic acid one
aspirin train of `acetylsalicylic-acid-1` takes (0.786 kg per kg of aspirin at 1291 t/a, about
1015 t/a; its process.yaml and lca/inventory.csv at PR #528's head ebe44b3f). The product is the dried first crop, modelled 99.7 wt% (D-008); SRC-1 states
99.5 % for the conventional work-up. A pharmacopoeia grade (colour, ash, phenol and
4-hydroxybenzoic acid limits) is not modelled.

## D-003 Batch basis, recipe and vessels (2026-11-19)
`process/recipe.yaml`: one batch makes 2865.51 kg of S22; the kneader-reactor R-102 is the
bottleneck at 22.7 h (13.95 h drying from D101's rate, 5 h CO2, 1 h hold, venting, cooling and
the water fill), so 349.0 batches a year. The batch size is the fixed point batch = rate x
cycle that `cheme.recipe-basis` names (the drying time grows with the batch), so the flowsheet's
year averages and the recipe agree (no recipe-basis finding). The recipe sizes R-101 (5 m3,
72 % full) and D-201 (8 m3, 51 % full, 11.3 m2). R-102 is sized by hand (`vessel.volume`): core
would size it from R102's content (2.62 m3, 5 m3 at a 60 % fill), but the phenoxide solution it
dries is larger, about 4.23 t a batch, 3.25 m3 at an ASSUMED 1300 kg/m3 (D-006), which needs
5.4 m3 at the kneader's ASSUMED 60 % working fill: the next R10 size, 6.3 m3 (52 % full with
the solution, 42 % with the crude). The larger kneader's heated area sets the drying time and
its free volume the head space's CO2 (D-005). R-201 is sized by hand at 40 m3 (about 36.2 t of
slurry a batch, 87 % full): core sizes no vessel from a conversion step (L-5). Durations other
than the models' are ASSUMED.

## D-004 Feeds and charge (2026-11-19)
- Charge ratio: 23.2 mol phenol per 23.0 mol NaOH (SRC-1 Example I, 0.87 % excess, just below
  its preferred excess of about 1 to 10 %), the recovered phenol S20 counted in it: the design
  specification `phenol` adjusts the fresh phenol S1 to hold the ratio.
- Caustic soda 50 wt% as chlor-alkali-1 delivers it, not Example I's 40 %: SRC-1 allows 25 to
  55 %, and less water to evaporate in the bottleneck.
- CO2: 0.90932 mol per mol NaOH dosed, from carbon-capture-1 let down to 700 kPa(a): what
  reacts in Example I (0.88954 mol per mol) and what fills R-102's head space at the end of the
  hold (0.01978 mol per mol, D-005; scripts/balance.py). SRC-1 feeds stoichiometric amounts;
  Example I's 5 mol/h over 5 h (25 mol for 23.0 mol of NaOH) is a laboratory autoclave's and
  gives no vent, so it is not scaled up as an excess.
- Sulfuric acid 98.5 wt% (sulfuric-acid-1), 0.51 mol per mol of sodium (2 % excess, ASSUMED).
- Water: 9 kg per kg of sodium salicylate formed to dissolve the crude (ASSUMED from SRC-1's
  background, where the conventional process acidifies about 1 t of sodium salicylate in 8 to
  10 t of water; D-007), 2.0 kg per kg of caustic to wash the cake (ASSUMED, about 1.4 kg per kg of
  crystals).
- The design specification `rate` adjusts the caustic S3 for 1000 t/a of S22, the CO2, the
  dissolution water, the acid and the wash water following it at the ratios above (core ADR
  0070). Per kg of product: phenol 0.711 kg, caustic 50 wt% 0.675 kg, CO2 0.338 kg, sulfuric
  acid 0.429 kg, water 12.1 kg.

## D-005 Reactors R101 and R102: semi-batches, kinetics and heats (2026-11-19)
- R101: the caustic dosed over 1 h into the molten phenol at 343.15 K, isothermal, held to
  0.999 conversion of the NaOH; NEUT second order, k 1.0 m3/(kmol s) at 343 K, Ea 20 kJ/mol,
  ASSUMED; heat -30 kJ/mol ASSUMED (no formation enthalpy of sodium phenoxide found).
- R102: the CO2 dosed at a constant rate over 5 h into the dry phenoxide at 463.15 K (190 C,
  the end of SRC-1's drying and within Example 3's optimum), held 1 h. SRC-1 feeds
  stoichiometric amounts, reports the CO2 absorbed at once (under vacuum for the first half) and
  the pressure rising to 5 bar only at the end. The dose is therefore what reacts in Example I,
  20.48/23.0 x 0.999 = 0.88954 mol per mol of NaOH, and what then fills R-102's free volume:
  6.3 m3 less the crude's 2.62 m3 at 463.15 K and an ASSUMED 500 kPa(a) (SRC-1's "5 bar" read
  as absolute; as gauge it would be 20 % more), by the ideal gas 0.478 kmol (21.0 kg) a batch,
  0.01978 mol per mol of NaOH (scripts/balance.py). Of the dose 0.97825 is taken up
  (`absorbed`); the rest is the head space's CO2, let down to the vent S8 after the hold
  (0.0073 kg per kg of product). The model holds the powder at 101.325 kPa(a) and sends that
  share to the vent through the dosing (L-2), so its vent rate during the dosing (3.6 m3/h in
  `cheme process recipe`) is not the plant's; the plant's vent load is the let-down (D-011).
- CARB and PARA second order in the phenoxide and the CO2 taken up, k 0.01 m3/(kmol s) at
  463 K, Ea 60 kJ/mol, ASSUMED fast (SRC-1: absorbed at once); PARA's rate constant 0.003922 of
  CARB's, Example I's (0.054 + 0.026)/20.4, the two by-product acids lumped as one
  4-hydroxybenzoate each. R102 converts 89.0 % of the phenoxide; the salicylate formed is
  87.8 % of the phenol charged per batch, SRC-1's 88 %.
- Heats: CARB and PARA -50 kJ/mol ASSUMED with CO2 as the dosed gas. The one related figure is
  the acids' reaction, phenol (s) + CO2 (g) -> salicylic acid (s), -31.3 kJ/mol from the CRC
  Handbook formation enthalpies packaged in chemicals 1.5.2 (single values queried, the
  handbook not read; SRC-4); the salts'
  heat is taken larger so that the screening is not optimistic. To be measured.
- Unreacted phenol: Example I finds 1.42 mol of phenol in the stock solution; the model carries
  2.52 mol of unreacted phenoxide per 23.0 mol (the 1.10 mol difference is not explained by
  SRC-1: phenol lost in the drying vapour, or tar). The model's fresh phenol is therefore a lower
  bound: if the 1.10 mol were lost, 4.7 % more phenol would be needed (D-012).

## D-006 Drying the phenoxide D101 (2026-11-19)
Core's dryer: water and phenol evaporate to 0.2 wt% left (ASSUMED; SRC-1 shows that incomplete
drying lowers the conversion to 60 %), at 463.15 K; the heat is the solution's sensible heat
(3.0 kJ/(kg K) ASSUMED), the latent heats (water at 373.15 K, where most of it boils off at
ambient pressure; phenol at 463.15 K; SRC-5) and the 6.3 m3 kneader's metal (6300 kJ/K, about
12.6 t of steel, ASSUMED) at 80 % efficiency: Q2 83.3 kW year average, 0.659 kWh/kg, from HP
steam through a hot-oil circuit (the drying ends at 463 K; LP or MP steam is too cold). The
drying time, 13.95 h, follows from an ASSUMED 10 kg/(m2 h) on R-102's heated area. The vapour
(62.5 kg/h, 1.6 wt% phenol: the charge's excess) is condensed in E-102 (Q8, D-009) and collected
for the phenol recovery. Core reports the dryer's duty but does not write it (L-6), so Q2 is
entered as assumed from `cheme process crystallizers`.
The solution charged (S4) is about 66 wt% sodium phenoxide, 33 wt% water and 0.5 wt% phenol
(the 50 wt% caustic's water and the neutralisation's); its density, ASSUMED 1300 kg/m3, sizes
R-102 (D-003). Whether it stays liquid at 343 K for the transfer from R-101 (no open solubility
of sodium phenoxide in water read) is an open input; if not, R-101 would run hotter or the
caustic be charged less concentrated.

## D-007 Acidification R201 and the two crops (2026-11-19)
- R201: a conversion step, every sodium salt (salicylate, phenoxide, 4-hydroxybenzoate and the
  NaOH left) to its acid and sodium sulfate, at 328.15 K (SRC-1: 50 to 60 C).
- Before the water fill the crude and the kneader are cooled from 463 to 373 K (SRC-1 Example
  I: cooled to 100 C, then filled with water), through the hot-oil loop to cooling water: E103,
  a cooler step, Q9 11.9 kW (the crude 5.0 kW, the metal 6.9 kW; scripts/balance.py). So the
  crude S28 enters the acidification at 373 K, and core's conversion duty (Q4) counts its
  sensible heat from 373 K, the dissolution water's from 298 K (ASSUMED, process water at
  ambient) and the acid's heat (-60 kJ per mol of sulfuric acid, ASSUMED): 32.6 kW net heating,
  the water must be warmed to 328 K.
- The dissolution water, about 30.9 t a batch, does not fit the 6.3 m3 kneader. SRC-1 fills the
  autoclave with water "to a concentrated stock solution" and gives no quantity: about 1.2 t
  goes into the kneader (ASSUMED, up to its 60 % working fill with the crude's 2.6 m3) and the
  stock solution is pumped to R-201, which holds the rest, both at 298 K. One conversion step
  carries both parts, so the heat balance is whole; the kneader's metal cooled further by the
  fill (373 to about 343 K, about 2.3 kW) warms the water and is not credited against Q4
  (conservative). The 9 kg of water per kg of salicylate is the conventional process's dilution
  for the acidification (SRC-1 background), taken here for R-201, not for the kneader fill.
- CR201 (328.15 K) and CR202 (298.15 K): core's crystallizer with the solubility of salicylic
  acid in water (SRC-3's points, g/L taken as kg per kg of water, interpolated linearly by core:
  0.00983 at 328.15 K) and the liquor's other solutes as spectators without a salting-out
  correction (no data; L-4). The first crop holds 90.0 % of the acid in R201's outlet, the
  second crop (S19) goes back to R201; together 96.6 % of the salicylate formed is isolated,
  between SRC-1's 85 % (first crop) and about 95 % (with the second crop) of the conventional
  process, whose crude holds more by-products.
- The second crop's cooling to 298 K is on chilled water (Q5, 48.3 kW, core's crystallizer duty).

## D-008 Separation, washing, drying and phenol recovery (2026-11-19)
- F201, F203: a peeler centrifuge, 99.5 % of the crystals to the cake, 0.15 kg of liquor per
  kg (ASSUMED); W201: a reslurry wash on the centrifuge with water at 298 K, the acid dissolving
  to saturation (core's crystallizer); F202: a nutsche, 99 %, 0.3 kg/kg.
- D201: core's dryer at 333.15 K to 0.2 wt% volatiles: salicylic acid sublimes from 76 C
  (SRC-3), so the drying stays below it, at an ASSUMED 10 kPa(a) (water's vapour pressure at
  333.15 K is 19.9 kPa, SRC-4); Q6 21.1 kW (L-6 as D101); the vapour is condensed in the vacuum
  condenser E-202 on cooling water (Q10, D-009). The product is 99.7 wt%
  salicylic acid, 0.08 wt% sodium sulfate, 0.2 wt% water.
- X301: a component separator (core ADR 0070), 95 % of the phenol in the collected liquors and
  condensates back to T-101, ASSUMED (SRC-1: the unreacted phenol is recyclable; SRC-2 names
  distillation or water extraction). The method (a solvent extraction of the acidic liquor and
  the solvent stripped) and its solvent are open; its steam is ASSUMED 2 kWh per kg of phenol
  recovered (Q7, 22.7 kW). The rest of the phenol, 0.04 wt%, goes with the liquor to treatment.

## D-009 Utilities and heat (2026-11-19)
Every energy flow per hour of the year average:
- Q1 5.85 kW and Q3 11.5 kW: core's semi-batch duties of R101 and R102 to cooling water (R102
  through the kneader's hot-oil loop, which also heats the drying);
- Q8 43.0 kW, Q9 11.9 kW and Q10 12.7 kW to cooling water (scripts/balance.py, library ADR
  0027; no core model gives them): E-102 condensing the drying vapour S6 at the latent heats
  D101 uses and the condensate cooled to 313 K; the crude and the kneader's metal cooled from
  463 to 373 K before the water fill (D-007); E-202 condensing the product dryer's vapour S23 at
  D201's latent heats and the condensate cooled to 303 K. The cooling water is 85.1 kW, 0.674
  kWh/kg;
- Q2 83.3 kW (HP steam 4100 kPa(a), 525 K saturation) and Q6 21.1 kW (LP steam 350 kPa(a)):
  core's dryer model; Q4 32.6 kW (LP steam): core's conversion duty; Q5 48.3 kW (chilled water
  278/283 K): core's crystallizer duty; Q7 22.7 kW (LP steam): ASSUMED; LP steam 76.4 kW,
  0.605 kWh/kg;
- power: agitators 2 + 4 kW, the kneader's drive and vacuum pump 20 kW, the centrifuge 4 kW, the
  dryer 3 kW, the phenol recovery's pumps 2 kW, year averages ASSUMED: 0.277 kWh/kg.
- Not counted, each estimated: the phenol tank's trace heating (heat losses of an insulated
  tank at 343 K, about 1 kW, ASSUMED); the drying vapour's superheat in the vacuum stage (the
  last of the water, under 1 kW); the kneader's metal cooled further by the water fill (about
  2.3 kW, a credit to Q4 left out, D-007); the product and D-201's metal cooled from 333 to
  303 K before discharge (about 1.4 + 0.7 kW, cake 1.3 kJ/(kg K) and 2000 kJ/K as D201's).
  Together about 5 kW, under 2 % of the 328 kW counted (heat and power).

## D-010 Wastes and emissions (2026-11-19)
The liquor after phenol recovery (13.27 kg/kg: 4.5 wt% sodium sulfate, dissolved salicylic and
4-hydroxybenzoic acids, 0.04 wt% phenol, 0.06 wt% sulfuric acid) goes to the site's wastewater
treatment; no sulfate recovery. The CO2 not taken up (0.0073 kg/kg, the head space's 0.478 kmol
a batch at an ASSUMED 500 kPa(a), D-005) is let down to the vent after the hold; it could be
recompressed to the next batch (not modelled). Phenol vents of the
phenol tank and the neutraliser, the dryer's dust and the recovery unit's losses are not
estimated (`emission_exclusions`).

## D-011 Thermal screening (2026-11-19)
`cheme process reactor-hazards`, screening values only:
- R101: dT_ad 70.4 K, the caustic's accumulation 0.30 %, MTSR 343.4 K against an MTT of
  373.15 K (water's boiling point, a lower bound of the solution's bubble point; R-101 vented to
  atmosphere through its condenser).
- R102: dT_ad 229.4 K for the dry powder (its heat capacity small, the ASSUMED -50 kJ/mol);
  the CO2's accumulation 0.51 %, MTSR 464.4 K against an ASSUMED MTT of 493.15 K (220 C, the
  top of SRC-1's range: above it SRC-1 loses conversion to phenol's vapour pressure, and
  salicylic acid decarboxylates at 200 to 230 C, SRC-3).
- Gas at a cooling failure: the screening finds none at the MTSR, which is below 473 K, the
  lower end of SRC-3's decarboxylation range (given for the free acid; R102 holds its sodium
  salt, so the bound is taken as conservative). The 0.51 % accumulation rests on the ASSUMED
  fast kinetics; it is also bounded physically: the CO2 not yet taken up is at most the head
  space's 0.478 kmol against about 21.5 kmol taken up a batch, 2.2 %, which would add about 5 K
  (MTSR about 468 K), still below 473 K. dT_ad's 229 K would need the whole dose to accumulate,
  which the dosing trips prevent. A decomposition that forms gas (decarboxylation of the
  salicylate to phenol and CO2 above about 473 K, on a fire or a hot-oil control failure) is
  not screened: no TD24 or decomposition data (open input with R-102's relief).
- Vent: the plant's vent load is the head space let down after the hold, 0.478 kmol of CO2 in
  the recipe's 0.25 h, about 73 m3/h at 463 K and 101.325 kPa(a) (scripts/balance.py), within
  the ASSUMED 100 m3/h vent capacity. The model's vent flow during the dosing (3.6 m3/h) is an
  artefact of `absorbed` (L-2). Overpressure from the CO2 supply: it is let down to 700 kPa(a),
  below R-102's ASSUMED design pressure of 10 bar(g). R-102's relief device and its sizing case
  (fire, decomposition) are an open input, as in oxalyl-chloride-1.
- The large dT_ad makes R102 dosing-controlled: the CO2 feed must trip on high temperature and
  on the kneader's drive stopping (the powder no longer renewed at the wall). No criticality class without a TD24 (open input). Hazards of the materials (no data copied): phenol toxic and
  corrosive to skin, hot caustic phenoxide, salicylic acid eye damage (SRC-3: H302, H318), CO2
  asphyxiation from the vent.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
`lca/lca.yaml`: every exchange per kg of S22, the rinses of R-201, C-201 and V-202 (1.5 t a
batch, ASSUMED) as a per-batch consumable. Linked: phenol to acetone-1, caustic soda to
chlor-alkali-1, CO2 to carbon-capture-1 (its dense-phase product let down; the compression
burden carried, conservative), sulfuric acid to sulfuric-acid-1, the steam as heat delivered.
Gaps: water, power, cooling water (0.674 kWh/kg with the condensers and the cool-down, D-009),
chilled water, wastewater treatment. The vented CO2 (the head space's, D-005) is a fossil
emission (captured from a fossil point source), 0.0073 kg/kg. The fresh phenol is a lower bound
(D-005). One product, no allocation.

## D-013 Dedicated train (2026-11-19)
T-101, R-101, R-102, E-102, R-201, C-201, V-202, F-202, D-201, E-202, T-301 and X-301 make
only salicylic acid, batch after batch: 349.0 batches in 7920 h (ASSUMED, library ADR 0035).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| feeds for 1000 t/a and the charge ratio | done in cheme (design specifications) | D-004, core ADR 0070 |
| second-crop and phenol recycles | done in cheme (tears S19, S20) | D-007, D-008, core ADR 0060 |
| semi-batches R101 and R102: accumulation, MTSR, duties Q1, Q3 | done in cheme, kinetics and heats ASSUMED | D-005, D-011, core ADRs 0050, 0054, 0059 |
| dryers D101, D201: product, vapour, drying times | done in cheme; duties Q2, Q6 from core's report | D-006, D-008, core ADR 0057, L-6 |
| acidification R201 and its heat Q4 | done in cheme (conversion step), heats ASSUMED | D-007 |
| crystallisation CR201, CR202, W201 and Q5 | done in cheme, solubility SRC-3, no salting-out | D-007, core ADR 0056 |
| filters, phenol recovery | specified splits | D-008 |
| condensers E-102, E-202, the kneader's cool-down E103 (Q8 to Q10), the CO2 dose's head-space share | scripts/balance.py (checked by scripts/check_balance_scripts.py) | D-005, D-007, D-009, library ADR 0027 |
| batch recipe, cycle, R-101, D-201 | done in cheme; R-102 (from the solution it dries) and R-201 by hand | D-003 |
| LCI inventory | done, five backgrounds linked | D-012 |

## Core features used (core 1.12.0)

- `reactor: semibatch` with `batch.dosing`, `target`, `time`, `heat: isothermal` (ADR 0050);
  a dosed gas with `absorbed` and `batch.vent` (ADR 0054); `energy_port` duties (ADR 0059);
  `hazard.mtt` and `hazard.vent_capacity` (ADR 0058).
- `dryer:` with `energy` and `drying_rate` on two steps (ADR 0057); `crystallizer:` with
  solubility `points`, spectators and `energy` (ADR 0056); `solid_separation:`.
- `recovery:` component separator and two `specs:` (a feed with followers, a ratio target),
  solved with the `tears:` (ADRs 0060, 0070).
- `process/recipe.yaml` with `units` over several steps, `dose`/`react`/`dry` `from:` the
  models, vessel sizing (ADRs 0051, 0052, 0057); `lca.yaml` `consumables` with `per_batch`
  (ADR 0053), `emission_exclusions`.

## Core limits hit (each a candidate core issue)

- L-1: a gas-solid reaction. The dry phenoxide powder (it melts at 657 K) is carried
  pseudo-homogeneously in a liquid semi-batch: its volume and heat capacity as if it were a
  liquid, the CO2 dissolving in it. A gas-solid batch reactor (uptake limited by the renewed
  surface, the kneader's mixing) would let the CO2 uptake and the 5 bar end follow from the
  powder, not from `absorbed`.
- L-2: one pressure per semi-batch. SRC-1 starts the dosing under vacuum and ends at 5 bar as the
  head space fills; the model holds 101.325 kPa(a) and sends the CO2 not taken up straight to the
  vent through the dosing (`absorbed`), so it cannot show the pressure rise or the let-down after
  the hold (the head space's CO2 is sized by hand, D-005), and the vent warns that CO2 forms in no
  reaction (accepted in `checks/checks.yaml`). A recipe vessel sizes from one unit's content:
  the kneader's two units (the solution D101 dries, the crude R102 holds) need R-102 sized by
  hand (D-003).
- L-3: drying to dryness in a vessel that then reacts: core's dryer gives the evaporation and
  the heat at one temperature and pressure (463 K), not the ambient-then-vacuum programme of
  SRC-1, and has no endpoint model (the residual water that sets the conversion, SRC-1 run 3-5,
  is an input).
- L-4: no salting-out data: the solubility of salicylic acid is the pure-water one in a 5 wt%
  sodium sulfate liquor (`salting_out` coefficients 0, ASSUMED); and SRC-3's g/L values are
  taken per kg of water.
- L-5: core sizes no vessel from a conversion step (R-201, ACIDIFY), and a conversion step has no
  dosing time: R-201 is sized by hand and the acid's dosing time is ASSUMED.
- L-6: core's dryer reports its duty (`cheme process crystallizers`) but does not write it on its
  energy stream (ADR 0059 covers the semi-batches, stills, crystallizers and conversion steps):
  Q2 and Q6 are entered as assumed with the report's value.

## Open inputs
Kinetics and heat of the carboxylation and the neutralisation by reaction calorimetry; the TD24
of the dry phenoxide and of the crude; the heat of the acidification; the solubility of
salicylic acid in sodium sulfate liquors at 298 to 328 K; the kneader's drying rate and
endpoint; the fate of SRC-1's 1.10 mol of phenol not found (D-005); the phenol recovery's method,
solvent and steam; the product specification; R-102's relief device and its sizing case (fire,
decomposition), the CO2 vent's routing and SRC-1's "5 bar" as absolute or gauge; the density
of the phenoxide solution and whether it stays liquid at 343 K (D-006); the share of the
dissolution water in the kneader (D-007); prices and a TEA.
