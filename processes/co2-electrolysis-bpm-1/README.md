# CO2 electrolysis in a reverse-bias bipolar-membrane cell (co2-electrolysis-bpm-1)

> **AI-generated research output, not engineering advice.** This design was produced by AI coding
> agents (Claude Code) under human direction and is checked by automated tools; it has had
> no independent human review. It is not approved for construction, operation, procurement or
> safety decisions and comes with no warranty. Check the design maturity and review status in
> `process.yaml` before relying on any number.

## This case

The case is CO2 electrolysis to CO, grounded in the measured water dissociation efficiencies of
Prats Vergel, Vermaas, Burdyny et al. (Nature Chemical Engineering 2025; 4TU dataset v1,
CC BY 4.0, see `NOTICE.md`). The tracker is ChemE-as-Code/core#136; the measured cell is #329,
its series and cell balance the groundwork of #330.

| path | what |
|---|---|
| `process/design-basis.yaml` | the measured reference cell (5 cm2 MEA, Fumasep FBM reverse bias, Ag GDE, Ni foam, KOH anolyte) |
| `data/measured/wde-1m-koh.yaml` | WDE vs current density in 1 M KOH, calculated from the raw titration sheets (generated) |
| `experiments/electrochemistry/rbpm-1m-koh.yaml` | the measured series: cell voltage, outlet gas (CO, H2) and titration of each of the 18 runs at 25-250 mA/cm2, from the raw CP, MFM, GC and titration files (generated; `cheme experiments electrochem`) |
| `process/materials.yaml`, `process/reactions.yaml` | components; CO2 -> CO + 1/2 O2 and H2O -> H2 + 1/2 O2 with CODATA heats of reaction |
| `process/cells.yaml` | the bench cell at 200 mA/cm2, its voltage and efficiencies looked up in the measured series (`cheme process cell`) |
| `scripts/adapt_4tu.py` | downloads the pinned raw data, verifies its sha256, writes the two data files and `figures/wde-1m-koh.svg` (`scripts/rawsheets.py` reads the spreadsheets) |
| `figures/polarisation.svg`, `faradaic-efficiency.svg`, `partial-current-density.svg`, `water-dissociation-efficiency.svg` | the measured series, drawn by `cheme experiments electrochem --plot` |
| `scripts/cell_section.py` | draws `figures/cell-cross-section.svg` from the design basis |
| `DESIGN.md` | decisions D-001 to D-006 |

Regenerate, from this folder:

```sh
cheme run scripts/adapt_4tu.py
cheme experiments electrochem experiments/electrochemistry/rbpm-1m-koh.yaml --plot figures/
cheme process cell
cheme run scripts/cell_section.py
```

The comparison with the published results is held out in
`benchmarks/reproductions/vermaas-rbpm-wde/` and is not used here (ADR 0032).

The following stages are planned:

- **core#138, core#139, #330:** intermittent operation, stack sizing and two pilot skids.
- **#331:** life-cycle inventory and assessment.

<p align="center">
  <a href="https://cheme-as-code.org"><img src="https://img.shields.io/badge/built_with-ChemE--as--Code-0b7285" alt="Built with ChemE-as-Code"></a>
  <a href="https://atlas.cheme-as-code.org"><img src="https://img.shields.io/badge/Process_Atlas-atlas.cheme--as--code.org-2b8a3e" alt="Process Atlas"></a>
  <a href="https://docs.cheme-as-code.org"><img src="https://img.shields.io/badge/docs-cheme--as--code-1c7ed6" alt="Documentation"></a>
  <img src="https://img.shields.io/badge/status-research_preview-orange" alt="Status: research preview">
  <a href="../../actions/workflows/validate.yml"><img src="../../actions/workflows/validate.yml/badge.svg" alt="validate"></a>
</p>

