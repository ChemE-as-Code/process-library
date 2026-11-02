# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.

THF-1: tetrahydrofuran (THF) from 1,4-butanediol (BDO), issue
ChemE-as-Code/process-library#126. Concept stage: design basis, balanced BFD/PFD and a
preliminary gate-to-gate LCI. Run of 2026-10-28, starting from library `main` at 11d50ef with
cheme-as-code 0.8.0 (pyDEXPI 2.1.0, thermo 0.6.1, Python 3.15). Designed independently: no
published plant balance was looked for or copied (held-out benchmark).

## Route and boundary memo

**Routes considered** (screening; the Ullmann chapter, doi:10.1002/14356007.a26_221.pub3, is the
lead for the industrial route survey and was not read in this run):

| route | feed | for | against | decision |
|---|---|---|---|---|
| BDO cyclodehydration, acid catalysed, liquid phase | BDO | one reaction step, THF and water only plus small heavies; a published, detailed reactive-distillation patent (US 9284289 B2) with operating ranges; Li and Chen (2019, Introduction) call it the typical production route | depends on a purchased BDO; corrosive acid | **selected** (the issue's route) |
| BDO dehydration in high-temperature water, no catalyst | BDO in water | no acid | reversible, equilibrium yields 84-94 % at 200-350 C (Hunter et al. 2006), high pressure, dilute | rejected: lower yield, dilute feed |
| BDO over solid acids (Zr-Al oxides, zeolites, resins), liquid phase | BDO | no homogeneous acid, no acid bleed | resins below 120 C give at most ~70 %, zeolites deactivate (Li and Chen 2019, Introduction); 220-240 C | rejected for the base case; an alternative to keep (I-09) |
| Hydrogenation of maleic anhydride / gamma-butyrolactone to THF with BDO co-product; furan hydrogenation | maleic anhydride, furfural | integrated routes | other feeds, hydrogen loop; not the issue's scope | not designed (outside the issue's route) |

**Plant boundary (battery limits)**: from the BDO and catalyst at the battery limit to THF
(99.95 wt%) at 313 K to storage. Outside: BDO production (boundary feed, no library process makes
it yet), feed and product tanks, steam and cooling water generation, power supply, wastewater
treatment and incineration of the heavies bleed. These leave the plant as exchanges of the LCI.

**BFD**: (1) RXN reaction by reactive distillation (feed pump, steam-heated stirred reactor with
homogeneous p-toluenesulfonic acid, rectifying column, condenser, heavies bleed); (2) SEP
pressure-swing distillation (LP column 110 kPa(a) with water bottoms, HP column 800 kPa(a) with
THF bottoms and the distillate recycled to the LP column, product and water coolers). Recycle:
the HP distillate (8.2 t/h, 89.5 wt% THF). Purge: the reactor bleed (heavies and acid).

## Decisions

### D-001 Route: BDO cyclodehydration by reactive distillation, pressure-swing distillation (2026-10-28)
Decision: liquid-phase cyclodehydration of BDO with a homogeneous sulfonic acid in a stirred,
steam-heated reactor under a short rectifying column (reactive distillation): THF and water leave
as vapour, BDO and heavies stay in the reactor; the THF/water azeotrope is broken by
pressure-swing distillation.
Reason: the issue's route; US 9284289 B2 (Mitsubishi Chemical; Google Patents text, sections
"Production Method 1" and "2" and the examples) describes this reaction mode, catalyst and
operating window; pressure-swing distillation needs no entrainer because the THF/water azeotrope
moves strongly with pressure (D-007).
Rejected: extractive distillation (needs a solvent, e.g. a glycol, and its losses), azeotropic
drying with an entrainer, molecular sieves (regeneration water), solid-acid fixed beds (see memo).
Assumptions: the patent's ranges apply to a continuous 50 kt/a plant.

### D-002 Capacity and product specification (2026-10-28)
Decision: 50 kt/a THF, 8000 h/a: 6250 kg/h; product 99.95 wt% THF, 0.05 wt% water.
Reason: a single-train size in the range of solvent / PTMEG-feed plants; no client figure. The
water content is the target of the HP column bottoms.
Assumptions: ASSUMED capacity, hours and specification. Stabiliser (e.g. BHT), peroxides,
2,3-dihydrofuran (US 9284289 B2 reports 37-327 ppm in the condensates of Examples 2-1 to 2-3
and Comparative Examples 2-1 to 2-3), colour and acidity are
outside the model (I-08, I-10).

