# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Acrylonitrile by SOHIO propylene ammoxidation, issue ChemE-as-Code/process-library#460, the
coverage item of rank 52 (`acrylonitrile`). Concept stage: design basis, balanced BFD/PFD with a
sourced reactor slate, equipment list and a preliminary gate-to-gate LCI. Out of scope here: P&IDs,
layout, HAZOP, TEA, datasheets, a rigorous VLE design of the columns.

Starting point (2026-11-19): library `main` (c241d8d7) with the core pin 0e85885 (v1.12.0 and
#254). Core 1.12 brings what this continuous plant needs beyond a conversion reactor: component
separators with a specified split (`recovery:`), design specifications on feeds and splits
(`specs:`), both solved by propagate together with the recycle tear (core ADRs 0060, 0070), and
conversion-step duties from ideal-gas enthalpies (ADR 0059). Templates: `formaldehyde-1`
(continuous gas-phase catalytic oxidation with absorption and an off-gas oxidiser) for the
structure, `oxalyl-chloride-1` for the source register and the depth. Requires cheme-as-code 1.12
(plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 6 596 897 B1, X. Guan, X. Chen, L. Wu (Sinopec Research Institute of Petroleum Processing, China Petrochemical Corp.), priority CN 97106580, 1997-09-03, published 2003-07-22: Catalyst for producing acrylonitrile, https://patents.google.com/patent/US6596897B1/en | evaluation results 1 to 3: 38 mm fluidised-bed test reactor, propylene/ammonia/air 1/1.2/9.8 mol, 440 C; evaluation 1 at 0.14 MPa and WWH 0.085 1/h, example 1: propylene conversion 97.5 %, NH3 conversion 96.5 %, single-pass yields acrylonitrile 79.7, acetonitrile 2.8, HCN 1.9, acrolein 0.5, acrylic acid 1.5, CO 3.1, CO2 8.1 %; the invention's other examples 79.2 to 81.4 % acrylonitrile (evaluations 1 and 2), and example 1 at 0.08 to 0.15 MPa 78.2 to 80.1 % (evaluation 3, whose 0.14 MPa row is evaluation 1's); the prior-art comparative examples CE1 and CE2 77.7 and 77.1 % (evaluation 1); the patent does not say whether its pressures are absolute or gauge | read (Google Patents text); patent, facts only | D-003, D-004 |
| SRC-2 | Li, Q., Dimian, A. C., Kiss, A. A. (2025) Energy efficient process designs for acrylonitrile production by propylene ammoxidation. Syst. Control Trans. 4, 479-484 (ESCAPE 35), doi:10.69997/sct.107589, open text at LAPSE:2025.0228 | sections 3.1, 4.1, 4.2: Aspen Plus whole-plant design of 120 kt/a (99.4 wt%, 99.9 % recovery, 272.34 kmol/h acrylonitrile from the reactor) with the slate of SRC-1; fluid bed 2.0 bar, 440 C; feed 1/1.2/9.8; effluent cooled to 220 C before an acid quench at 1.9 bar (ammonium sulfate co-product); absorber 24 stages at 1.6 bar with water at 5 C; recovery column 36 stages with an overhead decanter; HCN, acrolein, extractive acrylonitrile/acetonitrile/water and pressure-swing acetonitrile sections; base case 48.42 MW hot and 43.15 MW cold utilities (of which 3.39 MW refrigeration of the absorber water ABS-H2O from 25 to 5 C) after 11.88 MW recovered; reaction heat 59.74 MW; LP steam 6 barg, VHP 40 barg; section 3.1: UNIQUAC-RK, a stoichiometric reactor on the patent's activity data (the reaction set is not listed); section 4.2.1 and the abstract: Design 1 needs 28.87 MW hot utility (2.26 MW fuel gas, 26.61 MW LP steam), 86.91 % less fuel gas and 17.38 % less LP steam than the base case, LPS placed on the reactor feeds C1, C2, C11 only at an intermediate stage, to avoid fuel gas; section 4.2.3: the cold streams C3 to C10 need 42.02 MW, the reactor feeds C1, C2, C11 take 5.28 MW of steam and 9.71 MW from the effluent H1 to 420 C, and 1.40 MW of the reaction heat to 440 C | read (open PDF); facts only | D-001, D-002, D-004 to D-009 |
| SRC-3 | US EPA (1984) Locating and Estimating Air Emissions from Sources of Acrylonitrile, EPA-450/4-84-007a, https://19january2021snapshot.epa.gov/sites/static/files/2020-09/documents/acrylonitrile.pdf | pp. 8, 16 to 22: the SOHIO process used by all US producers; near-stoichiometric feed, typical propylene/ammonia/air 1/1.06/8.4; 200 kPa, 400 to 510 C; reactor heat to a waste-heat boiler; water quench with sulfuric acid against unreacted ammonia, liquor stripped and sent to deep wells; absorber, recovery, acetonitrile, light-ends (HCN) and product columns; absorber vent about 0.001 wt% acrylonitrile, incinerated at 98 % or more; start-up venting; column vents to a flare | read (US government work); facts only | D-001, D-005 to D-008, LCA exclusions |
| SRC-4 | IPCC (2006) 2006 IPCC Guidelines for National Greenhouse Gas Inventories, Vol. 3, ch. 3, section 3.9, https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/3_Volume3/V3_3_Ch3_Chemical_Industry.pdf | Box 3.12 (p. 3.61): the SOHIO process and its reactions (acrylonitrile, HCN, acetonitrile, feedstock oxidation); more than 90 % of acrylonitrile by this route; about 70 % of the propylene to acrylonitrile and 85 % to the three nitriles; Table 3.22 (p. 3.79): process CO2 1.00, 0.83 and 0.79 t/t by configuration, and the text under it (p. 3.79): 1.09 t propylene per t at about 70 % yield, 18.5 kg acetonitrile and 105 kg HCN per t, all from the 2003 LVOC BREF; CH4 0.18 kg/t (p. 3.79), which IPCC takes from the APME life-cycle report (Boustead 1999) on European plants of 1990 to 1996; Table 3.26 (p. 3.82): the same 18.5 and 105 kg/t, its source given as European IPPC Bureau 2005 (LVOC BAT document, section 11.3.4) | read; facts only | D-001, D-004, benchmarks |
| SRC-5 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment), through `cheme chemistry thermo` and `cheme chemistry library acrylonitrile`, and thermo directly for scripts/utilities.py | per component, as its `source:` in process/materials.yaml names: formation enthalpy (methods ATCT_G, CRC, API_TDB_G, WEBBOOK), entropy (CRC, YAWS, WEBBOOK), Cp/R (Poling et al., 5th ed., or fitted to thermo's TRCIG, HEOS_FIT and WEBBOOK_SHOMATE correlations), critical constants (HEOS, IUPAC, PSRK, YAWS); for scripts/utilities.py: liquid water heat capacity 278 to 308 K and the heats of vaporisation of ammonia and propylene at 298.15 K (thermo HEOS_FIT) | open-source packages queried; single values, facts only (library ADR 0037); the underlying works (ATcT, the CRC Handbook, API TDB, NIST WebBook, Yaws, Poling et al., TRC, IUPAC) were not read here | materials, duties, D-009 |
| SRC-6 | PubChem PUG REST: CIDs 7855 (acrylonitrile), 6342 (acetonitrile), 768 (hydrogen cyanide) | formula, InChIKey, CAS, ChEBI cross-references | read | registry |
| SRC-7 | processes/propylene-pdh-1, ammonia-1, sulfuric-acid-1 (this library) | polymer-grade propylene, liquid ammonia, sulfuric acid 98.5 wt% | library, internal | D-003, D-011 |
| SRC-8 | US 4 341 535 (ammonium sulfate recovery from acrylonitrile quench bottoms), named by a web search | - | not read; a search snippet only (quench bottoms about 10 wt% ammonium sulfate and 16 wt% heavy organics) | not used for numbers |
| SRC-9 | EU LVOC BREF 2003 (chapter 11, acrylonitrile) and Ullmann's article on acrylonitrile | - | not read: the 2003 BREF was not found at a working open URL in this run (the 2017 revision has no acrylonitrile chapter); Ullmann's is licensed | route lead only; its numbers reach this entry only through SRC-4 |

Searched and not found openly (2026-11-19): kinetics of propylene ammoxidation usable at plant
scale, an open VLE/LLE set for acrylonitrile, acetonitrile, HCN and water with a qualified
package, plant-specific steam and power consumptions, the catalyst make-up per tonne, prices.

## D-001 Route and boundary (2026-11-19)
Decision: the SOHIO process (SRC-3, SRC-4): propylene, ammonia and air in a fluidised bed over a
multicomponent bismuth molybdate catalyst, effluent heat to steam, a sulfuric-acid quench taking
the unconverted ammonia as ammonium sulfate, absorption of the nitriles in chilled water, an
extractive recovery column, an acetonitrile stripper and purification, an HCN column and a
drying/product column (lumped), and a thermal oxidiser on the absorber off-gas and the heads cut
with a waste-heat boiler. HCN and acetonitrile are recovered as co-products (the task's scope).

Rejected:
- propane ammoxidation (SRC-4 names it, with propane plus hydrogen peroxide; no open process
  data: SRC-4 gives no method for it);
- older routes (acetylene plus HCN, ethylene oxide plus HCN): superseded, more than 90 % of
  production is SOHIO (SRC-4);
- bio-based routes (glycerol or 3-hydroxypropionic acid): not industrial;
- burning the HCN and acetonitrile instead of recovering them (SRC-3 says most were incinerated
  in 1984 US plants): the task asks for co-products; the configuration matters for the CO2
  (SRC-4 Table 3.22) and is noted in D-011.

Boundary: from the propylene, ammonia, acid and air at the battery limit to the three products in
storage, the quench liquor and wastewater to their treatment, and the flue gas to the stack.
Ammonium sulfate crystallisation, the HCN user, product storage and the flare are outside.

## D-002 Capacity, product and operating hours (2026-11-19)
15 000 kg/h of product (120 kt/a at 8000 h/a, ASSUMED), the capacity of SRC-2, so its utility
figures scale by a factor close to 1 (1.039). Product above 99.5 wt% (SRC-2: 99.4 wt%; SRC-3:
99+ %); modelled 99.75 wt%. The rate is a design specification (SP-RATE): propagate solves the
propylene feed for 15 000 kg/h of S27.

## D-003 Feeds (2026-11-19)
- Propylene taken as pure (propylene-pdh-1 makes polymer grade; SRC-3 accepts 90+ %); ammonia
  pure; both vaporised at the battery limit. Their vaporisation heat is not modelled (L-4): at
  298.15 K it is 2.36 MW for the ammonia and, if the propylene arrives liquid, 1.39 MW for it
  (scripts/utilities.py, thermo heats of vaporisation, SRC-5), together 0.25 kWh per kg of
  product. At the feeds' 350 kPa(a) ammonia boils at 268 K and propylene at 257 K (thermo
  vapour pressures, SRC-5), below ambient temperature, so this is a heat sink (it could take heat from cooling water or chill the absorber water), not a
  steam demand: leaving it out overstates the cooling and the chiller, it understates no burden.
- Feed ratios propylene/ammonia/air 1/1.2/9.8 mol (SRC-1's test feed, used by SRC-2); SRC-3's
  1984 plant ratio, 1/1.06/8.4, belongs to an older catalyst. The followers of SP-RATE carry them
  as mass ratios: NH3 1.2 x 17.0305/42.0797 = 0.48566 kg/kg, air 9.8 x 28.9593/42.0797 = 6.744317
  kg/kg (dry air N2/O2/Ar 0.7812/0.2095/0.0093, ASSUMED).

## D-004 Reactor R101: conversion and selectivities (2026-11-19)
Decision: a conversion step with SRC-1's evaluation 1, example 1 (440 C, 0.14 MPa, WWH 0.085
1/h): the invention's first example, tested at what the patent calls the higher pressure and
duty, and the one example evaluation 3 repeats across pressures (its 0.14 MPa row is the same
result). SRC-2 takes this patent's activity data. The patent does not say whether its pressures
are absolute or gauge, so no row is "closest" to the plant's 200 kPa(a); across evaluation 3
(0.08 to 0.15 MPa) the acrylonitrile yield moves between 78.2 and 80.1 %, under 2 points. The source's yields add up to
97.6 %, against a conversion of 97.5 %: they are single-pass carbon yields (molar yields would
not add up to the conversion). We normalise them to the conversion (factor 97.5/97.6) and convert
them to kmol of product per kmol of propylene converted, as core's `selectivity:` takes them:
acrylonitrile 0.816598, HCN 0.058402 (three per propylene), acetonitrile 0.043033 (1.5 per
propylene), acrolein 0.005123, acrylic acid 0.015369, CO 0.095287 and CO2 0.248975 (three per
propylene). The ammonia converted (96.5 % of 1.2 mol) exceeds the nitrogen of the nitriles: the
rest (0.263 mol per mol propylene fed) is taken as burnt to N2 (reaction NH3_OX, ASSUMED: the
source measures no N2), selectivity 0.134830 to N2. The oxygen left at the outlet is 0.72 % of
the effluent by mass (891 kg/h).
- Outlet 713.15 K and 200 kPa(a) (SRC-2); the mixed feed at 373.15 K is an ASSUMED stand-in for
  separately fed, partly preheated feeds (L-4). The catalyst window warning at the inlet is
  accepted in checks.yaml: the feeds heat up in the bed.
- Result: 283.4 kmol/h acrylonitrile formed, 0.999 kg propylene per kg product. The reactor duty
  cheme calculates, Q4 = 56.8 MW, is net of heating the feed S5 in the bed from 373 to 713 K
  (15.0 MW, scripts/utilities.py). With the feed at the reactor temperature, SRC-2's basis (its
  feeds reach 420 C before the bed and 440 C with 1.40 MW of the reaction heat), the reaction
  heat is 71.9 MW, 913 MJ per kmol acrylonitrile, against SRC-2's 59.74 MW at 272.34 kmol/h,
  790 MJ/kmol (808 with the 1.40 MW): 13 to 16 % higher per kmol. NH3_OX, the ASSUMED burning
  of the surplus ammonia, accounts for most of the difference: 46.8 kmol/h x 632 MJ/kmol =
  8.2 MW (`cheme process reactors`), 104 MJ/kmol acrylonitrile; without it the reaction heat is
  808 MJ/kmol. SRC-2 does not list its reactions; that it leaves the surplus ammonia unburnt is
  our inference, not a statement of the source.
- Rejected: kinetics (none open at plant scale); SRC-4's yields (70 % on propylene, a 2003 plant
  average, D-011 benchmarks); SRC-3's 1984 yields (73 wt%).
