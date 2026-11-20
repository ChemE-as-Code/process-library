"""Run the constant-influent EXPOsan ASM1 example through the shared QSDsan worker contract."""

import json
import math
import sys
from importlib.metadata import version
from pathlib import Path


def process_streams(system):
    units = {unit.ID: unit for unit in system.units}
    a1, a2, o1, o2, o3, c1 = (units[k] for k in ("A1", "A2", "O1", "O2", "O3", "C1"))
    return {
        "INFLUENT": a1.ins[0],
        "INTERNAL": o3.outs[0],
        "RAS": c1.outs[1],
        "WAS": c1.outs[2],
        "EFFLUENT": c1.outs[0],
        "TO_CLARIFIER": o3.outs[1],
        "A1_OUT": a1.outs[0],
        "A2_OUT": a2.outs[0],
        "O1_OUT": o1.outs[0],
        "O2_OUT": o2.outs[0],
    }


def verify_connections(sheet, streams):
    actual = {}
    boundary = {"EFFLUENT": "EFF", "WAS": "SLUDGE"}
    for key, stream in streams.items():
        source = stream.source.ID if stream.source is not None else "INF"
        sink = stream.sink.ID if stream.sink is not None else boundary[key]
        actual[key] = (source, sink)
    drawn = {
        row["id"]: (row["from"].split(".")[0], row["to"].split(".")[0])
        for row in sheet["streams"]
    }
    if actual != drawn or len(drawn) != len(sheet["streams"]):
        raise ValueError("Flowsheet streams do not match the ASM1 system connections")


def measurements(stream):
    values = {
        "flow": (stream.state[-1], "m3/day"),
        "COD": (stream.COD, "mg COD/L"),
        "TN": (stream.TN, "mg N/L"),
        "TSS": (stream.get_TSS(), "mg TSS/L"),
        "NH4": (stream.state[stream.components.index("S_NH")], "mg N/L"),
    }
    if any(not math.isfinite(v) or v < 0 for v, _ in values.values()):
        raise ValueError(f"Invalid final measurement in {stream.ID}")
    return {key: {"value": float(v), "unit": u} for key, (v, u) in values.items()}


def main(request, response):
    import numpy as np
    import yaml
    from exposan.bsm1 import create_system

    if (request["schema"], request["mode"]) != ("cheme/worker-request/v1", "dynamic"):
        raise ValueError("MLE requires a v1 worker request for dynamic integration")
    config = json.loads(Path(request["input"]).read_bytes())
    versions = {package: version(package) for package in ("qsdsan", "exposan")}
    if any(v != "1.5.3" for v in versions.values()):
        raise ValueError(f"This baseline requires QSDsan and EXPOsan 1.5.3: {versions}")
    if (config["case"], config["model"], config["reactor"]) != (request["case"], "ASM1", "CSTR"):
        raise ValueError("Expected the configured ASM1 stirred-tank case")
    system = create_system(suspended_growth_model=config["model"], reactor_model=config["reactor"])
    streams = process_streams(system)
    verify_connections(yaml.safe_load(Path("process/flowsheet.yaml").read_bytes()), streams)
    days = config["days"]
    system.simulate(
        state_reset_hook="reset_cache", t_span=(0, days), method=config["method"],
        rtol=config["rtol"], atol=config["atol"], max_step=config["max_step"],
    )
    sol = system.scope.sol
    if not sol.success or abs(sol.t[-1] - days) > 1e-8 or not np.isfinite(sol.y).all():
        raise ValueError(f"Integration failed at day {sol.t[-1]}: {sol.message}")
    system.DAE(float(days), sol.y[:, -1].copy())
    system._write_state()
    rows = [{"id": key, "values": measurements(stream)} for key, stream in streams.items()]
    residual = streams["INFLUENT"].state[-1] - streams["EFFLUENT"].state[-1] - streams["WAS"].state[-1]
    if abs(residual) > 1e-5:
        raise ValueError(f"External water balance residual is {residual} m3/day")
    result = {
        "schema": "cheme/adapter-result/v2",
        "case": request["case"],
        "status": "completed",
        "outcome": {
            "mode": "dynamic",
            "convergence": "not-applicable",
            "integration": {
                "start": float(sol.t[0]),
                "requested_end": days,
                "achieved_end": float(sol.t[-1]),
                "time_unit": "day",
                "completed": True,
            },
            "steady_state": {"state": "not-evaluated"},
        },
        "solver": {"name": "QSDsan", "version": versions["qsdsan"], "method": "ASM1 / " + config["method"]},
        "streams": rows, "units": [{"id": u.ID, "status": "simulated"} for u in system.units],
        "verification": {"day": float(sol.t[-1]), "versions": versions, "water_residual_m3_d": float(residual)},
        "messages": ["Constant-influent teaching run completed. ASM1 supplies no TP or PO4 result."],
    }
    encoded = json.dumps(result, indent=2, allow_nan=False)
    (Path(request["evidence"]) / "baseline-result.json").write_text(encoded, encoding="utf-8")
    response.write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    main(json.loads(Path(sys.argv[1]).read_bytes()), Path(sys.argv[2]))
