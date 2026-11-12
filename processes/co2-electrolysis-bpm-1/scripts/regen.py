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
   duty's pH threshold from the design basis' trip value (threshold.trip.ph, the pH the plant
   stops at, D-058; threshold.ph is the stability criterion D-003 it protects), and D-A-PART's
   step points (12 h at 200, 12 h at 100 mA/cm2) over 3 H.
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
    `--case skid-b` for the 2xx tags, then `cheme layout render` of the plot plan (core's A1
    sheet, figures/skids/<H>h/layout-plan.{svg,png}) and per skid of the frame's plan, a
    section across the reservoir and one across the first stack (x), one along the stack row
    and one along the whole frame (y), each sheet cropped to its drawing at core's scale and
    rasterised (scripts/_figures.py, DESIGN.md D-041), as
    figures/skids/<H>h/layout-plan-skid-<k>.{svg,png} and layout-section-<x|y>-skid-<k>-<what>.
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
    model as an envelope) against the other items and their generated parts, and each stack's
    replacement by hand (D-047, layout/layout-checks.yaml stack_removal): its far end plate
    within reach of a person at grade at the frame's south side and its slide lane at deck
    level out over that edge clear (each a reason when it fails); the ignition sources U-x01 and
    X-x32 against every hazardous zone source's outline, its box joined with its nozzle points
    (sphere radius plus a margin, an error finding when short; D-057), the same sources against
    the feet of the frame's stairs (layout/layout-checks.yaml stair_feet, an error finding when
    short; D-057) and the cable trays against the vent and flue outlets (a warning); the
    generated details (tank roof handrails, ladders, hose valves) above the envelope or outside
    the frame in plan and the pipes above it are reported apart. Then the validate findings.

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
    the scenario totals and the gaps. A step 20 error (the LCA cannot be made, a dataset that
    does not reconcile, lca-cases disagreeing, an open K or C balance, a spent or bleed density
    outside its band, the run not traced) fails the run (exit 4): the committed LCA would
    otherwise stay as an earlier design left it. When the LCA cannot be made at all, the
    scenario's lca.json is removed (it would describe another design).
21. Item weights (run before step 10, numbered after the existing steps; scripts/_lifting.py,
    DESIGN.md D-043): every listed item's empty weight from layout/lifting-basis.yaml (ASSUMED:
    the outline volume times a bulk density, a tank's shell, bottom and roof at one wall
    thickness, or a vendor's weight) into the equipment list's dimensions.weight, so the model
    and core's lifting study carry it; the tanks' weights follow their sizes with H.
22. Material take-off (after step 12, before step 13, whose validate then reads it current):
    `cheme assess mto --write` (estimate/mto.csv, .md) of the model as built; its totals into
    the record. No estimate: the project has no rates of its own (D-044).
23. Lifting study (after step 22, before step 13): `cheme layout lifting --write`
    (layout/lifting-study.csv, .md: every listed item of heavy_lift_t or more), then the lifts
    core cannot express, worked
    out with its criteria on the model (scripts/_lifting.py): each skid as a 20 ft unit, dry and
    with its tanks full, and T-101 alone, drained and full, into
    layout/lifting-study-units.csv and .md; both into the record (at 10,000 h the infeasible
    Skid A's lifts are reported there, never fixed).
24. Cable schedule (after step 23, before step 13; DESIGN.md D-045): the model step 10 built
    holds the trays and cables of electrical/electrical-list.yaml and electrical/tray-rules.yaml
    (hand-authored intent); `cheme layout cables --write` writes electrical/cable-schedule.csv
    and .md, its summary (cables, trays, lengths, what has no cable) and the tray and cable
    findings of step 13's validate go into the record. Step 13 also reports, per skid, the
    trays over the frame above the envelope (site-fitted, as the vent risers) and any level
    tray run lower than the walkway headroom over the deck.
25. The 3D results into the record (after step 13; DESIGN.md D-046): `cheme layout report
    --json` gives every line's status, so the record's layout block holds the process lines of
    DN 25 and above routed, skipped with their reason or unrouted (a warning), the smaller
    lines by status, the route methods (a direct fallback is a warning), the model rule
    finding counts, the clashes of step 13's validate (each accepted in checks/checks.yaml or
    not) and per skid the items' top against the envelope. With the record's lifting (step 23)
    these are the 3D results of each scenario; at 10,000 h they are reported, never fatal.

