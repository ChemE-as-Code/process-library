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
entry was built with core main 7334d7c and rechecked on the release **1.8.0** (4e8fd80), which
the library now pins, because it uses
the gas vent and gas dosing of core ADR 0054 and the recipe units and filtration time of core
ADR 0057 ("Core features used" below). The route and its sources were scouted for core#158 on
2026-11-05.
Moved to core **1.9.0** (314642c) on 2026-11-06 with the library's pin (branch ci/core-1.9.0).
The entry uses three of its features ("Core features used" below): R101's model writes Q1
(`energy_port`, core ADR 0059, D-009), the default MTT at R-101's pressure replaces the hand-set
`hazard.mtt` (ADR 0058; 351.15 to 356.3 K, D-011), and the gas release at the MTSR is compared
with a stated vent capacity (ADR 0058, D-011); `plant.yaml` requires `cheme-as-code>=1.9`. The
balance, the recipe and the LCI amounts do not change (Q1 stays 134.1 kW); Q1 becomes
`calculated`, so its pedigree in the LCA dataset goes from [4,4,1,3,3] to [3,4,1,3,3] and the
data-quality rating changes (P 3.8 to 3.7, DQR 2.7 to 2.675).
Rechecked on core **1.12.0** (0e85885, the library's pin) on 2026-11-19 for the design findings
of process-library#427 (the vent, the relief and the heating medium, D-010 and D-011): the
balance, the recipe, the MTSR and the MTT do not change; the new screening of core ADRs 0069 and
0071 (the largest gas release over the batch, the dissolved gases a cooling failure releases,
the consecutive-reaction network, the bubble-point MTT, the boil-up of a content boiling at the
MTSR) decides the relief basis and the initiation and heating conditions in D-014. No file of
the model changed for it: the boil-up needs the vent's vapour, which ran on scratch copies only.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session, or in the route scouting of the same day where said.

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | Albemarle Corporation, Technical Data Sheet, Methylmagnesium Bromide, typ. 35 % solution in 2-Methyl-THF (typ. 3.2 M), product number 10000303, date of issue 2025-02-24, https://www.albemarle.com/sites/default/files/2026-01/_TDS_00000191_TDS_ALB_E.PDF | pp. 1-3: specification 34.0-36.0 % MeMgBr, assay as total base by acidimetric titration after hydrolysis; dark brown liquid, crystallises below -10 C; density about 1.1 g/cm3 at 25 C; boiling point and flash point of the solvent 78 C and -10 C; handle under nitrogen or argon, never with water, acids or oxidisers; UN 3399, class 4.3 PG I; steel bottles of 125-2500 L filled to at most 90 %, drums of 30 and 200 L | read in full (PDF text); vendor document, facts only | D-001, D-002, D-006, D-011 |
| SRC-2 | NIST Chemistry WebBook, Methylmagnesium bromide, CAS 75-16-1 (C75161), reaction thermochemistry, https://webbook.nist.gov/cgi/cbook.cgi?ID=C75161&Mask=8 | Mg(cr) + CH3Br(l) -> CH3MgBr (solution, diethyl ether), -267.8 +/- 4.4 kJ/mol, and HBr(g) + CH3MgBr -> CH4 + MgBr2 (solution), -274.5 +/- 2.2 kJ/mol, both Holm (1981), J. Chem. Soc. Perkin Trans. 2, 464 (the WebBook notes possible side reactions in the first) | read; US government data | D-005 |
| SRC-3 | PubChem CID 6349, Methylmagnesium bromide, https://pubchem.ncbi.nlm.nih.gov/compound/6349 | identity (CH3BrMg, InChIKey NXPHGHWWQRMDIA-UHFFFAOYSA-M); HSDB Methods of Manufacturing: reaction of magnesium and methyl bromide | read (PUG REST and PUG View) | D-001, chemicals registry |
| SRC-4 | PubChem CID 6323 (bromomethane), 7301 (2-methyltetrahydrofuran), 5462224 (magnesium) | identities; HSDB densities: 2-MeTHF 0.853 g/cm3 at 20 C, magnesium 1.738 g/cm3 at 20 C; methyl bromide made from methanol and hydrogen bromide (Methods of Manufacturing, read by the scouting session); methyl bromide's safety: GHS classification (H331 toxic if inhaled, H330 fatal if inhaled in a part of the notifications, flammable gas) and the NIOSH IDLH of 250 ppm (PUG View headings "GHS Classification" and "Immediately Dangerous to Life or Health (IDLH)", read 2026-11-05) | read (PUG REST and PUG View) | D-006, D-011, D-012, chemicals registry |
| SRC-5 | Fraunhofer IMM, Scalable continuous Grignard reagent formation (flyer), https://www.imm.fraunhofer.de/content/dam/imm/de/documents/PDFs-neu2018/E-und-C/IMM-Scalable-Continuous-Grignard-Reagent-Formation.pdf | in batch the exothermic formation is dosing-controlled to remove the heat and often needs long reaction times; the Wurtz coupling is the main side reaction; the continuous packed-magnesium-bed process is demonstrated at pilot scale for PhMgBr, allyl-MgCl and EtMgBr in THF, not for MeMgBr | read by the scouting session (2026-11-05), the summary rechecked by search here | D-001, D-005 |
| SRC-6 | am Ende, D. J. et al. (1999) Org. Process Res. Dev. 3, 319, doi:10.1021/op9901801 | Grignard initiation monitored by in-situ FTIR: a small part of the halide charged and the initiation confirmed before the rest is dosed | abstract only (and a vendor note on it), no design numbers taken | D-004 (practice only) |
| SRC-7 | chemicals 1.5.2 and thermo 0.6.1 packages of core's environment (open-source, MIT; the versions core pins): the gas formation data from their CRC, NIST WebBook / JANAF and ATcT tables; methyl bromide's heat of vaporisation and liquid density from thermo's default method for it, DIPPR_PERRY_8E, a correlation whose coefficients thermo takes from Perry's Chemical Engineers' Handbook, 8th ed. (a licensed book, itself drawing on the DIPPR 801 database; not read here); the liquid heat capacities from thermo's Dadgostar-Shaw estimate; methyl bromide's ideal-gas heat capacity (43.2 kJ/(kmol K) at 308 K) from thermo's default TRCIG correlation, whose coefficients come from the TRC compilation thermo cites (Thermodynamics of Organic Compounds in the Gas State; not read here; a single fact with this source, library ADR 0037); the rest from the packages' estimation methods | printed per component in process/materials.yaml: methyl bromide gas formation enthalpy -36.38 kJ/mol, S0 246.4 J/(mol K), heat of vaporisation 23.3 kJ/mol at 298 K and 23.5 at 293 K, normal boiling point 276.55 K, liquid density 1.663 g/cm3, liquid and ideal-gas heat capacities; 2-MeTHF liquid heat capacity 173.2 kJ/(kmol K) at 318 K; gas formation enthalpies of HBr, methane and ethane | open-source packages queried; single values only, facts only. The three DIPPR_PERRY_8E values (23.3 and 23.5 kJ/mol, 1.663 g/cm3) are not open data; they are used as single facts with this source, as the maintainer decided for values computed from packaged coefficients (library ADR 0037, 2026-11-06), with no coefficients copied; open alternatives for the same values are the NIST WebBook (SRD 69) and PubChem (HSDB) | D-005, D-006, D-009 |
| SRC-8 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-9 | processes/asu-1, processes/iodine-1, processes/thf-1, processes/methanol-1, processes/hydrogen-bromide-1 (this library) | gaseous nitrogen and iodine to the battery limit (linked); THF, methanol and HBr (named as proxies, not linked) | library, internal | D-012 |
| SRC-10 | NIST Chemistry WebBook, 2-Methyltetrahydrofuran (C96479), phase change data, https://webbook.nist.gov/cgi/cbook.cgi?ID=C96479&Mask=4 | enthalpy of vaporization 34.0 kJ/mol from vapour pressures of 283 to 353 K (Stephenson and Malanowski 1987), and 33.7 kJ/mol (Moiseev and Antonova 1970); boiling point 352 +/- 10 K (average of 6 values) | read 2026-11-06; US government data | D-011 (the MTT at 120 kPa(a)) |
| SRC-10a | the same page (C96479, phase change data), fusion | triple/fusion point Tfus 137.05 K (Boord, Greenlee et al. 1949, uncertainty 0.4 K assigned by TRC); the page has no Antoine parameters for 2-MeTHF | read 2026-11-19; US government data | D-014 (the vent condenser cannot freeze) |
| SRC-12 | NIST Chemistry WebBook, Bromomethane (C74839), phase change data, https://webbook.nist.gov/cgi/cbook.cgi?ID=C74839&Mask=4 | Antoine parameters log10(P/bar) = 4.26874 - 1069.708/(T/K - 25.771), 203 to 276.8 K (coefficients calculated by NIST from Beersmans and Jungers 1947); triple point 179.47 K (Egan and Kemp 1938); boiling point 276.6 K (Majer and Svoboda 1985 and others) | read 2026-11-19; US government data | D-014 (methyl bromide stripped on a cooling failure, scratch copies only; the vent condenser) |
| SRC-11 | Montreal Protocol on Substances that Deplete the Ozone Layer, Article 1 (Definitions), UNEP Ozone Secretariat, https://ozone.unep.org/treaties/montreal-protocol/articles/article-1-definitions | paragraph 5: production is the amount produced minus the amount destroyed and minus the amount entirely used as feedstock in the manufacture of other chemicals | read (2026-11-06); treaty text, facts only | D-012 |

Not read and not cited as read: Ullmann's Encyclopedia (licensed; the HSDB entries cite it),
Organic Syntheses procedures (the scouting session was blocked by a browser check and did not get
round it), RSC React. Chem. Eng. 2023 d3re00191a and OPRD 2020, 24, 315 (abstract or snippet only).
Searched and not found openly (2026-11-05): kinetics or reaction calorimetry of the formation of
MeMgBr from methyl bromide gas, its induction time, the Wurtz selectivity of methyl bromide, a
TD24 of the solution, the solubility of methyl bromide in 2-MeTHF, a plant's specific
consumptions, and a market volume.

## Core features used (core 1.9.0)

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
- **The default MTT of what boils, at the vessel's pressure** (core 1.9.0, ADR 0058): the dosed
  methyl bromide (a dose with `absorbed`) and the vented ethane are left out, and 2-MeTHF's
  boiling point at R-101's 120 kPa(a) comes by Clausius-Clapeyron from its declared
  `heat_of_vaporization` (34.0 kJ/mol, NIST WebBook, SRC-10): 356.3 K. It replaces the
  `hazard.mtt` of 1.8.0 (D-011, L-5).
- **`hazard.vent_capacity`, the gas release at the MTSR and the MTSR profile** (core 1.9.0, ADR
  0058, rule `cheme.reactor-hazard-vent`): R-101's vent, 20 m3/h ASSUMED, against the ethane a
  cooling failure forms at the MTSR (D-011).
- **`energy_port: q` on R101** (core 1.9.0, ADR 0059): `propagate --fill` writes the
  semi-batch's year-average duty on Q1 (calculated), in place of the hand value (D-009, L-9).
- **Recipe `units: [M101, R101]`** (core ADR 0057): one vessel, R-101, over the charge mixer and
  the semi-batch; the vessel is sized from R101's model (core ADR 0052).
- **A `heat` operation with `temperatures:`** (core ADR 0052): the warm-up time from the jacket.
- **`solid_separation.filtration:` and a recipe `filter` with `from: F101`** (core ADR 0057): the
  filtration time from Ruth's equation.
- Not needed here: the batch still and solvent swap (ADR 0055), the crystallizer's spectators
  (ADR 0056) and the dryer (ADR 0057): the product is sold as a solution, with no isolation; the
  recycle tears of core 1.9.0 (ADR 0060): the flowsheet has no recycle (a magnesium heel, D-007,
  would be one).
- `hazard.reactions` (ADR 0058) is not used: the default counts every reaction and takes the
  largest, GRIG (MTSR 321.5 K); the Wurtz coupling alone reaches 321.4 K at its worst moment
  (D-011), so naming the reactions would change nothing.
- **Core 1.12.0's screening (ADRs 0069 and 0071), read without a change to the files (D-014):**
  the largest gas release over the batch and the methyl bromide held in the liquid
  (`dissolved_release`, rule `cheme.reactor-hazard-dissolved`) on the entry as it is; the
  consecutive pair GRIG-WURTZ (`network`, reported without `hazard.potential`); on scratch
  copies the bubble-point MTT (`hazard.mtt_from: bubble-point`, not adopted) and, with the
  vent's vapour declared, the boil-up of a content boiling at the MTSR (`gas_release.boil_up`),
  the relief basis. `hazard.potential: network`, the head space and inerts, the heat of
  absorption and the Henry degassing of ADR 0071 are not used (D-014 says why).

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
gas below the surface is the design basis of D-004 and what core's gas dosing and vent (core
ADR 0054) model, and it keeps the heat of
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
then 1.58 kJ/(kg K) (S9's composition, my arithmetic; the slurry S6 also 1.58: 4.37 GJ per batch
over 5052 kg x 1.58 kJ/(kg K) is the screening's 548 K, D-011), lower than the 1.9-2.0 an ether
solution would have: conservative for the adiabatic rise. The Schlenk equilibrium does not change the balance and is not modelled.
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
Hazard of the quench: the cake is killed with an alcohol and then water (lca.yaml). Each mol of
magnesium gives one mol of hydrogen (Mg + 2 ROH or 2 H2O -> Mg(OR)2 or Mg(OH)2 + H2): 25.6 kg of
magnesium is about 1.05 kmol, 2.1 kg or 24 Nm3 of hydrogen per batch (my arithmetic), with about
0.075 kmol of methane from the MeMgBr in the cake's liquor (9 kg), and the quench's heat. The
quench drum must be inerted with nitrogen and vented to a safe place (flammable gas, no air in
the head space), and the alcohol and water dosed against the gas rate; its sizing and the vent's
route are open inputs for basic engineering.
Reason: the product is sold as a clear solution (SRC-1: no isolation); the excess magnesium must
be removed before filling. Settling and decanting would leave more liquor with the magnesium; a
filter is the conservative choice for the loss.
Rejected: keeping the excess magnesium in R-101 for the next batch (a magnesium heel): the usual
plant practice in some Grignard trains, but the oxide and fines build up, and the heel's
behaviour (its activity, the initiation on a heel) has no open basis; an open variant for basic
engineering. Core 1.9.0 converges a recycle at a declared tear (ADR 0060), so the recycle itself
is no longer the obstacle it was on 1.8.0.

## D-008 Product (2026-11-05)
Decision: the filtered solution is the product at 318 K to the filling tank, cooled there and
filled under nitrogen (outside the boundary); its assay is titrated in R-101 before the transfer,
and a correction with 2-MeTHF (not modelled) brings an off-spec batch back into 34.0-36.0 %.
Reason: SRC-1. The model's 35.0 wt% is the centre of the specification.

## D-009 Utilities and heat (2026-11-05, Q1 from the model 2026-11-06)
Decision (year averages; Q1 from R101's model, the others by hand, all ASSUMED where not stated):
- Q1, R-101 to chilled brine 263/268 K: 134.1 kW, written by `cheme process propagate --fill`
  from R101's semi-batch model on the stream its `energy_port: q` names (core 1.9.0, ADR 0059,
  `calculated`): the reactions' heat 134.763 kW less the doses warmed to 318.15 K, 0.658 kW for
  the dissolved methyl bromide and 0.004 kW for the gas passing to the vent. Until 2026-11-05 it
  was typed by hand as 134.10 kW from the extents (134.76 less 0.66 kW); the model agrees and
  also counts the vented gas's warming, so the hand value was dropped. Over the dosing R-101
  removes 241.6 kW at the peak (`cheme process recipe`).
- Q2, the charge's warm-up from 298 to 318 K on LP steam through the jacket's hot-water loop:
  4.27 kW ((359.99 x 2.011 + 43.013 x 1.024) kJ/(h K) x 20 K); losses and the vessel's own heat
  not counted. It stays typed on its own stream: R101's model holds the batch at 318.15 K from
  the start and leaves the heat-up to the recipe's `heat` operation (core ADR 0059), so R101 has
  two heat streams, Q1 the model's and Q2 this one; both are in the LCI (brine and LP steam).
- Q3, the methyl bromide vaporiser E-101 on LP steam: 11.12 kW, 1.6855 kmol/h x (23.53 MJ/kmol at
  293 K + 5 K of gas warming) (SRC-7).
- Electricity 5.3 kW: R-101's agitator 5 kW (P1), F-101 0.3 kW (P2).
Per kg of solution: chilled brine 0.241 kWh removed, LP steam 0.028 kWh, power 0.0095 kWh.
Reason: R101's model gives the heat release and, since core 1.9.0, writes it (L-9 resolved);
the heat of absorption of the unreacted dissolved gas is still left out (L-7). E101 has no
property package for the phase change (L-11). The refrigeration unit is outside the boundary
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
Heating medium above the solvent's normal boiling point (the MTT if the pad is lost): the warm-up's hot water at 353.15 K (fed from LP steam at about
412 K) lies 2 K above the solvent's normal boiling point, 351.15 K, which is the MTT once R-101's
pressure falls to atmospheric (the nitrogen pad lost, the vent open to an atmospheric header),
and 3.2 K below the MTT at the pad's 120 kPa(a), 356.3 K (D-011, core 1.9.0); the hot-water
loop's steam at about 412 K is far above both. An uninitiated 5 % initiation charge already
reaches 349.5 K. A jacket left on hot water when the dosing starts, or a failed hot-water
temperature control, can take the content to the boiling solvent by itself, and with a starting
reaction both heats add. Kept here at 353.15 K, with two safeguards recorded as open (next to the
dosing interlocks of D-011): the heating isolated (steam to the hot-water loop shut, the jacket
switched to brine) is a permissive for the dosing, and a high-temperature trip of the hot-water
supply cuts the steam. The higher MTT at 120 kPa(a) does not lift them: it rests on the ASSUMED
pad pressure being held. Rejected for now: lowering the hot water to 343.15 K, below the normal
boiling point. It lengthens the warm-up from 0.19 to 0.25 h, the cycle to 9.06 h and the year to
873.9 batches (a scratch copy of `cheme process recipe`, not in the files), a choice for basic
engineering together with the interlocks.
Amended 2026-11-19 (core 1.12.0, D-014): the methyl bromide dissolved in an uninitiated
initiation charge (71.2 kg, core's `dissolved_release`) lowers the bubble point of R-101's
content to about 352.1 K at the pad's 120 kPa(a) and 346.8 K at atmospheric pressure (my
arithmetic, Raoult's law over 2-MeTHF and methyl bromide, D-014). The hot water at 353.15 K is
therefore above the content's bubble point **with the pad held** as soon as the first methyl
bromide is in, not only above the normal boiling point. Decision: the heating permissive applies
to the **initiation charge**, not only to the main dosing: no methyl bromide enters R-101 until
the steam to the hot-water loop is shut and the jacket's loop is at or below the process
temperature (318.15 K); the high-temperature trip of the hot-water supply stays. Recomputed on
core 1.12.0, the 343.15 K alternative still costs a warm-up of 0.249 h (was 0.19 h), a cycle of
9.062 h and 873.9 batches a year (scratch copy of `process recipe`), and would keep the medium
3.7 K below the 346.8 K, so it no longer depends on the pad or the permissive; it is
recommended, and left to the engineering review because it trades 0.6 % of the capacity
against an instrumented permissive whose reliability is not known here (no SIL or frequency
is claimed). Applying it changes the recipe, the flowsheet's year averages and the LCI.

## D-011 Thermal screening: initiation, accumulation and the vent (2026-11-05, core 1.9.0 2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054 and 0058): adiabatic temperature
rise of the whole batch 548 K; largest accumulation of the dosed methyl bromide 0.615 %, at the
end of the dosing; MTSR at the worst moment 321.5 K, against an MTT of 356.3 K. Each reaction
alone (`per_reaction`): GRIG dT_ad 548.0 K, MTSR 321.5 K; WURTZ alone gives dT_ad 0.0 K over the
batch (its reactants, MeMgBr and the dosed methyl bromide, are not in the initial charge) and an
MTSR of 321.4 K at its worst moment, a 3.3 K rise over T_p 318.1 K and below GRIG's 321.5 K, so
the default (the largest reaction) already counts the right one and `hazard.reactions` is not
needed. The MTSR
over the batch (`mtsr_profile`) rises from 318.9 K after the initiation to 321.5 K at the end of
the dosing: the worst moment is the end of the main dosing, not the initiation charge, at the
base rate. The vented ethane is not part of the MTSR or the MTT. No TD24 is known (none
estimated): no criticality class (`cheme.reactor-hazard-missing`, info).
MTT: core 1.9.0's default (ADR 0058), 356.3 K, the boiling point of 2-MeTHF at R-101's 120 kPa(a)
by Clausius-Clapeyron from its normal boiling point 351.15 K (the TDS, SRC-1; thermo gives 353.15
K) and its heat of vaporization, 34.0 kJ/mol (NIST WebBook, SRC-10; declared in materials.yaml).
The dosed methyl bromide is left out (a dosed gas, `mtt_left_out`) and the ethane (a vent
component). It replaces `hazard.mtt: 351.15` of 1.8.0, the solvent's normal boiling point, set
by hand because the 1.8.0 default was methyl bromide's 276.55 K (L-5, resolved). The value at the
vessel's pressure is the MTT of Stoessel's open reactor; it rests on the ASSUMED 120 kPa(a) pad
being held (the vent to the oxidiser at that pressure). At atmospheric pressure the solvent boils
at 351.15 K, 5.2 K lower, which D-010 keeps for the heating medium. thermo's
corresponding-states heats of vaporization, 29.5 to 30.8 kJ/mol at 351 K, would give 356.9 to
357.1 K; the sourced, larger value gives the lower MTT, the conservative one.
Vent and gas release (core 1.9.0, `hazard.vent_capacity`, rule `cheme.reactor-hazard-vent`):
R-101's vent runs through its reflux condenser to the thermal oxidiser's header and is sized
(ASSUMED) for the largest normal gas flow it takes, the nitrogen purge that inerts R-101 (three
volume changes of 6.3 m3, 18.9 Nm3 as in the LCI's nitrogen (D-012), in the 1 h inert step:
about 16 to 17.4 m3/h at 120 kPa(a) and 273 to 298 K), rounded up to 20 m3/h at 120 kPa(a). The normal peak of the off-gas, 3.0 m3/h at the end
of the dosing (`cheme process recipe`), is well inside it. With a cooling failure at the worst
moment, the Wurtz coupling at the MTSR forms ethane at 3.49e-5 kmol/s, 2.8 m3/h at 321.5 K and 120
kPa(a), 0.14 times the vent capacity (info); run to completion it would form 0.092 kmol (2.1
m3) per batch. The screening counts only the vent's components (the ethane), not the dissolved
methyl bromide a cooling failure drives out (core ADR 0058 limitation, L-6): at the base rate
about 9 kg, 0.093 kmol or 2.1 m3 at 321.5 K and 120 kPa(a); driven out within 15 min (ASSUMED) it
adds 8.3 m3/h, together with the ethane 11.1 m3/h, still within the 20 m3/h.
Sensitivity of the rate (both rate constants divided, scratch copies, not in the files; the
accumulation, MTSR, cycle and duty columns are those of 1.8.0, which core 1.9.0 reproduces; the
MTT and the gas release from core 1.9.0):

| case | max. accumulation | MTSR | MTSR - MTT | gas at the MTSR | post-reaction | cycle | batches/a | peak duty | screening reading |
|---|---|---|---|---|---|---|---|---|---|
| base (ASSUMED k) | 0.615 % | 321.5 K | -34.8 K | 2.8 m3/h | 0.063 h | 9.00 h | 879.5 | 241.6 kW | MTSR < MTT: dosing-controlled; gas within the vent |
| k/10 | 4.27 % | 341.5 K | -14.8 K | 4.8 m3/h | 1.23 h | 10.17 h | 778.5 | 237.3 kW | MTSR < MTT, small margin; gas within the vent |
| k/100 (sluggish or delayed initiation) | 21.1 % | 433.9 K | +77.6 K | 49.2 m3/h | 15.64 h | 24.58 h | 322.2 | 203.7 kW | MTSR far above MTT: the solvent boils off and the vessel pressurises; ethane alone 2.5 times the vent |
| initiation charge uninitiated (5 % only, k/10000) | 99.8 % of the 5 % | 349.5 K | -6.8 K | - | - | - | - | - | the initiation charge alone stays below the MTT (1.7 K below the normal boiling point); with its dissolved methyl bromide counted, 2.6 K below its content's bubble point at 120 kPa(a) and 2.7 K above it at atmospheric pressure (D-014) |
| whole dose uninitiated (k/10000, dosing not stopped) | 95.8 % | 843 K | +487 K | 48.3 m3/h | - | - | - | - | Stoessel class 5 territory: the classic Grignard runaway; ethane alone 2.4 times the vent |

The gas release of the k/100 and uninitiated cases takes the rate laws at the MTSR, far outside
their ASSUMED 298-338 K range: an order of magnitude, not a value.
Interpretation: this step is the showcase of the screening's initiation-versus-accumulation
question. While the reaction runs at the dosing rate, the accumulated methyl bromide is below 1 %
and a cooling failure stays 35 K below the boiling point. If the initiation is slow or delayed
(k/100 stands for an induction period, which core cannot model, L-1), a fifth of the dose
accumulates and a cooling failure would heat the content 78 K above the boiling point of the
solvent; if dosing continued into a reactor that never initiated, nearly the whole adiabatic rise
is available. Each 1 % of accumulated methyl bromide adds about 5.5 K. Two design consequences
follow and stay open for the next stage: the initiation charge must not exceed about 5 % (an
uninitiated 5 % already takes the charge to 349.5 K), and the main dosing must be interlocked on
a positive initiation signal and stopped on low heat flow, high temperature, loss of brine or of
the agitator. Dissolved methyl bromide also lowers the liquor's boiling point, so the MTT is
optimistic for an accumulating batch.
Design finding, the vent (2026-11-06): the vent passes the base case's gas release seven times
over, but not that of a sluggish or failed initiation: at k/100 the ethane alone is 49 m3/h, 2.5
times the 20 m3/h, before the boiling solvent and the methyl bromide it drives out (the larger
part, not screened). No credible process vent passes that case; it is not hidden by a larger
`vent_capacity`. It is met by not letting it arise and by a relief: (1) the dosing interlocks
above (a positive initiation signal before the main dosing, a dosing stop on low heat flow, high
temperature, loss of brine or of the agitator) keep the accumulation at the base case's level;
(2) R-101's emergency relief, separate from the process vent, is sized for the boiling-solvent
case with its methyl bromide and ethane (two-phase venting likely, a DIERS-type sizing) and
routed to a containment or the oxidiser, never to atmosphere. Both are open safeguards for basic
engineering, with the calorimetry that sets the real accumulation.
Rescreened on core 1.12.0 (2026-11-19, D-014): the relief basis is the boil-up of the k/100
case, about 3.9e3 m3/h of 2-MeTHF vapour with its 301 kg of methyl bromide, to a catch tank;
the uninitiated whole dose is excluded from the relief basis and prevented by the initiation
permissive; the vent's 20 m3/h holds for the base and k/10 cases with the solvent vapour.
Toxic gas release: what accumulates is dissolved methyl bromide, which boils at 276.55 K, 42 K
below the process temperature. A cooling failure with accumulated dose therefore first drives the
methyl bromide out of the liquor, before and with the solvent, through the vent or the relief.
Methyl bromide is acutely toxic by inhalation (GHS H331 toxic if inhaled, notified by some
suppliers as H330 fatal if inhaled; NIOSH IDLH 250 ppm, a potential occupational carcinogen;
SRC-4) and is also classed as a flammable gas. The amounts at the worst moment (my arithmetic,
accumulation x 1441 kg dosed per batch): about 9 kg at the base rate (0.615 %), 62 kg at k/10,
about 300 kg at k/100 (21.1 %), and about 72 kg for an uninitiated 5 % initiation charge (99.8 %
of 72 kg). The relief and vent case of R-101 is therefore not solvent vapour only: it must be
sized for methyl bromide plus 2-MeTHF and routed to a containment or the thermal oxidiser, never
to atmosphere, and the toxicity of methyl bromide is a HAZOP and consequence item (release
from the vent, the relief, the vaporiser E-101 and the liquefied store).
Open: calorimetry (heat of reaction in 2-MeTHF with gas dosing, heat-flow profile, the induction
time, TD24 of the solution and of the wet magnesium cake), the relief of R-101 for the
boiling-solvent case with its methyl bromide release and its routing, the vent's pressure case,
the toxic-release consequence of methyl bromide, the heating-medium safeguards of D-010. D-014
settles the relief's case and routing and the permissive's scope, and states what of these
stays open and which measurement gates which decision.
Screening values only, not a reaction-hazard assessment.

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
scrubber; methyl bromide is a controlled ozone-depleting substance; an amount entirely used as
feedstock in making other chemicals is not counted as production under the Montreal Protocol,
Article 1(5) (SRC-11), but its emission must be destroyed, not vented. The wet magnesium cake
(10.2 g/kg) to quench and hazardous-waste treatment. Not counted: the 2-MeTHF vapour in the off-gas and the filter's nitrogen (core models
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

## D-014 Relief basis, initiation and heating conditions from core 1.12.0's screening (2026-11-19)
Context: process-library#427 lists this entry's open design findings: the k/100 and the
uninitiated whole-dose cases exceed the 20 m3/h vent about 2.5 times, they need the initiation
permissive and a relief, and the heating medium is close to the MTT (D-010, D-011). Rescreened
with `cheme process reactor-hazards` on core 1.12.0 (0e85885; core ADRs 0069 and 0071).

**The entry as it is (no file changed).** dT_ad 548.0 K, accumulation 0.615 %, MTSR 321.5 K, MTT
356.3 K, as on 1.9.0. The largest gas release over the batch is the release at the MTSR, 2.797
m3/h of ethane at 5.75 h (0.14 times the vent). Methyl bromide held in the liquid: at most
0.0924 kmol (8.77 kg) at 5.75 h (`dissolved_release`, `cheme.reactor-hazard-dissolved`, info),
core's own figure for the 9 kg D-011 had by hand. Core reports WURTZ as a consecutive reaction
on GRIG's product (`network`): dT_ad 548.0 K and MTSR 321.5 K, the same as the largest single
reaction (GRIG takes the methyl bromide, the more exothermic of the pair), so
`hazard.potential: network` is not set.

**The cases of D-011 on 1.12.0** (scratch copies, both rate constants divided as in D-011; "with
vapour" adds `vent.vapour: {components: [METHF]}` with 2-MeTHF's vapour pressure as the
Clausius-Clapeyron line through 351.15 K with 34.0 kJ/mol, the line core's default MTT uses,
written in Antoine form ln(P/kPa) = 16.2637 - 4089.26 K / T, my arithmetic from SRC-1 and
SRC-10, ASSUMED; the files declare no vapour pressure):

| case | MTSR | largest release over the batch (ethane) | times the vent | methyl bromide held, largest | with the 2-MeTHF vapour | boil-up at the bubble point |
|---|---|---|---|---|---|---|
| base | 321.5 K | 2.80 m3/h at 5.75 h | 0.14 | 8.77 kg at 5.75 h | 3.51 m3/h, vapour share 0.20 (0.18 times the vent) | does not boil |
| k/10 | 341.5 K | 4.77 m3/h at 5.75 h | 0.24 | 60.9 kg at 5.75 h | 8.27 m3/h, vapour share 0.42 (0.41 times the vent) | does not boil |
| k/100 | 433.9 K | 49.25 m3/h at 5.75 h | 2.46 | 301.2 kg at 5.75 h | boils at the MTSR | 3863 m3/h of vapour at 369.6 K from 1425 kW (193 times the vent) |
| 5 % initiation charge, uninitiated | 349.5 K | 6.6e-5 m3/h | 3e-6 | 71.2 kg at 0.25 h | 1.1e-4 m3/h | does not boil (but see below) |
| 3 % initiation charge, uninitiated | 337.0 K | - | - | 42.7 kg at 0.25 h | - | does not boil |
| whole dose uninitiated | 843.0 K | 93.13 m3/h at 15.1 h (its MTSR 775.2 K) | 4.66 | 1366 kg at 5.75 h | boils at the MTSR | 503 m3/h at 375.7 K from 182.5 kW (25 times the vent) |

The k/100 and uninitiated rows take the ASSUMED rate laws far outside their 298-338 K range: an
order of magnitude, not a value. With the vapour, core's largest release over the batch at k/100
is 3.1e4 m3/h: the reactions' heat at the MTSR, 434 K, a temperature a content boiling at 369.6
K does not reach while it is relieved; the boil-up at the bubble point (`gas_release.boil_up`, a
tempered reaction) is the relief's case. Methyl bromide stripped by the gas release on a cooling
failure (a further scratch run with methyl bromide's Antoine parameters, SRC-12, extrapolated
from 276.8 K): at most 0.097 kg/h at the base rate and 2.83 kg/h at k/10, and the release with
the vapour 3.53 and 9.43 m3/h (0.18 and 0.47 times the vent).

**The bubble point with the dissolved methyl bromide** (my arithmetic: Raoult's law, an ideal
liquid ASSUMED, over 2-MeTHF and methyl bromide only, both by Clausius-Clapeyron, methyl
bromide from 276.55 K and 23.3 kJ/mol, SRC-7; the dissolved salts and the magnesium left out,
which gives the lower, conservative value; core's bubble point leaves a dosed gas boiling below
`T_p` out, L-14): base at its worst moment 355.8 K at 120 kPa(a) and 350.6 K at atmospheric
pressure; the uninitiated 5 % initiation charge 352.1 and 346.8 K; 3 % 353.7 and 348.5 K; k/100
at its worst moment 341.1 and 335.6 K; the whole uninitiated dose 316.2 K, below `T_p`: a whole
dose could not be held dissolved at 120 kPa(a) (the fixed `absorbed: 0.99` does not follow this),
so it would raise R-101's pressure and pass to the vent before it all accumulated.

Decisions:
1. **Relief basis: the tempered boil-up of a sluggish reaction (k/100).** R-101's emergency
   relief, separate from the process vent, is designed for about 3.9e3 m3/h of 2-MeTHF vapour at
   369.6 K and 120 kPa(a) (0.0419 kmol/s, about 13 t/h, from 1.4 MW of reaction heat), preceded
   by the 301 kg of dissolved methyl bromide, which boils off first (the content with it boils
   at about 341 K). It discharges to a catch tank, not to the oxidiser's header (193 times the
   20 m3/h it is sized for) and never to atmosphere; the catch tank holds R-101's liquid at the
   end of the dosing, 4.56 m3 (`cheme process recipe`; ASSUMED, as a two-phase discharge can
   carry the content out), is kept dry and under nitrogen (the Grignard solution reacts with
   water), and its vent goes to the thermal oxidiser and caustic scrubber for the methyl bromide.
   Reason: the boil-up is two orders of magnitude above any process vent; the relief load of a
   tempered reaction is the vapour the reaction heat makes at the bubble point (core ADR 0069,
   Stoessel, SRC-8, method). The k/10 case needs no relief: the vent holds it with the solvent
   vapour (0.41 times).
2. **The uninitiated whole dose is not a relief case.** Its accumulated 1366 kg of methyl bromide
   reacting at the initiated rate would release the batch's whole heat, about 4.2 GJ (14.39 kmol x
   291.1 MJ/kmol), in seconds (at the base rate constant the same content releases about 1e4
   times the 182.5 kW of the k/10000 case at 375.7 K: my arithmetic, the rate law ASSUMED far out
   of range): no relief of a 6.3 m3 vessel can be sized for it. It is excluded from the relief
   basis and prevented: the initiation permissive (the main dosing only after a positive
   initiation signal of the initiation charge: temperature rise, heat flow or in-situ IR, SRC-6
   practice) and the dosing stop on low heat flow, high temperature, loss of brine or of the
   agitator (D-011). Their logic, signals and reliability (SIL) are for the HAZOP and LOPA; none
   is claimed here.
