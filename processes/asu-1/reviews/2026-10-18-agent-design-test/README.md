# Agent design test, 2026-10-18

This plant was designed from an empty `plantcode init` repository (plantcode 0.3) by six staged
headless Claude Code sessions (model claude-opus-5-5), billed to an Anthropic API key with a hard
budget per session. After each stage an independent reviewer agent checked validation, rendered
sheets, process numbers and oxygen safety; its findings were handed to the next stage to fix first.

- Total API spend: $29.10 of a $50 cap.
- `stage-reviews.md`: every stage's cost, turns, reviewer scores and full findings.
- `prompts/`: the exact prompt of each stage (reproducible with the same plantcode version).
- The assessment below was written by an independent agent after the last stage and is not a
  human engineering review. Everything marked ASSUMED in the design files is a placeholder.

---

# ASU design test: final assessment

**Bottom line:** Six staged headless sessions turned an empty plantcode 0.3 repo into a complete first-pass basic-engineering draft for a 500 t/d GOX double-column ASU. It has 4 drawn P&IDs, consistent lists, 26 recorded decisions, a 3D layout and a stage sign-off. Total spend was **$29.11 of $50**. The final checks are clean: `validate` shows 0 errors and 0 warnings, and all 13 `check` gates pass. It is not yet a package an outside reviewer could sign: the last review's carry-over items are still open, the process has not been checked by simulation, every review was done by an agent, and the work sits on an unmerged branch.

Checked in this assessment, without modifying any tracked files (repo clean, HEAD `ffdb3ba` on `s6-basic-closeout`):
- `plantcode validate`: 12 files, 0 errors, 0 warnings, 3 info notices. `--fail-on warning` gives rc 0 and `fmt --check` gives rc 0.
- `plantcode check`: 7 concept gates and 6 basic gates, all ok.
- All 4 sheets rendered to PNG, plus 2 crops of P-04, and I looked at each one. Renders are in `(renders: run `plantcode render --png`)/`.

## 1. What was produced (repo `/Users/arturschweidtmann/Developer/repos/plantcode-asu`)

| Area | Content |
|---|---|
| Sheets (DEXPI 2.0.1, A3) | **P-01** main air compressor (MAC) and precooling: 11 equipment items, 18 lines, 12 instruments. **P-02** adsorber purification (TSA): 4 equipment, 5 lines, 14 instruments. **P-03** cold box: 9 equipment, 25 lines, 15 instruments. **P-04** products, storage and backup: 15 equipment, 28 lines, 22 instruments. |
| Lists | **39 equipment items, 76 lines, 63 instrument functions.** PSVs, XVs and silencers are drawn as DEXPI piping components, so they are not in these counts. Lists and sheets match (cross-checked by validate). |
| DESIGN.md | 531 lines: process description, block flow, mass balance, refrigeration and utilities, relief case list, decisions D-001 to D-026 |
| Design basis | `process/design-basis.yaml` with 23 values marked ASSUMED |
| Reviews | `reviews/2026-10-18-o2-safety-review.md` (EIGA 13/33/65 checklist), `reviews/2026-10-18-design-review-S4.md`, `reviews/2026-10-18-basic-engineering.md`. All three were written by the agents themselves. |
| Checks | `checks/checks.yaml` with ASU-specific gates (O2 safety, hydrocarbons, relief, relief case list). `checks/status.json` records the basic-stage sign-off. |
| Layout | Site plan: 200 x 150 m, 5 areas, vent area V1, 5 roads, racks PR1 and PR2. Building B1 is the MAC house, 36 x 26 m. Placement covers 38 of 39 items; E-3103 sits inside C-3102 on purpose. The 50 m cold box is shown as the two stacked columns. All dimensions are ASSUMED. |
| Generators | All four sheets are produced by scripts: `scripts/draft_P-0{1..4}.py`, `regen.py`, `fix_titleblock.py` |

## 2. Quality by area (scores per stage S1 to S6, then evidence)