- Catalyst inventory not sized: SRC-1's WWH of 0.085 1/h would mean about 176 t, a bench value.

## D-005 Quench (2026-11-19)
R102 neutralises all unconverted ammonia (254.6 kg/h) with sulfuric acid 98.5 wt%, spec SP-ACID
at 0.525 mol H2SO4 per mol NH3 (5 % excess, ASSUMED). The quench separator Q101 sends the salt,
the excess acid, the acrylic acid (which polymerises and leaves with the heavies, ASSUMED), 10 %
of the water and small organic losses (0.2 % of the acrylonitrile, 1 % of the acetonitrile) to
the liquor: 3.59 t/h with about 28 wt% ammonium sulfate. Gas leaves at 358 K, is cooled to 313 K
(E-102) and goes with its condensate to the absorber. Conditions after SRC-2 (220 C in, 1.9 bar)
and SRC-3 (acid quench, stripped liquor). The liquor's stripping and the salt recovery are not
modelled (L-6). The quench has no energy stream: the gas's sensible heat from 493 to 358 K alone
is 5.8 MW (ideal gas, scripts/utilities.py), before the heat of neutralisation (L-6) and of the
water condensed into the liquor. SRC-2's plant has the same quench and cools the gas to 30 C
before the absorber (section 4.1), so this heat is inside its cold utility and with it inside
the cooling-water lump Q8 (D-009); in a hot-gas quench most of it evaporates liquor water and
reaches E-102. A separate quench duty would count it twice.

