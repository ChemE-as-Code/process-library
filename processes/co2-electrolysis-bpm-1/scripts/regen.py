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

1. Preflight: core version (and, printed only, the commit its installer recorded), sha256 of
   the inputs regen never writes (the model files it writes are hashed after the run, in the
   record's model_sha256); H in the design basis scenarios, else the run is labelled ad hoc.
2. Sync from the design basis: stacks[].product (rate, recovery, purity, pressure) and
   stacks[].replacement.operating_hours.
3. Write the horizons and thresholds: D-A and D-B to H, the comparison duties to 3 H, every
   duty's pH threshold from the design basis, and D-A-PART's step points (12 h at 200, 12 h
   at 100 mA/cm2) over 3 H.
4. Check the cell: `cheme process cell --json`; a refused cell stops the run.
5. Size Skid A: `cheme process stack --write` writes D-A's reservoir volume (core's
   `reservoir.size: to_horizon`, exact: V = V0 Q(H) / Q*, rounded up to 4 significant
   figures) and the tanks from the duty at it; D-A then runs at that volume, asserted to reach
   its horizon (feasible) with no dosing, bleed, make-up or degassing.
6. Set Skid B at the design basis' setpoints (capacity.pilot_skid.skid_b_setpoints): the bleed
   b = Cx (1 - WDE) N I / (F C_T) at the setpoint carbon C_T, the dose
   [b [K+] + (1 - Cx)(1 - WDE) N I / F] / c_dose with [K+] from the setpoints' charge balance
   and c_dose D-B's dosing concentration, and the make-up b - dose, corrected once from the
   probe run's volume drift (N I from the probe's charge over its operating time, so a probe
   that ends early still gives the right rates); asserted: |V_end - V0| / V0 <= 1 % and the
   species at H at the setpoints within 1e-3 mol/L.
7. Copy D-A's volume into the comparison duties (they run at STK-A's arrangement through
   `stack: STK-A`; asserted equal to the stack's).
8. `cheme datasheets draft` (new tags only), then `cheme process stack --write` again: the
   tanks and the pumps' type_specific from the duties as they now are. The tool owns those
   values; never hand-edit them.
9. `cheme run scripts/skid_balance.py` (contract balance-output/1), its values (flows,
   compositions, duties, the anolyte temperatures and the compressor and product pressures)
   applied to process/flowsheet.yaml (targeted edit), then `cheme process build` (BFD, PFD)
   and `cheme process streams` for both cases. A duty that ends before H is a finding: the
   balance is then over its operating time; a balance that cannot be made is a finding too,
   and the flowsheet is left as it was. Then the calculated setpoints of control/loops.yaml:
   every target linked to a stream (`stream:`, `property:`) from the flowsheet, the stack
   current (JIC-x01) from `cheme process stack` and the pH setpoint of AIC-201 from D-B.
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
    findings of `cheme validate --json`, and the stacks' maintenance access (process/cells.yaml
    stacks[].access: the clear space at the ends and sides of each stack, which core does not
    model as an envelope) against the other items; the generated details (tank roof
    handrails, ladders, hose valves) above the envelope or outside the frame in plan and the
    pipes above it are reported apart. Then the validate findings.

14. Conditional invariants: per skid, from the duty's series, the hours outside the measured
    current density (core's time_outside_measured_range_h), temperature (the cooler duty
    against the stack heat: the model is isothermal by assumption), electrolyte state (OH- and
    carbon of species_mol_l against fresh 1 M KOH after its 1 h run) and time on stream (H
    against 1 h). FE, WDE, U and kWh/kg are "invariant" only if every condition holds, else
    "held constant by assumption, not supported by measurement" (DESIGN.md D-014).
15. --uncertainty: in temporary copies only, bounding `performance: specified` cells at the
    measured mean and mean +- 1 sd of WDE, FE CO and U (the sd of the measured series) and at
    the 20 degC meter basis (FE x 273.15 / 293.15, D-005): the cells, the reservoir volume to the
    horizon and the time the design reservoir lasts, the dosing and kWh/kg, into
    results/scenarios/<H>h/uncertainty.json, and two band figures drawn by the script
    (figures/skids/<H>h/uncertainty-ranges.svg, uncertainty-ph-band.svg).
16. The calculation record results/scenarios/<H>h/record.json: the inputs' sha256, core's
    version, the condensed duty, stack and comparison results, the per-skid values, the duty
    run_fingerprint, the feasibility with its reasons and the invariants. Deterministic: no time
    stamp or git HEAD, floats to 10 significant figures (scripts/_results.py).
17. The resize report results/resize-1000h-10000h.{json,md} once both scenarios' records exist:
    one row per quantity and skid with both values, changed or not, its rule
    (invariant-of-duration, proportional-to-duration, fixed-by-setpoint, amortisation,
    infeasible), the calculated cause (its inputs taken from the records) and the frozen hand
    value of results/expected.yaml with its tolerance and status, and the errata of the frozen
    file (results/expected-errata.yaml); the unchanged artefacts (P&ID sha256, stack
    dimensions); and the results table of README.md (between its regen markers). With them, once
    both scenarios' LCA records exist (step 20), the LCA's sensitivities and ranking
    (lca/sensitivity-*.json, lca/ranking.json) and the tables of lca/README.md
    (scripts/lca_sensitivity.py, #331).
18. --record: `cheme runs record --kind manual --slug regen-<H>h --report-file
    results/resize-1000h-10000h.md` (the session record of ADR 0020, not the calculation
    record).
19. --check: every scenario (or only --duration H) regenerated in a temporary copy and compared
    with the committed records, the resize report, the README results table, the scenario's
    figures and, for the design duration, the model files (with control/loops.yaml) and
    datasheets, the LCA's files (lca/lca.yaml, core's outputs, lca/datasets/, lca/scenarios/) and
    the LCA reports of step 17 (exit 3 on a difference). The uncertainty runs are repeated for a
    scenario whose uncertainty.json is committed.
