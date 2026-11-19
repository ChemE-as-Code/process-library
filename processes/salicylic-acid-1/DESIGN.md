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
in this work (Google Patents machine text, the PMC full text, the Wikipedia page, and the open
data packaged in the `chemicals` and `thermo` Python packages).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 376 867 A, G. Jansen and P. Wolff, filed 1981-07-07, granted 1983-03-15: Chemical process, https://patents.google.com/patent/US4376867A/en | background: the conventional process takes up CO2 below about 140 C to sodium phenyl carbonate and rearranges it at 150 to 160 C, the unreacted phenol (about 10 to 15 % of the charge) is stripped and recycled; the crude salicylate is dissolved, carbon-treated and precipitated with sulfuric or hydrochloric acid and centrifuged; about 1 t of sodium salicylate in 8 to 10 t of water acidified at 50 to 60 C gives 99.5 % pure acid at about 85 % yield, a second, impure crop at about 25 C recycled brings it to about 95 %; the conventional crude holds 5 to 10 mol% 4-hydroxybenzoic acid. Claims 1 to 6: phenol with aqueous NaOH, the water removed above about 175 C, CO2 at above about 175 C (180 to 220 C) in one stage, a mixer-kneader. Description: phenol about 1:1 with NaOH, 1 to 10 % phenol excess preferred, below 25 %; NaOH 25 to 55 %; water removed at ambient, then 5 to 100 mm Hg above 165 C; CO2 absorbed at once even under vacuum, the pressure rising to 4 to 6 bar and held 0.5 to 4 h; the absorption is exothermic (no value); the conversion about 85 to 88 % at 165 and 200 C; the kneader of US 3 880 407 (Heinz List). Example I: 23.2 mol phenol, 23.0 mol NaOH as a 40 % solution, dried at ambient, then 30 mm Hg to 190 C; CO2 at 5 mol/h, under vacuum in the first half, 5 bar after 5 h held 1 h; cooled to 100 C, filled with water; 20.4 mol salicylic acid (88 % on phenol), 0.054 mol 4-hydroxybenzoic and 0.026 mol 4-hydroxyisophthalic acid, 1.42 mol phenol. Example 3, runs at 140 to 243 C: by-products have a minimum about 180 to 210 C; incomplete drying (run 3-5) 60 %, 237 to 243 C (run 3-7) 31 % conversion | read (Google Patents); patent, facts only | D-001, D-004 to D-008 |
| SRC-2 | Mohammad, O.; Onwudili, J. A.; Yuan, Q. (2024) Molecules 29(11), 2527, doi:10.3390/molecules29112527, https://pmc.ncbi.nlm.nih.gov/articles/PMC11174078/ | sodium phenoxide suspended in toluene with added phenol (2:1), 225 C, 30 bar CO2, 2 h, 1000 rpm: 92.68 % molar yield of salicylic acid (0.3 g scale); the conventional gas-solid reaction described as slow with poor heat and mass transfer and a hygroscopic phenoxide; work-up with HCl; phenol recovery by distillation or water extraction named, not shown | read; CC BY 4.0, facts only | D-001, D-008 |
| SRC-3 | Wikipedia, Salicylic acid, https://en.wikipedia.org/wiki/Salicylic_acid | solubility in water 1.24, 2.48, 4.14, 17.41 and 77.79 g/L at 0, 25, 40, 75 and 100 C; melting point 158.6 C; density 1.443 g/cm3; pKa 2.97; sublimes at 76 C; decarboxylates slowly to phenol and CO2 at 200 to 230 C; made from sodium phenolate and CO2 (100 atm, 115 C), acidified with sulfuric acid; H302, H318 | read (first part of the page); CC BY-SA, facts only | D-005, D-007, D-008, D-011 |
| SRC-4 | The `chemicals` 1.5.2 package (core's environment): the CRC Handbook tables it packages (`CRC_standard_data`, `CRC_organic_data`, `CRC_inorganic_data`), `iapws95_Tsat` | formation enthalpies phenol (s) -165.1, salicylic acid (s) -589.9, CO2 (g) -393.5 kJ/mol; no entry for sodium phenoxide or sodium salicylate; sodium phenolate melts at 657.15 K, phenol at 314.04 K and boils at 454.95 K; densities and heat capacities of materials.yaml; steam saturation 524.97 K at 4100 kPa and 412.01 K at 350 kPa | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037); the printed handbook was not read | materials, reactions, D-005, D-009 |
| SRC-5 | The `thermo` 0.6.1 package | phenol's liquid density (1023.8 kg/m3) and heat capacity (Rowlinson-Poling, 197.5 kJ/(kmol K)) at 353.15 K; latent heats of water (2256.4 kJ/kg at 373.15 K, 2357.7 at 333.15 K) and phenol (486.6 at 463.15 K, 588.2 at 333.15 K); sulfuric acid's density | as SRC-4 | materials, D-006, D-008 |
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
aspirin train of `acetylsalicylic-acid-1` takes (about 0.8 kg per kg of aspirin at 1170 t/a,
its process.yaml). The product is the dried first crop, modelled 99.7 wt% (D-008); SRC-1 states
99.5 % for the conventional work-up. A pharmacopoeia grade (colour, ash, phenol and
4-hydroxybenzoic acid limits) is not modelled.

## D-003 Batch basis, recipe and vessels (2026-11-19)
`process/recipe.yaml`: one batch makes 2796.53 kg of S22; the kneader-reactor R-102 is the
bottleneck at 22.15 h (13.4 h drying from D101's rate, 5 h CO2, 1 h hold, venting, cooling and
the water fill), so 357.6 batches a year. The batch size is the fixed point batch = rate x
cycle that `cheme.recipe-basis` names (the drying time grows with the batch), so the flowsheet's
year averages and the recipe agree (no recipe-basis finding). The recipe sizes R-101 (5 m3,
70 % full), R-102 (5 m3 from R102's content; the solution it dries, 3.18 m3 at an ASSUMED
1300 kg/m3, fills it to 64 %, checked by hand) and D-201 (8 m3, 11.1 m2). R-201 is sized by
hand at 40 m3 (about 35.3 t of slurry a batch): core sizes no vessel from a conversion step
(L-5). Durations other than the models' are ASSUMED.

## D-004 Feeds and charge (2026-11-19)
- Charge ratio: 23.2 mol phenol per 23.0 mol NaOH (SRC-1 Example I, 0.87 % excess, within its
  preferred 1 to 10 % only just), the recovered phenol S20 counted in it: the design
  specification `phenol` adjusts the fresh phenol S1 to hold the ratio.
- Caustic soda 50 wt% as chlor-alkali-1 delivers it, not Example I's 40 %: SRC-1 allows 25 to
  55 %, and less water to evaporate in the bottleneck.
- CO2: 25/23 mol per mol NaOH dosed (Example I's 5 mol/h over 5 h for 23.0 mol), from
  carbon-capture-1 let down to 700 kPa(a).
- Sulfuric acid 98.5 wt% (sulfuric-acid-1), 0.51 mol per mol of sodium (2 % excess, ASSUMED).
- Water: 9 kg per kg of sodium salicylate formed to dissolve the crude (SRC-1 background: 8 to
  10 t per t), 2.0 kg per kg of caustic to wash the cake (ASSUMED, about 1.4 kg per kg of
  crystals).
- The design specification `rate` adjusts the caustic S3 for 1000 t/a of S22, the CO2, the
  dissolution water, the acid and the wash water following it at the ratios above (core ADR
  0070). Per kg of product: phenol 0.711 kg, caustic 50 wt% 0.675 kg, CO2 0.404 kg, sulfuric
  acid 0.429 kg, water 12.1 kg.

## D-005 Reactors R101 and R102: semi-batches, kinetics and heats (2026-11-19)
- R101: the caustic dosed over 1 h into the molten phenol at 343.15 K, isothermal, held to
  0.999 conversion of the NaOH; NEUT second order, k 1.0 m3/(kmol s) at 343 K, Ea 20 kJ/mol,
  ASSUMED; heat -30 kJ/mol ASSUMED (no formation enthalpy of sodium phenoxide found).
- R102: the CO2 dosed at a constant rate over 5 h into the dry phenoxide at 463.15 K (190 C,
  the end of SRC-1's drying and within Example 3's optimum), held 1 h. SRC-1 reports the CO2
  absorbed at once and the pressure rising to 5 bar only at the end: the share of the dose that
  reacts in Example I is taken up (`absorbed: 0.81838` = 20.48/23.0 x 0.999 / (25/23)) and the
  rest passes to the vent S8 (in the plant: it fills the head space and is vented after the
  hold). The model holds the powder at 101.325 kPa(a) (L-2).
- CARB and PARA second order in the phenoxide and the CO2 taken up, k 0.01 m3/(kmol s) at
  463 K, Ea 60 kJ/mol, ASSUMED fast (SRC-1: absorbed at once); PARA's rate constant 0.003922 of
  CARB's, Example I's (0.054 + 0.026)/20.4, the two by-product acids lumped as one
  4-hydroxybenzoate each. R102 converts 89.0 % of the phenoxide; the salicylate formed is
  87.8 % of the phenol charged per batch, SRC-1's 88 %.
- Heats: CARB and PARA -50 kJ/mol ASSUMED with CO2 as the dosed gas. The one open figure is the
  acids' reaction, phenol (s) + CO2 (g) -> salicylic acid (s), -31.3 kJ/mol (SRC-4); the salts'
  heat is taken larger so that the screening is not optimistic. To be measured.
- Unreacted phenol: Example I finds 1.42 mol of phenol in the stock solution; the model carries
  2.52 mol of unreacted phenoxide per 23.0 mol (the 1.10 mol difference is not explained by
  SRC-1: phenol lost in the drying vapour, or tar). The model's fresh phenol is therefore a lower
  bound: if the 1.10 mol were lost, 4.7 % more phenol would be needed (D-012).

## D-006 Drying the phenoxide D101 (2026-11-19)
Core's dryer: water and phenol evaporate to 0.2 wt% left (ASSUMED; SRC-1 shows that incomplete
drying lowers the conversion to 60 %), at 463.15 K; the heat is the solution's sensible heat
(3.0 kJ/(kg K) ASSUMED), the latent heats (water at 373.15 K, where most of it boils off at
ambient pressure; phenol at 463.15 K; SRC-5) and the kneader's metal (5000 kJ/K, ASSUMED) at 80 %
efficiency: Q2 81.1 kW year average, 0.642 kWh/kg, from HP steam through a hot-oil circuit (the
drying ends at 463 K; LP or MP steam is too cold). The drying time follows from an ASSUMED
10 kg/(m2 h) on R-102's heated area. The vapour (62.5 kg/h, 1.6 wt% phenol: the charge's excess)
is condensed in E-102 and collected for the phenol recovery. Core reports the dryer's duty but
does not write it (L-6), so Q2 is entered as assumed from `cheme process crystallizers`.

