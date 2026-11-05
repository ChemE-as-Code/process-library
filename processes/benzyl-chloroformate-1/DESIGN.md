# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Benzyl chloroformate (BCF, Cbz-Cl) by the phosgenation of benzyl alcohol, issue
ChemE-as-Code/process-library#153. Concept stage: design basis, batch recipe, balanced BFD/PFD,
thermal screening and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP,
TEA, datasheets.

Starting point (2026-11-05): library `main` at 77fa11c2; cheme-as-code core `main` at 7334d7c
(to be released as 1.8.0; `cheme --version` still prints 1.7.0 there). The entry uses core
features that 1.7.0 does not have (batch.vent, dosing.absorbed, still:, recipe units:; see
"Core features used"): the library's CI, pinned to 1.7.0, may refuse them until the pin moves.

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; no paragraph numbers, so the locator is the part
of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US6696590B2, H. Bonnard, L. Ferruccio, P. Gauthier, J.-P. Senet (SNPE, now Isochem), 2004: Process for the synthesis of aliphatic, cycloaliphatic or araliphatic chloroformates, https://patents.google.com/patent/US6696590B2/en | description: phosgenation at or below 950 mbar (preferred 350-750 mbar), -30 to +50 C (preferred -10 to +20 C), phosgene added below 8 C, then 2-8 h at -10 to 20 C; 1 to 10 mol phosgene per mol (preferred 1.5-2.5); solvent optional; a reflux condenser with a dry-ice trap and two charcoal columns take the phosgene and HCl given off; the product is degassed at the final reaction temperature. Ex. 3: 217 g (1.99 mol) benzyl alcohol cooled to about 0 C, 250 g (2.52 mol, 1.27 eq) phosgene added at 500 mbar and 0-6 C, 6.5 h in all; 275 g product (1.61 mol), 81 % yield, 98.4 % purity, 0.4 % benzyl alcohol, 0.51 % benzyl chloride, 0.26 % dibenzyl carbonate. Ex. 4: 250 mbar, 1.34 eq, 2 h more stirring; 75 % yield, 97.1 % purity. A comparative test at atmospheric pressure (menthol in toluene) gives 68 % with a third of the alcohol unreacted; the patent gives no mechanism for the benefit of the vacuum | read; patent, facts only | D-001, D-004, D-005, D-006, D-008, benchmarks |
| SRC-2 | US3966786A, L. Rozsa, L. Meszaros, F. Mogyorodi (Eszakmagyarorszagi Vegyimuevek), 1976: Method for producing chloroformates, https://patents.google.com/patent/US3966786A/en | background: chloroformates from an alcohol and phosgene with HCl given off, strongly exothermic, the dialkyl carbonate as side product; the older batch route adds the alcohol to liquid phosgene near 0 (0-10) C with a large phosgene excess, sometimes in toluene or benzene, in lead-lined or enamelled stirred vessels with reflux condensers and cooling jackets; nitrogen flushes the excess phosgene out; drawbacks named: large cooling duties, corrosion-resistant materials, a crude high in HCl and carbonate, a large phosgene inventory. Ex. 8: benzyl chloroformate in its own continuous reactor at 170 C, 17 s, 81 % yield, 91 % purity (not used) | read; patent, facts only | D-001, equipment |
| SRC-3 | NIST Chemistry WebBook, SRD 69, benzyl chloroformate (C501531), https://webbook.nist.gov/cgi/cbook.cgi?ID=C501531&Units=SI&Mask=2 | liquid enthalpy of formation -376.2 +/- 1.1 kJ/mol, from the solution calorimetry of Finch and Salem (1987), Thermochim. Acta 116, 65-69 (the paper itself not read) | read (public SRD page) | D-005 |
| SRC-4 | chemicals 1.5.2 and thermo (Caleb Bell, MIT licence), as packaged with cheme-as-code | formation enthalpies (benzyl alcohol and benzyl chloride liquid: CRC/WebBook; phosgene, HCl, CO2 gas: ATcT), critical constants, COSTALD liquid volumes, liquid heat capacities, heats of vaporization, vapour pressures, normal boiling points | open-source package, facts only | materials.yaml, D-005, D-006 |
| SRC-5 | PubChem CID 10387 (benzyl chloroformate) and CID 244 (benzyl alcohol); EBI OLS (ChEBI) | identity (formula, InChIKey, CAS) | read (PUG REST) | chemicals registry |
| SRC-6 | processes/phosgene-1, chlor-alkali-1, asu-1 (this library); Hughes, Rossi, Lennon (2023) React. Chem. Eng. 8, 3150, doi:10.1039/D3RE00354J (CC BY 3.0), section 2.1.1, as cited by phosgene-1 | liquid phosgene at 253 K, 340 kPa(a); caustic soda 50 wt%; gaseous nitrogen; phosgene destroyed in caustic to carbonate and chloride | library, internal; open paper | D-004, D-007, LCI links |
| SRC-7 | Stoessel, F. (2008) Thermal Safety of Chemical Processes, Wiley-VCH, doi:10.1002/9783527621606 | accumulation, MTSR and criticality classes of a semi-batch (method, implemented in core ADRs 0050, 0054) | method reference, no data taken | D-011 |
| SRC-8 | Ullmann's Encyclopedia of Industrial Chemistry, Chloroformic Esters, doi:10.1002/14356007.a06_559.pub3; Phosgene, doi:10.1002/14356007.a19_411.pub2 | - | not read (licensed); named by the issue's literature note | route reference leads only |
| SRC-9 | Org. Synth. Coll. Vol. 3, p. 167 (benzyl chloroformate); Hough and Priddle, J. Chem. Soc. 1961, doi:10.1039/JR9610003178; US6919471 Ex. 8-9 (triphosgene in toluene) | - | not read (access blocked, or a search snippet only) | not used |

