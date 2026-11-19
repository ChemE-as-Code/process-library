# Design decisions: sodium-chlorate-1

Sodium chlorate by electrolysis of brine in undivided cells, crystallisation and drying, with
hydrogen as a co-product. Concept stage, issue ChemE-as-Code/process-library#512. Every number
below is either taken from a source in the register (with its locator), calculated by core from
the files, or marked ASSUMED. Nothing is copied from the sources: no tables, figures or text,
only single facts in our own words.

## Source register

| id | source | access | used for |
|---|---|---|---|
| SRC-1 | European Commission JRC (2007), *Reference Document on Best Available Techniques for the Manufacture of Large Volume Inorganic Chemicals - Solids and Others industry* (LVIC-S BREF), section 7.13 Sodium chlorate, <https://eippcb.jrc.ec.europa.eu/sites/default/files/2019-11/lvic-s_bref_0907.pdf> | open PDF, read (text extracted), 2026-11-19 | the route and its steps (7.13.1.1, 7.13.2.1-7.13.2.6); cells at 60-80 C, pH 6.0-6.5, titanium anodes with noble-metal coating, steel cathodes (7.13.2.3); consumptions and emissions per t (Table 7.79); 1.0-3.0 kA/m2, 2.6-3.6 V, 4700-5200 and 100-500 kWh/t (Table 7.80); auxiliaries (Table 7.81); 60 kg H2 per t (7.13.3.3); 2.75-3.6 V, current efficiency 95 %, 2-2.5 % O2 in H2, 3-5 g/L dichromate (7.13.4.1); heat about 50 % of the energy, used in the crystallizer (7.13.4.3); fluid-bed dryer with air at about 150 C (7.13.2.5); 687 kt/a on 15 Western European sites in 2002 (Table 7.78) |
| SRC-2 | Eka Nobel AB (1995), *Process for the production of alkali metal chlorate*, US 5 419 818 A, <https://patents.google.com/patent/US5419818A/en> | open, read (description), 2026-11-19 | the cyclic process (cells, reaction vessels, crystallizer, mother liquor back to the electrolyte preparation, condensate to the salt); electrolyte 100-140 g/L NaCl and 500-650 g/L NaClO3, preferably 110-125 and 550-580; 75-200 m3 of electrolyte through the cells per t; cells at 60-80 C; pH 5.5-6.5 at the cells, alkaline in the crystallizer; the mother liquor saturated in chlorate with much NaCl. The patent's own subject (a separator cell making acid and alkali in the loop) is not designed (D-001) |
| SRC-3 | Spasojevic, M.; Markovic, D.; Trisovic, T.; Spasojevic, M. (2018), *Mathematical model of the catalytic effect of chromium(VI) on hypochlorite disproportionation in chlorate electrolysis*, J. Electrochem. Soc. 165, E8-E19, doi:10.1149/2.0291802jes; peer-reviewed version in the university repository (CC BY-NC-ND 4.0: facts only, nothing reproduced) | open, read (text extracted), 2026-11-19 | the reaction scheme (reactions 1-8: anodic chlorine, hydrolysis, HOCl dissociation with K3 = 2e-7 mol/L at 70 C, disproportionation 2 HOCl + OCl- -> ClO3- + 2 Cl- + 2 H+, oxygen from hypochlorite); the rate -dC/dt = k1 C(HOCl)^2 C(OCl-) with k1 = 7.19 mol-2 dm6 s-1 at 70 C in 526 g/L NaClO3 and 113 g/L NaCl (quoting Wanngard and Wildlock; not read here); fastest at pH 6.1-6.5 and 70-90 C; current efficiency 94-96 %, limited by oxygen; world production 3.6 Mt in 2015 |
| SRC-4 | PubChem (CIDs 516902, 25408) and ChEBI via EBI OLS (65242, 39483) | open, 2026-11-19 | identity of sodium chlorate (registry entry); sodium dichromate is named in the LCA only, not in the registry (its atomic weights have no chromium) |
| SRC-5 | `chemicals` 1.5.2 and `thermo` 0.6.1 Python packages (C. Bell et al.) | queried, 2026-11-19 | single values (library ADR 0037): formation enthalpies NaCl(s) -411.2 and NaClO3(s) -365.8 kJ/mol (method CRC: the CRC Handbook's tables as the package bundles them, the handbook not read here), H2O(l) -285.825 kJ/mol (method ATCT_L, Active Thermochemical Tables); normal boiling points of water, hydrogen and oxygen (default method); heat of vaporisation of water 2382 kJ/kg at 323.15 K and 2308 kJ/kg at 353.15 K (thermo, method HEOS_FIT, a fit to the IAPWS-95 formulation). These are facts with their source, not open data |

Sources looked for and not found or not read: an open solubility diagram of NaCl-NaClO3-H2O
at the crystallizer's temperature, an open heat of solution of NaClO3, an open density of the
chlorate liquor, and an open formation enthalpy of the active chlorine species. Each is an
assumption below (L-2, L-5).

## Decisions

### D-001 Route

**Chosen: electrolysis of purified NaCl brine in undivided cells with sodium dichromate, chlorate
formed in the cells and reaction tanks, evaporative crystallisation, centrifuging and drying,
mother liquor recycled (SRC-1, SRC-2).** It is the process by which sodium chlorate is made: the
BREF describes no other, and the patent and the paper describe the same loop.

Recorded and rejected:

- *Chromate-free operation.* The BREF (7.13.4.1) says no alternative to dichromate had been found
  in spite of extensive research, and its consumption figures are those of chromate plants. The
  library has no open source with the current efficiency and voltage of a chromate-free cell, so
  that variant would rest on numbers we do not have. The dichromate stays, with its make-up and
  its sludge recorded (D-010, D-011).
- *Selling the liquor instead of crystals.* The BREF names chlorate solution as a product, but
  the issue asks for the crystal and the crystallizer is half of the case; the liquor would also
  carry the dichromate to the customer.
- *The integrated separator cell of SRC-2,* which makes the loop's hydrochloric acid and caustic
  soda in a diaphragm cell on a partial flow. It removes the purchased HCl and NaOH but adds a
  second cell type and a dialysis gas; its own current efficiency and voltage are not given as
  plant figures. The purchased acid and caustic stay consumables (D-010).
- *Thermal or chemical routes* (chlorine into hot caustic soda, 3 Cl2 + 6 NaOH -> NaClO3 +
  5 NaCl + 3 H2O): five sixths of the chlorine end as salt; no source treats it as an industrial
  route for sodium chlorate.
- *Potassium chlorate* in the same plant (SRC-1, SRC-2): out of scope.

### D-002 Capacity and basis

50 000 t/a of sodium chlorate crystal, 6250 kg/h in 8000 h (ASSUMED). The BREF's 687 kt/a on 15
Western European sites in 2002 (Table 7.78) makes about 46 kt/a a site, so the basis is of a
real plant's order. It is a normalisation basis for the inventory, not a market claim. The
product stream S20 is the dried crystal with what its cake liquor leaves on drying: 6350.7 kg/h,
98.4 wt% crystal, 1.2 wt% dissolved chlorate dried on, 0.28 wt% NaCl, 0.1 wt% water. The
functional unit is 1 kg of S20.

### D-003 Continuous plant, one design case

The process is continuous (SRC-1, 7.13.2), so no recipe and no reactor-hazard screening of a
batch apply: the reaction tanks are continuous, isothermal, at 70 C, with a liquid that is
mostly water and salts and no thermal runaway mechanism of the kind core screens (the
disproportionation is the plant's normal duty). The hazards are reasoned in D-012.

### D-004 Components and the liquor's basis

The liquor is written as neutral salts in water (NaCl, NaClO3, and NaOCl for the active chlorine,
hypochlorous acid and hypochlorite together), an inventory basis, not a speciation (L-1). The
crystal is a separate solid component NaClO3_s (core ADR 0025). The dichromate is not a
component: at 3-5 g/L it circulates, and its make-up is a consumable (D-010).

### D-005 The loop: salt, liquor composition and circulation

- Solid salt (pure NaCl, ASSUMED; its impurities and their precipitation left out, L-3) is
  dissolved in V-101 in the mother liquor and the crystallizer's condensate (SRC-2: the
  condensate prepares the electrolyte), with make-up water.
- The strong liquor joins the circulating electrolyte; the cell feed S6 is the tear stream.
- Two design specifications (core ADR 0070) close the loop: the salt S1 for 6250 kg/h of crystal
  in S20, and the process water S2 for 0.40357 mass fraction NaClO3 in S6, which is 565 g/L
  (the middle of SRC-2's preferred 550-580 g/L) at a liquor density of 1.40 kg/L (ASSUMED, no
  open density read). The salt comes out at 3492.46 kg/h (0.550 kg/kg, BREF 0.550-0.580) and the
  water at 3459.36 kg/h (0.545 m3/t, BREF 0.4-2.7).
- The NaCl in the cell feed follows from the cells' per-pass conversion (D-006): 0.0865 mass
  fraction, 121 g/L at the same density, inside SRC-2's 110-125 g/L.
- The circulation through the cells is 859 t/h, 614 m3/h at 1.40 kg/L or 98 m3 per t of chlorate,
  inside SRC-2's 75-200 m3/t. The split SP201 sends 11.80 % of it to the crystallizer (ASSUMED,
  chosen so that 15 % of the side stream's chlorate makes the plant's crystal at the loop's
  composition).