**Process: 4/4/4/4/4/4.** Sound basis: double column without an argon column, oil-free GOX compressor outside the cold box, booster-braked expander exhausting into the LP column, GAN taken from the top of the HP column, air/O2 ratio of 5.2 at 94 % recovery (with a 90 % sensitivity case in D-018), about 215 kW of refrigeration giving about 940 kg/h of liquid. The reviewers caught the expander temperature mismatch in S1 and the 600 vs 470 kg/h mismatch in S4, and both were fixed. Still open:
- No simulation has checked the balance; it is shortcut figures only.
- D-017, the client's choice for the 22/27-day tank refill time, is open.
- Tank sizing is now shown (LIN: 372 m³ net in a 400 m³ working tank, about 440 m³ gross).

**O2 safety: 3/3/3/3/4/4.** This is the strongest result of the review loop. Real hazards were found and fixed:
- The shared LOX tank / 31 bara blowdown vent was split.
- A GOX suction vent was added.
- The compander got seal-gas trip PDSLL-3115 and an oil mist eliminator, so no oil reaches the LP column.
- Anti-surge was added on K-3101 and K-4102.
- True double block and bleed at the GOX and GAN battery limits, fail-closed tank outlets, TSVs, vacuum breakers.
- Hydrocarbon analyzers: AIA-3103 on the sump/LOX-3001, AIA-4121 on the LOX tank, AIA-3122 on the casing breather.

Still open:
- The GOX blowdown silencers S-4101/S-4102 are in V1, about 100 m from K-4101, and no rack carries that line (PR1 ends at x=182, y=68; V1 is at y=112-137).
- K-4101 is about 33 m from the columns, inside the 50 m toppling radius that D-026 itself states.
- LOX tanker fill valve HV-4146 is manual; remote-closing vs manual is left to HAZOP.
- No check valves on the backup risers. D-024 justifies this, but it needs HAZOP confirmation.
- EIGA clause numbers are missing, and the O2 review is a self-review.

**Drawing: 2/3/3/3/4/3.** From my reading of the renders:
- Strengths: sheets are legible, title blocks are correct (ASU-1, rev A, approval fields empty), off-page connectors are consistent, PSV discharges have atmosphere arrows, and P-02 has no crossings.
- Defects confirmed in the crops:
  - The `LALL-4108 / TSLL-4114 trip P-4102A/B…` note sits between PICA-4109 and LIA-4107, on the LOX tank T-4101, although it belongs to the LIN tank.
  - At the GOX battery limit, the labels XV-4133, XV-4132 and XV-4119 do not clearly attach to their valves, and the second BL block valve has no label.
- Other issues:
  - P-03: LOX-3001 crosses the GAN-3002 riser.
  - P-01: the CWR-1001 "DN 250" label is crossed by its own line.
  - P-04: the UIC-4103 measuring line crosses the GOX-4003 recycle loop.
  - Trips are written as literal text, not drawn as signal lines (validate flags them `label-literal`).
- The S6 review record claims "no overlaps of symbols or labels". The crops show this is not accurate.

**Consistency: 4/4/4/3/3/4.** Lists, sheets and layout match by validate. Each decision is recorded with its reason, and assumed values are marked ASSUMED throughout. `PROGRESS.md` has an entry for every change.

Gaps:
- All four XML files still have `Model name="example"`.
- `equipment/datasheets/` holds only a README.
- The silencer/PSV table in D-020 lives outside the lists, so validate cannot cross-check it.
- The S6 commits are on `s6-basic-closeout` and are not merged into `main`.

## 3. Cost

| Stage | Scope | Cost / budget | Turns | Time |
|---|---|---|---|---|
| S1 | Concept, lists, gates | $2.18 / $6 | 44 | 8 min |
| S2 | S1 fixes, P-01, P-02 | $5.85 / $8 | 74 | 19 min |
| S3 | P-01/P-02 fixes, P-03 | $4.66 / $7 | 40 | 20 min |
| S4 | P-03 fixes, P-04, reviews | $5.64 / $10 | 58 | 20 min |
| S5 | P-04 hardening, layout | $5.67 / $7 | 88 | 17 min |
| S6 | Close-out, sign-off | $5.11 / $6 | 167 | 12 min |
| **Total** | | **$29.11 / $50** | **471** | **about 97 min** |

