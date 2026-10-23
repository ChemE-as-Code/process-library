"""Snapshot export: which processes are exported, with which flags (a fake cheme records them)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import export_snapshots  # noqa: E402
from publication import DEFAULT_EXCLUDE, LCA_RESULT_FILES, MANIFEST  # noqa: E402

LIBRARY = KIT / "tests" / "fixtures" / "library"
#: Stands in for cheme: records its arguments, writes a manifest into the target.
FAKE_CLI = """
import json, os, sys
from pathlib import Path
with open(os.environ["FAKE_CHEME_LOG"], "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
target = Path(sys.argv[2])
target.mkdir(parents=True, exist_ok=True)
(target / "manifest.json").write_text("{}")
print("1 responses written")
"""


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    # a second plantcode process, internal (no publication block)
    shutil.copy(copy / "processes" / "fixture-electrolysis" / "plant.yaml", copy / "processes" / "fixture-ammonia" / "plant.yaml")
    return copy


def _run(library: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *extra: str) -> dict[str, list[str]]:
    fake = tmp_path / "fake_cheme.py"
    fake.write_text(FAKE_CLI)
    log = tmp_path / "calls.jsonl"
    log.unlink(missing_ok=True)
    monkeypatch.setenv("FAKE_CHEME_LOG", str(log))
    cli = f"{sys.executable} {fake}"
    assert export_snapshots.main(["--library", str(library), "--out", str(tmp_path / "snaps"), "--cli", cli, *extra]) == 0
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []
    return {Path(call[1]).name: call for call in calls}


def _excludes(call: list[str]) -> list[str]:
    return [call[i + 1] for i, arg in enumerate(call) if arg == "--exclude"]


def test_without_public_every_plant_is_exported_without_excludes(library: Path, tmp_path: Path, monkeypatch) -> None:
    calls = _run(library, tmp_path, monkeypatch)
    assert sorted(calls) == ["fixture-ammonia", "fixture-electrolysis"]
    for pid, call in calls.items():
        assert call == ["export-static", str(tmp_path / "snaps" / pid), "--repo", str(library / "processes" / pid)]


def test_public_exports_published_processes_with_the_publication_excludes(library: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    calls = _run(library, tmp_path, monkeypatch, "--public")
    assert sorted(calls) == ["fixture-electrolysis"]
    assert "fixture-ammonia: not public, skipped" in capsys.readouterr().out
    call = calls["fixture-electrolysis"]
    assert call[:4] == ["export-static", str(tmp_path / "snaps" / "fixture-electrolysis"), "--repo", str(library / "processes" / "fixture-electrolysis")]
    # defaults, the manifest, the process's own glob, and (placeholder factors) LCA result files
    assert _excludes(call) == sorted({*DEFAULT_EXCLUDE, MANIFEST, "docs/private/**", *LCA_RESULT_FILES})
    assert len(call) == 4 + 2 * len(_excludes(call))


def test_public_with_published_factors_keeps_the_lca_results(library: Path, tmp_path: Path, monkeypatch) -> None:
    factors = library / "processes" / "fixture-electrolysis" / "lca" / "factors.yaml"
    factors.write_text(factors.read_text().replace("example: true", "example: false"))
    call = _run(library, tmp_path, monkeypatch, "--public")["fixture-electrolysis"]
    assert _excludes(call) == sorted({*DEFAULT_EXCLUDE, MANIFEST, "docs/private/**"})


def test_defaults_match_contributing() -> None:
    contributing = (KIT / "CONTRIBUTING.md").read_text()
    for glob in (*DEFAULT_EXCLUDE, MANIFEST):
        assert f"`{glob}`" in contributing, glob
