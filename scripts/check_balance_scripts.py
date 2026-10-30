# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Re-run each process's balance script and compare its output with the flowsheet values it sources.

A process whose flowsheet cannot be calculated by core yet gets its stream values and duties
from a standalone balance script, ``processes/<id>/scripts/<name>.py``, run with ``cheme run``.
The flowsheet (``process/flowsheet.yaml``) gives those values as ``provenance: assumed`` with a
``source`` that starts with the script's path (``"scripts/h2_balance.py: ..."``). This checker
stops the two from drifting apart (ADR 0024):

1. It collects every flowsheet value whose ``source`` starts with ``scripts/<name>.py``:
   ``streams[].state.<case>.<quantity>`` with quantity ``flow``, ``temperature``,
   ``pressure``, ``duty``, ``composition`` or ``phase``.
2. A script that follows the balance-output contract (its text names ``BALANCE_OUTPUT``) is
   re-run with ``cheme run scripts/<name>.py`` in the process folder, with the environment
   variable ``BALANCE_OUTPUT`` set to a file path; the script writes its values there as JSON::

       {"contract": "balance-output/1",
        "script": "scripts/h2_balance.py",
        "cases": {"design": {"S1": {"flow": 29303.44, "temperature": 288.15},
                             "S14": {"composition": {"H2": 0.74, "CH4": 0.056}},
                             "Q1": {"duty": 18.8}}}}

   Numbers are in the flowsheet's own units and basis (``units:``, the ``basis`` of the flow and
   of the composition), so they compare directly.
3. Every cited value must be in the output (else ``missing``) and agree within the tolerance
   (else ``drift``); a script that fails is an ``error``. A script without the contract is
   ``not-migrated``: reported, and run only with ``--run-unmigrated`` (then just for its exit
   code).

Tolerances: ``|flowsheet - script| <= abs + rel * |script|``.

- ``flow`` and ``duty``: the flowsheet's own ``tolerance`` (``abs``, ``rel``; default 1.0, 0.005),
  the same tolerance ``cheme validate`` applies to its balances;
- ``temperature``: abs 0.5 K; ``pressure``: abs 0.5 kPa, rel 0.001;
- ``composition``: per component, abs 1e-4, rel 0.005; a component in only one of the two is
  compared with zero;
- ``phase``: equal.

Exit status: 1 when any migrated script has a drift, a missing value or an error (``--strict``:
also when a cited script is not migrated), else 0. ``--markdown`` writes the drift table that a
pull request carries; ``--json`` the full report.

Run it with the cheme of library CI (pinned in .github/workflows/validate.yml): ``uv run
scripts/check_balance_scripts.py --library . [--process hydrogen-1 ...]``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shlex
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

CONTRACT = "balance-output/1"
ENV = "BALANCE_OUTPUT"
QUANTITIES = ("flow", "temperature", "pressure", "duty", "composition", "phase")
DEFAULT_TOLERANCE = {"abs": 1.0, "rel": 0.005}
FIXED_TOLERANCE = {
    "temperature": {"abs": 0.5, "rel": 0.0},
    "pressure": {"abs": 0.5, "rel": 0.001},
    "composition": {"abs": 1e-4, "rel": 0.005},
}
SOURCE = re.compile(r"^\s*(scripts/[\w.\-]+\.py)\b")
TIMEOUT_S = 900


@dataclass
class Cited:
    """One flowsheet value that names a script as its source."""

    script: str
    case: str
    stream: str
    quantity: str
    value: object
    source: str


@dataclass
class Finding:
    """The comparison of one cited value (one component of a composition)."""

    process: str
    script: str
    case: str
    stream: str
    quantity: str
    status: str  # ok | drift | missing
    flowsheet: object = None
    script_value: object = None
    deviation: float | None = None
    allowed: float | None = None


@dataclass
class ScriptResult:
    process: str
    script: str
    status: str  # checked | not-migrated | error | missing-script
    cited: int = 0
    message: str = ""
    findings: list[Finding] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        return self.status in ("error", "missing-script") or any(
            f.status != "ok" for f in self.findings
        )


def cited_values(flowsheet: dict) -> list[Cited]:
    """Every ``streams[].state.<case>.<quantity>`` whose source starts with a script path."""
    out = []
    for stream in flowsheet.get("streams") or []:
        if not isinstance(stream, dict):
            continue
        for case, state in (stream.get("state") or {}).items():
            if not isinstance(state, dict):
                continue
            for quantity in QUANTITIES:
                entry = state.get(quantity)
                if not isinstance(entry, dict):
                    continue
                match = SOURCE.match(str(entry.get("source") or ""))
                if not match:
                    continue
                value = entry.get("values") if quantity == "composition" else entry.get("value")
                out.append(
                    Cited(
                        match.group(1),
                        str(case),
                        str(stream.get("id")),
                        quantity,
                        value,
                        str(entry.get("source")),
                    )
                )
    return out


