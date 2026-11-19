# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Methyl tert-butyl ether by catalytic distillation, issue ChemE-as-Code/process-library#509, a
continuous Tier 2 entry of the library. Concept stage: design basis, balanced BFD/PFD solved by
core, duties, equipment list and a preliminary gate-to-gate LCI. Out of scope here: P&IDs,
layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` at c04ed69 with the core pin b97a833 (v1.13.0).
Core solves a loop with design specifications and component separators (core ADR 0070) together
with tear streams (ADR 0060); this entry uses both, so the whole material balance is calculated
by `cheme process propagate`. Templates: `vinyl-acetate-1` (continuous structure, source
register, balance-output script), `oxalyl-chloride-1` (depth and register), `isobutene-1` (the
reverse reaction, MTBE cracking, and its components). Requires cheme-as-code 1.13 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Murat, M.N.; Mohamed, A.R.; Bhatia, S. (2003) Modeling of a reactive distillation column: methyl tertiary butyl ether (MTBE) simulation studies. IIUM Engineering Journal 4(2), 13-30, https://journals.iium.edu.my/ejournal/index.php/iiumej/article/download/371/319/1573 | section 2 (equilibrium-stage model, liquid-phase reaction, UNIQUAC liquid, ideal vapour; the activity-based rate law of Rehfinger and Hoffmann with 4.9 equiv H+ per kg of resin, a forward rate constant 3.67e12 exp(-11110/T) mol/(s equiv) and an equilibrium constant 284 exp(f(T)), equations 7 to 11); section 3.1 and Table 1 (basis 197 mol/s of MTBE, 500 000 t/a; 17 stages numbered from the top with the total condenser 0 and the partial reboiler 16; reactive stages 3 to 10 with 800 kg of catalyst each, 6400 kg; 11 bar; reflux ratio 7; methanol 206 mol/s liquid at 320 K and butenes 549 mol/s vapour at 350 K with 0.356 isobutene and 0.644 1-butene, both on stage 10; bottoms 197 mol/s); section 3.2 (1-butene stands for every inert C4; by-products neglected); Table 2 (their model against Nijhuis et al. 1993: top 348.8 K, bottom 423.8 K; distillate 363.7 mol/s with 0.032 methanol, 0.003 isobutene, 0.965 1-butene; bottoms 0.986 MTBE, 0.014 1-butene; condenser 49.7 MW, reboiler 39.3 MW (35.1 MW in Nijhuis et al.); isobutene conversion 99.5 % (98.5 %); reflux 2.55 kmol/s); Figure 6 text (methanol activity coefficients up to 11.6); Tables 3 and 4 (Bao et al.'s 2002 industrial column: distillate 5494 kg/h with 4.61 wt% methanol, bottoms 5428 kg/h at 98.64 wt% MTBE, isobutene conversion 99.62 %; top 336 K, bottom 417 K; a pre-reactor upstream of the column) | read (open access PDF, text extracted); facts only | D-001, D-002, D-004, D-005, D-008, benchmarks |
| SRC-2 | Svandova, Z.; Labovsky, J.; Markos, J.; Jelemensky, L. (2007) Impact of mathematical model selection on prediction of steady state and dynamic behaviour of a reactive distillation column. ESCAPE17, https://skoge.folk.ntnu.no/prost/proceedings/escape17/papers/T5-410.pdf | section 2.2 (MTBE from isobutene and methanol on strong ion-exchange resin, Rehfinger and Hoffmann kinetics, 1-butene as the inert, side reactions ignored, UNIQUAC); section 2.3 (Jacobs and Krishna's column: total condenser, 15 trays as 2 rectifying, 8 reactive with 1000 kg of catalyst each and 5 stripping, partial reboiler; 1110 kPa; methanol 775.8 kmol/h and butenes 1976.4 kmol/h on stage 10; reflux ratio 7; bottoms 675 kmol/h; 60 % stage efficiency); section 2.4 (three steady states at the operating feeds in both the equilibrium and the rate-based model; isolated branches of solutions; transitions between steady states after feed disturbances) | read (open PDF, text extracted); facts only | D-001, D-004, D-009 |
| SRC-3 | US 4 918 243 A, L.A. Smith, E.M. Jones, D. Hearn (Chemical Research and Licensing Co.), priority 1988-10-28: Heat recovery in MTBE methanol recovery, https://patents.google.com/patent/US4918243A/en | detailed description and claims: C4 raffinate from the MTBE unit with about 3 wt% methanol washed with water at 0.21 kg/kg (preferably 0.1-0.4) in a mixer and decanter, the water leaving with about 15 wt% methanol; methanol/water column, 99.9+ wt% methanol overhead, the water back to the wash with make-up; the conventional column at about 5 psig with an overhead of about 74 C (the invention raises it to 40-60 psig for heat recovery); feed of 5-60 wt% isobutene, methanol 10 % below to 100 % above stoichiometric, acidic cation-exchange resin | read (Google Patents, via a fetch summary of the full text); patent, facts only | D-001, D-006, D-007 |
| SRC-4 | US 5 336 841 A, J.R. Adams (Chemical Research and Licensing Co.), priority 1993-04-05: Oxygenate removal in MTBE process, https://patents.google.com/patent/US5336841A/en | background (water washing of the C4 raffinate leaves methanol, DME and MTBE traces); description of the figure (the washed C4, stream 27, with about 10 wppm methanol and 400 wppm water); claim 4 (a C4 overhead cooled to 20-50 C); MTBE units commercially at 85 %+ conversion | read (Google Patents, via a fetch summary of the full text); patent, facts only | D-006 |
| SRC-5 | processes/methanol-1, butadiene-1, isobutene-1 (this library) | methanol-1's Grade AA product; butadiene-1's raffinate-1 co-product (mass allocation); isobutene-1 cracks MTBE back to isobutene | library, internal | D-003, D-010 |
| SRC-6 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment, C. Bell, MIT) | ideal-gas data of process/materials.yaml (`cheme chemistry thermo`); liquid heat capacities (HEOS_FIT; ZABRANSKY_SPLINE for MTBE) averaged over 298-424 K: methanol 99.1, water 76.0, MTBE 212.5, 1-butene 166.2, isobutene 171.6 kJ/(kmol K); heats of vaporization (HEOS_FIT): isobutene 16.23, 1-butene 16.37 kJ/mol at 350 K, methanol 34.79 and water 41.93 kJ/mol at 345.3 K; vapour pressures: 1-butene boils at 349.3 K at 1100 kPa(a), MTBE at 426.5 K at 1100 kPa(a), methanol at 345.3 K at 136 kPa(a), water at 386.5 K at 160 kPa(a); liquid densities at 313 K | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037); the underlying works (ATcT, CRC, NIST WebBook, Yaws, the TRC tables, Zabransky et al., the DIPPR and HEOS correlations) were not read here | materials, scripts/balance.py, D-005, D-007, D-008 |
| SRC-7 | Rehfinger and Hoffmann (1990) Chem. Eng. Sci. 45(6); Nijhuis, Kerkhof and Mak (1993) Ind. Eng. Chem. Res. 32; Bao et al. (2002) Chem. Eng. J. 90(3); Ullmann's, Methyl tert-butyl ether | - | not read (licensed); the primary works behind SRC-1 and SRC-2 | route lead only |

## D-001 Route and boundary (2026-11-19)

Decided: etherification of the isobutene of a C4 raffinate with methanol over a strongly acidic
ion-exchange resin in one catalytic (reactive) distillation column, as SRC-1 and SRC-2 model it:
C4H8 + CH3OH <=> C5H12O. The reaction removes the isobutene from the C4 while the column takes
the MTBE away to the bottom, so the equilibrium-limited conversion goes to 99.5 % (SRC-1). The
C4 distillate carries the excess methanol (its azeotrope with the C4); a water wash takes it out
and a methanol column recovers it for recycle (SRC-3, SRC-4), which the column sources do not
model. The boundary is the plant gate: the raffinate from a C4 supplier (butadiene-1's
raffinate-1, steam cracker or FCC C4) and its inert C4 back as raffinate-2; methanol from
methanol-1; utilities from the site.

Rejected:
- **Fixed-bed reactors followed by conventional distillation** (the older layout; SRC-3's
  background: fixed-bed resin reactors and a debutaniser). Equilibrium limits the isobutene
  conversion in the reactors to about 90 % unless a second stage follows (SRC-4: commercial
  units 85 %+); the open sources read here give no reactor data for it. Catalytic distillation
  reaches 99.5 % in one column with open numbers.
- **A pre-reactor ahead of the catalytic distillation column** (the industrial arrangement
  SRC-1 names for Bao et al.'s plant): it would take most of the conversion and leave the column
  the polishing, but no open source read here gives the pre-reactor's conversion or the column
  that follows it at that duty; the open column of SRC-1 takes the whole conversion and is
  designed here.
- **ETBE with ethanol, or TAME from C5 isoamylenes**: other products, not the issue's.
- **Isobutene from isobutane dehydrogenation as the feed**: changes the feed, not the
  etherification; the raffinate route is the one the sources model.

## D-002 Capacity, product and operating hours (2026-11-19)

The capacity is SRC-1's basis: 197 mol/s of bottoms, which SRC-1 equates with 500 000 t/a of
MTBE. With the source's conversion and bottoms composition the product is 62.27 t/h, 498 kt/a in
8000 h (ASSUMED hours), 99.10 wt% MTBE (98.6 mol%) with 0.90 wt% C4: within commercial MTBE
grades for gasoline blending, not a solvent grade. Cooled to 313 K for storage.

## D-003 Feeds (2026-11-19)

The raffinate is SRC-1's two-component surrogate: 549 mol/s with 35.6 mol% isobutene and the
rest 1-butene, which stands for every inert C4 (SRC-1 section 3.2). A real raffinate-1 holds
butanes and 2-butenes too, and traces of butadiene, water and nitriles that poison the resin;
none is modelled. It arrives liquid at 298 K and 1300 kPa(a) (ASSUMED) and is vaporised in
E-104 to the source's 350 K vapour at 1100 kPa(a) (1-butene's dew point there is 349.3 K,
SRC-6). The raffinate is booked as two feed terminals, its isobutene (IBC, S1) and its inert C4
(C4I, S2), joined in M100: one stream physically, two exchanges for the LCI (D-010).
The methanol is methanol-1's Grade AA product taken as pure; the column receives SRC-1's
206 mol/s, fresh and recycled together, set by the design specification `methanol`.

## D-004 Reaction model: conversion, not kinetics (2026-11-19)

R101, the reactive zone of C-101, converts 99.5 % of the isobutene it receives (SRC-1 Table 2,
their model; 98.5 % in Nijhuis et al.'s), with no side reaction (both sources neglect them).
The methanol excess over the isobutene is 5.4 % (206 against 195.4 mol/s), about 11.5 mol/s of
methanol leaving with the distillate. SRC-1 states the activity-based rate law on the resin's
acid capacity (4.9 equiv/kg) with its forward rate constant and equilibrium constant; core has
no reactive-distillation model to integrate it stage by stage (L-1), so it is recorded and not
used. The heat of reaction from the ideal-gas data is -65.4 kJ/mol (materials.yaml); in the
liquid it is smaller, and it stays inside the column (D-008).

## D-005 The column's separation (2026-11-19)

C101 splits the reactive zone's outlet as SRC-1's Table 2 gives the products: all MTBE to the
bottoms with 0.781 % of the 1-butene (9.94 kmol/h, so 1.4 mol% C4 in the bottoms), the methanol
and the unconverted isobutene overhead. The result reproduces the source's distillate (363.6
mol/s, 3.2 mol% methanol, 0.3 mol% isobutene) and bottoms (197.2 mol/s). The trace water of the
recycle methanol (1.3 kg/h) goes with the MTBE (ASSUMED; 21 ppm(wt)). Temperatures: top 348.8 K
and bottom 423.8 K (SRC-1), consistent with the boiling points of 1-butene and MTBE at 1100
kPa(a) (349.3 and 426.5 K, SRC-6). The internal stream S8 between the two steps has no duty
and an ASSUMED temperature.

## D-006 Water wash (2026-11-19)

The cooled distillate (313 K, inside SRC-4's 20-50 C) is washed countercurrently with 0.15 kg
of water per kg (ASSUMED inside SRC-3's 0.1-0.4; design specification `wash`). The washed
raffinate-2 keeps 0.05 % of the methanol (about 9 ppm(wt)) and 400 ppm(wt) water, the washed C4
of SRC-4; 0.02 % of the C4 dissolve in the extract (ASSUMED). The extract holds 10.9 wt%
methanol (SRC-3's example: about 15 wt% from a 3 wt% raffinate at 0.21 kg/kg). The stages are
not sized: core has no liquid-liquid equilibrium system for methanol, water and C4 (L-3); a
mixer-settler is SRC-3's layout, a countercurrent column is chosen here for the lower methanol
left (ASSUMED).

## D-007 Methanol column and wash loop (2026-11-19)

C-202 runs at about atmospheric pressure, the usual column SRC-3 names (top 136 kPa(a) and
345.3 K, bottom 160 kPa(a) and 386.5 K, SRC-6; ASSUMED), so LP steam heats it. It takes 99.9 %
of the methanol overhead at 99.9 wt% on a C4-free basis (SRC-3: 99.9+ wt%), with the dissolved
C4 (1.05 wt% of the overhead, held in the condensate under pressure after the pump, ASSUMED;
a vent to fuel gas is a next-stage detail), back to the methanol feed. The bottoms water (about
120 ppm(wt) methanol) is cooled and 2 % of it purged (ASSUMED) to keep non-volatile impurities
out of the loop; make-up demineralised water closes it. Reflux ratio 1.5 (ASSUMED). The heat
recovery of SRC-3 (the column pressurised so that its overhead reboils another column) is not
taken: an open improvement.

## D-008 Heat and power: every energy flow (2026-11-19)

C-101's reboiler (Q3, 39.3 MW) and condenser (Q4, 49.7 MW) are SRC-1's values for the whole
column with its reaction (its own model; Nijhuis et al.'s reboiler 35.1 MW). The reaction's heat
stays inside the column (R101 declared adiabatic in process/simulation.yaml). The reboiler needs
MP steam: the bottoms boil at 423.8 K, above LP steam's 421 K. Every other duty comes from
`scripts/balance.py` (balance-output contract, library ADR 0027):

| stream | duty, kW | basis |
|---|---|---|
| Q1 | 13746.7 | E-104: the raffinate heated as liquid to 350 K and vaporised |
| Q2 | 391.9 | E-103: methanol from the mixer's 300.8 K to 320 K |
| Q3 | 39300.0 | C-101's reboiler, SRC-1 Table 2 |
| Q4 | 49700.0 | C-101's condenser, SRC-1 Table 2 |
| Q5 | 4623.5 | E-101: MTBE from 423.8 to 313.15 K |
| Q6 | 2125.6 | E-102: distillate from 348.8 to 313.15 K |
| Q7 | 1975.0 | C-202's reboiler, from its balance with the condenser |
| Q8 | 1007.7 | C-202's condenser, reflux 1.5 (ASSUMED) |
| Q9 | 930.2 | E-201: wash water from 386.45 to 313.15 K |
| P1 | 232.3 | pumps of C-101 (raffinate and methanol feeds, reflux, bottoms), efficiency 0.65 (ASSUMED) |
| P2 | 5.5 | pumps of the methanol recovery |

The enthalpy basis: liquids at constant heat capacities from 298.15 K, vaporisation at the
temperature named, no heats of mixing (SRC-6; L-2). The vaporiser E-104 is the largest steam
user after C-101: the source feeds the C4 as vapour, which lowers the column's reboiler. Per kg
of product: 0.631 kWh MP steam, 0.259 kWh LP steam, 0.938 kWh to cooling water, 0.0038 kWh of
electricity. No heat integration: the bottoms (Q5, 4.6 MW at 424-313 K) could preheat the
raffinate, and C-202 could run on the condensing duty of a pressurised column (SRC-3); both open.

## D-009 Hazards and operability (2026-11-19)

- **Multiple steady states.** SRC-2 finds three steady states of this column at the same feeds,
  in both the equilibrium and the rate-based model, and isolated branches when the butenes feed
  varies; a feed disturbance can move the column to another state with a far lower isobutene
  conversion. For the next stage: a start-up procedure that reaches the high-conversion branch,
  control of the methanol-to-isobutene ratio (the design specification here), and the
  continuation check of a stage-by-stage model (L-1).
- **Flammability.** Isobutene, 1-butene, methanol and MTBE are highly flammable; the column
  takes about 135 t/h of C4 and methanol at 11 bar and runs up to 424 K. Pressure relief on fire
  and on loss of condenser cooling (49.7 MW) are the governing cases for the next stage; core's
  relief scenarios are not run at the concept stage.
- **Thermal.** The etherification is exothermic but the column is self-limiting: the heat boils
  liquid at the column's pressure, so the temperature is fixed by the boiling points. Core's
  thermal screening (`reactor-hazards`) needs kinetics and a reactor model; a conversion step
  gives neither (L-4). A hot spot in the resin above its upper service temperature would degrade
  it (not sourced here).
- **MTBE in water.** MTBE is highly soluble in water and persistent in groundwater; the purge and
  any leak are handled as an environmental hazard (tank bunds, the purge to biological
  treatment).

## D-010 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml` takes every exchange of the design case per kg of product (`cheme assess lca
--write`). The raffinate is subdivided: the etherification takes only its isobutene, and its
inert C4 pass the plant and return to the supplier as raffinate-2. So the raffinate's isobutene
(feed:IBC) carries the burden, and the inert C4 feed (feed:C4I) and the raffinate-2
(product:RAF2) are outside the system (`free`); MTBE is the one product, with no allocation. In
the Atlas LCI, lca/mappings.yaml links feed:IBC to butadiene-1's raffinate-1 by mass: that
dataset allocates by mass, so a kg of its raffinate's isobutene carries the burden of a kg of
raffinate-1. The unconverted isobutene (0.32 % of the product mass) and the methanol in the
raffinate-2 are charged to MTBE (conservative). Methanol is linked to methanol-1, both steams
counted as heat (kWh), the make-up water to deionised water; the shared lci/mappings.yaml links
electricity, cooling water and the purge's treatment. The core study links no background, so
lca/gaps.csv lists every input as missing with the activity it should connect to.

