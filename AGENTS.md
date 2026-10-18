# Working in this plant repository

This repository is a process plant design. The files are the design; there is no other database.

## Ground rules

- P&IDs are DEXPI 2.0.1 XML in `pid/`. Edit them **directly as text** (skills `dexpi-xml`,
  `pid-edit`, `pid-draft`). Do not type the verbose drawing XML: `plantcode copy` duplicates an
  object with its drawing (a spare pump, a second valve), `plantcode fragment` prints valves,
  tees, nodes, pipes, segments and labels ready to paste. Hand edits are for re-pointing
  references, moving blocks and changing data. A throwaway generator script in `scripts/`
  (pyDEXPI model classes) is a last resort for large drafts; its output is then the source of
  truth.
- After every change: `plantcode fmt <sheet> && plantcode validate`. Fix every `error`. Do not
  commit with errors; the pre-commit hook and CI refuse it anyway.
- One logical change per commit. Say what changed on which sheet and why. Append the change to
  `PROGRESS.md`.
- Keep the lists in step with the P&IDs (skill `lists-sync`), and the 3D layout in `layout/`
  in step with the equipment list (skill `layout-yaml`).
- Record decisions and assumptions in `DESIGN.md`, with the reason. Mark assumed values
  `ASSUMED` in the YAML or the decision text, never present a guess as data.
- Work on a branch for anything larger than one fix; review with `plantcode diff main --list`.
- Do not edit `checks/status.json` or `build/` by hand; they are generated. `build/` is ignored.
- `checks/status.json` records a stage sign-off: `plantcode check` only prints the gates;
  `plantcode check --stage <stage> --write` writes the file, and you commit it only when signing
  off that stage, together with its review record (skill `review`). Do not commit a
  `status.json` from an ordinary check run.

## Commands

| | |
|---|---|
| `plantcode validate [files] [--json]` | all P&IDs and lists, and lists vs P&IDs (equipment, lines and DN, instruments); the last line says what was compared |
| `plantcode fmt [files] [--check]` | canonical XML, readable id on every object |
| `plantcode show <id or tag> [--sheet F]` | `file:start-end` of an object and its drawing, owner chain, references in and out; `instrumentation:` the loop, actuating and signal chains it is part of; for equipment the lines, segments and branches at each nozzle; for a line number its segments, items and nodes with DN |
| `plantcode render [files] [--png] [--crop X0,Y0,X1,Y1] [--scale S] [--rev R]` | `build/<sheet>.svg` (`.png` with `--png`, `<sheet>@<rev>` with `--rev`, `<sheet>_crop-X0-Y0-X1-Y1` with `--crop`, so a crop never overwrites the full sheet); `--crop` in sheet mm, Y down |
| `plantcode diff <old> [new] [--list [--verbose \| --flat] \| --json]` | HTML report in `build/diff.html`; `--list` one line per changed plant item with its added/removed/modified counts, `--verbose` each change under it, `--flat` one line per changed object with the drawing that shows it; `--json` the data |
| `plantcode check [--stage S] [--write]` | engineering-step gates in `checks/checks.yaml`; `--write` only at sign-off |
| `plantcode schema [kind]` | JSON Schema of a YAML file kind; no kind lists them |
| `plantcode git-setup` | once per clone: `git diff` shows P&IDs as review text with their XML ids, pre-commit hook |
| `plantcode copy <id or tag> --prefix NEWID [--tag T] [--offset DX,DY] [--into PARENT] [--print]` | duplicate an object with its parts and everything that draws it, every id renamed from `NEWID`; prints the new ids, the lines written and what was not copied (pipes at its nozzles: connect them) |
| `plantcode fragment KIND --id ID [--sheet F] ...` | ready-to-paste XML, a CONCEPTUAL and a DRAWING part each saying where it goes; KIND `valve`, `tee`, `node`, `pipe`, `segment`, `label` (`plantcode fragment --help`, skill `dexpi-xml`) |

## YAML files and their schema kind

| file | kind |
|---|---|
| `plant.yaml` | `plant` |
| `process/design-basis.yaml` | `design_basis` |
| `equipment/equipment-list.yaml` | `equipment` (tag, type, service, sheet, design data, notes) |
| `piping/line-list.yaml` | `lines` (number, from, to, nominal_diameter, ..., notes, `segments` with a DN each) |
| `control/instrument-list.yaml` | `instruments` (tag as printed, service, sheet, notes) |
| `checks/checks.yaml` | `checks` |
| `layout/site-plan.yaml` | `site_plan` (site box, areas, roads, pipe racks) |
| `layout/building.yaml` | `building` (buildings, levels, column grid) |
| `layout/equipment-placement.yaml` | `placement` (tag, position, shape, size, building, level) |

`plantcode schema <kind>` prints the full JSON Schema.
