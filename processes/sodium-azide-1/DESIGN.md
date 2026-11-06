# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Sodium azide (NaN3) by the hydrazine / methyl nitrite route, issue
ChemE-as-Code/process-library#167, a batch entry after n-bromosuccinimide-1 (#140) and
phosphorus-tribromide-1 (#134), whose pattern it follows (library ADR 0035). Concept stage:
design basis, batch recipe with the reactors' vessels and jackets and the filter-dryer, balanced
BFD/PFD with the mother-liquor and methanol recycles, thermal screening and a preliminary
gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-11-05): library `main` at fcde3262; cheme-as-code core main 7334d7c,
rechecked on the release **1.8.0** (4e8fd80), with the batch work-up of core#165: gas vents
and gas dosing (ADR 0054), the batch still (ADR 0055), precipitation from a mixed liquor (ADR
0056) and the filter-dryer with recipe units over several steps (ADR 0057).
Rechecked (2026-11-06) on core **1.9.0** (314642c), which the library now pins: propagate
converges the two recycles at declared tear streams (ADR 0060, D-006), the batch models write
their duties (ADR 0059, D-012), and the screening takes the MTT of what boils and gives the gas
release at the MTSR against a stated vent capacity (ADR 0058, D-011, D-017). The folder uses all
three, so it requires 1.9 (see "Core features used").

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text, which has no column numbers, so the locator is the
part of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US 5 208 002 A, M. Sasaki, H. Shibafuchi, Y. Imai, M. Yoshida, K. Miyata (Nippon Carbide Industries), 1993-05-04: Method of producing alkali metal azides; family EP 0 514 143 B1, priority JP 1991-05-17; https://patents.google.com/patent/US5208002A/en | description and claims: hydrazine (anhydrous or hydrate, preferably 50 wt% or more) with 1-1.5 mol NaOH per mol in water, an alkyl nitrite gas absorbed at 0-80 C (preferably 20-50 C), the hydrazine conversion held at 50-90 % (examples 70 %); above 90 % the nitrite attacks the azide (nitrogen and nitrite by-products), selectivity and purity fall (comparative example: 98 % conversion, 75 % selectivity); NaOH below 1 mol per mol hydrazine or above 4 mol gives side reactions; water content at the end at least 50 % (80-90 % most preferred, on water plus alcohol); the alkyl nitrite made in a separate vessel. Example 1: 47.5 mol NaNO2 as 35 wt% solution with 47.6 mol methanol, 23.8 mol H2SO4 as 50 wt% acid pumped in at 25 C over 8 h, the methyl nitrite gas passed into 74.0 mol NaOH (35 wt%) and 61.8 mol hydrazine (51.2 wt%) at 30 C, 1 h more; 42.8 mol methanol distilled as a 90 wt% cut, the liquor concentrated under reduced pressure to about a third of its volume, centrifuged: 2.44 kg wet crystals (95 wt%), 3.3 kg filtrate (Table 1: 18.2 mol hydrazine, 32.9 mol NaOH, 5.5 mol NaN3), vacuum-dried at 60 C: 2.32 kg NaN3, 99.8 %, 82.4 % on hydrazine consumed. Example 2 (Table 2): the filtrate recycled 11 times with 43.2 mol fresh hydrazine and 51.0 mol fresh NaOH per batch and the recovered methanol to the nitrite vessel; 41.0 mol NaN3 per steady batch; 444.2 mol NaN3 (99.5 %) from 493.8 mol hydrazine, 90.0 %. Example 3: about 20 mL methanol wash on 36.4 g product, 95 % selectivity at 70 % conversion | read; patent, facts only | D-001, D-004, D-005, D-007, D-008, D-009, D-016, benchmark |
| SRC-2 | US 5 098 597 A, E. F. Rothgery, D. F. Gavin, K. A. Thomas (Olin), 1992-03-24: Continuous process for the production of azide salts; https://patents.google.com/patent/US5098597A/en | claims 1 and 4: a continuous process, a C1-C3 alkyl nitrite gas made from an alkanol in a first reactor and fed below the surface of the hydrazine / hydroxide solution in a second, which is replenished with hydrazine and hydroxide; detailed description: the two reactors keep the first reactor's acid from the azide mixture, so that little or no hydrazoic acid forms; Example 1: ethanol and ethyl nitrite, the azide filtered off continuously and the filtrate replenished and recycled, 49 g NaN3 over about 8 h, 75.4 % overall | read (2026-11-06); patent, facts only | D-001, D-015 |
| SRC-3 | J. Studley, "Sodium Azide - Sonic Boom Boy", Scientific Update, 12 March 2023, https://www.scientificupdate.com/?p=23740 | the Wislicenus route: sodium amide from molten sodium and ammonia at about 350 C, then N2O at about 230 C, with water a serious hazard; residual azide destroyed with nitrous acid (from nitrite and acid); azide in waste pipes forms shock-sensitive metal azides, copper in particular, with explosions when blocked drains were cleared | read (2026-11-06); secondary source, facts only | D-001, D-015 |
| SRC-4 | Perrott, J. R.; Stedman, G.; Uysal, N., J. Chem. Soc., Dalton Trans. 1976, 2058 (nitrosation of hydrazine) | the N-nitrosohydrazine intermediate gives HN3 at high acidity, ammonia and N2O at low acidity | abstract seen in a web search only, not read (the publisher refused access) | D-005, a lead only |
| SRC-5 | chemicals and thermo packages of core's environment (open-source, MIT): CRC Handbook tables as packaged, ATcT, NIST WebBook / JANAF, estimates, and thermo's correlations, some of which (DIPPR_PERRY_8E) take their coefficients from Perry's Chemical Engineers' Handbook, 8th ed. (a licensed book drawing on the DIPPR 801 database; not read here; whether values computed from them may be published is a library-wide question for the maintainers) | printed per component in process/materials.yaml and process/reactions.yaml: formation enthalpies, liquid densities and heat capacities, solid densities, boiling points, heats of vaporization | open-source packages queried; facts only | D-005, D-006 |
| SRC-6 | NIST Chemistry WebBook, SRD 69, https://webbook.nist.gov/ | Antoine parameters: water 255.9-373 K (Stull 1947), methanol 288.1-356.83 K | read (web page and `cheme chemistry props --source NIST`) | D-007 |
| SRC-7 | PubChem CID 33557 (sodium azide), CID 948 (nitrous oxide); EBI OLS ChEBI 278547, 17045 | identity (formula, InChIKey) | read (PUG REST, OLS API) | chemicals registry |
| SRC-8 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | the accumulation and MTSR of a semi-batch and the criticality classes (method, implemented in core ADR 0050) | method reference, no data taken | D-011 |
| SRC-9 | processes/sodium-nitrite-1, sulfuric-acid-1, hydrazine-1, chlor-alkali-1, methanol-1, asu-1 (this library) | the feeds' grades: dried NaNO2 99.0 wt%, H2SO4 98.5 wt%, hydrazine hydrate 64 wt% N2H4, caustic soda 50 wt%, Grade AA methanol, gaseous nitrogen | library, internal | D-004, D-013 |
| SRC-10 | Ullmann's Encyclopedia of Industrial Chemistry, Azides (doi:10.1002/14356007.a13_193.pub2) | - | not read (licensed); named by the route scouting only | - |