## D-007 Acidification R201 and the two crops (2026-11-19)
- R201: a conversion step, every sodium salt (salicylate, phenoxide, 4-hydroxybenzoate and the
  NaOH left) to its acid and sodium sulfate, at 328.15 K (SRC-1: 50 to 60 C). The crude enters
  at 463 K and the dissolution water at 298 K: core's conversion duty (Q4) counts their sensible
  heats and the acid's heat (-60 kJ per mol of sulfuric acid, ASSUMED): 27.6 kW net heating, the
  water must be warmed to 328 K. In the plant the water goes into the kneader at 373 K (SRC-1)
  and the solution to R-201; one step keeps the heat balance whole.
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
  (SRC-3), so the drying stays below it; Q6 21.1 kW (L-6 as D101). The product is 99.7 wt%
  salicylic acid, 0.08 wt% sodium sulfate, 0.2 wt% water.
- X301: a component separator (core ADR 0070), 95 % of the phenol in the collected liquors and
  condensates back to T-101, ASSUMED (SRC-1: the unreacted phenol is recyclable; SRC-2 names
  distillation or water extraction). The method (a solvent extraction of the acidic liquor and
  the solvent stripped) and its solvent are open; its steam is ASSUMED 2 kWh per kg of phenol
  recovered (Q7, 22.7 kW). The rest of the phenol, 0.04 wt%, goes with the liquor to treatment.

