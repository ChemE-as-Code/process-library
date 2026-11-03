# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#313 (PFD + LCI + simulation for the pilot processes). Run
of 2026-11-03 (concept: design basis to a balanced and simulated PFD and a preliminary LCI, a
cradle-to-gate study with the foreground inventory only). Starting library commit dc8f2220
(origin/main), cheme-as-code v1.4.1 (the commit pinned in .github/workflows/validate.yml),
DWSIM 9.0.5 (Docker image), thermo/chemicals as bundled with cheme.

Before this run cumene-1 was a manifest-only pilot with a hand-written Tier 0 dataset
(stoichiometry with the Versalis brochure's benzene and net steam, US EPA facility air
emissions, core's Tier 0 electricity default). Its sourced facts are kept as the cross-check of
the flowsheet (D-012); the dataset itself is retired (D-013).

## Route and boundary memo

**Route.** Liquid-phase alkylation of benzene with propylene on a zeolite (beta type):
C6H6 + C3H6 -> C9H12 (exothermic, -99.6 MJ/kmol at 298 K, ideal gas), with the consecutive
alkylation to diisopropylbenzene (DIPB) and on to triisopropylbenzene (TIPB, the heavy ends),
and the transalkylation of DIPB with benzene back to cumene (C12H18 + C6H6 -> 2 C9H12, about
thermoneutral) in a second reactor. Solid phosphoric acid (vapour phase, no transalkylation)
and aluminium chloride (corrosive, acid waste) were not chosen: the issue asks for the zeolite
route, and the current licensed processes use it (process/reaction-evidence.yaml, routes).

**Plant boundary (battery limits).** From fresh benzene and chemical-grade propylene at the
battery limit to cumene, propane (LPG) and heavy ends at the battery limit, plus LP steam
exported to the site header. Outside: benzene and propylene production, feed and product
storage, the users of the LPG, heavy ends and LP steam, utility generation (steam boilers,
cooling tower, power), flare, catalyst regeneration. No process water is fed or formed in the
model (the oily water the licensor names is an open item, I-07). Utilities cross the boundary as
energy streams (power, MP and HP steam in, LP steam out, cooling water).

```
 benzene ─┐                                      ┌─> LPG (propane)
          ├─> RXN: benzene drum, charge pump,    │
propylene ┘    feed/effluent exchanger,          │   SEP: depropaniser (slipstream)
              alkylator (LP steam), DIPB pump,  ─┤        benzene column ─> benzene recycle ─┐
              transalkylator ─> effluent         │        cumene column ─> cumene            │
          ^                                      │        DIPB column   ─> heavy ends        │
          ├──── benzene recycle <────────────────┼───────────────────────────────────────────┘
          └──── DIPB recycle    <────────────────┘
```

**Reference models (not used as data).** DWSIM/FOSSEE flowsheets of cumene (CC BY-SA) and the
cumene flowsheets of Luyben's textbook and papers were not opened for data: no topology,
stream value or specification of them is used. Every number here is this study's choice
(ASSUMED) or a fact from a cited source (process/reaction-evidence.yaml, the Versalis brochure,
the LVOC BREF, the US EPA dataset).

## Decisions

### D-001 Independent concept design of the zeolite cumene process (2026-11-03)
Decision: design the plant from the route chemistry and openly cited facts with the units the
issue names: alkylator, transalkylator, depropaniser, benzene recycle column, cumene and DIPB
columns, heavy ends; concept stage only (no P&IDs, HAZOP, layout or estimate in this run).
Reason: #313 asks for a PFD, a simulation and an LCI derived from the flowsheet for the pilot.
Rejected: reconstructing a published flowsheet (DWSIM/FOSSEE, Luyben): licence (CC BY-SA) and
the library's rule that every design is its own.

### D-002 Capacity and product specification (2026-11-03)
Decision: 34.0 t/h cumene product stream (272 kt/a at 8000 h/a); target purity 99.95 wt% or
better, benzene and DIPB the only modelled impurities.
Reason: the capacity covers acetone-1's fresh cumene (33.2 t/h, its S01) with about 2 % margin,
so that the library's phenol/acetone chain can use this plant (ASSUMED, no client figure); the
purity is the licensor's typical figure (Versalis brochure, PDF p. 3).
Assumptions: n-propylbenzene, ethylbenzene, butylbenzenes and the bromine index of a commercial
specification are not modelled (I-03).

### D-003 Feeds (2026-11-03)
Decision: fresh benzene pure, 303 K, 400 kPa(a); chemical-grade propylene 95 mol% with 5 mol%
propane (the only impurity), liquid at 313 K, 2000 kPa(a).
Reason: the issue asks for propane in the propylene as an inert that is purged; the licensor
states that chemical- and refinery-grade propylene can be processed (Versalis brochure, PDF
p. 3). The purities are ASSUMED (I-01, I-02).

### D-004 Reaction section conditions (2026-11-03)
Decision: the charge pumps P-101, P-102 and P-103 deliver 4200 kPa(a); the alkylator feed
(benzene/propylene 4 mol/mol) is preheated to 413.15 K in the feed/effluent exchanger E-101 and
reacts in the liquid phase to an outlet of 436.15 K at 4000 kPa(a); pressure drops 100 kPa per
exchanger side and reactor (ASSUMED). Propylene is injected before each bed in the real
reactor (Versalis brochure, PDF p. 4) with interbed coolers; the model is one cooled conversion
reactor whose heat removal raises LP steam (D-009). The transalkylator feed (benzene + DIPB
recycle) is heated in E-102 to 433.15 K and reacts adiabatically.
Reason: the alkylator outlet is the temperature of the patent's liquid-phase example on zeolite
beta (US4891458A Example 4: 325 F, 600 psig, complete propylene conversion; reaction-evidence
O1); 4.1 MPa keeps the feed with its propane liquid. A benzene/propylene ratio of 4 lies inside
the range 1-10 of US6888037B2 (O3) and below the ratio of O1 (about 7.4), the usual trade
between benzene recycle and DIPB make; it is ASSUMED, not optimised (I-04).
Results (scripts/cumene_balance.py): E-101 duty 5.4 MW, effluent leaves at about 344 K;
the alkylator removes 6.2 MW to LP steam.

### D-005 Reaction model: specified conversions, selectivity split ASSUMED (2026-11-03)
Decision: conversion reactors (process/reactions.yaml). R-101 converts all the propylene,
0.88 of it to cumene (ALK), 0.115 to DIPB (ALK2, benzene + 2 propylene) and 0.005 to TIPB
(ALK3, benzene + 3 propylene), each written keyed on propylene so that DWSIM's conversion
reactor reproduces the split. R-102 converts 0.40 of the DIPB per pass with benzene/DIPB 5 mol/mol
at its inlet (TRANS); TIPB does not react. DIPB is represented by 1,4-diisopropylbenzene and the
heavy ends by 1,3,5-triisopropylbenzene (isomer surrogates); the 1,3-isomer, which the patent
reports as the larger DIPB fraction, is not in DWSIM's database, the 1,4-isomer is (D-011).
TIPB's formation enthalpy is a Joback estimate and its entropy a group increment (ASSUMED,
materials.yaml); it only enters the small ALK3 heat.
Reason: route selection in process/reaction-evidence.yaml (model_basis): complete conversion is
reported (O1); the cumene/DIPB split at the design ratio is not, so it is ASSUMED from O1's
0.915/0.085 (derived) at the higher ratio of about 7.4, with more DIPB at ratio 4; the TRANS
conversion is ASSUMED at the upper end of O2's 35-40 % (411 K, LHSV 1), with the reactor
hotter (433 K). No kinetics: reactor volumes are not sized.
Rejected: an equilibrium model of transalkylation (no equilibrium data read, I-05).
Results: overall yield 0.9963 kg cumene per kg benzene + propylene; consumption 0.652 t benzene
and 0.352 t propylene per t cumene (D-012).