def tolerance(flowsheet: dict, quantity: str) -> dict:
    if quantity in FIXED_TOLERANCE:
        return FIXED_TOLERANCE[quantity]
    own = flowsheet.get("tolerance") or {}
    return {k: float(own.get(k, DEFAULT_TOLERANCE[k])) for k in DEFAULT_TOLERANCE}


def _number(x: object) -> float | None:
    if isinstance(x, bool) or x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _compare(fs: float, sc: float, tol: dict) -> tuple[bool, float, float]:
    dev = abs(fs - sc)
    allowed = tol["abs"] + tol["rel"] * abs(sc)
    return dev <= allowed, dev, allowed


def compare(process: str, cited: Cited, emitted: dict, flowsheet: dict) -> list[Finding]:
    """Compare one cited value with the script's output for its case and stream."""
    base = {"process": process, "script": cited.script, "case": cited.case, "stream": cited.stream}
    entry = (emitted.get(cited.case) or {}).get(cited.stream) or {}
    if cited.quantity not in entry:
        return [Finding(**base, quantity=cited.quantity, status="missing", flowsheet=cited.value)]
    got = entry[cited.quantity]
    tol = tolerance(flowsheet, cited.quantity)
    if cited.quantity == "phase":
        ok = str(got) == str(cited.value)
        return [
            Finding(
                **base,
                quantity="phase",
                status="ok" if ok else "drift",
                flowsheet=cited.value,
                script_value=got,
            )
        ]
    if cited.quantity == "composition":
        if not isinstance(got, dict) or not isinstance(cited.value, dict):
            return [
                Finding(
                    **base,
                    quantity="composition",
                    status="drift",
                    flowsheet=cited.value,
                    script_value=got,
                )
            ]
        findings = []
        for comp in sorted(set(cited.value) | set(got)):
            fs, sc = _number(cited.value.get(comp, 0.0)), _number(got.get(comp, 0.0))
            q = f"composition.{comp}"
            if fs is None or sc is None:
                findings.append(
                    Finding(
                        **base,
                        quantity=q,
                        status="drift",
                        flowsheet=cited.value.get(comp),
                        script_value=got.get(comp),
                    )
                )
                continue
            ok, dev, allowed = _compare(fs, sc, tol)
            findings.append(
                Finding(
                    **base,
                    quantity=q,
                    status="ok" if ok else "drift",
                    flowsheet=fs,
                    script_value=sc,
                    deviation=dev,
                    allowed=allowed,
                )
            )
        return findings
    fs, sc = _number(cited.value), _number(got)
    if fs is None or sc is None:
        return [
            Finding(
                **base,
                quantity=cited.quantity,
                status="drift",
                flowsheet=cited.value,
                script_value=got,
            )
        ]
    ok, dev, allowed = _compare(fs, sc, tol)
    return [
        Finding(
            **base,
            quantity=cited.quantity,
            status="ok" if ok else "drift",
            flowsheet=fs,
            script_value=sc,
            deviation=dev,
            allowed=allowed,
        )
    ]


def is_migrated(script: Path) -> bool:
    try:
        return ENV in script.read_text(encoding="utf-8")
    except OSError:
        return False


