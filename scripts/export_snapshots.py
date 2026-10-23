# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""Write a viewer snapshot (``cheme export-static``) of every plantcode process in a library.

For each ``processes/<id>/plant.yaml`` it runs ``<cli> export-static <out>/<id> --repo <folder>``.
The snapshot holds the viewer's API answers of that revision (manifest.json + data/), so the
Atlas can embed the viewer without a server. Everything is produced by core; nothing here reads
engineering files (``--public`` reads only ``process.yaml`` and ``lca/factors.yaml``).

``--public`` exports only the processes whose ``process.yaml`` has ``publication.status:
public``, each with ``--exclude`` for the default and the process's own globs (``publication.py``)
and, when its LCA factors are placeholders, for core's LCA result files. The catalog's
``--public`` build refuses a snapshot whose manifest does not record these excludes.

``--source <id>=<path>`` exports a process from another checkout instead of its library folder
(the interim example-asu arrangement, so the snapshot keeps the git history and commit).

The command is ``cheme`` unless ``--cli`` (or ``$CHEME_CLI``) names another, e.g.
``"uv run --project ../core cheme"``. A process whose export fails is reported and skipped; the
Atlas then shows its static previews.

    uv run export_snapshots.py --library ../process-library --out build/snapshots [--public]
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from publication import LCA_RESULT_FILES, is_public, placeholder_factors, snapshot_excludes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cli", default=os.environ.get("CHEME_CLI", "cheme"))
    parser.add_argument("--source", action="append", default=[], metavar="ID=PATH")
    parser.add_argument("--public", action="store_true", help="published processes only, exported without the publication excludes")
    args = parser.parse_args(argv)

    cli = shlex.split(args.cli)
    if shutil.which(cli[0]) is None:
        print(f"{cli[0]} not found: snapshots skipped (the Atlas shows static previews)", file=sys.stderr)
        return 0
    sources = dict(item.split("=", 1) for item in args.source)
    out = args.out.resolve()
    failures = 0
    for plant in sorted(args.library.resolve().glob("processes/*/plant.yaml")):
        pid = plant.parent.name
        folder = Path(sources.get(pid, plant.parent)).resolve()
        target = out / pid
        excludes: list[str] = []
        if args.public:
            manifest_path = plant.parent / "process.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else None
            if not is_public(manifest):
                print(f"{pid}: not public, skipped")
                continue
            excludes = snapshot_excludes(manifest)
            if placeholder_factors(folder):
                excludes = sorted({*excludes, *LCA_RESULT_FILES})
        done = subprocess.run(
            [*cli, "export-static", str(target), "--repo", str(folder), *(a for g in excludes for a in ("--exclude", g))],
            capture_output=True,
            text=True,
        )
        if done.returncode != 0 or not (target / "manifest.json").is_file():
            failures += 1
            shutil.rmtree(target, ignore_errors=True)
            print(f"{pid}: export failed: {(done.stderr or done.stdout).strip()[-400:]}", file=sys.stderr)
            continue
        print(f"{pid}: {done.stdout.strip()}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