- Temperatures: the loop at 343.15 K (70 C, SRC-1 60-80 C, the temperature of SRC-3's rate
  constant).

### D-006 The cells (process/cells.yaml, cheme process cell)

- Overall reaction CHLORATE, NaCl + 3 H2O -> NaClO3 + 3 H2, 6 electrons (SRC-1). The anode's
  half-reaction is written for the net change at the anode and in the liquor (chloride to
  chlorate, via chlorine, hypochlorous acid and hypochlorite), so that the electrons and the
  products per extent are the plant's; the bulk chemistry is not an electrode reaction.
- Current efficiency 0.95, given (SRC-1, 7.13.4.1; SRC-3: 94-96 %).
- Oxygen: 4.5 % of the current to WATER_SPLIT (ASSUMED), which gives 2.2 mol% O2 in the cell gas,
  inside SRC-1's 2-2.5 %. The remaining 0.5 % (cathodic reduction of hypochlorite and chlorate,
  which dichromate suppresses, SRC-1) forms nothing and becomes heat.
- 3.0 V (ASSUMED inside SRC-1's 2.75-3.6 V and 2.6-3.6 V), 2.5 kA/m2 (ASSUMED inside 1.0-3.0
  kA/m2), 400 cells of 10.062 m2 in series as one DC load (a simplification; the split into cell
  boxes and rectifier circuits does not change the balance), 25.1557 kA: the current that forms
  the flowsheet's chlorate, 59.4442 kmol/h.