Searched and not found openly (2026-11-05): kinetics or reaction calorimetry of the methyl
nitrite-hydrazine reaction or of the nitrite generation; a TD24 of the azide liquor, the
mother liquor or dry NaN3; the solubility of NaN3 in caustic hydrazine liquors other than the
patent's one filtrate; the heats of solution in these liquors; a plant's specific consumptions,
off-gas or wastes; a market volume.

## D-001 Route and boundary (2026-11-05)
Decision: the hydrazine / alkyl nitrite route of SRC-1 with methyl nitrite: NaNO2 + CH3OH +
1/2 H2SO4 -> CH3ONO (gas) in R-101, absorbed into N2H4 + NaOH in water in R-102 (N2H4 + CH3ONO +
NaOH -> NaN3 + CH3OH + 2 H2O); methanol stripped and the liquor concentrated under vacuum in
C-101, NaN3 precipitated from the concentrated liquor, filtered, washed with methanol and dried
in the filter-dryer F-101, the mother liquor and the methanol recycled. Dedicated train (D-014).
Boundary feeds: sodium nitrite, sulfuric acid, hydrazine hydrate, caustic soda, methanol make-up,
process water, nitrogen (per batch), electricity, LP steam; returns: chilled and cooling water;
outputs: dried NaN3, the sodium sulfate liquor, the evaporator condensate, the mother-liquor
purge (to azide destruction) and R-102's off-gas (to the thermal oxidiser).
Reason: the best-documented open route (SRC-1 gives charges, conversions, the filtrate's
composition and an 11-batch recycle), and every feed has a library producer (sodium-nitrite-1,
sulfuric-acid-1, hydrazine-1, chlor-alkali-1, methanol-1). It runs batchwise in the patent. The
nitrite vessel apart from the azide vessel keeps acid away from the azide (SRC-1, SRC-2), so the
azide never meets acid; hydrazine carried in the recovered methanol would still form hydrazoic
acid in R-101, so the methanol has a hydrazine limit (D-015).
Rejected: the Wislicenus route (molten sodium amide with N2O at about 230 C, SRC-3): it needs
sodium metal (no library entry), gas-melt reactions that core cannot model, and molten sodium
with ammonia at about 350 C, where any water is a serious hazard. Ethyl nitrite in ethanol (SRC-2): the same chemistry; the patent with the open
batch figures uses methanol. Acidifying to HN3 and distilling it (the prior art SRC-1 names):
dangerous. Continuous operation (SRC-2): a candidate variant (`sodium-azide-2`); the issue asks
for the batch entry.

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 670.6 t/a dried NaN3 (84.68 kg/h year average), 7920 h/a (330 days of 24 h), ASSUMED.
Product in the model: 99.6 wt% NaN3 (99.55 % crystals, 0.06 % from the dried cake liquor), NaOH
0.20, hydrazine 0.09, methanol 0.09, water 0.01 wt%.
Reason: no open market or plant figure was found; NaN3 is now a speciality (tetrazole and
pharmaceutical syntheses, preservatives), no longer the airbag commodity. The scale follows from
the batch the jacket allows (D-010). The LCI is per kg and does not depend on the scale.
Open: the product specification (assay, NaOH, hydrazine, heavy metals, particle size).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 1027.6 kg of dried NaN3 (stream S26); `process/recipe.yaml` has four
unit procedures, one per vessel:
- GENERATE on M101+R101 (R-101): charge 1 h, the acid dose 10 h and the post-reaction 0.53 h
  from R101's model, drain 0.5 h: 12.03 h;
- AZIDE on M102+R102 (R-102), started with GENERATE's charge (`start.after`) so that the methyl
  nitrite flows while it forms: charge 1 h, the absorption 10 h and the post-reaction 0.64 h from
  R102's model, transfer 0.5 h: 12.14 h, the bottleneck;
- CONCENTRATE on ST101+X102+CR101 (C-101): receive 0.5 h, distil 4.52 h from ST101's model, cool
  and crystallise 2 h, transfer 0.5 h: 7.52 h;
