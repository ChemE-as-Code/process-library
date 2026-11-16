"""Compare recorded solver states under explicitly checked matching engineering inputs."""

import json


def compare(a, b, rtol, atol):
    import numpy as np

    r1 = json.loads((a / "result.json").read_text(encoding="utf-8"))
    r2 = json.loads((b / "result.json").read_text(encoding="utf-8"))
    if any(r["status"] != "completed" for r in (r1, r2)):
        raise ValueError("Only completed runs with passing basic checks can be compared")
    inputs = [json.loads((p / "inputs.json").read_text(encoding="utf-8")) for p in (a, b)]
    engineering = ("influent", "reactor_volumes_m3", "recycles", "aeration", "clarifier")
    if any(inputs[0][key] != inputs[1][key] for key in engineering):
        raise ValueError("Engineering conditions differ")
    if inputs[0]["solver"]["days"] != inputs[1]["solver"]["days"]:
        raise ValueError("Simulation horizons differ")
    if (a / "source/system.py").read_bytes() != (b / "source/system.py").read_bytes():
        raise ValueError("Upstream model source differs")
    if (a / "solver_state_headers.json").read_bytes() != (
        b / "solver_state_headers.json"
    ).read_bytes():
        raise ValueError("Solver state ordering differs")
    x1 = np.load(a / "solver_states.npz")["states"][:, -1]
    x2 = np.load(b / "solver_states.npz")["states"][:, -1]
    thresholds = atol + rtol * np.maximum(np.abs(x1), np.abs(x2))
    normalized = np.abs(x1 - x2) / thresholds
    return {
        "left_run": a.name,
        "right_run": b.name,
        "relative_tolerance": rtol,
        "absolute_tolerance_native_state_units": atol,
        "all_final_solver_states_pass": bool(np.all(normalized <= 1)),
        "max_normalized_final_state_difference": float(normalized.max()),
        "effluent_comparison": {
            k: {
                "left": v,
                "right": r2["effluent"][k],
                "difference": r2["effluent"][k] - v,
                "pass": bool(
                    abs(r2["effluent"][k] - v) <= atol + rtol * max(abs(v), abs(r2["effluent"][k]))
                ),
            }
            for k, v in r1["effluent"].items()
        },
    }
