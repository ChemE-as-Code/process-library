"""Resolve local environments without importing numerical or presentation packages."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT.parents[1]
CORE = Path(os.environ.get("CHEME_CORE_PATH", ROOT.parents[2] / "core")).resolve()


def venv_python(directory: Path, platform: str | None = None) -> Path:
    platform = platform or os.name
    return directory / ("Scripts/python.exe" if platform == "nt" else "bin/python")


PYTHON = venv_python(ROOT / ".venv")
CORE_PYTHON = Path(os.environ.get("CHEME_CORE_PYTHON", venv_python(CORE / ".venv"))).absolute()


def environment() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        PYTHONUTF8="1",
        OPENBLAS_NUM_THREADS="1",
        OMP_NUM_THREADS="1",
        GIT_CEILING_DIRECTORIES=str(LIBRARY.parent),
    )
    return env


def select_environment(entry: Path) -> None:
    """Keep the VS Code Run button usable with a different selected interpreter."""
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        if not PYTHON.is_file():
            raise SystemExit("Create the WWTP-A2O environment first; see README.md.")
        print("Using the WWTP-A2O Python environment...", flush=True)
        try:
            completed = subprocess.run(
                [str(PYTHON), str(entry), *sys.argv[1:]],
                cwd=ROOT,
                env=environment(),
                check=False,
            )
        except KeyboardInterrupt:
            raise SystemExit(130) from None
        raise SystemExit(completed.returncode)
    os.environ.update(
        {
            k: environment()[k]
            for k in (
                "PYTHONUTF8",
                "OPENBLAS_NUM_THREADS",
                "OMP_NUM_THREADS",
                "GIT_CEILING_DIRECTORIES",
            )
        }
    )
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