20. The LCA of both skids (#331, scripts/_lca.py; run after step 16, numbered after the
    existing steps): the values lca/lca.yaml takes from the design (the functional unit's
    kg_per_unit, the replaced parts and the operating hours), `cheme assess lca --write`, `--write
    --case skid-b` (Skid B's own dataset in lca/datasets/), `cheme assess lca-scenarios --write`,
    the readings `cheme assess lca --json`, `--balance --json` (Skid B's in a copy studying
    skid-b) and `lca-cases --json`, then the scenario's LCA record
    results/scenarios/<H>h/lca.json: every exchange per kg CO, the reconciliation with the duty
    totals of the record (E10), the K and C balances, the run fingerprints and their citations,
    the scenario totals and the gaps. A dataset that does not reconcile is a finding (error).

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

import _core
import _lca
import _results as res
import _yamledit as ye
import lca_sensitivity
import yaml

SCRIPT = "scripts/regen.py"
#: the hand-maintained inputs that regen reads and never writes (hashed in step 1); the files
#: it writes in part are hashed after the run (MODEL_FILES, the record's model_sha256)
INPUTS = (
    "process/design-basis.yaml",
    "process/materials.yaml",
    "process/reactions.yaml",
    "experiments/electrochemistry/rbpm-1m-koh.yaml",
    "layout/equipment-placement.yaml",
    "layout/structures.yaml",
    "layout/zones.yaml",
    "control/cause-effect.yaml",
    "control/sequences.yaml",
    # the LCA's own inputs (step 20, #331); lca/lca.yaml is written in part by step 20
    "lca/factors.yaml",
    "process/simulation.yaml",
)
#: what --check compares (the model files this stage writes); hashed after the run
MODEL_FILES = (
    "process/cells.yaml",
    "process/duties.yaml",
    "process/flowsheet.yaml",
    "process/BFD.xml",
    "process/PFD.xml",
    "equipment/equipment-list.yaml",
    "layout/plant-model.yaml",
    "control/loops.yaml",
)
#: what --check also compares at the design duration: the LCA (step 20) and the files and
#: folders core's LCA writes (scripts/_lca.py)
LCA_COMPARE = (_lca.LCA_YAML, *_lca.LCA_OUTPUTS)
README = "README.md"
README_BEGIN = "<!-- regen:results begin (scripts/regen.py step 17; do not edit) -->"
README_END = "<!-- regen:results end -->"
ERRATA = "results/expected-errata.yaml"
#: the figure folders of one scenario (H substituted), written by steps 10, 12 and 15
SCENARIO_FIGURES = ("figures/skids/{h}h", "figures/duty/{h}h", "figures/compare/{h}h")
#: the records of one scenario (steps 15 and 16)
SCENARIO_RESULTS = "results/scenarios/{h}h"
RECORD = SCENARIO_RESULTS + "/record.json"
UNCERTAINTY = SCENARIO_RESULTS + "/uncertainty.json"
#: the resize report between the two design scenarios (step 17)
RESIZE = "results/resize-1000h-10000h"
EXPECTED = "results/expected.yaml"
PIDS = ("pid/P-01.xml", "pid/P-02.xml")
#: the bounding cells of --uncertainty (step 15): name, shifts in sd of the measured point
UNCERTAINTY_CASES = (
    ("mean (specified)", {}),
    ("WDE -1 sd", {"wde": -1}),
    ("WDE +1 sd", {"wde": 1}),
    ("FE CO -1 sd", {"fe": -1}),
    ("FE CO +1 sd", {"fe": 1}),
    ("U -1 sd", {"u": -1}),
    ("U +1 sd", {"u": 1}),
    ("FE at the 20 degC meter basis", {"meter_k": 293.15}),
)
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
IGNORED = ("build", ".venv", "__pycache__", ".DS_Store", ".claude", "runs")
COPY_IGNORE = shutil.ignore_patterns(*IGNORED)
STACKS = {"A": "STK-A", "B": "STK-B"}
SKID_DUTIES = {"A": "D-A", "B": "D-B"}
COMPARISON = ("D-A-ONOFF", "D-A-PART")
PART_LOAD = ((12.0, 200.0), (12.0, 100.0))  # (h, mA/cm2): both measured points
#: the loops whose setpoint regen calculates without a stream link: {loop: (what, skid)}
CALCULATED_SETPOINTS = {
    "JIC-101": ("bus_current", "A"),
    "JIC-201": ("bus_current", "B"),
    "AIC-201": ("steady_ph", "B"),
    "LIC-201": ("working_level", "B"),
}


class Refused(RuntimeError):
    """Input the run refuses (exit 2)."""


class Run:
    def __init__(self, root: Path, duration: float, uncertainty: bool = False) -> None:
        self.root = root
        self.h = float(duration)
        self.with_uncertainty = uncertainty
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

    def basis(self) -> dict:
        return self.load("process/design-basis.yaml")["capacity"]["pilot_skid"]

    def setpoints(self) -> dict[str, float]:
        """Skid B's ASSUMED steady state (design basis skid_b_setpoints, DESIGN.md D-010)."""
        sp = self.basis()["skid_b_setpoints"]
        return {k: float(sp[k]["value"]) for k in ("hydroxide_mol_l", "carbon_mol_l")}

    # -- 1 ----------------------------------------------------------------------------------
    def preflight(self) -> None:
        core = _core.core_info()
        shas = {}
        for rel in INPUTS:
            path = self.root / rel
            shas[rel] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        basis = self.basis()
        scenarios = [float(x) for x in basis["duration"]["scenarios"]]
        ad_hoc = self.h not in scenarios
        if ad_hoc:
            self.note(
                "1",
                "warning",
                f"duration {self.h:g} h is not a design scenario {scenarios}: the run is ad hoc",
            )
        frozen = (self.load(EXPECTED) or {}).get("core") or {}
        if frozen.get("version") and frozen["version"] != core["version"]:
            self.note(
                "1",
                "warning",
                f"core {core['version']} is not the {frozen['version']} the expectations were frozen for",
            )
        # the record carries the version only: the commit depends on how core was installed
        self.summary.update(
            core={"version": core["version"]},
            core_install_commit=core["commit"],
            inputs_sha256=shas,
            ad_hoc=ad_hoc,
            scenarios_h=scenarios,
        )
        print(
            f"[1] core {core['version']} (installed from {core['commit'] or 'a local tree, commit not recorded'}), H = {self.h:g} h"
        )

    # -- 2 ----------------------------------------------------------------------------------
    def sync_product(self) -> None:
        basis = self.basis()
        product = basis["product"]
        hours = basis["operating_hours"]
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
            have = stack["replacement"]["operating_hours"]
            for key in ("value", "unit"):
                if have.get(key) != hours[key]:
                    path = ["stacks", ("id", sid), "replacement", "operating_hours", key]
                    changes.append((path, hours[key]))
        changed = self.edit("process/cells.yaml", changes)
        print(
            f"[2] stacks[].product and replacement.operating_hours "
            f"{'synced (' + str(len(changes)) + ' values)' if changed else 'current'}"
        )

    # -- 3 ----------------------------------------------------------------------------------
    def horizons(self) -> None:
        duties = self.load("process/duties.yaml")
        threshold = self.basis()["threshold"]["ph"]
        changes = []
        for did, h in [(d, self.h) for d in SKID_DUTIES.values()] + [
            (d, 3 * self.h) for d in COMPARISON
        ]:
            duty = next(x for x in duties["duties"] if x["id"] == did)
            want = {"value": h, "unit": "h"}
            if duty["horizon"] != want:
                changes.append((["duties", ("id", did), "horizon"], want))
            if duty["threshold"]["ph"] != threshold:
                changes.append((["duties", ("id", did), "threshold", "ph"], threshold))
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
        if da["refused"]:
            raise Refused(f"D-A refused by cheme process duty: {da['reasons']}")
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
            "limited_by": da["required_volume_limited_by"],
            "ended": da["ended"],
            "feasible": da["feasible"],
        }

    # -- 6 ----------------------------------------------------------------------------------
    def set_skid_b(self, point: dict) -> None:
        duties = self.load("process/duties.yaml")
        db = next(d for d in duties["duties"] if d["id"] == "D-B")
        v0 = _litres(db["reservoir"]["volume"])
        c_dose = _molar(db["dosing"]["concentration"])
        setpoints = self.setpoints()
        oh_set, ct_set = setpoints["hydroxide_mol_l"], setpoints["carbon_mol_l"]
        probe = _core.duty(_core.duty_report(self.root, ["D-B"]), "D-B")
        if probe["refused"]:
            raise Refused(f"D-B refused by cheme process duty: {probe['reasons']}")
        tot = _core.totals(probe)
        n_cells = int(probe["cells_in_series"]) * int(probe["stacks"])
        # the electrons per hour over the time the probe ran, not over H: a probe at stale rates
        # may end early (threshold, minimum inventory), and its charge covers only that time
        e_mol_h = tot["charge_c"] / _hours_run(probe) / _core.FARADAY
        co_ion = tot["membrane_cation_mol"] + tot["membrane_carbon_mol"]
        cx = tot["membrane_carbon_mol"] / co_ion  # the duty's carbon share (the titration's)
        b = _steady_b(point["wde"], cx, e_mol_h, setpoints, probe, c_dose)
        k_set, bleed, dose_mol, dose_l = b["cation_mol_l"], b["bleed_l_h"], b["dose_mol_h"], b["dose_l_h"]
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
        drift = (v0 - _core.totals(run)["final_volume_l"]) / _hours_run(run)
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
            "final_ph": t2["final_ph"],
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
            result = _core.cheme(
                self.root,
                "run",
                "scripts/skid_balance.py",
                env={"BALANCE_OUTPUT": str(out)},
                ok=(0, 1),
            )
            doc = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
        if result.returncode != 0 or doc is None:
            # no balance (a refused duty, a route balance that does not close): a finding; the
            # flowsheet keeps its values and the record says why
            message = (result.stderr or result.stdout).strip().splitlines()
            self.note(
                "9",
                "error",
                "scripts/skid_balance.py made no balance, process/flowsheet.yaml left as it was: "
                + (message[-1] if message else f"exit {result.returncode}"),
            )
            self.summary["balance"] = {"changed_values": 0, "balances": {}, "made": False}
            _core.cheme(self.root, "process", "build")
            return
        if doc.get("contract") != "balance-output/1":
            raise _core.CoreError("scripts/skid_balance.py wrote no balance-output/1")
        for message in doc.get("notes") or []:
            self.note("9", "error", f"scripts/skid_balance.py: {message}")
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
                for quantity in ("pressure", "temperature"):
                    if quantity not in values:
                        continue
                    want = {
                        "value": values[quantity],
                        "provenance": "assumed",
                        "source": doc["condition_sources"][case][sid][quantity],
                    }
                    if not _same(state.get(quantity), want):
                        changes.append((["streams", ("id", sid), "state", case, quantity], want))
                if "flow" not in values:
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
        self.summary["balance"] = {"changed_values": len(changes), "balances": balances, "made": True}
        print(f"[9] flowsheet: {len(changes)} value(s) applied; BFD and PFD built")

    def control_setpoints(self) -> None:
        """The calculated setpoints of control/loops.yaml: a target linked to a stream from the
        flowsheet (its case's value), the stack current from `cheme process stack`, the Skid B
        pH setpoint from D-B's steady state (2 decimals) and its level setpoint from the
        reservoir margin (CALCULATED_SETPOINTS)."""
        loops = self.load("control/loops.yaml")
        flowsheet = self.load("process/flowsheet.yaml")
        streams = {s["id"]: s for s in flowsheet["streams"]}
        units = flowsheet.get("units") or {}
        changes = []
        for loop in loops.get("loops") or []:
            for i, target in enumerate(loop.get("targets") or []):
                want = None
                if target.get("stream") and target.get("property"):
                    case = (target.get("cases") or loop.get("cases") or [None])[0]
                    state = ((streams.get(target["stream"]) or {}).get("state") or {}).get(case) or {}
                    quantity = state.get(target["property"]) or {}
                    if "value" not in quantity:
                        self.note(
                            "9", "warning",
                            f"{loop['id']}: {target['stream']} {target['property']} has no value in case {case}",
                        )  # fmt: skip
                        continue
                    unit = units.get(target["property"])
                    if unit and target.get("unit") and target["unit"] != unit:
                        self.note(
                            "9", "warning",
                            f"{loop['id']}: setpoint in {target['unit']}, the flowsheet in {unit}: not synced",
                        )  # fmt: skip
                        continue
                    want = float(quantity["value"])
                elif target.get("kind") == "setpoint" and loop["id"] in CALCULATED_SETPOINTS:
                    what, key = CALCULATED_SETPOINTS[loop["id"]]
                    if what == "bus_current":
                        want = float(self.summary["stacks"][STACKS[key]]["values"]["bus_current_a"])
                    elif what == "working_level":
                        # the working volume in the tank's held volume (its margin), flat ends
                        stack = next(
                            s for s in self.load("process/cells.yaml")["stacks"] if s["id"] == STACKS[key]
                        )
                        margin = float(stack["equipment"]["reservoir"]["margin"]["value"])
                        want = round(100.0 / (1.0 + margin), 1)
                    else:
                        want = round(float(self.summary["skid_b"]["final_ph"]), 2)
                if want is None:
                    continue
                want = _num(want) if float(want).is_integer() else want
                if not _same(target.get("value"), want):
                    changes.append((["loops", ("id", loop["id"]), "targets", i, "value"], want))
        self.edit("control/loops.yaml", changes)
        self.summary["control_setpoints"] = {"changed_values": len(changes)}
        print(f"[9] control/loops.yaml: {len(changes)} calculated setpoint(s) written")

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
        co_rate = _core.totals(da)["product_kg"] / _hours_run(da)
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
                r["id"]: {k: v for k, v in r.items() if k != "id"}
                for r in _core.compare_rows(report)
            }
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
            for d in _core.duties(run)
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
            # the stacks' maintenance access (process/cells.yaml stacks[].access): core sizes
            # the stack footprint with it but draws no envelope for it, so it is checked here
            cells = self.load("process/cells.yaml")
            stack_cfg = next(s for s in cells["stacks"] if s["id"] == STACKS[key])
            access = {k: float(v["value"]) for k, v in (stack_cfg.get("access") or {}).items()}
            access_clear = _stack_access(items, stack_cfg["tags"], access)
            reasons += access_clear
            # generated details outside the frame in plan (ladders, nozzles, hose valves):
            # reported, not counted, as the details above the envelope
            outside = []
            for i in items:
                p = i["parts_plan"]
                if p and (p[0] < x0 - tol or p[1] < y0 - tol or p[2] > x1 + tol or p[3] > y1 + tol):
                    outside.append({"tag": i["tag"], "kind": "parts", "plan": p})
            for i in _core.model_inline_of(model, f"pid/{skid['sheet']}.xml"):
                p = i["plan"]
                if p and (p[0] < x0 - tol or p[1] < y0 - tol or p[2] > x1 + tol or p[3] > y1 + tol):
                    outside.append({"tag": i["tag"], "kind": "inline", "plan": p})
            outside.sort(key=lambda d: (d["kind"], d["tag"]))
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
                "details_outside_plan": outside,
                "stack_access_m": access,
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
            if outside:
                self.note(
                    "13",
                    "info",
                    f"Skid {key}: generated details beyond the frame {skid['frame']} in plan, not "
                    "counted (ladders, nozzles and hose valves at its edge): "
                    + ", ".join(
                        f"{d['tag']} {'details' if d['kind'] == 'parts' else 'inline'} "
                        f"[{d['plan'][0]:.3f}, {d['plan'][1]:.3f}, {d['plan'][2]:.3f}, {d['plan'][3]:.3f}]"
                        for d in outside
                    ),
                )
        accepted = _accepted_ids(self.root)
        problems = [
            f
            for f in validate
            if f.get("level") in ("error", "warning") and f.get("id") not in accepted
        ]
        for f in problems:
            self.note(
                "13", f["level"], f"{f.get('file')}:{f.get('line')} {f.get('rule')}: {f.get('message')}"
            )
        self.summary["envelope"] = {"basis": env, "skids": result}
        print(
            f"[13] validate: {len(problems)} error/warning finding(s) not accepted in "
            "checks/checks.yaml"
        )

    # -- 14 ---------------------------------------------------------------------------------
    def measured_state(self, duty_a: dict) -> dict:
        """The electrolyte the performance was measured in: fresh 1 M KOH (90 mL) after its 1 h
        run at 1 A, from the measured WDE and the duty's carbon share (the titration's)."""
        bench = _core.cell_point(_core.cell_report(self.root), "bench-cell")
        ref = self.load("process/design-basis.yaml")["capacity"]["reference_cell"]
        volume_l = _litres_text(ref["anolyte"]["volume"])
        seconds = float(bench["validity"].get("duration_s") or 3600.0)
        tot = _core.totals(duty_a)
        cx = tot["membrane_carbon_mol"] / (tot["membrane_cation_mol"] + tot["membrane_carbon_mol"])
        co_ion = (1 - bench["wde"]) * bench["current_a"] * seconds / _core.FARADAY / volume_l
        c0 = float(
            next(d for d in self.load("process/duties.yaml")["duties"] if d["id"] == "D-A")[
                "reservoir"
            ]["composition"]["hydroxide"]["value"]
        )
        return {
            "electrolyte": bench["validity"].get("electrolyte"),
            "hydroxide_fresh_mol_l": c0,
            "carbon_max_mol_l": cx * co_ion,
            # [OH-] = [K+] - 2 C at pH ~14: the K+ that left and two OH- per carbon taken up
            "hydroxide_min_mol_l": c0 - (1 - cx) * co_ion - 2 * cx * co_ion,
            "time_on_stream_h": seconds / 3600.0,
            "anolyte_volume_l": volume_l,
            "co_ion_carbon_share": cx,
            "source": (
                "experiments/electrochemistry/rbpm-1m-koh.yaml (1 h runs at 1 A on 5 cm2 in 90 mL "
                "fresh 1 M KOH): carbon Cx (1 - WDE) I t / (F V), hydroxide c0 - (1 + Cx)(1 - WDE) "
                "I t / (F V)"
            ),
        }

    def invariants(self) -> None:
        run = _core.duty_report(self.root, list(SKID_DUTIES.values()))
        measured = self.measured_state(_core.duty(run, "D-A"))
        flowsheet = self.load("process/flowsheet.yaml")
        cells = self.load("process/cells.yaml")
        pilot = next(c for c in cells["cells"] if c["id"] == "pilot-cell")
        t_cell = float(pilot["thermal"]["temperature"]["value"])
        t_meas = self.summary["cell"]["validity"].get("temperature_k") or [298.15, 298.15]
        t_meas_c = float(t_meas[0]) - 273.15
        out, final = {}, {}
        for key, did in SKID_DUTIES.items():
            duty = _core.duty(run, did)
            n = 1 if key == "A" else 2
            cooler = _stream_duty(flowsheet, f"Q{n}05", SKIDS[key]["case"])
            heat = self.summary["stacks"][STACKS[key]]["values"]["heat_duty_kw"]
            out[key] = res.conditions(duty, measured, cooler, heat, t_cell, t_meas_c)
            out[key]["cooler_stream"] = f"Q{n}05"
            series = duty["series"]
            species = {k: v[-1] for k, v in series["species_mol_l"].items()}
            final[key] = {
                "species_mol_l": species,
                "ionic_strength_mol_l": series["ionic_strength_mol_l"][-1],
                "duty": _core.condensed_duty(duty),
            }
            failed = out[key]["failed"]
            if failed:
                hours = ", ".join(
                    f"{name} {out[key]['conditions'][name]['hours_outside']:,.1f} h"
                    for name in failed
                )
                self.note(
                    "14",
                    "warning",
                    f"Skid {key} ({did}): FE, WDE, U and kWh/kg {res.LABEL_ASSUMED} "
                    f"(outside the measured conditions: {hours})",
                )
            else:
                print(f"[14] Skid {key} ({did}): every condition holds, FE, WDE, U invariant")
        self.summary["measured_state"] = measured
        self.summary["invariants"] = out
        self.summary["skid_final"] = final

    # -- 15 ---------------------------------------------------------------------------------
    def uncertainty(self) -> None:
        """Bounding specified cells in temporary copies: the measured mean, mean +- 1 sd of WDE,
        FE CO and U one at a time, and the 20 degC meter basis (D-005)."""
        point = self.summary["cell"]
        da = next(d for d in self.load("process/duties.yaml")["duties"] if d["id"] == "D-A")
        design_l = _litres(da["reservoir"]["volume"])
        threshold = float(da["threshold"]["ph"])
        setpoints = self.setpoints()
        db = next(d for d in self.load("process/duties.yaml")["duties"] if d["id"] == "D-B")
        c_dose = _molar(db["dosing"]["concentration"])
        rows, band = [], []
        with tempfile.TemporaryDirectory() as tmp:
            for i, (name, shift) in enumerate(UNCERTAINTY_CASES):
                copy = Path(tmp) / f"case-{i}" / self.root.name
                shutil.copytree(
                    self.root, copy, ignore=shutil.ignore_patterns(*IGNORED, "figures", "results")
                )
                cell = _bounding_cell(point, shift)
                _write_specified(copy / "process", cell, name)
                stack = _core.stack(_core.stack_report(copy), STACKS["A"])
                v = {k: (x or {}).get("value") for k, x in (stack.get("values") or {}).items()}
                run = _core.duty_report(copy, ["D-A"])
                d = _core.duty(run, "D-A")
                if d.get("refused"):
                    raise _core.CoreError(f"--uncertainty {name}: D-A refused: {d.get('reasons')}")
                required = d["required_volume_l"]
                lasts = d["time_to_threshold_h"] if d["ended"] == "threshold" else self.h
                e_mol_h = v["cells_total"] * v["stack_current_a"] * 3600.0 / _core.FARADAY
                tot = _core.totals(d)
                # the carbon share the specified cell's duty ran at (its membrane block)
                cell["cx"] = tot["membrane_carbon_mol"] / (
                    tot["membrane_cation_mol"] + tot["membrane_carbon_mol"]
                )
                b = _steady_b(cell["wde"], cell["cx"], e_mol_h, setpoints, d, c_dose)
                rows.append(
                    {
                        "case": name,
                        "cell": cell,
                        "cells": v["cells_total"],
                        "stacks": v["stacks"],
                        "cells_per_stack": v["cells_per_stack"],
                        "dc_power_kw": v["dc_power_kw"],
                        "co_formed_kg_h": v["product_output_kg_h"],
                        "kwh_per_kg_formed": v["electricity_kwh_per_kg"],
                        "skid_a_volume_to_horizon_l": required,
                        "skid_a_design_volume_lasts_h": lasts,
                        "skid_a_design_volume_reaches_horizon": d["ended"] == "horizon",
                        "skid_b_bleed_l_h": b["bleed_l_h"],
                        "skid_b_dose_mol_h": b["dose_mol_h"],
                        "skid_b_dose_l_h": b["dose_l_h"],
                    }
                )
                if name in ("mean (specified)", "WDE -1 sd", "WDE +1 sd"):
                    band.append(
                        {
                            "label": f"WDE {cell['wde']:.4f}"
                            + (" (mean)" if name.startswith("mean") else f" ({name[4:]})"),
                            "t_h": d["series"]["t_h"],
                            "ph": d["series"]["ph"],
                        }
                    )
                print(
                    f"[15] {name}: {v['cells_total']} cells ({v['stacks']} x {v['cells_per_stack']}), "
                    f"{v['electricity_kwh_per_kg']:.4g} kWh/kg, V_A {required:.6g} L to {self.h:g} h, "
                    f"the design {design_l:g} L lasts {lasts:.6g} h; Skid B dose {b['dose_mol_h']:.5g} mol/h"
                )
        base = rows[0]
        keys = (
            ("cells", "cells", "-"),
            ("kwh_per_kg_formed", "electricity per kg CO formed", "kWh/kg"),
            ("skid_a_volume_to_horizon_l", "Skid A volume to the horizon", "L"),
            ("skid_a_design_volume_lasts_h", "Skid A design reservoir lasts", "h"),
            ("skid_b_dose_mol_h", "Skid B KOH dose", "mol/h"),
            ("skid_b_bleed_l_h", "Skid B bleed", "L/h"),
        )
        ranges = {}
        for key, _label, _unit in keys:
            sd_vals = [r[key] for r in rows[1:-1] if r[key] is not None]
            ranges[key] = {
                "mean": base[key],
                "sd_bounds": [min(sd_vals), max(sd_vals)],
                "meter_20c": rows[-1][key],
            }
        doc = {
            "schema": res.UNCERTAINTY_SCHEMA,
            "issue": 330,
            "duration_h": self.h,
            "design_volume_l": design_l,
            "method": (
                "bounding runs (core does not propagate the measured scatter, design core_gaps C2): "
                "pilot-cell as performance: specified at the measured mean and at mean +- 1 sd of "
                "one parameter at a time (the sample sd over the replicates of P200), and at the "
                "20 degC meter basis (FE x 273.15 / 293.15, DESIGN.md D-005); the co-ion split "
                f"the membrane block's (carbon share {base['cell']['cx']:.4g}, the share the "
                "bounding duties ran at); Skid B's rates from the closed-form steady state at "
                f"the setpoints ({setpoints['hydroxide_mol_l']:g} mol/L OH-, "
                f"{setpoints['carbon_mol_l']:g} mol/L carbon) and D-B's {c_dose:g} mol/L dose"
            ),
            "cases": rows,
            "ranges": ranges,
        }
        out = self.root / UNCERTAINTY.format(h=f"{self.h:g}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(res.dump(doc), encoding="utf-8")
        figs = self.root / SCENARIO_FIGURES[0].format(h=f"{self.h:g}")
        figs.mkdir(parents=True, exist_ok=True)
        quantities = [
            {
                "label": label,
                "unit": unit,
                "base": base[key],
                "cases": [{"case": r["case"], "value": r[key]} for r in rows[1:]],
            }
            for key, label, unit in keys
        ]
        (figs / "uncertainty-ranges.svg").write_text(
            res.range_svg(
                quantities,
                f"Measurement uncertainty at {self.h:,.0f} h: one parameter at a time",
                "Bounding specified cells at the P200 mean +- 1 sd of WDE, FE CO and U, and FE at "
                "the 20 degC meter basis",
            ),
            encoding="utf-8",
        )
        (figs / "uncertainty-ph-band.svg").write_text(
            res.band_svg(
                band,
                threshold,
                self.h,
                f"Skid A design reservoir ({design_l:,.0f} L) against WDE +- 1 sd",
                f"Duty D-A at 200 mA/cm2; the reservoir sized at the mean reaches pH {threshold:g} "
                "early at WDE - 1 sd (no time margin, D-009)",
            ),
            encoding="utf-8",
        )
        self.summary["uncertainty"] = {"ranges": ranges}
        print(f"[15] {len(rows)} bounding runs: {out.relative_to(self.root)}, two band figures")

    # -- 16 ---------------------------------------------------------------------------------
    def skid_block(self, key: str) -> dict:
        s = self.summary
        sid = STACKS[key]
        st = s["stacks"][sid]
        v = st["values"]
        eq = {e["tag"]: e for e in st["equipment"]}
        res_tag = SKIDS[key]["reservoir"]
        tank = eq[res_tag]["values"]
        did = SKID_DUTIES[key]
        tot = s["duties"][did]["totals"]
        final = s["skid_final"][key]
        recovery = v["product_recovery"]
        delivered = tot["product_kg"] * recovery
        m_koh = _molar_mass(self.root, "KOH")
        stacks_cfg = next(x for x in self.load("process/cells.yaml")["stacks"] if x["id"] == sid)
        margin = float(stacks_cfg["equipment"]["reservoir"]["margin"]["value"])
        fill_kg = tot["initial_cation_mol"] * m_koh / 1000.0
        dosed_kg = tot["dosing_hydroxide_kg"]
        env = s["envelope"]["skids"][key]
        duty_ok = bool(s["duties"][did]["feasible"])
        reasons = list(env["reasons"])
        if not duty_ok:
            reasons.insert(0, f"duty {did} ended by {s['duties'][did]['ended']}")
        feasible = duty_ok and env["feasible"]
        pump = eq[f"P-{1 if key == 'A' else 2}01"]["values"]
        block = {
            "stack": sid,
            "duty": did,
            "case": SKIDS[key]["case"],
            "cells": v["cells_total"],
            "stacks": v["stacks"],
            "cells_per_stack": v["cells_per_stack"],
            "stack_voltage_v": v["stack_voltage_v"],
            "bus_current_a": v["bus_current_a"],
            "dc_power_kw": v["dc_power_kw"],
            "ac_power_kw": v["ac_power_kw"],
            "co_formed_kg_h": v["product_output_kg_h"],
            "co_delivered_kg_h": v["product_delivered_kg_h"],
            "margin": v["output_margin"],
            "kwh_per_kg_formed": v["electricity_kwh_per_kg"],
            "kwh_per_kg_delivered": v["electricity_kwh_per_kg_delivered"],
            "stack_heat_kw": v["heat_duty_kw"],
            "cooler_kw": s["invariants"][key]["conditions"]["temperature"]["cooler_kw"],
            "recirculation_kg_h": pump.get("mass_flow_kg_h"),
            "stack_envelope_m": {
                "length": v["stack_length_m"],
                "width": v["stack_width_m"],
                "height": v["stack_height_m"],
            },
            "reservoir_tag": res_tag,
            "reservoir_volume_l": v["reservoir_working_volume_l"],
            "reservoir_held_m3": v["reservoir_working_volume_l"] * (1 + margin) / 1000.0,
            "reservoir_diameter_m": tank["diameter"],
            "reservoir_height_m": tank["height"],
            "final_ph": tot["final_ph"],
            "final_carbon_mol_l": tot["final_carbon_mol"] / tot["final_volume_l"],
            "final_cation_mol_l": tot["final_cation_mol"] / tot["final_volume_l"],
            "final_hydroxide_mol_l": final["species_mol_l"].get("OH-"),
            "final_ionic_strength_mol_l": final["ionic_strength_mol_l"],
            "final_volume_l": tot["final_volume_l"],
            "totals_charge_c": tot["charge_c"],
            "totals_energy_kwh": tot["energy_kwh"],
            "totals_product_kg": tot["product_kg"],
            "totals_delivered_kg": delivered,
            "dosed_solution_l": tot["dosing_solution_l"],
            "dosed_hydroxide_kg": dosed_kg,
            "bleed_l": tot["bleed_l"],
            "makeup_water_l": tot["makeup_water_l"],
            "hydroxide_deficit_mol": tot["hydroxide_deficit_mol"],
            "koh_fill_kg": fill_kg,
            "koh_fill_kg_h": fill_kg / self.h,
            "koh_per_kg_delivered": (fill_kg + dosed_kg) / delivered,
            "koh_fill_per_kg_delivered": fill_kg / delivered,
            "koh_dosed_per_kg_delivered": dosed_kg / delivered,
            "run_fingerprint": st["duty"].get("run_fingerprint"),
            "equipment": st["equipment"],
            "items_top_m": env["items_top_m"],
            "envelope_top_m": env["envelope_top_m"],
            "headroom_left_m": env["headroom_left_m"],
            "envelope_feasible": env["feasible"],
            "duty_feasible": duty_ok,
            "feasible": feasible,
            "reasons": reasons,
            "sentences": _infeasible_sentences(key, self.h, did, s["duties"][did], env["feasible"]),
            "details_above_envelope": env["details_above_envelope"],
            "details_outside_plan": env["details_outside_plan"],
            "stack_access_m": env["stack_access_m"],
            "invariants": s["invariants"][key],
            "duty_result": final["duty"],
        }
        reservoir_cfg = stacks_cfg["equipment"]["reservoir"]
        # the inputs of the resize report's calculated causes (step 17)
        basis = {
            "reservoir_margin": margin,
            "reservoir_aspect_ratio": float(reservoir_cfg["aspect_ratio"]["value"]),
            "usable_height_m": s["envelope"]["basis"]["usable_height"],
            "threshold_ph": float(self.basis()["threshold"]["ph"]),
            "max_stack_voltage_v": float(stacks_cfg["electrical"]["max_stack_voltage"]["value"]),
        }
        if key == "A":
            block["reservoir_volume_exact_l"] = s["skid_a"]["volume_exact_l"]
            block["reservoir_limited_by"] = s["skid_a"]["limited_by"]
        else:
            b = s["skid_b"]
            tank_cfg = stacks_cfg["equipment"]["dosing_tank"]
            pump_cfg = stacks_cfg["equipment"]["dosing_pump"]
            db = next(d for d in self.load("process/duties.yaml")["duties"] if d["id"] == did)
            basis.update(
                {f"setpoint_{k}": v for k, v in self.setpoints().items()},
                dose_concentration_mol_l=_molar(db["dosing"]["concentration"]),
                dose_density_kg_l=float(db["dosing"]["density"]["value"]),
                dosing_pump_margin=float(pump_cfg["margin"]["value"]),
                refill_interval_h=float(tank_cfg["refill_interval"]["value"]),
                reservoir_volume_l=_litres(db["reservoir"]["volume"]),
            )
            block.update(
                bleed_l_h=b["bleed_l_h"],
                dose_mol_h=b["dose_mol_h"],
                dose_l_h=b["dose_l_h"],
                makeup_l_h=b["makeup_l_h"],
                residence_h=b["residence_h"],
                carbon_share_duty=b["carbon_share_duty"],
                cation_setpoint_mol_l=b["cation_setpoint_mol_l"],
                dosing_pump_kg_h=eq["P-202"]["values"]["mass_flow_kg_h"],
                dosing_tank_diameter_m=eq["T-202"]["values"]["diameter"],
                dosing_tank_height_m=eq["T-202"]["values"]["height"],
                dosing_tank_fills=v["dosing_tank_fills_per_campaign"],
                dosing_solution_per_fill_l=v["dosing_solution_per_fill_l"],
                dosing_tank_held_l=v["dosing_solution_per_fill_l"]
                * (1 + float(tank_cfg["margin"]["value"])),
            )
        block["sizing_basis"] = basis
        return block

    def write_record(self) -> None:
        s = self.summary
        root = self.root
        record = {
            "schema": res.RECORD_SCHEMA,
            "issue": 330,
            "command": f"cheme run {SCRIPT} --duration {self.h:g}",
            "duration_h": self.h,
            "ad_hoc": s["ad_hoc"],
            "scenarios_h": s["scenarios_h"],
            "core": s["core"],
            # the hand-maintained inputs regen never writes; the files it writes, after the run
            "inputs_sha256": s["inputs_sha256"],
            "model_sha256": {rel: _sha(root / rel) for rel in MODEL_FILES},
            "pid_sha256": {rel: _sha(root / rel) for rel in PIDS},
            "cell": {k: v for k, v in s["cell"].items() if k != "reasons"},
            "measured_state": s["measured_state"],
            "skids": {key: self.skid_block(key) for key in SKIDS},
            "duties": s["duties"],
            "comparisons": s["comparisons"],
            "envelope_basis": s["envelope"]["basis"],
            "control": s["control"],
            "findings": [f for f in self.findings if f["level"] in ("error", "warning")],
        }
        if "uncertainty" in s:
            record["uncertainty"] = {
                "file": UNCERTAINTY.format(h=f"{self.h:g}"),
                "ranges": s["uncertainty"]["ranges"],
            }
        out = root / RECORD.format(h=f"{self.h:g}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(res.dump(record), encoding="utf-8")
        a, b = record["skids"]["A"], record["skids"]["B"]
        print(
            f"[16] {out.relative_to(root)}: Skid A feasible {a['feasible']}, Skid B feasible "
            f"{b['feasible']}; invariants: A {a['invariants']['fe_wde_u_kwh_per_kg']!r}, "
            f"B {b['invariants']['fe_wde_u_kwh_per_kg']!r}"
        )

    # -- 20 ---------------------------------------------------------------------------------
    def lca(self) -> None:
        """The LCA of both skids on the design as this run left it (scripts/_lca.py, #331)."""
        record = json.loads((self.root / RECORD.format(h=f"{self.h:g}")).read_text(encoding="utf-8"))
        rep = _core.stack_report(self.root)
        stacks = {sid: _core.stack(rep, sid) for sid in STACKS.values()}
        try:
            out = _lca.step(self.root, self.h, record, stacks)
        except _lca.LcaError as exc:
            self.note("20", "error", f"the LCA cannot be made: {exc}")
            return
        doc = out["doc"]
        for key, s in doc["skids"].items():
            bad = [r["quantity"] for r in s["reconciliation"] if not r["ok"]]
            if bad:
                self.note("20", "error", f"Skid {key}: the dataset does not reconcile with the duty totals: {', '.join(bad)}")
            if not s["lca_cases_agree"]:
                self.note("20", "error", f"Skid {key}: cheme assess lca-cases differs from the dataset")
            if not (s["balance"]["k_closed"] and s["balance"]["c_closed"]):
                self.note("20", "error", f"Skid {key}: the K or C balance of the dataset does not close")
            if not s["tanks_carry_run"] or s["sources_uncited"]:
                self.note("20", "error", f"Skid {key}: run {s['run_fingerprint']} not on {s['tank_fingerprints']} or not cited by {s['sources_uncited']}")
        if not doc["manifest_fingerprints_flowsheet"]:
            self.note("20", "error", "lca/manifest.json does not fingerprint the current process/flowsheet.yaml")
        a, b = doc["skids"]["A"], doc["skids"]["B"]
        print(
            f"[20] {out['path'].relative_to(self.root)}: {doc['label']}; per kg CO, Skid A "
            f"{a['impacts']['total']:.4g} and Skid B {b['impacts']['total']:.4g} kg CO2e characterised "
            f"({len(a['impacts']['gaps'])} and {len(b['impacts']['gaps'])} gaps); reconciled A {a['reconciled']}, "
            f"B {b['reconciled']}{'; lca/lca.yaml synced' if out['scope_changed'] else ''}"
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
        self.control_setpoints()
        self.layout_and_datasheets()
        self.control()
        self.duty_plots()
        self.envelope_check()
        self.invariants()
        if self.with_uncertainty:
            self.uncertainty()
        else:
            # step 10 removed the scenario's band figures: a kept uncertainty.json would be stale
            stale = self.root / UNCERTAINTY.format(h=f"{self.h:g}")
            if stale.exists():
                stale.unlink()
                print(f"[15] {stale.relative_to(self.root)} removed (run without --uncertainty)")
        self.write_record()
        self.lca()


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


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def _litres_text(text) -> float:
    """'90 mL' (the design basis' free text) in L."""
    value, unit = str(text).split()[:2]
    return float(value) * {"L": 1.0, "mL": 1e-3, "m3": 1e3}[unit]


def _molar_mass(root: Path, component: str) -> float:
    data = yaml.safe_load((root / "process" / "materials.yaml").read_text(encoding="utf-8"))
    return float(next(c for c in data["components"] if c["id"] == component)["molar_mass"])


def _stream_duty(flowsheet: dict, stream_id: str, case: str) -> float:
    stream = next(s for s in flowsheet["streams"] if s["id"] == stream_id)
    return float(stream["state"][case]["duty"]["value"])


def _accepted_ids(root: Path) -> set[str]:
    """The finding ids that checks/checks.yaml accepts with a reason (any gate)."""
    path = root / "checks" / "checks.yaml"
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = list(data.get("accept") or [])
    for c in data.get("checks") or []:
        entries += c.get("accept") or []
    return {a["id"] for a in entries if isinstance(a, dict) and "id" in a}


def _bounding_cell(point: dict, shift: dict) -> dict:
    """The specified values of one bounding run: the measured mean of P200 moved by whole sd.
    The co-ion split is the membrane block's of process/cells.yaml, which _write_specified
    leaves as it is (a specified cell's duty runs at it); the run reports the share it used."""
    u = point["voltage_v"] + shift.get("u", 0) * point["voltage_sd_v"]
    fe = dict(point["fe"])
    fe["CO"] += shift.get("fe", 0) * point["fe_sd"]["CO"]
    if "meter_k" in shift:  # the flow meter's 0 degC standard basis read at another temperature
        fe = {k: x * 273.15 / shift["meter_k"] for k, x in fe.items()}
    wde = point["wde"] + shift.get("wde", 0) * point["wde_sd"]
    return {"voltage_v": u, "fe_co": fe["CO"], "fe_h2": fe["H2"], "wde": wde}


def _hours_run(duty: dict) -> float:
    """The hours a duty ran (its operating time; the simulated time without one)."""
    hours = duty.get("operating_time_h") or duty.get("simulated_h")
    if not hours:
        raise _core.CoreError(f"duty {duty.get('id')}: no operating or simulated time")
    return float(hours)


def _molar(q: dict) -> float:
    """A concentration in mol/L."""
    unit = q.get("unit", "mol/L")
    factor = {"mol/L": 1.0, "M": 1.0, "mmol/L": 1e-3, "mol/m3": 1e-3}.get(unit)
    if factor is None:
        raise Refused(f"concentration unit {unit} is not known to scripts/regen.py")
    return float(q["value"]) * factor


def _stack_access(items: list[dict], tags: list[str], access: dict[str, float]) -> list[str]:
    """The clear space at the ends (along the stack axis, the item's own x) and sides of each
    stack (process/cells.yaml stacks[].access) against the bodies of the other items on the
    frame, at the stack's height; beyond the frame is the access aisle at grade."""
    end, side = access.get("end", 0.0), access.get("side", 0.0)
    by_tag = {i["tag"]: i for i in items}
    problems = []
    for tag in tags:
        stack = by_tag.get(tag)
        if stack is None:
            continue
        x0, y0, z0, x1, y1, z1 = stack["bbox"]
        axis_y = round(stack["rotation_deg"] / 90.0) % 2 == 1  # the axis runs north-south
        ex, ey = (0.0, end) if axis_y else (end, 0.0)
        sx, sy = (side, 0.0) if axis_y else (0.0, side)
        zones = {
            "end": [(x0 - ex, y0 - ey, x0 if ex else x1, y0 if ey else y1),
                    (x1 if ex else x0, y1 if ey else y0, x1 + ex, y1 + ey)],
            "side": [(x0 - sx, y0 - sy, x0 if sx else x1, y0 if sy else y1),
                     (x1 if sx else x0, y1 if sy else y0, x1 + sx, y1 + sy)],
        }  # fmt: skip
        for kind, boxes in zones.items():
            clear = end if kind == "end" else side
            for ax0, ay0, ax1, ay1 in boxes:
                for other in items:
                    if other["tag"] == tag:
                        continue
                    b = other["bbox"]
                    tol = 1e-6
                    if (
                        b[0] < ax1 - tol and b[3] > ax0 + tol and b[1] < ay1 - tol and b[4] > ay0 + tol
                        and b[2] < z1 - tol and b[5] > z0 + tol
                    ):  # fmt: skip
                        problems.append(
                            f"stack access: {other['tag']} stands in the {clear:g} m {kind} access of {tag}"
                        )
    return sorted(set(problems))


def _infeasible_sentences(key: str, h: float, did: str, duty: dict, envelope_ok: bool) -> list[str]:
    """The sentences of an infeasible skid, one per check that failed."""
    out = []
    if not envelope_ok:
        out.append(f"Skid {key} cannot meet the {h:,.0f} h duty within the skid envelope")
    if not duty["feasible"] or duty["ended"] != "horizon":
        out.append(
            f"Skid {key} cannot meet the {h:,.0f} h duty: duty {did} ended by {duty['ended']}"
        )
    return out


def _write_specified(process: Path, cell: dict, case: str) -> None:
    """In a temporary copy only: pilot-cell as `performance: specified` at *cell*, and its duties
    naming their product (a specified cell's duty must; a measured one takes it from the
    measurement). The files are rewritten by pyyaml: their comments do not matter there."""
    path = process / "duties.yaml"
    duties = yaml.safe_load(path.read_text(encoding="utf-8"))
    for duty in duties["duties"]:
        if duty.get("cell") == "pilot-cell":
            duty.setdefault("product", "CO")
    path.write_text(yaml.safe_dump(duties, sort_keys=False, allow_unicode=True), encoding="utf-8")
    path = process / "cells.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    pilot = next(c for c in data["cells"] if c["id"] == "pilot-cell")
    src = f"bounding run {case} (scripts/regen.py --uncertainty, temporary copy)"
    pilot["performance"] = "specified"
    pilot.pop("measurements", None)
    pilot["voltage"] = {"value": cell["voltage_v"], "unit": "V", "provenance": "assumed", "source": src}
    pilot["faradaic_efficiency"] = {"value": cell["fe_co"], "provenance": "assumed", "source": src}
    pilot["side_reactions"] = [
        {
            "reaction": "WS",
            "electrons": 2,
            "current_fraction": {"value": cell["fe_h2"], "provenance": "assumed", "source": src},
        }
    ]
    pilot["membrane"]["water_dissociation_efficiency"] = {
        "value": cell["wde"],
        "provenance": "assumed",
        "source": src,
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _steady_b(
    wde: float, cx: float, e_mol_h: float, setpoints: dict, duty: dict, c_dose: float
) -> dict:
    """Skid B's bleed and dose at the setpoints, the closed form of step 6: the duty's anolyte
    constants, the carbon share Cx, the electrons per hour N I / F and the dosing
    concentration c_dose (mol/L)."""
    consts = duty["anolyte_constants"]
    oh, ct = setpoints["hydroxide_mol_l"], setpoints["carbon_mol_l"]
    h = consts["Kw"] / oh
    k1, k2 = 10.0 ** -consts["pK1"], 10.0 ** -consts["pK2"]
    g = (k1 * h + 2 * k1 * k2) / (h**2 + k1 * h + k1 * k2)
    cation = oh + ct * g - h
    bleed = cx * (1 - wde) * e_mol_h / ct
    dose = bleed * cation + (1 - cx) * (1 - wde) * e_mol_h
    return {
        "cation_mol_l": cation,
        "bleed_l_h": bleed,
        "dose_mol_h": dose,
        "dose_l_h": dose / c_dose,
    }


def _scenarios(root: Path) -> tuple[float, list[float]]:
    basis = yaml.safe_load((root / "process" / "design-basis.yaml").read_text(encoding="utf-8"))
    duration = basis["capacity"]["pilot_skid"]["duration"]
    return float(duration["design"]["value"]), [float(x) for x in duration["scenarios"]]


def _resize_texts(
    root: Path,
    records: dict[float, dict],
    uncertainty: dict[float, dict] | None = None,
    lca_docs: dict[float, dict] | None = None,
) -> dict[str, str]:
    """The resize report (JSON, Markdown) and README.md with its results table regenerated, and
    the LCA's sensitivities, ranking and lca/README.md tables (scripts/lca_sensitivity.py, #331);
    *uncertainty*, *lca_docs*: the scenarios' uncertainty.json and lca.json (default: those in
    *root*)."""
    if uncertainty is None:
        uncertainty = {}
        for h in records:
            path = root / UNCERTAINTY.format(h=f"{h:g}")
            if path.exists():
                uncertainty[h] = json.loads(path.read_text(encoding="utf-8"))
    expected = yaml.safe_load((root / EXPECTED).read_text(encoding="utf-8"))
    errata_path = root / ERRATA
    errata = yaml.safe_load(errata_path.read_text(encoding="utf-8")) if errata_path.exists() else None
    report = res.resize_report(records, expected, errata)
    texts = {
        f"{RESIZE}.json": res.dump(report),
        f"{RESIZE}.md": res.resize_markdown(res.tidy(report)),
    }
    readme = root / README
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        if README_BEGIN in text and README_END in text:
            head, rest = text.split(README_BEGIN, 1)
            _, tail = rest.split(README_END, 1)
            table = res.readme_table(records, uncertainty)
            texts[README] = f"{head}{README_BEGIN}\n{table}{README_END}{tail}"
    texts.update(lca_sensitivity.texts(root, lca_docs))
    return texts


def write_resize(root: Path) -> list[str]:
    """Step 17: the resize report, when both design scenarios have a record in *root*."""
    _, scenarios = _scenarios(root)
    paths = {h: root / RECORD.format(h=f"{h:g}") for h in scenarios}
    if len(scenarios) != 2 or not all(p.exists() for p in paths.values()):
        print("[17] resize report: waits for the record of every design scenario")
        return []
    records = {h: json.loads(p.read_text(encoding="utf-8")) for h, p in paths.items()}
    stale = [f"{h:g} h" for h, r in records.items() if "sizing_basis" not in r["skids"]["A"]]
    if stale:
        print(f"[17] resize report: waits for the record of {', '.join(stale)} from this regen.py")
        return []
    written = []
    for rel, text in _resize_texts(root, records).items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
        written.append(rel)
    report = json.loads((root / f"{RESIZE}.json").read_text(encoding="utf-8"))
    s = report["summary"]
    print(
        f"[17] {RESIZE}.md: {s['rows']} rows, hand checks failed {s['hand_checks_failed']}, "
        f"rules broken {s['rules_broken'] or 'none'}"
        + ("; README.md results table" if README in written else "")
    )
    return written


def _scenario_outputs(h: float) -> list[str]:
    return [p.format(h=f"{h:g}") for p in (*SCENARIO_FIGURES, SCENARIO_RESULTS)]


def _check(root: Path, durations: list[float]) -> int:
    """Step 19: every scenario regenerated in a temporary copy and compared."""
    design, scenarios = _scenarios(root)
    differ: list[str] = []
    records: dict[float, dict] = {}
    uncertainty: dict[float, dict] = {}
    lca_docs: dict[float, dict] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for h in durations:
            scratch = Path(tmp) / f"{h:g}h" / root.name
            shutil.copytree(root, scratch, ignore=COPY_IGNORE)
            with_unc = (root / UNCERTAINTY.format(h=f"{h:g}")).exists()
            print(f"[check] regenerating {h:g} h{' with --uncertainty' if with_unc else ''}")
            Run(scratch, h, uncertainty=with_unc).run()
            rel_files = []
            if h == design:
                rel_files += [*MODEL_FILES, *LCA_COMPARE]
                for rel in _lca.LCA_TREES:
                    mine, theirs = _tree(root, rel), _tree(scratch, rel)
                    differ += [name for name in sorted(set(mine) | set(theirs)) if mine.get(name) != theirs.get(name)]
                ds = root / "equipment" / "datasheets"
                for path in sorted((scratch / "equipment" / "datasheets").glob("*.yaml")):
                    mine = ds / path.name
                    if not mine.exists() or mine.read_bytes() != path.read_bytes():
                        differ.append(f"equipment/datasheets/{path.name}")
            differ += [
                rel for rel in rel_files if (scratch / rel).read_bytes() != (root / rel).read_bytes()
            ]
            for rel in _scenario_outputs(h):
                mine, theirs = _tree(root, rel), _tree(scratch, rel)
                for name in sorted(set(mine) | set(theirs)):
                    if mine.get(name) != theirs.get(name):
                        differ.append(name)
            path = scratch / RECORD.format(h=f"{h:g}")
            records[h] = json.loads(path.read_text(encoding="utf-8"))
            unc = scratch / UNCERTAINTY.format(h=f"{h:g}")
            if unc.exists():
                uncertainty[h] = json.loads(unc.read_text(encoding="utf-8"))
            lca = scratch / _lca.SCENARIO_LCA.format(h=f"{h:g}")
            if lca.exists():
                lca_docs[h] = json.loads(lca.read_text(encoding="utf-8"))
    if len(scenarios) == 2 and set(scenarios) <= set(records):
        texts = _resize_texts(
            root,
            {h: records[h] for h in scenarios},
            uncertainty,
            {h: lca_docs[h] for h in scenarios} if set(scenarios) <= set(lca_docs) else None,
        )
        for rel, text in texts.items():
            if not (root / rel).exists() or (root / rel).read_text(encoding="utf-8") != text:
                differ.append(rel)
    for rel in differ:
        print(f"[check] differs from a regeneration: {rel}")
    print(f"[check] {'clean' if not differ else str(len(differ)) + ' file(s) differ'}")
    return 3 if differ else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="cheme run scripts/regen.py", description=__doc__.split("\n\n")[0]
    )
    parser.add_argument(
        "--duration", type=float, help="the campaign H, h (with --check: only this scenario)"
    )
    parser.add_argument("--scratch", type=Path, help="run in a copy of the folder at DIR")
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate every scenario (or --duration) in a temporary copy and compare",
    )
    parser.add_argument(
        "--uncertainty", action="store_true", help="bounding runs of the measured scatter (step 15)"
    )
    parser.add_argument(
        "--record", action="store_true", help="cheme runs record of this run (step 18)"
    )
    args = parser.parse_args(argv)
    root = Path.cwd()
    source = root
    try:
        if args.check:
            if args.scratch or args.record or args.uncertainty:
                raise Refused("--check takes no --scratch, --record or --uncertainty")
            _, scenarios = _scenarios(root)
            return _check(root, [args.duration] if args.duration else scenarios)
        if args.duration is None:
            raise Refused("--duration H is required (except with --check)")
        if args.scratch:
            target = args.scratch.resolve()
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(root, target, ignore=COPY_IGNORE)
            root = target
        run = Run(root, args.duration, uncertainty=args.uncertainty)
        run.run()
        resized = write_resize(root) if not run.summary["ad_hoc"] else []
        if root != source:
            # the scenario's figures and records are committed; its model files stay in the
            # scratch copy
            for rel in _scenario_outputs(args.duration):
                if (root / rel).exists():
                    if (source / rel).exists():
                        shutil.rmtree(source / rel)
                    shutil.copytree(root / rel, source / rel)
                    print(f"regen: {rel} copied back from the scratch run")
            for rel in resized:
                (source / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / rel, source / rel)
                print(f"regen: {rel} copied back from the scratch run")
        if args.record:
            report = f"{RESIZE}.md" if (source / f"{RESIZE}.md").exists() else None
            rec = ["runs", "record", "--kind", "manual", "--slug", f"regen-{args.duration:g}h"]
            if report:
                rec += ["--report-file", report]
            out = _core.cheme(source, *rec).stdout.strip()
            print(f"[18] cheme runs record: {out.splitlines()[-1] if out else 'written'}")
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
