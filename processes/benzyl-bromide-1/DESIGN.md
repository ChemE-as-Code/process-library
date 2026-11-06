# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Benzyl bromide by the light-driven side-chain bromination of toluene, issue
ChemE-as-Code/process-library#139, a batch entry of core#158. Concept stage: design basis,
batch recipe, balanced BFD/PFD, thermal screening with a rate-constant sensitivity and a
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-06): library `main` at b8043f4c (core pin v1.8.0, 4e8fd80); cheme-as-code
1.8.0: `reactor: semibatch` with `batch.vent` (core ADRs 0050, 0054), the batch still `still:`
with `cuts:` (ADR 0055), `process/recipe.yaml` with vessel, jacket, `distil from:` and `units:`
over several steps (ADRs 0051, 0052, 0055, 0057), per-batch LCA consumables (ADR 0053). Library
ADR 0035: one dedicated train, campaigns out of scope (D-013).

Core pin v1.9.0 (2026-11-06, 314642c): the models write the duties of their energy streams
(core ADR 0059), so R101's duty (on Q12, the off-gas vapour's heat to the reflux condenser) and
the stills' boil-up Q7 and Q9 are now `calculated` by `cheme process propagate --fill`, and the
hand still duties, found too low, are replaced (D-009); propagate converges the toluene recycle
at its tear S2 (ADR 0060, D-006); the semi-batch screening gives the MTSR over the batch and the
HBr released at the MTSR, against R-101's off-gas capacity (ADR 0058, D-011, D-014). Requires
cheme-as-code 1.9 (plant.yaml).

