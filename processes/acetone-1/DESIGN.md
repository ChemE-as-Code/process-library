# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#132. Run of 2026-10-28 (concept: design basis to
balanced PFD and a preliminary gate-to-gate LCI). Starting library commit 11d50ef,
cheme-as-code 0.8.0 (pyDEXPI 2.1.0, Python 3.15). Designed independently from open sources;
no published flowsheet or stream table was copied.

## Route and boundary memo

**Route.** Cumene hydroperoxide (Hock) process: cumene + O2 -> cumene hydroperoxide (CHP);
CHP -> phenol + acetone over an acid. It is the route most used worldwide and the one
predominant in Europe (LVOC BREF 8.2.1); acetone is a fixed co-product (about 0.62 t per t
phenol). Rejected for this case: acetone from isopropanol dehydrogenation (issue #132 proposes
it as a separate case; it has no phenol co-product and needs its own boundary) and the
phenol routes without acetone (toluene via benzoic acid, benzene direct oxidation, coal tar;
LVOC BREF 8.2.1: not, or no longer, commercial in Europe).

**Boundary.** From fresh cumene, air, hydrogen, sulfuric acid, caustic soda and wash water at
the battery limit to acetone, phenol, tar, aqueous effluent and vents at the battery limit.
Outside: cumene production (benzene alkylation; a boundary feed, D-001), hydrogen production
(library `hydrogen-1` could supply it), caustic (`chlor-alkali-1`), sulfuric acid
(`sulfuric-acid-1`), storage, the site boilers, cooling tower, waste water treatment and the
furnace that burns the tar. Utilities cross the boundary as energy streams.

```
 cumene ─┐   ┌────────── recycle cumene (CONC, A101, HYD) ─────────────┐
 air ────┴─> OXI: compressor, oxidisers, spent-air recovery ─> vent    │
              │ oxidate 25 % CHP                                       │
              v                                                        │
            CONC: vacuum flash to 80 % CHP ─> cumene ──────────────────┤
              │                                                        │
 H2SO4, NaOH, water ─> CLV: cleavage, neutraliser, decanter ─> brine   │
              │ organic                                                │
              v                                                        │
            FRAC: crude acetone, acetone, cumene/AMS, phenol columns   │
              ├─> acetone   ├─> phenol   ├─> tar   ├─> water           │
              └─> cumene/AMS ─> HYD: Pd hydrogenation (+H2) ─> cumene ─┘
```

## Source register

