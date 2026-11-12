# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#313 (DWSIM/FOSSEE pilot: PFD + LCI + simulation). Run of
2026-11-03, concept stage only (no P&IDs, HAZOP, layout or economics). cheme-as-code v1.4.1
(pinned in the library CI), DWSIM 9.0.5 in the `cheme-dwsim:9.0.5` container, thermo/chemicals
as bundled with cheme. Until this run styrene-1 was a manifest-only pilot with a hand-written
Tier 1 dataset from the LVOC BREF; that dataset is the cross-check of D-014.

## Route and boundary memo

**Route.** Adiabatic catalytic dehydrogenation of ethylbenzene (EB) with superheated steam over
potassium-promoted iron oxide: C8H10 <=> C8H8 + H2 (endothermic, +118 kJ/mol at 298 K), with
toluene, benzene, light gases and heavies as by-products. About 85 % of styrene is made this way
(LVOC BREF 5.2.1.2, p. 240). Not modelled: the PO/SM co-production route, isothermal
(steam-heated tubular) reactors and oxidative reheat.

**Plant boundary.** From fresh EB, dilution steam (site MP header), natural gas and air at the
battery limit to styrene, benzene, toluene and tar at the battery limit, process condensate to
the stripper, flue gas to the stack. Inside: feed vaporisation, the steam superheater (SSH) with
its burners, two adiabatic beds with interstage reheat, effluent heat exchange and condensation,
three-phase separation, off-gas compression, fractionation with EB recycle. Outside: EB
production (ethylbenzene-1), steam and power generation, cooling tower, condensate stripping and
wastewater treatment, storage, flare, vacuum systems (as cut-off flows, D-013).

```
 EB ──┐                    ┌─ steam superheater (off-gas + natural gas burners) ─> stack
      ├─> vaporise (E-101) ─> bed 1 ─> reheat (E-102) ─> bed 2 ─> E-101 ─> condenser E-103
 steam┘          ^                                                         │
                 │                     off-gas <─ K-101 <─ V-101 three-phase separator
                 │                                         │            └─> process condensate
                 │                                   crude styrene (inhibitor)
                 │                     C-301 B/T column ─> C-304 ─> benzene, toluene
                 └──── EB recycle <──── C-302 EB/styrene splitter ─> C-303 ─> styrene, tar
```

**Primary source and leads.** Facts come from the EU LVOC BREF (Falcke et al. 2017, EUR 28882 EN,
doi:10.2760/77304), chapter 5, read in this run (sections and pages cited at each use), and the
aqueous solubilities from PubChem's HSDB records. The DWSIM/FOSSEE collection entry 231 and its
stated reference (Luyben, Ind. Eng. Chem. Res., styrene process) were leads only: no DWSIM file
was downloaded or opened, and the paper was not read in this run, so nothing of either is used
(issue #313 rule: if a value cannot be traced to a source other than the DWSIM file, it does not
go in). The private blind comparison with the DWSIM entry that #313 plans is open (I-08).

## Decisions

### D-001 Independent concept design (2026-11-03)
Decision: design the plant from the route chemistry and the LVOC BREF's facts, with the units of
the issue: adiabatic dehydrogenation with superheated steam, effluent cooling and condensation,
three-phase separation, B/T/EB/styrene distillation with EB recycle, inhibitor and tar.
Reason: #313 asks for a PFD, an LCI and a simulation from an independent source.
Rejected: rebuilding the DWSIM/FOSSEE flowsheet (CC BY-SA; facts and leads only).

### D-002 Capacity and product (2026-11-03)
Decision: 300 kt/a styrene product stream at 8000 h/a = 37.5 t/h, one train in the model;
product at least 99.8 wt% styrene (BREF 5.2.3.1.3, p. 256), the simulated product is 99.85 wt%
with ethylbenzene the impurity.
Reason: the BREF's catalyst charge (120-160 t) refers to a 300 kt/a plant (5.2.3.1.1, p. 255).
The BREF's plants have 70-100 kt/a per reactor and several reactors (p. 256): a real plant of
this size would have parallel reactor trains; the model lumps them (ASSUMED).

