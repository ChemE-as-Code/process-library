# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
2-Ethylhexanol by propylene hydroformylation, aldol condensation and hydrogenation, issue
ChemE-as-Code/process-library#511, a continuous Tier 2 entry of the library. Concept stage:
design basis, balanced BFD/PFD solved by core, duties, equipment list and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-19): library `main` at c04ed69 with the core pin b97a833 (v1.13.0).
Core solves loops with design specifications and component separators (core ADR 0070)
together with tear streams (ADR 0060); this entry uses both, so the whole material balance is
calculated by `cheme process propagate` from the feeds' compositions, the reactions and the
specified splits. Templates: `vinyl-acetate-1` (a continuous loop with specifications and a
balance-output script) and `oxalyl-chloride-1` (structure, source register). Requires
cheme-as-code 1.13 (plant.yaml).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this work (Google Patents machine text, PubChem, ChEBI, the data packaged in `chemicals` and
`thermo`).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 4 684 750 A, G. Kessen, B. Cornils, W. Gick, E. Wiebus, J. Hibbel, H. Bach, W. Zgorzelski (Ruhrchemie AG), priority DE 3530839, 1985-08-29, granted 1987-08-04: Process for the production of 2-ethyl-hexanol, https://patents.google.com/patent/US4684750A/en | example: propene and an aqueous solution of about 400 mg Rh per litre with trisulfonated triphenylphosphine, 1 : 8.75 by volume per hour, 115-125 C, 50 bar CO/H2 1:1, about 30 min; crude 5.0 wt% isobutanal, 94.0 % n-butanal, 1.0 % higher boilers; n/iso column of 100 theoretical plates at 50-80 kPa, head 60-70 C, bottom 90-100 C, overhead 99.9 % isobutanal, bottoms 0.2 % isobutanal and 98.8 % n-butanal; aldolisation of 1000 parts bottoms with 10 parts 20 % NaOH at 130-150 C for about 3 min, phase separation at about 60 C, the aqueous phase (about 1-2 % NaOH) returned, the organic phase above 93 % 2-ethylhexenal; hydrogenation over about 60 % Cu on silica at 140-160 C and LHSV 0.4 in the gas phase (claimed 0.05-0.5 MPa), then over Ni (55-60 %) at 120-140 C, 2-2.5 MPa and 0.8-1.1 1/h in the liquid phase, conversion and selectivity above 99 % and virtually quantitative; three columns (light ends, pure product overhead, after-run); yield 97.74 % of theory on n-butanal. General ranges: aldolisation 80-170 C, 0.1-0.7 MPa, 0.2-5 min, 0.5-5 % NaOH | read (Google Patents); patent, facts only | D-001, D-004 to D-007, benchmark |
| SRC-2 | US 4 523 036 A, B. Cornils, J. Hibbel, B. Lieder, J. Much, V. Schmidt, E. Wiebus, W. Konkol (Ruhrchemie AG), priority DE 3234701, 1982-09-18, granted 1985-06-11: Process for the preparation of aldehydes, https://patents.google.com/patent/US4523036 | 125 C and 5000 kPa; Rh 50-800 ppm in the aqueous solution, 10-100 mol of the sulfonated phosphine per g-atom Rh, CO:H2 preferably 1:1; crude separated uncooled from the catalyst phase keeps much less dissolved propylene (about 0.4 kg per kg of crude) than cooled, and the dissolved olefin is stripped by synthesis gas in countercurrent and returned; the cycle gas recycled by a compressor, part vented; water added for the water lost; the reaction heat raises process steam or heats the aldehyde distillation; 10:1 aqueous to organic, 0.5-1.5 wt% high boilers | read (Google Patents); patent, facts only | D-004, D-009 |
| SRC-3 | US 4 148 830 A, R. L. Pruett, J. A. Smith (Union Carbide), priority 1975-03-07, granted 1979-04-10: Hydroformylation of olefins, https://patents.google.com/patent/US4148830A/en | homogeneous Rh with excess triphenylphosphine at 50-145 C, H2 + CO below about 450 psia, H2:CO 3:2 to 20:1, at least 2 (preferably 10) mol free phosphine per mol Rh; continuous examples (Ex. 12: 97 C, n/iso 9.1:1; Ex. 13: 110 C, 82 psig, the products flashed and vaporised off the catalyst solution, 720 h without rhodium loss; its stated n/iso 0.5:1 is inconsistent with the rest and not used) | read (Google Patents, first 100 000 characters); patent, facts only | D-001 (rejected alternative) |
| SRC-4 | PubChem (PUG REST) CIDs 7720, 6561, 263; ChEBI (OLS search) | formulas, InChIKeys and IUPAC names of 2-ethylhexan-1-ol, 2-methylpropanal, butan-1-ol; CHEBI:16011, 48943, 28885 | read | registry |
| SRC-5 | processes/propylene-pdh-1, hydrogen-1, chlor-alkali-1, acrylic-acid-1 (this library) | the feeds' grades: propylene taken at chemical grade with 0.5 mol% propane (as acrylic-acid-1); hydrogen 99.9 mol% with nitrogen at 2850 kPa(a); caustic soda 50 wt% | library, internal | D-003, D-010 |
| SRC-6 | The `chemicals` 1.5.2 and `thermo` 0.6.1 packages (core's environment, C. Bell, MIT) | formation enthalpies at 298.15 K, kJ/mol: gas propylene 20.37, propane -104.39, CO -110.525 (ATcT); liquid n-butanal -239.2, isobutanal -247.3, 2-ethylhexanol -432.8, n-butanol -327.3, isobutanol -334.7 (CRC; their gas values -204.8, -215.7, -365.3, -274.9, -283.8 give the heats of vaporization), 2-ethylhexenal -261.3 (NIST WebBook), water -285.825 (ATcT); butyl butyrate gas -524.9 (Yaws); critical constants and acentric factors (2-ethylhexenal Tc 636 K, omega 0.454; butyl butyrate 612.1 K, 0.4852) for the Pitzer heats of vaporization 49.63 and 48.39 kJ/mol; liquid heat capacities, kJ/(kmol K) (n-butanal 163.7 CRCSTD; water 75.4, n-butanol 218.5, isobutanol 229.5, 2-ethylhexanol 385 near 350 K, thermo's HEOS and Zabransky fits; NaOH liquid 87.5 at 350 K, WEBBOOK_SHOMATE; no measured value packaged for 2-ethylhexenal, butyl butyrate and isobutanal: thermo's Dadgostar-Shaw estimates at 350 K, 266.5 and 302.7, for the first two, and isobutanal at n-butanal's 163.7, ASSUMED, the Dadgostar-Shaw estimate giving both butanals the same value); NaOH formation enthalpy -416.88 kJ/mol (chemicals' liquid value Hfl, used for the dissolved caustic; NaOH reacts in no step, so it cancels); ideal-gas heat capacities (means over 298-450 K: HEOS fits, TRCIG, WEBBOOK_SHOMATE for NaOH 55.8, Joback); vapour pressures (Wagner-McGarry for the butanals and 2-ethylhexanol, Landolt for 2-ethylhexenal, Ambrose-Walton for butyl butyrate): the iso/n relative volatility 1.43 at 338 K, the bubble points of 2-ethylhexanol at 20, 30 and 60 kPa(a) and butyl butyrate's 397 K at 30 kPa(a); liquid propylene density 506 kg/m3 at 298 K (HEOS); n-butanal's liquid density 703 kg/m3 at 391 K and 5 MPa (DIPPR Perry 8E with COSTALD) | open-source packages queried 2026-11-19; single values, facts only, with their source; not open data (library ADR 0037); the underlying works (ATcT, CRC Handbook, NIST WebBook, Yaws, Zabransky et al., Landolt-Boernstein, Joback) were not read here | materials, reactions, scripts/balance.py, C-102's reflux |
| SRC-7 | Ullmann's Encyclopedia of Industrial Chemistry, "2-Ethylhexanol" and "Butanals"; Cornils and Kuntz's reviews of the Ruhrchemie/Rhone-Poulenc process | - | not read (licensed); known leads for the per-pass conversion, the gas composition, the rhodium losses and the by-products | route lead only |

## D-001 Route and boundary (2026-11-19)

Decided: the oxo route with the aqueous biphasic rhodium catalyst of Ruhrchemie (SRC-1, SRC-2):
CH2=CHCH3 + CO + H2 -> n-butanal (and isobutanal), with the aqueous Rh/TPPTS catalyst phase
decanted from the crude and returned to the reactor; the n/iso split in one 100-plate column;
aldol condensation of n-butanal with aqueous caustic to 2-ethyl-2-hexenal and water; its
hydrogenation in a gas-phase stage over copper and a liquid-phase stage over nickel; three
distillation columns. The boundary is the plant gate: propylene, synthesis gas, hydrogen and
caustic soda in, utilities from the site, the off-gas, light ends and heavies to the site's
fuel, the effluent to the site's treatment.

Rejected:
- **Low-pressure homogeneous Rh/triphenylphosphine oxo** (Union Carbide, SRC-3): the main
  alternative, with the products vaporised off the catalyst solution. It needs a gas-recycle or
  liquid-recycle evaporator to keep the rhodium in the plant, and its open patent gives no full
  train to 2-ethylhexanol; SRC-1 gives the whole chain from propylene to the alcohol with one
  set of conditions and the overall yield, which is what a library entry can be built and
  checked on. Recorded as the alternative.
- **Cobalt-catalysed high-pressure oxo** (the older process): no open source with process
  data was read here; it runs at much higher pressure with lower n/iso selectivity and a cobalt
  recovery step.
- **Aldol condensation and hydrogenation in one step** (a bifunctional catalyst) and the
  **Guerbet condensation of n-butanol**: not read in an open source with process data here; not
  the industrial route of the sources.
- **A separate n-butanol product** from the light ends and a second hydrogenation of the
  isobutanal to isobutanol: options of the next stage; here the light ends go to fuel and the
  isobutanal is sold as such (D-007, D-010).

## D-002 Capacity, product and operating hours (2026-11-19)

120 kt/a of 2-ethylhexanol in 8000 h (15 t/h), ASSUMED: a normalisation basis for the
inventory, of the order of a single oxo-alcohol train, not an owner figure. The product is
C-402's distillate cooled to 313 K: 99.98 wt% 2-ethylhexanol as the ASSUMED splits give it
(SRC-1 says "high purity" without a figure).

## D-003 Feeds (2026-11-19)

Propylene from the library's propylene-pdh-1, taken at chemical grade with 0.5 mol% propane as
acrylic-acid-1 takes it (SRC-5); pumped liquid at 5.2 MPa(a). Synthesis gas H2/CO about 1:1
(SRC-1, SRC-2), 2 % hydrogen-rich so that the hydrogen the propane formation takes does not
accumulate CO in the loop, with 1 mol% inerts (nitrogen standing for methane, CO2 and argon),
ASSUMED; no library process makes this grade (acetylene-1's synthesis gas is about 2:1 H2/CO),
so it is an LCI gap (D-010). Hydrogen 99.9 mol% from hydrogen-1 at its delivery pressure. Caustic
soda 50 wt% from chlor-alkali-1 (SRC-1 doses 20 wt%; the dilution in the recycled aqueous phase
makes the difference immaterial). Demineralised water replaces the water the crude takes out of
the catalyst phase. The feeds' flows are solved by core's design specifications (D-004 to
D-006).

## D-004 Hydroformylation, the oxo loop and the n/iso split (2026-11-19)

R-101 runs at 5 MPa(a) and 393 K (SRC-1: 50 bar, 115-125 C). It is a conversion reactor: per
pass 90.0 % of the inlet propylene goes to aldehydes, ASSUMED (no open source read gives the
per-pass conversion), split 94.0 : 5.0 between n- and isobutanal as in SRC-1's crude; 0.5 % of
the propylene is hydrogenated to propane, ASSUMED. A second conversion step of the same vessel
(R102) forms the heavies, 1.0 wt% of the crude as SRC-1 has it, as the Tishchenko ester of
n-butanal (butyl butyrate standing for the aldols, trimers and esters; process/materials.yaml).

The aqueous catalyst phase stays in R-101/V-101 (L-3); its water losses with the crude are
replaced (S4). The crude is separated uncooled (SRC-2) and its dissolved propylene and propane
are stripped by the fresh synthesis gas in C-101 (SRC-2) and returned. V-101 runs at 4950
kPa(a), below R-101 (5000); the crude pump P-101 lifts its liquid to C-101's head (5050 kPa(a),
the bottom at 5080, the synthesis gas fed at 5100), from where the strip gas flows on to
R-101. V-101 and C-101 have no duty: their outlets take the temperature that closes their
energy balance, 391 and 373 K (the aldehydes and water they evaporate into the gas, D-009). All
pressures ASSUMED. The splits are ASSUMED:

| step | split | why |
|---|---|---|
| V101 | to the gas: 20 % of the propylene and propane, 97-99 % of CO, hydrogen and inerts, 2-2.5 % of the aldehydes and water | SRC-2: much propylene stays dissolved in the uncooled crude |
| C101 | to the strip gas: 99.5 % of the propylene and propane, all CO, hydrogen and inerts, 1-1.5 % of the aldehydes and water | SRC-2's stripping column |
| X101 | 5 % of the cycle gas purged to the fuel gas | holds the inerts and propane (about 29 and 16 wt% of the cycle gas) |
| C102 | vent: the dissolved gases; overhead: 96.2 % of the isobutanal, 0.005 % of the n-butanal; decanter: all water | SRC-1: overhead 99.9 wt% isobutanal, bottoms 0.2 wt% isobutanal (both reproduced) |

Two design specifications hold the oxo section: the synthesis gas for 1.5 mol CO per mol
propylene in R-101's feed (ASSUMED, an excess of CO over the propylene converted) and the water
make-up for 1.0 wt% water in the stripped crude (ASSUMED). The rate specification sets the
propylene feed for the product. With these, 98.0 % of the propylene fed ends in the aldehydes;
the rest leaves with the purge and C-102's vent (propane formed and fed, propylene dissolved).

C-102 runs at 50-80 kPa(a) with 100 theoretical plates (SRC-1). The relative volatility of
isobutanal to n-butanal at 338 K is 1.43 (thermo's vapour pressures, SRC-6); Underwood's
minimum reflux for the propagated feed (5.1 mol% isobutanal of the aldehydes) and SRC-1's
overhead is 45.5; 100 plates are 2.7 times Fenske's minimum (about 37), so a reflux of
1.1 times the minimum, 50, is taken (ASSUMED, Gilliland's correlation puts such a column near
the minimum). Only the organic phase of the overhead is refluxed: the water is condensed once
and decanted (S16). The reboiler this gives, 5.2 MW, is covered by R-101's heat (D-009). The
column runs under vacuum: a liquid-ring pump (P-102) takes the vent to 150 kPa(a).

## D-005 Aldol condensation (2026-11-19)

As SRC-1: the n-butanal (C-102's bottoms) is mixed by a mixing pump with the recycled aqueous
caustic and the make-up, reacts in a mixing section at 413 K and 500 kPa(a) for about 3 min,
is cooled to 333 K and decanted. The aqueous phase holds 1.5 wt% NaOH (SRC-1: 1-2 wt%), a
design specification on the caustic make-up; 90 % of it returns, 10 % is purged (X201,
ASSUMED). The make-up this gives, 1.7 kg of NaOH per tonne of n-butanal, is near SRC-1's
example (10 parts of 20 % NaOH per 1000 parts, 2 kg per tonne), a check that the purge
carries the reaction water at the source's strength.

R201 converts 97.9 % of the n-butanal to 2-ethylhexenal and 0.4 % to heavies, ASSUMED so that
the plant's yield on the n-butanal fed to the aldolisation is SRC-1's 97.74 % of theory (the
model gives 97.73 %). The organic phase then holds 95.0 wt% 2-ethylhexenal (SRC-1: above 93 %),
1.9 % n-butanal, 1.7 % heavies, 1.3 % water (V201: 99 % of the water, all the NaOH, 1 % of the
n-butanal and 0.05 % of the 2-ethylhexenal to the aqueous phase, ASSUMED). The isobutanal left
in the n-butanal (0.2 wt%) is not condensed in the model (its cross-aldol is not modelled, L-4)
and is hydrogenated to isobutanol.

## D-006 Hydrogenation (2026-11-19)

As SRC-1, in two stages. The organic phase is vaporised into the hydrogen cycle gas (E-301) and
hydrogenated in the gas phase over copper at 423-433 K and 400 kPa(a) (R-301, inside SRC-1's
140-160 C and 0.05-0.5 MPa). A design specification holds 90 mol% hydrogen in its vapour feed
(ASSUMED): 2-ethylhexenal is then at 7.3 mol%, 29 kPa, below its vapour pressure at 423 K
(about 50 kPa, SRC-6), so the feed stays a vapour. The product is condensed (E-302), the gas
recycled by K-301 with 1 % purged (ASSUMED). The liquid is pumped to 2.3 MPa(a), takes the fresh
hydrogen and is finished over nickel in a trickle bed at 393-395 K (R-302, inside 120-140 C and
2-2.5 MPa); the excess hydrogen is let down into the first stage (V-302), so that all the fresh
hydrogen enters at the high-pressure stage. Each stage converts 99 % of the aldehydes entering
it (SRC-1: above 99 % and virtually quantitative, ASSUMED values); 2-ethylhexanal, the
intermediate, is not a component (L-4). Fresh hydrogen: 0.034 kg/kg, 1.05 times the
stoichiometric need of the aldehydes hydrogenated.

## D-007 Distillation and the by-products (2026-11-19)

Three columns as SRC-1: C-401 takes the water (decanted to the effluent) and the light ends
(n- and isobutanol, 0.05 % of the 2-ethylhexanol) overhead; C-402 takes the pure product
overhead at 20 kPa(a) (97 % of its 2-ethylhexanol per pass, the heavies 0.2 %); C-403 returns
the after-run (96 % of the 2-ethylhexanol, 5 % of the heavies) to C-402 and leaves the heavies
with 7 wt% 2-ethylhexanol. All splits ASSUMED. Butyl butyrate stands for the heavies: its own
boiling point (438 K) is below 2-ethylhexanol's, but its splits follow the heavies it stands
for, not its own volatility (L-4); so does C-403's bottoms temperature, 453 K (ASSUMED), above
butyl butyrate's own bubble point at 30 kPa(a) (397 K, SRC-6): the heavies cooled from 453 K
in Q16 are the real heavies, about 9 kW more than the pseudo-component from its bubble point.
C-401 refluxes its light ends; its water is condensed once and decanted. C-401 to C-403 run
under vacuum on liquid-ring pumps (P-401). The light ends (0.023 kg/kg) and the heavies
(0.018 kg/kg) go to the site's liquid fuel, the isobutanal (0.059 kg/kg, 99.9 wt%) is a
co-product.

## D-008 Hazards (2026-11-19)

Screening statements for the next stage, not a HAZOP:
- **Carbon monoxide** (toxic, flammable) at 5 MPa in R-101, V-101, C-101 and K-101, and in the
  off-gas: CO detection, closed vents to the fuel gas, no confined spaces without monitoring.
- **Hydrogen and propylene** (extremely flammable, wide limits): the oxo loop at 5 MPa and the
  hydrogenation at 0.4 and 2.3 MPa; hazardous-area classification, relief to a flare.
- **Reaction heat**: hydroformylation releases about 149 kJ/mol; of R-101's 8.7 MW, 5.2 MW go
  to C-102's reboiler through the cooling register and 3.5 MW to the trim cooler on cooling
  water. A loss of the column's duty is a loss of most of the reactor's cooling: the trim
  cooler must take R-101's whole heat then (its sizing is a next-stage item). The gas-phase
  hydrogenation releases 171.5 kJ/mol of 2-ethylhexenal in a cooled multitubular bed (4.9 MW of
  LP steam): a loss of the shell's water or of hydrogen dilution gives a hot spot; temperature
  trips on the bed. The aldol step is mildly exothermic (68.7 kJ/mol) and self-heating; its
  feed must not be preheated above SRC-1's 150 C.
- **Caustic soda** 50 wt% (corrosive) and the alkaline aldol purge.
- **2-Ethylhexenal and the butanals** are flammable liquids; the rhodium catalyst phase is kept
  in a closed loop (its losses are an open input, D-010).
No thermal screening by core applies: the reactors are continuous conversion steps without
kinetics (L-1).

## D-009 Heat and power: every energy flow (2026-11-19, revised 2026-11-20)

Every duty comes from `scripts/balance.py` (balance-output contract, library ADR 0027) on one
basis: formation enthalpies at 298.15 K (liquid for the organics and water, ideal gas for the
light gases), constant liquid and ideal-gas heat capacities and heats of vaporization at
298.15 K (SRC-6), so the reactors' duties hold their heats of reaction. The light gases are
gaseous in every stream, the dissolved ones too (L-2); only the liquid propylene feed S1 holds
its propylene and propane as liquids, which take up their heat of vaporization in M101 (so
S5's 309 K is notional; R-101's heat, S5 - S7, does not depend on it). Core writes no duty
here: the reactors' streams change phase (a gas fed to a liquid product, L-2) and no property
package covers the liquids. The script also gives the outlet temperatures of the adiabatic
mixers, of V-101 and C-101 (no duty, D-004) and of the compressors, and checks that every
step's energy balance closes within 1 kW with its energy streams; only the compressors' drive
losses and the pumps' work leave as heat (the streams do not carry them).

| stream | duty, kW | what |
|---|---|---|
| Q1 + Q17 | 5170.8 + 34.9 | R-101's heat (reactions, the feed warmed to 393 K) to C-102's whole reboiler through its cooling register (SRC-2) |
| Q18 | 3491.8 | the rest of R-101's heat to its trim cooler on cooling water |
| Q3 | 1171.9 | LP steam 300 kPa(a) raised in R-301 to R-302's feed heater (313 to 395 K, less the stage's small reaction heat) |
| Q4 | 3734.6 | R-301's surplus LP steam, exported (0.249 kWh/kg) |
| Q5 | 5310.2 | C-102's condenser at reflux 50 (D-004): the organic overhead boiled up at R + 1, the decanted water condensed once, the overhead and vent cooled to 313 K |
| Q6, Q7 | 52.1, 2524.9 | R-201's surplus heat and the aldol product cooled to 333 K |
| Q8 | 3252.4 | E-301 on MP steam: the organic phase vaporised into the cycle gas |
| Q9 | 4449.0 | E-302: the first stage's product condensed to 313 K |
| Q10, Q11 | 909.6, 388.9 | C-401 reboiler (MP steam), condenser at reflux 3 (ASSUMED) of the light ends, the decanted water condensed once |
| Q12, Q13, Q14 | 2922.1, 3303.0, 1182.7 | C-402 reboiler, condenser at reflux 1 (ASSUMED), product cooler |
| Q15, Q16 | 98.3, 120.0 | C-403 reboiler and condenser at reflux 1 (ASSUMED), the heavies cooled from 453 K (D-007) |
| P1, P2, P3 | 20.1, 250.2, 150.0 | K-101, K-301 (isentropic 0.75, drive 0.95), the pumps (ASSUMED allowance) |
| P6 | 2.7 | the crude pump P-101, 4950 to 5100 kPa(a) (efficiency 0.60, ASSUMED; the crude's density as n-butanal's, SRC-6) |
| P4, P5 | 17.1, 45.0 | the liquid-ring vacuum pumps: C-102's vent from its head (50 kPa(a)) to 150 kPa(a) at isentropic efficiency 0.40, and 15 kW per vacuum column (C-102, C-401 to C-403) for the air leaking in and the vapour it carries (ASSUMED) |

R-101's heat, 8.7 MW at 393 K, exceeds C-102's reboiler (5.2 MW, bottoms 368 K): the reboiler
takes no steam, and the surplus goes to cooling water. Raising steam from it, as SRC-2 names,
would give steam below about 150 kPa(a) at a reactor of 393 K, of little use on a generic
site; it is an option of the next stage, and cooling water is the conservative choice for the
inventory. Steam levels: MP 1500 kPa(a) (471 K) for E-301 and the reboilers of C-401 to C-403
(bottoms up to 453 K); R-301's shell raises LP steam at 300 kPa(a) (407 K), which serves
R-302's feed heater (to 395 K, a 12 K approach); the rest is exported. Per kg of
2-ethylhexanol: 0.479 kWh of MP steam imported, 0.249 kWh of LP steam exported, 1.39 kWh to
cooling water and 0.032 kWh of electricity.

## D-010 LCI and allocation (2026-11-19)

Preliminary gate-to-gate inventory from the design case (lca/lca.yaml). Mass allocation between
2-ethylhexanol and isobutanal (94.46 : 5.54), the two products of one hydroformylation; the
exported LP steam carries no burden and no credit (conservative, as phthalic-anhydride-1). In
the Atlas build: propylene to propylene-pdh-1, hydrogen to hydrogen-1, caustic soda to
chlor-alkali-1, the make-up water as deionised water, the MP steam as heat; electricity,
cooling water and the effluent through the shared proxies. Gaps: the synthesis gas (no library
producer of the 1:1 grade), the off-gas, the light ends and the heavies to the site's fuel.

Open inputs (not inventoried, not cut off): the rhodium lost from the catalyst phase (R-101
holds about 40 kg) and the TPPTS make-up, and the copper and nickel catalysts' replacement. No
open source read here gives their rates; a precious-metal catalyst is never cut off.

## Core features used and limits

Used: design specifications with component separators and tear streams (core ADRs 0060, 0070:
five specifications and six tears solved together), conversion steps, the balance-output
contract of library ADR 0027, `process build`, `assess lca`.

- **L-1** No kinetics or reactor model: the conversions are specifications (D-004 to D-006),
  so neither the n/iso selectivity of the Rh/TPPTS catalyst nor the hydrogenation's approach
  to completion is predicted; no thermal screening applies to continuous conversion steps.
- **L-2** No property package of core covers the aldehyde, alcohol and water liquids, the
  caustic or the oxo gas at 5 MPa; the duties come from scripts/balance.py on constant heat
  capacities, and core's conversion-step duty does not apply where a component is fed as a gas
  and leaves as a liquid. The dissolved gases' heat of solution, the caustic's heat of
  dilution and the gases' solubility (the V101 and C101 splits) are not modelled.
- **L-3** The aqueous catalyst phase is not a stream: core has no circulating catalyst
  inventory with its water balance, so R-101/V-101 hold it internally and only its make-up
  water is a feed.
- **L-4** By-products are lumped: butyl butyrate stands for all heavies (with ASSUMED splits
  and C-403's bottoms temperature that do not follow its own boiling point), 2-ethylhexanal, the cross-aldol of isobutanal,
  sodium butyrate from the Cannizzaro reaction and the acetals are not modelled.
- **L-5** The columns are component splits, not stage-by-stage models: C-102's reflux comes
  from Underwood's minimum and a factor, not from a rigorous 100-plate column (a DWSIM check
  with `cheme process simulate` is a next-stage item).
