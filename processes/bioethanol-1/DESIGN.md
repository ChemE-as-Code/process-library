# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Fuel ethanol from corn by the dry-grind process, issue ChemE-as-Code/process-library#468, the
library's entry for the coverage item `bioethanol` (rank 32, variant `corn-dry-mill`). Concept
stage: design basis, balanced BFD/PFD with converged recycles, equipment list and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (cheme-as-code 1.12.0).
Neighbours: `ethanol-1` makes synthetic ethanol by ethylene hydration (its README says
fermentation is not designed there); `bio-ethylene-1` buys hydrated bio-ethanol and dehydrates
it to ethylene. This entry makes the fermentation ethanol under the same registry slug
`ethanol`, so a consumer of bio-ethanol can link to it later (D-003). Templates:
`kraft-pulp-1` (lumped biomass components, biogenic and fossil CO2 apart),
`oxalyl-chloride-1` (structure and depth). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | McAloon, A.; Taylor, F.; Yee, W. (USDA-ARS ERRC); Ibsen, K.; Wooley, R. (NREL) (2000) Determining the Cost of Producing Ethanol from Corn Starch and Lignocellulosic Feedstocks. NREL/TP-580-28893, October 2000, https://docs.nlr.gov/docs/fy01osti/28893.pdf (the NREL document server, now under the NLR host) | p. 2: simplified corn of 70 % starch, 18 % suspended and 12 % dissolved non-fermentables (dry basis), 15 % moisture; yield used 114 gal pure ethanol per dry short ton (2.71 gal/bu), the maximum then 2.74 gal/bu; Table 1: corn composition; pp. 6-7: the dry-mill process (Delta-T's flowsheet): grain cleaning (0.3 % trash), hammer mills, continuous liquefaction at 88 C with alpha-amylase, pH 6 with lime and used caustic, urea for the yeast, backset 15 vol% of the final mash added after liquefaction, cooking at 110 C for 20 min, cooling to 60 C, continuous saccharification with glucoamylase and sulfuric acid at pH 4.4 for 6 h, cooling to 32 C, four continuous cascade fermentors (46 h, below 34 C by external coolers, pH above 3.5, mixed by recirculated off-gas), beer of 9 wt% (12 vol%) ethanol, beer heated and degassed, off-gas water-scrubbed and vented, whole stillage below 0.1 wt% ethanol, rectifier from 45 to 91 wt%, stripper bottoms below 0.1 wt% back to liquefaction, vapour-phase molecular sieves (two beds) to more than 99 wt%, denatured with 5 vol% gasoline, 12 days' storage, whole stillage partly evaporated in three of six effects before the decanter, wet cake 35 wt% solids, thin stillage partly backset, the rest evaporated to a 55 wt% syrup, the rectifier's overhead condensed in the evaporator, gas-fired rotary dryer to 9 wt% moisture, zero liquid discharge, make-up water only for the cooling tower and the CO2 scrubber; p. 10: the enzymes convert essentially all the starch; Table 2: DDG composition, 243.6 short tons a day at 9 % moisture, 6.4 lb per gal of fuel ethanol; Table 3: 633 dry short tons of corn a day, 25 MMgal/a of fuel ethanol (95 vol% ethanol, 5 vol% gasoline), 330 days; p. 19: DDG at $0.045/lb, about 20 % of the sales income; CO2 vented, not sold; Table 8: steam bought at $4.50 per 1000 lb, $0.085 per gal fuel ethanol; natural gas for the DDG dryers at $2.95 per 1000 ft3, $0.038 per gal; p. 24: 2090 kW of power, 53 % solids separation, drying and evaporation, 7 % fermentation, 8 % grain handling; distillation the main steam user | read (PDF text); US government report, facts only | D-001 to D-012 |
| SRC-2 | Humbird, D.; Davis, R.; Tao, L. et al. (2011) Process Design and Economics for Biochemical Conversion of Lignocellulosic Biomass to Ethanol. NREL/TP-5100-47764, https://docs.nlr.gov/docs/fy11osti/47764.pdf | section 3.5.2, pp. 45-46: beer column with solids-tolerant trays at 2 atm overhead, rectifier to 92.5 wt% at a molar reflux ratio of 3.5, vent scrubber recovering 99 % of the vented ethanol, vapour-phase molecular sieve removing 95 % of the water to 99.5 wt% ethanol, regenerate (about 72 wt%) back to the rectifier | read (PDF text); US government report, facts only | D-006, D-007 |
| SRC-3 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment) | formation enthalpies at 298.15 K (`Hfl`, `Hfg`, default methods): ethanol (l) -277.03, glycerol (l) -669.6, acetic acid (l) -483.58, water (l) -285.825 and (g) -241.822, CO2 (g) -393.474, CH4 (g) -74.534 kJ/mol; IAPWS-95 saturation of water at 450 kPa(a): 421.05 K, latent heat 2120.2 kJ/kg; ethanol's liquid density at 288.71 K (60 F): 793.2 kg/m3, latent heat at its boiling point 849.8 kJ/kg | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037) | reactions, D-002, D-005, D-009 |
| SRC-4 | Wikipedia, Glucose, https://en.wikipedia.org/wiki/Glucose | infobox: standard enthalpy of formation of the solid -1271 kJ/mol | read; CC BY-SA, a single fact, secondary, so ASSUMED | reactions (FERM, GLYC) |
| SRC-5 | processes/ethanol-1, bio-ethylene-1, kraft-pulp-1, utility-steam-ng-boiler, utility-cooling-tower (this library) | the synthetic-ethanol entry, the bio-ethanol consumer, the lumped-biomass pattern, the steam and cooling-water utilities | library, internal | D-001, D-003, D-012 |