Searched and not found openly (2026-11-05): kinetics or reaction calorimetry of the
phosgenation of benzyl alcohol, the formation enthalpy of dibenzyl carbonate, the solubility of
HCl and phosgene in benzyl alcohol or the chloroformate, a TD24 or decomposition data of benzyl
chloroformate (a secondary source reports its decarboxylation slow at 100 C and vigorous at
155 C, citing older work; not used), a plant's capacity or specific consumptions, and a market
volume.

## D-001 Route and boundary (2026-11-05)
Decision: phosgene dosed as a gas into neat benzyl alcohol at 278 K and 50 kPa(a), without base
or solvent, in a semi-batch on a dedicated train (D-013), the reduced-pressure batch route of
SRC-1 (Ex. 3); PhCH2OH + COCl2 -> PhCH2OCOCl + HCl, with the HCl leaving as it forms. The crude
is degassed in the same vessel and leaves neat as the product, not distilled. Vent and degassing
gas go through a vacuum pump to a caustic scrubber. Boundary feeds: benzyl alcohol, liquid
phosgene, caustic soda 50 wt%, process water, electricity, LP steam, nitrogen (per batch);
returns: chilled brine, cooling water; outputs: neat BCF, the spent scrubber liquor.
Reason: SRC-1 is the one open source with a plant-like batch procedure for this compound, its
conditions and impurities; SRC-2 confirms the batch route with excess phosgene in enamelled
vessels as the established practice. The route uses the library's phosgene (phosgene-1, captive
on the same site, as phosgene is not shipped) and caustic (chlor-alkali-1). It exercises a dosed
exothermic step with gas evolution and a gas dose: the features core ADR 0054 adds.
Rejected: (a) the alcohol added to liquid phosgene (the reverse order, SRC-2's older route): a
large phosgene inventory in the reactor, which is the main hazard SRC-2 names; (b) a solvent
(toluene): more volume and a solvent recovery, and SRC-1 needs none; (c) SRC-2's continuous fog
reactor at 170 C: not the practice for BCF, 91 % purity; (d) triphosgene: a solid phosgene
substitute for small scale, not made in the library. Variants: a phosgene recovery (D-007), an
HCl recovery as hydrochloric acid (D-007), the toluene-solution product (`benzyl-chloroformate-2`).

## D-002 Capacity, product and operating hours (2026-11-05)
Decision: 1000 t/a neat BCF, 7920 h/a (330 days of 24 h), ASSUMED. Product: 99.2 wt% BCF with
0.51 wt% benzyl chloride, 0.26 wt% dibenzyl carbonate, 0.03 wt% phosgene, 0.02 wt% benzyl
alcohol (stream S8, D-008), to cold storage at 278 K.
Reason: no open market or plant figure was found; BCF is a fine-chemical reagent (the Cbz
protecting group), so a batch plant of about a thousand tonnes a year next to a phosgene unit is
the plausible scale. The LCI is per kg and does not depend on the scale; the batch size does
(D-003).

## D-003 Batch basis and recipe (2026-11-05)
Decision: one batch makes 1770 kg of neat BCF (stream S8). The recipe (`process/recipe.yaml`)
has one unit procedure, PHOSGENATE, on R-101 over three steps of the flowsheet (`units: [E101,
R101, T101]`, core ADR 0057): nitrogen purge and evacuation 0.5 h, charge 0.5 h, cool-down from
298 to 278 K 0.22 h (from the jacket, core ADR 0052), phosgene dosing 10.0 h and post-reaction 0
h (from R101's model: the target conversion is reached when the dosing ends), degassing 1.79 h
(from T101's boil-up, core ADR 0055), vacuum break and sampling 0.5 h, transfer 0.5 h: 14.01 h.
R-101 is the bottleneck: cycle time 14.01 h, 565.3 batches in 7920 h, 1000 t/a; the flowsheet's
flows are the recipe's year averages (126.30 kg/h of S8 against 126.33 kg/h from the recipe,
within 1 %, no `cheme.recipe-basis` finding).
Vessel: 1.63 m3 of crude at the end of the dosing; the recipe sizes R-101 from R101's model
(fill fraction 0.8, H/D 1.2, ASSUMED): 2.5 m3 (R10 preferred size), 65 % full, D 1.38 m. Jacket:
U 250 W/(m2 K) of an enamelled vessel with brine at 248 K (ASSUMED) removes 34.4 kW over the
4.58 m2 the charge wets, against the model's peak duty of 31.4 kW (no `cheme.recipe-jacket`
finding). The dosing time of 10 h is set by this check: 8 h gave a 39.2 kW peak above what the
jacket removes.
Reason: core ADR 0051 puts the batch basis in one place; the dosing, post-reaction, degassing
and cool-down times come from the models, so a change of kinetics, dosing or boil-up changes
the cycle (D-011 shows how much). The other durations are ASSUMED concept values.

## D-004 Feeds and phosgene supply (2026-11-05)
Decision: 1.27 mol of phosgene per mol of benzyl alcohol (SRC-1 Ex. 3), from phosgene-1's
liquid phosgene (253 K, 340 kPa(a)), evaporated in E-102 with tempered water and dosed as a gas
at 293 K, 150 kPa(a). Dry benzyl alcohol, 100 % in the model, from storage at 298 K.
Reason: the ratio is the one of the example that gives the best yield and purity at 500 mbar;
SRC-1's preferred range is 1.5-2.5, so 1.27 is at its lean end and keeps the phosgene destroyed
in the scrubber smaller. Dosing the gas keeps the phosgene inventory in R-101 to what is
dissolved (at most about 11 wt%). Benzyl alcohol has no library producer: its own entry
(benzyl-alcohol-1, #154, benzyl chloride hydrolysis) was not on main and had no open PR on
2026-11-05, so the LCI keeps it a gap (D-012); its water and benzaldehyde (which would consume
phosgene) are not modelled.

## D-005 Phosgenator R-101: semi-batch with vent, kinetics and heats (2026-11-05)
Decision: R101 is `reactor: semibatch` (core ADR 0050) with a vent (ADR 0054): the charge S2 at
278.15 K and 50 kPa(a); phosgene S4 dosed at a constant rate over 10 h with `absorbed: 0.95`
(5 % passes straight to the vent stream S6); `vent: {components: [HCL, CO2], fraction: {HCL:
0.95}}` (95 % of the HCl formed leaves as it forms, 5 % stays dissolved; all CO2 leaves);
isothermal; target 0.994 conversion of the alcohol (0.4 wt% left in SRC-1 Ex. 3), which the run
passes when the dosing ends (0.9996).
Reactions (`process/reactions.yaml`): PHOSG, the main reaction; CARB, chloroformate + alcohol ->
dibenzyl carbonate + HCl; CLBN, the net of the alcohol's chlorination by HCl and the phosgene's
hydrolysis by the water it gives, alcohol + phosgene -> benzyl chloride + CO2 + HCl (both side
reactions SRC-1 names through its impurities). Rate laws: second order in the two reactants,
Ea 40 kJ/mol, k(278 K) = 1.0e-3 m3/(kmol s) for PHOSG, ASSUMED; CARB's and CLBN's constants set
so that R101 makes Ex. 3's 0.26 wt% dibenzyl carbonate and 0.51 wt% benzyl chloride (result:
0.26 and 0.51 wt%).
Heats, on the gas basis of phosgene, HCl and CO2 (ADR 0054: the dosed gas reacts as a gas, the
vented gas forms as a gas): PHOSG -88.6 kJ/mol and CLBN -138.4 kJ/mol from formation enthalpies
(SRC-3, SRC-4); CARB -30 kJ/mol ASSUMED (no formation enthalpy of dibenzyl carbonate).
Reason: no open kinetics exist (searched 2026-11-05). The fast effective rate makes the step
dosing-controlled, as SRC-1's 0-6 C operation with a cold condenser suggests; it is an ASSUMED
placeholder for reaction calorimetry. The absorbed and vent shares are ASSUMED stand-ins for the
unknown solubilities: at 50 kPa(a) and 278 K phosgene is near its boiling point (about 264 K at
50 kPa), and a brine reflux condenser returns most of what evaporates, so the share that passes
is what the condenser does not hold back; HCl, far above its boiling point, mostly leaves.
SRC-1's benefit of the vacuum (faster HCl removal, a higher yield than at atmospheric pressure)
is not modelled: the vent share does not depend on the pressure (core limit L-4).
**The accumulation in D-011 is a consequence of the assumed rate law and of the deliberate
phosgene excess**, and must be confirmed by reaction calorimetry with gas dosing (heat flow and
gas flow during the dosing) before basic engineering.

## D-006 Degassing T101: a batch still at 20 kPa(a) (2026-11-05)
Decision: T101 is a `still:` (core ADR 0055) in R-101 after the dosing: constant relative
volatility HCl 30, phosgene 1, CO2 100 (ASSUMED, the ratio of their vapour pressures at 278 K,
about 2940 and 92 kPa, SRC-4), the benzyl compounds non-volatile, a boil-up of 1.5 kmol/h of
gas (the vacuum pump K-201, about 173 m3/h at 20 kPa(a) and 278 K, ASSUMED), to 0.05 mol%
phosgene in the residue (ASSUMED specification); heats of vaporization of the gases at 278 K
(SRC-4) stand for their heats of desorption. Result (`cheme process stills`): 233 kg of gas per
batch (2.17 kmol phosgene, 0.52 kmol HCl), 1.79 h, 9.2 kW mean (10.3 kW peak), 16.5 kWh per
batch; the product holds 0.03 wt% phosgene and no HCl.
Reason: SRC-1 degasses at the final reaction temperature; SRC-2 flushes with nitrogen. A still
gives the degassing time for the cycle and its gas per batch from stated inputs, instead of a
specified split with a guessed time. The constant volatilities only order HCl before phosgene;
the time follows from the gas drawn off, so the vacuum pump's capacity, not the volatilities,
sets it. The degassing is not a distillation of the product: the benzyl compounds stay.
Rejected: a specified split after R101 (the 1.7.0 workaround): no time, no gas amount per batch;
a nitrogen sparge: core's still has no inert stripping gas (core limit L-5).

## D-007 Off-gas: vacuum pump and caustic scrubber (2026-11-05)
Decision: the reactor's vent S6 and the degassing gas S7 join in M201 (the vacuum pump K-201)
and are destroyed in the caustic scrubber T-201 (S101, a conversion step): HCl + NaOH -> NaCl +
H2O and COCl2 + 4 NaOH -> Na2CO3 + 2 NaCl + 2 H2O at 99.99 % (as phosgene-1's scrubber,
SRC-6), CO2 + 2 NaOH -> Na2CO3 + H2O at 99 %, all ASSUMED; caustic 50 wt% at 1.1 times the
NaOH the gas takes, diluted to 10 wt% (M202). Per batch: 429 kg of vent gas (HCl 9.88 kmol,
phosgene 0.66 kmol, CO2 0.07 kmol; peak 0.35 mol/s, 58 m3/h at 278 K and 50 kPa(a), 0.46 h into
the dosing, `cheme process recipe`) and 233 kg of degassing gas (D-006): 662 kg, of it about 379
kg HCl and 280 kg phosgene. The spent liquor (5.80 kg/kg BCF: 9.1 wt% NaCl, 3.0 wt% Na2CO3,
0.85 wt% NaOH) goes to the site wastewater treatment.
Reason: a caustic scrubber is the usual last barrier for phosgene and HCl; destroying both is
the simplest closed balance. The scrubber has one outlet in the balance (the liquor): core has no
specified component separator that would send the unabsorbed traces and the purge nitrogen to
the stack (core limit L-7), so they stay in the liquor and the stack emission is an exclusion.
Not done, recorded as open: condensing the excess phosgene (0.27 mol per mol of alcohol, 0.16
kg/kg BCF) back for the next batch, which SRC-1's dry-ice trap does in the laboratory and a plant
would do with a brine condenser (it would save about half of the scrubber's caustic); recovering the HCl
as hydrochloric acid after the phosgene is removed (a co-product with its allocation). Both
change the LCI substantially (0.74 kg phosgene and 1.09 kg 50 % caustic per kg BCF here).

## D-008 Product, yield and the patent's 81 % (2026-11-05)
Decision: the product is the degassed crude, neat, not distilled: 99.2 wt% BCF, 98.9 % yield
on the alcohol (the model). It is kept at 278 K.
Reason: SRC-1 isolates the degassed crude as its product, and the chloroformate decomposes on
heating to benzyl chloride and CO2 (D-011), so a distillation is avoided. The model's purity
(99.2 %) is above Ex. 3's 98.4 % and its yield (98.9 %) far above Ex. 3's 81 % isolated yield.
The impurities match Ex. 3 by construction (D-005); the rest of Ex. 3's loss, 19 % of the
alcohol, is not explained by the patent: its stated impurities account for about 1.2 % of the
product, so the loss is in the laboratory work-up (hold-up, the traps, handling of 0.3 kg),
which the plant model does not have. **The yield is therefore not a sourced value**: a plant
yield between the model's 98.9 % and the laboratory's 81 % is open, and it changes the alcohol
and phosgene per kg in the same ratio. The benchmarks record it (`benchmarks/chlorinated-
organics.yaml`, no_open_reference with Ex. 3's 0.79 kg/kg named).

## D-009 Utilities and heat (2026-11-05)
Decision: chilled brine at 248/253 K for R-101's jacket: Q1 0.71 kW year average (the charge
from 298 to 278 K at 171 kJ/(kmol K)) and Q2 20.03 kW (the heat released, `cheme process
reactors`: 40265 kJ per kmol of charge and doses, the reactions on the gas basis and the doses'
sensible heat, 18.85 kW; plus 1.18 kW, the heat of absorption of the phosgene and HCl left
dissolved in the crude S5, 2.17 kmol phosgene at 24.8 kJ/mol and 0.52 kmol HCl at 10.9 kJ/mol,
59.5 MJ per batch: the latent heat the degassing takes back as Q4, which core leaves out of the
semi-batch, core limit L-10), brine 20.73 kW in all; LP steam 350 kPa(a) to tempered-water
circuits: Q3 7.54 kW for the phosgene evaporator (liquid warmed 40 K at 100 kJ/(kmol K) and evaporated at 24.8 kJ/mol) and Q4 1.18 kW
for the degassing (D-006); cooling water 298/308 K for the scrubber, Q5 44.65 kW (its reactions'
ASSUMED heats, HCl gas into caustic -130.8, phosgene -444, CO2 -109.5 kJ/mol, less the liquor
warmed 10 K); electricity 6.5 kW year average (R-101 agitator 3 kW, vacuum pump 2 kW, scrubber
pump 1.5 kW). All ASSUMED. The duties are hand arithmetic from cheme's reports, written with the
arithmetic in each energy stream's `source` (no balance script): core writes no energy stream
from a model (core limit L-8).
During the 10 h of dosing R-101 removes up to 31.4 kW (19.3 kW per m3 of the final 1.63 m3,
`cheme process reactors`), at 0.46 h; the absorption heat left out (L-10) is small then (the
dissolved phosgene reacts about as fast as it is dosed) and largest near the end of the dosing, about 8.6 kW
(1.255 kmol/h x 24.8 kJ/mol) when the reaction heat has fallen off, well below the jacket's
34.4 kW; the evaporator takes about 10.6 kW while dosing. The brine at 248 K is below the melting point of benzyl alcohol (258 K): the wall temperature must be watched (a
basic-engineering item; a tempered brine at 258 K would need a longer dosing).

## D-010 Materials of construction (2026-11-05)
Decision: enamelled (glass-lined) steel for R-101 and the phosgene and wet-HCl lines, as SRC-2
names for this service; the scrubber in plastic-lined steel or FRP. Not designed further.
Reason: wet HCl and chloroformates corrode steel and stainless steel; iron also catalyses the
chloroformate's decomposition (the secondary source of D-011).

## D-011 Thermal screening and the kinetic sensitivity (2026-11-05)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054): adiabatic temperature rise
474.6 K: this is the heat of the side reaction CLBN (138.4 kJ/mol) on all the alcohol, as core
takes the largest single reaction run to completion (core limit L-1); the main reaction PHOSG
alone (88.6 kJ/mol) gives 303.9 K (a scratch copy with R101 `reactions: [PHOSG]`). Either way the
neat batch has no solvent to take up the heat: an all-in batch would be a runaway. Largest
accumulation of the dosed phosgene 0.173, at the end of the dosing: that is the deliberate
excess, which has almost no alcohol left to react with; MTSR at the worst moment 355.7 K, at
4.2 h into the dosing, against an MTT of 280.65 K (`hazard.mtt`); no TD24 known (never
estimated): no criticality class (`cheme.reactor-hazard-missing`, info) and a
`cheme.reactor-hazard-mtsr` warning (MTSR above MTT). The vent's peak gas rate is 0.216 mmol/(s
m3) at 0.46 h; with the vent blocked it pressurises the vessel (not screened).
- The MTT is set by hand: the default, the lowest normal boiling point of the liquid's
  components, would be the dissolved HCl's 188 K (core limit L-2). Phosgene's normal boiling
  point is taken instead: above it the dissolved phosgene boils off and the reflux condenser,
  the vent and the scrubber, not the jacket, hold the temperature; at the vessel's 50 kPa(a) it
  would be lower still.
- The MTSR of 355.7 K is set by the side reaction CARB: core takes, at each moment, the largest
  potential of any single reaction run to completion, and mid-dosing the chloroformate and the
  alcohol are both present in quantity (core limit L-1). Without CARB (a scratch copy) the MTSR
  is 312.4 K, still set by a side reaction (CLBN's heat on the phosgene accumulated near the end
  of the dosing); with PHOSG alone it is 300.1 K. The hazard numbers are thus those of the side
  reactions; the conclusions below hold for PHOSG alone too (300.1 K is above the MTT).
Kinetic sensitivity (scratch copies, every rate constant divided, all else equal):

| rate constants | peak accumulation | MTSR | MTT | class | post-reaction | cycle | batches/a |
|---|---|---|---|---|---|---|---|
| as designed (k) | 0.173 (end of dosing) | 355.7 K | 280.65 K | none (no TD24) | 0 h | 14.01 h | 565 |
| k/10 | 0.230 (end of dosing) | 384.9 K | 280.65 K | none (no TD24) | 4.6 h | 18.65 h | 425 |
| k/100 | 0.521 (end of dosing) | 571.2 K | 280.65 K | none (no TD24) | 67.0 h | 81.07 h | 98 |

Interpretation: at every rate the MTSR is above the MTT, so a cooling failure during the dosing
boils phosgene off whatever the kinetics: the dosing must stop on high temperature, low cooling
or agitator failure (interlock), the reflux condenser and the scrubber must take the phosgene
then released, and the vessel's relief goes to the scrubber, not to air. With k/100 the
potential (571 K) would reach the chloroformate's decomposition range (vigorous at 155 C, 428
K, by the secondary source) and the cycle would rule out the design; with k/10 the cycle grows by
a third. Open for the next stage: reaction calorimetry with gas dosing (heat and gas flow), the
TD24 of the crude and of the product (DSC, ARC), the phosgene solubility, the vent and relief
sizing with the gas-generation term, the phosgene containment (enclosure, detection,
emergency scrubber). Screening values only, not a reaction-hazard assessment.