### D-006 Propane purge on a benzene slipstream (2026-11-03)
Decision: the propane entering with the propylene passes both reactors and is taken overhead in
the benzene column with the recycle benzene; a slipstream of the pumped benzene (SPL1, about
20 % of it) goes to the depropaniser C-201, which takes the propane overhead as LPG (98 mol%,
2 mol% benzene) and returns the benzene through the benzene column. The slipstream is set so
that the benzene recycle holds 5 mol% propane.
Reason: the propane must leave somewhere (Versalis brochure, PDF p. 4: recovered as propane
product or fuel); a depropaniser on the slipstream heats only a fifth of the recycle to its
1.5 MPa bottoms temperature instead of the whole reactor effluent (ASSUMED arrangement).
5 mol% keeps the benzene column's total condenser above the cooling-water return (C-202 top
about 321 K in the script): more propane would lower it below.
Rejected: a depropaniser on the whole effluent (about five times the reboiler duty); a vent on
the benzene column (benzene losses).

### D-007 Independent balance script; property method not qualified (2026-11-03)
Decision: scripts/cumene_balance.py balances the plant independently of DWSIM: recycles solved
by fsolve, columns by component specifications, minimum reflux by Underwood at constant
relative volatility (Raoult) with the feed's thermal condition, duties from column energy
balances, enthalpies and pump volumes from thermo's Peng-Robinson with the ChemSep kij set and
the formation enthalpies of process/materials.yaml. Its fresh-feed flows and split fractions
go into the flowsheet as `assumed` with the script as source (balance-output contract,
ADR 0027); everything else is DWSIM's (D-011), and the two are compared there.
Reason: core has no qualified property package for aromatics with light hydrocarbons (its
packages cover air and syngas; predictive.property-regime covers N2/O2/Ar and ethanol-water
only), so `props --fill` cannot be used and the simulation cannot be validated against a
benchmark; a second, independent implementation is the check (the hda-1 pattern).
Results: recycle residual below 1e-13; mass in 34785.20, out 34784.64 kg/h; energy closure
32339.9 kW in, 32137.3 kW out, the difference 202.6 kW (0.63 %) against 310.7 kW of pump
work whose temperature rise the script neglects.

