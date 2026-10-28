# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/balance.py`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#130.

Run record of this stage (2026-10-28): library branch `case/hydrogen-bromide-1` from `cc5624f`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core#364 (electrolytes)
could not be opened from this run (`gh`: not resolvable), so its state is taken from the
installed cheme: `cheme process methods` lists ENRTL-PR and PITZER-RKS as unsupported and the
electrolyte route as NaCl-H2O only, so **HBr-water is not supported** by any phase, property or
simulation route of this cheme; `cheme process props --coverage` finds no package for HBr, Br2
or water either. Both gates are recorded in section 6.

## 1. Route and boundary memo

- **Route** (issue #130 case notes): bromine vapour burnt in hydrogen, H2 + Br2 -> 2 HBr, the
  residual bromine finished over a catalyst, the HBr gas cooled and absorbed in water to
  48 wt-% hydrobromic acid. Two open patents describe the industrial burner: US 3 988 427 A
  (Ethyl Corp., flame reactor) and US 6 036 936 A (Elf Atochem, burner with graphite cooling
  and an optional activated-charcoal finishing stage). Older practice passes the mixture over
  platinum or asbestos at 200-400 degC (SRC-3). Rejected routes: HBr as a by-product of
  organic brominations (it belongs to the process that makes it; the issue asks for the
  intentional synthesis), and bromide salts with sulfuric or phosphoric acid, or bromine with
  sulfur dioxide/phosphorus and water (SRC-4: historical and laboratory routes; they carry
  sulfate or phosphate by-products).
- **Product form** (issue: anhydrous gas vs aqueous acid): aqueous hydrobromic acid 48 wt-%,
  the case notes' product (D-002). Anhydrous HBr would be the gas S6 itself before absorption
  (dried, compressed), not designed here.
- **Boundary of this case: saleable acid** (D-001). From liquid bromine and hydrogen gas at the
  fence, demineralised water, LP steam, electricity and cooling water to 48 wt-% acid at
  300 kPa(a) to storage and the scrubber vent. Inside: bromine vaporiser (E-101), burner with
  water-cooled chamber and hydrogen let-down (R-101), activated-carbon finishing bed (R-102),
  graphite gas cooler (E-102), falling-film absorber (C-201), tail gas scrubber (C-202),
  product pump (P-201). Outside: bromine and hydrogen production, bromine storage and its
  transfer pump, acid storage and loading, the emergency (caustic) absorption system, steam
  and cooling water generation, demineralised water production.
- **What crosses the boundary**: BR2, H2, DMW (raw materials), LPS and POWER (utilities in),
  HBRACID (product), VENT (emission), CW (utility out). One product: no allocation.
- **Normalisation**: per kg of HBr (100 %) contained in the acid; the acid stream is 2.083 kg
  per kg HBr.
- **Link to other library processes**: H2 is hydrogen-1's product S17 with its state (99.9
  mol-% H2, 0.1 mol-% N2, 2850 kPa(a), 313 K); this unit uses 13.3 of its 9 110 kg/h (0.15 %).
  Bromine is the product of the planned library process bromine-1, which does not exist yet;
  its state here is ASSUMED. Neither is integrated: the producers stay separate processes and
  this case consumes (issue: link rather than integrate).

## 2. Source register

Read status: "read" = the cited locator was read in the full text page by this run (through a
fetch tool that summarises the page); "metadata" = only the identity was checked. Facts are in
our own words; nothing copied.