## D-012 Preliminary gate-to-gate LCI (2026-11-05)
Decision: `cheme assess lca --write` per kg of neat BCF from the flowsheet's year averages;
phosgene, caustic soda and the nitrogen consumable linked to phosgene-1, chlor-alkali-1 and
asu-1 (`lca/mappings.yaml`), the LP steam counted as heat (kWh); every other background a gap
with the activity it should connect to; benzyl alcohol a gap (no library producer, D-004; no
proxy, which would be a guess). The nitrogen of the purges, the vacuum break and the transfer
padding (12 Nm3, 15 kg per batch, ASSUMED) is an `lca.yaml` consumable `per_batch` (core ADR 0053,
library ADR 0035): 8.5 g/kg BCF at 565 batches a year. There is no rinse: the train is kept dry
(the chloroformate and phosgene hydrolyse). Not counted (emission_exclusions): the scrubbed vent
to the stack (traces, D-007) and fugitive phosgene.
Per kg BCF: benzyl alcohol 0.636 kg, phosgene 0.738 kg, caustic 50 wt% 1.086 kg, process water
4.34 kg, nitrogen 8.5 g, electricity 0.051 kWh, LP steam 0.069 kWh, brine 0.164 kWh removed,
cooling water 0.354 kWh removed, spent liquor 5.80 kg.

