# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Benzyl chloroformate (BCF, Cbz-Cl) by the phosgenation of benzyl alcohol, issue
ChemE-as-Code/process-library#153. Concept stage: design basis, batch recipe, balanced BFD/PFD,
thermal screening and a preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP,
TEA, datasheets.

Starting point (2026-11-05): library `main` at 77fa11c2; built on cheme-as-code core
`main` at 7334d7c and rechecked on the release, 1.8.0 (4e8fd80). Moved to core 1.9.0 (314642c)
on 2026-11-06, when the library's pin went to it: the model's duties of R101 and T101 (ADR 0059)
and the semi-batch screening's reactions, MTSR profile and gas release against the vent's
capacity (ADR 0058) are used. Moved to core 1.10.0 (c55e9c7) on 2026-11-06: the absorbed
phosgene's heat of solution is the dose's `heat_of_solution` with the heats of reaction on the
dissolved basis (ADR 0063), replacing the hand stream Q2A (D-015), so the entry needs 1.10
(plant.yaml `requires`; see "Core features used").

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
U 250 W/(m2 K) of an enamelled vessel with brine at 248 K (ASSUMED) removes 34.35 kW over the
4.58 m2 the charge wets, against the model's peak duty of 31.65 kW, which since core 1.10.0
holds the heat of solution of the phosgene as it is dosed (D-015; 31.41 kW without it on 1.9.0;
no `cheme.recipe-jacket` finding). The dosing time of 10 h is set by this check: 8 h gives a
39.52 kW peak above what the jacket removes (a scratch copy on 1.10.0; 39.2 kW on 1.9.0).
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
Heats: from formation enthalpies with phosgene, HCl and CO2 as gases (SRC-3, SRC-4), PHOSG
-88.6 kJ/mol and CLBN -138.4 kJ/mol; CARB -30 kJ/mol ASSUMED (no formation enthalpy of dibenzyl
carbonate). Since core 1.10.0 they are written on the dissolved basis of phosgene (D-015): the
dose releases the absorbed phosgene's heat of solution (-24.8 kJ/mol, ASSUMED) as it dissolves,
the reactions consume dissolved phosgene (+24.8 kJ/mol each), and 5 % of the HCl each forms
stays dissolved (-0.55 kJ/mol): PHOSG -64.39, CLBN -114.16, CARB -30.55 kJ/mol.
Reason: no open kinetics exist (searched 2026-11-05). The fast effective rate makes the step
dosing-controlled, as SRC-1's 0-6 C operation with a cold condenser suggests; it is an ASSUMED
placeholder for reaction calorimetry. The absorbed and vent shares are ASSUMED stand-ins for the
unknown solubilities: at 50 kPa(a) and 278 K phosgene is near its boiling point (about 264 K at
50 kPa), and the share that passes stands for the phosgene the vent's HCl carries off past the
reflux condenser; HCl, far above its boiling point, mostly leaves. Core 1.10.0's vent vapour
(ADR 0062), tried on a scratch copy, does not support a brine condenser holding most of it
back (D-015): the share stays a placeholder.
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

