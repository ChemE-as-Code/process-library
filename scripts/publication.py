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
#: core's LCA result files (``cheme assess lca --write``): footprint values, excluded from the
#: snapshot of a process whose factors are placeholders, like the ``lca`` answer.
LCA_RESULT_FILES = ("lca/results.csv", "lca/results.md", "lca/uncertainty.csv")


def is_public(manifest: dict[str, Any] | None) -> bool:
    return ((manifest or {}).get("publication") or {}).get("status") == "public"


def snapshot_excludes(manifest: dict[str, Any] | None) -> list[str]:
    """The globs a published snapshot of this process must be exported without (sorted)."""
    own = ((manifest or {}).get("publication") or {}).get("exclude") or []
    return sorted({*DEFAULT_EXCLUDE, MANIFEST, *own})


def placeholder_factors(folder: Path) -> bool:
    """Whether the process's LCA factors are placeholders (``lca/factors.yaml`` ``example: true``)."""
    import yaml  # the callers declare pyyaml; this module stays importable without it

    path = folder / "lca" / "factors.yaml"
    return path.is_file() and bool((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("example"))
