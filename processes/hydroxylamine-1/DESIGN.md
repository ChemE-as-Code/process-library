# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Hydroxylamine as hydroxylammonium sulfate, issue ChemE-as-Code/process-library#182. Starting
point: library main `9f27e7a`, cheme-as-code 0.8.0 (pyDEXPI 2.1.0), thermo 0.6.1 / chemicals
1.5.2 in cheme's interpreter. Concept stage, written by an agent run on 2026-10-28; not reviewed.

## Source register

Every number taken from a source is recorded in our own words with its locator; no table, figure
or text is copied. Patents were read on Google Patents (full text, machine OCR of the US
documents); "read" means the cited section was read in this run.

| id | source | locator | read status | use |
|---|---|---|---|---|
| S1 | Krauss, Diekmann (BASF), US 3,110,563 (1963), process for high-percentage nitric oxide, https://patents.google.com/patent/US3110563A/en | Description, Examples a-c; Claims 1-6 | read (OCR garbles a few values, noted below) | burner feed NH3:O2:steam 14:18.6:67.4 by volume, NH3:O2 optimum 1:1.33-1.35, Pt/Rh with 3-10 % Rh, 750-1000 C (preferred 850-900 C); Example a: 98 % of the NH3 nitrogen as NO (82 %), HNO3 (15 %) and nitrite (1 %), rest N2/N2O; about 6 % HNO3 in the condensate when O2 is in excess (D-003, D-005) |
| S2 | Kretschmar, Leetsch (DOMO Caproleuna), EP 0 945 401 A2/B1 (1999/2002), hydroxylammonium sulfate with integrated NO generation, https://patents.google.com/patent/EP0945401A2/en | Example (reactors 2, 4, 11; condensers 5, 6; mixer 12) | read | NH3 burnt with O2 and steam, O2 8-10 % above stoichiometric; nitrous gas cooled to 260-280 C in the boiler; 90 % of the residual O2 hydrogenated on Ag-Mn; two-stage condensation with HNO3 in the condensates; condensate reused to make 19 % H2SO4 for the hydrogenation cascade; off-gas to combustion (D-003, D-005, D-009) |
| S3 | BASF, US 4,895,711 (1990), preparation of hydroxylammonium salts, https://patents.google.com/patent/US4895711A/en | Description (conditions); Example 1 and Table (Examples 1-4, comparative 1-6) | read | 4-6 N acid, not below 0.2 N; 30-80 C (35-60 preferred); atmospheric to 30 bar (1.5-20 preferred); H2:NO 1.5-6 (3.5-5 preferred); Pt 0.1-5 wt% on carbon/graphite, 20-100 g/l; Example 1: 40 C, 4.3 N H2SO4, 35 % NO / 65 % H2; selectivities NH2OH 85.6-87.6 %, NH3 10.4-12.5 %, N2O 1.9-2.2 % (Examples 1-3); space-time yield about 0.97 (unit not stated in the abstract we read, D-008) |
| S4 | Bender, Wilfinger, Schenkel (BASF), EP 1 343 719 (2003), continuous preparation of hydroxylammonium salts, https://patents.google.com/patent/EP1343719 | claims and description (German); no examples on the page | read (description) | 2-10 stages in series (4-8 preferred), each fed with NO/H2; off-gas collected, freed of by-products, topped up with NO and recycled; 40-60 C; H2:NO per stage 1.5-2.5, especially 2:1; pH 1.0-1.5 with sulfuric acid; N2O, N2 and ammonium salts as by-products, explosive mixtures at high N2O (D-007) |
| S5 | Fuchs, Neubauer, Ritz, Weiss (BASF), US 4,997,635 (1991), crystalline hydroxylammonium sulfate low in ammonium sulfate, https://patents.google.com/patent/US4997635A/en | Description (typical ranges) and Example (feed analysis) | read | hydrogenation solution: 254 g/kg hydroxylammonium sulfate, 18.6 g/kg ammonium sulfate, 13.0 g/kg free H2SO4 (typical 24-26 %, 1.5-2 %, 1.2-1.5 %) (D-004, D-007) |
| S6 | BASF, US 4,457,906 (1984), preparation of hydroxylammonium salts, https://patents.google.com/patent/US4457906A/en | Background, Examples 1-2 | read | N2O forms explosive mixtures with H2 and NO, especially under pressure; prior art dilutes with 10-80 vol% N2 (EP 0 008 479); 2-3 % N2O in the batch gas phase with foam suppression, about 30 % without (D-007, O-7) |
| S7 | IPCC (2006) Guidelines, Vol. 3 Ch. 3, https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/3_Volume3/V3_3_Ch3_Chemical_Industry.pdf | section 3.3, Table 3.3 (printed p. 3.23); section 3.5.2 and Table 3.5 (p. 3.36) | read (text extracted 2026-10-28) | N2O default for atmospheric-pressure ammonia oxidation 5 kg N2O/t HNO3 (+/-10 %); caprolactam default 9.0 kg N2O/t caprolactam (+/-40 %, based on high-pressure nitric acid plants); NH3 oxidation is the N2O source of all caprolactam routes (D-005, D-009) |
| S8 | Wagman et al. (1982) The NBS tables of chemical thermodynamic properties, J. Phys. Chem. Ref. Data 11, Suppl. 2 | NH3OH+(aq), NH4+(aq), H2O(l), NO(g), N2O(g) enthalpies of formation | **not re-read in this run** (the open TN 270-3 scan has no text layer); values used as known handbook values, open input O-4 | heats of reaction of the cascade (D-005) |
| S9 | thermo 0.6.1 / chemicals 1.5.2 (C. Bell, MIT licence) | `Hfgm`, ideal-gas heat capacities, vapour pressure and heat of vaporisation of water and ammonia | used through cheme's interpreter | gas-phase enthalpies, burner and boiler temperatures and duties (D-006) |
| S10 | library processes asu-1, ammonia-1, hydrogen-1, sulfuric-acid-1 (design bases) | asu-1 design basis: GOX >= 99.5 mol% O2; sulfuric-acid-1: 98.5 wt% product | read | boundary feed states (D-003) |
| L1 | Ritz, Fuchs, Perryman, Hydroxylamine, Ullmann's Encyclopedia, doi:10.1002/14356007.a13_527 | - | lead only, not read (licensed) | route family overview to audit later (O-1) |

