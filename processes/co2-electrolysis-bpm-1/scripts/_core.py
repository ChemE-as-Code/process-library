"""The one coupling of the #330 skid scripts to cheme-as-code (core).

scripts/regen.py and scripts/skid_balance.py reach core only through this module, and only
through the `--json` output of its commands, run as ``[sys.executable, "-m", "chemeascode",
...]`` in the process folder (core ADR 0044 and its amendment; the design spec of #330,
section 0). Field names of core's JSON are read here and nowhere else, so a change of core's
interface is one edit in one file.

Commands used: ``cheme process cell --json``, ``cheme process stack [--write] --json``,
``cheme process duty IDS --json [--plot DIR]``, ``cheme process duty --compare``,
``cheme datasheets draft``, ``cheme datasheets fill --case C --tag T``, ``cheme process build``,
``cheme process streams``, ``cheme layout build``, ``cheme layout render``,
``cheme control report --json``, ``cheme validate --json``, ``cheme run``. The generated layout
model ``layout/plant-model.yaml`` (schema ``cheme schema layout_model``) is read here too, for
the envelope check: core checks containment in a structure in plan only.
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


def duty_plots(root: Path, ids: list[str], out: Path) -> dict[str, Any]:
    """``cheme process duty IDS --json --plot OUT``: the time plots and operating maps."""
    return cheme(root, "process", "duty", *ids, "--json", "--plot", str(out), ok=(0, 1)).json()


def compare_report(
    root: Path, ids: list[str], co_kg: float, tolerance: float, plot: Path | None = None
) -> dict[str, Any]:
    args = [
        "process",
        "duty",
        "--compare",
        ",".join(ids),
        "--co",
        repr(co_kg),
        "--tolerance",
        repr(tolerance),
        "--json",
    ]
    if plot is not None:
        args += ["--plot", str(plot)]
    return cheme(root, *args, ok=(0, 1)).json()


def compare_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    return list(report.get("rows") or [])


def layout_build(root: Path) -> str:
    """``cheme layout build``: writes layout/plant-model.yaml, prints the model findings (exit 1
    on an error finding, such as a clash: the model is still written, the clash is a result)."""
    result = cheme(root, "layout", "build", ok=(0, 1))
    if not (root / "layout" / "plant-model.yaml").exists():
        raise CoreError(f"cheme layout build wrote no model: {result.stderr.strip()[-400:]}")
    return result.stdout


def render(root: Path, *args: str) -> list[Path]:
    """``cheme layout render ARGS``: the files it wrote (under build/), from its output."""
    out = cheme(root, "layout", "render", *args).stdout
    paths = [
        root / line.split("wrote ", 1)[1].strip()
        for line in out.splitlines()
        if line.startswith("wrote ")
    ]
    if not paths:
        raise CoreError(f"cheme layout render {' '.join(args)}: wrote nothing: {out.strip()[-400:]}")
    return paths


def datasheets_fill(root: Path, case: str, tags: list[str]) -> Result:
    args = ["datasheets", "fill", "--case", case]
    for tag in tags:
        args += ["--tag", tag]
    return cheme(root, *args, ok=(0, 1))


def control_report(root: Path, out: Path) -> dict[str, Any]:
    return cheme(root, "control", "report", "--json", "-o", str(out), ok=(0, 1)).json()


def validate(root: Path) -> dict[str, Any]:
    return cheme(root, "validate", "--json", ok=(0, 1)).json()


def validate_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Findings with level, rule, file, line, message, id and whether they are accepted."""
    return list(report.get("findings") or [])


# -- the layout model (layout/plant-model.yaml) -------------------------------------------------


def plant_model(root: Path) -> dict[str, Any]:
    import yaml

    path = root / "layout" / "plant-model.yaml"
    if not path.exists():
        raise CoreError("no layout/plant-model.yaml: cheme layout build wrote no model")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def model_structure(model: dict[str, Any], structure_id: str) -> dict[str, Any]:
    """A structure's footprint [x0, y0, x1, y1], rotation and level elevations."""
    entry = next((s for s in model.get("structures") or [] if s.get("id") == structure_id), None)
    if entry is None:
        raise CoreError(f"layout/plant-model.yaml: no structure {structure_id}")
    return {
        "id": entry["id"],
        "footprint": [float(v) for v in entry["footprint"]],
        "rotation_deg": float(entry.get("rotation_deg") or 0.0),
        "width": float(entry["width"]),
        "depth": float(entry["depth"]),
        "levels": {lv["id"]: float(lv["elevation"]) for lv in entry.get("levels") or []},
    }


def model_items_on(model: dict[str, Any], structure_id: str) -> list[dict[str, Any]]:
    """The equipment mounted on a structure: tag, bbox [x0, y0, z0, x1, y1, z1], dimensions,
    size_from, and the top of its generated detail parts (handrails, ladders, nozzles)."""
    items = []
    for item in model.get("equipment") or []:
        if (item.get("mount") or {}).get("structure") != structure_id:
            continue
        tops = [t for t in (_part_top(p) for p in item.get("parts") or []) if t is not None]
        items.append(
            {
                "tag": item["tag"],
                "bbox": [float(v) for v in item["bbox"]],
                "dimensions": dict(item.get("dimensions") or {}),
                "size_from": item.get("size_from"),
                "parts_top_m": max(tops) if tops else None,
            }
        )
    return items


def model_pipes_over(model: dict[str, Any], footprint: list[float]) -> list[dict[str, Any]]:
    """Pipes with a point over a plan footprint: id, line and their highest point."""
    x0, y0, x1, y1 = footprint
    found = []
    for pipe in model.get("pipes") or []:
        points = pipe.get("points") or []
        over = [p for p in points if x0 <= p[0] <= x1 and y0 <= p[1] <= y1]
        if over:
            found.append(
                {
                    "id": pipe["id"],
                    "line": pipe.get("line"),
                    "top_m": max(float(p[2]) for p in over),
                }
            )
    return found


def _part_top(part: dict[str, Any]) -> float | None:
    kind = part.get("kind")
    if kind == "cylinder" and "start" in part and "end" in part:
        vertical = abs(part["start"][0] - part["end"][0]) < 1e-9 and abs(
            part["start"][1] - part["end"][1]
        ) < 1e-9
        top = max(part["start"][2], part["end"][2])
        return float(top if vertical else top + part.get("radius", 0.0))
    if kind == "box" and "centre" in part and "size" in part:
        return float(part["centre"][2] + part["size"][2] / 2)
    if kind == "annulus" and "centre" in part:
        return float(part["centre"][2] + part.get("depth", 0.0) / 2)
    return None


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
