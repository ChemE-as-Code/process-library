# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Vinyl acetate monomer by gas-phase acetoxylation of ethylene, issue
ChemE-as-Code/process-library#479, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD solved by core, duties, equipment list and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` with the core pin 0e85885 (v1.12.0 with #254).
Core 1.12 solves a loop with design specifications and component separators (core ADR 0070)
together with tear streams (ADR 0060), and writes a conversion step's duty on its energy stream
(ADR 0059). This entry uses all three, so the whole material balance is calculated by `cheme
process propagate` from the feeds' compositions, the reactions and the specified splits.
Templates: `oxalyl-chloride-1` (structure, source register, balance-output script),
`ethylene-glycol-1` and `acetaldehyde-1` (ethylene oxidation loops with recycle gas, purge and
CO2 removal). Requires cheme-as-code 1.12 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, Wikipedia, PubChem, the data packaged in `chemicals`
and `thermo`).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 8 765 995 B2, W. Dafinger, P. Holl, G. Rudolf, M. Schoenleben (Wacker Chemie AG), priority DE 10 2009 001 021, 2009-02-19, granted 2014-07-01: Process and apparatus for preparing vinyl acetate monomer, https://patents.google.com/patent/US8765995B2/en | background: gas-phase reaction of ethylene, acetic acid and oxygen over supported Pd catalysts with alkali salts (Au, Rh or Cd doped), fixed-bed tube reactors with 2000 to 6000 tubes cooled by boiling water, 130-200 C, 1-30 bar, steam of 1-10 bar (preferably 2.5-5 bar) raised; ethylene conversion about 10 %, acetic acid 20-30 %, oxygen up to 90 %; good ethylene selectivities above 92 %, VAM to CO2 about 7 to 1, so about half the heat comes from the CO2; heats of reaction -176 kJ/mol (VAM) and -1324 kJ/mol (CO2 side reaction); the work-up (condensation, acetic acid scrubber, CO2 removal from all or part of the cycle gas, multistage distillation: dewatering, azeotropic, pure VAM columns). Example: KL 7900 SH catalyst (1.5 wt% Pd, 1 wt% Au), cycle gas 8.5, 150-155 C; Tables 1 to 4: feed 61-65 mol% ethylene, 11.5-12.3 mol% acetic acid, 6.8-8.8 mol% oxygen, GHSV 3600-3820 1/h, STY 850-980 g/(l h), ethylene selectivity 90.9-93.4 %, oxygen selectivity 55-80 %; tubes 33 and 27 mm, 6.30 m | read (Google Patents); patent, facts only | D-001, D-004, D-005, D-008, benchmark |
| SRC-2 | US 8 410 307 B2, M. Guenaltay, W. Dafinger, P. Holl (Wacker Chemie AG), priority DE 10 2010 001 097, 2010-01-21, granted 2013-04-02: Method for producing vinyl acetate, https://patents.google.com/patent/US8410307B2/en | description and example: tube reactors, 8-12 bar(a) cycle gas, 130-200 C; product gas with VAM, ethylene, acetic acid, water, oxygen, CO2, ethyl acetate, inerts; brought to 115-130 C into a preliminary dewatering column run at cycle-gas pressure (bottoms 100-120 C), overhead cooled to -20 to +50 C and decanted (organic phase 90-99 wt% VAM, 0.5-8 wt% water); the uncondensed gas scrubbed with acetic acid, its bottoms to the azeotropic column (top 1.1-1.5 bar(a), 50-90 C; bottoms mostly acetic acid, back to the scrubber or the reactor); a dewatering column (top 1.1-2 bar(a), 50-90 C) with the pure VAM side draw between the 5th and 20th plate above the bottom, its bottoms (0.5 % of the feed in the example) back to the azeotropic column; product >= 99 wt% (preferably >= 99.95), <= 100 ppm water, <= 50 ppm acetic acid; example side draw 99.998 wt% | read (Google Patents); patent, facts only | D-001, D-005, D-007 |
| SRC-3 | US 6 420 595 B1 (Millennium Petrochemicals, priority 2001-09-10): Process control for vinyl acetate manufacture, https://patents.google.com/patent/US6420595B1/en | ethylene and acetic acid in excess (ethylene at least 60 mol% in the reaction section); the acid tower saturates the ethylene with acid; a slip stream of the recycle gas through a scrubber to a potassium carbonate absorber that removes almost half of its CO2, regenerated in a stripper (CO2 and water to flare); absorber bottoms about 1-4 wt% K2CO3 and 20-25 wt% KHCO3, potassium acetate below 4 wt%; nitrogen and argon purged; acid tower liquid 70-95 % acetic acid in water | read (Google Patents, first 100 000 characters); patent, facts only | D-005, D-006, D-007 |
| SRC-4 | US 5 550 281 A (The Standard Oil Company, priority 1994-06-02): Fluid bed process for the acetoxylation of ethylene in the production of vinyl acetate, https://patents.google.com/patent/US5550281A/en | fluid bed with the oxygen fed separately into the bed, so that no flammable mixture forms outside it; 8-25 % oxygen, 30-70 % ethylene, 10-25 % acetic acid, 100-250 C (preferably 135-190 C), 50-200 psig; nearly isothermal bed | read (Google Patents); patent, facts only | D-001 (rejected alternative), D-009 |
| SRC-5 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment, C. Bell, MIT): ATcT and CRC (standard-state table) ideal-gas and liquid formation enthalpies, CRC entropies, Yaws's ideal-gas entropy of vinyl acetate (the only one packaged), Poling et al. (5th ed.) ideal-gas heat-capacity polynomials, CRC normal boiling points and liquid heat capacities; thermo's TRCIG ideal-gas and ZABRANSKY_SPLINE_C liquid heat capacities of vinyl acetate, its vapour pressures (Wagner-McGarry for vinyl acetate and acetic acid, IAPWS for water) and its Dortmund UNIFAC (the DOUFIP2016 parameters) | formation enthalpies (kJ/mol, ideal gas): ethylene 52.56, ethane -83.78, CO2 -393.474, water -241.822 (ATcT), acetic acid -432.2, vinyl acetate -314.4 (CRC); liquid: water -285.825 (ATcT), acetic acid -484.3, vinyl acetate -349.2 (CRC), so the heats of vaporization to the ideal-gas monomer at 298.15 K are 44.0, 52.1 and 34.8 kJ/mol; vinyl acetate S_298 328.02 J/(mol K) (Yaws); liquid heat capacities acetic acid 123.3, water 75.3, vinyl acetate about 172 kJ/(kmol K) (298-360 K); vinyl acetate's bubble points 361.3 K at 165 kPa(a) and 362.3 K at 170 kPa(a); the acetic acid activity coefficients of D-005 and D-006 | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037); the underlying works (ATcT, the CRC Handbook, Yaws's handbook, Poling et al., the TRC tables, Zabransky et al., the Dortmund UNIFAC parameter publications) were not read here, the printed (licensed) handbooks not at all | materials, reactions, scripts/balance.py, the splits of C101, C102, C104 and C202 |
| SRC-6 | Wikipedia, Vinyl acetate, https://en.wikipedia.org/wiki/Vinyl_acetate | the ethylene route with a palladium catalyst is the major one and replaced the acetylene route (acetic acid on acetylene over zinc acetate, still about a third of world output, mainly in China); ethylidene diacetate's decomposition as a further route; flash point -8 C, autoignition 427 C, explosive limits 2.6-13.4 %; H225, H332, H335, H351 | read; CC BY-SA, facts only | D-001, D-009 |
| SRC-7 | PubChem CID 7904 (PUG REST), ChEBI (OLS search) | formula C4H6O2, InChIKey XTXRWKRVRITETP-UHFFFAOYSA-N, IUPAC name ethenyl acetate; CHEBI:46916 | read | registry |
| SRC-8 | processes/ethylene-1, acetic-acid-1, asu-1 (this library) | the feeds' grades: ethylene >= 99.95 mol% with ethane; glacial acetic acid with 691 ppm(wt) water; GOX 99.7 mol% O2 | library, internal | D-003, D-010 |
| SRC-9 | Ullmann's Encyclopedia of Industrial Chemistry, Vinyl Esters; Luyben and Tyreus's VAM plant-wide control case (Comput. Chem. Eng., 1998) | - | not read (licensed); known leads for kinetics and a full flowsheet | route lead only |