## D-001 Route, product and boundary (2026-10-28)
Decision: catalytic hydrogenation of nitric oxide in dilute sulfuric acid over suspended platinum
on graphite (the BASF process family, S3-S5), product **hydroxylammonium sulfate solution, 25.4
wt% (NH3OH)2SO4 = 10.2 wt% NH2OH**, with 1.9 wt% ammonium sulfate and 1.3 wt% free acid as it
leaves the hydrogenation (S5). **NO is made inside the boundary** by burning ammonia with
oxygen and steam on Pt/Rh (S1, S2). Boundary feeds: liquid ammonia (ammonia-1), GOX (asu-1),
hydrogen (hydrogen-1 or chlor-alkali-1 by-product), sulfuric acid 98.5 wt% (sulfuric-acid-1),
demineralised water and LP steam; boundary products: the solution to storage, MP steam export,
the oxidiser flue gas.
Reason: the issue asks for this route. NO is not traded: it is toxic, oxidises in air and is made
where it is used, and both the BASF burner (S1) and the integrated DOMO process (S2) put the NO
generation, its condensate and the acid make-up into one water balance; a boundary feed "NO"
would hide the N2O source (S7) and the steam export. The solution is the form used directly for
cyclohexanone oximation (S4, S5 application notes); crystallising the salt (S5) or making the
free base are extra steps a consumer may not need.
Rejected: Raschig process (nitrite + SO2 + NH3, disulfonate hydrolysis; S7 section 3.5.2
describes it) for its ammonium sulfate load and SO2 step; nitrate hydrogenation in a phosphate
buffer (HPO) because its hydroxylamine stays in the oximation loop and is not a saleable product
(route knowledge, not sourced in this run, O-1); free-base hydroxylamine (50 wt%) as a further
downstream step outside this scope.
Assumptions: the selectivity and product analysis of the patents apply to a continuous plant;
NO generation at about atmospheric pressure.