Searched and not read (2026-11-19): Kwiatkowski et al. (2006), Industrial Crops and Products
23:288-296 (the 40 MMgal/a USDA dry-grind model; publisher's paywall); the USDA 2015 energy
balance report and the 2012 corn ethanol survey of Mueller and Kwik (the servers refused the
download). No open source with amounts of enzymes, yeast, urea, lime or sulfuric acid per
gallon was read: SRC-1 gives only their cost.

## D-001 Route and feedstock (2026-11-19)

Decision: fuel ethanol from **corn by the dry-grind (dry-mill) process** with continuous
fermentation, as SRC-1 describes it: milling, enzymatic liquefaction and saccharification, four
continuous cascade fermentors, beer column, rectifier and stripper, molecular-sieve dehydration,
decanter, evaporator and natural-gas dryer to DDGS.

Reason: the dry mill is the route the coverage item names first (`corn-dry-mill`, market mix)
and SRC-1 is an open report that states the whole flowsheet with its compositions,
temperatures, times, yields and utilities on one basis, from a plant designer's (Delta-T)
flowsheet. That is enough for a balanced Tier 2 flowsheet without inventing the process.
Fermentation is continuous in SRC-1, which suits core's steady-state propagation; no batch
recipe is needed.

Rejected:
- **Sugarcane juice with vinasse** (coverage variant `sugarcane`): the other market route; no
  open source of a whole mill (juice extraction, juice treatment, Melle-Boinot fed-batch
  fermentation with yeast recycle, bagasse CHP, vinasse) on one basis was read in this work. A
  candidate for a second entry.
- **Corn wet milling**: SRC-1 p. 3 gives it about 60 % of the 1999 US ethanol, but it is a
  multi-product refinery (corn oil, gluten feed and meal, starch and syrups) with more capital;
  new plants are dry mills (SRC-1 p. 3).
- **Lignocellulosic ethanol** (variant `lignocellulosic`): SRC-2's design; not at commercial
  scale (SRC-1 p. 4), and pretreatment, enzyme production and a solids boiler would triple the
  flowsheet.
- **Batch fermentation**: common in dry mills, but SRC-1's basis is continuous; a batch recipe
  would add a cycle without changing the year-average balance.
- **Ethylene hydration**: that is `ethanol-1`, fossil.

Assumptions: SRC-1's process of 2000 stands for the route; modern plants extract corn oil from
the syrup and run simultaneous saccharification and fermentation with higher solids, not
represented (open input).

## D-002 Capacity, hours and the corn feed (2026-11-19)

Decision: SRC-1's plant: 633 dry short tons of corn a day (Table 3), 23 927.5 kg/h dry, at 15 wt%
moisture 28 150 kg/h (S1, given); 330 days on stream, 7920 h/a. The anhydrous ethanol follows:
9065.7 kg/h at 99.55 wt%, 71 800 t/a.

Reason: SRC-1's 25 MMgal/a of fuel ethanol (95 vol% ethanol, 5 vol% gasoline) is 23.8 MMgal of
pure ethanol from 633 dry tons a day at 114 gal per dry ton; keeping the source's corn rate keeps
every other number of SRC-1 on its basis. A larger plant (modern dry mills are often 100 MMgal/a
and more) scales the flows, not the design.

## D-003 Product, boundary and registry (2026-11-19)

Decision: the product is anhydrous ethanol, at least 99.5 wt% (modelled 99.55 wt%, the rest
water), undenatured, at the plant gate to storage (S22), registry slug `ethanol`. The
denaturing with 5 vol% gasoline at the load-out (SRC-1 p. 7) and the storage are outside the
boundary. The co-product DDGS has the new registry slug `ddgs`, the corn `corn-grain`.

Reason: the denaturant is a blend, not a process step, and a fossil gasoline input in the
dataset would mix the product's carbon; the anhydrous ethanol is what `bio-ethylene-1` (which
buys hydrated ethanol, 93 wt%) and other consumers would link to. ASTM or EN fuel-ethanol
specifications were not read (licensed); 99.5 wt% is SRC-2's product, SRC-1 says more than 99 wt%.