## D-009 Utilities and heat (2026-11-05, core 1.9.0 and 1.10.0 2026-11-06)
Decision: chilled brine at 248/253 K for R-101's jacket, on two streams: Q1 0.71 kW year
average (the charge from 298 to 278 K at 171 kJ/(kmol K)); and Q2 19.88 kW, the semi-batch
model's year-average duty (R101 `energy_port: q`, written by `cheme process propagate --fill`,
core ADR 0059 and 0063): the reactions on the dissolved basis 13.33 kW, the absorbed phosgene's
heat of solution 6.17 kW (the dose's `heat_of_solution`, D-015), the doses cooled from 293 to
278 K 0.373 kW and the vented share of the dose 0.011 kW; brine 20.59 kW in all. Q2 holds the
heat of absorption of the phosgene and HCl left dissolved in the crude S5 (2.17 kmol phosgene at
24.8 kJ/mol and 0.52 kmol HCl at 10.9 kJ/mol, 59.5 MJ per batch, 1.18 kW: the latent heat the
degassing takes back as Q4), which the hand stream Q2A carried on core 1.9.0 (D-015). LP steam
350 kPa(a) to tempered-water circuits: Q3 7.54 kW for the phosgene evaporator (liquid warmed 40
K at 100 kJ/(kmol K) and evaporated at 24.8 kJ/mol) and Q4 1.177 kW for the degassing, the
still model's year-average duty (written by propagate, ADR 0059; D-006); cooling water 298/308 K
for the scrubber, Q5 44.65 kW (its reactions' ASSUMED heats, HCl gas into caustic -130.8,
phosgene -444, CO2 -109.5 kJ/mol, less the liquor warmed 10 K); electricity 6.5 kW year average
(R-101 agitator 3 kW, vacuum pump 2 kW, scrubber pump 1.5 kW). Q1, Q3, Q5 and the power are
ASSUMED hand arithmetic, written with the arithmetic in each energy stream's `source` (no
balance script): the charge cooling and the evaporator are pass-through steps with no model,
and core cannot give S101's duty (L-8).
Why Q2 was split on 1.9.0 (2026-11-06): on 1.8.0, Q2 was typed by hand as 20.03 kW, the 1.8
report's heat released (40265 kJ per kmol of charge and doses, 18.85 kW) plus the 1.18 kW of
absorption. Core 1.9.0 computed the semi-batch's duty itself, 18.70 kW from the extents of PHOSG,
CARB and CLBN on the gas basis and the doses' sensible heat, and flagged the typed value
(`cheme.process-duty`, 20.03 against 18.7043 kW). The model's figure replaced the hand value,
which was wrong by 0.14 kW: the 1.8 report's 40265 kJ/kmol is the reaction heat per kmol of the
charge and the absorbed dose (0.74232 + 0.95 x 0.94274 kmol/h gives 18.32 kW, the 1.9.0 model's
reaction term), but the hand value multiplied it by the whole dose (0.53 kW too much) and left
out the doses' cooling it named (0.37 kW). The heat of absorption, which the 1.9.0 model left
out, had its own ASSUMED stream Q2A (1.18 kW) to the same brine. On core 1.10.0 the model holds
it (D-015): Q2 19.884 kW is the 1.9.0 model's 18.7043 kW plus Q2A's 1.18 kW to 0.0003 kW, and the
brine stays 20.59 kW.
Q4's hand value (1.178 kW) agreed with the still model and is now written by it (1.17705 kW).
During the 10 h of dosing R-101 removes up to 31.65 kW (19.47 kW per m3 of the final 1.63 m3,
`cheme process reactors`); since core 1.10.0 that peak holds the heat of solution, released at
the dose's rate, about 8.6 kW all through the dosing (1.255 kmol/h x 24.8 kJ/mol), while the
reactions on the dissolved basis release that much less when the phosgene reacts as fast as it
is dosed, so the peak rose only 0.24 kW (31.41 kW on 1.9.0). The heat of solution is largest in
share near the end of the dosing, when the reaction heat has fallen off, well below the jacket's
34.35 kW; the evaporator takes about 10.6 kW while dosing. The brine at 248 K is below the
melting point of benzyl alcohol (258 K): the wall temperature must be watched (a
basic-engineering item; a tempered brine at 258 K would need a longer dosing).

## D-010 Materials of construction (2026-11-05)
Decision: enamelled (glass-lined) steel for R-101 and the phosgene and wet-HCl lines, as SRC-2
names for this service; the scrubber in plastic-lined steel or FRP. Not designed further.
Reason: wet HCl and chloroformates corrode steel and stainless steel; iron also catalyses the
chloroformate's decomposition (the secondary source of D-011).