## D-002 Capacity and operating time (2026-10-28)
Decision: 30 kt/a NH2OH contained (3750 kg/h), 8000 h/a; 36.7 t/h of solution.
Reason: no traceable published plant basis (issue: capacity missing). 30 kt/a is the
hydroxylamine of a ~100 kt/a caprolactam train at one NH2OH per caprolactam (0.29 t/t); a
normalisation for the inventory, not a market claim. ASSUMED.

## D-003 Feeds and their states (2026-10-28)
Decision: NH3 pressurised liquid at 298 K, 1200 kPa(a), vaporised in E-100 with LP steam; GOX
99.5 mol% O2 (rest Ar) at 300 kPa(a) (asu-1 spec, S10); H2 99.9 mol% treated as pure at >= 300
kPa(a); H2SO4 98.5 wt% (sulfuric-acid-1); dilution steam LP 500 kPa(a) saturated (direct use).
Reason: the library's upstream processes; states ASSUMED. The O2:NH3 and steam:NH3 ratios are
S1 Example a. The steam keeps the NH3/O2 mixture out of its flammable range (S1's purpose of the
dilution); the margin is not checked here (O-7).

## D-004 Components, product specification and product form (2026-10-28)
Decision: molecular salts HAS (NH3OH)2SO4 and AS (NH4)2SO4, H2SO4, HNO3 and water in the liquid;
no ions or HSO4-/SO4-- speciation. The product is set to the S5 analysis (25.4 / 1.86 / 1.30
wt%) by the acid feed (H2SO4 bound in both salts plus the free acid) and the demineralised
water. The condensate's HNO3 (0.26 wt% of the product) is carried into the product unchanged.
Reason: element balances need only the salts; speciation is not supported in core (core #364:
aqueous NaCl only, issue comment 27 Oct 2026). Whether nitrate is hydrogenated over Pt in the
cascade is not known to us; S2 hydrogenates its stronger condensate separately (reactor 11) and
feeds a weak one (<= 0.2 % HNO3) to the acid make-up. Carrying the nitrate through is the
conservative choice for the yield (O-6).
Rejected: a free-acid-only product spec (the patents give the full analysis).

## D-005 Reaction models and their evidence (2026-10-28)
Decision: conversion models (process/reactions.yaml), solved by cheme:
- Burner R-101: complete NH3 conversion; 98.0 % of the NH3 nitrogen to NO (S1 Example a: NO +
  HNO3 + nitrite; the oxidised share is treated as NO at the gauze), 1.4031 % to N2O, 0.5969 %
  to N2. The N2O share is the IPCC atmospheric-pressure default (S7 Table 3.3, 5 kg N2O/t HNO3)
  referred to the NH3 nitrogen: (5/44.013 x 2) kmol N per (1000/63.013) kmol HNO3, times the 0.98
  NOx yield. An inventory default, not a gauze measurement; the burner of S1 runs with O2 and
  steam, not air. Adiabatic outlet 1196 K from a 385 K feed (ideal gas, S9), inside S1's 750-1000
  C. Heat: -226.6 kJ/mol NH3 (S9).
- O2 removal R-102: H2 stoichiometric for all residual O2 is added and 90 % of the O2 is
  hydrogenated (S2 Example); adiabatic 543 -> 678 K.
- Condenser E-102: the remaining O2 oxidises NO and leaves as HNO3 in the condensate (S1 and S2
  report HNO3 in the condensate); complete (ASSUMED). 0.38 kmol/h HNO3, 0.62 wt% in 15.6 t/h.
- Cascade R-201 (D-007): three parallel reactions of the NO fed: 2 NO + 3 H2 + H2SO4 -> HAS;
  2 NO + 5 H2 + H2SO4 -> AS + 2 H2O; 2 NO + H2 -> N2O + H2O. Heats from S8 (NH3OH+(aq) -137.3,
  NH4+(aq) -132.51, H2O(l) -285.83, NO(g) 90.29, N2O(g) 82.05 kJ/mol): -227.6 kJ per mol NO to
  NH2OH, -508.6 to NH4+, -192.2 to N2O; acid speciation and heats of solution neglected.
