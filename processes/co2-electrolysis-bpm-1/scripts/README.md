# Scripts

Generator scripts for P&ID sheets. Run them with `cheme run scripts/<script>.py ARGS`: it
uses cheme-as-code's own interpreter, where pyDEXPI and the authoring API `chemeascode.domains.piping.authoring`
import (`python3` and `uv run python` do not have them here). `example_draft.py` shows the API.

A sheet is in one of two states, set in `plant.yaml`:

- **generated**: the sheet's entry has `generator: {script: scripts/draft_<sheet>.py, frame:
  <commit or file>}`. The script is the source. Change the script, then `cheme regen
  <sheet>` (frame -> script -> `fmt`); never edit the XML by hand. `regen` refuses a sheet that
  was edited by hand and names the items; `cheme validate` warns `generated-sheet-drift`.
- **hand-maintained** (no `generator:`): the XML in `pid/` is the source; a script here is
  provenance only and is never rerun over the sheet (validate notes it as
  `generator-undeclared`).

To move a sheet from generated to hand-maintained: `cheme regen --detach <sheet>`, then
edit the XML (skill `pid-edit`). To move back, put the hand edits into the script until
`cheme regen <sheet>` reproduces the sheet, then declare the generator.

A generator takes the sheet file as its argument and edits it in place, starting from the
frame (for a new sheet: the one `cheme sheet new` wrote).

The pilot skids of #330 (DESIGN.md D-007 to D-023):

- `regen.py`: the single rerun command, `cheme run scripts/regen.py --duration H
  [--scratch DIR] [--uncertainty] [--record]` or `--check [--duration H]`. It carries the design
  basis through `cheme process cell`, `duty`, `stack --write`, `datasheets draft`, the balance
  and `process build`, `layout build`, `datasheets fill` per case, `layout render`, `control
  report`, the duty plots and comparisons and the envelope check into every value and figure that
  depends on the campaign duration (steps 1 to 13), then checks the conditional invariants,
  writes the calculation record `results/scenarios/<H>h/record.json` and, once both scenarios
  have one, the resize report `results/resize-1000h-10000h.{json,md}` and README.md's results
  table (steps 14 to 17). It also writes the calculated setpoints of `control/loops.yaml`
  (step 9). An infeasible skid is a result, recorded with its reasons, never a tool error
  (DESIGN.md D-023).
  `--uncertainty` adds the bounding runs (step 15), `--record` the session record (step 18). It
  owns the draft datasheets (D-020). `--check` regenerates every design scenario in a temporary
  copy and reports any record, figure, model file or datasheet that differs (exit 3). `--scratch
  DIR` runs in a copy and copies the scenario's figures and records back (D-021, D-022).
- `_results.py`: the arithmetic of steps 14 to 17 (invariants, record, resize report) and the
  uncertainty figures, plain SVG; no core import.
- `_lca.py`: regen step 20, the LCA of both skids (#331, DESIGN.md D-024 to D-027): the values
  `lca/lca.yaml` takes from the design, `cheme assess lca --write` (and `--case skid-b`),
  `lca-scenarios --write`, and the scenario's LCA record `results/scenarios/<H>h/lca.json` with the
  reconciliation against the duty totals (E10).
- `lca_sensitivity.py`: `cheme run scripts/lca_sensitivity.py [--check]`, the membrane-life,
  H2 co-product, electricity-mix and duration sensitivities, the ranking rule and the tables of
  `lca/README.md`, from both scenarios' LCA records (regen runs it in step 17).
- `skid_balance.py`: the flowsheet's stream values of both cases from core's stack and duty
  results (library ADR 0027, contract `balance-output/1`).
- `_core.py`: the one coupling to cheme-as-code (its commands' `--json` output only); the duty
  and comparison fields the scripts read are mapped and checked there, and the layout model is
  read there (the items on a frame, their parts, the solids a stack's hand lift meets).
- `_yamledit.py`: targeted edits of hand-maintained YAML that refuse any other change.
- `_figures.py`: the skid plans and sections of step 10, core's A1 sheets (`cheme layout
  render`) cropped to the drawing at their scale, the grid bubbles, scale bar, north arrow and
  title block moved beside it, rasterised by resvg (DESIGN.md D-041); no core import.
- `draft_P-01.py`, `draft_P-02.py`: the generators of the skid P&IDs P-01 (Skid A) and P-02
  (Skid B), both drawing with `_skid_pid.py` from the frames `pid/frames/P-0x.xml` (generated
  sheets, DESIGN.md D-017): change them, then `cheme regen P-01 P-02`.

`agent-run/` holds the runner and prompts of a staged agent design run (see its README).
