# Scripts

Generator scripts for P&ID sheets. Run them with `plantcode run scripts/<script>.py ARGS`: it
uses plantcode's own interpreter, where pyDEXPI and the authoring API `plantcode.domains.piping.authoring`
import (`python3` and `uv run python` do not have them here). `example_draft.py` shows the API.

A sheet is in one of two states, set in `plant.yaml`:

- **generated**: the sheet's entry has `generator: {script: scripts/draft_<sheet>.py, frame:
  <commit or file>}`. The script is the source. Change the script, then `plantcode regen
  <sheet>` (frame -> script -> `fmt`); never edit the XML by hand. `regen` refuses a sheet that
  was edited by hand and names the items; `plantcode validate` warns `generated-sheet-drift`.
- **hand-maintained** (no `generator:`): the XML in `pid/` is the source; a script here is
  provenance only and is never rerun over the sheet (validate notes it as
  `generator-undeclared`).

To move a sheet from generated to hand-maintained: `plantcode regen --detach <sheet>`, then
edit the XML (skill `pid-edit`). To move back, put the hand edits into the script until
`plantcode regen <sheet>` reproduces the sheet, then declare the generator.

A generator takes the sheet file as its argument and edits it in place, starting from the
frame (for a new sheet: the one `plantcode sheet new` wrote).

`agent-run/` holds the runner and prompts of a staged agent design run (see its README).
