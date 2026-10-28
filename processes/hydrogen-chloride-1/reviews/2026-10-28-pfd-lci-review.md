---
topic: design
reviewed_commit: 60236ff4cda5886d62be6547d2238f62123881ba
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/reactions.yaml, process/materials.yaml, process/BFD.xml, process/PFD.xml, scripts/balance.py, lca/, equipment/equipment-list.yaml, runs/20261028-150623-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/hydrogen-chloride-1
merge: pending
---
# Review: design (concept PFD and preliminary gate-to-gate LCI), hydrogen-chloride-1

Independent review of the concept-stage case study for issue #137 (HCl synthesis burner, graphite
falling-film absorption to 33 wt-% acid, tail gas scrubbing, steam recovery), as committed on
`case/hydrogen-chloride-1` at 60236ff (6 commits above `origin/main`: f898e0d scaffold,
fe8d346 basis/BFD/PFD/balance, 8114a7a LCI and process.yaml, 0586c8f DESIGN.md/PROGRESS.md,
09aa013 D-009 check, 60236ff run record). The reviewer did not author any of it and changed no
design file.

Commands I re-ran myself at 60236ff:

- `cheme validate`: `16 file(s): 0 error(s), 0 warning(s)`. Infos: `cheme.decision-unknown`
  D-023 at `checks/checks.yaml:76` (a template comment), and `dexpi.load` port cycles on the
  BFD and PFD. It compared 2 sheets (BFD, PFD) and 12 lists. It skipped the lists-vs-P&ID
  cross-checks because no P&ID exists, which is out of scope here.
- `cheme check`: every concept gate passes except `layout-plot-plan` (layout out of scope).
  The basic/detail gates that fail (`pids-exist`, `design-review`, `layout-*`, `lifting-study`,
  `mto`, `electrical`, `hvac`, `datasheets`) are out of this run's scope. This record is meant
  to satisfy `design-review`.
- `cheme maturity`: calculation maturity **none**. `sourced.boundary` fails because the feed
  states are `assumed`, taken over from chlor-alkali-1 where they are also assumed.
  `balanced.model-basis` fails because R101's conversion and the C201/C202 outlets are
  specified, not sourced. Warning `cheme.maturity-claim-exceeds` at `process.yaml:35`.
- `cheme process streams`: SYN 3388.2 = 3388.2 kg/h; ABS 10013 = 10013 kg/h; steps R101, C201
  (10031.5), C202 (6656.3/6656.31) and P201 all ok. Extents HCL_SYN 45.2538 and H2_OX 0.820787
  kmol/h.
- `cheme process propagate --check`: no output, so no stale or deviating calculated value.
- `cheme assess lca --coverage`: "partial screening carbon footprint" with 7 gaps (feed:CL2,
  feed:H2, feed:DMW, feed:POWER, product:CW, emission:H2 and emission:HCl uncharacterised).
  Mass, element and carbon-origin balances closed; energy closure 130.9 %, explained in
  DESIGN.md section 5. Publication: public; publishable.
- `git diff --name-only origin/main..HEAD`: every path is under `processes/hydrogen-chloride-1/`.

## Findings

