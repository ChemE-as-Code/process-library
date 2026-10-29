"""Append one session's row to runs/ledger.csv (ammonia-1 platform-paper run).

    python3 ledger_row.py LEDGER RUNS_JSONL RUN_ID JOB SECTION ROLE KEY_BATCH WORKTREE \
        [--pr N] [--pushed-by X] [--merged-by X] [--review FILE] [--core-issue URL] [--notes T]

Cost, tokens, turns, wall time and exit come from agent-cli's runs.jsonl (the API's numbers);
start/end commit from the run record `runs/<run-id>/run.yaml` on the job's branch; gates and
maturity from `cheme check` / `cheme maturity` run in WORKTREE/processes/ammonia-1 right after
the job; findings by severity from the review record the job wrote (review jobs only).
Standard library only; nothing is estimated: a value that cannot be read stays empty.
"""

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

COLS = ("run_id,job,section,role,key_batch,model,cost_usd,input_tokens,output_tokens,"
        "cache_read_tokens,cache_write_tokens,turns,wall_s,start_commit,end_commit,exit,pr,"
        "pushed_by,merged_by,gates_passed,gates_total,maturity_after,findings_critical,"
        "findings_high,findings_medium,findings_low,core_issue,notes").split(",")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    p = argparse.ArgumentParser()
    for a in ("ledger", "runs_jsonl", "run_id", "job", "section", "role", "key_batch", "worktree"):
        p.add_argument(a)
    for o in ("--pr", "--pushed-by", "--merged-by", "--review", "--core-issue", "--notes"):
        p.add_argument(o, default="")
    a = p.parse_args()
    rec = next((json.loads(l) for l in Path(a.runs_jsonl).read_text().splitlines()
                if json.loads(l).get("run_id") == a.run_id), {})
    u = rec.get("usage") or {}
    plant = Path(a.worktree) / "processes" / "ammonia-1"
    folder = next(iter(sorted((plant / "runs").glob(a.run_id.split("-", 2)[0] + "-*-" + a.job.lower()))), None)
    start = end = ""
    if folder and (folder / "run.yaml").exists():
        text = (folder / "run.yaml").read_text()
        start = (re.search(r"^start_commit:\s*'?(\w+)", text, re.M) or [None, ""])[1][:12]
        end = (re.search(r"^end_commit:\s*'?(\w+)", text, re.M) or [None, ""])[1][:12]
    check = run(["cheme", "check"], plant).stdout
    ok, fail = len(re.findall(r"^ok ", check, re.M)), len(re.findall(r"^FAIL ", check, re.M))
    mat = run(["cheme", "maturity"], plant).stdout
    levels = re.findall(r"^(sourced|balanced|predictive|engineering): .* -- (\w+)$", mat, re.M)
    reached = [lv for lv, verdict in levels if verdict == "ok"]
    sev = {"critical": "", "high": "", "medium": "", "low": ""}
    if a.review and Path(a.review).exists():
        body = Path(a.review).read_text().lower()
        for s in sev:
            sev[s] = str(len(re.findall(rf"\b(severity:\s*{s}|\({s}\)|\| {s} \|)", body)))
    final = rec.get("final_status") or ""
    exit_ = {"DONE": "DONE", "BLOCKED": "BLOCKED"}.get(final, "") or (
        "cap" if rec.get("subtype") == "error_max_budget_usd" else
        "crash" if rec.get("subtype") in ("crashed", "no-result") else final or rec.get("subtype", ""))
    row = {"run_id": a.run_id, "job": a.job, "section": a.section, "role": a.role,
           "key_batch": a.key_batch, "model": rec.get("model"), "cost_usd": rec.get("cost_usd"),
           "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
           "cache_read_tokens": u.get("cache_read_input_tokens"),
           "cache_write_tokens": u.get("cache_creation_input_tokens"), "turns": rec.get("num_turns"),
           "wall_s": rec.get("wall_s"), "start_commit": start, "end_commit": end, "exit": exit_,
           "pr": a.pr, "pushed_by": a.pushed_by, "merged_by": a.merged_by, "gates_passed": ok,
           "gates_total": ok + fail, "maturity_after": reached[-1] if reached else "none",
           "findings_critical": sev["critical"], "findings_high": sev["high"],
           "findings_medium": sev["medium"], "findings_low": sev["low"],
           "core_issue": a.core_issue, "notes": a.notes}
    with open(a.ledger, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=COLS).writerow(row)
    print({k: row[k] for k in ("run_id", "cost_usd", "exit", "gates_passed", "gates_total", "maturity_after")})


if __name__ == "__main__":
    main()