## D-011 Thermal screening and the kinetic sensitivity (2026-11-05, core 1.9.0 and 1.10.0 2026-11-06)
Result (`cheme process reactor-hazards`, core ADRs 0050, 0054, 0058, 0063): adiabatic
temperature rise 494.0 K: this is the heat of the side reaction CLBN on the dissolved basis
(114.2 kJ/mol) on all the alcohol, 391.4 K, as core takes the largest counted reaction run to
completion (core limit L-1), plus the heat of solution of the whole absorbed dose, 102.6 K,
which core 1.10.0 counts in dT_ad (ADR 0063); the main reaction PHOSG alone (64.4 kJ/mol on the
dissolved basis) gives 220.8 K (`per_reaction`, the same run), 323.4 K with the heat of solution.
On core 1.9.0, with the heats on the gas basis and no heat of solution, these were 474.6 and
303.9 K: the gas basis left out the dissolution of the excess phosgene (0.21 mol per mol of
alcohol) and of the retained HCl, so the 1.10.0 values are the more complete ones (D-015).
Either way the neat batch has no solvent to take up the heat: an all-in batch would be a
runaway. Largest accumulation of the dosed phosgene 0.173, at the end of the dosing: that is the
deliberate excess, which has almost no alcohol left to react with; MTSR at the worst moment 357.1
K (355.7 K on 1.9.0), at 4.2 h into the dosing, against an MTT of 280.65 K (`hazard.mtt`); the
heat of solution is not in the MTSR, as it is released when the phosgene mixes in and nothing of
it is accumulated when the dosing stops (ADR 0063); no TD24 known (never
estimated): no criticality class (`cheme.reactor-hazard-missing`, info) and a
`cheme.reactor-hazard-mtsr` warning (MTSR above MTT), which is a real finding and stays. The
MTSR over the batch (`mtsr_profile`) rises from 278 K at the start to 357.1 K at 4.2 h, falls to
about 302 K at 8 h and to 278.3 K at the end of the dosing, where the accumulated phosgene is
the excess with no alcohol left. The vent's peak gas rate in normal operation is 0.216 mmol/(s
m3) at 0.46 h; the gas a cooling failure releases is compared with the vent in D-014
(`cheme.reactor-hazard-vent`, a warning and a finding).
- The MTT stays set by hand (`hazard.mtt` 280.65 K). Core 1.9.0's default no longer takes the
  dissolved HCl's 188 K (vent components and the dosed gas are left out, ADR 0058), but what it
  then takes is benzyl alcohol's normal boiling point, 478.4 K (a scratch copy without
  `hazard.mtt`): the dosed phosgene is left out because it "boils off rather than boils the
  batch". Here that boil-off is the hazard: up to 17 % of the dose, toxic, dissolved in the
  batch. Phosgene's normal boiling point is kept: above it the dissolved phosgene boils off and
  the reflux condenser, the vent and the scrubber, not the jacket, hold the temperature; at the
  vessel's 50 kPa(a) it would be lower still. With the default the MTSR warning would go,
  which would hide this finding. Core still screens no dissolved toxic gas boiling off (ADR
  0058 known limitation, L-3).
- Reactions counted (`hazard.reactions: [PHOSG, CARB, CLBN]`, stated on purpose, the same set as
  the default): all three. The MTSR of 357.1 K is set by the side reaction CARB, the product
  with the alcohol left (chloroformate + alcohol -> dibenzyl carbonate + HCl): mid-dosing both
  are present in quantity, about half of the charge each. CARB stays counted, which is the
  conservative choice. A cooling failure leaves the product and the alcohol together, hot, for
  as long as it lasts, and nothing stops CARB then. Its rate law and its heat (-30 kJ/mol) are
  ASSUMED placeholders (D-005), so no data show it too slow to matter on the time scale of a
  cooling failure. With its Ea of 40 kJ/mol it runs 46 times faster at 357.1 K than at 278 K.
  The patent's phosgene excess is there to suppress it (SRC-1), and iron catalyses the
  chloroformate's decomposition (D-010). CLBN takes the same reactants as PHOSG, the accumulated
  phosgene, and cannot be separated from it. Leaving CARB out (`[PHOSG, CLBN]`) would need
  calorimetry of the mid-dosing mass showing CARB's heat flow negligible over a cooling
  failure. Each reaction alone, from the same run (`per_reaction`): PHOSG MTSR 294.1 K at 8.2 h,
  CLBN 306.5 K at 8.2 h, CARB 357.1 K at 4.2 h (on 1.9.0, gas basis: 300.2, 312.5 and 355.7 K).
  PHOSG's and CLBN's MTSR fell on 1.10.0 because the accumulated phosgene is dissolved and has
  released its heat of solution already: reacting, it gives the dissolved-basis heat. The
  conclusions below hold for PHOSG alone too (294.1 K is above the MTT).