## D-013 Dedicated train (2026-11-05)
Decision: R-101, E-102, K-201 and T-201 make only BCF, batch after batch: 565 batches in 7920 h
on a dedicated train (ASSUMED, library ADR 0035).
Reason: one product per process folder (library ADR 0002); a share of a multipurpose train
cannot be checked without the other products' campaigns.
Out of scope, so not LCI gaps: the changeover cleaning between campaigns of other products, the
idle time of a multipurpose train, shared tank farms. Chloroformates are often made in campaigns
on a multipurpose phosgenation plant: there the burden per kg is higher, and this LCI is a lower
bound for it.

## Core features used (core main 7334d7c, to be 1.8.0)

- `batch.vent: {stream, components, fraction}` (ADR 0054): HCl and CO2 leave R101 as they form,
  95 % and 100 %, by the vent stream S6; the liquid's volume and concentrations are without them.
- `dosing.absorbed` (ADR 0054): 95 % of the phosgene gas dissolves, 5 % passes to the vent,
  cooled to the vessel with its ideal-gas cp.
- `cheme process recipe` vent report (ADR 0054): the vent's peak rate (kmol/s, m3/h at the
  vessel) and what one batch gives off, the scrubber's basis.
- `still:` with `volatility: {model: constant}`, `nonvolatile`, `boilup` in kmol/h, `end:
  {residue: {key, mole_fraction}}` (ADR 0055): the degassing T101 with its gas, time and duty per
  batch (`cheme process stills`); recipe `distil` `from: T101`.
