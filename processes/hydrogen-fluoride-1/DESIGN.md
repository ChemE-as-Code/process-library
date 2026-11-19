# Design decisions: hydrogen-fluoride-1

Anhydrous hydrogen fluoride (AHF) from acid-grade fluorspar and sulfuric acid in an indirectly
fired rotary kiln, with anhydrite and fluorosilicic acid as co-products. Concept stage, issue
ChemE-as-Code/process-library#513. Every number below is either taken from a source in the
register (with its locator), calculated by core from the files, or marked ASSUMED. Nothing is
copied from the sources: no tables, figures or text, only single facts in our own words.

## Source register

| id | source | access | used for |
|---|---|---|---|
| SRC-1 | European Commission JRC (2007), *Reference Document on Best Available Techniques for the Manufacture of Large Volume Inorganic Chemicals - Ammonia, Acids and Fertilisers* (LVIC-AAF BREF), chapter 6 Hydrofluoric acid, <https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/lvic_aaf.pdf> | open PDF, read (text extracted), 2026-11-19 | EU capacity about 300 kt/a, plants from below 5 to above 40 kt/a (6.1); main reaction (1) with dH = 59 kJ/mol and side reactions (2)-(9) (6.2.1); acid spar above 97 % CaF2 with SiO2, CaCO3, Fe/Al oxides each below 2 %, flotation fatty acids below 0.3 % (Table 6.2), dried at about 120 C (6.2.2); continuous indirectly heated rotary kilns, feed acid of 90-95 % H2SO4 from fresh acid, oleum and the scrubber acid, the plant under suction (6.2.3); 5-10 m2 of kiln surface per t/d of HF, 2.5-3 with spar calcination, pre-reactor (Table 6.3); process gas at about 150 or 220 C, anhydrite at 200-220 C (6.2.3); pre-purification with concentrated acid to below 100 C, condensation with chilled water or brine, low-boiler column (mainly SO2, SiF4), final H2SO4 scrubber, SiF4 absorber to H2SiF6, the cold acid of the final scrubber heated in the pre-purification column and mixed with fresh acid and oleum to the feed acid, high-boiler column at about 350 kg of steam (0.6 GJ) per t of HF (6.2.4); tail gas water or caustic scrubbing (6.2.5); anhydrite marketed or disposed of (6.2.6, 6.4.3); AHF boils at 19.5 C, stored below 15 C in carbon steel (6.2.7); consumption per t of HF (Table 6.4); dust, SO2 and fluoride emissions (Tables 6.5, 6.6, 6.12); effluent and solid waste, about 3.7 t of CaSO4 per t (Tables 6.7, 6.8); options to improve heat transfer (Table 6.9); kiln shell exit gas up to about 400 C (6.4.2); 25-35 % fluosilicic acid (6.4.4); alkaline absorption at pH 7-9, CO2 not absorbed at pH 8 or less (6.4.7); BAT fuel 4-5 GJ/t for new AHF plants (Table 6.14); the fluosilicic acid process (6.4.10, rejected in D-001) |
| SRC-2 | Bayer AG (2004), *Process for preparing hydrogen fluoride in a rotary tube furnace*, US 6 699 455 B2 (Lanxess), <https://patents.google.com/patent/US6699455B2/en> | open, read (description, examples, claims), 2026-11-19 | the kiln in three equal zones each heated indirectly by its own combustion chambers, the hottest at the feed end; spar preheated indirectly to 350-450 C, acid heated against the HF gas to 80-180 C, both premixed in a screw mixer; zone wall temperatures (claims 3, 5, 7); Example 4: a 20 m x 2.5 m kiln, 80 kg/min of spar at about 400 C and 109 kg/min of H2SO4 (100 %) at about 120 C, one third straight into zone 1, nine burners, at most 189 m3/h of natural gas, walls 370 C falling to 210 C, HF gas out at 205 C, solids at 204 C with 0.5-1.1 % CaF2 and 0.5-1.7 % H2SO4; prior art with 2-5 % of each; capacity up more than 30 % |
| SRC-3 | PubChem (CIDs 14917, 84512, 24497, 24682) and ChEBI via EBI OLS (29228, 35437, 31346, 29384) | open, 2026-11-19 | identity of the registry entries hydrogen-fluoride, calcium-fluoride, calcium-sulfate, sulfur-trioxide (the fluorosilicic acid uses the existing entry fluosilicic-acid) |
| SRC-4 | `chemicals` 1.5.2 and `thermo` 0.6.1 Python packages (C. Bell et al.) | open-source packages queried, 2026-11-19; single values, facts only | single values (library ADR 0037): formation enthalpies CaF2(s) -1228.0, CaSO4(s) -1434.5, H2SO4(l) -814.0, SO3(l) -441.0 kJ/mol (method CRC, the CRC Handbook's tables as the package bundles them, not read here), HF(g) -272.711, H2O(l) -285.825, H2O(g) -241.822, CH4(g) -74.534 kJ/mol (chemicals); normal boiling points HF 293.15, SO2 263.14, SiF4 187.15, SO3 317.65, H2SO4 610.15 K (CRC_INORG, HEOS for SO2) and water 373.12 K (HEOS); heat of vaporisation of HF 7.52 kJ/mol at 292.67 K (thermo, method DIPPR_PERRY_8E: Perry's 8th edition DIPPR fit as the package bundles it, not read here); heats of vaporisation of water 2441.7, 2282.5 and 2120.4 kJ/kg at 298.15, 363.15 and 421 K and of SO2 389.6 kJ/kg at its boiling point (HEOS_FIT); heat capacities: HF ideal gas 1.457 kJ/(kg K) (TRCIG), HF liquid 2.96 kJ/(kg K) at 280.65 K (VDI_TABULAR), CaF2 solid 68.8-79.9 J/(mol K) at 300-650 K (WEBBOOK_SHOMATE, the NIST WebBook's Shomate fit), CaSO4 solid 110.2 J/(mol K) at 400 K (PERRY151), H2SO4 liquid 138.9 J/(mol K) (CRCSTD), water vapour 1.896 kJ/(kg K) at 388 K (HEOS_FIT). These are facts with their source, not open data |

Sources looked for and not read: an open vapour-liquid equilibrium data set of HF-H2O and of HF
with SO2 and SiF4, open absorption data of HF and water in sulfuric acid, and an open
specification of commercial AHF. Each is an assumption below (L-2).

## Decisions

### D-001 Route

**Chosen: acid-grade fluorspar with sulfuric acid in an indirectly fired rotary kiln (spar
preheated, acid premixed in a screw mixer), sulfuric acid pre-purification with the acid
returned to the kiln, refrigerated condensation, low- and high-boiler distillation, a final
sulfuric acid scrubber, SiF4 absorption and alkaline tail-gas scrubbing (SRC-1, SRC-2).** It is
how HF is made in Europe: the BREF describes no other industrial route from a mineral, and the
patent's kiln is a real plant's (Bayer/Lanxess, Leverkusen).

Recorded and rejected:

- *HF from fluosilicic acid* (SRC-1, 6.4.10): H2SiF6 from phosphoric acid plants decomposed in
  strong sulfuric acid. It uses a by-product instead of fluorspar, but the BREF gives it 5 to 6
  times the direct energy of the fluorspar route and 28-30 t of sulfuric acid per t of HF to
  recycle to a phosphoric acid plant; it only makes sense on an integrated phosphate site, which
  the library does not have (phosphoric-acid-1 is a manifest-only entry).
- *Pre-reactor (kneader) or spar calcination before the kiln* (SRC-1, Tables 6.3 and 6.9): they
  raise a given kiln's capacity. The patent's indirect spar preheating with zoned firing reaches
  2.9 m2 of kiln shell per t/d of HF without either (R-101 in the equipment list); the variants
  change the kiln's size and fuel, not the balance, and have no open design data.
- *A fluidised bed reactor* (described in SRC-2 as prior art): the HF must then be separated from
  the fluidising gas and fine spar dust is carried out; no industrial plant is described.
- *Aqueous hydrofluoric acid as the product*: the issue asks for AHF; the BREF says the solution
  costs more fuel in the kiln. Diluting AHF to 40-85 % is a downstream step (SRC-1, 6.2.4).

### D-002 Capacity and basis

4800 kg/h of dried spar to one kiln, the feed of SRC-2's Example 4 (80 kg/min), so that the kiln
size, the temperatures and the residues of the patent apply to the design case. It gives 2304.8
kg/h of AHF (S17), 18 439 t/a in 8000 h (ASSUMED), inside SRC-1's 5-40 kt/a of EU plants. The
functional unit is 1 kg of S17.

### D-003 Continuous plant, one design case

The process is continuous (SRC-1, 6.2.3), so no recipe and no reactor-hazard screening of a
batch apply: the kiln reaction is endothermic and fed by the burners, so there is no thermal
runaway of the kind core screens. The hazards are reasoned in D-012.

### D-004 Components and the spar

The spar is 97.5 wt% CaF2, 1.0 SiO2, 1.0 CaCO3, 0.4 Fe2O3 (standing for the iron and aluminium
oxides) and 0.1 stearic acid (standing for the flotation fatty acids), ASSUMED inside SRC-1's
Table 6.2 limits; MgCO3, BaSO4, sulfides and phosphates are left out (L-3). It is dried before
the plant (SRC-1, 6.2.2: some plants buy it dried) and preheated to 673.15 K (SRC-2). The solids
are components with phase: solid (core ADR 0025).

### D-005 The kiln's side reactions

R2 to R5 follow SRC-1's reactions (2) to (5). Reaction (5) as the BREF prints it does not balance
in oxygen; written for stearic acid (n = 16) and balanced here, one fatty acid reduces 52 H2SO4
to 52 SO2 with 18 CO2 and 70 H2O. 90 % of the silica leaves as SiF4 (ASSUMED; SRC-1 says the
silica ends in the anhydrite or as SiF4); the carbonate, the oxides and the organics react
completely (ASSUMED). The H2S and sulfur of reactions (7) and (8) are left out with the spar's
sulfides (L-3).

### D-006 The kiln

- One conversion reactor R101 with R1 to R5 (core's conversion on the inlet, all at once). R1
  converts 0.9613 of the CaF2 fed (ASSUMED), so that with R2 the kiln solids keep 0.8 wt% CaF2,
  inside SRC-2's 0.5-1.1 wt% (S7: 68.8 kg/h in 8310.4 kg/h).
- The fresh acid S20 is set by the design specification `acid` for 1.0 wt% free H2SO4 in the kiln
  solids S7, inside SRC-2's 0.5-1.7 wt%: 5348.4 kg/h of 98.5 wt% acid. With the oleum's SO3 the
  plant uses 6043.8 kg/h of H2SO4 equivalent, 2.622 kg per kg of HF (SRC-1: 2.6-2.7). SRC-2's
  Example 4 feeds 6540 kg/h of H2SO4 to the same spar; that much acid cannot react with a 97.5 %
  spar and leave at most 1.7 % in the solids, so the patent's spar must have been less pure or
  its acid basis different: the balance follows the residues, not the acid rate.
- The kiln discharge V101 sends the solids and the free acid to the anhydrite and every gas and
  vapour to the process gas (ASSUMED); the dust carried with the gas is left out (L-3). The
  temperatures are SRC-2's: gas 478.15 K, solids 477.15 K, spar 673.15 K, acid 393.15 K.
- Size: SRC-2's 20 m x 2.5 m kiln, 157 m2 of shell for 55.3 t/d of HF, 2.84 m2 per t/d; SRC-1
  gives 5-10 m2 per t/d for a kiln without a pre-reactor and 2.5-3 with spar calcination, so the
  patent's zoned kiln with hot spar sits at the calcination end (consistent with its claimed 30 %
  more capacity).

### D-007 Gas purification, the acid loop and the distillation

- T201 (pre-purification) takes all the acid and 98 % of the water out of the kiln gas and
  dissolves 3 % of the HF in the hot acid (ASSUMED); the acid returns to the kiln through V-102.
  The gas leaves at 363.15 K (SRC-1: below 100 C), the acid at 338.15 K (ASSUMED).
- T301 (final scrubber) recovers 99 % of the HF of the condenser vent and the low boilers into
  the fresh acid (ASSUMED; SRC-1: most of the HF is recovered), which then feeds T201 (SRC-1).
- Oleum keeps the feed acid's water constant (SRC-1, reaction (9)): the design specification
  `oleum` sets its free SO3 (S31, 633.2 kg/h) for 3.0 wt% water in the feed acid S3 (ASSUMED,
  95 % H2SO4 with 2.3 % dissolved HF, the top of SRC-1's 90-95 %). The oleum's H2SO4 part is
  counted with the fresh acid (L-3). Two recycles are torn: S3 (feed acid) and S21 (final
  scrubber acid); both converged in 3 iterations with the specifications.
- E201 condenses 98.5 % of the HF with the water, half of the SO2 and some SiF4 and CO2 against
  brine at 258 K (ASSUMED splits). C301 sends SO2, SiF4 and CO2 to the top with 2 % of the HF;
  C302 sends 97 % of its HF and 1 % of its water to the top as product, the rest back to the feed
  acid (ASSUMED splits). The product S17 is 99.997 wt% HF with 29 ppm water. The columns are
  splits, not stage models (L-2).

### D-008 Co-products, absorbers and neutralisation

- R401 absorbs the SiF4 in water (3 SiF4 + 2 H2O -> 2 H2SiF6 + SiO2, balanced here; SRC-1: the
  water absorption of SiF4 makes aqueous H2SiF6), conversion 0.9995 (ASSUMED). 200 kg/h of water
  (ASSUMED) give 25.0 wt% H2SiF6 (SRC-1, 6.4.4: 25-35 %) with 14.4 kg/h of precipitated silica,
  which stays in the product acid here (L-3).
- R402 scrubs 99.9 % of the SO2 with 50 wt% caustic at 2.2 mol NaOH per mol SO2 (ASSUMED); the
  CO2 passes (SRC-1, 6.4.7). The SO2 slip is 0.024 g per kg of HF, inside SRC-1's 0.001-0.065
  kg/t with alkaline scrubbing.
- R501 neutralises the anhydrite's free acid with 1.05 mol CaO per mol (49.9 kg/h, ASSUMED); the
  BREF names lime for the anhydrite and SRC-2 says the free acid otherwise needs lime.
- The anhydrite S9 is 3.63 kg per kg of HF (SRC-1, Table 6.8: about 3.7 t/t).

### D-009 Energy

| stream | kW | from |
|---|---|---|
| Q1 spar preheater (fired, absorbed) | 478.1 | 4800 kg/h x 0.956 kJ/(kg K) x 375 K (CaF2, SRC-4) |
| Q2 kiln (fired, absorbed) | 899.3 | R1 extent 57.623 kmol/h x 59 MJ/kmol (SRC-1) = 944.4 kW; + solids to 477.15 K, 336.9 kW (CaSO4 cp, SRC-4); + gas to 478.15 K with the feed acid's 191.5 kg/h water and 147.4 kg/h HF evaporated, 354.7 kW (SRC-4); - spar from 673.15 K, 478.1 kW; - feed acid from 393.15 K, 258.5 kW |
| P1 auxiliary power | 518.6 | 225 kWh/t x 2.3048 t/h, the middle of SRC-1's 150-300 kWh/t |
| Q3 pre-purification cooler (CW) | 204.2 | gas 478.15 to 363.15 K with 247.1 kg/h of water condensed (290.8 kW) less the scrubber acid warmed by 40 K (86.6 kW) |
| Q4 HF condensers (brine) | 383.6 | gas 363.15 to 293.15 K, 2424.5 kg/h HF condensed at 376.0 kJ/kg (253.2 kW), subcooled to 268.15 K, water and SO2 condensed |
| Q5, Q6 low-boiler column | 25.7 each | boil-up 10 % of the feed (ASSUMED) x 376.0 kJ/kg |
| Q7, Q8 high-boiler column | 384.1 each | 0.6 GJ per t of HF (SRC-1, 6.2.4); boil-up 3678 kg/h, reflux ratio 0.60 |

Checks: the fired heat absorbed is 1377.4 kW, 2.15 GJ per t of HF. SRC-2's Example 4 burns at
most 189 m3/h of natural gas in the kiln, 1880 kW at 35.81 MJ/m3 (methane's lower heating value
from the SRC-4 formation enthalpies at 0 C and 101.325 kPa, natural gas taken as methane,
ASSUMED), so the kiln's absorbed 899 kW is 48 % of its fuel; the rest leaves with the flue gas
at up to 400 C (SRC-1, 6.4.2) and through the shell. SRC-1's BAT fuel for new AHF plants, 4-5
GJ/t, gives 43-54 % for the plant's 2.15 GJ/t. The LCI counts the heat absorbed; the furnace
efficiency is in the background (lca/mappings.yaml). The formation enthalpies of SRC-4 give R1
62.1 kJ/mol against the BREF's 59. The hydration heat of the oleum (HYD, 191.5 kW) warms the
feed acid from 338 to 393 K (141 kW at an ASSUMED 1.45 kJ/(kg K)); the rest and the heats of
absorption and dilution are left out (L-2). Refrigeration is 793.4 kW, 1.24 GJ/t, below SRC-1's
2-3 GJ/t: the BREF's figure includes the HF scrubber's quench, product and storage cooling and
the dilution to aqueous grades, which are not modelled. Steam is 409.8 kW, 0.30 kg of 450 kPa
steam per kg of HF (SRC-1: 0.15-0.8). `cheme assess lca` reports R102, R401, R402 and R501 as
exchanging heat without a utility (cheme.boundary-utility-unassigned): their small heats are not
balanced (L-2).

### D-010 Auxiliaries not in the flowsheet

The effluent treatment's lime and coagulants (SRC-1, 6.4.9) and the cleaning of the sulfur
traps are not inventoried: the BREF gives no amounts. They are part of the effluent's treatment
outside the boundary (D-011).

### D-011 LCA: boundary, allocation, mappings, gaps

- Gate-to-gate foreground per kg of AHF, written by `cheme assess lca --write`; boundary key
  cradle-to-gate so that the purchased inputs stay open gaps (as other entries).
- Allocation `none` (agent proposal, for the LCA practitioner to confirm): the anhydrite goes to
  inert landfill, as most excess anhydrite does (SRC-1, 6.4.3), and the fluorosilicic acid leaves
  burden-free as a by-product. A mass allocation would put most of the burden on the anhydrite,
  which no source supports; no prices are sourced.
- Linked: sulfuric acid to sulfuric-acid-1, quicklime to lime-1, caustic to chlor-alkali-1, the
  oleum's SO3 to the shared sulfur-trioxide entry, water, fired heat (heat from natural gas,
  counted as heat absorbed), steam heat, inert landfill and waste water to shared entries.
- Gaps: fluorspar (no library producer, no shared entry), refrigeration, electricity in
  `cheme assess lca` (the Atlas build links it through the shared entry). Spar and anhydrite dust
  and fluoride traces are excluded (emission_exclusions; SRC-1 Tables 6.5 and 6.6 give 0.01-0.1
  and 0.002-0.015 kg/t).
- CO2 of the spar's carbonate and fatty acids, 15.0 g per kg, is booked fossil (L-3).
- Downstream: aluminium-1 buys aluminium fluoride, which is made from HF; that link is a later
  change of aluminium-1 (an AlF3 entry), not made here.

### D-012 Hazards (reasoned; no HAZOP at this stage)

- **Hydrogen fluoride**: acutely toxic by inhalation and skin contact, corrosive, boils at
  19.5 C (SRC-1, 6.2.7). The whole plant is under suction (SRC-1, 6.2.3); AHF is stored below
  15 C with vent condensers; the liquid velocity in carbon-steel lines is kept low to keep the
  FeF2 layer (SRC-1). Release scenarios (line or tank failure, the condensers losing brine) are
  for the HAZOP.
- **Kiln**: corrosion and encrustation of the hot shell, which zoned firing reduces (SRC-2); air
  ingress raises the waste gas (SRC-1); burner management of nine combustion chambers.
- **Oleum and SO3**: fuming, violently reacting with water; the hydration in V-102 is
  exothermic (D-009).
- **SO2 and SiF4** in the low boilers and tail gas; **caustic** in the scrubber.
- **Refrigeration**: loss of brine at E201 sends HF to the final scrubber, which then carries
  the plant's HF.
- No reactive-chemistry screening applies to the continuous endothermic kiln (D-003).

## Core features used

- `cheme process propagate --fill`: five conversion reactors, eight component separators, two
  tears with Broyden, two design specifications (core ADR 0070).
- `cheme validate`: mass, component and element balances of every step and block.
- `cheme process build`: BFD and PFD.
- `cheme assess lca --write`: the gate-to-gate inventory and dataset.

## Core limits (L-n)

| id | limit | effect here |
|---|---|---|
| L-1 | No kinetic model of a gas-solid-liquid reaction in a rotary kiln: the conversion reactor applies given conversions; core's furnace model (`cheme process furnace`) covers lime calcination only. | The kiln's conversions are set to the patent's residues (D-006), not predicted from the wall temperature profile or the residence time; the zones are not modelled. |
| L-2 | No property package for HF (vapour association, HF-H2O azeotrope), sulfuric acid or solids: no flash, no column model, no absorption model; a conversion step's duty needs liquid heat capacities core does not have for solids. | Scrubbers, condenser and columns are ASSUMED component splits; every duty is a hand balance with SRC-4 values (D-009); heats of absorption, dilution and HF association are left out. |
| L-3 | Lumped spar and products: one stand-in each for the oxides and the fatty acids, no MgCO3, BaSO4, sulfides or phosphates, no dust; the oleum is its free SO3; the silica stays in the fluorosilicic acid. | Minor SO2, H2S and sulfur and the dust emissions are missing; the fatty acids' biogenic CO2 is booked fossil (D-005, D-011). |
| L-4 | The LCA background for fluorspar and refrigeration does not exist in the library. | Two gaps; the Atlas dataset is preliminary (ADR 0026). |

## Open items

- A vapour-liquid model for HF-H2O and the low boilers, to replace the splits (L-2).
- Kiln residence time and wall heat flux against the zone temperatures of SRC-2 (L-1).
- A fluorspar producer for the LCI, and the downstream aluminium fluoride entry that would let
  aluminium-1 close its fluorine balance.