- Core's Faraday balance: 30 186.8 kW DC, 15 579.2 kW into the reaction enthalpy, 14 607.6 kW of
  heat (48 % of the power; SRC-1 7.13.4.3: about 50 %), U_tn 1.5596 V, 4.771 kWh/kg NaClO3 formed,
  376.55 kg/h H2 (59.5 kg/t; SRC-1 7.13.3.3: 60 kg/t).
- In the flowsheet the cells EL201 form the active chlorine (HYPO, NaCl + H2O -> NaOCl + H2,
  a conversion of 0.14683 of the cell feed's NaCl per pass) and the reaction tanks R201 turn it
  into chlorate (CHEM, 3 NaOCl -> NaClO3 + 2 NaCl) and, for the cell's oxygen, into oxygen and
  chloride (OXY, 2 NaOCl -> 2 NaCl + O2). Three HYPO and one CHEM make one CHLORATE; two HYPO
  and one OXY make one WATER_SPLIT. With the conversions of CHEM and OXY in the ratio
  0.95 : 0.045, the extents (CHEM 59.444, OXY 4.2235 kmol/h) equal the cell's (CHLORATE 59.444,
  WATER_SPLIT 4.2237 kmol/h): the flowsheet and the cell model carry the same chemistry. The
  anodic oxygen is booked in the tanks (L-1).

