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
10. Layout and datasheets: `cheme layout build` (the 3D model from layout/*.yaml, the
    equipment list's sizes and the P&IDs; routing every line, so the same as `cheme layout
    route` without --line); the draft datasheets drafted again from the model as it now is,
    train B's from case skid-b (D-020), and `cheme process stack --write` into them;
    `cheme datasheets fill --case skid-a` for the 1xx tags and
    `--case skid-b` for the 2xx tags, then per skid `cheme layout render` of the frame's
    plan, a section across the reservoir (x) and one along the frame (y), SVG and PNG, copied
    to figures/skids/<H>h/.
11. `cheme control report --json` (into build/control/): the loop and sequence findings.
12. Duty plots and comparisons: `cheme process duty D-A D-B D-A-ONOFF D-A-PART --plot
    figures/duty/<H>h/`; `--compare D-A,D-A-ONOFF,D-A-PART` at half the campaign's CO,
    `D-A,D-A-PART` at the whole (the part-load duty reaches the threshold first:
    cheme.duty-target-not-reached) and `D-A,D-B` at half, each plotted into
    figures/compare/<H>h/<name>/. The CO target is D-A's product over H, from the run.
13. Envelope check: per skid, the union of the layout model's bounding boxes of the items on
    frame SKID-A or SKID-B against the frame's plan and the deck plus the usable height
    (process/design-basis.yaml skid_envelope), plus core's "is not inside structure"
    findings of `cheme validate --json`; the generated details (tank roof handrails, ladders)
    and the pipes above the envelope are reported apart. Then the validate findings.

Steps 14 to 19 (the invariant checks, --uncertainty, the calculation record, the resize
report, --record and the --check of the records) follow in the next stage of #330.

With --scratch DIR the run is made in a copy; the scenario's figures (figures/skids/<H>h,
figures/duty/<H>h, figures/compare/<H>h) are then copied back into this folder, so that the
10,000 h scenario's figures are committed while the model files stay at the 1,000 h design.

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
    "layout/plant-model.yaml",
)
#: the figure folders of one scenario (H substituted), written by steps 10 and 12
SCENARIO_FIGURES = ("figures/skids/{h}h", "figures/duty/{h}h", "figures/compare/{h}h")
#: the train of each skid: its sheet, flowsheet case, frame and reservoir
SKIDS = {
    "A": {"sheet": "P-01", "case": "skid-a", "frame": "SKID-A", "reservoir": "T-101"},
    "B": {"sheet": "P-02", "case": "skid-b", "frame": "SKID-B", "reservoir": "T-201"},
}
#: the comparisons of step 12: name, duties, share of D-A's campaign CO
COMPARISONS = (
    ("equal-co-half", ("D-A", "D-A-ONOFF", "D-A-PART"), 0.5),
    ("part-load-full", ("D-A", "D-A-PART"), 1.0),
    ("skid-a-vs-b-half", ("D-A", "D-B"), 0.5),
)
COMPARE_TOLERANCE = 1e-3
#: margins of the rendered views around a frame, m (the access steps stand outside it)
VIEW_MARGIN = {"west": 0.6, "south": 2.1, "east": 2.1, "north": 0.8}
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
            "ended": run["ended"],
            "feasible": run["feasible"],
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
        self.summary["balance"] = {"changed_values": len(changes), "balances": balances}
        print(f"[9] flowsheet: {len(changes)} value(s) applied; BFD and PFD built")

    # -- 10 ---------------------------------------------------------------------------------
    def layout_and_datasheets(self) -> None:
        # the model first: a draft takes the tanks' tangent lengths from it
        build = _core.layout_build(self.root)
        equipment = self.load("equipment/equipment-list.yaml")["equipment"]
        redrafted = self.redraft_datasheets(equipment)
        written = next((ln for ln in build.splitlines() if ln.startswith("wrote ")), "")
        # the model's findings are taken from cheme validate in step 13, which applies the
        # acceptances of checks/checks.yaml; the build prints them unaccepted
        model_findings = sum(
            1 for ln in build.splitlines() if " warning cheme." in ln or " error cheme." in ln
        )
        if not any(ln.startswith(("wrote ", "unchanged ")) for ln in build.splitlines()):
            raise _core.CoreError(f"cheme layout build: no model written: {build.strip()[-400:]}")
        written = next(
            (ln for ln in build.splitlines() if ln.startswith(("wrote ", "unchanged "))), ""
        )
        filled = {}
        for key, skid in SKIDS.items():
            tags = [e["tag"] for e in equipment if e.get("sheet") == skid["sheet"]]
            result = _core.datasheets_fill(self.root, skid["case"], tags)
            for line in (result.stdout + result.stderr).splitlines():
                if " warning cheme." in line or " error cheme." in line:
                    self.note("10", "warning", line.split(" -- ")[0])
            filled[skid["case"]] = tags
        model = _core.plant_model(self.root)
        out = self.root / SCENARIO_FIGURES[0].format(h=f"{self.h:g}")
        _fresh(out)
        figures = []
        for key, skid in SKIDS.items():
            frame = _core.model_structure(model, skid["frame"])
            x0, y0, x1, y1 = frame["footprint"]
            deck = max(frame["levels"].values())
            items = _core.model_items_on(model, skid["frame"])
            reservoir = next(i for i in items if i["tag"] == skid["reservoir"])
            tops = [i["bbox"][5] for i in items] + [
                p["top_m"] for p in _core.model_pipes_over(model, frame["footprint"])
            ]
            z_top = math.ceil((max(tops + [deck + self.envelope()["usable_height"]]) + 0.6) * 2) / 2
            px0, px1 = x0 - VIEW_MARGIN["west"], x1 + VIEW_MARGIN["east"]
            py0, py1 = y0 - VIEW_MARGIN["south"], y1 + VIEW_MARGIN["north"]
            x_res = (reservoir["bbox"][0] + reservoir["bbox"][3]) / 2
            y_mid = (y0 + y1) / 2
            views = {
                "plan": ["--plan", "--crop", _crop(px0, py0, px1, py1)],
                "section-x": [
                    "--section",
                    f"x={_r(x_res)}",
                    "--depth",
                    _r(reservoir["bbox"][3] - reservoir["bbox"][0] + 0.3),
                    "--crop",
                    _crop(y0 - 1.0, 0.0, y1 + 1.0, z_top),
                ],
                "section-y": [
                    "--section",
                    f"y={_r(y_mid)}",
                    "--depth",
                    _r(y1 - y0 + 0.4),
                    "--crop",
                    _crop(px0, 0.0, px1, z_top),
                ],
            }
            for view, args in views.items():
                for fmt in ([], ["--png"]):
                    for path in _core.render(self.root, *args, *fmt):
                        target = out / f"skid-{key.lower()}-{view}{path.suffix}"
                        shutil.copyfile(path, target)
                        figures.append(str(target.relative_to(self.root)))
        self.summary["layout"] = {
            "build": written,
            "build_findings": model_findings,
            "datasheets_redrafted": redrafted,
            "datasheets_filled": filled,
            "figures": figures,
        }
        print(
            f"[10] {written or 'layout built'} ({model_findings} model finding(s), accepted or not: step 13); datasheets filled per case "
            f"({', '.join(f'{c}: {len(t)}' for c, t in filled.items())}); {len(figures)} figure(s) in {out.relative_to(self.root)}"
        )

    def redraft_datasheets(self, equipment: list[dict]) -> list[str]:
        """Redraw every draft datasheet from the model as it now is, each from its own case.

        `cheme datasheets draft` copies the list sizes and the linked streams' conditions into a
        datasheet and never touches an existing one, `cheme datasheets fill` never overwrites a
        value it gives, and draft reads the default case only (core 1.5.0). A draft kept from an
        earlier run would keep the old campaign's tank size and stream values, and train B's
        drafts would carry case skid-a (zero flows). So regen owns the drafts (`draft: true`,
        DESIGN.md D-020): they are removed and drafted again, train A's in this folder (default
        case skid-a), train B's in a temporary copy whose default case is skid-b, copied back.
        A datasheet without `draft: true` (completed by hand) is kept as it is."""
        ds = self.root / "equipment" / "datasheets"
        drafted = []
        for key, skid in SKIDS.items():
            tags = [e["tag"] for e in equipment if e.get("sheet") == skid["sheet"]]
            redo = []
            for tag in tags:
                path = ds / f"{tag}.yaml"
                if path.exists():
                    if not (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("draft"):
                        continue
                    path.unlink()
                redo.append(tag)
            if not redo:
                continue
            args = ["datasheets", "draft"] + [a for t in redo for a in ("--tag", t)]
            if _default_case(self.load("process/flowsheet.yaml")) == skid["case"]:
                _core.cheme(self.root, *args)
            else:
                with tempfile.TemporaryDirectory() as tmp:
                    copy = Path(tmp) / self.root.name
                    shutil.copytree(self.root, copy, ignore=COPY_IGNORE)
                    _set_default_case(copy / "process" / "flowsheet.yaml", skid["case"])
                    _core.cheme(copy, *args)
                    for tag in redo:
                        shutil.copyfile(
                            copy / "equipment" / "datasheets" / f"{tag}.yaml", ds / f"{tag}.yaml"
                        )
            drafted += redo
        # the pumps' type_specific values of cheme process stack go into the new drafts
        _core.stack_report(self.root, write=True)
        print(f"[10] {len(drafted)} draft datasheet(s) drafted again, each from its case")
        return drafted

    # -- 11 ---------------------------------------------------------------------------------
    def control(self) -> None:
        report = _core.control_report(self.root, self.root / "build" / "control")
        levels: dict[str, int] = {}
        for f in report.get("findings") or []:
            levels[f.get("level", "?")] = levels.get(f.get("level", "?"), 0) + 1
            if f.get("level") == "error":
                self.note("11", "error", f"{f.get('rule')}: {f.get('message')}")
        self.summary["control"] = {
            "loops": len(report.get("loops") or []),
            "sequences": len(report.get("sequences") or []),
            "findings_by_level": dict(sorted(levels.items())),
        }
        print(
            f"[11] control report: {self.summary['control']['loops']} loop(s), "
            f"{self.summary['control']['sequences']} sequence(s), findings {self.summary['control']['findings_by_level']}"
        )

    # -- 12 ---------------------------------------------------------------------------------
    def duty_plots(self) -> None:
        h = f"{self.h:g}"
        duty_dir = self.root / SCENARIO_FIGURES[1].format(h=h)
        _fresh(duty_dir)
        ids = [*SKID_DUTIES.values(), *COMPARISON]
        run = _core.duty_plots(self.root, ids, duty_dir)
        da = _core.duty(run, "D-A")
        co_rate = _core.totals(da)["product_kg"] / float(da["horizon_h"])
        compare_dir = self.root / SCENARIO_FIGURES[2].format(h=h)
        _fresh(compare_dir)
        results = {}
        for name, duties, share in COMPARISONS:
            target = _round(share * self.h * co_rate, 12)
            plot = compare_dir / name
            plot.mkdir(parents=True)
            report = _core.compare_report(
                self.root, list(duties), target, COMPARE_TOLERANCE, plot=plot
            )
            rows = {
                r["id"]: {
                    k: r.get(k)
                    for k in (
                        "reached", "ended", "delivered_kg", "elapsed_h", "charge_c",
                        "energy_kwh", "final_ph", "dosing_hydroxide_kg",
                        "hydroxide_deficit_mol", "feasible", "reason",
                    )
                }
                for r in _core.compare_rows(report)
            }  # fmt: skip
            rules = sorted({f.get("rule") for f in _core.findings(report) if f.get("rule")})
            results[name] = {"duties": list(duties), "target_kg": target, "rows": rows, "rules": rules}
            print(
                f"[12] compare {','.join(duties)} at {target:.6g} kg CO: "
                + "; ".join(
                    f"{d} {'reached' if r['reached'] else 'not reached'} in {r['elapsed_h']:.6g} h"
                    for d, r in rows.items()
                )
                + (f" ({', '.join(rules)})" if rules else "")
            )
        self.summary["duties"] = {
            d["id"]: {
                "ended": d["ended"],
                "feasible": d["feasible"],
                "horizon_h": d["horizon_h"],
                "totals": _core.totals(d),
            }
            for d in run.get("duties", [])
        }
        self.summary["comparisons"] = {"co_rate_kg_h": co_rate, "results": results}
        print(f"[12] duty plots of {', '.join(ids)} in {duty_dir.relative_to(self.root)}")

    # -- 13 ---------------------------------------------------------------------------------
    def envelope(self) -> dict:
        env = self.load("process/design-basis.yaml")["capacity"]["pilot_skid"]["skid_envelope"]
        return {k: float(env[k]["value"]) for k in ("length", "width", "usable_height")}

    def envelope_check(self) -> None:
        env = self.envelope()
        model = _core.plant_model(self.root)
        validate = _core.validate_findings(_core.validate(self.root))
        result = {}
        for key, skid in SKIDS.items():
            frame = _core.model_structure(model, skid["frame"])
            x0, y0, x1, y1 = frame["footprint"]
            deck = max(frame["levels"].values())
            limit = deck + env["usable_height"]
            reasons = []
            if not (
                math.isclose(frame["width"], env["length"], abs_tol=1e-6)
                and math.isclose(frame["depth"], env["width"], abs_tol=1e-6)
            ):
                reasons.append(
                    f"frame {skid['frame']} is {frame['width']:g} x {frame['depth']:g} m, the envelope "
                    f"{env['length']:g} x {env['width']:g} m"
                )
            items = _core.model_items_on(model, skid["frame"])
            box = [
                min(i["bbox"][0] for i in items),
                min(i["bbox"][1] for i in items),
                min(i["bbox"][2] for i in items),
                max(i["bbox"][3] for i in items),
                max(i["bbox"][4] for i in items),
                max(i["bbox"][5] for i in items),
            ]
            tol = 1e-6
            for i in items:
                b = i["bbox"]
                if b[0] < x0 - tol or b[1] < y0 - tol or b[3] > x1 + tol or b[4] > y1 + tol:
                    reasons.append(
                        f"{i['tag']} [{b[0]:.3f}, {b[1]:.3f}, {b[3]:.3f}, {b[4]:.3f}] is outside the frame "
                        f"in plan [{x0:g}, {y0:g}, {x1:g}, {y1:g}]"
                    )
                if b[5] > limit + tol:
                    reasons.append(
                        f"{i['tag']} top {b[5]:.3f} m above grade is above the envelope's {limit:.3f} m "
                        f"(deck {deck:g} m + {env['usable_height']:g} m usable height) by {b[5] - limit:.3f} m"
                    )
            core = [
                f["message"]
                for f in validate
                if f.get("rule") == "cheme.layout-level"
                and f"is not inside structure {skid['frame']} " in f.get("message", "")
            ]
            reasons += [f"core: {m}" for m in core]
            # an item that no longer fits beside the others on the frame (a clash error of the
            # layout model) does not fit the skid either
            tags = {i["tag"] for i in items}
            clashes = [
                f["message"]
                for f in validate
                if f.get("level") == "error"
                and str(f.get("rule", "")).startswith("cheme.layout-clash")
                and tags & set(f.get("ids") or [])
            ]
            reasons += [f"core: {m}" for m in clashes]
            details = sorted(
                (
                    {"tag": i["tag"], "parts_top_m": i["parts_top_m"]}
                    for i in items
                    if i["parts_top_m"] is not None and i["parts_top_m"] > limit + tol
                ),
                key=lambda d: d["tag"],
            )
            pipes = sorted(
                (
                    p
                    for p in _core.model_pipes_over(model, frame["footprint"])
                    if p["top_m"] > limit + tol
                ),
                key=lambda p: p["id"],
            )
            feasible = not reasons
            duty_ok = self.summary.get(f"skid_{key.lower()}", {}).get("feasible", True)
            result[key] = {
                "frame": skid["frame"],
                "footprint": frame["footprint"],
                "deck_m": deck,
                "envelope_top_m": limit,
                "items_bbox": box,
                "items_top_m": box[5],
                "headroom_left_m": limit - box[5],
                "feasible": feasible,
                "reasons": reasons,
                "core_not_inside": core,
                "details_above_envelope": details,
                "pipes_above_envelope": [{"id": p["id"], "line": p["line"], "top_m": p["top_m"]} for p in pipes],
                "skid_feasible": feasible and bool(duty_ok),
            }
            if feasible:
                print(
                    f"[13] Skid {key}: inside the envelope (items top {box[5]:.3f} m, envelope {limit:.3f} m, "
                    f"{limit - box[5]:.3f} m left)"
                )
            else:
                self.note(
                    "13",
                    "error",
                    f"Skid {key} cannot meet the {self.h:,.0f} h duty within the skid envelope: "
                    + "; ".join(reasons),
                )
            if details or pipes:
                self.note(
                    "13",
                    "info",
                    f"Skid {key}: above the {limit:.3f} m envelope but not counted (generated details, "
                    f"fitted or cut at site): "
                    + ", ".join(
                        [f"{d['tag']} details to {d['parts_top_m']:.3f} m" for d in details]
                        + [f"{p['line']} to {p['top_m']:.3f} m" for p in pipes]
                    ),
                )
        problems = [f for f in validate if f.get("level") in ("error", "warning")]
        for f in problems:
            self.note(
                "13", f["level"], f"{f.get('file')}:{f.get('line')} {f.get('rule')}: {f.get('message')}"
            )
        self.summary["envelope"] = {"basis": env, "skids": result}
        print(f"[13] validate: {len(problems)} error/warning finding(s) not accepted")

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
        self.layout_and_datasheets()
        self.control()
        self.duty_plots()
        self.envelope_check()


def _num(x: float):
    return int(x) if float(x).is_integer() else x


def _round(x: float, digits: int = 9) -> float:
    return float(f"{x:.{digits}g}")


def _r(x: float) -> str:
    """A coordinate for a command line: rounded to the millimetre, shortest form."""
    return f"{round(x, 3):g}"


def _crop(a: float, b: float, c: float, d: float) -> str:
    return ",".join(_r(v) for v in (a, b, c, d))


def _default_case(flowsheet: dict) -> str:
    cases = flowsheet.get("cases") or []
    return next((c["id"] for c in cases if c.get("default")), cases[0]["id"] if cases else "")


def _set_default_case(path: Path, case: str) -> None:
    """In a temporary copy only: make *case* the flowsheet's default (the `default: true` line
    moved under its id), checked by loading the result."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines = [ln for ln in lines if ln.strip() != "default: true"]
    at = next(i for i, ln in enumerate(lines) if ln.strip() == f"- id: {case}")
    indent = lines[at][: len(lines[at]) - len(lines[at].lstrip())] + "  "
    lines.insert(at + 1, f"{indent}default: true\n")
    text = "".join(lines)
    if _default_case(yaml.safe_load(text)) != case:
        raise ye.EditRefused(f"{path}: could not make {case} the default case")
    path.write_text(text, encoding="utf-8")


def _fresh(path: Path) -> None:
    """An empty folder: the previous run's figures are removed, so none is left stale."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def _tree(root: Path, rel: str) -> dict[str, bytes]:
    base = root / rel
    if not base.exists():
        return {}
    return {
        str(p.relative_to(root)): p.read_bytes() for p in sorted(base.rglob("*")) if p.is_file()
    }


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
        for pattern in SCENARIO_FIGURES:
            rel = pattern.format(h=f"{duration:g}")
            mine, theirs = _tree(root, rel), _tree(scratch, rel)
            for name in sorted(set(mine) | set(theirs)):
                if mine.get(name) != theirs.get(name):
                    differ.append(name)
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
    source = root
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
        if root != source:
            # the scenario's figures are committed; its model files stay in the scratch copy
            for pattern in SCENARIO_FIGURES:
                rel = pattern.format(h=f"{args.duration:g}")
                if (root / rel).exists():
                    if (source / rel).exists():
                        shutil.rmtree(source / rel)
                    shutil.copytree(root / rel, source / rel)
                    print(f"regen: {rel} copied back from the scratch run")
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
