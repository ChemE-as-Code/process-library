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
| SRC-1 | BioSTEAM lactic biorefinery: Bioindustrial-Park, `biorefineries/lactic` (Li, Y.; Bhagwat, S. S.; Cortes-Pena, Y. R. et al.), https://github.com/BioSTEAMDevelopmentGroup/Bioindustrial-Park/tree/master/biorefineries/lactic, the model of Li et al. (2021) ACS Sustainable Chem. Eng. 9, 1341-1351 | `README.rst`: SSCF and SHF configurations; MPSP 1.414 $/kg, GWP 4.567 kg CO2-eq/kg, FEC 58.67 MJ/kg (SSCF); the system's lime stream 243 kmol/h of Ca(OH)2 and the product 256 kmol/h of lactic acid (with 86.1 kmol/h water, 13.1 kmol/h ethyl lactate). `_units.py`: CoFermentation (T 50 C; titer 130 g/L, the maximum of the collected data; productivity 0.89 g/(L h); yield 0.76 g/g; turnaround 12 h; parallel reactions glucose to 2 lactic acid 0.76, to 3 acetic acid 0.07, to 6 cell mass 0.02; CSL 10 g/L; lime for the acids plus 10 %; neutralisation to the calcium salts at 1; V_wf 0.8); the Reactor class (agitation 0.0985 kW/m3, from 0.5 hp/1000 gal); AcidulationReactor (calcium salts and lime with H2SO4 at 1, the acid 10 % over and 93 % pure); Esterification (T 351.15 K; 1.5 mol ethanol per mol acid; Amberlyst-15 3.9 wt%; K = exp(2.9625 - 515.13/T)); HydrolysisReactor (12 mol water per mol ester, conversion 0.8). `_processes.py`, create_separation_process: cell mass filter moisture 0.35; acidulation tau 1 h, SS316; gypsum filter moisture 0.2; flash F401 at 379 K; D401 acetic acid recovery 0.99; D402 ethanol 0.99; D403 ethyl lactate 0.995 over lactic acid 0.9995, its bottoms 97 % recycled; R403 tau 4 h; D404 ethanol 0.9, water 0.9935 to the bottoms; F402 to 88 wt% lactic acid. `_chemicals.py`: CSL as 50 % water, 25 % protein, 25 % lactic acid. `utils.py` get_splits: gypsum 0.995 to the cake. The ethanol recycle about 91 % ethanol with 8 % water (Esterification._run comment). Read 2026-11-25 for basic engineering, `_units.py`: `SeedTrain` costed as 5 stages in 2 trains; seed turnaround 12 h ("the same as" Humbird et al. 2011, NREL, not read here); seed productivity 0.95 x 0.89 g/(L h); seed temperature 50 C; a `SeedHoldTank` after the seed train (tank, agitator, pump); `CoFermentation.inoculum_ratio = 0.07` (7 % of the fermentation feed split to the seed train); the main fermentation in `mode='batch'` with no air or oxygen input and no CO2 in its reactions (lactic and acetic acid and cell mass only): not aerated | read 2026-11-19 and 2026-11-25; MIT licence (repository LICENSE.txt); code read, numbers used as facts, no code copied | D-001, D-003, D-005 to D-010, benchmarks |
| SRC-2 | Garrido, R.; Cabeza, L. F.; Falguera, V. (2023) Lactic Acid Production from Cow Manure: Technoeconomic Evaluation and Sensitivity Analysis. Fermentation 9, 901, doi:10.3390/fermentation9100901 | p. 5, Table 3: SSAF at 50 C, product recovery 92 %, final product 88 % w/w lactic acid. p. 6: 8640 h a year. pp. 7-8: calcium carbonate or hydroxide to hold pH 5 to 6; gypsum precipitated with sulfuric acid and filtered; technical-grade acid esterified with methanol or ethanol, the ester distilled, hydrolysed and the alcohol recycled; the zinc lactate alternative. p. 11, Table 4: scenario I, 109 723 t/a fermented, 100 945 t/a recovered. p. 13, Table 6: sulfuric acid 93 % 1981 kg/h; grid electricity 12 797 kW under by-products and credits (an export) | read 2026-11-19; CC BY 4.0, facts only | D-001, D-002, D-005, D-007, D-008 |
| SRC-3 | Wikipedia, "Glucose" (infobox: enthalpy of formation -1271 kJ/mol, citing Ponomarev and Migarskaya 1960) and "Calcium lactate" (solubility of the L-lactate: 6.7 g/100 mL at 25 C, 8.5 g/100 mL at 30 C, citing Vavrusova et al. 2013) | infoboxes and text, read 2026-11-19 | secondary sources, values ASSUMED | reactions (FLA, FAA), D-005 |
| SRC-4 | thermo 0.6.1 and chemicals 1.5.2 (Caleb Bell, MIT; core's environment) | formation enthalpies (kJ/mol): L-lactic acid(s) -694.08 (`Hfs`, method WEBBOOK, the NIST WebBook value as packaged), CaO(s) -634.9 and Ca(OH)2(s) -985.2 (`Hfs`, CRC), water(l) -285.825 and acetic acid(l) -483.58 (`Hfl`, ATCT_L, the Active Thermochemical Tables); heat capacities: water 75.33 and ethanol 122.02 kJ/(kmol K) at 323.15 K (HEOS_FIT), acetic acid 135.55 (VDI_TABULAR, the VDI Heat Atlas as bundled), sulfuric acid 138.9 (CRCSTD), CaO 42.10 and Ca(OH)2 87.48 (WEBBOOK_SHOMATE), gypsum 195.81 (PERRY151, Perry's Handbook table 2-151 as bundled); heats of vaporisation (HEOS_FIT): water 43.34, 42.47, 42.25, 41.65 kJ/mol at 313.15, 333.15, 338.15, 351.57 K, ethanol 40.43 and 39.14 kJ/mol at 333.15 and 351.57 K; boiling points (`Tb`): water 373.12 (HEOS), ethanol 351.57 (HEOS), acetic acid 391.05 (CRC_ORG), ethyl lactate 427.15 K (COMMON_CHEMISTRY); water's vapour pressure 20 kPa at 333.2 K, 450 kPa at 421.1 K, 1000 kPa at 453.0 K (IAPWS_PSAT). No heat capacity of lactic acid, ethyl lactate, glucose or the calcium salts, no heat of vaporisation of ethyl lactate, no formation enthalpy of liquid ethyl lactate or the calcium salts | open-source package queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037). The underlying works (the CRC Handbook, the VDI Heat Atlas, Perry's Handbook, CoolProp's reference equations, the NIST WebBook, the ATcT) were not read here | materials, reactions, D-009 |
| SRC-5 | PubChem (identifiers of L-lactic acid CID 107689, D-glucose CID 107526 (open chain, the identity the chemicals package gives CAS 50-99-7) and CID 5793 (pyranose), calcium sulfate dihydrate CID 24928: formula, InChIKey, ChEBI cross-reference) | PUG REST, queried 2026-11-19 | open data | chemicals registry |
| SRC-6 | processes/lime-1, sulfuric-acid-1, bioethanol-1, biodiesel-1, oxalyl-chloride-1, 4-aminophenol-1 (this library) | quicklime; 98.5 wt% sulfuric acid; anhydrous fuel ethanol; the templates' structure and LCA; 4-aminophenol-1 D-009: the heat of dilution of sulfuric acid, 59.2 kJ/mol, derived from SRC-8 | library, internal | D-006 to D-008, D-011 |
| SRC-8 | US 4 307 249 A, E. L. Derrenbacker (Mallinckrodt), 1981, https://patents.google.com/patent/US4307249A/en | Example 1: 110 g of 95 to 98 % sulfuric acid added to 650 mL of water at 70 C, which rises to 90 to 95 C | read 2026-11-20 (Google Patents); facts only | D-007 (the order of the acid's dilution heat, with processes/4-aminophenol-1 D-009's derivation, 59.2 kJ/mol, a lower bound) |
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
calcium lactate at 0.14716 kg/kg in the broth (130 g/L of lactic acid as calcium lactate at an
ASSUMED broth density of 1070 kg/m3). The CSL dose is SRC-1's loading of 10 g/L, but per litre
of broth, ASSUMED: SRC-1 doses it per litre of its sugar feed (`_units.py` CoFermentation, the CSL
from the feed's volume times CSL_loading), a dilute hydrolysate that is most of its broth; the
70 wt% syrup here is diluted with the medium water, so per litre of syrup the dose would be
several times smaller. 157 g/L of
calcium lactate is about twice its solubility at 30 C (8.5 g/100 mL, SRC-3); whether it stays
dissolved at 50 C is not checked (L-4). The broth is therefore kept at or above 323 K until
acidulation (T-201), and crystallisation of calcium lactate in a cold spot is an open point.

The medium is sterilised continuously (E-101) and enters the fermenters at 323 K. The process
water S2 comes at 298 K like the slaking water; the syrup and the CSL arrive at 323 K. The net
LP steam of the steriliser is the medium water's warm-up, Q17 1478 kW (59.1 kW/K x 25 K, hand
estimate, 0.12 kWh per kg of lactic acid): the heat to the sterilising temperature is given back
to the incoming medium in a regenerative exchanger, which with the medium mixed at about 306.6 K
and leaving at 323 K works at an approach of about 16.5 K (ASSUMED); the sterilising
temperature and holding time are not set, and the holding section's losses are not counted.
The fermenters' sterilisation in place between batches (the recipe's cleaning step) is left out
of the flowsheet; its steam is an ASSUMED order of magnitude, about 2.7 MWh per batch (100 t of
steel at 0.5 kJ/(kg K) heated 298 to 394 K, doubled for the internals, losses and vented
steam), 2.2 GWh/a or 0.02 kWh per kg of lactic acid, 0.5 % of the steam heat, recorded as a
cut-off in lca/lca.yaml (D-011).

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
lactic acid, the largest single loss (3.8 % of the 13 601 kg/h formed, the basis of D-008). A displacement wash of the cake would recover most
of it at the cost of more water to evaporate; SRC-1 has none and none is designed here (an open
optimisation). Gypsum cake: 20.2 t/h, 1.61 kg per kg of lactic acid, to landfill or use, not
credited (D-011). The heats of the acidulation and of the acid's dilution are ASSUMED 0 (L-5),
so R301's duty (237 kW to cooling water) is not a heat of reaction: it comes from the heat
capacities assumed per kg (D-009). With the heats at 298.15 K set to 0, the reactions' change of
heat capacity over the 25 K between 298.15 K and 323.15 K gives -350 kW (ACL -599.6, ACA -484.0
and ACH -30.6 kJ/(kmol K) at 75.3, 10.2 and 8.6 kmol/h), mostly the dissolved calcium lactate
taken at water's heat capacity per kg; warming the 93 % acid S11 from 298.15 to 323.15 K takes
+112 kW back: -237 kW net. The heat left out is far larger. The acid's dilution alone is about
59 kJ per mol of H2SO4 or more (a lower bound that processes/4-aminophenol-1 D-009 derives from
SRC-8, US 4 307 249 A Example 1: 110 g of 95 to 98 % acid into 650 mL of water raise it from
70 C to 90 to 95 C); on the 95.3 kmol/h of S11 that is about 1.6 MW,
ASSUMED transferable to the 93 % acid, which has given up part of it already. The acidulation's
own heat (calcium lactate to gypsum and the free acid) is not sized (no data, L-5). R-301's
cooling is therefore of the order of 1.5 to 2 MW, not 237 kW, and the cooling water about
1.5 MW more than the model's; R-301's coil is to be sized on it (D-010).

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
  that recycle is rejected here because the unconverted glucose (2.6 t/h in the broth, D-005;
2.5 t/h reaching the esterifier after the cakes) would build
  up in it to some thirty times its feed. With the bottoms purged, a high single-pass conversion
  is needed; at SRC-1's equilibrium constant (4.5 at 351 K) and an ideal solution, a stirred
  reactor on this feed (with the recycles' water) would stop near 67 %, so the 98 % rests on the reactive distillation's
  removal of water, not on a source read (L-6).
- C-401, ester column at 20 kPa(a): ethanol, water, acetic acid and 99.5 % of the ethyl lactate
  (SRC-1's D403) overhead; the residue (glucose, the unconverted 2 % of the lactic acid, the
  sulfuric acid, fine gypsum; 3.1 t/h) at about 423 K (ASSUMED) to anaerobic digestion. With all
  the water overhead, the residue is a water-free melt of 82 wt% glucose with 8.5 wt% lactic
  acid and 3.7 wt% sulfuric acid at 423 K; whether it stays a stable, pumpable liquid is not
  checked (acid-catalysed dehydration and caramelisation of the sugar, its viscosity). A real
  column would likely keep water in its bottoms or dilute the residue as it leaves; that changes
  C-401's bottoms temperature and the residue's mass, not the lactic acid balance. An open point
  (Open inputs).
- C-402, ethanol column at 1 atm: 99 % of the ethanol (SRC-1's D402) overhead at about 91 wt%
  (SRC-1's recycle composition; the water split set for it), back to the esterifier (tear S18).
- R-402, hydrolysis at 363 K (ASSUMED; SRC-1 gives 4 h but no temperature) with 12 mol of water
  per mol of ester (SRC-1; the design specification `hydrolysis-water`), 80 % per pass (SRC-1).
  Its feed S25 is the ester S24 (373 K) and the recycled water S29 (323 K) mixed without heat
  exchange, 338.05 K at the heat capacities of process/materials.yaml; R-402 heats it to 363 K
  (Q11).
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
  water); R301 Q3 237 kW (an artefact of the assumed heat capacities, the acid's dilution heat
  left out, D-007); R401 Q6 214 kW; R402 Q11 1388 kW (the mixed feed S25 heated from 338 to
  363 K). Heats of reaction: SLK, FLA, FAA from formation enthalpies (SRC-3, SRC-4), the
  fermentation's neutralisations (in FLA, FAA, NEU) at the strong acid-strong base value
  -55.8 kJ/mol (ASSUMED); FBIO, ACL, ACA, ACH, EST, HYD ASSUMED 0 for want of data (L-5). The
  heat capacities of lactic acid and ethyl lactate are taken at acetic acid's per kg, those of
  glucose, the salts, cell mass and CSL at water's per kg (ASSUMED).
- Hand estimates (ASSUMED, the arithmetic in each energy stream's source), each heater and
  condenser pair closing its step's balance with the streams' sensible heats: E-401 four
  effects without thermocompression (Q4 13.7 MW of steam, Q5 14.5 MW condensed); C-401 reflux
  ratio 1 (Q7 12.1 MW MP steam, Q8 12.5 MW); C-402 reflux ratio 3 (Q9 5.1 MW, Q10 4.2 MW);
  C-403 reflux ratio 2 (Q12 6.1 MW, Q13 5.8 MW); E-404 two effects (Q14 11.0 MW, Q15 13.1 MW);
  E-405 product cooler (Q16 0.6 MW); E-101 the medium's steriliser (Q17 1.5 MW, D-005). Ethyl
  lactate's heat of vaporisation by Trouton's rule
  (88 J/(mol K) x 427.15 K = 37.6 kJ/mol, ASSUMED).
- Power (all ASSUMED): fermenter agitators 1880 kW (0.0985 kW/m3, the default of SRC-1's
  generic Reactor class, which SRC-1's own fermenter does not use: it takes a mixing intensity,
  or in batch mode a costed agitator; on 20 656 m3 of vessels, over the 146 h of 158 h they
  ferment), centrifuges 300 kW, filter 200 kW,
  evaporator 250 kW, purification 300 kW, preparation 100 kW; 3.03 MW, 0.24 kWh per kg of
  lactic acid.
Per kg of lactic acid (as 100 %): 4.09 kWh of steam heat (14.7 MJ), of which E-401 1.10,
C-401 0.97, E-404 0.88, C-403 0.48, C-402 0.41, the medium's steriliser 0.12, the hydrolysis
0.11 kWh; per kg of the 88 wt% product 2.75 kWh of LP and 0.855 kWh of MP steam. The
fermenters' sterilisation in place, about 0.02 kWh more, is a cut-off (D-005, D-011). No heat
integration (L-7): the condensers
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
by about 5.9 %, 0.985/0.93 = 1.059), ethanol to bioethanol-1, LP and MP steam as heat
delivered. The Atlas build (build_lci.py) also links process water, power, cooling water and
the wastewater WW through the shared lci/mappings.yaml entries; this folder's own assessment
(lca/gaps.csv) lists them as not mapped. The ester column's residue RES is a concentrated sugar
residue for anaerobic digestion (the registry's sugar-residue, added here), not a wastewater for
activated sludge, so the build does not link it to the wastewater treatment. Gaps in the build, with the
activity each should connect to: glucose syrup and corn steep liquor (no library producer; corn
wet milling is not in the library), the gypsum and cell mass cakes, the residue, and the
cleaning consumables with their disposal. Cut off with their amounts (lca/lca.yaml `cutoff:`):
the Amberlyst-15 resin of R-401, its charge 1135 kg on SRC-1's basis (3.9 wt% of one hour's
feed mass, `_units.py` Esterification) replaced once a year (ASSUMED), 1.0e-5 kg per kg; and the
fermenters' sterilisation steam (D-005). The carbon of glucose, CSL and ethanol is declared
biogenic. Emission
exclusions: the ethanol-bearing vents, the fermenters' and broth tank's breathing, the slaker
and acidulation vents (D-012). Not checked: SRC-1's cradle-to-gate 4.567 kg CO2-eq/kg is for a
lignocellulosic biorefinery with its own boiler and is not comparable with this gate-to-gate
inventory.

## D-012 Hazards (2026-11-19)
- The fermentation is exothermic: 5.27 MW for the whole train (Q2 less the agitators' 1.88
  MW), about 187 GJ per batch (5.27 MW x 9.879 h) released over 146 h, 0.36 MW per fermenter.
  If the cooling were lost for a whole batch, its 1106 t of broth (at water's 4.18 kJ/(kg K))
  would warm by about 40 K from the fermentation alone. The agitators add heat whatever the
  bacteria do: 2035 kW / 16 = 127.2 kW per fermenter (P2) over the 146.07 h, 66.9 GJ, another
  14.5 K. Together about 55 K, to about 378 K: above the broth's boiling point at 1 atm (water
  373.12 K; the dissolved salts raise it by about 1 K at most, ASSUMED). So the adiabatic whole-batch bound does not
  stay below boiling. What keeps it there: the fermentation heat comes from the bacteria, which
  ferment at 323 K (SRC-1, SRC-2), so an overheated batch is expected to stop releasing heat
  well before (ASSUMED, not quantified), which leaves the agitators' 14.5 K, to about 338 K; and
  a trip of the agitator on high temperature or lost cooling, which the safeguarding stage must
  add (control/cause-effect.yaml has no interlocks yet; Open inputs). The rise is slow (days),
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

## Basic engineering (from 2026-11-25)

Stage basic starts from the concept (PR #561) and keeps its numbers: the flowsheet, the recipe
and the duties are unchanged; the decisions below split the concept's items into the parts a
basic-engineering P&ID and layout need. No source beyond the register was read; every size,
condition and practice below is ASSUMED unless an SRC is named, and usual industry practice is
stated as an ASSUMED choice, not as data.

## D-013 Seed train: 5 stages at 1:10, three plant trains (2026-11-25)
Decision: SRC-1's 5 stages at 1:10 per step (ratio ASSUMED). The stage-5 seed is 7 % of the
batch (SRC-1's inoculum ratio 0.07, taken on the broth): 0.07 x 1033 = 72 m3, then 7.2, 0.72,
0.072 and 0.0072 m3. Stages 1 (7 L flask) and 2 (72 L lab fermenter) are grown in the
microbiology laboratory off-plot (a note on P-201); stages 3 to 5 are plant seed fermenters R-211
(1 m3), R-212 (10 m3) and R-213 (about 107 m3), at about 72, 72 and 67 % fill (ASSUMED; D-030). On SRC-1's 7 %
of the feed (761 t of medium per batch, S6 x 9.879 h) the seed medium is 53 t; the 72 m3 basis is
the larger and sizes R-213. The seed medium is a side-draw of the sterile medium header (D-014),
so the flowsheet's medium and the production fermenters' totals are unchanged (L-3 stands: the
seed's growth is not modelled apart).
- Schedule: SRC-1 sizes its seed batch on the main titer and productivity, 130 / (0.95 x 0.89) =
  153.8 h per stage; five stages in series would take 769 h, and no schedule that must inoculate
  every 9.88 h can follow it. A seed stage is grown to the late exponential phase instead: at 1:10
  about 3.3 doublings, at a doubling time of 1 to 1.5 h plus a lag (ASSUMED, no source read) 6 to
  8 h; chosen 8 h of growth, 1 h fill and up to 0.9 h transfer, so a stage occupies its vessel
  9.88 h (one production period) from fill to transfer, then SRC-1's 12 h turnaround (emptying,
  CIP, SIP, cool-down): 21.88 h per vessel cycle.
- Trains: each stage must deliver every 9.88 h, so ceil(21.88 / 9.88) = 3 vessels per stage:
  three trains A, B, C, each starting a seed every 29.64 h (7.76 h slack per cycle), staggered by
  one period; stage 3 of a train is filled at period k, transfers to stage 4 at k+1, to stage 5
  at k+2 and into the production fermenter at k+3. SRC-1's two trains would need a cycle of at most
  19.76 h, which leaves 7.76 h for fill, growth and transfer after the 12 h turnaround: rejected
  as too tight. Every seed fill falls in a production fill campaign of the steriliser (D-014).
- No seed hold tank (ASSUMED): stage 5 transfers straight into the filling production fermenter
  by sterile nitrogen pressure (no pump seal on the sterile boundary); SRC-1's `SeedHoldTank` would
  add a sterile vessel and a holding time for a culture that is better transferred in its
  exponential phase. Rejected: SRC-1's hold tank with a pump.
- pH: stage 5 on the milk-of-lime ring main like the production fermenters (D-018); stages 3 and
  4, too small for a lime slurry branch (plugging), on NaOH 10 wt% from T-215 through a 0.2 um
  sterile filter (ASSUMED; about 0.5 t of solution per stage-4 batch, its sodium neglected).
- Seed fermenters: 3.0 barg and full vacuum, 150 C, SS316L, jackets on cooling water, top-entry
  agitators (A-211 0.4 kW, A-212 2.2 kW, A-213 15 kW, ASSUMED), sterile vent and inlet gas filters
  as on R-201A (drawn on P-201, tagged there as parts of the fermenter), in building B-201 (D-026).

## D-014 Medium preparation: blended at the fill rate in campaigns (2026-11-25)
Decision: the flow mismatch (the flowsheet carries the year-average medium S6, 77.0 t/h, but a
fermenter fills in 4 h, recipe) is resolved by running medium preparation and the steriliser
in campaigns at the fill rate: 761 t in 4 h = 190 t/h, designed for 200 t/h (ASSUMED margin),
about 4 h of every 9.88 h, the seed stages' side-draws within the same campaign (D-013). Syrup,
CSL and process water are blended in line on ratio control into V-101 (the concept's 200 m3,
about 1 h at the fill rate), so the averaging happens in the syrup and CSL day tanks. Between
campaigns the steriliser is stopped, not held hot; it is re-sterilised before each campaign on
once-through water (D-015, revised 2026-11-25 for review finding #5). The year average of the
medium heating is unchanged: Q17 1478 kW stays the net steam (D-005), the campaign peak is
3.8 MW (D-015); the re-sterilisation steam comes on top (D-015).
Rejected: E-101 continuous at 77 t/h into a sterile medium buffer of one batch (about 720 m3 of
24 wt% sugar at 323 K, an ideal growth medium held sterile for up to 10 h: a large sterile
vessel with SIP, a filter and a contamination risk on every batch).
Storage (ASSUMED): syrup T-101A/B 2 x 2150 m3, 7 days at 1340 kg/m3 (ASSUMED density); syrup day
tank T-103 450 m3 (one day); CSL storage T-102 200 m3 (7 days) and day tank T-104 25 m3; syrup
and CSL tanks kept at 323 K (the concept's feed temperature).

## D-015 Continuous steriliser E-101 in its parts (2026-11-25)
Decision: the concept's E-101 becomes the train regenerative exchanger E-101, steam heater E-102,
holding tube X-101, trim cooler E-103, back-pressure valve and divert valve, at 200 t/h:
- Sterilising temperature 413 K (140 C) and hold 120 s: ASSUMED (usual continuous medium
  sterilisation practice, no source read; Open inputs).
- E-101, wide-gap plates (CSL solids): raw medium from about 306.6 K (the blend, D-005) to
  396.6 K against the sterile medium from 413 K to 323 K, 16.5 K approach on both ends (D-005's
  approach, now on both ends because both sides carry the same flow and heat capacity), about
  21 MW at 200 t/h. E-102 on LP steam: 396.6 to 413 K, 16.4 K x 89.4 kW/K = 1.47 MW on the year
  average (the medium at water's heat capacity per kg, D-009), which is Q17 1.48 MW; at 200 t/h
  3.8 MW, E-102 designed for 4.0 MW. E-103 on cooling water, 1.0 MW, for start-up on water and the
  regenerator's drift.
- Sterile side above raw side in E-101 (revised 2026-11-25, review finding #1: with only the
  back-pressure valve after E-103 the raw side, upstream of E-102 and X-101, is at the higher
  pressure, so a plate leak would carry raw medium into the sterile medium). A sterile-side
  booster P-108A/B (sanitary, variable speed, double mechanical seal with a steam barrier,
  ASSUMED) after X-101 raises the sterile side. Pressures (ASSUMED, pressure drops of about
  0.5 to 0.7 bar per exchanger pass and 0.5 bar in X-101): X-101 outlet 3.5 barg (PIC-1029 on
  the booster speed; 0.9 bar above water's 2.6 barg at 413 K, SRC-4), so the raw side enters
  E-101 at about 5.4 barg; the booster delivers about 7.1 barg (3.6 bar, about 40 m), the sterile
  side leaves E-101 at about 6.4 barg, 1.0 bar above the highest raw pressure, and PIC-1026
  holds about 6 barg after E-103 with PV-1026. PDT-1028 measures the sterile outlet of E-101
  against its raw inlet; below 1.0 bar (ASSUMED) it diverts like a low holding temperature
  (C&E I-103). Rejected: a second pump on the raw side after E-101 (the raw side at 397 K would
  have to stay above 2.2 bar(a) anyway, leaving too little margin), and a double-wall or
  intermediate-loop regenerator (a third circuit and about twice the plate area).
- Standby and water (revised 2026-11-25, review finding #5): no hot standby on water circulating
  to V-101, and no water into V-101 at all. Before each campaign the steriliser and the sterile
  header are sterilised on once-through process water (XV-1034 into the P-104 suction) at 413 K
  for 30 min (ASSUMED) to the wastewater (XV-1032, 150-WW-1018); the water-to-medium front at the
  start goes to the wastewater for one hold-up volume (about 10 m3, ASSUMED), the last medium of
  a campaign is pushed forward into the fermenter being filled by water (about 10 m3, about 1 %
  of a batch, ASSUMED, the blend of the last hour made correspondingly stronger). Only a divert of
  medium returns to V-101 (XV-1030). Steam on top of Q17 (ASSUMED estimate): heating the hold-up
  and steel (about 1 h at up to 2 MW) plus 30 min at 100 t/h with the regenerator's 16.5 K
  approach (about 1.9 MW), about 2.5 to 3 MWh per campaign, i.e. about 0.3 MW or 0.5 t/h of LP
  steam as a year average (+20 % on Q17), and about 50 m3 of wastewater per campaign; Q17 and the
  LCI do not carry it yet (Open inputs).
- X-101: 120 s at 189 m3/h = 6.3 m3, DN 250 (0.049 m2, 1.07 m/s), about 130 m of serpentine on a
  skid, rising, insulated. The holding pressure is above water's 3.6 bar(a) at 413 K (SRC-4's
  IAPWS series gives 450 kPa at 421 K): held at 3.5 barg by PIC-1029 (see the booster above);
  design 10 barg, 160 C.
- Divert: TT-1023 and TT-1024 (two elements, 1oo2) at the holding-tube outlet; below 411 K
  (ASSUMED, 2 K under the set point) or on PDT-1028 low, the divert pair after PV-1026 acts:
  US-1025 closes the forward valve XV-1025A to the sterile header, UY-1025 opens XV-1025B back to
  V-101 (a pair of on/off valves instead of one three-way valve, so the forward valve is a tight
  block); the sterile side is then re-sterilised on water at 413 K for 30 min (ASSUMED) before
  forward flow is released. C&E I-101 to I-103. Rejected: diverting at the holding-tube outlet
  (413 K medium to an atmospheric tank).

## D-016 Production fermenters R-201A to P (2026-11-25)
Decision: 16 tags R-201A to R-201P (the concept's R-201 split). Each 1291 m3 (D-010), D 9.0 m,
straight side 17.3 m (63.6 m2 x 17.3 m = 1100 m3 plus two 2:1 heads of 95.4 m3), 2 m skirt,
23.8 m overall; broth level about 14.7 m above the bottom tangent. Design 2.5 barg and full
vacuum (D-034 replaces the -0.3 barg first chosen here), 150 C (SIP at about 121 C, 1.05 barg;
ASSUMED). Material SS304 (SRC-1) with SS316L nozzles and probe ports
(ASSUMED); empty weight about 100 t (D-005). Agitators A-201A to P tagged apart (they carry the
trip of D-017): top entry, 127 kW absorbed (D-012: 2035 kW / 16; D-009's 1880 kW is the year
average), 160 kW motor (ASSUMED next size with margin), gearbox on the top head, double mechanical
seal with a sterile barrier fluid (condensate or water at above the headspace pressure, ASSUMED).
R-201A is drawn in full on P-202 as the typical; B to P on P-203 with the common headers and
their branch valves, noted "instrumented as R-201A, typical". Rows outdoors on a foundation with
a steel access structure at their tops (D-026).

## D-017 Fermenter temperature: half-pipe coils on a tempered-water loop (2026-11-25)
Decision: half-pipe coils on the shell, each fermenter with its own tempered-water loop: pump
P-201x (85 m3/h) circulates through the coils; cooling water is injected on TIC-2011x (broth
temperature, set 323 K) by TV-2011x, the surplus overflowing to the cooling-water return (ASSUMED
usual practice; keeps the coil inlet warm against calcium lactate crystallising at a cold wall,
D-005). Duty: Q2 7153 kW / 16 = 447 kW per fermenter on average; peak 1.5 times (ASSUMED) = 0.67
MW; at U 400 W/(m2 K) and an LMTD of 11 K (broth 323 K, loop 308 to 315 K, ASSUMED) 152 m2 of the
416 m2 of wetted shell. Alarms TAH-2011x on the broth; an independent TT-2012x with TSHH-2012x
(set 333 K, ASSUMED) and FSLL-2014x on the loop flow (lost cooling) trip the agitator A-201x (the
open safeguard of D-012) and alarm; in control/cause-effect.yaml once P-202 is drawn. Rejected:
cooling water straight through the coils (a cold wall at 298 K).

## D-018 pH: milk-of-lime ring main with dosing branches (2026-11-25)
Decision: pH 5 to 6 (set 5.5, ASSUMED) on two steam-sterilisable pH probes AT-2021x and
AT-2022x (two of two compared, deviation alarm), AIC-2021x to the on/off dosing valve AV-2021x
on a DN 25 branch of a circulating milk-of-lime ring main, with a water flush connection after
each dose against plugging and a steam block at the vessel nozzle (D-020). Demand: S7 34.9 t/h,
about 2.4 t/h per fermenting vessel on average (about 15 vessels ferment at once), 3.5 m3/h peak
(ASSUMED 1.5 times at 1150 kg/m3). Ring main DN 100 from T-105 through all fermenters and back,
P-106A/B at 80 m3/h (2.8 m/s), about twice the 35 m3/h of all draws, so the return end stays above
1.4 m/s (ASSUMED minimum against settling); PIC-1035 holds the ring pressure by a back-pressure
valve at the return. The milk of lime is not sterile: its pH (about 12.4) and the slaking heat
keep its bioburden low, and the thermophilic fermentation at 323 K and pH 5 to 6 is robust
(ASSUMED; no source read); the dosing branch's steam block is the sterile boundary, accepted
as a contamination risk. Rejected: NaOH or ammonia (sodium or ammonium sulfate instead of
gypsum downstream: another route, D-001).

## D-019 No aeration; nitrogen overlay, sterile filters, relief and vacuum protection (2026-11-25)
Decision: the fermentation is not aerated: SRC-1 runs it in batch with no air or oxygen input and
no CO2 among its products (homofermentative lactic acid bacteria, glucose to two lactic acid);
the fermenters have no sparger, compressor or air filter train, and a note on P-202 says so.
- Overlay: sterile-filtered nitrogen at 0.3 barg (ASSUMED) keeps the sterile boundary under
  positive pressure, PIC-2041x split range on the N2 inlet PV-2042x and the vent back-pressure
  valve PV-2041x. N2 about 1340 Nm3 per harvest (1033 m3 at 1.3 bar(a)) and 1300 Nm3 per SIP
  cool-down, about 270 Nm3/h on average (ASSUMED estimate), from a site supply at the battery
  limit. Rejected: a plain sterile vent (air drawn in at harvest; no positive pressure).
- Filters: vent F-201x and inlet gas F-202x, DN 150 housings with 0.2 um hydrophobic cartridges,
  steam-sterilised with the vessel, condensate drained at the housing low points. DN 150 because
  the cool-down after SIP condenses about 1291 m3 of steam: at a controlled cool-down of at least
  60 min (ASSUMED, by the coil valve) about 1300 m3/h of gas must come in (20 m/s in DN 150).
- Relief: a sanitary reverse-acting rupture disc on the headspace, set 2.5 barg, sized on the SIP
  steam case (the SIP steam valves failed open, about 3 t/h of LP steam, ASSUMED; sizing at
  stage basic, piping/special-items.yaml), discharged to a safe location. Vacuum: the gas inlet
  (operational) and a vacuum relief valve set at -0.2 barg admitting gas through F-202x
  (ASSUMED), so the -0.3 barg rating is never reached.

## D-020 Sterile boundary, steam blocks and aseptic sampling (2026-11-25)
Decision: the sterile boundary runs at the first valve on every line into a sterile vessel or
header; every entry that is opened and closed (medium inlet, inoculum inlet, lime dosing, harvest
and CIP return, CIP supply, sampling) has a steam block: two block valves with steam fed and
condensate drained between them (double block and bleed with steam, ASSUMED usual practice),
steamed whenever the line is idle. The aseptic sampling valve is steam- and condensate-flushed
before and after each sample. The boundary is marked on the sheets by notes and spec breaks
(sterile class SS316L, orbital-welded, drainable). SIP steam enters at the headspace and at the
bottom; condensate traps at the low points (bottom valve cluster, filter housings, coil drain).

## D-021 CIP station and SIP steam (2026-11-25)
Decision: one CIP station in building B-201 for the production fermenters, seed fermenters and
transfer lines: caustic T-221 (NaOH about 2 wt%, 353 K), acid T-222 (nitric acid about 1 wt%,
weekly), fresh water T-223, recovered rinse T-224 (40 m3 each), caustic 50 wt% make-up T-225 with
P-223, heater E-221 on LP steam (2.0 MW), supply pumps P-221A/B (60 m3/h at about 3 barg at the
spray devices on the fermenter top: about 30 L/min per metre of circumference, 28 m for 9 m, 51
m3/h, ASSUMED), return pumps P-222A/B (self-priming). Sequence (ASSUMED): pre-rinse from T-224,
caustic 30 min at 353 K, rinse, acid weekly, final rinse to T-224. The concept's 20 t of rinse
water and 50 kg of NaOH per fermenter cleaned stay (D-003). SIP: plant LP steam through the
sintered steam filters F-231A/B (1 um, ASSUMED; filtered plant steam, not clean steam) to the
sterile users, 121 C for 30 min (ASSUMED); its condensate drained to the wastewater (not returned:
possible product contamination, ASSUMED). The SIP steam per batch is the concept's cut-off
(D-005).

## D-022 Lime: silo, feeder, slaker and milk-of-lime tank (2026-11-25)
Decision: quicklime silo V-102 (400 m3, 3 days at 1000 kg/m3 bulk, ASSUMED) with a bin vent
filter, weigh feeder X-102 to slaker R-101 (the concept's 40 m3, D-006), slaker vent to a wet
scrubber, a grit screen at its outlet, pumps P-107A/B to the milk-of-lime tank T-105 (250 m3, 8 h
of S7 against a slaker outage, ASSUMED), ring main pumps P-106A/B (D-018).

## D-023 Sheets, tags, line numbers (2026-11-25)
Decision: ten P&IDs as the specification plans them: P-101 medium and steriliser, P-102 lime and
ring main, P-201 seed train, P-202 R-201A (typical, detailed), P-203 R-201B to P with headers,
harvest and T-201, P-204 CIP and SIP, P-301 cell removal, acidulation and gypsum, P-401
evaporation, P-402 esterification and ester column, P-403 ethanol recovery, hydrolysis and
product; all `planned` in plant.yaml. P-203 and P-201 may be generated by scripts (16 fermenters,
three trains).
- Equipment tags: letter, area digit and two digits (T tank, V vessel or drum, R reactor or
  fermenter, A agitator of a fermenter, E exchanger or evaporator, X holding tube or feeder, P pump,
  K vacuum pump, S centrifuge or solids filter, F gas or steam filter, C column); A, B... for
  installed spares and parallel units, the fermenter letter for its own items (P-201A belongs to
  R-201A). Other tanks' agitators are parts of their tanks.
- Line numbers: `<DN>-<fluid>-<area><three digits>[train letter]`, e.g. 200-SM-2001A; fluid codes
  SM sterile medium, PM process medium, IN inoculum, BR broth, ML milk of lime, CS/CR CIP supply
  and return, LS LP steam, SS filtered SIP steam, CD condensate, NS sterile nitrogen, VT vent,
  TW tempered water, CW/CWR cooling water, PW process water, PL process liquid. DN from a velocity
  basis given per line in the line list (liquids 1 to 2.5 m/s, slurries at least 1.5 m/s,
  gas and steam up to 30 m/s; ASSUMED).
- Instrument tags: ISA letters and a loop number `<area><two digits>` plus the fermenter or train
  letter (TIC-2011A on R-201A; TIC-2131B on R-213B).

## D-024 Harvest and broth hold (2026-11-25)
Decision: each fermenter's bottom valve cluster (harvest and CIP return) on a DN 250 harvest
header; harvest pumps P-202A/B, 280 m3/h (1106 t in 4 h, recipe) to T-201 (the concept's 2500 m3,
D-010), agitated, insulated, with an LP-steam coil to hold at or above 323 K (D-005); broth feed
pumps P-203A/B, 125 m3/h on T-201's level and the downstream rate, to the centrifuges.

## D-025 Downstream items for basic engineering (2026-11-25)
Decision (sizes ASSUMED from the flowsheet flows): three disc-stack centrifuges S-301A to C, two
running (55 m3/h each), cake hopper V-301 and cake pumps to anaerobic digestion; R-301's cooling
on a pump-around through the spiral exchanger E-301 sized for 2.0 MW (D-007's 1.5 to 2 MW with
the acid's dilution heat; a coil of about 200 m2 in a 150 m3 gypsum slurry tank was rejected for
scaling), acid storage T-301 (7 days) and dosing pumps; belt filter S-302 with liquid-ring
vacuum pumps K-301A/B, filtrate receiver V-303 and pumps; evaporator E-401 as effects E-401A to D
with circulation pumps, surface condenser E-402, receiver V-401 and vacuum pumps K-401; R-401
with feed heater E-411; C-401, C-402 and C-403 each with reboiler, condenser, reflux drum, reflux
and bottoms pumps (C-401 with vacuum pumps K-421); R-402 with heater E-441; E-404 as effects
E-404A and B with condenser E-461, drum V-461 and vacuum pumps K-461; product cooler E-405;
product tanks T-401A/B (7 days); ethanol make-up tank T-402 with pumps P-472. The flowsheet links
name the split tags (R-201A to P, S-301A to C, E-401A to D, E-404A/B, the steriliser's parts).

## D-026 Plot plan (2026-11-25)
Decision: a 360 m x 260 m site (ASSUMED) with a perimeter road and internal roads (8 m), areas
A-110 lime, A-130 media day tanks, A-120 with the clad building B-201 for medium preparation,
the steriliser, the seed train and the CIP station, A-200 production fermentation, A-300 cell
removal, acidulation and gypsum with the gypsum store A-310, A-400 evaporation and purification
(the ethanol area), A-600 tank farm (syrup, CSL, acid, product), A-610 ethanol storage apart,
A-700 control room and substation, A-800 utilities (reserved). The production fermenters stand
outdoors in two rows of eight (pitch 14 m, 5 m between shells) on a foundation, the main rack
PR-1 between the rows (tiers 6, 8 and 10 m), the tempered-water pumps beside the rack, a steel
access structure at the fermenter tops for the agitator drives and filters (structures.yaml at
the layout-3d step). Racks PR-4 and PR-6 (along B-201's north wall) take the medium, inoculum,
CIP and SIP headers from the building to PR-1; PR-5 and PR-3 serve the tank farm and the
downstream areas, PR-2 the ethanol area. A branch line that starts at a header names the area
of its tie-in (`from_area: A-200`), since a header has no single position. Rejected: a fermentation hall (16 vessels of 24 m: a building of about
120 x 45 x 30 m for no process reason; the drives need weather protection only). Separations
(ASSUMED, measured by `cheme validate`): the ethanol area and the ethanol tank at least 30 m from
the control room and substation, the ethanol tank 15 m from the site boundary, tanks 8 m from
roads. Elevated items (agitators, fermenter filters) are placed at their elevation; their mounts
and structures follow with the 3D layout (gate layout-3d).

## D-027 Component balances with the NUT lump (2026-11-25)
Decision: the basic gate's component balance of PREP, FERM, ACID, R201 and R301 cannot be
evaluated because the CSL protein lump NUT has no formula (D-004). Its mass balances close. A
formula would be invented data (no CSL composition was read), so the five findings are accepted
at the gate `process-basic` in checks/checks.yaml with this reason, for the design review to
confirm. Rejected: an ASSUMED amino-acid formula for NUT (it would make a nitrogen balance look
sourced that is not, L-3).

## D-028 P-101 split: medium preparation P-101, continuous steriliser P-103 (2026-11-25)
Decision: the sheet frame is A3; storage, day tanks, blending and the steriliser do not fit on one
readable sheet. P-101 keeps syrup and CSL receipt, storage T-101A/B and T-102, day tanks T-103
and T-104, their pumps, the ratio blend (FIC-1011/1012/1013) and V-101 with LIC-1014; the new
P-103 carries the steriliser (P-104A/B, E-101, E-102, X-101, P-108A/B, E-103, PV-1026, the divert
pair XV-1025A/B, the water and wastewater connections). 250-PM-1004 (V-101 to P-104) and
200-PM-1007 (divert to V-101) continue across both sheets under their numbers. New lines
150-PM-1008/1009 (syrup receipt and transfer), 50-PM-1010/1011 (CSL), 200-PM-1012/1013,
200-SM-1014/1015/1016 (the steriliser's legs between items), 150-WW-1018, 150-PW-1019 and the
utility connections 200-LS-1021, 80-SC-1022, 150-CW-1023/1024 (sizes in the line list, velocity
bases ASSUMED). New level indicators LI-1003/1004/1005 on the storage tanks. Drawn from
scripts/draft_P-101.py and scripts/draft_P-103.py (provenance; both sheets are hand-maintained
from now on). Tank heating coils are named in a note on P-101, not drawn (basic level). Open
drawing warnings on P-103: two signal lines (US-1025 to XV-1025A, PDT-1028 to US-1025) cross the
booster discharge 200-SM-1014, which encloses the instruments of the sterile loop; the CW
connections of E-103 end in connectors by the exchanger because every way to a sheet edge crosses
the sterile loop or the header.

## D-029 P-102 lime slaking and ring main as drawn (2026-11-25)
Decision: P-102 ("Lime and ring main") draws V-102 with pneumatic filling (100-QL-1110), the
weigh feeder X-102 (WIC-1032, its rate set by LIC-1034 on T-105), R-101 with slaking water on
FV-1105 (ratio to the lime rate, ASSUMED), the cooling coil on TIC-1033/TV-1033 (100-CW-1107/1108,
820 kW at a 10 K rise, ASSUMED), the vent to the wet scrubber (150-VT-1106), P-107A/B to T-105,
P-106A/B (suction 150-ML-1109) into the ring main 100-ML-1102 and its return 100-ML-1103 with
PIC-1035/PV-1035 and FIL-1036. R-101 is drawn and listed as a Vessel (agitated, in a note):
this core's DEXPI classes have no stirred-tank reactor; the seed fermenters will meet the same
(core limit, candidate issue). Review finding #8 (ring-main return velocity at peak draws) is
not resolved by this sheet: P-106A/B stay at 80 m3/h until it is decided.

## D-030 Seed train A on P-201; transfer hydraulics and campaign timeline (2026-11-26)
Decision: P-201 draws train A in full (R-211A, R-212A, R-213A with agitators A-211A to A-213A,
T-215, P-215A/B, F-215); trains B and C go on the new sheet P-205 as typicals of train A (planned;
their 12 list items moved to it). Drawn from scripts/draft_P-201.py (provenance; the sheet is
hand-maintained from now on). ASSUMED throughout, no source read:
- Per vessel: medium from 100-SM-2003, base (NaOH 15-NA-2147 through F-215; lime 25-ML-2131A on
  R-213A) and inoculum each through a steam block (two ball valves, 15-SS-2148 steam and a trap to
  the drain between them, D-020); the R-213A outlet 100-IN-2138A has its own steam block before
  100-IN-2004 (P-203). Sterile N2 from 40-NS-2141 through the inlet filter F-242A/244A/246A and
  PV-21x4A (PIC-21x4A on the N2 inlet), vent through F-241A/243A/245A and a hand valve to atm. (a
  constant sweep; closed for a transfer). Rupture disc on each vessel to a safe location (sizing
  on the SIP steam case at detail). Jackets on cooling water with TIC-21x1A on TV-21x1A; pH
  AIC-21x2A on AV-21x2A; WI-2113A/2123A (load cells), LI-2133A (radar). Bottom valve cluster:
  bottom valve, SIP steam tee (25-SS-2150 from 50-SS-2144), transfer tee, CIP return valve to
  50-CR-2143; CIP supply 50-CS-2142 to a spray device through one valve, steamed with the vessel
  (the steam-block rule of D-020 is not applied to CIP connections of the seed vessels: open for
  the review). Headers to P-205 at the right edge. Drawing: SIP steam is the lowest top header so
  no steam-block feed crosses a header; the 31 remaining crossings (drops through the headers
  below) and the CW stubs are accepted in checks.yaml with this reason.
- Transfer hydraulics (review S1#2): R-213A in B-201 to the R-201 top inlets, about 250 m of DN 100
  (S1 estimate). Transfer in 1.5 h instead of 1 h: 48 m3/h, 1.7 m/s; friction scales with v^2 from
  S1's 1.3 to 1.7 bar at 2.5 m/s to about 0.6 to 0.8 bar; lift to the 23.8 m fermenter top about
  2.4 bar (24 m at 1030 kg/m3, ASSUMED); target headspace 0.3 barg: R-213A at about 3.5 barg at
  the start of the transfer. R-213A's design pressure is raised from 3.0 to 6.0 barg (list
  updated; a 4 m vessel at 6 barg is ordinary) so the transfer runs at least 1.5 bar below it;
  R-211A and R-212A stay at 3.0 barg (local transfers in B-201, lift under 5 m). The line hold-up
  (about 2 m3, 250 m x 7.9 L/m) is blown forward into the fermenter with sterile N2 at the end of
  the transfer, then the line is steamed (D-020). The 1.5 h transfer fits D-013's cycle: stage 5
  occupies 1 h fill + 8 h growth + 1.5 h transfer = 10.5 h, plus 12 h turnaround = 22.5 h, under
  the 29.64 h a vessel has per seed (three trains). Rejected: a bottom inoculum inlet (the broth
  head adds up to 1.5 bar), stage 5 beside the fermenter rows (a second sterile building).
- Campaign timeline (review S1#6): per production period (9.88 h) the steriliser runs 1.5 h
  heat-up and 30 min water sterilisation (D-015), 4 h production fill at 190 t/h, then the seed
  fills at about 80 t/h (40 % of the 200 t/h design, ASSUMED within a plate steriliser's turndown;
  the hold time rises to about 5 min, on the safe side): 72 m3 to a stage-5 vessel in about 1 h,
  7.2 and 0.72 m3 to stages 4 and 3 in the same hour on their own branches; 6.5 to 7 h of 9.88 h.
  The seed fill is never inside a production fill, so the steriliser never exceeds 200 t/h.
  R-213 holds 72 m3 in about 107 m3: 67 % fill, not 72 % (D-013 corrected). The seed medium is the
  full-strength production medium (about 240 g/L sugar, ASSUMED acceptable for the strain; no
  source read, Open inputs); dilution with sterile water rejected for now (a sterile water supply).

## D-031 P-202: production fermenter R-201A as drawn, the typical of R-201A to P (2026-11-26)
Decision: P-202 draws R-201A in full (scripts/draft_P-202.py is provenance; the XML is the source,
with the second split-range signal of TIC-2011A added by hand from `cheme fragment signal`). It
answers the open review findings S1#3, S1#4, S1#7, S2#9 and, for R-201A, S2#1/S3#5 and S3#4.
Changes to D-016 to D-021, each ASSUMED unless a source is named:
- **Class.** R-201A to P are DEXPI `Vessel` with a separate `Agitator`, as the seed fermenters
  (one class for all fermenters, S3#3); F-201x/F-202x are `GasFilter`.
- **Temperature, heating (S1#7).** The tempered-water loop of D-017 gets direct LP-steam injection
  TV-2011B (25-LS-2031A, check valve) besides the CW injection TV-2011A; TIC-2011A is split range
  (0 to 50 % steam, 50 to 100 % CW). Heating is needed at the start (medium arrives at about 323 K
  from E-101 but the steel and coil water start cold) and in the lag phase of an outdoor vessel in
  winter: shell about 620 m2 at an ASSUMED 0.5 W/(m2 K) insulated loss and 40 K to winter ambient
  is about 12 kW, the coil water about 10 m3; 100 kW (about 0.15 t/h of steam) is the ASSUMED
  heater size. CW injection: 0.67 MW with CW at 298 K replacing loop water at 315 K is 34 m3/h,
  DN 80 at 1.9 m/s; the same flow overflows to the CW return. Rejected: a separate plate heater on
  the loop (more equipment for a duty used a few hours per batch).
- **Headspace pressure.** PIC-2041A holds 0.3 barg on the vent back-pressure valve PV-2041A; N2 is
  made up by the self-acting regulator PCV-2042A set at 0.25 barg (tank-blanketing practice),
  instead of the split range of D-019. Reason: the N2 make-up (the cool-down after SIP, the
  harvest) then works without the control system and cannot be driven open by a controller fault;
  its trim is restricted to about 1500 Nm3/h at 6 barg.
- **Relief (D-019).** PSE-2045A, rupture disc set 2.5 barg on its own DN 150 nozzle to a safe
  location. Cases: SIP steam valves failed open, 3 t/h of LP steam: 0.83 kg/s at about 3.5 bar(a)
  and 140 C (1.85 kg/m3) is 0.45 m3/s, 25 m/s in DN 150; PCV-2042A failed open, 1500 Nm3/h =
  0.52 kg/s of N2 at 3.65 kg/m3 is 0.14 m3/s. The SIP steam case governs (piping/special-items.yaml).
  The same check of the N2 failure case is what S3#1 asks of the seed vessels (left to S9).
- **Vacuum (S1#4).** The governing credible case is steam collapse after SIP: cooling water into the
  coils at the full loop flow (TV-2011A open early or failed open) takes up to about 8.9 MW
  (23.6 kg/s by 90 K), condensing about 4 kg/s of steam, about 24 000 m3/h of gas demand at
  atmospheric pressure; cold medium or CIP spray into a steamed vessel is of the same order. No
  sterile-filter path can pass that, so the case is **prevented, not relieved**: I-204 (PALL-2043A
  at -0.05 barg, own tapping) closes TV-2011A and the medium inlet; the sequence permits coil
  cooling, fill and CIP only with the headspace above +0.1 barg under N2 (control/sequences.yaml,
  stage S9). PSV-2046A (vacuum relief at -0.2 barg, drawn as a check valve, no vacuum-valve class
  in the authoring API) admits air through F-202A for the loss of N2 make-up during the controlled
  cool-down, 1300 m3/h (D-019). If the HAZOP/LOPA does not credit I-204 and the permissives, the
  fermenters must be rated for full vacuum: an open item for the HAZOP of the fermentation area.
- **Vent filter wetting (S1#4).** During CIP the hydrophobic cartridge of F-201A is isolated by
  XV-2043A and the vessel vents through the bypass XV-2044A (100-VT-2028A); both filters are
  steamed with the vessel and drained at the housing low points through traps.
- **High level (S3#4 for R-201A).** LIC-2031A (radar) closes the outer medium valve XV-2033A at the
  batch volume (14.7 m); LSHH-2032A, an independent switch at 16.0 m (1.3 m = 83 m3, 19 min of the
  258 m3/h fill, below the vent nozzle), closes the inner valve XV-2034A (I-203).
- **Steam blocks (S2#1, S3#5 for R-201A).** Medium, inoculum, lime, CIP supply, CIP return and
  harvest each have a steam block. The head SIP steam enters through the CIP spray line (it steams
  the spray device and the line after the block); the bottom SIP steam through the bottom valve
  cluster, with TI-2015A at the coldest point (121 C for 30 min, D-021).
- **Lime dosing and the sterile boundary (S2#9).** The boundary is the steam block at the nozzle of
  the DN 25 dosing branch, steamed while idle; after each dose the branch is flushed with water
  (25-PW-2032A) against plugging. When dosing, non-sterile milk of lime crosses the boundary: the
  contamination risk is accepted on the lime's pH of about 12.4 and the robust thermophilic
  fermentation at 323 K, pH 5 to 6 (as D-018; no source read).
- **Aseptic sampling** on a DN 25 shell nozzle: sampling valve, steam fed between it and the outlet
  valve, flushed to drain before and after each sample.
- **Trips** in control/cause-effect.yaml: I-201 TSHH-2012A (333 K) and I-202 FSLL-2014A stop
  A-201A (D-012); I-203 LSHH-2032A; I-204 PALL-2043A. SIL: from the HAZOP/LOPA, not assumed.
- **Turnaround with SIP (S1#3).** Timed sequence (all ASSUMED): harvest 3.7 h (1033 m3 at
  280 m3/h) + drain 0.3 h = 4.0 h; CIP 1.5 h (pre-rinse 15 min, caustic 30 min at 353 K, rinse
  15 min, final rinse 15 min, drains 15 min); SIP 3.0 h (heat-up and air purge 1.5 h: about 4.5 t of
  steam at 3 t/h for 100 t of steel by 71 K = 1.6 t, the steam inventory of 1291 m3 = 1.45 t and the
  purge; hold 0.5 h; controlled cool-down under N2 1.0 h); fill 4.0 h. Total 12.5 h against the
  12 h of D-003: the batch cycle becomes 158.6 h and the harvest period 158.6 / 16 = 9.91 h instead
  of 9.88 h, 0.3 % fewer batches a year. Decision: keep 16 fermenters and the solved flowsheet (the
  difference is within the precision of the ASSUMED step times); record the 12.5 h as the basis of
  the control sequences, and recover the 0.5 h, if the schedule needs it, by starting the CIP
  pre-rinse while the harvest drains. Rejected: a 17th fermenter for 0.3 %.
- **Line numbers.** The lime branch is 25-ML-2024A (25-ML-2021A reused the sequence of 80-SS-2021A).

## D-033 P-202 to the S4 review: tags, agitator drive, coils, I-204, relief load, turnaround (2026-11-26)
Decision: P-202 stays hand-maintained; `scripts/fix_P-202_s4b.py` (run once, provenance) added the
labels and texts below, the drive and coil outlines and the moved bubbles are hand edits. All
values ASSUMED unless a source is named.
- **Valve tags (S4#1).** XV-2033A/2034A, TV-2011A/B, PV-2041A, XV-2043A/2044A, AV-2021A and
  PSV-2046A carry printed tag labels. PCV-2042A is drawn as a field regulator bubble on the N2
  valve with its impulse line from 50-NS-2025A downstream of the valve ("self-acting" note).
  `cheme validate` still reports the valve-tagged instruments (TV, AV, XV, PV) as
  instrument-not-on-pid: it reads instrument tags from bubbles and actuators, not from valve
  labels (a core limit, listed below for the review to judge).
- **Agitator (S4#2).** A-201A is drawn as a top-entry drive on the vessel axis line (x shifted
  8 mm right of the centre so the drive clears the head SIP line): motor M (catalogue
  MOTOR_SHAPE, 160 kW installed for the 127 kW of D-012), gearbox G, shaft through the top head,
  double mechanical seal S with a sterile barrier fluid above headspace pressure (D-016), and the
  impeller symbol in the broth. The drive is drawing only (no separate motor tag; the motor list
  comes with electrical-list.yaml).
- **Coils (S4#3).** The half-pipe coils of D-017 are drawn as an outline outside the straight
  shell; 150-TW-2022A/2023A connect to them, not to the broth.
- **I-204 and the loop during SIP (S4#4).** During SIP P-201A is stopped and TV-2011A/B are
  closed (sequence step, S9); the stagnant loop water is warmed by the shell. I-204 (PALL-2043A)
  now also stops P-201A, so the about 10 m3 of loop water cannot be circulated through the coils
  of a steamed vessel, and stops the CIP supply pumps P-221A/B (one fermenter is cleaned at a
  time, D-021), so no cold CIP spray enters a steamed vessel. Cold medium stays covered by
  XV-2034A. Rejected: a trip valve in the CIP supply steam block (another actuated valve on every
  fermenter for a case the pump stop covers).
- **Relief load (S4#5).** PSE-2045A is checked against the full-open SIP paths, not the normal
  3 t/h: from the LP header at 4.5 bar(a) (design basis) into the vessel at 3.75 bar(a)
  relieving, 100-SS-2020A and 80-SS-2021A with K = 10 each (take-off, steam filter, valves,
  bends) pass about 2.5 kg/s (9 t/h). The DN 150 disc to atmosphere is choked at about
  360 kg/(m2 s) with Kd 0.62, 6.7 kg/s, 2.7 times that load: DN 150 stays, no restriction orifice.
  Burst indicator XA-2045A (alarm) on the disc, so a burst disc does not open the sterile vessel
  unnoticed. The same check for the seed vessels (S3#1) is left to S9.
- **TIC-2011A (S4#6), PSV-2046A (S4#7).** TIC-2011A sits right of the loop riser with a straight
  measuring line from the broth; its outputs are labelled "TV-2011A: 50-100 % (CW)" and
  "TV-2011B: 0-50 % (LP steam)" and cross the riser once each (accepted in checks.yaml).
  PSV-2046A is tagged and labelled "vacuum relief -0.2 barg".
- **Turnaround (S4#8).** process/recipe.yaml now follows D-031's steps and keeps the 12 h of
  D-003 with two overlaps: the CIP pre-rinse starts in the last 0.25 h of the harvest drain
  (CIP 1.25 h after the harvest's 4.0 h), and the fill starts in the last 0.25 h of the SIP
  cool-down once the vessel is under N2 above +0.1 barg (SIP 2.75 h before the fill's 4.0 h):
  4.0 + 1.25 + 2.75 + 4.0 = 12.0 h. The 1.5 h inoculum transfer of D-030 runs in the last 1.5 h
  of the fill through its own nozzle, so it adds no time. 16 fermenters and the 9.88 h harvest
  period stay. Rejected: a 12.5 h turnaround (0.3 % fewer batches).
- **Crossings on P-201 (S3#6).** The wildcard acceptances in checks.yaml are replaced by the 37
  explicit finding ids.
- Left open: S4#9 (vent filter housing heating), S3#1 to #5, #7 to #10, S2 and S1 lows (to S9).

## D-034 P-202 to the S4b review: full vacuum, set points, LP header relief, legibility (2026-11-26)
Decision (all values ASSUMED unless a source is named):
- **Full vacuum (S4b#2).** R-201A to P are designed for 2.5 barg **and full vacuum** (FV), 150 C,
  as the seed vessels R-211x to R-213x already are (D-013). Reason: steam collapse after SIP can
  draw about 24 000 m3/h (D-031), far above any sterile-filter path, and usual practice for
  steam-sterilised fermenters is an FV rating (no source read). I-204 and the permissives of S9
  stay, but now protect the sterile boundary (filter cartridges, seals, gaskets drawn in) and
  the batch, not the vessel; PSV-2046A covers the loss of N2 during the controlled cool-down.
  Cost: stiffening rings on a 9 m shell; the 100 t empty weight of D-016 is kept until the vessel
  vendor confirms it. D-016's "-0.3 barg, vacuum prevented" is replaced. The seed vessels of
  trains B and C get the class and pressures of train A (R-213B/C 6.0 barg, `Vessel`, S3#3).
- **Overlay set points (S4b#6).** PIC-2041A 0.30 barg on the vent valve; PCV-2042A 0.25 barg
  (lock-up about 0.27 barg), below the PIC set point, so N2 enters only below 0.25 barg and
  leaves only above 0.30 barg: no continuous purge. PCV-2042A senses its outlet at the F-202A
  inlet; at the cool-down peak (1300 m3/h) the filter and line drop about 0.05 to 0.1 bar, so
  the headspace stays at about +0.15 barg, above PALL-2043A (-0.05 barg). In control/loops.yaml.
- **LP header relief (S4b#3).** The LP steam header (4.5 bar(a) = 3.5 barg normal maximum,
  design basis) is protected at the site letdown station by its own relief valve, set at the LP
  header design pressure of 3.5 barg and sized for the letdown valve failed open (utility
  system, ASSUMED; outside this battery limit). A failed letdown therefore raises the header at
  most to 3.5 barg plus 10 % accumulation, 4.85 bar(a): the full-open SIP load into R-201A scales
  with the upstream pressure to about 2.7 kg/s, against the 6.7 kg/s of the DN 150 disc of D-033.
  The fermenter disc (2.5 barg) is below the header's set pressure, as it must be.
- **Valve tags (S4b#1).** The eight actuated valves keep their printed tag labels; validate's
  instrument cross-check reads tags only from bubbles and actuators, so the eight list entries are
  accepted in checks.yaml with this reason, and the PSE-2045A note tag with D-031's.
- **Legibility (S4b#4, #5).** The six small explanatory texts of P-202 are raised from 2.0 to
  2.5 mm; the 100-CS-2016A label moved right of the CIP drop below the head SIP tee, clear of the
  steam block's bleed (its two acceptances removed).

## D-035 P-203, P-206, P-207: fermenters R-201B to P as typicals, headers, harvest and T-201 (2026-11-26)
Decision (ASSUMED unless a source is named; drawn by `scripts/draft_P-203.py`, provenance only,
the XML is the source):
- **Sheets.** The 15 typicals do not fit one A3 sheet legibly (15 columns of about 26 mm with
  five header drops, two filters and a pump each). P-203 draws R-201B to I, the new P-206 R-201J
  to P, the new P-207 the harvest pumps P-202A/B, T-201 with its agitator A-202 and the feed pumps
  P-203A/B. D-023's P-203 is split; the lists' `sheet:` follow. Rejected: one sheet at 26 mm per
  fermenter (labels unreadable at slide size), an A1 sheet (the template is A3).
- **Typical column.** Each fermenter is drawn by one loop body: R-201x with A-201x, branch drops
  from the top headers (inoculum 100-IN-2004, sterile medium 200-SM-2001, CIP supply 100-CS-2015,
  SIP steam 150-SS-2019 teed into the CIP drop as on R-201A, N2 80-NS-2008 through F-202x), the vent
  through F-201x to atmosphere, the tempered-water loop P-201x on the coils, and below the vessel
  the harvest drop to 250-BR-2011 with the CIP return 150-CR-2017 teed off, and the lime branch from
  the ring main 100-ML-1102 to the low shell nozzle. Each branch valve drawn stands for R-201A's
  steam block, and the instruments, trips, sampling, bottom SIP and the TW loop's CW/LP-steam
  injection are "as R-201A" (sheet note), as a typical overview usually does. The 195 branch line
  numbers follow R-201A's with the fermenter's letter (e.g. 200-SM-2002B) and are listed.
- **Headers.** The drops cross the headers below them; a header set common to all fermenters
  cannot be drawn without (each fermenter connects to every header). Those crossings, and only
  those (drop with header, by the Line_Drop_*/Line_Hdr_* ids), are accepted in checks.yaml. Top
  headers end on P-206 at a low-point drain (SIP steam: trap; N2: vent); the harvest header goes to
  P-207, the CIP return to P-204, the ring main into its return leg 100-ML-1103 (P-102).
- **Harvest and hold (D-024).** 250-BR-2011 feeds P-202A (duty) and P-202B (spare), check valves
  on both, 200-BR-2012 with FI-2053 into the top of T-201. T-201 is agitated by A-202 (not sized:
  0.05 to 0.1 kW/m3 for solids suspension, 125 to 250 kW, ASSUMED, vendor to size), insulated, with
  an LP-steam coil on TIC-2052/TV-2052 (50-LS-2054, condensate 25-CD-2055 through a trap) to hold
  at or above 323 K (D-005). 200-BR-2013 to P-203A (variable speed, duty) and P-203B (spare),
  150-BR-2014 heat-traced to S-301A to C (P-301); LIC-2051 sets the feed by P-203A's speed.
- **DN 250.** DEXPI's DIN 2448 list has no DN 250, so the harvest header's nominal diameter is
  printed in its label and listed as DN250, but left out of the model (authoring note).
- Left open: TV-2052 is printed as a valve tag only (not in the instrument list, as the P-202
  valves); the CIP of T-201 and its overflow are not drawn.

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
  ASSUMED 0 and the acid's dilution heat is left out (of the order of 1.6 MW at R-301, D-007).
- L-6: no reactive distillation model: the esterifier is a conversion step and a separator,
  its 98 % assumed; no kinetic or equilibrium esterification model to check it.
- L-7: component separators carry no duty model (as biodiesel-1 L-4): the evaporators' and
  columns' duties are hand estimates; no heat integration or multiple-effect evaporator model.
- L-8: `cheme process reactor-hazards` screens no batch fermentation (a conversion step without
  MTT or TD24): the adiabatic rise of D-012 is a hand estimate.

## Open inputs
- The steriliser's re-sterilisation steam (about 0.3 MW year average) and water (about 50 m3 per
  campaign) on top of Q17 and S2, for the utilities and the LCI (D-015).
- A dextrose-fed fermentation's yield, titer and productivity (the sources' are for
  lignocellulosic sugars).
- The reactive distillation's conversion and the ester column's conditions from an open source.
- Calcium lactate's solubility at 323 K.
- Whether a gypsum cake wash pays.
- The medium steriliser's conditions (413 K and 120 s ASSUMED, D-015) and the fermenters'
  sterilisation in place, here a hand estimate and a cut-off (D-005); the seed growth time (8 h
  ASSUMED, D-013) and the dosing of a non-sterile milk of lime (D-018).
- R-301's cooling with the acid's heat of dilution and the acidulation's heat (D-007, L-5).
- Whether the ester column's water-free residue stays stable and pumpable at 423 K, or the
  column keeps water in its bottoms (D-008).
- An agitator trip on high temperature or lost cooling of a fermenter (D-012), for the
  safeguarding stage.
