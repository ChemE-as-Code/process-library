# ammonia-1 platform-paper run: plan

The main case study of the ChemE-as-Code platform paper (process-library#86). Goal: take
ammonia-1 from its concept state to a complete design (simulation, basic engineering, HAZOP,
datasheets, relief, detail gates as far as they go), AI-generated end to end, with every session,
cost, check result and human action recorded as it happens.

Written 2026-10-29 before any run job; committed and tagged `nh3-run-start` together with every
prompt in `orchestration/prompts/`. Changes to this plan after the tag are interventions
(`interventions.md`).

## Starting point (not redone)

Concept stage as of process-library `main` at tag `nh3-run-start`: 1,500 t/d natural-gas SMR,
air-fed secondary reformer, HT/LT shift, aMDEA (CO2 vented), methanation, synthesis loop, purge
recovery; 7 blocks / 51 steps, BFD/PFD, 44 equipment items, DESIGN.md D-001..D-021, open inputs
I-01..I-10, preliminary LCI, review `reviews/2026-10-27-pfd-lci-review.md` (R-01..R-05 open,
R-03 = the unsourced natural-gas feed). No process simulation: separators, CO2 removal, purge
recovery, steam system and duties are specified values (D-006). Earlier sessions
`runs/20261027-*` (pre-release core 44680fa) are the **basis (pre-existing)**, ledger rows kept
apart from this run.

## Versions (fixed for the whole run)

- core / `cheme` / `agent-cli`: tag **v1.0.0** = commit `9eff8266225c078b56acccd8e746f546c3303ebd`
  (`cheme 1.0.0 (pyDEXPI 2.1.0)`, installed with `uv tool install ...core.git@v1.0.0`; the
  agent-cli checkout is detached at the tag). Model `claude-opus-5-5`, effort high.
- DWSIM: Docker 29.9.2, image `cheme-dwsim:9.0.5` (id b2d8ebbbe723), built from core v1.0.0
  `docker/dwsim/Dockerfile` as core's README describes (linux/amd64 on an arm64 host).
- `cheme validate`: 0 errors; `cheme migrate --check`: nothing to migrate (no migration job).
- Held-back benchmark: `benchmarks/ammonia.yaml` on branch `benchmark/ammonia`, commit
  `7651243b52c6f124d943505e3fd8a2aec8cf8ab1` (2026-10-29T09:18:55+01:00), posted on #86. No job
  checks that branch out; no prompt contains its values. Evaluated only after the design is final.

## Sections, jobs and caps (USD)

One implementation job per section (S3 in three jobs), each followed by an independent review job.
Branches `stage/<stage>-<topic>` from `origin/main` at the section start, one worktree each
(`~/Developer/test/wt/nh3-<topic>`), job cwd `processes/ammonia-1`.

| S | section | branch | jobs (cap) | gates the section must pass |
|---|---|---|---|---|
| S1 | Concept close-out | `stage/concept-closeout` | implement 10 | all concept gates (design-basis, concept-lists, process-concept, process-balances, process-links-concept, assumptions-marked, layout-plot-plan, issues-concept); R-01..R-05 closed or carried with a reason; I-01..I-10 resolved or ASSUMED with a reason; plot plan; class 5 estimate + screening TEA (`estimate/tea.yaml`); **concept sign-off** |
| S2 | Process simulation | `stage/basic-simulation` | implement 25 | `cheme process simulate --check` converged for every design-basis case; recycles converged; `process-balances` ok on simulated values; energy audit closed; gate `maturity-balanced` (template, uncommented) evaluated; `cheme maturity` reported, with the exact unsupported requirement if core#315 caps it |
| S3 | P&IDs | `stage/basic-pids-{front,mid,loop}` | 3 x implement 15 | pids-exist, pids-valid (0 errors), drawing-clean, process-basic, process-links; every section of the PFD on a sheet |
| S4 | Control and lists | `stage/basic-control-lists` | implement 15 | lists complete and linked (validate clean), control loops, sequences, interlocks, cause and effect (`cheme control report` clean), PFD current |
| S5 | 3D layout, MTO, class 4 estimate | `stage/basic-layout` | implement 25 | layout-3d (every DN25+ process line routed), lifting-study, mto, gate `tea` (template, uncommented); zones |
| S5r | Basic design and layout reviews | (on S5's branch) | review jobs from the review pool | design-review and layout-review (records `reviewer_kind: agent`), all basic gates; **basic sign-off** |
| S6 | HAZOP | `stage/basic-hazop` | implement 20 | HAZOP of all P&IDs rated against `safety/risk-matrix.yaml`; `cheme safety hazop check` clean; actions closed or carried with owner and reason |
| S7 | Datasheets | `stage/detail-datasheets` | implement 20 | gate `datasheets` (every equipment-list item, sized from the simulation, provenance on every value) |
| S8 | Relief | `stage/detail-relief` | implement 15 | relief scenarios for every relief device on the P&IDs (skill `relief-scenarios`), governing case and required capacity per device; what core cannot size is stated; gate `relief-on-pid` (template, uncommented) |
| S9 | Detail gates | `stage/detail-gates` | implement 15 | detail gates as far as they go (control-complete, layout-detail, electrical, hvac, datasheets, issues-detail); report pass/fail per gate |
| - | Reviews and fixes (all sections) | - | pool 40 | review 3-5, fix 3-6, sign-off 1.5, merge 1.5 per job |
| - | Reserve | - | 15 | only with the user's approval |
| | **Total** | | **245** | |

A gate is never relaxed, skipped or accepted to get further. A template gate is enabled
(uncommented, as the template documents it) where the section's target names it; that is not a
relaxation. A plant-specific gate added by a job is listed in its PR.

## Job flow per section

1. **implement** (`--approve deny`): does the section on its branch, commits, writes its PR body
   to `build/pr-body.md`, ends with `STATUS: DONE` or `STATUS: BLOCKED: <reason>`.
2. **orchestrator push** (decision 2026-10-29, `interventions.md` I-001): implementation and fix
   jobs cannot push under `--approve deny` in core v1.0.0, so the orchestrator pushes the branch
   and opens the PR with the job's `build/pr-body.md` unchanged. Ledger column `pushed_by`.
3. **review** (`--approve auto`, separate session): review record `reviews/<date>-<topic>.md`
   (`reviewer_kind: agent`, findings by severity), `VERDICT: approve` or `VERDICT: fix`. On
   approve and green CI it merges the PR (no sign-off sections); it never pushes to `main` and
   never force-pushes (hard-denied by the runner).
4. `fix` -> **fix** job (`--approve deny`, critical/high first) -> orchestrator push -> **review**
   again. At most two fix rounds; a third `fix` -> stop and ask the user.
5. Stage sign-off sections (S1 concept, S5r basic): after `VERDICT: approve` the reviewer does not
   merge; a **sign-off** job (author side, `--approve deny`) runs
   `cheme check --stage <s> --write --review <record>` as the branch's last commit; orchestrator
   push; a **merge** job (reviewer side, `--approve auto`) checks that only `checks/status.json`
   changed since the approved commit and CI is green, then merges. A sign-off counts once merged.
6. After every job: `cheme runs record` folder `runs/<run-id>/` present on the job's branch (and,
   after the merge, on `main`); ledger row appended and pushed (branch `run/nh3-ledger`, merged
   into `main` at each section end); tag `nh3-run-S<n>` on `main` after the section's merge.

Jobs are run by `uv run jobs.py <section>.json --total <left in the key batch>` from
`core/agent-cli` at v1.0.0, one section at a time (sections depend on each other).

## Budget, key batches and stop rules

- Key batch 1: USD 150 (`--total 150` across batch 1). Before starting a job, if the batch's spend
  plus that job's cap would exceed 150: stop at that clean point (nothing running, all branches
  pushed, ledger current) and ask the user to switch the key. The ledger records the batch
  (`batch 1`, `batch 2`), never the key.
