# 0002. One folder per process; the library is the single source of the Atlas and its LCI database

- **Status:** Accepted, 2026-10-23
- **Scope:** repository structure

## Context

The Process Atlas (a separate repository, ChemE-as-Code/process-atlas) shows processes, links
them through the chemicals they make and use, and offers their life-cycle inventories as a
Brightway database. Its first tooling (catalog builder, LCI builder, installer, schemas) was
staged in the Atlas repository (`process-atlas/library-kit`), while the only designed process,
the ASU, was its own repository. Keeping the data next to the Atlas would have tied every new
process to an Atlas release; keeping each process in its own repository would have scattered
the registry, the mappings and the checks that must agree across processes.

## Decision

- The process library is one repository with **one folder per process**,
  `processes/<id>/`. The folder is the unit: it is added, reviewed, versioned and published as
  a whole. `<id>` is a lowercase slug that never changes once listed, because it is the Atlas
  URL.
- What is shared between processes lives at the root: `chemicals/`, `taxonomy/`, `lci/`,
  `benchmarks/`, `coverage.yaml`, `schemas/`, `scripts/`, `python/`, `templates/process/`,
  `tests/`.
- The library is the **single source** of the Atlas catalog (`scripts/build_catalog.py` writes
  the catalog the Atlas reads) and of the Atlas LCI database (`scripts/build_lci.py`). Adding a
  process needs no change to the Atlas.
- An engineering project in a process folder is self-contained: `cheme` and Claude Code run
  **in that folder**, where its own `CLAUDE.md`, `AGENTS.md` and `.claude/` apply. The root
  `CLAUDE.md` covers only the library tooling and the licence rules.

## Consequences

- Cross-process consistency (registry slugs, mappings, taxonomy) is checked in one CI run.
- The clone grows with every process and every P&ID revision (a DEXPI P&ID is 1 to 3 MB of
  XML). The README's "Repository size" section answers with shallow and sparse clones, generated
  output kept out of git, and Git LFS only for large generated binaries.
- The catalog's git facts (each folder's last commit) need full history in the job that builds
  it (`fetch-depth: 0`); the other CI jobs check out shallowly.
- A process's engineering files are changed only through that process's own review; the root
  must not rewrite them (CONTRIBUTING.md).

## Evidence

- `986803b` "Process library: manifest, registry, schemas, tooling and CI at the root" (tooling
  moved from `process-atlas/library-kit`), merged in
  [#15](https://github.com/ChemE-as-Code/process-library/pull/15).
- `d40e3a8` repository size guidance and shallow checkouts (in
  [#28](https://github.com/ChemE-as-Code/process-library/pull/28)).
- README.md (table of paths, "Working on a process", "Repository size"), CONTRIBUTING.md step 1.
