# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#151. Run of 2026-10-28 (concept: design basis to
balanced PFD and a preliminary gate-to-gate LCI). Starting library commit cc5624f,
cheme-as-code 0.8.0 (pyDEXPI 2.1.0, Python 3.15). Designed independently from open sources;
no published flowsheet, stream table or plant data set was copied. The issue's core links
(#315, #364) could not be opened from this environment (`gh` cannot resolve them); the gated
steps below are stated from what `cheme process methods` and `props --coverage` report today.

## Route and boundary memo

**Route.** Gas-phase hydrochlorination of methanol over alumina:
CH3OH + HCl -> CH3Cl + H2O, with dimethyl ether (2 CH3OH -> CH3OCH3 + H2O) as the main
by-product. The reactor gas is quenched with hydrochloric acid, which condenses the water of
reaction with the excess HCl; the crude methyl chloride is dried with concentrated sulfuric
acid, which also absorbs the DME; it is then compressed, condensed and freed of dissolved HCl
by distillation. This is the route named in the issue and the alumina process described as
the general practice in US 4,794,204 (S1, background).

Rejected for this case:
- *Liquid-phase hydrochlorination* (uncatalysed at about 105 C in S5's examples, or over a zinc
  chloride catalyst): makes less DME but needs aqueous HCl handling and a different reactor; it is
  a separate case if wanted.
- *Methane chlorination*: makes methyl chloride together with dichloromethane, chloroform and
  carbon tetrachloride and consumes chlorine, producing HCl; a co-product system with its own
  boundary (issue scope note: keep the routes apart).
- *DME removal by catalytic cleavage with HCl* (the invention of S1): it lowers the acid
  consumption but adds a second catalytic reactor; the conventional sulfuric acid wash is kept
  as the base case (issue route) and the cleavage noted as an improvement (I-06).

**Boundary.** From methanol, anhydrous HCl gas and 96 wt% sulfuric acid at the battery limit to
liquid methyl chloride, dilute hydrochloric acid, spent sulfuric acid and an inert purge at the
battery limit. Outside: methanol production (library `methanol-1` supplies it), the HCl source
(D-003), sulfuric acid production and spent acid regeneration (`sulfuric-acid-1`), storage,
the site boilers, cooling tower, thermal oxidiser and waste water treatment. Utilities cross
the boundary as energy streams.

```
 methanol ─> M100 ─> E101 vaporiser ─┐            ┌── recycle (HCl, CH3Cl, N2) ──────────┐
   ^ methanol recycle (C202)         v            v                                      │
 HCl gas ─────────────────────────> M101 ─> E102 superheater ─> R101 alumina reactor     │
                                                                  │ 613 K                │
                         dilute HCl <─ C202 stripper <─ acid ─ Q201 quench + graphite cooler
                                                                  │ crude gas           │
                  96 % H2SO4 ─> T301 drying tower ─> spent acid (80 %, DME)              │
                                       │ dry gas                                         │
                                       v                                                 │
                         K401 compressor ─> E401 condenser ─> C401 HCl column ─> top ─> S401 ─> purge
                                                                  └─> methyl chloride (liquid)
```

## Source register

| # | source | locator | read | reuse | used for |
|---|---|---|---|---|---|
| S1 | US 4,794,204 (Hoechst AG, 1988) Process for the removal of dimethyl ether in methyl chloride, [Google Patents](https://patents.google.com/patent/US4794204) | Description, first paragraphs: alumina process generally 350-400 C; crude CH3Cl after cooling and water condensation: methanol < 0.03 %, DME 0.3-2 %, HCl < 2 %, water ~0.1 %; drying acid at least 80 wt%, 95 % most used; spent acid about 80 % with 5-10 % bound DME. Plant embodiment (figure description): reactor gas ~300 C quenched in a packed column with circulating acid to 125 C, quench acid 20-25 % HCl; graphite cooler to 40-45 C, condensate 35-40 % HCl; crude gas 0.1-0.2 % water, 0.3-4 % HCl. | page text via fetch; sections located, no column numbers | patent text: facts only | D-001, D-006, D-008, crude-gas and acid checks |
| S2 | Schmidt, S.A., Vajglova, Z., Eränen, K., Murzin, D.Yu., Salmi, T. (2014) Microreactor technology for on-site production of methyl chloride. Green Process. Synth. 3(5) 345-352, [doi:10.1515/gps-2014-0039](https://doi.org/10.1515/gps-2014-0039) | abstract (Åbo Akademi research portal): gamma-alumina, best result at 340 C, methanol conversion 97.6 %, CH3Cl selectivity 98.8 %, close to the calculated equilibrium | abstract only (full text not retrieved: publisher returned 405) | facts only | D-004 |
| S3 | WO 2000/076658 A1 (ICI / Ineos Chlor) Use of alkali metal doped eta-alumina as methanol hydrochlorination catalyst, [Google Patents](https://patents.google.com/patent/WO2000076658A1/en) | Description, background: methanol and HCl about 1:1 molar to fixed or fluidised beds at 250-300 C; strongly exothermic, hot spots above 400 C sinter the catalyst and cause coking; DME main by-product on gamma-alumina; pressure not critical. Claims 11-13: HCl:MeOH 1:1.5-1.5:1, 200-450 C, 1-10 bara | page text via fetch | patent text: facts only | D-004, D-005 |
| S4 | cheme chemistry thermo (bundled `chemicals`): ideal-gas dHf (ATcT), S (CRC), cp (Poling 5th ed.) | per component | tool output | open data | reaction heats, equilibrium check, duties |
| S5 | US 3,983,180 (Shin-Etsu, 1976) Process for preparing methyl chloride, [Google Patents](https://patents.google.com/patent/US3983180A/en) | Description of the prior art (vapour-phase catalytic processes make more DME); examples 1-4 (liquid phase, 105 C, DME 0.1-0.2 wt%) | page text via fetch | facts only | route comparison only |
| S6 | Thyagarajan, M.S., Kumar, R., Kuloor, N.R. (1966) Hydrochlorination of methanol to methyl chloride in fixed catalyst beds. Ind. Eng. Chem. Process Des. Dev. | repository abstract (via search): gamma-alumina gives nearly equilibrium conversion at 300-390 C | search summary only; full text restricted | - | supports the near-equilibrium statement of S2; not used for numbers |
| S7 | Schmidt et al. (2013) Chem. Eng. Sci. 95, 232-245 (methyl chloride synthesis over Al2O3-coated microreactor, kinetics) | portal abstract (via search): activation energies 108 kJ/mol (CH3Cl) and 118 kJ/mol (DME) | search summary only | - | lead for kinetics at basic stage (I-03); not used |
| S8 | Ullmann's Encyclopedia: Chloromethanes, [doi:10.1002/14356007.a06_233.pub4](https://doi.org/10.1002/14356007.a06_233.pub4) | not opened (licensed) | not read | - | issue lead only |
| S9 | Library processes `methanol-1` (product spec, delivery 300 kPa(a), 313 K), `hydrogen-chloride-1` (33 wt% acid product), `acetone-1` (LCI conventions) | their process/design-basis.yaml, process/flowsheet.yaml, lca/ | read | CC BY 4.0 (own library) | D-003, D-013 |

No open source with plant utility consumptions (steam, power, cooling per t) for this route
was found in this run (no BREF chapter covers methyl chloride; the LVOC BREF 2017 chapters
cover other products). The utilities are therefore hand estimates (D-010), not benchmarked.

## D-001 Route and boundary (2026-10-28)
Decision: gas-phase hydrochlorination over gamma-alumina with HCl quench, sulfuric acid drying,
compression and distillation (route memo above); methanol, anhydrous HCl and sulfuric acid are
boundary feeds.
Reason: the route the issue names; S1 describes it as the general practice and gives the
crude-gas, quench and drying data needed to check a concept balance.
Rejected: liquid-phase and methane-chlorination routes (memo).

## D-002 Capacity 100 kt/a, 8000 h/a (2026-10-28)
Decision: 12 500 kg/h methyl chloride product (stream S17), 8000 h/a.
Reason: ASSUMED single-train scale for a silicones or methyl cellulose site; no traceable plant
basis was found (issue: capacity missing). The LCI is per kg, so the scale only affects
the absolute duties.

## D-003 Feeds (2026-10-28)
Decision: methanol at the methanol-1 product specification (99.95 wt%, water 0.05 wt%, 300 kPa(a),
313 K; provenance `given` from that design). Anhydrous HCl gas 99.9 mol% with 0.1 mol% inerts
lumped as N2 (ASSUMED), 450 kPa(a), 303 K. Sulfuric acid 96 wt% (D-008).
Reason: industrial methyl chloride plants usually take recycled anhydrous HCl (from the
hydrolysis of methylchlorosilanes or from chlorinations); its inert content is not sourced and is
set small so that a purge is needed but not dominant. hydrogen-chloride-1 makes 33 wt% acid, not
gas: linking it needs an HCl desorption step outside this boundary (noted in lca/lca.yaml).
Assumptions: inerts 0.1 mol% ASSUMED; no water or organics in the HCl.

## D-004 Reactor model: conversion and selectivity, not kinetics (2026-10-28)
Decision: R101 is a `reactor: conversion` step with `selectivity:` key MEOH, per-pass
conversion 0.976, 0.988 kmol CH3Cl and 0.006 kmol DME per kmol methanol converted. HCl/MeOH
1.10 mol/mol at the reactor inlet (ASSUMED).
Reason: S2 gives 97.6 % conversion and 98.8 % selectivity at 340 C on gamma-alumina and reports
them close to equilibrium; the rest of the converted methanol is assigned to DME (S1, S3: main
by-product). The ratio 1.10 is inside the 1:1.5-1.5:1 of S3 and gives a slight HCl excess that
drives the methanol conversion. Check with `cheme process reactors` (ideal gas, S4): at the
outlet (613 K, 300 kPa) ln(Q/K) = -0.096 for the hydrochlorination (Q/K = 0.91: just short of
equilibrium, consistent with S2) and +0.285 for DME formation (Q/K = 1.33: the modelled DME is
slightly above its own equilibrium with methanol and water; within the uncertainty of one data
point, and DME is cleaved back by HCl over alumina according to S1, so the model is if anything
conservative on DME). The resulting crude gas holds 0.56 mol% DME, inside S1's 0.3-2 %.
Rejected: an equilibrium reactor (it would also equilibrate DME and is not more sourced) and
kinetics (S7 not read; no invented rate data).
Assumptions: the S2 data point (a microreactor; its HCl ratio is not in the abstract) applies to
a multitubular industrial bed; selectivity and conversion independent of the recycle's water and
CH3Cl; recycled CH3Cl and DME inert in R101. Provenance kept `assumed` for that transfer.

## D-005 Reactor conditions (2026-10-28)
Decision: feed superheated to 523 K, outlet 613 K, 350/300 kPa(a); multitubular reactor with a
heat transfer fluid on the shell side; methanol vaporised at 400 kPa(a) (about 385 K).
Reason: 250 C inlet is the low end of S3's 250-300 C; 340 C outlet is S2's data point and inside
S1's 300-400 C; pressure inside S3's 1-10 bara, high enough for the downstream pressure drop.
Hot spots above 400 C must be avoided (S3): the multitubular cooled bed is chosen for that.

## D-006 Quench and acid condensation (2026-10-28)
Decision: step Q201 (quench column T-201 with circulating acid and graphite cooler E-201) cools
the gas to 313 K at 200 kPa(a). The crude gas keeps 0.5 mol% HCl (ASSUMED, inside S1's
0.3-4 %), 0.02 mol% methanol (S1: < 0.03 %) and 2.6 mol% water (water activity 0.7 over the
acid at 313 K, ASSUMED, times its vapour pressure 7.38 kPa over 200 kPa); 0.5 % of the CH3Cl
and 5 % of the DME dissolve in the acid (ASSUMED). The rest of the water, HCl and methanol leave
as quench acid S08.
Check: S08 is 20.5 wt% HCl, inside the 20-25 % quench acid of S1 (an outcome of D-004, not a
specification).
Gated: the split needs HCl-water-methanol VLE (an electrolyte); no package in core covers it
(D-011).

## D-007 Methanol stripper and dilute acid (2026-10-28)
Decision: C202 strips 99 % of the methanol and all dissolved CH3Cl and DME from the quench acid
(ASSUMED), with 0.5 kg water and 0.15 kg HCl per kg methanol overhead (ASSUMED); the overhead is
condensed and returned to the methanol vaporiser (M100, recycle S09). The bottoms, about 21 wt%
HCl with 0.04 wt% methanol (S10, 0.447 kg per kg product), leave the plant.
Reason: without the stripper 2.4 % of the methanol would be lost with the acid. The acid is close
to the HCl-water azeotrope (about 20 wt% at atmospheric pressure), so its HCl cannot be stripped
back by simple distillation; HCl recovery (pressure-swing or salt-assisted distillation) or
neutralisation lies outside this boundary (open item I-04). It is the largest waste flow and the
reason fresh HCl is 0.823 kg/kg against 0.722 stoichiometric.

## D-008 Sulfuric acid drying (2026-10-28)
Decision: T301 with 96 wt% acid (S1: 95 % most used). It absorbs all water and methanol, 99 % of
the DME and 0.1 % of the CH3Cl (ASSUMED). The acid rate is set so the spent acid holds 8 wt% DME
(ASSUMED, inside S1's 5-10 % limit): 52 g acid per kg product.
Check: the spent acid strength then follows as 80.5 % (H2SO4 on H2SO4 + water), S1 reports about
80 %: the assumed water content of the crude gas (D-006) and the DME limit are consistent.
Reason: DME (normal boiling point 248.3 K) and CH3Cl (249.1 K) cannot be separated by
distillation; the acid takes up DME as well as water (S1).

## D-009 Compression and HCl column (2026-10-28)
Decision: K401 compresses the dry gas from 190 to 1050 kPa(a) in two intercooled stages; E401
condenses the CH3Cl on cooling water (vapour pressure about 0.9 MPa at 313 K). C401 at 1000
kPa(a) strips the dissolved HCl and inerts; its partial condenser on cooling water leaves an
overhead vapour of 70 mol% CH3Cl (ASSUMED), 90 % of which returns to the reactor (S19) and 10 %
is purged (S401, ASSUMED) to the site thermal oxidiser. Product S17: 99.994 wt% CH3Cl, 56 ppm
DME (ASSUMED design target >= 99.9 wt%).
Reason: a refrigerated condenser would cut the CH3Cl in the purge (0.39 % of the product with
the purge, 0.10 % in the spent acid) but costs refrigeration; not justified at concept.
Assumptions: no heavies (higher chlorides do not form on this route); the HCl and water content of
the product are not resolved.

## D-010 Utilities: hand estimates (2026-10-28)
Decision: every duty is a hand estimate of `scripts/balance.py` with ideal-gas cp (S4) and round
latent and absorption heats (ASSUMED): methanol 33.5-37 kJ/mol, water 41-43, HCl absorption 63,
CH3Cl 19.3; boil-up of C401 0.3 kmol/kmol bottoms; compressor isentropic efficiency 0.75, motor
0.95; pumps 10 % of the compressor power. The reactor heat (cheme process reactors: 1510.8 kW,
hand estimate 1534 kW) is used inside the plant through the coolant loop: 964 kW superheat the
feed (E102), 546 kW go to the methanol vaporiser (E101). LP steam (500 kPa(a)) supplies the rest
of E101 and the C202 and C401 reboilers.
Per kg methyl chloride: LP steam 0.263 kWh (0.95 MJ), power 0.044 kWh, cooling water 0.649 kWh
(the quench 69 % of it).
Reason: no open source of plant utilities found (source register); no property package
qualified (D-011).
Rejected: exporting the reactor heat as steam (a co-product needing allocation) when the plant
itself needs more heat than the reactor gives.

## D-011 Property method: none qualified; gated energy balance (2026-10-28)
Decision: `property_method: placeholder`; no `cheme process props --fill` and no `cheme process
simulate`. Stream enthalpies, the energy closure and the separator splits (Q201, C202, T301,
C401) stay specified.
Reason: `cheme process props --coverage` finds no package for any stream (the benchmarked
packages cover N2/O2/Ar and syngas only); `cheme process methods` lists the electrolyte models
(ENRTL, Pitzer) as unsupported, the electrolyte route covering NaCl-water only. HCl-water and
H2SO4-water are electrolytes (core electrolyte support, issue #364); the polar CH3Cl-methanol-
water-DME gas needs a qualified package (core #315). These are the gated steps for a predictive
balance.

## D-012 Lists at concept (2026-10-28)
Decision: one equipment tag per PFD step (10 tags; Q201 links T-201 and E-201); reboilers,
condensers, pumps, drums, the coolant loop and spares not split out. The line list stays empty:
lines are numbered with the P&IDs, which are out of scope. Instrument list empty.

## D-013 LCI: foreground only, single product, wastes to treatment (2026-10-28)
Decision: lca/lca.yaml with functional unit 1 kg of methyl chloride product (S17) at the gate;
every exchange from the flowsheet; every background `missing:` with the activity it should link
to; no allocation (single product); the dilute HCl, spent acid and purge are wastes to treatment
(cut-off system model, no credits). Overrides in lca/mappings.yaml: LP steam counted as heat
(kWh) and the anhydrous HCl kept from linking to an aqueous acid producer.
Reason: library ADR on LCI gaps (an internal process reports gaps, never zeros); no licensed data
used. Treating the 21 % acid and the 80 % spent acid as wastes is conservative; if they are sold
or regenerated in a library process, the shared entry `spent-sulfuric-acid` (cut-off re-use) and
a new dilute-acid entry would replace the treatment (I-04, I-08).

## D-014 LCI exclusions (2026-10-28)
Decision: fugitive emissions, storage, the purge's combustion (in the treatment background) and
non-routine emissions (catalyst regeneration, start-up, relief) are declared exclusions without
an amount; the plant has no direct emission point in the model (the purge goes to the thermal
oxidiser).
Reason: fugitive estimates need P&ID component counts; no open source with amounts was found.

## Results (generated values are in the files)
- Balance: `cheme process streams`: 4 blocks and 12 steps closed; overall 19 011 kg/h in and out
  (scripts/balance.py). Extents: hydrochlorination 248.8 kmol/h, DME formation 1.51 kmol/h.
- Yields: CH3Cl on fresh methanol 98.3 mol%; Cl of fresh HCl to product 87.9 %, 11.7 % with the
  dilute acid, 0.4 % as CH3Cl in the purge and the spent acid, 0.05 % as HCl in the purge.
- LCI per kg CH3Cl (lca/inventory.csv): methanol 0.646 kg, HCl 0.823 kg, sulfuric acid 96 %
  0.052 kg, electricity 0.044 kWh, LP steam 0.263 kWh; out: dilute HCl 0.447 kg, spent acid
  0.069 kg, purge 0.005 kg, heat to cooling water 0.649 kWh. Mass in 1.5209 kg = out 1.5209 kg;
  `cheme assess lca --coverage`: mass, element and carbon-origin balances closed, 9 gaps,
  result "partial screening carbon footprint" (no impact claimed).

## Open items
- I-01 Capacity, site and HCl source not chosen (D-002, D-003).
- I-02 Rigorous energy balance and separator splits gated on electrolyte and polar property
  packages in core (#364, #315) (D-011).
- I-03 Reactor: one literature data point; read S2 and S7 in full for the HCl ratio and kinetics
  before basic engineering; hot-spot and catalyst life (coking, S3) not assessed
  (`cheme process reactor-hazards` once a bed is defined).
- I-04 Dilute hydrochloric acid (0.447 kg/kg): HCl recovery to the reactor vs neutralisation;
  the biggest lever on HCl use and waste.
- I-05 Alumina catalyst replacement (consumable) and regeneration off-gas not inventoried.
- I-06 DME cleavage with HCl (S1) as an alternative to part of the acid drying.
- I-07 Utilities not benchmarked against plant data (no open source found).
- I-08 Missing shared entries (to the consolidated PR, not edited here): chemicals registry
  `methyl-chloride` (chloromethane, CAS 74-87-3), `methanol` (67-56-1), `hydrogen-chloride`
  (anhydrous gas, 7647-01-0, distinct from hydrochloric acid), `sulfuric-acid` (7664-93-9),
  `dimethyl-ether` (115-10-6); lci/mappings.yaml technosphere entries `methanol`,
  `hydrogen-chloride-anhydrous`, a dilute hydrochloric acid treatment and a chlorinated vent gas
  thermal oxidation.
