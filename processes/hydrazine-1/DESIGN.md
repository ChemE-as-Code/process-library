# Design decisions

One entry per decision: what was decided, why, what was rejected, and what it assumes.
Issue: ChemE-as-Code/process-library#141. Run of 2026-10-28 (concept: design basis to
balanced PFD and a preliminary gate-to-gate LCI). Starting library commit cc5624f,
cheme-as-code 0.8.0 (pyDEXPI 2.1.0, Python 3.15). Designed independently from open sources
(patents, NIST WebBook); no published flowsheet, stream table or figure was copied.

## Route and boundary memo

**Route.** Peroxide process (Pechiney-Ugine-Kuhlmann, PCUK; now Arkema), as set by the issue:
2 NH3 + H2O2 + 2 MEK -> methyl ethyl ketazine + 4 H2O in an activated aqueous working
solution, then ketazine + 2 H2O -> N2H4 + 2 MEK by hydrolysis under pressure, MEK recycled.
Why this route, against the other industrial families (screening from general knowledge and
S7, not a quantified comparison):

| route | oxidant / carrier | salt co-product | why not chosen here |
|---|---|---|---|
| Raschig / Olin-Raschig | NaOCl with NH3 (chloramine) | NaCl, dilute product, large evaporation | issue scope; salt and chlorine/caustic demand |
| Bayer ketazine (hypochlorite-ketazine) | NaOCl with acetone | NaCl | issue scope; still needs hypochlorite |
| Urea (Hofmann-type) | NaOCl with urea | NaCl, Na2CO3 | issue scope; small plants |
| **Peroxide (PCUK)** | H2O2 with MEK | none | chosen: no salt, azine decants (S7), recycles close |

The ketazine (rather than acetone azine) is chosen because it is insoluble in the working
solution and separates by decantation (S1 stage (b); S7). The aldazine/ketazine chemistry of
the `tech-heavy-chem-reaction-families` skill is not needed beyond this.

**Product.** Hydrazine hydrate solution at 64.0 wt% N2H4 (the "100 % hydrazine hydrate"
grade, N2H4.H2O), the form in which hydrazine is mostly traded (D-002). Anhydrous hydrazine
(beyond the hydrazine-water maximum-boiling azeotrope, needing an entrainer or a caustic
dehydration) is out of scope.

**Boundary.** From hydrogen peroxide (70 wt%), anhydrous ammonia, MEK, acetic acid, disodium
phosphate and demineralised water at the battery limit to hydrazine hydrate, a 2-butanol
bleed, a pyrazoline purge, a working-solution purge, waste water and the reactor off-gas at
the battery limit. Outside: H2O2 (library `hydrogen-peroxide-1`), NH3 (library `ammonia-1`;
its hydrogen could come from `hydrogen-1`), storage, the site boilers, cooling tower,
incinerator and waste water treatment. Utilities cross the boundary as energy streams.

```
 H2O2 70 % ─┐                 ┌───────── MEK + water (S41) from hydrolysis ─────────┐
 NH3 ───────┼─> AZN: R-101 reactors 323 K ─> V-101 decanter ─> off-gas (O2, N2) vent │
 MEK make-up┘     ^  ^  ^                    │ azine phase      │ spent working sol. │
                  │  │  └── MEK recycle ─────┤                  v                    │
                  │  │      (S31)            v           WSR: E-201 heater (+ acetic │
                  │  │                AZD: C-301 azine col.     acid, phosphate)     │
                  │  │                 ├─> 2-butanol bleed      C-201 regeneration ─> purge
                  │  │                 │ azine                  │ water + NH3        │
                  │  └── NH3 (+MEK) ───┼────────────────────── C-202 NH3 recovery ─> waste water
                  └──── working solution (S20) ─┘               (bottoms)            │
                                       v                                             │
 demin water ──────────────> HYD: C-401 hydrolysis (reactive distillation, 900 kPa) ─┘
                              ├─> pyrazoline purge    │ 30 % hydrate
                              │   water recycle <──── C-402 concentration ─> hydrazine hydrate 64 % N2H4
```

## Source register

