"""The one coupling of the #330 skid scripts to cheme-as-code (core).

scripts/regen.py and scripts/skid_balance.py reach core only through this module, and only
through the `--json` output of its commands, run as ``[sys.executable, "-m", "chemeascode",
...]`` in the process folder (core ADR 0044 and its amendment; the design spec of #330,
section 0). The duty and comparison fields the scripts read are mapped here, from core's JSON
names to the names the scripts use (DUTY_FIELDS, DUTY_TOTALS, DUTY_SERIES, COMPARE_FIELDS), and
checked on every read: a field that core renames or drops stops the run with a CoreError that
names it, and the rename is one edit in these tables. The cell point is mapped the same way
(:func:`cell_point`); the stack report's values are read by their key through
:func:`stack_value` and :func:`equipment_number`, the layout model through the model_*
functions.

Commands used: ``cheme process cell --json``, ``cheme process stack [--write] --json``,
``cheme process duty IDS --json [--plot DIR]``, ``cheme process duty --compare``,
``cheme datasheets draft``, ``cheme datasheets fill --case C --tag T``, ``cheme process build``,
``cheme process streams``, ``cheme layout build``, ``cheme layout render``,
``cheme control report --json``, ``cheme validate --json``, ``cheme layout lifting [--write]
--json`` and ``cheme assess mto [--write] --json`` (scripts/_lifting.py), ``cheme run``, and for the LCA
(scripts/_lca.py, #331) ``cheme assess lca --write [--case C]``, ``--json``, ``--balance
--json``, ``cheme assess lca-scenarios --write`` and ``cheme assess lca-cases --json``. The generated layout
model ``layout/plant-model.yaml`` (schema ``cheme schema layout_model``) is read here too, for
the envelope check: core checks containment in a structure in plan only.
"""

from __future__ import annotations

import json
import math
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
    """The installed core's version and, where the installer recorded it (a git install does,
    a local one does not), the commit it was built from. Only the version goes into a
    calculation record: the commit depends on how core was installed (DESIGN.md D-023)."""
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
    """The rows of `cheme process duty --compare`, each with the fields of COMPARE_FIELDS."""
    rows = []
    for row in report.get("rows") or []:
        _require(row, ("id", *COMPARE_FIELDS.values()), "cheme process duty --compare row")
        rows.append({"id": row["id"], **{k: row.get(v) for k, v in COMPARE_FIELDS.items()}})
    return rows


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


def lifting_study(root: Path, write: bool = False) -> dict[str, Any]:
    """``cheme layout lifting --json`` (criteria, lifts, findings) of the committed model; with
    *write*, ``--write`` first (layout/lifting-study.csv and .md)."""
    if write:
        cheme(root, "layout", "lifting", "--write")
    report = cheme(root, "layout", "lifting", "--json").json()
    _require(report, ("criteria", "lifts", "model_sha256"), "cheme layout lifting --json")
    return report


def take_off(root: Path, write: bool = False) -> dict[str, Any]:
    """``cheme assess mto --json`` (rows, totals, findings) of the committed model; with
    *write*, ``--write`` first (estimate/mto.csv and .md)."""
    if write:
        cheme(root, "assess", "mto", "--write")
    report = cheme(root, "assess", "mto", "--json").json()
    _require(report, ("rows", "totals", "model_sha256"), "cheme assess mto --json")
    return report


def cable_schedule(root: Path, write: bool = False) -> dict[str, Any]:
    """``cheme layout cables --json`` (cables, cabling summary) of the committed model; with
    *write*, ``--write`` first (electrical/cable-schedule.csv and .md)."""
    if write:
        cheme(root, "layout", "cables", "--write")
    report = cheme(root, "layout", "cables", "--json").json()
    _require(report, ("cables", "cabling"), "cheme layout cables --json")
    return report


