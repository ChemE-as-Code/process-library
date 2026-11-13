# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Thionyl chloride from sulfur, chlorine and sulfur dioxide, issue
ChemE-as-Code/process-library#138. Concept stage: design basis, balanced BFD/PFD and a
preliminary gate-to-gate LCI. Out of scope here: P&IDs, layout, HAZOP, TEA, datasheets.

Starting point (2026-10-28): library `main` at cc5624f, cheme-as-code 0.8.0 (pyDEXPI 2.1.0),
`thermo` package as shipped with cheme. DWSIM was not used (D-006).

## Source register

Facts are restated in our own words; nothing is copied. "Read" means the passage named was read
in this session (Google Patents machine text; no paragraph numbers, so the locator is the part
of the document).

| id | source | locator | access / terms | used for |
|---|---|---|---|---|
| SRC-1 | US2431823A, A. Pechukas (Pittsburgh Plate Glass), 1947: Manufacturing thionyl chloride, https://patents.google.com/patent/US2431823 | description: a sulfur chloride (S2Cl2 or SCl2) with SO2 and Cl2 over activated carbon; appreciable conversion from about 150 C, preferred 175-225 C, about 200 C best, poorer yields above 225 C, effluent should leave at or below about 200 C; below about 100 C SO2 + Cl2 give SO2Cl2; preferred feed excess about 100 % SO2 and 0-10 % Cl2 over stoichiometric, a chlorine deficiency undesirable; preheater about 125 C in an example; off-gas SO2/Cl2 recycled; still bottoms (S2Cl2 with sulfur) chlorinated and recycled; one pass gives a crude above 50 % SOCl2, the rest roughly equal parts SCl2 and S2Cl2; final treatment with sulfur and an iron catalyst to above 99 % SOCl2 | read (OCR text partly garbled; the example numbers are uncertain and not used); patent, facts only | D-001, D-004, D-005, D-008 |
| SRC-2 | DE2430631A1, Bayer AG, 1976: purifying crude gaseous thionyl chloride by contact with molten sulfur or polysulfur chlorides, https://patents.google.com/patent/DE2430631A1/en | abstract and description: gas-phase reaction of sulfur chlorides with SO2 and Cl2 at 160-240 C over activated carbon without pressure; conversion 50-80 % per pass because of the equilibrium; crude gas holds 20-50 wt% SCl2, S2Cl2, SO2, Cl2; examples 1A/2: reactor conversion 70-75 %; example 1A crude about 75 % SOCl2 by mass with SCl2, Cl2 and SO2 of similar molar amounts and little S2Cl2; iron (FeS) added to the sulfur melt; crude vapour through molten sulfur at 138-160 C turns SCl2 into S2Cl2; S2Cl2 and SO2 recycled, overall yield on SO2 practically 100 %; product up to about 1 % SCl2 | read; patent, facts only | D-005, D-007, D-008, reactions.yaml |
| SRC-3 | US4759826A, Occidental Chemical, 1988: Process for purifying thionyl chloride, https://patents.google.com/patent/US4759826 | description and examples: crude from S2Cl2, SO2 and Cl2 over activated carbon holds about 70-85 % SOCl2 (example crude: about 80 % SOCl2, 12 % SCl2, 7 % S2Cl2, below 1 % SO2Cl2 and SO2; other examples about 72-74 % SOCl2 and 25-27 % SCl2); SCl2 and SO2Cl2 hard to separate from SOCl2 by distillation; double distillation with sulfur in the reboiler (reboiler about 78-130 C) shifts SCl2 to S2Cl2 that stays in the bottoms; a carbon bed in the vapour lowers SO2Cl2; finished products 99.4-99.8 % SOCl2, typically about 0.05 % SO2Cl2, 0.1 % SCl2, 0.2 % SO2 | read; patent, facts only | D-002 (product spec range), D-008 |
| SRC-4 | EP0042530B1 (1981): Verfahren zur Reinigung von Thionylchlorid, https://patents.google.com/patent/EP0042530B1/de | description: sulfur (with AlCl3) added before or during distillation, 1-15 wt%, preferably 2.5-7 wt%, of the thionyl chloride | read through the search summary only (abstract level) | D-008 (sulfur dose cross-check) |
| SRC-5 | US4337235A and US4388290A (Hooker / Occidental): purification of thionyl chloride with sulfur and AlCl3; US4388290 also returns uncondensed SO2 and Cl2 to the feed | abstracts | abstract level only | D-007 (recycle of the uncondensed gas), D-008 (alternatives) |
| SRC-6 | Lauss, H.-D.; Steffens, W.: Sulfur Halides. *Ullmann's Encyclopedia of Industrial Chemistry*, doi:10.1002/14356007.a25_623 | - | not read (licensed); named by the issue | route reference lead only |
| SRC-7 | chemicals 1.5.2 and thermo 0.6.1 packages of core's environment (open-source, MIT; the versions core pins), through `cheme chemistry thermo` and `thermo.Chemical` in scripts/balance.py: gas formation enthalpies and standard entropies from chemicals' packaged CRC Handbook table `heat_capacity.CRC_standard_data` (SOCl2 and SO2, and the entropies of Cl2, O2 and water; from the CRC Handbook of Chemistry and Physics, 2014 edition as chemicals cites it; a licensed book, not read here), its NIST WebBook data (`WEBBOOK`: SCl2, S2Cl2) and its Active Thermochemical Tables 1.112 data (`ATCT_G`: Cl2, O2, water); ideal-gas cp from chemicals' `heat_capacity.Cp_data_Poling` polynomials (Poling, Prausnitz and O'Connell, The Properties of Gases and Liquids, 5th ed.; a licensed book, not read here: SO2, Cl2, O2, water) or fitted to thermo's TRCIG and JANAF correlations (SOCl2, SCl2, S2Cl2); the normal boiling points of SOCl2, SCl2 and S2Cl2 from chemicals' packaged CRC inorganic table (`miscdata.CRC_inorganic_data`); critical constants by the methods printed per component in process/materials.yaml (YAWS: Yaws, Thermophysical Properties of Chemicals and Hydrocarbons, 2nd ed. (2014) as chemicals cites it; a licensed book, not read here); thermo's default vapour pressures: NIST WebBook Antoine constants (ANTOINE_WEBBOOK: SOCl2, S2Cl2), Antoine constants from Landolt-Börnstein (LANDOLT: SCl2; K. R. Hall, ed., Springer 1999; a licensed work, not read here), fits to CoolProp's reference equations of state (HEOS_FIT: SO2, Cl2) and IAPWS-95 (water); heats of vaporization from the Morgan-Kobayashi corresponding-states estimate (MORGAN_KOBAYASHI: SOCl2, SCl2, S2Cl2) and HEOS_FIT (SO2, Cl2, water) | printed per component in process/materials.yaml; called in scripts/balance.py | open-source packages queried; single values, facts only; not open data (library ADR 0037) | ideal-gas data, Raoult flash, latent heats |
| SRC-8 | NIST Chemistry WebBook, condensed-phase data of sulfur (rhombic -> monoclinic transition about 368 K, 0.40 kJ/mol; fusion about 388 K, 1.72 kJ/mol; Cp solid about 23 J/(mol K), liquid about 31 J/(mol K)) | rounded values, approximate | open | liquid sulfur enthalpy in scripts/balance.py (D-006) |
| SRC-9 | processes/chlor-alkali-1 (this library) | its chlorine product (400 kPa(a), 313 K) and 50 wt% caustic | library, internal | chlorine and caustic feed links (D-003, D-009) |