## D-001 Route and boundary (2026-11-19)

Decided: the gas-phase acetoxylation of ethylene with acetic acid and oxygen over a supported
Pd/Au catalyst with potassium acetate, in a multitubular fixed bed cooled by boiling water, as
Wacker's patents describe it (SRC-1, SRC-2): C2H4 + CH3COOH + 0.5 O2 -> CH2=CHOOCCH3 + H2O, with
the combustion of ethylene to CO2 and water as the one side reaction. Work-up after SRC-2: a
preliminary dewatering column at loop pressure whose decanter gives an organic and an aqueous
phase, an acetic acid scrubber on the cycle gas, an azeotropic column with a decanter and a
dewatering column with the pure VAM side draw. CO2 removal on a slip stream, washed first in a
scrubber and then treated with hot potassium carbonate, and an inerts purge (SRC-3). The
boundary is the plant gate: ethylene, acetic acid and oxygen in from the library's producers
(ethylene-1, acetic-acid-1, asu-1), demineralised wash water and utilities from the site, purge
and effluent to the site's treatment.

Rejected:
- **The acetylene route** (acetic acid on acetylene over zinc acetate, SRC-6): still a third of
  world output, but it needs acetylene (acetylene-1 exists, from methane partial oxidation) and
  it is the older route; the ethylene route is the major one and has open process patents.
