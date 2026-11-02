# 0010. Two builds, preview and public; the public build fails closed

- **Status:** Accepted, 2026-10-23 (LCA values by core's publication policy since 2026-10-24)
- **Scope:** `scripts/publication.py`, `--public` of `build_catalog.py`, `build_lci.py` and `export_snapshots.py`

## Context

The library holds work in progress that is not ready to publish: processes nobody has decided to
release, agent and review files, and LCA results computed with placeholder factors or with
sources whose terms forbid publication. The Atlas still needs a preview of everything for the
people working on it. A rule that publishes unless something is marked private would leak by
omission.

## Decision

- **Preview build** (the default): every process as the library has it.
- **Public build** (`--public`): what may be published, as a whole. It is opt-in per process and
  withholds whenever permission is not stated:
  - only processes with `publication.status: public` are included; `internal` (the default) and
    `candidate` are left out entirely. Setting `public` is the maintainers' decision in its own
    change, with a `publication.license` (no default);
  - `repository` is shown only when its `access` is `public`;
  - LCA footprint values are shown only when core's committed run manifest
    (`lca/manifest.json`) says the result is publishable under its sources' terms and is current
    (`lca_withheld`): placeholder factors, a missing or stale manifest, restricted or local
    sources withhold them, while goal, scope, inventory and attributions stay;
  - viewer snapshots are exported without the default excludes (`.claude/**`, `AGENTS.md`,
    `CLAUDE.md`, `reviews/**`, `PROGRESS.md`, ...), `process.yaml` and the process's own
    `publication.exclude`.
- The rules live in one module, `scripts/publication.py`, used by all three scripts.

## Consequences

- Forgetting a field keeps data out rather than letting it out.
- Everything else in a public process folder, including `README.md` and `DESIGN.md`, is
  published as text: authors must write for the public or exclude it.
- Two outputs to test; CI builds both catalogs, and the release workflow uses only `--public`.
- The default excludes are listed in both `publication.py` and CONTRIBUTING.md and must be
  changed together.

## Evidence

- `28bb7b9` "Public build mode: published processes only, placeholder footprints withheld",
  [#20](https://github.com/ChemE-as-Code/process-library/pull/20).
- `5f96993` "publish LCA values by core's policy, not the example flag" and `99224ec` (stale run
  manifests withheld), [#35](https://github.com/ChemE-as-Code/process-library/pull/35).
- CONTRIBUTING.md "Publishing a process", `scripts/publication.py`.
