---
topic: design
reviewed_commit: 04ddb0e880554c1b7b12259a609b3567b4e20280
scope: [DESIGN.md, process/design-basis.yaml, process/materials.yaml, process/reactions.yaml, process/flowsheet.yaml, process/BFD.xml, process/PFD.xml, equipment/equipment-list.yaml, piping/line-list.yaml, lca/, process.yaml, scripts/ib_balance.py, runs/20261028-150003-design/report.md]
reviewer: review-agent
reviewer_kind: agent
branch: case/isobutene-1
merge: pending
---
# Review: isobutene-1 concept PFD and preliminary LCI (issue #165)

An independent review of the concept run on `case/isobutene-1` (5 commits on `origin/main`,
`1d662b2..04ddb0e`). It covers the design basis, the balanced flowsheet with its generated BFD and
PFD, the equipment and line lists, the foreground LCI and the Atlas manifest. I did not write any
of it, and I changed no design file in this review.

Commands I re-ran myself at `04ddb0e`:

- `cheme validate`: 16 files, 0 errors, 0 warnings. It compared BFD and PFD and 12 lists. The
  P&ID cross-checks were skipped because there is no P&ID.
- `cheme check`: every concept gate passes except `layout-plot-plan`. The basic and detail gates
  `pids-exist`, `design-review`, the layout gates, `mto`, `electrical`, `hvac` and `datasheets`
  fail. See #6.
- `cheme maturity`: calculation maturity none, with the warning `cheme.maturity-claim-exceeds`
  against `maturity: concept`. See #7.
- `cheme process streams`: every block (RXN, IBPUR, MEOHREC) and all 18 steps are `ok`. The
  reactor extents are CRACK 112.265, DMEF 1.12 and DIM 0.112 kmol/h.
- `cheme process propagate --check`: no output, so it found no deviation and no stale value.
- `cheme assess lca --coverage`: the mass, element and carbon-origin balances are closed. It
  reports 8 gaps, each with a description, a partial screening result, and "publishable".

## Findings
| id | sheet | item | finding | severity | status | proposed action |
|---|---|---|---|---|---|---|
| 2026-10-28-pfd-lci-review#1 | DESIGN.md:88 | D-005 C8 selectivity | The C8 basis is attributed to "the same effluent" (Example 2, Table 11 of US 8,633,345 B2) with a C8/isobutene molar ratio of about 0.0007. My reading of the patent finds no C8 hydrocarbons in Example 2's reactor effluent. The C8 value sits in Example 1 (Table 6, about 0.06 wt% of the effluent, molar C8/isobutene about 0.0005). The other locators I checked are right: the DME/isobutene molar ratio of about 0.010 (Table 11), the high-boiler bottoms at about 62 % MTBE (Table 10), methanol at about 99 wt% from the methanol column (Table 12), and the lab example at 280 C / 0.7 MPa / 98 % (Table 6). The design value 0.001 stays conservative either way. | low | open | Correct the locator in D-005 to the table that holds the C8 figure, and keep 0.001 ASSUMED. |
| 2026-10-28-pfd-lci-review#2 | DESIGN.md:162 | D-009, Q7 (C-201 reboiler) | D-009 says C-201 (bottoms 394 K) "needs MP steam". LP steam at 450 kPa(a) condenses at 420.8 K, which leaves a 27 K approach, above the 10 K `min_approach` the flowsheet declares for LPS. So the stated reason does not hold. LP steam would serve C-201, and MP would remain only for C-101 (436 K). The LCI is barely affected: both levels map to `steam-heat`, and the background does not tell the levels apart. The split 1.98 MJ MP / 0.48 MJ LP per kg is misleading, though. | low | open | Either move Q7 to LPS, or give the real reason for MP (for example, reboiler area or fouling) in D-009. |
| 2026-10-28-pfd-lci-review#3 | lca/lca.yaml:74 | cutoff `hot-oil-and-fans` | The heater fan and hot-oil pump power (about 30 kW, 240 MWh/a, ASSUMED) is cut off. It is about twice the electricity that is in the inventory (`feed:POWER` 15.8 kW). A cut-off is meant for flows that do not matter next to what is counted. The impact on climate is small compared with 2.2 MW of fired heat and 4.3 MW of steam, but the power exchange is understated by a factor of about 3. | low | open | Add the 30 kW to `feed:POWER` (or as a separate Q stream) as ASSUMED, instead of a cut-off. |
| 2026-10-28-pfd-lci-review#4 | DESIGN.md:35 | D-001 route attribution | The text says "the issue names this route". Issue #165 leaves the route as "not selected" and asks for separation from mixed C4 streams to be compared, as a case, with on-purpose production. The MTBE route was named in the run's task (`runs/20261028-150003-design/task.md`, line 21). The route memo also does not discuss the mixed-C4 separation cases the issue proposes, beyond the remark that distillation alone cannot do it. | low | open | Attribute the route choice to the task (and the patent), and add one line on the issue's comparison of C4 separation cases as an open item (I-0x). |
| 2026-10-28-pfd-lci-review#5 | process.yaml | summary / description | The manifest states "99.97 wt% isobutene" without the caveat that the design basis gives: linear butenes and C5 (from MSBE and C5 in technical MTBE) are outside the model because the feed is pure MTBE (D-003). In a real plant, those butenes, not MTBE, DME or methanol, decide polymer grade. The same pure feed understates the C-101 duty (I-04). A catalog reader sees only the manifest. | low | open | Add "pure MTBE feed; linear butenes not modelled (D-003)" next to the purity in `process.yaml`. |
| 2026-10-28-pfd-lci-review#6 | checks/checks.yaml:91 | gates | `cheme check` fails the concept gate `layout-plot-plan`, plus the basic and detail gates for P&IDs, the design review, layout, MTO, electrical, HVAC and datasheets. These were out of this run's scope (task.md). The report states it for the plot plan. This record is the independent `design` review, but the gate also needs the next review to stay current. The concept stage cannot be signed off while `layout-plot-plan` fails. | low | open | Either do the plot plan before a concept sign-off, or have a human accept the gate as out of scope for this library case. No change to the design is needed for the merge. |
| 2026-10-28-pfd-lci-review#7 | process.yaml:38 | maturity | `cheme maturity` reports that the evidence supports no design maturity and warns `cheme.maturity-claim-exceeds` against `maturity: concept`. The causes are the unsourced feed and capacity, and specified separator splits. `concept` is the lowest value the schema allows. `validation.notes` and the comment above `maturity:` say all of this honestly. This is recorded only so the warning is tracked, not as a misstatement. | low | open | Keep the claim and the note. Lift `sourced-boundary` with a sourced capacity and MTBE assay (I-01), or raise the missing "none" level with the library schema. |