## D-006 Absorber and lean-water loop (2026-11-19)
A101 is a component separator with ASSUMED splits: 99.99 % of the acrylonitrile and acetonitrile,
99.5 % of the HCN and 98 % of the acrolein to the rich water; water to the off-gas 0.12 % (the
off-gas comes out near saturation at 283 K: 399 kg/h computed, about 440 kg/h at saturation).
The off-gas carries 0.0018 wt% acrylonitrile, the order SRC-3 gives (0.001 wt%). Water rate: spec
SP-LG, 4.0 mol of lean water per mol of absorber inlet (about 5.8 per mol of the non-absorbed gas,
an absorption factor near 1.4 for acrylonitrile at 278 K with an ASSUMED activity coefficient of
about 100), solved by varying the lean-water split SPW (0.947 of the lean water returns, 313.5 t/h).
The loop is torn at S20 and converges in 2 Broyden iterations with the three specs.
SRC-2's refrigeration of its absorber water (3.39 MW from 25 to 5 C, section 4.1) implies about
146 t/h of water; S20 is 2.15 times that. The rate is not tuned to SRC-2's, whose absorber
design (UNIQUAC-RK) is not given in the paper: with our ASSUMED activity coefficient the lower
rate would put the absorption factor below 1, too low for 99.99 % recovery. The consequences are
carried where they can be: the chiller is sized on S20 (D-009). The recovery column's steam and
the lean-water cooling scale with the water circulated, but the lumps Q7 and Q8 scale with
capacity only, so in this respect they are low (L-2).

