"""Persist calculated evidence; numerical methods live in domains/process."""

import csv
import json
import shutil
from pathlib import Path

from wwtp_a2o.domains.process.simulation import METRICS, Calculation
from wwtp_a2o.integrations.plotting import save_plot


def write_json(path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )


def save_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def source_files(root: Path) -> list[Path]:
    return sorted(
        [
            *root.glob("*.py"),
            *(root / "wwtp_a2o").rglob("*.py"),
            *(root / "wwtp_a2o").rglob("*.html"),
            root / "requirements.lock.txt",
            root / "pyproject.toml",
        ]
    )


def snapshot_sources(root: Path, run: Path) -> list[str]:
    paths = source_files(root)
    for path in [*paths, *(root / "licenses").glob("*.txt")]:
        target = run / "source" / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    return [p.relative_to(root).as_posix() for p in paths]


def save_solver(run, time_days, states, headers):
    import numpy as np

    np.savez_compressed(run / "solver_states.npz", time_days=time_days, states=states)
    write_json(run / "solver_state_headers.json", headers)


def save_calculation(run: Path, calculation: Calculation):
    save_solver(run, calculation.time_days, calculation.states, calculation.headers)
    for filename, rows in (
        ("streams.csv", calculation.streams),
        ("trajectory.csv", calculation.trajectory),
        ("influent_components.csv", calculation.components),
        ("reactors.csv", calculation.reactors),
    ):
        save_csv(run / filename, rows)
    save_plot(run, calculation.trajectory, METRICS)


def make_adapter(result, streams, reactors, source, findings):
    ok = result["status"] == "completed"
    return {
        "schema": "cheme/adapter-result/v1",
        "case": result["case_id"],
        "status": "converged" if ok else "not-converged",
        "solver": {
            "name": "QSDsan",
            "version": result["versions"]["qsdsan"],
            "method": "ASM2d / " + result["solver"]["method"],
        },
        "inputs": source,
        "findings": findings,
        "units": [
            {"id": r["reactor"], "status": "simulated", "results": {"volume_m3": r["volume_m3"]}}
            for r in reactors
        ]
        + [{"id": "C1", "status": "simulated", "results": {}}],
        "streams": [
            {
                "id": r["stream"],
                "filled": [],
                "values": {k: {"value": r[k], "unit": unit} for k, unit in METRICS.items()},
            }
            for r in streams
        ],
        "messages": [
            (
                "Converged denotes completion of the requested integration and basic "
                "checks, not a steady-state or plant-validation claim."
            )
        ],
        "verification": result["verification"],
        "steady_state_screen": result["steady_state_screen"],
    }
