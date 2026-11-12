# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Di-tert-butyl dicarbonate (Boc2O, Boc anhydride) by the one-pot phosgene route, issue
ChemE-as-Code/process-library#160. Concept stage: design basis, batch recipe, balanced BFD/PFD,
thermal screening with a rate sensitivity and a preliminary gate-to-gate LCI. Out of scope here:
P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-06): library `main` at 7f2292c6, which pins cheme-as-code 1.9.0
(314642c): gas evolution and gas dosing in a batch (core ADR 0054), the batch still (0055), the
semi-batch screening's default MTT, MTSR profile and gas release against the vent (0058), the
models' duties at `energy_port` (0059) and recycle tears (0060), on top of the semi-batch and the
recipe of 1.7.0 (core ADRs 0050 to 0053). benzyl-chloroformate-1 (phosgene dosing),
benzyl-bromide-1 (strip, vacuum still with cuts and a recycle tear) and
p-toluenesulfonyl-chloride-1 (the gas release over the cooling profile) are the templates.

Core 1.10.0 (2026-11-06): library `main` at e8edcb4b pins cheme-as-code 1.10.0 (c55e9c7). The
entry moved from hand workarounds onto its vent vapour and vent condenser (core ADR 0062), the
doses' heats of solution, a still's charge heat-up and the vessels of the stills' unit
procedures (ADR 0063); the batch column (ADR 0061) and the vessel metal were checked and not
adopted. D-015 records what changed, the numbers before and after and why; the decisions below
carry the new numbers.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (the patents as Google Patents machine text, through a fetch-and-summarise tool;
no paragraph numbers, so the locator is the part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | EP0256559A2, Mitsubishi Kasei, priority 1986, published 1988 (application refused): process for the preparation of di-tert-butyl dicarbonate, https://patents.google.com/patent/EP0256559A2/en | description: the alkali tert-butyl carbonate from the alkoxide and CO2 (0.5-10, preferably 1-3 mol CO2 per mol, at or below 50 C, preferably -20 to 30 C); phosgene (0.4-5, preferably 0.5-1.5 mol per mol of carbonate) with a tertiary amine (0.005-50, preferably 0.005-5 mol%; triethylamine, DABCO) in an ether, cyclic ether, aromatic, aliphatic or halogenated hydrocarbon (2-100, preferably 4-20 times the carbonate's weight), -20 to 50 C preferred, phosgene added gradually with external cooling (exothermic), 0.5-20 h; Di-BOC forms directly, no tricarbonate isolated; acidic by-products such as tert-butyl chloroformate form in the crude; the alkali chloride removed mainly by washing with water (filtration possible but slow, the mixture is paste-like); a water-miscible solvent swapped for a water-insoluble one before the wash; solvent removed under reduced pressure; distillation at 60-120 (preferably 60-100) C under reduced pressure with a liquid paraffin (bp at least 250 C, mp at most 20 C) at 0.01-10 (preferably 0.03-7) times the product's weight to suppress decomposition. Example 1: 1.5 mol KOtBu, 2060 mL THF, 0.018 mol DABCO, 3 mol CO2 over 3 h at 5 C, 2.25 mol phosgene over 4 h at 5 C, THF swapped for dibutyl ether below 50 C, two 500 mL water washes, MgSO4, distilled at 62-66 C and 0.5 mmHg: 149 g. Examples 6-7: 0.81 mol phosgene. Comparative 1: no amine, scarcely any product. The tables' yields and purities are images, not in the text: not read | read; patent, facts only | D-001, D-004, D-005, D-007, D-008 |
| SRC-2 | US5151542A, Sumitomo Seika, 1991/1992: process for preparing di-tert-butyl dicarbonate, https://patents.google.com/patent/US5151542A/en (family EP0468404A2) | description: Boc2O is thermally unstable; solvent removal at no more than 50 C under reduced pressure (the examples 35-40 C); CO2 bubbled through the alkoxide in a hydrocarbon or ether at -50 to +70 C, 0.5-10 (preferably 1-3) mol per mol; Example 1: 3 mol KOtBu in 3.6 L hexane, 4 mol CO2 at 15-25 C over 2 h, then methanesulfonyl chloride, two 1 L water washes, concentrated at 35-40 C: 285.8 g, 87 %, 99.7 %, mp 22-23 C; Examples 2-26: 71-90 %, 95.6-99.9 %; Comparative Examples 1 and 4 (60-70 C): gas vigorously generated, 11 % and 5 %; conventional high-vacuum distillation called not easy at industrial scale (Comparative Example 5: 56-58 C at 0.5 mmHg, 57.6 %) | read; patent, facts only | D-001 (variant, rejected), D-004, D-006, D-008, D-011 |
| SRC-3 | US6020514A, Tokuyama, 1997-2000 (sodium alkoxide in tert-butanol, CO2 under pressure, p-toluenesulfonyl chloride) | - | not read (named by the route scouting) | lead only (D-001) |
| SRC-4 | Pope, B. M.; Yamamoto, Y.; Tarbell, D. S., Organic Syntheses (1977): di-tert-butyl dicarbonate via the tricarbonate | - | not read (not accessible when checked); named by SRC-2 and SRC-5 | lead only (D-001) |
| SRC-5 | Wikipedia, Di-tert-butyl dicarbonate, https://en.wikipedia.org/wiki/Di-tert-butyl_dicarbonate | infobox: density 0.95 g/cm3, mp 22-24 C, bp 56-57 C at 0.5 mmHg, insoluble in water; decomposes to gaseous products on heating (a blowing agent); with moisture slowly to tert-butanol and CO2, pressure in closed containers (uncited); routes named (the classical phosgene route cited to Organic Syntheses; the sulfonic acid routes uncited); sold neat or as 70 % solutions (uncited); rat LC50 100 mg/m3 over 4 h (a supplier's MSDS) | read; CC BY-SA, facts only | materials, D-008, D-011 |
| SRC-6 | Wikipedia, Potassium chloride, https://en.wikipedia.org/wiki/Potassium_chloride | density 1.984 g/cm3; solubility 27.8 g/100 mL at 0 C, 34.0 at 20 C | read; CC BY-SA, facts only | materials, D-007 |
| SRC-7 | Wikipedia, Potassium tert-butoxide, https://en.wikipedia.org/wiki/Potassium_tert-butoxide | solubility 25 g/100 g in THF, 0.27 in hexane, 2.27 in toluene; made from dry tert-butanol and potassium metal; sold as a solid and in solution | read; CC BY-SA, facts only | D-004, D-005 (a suspension), D-012 (proxy) |
| SRC-8 | PubChem CIDs 90495 (Boc2O), 23665647 (KOtBu), 8058 (n-hexane), 9237 (DABCO) | identity: formula, InChIKey, CAS | read (PUG REST) | registry, materials |
| SRC-9 | Property data of core's environment and the NIST Chemistry WebBook, SRD 69 (https://webbook.nist.gov): Antoine constants of n-hexane (C110543, Willingham et al. 1945), tert-butanol (C75650, Brown et al. 1969), phosgene (C75445, Stull 1947), water (C7732185, Stull 1947); CO2's saturation pressures; the `chemicals` 1.5.2 package (open-source, MIT; the version core pins): its packaged CRC Handbook tables (`miscdata.CRC_organic_data`: densities and boiling points; `heat_capacity.CRC_standard_data`: heat capacities and standard entropies), which chemicals takes from the CRC Handbook of Chemistry and Physics, 2014 edition as chemicals cites it; a licensed book, not read here, its Active Thermochemical Tables 1.112 data (`ATCT_G`: gas formation enthalpies), and the ideal-gas cp/R fits to thermo 0.6.1's HEOS_FIT and WEBBOOK_SHOMATE correlations printed per component; CoolProp 8.0.0 (MIT licence), water's saturation temperature at 350 kPa(a) from its default IAPWS-95 formulation (the LP steam's 412.007 K) | per component in `process/materials.yaml`; the LP steam in `process/flowsheet.yaml` | open-source packages queried and WebBook pages read (2026-11-06); single values, facts only; not open data (library ADR 0037) | materials, the flowsheet's utilities, D-006, D-008, D-009 |
| SRC-10 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (the method of core ADRs 0050, 0058) | method reference, no data taken | D-011 |
| SRC-11 | processes/phosgene-1, chlor-alkali-1, asu-1, benzyl-chloroformate-1, potassium-tert-butoxide-1 (this library) | liquid phosgene at 253 K and 340 kPa(a); caustic soda 50 wt%; gaseous nitrogen; the phosgene evaporator's heat, the degassing still and the scrubber pattern; potassium tert-butoxide powder from potassium and dry tert-butanol (99.47 wt% KOtBu modelled) | library, internal | D-004, D-006, D-007, D-012 |
| SRC-12 | Ullmann's Encyclopedia of Industrial Chemistry (carbonic acid esters) | - | not read (licensed) | nothing taken |

Searched and not found openly (2026-11-06): kinetics or reaction calorimetry of the carbonation
of an alkali tert-butoxide or of the phosgenation of the carbonate; a formation enthalpy of the
carbonate or of Boc2O; a vapour-pressure equation, heat of vaporization, heat of fusion, DSC
onset or TD24 of Boc2O; a plant's specific consumptions; a market volume. The route scouting's
reading of EP0468404A2 (Sumitomo, the family of SRC-2) is not used beyond SRC-2.

## D-001 Route and boundary (2026-11-06)
Decision: the one-pot phosgene route of SRC-1 on a dedicated train (D-013):
- R-101: potassium tert-butoxide suspended in hexane with DABCO at 278 K; CO2 dosed (CARB:
  KOtBu + CO2 -> potassium tert-butyl carbonate), then phosgene gas (PHOS: 2 carbonate + COCl2
  -> Boc2O + CO2 + 2 KCl, the amine-catalysed net reaction; SIDE: the lumped loss to
  tert-butanol, isobutene and CO2, D-005); the CO2 and isobutene that form, and the CO2 that is
  not taken up, leave by the vent; the slurry degassed (DG101);
- V-201: the hexane stripped at 15 and 1 kPa(a) up to 313 K (ST101, ST102) and recycled; the Boc2O
  melt with its KCl washed with warm water and split from the brine (DC201);
- C-301: Boc2O distilled at 0.13 kPa(a) from a liquid-paraffin heel (ST301: forerun and main cut),
  the heel returned to the next batch with a 10 % purge;
- T-401: the vents to a caustic scrubber (phosgene destroyed, a share of the CO2 absorbed), the
  scrubbed gas to the site's thermal oxidiser.
Boundary feeds: potassium tert-butoxide, liquid phosgene (phosgene-1), CO2, hexane make-up,
DABCO, liquid paraffin, caustic soda 50 wt%, process water, electricity, LP steam; returns:
cooling water, chilled water, brine; outputs: distilled Boc2O, wash brine, spent scrubber
liquor, waste solvent and the heel's purge to incineration, the scrubbed vent to the oxidiser.
Reason: the issue names the alkoxide + CO2 + phosgene route; SRC-1 is the most complete open
description of it as one pot, without the tricarbonate that the older Organic Syntheses route
isolates (SRC-4, as SRC-2 and SRC-5 name it; not read) and with a work-up order (wash, solvent
removal, distillation from paraffin). Phosgene-1
exists in the library, so the route links its main reagent. It exercises gas dosing
(`dosing.absorbed`), gas evolution (`batch.vent`), batch stills and recycle tears.
**Solvent: hexane, not the example's THF (ASSUMED).** SRC-1 claims aliphatic hydrocarbons among
its solvents, and SRC-2 carbonates KOtBu in hexane; the readable text of SRC-1 shows only THF
(Examples 2-5 vary the solvent in a table that is an image). THF is water-miscible: the patent
swaps it for dibutyl ether before the wash. In hexane the wash can follow the solvent strip, so
the hexane that is recycled never meets water (D-006) and no swap and no THF recovery are needed.
Its cost: the carbonation and phosgenation run in a suspension (KOtBu 0.27 g/100 g in hexane,
SRC-7), which the one-phase model carries as dissolved (L-11). The rate laws are ASSUMED either way.
Rejected:
- the THF route as in SRC-1's Example 1 with the swap to dibutyl ether (or heptane): a swap in
  core's still is possible, but THF's recovery from the swap's distillate needs a fractionation
  (THF/heptane or THF/DBE) and the recovered THF would carry the wash's water unless the wash
  follows the swap; one more recycle through a column core cannot model (L-4);
- the methanesulfonyl chloride route (SRC-2): phosgene-free, 87-90 % and 99.7 %, no
  distillation, but methanesulfonyl chloride has no library entry yet (#159); a variant;
- the tosyl chloride route (SRC-3, not read) and the tricarbonate route (SRC-4, not read);
- isolating the carbonate (SRC-1 allows it): an extra filtration of a paste.
Lumped, not modelled step by step: the mixed anhydride and the tricarbonate (in PHOS); the
chloroformate path and its decomposition (in SIDE); MgSO4 drying (the water leaves with the
forerun, D-008); the two washes of SRC-1 and SRC-2 (one wash stage, D-007).
Links: potassium tert-butoxide from potassium-tert-butoxide-1 (since issue #418, D-012),
phosgene from phosgene-1, caustic soda from chlor-alkali-1, nitrogen from asu-1. No library
process makes hexane, DABCO, CO2 as a product or the paraffin.

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: 500 t/a distilled Boc2O, 7920 h/a (330 days of 24 h), ASSUMED. Modelled product (S25):
99.98 wt% Boc2O, 0.016 wt% water, 0.004 wt% tert-butanol. **The 99.98 wt% is an upper bound, not
a specification**: di-tert-butyl carbonate, the tricarbonate, the chloroformate and the other
by-products are not modelled (the lumped SIDE makes only tert-butanol and isobutene); SRC-2's
isolated products are 95.6 to 99.9 %, its Example 1 99.7 %. The product specification is an
open input.
Reason: no open market or plant figure was found; Boc2O is a fine-chemical reagent (peptide and
pharmaceutical protection chemistry), a batch product. The LCI is per kg; the batch size follows
from the cycle (D-003).

## D-003 Batch basis, recipe and vessels (2026-11-06)
Decision: one batch makes 655.71 kg of distilled Boc2O (stream S25); the recipe
(`process/recipe.yaml`) has three unit procedures:
- REACT on R-101, one vessel over M101, E101, R101 and DG101 (`units`, core ADR 0057): nitrogen
  purge 0.25 h, charge 1 h, cool 284.52 -> 278.15 K 0.20 h (from the jacket), dose 6.0 h (CO2 2 h,
  then phosgene 4 h) and post-reaction 1.59 h to 0.9999 conversion of the phosgene (both from
  R101's model), degas with a nitrogen sweep 0.85 h (DG101's still), transfer 0.5 h: 10.39 h;
- WORKUP on V-201 over ST101, ST102 and DC201: receive 0.5 h (the slurry heated to its bubble
  point by E-204 as it arrives, D-015), strip at 15 kPa(a) 4.67 h and down to 1 kPa(a) 2.57 h
  (the stills' boil-up times), wash 1 h, settle 1 h, transfer 0.5 h: 10.24 h;
- DISTIL on C-301 over M301 and ST301: receive 0.5 h, evacuate 0.5 h, the forerun held to the
  vacuum pump's capacity 3.35 h (L-6), distil 1.93 h (ST301), purge 0.25 h: 6.53 h.
R-101 is the bottleneck: cycle 10.387 h, 762.5 batches in 7920 h; one batch takes 26.16 h from the
purge to the heel's purge. The flowsheet's flows are the recipe's year averages: 655.71 kg x 762.5
/ 7920 h = 63.13 kg/h of S25 (no `cheme.recipe-basis` finding); the batch size was found by
fixed-point iteration with the feeds scaled to the product (L-13).
R-101: 12.5 m3 (preferred size) as the recipe sizes it from R101's model, 8.81 m3 of slurry at the
end of the dosing (70 % full, D 2.37 m), glass-lined; the jacket (U 300 W/(m2 K), 18.9 m2 at the
charge) on brine 258/263 K checked at the log-mean coolant temperature against the content,
278.15 - (20 - 15) / ln(20 / 15) = 260.77 K: it removes 98.4 kW against the model's peak of
73.8 kW (during the CO2 dosing: the carbonation's heat with the CO2's heat of absorption, which
R101's dose now releases as it dissolves, D-015): 25 % margin ((98.4 - 73.8) / 98.4). (Until core 1.10.0 a hand 1.5 kW
for the dissolved excess CO2 was added to the peak, 75.4 kW; the model puts that heat where it
is released, after the peak, when the alkoxide runs out.)
V-201: 12.5 m3 (preferred size) as the recipe sizes it from what its steps take in (core 1.10.0,
ADR 0063, D-015): 8.73 m3 of degassed slurry (6.41 t) at the materials' liquid molar volumes, 70
% full, D 2.37 m (the hand figure was about 9.3 m3 at 278 K; the same vessel); a forced-circulation
reboiler E-204 (tubular, for the KCl slurry, about 27 m2 at U 600 W/(m2 K)) on hot water 321/316 K
heats the slurry from 278 K to its bubble point at 15 kPa(a) (295.0 K) while V-201 receives it
(62.2 kWh, about 124 kW over the 0.5 h, a 7.7 K approach, D-015) and gives the 100 kW of ST101 even
at its end (312.1 K, 6.4 K below the water's mean 318.5 K: 600 x 27
x 6.4 = 104 kW; 25 m2 would give 96 kW and lengthen the strip's end) and the 25 kW of ST102; the jacket alone wets too little as the pot empties. C-301: 1.6 m3
(preferred size) as the recipe sizes it, 1.02 m3 (64 % full, D 1.19 m): 0.69 t of melt onto the
0.23 t heel; a forced-circulation reboiler E-303
(about 8 m2 at U 600) on hot water 368/363 K: 36 kW at the main cut's end (357.9 K, 7.6 K below the
mean 365.5 K) against ST301's 30 kW. Core sizes no reboiler and checks no heating of a still's
vessel: E-204 and E-303 are sized by hand.
Reason: core ADR 0051 puts the batch basis in one place, so the balance, the LCI per kg and a
later TEA share it; the dosing, reaction, degassing, strip and distillation times come from the
models.

## D-004 Feeds and charge (2026-11-06)
Decision, per mol of potassium tert-butoxide:
- hexane in the charge about 5 kg per kg of the carbonate it makes (7.94 kg per kg of product): the
  lower end of SRC-1's preferred 4-20 times; SRC-2 uses 3.6 L for 3 mol (about 0.79 kg per mol,
  the same order); the recovered hexane S30 (498.8 kg/h, its flow held, D-006) and the make-up S2
  (7.149 kg/h, a little more than the losses, the rest purged: 4.76 kg/h leaves with R-101's
  vent-condenser gases, 1.54 kg/h with the dosing's S9 and 3.22 kg/h with the degassing's S11,
  D-006, D-015, 1.62 kg/h with the stripped melt, 0.77 kg/h with the purge S36);
- DABCO 0.012 mol (SRC-1, Example 1: 0.018 mol on 1.5 mol);
- CO2 1.3 mol (SRC-2, Example 1: 4 mol on 3; SRC-1 prefers 1-3 and uses 2), 85 % of it taken up
  (ASSUMED, `dosing.absorbed`), the rest to the vent;
- phosgene 0.49 mol: SRC-1's Examples 6-7 use 0.54 (0.81 mol on 1.5 mol), Example 1 1.5. A 2 %
  deficit on the net reaction's 0.5 is ASSUMED, so that no phosgene is left in the crude: the
  work-up, the recycled hexane and the wash then meet only traces (DG101 strips what is left);
  the carbonate not converted (about 2 %) leaves with the wash brine. It costs about 2 % of the
  alkoxide.
The feeds are these ratios scaled to 0.6473 kmol/h (72.63 kg/h) of the alkoxide, the alkoxide that
gives 63.131 kg/h of S25 at the model's yield (0.03 % more than on core 1.9.0: R101's vent now
strips a little of the phosgene, D-015). Phosgene from phosgene-1 as liquid at 253 K and 340
kPa(a), evaporated in E-102 to gas at 293 K and 150 kPa(a) (as benzyl-chloroformate-1); CO2 gas
from the site's supply at 298 K; the alkoxide a technical solid (its tert-butanol and KOH, and
the hexane's isomers, are not modelled).

## D-005 Reaction model, kinetics, heats and the yield (2026-11-06)
Decision: R101 is `reactor: semibatch` (core ADR 0050) at 278.15 K, isothermal, the charge S5
(hexane, the alkoxide, DABCO and what the recycle carries), CO2 S8 dosed over 2 h from 0, phosgene
S7 over 4 h from 2 h (SRC-1, Example 1: 3 h and 4 h at 5 C; SRC-2: 2 h of CO2), then the
post-reaction to 0.9999 conversion of the phosgene (1.59 h). `batch.vent` takes the CO2 and the
isobutene as they form (all of it, ASSUMED: CO2 is only sparingly soluble in a hydrocarbon at 278
K); the dosed CO2's untaken 15 % passes to the vent; the phosgene is taken up whole
(`absorbed: 1.0`, ASSUMED: it is very soluble in hexane at 278 K, below its 280.65 K boiling
point). Since core 1.10.0 (ADR 0062, D-015) the vent gas leaves the slurry saturated with its
hexane, tert-butanol and phosgene (`vent.vapour`, Raoult on materials.yaml's NIST lines) and
passes R-101's vent condenser at 263.15 K, whose condensate runs back (`vent.condenser`): S9
carries 1.54 kg/h of hexane (the hand figure was 1.55 kg/h, lumped into DG101's gas S11 until
then) and 0.0082 kg/h of phosgene, 0.085 kg a batch, the phosgene the dissolved dose's partial
pressure puts into the vent gas (D-007). Rate laws, ASSUMED (no open kinetics, searched 2026-11-06):
- CARB second order in the alkoxide and CO2, k 0.05 m3/(kmol s) at 278 K, Ea 40 kJ/mol;
- PHOS and SIDE second order in the carbonate and phosgene, k 0.05 and 0.00376 m3/(kmol s) at
  278 K (93 : 7, so that 7 % of the phosgene goes to SIDE whatever the concentrations), Ea 50
  kJ/mol.
The alkoxide is a suspension (SRC-7): the one-phase model carries it, the carbonate and the KCl
as dissolved, at their crystal volumes and ASSUMED heat capacities (L-11). DABCO is a spectator.
Heats, ASSUMED (no open calorimetry or formation enthalpies, searched 2026-11-06), with the dosed
gases as gases:
- CARB -70 kJ/mol (SRC-1 cools the carbonation to 5 C);
- PHOS -200 kJ/mol of phosgene: phosgene's hydrolysis to CO2 and HCl gas is about -73 kJ/mol
  (formation enthalpies, chemicals 1.5.2), and each HCl taken up by a carboxylate salt to solid
  KCl adds of the order of -60 kJ/mol; SRC-1 doses phosgene slowly with external cooling;
- SIDE -200 kJ/mol, as PHOS.
Since core 1.10.0 (ADR 0063, D-015) the doses carry their heats of absorption (`heat_of_solution`,
ASSUMED: CO2 -15 kJ/mol, the heat of desorption DG101 counts; phosgene -24.8 kJ/mol, minus its heat
of vaporization, an ideal solution) and reactions.yaml writes the three heats on the dissolved
basis: CARB -55, PHOS and SIDE -175.2 kJ/mol, the same totals.
Results (`cheme process reactors`): CARB 0.6473, PHOS 0.2949 and SIDE 0.0222 kmol/h; 0.2949 kmol/h
of Boc2O formed, 91.1 % of the alkoxide in the crude (2 x 0.2949 / 0.6473). After the work-up's
losses (D-007, D-008: 0.30 % to the brine, 0.86 % with the forerun, 0.76 % with the heel's purge)
0.2892 kmol/h of Boc2O is distilled (S25's 63.12 kg/h of Boc2O; S25's 0.2898 kmol/h holds its
water and tert-butanol too): **89.4 % on the alkoxide, 91.2 % on phosgene.**
**The yield against the source.** SRC-1's Example 1 gives 149 g from 1.5 mol of the alkoxide, 91.0
% of the 163.7 g in theory, by mass with its purity not stated in the text (the table is an
image): an upper bound of its yield. The modelled 89.4 % stays below it; the SIDE share (7 %) was
set so (with 5 % the model gave 91.4 %, above the source, and was raised). SRC-2's route (another
coupling reagent) gives 87-90 %. Every feed, waste and utility per kg scales with 1/yield: at
85 % (an ASSUMED lower case) each would be about 5 % higher; not modelled.
**The low accumulation in D-011 is a consequence of the assumed rate laws** and must be confirmed
by reaction calorimetry with gas measurement before basic engineering.

## D-006 Degassing, the hexane strips and the recycle (2026-11-06)
Decision:
- DG101 (in R-101): a still at constant relative volatility (as benzyl-chloroformate-1's T101)
  at 30 kPa(a) and 278 K with a **nitrogen sweep**, its gas drawn through R-101's vent condenser on
  brine (gas out at 263 K) by the dry screw pump K-101 (about 300 m3/h at 30 kPa(a), 7.5 kW) to
  the vent header. **Why a sweep:** at 278 K the slurry's own vapour pressure is hexane's 0.84 x
  7.85 kPa = 6.6 kPa plus CO2's x_CO2 x 3970 kPa (materials.yaml's lines), so at 30 kPa(a) it boils
  only while x_CO2 is above about 0.006; without a stripping gas most of the dissolved CO2 would
  stay (the 10 ppm end would be out of reach) and flash in V-201 instead. Nitrogen through the dip
  pipe strips the CO2 from 0.006 to 10 ppm(mol) as a stripping gas in equilibrium with the liquid
  (y_CO2 = 132 x_CO2 at 30 kPa(a)): 3.83 kmol of gas a batch leave the pot, 2.27 kmol of it
  nitrogen (63.7 kg, 51.0 Nm3; a per-batch consumable, D-012), the rest CO2 and hexane at its 6.6
  kPa. The vent condenser returns the hexane down to its saturation at 263.15 K and 30 kPa(a)
  (3.45 kPa, 11.5 mol%): 0.387 kmol a batch (3.21 kg/h) passes with the nitrogen and the CO2, the
  rest (0.455 kmol a batch) refluxes. K-101 then moves about 290 m3/h at its suction (3.37 kmol
  over the 0.85 h) and about 100 m3/h at its discharge to T-401.
  **The sweep's hexane is set here, the dosing's vent carries its own (core 1.10.0, D-015).**
  The vent gas S9 of the dosing leaves R-101's vent condenser saturated with hexane at 263.15 K:
  R101's `vent.vapour` and `vent.condenser` give 0.0179 kmol/h, 1.54 kg/h (the hand figure,
  0.0180 kmol/h and 1.55 kg/h, was lumped into DG101's gas until core 1.10.0, L-14; the
  condenser returns 0.019 kmol/h of the 0.037 kmol/h the gas takes off the slurry at 278 K).
  Core's vent and still carry no sweep gas, so DG101's volatilities stand for the pot and the
  vent condenser together, and the CO2's is set (ASSUMED 1070, 720 while it carried the dosing's
  hexane too) so that the gas S11 carries the sweep's hexane: 3.22 kg/h against the 3.21 kg/h
  of saturation (0.2 % more). Phosgene about 11 x 14 (its vapour-pressure ratio to hexane's at 278 and
  263 K, chemicals 1.5.2, SRC-9), ASSUMED 150; tert-butanol 0.1; the salts, Boc2O and DABCO
  non-volatile. It ends when CO2 is 10 ppm(mol) of the slurry (0.85 h at the boil-up of 1.294
  kmol/h of CO2, hexane and traces the sweep sets: 1.094 kmol a batch net of the vent condenser's
  reflux; 1.518 kmol/h while the dosing's vent hexane was lumped in), taking 2.99 kg/h of CO2,
  3.22 kg/h of hexane and 62 % of the phosgene left (S11) to the scrubber. S11 leaves K-101 at about 298 K: with the
  nitrogen, which the flowsheet does not carry as a component, the degassing's gas holds about 11
  mol% hexane at 101.3 kPa(a), below saturation (its dew point 286 K). A discharge condenser on
  K-101 (brine, 263 K, 101.3 kPa(a): 3.4 mol%) would recover about 2.4 kg/h of the hexane: an
  option for basic engineering, not taken here.
- ST101 and ST102 (in V-201): Rayleigh stills on Raoult's law (core ADR 0055) with the NIST
  Antoine constants of hexane, tert-butanol, phosgene and water, Boc2O's ASSUMED line (D-008) and
  CO2's saturation curve extrapolated (traces only), the salts, the carbonate and DABCO
  non-volatile. ST101 at 15 kPa(a) until hexane is 41 mol% of the pot (312.1 K; 295.0 K at the
  start; ST101's model heats the charge from 278.15 K to that bubble point, `still.heat_up`,
  D-015), ST102 at 1 kPa(a) until it is 1.9 mol% (312.7 K): both below the 323 K limit of D-008.
  ST102 stands for the real operation, the pressure falling from 15 to 1 kPa(a) with the pot held
  near 313 K: core's still has one pressure (L-5), so its pot starts at 257 K in the model, which
  the plant does not do. Both ends are a residue key, set to the temperature by hand, because
  the stills' temperature end failed on this charge (L-7). The suspended KCl counts in the liquid's
  mole fractions (L-3), so the model leaves about three times the hexane a 313 K end would.
- The condensates, 440 kg/h and 60 kg/h of hexane with tert-butanol (S13, S15), at 283.15 K
  (ST101's condenser on chilled water at 15 kPa(a), its dew point 291-300 K; ST102's vapour
  through the dry pump K-201 to its discharge condenser), are collected in T-202 (M201, S35).
- SP201: S30, 498.8 kg/h, back to the next charge (its flow held, ASSUMED, the tear's flow), the
  remainder S36, 0.777 kg/h (0.16 % of S35's 499.6 kg/h), purged to the waste solvent: it takes the make-up's excess
  over the losses and bounds what accumulates.
- **The recycle S30 is a tear converged by propagate** (core ADR 0060, Wegstein, 16 iterations,
  worst residual 6e-7 kg/h): its composition (hexane 99.06 wt%, tert-butanol 0.92 wt%, Boc2O
  0.017 wt%, phosgene and CO2 traces) is the loop's fixed point. The tert-butanol SIDE forms
  (1.65 kg/h) returns mostly with the hexane (its volatility at the strips' end is about 0.4 of
  hexane's) and leaves by the wash; it is a spectator in R101 (its reaction with phosgene is
  lumped in SIDE's ASSUMED share).
Reason: the wash after the strip keeps water out of the recycle (water would destroy the
alkoxide in the next charge); the degassing keeps CO2 and phosgene out of it. The strips at up to
313 K follow SRC-1 (THF removed below 50 C) and SRC-2 (no more than 50 C).

## D-007 Wash, phase split and scrubber (2026-11-06)
Decision:
- DC201 (in V-201, scripts/balance.py): the stripped melt S16 (Boc2O with 47.3 kg/h of KCl, the
  unreacted carbonate, DABCO, 1.6 kg/h each of tert-butanol and hexane) and 223.2 kg/h of process
  water heated to 318.15 K (E201; 3.5 kg per kg of product, KCl about 17 wt% in the brine, below
  its 34 g/100 mL solubility, SRC-6) are mixed, settled and split. Split to the brine, ASSUMED: KCl,
  the carbonate, the alkoxide traces, CO2 and phosgene traces 1.0, DABCO 0.95, tert-butanol 0.8,
  Boc2O 0.003 (insoluble, SRC-5; dissolved and entrained), hexane 0; the melt keeps 0.2 wt% water.
  One stage stands for the sources' two washes (SRC-1: 2 x 500 mL for 149 g; SRC-2: 2 x 1 L for
  286 g, about 7 kg/kg; here 3.5 kg/kg, ASSUMED). Both phases leave at 307.46 K: the adiabatic mix
  of S16 at 313.15 K and S18 at 318.15 K at the liquid heat capacities of materials.yaml, less
  the KCl's heat of solution, +17 kJ/mol (endothermic, ASSUMED order): above Boc2O's 296 K melting
  point, which is why the water is warmed. The brine S20 (274.8 kg/h) goes to wastewater
  treatment. Core has no liquid-liquid component separator in propagate (L-4); DC201 lies in no
  recycle.
- S101/X401 (T-401): the vents S9 (263.15 K, past R-101's vent condenser) and S11 mixed at
  272.18 K (M401, ideal-gas heat capacities) to
  a caustic scrubber with 10.35 kg/h of 50 wt% caustic and 40.4 kg/h of make-up water: NPH
  destroys the phosgene (0.9999), NCO takes up 10 % of the CO2 (ASSUMED: a scrubber built for the
  phosgene with a short gas contact; caustic absorbs CO2 well, so a longer contact takes more:
  at 100 % the caustic would be about ten times as much, 1.7 kg of 50 wt% caustic per kg, recorded,
  not modelled), the NaOH about 1.17 times what both take. X401 (scripts/balance.py) splits the scrubbed vent S33
  (28.5 kg/h: CO2, isobutene, 4.76 kg/h of hexane, water vapour to saturation at 303.15 K) from
  the liquor S34 (52.8 kg/h, sodium carbonate with excess NaOH). The vent goes to the site's
  thermal oxidiser. T-401 is sized for about 100 m3/h, K-101's discharge during the degassing
  (D-006); R-101's vent line for 50 m3/h (D-014).
- **The scrubber's phosgene design load in normal operation** is a peak, not the balance's year
  average. Since core 1.10.0 the dissolved phosgene's own partial pressure puts it into the vent
  gas S9 in the balance (R101's `vent.vapour`, D-015): 0.0082 kg/h year average, 0.085 kg a
  batch, which R-101's vent condenser hardly returns (6.2e-6 of the 8.9e-5 kmol/h the gas takes
  off the slurry; phosgene boils at 280.65 K); S28 carries 0.0101 kg/h with what DG101 strips.
  Until core 1.10.0 the slip was not in the balance and was bounded by hand at about 0.4 kg a
  batch; the model's 0.085 kg is below that bound, as it follows the phosgene's accumulation
  over the dosing instead of taking its end value for 4 h. At the end of the phosgene dosing
  the slurry holds 0.0878 kmol a batch of it, x about 0.0014 of the liquid (the suspended salts
  left out); at 278 K and its p* of 89 kPa (materials.yaml's NIST line) that is p 0.12 kPa,
  about 0.12 mol% of the vent gas, about 0.1 kg/h in the about 18 m3/h of CO2 the phosgenation
  then releases. T-401's caustic and its phosgene-destruction efficiency are designed for that
  0.1 kg/h, about 10 times the balance's year average, and for the cooling-failure load of D-011
  (0.11 kg/h at the design rate, 5.5 kg/h at k/100), recorded here with its number (library ADR
  0035).
Reason: SRC-1 washes out the chloride with water; core cannot split two liquids or a gas from a
liquid itself. The scrubber is the phosgene unit's usual last barrier (benzyl-chloroformate-1).

## D-008 Vacuum distillation, the paraffin heel and Boc2O's limits (2026-11-06)
Decision:
- ST301 (in C-301): a Rayleigh still at 0.13 kPa(a) (1 mmHg, between SRC-1's 0.5 and 2 mmHg) on
  Raoult's law, from the washed melt S19 with the recycled heel S22 and the paraffin make-up S21
  (1.913 kg/h; M301, the charge at 321.44 K, the adiabatic mix of the three). Paraffin, DABCO and
  the salts non-volatile. A forerun until tert-butanol is 0.01 mol% of the pot (0.338 kmol a batch:
  hexane, water, tert-butanol and 7.8 mol% Boc2O, 336.3 K at its end), then the main cut until Boc2O
  is 30 mol% of the residue (357.9 K). The main cut is the product S25 (0.998 mole fraction Boc2O).
  The forerun with the hexane purge goes to incineration (S37, 3.40 kg/h); it is not recycled, as
  it carries the water. No column (core 1.10.0's `still.column`, ADR 0061, D-015): SRC-1 distils
  without one, the one-stage still already gives 0.998 of the modelled components (the
  by-products that would set the purity are not modelled, D-002), and a column's pressure drop
  would not leave 0.13 kPa(a) at the pot.
- The heel: SP301 returns 90 % of the residue to the next batch (S22, the tear of the second
  recycle, converged by propagate), 10 % is purged to incineration (S27, 2.45 kg/h). The heel then
  holds 179 kg of paraffin a batch, 0.27 kg per kg of product, within SRC-1's preferred 0.03-7.
  DABCO's 5 % share left in the melt leaves by the purge.
- **Boc2O's vapour pressure** has one open point (56-57 C at 0.5 mmHg, SRC-5); with an ASSUMED heat
  of vaporization of 65 kJ/mol it is a two-constant line, log10(P/bar) = 7.1239 - 3395.4/T. It
  boils at 339 K at 0.13 kPa(a) on this line; SRC-1 distils at 62-66 C at 0.5 mmHg, so the line may
  put the boiling point a few kelvin low (open input: a measured vapour pressure).
- **Temperature limits, from the sources:** Boc2O, its precursors and the crude are held below
  323 K wherever they are held for hours (the reaction at 278 K; the strips end at 312-313 K;
  the wash at 307 K), after SRC-2 (solvent removal at no more than 50 C, vigorous gas at 60-70 C)
  and SRC-1 (THF removed below 50 C); the hot water of V-201 is 321 K, below it. Only the paraffin
  still goes higher: its pot ends at 357.9 K and its water is 368 K, below SRC-1's preferred
  distillation range's 100 C (373 K), which it states with the paraffin present. Boc2O melts at
  22-24 C (SRC-5): the main-cut condenser runs on a tempered loop above 296 K and the product is
  stored at 303 K.
- No reaction runs in a still or the wash: Boc2O's thermal and hydrolytic decomposition has no
  open rate; its loss in the still and the wash is not modelled (L-10). The heel's 0.76 % and the
  forerun's 0.86 % are what the stills distil off or leave.
Reason: SRC-1 distils from a paraffin to limit decomposition; the heel (a usual practice for a
heavy chaser) keeps the Boc2O it holds in the process.

## D-009 Utilities and heat: every energy flow (2026-11-06)
Decision (year averages; Q2, Q17, Q5, Q6, Q7 and Q11 written by `cheme process propagate --fill`
from the models at `energy_port` and the vent condenser's port, core ADRs 0059, 0062, 0063; the
others scripts/balance.py, each with its arithmetic in the flowsheet's source):
- brine 258/263 K (product:BRINE), 33.10 kW, 0.524 kWh/kg: Q1 2.21 kW, the charge cooled from its
  mix at 284.52 K (S1, S2, S3 at 298.15 K and the recovered hexane at 283.15 K) to 278.15 K; Q2
  30.62 kW, R101's model (its reactions on the dissolved basis 25.32 kW: CARB 0.6473 kmol/h x 55
  MJ, PHOS and SIDE 0.3171 kmol/h x 175.2 MJ; the doses' heats of solution 5.16 kW, which hold the
  0.28 kW of the CO2 S10 keeps dissolved, 0.068 kmol/h x 15 kJ/mol, Q3 by hand until core 1.10.0,
  L-9; the doses cooled to 278 K 0.45 kW and the vent gas 0.03 kW; less the vent vapour's
  evaporative cooling 0.32 kW and its condensate warmed back 0.02 kW, D-015); Q17 0.27 kW, R-101's vent
  condenser (R101's model, core ADR 0062: the hexane condensed 0.17, the vapour and the gas cooled
  from 278 to 263 K 0.03 and 0.07 kW; the isobutene's cooling left out, no ideal_gas data, about
  0.01 kW);
- chilled water 278/283 K (product:CHW), 58.39 kW, 0.925 kWh/kg: Q9 50.63 kW (ST101's condensate:
  its latent heat, the model's boil-up in Q6, and the condensate cooled from the still's mean 303.5 K to
  283 K), Q16 7.33 kW (ST102's, after the vacuum pump, its vapour from the pot's 313 K), Q13 0.43 kW (the forerun's, after K-301);
- cooling water 298/308 K (product:CW), 7.79 kW, 0.123 kWh/kg: Q14 6.39 kW (the main cut's latent
  heat and its cooling from the still's mean 347.1 K to 303.15 K, through a tempered loop above Boc2O's melting point),
  Q15 1.40 kW (the scrubber: NPH and NCO's heats, the caustic's dilution at -15 kJ/mol NaOH,
  ASSUMED, less the gas and the liquids brought to 303 K and the water evaporated into the vent);
- LP steam 350 kPa(a) to hot-water circuits (feed:LPS), 76.30 kW, 1.209 kWh/kg: Q4 2.54 kW
  (phosgene evaporated, 100 kJ/(kmol K) x 40 K + 24.8 MJ/kmol); Q5 0.61 kW (DG101's model, the
  desorption heat of CO2 and the latent heat of the hexane its gas S11 carries off, D-006); Q6
  50.95 kW (ST101's model: its boil-up's latent heat 44.96 kW and its charge heated from 278.15 K
  to its bubble point 295.0 K, 5.99 kW, `still.heat_up`, D-015) and Q7 6.20 kW (ST102's model, its
  boil-up's latent heat); Q8 4.08 kW (V-201's sensible heat the stills leave out: the distillates
  from ST101's bubble point to their stills' mean temperatures, the melt from it to 313 K, V-201's steel,
  2000 kJ/K ASSUMED, from the wash's 307.5 K back to 313 K each batch; 10.06 kW with the charge's
  heat-up until core 1.10.0); Q10 5.18 kW (the wash
  water to 318 K); Q11 5.58 kW (ST301's model); Q12 1.16 kW (C-301's sensible heat: the melt and
  the make-up from their temperatures to those their outlets leave at; the heel and C-301's steel
  leave as they came);
- electricity 26.75 kW, 0.424 kWh/kg: R-101's agitator and K-101 6.11, V-201's agitator and K-201
  10.66, C-301's agitator and K-301 6.98, the scrubber's pump and fan 3.0 kW (ASSUMED, each with its
  occupancy in the source, on the recipe's hours and 10.39 h cycle since D-015: 10.5 and 6.6 kW,
  26.21 kW, before, on the 10.43 h cycle's hand hours).
Every energy flow of the batch is in the flowsheet and so in the LCI (library ADR 0035), except
these, each recorded with its number:
- T-202's heat gains: the recovered hexane is charged at 283 K (insulated tank, within the cycle);
  if it warmed to 298 K in storage, Q1 would be 4.72 kW more (498.8 kg/h x 2.27 kJ/(kg K) x 15 K,
  0.075 kWh/kg of brine);
- R-101's vent condenser during DG101: the hexane the sweep takes from the pot and the condenser
  returns, 0.455 kmol a batch, about 0.38 kW each on LP steam and brine (year average); the
  nitrogen's sensible heat is negligible;
- (resolved by core 1.10.0, D-015: the dosing's vent hexane evaporating in the pot and R-101's
  vent condenser during the dosing, a hand 0.16 kW and about 0.3 kW until then, are R101's model
  terms in Q2 and Q17;)
- the vessels' heat losses and gains (R-101 at 278 K, V-201 at up to 313 K, C-301 at up to 358 K,
  insulated): about 1.5 kW in all, ASSUMED order, not counted;
- the vacuum pumps' compression heat: inside their power (P1 to P3), removed by their own cooling;
- the product store's heat tracing above 296 K: outside the plant gate;
- the CO2's evaporation at the supply: part of the CO2 supply (a gap, D-012);
- the heats of solution of the carbonate and DABCO in the wash (0.013 and 0.007 kmol/h): not
  known, not counted (the KCl's is, D-007).

## D-010 Wastes (2026-11-06)
Decision: the wash brine (4.35 kg per kg product: about 17 wt% KCl, 0.5 wt% tert-butanol, DABCO
and the carbonate) and the spent scrubber liquor (0.84 kg per kg: sodium carbonate with excess
NaOH) to wastewater treatment; the waste solvent (the forerun and the hexane purge, 54 g per kg)
and the heel's purge (paraffin with Boc2O and DABCO, 39 g per kg) to incineration; the scrubbed
vent (451 g per kg, mostly CO2, 75 g of it hexane, and the nitrogen) to the thermal oxidiser. Neither KCl nor the solvent of the purges
is recovered.
Reason: SRC-1 and SRC-2 end in a salt solution; KCl recovery or a DABCO recovery is outside this
concept.

## D-011 Thermal screening and the rate sensitivity (2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054, 0058, 0062, 0063) for R101:
- T_p 278.15 K, dT_ad 40.5 K (core's: CARB's on the dissolved basis, the charge's alkoxide, 26.6 K,
  and the doses' heats of solution, 13.9 K, which core 1.10.0 counts in dT_ad and not in the MTSR,
  ADR 0063; 33.8 K on core 1.9.0 with CARB as a gas and no heat of solution, D-015; PHOS's
  `per_reaction` dT_ad is 0 K, as its carbonate forms in the batch, L-1); the whole batch's heat,
  both steps, over the content's heat capacity is about 82 K, the phosgenation's alone about 48 K
  (hand arithmetic: 108.7 MJ and 63.4 MJ per hour of flows over about 1330 kJ/K, the charge with the
  doses' taken-up share; the same totals on the dissolved basis);
- accumulation 10.1 % at 7200 s (core's figure is the first dose's, the CO2, a deliberate excess
  that has no alkoxide left to react with, L-1); the phosgene accumulates at most 2.67 % of its dose
  at the end of its dosing (0.0878 of 3.294 kmol a batch, from core's cooling profile); 0.65 % of the
  alkoxide (0.0435 kmol a batch) is left when the phosgene starts;
- MTSR 279.5 K at core's worst moment (6534 s, CARB in the CO2 dosing); PHOS's own MTSR 279.3 K at the
  end of the phosgene dosing; MTT 333.15 K (`hazard.mtt`, D-014): **MTSR below the MTT**. (279.9 and
  279.5 K on core 1.9.0: the accumulated, dissolved reagents now react at their dissolved-basis
  heats, their heats of absorption having been released and removed as they dissolved, D-015;)
- gas release: core takes it at the highest MTSR (CARB forms no gas: 0 m3/h), since core 1.10.0
  with the liquid's vapour (a vapour share of 0.074 at 279.5 K, no condenser credited); over the
  whole cooling profile (core's `stirred_tank.vent_gas_rate` at each point's MTSR, per batch, as
  the p-toluenesulfonyl-chloride-1 entry, over 1 - Y with Y the vent vapour's share at that MTSR
  on core's basis), the most is 24.5 m3/h at 7367 s (the start of the phosgene dosing; 22.9 m3/h
  of it CO2 and isobutene, Y 0.069), 0.49 of the vent's 50 m3/h (D-014; 23.0 m3/h of CO2 alone,
  0.46, on core 1.9.0);
- no TD24 is known for the slurry, the crude or Boc2O (never estimated): no class
  (`cheme.reactor-hazard-missing`, info). With MTSR below the MTT, core's `criticality()` gives
  class 1 or 2 if the TD24 is at or above the MTSR (1 if it is above the MTT), and class 5 if it is
  below the MTSR; classes 3 and 4 are excluded. The same holds at k/10 and k/100 (MTSR below the
  MTT in each).
Sensitivity (scratch copies with every rate constant of R101 divided by 10 and by 100; nothing
else changed; not committed):

| case | CO2 accumulation at 7200 s (core) | alkoxide left when the phosgene starts | phosgene accumulated at the end of its dosing | MTSR (core's worst moment) | PHOS's MTSR (core) | largest gas over the batch with its vapour, of 50 m3/h (CO2 and isobutene) | most phosgene stripped into that gas | post-reaction | cycle, batches/a |
|---|---|---|---|---|---|---|---|---|---|
| k (design) | 10.1 % | 0.65 % | 2.67 % (0.088 kmol) | 279.5 K | 279.3 K | 24.5 m3/h, 0.49 (22.9) | 0.11 kg/h (y 0.12 %) | 1.59 h | 10.39 h, 762.5 |
| k/10 | 18.4 % | 9.8 % | 9.71 % (0.320 kmol) | 282.5 K | 282.3 K | 26.6 m3/h, 0.53 (24.7) | 0.51 kg/h (y 0.51 %) | 16.2 h | 24.95 h, 317.4 |
| k/100 | 48.1 % | 42.7 % | 36.1 % (1.189 kmol) | 292.0 K | 292.0 K | 52.9 m3/h, 1.06 (45.0) | 5.5 kg/h (y 2.6 %, 1.3 m3/h) | 129.8 h | 138.6 h, 57.1 |

(Rerun 2026-11-06 on core 1.10.0 with R101's vent vapour and condenser and the doses' heats of
solution, D-015, scratch script over core's cooling profile. On core 1.9.0 the table read: MTSR
279.9, 283.7, 294.6 K; PHOS's 279.5, 282.9, 294.4 K at the end of its dosing; 23.0, 25.5, 53.5
m3/h of CO2 alone (0.46, 0.51, 1.07); 0.11, 0.55, 7.3 kg/h of phosgene; post-reaction 1.61, 17.4,
182.5 h. Why they moved: the MTSRs fall because the accumulated reagents are dissolved and react
at their dissolved-basis heats, 55 and 175.2 kJ/mol, not 70 and 200 (their heats of absorption
were released and removed as they dissolved; at k/100 the 1.19 kmol of phosgene then hold about
29 MJ less, about 2 K over the content); the gas grows by the vapour it carries (Y 0.07 to 0.15)
and shrinks with the lower MTSR (the rates at it); the phosgene stripped falls with the MTSR's
vapour pressure (151 kPa at 291.9 K against 165 kPa at 294.4 K) and the smaller accumulation. The
post-reaction is shorter at k/10 and k/100 because the vent now strips phosgene from the slurry
in normal operation (0.18 % and 1.05 % of the dose at k/10 and k/100, 0.026 % at the design rate):
the carbonate's excess at the end grows (0.204 against 0.135 kmol a batch at k/100) and the
second-order tail runs faster; at k/100 the yield falls by about 1 %.) MTT 333.15 K in every case.
Interpretation: the MTSR stays far below the
decomposition limit in every case, because the hexane's heat capacity is large; the risks lie
elsewhere:
- **dissolved phosgene stripped into the gas**: the accumulated phosgene is dissolved, x about
  0.0014 of the liquid at the end of the design case's phosgene dosing, 0.0049 at k/10 and 0.017
  at k/100 (the suspended salts left out), in about 60 kmol of hexane a batch. Its pure boiling
  point (280.65 K) is no limit for the solution: what boils is set by the liquid's bubble pressure
  (hexane 15.3 kPa at 292 K and the dissolved CO2), far below the vessel's. A cooling failure
  releases the phosgene by stripping it into the CO2 the reactions keep forming, at y = x p*(T) /
  P (materials.yaml's NIST line, p* 93 kPa at 279.3 K, 151 kPa at 291.9 K; the hexane's own
  vapour pressure in the gas counted). Over the cooling profile (each point at its MTSR, with its
  gas rate, as the gas release) the most is 0.11 kg/h at the design rate, 0.51 kg/h at k/10 and 5.5
  kg/h (1.3 m3/h) at k/100, at or near the end of the phosgene dosing; it is a toxic load on the
  scrubber. Core 1.10.0's vent vapour carries phosgene in normal operation (D-007) and its
  screening's gas release carries the vapour's volume, but not which component it is (L-2), and
  on core's basis (the suspended salts in the liquid, L-3) the figures are about 10 % lower (0.096
  and 4.9 kg/h); the hand basis is kept. The caustic stays sized for the whole accumulated
  inventory (below), a conservative bound;
- **CO2**: at k/100 the gas a cooling failure releases, with its vapour, is 1.06 times the vent's
  capacity (1.07 on core 1.9.0 for the CO2 alone);
- **unreacted alkoxide when the phosgene starts**: at k/10 and k/100, 10 and 43 % of the alkoxide is
  not yet carbonated; phosgene with the alkoxide gives the chloroformate route (not modelled), so
  the CO2 uptake has to be complete before the phosgene starts (a permissive, D-014);
- the slow post-reaction at k/10 and k/100 makes the cycle impractical, as in the other entries,
  and at k/100 the vent then takes about 1 % of the phosgene to the scrubber in normal operation.
**Water ingress** into R-101 (a leak of the aqueous brine from the jacket through the glass
lining, wet hexane, a wet line or the CO2): water destroys the alkoxide (KOH and tert-butanol, exothermic), hydrolyses
the phosgene to HCl and CO2 (corrosive gas to the vent) and Boc2O to tert-butanol and CO2 (gas,
SRC-5); the recycle is kept dry by the wash's place after the strip (D-006); a water analysis of the
recovered hexane and the CO2's dew point before each batch, and a jacket at a pressure below
the vessel's or a non-aqueous coolant, are open inputs. **Loss of the scrubber** (caustic spent, the
pump or the fan stopped) with phosgene in R-101: the dosing must stop on the scrubber's caustic
strength, flow and level (D-014); the caustic in T-401 must hold at least the phosgene that can
accumulate (0.088 kmol a batch at the design rate: 14 kg of NaOH at 4 mol per mol; 1.19 kmol, 190 kg
at k/100); the thermal oxidiser behind it is no phosgene barrier (it would make HCl and Cl2).
Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of distilled Boc2O from the flowsheet's year averages;
potassium tert-butoxide linked to potassium-tert-butoxide-1, phosgene to phosgene-1 (its liquid
phosgene, a captive supply), caustic soda to chlor-alkali-1, the nitrogen consumable to asu-1's
gaseous nitrogen (`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other
background a gap with the activity it should connect to.
- **Potassium tert-butoxide (linked 2026-11-06, issue #418).** `feed:KOTBU` links the Atlas
  producer potassium-tert-butoxide-1 kg for kg (`lca/mappings.yaml`, `dataset` to its
  `product:KOTBU`), as feed:PHOS links phosgene-1. Grade and unit: this entry's S1 is the
  technical solid, modelled as 100 % KOtBu in kg/h (D-004); that entry's product is the dried
  powder from potassium metal and dry tert-butanol in kg, modelled 99.47 wt% KOtBu, 0.23 wt% KOH
  and 0.30 wt% tert-butanol: the same grade per kg of powder, the link counting that entry's
  burden per kg of powder (its D-014). That entry dries its make-up tert-butanol past the
  azeotrope on a molecular sieve, links the alcohol contained to tert-butanol-1 (TBA contained,
  its product's basis), and keeps potassium metal a gap with its proxy (KCl + Na) recorded, so
  the alkoxide's potassium stays a gap upstream, not here.
- Until then (PR #402 to #418) the alkoxide was a gap: an exchange override links a whole
  exchange to one Atlas product kg for kg and a shared proxy's inputs are background activities
  only, so the stoichiometric proxy's tert-butanol share (0.6606 kg tert-butanol and 0.3484 kg
  potassium per kg, SRC-7) could not link tert-butanol-1, and tert-butanol-1's TBA contained is
  not the dry tert-butanol the alkoxide needs. A potassium tert-butoxide entry whose tert-butanol
  feed links tert-butanol-1 was the way the library chose (issue #418, option 1); proxy inputs
  that name an Atlas product (option 2) stay a broader to-do.
- Hexane, DABCO, CO2 and the liquid paraffin: gaps, no library producer (CO2 is a by-product of
  ammonia or ethylene-oxide plants; none of the library's entries supplies it as a product).
- Wastes: the brine and the scrubber liquor to wastewater treatment, the waste solvent and the heel
  purge to incineration, the vent to the thermal oxidiser: gaps with their routes.
Per batch, not in the flowsheet (core ADR 0053, library ADR 0035): nitrogen 157.5 kg (about 126
Nm3: DG101's sweep 51.0 Nm3, 63.7 kg, D-006; R-101's purge and vacuum break, the phosgene line's
purge, V-201's and C-301's vacuum breaks, the tanks' blankets 75 Nm3, ASSUMED), 0.240 kg per kg;
it leaves with the vent to the oxidiser. No rinse between batches: R-101 and C-301 are kept dry
(the alkoxide and phosgene; the hot heel), and V-201 is washed each batch by the wash the
flowsheet carries.
Per kg Boc2O: potassium tert-butoxide 1.150 kg, phosgene 0.497 kg, CO2 0.587 kg, hexane make-up
0.113 kg, DABCO 0.0138 kg, paraffin 0.030 kg, caustic soda 50 wt% 0.164 kg, water 4.18 kg,
electricity 0.424 kWh, LP steam 1.209 kWh, chilled water 0.925 kWh removed, brine 0.524 kWh
removed, cooling water 0.123 kWh removed; wash brine 4.35 kg, scrubber liquor 0.836 kg, waste
solvent 0.054 kg, heel purge 0.039 kg, vent 0.451 kg (of it 0.349 kg CO2, 0.020 kg isobutene, 0.075
kg hexane: the hexane that saturates R-101's vent-condenser gas in the dosing, R101's vent vapour
since core 1.10.0, and in the degassing, D-006, D-015). Not counted: fugitive phosgene, the tanks'
breathing, the vacuum exhausts' traces, the product store's CO2 (emission_exclusions). The
phosgene the dosing's vent gas strips from the slurry to the scrubber is in the balance since
core 1.10.0 (0.085 kg a batch, destroyed there, D-007).

## D-013 Dedicated train (2026-11-06)
Decision: R-101, V-201, C-301, T-202 and T-401 make only Boc2O, batch after batch: 762.5 batches in
7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, and a shared phosgene unit's other consumers.

## D-014 Core 1.9.0: the vent capacity, the MTT and the design findings (2026-11-06)
Decision:
- **`hazard.vent_capacity: 50` m3/h on R101**, ASSUMED: R-101's vent line sized for about 2.2
  times the recipe's normal peak (T-401 takes about 100 m3/h, K-101's discharge in the degassing,
  D-006), 22.2 m3/h of CO2 with its hexane past the vent condenser at 263 K (`cheme process
  recipe`, core 1.10.0; 22.8 m3/h of CO2 at 278 K before); no vent
  sizing yet (no P&ID). Core's release at its worst moment is 0 (CARB, no gas;
  `cheme.reactor-hazard-vent`, info); the largest over the batch with the liquid's vapour 24.5
  m3/h (0.49), at k/10 26.6 (0.53), at k/100 52.9 m3/h (1.06, D-011; 23.0, 25.5 and 53.5 m3/h of
  CO2 alone on core 1.9.0).
- **`hazard.mtt: 333.15` K**, the technical limit of the mass, not a boiling point: SRC-2's
  Comparative Examples 1 and 4 at 60-70 C evolved gas vigorously and lost the product (11 % and 5 %
  yield): a decomposition observed over a reaction's hours. Core's default would take hexane's
  341.87 K (the dosed phosgene and the vented CO2 left out, ADR 0058). The 333.15 K is no TD24 and
  no estimate of one (none is made).
- **Design findings** (the rates are ASSUMED, so they stand until calorimetry): (1) reaction
  calorimetry with gas measurement for both steps, the TD24 or DSC onset of the slurry, the crude and
  Boc2O; (2) the phosgene dosing interlocked to stop on a high temperature, a loss of cooling, the
  agitator's stop, a high vent flow and a phosgene-accumulation estimate from the heat flow, since
  the screened MTSR assumes the dosing stops at the worst moment and the phosgene a cooling
  failure strips into the vent gas grows with both the accumulation and the temperature (y = x
  p*(T) / P: 0.11 kg/h at the design rate, 5.5 kg/h at k/100, D-011); (3) a permissive: the CO2 uptake complete (no free
  alkoxide) before the phosgene starts; (4) the scrubber's caustic strength, flow and level
  interlocked with the phosgene dosing, and its caustic inventory sized for the phosgene that can
  accumulate (D-011); (5) R-101's relief (a bursting disc to a catch tank and the scrubber) sized for
  the CO2 and phosgene of a runaway by a DIERS method from that calorimetry, not from the normal
  vent; (6) the phosgene enclosure, its gas detection and the emergency neutralisation as the site's
  phosgene unit.
- **Duties from the models (ADR 0059)**: R101, DG101, ST101, ST102 and ST301 name their energy
  stream (`energy_port`), so propagate writes Q2, Q5, Q6, Q7 and Q11 as `calculated`, and R101's
  vent condenser Q17 (core 1.10.0, D-015); what they leave out is on its own stream (Q8, Q9, Q12
  to Q16, D-009; Q3 until core 1.10.0).
- **Tears (ADR 0060)**: the recovered hexane S30 and the paraffin heel S22 (D-006, D-008).
- **`hazard.reactions` not used**: CARB and PHOS each count; CARB sets the MTSR (D-011).
Rejected: a larger vent capacity (nothing yet sizes one; the interlocks and the relief are the
measures); naming phosgene a vent component (core would then vent it as it forms, and none
forms; and the dosed phosgene would no longer be taken up in normal operation; since core 1.10.0
it leaves with the vent's vapour by its partial pressure instead, D-015).

## D-015 Core 1.10.0: vent vapour, heats of solution, the strip's heat-up, the stills' vessels (2026-11-06)
Decision: adopt, on R101, ST101 and the recipe, the core 1.10.0 features that model a step at
least as credibly as the hand value they replace; check the rest and keep the hand value where
the model is less credible. Every number below is from `cheme process propagate`, `reactors`,
`stills`, `recipe`, `reactor-hazards` and the scratch rerun of D-011, before (core 1.10.0 on the
entry as merged, which gives 1.9.0's output) and after.
- **R101's vent carries the slurry's vapour through R-101's vent condenser** (`batch.vent.vapour:
  [HEX, TBA, COCL2]`, `vent.condenser` at 263.15 K back to the vessel, its duty on the new stream
  Q17 to brine; ADR 0062). The reviewed limit (the vent S9 had no hexane; L-14's first part) is resolved: S9
  carries 1.54 kg/h of hexane past the condenser, where the hand figure was 1.55 kg/h (one
  condensable over an inert, G K / (1 - K), agrees with the model's flash to 0.6 %). The gas
  takes 0.037 kmol/h of hexane off the slurry at 278 K and the condenser returns 0.019 kmol/h:
  the vessel's evaporative cooling (0.32 kW) and the condensate's warming back (0.02 kW) are now
  terms of Q2, and the condenser's 0.27 kW is Q17 (hand estimates of 0.16 and about 0.3 kW, not
  counted until now, D-009). DG101 no longer stands for the dosing's vent: its CO2 volatility goes
  from 720 to 1070 and its boil-up from 1.518 to 1.294 kmol/h, so that S11 carries the sweep's 3.22
  kg/h of hexane over the same 0.85 h (the nitrogen sweep sets the time; neither core's still nor
  its vent carries a sweep gas, L-14). The hexane lost to the vents stays 4.76 kg/h (4.79 before),
  so the make-up S2 stands. The vapour also carries phosgene (0.0082 kg/h year average, 0.085 kg a
  batch to the scrubber, which the hand bound put at 0.4 kg, D-007) and so takes 0.026 % of it
  from PHOS: the feeds are scaled up by 0.03 % (S1 72.63 kg/h) to hold 500 t/a; the yields stay
  89.4 % and 91.2 %.
- **The doses' heats of solution** (`dosing.heat_of_solution`, ADR 0063): CO2 -15 kJ/mol (the
  heat of desorption DG101 already counts, ASSUMED) and phosgene -24.8 kJ/mol (minus its heat of
  vaporization, an ideal solution, ASSUMED, as benzyl-chloroformate-1), with CARB, PHOS and SIDE
  rewritten on the dissolved basis (-55 and -175.2 kJ/mol, the same totals; reactions.yaml). The
  hand Q3 (0.283 kW, the absorption heat of the CO2 left dissolved, L-9) goes: R101's term
  `solution` is 5.16 kW, of which the dissolved excess is about 0.28 kW. Brine Q1 + Q2 + Q17 is
  33.10 kW against 33.17 kW for Q1 + Q2 + Q3 before (the vent's evaporative cooling, -0.32 kW, less
  Q17, +0.27 kW). The model's peak cooling duty is 73.8 kW (73.9 before, plus the hand 1.5 kW of
  Q3's peak: 75.4): the model releases the excess CO2's heat after the peak, when the alkoxide is
  used up, so the jacket margin is 25 %, not 24 % (the removable duty's share left over: (98.4 -
  73.8) / 98.4 against (98.6 - 75.4) / 98.6). In the screening, dT_ad becomes 40.5 K (33.8 K:
  the heats of solution, 13.9 K, now count in it, CARB's on the dissolved basis falls to 26.6 K) and
  the MTSR 279.5 K (279.9 K), because accumulated, dissolved reagents no longer release their
  heats of absorption a second time; the k/10 and k/100 cases fall to 282.5 and 292.0 K (D-011).
  This is the physically consistent basis and less conservative than before; the heats are
  ASSUMED either way and the calorimetry of D-014 (1) stays the measure.
- **ST101's charge heat-up** (`still.heat_up`, ADR 0063): the slurry heated from 278.15 K to its
  bubble point at 15 kPa(a), 295.0 K, 5.99 kW year average (62.2 kWh a batch), is in Q6 (50.95 kW);
  Q8 keeps what the still still leaves out, the content's rise while it boils and V-201's steel:
  4.08 kW (10.06 kW with the heat-up, by hand, before; together 55.03 against 55.02 kW). The
  recipe's 0.5 h `receive` now holds that heat-up (E-204 at about 124 kW, 7.7 K approach); before,
  the heat-up had no time at all. ST102 and ST301 get no heat-up: both charges enter above their
  bubble points at their pressures (ST102's 257 K under L-5, ST301's 258.6 K).
- **The stills' vessels sized by the recipe** (a unit procedure holding a still may give a
  `vessel`, ADR 0063; L-12 resolved): V-201 12.5 m3 (8.73 m3, 70 % full; the hand estimate was
  about 9.3 m3 in the same 12.5 m3), C-301 1.6 m3 (1.02 m3, 64 %; hand about 1.0 m3 in 1.6 m3): the
  recipe agrees with the hand sizes. Their reboilers E-204 and E-303 stay hand-sized (no jacket
  check for a still's vessel).
- **The cycle**: the post-reaction shortens from 1.61 to 1.59 h (the phosgene the vent strips
  leaves a little more carbonate), so the batch is iterated again to 655.71 kg (657.28 kg) in a
  10.387 h cycle (10.411 h), 762.5 batches a year (760.7).
- **The power on the recipe's hours** (review of PR #410): P1 to P3 now take their running hours
  from the recipe and the 10.39 h cycle (P2 and P3 still carried the 10.43 h cycle of an earlier
  draft and 7.1 h of strips and 5.1 h of C-301's pump): V-201's agitator at 98.6 % occupancy and
  K-201 over the strips' 7.24 h, 10.66 kW (10.5); C-301's agitator over its 6.53 h and K-301 over
  the forerun and the distillation, 5.28 h, 6.98 kW (6.6); electricity 26.75 kW, 0.424 kWh/kg
  (26.21 kW, 0.415), D-009.
Not adopted, checked on scratch copies:
- **`vessel.metal_heat_capacity` on V-201 and C-301** (L-8 stays for the metal): core's metal
  follows the content from the still's start (its bubble point, or the charge's temperature with
  `heat_up`) to its end each batch. With V-201's 2000 kJ/K it adds 1.81 kW to ST101 (278 to 312
  K) and 2.96 kW to ST102 (from its model's 257 K start, L-5, to 313 K): 4.78 kW, against the 0.30
  kW of the hand value, which heats the steel only from the wash's 307.5 K back to 313 K (V-201
  stays warm between batches, insulated, and its steel never cools to 257 K). For C-301 it would
  heat the steel from the charge's 258.6 K bubble point to 357.9 K each batch, 2.7 kW per 1000
  kJ/K, where the hot heel keeps C-301 near its end temperature and the hand balance counts no
  net metal heat. Both are less credible than the hand values, so neither vessel gives a metal
  heat capacity (L-15). R-101's metal is not given either: the charge is cooled in E101 (Q1) and
  the semi-batch runs at its charge's temperature, so the model would count no metal, and the
  jacket's 0.20 h cool time would grow by the steel's share.
- **`still.condenser_port`** for the one-stage stills: the model's condenser duty is the boil-up's
  latent heat only (44.96 kW for ST101), while the hand Q9, Q13, Q14 and Q16 also cool the
  condensate to 283 K or 303 K, and Q13 and Q16 condense after the vacuum pumps: splitting each
  into a model latent heat and a hand subcooling stream would keep the same arithmetic on two
  streams. Kept by hand.
- **`still.column` and a `purity` end on ST301** (ADR 0061): not adopted, D-008.
- **`batch.heat_up` on R101**: its charge S5 enters at the batch's 278.15 K (E101 cools it), so it
  would add nothing.
- **`vent.henry` for CO2**: no sourced Henry constant of CO2 in the slurry at hand; the formed CO2
  stays vented whole and the dose's absorbed share stays 0.85 (ASSUMED, open input).
Reason: the library's rule for adopting a core feature: a model replaces a hand value only where
it models the step at least as credibly; where it does not (the vessel metal), the difference is
recorded with its numbers.

## Core features used (cheme-as-code 1.9.0 and 1.10.0)

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with two sequential doses (`start`) and a `target` | R101 (CO2, then phosgene) | 0050 |
| `dosing.absorbed`: a dosed gas partly (CO2 0.85) or wholly (phosgene 1.0) taken up | R101 | 0054 |
| `batch.vent` with two components | R101 (CO2, isobutene) | 0054 |
| recipe vent report (peak kmol/s, m3/h, kg per batch) | the vent and the scrubber, D-007, D-014 | 0054 |
| `hazard.mtt` and the screening of a vented semi-batch; the default MTT leaving out the dosed gas and the vent gas (1.9.0) | R101, D-011, D-014 | 0050, 0054, 0058 |
| `per_reaction`, the MTSR profile, the gas release at the MTSR against `hazard.vent_capacity` (1.9.0); `stirred_tank.vent_gas_rate` over the cooling profile | R101, D-011, D-014 | 0058 |
| `still:` at a constant relative volatility, `nonvolatile`, boil-up in kmol/h | DG101 (degassing) | 0055 |
| `still:` on Raoult's law (Antoine `vapour_pressure`, `heat_of_vaporization`), boil-up in kW, `end: residue` | ST101, ST102 | 0055 |
| `still:` with `cuts:` (forerun, main cut) | ST301 | 0055 |
| duties written by the models at `energy_port` (1.9.0): a semi-batch, four stills | Q2, Q5, Q6, Q7, Q11, D-009 | 0059 |
| recycle `tears:` with `convergence: wegstein`, a tear with a held flow | S30 (hexane), S22 (heel) | 0060 |
| recipe `units:` (one vessel over several steps), `distil from:` | R-101 (M101, E101, R101, DG101), V-201 (ST101, ST102, DC201), C-301 (M301, ST301) | 0055, 0057 |
| vessel sizing and jacket check, the `cool` time from the jacket | R-101 | 0052 |
| per-batch LCA consumables | nitrogen | 0053 |
| splitters and mixers in propagate | SP201 (purge), SP301 (heel), M101, M201, M301, M302, M401 | - |

Core 1.10.0 part (D-015):

| feature | where | ADR |
|---|---|---|
| `batch.vent.vapour` (the gas saturated with the liquid's hexane, tert-butanol and phosgene) | R101's vent S9 | 0062 |
| `batch.vent.condenser` at 263.15 K, `returns: vessel`, its duty on its own `energy_port` | R-101's vent condenser, Q17 | 0062 |
| the screening's gas release with the liquid's vapour (`vapour_share`) | R101, D-011, D-014 | 0062 |
| `dosing.heat_of_solution`, the reactions on the dissolved basis; dT_ad with the heats of solution | R101 (CO2, phosgene), Q2, D-011 | 0063 |
| `still.heat_up` (the charge to its bubble point in the still's duty) | ST101, Q6 | 0063 |
| a `vessel` on a unit procedure of stills, sized by the recipe without a jacket check | V-201 (WORKUP), C-301 (DISTIL) | 0063 |

Checked and not used (D-015): `vessel.metal_heat_capacity` (V-201, C-301, R-101), `still.condenser_port`
for the one-stage stills, `still.column` and the `purity` end (ST301, D-008), `batch.heat_up`
(R101), `vent.henry`.

Not used: `crystallizer` and its `spectators`, `dryer:`, `filtration:` (no solid is isolated: the
KCl is washed out); `still.feed` (no solvent swap: the hexane route needs none, D-001);
`hazard.reactions` (D-014).

## Core limits hit (for core issues)

- L-1: the screening's accumulation is the first dosed reactant's (here the CO2, a deliberate
  excess with nothing left to react with: 10.1 %), not the hazardous dose's (the phosgene, 2.7 %);
  `per_reaction` gives PHOS a dT_ad of 0 K, as its reactant (the carbonate) forms in the batch and is
  not in the charge or the doses; and the gas release is taken only at the highest MTSR (CARB's,
  which forms no gas). The phosgene's accumulation and the largest gas release came from the
  cooling profile by a scratch script (D-011). Core could report the accumulation of each dosed
  reactant and the gas release at every point of the cooling profile.
- L-2 (partly resolved by core 1.10.0, D-015): a dosed gas that dissolves sets no MTT in the
  screening, and its share of the gas release is not reported. Since core 1.10.0 the vent's
  vapour carries the dissolved phosgene by its partial pressure in normal operation (0.085 kg a
  batch, D-007) and the gas release at the MTSR carries the vapour's volume; the phosgene a
  cooling failure strips into that gas (y = x p*(T) / P, up to 5.5 kg/h at k/100 over the cooling
  profile, D-011) is still the scratch script's, as is the release away from core's worst
  moment (L-1). Core could report each vapour component's rate in the gas release. `hazard.mtt`
  was set by hand to the decomposition limit.
- L-3: the still counts suspended solids (KCl, the carbonate) and non-volatile components in the
  liquid's mole fractions for Raoult's law. At ST102's end they are 66 % of the pot: the hexane left
  (1.9 mol%) would boil at about 291 K without them (by the same Antoine lines), not at 313 K, so the
  model leaves about three times the hexane a 313 K end would, and the forerun's vacuum load and the
  hexane lost follow. A solid phase should not dilute the liquid.
- L-4: propagate has no liquid-liquid or gas-liquid component separator: the wash's phase split
  DC201 and the scrubbed vent X401 are hand splits in scripts/balance.py (ADR 0027 contract);
  `cheme process extract` (NRTL) has no Boc2O data and is not coupled to propagate.
- L-5: a still has one pressure: the second strip, which falls from 15 to 1 kPa(a) at about 313 K,
  is modelled at 1 kPa(a) from its start, its pot falling to 257 K in the model (below where Boc2O
  would crystallise from the concentrate), which the plant does not do; its vapour volume and
  condensers follow the real ramp by hand.
- L-6: a still has one boil-up for every cut: the forerun, whose vapour does not condense at 0.13
  kPa(a) and is limited by the vacuum pump (97.7 mol/h), takes 3.47 h, not the model's 0.12 h; the
  difference is a hand-timed recipe operation (D-003). Core needs a boil-up per cut, or a vapour
  limit (m3/h at the still's pressure).
- L-7: a still's `end: {temperature}` failed with "the still boils dry before its end" on these
  charges for some temperatures and not for others (ST102: 280 and 320 K solved, 300 and 313.15 K
  failed; ST101 at 313.15 K solved once and failed later on a nearly equal charge), while the same
  still ended at a residue key that it passed at those temperatures. Both strips therefore end at a
  residue key set by hand to about 313 K (D-006). Looks like a stop detection in the integration
  near the bubble point (core issue).
- L-8 (as benzyl-bromide-1 L-6; partly resolved by core 1.10.0, D-015): the still had no
  sensible heat, no condensers and no vessel metal. ST101's charge heat-up to its bubble point is
  now its model's (`still.heat_up`, in Q6); the content's rise while a still boils is still left
  out by core (Q8, Q12 by hand), the condensers are kept by hand because they also subcool the
  condensate (Q9, Q13, Q14, Q16; `still.condenser_port` would carry the latent heat only), and
  the vessel metal is kept by hand (L-15).
- L-9 (as benzyl-chloroformate-1 L-10): **resolved by core 1.10.0** (`dosing.heat_of_solution`,
  ADR 0063, D-015): the CO2 left dissolved was Q3 by hand; it is now in R101's duty Q2.
- L-10: no reaction runs in a still or a separator: Boc2O's thermal and hydrolytic decomposition
  during the strips, the wash and the distillation cannot be modelled (and has no open rate).
- L-11: the semi-batch is one liquid phase: the alkoxide, the carbonate and the KCl are carried as
  dissolved at their crystal volumes, so the concentrations and the rate laws are of a pseudo-liquid
  (as n-bromosuccinimide-1's L-2).
- L-12: **resolved by core 1.10.0** for the vessels (ADR 0063, D-015): the recipe sizes V-201 and
  C-301 from what their steps take in; it still checks no heating of a still's vessel, so the
  reboilers E-204 and E-303 are sized by hand (D-003).
- L-13 (as p-toluenesulfonyl-chloride-1 L-6): propagate does not solve the feeds for a product
  rate, and the batch size and the cycle depend on each other: both iterated by hand (feeds scaled,
  then the fixed point of batch size = rate x cycle).
- L-14 (partly resolved by core 1.10.0, D-015): resolved for the dosing's vent (`vent.vapour`,
  `vent.condenser`, ADR 0062): `batch.vent` carried the vent's named components only, so the hexane that
  saturates the vent gas past R-101's vent condenser (1.55 kg/h by hand) was lumped into DG101's
  gas S11; R101's vent S9 now carries it (1.54 kg/h) and the dissolved phosgene with it. Still
  open: a sweep gas as the vapour's carrier (core's vent carries vapour only on the gas the
  reactions form and a passing dose; DG101's nitrogen sweep is not modelled, so its hexane stays
  set by DG101's ASSUMED CO2 volatility, D-006).
- L-15 (new with core 1.10.0, D-015): a recipe vessel's `metal_heat_capacity` follows the
  content from each model's start temperature: a still's metal from its bubble point (or from the
  charge's temperature with `heat_up`) to its end each batch. A vessel that stays warm between
  batches (V-201 between the wash's 307.5 K and 313 K; C-301 with its hot heel near 358 K) is
  not modelled, and with L-5 ST102's metal would start at its model's 257 K: 4.78 kW for V-201's
  2000 kJ/K against the hand 0.30 kW. Core could take the metal's starting temperature from the
  previous operation or a stated value.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R101: composition, vent, accumulation, MTSR, peak cooling, gas release | done in cheme, kinetics ASSUMED | D-005, D-011, D-014, `cheme process reactors`, `reactor-hazards` |
| degassing, strips, vacuum distillation, both recycles | done in cheme (stills, tears), volatilities partly ASSUMED | D-006, D-008, core ADRs 0055, 0060 |
| duties Q2, Q17, Q5, Q6, Q7, Q11 (with the heats of solution, the vent's vapour and condenser, ST101's heat-up) | done in cheme (the models' duties) | D-009, D-015, core ADRs 0059, 0062, 0063 |
| wash split, vent split, the other duties and mixed temperatures | scripts/balance.py (ADR 0027 contract) | D-007, D-009, L-4, L-8 |
| batch recipe, cycle, basis check, R-101's, V-201's and C-301's vessels, R-101's jacket, vent loads | done in cheme | D-003, D-015, `cheme process recipe` |
| feeds for 500 t/a, the batch size | hand (scaled, iterated) | D-004, L-13 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Open inputs
Kinetics, heats of reaction and gas release (calorimetry of both steps), TD24 or DSC onset of the
slurry, the crude, the melt and Boc2O; the solubility of CO2 and phosgene in the hexane slurry
(the absorbed shares), their heats of solution (ASSUMED -15 and -24.8 kJ/mol, D-015) and a
sourced Henry constant of CO2 in the slurry (for `vent.henry`, D-015); the side share and the by-products (di-tert-butyl carbonate, the
tricarbonate, the chloroformate) and so the product's assay; Boc2O's vapour pressure and heat of
vaporization; the wash's partition (tert-butanol, DABCO, Boc2O) and the melt's water; the CO2
uptake of the scrubber; the product specification; R-101's relief and the phosgene enclosure
(D-014); a potassium metal producer for potassium-tert-butoxide-1's gap (D-012); a TEA
(`operation.batch: {recipe: true}`).