## D-004 Components (2026-11-19)

Decision: corn as SRC-1's three-part composition, lumped (`process/materials.yaml`): STARCH,
NFS (suspended non-fermentables: fibre, protein, oil) and NFD (dissolved non-fermentables), each
with the nominal formula of an anhydrohexose unit C6H10O5, as `kraft-pulp-1` does for wood;
glucose, ethanol, glycerol, acetic acid, biogenic CO2 (CO2B, from the corn) apart from fossil CO2
(the burner's), methane, oxygen and nitrogen. Yeast, enzymes, urea, lime, sulfuric acid and
caustic are not components (L-3).

Reason: SRC-1's model itself uses the simplified composition (p. 2). The nominal formula keeps
the elements balanced; it misstates the protein's nitrogen and the oil's lower oxygen, which only
matters for the DDGS's elemental composition (L-2).

## D-005 Conversion: hydrolysis and fermentation (2026-11-19)

Decision: conversion reactors (`process/reactions.yaml`):
- R202, starch hydrolysis HYD (STARCH + H2O -> GLC), 0.99 of the starch (ASSUMED: SRC-1 p. 10
  says essentially all of it; 1 % left to the DDGS);
- R301, fermentation FERM (GLC -> 2 ETOH + 2 CO2B) at 0.9502 of the glucose and the by-product
  reaction GLYC (2 GLC + H2O -> 2 GLY + HAC + ETOH + 2 CO2B) at 0.03 (ASSUMED); 1.98 % of the
  glucose is left unfermented to the DDGS.

FERM's conversion is **calibrated** so the anhydrous ethanol is SRC-1's yield: 9025 kg/h of
ethanol in S22 from 23 927.5 kg/h of dry corn is 113.97 gal per dry short ton (US gal of 3.785 L
at 793.2 kg/m3, 60 F, SRC-3), against SRC-1's 114. GLYC is a net bookkeeping reaction that
balances the elements and the yeast's redox (acetate's NADH reoxidised by glycerol formation);
its share is ASSUMED: no open source of the glycerol yield was read; SRC-1 Table 2 counts
glycerol among the DDG's 6 % "other". Heats of reaction from formation enthalpies (SRC-3, the
glucose's from SRC-4, ASSUMED): FERM -70.0 MJ per kmol of glucose, GLYC -58.9 MJ per kmol.

