"""The one coupling of the #330 skid scripts to cheme-as-code (core).

scripts/regen.py and scripts/skid_balance.py reach core only through this module, and only
through the `--json` output of its commands, run as ``[sys.executable, "-m", "chemeascode",
...]`` in the process folder (core ADR 0044 and its amendment; the design spec of #330,
section 0). Field names of core's JSON are read here and nowhere else, so a change of core's
interface is one edit in one file.

Commands used: ``cheme process cell --json``, ``cheme process stack [--write] --json``,
``cheme process duty IDS --json``, ``cheme datasheets draft``, ``cheme process build``,
``cheme process streams``, ``cheme run``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

#: C/mol, CODATA 2018 (exact), as core uses it
FARADAY = 96485.33212


class CoreError(RuntimeError):
    """A core command failed as a tool (not a design finding): regen exits non-zero."""


@dataclass
class Result:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str

    def json(self) -> dict[str, Any]:
        try:
            return json.loads(self.stdout)
        except json.JSONDecodeError as exc:
            raise CoreError(
                f"cheme {' '.join(self.args)}: no JSON output (exit {self.returncode}): "
                f"{self.stderr.strip()[-400:]}"
            ) from exc


def cheme(root: Path, *args: str, env: dict[str, str] | None = None, ok=(0,)) -> Result:
    """Run ``cheme ARGS`` in *root* with this interpreter; refuse an exit code not in *ok*."""
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    proc = subprocess.run(
        [sys.executable, "-m", "chemeascode", *args],
        cwd=root,
        capture_output=True,
        text=True,
        env=full_env,
        check=False,
    )
    result = Result(list(args), proc.returncode, proc.stdout, proc.stderr)
    if proc.returncode not in ok:
        raise CoreError(
            f"cheme {' '.join(args)} exited {proc.returncode}: "
            f"{(proc.stderr or proc.stdout).strip()[-1500:]}"
        )
    return result


def core_info() -> dict[str, Any]:
    """The installed core's version and, where pip recorded it, the commit it was built from."""
    dist = metadata.distribution("cheme-as-code")
    info: dict[str, Any] = {"version": dist.version, "commit": None}
    try:
        direct = json.loads(dist.read_text("direct_url.json") or "{}")
    except json.JSONDecodeError:
        direct = {}
    commit = (direct.get("vcs_info") or {}).get("commit_id")
    if commit:
        info["commit"] = commit
    return info


# -- the reports --------------------------------------------------------------------------------


def cell_report(root: Path) -> dict[str, Any]:
    # exit 1 is a refused cell: a finding, read from the JSON
    return cheme(root, "process", "cell", "--json", ok=(0, 1)).json()


def stack_report(root: Path, write: bool = False) -> dict[str, Any]:
    args = ["process", "stack", "--json"] + (["--write"] if write else [])
    return cheme(root, *args, ok=(0, 1)).json()


def duty_report(root: Path, ids: list[str]) -> dict[str, Any]:
    return cheme(root, "process", "duty", *ids, "--json", ok=(0, 1)).json()


def compare_report(root: Path, ids: list[str], co_kg: float, tolerance: float) -> dict[str, Any]:
    return cheme(
        root,
        "process",
        "duty",
        "--compare",
        ",".join(ids),
        "--co",
        repr(co_kg),
        "--tolerance",
        repr(tolerance),
        "--json",
        ok=(0, 1),
    ).json()


# -- reading them -------------------------------------------------------------------------------


def cell(report: dict[str, Any], cell_id: str) -> dict[str, Any]:
    entry = next((c for c in report.get("cells", []) if c.get("id") == cell_id), None)
    if entry is None:
        raise CoreError(f"cheme process cell: no cell {cell_id}")
    return entry


def cell_point(report: dict[str, Any], cell_id: str) -> dict[str, Any]:
    """The operating point of one cell: U, FE of CO and H2, WDE, co-ion split, heat."""
    c = cell(report, cell_id)
    membrane = c.get("membrane") or {}
    flux = membrane.get("co_ion_flux_mol_s") or {}
    total = sum(flux.values())
    return {
        "refused": bool(c.get("refused")),
        "reasons": c.get("reasons", []),
        "current_a": c["current_a"],
        "current_density_a_m2": c["current_density_a_m2"],
        "voltage_v": c["voltage_v"],
        "fe": dict((c.get("measurement") or {}).get("faradaic_efficiency") or {}),
        "fe_sd": dict((c.get("measurement") or {}).get("faradaic_efficiency_sd") or {}),
        "voltage_sd_v": (c.get("measurement") or {}).get("voltage_sd_v"),
        "wde": membrane.get("water_dissociation_efficiency"),
        "wde_sd": membrane.get("water_dissociation_efficiency_sd"),
        "carbon_share": (flux.get("HCO3-", 0.0) / total) if total else None,
        "formed_kmol_h": dict(c.get("formed_kmol_h") or {}),
        "heat_kw": c.get("heat_duty_kw"),
        "validity": (c.get("measurement") or {}).get("validity") or {},
    }


def stack(report: dict[str, Any], stack_id: str) -> dict[str, Any]:
    entry = next((s for s in report.get("stacks", []) if s.get("id") == stack_id), None)
    if entry is None:
        raise CoreError(f"cheme process stack: no stack {stack_id}")
    return entry


def stack_value(entry: dict[str, Any], key: str) -> Any:
    value = (entry.get("values") or {}).get(key)
    return None if value is None else value.get("value")


def stack_equipment(entry: dict[str, Any], tag: str) -> dict[str, Any] | None:
    return next((e for e in entry.get("equipment", []) if e.get("tag") == tag), None)


def equipment_number(entry: dict[str, Any], tag: str, key: str) -> Any:
    item = stack_equipment(entry, tag)
    if item is None:
        return None
    value = (item.get("values") or {}).get(key)
    return None if value is None else value.get("value")


def stack_duty(entry: dict[str, Any]) -> dict[str, Any]:
    return entry.get("duty") or {}


def duty(report: dict[str, Any], duty_id: str) -> dict[str, Any]:
    entry = next((d for d in report.get("duties", []) if d.get("id") == duty_id), None)
    if entry is None:
        raise CoreError(f"cheme process duty: no duty {duty_id}")
    return entry


def totals(entry: dict[str, Any]) -> dict[str, Any]:
    return entry.get("totals") or {}


def findings(report: dict[str, Any], level: str | None = None) -> list[dict[str, Any]]:
    return [f for f in report.get("findings", []) if level is None or f.get("level") == level]


def fingerprints(report: dict[str, Any]) -> dict[str, str]:
    return dict((report.get("source") or {}).get("fingerprints") or {})


def condensed_duty(entry: dict[str, Any]) -> dict[str, Any]:
    """A duty's result without its series (for a calculation record)."""
    keep = (
        "id", "cell", "cells_in_series", "stacks", "schedule", "threshold_ph", "horizon_h",
        "ended", "simulated_h", "time_to_threshold_h", "operating_time_h",
        "time_outside_measured_range_h", "first_exit_h", "time_outside_model_range_h",
        "feasible", "totals", "required_volume", "events",
    )  # fmt: skip
    return {k: entry.get(k) for k in keep if k in entry}