The issue's handoff asked not to search for published "answers"; no benchmark plant figures were
looked for or used. The capacity is an assumption, not a published plant.

## D-001 Route and boundary (2026-10-28)
Decision: Continuous gas-phase synthesis SCl2 + SO2 + Cl2 -> 2 SOCl2 over activated carbon
(SRC-1, SRC-2, SRC-3), with the sulfur chlorides made inside the boundary from molten sulfur and
chlorine (2 S + Cl2 -> S2Cl2, S2Cl2 + Cl2 -> 2 SCl2). Overall: S + SO2 + 2 Cl2 -> 2 SOCl2.
The crude is condensed and degassed, the SO2/Cl2 gas recycled, and the crude distilled with
sulfur; the S2Cl2-rich still bottoms return to the chlorination (SRC-1, SRC-2). A caustic
scrubber takes the small purge. Boundary feeds: molten sulfur, chlorine, liquid SO2, caustic
soda 50 wt%, process water, LP steam, electricity; returns: cooling water, brine; outputs:
thionyl chloride, spent liquor, scrubbed vent.
Reason: the case brief prescribes this route; all sources read describe it as the industrial
one. Making the sulfur chlorides in the boundary is necessary anyway because the purification
returns S2Cl2 that must be rechlorinated (SRC-1, SRC-2); buying SCl2 would still need that
loop, and SCl2 is unstable in storage (it disproportionates to S2Cl2 and Cl2).
Rejected: SO3 + SCl2 (gives SO2 as by-product, needs oleum; not prescribed); PCl5 or COCl2 with
SO2 (laboratory routes, POCl3 or CO2 by-products). SO2 made in the boundary by burning sulfur
with oxygen: possible integration, but it adds an O2 supply and an SO2 absorption/liquefaction
step without changing the chemistry; left as an option.
Links to other library processes: chlorine and caustic soda from chlor-alkali-1. No library
process makes elemental sulfur (a Claus unit would) or pure liquid SO2 (sulfuric-acid-1 has
only dilute burner gas). LP steam, cooling water, brine and wastewater treatment could later
connect to utility-steam-ng-boiler, utility-cooling-tower, utility-chiller and utility-wwtp.