def model_trays_over(model: dict[str, Any], footprint: list[float]) -> list[dict[str, Any]]:
    """Cable trays with a run over a plan footprint: id, system, kind, the cables and the
    lowest and highest bottom of their runs over it (a branch's last run, the drop onto its
    load, left out of the lowest)."""
    x0, y0, x1, y1 = footprint
    found = []
    for tray in model.get("trays") or []:
        points = tray.get("points") or []
        runs = list(zip(points, points[1:]))
        level = [
            (a, b)
            for k, (a, b) in enumerate(runs)
            if abs(a[2] - b[2]) < 1e-6
            and not (tray.get("kind") == "branch" and k == len(runs) - 1)
            and min(a[0], b[0]) < x1 and max(a[0], b[0]) > x0
            and min(a[1], b[1]) < y1 and max(a[1], b[1]) > y0
        ]  # fmt: skip
        over = [p for p in points if x0 <= p[0] <= x1 and y0 <= p[1] <= y1]
        if not (over or level):
            continue
        zs = [float(p[2]) for p in over] + [float(a[2]) for a, _ in level]
        found.append(
            {
                "id": tray["id"],
                "system": tray.get("system"),
                "kind": tray.get("kind"),
                "cables": list(tray.get("cables") or []),
                "level_low_m": min((float(a[2]) for a, _ in level), default=None),
                "top_m": max(zs) + float(tray.get("depth") or 0.0),
            }
        )
    return found


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
    """The equipment mounted on a structure: tag, bbox [x0, y0, z0, x1, y1, z1], rotation,
    dimensions, size_from, the top of its generated detail parts (handrails, ladders, nozzles)
    and their plan extent [x0, y0, x1, y1] (the bbox covers the body only)."""
    items = []
    for item in model.get("equipment") or []:
        if (item.get("mount") or {}).get("structure") != structure_id:
            continue
        parts = item.get("parts") or []
        tops = [t for t in (_part_top(p) for p in parts) if t is not None]
        items.append(
            {
                "tag": item["tag"],
                "bbox": [float(v) for v in item["bbox"]],
                "rotation_deg": float(item.get("rotation_deg") or 0.0),
                "dimensions": dict(item.get("dimensions") or {}),
                "size_from": item.get("size_from"),
                "parts_top_m": max(tops) if tops else None,
                "parts_plan": _plan_union([_part_plan(p) for p in parts]),
            }
        )
    return items


def model_inline_of(model: dict[str, Any], sheet: str) -> list[dict[str, Any]]:
    """The inline items (valves, instruments in the line) of one P&ID sheet: tag, id and the
    plan extent [x0, y0, x1, y1] of their parts."""
    found = []
    for item in model.get("inline") or []:
        if (item.get("refs") or {}).get("sheet") != sheet:
            continue
        plan = _plan_union([_part_plan(p) for p in item.get("parts") or []])
        if plan is None and item.get("point"):
            x, y = float(item["point"][0]), float(item["point"][1])
            plan = [x, y, x, y]
        found.append({"tag": item.get("tag") or item["id"], "id": item["id"], "plan": plan})
    return found


def _part_plan(part: dict[str, Any]) -> list[float] | None:
    """A generated part's extent in plan: a box by its corners turned by its rotation, any
    other part by its points padded with its radius."""
    if part.get("kind") == "box" and "centre" in part and "size" in part:
        cx, cy = float(part["centre"][0]), float(part["centre"][1])
        hx, hy = float(part["size"][0]) / 2, float(part["size"][1]) / 2
        a = math.radians(float(part.get("rotation_deg") or 0.0))
        c, s = math.cos(a), math.sin(a)
        corners = [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx in (-hx, hx) for dy in (-hy, hy)]
        xs, ys = [p[0] for p in corners], [p[1] for p in corners]
        return [min(xs), min(ys), max(xs), max(ys)]
    points = [part[k] for k in ("start", "end", "centre", "point") if k in part]
    if not points:
        return None
    pad = max(float(part.get("radius", 0.0)), float(part.get("radius_end", 0.0)))
    xs, ys = [float(p[0]) for p in points], [float(p[1]) for p in points]
    return [min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad]


def _plan_union(boxes: list[list[float] | None]) -> list[float] | None:
    boxes = [b for b in boxes if b is not None]
    if not boxes:
        return None
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


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


