#!/usr/bin/env python3
"""Run one stage of a staged agent design run, or the independent review after it.

    python3 scripts/agent-run/run_stage.py stage S1 --budget 3
    python3 scripts/agent-run/run_stage.py review S1 --budget 2
    python3 scripts/agent-run/run_stage.py stage S2 --budget 7 --dry-run   # print the prompt

Standard library only, Python 3.9 or later (macOS's ``/usr/bin/python3`` runs it); run it from
the plant repository root. It needs ``cheme`` and ``claude`` (Claude Code) on PATH, or
``CHEME`` / ``CLAUDE_BIN`` naming them.

The prompt is built from the repository, not from a plan written in advance:

- ``scripts/agent-run/spec.md``: the plant specification (one file, never repeated by hand);
- ``scripts/agent-run/stages.json``: per stage its ``target`` (a plant.yaml stage), ``task`` and
  ``budget_usd``;
- ``THIS STAGE``: the task, then what ``cheme status --json`` says is still to do for the
  target stage -- the sheets already drawn (not to be drawn again), the empty or planned sheets,
  the failing gates of every stage up to the target;
- ``FIX FIRST``: the open review findings (``cheme status``) and the previous review's
  ``carry_over`` list (``build/agent-run/<previous>/review.json``).

Everything a run produces goes to ``build/agent-run/<stage>/`` (``--out``): ``prompt.txt``,
``launch.json`` (command, versions, time), ``result.json`` (Claude Code's JSON output) and
``stderr.log``. Copy it into the run record (``docs/agent-design-run.md`` in cheme-as-code).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import string
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def tool(env: str, name: str, required: bool = True) -> str:
    found = os.environ.get(env) or shutil.which(name)
    if not found:
        if not required:  # a dry run only prints the command
            return name
        sys.exit(f"{name} not found: put it on PATH or set {env}")
    return found


def load_plan(path: Path) -> dict[str, dict]:
    stages = json.loads(path.read_text(encoding="utf-8"))["stages"]
    return {stage["id"]: stage for stage in stages}


def status(cheme: str) -> dict:
    result = run([cheme, "status", "--json"])
    if result.returncode != 0:
        sys.exit(f"cheme status failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def stages_up_to(data: dict, target: str) -> list[str]:
    stages = data["plant"]["stages"]
    return stages[: stages.index(target) + 1] if target in stages else stages


def this_stage(stage: dict, data: dict) -> str:
    """The stage task followed by what the repository says is left for its target stage."""
    lines = [stage["task"].strip(), ""]
    drawn = [s["id"] for s in data["sheets"] if s["state"] == "drawn"]
    todo = [f"{s['id']} ({s['state']})" for s in data["sheets"] if s["state"] != "drawn"]
    if drawn:
        lines.append(
            "Already drawn (edit them only to fix findings, never draw them again): "
            + ", ".join(drawn)
        )
    if todo:
        lines.append("Not drawn yet: " + ", ".join(todo))
    if data.get("next_sheet"):
        lines.append(f"Next sheet to draw: {data['next_sheet']}")
    failing = [
        f"[{name}] {gate['id']}: {gate['detail'] or gate['title']}"
        for name in stages_up_to(data, stage["target"])
        for gate in data["gates"].get(name, [])
        if gate["status"] == "fail"
    ]
    lines.append(
        f"Failing gates up to stage {stage['target']}: "
        + ("; ".join(failing) if failing else "none")
    )
    v = data["validation"]
    lines.append(
        f"cheme validate now: {v['errors']} error(s), {v['warnings']} warning(s)"
        + (
            " (not on a P&ID, by sheet: "
            + ", ".join(f"{k} {n}" for k, n in v["not_on_pid"].items())
            + ")"
            if v["not_on_pid"]
            else ""
        )
    )
    return "\n".join(lines)


def fix_first(stage_id: str, plan: dict[str, dict], data: dict, out_root: Path) -> str:
    ids = list(plan)
    previous = ids[ids.index(stage_id) - 1] if ids.index(stage_id) > 0 else None
    lines = []
    if previous:
        review = out_root / previous / "review.json"
        if review.is_file():
            carry = json.loads(review.read_text(encoding="utf-8")).get("carry_over") or []
            lines += [f"{i}) {item}" for i, item in enumerate(carry, 1)]
    for row in data["reviews"]["open"]:
        lines.append(f"- open review finding {row['id']} ({row['severity']}): {row['finding']}")
    return "\n".join(lines) or "nothing"


def fill(template: Path, values: dict[str, str]) -> str:
    return string.Template(template.read_text(encoding="utf-8")).safe_substitute(values)


def launch(args: argparse.Namespace, prompt: str, out: Path, budget: float, max_turns: int) -> int:
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.txt").write_text(prompt, encoding="utf-8")
    tools = [
        line.strip()
        for line in (HERE / "allowed-tools.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    command = [
        tool("CLAUDE_BIN", "claude", required=not args.dry_run),
        "-p",
        prompt,
        "--output-format",
        "json",
        "--max-turns",
        str(max_turns),
        "--max-budget-usd",
        f"{budget:g}",
        "--settings",
        ".claude/settings.json",
        "--allowedTools",
        *tools,
    ]
    shown = [c if c != prompt else "<prompt.txt>" for c in command]
    meta = {
        "stage": args.stage,
        "mode": args.mode,
        "command": shown,
        "budget_usd": budget,
        "max_turns": max_turns,
        "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "cheme": run([tool("CHEME", "cheme"), "--version"]).stdout.strip(),
        "head": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
    }
    if args.dry_run:
        print(prompt)
        print(f"\n(dry run: would run {' '.join(shown)}; prompt in {out / 'prompt.txt'})")
        return 0
    result, log = out / "result.json", out / "stderr.log"
    with result.open("w", encoding="utf-8") as stdout, log.open("w", encoding="utf-8") as stderr:
        code = subprocess.run(command, stdout=stdout, stderr=stderr, check=False).returncode
    meta["finished"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    meta["exit_code"] = code
    (out / "launch.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"{args.stage} {args.mode}: exit {code}; output in {out}")
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("mode", choices=["stage", "review"])
    parser.add_argument("stage", help="Stage id of stages.json, e.g. S1.")
    parser.add_argument("--budget", type=float, help="USD cap (default: stages.json).")
    parser.add_argument("--max-turns", type=int, default=200)
    parser.add_argument("--plan", type=Path, default=HERE / "stages.json")
    parser.add_argument("--spec", type=Path, default=HERE / "spec.md")
    parser.add_argument("--out", type=Path, help="Output directory (default build/agent-run).")
    parser.add_argument("--dry-run", action="store_true", help="Print the prompt, run nothing.")
    args = parser.parse_args(argv)
    if not Path("plant.yaml").is_file():
        sys.exit("run it from the plant repository root (no plant.yaml here)")
    plan = load_plan(args.plan)
    if args.stage not in plan:
        sys.exit(f"unknown stage {args.stage}; {args.plan} has {', '.join(plan)}")
    stage = plan[args.stage]
    spec = args.spec.read_text(encoding="utf-8").strip()
    out_root = args.out or Path("build") / "agent-run"
    data = status(tool("CHEME", "cheme"))
    values = {
        "STAGE": args.stage,
        "TARGET": stage["target"],
        "SPEC": spec,
        "TASK": stage["task"].strip(),
        "THIS_STAGE": this_stage(stage, data),
        "FIX_FIRST": fix_first(args.stage, plan, data, out_root),
        "BUDGET": f"{args.budget or stage.get('budget_usd', 5):g}",
        "OUT": str(out_root / args.stage),
    }
    if args.mode == "stage":
        prompt = fill(HERE / "stage-prompt.md", values)
        budget = args.budget or float(stage.get("budget_usd", 5))
    else:
        result = out_root / args.stage / "result.json"
        values["RESULT"] = result.read_text(encoding="utf-8")[-4000:] if result.is_file() else "{}"
        prompt = fill(HERE / "reviewer-prompt.md", values)
        budget = args.budget or float(stage.get("review_budget_usd", 2))
    out = out_root / args.stage / ("review" if args.mode == "review" else "")
    return launch(args, prompt, out, budget, args.max_turns)


if __name__ == "__main__":
    sys.exit(main())
