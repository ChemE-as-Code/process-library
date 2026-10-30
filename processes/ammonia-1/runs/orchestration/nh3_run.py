"""Driver of the ammonia-1 platform-paper run (process-library#86): sections S2..S9 after S1.

    zsh -c 'source ~/.zshrc; uv run python jobs/nh3/nh3_run.py'   (from core/agent-cli)

It runs the flow of runs/plan.md section by section, every agent session through core's
jobs.py (agent.py, guards, caps, cheme runs record):
  implement (--approve deny) -> orchestrator pushes, opens the PR with the job's build/pr-body.md
  -> review (--approve auto; merges on approve unless the section ends with a sign-off)
  -> on fix: fix job -> push -> review again (max 2 fix rounds, then a third only with the
     owner's standing permission of 2026-10-29 to continue autonomously; recorded)
  -> sign-off sections: sign-off job -> push -> merge job
After every session: a ledger row (ledger_row.py), run records carried to main, interventions
entries; at a section's end: the ledger PR merged and tag nh3-run-S<n>.
Key batches: batch 1 is the key in ANTHROPIC_API_KEY (limit 150, see I-004); when the next job's
cap would exceed it, the driver switches at that clean point to batch 2, the key in
ANTHROPIC_API_KEY_personal_account (limit 190; owner, 2026-10-29). Keys are never printed,
logged or written; the child sessions never see the second variable.
State in logs/nh3-driver.state.json: rerun to resume. Lines starting NOTIFY/STOP in
logs/nh3-driver.log are for the orchestrator.
"""

import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

AC = Path(__file__).resolve().parents[2]            # core/agent-cli
T = AC.parents[1]                                   # ~/Developer/test
LIB, WT = T / "process-library", T / "wt"
LEDGER_WT = WT / "nh3-ledger"
RUNS = LEDGER_WT / "processes/ammonia-1/runs"
J = AC / "jobs" / "nh3"
PROMPTS = RUNS / "orchestration" / "prompts"
STATE = AC / "logs" / "nh3-driver.state.json"
LOG = AC / "logs" / "nh3-driver.log"
LIMITS = {1: 150.0, 2: 190.0}
BATCH_OF = {}  # run_id -> key batch, for the ledger
CAPS = {"review": 4.0, "fix": 6.0, "signoff": 1.5, "merge": 2.0, "ci-merge": 3.0}
FIND_RULE = ("\n\nAt the very end, before the VERDICT line, add one line exactly like "
             "`FINDINGS: critical=<n> high=<n> medium=<n> low=<n>` counting only the findings "
             "new in this review (not carried ones).\n")

SECTIONS = [  # id, tag, branch, worktree, cap, task key in sections.md, signoff stage, reviews
    dict(id="S2", tag="S2", branch="stage/basic-simulation", wt="nh3-basic-simulation", cap=25,
         key="S2", resume_after="S2-continue", reviews=["simulation"]),
    dict(id="S3a", tag=None, branch="stage/basic-pids-front", wt="nh3-basic-pids-front", cap=15, key="S3a", reviews=["pids-front"]),
    dict(id="S3b", tag=None, branch="stage/basic-pids-mid", wt="nh3-basic-pids-mid", cap=15, key="S3b", reviews=["pids-mid"]),
    dict(id="S3c", tag="S3", branch="stage/basic-pids-loop", wt="nh3-basic-pids-loop", cap=15, key="S3c", reviews=["pids-loop"]),
    dict(id="S4", tag="S4", branch="stage/basic-control-lists", wt="nh3-basic-control-lists", cap=15, key="S4", reviews=["control-lists"]),
    dict(id="S5", tag="S5", branch="stage/basic-layout", wt="nh3-basic-layout", cap=25, key="S5",
         reviews=["design", "layout"], signoff="basic"),
    # O-032: S5 stopped after 3 rounds; S5b closes the two failing basic gates on the same branch/PR.
    # On a further stop the run continues with S6-S8 (from main) and leaves PR #257 open; S9 needs S5b.
    dict(id="S5b", tag="S5", branch="stage/basic-layout", wt="nh3-basic-layout", cap=20, key="S5b",
         reviews=["design", "layout"], signoff="basic", continue_on_stop=True),
    dict(id="S6", tag="S6", branch="stage/basic-hazop", wt="nh3-basic-hazop", cap=20, key="S6", reviews=["hazop"]),
    dict(id="S7", tag="S7", branch="stage/detail-datasheets", wt="nh3-detail-datasheets", cap=20, key="S7", reviews=["datasheets"]),
    dict(id="S8", tag="S8", branch="stage/detail-relief", wt="nh3-detail-relief", cap=15, key="S8", reviews=["relief"]),
    # O-041: S5 (#257) waits for the owner; S9 stacks on it: base stage/basic-layout, brought up to
    # date with main by a sync job first; the S9 PR is approved but not merged (stacked).
    dict(id="S9", base="stage/basic-layout", sync="nh3-basic-layout", no_merge=True, tag="S9", branch="stage/detail-gates", wt="nh3-detail-gates", cap=15, key="S9", reviews=["detail-gates"]),
]


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def sh(cmd, cwd=None, check=True, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd))}: {(r.stderr or r.stdout).strip()[-600:]}")
    return r


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {"batch": 1, "spent": {"1": None, "2": 0.0}, "done": {}, "o": None}


