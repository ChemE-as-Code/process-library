---
name: review
description: Review the plant repository or a change to it - run validation and the engineering-step checks, look at the rendered sheets and the diff, and write findings to reviews/. Use when asked to review, check, or sign off a stage or a branch.
---

# Reviewing

1. `plantcode validate` and `plantcode check`. Every failing check and every error is a finding.
   Read the last line of `validate`: it names the sheets, lists and cross-checks it ran; what it
   did not compare goes under "Not checked". `plantcode check` prints the gates and writes
   nothing.
2. For a branch: `plantcode diff main --list` gives one line per changed plant item with its
   counts (`--verbose` adds each change and the drawing that shows it, `--flat` one line per
   object); `plantcode diff main` writes `build/diff.html` to look at. Does every change have a
   reason in the commit messages and `PROGRESS.md`? Is any changed item `not drawn`?
3. Engineering review of each changed sheet. Render the changed regions, `plantcode render
   pid/<sheet>.xml --png --crop X0,Y0,X1,Y1` (`plantcode show <tag>` prints the drawing's region
   as `at X0,Y0,X1,Y1 mm`; the PNG is `build/<sheet>_crop-X0-Y0-X1-Y1.png`, and `--rev main`
   with the same crop gives the before picture), and read the XML of what you doubt: isolation valves around
   equipment that is maintained, check valves on pump discharges, relief for anything that can
   be blocked in, drains and vents at low and high points, instruments for what the design basis
   says is controlled (`plantcode show <instrument tag>` prints its loop, signal and actuating
   chain), DN consistent along each line and with the line list (and with literal labels:
   `plantcode.label-literal`). Note what you
   checked and what you could not.
4. Write `reviews/<YYYY-MM-DD>-<topic>.md`:
   ```markdown
   # Review: <topic>
   Scope: <branch / sheets / stage>   Reviewer: <name or agent>   Date: <date>
   ## Findings
   | # | sheet | item | finding | severity | proposed action |
   ## Checked and fine
   ## Not checked
   ```
5. Do not fix findings in the same commit as the review; each fix is its own change.
6. **Signing off a stage** (only when asked to sign off, and only with no failing check):
   `plantcode check --stage <stage> --write` writes `checks/status.json`; commit it together with
   the review record. Do not run `--write` in an ordinary review, and never edit
   `status.json` by hand.