### D-003 Feeds (2026-11-03)
Decision: fresh EB pure at 303 K and 300 kPa(a) (the BREF's fresh EB is 97.5-99.8 %, Table 5.11,
p. 285; impurities not modelled); dilution steam from the site MP header at 1100 kPa(a), 3 K
above saturation (460.2 K) so that no model reads it as liquid; natural gas as pure methane at
400 kPa(a); dry air (N2 0.79, O2 0.21) at 105 kPa(a). All ASSUMED.

### D-004 Reaction section conditions (2026-11-03)
Decision: two adiabatic radial beds in series; each inlet 893.15 K (620 C, BREF 5.2.1.2, p. 240);
pressures 85 -> 75 kPa(a) (bed 1) and 70 -> 60 kPa(a) (bed 2), i.e. under vacuum held by the
off-gas compressor (BREF Table 5.10: 300-500 mbar vacuum level); steam to EB 1.3 kg/kg at bed 1
(BREF 1-1.8 kg/kg, 5.2.3.1.1, p. 255; Table 5.10 0.67-1.5); 10 % of the steam is primary steam
mixed with the EB; EB and primary steam vaporised and preheated to 793.15 K (520 C, BREF
5.2.3.1.1, p. 255) against the effluent in E-101; the main steam is let down to 150 kPa(a),
superheated to 1073.15 K in SSH coil 1 (below the BREF's up to 900 C, 5.3.1.2.1, p. 269), heats
the bed 1 effluent back to 893 K in the interstage reheater E-102, is superheated again in coil 2
and mixed with the EB feed. Pressure drops (10 kPa per bed and per exchanger side, 15 kPa per
coil) ASSUMED.
Reason: the BREF describes the adiabatic multi-bed arrangement with superheated steam as the
heat carrier and interstage reheat (5.2.3.1.1, pp. 254-255); two beds are the smallest number
its plants report (Table 5.10).
Results (script): coil 2 outlet 1008 K for the 893 K mixed inlet; bed 1 outlet 814 K, bed 2
outlet 846 K; E-101 25.7 MW with the effluent leaving at 565 K.

### D-005 Reaction model: conversion beds with assumed selectivities (2026-11-03)
Decision: each bed a conversion reactor keyed on EB: 40 % of the inlet EB per bed (64 % overall,
inside the BREF's typical 60-65 %, 5.2.3.1.1, p. 255, and 50-70 %, 5.2.1.2, p. 240), split by
molar selectivities per mol EB converted: styrene 0.952 (BREF: above 90 %, yields 88-95 mol%),
toluene 0.028 (EB + H2 -> toluene + CH4), benzene 0.012 (EB -> benzene + ethylene), tar 0.008
(lumped 2 EB -> biphenyl + 2 ethylene + H2). All ASSUMED, chosen so that the by-products fall
inside the BREF's ranges (toluene 16-94, benzene up to 20, tar 6.4-12.9 kg/t, 5.3.6.2 and Table
5.11, p. 285). No rate law: the bed volumes are not sized.
Tar proxy: biphenyl stands in for the oligomers and high boilers of the tar (BREF 5.3.6.2,
p. 286), only for its boiling point and because DWSIM and thermo know it; trans-stilbene was
tried first and is not in DWSIM's database. The TAR reaction is element-balanced, not a
mechanism.
Not modelled: CO and CO2 from the steam gasification of coke (BREF 5.2.1.2), C2 hydrocarbons
other than ethylene, alpha-methylstyrene, catalyst ageing (benzene rising over the run).
Equilibrium check (script, ideal gas with the formation data of materials.yaml): ln(Q/K) of the
dehydrogenation is -1.04 at the bed 1 outlet and -0.54 at the bed 2 outlet, so both beds stay on
the forward side of equilibrium (Q/K 0.35 and 0.58).
Results: styrene yield 0.940 mol per mol fresh EB; EB 1082.9 kg/t styrene.

### D-006 Independent balance script; property method not qualified (2026-11-03)
Decision: scripts/sm_balance.py computes the recycle, the feed flows, every duty and the
separations: ideal gas with the formation enthalpies and cp polynomials of materials.yaml for
the gas side; ideal liquids (h = h_ig - Hvap, thermo heats of vaporisation and vapour pressures);
water and the aromatics as immiscible liquids (D-008); shortcut columns with specified key
splits, Underwood minimum reflux at constant relative volatility (feed taken as saturated liquid)
and R = 1.3 Rmin (at least 0.5); duties from the column energy balances with the arriving feed.
It follows the balance-output contract (ADR 0027): the flowsheet cites it for the feed flows S1,
S3, S36, S37 and for the off-gas section (S21, S22, Q3, Q5).
Reason: core has no qualified package for aromatics with water and hydrogen (core#315), as for
hda-1; the script is the basis the simulation is checked against.
Results: recycle converged to 6e-11; mass in 165 700.68 kg/h, out 165 700.68 kg/h; overall
energy closure 6.7 kW in 264 MW (enthalpies with formation; the pump temperature rise is
neglected).

### D-007 Condensation, separator and off-gas compression (2026-11-03)
Decision: the effluent is cooled from 566 K to 313.15 K in E-103 (cooling water) and separated
at 45 kPa(a) in V-101; the off-gas (74 mol% H2 with 16 % water vapour and 5 % aromatics) is
compressed by K-101 from 45 to 300 kPa(a) in one stage in the model (isentropic efficiency 0.75,
outlet 528 K), cooled to 313.15 K (E-104) and knocked out (V-102); the condensate joins the
separator liquid. ASSUMED. Two stages with intercooling are expected at basic engineering (a
pressure ratio of 6.7 in one stage is high).
Reason: the off-gas compressor holds the reactor vacuum and delivers the hydrogen-rich gas to the
burners, as in the BREF's description (5.2.3.1.2, p. 256).
Not modelled: the aromatics absorber or chilled recovery of the off-gas (BREF 5.2.3.1.2; 5.3.6.2,
p. 286): 11.3 kg/t of aromatics go to the burners as fuel (I-03).

### D-008 Separations: water/aromatics LLE and the columns (2026-11-03)
**Liquid-liquid equilibrium.** Water and the aromatics are taken as immiscible liquids. In the
script's flashes (V-101, V-102), the water phase is pure water, the organic phase an ideal
solution (Raoult's law), the light gases stay in the vapour. In the decanter X-101 the aqueous
phase carries each aromatic at its aqueous solubility times its mole fraction in the organic
phase (solubility at 25 C from PubChem/HSDB: benzene 1790, toluene 526, EB 169, styrene 300 mg/L;
biphenyl taken as 0); all water and the few dissolved light gases go to the condensate (water
dissolved in the crude styrene, about 0.05 wt%, not modelled: ASSUMED negligible). Result:
21.7 kg/h aromatics in 81.8 t/h condensate (about 265 mg/kg), 0.58 kg/t styrene. In the DWSIM model these three units are specified splits with the script's recoveries
(D-012): Peng-Robinson's two-phase flash cannot represent the split. The decanter temperature
dependence of the solubilities (40 C instead of 25 C) is not modelled.
**Columns** (all total condensers, LP steam reboilers, ASSUMED specifications): C-301 B/T column
50/65 kPa(a), toluene 0.003 mol fraction in the bottoms, EB 0.02 in the distillate; C-304 B/T
splitter 45/60 kPa(a), benzene product 99.5 mol%, benzene 0.01 in the toluene; C-302 EB/styrene
splitter 10/25 kPa(a), EB 0.0015 in the bottoms (gives the 99.8 wt% product), styrene 0.02 in
the EB recycle; C-303 finishing column 8/12 kPa(a), tar with 30 wt% styrene to keep it fluid,
biphenyl 1e-5 in the product. Vacuum and inhibitor on every styrene column (BREF 5.2.3.1.3,
p. 256; skill tech-petchem-styrene-and-phenol); the styrene columns' bottoms stay below 378 K.
Reflux 1.3 x the Underwood minimum, at least 0.5. Stage numbers: DWSIM's shortcut (D-012).
Tar: biphenyl proxy plus styrene, 8.9 kg/t (BREF 6.4-12.9 kg/t, Table 5.11). The BREF's plants
use flux oil from the EB unit to dilute the column bottoms (Table 5.11 footnote); not modelled.

### D-009 Steam superheater and fuel (2026-11-03)
Decision: the SSH (H-101) burns the compressed off-gas and natural gas with 15 % excess air
(complete combustion, conversion 1.0 of every fuel component), adiabatic firebox; the flue gas
heats coil 2 (reheat to 1008 K) first and then coil 1 (main steam 445/460 -> 1073 K); the
natural gas is the make-up that brings the flue gas to a 523.15 K stack in the script. ASSUMED.
Reason: the BREF names the SSH as the largest energy user and three of its plants burn the
off-gas in it (5.3.1.2.1-5.3.1.2.2, pp. 269-270; Table 5.4).
Results (script): absorbed 31.6 MW, of which the off-gas covers 96 %: natural gas only 96 kg/h
(2.6 kg/t); SSH efficiency on LHV 0.91 (no radiation loss or air preheat modelled); adiabatic
flame 2285 K (above the 2200 K fit range of the CO2/H2O/N2 heat capacities: a small
extrapolation). The SSH's NOx, CO, SO2 and CH4 come from the BREF's Plant #5 (D-013).

### D-010 Utilities and machines (2026-11-03)
Decision: cooling water 298.15/308.15 K; LP steam 450 kPa(a) (420.8 K) for all reboilers (every
bottoms is below 400 K); electric drives; compressor isentropic efficiency 0.75, pump efficiency
0.65; P-201 (crude styrene, 45 -> 150 kPa(a)) and P-302 (EB recycle, 10 -> 300 kPa(a)) are the
only pumps on the PFD; reflux, product and condensate pumps, the column vacuum systems and the
combustion air fan are not in the flowsheet (cut-off flows of about 500 kW each, D-013); least
exchanger approach checked 20 K. All ASSUMED.

### D-011 Inhibitor, lists and materials (2026-11-03)
Decision: the polymerisation inhibitor (phenolic, BREF 5.2.3.1.3, p. 256) is dosed upstream of
C-301 at 0.075 kg/t (median of the BREF's three plants, Table 5.12, p. 285); it is not a stream
of the flowsheet (its 2.8 kg/h does not change the balance) but a consumable of the LCI. The
equipment list holds the 17 items the PFD links to, with ASSUMED design conditions (highest
operating value + 10 %, at least + 2 bar or full vacuum; + 25 K). Materials of the hot sections
(E-101, E-102, H-101, R-101/102) are an open input. No line or instrument list at this stage.

### D-012 DWSIM simulation of the plant (2026-11-03)
Decision: run `cheme process simulate` on the whole flowsheet except the off-gas compression,
with Peng-Robinson as a recorded substitution. It converged (four tears S10, S12, S16, S32 with
the script's first guesses); the simulated values are in process/flowsheet.yaml (`calculated`)
and process/simulation-run.json.
Property package: the selection facts (polar water, liquid-liquid split expected, no known
water-aromatics interaction parameters, 11 bar(a) at the steam feed) give PSRK or PR/RKS with
Huron-Vidal or Wong-Sandler mixing rules, none of which the DWSIM route runs; core names
Peng-Robinson as their substitute. At the separator's own 45 kPa(a) the tree gives UNIFAC-LL,
which the DWSIM route does not run at all. DWSIM's NRTL/UNIQUAC sets hold no water-EB or
water-styrene pair (checked in its database), so NRTL would have predicted no second liquid.
Peng-Robinson is therefore used as an unapproved substitution (`method_selection.substitution`),
and core's `methods.yml` benchmarks it only for N2/O2/Ar (core#315): `cheme maturity` fails
`predictive.property-regime`. The run is an unqualified cross-check of the script, not validated
data.
How the water/aromatics LLE is handled: a first run flashed V-101 with Peng-Robinson. Its
two-phase flash returned pure water as the liquid and left all the aromatics in the "vapour"
(one liquid phase only), and K-101's flash then failed. V-101, V-102 and the decanter X-101 are
therefore component separators with the script's recoveries (D-008): specified, not predicted
(the run record marks them `basis: specified`). K-101, E-104 and V-102 are excluded; S21, S22, Q3
and Q5 are the script's. E-103 still flashes its outlet with Peng-Robinson: its duty misses the
condensation of the organic phase, which then appears as the decanter's stated enthalpy residual
(-7.9 MW, `sim-energy-stated`).
Other changes the run needed: C-302's reflux 11.55 (1.3 x DWSIM's Underwood minimum 8.88; the
script's minimum is 6.75 from vapour pressures, and R 8.77 is below DWSIM's minimum); C-303 is a
rigorous column (10 stages, R 0.5, bottoms 334.1 kg/h from the script) because the shortcut's
tar fractions added up to 1.014; the steam feed is 3 K superheated (D-003). The generated PFD
carries five `pydexpi_composition_fractions` warnings (S27, S28, S31, S33, S38 sum to 1 within
8e-6, shortcut and mixer residue), as hda-1's.

| quantity | script | DWSIM | deviation |
|---|---|---|---|
| bed 1 outlet T (S14) | 813.6 K | 813.1 K | -0.5 K |
| bed 2 outlet T (S16) | 845.8 K | 845.6 K | -0.2 K |
| E-101 duty | 25.74 MW | 25.62 MW | -0.5 % |
| E-101 effluent outlet (S17) | 565.3 K | 565.8 K | +0.6 K |
| E-102 duty | 7.85 MW | 7.88 MW | +0.5 % |
| SSH coil 1 (H-101A) | 26.88 MW | 27.32 MW | +1.6 % |
| SSH coil 2 (H-101B) | 4.76 MW | 4.81 MW | +1.0 % |
| main steam after let-down (S9) | 460.2 K (ideal gas) | 445.3 K | -15 K (real-gas throttling) |
| flame (S39) | 2284.6 K | 2302.8 K | +18 K |
| stack (S41) | 523.15 K (sizes the natural gas) | 482.7 K | -40 K |
| E-103 duty | 79.74 MW | 74.05 MW | -7.1 % (organic phase not condensed in PR) |
| C-301 reboiler / condenser | 7.00 / 4.14 MW | 6.91 / 4.19 MW | -1.2 / +1.3 % |
| C-304 reboiler / condenser | 0.132 / 0.127 MW | 0.131 / 0.124 MW | -1.2 / -2.3 % |
| C-302 Rmin / R | 6.75 / 8.77 | 8.88 / 11.55 | +32 % |
| C-302 reboiler / condenser | 22.15 / 23.50 MW | 28.53 / 29.77 MW | +29 / +27 % |
| C-303 reboiler / condenser | 5.67 / 6.27 MW | 5.52 / 6.10 MW | -2.8 / -2.7 % |
| EB recycle (S32) | 23 055 kg/h | 23 055 kg/h | 0.00 % |
| styrene product (S34) | 37 500 kg/h, 99.85 wt% | 37 498 kg/h, 99.85 wt% | -0.005 % |
| tar (S35), styrene in it | 334.1 kg/h (spec), 38.8 mol% | 334.1 kg/h, 38.6 mol% | spec |

The reactor section, the SSH and three of the four columns agree within about 3 % (1 K for the
bed temperatures). Both sides use the same specifications, so this checks the arithmetic and the
gas-phase enthalpies, not the property model. The large differences have stated causes: C-302's
relative volatility (Peng-Robinson's EB/styrene volatility is lower than the vapour-pressure
ratio the script uses; the BREF names this splitter the main energy user, 5.3.5, p. 282), the
stack temperature (DWSIM's real-gas steam and flue-gas enthalpies leave about 1.3 MW more heat
for the coils at the script's natural gas: with DWSIM's numbers the natural gas could be lower
still) and E-103 (LLE, above). C-301's minimum reflux differs (2.0 in DWSIM, 23.5 in the script:
the script's Underwood is per mol of a very small distillate with the feed as saturated
liquid), but at the same R the duties agree.
DWSIM's formation enthalpies differ from materials.yaml by 33 kW on bed 1's reaction heat, inside
the 74 kW data tolerance (`sim-formation-data`).

### D-013 LCI: cradle-to-gate study, foreground from the flowsheet (2026-11-03)
Decision: lca/lca.yaml with functional unit 1 kg styrene (product STYRENE), design case; every
exchange from the flowsheet (`cheme assess lca --write`), no background linked in the study
(`missing:` for each, process.yaml `lca.source: none`, as hda-1); the library's LCI build links
the exported dataset: feed:EB to ethylbenzene-1's flowsheet dataset (PR #323), feed:DSTEAM to
utility-steam-ng-boiler (11 bar(a), pinned because ammonia-1 and hydrogen-1 also export steam),
feed:LPS as steam heat, feed:NG to pipeline natural gas (not the Atlas methane producer).
Allocation: mass between styrene, benzene and toluene (styrene 96.8 %), the pilot's choice; no
prices exist for the WBCSD price ratio (`allocation.deviation`). The tar (0.86 % of the output
mass) is a waste burned with energy recovery (cut-off keeps that treatment with the producer;
no open background yet). The SSH is inside the boundary: its CO2 (73 kg/t) is a foreground
emission; NOx, CO, SO2 and CH4 from the BREF's Plant #5 (5.3.1.2.1, pp. 269-270, midpoints)
as an emission estimate; particulates and NMVOC (together about 2.5 g/t) are declared but not
written (no single substance with a CAS number). Catalyst 140 t every two years (BREF
5.2.3.1.1, p. 255) and inhibitor 22.5 t/a as consumables. Cut-off: column vacuum systems and
small machines (about 500 kW each, ASSUMED). Excluded and declared: fugitive leaks (BREF 3-16
g/t), storage tanks, vacuum vents.
Reason: the issue's target is an LCI derived from the flowsheet; the study is cradle-to-gate with
the foreground only, so it claims no impact result of its own.
Results per t styrene (unallocated): EB 1083 kg, dilution steam 2186 kg, LP steam 1096 kWh,
natural gas 2.6 kg, power 29 kWh (plus about 27 kWh cut off), cooling water 3104 kWh, process
condensate 2182 kg, CO2 73 kg; co-products benzene 7.6 kg, toluene 25.9 kg; tar 8.9 kg.

### D-014 Cross-check against the pilot's sourced facts; the Tier 1 dataset (2026-11-03)
Decision: the hand-written Tier 1 dataset (`lca/datasets/styrene-eb-dehydrogenation.yaml`, LVOC
BREF midpoints and a closing balance) is removed; the flowsheet dataset `lca/dataset.yaml` is
the process's LCI, and the benchmark binding in benchmarks/styrenics.yaml moves to it.
Reason: the library has no process with both a flowsheet dataset and a Tier 1 one
(scripts/build_lci.py exports every `lca/dataset.yaml` and `lca/datasets/*.yaml` of a process, so
keeping both would put two styrene activities of one process into the Atlas); hda-1 and the
ethylbenzene-1 conversion (#323) follow the same rule. The old dataset stays in git history.
Comparison (per t styrene; the BREF ranges are 5.3.4.1, 5.3.5, 5.3.3.2, 5.3.6.2 and Table 5.11):

| quantity | LVOC BREF range | pilot (Tier 1) | this flowsheet |
|---|---|---|---|
| ethylbenzene | 1040-1100 kg | 1070 | 1083 |
| toluene | 16-94 kg | 23.6 (residual) | 25.9 |
| benzene | up to 20 kg | 10 (ASSUMED) | 7.6 |
| tar | 6.4-12.9 kg | 9.65 | 8.9 |
| hydrogen formed | up to 50 kg | (burned) | 19.0 (burned) |
| steam | 1850-2900 kWh | 2375 | 2746 (dilution steam 1650 as heat above 15 C water, reboilers 1096) |
| fuel | 1100-2900 kWh | 2000 | 928 (off-gas 892 + natural gas 36, LHV) |
| electricity | 50-170 kWh | 110 | 29 in the flowsheet, about 56 with the cut-off machines |
| total | 3200-4700 kWh | 4485 | 3703 (gross, no heat recovery credited) |
| effluent | 2.0-2.3 m3 | 2.15 | 2.18 (process condensate) |
| CO2 of the SSH | (not given) | 292 kg | 73 kg |

Where they differ: the fuel and CO2. The pilot read the BREF's fuel midpoint as including the
off-gas and made up the rest with natural gas; this design needs only 31.6 MW absorbed at 1.3 kg
steam per kg EB and a 91 % efficient SSH, which the off-gas almost covers. The BREF's plants run
at higher steam ratios, hotter SSH outlets, real furnace losses and some with more than two beds,
and their fuel range may include site fuel gas for other duties; the design's fuel is therefore
below the BREF's lower bound and its CO2 a quarter of the pilot's. Electricity is below the range
because the vacuum systems, fans and small pumps are outside the flowsheet. Steam is above the
pilot and inside the range, mainly through C-302 (D-012). The EB, toluene, benzene and tar
figures are inside the ranges by construction (D-005), not an independent check. There is no
licensor brochure among styrene-1's sources (the accepted brochure of #317 belongs to cumene-1).

## Open inputs

| id | what | why it matters |
|---|---|---|
| I-01 | fresh EB purity and impurities, real dilution steam pressure | feed definition (D-003) |
| I-02 | selectivities, per-bed conversion and catalyst ageing from a kinetic or plant source (e.g. the Luyben paper behind the #313 lead, once read) | yields, by-products, bed size (D-005) |
| I-03 | off-gas aromatics recovery (absorber or chilled condensation) | 11.3 kg/t aromatics burned (D-007) |
| I-04 | heat recovery from the effluent (LP steam raising, 566 -> about 420 K) and air coolers instead of cooling water | the BREF credits 210-840 kWh/t heat recovery; E-103 rejects 74-80 MW to cooling water (D-007) |
| I-05 | a property method qualified for water-aromatics LLE and the EB/styrene VLE | C-302 duty differs by 29 % between the two models; LLE is specified (D-012) |
| I-06 | two-stage off-gas compression, vacuum systems, fans: sized | electricity (D-010) |
| I-07 | fugitive, vacuum-vent and storage emissions | need P&ID counts (D-013) |
| I-08 | the private blind comparison against the DWSIM/FOSSEE entry 231 that #313 plans | lead check, recorded in our own words only |
| I-09 | materials of the hot section (E-101, E-102, H-101, R-101/102) | equipment list (D-011) |

## Source register

| id | source | used for |
|---|---|---|
| SRC-1 | EU JRC (2017) LVOC BREF, EUR 28882 EN, doi:10.2760/77304, chapter 5 (pp. 238-287), read 2026-11-03 | conditions (D-004), conversion and selectivity (D-005), separations and inhibitor (D-008, D-011), SSH and its emissions (D-009, D-013), catalyst, cross-check ranges (D-014); facts in our own form |
| SRC-2 | PubChem compound records (HSDB): water solubility of benzene (CID 241), toluene (1140), ethylbenzene (7500), styrene (7501), retrieved 2026-11-03 | decanter split (D-008) |
| SRC-3 | `chemicals`/thermo (bundled with cheme): formation data, heat capacities, critical constants, vapour pressures, heats of vaporisation | materials.yaml, the script (D-006) |
| lead | DWSIM/FOSSEE completed flowsheet 231 (styrene), CC BY-SA; its reference Luyben (Ind. Eng. Chem. Res.) | not opened, not used (D-001) |

## Method and dependency table

| unit | method | qualified? |
|---|---|---|
| reactors R-101/R-102 | conversion beds (assumed selectivities), adiabatic, ideal gas; DWSIM conversion reactors (PR) | no: conversion model, unqualified package |
| SSH B-101, H-101A/B | complete combustion, adiabatic; two-stream exchangers | no (PR, gas phase, beyond 2200 K fit) |
| V-101, V-102, X-101 | immiscible liquids + solubilities (script); specified splits in DWSIM | no: specified, not predicted |
| K-101, E-104 | ideal-gas compression (script only) | no |
| columns | shortcut (FUG) and rigorous C-303 in DWSIM; Underwood in the script | no (PR for aromatics unqualified) |
