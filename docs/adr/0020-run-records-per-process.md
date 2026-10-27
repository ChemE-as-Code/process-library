# 0020. Record each design run with its process, organised by run, kept out of publication

- **Status:** Proposed, 2026-10-27
- **Deciders:** the owner
- **Scope:** library structure (a `runs/` folder in each process) and publication (`runs/**` excluded)

## Context

Case studies are now developed by agent runs (the first: methanol-1, #187, $5.08 and 15 min of
API use). Git shows what each run changed in the design; it does not show what the change cost,
what the agent was asked, from which commit it started, or which checks were run on the result.
These are needed to compare runs and to report effort in the paper.

Core's agent-design-run guide (`docs/agent-design-run.md` in ChemE-as-Code/core) keeps a record
per *stage* under `reviews/<date>-agent-design-run/runs/<stage>/`. A stage is often redone or
split, and a revision of an earlier stage then overwrites or mixes with its record. Organising by
run avoids this: a record is written once and never edited.

## Decision

- Every design run on a process (an agent run, an interactive session, a manual change worth
  recording) gets a folder `processes/<id>/runs/<run-id>/`, `run-id` = `YYYYMMDD-HHMMSS-<slug>`
  (start time, UTC). A revision is a new run; existing run folders are not edited.
- The folder holds `run.yaml` (schema `process-run/v1`, fields in
  [run-records.md](../run-records.md)), `task.md` (the exact prompt) and, when the session is
  available, `session.jsonl.gz` (the Claude Code session export, gzipped, committed only after a
  secret scan).
- A record that misses facts says so: `complete: false` with `incomplete_notes`. Facts learnt
  later are recorded as such (`observed_later`), never as if measured during the run.
- The run's record is committed as the last commit of the run, directly on top of the design
  commits it describes.
- `runs/**` is in `DEFAULT_EXCLUDE` (`scripts/publication.py`): records stay in git and leave
  the Atlas and viewer snapshots out, like `reviews/**`.
- The design chosen for the paper is marked with an annotated tag `paper/<process-id>-v<n>` on a
  commit that contains the design and its run records; the tag message lists the run ids.

## Consequences

- Effort and outcomes per run can be summed and compared across processes from git alone.
- Session exports add about 0.5 MB per run to the repository.
- The stage-based record of core's guide stays valid for repositories that use core's runner;
  this library uses the run-based one. Core's guide may adopt it later (a core change).
- Records written before this decision (methanol-1's first two runs) are backfilled with
  `complete: false`.

## Evidence

`scripts/publication.py` (`DEFAULT_EXCLUDE`), `CONTRIBUTING.md`, the snapshot fixture
(`tests/fixtures/snapshots/fixture-electrolysis/manifest.json`) and the `runs` case of
`test_snapshot_not_exported_for_publication_is_an_error` in `tests/test_build_catalog.py`;
format in `docs/run-records.md`; first records in `processes/methanol-1/runs/` (#187).