| # | source | locator | read | reuse | used for |
|---|---|---|---|---|---|
| S1 | US 6,562,311 B1 (2003), Method for preparing hydrazine hydrate, [Google Patents](https://patents.google.com/patent/US6562311) | Description stage (a): 0-100 C (pref. 30-70 C), atmospheric to ~10 bar, per mol H2O2 0.2-5 mol MEK and 0.1-10 mol NH3 (pref. 1.5-4), 0.1-1 kg working solution; yields >50 % up to ~90 % of H2O2; Ex. 4 (acetamide/ammonium acetate, 50 C, 7 h): H2O2 conversion 98 %, azine yield 81 %; Ex. 5: 99 % / 81.9 %; definitions: 2-butanol formed by reduction of MEK by a hydrazine derivative; claims: 2-butanol/MEK 0.05-0.15 at the reactor inlet, the rest bled; stage (e): 2-butanol dehydrogenation to MEK; stage (f): hydrolysis 2-25 bar, bottom 150-200 C (pref. 175-190 C), water/azine 5-8 mol/mol, bottoms typically 30 % up to 45 % hydrazine hydrate | page text via fetch, sections and examples located, no column numbers | patent text: facts only | D-003, D-004, D-006, D-007 |
| S2 | US 6,605,265 B1 (2003), Continuous production of azines/hydrazine hydrate, [Google Patents](https://patents.google.com/patent/US6605265B1/en) | Description: H2O2 30-90 wt%, working solution 0.1-1 kg per mol H2O2, phosphate catalyst 10-1000 ppm (disodium phosphate preferred), regeneration by heating above 130 C (pref. 150-250 C) with water removal, column 5-50 plates, 10 min-2 h; NH3 overhead returned to the reactor; Ex. 1: per 1000 kg/h H2O2 (100 %, from 70 %): NH3 1000 kg/h, MEK make-up 100 kg/h, acetic acid 60 kg/h, disodium phosphate 3 kg/h, working solution 11 000 kg/h, regeneration column head 0.9 bar(a), base 180 C, reboiler steam 10 500 kg/h at 18 bar(a); azine 3 900 kg/h | page text via fetch, examples located | patent text: facts only | D-003, D-005, D-010 |
| S3 | US 12,134,558 B2 (2024), Process for preparing hydrazine hydrate with pyrazoline recycling, [Google Patents](https://patents.google.com/patent/US12134558) | step (f): reactive distillation 2-25 bar, bottom 150-200 C, 40-50 trays at 8-10 bar, water/azine 5-30 (pref. 10-20); Ex. 1: overhead 7.5-9.7 bar(a), condenser 160 C, bottom 178-190 C, reboiler 200 C at 16 bar, 5 000 kg/h azine + 10 000 kg/h water; pyrazolines (trimethyl-ethyl- and diethyl-methyl-pyrazoline) form mainly in hydrolysis, tray level kept at 1-3 wt% by a side purge recycled through the azine wash and distillation | page text via fetch | patent text: facts only | D-006, D-007 |
| S4 | US 4,724,133 A (1988, Atochem), Preparation of concentrated aqueous solution of hydrazine hydrate, [Google Patents](https://patents.google.com/patent/US4724133) | search abstract: water/azine 3-7 mol/mol, column base 150-200 C (pref. 175-200 C); hydrolysing dilute acetone-azine solutions needs at least 10 t steam per t hydrate | search snippet, full text not audited | patent text: facts only | D-007 context, D-010 plausibility |
| S5 | NIST Chemistry WebBook, SRD 69, [webbook.nist.gov](https://webbook.nist.gov/chemistry/) | standard formation enthalpies: H2O2(l) -187.8, H2O(l) -285.83, NH3(g) -45.9, N2H4(l) +50.6 kJ/mol | values as commonly tabulated, not re-fetched in this run | facts | D-010 reactor heat |
| S6 | PubChem, [CID lookup by CAS 5921-54-0](https://pubchem.ncbi.nlm.nih.gov/) | 5921-54-0 = 2-butanone (1-methylpropylidene)hydrazone (methyl ethyl ketone azine) | REST query | open data | materials.yaml identity |
| S7 | Wikipedia, "Peroxide process", [en.wikipedia.org](https://en.wikipedia.org/wiki/Peroxide_process) (CC BY-SA; secondary, citing Ullmann's and Hayashi et al. 1976 doi 10.1021/i360060a016) | developed early 1970s by PCUK; ketazine decants; ~50 C, atmospheric, H2O2:ketone:NH3 about 1:2:4; hydrolysis endothermic, ~8 bar, 130/179 C top/bottom; 30-45 % hydrate; no salt co-product; Lannemezan plant 17 kt/a of hydrazine products | page via fetch | facts only, secondary | route memo, D-002 scale check |
| S8 | Schirmann, Bourdauducq: Hydrazine, Ullmann's Encyclopedia (doi 10.1002/14356007.a13_177) | not opened (licensed); issue #141 lead | not read | - | lead only |

Core issues #315 and #364 named in the issue could not be read from this environment (`gh`:
not resolvable in ChemE-as-Code/core); the gated steps below are stated from what cheme 0.8.0
itself reports (`cheme process props --coverage`).

## D-001 Hydrogen peroxide and ammonia are boundary feeds (2026-10-28)
Decision: H2O2 (70 wt%) and anhydrous liquid ammonia enter at the battery limit, MEK, acetic
acid and disodium phosphate are purchased make-ups.
Reason: issue scope; the library has `hydrogen-peroxide-1` and `ammonia-1` to link later as
datasets (the H2O2 concentration of that design must be checked against 70 wt%).
Rejected: an integrated H2O2 plant (one site, the anthraquinone loop sharing utilities): its
own case.

## D-002 Product and capacity: 2000 kg/h hydrazine hydrate (64 wt% N2H4), 8000 h/a (2026-10-28)
Decision: 16 kt/a of 100 % hydrazine hydrate (10.2 kt/a N2H4).
Reason: the traded grade; scale of the same order as the largest peroxide plant named in S7
(17 kt/a of hydrazine products). ASSUMED, no client basis.

## D-003 Azine synthesis conditions (2026-10-28)
Decision: stirred reactors in series (lumped, R-101) at 323 K and about 150 kPa(a); inlet
MEK/H2O2 2.2 and NH3/H2O2 2.5 mol/mol (with recycles), H2O2 fed at 70 wt%.
Reason: 50 C in S1 Ex. 4-5 and S2 Ex. 1; ratios inside the preferred 1.5-4 of S1/S2. S7
quotes about 1:2:4 for H2O2:ketone:NH3; a lower ammonia excess is chosen to reduce the NH3
recycle, ASSUMED. Pressure slightly above atmospheric to keep NH3 dissolved, ASSUMED.

## D-004 Azine reactor model: complete H2O2 conversion with selectivities (2026-10-28)
Decision: `selectivity` on R101, key H2O2, conversion 1.0; per kmol H2O2: 0.85 kmol azine
(AZINE), 0.03 kmol 2-butanol (BUTANOL, 2 H2O2 each), 0.045 kmol O2 (DECOMP, 2 H2O2 each).
Reason: S1 Ex. 4-5 give 98-99 % conversion and 81-82 % azine yield in batch; S1 and S2 state
yields "up to about 90 %"; the continuous S2 Ex. 1 implies a higher figure (3 900 kg/h azine
per 1 000 kg/h H2O2 would be ~95 %, if the stream were pure azine, which is not stated). 0.85
is ASSUMED inside that range. 2-butanol: S1 names the reduction of MEK; the net equation
(diimine reducing MEK, N2 released) is this study's. The share 0.03 is ASSUMED so that the MEK
make-up (0.093 kg per kg H2O2) is close to S2 Ex. 1 (0.100). The rest of the H2O2 is counted
as decomposed to O2, ASSUMED (no source on the split between decomposition and oxidation of
NH3 to N2). A sourced range check, not kinetics.
Rejected: the batch 81 % as the design value (continuous recycle of the working solution and
of MEK is what the industrial process does; S2).
Sensitivity: each 1 point of azine yield changes the H2O2 demand by about 1.2 %.

## D-005 Working solution and its regeneration (2026-10-28)
Decision: the working solution (activator acetamide/ammonium acetate, lumped as acetamide;
disodium phosphate catalyst) circulates at 11 kg per kg H2O2 (S2 Ex. 1), returns at 45 wt%
acetamide and 500 ppm phosphate (ASSUMED; S2: 40-80 % as acetic acid equivalent, phosphate
10-1000 ppm). It is heated above 403 K (E-201) and regenerated in C-201 (head 90 kPa(a), base
about 453 K, S2 Ex. 1), which removes all reaction and peroxide water with the excess NH3 and
the dissolved MEK. C-202 (about 300 kPa(a), ASSUMED) returns NH3 and MEK as vapour to the
reactors (S2: NH3 overhead returned) and sends the water to treatment. Make-up 60 kg acetic
acid and 3 kg disodium phosphate per t H2O2 (S2 Ex. 1); the acetic acid becomes activator
(AMIDATION, ASSUMED complete) and an equal amount of activator leaves in a purge S15 (50 wt%
water, ASSUMED) with the phosphate. The impurity adsorber of S2 is not modelled.
Assumptions: the purge, its route (incineration) and the lumping of the activator system are
ASSUMED; the real loss mechanism of the activator (degradation, adsorber regeneration) is not
known from the sources read (I-03).

## D-006 Decanter and azine column (2026-10-28)
Decision: V-101 separates the organic azine phase (all azine, excess MEK less 1 wt% dissolved
in the aqueous phase, all 2-butanol, 3 wt% water and 0.5 wt% NH3, ASSUMED) from the working
solution and vents the gas. C-301 sends excess MEK with the dissolved water and NH3 back to
the reactors, bleeds the 2-butanol formed in a side draw (85 wt% 2-butanol, 10 wt% MEK,
ASSUMED composition), and gives a pure azine bottoms (sharp split ASSUMED). The azine wash
column of S3 is lumped in.
Rejected: dehydrogenating the 2-butanol back to MEK (S1 stage (e)): an extra reactor for
about 105 kg/h; the bleed goes to incineration (open: I-06).

## D-007 Hydrolysis and concentration (2026-10-28)
Decision: C-401, a reactive distillation column at about 900 kPa(a) (S3 Ex. 1: 7.5-9.7 bar(a)),
modelled as a conversion zone (R401: HYDROLYSIS 0.995 and ISOMERISATION 0.005 of the azine fed,
parallel; ASSUMED) and a separation (C401): MEK with 11 wt% water overhead (near the MEK-water
azeotrope, ASSUMED) to the reactors; a pyrazoline purge (50 wt% water, ASSUMED) after the azine
and MEK have been recovered from it (S3 recycles it through the wash and azine column, lumped
here); bottoms 30 wt% hydrazine hydrate (S1: typically 30 %). Water/azine at the inlet 10.5
mol/mol (S3: 5-30, pref. 10-20; S1: 5-8). C-402 concentrates the bottoms to 64 wt% N2H4 (below
the maximum-boiling hydrazine-water azeotrope, so water goes overhead); its water returns to
the hydrolysis, demineralised make-up closes the water balance.
Reason: the reaction is an equilibrium (S1, S3), pushed to completion by removing MEK
overhead; modelled as complete with an irreversible reaction (the conversion reactor needs
it).
Rejected: hydrolysis near atmospheric pressure (older patent US 3,481,701, search snippet):
S1/S3 describe pressure columns.

## D-008 Off-gas and waste water (2026-10-28)
Decision: the reactor off-gas (O2 2.13 kmol/h, N2 1.42 kmol/h) leaves V-101 after a vent
condenser/scrubber (lumped) with 1 mol% NH3 and 0.5 mol% MEK (ASSUMED, no emission source
read). The waste water (C-202 bottoms) carries 1000 mg/kg MEK and 100 mg/kg NH3 (ASSUMED).
Open: I-04.

## D-009 Balance method (2026-10-28)
Decision: `scripts/balance.py` derives every assumed separator and boundary stream from D-002 to
D-008 (iterating the recycles: MEK, working solution, NH3, hydrolysis water); `cheme process
propagate --fill` calculates the mixers M101, M401 and the reactors R101, R201, R401 from those
inlets; `cheme process streams` checks every block and step.

## D-010 Utilities: one scaled patent figure and hand estimates (2026-10-28)
Decision (kW, design case; per kg hydrate in brackets):
- Regeneration (E-201 + C-201) 8 958 kW MP steam: 10.5 t of 18 bar(a) steam per t H2O2 (S2 Ex. 1)
  scaled to 1.607 t/h H2O2, latent heat 1 912 kJ/kg; split heater 2 174 kW (S12 heated 323 to
  423 K at 3.4 kJ/(kg K), ASSUMED) and column 6 784 kW. The S2 feed entered the column at 50 C,
  so the heating is inside the patent figure, not added.
- C-301 834 kW MP steam (overhead vapour at reflux ratio 1.5, latent heats at 1 atm, ASSUMED).
- C-401 2 627 kW MP steam (MEK/water overhead at reflux ratio 1, plus heating the water feed
  373 to 458 K, ASSUMED); the hydrolysis heat (endothermic per S7) is not counted: unknown,
  so C-401 steam is a lower bound.
- C-402 3 247 kW LP steam (overhead water at reflux 0.3, less the flash of the 458 K feed).
- C-202 739 kW LP steam (0.2 kg stripping steam per kg feed water plus NH3 vaporisation).
- R-101 cooling 2 904 kW: -241.5 kJ/mol for H2O2 + 2 NH3(g) -> N2H4(l) + 2 H2O(l) (S5),
  counted for the azine and the 2-butanol path, plus -98.2 kJ/mol H2O2 decomposed; the heat of
  condensing hydrazine with MEK to the azine is neglected (exothermic if the hydrolysis is
  endothermic, S7), so this is a lower bound.
- Condensers equal to the reboilers (C-201, C-301), C-401 1 859 kW, C-402 3 802 kW (includes the
  feed flash), C-202 537 kW. Power 100 kW (pumps, agitators), ASSUMED hand estimate.
Totals: MP steam 12 419 kW (6.21 kWh/kg), LP steam 3 986 kW (1.99 kWh/kg), cooling water
18 894 kW (9.45 kWh/kg), power 0.05 kWh/kg. Steam at 2.2 MJ/kg corresponds to about 13 kg
steam per kg hydrate, 55 % of it the regeneration: a single patent example, the largest
uncertainty of the LCI. No heat integration (the C-401 condenser at about 433 K, S3, could
raise LP steam for C-402; I-05).
Reason: no property package covers the mixture (D-011), so duties cannot be calculated.

## D-011 Property method: none qualified (2026-10-28)
Decision: `property_method: placeholder`. `cheme process props --coverage`: the only
benchmarked package of this process scope is a syngas Peng-Robinson vapour package; water,
hydrazine, MEK, the azine, acetamide, acetic acid and the phosphate are outside every package.
Gated step: energy balances and a DWSIM simulation (`cheme process simulate`) need a qualified
activity-coefficient package for hydrazine-water-MEK-azine-NH3 (the hydrazine-water azeotrope,
MEK-water heterogeneous azeotrope) and electrolyte support for the ammonium acetate/phosphate
working solution (the issue names core #315 and #364; not readable from here).

## D-012 Lists at concept (2026-10-28)
Decision: one equipment tag per PFD step (pumps, reboilers, condensers, coolers, the vent
scrubber and the working-solution adsorber not split out); line and instrument lists stay
empty until P&IDs.

## D-013 LCI: foreground only, single product (2026-10-28)
Decision: functional unit 1 kg hydrazine hydrate solution (64 wt% N2H4) at the gate (per kg
N2H4 divide by 0.64); cradle-to-gate frame with the foreground only; no allocation (one
product: the 2-butanol bleed and both purges are wastes with `treatment:`, not co-products);
every background `missing:` with the activity it should connect to; steam counted in kWh of
heat delivered (lca/mappings.yaml); O2 and N2 in the vent free (no characterised burden), NH3
and MEK elementary emissions to air. No construction inventory.

## D-014 LCI exclusions (2026-10-28)
Decision: fugitive emissions (need P&ID counts), storage breathing (outside the boundary), the
combustion of the bleed and purges (in their treatment backgrounds) and the column/vacuum vents
(not in the flowsheet) are listed under `emission_exclusions`, not claimed negligible. Not
modelled at all: hydrazine traces in the waste water and in the product's organic impurities,
H2O2 stabiliser, resin/adsorbent consumption (S2), catalyst none (homogeneous).

## Results (generated values are in the files)

- Balances: `cheme process streams`: every block (AZN, WSR, AZD, HYD) and step closes; reactor
  extents AZINE 40.14, BUTANOL 1.42, DECOMP 2.13, AMIDATION 1.60, HYDROLYSIS 39.94,
  ISOMERISATION 0.20 kmol/h; `cheme validate` 0 errors, 0 warnings (element balances included).
- Boundary (kg/h): in H2O2 70 % 2 294.8, NH3 1 444.0, MEK 149.2, acetic acid 96.4, Na2HPO4 4.8,
  water 2 899.2 = 6 888.4; out hydrate 2 000.0, 2-butanol bleed 123.6, pyrazoline purge 56.3,
  working-solution purge 199.2, waste water 4 399.7, off-gas 109.6 = 6 888.4.
- Per kg N2H4: H2O2 (100 %) 1.255 kg (stoichiometric 1.061), NH3 1.128 kg (stoichiometric 1.063),
  MEK 0.117 kg.
- LCI per kg hydrate (lca/inventory.csv): inputs 3.44422 kg = outputs 3.44422 kg; MP steam 6.21
  kWh, LP steam 1.99 kWh, cooling water 9.45 kWh, power 0.05 kWh. `cheme assess lca --coverage`:
  mass, element and carbon balances closed, energy closure 0.0 %; 14 background gaps and 2
  uncharacterised emissions (NH3, MEK in GWP100); result class "partial screening", no impact
  claimed.
- `cheme check`: concept gates ok except layout-plot-plan (out of scope); `cheme maturity`:
  calculation maturity none (feed flows from an assumed capacity, specifications assumed).

## Open items

- I-01 Azine yield and by-product split (D-004) assumed inside patent ranges: read Hayashi et
  al. 1976 (doi 10.1021/i360060a016) and Ullmann's (S8) for continuous-plant yields.
- I-02 Property package and electrolyte support (D-011), then simulate C-201, C-301, C-401,
  C-402 and replace the hand duties (D-010).
- I-03 Activator loss mechanism, purge size and adsorber regeneration (D-005).
- I-04 Off-gas treatment, NH3/MEK emissions, column vents, fugitive emissions (D-008, D-014).
- I-05 Heat integration: C-401 condenser to C-402, feed/bottoms exchange around C-201 (D-010).
- I-06 2-butanol: bleed vs dehydrogenation to MEK (D-006).
- I-07 Choose the backgrounds (lca/lca.yaml `missing:` texts) with the LCA practitioner; link
  hydrogen-peroxide-1 and ammonia-1 datasets.
- I-08 cheme 0.8.0 finding for core: `chemeascode/domains/process/model.py` (reactor checks,
  about line 988) reassigns the name `declared` (the reactions-by-id dict) to a list inside the
  selectivity check, so every reactor step after the first one with a `selectivity:` sees no
  reactions ("the key ... is a reactant of none of its reactions"). Worked around: R401 uses
  per-reaction conversions.
- I-09 Registry entries missing in `chemicals/chemicals.yaml` (consolidated library PR):
  hydrazine (with a `hydrazine/hydrate-64` grade), hydrogen-peroxide (70 wt% grade), ammonia,
  methyl-ethyl-ketone, acetic-acid, 2-butanol, sodium-phosphate (disodium hydrogen phosphate),
  acetamide; LCI vocabulary entries `hydrogen-peroxide`, `methyl-ethyl-ketone`, `acetic-acid`,
  `sodium-phosphate`, solvent and hazardous-waste incineration.
- I-10 Benchmark: the LCI reproduces no published inventory by design; compare once reviewed.
