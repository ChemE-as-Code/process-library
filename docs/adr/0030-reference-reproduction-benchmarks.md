# 0030. Reference reproductions live in benchmarks/reproductions/, with tolerances frozen first

- **Status:** Proposed, 2026-11-01
- **Deciders:** the owner (to accept); drafted by the coordinator's agent for #302
- **Scope:** library structure (benchmarks), evaluation protocol

## Context

`benchmarks/<family>.yaml` (docs/benchmarks.md) holds KPI reference *ranges* that a published
LCI dataset is compared with. Issue #302 asks for a different kind of check: a **numerical
reproduction** of a published reference model (the IDAES HDA tutorial) by a cheme simulation
backend, kept apart from the independent hda-1 design (processes/hda-1/DESIGN.md, D-001: "not
a reference reconstruction"). Such a check needs a pinned source revision, the case
specification and the reported results as cited facts, tolerances fixed before the run, and a
comparison table. It does not fit the KPI-range schema, and it must not live in a process
folder that a design job works in, because the expected outputs are held out from that job.

Options considered: (a) extend `schemas/benchmarks.schema.json` with a reproduction kind,
(b) put the case in `processes/hda-1/`, (c) a separate folder per reproduction.

## Decision

- A reference reproduction is a folder `benchmarks/reproductions/<id>/`. The KPI registry
  loader (`scripts/benchmarks.py`) reads only `benchmarks/*.yaml`, so these folders are not
  part of it.
- The folder holds: `README.md` (purpose, protocol, status), `source.yaml` (pinned repository
  revision, licence, the reference case specification and the reported results, as facts in
  our own form with exact locators; no copied code, notebook text or figures), `tolerances.yaml`,
  a minimal cheme case (`case/`), and `comparison.md` with the deviations and their
  explanations.
- **Order is part of the evidence.** `tolerances.yaml` is committed in its own commit before
  any comparison run, and is not edited afterwards; a later change is a new file with a reason.
  `git log -- benchmarks/reproductions/<id>/` shows the order of the commits, and
  `git diff <freezing commit> HEAD -- benchmarks/reproductions/<id>/tolerances.yaml` is empty
  when the file has not changed since it was frozen. (`git log --follow` alone does not show an
  edit made in a merge commit.)
- A reproduction is numerical agreement with a model, not validation against plant or
  experiment, and its result is never used as design data in a process folder.

## Consequences

- Reproductions can be added without a schema change. CI does not check them: `validate.yml`
  validates only `processes/*/plant.yaml`, so neither `case/` nor the rest of the folder is
  validated (no structured checker yet: a follow-up if more reproductions come).
- The held-out results sit in a public repository; "held-out" means only that design jobs
  (which work in `processes/<id>/`) do not get them in their prompts, as for
  `benchmarks/ammonia.yaml` (#86).

## Evidence

- `benchmarks/reproductions/idaes-hda-tutorial/` (first reproduction), issue #302, core#104.