The run task asked for findings as R-01 ...; the ids below use the repository's required form
(`reviews/README.md`), with the R-number at the start of each finding.

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | lca/lca.yaml:29-43, DESIGN.md D-013 | allocation HCLACID/STEAM | R-01: The 1.0/0.0 shares between acid and exported steam (0.665 kWh = 1.03 kg steam per kg HCl) depart from the library allocation hierarchy (ADR 0007: physical relationship, else the WBCSD price-ratio rule). The deviation text says the price ratio "does not apply" because steam is counted in kWh. That argument does not hold: a price per kWh or per kg of steam can be compared with the acid price just as well. At typical orders of magnitude (steam a few cents/kg, bulk 33 % acid about ten times that per kg of acid) a price-ratio allocation would give the steam a share of very roughly 5-15 %. So the acid's future footprint is overstated by that much, and silently, once backgrounds are linked. Today every background is a gap, so no number is wrong yet. The rationale as written would mislead a later reader. | medium | open | Either compute the WBCSD price ratio with sourced acid and steam prices (step 3 of ADR 0007) and allocate accordingly, or keep 1/0 as an explicit owner-decided deviation (ADR 0007: a departure is a finding) and delete the "kWh, so the price ratio does not apply" argument from `lca/lca.yaml` and D-013. Add the economic-allocation result as a scenario. |
| 2026-10-28-pfd-lci-review#2 | DESIGN.md D-007; scripts/balance.py | Q1 steam export 2195 kW | R-02: The steam yield of 1.03 t/t HCl with 3 % heat loss sits close to the thermodynamic ceiling. The HCl reaction heat (about 2.53 MJ/kg HCl) over 2.34 MJ/kg steam gives about 1.08 t/t, before the gas leaves at 250 degC. About 110 kW (5 % of Q1) comes from burning the O2 impurity, which rests on chlor-alkali-1's assumed 1.8 vol-% O2. DESIGN.md section 2 admits that no reported steam yield of a real unit was found. The arithmetic is checked and correct (2427.6 + 23.7 - 183.4 = 2267.9 kW released; 2195.1 kW / 2336.1 kJ/kg = 3383 kg/h). The value is the most optimistic end of the plausible range and is not marked as such. | low | open | In D-007, state that 1.03 t/t is close to the ideal-recovery bound. Give the O2-combustion share. Replace with a vendor or literature steam yield when found (open input already listed). |
| 2026-10-28-pfd-lci-review#3 | DESIGN.md D-008; scripts/balance.py (`y_w_abs`) | S5 absorber tail gas | R-03: The tail gas water is set by the vapour pressure of pure water at 40 degC ("over the weak acid, taken as water"). In a falling-film absorber the gas leaves where it meets the strong (33 %) acid, whose water vapour pressure is far lower, and it also carries HCl near that acid's HCl vapour pressure. The script also excludes the HCl moles from the dry-gas basis. The effect is a few kg/h on an internal stream: S5 water 5.5 kg/h, no change to the boundary streams or the LCI. The description of the absorber outlet is physically inconsistent with the chosen equipment. | low | open | Describe the absorber flow arrangement in D-008 and note that S5 water is an upper bound. Replace it with the acid's vapour pressures when core#364 or a sourced table allows. |
| 2026-10-28-pfd-lci-review#4 | process/flowsheet.yaml:6-7 (header comment) | R101 / S3 | R-04: The header comment says S3 is calculated "by cheme (equilibrium reactor R101, D-005)", but R101 is `reactor: conversion`. D-005 rejects the equilibrium reactor because it does not converge. | low | open | Correct the comment to "conversion reactor at the equilibrium limit (D-005)". |
| 2026-10-28-pfd-lci-review#5 | process.yaml:5-10, 33-35 | summary / maturity | R-05: `maturity: concept` is the lowest value the schema allows, and the comment and `validation.notes` say honestly that `cheme maturity` reaches no level. The one-line `summary` that the Atlas shows still says "Concept stage", and `cheme maturity` keeps warning `cheme.maturity-claim-exceeds`. DESIGN.md section 5's "0 warnings" refers to `cheme validate` only. | low | open | Add "calculation maturity: none (cheme maturity)" to the `summary`, and say in DESIGN.md section 5 that `cheme maturity` warns claim-exceeds. |
| 2026-10-28-pfd-lci-review#6 | process.yaml:48-61 | chemistry outputs | R-06: The main product (33 wt-% hydrochloric acid) and the chlorine feed have no `chemistry:` entry because the registry lacks them. The Atlas page will therefore list steam as the only product-type output. This is disclosed in `validation.notes` and in the steam note. | low | open | Add `hydrogen-chloride` / `hydrochloric-acid/33` and `chlorine` in the consolidated registry PR (already listed in DESIGN.md section 7), then add both to `chemistry:`. |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md section 2 (SRC-1, SRC-6), D-009 | source locators | R-07: Three key values rest on second-hand reads: the JANAF dHf values ("via search summary"), Parker's infinite-dilution heat ("from a search summary", PDF 404), and the D-009 base value ("recalled" NBS Circular 500, not read). All are disclosed and D-009 is marked ASSUMED. My own check agrees: -61.4 kJ/mol at 4.11 mol water per mol HCl lies on the -26.0 (n = 1) to -69.0 (n = 10) curve derived from SRC-6, and is consistent with commonly tabulated integral heats of solution of HCl. Not wrong, but weak provenance for the value behind 92 % of Q3. Minor citation slips: the `H_STEAM, H_BFW` line of `scripts/balance.py` cites D-010 instead of D-007; the script uses the ATcT dHf of HCl (-92.173 kJ/mol) while `reactions.yaml` gives JANAF (-92.31). The difference is 0.15 % and documented in DESIGN.md section 3. | low | open | Read JANAF Cl-026 / H-064 and NBS (Parker 1965 or the NBS tables) at source and record table and page. Fix the D-010 to D-007 reference in the script comment. |
| 2026-10-28-pfd-lci-review#8 | checks/checks.yaml:76 | template comment | R-08: The example `accept:` comment cites D-023, which does not exist in DESIGN.md (info `cheme.decision-unknown`). It is template text, but it leaves an info in every validate run. | low | open | Neutralise the example's decision id in the template comment, or leave it and report the template issue to cheme-as-code. |

No critical or high finding.

## Previous findings

| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: no earlier review record exists for this process (`reviews/` held only README.md at
60236ff).

## Drawing

- `process/BFD.xml` and `process/PFD.xml` are **generated** by `cheme process build`.
  `cheme validate` reports no generated-sheet drift and 0 warnings. It prints no `drawing <sheet>:`
  line for these process sheets, so no lint counts are available. There are no P&IDs (out of
  scope).
- I rendered the whole PFD (`build/PFD.png`) and read it. All 4 steps, 7 terminals, 9 material
  and 4 energy streams are present and labelled. Cosmetic only: the generated routing crosses S1
  and S2 near the SYN block entry, and Q1/Q4 cross. Pinning `layout.pfd` could tidy this; it is
  not a finding at concept stage. I did not tile the PFD or render the BFD.

