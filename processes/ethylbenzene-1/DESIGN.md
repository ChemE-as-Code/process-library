# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#313 (PFD + LCI + simulation for the manifest-only pilots).
Run of 2026-11-03 (concept: design basis to balanced PFD, simulation and an LCI derived from the
flowsheet). Starting library commit dc8f2220 (origin/main), cheme-as-code 1.4.1 (the core commit
the library CI pins), DWSIM 9.0.5 in the `cheme-dwsim:9.0.5` container, thermo/chemicals as
bundled with cheme.

## Route and boundary memo

**Route.** Liquid-phase alkylation of benzene with ethylene on a large-pore zeolite (MCM-22 or
beta type) in fixed beds, C6H6 + C2H4 -> C8H10 (exothermic, -105.8 MJ/kmol at 298 K, ideal gas),
with the consecutive ethylation to polyethylbenzenes and their transalkylation with benzene back
to ethylbenzene (C10H14 + C6H6 -> 2 C8H10, nearly thermoneutral) in a second reactor. Benzene is
fed in excess and recycled; three columns separate benzene (recycle), ethylbenzene (product) and
the polyethylbenzenes (recycle to transalkylation) from a heavy residue (flux oil). The AlCl3 and
the vapour-phase ZSM-5 routes were not chosen (D-001).

**Plant boundary (battery limits).** From benzene and polymer-grade ethylene at the battery
limit to ethylbenzene, flux oil and exported 200 kPa(a) steam at the battery limit. Outside:
benzene and ethylene production, feed and product storage, feed pretreatment (benzene drying
column, guard beds: the feeds are taken as dry and pure, D-003), vents and their abatement,
utility generation (HP steam, cooling water, power), catalyst regeneration. Utilities cross the
boundary as energy streams (power, HP steam in, steam raised out, cooling water).

```
 benzene ──> V-101 ─> P-101 ─> E-101 ─┬─> R-101 alkylator ──> E-101 ─┐
 ethylene ────────────────────────────┘   (steam raised)              │
              ^ recycle benzene                                       ├─> C-201 benzene ─> C-202 EB ─> E-207 ─> ethylbenzene
              │                       ┌─> P-102 ─> E-102 ─> R-102 ────┘   column (steam)   column (steam)
              │   recycle benzene ────┤                    transalkylator     │                 │
              │                       └── PEB recycle <── P-103 <── C-203 PEB column (vacuum) <─┘
              └─────────────────────────────── C-201 top                      └─> flux oil
```

**Cross-check, not input.** The manifest-only pilot of this process carried a Tier 1 dataset
written from the EU LVOC BREF (2017, chapter 5). Its sourced ranges are this design's
cross-check (D-015). Only the tar rate is taken from it as an input (D-005), because no open
source for the heavies make was read.

## Decisions

