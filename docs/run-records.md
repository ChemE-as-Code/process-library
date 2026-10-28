# Run records

Each design run on a process leaves a record in `processes/<id>/runs/<run-id>/`
([ADR 0020](adr/0020-run-records-per-process.md)). Git shows what a run changed; the record shows
what it was asked, what it cost and how its result was checked. Records are organised by run,
not by stage: a revision is a new run, and an existing record is never edited. `runs/**` is not
published in the Atlas or the viewer.

## Format and writer: core

ChemE-as-Code core defines the record and writes it (core ADR 0029, core#403):

- the folder layout and `run.yaml`: schema `process-run/v1`, printed by
  `cheme schema process-run`; each process's `runs/README.md` (from core's project template)
  summarises the files;
- `cheme runs start` / `cheme runs record`: run by the SessionStart/SessionEnd hooks in each
  process's `.claude/settings.json` (copied unchanged from core's template) and by the agent
  runner; `cheme runs list` lists a process's records.

This page does not repeat the fields; the schema is the reference. A record written by hand
(a manual change worth recording) must validate against it.

## What the library adds

- **Where:** start Claude Code in `processes/<id>/`. The process folder is the plant repository
  root, so the hooks write into `processes/<id>/runs/`.
- **Committing:** the hook leaves an interactive session's record uncommitted; commit it with
  the session's work (or delete it, before it is committed, when the session should not count).
  The agent runner commits its record alone. Set `CHEME_RUN_RECORD=off` to switch the hooks off.
- **Publication:** `runs/**` is in `DEFAULT_EXCLUDE` (`scripts/publication.py`): records stay in
  git and out of the Atlas and viewer snapshots. A session transcript is committed only when
  core's writer allows it; otherwise it stays in the ignored `build/run-records/`.
- **Migration:** records written before core's schema were migrated once (2026-10-28): fields
  core does not know moved under `observed_later.migrated_fields` with their values unchanged,
  and each says so in `incomplete_notes`.

## Tagging a design for the paper

```sh
git tag -a paper/<process-id>-v1 <commit> -m "<process-id> v1: runs <run-id>, <run-id>"
```

The commit must contain the chosen design and the records of every run that produced it. Push
tags only when the design is final (`git push origin paper/<process-id>-v1`).
