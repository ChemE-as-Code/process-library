# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Numbers live in the YAML (`process/*.yaml`, `lca/lca.yaml`); this file keeps the reasons.
Issue: ChemE-as-Code/process-library#127. Stage: concept (design basis, balanced BFD/PFD,
preliminary gate-to-gate LCI). Run on library commit `11d50ef` (main), cheme-as-code 0.8.0
(pyDEXPI 2.1.0, Python 3.15.0, thermo 0.6.1).

## Source register

All sources were read for the facts named here; nothing is copied (facts restated in our own
words, numbers with their locator). Patents are public documents; facts and numbers from them
are used with citation.

| id | source | locator | read | used for |
|---|---|---|---|---|
| SRC-1 | US 4,098,820 A, UCB SA (1978), "Process for the production of formamides", <https://patents.google.com/patent/US4098820A/en> | Examples 1-6 and the description of the loop reactor; heat of reaction stated in the description | full text (Google Patents) | reactor type, 90 C / 22 bar, 98.5 % DMA conversion, 95 mol% CO yield, NaOMe 0.75-0.79 wt% on amine, DMA:methanol 2.3 by weight (Ex. 1), CO 99.5 %, feed water limits, ~27 kcal/mol heat of reaction, vent of inerts through a pressure controller, methyl formate as side product |
| SRC-2 | US 4,354,041 A, E. I. du Pont (1982), "Method for deactivating catalyst in preparation of dimethylformamide from dimethylamine and carbon monoxide", <https://patents.google.com/patent/US4354041A/en> | Background, Detailed Description, Best Mode, Claims 1-4 | full text | in-situ deactivation (CO + methanol -> methyl formate; methoxide + alkyl formate -> insoluble alkali formate + ether), filtration or centrifugation of the formate, water limit ~0.02-0.03 wt%, water-quench alternative costing up to 2 wt% DMF |
| SRC-3 | US 4,302,598 A, E. I. du Pont (1981), "Recycling catalyst in preparation of dimethylformamide from dimethylamine and carbon monoxide", <https://patents.google.com/patent/US4302598A/en> | Detailed Description, Best Mode | full text | rejected alternative (catalyst recycle in the distillation residue, 5-10 % make-up per cycle); confirms 60-130 C, 0.6-1.4 MPa(g) range |
| SRC-4 | US 4,251,460 A (1981), "Process for production of dimethylformamide", <https://patents.google.com/patent/US4251460A/en> | Example (columns B-F) | full text | order of magnitude only: heavy residue ~1.2 % of the DMF, steam use of the purification (0.48 t/h for 399 kg/h DMF incl. trimethylamine removal) used as a plausibility check of D-010 |
| SRC-5 | NIST Chemistry WebBook, SRD 69, <https://webbook.nist.gov> | DMF (CAS 68-12-2): condensed-phase thermochemistry (Delta_fH liquid -239.4 +/- 1.2 kJ/mol, Vasil'eva et al. 1972), phase change (Tb 426 +/- 1 K, Delta_vapH 46.7 kJ/mol at 298 K); DMA (124-40-3): gas Delta_fH -19 +/- 2 kJ/mol (Issoire and Long 1960), Delta_vapH 26.0 kJ/mol | web pages | heat of reaction (D-005), latent heats (D-010), boiling points (materials.yaml) |
| SRC-6 | Eastman Chemical, Sales Specification T51021 "Dimethylformamide" (2017), <https://www.eastman.com/supplemental/salespecs/71103587.pdf> (via search summary) | specification table | summary only | product specification (D-002): DMF >= 99.90 %, water <= 0.03 %, DMA <= 10 ppm, formic acid <= 3 ppm, methanol <= 50 ppm |
| SRC-7 | Ullmann's Encyclopedia, "Formamides" (doi:10.1002/14356007.a12_001.pub2) and "Amines, Aliphatic" (doi:10.1002/14356007.a02_001.pub2) | not read (licensed) | identity only (issue #127 notes) | route background lead; to be audited with section/page locators before basic engineering |