## D-009 Utilities and heat (2026-11-19)
Every energy flow per hour of the year average:
- Q1 5.85 kW and Q3 11.2 kW: core's semi-batch duties of R101 and R102 to cooling water (R102
  through the kneader's hot-oil loop, which also heats the drying);
- Q2 81.1 kW (HP steam 4100 kPa(a), 525 K saturation) and Q6 21.1 kW (LP steam 350 kPa(a)):
  core's dryer model; Q4 27.6 kW (LP steam): core's conversion duty; Q5 48.3 kW (chilled water
  278/283 K): core's crystallizer duty; Q7 22.7 kW (LP steam): ASSUMED;
- power: agitators 2 + 4 kW, the kneader's drive and vacuum pump 20 kW, the centrifuge 4 kW, the
  dryer 3 kW, the phenol recovery's pumps 2 kW, year averages ASSUMED: 0.277 kWh/kg.
- Not counted: the condensers E-102 and the product dryer's vacuum condenser (their cooling
  water), the phenol tank's trace heating, the hold's cooling of the kneader from 463 to 373 K
  (sensible heat in R201's balance).

## D-010 Wastes and emissions (2026-11-19)
The liquor after phenol recovery (13.27 kg/kg: 4.5 wt% sodium sulfate, dissolved salicylic and
4-hydroxybenzoic acids, 0.04 wt% phenol, 0.06 wt% sulfuric acid) goes to the site's wastewater
treatment; no sulfate recovery. The CO2 not taken up (0.073 kg/kg) is vented from the kneader
after the hold; it could be recompressed to the next batch (not modelled). Phenol vents of the
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
  salicylic acid decarboxylates at 200 to 230 C, SRC-3). A cooling failure forms no gas; the
  CO2 held (up to 4.7 kg a batch) and the drying's last water can leave on a temperature rise:
  the vent capacity is ASSUMED 100 m3/h against the 35 m3/h of CO2 passing through at the start
  of the dosing (`cheme process recipe`).