The fermentors' heat, 1917 kW (Q7), is these heats at the extents (97.29 and 1.54 kmol/h), in and
out at 305 K, given by hand: core has no heat capacities of the lumped corn components, so the
conversion step cannot write its duty (L-1). Yeast growth (a few per cent of the sugar) is
lumped into the unfermented glucose (L-3).

Rejected: kinetic fermentation models (Monod, product inhibition): no open parameters for this
plant's yeast were read, and the year-average balance needs only the conversion.

## D-006 Fermentation off-gas, scrubber, beer and water balance (2026-11-19)

Decision:
- V301 (beer well and degasser) takes all the CO2 to the off-gas with the beer's vapours, 2.4 %
  of the ethanol and 0.225 % of the water (ASSUMED: gas saturated at 307 K, about 2.3 and 5.1 kPa
  partial pressure over a 9 wt% beer, with an ethanol activity coefficient of about 4.5,
  ASSUMED). All the CO2 leaving here simplifies SRC-1's degassing of the heated beer.
- A301 (CO2 scrubber) recovers 99 % of the off-gas's ethanol into the scrubber liquor (as SRC-2
  p. 46), which joins the beer to the beer column; the vent keeps 4 % of the water (ASSUMED,
  saturated).
- **Design specification `beer`**: the scrubber's make-up water S12 is solved so the degassed
  beer S11 holds 9 wt% ethanol (SRC-1 p. 7): 9476.0 kg/h. SRC-1's plant discharges no liquid and
  takes make-up water only for the cooling tower and the scrubber, so this make-up closes the
  water balance: the water leaves with the dryer's exhaust and the DDGS.
- **Design specification `backset`**: X502's backset share is solved so the backset is 15 % of
  the mash (S25 per S7, mass): 0.2172 of the thin stillage. SRC-1 says 15 % by volume; by mass
  ASSUMED (similar densities).

Finding: the make-up the zero-discharge balance needs, 9.5 t/h (1.05 kg per kg of ethanol), is
more than a CO2 scrubber needs; in a real plant part of the water enters as the jet cooker's
live steam and as the cleaning-in-place water, which this flowsheet does not carry (the cooking
steam is an energy stream, L-4). The water balance itself is the result, not the split of its
inputs.

## D-007 Distillation and dehydration (2026-11-19)

Decision: specified component recoveries (no rigorous VLE; L-1):
- C401 beer column: 99.5 % of the ethanol and 12.15 % of the water to the overhead vapour,
  which is then 45.3 wt% ethanol (SRC-1: 45 wt%); the whole stillage holds 0.05 wt% ethanol
  (SRC-1: below 0.1 wt%); everything else to the stillage.
- C402 rectifier and stripper: 99.93 % of the ethanol and 9.6 % of the water to the overhead,
  91.2 wt% ethanol (SRC-1: 91 wt%); the stripper bottoms (0.08 wt% ethanol) go back to the slurry
  tank (SRC-1 p. 7).
- D401 molecular sieves: 96.5 % of the water adsorbed (SRC-2: 95 %) and 24.4 % of the ethanol
  to the regenerate, so the regenerate is 72 wt% ethanol (SRC-2: about 72 wt%) and the product
  99.55 wt%; the regenerate back to C402.

Reason: the shares are chosen so each stream has SRC-1's stated composition; they were set by
hand in two passes from the propagated balance (the values are inputs, not fits by a script).
The product's purity follows from the sieve's water share. The reflux, stages and pressures of
the columns are not designed here (SRC-2 gives 2 atm overhead on its beer column and a molar
reflux of 3.5 on its rectifier, for a more dilute beer).

## D-008 Stillage, evaporator, dryer and DDGS (2026-11-19)

