# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Methylmagnesium bromide (MeMgBr), sold as a 35 wt% solution in 2-MeTHF, by the semi-batch
Grignard reaction of magnesium with methyl bromide gas, issue ChemE-as-Code/process-library#157,
the library's third semi-batch entry after n-bromosuccinimide-1 (#140) and
phosphorus-tribromide-1 (#134, open PR #379), whose pattern it follows (library ADR 0035, D-013).
Concept stage: design basis, batch recipe with the reactor's vessel and jacket, balanced BFD/PFD,
thermal screening of the initiation and the accumulation, and a preliminary gate-to-gate LCI.
Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at 1ff21eeb (pinned to cheme-as-code 1.7.0); this
entry is built and checked with **core main 7334d7c** (to be released as 1.8.0), because it uses
the gas vent and gas dosing of core ADR 0054 and the recipe units and filtration time of core
ADR 0057 ("Core features used" below). The route and its sources were scouted for core#158 on
2026-11-05.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session, or in the route scouting of the same day where said.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Albemarle Corporation, Technical Data Sheet, Methylmagnesium Bromide, typ. 35 % solution in 2-Methyl-THF (typ. 3.2 M), product number 10000303, date of issue 2025-02-24, https://www.albemarle.com/sites/default/files/2026-01/_TDS_00000191_TDS_ALB_E.PDF | pp. 1-3: specification 34.0-36.0 % MeMgBr, assay as total base by acidimetric titration after hydrolysis; dark brown liquid, crystallises below -10 C; density about 1.1 g/cm3 at 25 C; boiling point and flash point of the solvent 78 C and -10 C; handle under nitrogen or argon, never with water, acids or oxidisers; UN 3399, class 4.3 PG I; steel bottles of 125-2500 L filled to at most 90 %, drums of 30 and 200 L | read in full (PDF text); vendor document, facts only | D-001, D-002, D-006, D-011 |
| SRC-2 | NIST Chemistry WebBook, Methylmagnesium bromide, CAS 75-16-1 (C75161), reaction thermochemistry, https://webbook.nist.gov/cgi/cbook.cgi?ID=C75161&Mask=8 | Mg(cr) + CH3Br(l) -> CH3MgBr (solution, diethyl ether), -267.8 +/- 4.4 kJ/mol, and HBr(g) + CH3MgBr -> CH4 + MgBr2 (solution), -274.5 +/- 2.2 kJ/mol, both Holm (1981), J. Chem. Soc. Perkin Trans. 2, 464 (the WebBook notes possible side reactions in the first) | read; US government data | D-005 |
| SRC-3 | PubChem CID 6349, Methylmagnesium bromide, https://pubchem.ncbi.nlm.nih.gov/compound/6349 | identity (CH3BrMg, InChIKey NXPHGHWWQRMDIA-UHFFFAOYSA-M); HSDB Methods of Manufacturing: reaction of magnesium and methyl bromide | read (PUG REST and PUG View) | D-001, chemicals registry |
| SRC-4 | PubChem CID 6323 (bromomethane), 7301 (2-methyltetrahydrofuran), 5462224 (magnesium) | identities; HSDB densities: 2-MeTHF 0.853 g/cm3 at 20 C, magnesium 1.738 g/cm3 at 20 C; methyl bromide made from methanol and hydrogen bromide (Methods of Manufacturing, read by the scouting session) | read (PUG REST and PUG View) | D-006, D-012, chemicals registry |
| SRC-5 | Fraunhofer IMM, Scalable continuous Grignard reagent formation (flyer), https://www.imm.fraunhofer.de/content/dam/imm/de/documents/PDFs-neu2018/E-und-C/IMM-Scalable-Continuous-Grignard-Reagent-Formation.pdf | in batch the exothermic formation is dosing-controlled to remove the heat and often needs long reaction times; the Wurtz coupling is the main side reaction; the continuous packed-magnesium-bed process is demonstrated at pilot scale for PhMgBr, allyl-MgCl and EtMgBr in THF, not for MeMgBr | read by the scouting session (2026-11-05), the summary rechecked by search here | D-001, D-005 |
| SRC-6 | am Ende, D. J. et al. (1999) Org. Process Res. Dev. 3, 319, doi:10.1021/op9901801 | Grignard initiation monitored by in-situ FTIR: a small part of the halide charged and the initiation confirmed before the rest is dosed | abstract only (and a vendor note on it), no design numbers taken | D-004 (practice only) |
| SRC-7 | chemicals and thermo packages (the open data of core's environment: CRC Handbook tables, NIST WebBook / JANAF, DIPPR fits, estimates) | printed per component in process/materials.yaml: methyl bromide gas formation enthalpy -36.38 kJ/mol, S0 246.4 J/(mol K), heat of vaporisation 23.3 kJ/mol at 298 K and 23.5 at 293 K, normal boiling point 276.55 K, liquid density 1.663 g/cm3, liquid and ideal-gas heat capacities; 2-MeTHF liquid heat capacity 173.2 kJ/(kmol K) at 318 K; gas formation enthalpies of HBr, methane and ethane | open data packages | D-005, D-006, D-009 |
| SRC-8 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-9 | processes/asu-1, processes/iodine-1, processes/thf-1, processes/methanol-1, processes/hydrogen-bromide-1 (this library) | gaseous nitrogen and iodine to the battery limit (linked); THF, methanol and HBr (named as proxies, not linked) | library, internal | D-012 |

Not read and not cited as read: Ullmann's Encyclopedia (licensed; the HSDB entries cite it),
Organic Syntheses procedures (the scouting session was blocked by a browser check and did not get
round it), RSC React. Chem. Eng. 2023 d3re00191a and OPRD 2020, 24, 315 (abstract or snippet only).
Searched and not found openly (2026-11-05): kinetics or reaction calorimetry of the formation of
MeMgBr from methyl bromide gas, its induction time, the Wurtz selectivity of methyl bromide, a
TD24 of the solution, the solubility of methyl bromide in 2-MeTHF, a plant's specific
consumptions, and a market volume.

## Core features used (core main 7334d7c, to be 1.8.0)

- **`reactor: semibatch` with `dosing.profile`** (core ADR 0050): 5 % of the methyl bromide in 15
  min, a segment of share 0 for the 30 min initiation hold, then 95 % over 5 h.
- **`dosing.absorbed: 0.99` and `batch.vent: {stream: S7, components: [C2H6]}`** (core ADR 0054):
  the 1 % of the gas that passes through the liquid and the ethane of the Wurtz coupling leave by
  the vent as a second outlet of R101; propagate writes both outlets, the screening leaves the
  vented gas out of the MTSR and the MTT, `process recipe` gives the vent's peak (3.0 m3/h) and
  what a batch gives off (18.3 kg). Methyl bromide's `ideal_gas` data let the passing gas be
  warmed to the vessel's temperature.
- **A solid reactant in the liquid semi-batch**: magnesium is `phase: solid` with a
  `liquid_molar_volume` (its own volume in the slurry) and a heat capacity; the rate law uses its
  pseudo-concentration. It ran without a change to core (the scouting had flagged it as
  untested).
- **`hazard.mtt`** (core ADR 0050): the solvent's boiling point instead of the default.
- **Recipe `units: [M101, R101]`** (core ADR 0057): one vessel, R-101, over the charge mixer and
  the semi-batch; the vessel is sized from R101's model (core ADR 0052).
- **A `heat` operation with `temperatures:`** (core ADR 0052): the warm-up time from the jacket.
- **`solid_separation.filtration:` and a recipe `filter` with `from: F101`** (core ADR 0057): the
  filtration time from Ruth's equation.
- Not needed here: the batch still and solvent swap (ADR 0055), the crystallizer's spectators
  (ADR 0056) and the dryer (ADR 0057): the product is sold as a solution, with no isolation.

## D-001 Route and boundary (2026-11-05)
Decision: Mg + CH3Br -> CH3MgBr in dry 2-MeTHF at 318 K under nitrogen (SRC-3), methyl bromide
dosed as a gas into magnesium turnings (semi-batch); the product is the solution, 35 wt% MeMgBr
(SRC-1), filtered from the excess magnesium; on a dedicated train (D-013). Boundary feeds:
magnesium turnings, liquefied methyl bromide, dry 2-MeTHF, iodine (per batch), nitrogen (per
batch), electricity, LP steam; returns: chilled brine; outputs: the solution to filling, the wet
magnesium cake to quench and hazardous-waste treatment, the off-gas to a thermal oxidiser.
Reason: the reaction of magnesium with methyl bromide is the manufacturing route (SRC-3), and
industrial Grignard formation is a dosing-controlled semi-batch (SRC-5). 2-MeTHF is the solvent of
the one product grade with a full open specification (SRC-1); MeMgBr is also sold in diethyl
ether, but no open specification of a THF grade was found, so the library's THF (thf-1) cannot be
used as the solvent on a sourced basis. Filling and the steel bottles are outside the boundary.
Rejected: continuous formation in a packed magnesium bed (SRC-5: pilot scale, not shown for
MeMgBr): a candidate variant `methylmagnesium-bromide-2`. Diethyl ether (boiling point 35 C,
below a practical reaction temperature with brine cooling, and no open specification read).
Liquefied methyl bromide dosed as a liquid: it would flash in the vessel at 318 K; dosing it as a
gas below the surface is what the task and the vent model describe, and it keeps the heat of
vaporisation out of the reactor (E-101 supplies it).
Links: asu-1 (nitrogen) and iodine-1 (iodine). No library process makes magnesium, methyl bromide
or 2-MeTHF (D-012).

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 5000 kg of solution per batch (ASSUMED), 7920 h/a (330 days of 24 h), 879.5 batches a
year from the recipe (D-003): 4398 t/a of solution, 1539 t/a of contained MeMgBr. Product 35.0
wt% MeMgBr, 0.47 wt% MgBr2 (from the Wurtz coupling), 0.03 wt% dissolved methyl bromide and 10
mg/kg magnesium fines in the model; the specification is 34.0-36.0 wt% by titration (SRC-1).
Reason: no open market or plant figure was found. A 6.3 m3 reactor is a common size of a
dedicated organometallics train; the capacity follows from it and the cycle. The LCI is per kg and
does not depend on the scale; the batch size does (D-003).
Open: the specification beyond the assay (MgBr2, Me2Mg from the Schlenk equilibrium, colour,
turbidity, iodide).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 5000 kg of filtered solution (stream S9); `process/recipe.yaml` has two
unit procedures:
- REACT on R-101 (`units: [M101, R101]`): nitrogen inerting 1 h, charging the magnesium 0.5 h and
  the 2-MeTHF with the iodine 0.5 h, warm-up from 298 to 318 K from the jacket (0.19 h), the
  dosing with its initiation hold (5.75 h) and the post-reaction to 0.999 conversion of the
  methyl bromide (0.063 h), both from R101's model, sampling and titration 0.5 h, pressing the
  slurry to F-101 0.5 h: 9.005 h;
- FILTER on F-101: receiving 0.5 h, filtration 0.93 h from Ruth's equation (D-007), blowing and
  discharging the cake 1 h: 2.43 h.
R-101 is the bottleneck: cycle 9.005 h, 879.5 batches in 7920 h; one batch takes 10.93 h. The
flowsheet's flows are the recipe's year averages, `per batch x 879.5 / 7920 h` (the arithmetic is
in each feed's `source`): per batch 387.3 kg magnesium, 1441.0 kg (15.18 kmol) methyl bromide and
3241.8 kg 2-MeTHF. `cheme process recipe` checks the basis (555.26 against 555.32 kg/h, no
`cheme.recipe-basis` finding).
Vessel: the recipe sizes R-101 from R101's model (core ADR 0052, fill 0.8 and H/D 1.2 ASSUMED):
4.56 m3 of slurry at the end of the dosing in a 6.3 m3 vessel (R10 preferred size), 72 % full, D
1.88 m. F-101 is not sized as a vessel: its plate area is given (D-007).
Reason: core ADR 0051 puts the batch basis in one place; the dosing time comes from the jacket
(D-010), the post-reaction, warm-up and filtration from models, so a change of the kinetics, the
jacket or the cake changes the cycle (D-011 shows by how much). The other durations are ASSUMED
concept values. There is no rinse between batches: the train is kept dry and inert (a Grignard
reagent reacts with water and air).

## D-004 Feeds, charge and dosing (2026-11-05)
Decision:
- Magnesium turnings, 1.05 mol per mol of methyl bromide dosed (ASSUMED: a small excess keeps
  the surface for the end of the dosing and limits the Wurtz coupling, SRC-5); modelled as pure
  Mg (oxide skin not modelled).
- Dry 2-MeTHF, the amount that gives 35.0 wt% MeMgBr in the filtered product; its water (below
  100 ppm, ASSUMED) and the methane it would give are not modelled.
- Iodine as the activator, 0.4 kg per batch (about 0.1 % of the magnesium, ASSUMED), an LCA
  consumable (D-012), not in the balance.
- Methyl bromide from a liquefied store at 293 K and 300 kPa(a), evaporated and warmed to 298 K in
  E-101 and dosed as a gas below the surface: 5 % in 15 min, a 30 min hold in which the
  initiation is confirmed (temperature rise, heat flow or in-situ IR, SRC-6 practice), then 95 %
  over 5 h (`dosing.profile`). 99 % of the dosed gas is taken up by the liquid
  (`dosing.absorbed: 0.99`, ASSUMED: no open solubility of methyl bromide in 2-MeTHF; a subsurface
  dip pipe and a reflux condenser keep the slip small); the rest passes to the vent.
Reason: the initiation charge followed by a hold is the established practice against a delayed
initiation (SRC-6); the size of the initiation charge is checked in D-011: 5 % uninitiated takes
the charge to 349.5 K, just below the boiling point of the solvent.

## D-005 Grignard reactor R-101: semi-batch model, kinetics and heats of reaction (2026-11-05)
Decision: R101 is `reactor: semibatch` (core ADRs 0050, 0054): the charge S3 (magnesium in
2-MeTHF at 318.15 K), the methyl bromide gas S5 dosed as in D-004, then the post-reaction to 0.999
conversion of the methyl bromide (`batch.target`), isothermal at 318.15 K (45 C, ASSUMED: warm
enough for a steady reaction, 33 K below the solvent's boiling point), at 120 kPa(a) under
nitrogen. Two reactions:
- GRIG, Mg + CH3Br -> CH3MgBr: -291.1 kJ/mol, Holm's -267.8 kJ/mol for liquid methyl bromide in
  diethyl ether (SRC-2) less the heat of vaporisation of methyl bromide at 298 K, 23.3 kJ/mol
  (SRC-7): the dosed gas's basis, as core ADR 0054 asks for a dissolving gas. The heat of solution
  in 2-MeTHF is taken as equal to that in diethyl ether (ASSUMED). Rate first order in dissolved
  methyl bromide and of order 2/3 in the magnesium's pseudo-concentration (the surface of the
  turnings shrinking with their mass), k = 0.02 (m3/kmol)^(2/3)/s at 318 K, Ea 40 kJ/mol,
  ASSUMED.
- WURTZ, CH3MgBr + CH3Br -> C2H6 + MgBr2: -283.2 kJ/mol, derived (my arithmetic) from Holm's two
  reactions (SRC-2) and the gas formation enthalpies of HBr, methane, methyl bromide and ethane
  (SRC-7), with gaseous methyl bromide and ethane; methane's heat of solution neglected. Rate first
  order in each reactant, k = 1e-4 m3/(kmol s) at 318 K, Ea 40 kJ/mol, ASSUMED so that about 1 %
  of the methyl bromide is coupled: 0.86 % of the extents, 1.7 % of the methyl bromide (two per
  ethane). The ethane leaves by the vent as it forms (`batch.vent`).
Result: GRIG 1.6527 and WURTZ 0.01425 kmol/h (year averages); yield 96.7 % on the methyl bromide
dosed (losses: 1.0 % passed to the vent, 1.7 % to ethane, 0.5 % with the cake, 0.1 % left
dissolved) and 92.1 % on the magnesium.
Reason: no open kinetics or calorimetry of this reaction were found (2026-11-05). The order 2/3
in magnesium makes the rate fall at the end as the excess runs low, which is why the
post-reaction is not instantaneous; it is a surface-area proxy, not a mechanism. Core has no
surface rate (particle size, specific area) and no induction period (L-1, L-4).
**The low accumulation of D-011 is a consequence of the assumed rate law** and must be confirmed
by reaction calorimetry with gas dosing and in-situ IR before basic engineering.

## D-006 Balance method and property data (2026-11-05)
Decision: cheme propagates every material step: the charge mixer M101, the vaporiser E101 (a
pass-through), the semi-batch R101 with its two outlets, and the specified filter F101. There is
no balance script. The liquid data are declared by hand in materials.yaml: densities from PubChem
(SRC-4) and thermo (SRC-7); MeMgBr's apparent molar volume, 0.0501 m3/kmol, is my arithmetic from
the TDS density, about 1.1 g/cm3 for 35 wt% in 2-MeTHF (SRC-1), with ideal mixing; MeMgBr's heat
capacity 95.9 kJ/(kmol K) by Kopp's rule (solid Mg plus liquid methyl bromide, ASSUMED); MgBr2
from the solid's density and heat capacity (ASSUMED as dissolved). The product's heat capacity is
then 1.66 kJ/(kg K), lower than the 1.9-2.0 an ether solution would have: conservative for the
adiabatic rise. The Schlenk equilibrium does not change the balance and is not modelled.
Reason: no property package of core covers an organomagnesium solution; core's semi-batch needs
only the liquid molar volumes and heat capacities.

## D-007 Filtration of the excess magnesium (2026-11-05)
Decision: F-101 is a closed pressure Nutsche with a 1 m2 sintered-metal plate under 2 bar of
nitrogen: `solid_separation` with 99.8 % of the magnesium to the cake and 1 kg of solution per kg
of magnesium in the cake (ASSUMED); filtration time from Ruth's equation (core ADR 0057) with a
specific cake resistance of 5e9 m/kg (coarse metal fines), a medium resistance of 1e10 1/m and a
viscosity of 2 mPa s (all ASSUMED): 0.93 h per batch. The cake (51.1 kg per batch: 25.6 kg of
magnesium and 25.6 kg of solution) is blown with nitrogen and
discharged wet into a quench drum; it is a waste (D-012).
Reason: the product is sold as a clear solution (SRC-1: no isolation); the excess magnesium must
be removed before filling. Settling and decanting would leave more liquor with the magnesium; a
filter is the conservative choice for the loss.
Rejected: keeping the excess magnesium in R-101 for the next batch (a magnesium heel): the usual
plant practice in some Grignard trains, but a recycle that propagate does not converge, and the
oxide and fines build up; an open variant for basic engineering.

## D-008 Product (2026-11-05)
Decision: the filtered solution is the product at 318 K to the filling tank, cooled there and
filled under nitrogen (outside the boundary); its assay is titrated in R-101 before the transfer,
and a correction with 2-MeTHF (not modelled) brings an off-spec batch back into 34.0-36.0 %.
Reason: SRC-1. The model's 35.0 wt% is the centre of the specification.

## D-009 Utilities and heat (2026-11-05)
Decision (year averages, by hand from the models; all ASSUMED where not stated):
- Q1, R-101 to chilled brine 263/268 K: 134.10 kW, the extents of GRIG and WURTZ times their heats
  of reaction (134.76 kW) less the warming of the dissolved dose from 298 to 318 K (0.66 kW). Over
  the dosing R-101 removes 241.6 kW at the peak (`cheme process recipe`).
- Q2, the charge's warm-up from 298 to 318 K on LP steam through the jacket's hot-water loop:
  4.27 kW ((359.99 x 2.011 + 43.013 x 1.024) kJ/(h K) x 20 K); losses and the vessel's own heat
  not counted.
- Q3, the methyl bromide vaporiser E-101 on LP steam: 11.12 kW, 1.6855 kmol/h x (23.53 MJ/kmol at
  293 K + 5 K of gas warming) (SRC-7).
- Electricity 5.3 kW: R-101's agitator 5 kW (P1), F-101 0.3 kW (P2).
Per kg of solution: chilled brine 0.241 kWh removed, LP steam 0.028 kWh, power 0.0095 kWh.
Reason: R101's model gives the heat release but core writes no energy stream for a batch (L-9);
E101 has no property package for the phase change. The refrigeration unit is outside the boundary
(an LCA gap, D-012).

## D-010 Heat removal sets the dosing time (2026-11-05)
Decision: R-101 has a half-pipe jacket, U 400 W/(m2 K) for a stirred stainless-steel vessel with
brine (ASSUMED), on chilled brine at 263.15 K and hot water at 353.15 K for the warm-up; the recipe
checks it (core ADR 0052): 11.3 m2 wetted at the charge removes 249.2 kW against the model's peak
241.6 kW at a 5 h main dosing: the jacket check passes. A shorter main dosing raises the peak
above what the jacket removes at the charge (`cheme.recipe-jacket`).
Reason: the heat release of 4.3 GJ per batch has to leave through the jacket; the 5 h dosing
was set by hand to the jacket's limit (L-10). Cooling water at 298 K would give only about 90 kW
at the charge and a 14 h dosing. Reflux cooling of the boiling solvent (the plant's usual
emergency and often normal heat sink) is not credited: core checks only a jacket or a coil.

## D-011 Thermal screening: initiation and accumulation (2026-11-05)
Result (`cheme process reactor-hazards`, core ADRs 0050 and 0054): adiabatic temperature rise of
the whole batch 548 K; largest accumulation of the dosed methyl bromide 0.615 %, at the end of the
dosing; MTSR at the worst moment 321.5 K, against an MTT of 351.15 K. The vented ethane is not
part of the MTSR or the MTT; the vent's peak gas rate is 8.3e-6 kmol/(s m3) at the end of the
dosing (with the vent blocked it pressurises R-101: not screened, L-6). No TD24 is known (none
estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
MTT: `hazard.mtt` 351.15 K, the boiling point of 2-MeTHF from the TDS (SRC-1; thermo gives 353.15
K), the liquor's solvent: R-101 runs at about atmospheric pressure with a reflux condenser
(ASSUMED). Without it the screening takes the lowest normal boiling point of the liquor's
components, methyl bromide's 276.55 K, 42 K below the process temperature (L-5).
Sensitivity of the rate (both rate constants divided, scratch copies, not in the files):

| case | max. accumulation | MTSR | MTSR - MTT | post-reaction | cycle | batches/a | peak duty | screening reading |
|---|---|---|---|---|---|---|---|---|
| base (ASSUMED k) | 0.615 % | 321.5 K | -29.6 K | 0.063 h | 9.00 h | 879.5 | 241.6 kW | MTSR < MTT: dosing-controlled |
| k/10 | 4.27 % | 341.5 K | -9.6 K | 1.23 h | 10.17 h | 778.5 | 237.3 kW | MTSR < MTT, small margin |
| k/100 (sluggish or delayed initiation) | 21.1 % | 433.9 K | +82.8 K | 15.64 h | 24.58 h | 322.2 | 203.7 kW | MTSR far above MTT: the solvent boils off and the vessel pressurises |
| initiation charge uninitiated (5 % only, k/10000) | 99.8 % of the 5 % | 349.5 K | -1.7 K | - | - | - | - | the initiation charge alone stays just below the MTT |
| whole dose uninitiated (k/10000, dosing not stopped) | 95.8 % | 843 K | +492 K | - | - | - | - | Stoessel class 5 territory: the classic Grignard runaway |

Interpretation: this step is the showcase of the screening's initiation-versus-accumulation
question. While the reaction runs at the dosing rate, the accumulated methyl bromide is below 1 %
and a cooling failure stays 30 K below the boiling point. If the initiation is slow or delayed
(k/100 stands for an induction period, which core cannot model, L-1), a fifth of the dose
accumulates and a cooling failure would heat the content 83 K above the boiling point of the
solvent; if dosing continued into a reactor that never initiated, nearly the whole adiabatic rise
is available. Each 1 % of accumulated methyl bromide adds about 5.5 K. Two design consequences
follow and stay open for the next stage: the initiation charge must not exceed about 5 % (an
uninitiated 5 % already takes the charge to 349.5 K), and the main dosing must be interlocked on
a positive initiation signal and stopped on low heat flow, high temperature, loss of brine or of
the agitator. Dissolved methyl bromide also lowers the liquor's boiling point, so the MTT is
optimistic for an accumulating batch. Open: calorimetry (heat of reaction in 2-MeTHF with gas
dosing, heat-flow profile, the induction time, TD24 of the solution and of the wet magnesium
cake), the relief of R-101 for the boiling-solvent case, the vent's pressure case. Screening
values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of the 35 wt% solution from the flowsheet's year
averages. Linked (`lca/mappings.yaml`): the nitrogen consumable to asu-1's gaseous nitrogen, the
iodine consumable to iodine-1, and the LP steam as heat (kWh). Every other background is a gap
with the activity it should connect to. Feeds without a library producer, with their cited
proxies recorded in `lca.yaml` and **not linked** (never map to a guess):
- magnesium: the primary metal by the Pidgeon (silicothermic) process, a background-database
  ingot plus turning;
- methyl bromide: made from methanol and HBr (SRC-4); the proxy is the stoichiometric inputs of
  methanol-1 and hydrogen-bromide-1 (0.337 kg and 0.852 kg per kg), a candidate continuous entry
  `methyl-bromide-1` (shared with #133);
- 2-MeTHF: made from furfural (a bio-based route); thf-1 is the library's nearest ether solvent
  and is named as the proxy, not linked, being another substance from another feedstock.
Per batch and not in the flowsheet (library ADR 0035, core ADR 0053): nitrogen 30 Nm3 (37.5 kg)
for inerting R-101, pressing the slurry and blowing the cake, and iodine 0.4 kg, both ASSUMED;
the nitrogen leaves through the oxidiser (no disposal exchange); the iodine ends as MgI2 in the
product (about 90 mg/kg, not in the balance: `cheme.lci-balance-unassessable`, info).
Wastes: the off-gas (ethane and methyl bromide, 3.65 g/kg) to a thermal oxidiser with a caustic
scrubber; methyl bromide is a controlled ozone-depleting substance, whose use as a feedstock is
exempt from the Montreal Protocol's production controls (scouting note from a summary of MOP-4;
to be confirmed against the Ozone Secretariat's text before relying on it), so its emission must
be destroyed, not vented. The wet magnesium cake (10.2 g/kg) to quench and hazardous-waste
treatment. Not counted: the 2-MeTHF vapour in the off-gas and the filter's nitrogen (core models
no solvent stripping by the gas, L-6), the methyl bromide store's losses (emission exclusions).
Per kg of solution: magnesium 0.0775 kg, methyl bromide 0.288 kg, 2-MeTHF 0.648 kg, nitrogen 7.5
g, iodine 0.08 g, electricity 0.0095 kWh, LP steam 0.028 kWh, brine 0.241 kWh removed, off-gas
3.65 g, cake 10.2 g.
KPIs (`benchmarks/inorganic-chemicals.yaml`): methyl bromide and magnesium per kg of solution,
both `no_open_reference`; the stoichiometric floors are 0.279 and 0.071 kg/kg.

## D-013 Dedicated train (2026-11-05)
Decision: R-101, E-101 and F-101 make only MeMgBr solution, batch after batch: 879.5 batches in
7920 h on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train cannot
be checked without the other products' campaigns. Organometallic reagents are often made on
multipurpose trains (several Grignard reagents in turn); this LCI is then a lower bound.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products (a
quench and solvent flush of the train), the idle time of a multipurpose train, shared tank farms,
the thermal oxidiser and the filling station.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with gas dosing and vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas | done in cheme, kinetics and gas uptake ASSUMED | D-004, D-005, D-011, `process reactors`, `reactor-hazards` |
| magnesium as a solid reactant | done in cheme (pseudo-concentration) | D-005, D-006 |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| vessel sizing, jacket check, warm-up time (R-101) | done in cheme, U and media ASSUMED | D-003, D-010, core ADR 0052 |
| filtration and its time (F-101) | specified split, Ruth time in cheme, cake data ASSUMED | D-007, core ADR 0057 |
| duties | by hand from the models | D-009 |
| per-batch exchanges (nitrogen, iodine) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Lessons for core (core limits hit; candidates for core issues)

- L-1: **no induction period or initiation model.** A delayed initiation can only be shown by a
  rate constant that is slow for the whole batch (k/100 in D-011), not by a rate that switches on
  after an induction time while the dosing goes on, and the dosing cannot be made conditional on
  the initiation (no control of the dosing, core ADR 0050). A `batch.induction: {time, factor}` or
  a time-dependent rate multiplier, and a screening scenario "dosing continues uninitiated for
  t", would show the real hazard of a Grignard step directly.
- L-2: **only the worst cooling-failure moment is reported.** The MTSR of the initiation charge
  (5 % dosed into the cold charge, then a hold) needed a second scratch run with only that dose.
  The MTSR profile over time in `process reactors --json` (it already has the accumulation's), or
  the screening at named moments (end of each dosing segment), would answer it in one run.
- L-3: **propagate writes the vented component into the liquid outlet** with a mole fraction of 0
  (`C2H6: 0.0`), so the liquid's template must list the gas, or validate reports
  `cheme.process-component`. A vented component that never stays in the liquid should be left out
  of the liquid outlet's composition.
- L-4: **a solid reactant works, as a pseudo-liquid.** Magnesium needs a `liquid_molar_volume`
  and `liquid_heat_capacity` and enters the rate law as a pseudo-concentration (order 2/3 here as
  a surface proxy); there is no surface-area rate (particle size, specific area, a shrinking
  particle), which a Grignard formation or any dissolving-metal step would need.
- L-5: **default MTT below the process temperature** (methyl bromide's 276.55 K in the liquid,
  dissolved 42 K above its boiling point; as phosphorus-tribromide-1 L-2 with bromine): fixed with
  `hazard.mtt`. A finding when the default MTT lies below the process temperature would point to
  it; the dissolved gas also lowers the liquor's boiling point, which the MTT does not follow.
- L-6: **the vent carries no solvent vapour and has no pressure.** At 318 K, 2-MeTHF has a vapour
  pressure of about 30 kPa, so the ethane and the passing methyl bromide strip solvent to the
  oxidiser; core models no stripping (core ADR 0054 limitation), so the LCI excludes it. There is
  no gas-solubility basis for `absorbed` (a fixed share stands for Henry's law and mass
  transfer), and the screening does not assess the pressure of a blocked vent (Stoessel's gas
  release criterion, an ADR 0054 follow-up).
- L-7: **heat of absorption.** A dissolving gas adds only its sensible heat; the heat of
  reaction is written on the gas basis (core ADR 0054), so the MTSR is conservative but the
  isothermal duty during the dosing leaves out the absorption of the unreacted gas (small here,
  0.6 % accumulated).
- L-8: **core main still reports version 1.7.0**, so `plant.yaml` cannot require the 1.8.0 that
  `batch.vent`, `dosing.absorbed`, recipe `units:` and `filtration:` need; a core pinned at 1.7.0
  (the library's CI) rejects these fields.
- L-9: **no energy stream from a batch model.** R101's isothermal heat removal is known to the
  model but `process propagate` does not write it onto the energy port, and `process reactors`
  reports its duty as `?` without ideal-gas data for every component; Q1 is copied by hand from
  the extents (D-009). Writing the year-average duty of an isothermal batch or semi-batch would
  remove the hand step.
- L-10: **the dosing time is found by hand against the jacket** (as phosphorus-tribromide-1 L-3):
  the jacket check compares the peak duty with the wetted area at the charge, there is no reflux
  cooling, and no solve for the shortest dosing the jacket allows.
- L-11: **a vaporiser has no duty model** without a property package: E101 is a pass-through and
  its latent heat is a hand calculation (D-009).
- L-12: **an LCA consumable cannot carry a composition or a balance exclusion** (as
  phosphorus-tribromide-1 L-6): the nitrogen and the iodine leave `cheme.lci-balance-unassessable`
  (info), and a nitrogen purge to the oxidiser has no way to say so other than leaving out the
  disposal (`cheme.lca-disposal`, info).
- L-13 (library, not core): the taxonomy has no organometallics family; `inorganic-chemicals` is
  the nearest (D-002).

## Open inputs
Kinetics, induction time and heat of reaction in 2-MeTHF with gas dosing (calorimetry, in-situ
IR); TD24 of the solution and of the wet magnesium cake; methyl bromide's solubility in 2-MeTHF
and the real slip to the vent; the Wurtz selectivity; R-101's cooling arrangement and U (D-010)
and its relief for the boiling-solvent case; the filter cake's resistance and liquor (D-007); a
magnesium heel as an alternative (D-007); the product specification beyond the assay; the
oxidiser and scrubber; a TEA (`operation.batch: {recipe: true}`).
