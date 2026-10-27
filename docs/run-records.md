# Run records

Each design run on a process leaves a record in `processes/<id>/runs/<run-id>/`
([ADR 0020](adr/0020-run-records-per-process.md)). Git shows what a run changed; the record shows
what it was asked, what it cost and how its result was checked. Records are organised by run,
not by stage: a revision is a new run, and an existing record is never edited. `runs/**` is not
published in the Atlas or the viewer.

```
processes/<id>/runs/<YYYYMMDD-HHMMSS>-<slug>/
  run.yaml           the record (below)
  task.md            the exact prompt or brief
  session.jsonl.gz   the Claude Code session export, when available (secret-scanned)
```

## run.yaml

```yaml
schema: process-run/v1
run_id: 20261027-202241-concept-to-pfd
process: methanol-1
kind: agent                 # agent | interactive | manual
complete: true              # false when facts are missing; then incomplete_notes says which
incomplete_notes: []
branch: case/methanol-1
start_commit: b43b479...    # HEAD before the run
end_commit: 9b5639f...      # last design commit of the run (the record's own commit follows)
started: 2026-10-27T20:22:41Z
finished: 2026-10-27T20:38:02Z
wall_s: 921
cost_usd: 5.08              # as reported by the API client (total_cost_usd)
budget_usd: 25
model: claude-opus-5-5
effort: high
num_turns: 114
tokens: {input: 160, output: 89211, thinking: 37364, cache_read: 11034284, cache_write: 218162}
session_id: 4c866f29-...
session_export: {file: session.jsonl.gz, sha256: ...}
tools: {cheme: 0.8.0, core_commit: ..., claude_agent_sdk: 0.2.174, runner_commit: ...}
checks_by_agent: [cheme check, cheme maturity, ...]      # what the agent ran, from the transcript
checks_after_run:                                       # re-run by the runner on end_commit
  - {command: cheme check, exit: 1, summary: "..."}
outcome: {result: success, guard_denials: 0, report: "..."}
observed_later: {}          # facts added after the run, with the date they were observed
```

Unknown values are `null`, never estimates.

## Writing records

The agent runner (`agent.py`) writes the folder and commits it as the run's last commit. Write
the records of other runs by hand in the same format.

## Tagging a design for the paper

```sh
git tag -a paper/<process-id>-v1 <commit> -m "<process-id> v1: runs <run-id>, <run-id>"
```

The commit must contain the chosen design and the records of every run that produced it. Push
tags only when the design is final (`git push origin paper/<process-id>-v1`).
