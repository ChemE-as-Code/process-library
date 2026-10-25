"""What a public build may show: the rules shared by the build scripts' ``--public`` mode.

A process is published when its ``process.yaml`` says ``publication.status: public``; every
other status (``internal``, ``candidate``, none) keeps it out of a public build entirely. A
published process's viewer snapshot is exported without :data:`DEFAULT_EXCLUDE` and
:data:`MANIFEST` (always) and the process's own ``publication.exclude`` globs; core's ``cheme export-static --exclude``
matches them (``**`` spans directories, ``*`` stays in one, a plain name is the root file).

Every script imports it from beside itself (``scripts/`` is on ``sys.path`` when one runs).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

#: Excluded from every published snapshot: agent instructions and working notes, not design.
#: Documented in CONTRIBUTING.md; change both together.
DEFAULT_EXCLUDE = (
    ".claude/**",
    "AGENTS.md",
    "CLAUDE.md",
    "reviews/**",
    "PROGRESS.md",
    "scripts/agent-run/**",
    "**/.gitattributes",
)
#: The Atlas manifest, in the process folder beside the engineering files: also excluded from
#: every published snapshot, as it names the repository (maybe private) and the excludes; the
#: catalog publishes what of it may be public.
MANIFEST = "process.yaml"
#: core's LCA result files (``cheme assess lca --write``, and the per-scenario records of
#: ``cheme assess lca-scenarios --write``, a glob): footprint values and what they lack,
#: excluded from the snapshot of a process whose LCA may not be published, like the ``lca``
#: answer (core's ``export-static`` withholds the same).
LCA_RESULT_FILES = ("lca/results.csv", "lca/results.md", "lca/gaps.csv", "lca/uncertainty.csv", "lca/scenarios/**")
#: core's run manifest of the LCA: the result's class and publication policy.
LCA_MANIFEST = "lca/manifest.json"


def is_public(manifest: dict[str, Any] | None) -> bool:
    return ((manifest or {}).get("publication") or {}).get("status") == "public"


def snapshot_excludes(manifest: dict[str, Any] | None) -> list[str]:
    """The globs a published snapshot of this process must be exported without (sorted)."""
    own = ((manifest or {}).get("publication") or {}).get("exclude") or []
    return sorted({*DEFAULT_EXCLUDE, MANIFEST, *own})


def lca_withheld(folder: Path) -> str | None:
    """Why the process's LCA values may not be published, or None when they may.

    The rule follows core's publication policy, read from the committed run manifest
    (``lca/manifest.json``, written by ``cheme assess lca --write``): its result must be
    ``publishable`` (every source ``public``, or ``restricted`` with the study's reviewed
    decision). Placeholder factors are never published, and without a manifest (an LCA written
    by an older core) nothing says the sources permit it, so the values are withheld too. A
    manifest whose input fingerprints (``inputs``: path -> sha256 with normalised line endings)
    no longer match the files, whose ``results`` fingerprint (sha256 of ``lca/results.csv``,
    when the manifest has one) is not the committed file's, or whose backend is not the scope's, describes another run:
    ``stale-run-manifest``.
    """
    import hashlib
    import json

    import yaml

    if not (folder / "lca" / "lca.yaml").is_file():
        return None
    if placeholder_factors(folder):
        return "placeholder-factors"
    path = folder / LCA_MANIFEST
    if not path.is_file():
        return "no-run-manifest"
    try:
        run = json.loads(path.read_text(encoding="utf-8")) or {}
        scope = yaml.safe_load((folder / "lca" / "lca.yaml").read_text(encoding="utf-8")) or {}
    except (OSError, ValueError, yaml.YAMLError):
        return "no-run-manifest"
    for rel, sha in (run.get("inputs") or {}).items():
        target = folder / rel
        if not target.is_file():
            return "stale-run-manifest"
        content = target.read_bytes().replace(b"\r\n", b"\n")
        if "sha256:" + hashlib.sha256(content).hexdigest() != sha:
            return "stale-run-manifest"
    # the committed results.csv is the text this run wrote (manifests of core before the
    # fingerprint have no "results" and are not checked)
    recorded = run.get("results")
    if recorded is not None:
        csv_path = folder / "lca" / "results.csv"
        if not csv_path.is_file():
            return "stale-run-manifest"
        text = csv_path.read_bytes().replace(b"\r\n", b"\n")
        if "sha256:" + hashlib.sha256(text).hexdigest() != recorded:
            return "stale-run-manifest"
    if (run.get("background") or {}).get("backend", "factors") != scope.get("backend", "factors"):
        return "stale-run-manifest"
    result = run.get("result") or {}
    if result.get("publishable") is True:
        return None
    return f"{result.get('publication') or 'unknown'}-sources"


def placeholder_factors(folder: Path) -> bool:
    """Whether the process's LCA factors are placeholders (``lca/factors.yaml`` ``example: true``)."""
    import yaml  # the callers declare pyyaml; this module stays importable without it

    path = folder / "lca" / "factors.yaml"
    return path.is_file() and bool((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("example"))