- recipe `units: [E101, R101, T101]` (ADR 0057): one vessel over three flowsheet steps, sized
  from the semi-batch and occupied once.
- From 1.7.0: `reactor: semibatch`, recipe `from:` for dose and react, vessel sizing and the
  jacket check, a `cool` operation timed by the jacket (ADR 0050 to 0052), `per_batch`
  consumables (ADR 0053), `hazard.mtt`.
- Not used: `crystallizer.spectators`, `kind: phase-change` (ADR 0056) and `dryer:`,
  `filtration:` (ADR 0057): the process has no solids.

## Core limits hit (to become core issues)

- L-1: the adiabatic rise and the MTSR take the largest potential of any one reaction run to
  completion (the MTSR at each moment). The side reactions set both: dT_ad 474.6 K is CLBN's
  heat (the benzyl chloride route, about 0.7 % of the alcohol converted) on all the alcohol, against 303.9 K for
  PHOSG alone; a slow side reaction between the product and the charge (CARB, chloroformate +
  alcohol) sets the MTSR (355.7 K; 312.4 K without CARB, then set by CLBN; 300.1 K with PHOSG
  alone): there is no way to say which reactions a cooling failure completes, or to screen the desired reaction's accumulation alone as Stoessel
  does and the side reactions through their own rates. The accumulation also counts a deliberate
  excess of the dosed reagent (0.173 at the end) although nothing is left to react with it.