## D-002 Capacity, product and operating hours (2026-10-28)
Decision: 3750 kg/h thionyl chloride, 30 kt/a at 8000 h/a, ASSUMED. Product 99.7 wt% SOCl2,
0.1 wt% SCl2, 0.2 wt% S2Cl2 (ASSUMED, within the finished products of SRC-3); SO2Cl2, dissolved
SO2 and colour are not modelled.
Reason: no traceable published plant basis is used (issue note); the LCI is per kg and does not
depend on scale. Technical grade is the bulk use (chlorinating agent for acid chlorides,
pharmaceuticals, agrochemicals, battery electrolyte).

## D-003 Feed specifications (2026-10-28)
Decision: molten sulfur 100 % S at 413 K, 400 kPa(a) (bright sulfur; ash, carbon, H2S and
water neglected, open input). Chlorine gas 99.9 mol% Cl2, 0.1 mol% O2, 313 K, 400 kPa(a), i.e.
chlor-alkali-1's chlorine after drying, liquefaction and re-evaporation (ASSUMED). Liquid SO2
100 % at 298 K, 500 kPa(a) (ASSUMED).
Reason: water must stay out (hydrolysis of SOCl2 and the sulfur chlorides to HCl, SO2 and
sulfur). The O2 of the chlorine is inert here but accumulates in the gas loop; it sets the purge
(D-007). Cell-room chlorine with about 2 mol% O2 would need a purge about 20 times larger.

## D-004 Sulfur chlorination (2026-10-28)
Decision: R-101: the fresh sulfur (49 % of the sulfur feed) and the sulfur dissolved in the still
bottoms are chlorinated completely to S2Cl2 with stoichiometric chlorine at 343 K, 200 kPa(a),
in a pool of sulfur chlorides (molten sulfur dissolves in S2Cl2). R-102: 90 % of the S2Cl2
chlorinated on to SCl2 at 313 K with stoichiometric chlorine (ASSUMED; no sourced liquid-phase
equilibrium; SRC-1 notes that S, Cl2 and both chlorides coexist in equilibrium). Both cooled by
cooling water. The SOCl2 of the bottoms passes through inert. The iron catalyst of SRC-2 and
dissolved free chlorine are not modelled.
Reason: two steps because a conversion reactor converts the inlet flows only (the SCl2 step
works on the S2Cl2 that R-101 makes); also the usual practice of a sulfur chlorinator followed
by a chlorine-rich stage. The reactor inlet gets the remaining S2Cl2 (4.8 mol% of the liquor),
which R-201 chlorinates (D-005).
Simplification (review R-05): the O2 of the chlorine is carried dissolved in the chlorinator
liquors S10 and S11 (0.03-0.06 mol%), although D-006/D-007 treat O2 as insoluble elsewhere.
Real liquid-phase chlorinators vent inerts and unreacted Cl2; the overall balance does not
change, since the O2 reaches the same purge either way. When the P&IDs are drawn, R-101 and
R-102 get an off-gas vent to the K-201 suction or to T-401.

