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

``--cache DIR`` keeps each snapshot with the key it was exported under (``DIR/<id>/key.json``
beside ``DIR/<id>/snapshot/``): the process folder's last commit (``git log -1 -- <folder>``),
the tool's ``--version`` and the export arguments (``--public`` and the excludes). When the key
matches, the cached snapshot is copied to ``<out>/<id>`` instead of exporting (an export takes
about a minute). A folder with uncommitted changes, outside git, or a tool without a version is
always exported and not cached. Each process is reported as ``cached`` or ``exported``.

The command is ``cheme`` unless ``--cli`` (or ``$CHEME_CLI``) names another, e.g.
``"uv run --project ../core cheme"``. A process whose export fails is reported and skipped; the
Atlas then shows its static previews.

    uv run export_snapshots.py --library ../process-library --out build/snapshots [--public] [--cache .cache/snapshot-cache]
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

from publication import LCA_RESULT_FILES, is_public, placeholder_factors, snapshot_excludes


def _run(*command: str) -> str | None:
    """stdout of *command*, or None when it cannot run or fails."""
    try:
        done = subprocess.run(command, capture_output=True, text=True)
    except OSError:
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def _cache_key(folder: Path, tool: str | None, public: bool, excludes: list[str]) -> dict | None:
    """What a snapshot of *folder* depends on, or None when it must not be cached.

    None for a folder outside git or with uncommitted changes (``git status``), and for a tool
    that does not report its version.
    """
    commit = _run("git", "-C", str(folder), "log", "-1", "--format=%H", "--", ".")
    if not commit or not tool or _run("git", "-C", str(folder), "status", "--porcelain", "--", ".") != "":
        return None
    return {"commit": commit, "tool": tool, "args": {"public": public, "exclude": excludes}}


def _cached(cache: Path, pid: str, key: dict | None) -> Path | None:
    """The cached snapshot of *pid* when it was exported under *key*."""
    entry = cache / pid
    if key is None or not (entry / "key.json").is_file() or not (entry / "snapshot" / "manifest.json").is_file():
        return None
    try:
        stored = json.loads((entry / "key.json").read_text(encoding="utf-8"))
    except ValueError:
        return None
    return entry / "snapshot" if stored == key else None


def _store(cache: Path, pid: str, key: dict, snapshot: Path) -> None:
    entry = cache / pid
    shutil.rmtree(entry, ignore_errors=True)
    shutil.copytree(snapshot, entry / "snapshot")
    # written last: an interrupted store leaves no key, so the entry is a miss
    (entry / "key.json").write_text(json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cli", default=os.environ.get("CHEME_CLI", "cheme"))
    parser.add_argument("--source", action="append", default=[], metavar="ID=PATH")
    parser.add_argument("--public", action="store_true", help="published processes only, exported without the publication excludes")
    parser.add_argument("--cache", type=Path, metavar="DIR", help="reuse snapshots whose folder commit, tool version and arguments match")
    args = parser.parse_args(argv)

    cli = shlex.split(args.cli)
    if shutil.which(cli[0]) is None:
        print(f"{cli[0]} not found: snapshots skipped (the Atlas shows static previews)", file=sys.stderr)
        return 0
    sources = dict(item.split("=", 1) for item in args.source)
    out = args.out.resolve()
    cache = args.cache.resolve() if args.cache else None
    tool = _run(*cli, "--version") if cache else None
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
        key = _cache_key(folder, tool, args.public, excludes) if cache else None
        hit = _cached(cache, pid, key) if cache else None
        if hit:
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(hit, target)
            print(f"{pid}: cached")
            continue
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
        if key:
            _store(cache, pid, key, target)
        print(f"{pid}: exported: {done.stdout.strip()}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
