# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Concept stage of issue ChemE-as-Code/process-library#129. Every number below that is not cited
is ASSUMED. Facts from sources are restated in our own words; no table, figure or text is
copied (library CLAUDE.md).

Starting point (2026-10-28): library commit 11d50ef on `main`, cheme-as-code installed as the
`cheme` uv tool (DWSIM 9.0.5 for `process simulate`, not used here).

## Source register

| id | source | locator | read status | used for |
|---|---|---|---|---|
| SRC-1 | US 4003952 A, "Direct hydration of olefins to alcohols", https://patents.google.com/patent/US4003952A/en | Background (prior-art process); Illustrative embodiment | full text read (Google Patents HTML) | conversion per pass 4-5 % at about 540 F / 1000 psia over phosphoric acid on celite and the large recycle it needs; diethyl ether the main by-product (1-10 % of the ethanol made) and equilibrium-limited, so recycling it suppresses its net make; acetaldehyde, crotonaldehyde and butanol named as further by-products (no amounts); water scrubbing of the reactor gas gives crude of about 10-12 mol% ethanol |
| SRC-2 | US 5349096 A (BP Chemicals), "Olefin hydration process", https://patents.google.com/patent/US5349096A/en | Summary (a)-(f), Description (temperature, pressure, feed paragraphs), claims 1, 3, 5, 9, 10; Examples, Tables 1-5 | full text read (Google Patents HTML) | operating window for ethylene: 225-280 C (preferred 230-260 C), 3000-10000 kPa, water/olefin 0.15-0.50 mol (preferred 0.30-0.40), acid loading 5-55 % w/w on silica; test runs at 6895 kPa, inlet 240 C, exit 260 C give 8-10.6 % ethylene conversion with ethanol space-time yields of about 0.10-0.11 kg/(L h) and large ether make when ether is not recycled |
| SRC-3 | US 4329520 A, "Process and catalyst for olefin hydration", https://patents.google.com/patent/US4329520 | Description, preferred ethylene conditions | search-result summary only, not opened: to verify | corroborates the window: 250-290 C, water/olefin 0.3-1, 900-1100 psig preferred for ethylene |
| SRC-4 | US 3953533 A, "Process for the hydration of olefins to alcohols" | - | lead only, not read | optional caustic wash of acid carried out of the reactor (D-007) |
| SRC-5 | Ullmann's Encyclopedia, "Ethanol", doi:10.1002/14356007.a09_587.pub2 | - | not accessible here; not audited (issue #129 notes the same) | general route reference only; no number taken from it |
| SRC-6 | NIST Chemistry WebBook, water, Antoine parameters (Bridgeman and Aldrich 1964; Stull 1947) | https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4 | parameters used in scripts/balance.py | water vapour pressure in the E-101 evaporation / condensation estimate |
| SRC-7 | `chemicals`/`thermo` data via `cheme chemistry thermo` (ATcT formation enthalpies, CRC entropies, Poling 5th ed. heat capacities, HEOS critical data) | materials.yaml `source:` fields | packaged data | ideal-gas formation data, reaction heats, reactor energy balance |
| SRC-8 | EN 15376 (fuel ethanol) water limit 0.3 % m/m | standard, clause on requirements | from general knowledge, not re-read: to verify | product water target (D-002) |