- **Fluid-bed acetoxylation** (SRC-4, BP/Standard Oil): oxygen fed into the bed allows more
  oxygen and a near-isothermal bed, but it has one licensor, no open pilot data comparable to
  SRC-1's tables, and core has no fluid-bed model; recorded as the alternative for D-009's
  flammability question.
- **Liquid-phase acetoxylation** with dissolved palladium and copper salts (the Wacker-Hoechst
  chemistry of acetaldehyde-1 applied to acetic acid) and **ethylidene diacetate** from
  acetaldehyde and acetic anhydride (SRC-6): not read in an open source with process data here;
  neither is the dominant route.
- **A separate pure VAM column** after the dewatering column: SRC-2 claims that the side draw
  makes it unnecessary, and the product meets its specification without it (D-007).

## D-002 Capacity, product and operating hours (2026-11-19)

200 kt/a of vinyl acetate in 8000 h (25 t/h), ASSUMED: a normalisation basis for the
inventory, of the order of a single-train plant, not an owner figure. The product is the
dewatering column's side draw cooled to 303 K: 99.99 wt% with 90 ppm(wt) water as the ASSUMED
splits give it (SRC-2: >= 99.95 wt%, <= 100 ppm water); its inhibitor is not modelled (a cut-off
input of the LCI, D-010).

## D-003 Feeds (2026-11-19)

The feeds are the library producers' products (SRC-8): ethylene at 99.95 mol% with 0.05 mol%
ethane, GOX at 99.7 mol% with the rest counted as argon, glacial acetic acid with 691 ppm(wt)
water (propionic acid not modelled). Their flows are not given: core's design specifications
solve them (D-004). The slip-gas scrubber C-104 takes 540 kg/h of the site's demineralised
water (D-006).

## D-004 Reactor feed, conversions and the design specifications (2026-11-19)