Inputs not in the inventory: the ion-exchange resin (6400 kg in the column, SRC-1) is cut off
with an ASSUMED 2-year life (3.2 t/a, 6 ppm of the input mass): no open source read here gives
its life. Fugitive and storage losses are declared exclusions (no P&ID yet).

## Method and dependency table

| value | from | changes when |
|---|---|---|
| S5, S21 and every flow and composition but the feeds' | propagate: specs, R101, separators, tears | reactions.yaml, the splits, the targets |
| Q3, Q4, the column's temperatures | SRC-1 | the column basis |
| Q1, Q2, Q5 to Q9, P1, P2, S6's temperature | scripts/balance.py | any stream (rerun the script after propagate) |
| LCA outputs | cheme assess lca --write | the flowsheet or lca.yaml |

## Core features used (core 1.13.0)

- `specs:` with two design specifications, a feed's flow for a component flow and a feed's flow
  for a mass ratio (ADR 0070)
- `recovery:` component separators on three steps (ADR 0070)
- `tears:` on two streams, converged with the specifications (ADR 0060)
- `reactor: conversion` with a reversible reaction on its key; `mode: adiabatic` in
  process/simulation.yaml
- `ideal_gas` data for every component

## Core limits hit (each a candidate core issue)

- **L-1** No reactive-distillation model: C-101 is a conversion step followed by a component
  split, its duties the source's. An equilibrium-stage model with a kinetic or equilibrium
  reaction on the catalytic stages (SRC-1's model) would derive the conversion, the profile and
  the duties, and a continuation over a feed would show SRC-2's multiple steady states.
- **L-2** No property package covers methanol, C4, MTBE and water (UNIQUAC with methanol
  activity coefficients up to 11.6, the methanol/C4 and methanol/MTBE azeotropes, two liquid
  phases in the wash): the liquid and phase-change duties stay outside core in the script.
- **L-3** No liquid-liquid equilibrium system for methanol, water and C4 in `cheme process
  extract`: the wash's split is ASSUMED and its stages are not sized.
- **L-4** No thermal or hot-spot screening for a catalytic packing inside a column:
  `reactor-hazards` needs a reactor model with kinetics.
- **L-5** No continuous column model for C-202 (methanol/water): its split and reflux are
  ASSUMED and its duties hand-estimated in the script.

## Open inputs

- The resin's life and replacement (D-010), and its poisons in a real raffinate.
- A real raffinate composition (butanes, 2-butenes) and the column's response to it.
- Heat integration (D-008) and the pressurised methanol column of SRC-3 (D-007).
- The start-up path to the high-conversion steady state (D-009).