3. **Initiation charge: 5 % stays in the model; 3 % is recommended.** An uninitiated 5 % charge
   reaches 349.5 K, 2.6 K below its content's bubble point with the pad at 120 kPa(a) and 2.7 K
   above it at atmospheric pressure: it is safe only with the pad held through the hold. A 3 %
   charge (scratch copy, core 1.12.0) reaches 337.0 K, 11.5 K below the atmospheric bubble point
   of its content (348.5 K), with 42.7 kg of methyl bromide held instead of 71.2 kg; over the
   whole batch it changes little (peak cooling 234.3 kW against the jacket's 249.2 kW, MTSR 321.6
   K, accumulation 0.627 %, cycle unchanged). It is not adopted yet because the charge must give an
   unambiguous initiation signal (3 % gives an adiabatic rise of 18.9 K against 31.4 K at 5 %),
   which only the calorimetry can show.
4. **The heating permissive covers the initiation charge** (D-010, amended): the hot water
   (353.15 K) is above the bubble point of the initiation charge's content even at 120 kPa(a).
5. **The MTT stays core's default, 356.3 K.** `hazard.mtt_from: bubble-point` gives 367.6 K (the
   content after GRIG at 120 kPa(a), the MeMgBr counted as an ideal non-volatile solute at about
   28 mol%): higher, so less conservative, resting on Raoult's law for a concentrated
   organomagnesium solution with no basis, and blind to the dissolved methyl bromide, which
   lowers the bubble point (above). Not adopted.
