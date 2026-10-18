# Lessons from the run and the issues that track them

**State of the ASU repo:** the S6 branch is already merged into `main` (2a6c413), and the run record is committed (21a7495, `reviews/2026-10-18-agent-design-test/`). No new merge is needed. The independent reviewer prompt is missing from `prompts/` and should be added to the record.

**Merged / restructured:** the 7 dropped candidates were folded into their lower-numbered duplicates (geometry lint, planned sheets, generator lifecycle, on-sheet gate). The title-block issue was split in two: a small P1 **bug** `fmt: keep the Model name and uri` (one-line fix: pass `DexpiXmlModelMetadata` from the parsed root) and `sheet new / sheet meta` (template clean-up plus commands). Cross-references to candidate numbers (#4, #12, #32, ...) were replaced by issue names, because plantcode PRs #1-#5 would otherwise auto-link. Facts corrected: plant capacity 500 t/d (not 1,000); generator scripts are 1,318 lines and stdlib-only (they do not use pyDEXPI); P-04 is 53,949 lines. Labels used: only the existing `bug`, `enhancement` and `documentation`. Order: 7 P1, then 16 P2, then 5 P3.

**What the run teaches, and where each lesson goes:**
1. **Drafting a sheet from scratch still means writing a script.** pyDEXPI cannot be imported in a plant repo, `fragment` has no equipment, instrument, signal or off-page kinds, and there is no public builder API. Issues: `plantcode run` (P1), fragment kinds (P1), authoring API, shape catalogue, generator lifecycle (`regen` and a drift check, because the S6 hand edit to P-04 no longer matches `draft_P-04.py`).
2. **Editing an existing sheet is slow and fragile.** `copy` leaves wrong sensor letters and duplicate inner tags (P1 bug), and there are no move, rename or set commands. These need 53 Edits on a 54k-line file. Shell rewrites were denied (34 denials), and the template permissions were ignored in an untrusted folder. Issues: copy, move/rename/set, headless permissions.
3. **Visual self-review is unreliable.** The S6 record claimed "no overlaps" and was wrong. Issues: drawing-geometry lint with crop boxes (P1), evidence-based review and drawing gates, `render --tiles`, checks on tags named in literal labels and off-page texts.
4. **Gates and sign-off are too easy to pass.** They check with grep or that a file exists, an agent can sign off its own review, and nothing records provenance. Issues: sign-off provenance (P1), `kind: review`, `kind: on-sheet`, finding IDs with status, template placeholder metadata and approval fields, branch/merge policy.
5. **Safety items fall outside every check.** This covers silencers and PSVs that no list holds, vent routing with no rack, broken spacing rules (the compressor is 32 m away against the 50 m required), and trips kept only as text. Issues: piping-items list, layout line-route, layout separations, interlocks/C&E.
6. **Stage friction.** The concept stage forced empty frames and 124 warnings, sample title-block data ended up on the sheets, and stage tasks were built by hand from reviewer prose. Issues: planned sheets with `--ignore`/`--only`, `sheet new` with the fmt fix, `plantcode status`, a packaged agent-run runner with reviewer prompts, and a datasheet format.

## Issues filed (process-intelligence-research/plantcode)

- [#6](https://github.com/process-intelligence-research/plantcode/issues/6) plantcode run: run generator scripts in plantcode's interpreter so pyDEXPI imports work
- [#7](https://github.com/process-intelligence-research/plantcode/issues/7) fragment: add equipment, nozzle, instrument, signal (actuating system), off-page and note kinds
- [#8](https://github.com/process-intelligence-research/plantcode/issues/8) copy: retag sensor letters, rename inner tags and fluid code, and report duplicate tags
- [#9](https://github.com/process-intelligence-research/plantcode/issues/9) fmt: keep the Model name and uri instead of resetting them to 'example'
- [#10](https://github.com/process-intelligence-research/plantcode/issues/10) sheet new / sheet meta: create sheets with a real title block; remove pyDEXPI sample data from the template sheet
- [#11](https://github.com/process-intelligence-research/plantcode/issues/11) validate: drawing-geometry lint for P&IDs (lines through labels, crossings, overlapping and misplaced labels) with crop boxes
- [#12](https://github.com/process-intelligence-research/plantcode/issues/12) check --write: record stage sign-off provenance and refuse on dirty tree, failing gates or a self-signed review
- [#13](https://github.com/process-intelligence-research/plantcode/issues/13) authoring: expose the fragment/copy builders as a documented Python API for generator scripts
- [#14](https://github.com/process-intelligence-research/plantcode/issues/14) Edit commands for existing objects: plantcode move, rename and set
- [#15](https://github.com/process-intelligence-research/plantcode/issues/15) Shape catalogue: add compressor, expander, column, filter, silencer, cooler, vaporizer and flat-bottom tank symbols
- [#16](https://github.com/process-intelligence-research/plantcode/issues/16) Generator scripts: declare generated vs hand-maintained sheets, add plantcode regen and a drift check
- [#17](https://github.com/process-intelligence-research/plantcode/issues/17) Planned sheets and sheet-scoped not-on-pid: no empty frames or warning flood at concept stage
- [#18](https://github.com/process-intelligence-research/plantcode/issues/18) review skill and gates: back drawing claims with lint counts, and let validate gates require zero unaccepted drawing warnings
- [#19](https://github.com/process-intelligence-research/plantcode/issues/19) validate: warn on template placeholder metadata and on approval fields without a sign-off
- [#20](https://github.com/process-intelligence-research/plantcode/issues/20) Lists: add tagged piping components (silencers, safety valves) with P&ID cross-check and layout placement
- [#21](https://github.com/process-intelligence-research/plantcode/issues/21) layout validate: check that lines between placed items have a rack route, using the line list
- [#22](https://github.com/process-intelligence-research/plantcode/issues/22) layout validate: declared minimum separations and keep-clear radii
- [#23](https://github.com/process-intelligence-research/plantcode/issues/23) Interlocks: structured cause-and-effect list cross-checked by validate, instead of literal trip text
- [#24](https://github.com/process-intelligence-research/plantcode/issues/24) check: add an on-sheet gate kind that queries tags and classes in the model instead of grep
- [#25](https://github.com/process-intelligence-research/plantcode/issues/25) check: add a review gate kind that checks reviewed commit, reviewer kind and staleness
- [#26](https://github.com/process-intelligence-research/plantcode/issues/26) review skill: stable finding ids, a status column and a Previous findings section for carry-over
- [#27](https://github.com/process-intelligence-research/plantcode/issues/27) docs: package a repeatable staged agent design run (runner, stage and reviewer prompts, budgets)
- [#28](https://github.com/process-intelligence-research/plantcode/issues/28) Headless agent runs: document workspace trust and steer agents away from sed -i, heredocs and compound commands
- [#29](https://github.com/process-intelligence-research/plantcode/issues/29) validate: check tags named in literal labels and off-page connector texts
- [#30](https://github.com/process-intelligence-research/plantcode/issues/30) render --tiles: overlapping crop sweep so visual review covers the whole sheet
- [#31](https://github.com/process-intelligence-research/plantcode/issues/31) plantcode status [--json]: one summary of sheets, findings by sheet, gates and sign-off
- [#32](https://github.com/process-intelligence-research/plantcode/issues/32) Template: define branch and merge policy for stage work and sign-off
- [#33](https://github.com/process-intelligence-research/plantcode/issues/33) Template: datasheet format and generic concept and detail gates