Kinetic sensitivity (scratch copies on core 1.10.0, every rate constant divided, all else
equal; the MTSR on 1.9.0 in brackets):

| rate constants | peak accumulation | MTSR | MTT | class | post-reaction | cycle | batches/a |
|---|---|---|---|---|---|---|---|
| as designed (k) | 0.173 (end of dosing) | 357.1 K (355.7) | 280.65 K | none (no TD24) | 0 h | 14.01 h | 565 |
| k/10 | 0.230 (end of dosing) | 366.2 K (384.9) | 280.65 K | none (no TD24) | 4.6 h | 18.65 h | 425 |
| k/100 | 0.521 (end of dosing) | 519.8 K (571.2) | 280.65 K | none (no TD24) | 67.0 h | 81.07 h | 98 |

Interpretation: at every rate the MTSR is above the MTT, so a cooling failure during the dosing
boils phosgene off whatever the kinetics: the dosing must stop on high temperature, low cooling
or agitator failure (interlock), the reflux condenser and the scrubber must take the phosgene
then released, and the vessel's relief goes to the scrubber, not to air (D-014). With k/10 and
k/100 the MTSR is set by CLBN on the accumulated phosgene, so the dissolved basis lowers it
most there. With k/100 the potential (520 K) would reach the chloroformate's decomposition range (vigorous at 155 C, 428
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
4.34 kg, nitrogen 8.5 g, electricity 0.051 kWh, LP steam 0.069 kWh, brine 0.163 kWh removed
(Q1 and Q2, D-009; Q2 holds the heat of absorption since core 1.10.0, D-015, the same total as
Q2 and Q2A on 1.9.0; 0.164 before the duty split of 2026-11-06),
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

## D-014 Gas release at a cooling failure against the vent: a design finding (2026-11-06, core 1.10.0 the same day)
Decision: R101 `hazard.vent_capacity` 173 m3/h, ASSUMED. That is the suction volume of the
vacuum pump K-201, about 173 m3/h at 20 kPa(a) and 278 K (1.5 kmol/h, D-006). The pump is the
only path the gas has out of R-101 at its 50 kPa(a): the vent S6 goes through it to the scrubber
(D-007). A dry-running pump's displacement is taken as about the same at 50 kPa(a) as at 20.
No relief device is designed yet, so none is counted.
Result (`cheme process reactor-hazards`, core ADR 0058, on 1.10.0): the gas the vent components
form at the MTSR is 0.01506 kmol/s, 3219 m3/h at 357.1 K and 50 kPa(a), from the content at the
worst moment (4.2 h). That is **18.6 times the vent capacity**: the warning
`cheme.reactor-hazard-vent` stands, a finding, not silenced. Run to completion, CARB would form
4.891 kmol of HCl (290 m3 at the MTSR and 50 kPa(a)) from that content. On core 1.9.0 it was
0.01427 kmol/s, 3039 m3/h at 355.7 K, 17.6 times: the dissolved basis (D-015) raises CARB's heat
by its retained HCl (0.55 kJ/mol), so the MTSR is 1.4 K higher and the rate laws at it 6 % faster.
What the rate is (hand estimate from the rate laws of `process/reactions.yaml` at 357.1 K, for
reading the number only): nearly all of it is PHOSG and CLBN on the accumulated phosgene. At the
worst moment that is about 0.08 kmol (X_ac 0.0066 of the dose), taken whole at the MTSR, which
CARB's heat sets. CARB itself at the MTSR forms about 8 m3/h, within the pump. The bound is
therefore loose in time: the accumulated phosgene lives about 4 min even at 278 K and would be
gone before CARB's slow heat brought the mass to 357.1 K. The gas over the cooling failure's
course, CARB's 4.9 kmol of HCl, is slow but large: with the vent blocked, the 1.2 m3 head space
of R-101 could not hold it. With PHOSG alone counted (scratch copy on 1.10.0, `hazard.reactions:
[PHOSG]`) the release is 97 m3/h at its 294.1 K MTSR, 0.56 times the vent (137 m3/h at 300.2 K,
0.79 times, on 1.9.0). That set is not a valid one: CLBN takes the same accumulated phosgene and
cannot be separated from PHOSG (D-011). With PHOSG and CLBN it is 195 m3/h at 306.5 K, 1.13
times (269 m3/h at 312.5 K, 1.56 times, on 1.9.0), the least that is left if calorimetry shows
CARB slow. These two fell on 1.10.0 because the accumulated phosgene, already dissolved, reacts
with the dissolved-basis heat. Neither choice is taken, for the reasons of D-011.
Finding and what the design must do (open for basic engineering, not designed here):
- the phosgene dosing stops on high temperature, low brine flow or a high brine temperature,
  agitator failure and high pressure in R-101 (interlock, SIL from the LOPA). It keeps the
  accumulation at the trip to the dissolved phosgene then, at most 0.0066 of the dose
  mid-dosing;