### D-003 BDO feed (2026-10-28)
Decision: pure BDO at 303 K and 300 kPa(a) as a boundary feed.
Reason: no library process makes BDO; purchased BDO is the issue's boundary.
Assumptions: ASSUMED purity 100 %; commercial BDO carries impurities (US 9284289 B2 names
2-(4-hydroxybutoxy)-THF, gamma-butyrolactone, 1-acetoxy-4-hydroxybutane) that form heavies or
acetal polymer; not modelled (I-01).

### D-004 Reactor conditions and catalyst (2026-10-28)
Decision: R-101 at 418 K (145 C) and 130 kPa(a); p-toluenesulfonic acid 2 wt% and water 5 wt%
in the reactor liquid; rectifying column C-101 with reflux ratio 0.5; total condenser E-101 to
313 K; MP steam 1000 kPa(a) for heating.
Reason: inside the ranges US 9284289 B2 gives (liquid 80-250 C, preferred 120-180 C, examples
140-180 C and 145 C at the larger scale; 10-1000 kPa, preferred 100-500 kPa; acid 0.01-20 wt%,
examples 0.2-0.4 wt%; water in the reactor liquid 1.4-10 wt%, preferred 2-8 wt%, below it an
acetal polymer forms solids, above it water inhibits THF formation; 1-5 theoretical stages on the
reactor, 4 in the examples; reflux ratios 0.01-4). The patent also reports that at 110 C hardly
any THF formed.
Rejected: the patent's 0.2-0.4 wt% acid (a higher 2 wt% taken for a continuous plant without
kinetics to size against, ASSUMED); atmospheric pressure (130 kPa(a) gives margin for the
condenser and vent).
Assumptions: values ASSUMED within the sourced ranges; reactor volume not sized (no rate law,
I-03). Materials for hot sulfonic acid are an open input (equipment list).

