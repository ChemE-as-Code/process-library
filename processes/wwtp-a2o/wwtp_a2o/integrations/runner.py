"""Run the standalone example in its own numerical interpreter."""

import subprocess
from pathlib import Path

from wwtp_a2o.foundation.runtime import PYTHON, environment


def execute_example(root: Path, extra: list[str]) -> Path:
    before = {p.name for p in (root / "process/simulation-runs").glob("*") if p.is_dir()}
    completed = subprocess.run(
        [str(PYTHON), "-u", str(root / "run_example.py"), "--no-viewer", *extra],
        cwd=root,
        env=environment(),
        check=False,
    )
    added = [
        p
        for p in (root / "process/simulation-runs").iterdir()
        if p.is_dir() and p.name not in before and (p / "result.json").is_file()
    ]
    if completed.returncode or len(added) != 1:
        raise RuntimeError("Verification execution failed; inspect the new run folder")
    return added[0]
