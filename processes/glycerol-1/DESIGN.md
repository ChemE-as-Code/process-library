# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml`; the stream table is generated: `cheme process streams
--md` (provenance letter per value). Issue: ChemE-as-Code/process-library#186.

Run record of this stage (2026-10-28): library branch `case/glycerol-1` from `11d50ef`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core dependencies from the
issue comments were not re-audited against core main in this
run; this design does not use extraction, so core's extraction support does not apply (D-001).

## 1. Route and boundary memo

- **Route**: refining of the crude glycerol phase of a biodiesel (FAME) plant to USP-grade
  glycerol by the classical chemical-physical sequence: acidulation, separation of the freed
  fatty matter, neutralisation, methanol recovery, dewatering, vacuum distillation with salt
  removal, bleaching. The issue asks to keep this apart from fat splitting / soap-lye glycerol
  and from synthetic glycerol (propylene via epichlorohydrin); neither is modelled.
- **Alternatives not taken**: ion exchange of a dilute glycerol-water solution (low energy but
  limited to low-salt feeds and large regenerant volumes; Thompson & He 2006 p. 261 mention it
  as the less energy-intensive refining route), membrane processes and the multi-step
  physico-chemical route without distillation (Attarbachi et al. 2024: reaches about 82-85 wt%,
  not USP). Vacuum distillation is the established commercial route to 99.5 %+ glycerol
  (Molecules review 2026, section 4.1).
- **Boundary** (gate-to-gate): from crude glycerol, 32 wt% HCl, 50 wt% NaOH and activated
  carbon at the battery limit to refined glycerol at the product cooler outlet. Inside:
  acidulator, fatty-layer decanter, neutraliser, methanol column, dewatering evaporator, vacuum
  still with condensers, salt centrifuge, carbon bleacher, product cooler. Outside: the
  biodiesel plant (which makes the feed and takes back the methanol and the fatty layer),
  steam and power generation, cooling tower, wastewater treatment, waste treatment, storage.
- **What crosses the boundary**: CRUDE, HCLA, NAOHS, ACF (raw materials); GLYC (product);
  MEOHR, FAL (co-products to the biodiesel plant); SALT, FOOTS, SPAC (wastes); WW
  (wastewater); POWER, LSTM (live steam, material), MSTM (ejector motive steam, material), LPS,
  MPS and HPS (heat), CW (utilities).
- **Library links**: caustic soda from chlor-alkali-1 (membrane caustic); methanol for the
  biodiesel plant from methanol-1 (outside this boundary: the refinery returns methanol, it
  does not buy it). Hydrochloric acid is not made by any library process yet (chlor-alkali-1
  makes Cl2 and H2, not HCl). No library process makes biodiesel or crude glycerol.

## 2. Decisions

## D-001 Route and boundary (2026-10-28)
Decision: classical refining of biodiesel crude glycerol as in section 1, sodium-methylate
catalyst plant upstream, HCl acidulation (so the salt is NaCl).
Reason: the issue's route; HCl suits a sodium catalyst (NaCl removed in the still residue).
The plant described by Attarbachi et al. (2024, section 1, an industrial biodiesel refinery)
runs the same front end: acidulation to about pH 3, three-phase separation of fatty acids,
glycerol and salt, neutralisation, methanol distillation, dewatering.
Rejected: H2SO4 or H3PO4 acidulation (gives Na2SO4 / phosphate salts, used with KOH
catalysts when the salt is sold as fertiliser, Attarbachi et al. 2024 section 2); extraction
(no extraction step: core's extraction support not needed); ion exchange and membrane routes (section 1).
Assumptions: the feed reaches the refinery unstripped (methanol still in it).

## D-002 Capacity and operating hours (2026-10-28)
Decision: 1250 kg/h refined glycerol (10 000 t/a at 8000 h/a). ASSUMED.
Reason: a normalisation basis for the inventory, about the glycerol of a 100 000 t/a
biodiesel plant (crude glycerol is about 10 % of the oil, Thompson & He 2006 p. 261); not a
claim about a commercial plant (issue #186 scope notes). Geography not chosen.

## D-003 Product specification (2026-10-28)
Decision: glycerol 99.7 wt%, water 0.3 wt%, colourless after bleaching. ASSUMED design grade.
Reason: refined glycerol from biodiesel is traded at 99.5-99.7 % (RSC Advances 2022 review,
text after Table 1); the USP monograph assay (99.0-101.0 % on the anhydrous basis) is met.
Trace limits (chloride, sulfate, heavy metals, related substances, colour) are not modelled.

## D-004 Crude glycerol feed composition (2026-10-28)
Decision: S1 mass fractions glycerol 0.59841, methanol 0.29332, NaOCH3 0.02847, fatty matter
0.0798, given.
Source: Thompson & He (2006), Appl. Eng. Agric. 22(2) 261-265, soybean oil with NaOCH3:
glycerol layer 16.16 g, glycerol by difference 10.96 g (Table 3), catalyst 0.46 g (Table 1),
so methanol 4.74 g (the paper determines methanol by difference, p. 262); fat 7.98 % of the
crude glycerol (Table 6). Because the paper's glycerol is by difference, it holds the fat: the
fat is taken out of it here. The sodium of the catalyst (1.21 wt% Na) agrees with the
measured 1.20 wt% Na of Table 5.
Lumps: fatty matter (soaps, esters, glycerides) as one component with the formula of methyl
oleate; the catalyst as NaOCH3 as charged (in the glycerol layer it is partly NaOH, sodium
glyceroxide and soap; the acid demand per Na is the same). No water: the laboratory reagents
were anhydrous; an industrial glycerol phase carries some water (open item).
Inconsistency (open): Table 5 gives 26 wt% carbon for the same crude glycerol, but any mixture
of glycerol (39 wt% C) and methanol (37.5 wt% C) has more than 37 wt% C; the sample analysed
was probably dried or diluted differently. The model follows Tables 1, 3 and 6.
The design basis (process/design-basis.yaml) carries the same composition (corrected
2026-10-28 after review #1, which found an older draft composition with water and NaOH there).
Variability: industrial crude glycerols range 30-80 wt% glycerol with up to 16 wt% ash and up
to 40 wt% MONG (Attarbachi et al. 2024, Table 1); a second design case should cover a
high-ash, high-MONG feed.

## D-005 Acidulation and neutralisation (2026-10-28)
Decision: 32 wt% HCl at 10 % over the catalyst sodium in R-101 at about 342 K (pH about 3-4);
the catalyst is converted to NaCl and methanol (NEUT1, full conversion); the soaps split and
the fatty matter separates. The excess acid is neutralised with 50 wt% NaOH in R-102 (NEUT2,
stoichiometric). Both adiabatic (process/simulation.yaml): NEUT1 releases about 18 kW
(1.16 kmol/h x 55.8 kJ/mol), NEUT2 1.8 kW; with the mixing of the cold acid and caustic and
ASSUMED liquid heat capacities, scripts/glycerol_balance.py gives S3 341.6 K and S7 342.6 K
(revised 2026-10-28 after review #6, which found the earlier "65 kW" a unit slip).
Reason: acidulation to about pH 3 then neutralisation is the industrial practice reported by
Attarbachi et al. (2024, section 1). Below pH 3 glycerol can dehydrate to acrolein; at high pH
near 200 C it polymerises (Molecules review 2026, section 4.1): the still must see a neutral
feed. Excess 10 % ASSUMED. The heat of neutralisation (-55.8 kJ/mol) is the dilute-water value,
ASSUMED for the glycerol-methanol medium. Chloride below pH 7 needs lined or alloy equipment
(material not chosen).

## D-006 Fatty-layer separation (2026-10-28)
Decision: 97 % of the fatty matter to the fatty layer S4; the layer holds 5 wt% methanol and
1 wt% glycerol; no salt or water in it. ASSUMED. The layer goes back to the biodiesel plant
(esterification of the free fatty acids), as in the plant of Attarbachi et al. (2024,
section 1). The 3 % left in the glycerol ends in the still residue.

## D-007 Methanol recovery (2026-10-28)
Decision: atmospheric column C-201 (120 kPa(a) at the bottom), 99.5 % of the methanol to a
99.5 wt% distillate, reflux ratio 1.0, bottoms about 425 K, reboiler E-201 on MP steam
1000 kPa(a) (453 K). ASSUMED (no VLE calculation: glycerol-methanol-water with NaCl is not
covered by a qualified package, D-012). Methanol and water are easily separated in the
presence of glycerol; the reflux is a conservative placeholder for the duty.
Revision (2026-10-28, review #3): nearly all the water stays in the bottoms (about 7 wt%,
93 wt% glycerol salt-free), and aqueous glycerol of that strength boils near 418-425 K at
1 atm (the reviewer's estimate from general glycerol-water boiling data, not re-read here),
so the earlier 383 K was too low and LP steam (421 K) cannot serve E-201 with a 10 K approach.
The bottoms temperature is ASSUMED 425 K and E-201 moved to MP steam. Holding more water or
methanol in the bottoms is not an option: the water load is fixed by the acid and caustic.

## D-008 Dewatering (2026-10-28)
Decision: falling-film evaporator E-301 at 10 kPa(a), 403 K, to 1 wt% water; all residual
methanol and 0.1 % of the glycerol go to the condensate. ASSUMED.
Reason: the still feed must hold no more than 10-15 wt% water to keep the vacuum stable
(Molecules review 2026, section 4.1). Revision (2026-10-28, review #3): the earlier 5 wt% water
at 10 kPa(a) and 403 K was inconsistent (5 wt% water boils near 355 K at 10 kPa(a)). A Raoult
estimate (water saturation pressure about 270 kPa at 403 K, water activity coefficient in
glycerol about 0.9, ASSUMED) gives about 0.8-1 wt% water at 10 kPa(a) and 403 K, taken as
1 wt%. The feed S9 arrives at about 425 K, so part of the water flashes and the steam duty Q3
is small; the drier still feed also cuts the vapour the still vacuum system must handle.

## D-009 Vacuum distillation (2026-10-28)
Decision: wiped-film or forced-circulation still C-401 at 1.5 kPa(a) and 448 K bottoms, live
steam 0.10 kg per kg glycerol fed; 95 % of the glycerol to the distillate (99.7 wt%), 0.5 % to
the vacuum condenser, 4.5 % with the salt and fatty matter to the residue. ASSUMED.
Reason: industrial glycerol stills run at 10-30 mbar, and a salt content of 2-5 wt% calls for a
scraped-wall evaporator (Molecules review 2026, section 4.1); 448 K stays below the
polymerisation range near 200 C (same section). The live steam lowers the glycerol partial
pressure (ASSUMED ratio). Recoveries are placeholders: no VLE of glycerol-water-NaCl is
qualified (D-012). Overall glycerol recovery feed to product: 94.6 %.
Vacuum system (added 2026-10-28, review #2): after the glycerol condenser E-402 the vapour
(live steam S14, the residual water of S11 and a little glycerol, about 148 kg/h) cannot be
condensed on cooling water at 1.5 kPa(a), where water saturates near 286 K, and at about
1.5 kPa(a) it is of the order of 10^4 m3/h, beyond a mechanical vacuum pump of the size the
power estimate allows. Decision: two steam-jet booster ejectors J-403 on MP steam 1000 kPa(a)
(S22, feed MSTM) compress it to 8 kPa(a), where water saturates near 315 K (steam tables), so
the intercondenser E-403 condenses vapour and motive steam on cooling water 298/308 K (S15 at
313 K); a liquid-ring vacuum pump P-404 takes the non-condensables to atmosphere (in W4).
Motive steam 1.5 kg per kg vapour drawn (ASSUMED engineering order of magnitude for a
compression ratio of about 5 in two stages, not sourced; to be replaced by an ejector vendor's
or a sourced steam-consumption curve): 222.5 kg/h, 0.18 kg per kg product. The motive steam
is condensed into the wastewater (S15), not returned. Rejected for now: a chilled-water
condenser at 1.5 kPa(a) (needs refrigeration below 280 K and a large condenser) and dry
mechanical vacuum pumps on the full vapour load; both are lower-steam alternatives for a later
comparison.

## D-010 Salt removal and residue (2026-10-28)
Decision: the salt crystallises in the still residue; a decanter centrifuge S-402 separates 90 %
of it as cake holding 0.25 kg mother liquor per kg crystals; the rest (glycerol foots, about
82 wt% glycerol, 10 wt% NaCl, 7 wt% fatty matter) goes to anaerobic digestion or incineration
outside the boundary. ASSUMED. Salt cake to landfill (no buyer assumed).
Reason: the NaCl content of the dewatered glycerol (about 5 wt%) is near its solubility in
glycerol, so it does not settle before the still; it accumulates as the glycerol evaporates.
Solubility not calculated (core's single-solute crystallisers do not cover NaCl in
glycerol; electrolyte route covers aqueous NaCl only).

## D-011 Bleaching (2026-10-28)
Decision: activated carbon bed V-501 at 363 K, 2 kg carbon per t distilled glycerol, 1 kg
glycerol held per kg spent carbon. ASSUMED.
Reason: carbon treatment decolorises and deodorises, with little change in purity (Attarbachi
et al. 2024, results on the carbon step). Their crude-glycerol dose (50 g/L laboratory,
7.36 kg per m3 product in their scaled design) is for undistilled glycerol; distilled glycerol
needs far less (ASSUMED 2 kg/t, to be checked with a supplier).

## D-012 Utilities and duties (2026-10-28)
Decision: cooling water 298/308 K; LP steam 450 kPa(a) (421 K) for the evaporator and the
live steam; MP steam 1000 kPa(a) (453 K) for the methanol reboiler (D-007) and the ejector
motive steam (D-009); HP steam 3000 kPa(a) (507 K) for the still reboiler (thermal oil is the
usual alternative); electric power 50 kWh/t product (pumps, agitators, liquid-ring vacuum
pumps, centrifuge), all ASSUMED. Duties from a lumped latent plus sensible heat balance in
scripts/glycerol_balance.py: methanol 35.21 kJ/mol at its boiling point (NIST WebBook),
water 2333 kJ/kg near 343 K (steam tables), glycerol 85 kJ/mol near 450 K (ASSUMED within the
range of NIST WebBook entries), liquid heat capacities near 298 K (ASSUMED for the lumps).
Result per t product (revised 2026-10-28 after review #2 and #3): indirect steam heat 757 kWh
(MP 430, LP 29, HP 298), live steam 105 kg, ejector motive steam 178 kg, power 50 kWh, heat to
cooling water 921 kWh.
Cross-check: a reported 166.5 kWh heat per t at the reboiler of a vacuum distillation design
starting from 80 wt% glycerol (Braga et al., as cited by Attarbachi et al. 2024, energy
discussion) is below the latent heat of the glycerol itself (about 256 kWh/t), so it probably
excludes evaporation or assumes heat recovery; a planned 50 000 t/a refinery to 99.7 % is
quoted at about 1000 kWh/t heat and power together (same place). This design: about
1020 kWh/t (757 + 283 kg live and motive steam at about 0.75 kWh/kg + 50), the same order as
the second figure.
Heat integration not studied (E-402 condenses glycerol at about 420-450 K and could raise LP
steam).
Gated step: energy closure in core. `cheme process energy` reports every block not evaluable
(no stream enthalpies) and `cheme process props --coverage` finds no package for glycerol,
methanol, water, NaCl or the lumps. Needed: a qualified polar / activity-coefficient package
for glycerol-methanol-water with liquid-phase enthalpies, NaCl in glycerol-water
(core's electrolyte support covers aqueous NaCl only) and salt crystallisation in the still.

## D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg refined glycerol (GLYC) at the gate; every foreground exchange
of the balanced flowsheet; every background left unmapped (`missing:` with the activity it
should connect to, lca/lca.yaml), so each is a gap, never 0. Mass allocation between refined
glycerol, recovered methanol and the fatty layer (glycerol share 0.594), declared as a
deviation from the library hierarchy until prices are sourced; economic allocation and
substitution are open sensitivities. Carbon origin: biogenic fraction of the crude glycerol
carbon 0.710 (glycerol and fatty chains from vegetable oil; methanol, methoxide and ester
methyl fossil). No construction, transport or end of life at this stage. lca/mappings.yaml has
no overrides (internal process, ADR 0022).
Allocation variants (added 2026-10-28, review #5): the recovered methanol S8 is the biodiesel
plant's own excess reactant, which arrives in the crude and leaves unchanged; under mass
allocation it takes 32 % of the burden, including 32 % of the crude glycerol it arrived in.
lca/lca.yaml therefore reports three variants side by side (`allocation.compare`): mass
(glycerol share 0.594), `shares` with the methanol treated as a return (share 0; glycerol
0.873, fatty layer 0.127 by mass) and `none` (glycerol carries everything, 1.000). Before any
background is linked, the preferred treatment is the return: either net the methanol off the
crude feed or use system expansion; the choice is open until the crude-glycerol background is
chosen, because that dataset's own allocation decides whether the methanol mass is already in
it.
Baseline changed to `shares` (methanol as a return, 2026-10-28, PR #218 CI): the preferred
treatment above becomes the baseline, mass and none stay as variants. Reason besides the
review: `mass` is the schema default, and `cheme assess lca --write` leaves defaults out of
lca/dataset.yaml, so the library's strict LCI build (scripts/build_lci.py) saw no dataset
method and warned that the study's `mass` differed from it, which failed CI. An explicit
non-default method is written and read back unchanged. Mass in the first paragraph of this
decision is superseded by this; prices (economic) remain the open sensitivity.
Result (cheme assess lca --balance, per hour, revised after review #2): mass in 2713.0 kg = out
2713.0 kg; C, H, O, Na, Cl closed within 0.01 %; carbon in 265.5 kg fossil + 643.8 kg
biogenic. The inventory's boundary flows equal the flowsheet's boundary streams (S1, S2, S6,
S14, S18, S22 in; S4, S8, S10, S12, S13, S15, S19, S21 out). Coverage: partial (15 gaps),
climate category only.

## 3. Method and dependency table

| step | model here | what would make it predictive | core item |
|---|---|---|---|
| R-101, R-102 | full-conversion acid-base reactions (balanced by cheme) | adequate as is | - |
| V-102 decanter | specified split | LLE of glycerol-methanol-fatty matter, salt effects | core: polar qualification; extraction not needed |
| C-201 | specified recovery | VLE glycerol-methanol-water(-NaCl) | core: property qualification, electrolytes |
| E-301 | specified water content | VLE and enthalpy of glycerol-water-NaCl | core: property qualification, electrolytes |
| C-401, S-402 | specified recoveries, salt split | VLE at vacuum, NaCl solubility in glycerol, crystallisation | core: property qualification, electrolytes, solids |
| duties | lumped latent + sensible script | liquid enthalpies of the mixtures | core: property qualification |

## 4. Sources (register)

| source | locator | read | terms | used for |
|---|---|---|---|---|
| Thompson & He (2006), Appl. Eng. Agric. 22(2) 261-265, https://biodieseleducation.org/Literature/Journal/2006_Thompson_Characterization_of_.pdf | Tables 1, 3, 5, 6; p. 261-262 | full text | ASABE copyright; facts only | D-004, D-002 |
| Attarbachi et al. (2024), Ind. Eng. Chem. Res., doi 10.1021/acs.iecr.3c03868 (Europe PMC PMC10958504) | section 1 (industrial front end), Table 1, carbon step results, energy discussion (Braga et al.; planned refinery) | full text | CC BY 4.0; facts only | D-001, D-004, D-005, D-006, D-011, D-012 |
| The Crude Glycerol Challenge (2026), Molecules 31(11) 1841, doi 10.3390/molecules31111841 (PMC13258803) | section 4.1 | section read | open access; facts only | D-005, D-008, D-009 |
| Recovery and utilization of crude glycerol (2022), RSC Advances, doi 10.1039/d2ra05090k (PMC9523763) | Table 1 and following text | section read | CC BY-NC 3.0; facts only | D-003 |
| Yang, Hanna, Sun (2012), Biotechnol. Biofuels 5:13, doi 10.1186/1754-6834-5-13 | introduction | skimmed | CC BY 2.0 | context |
| NIST Chemistry WebBook (methanol, glycerol phase-change data) | enthalpy of vaporization entries | values recalled, not re-read in this run | US public data | D-012 (ASSUMED where marked) |
| Ullmann's: Glycerol, doi 10.1002/14356007.a12_477.pub2 | - | not read | licensed | lead only |

## 5. Missing registry and vocabulary entries (for the consolidated shared PR)

- `chemicals/chemicals.yaml`: glycerol (and a USP / 99.7 % grade), crude glycerol (biodiesel
  glycerol phase), methanol, hydrochloric acid (32 wt%), sodium hydroxide (50 wt% solution),
  activated carbon, sodium chloride (salt cake), fatty acids / fatty matter; a glycerol family
  in `taxonomy/families.yaml` (process.yaml uses bio-based-chemicals).
- `lci/mappings.yaml` technosphere entries for: crude glycerol from biodiesel, caustic soda
  50 %, activated carbon, spent activated carbon treatment, salt residue landfill,
  glycerol-residue digestion or incineration; existing candidates for the rest
  (hydrochloric-acid-32, steam, steam-heat, electricity, wastewater-kg, cooling water).

## 6. Open items

- Feed water, ash and MONG variability (second case with a high-ash crude, D-004).
- Separator parameters (D-006 to D-011) from a VLE/LLE model or plant data once core
  qualifies the mixtures; NaCl solubility in glycerol for D-010.
- Sourced prices for allocation; substitution variant (D-013).
- Emissions to air: methanol from the vacuum system vents and tank breathing are not
  estimated (no tanks in the boundary; vents not modelled). After D-008 all residual methanol
  leaves in the evaporator vapour, so the methanol vent is that of the E-302 vacuum pump; the
  still vent (P-404) carries air in-leakage and traces of water and glycerol only. An ASSUMED
  vent loss needs the E-302 vent design (review #9, open).
- Feed analysis (review #7, open): D-004 says both that the paper's glycerol and its methanol
  are "by difference"; which quantity Thompson & He measured decides whether the fat must be
  subtracted from the glycerol. Not re-read in this revision (no PDF text extraction here).
- Tool finding (review #10): `cheme maturity` prints a model basis "equilibrium-stage /
  shortcut, predictive, sourced" for V102, C201 and C401, which declare no model; their
  outlets are ASSUMED values from scripts/glycerol_balance.py. Not to be quoted as evidence;
  to be reported to cheme-as-code.
- Heat integration of the glycerol condenser (D-012); HP steam vs thermal oil.
- Still vacuum: ejector motive-steam ratio (D-009, ASSUMED 1.5 kg/kg) from a vendor or sourced
  curve; comparison with a chilled condenser or dry vacuum pumps.
- Glycerol-water boiling points for S9 and S11 (D-007, D-008) from sourced data or a qualified
  VLE.
- Library/core findings of this run: the LCI dataset written by `cheme assess lca` omits
  `allocation.method` when it is mass, so `scripts/build_lci.py` warns "differs from the
  dataset's default None"; the maturity rule `sourced.boundary` asks for `given` flows of
  reagent feeds whose flows are design results (HCl, NaOH, steam, carbon).