## D-005 Reactor R-201 (2026-10-28)
Decision: multitubular reactor with activated carbon in the tubes and a tempered-water shell
circuit rejecting to cooling water; inlet 398 K (preheated, as SRC-1's example), outlet 473 K
(SRC-1: effluent at or below about 200 C; SRC-2: 160-240 C), 170 -> 140 kPa(a) (near
atmospheric, SRC-2). Feed: SO2 2.0 x and Cl2 1.05 x the stoichiometric need of the sulfur
chlorides at the inlet (SRC-1 preferences), counting the recycle gas. Conversion model: 95 % of
the inlet S2Cl2 to SCl2 (ASSUMED) and 75 % of the inlet SCl2 to SOCl2 (SRC-2: 70-75 % in the
examples, 50-80 % stated). Heat of reaction -110.6 kJ/mol (ideal gas, materials.yaml).
The 75 % applies to the SCl2 entering R-201 only (cheme's conversion-reactor rule); the SCl2
formed in the bed from S2Cl2 passes unconverted, so the effective per-pass conversion of all
SCl2 is 67.9 % (15.72 kmol/h converted of 20.96 entering plus 2.20 formed; review R-03), still
inside SRC-2's 50-80 %.
Reason: the per-pass conversion is the only sourced performance figure; no kinetics are
published in the open sources read, and none are invented. Steam raising from the reactor heat
(473 K allows LP steam) is an open heat-integration option, not taken in the base case.
Evidence note: `cheme process reactors` gives ln K = 12.2 at 473 K for SCl2 + SO2 + Cl2 <=>
2 SOCl2 on ideal-gas data and ln(Q/K) = -8.6 at the outlet, i.e. the ideal-gas equilibrium
would allow almost complete conversion. SRC-2 attributes the 50-80 % to the equilibrium; the
discrepancy is not resolved (possible causes: the SOCl2 decomposition and sulfur chloride
equilibria at the catalyst, non-ideal data for SCl2, kinetic limitation at short contact
times). The model therefore carries the patent conversion as a given empirical value, labelled
so; it predicts nothing. SO2Cl2 formation is excluded above 448 K (SRC-1: forms below about
100 C) and SOCl2 dissociation at 473 K is neglected.

## D-006 Balance method and property gate (2026-10-28)
Decision: every stream value and duty comes from scripts/balance.py (run: `cheme run
scripts/balance.py`): ideal gas with the materials.yaml data; liquids as ideal gas minus the
`thermo` heat of vaporization; Raoult flash with `thermo` vapour pressures, O2 insoluble;
liquid sulfur from approximate condensed-phase data (SRC-8); conversion reactors as in cheme;
both recycle loops (sulfur chlorides through T-301/R-101, gas through K-201) closed by
successive substitution (853 iterations, residual below 1e-9 kmol/h). The values enter
flowsheet.yaml as `assumed` with this source.
Reason: no property package of core is qualified for SOCl2, SCl2, S2Cl2 or the caustic liquor
(`cheme process props --coverage`: only the air package is benchmarked; core issues on
property/phase and reaction-energy qualification and on electrolytes, not resolvable from this
session's GitHub access). DWSIM's database coverage of SCl2 and S2Cl2 was not established, so
`cheme process simulate` was not attempted.
Checks: cheme closes mass, component and element balances on every block and step (tolerance
1 kg/h + 0.5 %), `cheme process propagate --check` agrees, and `cheme process reactors`
reproduces the R-201 duty from ideal-gas data (-386.56 kW, the script -386.56 kW). The R-102
duty in core (-61.9 kW) is on an ideal-gas basis; the script's -127.3 kW includes the latent
heats of the liquid phase. The energy balance of the condensers, degasser, column and scrubber
is not evaluable in core (gated: qualified VLE and liquid enthalpies for the sulfur chlorides;
electrolyte liquor).

## D-007 Condensation, degassing, gas recycle and purge (2026-10-28)
Decision: E-204 cools the reactor gas to 308 K on cooling water, E-205 to 263 K on brine
(253 K supply); V-201 at 130 kPa(a). T-201 strips SO2 and Cl2 from the crude completely
(ASSUMED sharp split), with a brine overhead condenser at 263 K whose vapour carries the heavies
at their Raoult partial pressures; the bottoms leave at the Raoult bubble point of the
lights-free crude at the column pressure (350.1 K at 125 kPa(a), computed by the script);
reboiler duty = heating of the crude to that temperature plus 1.5 x the latent heat of the
stripped lights (ASSUMED). Revised 2026-10-28 after review R-01: the first balance took 345 K,
below the crude bubble point at 125 kPa(a) (about 100 kPa at 345 K), so by Raoult some SO2/Cl2
would have stayed in S22 and reached the T-301 distillate, which has no lights outlet. At the
bubble point the sharp split is consistent with the Raoult basis of D-006 (the lights' partial
pressure in the bottoms vapour tends to zero only with stripping stages; the stage count is not
designed, see Open inputs). Q9 rises from 464.85 to 471.01 kW and the warmer T-301 feed lowers
Q13 from 684.47 to 678.05 kW; the LP steam total is unchanged to 0.02 % (0.422 kWh/kg). The separator and degasser gases are joined,
1 % is purged (ASSUMED, giving 7.2 mol% O2 in the loop) and the rest is recompressed by K-201
(125 -> 180 kPa(a), isentropic 0.70, motor 0.95) to the reactor feed (SRC-1, SRC-5: off-gas
recycled).
Reason: the recycle keeps the SO2 excess of D-005 affordable (2.77 t/h recycle gas against
1.03 t/h fresh SO2). The purge is the only exit for the O2 of the chlorine; 1 % loses 1.9 % of
the SO2 and 0.5 % of the chlorine. Alternatives: absorbing SO2/Cl2 from the purge in cold crude
(less loss), or SRC-1's cold-carbon conversion of the off-gas to SO2Cl2; left for optimisation.

## D-008 Purification with sulfur (2026-10-28)
Decision: the degassed crude (84 wt% SOCl2, 16 wt% SCl2, consistent with SRC-3's crude range)
gets molten sulfur at 1.10 x the SCl2 to be converted (258 kg/h = 6.5 wt% of the SOCl2;
SRC-4: 1-15 %, preferably 2.5-7 %) and is distilled at atmospheric pressure in T-301 with the
sulfur reaction in the reboiler (SRC-3, SRC-2): SCl2 + S -> S2Cl2 converts 99.5 % of the SCl2
so that the distillate meets D-002. Bottoms keep 20 wt% SOCl2 (ASSUMED, bottoms bubble point
about 386 K at 101 kPa by Raoult), reflux ratio 2 (ASSUMED, no column design); the bottoms
(72 mol% S2Cl2, 7 mol% dissolved sulfur, 21 mol% SOCl2) return to R-101.
Reason: SCl2 boils below SOCl2 (333 vs 349 K) and cannot be distilled off cleanly (SRC-3);
converting it to S2Cl2 (410 K) moves it to the bottoms, and the bottoms close the sulfur loop.
The two-stage distillation and carbon bed of SRC-3 against SO2Cl2 are not modelled (SO2Cl2 is
not in the component set; D-005).

## D-009 Purge gas scrubber (2026-10-28)
Decision: T-401 absorbs 99.9 % of the SO2, Cl2, SOCl2 and sulfur chlorides of the purge in
circulating 10 wt% NaOH (50 wt% caustic from chlor-alkali-1 diluted with process water), NaOH
1.2 x the consumption (ASSUMED). Chemistry: SO2 to sulfite; Cl2 reduced by the sulfite to
sulfate and chloride (the sulfite is in excess, so no hypochlorite remains); SOCl2 to sulfite
and chloride; the sulfur chlorides written to thiosulfate, chloride and sulfur (simplified). The
vent (95 mol% O2, water-saturated at 303 K) goes to atmosphere. The scrubber heat is not
evaluated (aqueous electrolyte, no package).
Reason: a caustic scrubber is the usual end-of-pipe device for acid chloride and SO2 vents; the
same unit would take the storage and relief vents (D-011). 99.9 % is an assumed design value,
not a guaranteed emission level; no BREF value was read for this plant type (open).

## D-010 Utilities, pressures and pumps (2026-10-28)
Decision: LP steam 500 kPa(a) (425 K) for the vaporisers, preheater and reboilers; cooling
water 298/308 K; brine 253/258 K from a refrigeration unit outside the boundary; pumps from
V dp / (0.6 x 0.95) with assumed pressure rises (300-400 kPa) and densities; the scrubber
circulation 5 m3/h. Pressure profile as in the stream table (ASSUMED). No fuel.
Reason: concept-stage allowances; the duties dominate the utility inventory, the pump power is
small (2.5 kW of 17.7 kW electric).
No heat integration in the base case, so the utilities per kg in D-012 are at the upper end.
Open heat-integration items (review R-06), none evaluated: (1) a feed/bottoms interchanger at
T-201 (the crude is chilled to 263 K on brine and reheated to 350 K by steam, Q9 471 kW);
(2) the SO2 vaporiser E-202 on cooling water or recovered heat instead of 425 K LP steam
(104 kW at 298 -> 313 K); (3) the R-201 heat at 473 K (387 kW, now to cooling water) raising LP
steam. A heat-integrated LCI scenario follows once a pinch study is done.

## D-011 Safety notes for the next stage (2026-10-28)
Not designed here (no HAZOP in scope): SOCl2 and the sulfur chlorides react violently with water
(HCl, SO2); chlorine and SO2 are toxic gases. Dry equipment and inert blanketing, containment of
the chlorination and reaction train, storage vents and relief to T-401, materials (dry
chlorine/chloride service; nickel alloys or glass-lined equipment where moist) are open items
for basic engineering.

## D-012 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml lists every foreground exchange of the design case per kg of product
(stream S31): raw materials (sulfur, chlorine, SO2, caustic, process water), utilities (LP steam,
electricity, cooling water, brine), the spent liquor as a waste to treatment, and the scrubbed
vent with its components as emissions to air (non-urban high stack ASSUMED). Every background
is left unmapped (`missing:` with the activity it should connect to): a gap, never zero, and no
values from licensed databases. Boundary key cradle-to-gate so that the feeds stay gaps (as
phosgene-1). The activated carbon make-up and the iron catalyst are recorded as cut-off flows
with unknown amounts; fugitive, storage and start-up emissions as exclusions.
Results (cheme assess lca --inventory --write, --coverage): per kg SOCl2: sulfur 0.1357 kg,
chlorine 0.5980 kg, SO2 0.2738 kg, caustic 50 wt% 0.0211 kg, process water 0.0844 kg; LP steam
0.422 kWh (1.52 MJ), electricity 0.0047 kWh, cooling water 0.501 kWh, brine 0.119 kWh; spent
liquor 0.1127 kg; vent 0.28 g (O2 0.27 g, SO2 5.3 mg, Cl2 1.7 mg, SOCl2 0.23 mg). Mass balance
closed (inputs 1.11300 kg, outputs 1.11300 kg; coverage: mass, element and carbon-origin
closed). Yields: 98.1 % on SO2, 99.0 % on sulfur atoms; stoichiometric minimum per kg pure SOCl2
is 0.1348 kg S, 0.2692 kg SO2, 0.5960 kg Cl2. Classification: no impact result (15 gaps).

## D-013 Missing shared-registry entries (for the consolidated shared-files PR)
Not edited here (outside the folder): chemicals/chemicals.yaml has no `thionyl-chloride`
(product), `sulfur`, `sulfur-dioxide` (liquid grade), `chlorine`, `sodium-hydroxide` (50 wt%
grade), and no brine-refrigeration utility at 253 K (only `chilled-water`); lci/mappings.yaml
has no technosphere entries for these and no biosphere identity for Cl2, SOCl2, SCl2 or S2Cl2 to
air (the cheme crosswalk lacks them too; SO2 has a biosphere3 id without an EF 3.1 UUID).
process.yaml lists only the registered flows under `chemistry` until then.

## Method and dependency table

| step | status | basis |
|---|---|---|
| mass, component, element balances | done in cheme | cheme validate / process streams / propagate --check |
| reactor R-201 conversion and duty | done (conversion model, sourced per-pass conversion); duty reproduced by core | D-005, `cheme process reactors` |
| equilibrium model of R-201 | not used: ideal-gas K contradicts the patent's equilibrium claim | D-005 |
| VLE of condensers, degasser, column | script (Raoult, `thermo` Psat), not qualified | D-006; gated on core property qualification (issue 315) |
| liquid-phase energy balances (R-101, R-102, T-201, T-301) | script only | D-006; gated as above |
| scrubber liquor | molecular pseudo-components, no energy | D-009; gated on electrolyte support (issue 364) |
| LCI inventory | done, backgrounds unmapped | D-012 |

## Open inputs
Capacity and site; feed impurities (sulfur ash/carbon/H2S, water in Cl2 and SO2); R-102
equilibrium; kinetics or a bed sizing basis for R-201 and the carbon life; product SO2Cl2 and
colour specification; column design (stages, reflux) on a qualified VLE; emission limits for the
vent (BREF); scrubber design and its heat; heat integration (D-010: T-201 feed/bottoms
interchange, SO2 vaporiser off steam, reactor heat to LP steam); T-201 stripping stages; full
text of SRC-4 and SRC-5 before any value rests on them alone.
