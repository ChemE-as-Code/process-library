# Working in this plant repository

This repository is a process plant design. The files are the design; there is no other database.

## Ground rules

- P&IDs are DEXPI 2.0.1 XML in `pid/`. Edit them **directly as text** (skills `dexpi-xml`,
  `pid-edit`, `pid-draft`). Do not type the verbose drawing XML: `plantcode copy` duplicates an
  object with its drawing (a spare pump, a second valve), `plantcode fragment` prints equipment
  with nozzles, lines, segments, valves, tees, pipes, instruments, signal lines (with the
  actuating system), off-page connectors, notes and missing catalogue shapes ready to paste,
  enough to draft a whole sheet. Change what is already on a sheet with `plantcode move` (an
  object's drawing), `plantcode rename` (an id with every reference, or a tag with its labels)
  and `plantcode set` (one data value and the labels showing it) before reaching for a hand
  edit; hand edits remain for re-pointing references and moving blocks. For what fragments
  cannot express, a generator script in
  `scripts/draft_<sheet>.py` uses the Python API `plantcode.domains.piping.authoring` (the same builders as
  `fragment`; example `scripts/example_draft.py`). Run it with `plantcode run`: `python3` and
  `uv run python` have no pyDEXPI in this repository. Never write your own XML helpers.
- Every sheet is either **hand-maintained** (the default: the XML is the source; a script in
  `scripts/` is provenance only and is never rerun over the sheet) or **generated** (its
  `plant.yaml` entry has `generator: {script, frame}`: the script is the source, the XML is not
  edited by hand, `plantcode regen <sheet>` rebuilds it). `plantcode regen --detach <sheet>`
  turns a generated sheet into a hand-maintained one. `plantcode validate` warns
  (`generated-sheet-drift`) when a generated sheet no longer matches its script.
- The block and process flow diagrams (`process/BFD.xml`, `process/PFD.xml`, `kind: bfd|pfd` in
  `plant.yaml`) are **generated** from `process/materials.yaml` and `process/flowsheet.yaml` by
  `plantcode process build` (skill `process-design`). Change the YAML and rebuild, never the XML
  (`plantcode.generated-edited`). Stream values carry their provenance (`given` with a `source`,
  `assumed`, `calculated` by `plantcode process propagate --fill` or `plantcode process props
  --fill` only); `DESIGN.md` keeps the
  decisions, not a second copy of the numbers. P&IDs start from the PFD (skill `pid-draft`).
- After every change: `plantcode fmt <sheet>`, then `plantcode validate`. Fix every `error`. Do not
  commit with errors; the pre-commit hook and CI refuse it anyway.
- One logical change per commit. Say what changed on which sheet and why. Append the change to
  `PROGRESS.md`.
- Keep the lists in step with the P&IDs (skill `lists-sync`), and the 3D layout in `layout/`
  in step with the equipment list (skill `layout-yaml`).
- Record decisions and assumptions in `DESIGN.md`, with the reason. Mark assumed values
  `ASSUMED` in the YAML or the decision text, never present a guess as data.
- **Branches and merges.** Each stage, and any change larger than one fix, goes on its own
  branch `stage/<stage>-<topic>` (e.g. `stage/basic-p04-products`); small fixes may go straight
  to the default branch (`main`). The branch is reviewed with `plantcode diff main --list`, quoted
  in the review record, and merged by a human or the reviewer, never by its author. Merge once
  the review's critical and high findings are closed. A stage sign-off is the last commit on
  its branch and counts only once it is merged: a stage is reached when its sign-off is on the
  default branch. End your summary by saying whether a merge is pending.
- Do not edit `checks/status.json` or `build/` by hand; they are generated. `build/` is ignored.
- `checks/status.json` records stage sign-offs: `plantcode check` only prints the gates;
  `plantcode check --stage <stage> --write --review reviews/<record>.md` adds that stage's entry
  (commit, date, signer, branch, review record, the gates of every stage up to it). It refuses
  on uncommitted changes, a failing gate, a review you wrote yourself (without a human
  `approved_by`) or an open critical/high finding, counting one closed by a commit not in
  HEAD's history (skill `review`, step 7). Never sign off your
  own review, and never edit `status.json` by hand.

- **How to run commands** (also headless, where every denied command costs a turn):
  - change files with the Edit and Write tools only -- never `sed -i`, `awk`, `perl -i`, `cp`
    over a sheet, heredocs (`cat > f <<EOF`, `python3 - <<EOF`) or shell redirection into
    repository files. A shell rewrite of a 50,000-line DEXPI file is unreviewable and fails
    silently when a pattern matches zero or several times;
  - one command per Bash call: no `for` loops, `&&` / `;` chains, pipes into files or
    `VAR=...;` prefixes. Read with `plantcode show`, `grep`, `sed -n 'A,Bp'`, `head`, `wc`;
  - scratch files go in `build/` (ignored), never next to the sheets.

## Commands

| | |
|---|---|
| `plantcode status [--json]` | start here: stage, each sheet drawn / empty / planned with the listed items it does not draw yet, the next sheet to draw, findings by sheet, gates per stage, sign-offs (and whether merged), open review findings, branch state |
| `plantcode impact [--json]` | review needed (info, read-only): review records whose scope or `basis` changed since, generated sheets whose `process/*.yaml` changed, stale calculated values; nothing is regenerated |
| `plantcode validate [files] [--json] [--ignore RULE[,RULE]] [--only RULE] [--skip-generators]` | all P&IDs and lists, and lists vs P&IDs (equipment, lines and DN, instruments), drawing geometry (lines through labels, crossings, overlapping and misplaced labels, each with a `[crop ...]`) and tags named in texts; a `drawing <sheet>:` count line per sheet; the last line says what was compared; rules may be globs (`plantcode.*-not-on-pid`); generated sheets are rebuilt in a scratch copy and compared unless `--skip-generators` |
| `plantcode sheet new <ID> [--title T] [--file F]` | a new sheet from the template with its title block filled from `plant.yaml` (project block), added to `sheets:` (a planned one becomes drafted) |
| `plantcode sheet meta <ID> [Key=Value ...]` | show or set title-block values (`Revision=B`, `Title=...`, `Status=...`, any MetaData property, `ModelName`, `DiagramName`): MetaData and the title-block texts together |
| `plantcode fmt [files] [--check]` | canonical XML, readable id on every object |
| `plantcode show <id or tag> [--sheet F] [--layout]` | `file:start-end` of an object and its drawing, owner chain, references in and out; `instrumentation:` the loop, actuating and signal chains it is part of; for equipment the lines, segments and branches at each nozzle; for a line number its segments, items and nodes with DN; `--layout` the measured plot-plan distances around a placed item |
| `plantcode render [files] [--png] [--crop X0,Y0,X1,Y1 \| --tiles CxR] [--findings] [--scale S] [--rev R]` | `build/<sheet>.svg` (`.png` with `--png`, `<sheet>@<rev>` with `--rev`, `<sheet>_crop-X0-Y0-X1-Y1` with `--crop`, so a crop never overwrites the full sheet); `--crop` in sheet mm, Y down; `--tiles 4x3` (or `auto`) overlapping tiles `<sheet>_tile-B3` covering the sheet, each with its `--crop`; `--findings` marks the drawing findings |
| `plantcode diff <old> [new] [--list [--verbose \| --flat] \| --json]` | HTML report in `build/diff.html`; `--list` one line per changed plant item with its added/removed/modified counts, `--verbose` each change under it, `--flat` one line per changed object with the drawing that shows it; `--json` the data |
| `plantcode check [--stage S [--only-stage]] [--write --review R]` | engineering-step gates in `checks/checks.yaml` of every stage up to S; `--write` only at sign-off. For what a P&ID must show write `kind: on-sheet` gates (printed tags and classes in the model), not `grep` over the XML |
| `plantcode cause-effect` | the cause-and-effect matrix of `control/cause-effect.yaml` to `build/cause-effect.html` and `.csv` |
| `plantcode schema [kind]` | JSON Schema of a YAML file kind; no kind lists them |
| `plantcode skills status \| update [NAME...] [--force]` | the bundled skills in `.claude/skills/`: current, outdated, modified (changed here) or missing; `update` installs missing and outdated files and keeps a modified one (reported) unless `--force` |
| `plantcode git-setup` | once per clone: `git diff` shows P&IDs as review text with their XML ids, pre-commit hook |
| `plantcode copy <id or tag> --prefix NEWID [--tag T] [--offset DX,DY] [--into PARENT] [--rename OLD=NEW] [--renumber A:B] [--set PROP=VALUE] [--connect PIPE=ITEM:NODE] [--sense-at ID[:X,Y]] [--print]` | duplicate an object with its parts and everything that draws it, every id renamed from `NEWID`; `--rename`/`--renumber` give inner valves their own tags, `--set` e.g. the fluid code, `--connect` closes an open pipe end, `--sense-at` re-points an instrument's sensing location; prints the new ids, the lines written, what was not copied and the tags still duplicated |
| `plantcode move <id or tag> --offset DX,DY [--print]` | move an object's drawing (symbol, node positions, labels); attached lines follow, bends that stay are listed |
| `plantcode rename OLD NEW [--children] [--ids] [--tag] [--print]` | an id and every `#OLD` reference (`--children`: also `OLD_*`); given a tag, the tag data and its labels (`--ids`: and the ids that spell it); `--tag`: NEW is the new tag of the object with the id OLD (retag one of two objects sharing a tag; an instrument's sensor and actuator follow) |
| `plantcode set <id or tag> PROP=VALUE... [--print]` | data values by DEXPI name, typed (string, number, enumeration, `'50 mm'` quantity, `Stroke.Width`), and the label texts showing them; `PROP=` removes one |
| `plantcode run [--fmt SHEET] SCRIPT [ARGS]` | run a Python script in plantcode's interpreter (pyDEXPI and `plantcode.domains.piping.authoring` import), cwd the repository root; arguments and exit code pass through; `--fmt` goes before SCRIPT (after it, it goes to the script) |
| `plantcode regen [SHEET...] [--force \| --detach \| --list]` | rebuild generated sheets (frame -> script -> fmt); refuses a sheet edited by hand and names the items; `--detach` makes a sheet hand-maintained |
| `plantcode process build [SHEET...] [--force]` | generate the BFD and PFD from `process/*.yaml`; refuses while the flowsheet has errors, and over a sheet edited by hand unless `--force` |
| `plantcode process streams [--case C] [--md \| --csv \| --json]` | the stream table (value, unit, provenance G/A/C per property, stale calculated values) and the balance of every block and step |
| `plantcode process propagate --fill \| --check [--case C]` | compositions and flows through pass-through steps, mixers and splitters (`split:` fractions); separators and reactors only checked; never overwrites given or assumed values; `--check` writes nothing |
| `plantcode process props --fill \| --check [--case C]` | phase, molar mass, density, enthalpy (extra `props`), inside the validated range only; never overwrites given or assumed values; `--check` writes nothing |
| `plantcode process layout [IDS...] [--view bfd\|pfd] [--pin]` | the generated positions; `--pin` writes them into `layout.<view>` of `flowsheet.yaml` |
| `plantcode fragment KIND --id ID [--sheet F] ...` | ready-to-paste XML, a CONCEPTUAL and a DRAWING part each saying where it goes; KIND `valve`, `tee`, `node`, `pipe`, `segment`, `line`, `label`, `equipment`, `nozzle`, `instrument`, `signal`, `offpage`, `note`, `shape` (`plantcode fragment --help`, skill `dexpi-xml`) |

## YAML files and their schema kind

| file | kind |
|---|---|
| `plant.yaml` | `plant` (sheets, each optionally with `generator: {script, frame}`) |
| `process/design-basis.yaml` | `design_basis` |
| `process/materials.yaml` | `process-materials` (components, templates, the property method `props --fill` records) |
| `process/flowsheet.yaml` | `process-flowsheet` (units, cases, tolerance, feeds, products, blocks, steps, streams with per-case state and provenance, links, `layout.bfd`/`layout.pfd`) |
| `equipment/equipment-list.yaml` | `equipment` (tag, type, service, sheet, design data, notes) |
| `piping/line-list.yaml` | `lines` (number, from, to, nominal_diameter, ..., notes, `segments` with a DN each) |
| `control/instrument-list.yaml` | `instruments` (tag as printed, service, sheet, notes) |
| `control/cause-effect.yaml` | `interlocks` (id, cause tag and condition, effects with actions, sheet, sil): every trip, instead of literal sheet text |
| `piping/special-items.yaml` (optional) | `piping_items` (tag, type, line, sheet, set_pressure_barg, relief_case: safety valves, silencers) |
| `checks/checks.yaml` | `checks` |
| `equipment/datasheets/<TAG>.yaml` | `datasheet` (one per equipment item: conditions, materials, sizing basis, `assumed` values) |
| `reviews/<date>-<topic>.md` front matter | `review` (topic, reviewed_commit, scope, reviewer, reviewer_kind) |
| `checks/status.json` (generated) | `status` |
| `layout/site-plan.yaml` | `site_plan` (site box, areas, roads, pipe racks, `separations`, `max_unsupported_length`) |
| `layout/building.yaml` | `building` (buildings, levels, column grid) |
| `layout/equipment-placement.yaml` | `placement` (tag, position, shape, size, building, level) |

`plantcode schema <kind>` prints the full JSON Schema.