- no isolation between R-101 and K-201 without a relief path. K-201 and the scrubber's pump
  run on emergency power;
- an emergency relief of R-101 (rupture disc and safety valve) sized by the DIERS method for the
  gas generation, with two-phase flow checked, to a catch tank and the scrubber or an emergency
  phosgene absorber, never to air. The scrubber T-201 is sized for the normal peak of 58 m3/h
  and must take the relief flow, or a separate absorber must;
- reaction calorimetry with gas flow (D-005, D-011) measures the gas rate and the accumulation
  of a cooling failure mid-dosing. If CARB is confirmed slow, the release is that of PHOSG and
  CLBN, which cannot be separated (D-011): about 195 m3/h by the screening, still 1.13 times
  K-201's capacity, so the emergency relief stays needed (with less margin than on 1.9.0's 1.56
  times, so calorimetry decides it the more). K-201 or the relief is sized against
  the measured rate.

## D-015 Core 1.10.0: the phosgene's heat of solution in the semi-batch model (2026-11-06)
Decision: R101's dose S4 gets `heat_of_solution: {values: {COCL2: -24800}}` (core ADR 0063),
ASSUMED: the absorbed phosgene's heat of solution in the crude taken as minus its heat of
vaporization at 278.15 K (an ideal solution; SRC-4), the same 24.8 kJ/mol the degassing T101
takes back (D-006); no open solubility or heat of solution of phosgene in benzyl alcohol or the
chloroformate was found (2026-11-05). The heats of PHOSG, CARB and CLBN are then written on the
dissolved basis (`process/reactions.yaml`), as ADR 0063 requires so that the absorption is not
counted twice: +24.8 kJ/mol per mol of phosgene consumed, and -0.55 kJ/mol for the 5 % of each
mol of HCl formed that stays dissolved (the vent's `fraction`; core has no heat of solution for
a vented gas's retained share and ADR 0063 says to write it into the heat of reaction, at minus
HCl's heat of vaporization at 278.15 K, 10.91 kJ/mol): PHOSG -64.389, CLBN -114.163, CARB
-30.546 kJ/mol. The hand stream Q2A (1.18 kW), R101's port `q_abs`, REACT's `brine_abs` and
BRINE's `r101_abs` are removed.
Check against the hand value: the model's Q2 is 19.884 kW, the 1.9.0 model's 18.7043 kW plus
Q2A's 1.18 kW (4247 kJ/h) to 0.0003 kW. Its terms: the reactions on the dissolved basis 13.330
kW (18.320 kW on the gas basis), the heat of solution of all the absorbed phosgene 6.170 kW, the
doses cooled 0.373 kW and the vented share 0.011 kW; the heat of solution less what the
reactions now release less is the 1.18 kW of phosgene and HCl that S5 keeps dissolved. The
heats change only the duty of an isothermal batch: no stream changed (propagate wrote new
fingerprints for S5 and S6 and the new Q2), so the LCI per kg is the same (brine 0.163 kWh/kg,
now Q1 and Q2). Adopted: the model reproduces the hand value and now carries it where the hand
stream did not reach: the recipe's jacket check (peak 31.65 kW, 31.41 kW without it; 34.35 kW
removable, D-003) and the screening. The screening moves (D-011, D-014): dT_ad 494.0 K (474.6 K)
with the dose's heat of solution counted, 102.6 K; PHOSG alone 220.8 K, 323.4 K with the heat of
solution (303.9 K); MTSR 357.1 K (355.7 K), CARB's by its retained HCl; PHOSG alone 294.1 K
(300.2 K), CLBN 306.5 K (312.5 K); the gas release at the MTSR 3219 m3/h, 18.6 times the vent
(3039 m3/h, 17.6 times). The dissolved basis is the more credible one for the screening: on the
gas basis the accumulated phosgene, already dissolved and its absorption heat already removed
by the jacket, released that heat a second time when it reacted after a cooling failure, while
the dissolution of the excess phosgene and the retained HCl was left out of dT_ad.
Not adopted (core 1.10.0 features that do not fit this step, with the reason):
- `batch.vent.vapour` with a `condenser` (ADR 0062), tried on a scratch copy with phosgene's
  Antoine constants fitted to thermo's vapour pressure (213-295 K, within 0.12 %, SRC-4) and a
  brine condenser at 253.15 K returning its condensate: the vent carries a further 0.022 kmol/h
  of phosgene off the liquid (Raoult over an ideal crude; phosgene 0.27 of the vent gas at the
  end of the dosing), and the condenser condenses none: the phosgene's partial pressure in the
  vent, about 13 kPa at most, is below its vapour pressure at 253 K (30.6 kPa); the gas would
  have to be cooled below its dew point, about 238 K at the end of the dosing and lower before,
  to return any (SRC-1 uses a dry-ice trap). Two findings follow, recorded rather than adopted:
  the assumed `absorbed: 0.95` and the vapour would both count the phosgene the vent's HCl
  carries off, so the one cannot be added to the other; and D-005's earlier reason, that a
  brine reflux condenser returns most of what evaporates, does not hold against Raoult. Raoult
  over an ideal crude without a measured solubility is no better evidence than the assumed
  share, and adopting it means redoing the dose's passing share, the vent and the cycle (13.81 h
  on the scratch copy): the share stays the placeholder of D-005, and the phosgene condenser (or
  the recovery of D-007) is open for basic engineering.