| # | source | locator | read | reuse | used for |
|---|---|---|---|---|---|
| S1 | EU JRC (2017) LVOC BREF, EUR 28882 EN, [PDF](https://bureau-industrial-transformation.jrc.ec.europa.eu/sites/default/files/2019-11/JRC109279_LVOC_Bref.pdf) | ch. 8 Phenol, pp. 395-411: 8.2.2.1 (oxidation 80-120 C, atmospheric to ~700 kPa, 4-20 h, DMBA/ACP/methanol side products, dry oxidation), 8.2.2.2 (CHP 17-30 % to 65-85 %, vacuum), 8.2.2.3 (sulfuric acid, two-step cleavage, neutralisation), 8.2.2.4 (fixed-bed AMS hydrogenation, excess H2 recycled), 8.3.1.1 (spent air 1 000-1 500 Nm3/t, 35 mg C/Nm3 after adsorbers, methane 100-400 mg/Nm3), 8.3.1.3-4 (vents 10-15 Nm3/t; H2 vent 0.8-1.2 Nm3/t), 8.3.1.6 (fugitive 0.02-0.06 kg/t), 8.3.2.2 (phenol 1-2 % in neutralisation effluent), 8.3.3 (cumene 1.31-1.38 t/t), Table 8.5 (steam 1.9 t/t at 18 bar plus 0.4-0.9 t/t at 5 bar, 190 kWh/t; second data set 6.32 t/t, 326 kWh/t), 8.3.5 (water 1-4 t/t), 8.3.6 (tar 20-200 kg/t, burned or cracked) | full chapter read | EU Commission reuse policy (Decision 2011/833/EU): reuse with attribution; facts only used, nothing copied | conditions, ranges, utilities, emissions |
| S2 | Speight (2002) Chemical Process and Design Handbook, Part 2, via skill `tech-petchem-styrene-and-phenol` | table "Phenol: 1.31 t cumene per t phenol, 0.616 t acetone" | skill summary only | fact | cross-check of yields |
| S3 | US 5,245,090 (1993), Two-stage cleavage of CHP | background and examples (search abstract: oxidation 110-115 C to 20-25 % CHP; cleavage fast, essentially complete, 70-90 C) | abstract/snippet, full text not audited | patent text: facts only | D-004, D-005 support |
| S4 | cheme chemistry thermo (chemicals/thermo bundled): ideal-gas dHf (CRC, ATcT, NIST WebBook) | per component | tool output | open data | reaction heats, LHV |
| S5 | Ullmann's: Acetone (doi 10.1002/14356007.a01_079.pub4), Phenol (Weber et al.) | not opened (licensed); cited by S1 | not read | - | lead only |

## D-001 Cumene is a boundary feed (2026-10-28)
Decision: no cumene unit in the boundary; pure cumene at 400 kPa(a), 313 K.
Reason: the case notes say so; the library may later model cumene from benzene and propylene.
Assumptions: pure cumene (the real feed carries up to 0.001 wt% benzene, S1 8.3.1.1).

## D-002 Capacity 200 kt/a phenol, 8000 h/a (2026-10-28)
Decision: 25 000 kg/h phenol; acetone (15 718 kg/h) follows. ASSUMED.
Reason: within the 185-680 kt/a of the EU plants listed in S1 Table 8.1; a mid-size train. No
client figure. The LCI is per kg and nearly independent of scale at this stage.

## D-003 Dry oxidation with air, 500 kPa(a), spent air 5 mol% O2 (2026-10-28)
Decision: oxidisers lumped as R101 (bubble columns in series); air compressed to 600 kPa(a);
dry air (Ar counted as N2, humidity ignored); spent air 5 mol% O2 on a dry, organics-free basis
and 2 mol% cumene vapour before recovery. ASSUMED within S1 8.2.2.1 (80-120 C, up to about
700 kPa; O2 kept low for safety, monitored, S1 8.2.2.1/8.3.1.1).
Check: air 37 279 Nm3/h, spent air 1 240 Nm3/t phenol, inside S1's 1 000-1 500 Nm3/t.

## D-004 Oxidation model: conversion with selectivities (2026-10-28)
Decision: conversion reactor; per kmol cumene converted 0.94 CHP, 0.05 DMBA, 0.01 acetophenone
(+ methanol); conversion per pass 0.2174, which gives 25 wt% CHP in the oxidate. ASSUMED.
Reason: no open kinetic data were read; the selectivities are chosen so that the overall
cumene use (1.330 t/t phenol) and tar (47 kg/t) fall inside S1's ranges (1.31-1.38 t/t;
20-200 kg/t). The CHP level is inside S1's 17-30 % and S3's 20-25 %. A sourced range check,
not a predictive model; organic acids, formic acid and methyl hydroperoxide are not modelled.

## D-005 Cleavage model (2026-10-28)
Decision: CHP fully cleaved (S3: fast and essentially complete); DMBA 75 % dehydrated to AMS,
25 % reacting with phenol to cumylphenol, the surrogate of all heavies (AMS dimers,
cumylphenols). Two-step cleavage lumped into R301. Acetone recycle for dilution and the water
added in the second step (S1 8.3.2.2) are not modelled. ASSUMED split.

## D-006 CHP concentration to 80 wt% (2026-10-28)
Decision: one lumped vacuum step E201 (pre-flash drum, flash column, vaporisers; S1 8.2.2.2)
concentrating to 80 wt% CHP (S1: 65-85 %). The recycled cumene is pure; methanol stays with
the concentrate. ASSUMED. Vacuum by liquid-ring/dry pumps (power), not steam ejectors (which
would add effluent, S1 8.3.2.2).