Decision:
- S501 decanters: 95 % of the suspended solids and the residual starch to the wet cake, and
  11.3 % of the liquid (all its solutes alike), so the wet cake is 34.7 wt% solids (SRC-1: 35).
- X502 splits the thin stillage: the backset by the specification (D-006), the rest to E501.
- E501 evaporator: 95.5 % of the water, all the ethanol and half the acetic acid (ASSUMED) to
  the condensate, which goes back to the slurry tank; the syrup is 55.3 wt% solids (SRC-1: 55).
- R601 burner and D601 dryer: the natural gas burnt completely with 10 % excess oxygen
  (ASSUMED); its heat (lower heating value, 10.84 MW, Q9) goes to the dryer; core's dryer model
  takes the water, ethanol and acetic acid off to 9 wt% moisture in the DDGS (SRC-1); the flue gas
  joins the dryer's vapour in the exhaust.
- The grain-cleaning trash (0.3 % of the corn, SRC-1 p. 6) is landfilled.

Deviation from SRC-1: SRC-1 evaporates the whole stillage partly in the first three effects
before the decanter; here the decanter takes the whole stillage and the evaporator only the
thin stillage. The balance of solids and water is the same; the evaporator's arrangement is a
basic-engineering choice.

Checks: the dryer evaporates 10.7 t/h with 10.84 MW, 3.6 MJ per kg of water, plausible for a
direct-fired rotary dryer (latent heat about 2.3 MJ/kg plus the exhaust's losses); the DDGS,
8681 kg/h at 9 wt% moisture (0.958 kg per kg of ethanol), is 5.7 % below SRC-1's 243.6 short tons
a day (9208 kg/h): yeast cell mass and the enzymes, urea and lime that go to the DDGS are not
represented (L-3).

## D-009 Utilities and energy (2026-11-19)

Decision:
- **Steam** (SRC-1 Table 8): $0.085 per gallon of fuel ethanol at $4.50 per 1000 lb is 18.89 lb
  per gallon; at 3156.6 gal/h (25 MMgal over 7920 h) 27 045 kg/h, taken as LP steam at 450 kPa(a)
  (ASSUMED) condensing at 2120.2 kJ/kg (SRC-3): 15 928 kW, 1.757 kWh per kg of ethanol. Split
  ASSUMED: 25 % to cooking (Q1 2091 kW to the liquefaction R201 and Q1B 1891 kW to the jet
  cooker R202, by their temperature rises), 75 % (Q2, 11 946 kW) to the beer column, evaporator
  and sieve superheater (SRC-1 p. 24: distillation is the main steam user).
- **Natural gas** (SRC-1 Table 8): $0.038 per gallon at $2.95 per 1000 ft3 is 12.88 ft3 per
  gallon, 40 661 ft3/h at 60 F and 1 atm, 48.60 kmol/h as methane (ASSUMED), 779.7 kg/h (S32),
  10.84 MW lower heating value.
- **Power** (SRC-1 p. 24): 2090 kW by SRC-1's shares, 8 % grain handling (Q3, Z101), 7 %
  fermentation (Q4, R301), 53 % solids separation, evaporation and drying (Q5, S501), the
  remaining 32 % (Q6) put on C401 for the rest of the plant.
- **Cooling water** at 298/308 K (ASSUMED): the fermentors' heat Q7 (1917 kW, D-005) and the
  product condenser Q8 (2160 kW: 9025 kg/h of ethanol vapour at 849.8 kJ/kg, SRC-3, and its water,
  cooled to 308 K, by hand). SRC-1 cools the fermentors with well water; here cooling water.
- The rectifier's overhead is condensed in the evaporator (SRC-1 p. 7): the energy stream Q10
  from C402 to E501 shows the heat transfer without a duty (not quantified, L-4).
- Heat recovery between the mash, the beer and the stillage (SRC-1 p. 7) is not modelled: the
  temperatures are given at the points SRC-1 states, without exchangers between them (L-4).

The steam and natural gas are derived from SRC-1's costs, so they carry the two-digit precision
of its cents per gallon (about 1 %).

## D-010 Recycles and convergence (2026-11-19)

Decision: four recycles converged by cheme at their tears (`tears:`, Wegstein, tolerance
0.001 kg/h absolute, 1e-6 relative): the backset S25, the evaporator condensate S27, the
stripper bottoms S20 and the sieve regenerate S18, with the two design specifications (D-006)
solved together. Every component has an exit: the water and the volatiles through the dryer
and the vent, the solids through the DDGS, the ethanol through the product.

## D-011 Hazards and emissions (2026-11-19)

Reasoned at the concept stage, for the P&ID and HAZOP stage:
- **Ethanol**: a flammable liquid (flash point near ambient temperature, wide flammable range in
  air); the distillation, sieve, product condenser and storage areas are hazardous areas, the
  storage with inerted or floating-roof tanks; the 12 days' storage (SRC-1) is outside the
  boundary but sets the site's inventory.
- **CO2 in the fermentation area**: the fermentors and the beer well release about 8.7 t/h of
  CO2; confined spaces (fermentor entry, the cellar, pits) are an asphyxiation hazard; the vent
  is elevated and the fermentors are entered only after ventilation and gas testing.
- **Grain dust**: the receiving, cleaning and hammer-mill area is a combustible-dust explosion
  hazard (dust collection, explosion venting or suppression, ignition-source control).
- **The dryer**: a fire hazard (DDGS fires in the dryer and in the cooling and storage of hot
  DDGS); the exhaust carries VOC and particulates, which a real plant treats in a thermal
  oxidiser (not modelled; an emission exclusion of the LCA).
- **Natural gas burner**: the usual burner management (purge, flame failure trip).
- **No exothermic batch**: the fermentation is continuous and releases about 1.9 MW, removed by
  external coolers; a cooling failure warms the beer slowly (the yeast slows and dies above
  about 40 C), not a runaway; core's reactor-hazard screening applies to batch and semi-batch
  reactors and is not used.
- **Contamination**: bacterial infection of the fermentors lowers the yield (lactic and acetic
  acid); cleaning-in-place with caustic, not in the flowsheet.

Emissions not estimated (`lca/lca.yaml` `emission_exclusions`): the dryer's other VOC,
particulates, CO and NOx; the fermentation off-gas's trace volatiles (acetaldehyde); the mash
tanks' and the ethanol storage's vents.

## D-012 Preliminary gate-to-gate LCI (2026-11-19)

Decision: `lca/lca.yaml`, functional unit 1 kg of anhydrous ethanol (S22), cradle-to-gate
boundary key with the purchased inputs open. Linked (`lca/mappings.yaml`): the natural gas by
mass (the shared unit proxy, as `kraft-pulp-1`), the LP steam as heat delivered (kWh), the power
to the shared electricity entry; the cooling water links the library's cooling tower by its
registry slug. Gaps: the corn (no library producer; the dominant burden, with its field N2O and
land use), the scrubber's process water (the shared `water` is deionised), the trash's landfill.
Not in the inventory: enzymes, yeast, urea, lime, sulfuric acid, caustic (no amounts in an open
source read; SRC-1 gives their cost, about 4.5 cents a gallon for enzymes and yeast together).

The vent's mash template lists the lumped solids, glucose and glycerol at 0 kg; the shared
`lci/mappings.yaml` records them as declared zeros under `pass_through` (as chlor-alkali-1's), and
the burner's methane (0 kg at complete combustion) is mapped as fossil methane to air.

Carbon: the corn's carbon is biogenic (`carbon_accounting`, the corn, the ethanol, the DDGS and
the trash biogenic), the fermentation CO2 (CO2B, 0.959 kg per kg of ethanol) a biogenic
emission, the dryer's CO2 from natural gas (0.236 kg per kg) fossil. Ethanol and acetic acid in
the exhaust and the vent are biogenic emissions without a GWP factor in the screening method.

Allocation between ethanol and DDGS by the library hierarchy (docs/system-model.md): no
physical relationship (DDGS is a feed, not a fuel), so the WBCSD rule: SRC-1's DDG price and its
20 % share of the income give ethanol a price per kg about 3.8 times the DDGS's, below 5, so mass
allocation: 51.1 % ethanol, 48.9 % DDGS. For comparison (not used): economic at SRC-1's income
split 0.80 / 0.20; the EU's energy allocation for biofuels would need the DDGS's heating value.

The screening result (lca/results.md) counts only what the open profile characterises: the
fossil CO2 of the dryer (0.121 kg CO2-eq per kg after allocation); the steam, the power and the
corn are gaps there, so it is far below a cradle-to-gate footprint.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| starch hydrolysis, fermentation, combustion | done in cheme (conversion reactors), conversions calibrated or ASSUMED | D-005, D-008 |
| separators (degasser, scrubber, columns, sieves, decanter, evaporator) | done in cheme (`recovery:`), shares ASSUMED for SRC-1's compositions | D-006 to D-008 |
| dryer to 9 wt% moisture | done in cheme (dryer model) | D-008 |
| four recycles, two design specifications | done in cheme (tears, specs) | D-006, D-010 |
| steam, natural gas, power | derived from SRC-1 by hand, split ASSUMED | D-009 |
| fermentation heat Q7, product condenser Q8, burner heat Q9 | by hand (heats of reaction, latent heat, LHV) | D-005, D-008, D-009 |
| LCI inventory | done, corn and water gaps | D-012 |

## Core features used (core 1.12.0)

- `reactor: conversion` with the reactions' `conversion` for the hydrolysis, the fermentation
  with its by-products and the burner.
- `recovery:` (ADR 0070) for the degasser, the scrubber, both columns, the sieves, the decanter and
  the evaporator; `split:` for the grain cleaning.
- `dryer:` (ADR 0057) with `residual_moisture` for the DDGS dryer, used here for a continuous
  dryer (its time and vessel terms are not used).
- `tears:` with Wegstein `convergence` (ADR 0060) for four recycles, and `specs:` (ADR 0070)
  varying a feed (the scrubber water, for a component fraction) and a splitter outlet (the
  backset, for a mass ratio).
- `lca.yaml` with `carbon_accounting` (biogenic content of the corn and the products), mass
  allocation, `emission_exclusions`.

## Core limits hit (each a candidate core issue)

- L-1: no property package covers corn mash, stillage, syrup or ethanol-water, and the lumped
  components have no heat capacities: no rigorous VLE for the columns, no enthalpies, so the
  conversion steps cannot write their duties (`cheme.process-duty`: missing liquid heat
  capacities) and the fermentation's and burner's heats are given by hand. The ethanol-water
  azeotrope is therefore a stated composition (91 wt%), not a calculated one.
- L-2: a lumped component has one nominal formula: the corn's protein (nitrogen) and oil cannot
  be represented together with an elemental balance unless each gets its own lumped component.
- L-3: no biomass (yeast cell) growth model with a nitrogen source: yeast growth, urea and the
  enzymes are not in the balance.
- L-4: propagate's pass-through classes include no size-reduction class (`Grinding`,
  `Crushing`): the hammer mill is drawn as `TransportingMaterial`; a heat transfer between two
  steps (the rectifier's overhead into the evaporator) carries no duty unless given; heat
  recovery between process streams is not modelled.
- L-5: the R601 burner's duty to the dryer was not written by propagate (`missing the
  temperature of every stream` although S32, S33 and S34 carry temperatures); it is given as the
  lower heating value.

## Open inputs

- Amounts of enzymes, yeast, urea, lime, sulfuric acid and caustic (an open survey or vendor
  data), and the cleaning-in-place water.
- A modern basis: corn oil extraction, higher-solids fermentation, a larger plant; sugarcane as
  a second entry.
- A rigorous ethanol-water distillation (reflux, stages, the beer column's pressure) and the
  heat integration of SRC-1 (evaporator heated by the rectifier).
- The corn's background (maize grain production) and a process-water entry in the shared LCI
  vocabulary.
