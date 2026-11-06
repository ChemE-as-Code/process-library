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

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; NIST WebBook and PubChem pages).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 3 528 899 A, E. Plander, J. Zahalka, V. Formacek, 1970 (priority CS 1965): Method of brominating the side chain of an alkyl benzene, https://patents.google.com/patent/US3528899A/en | background: side-chain bromination activated by light, heat or peroxides was mainly a laboratory process, because light penetrates the mixture only a short way, the reaction slows as bromine builds up, excess bromine accumulates and the ring is brominated as well. Example I: 0.6 mol bromine added to 0.5 mol toluene at room temperature under X-rays, at a rate that keeps unreacted bromine from leaving with the HBr, the HBr withdrawn; the cut at 190-210 C refined by repeated fractional distillation, about 90 % of theory on toluene. Discussion: the side-chain bromination is a series of successive reactions, the degree of bromination set by the moles of bromine introduced (Example II, xylene: 41 % monobromo- and 46 % dibromoxylene); benzal bromide itself is not named | read; patent, facts only | D-001, D-005, D-010, reactions.yaml (BALBR), benchmarks |
| SRC-2 | NIST Chemistry WebBook, SRD 69: toluene (C108883), bromine (C7726956), benzyl bromide (C100390), benzal bromide (C618315) | Antoine constants (NIST fits: toluene to Willingham et al. 1945, 308.5-384.7 K; bromine to Blair and Ihle 1973, 343-383 K; benzyl bromide to Stull 1947, 305.4-471.7 K); heats of vaporization (toluene 35.4 kJ/mol at 360 K, Rivenq 1975; bromine 29.8 at 358 K, Blair and Ihle; benzyl bromide 48.1 at 355 K, Ashcroft 1976); boiling points (toluene 383.8 +/- 0.2 K; benzyl bromide 471.7 K, Aldrich 1990, and 471 K); formation enthalpies of the liquids (toluene 12.0 kJ/mol, Prosen et al. 1945; benzyl bromide 16 +/- 2, Ashcroft, Carson et al. 1963, with 22 and 30 +/- 14 also listed); benzal bromide: only a reduced-pressure boiling point, 429.2 K at 0.031 bar (Weast and Grasselli 1989); toluene's liquid heat capacity about 157 J/(mol K) at 298 K | read | materials.yaml, reactions.yaml, D-005, D-007 |
| SRC-3 | PubChem CID 7498 (benzyl bromide), CID 24408 (bromine), CID 1140 (toluene) | benzyl bromide: identity (C7H7Br, InChIKey AGEZXYOZHKGVCM-UHFFFAOYSA-N); HSDB methods of manufacturing: toluene brominated under ultraviolet light (citing the Merck Index 2013), toluene bromination or benzyl alcohol with HBr (citing Hawley's 15th ed.), dibenzyl ether with bromine; boiling point 198-201 C, density 1.438 at 20 C, flash point 79-86 C closed cup; a lachrymator; decomposes slowly with water to HBr, attacks most metals when moist releasing heat and HBr, reacts violently with bases, magnesium and strong oxidants; GHS H315, H319, H335. Bromine: GHS H314, H330 (fatal if inhaled), H400. Toluene: flash point 4 C closed cup, lower explosive limit 1.1 vol%, autoignition temperature 480 C | read (PUG REST, PUG View; toluene 2026-11-06); the Merck Index and Hawley's are cited through HSDB, not read | D-001, D-011, registry |
| SRC-4 | The `chemicals` 1.5.2 package (Caleb Bell, MIT licence): its packaged CRC Handbook tables (`CRC_organic_data`, `CRC_inorganic_data` densities and melting points, `CRC_standard_data` heat capacities and formation enthalpies) and its critical constants with COSTALD | toluene COSTALD volume at 363 K, 0.1156 m3/kmol; densities: bromine 3102.8, benzyl bromide 1438.0, benzal bromide 1836.5 kg/m3; heat capacities: toluene 157.3, bromine 75.7 J/(mol K) (liquid), HBr 29.1 (gas); HBr (g) formation enthalpy -36.3 kJ/mol; melting point of bromine 265.95 K | open data package queried (2026-11-06); the CRC values are the tables packaged in `chemicals`, not the printed (licensed) handbook | materials.yaml, D-005, D-008 |
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
ASSUMED. Product in the model: 98.3 wt% benzyl bromide, 1.6 wt% benzal bromide, 0.1 wt%
toluene (D-007). **The 98.3 wt% is an upper bound**: ring-brominated toluenes (Fe or other
Lewis-acid traces, SRC-1), the dibenzyl and polybenzyl condensation products, dissolved HBr and
water are not modelled.
Reason: no open market or plant figure was used; a thousand tonnes a year is a plausible size
for a dedicated batch train of a fine benzylating agent. The LCI is per kg and does not depend
on the scale; the batch size does (D-003).

## D-003 Batch basis and recipe (2026-11-06)
Decision: one batch makes 889.6 kg of distilled benzyl bromide (stream S15); the recipe
(`process/recipe.yaml`) has two unit procedures: REACT on R-101 (`units: [E101, R101]`: nitrogen
purge, charge the toluene, heat 0.30 h to 363 K from the jacket, dose 5 h and react 0.25 h to
0.999 conversion of the bromine, both from R101's model, sample, transfer: 7.046 h) and DISTIL on
C-101 (`units: [ST101, ST102]`: receive, strip 1.15 h from ST101's boil-up, evacuate, forerun and
main cut 1.20 h from ST102's, cool and break the vacuum, drain: 3.85 h). R-101 is the bottleneck:
cycle time 7.046 h, 1124 batches in 7920 h; one batch takes 10.40 h from the purge to the
residue's drain. The flowsheet's flows are the year averages of the recipe: 889.6 kg x 1124.1 /
7920 h = 126.26 kg/h of S15; `cheme process recipe` checks this (no `cheme.recipe-basis`
finding).
Per batch: 2468 kg of toluene charge (78 % of it recycled), 923 kg (5.78 kmol) of bromine
dosed, 467 kg of HBr off, 2924 kg (2.98 m3) of crude at the end of the dosing. The recipe sizes
R-101 from R101's model (core ADR 0052, fill fraction 0.8 and H/D 1.2 ASSUMED): a 4 m3 vessel (the
R10 preferred size), 75 % full, 1.62 m diameter; its jacket on a tempered-water loop (U 300
W/(m2 K), the cooling water's mean of 303 K over its 298 K supply and 308 K return, ASSUMED)
removes 166.9 kW at the charge's 9.27 m2 against the model's 10.3 kW peak, to which the absorbed
light adds 6 kW and the agitator 3 kW (D-009). C-101 (4 m3, D-007) is busy 55 % of the cycle
at core's constant boil-up, 68 % with the boil-up its jacket allows as the pot empties (D-007).

## D-004 Feeds and charge (2026-11-06)
Decision: 4.0 mol of toluene in R-101's charge per mol of bromine dosed (the recycle's toluene
counted), ASSUMED; the bromine scaled by scripts/balance.py for 1000 t/a, the toluene make-up the
rest of the charge's toluene. Bromine 100 % (bromine-1 makes 99.96 wt%; its chlorine would give
benzyl chloride), toluene 100 %, both ASSUMED pure.
Reason: an excess of toluene keeps the benzyl bromide dilute, so the series bromination to benzal
bromide stays low; the excess is recovered by distillation (D-007). At 3 mol per mol (tried in a
scratch copy, with the strip, forerun and purge of D-007) the yield on bromine was 85.0 % against
88.5 % at 4; more toluene means a larger strip and recycle. SRC-1's Example I runs the other way (bromine in
excess, 1.2 mol per mol), with a different initiation.