- `vent.henry` for the HCl: no open solubility of HCl in benzyl alcohol or the chloroformate
  (searched 2026-11-05); the fixed `fraction` stays.
- `still.column` and `purity` (ADR 0061): T101 is a degassing, not a rectification, and the
  product is not distilled (D-008).
- `still.heat_up` needs `volatility: raoult` (a schema error at constant volatility); T101
  degasses at the reaction temperature.
- `vessel.metal_heat_capacity`: the recipe gives no metal for R-101 (no vessel mass is sourced;
  the equipment list holds none), so none is added. It would change little here: T101 at
  constant volatility models no temperature and leaves the metal out (ADR 0063), R101 without
  `heat_up` too; only the jacket-timed cool-down (0.22 h) would lengthen. Open for basic
  engineering with the vessel's mass.
- `batch.heat_up` on R101: the charge enters at 278 K, cooled by E101 (Q1, one heat capacity
  over 20 K), so the batch has nothing to heat up; folding E101 into R101 would change the
  flowsheet for a 0.71 kW stream.

## Core features used (core 1.10.0)

- Core 1.10.0, ADR 0063: R101's dose S4 `heat_of_solution` (phosgene, -24.8 kJ/mol, ASSUMED)
  with the heats of PHOSG, CARB and CLBN on the dissolved basis: the semi-batch's duty on Q2
  holds the heat of absorption (the term `solution`, 6.17 kW), the peak cooling duty and the
  recipe's jacket check take it (31.65 kW), and the screening counts it in dT_ad (102.6 K, not
  in the MTSR). The hand stream Q2A is gone (D-015).
