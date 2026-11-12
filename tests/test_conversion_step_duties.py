"""A heat stream that core's conversion-step model writes is not also given by a balance script.

Since core 1.9.0 (its ADR 0059) `cheme process propagate --fill` writes the duty of a conversion
step's heat stream (provenance calculated, source "cheme process propagate: conversion duty
..."). Where a process moved such a duty from its balance script to core (#396), the script
keeps its own value only as a printed cross-check: its balance output (library ADR 0027) gives
the values the flowsheet cites from it, and a duty cheme writes is not one of them. A script
that still gave it would make two sources of one number (review of PR 436: ethylene-1 Q102).

Each such process's migrated scripts are run with BALANCE_OUTPUT set; a script whose imports
(thermo, CoolProp) are missing in this environment is skipped here and still runs in the
balance-scripts job (scripts/check_balance_scripts.py).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
CONVERSION_DUTY = "cheme process propagate: conversion duty"
MISSING_MODULE = re.compile(r"ModuleNotFoundError: No module named '([\w.]+)'")


def _written_duties(flowsheet: dict) -> set[tuple[str, str]]:
    """(case, stream) of every duty that core's conversion-step model writes."""
    out = set()
    for stream in flowsheet.get("streams") or []:
        for case, state in (stream.get("state") or {}).items():
            duty = (state or {}).get("duty")
            if (isinstance(duty, dict) and duty.get("provenance") == "calculated"
                    and str(duty.get("source", "")).startswith(CONVERSION_DUTY)):
                out.add((str(case), str(stream["id"])))
    return out


def _cases() -> list[tuple[str, str, frozenset]]:
    cases = []
    for path in sorted((KIT / "processes").glob("*/process/flowsheet.yaml")):
        written = _written_duties(yaml.safe_load(path.read_text(encoding="utf-8")))
        if not written:
            continue
        folder = path.parents[1]
        for script in sorted((folder / "scripts").glob("*.py")):
            if "BALANCE_OUTPUT" in script.read_text(encoding="utf-8"):
                cases.append((folder.name, f"scripts/{script.name}", frozenset(written)))
    return cases


CASES = _cases()


def test_the_entries_of_396_are_covered():
    covered = {process for process, _, _ in CASES}
    assert {"ethylene-1", "formic-acid-1", "hydrogen-bromide-1", "hydrogen-chloride-1",
            "phosphorus-oxychloride-1"} <= covered


@pytest.mark.parametrize("process,script,written", CASES, ids=[f"{p}:{s}" for p, s, _ in CASES])
def test_the_script_does_not_give_a_duty_cheme_writes(process, script, written, tmp_path):
    out = tmp_path / "balance-output.json"
    env = {**os.environ, "BALANCE_OUTPUT": str(out), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, script], cwd=KIT / "processes" / process, env=env,
        capture_output=True, text=True, check=False, timeout=600,
    )
    missing = MISSING_MODULE.search(proc.stderr or "")
    if proc.returncode and missing:
        pytest.skip(f"{script} needs {missing.group(1)} (runs in the balance-scripts job)")
    assert proc.returncode == 0, proc.stderr[-2000:]
    cases = json.loads(out.read_text(encoding="utf-8"))["cases"]
    given = {(case, sid) for case, streams in cases.items() for sid, q in streams.items() if "duty" in q}
    assert not (given & written), (
        f"{process}/{script} gives {sorted(given & written)}, which core's conversion-step model "
        "writes: keep the script's value as a printed cross-check, out of its balance output"
    )
