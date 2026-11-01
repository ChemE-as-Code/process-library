---
topic: design
reviewed_commit: 8412c2e2dc094e540231b81e276578bf42cfc790
scope: [process.yaml, DESIGN.md, PROGRESS.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, scripts/kraft_balance.py, equipment/equipment-list.yaml, lca/lca.yaml, lca/mappings.yaml, lca/results.md, lca/results.csv, lca/gaps.csv, lca/inventory.csv, lca/dataset.yaml, lca/manifest.json, runs/20261028-155500-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/kraft-pulp-1
merge: pending
---
# Review: design (concept BFD/PFD and preliminary LCI, kraft-pulp-1, issue #180)

An independent agent reviewed this case. It did not write it. The branch is `case/kraft-pulp-1`
(5 commits, 902b0ec..8412c2e), compared with its merge base on `origin/main`. Diffing against
`origin/main` itself also lists `processes/thf-1/` as deleted. That is only because `main` moved
on after the branch was made: `git diff --name-only $(git merge-base origin/main HEAD)..HEAD`
lists only files under `processes/kraft-pulp-1/` (191 files).

## Commands re-run by the reviewer

| command | result |
|---|---|
| `cheme validate` | 16 files, 0 errors, 0 warnings. Infos: `cheme.decision-unknown` for D-501 (an equipment tag, not a decision) and D-023 (a template comment in checks/checks.yaml). Both are false positives. No P&IDs exist, so list-vs-P&ID cross-checks were skipped. |
| `cheme check` | Concept gates ok: design-basis, concept-lists, process-concept, process-balances, process-links-concept, assumptions-marked. `layout-plot-plan` fails (layout is out of scope for this stage). `design-review` fails until this record is committed. All P&ID, layout, datasheet and detail gates fail, which is expected at concept. |
| `cheme maturity` | Calculation maturity **none**. `cheme.maturity-sourced-boundary` fails because no feed flow or composition is `given` with a source; every value is ASSUMED. `cheme.maturity-claim-exceeds` warns on `maturity: concept` (see #4). |
| `cheme process streams` | All 10 blocks and 16 steps balance (largest residual 1 kg/h, at W201). Every stream value has provenance A. |
| `cheme process propagate --check` | No output, exit 0. |
| `cheme run scripts/kraft_balance.py` | Reproduces the flowsheet: every step's mass closes, the worst element residual is 3.7e-7 kmol/h, and the Na/S/NaOH cycle converges in 153 iterations. |
| `cheme assess lca --coverage` | Partial screening carbon footprint. 17 gaps: 14 declared-missing backgrounds, each with a description of the activity to connect, plus NO2, SO2 and dust, which have no GWP factor. Mass, element and carbon-origin balances closed at 5 %. Energy closure 20.7 % (see #7). Publishable. |

## Findings

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | lca/results.md:54, lca/results.csv, lca/manifest.json | climate result | **The published climate result misstates fossil CO2.** `results.md` and `results.csv` report 0.0499 kg CO2-eq per kg pulp as "fossil GHG emissions" and as "PCF excluding biogenic". The inventory's own fossil CO2 is 0.0823 kg/kg: 30 kg CH4 per ADt in K902 (COMB_NG 77.9 kmol/h x 44 kg/kmol over 41,667 kg/h), which I checked by hand. The core characterisation ignores the `origin: fossil/biogenic` declared on emission:CO2 and emission:CO2B (lca.yaml:90). Instead it applies the plant-wide fossil carbon share (2.1 %) to every CO2 emission. As a result, 98 % of the fossil kiln CO2 is counted as biogenic, 0.048 kg of the biogenic CO2B is counted as fossil, and the results show 0.0084 kg **fossil carbon content of the product** (results.md:64) for a pulp that is 100 % wood carbon. The fossil figure is 40 % too low and is labelled as fossil. Only DESIGN.md section 5 (line 240) and the run report explain this. Nothing in `lca/` warns about it, and results.md/results.csv/manifest.json are what the Atlas and a reader take. | high | open | Raise the characterisation behaviour with core (origin declared per elementary flow must win over the pool share). Until it is fixed, do not present the number as the study's result. Either withhold the climate result from the published outputs, or put a visible caveat at the top of lca/README.md (and in process.yaml `validation.notes`) that the inventory split (fossil 0.082, biogenic 2.30 kg CO2/kg) is authoritative and the characterised 0.050 is a known core error. Then rewrite the outputs. |
| 2026-10-28-pfd-lci-review#2 | DESIGN.md:12-14 | core dependencies | Issue #180 (job handoff comment) asks the run to inspect the current state of the core issues on electrolytes, solids and furnace energy at startup, check them against this case's species and conditions, and record the resolved core commit "before calling this a blocker". DESIGN.md says this was **not re-audited (budget)** and records cheme 0.8.0 but no core commit. DESIGN.md D-007, D-009 and section 5 still name the electrolyte and furnace energy issues as the reasons why energy closure and the kiln furnace energy were not done. The gating claims therefore have no evidence behind them. | medium | open | Record the core commit, check those core issues (issue or PR state and what is merged) against black liquor, smelt, lime mud and the kiln, and update D-007, D-009 and section 5. If `cheme process furnace` now applies to the kiln, run it. |
| 2026-10-28-pfd-lci-review#3 | DESIGN.md:169-180, lca/lca.yaml:90 | biogenic carbon of kiln calcination CO2 | The classification of lime-mud calcination CO2 (0.172 kg/kg) as biogenic is a key LCI convention. D-012 rests it on "NCASI/WRI-type pulp and paper GHG guidance ... not re-read in this run; to be cited with locator". The CO2B entry in lca.yaml states the convention without any source. The task brief requires facts to cite a source with a locator. | medium | open | Cite the guidance (document, edition, section) that treats recycled-mud calcination CO2 as biogenic, or mark the convention ASSUMED in lca.yaml and D-012 and show the fossil-case sensitivity (+0.172 kg CO2/kg). |
| 2026-10-28-pfd-lci-review#4 | process.yaml:37-49 | maturity | `cheme maturity` warns `cheme.maturity-claim-exceeds`: `concept` is claimed, but the evidence supports none, because no feed or specified value is `given` with a source. `concept` is the lowest value the schema allows, and the comment explains that every parameter is assumed. However, `validation.notes` does not say that no calculation maturity level is reached. | low | open | Add one sentence to `validation.notes`: calculation maturity none (`cheme maturity`), and why. Close the gap later by giving sourced values (e.g. an owner or reference-mill basis) the provenance `given`. |
| 2026-10-28-pfd-lci-review#5 | DESIGN.md:57-76 | black liquor representation | The lumped strong black liquor solids are C 38.0 %, H 4.5 %, S 4.5 %. BREF 2015 Table 3.12 gives C 31-32 %, H 3.1-3.3 %, S 6.1-6.3 % (D-003 states this honestly). Steam is then taken as 3.5 kg/kg of this BLDS mass. A real-composition BLDS carrying the same wood carbon would weigh more (about 2.0 rather than 1.69 t/ADt), so the steam basis is ambiguous. One cross-check holds: 1689 kg x 13-15 MJ/kg HHV gives 22-25 GJ, so 16.6 GJ steam is about 70 % boiler efficiency, which is plausible. | low | open | State in D-011 which BLDS basis the 3.5 kg/kg applies to, and add the HHV/efficiency cross-check as the check of the steam figure. |
| 2026-10-28-pfd-lci-review#6 | process/reactions.yaml:76, DESIGN.md:209,219 | heats of reaction | The heats of reaction are "recalled" NBS values, not checked. For CALC, the formation enthalpies quoted (CaCO3 -1207.6, CaO -635.1, CO2 -393.5 kJ/mol) give +179.0 kJ/mol, not the +178.3 entered. They are marked assumed and enter no balance yet. | low | open | Check the values against the NBS tables (or NIST WebBook) with a locator before `cheme process furnace` uses them. Make the source values and the result agree. |
| 2026-10-28-pfd-lci-review#7 | lca/ (coverage) | LCI energy closure | `cheme assess lca --coverage` reports "energy closure 20.7 %" against a 5 % tolerance. Neither DESIGN.md nor lca/ explains what this residual measures or why it is acceptable. | low | open | Explain the figure in D-011/D-014 (no stream enthalpies, D-007), or say why the check does not apply. |
| 2026-10-28-pfd-lci-review#8 | lca/lca.yaml:47, lca/mappings.yaml:13 | unit basis of chemicals | `feed:CLO2` is 1 kg of 10 g/kg solution per kg pulp, but its `missing:` text leaves the basis open ("per kg of solution or per kg ClO2"). A later link per kg ClO2 would be 100x too high. Similarly, the H2SO4 override counts the 93 % solution against a shared entry whose basis is open (up to 7.5 %). | low | open | Fix the basis in the text: per kg ClO2, with 0.99 kg of process water as a separate exchange, or per kg solution. Convert H2SO4 to 100 % if the shared entry is on that basis. |
| 2026-10-28-pfd-lci-review#9 | DESIGN.md:40-55 | route comparison | #180 asks to compare industrial route alternatives. D-001 rejects only hardwood and an integrated mill. Other pulping routes are not addressed: sulfite, soda/AQ, mechanical/CTMP. | low | open | Add a short route comparison (one line each, with the reason kraft was chosen) to D-001. |
| 2026-10-28-pfd-lci-review#10 | process/PFD.xml | PFD readability | The generated PFD (build/PFD.png, read at full size) is about 9.4 m wide at 1:1 px. Long return lines run over most of the sheet (the condensate, filtrate and white-liquor recycles) with many crossings, so it is hard to follow. | low | open | Pin a tidier layout (`cheme process layout --pin`, `layout.pfd` in flowsheet.yaml) at the next stage. |
| 2026-10-28-pfd-lci-review#11 | runs/20261028-155500-design/report.md | process | The author's report says files were edited with `sed -i` twice and a Python heredoc once, which AGENTS.md forbids. The content validates and the balances reproduce, so the result is not affected. | low | accepted: self-reported, content re-checked by this review (validate, script re-run); review-agent | none beyond following AGENTS.md in later runs |

## Previous findings

None: this is the first review record of `processes/kraft-pulp-1/` (`ls reviews/` held only
README.md).

## Drawing

No P&ID exists, so there are no drawing-lint counts. `cheme validate` lints only P&ID sheets and
prints no `drawing` line for the generated BFD/PFD. The PFD was rendered (`build/PFD.png`) and
read as a whole: all 16 steps, 10 block frames, terminals and stream labels are present, and its
readability is #10. The BFD was not rendered.

## Checked and fine

- **Scope and boundary vs #180.** Bleached softwood kraft market pulp with full chemical recovery,
  gate-to-gate. Pulp and electricity are the co-products, as #180 asks. The boundary exclusions are
  explicit in the D-001 memo: wood room, bark boiler, ClO2 plant, ASU, effluent treatment and tall
  oil/turpentine. Capacity is declared as a normalisation basis, not a mill claim.
- **Nothing outside `processes/kraft-pulp-1/` changed** (merge-base diff).
- **Balances.** Every block and step closes in `cheme process streams`, and the independent
  script reproduces them. Hand checks:
  - wood: 0.9/0.44 = 2045 kg dry/ADt;
  - white liquor: AA 0.1068, sulfidity 35 %, causticity 81 % and reduction 92 % all follow from
    the white-liquor composition the script prints;
  - evaporation: 15 % to 80 % solids on 1689 kg BLDS gives 9.15 t water/ADt;
  - HP steam: 246 t/h = 3.5 x BLDS, 16.6 GJ/ADt above 398 K feedwater;
  - heat: 16.6 - 3.29 (913 kWh) - 1.68 (condensing tail) = 11.6 GJ process heat;
  - kiln: burner air 569 kg/ADt = 17.2 x 1.1 x 30 kg CH4; about 6.8 GJ/t CaO reburned;
  - dryer: 0.9 t water evaporated/ADt at 3.4 MJ/kg = 3.06 GJ.
- **Plausibility against general knowledge and the cited facts.** Bleached yield 44 %, BLDS
  1.69 t/ADt, power generation 913 and use 650 kWh/ADt, process heat 11.6 GJ/ADt, kiln fuel
  1.5 GJ/ADt, effluent 18 m3/ADt and recovery-boiler emissions are all in the usual ranges for a
  modern Nordic market mill and inside the BREF ranges quoted with locators. The low total NaOH
  is explained (D-008).
- **ASSUMED marking.** The design basis and DESIGN.md mark every engineering choice ASSUMED,
  every stream carries provenance A with a source, no kinetics or vendor data are invented, and
  the lumped components are declared as bookkeeping and not molecular identity (D-003).
- **Sources and licences.** Only facts and numbers with section and table locators (BREF 2015,
  Tran and Vakkilainen, AP-42). No tables, figures or passages are copied. The BREF Table 3.12
  comparison quotes four ranges as facts. Ullmann is marked as not accessed. No licensed
  database values.
- **LCI.**
  - Per functional unit (1 kg air-dry pulp); hand-checked against the flowsheet: chips
    4.0909 = 170,454/41,667, NaOH solution 0.0419, H2O2 0.006, NG 0.030, CW 1.266 kWh, export
    -0.263 kWh.
  - Mass residual 0.3 kg/h of 1.31e6.
  - No zero-filled or licensed background values. Every background is `missing:` with a
    description of the activity to connect and appears in gaps.csv. Uncharacterised emissions
    are gaps, not zero.
  - Per-process overrides sit in `lca/mappings.yaml`. Excluded emissions are declared with
    reasons.
  - The fossil/biogenic split in the inventory itself is correct (the problem is in the
    characterisation only, #1).
- **process.yaml** claims the lowest maturity and `validation: unreviewed`. Its description says
  how preliminary the work is and that the components are lumped.

## Not checked

- The BREF 2015 and Tran and Vakkilainen locators were not re-opened. The quoted ranges were
  checked for plausibility only.
- The wood composition and yields were not checked against a species assay (none was cited).
- The current state of those core issues (#2).
- The BFD drawing, and the equipment-list content beyond the links resolving.
- Atlas build (`build_lci.py`) of the mappings overrides.
- No layout, P&ID, HAZOP or control content exists at this stage.
