"""Calculate a structured A2/O result from explicit inputs; no files or console UI."""

import importlib.metadata as md
import sys
import time
from dataclasses import dataclass
from typing import Any

from wwtp_a2o.domains.process.model import REACTORS, connections, validate_inputs
from wwtp_a2o.integrations.qsdsan import build_model, integrate

METRICS = {
    "COD": "mg COD/L",
    "TN": "mg N/L",
    "TP": "mg P/L",
    "TSS": "mg TSS/L",
    "NH4": "mg N/L",
    "PO4": "mg P/L",
    "flow": "m3/day",
}


@dataclass
class Calculation:
    """Accepted solver evidence and derived values, with explicit measurement units."""

    result: dict
    streams: list[dict]
    reactors: list[dict]
    components: list[dict]
    trajectory: list[dict]
    time_days: Any
    states: Any
    headers: list[list[str]]
    component_order: list[str]


class IntegrationStopped(RuntimeError):
    """Carry partial accepted states to the evidence writer on an incomplete solve."""

    def __init__(self, solution, headers):
        super().__init__(f"Integration stopped at day {solution.t[-1]}: {solution.message}")
        self.time_days = solution.t
        self.states = solution.y
        self.headers = headers


def metrics(stream):
    return {
        "COD": float(stream.COD),
        "TN": float(stream.TN),
        "TP": float(stream.TP),
        "TSS": float(stream.get_TSS()),
        "NH4": float(stream.state[stream.components.index("S_NH4")]),
        "PO4": float(stream.state[stream.components.index("S_PO4")]),
        "flow": float(stream.state[-1]),
    }


