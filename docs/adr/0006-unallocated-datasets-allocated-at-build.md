# 0006. LCI data enters as unallocated datasets; the database build allocates per co-product

- **Status:** Accepted, 2026-10-23
- **Scope:** `processes/<id>/lca/`, `scripts/build_lci.py`, `lci/mappings.yaml`

## Context

A process's study (`lca/lca.yaml` of an engineering project) answers its own question and may
choose its own allocation. A database of many processes needs one consistent treatment of
multi-output processes, and has to be able to change it (a new rule, a curated decision) without
editing the processes. Brightway's Excel importer (bw2io) has no clean representation of an
unallocated multi-output activity.

## Decision

- The input of the LCI database is core's **unallocated** LCI dataset of each process
  (`kind: lci_dataset`): `processes/<id>/lca/dataset.yaml`, written by
  `cheme assess lca --write` in an engineering project, or hand-written
  `lca/datasets/*.yaml` of a manifest-only process. The builder reads core's dataset contract
  v2 (`cheme/lci_dataset/v2`) and the v1 files.
- `build_lci.py` exports **one single-output activity per co-product**, per 1 unit of it,
  allocated at build time by the library's rules
  ([0007](0007-cut-off-system-model-and-allocation-hierarchy.md)): a curated entry in
  `lci/mappings.yaml` `allocation:` first, else the study's or dataset's method when it agrees
  with the hierarchy, else a recorded finding. Only proportional methods are accepted;
  substitution and `none` are refused. Activity codes are `<process>:<dataset>:<product key>`.
- Every activity and `datapackage.json` record the allocation used: method, source, rule,
  reason, shares and whether it follows the hierarchy.

## Consequences

- The database can re-allocate (a new rule, prices, a curated decision) without touching any
  process's files, and the process study keeps its own choice.
- The study and the database can disagree; the database records which rule it applied and why
  (for ASU-1 both use exergy, D-056).
- The unallocated multi-output form is not exported; users who want another allocation must
  rebuild from the datasets.
- The builder carries adapters for several core dataset contracts and must follow core's.

## Evidence

- `986803b` (builder moved in), [#15](https://github.com/ChemE-as-Code/process-library/pull/15).
- `2f6c009`, `d39f60a` allocation by the hierarchy with findings,
  [#68](https://github.com/ChemE-as-Code/process-library/pull/68).
- `0733ec0` core's dataset contract v2 adapter, [#75](https://github.com/ChemE-as-Code/process-library/pull/75) (core#294).
- lci/README.md ("Source", "Co-products"), [system-model.md](../system-model.md) section 2.
