# 0034. An engineering project may export a design case's own LCI dataset beside its study's

- **Status:** Proposed, 2026-11-05
- **Deciders:** the owner (to accept); drafted for #331
- **Scope:** the LCI pipeline (`scripts/build_lci.py`) and the layout of a process's `lca/`
  (`REFERENCE.md`, `CONTRIBUTING.md`, `lci/README.md`)

## Context

A process folder holds one engineering project (ADR 0002) and its LCA studies one flowsheet
case: `lca/lca.yaml` names it (`case:`), and `cheme assess lca --write` derives the unallocated
dataset `lca/dataset.yaml` from that case only. `processes/co2-electrolysis-bpm-1` (#330) has
two computed designs in one flowsheet, two pilot skids as the cases `skid-a` and `skid-b`
(its DESIGN.md D-007), and #331 asks for the inventory of both. Until now `lca/datasets/` held
hand-written datasets of manifest-only processes (the utilities, the Tier 0/1 estimates).

Core 1.5.0 (core ADR 0045) writes a design case's dataset itself: `cheme assess lca --write
--case <case>` writes `lca/datasets/<dataset id>-<case>.yaml`, with an id, title (`<title>,
case <case>`) and uuid (`uuid5(<the study dataset's uuid>, "case:<case>")`) that name the case,
`parent` the study dataset's uuid, `provenance.case`, and the study's documentation except its
review. `--check --case` exits 1 when the file is stale.

Options considered:

- (a) A scratch copy of the project with `lca.yaml case: skid-b` and a second `dataset:` title,
  run by the process's own script, the result copied into `lca/datasets/` (the design spec's
  fallback). It duplicates what core now does, and the file would claim no case.
- (b) A second process folder for the second design: the engineering sources would be copied
  (the reason D-007 rejected it).
- (c) Core's case dataset, committed in `lca/datasets/`, kept current by a command gate, and
  exported by the LCI build as a dataset of its own.

The LCI build named every activity after the process (`process.yaml` `title`), so the two
designs' activities would share name, reference product, location and unit, which the build
refuses (the installer cannot tell them apart); and a market of the product would find two
activities of one supplier.

## Decision

- **A process with an engineering project may commit a design case's dataset**
  `lca/datasets/<dataset id>-<case>.yaml`, written by `cheme assess lca --write --case <case>`,
  never by hand. It has its own title and uuid (core's). A `kind: command` gate keeps it current
  (`cheme assess lca --check --case <case>`); a process that regenerates its design writes it in
  the same run (co2-electrolysis-bpm-1: `scripts/regen.py` step 20).
- **The study's choices stay with the study's dataset.** Data quality (`lca/manifest.json`) and
  the study's allocation (`lca/lca.yaml`) apply to `lca/dataset.yaml` only; a case dataset is
  allocated by its own (or the library's) method. The catalog's LCA headline is the study's
  case (`lca/results.csv`); a case dataset's characterised results are the scenario records'
  (`lca/scenarios/<id>.json`, a `case:` scenario).
- **The LCI build exports both** (`scripts/build_lci.py`). A dataset is a design case's when it
  is not the study's `lca/dataset.yaml`, its `provenance.generator` is `cheme assess lca` and
  it names `provenance.case` (`build_lci.design_case`). Its activities are named
  `<process title>, case <case>`; a hand-written dataset gets no such name, so a hand-written
  twin of the study's dataset is still refused. Where a market or a consumer's Atlas link must
  choose between the two, the study's dataset comes first: it is the process's default
  producer. This holds within one process only: the grade a consumer names still decides
  first, so a producer of that grade wins over another process's ungraded study dataset even
  when it offers the product through a case dataset alone.

## Consequences

- A second design of one plant is inventoried without a copy of the project, and stays current
  with the flowsheet through the gate.
- `lca/datasets/` now holds two kinds of file: hand-written datasets (manifest-only processes,
  estimates) and generated case datasets (engineering projects). The header comment and
  `provenance` tell them apart; `REFERENCE.md`, `CONTRIBUTING.md` and `lci/README.md` say so.
- The case's activity name is longer and depends on the case id; renaming a case renames the
  activity (its code changes with the dataset id anyway).
- Not covered: construction per case (core selects construction by equipment tag, not by
  case), scenario-dependent consumable amounts, and a case dataset's own data-quality rating;
  they stay open in the process that needs them (#331).

## Evidence

- `scripts/build_lci.py` (`design_case`, `_product_rows`, the market and plant choices),
  `tests/test_lci_case_datasets.py` (a fixture library with both files; a hand-written twin is
  still refused, `test_a_hand_written_twin_is_still_refused`; the grade before the study's
  dataset across processes; the two skids in the workbook, the JSON-LD package and the
  multifunctional JSON with their datasets' amounts; the KOH solution proxies against the
  datasets' compositions; the public build leaves the internal process out),
  `tests/test_lci_dataset_v2.py` (two activities the installer cannot tell apart are an error).
- `processes/co2-electrolysis-bpm-1/lca/datasets/`, its `checks/checks.yaml` gate
  `lca-case-dataset-current`, DESIGN.md D-024 to D-027; issue #331.
- Core ADR 0045 and `docs/framework/lci-scenarios.md` of core ("A design case's own dataset").