The reactor feed is Wacker's Table 2 composition (SRC-1, comparative 33 mm tube after 400 h):
65 mol% ethylene, 12.3 mol% acetic acid, 8.6 mol% oxygen. Four specifications (`specs:`,
core ADR 0070) make the flowsheet reach it: the ethylene feed S1 for 200 kt/a of vinyl acetate
in S33, the oxygen S7 for 8.6 mol%, the fresh acid S4 for 12.3 mol% (the recycle acid follows
from the splits), and X102's CO2 slip fraction for 65 mol% ethylene (0.337). They are solved
together with the three tears (D-005).

R101 is a conversion reactor. The same table's space-time yield (900 g VAM per litre of
catalyst and hour) at its GHSV (3750 1/h, taken at 273.15 K and 101.325 kPa, ASSUMED) gives
0.0625 mol of VAM per mol of feed; at the table's ethylene selectivity of 91.0 % that is
9.61 % of the inlet ethylene to VAM and 0.95 % burnt (process/reactions.yaml shows the
arithmetic). The resulting oxygen conversion, 58 %, and oxygen selectivity, 63 %, lie near the
table's 65-70 % and below SRC-1's "up to 90 %". The ethylene's 10.6 % per pass matches SRC-1's
"about 10 %"; the acetic acid's 51 % is above SRC-1's general 20-30 %, which belongs to its
background, not to the table: the table's feed and yield fix it. Acetic acid's own combustion
and the by-products (ethyl acetate, acetaldehyde, methyl acetate, heavies) are not modelled.

The catalyst volume this implies, 28 m3, gives about 5200 tubes of 33 mm and 6.3 m, inside
SRC-1's 2000-6000 tubes of industrial reactors: a check that the pilot data scale.

## D-005 Loop, separators and tears (2026-11-19)

Temperatures and pressures are ASSUMED inside SRC-1 and SRC-2's ranges: reactor 1000 kPa(a),
423 K in and 438 K out; effluent cooled to 398 K into C-101 (115-130 C); C-101's bottoms
383 K (100-120 C), its overhead condensed at 308 K (-20 to +50 C). The separators are
component splits (`recovery:`, core ADR 0070), ASSUMED design specifications:

| step | split (share of each component's inlet) | checked against |
|---|---|---|
| C101 | gases all to the gas; VAM 25 %, water 3 %, acid 0.2 % to the gas; VAM 55 %, water 2 % to the organic phase; water 14 %, acid 0.2 %, VAM 0.03 % to the aqueous phase; the rest to the bottoms | organic phase 98.9 wt% VAM, 1.1 wt% water (SRC-2: 90-99 wt%, 0.5-8 wt%); aqueous phase see below |
| C102 | gases all overhead; VAM 0.5 %, water 30 %, acid 12.5 % with them | VAM in the scrubbed gas 0.01 mol%; acid 0.41 mol%, 95 % of the equilibrium with the lean scrub acid (below) |
| C104 | gases and VAM all to the gas; water 25 % (the gas leaves near saturation at 313 K), acid 1 % with it; the rest to the liquor | below (D-006) |
| A101 | CO2 45 % to the vent; ethylene, ethane, oxygen, argon 0.1 % with it | SRC-3: almost half the CO2 |
| C201 | organic phase VAM 99.5 %, water 2 %; aqueous phase water 75 %, VAM 0.4 %; the rest to the bottoms | recycle acid 93.3 wt% (SRC-3: 70-95 %) |
| C202 | side draw VAM 99.3 %, water 0.75 %; top water 99.249 %, VAM 0.2 %; the rest (0.5 % of the feed, with 0.001 % of its water) to the bottoms | SRC-2: bottoms 0.5 % of the feed; product 99.99 wt% |

C-101's aqueous phase. SRC-2's claim 1 takes off the aqueous phase that the condensed overhead
forms (step c) and sends only the organic phase on or back as runback; it gives no amount. The
amount here: the overhead vapour of a column whose top liquid splits into two phases carries
water and VAM in the ratio of their activities times their vapour pressures, 0.33-0.39 mol of
water per mol of VAM at 323-338 K (thermo's Dortmund UNIFAC and vapour pressures, SRC-5; taken
0.35, ASSUMED). The overhead's 234 kmol/h of VAM then carry 82 kmol/h of water; less the 13 in
the gas and the 9 in the organic phase, 60 kmol/h (14 % of the reactor effluent's water)
separate as the aqueous phase S38, to the effluent with C-201's aqueous phase. It holds VAM in
about the ratio to water
of C-201's decanter (S27), both decanted near 310 K (ASSUMED; Dortmund UNIFAC's liquid-liquid
split of VAM and water is far from SRC-2's organic phase and is not used), and acid as the gas's
share. Without this outlet the water went through C-201's overhead (its boil-up scales with it).

C-102's acid overhead. The gas leaves the top in contact with the lean scrub acid S15 (80.7
mol% acid, 19 % water, 313 K): with Dortmund UNIFAC (acid activity coefficient 1.02) and the
acid's vapour pressure (4.7 kPa) the gas in equilibrium with it holds 0.43 mol% acid at 880
kPa(a), so the scrubber strips acid into the gas, which enters with 0.02 mol%. The split takes
12.5 % of the acid overhead: 14.6 kmol/h, 0.41 mol%. The cycle gas returns it to the reactor;
the purge and the CO2 slip carry their shares (D-006).

The gases dissolved in the liquids are not modelled: they leave overhead (in a plant a flash
recovers them to the loop). X201 sends 30 % of the recycle acid to the scrubber and 70 % to the
saturator, ASSUMED. Three streams are torn: the cycle gas S2, the recycle acid S28 and C-202's
bottoms S31 (core ADR 0060); the Newton solver converges them with the four specifications in a
few iterations.

## D-006 Purge, CO2 removal and the cycle gas (2026-11-19)

The purge X101 takes 0.3 % of the scrubbed gas, ASSUMED: argon reaches 4.5 mol% and ethane
1.1 mol% at the reactor inlet, and the purge carries 9.1 g of ethylene per kg of product to the
thermal oxidiser. A larger purge loses more ethylene, a smaller one dilutes the loop; the choice
is open (an ethylene recovery on the purge, SRC-3, is a next-stage option). The CO2 removal
treats the share of the gas that holds the reactor feed at 65 mol% ethylene (33.7 %, D-004);
the reactor feed then holds 6.8 mol% CO2. The regenerator's CO2 (0.0995 kg/kg) goes to
atmosphere in the base case with the co-absorbed ethylene (ASSUMED 0.1 %, 1.0 g/kg); SRC-3
sends it to a flare.

The slip carries the scrubbed gas's acid, 4.9 kmol/h (about 300 kg/h). Hot carbonate would turn
it into potassium acetate, losing the acid and the carbonate. As SRC-3 does, a scrubber C-104
washes the slip ahead of the absorber: 540 kg/h of demineralised water (about 6 mol per mol of
the acid, ASSUMED) take out 99 % of it. With Dortmund UNIFAC the acid's equilibrium ratio in
water at 313 K and 875 kPa(a) is 0.010 (at the liquor's 16 mol%) to 0.018 (dilute), so the
absorption factor is 1.4-2.5 and about six stages reach 99 % (Kremser, ASSUMED); the liquor's own
equilibrium (0.16 mol% acid) stays below the gas's 0.41 mol%. The vinyl acetate passes (it is
almost insoluble in water); the gas leaves near saturation with water (a quarter of the water in
goes with it, ASSUMED). The liquor S37 (16 mol% acid, 323 K adiabatic, `scripts/balance.py`)
goes to C-201, which recovers the acid. The 1 % left, 0.05 kmol/h (3 kg/h, 0.12 g/kg), reaches
the carbonate: in the model it passes back to the loop with the treated gas S22 (A101's split
has no acid outlet); in a plant the carbonate takes it up as potassium acetate, consuming about
0.14 g of K2CO3 per kg of product (half a mole per mole of acid), which leaves with the bleed that keeps the potassium acetate
below 4 wt% (SRC-3). Both are cut-off inputs of the LCI (D-010).

## D-007 Distillation (2026-11-19)

As SRC-2: the azeotropic column C-201 takes the bottoms of C-101 and C-102 and of C-202 (and
here the liquor of C-104, D-006), distils the vinyl acetate-water heteroazeotrope overhead to a
decanter and leaves the acetic acid at the bottom; the organic phases of C-101 and C-201 are
collected (V-201) and fed to the dewatering column C-202, which takes water overhead and the
product from its stripping section. The aqueous effluent (the water phases of C-101 and C-201
and C-202's top, 0.280 kg/kg) carries 1.5 wt% vinyl acetate and 0.65 wt% acetic acid to
biological treatment: 0.41 % of the vinyl acetate formed. A stripper returning it to the
decanter is a next-stage option. Column pressures: C-201 at 150 kPa(a) top (1.1-1.5 bar(a)),
C-202 at about 150-170 kPa(a).

C-202's profile: water is the light key, so its concentration falls down the stripping
section; the draw, 5-20 plates above the bottom (SRC-2), is wetter than the bottoms below it,
which carry the acid back to C-201. The draw S32 is a tray liquid at its bubble point, 361.3 K
at 165 kPa(a), and the bottoms S31 362.5 K at 170 kPa(a) (thermo's vapour pressures, SRC-5).

## D-008 Heat and power: every energy flow (2026-11-19)

R-101's duty, 23.7 MW, is written by `cheme process propagate` on the elements basis from the
ideal-gas data (core ADR 0059); those data reproduce SRC-1's heats of reaction (materials.yaml
header). The heat raises LP steam at 450 kPa(a) (421 K saturation, inside SRC-1's 2.5-5 bar),
which the plant uses: the energy streams Q2 (T-101), Q7 (CO2 regenerator) and Q11 (C-202) leave
R101 with the script's duties, and propagate writes the rest, Q1 = 3.99 MW, to C-201's reboiler
(`energy_port: stm`). C-201 imports the remaining 6.18 MW (Q9). Every other duty comes from
`scripts/balance.py` (balance-output contract, library ADR 0027):

| stream | duty, kW | basis |
|---|---|---|
| Q1 | 3994.5 | propagate: R101's heat less Q2, Q7, Q11 |
| Q2 | 12844.9 | T-101: the acid vaporised into the cycle gas |
| Q3 | 1240.2 | E-101/E-102 feed/effluent: S8 to 423 K |
| Q4 | 1550.4 | E-102 trim cooler: effluent to 398 K |
| Q5 | 15326.3 | C-101's condenser |
| Q6 | 603.9 | C-102 with the scrub-acid cooler |
| Q7 | 1727.6 | regenerator, 2500 kJ per kg CO2 (ASSUMED) |
| Q8 | 1322.2 | regenerator condenser and lean cooler |
| Q9 | 6182.2 | imported steam, C-201's reboiler less Q1 |
| Q10 | 10385.7 | C-201's condenser, boil-up 2 mol/mol of the decanted overhead (ASSUMED) |
| Q11 | 5136.8 | C-202's reboiler |
| Q12 | 4425.9 | C-202's condenser, reflux 20 on its top product (ASSUMED) |
| Q13 | 806.9 | E-201 product cooler |
| P1 | 704.2 | K-101, isentropic efficiency 0.75, drive 0.95 (ASSUMED) |
| P2, P3 | 250, 180 | pumps, ASSUMED |

The enthalpy basis: liquids at constant heat capacities from 298.15 K, vapours through the
heat of vaporization at 298.15 K and the ideal-gas heat capacities (SRC-5; L-2). The heats of
vaporization are the differences of the liquid and ideal-gas formation enthalpies of one source
each (acetic acid 52.1, vinyl acetate 34.8, water 44.0 kJ/mol), so every vapour is the
ideal-gas monomer that R-101's duty and materials.yaml use and the plant's overall heat balance
is the one of its liquid feeds and products. The heat of vaporization to the real, associated
acid vapour (23.4 kJ/mol) is not mixed with the monomer's formation enthalpy: it would release
28 kJ per mol of acid consumed that the plant does not release (2.3 MW). The association itself
is left out (L-2): it would lower T-101's and C-101's duties somewhat, not the overall balance.

The script derives every temperature the flowsheet does not state as a design choice: the
outlets of the adiabatic mixers (S3 335.6 K, S8 405.0 K, S24 323.1 K, S25 364.1 K, S29 310.4 K,
S34 312.4 K), C-104's liquor S37 (322.9 K) and the compressor's discharge S2 (339.2 K); the
flowsheet takes them from the script, and the duties downstream use them. Per kg of product:
1.20 kWh of LP steam used (0.95 from R-101), 0.247 kWh imported, 1.38 kWh to cooling water,
0.045 kWh of electricity.

## D-009 Hazards (2026-11-19)

- **Oxygen and flammability.** The reactor feed holds 8.6 mol% oxygen in ethylene at 1000
  kPa(a) and 423 K; the mixing nozzle, the feed superheater and R-101's inlet are where a
  flammable mixture can form. SRC-3 names the excess of ethylene and acetic acid as what keeps
  the mixture outside the explosive range; SRC-4 avoids the premixing altogether. For the next
  stage: the flammability limit of the actual feed at its temperature and pressure (no open
  value read here), oxygen analysers with trips on the feed (two out of three), oxygen-cleaned
  piping and a nitrogen purge on a trip.
- **Thermal.** R-101 releases 23.7 MW, about 40 % of it from the ethylene's combustion (SRC-1:
  about half); a loss of boiling water or of steam offtake lets the bed run away as the
  combustion speeds up. Core's thermal screening (`reactor-hazards`) needs kinetics, a bed
  model and its coolant; this entry has a conversion reactor, so no screening is run (L-3). For
  the next stage: kinetics from an open source, the hot-spot sensitivity to the coolant
  temperature, the boiling-water pressure control and the oxygen trip on high bed temperature.
- **Vinyl acetate.** Highly flammable (flash point -8 C, explosive limits 2.6-13.4 %, SRC-6),
  suspected carcinogen (H351), polymerises: stored inhibited and cool under nitrogen (the
  inhibitor not modelled). The CO2 vent and the effluent carry traces (D-006, D-007).

## D-010 Preliminary gate-to-gate LCI (2026-11-19)

`lca/lca.yaml` takes every exchange of the design case per kg of product (`cheme assess lca
--write`). In the Atlas LCI (`scripts/build_lci.py`), lca/mappings.yaml links ethylene to
ethylene-1, acetic acid to acetic-acid-1, oxygen to asu-1, the imported LP steam as heat (kWh)
and the wash water to deionised water; the shared lci/mappings.yaml links electricity (medium
voltage), cooling water (its screening proxy per kWh rejected) and the effluent (the wastewater
treatment proxy per kg). The Atlas gaps are the purge's thermal oxidation (no mapping for a
hydrocarbon vent gas) and the vent's acetic acid and vinyl acetate, template components at zero
without a biosphere identity. The core study (`cheme assess lca`, lca/gaps.csv) links no
background at all, so there every feed, utility and waste is listed as missing with the
activity it should connect to. The vented CO2 (0.0995 kg/kg) is the one characterised emission;
the vented ethylene and ethane have no GWP100 factor and are listed as uncharacterised. One
product, no allocation. The steam R-101 raises is used inside the plant and does not cross the
boundary (D-008), so the LCI holds only the net import.

Inputs not in the inventory, each declared in lca/lca.yaml:
- **The Pd/Au/potassium acetate catalyst** (about 28 m3, 1.5 wt% Pd and 1 wt% Au, SRC-1): its
  replacement and the precious metals lost on refining the spent catalyst are an input of the
  system (never cut, library docs/system-model.md), but no open source read here gives its life
  or its metal losses; an amount would be a guess. Not inventoried and not cut off: an open gap,
  to connect to primary palladium and gold with recovery from spent catalyst once a rate is
  sourced. The same holds for the potassium acetate the catalyst is replenished with in
  operation (no open rate read).
- **The carbonate's K2CO3 make-up** for the acid that reaches it (D-006: about 0.14 g of K2CO3
  per kg, leaving as potassium acetate with the bleed, with 0.12 g of acid) and **the
  inhibitor** of the product (ASSUMED order of 20 ppm by weight, not modelled): cut off with
  their amounts (`cutoff:`), each far below 1 % of the input mass.