| id | source | locator | status | terms | used for |
|---|---|---|---|---|---|
| SRC-1 | US 6 036 936 A (Elf Atochem, 1996 priority), https://patents.google.com/patent/US6036936 | Summary (H2/Br2 > 1 and < 1.4 mol/mol; heat released 12.3 kcal/mol HBr; adiabatic flame above 1600 degC; pressures: reaction at least 1, preferably 1.8-10 bar(a); cooling to 40-125 degC, preferably about 60 degC); Description, FIG. 3 variant (jacketed active-charcoal finishing stage entered at 150-200 degC); claims 6, 14, 18-19; Example (bromine fed at 3 bar(a), 95 degC with < 0.01 % water and < 0.05 % Cl2; 400 kg/h HBr with < 50 mg Br2 per kg HBr; product at 1.8 bar(a), 40 degC; chamber cooled with water at 28 degC); materials (impregnated graphite blocks in a steel jacket, silica/quartz/nickel burner tube) | read (Google Patents text) | patent text: facts only | D-004, D-005, D-007, burner and cooler materials |
| SRC-2 | US 3 988 427 A (Ethyl Corp.), https://patents.google.com/patent/US3988427 | Example (bromine conversion 99.96-99.99 mol-%, average about 99.97, at about 2.6 mol-% H2 excess; stable from 15 to about 120 % of design; flame about 2500 degF, product leaving at about 580 degF); Description (burner coil with cooling water or Dowtherm in operation; bromine vapour preheated to about 150 degF) | read (Google Patents text) | patent text: facts only | D-005 burner conversion, turndown |
| SRC-3 | Wikipedia, "Hydrogen bromide", https://en.wikipedia.org/wiki/Hydrogen_bromide | section Industrial preparation (H2 + Br2 at 200-400 degC, platinum or asbestos catalyst); infobox (bp -66.8 degC, dHf -36.13 to -36.45 kJ/mol) | read | CC BY-SA: facts only | route, normal boiling point, cross-check of dHr |
| SRC-4 | Wikipedia, "Hydrobromic acid", https://en.wikipedia.org/wiki/Hydrobromic_acid | lead (azeotrope 47.6 wt-% at 124.3 degC); infobox (48 % acid 1.49 g/cm3); sections Synthesis, Uses | read | CC BY-SA: facts only | D-002 product grade, D-011 density |
| SRC-5 | ATcT / CRC / Poling 5th ed. via `cheme chemistry thermo` (`chemicals` package); `thermo` for the Br2 saturation temperature | printed records in process/materials.yaml; Tsat(Br2, 300 kPa) = 368.7 K | read (tool output) | data facts | ideal-gas data, heat of reaction, reactor duties, D-007 |
| SRC-6 | Parker, V. B. (1965) Thermal Properties of Aqueous Uni-Univalent Electrolytes, NSRDS-NBS 2, as tabulated by Purdue Science Express "Enthalpy of Solution Reference" | HBr(g) to infinite dilution -85.14 kJ/mol at 25 degC | value from a search summary; PDF not opened | US government data | bound for D-009 |
| SRC-7 | Ullmann's Encyclopedia, "Bromine Compounds", doi:10.1002/14356007.a04_405, and "Bromine", doi:10.1002/14356007.a04_391.pub2 | none | metadata (issue #130 leads) | licensed | route identity only; no number taken |
| SRC-8 | hydrogen-1 (this library), process/flowsheet.yaml stream S17 | stream state | read | CC BY 4.0 (own) | D-003 hydrogen feed |
| SRC-9 | IAPWS R7-97(2012), Revised Release on the IAPWS Industrial Formulation 1997 (IAPWS-IF97), http://www.iapws.org/relguide/IF97-Rev.html | region 4: saturation-pressure equation (Eq. 30) psat(303.15 K) = 4.247 kPa, psat(313.15 K) = 7.384 kPa; saturation-temperature equation (Eq. 31) Tsat(450 kPa) = 421.06 K; latent heat h'' - h' at 450 kPa(a) = 2 120.2 kJ/kg from regions 1 and 2 at saturation | computed with the IF97 implementation of CoolProp 8.0.0 (`IF97::Water` backend), 2026-10-28 | open standard | D-007, D-008 |
| SRC-10 | US 6 303 088 B1 and US 6 355 222 (HBr gas devices) | none | found by search, not read | patent | not used |

Not found in open sources by this run: an integral heat of solution of HBr at about 5 mol water
per mol HBr, the absorber recovery and the vent HBr concentration of a real unit, the life of
the finishing carbon, a BAT-AEL or emission factor for HBr synthesis vents.

## 3. Reaction and model evidence