## D-007 Recovery and purification columns (2026-11-19)
All component separators with ASSUMED splits, the columns' stages and refluxes not designed (no
qualified property package, L-1):
- C201 recovery column with its decanter: 99.9 % of the acrylonitrile, all HCN and acrolein, 2 %
  of the acetonitrile and 0.19 % of the water overhead (crude 3.9 wt% water); the acetonitrile
  stays in the water (extractive distillation, SRC-2).
- C202 stripper: the acetonitrile overhead with some water (16 wt%), lean water from the bottom.
- C203 acetonitrile purification (SRC-2: a pressure-swing pair): 98 % recovery to 99.5 wt%.
- C301 HCN column: 99.8 % of the HCN overhead at 99.7 wt%.
- C302 drying and product column: 99.8 % of the acrylonitrile to the product; water, acrolein and
  the rest of the HCN to a heads cut that is burnt (in plants acrolein is often recovered or
  converted; SRC-2 has an acrolein section).
Overall acrylonitrile recovery: 99.5 % of what the reactor makes (SRC-2: 99.9 %).
Not modelled or screened: the stabilisers. Liquid HCN (S25, 546 kg/h at 99.7 wt%) self-polymerises
unless acid-stabilised; acrylonitrile polymerises explosively with strong alkali (SRC-3 p. 5) and
the product needs an inhibitor (MEHQ, ASSUMED). Neither dosing is in the balance, and the HCN hazard needs a
screen before any HAZOP (open input).