### D-008 Separation train (2026-11-03)
Decision: four columns with total condensers (shortcut, Fenske-Underwood-Gilliland):
- C-201 depropaniser 1500/1520 kPa(a): propane in the bottoms 0.05 mol%, benzene in the LPG
  2 mol%; HP-steam reboiler (bottoms about 476 K).
- C-202 benzene column 150/180 kPa(a): benzene in the bottoms 0.02 mol%, cumene in the recycle
  0.05 mol%; MP-steam reboiler.
- C-203 cumene column 120/150 kPa(a): DIPB in the cumene 0.01 mol%, cumene in the bottoms
  1 mol%; HP-steam reboiler; product cooler E-103 to 313 K.
- C-204 DIPB column 30/45 kPa(a) (vacuum, to keep the bottoms within HP steam): TIPB in the DIPB
  recycle 0.5 mol%, DIPB in the heavy ends 5 mol%; HP-steam reboiler.
Reflux 1.3 x Underwood minimum, at least 0.5. Stage numbers not fixed (datasheets at basic).
Reason: specifications that meet the 99.95 wt% product (99.97 wt% results) and keep the
recycles clean; pressures from the condensing and reboiling temperatures against cooling water
and the steam levels (ASSUMED). The Versalis brochure (PDF p. 4) has the same three main
columns (benzene, cumene, PIPB).

### D-009 Reaction heat to LP steam; by-product destinations (2026-11-03)
Decision: the alkylator's heat (6.2 MW) raises LP steam at 250 kPa(a) (saturation 400.6 K, 12.5 K
below the coolest bed temperature, the 413 K inlet, and 35.6 K below the outlet) for export to
the site header (product LPSX). The interbed coolers cool each bed's effluent back to about the
413 K inlet temperature, so the steam must boil below 403 K for a 10 K approach; a first
choice of 350 kPa(a) (411 K) left only 2 K there. The LPG goes to sale or
fuel and the heavy ends to fuel, outside the boundary.
Reason: the licensor's net steam figure is HP import less LP export (Versalis brochure, PDF
p. 3, note 1), i.e. the reference plant exports LP steam; the alkylator heat is the source at
this temperature. 250 kPa(a) is ASSUMED (I-06).

### D-010 Utilities and machines (2026-11-03)
Decision: cooling water 298/308 K; MP steam 1500 kPa(a) (E-102, C-202), HP steam 4200 kPa(a)
(C-201, C-203, C-204); electric pump drives, efficiency 0.65; reflux, bottoms and product
pumps and the C-204 vacuum system are not in the flowsheet but declared as LCA cut-offs
(lca/lca.yaml). All ASSUMED.