- Thermal oxidiser X-301: H2 burnt completely; NO and N2O unchanged (D-009).
Reason: no kinetics are available (issue: no invented kinetics); the patents give yields and
selectivities at stated conditions, which a conversion model carries with its sources. cheme
maturity: model basis "specified conversion" (sourced for NH3_NO, O2_HYD; assumed for the rest).
Rejected: equilibrium models (the selectivities are kinetic and catalyst-controlled; NO
hydrogenation equilibrium lies entirely on the product side).

## D-006 Balance method and what core can and cannot check (2026-10-28)
Decision: an independent script, scripts/has_balance.py (run with `cheme run`), fixes the NH3
feed for the NH2OH target, the gas recycle, the purge, the separator outlets (V-101, V-201) and
all temperatures and duties, with ideal-gas enthalpies (S9) and the aqueous heats of D-005.
cheme calculates the five reactor outlets, the mixers, the splitter and the pass-through steps
(`cheme process propagate --fill`) and checks every block and step: mass, component and element
(extent) balances close (cheme process streams: NOX 19 803.8, HAS 37 025, OGT 5944.9 kg/h in =
out). The script's reactor outlets agree with cheme's extents (e.g. HAS_FORM 56.7665 kmol/h).
Energy closure is **not evaluable in core**: no property package covers NO, N2O, steam-rich
nitrous gas or the aqueous salt solution (`cheme process props --coverage`: every stream
refused; core #315 for gas mixtures, core #364 for electrolytes: aqueous NaCl only, weak
electrolytes and speciation not covered). The gated steps are exactly: (1) `cheme process
props --fill` enthalpies for the nitrous gas (NH3/O2/H2O/NO/N2O/N2/Ar) and (2) for the
H2SO4-(NH3OH)2SO4-(NH4)2SO4-water solution; until then the duties are the script's.
Note: cheme 0.8.0 `Heating` is not treated as a pass-through class by propagate; E-100 uses
`ExchangingThermalEnergy`.

## D-007 Hydrogenation cascade, recycle and purge (2026-10-28)
Decision: six stirred tanks in series (S4: 2-10, preferably 4-8; number ASSUMED) represented by
one reactor step R-201 at 313 K (S3, S4: 40-60 C) and 200 kPa(a) (S3: 1.5-20 bar preferred;
low end chosen because of the N2O/H2/NO explosion hazard, S6). Acid make-up about 20 wt%
H2SO4 (calculated: 20.2 %, against 19 % in S2 and 4.3 N in S3). H2:NO = 2.0 at the cascade
inlet (S4). **NO converted per pass 0.90 (ASSUMED)**; of the converted NO: NH2OH 89.83 %, NH3
8.17 %, N2O 2.0 %. The N2O share is S3 Examples 1-3 (1.9-2.2 %); the NH3:NH2OH ratio
(0.0910 mol/mol) is derived from the product analysis of S5 (18.6 g/kg AS, 254 g/kg HAS), so that
the calculated product matches it. S3's batch laboratory examples give 85.6-87.6 % NH2OH, so
the design is at the better end (O-2). The off-gas (stream S22: 73.9 mol% H2, 12.4 % NO, 6.5 % N2O, 2.7 % Ar, 1.2 % N2, 3.3 % H2O)
is collected in V-201;
**30 % purged (ASSUMED)**, 70 % recycled by K-201. Result: N2O 6.5 mol% and NO 12.4 mol% in
the loop gas, overall NO utilisation 96.8 %, fresh H2 444 kg/h plus 46 kg/h to R-102. Water in
the off-gas at activity 0.9 (ASSUMED).
Reason: S4 recycles the off-gas after removing by-products; we found no open source for how N2O
is removed, so a purge stands for it. Purge sensitivity (script argument): 10 % purge gives 16
mol% N2O in the loop gas and 98.9 % NO utilisation; 50 % gives 4.1 mol% and 94.7 %. 30 % keeps
N2O within a few times the 2-3 % of S6's foam-free batch gas phase while losing 3 % of the NO.
The explosion envelope of NO/H2/N2O is not known to us (O-7).
Rejected: N2 dilution (prior art cited by S6: makes the off-gas unusable, slows the reaction).