## Method and dependency table

| value | from | changes when |
|---|---|---|
| feeds S1, S4, S7 and every other flow and composition | propagate: specs, R101, separators, tears | reactions.yaml, the splits, the targets |
| Q1 | propagate: R101's conversion duty | the reactor's streams or Q2, Q7, Q11 |
| Q2 to Q13, P1 to P3, the temperatures of S2, S3, S8, S24, S25, S29, S34 and S37 | scripts/balance.py | any stream (rerun the script after propagate) |
| LCA outputs | cheme assess lca --write | the flowsheet or lca.yaml |

## Core features used (core 1.12.0)

- `specs:` with four design specifications, a feed's flow and a splitter's fraction (ADR 0070)
- `recovery:` component separators on six steps (ADR 0070)
- `tears:` on three streams, converged with the specifications (ADR 0060)
- `reactor: conversion` with two reactions on one key, and its duty on the elements basis
  through `energy_port` with the other energy streams of the step counted as work (ADR 0059)
- `ideal_gas` data for every component

## Core limits hit (each a candidate core issue)

- **L-1** No column model for a continuous distillation: C-101, C-201 and C-202 are component
  splits, their duties hand-estimated from ASSUMED boil-ups in the script. A shortcut column
  (Fenske-Underwood-Gilliland with an activity model) would derive both.