## D-007 Acid, caustic and wash water (2026-10-28)
Decision: 102 kg/h 98 wt% H2SO4 (about 0.2 wt% of the concentrate; S3 gives 0.01-5 wt%,
preferably 0.1-2 %), neutralised with stoichiometric 50 wt% NaOH; 1 000 kg/h wash water keeps
Na2SO4 near 11 wt% in the brine. ASSUMED. Neutralisation with sodium phenate or ion exchange
resins (S1 8.2.2.3) not modelled; caustic washing of the recycled cumene not modelled.

## D-008 Decanter, hydrogenation (2026-10-28)
Decision: the decanter brine carries all the salt, the acid/caustic/neutralisation/wash water,
1.5 wt% phenol (S1 8.3.2.2: 1-2 %) and 1.0 wt% acetone (ASSUMED). No phenol recovery unit in
the boundary (the effluent goes to site treatment with its phenol). AMS fully hydrogenated on
Pd (S1 8.2.2.4) with a hydrogen vent of 1 Nm3/t phenol (S1 8.3.1.4); excess hydrogen recycle
internal to R501, not drawn.

## D-009 Fractionation and products (2026-10-28)
Decision: four columns: C401 crude acetone (acetone, water, methanol overhead), C402 acetone
finishing (99.7 wt% acetone, 0.3 wt% water; bottoms water and methanol with 0.5 wt%
acetone), C403 cumene/AMS cut, C404 phenol (crude phenol and finishing lumped; phenol 100 %
in the model; tar with 5 wt% phenol). Sharp splits otherwise. ASSUMED. Aldehyde caustic
treatment, mesityl oxide, 2-methylbenzofuran and the phenol purification resins are not
modelled. Result: acetone 0.629 t/t phenol (S2: 0.616; the model has no acetone condensation
losses).

## D-010 Spent-air recovery (2026-10-28)
Decision: A101 lumps the condensers and activated carbon adsorbers; cumene recovered to the
oxidiser feed; residual VOC 35 mg C/Nm3 counted as cumene (S1 8.3.1.1, adsorber outlet
without a thermal oxidiser). No RTO modelled (open item I-04).