## D-008 Thermal oxidiser (2026-11-19)
The absorber off-gas (85.4 t/h, 91 wt% N2) and the heads cut are burnt with natural gas support
fuel (0.005 kg per kg propylene, 75 kg/h) and combustion air (2.0 mol per mol propylene), 99 %
destruction of every combustible (ASSUMED; SRC-3: 98 % or more, with supplemental fuel because
97+ % of the gas is not combustible). The firebox and its boiler are one conversion step whose
outlet is the stack at 473 K: cheme calculates the heat to steam, 4.06 MW. cheme's screening
(`cheme process reactor-hazards`, core 1.13.0) gives 152 K for its largest single reaction
(propylene burnt); the sum of its seven per-reaction rises, our estimate of the whole charge
burning at once, is 306 K from 298 K. (Core 1.12.0 gave 156 K and 313 K: 1.13.0 screens the
step at its outlet's 473 K instead of the feed's 298 K.) Either way the off-gas's own CO and propylene do not reach an oxidation
temperature without preheat, so the fuel figure presumes a recuperative preheat of the off-gas
to about 800 K (ASSUMED, not modelled; with no preheat the
support fuel would be about an order of magnitude larger). Fuel nitrogen goes to N2 in the model:
NOx is not estimated (L-5, an LCA exclusion).