- **L-2** No property package covers vinyl acetate, water and acetic acid liquids or the cycle
  gas with acetic acid (association in the vapour, the heteroazeotrope, the decanter's liquid-liquid split):
  the liquid and phase-change duties stay outside core; the acetic acid is an ideal-gas monomer
  in R-101's duty and in the script, whose heats of vaporization are taken to that monomer
  (D-008). The splits that need phase equilibria (C-101's aqueous phase, C-102's and C-104's
  acid, C-202's bubble points) rest on checks with thermo outside core (D-005 to D-007).
- **L-3** No thermal screening for a continuous cooled fixed bed without kinetics:
  `reactor-hazards` needs a rate law and a bed; a conversion reactor gives neither.
- **L-4** Temperatures of mixers and compressors are not derived by propagate (no energy
  balance on a mixer, no compressor model): the script solves the six mixers' outlets
  adiabatically and the compressor's discharge, and the flowsheet takes these temperatures
  from it (D-008).
- **L-5** A splitter's outlet at another temperature than its inlet (X201's scrub acid at
  313 K) has no cooler of its own: E-202's duty is counted in C-102's.

## Open inputs

- Kinetics of the Pd/Au catalyst from an open source, for a bed model and the thermal screening;
  its life, precious-metal losses and potassium acetate make-up for the LCI (D-010).
- The flammability limit of the reactor feed at 1000 kPa(a) and 423 K.
- An ethylene recovery on the purge and a VAM stripper on the effluent (D-006, D-007).
- By-products (ethyl acetate, acetaldehyde, heavies) and their removal columns.