### D-005 Reaction model: specified conversion, assumed selectivity, heavies bleed (2026-10-28)
Decision: conversion reactor (cheme `selectivity:`) with two reactions (process/reactions.yaml):
CYCLO BDO -> THF + H2O and ETHER 2 BDO -> DHBE + H2O, DHBE (the BDO dimer ether,
4-(4-hydroxybutoxy)butan-1-ol, PubChem CID 76946) lumping the heavies. THF selectivity 0.995 kmol
per kmol BDO converted (ASSUMED). The heavies are held at 30 wt% in the reactor liquid by a bleed
(117.7 kg/h: 63 % BDO, 30 % DHBE, 5 % water, 2 % acid); the BDO leaving with it fixes the plant
conversion 0.9906 and the THF yield 0.9857 mol per mol BDO fed (1.2674 kg BDO per kg THF against
the stoichiometric 1.2492). No BDO overhead (the patent reports BDO below 10 ppm in its
condensate).
Reason: the reaction is reversible only in liquid water at high temperature (Hunter et al. 2006:
equilibrium yields 84 % at 200 C to 94 % at 350 C); under reactive distillation the products
leave as vapour, so a conversion model with the bleed as the loss is the honest basis. The
patent gives no overall yield or selectivity figure; it names oligomers (dimers, trimers) and an
acetal polymer accumulating in the reactor, which justify a heavies bleed.
Rejected: invented kinetics; the 84-94 % equilibrium yields (they describe the aqueous batch
system, not reactive distillation).
Assumptions: the selectivity 0.995 and the 30 wt% heavies are ASSUMED (I-02); DHBE stands for
all heavies. 2,3-dihydrofuran and other light by-products are not modelled (I-08).
The bleed (S7) is taken free of THF: the THF dissolved in the boiling reactor liquid at 418 K
and 130 kPa(a) is neglected, likely a few kg/h, below 0.1 % of the product, so the yield is
very slightly overstated (not calculated; review 2026-10-28-pfd-lci-review#6). Heat of
reaction CYCLO +3.27 kJ/mol from liquid formation enthalpies (chemicals package), slightly
endothermic; ETHER taken as thermoneutral in the balance (0.25 % of the extent).

### D-006 Independent balance script; property method not qualified (2026-10-28)
Decision: the feed flow, the reactor overhead and bleed, the column outlets and all duties come
from `scripts/thf_balance.py` (run `cheme run scripts/thf_balance.py`), entered in
process/flowsheet.yaml as ASSUMED with that source; mixers, pumps, coolers and the reactor are
then calculated by `cheme process propagate --fill` and cheme's conversion reactor, which
reproduce the script (block and step balances close).
Reason: cheme 0.8.0 qualifies NRTL only for ethanol/water (`cheme process methods`), and no
property package covers THF/water/BDO (`props --coverage`): `cheme process simulate` and `props
--fill` cannot be used (gated, open on 2026-10-27).
Method: thermo NRTL with the ChemSep THF/water parameters packaged in thermo 0.6.1 (b12 460.821 K,
b21 868.103 K, alpha 0.4522; `cheme process phase 109-99-9 7732-18-5 --liquid NRTL` reports them
sourced), ideal gas, Psat basis; the bubble point is solved directly (thermo's PVF flash failed
for this pair). Columns: binary McCabe-Thiele minimum reflux with constant molar overflow, feed
condition q from the feed enthalpy, total condensers, products at their bubble points, reboiler
duty from each column's energy balance. Reactor: energy balance of R-101 with C-101 on liquid
formation enthalpies (chemicals Hfl) plus thermo's enthalpy changes. DHBE and p-TSA take BDO's
specific enthalpy (0.6 % of the reactor mass flow).
Results: azeotrope x_THF 0.834 (95.3 wt%) at 337.2 K and 101.3 kPa, 0.827 at 110 kPa(a), 0.651
(88.2 wt%) at 410.4 K and 800 kPa(a); overall mass closure 0.0007 kg/h; overall energy closure
0.4 kW of 6265 kW steam (0.01 %).
Assumptions: accuracy not stated. The NRTL azeotrope agrees with the values quoted in an
engineering forum thread (about 0.8 mol/mol at 1 atm, 0.65 at 8 bar; weak source, cross-check
only); qualification against measured VLE at both pressures is open (I-04). NRTL with these
parameters predicts a liquid-liquid split of THF/water at e.g. x_THF 0.15 between 342 and 360 K
(`cheme process phase ... --two-liquids`); the script assumes one liquid phase (I-04).

### D-007 Pressure-swing distillation (2026-10-28)
Decision: LP column C-201 at 110 kPa(a) takes the reactor condensate (80.0 wt% THF) and the HP
recycle, gives process water (x_THF 2e-5, 80 ppm(wt)) and a distillate 0.03 mol/mol below the LP
azeotrope (x_THF 0.797, 94.0 wt%); HP column C-202 at 800 kPa(a) gives THF (99.95 wt%) and a
distillate 0.03 mol/mol above the HP azeotrope (x_THF 0.681, 89.5 wt%), recycled to C-201.
Reflux 1.3 x minimum, at least 0.3 (minimum 0.14 for C-201, 0.17 for C-202: both at the 0.3
floor). Results: recycle 8224 kg/h; LP condenser 2818 kW, reboiler 2666 kW; HP condenser 1738 kW,
reboiler 2288 kW (subcooled feed, q 1.26).
Reason: the water-rich feed goes to the low-pressure column first (its composition lies between
water and the LP azeotrope); 800 kPa(a) moves the azeotrope by 0.18 mol/mol, enough for a recycle
of 1.3 t per t of product and an HP condenser hot enough to reboil the LP column (D-009). The
0.3 floor gives margin for the constant-molar-overflow error (THF and water latent heats differ by
about a third).
Rejected: a higher HP pressure (more MP-steam temperature needed; not optimised); feeding the
condensate to the HP column first (wrong side of the HP azeotrope).
Assumptions: pressures, approaches, product purities, reflux rule ASSUMED; stages and pressure
drop not calculated (I-11). The LP column duties (reboiler, condenser, and so the LP steam and
part of E-201) assume one homogeneous liquid on every stage, although the same NRTL parameters
predict two liquid phases near x_THF 0.15 at 342-360 K, a range the C-201 stripping section
passes through (D-006); they stay unverified until a stage-by-stage VLLE check of C-201 at
110 kPa(a) or a qualified property method (I-04).
Steam range (review 2026-10-28-pfd-lci-review#2): with the reflux at 1.3 x Rmin instead of
the 0.3 floor (0.18 and 0.22) and boil-up scaled with R + 1 at fixed distillates (hand
estimate), E-206 falls to about 2.18 MW and E-202 to about 0.79 MW, so the separation steam is
about 8 % and the total steam about 4 % lower (about 3.47 instead of 3.61 MJ/kg THF). No upper
bound can be calculated yet: finite stages, the constant-molar-overflow error and a possible
liquid-liquid split in C-201 can only raise the duties. For screening, the steam per kg THF is
taken as 3.6 MJ/kg -5 %/+30 % (the +30 % ASSUMED, engineering judgement, not calculated) until
stages are set (I-11).

### D-008 Utilities and machines (2026-10-28)
Decision: MP steam 1000 kPa(a) (453 K) for R-101 and E-206; LP steam 450 kPa(a) (420.8 K) for the
LP trim reboiler E-202; cooling water 298/308 K; electric pumps P-101 (300 -> 400 kPa(a)) and
P-201 (110 -> 830 kPa(a)), efficiency 0.6. Reflux pumps, the LP bottoms pump and the R-101
agitator are not on the PFD; together about 25 kW, cut off in the LCI (below 1 % of the energy
input).
Assumptions: all ASSUMED.

### D-009 Heat integration: HP condenser reboils the LP column (2026-10-28)
Decision: E-201 condenses the HP overhead (410.4 K) against the LP bottoms (375.4 K, 35 K
difference) and takes the whole HP condenser duty (1738 kW); LP steam trims the remaining 928 kW.
Reason: the standard heat integration of a pressure-swing pair; it saves 22 % of the steam
(6265 kW with it, 8003 kW without).
Rejected for this stage: product / HP feed exchange, use of the reactor overhead heat (2.9 MW
condensing from 362 K), process water / LP feed exchange (I-06).

### D-010 Lists (2026-10-28)
Decision: equipment list of the 13 items the PFD links (pumps, reactor, three columns with their
condensers and reboilers, two coolers) with ASSUMED design conditions (operating maximum + 10 %,
at least + 2 bar, + 25 K), applied to each side of a heated item: the steam side of E-206 and
of the R-101 heating surface 11 barg, of E-202 5.5 barg; the list carries the higher side and
the other in the notes (review 2026-10-28-pfd-lci-review#5). No line or instrument list: there are no P&IDs at this stage (out of
scope of this run).

### D-011 Preliminary LCI: gate-to-gate foreground inventory, every background a gap (2026-10-28)
Decision: `lca/lca.yaml` with the functional unit 1 kg THF (product:THFP) at the gate, boundary
gate-to-gate, design case; every exchange from the balanced flowsheet; every background
`missing:` with the activity it should connect to; `lca/mappings.yaml` without overrides; no
allocation (one product: the process water and the bleed are wastes with a `treatment:`);
process.yaml `lca.source: none`, so the all-gap result does not reach the catalog as 0.
Emission exclusions with reasons: storage tanks (outside the boundary), fugitive leaks and
condenser vents (not estimated, not claimed negligible: need P&IDs and inert flows, I-07),
wastewater effluent (belongs to the treatment background). Cut-off: small pumps and agitator
power (about 25 kW, D-008).
Reason: the run's scope (issue #126, ADR 0022: an unmapped exchange of an internal process is a
reported gap); no licensed values are used.
Note 2026-11-01: the owner has since marked all 50 processes public, so this one is no longer internal.

## LCI summary (lca/inventory.csv, per kg THF)

| exchange | amount | provenance | stream | background it should link to |
|---|---|---|---|---|
| feed:BDOF 1,4-butanediol | 1.26739 kg | assumed (script) | S1 | BDO, market for (route to be chosen) |
| feed:PTSAF p-toluenesulfonic acid | 0.000377 kg | assumed | S2 | p-TSA or a declared proxy |
| feed:POWER electricity | 0.000979 kWh | assumed | Q1, Q2 | electricity, medium voltage, site grid |
| feed:MPS MP steam 1000 kPa(a) | 0.8539 kWh (3.074 MJ) | assumed | Q3, Q8 | steam in chemical industry (utility-steam-ng-boiler) |
| feed:LPS LP steam 450 kPa(a) | 0.1485 kWh (0.535 MJ) | assumed | Q5 | steam in chemical industry |
| product:CW heat to cooling water | 0.9831 kWh (3.539 MJ) | assumed | Q4, Q7, Q9, Q10 | cooling water (utility-cooling-tower) |
| product:WW process water to treatment | 0.2489 kg (80 ppm(wt) THF) | calculated | S13 | wastewater treatment (utility-wwtp) |
| product:BLEED heavies to incineration | 0.01883 kg | assumed | S7 | hazardous liquid waste incineration |

Balance (`cheme assess lca --balance`, per hour): mass 7923.53 kg in and out; C 4223.93 / 4223.90
kg, H 886.081 / 886.081, O 2813.09 / 2813.11, S 0.4383 / 0.4383: all closed (largest residual
0.01 %, S). Energy: steam 6265.3 kWh + power 6.1 kWh in, 6144.3 kWh to cooling water; the
difference (127 kW) is the enthalpy of the material streams, which the LCI does not count; the
script's full energy balance closes to 0.01 %. Carbon of the BDO is counted as fossil (default; a
bio-based BDO would change it). Result: no impact total (8 gaps); data quality DQR 2.33
(`--coverage`). The library LCI build (`scripts/build_lci.py --strict`, run into a scratch
directory) passes with the 8 gaps reported unlinked.