## Checked and fine

- **Scope vs issue #137** (per the run's task.md case notes): direct H2 + Cl2 burner, graphite
  absorber to 32-36 % acid (33 % chosen), tail gas scrubbing and steam recovery, with chlorine
  and hydrogen as boundary feeds linked to chlor-alkali-1 and not integrated. Rejected routes
  (by-product HCl, Mannheim) and the out-of-boundary items (storage, emergency caustic absorber,
  BFW treatment) are stated with reasons (D-001).
- **Balance by hand**:
  - Cl2 in S1 = 3208.8 kg/h = 45.254 kmol/h, giving 90.51 kmol/h = 3300.0 kg/h HCl.
  - O2 = 26.26 kg/h = 0.821 kmol/h.
  - H2 = 1.10 x (45.254 + 2 x 0.821) = 51.59 kmol/h = 104.0 kg/h = S2 x 0.679; excess 9.46 kg/h
    equals the vent H2.
  - Water: 6700 (acid) + 3.56 (vent) - 49.18 (wet H2) - 29.58 (formed) = 6624.8 kg/h = S7.
  - Vent HCl 1.10 g/h = 10 mg/Nm3 x 109.6 Nm3/h (wet).
  - Q3 is about 1544 kW heat of solution plus about 130 kW gas cooling and condensation.
  - Pumps: 8.6 m3/h x 130 kPa / 0.5 = 0.62 kW; BFW 3.5 m3/h x 1 MPa / 0.5 = 2.0 kW.

  All agree with `flowsheet.yaml` and `scripts/balance.py`.
- **Plausibility**: Cl2 0.972 kg/kg HCl (stoichiometric 0.9724) and H2 31.5 g/kg (28.6 g
  stoichiometric + 10 %). The 10 % excess lies inside the cited 2-15 % (SRC-4 [0015]). The
  250 degC furnace outlet and the 7-16 bar steam range are cited from SRC-3. Electricity of
  1.7 kWh/t HCl is low but consistent with no blower (feed pressures drive the gas) and cooling
  water pumping sitting in the CW background. Cooling 0.51 kWh/kg HCl, dominated by the heat of
  solution, is plausible. The 33 % product being above the 20.2 % azeotrope, and so needing
  cooled absorption, is correctly argued.
- **Equilibrium argument (D-005)**: K about 2.6e19 at 523 K. The conversion-1.0 representation
  is a labelled model basis with no invented kinetics. Free Cl2 in real acid is acknowledged as
  not modelled.
- **ASSUMED marking**: every stream value is `assumed` with a source or decision, except S3
  (calculated by propagate, fingerprints current). Design-basis values carry ASSUMED or a cited
  locator.
- **No third-party content copied**: DESIGN.md, the YAML and the script are written in own words.
  Facts are cited with locators (patent paragraphs and sections, Wikipedia sections, JANAF
  table ids). The licensed Ullmann chapter is used for route identity only, with no number.
  No figures or tables were reproduced.
- **LCI**:
  - Functional unit 1 kg contained HCl (3.0303 kg acid), consistent with S9.
  - Per FU: inputs 0.980312 + 0.0464152 + 2.00752 = 3.03425 kg; outputs 3.0303 + 0.003945 =
    3.03425 kg. Mass closes. Every exchange matches its flowsheet stream divided by 3300 kg/h.
  - No zero-filled background and no licensed values. `results.csv` total 0 only because every
    background is a gap, and `--coverage` says so.
  - Every unmapped background (and the steam substitution) is `missing:` with a description of
    the activity to link, listed in `gaps.csv`.
  - `lca/mappings.yaml` holds the per-process override file (empty, with reasons and
    candidates). The shared `lci/mappings.yaml` is untouched.
  - Emission exclusions are declared with reasons. H2 to air is reported as a gap, not as 0.
- **process.yaml**: `publication.status: internal`, `validation.status: unreviewed`. Notes
  state maturity none, specified absorber values and the core#364 gate. References are given
  with locators. The `inventory_key` removal on wet hydrogen and demineralised water is
  justified.
- **Nothing outside `processes/hydrogen-chloride-1/` changed.**

## Not checked

- I did not run the library build (`scripts/build_lci.py --strict`). The report's "4 gaps, no
  error" is not verified, including whether the build flags the allocation deviation of #1.
- I did not read the issue #137 thread itself (`gh`). The scope was taken from the run's task.md
  case notes.
- I did not fetch or re-read the cited sources (patents, Wikipedia, JANAF, Parker). Values were
  checked for internal consistency and against general engineering knowledge only.
- `process/materials.yaml` formation and heat capacity records were not checked value by value.
  `lca/dataset.yaml` and `manifest.json` (generated) were not read line by line.
- BFD render, PFD tiles, and the equipment-list design conditions and materials (D-012) were not
  reviewed in detail.
- Safety aspects (hydrogen-rich vent location, burner management, chlorine breakthrough) are
  not in scope at this stage. They belong to the HAZOP and basic engineering.