## D-008 Utilities, machines and duties (2026-10-28)
Decision: cooling water 25/35 C; LP steam 500 kPa(a) (burner dilution, direct; NH3 vaporiser,
indirect); MP steam 1500 kPa(a) raised in the waste-heat boiler (nitrous gas 1196 -> 543 K, S2's
260-280 C); electric drives. Duties (scripts/has_balance.py): E-100 744 kW (heat of
vaporisation of NH3 at 298 K); E-101 6992 kW to MP steam; E-102 14 000 kW to CW (678 -> 313 K,
condensing 15.6 t/h); E-201 1158 kW to CW (heat of dilution of 98.5 % acid to 20 %, about 74
kJ/mol H2SO4, ASSUMED handbook order, O-4); R-201 9184 kW to CW (reaction 8772 kW, gas sensible
81 kW, minus evaporation 98 kW, plus the agitator work); K-101 99 kW (115 -> 220 kPa(a),
isentropic efficiency 0.75); K-201 8 kW; P-201 4 kW; K-301 10 kW; R-201 agitators 234 kW
(2 kW/m3 ASSUMED x 117 m3 liquid from a space-time yield of 0.97 mol NH2OH/(l h), S3, unit
interpretation ASSUMED). Per kg NH2OH: electricity 0.095 kWh, LP steam 3.12 kg direct + 0.20
kWh heat, MP steam export 1.86 kWh, cooling water 6.49 kWh.
Reason: concept values for the inventory; the MP steam export roughly offsets the dilution
steam taken (heat integration, e.g. raising the dilution steam in E-101, is an option not taken
at this stage). Pumps other than P-201 and the product transfer are neglected.