## D-009 Utilities and energy (2026-11-19)
- HP steam (4100 kPa(a), SRC-2's VHP level): reactor coils 56.8 MW (cheme, conversion duty),
  effluent boiler E-101 10.1 MW (scripts/utilities.py, ideal gas 713 -> 493 K), oxidiser boiler
  4.1 MW (cheme): 71.0 MW, 4.73 kWh per kg of product, gross.
- LP steam to all reboilers: SRC-2's base-case hot utility, 48.42 MW, includes the preheat of the
  reactor feeds C1, C2 and C11 (propylene, ammonia, air) to 440 C: 5.28 + 9.71 MW to 420 C and
  1.40 MW to 440 C (section 4.2.3), 16.39 MW, which LP steam at 160 C cannot deliver and which the
  base case fires (Design 1's figures put the base case at 2.26/(1 - 0.8691) = 17.3 MW of fuel gas
  and 26.61/(1 - 0.1738) = 32.2 MW of LP steam, section 4.2.1 and the abstract). This plant does
  not preheat its feeds: the compressed air (407 K) and the vaporised feeds mix adiabatically to
  376 K, for which S5's 373.15 K stands, and the rest of the heating happens in the bed, netted
  out of Q4 (D-004). So the LP steam is (48.42 - 16.39) MW = 32.03 MW scaled by 15 000/14 437,
  33.3 MW (2.22 kWh/kg), ASSUMED, as one lump on C201 (L-2); scripts/utilities.py.
- Refrigeration: the lean water S20 (313.5 t/h, D-006) chilled from 308 K, the lowest the
  25/35 C cooling water reaches with its 10 K approach, to 278 K: 10.94 MW (liquid water heat
  capacity, SRC-5), at an electric COP of 4.0 (ASSUMED): 2.73 MW (scripts/utilities.py). SRC-2's
  3.39 MW chills about half as much water from 25 C (D-006).
- Cooling water: (43.15 - 3.39) MW of SRC-2 scaled, 41.3 MW, plus the chiller's condenser
  (refrigeration plus power, 13.7 MW): 55.0 MW (3.67 kWh/kg), as one lump on E-102 (L-2), at
  25/35 C, the library cooling tower's range (SRC-2 uses 20-25 C water), so that it links to
  utility-cooling-tower. The quench's heat is inside it (D-005); the feed vaporisers' cold
  (D-003) is not credited against it.
- Power: air compressor 3.22 MW (scripts/utilities.py: ideal gas, 101.3 -> 250 kPa(a),
  isentropic efficiency 0.80, motor 0.96, ASSUMED), chiller 2.73 MW, pumps 0.6 MW (ASSUMED lump):
  6.56 MW, 0.44 kWh per kg. A steam-turbine drive of K-101 on the HP steam is the usual
  alternative.
- SRC-2's base case is not heat-integrated; its Design 1 needs 17 % less LP steam and its
  Designs 2 and 3 import none (they use the reaction heat). In that respect the lumps are upper values for a modern plant; in
  another they are low: they scale with capacity, not with this design's water circulation,
  which is twice SRC-2's (D-006).

## D-010 Equipment list (2026-11-19)
The flowsheet's unit steps link their tags (`links:`): one or more per step, the columns lumped
as in the PFD. The quench steps R102 and Q101 share C-101 (Q101 with its pump P-101), A101 has
C-102 and the chiller E-103, C201 has C-201 and the decanter V-201. The mixers and the splitter
M101, SPW, M201 and M401 are modelling nodes without a tag (M101 is R-101's feed distribution,
M401 H-401's burner). Design pressures and temperatures are concept values (operating plus
margins), ASSUMED; no sizes.

## D-011 Preliminary gate-to-gate LCI (2026-11-19)
`lca/lca.yaml`, written by `cheme assess lca --write`. Per kg of product, unallocated: propylene
0.999 kg, ammonia 0.485 kg, sulfuric acid 0.052 kg, natural gas 0.005 kg, electricity 0.44 kWh,
LP steam 2.22 kWh, cooling 3.67 kWh, HP steam export 4.73 kWh, quench liquor 0.239 kg,
wastewater 1.17 kg, fossil CO2 0.463 kg (reactor 0.254, oxidiser 0.209, of which the support
fuel 0.014).
- Links in the library's Atlas build (scripts/build_lci.py): propylene, ammonia and sulfuric acid
  to propylene-pdh-1, ammonia-1 and sulfuric-acid-1 and the LP steam to the shared steam-heat
  entry (`lca/mappings.yaml`); electricity, cooling water and wastewater through process.yaml's
  chemistry slugs (electricity, cooling-water, wastewater) to the shared entries of
  lci/mappings.yaml (medium-voltage electricity, the cooling-water and wastewater-treatment
  services). Gaps there, each with its connection named in lca.yaml: natural gas, the quench
  liquor, the exported HP steam, the catalyst make-up (60 t/a, ASSUMED order of magnitude) and
  the emissions without a characterisation. In this folder's own LCI (`cheme assess lca`,
  lca/gaps.csv) every background is a gap.
