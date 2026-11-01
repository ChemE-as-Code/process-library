# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Formic acid by methanol carbonylation and methyl formate hydrolysis, issue
ChemE-as-Code/process-library#185. Concept stage: design basis, balanced BFD/PFD and a
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-10-28): branch `case/formic-acid-1` from library commit 57b916c,
cheme-as-code 0.8.0 (pyDEXPI 2.1.0). The core issues on property qualification and on extraction could not be opened from this
session (`gh` does not resolve them); their state is taken from the issue comments (property qualification open;
extraction closed by `cheme process extract`, qualified only for water / 1-propanol /
n-butyl acetate). The route chosen here needs no extraction, so that issue does not gate it (D-004).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage given was read
in this session (through the Google Patents text, which has no paragraph numbers: the locator is
the section).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US4216339A, UCB SA (Couteau, Ramioulle), granted 1980-08-05: process for the production of methyl formate | description (70-110 C, preferably 75-85; 20-110 bar; 0.2-4 wt% alkali methoxide, preferably 0.4-2.5 %; CO/methanol 0.30-0.85 mol/mol; CO water < about 5 ppm, methanol < about 100 ppm; water forms sodium formate which precipitates and deactivates); equilibrium table (at 80 C the conversion limit rises from about 20 % at 20 bar to 85 % at 80 bar); Example 1 (80 C, 44 bar, pure CO: methanol conversion 30 % = 75 % of the about 40 % limit, CO yield 92 mol%, methanol yield practically quantitative, ester distilled off and the methanol with the catalyst recycled); Example 2 (36 % conversion cuts productivity, stay below 75-85 % of the limit); Example 3 (formate filtered from the recycle) | read; patent document (facts only) | D-005, D-007 |
| SRC-2 | EP2747883A1, Taminco BV (Pasek, Trejbal, Roose), published 2014-07-02: process of formic acid production by hydrolysis of methyl formate | background (hydrolysis K = 0.18-0.24; water/ester 0.8-7 in earlier processes; reverse esterification in the columns and decomposition to CO of earlier processes; prior-art reboiler duty about 2400 kWh per t of 85 % acid); description (hydrolysis 90-140 C, 2-7 bar, autocatalysed by formic acid, slow without it; decomposition to CO and water from about 140 C; fresh ester holds 4-6 % methanol, recovered ester up to 1-2 %; vacuum rectification at 8-20 kPa, preferably 10-13, at most about 60 C, giving 85-90 % acid overhead and 63-66 % bottoms recycled to the hydrolysis; about 2.5 t steam per t of 85 % acid for the invention) | read; patent document (facts only) | D-008, D-009, D-011 cross-check |
| SRC-3 | EP3661904B1 (A1 2020-06-10, B1 2026-01-07), Eastman Chemical Co.: formic acid using low-boiling formate esters | definitions (water / formic acid maximum-boiling azeotrope; water/acid mass ratios about 42/58 at 0.04 bar(a), 40/60 at 0.067, 25/75 at 1.013, 20/80 at 2.03, 17/83 at 3.04, 16/84 at 4.05); background (conventional pressure-swing distillation: high-pressure column takes water overhead and leaves the azeotrope, a low-pressure column gives 90-99 % acid overhead and recycles its bottoms; methyl formate hydrolysis only 25-30 % converted even at water/ester 2; 3-4 t ester recycled per t acid); examples (Kx 0.18; 32 % at water/ester 1.82 and 28 % at 1.42) | read (first 100 000 characters of the page); patent document (facts only) | D-004, D-008, D-009 |
| SRC-4 | US4299981: preparation of formic acid by hydrolysis of methyl formate | claims and abstract as returned by a web search (liquid-phase hydrolysis 90-140 C, 5-18 atm, a molar ratio of ester and water of 1.5-10 whose direction the search text leaves unclear (the reactions.yaml entry had it as MF/water; it covers the design's water/MF 1.5 only if it is water/ester); reactor sized for at least 95 % of equilibrium) | full text not read: an unverified lead, no value is taken from it as given (review R-05) | D-008 (95 % approach, ASSUMED) |
| SRC-5 | MDPI *Catalysts* 11 (2021) 869 (open access) | introduction, as summarised by a web search: conventional carbonylation with 2.5 wt% sodium methoxide at 80 C and 4.5 MPa, about 30 % methanol conversion, high selectivity | identified, not read in full | corroborates D-005 |
| SRC-6 | Formic Acid, *Ullmann's Encyclopedia of Industrial Chemistry*, doi:10.1002/14356007.a12_013.pub3 | - | not read (licensed); the issue's reference lead | none |
| SRC-7 | cheme chemistry thermo / props (chemicals and thermo packages: ATcT, CRC, Poling 5th ed., Thermo vapour pressures and heats of vaporization) | printed per component in process/materials.yaml and scripts/balance.py | open data packages | ideal-gas data, boiling points, vapour pressures at 313 K, heats of vaporization |
| SRC-8 | processes/methanol-1 (this library) | its methanol product | library, internal | methanol make-up link (D-003) |

The issue's handoff asked not to search for published "answers"; no benchmark plant figures or
published balances of this route were looked for or used. The prior-art energy figure of SRC-2
is used only as an order-of-magnitude cross-check (D-011), not as an input.

## D-001 Route and boundary (2026-10-28)
Decision: Formic acid by the two-step methyl formate route: liquid-phase carbonylation of
methanol over sodium methoxide (SRC-1), hydrolysis of the ester with water autocatalysed by
formic acid (SRC-2), distillative recovery and recycle of the unreacted ester and of the
methanol formed, concentration of the aqueous acid by pressure-swing distillation (SRC-3) to
85 wt%. The CO-rich vent of the carbonylation is burnt in a thermal oxidiser. Net reaction:
CO + H2O -> HCOOH; methanol is an intermediate recycled within the boundary, made up for losses.
Boundary feeds: CO, methanol, sodium methoxide solution, demineralised water, air, electricity,
LP steam; outputs: 85 wt% acid, spent catalyst purge, flue gas, heat to cooling water.
Reason: the case brief prescribes this route; it is the industrial methyl formate route of
every source read. Links to other library processes: methanol from methanol-1 (make-up only,
12.5 g/kg product); LP steam and cooling water from utility-steam-ng-boiler and
utility-cooling-tower (LCI gap notes). No library process makes pure CO yet (a syngas cold box
would).
Rejected: direct CO2 hydrogenation, oxidation of hydrocarbons (by-product formic acid) and the
formamide route: not in the brief.

## D-002 Capacity, product grade and hours (2026-10-28)
Decision: 6250 kg/h formic acid 85 wt% (5312.5 kg/h HCOOH; 50 kt/a at 8000 h), ASSUMED.
Reason: no traceable published plant basis is used (issue note); the LCI per kg is independent
of scale. 85 wt% is a common commercial grade (SRC-2 makes 85-90 %) and lies above the 75 wt%
azeotrope at 1 atm, so the concentration step has to cross the azeotrope (D-004). A 98-99 %
grade is possible with the same scheme (a purer C-302 distillate) at higher reflux; not
designed.

## D-003 Feed specifications (2026-10-28)
Decision: CO 99 mol%, impurities lumped as N2, at 303 K and 200 kPa(a), water-free (ASSUMED).
Methanol make-up taken as pure (AA grade). Catalyst as 30 wt% sodium methoxide in methanol
(ASSUMED, a commercial form). Demineralised water.
Reason: water and CO2 destroy the methoxide (SRC-1), so the CO must be dry; the supplier
specification of H2, CH4, CO2 and sulfur is an open input. Inerts pass to the vent (1 mol% N2
gives 11 mol% N2 in the vent).

## D-004 Concentration by pressure-swing distillation, not extraction (2026-10-28)
Decision: Two columns: C-301 at 203 kPa(a), water overhead, bottoms 77 wt% acid (the azeotrope
is about 80 wt% at 2.03 bar(a), SRC-3); C-302 at 12 kPa(a), product 85 wt% overhead, bottoms
66 wt% (SRC-2: 63-66 % at 10-13 kPa, consistent with SRC-3's about 60 % at 0.067 bar(a)),
recycled to the hydrolyser where it serves as the acid catalyst (as in SRC-2).
Reason: SRC-3 names pressure-swing distillation as the conventional separation, and it needs no
auxiliary solvent; an amide extraction (the other industrial option named in the brief) would
need an extraction model with sourced NRTL parameters that core qualifies only for another
system, plus a solvent inventory. C-301 is kept at 203 kPa(a) so that its
bottoms (about 403 K, not calculated) stay below the about 413 K at which the acid starts to
decompose (SRC-2).
Rejected: extractive distillation and amide extraction (energy-saving candidates for basic
engineering); a higher C-301 pressure (richer azeotrope, but hotter bottoms).

## D-005 Carbonylation model (2026-10-28)
Decision: R-101 is a conversion reactor: 30 % of the methanol converted per pass, CO fed at
methanol extent / 0.92 (92 mol% CO yield), 353 K, 4500 kPa(a), 2.5 wt% NaOMe in the liquid feed
(all from SRC-1 Example 1 and description; SRC-5 corroborates). The 8 % of the CO not converted
leaves with the vent (SRC-1 operates once-through on the gas, without CO recycle).
Heat of reaction -37.7 kJ/mol (liquid methanol and ester, CO gas) from the ideal-gas formation
enthalpies and the Thermo heats of vaporization at 298 K (SRC-7), ASSUMED derivation; the duty
(1.21 MW) goes to cooling water.
Reason: no open rate law for the commercial catalyst was found; SRC-1's example is a measured
operating point. Core's ideal-gas equilibrium check (`cheme process reactors`) gives
ln(Q/K) = +1.5 for the gas-phase reaction at the outlet: the gas-phase constant does not apply
to this liquid-phase reaction (SRC-1 gives a 40 % liquid-phase limit at these conditions), so it
is recorded as a limitation, not a finding. A CO recycle or a second stage on the vent (SRC-1
Example 6) would cut the CO use and the CO2 emission (0.072 kg/kg); a candidate for basic
engineering.

## D-006 Balance method and what core cannot evaluate (2026-10-28)
Decision: An independent script, scripts/balance.py (`cheme run scripts/balance.py`), solves
the recycles by direct substitution from the specified conversions and splits and gives every
separator outlet and duty; these enter the flowsheet as `assumed` with that source. `cheme
process propagate --fill` calculates the mixers, pumps, exchangers, the splitter SP101 and the
reactors R101, R201, X101 (conversion model); `cheme validate` checks every block and step
balance (all close; the carbonylation block within 0.01 kg/h).
Reason: no property package of core covers liquid methanol / methyl formate / water / formic
acid or the methoxide catalyst (`cheme process props --coverage`), DWSIM is not qualified for
this mixture and the liquid-reactor energy basis is not verified. The energy
balance of the blocks is therefore not evaluable in core (`cheme process energy`: stream
enthalpies missing); the duties are shortcut estimates (D-011). Gated step: a predictive
column and energy balance needs a qualified NRTL/UNIQUAC (or similar) package with vapour
association of formic acid.

## D-007 Carbonylation separation, catalyst loss and purge (2026-10-28)
Decision: The effluent is cooled to 313 K (E-101); V-101 sends all CO and N2 with methyl formate
and methanol vapour by Raoult's law (Thermo vapour pressures at 313 K) to the vent; dissolved CO
neglected in the split. Its size (review R-03), ASSUMED order of magnitude: CO solubility in
methanol about 3e-4 mole fraction per atm (reviewer's estimate, no source read) at a CO partial
pressure of about 38 atm gives x about 0.013 in the 393 kmol/h of S10, i.e. about 5 kmol/h CO
(140 kg/h, 22 g/kg product, half the vent CO) leaving dissolved and released at the C-101
condenser. The C-101 condenser vent must therefore go to X-101 (basic engineering): then the
CO burnt, the oxidiser CO2 and the LCI are unchanged, only the S9 / column-vent split is not
representative. Vented unburnt it would exceed the 1 % cut-off (13 g/kg), so it is not a
negligible exclusion but a routing requirement (`lca/lca.yaml` column-vents). C-101 (250 kPa(a), so that the ester condenses against cooling water) takes all the
ester overhead with 4 wt% methanol (SRC-2: fresh ester holds 4-6 %); its bottoms (methanol,
methoxide, sodium formate) are recycled, 1 % purged to incineration (ASSUMED purge fraction, no
source; sets the sodium formate level). Catalyst loss: all water reaching the reactor (the 100
ppm(wt) of the recycle methanol, SRC-1's limit) destroys methoxide to sodium formate (reaction
DEACT); make-up = destroyed + purged = 2.3 g of 30 wt% solution per kg product.
Assumptions: no other methoxide loss (CO2 in the CO would add one); the formate stays suspended
(SRC-1 Example 3) and leaves with the purge.

## D-008 Hydrolysis and ester / methanol recovery (2026-10-28)
Decision: R-201 at 393 K and 600 kPa(a), water/methyl formate 1.5 mol/mol at the inlet, the
recycled 66 wt% acid as catalyst. Conversion = 95 % (ASSUMED; SRC-4 is an unverified lead, its
full text not read, review R-05) of the equilibrium conversion of the
actual feed with Kx = 0.20 (mid of SRC-2's 0.18-0.24; SRC-3 gives 0.18): 28.9 % per pass, inside
SRC-3's 28-32 % at 1.42-1.82 and 25-30 % generally. The recycled ester (C-201 distillate,
17.0 t/h MF) is 3.2 t per t HCOOH, inside SRC-3's 3-4 t/t; the hydrolyser sees 24.0 t/h MF. Core confirms ln(Q/K) = -0.11
at the outlet with the given Kx. C-201 takes all the ester overhead with 2 wt% methanol (SRC-2),
C-202 dry methanol overhead (100 ppm water, SRC-1) back to the carbonylation; the 48.9 wt% acid
goes to C-301. Heat of hydrolysis +8 kJ/mol ASSUMED (nearly thermoneutral; core's ideal-gas
value is +20.1 kJ/mol, which does not apply to the liquid; no sourced liquid value was read:
open input, 0.26 MW of 27.9 MW steam either way).
Assumptions: reverse esterification in C-201/C-202 and decomposition of formic acid are
neglected (SRC-2 reports both as losses of earlier processes: an open risk for the yield);
splits sharp otherwise.

## D-009 Pressure-swing columns (2026-10-28)
Decision: see D-004. C-301 distillate: water with 0.5 wt% acid (ASSUMED), recycled to the
hydrolyser; its flow is what the water/ester ratio of 1.5 requires (the loop's water inventory
is a design variable, fixed by that ratio). The C-302 split follows the lever rule
85 / 77 / 66 wt%: 10.8 t/h feed, 4.5 t/h bottoms recycled. Product 85 wt% with no methanol or
ester (sharp C-202 split).

## D-010 Pressures, machines and the vent oxidiser (2026-10-28)
Decision: CO compressed 200 -> 4600 kPa(a) in K-101 (3 intercooled stages, isentropic 0.75,
motor 0.95, ideal gas: 470 kW); the methanolic feed pumped to 4600 kPa(a) (P-101, 34 kW) and the
hydrolyser feed to 650 kPa(a) (P-201, 7.5 kW), pump 0.60 and motor 0.95; stream pressures in
the flowsheet are an ASSUMED profile. X-101 burns the vent with twice the stoichiometric air,
99.9 % destruction of CO, ester and methanol (ASSUMED), adiabatic, no support fuel and no heat
recovery (`process/simulation.yaml`: mode adiabatic); its outlet temperature is not calculated.
The air fan is within the oxidiser package (not counted).
Open: NOx of the oxidiser (LCI exclusion), steam raising from the vent (it carries about
0.79 MW of CO heating value: 10 kmol/h x 283 kJ/mol).

## D-011 Utilities and shortcut duties (2026-10-28)
Decision: One steam level, LP 450 kPa(a) saturated (421 K), for every reboiler, the hydrolyser
feed preheater (340 -> 393 K, cp 3.0 kJ/(kg K)) and the hydrolysis heat; cooling water 298/308 K
for condensers, the reactor, the effluent cooler and the compressor intercoolers. Reboiler duty
= (R+1) x distillate x heat of vaporization (methyl formate 27.7, methanol 35.3, water 40.7,
formic acid 20.0 kJ/mol; SRC-7 or ASSUMED near the column top), condenser duty equal; reflux
ratios ASSUMED: C-101 1.0, C-201 1.0, C-202 1.5, C-301 2.4, C-302 1.5. Feed preheat in the
columns, heat losses and the product pump are not counted; vacuum system 15 kW allowance.
C-301 (review R-01): water / formic acid has a low relative volatility on the way to the
azeotrope, so its reflux is set from a minimum-reflux estimate, `scripts/c301_rmin.py`: Thermo
vapour pressures, ideal vapour (acid association not modelled), a one-parameter Margules liquid
fitted so that the azeotrope lies at 80 wt% acid at 203 kPa(a) (SRC-3; A = -0.81, 130.5 C),
saturated liquid feed. Relative volatility 1.69 at the feed (49 wt%); both sections pinch at the
feed, R_min = 1.96 (the earlier R = 1.0 was below it); R = 2.4 = 1.2 R_min ASSUMED. The estimate
is a shortcut on a fitted activity model, uncertain in both directions; a rigorous VLE basis
replaces it (D-014). E-201 duty from the S19 temperature 340 K (review R-02).
Result: 27.9 MW LP steam heat (4.46 kWh/kg product; C-301 13.3 MW of it), 28.0 MW to cooling
water, 0.53 MW power.
Cross-check: SRC-2 quotes about 2400 kWh/t of 85 % acid for the reboilers of prior art; the
shortcut is about 1.9 times that, plausibly because there is no heat integration (a feed-effluent
exchanger at R-201, condensing the C-301 vapour in another reboiler, vapour recompression) and
the other reflux ratios are not optimised. Not a conservative bound: the C-301 term rests on a
fitted VLE model and the other reflux ratios are not checked against their minima; the steam
figure is uncertain in both directions until a rigorous column design (gated, D-006).

## D-012 Preliminary gate-to-gate LCI (2026-10-28)
Decision: `lca/lca.yaml`: functional unit 1 kg formic acid 85 wt% at the gate (stream S28);
every foreground exchange from the balanced flowsheet (feeds S1, S3, S4, S17, S15; utilities
Q1-Q19; purge S14; flue gas S16 split into its components). Every background is left unmapped
(`missing:` with the activity it should connect to): 8 declared gaps, never zero, no licensed
values. The oxidiser's CO2 (fossil), CO, methyl formate and methanol go to air as elementary
flows; the method (IPCC 2021 GWP100) has no factor for CO, methyl formate and methanol (3
uncharacterised gaps). The boundary key is `cradle-to-gate` so that the purchased inputs stay
open gaps (the schema's gate-to-gate would map them free), as phosgene-1 does. Exclusions with
reasons: oxidiser NOx, fugitive emissions (no P&ID), column vents (dissolved CO neglected),
formic acid decomposition. Construction, transport and end of life not included.
Result (`cheme assess lca --coverage`): mass, element and carbon-origin balances closed (inputs
1.3009 kg = outputs 1.3009 kg per kg product); no impact totals (every background a gap).
Per kg product: stoichiometric 0.517 kg CO; 0.568 kg of 99 mol% gas at 92 % CO yield; methanol
12.5 g, NaOMe solution 2.3 g, water 0.483 kg (0.333 kg reacted + 0.150 kg in the product), air
0.235 kg, power 0.084 kWh, LP steam 4.46 kWh, cooling water 4.49 kWh, purge 14.1 g, CO2 72.4 g.
Exclusions with ASSUMED bounds (review R-07, in `lca/lca.yaml`): oxidiser NOx about 0.02 g/kg,
decomposition CO at most about 2.6 g/kg (burnt in X-101), column vents about 22 g/kg CO but
routed to X-101 and so already counted as CO2 (D-007); fugitives cannot be bounded before P&IDs.

## D-013 Open library and core items (2026-10-28)
- Chemicals registry (`chemicals/chemicals.yaml`, consolidated shared-files PR): missing
  formic-acid (with an 85 wt% grade), methyl-formate, carbon-monoxide, methanol,
  sodium-methoxide, sodium-formate. The main product and those feeds are therefore not listed
  under `chemistry:` in process.yaml.
- Shared LCI vocabulary (`lci/mappings.yaml`): no technosphere entries for these, and no
  biosphere identity for methyl formate and methanol to air (crosswalk). formic-acid-1's
  `lca/mappings.yaml` stays empty.
- Core bug: `cheme process build` (0.8.0, pyDEXPI 2.1.0) fails with "TypeError: 'typing.Union'
  object is not iterable" for a step of class `Pumping` (its `method` annotation is
  `PumpingMethod | Undefined | None`, which `step_method` in domains/process/build.py iterates).
  P101 and P201 use the parent class `GeneratingFlow` until it is fixed.
- Core: property package and liquid-reactor energy for this mixture (gated step, D-006).

## D-014 Gated steps and next stage (2026-10-28)
Gated: predictive simulation and energy closure (no qualified package for
methanol / methyl formate / water / formic acid with acid association; liquid-reactor energy).
`cheme maturity` reaches no calculation level: feeds, the hydrolysis and oxidiser conversions
and the column splits are assumed (only the carbonylation conversion is given with a source).
Next stage (concept, continued): a source audit of SRC-2/3/4 full texts and an open source for
the liquid heat of hydrolysis; a rigorous VLE basis for the formic acid / water azeotrope across
pressure (to replace the patent table and the shortcut duties); a heat-integration pass (feed-
effluent exchange, double-effect C-301/C-302); the CO supply link (a syngas cold box process);
then the review of this stage and P&IDs (basic).