def calculate(data: dict, reference: bool = False) -> Calculation:
    """Use exactly the previous equations, integration and accepted-state postprocessing."""
    import numpy as np

    validate_inputs(data)
    system, units, streams = build_model(data, REACTORS, upstream_reference=reference)
    solver = data["solver"]
    days = solver["days"]
    started = time.perf_counter()
    sol = integrate(system, solver)
    integration_seconds = time.perf_counter() - started
    headers = [list(x) for x in system.scope.sol_header]
    if not sol.success or abs(sol.t[-1] - days) > 1e-8:
        raise IntegrationStopped(sol, headers)
    # Evaluate output streams from the accepted solution, not internal trial-step scopes.
    times = np.unique(np.r_[np.linspace(0, days, 401), days])
    trajectory = []
    for t in times:
        system.DAE(float(t), sol.sol(t).copy())
        system._write_state()
        trajectory.append({"day": float(t), **metrics(streams["EFFLUENT"])})
    system.DAE(float(days), sol.y[:, -1].copy())
    system._write_state()
    final = metrics(streams["EFFLUENT"])
    stream_rows = [
        {"stream": sid, "from": a, "to": b, "expected_flow_m3_d": q, **metrics(streams[sid])}
        for sid, a, b, q in connections(data)
    ]
    cmps = streams["INFLUENT"].components
    component_rows = []
    for i, c in enumerate(cmps):
        component_rows.append(
            {
                "component": c.ID,
                "measurement_basis": str(c.measured_as or "component mass"),
                "influent_mg_L": float(streams["INFLUENT"].state[i]),
                "i_COD": float(c.i_COD),
                "i_N": float(c.i_N),
                "i_P": float(c.i_P),
                "basis_status": "software example; not measured plant data",
            }
        )
    reactor_rows = [
        {
            "reactor": uid,
            "volume_m3": float(units[uid].V_max),
            "DO_mg_O2_L": float(units[uid].state["S_O2"]),
            "NO3_mg_N_L": float(units[uid].state["S_NO3"]),
            "NH4_mg_N_L": float(units[uid].state["S_NH4"]),
            **{c: float(units[uid].state[c]) for c in cmps.IDs},
        }
        for uid in REACTORS
    ]
    raw_eff = streams["EFFLUENT"].state[:-1]
    tn_sum = float(raw_eff @ (cmps.i_N * (1 - cmps.g)))
    tp_sum = float(raw_eff @ (cmps.i_P * (1 - cmps.g)))
    water_residual = (
        metrics(streams["INFLUENT"])["flow"] - final["flow"] - metrics(streams["WAS"])["flow"]
    )
    hydraulic_error = max(abs(row["flow"] - row["expected_flow_m3_d"]) for row in stream_rows)
    checks = {
        "integration_reached_requested_day": True,
        "accepted_solver_states_finite": bool(np.isfinite(sol.y).all()),
        "accepted_states_nonnegative_within_tolerance": bool(
            np.min(sol.y) >= -data["screening"]["negative_state_tolerance"]
        ),
        "external_water_balance": bool(abs(water_residual) < 1e-6),
        "stream_flow_mapping": bool(hydraulic_error < 1e-5),
        "TN_component_sum": bool(np.isclose(tn_sum, final["TN"], rtol=1e-9, atol=1e-9)),
        "TP_component_sum": bool(np.isclose(tp_sum, final["TP"], rtol=1e-9, atol=1e-9)),
        "total_biological_volume": bool(
            np.isclose(
                sum(units[x].V_max for x in REACTORS), sum(data["reactor_volumes_m3"].values())
            )
        ),
    }
    window = min(data["screening"]["tail_window_days"], days / 2)
    tail_times = np.linspace(days - window, days, 41)
    tail = sol.sol(tail_times)
    spans = np.ptp(tail, axis=1)
    limits = data["screening"]["absolute_state_change_tolerance"] + data["screening"][
        "relative_state_change_tolerance"
    ] * np.max(np.abs(tail), axis=1)
    normalized = spans / limits
    steady = {
        "status": "passed" if np.all(normalized <= 1) else "not_passed",
        "window_days": window,
        "max_normalized_state_span": float(np.max(normalized)),
        "criterion": (
            "Across 41 samples in the final window, every integrated state has "
            "range <= absolute tolerance + relative tolerance * maximum absolute "
            "state."
        ),
        "absolute_tolerance": data["screening"]["absolute_state_change_tolerance"],
        "relative_tolerance": data["screening"]["relative_state_change_tolerance"],
        "meaning": (
            "Local finite-window screen only; not proof of asymptotic stability, "
            "initialization robustness, or conservation."
        ),
    }
    result = {
        "case_id": data["case_id"],
        "status": "completed" if all(checks.values()) else "checks_failed",
        "scope": data["description"],
        "solver": solver,
        "elapsed_simulation_s": integration_seconds,
        "solver_nfev": sol.nfev,
        "solver_njev": sol.njev,
        "solver_nlu": sol.nlu,
        "effluent": final,
        "metric_units": METRICS,
        "influent": metrics(streams["INFLUENT"]),
        "basic_checks": checks,
        "steady_state_screen": steady,
        "residuals": {
            "external_water_m3_d": water_residual,
            "max_stream_flow_error_m3_d": hydraulic_error,
            "minimum_solver_state": float(np.min(sol.y)),
        },
        "versions": {
            p: md.version(p)
            for p in ("qsdsan", "exposan", "biosteam", "thermosteam", "numpy", "scipy", "numba")
        },
        "python": sys.version,
        "executable": sys.executable,
        "verification": {
            "whole_system_N_P_balance_with_accumulation_and_gas": "not_verified",
            "solver_method_and_tolerance_robustness": "not_verified",
            "initialization_robustness": "not_tested",
            "plant_validation": "not_applicable_generic_example",
            "design_feasibility": "not_assessed",
            "official_ASM2d_full_train_reference": "not_claimed",
        },
        "limitations": [
            "Not original ASM1 BSM1 and not Bergambacht.",
            "Constant example influent; no measured plant calibration.",
            (
                "KLa is an assumed/example oxygen-transfer coefficient, not blower "
                "power or measured aeration capacity."
            ),
            (
                "Secondary clarification is nonreactive; no digestion, headworks, "
                "chemical dosing or sludge-treatment train."
            ),
            "TN/TP calculation checks do not establish whole-system elemental conservation.",
            "Nominal zone labels do not guarantee zero DO or nitrate; inspect reactors.csv.",
        ],
    }

    return Calculation(
        result=result,
        streams=stream_rows,
        reactors=reactor_rows,
        components=component_rows,
        trajectory=trajectory,
        time_days=sol.t.copy(),
        states=sol.y.copy(),
        headers=headers,
        component_order=list(cmps.IDs),
    )
