"""CI installs one pinned core (#91): an unpinned install changes generated records under us."""

from __future__ import annotations

import re
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
WORKFLOWS = KIT / ".github" / "workflows"


def test_core_pinned_to_one_commit():
    refs = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for url in re.findall(r"github\.com/ChemE-as-Code/core\.git[^\s\"']*", path.read_text()):
            match = re.fullmatch(r"github\.com/ChemE-as-Code/core\.git@([0-9a-f]{40})", url)
            assert match, f"{path.name}: core not pinned to a full commit: {url}"
            refs.setdefault(match.group(1), []).append(path.name)
    assert {"validate.yml", "release.yml"} <= {name for names in refs.values() for name in names}
    assert len(refs) == 1, f"core pinned to different commits: {refs}"


def test_lca_files_checked_per_plant():
    """A stale LCA run manifest withholds a public footprint (#422, ADR 0038): the per-plant job
    checks the LCA files wherever lca/lca.yaml exists, and a failure fails the job."""
    import yaml

    steps = yaml.safe_load((WORKFLOWS / "validate.yml").read_text())["jobs"]["validate"]["steps"]
    step = next((s for s in steps if s.get("name") == "LCA files current"), None)
    assert step, "validate job has no 'LCA files current' step"
    assert "cheme assess lca --check" in step["run"] and "lca/lca.yaml" in step["run"]
    assert not step.get("continue-on-error"), "the LCA check must fail the job"