## D-001 Route, boundary and what is not designed (2026-10-28)
Decision: vapour-phase direct hydration of ethylene over phosphoric acid on silica (fixed bed,
gas recycle), water scrubbing of the recycle gas, a light-ends column, a concentrating column to
93 wt% ethanol and molecular-sieve dehydration to anhydrous ethanol. Gate-to-gate boundary:
ethylene arrives by pipeline at loop pressure from a steam cracker outside the boundary (no
library process makes ethylene yet; the boundary feed is the link to note); demineralised water,
HP and LP steam, cooling water and power come from the site utilities; the purge and light-ends
gas go to the site fuel-gas header, the water-loop blowdown to the site wastewater treatment.
Reason: issue #129 names this route; it is the petrochemical route with the open patent record
of SRC-1/SRC-2.
Rejected / not designed: fermentation of sugars or starch, the dominant route for ethanol by
volume worldwide (fuel ethanol), is noted only: it needs solids, biological inventory and
beer-column modelling (core #365) and is a separate case. The older indirect (sulfuric acid,
ethyl sulfate) process is obsolete (corrosion, acid reconcentration) and not considered.
Azeotropic distillation with an entrainer (cyclohexane, formerly benzene) for dehydration is
rejected in favour of molecular sieves (D-005): no entrainer inventory, lower steam; it would
avoid the adsorption gate (core #368) but brings a third component the balance would need.
Assumptions: product anhydrous ethanol (hydrous 93-95 wt% would remove V-301; D-002).

## D-002 Capacity, feed and product (2026-10-28)
Decision: 100 000 t/a anhydrous ethanol at 8000 h/a, 12 500 kg/h product with 0.2 wt% water
(EN 15376 limits water to 0.3 wt%, SRC-8; margin ASSUMED); polymer-grade ethylene 99.9 mol%
with 0.08 % ethane and 0.02 % methane (ASSUMED typical grade), 7300 kPa(a) and 303 K at the
battery limit (ASSUMED: no make-up compressor); demineralised make-up water.
Reason: no published plant basis was selected (issue #129 leaves capacity open); 100 kt/a is a
mid-size synthetic ethanol train, a normalisation basis, not a claimed plant scale. The LCI is
per kg and almost independent of it.
Rejected: a hydrous (95 wt%) product: the issue asks for anhydrous via dehydration.
Assumptions: the full product specification (methanol, higher alcohols, acidity) is not
modelled; the balance gives diethyl ether ~170 ppm(wt) in the product, a quality question for
basic engineering (an ether/ethanol topping cut or ether recycle, D-004).

## D-003 Reactor conditions (2026-10-28)
Decision: adiabatic fixed bed, inlet 513.15 K and 7050 kPa(a), water/ethylene 0.35 mol/mol at
the inlet; the outlet (540.9 K, 6950 kPa(a)) follows from the energy balance.
Reason: inside the ethylene window of SRC-2 (225-280 C, 3-10 MPa, preferred water/olefin
0.30-0.40; its test runs at 6895 kPa with 240 C in and 260 C out) and of SRC-3 (250-290 C,
900-1100 psig); 1000 psi is also the prior-art pressure of SRC-1. The low water ratio keeps the
water evaporation load down; HP steam at 4200 kPa(a) can then finish the feed heating
(D-008). cheme confirms the adiabatic outlet: `cheme process reactors` gives a step duty of
-0.3 kW at 540.86 K on the ideal-gas data of materials.yaml.
Rejected: 0.6 or higher water ratio (SRC-3 allows up to 1): about twice the evaporation duty;
a fired heater for the last superheat (no fuel combustion needed at 513 K inlet).
Assumptions: pressure drops (100 kPa over the bed, 50-100 kPa per exchanger) ASSUMED;
catalyst life, acid make-up and bed volume open (D-007, equipment list R-101).

## D-004 Reaction model: sourced conversion, assumed selectivities (2026-10-28)
Decision: conversion reactor, 5 % of the inlet ethylene converted per pass (SRC-1: 4-5 %,
upper end taken), with 0.97 kmol ethanol, 0.01 kmol diethyl ether and 0.005 kmol butenes
(1-butene standing for the oligomers) per kmol ethylene converted (ASSUMED). Reactions
HYD, ETHER, OLIGO in process/reactions.yaml; cheme computes the outlet (`propagate`) and
balances elements and extents.
Evidence and checks: SRC-2's test runs reach 8-10.6 % conversion at 240-265 C, but with ether
space-time yields of the same order as ethanol's because the ether is not recycled there;
SRC-1 says the ether make is equilibrium-limited and recycling it to the reactor drives its
net make towards zero. The ASSUMED 1 mol% (2 % of the ethylene) net ether stands for a plant
that removes ether in the light ends rather than recycling it to extinction, the low end of
SRC-1's 1-10 % (of the ethanol made). `cheme process reactors`: the hydration outlet lies at
Q/K = 0.66 (ln(Q/K) = -0.42) of its ideal-gas equilibrium at 540.9 K, so 5 % per pass is
thermodynamically feasible and not at equilibrium; ether and oligomers are far from theirs.
Rejected: an equilibrium reactor (it would overpredict the conversion the catalyst reaches in
practice; SRC-1 says the commercial per-pass conversion is low); kinetics (none sourced:
no rate law is invented).
Assumptions: selectivities are the main uncertainty of the yield: the overall ethylene to
ethanol-product yield is 94.2 mol% in this balance (losses: by-products 3 %, purge 1.9 %,
ethanol in the light ends 1 %). Acetaldehyde, crotonaldehyde and higher alcohols (SRC-1)
are not modelled.

## D-005 Separations: specified splits (2026-10-28)
Decision: every separator is a specified component split (scripts/balance.py), ASSUMED:
- V-101 HP separator at 313 K: to the liquid 99.8 % of the water, 97 % ethanol, 40 % ether,
  3 % butenes, 0.2 % ethylene and ethane, 0.1 % methane (dissolved gas);
- C-101 scrubber, 3600 kg/h wash water: recovers 99 % of the ethanol, 80 % of the ether, 5 %
  of the butenes, 0.06 % of the ethylene of the separator gas;
- loop purge 0.1 % of the scrubbed gas: inerts (ethane, methane, butenes) settle at 7.3 mol%
  in the loop; recycle/fresh 20 (molar);
- V-102 let-down to 300 kPa(a): 98 % of the dissolved ethylene and ethane, 90 % of the butenes,
  30 % of the ether flash off and are recompressed to the loop by K-102 (not lost);
- C-201 light ends: overhead all dissolved gas and butenes, 99 % of the ether, 1 % of the
  ethanol (0.25 mol fraction of the off-gas), boil-up 0.05 kmol/kmol feed;
- C-202: top vapour 93 wt% ethanol at 200 kPa(a), bottoms 100 ppm(wt) ethanol, reflux ratio 3
  (minimum reflux of ethanol-water to near the azeotrope is about 2, a judgement, not
  calculated);
- V-301 molecular sieve: product 0.2 wt% water, regeneration return of 18 % of the feed
  ethanol as a ~71 wt% condensate to C-202;
- water loop: 10 % of the C-202 bottoms to wastewater (blowdown of sodium phosphate and
  heavies), the rest with make-up water back to the scrubber and the reactor.
Reason: core cannot yet qualify flashes of ethylene / water / ethanol at 7 MPa or the
non-ideal distillation (core #315; its NRTL benchmark covers ethanol-water only, see D-012).
Rejected: hand-tuned "simulated" values presented as calculated.
Assumptions: all of the above; they set the losses and the recycle flows.

## D-006 Heat and material balance method (2026-10-28)
Decision: an independent script, scripts/balance.py (`cheme run scripts/balance.py`), solves
the four recycles (gas loop, flash gas, water loop, sieve regeneration) by successive
substitution to 1e-6 kg/h and estimates the duties: ideal-gas enthalpies from
materials.yaml, latent heats by Watson from the normal-boiling values, liquid heat capacities
constant (water 75.4, ethanol 112 kJ/(kmol K)), water evaporation and condensation in E-101 by
Raoult's law on water alone (SRC-6), E-101 found at a 10 K minimum approach along its length;
compressors ideal gas at isentropic efficiency 0.75, pump efficiency 0.65; heats of mixing and
non-ideal VLE ignored. Its separator and exchanger outlets and all duties enter the flowsheet
as ASSUMED; mixers, splitters, pass-through steps and the reactor are calculated by cheme.
Results (design case): E-101 41.1 MW recovered; E-102 4.6 MW HP steam; E-103 8.8 MW,
C-201 1.2/1.3 MW, C-202 16.6/12.4 MW, V-301 5.0 MW condensers; power 0.69 MW.
Reason: the energy closure of the separators, columns and exchangers cannot be evaluated by
core for this mixture (no property package: `cheme process props --coverage`, core #315).
Assumptions: concept accuracy, not stated; the C-202 reboiler (reflux ratio, feed at 12.5 mol%
ethanol) dominates the steam and is the first number to check by simulation.

## D-007 Acid carry-over, neutralisation, catalyst (2026-10-28)
Decision: phosphoric acid lost from the catalyst with the effluent is made up continuously to
the catalyst, and the acid in the effluent is neutralised by caustic soda injected before
E-103/V-101; the sodium phosphate leaves with the water-loop blowdown. These small flows are
not in the stream table; the LCI counts the acid make-up, caustic and the catalyst replacement
as ASSUMED consumables (lca/lca.yaml).
Reason: SRC-2 and SRC-1 describe the catalyst; SRC-4 names a caustic wash (lead, unread). No
open source of the acid loss rate was found: rates in lca.yaml are ASSUMED orders of
magnitude.
Assumptions: wetted parts downstream of the reactor stainless or lined (equipment list).

## D-008 Utilities (2026-10-28)
Decision: HP steam 4200 kPa(a) (526.4 K) for E-102; LP steam 450 kPa(a) (420.8 K) for the
reboilers; cooling water 298/308 K; electric drives. All ASSUMED site levels.
Reason: E-102 heats the feed to 513 K with a 13 K approach to HP steam saturation; the
column bottoms (398-403 K) leave about 18 K to LP steam.

## D-009 Equipment design conditions (2026-10-28)
Decision: design pressure = highest operating pressure + 10 % (at least + 2 bar), design
temperature = highest operating + 25 K; one design pressure (80 barg) for the HP loop.
ASSUMED concept rule, as in methanol-1.

## D-010 Line sizes (2026-10-28)
Decision: first-pass DN from velocity (gas 15 m/s above 1000 kPa(a), 20 m/s below, two-phase
10 m/s, liquid 1.5 m/s), ideal-gas density with an ASSUMED compressibility (0.6 loop gas at
313 K, 0.9 at reactor temperature). ASSUMED.

## D-011 Core findings met on the way (2026-10-28)
- `cheme process build` stops with `TypeError: 'typing.Union' object is not iterable` on a
  step of class `Pumping` (its pyDEXPI `method` field is `PumpingMethod | Undefined | None`
  and `step_method` lists it as an enum). P-101 uses `TransportingFluids` (also pass-through)
  until core fixes it. To report to core.
- A step of class `Heating` is not treated as pass-through by `propagate` (E-102 left
  unsolved); `ExchangingThermalEnergy` with one material stream is.

## D-012 Methods and gated steps (2026-10-28)
| step | method used | status / gate |
|---|---|---|
| mass, component, element balances | cheme validate / process streams | closed for every block and step |
| reactor outlet and energy | cheme conversion reactor; `process reactors` ideal-gas duty | calculated; adiabatic outlet closes (-0.3 kW) |
| separators, columns, exchangers, utilities | scripts/balance.py specified splits and estimates | ASSUMED; energy closure not evaluable in core: no property package for ethylene/water/ethanol at loop pressure (core #315, polar/activity-coefficient benchmark open) |
| ethanol-water distillation and sieve return | could be simulated with NRTL in DWSIM, which core benchmarks for ethanol-water (`cheme process methods`) | next stage: simulate C-202 alone with its ether-free feed |
| molecular sieve | specified split | core #368 (adsorption PSA/TSA) not available |
| fermentation variant | not designed | core #365 (solids) would gate it |
| consumables in the LCI element balance | not assessable | `cheme assess lca --balance` asks for a composition of each consumable, but the lca schema of cheme-as-code 0.8.0 has no `composition` field on consumables (refused as an extra input): core finding |

## D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml quantifies every foreground exchange of the balanced flowsheet per kg of
the anhydrous ethanol product (S23) and leaves every background unmapped (`missing:` with the
background activity it should connect to): cradle-to-gate scope with all backgrounds open, as
nitric-acid-1 (ADR 0022: an unmapped exchange of an internal process is a reported gap).
Allocation none: ethanol is the only product; the purge and light-ends off-gas are a waste
burned with energy recovery in the site fuel-gas system (cut-off, no credit), the blowdown a
wastewater to biological treatment. No direct emission inside the boundary (no combustion, no
tank, no discharge; leaks not estimated without a P&ID count): declared in
`emission_exclusions`. Construction is cut off (no take-off at concept stage).
Consumables, ASSUMED orders of magnitude without an open source (D-007): phosphoric acid
make-up 1 kg/t ethanol (100 t/a), caustic soda 82 t/a (2 mol NaOH per mol acid), catalyst
charge ~60 t every 4 years (~115 m3 from the space-time yield of SRC-2, ~0.5 t/m3), 3A sieve
30 t every 5 years; each with a disposal (wastewater or landfill), unmapped.
Overrides: lca/mappings.yaml names the shared `steam-heat` entry for feed:HPS and feed:LPS,
because cheme counts steam as heat delivered (kWh) and the registry slug `steam` is per kg
(the Atlas build refused the unit otherwise); everything else stays a gap.
Result (cheme assess lca --inventory/--coverage, 2026-10-28), per kg product: ethylene
0.646 kg (stoichiometric minimum 0.607 kg for 0.998 kg ethanol: 94.1 % yield), make-up water
0.678 kg, electricity 0.055 kWh, HP steam heat 0.371 kWh (1.34 MJ), LP steam heat 1.430 kWh
(5.15 MJ), heat to cooling water 2.21 kWh, off-gas 0.0517 kg, wastewater 0.272 kg, H3PO4
1.0 g, NaOH 0.82 g, catalyst 0.15 g, sieve 0.06 g. 16 exchanges are gaps; classification
"partial screening" (no background); mass and C, H, O balances of the dataset close
(residuals 0.002 kg/h mass, 0.09 kg/h C on 16 575 kg/h); the element balance of the
consumables is not assessable (D-012). Inventory mass against the flowsheet: in 8076.49 +
8473.02 kg/h = out 12 502.09 + 645.94 + 3401.48 kg/h (16 549.51 kg/h each).
Plausibility: the steam (6.5 MJ/kg) is dominated by the C-202 reboiler at reflux ratio 3; the
duties are concept estimates (D-006).
Assumptions: all inventory amounts inherit the ASSUMED splits and duties of D-005/D-006.
