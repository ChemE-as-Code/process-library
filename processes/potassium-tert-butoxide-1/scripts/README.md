# Scripts

`makeup_drying.py` is a balance script (library ADR 0027): the make-up tert-butanol's dehydration
on a molecular sieve (A001, DESIGN.md D-004), which core has no model for. It reads the two feeds
S3 and S4 from `process/flowsheet.yaml` and prints the dried make-up S6, the regeneration
condensate S7 and the unit's energy streams Q10, Q11, Q12 and P4; the flowsheet cites them with
sources that start `scripts/makeup_drying.py`. With `BALANCE_OUTPUT` set it writes them as JSON,
which the library's `scripts/check_balance_scripts.py` compares with the flowsheet. Run it with
`cheme run scripts/makeup_drying.py` after a change to S3 or S4, and copy its values into the
flowsheet in the same commit.

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
