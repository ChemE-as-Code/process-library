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

The pilot skids of #330 (DESIGN.md D-007 to D-021):

- `regen.py`: the single rerun command, `cheme run scripts/regen.py --duration H
  [--scratch DIR] [--check]`. It carries the design basis through `cheme process cell`,
  `duty`, `stack --write`, `datasheets draft`, the balance and `process build`, `layout build`,
  `datasheets fill` per case, `layout render`, `control report`, the duty plots and
  comparisons and the envelope check into every value and figure that depends on the campaign
  duration (steps 1 to 13; the invariants, records and `--uncertainty`/`--record` follow in
  the next stage). It owns the draft datasheets (D-020). `--check` regenerates in a temporary
  copy and reports any model file, datasheet or figure of that duration that differs (exit 3).
  `--scratch DIR` runs in a copy and copies the scenario's figures back (D-021).
- `skid_balance.py`: the flowsheet's stream values of both cases from core's stack and duty
  results (library ADR 0027, contract `balance-output/1`).
- `_core.py`: the one coupling to cheme-as-code (its commands' `--json` output only).
- `_yamledit.py`: targeted edits of hand-maintained YAML that refuse any other change.
- `draft_P-01.py`, `draft_P-02.py`: the generators of the skid P&IDs P-01 (Skid A) and P-02
  (Skid B), both drawing with `_skid_pid.py` from the frames `pid/frames/P-0x.xml` (generated
  sheets, DESIGN.md D-017): change them, then `cheme regen P-01 P-02`.

`agent-run/` holds the runner and prompts of a staged agent design run (see its README).