def save(st):
    STATE.write_text(json.dumps(st, indent=1))


def ledger_spent(batch):
    rows = list(csv.DictReader((RUNS / "ledger.csv").open()))
    return sum(float(r["cost_usd"] or 0) for r in rows if r["key_batch"] == f"batch {batch}")


def next_o(st):
    if st["o"] is None:
        nums = [int(m) for m in re.findall(r"^\| O-(\d+) ", (RUNS / "interventions.md").read_text(), re.M)]
        st["o"] = max(nums or [0])
    st["o"] += 1
    return f"O-{st['o']:03d}"


def intervention(st, what, why="plan", commit="-"):
    o = next_o(st)
    with (RUNS / "interventions.md").open("a") as f:
        f.write(f"| {o} | {datetime.now():%Y-%m-%d %H:%M} | orchestrator (driver) | {what} | {why} | {commit} |\n")
    save(st)


def commit_ledger(msg):
    sh(["git", "add", "processes/ammonia-1/runs"], cwd=LEDGER_WT)
    if sh(["git", "diff", "--cached", "--quiet"], cwd=LEDGER_WT, check=False).returncode:
        sh(["git", "commit", "-q", "-m", msg + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=LEDGER_WT)
    sh(["git", "push", "-q"], cwd=LEDGER_WT, check=False)


def section_text(key):
    t = (PROMPTS / "sections.md").read_text()
    if key.startswith("S3"):
        block = t[t.index("## S3a"):t.index("## S4")]
        part = {"S3a": "S3a (front)", "S3b": "S3b (mid)", "S3c": "S3c (loop)"}[key]
        return block + f"\nYour part: **{part}** only; the other parts are separate sections.\n"
    heads = [m.start() for m in re.finditer(r"^## S", t, re.M)]
    start = t.index(f"## {key} ")
    end = next((h for h in heads if h > start), len(t))
    if key == "S5":  # the basic reviews and sign-off (S5r) run on S5's branch
        end = next((h for h in heads if h > t.index("## S5r")), len(t))
    return t[start:end]


def env_for(batch):
    e = dict(os.environ)
    second = e.pop("ANTHROPIC_API_KEY_personal_account", None)
    if batch == 2:
        if not second:
            raise RuntimeError("batch 2 key variable not set")
        e["ANTHROPIC_API_KEY"] = second
    return e


def run_job(st, name, cwd, preamble, task, cap, approve):
    """One session via jobs.py; returns (runs.jsonl record, log text)."""
    batch = st["batch"]
    if st["spent"][str(batch)] + cap > LIMITS[batch]:
        if batch == 1:
            st["batch"] = batch = 2
            intervention(st, f"Key switch at a clean point before {name}: batch 1 booked "
                         f"${st['spent']['1']:.2f} of {LIMITS[1]:.0f}; next cap {cap}. From here batch 2 "
                         f"(the owner's second key; never printed)", "brief: switch keys only between jobs; owner 2026-10-29 evening")
            commit_ledger(f"ammonia-1 run: key switch to batch 2 before {name}")
            log(f"NOTIFY key switch to batch 2 before {name}")
        if st["spent"]["2"] + cap > LIMITS[2]:
            log(f"STOP budget: batch 2 booked ${st['spent']['2']:.2f}, next {name} cap {cap}")
            raise SystemExit(2)
    (J / f"{name}.md").write_text(task)
    jf = J / f"{name}.json"
    jf.write_text(json.dumps({"preamble_file": preamble, "defaults": {"budget": cap, "approve": approve,
                  "effort": "high", "max_restarts": 1}, "jobs": [{"name": name, "cwd": os.path.relpath(cwd, J),
                  "budget": cap, "task_file": f"{name}.md"}]}, indent=1))
    before = len((AC / "runs.jsonl").read_text().splitlines())
    left = LIMITS[batch] - st["spent"][str(batch)]
    log(f"{name}: start (batch {batch}, cap {cap}, approve {approve})")
    r = sh(["uv", "run", "-q", "jobs.py", str(jf), "--total", f"{left:.2f}", "--max-sessions", "1"],
           cwd=AC, check=False, env=env_for(batch))
    new = [json.loads(l) for l in (AC / "runs.jsonl").read_text().splitlines()[before:]]
    recs = [x for x in new if x["run_id"].endswith(name)]
    for x in recs:
        st["spent"][str(batch)] += x.get("cost_usd") or 0
        BATCH_OF[x["run_id"]] = batch
    save(st)
    rec = recs[-1] if recs else {}
    text = "".join((AC / "logs" / f"{x['run_id']}.log").read_text() for x in recs
                   if (AC / "logs" / f"{x['run_id']}.log").exists())
    log(f"{name}: end {rec.get('final_status')} {rec.get('subtype')} ${sum((x.get('cost_usd') or 0) for x in recs):.2f} ({len(recs)} session(s))")
    return recs, text


def row(recs, job, sec, role, wt, pr="", pushed="", merged="", findings="", notes=""):
    for x in recs:
        args = ["python3", str(RUNS / "orchestration/ledger_row.py"), str(RUNS / "ledger.csv"), str(AC / "runs.jsonl"),
                x["run_id"], job, sec, role, f"batch {BATCH_OF.get(x['run_id'], 1)}", str(wt)]
        for k, v in (("--pr", pr), ("--pushed-by", pushed), ("--merged-by", merged), ("--findings", findings), ("--notes", notes)):
            if v:
                args += [k, v]
        sh(args, check=False)


def push(wt, branch):
    sh(["git", "push", "-q", "-u", "origin", branch], cwd=wt, check=False)


def pr_of(branch):
    out = sh(["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "number,state"], cwd=LIB).stdout
    prs = json.loads(out)
    return (str(prs[0]["number"]), prs[0]["state"]) if prs else (None, None)


def verdict(text):
    v = re.findall(r"VERDICT: (approve|fix|merge)", text)
    f = re.findall(r"FINDINGS: critical=(\d+) high=(\d+) medium=(\d+) low=(\d+)", text)
    return (v[-1] if v else None), (",".join(f[-1]) if f else "")


def carry_records(wt):
    """Run records committed on the stage branch after its merge (not on main) go via the ledger branch."""
    sh(["git", "fetch", "-q", "origin"], cwd=LEDGER_WT)
    plant = Path(wt) / "processes/ammonia-1/runs"
    have = set(sh(["git", "ls-tree", "--name-only", "origin/main", "processes/ammonia-1/runs/"], cwd=LEDGER_WT).stdout.split())
    for d in sorted(plant.glob("2026*")):
        rel = f"processes/ammonia-1/runs/{d.name}"
        if rel not in have and not (LEDGER_WT / rel).exists():
            sh(["cp", "-R", str(d), str(LEDGER_WT / "processes/ammonia-1/runs/")])


def end_section(st, sec):
    wt = WT / sec["wt"]
    carry_records(wt)
    sh(["git", "fetch", "-q", "origin"], cwd=LEDGER_WT)
    sh(["git", "merge", "-q", "--no-edit", "origin/main"], cwd=LEDGER_WT, check=False)
    for f in J.glob(f"{sec['id']}-*"):
        sh(["cp", str(f), str(RUNS / "orchestration/jobs/")], check=False)
    intervention(st, f"{sec['id']} merged; ledger PR for the section's accounting")
    commit_ledger(f"ammonia-1 run: {sec['id']} accounting")
    num, state = pr_of("run/nh3-ledger")
    if state != "OPEN":
        sh(["gh", "pr", "create", "--base", "main", "--head", "run/nh3-ledger", "--title",
            f"ammonia-1 run: accounting through {sec['id']}", "--body",
            "Ledger rows, interventions, job files and post-merge run records of the ammonia-1 run (#86). "
            "No design change.\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"], cwd=LIB, check=False)
        num, state = pr_of("run/nh3-ledger")
    time.sleep(60)
    sh(["gh", "pr", "checks", num, "--watch", "--interval", "30"], cwd=LIB, check=False)
    if sh(["gh", "pr", "merge", num, "--merge"], cwd=LIB, check=False).returncode == 0 and sec.get("tag"):
        sh(["git", "fetch", "-q", "origin"], cwd=LIB)
        m = sh(["gh", "pr", "view", num, "--json", "mergeCommit", "-q", ".mergeCommit.oid"], cwd=LIB).stdout.strip()
        tag = f"nh3-run-{sec['tag']}"
        sh(["git", "tag", "-a", tag, "-m", f"ammonia-1 run {sec['tag']} complete", m], cwd=LIB, check=False)
        sh(["git", "push", "-q", "origin", tag], cwd=LIB, check=False)
        log(f"NOTIFY {sec['id']} complete, tagged {tag} at {m[:12]}")
    sh(["git", "fetch", "-q", "origin"], cwd=LEDGER_WT)
    sh(["git", "merge", "-q", "--no-edit", "origin/main"], cwd=LEDGER_WT, check=False)
    sh(["git", "push", "-q"], cwd=LEDGER_WT, check=False)


def run_section(st, sec):
    sid, wt = sec["id"], WT / sec["wt"]
    plant = wt / "processes/ammonia-1"
    sh(["git", "fetch", "-q", "origin"], cwd=LIB)
    base = sec.get("base", "main")
    if sec.get("sync") and not st.get("synced", {}).get(sid):
        swt = WT / sec["sync"]
        sname = f"{sid}-sync-{base.split('/')[-1]}"
        recs, out = run_job(st, sname, swt / "processes/ammonia-1", "implement.md",
                            f"# Your job: bring `{base}` (checked out, open PR) up to date with main\n"
                            "Merge `origin/main` into this branch (`git fetch origin` then `git merge origin/main`). "
                            "main has the merged S6 HAZOP, S7 datasheets and S8 relief; this branch has the S5/S5b layout, "
                            "lifting and estimate work. Resolve every conflict by keeping both sides' intent: datasheets from "
                            "main (S7, complete) with this branch's sizing additions where they are better sourced; DESIGN.md "
                            "and PROGRESS.md with both sides' entries (renumber a clashing decision id and fix its references); "
                            "regenerate generated files (`cheme process build`, `cheme layout build`, `cheme assess mto --write`, "
                            "estimate) instead of hand-merging them. No engineering change beyond what the merge needs. "
                            "`cheme validate` 0 errors, report `cheme check --stage basic`. Commit the merge; do not push. "
                            "Write nothing to build/pr-body.md.\n", 6.0, "deny")
        row(recs, sname, sid, "sync", swt, pushed="orchestrator")
        push(swt, base)
        st.setdefault("synced", {})[sid] = True
        save(st)
        commit_ledger(f"ammonia-1 run: {sname} row")
    if not wt.exists():
        sh(["git", "worktree", "add", "-q", "-b", sec["branch"], str(wt), f"origin/{base}"], cwd=LIB)
    text = section_text(sec["key"])
    head = f"Branch: {sec['branch']} (checked out). Earlier sections are merged on main.\n\n"
    if base != "main":
        head = (f"Branch: {sec['branch']} (checked out), stacked on `{base}` (open PR, waiting for the owner's "
                "decisions: lifting acceptance, feed specification, risk matrix, estimate rates); its PR's base is "
                f"`{base}`. S6-S8 are merged on main and in `{base}`.\n\n")
    if not sec.get("resume_after"):
        recs, out = run_job(st, f"{sid}-implement", plant, "implement.md", f"# Your section: {sid} of ammonia-1\n" + head + text, sec["cap"], "deny")
        row(recs, f"{sid}-implement", sid, "implement", wt, pushed="orchestrator")
        final = recs[-1].get("final_status") if recs else None
        if not recs or final not in ("DONE", "BLOCKED"):
            c = round(sec["cap"] * 0.6, 2)
            intervention(st, f"{sid}-implement ended without DONE/BLOCKED ({(recs or [{}])[-1].get('subtype')}); one continuation job, cap {c} (owner: more budget if needed)", "owner 2026-10-29 evening")
            recs, out = run_job(st, f"{sid}-continue", plant, "implement.md", f"# Your section: {sid} of ammonia-1, continuation\n"
                                "The previous session stopped (cap or crash) before finishing; see git log, PROGRESS.md and build/. Finish the section.\n" + head + text, c, "deny")
            row(recs, f"{sid}-continue", sid, "implement", wt, pushed="orchestrator")
    push(wt, sec["branch"])
    num, state = pr_of(sec["branch"])
    if not num:
        body = plant / "build/pr-body.md"
        args = ["gh", "pr", "create", "--base", "main", "--head", sec["branch"], "--title", f"ammonia-1 {sid}: {sec['branch'].split('/')[-1]} (#86)"]
        args[4] = base
        args += ["--body-file", str(body)] if body.exists() else ["--body", f"Section {sid} of the ammonia-1 run (#86); the job wrote no build/pr-body.md.\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)"]
        sh(args, cwd=LIB, check=False)
        num, state = pr_of(sec["branch"])
        intervention(st, f"{sid}: pushed `{sec['branch']}`, opened #{num} with the job's own PR body (I-001)")
    commit_ledger(f"ammonia-1 run: {sid} implement rows, PR #{num}")
    signoff = sec.get("signoff")
    for rnd in range(1, 4):
        verdicts = []
        for topic in sec["reviews"]:
            rname = f"{sid}-review-{topic}-r{rnd}"
            rtask = (f"# Review this section's PR: {sid} of ammonia-1 (PR #{num}), round {rnd}\nReview topic for the record: `{topic}`.\n"
                     + ("This section ends with a stage sign-off: on `VERDICT: approve` do **not** merge.\n" if signoff or len(sec['reviews']) > 1 else "")
                     + (f"This PR is stacked on `{base}` (open): on `VERDICT: approve` do **not** merge.\n" if sec.get("no_merge") else "")
                     + head + text + FIND_RULE)
            recs, out = run_job(st, rname, plant, "review.md", rtask, CAPS["review"], "auto")
            v, f = verdict(out)
            verdicts.append(v)
            num, state = pr_of(sec["branch"])
            merged = recs[-1]["session_id"] if state == "MERGED" and recs else ""
            row(recs, rname, sid, "review", wt, pr=num, findings=f, merged=merged, notes=f"VERDICT: {v}")
            commit_ledger(f"ammonia-1 run: {rname} row")
        if all(v == "approve" for v in verdicts):
            break
        if rnd == 3:
            log(f"STOP {sid}: review still says fix after 3 rounds (PR #{num})")
            raise SystemExit(3)
        if rnd == 2:
            intervention(st, f"{sid}: review says fix after two rounds; a third round runs under the owner's standing permission to continue autonomously", "owner 2026-10-29 evening")
        fname = f"{sid}-fix-r{rnd}"
        recs, out = run_job(st, fname, plant, "fix.md", f"# Fix the open findings of the newest review of this section: {sid} (PR #{num}), round {rnd}\n" + head + text, CAPS["fix"], "deny")
        row(recs, fname, sid, "fix", wt, pr=num, pushed="orchestrator")
        push(wt, sec["branch"])
        cm = plant / "build/pr-comment.md"
        if cm.exists():
            sh(["gh", "pr", "comment", num, "--body-file", str(cm)], cwd=LIB, check=False)
        commit_ledger(f"ammonia-1 run: {fname} row")
    if signoff:
        recs, _ = run_job(st, f"{sid}-signoff", plant, "signoff.md", f"# Your job: sign off stage `{signoff}` of ammonia-1\n"
                          f"Branch: {sec['branch']} (checked out). Approving review records: the newest records in `reviews/` for topics {', '.join(sec['reviews'])} (PR #{num}). Use the design review record for `--review`.\n", CAPS["signoff"], "deny")
        row(recs, f"{sid}-signoff", sid, "signoff", wt, pr=num, pushed="orchestrator")
        push(wt, sec["branch"])
        recs, out = run_job(st, f"{sid}-merge", plant, "merge.md", f"# Your job: merge the signed-off stage `{signoff}` of ammonia-1 (PR #{num})\nBranch: {sec['branch']} (checked out).\n", CAPS["merge"], "auto")
        num, state = pr_of(sec["branch"])
        row(recs, f"{sid}-merge", sid, "merge", wt, pr=num, merged=(recs[-1]["session_id"] if state == "MERGED" and recs else ""), notes=f"VERDICT: {verdict(out)[0]}")
    num, state = pr_of(sec["branch"])
    if state != "MERGED" and not sec.get("no_merge"):
        recs, out = run_job(st, f"{sid}-ci-merge", plant, "review.md", f"# PR #{num} ({sid}) is approved by its review but not merged\n"
                            "Get its CI green (fix only what CI reports, in this section's scope) and merge it; if a fix needs more than CI causes, do not merge and say why.\n" + FIND_RULE, CAPS["ci-merge"], "auto")
        num, state = pr_of(sec["branch"])
        row(recs, f"{sid}-ci-merge", sid, "merge", wt, pr=num, merged=(recs[-1]["session_id"] if state == "MERGED" and recs else ""))
        if state != "MERGED":
            log(f"STOP {sid}: PR #{num} approved but not merged")
            raise SystemExit(4)
    end_section(st, sec)


def main():
    st = load()
    if st["spent"]["1"] is None:
        st["spent"]["1"] = ledger_spent(1)
        save(st)
    log(f"driver start: batch {st['batch']}, booked batch1 ${st['spent']['1']:.2f}, batch2 ${st['spent']['2']:.2f}")
    for sec in SECTIONS:
        if st["done"].get(sec["id"]):
            continue
        if sec.get("needs") and not st["done"].get(sec["needs"]):
            log(f"STOP {sec['id']}: needs {sec['needs']}, which is not merged")
            raise SystemExit(6)
        try:
            run_section(st, sec)
        except SystemExit as e:
            if sec.get("continue_on_stop") and e.code in (3, 4):
                intervention(st, f"{sec['id']} stopped (exit {e.code}); its PR stays open, the run goes on with the next independent sections", "owner 2026-10-29: work autonomously")
                commit_ledger(f"ammonia-1 run: {sec['id']} stopped, continuing")
                log(f"NOTIFY {sec['id']} stopped, continuing with the next sections")
                continue
            raise
        except Exception as e:  # noqa: BLE001  a driver error stops the run for the orchestrator
            log(f"STOP {sec['id']}: driver error {e}")
            raise SystemExit(5)
        st["done"][sec["id"]] = True
        save(st)
    log("NOTIFY ALL DONE")


if __name__ == "__main__":
    main()