- Not used (D-015): `batch.vent.vapour`, `vent.condenser` and `vent.henry` (ADR 0062; tried on a
  scratch copy, a finding recorded), `still.column`, `purity`, `still.condenser_port` (ADR
  0061), `still.heat_up`, `batch.heat_up` and `vessel.metal_heat_capacity` (ADR 0063).

From core 1.9.0:

- Core 1.9.0, ADR 0059: R101's `energy_port: q`, so that `cheme process propagate --fill` writes
  the semi-batch's year-average duty on Q2 (19.884 kW on 1.10.0, 18.7043 kW on 1.9.0); T101's
  still duty on Q4 (1.17705 kW), its one heat stream. Both are `calculated` and go stale with
  the model.
- Core 1.9.0, ADR 0058: `hazard.reactions` (stated, all three, D-011), `per_reaction` (each
  reaction's dT_ad and MTSR in one run), the `mtsr_profile`, and the gas release at the MTSR
  against `hazard.vent_capacity` (D-014). `hazard.mtt` stays set by hand (D-011).
- Not used: `tears:` (ADR 0060). The plant has no recycle: no phosgene or HCl is recovered
  (D-007).

From core 1.8.0:

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

Status on core 1.10.0 (2026-11-06): L-10 is resolved; L-1, L-2, L-3, L-4 and L-8 are partly
resolved (each says what is left); L-5 to L-7 and L-9 stand.

- L-1: the adiabatic rise and the MTSR take the largest potential of any one counted reaction
  run to completion (the MTSR at each moment). The side reactions set both: the adiabatic rise
  of 494.0 K is CLBN's heat (the benzyl chloride route, about 0.7 % of the alcohol converted) on
  all the alcohol plus the dose's heat of solution (core 1.10.0, D-015), against 323.4 K for
  PHOSG alone with it (220.8 K without); a slow side reaction between the product and the
  charge (CARB, chloroformate + alcohol) sets the MTSR (357.1 K; 306.5 K for CLBN, 294.1 K for
  PHOSG alone).
  **Partly resolved in core 1.9.0** (ADR 0058): `hazard.reactions` names the reactions counted
  and `per_reaction` gives each one's dT_ad and MTSR in one run, so the main reaction is no
  longer hidden and no scratch copies are needed (D-011). Still open: each reaction is run to
  completion alone, never at its own rate, so a slow side reaction is either counted whole or
  not at all. The accumulation also counts a deliberate excess of the dosed reagent (0.173 at the
  end) although nothing is left to react with it (ADR 0058 known limitation).
- L-2: on 1.8.0 the default MTT was the lowest normal boiling point of the liquid's components,
  so a dissolved gas that is partly vented (HCl at 5 %, 188 K) made it meaningless, and it
  ignored the vessel's pressure (50 kPa(a) here). **Resolved in core 1.9.0** (ADR 0058) for
  HCl and the pressure: vent components, dosed gases and minor dissolved gases are left out,
  and under vacuum a component with `heat_of_vaporization` boils at the vessel's pressure.
  Still set by hand here (D-011): the default leaves the dosed phosgene out and takes benzyl
  alcohol's 478.4 K (at its normal boiling point, as the alcohol has no
  `heat_of_vaporization` in materials.yaml). A dissolved toxic gas that boils off has no MTT of
  its own.
- L-3: on 1.8.0 the screening had no gas-generation term. **Partly resolved in core 1.9.0**
  (ADR 0058): the gas release at the MTSR is compared with `hazard.vent_capacity` (D-014). Still
  open: the rate takes the worst moment's content whole at the MTSR (a loose bound in time,
  D-014), there is no blocked-vent pressure (no head-space or relief model), and no
  toxic-release term for the phosgene that boils off.
