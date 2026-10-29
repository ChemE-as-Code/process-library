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
| O-004 | 2026-10-29 10:57 | orchestrator | Merged #240 (plan, prompts, accounting files; 93 checks green) and tagged `nh3-run-start` on `main` at ffb1ea7 | brief, Step 0: plan committed and tagged before the run | ffb1ea7 |
| O-005 | 2026-10-29 11:00 | orchestrator | S1 started: worktree `wt/nh3-concept-closeout` on `stage/concept-closeout` from ffb1ea7; job file `S1-implement` (preamble `implement.md` + section S1 text, cap 10, `--approve deny`), `jobs.py --total 150` (key batch 1) | plan, S1 | - |
| O-006 | 2026-10-29 11:20 | orchestrator | S1-implement DONE ($6.50); pushed `stage/concept-closeout` and opened #241 with the job's `build/pr-body.md` unchanged (I-001); ledger row added | plan step 2 | - |
| O-007 | 2026-10-29 11:25 | orchestrator | Prompt change: `review.md` and `merge.md` now end with `VERDICT: ...` followed by `STATUS: DONE`. The first S1-review session ended correctly with `VERDICT: approve`, but core v1.0.0's runner recognises only `VERDICT: merge\|fix`, so jobs.py restarted it (second session $0.33 confirmed the verdict). Orchestration error, not a core defect (the runner's vocabulary is documented as merge\|fix). Ledger tool: findings by severity now passed explicitly from the review's summary (a regex miscounted) | the brief's `VERDICT: approve\|fix` vs the runner's vocabulary | this commit |
| O-008 | 2026-10-29 11:26 | orchestrator | S1 review: VERDICT approve (record `reviews/2026-10-29-concept.md`, 0 critical, 0 high, 1 medium, 3 low; pushed by the reviewer); next: sign-off job, then merge job | plan step 5 | - |
| O-009 | 2026-10-29 11:27 | orchestrator | S1-signoff DONE ($0.29, commit c6a1dcd: checks/status.json only); pushed the branch | plan step 5 | c6a1dcd |
| O-010 | 2026-10-29 11:40 | orchestrator | S1-merge merged #241 (VERDICT approve, 36c6a9e). Its own run record (committed by `cheme runs record` after the merge, f0cafa8) is carried to `main` by cherry-picking it onto `run/nh3-ledger` | every job's run record must reach main | f0cafa8 |
