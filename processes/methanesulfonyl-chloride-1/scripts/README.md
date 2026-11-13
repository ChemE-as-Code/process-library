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

`agent-run/` holds the runner and prompts of a staged agent design run (see its README).

`balance.py` is no generator: it gives the values of `process/flowsheet.yaml` that core cannot
calculate (the feeds for 1000 t/a with the thionyl chloride recycle, the scrubber's caustic and
its dilution water, the still's stream temperatures, and the duties Q7 and Q9; core's
models write the others; DESIGN.md D-006). It also prints the crude's flash on evacuation as
a cross-check, which is no duty of its own (it lies in the still's Q3 and Q4, D-007). Run it with `cheme run scripts/balance.py` after
`cheme process propagate --fill`, and repeat both until the feeds stop changing; it follows the
library's balance-output contract (`BALANCE_OUTPUT`, library ADR 0027).