Core pin v1.10.0 (2026-11-06, c55e9c7): the forerun and the main cut run through a packed column
on the still (`still.column`, Diwekar's shortcut, core ADR 0061; ST102 split into ST102 and
ST103), the product is 99.85 wt% instead of 98.3 wt% and the yield on the bromine 90.2 %
instead of 88.5 %; R101's vent carries the content's vapour through E-102 as its vent condenser
(`batch.vent.vapour`, `batch.vent.condenser`, ADR 0062), so E-102's duty Q4 is the model's and
the hand streams Q12 and Q13 go; `still.heat_up` (ADR 0063) was tried and not adopted (both
charges enter above their bubble points). Each change and what was compared is D-015. Requires
cheme-as-code 1.10 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; NIST WebBook and PubChem pages).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 3 528 899 A, E. Plander, J. Zahalka, V. Formacek, 1970 (priority CS 1965): Method of brominating the side chain of an alkyl benzene, https://patents.google.com/patent/US3528899A/en | background: side-chain bromination activated by light, heat or peroxides was mainly a laboratory process, because light penetrates the mixture only a short way, the reaction slows as bromine builds up, excess bromine accumulates and the ring is brominated as well. Example I: 0.6 mol bromine added to 0.5 mol toluene at room temperature under X-rays, at a rate that keeps unreacted bromine from leaving with the HBr, the HBr withdrawn; the cut at 190-210 C refined by repeated fractional distillation, about 90 % of theory on toluene. Discussion: the side-chain bromination is a series of successive reactions, the degree of bromination set by the moles of bromine introduced (Example II, xylene: 41 % monobromo- and 46 % dibromoxylene); benzal bromide itself is not named | read; patent, facts only | D-001, D-005, D-010, reactions.yaml (BALBR), benchmarks |
| SRC-2 | NIST Chemistry WebBook, SRD 69: toluene (C108883), bromine (C7726956), benzyl bromide (C100390), benzal bromide (C618315) | Antoine constants (NIST fits: toluene to Willingham et al. 1945, 308.5-384.7 K; bromine to Blair and Ihle 1973, 343-383 K; benzyl bromide to Stull 1947, 305.4-471.7 K); heats of vaporization (toluene 35.4 kJ/mol at 360 K, Rivenq 1975; bromine 29.8 at 358 K, Blair and Ihle; benzyl bromide 48.1 at 355 K, Ashcroft 1976); boiling points (toluene 383.8 +/- 0.2 K; benzyl bromide 471.7 K, Aldrich 1990, and 471 K); formation enthalpies of the liquids (toluene 12.0 kJ/mol, Prosen et al. 1945; benzyl bromide 16 +/- 2, Ashcroft, Carson et al. 1963, with 22 and 30 +/- 14 also listed); benzal bromide: only a reduced-pressure boiling point, 429.2 K at 0.031 bar (Weast and Grasselli 1989); toluene's liquid heat capacity about 157 J/(mol K) at 298 K | read | materials.yaml, reactions.yaml, D-005, D-007 |
| SRC-3 | PubChem CID 7498 (benzyl bromide), CID 24408 (bromine), CID 1140 (toluene) | benzyl bromide: identity (C7H7Br, InChIKey AGEZXYOZHKGVCM-UHFFFAOYSA-N); HSDB methods of manufacturing: toluene brominated under ultraviolet light (citing the Merck Index 2013), toluene bromination or benzyl alcohol with HBr (citing Hawley's 15th ed.), dibenzyl ether with bromine; boiling point 198-201 C, density 1.438 at 20 C, flash point 79-86 C closed cup; a lachrymator; decomposes slowly with water to HBr, attacks most metals when moist releasing heat and HBr, reacts violently with bases, magnesium and strong oxidants; GHS H315, H319, H335. Bromine: GHS H314, H330 (fatal if inhaled), H400. Toluene: flash point 4 C closed cup, lower explosive limit 1.1 vol%, autoignition temperature 480 C | read (PUG REST, PUG View; toluene 2026-11-06); the Merck Index and Hawley's are cited through HSDB, not read | D-001, D-011, registry |
| SRC-4 | The `chemicals` 1.5.2 package (Caleb Bell, MIT licence): its packaged CRC Handbook tables (`CRC_organic_data`, `CRC_inorganic_data` densities and melting points, `CRC_standard_data` heat capacities, formation enthalpies and entropies), its Poling ideal-gas heat capacities (`Cp_data_Poling`) and its critical constants with COSTALD | toluene COSTALD volume at 363 K, 0.1156 m3/kmol; densities: bromine 3102.8, benzyl bromide 1438.0, benzal bromide 1836.5 kg/m3; heat capacities: toluene 157.3, bromine 75.7 J/(mol K) (liquid), HBr 29.1 (gas; Poling's ideal-gas Cp/R polynomial, `Cp_data_Poling`, 29.05 at 263 K to 29.15 at 363 K); HBr (g) formation enthalpy -36.3 kJ/mol and entropy 198.7 J/(mol K) (CRC, `CRC_standard_data`); melting point of bromine 265.95 K | open-source package queried (2026-11-06); single values, facts only (library ADR 0037); the CRC Handbook of Chemistry and Physics (the source of the `CRC_*` tables) and Poling, Prausnitz, O'Connell, The Properties of Gases and Liquids, 5th ed. (the source of `Cp_data_Poling`) not read here | materials.yaml (HBr's `ideal_gas` for the vent condensers), D-005, D-008 |
| SRC-5 | processes/hydrogen-bromide-1 (this library), DESIGN.md D-009 | the integral heat of solution of HBr to 48 wt% acid, -72.0 kJ/mol, ASSUMED there from the infinite-dilution -85.14 kJ/mol (NSRDS-NBS 2) | library, internal | D-008 |
| SRC-6 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and the criticality classes of a semi-batch (method, implemented in core ADRs 0050, 0054) | method reference, no data taken | D-011 |
| SRC-7 | processes/bromine-1, btx-1, asu-1 (this library) | bromine 99.96 wt%; toluene from reformate extraction; gaseous nitrogen | library, internal | D-004, D-012 |
| SRC-8 | Steiner, A.; Kappe, C. O. et al. (2020) Green Chem. 22, 448, doi:10.1039/c9gc03662h (continuous photochemical benzylic bromination with in-situ bromine) | - | abstract seen in the route scouting only; not read, no numbers taken | D-001 (continuous alternative, lead only) |
| SRC-9 | Ullmann's Encyclopedia of Industrial Chemistry, Bromine Compounds | - | not read (licensed) | not used |
| SRC-10 | CoolProp (MIT licence), IAPWS-95 water | saturation temperature of steam at 450 kPa(a): 421.05 K | open package queried (2026-11-06) | LP steam in the flowsheet, D-009 |

Searched and not found openly (2026-11-06): kinetics, quantum yield or calorimetry of the
light-driven bromination of toluene at plant scale; the relative rate of benzyl bromide and
toluene towards bromine atoms at these conditions; a formation enthalpy, vapour-pressure equation
or heat capacity of benzal bromide; a heat capacity of liquid benzyl bromide; a TD24 or DSC onset
of benzyl bromide or of the crude; the solubility of HBr in toluene at 363 K; the heat of
solution of bromine in toluene; a plant's specific consumptions.

## D-001 Route and boundary (2026-11-06)
Decision: bromine dosed into excess toluene under light, the free-radical chain brominating the
side chain to benzyl bromide and, in series, to benzal bromide; the HBr leaving as gas, absorbed
to 48 wt% hydrobromic acid; the crude stripped of its toluene (recycled to the next batch with a
purge) and the benzyl bromide distilled off the benzal bromide under vacuum; one product on a
dedicated train (D-013). Boundary feeds: bromine (bromine-1), toluene make-up (btx-1), process
water, electricity, LP steam, nitrogen (per batch); returns: cooling water, chilled brine;
outputs: distilled benzyl bromide, 48 wt% hydrobromic acid (a co-product, D-012), the still
residue and the toluene purge to hazardous-waste incineration.
Reason: the route PubChem's HSDB names for benzyl bromide (SRC-3), and the one issue #139 asks
for; SRC-1 describes its practice (bromine dosed at the rate it reacts, HBr withdrawn) and its
weak points (light penetration, bromine build-up, ring bromination). Batch is ASSUMED for a
fine-chemical volume; continuous photochemistry exists (SRC-8, not read) and belongs on the
continuous track.
Rejected: benzyl alcohol with hydrobromic acid (SRC-3; would link benzyl-alcohol-1 once on main,
a variant `benzyl-bromide-2`); toluene with HBr and hydrogen peroxide (in-situ bromine, no HBr
co-product); NBS (a laboratory reagent). The HBr oxidised back to bromine on site (half the
bromine recovered) is a variant; here the HBr is sold as acid (D-012).

## D-002 Capacity, product and operating hours (2026-11-06)
Decision: 1000 t/a of distilled benzyl bromide (126.263 kg/h year average), 7920 h/a,
ASSUMED. Product in the model: 99.85 wt% benzyl bromide, 0.11 wt% toluene, 0.04 wt% benzal
bromide (D-007; until core 1.10.0 one stage gave 98.3 wt% with 1.6 wt% benzal bromide).
**The 99.85 wt% is an upper bound**: ring-brominated toluenes (Fe or other
Lewis-acid traces, SRC-1), the dibenzyl and polybenzyl condensation products, dissolved HBr and
water are not modelled.
Reason: no open market or plant figure was used; a thousand tonnes a year is a plausible size
for a dedicated batch train of a fine benzylating agent. The LCI is per kg and does not depend
on the scale; the batch size does (D-003).

## D-003 Batch basis and recipe (2026-11-06; the column's steps under core 1.10.0, 2026-11-06)
Decision: one batch makes 887.3 kg of distilled benzyl bromide (stream S15); the recipe
(`process/recipe.yaml`) has two unit procedures: REACT on R-101 (`units: [E101, R101]`: nitrogen
purge, charge the toluene, heat 0.29 h to 363 K from the jacket, dose 5 h and react 0.24 h to
0.999 conversion of the bromine, both from R101's model, sample, transfer: 7.027 h) and DISTIL on
C-101 (`units: [ST101, ST102, ST103]`: receive, strip 1.13 h from ST101's boil-up, evacuate,
forerun 0.44 h from ST102's and main cut 1.30 h from ST103's, both through the column K-101, cool
and break the vacuum, drain: 4.37 h). R-101 is the bottleneck: cycle time 7.027 h, 1127 batches
in 7920 h; one batch takes 10.9 h from the purge to the residue's drain. The flowsheet's flows
are the year averages of the recipe: 887.3 kg x 1127.0 / 7920 h = 126.27 kg/h of S15; `cheme
process recipe` checks this (no `cheme.recipe-basis` finding). Until core 1.10.0: 889.6 kg,
7.046 h, 1124 batches (the column's forerun returns less benzyl bromide, so the charge is
smaller and warmer: the heat-up and the post-reaction are a little shorter).
Per batch: 2274 kg of charge (2116 kg of toluene, 74 % of it recycled), 917 kg (5.74 kmol) of
bromine dosed, 463 kg of HBr off, 2698 kg (2.80 m3) of crude at the end of the dosing. The recipe
sizes R-101 from R101's model (core ADR 0052, fill fraction 0.8 and H/D 1.2 ASSUMED): a 4 m3
vessel (the R10 preferred size), 70 % full, 1.62 m diameter; its jacket on a tempered-water loop
(U 300 W/(m2 K), the cooling water's mean of 303 K over its 298 K supply and 308 K return,
ASSUMED) removes 160.2 kW at the charge's 8.90 m2 against the model's 10.2 kW peak, to which the
absorbed light adds 6 kW and the agitator 3 kW (D-009). C-101 (4 m3, D-007) is busy 62 % of the
cycle at core's constant boil-up, 80 % with the boil-up its jacket allows as the pot empties
(D-007).

## D-004 Feeds and charge (2026-11-06)
Decision: 4.0 mol of toluene in R-101's charge per mol of bromine dosed (the recycle's toluene
counted), ASSUMED; the bromine scaled by scripts/balance.py for 1000 t/a, the toluene make-up the
rest of the charge's toluene. Bromine 100 % (bromine-1 makes 99.96 wt%; its chlorine would give
benzyl chloride), toluene 100 %, both ASSUMED pure.
Reason: an excess of toluene keeps the benzyl bromide dilute, so the series bromination to benzal
bromide stays low; the excess is recovered by distillation (D-007). At 3 mol per mol (tried in a
scratch copy under core 1.9.0, with the one-stage strip, forerun and purge of D-007 then) the
yield on bromine was 85.0 % against 88.5 % at 4; more toluene means a larger strip and recycle. SRC-1's Example I runs the other way (bromine in
excess, 1.2 mol per mol), with a different initiation.

## D-005 Reactor R-101: semi-batch photoreactor with an HBr vent, rate and heat (2026-11-06)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the toluene charge S4 at 363.15 K, the
bromine S5 (298.15 K) dosed at a constant rate over 5 h, then the post-reaction to 0.999
conversion of the bromine (`batch.target`; 0.24 h from the model), isothermal at 363.15 K and
atmospheric pressure, the lamps on throughout. `batch.vent: {stream: S7, components: [HBR]}`
(core ADR 0054): the HBr leaves the liquid as it forms, all of it (fraction 1, ASSUMED: no open
solubility of HBr in toluene at 363 K found), by the second outlet S7.
Rate laws (reactions.yaml): BNBR first order in toluene and in bromine, k1 = 5.0e-4 m3/(kmol s)
at 363 K; BALBR first order in benzyl bromide and in bromine, k2 = 0.2 k1; Ea 30 kJ/mol for both,
all ASSUMED. **These are effective rates of a light-driven chain** (core limit L-1): the real
rate is set by the photons the bromine absorbs (lamp power, light path, quantum yield), and goes
to nearly nothing in the dark. Since both reactions are first order in bromine, the selectivity
follows from how much bromine is dosed into how much toluene, not from the dosing rate.
The lamps: 20 kW of LED wells at about 420 nm (ASSUMED), 30 % of it emitted as light (6 kW),
all absorbed by the content. At an ASSUMED quantum yield of 20 (mol of bromine reacted per mol
of photons), the 5 h dosing (0.319 mol/s of bromine) needs 4.54 kW of light (285 kJ per mol of
photons at 420 nm): a 32 % margin. k1 is chosen so that the bromine reacts about as fast as it
is dosed (accumulation 1.7 %, D-011), which is what lamps with that margin give; the dosing time
is the photon budget's, not the jacket's. Both the quantum yield and the light share are
unmeasured here: a photoreactor test must give them (SRC-1: light penetrates only a short way).
Temperature: 363 K, ASSUMED, below the toluene's boiling point. Rejected: the reaction at the
toluene's reflux (about 384 K, as issue #139 suggests): there the HBr would carry about 50 mol of
toluene vapour per mol (Raoult: the content's vapour pressure is then nearly 101 kPa), the
temperature would follow the rising bubble point (386 K at the start, 396 K at the end), which
core's isothermal semi-batch cannot follow (L-2), and the MTT would equal the process
temperature. At 363 K the HBr still carries 1.07 mol of organic vapour per mol at the start and
0.66 at the end, 0.87 over the batch (core 1.10.0's vent vapour, D-008), which the reflux
condenser returns, so the batch runs under reflux of its off-gas, not at the boil.
Heat of BNBR: -32.3 kJ/mol with HBr as gas, from the formation enthalpies (SRC-2: benzyl bromide
16, toluene 12.0; SRC-4: HBr -36.3 kJ/mol), the most exothermic of the three NIST values for
benzyl bromide; BALBR ASSUMED the same. Vented whole, HBr needs no liquid data (core ADR 0054).
The third bromination, to benzotribromide, is not modelled: it needs benzal bromide, which is
0.88 mol% of the crude, against 73 mol% toluene and 26 mol% benzyl bromide; with a k3 no larger
than k2 its rate is at most 0.88/26.4 = 0.033 of BALBR's at the end of the batch and less before,
so it would take below 0.2 % of the bromine (0.033 x the 3.6 % that BALBR takes).
Off-gas (`cheme process recipe`): 463 kg (5.72 kmol) of HBr a batch with 26 kg of toluene and 5
kg of bromine past E-102, peak 0.334 mol/s of gas, 29.89 m3/h at E-102's 303.15 K and 101 kPa(a),
0.69 h into the dosing. Until core 1.10.0 the recipe gave the HBr alone at 363 K (34.32 m3/h).
The off-gas system (the vapour line to E-102, E-102, E-103 and A-101) is sized for the largest
gas release of a cooling failure over the batch with the content's vapour, 72.80 m3/h 0.38 h
into the dosing (59.57 m3/h at the worst-accumulation moment that `reactor-hazards` reports),
with a margin: 90 m3/h (D-014).

## D-006 Balance method and property gate (2026-11-06; core 1.10.0, 2026-11-06)
Decision: cheme propagates the charge mixer M101, the heat-up E101, the semi-batch R101 with both
outlets (its vent with the content's vapour past its vent condenser E-102, core ADR 0062, D-008),
the absorber A101, the strip ST101, the forerun ST102 and the main cut ST103 through the column
(D-007), the recycle mixer M201 and the splitter SP201 (98 % to the recycle, `split:`).
Since core 1.9.0 it converges the toluene recycle at its tear stream S2 (`tears:`, ADR 0060):
Wegstein's method from the last fixed point as the guess, in 48 iterations (core 1.10.0), to a
residual of 1e-5 kg/h plus 1e-8 of the flow (`convergence:`, tighter than the balances' because
the loop's gain is near 1: 98 % of the recovered toluene returns); S2 is `calculated` and goes
stale on any change upstream. It also writes the model duties Q4, Q7, Q9, Q10, Q11 and Q14 (ADR
0059, 0061, 0062, D-009).
Under core 1.8.0 S2 was an assumed stream that the script and `cheme process propagate --fill`
brought to its fixed point in 14 passes; at the same feeds the tear gave 273.391 kg/h against
their 273.415 (0.009 % less), under core 1.9.0.
scripts/balance.py gives what core has no model for (library ADR 0027): the bromine S5 and the
toluene make-up S1 that make 1000 t/a at 4 mol per mol (core propagates from the feeds and does
not solve them for a product rate), run in turn with `cheme process propagate --fill` until the
product is within 0.01 % of 1000 t/a and the charge at 4.000 mol per mol; the make-up is the
charge's toluene less the recycle's, the recycle's toluene taken as the splitter's 0.98 of the
stills' share of the crude's toluene plus E-103's condensate, since S2 follows the make-up 49
times as strongly (only 2 % is purged) and a make-up from S2 as given diverges (until core
1.10.0 the recycle was taken as one ratio to the crude, which barely moves once E-103's
condensate joins T-201: corrected, 2026-11-06); E-103, the brine vent condenser after E-102, one
flash of S7 at 268.15 K with the HBr an inert and Raoult over an ideal condensate, as core's vent
condenser does (core's vent has one condenser), giving the gas S9 to the absorber and the
condensate S19 to T-201 and E-103's duty Q5; the absorber water S10; the temperatures that follow
from mixing (S3 from S1 and S2, S17 from S12, S14 and S19, S2 and S18 as S17) or from a bubble
point (S13, the strip's end, and S20, the forerun's, by Raoult as the stills); the duties Q1,
Q2, Q3, Q5, Q6, Q8, Q15, Q16 and the lamps' P1 (D-009), and as a cross-check its own values of
the model duties (Q7 24.0899, Q9 and Q10 5.0481, Q14 and Q11 14.8002 kW, R101's model 2.5204
kW into R-101; propagate and `cheme process reactors` give the same to 1e-4 kW).
It reads the streams propagate wrote and the data of materials.yaml, and follows the
balance-output contract (`scripts/check_balance_scripts.py`: 22 values checked).
Reason: no property package of core covers these liquids (bromine and HBr in aromatics, HBr in
water), so the heats are heat capacities and latent heats in the script.

## D-007 Batch still C-101 with its column K-101: the strip, the forerun and the main cut, the toluene recycle and the product (2026-11-06; the column under core 1.10.0, 2026-11-06)
Decision: one batch still, C-101 (4 m3, glass-lined, LP steam jacket), with a packed column
K-101 on it, three core still steps in it (`still:`, core ADR 0055), all on Raoult's law with the
NIST Antoine constants of toluene, bromine and benzyl bromide (SRC-2) and an ASSUMED line for
benzal bromide (through its one measured point, 429.2 K at 3.1 kPa, with an ASSUMED heat of
vaporization of 55 kJ/mol, so a relative volatility of benzyl bromide to benzal bromide of about
15 at 365 K; 12 at 50 kJ/mol, 19 at 60):
- ST101, the toluene strip at 15 kPa(a), one Rayleigh stage (K-101 bypassed), boil-up 150 kW,
  until toluene is 15 mol% of the pot: 1622 kg of distillate a batch (95.4 mol% toluene, 4.5 mol%
  benzyl bromide), the pot from 335.5 to 373.8 K, 1.13 h;
- ST102, the forerun at 2 kPa(a) through K-101 (`still.column`, core ADR 0061: 5 theoretical
  stages with the still, reflux ratio 2, ASSUMED), boil-up 80 kW, until toluene is 0.2 mol% of
  the pot: 118.1 kg (77 wt% toluene, 23 wt% benzyl bromide), 98.9 % of the pot's toluene and 2.9
  % of its benzyl bromide, the pot from 321.4 to 355.1 K, 0.44 h;
- ST103, the main cut at 2 kPa(a) through K-101 (the same 5 stages, reflux ratio 0.5, ASSUMED),
  boil-up 80 kW, until benzyl bromide is 35 mol% of the residue: 887.3 kg of product (99.85 wt%
  benzyl bromide, 0.11 wt% toluene, 0.04 wt% benzal bromide), 97.9 % of the benzyl bromide the
  forerun leaves in the pot, the pot from 355.1 to 376.8 K, 1.30 h; residue 70.0 kg (65 mol%
  benzal bromide), drained after cooling to 333 K to incineration.
The strip distillate, the forerun and E-103's condensate (D-008) go to T-201 (S17, 1765 kg a
batch) and back to the next charge; 2 % of it is purged (S18, 35 kg a batch, 40 g per kg of
product, ASSUMED) so that what the model does not carry (water, ring-brominated toluenes, the
toluene's own impurities) cannot build up. The purge carries 9.0 wt% benzyl bromide: 0.45 kg/h,
0.36 % of the product.
Reason: the strip is what the still model is for (a one-stage solvent strip, ADR 0055). A single
stage cannot strip deep without boiling up benzyl bromide: stripping to 3 mol% toluene at 30
kPa (tried in a scratch copy under core 1.8.0, at 3 mol of toluene per mol and a 5 % purge) sent
11.7 mol% benzyl bromide into the distillate and the pot to 421 K, above the LP steam less its
approach; the recycled benzyl bromide is brominated again in R-101 (yield on bromine 79.8 %).
Hence the shallow strip at 15 kPa and the forerun at 2 kPa, where the relative volatility of
toluene to benzyl bromide is about 28 (at 330 K) against 17 at the strip's end (374 K, NIST
Antoine). The column takes the forerun and the main cut, where the separation is: at reflux 2
the forerun returns 2.9 % of the pot's benzyl bromide to R-101 instead of the one stage's 304 kg
at 50 mol% (a fifth of the benzyl bromide), so less of it is brominated again to benzal bromide,
and the main cut holds back the benzal bromide (0.6 % of it goes over, against about a quarter at
one stage). **Why the column's 99.85 wt% is adopted over the one stage's 98.3 wt%**: it is the
same still on the same data with the stages and the reflux added; core's shortcut is never purer
than a rigorous column (ADR 0061: within 0.01 of it for a ternary forerun and main cut), and it
reduces to the one stage at no reflux. On scratch copies of this folder (the forerun as designed,
core 1.10.0; 2026-11-06): the main cut at reflux 0 gives 98.54 wt% benzyl bromide with 1.35 wt%
benzal bromide (the one-stage figure; until core 1.10.0 98.3 wt% at the larger forerun); at
reflux 1, 99.88 wt% in 1.74 h of boil-up; at 3 stages 99.43 wt% and at 8 stages 99.87 wt%;
with benzal bromide's heat of vaporization at 50 or 60 kJ/mol 99.81 or 99.87 wt%. The product
is therefore 99.4 to 99.9 wt% over the column's and the data's assumptions, and the toluene
the forerun leaves (0.11 wt%) bounds it from below; the recovery stays at 97.9 to 98.4 %. The
reflux ratios are ASSUMED design choices, not optimised: reflux 0.5 for the main cut costs 50 %
more boil-up than none and the column's condenser takes it (D-009). The recycle is a
batch-to-batch recycle; its year average is the fixed point of D-006.
Not modelled (L-4, L-6, L-9): the column's holdup, its total-reflux start-up, hydraulics,
diameter, packing height and pressure drop (the pot is taken at the top's 2 kPa(a), so the pot's
temperature is a lower bound); a ring-brominated impurity, close-boiling to benzyl bromide;
the crude arrives at 363 K, above its 335 K bubble point at 15 kPa, and the stripped crude at 374
K, above its 321 K bubble point at 2 kPa, so part flashes as the still is evacuated (in the
stills' full energy balance of D-009, not in core's boil-up time nor in the steam Q7, Q9 and Q14
its model writes; `still.heat_up`, core ADR 0063, gives none for a charge above its bubble
point, D-015); the dissolved HBr the crude holds (none in the model, D-005) would leave first,
to the vacuum system; the jacket's area falls as the pot empties, so the constant boil-up is
optimistic; the strip's condenser and the vacuum system are sized by hand.
**The end of the main cut cannot run at 80 kW.** The residue, 70.0 kg (35 mol% benzyl bromide,
65 mol% benzal bromide, about 1.6-1.7 kg/L), is about 0.04 m3 at the end of ST103: it sits well
inside C-101's dished bottom (about 0.42 m3 for a DIN 28011 end of 1.62 m), the jacket is wetted
on about 0.95 m2 only, and at U 300 W/(m2 K) (ASSUMED, as R-101's) and the steam's 421 K it gives
about 12.7 kW, 16 % of the stated boil-up. scripts/still_jacket.py repeats the three stills
with the boil-up capped at the jacket's duty for the wetted area: ST101 takes 1.37 h instead of
1.13 h (its end, 0.83 m3, at 57 kW against 150 kW), ST102 0.45 h instead of 0.44 h, ST103 2.34 h
instead of 1.30 h, so C-101 is 1.29 h longer a batch. Decision: keep the cut to the 35 mol%
residue in C-101, the end of it at the falling boil-up the jacket allows. C-101 is then busy
5.66 h of the 7.03 h cycle (80 % instead of 62 %), so R-101 stays the bottleneck: the batches a
year, the year-average streams and the duties (energy per batch, not per hour) do not change;
one batch takes about 12.2 h end to end instead of 10.9 h, and the residue is held hot about 1.0
h longer (its TD24 is open, D-011).
Rejected: ending the main cut at a larger heel (at 0.4 m3 the pot still holds more than half of
the benzyl bromide the cut is meant to take, and carrying a hot heel over to the next batch needs the
residue's TD24); a smaller still or receiver for the cut (a second vessel and a transfer for 1.0
h saved on a vessel that is not the bottleneck). The recipe keeps core's constant-boil-up times
(L-6).
Rejected: a specified split for the product (a stated column, the workaround before core
1.10.0); the main cut at the forerun's reflux 2 (99.9 wt% is no grade asked for here, and the
boil-up would double); the strip through the column (at 15 kPa the toluene's separation from
benzyl bromide needs no reflux, and a deeper strip would need the pot above 421 K).

## D-008 Off-gas: reflux condenser, vent condenser and HBr absorption (2026-11-06)
Decision: the HBr leaves R-101 saturated with the content's vapour and passes E-102, a reflux
condenser on cooling water (gas out at 303 K, its condensate back to R-101 by a liquid seal), and
E-103, a vent condenser on brine (gas out at 268 K, its condensate to T-201), and is absorbed in
process water to 48 wt% hydrobromic acid (on HBr and water) in A-101, a falling-film absorber
with a water tail scrubber (a mixer in the model, all HBr absorbed): 71.35 kg/h of water, 138.13
kg/h of acid (1.094 kg per kg of product, 0.522 kg of HBr), the acid at 313 K. Heat of solution
-72.0 kJ/mol (SRC-5, ASSUMED there), less the gas's and the water's warming.
The vapour the HBr carries is core's since 1.10.0 (`batch.vent.vapour` and `condenser`, core ADR
0062; D-015): the gas leaves saturated with the liquid's toluene, bromine, benzyl and benzal
bromide (Raoult over the ideal liquid with the stills' Antoine constants) at each moment of the
semi-batch, 0.87 mol per mol of HBr over the batch (1.07 at the start, 0.66 at the end), and
E-102 is R101's vent condenser at 303.15 K, one flash with the HBr an inert, its condensate
returned to the vessel and its duty written on Q4 (D-009). Past E-102 the gas S7 holds 0.050 mol
of toluene and 0.0054 of bromine per mol of HBr (26 kg of toluene and 5 kg of bromine a batch).
E-103 is the same flash at 268.15 K in scripts/balance.py (core's vent has one condenser): down to
0.0061 mol of toluene and 0.0034 of bromine per mol; its condensate S19, 24.8 kg a batch (7 wt%
bromine), joins the recovered toluene in T-201. What passes E-103, 3.2 kg of toluene and 3.1 kg
of bromine a batch (3.6 and 3.5 g per kg of product), now in the balance, stays in the acid in
the model (0.33 and 0.32 wt%, the acid 47.7 wt% HBr on the whole): an upper bound on the acid's
organics. The toluene would separate as a film on the acid or pass to the tail scrubber, the
bromine dissolves and colours the acid; where each goes is an emission exclusion (lca.yaml
`vent-toluene`), for basic engineering (an organic phase on the acid, a tail-gas adsorber).
**The model's vapour differs from the hand value of core 1.9.0, and why.** By hand, 0.983 mol per
mol at the start and 0.623 at the end of the batch (Raoult on the charge and the crude, 50.2 and
38.9 kPa), 0.803 as their ASSUMED linear mean, E-102's Q4 8.16 kW. The model gives 0.87 and Q4
8.78 kW. Raoult by hand on this charge and crude gives the model's start and end (52.3 and 40.3
kPa: 1.07 and 0.66 mol per mol): the charge holds more toluene (96.1 mol% against 92.1 %) because
the column's forerun returns less benzyl bromide (D-007), and the mean over the batch is weighted
by the HBr as it forms (most of it early, at the larger vapour share), not a linear mean. The hand
Q4 scaled to 0.87 mol per mol is 8.85 kW, 1 % above the model's. The model is adopted: it is the
hand method integrated with the batch, and it closes R-101's and E-102's balance. ADR 0062's
scratch figure for this entry (0.734 mol per mol, Q4 6.97 kW) is not this design's: that copy kept
core 1.9.0's feeds, so the toluene the vent now carried off was not made up and its charge fell
to 2.86 mol of toluene per mol of bromine (repeated on a scratch copy, 2026-11-06).
Reason: the acid is the saleable form of half the bromine (D-012); 48 wt% is hydrogen-bromide-1's
product grade. The brine stage is needed because 5 mol% of toluene in the HBr would otherwise
reach the acid (26 kg a batch). The vent gas stays at 268 K, above bromine's melting point of
266 K (SRC-4); the bromine in the condensate is a dilute solution in toluene and does not freeze.
E-103's condensate goes to T-201, not to R-101: it is recovered toluene like the strip's, and
core's vent condenser returns one condensate only.
Not modelled: HBr dissolved in the condensates and the crude (ADR 0062's vent gases do not
dissolve; no Henry constant of HBr in toluene at hand, so `vent.henry` is not used); the acid's
organic carbon.

## D-009 Utilities and heat: every energy flow (2026-11-06; the model duties and the stills' balance under core 1.9.0, the column's and the vent condenser's duties under core 1.10.0, 2026-11-06)
Decision (scripts/balance.py and core's models, year averages, kW; per kg of product in kWh; all
ASSUMED unless sourced):
- Q1 10.49 (0.083) of LP steam 450 kPa(a) to R-101's jacket: the charge S3 from its mixing
  temperature of 299.9 K (S1 at 298 K, S2 at 300.4 K) to 363.15 K, 10 % losses; 0.29 h from the
  jacket (`cheme process recipe`).
- R-101's heat. Core's semi-batch model (ADR 0059, with the vent's vapour of ADR 0062) holds the
  reactions' 7.30 kW released, the bromine's warming from 298 to 363 K (1.12 kW taken), the
  vapour the HBr carries off (its latent heat, 6.98 kW taken) and E-102's condensate warmed back
  from 303 K (1.73 kW taken): its duty is 2.52 kW **into** the content, which the light it
  absorbs (4.47) and the agitator (3.0) supply. Q2, R-101's jacket to cooling water through a
  tempered-water loop, takes the rest: 4.47 + 3.0 - 2.52 = 4.95 (0.039), the script's. R101 has
  no `energy_port`: its model's duty runs into the vessel and no energy stream carries it
  (`cheme.process-duty`, info, two heat streams Q2 and Q3); on Q2, which runs out, core would
  refuse it as a flow against the stream's direction. The script repeats the model's terms from
  Q4 and the streams (2.5204 kW, core 2.5202). Until core 1.10.0 the model's duty was the
  reactions' heat less the bromine's warming (6.24 kW out) on Q12 to E-102, the vapour's rest on
  Q13 (2.01 kW, the script's), and Q2 was 5.46 kW: Q12 and Q13 are gone, the vapour's heat now in
  R101's model and its vent condenser.
  Rejected: the lamp wells Q3 as the port (they take the lamps' losses, not the content's heat);
  reversing Q2 (the jacket removes heat).
- Q3 10.43 (0.083) from the lamp wells to cooling water: the lamps' electricity less the light
  (70 % of P1).
- Q4 8.78 (0.070) from E-102 to cooling water: R101's vent condenser duty (core ADR 0062,
  `condenser.energy_port: e102`, `calculated`): the vapour condensed at 363 K (6.54), all of it
  cooled as liquid to 303 K (1.84) and the HBr cooled as an ideal gas (0.39; HBr's `ideal_gas`
  from the chemicals package, SRC-4). Until core 1.10.0 the script's 8.16 kW (D-008).
- Q5 0.66 (0.005) from E-103 to brine: the toluene and bromine of S7 condensed at 268 K, all
  of S7's condensables cooled as liquid from 303 K and the HBr as a gas (the script's flash).
- Q6 14.74 (0.117) from A-101 to cooling water: HBr from gas at 268 K to 48 wt% acid at 313 K.
- Q7 24.09 (0.191), Q9 5.05 (0.040) and Q14 14.80 (0.117) of LP steam to ST101, ST102 and ST103:
  written by core's still model (`energy_port: steam`, `calculated`, ADR 0059, 0061): the latent
  heat of what the strip boils up, and for the column `(R + 1)` times the distillate's latent
  heat (the reflux boiled up again: R 2 and 0.5); 150, 80 and 80 kW while distilling. Until core
  1.10.0 the one-stage ST102 took 13.64 kW for both cuts; the column's reflux costs 6.2 kW more
  (Q9 + Q14 19.85 kW).
  Under core 1.9.0 the model's steam replaced the hand values (20.21 and 10.78 kW), which were
  too low: they counted the charge's cooling to its first bubble point but not the pot heating
  back up as it strips, nor that the vapour leaves at the pot's rising temperature. The full
  balance from the charge's temperature (scripts/balance.py repeats the strip on the same data,
  its cut within 0.01 % of core's) is now 22.58 kW for ST101 (sensible -1.51) and 18.52 for ST102
  with ST103 (-1.33): the model's are kept; the net sensible credit, 2.84 kW, is a recorded
  exclusion (below): it is negative, so no stream of its own can carry it beside the model's
  steam, and `still.heat_up` (ADR 0063) gives no heat-up for a charge above its bubble point
  (D-015).
- Q8 28.44 (0.225) from ST101's condenser to cooling water: S12's vapour condensed from the pot's
  temperature at which each part leaves (335.5 to 373.8 K) at 15 kPa(a) and cooled to 303 K;
  about 177 kW while stripping. The strip bypasses K-101, so its condenser is the script's.
- Q10 5.05 (0.040) from K-101's condenser to brine during the forerun and Q11 14.80 (0.117) to
  cooling water during the main cut: the column's condenser duties, `(R + 1)` times the
  distillate's latent heat (`still.condenser_port`, `calculated`, ADR 0061), 80 kW while each
  runs; at 2 kPa(a) the forerun condenses near 289 K, below the cooling water, so on brine.
  Q16 0.15 (0.001) to brine: the forerun cooled from its bubble point (289.0 K) to 268 K; Q15
  1.99 (0.016) to cooling water: the product from its bubble point (354.3 K) to 303 K and the
  residue S16 in C-101 from 376.8 to 333 K (the script's). Until core 1.10.0 the script gave
  the condensers with the coolers in them (Q10 4.91, Q11 11.97 kW for the one stage).
- P1 14.90 (0.118) for the lamps (20 kW for the 5.24 h of light a batch), P2 3.0 (0.024) for
  R-101's agitator, P3 2.25 (0.018) for C-101's agitator (1.5 kW) and dry vacuum pump (4 kW)
  while distilling, 2.87 h a batch.
Totals per kg: cooling water 0.666 kWh, brine 0.046 kWh, LP steam 0.431 kWh, electricity 0.160
kWh (until core 1.10.0: 0.634, 0.044, 0.392 and 0.156; until core 1.9.0: 0.618, 0.039, 0.335 and
0.156). The jackets are checked against the cooling water's mean temperature (303 K), and LP steam
at 421 K is the hottest medium; no decomposition onset of benzyl bromide or of the residue is
open, so the TD24 or DSC onset of both must lie above the 421 K wall (D-011), else the still and
the heat-up need hot water.
Recorded exclusions, each with its number:
- the stills' sensible heat (the charges hotter than the pot's first bubble point, the vapour
  and the residue leaving at the pot's temperature): 2.84 kW (0.022 kWh/kg) less LP steam than
  the model's Q7, Q9 and Q14 (ST101 -1.51, ST102 and ST103 -1.33 kW; scripts/balance.py), so the
  LCI's LP steam is 5.2 % high (core limit L-6);
- the heat of mixing of bromine into toluene: not known openly; at an ASSUMED 5 kJ/mol it would
  be 1.1 kW (0.009 kWh/kg) more on R-101's jacket;
- the heat of mixing of bromine into toluene is not used as core 1.10.0's dose
  `heat_of_solution` (ADR 0063) for want of a value (D-015);
- the still agitator's 1.5 kW while distilling (0.61 kW year average) goes into the pot and would
  save as much steam; the vacuum pump's 4 kW (1.64 kW year average) leaves with its own air
  cooling;
- heat losses of R-101 while dosing and of C-101 (only the heat-up carries 10 %); the
  brine's and the cooling water's own electricity (chiller, pumps, tower) are in their LCI
  backgrounds (D-012).

## D-010 Yields against the source (2026-11-06; core 1.10.0, 2026-11-06)
Decision: the model's yields are 90.2 % of theory on the bromine (mol of benzyl bromide in S15
per mol of bromine dosed; HBr takes the other half of the bromine) and 87.7 % on the toluene
make-up S1 (1.034 kg of bromine and 0.614 kg of toluene per kg of product; stoichiometric 0.934
and 0.539). Until core 1.10.0: 88.5 % and 86.9 % (1.038 and 0.609 kg/kg); the column's forerun
returns less benzyl bromide to be brominated again (D-007), and the toluene the vent carries to
the acid (3.6 g/kg, D-008) is now made up. **The modelled yield on toluene is below the source's**:
SRC-1, Example I, gives about 90 % on toluene, under X-rays with bromine in excess. The yields
follow from the ASSUMED k2/k1 and from the separations, so they are not predictions: in scratch
copies at the recycle's fixed point (core 1.9.0, the one-stage product cut), k2/k1 = 0.1 gave
93.5 % on the bromine (99.1 mol% product) and 0.4 gave 79.9 % (97.9 mol%).
Both are upper bounds in one respect: ring bromination and the condensation of benzyl bromide
are not modelled.

## D-011 Thermal screening, the rate-constant sensitivity and the hazards (2026-11-06; core 1.10.0, 2026-11-06)
Result (`cheme process reactor-hazards`, core ADR 0050, 0054, 0058, 0062): adiabatic temperature
rise of the whole batch 44.2 K (with -32.3 kJ/mol; 42.2 K until core 1.10.0, on a charge with
more benzyl bromide); largest accumulation of the dosed bromine 1.66 %, at the end of the
dosing; MTSR at that moment 363.9 K, against an MTT of 383.8 K (`hazard.mtt`: the
normal boiling point of toluene, the liquid's main component; core's default, the lowest boiling
point of the charge and the dose, would be bromine's 331.95 K, a dose that does not stay as such
in the liquid: L-5; core 1.9.0's default is still bromine's, which at 18.7 mol% of the charge and
doses is no dissolved gas, ADR 0058's known limitation). The content's bubble point by Raoult is 385.0 K at the start and 393.7 K at
the worst moment (with the 0.5 mol% bromine accumulated), so 383.8 K is a lower bound in the
design case. The vented HBr adds nothing to the MTSR; at the MTSR it forms at 34.67 m3/h and
leaves with the content's vapour at 59.57 m3/h (core 1.10.0, ADR 0062: 0.418 of the gas is
vapour), within R-101's off-gas capacity of 90 m3/h (D-014); with the vent blocked it
pressurises the vessel, which the screening does not assess (D-014).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
With MTSR below MTT the class is 1 or 2 if the TD24 lies above the MTSR, and 5 if it lies below
(TD24 < 363.9 K: core's `criticality()` and Stoessel test the TD24 against the MTSR first,
SRC-6); it needs the TD24.
Sensitivity (a scratch copy of the folder per case, both A divided, the feeds re-solved by
scripts/balance.py and `cheme process propagate --fill` in turn for 1000 t/a at 4 mol of
toluene per mol of bromine, everything else as designed; `reactor-hazards`, `reactors`,
`recipe`; core 1.10.0 with the vent's vapour, 2026-11-06, compared with the 90 m3/h of D-014):

| k at 363 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 383.8 K | gas release at the MTSR (101.3 kPa(a); with the content's vapour, the non-condensable HBr in brackets) vs the off-gas system's 90 m3/h | post-reaction to 0.999 | cycle, batches/a | class without TD24 |
|---|---|---|---|---|---|---|---|
| 5.0e-4 (design) | 1.66 % | 363.9 K | 19.9 K below | 59.57 m3/h (0.3224 mol/s, 34.67 m3/h): 0.66 x | 0.24 h | 7.03 h, 1127 | 1, 2 or 5 |
| k/10 | 14.8 % | 370.3 K | 13.5 K below | 102.3 m3/h (0.3612 mol/s, 39.51 m3/h): 1.14 x | 4.13 h | 10.92 h, 725 | 1, 2 or 5 |
| k/100 | 67.6 % | 396.1 K | 12.3 K above | the content boils (`boils`, its vapour pressure 197 kPa): not bounded (0.3575 mol/s, 41.83 m3/h of HBr) | 51.9 h | 58.7 h, 135 | 3, 4 or 5 |

Until core 1.10.0 (the HBr alone, the one-stage product cut): the design case 1.73 %, 363.9 K,
35.10 m3/h; k/10 16.4 %, 370.5 K, 41.13 m3/h; k/100 73.1 %, 394.6 K, 38.18 m3/h. The HBr released at
a cooling failure stays near the dosing rate in all three cases (0.319 mol/s of bromine dosed): a
slower chain accumulates more bromine, but its smaller rate constant offsets most of it, and the
HBr forms at most 1.12 times as fast at its MTSR (k/10). What grows is the vapour with it (0.72
mol per mol of HBr at the design MTSR, 1.59 at k/10) and the gas a blocked vent must hold
(D-014). A finding of this run: at fixed feeds (the make-up not re-solved) the slow cases drift
to a charge of 5.1 and 6.8 mol of toluene per mol of bromine, since less toluene reacts and more
bromine leaves with the vent's vapour, and the dilution lowers the k/100 MTSR to 382.6 K, below
the MTT; at the designed 4 mol per mol it is 396.1 K. The sensitivity is only comparable with the
feeds re-solved.
At k/100 the vent's vapour takes bromine off the content: 0.72 kmol a batch past E-102, 12.6 %
of the bromine dosed (0.031 kmol, 0.5 %, in the design case), which E-103 and the absorber then
take: a slow chain loads the acid and the scrubber with bromine (D-008, D-014).

MTSR over the batch (core 1.10.0, ADR 0058): 363.3 K at the start, 363.8 K at 1.02 h, 363.9 K
from 2.12 h to the end of the dosing (5.0 h), back to 363.2 K at the end of the post-reaction
(5.24 h): the worst moment is the end of the dosing, as the single value said.

Interpretation: all at once (accumulation 1) the MTSR would be about 407 K, above the boiling
point of toluene, so the dosing, not the dilution, keeps it below the MTT. **For a photoreactor
the slow cases are the lamp-failure cases**: weak, fouled or failed lamps (or a bromine-coloured
light path, SRC-1) slow the chain like a smaller k, and in the dark the bromine accumulates while
it is dosed; when the light comes back the accumulated bromine reacts at once, with its HBr. At
k/100 the content holds about 14 mol% bromine at the end of the dosing (3.9 kmol in 27.8 kmol of
liquid: the 23.9 kmol charge plus the 5.74 kmol dosed less the 1.86 kmol reacted, each reaction
taking one mole out of the liquid as its HBr is vented), which lowers its bubble point to about
372 K (Raoult, the bromine's Antoine extrapolated), so the margin is smaller still than the
table's MTT shows. The bromine dosing must therefore be interlocked with the lamps' power and
light sensors, the temperature, the agitator and the HBr off-gas flow: HBr forms only as the
bromine reacts, so dosing without off-gas means bromine accumulating. At k/100 the cycle (59 h)
rules out the design before safety does. Open for the next stage: a photoreactor test with
reaction calorimetry and off-gas measurement (rate against light, quantum yield, the dark rate),
the TD24 of the crude, the product and the residue (benzyl halides condense with HBr evolution in
contact with iron and other metals, SRC-3), the gas-generation pressure with a blocked vent
(Stoessel's separate criterion; R-101's relief, D-014). Screening values only, not a reaction-hazard assessment.
Open, toxic gases, water and the scrubber (reasoning only, for the HAZOP):
(a) Loss of the absorber water while R-101 doses: up to 0.32 mol/s of HBr (and the bromine
vapour with it) to the tail scrubber or to air. Stopping the bromine and the lamps stops the HBr
within the chain's dark lifetime; the 1.66 % accumulated bromine (0.095 kmol, 15 kg a batch)
stays in R-101 and gives at most 0.095 kmol (8 kg) of HBr if the light comes back. The dosing and
the lamps are to be interlocked on A-101's water flow and on HBr breakthrough, and a caustic
guard scrubber is to take the accumulated HBr and bromine (equipment list).
(b) Water ingress into R-101: suck-back from A-101 (HBr absorption in water pulls a vacuum once
the gas stops or the reactor cools) or a jacket leak from the tempered-water loop. Water does not
react violently with the content (benzyl bromide hydrolyses slowly, SRC-3), but it takes up HBr
and bromine to a corrosive aqueous phase and attacks the vessel at any defect of the glass
lining; anti-suck-back protection on the off-gas line (a nitrogen-padded seal pot or a vacuum
breaker on nitrogen) and jacket-leak detection are to be assessed.
(c) Bromine (H330, fatal if inhaled; H314, SRC-3): its storage, transfer and dosing in a closed
system with a caustic (or thiosulfate) scrubber for its vents; an emergency vent from R-101 to
the caustic scrubber, not to air. Benzyl bromide is a strong lachrymator (SRC-3): closed sampling,
the receivers and T-201 padded and vented to the scrubber, product filled under nitrogen.
(d) The lamp wells and flammability. R-101 holds 20 kW of electric lamps in immersion wells
(glass or quartz, ASSUMED), cooled on cooling water (Q3, about 14 kW while lit), immersed in
toluene at 363 K, 86 K above toluene's flash point of 4 C (277 K, SRC-3); benzyl bromide's flash
point (79-86 C) is passed too, here and in C-101. The off-gas carries 0.66 to 1.07 mol of
toluene vapour per mol of HBr (D-005, D-008), far above toluene's lower explosive limit of 1.1 vol% (SRC-3): with
air in the head space or the vent it is a flammable atmosphere. A rupture of a well or a leak at
its seal (thermal shock, a blow, an overheated lamp) puts the well's cooling water straight into
a content of bromine, HBr and benzyl bromide, a path apart from the jacket leak of (b) and at the
cooling water's pressure, and exposes the lamp's electrics, a heat and ignition source, to the
flammable liquid and its vapour. Safeguards to be assessed: the well coolant held below the
vessel's pressure, or a non-aqueous inert coolant in the wells; leak detection in the well
coolant (conductivity or pH for HBr, or a loss of level or pressure); the lamp power tripped on a
well-coolant fault (low flow, high temperature, leak) and on a lamp over-temperature, the lamp
surfaces kept far below toluene's autoignition temperature of 480 C (SRC-3); nitrogen inerting
kept through the whole of the lighting, with an O2 check of the head space before the lamps are
switched on and an O2 trip while they are on; lamps, wells and terminals rated for the zone (the
area classification is open). Open for the HAZOP: air in-leakage into the vacuum stills (C-101 at
15 and 2 kPa(a) with hot toluene and benzyl bromide above their flash points), their receivers
and the vacuum pump's discharge.

## D-012 Preliminary gate-to-gate LCI (2026-11-06)
Decision: `cheme assess lca --write` per kg of distilled benzyl bromide from the flowsheet's
year averages; the nitrogen per batch (20 Nm3, 25.0 kg, ASSUMED: R-101 purged with 3 volumes, C-101's
vacuum broken once, the receivers and T-201 padded and the crude pressed over) is an `lca.yaml`
consumable `per_batch` (core ADR 0053, library ADR 0035), 28 g/kg, linked to asu-1; the bromine
linked to bromine-1; the toluene make-up linked to btx-1 (the library entry whose dataset makes
toluene, as p-toluenesulfonyl-chloride-1 links it; the issue's scouting predates btx-1 on main,
so no proxy was needed); the LP steam counted as heat (kWh); every other background a gap with
the activity it should connect to. No water rinse: one product, the train kept dry.
Allocation: by mass, written as shares: the benzyl bromide (126.263 kg/h) and the HBr in the acid
(65.864 kg/h, counted as the HBr it contains): 0.6572 and 0.3428 (lca.yaml `allocation`, agent
proposal; until core 1.10.0 0.6556 and 0.3444). No physical relationship is clear and no price is sourced, so the WBCSD rule of
docs/system-model.md falls back to mass (docs/registry.md). Rejected: shares 1/0 (as
benzoyl-chloride-1 gives its hydrochloric acid): half the bromine leaves in the acid, a
bromine product sold at a price far closer to the main product's than hydrochloric acid's;
substitution of hydrogen-bromide-1's acid, which belongs to the substitution variant database,
not to this cut-off dataset (library ADR 0007), recorded as the variant to compare.
Per kg of benzyl bromide (unallocated): bromine 1.034 kg, toluene 0.614 kg, process water 0.565
kg, nitrogen 28 g, electricity 0.160 kWh, LP steam 0.431 kWh, cooling water 0.666 kWh and brine
0.046 kWh removed (D-009); out: 48 wt% acid 1.094 kg (with 3.6 g of toluene and 3.5 g of
bromine in the model, D-008), residue 79 g and toluene purge 40 g to incineration. Until core
1.10.0: bromine 1.038, toluene 0.609, water 0.569 kg, electricity 0.156, LP steam 0.392, cooling
water 0.634, brine 0.044 kWh, acid 1.095 kg, residue 77 g, purge 44 g (until core 1.9.0 LP steam
0.335, cooling water 0.618, brine 0.039).
Not counted: the vents (emission_exclusions; the toluene and bromine past E-103 are now in the
balance, in the acid, and where they go from there is the `vent-toluene` exclusion, D-008).

## D-013 Dedicated train (2026-11-06)
Decision: R-101, E-102, E-103, A-101, C-101 with K-101 and T-201 make only benzyl bromide, batch
after batch: 1127 batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms.

## D-014 R-101's off-gas capacity against the gas released at a cooling failure (2026-11-06; with the content's vapour under core 1.10.0, 2026-11-06)
Result (`cheme process reactor-hazards`, core 1.10.0, ADR 0058 with the vent's vapour of ADR
0062): at a cooling failure at the worst moment (the end of the dosing, 1.66 % of the bromine
accumulated) the reactions run on at the MTSR, 363.9 K, and give off 0.3224 mol/s of HBr, 34.67
m3/h at 363.9 K and 101.3 kPa(a), which leaves saturated with the content's vapour (0.418 of the
gas, 0.72 mol per mol of HBr): 59.57 m3/h up the line to E-102 (per batch of the recipe, from the
worst moment's content; the condenser is not credited, its cooling may fail too). Run to
completion the accumulated bromine gives 0.0956 kmol (2.86 m3 at the MTSR, 4.91 m3 with the
vapour) more HBr. `reactor-hazards` reports that worst-accumulation moment only; the release
is larger earlier in the dosing, when the content holds more toluene and so more vapour per mol
of HBr. Core's gas release at the MTSR applied to each moment of R101's cooling profile (126
moments, its `_gas` on each moment's content at that moment's MTSR; the library test
`test_core_screens_the_gas_release_at_every_moment`) gives the largest, 72.80 m3/h, for a cooling failure
0.38 h into the dosing: 34.54 m3/h of HBr at an MTSR of 363.8 K with 0.526 of the gas vapour
(1.11 mol per mol). In normal operation the off-gas peaks at 0.334 mol/s past E-102 (29.89 m3/h
at 303 K, `cheme process recipe`, 0.69 h into the dosing); at the vessel that HBr (0.316 mol/s)
carries 1.03 mol of vapour per mol (the content then at 363.15 K, Raoult as in core's vent),
68.9 m3/h at 363 K (core reports the vent at the condenser's temperature). A cooling failure at
that moment releases at least that, and the 72.80 m3/h covers it.
Until core 1.10.0 core compared the HBr alone, 35.10 m3/h, with a capacity of 45 m3/h; with the
vapour the release is 1.32 times that capacity (`cheme.reactor-hazard-vent`, warning).
Decision: R-101's off-gas system (the vapour line to E-102, E-102, E-103 and A-101 with its
tail scrubber) is sized for 90 m3/h of gas with its vapour at the vessel's pressure,
`hazard.vent_capacity: 90`, ASSUMED: 1.2 x the largest gas release of a cooling failure over the
batch with the assumed rate law and the content's vapour (1.2 x 72.80 = 87.4 m3/h), rounded up
to the next 5 m3/h. The release at the worst-accumulation moment's MTSR is then 0.66 of it
(`cheme.reactor-hazard-vent`, info), the largest over the batch 0.81, the normal peak at the
vessel 0.77. A first sizing of 75 m3/h took 1.2 x the worst-accumulation moment's 59.57 m3/h as
the largest; it left 1.09 over the normal peak and 1.03 over the release 0.38 h into the
dosing, so it is not kept. E-102 condenses about 14 kW at the normal peak (8.78 kW year average,
11.8 kW over the 5.24 h of gas).
Reason: with a fast chain the release follows the dosing, so sizing for it costs little and
needs no slower dosing; the vapour is most of the volume and has to pass the line to E-102. The
1.2 is a margin on that case, not on the kinetics: the rate law is ASSUMED (D-005), and the
capacity is no more credible than it.
Open (design findings, for the next stage):
- **The slow cases exceed it.** In D-011's k/10 case the release at the MTSR is 102.3 m3/h (39.51
  m3/h of HBr with 1.59 mol of vapour per mol, 370.3 K, 3.4 mol% bromine accumulated), 1.14 x the
  capacity (at its worst-accumulation moment; the other moments of that case were not
  screened), and E-102 would have to condense about 26 kW; at k/100 the MTSR, 396.1 K, is above
  the content's bubble point (about 372 K): the content boils (`boils`) and the vapour is not
  bounded by the screening (D-011, there ruled out by the 59 h cycle). Either the vapour line and
  E-102 are sized for about 105 m3/h and 26 kW, or the dosing is interlocked so that the
  accumulation stays at the design case's (D-011). Until core 1.10.0 the same finding was hand
  arithmetic (1.51 mol per mol at k/10, about 115 m3/h on 45 m3/h of HBr).
- **The blocked vent.** A flooded or frozen absorber or a closed valve in the off-gas line puts
  the gas into R-101's head space, 1.20 m3 at the end of the dosing (4 m3 vessel, 2.80 m3 of
  crude): the 0.0956 kmol of the design case raise it by about 0.24 MPa at 363.9 K, the 0.882
  kmol of k/10 by about 2.3 MPa at 370.3 K, besides the content's own vapour pressure, more
  than a glass-lined vessel is usually rated for; during the dosing the HBr forms all the time.
  So R-101 needs a relief device (rupture disc to a catch tank and the caustic scrubber, never
  to air, D-011 (c)) sized for the gas generation by a DIERS method from calorimetry, the
  bromine dosing interlocked on R-101's pressure and on the off-gas flow (D-011), and no
  isolation in the off-gas line without a relief path. Reasoning only, not a relief sizing.
Rejected: keeping 45 m3/h (sized on the HBr alone, it would not pass the vapour that goes with
it at the design MTSR); 75 m3/h (1.2 x the worst-accumulation moment's release only, see
above); a larger capacity for the k/100 case (what exceeds is the boiling content, which a
relief device takes, not the off-gas system).

## D-015 Core 1.10.0: the column on the still, the vent's vapour and its condenser (2026-11-06)
Decision: on the core pin v1.10.0 (c55e9c7) the entry moves three hand workarounds onto core's
models, each compared with the value it replaces before it was adopted:
- **The product cut through a column** (`still.column`, `still.condenser_port`, core ADR 0061;
  L-4). ST102 is split into the forerun ST102 and the main cut ST103, both through K-101 (5
  theoretical stages, reflux ratio 2 and 0.5, ASSUMED), their condensers on Q10 and Q11 written
  by propagate beside the reboilers Q9 and Q14; the coolers the hand condensers held are Q16 and
  Q15 of the script. Compared: the one stage gave 98.3 wt% benzyl bromide with 1.6 wt% benzal
  bromide and 88.5 % on the bromine; the column gives 99.85 wt% and 90.2 %. The column at no
  reflux repeats the one stage (98.54 wt% on this forerun); the purity holds between 99.4 and
  99.9 wt% over 3 to 8 stages, reflux 0.5 to 1 and benzal bromide's assumed heat of vaporization
  (D-007). Cost: 6.2 kW more LP steam for the reflux (D-009).
- **The vent's vapour and E-102 as R101's vent condenser** (`batch.vent.vapour`,
  `batch.vent.condenser` with `energy_port: e102`, core ADR 0062; L-3). The step E102 and its
  hand streams Q12 (R101's model duty to E-102) and Q13 (the vapour's rest) are gone; E-102's
  duty Q4 is the model's, 8.78 kW (the hand 8.16 kW on a linear mean vapour of 0.803 mol per
  mol, 8.85 kW at the model's 0.87: D-008 says why they differ); HBr has `ideal_gas` data from
  the chemicals package (SRC-4) so that the condenser cools the gas too (0.39 kW). The vapour
  past E-102 is now in the balance: E-103 is a flash in scripts/balance.py on S7 (core's vent
  has one condenser), its condensate S19 to T-201, its gas S9 with 0.0061 mol of toluene and
  0.0034 of bromine per mol of HBr to the acid. The toluene that leaves with the acid is made
  up (S1 0.614 instead of 0.609 kg/kg).
- **The gas release at a cooling failure with the vapour** (core ADR 0062 in the screening of
  ADR 0058): 59.57 m3/h at the MTSR, of which 34.67 m3/h non-condensable, 1.32 times the 45
  m3/h of core 1.9.0's capacity; the largest release over the batch, 72.80 m3/h 0.38 h into the
  dosing, sets the capacity, raised to 90 m3/h (D-014).
Tried and not adopted:
- `still.heat_up` (ADR 0063) on ST101, ST102 and ST103 (a scratch copy, 2026-11-06): 0 kW for
  ST101 and ST102, whose charges enter at 363.15 and 373.76 K, above their bubble points of 335.5
  and 321.4 K (core does not model their flash, and gives no credit), and 7e-5 kW for ST103,
  whose charge is at its bubble point. It changes nothing, so the stills' net sensible credit
  stays the recorded exclusion of D-009 (2.84 kW, L-6).
Not used: `batch.heat_up` (R-101's heat-up is E101's step with the script's Q1 and the recipe's
jacket time; R101's model duty has no stream, D-009); `vessel.metal_heat_capacity` (no vessel
mass at the concept stage; the heat-up's 10 % losses stand in); a dose's `heat_of_solution` (no
value for bromine into toluene, D-009's exclusion); `vent.henry` (no HBr solubility in toluene at
hand, D-005); a `purity` end (the main cut ends on the residue's mobility, D-007).
Reason: each model is the hand method made part of the balance (the vapour integrated with the
batch, the column with the still's path), checked against the hand value on the same data; the
differences come from the design (the charge, the forerun), not from the models.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its HBr vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas rate, year-average duty (no stream: into the content) | done in cheme, effective rate ASSUMED | D-005, D-009, D-011, core ADRs 0050, 0054, 0059 |
| the vent's vapour and E-102 as its vent condenser: S7 past E-102, the condensate returned, E-102's duty Q4 | done in cheme, ideal liquid ASSUMED | D-008, D-009, core ADR 0062 |
| MTSR over the batch, gas release at the MTSR with the content's vapour against the off-gas capacity | done in cheme, capacity ASSUMED | D-011, D-014, core ADRs 0058, 0062 |
| photon budget of the lamps | hand (script), quantum yield ASSUMED | D-005, L-1 |
| batch recipe, cycle time, basis check, R-101's vessel and jacket | done in cheme | D-003, core ADRs 0051, 0052, 0057 |
| strip ST101 (one stage): distillate, residue, boil-up time, latent heat (Q7) | done in cheme, ideal liquid ASSUMED | D-007, D-009, core ADRs 0055, 0059 |
| forerun ST102 and main cut ST103 through K-101 (5 stages, reflux 2 and 0.5): cuts, recoveries, boil-up times, reboilers Q9, Q14 and condensers Q10, Q11 | done in cheme (Diwekar's shortcut), stages, reflux, ideal liquid and benzal bromide's vapour pressure ASSUMED | D-007, D-009, core ADR 0061 |
| stills' full energy balance (sensible heat, left out of Q7, Q9 and Q14), the strip's condenser Q8 and the coolers Q15, Q16 | script (the strip repeated on core's data) | D-009, L-6 |
| C-101's jacket against the stills' constant boil-up (wetted area as the pot empties) | hand (scripts/still_jacket.py), U and the head's shape ASSUMED | D-007, L-6 |
| toluene recycle S2 | done in cheme (tear, Wegstein) | D-006, core ADR 0060 |
| feeds for 1000 t/a, absorber water, mixing and bubble-point temperatures, duties Q1, Q2, Q3, Q5, Q6, Q8, Q15, Q16, P1 | script (with propagate in turn for the feeds) | D-006, D-008, D-009, L-7 |
| E-103, the second vent condenser: S9, S19, Q5 | script (a flash as core's vent condenser) | D-008, L-3 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (core 1.10.0)

- Core 1.10.0, ADR 0061: `still.column: {stages: 5, reflux: constant, ratio}` on ST102 (ratio 2)
  and ST103 (ratio 0.5), the forerun and the main cut through K-101 on Diwekar's shortcut, and
  `still.condenser_port: q`, so that propagate writes the reboilers Q9 (5.04814 kW) and Q14
  (14.8002 kW) and the column's condensers Q10 and Q11 (the same, `(R + 1)` times the
  distillate's latent heat); `cheme process stills` reports each cut's recovery and the reflux
  (D-007, D-009). ST102 of core 1.9.0 (one stage, two `cuts:`) is split in two steps, since the
  reflux is one per still step.
- Core 1.10.0, ADR 0062: R101's `batch.vent.vapour: {}` (the content's toluene, bromine, benzyl and
  benzal bromide, Raoult) and `vent.condenser: {temperature: 303.15, returns: vessel,
  energy_port: e102}`: E-102 is R101's vent condenser, its duty written on Q4 (8.77959 kW), the
  vent S7 past it at 303.15 K with the vapour left in it; the screening's gas release at the MTSR
  with the vapour (59.57 m3/h, `vapour_share` 0.418) against `hazard.vent_capacity` (D-008,
  D-014). HBr's `ideal_gas` data (materials.yaml, SRC-4) let the condenser cool the gas.
- Tried, not adopted (D-015): `still.heat_up` (ADR 0063; no heat-up for a charge above its
  bubble point, both here). Not used: `batch.heat_up`, `vessel.metal_heat_capacity`, a dose's
  `heat_of_solution` (ADR 0063), `vent.henry` (ADR 0062), a `purity` end (ADR 0061), each for
  the reason D-015 gives.

From core 1.9.0:

- Core 1.9.0, ADR 0059: ST101's, ST102's and ST103's `energy_port: steam`, so that
  `cheme process propagate --fill` writes the boil-up's duty on Q7 (24.0899 kW), Q9 and Q14;
  all are `calculated` and go stale with the model; Q2 and the script's condensers and coolers
  carry what the models leave out (D-009). Until core 1.10.0 R101's `energy_port: reflux` put
  its model's duty on Q12 (6.23565 kW) to E-102, with the vapour's rest on Q13; both are gone,
  and R101's model duty, now into the content, has no stream (D-009).
- Core 1.9.0, ADR 0058: the `mtsr_profile`, `per_reaction` (BNBR and BALBR, one run) and the gas
  release at the MTSR against `hazard.vent_capacity` (D-011, D-014). `hazard.mtt` stays set by
  hand: the default is still bromine's boiling point (L-5).
- Core 1.9.0, ADR 0060: `tears: [{stream: S2, initial}]` and `convergence:` with SP201's `split:
  {rec: 0.98}`: the toluene recycle converged by propagate (D-006), replacing the 14 hand passes
  of core 1.8.0.
- Not used: `hazard.reactions` (both reactions are brominations by the accumulated bromine and
  count together; BNBR sets the MTSR).

From core 1.8.0:

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with `batch.dosing` and `batch.target` | R101 (bromine dosed into the toluene) | 0050 |
| `batch.vent` | R101 (all HBr) | 0054 |
| recipe vent report (peak kmol/s, m3/h, kg per batch) | the condensers' and absorber's load, D-005, D-008 | 0054 |
| `hazard.mtt` and the screening of a vented semi-batch | R101, D-011 | 0050, 0054 |
| `still:` with Raoult's law (Antoine `vapour_pressure`, `heat_of_vaporization`), `boilup` in kW, `end: residue` | ST101 | 0055 |
| `still:` with `cuts:` (forerun and main cut; until core 1.10.0, replaced by two column steps) | ST102 | 0055 |
| recipe `distil from:` and `units:` (one vessel over several steps) | C-101 (ST101, ST102, ST103), R-101 (E101, R101) | 0055, 0057 |
| vessel sizing and jacket check, `heat` time from the jacket | R-101 | 0052 |
| per-batch LCA consumables, `allocation: shares` | nitrogen; the acid | 0053 |
| splitter and mixers in propagate | the toluene recycle and purge | - |

Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
filter and the dryer (no solids), `still.feed` (no solvent swap).

## Core limits hit (each a candidate core issue)

Status on core 1.10.0 (2026-11-06): L-4 resolved, L-3 mostly resolved (core ADRs 0061, 0062,
D-015); on core 1.9.0 L-8 resolved, L-6 and L-7 partly (each says what is left); L-1, L-2, L-5
and L-9 stand.

- L-1: no photochemical rate law. The rate of a light-driven chain depends on the absorbed photon
  flux (lamp power, emission spectrum, the light path through a bromine-coloured liquid, the
  quantum yield) and is nearly zero in the dark; core takes only a thermal power law, so the rate
  is an ASSUMED effective k (D-005), the lamps' photon budget is hand arithmetic in the script,
  and a lamp failure can only be screened as a smaller k (D-011). Core needs a photon-flux rate
  term (with a light on/off state in the recipe) and the light's heat in the energy balance.
- L-2: the semi-batch is isothermal at one temperature or adiabatic; a reactor at reflux, whose
  temperature follows the content's rising bubble point and whose heat leaves through the
  condenser, cannot be modelled (the reason the reaction is held below the boil, D-005).
- L-3 (ADR 0054): the vent carries only the named gas, no vapour of the liquid. At 363 K the HBr
  carries 0.6 to 1.1 mol of toluene vapour per mol, condensed and returned in E-102 and E-103:
  their duties, the evaporative cooling of R-101 and the toluene left in the vent (3.8 g/kg) are
  script values outside the balance. Core needs the solvent vapour in the off-gas from the
  vessel's VLE, with a partial (reflux) condenser on the vent (as benzoyl-chloride-1's L-2).
  Core 1.9.0 compares the gas release at the MTSR with the vent's capacity (ADR 0058), for the
  vent gas alone: the vapour with it at a cooling failure (0.68 to 1.51 mol per mol, D-014) is
  hand arithmetic, and the vapour's heat had to be carried by energy streams from R-101 to E-102
  (Q12, Q13, D-009).
  **Mostly resolved in core 1.10.0** (ADR 0062, D-015): the vent carries the content's vapour,
  E-102 is R101's vent condenser with its duty on Q4, the evaporative cooling and the condensate's
  return are in R101's model, and the screening counts the vapour with the gas (D-014); Q12 and
  Q13 are gone. Still open: one condenser per vent (E-103 is a flash in the script), no HBr
  dissolved in the condensates or the crude without its Henry constant, an ideal liquid.
- L-4 (core#173): no batch rectification with reflux; the strip has to stay shallow (D-007) and
  the product's purity rests on the heavy's large volatility; a higher grade needs a column.
  **Resolved in core 1.10.0** (ADR 0061, `still.column`): the forerun and the main cut run through
  K-101 (99.85 wt% instead of 98.3 wt%, D-007, D-015). The column's holdup, start-up and
  hydraulics are not modelled (ADR 0061's limitations).
- L-5: the default MTT is the lowest boiling point of the charge and the doses (here bromine's
  332 K, below the process temperature); it ignores that the dose reacts and that the content is
  a mixture. `hazard.mtt` was set by hand; core could give the content's bubble point at the
  worst moment from its Antoine data (D-011: 393.7 K design, about 372 K at k/100). Still so in
  core 1.9.0 and 1.10.0: ADR 0058 leaves out vent components, dosed gases and minor dissolved
  gases, but a dosed liquid above 5 mol% of the charge and doses (bromine) still sets the
  default; core 1.10.0's `boils` (ADR 0062) now says when the content boils at the MTSR (k/100).
- L-6 (ADR 0055): the still has no heat-up, flash or sensible heat of a charge hotter than its
  bubble point (both charges here), a constant boil-up whatever the wetted jacket area, and does
  not size its vessel, jacket, condensers or vacuum system: C-101 is sized by hand. Here the
  residue at the end of ST103 (about 0.04 m3) wets only about 0.95 m2 of jacket, about 12.7 kW
  against the 80 kW boil-up; the jacket-limited times (scripts/still_jacket.py, D-007) are 1.29 h
  a batch longer than core's. Core needs the boil-up from U, the wetted jacket area of the vessel
  and the steam temperature.
  **Partly resolved in core 1.9.0** (ADR 0059): the still's model writes its steam duty, the
  boil-up's latent heat (Q7, Q9). **And in core 1.10.0** (ADR 0061): a column's condenser duty
  on its own stream (Q10, Q11). Still open: the sensible heat of a charge hotter than its bubble
  point, the vapour and the residue (2.84 kW less steam here, a recorded exclusion, D-009):
  ADR 0063's `still.heat_up` heats a colder charge to its bubble point but gives a hotter one
  none (its flash is not modelled, D-015); a one-stage still's condenser from the pot's rising
  temperature (Q8, the script's).
- L-7: core propagates from the feeds and cannot solve them for a product rate, and did not tear
  a recycle: the script scaled the feeds and brought the toluene recycle to its fixed point by
  passes of propagate and the script (as n-bromosuccinimide-1's L-6). **The recycle is resolved
  in core 1.9.0** (ADR 0060: S2 is a tear converged by propagate, D-006). Still open: the feeds
  for the product rate and the charge ratio (a design specification on S1 and S5) take passes
  of the script and propagate.
- L-8 (resolved in core 1.9.0, ADR 0059): an isothermal semi-batch reported its peak cooling
  duty and the heat released, but no year-average duty for its energy stream, so the script
  gave it. Core 1.9.0 writes it on Q12 (6.23565 kW, the script's own 6.2356 kW). Under core
  1.10.0 the duty, with the vent's vapour, flows into the content (2.52 kW) and has no stream
  (D-009).
- L-9 (ADR 0055): an ideal liquid only, and a component needs an Antoine equation or a constant
  alpha for the whole still: benzal bromide has one measured point, so its line is ASSUMED and
  the stills' basis is "not sourced".

## Open inputs
Photoreactor test: rate against light, quantum yield, dark rate, the heat of reaction and the
bromine's heat of mixing by calorimetry with off-gas measurement; the relative rate k2/k1 and the
ring-bromination share; the TD24 or DSC onset of the crude, the product and the residue; HBr
solubility in toluene at 363 K; VLE of toluene with benzyl bromide and of benzyl bromide with
benzal bromide; benzal bromide's vapour pressure; the product specification; the purge's need;
K-101's stages, reflux, packing and pressure drop (a pilot distillation); the vent's toluene and
bromine and the acid's quality; prices for the allocation; a TEA (`operation.batch: {recipe:
true}`); R-101's relief device and blocked-vent case, the vapour line and E-102 for the vapour of
a cooling failure in the slow cases (D-014).