Findings of steps 1 to 17, 21 to 25 are collected, never fatal: an infeasible skid is a result. The exit
code is non-zero on a tool error (1), on refused input (2), on a --check difference (3) or on a
step 20 error (4; --check counts it as a difference too, and requires the scratch run to have
written the scenario's lca.json).
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path

import _core
import _figures
import _lca
import _lifting
import _results as res
import _yamledit as ye
import lca_sensitivity
import yaml

SCRIPT = "scripts/regen.py"
#: the cable schedule `cheme layout cables --write` writes (step 24)
CABLE_CSV = "electrical/cable-schedule.csv"
CABLE_MD = "electrical/cable-schedule.md"
#: the walkway headroom over a deck that a level tray run should keep, m (core's routing
#: default headroom_walkway_m; core checks pipes against it, not trays: step 13 reports them)
TRAY_HEADROOM_M = 2.1
#: the project's own layout checks of step 13 (D-047): stack removal, ignition sources, vent
#: outlets against the trays, the steel core draws that the design deletes
LAYOUT_CHECKS = "layout/layout-checks.yaml"
#: the smallest nominal diameter whose process lines must be routed or skipped with a reason
#: (the layout-3d gate; step 25): the DN 15 skid small bore is the fabricator's (D-019)
ROUTED_DN = 25
#: the hand-maintained inputs that regen reads and never writes (hashed in step 1); the files
#: it writes in part are hashed after the run (MODEL_FILES, the record's model_sha256)
INPUTS = (
    "process/design-basis.yaml",
    "process/materials.yaml",
    "process/reactions.yaml",
    "experiments/electrochemistry/rbpm-1m-koh.yaml",
    "layout/equipment-placement.yaml",
    "layout/site-plan.yaml",
    "layout/structures.yaml",
    "layout/zones.yaml",
    "layout/lifting-basis.yaml",
    LAYOUT_CHECKS,
    "piping/routing.yaml",
    # the electrical intent (step 24, D-045): rooms, motors, feeders, junction boxes, points
    "electrical/electrical-list.yaml",
    "electrical/tray-rules.yaml",
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
    # the take-off (step 22) and the lifting studies (step 23) of the model
    "estimate/mto.csv",
    "estimate/mto.md",
    "layout/lifting-study.csv",
    "layout/lifting-study.md",
    _lifting.UNITS_CSV,
    _lifting.UNITS_MD,
    # the cable schedule of the model (step 24)
    CABLE_CSV,
    CABLE_MD,
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
#: margins of the rendered views around a frame, m (the access steps stand outside it, the
#: tail-gas oxidiser east of it, D-047)
VIEW_MARGIN = {"west": 0.6, "south": 2.1, "east": 3.9, "north": 0.8}
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
    # the total cathode CO2 (D-062): the fresh CO2 and the PSA recycle of the case's flowsheet
    "FIC-104": ("stream_sum", "A"),
    "FIC-204": ("stream_sum", "B"),
}
#: the streams whose flows a "stream_sum" setpoint adds, per loop (the fresh CO2 and the recycle)
SUMMED_STREAMS = {"FIC-104": ("S101", "S103"), "FIC-204": ("S201", "S203")}


class Refused(RuntimeError):
    """Input the run refuses (exit 2)."""


class Run:
    def __init__(self, root: Path, duration: float, uncertainty: bool = False) -> None:
        self.root = root
        self.h = float(duration)
        self.with_uncertainty = uncertainty
        self.findings: list[dict] = []
        self.summary: dict = {"duration_h": self.h}
        #: step 13's `cheme validate --json` findings (step 25 reads its clashes)
        self.validate_findings: list[dict] = []

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

    def trip_ph(self) -> float:
        """The pH the duties run to and T-101 is sized at: the trip of I-101 and I-201, above
        the stability criterion threshold.ph (D-003) by the margin of D-058."""
        threshold = self.basis()["threshold"]
        trip = float(threshold["trip"]["ph"])
        if trip < float(threshold["ph"]):
            raise SystemExit(f"design basis: the trip pH {trip:g} is below the criterion {threshold['ph']:g}")
        return trip

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
        threshold = self.trip_ph()
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
        pH setpoint from D-B's steady state (2 decimals), its level setpoint from the
        reservoir margin and the total cathode CO2 as the sum of the fresh and the recycle
        streams (CALCULATED_SETPOINTS, SUMMED_STREAMS, D-062)."""
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
                    elif what == "stream_sum":
                        case = (target.get("cases") or loop.get("cases") or [None])[0]
                        flows = [
                            (((streams.get(s) or {}).get("state") or {}).get(case) or {}).get("flow") or {}
                            for s in SUMMED_STREAMS[loop["id"]]
                        ]
                        if any("value" not in f for f in flows):
                            self.note("9", "warning", f"{loop['id']}: a summed stream has no flow in case {case}")
                            continue
                        want = sum(float(f["value"]) for f in flows)
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
        flagged = self.flag_assumed_weights(equipment)
        model = _core.plant_model(self.root)
        out = self.root / SCENARIO_FIGURES[0].format(h=f"{self.h:g}")
        _fresh(out)
        figures = []
        # the plot plan of the whole plot: core's A1 sheet (1:50 fits the 32 m plot), its roads
        # drawn under its zones so the crane pads and the laydown on the road show (D-043),
        # rasterised at core's own resolution
        for path in _core.render(self.root, "--plan"):
            svg = _figures.roads_under_zones(path.read_text(encoding="utf-8"))
            (out / "layout-plan.svg").write_text(svg, encoding="utf-8", newline="")
            (out / "layout-plan.png").write_bytes(_figures.svg_to_png(svg, _figures.CORE_PX_PER_MM))
            figures += [f"{out.relative_to(self.root)}/layout-plan{s}" for s in (".svg", ".png")]
        cells = self.load("process/cells.yaml")
        scenario = f"{self.h:,.0f} h campaign"
        for key, skid in SKIDS.items():
            frame = _core.model_structure(model, skid["frame"])
            x0, y0, x1, y1 = frame["footprint"]
            deck = max(frame["levels"].values())
            items = _core.model_items_on(model, skid["frame"])
            reservoir = next(i for i in items if i["tag"] == skid["reservoir"])
            stack_cfg = next(s for s in cells["stacks"] if s["id"] == STACKS[key])
            access = {k: float(v["value"]) for k, v in (stack_cfg.get("access") or {}).items()}
            stacks = [i for i in items if i["tag"] in stack_cfg["tags"]]
            tops = [i["bbox"][5] for i in items] + [
                p["top_m"] for p in _core.model_pipes_over(model, frame["footprint"])
            ]
            z_top = math.ceil((max(tops + [deck + self.envelope()["usable_height"]]) + 0.6) * 2) / 2
            px0, px1 = x0 - VIEW_MARGIN["west"], x1 + VIEW_MARGIN["east"]
            py0, py1 = y0 - VIEW_MARGIN["south"], y1 + VIEW_MARGIN["north"]
            x_res = (reservoir["bbox"][0] + reservoir["bbox"][3]) / 2
            y_mid = (y0 + y1) / 2
            # the first stack across (its slide lane to the south side, D-047) and the
            # stack row along the frame, each as deep as the stacks with their hand room
            first = min(stacks, key=lambda i: i["tag"])
            x_stk = (first["bbox"][0] + first["bbox"][3]) / 2
            y_stk = (min(i["bbox"][1] for i in stacks) + max(i["bbox"][4] for i in stacks)) / 2
            stk_dx = first["bbox"][3] - first["bbox"][0] + 2 * access.get("side", 0.0)
            stk_dy = max(i["bbox"][4] for i in stacks) - min(i["bbox"][1] for i in stacks)
            stk_dy += 2 * access.get("end", 0.0)
            name = f"Skid {key}"
            section_x_crop = _crop(y0 - 1.0, 0.0, y1 + 1.0, z_top)
            views = {
                f"layout-plan-skid-{key.lower()}": (
                    f"{name} plan ({scenario})",
                    ["--plan", "--crop", _crop(px0, py0, px1, py1)],
                ),
                f"layout-section-x-skid-{key.lower()}-reservoir": (
                    f"{name} section x = {_r(x_res)} m through {skid['reservoir']}, looking west ({scenario})",
                    ["--section", f"x={_r(x_res)}", "--depth",
                     _r(reservoir["bbox"][3] - reservoir["bbox"][0] + 0.3), "--crop", section_x_crop],
                ),
                f"layout-section-x-skid-{key.lower()}-stack": (
                    f"{name} section x = {_r(x_stk)} m through {first['tag']}, looking west ({scenario})",
                    ["--section", f"x={_r(x_stk)}", "--depth", _r(stk_dx), "--crop", section_x_crop],
                ),
                f"layout-section-y-skid-{key.lower()}-stacks": (
                    f"{name} section y = {_r(y_stk)} m along the stacks, looking north ({scenario})",
                    ["--section", f"y={_r(y_stk)}", "--depth", _r(stk_dy), "--crop",
                     _crop(px0, 0.0, px1, z_top)],
                ),
                f"layout-section-y-skid-{key.lower()}-frame": (
                    f"{name} section y = {_r(y_mid)} m, the whole frame, looking north ({scenario})",
                    ["--section", f"y={_r(y_mid)}", "--depth", _r(y1 - y0 + 0.4), "--crop",
                     _crop(px0, 0.0, px1, z_top)],
                ),
            }  # fmt: skip
            for stem, (title, args) in views.items():
                for path in _core.render(self.root, *args):
                    # core's A1 sheet cropped to the drawing, at its scale (D-041)
                    svg = _figures.crop_sheet(path.read_text(encoding="utf-8"), title)
                    (out / f"{stem}.svg").write_text(svg, encoding="utf-8", newline="")
                    (out / f"{stem}.png").write_bytes(_figures.svg_to_png(svg))
                    figures += [f"{out.relative_to(self.root)}/{stem}{s}" for s in (".svg", ".png")]
        self.summary["layout"] = {
            "build": written,
            "build_findings": model_findings,
            "datasheets_redrafted": redrafted,
            "datasheets_filled": filled,
            "datasheets_weight_assumed": flagged,
            "figures": figures,
        }
        print(
            f"[10] {written or 'layout built'} ({model_findings} model finding(s), accepted or not: step 13); datasheets filled per case "
            f"({', '.join(f'{c}: {len(t)}' for c, t in filled.items())}); {len(figures)} figure(s) in {out.relative_to(self.root)}"
        )

    def flag_assumed_weights(self, equipment: list[dict]) -> list[str]:
        """Mark the empty weight of a draft datasheet `assumed: true` where the equipment list
        marks the item's dimensions assumed (every weight of step 21 is, D-043). Core 1.5.0's
        draft copies `dimensions.weight` into `weights.empty` and `type_specific.weight_t`
        with the flag off (it carries the list's flag to the other dimensions only), so those
        two entries are flagged here: a line added to each, checked to change nothing else."""
        ds = self.root / "equipment" / "datasheets"
        flagged = []
        for item in equipment:
            dims = item.get("dimensions") or {}
            path = ds / f"{item['tag']}.yaml"
            if not (dims.get("assumed") and dims.get("weight") is not None and path.exists()):
                continue
            text = path.read_text(encoding="utf-8")
            before = yaml.safe_load(text) or {}
            if not before.get("draft"):
                continue
            lines = text.split("\n")
            want = []
            for parent, key in (("weights", "empty"), ("type_specific", "weight_t")):
                if key not in (before.get(parent) or {}) or (before[parent][key] or {}).get("assumed"):
                    continue
                top = lines.index(f"{parent}:")
                at = next(i for i in range(top + 1, len(lines)) if lines[i] == f"  {key}:")
                end = at + 1
                while end < len(lines) and lines[end].startswith("    "):
                    end += 1
                lines.insert(end, "    assumed: true")
                want.append((parent, key))
            if not want:
                continue
            new = "\n".join(lines)
            expect = before
            for parent, key in want:
                expect[parent][key]["assumed"] = True
            if yaml.safe_load(new) != expect:
                raise _core.CoreError(f"{path.name}: flagging the weight assumed would change more")
            path.write_text(new, encoding="utf-8")
            flagged.append(item["tag"])
        print(f"[10] {len(flagged)} datasheet(s): the empty weight flagged assumed (core drafts it unflagged)")
        return flagged

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
        solids = _core.model_solids(model)
        validate = _core.validate_findings(_core.validate(self.root))
        # step 25 reads the clashes of this validate
        self.validate_findings = validate
        # the project's own layout checks (D-047): stack removal, ignition sources, vent
        # outlets against the trays, the steel core draws that the design deletes
        checks = self.load(LAYOUT_CHECKS)
        deleted = [d["pattern"] for d in checks.get("deleted_steel") or []]
        vents = _vent_tray_clearance(model, checks["vent_tray_clearance"])
        for v in vents:
            self.note(
                "13",
                "warning",
                f"tray {v['tray']} is {v['distance_m']:.3f} m from the outlet of {v['line']} at "
                f"{v['outlet'][2]:.3f} m{' and runs above it' if v['above'] else ''}, under the "
                f"{v['clearance_m']:g} m clearance of layout/layout-checks.yaml (D-047)",
            )
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
            access_clear = _stack_access(items, stack_cfg["tags"], access, solids)
            reasons += access_clear
            # the replacement of each stack by hand (D-047, layout/layout-checks.yaml, review
            # 2026-11-05-layout#1): its far end plate within reach of a person at grade at the
            # frame's long side, and its slide lane at deck level out over that edge clear
            # (each a reason when it fails: a stack that cannot be replaced is not a skid)
            by_tag = {i["tag"]: i for i in items}
            removal_cfg = checks["stack_removal"]
            removals = [
                _stack_removal(solids, by_tag[t], frame["footprint"], deck, removal_cfg, deleted)
                for t in stack_cfg["tags"]
                if t in by_tag
            ]
            for r in removals:
                if not r["reach_ok"]:
                    reasons.append(
                        f"stack removal: the far end plate of {r['tag']} is {r['reach_m']:.3f} m from the "
                        f"standing position at the frame's {r['side']} side, beyond the {r['reach_limit_m']:g} m reach"
                    )
                if r["lane_blocked_by"]:
                    reasons.append(
                        f"stack removal: {', '.join(r['lane_blocked_by'])} in the slide lane of {r['tag']} "
                        f"to the frame's {r['side']} side"
                    )
            # the ignition sources against the hazardous zones (D-047, review #2, #3): the
            # sphere's radius plus the margin to every source item's outline
            ignition = _ignition_clearance(model, checks["ignition_sources"], {i["tag"] for i in items})
            for g in ignition:
                if not g["ok"]:
                    self.note(
                        "13",
                        "error",
                        f"Skid {key}: ignition source {g['tag']} ({g['kind']}) is {g['clearance_m']:.3f} m from "
                        f"the outline of zone source {g['nearest_source']} ({g['zone']}), under the "
                        f"{g['required_m']:.3f} m of its sphere radius plus the margin",
                    )
            # the ignition and hot sources against the feet of the frame's stairs, where the
            # ways off the deck land (D-057, review 2026-11-05-layout-r2#3)
            stair_feet = _stair_foot_clearance(
                model, checks["stair_feet"], skid["frame"], {i["tag"] for i in items}
            )
            for g in stair_feet:
                if not g["ok"]:
                    self.note(
                        "13",
                        "error",
                        f"Skid {key}: ignition or hot source {g['tag']} ({g['kind']}) is {g['clearance_m']:.3f} m "
                        f"in plan from the foot of stair {g['stair']}, under the {g['required_m']:g} m of "
                        f"layout/layout-checks.yaml stair_feet",
                    )
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
            # the cable trays over the frame (step 24, D-045): those above the envelope are
            # site-fitted like the vent risers (reported, not counted); a level run under the
            # walkway headroom over the deck is reported (core checks pipes against it, not trays)
            trays = _core.model_trays_over(model, frame["footprint"])
            trays_above = sorted(
                ({"id": t["id"], "system": t["system"], "top_m": round(t["top_m"], 3)} for t in trays if t["top_m"] > limit + tol),
                key=lambda t: t["id"],
            )
            trays_low = sorted(
                (
                    {"id": t["id"], "level_low_m": round(t["level_low_m"], 3)}
                    for t in trays
                    if t["level_low_m"] is not None and t["level_low_m"] < deck + TRAY_HEADROOM_M - tol
                ),
                key=lambda t: t["id"],
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
                "stack_removal": removals,
                "ignition_clearance": ignition,
                "stair_foot_clearance": stair_feet,
                "pipes_above_envelope": [{"id": p["id"], "line": p["line"], "top_m": p["top_m"]} for p in pipes],
                "trays_above_envelope": trays_above,
                "trays_under_headroom": trays_low,
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
            if removals:
                worst = max(removals, key=lambda d: d["reach_m"])
                print(
                    f"[13] Skid {key}: stack removal from the {worst['side']} side, reach at most "
                    f"{worst['reach_m']:.3f} m ({worst['tag']}, limit {worst['reach_limit_m']:g} m), slide lanes "
                    f"{'clear' if not any(d['lane_blocked_by'] for d in removals) else 'blocked'}"
                )
            if ignition:
                tight = min(ignition, key=lambda g: g["clearance_m"] - g["required_m"])
                print(
                    f"[13] Skid {key}: ignition sources {', '.join(g['tag'] for g in ignition)}: least clearance "
                    f"{tight['clearance_m']:.3f} m ({tight['tag']} to {tight['nearest_source']}, "
                    f"{tight['required_m']:.3f} m required)"
                )
            if stair_feet:
                tight = min(stair_feet, key=lambda g: g["clearance_m"])
                print(
                    f"[13] Skid {key}: ignition and hot sources to the stair feet: least "
                    f"{tight['clearance_m']:.3f} m ({tight['tag']} to {tight['stair']}, "
                    f"{tight['required_m']:g} m required)"
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
            if trays_above:
                self.note(
                    "13",
                    "info",
                    f"Skid {key}: {len(trays_above)} cable tray(s) over the frame above the {limit:.3f} m "
                    f"envelope, site-fitted, not counted (D-045): up to "
                    f"{max(t['top_m'] for t in trays_above):.3f} m",
                )
            for t in trays_low:
                self.note(
                    "13",
                    "info",
                    f"Skid {key}: tray {t['id']} runs level at {t['level_low_m']:.3f} m over the frame, "
                    f"under the {TRAY_HEADROOM_M:g} m walkway headroom over the {deck:g} m deck (the deck is stepped onto, not a walkway, D-019)",
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
        # the review records' own bookkeeping (cheme.review-*) is not a result of this run, and
        # it depends on git: without history (a --scratch or --check copy) core orders records of
        # one date by file name, so the scenario record would differ between the folder and a copy
        problems = [
            f
            for f in validate
            if f.get("level") in ("error", "warning")
            and f.get("id") not in accepted
            and not str(f.get("rule") or "").startswith("cheme.review-")
        ]
        for f in problems:
            self.note(
                "13", f["level"], f"{f.get('file')}:{f.get('line')} {f.get('rule')}: {f.get('message')}"
            )
        self.summary["envelope"] = {"basis": env, "skids": result, "vent_tray_clearance": vents}
        print(f"[13] vent outlets: {len(vents)} tray(s) within the clearance of layout/layout-checks.yaml")
        print(
            f"[13] validate: {len(problems)} error/warning finding(s) not accepted in "
            "checks/checks.yaml"
        )

    # -- 21 ---------------------------------------------------------------------------------
    def weights(self) -> None:
        """Step 21 (before step 10, numbered after the existing steps): every listed item's
        empty weight from layout/lifting-basis.yaml into the equipment list's
        dimensions.weight (a targeted edit of the value; the key is written by hand once), so
        the model and core's lifting study carry it. The tanks' weights follow their sizes."""
        basis = self.load(_lifting.BASIS)
        equipment = self.load("equipment/equipment-list.yaml")["equipment"]
        try:
            weights = _lifting.item_weights(equipment, basis)
        except _lifting.BasisError as exc:
            raise Refused(str(exc)) from exc
        changes = []
        for item in equipment:
            dims = item.get("dimensions") or {}
            if "weight" not in dims:
                raise Refused(
                    f"equipment/equipment-list.yaml: {item['tag']} has no dimensions.weight: "
                    "add the key once (step 21 keeps its value)"
                )
            want = weights[item["tag"]]["weight_t"]
            if not _same(dims["weight"], want):
                changes.append((["equipment", ("tag", item["tag"]), "dimensions", "weight"], want))
        self.edit("equipment/equipment-list.yaml", changes)
        self.summary["weights"] = weights
        print(f"[21] item weights from {_lifting.BASIS}: {len(changes)} written into the equipment list")

    # -- 22 ---------------------------------------------------------------------------------
    def take_off(self) -> None:
        """Step 22: `cheme assess mto --write` of the model as built (estimate/mto.csv, .md)."""
        report = _core.take_off(self.root, write=True)
        for f in report.get("findings") or []:
            self.note("22", "warning", f"{f.get('rule')}: {f.get('message')}")
        self.summary["take_off"] = report
        totals = ", ".join(
            f"{cat} {_num(round(q, 3))} {unit}"
            for cat, units in report["totals"].items()
            for unit, q in units.items()
        )
        print(f"[22] cheme assess mto --write: {totals}")

    # -- 23 ---------------------------------------------------------------------------------
    def lifting(self) -> None:
        """Step 23: core's lifting study (`cheme layout lifting --write`: every listed item of
        heavy_lift_t or more) and the unit lifts it cannot express (scripts/_lifting.py: the
        skids as 20 ft units, T-101 drained and full) into layout/lifting-study-units.csv/.md."""
        study = _core.lifting_study(self.root, write=True)
        for f in study.get("findings") or []:
            self.note("23", "warning", f"{f.get('rule')}: {f.get('message')}")
        basis = self.load(_lifting.BASIS)
        densities: dict[str, float] = {}
        duties = {d["id"]: d for d in self.load("process/duties.yaml")["duties"]}
        stacks = self.summary["stacks"]
        for entry in basis.get("contents") or []:
            kind, ref = entry["density_from"].split(" ", 1)
            if kind == "pump":
                rho = next(
                    (
                        e["values"].get("density_kg_m3")
                        for st in stacks.values()
                        for e in st["equipment"]
                        if e["tag"] == ref
                    ),
                    None,
                )
            else:
                did = ref.split()[0]
                q = duties[did]["dosing"]["density"]
                rho = float(q["value"]) * (1000.0 if q["unit"] in ("kg/L", "g/mL") else 1.0)
            if rho is None:
                raise Refused(f"{_lifting.BASIS}: no density for {entry['tag']} ({entry['density_from']})")
            densities[entry["tag"]] = float(rho)
        model = _core.plant_model(self.root)
        try:
            result = _lifting.unit_study(
                model, basis, study["criteria"], self.summary["take_off"], densities
            )
        except _lifting.BasisError as exc:
            raise Refused(str(exc)) from exc
        for message in result["findings"]:
            self.note("23", "warning", message)
        for row in result["rows"]:
            permitted = "not permitted" not in row["status"]
            if permitted and ("blocked" in row["status"] or "no " in row["status"]):
                self.note("23", "warning", f"unit lift {row['id']} ({row['weight_t']} t): {row['status']}")
        (self.root / _lifting.UNITS_CSV).write_text(_lifting.study_csv(result), encoding="utf-8")
        (self.root / _lifting.UNITS_MD).write_text(
            _lifting.study_markdown(
                result, basis, self.summary["weights"], study["criteria"], study["model_sha256"], self.h
            ),
            encoding="utf-8",
        )
        self.summary["lifting"] = {
            "heavy_lift_t": float(study["criteria"]["heavy_lift_t"]["value"]),
            "carry_limit_m": (basis.get("units") or {}).get("carry_limit_m"),
            "core_lifts": [
                {k: lift.get(k) for k in ("tag", "weight_t", "pad", "required_t", "status")}
                for lift in study["lifts"]
            ],
            "unit_lifts": _lifting.summary(result),
        }
        rows = {r["id"]: r for r in result["rows"]}
        print(
            f"[23] cheme layout lifting --write: {len(study['lifts'])} heavy item(s); unit lifts: "
            + "; ".join(f"{k} {r['weight_t']} t {r['status']}" for k, r in rows.items())
        )

    # -- 24 ---------------------------------------------------------------------------------
    def cables(self) -> None:
        """Step 24: `cheme layout cables --write` of the model as built (electrical/
        cable-schedule.csv, .md); its summary into the record (D-045)."""
        report = _core.cable_schedule(self.root, write=True)
        cabling = report["cabling"]
        cables = report["cables"]
        by_room: dict[str, int] = {}
        for c in cables:
            by_room[c["from"]] = by_room.get(c["from"], 0) + 1
        dc = [c for c in cables if c["system"] == "power" and float(c["voltage_v"] or 0) <= 120]
        risers = self.dc_risers(dc)
        review = sorted(c["tag"] for c in cables if c.get("review_needed"))
        for m in cabling.get("missing") or []:
            self.note("24", "warning", f"no cable: {m['tag']} ({m['kind']}): {m['reason']}")
        for tag in review:
            self.note("24", "warning", f"cable {tag} review_needed")
        self.summary["cabling"] = {
            "cables": cabling["cables"],
            "power": cabling["power"],
            "instrument": cabling["instrument"],
            "dc_48v": len(dc),
            "motors": cabling["motors"],
            "instruments": cabling["instruments"],
            "junction_boxes": cabling["junction_boxes"],
            "trays": cabling["trays"],
            "tray_length_m": cabling["tray_length_m"],
            "cable_length_m": cabling["cable_length_m"],
            "dc_cable_length_m": sum(int(c["length_m"]) for c in dc),
            # the riser from the rectifier's cabinet top to each DC output's point, which core
            # neither models nor counts (D-045): per cable, m, and the route with it
            "dc_riser_m": risers,
            "dc_route_with_riser_m": {
                c["tag"]: round(float(c["route_length_m"]) + risers[c["tag"]], 3) for c in dc
            },
            "missing": cabling.get("missing") or [],
            "review_needed": review,
        }
        print(
            f"[24] cheme layout cables --write: {cabling['cables']} cables ({cabling['power']} power, "
            f"{len(dc)} of them 48 V DC, {cabling['instrument']} instrument), {cabling['trays']} trays "
            f"{cabling['tray_length_m']:g} m, cable {cabling['cable_length_m']:g} m, "
            f"{len(cabling.get('missing') or [])} without a cable; DC risers not modelled "
            f"{sum(risers.values()):.2f} m"
        )

    def dc_risers(self, dc: list[dict]) -> dict[str, float]:
        """Per DC cable: the length of the riser that is not modelled, from its rectifier's
        cabinet top (U-x01's model bbox) to its DC output's room point: the plan distance from
        the cabinet's top face plus the rise (electrical/electrical-list.yaml, D-045)."""
        rooms = {r["id"]: r for r in self.load("electrical/electrical-list.yaml")["rooms"]}
        boxes = {e["tag"]: e["bbox"] for e in _core.plant_model(self.root).get("equipment") or []}
        out = {}
        for c in dc:
            room = rooms[c["from"]]
            x0, y0, _, x1, y1, top = (float(v) for v in boxes["U-" + c["from"][3:6]])
            x, y, z = (float(v) for v in room["point"])
            plan = math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1))
            out[c["tag"]] = round(plan + max(z - top, 0.0), 3)
        return out

    # -- 25 ---------------------------------------------------------------------------------
    def layout_results(self) -> None:
        """Step 25 (after step 13): the 3D results of the model as built, for the record at
        every duration (at 10,000 h those of the infeasible Skid A: reported, never fatal).
        From `cheme layout report --json`: the process lines of DN 25 and above routed, skipped
        with their reason or unrouted, the smaller lines by status and the route methods; from
        step 13's validate, the clashes (accepted in checks/checks.yaml or not); per skid, the
        items' top against the envelope. The lifts are step 23's (the record's lifting)."""
        report = _core.layout_report(self.root)
        dn = {
            line["number"]: _dn(line.get("nominal_diameter"))
            for line in self.load("piping/line-list.yaml")["lines"]
        }
        big, small = [], {}
        for line in report["lines"]:
            size = dn.get(line["line"])
            if size is not None and size >= ROUTED_DN:
                big.append(line)
            else:
                small[line["status"]] = small.get(line["status"], 0) + 1
        routed = sorted(line["line"] for line in big if line["status"] == "routed")
        skipped = {
            line["line"]: sorted({u["reason"] for u in line["unrouted"]})
            for line in big
            if line["status"] == "skipped"
        }
        unrouted = {
            line["line"]: sorted({u["reason"] for u in line["unrouted"]})
            for line in big
            if line["status"] not in ("routed", "skipped")
        }
        for lid, why in unrouted.items():
            self.note("25", "warning", f"line {lid} (DN {dn[lid]}) is not routed: {'; '.join(why)}")
        methods = dict(sorted(report["methods"].items()))
        if methods.get("direct"):
            self.note("25", "warning", f"{methods['direct']} segment(s) fell back to a direct route")
        clashes = sorted(
            (
                {
                    "rule": f["rule"],
                    "level": f["level"],
                    "message": f["message"],
                    "accepted": f.get("accepted") or None,
                }
                for f in self.validate_findings
                if str(f.get("rule", "")).startswith("cheme.layout-clash")
            ),
            key=lambda c: (c["rule"], c["message"]),
        )
        open_clashes = [c for c in clashes if not c["accepted"]]
        heights = {
            key: {
                "items_top_m": e["items_top_m"],
                "envelope_top_m": e["envelope_top_m"],
                "above_envelope_m": max(0.0, e["items_top_m"] - e["envelope_top_m"]),
                "envelope_feasible": e["feasible"],
            }
            for key, e in self.summary["envelope"]["skids"].items()
        }
        self.summary["layout"] = {
            "routed_dn_min": ROUTED_DN,
            "lines": {
                "listed": len(big),
                "routed": routed,
                "skipped": skipped,
                "unrouted": unrouted,
                "smaller_by_status": dict(sorted(small.items())),
            },
            "methods": methods,
            "clashes": clashes,
            "clashes_open": len(open_clashes),
            "model_findings": dict(sorted(report["findings"].items())),
            "sources": dict(sorted(report["sources"].items())),
            "height": heights,
            # the cable trays within the clearance of a vent or flue outlet (step 13, D-047)
            "vent_tray_clearance": self.summary["envelope"].get("vent_tray_clearance", []),
        }
        print(
            f"[25] lines of DN {ROUTED_DN} and above: {len(routed)} of {len(big)} routed, "
            f"{len(skipped)} skipped, {len(unrouted)} unrouted (smaller: "
            + ", ".join(f"{n} {s}" for s, n in sorted(small.items()))
            + f"); methods {methods}; {len(clashes)} clash finding(s), {len(open_clashes)} not "
            "accepted; "
            + "; ".join(
                f"Skid {k} top {h['items_top_m']:.3f} m (envelope {h['envelope_top_m']:.3f} m)"
                for k, h in heights.items()
            )
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
            "stack_removal": env["stack_removal"],
            "ignition_clearance": env["ignition_clearance"],
            "stair_foot_clearance": env["stair_foot_clearance"],
            "invariants": s["invariants"][key],
            "duty_result": final["duty"],
        }
        reservoir_cfg = stacks_cfg["equipment"]["reservoir"]
        # the inputs of the resize report's calculated causes (step 17)
        basis = {
            "reservoir_margin": margin,
            "reservoir_aspect_ratio": float(reservoir_cfg["aspect_ratio"]["value"]),
            "usable_height_m": s["envelope"]["basis"]["usable_height"],
            "threshold_ph": self.trip_ph(),
            "stability_ph": float(self.basis()["threshold"]["ph"]),
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
            # steps 22 and 23: the take-off's totals and the lifts (core's heavy items and the
            # unit lifts of layout/lifting-study-units.md), reported at every duration
            "take_off": {"totals": s["take_off"]["totals"], "findings": len(s["take_off"].get("findings") or [])},
            "lifting": s["lifting"],
            # step 24: the cable schedule's summary (D-045)
            "cabling": s["cabling"],
            # step 25: the routed lines, clashes and heights of the model as built
            "layout": s["layout"],
            "findings":[f for f in self.findings if f["level"] in ("error", "warning")],
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
            stale = self.root / _lca.SCENARIO_LCA.format(h=f"{self.h:g}")
            if stale.exists():
                stale.unlink()
                print(f"[20] {stale.relative_to(self.root)} removed: it described an earlier design")
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
            if not s["densities_plausible"]:
                bad = [f"{r['quantity']} {r['kg_l']:.4g} kg/L" for r in s["densities"] if not r["ok"]]
                self.note("20", "error", f"Skid {key}: mass over the duty's volume outside {_lca.DENSITY_BAND_KG_L} kg/L: {', '.join(bad)}")
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

    def lca_errors(self) -> list[dict]:
        """The step 20 errors: each fails the run (exit 4) and --check."""
        return [f for f in self.findings if f["step"] == "20" and f["level"] == "error"]

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
        self.weights()
        self.layout_and_datasheets()
        self.control()
        self.duty_plots()
        # steps 22 and 23 before step 13: its validate then reads the take-off and the lifting
        # study of the model as built (cheme.layout-lifting-study-outdated otherwise)
        self.take_off()
        self.lifting()
        self.cables()
        self.envelope_check()
        self.layout_results()
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


def _dn(text) -> int | None:
    """A line list nominal diameter ("DN25") as a number, None when it has none."""
    s = str(text or "").strip().upper()
    return int(s[2:]) if s.startswith("DN") and s[2:].isdigit() else None


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


def _stack_access(
    items: list[dict], tags: list[str], access: dict[str, float], parts: list[dict] | None = None
) -> list[str]:
    """The clear space at the ends (along the stack axis, the item's own x) and sides of each
    stack (process/cells.yaml stacks[].access) against the bodies of the other items on the
    frame and their generated parts (*parts*: the model's solids), at the stack's height; beyond
    the frame is the access aisle at grade."""
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
                # the generated parts of the other items too (a transmitter stand, D-040)
                for s in parts or []:
                    if s["owner"] == tag or s["owner"] not in by_tag:
                        continue
                    p, z = s["plan"], s["z"]
                    tol = 1e-6
                    if (
                        p[0] < ax1 - tol and p[2] > ax0 + tol and p[1] < ay1 - tol and p[3] > ay0 + tol
                        and z[0] < z1 - tol and z[1] > z0 + tol
                    ):  # fmt: skip
                        problems.append(
                            f"stack access: {s['id']} stands in the {clear:g} m {kind} access of {tag}"
                        )
    return sorted(set(problems))


def _deleted(solid: dict, patterns: list[str]) -> bool:
    """Whether a model solid is steel core draws that the design deletes (D-047)."""
    return any(fnmatch.fnmatchcase(solid["id"], p) for p in patterns)


def _stack_removal(
    solids: list[dict], stack: dict, frame: list[float], deck: float, cfg: dict, deleted: list[str]
) -> dict:
    """The replacement of one stack by hand (D-047, layout/layout-checks.yaml stack_removal):
    the person stands at grade at the frame's long side (``side``), the standing position
    ``ankle_m`` behind its edge; the stack's far face (its connection end plate) must be within
    ``reach_m`` of it. The stack, its connections undone, slides out over that edge at deck level
    onto a deck-height trolley: its lane, as wide as the stack, from the stack to
    ``lane_beyond_edge_m`` beyond the edge and from the deck to the stack's top plus
    ``lane_clearance_m``, must hold no solid but the stack's own parts and the deleted steel
    (the deck rail core draws, D-047)."""
    x0, y0, z0, x1, y1, z1 = stack["bbox"]
    side = cfg.get("side", "south")
    fx0, fy0, fx1, fy1 = frame
    beyond = float(cfg.get("lane_beyond_edge_m", 0.3))
    if side == "south":
        far, near = y1 - fy0, y0 - fy0
        lane = (x0, fy0 - beyond, x1, y0)
    elif side == "north":
        far, near = fy1 - y0, fy1 - y1
        lane = (x0, y1, x1, fy1 + beyond)
    else:
        raise ValueError(f"{LAYOUT_CHECKS}: stack_removal side {side!r} (south or north)")
    reach = far + float(cfg["ankle_m"])
    top = z1 + float(cfg.get("lane_clearance_m", 0.0))
    tol = 1e-6
    own = stack["tag"]

    def meets(plan, box):
        return plan[0] < box[2] - tol and plan[2] > box[0] + tol and plan[1] < box[3] - tol and plan[3] > box[1] + tol

    blockers = sorted(
        {
            s["id"] if s["owner"].startswith(("SKID-", "PR-")) else s["owner"]
            for s in solids
            if s["owner"] != own
            and not s["owner"].startswith(f"{own}/")
            and not _deleted(s, deleted)
            and meets(s["plan"], lane)
            and s["z"][1] > deck + tol
            and s["z"][0] < top - tol
        }
    )
    return {
        "tag": own,
        "side": side,
        "near_face_from_edge_m": round(near, 3),
        "far_face_from_edge_m": round(far, 3),
        "reach_m": round(reach, 3),
        "reach_limit_m": float(cfg["reach_m"]),
        "reach_ok": reach <= float(cfg["reach_m"]) + tol,
        "lane_top_m": round(top, 3),
        "lane_blocked_by": blockers,
    }


def _box_gap(a: list[float], b: list[float]) -> float:
    """The shortest distance between two axis-aligned boxes [x0, y0, z0, x1, y1, z1] (0 when
    they touch or overlap)."""
    d = [max(a[k] - b[k + 3], b[k] - a[k + 3], 0.0) for k in range(3)]
    return math.sqrt(sum(v * v for v in d))


def _outline(item: dict) -> list[float]:
    """A zone source item's outline for the ignition check: its body box joined with the points
    of its nozzles, whose flanges stand outside the box (review 2026-11-05-layout-r2#1, D-057)."""
    box = [float(v) for v in item["bbox"]]
    for n in item.get("nozzles") or []:
        p = [float(v) for v in n["point"]]
        box = [min(box[k], p[k]) for k in range(3)] + [max(box[k + 3], p[k]) for k in range(3)]
    return box


def _in_train(tag: str, on_frame: set[str]) -> bool:
    """Whether *tag* is on this frame or belongs to the frame's train standing off it (the
    third character of the tag is the train digit: X-132 and U-101 of Skid A's 1xx)."""
    trains = {t[2] for t in on_frame if len(t) > 2}
    return tag in on_frame or (len(tag) > 2 and tag[2] in trains)


def _source_box(entry: dict, equipment: dict) -> list[float] | None:
    """An ignition or hot source's box: the model item of its tag, or the outline its entry
    declares (``box``, a vendor part the model does not hold, D-065); None when neither."""
    if entry.get("box"):
        return [float(v) for v in entry["box"]]
    item = equipment.get(entry["tag"])
    return [float(v) for v in item["bbox"]] if item else None


def _ignition_clearance(model: dict, cfg: dict, on_frame: set[str]) -> list[dict]:
    """Per ignition source of layout/layout-checks.yaml on this frame or standing beside it
    (the items of *on_frame*, or a tag of the frame's train standing off it): the least
    clearance from its outline (a model item's box, or the entry's declared ``box``) to the
    outline of any source item of a hazardous zone, its body box joined with its nozzle points
    (to the point of a nozzle source), against that sphere's radius plus ``margin_m`` (D-047,
    D-057, D-065)."""
    equipment = {e["tag"]: e for e in model.get("equipment") or []}
    nozzles = {n["id"]: n for e in equipment.values() for n in e.get("nozzles") or []}
    margin = float(cfg.get("margin_m", 0.0))
    found = []
    for entry in cfg.get("items") or []:
        tag = entry["tag"]
        box = _source_box(entry, equipment)
        if box is None or not _in_train(tag, on_frame):
            continue
        best = None
        for zone in model.get("zones") or []:
            if zone.get("kind") != "hazardous":
                continue
            for v in zone.get("volumes") or []:
                if v.get("shape") != "sphere" or (v.get("item") is not None and v.get("item") == tag):
                    continue
                # an explicit sphere (a declared release point, the reserved vent outlets of
                # D-068) counts by its centre, under the zone's id
                src = v.get("item") or zone["id"]
                if src in equipment:
                    other = _outline(equipment[src])
                elif src in nozzles:
                    p = [float(x) for x in nozzles[src]["point"]]
                    other = p + p
                else:
                    c = [float(x) for x in v["centre"]]
                    other = c + c
                gap = _box_gap(box, other)
                need = float(v["radius"]) + margin
                if best is None or gap - need < best["clearance_m"] - best["required_m"]:
                    best = {
                        "tag": tag,
                        "kind": entry.get("kind", ""),
                        "zone": zone["id"],
                        "nearest_source": src,
                        "clearance_m": round(gap, 3),
                        "required_m": round(need, 3),
                    }
        if best is not None:
            best["ok"] = best["clearance_m"] >= best["required_m"] - 1e-6
            found.append(best)
    return found


def _stair_feet(model: dict, structure_id: str) -> list[dict]:
    """The feet of the stairs from grade of one structure: per stair the plan box of its base
    landing at grade (core's ``<stair>/landing-base``), else the stair's own plan box."""
    entry = next((s for s in model.get("structures") or [] if s.get("id") == structure_id), None)
    feet = []
    for stair in (entry or {}).get("stairs") or []:
        if stair.get("from") != "grade":
            continue
        base = next((p for p in stair.get("parts") or [] if str(p.get("id", "")).endswith("/landing-base")), None)
        plan = _core._part_plan(base) if base else None
        if plan is None:
            b = [float(v) for v in stair["box"]]
            plan = [b[0], b[1], b[3], b[4]]
        feet.append({"id": stair["id"], "plan": [round(float(v), 3) for v in plan]})
    return feet


def _stair_foot_clearance(model: dict, cfg: dict, structure_id: str, on_frame: set[str]) -> list[dict]:
    """Per ignition or hot source of layout/layout-checks.yaml on this frame or standing beside
    it (as _ignition_clearance): the least plan distance from its outline to the foot of any
    stair of the frame from grade, where the ways off the deck land, against ``clearance_m``
    (review 2026-11-05-layout-r2#3, D-057; a declared ``box`` for a vendor part the model does
    not hold, review 2026-11-06-layout-r3#1, D-065)."""
    equipment = {e["tag"]: e for e in model.get("equipment") or []}
    clearance = float(cfg["clearance_m"])
    feet = _stair_feet(model, structure_id)
    found = []
    for entry in cfg.get("items") or []:
        tag = entry["tag"]
        b = _source_box(entry, equipment)
        if b is None or not _in_train(tag, on_frame) or not feet:
            continue
        best = None
        for foot in feet:
            p = foot["plan"]
            gap = math.hypot(max(p[0] - b[3], b[0] - p[2], 0.0), max(p[1] - b[4], b[1] - p[3], 0.0))
            if best is None or gap < best["clearance_m"]:
                best = {"tag": tag, "kind": entry.get("kind", ""), "stair": foot["id"], "foot_plan": p,
                        "clearance_m": round(gap, 3), "required_m": clearance}
        best["ok"] = best["clearance_m"] >= clearance - 1e-6
        found.append(best)
    return found


def _segment_point_distance(a, b, p) -> tuple[float, list[float]]:
    """The distance from point *p* to segment *ab* (3D) and the nearest point on it."""
    ab = [b[k] - a[k] for k in range(3)]
    ap = [p[k] - a[k] for k in range(3)]
    ll = sum(v * v for v in ab)
    t = 0.0 if ll < 1e-12 else max(0.0, min(1.0, sum(ab[k] * ap[k] for k in range(3)) / ll))
    q = [a[k] + t * ab[k] for k in range(3)]
    return math.dist(q, p), q


def _vent_tray_clearance(model: dict, cfg: dict) -> list[dict]:
    """Every cable tray within ``clearance_m`` of the open end of a vent or flue line of
    layout/layout-checks.yaml, or above that outlet within ``clearance_m`` in plan (its plume;
    D-047, review 2026-11-05-layout#5). A tray is its centreline at mid-depth less half its
    larger cross dimension."""
    patterns = cfg.get("lines") or []
    clearance = float(cfg["clearance_m"])
    outlets = []
    for pipe in model.get("pipes") or []:
        if not any(fnmatch.fnmatchcase(pipe.get("line", ""), p) for p in patterns):
            continue
        if "end" not in (pipe.get("open_ends") or []):
            continue
        outlets.append((pipe["line"], [float(v) for v in pipe["points"][-1]]))
    # outlets declared by point, of lines the model does not route (the reserved vent outlets
    # of the cathode relief and the condensate collection, D-068)
    for entry in cfg.get("outlets") or []:
        outlets.append((str(entry["id"]), [float(v) for v in entry["point"]]))
    found = []
    for tray in model.get("trays") or []:
        half = max(float(tray.get("width") or 0.0), float(tray.get("depth") or 0.0)) / 2
        lift = float(tray.get("depth") or 0.0) / 2
        pts = [[float(p[0]), float(p[1]), float(p[2]) + lift] for p in tray.get("points") or []]
        for line, outlet in outlets:
            best, above = None, False
            for a, b in zip(pts, pts[1:]):
                d, q = _segment_point_distance(a, b, outlet)
                d = max(d - half, 0.0)
                best = d if best is None else min(best, d)
                # above the outlet within the clearance in plan: sample the run
                n = max(1, int(math.dist(a, b) / 0.05))
                for k in range(n + 1):
                    x = [a[j] + (b[j] - a[j]) * k / n for j in range(3)]
                    if x[2] - lift > outlet[2] and math.hypot(x[0] - outlet[0], x[1] - outlet[1]) < clearance + half:
                        above = True
            if best is not None and (best < clearance - 1e-6 or above):
                found.append(
                    {"tray": tray["id"], "line": line, "outlet": outlet, "distance_m": round(best, 3),
                     "above": above, "clearance_m": clearance}
                )
    return sorted(found, key=lambda v: (v["line"], v["tray"]))


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
    failed: list[str] = []
    records: dict[float, dict] = {}
    uncertainty: dict[float, dict] = {}
    lca_docs: dict[float, dict] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for h in durations:
            scratch = Path(tmp) / f"{h:g}h" / root.name
            shutil.copytree(root, scratch, ignore=COPY_IGNORE)
            with_unc = (root / UNCERTAINTY.format(h=f"{h:g}")).exists()
            print(f"[check] regenerating {h:g} h{' with --uncertainty' if with_unc else ''}")
            # the scratch run must write the LCA record itself: a copied one would compare clean
            copied = scratch / _lca.SCENARIO_LCA.format(h=f"{h:g}")
            if copied.exists():
                copied.unlink()
            run = Run(scratch, h, uncertainty=with_unc)
            run.run()
            for finding in run.lca_errors():
                failed.append(f"{h:g} h step 20: {finding['message']}")
            if not copied.exists():
                failed.append(f"{h:g} h: step 20 wrote no {_lca.SCENARIO_LCA.format(h=f'{h:g}')}")
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
            if copied.exists():
                lca_docs[h] = json.loads(copied.read_text(encoding="utf-8"))
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
    for message in failed:
        print(f"[check] failed: {message}")
    if not differ and not failed:
        print("[check] clean")
        return 0
    print(f"[check] {len(differ)} file(s) differ, {len(failed)} step 20 failure(s)")
    return 3


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
    lca_errors = run.lca_errors()
    if lca_errors:
        for finding in lca_errors:
            print(f"regen: step 20 failed: {finding['message']}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