- L-2: the default MTT is the lowest normal boiling point of the liquid's components, so a
  dissolved gas that is partly vented (HCl at 5 %, 188 K) makes it meaningless; and it ignores
  the vessel's pressure (50 kPa(a) here). `hazard.mtt` was set by hand.
- L-3: the screening has no gas-generation term (the vent blocked, ADR 0054 follow-up) and no
  toxic-release consideration (phosgene): for this process the vent and scrubber are the
  safety-critical path, and the screening says so only in a note.
- L-4: `vent.fraction` and `dosing.absorbed` are fixed shares: no solubility or Henry's law, so
  the reduced pressure, which SRC-1 shows is what drives the conversion, has no effect in the
  model; no headspace or reflux condenser (the phosgene that evaporates and is returned).
- L-5: the still has no inert stripping gas (a nitrogen sparge) and no Henry-law volatility for a
  dissolved gas: constant relative volatilities stand in. It writes the non-volatile components
  at 0 into the distillate's composition, so the off-gas template must list them.
- L-6: the recipe reports the semi-batch's vent per batch but not the still's distillate that
  goes to the same scrubber: the scrubber's load per batch (662 kg) is added by hand from two
  reports. A per-batch off-gas total by destination (or for a named downstream step) would close
  it.
- L-7: propagate has no specified component separator (component recoveries to two outlets): the
  scrubber's scrubbed vent cannot be split from its liquor, so the traces and the stack emission
  are an exclusion.
