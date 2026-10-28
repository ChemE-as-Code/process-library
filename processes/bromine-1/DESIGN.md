# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
The numbers live in `process/*.yaml` and `scripts/balance.py`; the stream table is generated:
`cheme process streams --md` (provenance letter per value). Issue:
ChemE-as-Code/process-library#136.

Run record of this stage (2026-10-28): library branch `case/bromine-1` from `cc5624f`;
cheme-as-code 0.8.0 (pyDEXPI 2.1.0), Python 3.15.0; DWSIM not used. Core issues #364
(electrolytes) and #369 (LLE) named in the issue could not be read (`gh`: not resolvable from this
account). As installed, `cheme process methods` lists ENRTL-PR and PITZER-RKS as unsupported and
the electrolyte route as **NaCl-H2O only**, so the Ca/Na chloride brine with Br2/Cl2 is not
covered by any phase, property or simulation route of this cheme (section 6). The route uses no
liquid-liquid extraction, so #369 does not apply.

## 1. Route and boundary memo

- **Route** (issue #136 case notes): chlorine oxidation of a bromide brine
  (2 Br- + Cl2 -> Br2 + 2 Cl-) in a hot-brine **steaming-out tower** (the Kubierschky type: brine
  at the top, chlorine and live steam at the bottom, bromine stripped overhead), condensation,
  gravity separation of crude bromine from bromine water, chlorine stripping of the crude
  bromine, drying with 98 wt-% sulfuric acid. Brine and route identity: Wikipedia "Bromine",
  section Occurrence and production (chlorine oxidation, stripping with steam or air,
  condensation and purification); US 4 719 096 and US 4 725 425, Background (conventional
  atmospheric towers on Arkansas brine).
- **Rejected alternatives.** Air blowing-out with SO2/HBr absorption (the seawater route): it
  suits dilute brines (seawater 65 ppm bromine, Wikipedia "Bromine") and needs an absorption and
  second oxidation stage; at 4 300 mg/kg bromide and a brine already near 90 degC from the wells,
  direct steaming-out is the established choice (US 4 719 096, Background). The vacuum
  steaming-out variants of US 4 719 096 / US 4 725 425 (60-75 % less steam) are patented
  improvements: noted as the main improvement lever (section 9), not the base case. Dead Sea end
  brine (0.4 % bromide in Dead Sea water, Wikipedia "Bromine") was not taken: no open source for
  an end-brine composition was found by this run, whereas the Arkansas brine has open,
  locatable constituent ranges (D-004).
- **Boundary** (D-001): brine at the plant fence (wells, well pumps and gathering pipeline
  outside) to dry bromine to storage; the neutralised tail brine leaves to reinjection
  (injection pumps and wells outside). Inside: brine feed pump P-101, steaming-out tower C-101,
  condenser E-102, separator V-103, purification column C-104, bromine cooler E-105, drying tower
  C-106, tail brine neutraliser T-107. Outside: chlorine production and liquefaction, bromine
  storage and loading, emergency scrubbing, steam and cooling water generation, spent acid
  treatment, bromine derivatives (about 85 % of Arkansas bromine is used on site, AGS).
- **What crosses the boundary**: BRINE, CL2, H2SO4, LIME (raw materials), LPS (live steam,
  material), LPH (reboiler steam heat), POWER (utilities in), BR2 (product), TAILB, SPACID
  (wastes to treatment), CW (utility out).
- **Normalisation**: per kg of the bromine product (99.957 wt-% Br2).
- **Link to other library processes**: chlorine is chlor-alkali-1's product CL2 (its S42),
  **liquefied** and vaporised at the user, so its 1.8 vol-% O2 is not carried (D-003); sulfuric
  acid is sulfuric-acid-1's product. Neither is integrated: they are boundary feeds with the
  link recorded in `lca/lca.yaml`.

## 2. Source register

Read status: "read" = the cited locator was read in the page text by this run (through a fetch
tool's extraction); "metadata" = only the identity was checked. Facts are in our own words;
nothing copied.

| id | source | locator | status | terms | used for |
|---|---|---|---|---|---|
| SRC-1 | US 4 719 096 (Ethyl Corp.), "Continuous two-stage vacuum process for recovering bromine", https://patents.google.com/patent/US4719096 | Detailed Description: typical brine 3 000-5 000 ppm bromide (as NaBr), 200 000-250 000 ppm chloride, 150-200 ppm NH3, 100-300 ppm H2S, 10-20 ppm NaI; tail brine 50-200 ppm bromide; feed brine 180-210 degF; conventional chlorine 0.55-0.60 lb/lb Br2 (stoichiometric 0.42-0.44) for 95-96 % recovery; conventional net steam 5.2-5.7 lb/lb Br2. Background: conventional towers at 14.7-15.0 psia, brine boiling at 228-230 degF, about 40 % excess chlorine on natural brines because of side reactions; lime used to neutralise the tail brine (Summary) | read (Google Patents text, via fetch extraction) | patent text: facts only | D-004, D-005, D-006, D-009; checks in section 5 |
| SRC-2 | US 4 725 425 (Ethyl Corp.), "Continuous vacuum process for recovering bromine", https://patents.google.com/patent/US4725425 | Detailed Description and claims: brine 2 000-6 000 ppm NaBr, 180-210 degF; tail brine to a neutraliser | read | patent text: facts only | D-004 (corroboration) |
| SRC-3 | Arkansas Geological Survey, "Bromine (Brine)", https://www.geology.arkansas.gov/minerals/industrial/bromine-brine.html | 2nd paragraph: original Smackover analyses 4 000-4 600 ppm bromine, 1.5-1.8 lb bromine recovered per barrel; 1st paragraph: about 85 % used at the producing site | read | state government page: facts only | D-004, recovery check |
| SRC-4 | Wikipedia, "Bromine production in the United States", https://en.wikipedia.org/wiki/Bromine_production_in_the_United_States | Smackover section: 5 000-6 000 ppm bromine; Introduction: 2007 capacities of the two Arkansas producers (148 and 130 kt/a) | read | CC BY-SA: facts only | D-002 scale context, D-004 range |
| SRC-5 | Wikipedia, "Bromine", https://en.wikipedia.org/wiki/Bromine | Occurrence and production (route steps; Dead Sea 0.4 % bromide, seawater 65 ppm); infobox (bp 58.8 degC, heat of vaporisation 29.96 kJ/mol) | read (first 100 000 characters) | CC BY-SA: facts only | route identity, physical data in scripts/balance.py |
| SRC-6 | USGS, "Elemental and isotope geochemistry of Smackover Formation brines, Alabama and Arkansas", https://www.usgs.gov/publications/elemental-and-isotope-geochemistry-smackover-formation-brines-alabama-and-arkansas | abstract (via search summary): Na-Ca-Cl facies, sulfate-depleted | metadata | US government | D-004 cation split (qualitative only) |
| SRC-7 | NBS Tables of Chemical Thermodynamic Properties (Wagman et al. 1982, J. Phys. Chem. Ref. Data 11, Suppl. 2) | dHf(298 K): Cl-(aq) -167.16, Br-(aq) -121.55, Br2(aq) -2.59, Br2(g) 30.91, H2S(aq) -39.7 kJ/mol | **recalled, not re-read in this run** (O-5) | US government data | heats of reaction, tower energy balance |
| SRC-8 | IAPWS-IF97 steam properties; Antoine constants of water (8.07131, 1730.63, 233.426; mmHg, degC) | saturated steam 350 kPa(a): 411 K, h'' 2731.6 kJ/kg | values as commonly tabulated | open standard | D-006 |
| SRC-9 | Boldyryev and Varbanov (2014), Process integration for bromine plant, Chem. Eng. Trans. 39, 1423-1428, doi:10.3303/CET1439238 | whole paper | read | open access (AIDIC): facts only | not used for numbers: a sea-bittern ferric-bromide route in Crimea, site heating 3.1 MW, no per-tonne data; confirms the scarcity of open energy data |
| SRC-10 | Arkansas Geological Survey OFR 2023-01 (Li 2023), Smackover Formation lithium update | text | read (no major-ion table found) | state government | not used |
| SRC-11 | Ullmann's Encyclopedia, "Bromine", doi:10.1002/14356007.a04_391.pub2 | none | metadata (issue #136 lead) | licensed | route identity only; no number taken |
| SRC-12 | chlor-alkali-1 (this library), process/flowsheet.yaml stream S42 | state of the chlorine product | read | CC BY 4.0 (own) | D-003 |

Not found in open sources by this run: a full major-ion analysis (Na, Ca, Mg) of a Smackover
bromine brine, the water activity and heat capacity of such a brine, a Dead Sea end-brine
analysis, the composition of crude bromine and bromine water, the product specification of
commercial bromine, the water in wet bromine, spent drying-acid strength, the vent flow and its
bromine/chlorine content, and the lime dose of a real tail-brine neutraliser.

## 3. Reaction and model evidence

- **Chemistry** (`process/reactions.yaml`): BR_OX 2 NaBr + Cl2 -> 2 NaCl + Br2 (the brine's
  bromide carried as NaBr); H2S_OX H2S + Cl2 -> S + 2 HCl (side reaction); NEUT
  2 HCl + Ca(OH)2 -> CaCl2 + 2 H2O (tail brine). Heats of reaction from SRC-7: BR_OX
  -93.8 kJ per mol extent (aqueous ions, Br2 dissolved), H2S_OX -294.6 kJ (recalled values,
  marked `assumed`, O-5).
- **Model basis: specified conversions, no kinetics** (D-005). The bromide conversion is the
  *reported performance* of conventional steaming-out towers: 95-96 % recovery (SRC-1); 95.5 %
  is taken. No rate law, no equilibrium constant: the oxidation of bromide by chlorine is fast
  and nearly complete in acid brine; what limits recovery in practice is stripping, chlorine
  distribution and side reactions, none of which a conversion reactor predicts. A speciation
  model (Br2/Br3-/BrCl/HOBr in a 31 wt-% Ca/Na chloride brine) would need an electrolyte
  package (core#364, not available). Labelled in cheme as specified, unsourced conversions
  (`cheme maturity`: model basis "conversion, specified").
- **Side reaction as the chlorine sink** (D-005). SRC-1 reports that natural brines need
  0.55-0.60 lb Cl2/lb Br2 against 0.42-0.44 stoichiometric because side reactions consume part
  of the chlorine, and lists H2S (100-300 ppm) and NH3 (150-200 ppm) among the brine's
  constituents. The model lets H2S at 250 ppm take the excess chlorine to elemental sulfur
  (one Cl2 per H2S): the resulting chlorine use, 0.571 kg/kg Br2, falls inside the patent's
  range without tuning anything but the H2S content within its reported range. This is a
  calibrated representation, not a mechanism: real side reactions include NH3 (chloramines,
  N2), further oxidation of sulfur to sulfate, iron and organics. Ammonia is not modelled; with
  its full chlorine demand the patent's chlorine use would be exceeded, so part of it must
  stay unreacted or be removed upstream (O-3).
- **Stripping** (D-006). Free bromine is taken to leave entirely overhead (no free halogen in
  the tail brine); the overhead water follows from the water partial pressure over the brine at
  the top (feed temperature + 2 K, 105 kPa(a), water activity 0.75 ASSUMED). As a plausibility
  check on volatility, Henry's law for Br2 in water (about 0.7 M/atm at 25 degC, strongly
  decreasing with temperature; Sander's compilation, values recalled, not re-read) gives Br2 a K-value of order
  10^3 relative to the liquid at 100 degC, so stripping is not the steam-limiting step: the
  steam is set by heating the brine to its boiling point, as SRC-1 states. Not used as an input.

## 4. Decisions

### D-001 Boundary: brine at the fence to dry bromine; tail brine to reinjection (2026-10-28)
Decision: section 1. Reason: the issue asks for oxidation, stripping, condensation, separation
and drying; brine production and reinjection are field operations with their own wells.
Rejected: including well pumping (no open data on depths/rates for a design value). Assumptions:
brine arrives at 150 kPa(a) and 195 degF. The tail brine leaves at the T-107 pressure
(120 kPa(a)). The reinjection system outside the boundary starts with the transfer pump that
draws from T-107 and lifts the 933 t/h (about 0.22 m3/s) to the injection header, followed by the
injection pumps and wells (review R-02).

### D-002 Capacity and product (2026-10-28)
Decision: 3 750 kg/h dry bromine, 8000 h/a = 30 kt/a, product 99.957 wt-% Br2 with 400 ppm Cl2
and 30 ppm water. Reason: one train of the size of an Arkansas satellite plant (two producers
with 130-148 kt/a each over several plants in 2007, SRC-4); chosen, not a client figure. The
specification is ASSUMED (no open commercial spec found): chlorine and water are the
impurities the process controls. Rejected: per-unit design only (the issue asks for a balanced
PFD at a named scale).

### D-003 Chlorine feed: chlor-alkali-1's chlorine, liquefied (2026-10-28)
Decision: pure Cl2 gas at 400 kPa(a), 313 K, from vaporised liquid chlorine. Reason: inerts in
cell-gas chlorine (O2 1.8 vol-% in chlor-alkali-1's S42) would need a purge and a vent scrubber
that this concept balance does not carry; bromine plants receive liquid chlorine or a dedicated
chlor-alkali supply. Rejected: chlor-alkali-1's gas as it is (O2 would accumulate in the
condenser-separator loop). Assumptions: liquefaction belongs to the chlorine background (noted
in `lca/lca.yaml`).

### D-004 Brine composition (2026-10-28)
Decision: per kg brine 4 300 mg bromide, 185 000 mg chloride, 30 000 mg calcium (sodium by charge
balance), 250 mg H2S; as NaBr 0.554 wt-%, CaCl2 8.31 wt-%, NaCl 21.75 wt-%, water 69.37 wt-%;
195 degF. Reason: bromide in the middle of the AGS 4 000-4 600 ppm (SRC-3) and of US 4 719 096's
3 000-5 000 ppm (SRC-1); the mass basis is chosen because the resulting recovery, 1.73 lb Br2
per barrel at 1.2 kg/L, falls in the AGS 1.5-1.8 lb/bbl (with a mg/L reading it would be 1.44);
chloride: SRC-1's 200 000-250 000 ppm read as mg/L at 1.2 kg/L, so that the salts stay near
31 wt-%; feed temperature the midpoint of 180-210 degF (SRC-1, SRC-2). ASSUMED: calcium (Na-Ca-Cl
facies, SRC-6, but no number found), density 1.2 kg/L, and the omission of NH3, NaI, Mg, K, Sr,
Li, Fe and organics. Halite saturation of the brine at 195-229 degF is not checked (no
electrolyte model, O-2). Rejected: a Dead Sea end brine (no open analysis found).

### D-005 Reactions and recovery (2026-10-28)
Decision: section 3: 95.5 % of the bromide oxidised and recovered; all H2S oxidised to sulfur;
chlorine fed = bromide demand + H2S demand + the product's Cl2 = 2 139 kg/h. Reason: SRC-1
performance data. Assumptions: no bromine leaves with the tail brine as free Br2, the spent acid
or a vent; the 4.5 % unrecovered bromide stays as bromide (189 mg/kg in the tail brine).

### D-006 Balance model and steam (2026-10-28)
Decision: an independent specified-split balance, `scripts/balance.py`, gives every stream; the
live steam follows from the script's tower energy balance: brine heat-up from 195 to 229 degF
(13.9 MW at cp 2.9 kJ/kg K ASSUMED), overhead water and bromine, heating of the recycles and
chlorine, minus the reaction heat (1.16 MW, SRC-7), with 3 % heat loss (ASSUMED); LP steam
350 kPa(a) saturated, condensing into the brine. Result 21.8 t/h = 5.82 kg/kg Br2. Reason: the
patent figure is a range for unspecified plants; calculating it from stated inputs makes the
dependence visible (about 0.32 kg/kg Br2 per kelvin of feed temperature). Rejected: copying
5.45 kg/kg from SRC-1 as an assumed value (the energy balance would then be unchecked).
Assumptions: water activity 0.75, cp 2.9 kJ/kg K and density 1.2 kg/L of the brine
(ASSUMED; no property package for this brine, core#364); tower at 105 kPa(a) top, 130 kPa(a)
bottom.

### D-007 Condensation, separation and chlorine stripping (2026-10-28)
Decision: E-102 condenses the overhead to 30 degC (623 kW); V-103 decants bromine water with
3.5 wt-% Br2 (returned to C-101) from crude bromine with 2 wt-% Cl2 and 0.1 wt-% water; C-104
strips the crude to 400 ppm Cl2, its overhead (Cl2, an equal mass of Br2 and the excess water,
155 kg/h) returned as vapour to C-101; reflux ratio 3, reboiler 61 kW LP steam, condenser
34 kW. Reason: closes the chlorine loop inside the plant (the conventional arrangement: halogen
returned to the tower). All values ASSUMED (no open data); the Br2 solubility in water near
3.5 wt-% is the order of the value commonly tabulated near 20 degC.

### D-008 Drying (2026-10-28)
Decision: E-105 cools the bromine to 30 degC; C-106 dries it from 0.05 wt-% to 30 ppm water with
98 wt-% sulfuric acid leaving at 80 wt-% (7.8 kg/h in, 9.6 kg/h out). Reason: the drying step of
the issue's route. ASSUMED: water in wet bromine, final water, spent acid strength; bromine
dissolved in the spent acid not modelled.

### D-009 Tail brine neutralisation and reinjection (2026-10-28)
Decision: T-107 neutralises the 488 kg/h HCl of the side reaction with 496 kg/h hydrated lime
(stoichiometric, pure Ca(OH)2 ASSUMED) and sends 933 t/h brine to reinjection at 382.89 K and
120 kPa(a). Reason: SRC-1 names lime for the tail brine and SRC-2 a neutraliser before
discharge; reinjection keeps the brine out of surface water. Free halogen in the tail brine
(and its reduction, e.g. with sulfite) is not modelled (O-4).
Energy (review R-01, 2026-10-28): T-107 is a closed agitated tank held at 120 kPa(a) (ASSUMED,
inside its 0.5 barg design), above the brine's boiling pressure at 229 degF (about 103 kPa(a),
SRC-1), so the tail brine does not flash and no water vapour leaves T-107. Its vent carries only
displaced gas to the vent scrubber (exclusion `vent`, O-9). The neutralisation
Ca(OH)2(s) + 2 H+ -> Ca2+ + 2 H2O releases 128.4 kJ/mol (from the SRC-7 formation enthalpies of
Ca(OH)2(s), Ca2+(aq) and H2O(l)): 239 kW, less 14 kW to heat the lime from 25 degC
(cp 1.18 kJ/kg K ASSUMED), so the brine warms by 0.30 K to 382.89 K (tank heat loss neglected,
ASSUMED). `scripts/balance.py` computes it. The earlier 375 K had no basis. Rejected: an
atmospheric tank with a flash (about 1 t/h of vapour with halogen traces to treat, for no
process benefit).
Pressure (review R-02): S17 leaves at the T-107 pressure. The transfer pump from T-107 to the
injection header belongs to the reinjection system outside the boundary (D-001). Its
electricity is counted in the reinjection treatment that `product:TAILB` will link to
(`lca/lca.yaml`), not in Q6.

### D-010 Cooling water 25/35 degC (2026-10-28)
ASSUMED site cooling water; 671.5 kW in total (E-102, C-104 condenser, E-105).

### D-011 Power (2026-10-28)
P-101: 913 t/h at 1.2 kg/L, 350 kPa rise, eta 0.70: 105.6 kW; other drives 15 kW lumped
(ASSUMED). Brine well pumps and the reinjection system are outside the boundary (D-001). That
includes the tail-brine transfer pump from T-107, roughly 50-60 kW for a 170-200 kPa lift
(review R-02). The plant's power is therefore a known underestimate of the field's: the gate's
0.0322 kWh/kg would be about 0.047 kWh/kg with the transfer pump.

### D-012 Equipment materials (2026-10-28)
Placeholders for the materials question only (equipment list): wet bromine and chlorine need
glass, PTFE/PVDF, tantalum or lead linings; the hot sour chloride brine needs FRP, brick-lined or
duplex/super-duplex. Not a materials selection.

### D-013 Preliminary gate-to-gate LCI (2026-10-28)
Decision: `lca/lca.yaml`: functional unit 1 kg of the bromine product (S12); every feed, utility
and waste route declared `missing:` with the background activity it should connect to; no
emissions to air or water in the balance (all chlorine and bromine leave as product or in the
reinjected brine); the vent, H2S/NH3 off-gas, non-routine releases, leaks and tank breathing
declared as emission exclusions with their reasons; one product, no allocation; the tail brine
and spent acid are wastes to treatment (reinjection, neutralisation/regeneration). Reason: the
issue's scope (no licensed values, gaps not zeros, library ADR on LCI gaps). Assumptions: live
steam counted in kg (condensate lost into the brine), reboiler steam in kWh.

## 5. Results and checks against the sources

Per kg of bromine product (`lca/inventory.csv`, from the flowsheet):

| exchange | amount | unit | stream |
|---|---|---|---|
| raw brine | 243.41 | kg | S1 |
| chlorine | 0.5705 | kg | S3 |
| live LP steam | 5.815 | kg | S4 |
| reboiler LP steam heat | 0.0162 | kWh | Q2 |
| sulfuric acid 98 % | 0.00209 | kg | S13 |
| hydrated lime | 0.1323 | kg | S16 |
| electricity | 0.0322 | kWh | Q5, Q6 |
| cooling water (heat removed) | 0.1791 | kWh | Q1, Q3, Q4 |
| tail brine to reinjection | 248.93 | kg | S17 |
| spent sulfuric acid | 0.00256 | kg | S14 |

Mass balance of the inventory: 249.932 kg in = 249.932 kg out per kg Br2 (cheme: mass, element
and carbon-origin balances closed; energy closure not evaluable in core).

| check | model | source | verdict |
|---|---|---|---|
| chlorine use | 0.571 kg/kg Br2 | 0.55-0.60 lb/lb (SRC-1) | inside |
| excess over the bromide demand | 28.5 % | about 25 % side-reaction share at 95-96 % recovery; about 40 % on natural brines (SRC-1) | inside the span |
| live steam | 5.82 kg/kg Br2 | 5.2-5.7 lb/lb, conventional net steam (SRC-1) | 2 % above the range |
| tail brine bromide | 189 mg/kg | 50-200 ppm (SRC-1) | inside |
| recovery per barrel | 1.73 lb Br2/bbl | 1.5-1.8 lb/bbl (SRC-3) | inside |
| tail brine temperature | 229 degF | brine boils at 228-230 degF (SRC-1) | input |

`cheme process streams`: every block and step balances (LIB, REC, PUR, TBT), with reaction
extents BR_OX 23.46, H2S_OX 6.70, NEUT 6.70 kmol/h. `cheme validate`: 0 errors, 0 warnings.
`cheme check --stage concept`: 6 ok, layout-plot-plan fails (layout out of scope of this run).
`cheme maturity`: calculation maturity none (feeds and specified values are `assumed`, the
reactors and separators are specified, no simulation), so the evidence supports no design
maturity. The manifest has no level below concept. It claims concept, and `validation.notes`
says that this claim exceeds the evidence (warning `cheme.maturity-claim-exceeds`, review R-03).
A level below concept is a library item (section 8).

## 6. Methods, dependencies and gated steps

| step | method now | what it needs | gate |
|---|---|---|---|
| tower and separations | specified splits (scripts/balance.py) | rate-based or equilibrium-stage model of Br2/Cl2 stripping from a Ca/Na chloride brine, with speciation (Br3-, BrCl, HOBr) | core#364 (electrolytes; installed cheme: NaCl-H2O only) |
| stream enthalpies, energy closure in core | script energy balance, brine cp and water activity ASSUMED | an electrolyte property package for NaCl-CaCl2-NaBr-H2O and Br2/Cl2 solubility | core#364 |
| halite saturation, solids | not checked | solid-liquid equilibrium of NaCl in CaCl2 brine at 90-110 degC | core#364 |
| DWSIM simulation (`cheme process simulate`) | not run | a property package for the brine and liquid bromine; P101 maps to no unit operation in the current translation | core#364 |
| LLE | not used | n/a | core#369 not applicable |
| LCI background | all gaps | registry entries and shared mappings (section 8); chlor-alkali-1 and sulfuric-acid-1 datasets | library consolidated PR |

## 7. Open inputs

- O-1 A full major-ion analysis of the design brine (Na, Ca, Mg, K, Sr, Fe, NH3, H2S, organics,
  density, temperature) from one source; calcium and density are ASSUMED.
- O-2 Brine heat capacity, water activity and halite saturation at 90-110 degC (property data
  or an electrolyte model); the steam depends on cp linearly.
- O-3 The side reactions: the actual chlorine sinks (NH3, H2S to S or sulfate, Fe, organics) and
  whether H2S is degassed before the tower; this sets the lime demand (0.132 kg/kg Br2 now) and
  possible H2S emissions.
- O-4 Free chlorine/bromine in the tail brine and whether it is reduced (sulfite) before
  reinjection; the vent flow (air in-leakage, inerts) and its scrubbing.
- O-5 Re-read the NBS (Wagman 1982) formation enthalpies used for the heats of reaction.
- O-6 Crude bromine and bromine water compositions, C-104 split and reflux, water in wet
  bromine, spent acid strength: all ASSUMED.
- O-7 Commercial bromine specification (purity, Cl2, water, organics).
- O-8 Brine and reinjection well pumping energy (outside the boundary, but the largest power
  users of a bromine field).
- O-9 The LCA schema has no process-vent emission-exclusion method; the vent exclusions are
  filed under equipment-leaks with the equipment named (core item).

## 8. Missing registry entries (for the consolidated library PR)

`chemicals/chemicals.yaml`: `bromine` (main product), `chlorine` (liquid), a bromide `brine` (or
produced brine) feed, `sulfuric-acid`, `calcium-hydroxide` (hydrated lime). `lci/mappings.yaml`:
a brine-extraction entry (with the resource "bromine, in ground brine"), produced-brine
reinjection, spent sulfuric acid treatment, an LP live-steam grade (feed:LPS is kept out of the
Atlas link, `atlas: false`, until one exists). Candidate mappings are listed in
`lca/mappings.yaml`. Manifest schema: a maturity level below `concept` for designs whose
calculation maturity is none (review R-03).

## 9. Recommended next stage

Basic engineering of the tower model once an electrolyte property route covers the brine
(core#364): replace the specified splits of C-101/V-103/C-104 by a stripping model checked
against SRC-1's recovery, chlorine and steam figures; close O-1..O-4 (brine analysis, side
reactions, vent and scrubber); add brine preheating with the hot tail brine and the vacuum
variant as an alternative (heating the brine, 13.9 MW, is more than the tower's whole net demand of 13.4 MW); then P&IDs. Acceptance checks:
chlorine 0.55-0.60 kg/kg, recovery 95-96 %, tail brine 50-200 mg/kg bromide, steam within
5.2-5.7 kg/kg for the atmospheric tower, LCI balances closed and the gaps listed.