## D-011 Utilities from the BREF plant data (2026-10-28)
Decision: steam and power totals from S1 Table 8.5 (first data set): MP steam 1.9 t/t at 18
bar (25 228 kW at 1 912 kJ/kg latent heat), LP steam 0.65 t/t at 5 bar (midpoint of 0.4-0.9;
9 515 kW at 2 108 kJ/kg), power 190 kWh/t (4 750 kW). Air compressor 2 716 kW (isothermal
101.3 to 600 kPa(a), isothermal efficiency 0.75, ASSUMED); the rest of the power split
ASSUMED between the concentration (1 000 kW) and fractionation (1 034 kW) vacuum systems. Steam
split between the four columns ASSUMED. Cooling water: each condenser rejects its reboiler
duty (ASSUMED); oxidation, cleavage and hydrogenation heats from ideal-gas formation enthalpies
(S4; gas basis, screening), the compression heat into the oxidiser coolers; neutralisation
about 57 kJ per mol water (ASSUMED). Total 61 903 kW to cooling water against 63 607 kW in
(steam, power, reaction heats): an independent closure within 2.7 %.
Rejected: S1's second data set (6.32 t/t steam, 326 kWh/t), which is a less integrated plant;
the spread is the main uncertainty of the utility inventory.
Gated: an enthalpy balance by cheme needs a property package for the polar
cumene/CHP/phenol/acetone/water system (core #315; no package covers it, D-012).

## D-012 Property method: none qualified (2026-10-28)
`property_method` stays a placeholder. The benchmarked packages (air-pr-chemsep,
syngas-pr-vapor) do not cover these components; a polar activity-coefficient benchmark is
open work under core #315 (issue #132 comment). No `props --fill`, no `simulate`: temperatures
and pressures on the streams are assumed, the separators are specified. Phenol-water,
acetone-water and the cumene/phenol/AMS azeotropes need NRTL/UNIQUAC with sourced binary
parameters before any column is designed.

## D-013 Lists at concept (2026-10-28)
One equipment tag per PFD step; trains, spares, reboilers and condensers are not split out.
No line list yet (no P&IDs). The template DEXPI sheet was not created; no P&ID in scope.

## D-014 LCI: foreground only, mass allocation (2026-10-28)
Decision: functional unit 1 kg acetone (S20, 99.7 wt%) at the gate; mass allocation between
acetone and phenol (acetone share 0.386), energy (LHV, gas basis: acetone 29.0, phenol 31.8
MJ/kg) as a comparison. The tar is a production residue burned with heat recovery outside the
boundary: a waste under cut-off, not a co-product. Every background `missing:` with the
activity it should connect to (lca/lca.yaml); no factor, no licensed value. Proposal for the
LCA practitioner to confirm; economic allocation needs prices (acetone's are volatile, S1 8.1).

## D-015 LCI exclusions (2026-10-28)
Fugitive VOC (S1: 0.02-0.06 kg/t phenol) not estimated until the P&ID component counts exist;
storage outside the boundary; tar combustion belongs to its treatment; vacuum/fractionation
vents and the oxidiser off-gas methane not in the flowsheet (I-04). Construction, catalysts
(Pd, activated carbon replacement) and transport not included.

## Results (generated values are in the files)

- Balances: `cheme process streams`: every block and step closes within 1 kg/h; the oxidiser,
  cleavage, neutraliser and hydrogenation outlets are calculated by `cheme process propagate`
  from the reactions; `cheme validate` 0 errors, 0 warnings (element balances included).
- Overall per t phenol: cumene 1.330 t, air 1.92 t, H2 0.96 kg, H2SO4 (98 %) 4.1 kg, NaOH
  (50 %) 6.5 kg, wash water 40 kg; acetone 0.629 t, tar 46.6 kg, effluent 64 kg, spent air 1.56 t.
- LCI per kg acetone (mass allocated, lca/inventory.csv): inputs 2.0264 kg (cumene 0.8163, air
  1.1785, H2 0.00059, acid 0.0025, caustic 0.0040, water 0.0246) = outputs 2.0264 kg (acetone
  1, tar 0.0286, effluent 0.0394, vent 0.9584); power 0.117 kWh, LP steam 0.234 kWh, MP steam
  0.620 kWh, cooling water 1.520 kWh. `cheme assess lca --coverage`: mass, element and carbon
  balances closed; 13 gaps; result class "partial screening", no impact claimed.

## Open items

- I-01 Selectivities and conversion (D-004, D-005) are assumed: find an open source with
  measured CHP selectivity versus conversion and DMBA/AMS yields in cleavage.
- I-02 Property package for the polar system (core #315), then simulate the concentration
  and the four columns; replace D-011's literature utilities with calculated duties.
- I-03 Heat integration (oxidation heat to the pre-flash, S1 8.2.2.2) not modelled.
- I-04 Vacuum/fractionation vents, RTO, methane in the off-gas, fugitive emissions.
- I-05 Phenol recovery unit, acetone recycle to cleavage, cumene washing, aldehyde treatment.
- I-06 Activated carbon, Pd catalyst and resin consumption (S1 8.3.3 g, 8.3.6).
- I-07 Choose the backgrounds (lca/lca.yaml `missing:` texts) and allocation with the LCA
  practitioner.
- I-08 Benchmark: the LCI reproduces no published inventory by design; compare once reviewed.
- I-09 Registry entries missing in `chemicals/chemicals.yaml` (consolidated library PR):
  cumene, acetone, phenol, sulfuric-acid, sodium-hydroxide, alpha-methylstyrene,
  acetophenone, cumene-hydroperoxide, sodium-sulfate, methanol (and a tar/heavy-residue
  entry); LCI vocabulary entries `cumene`, `sodium-hydroxide-50`, heavy-residue treatment.