## D-009 Off-gas treatment and emissions (2026-10-28)
Decision: the purge goes to a thermal oxidiser X-301 with air for a 1173 K flue gas; its H2
burns; **no NO or N2O destruction is credited** and no heat is recovered. Direct emissions per kg
NH2OH: N2O 25.9 g, NO 33.7 g (flue gas 5.94 t/h).
Reason: S2 sends its off-gas to a combustion unit without data; no open source for a destruction
efficiency was found, so the conservative choice is shown. Cross-check: at 0.29 t NH2OH per t
caprolactam the N2O is about 7.5 kg/t caprolactam against the IPCC default of 9.0 kg/t (+/-40 %,
S7 Table 3.5), i.e. inside its range. The NO emission is high and is the first abatement item
(O-8): an H2-rich purge invites a non-selective catalytic reduction (NO and N2O reduced by the
purge's own hydrogen), or a return of the purge to an absorption.

## D-010 Lists, materials and design conditions (2026-10-28)
Decision: equipment and line lists hold the PFD items (18 items, 22 lines); design pressure and
temperature = the highest operating value + 10 % (at least + 2 bar) and + 25 K; materials first
choices (stainless steel or lined steel for dilute sulfuric acid and hydroxylammonium salts,
304L for the dilute-HNO3 condensate, heat-resistant alloy at the gauze). Line sizes from
velocity. All ASSUMED; no datasheets at this stage.

## D-011 Preliminary gate-to-gate LCI (2026-10-28)
Decision: lca/lca.yaml, functional unit **1 kg NH2OH contained** in the 25.4 wt% solution
(kg_per_unit 9.78222 kg of solution; per kg of solution divide every amount by 9.78222, per kg
of (NH3OH)2SO4 multiply by 0.40247). Gate-to-gate, operation only, design case. Every
foreground exchange comes from the balanced flowsheet (stream ids in `source:`); the three
catalysts outside it are consumables with ASSUMED orders of magnitude: Pt/Rh gauze loss 0.5 g/t
NH3 (9.2 kg/a; the per-NH3 equivalent of nitric-acid-1's assumption), Pt loss 5 %/a of a 23 kg
inventory (1.2 kg/a), Ag-Mn O2-removal catalyst 800 kg/a (2.4 m3 at GHSV 10 000 1/h, 3-year
life) with its disposal to silver recovery. Catalyst preparation (graphite, chemicals) and gauze
fabrication/refining services are cut-off entries. Every background is **unmapped** (`missing:`
with the activity it should connect to); air, N2, O2, Ar and water vapour of the flue gas are
free; N2O, NO and H2 are elementary emissions to air. The MP steam export is a co-product with
shares 1/0 (all burdens to the product, no credit; same reasoning as nitric-acid-1 D-014);
substitution is given unmapped for comparison. lca/mappings.yaml only fixes the unit of the
indirect steam (steam-heat, kWh) and blocks automatic Atlas links for H2 and the dilution steam
until a supplier is chosen.
Result (cheme assess lca --inventory --write, --coverage --write), per kg NH2OH: NH3 0.612 kg,
GOX 1.538 kg, H2 0.131 kg, H2SO4 98.5 % 1.774 kg, demineralised water 2.700 kg, combustion air
1.494 kg, dilution steam 3.118 kg, LP steam heat 0.198 kWh, electricity 0.095 kWh, cooling
water 6.49 kWh, MP steam export 1.865 kWh, product solution 9.782 kg, flue gas 1.585 kg (N2O
0.0259, NO 0.0337, N2 1.132, O2 0.239, H2O 0.126, Ar 0.029 kg). Mass balance: 11.3675 kg in and
out (closed; the flowsheet gives 42 628.3 kg/h in, 42 628.2 out). The element balance is "not
assessable" in cheme only because the catalyst consumables carry no composition. 84.2 % of the
NH3 nitrogen ends as NH2OH. The coverage report classifies the result as a partial screening
carbon footprint with 13 gaps; its only characterised flow is the direct N2O (7.08 kg CO2-eq
per kg NH2OH with IPCC AR6 GWP100 273). **That number is the plant's direct N2O, not the
product's footprint** (NH3, H2, O2, acid, steam and power are all gaps). The generated
results.csv/results.md show it as a "total"; read it as the direct-emission line only.
Reason: the issue asks for a preliminary LCI with every background left open and a mass balance
check against the flowsheet. Per kg NH2OH is the comparable basis across salt and free-base
products.
Emission exclusions: equipment leaks (no P&ID yet), the acid make-up tank (no volatile source),
thermal NOx of the oxidiser flame (small against the NO passed through).

## Missing registry entries (for the consolidated library PR)
chemicals/chemicals.yaml has no entry for: hydroxylammonium sulfate (main product, CAS
10039-54-0; or hydroxylamine with a `hydroxylammonium-sulfate-solution` grade), ammonia (CAS
7664-41-7), sulfuric acid (7664-93-9), nitrous oxide (10024-97-2), nitric oxide (10102-43-9),
ammonium sulfate (7783-20-2), platinum/rhodium (catalyst metals). lci/mappings.yaml would need
technosphere entries for the Pt catalyst loss, the Ag-Mn catalyst and its silver recovery, and
an elementary-flow identity for NO (the packaged crosswalk has none).

## Open inputs
- O-1: audit the route families and the BASF process description in Ullmann (L1) with exact
  locators; confirm or replace S1-S5 values with plant data.
- O-2: continuous-plant selectivity and per-pass conversion of the cascade (here 89.8 % NH2OH,
  0.90 per pass ASSUMED), with catalyst age and regeneration (S3 Example 4).
- O-3: Pt/graphite catalyst make-up and Pt loss per t NH2OH; Pt/Rh gauze loss and campaign
  (used in the LCI as ASSUMED orders of magnitude, D-011).
- O-4: verify the NBS aqueous enthalpies of formation (S8) and the heat of dilution of H2SO4 with
  exact locators.
- O-5: burner pressure, gauze loading and temperature control; NO selectivity with O2/steam
  (98 %) at the chosen pressure.
- O-6: fate of the condensate nitrate in the cascade (hydrogenated or carried to the product).
- O-7: flammability and explosion limits: NH3/O2/steam burner feed; NO/H2/N2O cascade gas and
  off-gas; the purge rate that keeps the loop gas outside them.
- O-8: NOx and N2O abatement of the purge (NSCR with the purge hydrogen, or other) and the permit
  limits of the site.
- O-9: product specification of the oximation consumer (free acid, ammonium sulfate, nitrate,
  Pt fines).
