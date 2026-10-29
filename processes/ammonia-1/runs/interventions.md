# ammonia-1 run: human actions and orchestration edits

Every human action (key switch, answer to a question, prompt change, manual fix, decision) and
every orchestration edit, with time, what, why and commit, written as it happens. Merges by
reviewer agents are not listed here (see `ledger.csv`). Times are local (CET, UTC+1).

| id | time | who | what | why | commit |
|---|---|---|---|---|---|
| I-000 | 2026-10-29 08:40 | human (owner) | Task brief for the run given to the orchestrator (Claude Code session, model claude-opus-5-5): targets, gates, caps, budget batches, accounting | start of the run | - |
| I-001 | 2026-10-29 09:25 | human (owner) | Decision: implementation and fix jobs run with `--approve deny`; the orchestrator pushes their branch and opens the PR with the job's own `build/pr-body.md`; reviewers (`--approve auto`) merge | core v1.0.0's runner refuses every `git push` under `--approve deny` (no own-branch exception); core is not changed during the run | plan commit |
| O-001 | 2026-10-29 08:45-09:10 | orchestrator | Step 0: verified tag v1.0.0 = 9eff826 on core; installed `cheme` from the tag; agent-cli checkout detached at the tag; `cheme validate` 0 errors, `cheme migrate --check` nothing to migrate (no migration job); started Docker Desktop and built `cheme-dwsim:9.0.5` from core v1.0.0 `docker/dwsim/Dockerfile` | brief, Step 0 | - |
| O-002 | 2026-10-29 09:18 | orchestrator | Wrote the held-back benchmark `benchmarks/ammonia.yaml` from the EU LVIC-AAF BREF (2007) and the IEA Ammonia Technology Roadmap (2021) on branch `benchmark/ammonia` (7651243); hash and time posted on #86 (comment 6491606780), without values | brief, Step 0; held back from every job | 7651243 |
| O-003 | 2026-10-29 09:30 | orchestrator | Wrote `plan.md`, the role preambles and section tasks in `orchestration/prompts/`, `ledger.csv` (three basis rows from the 2026-10-27 run records) and this file | brief, Step 0 | plan commit |