- The large dT_ad makes R102 dosing-controlled: the CO2 feed must trip on high temperature and
  on the kneader's drive stopping (the powder no longer renewed at the wall). No criticality
  class without a TD24 (open input). Hazards of the materials (no data copied): phenol toxic and
  corrosive to skin, hot caustic phenoxide, salicylic acid eye damage (SRC-3: H302, H318), CO2
  asphyxiation from the vent.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)
`lca/lca.yaml`: every exchange per kg of S22, the rinses of R-201, C-201 and V-202 (1.5 t a
batch, ASSUMED) as a per-batch consumable. Linked: phenol to acetone-1, caustic soda to
chlor-alkali-1, CO2 to carbon-capture-1 (its dense-phase product let down; the compression
burden carried, conservative), sulfuric acid to sulfuric-acid-1, the steam as heat delivered.
Gaps: water, power, cooling water, chilled water, wastewater treatment. The vented CO2 is a
fossil emission (captured from a fossil point source). The fresh phenol is a lower bound
(D-005). One product, no allocation.

## D-013 Dedicated train (2026-11-19)
T-101, R-101, R-102, E-102, R-201, C-201, V-202, F-202, D-201, T-301 and X-301 make only
salicylic acid, batch after batch: 357.6 batches in 7920 h (ASSUMED, library ADR 0035).

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
| batch recipe, cycle, R-101, R-102, D-201 | done in cheme; R-201 by hand | D-003 |
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
  vent (`absorbed`), so it cannot show the pressure rise, and the vent warns that CO2 forms in no
  reaction (accepted in `checks/checks.yaml`).
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
solvent and steam; the product specification; R-102's relief and the CO2 vent's routing; prices
and a TEA.