- The exported HP steam (product:HPS) has no mapping on purpose: the build writes every linked
  non-product exchange as a positive technosphere amount, i.e. a consumption, so linking it as
  steam heat would book the export as 71 MWh/h of steam bought in. Its credit or allocation needs
  the receiving site's avoided steam and the practitioner's decision; until then it is a gap.
- Allocation by mass between acrylonitrile (93.0 %), HCN (3.4 %) and acetonitrile (3.6 %): one
  reactor fixes the split, no physical relationship and no sourced prices (docs/system-model.md).
  All burdens to acrylonitrile is the conservative bound (+7.5 %).
- Benchmarks (`benchmarks/nitrogen-organics.yaml`): propylene 0.999 against SRC-4's 1.09 t/t and
  process CO2 0.46 against 0.79 t/t (HCN and acetonitrile recovered): both below, recorded with
  the reason (a newer catalyst than the 2003 plants). HCN 36 kg/t and acetonitrile 39 kg/t
  against SRC-4's 105 and 18.5 kg/t: the slate of the newer catalyst makes far less HCN.
- Emission exclusions (lca.yaml, each with the method that covers its source): start-up venting
  at the absorber vent C-102 (non-routine; SRC-3 pp. 19-22: up to 4500 kg/h acrylonitrile for
  about four one-hour start-ups a year), the column vents to the flare (flare), breathing of the
  tanks, which are not in the equipment list (storage-tank), and the oxidiser's NOx (combustion,
  D-008, L-5).

## Method and dependency table