- ISOLATE on F101+W101+F102+D101 (F-101, recipe `units:`, core ADR 0057): receive 0.5 h, filter
  3.12 h (Ruth, from F101), reslurry wash 0.5 h, filter 0.11 h (F102), dry 3.76 h (D101's drying
  rate on the vessel's heated area), discharge 1 h: 9.0 h.
Cycle 12.14 h, 652.6 batches in 7920 h; one batch takes 27.65 h from the charge to the
discharge. The flowsheet holds the year averages: 1027.6 kg x 652.6 / 7920 h = 84.67 kg/h of
S26 against 84.68 kg/h in the flowsheet (no `cheme.recipe-basis` finding). Per batch: 1256 kg
NaNO2, 908 kg acid, 854 kg hydrazine hydrate, 1322 kg caustic soda 50 %, 76 kg fresh methanol,
1684 kg recycled mother liquor.
Vessels (core ADR 0052, fill 0.8, H/D 1.2 ASSUMED): R-101 4.54 m3 of liquor in 6.3 m3; R-102 5.71
m3 in 8 m3; F-101 sized by the recipe from the slurry and cake (ADR 0057, H/D 0.8): 1.51 m3 in
2 m3, heated area 4.36 m2. C-101 is not sized (core sizes no still, ADR 0055): about 6.2 t of
charge per batch.
No rinse between batches: the train is dedicated and the azide side stays alkaline (an aqueous
rinse would add an azide effluent); hence no rinse consumable.

## D-004 Feeds and charge ratios (2026-11-05)
Decision, from SRC-1 Example 1 (the charges per mol hydrazine of R-102's charge):
- NaOH 1.20 mol (74.0 on 61.8 mol), water 6.63 mol (the water of its 35 wt% caustic and 51.2 wt%
  hydrazine), so that the fresh caustic, hydrazine hydrate and water top the recycled mother
  liquor up to these ratios;
- sodium nitrite 0.769 mol (47.5 on 61.8 mol); per mol of nitrite, 1.002 mol methanol (47.6 on
  47.5), 0.501 mol H2SO4 (23.8 on 47.5) and 9.84 mol water (the water of the patent's 35 wt%
  nitrite solution and 50 wt% acid);
- 91.8 % of the methyl nitrite absorbed and reacted (`dosing.absorbed: 0.918`): Example 1's
  balance accounts for 43.6 mol of the 47.5 mol nitrite in the hydrazine consumed (61.8 - 18.2
  mol), and the NaOH consumed (41.1 mol) equals the NaN3 found (35.6 + 5.5 mol); the other 3.9 mol
  are not accounted for and are taken as leaving unabsorbed with R-102's off-gas (ASSUMED);
- feeds at 298 K: dried NaNO2 (sodium-nitrite-1, 100 % in the model) dissolved in R-101's charge;
  98.5 % acid (sulfuric-acid-1) dosed, with the water of the patent's 50 % acid in the charge
  instead (ASSUMED: one dosed stream; the dilution heat then arises in R-101, which the
  pure-acid heat of reaction counts, D-005); hydrazine hydrate 64 wt% N2H4 (hydrazine-1) instead
  of the patent's 51.2 %, with the difference in the water; caustic soda 50 wt% (chlor-alkali-1)
  instead of 35 %, the same; Grade AA methanol (methanol-1) as the make-up.
Result: the hydrazine conversion per batch is 70.5 % (the patent's 70 %), the water content at
the end (water over water and methanol, the patent's measure) 78 % (the patent's 86.4 %: the
recycled wash methanol adds methanol; the patent prefers 70-95 %).
Reason: the example is the one open set of quantities.

## D-005 Reactions, heats and kinetics (2026-11-05)
Decision (`process/reactions.yaml`):
- NTG, 2 NaNO2 + H2SO4 + 2 CH3OH -> 2 CH3ONO + Na2SO4 + 2 H2O, -82.75 kJ per mol of reaction
  (-41.4 kJ/mol CH3ONO); AZ, N2H4 + CH3ONO + NaOH -> NaN3 + CH3OH + 2 H2O, -339.7 kJ/mol; SIDE,
  N2H4 + CH3ONO -> N2O + NH3 + CH3OH, -178.5 kJ/mol. The heats are pure-substance standard-state
  values from chemicals (SRC-5; hydrazine as its liquid hydrate (ATcT), methyl nitrite, N2O and NH3
  as gases, the salts solid). The heats of solution are not counted: no open values were read in
  this session; for AZ they would lower the heat by about 15-20 % (NaOH dissolves exothermically,
  NaN3 endothermically), so the declared value is conservative for the screening and the jacket;
  for NTG they are of the same order as the heat itself, which is small.
- SIDE stands for the 5 % selectivity loss on hydrazine that consumes no NaOH (D-004). The
  products are ASSUMED from the low-acidity path of hydrazine nitrosation (SRC-4, a lead only);
  the patent names only nitrogen and nitrite at conversions above 90 %, where the nitrite attacks
  the azide (not modelled: the design stays at 70 %).
- Rate laws, all ASSUMED (no open kinetics, searched 2026-11-05): NTG second order in dissolved
  nitrite and acid, k 0.05 m3/(kmol s) at 298 K, Ea 50 kJ/mol; AZ second order in dissolved
  hydrazine and methyl nitrite, k 1.0e-3 m3/(kmol s) at 313 K (about 4 min half-life of the
  dissolved methyl nitrite at the charge's hydrazine), Ea 60 kJ/mol; SIDE AZ's law at 0.05/0.95
  of its constant, which holds the selectivity at 95 %.
- R-101 isothermal at 298 K (SRC-1: 25 C), the acid dosed over 10 h, then to 0.999 conversion of
  the nitrite; R-102 isothermal at 313 K (within the patent's 20-50 C; the examples 30-40 C), the
  methyl nitrite dosed over the same 10 h, then to 0.999 conversion of the dissolved methyl
  nitrite. The vents (core ADR 0054): methyl nitrite leaves R-101 whole as it forms (bp 261 K);
  N2O and NH3 leave R-102 whole as they form (ASSUMED for NH3, which is very soluble in water: the
  strongly caustic liquor and the gas flow through it strip it; the share left would go with the
  methanol cut).
- The 0.1 % of the dissolved methyl nitrite left at the end of R-102 is carried through the
  work-up as a non-volatile trace (0.02 wt% in the liquor): in the plant it desorbs in the still
  to the vent (L-2).
**The low accumulation of D-011 is a consequence of the assumed rate laws** and must be
confirmed by reaction calorimetry (heat flow and gas uptake during the dosing).

## D-006 Balance method, pseudo-components and the recycles (2026-11-05, recycles 2026-11-06)
Decision: every unit is calculated by `cheme process propagate`: the semi-batches
R101 and R102 with their vents, the still ST101, the crystallizer CR101, the filters F101 and
F102, the dryer D101, the mixers and the splitters' remainders. No balance script.
The liquors are molecular pseudo-components (NaNO2, H2SO4, Na2SO4, NaOH, hydrazine and NaN3
dissolved), as in n-bromosuccinimide-1: no property package of core covers these electrolyte
liquors. Their liquid volumes and heat capacities are the solids' or the liquids' (SRC-5,
ASSUMED for the dissolved salts).
The two recycles are the tear streams of the flowsheet's `tears:` (core 1.9.0, ADR 0060): the
mother liquor S11 (X101's recycle, `split: {recycle: 0.95}`, D-016) to R-102's charge and the
recovered methanol S3 (X102) to R-101's charge. Every loop of the flowsheet runs through one of
them (the cake wash S18 -> W101 -> F102 -> M103 -> S11 too), so each loop is torn once.
Propagate iterates them by Wegstein's method from first guesses (the earlier hand estimates,
rounded to three digits) to 1e-6 kg/h + 1e-9 relative per component, far tighter than the
balances' tolerance (0.02 kg/h + 0.001): a loop stops within tolerance / (1 - gain) of its fixed
point, and a first run at 1e-4 kg/h + 1e-6 (21 iterations) left that error in the last of the six
digits written (S17's mole fractions then summed to 1.000001, beyond the PFD's 1e-6 check); at
1e-6 kg/h the digits written are the fixed point's. 32 iterations, worst residual 7.1e-7 kg/h
(S11's total; `cheme.process-recycle`, info), about 14 s for propagate. S11's flow
and composition and S3's composition are `calculated`; S3's flow stays ASSUMED, the charge ratio
of 1.002 mol methanol per mol nitrite (D-004), and the iteration holds it fixed.
The fresh feeds that follow the charge ratios of D-004 (S1, S2, S8, S9, S10, S22) stay ASSUMED at
the values set at the hand-converged recycle: core has no design specification on a feed (ADR
0060, core#181 part 2). At the converged recycle the ratios hold to 1e-4: NaOH 1.2001 and water
6.6307 mol per mol hydrazine of the charge, nitrite 0.76906 mol per mol hydrazine, methanol
1.0020 mol per mol nitrite.
Until 1.9.0 the tears were ASSUMED values converged by hand (successive substitution over
`propagate --fill` with a scratch driver outside the folder, to 3e-5 kmol/h, L-1). Against that,
no stream's flow moved by more than 0.004 % (S18, the wash methanol) and the product S26 went from
84.677 to 84.6771 kg/h. A change to an upstream value now makes the tears stale, and `propagate
--fill` converges them again.

## D-007 Methanol strip and concentration in the batch still C-101 (2026-11-05)
Decision: ST101 is a batch (Rayleigh) still at 10 kPa(a) with two cuts (core ADR 0055): the
methanol cut until 0.05 mol% methanol is left (1075 kg per batch, 88.4 wt% methanol, 0.76 h), then
water until 63 % of the charge's mass is distilled (2858 kg per batch, 99.9 wt% water), at a
constant boil-up of 500 kW (LP steam, ASSUMED): 4.52 h, 2260 kWh per batch. Hydrazine, NaOH, NaN3
and the trace of methyl nitrite are non-volatile.
- Volatility: a constant relative volatility of methanol to water of 150 (ASSUMED), chosen so that
  the first cut is about the patent's 90 wt% (SRC-1 Example 1). An ideal one-stage still with the
  NIST Antoine data (SRC-6, kept in materials.yaml) gives a first cut of only about 20 mol%
  methanol (a trial run): the patent's cut needs a short column and reflux, and the salting-out
  of methanol by the caustic liquor, neither of which core's one-stage ideal still models (L-3).
  The 150 stands for both and is not a property.
- Hydrazine is taken as non-volatile: it boils at 387 K, forms a maximum-boiling azeotrope with
  water and is held by the caustic liquor; the patent's filtrate holds the hydrazine its
  balance leaves (61.8 - 43.6 = 18.2 mol, Example 1), so none went with the distillates.
  ASSUMED; a hydrazine loss to the condensate would add to the wastewater's load.
- The end of the water cut, 63 % of the charge's mass, is set so that the mother liquor is the
  composition of the patent's filtrate, the basis of the solubility (D-008): 39.0 wt% NaOH, 17.4
  wt% hydrazine, 10.8 wt% NaN3, 32.5 wt% water against the patent's 40.0, 17.7, 10.8 and 31.5
  wt%.
- The residue leaves at about 360 K (S17), ESTIMATED: the constant-volatility still gives no
  temperature (L-4). An ideal Raoult trial run gave 335 K at 10 kPa(a), but it counts NaOH as one
  molecular particle and misses the caustic liquor's boiling-point elevation. At the end the
  liquor holds 54.5 wt% NaOH on a NaOH-plus-water basis; a 50 wt% NaOH solution alone boils about
  40 K above water (Duhring lines of NaOH solutions, about 415 K at 1 atm), so at 10 kPa(a), where
  water boils at 319 K, the residue boils at about 355-370 K; 360 K is taken. The patent
  concentrates at 40 C or below in Example 4 and warns that heat lowers the azide's stability in
  solution: the design is well above that. A lower pressure does not reach it either: the
  elevation stays, so even 2-3 kPa(a) (water at 290-297 K) ends at about 325-340 K, and the water
  cut would then need a refrigerated condenser instead of cooling water. Kept: 10 kPa(a), with
  C-101 heated by tempered hot water (at most about 390 K, from LP steam, as F-101) instead of
  steam on the wall (412 K), and the hot concentrated azide / hydrazine liquor an open
  reaction-hazard item (D-011, D-015).
- The methanol cut is condensed on chilled water (Q4) and goes to R-101 (S3, 1.002 mol per mol
  nitrite) and the rest to the cake wash (S18); the water cut is condensed on cooling water (Q5)
  and goes to wastewater treatment (its reuse as process water is open).

## D-008 Precipitation from the concentrated liquor (CR101) (2026-11-05)
Decision: CR101 is a crystallizer at 303 K (core ADR 0056), NaN3 from water with the spectators
hydrazine, NaOH, methanol (none left) and the methyl nitrite trace; basis solubility, a single
value measured in the mother liquor: 0.1084 mass fraction NaN3, the patent's filtrate (SRC-1
Example 1, Table 1: 5.5 mol NaN3 in 3.3 kg). The patent does not state the temperature of its
centrifugation; 303 K is ASSUMED. The still is stopped where the mother liquor has the
filtrate's composition (D-007), so the value is used at the liquor it was measured in; core does
not check that (L-6). 84.3 kg/h of crystals form (87 % of the NaN3 in the liquor); the rest stays
in the mother liquor and is recycled (D-016).
Energy (lumped, ASSUMED): heat capacity 2.8 kJ/(kg K) of the liquor, heat of crystallization
-200 kJ/kg (about -13 kJ/mol; no open value read): 13.1 kW year average to cooling water (Q6),
the liquor cooled from the still's estimated 360 K (D-007).
Rejected: the phase change as a conversion "reaction" (the NBS pilot's workaround, its L-2): core
now models it, and the screening no longer counts it.

## D-009 Filter-dryer F-101: filtration, methanol wash, drying (2026-11-05)
Decision: an agitated Nutsche filter-dryer (one vessel, the recipe's `units:`):
- F101: 99.8 % of the crystals to the cake, the cake holds 5 wt% mother liquor (the patent's
  centrifuged crystals, 95 wt%), ASSUMED; Ruth's filtration time (core ADR 0057) with a specific
  cake resistance of 1e9 m/kg, a cloth of 1e10 1/m, 200 kPa of nitrogen, a liquor of 15 mPa s and
  1500 kg/m3, all ASSUMED: 3.1 h on the 1.7 m2 plate (with 1e10 m/kg, 29 h: the resistance must
  be measured);
- W101: a reslurry wash with 0.43 kg methanol per kg of product (SRC-1 Example 3: about 20 mL on
  36.4 g), the recovered methanol cut S18 topped up with fresh methanol S22; a mixer, so no NaN3
  dissolves in the wash (NaN3 is slightly soluble in methanol; not modelled, L-8);
- F102: as F101 with the methanol (0.7 mPa s, 830 kg/m3): 0.1 h;
- D101: vacuum drying at 333 K (the patent's 60 C) to 0.1 wt% water and methanol, ASSUMED; the
  dryer's energy (core ADR 0057): the cake's heat capacity 1.3 kJ/(kg K), latent heats 2358 (water,
  IAPWS) and 1132 kJ/kg (methanol, thermo), 8 t of steel at 0.5 kJ/(kg K) heated each batch, 70 %
  efficiency, all ASSUMED: 8.26 kW year average (Q7, checked by the dryer's energy port); drying
  time from a mean rate of 3 kg/(m2 h) (ASSUMED) on the recipe vessel's 4.36 m2: 3.8 h. The vapour
  is condensed on chilled water (Q8) and joins the mother liquor.
The wash brings the cake liquor's NaOH from 39 % to about 4 %; the dried product keeps 0.2 wt%
NaOH and 0.09 wt% hydrazine, within the patent's 99.5-99.8 % assay.
Rejected: a centrifuge (the patent's): a filter-dryer keeps the toxic wet cake and the dry
powder closed in one vessel (D-015).

## D-010 Jackets set the dosing time (2026-11-05)
Decision: R-101 and R-102 have jackets on chilled water at 278-283 K (the medium at 280.65 K),
U 400 W/(m2 K) for an agitated stainless or glass-lined vessel with water (ASSUMED). The recipe
checks them (core ADR 0052): R-102 removes 163.1 kW at the charge (12.5 m2 wetted) against the
model's peak 152.4 kW at a 10 h dosing; R-101 87 kW against 21 kW. The dosing of both is 10 h,
the patent's 8 h being too short for R-102's jacket at this batch (about 190 kW needed); the
batch size was chosen with it (D-002).
Reason: SRC-1 gives no cooling arrangement (its 20 L flask needs none). An external loop or a
colder coolant could shorten the dosing; core checks only a jacket or a coil.

## D-011 Thermal screening of the two semi-batches (2026-11-05)
Result (`cheme process reactor-hazards`, core ADR 0050; the vented gases count in neither the
heat capacity nor the MTT, ADR 0054):

| step | dT_ad | peak accumulation | MTSR | MTT | class |
|---|---|---|---|---|---|
| R101 | 43.2 K | 0.96 % (nitrite, end of dosing) | 298.6 K | 337.63 K | none (no TD24) |
| R102 | 307.2 K | 1.98 % (dissolved methyl nitrite, end of dosing) | 318.9 K | 337.63 K | none (no TD24) |

MTT: core 1.9.0's default (ADR 0058), the normal boiling point of methanol, 337.63 K (SRC-5): the
lowest boiling point of what boils in what is charged and dosed. In R-101 methanol is a charged
reactant. In R-102 core finds methanol only because the recycled mother liquor S11 brings it
into the charge S12 (5.8 mol%; S11 carries the methanol of the cake wash S25 and the dryer's
vapour S27, the filtrate S21 none): the products are not candidates for the MTT (ADR 0058, known
limitations), so the methanol AZ forms is not counted. **R-102's default MTT depends on that
recycle**: a charge without methanol (a first batch, no wash recycle, a changed wash) would take
water's boiling point, the unsafe direction, although AZ forms methanol whatever the recycle
carries; such a change must restore `hazard.mtt: 337.63` on R102 (the test checks that S12 carries
methanol). The screening leaves out R-101's vented methyl nitrite and, in R-102, the dosed methyl
nitrite (a note: `mtt_left_out`) and the vented N2O and NH3. Up to 1.8.0 the default took R-102's
dissolved methyl nitrite, 261 K, below the process temperature, so both reactors carried a hand
`hazard.mtt: 337.63` (L-10); it is removed, and the default gives the same MTT. No TD24 is known
for the liquors or for NaN3 (none estimated): no criticality class (`cheme.reactor-hazard-missing`,
info); the MTSR stays below the MTT in both. With two reactions R-102 reports each alone: AZ
307.2 K and 318.9 K, SIDE 161.4 K and 316.2 K (dT_ad, MTSR): AZ, the main reaction, sets the
MTSR, so `hazard.reactions` is not needed. Over the batch R-102's MTSR rises with the dosing from
313.5 K at its start to 318.9 K at its end (the MTSR profile), the worst moment the end of the
dosing; R-101 stays at 298.1-298.6 K. The gas release at the MTSR and the vents: D-017.
Sensitivity (the rate constants of NTG, AZ and SIDE divided, scratch copies on core 1.8.0, not in
the files):

| rate constants | R101 accumulation, MTSR, post-reaction | R102 accumulation, MTSR, post-reaction |
|---|---|---|
| as declared | 0.96 %, 298.6 K, 0.53 h | 1.98 %, 318.9 K, 0.64 h |
| k/10 | 2.88 %, 299.4 K, 6.3 h | 13.5 %, 352.9 K (above the MTT), 10.0 h |
| k/100 | 9.04 %, 302.3 K, 66 h | 55.6 %, 480.1 K (above the MTT), 119 h |

Interpretation: R-101 is benign in the screening (a small heat); R-102 is safe only while it
stays dosing-controlled. With its adiabatic rise of about 300 K each 1 % of accumulated methyl
nitrite adds about 3 K, so above about 8 % the liquor's methanol boils on a cooling failure; a ten
times slower reaction than assumed would already do so, and would also double the cycle. A
slow absorption also sends more methyl nitrite (toxic, flammable) to the vent. Open for the next
stage: reaction calorimetry with gas dosing (heat of reaction, heat-flow and gas-uptake profile),
the TD24 of the azide liquor and the mother liquor, and of the concentrated liquor at the end of
the still (about 360 K at 10 kPa(a), D-007; with the steam kept off C-101's wall), the dosing (acid
feed of R-101) interlocked with R-102's temperature, its agitator, the off-gas methyl nitrite and
both reactors' pressure (D-017). Screening values only, not a reaction-hazard assessment.

## D-012 Utilities and duties (2026-11-05, model duties 2026-11-06)
Decision (year averages; power ASSUMED). Written by `cheme process propagate` from the models
(core 1.9.0, ADR 0059; `calculated`, fingerprinted): R-101's heat to chilled water 17.2 kW (Q1,
NTG's extent x its heat, the acid dosed at the vessel's temperature); R-102's 126.2 kW (Q2:
126.68 kW released by AZ and SIDE less 0.48 kW that warms the absorbed methyl nitrite from 298 to
313 K); the still's boil-up 186.2 kW of LP steam (Q3, ST101's `energy_port: steam`, the latent
heat of 2260 kWh per batch); the crystallizer 13.1 kW to cooling water (Q6). Typed from core's
reports, ASSUMED: the still's methanol condenser 31.4 kW on chilled water (Q4) and its water
condenser 154.9 kW on cooling water (Q5) (core writes no per-cut condenser duty); the dryer 8.26
kW of LP steam (Q7, compared by the dryer's energy port) and its vapour condenser 1.45 kW on
chilled water (Q8); power 13 kW (agitators 2 + 4 + 4 + 3 kW, R-102's gas dispersion, the vacuum
pumps; P1-P4). Per kg NaN3: LP steam 2.30 kWh, chilled water 2.08 kWh, cooling water 1.98 kWh,
electricity 0.154 kWh.
Up to 1.8.0 Q1 to Q6 were typed from the reports (L-7). Core 1.9.0 compared them with the models:
Q1, Q3 and Q6 agreed, Q2 did not (`cheme.process-duty`: 126.68 kW typed against the model's
126.198 kW), since the typed value left out the warming of the dose. Q2 holds no heat the model
leaves out (the heat of absorption of methyl nitrite is not known and not counted, D-005), so
there is nothing to split off: the model's duty replaced it, and Q1, Q3 and Q6 are written by
their models too. Chilled water per kg NaN3 went from 2.087 to 2.081 kWh. The 8.2 % of the dose
that passes to the vent is not warmed in the model (no ideal-gas data for methyl nitrite, L-9):
well under a tenth of the absorbed part's 0.48 kW (a tenth of the dose, at a gas's heat capacity,
below the liquid's), ASSUMED negligible. The still's boil-up and the dryer take their LP steam through tempered hot-water loops (D-007, D-009); the steam is
counted as the heat delivered.
Not counted: the sensible heat of the still's content as it heats from 313 to about 360 K (D-007;
about 0.6 GJ per batch, about 8 % of the boil-up), the heating of R-102's charge to 313 K, heat
losses.

## D-013 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of dried NaN3 from the flowsheet's year averages. The
purchased feeds are linked to their library producers (`lca/mappings.yaml`): sodium nitrite to
sodium-nitrite-1, sulfuric acid to sulfuric-acid-1, hydrazine hydrate to hydrazine-1, caustic soda
to chlor-alkali-1, methanol to methanol-1, the nitrogen consumable to asu-1's gaseous nitrogen; the
LP steam counted as heat (kWh). Gaps in `cheme assess lca`, each with the activity it should
connect to: process water, electricity, chilled and cooling water, the sulfate liquor, the
condensate, the purge (azide destruction, no background) and R-102's off-gas (thermal
oxidation). The Atlas build (`scripts/build_lci.py`) links some of them through the library's
shared mappings (`lci/mappings.yaml`, by the chemical slugs of process.yaml): process water to
deionised water, electricity, cooling water, and the sulfate liquor and the condensate to average
(municipal) wastewater treatment, a proxy for these effluents. It leaves three gaps: chilled
water, the off-gas and the purge. The purge and the off-gas carry no chemical slug in process.yaml
on purpose, so that no generic treatment stands in for the azide destruction (its nitrite, acid
and oxidant and the N2O it releases) or for the thermal oxidation.
The nitrogen is an `lca.yaml` consumable `per_batch` (core ADR 0053, library ADR 0035): 40 Nm3
(50 kg) per batch, ASSUMED: 0.049 kg per kg NaN3 at 652.6 batches a year; it leaves with the
off-gas and the vents (no disposal exchange).
**The off-gas carries 0.036 kg N2O per kg NaN3** (from SIDE, D-005): about 10 kg CO2-eq per kg
NaN3 if it reached the air (GWP100 273, IPCC AR6), more than the feeds' burdens are likely to be.
Its fate in the thermal oxidiser (N2O is destroyed only in part at usual temperatures) is the open
item of a climate result; the gap says so, and SIDE's stoichiometry is itself ASSUMED.
Per kg NaN3: sodium nitrite 1.222 kg, sulfuric acid 0.883 kg, hydrazine hydrate 0.831 kg, caustic
soda 50 % 1.287 kg, methanol 0.074 kg, process water 4.43 kg, nitrogen 0.049 kg; wastes: sulfate
liquor 4.72 kg, condensate 2.78 kg, purge 0.086 kg, off-gas 0.138 kg.
Not counted (emission exclusions, no P&ID yet): the vacuum pumps' exhausts, the purge nitrogen,
the receiver's breathing, fugitive leaks; all to the thermal oxidiser in the design.

## D-014 Dedicated train (2026-11-05)
Decision: R-101, R-102, C-101, F-101 and T-101 make only NaN3, batch after batch: 652.6 batches
in 7920 h (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); an azide train is plausibly
dedicated anyway (contamination and the azide's hazards; the mother liquor carries over from
batch to batch).
Out of scope, so not LCI gaps: changeover cleaning, idle time on a multipurpose train, shared
tank farms and scrubbers. On a multipurpose plant the burden per kg is higher.
The sulfate liquor (S6, 26.6 wt% Na2SO4) is above the solubility of sodium sulfate at 298 K: in
the plant Glauber's salt would crystallise in R-101 unless it is drained warm or diluted; the
model keeps it dissolved (ASSUMED; the patent, at the same ratios, says nothing about it).

## D-015 Process safety notes (2026-11-05)
Not a hazard assessment; the points the design rests on, for the HAZOP and the reaction-hazard
study of the next stage:
- **Acute toxicity of NaN3**: highly toxic by ingestion, inhalation and skin contact (it blocks
  cytochrome oxidase, as cyanide does). The dry product is a dust hazard: closed filter-dryer,
  closed discharge, no open handling. Hydrazine (toxic, a carcinogen, corrosive) and methyl
  nitrite (toxic gas) need the same containment.
- **Hydrazoic acid (HN3)**: HN3 is a volatile (bp 309 K), very toxic and explosive acid (SRC-1
  names the prior art that distilled it as dangerous). It forms in two ways here: any acid turns
  azide into HN3, and hydrazine nitrosated by nitrous acid in acid gives HN3 directly (the
  N-nitrosohydrazine path at high acidity, SRC-4). The design keeps acid and azide apart: the acid
  is only in R-101, which never receives an azide liquor; the methyl nitrite is the only stream
  from R-101 to R-102; the azide side (R-102, C-101, F-101, T-101) stays strongly alkaline. The
  one stream back to the acid side is the recovered methanol S3, distilled from the alkaline
  liquor: it holds no azide (NaN3 is non-volatile), and the model takes hydrazine as non-volatile
  (ASSUMED, D-007). But hydrazine has a vapour pressure, ammonia is expected in that cut (D-005),
  and liquor can be entrained; hydrazine in S3 meets nitrous acid in R-101, which is acidic, and
  forms HN3 there, which then rides with the methyl nitrite into the gas line (or stays in the
  sulfate liquor S6). Hence a limit on S3, ASSUMED: at most 10 mg/kg hydrazine and no azide, each
  receiver charge analysed before it goes to R-101 (off-spec methanol back to the still); at that
  limit one charge (about 660 kg) carries about 7 g hydrazine, at most about 0.2 mol HN3 per
  batch. HAZOP items: hydrazine and liquor carry-over into S3 (entrainment, foaming, a wrong
  line-up), and azide in the sulfate liquor S6 before it goes to wastewater.
- **Purge destruction** (outside the boundary, not designed; the order matters): the purge S29
  holds about 3 mol hydrazine per mol azide (mole fractions N2H4 0.113, NaN3 0.036). Nitrite and
  acid added first would turn that hydrazine into more HN3, about three times the azide being
  destroyed. So, first the hydrazine is oxidised in the alkaline liquor (hypochlorite, kept
  alkaline, since chlorine azide forms in acid; or hydrogen peroxide without the usual copper
  catalyst, which would give copper azide) and checked hydrazine-free by analysis; only then is
  the azide destroyed with nitrite and acid (nitrous acid, to N2 and N2O) in a controlled, vented
  step with HN3 and N2O off-gas treatment, and checked azide-free before neutralisation and
  discharge.
- **Heavy-metal azides**: azide forms shock-sensitive metal azides, copper azide notoriously in
  drains (SRC-3), and lead azide is the detonator compound; zinc and brass are taken as unsafe
  too (ASSUMED, conservative): no copper alloys, lead or zinc on the azide side
  (stainless steel, glass-lined), and no azide to drains before destruction.
- **Methyl nitrite**: a toxic, flammable gas (bp 261 K) that can decompose explosively; the line
  from R-101 to R-102 is short, inerted and protected (flame arrester, non-return), and the acid
  feed stops when R-102 stops absorbing (D-011).
- **Gas evolution**: R-101 gives about 44.6 m3/h of methyl nitrite at its peak and R-102 8.1 m3/h
  of off-gas (`process recipe`). The vents are taken as 50 and 60 m3/h, and the gas a cooling
  failure releases at the MTSR is within them (29.4 and 6.3 m3/h); but with a vent blocked both
  vessels pressurise, so the acid dosing trips on either reactor's pressure and each reactor gets
  a relief device to the thermal oxidiser (D-017).
- **Thermal**: dry NaN3 decomposes at high temperature to sodium and nitrogen; no TD24 of the
  liquors or the solid was found and none is estimated (D-011). The still's residue (about 44 wt%
  NaN3 at the end, crystals once it precipitates), a concentrated azide / hydrazine caustic liquor, reaches about 360 K at
  10 kPa(a) (D-007), well above the patent's 40 C; C-101's jacket and coil take tempered hot water
  (at most about 390 K) instead of LP steam (412 K) on the wall. The hot concentrated liquor and its
  wall temperature are an open reaction-hazard item: its TD24 is needed before the still's pressure
  and heating medium are fixed. The dryer runs at 333 K on hot water.
- **Off-gas**: N2O (an oxidiser and a greenhouse gas), NH3 and methyl nitrite to the thermal
  oxidiser (D-013).

## D-016 Mother-liquor recycle and purge (2026-11-05)
Decision: the mother liquor, the wash filtrate and the dryer condensate are collected in T-101
(M103) and 95 % goes to the next batch's charge in R-102 (S11, X101's `split`); 5 % is purged (S29, 88.6 kg per
batch) to azide destruction, ASSUMED: the hydrazine oxidised first in the alkaline liquor, then the
azide destroyed with nitrite and acid (D-015).
Reason: SRC-1 Example 2 recycles the whole filtrate over 11 batches, and its steady batches give
41.0 mol NaN3 for 43.2 mol fresh hydrazine (94.9 %); a purge keeps the impurities the model does
not carry (nitrite, carbonate from the air, decomposition products, metals) from building up. The
5 % costs about 2 % of the hydrazine; the design's yield is 92.3 % on hydrazine, between the
patent's steady batches and its 90.0 % over all 11. Fresh caustic and hydrazine top the recycle
up to the charge ratios of D-004, so the purge sets the fresh caustic (1.05 mol NaOH per mol
NaN3).
Open: the purge from measured impurity build-up; the yield of the methanol wash.

## D-017 Vent capacities, the gas release at a cooling failure and a blocked vent (2026-11-06)
Decision: `hazard.vent_capacity` at the vessel's pressure 50 m3/h for R-101 and 60 m3/h for
R-102, ASSUMED from the vents of D-015 (no line sizing yet, no P&ID):
- R-101's vent is the methyl nitrite line S7 to R-102's sparger (inerted, flame arrester,
  non-return valve), 50 m3/h. It passes the normal peak, 44.6 m3/h of methyl nitrite at 298 K at
  the start of the dosing (`cheme process recipe`), with a headroom of 50/44.6 = 1.12.
- R-102's vent is the off-gas line S14 to the thermal oxidiser, 60 m3/h. Its normal peak is 8.1
  m3/h, but it is sized for R-102 not absorbing (agitator or sparger failure) until the interlock
  stops R-101's acid: R-101's whole methyl nitrite, 44.6 m3/h at 298 K or 46.9 m3/h at 313 K, then
  passes through, with the N2O and NH3 the dissolved methyl nitrite still forms as it reacts away,
  at most their normal rate, 4.3 m3/h (the 8.1 m3/h peak less its 3.8 m3/h of unabsorbed methyl
  nitrite): about 51 m3/h at 313 K, a headroom of 60/51 = 1.17.
- No nitrogen sweep is counted on either line: the 40 Nm3 of nitrogen per batch (D-013) inerts
  the vessels before the charge, breaks C-101's vacuum and drives F-101's pressure filtration, and
  none flows during the dosing. A sweep the P&ID adds passes S7 and S14 both and adds to both
  bases.

Result (`cheme process reactor-hazards`, core 1.9.0, ADR 0058; per batch of the recipe, at the
MTSR and 101.3 kPa(a)):

| step | gas at the MTSR | rate from | vent capacity | ratio | most gas one reaction forms |
|---|---|---|---|---|---|
| R101 | 29.4 m3/h (methyl nitrite, 0.333 mol/s) at 298.6 K | NTG, the worst moment's content | 50 m3/h | 0.59 | 0.161 kmol, 3.94 m3 (NTG run to completion) |
| R102 | 6.34 m3/h (N2O and NH3, 0.067 mol/s) at 318.9 K | SIDE, the worst moment's content | 60 m3/h | 0.11 | 0.660 kmol, 17.3 m3 (SIDE run to completion) |

Both are within the vents (`cheme.reactor-hazard-vent`, info). In R-101 the rate at the MTSR is
below the normal peak: the dosed acid accumulates to under 1 %. In R-102 only the side reaction
forms gas (AZ forms none), and the "most gas" is an upper bound that sends the whole accumulated
methyl nitrite by SIDE.
**Finding: a blocked vent** (a design item for the next stage; core screens no head space or
relief, ADR 0058, L-13; ideal gas, the head spaces from the recipe's vessels):
- S7 blocked (the non-return valve stuck, the sparger plugged): R-101 keeps making methyl nitrite
  at the dosing rate, 1.82 kmol/h, into about 1.76 m3 of head space (6.3 m3 less 4.54 m3 of
  batch), about 0.7 kPa/s at 298 K; once the acid stops, the accumulated acid still gives 0.161
  kmol, about 0.23 MPa.
- S14 blocked: R-102's side reaction on the whole accumulated methyl nitrite gives up to 0.660
  kmol into about 2.29 m3 (8 m3 less 5.71 m3), about 0.76 MPa at 318.9 K, and the generator's
  methyl nitrite keeps arriving until the acid stops.

Hence (ASSUMED, for the P&ID, the HAZOP and the relief study): R-101's acid dosing trips on high
pressure in R-101 or R-102 (with R-102's temperature, agitator and off-gas methyl nitrite, D-011),
and each reactor gets a relief device to the thermal oxidiser sized for at least its vent
capacity (50 m3/h for R-101, 60 m3/h for R-102), the vessels' design pressure set with it
(equipment list). Not screened either: the accumulated
dissolved methyl nitrite (1.98 % of the dose at the end of the dosing, about 0.33 kmol, at most
about 8.6 m3 at 318.9 K) desorbing on a cooling failure (core#178 item 5, L-10), toxic and to the
same vent.

## Core features used (core 1.8.0 and 1.9.0)

| feature | ADR | used for |
|---|---|---|
| `batch.vent {stream, components}` | 0054 | R101: methyl nitrite leaves as it forms (S7); R102: N2O and NH3 leave as they form (S14) |
| `dosing.absorbed` | 0054 | R102: the methyl nitrite gas dosed, 91.8 % absorbed, the rest to the vent |
| vented semi-batch in the screening and the recipe | 0054 | MTSR and MTT without the vented gas; peak vent rates per batch (D-015) |
| `still:` with `cuts` and a constant relative volatility, a recipe `distil` `from:` | 0055 | ST101: the methanol cut and the water cut, the boil-up time and energy |
| `crystallizer.spectators`, `solubility.measured_in: mother_liquor` | 0056 | CR101: NaN3 from the caustic hydrazine liquor at the patent's filtrate solubility |
| `dryer:` to a residual moisture with `energy`, `drying_rate`, `cake_density` | 0057 | D101: the product, the vapour, the duty (checked by its port) and the drying time |
| `solid_separation.filtration` and a recipe `filter` `from:` | 0057 | F101, F102: Ruth filtration times |
| recipe `units: [...]` | 0057 | one vessel each for M101+R101, M102+R102, ST101+X102+CR101 and F101+W101+F102+D101 |
| recipe `start: {after, operation}` | 0051 | R-102 absorbs while R-101 generates |
| `tears: [{stream, initial}]`, `convergence:` (1.9.0) | 0060 | S11 and S3: the two recycles converged by Wegstein's method, S3's flow held as a charge ratio (D-006) |
| model duties on energy streams, `energy_port:` (1.9.0) | 0059 | Q1, Q2, Q3 (ST101 `energy_port: steam`) and Q6 written by propagate (D-012) |
| default MTT of what boils, `gas_release`, `hazard.vent_capacity` (1.9.0) | 0058 | R101, R102: the MTT of methanol without `hazard.mtt` (in R-102 from the recycled methanol in the charge); the gas release at the MTSR against 50 and 60 m3/h (D-011, D-017) |

Core 1.7.0 refuses the 1.8 fields and 1.8.0 the 1.9 ones (`tears`, `energy_port`,
`hazard.vent_capacity`), so `plant.yaml` requires `cheme-as-code>=1.9`, the library's pin.

## Core limits met (candidates for core issues)

- L-1 (resolved in core 1.9.0, ADR 0060): **no recycle convergence in propagate.** The
  mother-liquor and methanol recycles were ASSUMED tear streams converged by a hand driver
  iterating `propagate --fill`; they are now the flowsheet's `tears:`, converged by propagate and
  `calculated` (D-006). Still open: no design specification (the fresh feeds that hold a charge
  ratio at the converged recycle stay ASSUMED at their values, core#181 part 2).
- L-2: **a vent takes only what forms.** A dissolved dose left unreacted (0.1 % of the methyl
  nitrite) cannot leave later, and a gas charged rather than formed cannot vent; the still cannot
  vent a dissolved gas either, so the trace is carried as non-volatile through the work-up (D-005).
- L-3: **the still is one ideal stage.** The patent's 90 wt% methanol cut needs a short column
  with reflux (core#173) and the salting-out of methanol by the caustic liquor (no activity
  model, no electrolyte); an effective relative volatility of 150 had to be calibrated (D-007).
- L-4: **a constant-volatility still gives no temperatures**, so the residue's temperature is an
  estimate typed in: an ideal Raoult trial run counts NaOH as one molecular particle and gave
  335 K, about 25 K short of the caustic liquor's boiling-point elevation, so the 360 K of S17 is
  estimated from Duhring data of NaOH solutions (D-007). A still that reports its pot temperature
  from an electrolyte (or a declared boiling-point elevation) model would give it and the wall's
  approach.
- L-5: **no evaporative crystallization with spectators in the still.** NaN3 stays dissolved,
  supersaturated, in the still's residue, and precipitates in the next step; an evaporating
  crystallizer with spectators (or a still that lets a solute crystallize) would be one step. The
  still's vessel is not sized either.
- L-6: **the liquor-measured solubility holds at one composition, and nothing checks it.** The
  still's end was tuned by hand so that the mother liquor matches the patent's filtrate (D-008);
  a check (or an end of the still at a target liquor composition) would help.
- L-7 (resolved in part in core 1.9.0, ADR 0059): **duties are copied by hand.** The
  semi-batches, the still's boil-up and the crystallizer now write their duties (Q1, Q2, Q3, Q6,
  D-012), and a typed duty that differs from its model is a warning. Still typed and able to go
  stale silently: the still's condensers Q4 and Q5 (no per-cut condenser duty, a follow-up of
  ADR 0059) and the dryer's vapour condenser Q8; the dryer's heat Q7 is compared by its port.
- L-8: **a wash is a mixer.** No dissolution of NaN3 into the methanol wash (it is slightly
  soluble in methanol) and no displacement efficiency (D-009); a reslurry crystallizer needs one
  solvent, and the wash liquor is aqueous methanol.
- L-9: **the gas dose has no ideal-gas data** (no `ideal_gas` for methyl nitrite in chemicals'
  ATcT set), so the warming of the gas that passes through R-102 is left out (a note; well under
  0.05 kW); since core 1.9.0 the absorbed part's warming is in Q2 (0.48 kW, D-012).
- L-10 (resolved for the MTT in core 1.9.0, ADR 0058): **the default MTT can be a dissolved
  gas's boiling point** (methyl nitrite 261 K in R-102), below the process temperature; a hand
  `hazard.mtt` fixed it up to 1.8.0. The default now leaves the dosed and vented gases out and
  gives methanol's 337.63 K, and the hand value is removed (D-011). Still open: the gas release
  of an accumulated, dissolved dose on a cooling failure (desorption) is not screened (core#178
  item 5; D-017); and the products are not MTT candidates (ADR 0058), so in R-102 the default
  finds methanol only in the recycled mother liquor of the charge, not in what AZ forms (D-011).
- L-11: **two coupled vessels.** R-101 makes the dose of R-102; the recipe aligns them with
  `start.after`, but nothing checks that the two dosing times are equal or that the generator's
  gas rate profile is the absorber's dose profile (both constant here by construction).
- L-12 (resolved): `requires: cheme-as-code>=1.8` could not be written before the release (core
  main reported 1.7.0); core 1.8.0 is released and pinned, and plant.yaml requires it (now 1.9).
- L-13: **the blocked-vent pressure is not screened.** The gas release at the MTSR is compared
  with the vent's capacity (ADR 0058), but there is no head-space or relief model, so the
  pressure a blocked vent builds up in R-101 and R-102 is estimated by hand (ideal gas, D-017).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batches R-101 and R-102 with vents: composition, accumulation, MTSR, peak cooling, gas rates | done in cheme, kinetics ASSUMED | D-005, D-011, `process reactors`, `reactor-hazards`, `recipe` |
| methanol strip and concentration | done in cheme (batch still), volatility ASSUMED | D-007, `process stills` |
| precipitation from the mother liquor | done in cheme, solubility from the patent's filtrate | D-008, `process crystallizers` |
| filtration, wash, drying | done in cheme, specified, data ASSUMED | D-009 |
| recycles | done in cheme (tears S11 and S3, Wegstein); the fresh feeds' charge ratios ASSUMED | D-006 |
| batch recipe, cycle time, basis check, vessels, jackets, filter and drying times | done in cheme | D-003, D-010 |
| duties | done in cheme for R-101, R-102, the still's boil-up and the crystallizer; the condensers and the dryer typed from core's reports | D-012, L-7 |
| vents: gas release at the MTSR against the vent capacity | done in cheme, capacities ASSUMED; the blocked-vent pressure by hand | D-017, L-13 |
| per-batch exchanges (nitrogen) | done in cheme, amount ASSUMED | D-013 |
| LCI inventory | done, feeds linked, utilities and treatments gaps | D-013 |

## Open inputs
Kinetics, heats of reaction and gas uptake (calorimetry with gas dosing), TD24 of the liquors and
of NaN3; the side reactions' products (N2O and NH3 or N2) and the off-gas analysis; NaN3
solubility in the mother liquor over temperature and composition; the still's column and
pressure and the boiling point of the concentrated liquor (about 360 K estimated, D-007), its
TD24; the hydrazine in the recovered methanol (its limit, D-015); filtration and drying data of
the cake; the purge from impurity build-up; the jackets' U; the product specification; the fate
of N2O in the thermal oxidiser; the azide-destruction step (hydrazine oxidised first, D-015); the
vent lines' and relief devices' sizing and the vessels' design pressure (D-017); a TEA
(`operation.batch: {recipe: true}`).