- L-8: no model writes or checks an energy stream's duty for a semi-batch, a still or a
  conversion step (the dryer's `cheme.process-dryer-duty` exists): Q2, Q4 and Q5 are copied by
  hand from `cheme process reactors`, `stills` and `streams` and do not go stale when the model
  changes.
- L-9: no property package for the reaction mass (organics with dissolved HCl and phosgene) or
  the caustic liquor: liquid volumes and heat capacities are per-component inputs, the scrubber's
  heats ASSUMED.
- L-10: `dosing.absorbed` and the dissolved share of a vented component have no heat of
  absorption (the semi-batch dissolves them on entry with no heat, its heats of reaction are on
  the gas basis), while the still counts their desorption with `heat_of_vaporization`: the energy
  accounting is one-sided. Q2 adds the absorption heat of what S5 holds dissolved by hand
  (4247 kJ/h, 1.18 kW; D-009), and the recipe's peak duty and jacket check leave it out.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with vent and gas dose: composition, accumulation, cooling-failure temperature, peak cooling, peak gas rate | done in cheme, kinetics and gas shares ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| degassing | done in cheme (batch still, constant volatilities ASSUMED) | D-006, `cheme process stills` |
| off-gas scrubber | conversion step, conversions ASSUMED | D-007 |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| vessel sizing, jacket check | done in cheme | D-003, core ADR 0052 |
| duties | hand arithmetic from cheme's reports | D-009, L-8 |
| per-batch exchanges (nitrogen) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Open inputs
Kinetics and heat flow with gas dosing (calorimetry), the TD24 of the crude and the product;
the solubility of phosgene and HCl in the reaction mass at 50 kPa(a); the plant yield (D-008);
the product specification (assay, free phosgene, HCl, benzyl chloride, colour, stabiliser); the
reflux condenser and the phosgene recovery (D-007); the HCl recovery; the vent and relief
design; a TEA (`operation.batch: {recipe: true}`).