## D-001 Route and boundary (2026-10-28)
Decision: one-step continuous carbonylation of anhydrous dimethylamine (DMA) with CO in
methanol, homogeneous sodium methoxide catalyst (SRC-1), in-situ catalyst deactivation to
sodium formate (SRC-2), filtration of the salt, distillation (methanol/DMA recovery with
recycle, then vacuum finishing of DMF). Gate-to-gate boundary: DMA, CO and the catalyst
solution enter as boundary feeds; DMF to storage, vent gas, filter cake, methanol purge and
heavy residue leave it. Utilities (power, MP and LP steam, cooling water) are boundary
terminals.
Reason: the route the case notes name; the one-step route needs one reactor and no separate
methyl formate synthesis; SRC-1 and SRC-2 give a consistent, open set of conditions.
Rejected: (a) two-step route via methyl formate (methanol carbonylation, then aminolysis with
DMA): one more reactor and a methyl formate loop; issue #127 asks to compare it, which stays
open (no sourced comparison of yields done here). (b) Catalyst recycle in the residue
(SRC-3): saves catalyst but carries the salt and water risk through the distillation; kept as
an alternative. (c) Water quench of the catalyst: costs up to 2 % DMF (SRC-2).
Links: DMA from processes/methylamines-1 (issue #166, not yet in the library); CO from a
syngas CO separation (cold box) downstream of hydrogen-1 or a gasifier (no library process
yet); the catalyst's methanol from processes/methanol-1. Solvent recovery of used DMF is not
new DMF manufacture and is outside this case.

## D-002 Capacity, operating hours and product (2026-10-28)
Decision: 50 000 t/a DMF at 8000 h/a = 6250 kg/h (ASSUMED); product to the Eastman
industrial-grade specification (SRC-6); design target 30 ppm(wt) methanol in the product.
Reason: no traceable published plant basis was found (issue #127 says capacity is missing);
50 kt/a is a study size, not a claim about a real plant. The LCI is per kg, so the choice
affects scale-dependent items only (power of fixed-size drives).
Open: the model carries no water, formic acid, DMA traces or colour; meeting those limits is a
basic-engineering question (water control in the feeds, D-004).

## D-003 Product state
DMF liquid at 313 K and 300 kPa(a) to storage.

## D-004 Feeds (2026-10-28)
Decision: DMA anhydrous (modelled pure; SRC-1 asks for < 100 ppm water in the amine), liquid at
500 kPa(a) and 298 K; CO 99.5 mol% (SRC-1 examples) with 0.3 mol% N2 and 0.2 mol% H2
(ASSUMED split of the impurities), at 300 kPa(a), 303 K (ASSUMED battery-limit pressure of a CO
cold box), compressed on site. Water and CO2 in the CO must be below a few ppm (SRC-1); not
modelled.
Reason: the catalyst is destroyed by water and CO2 (SRC-1, SRC-2); dry feeds are a
precondition of the route.

## D-005 Reactor and reaction model basis (2026-10-28)
Decision: liquid-phase loop reactor with external circulation cooler and gas induction
(SRC-1), 363.15 K and 2200 kPa(a) (given: SRC-1 Example 1). Conversion reactor:
DMF_SYN with 98.5 % DMA conversion per pass (given, SRC-1 Ex. 1); CO fed so that 95 mol% of it
ends in DMF (given, SRC-1 Ex. 1); NaOMe 0.75 wt% of the DMA to the reactor (SRC-1 Ex. 1, 2, 6:
0.75-0.79 %); DMA:methanol 2.3 by weight in the reactor feed (SRC-1 Ex. 1).
Heat of reaction: -109.9 kJ/mol for DMA(g) + CO(g) -> DMF(l) from SRC-5 formation enthalpies;
SRC-1 states about 27 kcal/mol (113 kJ/mol): agreement within 3 %.
Model basis: sourced conversion, not kinetics and not equilibrium. The 5 % of the CO not
converted to DMF is vented (in reality partly as methyl formate, which reacts on with DMA;
methyl formate is not modelled: ASSUMED). No rate law is invented. `cheme maturity` reports
this reactor as "specified conversion".

## D-006 Balance method and its limits (2026-10-28)
Decision: the separator, filter-feed and column outlets and all duties come from the short-cut
balance `scripts/dmf_balance.py` (run with `cheme run`), entered as ASSUMED; cheme propagates
the mixer, compressor, reactor, filter and splitter. The mass balance closes in every block
and step (`cheme process streams`).
Reason: no benchmarked property package covers DMF, methanol, DMA and sodium salts
(`cheme process props --coverage`: only the CO feed gas, `syngas-pr-vapor`). Polar VLE and
liquid-reactor energy are the open items of core #315 (issue #127 dependency note). The CO
compressor's enthalpies are calculated (S2, S4) and its energy balance closes (residual 3.6 kW
of 207 kW, within tolerance). Every other energy balance is not evaluable: this is the gated
step, not a design error.

## D-007 Catalyst feed and deactivation (2026-10-28)
Decision: catalyst bought as 30 wt% sodium methoxide in methanol (ASSUMED strength) and used
once through; at the end of the reaction it is converted in situ under CO pressure to sodium
formate and dimethyl ether (net CAT_DEACT: CH3ONa + CH3OH + CO -> HCOONa + CH3OCH3, SRC-2
mechanism), complete conversion ASSUMED. Heat of CAT_DEACT neglected (no sourced formation
enthalpy of solid sodium methoxide recorded; extent 0.55 kmol/h, against 86.5 kmol/h of
DMF_SYN).
Consequence: 4.8 kg NaOMe per t DMF; the catalyst solution brings more methanol than the plant
consumes, so a methanol purge is needed (D-009).

## D-008 Vent and salt removal (2026-10-28)
Decision: V-102 takes all CO, N2, H2 and DME to the vent with 3 mol% methanol, 0.2 mol% DMA,
0.2 mol% DMF (ASSUMED from vapour pressures at 363 K and the methanol mole fraction of the
liquid; a vent condenser would lower them). Nothing dissolved flashes later (ASSUMED; a
let-down flash of dissolved CO is an open item). The vent goes to a thermal oxidiser outside
the boundary. F-101 keeps 99 % of the sodium formate; the wet cake holds 25 wt% liquor
(ASSUMED); the cake goes to disposal.

## D-009 Distillation (2026-10-28)
Decision: C-201 at atmospheric pressure takes all DMA and methanol overhead, except the
product's 30 ppm methanol, and 0.1 % of the DMF (ASSUMED sharp split, reflux ratio 1.0);
the distillate is recycled to the feed drum except a purge of 2.6 % (calculated so that the
methanol balance closes: catalyst methanol in = methanol consumed and lost). C-202 under vacuum
(20 kPa(a) top, bottoms about 390 K) takes DMF overhead and 1 % of its DMF feed with the salt
fines to a heavy residue (ASSUMED; SRC-4 example ~1.2 %), reflux ratio 0.5 (ASSUMED).
Reason: methanol (338 K) and DMA (280 K) are far lighter than DMF (426 K): an easy split; the
finishing column only removes heavies and salt. Vacuum keeps DMF below its normal boiling
point in the presence of traces of base.
Rejected: catalyst-containing distillation (SRC-3).

## D-010 Utilities and duties (2026-10-28)
Decision: cooling water 298/308 K; MP steam 1100 kPa(a) (457.6 K) for C-201 (bottoms 426 K);
LP steam 450 kPa(a) (420.8 K) for C-202; electric drives. Duties from scripts/dmf_balance.py:
reactor cooler 2429 kW (heat of reaction less feed heating, liquid cp 2.2 kJ/(kg K) ASSUMED);
CO compressor 207 kW (two intercooled stages, isentropic efficiency 0.75, ASSUMED); feed pump
7.6 kW; C-201 reboiler 1299 kW, condenser 1088 kW; C-202 reboiler 1393 kW, condenser and
product cooler 1783 kW (latent heats SRC-5, DMF 43-44 kJ/mol near its boiling range ASSUMED);
loop pump 30 kW, column pumps 5 kW, vacuum system and pumps 20 kW (ASSUMED).
Check: steam for purification is 2.7 MW for 6.25 t/h DMF = 1.6 GJ/t; SRC-4's purification
uses about 1.2 t steam per t DMF (~2.5 GJ/t) including trimethylamine removal: same order.
All duties are +/-30 % or worse.

## D-011 Core findings met in this run (2026-10-28)
- A `Pumping` step stops `cheme process build` (cheme 0.8.0, Python 3.15: `step_method`
  iterates the `Union` annotation of `Pumping.method`). P101 is declared `GeneratingFlow`
  (Pumping's parent class); propagate then does not pass it through, so S6 is given ASSUMED
  equal to S5.
- `cheme process propagate` writes S10's mole fractions rounded to 6 significant digits; they
  sum to 1.0000011 and pyDEXPI warns (`pydexpi_composition_fractions`) on BFD/PFD. Calculated
  values are not edited by hand; to be fixed in core (renormalise or more digits).
- The flowsheet categories have no liquid-waste class: the heavy residue (RESID) is declared
  `solid_waste` (a waste to treatment); the methanol purge is `by_product`.

## D-012 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg DMF (product:DMFP, stream S16) at the gate, cut-off system
model, no allocation (DMF is the only product; the methanol purge is treated as a waste, see
below). Every foreground exchange comes from a flowsheet stream or energy stream
(`lca/inventory.csv` names them). No background is linked: each feed, utility and waste
treatment is `missing:` in `lca/lca.yaml`, with the background activity it should connect to
later. The result class is therefore "partial screening" with 11 gaps and no impact number.
Exchanges per kg DMF (lca/inventory.csv, design case):

| exchange | amount | streams | provenance |
|---|---|---|---|
| dimethylamine | 0.6244 kg | S1 | ASSUMED (balance, D-006) |
| carbon monoxide 99.5 mol% | 0.4074 kg | S2 | ASSUMED (D-004, D-005) |
| NaOMe 30 wt% in methanol | 0.01584 kg | S3 | ASSUMED (D-007) |
| electricity | 0.0431 kWh | Q1, Q3, Q4, Q8, Q11 | ASSUMED (D-010) |
| MP steam 1100 kPa(a), as heat | 0.2078 kWh | Q6 | ASSUMED (D-010) |
| LP steam 450 kPa(a), as heat | 0.2229 kWh | Q9 | ASSUMED (D-010) |
| heat to cooling water | 0.8811 kWh | Q2, Q5, Q7, Q10 | ASSUMED (D-010) |
| vent gas to thermal oxidation | 0.02214 kg | S8 | ASSUMED (D-008) |
| sodium formate cake to hazardous-waste incineration | 0.00790 kg | S10 | calculated (F-101) |
| methanol purge to incineration (or recovery) | 0.00737 kg | S13 | calculated (SPL) |
| heavy residue to hazardous-waste incineration | 0.01016 kg | S17 | ASSUMED (D-009) |

Balance check against the flowsheet (`cheme assess lca --balance`): mass in 6547.30 kg/h, out
6547.29 kg/h; C, H, N, Na and O close within 0.01 %; fossil carbon in 3200.1 kg C/h, 3081.0 in
the product, 119.1 in the wastes and vent. Stoichiometric minimum: 0.617 kg DMA and 0.383 kg CO
per kg DMF; the inventory is 1.2 % and 6.3 % above it (yield losses, CO excess).
Plausibility of the steam: 0.43 kWh (1.55 MJ) per kg against about 2.5 MJ/kg in SRC-4 (which
includes trimethylamine removal).
Why the purge is a waste: as `recyclable` under cut-off it would leave burden-free; no
recovery is arranged, so it is counted as solvent waste to incineration (gap) until one is.
Not in the inventory (open): direct emissions to air from the thermal oxidation of the vent
(CO2 about 0.03 kg/kg DMF from its carbon; NOx), fugitive and storage-tank emissions of DMF,
methanol and DMA (no equipment count or tank list yet; `emission_estimates:` need sourced
factors), wastewater (none in the model: dry route, D-004), catalyst-solution transport,
construction. Atlas build (`scripts/build_lci.py --strict`): dmf-1 builds with 7 reported gaps
(DMA, CO, CAT, VENT, CAKE, PURGE, RESID); the utilities follow the shared utility vocabulary
through `process.yaml` slugs (electricity, cooling-water, steam with the `steam-heat` unit
override in `lca/mappings.yaml`). The impurity entries of `process.yaml` carry no inventory
key, so the CO feed is not linked to hydrogen.

## Missing shared registry and vocabulary entries (for the consolidated PR)
`chemicals/chemicals.yaml`: n,n-dimethylformamide (main product, CAS 68-12-2), dimethylamine
(124-40-3), carbon-monoxide (630-08-0), methanol (67-56-1; also missing for methanol-1),
sodium-methoxide (124-41-4, as a 30 wt% methanol solution grade), sodium-formate (141-53-7),
dimethyl-ether (115-10-6). `lci/mappings.yaml` technosphere: dimethylamine, carbon monoxide,
sodium methoxide solution, hazardous solid-waste incineration, hazardous liquid-waste
incineration, spent-solvent incineration or recovery, thermal oxidation of a vent gas.
`taxonomy`: `nitrogen-organics` is used (amides are not named in its note; check). CPC 2.1
code of DMF for `lca.yaml` `dataset.classification.cpc` (not checked, left out).

## Method and dependency table

| step | status | needs |
|---|---|---|
| mass and component balances | closed by cheme (all blocks and steps) | - |
| element balances of the reactions | checked by cheme validate (DMF_SYN, CAT_DEACT) | - |
| CO compressor energy | closed (syngas-pr-vapor) | - |
| reactor, flash, column, filter energy | not evaluable | core #315: polar/activity-coefficient package for DMF-methanol-DMA (+ salts), liquid-reactor energy verification |
| predictive simulation (DWSIM) | not attempted | a qualified method selection for the polar system (NRTL/UNIQUAC with sourced BIPs for DMF-methanol, DMF-DMA, methanol-DMA), process/simulation.yaml |
| reactor kinetics | not available | sourced gas-liquid rate data; SRC-1 productivity (kg/h per L) only |
| route comparison (methyl formate route) | open | sourced yields of both steps |