### D-011 DWSIM simulation of the whole plant, an unqualified cross-check (2026-11-03)
Decision: `cheme process simulate --fill` (core v1.4.1, DWSIM 9.0.5, Peng-Robinson,
process/simulation.yaml) computes every stream downstream of the feeds and every duty; the
flowsheet keeps only the feeds, the design pressures and temperatures, the SPL1 fractions and
the drum outflow S3 as assumed values. The run converged (tears S13 and S9); the plant's
enthalpy closure on the formation basis is 1.3 kW.
How it is set up, and why:
- **Not qualified.** Core's predictive.property-regime covers N2/O2/Ar and ethanol-water only;
  no package is benchmarked for aromatics with propane and propylene (`cheme maturity` fails
  predictive.property-regime). The simulation is a second implementation of Peng-Robinson
  checking the script (D-007), not validated data. The recorded method selection
  (non-polar hydrocarbons, no electrolytes, no pseudocomponents, interaction parameters not
  checked) recommends Peng-Robinson.
- **Benzene loop closed at the drum.** Benzene is in excess and its consumption does not depend
  on the recycle, so with a fixed fresh benzene and fixed split fractions the loop's size is
  set only by trace losses: a trial run grew the recycle to 414 t/h (benzene/propylene about
  13). In the plant the drum level sets the fresh benzene. So M101 is excluded from DWSIM, the
  drum outflow S3 is the script's (assumed), and DWSIM computes the recycle S2. The M101
  balance then checks the loop: 135095.6 kg/h in (S1 + simulated S2) against 135092.4 out, 3 kg/h.
- **Liquid-full reactors.** DWSIM's reactors have a vapour and a liquid outlet; R-101 and R-102
  get a vapour port (S28, S29), which the run leaves empty (0 kg/h, i.e. the reactors stay
  liquid). Their all-zero compositions are left out of the flowsheet (a zero flow has none).
- **Surrogates.** DWSIM has neither 1,3-DIPB nor 1,3,5-TIPB. DIPB is 1,4-DIPB in materials.yaml
  too. TIPB stays TIPB in materials.yaml and the script; in DWSIM it is mapped to 1-tetradecene
  (normal boiling point 524 against 522 K, molar mass 196.4 against 204.4), so the heavy ends
  come back about 4 % light in mass (97.1 against 100.9 kg/h) and the TIPB component balance of
  C-204 is off by about 4 kg/h; the flowsheet tolerance is abs 5 kg/h for this (stated there).
  ALK3's heat with the surrogate differs by about 4 kW of the 6.2 MW reactor duty.
- **Columns.** C-201 to C-203 are DWSIM shortcut columns on the script's key specifications.
  C-201's reflux is 1.94 = 1.3 x DWSIM's Underwood minimum (1.49): the script's Raoult estimate
  (0.06) is far off for propane near its critical point, so the reflux differs by design.
  C-204 is rigorous (24 stages, reflux 0.5, heavy ends 0.4988 kmol/h): the shortcut's heavy-end
  mole fractions added up to 1.006. The shortcut products' mole fractions add up to 1 within
  1e-4 (S20, S23 to S26), which pyDEXPI reports as warnings on the BFD/PFD.
