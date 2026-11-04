"""Regenerate the two CO2 pilot skids (#330) for one campaign duration: the single rerun command.

    cheme run scripts/regen.py --duration H [--scratch DIR] [--check] [--uncertainty] [--record]

The design basis (process/design-basis.yaml capacity.pilot_skid), the cells and stacks
(process/cells.yaml), the duties (process/duties.yaml) and the flowsheet structure
(process/flowsheet.yaml) are written by hand; this script carries one design basis through
core's commands into every value that depends on the campaign duration H (DESIGN.md D-007 to
D-015). Core is reached only through scripts/_core.py; hand-maintained files are changed only
by targeted edits that refuse any other change (scripts/_yamledit.py, or core's own writers).
It reads only this process folder, never the library's held-out reproductions (ADR 0032).

Steps (design spec #330, section 6):

1. Preflight: core version and commit, sha256 of the inputs; H in the design basis
   scenarios, else the run is labelled ad hoc.
2. Sync stacks[].product (rate, recovery, purity, pressure) from the design basis.
3. Write the horizons: D-A and D-B to H, the comparison duties to 3 H, and D-A-PART's step
   points (12 h at 200, 12 h at 100 mA/cm2) over 3 H.
4. Check the cell: `cheme process cell --json`; a refused cell stops the run.
5. Size Skid A: `cheme process stack --write` writes D-A's reservoir volume (core's
   `reservoir.size: to_horizon`, exact: V = V0 Q(H) / Q*, rounded up to 4 significant
   figures) and the tanks from the duty at it; D-A then runs at that volume, asserted to reach
   its horizon (feasible) with no dosing, bleed, make-up or degassing.
6. Set Skid B: the bleed b = Cx (1 - WDE) N I / (F C_T) at the setpoint carbon C_T, the dose
   [b [K+] + (1 - Cx)(1 - WDE) N I / F] / 5 M with [K+] from the setpoints' charge balance,
   and the make-up b - dose, corrected once from the probe run's volume drift; asserted:
   |V_end - V0| / V0 <= 1 % and the species at H at the setpoints within 1e-3 mol/L.
7. Copy D-A's volume into the comparison duties (they run at STK-A's arrangement through
   `stack: STK-A`; asserted equal to the stack's).
8. `cheme datasheets draft` (new tags only), then `cheme process stack --write` again: the
   tanks and the pumps' type_specific from the duties as they now are. The tool owns those
   values; never hand-edit them.
9. `cheme run scripts/skid_balance.py` (contract balance-output/1), its values applied to
   process/flowsheet.yaml (targeted edit), then `cheme process build` (BFD, PFD) and
   `cheme process streams` for both cases.

Steps 10 to 19 (layout, datasheet fill, control report, duty plots and comparisons, the
envelope and invariant checks, --uncertainty, the calculation record, the resize report,
--record and the full --check of records and figures) follow in the next stage of #330.

Findings are collected, never fatal: an infeasible skid is a result. The exit code is non-zero
only on a tool error (1), on refused input (2) or on a --check difference (3).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

import _core
import _yamledit as ye

SCRIPT = "scripts/regen.py"
INPUTS = (
    "process/design-basis.yaml",
    "process/cells.yaml",
    "process/duties.yaml",
    "process/flowsheet.yaml",
    "process/materials.yaml",
    "process/reactions.yaml",
    "equipment/equipment-list.yaml",
    "experiments/electrochemistry/rbpm-1m-koh.yaml",
)
#: what --check compares (the model files this stage writes)
MODEL_FILES = (
    "process/cells.yaml",
    "process/duties.yaml",
    "process/flowsheet.yaml",
    "process/BFD.xml",
    "process/PFD.xml",
    "equipment/equipment-list.yaml",
)
COPY_IGNORE = shutil.ignore_patterns(
    "build", ".venv", "__pycache__", ".DS_Store", ".claude", "runs"
)
STACKS = {"A": "STK-A", "B": "STK-B"}
SKID_DUTIES = {"A": "D-A", "B": "D-B"}
COMPARISON = ("D-A-ONOFF", "D-A-PART")
PART_LOAD = ((12.0, 200.0), (12.0, 100.0))  # (h, mA/cm2): both measured points
#: Skid B's ASSUMED steady state (DESIGN.md D-010): ionic strength about 1.25 mol/L, inside the
#: anolyte model's 1.5
SKID_B_SETPOINTS = {"hydroxide_mol_l": 0.5, "carbon_mol_l": 0.25}


class Refused(RuntimeError):
    """Input the run refuses (exit 2)."""


class Run:
    def __init__(self, root: Path, duration: float) -> None:
        self.root = root
        self.h = float(duration)
        self.findings: list[dict] = []
        self.summary: dict = {"duration_h": self.h}

    # -- helpers --------------------------------------------------------------------------
    def note(self, step: str, level: str, message: str) -> None:
        self.findings.append({"step": step, "level": level, "message": message})
        print(f"[{step}] {level}: {message}")

    def load(self, rel: str) -> dict:
        return yaml.safe_load((self.root / rel).read_text(encoding="utf-8"))

    def edit(self, rel: str, changes) -> bool:
        if not changes:
            return False
        return ye.edit_file(self.root / rel, changes)

    # -- 1 ----------------------------------------------------------------------------------
    def preflight(self) -> None:
        core = _core.core_info()
        shas = {}
        for rel in INPUTS:
            path = self.root / rel
            shas[rel] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        basis = self.load("process/design-basis.yaml")["capacity"]["pilot_skid"]
        scenarios = [float(x) for x in basis["duration"]["scenarios"]]
        ad_hoc = self.h not in scenarios
        if ad_hoc:
            self.note(
                "1",
                "warning",
                f"duration {self.h:g} h is not a design scenario {scenarios}: the run is ad hoc",
            )
        self.summary.update(core=core, inputs_sha256=shas, ad_hoc=ad_hoc, scenarios_h=scenarios)
        print(
            f"[1] core {core['version']} ({core['commit'] or 'commit not recorded'}), H = {self.h:g} h"
        )

    # -- 2 ----------------------------------------------------------------------------------
    def sync_product(self) -> None:
        product = self.load("process/design-basis.yaml")["capacity"]["pilot_skid"]["product"]
        cells = self.load("process/cells.yaml")
        changes = []
        for sid in STACKS.values():
            stack = next(s for s in cells["stacks"] if s["id"] == sid)
            if stack["product"]["component"] != product["component"]:
                raise Refused(
                    f"{sid}: product {stack['product']['component']} is not the design basis {product['component']}"
                )
            for key in ("rate", "recovery", "purity", "pressure"):
                want = product[key]["value"]
                have = stack["product"][key]["value"]
                if have != want:
                    changes.append((["stacks", ("id", sid), "product", key, "value"], want))
                unit_want, unit_have = product[key].get("unit"), stack["product"][key].get("unit")
                if key in ("rate", "pressure") and unit_have != unit_want:
                    changes.append((["stacks", ("id", sid), "product", key, "unit"], unit_want))
        changed = self.edit("process/cells.yaml", changes)
        print(
            f"[2] stacks[].product {'synced (' + str(len(changes)) + ' values)' if changed else 'current'}"
        )

    # -- 3 ----------------------------------------------------------------------------------
    def horizons(self) -> None:
        duties = self.load("process/duties.yaml")
        changes = []
        for did, h in [(d, self.h) for d in SKID_DUTIES.values()] + [
            (d, 3 * self.h) for d in COMPARISON
        ]:
            duty = next(x for x in duties["duties"] if x["id"] == did)
            want = {"value": h, "unit": "h"}
            if duty["horizon"] != want:
                changes.append((["duties", ("id", did), "horizon"], want))
        points = []
        t = 0.0
        while t < 3 * self.h:
            for dt, j in PART_LOAD:
                if t < 3 * self.h:
                    points.append([t, j])
                t += dt
        part = next(x for x in duties["duties"] if x["id"] == "D-A-PART")
        if [list(map(float, p)) for p in part["schedule"]["points"]] != points:
            changes.append(
                (
                    ["duties", ("id", "D-A-PART"), "schedule", "points"],
                    [[_num(a), _num(b)] for a, b in points],
                )
            )
        self.edit("process/duties.yaml", changes)
        print(
            f"[3] horizons: D-A, D-B {self.h:g} h; comparison duties {3 * self.h:g} h ({len(points)} part-load points)"
        )

    # -- 4 ----------------------------------------------------------------------------------
    def check_cell(self) -> dict:
        report = _core.cell_report(self.root)
        point = _core.cell_point(report, "pilot-cell")
        if point["refused"]:
            raise Refused(f"pilot-cell refused by cheme process cell: {point['reasons']}")
        self.summary["cell"] = point
        print(
            f"[4] pilot-cell: U {point['voltage_v']:.5g} V, FE CO {point['fe']['CO']:.5g}, "
            f"FE H2 {point['fe']['H2']:.5g}, WDE {point['wde']:.6g}"
        )
        return point

    # -- 5 ----------------------------------------------------------------------------------
    def size_skid_a(self) -> None:
        duty = next(d for d in self.load("process/duties.yaml")["duties"] if d["id"] == "D-A")
        if (
            (duty.get("dosing") or {}).get("kind", "none") != "none"
            or duty.get("bleed")
            or duty.get("makeup_water")
            or duty["reservoir"].get("degassing")
        ):
            raise Refused(
                "D-A has dosing, bleed, make-up or degassing: its volume is not proportional to H"
            )
        if duty["reservoir"].get("size") != "to_horizon":
            raise Refused("D-A states no reservoir.size: to_horizon")
        report = _core.stack_report(self.root, write=True)
        entry = _core.stack(report, STACKS["A"])
        required = _core.stack_value(entry, "reservoir_required_volume_l")
        run = _core.duty_report(self.root, ["D-A"])
        da = _core.duty(run, "D-A")
        volume = next(d for d in self.load("process/duties.yaml")["duties"] if d["id"] == "D-A")[
            "reservoir"
        ]["volume"]
        ok = da["ended"] == "horizon" and da["feasible"] and math.isclose(da["horizon_h"], self.h)
        if not ok:
            self.note(
                "5",
                "error",
                f"D-A at {volume['value']:g} L ended by {da['ended']} at {da['simulated_h']:g} h, feasible {da['feasible']}",
            )
        print(
            f"[5] Skid A reservoir: {required:.6g} L exact, {volume['value']:g} L written; D-A ended by {da['ended']}, feasible {da['feasible']}"
        )
        self.summary["skid_a"] = {
            "volume_exact_l": required,
            "volume_written_l": volume["value"],
            "limited_by": (da.get("required_volume") or {}).get("limited_by"),
            "ended": da["ended"],
            "feasible": da["feasible"],
        }

    # -- 6 ----------------------------------------------------------------------------------
    def set_skid_b(self, point: dict) -> None:
        duties = self.load("process/duties.yaml")
        db = next(d for d in duties["duties"] if d["id"] == "D-B")
        v0 = _litres(db["reservoir"]["volume"])
        c_dose = float(db["dosing"]["concentration"]["value"])
        oh_set, ct_set = SKID_B_SETPOINTS["hydroxide_mol_l"], SKID_B_SETPOINTS["carbon_mol_l"]
        probe = _core.duty(_core.duty_report(self.root, ["D-B"]), "D-B")
        tot = _core.totals(probe)
        n_cells = int(probe["cells_in_series"]) * int(probe["stacks"])
        consts = probe["anolyte_model"]["constants"]
        e_mol_h = tot["charge_c"] / float(probe["horizon_h"]) / _core.FARADAY
        co_ion = tot["membrane_cation_mol"] + tot["membrane_carbon_mol"]
        cx = tot["membrane_carbon_mol"] / co_ion  # the duty's carbon share (the titration's)
        wde = point["wde"]
        h_conc = consts["Kw"] / oh_set
        k1, k2 = 10.0 ** -consts["pK1"], 10.0 ** -consts["pK2"]
        g = (k1 * h_conc + 2 * k1 * k2) / (h_conc**2 + k1 * h_conc + k1 * k2)
        k_set = oh_set + ct_set * g - h_conc
        bleed = cx * (1 - wde) * e_mol_h / ct_set
        dose_mol = bleed * k_set + (1 - cx) * (1 - wde) * e_mol_h
        dose_l = dose_mol / c_dose
        makeup = bleed - dose_l

        def write(makeup_l_h: float) -> None:
            changes = [
                (
                    ["duties", ("id", "D-B"), "dosing", "rate"],
                    {"value": _round(dose_l), "unit": "L/h"},
                ),
                (
                    ["duties", ("id", "D-B"), "bleed", "rate"],
                    {"value": _round(bleed), "unit": "L/h"},
                ),
                (
                    ["duties", ("id", "D-B"), "makeup_water", "rate"],
                    {"value": _round(makeup_l_h), "unit": "L/h"},
                ),
            ]
            current = self.load("process/duties.yaml")
            changes = [c for c in changes if not _same(ye.get(current, c[0]), c[1])]
            self.edit("process/duties.yaml", changes)

        write(makeup)
        run = _core.duty(_core.duty_report(self.root, ["D-B"]), "D-B")
        drift = (v0 - _core.totals(run)["final_volume_l"]) / self.h
        makeup += drift
        write(makeup)
        run = _core.duty(_core.duty_report(self.root, ["D-B"]), "D-B")
        t2 = _core.totals(run)
        v_end = t2["final_volume_l"]
        species = {k: v[-1] for k, v in run["series"]["species_mol_l"].items()}
        carbon = species.get("CO3-2", 0.0) + species.get("HCO3-", 0.0) + species.get("CO2", 0.0)
        if abs(v_end - v0) / v0 > 0.01:
            self.note("6", "error", f"D-B volume drifts from {v0:g} to {v_end:g} L")
        for name, have, want in (
            ("OH-", species.get("OH-"), oh_set),
            ("carbon", carbon, ct_set),
            ("K+", species.get("K+"), k_set),
        ):
            if abs(have - want) > 1e-3:
                self.note("6", "warning", f"D-B {name} at H {have:.6g} mol/L, setpoint {want:.6g}")
        if not (run["ended"] == "horizon" and run["feasible"]):
            self.note("6", "error", f"D-B ended by {run['ended']}, feasible {run['feasible']}")
        print(
            f"[6] Skid B: bleed {bleed:.7g} L/h, dose {dose_mol:.7g} mol/h = {dose_l:.7g} L/h of {c_dose:g} M, "
            f"make-up {makeup:.7g} L/h (drift correction {drift:+.3g} L/h); V_end {v_end:.6g} L, "
            f"pH {t2['final_ph']:.5g}, OH- {species.get('OH-'):.5g}, C {carbon:.5g}, K+ {species.get('K+'):.5g} mol/L"
        )
        self.summary["skid_b"] = {
            "carbon_share_duty": cx,
            "bleed_l_h": bleed,
            "dose_mol_h": dose_mol,
            "dose_l_h": dose_l,
            "makeup_l_h": makeup,
            "residence_h": v0 / bleed,
            "cation_setpoint_mol_l": k_set,
            "final_species_mol_l": species,
            "final_volume_l": v_end,
            "cells": n_cells,
        }

    # -- 7 ----------------------------------------------------------------------------------
    def copy_comparison(self) -> None:
        duties = self.load("process/duties.yaml")
        da = next(d for d in duties["duties"] if d["id"] == "D-A")
        want = {
            "value": da["reservoir"]["volume"]["value"],
            "unit": da["reservoir"]["volume"]["unit"],
        }
        changes = []
        for did in COMPARISON:
            duty = next(d for d in duties["duties"] if d["id"] == did)
            if duty.get("stack") != STACKS["A"]:
                raise Refused(f"{did} does not name {STACKS['A']}")
            if {k: duty["reservoir"]["volume"].get(k) for k in ("value", "unit")} != want:
                changes.append((["duties", ("id", did), "reservoir", "volume"], want))
        self.edit("process/duties.yaml", changes)
        stack = _core.stack(_core.stack_report(self.root), STACKS["A"])
        arrangement = (
            _core.stack_value(stack, "cells_per_stack"),
            _core.stack_value(stack, "stacks"),
        )
        run = _core.duty_report(self.root, list(COMPARISON))
        for did in COMPARISON:
            d = _core.duty(run, did)
            if (d["cells_in_series"], d["stacks"]) != arrangement:
                self.note(
                    "7",
                    "error",
                    f"{did} runs {d['cells_in_series']} x {d['stacks']}, STK-A is {arrangement}",
                )
        print(
            f"[7] comparison duties: reservoir {want['value']:g} {want['unit']}, arrangement {arrangement[0]} x {arrangement[1]} (stack: STK-A)"
        )

    # -- 8 ----------------------------------------------------------------------------------
    def datasheets_and_stacks(self) -> None:
        drafted = _core.cheme(self.root, "datasheets", "draft").stdout.strip()
        report = _core.stack_report(self.root, write=True)
        for f in _core.findings(report):
            if f["level"] in ("error", "warning"):
                self.note("8", f["level"], f"{f['rule']}: {f['message']}")
        written = report.get("written") or []
        stacks = {sid: _core.stack(report, sid) for sid in STACKS.values()}
        self.summary["stacks"] = {
            sid: {
                "values": {k: v.get("value") for k, v in (s.get("values") or {}).items()},
                "duty": _core.stack_duty(s),
                "equipment": [
                    {
                        "tag": e["tag"],
                        "role": e["role"],
                        "status": e["status"],
                        "fingerprint": e.get("fingerprint"),
                        "values": {k: v.get("value") for k, v in (e.get("values") or {}).items()},
                    }
                    for e in s.get("equipment", [])
                ],
            }
            for sid, s in stacks.items()
        }
        lines = [ln for ln in drafted.splitlines() if ln.strip()]
        print(
            f"[8] datasheets draft: {len(lines)} line(s); cheme process stack --write: {len(written)} file(s) written"
        )

    # -- 9 ----------------------------------------------------------------------------------
    def balance_and_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "balance.json"
            _core.cheme(
                self.root, "run", "scripts/skid_balance.py", env={"BALANCE_OUTPUT": str(out)}
            )
            doc = json.loads(out.read_text(encoding="utf-8"))
        if doc.get("contract") != "balance-output/1":
            raise _core.CoreError("scripts/skid_balance.py wrote no balance-output/1")
        flowsheet = self.load("process/flowsheet.yaml")
        ids = {s["id"] for s in flowsheet["streams"]}
        changes = []
        for case, streams in doc["cases"].items():
            for sid, values in streams.items():
                if sid not in ids:
                    raise Refused(
                        f"scripts/skid_balance.py gives {sid}, not a stream of process/flowsheet.yaml"
                    )
                stream = next(s for s in flowsheet["streams"] if s["id"] == sid)
                state = (stream.get("state") or {}).get(case) or {}
                src = doc["sources"][case][sid]
                if "duty" in values:
                    want = {"value": values["duty"], "provenance": "assumed", "source": src}
                    if not _same(state.get("duty"), want):
                        changes.append((["streams", ("id", sid), "state", case, "duty"], want))
                    continue
                want_flow = {
                    "value": values["flow"],
                    "basis": "mass",
                    "provenance": "assumed",
                    "source": src,
                }
                if not _same(state.get("flow"), want_flow):
                    changes.append((["streams", ("id", sid), "state", case, "flow"], want_flow))
                want_comp = {
                    "basis": "mass_fraction",
                    "values": values["composition"],
                    "provenance": "assumed",
                    "source": src,
                }
                if not _same(state.get("composition"), want_comp):
                    changes.append(
                        (["streams", ("id", sid), "state", case, "composition"], want_comp)
                    )
        self.edit("process/flowsheet.yaml", changes)
        _core.cheme(self.root, "process", "build")
        balances = {}
        for case in doc["cases"]:
            table = _core.cheme(self.root, "process", "streams", "--case", case, "--json").json()
            balances[case] = table.get("balances")
        validate = _core.cheme(self.root, "validate", "--json", ok=(0, 1)).json()
        problems = [
            f for f in validate.get("findings", []) if f.get("level") in ("error", "warning")
        ]
        for f in problems:
            self.note(
                "9",
                f["level"],
                f"{f.get('file')}:{f.get('line')} {f.get('rule')}: {f.get('message')}",
            )
        self.summary["balance"] = {"changed_values": len(changes), "balances": balances}
        print(
            f"[9] flowsheet: {len(changes)} value(s) applied; BFD and PFD built; validate: {len(problems)} error/warning finding(s)"
        )

    def run(self) -> None:
        self.preflight()
        self.sync_product()
        self.horizons()
        point = self.check_cell()
        self.size_skid_a()
        self.set_skid_b(point)
        self.copy_comparison()
        self.datasheets_and_stacks()
        self.balance_and_build()


def _num(x: float):
    return int(x) if float(x).is_integer() else x


def _round(x: float, digits: int = 9) -> float:
    return float(f"{x:.{digits}g}")


def _litres(q: dict) -> float:
    factor = {"L": 1.0, "mL": 1e-3, "m3": 1e3}[q.get("unit", "L")]
    return float(q["value"]) * factor


def _same(have, want) -> bool:
    if have is None:
        return False
    return yaml.safe_load(ye.flow(have)) == yaml.safe_load(ye.flow(want))


def _check(root: Path, duration: float) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / root.name
        shutil.copytree(root, scratch, ignore=COPY_IGNORE)
        Run(scratch, duration).run()
        differ = [
            rel for rel in MODEL_FILES if (scratch / rel).read_bytes() != (root / rel).read_bytes()
        ]
        ds = root / "equipment" / "datasheets"
        for path in sorted((scratch / "equipment" / "datasheets").glob("*.yaml")):
            mine = ds / path.name
            if not mine.exists() or mine.read_bytes() != path.read_bytes():
                differ.append(f"equipment/datasheets/{path.name}")
    for rel in differ:
        print(f"[check] differs from a regeneration at {duration:g} h: {rel}")
    print(f"[check] {'clean' if not differ else str(len(differ)) + ' file(s) differ'}")
    return 3 if differ else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="cheme run scripts/regen.py", description=__doc__.split("\n\n")[0]
    )
    parser.add_argument("--duration", type=float, required=True, help="the campaign H, h")
    parser.add_argument("--scratch", type=Path, help="run in a copy of the folder at DIR")
    parser.add_argument(
        "--check", action="store_true", help="regenerate in a temporary copy and compare"
    )
    parser.add_argument("--uncertainty", action="store_true", help="bounding runs (next stage)")
    parser.add_argument("--record", action="store_true", help="cheme runs record (next stage)")
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.uncertainty or args.record:
        print(
            "regen: --uncertainty and --record are not implemented yet (steps 15 and 18, next stage of #330)",
            file=sys.stderr,
        )
        return 2
    try:
        if args.check:
            return _check(root, args.duration)
        if args.scratch:
            target = args.scratch.resolve()
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(root, target, ignore=COPY_IGNORE)
            root = target
        run = Run(root, args.duration)
        run.run()
    except Refused as exc:
        print(f"regen: refused: {exc}", file=sys.stderr)
        return 2
    except (_core.CoreError, ye.EditRefused) as exc:
        print(f"regen: tool error: {exc}", file=sys.stderr)
        return 1
    summary = root / "build" / f"regen-{args.duration:g}h.json"
    summary.parent.mkdir(exist_ok=True)
    summary.write_text(
        json.dumps({"summary": run.summary, "findings": run.findings}, indent=1, default=str),
        encoding="utf-8",
    )
    errors = [f for f in run.findings if f["level"] == "error"]
    print(
        f"regen: H = {args.duration:g} h done; {len(run.findings)} finding(s), {len(errors)} error(s) (results, not tool failures); summary {summary.relative_to(root)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