### D-007 The reaction tanks (sized from the kinetics of SRC-3)

- The tanks R201 convert 0.87988 of the active chlorine entering them (CHEM 0.84009, OXY
  0.039794), ASSUMED so that 3 g/L of active chlorine as NaOCl leaves them (S9: 0.00221 mass
  fraction, 3.09 g/L at 1.40 kg/L, 0.0416 mol/L).
- Volume: the third-order rate -dC/dt = k1 C(HOCl)^2 C(OCl-) with k1 = 7.19 mol-2 dm6 s-1 at
  70 C (SRC-3), the HOCl share at pH 6.4 from K3 = 2e-7 mol/L (SRC-3): x = 10^-6.4 / (10^-6.4 +
  2e-7) = 0.666, so k1 x^2 (1 - x) = 1.065 mol-2 dm6 s-1. As one stirred volume at the outlet's
  0.0416 mol/L the rate is 7.65e-5 mol/(L s); the chlorate formed, 59.444 kmol/h, uses
  3 x 59.444 kmol/h = 49.54 mol/s of active chlorine, so the volume is 49.54 / 7.65e-5 L =
  648 m3, 1.06 h at 614 m3/h. This uses the uncatalysed constant; dichromate speeds the reaction
  (SRC-3), so the volume is an upper bound for the kinetics, and part of the chlorate forms in
  the cells' own liquor. The pH 6.4 is inside the optimum 6.1-6.5 of SRC-3. tests/ recompute it.
- No heat of reaction is given to HYPO, CHEM and OXY (no open enthalpy of the active chlorine
  read, L-2): the cell's energy balance carries the whole loop's heat. `cheme validate` reports
  R201 as exchanging heat without a utility (cheme.boundary-utility-unassigned): its heat is in
  the cell's Q2.

### D-008 Gas, crystallizer, centrifuge, dryer, hydrogen

- V201 takes the hydrogen and oxygen off the liquor completely (component separator); the gas's
  water vapour, its chlorine traces and the caustic scrubber the BREF requires are not modelled
  (L-4).
- X301, core's crystallizer on an imposed yield (L-5): 15 % of the side stream's water evaporated
  (ASSUMED) and 15 % of its chlorate crystallised, i.e. the mother liquor leaves with the feed's
  chlorate-to-water ratio, as for a liquor saturated in chlorate at the crystallizer (SRC-2: the
  mother liquor is saturated in chlorate). NaCl and the active chlorine are spectators. At 323.15
  K under vacuum (ASSUMED; SRC-1: concentration with heat and vacuum). Centrifuge: all the crystal
  to the cake with 3 kg of liquor per 100 kg of crystal (ASSUMED). The product is not washed
  (L-5).
- SP301 bleeds 3e-5 of the mother liquor to effluent (ASSUMED): 2.6 kg/h, 0.17 kg NaClO3 per t
  of crystal, inside SRC-1's 10-300 g/t to water.
- DR401, core's dryer: water down to 0.1 wt% (ASSUMED) at 353.15 K; air at about 150 C in a
  fluidised bed (SRC-1).