6. **R-101's vent, 20 m3/h, stays.** It holds the base and k/10 cases with the solvent vapour and
   the stripped methyl bromide (0.18 and 0.47 times). D-011's base-case figure (the dissolved 9
   kg driven out in 15 min, 11.1 m3/h) stays as an upper bound: the base content at the MTSR is
   34 K below its bubble point, so the methyl bromide leaves by stripping (0.1 kg/h).
7. **The vent condenser cannot freeze.** R-101's reflux condenser on brine at 263.15 K is far above
   the melting points of what it condenses, 2-MeTHF 137.05 K (SRC-10a) and methyl bromide
   179.47 K (triple point, SRC-12); the train is dry. No tempered coolant is needed. The rule
   `cheme.process-condenser-freezing` checks a modelled `vent.condenser`; the entry models none,
   so the melting points are not declared.
8. Not used from core ADR 0071: the head space and inerts (the nitrogen of inerting and the pad
   are the LCI's per-batch nitrogen, D-012; modelling them would carry solvent vapour into the
   vent, L-6, an LCI change outside #427), the heat of absorption and Henry's law (no sourced
   value for methyl bromide in 2-MeTHF, L-7, D-004).

Stays open, and what it gates:
- reaction calorimetry with gas dosing in 2-MeTHF up to the bubble point (heat flow, the
  induction time, the rate above 338 K): the relief load of decision 1 (the k/100 boil-up rests
  on the ASSUMED rate law extrapolated to 369.6 K), the dosing-stop thresholds of decision 2 and,
  with the initiation signal it shows, the 3 % or 5 % charge of decision 3;