Agreement with scripts/cumene_balance.py (script / DWSIM):
| item | script | DWSIM | difference |
|---|---|---|---|
| cumene product S25, kg/h | 34000.0 | 33996.2 | -0.01 % |
| cumene purity, wt% | 99.972 | 99.972 | 0 |
| benzene recycle S2, kg/h | 112931.8 | 112935.0 | 0.00 % |
| DIPB recycle S13, kg/h | 6703.4 | 6667.6 | -0.5 % (TIPB 0.5 against 0.1 mol%: rigorous C-204) |
| LPG S20, kg/h | 683.8 | 688.2 | +0.6 % |
| heavy ends S27, kg/h | 100.9 | 97.1 | -3.8 % (surrogate molar mass) |
| P-101 power, kW | 269.8 | 284.4 | +5.4 % |
| E-101, kW | 5378.7 | 5225.9 | -2.8 % |
| R-101 heat to LP steam, kW | 6157.0 | 6228.2 | +1.2 % |
| E-102, kW | 1017.3 | 960.4 | -5.6 % |
| C-201 reboiler / condenser, kW | 2461.9 / 92.6 | 2531.5 / 198.7 | +2.8 % / reflux 0.5 against 1.94 |
| C-202 reboiler / condenser, kW | 19528.1 / 21403.9 | 19341.8 / 21369.6 | -1.0 % / -0.2 % |
| C-203 reboiler / condenser, kW | 4439.0 / 4739.0 | 4517.9 / 4736.8 | +1.8 % / 0.0 % |
| E-103, kW | 2291.7 | 2254.3 | -1.6 % |
| C-204 reboiler / condenser, kW | 523.3 / 802.8 | 526.1 / 813.0 | +0.5 % / +1.3 % |
| R-102 outlet, K | 432.12 | 432.39 | +0.27 K |
| C-202 bottoms, K | 453.64 | 453.92 | +0.28 K |
| C-203 bottoms, K | 492.6 | 499.2 | +6.6 K (more TIPB in DWSIM's C-203 bottoms, surrogate) |
Findings the run leaves (warnings, recorded, not silenced):
- `sim-utility-level` R-101/LPSX: the check takes a cooled unit as a hot stream cooling from
  its inlet (413 K) to its outlet (436 K); this reactor heats up while cooled, so the check
  finds no feasible direction. With interbed coolers the steam at 400.6 K serves bed effluents
  of 413-436 K (D-009). A limit of the check for cooled exothermic reactors, to report to core.
- `sim-formation-data` R-102: DWSIM's benzene formation enthalpy (ChemSep, 82880 kJ/kmol)
  differs from ATcT's (83180, materials.yaml) by 300 kJ/kmol, 1.4 kW on a reaction heat of
  about 39 kW (TRANS is nearly thermoneutral, so the 1 % tolerance is 0.12 kW). The design rests
  on ATcT (the script); the effect on any duty is below 0.01 %.
- `sim-energy-unbalanced` P-103: 0.46 kW on 16 kW, the DIPB pump with the TIPB surrogate.
Rejected: shortcut C-204 (mole fractions above 1); a fixed fresh benzene with the loop inside
DWSIM (indeterminate loop, above; with it, the tight column specifications stalled just above
the tear tolerance and relaxed ones converged only at the 414 t/h recycle and below the product
purity).

### D-012 Comparison with the pilot's sourced facts (2026-11-03)
Decision: the pilot's facts stay the cross-check of the flowsheet; per t of cumene (DWSIM run):
| item | this flowsheet | source | standing |
|---|---|---|---|
| benzene | 0.652 t | 0.651 t (Versalis brochure, PDF p. 3) | +0.1 %: agrees |
| propylene (as C3H6) | 0.352 t | 0.352 t (brochure) | agrees |
| yield, cumene per benzene + propylene | 0.9962 kg/kg | 99.7 wt% or higher (brochure); 99 % (LVOC BREF 2.1.1.5) | between the two (benchmarks/aromatics.yaml) |
| steam, net of LP export | about 1.27 t (1.58 t imported, 0.30 t exported, as condensing heat at the levels' latent heats) | 0.2 t (brochure, HP import less LP export) | about six times higher |
| heat delivered by steam | 2.95 GJ gross, 2.29 GJ net of the export | US EPA dataset doi:10.23719/1503030: fuel inputs about 2.5 MJ/kg, facility-wide | the same order; neither confirms the other |
| electricity | 9.6 kWh (pumps) + about 5 kWh cut off (reflux, vacuum pumps) | none open; the pilot used core's Tier 0 default 333 kWh (dated site average) | the default was far above a process estimate; cooling-water circulation is in the cooling-water background |
| air emissions | not estimated (declared exclusion) | 5.9, 7.8 and 19 g of benzene, propylene and cumene (EPA, facility-level, 2011) | kept as the order of magnitude only |
| heavy ends | 2.9 kg | 2.8 kg (the pilot's balance closure) | agrees |
Reason: the yields follow from the selectivity split and the column specifications and land on
the licensor's figures, which supports the ASSUMED split (D-005) without proving it. The steam
gap is the heat integration a licensed plant has and this concept has not: the benzene column
alone takes 19.3 MW of MP steam, its 21.4 MW condenser rejects heat at 321 K; a licensor
recovers reaction heat at a higher level, runs a lower benzene ratio and integrates the
columns (pressure-staged or with vapour recompression). Open item I-08.

### D-013 LCI from the flowsheet; the Tier 0 dataset retired (2026-11-03)
Decision: lca/lca.yaml (cradle-to-gate, foreground only, functional unit 1 kg cumene) and
`cheme assess lca --write` give lca/dataset.yaml, the process's LCI; every background is
`missing:` (6 gaps) and process.yaml says `lca.source: none` (no impact result, ADR 0029). The
four products are co-products allocated by exergy (scripts/allocation_exergy.py): cumene
97.1 %, LPG 2.2 %, heavy ends 0.3 %, LP steam export 0.4 %. Omissions are declared
(emission_exclusions: fugitive leaks, storage, C-204 vacuum vent, oily water, catalyst
regeneration; cut-offs: column pumps and vacuum system power). The hand-written Tier 0 dataset
lca/datasets/cumene-zeolite-alkylation.yaml is removed (it stays in git history); its facts are
D-012's cross-check. benchmarks/aromatics.yaml now binds the new dataset (yield on benzene +
propylene, the propane share of feed:PRF taken out), and lca/mappings.yaml carries the new keys
(benzene and propylene suppliers not chosen; MP and HP steam counted as heat).
Reason: every plant folder of the library has exactly one dataset, lca/dataset.yaml; only
manifest-only processes keep hand-written lca/datasets/*.yaml (scripts/build_lci.py reads both,
so keeping the Tier 0 file would put two cumene producers into the Atlas and the market could
not choose). The library allocates exported steam by energy or exergy, never by credit
(aniline-1 D-013 is the precedent for exergy); the pilot's net-steam figure embedded such a
credit (its recorded deviation), which this dataset no longer has. The LP steam co-product has
no inventory_key in process.yaml, so it is not offered as an Atlas steam producer (aniline-1).
acetone-1: its feed:CUM now carries the registry slug cumene (inventory_key) and is pinned to
this dataset's product:CUMENE in acetone-1's lca/mappings.yaml; the Atlas build no longer
reports it as a gap. No guess: the same registry substance and unit (kg), acetone-1's S01 is
pure cumene and this product 99.97 wt%; the 0.03 wt% of benzene and DIPB is not counted.
Rejected: keeping the Tier 0 dataset beside the new one (two producers); energy (LHV)
allocation (it charges the steam's enthalpy at the value of fuel).

### D-014 Lists at concept (2026-11-03)
Decision: equipment list with the 13 PFD items (no P&ID yet), design pressure = highest
operating + 10 % (at least + 2 bar), design temperature + 25 K, carbon steel; line list with
one line per PFD stream, DN from scripts/line_sizes.py (velocity rule on the simulated streams);
instrument list empty until the P&IDs. All ASSUMED.
Not done at this stage (out of the scope of #313's concept target): plot plan (gate
layout-plot-plan fails), estimate and TEA, P&IDs, HAZOP.

## Open inputs

| id | what | why it matters | status |
|---|---|---|---|
| I-01 | fresh benzene purity (toluene, non-aromatics, water, sulfur) | impurities, product spec | ASSUMED pure |
| I-02 | propylene grade (propane content), supply pressure | depropaniser size, propane recycle | ASSUMED 95 mol% |
| I-03 | commercial cumene specification (n-propylbenzene, ethylbenzene, butylbenzenes, bromine index) | n-propylbenzene forms on zeolite and is not separable from cumene | not modelled |
| I-04 | benzene/propylene ratio, bed count, propylene staging | DIPB make against benzene recycle and column duties | ASSUMED 4, one cooled reactor |
| I-05 | transalkylation equilibrium and DIPB conversion | recycle size | ASSUMED 0.40, not checked |
| I-06 | LP steam level and its user (acetone-1's CHP concentration uses LP steam) | the export's value and allocation | ASSUMED 250 kPa(a) |
| I-07 | oily water, vacuum vents, drains (licensor names them) | emissions | not quantified |
| I-08 | heat integration (benzene column, product cooler, reactor heat level) | steam use six times the licensor's | open |
| I-09 | selectivity split at the design ratio, heavy-end species | yield, heavy ends | ASSUMED, informed by US4891458A Ex. 4 |
| I-10 | registry slugs for propane (LPG) and polyalkylbenzene heavy ends | listing the by-products under chemistry | missing in chemicals/chemicals.yaml |
