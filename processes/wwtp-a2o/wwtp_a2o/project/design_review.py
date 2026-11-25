"""Link the activated-sludge review to the evidence of one published A2/O run."""

import json
import math
from hashlib import sha256
from pathlib import Path

from wwtp_a2o.project.artifacts import write_json

ZONES = {
    "A1": "anaerobic",
    "A2": "anaerobic",
    "A3": "anoxic",
    "A4": "anoxic",
    "O1": "aerobic",
    "O2": "aerobic",
    "O3": "aerobic",
}
DESIGN_STREAMS = ("INFLUENT", "EFFLUENT", "WAS", "RAS", "TO_CLARIFIER")


def design_snapshot(data, calculation, run_id):
    """Take dimensions and final values from the same model and accepted state."""
    rows = {row["stream"]: row for row in calculation.streams}
    tanks = []
    for reactor in calculation.reactors:
        tank = reactor["reactor"]
        stream = "TO_CLARIFIER" if tank == "O3" else f"{tank}_OUT"
        tanks.append(
            {
                "id": tank,
                "zone": ZONES[tank],
                "volume_m3": reactor["volume_m3"],
                "mlss_mg_L": rows[stream]["TSS"],
                "sample_stream": stream,
            }
        )
    clarifier = data["clarifier"]
    count = clarifier["N_layer"]
    # The solver archive stores time in a separate array, but the header includes it.
    headers = [field for field in calculation.headers if field != ["-", "t [d]"]]
    states = calculation.states[:, -1]
    layers = {}
    if len(headers) == len(states):
        layers = {
            label: float(value)
            for (unit, label), value in zip(headers, states, strict=True)
            if unit == "C1"
        }
    profile = [layers.get(f"TSS{i + 1} [mg/L]") for i in range(count)]
    complete = all(value is not None and math.isfinite(value) and value >= 0 for value in profile)
    return {
        "case": data["case_id"],
        "run_id": run_id,
        "day": float(calculation.time_days[-1]),
        "tanks": tanks,
        "clarifier": {
            "unit_id": "C1",
            "area_m2": clarifier["surface_area"],
            "height_m": clarifier["height"],
            "n_layers": count,
            "layer_tss_mg_L": profile if complete else None,
        },
        "streams": {
            name: {"flow_m3_d": rows[name]["flow"], "tss_mg_L": rows[name]["TSS"]}
            for name in DESIGN_STREAMS
        },
        "sources": {
            "geometry": "This run's reactor volumes in reactors.csv and C1 geometry in inputs.json",
            "mlss": "Final TSS of each listed well-mixed reactor outlet from streams.csv",
            "streams": "Final flow and TSS by stream ID from streams.csv",
            "clarifier_tss": "C1 equal-volume layers, top to bottom, from the final solver state",
            "waterline": "Constant influent and solids wasting from the clarifier underflow",
        },
    }


def save_design_snapshot(evidence: Path, data, calculation, run_id):
    path = evidence / "design-snapshot.json"
    write_json(path, design_snapshot(data, calculation, run_id))
    return sha256(path.read_bytes()).hexdigest()


def project_file(root: Path, relative) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside the A2/O project: {relative}")
    return path


def current_snapshot(root: Path) -> tuple[Path, dict]:
    root = root.resolve()
    entry = json.loads((root / "process/simulation-run.json").read_bytes())["cases"]["baseline"]
    integration = entry["outcome"]["integration"]
    if entry["execution"]["state"] != "completed" or not integration["completed"]:
        raise ValueError("The A2/O case has no completed integration to review")
    digest = entry["verification"].get("design_snapshot_sha256")
    if not digest:
        raise ValueError("This run predates design snapshots; run the updated A2/O worker")
    evidence = project_file(root, entry["evidence"])
    if evidence.parent != (root / "process/simulation-runs").resolve():
        raise ValueError("Expected an A2/O simulation evidence folder")
    for name, expected in entry["inputs"]["fingerprints"].items():
        path = project_file(root, name)
        if not path.is_file() or "sha256:" + sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Run inputs or published stream values changed: {name}; rerun A2/O")
    path = project_file(root, evidence / "design-snapshot.json")
    if path.parent != evidence:
        raise ValueError("The design snapshot must be in this run's evidence folder")
    content = path.read_bytes()
    if sha256(content).hexdigest() != digest:
        raise ValueError("The design snapshot differs from the published run evidence")
    snapshot = json.loads(content)
    if (snapshot["case"], snapshot["run_id"], snapshot["day"]) != (
        entry["case"],
        evidence.name,
        integration["achieved_end"],
    ):
        raise ValueError("The design snapshot does not describe the published A2/O run")
    return path, {
        "case": snapshot["case"],
        "run_id": snapshot["run_id"],
        "day": snapshot["day"],
        "snapshot": path.relative_to(root).as_posix(),
        "model_fingerprint": entry["model_fingerprint"],
        "core_run_tool": entry["tool"],
        "inputs": entry["inputs"],
        "field_sources": snapshot["sources"],
    }