- SP501 sends 69 % of the cell gas to users (ASSUMED, the middle of SRC-1's 53-85 % utilisation),
  so 18.4 kg H2 per t is vented (SRC-1: 9-28 kg/t).

### D-009 Energy

| stream | kW | from |
|---|---|---|
| P2 DC power to the cells | 30 186.84 | cheme process cell |
| P1 AC to the rectifiers | 31 120.45 | P2 / 0.97 (rectifier efficiency ASSUMED); 4919 AC kWh per t NaClO3 formed, inside SRC-1's 4700-5200 |
| Q1 rectifier losses | 933.61 | P1 - P2 |
| P3 auxiliaries | 1 875.0 | 300 kWh/t x 6.25 t/h, the middle of SRC-1's 100-500 kWh/t |
| Q2 cell heat | 14 607.62 | cheme process cell |
| Q3 to the crystallizer | 3 437.31 | core's crystallizer energy balance (feed 343.15 K, liquor cp 2.9 kJ/(kg K) ASSUMED, latent heat SRC-5, heat of crystallization left out, L-2), written by propagate |
| Q4 cell heat to cooling water | 11 170.31 | Q2 - Q3 |
| Q5 crystallizer condenser | 5 069.94 | 7662.37 kg/h x 2382 kJ/kg (SRC-5) |
| Q6 dryer steam | 218.56 | core's dryer model (cake cp 1.0 kJ/(kg K) and efficiency 0.5 ASSUMED, latent heat SRC-5) |

Total electricity 5.196 kWh per kg of product (SRC-1: 5.0-6.0). The crystallizer is heated by
the cells' heat through a hot-water loop (SRC-1 7.13.4.3), so the plant needs steam only for the
dryer (0.034 kWh/kg; SRC-1 lists 100-1000 kg steam per t, which also covers ejectors and plants
without the heat recovery; the vacuum system's motive steam is not modelled). Cooling water and
LP steam at 298/308 K and 450 kPa(a) (ASSUMED).

### D-010 Auxiliary chemicals (LCA consumables)

The flowsheet does not carry the BREF's auxiliary chemicals; each is an `lca/lca.yaml`
consumable per year at the middle of its range in SRC-1 (Tables 7.79 and 7.81), per t of
product: NaOH 22.5 kg (as 45 kg of 50 wt% solution), HCl 22.5 kg (as 68.2 kg of 33 wt% acid),
soda ash 1.02 kg, sodium dichromate 0.08 kg, H2O2 2 kg (as 4 kg of 50 wt% solution), nitrogen
3.2 kg; all ASSUMED to be per t of chlorate and on the pure substance. The acid and caustic
neutralise each other in the loop to NaCl and water, which the flowsheet does not see (L-3);
they add about 10 % to the inventory's input mass, so `cheme assess lca` reports the
inventory's mass balance as open by that amount (cheme.lci-mass-balance, a recorded warning).

### D-011 LCA: boundary, allocation, mappings, gaps

- Preliminary gate-to-gate inventory per kg of S20, cradle-to-gate boundary key so that the
  purchased inputs stay gaps.
- Allocation between the crystal and the hydrogen used (S21): mass of the contained products,
  6350.71 : 259.83 kg/h, shares 0.9607 / 0.0393, as chlor-alkali-1 allocates its hydrogen. The
  conservative bound is all burdens to the chlorate. Agent proposal, for the LCA practitioner to
  confirm.
- Linked (lca/mappings.yaml): salt to the shared sodium-chloride entry, process water to the
  shared water entry, LP steam as heat; caustic soda to chlor-alkali-1, hydrochloric acid to
  hydrogen-chloride-1, soda ash to soda-ash-1, hydrogen peroxide to hydrogen-peroxide-1, nitrogen
  to asu-1. Cooling water links to the library's cooling tower by default.
- Gaps: electricity (the dominant exchange, about 5.2 kWh/kg; the grid of an undecided country),
  sodium dichromate (no library producer), the bleed's treatment. No total is shown while every
  contribution of a category is a gap.
- Not inventoried: the chromium-bearing and chromium-free sludges (SRC-1 Table 7.79: 0.1-1 and
  0.05-2 kg/t), chlorine traces (0.05-1 g/t) and chlorate dust (0.3-10 g/t) (emission
  exclusions in lca.yaml), the construction.
- This entry is the library producer kraft-pulp-1's chlorine dioxide gap names: sodium chlorate
  reduced to ClO2. Linking it there is kraft-pulp-1's own change (a ClO2 generator is not part
  of this entry).

### D-012 Hazards (reasoned; no HAZOP at this stage)

- **Hydrogen with oxygen.** The cell gas is hydrogen with 2.2 mol% oxygen; more oxygen (a higher
  pH, impurities, loss of dichromate) moves it toward the flammable range. SRC-1 says the oxygen
  content must be controlled for safety and the gas purged with nitrogen (Table 7.81); an oxygen
  analyser with a trip of the rectifiers and a nitrogen purge are expected at the basic stage.
- **Hydrogen in the building and the vent.** 31 % of the hydrogen is vented: the vent's height
  and dispersion, and hydrogen in the cell room, are area-classification items.
- **Chlorine.** A drop of the pH releases chlorine from the liquor (SRC-2: acidification needs
  thorough mixing to avoid chlorine and chlorine dioxide in local acid regions); the hydrogen and
  the tank vents go through a caustic scrubber (SRC-1).
- **Sodium chlorate as an oxidiser.** Dry chlorate with organic matter (dust, oil, clothing) burns
  vigorously and can explode (SRC-1, 7.13.1.2); the dryer, conveyors and store need dust control
  and separation from combustibles.
- **Hexavalent chromium.** The dichromate is toxic; its losses and sludges are hazardous waste
  (SRC-1).
- **Electrical.** 1200 V DC and 25 kA on the cell line.

## Core features used

- `process/cells.yaml` and `cheme process cell` (core ADR 0023) for the Faraday, charge and energy
  balance.
- Conversion reactors with element-balanced reactions; component separator (`recovery:`, ADR
  0070); splitters; the loop torn at S6 with Wegstein/Broyden and two design specifications (ADRs
  0060, 0070).
- Core's crystallizer with spectators, evaporation, centrifuge and energy balance (ADRs 0025,
  0056), the crystallizer's duty written to Q3 through `energy_port`; core's dryer (ADR 0057).
