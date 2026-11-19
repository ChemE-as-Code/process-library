"""Compose a local execution: fresh evidence folder, diagrams, calculation and report."""

import shutil
import time
import traceback
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from wwtp_a2o.domains.process.model import validate_inputs
from wwtp_a2o.domains.process.simulation import IntegrationStopped, calculate
from wwtp_a2o.integrations.cheme import collect_metadata, core_worker
from wwtp_a2o.integrations.qsdsan import upstream_evidence
from wwtp_a2o.project.artifacts import (
    make_adapter,
    save_calculation,
    save_solver,
    snapshot_sources,
    write_json,
)
from wwtp_a2o.project.prepare import prepare_project


@dataclass
class RunOutcome:
    run: Path
    status: int
    result: dict | None = None
    error: str | None = None


def create_run(root: Path, label: str) -> Path:
    safe = "".join(c for c in label if c.isascii() and (c.isalnum() or c in "_-"))[:40]
    run = (
        root
        / "process/simulation-runs"
        / (
            datetime.now().strftime("%Y%m%d_%H%M%S")
            + "_"
            + (safe or "case")
            + "_"
            + uuid.uuid4().hex[:6]
        )
    )
    run.mkdir(parents=True, exist_ok=False)
    (run / "source").mkdir()
    return run


def execute(
    root: Path,
    run: Path,
    data: dict,
    *,
    reference: bool = False,
    command: list[str] | None = None,
    progress: Callable[[str], None] | None = None,
) -> RunOutcome:
    """No terminal/global-path access: callers choose the workspace, run and progress sink."""

    def notify(message):
        if progress:
            progress(message)

    started = time.perf_counter()
    paths = snapshot_sources(root, run)
    write_json(run / "inputs.json", data)
    paths += [(run / "inputs.json").relative_to(root).as_posix()]
    manifest = {
        "started_at": datetime.now(UTC).isoformat(),
        "command": command or [],
        "local_only": True,
        "uses_MCP": False,
    }
    write_json(
        run / "metadata_request.json",
        {
            "root": str(root),
            "paths": paths,
            "checks": {},
        },
    )
    write_json(run / "manifest.json", manifest)
    try:
        metadata = collect_metadata(root, run)
        manifest.update(source=metadata["source"], fingerprints=metadata["source"]["fingerprints"])
        write_json(run / "manifest.json", manifest)
        validate_inputs(data)
        notify("[1/4] Building the EXPOsan ASM2d example...")
        parameters, upstream_files = upstream_evidence(data, reference)
        write_json(run / "model_parameters.json", parameters)
        for path in upstream_files:
            shutil.copy2(path, run / "source" / path.name)
        if not reference:
            notify("[2/4] Building and validating ChemE-as-Code diagrams...")
            prepare_project(run / "model", data)
            shutil.copytree(run / "model/process", run / "process_snapshot")
        solver = data["solver"]
        notify(f"[3/4] Integrating 0-{solver['days']:g} days ({solver['method']})...")
        calculated = calculate(data, reference)
        notify("[4/4] Saving accepted-state results and checks...")
        parameters["component_order"] = calculated.component_order
        write_json(run / "model_parameters.json", parameters)
        save_calculation(run, calculated)
        result = {
            **calculated.result,
            "run_id": run.name,
            "elapsed_total_s": time.perf_counter() - started,
        }
        write_json(
            run / "metadata_request.json",
            {
                "root": str(root),
                "paths": paths,
                "checks": result["basic_checks"],
                "source": metadata["source"],
            },
        )
        metadata = collect_metadata(root, run)
        result.update(source=metadata["source"], findings=metadata["findings"])
        manifest.update(source=metadata["source"], fingerprints=metadata["source"]["fingerprints"])
        write_json(run / "manifest.json", manifest)
        write_json(run / "result.json", result)
        write_json(
            run / "adapter-result.json",
            make_adapter(
                result,
                calculated.streams,
                calculated.reactors,
                metadata["source"],
                metadata["findings"],
            ),
        )
        core_worker(root, "validate", run)
        return RunOutcome(run, 0 if result["status"] == "completed" else 2, result)
    except Exception as error:  # noqa: BLE001 - retain evidence at the third-party execution boundary
        if isinstance(error, IntegrationStopped):
            save_solver(run, error.time_days, error.states, error.headers)
        (run / "error.log").write_text(traceback.format_exc(), encoding="utf-8")
        write_json(run / "failure.json", {"status": "failed", "error": str(error)})
        return RunOutcome(run, 1, error=str(error))