## Previous findings
None. This is the first review record of isobutene-1: `reviews/` held only README.md, and no
earlier record has an open finding.

## Drawing
BFD and PFD are generated by `cheme process build` from `process/flowsheet.yaml`. They are not
hand-maintained, and `cheme validate` reports no `drawing` count line for them. There are 0
errors and 0 warnings, and the `cheme.generated-edited` check is not raised. I rendered the full
PFD (`build/PFD.png`) and read it: the three blocks, all 18 steps and the boundary feeds and
products are present, and the stream ids match the stream table. The sheet is very wide (about
7:1). Labels are small at full-sheet scale but there is no overlap I could see. I did not read
it in tiles. No P&ID exists (out of scope).

## Checked and fine
- **Scope and route.** MTBE back-cracking over an acidic (Mg-doped silica-alumina) catalyst. The
  plant has a heavy-ends column, an isobutene column, a water wash, a drying/DME column, a
  methanol column with MTBE/methanol recycle, and wash-water regeneration. MTBE is a boundary
  feed, linked to methanol-1. Isobutane dehydrogenation is stated as a variant and not designed.
  This matches the run's task. Nothing outside `processes/isobutene-1/` changed
  (`git diff --name-only origin/main..HEAD`).
- **Patent facts (US 8,633,345 B2, checked against the full text).** The design takes these
  from the patent and they match:
  - cleavage at 150-500 C (200-400 C preferred) and 0.05-2 MPa;
  - WHSV 1-3 1/h preferred;
  - MTBE conversion 40-99 % per pass (85-95 % more preferred), about 94 % in Example 2 at
    305 C / 0.85 MPa;
  - DME selectivity below 10 % (below 4 % preferred);
  - Example 2 columns: K2 at 0.95 MPa, R 4.2; K3 at 0.65 MPa, R 0.7; K4 at 0.1 MPa, R 1.9;
  - drying column reflux below 40 preferred;
  - extraction with 4-16 theoretical stages at 15-50 C, targeting below 30 ppm methanol;
  - product purity above 99.9 wt% achievable;
  - endothermic cleavage.

  All of these are cited in our own words, with locators. No table, figure or passage is
  copied. The patent's technical MTBE table is referred to, not reproduced.
