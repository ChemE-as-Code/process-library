# 0020. Record each design run with its process, organised by run, kept out of publication

- **Status:** Proposed, 2026-10-27
- **Amended 2026-10-28:** core now owns the record format and its writer (core ADR 0029,
  core#403: schema `process-run/v1`, `cheme runs start | record | list`); this ADR keeps the
  library's part: the folder in each process, the publication exclusion and the paper tags.
- **Deciders:** the owner
- **Scope:** library structure (a `runs/` folder in each process) and publication (`runs/**` excluded)

## Context

Case studies are now developed by agent runs (the first: methanol-1, #187, $5.08 and 15 min of
API use). Git shows what each run changed in the design; it does not show what the change cost,
what the agent was asked, from which commit it started, or which checks were run on the result.
These are needed to compare runs and to report effort in the paper.

Core's agent-design-run guide (`docs/agent-design-run.md` in ChemE-as-Code/core) kept a record
per *stage* under `reviews/<date>-agent-design-run/runs/<stage>/`. A stage is often redone or
split, and a revision of an earlier stage then overwrites or mixes with its record. Organising by
run avoids this: a record is written once and never edited.

The first version of this ADR defined the `run.yaml` fields here and left the writing to the
library's agent runner and to hand-written records. Core has since adopted run-based records
for every plant repository (core ADR 0029): it defines `process-run/v1`, writes the records
(`cheme runs record`, from the SessionStart/SessionEnd hooks of the project template's
`.claude/settings.json` and from the agent runner) and lists them (`cheme runs list`). A second
definition in the library would drift from it.

## Decision

- **Core owns the format and the writer.** `run.yaml` follows core's schema `process-run/v1`
  (`cheme schema process-run` prints it); the library does not restate or extend its fields.
  Records are written by `cheme runs record`: the hooks in each process's
  `.claude/settings.json` (copied unchanged from core's project template) for interactive
  sessions, the agent runner for the sessions it starts. A record written by hand must validate
  against the same schema.
- Every design run on a process (an agent run, an interactive session, a manual change worth
  recording) gets a folder `processes/<id>/runs/<run-id>/` (the process folder is the plant
  repository root core writes into). A revision is a new run; existing run folders are not
  edited, except once to migrate a record written before core's schema to it (field names and
  shapes only, every value kept, said in its `incomplete_notes`).
- A record that misses facts says so: `complete: false` with `incomplete_notes`. Facts learnt
  later are recorded as such (`observed_later`), never as if measured during the run.
- `runs/**` is in `DEFAULT_EXCLUDE` (`scripts/publication.py`): records stay in git and leave
  the Atlas and viewer snapshots out, like `reviews/**`.
- The design chosen for the paper is marked with an annotated tag `paper/<process-id>-v<n>` on a
  commit that contains the design and its run records; the tag message lists the run ids.

## Consequences

- Effort and outcomes per run can be summed and compared across processes from git alone, and
  across any plant repository that uses core, since all write the same format.
- A change to the record format is a core change (core ADR, schema version); the library follows
  it by updating `cheme` and, when needed, migrating its records.
- Session exports add about 0.5 MB per run to the repository. Core's writer decides when a
  transcript may be committed (no API key in it, no web tools used); otherwise it stays in the
  ignored `build/run-records/`.
- An interactive session's record is left uncommitted by the hook; whoever ends the session
  commits it with the work (or deletes it if the session should not be recorded).
  `CHEME_RUN_RECORD=off` switches the hooks off.
- Records written before core's schema (all 22 of 2026-10-27, with runner fields such as
  `tools.runner_commit`) were migrated once on 2026-10-28: the fields core does not know moved
  under `observed_later.migrated_fields`, values unchanged.

## Evidence

`scripts/publication.py` (`DEFAULT_EXCLUDE`), `CONTRIBUTING.md`, the snapshot fixture
(`tests/fixtures/snapshots/fixture-electrolysis/manifest.json`) and the `runs` case of
`test_snapshot_not_exported_for_publication_is_an_error` in `tests/test_build_catalog.py`;
the hooks in `processes/*/.claude/settings.json`; conventions in `docs/run-records.md`; first
records in `processes/methanol-1/runs/` (#187). Format and writer: core ADR 0029, core#403.