## Reaction and model evidence

| item | evidence | used as |
|---|---|---|
| Cyclodehydration BDO -> THF + H2O, catalysts | Li and Chen 2019, Introduction (Eq. 1, catalyst families and their drawbacks); US 9284289 B2 | route and catalyst choice |
| Liquid conditions, acid, water window, reactive distillation, condensate 78-80 wt% THF, BDO < 10 ppm overhead, by-products (DHF 37-327 ppm, oligomers, acetal polymer) | US 9284289 B2, "Production Method 1/2" sections, Example 1-1, Example 1-4 (500 L SUS316L reactor charged with 400 L BDO: BDO at or below 10 ppm in the condensate), Examples and Comparative Examples 2-1 to 2-3 (DHF) | D-004, D-005 ranges; the script's 80.0 wt% condensate agrees |
| Reversibility and equilibrium yields 84-94 % (200-350 C, liquid water, no catalyst); water acts as proton donor | Hunter, Ehrenberger, Savage 2006, abstract | D-005: not used as the reactor model (other system) |
| Solid-acid yields: Zr-Al 97 % yield after 12 h at 220 C in water; pseudo-first-order constants 0.605 1/h (aqueous) and 0.139 1/h (pure BDO) at 220 C | Li and Chen 2019, Section 3.2, Figs. 2-5 | alternative route evidence only (I-09); not this catalyst |
| Kinetics for p-TSA catalysed liquid-phase dehydration at 145 C | none found in this run | reactor not sized (I-03) |
| THF/water VLE and azeotrope shift | ChemSep NRTL parameters in thermo (model); forum values as weak cross-check | D-006, D-007; qualification open (I-04) |
| Formation enthalpies (liquid) BDO -505.3, THF -216.2, water -285.825 kJ/mol | `chemicals` package (Hfl) | heat of reaction, reactor balance |