#: the model collections whose parts are solids a hand lift can meet (DESIGN.md D-042); the
#: proposed step-overs are left out (not adopted, D-040), as are the deck gratings (the floor)
SOLID_COLLECTIONS = (
    "equipment",
    "inline",
    "structures",
    "racks",
    "trays",
    "junction_boxes",
    "platforms",
    "support_steel",
    "supports",
)


def model_solids(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Every solid of the model as ``{id, owner, plan: [x0, y0, x1, y1], z: [bottom, top]}``:
    the parts of the items, in-line items, steel, trays and supports, and each straight run of
    every pipe (padded by its outside radius and insulation). Deck gratings are floors, not
    obstacles, and are left out."""
    found = []
    for key in SOLID_COLLECTIONS:
        for owner in model.get(key) or []:
            name = owner.get("tag") or owner.get("id")
            for part in owner.get("parts") or []:
                if part.get("material") == "grating":
                    continue
                plan, z = _part_plan(part), _part_z(part)
                pid = part.get("id", name)
                # steel by its member group (SKID-A/DECK: the deck's beams and handrail)
                who = "/".join(pid.split("/")[:2]) if key in ("structures", "racks") else name
                if plan is not None and z is not None:
                    found.append({"id": pid, "owner": who, "plan": plan, "z": z})
    for pipe in model.get("pipes") or []:
        r = float(pipe.get("od") or 0.0) / 2 + float(pipe.get("insulation_mm") or 0.0) / 1000
        points = pipe.get("points") or []
        for k, (a, b) in enumerate(zip(points, points[1:])):
            found.append(
                {
                    "id": f"{pipe['id']}#{k}",
                    "owner": pipe["id"],
                    "plan": [min(a[0], b[0]) - r, min(a[1], b[1]) - r, max(a[0], b[0]) + r, max(a[1], b[1]) + r],
                    "z": [min(a[2], b[2]) - r, max(a[2], b[2]) + r],
                }
            )
    return found


def _part_z(part: dict[str, Any]) -> list[float] | None:
    """A generated part's bottom and top elevation."""
    kind = part.get("kind")
    if kind == "box" and "centre" in part and "size" in part:
        c, h = float(part["centre"][2]), float(part["size"][2]) / 2
        return [c - h, c + h]
    if kind == "annulus" and "centre" in part:
        c, h = float(part["centre"][2]), float(part.get("depth", 0.0)) / 2
        return [c - h, c + h]
    points = [part[k] for k in ("start", "end", "centre", "point") if k in part]
    if not points:
        return None
    pad = max(float(part.get("radius", 0.0)), float(part.get("radius_end", 0.0)))
    if kind == "member" and part.get("profile"):
        pad = max(float(v) for v in part["profile"]) / 2
    zs = [float(p[2]) for p in points]
    vertical = len(points) == 2 and abs(points[0][0] - points[1][0]) < 1e-9 and abs(points[0][1] - points[1][1]) < 1e-9
    return [min(zs), max(zs)] if vertical else [min(zs) - pad, max(zs) + pad]


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


#: the duty fields the scripts read: {the scripts' name: core's JSON field}
DUTY_FIELDS = {
    "id": "id", "refused": "refused", "reasons": "reasons", "ended": "ended",
    "feasible": "feasible", "horizon_h": "horizon_h", "simulated_h": "simulated_h",
    "operating_time_h": "operating_time_h", "time_to_threshold_h": "time_to_threshold_h",
    "first_exit_h": "first_exit_h",
    "time_outside_measured_range_h": "time_outside_measured_range_h",
    "cells_in_series": "cells_in_series", "stacks": "stacks",
}  # fmt: skip
#: the totals over the run (core ADR 0044 amendment: by route)
DUTY_TOTALS = {
    k: k
    for k in (
        "charge_c", "energy_kwh", "product_kg", "product_mol", "final_ph", "final_volume_l",
        "initial_volume_l", "initial_cation_mol", "initial_carbon_mol", "final_cation_mol",
        "final_carbon_mol", "membrane_cation_mol", "membrane_carbon_mol", "bleed_cation_mol",
        "bleed_carbon_mol", "dosing_cation_mol", "co2_degassed_mol", "dosing_mol",
        "dosing_solution_kg", "dosing_solution_l", "dosing_hydroxide_kg", "bleed_l",
        "makeup_water_l", "hydroxide_deficit_mol",
    )
}  # fmt: skip
#: the series sampled over the run
DUTY_SERIES = {k: k for k in ("t_h", "ph", "species_mol_l", "ionic_strength_mol_l")}
#: the rows of a comparison
COMPARE_FIELDS = {
    k: k
    for k in (
        "reached", "ended", "delivered_kg", "elapsed_h", "charge_c", "energy_kwh", "final_ph",
        "dosing_hydroxide_kg", "hydroxide_deficit_mol", "feasible", "reason",
    )
}  # fmt: skip


def _require(entry: dict[str, Any], fields, what: str) -> None:
    missing = [f for f in fields if f not in entry]
    if missing:
        raise CoreError(
            f"{what}: core's JSON has no {', '.join(missing)} (scripts/_core.py maps core's "
            "fields; update the mapping for this core version)"
        )


def duty(report: dict[str, Any], duty_id: str) -> dict[str, Any]:
    """One duty of `cheme process duty --json`, mapped onto the scripts' names: the fields of
    DUTY_FIELDS, ``totals`` (DUTY_TOTALS) and ``series`` (DUTY_SERIES), the anolyte model's
    equilibrium constants (``anolyte_constants``: Kw, pK1, pK2), the volume to the horizon
    (``required_volume_l``, ``required_volume_limited_by``; core's reservoir.size) and the
    entry as core wrote it (``raw``, for :func:`condensed_duty`). A refused duty has no totals
    or series."""
    entry = next((d for d in report.get("duties", []) if d.get("id") == duty_id), None)
    if entry is None:
        raise CoreError(f"cheme process duty: no duty {duty_id}")
    what = f"cheme process duty {duty_id}"
    _require(entry, ("id", "refused", "ended", "feasible"), what)
    view: dict[str, Any] = {k: entry.get(v) for k, v in DUTY_FIELDS.items()}
    if entry.get("refused"):
        view.update(totals={}, series={}, anolyte_constants={}, raw=entry)
        view.update(required_volume_l=None, required_volume_limited_by=None)
        return view
    _require(entry, DUTY_FIELDS.values(), what)
    _require(entry, ("totals", "series", "anolyte_model"), what)
    _require(entry["totals"], DUTY_TOTALS.values(), f"{what} totals")
    _require(entry["series"], DUTY_SERIES.values(), f"{what} series")
    constants = (entry["anolyte_model"] or {}).get("constants") or {}
    _require(constants, ("Kw", "pK1", "pK2"), f"{what} anolyte_model.constants")
    required = entry.get("required_volume") or {}
    view.update(
        totals={k: entry["totals"][v] for k, v in DUTY_TOTALS.items()},
        series={k: entry["series"][v] for k, v in DUTY_SERIES.items()},
        anolyte_constants={k: constants[k] for k in ("Kw", "pK1", "pK2")},
        required_volume_l=required.get("volume_l"),
        required_volume_limited_by=required.get("limited_by"),
        raw=entry,
    )
    return view


def duties(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Every duty of a report, mapped as :func:`duty`."""
    return [duty(report, d["id"]) for d in report.get("duties", [])]


def totals(entry: dict[str, Any]) -> dict[str, Any]:
    return entry.get("totals") or {}


def findings(report: dict[str, Any], level: str | None = None) -> list[dict[str, Any]]:
    return [f for f in report.get("findings", []) if level is None or f.get("level") == level]


def fingerprints(report: dict[str, Any]) -> dict[str, str]:
    return dict((report.get("source") or {}).get("fingerprints") or {})


def condensed_duty(view: dict[str, Any]) -> dict[str, Any]:
    """A duty's result without its series (for a calculation record), as core wrote it."""
    entry = view.get("raw", view)
    keep = (
        "id", "cell", "cells_in_series", "stacks", "schedule", "threshold_ph", "horizon_h",
        "ended", "simulated_h", "time_to_threshold_h", "operating_time_h",
        "time_outside_measured_range_h", "first_exit_h", "time_outside_model_range_h",
        "feasible", "totals", "required_volume", "events",
    )  # fmt: skip
    return {k: entry.get(k) for k in keep if k in entry}