- `cheme assess lca` with consumables per year and shares allocation.

## Core limits (L-n)

- **L-1** No electrolyte speciation: the liquor is neutral salts, the active chlorine one lumped
  component; the pH and the HOCl/OCl- split enter only the hand sizing of D-007. A cell's
  flowsheet step must list the cell's reaction (`cheme.cell-flowsheet` warning), but a
  conversion reactor cannot hold the cell's current-fraction ratio on a recirculating feed, so the
  step lists HYPO and the tanks CHEM and OXY, whose extents equal the cell's (D-006).
- **L-2** No heats of solution or dilution and no formation enthalpy of dissolved species: the
  cell's heat of reaction is on solids (CRC) and liquid water, the crystallizer's heat of
  crystallization is left out, and HYPO, CHEM and OXY carry none.
- **L-3** The salt's impurities, the brine purification by precipitation and the pH chemicals
  are not streams; they are consumables (D-010) and their net NaCl and water stay out of the
  balance.
- **L-4** No gas-liquid equilibrium of the cell gas: its water vapour and chlorine traces, the
  scrubber and the hydrogen's cooling are not modelled.
- **L-5** No solubility of NaClO3 in the chloride liquor (no open data read, and core's
  crystallizer takes one solute's solubility): the crystallizer's yield is imposed, its
  temperature effect not predicted; no crystal wash.
- **L-6** The reaction-tank volume is a hand calculation (D-007): a `reactor: cstr` with the rate
  law would need liquid molar volumes of the dissolved salts, which are not sourced.

## Open items

- Sourced solubility data of NaClO3 in NaCl liquor (to replace the imposed yield), the liquor's
  density and heat capacity, a product specification and the wash.
- The dichromate's library producer, the grid electricity of a chosen site.
- A HAZOP and the P&IDs (basic stage).