Sourced conversion/equilibrium model: none at plant level; the reactor is a specified conversion
with assumed selectivity, labelled as such (`cheme maturity`: R101 conversion, specified,
unsourced).

## Source register

| source | locator | access / read | reuse terms | used for |
|---|---|---|---|---|
| US 9284289 B2, Method for producing tetrahydrofuran (Mitsubishi Chemical), https://patents.google.com/patent/US9284289 | description, "Production Method 1/2", Examples 1-1, 1-4, 2-1 to 2-3, Comparative Examples 2-1 to 2-3 (whole Google Patents text read on the review re-check) | open, read 2026-10-28 | patent text: facts used in own words | D-001, D-004, D-005 |
| Hunter, Ehrenberger, Savage (2006) J. Org. Chem. 71, 6229-6239, doi:10.1021/jo061017o | abstract (Penn State Pure record) | abstract only | facts only | D-005 |
| Li, Chen (2019) Materials 12, 2092, doi:10.3390/ma12132092 (PMC6651349) | Introduction; Sections 2.2, 3.1, 3.2; Figs. 1-5 | full text, read 2026-10-28 | CC BY 4.0 | memo, evidence table |
| Ullmann's, Tetrahydrofuran, doi:10.1002/14356007.a26_221.pub3 | not read | licensed | none | route survey lead (open) |
| ChemSep NRTL parameters as packaged in thermo 0.6.1 (C. Bell et al.) | THF/water pair | open software | MIT (thermo) | D-006 |
| `chemicals` package (formation enthalpies, molar masses, boiling points) | Hfl, Hfg, Tb, MW of 109-99-9, 110-63-4, 7732-18-5 | open software | MIT | materials, reactions, script |
| PubChem CID 76946 (4-(4-hydroxybutoxy)butan-1-ol) | identity, formula, registry numbers | open | public domain data | DHBE component |
| eng-tips forum thread 474537 (solvent/water/heavy separation) | posts on the THF/water azeotrope at 1 atm and 8 bar | open | facts only, weak | cross-check of D-006 only |