- A job that hits its cap stops; caps are not raised without asking.
- Stop and ask when: the key switch point is reached; DWSIM cannot be started; core needs a fix
  (one core issue per platform problem, linked in the ledger; core is not changed during the
  run); the design brief would change; a gate would have to be relaxed or accepted; a job ends
  BLOCKED twice on the same problem; a review still says `fix` after two rounds.

## Records

- `runs/ledger.csv`: one row per session: run_id, job, section, role
  (implement/review/fix/signoff/merge), key_batch, model, cost_usd, input/output/cache_read/
  cache_write tokens, turns, wall_s, start_commit, end_commit, exit (DONE/BLOCKED/cap/crash),
  pr, pushed_by, merged_by (session id), gates_passed/gates_total, maturity_after,
  findings_critical/high/medium/low, core_issue, notes. Basis rows first, marked `basis
  (pre-existing)`.
- `runs/interventions.md`: every human action and every orchestration edit (time, what, why,
  commit). Agent merges are listed in the ledger, not here.
- `runs/<run-id>/`: written by `cheme runs record` for every job.
- Prompts: `orchestration/prompts/` (committed before the run); per-job task files as generated
  are committed with the ledger.

## Final report

Comment on #86 and to the user: sections reached and signed off; gates per stage; calculation
maturity and what blocks the next level; simulation (cases converged, property package, what is
simulated and what stays specified); cost and tokens per section, per key batch and total;
"first complete basic-engineering draft" vs "reported state"; sessions, PRs, agent merges, human
interventions; review findings found and fixed; core issues filed. Only then: bind and evaluate
`benchmarks/ammonia.yaml` (in range / out of range with reasons). Plainly: what was assumed, what
was not reached, what the checks cannot see.
