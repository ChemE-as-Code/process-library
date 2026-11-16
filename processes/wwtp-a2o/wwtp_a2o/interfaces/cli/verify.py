"""Typer command for upstream/reference comparisons."""

import json
from pathlib import Path
from typing import Annotated

import typer

from wwtp_a2o.foundation.runtime import ROOT
from wwtp_a2o.project.verification import verify_runs

app = typer.Typer(add_completion=False)


@app.command()
def main(
    baseline_run: Path | None = None,
    reference_run: Path | None = None,
    numerics_run: Path | None = None,
    incomplete_probe: Annotated[list[Path] | None, typer.Option("--incomplete-probe")] = None,
):
    path, result, status = verify_runs(
        ROOT,
        baseline_run,
        reference_run,
        numerics_run,
        incomplete_probe,
    )
    print(json.dumps(result, indent=2))
    print(f"Verification evidence: {path}")
    raise typer.Exit(status)
