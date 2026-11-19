# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Lactic acid by batch fermentation of glucose, the gypsum route and purification through ethyl
lactate, issue ChemE-as-Code/process-library#517, a Tier 2 entry of the library with a batch
fermentation train and continuous downstream. Concept stage: design basis, batch recipe of the
fermenters, balanced BFD/PFD solved for its design specifications with three recycles
converged, equipment list, preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout (the
concept gate `layout-plot-plan` stays open on purpose, as in biodiesel-1), HAZOP, TEA,
datasheets.

Starting point (2026-11-19): library `main` with the core pin v1.13.0 (b97a833). Core solves
feeds and splits for design specifications and splits component separators on their recoveries
(core ADR 0070), converges recycles at tear streams (ADR 0060), writes a conversion step's duty
(ADR 0059) and derives a batch cycle from a recipe (ADR 0051). It has no qualified model of
fermentation broths, calcium salts, gypsum slurries or lactic acid with its esters (L-1).
Templates: `biodiesel-1` (a recent continuous entry: structure, specs, hand duties, LCA) and
`oxalyl-chloride-1` (a batch entry: recipe, per-batch consumables). Requires cheme-as-code 1.13
(plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage or code named
was read in this work (files fetched from GitHub and read; PDF text extracted and read; the
Python packages queried).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | BioSTEAM lactic biorefinery: Bioindustrial-Park, `biorefineries/lactic` (Li, Y.; Bhagwat, S. S.; Cortes-Pena, Y. R. et al.), https://github.com/BioSTEAMDevelopmentGroup/Bioindustrial-Park/tree/master/biorefineries/lactic, the model of Li et al. (2021) ACS Sustainable Chem. Eng. 9, 1341-1351 | `README.rst`: SSCF and SHF configurations; MPSP 1.414 $/kg, GWP 4.567 kg CO2-eq/kg, FEC 58.67 MJ/kg (SSCF); the system's lime stream 243 kmol/h of Ca(OH)2 and the product 256 kmol/h of lactic acid (with 86.1 kmol/h water, 13.1 kmol/h ethyl lactate). `_units.py`: CoFermentation (T 50 C; titer 130 g/L, the maximum of the collected data; productivity 0.89 g/(L h); yield 0.76 g/g; turnaround 12 h; parallel reactions glucose to 2 lactic acid 0.76, to 3 acetic acid 0.07, to 6 cell mass 0.02; CSL 10 g/L; lime for the acids plus 10 %; neutralisation to the calcium salts at 1; V_wf 0.8); the Reactor class (agitation 0.0985 kW/m3, from 0.5 hp/1000 gal); AcidulationReactor (calcium salts and lime with H2SO4 at 1, the acid 10 % over and 93 % pure); Esterification (T 351.15 K; 1.5 mol ethanol per mol acid; Amberlyst-15 3.9 wt%; K = exp(2.9625 - 515.13/T)); HydrolysisReactor (12 mol water per mol ester, conversion 0.8). `_processes.py`, create_separation_process: cell mass filter moisture 0.35; acidulation tau 1 h, SS316; gypsum filter moisture 0.2; flash F401 at 379 K; D401 acetic acid recovery 0.99; D402 ethanol 0.99; D403 ethyl lactate 0.995 over lactic acid 0.9995, its bottoms 97 % recycled; R403 tau 4 h; D404 ethanol 0.9, water 0.9935 to the bottoms; F402 to 88 wt% lactic acid. `_chemicals.py`: CSL as 50 % water, 25 % protein, 25 % lactic acid. `utils.py` get_splits: gypsum 0.995 to the cake. The ethanol recycle about 91 % ethanol with 8 % water (Esterification._run comment) | read 2026-11-19; MIT licence (repository LICENSE.txt); code read, numbers used as facts, no code copied | D-001, D-003, D-005 to D-010, benchmarks |
| SRC-2 | Garrido, R.; Cabeza, L. F.; Falguera, V. (2023) Lactic Acid Production from Cow Manure: Technoeconomic Evaluation and Sensitivity Analysis. Fermentation 9, 901, doi:10.3390/fermentation9100901 | p. 5, Table 3: SSAF at 50 C, product recovery 92 %, final product 88 % w/w lactic acid. p. 6: 8640 h a year. pp. 7-8: calcium carbonate or hydroxide to hold pH 5 to 6; gypsum precipitated with sulfuric acid and filtered; technical-grade acid esterified with methanol or ethanol, the ester distilled, hydrolysed and the alcohol recycled; the zinc lactate alternative. p. 11, Table 4: scenario I, 109 723 t/a fermented, 100 945 t/a recovered. p. 13, Table 6: sulfuric acid 93 % 1981 kg/h; grid electricity 12 797 kW under by-products and credits (an export) | read 2026-11-19; CC BY 4.0, facts only | D-001, D-002, D-005, D-007, D-008 |
| SRC-3 | Wikipedia, "Glucose" (infobox: enthalpy of formation -1271 kJ/mol, citing Ponomarev and Migarskaya 1960) and "Calcium lactate" (solubility of the L-lactate: 6.7 g/100 mL at 25 C, 8.5 g/100 mL at 30 C, citing Vavrusova et al. 2013) | infoboxes and text, read 2026-11-19 | secondary sources, values ASSUMED | reactions (FLA, FAA), D-005 |
| SRC-4 | thermo 0.6.1 and chemicals 1.5.2 (Caleb Bell, MIT; core's environment) | formation enthalpies (kJ/mol): L-lactic acid(s) -694.08 (`Hfs`, method WEBBOOK, the NIST WebBook value as packaged), CaO(s) -634.9 and Ca(OH)2(s) -985.2 (`Hfs`, CRC), water(l) -285.825 and acetic acid(l) -483.58 (`Hfl`, ATCT_L, the Active Thermochemical Tables); heat capacities: water 75.33 and ethanol 122.02 kJ/(kmol K) at 323.15 K (HEOS_FIT), acetic acid 135.55 (VDI_TABULAR, the VDI Heat Atlas as bundled), sulfuric acid 138.9 (CRCSTD), CaO 42.10 and Ca(OH)2 87.48 (WEBBOOK_SHOMATE), gypsum 195.81 (PERRY151, Perry's Handbook table 2-151 as bundled); heats of vaporisation (HEOS_FIT): water 43.34, 42.47, 42.25, 41.65 kJ/mol at 313.15, 333.15, 338.15, 351.57 K, ethanol 40.43 and 39.14 kJ/mol at 333.15 and 351.57 K; boiling points (`Tb`): water 373.12 (HEOS), ethanol 351.57 (HEOS), acetic acid 391.05 (CRC_ORG), ethyl lactate 427.15 K (COMMON_CHEMISTRY); water's vapour pressure 20 kPa at 333.2 K, 450 kPa at 421.1 K, 1000 kPa at 453.0 K (IAPWS_PSAT). No heat capacity of lactic acid, ethyl lactate, glucose or the calcium salts, no heat of vaporisation of ethyl lactate, no formation enthalpy of liquid ethyl lactate or the calcium salts | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying works (the CRC Handbook, the VDI Heat Atlas, Perry's Handbook, CoolProp's reference equations, the NIST WebBook, the ATcT) were not read here | materials, reactions, D-009 |
| SRC-5 | PubChem (identifiers of L-lactic acid CID 107689, D-glucose CID 107526 (open chain, the identity the chemicals package gives CAS 50-99-7) and CID 5793 (pyranose), calcium sulfate dihydrate CID 24928: formula, InChIKey, ChEBI cross-reference) | PUG REST, queried 2026-11-19 | open data | chemicals registry |
| SRC-6 | processes/lime-1, sulfuric-acid-1, bioethanol-1, biodiesel-1, oxalyl-chloride-1 (this library) | quicklime; 98.5 wt% sulfuric acid; anhydrous fuel ethanol; the templates' structure and LCA | library, internal | D-006 to D-008, D-011 |
| SRC-7 | Li, Y. et al. (2021) Sustainable Lactic Acid Production from Lignocellulosic Biomass. ACS Sustainable Chem. Eng. 9, 1341-1351, doi:10.1021/acssuschemeng.0c08055 | - | not read (not open); the paper SRC-1 implements | the model's citation only |

Searched and not found openly (2026-11-19): a design of a dextrose-fed lactic acid plant with
its fermentation data (both numerical sources ferment lignocellulosic or manure sugars, as the
issue's caveat says), the conversion of a reactive distillation esterifier of lactic acid with
ethanol, the solubility of calcium lactate at 50 C and at the broth's 157 g/L, vapour-liquid
data for ethyl lactate-lactic acid-water-ethanol, and an open production volume of lactic acid.

## D-001 Route and boundary (2026-11-19)
Decision: fermentation of bought-in glucose by lactic acid bacteria in batch fermenters at
323 K with the pH held at 5 to 6 by lime (SRC-2 pp. 7-8; SRC-1 CoFermentation), so the acid
forms as calcium lactate; cell mass separated; calcium lactate acidulated with sulfuric acid and
the gypsum filtered (the gypsum route, SRC-1 and SRC-2); the crude acid evaporated, esterified
with ethanol, the ethyl lactate distilled off the non-volatile residue, hydrolysed back to lactic
acid with water and concentrated to 88 wt%, the ethanol recovered and recycled (SRC-1
`_processes.py`; SRC-2 p. 8). The boundary starts at the glucose syrup, so the feedstock's
pretreatment and saccharification of both sources are left out (the issue: "a concept entry
would buy sugar in and keep the fermentation and separation train").

Rejected alternatives:
- Lignocellulosic sugars (corn stover in SRC-1, cow manure in SRC-2) with their pretreatment,
  enzymatic hydrolysis and simultaneous saccharification and fermentation: a second entry's
  scope (feedstock handling, acid pretreatment, enzymes, lignin to a boiler); the library has no
  pretreatment model yet. Bought-in glucose keeps the entry to the lactic acid train.
- Purification by precipitation only, to technical grade (22 to 44 %, SRC-2 p. 8): not the
  polymer-grade product the issue names.
- Methanol instead of ethanol for the esterification (SRC-2 p. 8 names either): SRC-1's model,
  parameters and equilibrium constant are for ethanol, and the ethanol can come from
  bioethanol-1, keeping the carbon biogenic (D-011).
- Zinc lactate recrystallisation with zinc precipitated as sulfide by hydrogen sulfide (SRC-2
  p. 8): a toxic reagent (H2S) and no numbers read.
- Gypsum-free routes (fermentation at low pH, ammonia neutralisation with salt splitting,
  electrodialysis, extraction with amines): no open source with process numbers was read for
  them (searched 2026-11-19); the gypsum route is the one both sources model.
- Chemical synthesis (not by fermentation): outside the issue's scope; no source read.

## D-002 Capacity, product and operating hours (2026-11-19)
Decision: 100 000 t/a of lactic acid (as 100 %), the order of SRC-2's scenario I (100 945 t/a
recovered, p. 11), 12 500 kg/h in 8000 h/a (ASSUMED; SRC-2 runs 8460 or 8640 h, SRC-1 7880 h
in its ash price, `_process_settings.py`). The product is an 88 wt% solution (SRC-2 p. 5, the
target of SRC-1's last flash), modelled 88.1 wt% lactic acid, 0.6 wt% ethyl lactate, 0.1 wt%
acetic acid and water; 14 188 kg/h. Optical purity, colour, residual sugar and metals are not
modelled (L-2). The functional unit of the LCI is 1 kg of this solution (D-011).

## D-003 Batch fermentation on a dedicated train (2026-11-19)
Decision: the fermentation is batch (SRC-1 runs its fermenter in batch mode with a 12 h
turnaround), in 16 fermenters on a dedicated train (library ADR 0035): fill 4 h, ferment
146.07 h (130 g/L at 0.89 g/(L h), SRC-1), harvest 4 h, clean in place 4 h (the 12 h
turnaround split, ASSUMED). A batch is harvested every 9.88 h, 809.8 a year, each 1106 t of
broth (about 1033 m3); `process/recipe.yaml` states it and the flowsheet holds its year average
(cheme process recipe: S8 111 949 kg/h from the recipe, 111 951 kg/h in the flowsheet). A broth
hold tank (T-201) buffers the harvests to the continuous downstream, which runs at the year
averages; it changes no composition and is not a flowsheet step. The cleaning between batches
enters the LCI per batch (rinse water 20 t and 50 kg of NaOH per fermenter cleaned, ASSUMED,
`lca/lca.yaml` consumables). Out of scope (ADR 0035): changeovers and campaigns; a lactic acid
plant of this size is dedicated anyway. The seed train is not modelled apart (L-3): SRC-1 grows
its inoculum at 0.95 of the main fermenter's yield; here the main fermenters carry the whole
glucose.

Reason for 16 fermenters: about 1300 m3 vessels (the broth at 80 % of the volume, SRC-1's
V_wf), a size chosen to keep the vessel count manageable; the count is a design choice
(ASSUMED).

## D-004 Feeds and lumps (2026-11-19)
Decision: the sugar is a glucose syrup of 70 wt% dry substance taken as pure glucose
(ASSUMED; neither source buys sugar, D-001). Cell mass is carried as the lump BIO with the
formula CH2O (a glucose equivalent), so that SRC-1's growth reaction (glucose to 6 cell mass)
balances; the nitrogen the cells take up is not carried (L-3). The corn steep liquor is SRC-1's
50 % water, 25 % protein (the lump NUT, no formula), 25 % lactic acid. Dissolved salts are
carried as neutral calcium lactate and acetate. No succinic acid, furfural, HMF or sugar
oligomers (they come from the lignocellulose of SRC-1).

## D-005 Fermentation (2026-11-19)
Decision: SRC-1's parallel conversions of the glucose (0.76 to lactic acid, 0.07 to acetic acid,
0.02 to cell mass) at 323 K, written as net reactions with the lime's neutralisation (FLA, FAA,
FBIO, and NEU for the CSL's lactic acid; process/reactions.yaml). 15 % of the glucose stays
unconverted, as in SRC-1 (2.6 t/h in the broth): it travels with the acid and leaves in the
ester column's residue (D-008). For a refined dextrose the sugar would likely be used further;
no source for that was read, so the source's conversions stand (the issue's caveat).

The titer, 130 g/L (SRC-1), sets the medium water: the design specification `titer` holds
calcium lactate at 0.14727 kg/kg in the broth (130 g/L of lactic acid as calcium lactate at an
ASSUMED broth density of 1070 kg/m3). The CSL dose is 10 g per litre of broth (SRC-1). 157 g/L of
calcium lactate is about twice its solubility at 30 C (8.5 g/100 mL, SRC-3); whether it stays
dissolved at 50 C is not checked (L-4). The broth is therefore kept at or above 323 K until
acidulation (T-201), and crystallisation of calcium lactate in a cold spot is an open point.

## D-006 Lime, cell mass (2026-11-19)
Decision: quicklime (lime-1) slaked on site to a 20 wt% milk of lime (ASSUMED) in R-101, which
is cooled to 323 K (Q1, 820 kW, core's conversion duty from the slaking enthalpy, SRC-4). The
lime is 10 % over the acids formed and the CSL's acid (SRC-1); its excess (636 kg/h of Ca(OH)2)
goes on with the broth and is neutralised in the acidulation, as in SRC-1. The cell mass is
centrifuged off (S-301): 98 % of the cell mass and 90 % of the CSL solids to a cake at 35 wt%
moisture (SRC-1's cell mass filter), which takes 0.278 % of the broth's liquid (set so that the
solved cake S9 holds 35 wt% liquid). The cake (0.88 t/h) goes to anaerobic digestion (D-011).

## D-007 Acidulation and gypsum (2026-11-19)
Decision: the clarified broth is acidulated with 93 wt% sulfuric acid (SRC-1; SRC-2 Table 6)
at 1.01 mol per mol of calcium (ASSUMED), not SRC-1's 10 % excess: the excess acid would pass
the evaporator and build up in a recycle; here it ends in the ester column's residue (114 kg/h).
Calcium lactate, calcium acetate and the excess lime all go to gypsum (SRC-1's reactions at
conversion 1), taken as the dihydrate CaSO4.2H2O (SRC-1 carries anhydrous CaSO4; the hydrate
formed at 323 K is ASSUMED). The gypsum belt filter (S-302) takes 99.5 % of the gypsum (SRC-1)
into a cake of 20 wt% moisture (SRC-1), which holds 3.85 % of the filtrate's liquid: 522 kg/h of
lactic acid, the largest single loss (3.9 %). A displacement wash of the cake would recover most
of it at the cost of more water to evaporate; SRC-1 has none and none is designed here (an open
optimisation). Gypsum cake: 20.2 t/h, 1.61 kg per kg of lactic acid, to landfill or use, not
credited (D-011). The heats of the acidulation and of the acid's dilution are ASSUMED 0 (L-5);
R301's duty (237 kW to cooling water) is the acid's sensible heat and the gypsum's water of
crystallisation only.

## D-008 Evaporation and purification through ethyl lactate (2026-11-19)
Decision, step by step (component separators on the recoveries named, D-010 for sizes):
- E-401, four-effect evaporator: 97 % of the water (ASSUMED) and 99 % of the acetic acid
  (SRC-1's D401) off, 0.5 % of the lactic acid entrained (ASSUMED), to a concentrate of about
  71 wt% lactic acid with 14 wt% glucose. SRC-1 stops at about 50 wt% before its stirred
  esterifier; the drier feed suits the reactive distillation and limits the water the
  hydrolysis loop must purge.
- R-401, esterification with ethanol at 1.5 mol per mol of lactic acid (SRC-1, the design
  specification `ethanol-ratio`) at 351 K on Amberlyst-15 (SRC-1), in a reactive distillation
  column that takes the water and the ester out of the reaction zone: 98 % conversion, ASSUMED.
  SRC-1 uses a stirred reactor at equilibrium and recycles 97 % of the ester column's bottoms;
  that recycle is rejected here because the unconverted glucose of D-005 (2.5 t/h) would build
  up in it to some thirty times its feed. With the bottoms purged, a high single-pass conversion
  is needed; at SRC-1's equilibrium constant (4.5 at 351 K) and an ideal solution, a stirred
  reactor on this feed (with the recycles' water) would stop near 67 %, so the 98 % rests on the reactive distillation's
  removal of water, not on a source read (L-6).
- C-401, ester column at 20 kPa(a): ethanol, water, acetic acid and 99.5 % of the ethyl lactate
  (SRC-1's D403) overhead; the residue (glucose, the unconverted 2 % of the lactic acid, the
  sulfuric acid, fine gypsum; 3.1 t/h) at about 423 K (ASSUMED) to anaerobic digestion.
- C-402, ethanol column at 1 atm: 99 % of the ethanol (SRC-1's D402) overhead at about 91 wt%
  (SRC-1's recycle composition; the water split set for it), back to the esterifier (tear S18).
- R-402, hydrolysis at 363 K (ASSUMED; SRC-1 gives 4 h but no temperature) with 12 mol of water
  per mol of ester (SRC-1; the design specification `hydrolysis-water`), 80 % per pass (SRC-1).
- C-403, ethanol stripper at 1 atm: 90 % of the ethanol overhead (SRC-1's D404) at about
  92 wt% (the water split set near C-402's, ASSUMED: SRC-1's 0.9935 of the water to the bottoms
  would give 96.6 wt% ethanol here), back to the esterifier (tear S19).
- E-404, product concentrator, two effects (ASSUMED), the last at 20 kPa(a): water off to
  88 wt% lactic acid (the split set for it), all the ethanol, 98 % of the unconverted ester and
  half of the acetic acid off with it (ASSUMED); the condensate goes back to the hydrolysis
  (tear S29), the 2.9 % that the water ratio leaves over is purged to the wastewater (the
  specification varies SP401's purge).
Results: 92 % of the lactic acid formed reaches the product (SRC-2 p. 5: 92 %); the losses are
the gypsum cake (3.8 %), the ester column's residue (2.4 %, as acid and ester), the
hydrolysis purge (0.7 %, as ester), the evaporator (0.5 %), the product's ester (0.5 %) and the
cell mass cake (0.3 %, as calcium lactate), counted as lactic acid on the 13 601 kg/h formed
(with the CSL's). Ethanol make-up 132 kg/h, 9.3 g/kg.

## D-009 Utilities and duties (2026-11-19)
Decision: LP steam 450 kPa(a) (421 K) for the evaporator, the esterifier, the ethanol column,
the hydrolysis, the stripper and the concentrator; MP steam 1000 kPa(a) (453 K) for the ester
column's reboiler, whose residue boils near 423 K; cooling water 298 to 308 K. All ASSUMED.
- Core's conversion duties (propagate, from the heats of reaction of process/reactions.yaml and
  the heat capacities of process/materials.yaml, net of the power booked on the step): R101 Q1
  820 kW; R201 Q2 7153 kW (the fermentation's heat and the agitators' 1880 kW, to cooling
  water); R301 Q3 237 kW; R401 Q6 214 kW; R402 Q11 528 kW. Heats of reaction: SLK, FLA, FAA from
  formation enthalpies (SRC-3, SRC-4), the neutralisations at the strong acid-strong base value
  -55.8 kJ/mol (ASSUMED); FBIO, ACL, ACA, ACH, EST, HYD ASSUMED 0 for want of data (L-5). The
  heat capacities of lactic acid and ethyl lactate are taken at acetic acid's per kg, those of
  glucose, the salts, cell mass and CSL at water's per kg (ASSUMED).
- Hand estimates (ASSUMED, the arithmetic in each energy stream's source), each heater and
  condenser pair closing its step's balance with the streams' sensible heats: E-401 four
  effects without thermocompression (Q4 13.7 MW of steam, Q5 14.5 MW condensed); C-401 reflux
  ratio 1 (Q7 12.1 MW MP steam, Q8 12.5 MW); C-402 reflux ratio 3 (Q9 5.1 MW, Q10 4.2 MW);
  C-403 reflux ratio 2 (Q12 6.1 MW, Q13 5.8 MW); E-404 two effects (Q14 11.0 MW, Q15 13.1 MW);
  E-405 product cooler (Q16 0.6 MW). Ethyl lactate's heat of vaporisation by Trouton's rule
  (88 J/(mol K) x 427.15 K = 37.6 kJ/mol, ASSUMED).
- Power (ASSUMED except the agitators): fermenter agitators 1880 kW (SRC-1's 0.0985 kW/m3 on
  20 656 m3 of vessels, over the 146 h of 158 h they ferment), centrifuges 300 kW, filter 200 kW,
  evaporator 250 kW, purification 300 kW, preparation 100 kW; 3.03 MW, 0.24 kWh per kg of
  lactic acid.
Per kg of lactic acid (as 100 %): 3.90 kWh of steam heat (14.0 MJ), of which E-401 1.10,
C-401 0.97, E-404 0.88, C-403 0.48, C-402 0.41 kWh. No heat integration (L-7): the condensers
reject at 313 to 352 K what the reboilers take at 373 to 423 K.

## D-010 Equipment sizes (2026-11-19)
Decision: first sizes from the flowsheet's flows (equipment/equipment-list.yaml): fermenters
from the recipe (1033 m3 of broth at 80 % fill, SRC-1's V_wf: 1291 m3 each); the broth tank
for one harvest plus 12 h; the acidulation tank for SRC-1's 1 h; the hydrolysis reactor for
SRC-1's 4 h; the rest by service. Materials are usual choices for hot organic acids
(stainless steel 316), to be confirmed. ASSUMED.

## D-011 Preliminary gate-to-gate LCI (2026-11-19)
Decision: `cheme assess lca --write` from the design case per kg of the 88 wt% product (S32),
no allocation (one product; the gypsum, cell mass, residue and wastewater are wastes; the
gypsum is not credited, as SRC-1 gives it no price in its baseline). Linked: quicklime to
lime-1, sulfuric acid to sulfuric-acid-1 (98.5 wt%, kg for kg of the 93 wt% acid: conservative
by 5.6 %), ethanol to bioethanol-1, LP and MP steam as heat delivered. Gaps with the activity
each should connect to: glucose syrup and corn steep liquor (no library producer; corn wet
milling is not in the library), process water, power, cooling, the four waste streams and the
cleaning consumables. The carbon of glucose, CSL and ethanol is declared biogenic. Emission
exclusions: the ethanol-bearing vents, the fermenters' and broth tank's breathing, the slaker
and acidulation vents (D-012). Not checked: SRC-1's cradle-to-gate 4.567 kg CO2-eq/kg is for a
lignocellulosic biorefinery with its own boiler and is not comparable with this gate-to-gate
inventory.

## D-012 Hazards (2026-11-19)
- The fermentation is exothermic: 5.27 MW for the whole train (Q2 less the agitators' 1.88
  MW), about 187 GJ per batch (5.27 MW x 9.879 h) released over 146 h, 0.36 MW per fermenter.
  If the cooling were lost for a whole batch, its 1106 t of broth (at water's 4.18 kJ/(kg K))
  would warm by about 40 K, to about 363 K, below the broth's boiling point at 1 atm; the heat
  comes from the bacteria, which ferment at 323 K (SRC-1, SRC-2), so an overheated batch is
  expected to stop releasing heat well before (ASSUMED, not quantified). The rise is slow (days),
  so the fermenter's temperature alarm and the operator have time. `cheme process
  reactor-hazards` has no full screening of these conversion steps (no MTT or TD24 given), so
  this hand estimate stands (L-8).
- Ethanol (flammable) in R-401, C-401 to C-403, R-402 and E-404 and their drums; vacuum on
  C-401 and E-404 (air ingress); hazardous-area classification needed there.
- Quicklime slaking is exothermic and dusty (R-101); 93 % sulfuric acid is corrosive and its
  dilution exothermic (R-301); hot concentrated lactic acid is corrosive (materials, D-010).
- Gypsum scaling in the evaporator; calcium lactate crystallisation in a cold broth line (D-005).
- Biological hazards are low (food-grade lactic acid bacteria); sterility failures are a
  quality, not a safety, issue.
No HAZOP at this stage; no semi-batch or dosed exothermic step (the lime is dosed on pH into a
fermentation, not a reaction mass with accumulation).

## Method and dependency table

| result | method | inputs | where |
|---|---|---|---|
| syrup, medium water, ethanol make-up, hydrolysis purge | core design specifications (ADR 0070) | D-002, D-005, D-008 | flowsheet `specs:` |
| recycles S18, S19, S29 | core tears (ADR 0060), Broyden | D-008 | flowsheet `tears:` |
| batch cycle and batches per year | core recipe (ADR 0051) | D-003 | process/recipe.yaml |
| reactor outlets | conversion models | process/reactions.yaml | propagate |
| separator outlets | component separators (ADR 0070) | D-006 to D-008 | `recovery:` |
| reactor duties | core conversion duty (ADR 0059) | reactions, materials | Q1, Q2, Q3, Q6, Q11 |
| separation duties | hand estimates | D-009 | Q4, Q5, Q7 to Q10, Q12 to Q16 |
| LCI | cheme assess lca | lca/lca.yaml, mappings | lca/ |

## Core features used (core 1.13.0)
- Design specifications on feeds and on a splitter's outlet, solved with the tears (ADR 0070).
- Three tear streams converged together (ADR 0060).
- Component separators with stated recoveries (ADR 0070), one outlet taking the rest.
- Conversion duties written to energy streams, net of the power on the step (ADR 0059).
- The batch recipe with a unit in parallel and the `cheme.recipe-basis` check (ADR 0051).
- Per-batch LCA consumables (ADR 0053).
- BFD/PFD generation (`cheme process build`).

## Core limits hit (each a candidate core issue)
- L-1: no property package for fermentation broths, dissolved calcium salts, gypsum slurries,
  lactic acid, its oligomers and ethyl lactate, and no VLE for ethyl lactate-lactic
  acid-ethanol-water: every split is specified, not predicted; no stream properties.
- L-2: no product-quality model (optical purity, colour, residual sugar, metals, oligomers);
  lactic acid's self-esterification to oligomers on concentration is not carried.
- L-3: no growth model: the cell mass is a glucose-equivalent lump without nitrogen; no seed
  train; no CO2 or gas from the fermentation.
- L-4: no solubility check of a dissolved salt in a reactor or tank (calcium lactate at 157 g/L,
  D-005); core's crystallizer solubility (ADR 0076) applies to a crystallizer step only.
- L-5: no formation enthalpies of dissolved calcium salts, ethyl lactate (liquid) or the cell
  mass in core's data, and no heats of solution or dilution: several heats of reaction are
  ASSUMED 0 and the acid's dilution heat is left out.
- L-6: no reactive distillation model: the esterifier is a conversion step and a separator,
  its 98 % assumed; no kinetic or equilibrium esterification model to check it.
- L-7: component separators carry no duty model (as biodiesel-1 L-4): the evaporators' and
  columns' duties are hand estimates; no heat integration or multiple-effect evaporator model.
- L-8: `cheme process reactor-hazards` screens no batch fermentation (a conversion step without
  MTT or TD24): the adiabatic rise of D-012 is a hand estimate.

## Open inputs
- A dextrose-fed fermentation's yield, titer and productivity (the sources' are for
  lignocellulosic sugars).
- The reactive distillation's conversion and the ester column's conditions from an open source.
- Calcium lactate's solubility at 323 K.
- Whether a gypsum cake wash pays.
- Sterilisation of the medium (continuous, steam) and the seed train.