### D-001 Independent concept design of liquid-phase zeolite alkylation (2026-11-03)
Decision: design the plant from the route chemistry and openly cited facts with the units of the
issue: alkylator, transalkylator, benzene recycle, benzene, EB and PEB columns, tar (flux oil).
Reason: the route the issue names; in the BREF's data collection four of five EB plants use
zeolites (Table 5.9), and large-pore zeolites are named for the liquid phase (5.2.2.1.3.4).
Zeolite plants need no catalyst handling and washing units and run in carbon steel (5.2.2.1.2).
Rejected: AlCl3 (catalyst preparation, washes and their effluents), vapour-phase ZSM-5 (higher
temperature, not the issue's route). DWSIM or FOSSEE flowsheet files were not used for anything.

### D-002 Capacity and product specification (2026-11-03)
Decision: 400 kt/a EB product stream at 8000 h/a = 50 t/h; EB with benzene and DEB traces as the
column specifications give them (D-008): DEB 20 ppm mol (the styrene feed limits
polyethylbenzenes because they become divinylbenzene), benzene about 0.05 mol%.
Reason: a single train of the size that feeds a world-scale styrene unit (ASSUMED, no client
figure). Turndown 60 % not checked.

### D-003 Feeds (2026-11-03)
Decision: pure, dry benzene at 303 K, 500 kPa(a); pure ethylene at 298 K, 4000 kPa(a), above the
alkylator pressure, so no ethylene compressor.
Reason: the BREF's plants all use feeds above 99.5 % purity (Table 5.9); modelling the impurities
(water, sulphur, nitrogen compounds, ethane, non-aromatics) needs a drying column, guard beds and
a vent that the concept leaves out (open input I-01).
Assumptions: ASSUMED values; with ethane in the ethylene a vent from the benzene column is needed.

### D-004 Reactor conditions and ratios (2026-11-03)
Decision: alkylator R-101 at 513.15 K outlet, 3850/3750 kPa(a), benzene/ethylene 4.0 mol/mol at
its inlet; feed preheated to 473 K against the effluent in E-101; the multi-bed reactor with
ethylene distributed over the beds and interbed steam generators is modelled as one conversion
reactor held at its outlet temperature, whose heat raises 200 kPa(a) steam. Transalkylator
R-102 adiabatic, inlet 503.15 K (E-102, HP steam), 3850/3750 kPa(a), benzene/DEB 3.0 mol/mol.
Pressure drops 50 kPa per exchanger side, 100 kPa per reactor (ASSUMED).
Reason: benzene/ethylene inside the BREF's plant range 3.27 to 8 (Table 5.9) and at the 3 to 4
it names for MCM-22 and about 4 for beta (5.2.2.1.3.4). The temperatures sit inside the 160 to
320 C range of the patent example used in D-005; at 3750 kPa(a) the effluent is liquid
(benzene's vapour pressure at 513 K is about 2.6 MPa). The pressure is above the 20 to 40 bar
of the BREF's liquid-phase catalyst wash (5.2.2.1.3.5) at its low end, a plausibility check only.
Assumptions: the alkylator inlet is two-phase (about 15 % vapour, ethylene, scripts/eb_balance.py)
because all ethylene is added at one point in the model; the reactions are therefore declared
`phase: mixed`. Real reactors inject the ethylene between beds so that it dissolves.

### D-005 Reaction model (2026-11-03)
Decision: R-101 converts all ethylene (ASSUMED) through three lumped reactions from benzene and
ethylene: ALK (to EB) 0.886792, DIALK (to DEB) 0.102987 and PENTA (to the flux oil) 0.010220 of
the inlet ethylene. R-102 converts 0.65 of the DEB per pass (TRANS, ASSUMED). The lumping lets
DWSIM's conversion reactor (one conversion per reaction, on the inlet) reproduce the shares.
Reason: the ethylene shares come from the product distribution of US5493065A Example 7 (MCM-22,
220 C, benzene/ethylene 5.5, 97 % ethylene conversion: EB 94.0, DEB 5.7, TEB 0.2 mol% of the
products; process/reaction-evidence.yaml O1): (2 x 5.7 + 3 x 0.2)/(94.0 + 11.4 + 0.6) = 0.1132
of the ethylene ends in polyethylbenzenes. PENTA takes its share so that the flux oil is 4.3 kg
per t EB, the midpoint of the BREF's 3 to 5.6 kg/t for zeolite plants (5.3.6.1.2), solved in
scripts/eb_balance.py. TEB is lumped with DEB (both are transalkylated).
Model compounds (ASSUMED): 1,4-diethylbenzene for all polyethylbenzenes;
1,2,3,4,5-pentaethylbenzene for the flux oil, which the BREF describes only as mono- and
polycyclic aromatics of 10 carbons or more. Pentaethylbenzene forms from benzene and ethylene
without hydrogen, so the element balance closes without the invented hydrogen off-gas that the
Tier 1 dataset's 1,1-diphenylethane needed; DWSIM has both model compounds (ChemSep, ChEDL), it
has no diphenylethane.
Consequence: pentaethylbenzene carries more ethylene per kg than diphenylethane, so the ethylene
use comes out 0.7 % above the BREF's range (D-015).
Rejected: kinetics (none read with a validity range); an equilibrium transalkylator (no
equilibrium data checked for the DEB isomers).
Assumptions: the O1 shares, measured at ratio 5.5 in one lab bed, hold at ratio 4.0 in a
multi-bed reactor; a lower ratio makes more polyethylbenzenes, so DEB is likely under-predicted
(open input I-02). Side products of O1 below 0.1 mol% (sec-butylbenzene, other C9+) are left
out; xylenes are not formed.

### D-006 Independent balance script; property method not qualified (2026-11-03)
Decision: scripts/eb_balance.py solves the plant independently (thermo 0.6 Peng-Robinson with
the ChemSep kij set, which has only the ethylene-benzene pair; ideal-gas heat capacities of
thermo; formation enthalpies of process/materials.yaml), with the column splits from the D-008
specifications, Underwood minimum reflux at constant relative volatility and column energy
balances on the arriving feed. The flowsheet cites from it only the feed flows S1 and S6 (and
the split fraction of SPL1); everything else is calculated by cheme (simulate, propagate).
Reason: core has no qualified property package for aromatics (its packages cover air and
syngas): `cheme process props --fill` refuses every stream and `cheme maturity` fails
predictive.property-regime. As in hda-1, the DWSIM run (D-014) is a second implementation of
Peng-Robinson checked against this script, not validated data.
Results: loop residual below 1e-13 (27 iterations); mass 50215.0 kg/h in and out; overall energy
closure 38264.4 kW in and out (formation enthalpies included, the pump temperature rise counted).

### D-007 Recycles (2026-11-03)
Decision: the benzene column distillate (99.9 mol% benzene, 0.1 % EB) is split: 92.68 % to the
alkylator (benzene/ethylene 4.0), the rest to the transalkylator (benzene/DEB 3.0); the PEB
column distillate is recycled to the transalkylator. No purge: the feeds carry no inerts (D-003).
Results: recycle benzene 120.7 t/h (2.6 kg per kg EB), PEB recycle 5.1 t/h.

### D-008 Separation train (2026-11-03)
Decision: three columns in the BREF's common sequence (5.2.2.1.4): C-201 benzene column at
450/480 kPa(a) (EB 0.1 mol% in the distillate, benzene 0.05 mol% in the bottoms); C-202 EB column
at 150/170 kPa(a) (DEB 20 ppm mol in the EB, EB 0.5 mol% in the bottoms); C-203 PEB column under
vacuum at 20/30 kPa(a) (heavies 0.01 mol% in the PEB recycle, DEB 2 mol% in the flux oil).
Reflux 1.3 x the Underwood minimum, at least 0.3; total condensers; the EB product cooled to
313 K in E-207 (cooling water).
Reason: C-201's pressure puts its condensing temperature at about 411 K, so its condenser raises
200 kPa(a) steam (the BREF's 2 bar steam from this condenser, 5.3.5) with a 17 K approach; C-202
inside the BREF's 1.1 to 1.7 bar for the EB column, also condensing above 420 K; C-203 under
vacuum so that its bottoms stay below 300 C (5.2.2.1.4: about 494 K here). All three reboilers
take HP steam (526 K saturation).
Assumptions: ASSUMED values; stage counts are DWSIM's shortcut estimates where usable (D-014);
the reflux and distillate pumps are implicit (not PFD steps, their power is a cut-off, D-013).
The BREF's benzene drag (lights) column is not needed with pure feeds.

### D-009 By-product and heat dispositions (2026-11-03)
Decision: the flux oil leaves as a by-product (flux oil in a styrene plant or fuel, both uses the
BREF reports, 5.3.6.1.2); the heat of R-101 and of the C-201 and C-202 condensers raises
200 kPa(a) steam that is exported (to the site or the styrene unit, 5.3.5).
Reason: the BREF's plants recover the alkylation heat and the overhead heat as steam; the
reaction heat could raise a higher level than 200 kPa(a) (open input I-05).

### D-010 Utilities and machines (2026-11-03)
Decision: HP steam 4200 kPa(a) (526.4 K) for all reboilers and E-102; steam raised at 200 kPa(a)
(393.4 K); cooling water 298/308 K; electric pumps with efficiency 0.65; minimum approaches 10 K
(steam) and 5 K (cooling water). All ASSUMED.

### D-011 Core findings met in this run (2026-11-03)
For core: (1) DWSIM's conversion reactor needs a vapour outlet even for a liquid-phase reactor,
and the empty outlet gets an all-zero composition that `cheme validate` then refuses
(placeholder used, D-014); (2) the `sim-utility-level` check reads a cooled exothermic reactor as
a stream heated from inlet to outlet and reports that the cooling utility "cannot cool it";
(3) the DWSIM mixer temperatures of D-014 (I-07); (4) DWSIM's shortcut column gives an Underwood
minimum of -154 for a hot, partly flashing feed. None is filed yet: to report with the PR.

### D-012 Lists (2026-11-03)
Decision: the equipment list holds the 18 items the PFD links (no P&ID, no sizes, no plot plan
at this stage, as the issue's scope says). Design pressures and temperatures are ASSUMED concept
values: the highest operating value + 10 % (at least + 2 bar) and + 25 K, one design pressure
(43 barg) for the reactor section; carbon steel throughout (BREF 5.2.2.1.2). The line and
instrument lists stay empty until the P&IDs. The concept gate `layout-plot-plan` fails: no plot
plan in scope (open input I-08).

### D-013 LCI from the flowsheet replaces the Tier 1 dataset (2026-11-03)
Decision: `lca/lca.yaml` with functional unit 1 kg ethylbenzene at the gate (product
`ethylbenzene`), design case, cradle-to-gate study with the foreground inventory only: every
exchange from the simulated flowsheet, every background `missing:` with the activity it should
connect to. Co-products flux oil and exported steam by `shares` 1/0/0 (all burdens to EB, no
credit), `dataset.system_model: cutoff`; substitution listed for comparison with its backgrounds
open. `cheme assess lca --write` writes `lca/dataset.yaml`, which becomes the process's LCI.
The hand-written Tier 1 dataset `lca/datasets/ethylbenzene-zeolite-liquid-phase.yaml` is
**removed**.
Reason for removing it: every plant folder of the library carries one flowsheet-derived
`lca/dataset.yaml` and no `lca/datasets/` (only manifest-only processes have those);
`scripts/build_lci.py` reads both, so keeping it would export two activities of
`ethylbenzene` from one process; it was never in a release (no release exists), so the
governance rule that keeps released datasets with `superseded_by` (docs/governance.md 5) does
not apply. Its sourced facts are kept as the cross-check (D-015) and in
`benchmarks/styrenics.yaml`; its inventory keys are kept (`feed:benzene`, `feed:ethylene`,
`feed:electricity`, `feed:steam`, `product:ethylbenzene`: the flowsheet's terminal ids are lower
case on purpose), so styrene-1's link changes only its path and the benchmark bindings keep their
expressions. The steam stays `feed:steam` with the shared `steam-heat` mapping (heat delivered,
kWh), as before.
Shares 1/0/0: the Tier 1 dataset credited no heat recovery either; nitric-acid-1 and
sulfuric-acid-1 treat exported steam the same way. The `allocation.deviation` states why energy
or exergy allocation is not used. Omissions declared: fugitive leaks (the BREF's upper bounds
10 g benzene and 50 g VOC per t are quoted, not counted), storage, no process effluent (drying
column outside the boundary; the BREF's 0.117 to 0.144 m3/t is quoted), no combustion, catalyst
regeneration; cut-offs: implicit column pumps (about 0.8 kWh/t) and the vacuum system (about
0.4 kWh/t), and the zeolite (7.5 g/t, the BREF midpoint, with no background yet).
Results: see the LCI summary below. `cheme assess lca --balance`: mass, C and H closed; the
energy closure reads 123.6 % because the reaction heat (and the feeds' and products' heating
values) are not in its basis: the exported steam exceeds the steam bought by the alkylation heat.
The catalog gets no LCA result while every background is a gap (process.yaml `lca.source: none`).

### D-014 DWSIM simulation of the whole plant, an unqualified cross-check (2026-11-03)
Decision: `cheme process simulate` runs the whole flowsheet with nothing excluded (core v1.4.1,
DWSIM 9.0.5, Peng-Robinson); every stream value and duty downstream of the feeds is DWSIM's
(`calculated`), the specs are in `process/simulation.yaml`, each repeating a D-004, D-008 or
D-010 choice. Tears S8 (feed/effluent loop), S19 (recycle benzene) and S12 (PEB recycle) with the
script's values as first guesses. The run converged; enthalpy closures: plant -0.10 kW
(tolerance 152 kW), R-101 and R-102 on the formation basis below 0.001 kW. Run record
`process/simulation-run.json`.
Status: Peng-Robinson is **not qualified by core for these aromatics** (`cheme maturity`
predictive.property-regime fails; `interaction_parameters_available: false`). The simulation is a
second implementation's check of scripts/eb_balance.py, not validated data.
Changes the run needed (none moves a design target):
- R-101 and R-102 have a liquid and a vapour outlet (S9, S17): DWSIM's conversion reactor with one
  outlet is taken as all vapour. Both vapour outlets carry no flow. DWSIM writes an all-zero
  composition for an empty outlet, which `cheme validate` refuses (composition sum 0), so S9 and
  S17 carry an ASSUMED placeholder composition (pure benzene) with the reason; a core finding.
- C-202 reflux: the D-008 rule 1.3 x Rmin is kept but applied to DWSIM's Underwood minimum, 0.742,
  so R = 0.97 instead of the script's 0.67 (Rmin 0.519): the C-201 bottoms arrive at 480 kPa(a)
  and 482 K and partly flash in the 150 kPa(a) column; the script's constant-volatility Underwood
  gives a lower minimum. R = 0.67 does not converge in DWSIM. The script reports C-202 at R = 0.97
  as well for the comparison.
- C-201: DWSIM's shortcut reports a meaningless minimum reflux (-154) and stage count (418) for
  the hot feed letting down from 3700 kPa(a); its duties follow from the given reflux and agree
  with the script. A rigorous column (40 stages) failed in DWSIM's PR flash. Stage count open
  (I-06; the BREF names about 60 trays).
- C-203: the shortcut with 0.1 mol% heavies in the distillate gave flux-oil fractions summing to
  0.9986 (an error); with 0.01 mol% (D-008 as now written) the sum is 0.9993, accepted as a
  `pydexpi_composition_fractions` warning like hda-1's. A rigorous C-203 did not converge
  (10 and 14 stages, reflux 0.3 and 0.5). DWSIM estimates 13.2 theoretical stages at R 0.3.
- Pressures of S7, S8, S9, S10, S18 follow DWSIM's mixer convention (the lowest inlet pressure).
Comparison with the independent script (same specs; C-202 at R 0.97):

| quantity | DWSIM | script | deviation |
|---|---|---|---|
| R-101 heat to steam (Q4) | 8706 kW | 8767 kW | -0.7 % |
| C-201 condenser / reboiler (Q7 / Q6) | 19417 / 17711 kW | 19453 / 17618 kW | -0.2 / +0.5 % |
| C-202 condenser / reboiler (Q9 / Q8) | 8980 / 7234 kW | 8986 / 7157 kW | -0.1 / +1.1 % |
| C-203 condenser / reboiler (Q11 / Q10) | 604 / 352 kW | 607 / 353 kW | -0.5 / -0.2 % |
| E-207 product cooler (Q12) | 3058 kW | 2965 kW | +3.1 % |
| E-101 feed/effluent (internal) | 6093 kW | 7463 kW | -18.4 % |
| E-102 transalkylator heater (Q5) | 732 kW | 841 kW | -12.9 % |
| pumps P-101 / P-102 / P-103 (Q1-Q3) | 289.8 / 27.7 / 1.2 kW | 270.8 / 26.9 / 1.3 kW | +7.0 / +2.9 % |
| C-201 bottoms S20, C-202 bottoms S23 | 55296 / 5296 kg/h | 55288 / 5288 kg/h | +0.01 / +0.14 % |
| recycle benzene S19, flux oil S25 | 120741 / 215.0 kg/h | 120741 / 215.0 kg/h | 0.0 % |
| EB product purity S22 | 99.944 mol% | 99.944 mol% | 0.0 |
| column tops C-201 / C-202, bottom C-203 | 411.1 / 424.7 / 494.5 K | 411.2 / 424.6 / 494.6 K | < 0.1 K |
| mixers M101 / M103 outlet | 403.3 / 419.0 K | 387.3 / 406.3 K | +16 / +13 K |

The reactor heat, every column and the material balance agree within about 1 %. The two
mixers do not: DWSIM's adiabatic mixer M103 returns 419.0 K from inlets at 411.1 and 400.5 K,
above both, which is not possible for nearly ideal liquid aromatics, and M101 is 16 K hotter
than a heat-capacity-weighted mix (about 384 K). The E-101 and E-102 duties, and the pump power,
follow from these inlet temperatures. Not resolved in this run (I-07): the LCI takes DWSIM's
values (E-102 is the only one that reaches a utility; its 109 kW difference is 2.2 kWh/t of HP
steam). Other findings of the run: `sim-formation-data` for R-102 (DWSIM's ChemSep DEB -22300
against the declared -20370 kJ/kmol, API TDB; the transalkylation heat is only -3 MJ/kmol, so the
1 % tolerance is 0.1 kW; the declared value is kept); `sim-utility-level` for R-101 (the
utility check treats the reactor as a stream heated from 453 to 513 K while it is cooled, so the
200 kPa(a) steam cannot "cool" it on paper; the real interbed coolers see 513 K against 393 K
steam).

### D-015 Utilities and yields against the EU LVOC BREF (2026-11-03)
Decision: the BREF's ranges (chapter 5, the facts the Tier 1 pilot carried) are the cross-check of
the flowsheet-derived LCI; each is a KPI in `benchmarks/styrenics.yaml`, with an
`out_of_range_reason` where the design falls outside. Per t EB (from the DWSIM-filled flowsheet,
`lca/inventory.csv`; the script's figures in brackets):

| KPI | design | BREF range (locator) | status | why |
|---|---|---|---|---|
| benzene | 0.7374 t/t (0.7374) | 0.735 to 0.746 (5.3.4.1) | inside | near stoichiometry (0.7358) plus the flux oil's benzene; not independent |
| ethylene | 0.2669 t/t (0.2669) | 0.254 to 0.265 (5.3.4.1) | 0.7 % above | the flux oil is modelled as pentaethylbenzene (5 ethylenes per benzene); the Tier 1 model's diphenylethane gave 0.2649 |
| flux oil (tar) | 4.30 kg/t | 3 to 5.6 (5.3.6.1.2) | midpoint by design | an input (D-005) |
| electricity | 6.4 kWh/t (6.0) | 25 to 32 (5.3.5) | far below | only the three feed pumps are steps; reflux and vacuum pumps are cut-offs (about 1.2 kWh/t), cooling-water and drying-column duties and feed compression are outside the model (ethylene arrives at pressure, D-003) |
| steam used | 521 kWh/t (492 at the script's own C-202 reflux, 519 at DWSIM's) | 100 to 2600 (5.3.5) | inside, low third | three columns at 1.3 x minimum reflux, the hot alkylator effluent preheats the C-201 feed |
| heat recovered (steam raised) | 742 kWh/t (717; 744 at DWSIM's C-202 reflux) | 700 to 2600 (5.3.5) | inside, low end | reaction heat 174 kWh/t, C-201 condenser 388 kWh/t, C-202 condenser 180 kWh/t, all at 200 kPa(a) |
| electricity + steam | 527 kWh/t | total 760 to 2600 (5.3.5) | below | follows from the two rows above; how the BREF nets recovery in its total is not stated |
| zeolite spent | 7.5 g/t (cut-off) | 3 to 12 (5.3.4.2) | midpoint by choice | not a design result |
| wastewater | none in the model | 0.117 to 0.144 m3/t (5.3.3.1) | excluded | drying column outside the boundary (D-013) |

Reading: the design is a well heat-integrated plant: it exports more steam (742 kWh/t, at low
pressure) than it buys (521 kWh/t, HP), which is what the BREF's recovery range says integrated
plants do. Its gross steam is a third of the Tier 1 midpoint (1350 kWh/t), which had no design
behind it. The electricity is not comparable until the pumps and the vacuum system are sized
and the cooling-water circulation is counted. The yields are close to stoichiometry in both
the BREF and the design, so they check the balance, not the chemistry.

## LCI summary (lca/inventory.csv, per kg ethylbenzene)

| exchange | amount | unit | provenance (flowsheet) | background to link later |
|---|---|---|---|---|
| feed:benzene | 0.737412 | kg | S1 (assumed, script) | benzene, aromatics complex or hda-1 |
| feed:ethylene | 0.266888 | kg | S6 (assumed, script) | ethylene, steam cracker (ethylene-1) |
| feed:electricity | 0.006373 | kWh | Q1 to Q3 (DWSIM) | electricity, medium voltage |
| feed:steam | 0.520573 | kWh | Q5, Q6, Q8, Q10 (DWSIM) | HP steam, site boiler |
| product:ethylbenzene | 1 | kg | S22 (design basis) | functional unit |
| product:flux_oil | 0.004300 | kg | S25 (DWSIM) | co-product, share 0 |
| product:steam_export | 0.742063 | kWh | Q4, Q7, Q9 (DWSIM) | co-product, share 0 (substitution: LP steam) |
| product:cw | 0.073243 | kWh | Q11, Q12 (DWSIM) | cooling water circulation |

Checks: `cheme assess lca --balance` mass 50215 kg/h in and out, C 45442.4 and H 4772.6 kg/h
closed. `--coverage`: partial screening carbon footprint, 5 gaps, no total; DQR 2.33.

## Reaction and model evidence

`process/reaction-evidence.yaml` (skills reaction-evidence-search and route-selection): sources
S1 (LVOC BREF, read in full for chapter 5) and S2 (US5493065A, read in full text), observations
O1 to O3, route LIQ-ZEO selected, model basis D-005. `cheme chemistry evidence` lists the gaps:
G1 shares at the design ratio, G2 transalkylation conversion, G3 flux oil composition, G4
catalyst deactivation.

| item | value used | source | status |
|---|---|---|---|
| Stoichiometry ALK, DIALK, PENTA, TRANS | reactions.yaml | route chemistry | sourced (textbook chemistry) |
| Heats of reaction | -105.84, -208.67, -521.18, -3.01 MJ/kmol | formation enthalpies (chemicals: ATcT, CRC, API TDB, TRC) | calculated |
| Ethylene shares EB / PEB | 0.8868 / 0.1132 | US5493065A Example 7 (O1), at ratio 5.5 | transferred to ratio 4.0, ASSUMED |
| Ethylene conversion | 1.0 | O1 has 0.97 in one lab bed | ASSUMED |
| Flux oil | 4.3 kg/t EB | LVOC BREF 5.3.6.1.2 (3 to 5.6, midpoint) | sourced amount, ASSUMED compound |
| Benzene/ethylene | 4.0 | BREF Table 5.9 (3.27 to 8), 5.2.2.1.3.4 (3 to 4 MCM-22) | inside the sourced range |
| Transalkylation | X(DEB) 0.65 at benzene/DEB 3 | none read | ASSUMED (G2) |

## Source register

| source | locator | access in this run | terms | use |
|---|---|---|---|---|
| Falcke, H. et al. (2017) LVOC BREF, EUR 28882 EN, doi:10.2760/77304 | chapter 5: 5.2.2.1 to 5.2.2.1.4 (pp. 242-253), 5.3.4.1 and Table 5.9 (p. 280), 5.3.4.2 (p. 281), 5.3.5 (p. 282), 5.3.6.1 (pp. 283-284) | full text of the JRC PDF | EU reuse policy; facts and numbers in our own form | route, ratios, column conditions, tar rate, cross-check ranges |
| US5493065A (1996) Liquid phase ethylbenzene synthesis with MCM-49 | Example 7 | full text (Google Patents) | patent; facts only | ethylene shares (O1) |
| `chemicals`/`thermo` Python packages (bundled with cheme) | ATcT, CRC, API TDB, TRC, Yaws, HEOS, IUPAC, PinaMartines, ChemSep PR kij | used | MIT; underlying data facts | formation data, critical constants, PR flash |
| DWSIM 9.0.5 compound databases (ChemSep, ChEDL Thermo) | p-diethylbenzene, pentaethylbenzene | used inside the simulation | GPL v3 software; no flowsheet file used | simulation |

No DWSIM or FOSSEE flowsheet file and no licensed database value is used.

## Open inputs

- I-01 Feed specifications (benzene water and non-aromatics, ethylene ethane and methane) and the
  pretreatment they need: drying column, guard beds, a lights vent.
- I-02 Ethylene shares and conversion at the design ratio and conditions (licensor or plant
  data); the transalkylator conversion and its approach to equilibrium.
- I-03 Flux oil composition and its model compound.
- I-04 Capacity and operating hours from an owner (400 kt/a, 8000 h/a are assumed).
- I-05 Steam levels: the reaction heat could raise MP steam; where the exported steam is used.
- I-06 Stage counts and a rigorous model of C-201 and C-203 (DWSIM's shortcut is unusable for
  C-201's stage count; rigorous runs failed, D-014).
- I-07 The DWSIM mixer temperatures M101 and M103 (16 and 13 K above the script, M103 above both
  inlets): find whether DWSIM's PR liquid enthalpy or the mixer is at fault (D-014).
- I-08 Concept economics and plot plan (gate `layout-plot-plan`, class 5 estimate, screening TEA):
  not in this run's scope.
