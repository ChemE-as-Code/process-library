---
topic: design
reviewed_commit: a5a06fde73a98e677a9cd8869cfcbaa067950730
scope: [DESIGN.md, process.yaml, process/design-basis.yaml, process/flowsheet.yaml, process/reactions.yaml, process/materials.yaml, process/BFD.xml, process/PFD.xml, scripts/acet_balance.py, lca/, equipment/equipment-list.yaml, runs/20261028-154007-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/acetaldehyde-1
merge: pending
---
# Review: design (concept PFD and preliminary gate-to-gate LCI), acetaldehyde-1

This is an independent review of the concept-stage case study for issue #183: acetaldehyde by the
one-stage Wacker process, 100 kt/a. I reviewed it as committed on `case/acetaldehyde-1` at a5a06fd,
which is 4 commits above the merge base with `origin/main`:

- b68efcd scaffold
- 59f17e5 concept PFD
- f5a888b design basis, DESIGN.md, lists and LCI
- a5a06fd run record

I did not write any of it, and I changed no design file.

I re-ran these commands myself at a5a06fd:

- `cheme validate`: `16 file(s): 0 error(s), 0 warning(s)`.
  - Infos: `cheme.decision-unknown` D-023 at `checks/checks.yaml:76` (a template comment), and
    `dexpi.load` port cycles on the BFD and PFD.
  - It compared 2 sheets (BFD, PFD) and 12 lists. It skipped the lists-vs-P&ID cross-checks
    because no P&ID exists, which is out of scope here.
- `cheme check`: every concept gate passes except `layout-plot-plan` (layout is out of scope).
  - The basic and detail gates that fail are outside this run's scope: `pids-exist`,
    `design-review`, `layout-3d`, `lifting-study`, `mto`, `layout-review`, `layout-detail`,
    `electrical`, `hvac` and `datasheets`.
  - This record is meant to satisfy `design-review`.
- `cheme maturity`: calculation maturity **none**.
  - `sourced.boundary` fails: the feed flows and compositions are `assumed` script results.
  - `balanced.model-basis` fails: R101's conversion and selectivities, and the V101, V102, C101,
    C201 and C202 outlets, are specified values without a source.
  - Warning `cheme.maturity-claim-exceeds` at `process.yaml:38`. DESIGN.md says this openly.
- `cheme process streams`: blocks RXN (78127.3), REC (152647) and DIS (122179 kg/h) are ok, and
  so are all 16 steps.
  - R101 extents in kmol/h: R1 287.709, R2 2.107, R3 2.409, R4 4.818, R5 0.451, R6 0.301,
    R7 0.377. They agree with the block extents.
- `cheme process propagate --check`: no output, so no stale or deviating calculated value.
- `cheme assess lca --coverage`: "partial screening carbon footprint".
  - 13 gaps. Every one is `missing:` and has a description of the background activity it should
    link to.
  - Mass, element and carbon-origin balances closed. DQR 2.33. Publication: public; publishable.
- `git diff --name-only origin/main...HEAD` (against the merge base): all 190 paths are under
  `processes/acetaldehyde-1/`.
  - The two-dot diff `origin/main..HEAD` also shows deletions in other folders, such as
    `processes/hydrogen-chloride-1/`. That is only because `origin/main` has moved on since the
    branch point; the branch does not touch those folders.
  - Merge or rebase onto current `main` before the PR is merged.

## Findings

The run task asked for findings numbered R-01 and so on. The ids below use the repository's
required form (`reviews/README.md`), with the R-number at the start of each finding.

| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | process/flowsheet.yaml (S26); scripts/acet_balance.py:92, 269-275; DESIGN.md D-008 | C-201 bottoms, Q07/Q08 | R-01: S26, the C-201 bottoms, is at 393.4 K and 200 kPa(a). That is the boiling point of pure water, yet the stream holds 11.6 wt% (4.5 mol%) acetaldehyde. With an effective acetaldehyde/water activity coefficient of about 3.5 (from its Henry constant) and its vapour pressure (about 15 bar at 393 K), the liquid would have a bubble pressure of about 420 kPa. At 200 kPa its bubble point is near 360 K. The script's live-steam enthalpy balances use `T["C1B"] = 393.4` for both columns. A bottoms temperature about 34 K lower moves about 4.3 MW from the C-202 condenser to the C-201 condenser: Q07 0.39 → about 4.7 MW, Q08 7.2 → about 2.9 MW. D-008's "reflux ratio of about 2.5" would then fall to about 0.4, which casts doubt on whether the scaled patent steam rate is enough for a 99.9 wt% product. Total cooling water, and with it the LCI, changes by under 1 %. | medium | open | Set the C-201 bottoms temperature to the mixture's bubble point (ASSUMED, with the activity or Henry basis stated), or choose a C-201 pressure consistent with 393 K. Rerun `scripts/acet_balance.py` and update S26, Q07 and Q08. Restate the reflux in D-008 and say whether the 13.46 t/h of live steam still gives a credible reflux. |
| 2026-10-28-pfd-lci-review#2 | lca/lca.yaml; lca/gaps.csv; DESIGN.md D-010/D-011 | Pd/Cu catalyst make-up | R-02: D-010 says the Pd and CuCl2 make-up is "a missing LCI exchange (not set to zero; an open item)". It does not appear in `lca/lca.yaml`, `gaps.csv`, the coverage limitations or `process.yaml`. The inventory therefore carries it as an implicit zero, and the coverage reads "13 gaps (every background)" as if the list were complete. Palladium has a very high burden per kg, so even g/t losses could matter at the percent level once backgrounds are linked. | medium | open | Make the omission visible in the generated outputs. Either add a `missing:` flow for the catalyst make-up (quantity unknown, with a description: palladium(II) chloride and copper(II) chloride make-up), or declare it as an explicit exclusion or cut-off with its reason, so that `gaps.csv` or the coverage limitations list it. Mention it in `process.yaml` `validation.notes`. |
| 2026-10-28-pfd-lci-review#3 | DESIGN.md SRC-1, SRC-2, D-004; process/design-basis.yaml assumptions | ethylene fate / selectivities | R-03: The selectivities set ethylene use, the largest LCI exchange. They come from the Wikipedia summary (SRC-1), which cites Ullmann's (SRC-2), and Ullmann's was not read. Issue #183 asks for the chapter version to be verified "before numerical use", with exact locators. The value is cross-checked against US 4,237,073 (677 vs 692 kg ethylene/t, within 2.2 %) and disclosed as O-1, so it is not misleading. Still, the main yield basis rests on a tertiary source. | medium | open | Audit Ullmann's §4.3.1 (and §5 for the product specification), record edition, section, page and table, and replace the Wikipedia locator as the basis of D-004. Keep SRC-1 only as a pointer. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md D-004; process/reactions.yaml R3 | CO2 formation | R-04: The source gives "0.8 CO2" per 100 mol of ethylene fed. D-004 reads this as 0.8 mol of ethylene burnt (R3 extent 2.41 kmol/h, so 4.8 kmol/h CO2). If the source counts moles of CO2, only 0.4 mol of ethylene burns: CO2 formation halves and the oxygen demand drops by about 1.2 %. The effect on the boundary flows is small, but it changes the purge and light-ends CO2 and the cycle-gas composition. | low | open | Settle the reading in the O-1 audit. Until then, state in D-004 that the "as ethylene" reading is an interpretation (ASSUMED) and give its effect. |
| 2026-10-28-pfd-lci-review#5 | equipment/equipment-list.yaml:11, 37 | R-101, C-202 design pressure | R-05: D-012's rule is the highest operating value + 10 %, and at least + 2 bar. R-101 is listed at 5 barg, but its feed enters at 500 kPa(a) (about 4 barg), which gives at least 6 barg. C-202 is listed at 3.5 barg, but its bottoms are at 300 kPa(a) (2 barg), which gives at least 4 barg. Both values sit below the stated rule. | low | open | Apply the D-012 rule to the bottom (highest) operating pressure of both items, or record why the top pressure governs. |
| 2026-10-28-pfd-lci-review#6 | process/flowsheet.yaml S28/S29 | E-203 | R-06: S28 (270 kPa(a)) passes the product cooler E-203 and leaves as S29 at 300 kPa(a). The pressure rises across a cooler with no pump step. The product pump's power is lumped into Q04 on C202. | low | open | Add the product pump as a step, or give S29 a pressure at or below that of S28. |
| 2026-10-28-pfd-lci-review#7 | DESIGN.md D-007; process/design-basis.yaml assumptions | cycle-gas O2 8 mol% | R-07: "8 mol% O2, below the limiting oxygen concentration of ethylene" is a safety-relevant claim with no source and no margin. The limiting oxygen concentration falls with temperature and pressure, and the cycle gas is at 308-342 K and 370-520 kPa(a). The value is marked ASSUMED, but the reason given for it is unsupported. | low | open | Cite a limiting-oxygen-concentration source for ethylene with CO2/Ar diluent at these conditions and state the margin, or reword the reason as "to be confirmed in the safety review". |
| 2026-10-28-pfd-lci-review#8 | process.yaml:4-10, 37-38 | summary / maturity | R-08: `maturity: concept` is the lowest value the schema allows, and the comment explains this. However, the `summary` and `validation.notes` that the Atlas shows say "Concept stage" and never mention that `cheme maturity` reaches calculation maturity **none** and warns `cheme.maturity-claim-exceeds`. Only DESIGN.md says so. | low | open | Add "calculation maturity: none (cheme maturity: feed flows and separator/reactor specifications not sourced)" to `validation.notes`, and preferably to the summary. |
| 2026-10-28-pfd-lci-review#9 | process.yaml:57 | chemistry outputs | R-09: `process.yaml` lists the purge (product:PURGE) as `carbon-dioxide, role: emission`. `lca/lca.yaml` treats the same purge as a waste to thermal oxidation, not a direct emission. The purge is 43 wt% CO2, 32 wt% ethylene, 13 wt% Ar and 7 wt% O2. The Atlas entry contradicts the LCI boundary. | low | open | Give the purge `role: waste` (purge gas to a thermal oxidiser), or drop the entry until a registry slug for vent gas exists. |
| 2026-10-28-pfd-lci-review#10 | DESIGN.md source register (SRC-1, SRC-3, SRC-4) | locators | R-10: The patent locators are "description" and "comparative example", with no column and line numbers. SRC-1 is located only by section. The water, steam and waste-water rates of D-006 and the whole LCI water basis rest on SRC-3. Issue #183 asks for exact locators. | low | open | Add column and line numbers (or paragraph numbers) for each fact taken from US 4,237,073 and US 7,339,084. |
| 2026-10-28-pfd-lci-review#11 | lca/manifest.json:158-167; DESIGN.md D-011 | energy closure | R-11: The coverage report and the published manifest print "energy closure 0.0%". The tool lists "heat rejected" under inputs, and the outputs are empty because no product energy content is given. A reader can take this for a failed energy balance. D-011 does not explain it. | low | open | Explain the 0.0 % in D-011 (no product energy content given, so closure is not evaluated), and report the input/output classification of heat rejected to cheme-as-code. |
| 2026-10-28-pfd-lci-review#12 | checks/checks.yaml:76 | template comment | R-12: The template's example `accept:` comment cites D-023, which does not exist in DESIGN.md (info `cheme.decision-unknown`). It is template text, but it leaves an info in every validate run. | low | open | Neutralise the example decision id, or report the template issue to cheme-as-code. |

No critical or high finding.

## Previous findings

| id | finding | severity | status | evidence |
|---|---|---|---|---|

None: no earlier review record exists for this process. At a5a06fd, `reviews/` held only
README.md.

## Drawing

- `process/BFD.xml` and `process/PFD.xml` are **generated** by `cheme process build`.
  - `cheme validate` reports no `generated-edited` finding and 0 warnings.
  - It prints no `drawing <sheet>:` line for these process sheets, so no lint counts are
    available.
  - There are no P&IDs (out of scope).
- I rendered the whole PFD (`build/PFD.png`) and read it at full-sheet scale.
  - All three blocks (RXN, REC, DIS) are present, with their steps, the 14 terminals (8 feeds, 6 products) and the
    material and energy streams labelled.
  - Cosmetic only: long generated routes around the blocks, and several crossings of the
    utility and energy lines. Pinning `layout.pfd` would tidy this; it is not a finding at
    concept stage.
- I did not tile the PFD or render the BFD.

## Checked and fine

- **Route and boundary** match the run's case notes and issue #183: one-stage Wacker with oxygen,
  PdCl2/CuCl2, scrubbing and two columns, chlorinated by-products, and ethylene and oxygen as
  boundary feeds. The route comparison with ethanol and acetylene is deferred as O-6. That is
  allowed by the issue's bounded first-job contract and stated in D-001.
- **Balances.** Every block and step closes in cheme. My recomputation of the element and
  chlorine bookkeeping agrees:
  - The HCl make-up (5.57 kmol/h) equals the Cl leaving as chloroacetaldehyde, chloroethane and
    chloromethane (4.82 + 0.45 + 0.30 kmol/h).
  - Ethylene lost unconverted is 2.83 kmol/h in the purge plus 0.48 kmol/h in the light ends,
    which is 1.10 % of fresh ethylene, as D-007 states.
  - Product yield is 283.5 / 301.4 kmol/h = 94.1 mol %.
- **Specific consumptions are plausible for this technology:**
  - Ethylene 0.6765 kg/kg against a stoichiometric minimum of 0.637 kg/kg, which corresponds to
    94.1 % yield.
  - Oxygen 0.410 kg/kg (stoichiometric 0.363 kg/kg, plus by-products and the O2 in the purge).
    The patent example gives 0.408 kg/kg.
  - The water and steam rates are scaled correctly from SRC-3 (×12.5/13): 14.4, 74.5, 1.44, 1.44,
    2.88 and 13.46 t/h. The sum of water inputs equals the patent's 112.5 m3/h waste water.
- **Energy figures:**
  - The heat of reaction is consistent with ideal-gas formation enthalpies (R1 about −218 kJ/mol;
    19.2 MW in total).
  - The reactor off-gas water (about 49 mol% at 400 kPa and 403 K) is consistent with a boiling,
    salt-depressed catalyst solution.
  - My compressor power check (k ≈ 1.3, η 0.75, 1372 kmol/h, pressure ratio 1.41) gives about
    455 kW against 461 kW.
  - E-201/E-202 are feasible: 8.5 MW on both sides, approach temperatures 23.6 K and 26 K.
  - Q08 is consistent with its stated reflux ratio for the 393.4 K feed assumed. R-01 questions
    that temperature.
- **Waste water.** Chloroacetaldehyde 443 mg/kg gives 200 mg/kg organic Cl and 360 mg/kg
  aldehyde, as in SRC-3. The acid under-estimate is disclosed in O-4.
- **Oxygen feed.** Oxygen enters the reactor directly (S03 → R101). It is not mixed with ethylene
  in M101.
- **LCI:**
  - Functional unit 1 kg PROD.
  - Inputs 9.7941 kg = outputs 9.7942 kg per kg. This matches the flowsheet's boundary streams
    divided by 12 500 kg/h.
  - Each exchange cites its stream ids.
  - No zero-filled and no licensed background values. All 13 backgrounds are `missing:` with a
    description.
  - The purge, light ends, side draw and waste water are wastes to treatment.
  - The per-process overrides (oxygen, LP and MP steam with `atlas: false`) are in this folder's
    `lca/mappings.yaml`, not in the shared file.
- **Sources and licences.** In DESIGN.md, `process.yaml` and the YAML comments I found no copied
  table, figure or passage. Facts are restated with sources. Ullmann's is honestly declared as
  not read. The secondary ChemicalBook figure is labelled "plausibility only".
- **Honesty.** `process.yaml` says `validation.status: unreviewed` and states its limitations,
  apart from R-08. The run report agrees with what I re-ran.
- **Scope.** Nothing outside `processes/acetaldehyde-1/` changed against the merge base.

## Not checked

- I did not read Ullmann's (licensed) or re-read the patents and the Wikipedia article. I checked
  the facts attributed to them only for internal consistency and arithmetic, not against the
  source text.
- I did not check for copied text by comparing against the sources, only by reading our files.
- The R-01 bubble-point estimate is mine: an activity coefficient of about 3.5 from Henry's law,
  and Clausius-Clapeyron with ΔHvap 25.8 kJ/mol. It has no rigorous flash behind it, because no
  property package covers the system (core #315).
- Not re-run: `scripts/acet_balance.py` (`cheme run`) and the library catalog/LCI build.
- The line list and instrument list beyond what `cheme validate` checks.
- The BFD rendering; tiles of the PFD.
- Out of scope for this stage: P&IDs, layout, HAZOP, datasheets and TEA.