- **Thermochemistry.** I recomputed the gas-phase heat of reaction:
  -17.6 - 200.7 + 283.7 = +65.4 kJ/mol. From the materials' S298 I get ln K(553 K) of about
  6.9, against cheme's 6.81. The equilibrium conversion of pure MTBE at 7.5 bar is
  sqrt(120/121), about 0.996, so 0.90 per pass is kinetically limited, as D-005 says. The
  reactor duty is 112.27 x 63.5 MJ/kmol, minus the small exotherms of DME and C8 formation,
  which gives about 1970 kW. That matches Q5.
- **Balances.** Every block and step closes.
  - Yield: 99.0 mol% on fresh MTBE. The losses I traced add up to about 1.1 kmol/h: MTBE in the
    heavies 0.21, isobutene to C8 0.22, isobutene in the C-403 vent 0.64, and dissolved in the
    C-402 vent about 0.03. That agrees with 112.49 - 111.37.
  - Water: in, 44.4 make-up + 20.2 formed. Out, 48.8 purge + 15.9 in the methanol + 0.05 in the
    product. Both sides are about 64.7 kg/h.
  - Methanol: the co-product, 3525 kg/h of methanol, equals the 110.0 kmol/h net formed.
  - Product impurities: MTBE 176, DME 58, methanol 26 and water 8 ppm(w), consistent with the
    stated splits.
- **Duties.** I spot-checked them with my own latent and sensible heats, and all agree within
  10 %:
  - C-101 reboiler about 1.97 MW (2013 given), partial condenser about 0.39 MW (376);
  - E-102 about 2.74 MW (2768);
  - C-201 condenser about 1.06 MW (1062) and reboiler about 1.36-1.42 MW (1423);
  - C-301 condenser about 0.42 MW (455);
  - C-402 condenser about 0.13 MW (125) and reboiler about 0.22 MW (210);
  - C-403 condenser about 0.25 MW (261) and reboiler about 0.38 MW (383);
  - H-101 superheat about 0.20 MW (222);
  - P-101 about 5.6 kW (6.7).

  Total condensation of the effluent at 700 kPa and 313 K is feasible, even with the IB/MeOH
  non-ideality. Per kg isobutene: 2.46 MJ of steam, 1.26 MJ of fired heat and 3.05 MJ of
  cooling. That is plausible for a gas-phase cracker whose whole feed is evaporated.
- **Marking of values.** Key values are ASSUMED or sourced with their decision. The method
  limits are stated honestly: ideal Raoult with no qualified package, about ±30 %
  on the duties. No kinetics are invented.
- **LCI.**
  - It is per 1 kg isobutene, by mass allocation. I recomputed the isobutene share,
    6250 / 9911.5 = 0.6306, and the MTBE per FU, 1.587 x 0.6306 = 1.0004 kg.
  - The unallocated mass is 9960.29 in and 9960.29 out, consistent with the flowsheet's
    boundary streams.
  - No zero fills and no licensed background values. All 8 backgrounds are `missing:`, each with
    a description of the activity, and listed in `lca/gaps.csv`.
  - The per-process overrides sit in `lca/mappings.yaml`. They use entries that exist in the
    shared `lci/mappings.yaml` (`heat-natural-gas`, `steam-heat`, `water`, `wastewater`), as
    hda-1 does.
  - `process.yaml` has `lca.source: none`, so the all-gap 0 in `results.csv` does not reach the
    catalog.
  - The exclusions are declared with reasons: heater combustion, storage, fugitive emissions,
    and fuel use by the users.
- **Equipment list.** The design pressure and temperature follow D-010. The run report reports
  the gates and the open items faithfully.

## Not checked
- The column, wash and split specifications against rigorous VLE/LLE (NRTL/UNIQUAC with sourced
  binaries). That is not possible until core's property-package qualification; the azeotrope-limited values (2.5 wt% and
  14 wt% methanol, the 0.08 wt% water saturation) are estimates (I-02).
- `scripts/ib_balance.py` line by line. I checked its results against hand calculations only.
- The line-list DN against velocities.
- The Atlas LCI build (`scripts/build_lci.py`), which needs openpyxl (I-08).
- P&IDs, layout, datasheets and HAZOP: out of scope for this stage.
- The PFD tile sweep (only the full-sheet render was read).
- Ullmann (licensed, metadata only).

Merge pending: no critical or high finding is open. The seven low findings can be closed in
follow-up commits. The merge is for a human, not the author.