- L-4: `vent.fraction` and `dosing.absorbed` are fixed shares: no solubility or Henry's law, so
  the reduced pressure, which SRC-1 shows is what drives the conversion, has no effect in the
  model; no headspace or reflux condenser (the phosgene that evaporates and is returned).
  **Partly resolved in core 1.10.0** (ADR 0062): a vent gas may take a Henry constant
  (`vent.henry`), and the vent may carry the liquid's vapour through a partial condenser
  (`vent.vapour`, `vent.condenser`). Not adopted here (D-015): no open Henry constant of HCl in
  the crude, and the vapour of the dissolved phosgene would count again what `absorbed`
  already passes. Still open: a dosed gas's uptake is a fixed share (no Henry for a dose), and
  the head space is not modelled.
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
- L-8: on 1.8.0 no model wrote or checked an energy stream's duty for a semi-batch, a still or
  a conversion step, so Q2, Q4 and Q5 were copied by hand and did not go stale with the model.
  **Resolved in core 1.9.0 for R101 and T101** (ADR 0059): Q2 and Q4 are written by `propagate
  --fill` (D-009). The check found the hand Q2 0.14 kW high. Still open for the scrubber S101:
  the conversion-step duty needs the liquid heat capacities of the liquor's water and salts
  (`cheme.process-duty`, info). Its heats of reaction are also on the gas basis while the gas
  inlet S9 is vapour and its traces leave in the liquid, which ADR 0059 leaves unknown. Q5
  stays ASSUMED hand arithmetic.
- L-9: no property package for the reaction mass (organics with dissolved HCl and phosgene) or
  the caustic liquor: liquid volumes and heat capacities are per-component inputs, the scrubber's
  heats ASSUMED.
- L-10: on 1.9.0 `dosing.absorbed` and the dissolved share of a vented component had no heat of
  absorption (the semi-batch dissolved them on entry with no heat, its heats of reaction on the
  gas basis), while the still counts their desorption with `heat_of_vaporization`: the energy
  accounting was one-sided, and the absorption heat of what S5 holds dissolved (4247 kJ/h, 1.18
  kW) was its own ASSUMED stream Q2A, left out of the recipe's peak duty and jacket check.
  **Resolved in core 1.10.0** (ADR 0063, D-015): the dose's `heat_of_solution` with the heats of
  reaction on the dissolved basis puts it in Q2 (19.884 kW = 18.7043 + 1.18), the peak cooling
  duty and the jacket check, and the screening's dT_ad. Left over: a vented gas's retained share
  has no heat of solution of its own (ADR 0063 limitation), so the 5 % of HCl that stays
  dissolved is written into the heats of reaction (-0.55 kJ/mol each).

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate |
| semi-batch R-101 with vent and gas dose: composition, accumulation, cooling-failure temperature, peak cooling, peak gas rate | done in cheme, kinetics and gas shares ASSUMED | D-005, D-011, `cheme process reactors`, `reactor-hazards` |
| degassing | done in cheme (batch still, constant volatilities ASSUMED) | D-006, `cheme process stills` |
| off-gas scrubber | conversion step, conversions ASSUMED | D-007 |
| batch recipe, cycle time, basis check | done in cheme | D-003, `cheme process recipe` |
| vessel sizing, jacket check | done in cheme | D-003, core ADR 0052 |
| duties | R101 (Q2, with the phosgene's heat of solution, core ADR 0063) and T101 (Q4) done in cheme (models' year averages, core ADR 0059); Q1, Q3, Q5, power hand arithmetic, ASSUMED | D-009, D-015, L-8 |
| gas release at a cooling failure against the vent | done in cheme (screening bound); vent capacity ASSUMED; relief not designed | D-014, core ADR 0058 |
| per-batch exchanges (nitrogen) | done in cheme, amounts ASSUMED | D-012, core ADR 0053 |
| LCI inventory | done, most backgrounds unmapped | D-012 |

## Open inputs
Kinetics and heat flow with gas dosing (calorimetry), the TD24 of the crude and the product;
the solubility of phosgene and HCl in the reaction mass at 50 kPa(a); the plant yield (D-008);
the product specification (assay, free phosgene, HCl, benzyl chloride, colour, stabiliser); the
reflux condenser and the phosgene recovery (D-007); the HCl recovery; the vent and relief
design against the gas release of a cooling failure (D-014: 18.6 times the vacuum pump's
capacity by the screening); the dosing interlock; the phosgene the vent carries off and a vent
condenser cold enough to return it (D-015); the vessel's metal (D-015); a TEA (`operation.batch: {recipe: true}`).
