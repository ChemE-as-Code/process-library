# ChemE-as-Code process library

Versioned designs of chemical processes, one folder per process, kept as plain files in git. It
is the source of the [Process Atlas](https://github.com/ChemE-as-Code/process-atlas)
(atlas.cheme-as-code.org, not yet public) and of its Brightway LCI database.

> Private. Formerly `ChemE-as-Code/example-asu`: the air separation unit that lived at the root
> now lives in [`processes/asu-1/`](processes/asu-1/) with its full history
> (`git log --follow processes/asu-1/<path>`).

| path | what |
|---|---|
| `processes/<id>/process.yaml` | the Atlas manifest of a process (schema `schemas/process.schema.json`): title, families, inputs and outputs by chemical, maturity, review status, references |
| `processes/<id>/plant.yaml` and the rest | optional: a cheme-as-code (plantcode) engineering project: P&IDs, BFD/PFD, lists, layout, LCA. Its own README says how to work in it |
| `processes/<id>/lca/dataset.yaml`, `lca/datasets/*.yaml` | optional: unallocated LCI datasets (core's `lci_dataset`), the input of the LCI database |
| `processes/<id>/lca/scenarios/<id>.json` | optional: core's per-scenario records (`cheme assess lca-scenarios --write`): the design case, regional background scenarios (geography, year, electricity), linked exchanges and their states, totals per functional unit; the catalog publishes them (see below) |
| `chemicals/chemicals.yaml` | chemical identity registry (CAS, InChIKey, ChEBI): the slugs processes name, which link them in the Atlas graph |
| `lci/mappings.yaml` | how LCI exchanges link to Brightway background and biosphere data (by name; no licensed data) |
| `schemas/` | JSON Schemas of process.yaml, the registry and the mappings |
| `templates/process/` | starter folder for a new process |
| `scripts/` | `build_catalog.py` (catalog for the Atlas), `build_lci.py` (Brightway workbook), `render_previews.py` and `export_snapshots.py` (drawings and viewer snapshots, via `cheme`); `publication.py` (the rules of `--public`) |
| `python/` | `cheme-as-code-lci`, the one-call Brightway installer of the LCI database |
| `tests/` | tests of the scripts, with a synthetic fixture library |

## Processes

| id | process | maturity | engineering project |
|---|---|---|---|
| [`asu-1`](processes/asu-1/) | Cryogenic air separation unit, 500 t/d GOX | screening (calculation level balanced since the owner fixed the design air as the design specification, D-099; basic-engineering deliverables present, predictive simulation not reached), not independently reviewed | yes (DEXPI P&IDs, BFD/PFD, 3D layout, MTO, LCA, DWSIM checks) |

## Working on a process

Each engineering project is self-contained: run `cheme` and Claude Code **in its folder**
(`cd processes/asu-1`). `cheme` finds the plant by walking up to `plant.yaml`, and what its
docs call "the repository root" is that folder. Once per clone, in a process folder:
`cheme git-setup` (readable P&ID diffs and the pre-commit check of that plant).

## Adding a process

See [CONTRIBUTING.md](CONTRIBUTING.md): copy `templates/process/` to `processes/<id>/`, fill in
`process.yaml`, add new chemicals to the registry. No change to the Atlas is needed.

## Building the catalog and the LCI database

```sh
uv run scripts/build_catalog.py --library . --out dist [--artifacts <previews>] [--snapshots <snapshots>] [--strict] [--public]
uv run scripts/build_lci.py --library . --out dist --version 0.1.0 [--strict] [--public]
uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl --with ./python --with bw2calc pytest -q tests
```

**Design cases and regional scenarios.** One engineering project serves several operating
cases (flowsheet `cases:`, each with its declared `capacity`) and several geographical
backgrounds (`scenarios:` in `lca/lca.yaml` with `location`, `year`, `electricity`, `missing:`,
`proxy:`; core docs/framework/lci-scenarios.md). No folder is copied per region or capacity.
Run `cheme assess lca-scenarios --write` in the process folder and commit `lca/scenarios/`; the
catalog gives each process `lca.design_cases` and `lca.scenarios` and copies the records to
`scenarios/<id>/<scenario>.json`. A scenario whose values may not be published, or whose record
is stale, keeps its geography, states and gaps but loses its totals. ASU-1 has `nl-grid` and
`de-grid` on core's packaged EEA 2024 grid factors (D-101). These are declared proxies for scope,
because they are generation-based while the baseline is at the consumer. A scenario missing data
the baseline has would be marked not comparable.

CI (`.github/workflows/validate.yml`): every `processes/*/plant.yaml` is validated with `cheme`
in its folder; the library job runs the tests (including the Brightway round trip) and builds
the catalog and the LCI database, and the public catalog (`--public`: only processes with
`publication.status: public`, placeholder footprints withheld; see CONTRIBUTING.md). Nothing is
published.

## Repository size

A DEXPI P&ID is 1 to 3 MB of XML (ASU-1's folder is about 14 MB), and every revision stays in
the history, so the clone grows with each process and each P&ID change. To keep that cheap:

- **Shallow clones where no history is needed.** CI checks out with `fetch-depth: 1`, except
  the library job, which builds the catalog: its git facts (each folder's last commit, whether
  previews and snapshots are behind it) need the history, so it uses `fetch-depth: 0`. A
  catalog built from a shallow clone gives every folder the head commit. For work on one
  process, a shallow sparse clone is enough:
  `git clone --depth 1 --filter=blob:none --sparse <url> && git sparse-checkout set processes/<id>`.
- **Keep generated output out of git.** `build/` and `dist/` are ignored: previews, viewer
  snapshots (about 14 MB per process) and the catalog are rebuilt from the sources.
  `export_snapshots.py --cache DIR` reuses a snapshot until its folder, the `cheme` version or
  the export options change.
- **Git LFS only for large generated binaries** that must be versioned (renders, meshes,
  spreadsheets exported for others), should they ever be committed. Never for the DEXPI XML or
  other engineering sources: they must stay text, diffable (`diff=dexpi`, `.gitattributes`) and
  reviewable. Blobs committed before a file moves to LFS stay in the history unless it is
  rewritten (`git lfs migrate`), so decide before the first commit.