| quantity | method | provenance |
|---|---|---|
| propylene, ammonia, air, acid, fuel feeds | `specs:` SP-RATE (with followers), SP-ACID | calculated (cheme) |
| reactor outlet S6 | conversion step, `selectivity:` of SRC-1 | calculated (cheme) |
| quench outlet S9 | conversion of NH3 (NEUT) | calculated (cheme) |
| separators Q101, A101, C201 to C302 | `recovery:` (ASSUMED splits) | calculated (cheme) |
| lean-water recycle S20 | tear, SP-LG on the split SPW | calculated (cheme) |
| oxidiser outlet S34 | conversions (ASSUMED) | calculated (cheme) |
| Q4, Q6 | conversion-step duties (ideal gas) | calculated (cheme) |
| Q1, Q5 | scripts/utilities.py (ideal gas) | assumed (script) |
| Q2 | scripts/utilities.py: S20 chilled from 308 K, COP 4.0 ASSUMED | assumed (script) |
| Q7, Q8 | scripts/utilities.py: SRC-2's utilities less its feed preheat (Q7) or refrigeration (Q8), scaled; Q8 with the chiller's condenser | assumed (script) |
| Q3 | ASSUMED lump | assumed |
| temperatures, pressures | design basis | assumed |

## Core features used (core 1.12.0)
- `specs:` on feed flows with followers and on a splitter's outlet (ADR 0070): the product rate,
  the feed ratios, the acid excess and the absorber water rate are calculated, not typed.
- `recovery:` component separators (ADR 0070) for the quench, absorber and five columns.
- `tears:` with Broyden alongside the specs (ADRs 0060, 0070).
- Conversion steps with a node `selectivity:` (eight reactions, one key) and their duties
  (ADR 0059).
- `cheme process reactor-hazards` (screening only; a continuous cooled fluid bed is not a
  semi-batch). Its bound for R101 is 2150 K: the largest single reaction, the complete
  combustion of propylene to CO2, run to completion over the heat capacity of the whole feed (the
  ammoxidation alone gives 1270 K). It says why the bed's cooling coils and trips matter, not a
  criticality class.

## Core limits hit (each a candidate core issue)
- **L-1** No property package covers acrylonitrile, acetonitrile, HCN and water (with their
  azeotropes and the liquid-liquid split): the columns are component splits, not stage models,
  and their duties are not calculated.
- **L-2** A `recovery:` separator has no energy model: its reboiler and condenser duties cannot be
  derived from the split, so the steam and cooling water are lumps on one step each.
- **L-3** Propagate writes every component of the flowsheet into each stream it derives (zero
  flows included), so a stream template must list all components, which makes templates
  meaningless for this plant (materials.yaml).
- **L-4** A mixer has no energy balance: the reactor feed temperature (and with it the reactor
  duty) is typed, not the adiabatic mix of the compressed air and the vaporised feeds (376 K by
  scripts/utilities.py against the typed 373 K); the feed vaporisers' heat, 3.75 MW (D-003), is
  outside the flowsheet.
- **L-5** No NOx in a combustion step: fuel nitrogen goes to N2.
- **L-6** A component with no ideal-gas formation data (ammonium sulfate) blocks the duty of the
  step that forms it: the quench's heat of neutralisation is not calculated, and `cheme assess
  lca` warns that R102 exchanges heat with no utility (its heat is inside the cooling-water lump,
  D-005).
- **L-7** A design specification cannot target a duty or a temperature: the oxidiser's support
  fuel cannot be solved for a firebox temperature.

## Open inputs
Kinetics or licensor data for the reactor; a qualified VLE/LLE model and the column designs,
with the absorber water rate (D-006); the HCN and product stabilisers and an HCN hazard screen
(D-007); the credit or allocation of the exported steam (D-011);
plant steam, power and catalyst figures; the HCN user; the ammonium sulfate recovery; prices for
an economic allocation; the start-up and flare emissions.
