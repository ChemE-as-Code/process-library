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
closure 38267.3 kW in and out (formation enthalpies included, the pump temperature rise counted).

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