## 4. What the workflow did well
- **Stage then independent review then carry-over.** Each review found real engineering defects and the next stage fixed almost all of them. Validate warnings fell from 124 to 90, 51 and then 0.
- **Discipline.** Every stage stayed within budget and none hit its cap. Every stage left a clean tree with one commit per logical change. ASSUMED marking, decision records and the progress log were kept up.
- **ASU-specific gates in `checks.yaml`** gave every stage concrete targets for O2 safety, hydrocarbons and relief.
- **Rendering and reading PNGs and crops** caught layout problems that a check on the XML text alone would miss.

## 5. Where agents struggled (friction for plantcode)
1. **Drafting.** All four sheets came from pyDEXPI generator scripts, which AGENTS.md calls a "last resort". Each fix regenerated the whole sheet; `copy`/`fragment` were not enough for drafting a new sheet.
2. **Label placement and crossings.** This took most of the review rounds. There is no lint for overlapping labels or crossing lines, and the agents' visual self-checks were unreliable, as the false "no overlaps" claim in S6 shows.
3. **Template and fmt bugs:**
   - `plantcode fmt` keeps rewriting the model name to `example`.
   - The pyDEXPI template title block came with "Oil & Gas, Inc. … APPROVED 2016" on the frames.
   - A declared sheet with no file is an error, so S1 had to create placeholder frames.
   - The 124 not-on-pid warnings at concept stage cannot be suppressed by stage.
4. **Model gaps:**
   - PSVs and silencers can't go in the lists, so a side table in DESIGN.md was needed.
   - Trips and cause-and-effect can only be literal text.
   - DEXPI class names are not validated.
   - The layout has no kind for a structure such as the cold box, no way to mark an item as intentionally unplaced (E-3103), and no check that vent lines reach the vent area.
5. **Weak gates.** The checks only grep for text, and an agent can write its own review file to pass the review gates.
6. **Operational:**
   - The repo folder was never trusted, so `.claude/settings.json` was ignored in every stage.
   - Stage task text fell one sheet behind actual progress (S3).
   - S6 used 167 turns and $5.11 of its $6 cap.
   - The sign-off was committed on a side branch.

## 6. Top 5 next steps to a reviewable basic engineering package
1. **Close the S6 carry-over, then merge.**
   - Move the LALL notes next to their own tanks and label each GOX battery-limit valve clearly.
   - Move the GOX vents near K-4101 or add rack PR3 to V1.
   - Add a tagged cold box structure, restate the toppling distances as measured values and justify or move K-4101.
   - Add the tanker fill bays and decide HV-4146.
   - Set PR2 over the road to at least 7 m.
   - Correct the "no overlaps" statement in the review record.
   - Then merge `s6-basic-closeout` into `main`.
2. **Verify the process.** Run a rigorous simulation (DWSIM/Aspen) of the columns, main heat exchanger pinch, expander refrigeration and 94 % vs 90 % recovery. Get the client's decision on D-017 (truck fill vs a larger expander).
3. **Complete control and safety documentation.** Draw signal lines or issue a cause-and-effect matrix for the trips (LALL, TSLL, TSHH, FI-4148 to UIC-4103, PIC-4102). Do a first SIL screening. Remove the remaining crossings: P-03 LOX-3001/GAN-3002, the P-01 CWR-1001 label, and the P-04 UIC-4103 line.
4. **Relief and hydraulics.** Size the relief valves against the case list, then do line hydraulics, pump NPSH and O2 velocity checks. Add EIGA 13/33/65 clause references, and have a human run the O2 safety review and HAZOP; the current reviews are all agent self-reviews.
5. **Prepare the issue set.**
   - Equipment datasheets, which are empty now.
   - Fix the `name="example"` model name; this likely needs a plantcode fix.
   - Fill the human checker fields.
   - Issue rev A as PDFs, with a `plantcode diff` report as the review baseline.

In parallel, fix the plantcode friction in section 5. The most valuable items are a label/crossing lint, the fmt model-name bug and stage-aware not-on-pid warnings.