- **Chemistry.** H2 + Br2(g) -> 2 HBr, dHr = -102.6 kJ per mol extent (MJ per kmol) from the ATcT data of
  SRC-5 (-103.1 to -103.8 kJ with SRC-3's range of dHf(HBr)); SRC-1 gives 12.3 kcal = 51.5 kJ
  per mol HBr, the same. From liquid bromine the reaction releases 30.9 kJ/mol less (the
  vaporisation enthalpy, supplied by E-101). The only reaction in `process/reactions.yaml`.
- **Model basis: sourced conversion plus equilibrium limit, not kinetics** (D-005). The
  hydrogen-bromine flame converts 99.96-99.99 % of the bromine at a 2.6 % hydrogen excess
  (SRC-2, Example); this run uses 99.97 % at 5 % excess (conservative: more excess helps). The
  bromine left by the flame is a mixing effect: at the burner outlet `cheme process reactors`
  gives ln K = 30.0 (K = 1.1e13 at 448 K) and ln(Q/K) = -17.5, i.e. the gas is far from
  equilibrium. The activated-carbon bed R-102 (SRC-1, FIG. 3 variant) brings it to
  equilibrium; cheme's equilibrium reactor (ideal gas, at the outlet's 448 K and 240 kPa(a))
  converges there (ln(Q/K) = 2e-7) and leaves a Br2 mole fraction of 3.6e-12 with 2.4 mol-%
  H2, i.e. the residual bromine is consumed. No rate law is used or needed;
  none is invented. SRC-1 reports < 50 mg Br2 per kg HBr in its product, consistent with this.
- **Cross-check by cheme.** `cheme process reactors`: R101 duty -166.39 kW and R102 -0.053 kW
  on the elements basis, equal to `scripts/balance.py` (166.39 kW heat removed by the chamber
  cooling water; R102 0.05 kW = 0.5 K adiabatic rise). Block SYN: -178.3 kW = Q2 + Q3.
