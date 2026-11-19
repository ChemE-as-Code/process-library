"""Thin Typer entry point for the existing VS Code run workflow."""

import json
import sys
import traceback
from pathlib import Path
from typing import Annotated

import typer

from wwtp_a2o.foundation.runtime import ROOT
from wwtp_a2o.interfaces.cli.console import recorded_console
from wwtp_a2o.project.artifacts import write_json
from wwtp_a2o.project.run import create_run, execute

app = typer.Typer(add_completion=False)


@app.command()
def main(
    input_path: Annotated[Path, typer.Option("--input")] = ROOT / "inputs/baseline.json",
    no_viewer: Annotated[bool, typer.Option("--no-viewer")] = False,
    port: int = 8770,
    days: float | None = None,
    rtol: float | None = None,
    atol: float | None = None,
    method: str | None = None,
    upstream_reference: Annotated[bool, typer.Option("--upstream-reference", hidden=True)] = False,
):
    data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    data["solver"].setdefault("wall_limit_s", 180)
    for key, value in (("days", days), ("rtol", rtol), ("atol", atol), ("method", method)):
        if value is not None:
            data["solver"][key] = value
    if upstream_reference:
        original = json.loads((ROOT / "inputs/baseline.json").read_text(encoding="utf-8"))
        if any(
            data[k] != original[k]
            for k in ("influent", "reactor_volumes_m3", "recycles", "aeration", "clarifier")
        ):
            raise typer.BadParameter(
                "Upstream reference requires the baseline engineering settings"
            )
    if not no_viewer:
        from wwtp_a2o.interfaces.cli.viewer import check_viewer

        check_viewer(port)
    run = create_run(ROOT, "reference" if upstream_reference else data["case_id"])
    with recorded_console(run):
        print(f"New run: {run}", flush=True)
        outcome = execute(
            ROOT,
            run,
            data,
            reference=upstream_reference,
            command=sys.argv,
            progress=lambda message: print(message, flush=True),
        )
        if outcome.error:
            print(f"Failed: {outcome.error}\nEvidence: {run}", flush=True)
            raise typer.Exit(outcome.status)
        from wwtp_a2o.interfaces.report import write_saved_report

        result = outcome.result
        try:
            write_saved_report(run, data, result)
        except Exception as error:
            (run / "error.log").write_text(traceback.format_exc(), encoding="utf-8")
            write_json(run / "failure.json", {"status": "failed", "error": str(error)})
            print(f"Failed: {error}\nEvidence: {run}", flush=True)
            raise typer.Exit(1) from error
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "effluent": result["effluent"],
                    "steady_state_screen": result["steady_state_screen"]["status"],
                    "evidence": str(run),
                },
                indent=2,
            ),
            flush=True,
        )
    if not no_viewer:
        from wwtp_a2o.interfaces.cli.viewer import launch_viewer

        launch_viewer(port, run_id=run.name)
    raise typer.Exit(outcome.status)