- vent-sizing tests of the solution (level swell, foaming, viscosity; DIERS method) and R-101's
  design and set pressures: the relief area and the catch tank of decision 1 (core models no
  two-phase relief or vessel pressure);
- the TD24 of the solution and the wet magnesium cake (DSC or ARC): the criticality class, and
  whether the k/100 MTSR (434 K) reaches a decomposition;
- the solubility and vapour-liquid equilibrium of methyl bromide in 2-MeTHF: the dissolved
  inventory and the bubble points above (Raoult's law ASSUMED);
- human sign-off: the hot water at 343.15 K against the instrumented heating permissive (D-010),
  and the SIL and LOPA of the permissive and the dosing stops (none claimed here).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with gas dosing and vent: composition, accumulation, cooling-failure temperature, peak cooling, off-gas | done in cheme, kinetics and gas uptake ASSUMED | D-004, D-005, D-011, `process reactors`, `reactor-hazards` |
| magnesium as a solid reactant | done in cheme (pseudo-concentration) | D-005, D-006 |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| vessel sizing, jacket check, warm-up time (R-101) | done in cheme, U and media ASSUMED | D-003, D-010, core ADR 0052 |
| filtration and its time (F-101) | specified split, Ruth time in cheme, cake data ASSUMED | D-007, core ADR 0057 |
| duties | Q1 in cheme (R101 `energy_port`, core ADR 0059); Q2, Q3, P1, P2 by hand | D-009 |
| per-batch exchanges (nitrogen, iodine) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Lessons for core (core limits hit; candidates for core issues)

- L-1: **no induction period or initiation model.** A delayed initiation can only be shown by a
  rate constant that is slow for the whole batch (k/100 in D-011), not by a rate that switches on
  after an induction time while the dosing goes on, and the dosing cannot be made conditional on
  the initiation (no control of the dosing, core ADR 0050). A `batch.induction: {time, factor}` or
  a time-dependent rate multiplier, and a screening scenario "dosing continues uninitiated for
  t", would show the real hazard of a Grignard step directly.
- L-2 (partly resolved, core 1.9.0 ADR 0058): **only the worst cooling-failure moment was
  reported.** Core 1.9.0 adds the MTSR over the batch (`mtsr_profile`, 22 points in
  `reactor-hazards --json`, 7 printed), which shows the base case's MTSR from the initiation to
  the end of the dosing (D-011). The MTSR of an uninitiated initiation charge (5 % dosed into the
  cold charge, then a hold) still needs a second scratch run with only that dose and a slow rate:
  the profile follows the modelled rate, not a failed initiation (L-1). Core 1.12.0 adds the
  largest gas release over the batch (ADR 0069; at the base rate the same as at the MTSR, D-014).
- L-3: **propagate writes the vented component into the liquid outlet** with a mole fraction of 0
  (`C2H6: 0.0`), so the liquid's template must list the gas, or validate reports
  `cheme.process-component`. A vented component that never stays in the liquid should be left out
  of the liquid outlet's composition.
- L-4: **a solid reactant works, as a pseudo-liquid.** Magnesium needs a `liquid_molar_volume`
  and `liquid_heat_capacity` and enters the rate law as a pseudo-concentration (order 2/3 here as
  a surface proxy); there is no surface-area rate (particle size, specific area, a shrinking
  particle), which a Grignard formation or any dissolving-metal step would need.
- L-5 (resolved, core 1.9.0 ADR 0058): **default MTT below the process temperature** (methyl
  bromide's 276.55 K in the liquid, dissolved 42 K above its boiling point; as
  phosphorus-tribromide-1 L-2 with bromine): on 1.8.0 fixed with `hazard.mtt`. Core 1.9.0's
  default leaves out the dosed gas and the vented ethane and takes 2-MeTHF's boiling point at
  R-101's 120 kPa(a), 356.3 K (D-011). Still open: the dissolved gas lowers the liquor's boiling
  point, which the MTT does not follow.
- L-6: **the vent carries no solvent vapour and has no pressure.** At 318 K, 2-MeTHF has a vapour
  pressure of about 30 kPa, so the ethane and the passing methyl bromide strip solvent to the
  oxidiser; core models no stripping (core ADR 0054 limitation), so the LCI excludes it. There is
  no gas-solubility basis for `absorbed` (a fixed share stands for Henry's law and mass
  transfer). Partly resolved by core 1.9.0 (ADR 0058): the gas release at the MTSR is compared
  with a stated `hazard.vent_capacity` (rule `cheme.reactor-hazard-vent`, D-011). Still open: the
  pressure of a blocked vent is not screened, and the release counts only the vent's components,
  not the dissolved toxic methyl bromide a cooling failure boils off (an ADR 0058 known
  limitation; D-011 adds it by hand). Core 1.12.0 (ADR 0069) reports the methyl bromide held in
  the liquid (8.77 kg at the base rate) and, with `vent.vapour`, what the gas release strips and
  a boiling content's boil-up (D-014); still open: the blocked vent's pressure, a two-phase
  relief, and the vapour pressure the entry would need to carry the solvent in the vent.
- L-7: **heat of absorption.** A dissolving gas adds only its sensible heat; the heat of
  reaction is written on the gas basis (core ADR 0054), so the MTSR is conservative but the
  isothermal duty during the dosing leaves out the absorption of the unreacted gas (small here,
  0.6 % accumulated).
- L-8 (resolved): core main reported version 1.7.0 before its release, so `plant.yaml` could not
  require the 1.8 that `batch.vent`, `dosing.absorbed`, recipe `units:` and `filtration:` need.
  Core 1.8.0 is released and pinned; `plant.yaml` requires `cheme-as-code>=1.8`.
- L-9 (resolved, core 1.9.0 ADR 0059): **no energy stream from a batch model.** On 1.8.0 R101's
  isothermal heat removal was known to the model but `process propagate` did not write it onto
  the energy port, and Q1 was copied by hand from the extents. With `energy_port: q` propagate
  writes the year-average duty on Q1, 134.1 kW `calculated` (D-009); the charge's warm-up (Q2)
  stays a hand value, as no model writes it.
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
- L-14 (core 1.12.0): **the bubble point leaves a dissolved, dosed gas out.** `hazard.mtt_from:
  bubble-point` and the boil-up's bubble point (ADR 0069) leave out a dosed gas boiling below
  `T_p`, but methyl bromide dissolved at 2 to 8 mol% lowers R-101's bubble point by 4 to 15 K
  (Raoult's law, D-014), the side that matters for the heating medium and the initiation charge.
  A dosed gas with a declared vapour pressure (or Henry constant) could be counted in the
  bubble point. L-7: core 1.12.0 has `vent.heat_of_absorption` (ADR 0071); the entry has no
  sourced value to give it.

## Open inputs
Kinetics, induction time and heat of reaction in 2-MeTHF with gas dosing (calorimetry, in-situ
IR); TD24 of the solution and of the wet magnesium cake; methyl bromide's solubility in 2-MeTHF
and the real slip to the vent; the Wurtz selectivity; R-101's cooling arrangement and U (D-010)
and its relief, whose case (the k/100 boil-up) and routing (a catch tank) D-014 sets, sized by a
two-phase study with the calorimetry and R-101's design pressure (D-011, D-014); the initiation
charge, 3 % or 5 %, from the initiation signal (D-014); the heating-medium safeguards or a hot
water below the content's bubble point (D-010, D-014); the quench drum's
inerting and hydrogen vent (D-007); the filter cake's resistance and liquor (D-007); a
magnesium heel as an alternative (D-007); the product specification beyond the assay; the
oxidiser and scrubber; a TEA (`operation.batch: {recipe: true}`).