- **Absorption**: specified-value model (C201: 99.5 % of the HBr absorbed; C202: vent at
  5 mg/Nm3 HBr), not predicted. HBr-water VLE and heats of solution need an electrolyte model
  (core#364, unsupported). The 48 wt-% product lies just above the 47.6 wt-% azeotrope
  (SRC-4), so it is made by cooled (isothermal) absorption, as for HCl; an adiabatic absorber
  boiling off water would tend to the azeotrope and needs a separate check.

## 4. Decisions

## D-001 Boundary: saleable 48 wt-% acid, no storage (2026-10-28)
Decision: the boundary of section 1. Reason: the case notes ask for the burner over a catalyst
and absorption to 48 wt-% acid with bromine and hydrogen as boundary feeds. Rejected:
including bromine and acid storage and the emergency caustic absorber (start-up and upsets
only, no routine flows).

## D-002 Capacity and product: 1 000 kg/h HBr as 48.0 wt-% acid, 8000 h/a (2026-10-28)
Decision: 2 083.3 kg/h acid = 1 000 kg/h HBr = 8 kt/a HBr (100 %). ASSUMED: no published plant
basis was chosen (issue #130: capacity missing); the size is one burner line, 2.5 times the
400 kg/h example of SRC-1. 48 wt-% is the case notes' grade and the usual commercial strength
next to the azeotrope (SRC-4). The per-kg inventory does not depend on the size.

## D-003 Feeds: pure liquid bromine, hydrogen-1's hydrogen (2026-10-28)
Decision: S1 is pure Br2 liquid at 298.15 K, 400 kPa(a) (from storage by the tank farm's
transfer pump, outside); ASSUMED, bromine-1 does not exist yet. Real bromine carries < 0.05 %
chlorine and < 0.01 % water (SRC-1, Example): the chlorine would leave as HCl in the acid and
the water would enter the acid; both are left out (an HCl specification of the acid is an open
input). S3 has hydrogen-1 S17's state (99.9 mol-% H2, 0.1 mol-% N2, 2850 kPa(a), 313 K),
ASSUMED there, so `assumed` here; it is let down to the burner pressure in R-101's package
(Joule-Thomson change of about 1 K, neglected). The N2 passes to the vent.

## D-004 Hydrogen excess 5 mol-% (2026-10-28)
Decision: H2 fed = 1.05 x Br2. ASSUMED inside SRC-1's H2/Br2 range above 1 and below 1.4 and
above SRC-2's 2.6 %; the excess keeps bromine out of the acid and the vent. It sets the vent
(0.62 kg/h H2, 0.62 g per kg HBr) and the hydrogen use; to be fixed with the burner supplier.

## D-005 R101 99.97 % conversion (sourced), R102 the rest (equilibrium limit) (2026-10-28)
Decision: justified by section 3: R101 a conversion reactor, Br2 conversion 0.9997 (the
reaction's own, SRC-2); R102 an equilibrium reactor (ideal gas, outlet 448 K), adiabatic
(`process/simulation.yaml`, 0.5 K rise), catalyst ACT_C (`process/catalysts.yaml`, window
150-200 degC from SRC-1). Rejected: cheme's equilibrium reactor for R101 (the flame outlet is
not at equilibrium, section 3); inventing a rate law for the carbon bed.

## D-006 Balance method: independent script for the absorption section (2026-10-28)
Decision: `scripts/balance.py` (run `cheme run scripts/balance.py`) gives the flows and
compositions of S1-S3 and S6-S12 and the duties Q1-Q6, entered as `assumed` with
`source: scripts/balance.py`; S4 and S5 are calculated by cheme (propagate) and agree with the
script (1 000.805 kg/h). Reason: cheme cannot solve the absorber or the scrubber (electrolyte,
core#364) nor the bromine vaporiser (no package for Br2 liquid). The script closes mass
(2 084.27 kg/h) and Br and H; cheme validate confirms every block, step and element balance.

## D-007 Vaporiser, burner and cooler temperatures; LP steam (2026-10-28)
Decision: E-101 vaporises bromine at 300 kPa(a) (saturation 368.7 K, SRC-5) and superheats it
to 378 K (SRC-1 feeds bromine at 3 bar(a), 95 degC), with LP steam at 450 kPa(a) (421.1 K
saturated, SRC-9; 42 K above the bromine, as methanol-1's LP level); Q1 = 58.0 kW = 98.5 kg/h steam,
0.058 kWh per kg HBr. The burner chamber is water-cooled (SRC-1, SRC-2) and its gas leaves at
175 degC (inside SRC-1's 150-200 degC entry to the finishing stage) at 250 kPa(a) (inside the
1.8-10 bar(a) of SRC-1); E-102 cools to 60 degC (SRC-1's preferred value). Q2 = 166.4 kW and
Q3 = 11.8 kW to cooling water. Heat losses are not separated (they go to the same cooling).
Rejected for now: raising steam or hot water from the burner (SRC-1 and SRC-2 cool with water;
at 178 kW the recovery would cover the vaporiser's 58 kW three times over; an option for basic
engineering, as a hot-water loop to E-101).

## D-008 Absorption: isothermal falling film, scrubber with all absorption water (2026-10-28)
Decision: C201 absorbs 99.5 % of the HBr (ASSUMED) into weak acid from C202 and delivers
48 wt-% acid at 313 K, 200 kPa(a); its tail gas leaves at 313 K saturated with water (psat
7.385 kPa over the weak acid, taken as water, SRC-9). C202 receives all 1 083 kg/h of
demineralised water (298 K, 300 kPa(a)), runs at 190 kPa(a) and 303 K, and vents through a
pressure control valve at 105 kPa(a), water-saturated at scrubber conditions, with 5 mg/Nm3
HBr (ASSUMED; no limit value read). P201 pumps the acid to 300 kPa(a). All ASSUMED, to be
replaced by an absorber model or vendor data.
The weak acid S9 runs from C202 to C201 by gravity, without a pump: C202 is stacked above
C201 (the usual arrangement of HCl and HBr falling-film absorbers with their tail gas
scrubbers), and the liquid leg below the C202 packing, about 2 m of weak acid (about 20 kPa
at 1 000 kg/m3), raises the 190 kPa(a) of the scrubber to 210 kPa(a) at its outlet, enough to
enter the absorber head at 200 kPa(a) after about 10 kPa of line and distributor loss. ASSUMED
(no elevation study at the concept stage; review 2026-10-28-pfd-lci-review#4). Rejected: a
weak-acid pump (a rotating machine in HBr service for 20 kPa; its power would be negligible in
the LCI).

## D-009 Heat of solution of HBr to 48 wt-% acid: -72.0 kJ/mol, ASSUMED (2026-10-28)
Decision: the integral enthalpy of solution of HBr(g) in water to the product (4.87 mol water
per mol HBr) is taken as -72.0 kJ/mol at 298 K; acid heat capacity 2.10 kJ/(kg K). Both
ASSUMED: the infinite-dilution value is -85.14 kJ/mol (SRC-6); for HCl the integral heat at
about 4 mol water is about 0.82 of its infinite-dilution value (hydrogen-chloride-1 D-009), and
the same fraction of about 0.85 at 4.87 mol water is applied here. The heat of solution is
247 kW and the absorber duty Q4 232 kW (the acid leaves 15 K above the reference), so a 10 %
error moves Q4 by about 11 %. Gate: core#364 (no HBr-water enthalpy).

## D-010 Cooling water 25/35 degC (2026-10-28)
ASSUMED, as hydrogen-chloride-1. R-101, E-102 and C-201 are cooled: Q2 + Q3 + Q4 = 410.6 kW =
0.411 kWh per kg HBr.

## D-011 Electric power (2026-10-28)
Decision: Q5 product pump 0.08 kW (100 kPa, 1 490 kg/m3 (SRC-4), efficiency 0.5); Q6 3 kW for
burner management, instruments and analysers. Both ASSUMED; 3.08 kW in total (3.1 kWh/t HBr).
No blower and no bromine pump inside the boundary: the feed pressures drive the gas through
the unit to the vent (SRC-1 runs the burner above 1.8 bar(a)).

## D-012 Preliminary gate-to-gate LCI; equipment list (2026-10-28)
Decision: `lca/lca.yaml`, functional unit 1 kg HBr in the 48 wt-% acid (2.0833 kg acid). Every
background is declared `missing:` with the activity it should connect to (bromine-1 or a
bromine market, hydrogen-1's dataset, demineralised water, LP steam heat, grid electricity,
cooling water), so each is a gap, never 0. One product, no allocation. Emissions: the vent
(H2, HBr to air; N2 and water free); the burner burns no air and no carbon, so no combustion
emission exists (declared exclusion); bromine slip, start-up and upset venting, tank
breathing (outside) and leaks are declared exclusions without amounts; the R-102 carbon is a
cut-off flow with an amount (D-013). Br2 to air is declared elementary, not free, so that a
non-zero slip in a later balance is characterised or a gap (review #3). `lca/mappings.yaml`
maps only the LP steam, counted as heat delivered (kWh, `steam-heat`), for the Atlas build;
the other candidates are listed there. The equipment list holds the
seven PFD items with ASSUMED design data; the line and instrument lists stay empty until the
P&IDs (out of scope of this run).

## D-013 R-102 activated carbon: a cut-off flow with an ASSUMED amount (2026-10-28)
Decision: the make-up activated carbon of the finishing bed and the bromine-loaded spent
carbon are routine flows, recorded as `cutoff:` entries of `lca/lca.yaml` with 130 kg/a each,
so that the 1 % mass criterion is checked, instead of a non-routine exclusion without an
amount (review 2026-10-28-pfd-lci-review#2). Basis, all ASSUMED (no bed volume or bed life in
the open sources read): 284 Nm3/h of gas through R-102 (S4, 12.7 kmol/h), a gas hourly space
velocity of 1 000 1/h, so 0.29 m3 of carbon, 450 kg/m3 bulk density, one change-out a year.
That is 1.6e-5 kg per kg HBr and 0.0008 % of the input mass, far below the 1 % rule. Rejected:
a `missing:` carbon feed and a waste output in the inventory (a gap for a flow this small would
only add noise to the coverage; revisit when the bed is sized with a vendor).

## 5. Results of this stage

- `cheme validate`: 0 errors, 0 warnings. `cheme process streams`: blocks VAP (987.5 kg/h),
  SYN (1 000.8 kg/h) and ABS (2 084.3 kg/h) and every step balance; extents HBR_SYN 6.1777
  (R101) + 0.0019 (R102) kmol/h.
- Per kg HBr: bromine 0.9875 kg (the stoichiometric 0.98754 plus 0.04 ug vent loss), hydrogen
  feed 0.01326 kg (0.01308 kg H2), demineralised water 1.0835 kg, LP steam 0.058 kWh
  (0.0985 kg), electricity 0.0031 kWh, cooling 0.411 kWh; vent 0.94 g (0.62 g H2, 0.18 g N2,
  0.13 g water, 0.036 mg HBr).
- LCI (`cheme assess lca --inventory --write`, `--coverage`, `--balance`): mass, Br and H close
  to 0.00 %; classification "partial screening carbon footprint" with 8 gaps (BR2, H2, DMW,
  LPS, POWER, CW unlinked; H2 and HBr to air without a climate factor). The `--balance`
  "energy closure 0.0 %" counts steam, electricity and cooling only, not the reaction and
  absorption heat of the feeds, so it is not an energy-balance finding. A hand check of the
  whole unit at 298.15 K: 58.0 kW steam + 123.1 kW reaction heat from liquid bromine + 247.2 kW
  heat of solution - 18.2 kW sensible heat of the acid at 313 K = 410.0 kW against 410.6 kW
  cooling (0.14 %, feed and vent sensible heats).
- `cheme check`: every concept gate ok except layout-plot-plan (layout out of scope of this
  run). `cheme maturity`: calculation maturity none, so the claimed design maturity concept
  exceeds the evidence (warning, as in hydrogen-chloride-1): "balanced" fails on the feed flows
  S1, S3, S10 (design choices, `assumed`, not `given`) and on the specified splits of C201 and
  C202 (ASSUMED recoveries, no source); R101 (sourced conversion) and R102 (equilibrium model)
  pass. "predictive" needs a simulation, gated by core#364.
- Library build: `scripts/build_catalog.py --strict` accepts the manifest (only "no preview
  rendered" warnings); `scripts/build_lci.py` was not run (openpyxl missing in this
  environment).

## 6. Methods, dependencies and gated steps

| step | method here | status | gate |
|---|---|---|---|
| burner composition | conversion 0.9997 (SRC-2) | calculated by cheme | none |
| finishing bed | equilibrium reactor, ideal gas (section 3), adiabatic | calculated by cheme | none |
| burner and cooler duties | cheme reactor duty (ideal gas) | calculated, equal to the script | none for the gas side |
| bromine vaporiser | script (dHf of Br2 gas as latent heat at 298 K + ideal-gas superheat) | ASSUMED path | no package covers liquid Br2 (`props --coverage`) |
| absorber, scrubber | specified values (script) | ASSUMED | core#364: HBr-water VLE, heat of solution, acid enthalpy unsupported |
| stream properties, energy balances | not filled | not evaluable | no package for Br2/HBr gas or HBr-water |
| simulation | none | not run | DWSIM route refuses electrolytes |
| LCI | foreground from the flowsheet | written | backgrounds missing; registry entries missing (section 7) |

## 7. Open inputs and library items

- Open inputs: burner hydrogen excess and Br2 conversion of the chosen burner (supplier),
  finishing-carbon life and disposal, absorber recovery and vent HBr (supplier or an
  electrolyte absorber model), integral heat of solution of HBr near 5 mol water at source,
  real bromine impurities (Cl2 -> HCl in the acid, water), site and capacity, burner heat
  recovery (D-007), start-up and upset venting.
- Missing in `chemicals/chemicals.yaml` (consolidated PR later): `bromine`,
  `hydrogen-bromide` (and a grade such as `hydrobromic-acid/48` for the solution). Missing in
  `lci/mappings.yaml`: a `bromine` technosphere entry (or prefer_atlas to bromine-1 once it
  exists), a demineralised-water entry (#45), biosphere identities for hydrogen bromide and
  hydrogen to air. The library has no bromine-1 process yet.
- Next stage: review of this concept, then a bromine-1 case to give the main feed a dataset;
  source the burner and absorber data, replace D-009 when core#364 supports HBr-water, then the
  P&IDs (pid-draft) and the LCI backgrounds (link hydrogen-1's dataset and the utilities).
