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
calculate yet (the feeds for 500 t/a, the thiosulfate solution and the wash water, the washes'
and the drying's specified splits D102, D103 and X101, R101's vent fraction,
the mixed temperatures, the duties other than R101's Q2, ST101's Q3 and ST102's Q8 and Q10, which
core's models write (Q2, Q3 since 1.9.0; ST102's reboiler and condenser with its column since
1.10.0), and the powers from the recipe's durations; DESIGN.md D-008 to D-012, D-016).
Run it with `cheme run scripts/balance.py` after `cheme process propagate --fill`; it follows the
library's balance-output contract (`BALANCE_OUTPUT`, library ADR 0027).