A plant design kept as plain files in git: P&IDs in DEXPI 2.0.1 (the open P&ID exchange
standard) in `pid/`, engineering lists as YAML, decisions and progress as Markdown. Edited by
people and by coding agents (Claude Code), checked by
[`cheme-as-code`](https://github.com/ChemE-as-Code/core).

New to ChemE-as-Code? [cheme-as-code.org](https://cheme-as-code.org) explains the idea in plain
language, the [documentation](https://docs.cheme-as-code.org) describes the commands and files,
and the [Process Atlas](https://atlas.cheme-as-code.org) is a library of chemical processes built
with the same tools. ChemE-as-Code is research software in active development: research output,
not engineering advice.

## What is where

| Path | Contents |
|---|---|
| `plant.yaml` | name, stage, sheets |
| `pid/` | P&ID sheets (DEXPI 2.0.1 XML) |
| `process/design-basis.yaml` | capacity, feeds, products, utilities, site |
| `process/materials.yaml`, `process/flowsheet.yaml` | components, blocks and streams: the source of the block flow and process flow diagrams (BFD, PFD) in `process/*.xml` |
| `equipment/equipment-list.yaml`, `piping/line-list.yaml`, `control/instrument-list.yaml` | lists, consistent with the P&IDs |
| `control/cause-effect.yaml` | interlocks and trips (cause and effect) |
| `piping/special-items.yaml` (optional) | tagged piping components: safety valves, silencers, rupture discs (skill `lists-sync`) |
| `safety/` | HAZOP studies (`safety/hazop/<id>/study.yaml`) and the risk matrix they rate against; `safety/README.md` says how |
| `layout/`, `electrical/`, `estimate/`, `lca/` | 3D layout, electrical, cost estimate and life cycle assessment; each folder's `README.md` says what goes there |
| `checks/checks.yaml` | engineering-step gates (checks that must pass before a stage is signed off); `checks/status.json` their result at the last sign-off |
| `reviews/` | review records |
| `runs/` | one record per design session, written by `cheme runs record` (`runs/README.md`); never edited |
| `DESIGN.md`, `PROGRESS.md`, `STAGES.md` | decisions, change log, stage definitions |
| `scripts/` | scripts that generate sheets (see `generator:` in `plant.yaml`) |
| `.claude/skills/` | skills: the instructions an AI agent follows when it works here |

## How this repository works

- **This repository holds your plant**: drawings, lists, decisions. It does not hold the tools.
- **The tools come from [`cheme-as-code`](https://github.com/ChemE-as-Code/core)**, installed once on
  your computer (`uv tool install git+https://github.com/ChemE-as-Code/core.git`). Every check,
  drawing and generated file is made by the `cheme` command, so you need it to work here. The
  continuous integration (CI) in `.github/workflows/` installs it too.
- **The skills in `.claude/skills/` are copies** of the ones in cheme-as-code, so that Claude Code
  finds them here. After upgrading (`uv tool upgrade cheme-as-code`), run `cheme skills update` to
  refresh them; `cheme skills status` shows which are out of date. A skill you changed here is
  kept.
- **While cheme-as-code is private**, you need read access to it, and the CI needs the secrets
  named in `.github/workflows/validate.yml`.

## Quick start

```sh
uv tool install git+https://github.com/ChemE-as-Code/core.git   # once: the cheme command
cheme git-setup                 # once per clone: readable P&ID diffs + pre-commit hook
cheme validate                  # after every change
```

To look at the plant in a browser (P&IDs, streams, 3D layout), install the Viewer extra with
`uv tool install 'cheme-as-code[serve] @ git+https://github.com/ChemE-as-Code/core.git'`, run
`cheme serve` here, and see the [Viewer documentation](https://docs.cheme-as-code.org/viewer/).

## More commands

```sh
cheme status                    # where the plant stands: sheets, findings, gates, sign-offs
cheme fmt                       # canonical XML, stable ids
cheme render [--png] [--crop]   # build/<sheet>[_crop-X0-Y0-X1-Y1].svg (or .png)
cheme render --png --tiles auto # build/<sheet>_tile-A1.png ... to read the whole sheet
cheme show <id or tag>          # where an object and its drawing are in the file
cheme diff main [--list]        # build/diff.html, or one line per changed plant item
cheme check                     # engineering-step gates (--write only at sign-off)
cheme runs list                 # the record of each design session in runs/
cheme process build             # BFD and PFD from process/*.yaml
cheme process streams           # stream table with provenance, block balances
```

## Licence

This folder is part of the ChemE-as-Code process library. Its data and designs are under
CC BY 4.0 ([`LICENSE-DATA`](../../LICENSE-DATA)); its scripts and skills are under
AGPL-3.0-or-later ([`LICENSE`](../../LICENSE)), like the ChemE-as-Code tools. The measured data
derive from the 4TU dataset of Prats Vergel et al. (CC BY 4.0); its attribution is in
[`NOTICE.md`](NOTICE.md).
