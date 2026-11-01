# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.

Case: potassium permanganate, issue ChemE-as-Code/process-library#146. This run (2026-10-28,
agent, library commit cbdf84a, cheme-as-code 0.8.0 / pyDEXPI 2.1.0) covers design basis ->
balanced BFD/PFD -> preliminary gate-to-gate LCI. Out of scope: P&IDs, layout, HAZOP, TEA,
datasheets. All numbers in the files are ASSUMED unless a `source:` says otherwise; nothing here
is owner, licensor or vendor data. The design is independent: no published plant balance was
reconstructed.

## Source register

What was read in this run, how, and what it is used for. Facts are restated in our own words;
no table, figure or text is copied. Patents are read through Google Patents (public documents);
locators are the patent sections because the HTML has no column numbers.

| id | source | access | used for |
|---|---|---|---|
| SRC-1 | Carus, P. III; Adolf, H.; Carus, P. II (1997) US 5,660,712, *Electrolytic production of potassium permanganate using a cationic membrane in an electrolytic cell* (Carus Chemical Co.), https://patents.google.com/patent/US5660712 | full text read (Description, Claims) | route steps (oxidation in 65-90 wt% KOH or roasting at about 225 degC, leaching in dilute KOH, electrolysis, crystallisation, KOH return); cell 2.0-3.5 V, about 55 degC, cathode 500-1500 A/m2, membrane cell; crystalliser 30-50 degC; mother liquor likely 125-175 g/l KOH, 10-25 g/l K2MnO4, 15-20 g/l KMnO4; only ~40 % of the process KOH ends in the product (D-001, D-006 to D-008) |
| SRC-2 | Garcia, M. O. G. (1991) US 5,011,672, *Process for producing potassium manganate* (Industrial Quimica del Nalon) https://patents.google.com/patent/US5011672 | full text read (Description, Claims) | conventional process steps (ore drying/grinding, attack, oxidation, dissolution and purification with lime, electrolysis, crystallisation, drying; mother liquors dissolve the manganate); ores of 70-80 % MnO2, 98 % < 80 um; KOH/MnO2 2-3 mol/mol, optimum ~2.5; oxidation 200-300 degC; > 95 % conversion claimed for the atomiser-plate reactor; prior-art liquid-phase oxidation with a large KOH excess (D-001, D-003 to D-005) |
| SRC-3 | Okabe, T. et al. (1976) US 3,986,941, *Process for the production of alkali permanganate* (Nippon Chemical Industrial) https://patents.google.com/patent/US3986941A/en | full text read (Examples 1-8) | alternative route: direct electrolytic oxidation of MnO2 slurry in 10-25 wt% KOH at 80-90 degC, nickel anode (rejected, D-001); temperature dependence of permanganate formation (cell temperature, D-006) |
| SRC-4 | US 4,911,802 (1990, MacDermid) *Conversion of manganate to permanganate* https://patents.google.com/patent/US4911802A/en | read | regeneration of etch baths, no plant data; only the solubility remark of KMnO4 in water; not used for numbers |
| SRC-5 | Subramanian, K.; Gomathi, K.; Asokan, K. (2008) Ind. Eng. Chem. Res. 47(22), 8526-8532 (CECRI record https://cecri.csircentral.net/119/) | abstract only | membrane cell with coated Ti anodes and steel cathode; ~1.5-1.7 water per K+ across the membrane; current efficiency NOT available (open input, D-006) |
| SRC-6 | Ullmann's, *Potassium Compounds*, doi:10.1002/14356007.a22_039 (issue #146 lead) | not accessed | route reference lead; production sections still to be audited |
| SRC-7 | Wagman, D. D. et al. (1982) NBS tables of chemical thermodynamic properties, J. Phys. Chem. Ref. Data 11 Suppl. 2 | values recalled, not re-read | formation enthalpies and Gibbs energies of reactions (D-009); to be checked against the table |
| SRC-8 | Cox, J. D. et al. (1989) CODATA Key Values for Thermodynamics | recalled (as in chlor-alkali-1) | heat of WATER_SPLIT (provenance assumed until the table is re-read, like SRC-7) |

Searches that found nothing usable (open): an open source for the current efficiency and the
specific DC energy of industrial manganate cells; roaster or liquid-phase oxidiser energy use;
emission factors (dust) of permanganate plants; a BREF chapter on permanganate (the LVIC-S BREF
was not checked in this run).

## Basis table (review #12)

Status of each design value: **sourced** (a value inside a range or a fact read in the named
source, locator as precise as the register gives), **assumed** (chosen without a source, or a
point inside a sourced range), **missing** (no value; gated or open). The values themselves live
in `process/design-basis.yaml`, `process/flowsheet.yaml`, `process/cells.yaml` and
`process/reactions.yaml`; this table only says how good they are.

| value | used | status | source / locator |
|---|---|---|---|
| route steps (roast, leach + lime, membrane cell, crystallise, KOH recovery) | D-001 | sourced | SRC-1 Description; SRC-2 Description |
| capacity 1250 kg/h, 8000 h/a, grade >= 98.5 wt% | D-002 | assumed | normalisation basis, no source |
| ore 70-80 % MnO2 (78 % chosen); gangue split Fe2O3/SiO2 | D-003 | sourced range / assumed point; gangue assumed | SRC-2 Description |
| grind 98 % < 80 um | D-003 | sourced | SRC-2 Claims |
| KOH/MnO2 2.5 mol/mol | D-004 | sourced (range 2-3, optimum ~2.5) | SRC-2 Description |
| roaster 523 K (range 200-300 degC; ~225 degC) | D-004 | sourced range / assumed point | SRC-2 Description; SRC-1 Description |
| MnO2 conversion 0.90; silicate dissolution 25 %; air 2.0 x O2 | D-004 | assumed | below SRC-2's > 95 % claim |
| leach 333 K (range ~45-95 degC) | D-005 | sourced range / assumed point | SRC-1 Description |
| lime 1.10 x silicate; cake liquid 0.6 kg/kg; wash recovery 90 % | D-005 | assumed | - |
| cell voltage 2.5 V (range 2.0-3.5 V) | D-006 | sourced range / assumed point | SRC-1 Description |
| cathode current density 1000 A/m2 (range 500-1500 A/m2) | D-006 | sourced range / assumed point | SRC-1 Description |
| anode current density / area | D-006 | missing | - |
| cell temperature 333 K (~55 degC; faster above 60 degC) | D-006 | sourced range / assumed point | SRC-1 Description; SRC-3 Examples |
| current efficiency 0.85 | D-006 | assumed (no open source) | SRC-5 full text not read |
| per-pass conversion 0.90 | D-006 | assumed | - |
| crystalliser 303 K (range ~30-50 degC) | D-007 | sourced range / assumed point | SRC-1 Description |
| mother liquor 1.5 wt% KMnO4, 13 wt% KOH | D-007 | sourced (g/l ranges), density assumed | SRC-1 Description |
| cake liquid 6 wt%; product moisture 0.2 wt% | D-007 | assumed | - |
| purge 3 %; evaporator concentrate 50 wt% KOH; economy 1.8 | D-008 | assumed | - |
| KMnO4/K2MnO4 solubility in KOH liquors | D-007 | missing | - |
| impurity balance (silicate, aluminate, carbonate) | D-008 | missing | - |
| formation enthalpies and Gibbs energies | D-009 | assumed (recalled, not re-read) | SRC-7, SRC-8 |
| KOH heat of solution at 50 wt% | D-009 | missing (review #1) | - |
| heat capacities, latent heats, losses, efficiencies, auxiliaries 150 kWh/t | D-009 | assumed | - |
| backgrounds of ore, KOH, lime, fired heat, power, steam, residue, purge | D-011 | missing | lca/gaps.csv |

## D-001 Route and boundary (2026-10-28)
Decision: Two-stage manganate route as named in the case notes: MnO2 ore + KOH roasted with air
to K2MnO4 (R-201), leaching with recycled mother liquor and silicate removal with lime (M-301,
F-301), anodic oxidation of manganate to permanganate in divided cells (EL-401), cooling
crystallisation, centrifuge and steam drying (X-501, C-501, DR-501), and a mother-liquor split to
the leach, to a KOH evaporator whose concentrate feeds the roaster (E-601), and to a purge.
Overall 2 MnO2 + 2 KOH + O2 -> 2 KMnO4 + H2. Boundary: ore (dried and ground) to dried KMnO4 at
the dryer outlet; packing, storage, effluent treatment of the purge and residue disposal are
outside (as exchanges). Boundary feeds made by other library processes: none directly (KOH
would come from KCl electrolysis, which the library does not have: chlor-alkali-1 makes NaOH;
the vented hydrogen could feed hydrogen users like those of hydrogen-1's market, D-006).
Reason: this sequence is the conventional industrial process described in SRC-1 and SRC-2
(background sections), and it is the route issue #146 asks for. The roaster is chosen over the
KOH-melt liquid-phase oxidiser because the case notes name roasting and because SRC-2 reports
that liquid-phase routes need a large KOH excess (MnO2/KOH <= 1/10), which would multiply the
KOH circulation and evaporation; the roasting conditions (KOH/MnO2 2.5, 200-300 degC) follow
SRC-2's ranges.
Rejected: liquid-phase oxidation in a KOH melt (large KOH excess, see above; worth a variant);
direct electrolysis of an MnO2 slurry in KOH (SRC-3: one-step but at laboratory scale, long
batch times, unclear current efficiency); chemical oxidation of manganate with Cl2 or
disproportionation with CO2 (by-product KCl or one third of the Mn back to MnO2); the
ferromanganese anode process (needs ferromanganese, not ore).
Assumptions: continuous steady-state operation; the alternative oxidisers change R-201 only.

## D-002 Capacity and product (2026-10-28)
Decision: 1250 kg/h dried product (10 000 t/a at 8000 h/a), technical grade; the balance gives
98.9 wt% KMnO4, 0.8 wt% KOH, 0.04 wt% K2MnO4, 0.2 wt% moisture.
Reason: issue #146 gives no capacity; a per-unit-product normalisation basis for the inventory
(the LCI is per kg, so the scale only affects equipment notes). The purity results from the cake
liquid left on the crystals (6 wt%, unwashed); a cake wash on C-501 would raise it.
Assumptions: capacity and hours ASSUMED; the grade target (>= 98.5 wt%) ASSUMED, not a
specification from a standard.

## D-003 Ore (2026-10-28)
Decision: dried, ground ore with 78 wt% MnO2, 8 wt% Fe2O3, 12 wt% SiO2 (standing for all
acid-insoluble gangue) and 2 wt% moisture.
Reason: SRC-2 states ores of 70-80 % MnO2 are usable and sizes its example at 80 %; 78 % sits
inside that range. Fe2O3 and SiO2 are ASSUMED representatives of the gangue; alumina, carbonates
and other Mn oxidation states (Mn2O3, Mn3O4) are not modelled.
Assumptions: no ore assay; drying and grinding are outside the balance (their power is in the
150 kWh/t auxiliary allowance, D-009).

## D-004 Roaster (oxidation) (2026-10-28)
Decision: indirectly gas-fired rotary roaster at 523 K, atmospheric; feed KOH/MnO2 2.5 mol/mol
(concentrate from E-601 plus 50 wt% make-up); MnO2 conversion to K2MnO4 0.90 (reaction OX);
25 % of the gangue SiO2 dissolved as K2SiO3 (SIL); the KMnO4 of the recycled concentrate
reverts to K2MnO4 in the hot melt (REDKM); air at 2.0 x the O2 of OX; the cake leaves with 3 wt%
water, the rest of the water and the air leave as off-gas.
Reason: KOH/MnO2 2.5 and 200-300 degC are SRC-2's ranges; SRC-1 names roasting with air at about
225 degC as known practice. 0.90 conversion is ASSUMED below the > 95 % SRC-2 claims for its own
improved reactor (a conventional roaster is expected to do worse). Permanganate is not stable
in hot concentrated alkali (it is reduced to manganate with oxygen release), so REDKM is taken
complete. Indirect firing keeps the flue gas apart from the process gas (the flowsheet carries
no combustion products, the fired heat is a utility).
Rejected: direct firing (flue gas CO2 would carbonate the KOH to K2CO3).
Assumptions: all ASSUMED; the reaction model is a sourced-range conversion model (no
kinetics). K2CO3 formation from air CO2 is neglected (it would need a causticising step,
SRC-1 mentions one). The 1.24 MW firing duty is a lumped estimate (D-009). Materials (nickel or
nickel-lined) for hot KOH are a basic-engineering item.

## D-005 Leach, silicate removal and residue (2026-10-28)
Decision: the cake is dissolved in 79.6 % of the mother liquor plus process water at 333 K
(M-301, steam-heated); hydrated lime at 1.10 x the dissolved silicate precipitates CaSiO3 and
returns the KOH (LIME, complete); F-301 separates the residue (unreacted MnO2, Fe2O3, SiO2,
CaSiO3, excess lime) with 0.6 kg liquid per kg solids and a displacement wash with the
evaporator condensate that recovers 90 % of the solutes of the cake liquid.
Reason: SRC-2 describes dissolving the manganate in crystallisation mother liquors and lime
purification of silicates and aluminates before electrolysis; SRC-1 gives leach temperatures of
about 45-95 degC (333 K chosen). Reusing the condensate as wash water closes the water balance.
Assumptions: lime excess, cake liquid and wash recovery ASSUMED; the residue (0.39 kg/kg) goes
to landfill (D-011).
Note (review #5): the whole evaporator condensate (3779 kg/h, S11) passes F-301 while the cake
holds only ~180 kg/h liquid, about 20 cake-liquid volumes. Only a wash of 2-3 cake volumes is a
displacement wash; the rest is in effect leach dilution water routed through the filter, and the
90 % recovery stands for the combined wash and dilution. The mass balance is unaffected; in basic
engineering the excess condensate goes straight to M-301 and F-301 gets a realistic wash ratio.

## D-006 Electrolysis (2026-10-28)
Decision: 60 divided cells in series (cation-exchange membrane), 4.41 kA each, 4.41 m2 at
1000 A/m2, 2.5 V, 333 K; cell feed 6.0 wt% K2MnO4 in ~11 wt% KOH; 90 % of the K2MnO4
converted per pass (ELEC); current efficiency 0.85, the rest evolving O2 at the anode (with H2
at the cathode, WATER_SPLIT). The cathode H2 (10 kg/h) and the anode O2 (12 kg/h) are vented
separately (H2 diluted). Checked by `cheme process cell` (process/cells.yaml): DC 661.8 kW =
449.3 kW reaction enthalpy + 212.5 kW heat to cooling water; 0.499 kWh DC per kg KMnO4 formed;
thermoneutral voltage 1.735 V.
Reason: SRC-1 gives the cell window (2.0-3.5 V, 500-1500 A/m2, about 55 degC, membrane between
nickel/Monel anode and steel cathode); SRC-3 reports faster formation above 60 degC, so 333 K
sits between the two. The 2.5 V is ASSUMED inside SRC-1's range.
Rejected: undivided cells (H2 and O2 mixed, permanganate reduced at the cathode).
Assumptions: current efficiency 0.85 ASSUMED with NO open source (key open input: the DC
energy scales with 1/CE); manganate disproportionation and permanganate reduction neglected;
the catholyte loop and the water carried across the membrane (SRC-5: ~1.5-1.7 H2O per K+) are
not modelled separately (one liquor outlet). Gas streams are dry. Cell count and area are a
balance basis, not a design. Heats of reaction at 298 K (cheme notes the 333 K difference).
Electrode areas and current efficiency (review #2): the 4.41 m2 per cell at 1000 A/m2 is the
**cathode** area, because SRC-1's 500-1500 A/m2 is a cathode current density. The anode area is
not set: the current efficiency depends on the anode current density against the manganate
mass-transfer limit, and the anolyte leaves at only 0.6 wt% K2MnO4 (S14) after 90 % conversion
per pass, so the anode must run at a much lower current density than the cathode (an expanded
anode several times the cathode area, ASSUMED design direction, no source). CE falls as the
per-pass conversion rises; CE 0.85 together with 90 % per pass is optimistic. Sensitivity of the
AC electricity per kg KMnO4 (rectifier 0.546 x 0.85/CE, auxiliaries 0.150 unchanged, voltage
2.5 V):

| CE | rectifier AC, kWh/kg | total electricity, kWh/kg |
|---|---|---|
| 0.60 | 0.774 | 0.924 |
| 0.70 | 0.663 | 0.813 |
| 0.80 | 0.580 | 0.730 |
| 0.85 (base) | 0.546 | 0.696 |
| 0.90 | 0.516 | 0.666 |

A lower CE also raises the cell heat to cooling water and the anode O2/cathode H2 (WATER_SPLIT);
the LCI keeps the base case.

## D-007 Crystallisation, centrifuge and drying (2026-10-28)
Decision: the cell liquor is cooled from 333 to 303 K in X-501; the mother liquor leaves with
1.5 wt% KMnO4 and 13 wt% KOH; C-501 delivers crystals with 6 wt% liquid (no wash); DR-501 dries
to 0.2 wt% moisture with LP steam.
Reason: SRC-1 cools its crystalliser to about 30-50 degC and gives likely mother-liquor
contents of 15-20 g/l KMnO4 and 125-175 g/l KOH (1.5 and 13 wt% at an ASSUMED density near
1.15 kg/l). KMnO4 is a single component whether dissolved or crystalline; the crystal amount is
what exceeds the mother-liquor content (scripts/kmno4_balance.py).
Rejected: the core crystalliser (`crystallizer:`): it models one solute in one
solvent and refuses KOH-K2MnO4-KMnO4 liquors (checked in chemeascode/domains/process/
crystallization.py: "impurities and several solutes" are refused), so a solubility-equilibrium
basis is not available; the crystalliser is a specified (imposed mother-liquor composition)
step.
Assumptions: cake liquid, moisture ASSUMED; KMnO4 solubility in KOH liquor is taken from the
SRC-1 operating range, not from solubility data (the pure-water solubility does not apply,
common-ion effect).
In-cell crystallisation (review #4): the cell liquor S14 carries 5.5 wt% KMnO4 at 333 K in
12.5 wt% KOH, more than the 1.5 wt% at 303 K of the mother liquor, and process/cells.yaml notes
that KMnO4 partly crystallises already in the anolyte. The flowsheet carries all of it dissolved
to X-501 and charges the whole crystallisation heat to Q6 (crystalliser cooling) instead of
partly to Q5 (cell cooling). The split between Q5 and Q6 is open until solubility data for KMnO4
in KOH liquors at 333 K are cited; the sum of the two duties is unaffected.

## D-008 KOH recovery, purge and make-up (2026-10-28)
Decision: the mother liquor is split 79.6 % to the leach, 17.4 % to the double-effect KOH
evaporator (concentrate 50 wt% KOH to the roaster, condensate to the residue wash) and 3 % to a
purge to effluent treatment; the KOH make-up (50 wt% solution, 0.92 kg/kg product) equals the
potassium leaving with product, residue and purge.
Reason: the evaporator share is what gives the roaster its KOH/MnO2 of 2.5 (D-004); a purge is
needed to bleed soluble impurities (SRC-1 lists 30-75 g/l soluble impurities in its mother
liquor and splits it into direct recycle, causticising and evaporation).
Assumptions: purge fraction ASSUMED (it carries 0.091 kg free KOH per kg product, against a net
chemical demand of 0.355 kg and a make-up of 0.460 kg, and 11 % of the Mn loss); impurity build-up is not tracked (no impurity
species), so 3 % is a placeholder until an impurity balance exists; causticising of K2CO3
(SRC-1) is not included because K2CO3 is not formed in this model (D-004).
Basic-engineering item (review #6): the evaporator concentrate S4 carries 5.8 wt% KMnO4 in
50 wt% KOH at 413 K. The permanganate reduction assigned to the roaster (REDKM, D-004) will
already start in E-601: O2 in the vapour, manganate and MnO2 deposits (fouling) on the heating
surfaces. No effect on the Mn balance (the Mn reaches the roaster as manganate either way), but
the evaporator materials, the fouling allowance and whether permanganate should be crystallised
out before evaporation are open for basic engineering.

## D-009 Energy, utilities and thermochemical data (2026-10-28)
Decision: duties from a lumped enthalpy balance in scripts/kmno4_balance.py: roaster
evaporation (2257 kJ/kg plus sensible heat) and heating of cake and air to 523 K less the heats
of OX and REDKM, with 15 % losses -> 1.24 MW fired heat; leach heating to 333 K including the
KOH dissolution heat (-57.6 kJ/mol) -> 0.68 MW LP steam; crystalliser 333 -> 303 K (cp 3.4
kJ/(kg K), crystallisation heat 43.56 kJ/mol) -> 0.96 MW cooling water; evaporator 2400 kJ/kg
vapour at an economy of 1.8 -> 1.40 MW LP steam and the same to cooling water; dryer 2600 kJ/kg
water at efficiency 0.65 -> 72 kW; rectifier efficiency 0.97; auxiliaries 150 kWh/t.
Utilities: LP steam 450 kPa(a), cooling water 298/308 K, natural gas firing, grid power.
Thermochemical data: standard formation enthalpies and Gibbs energies at 298 K from the NBS
tables (SRC-7) as recalled; heat of ELEC 334.9 kJ per 2 mol K2MnO4 (aqueous ions), reversible
cell voltage 1.38 V; heat of OX -112.7 kJ per 2 mol MnO2 (solids, water vapour).
Reason: no property package covers concentrated KOH-manganate electrolytes, KOH melts or the
solids (D-010), so core cannot close the energy balance; a lumped estimate is the honest
concept-stage substitute.
Assumptions: every heat capacity, latent heat, efficiency, loss and the auxiliary allowance is
ASSUMED; the NBS values must be checked against the table; pressures and temperatures in the
stream table are concept values.
Known inconsistency, open (review #1): the KOH enters as 50 wt% solution (S2, S4) while the
OX/REDKM heats use KOH(s), and the leach credits the KOH(s) dissolution heat. The heat to
separate KOH from its 50 wt% solution in the roaster, and the differential heat of
concentrating 13 -> 50 wt% in E-601, are not charged. The reviewer estimates Q1 understated by
roughly 0.25-0.35 MW (fired heat ~1.25 instead of 0.99 kWh/kg). Not corrected yet: it needs a
sourced integral heat of solution of KOH at both concentrations, which this run could not read.

## D-010 Thermodynamic and method selection; core dependencies (2026-10-28)
Decision: liquors carried as neutral molecules, no property package (`property_method`
placeholder); reactors as conversion models with element balances checked by cheme; the cells
by `cheme process cell` (specified performance); separators and the crystalliser as specified
stream values from the independent balance.
Method/dependency status at cheme-as-code 0.8.0 (installed in this run, checked in its code and
command help; the core issues themselves were not re-read):

| method | core status for this route | effect here |
|---|---|---|
| electrochemical cell balance | supported: Faraday, charge, element and energy balance with specified voltage and current efficiency (`cheme process cell`) | used, closes; CE and voltage remain inputs |
| solid-reaction / furnace energy | `cheme process furnace` covers lime kilns and calciners (calcination of CaCO3); other solid reactions are refused | not applicable to MnO2-KOH roasting: roaster energy is the lumped D-009 estimate (gated) |
| electrolyte speciation | `cheme process electrolyte` supports aqueous NaCl only | KOH-K2MnO4-KMnO4 liquors not covered: no activity, density or enthalpy; line sizing and energy closure gated |
| crystalliser / solid separation | one solute in one solvent (`crystallizer:`), or a specified filter/centrifuge | crystalliser refuses the multi-solute liquor; X-501/C-501 stay specified (`imposed` composition) |
| DWSIM simulation | no package for these electrolytes and solids | not run (process/simulation.yaml not written) |

Reason: the case's chemistry (alkaline manganese electrolytes, melts, solids) is outside every
benchmarked property package of core; issue #146 allows a sourced conversion/recovery model at a
lower declared target.
Assumptions: calculation maturity stays below `sourced screening` (cheme maturity: none, as for
soda-ash-1): feed flows are not "given with a source" and every conversion is assumed.

## D-011 Preliminary gate-to-gate LCI (2026-10-28)
Decision: functional unit 1 kg dried KMnO4 at the dryer outlet; `boundary: cradle-to-gate` with
every background declared `missing:` (a gap, never 0), as soda-ash-1 and asu-1 do; no
allocation (one product; H2 vented); roaster air and the N2, O2 and H2O returned to air free;
H2 vented as an elementary emission to air (no GWP100 factor: a gap "outside the method").
Exclusions declared in lca.yaml: purge discharges (belong to the effluent treatment
background), roaster combustion (indirect firing, emissions in the fired-heat background),
leach-tank breathing (no volatile species). Not estimated and not declarable in the schema (no
dust method): KOH/Mn dust of the roaster off-gas after its scrubber and KMnO4 dust of the dryer
exhaust (open item). lca/mappings.yaml only sets the utility unit conventions of the Atlas
build (steam and fired heat as kWh heat, process water by mass); ore, KOH, lime, residue and
purge stay unmapped (gaps).
Result (`cheme assess lca --coverage`): mass, element and carbon-origin balances closed;
partial screening carbon footprint with 11 gaps and no total; DQR 2.33.
Assumptions: construction, transport and end of life not included; the flows inherit every
ASSUMED parameter above.

## Key results per kg KMnO4 (design case, from process/flowsheet.yaml)

| exchange | per kg | stream / energy stream |
|---|---|---|
| manganese ore (78 % MnO2) | 0.787 kg (0.614 kg MnO2) | S1 |
| KOH make-up, 50 wt% | 0.920 kg (0.460 kg KOH) | S2 |
| hydrated lime | 0.032 kg | S7 |
| process water | 1.313 kg | S9 |
| air | 0.877 kg | S3 |
| electricity (AC) | 0.696 kWh (0.546 rectifiers, 0.150 auxiliaries) | Q2, Q11 |
| fired heat (natural gas) | 0.991 kWh = 3.57 MJ | Q1 |
| LP steam heat | 1.722 kWh = 6.20 MJ | Q7, Q8, Q10 |
| cooling water (heat rejected) | 2.076 kWh = 7.47 MJ | Q4, Q5, Q6, Q9 |
| leach residue (wet) | 0.390 kg | S12 |
| mother-liquor purge | 0.703 kg | S23 |
| H2 vented | 0.0080 kg | S15 |

Mn to product 88.6 %, K to product 76 % (theory 0.550 kg MnO2 and 0.355 kg KOH per kg KMnO4).

## Open inputs and gated steps
- Current efficiency and cell voltage of industrial manganate cells (open source needed; Ullmann
  SRC-6 and the full text of SRC-5 to audit). DC energy scales with V/CE.
- Roaster: conversion, energy use and off-gas dust for a real kiln or liquid-phase oxidiser;
  core furnace model does not cover this reaction (gated).
- KMnO4 and K2MnO4 solubility in KOH liquors (for a solubility-based crystalliser: core's solids support
  supports one solute only) and electrolyte properties for energy closure and line
  sizes.
- Impurity balance (soluble silicates, aluminates, carbonate) to set the purge.
- Ore assay; KOH make-up grade; effluent treatment route of the purge; residue disposal route.
- NBS formation data to be re-checked against the table (D-009).
- Plot plan (concept gate `layout-plot-plan`): deferred to basic engineering. This case's scope
  (issue #146) ends at the balanced PFD and the preliminary LCI, so the gate fails on purpose
  until a site plan and placement are added (review #13).
- Registry entries missing in `chemicals/chemicals.yaml` (for the consolidated PR): potassium
  permanganate (main product), manganese ore / manganese dioxide, potassium hydroxide (50 wt%
  solution grade), calcium hydroxide (hydrated lime); a shared `lci/mappings.yaml` vocabulary
  for those three raw materials and for an alkaline Mn-bearing effluent and residue.