def run_script(cheme: list[str], folder: Path, script: str, output: Path | None) -> tuple[int, str]:
    env = dict(os.environ)
    env.pop(ENV, None)
    if output is not None:
        env[ENV] = str(output)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        proc = subprocess.run(
            [*cheme, "run", script],
            cwd=folder,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {TIMEOUT_S} s"
    except OSError as exc:
        return 127, f"could not start {cheme[0]}: {exc}"
    tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
    return proc.returncode, "\n".join(tail)


def read_output(path: Path, script: str) -> dict:
    """The ``cases`` of a balance-output file; raises ValueError when it breaks the contract."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"no readable {ENV} output: {exc}") from exc
    if doc.get("contract") != CONTRACT:
        raise ValueError(f"output contract {doc.get('contract')!r}, expected {CONTRACT!r}")
    if doc.get("script") not in (None, script):
        raise ValueError(f"output names script {doc.get('script')!r}, expected {script!r}")
    cases = doc.get("cases")
    if not isinstance(cases, dict) or not all(isinstance(c, dict) for c in cases.values()):
        raise ValueError("output has no 'cases' mapping of case -> stream -> quantity")
    return cases


def check_process(
    folder: Path, cheme: list[str], run_unmigrated: bool = False
) -> list[ScriptResult]:
    flowsheet_path = folder / "process" / "flowsheet.yaml"
    if not flowsheet_path.is_file():
        return []
    flowsheet = yaml.safe_load(flowsheet_path.read_text(encoding="utf-8")) or {}
    cited = cited_values(flowsheet)
    by_script: dict[str, list[Cited]] = {}
    for c in cited:
        by_script.setdefault(c.script, []).append(c)
    results = []
    for script, values in sorted(by_script.items()):
        res = ScriptResult(folder.name, script, "checked", cited=len(values))
        path = folder / script
        if not path.is_file():
            res.status, res.message = "missing-script", f"{script} does not exist"
        elif not is_migrated(path):
            res.status = "not-migrated"
            if run_unmigrated:
                code, tail = run_script(cheme, folder, script, None)
                res.message = f"ran, exit {code}" + (f": {tail}" if code else "")
                if code:
                    res.status = "error"
        else:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "balance.json"
                code, tail = run_script(cheme, folder, script, out)
                if code:
                    res.status, res.message = "error", f"exit {code}: {tail}"
                else:
                    try:
                        emitted = read_output(out, script)
                    except ValueError as exc:
                        res.status, res.message = "error", str(exc)
                    else:
                        for c in values:
                            res.findings.extend(compare(folder.name, c, emitted, flowsheet))
        results.append(res)
    return results


def _fmt(x: object) -> str:
    if isinstance(x, float):
        return f"{x:.6g}"
    return "" if x is None else str(x)


def markdown(results: list[ScriptResult]) -> str:
    lines = [
        "| process | script | status | cited | ok | drift | missing |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for r in results:
        n = {s: sum(f.status == s for f in r.findings) for s in ("ok", "drift", "missing")}
        lines.append(
            f"| {r.process} | `{r.script}` | {r.status} | {r.cited} | {n['ok']} | "
            f"{n['drift']} | {n['missing']} |"
        )
    bad = [f for r in results for f in r.findings if f.status != "ok"]
    if bad:
        header = (
            "| process | case | stream | quantity | status | flowsheet | script | "
            "deviation | allowed |"
        )
        lines += ["", header, "|---|---|---|---|---|---:|---:|---:|---:|"]
        for f in bad:
            lines.append(
                f"| {f.process} | {f.case} | {f.stream} | {f.quantity} | {f.status} | "
                f"{_fmt(f.flowsheet)} | {_fmt(f.script_value)} | {_fmt(f.deviation)} | "
                f"{_fmt(f.allowed)} |"
            )
    errors = [r for r in results if r.message and r.status in ("error", "missing-script")]
    if errors:
        lines += ["", "Errors:", ""] + [f"- {r.process} `{r.script}`: {r.message}" for r in errors]
    return "\n".join(lines) + "\n"


def _report(res: ScriptResult) -> None:
    n_bad = sum(f.status != "ok" for f in res.findings)
    extra = f", {n_bad} not ok" if res.findings else ""
    msg = f" ({res.message})" if res.message else ""
    print(
        f"{res.process:28s} {res.script:36s} {res.status:13s} {res.cited:4d} cited{extra}{msg}",
        flush=True,
    )
    for f in res.findings:
        if f.status != "ok":
            bound = f" (|d| {f.deviation:.4g} > {f.allowed:.4g})" if f.deviation is not None else ""
            print(
                f"    {f.case}/{f.stream}.{f.quantity}: {f.status} flowsheet "
                f"{_fmt(f.flowsheet)} script {_fmt(f.script_value)}{bound}",
                flush=True,
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, default=Path("."), help="library root")
    parser.add_argument(
        "--process",
        action="append",
        default=[],
        help="process id (repeatable; default every process)",
    )
    parser.add_argument(
        "--cheme",
        default="cheme",
        help="the cheme command (default: cheme on PATH; may hold arguments)",
    )
    parser.add_argument(
        "--run-unmigrated",
        action="store_true",
        help="also run scripts without the contract, for their exit code",
    )
    parser.add_argument("--strict", action="store_true", help="fail on not-migrated scripts too")
    parser.add_argument("--markdown", type=Path, help="write the summary and drift table here")
    parser.add_argument("--json", type=Path, help="write the full report here")
    parser.add_argument(
        "--jobs", type=int, default=1, help="processes checked in parallel (default 1)"
    )
    args = parser.parse_args(argv)

    cheme = [t.strip("\"'") for t in shlex.split(args.cheme, posix=os.name != "nt")] or ["cheme"]
    root = args.library / "processes"
    folders = (
        [root / p for p in args.process]
        if args.process
        else sorted(p for p in root.iterdir() if p.is_dir())
    )
    for folder in folders:
        if not folder.is_dir():
            parser.error(f"no process folder {folder}")
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        per_process = pool.map(
            lambda folder: check_process(folder, cheme, args.run_unmigrated), folders
        )
        results: list[ScriptResult] = []
        for batch in per_process:  # in folder order, as each one finishes
            for res in batch:
                results.append(res)
                _report(res)
    if args.markdown:
        args.markdown.write_text(markdown(results), encoding="utf-8")
    if args.json:
        args.json.write_text(
            json.dumps([asdict(r) | {"failed": r.failed} for r in results], indent=1, default=str),
            encoding="utf-8",
        )
    failed = [r for r in results if r.failed or (args.strict and r.status == "not-migrated")]
    counts = {
        s: sum(r.status == s for r in results)
        for s in ("checked", "not-migrated", "error", "missing-script")
    }
    print(
        f"\n{len(results)} scripts: "
        + ", ".join(f"{v} {k}" for k, v in counts.items())
        + f"; {len(failed)} failing"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