## D-005 Reactor R-101: semi-batch photoreactor with an HBr vent, rate and heat (2026-11-06)
Decision: R101 is `reactor: semibatch` (core ADR 0050): the toluene charge S4 at 363.15 K, the
bromine S5 (298.15 K) dosed at a constant rate over 5 h, then the post-reaction to 0.999
conversion of the bromine (`batch.target`; 0.25 h from the model), isothermal at 363.15 K and
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
of photons), the 5 h dosing (0.321 mol/s of bromine) needs 4.57 kW of light (285 kJ per mol of
photons at 420 nm): a 31 % margin. k1 is chosen so that the bromine reacts about as fast as it
is dosed (accumulation 1.7 %, D-011), which is what lamps with that margin give; the dosing time
is the photon budget's, not the jacket's. Both the quantum yield and the light share are
unmeasured here: a photoreactor test must give them (SRC-1: light penetrates only a short way).
Temperature: 363 K, ASSUMED, below the toluene's boiling point. Rejected: the reaction at the
toluene's reflux (about 384 K, as issue #139 suggests): there the HBr would carry about 50 mol of
toluene vapour per mol (Raoult: the content's vapour pressure is then nearly 101 kPa), the
temperature would follow the rising bubble point (386 K at the start, 396 K at the end), which
core's isothermal semi-batch cannot follow (L-2), and the MTT would equal the process
temperature. At 363 K the HBr still carries 0.62 to 0.98 mol of organic vapour per mol, which a
reflux condenser returns (D-008), so the batch runs under reflux of its off-gas, not at the boil.
Heat of BNBR: -32.3 kJ/mol with HBr as gas, from the formation enthalpies (SRC-2: benzyl bromide
16, toluene 12.0; SRC-4: HBr -36.3 kJ/mol), the most exothermic of the three NIST values for
benzyl bromide; BALBR ASSUMED the same. Vented whole, HBr needs no liquid data (core ADR 0054).
The third bromination, to benzotribromide, is not modelled: it needs benzal bromide, which is
1.1 mol% of the crude, against 70 mol% toluene and 29 mol% benzyl bromide; with a k3 no larger
than k2 its rate is at most 1.1/29 = 0.037 of BALBR's at the end of the batch and less before,
so it would take below 0.2 % of the bromine (0.037 x the 4.5 % that BALBR takes).
Off-gas (`cheme process recipe`): 467 kg (5.78 kmol) of HBr a batch, peak 0.32 mol/s, 34 m3/h
at 363 K and 101 kPa(a), 0.76 h into the dosing; the condensers and A-101 are sized for it.

## D-006 Balance method and property gate (2026-11-06)
Decision: cheme propagates the charge mixer M101, the heat-up E101, the semi-batch R101 with both
outlets, the condensers E102 and E103 (pass-through), the absorber A101, the stills ST101 and
ST102 (D-007), the recycle mixer M201 and the splitter SP201. scripts/balance.py gives what core
has no model for (library ADR 0027): the bromine S5 and the toluene make-up S1 that make 1000 t/a
at 4 mol per mol (core propagates from the feeds and does not solve them for a product rate); the
recycle S2 at its fixed point, 0.98 of the recovered toluene S17 (core does not tear a recycle:
S2 is an assumed stream, and the script and `cheme process propagate --fill` were run in turn,
14 passes, until S2 moved by less than 0.01 kg/h); the absorber water S10; the temperatures that
follow from mixing (S3 from S1 and S2, S17 from S12 and S14, S2 and S18 as S17) or from a bubble
point (S13, the strip's end, by Raoult as the still); the duties Q1 to Q11 and the lamps' P1
(D-009). It reads the streams propagate wrote and the data of materials.yaml, and follows the
balance-output contract (`scripts/check_balance_scripts.py`: 22 values checked).
Reason: no property package of core covers these liquids (bromine and HBr in aromatics, HBr in
water), so the heats are heat capacities and latent heats in the script.

## D-007 Batch stills ST101 and ST102 in C-101, the toluene recycle and the product (2026-11-06)
Decision: one batch still, C-101 (4 m3, glass-lined, LP steam jacket), two core still steps in
it (`still:`, core ADR 0055), both one Rayleigh stage on Raoult's law with the NIST Antoine
constants of toluene, bromine and benzyl bromide (SRC-2) and an ASSUMED line for benzal bromide
(through its one measured point, 429.2 K at 3.1 kPa, with an ASSUMED heat of vaporization of 55
kJ/mol, so a relative volatility of benzyl bromide to benzal bromide of about 15 at 365 K; 12 at
50 kJ/mol, 19 at 60):
- ST101, the toluene strip at 15 kPa(a), boil-up 150 kW, until toluene is 15 mol% of the pot:
  1661 kg of distillate a batch (95.0 mol% toluene, 5.0 mol% benzyl bromide), the pot from 336.4
  to 373.8 K, 1.15 h;
- ST102 at 2 kPa(a), boil-up 80 kW, two cuts (`cuts:`): a forerun until toluene is 0.2 mol% of
  the pot (304 kg, 50 mol% toluene, 50 mol% benzyl bromide), then the main cut until benzyl
  bromide is 35 mol% of the residue: 889.6 kg of product (98.66 mol%, 98.3 wt% benzyl bromide,
  1.6 wt% benzal bromide, 0.1 wt% toluene), the pot from 321.4 to 376.8 K, 1.20 h; residue 68.7
  kg (65 mol% benzal bromide), drained after cooling to 333 K to incineration.
The strip distillate and the forerun go to T-201 (S17, 1966 kg a batch) and back to the next
charge; 2 % of it is purged (S18, 39 kg a batch, 44 g per kg of product, ASSUMED) so that what
the model does not carry (water, ring-brominated toluenes, the toluene's own impurities) cannot
build up. The purge carries 17 wt% benzyl bromide: 1.0 kg/h, 0.8 % of the product.
Reason: the strip is what the still model is for (a one-stage solvent strip, ADR 0055). A single
stage cannot strip deep without boiling up benzyl bromide: stripping to 3 mol% toluene at 30
kPa (tried in a scratch copy, at 3 mol of toluene per mol and a 5 % purge) sent 11.7 mol% benzyl
bromide into the distillate and the pot to 421 K, above the LP steam less its approach; the
recycled benzyl bromide is brominated again in R-101 (yield on bromine 79.8 %). Hence the
shallow strip at 15 kPa and the forerun at 2 kPa, where the relative volatility of toluene to
benzyl bromide is about 28 (at 330 K) against 17 at the strip's end (374 K, NIST Antoine).
**The product cut by one stage is credible here** because the heavy is far less volatile (alpha
about 15): one stage gives 98.66 mol% at 98 % recovery of the benzyl bromide the forerun leaves
in the pot, the grade of a technical benzyl bromide; a higher grade, or a ring-brominated impurity
(close-boiling, not modelled), needs a column with reflux (core#173, L-4). The recycle is a
batch-to-batch recycle; its year average is the fixed point of D-006.
Not modelled (L-4, L-5, L-6): the crude arrives at 363 K, above its 336 K bubble point at 15
kPa, and the stripped crude at 374 K, above its 321 K bubble point at 2 kPa, so part flashes as
the still is evacuated (counted as a sensible-heat credit in Q7 and Q9, D-009, not in core's
boil-up time); the dissolved HBr the crude holds (none in the model, D-005) would leave first, to
the vacuum system; the jacket's area falls as the pot empties, so the constant boil-up is
optimistic; the condensers and the vacuum system are sized by hand.
**The end of the main cut cannot run at 80 kW.** The residue, 68.7 kg (35 mol% benzyl bromide,
65 mol% benzal bromide, about 1.6-1.7 kg/L), is about 0.04 m3 at the end of ST102: it sits well
inside C-101's dished bottom (about 0.42 m3 for a DIN 28011 end of 1.62 m), the jacket is wetted
on about 0.9 m2 only, and at U 300 W/(m2 K) (ASSUMED, as R-101's) and the steam's 421 K it gives
about 12.5 kW, 16 % of the stated boil-up. scripts/still_jacket.py repeats both stills with the
boil-up capped at the jacket's duty for the wetted area: ST101 takes 1.37 h instead of 1.15 h
(its end, 0.97 m3, at 62 kW against 150 kW), ST102 1.92 h instead of 1.20 h, so C-101 is 0.93 h
longer a batch. Decision: keep the cut to the 35 mol% residue in C-101, the end of it at the
falling boil-up the jacket allows. C-101 is then busy 4.78 h of the 7.05 h cycle (68 % instead
of 55 %), so R-101 stays the bottleneck: the batches a year, the year-average streams and the
duties (energy per batch, not per hour) do not change; one batch takes about 11.3 h end to end
instead of 10.40 h, and the residue is held hot about 0.7 h longer (its TD24 is open, D-011).
Rejected: ending the main cut at a larger heel (at 0.4 m3 the pot still holds more than half of
the benzyl bromide the cut is meant to take, and carrying a hot heel over to the next batch needs the
residue's TD24); a smaller still or receiver for the cut (a second vessel and a transfer for 0.7
h saved on a vessel that is not the bottleneck). The recipe keeps core's constant-boil-up times
(L-6).
Rejected: a specified split for the strip or the product (a stated column, core#173) where one
stage does the work; distilling the forerun with the strip at 15 kPa (it would need the pot
above 421 K).

## D-008 Off-gas: reflux condenser, vent condenser and HBr absorption (2026-11-06)
Decision: the HBr off-gas S7 (66.34 kg/h year average) passes E-102, a reflux condenser on
cooling water (gas out at 303 K), and E-103, a vent condenser on brine (gas out at 268 K), and is
absorbed in process water to 48 wt% hydrobromic acid in A-101, a falling-film absorber with a
water tail scrubber (a mixer in the model, all HBr absorbed): 71.87 kg/h of water, 138.21 kg/h
of acid (1.095 kg per kg of product, 0.525 kg of HBr), the acid at 313 K. Heat of solution
-72.0 kJ/mol (SRC-5, ASSUMED there), less the gas's and the water's warming.
The organics the HBr carries: at 363 K the content's vapour pressure (Raoult) is 50.2 kPa at the
start and 38.9 kPa at the end of the batch, so 0.983 and 0.623 mol of vapour (mostly toluene) per
mol of HBr, 0.803 as their mean (ASSUMED linear); E-102 condenses it down to toluene's vapour
pressure at 303 K (0.051 mol per mol) and E-103 down to that at 268 K (0.0064 mol per mol); both
condensates return to R-101. What passes E-103, 0.037 kmol (3.4 kg) of toluene a batch, 3.8 g
per kg of product, is not in the balance (core's vent carries only HBr, L-3): an emission
exclusion with its number (lca.yaml `vent-toluene`), for basic engineering (an organic phase on
the acid or a tail-gas adsorber).
Reason: the acid is the saleable form of half the bromine (D-012); 48 wt% is hydrogen-bromide-1's
product grade. The brine stage is needed because 5 mol% of toluene in the HBr would otherwise
reach the acid (27 kg a batch). The vent gas stays at 268 K, above bromine's melting point of
266 K (SRC-4); the bromine in the condensate is a dilute solution in toluene and does not freeze.
Not modelled: the bromine vapour the HBr carries (the content holds at most 0.4 mol% bromine at
the end of the dosing, D-011) and the bromine the acid takes up (it colours the acid); the acid's
organic carbon.

## D-009 Utilities and heat: every energy flow (2026-11-06)
Decision (scripts/balance.py, year averages, kW; per kg of product in kWh; all ASSUMED unless
sourced):
- Q1 11.28 (0.089) of LP steam 450 kPa(a) to R-101's jacket: the charge S3 from its mixing
  temperature of 298.6 K (S1 at 298 K, S2 at 298.8 K) to 363.15 K, 10 % losses; 0.30 h from the
  jacket (`cheme process recipe`).
- Q2 5.46 (0.043) from R-101's jacket to cooling water through a tempered-water loop: the heat of
  the reactions (7.36), the light the content absorbs (4.47) and the agitator (3.0), less the
  bromine's warming from 298 to 363 K (1.12) and the toluene the HBr evaporates, its latent heat
  and the reheating of its condensate returned at 303 and 268 K (8.24).
- Q3 10.43 (0.083) from the lamp wells to cooling water: the lamps' electricity less the light
  (70 % of P1).
- Q4 8.16 (0.065) from E-102 to cooling water: the vapour of D-008 condensed and cooled from 363
  to 303 K, the HBr and the uncondensed toluene cooled.
- Q5 0.65 (0.005) from E-103 to brine: the toluene condensed from 303 to 268 K, the gas cooled.
- Q6 14.85 (0.118) from A-101 to cooling water: HBr from gas at 268 K to 48 wt% acid at 313 K.
- Q7 20.21 (0.160) of LP steam to ST101: the latent heat of S12 less the crude's sensible heat
  above its bubble point (363.15 - 336.4 K); 150 kW while stripping.
- Q8 27.36 (0.217) from ST101's condenser to cooling water: S12 condensed at 15 kPa(a) and cooled
  from its 329 K bubble point to 303 K; about 167 kW while stripping.
- Q9 10.78 (0.085) of LP steam to ST102: the latent heat of S14 and S15 less S13's sensible heat
  between its bubble points at 15 and 2 kPa(a) (373.8 - 321.4 K); 80 kW while distilling.
- Q10 4.28 (0.034) from ST102's forerun condenser to brine: S14 condensed at 2 kPa(a) (its
  bubble point there is 298.7 K, below the cooling water) and cooled to 268 K; about 90 kW over
  the forerun's 0.34 h.
- Q11 11.82 (0.094) to cooling water: the main cut S15 condensed at 2 kPa(a) and cooled from 354.5
  to 303 K, the residue S16 cooled in C-101 from 376.8 to 333 K.
- P1 14.90 (0.118) for the lamps (20 kW for the 5.25 h of light a batch), P2 3.0 (0.024) for
  R-101's agitator, P3 1.84 (0.015) for C-101's agitator (1.5 kW) and dry vacuum pump (4 kW)
  while distilling, 2.35 h a batch.
Totals per kg: cooling water 0.618 kWh, brine 0.039 kWh, LP steam 0.335 kWh, electricity 0.156
kWh. The jackets are checked against the cooling water's mean temperature (303 K), and LP steam
at 421 K is the hottest medium; no decomposition onset of benzyl bromide or of the residue is
open, so the TD24 or DSC onset of both must lie above the 421 K wall (D-011), else the still and
the heat-up need hot water.
Recorded exclusions, each with its number:
- the heat of mixing of bromine into toluene: not known openly; at an ASSUMED 5 kJ/mol it would
  be 1.1 kW (0.009 kWh/kg) more on R-101's jacket;
- the still agitator's 1.5 kW while distilling (0.50 kW year average) goes into the pot and would
  save as much steam; the vacuum pump's 4 kW (1.34 kW year average) leaves with its own air
  cooling;
- heat losses of R-101 while dosing and of C-101 (only the heat-up carries 10 %); the
  brine's and the cooling water's own electricity (chiller, pumps, tower) are in their LCI
  backgrounds (D-012).

## D-010 Yields against the source (2026-11-06)
Decision: the model's yields are 88.5 % of theory on the bromine (mol of benzyl bromide in S15
per mol of bromine dosed; HBr takes the other half of the bromine) and 86.9 % on the toluene
make-up S1 (1.038 kg of bromine and 0.609 kg of toluene per kg of product; stoichiometric 0.934
and 0.539). **The modelled yield on toluene is below the source's**: SRC-1, Example I, gives about
90 % on toluene, under X-rays with bromine in excess. The yields follow from the ASSUMED k2/k1 and
from the separations, so they are not predictions: in scratch copies at the recycle's fixed point,
k2/k1 = 0.1 gives 93.5 % on the bromine (99.1 mol% product) and 0.4 gives 79.9 % (97.9 mol%).
Both are upper bounds in one respect: ring bromination and the condensation of benzyl bromide
are not modelled.

## D-011 Thermal screening, the rate-constant sensitivity and the hazards (2026-11-06)
Result (`cheme process reactor-hazards`, core ADR 0050, 0054): adiabatic temperature rise of the
whole batch 42.2 K (with -32.3 kJ/mol); largest accumulation of the dosed bromine 1.73 %, at the
end of the dosing; MTSR at that moment 363.9 K, against an MTT of 383.8 K (`hazard.mtt`: the
normal boiling point of toluene, the liquid's main component; core's default, the lowest boiling
point of the charge and the dose, would be bromine's 331.95 K, a dose that does not stay as such
in the liquid: L-5). The content's bubble point by Raoult is 386.4 K at the start and 394.9 K at
the worst moment (with the 0.4 mol% bromine accumulated), so 383.8 K is a lower bound in the
design case. The vented HBr adds nothing to the MTSR; with the vent blocked it pressurises the
vessel, which the screening does not assess (core note: a peak of 0.11 mol/(s m3) of the final
content).
No TD24 is known (never estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
With MTSR below MTT the class is 1 or 2 if the TD24 lies above the MTSR, and 5 if it lies below
(TD24 < 363.9 K: core's `criticality()` and Stoessel test the TD24 against the MTSR first,
SRC-6); it needs the TD24.
Sensitivity (a scratch copy of the folder, both A divided, everything else as designed;
`cheme process propagate --fill`, `reactor-hazards`, `reactors`, `recipe`):

| k at 363 K | accumulation (end of dosing) | MTSR | MTSR vs MTT 383.8 K | post-reaction to 0.999 | cycle, batches/a | class without TD24 |
|---|---|---|---|---|---|---|
| 5.0e-4 (design) | 1.73 % | 363.9 K | 19.9 K below | 0.25 h | 7.05 h, 1124 | 1, 2 or 5 |
| k/10 | 16.4 % | 370.5 K | 13.3 K below | 4.42 h | 11.21 h, 706 | 1, 2 or 5 |
| k/100 | 73.1 % | 394.6 K | 10.8 K above | 56.5 h | 63.3 h, 125 | 3, 4 or 5 |

Interpretation: all at once (accumulation 1) the MTSR would be about 405 K, above the boiling
point of toluene, so the dosing, not the dilution, keeps it below the MTT. **For a photoreactor
the slow cases are the lamp-failure cases**: weak, fouled or failed lamps (or a bromine-coloured
light path, SRC-1) slow the chain like a smaller k, and in the dark the bromine accumulates while
it is dosed; when the light comes back the accumulated bromine reacts at once, with its HBr. At
k/100 the content holds about 14 mol% bromine at the end of the dosing (4.2 kmol in 29.3 kmol of
liquid: the 25.1 kmol charge plus the 5.78 kmol dosed less the 1.55 kmol reacted, each reaction
taking one mole out of the liquid as its HBr is vented), which lowers its bubble point to about
372 K (Raoult, the bromine's Antoine extrapolated), so the margin is smaller still than the
table's MTT shows. The bromine dosing must therefore be interlocked with the lamps' power and
light sensors, the temperature, the agitator and the HBr off-gas flow: HBr forms only as the
bromine reacts, so dosing without off-gas means bromine accumulating. At k/100 the cycle (63 h)
rules out the design before safety does. Open for the next stage: a photoreactor test with
reaction calorimetry and off-gas measurement (rate against light, quantum yield, the dark rate),
the TD24 of the crude, the product and the residue (benzyl halides condense with HBr evolution in
contact with iron and other metals, SRC-3), the gas-generation pressure with a blocked vent
(Stoessel's separate criterion). Screening values only, not a reaction-hazard assessment.
Open, toxic gases, water and the scrubber (reasoning only, for the HAZOP):
(a) Loss of the absorber water while R-101 doses: up to 0.32 mol/s of HBr (and the bromine
vapour with it) to the tail scrubber or to air. Stopping the bromine and the lamps stops the HBr
within the chain's dark lifetime; the 1.73 % accumulated bromine (0.10 kmol, 16 kg a batch)
stays in R-101 and gives at most 0.10 kmol (8 kg) of HBr if the light comes back. The dosing and
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
point (79-86 C) is passed too, here and in C-101. The off-gas carries 0.6 to 1.0 mol of toluene
vapour per mol of HBr (D-005), far above toluene's lower explosive limit of 1.1 vol% (SRC-3): with
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
(66.340 kg/h, counted as the HBr it contains): 0.6556 and 0.3444 (lca.yaml `allocation`, agent
proposal). No physical relationship is clear and no price is sourced, so the WBCSD rule of
docs/system-model.md falls back to mass (docs/registry.md). Rejected: shares 1/0 (as
benzoyl-chloride-1 gives its hydrochloric acid): half the bromine leaves in the acid, a
bromine product sold at a price far closer to the main product's than hydrochloric acid's;
substitution of hydrogen-bromide-1's acid, which belongs to the substitution variant database,
not to this cut-off dataset (library ADR 0007), recorded as the variant to compare.
Per kg of benzyl bromide (unallocated): bromine 1.038 kg, toluene 0.609 kg, process water 0.569
kg, nitrogen 28 g, electricity 0.156 kWh, LP steam 0.335 kWh, cooling water 0.618 kWh and brine
0.039 kWh removed; out: 48 wt% acid 1.095 kg, residue 77 g and toluene purge 44 g to incineration.
Not counted: the vents (emission_exclusions, the vent toluene with its 3.8 g/kg).

## D-013 Dedicated train (2026-11-06)
Decision: R-101, E-102, E-103, A-101, C-101 and T-201 make only benzyl bromide, batch after
batch: 1124 batches in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns.
Out of scope, so not LCI gaps: changeover cleaning between campaigns, the idle time of a
multipurpose train, shared tank farms.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with its HBr vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas rate | done in cheme, effective rate ASSUMED | D-005, D-011, core ADRs 0050, 0054 |
| photon budget of the lamps | hand (script), quantum yield ASSUMED | D-005, L-1 |
| batch recipe, cycle time, basis check, R-101's vessel and jacket | done in cheme | D-003, core ADRs 0051, 0052, 0057 |
| stills ST101, ST102 (one stage, two cuts): distillates, residue, boil-up times, latent heat | done in cheme, ideal liquid and benzal bromide's vapour pressure ASSUMED | D-007, core ADR 0055 |
| C-101's jacket against the stills' constant boil-up (wetted area as the pot empties) | hand (scripts/still_jacket.py), U and the head's shape ASSUMED | D-007, L-6 |
| toluene recycle at its fixed point | script and propagate in turn | D-006, L-7 |
| feeds for 1000 t/a, absorber water, mixing and bubble-point temperatures, duties Q1 to Q11, P1 | script | D-006, D-008, D-009 |
| off-gas organics (reflux and vent condensers) | hand (script), not in the balance | D-008, L-3 |
| per-batch nitrogen | done in cheme, amount ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Core features used (cheme-as-code 1.8.0)

| feature | where | ADR |
|---|---|---|
| `reactor: semibatch` with `batch.dosing` and `batch.target` | R101 (bromine dosed into the toluene) | 0050 |
| `batch.vent` | R101 (all HBr) | 0054 |
| recipe vent report (peak kmol/s, m3/h, kg per batch) | the condensers' and absorber's load, D-005, D-008 | 0054 |
| `hazard.mtt` and the screening of a vented semi-batch | R101, D-011 | 0050, 0054 |
| `still:` with Raoult's law (Antoine `vapour_pressure`, `heat_of_vaporization`), `boilup` in kW, `end: residue` | ST101 | 0055 |
| `still:` with `cuts:` (forerun and main cut) | ST102 | 0055 |
| recipe `distil from:` and `units:` (one vessel over several steps) | C-101 (ST101, ST102), R-101 (E101, R101) | 0055, 0057 |
| vessel sizing and jacket check, `heat` time from the jacket | R-101 | 0052 |
| per-batch LCA consumables, `allocation: shares` | nitrogen; the acid | 0053 |
| splitter and mixers in propagate | the toluene recycle and purge | - |

Not used, not needed by this route: `dosing.absorbed` (no gas is dosed), the crystallizer, the
filter and the dryer (no solids), `still.feed` (no solvent swap).

## Core limits hit (each a candidate core issue)

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
  carries 0.6 to 1.0 mol of toluene vapour per mol, condensed and returned in E-102 and E-103:
  their duties, the evaporative cooling of R-101 and the toluene left in the vent (3.8 g/kg) are
  script values outside the balance. Core needs the solvent vapour in the off-gas from the
  vessel's VLE, with a partial (reflux) condenser on the vent (as benzoyl-chloride-1's L-2).
- L-4 (core#173): no batch rectification with reflux; the strip has to stay shallow (D-007) and
  the product's purity rests on the heavy's large volatility; a higher grade needs a column.
- L-5: the default MTT is the lowest boiling point of the charge and the doses (here bromine's
  332 K, below the process temperature); it ignores that the dose reacts and that the content is
  a mixture. `hazard.mtt` was set by hand; core could give the content's bubble point at the
  worst moment from its Antoine data (D-011: 394.9 K design, about 372 K at k/100).
- L-6 (ADR 0055): the still has no heat-up, flash or sensible heat of a charge hotter than its
  bubble point (both charges here), a constant boil-up whatever the wetted jacket area, and does
  not size its vessel, jacket, condensers or vacuum system: C-101 is sized by hand, and Q7 and Q9
  carry the flash credit that core's boil-up time does not. Here the residue at the end of ST102
  (about 0.04 m3) wets only about 0.9 m2 of jacket, about 12.5 kW against the 80 kW boil-up; the
  jacket-limited times (scripts/still_jacket.py, D-007) are 0.93 h a batch longer than core's.
  Core needs the boil-up from U, the wetted jacket area of the vessel and the steam temperature.
- L-7: core propagates from the feeds and cannot solve them for a product rate, and does not tear
  a recycle: the script scales the feeds and brings the toluene recycle to its fixed point by
  passes of propagate and the script (as n-bromosuccinimide-1's L-6).
- L-8: an isothermal semi-batch reports its peak cooling duty and the heat released, but no
  year-average duty for its energy stream; Q2 comes from the script with the same data the model
  uses.
- L-9 (ADR 0055): an ideal liquid only, and a component needs an Antoine equation or a constant
  alpha for the whole still: benzal bromide has one measured point, so its line is ASSUMED and
  the stills' basis is "not sourced".

## Open inputs
Photoreactor test: rate against light, quantum yield, dark rate, the heat of reaction and the
bromine's heat of mixing by calorimetry with off-gas measurement; the relative rate k2/k1 and the
ring-bromination share; the TD24 or DSC onset of the crude, the product and the residue; HBr
solubility in toluene at 363 K; VLE of toluene with benzyl bromide and of benzyl bromide with
benzal bromide; benzal bromide's vapour pressure; the product specification; the purge's need;
the vent's toluene and bromine and the acid's quality; prices for the allocation; a TEA
(`operation.batch: {recipe: true}`).