## Method and dependency table

| step | method | status |
|---|---|---|
| Mass and element balances | `cheme process streams`, `cheme validate`, `cheme assess lca --balance` | closed |
| Reactor outlet | cheme conversion reactor (`selectivity:`) | calculated; selectivity ASSUMED |
| VLE, columns, duties | scripts/thf_balance.py, NRTL (thermo) | ASSUMED values; gated for qualification (polar activity-coefficient benchmark) |
| Energy closure in core | `cheme process props --fill` | gated: no package for THF/water/BDO |
| Liquid-phase reactor energy in core | `cheme process reactors` / simulate | gated: liquid-reactor energy verification |
| Simulation | `cheme process simulate` (DWSIM, NRTL) | not run: NRTL qualified for ethanol/water only in cheme 0.8.0 |
| LCI | `cheme assess lca --inventory --write`, `--coverage`, `--balance`; library `build_lci.py --strict` | written; 8 gaps |

## Open inputs

- I-01 BDO feed: specification, impurities, supplier route (fossil or bio-based), delivery state.
- I-02 THF selectivity and heavies formation rate, and the heavies level the reactor tolerates:
  plant or patent data with numbers (the Ullmann chapter is the next source to read).
- I-03 Kinetics of the p-TSA catalysed dehydration at 120-180 C to size R-101 (residence time,
  hold-up); none found.
- I-04 THF/water VLE: qualify NRTL against measured isobaric data at about 100 and 800 kPa
  (azeotrope compositions), and check the liquid-liquid split NRTL predicts (closed-loop region)
  against the LP column's stage temperatures with a rigorous, stage-by-stage column.
- I-05 BDO recovery from the bleed (74 kg/h BDO, 0.94 % of the feed) by a small vacuum column:
  would raise the yield toward the selectivity limit; not designed.
- I-06 Further heat integration (product/feed, reactor overhead heat, process water/LP feed).
- I-07 Vents and fugitive emissions: inert blanket flows, P&ID component counts.
- I-08 Light by-products (2,3-dihydrofuran, 4-hydroxybutyraldehyde intermediate) and their
  removal; product quality.
- I-09 Solid-acid catalyst alternative (no acid in the bleed, no corrosive liquid) to compare.
- I-10 Commercial THF specification (water, peroxide, stabiliser) to replace the assumed target.
- I-11 Column stages, feed stages, pressure drops and sizes (basic engineering).
- I-12 CPC Ver. 2.1 classification of THF for `dataset.classification.cpc` (not looked up
  reliably in this run; `cheme.lca-dataset-undocumented` info).

## Missing library registry entries (chemicals/chemicals.yaml, for the consolidated PR)

- `1-4-butanediol` (BDO, C4H10O2, CAS 110-63-4): feed:BDOF; also a technosphere entry in
  `lci/mappings.yaml` (BDO, market for).
- `tetrahydrofuran` (C4H8O, CAS 109-99-9): product:THFP, the main product.
- `p-toluenesulfonic-acid` (C7H8O3S, CAS 104-15-4): feed:PTSAF; a technosphere entry or a
  declared proxy.
- Shared `lci/mappings.yaml`: a treatment entry for incineration of liquid hazardous organic waste
  (product:BLEED). Existing entries (steam-heat, cooling-water, wastewater, electricity) cover the
  utilities once the gaps are closed by `use:` overrides in `lca/mappings.yaml`.
