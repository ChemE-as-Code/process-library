# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Render the sheets of every plantcode process in a library to preview SVGs.

For each ``processes/<id>/plant.yaml`` it runs ``<cli> render <sheet file> -o
<out>/<id>/<sheet id>.svg`` in the process folder, and writes ``<out>/<id>/render.json`` with
the tool version and the source commit, so the catalog can tell a stale preview from a current
one. Rendering is core's (cheme); nothing here draws.

The command is ``cheme`` unless ``--cli`` (or ``$CHEME_CLI``) names another, e.g.
``"uv run --project ../core cheme"``. A sheet that fails to render is reported and skipped; the catalog
then shows it as not generated.

    uv run render_previews.py --library ../process-library --out build/previews
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def _git(cwd: Path, *args: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cli", default=os.environ.get("CHEME_CLI", "cheme"))
    parser.add_argument("--commit", help="source commit to record when the library is not a git checkout")
    args = parser.parse_args(argv)

    cli = shlex.split(args.cli)
    if shutil.which(cli[0]) is None:
        print(f"{cli[0]} not found: previews skipped (the catalog shows them as not generated)", file=sys.stderr)
        return 0
    version = subprocess.run([*cli, "--version"], capture_output=True, text=True).stdout.splitlines()
    tool = version[0].strip() if version else args.cli

    library = args.library.resolve()
    failures = 0
    for plant_path in sorted((library / "processes").glob("*/plant.yaml")):
        folder = plant_path.parent
        pid = folder.name
        target = args.out.resolve() / pid
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        plant = yaml.safe_load(plant_path.read_text(encoding="utf-8")) or {}
        rendered = []
        for sheet in plant.get("sheets", []):
            svg = target / f"{sheet['id']}.svg"
            done = subprocess.run([*cli, "render", sheet["file"], "-o", str(svg)], cwd=folder, capture_output=True, text=True)
            if done.returncode != 0 or not svg.is_file():
                failures += 1
                print(f"{pid}/{sheet['id']}: render failed: {done.stderr.strip()[-300:]}", file=sys.stderr)
                continue
            rendered.append(sheet["id"])
        source_commit = _git(library, "log", "-1", "--format=%H", "--", str(folder.relative_to(library))) or args.commit
        (target / "render.json").write_text(
            json.dumps({"tool": tool, "source_commit": source_commit, "sheets": rendered}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"{pid}: {len(rendered)} sheet(s) rendered with {tool}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
