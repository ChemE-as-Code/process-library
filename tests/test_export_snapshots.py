"""Snapshot export: which processes are exported, with which flags (a fake cheme records them)."""

from __future__ import annotations

import json
import shutil
import subprocess
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
if sys.argv[1:] == ["--version"]:
    print(os.environ.get("FAKE_CHEME_VERSION", "cheme-as-code 0.0.0"))
    sys.exit(0)
with open(os.environ["FAKE_CHEME_LOG"], "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
target = Path(sys.argv[2])
target.mkdir(parents=True, exist_ok=True)
(target / "manifest.json").write_text(json.dumps({"tool": os.environ.get("FAKE_CHEME_VERSION")}))
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
    # core's run manifest says the result may be published
    (factors.parent / "manifest.json").write_text(
        json.dumps({"result": {"publication": "public", "publishable": True}})
    )
    call = _run(library, tmp_path, monkeypatch, "--public")["fixture-electrolysis"]
    assert _excludes(call) == sorted({*DEFAULT_EXCLUDE, MANIFEST, "docs/private/**"})


def test_public_with_restricted_sources_excludes_the_lca_results(library: Path, tmp_path: Path, monkeypatch) -> None:
    factors = library / "processes" / "fixture-electrolysis" / "lca" / "factors.yaml"
    factors.write_text(factors.read_text().replace("example: true", "example: false"))
    (factors.parent / "manifest.json").write_text(
        json.dumps({"result": {"publication": "restricted", "publishable": False}})
    )
    call = _run(library, tmp_path, monkeypatch, "--public")["fixture-electrolysis"]
    assert set(LCA_RESULT_FILES) <= set(_excludes(call))


def test_defaults_match_contributing() -> None:
    contributing = (KIT / "CONTRIBUTING.md").read_text()
    for glob in (*DEFAULT_EXCLUDE, MANIFEST):
        assert f"`{glob}`" in contributing, glob


# --- cache ---------------------------------------------------------------------------------------


def _git(library: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(library), "-c", "user.email=t@e", "-c", "user.name=t", *args], check=True, capture_output=True)


@pytest.fixture
def repo(library: Path) -> Path:
    _git(library, "init", "-q", "-b", "main")
    _git(library, "add", "-A")
    _git(library, "commit", "-qm", "library")
    return library


def _cached_run(repo: Path, tmp_path: Path, monkeypatch, capsys, *extra: str) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Export calls made, and each process's report (cached or exported)."""
    capsys.readouterr()
    calls = _run(repo, tmp_path, monkeypatch, "--cache", str(tmp_path / "cache"), *extra)
    lines = [line.split(": ") for line in capsys.readouterr().out.splitlines()]
    return calls, {line[0]: line[1] for line in lines}


BOTH = ["fixture-ammonia", "fixture-electrolysis"]


def test_cache_hit_copies_the_snapshot_without_exporting(repo: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys)
    assert sorted(calls) == BOTH and set(report.values()) == {"exported"}
    assert (tmp_path / "cache" / "fixture-electrolysis" / "preview" / "key.json").is_file()
    shutil.rmtree(tmp_path / "snaps")
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys)
    assert calls == {} and report == {pid: "cached" for pid in BOTH}
    for pid in BOTH:  # the output layout is unchanged
        assert (tmp_path / "snaps" / pid / "manifest.json").is_file()
    key = json.loads((tmp_path / "cache" / "fixture-electrolysis" / "preview" / "key.json").read_text())
    assert key["tool"] == "cheme-as-code 0.0.0" and key["args"] == {"public": False, "exclude": []}
    assert len(key["commit"]) == 40


def test_cache_misses_when_the_folder_commit_changes(repo: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    _cached_run(repo, tmp_path, monkeypatch, capsys)
    _git(repo, "commit", "-q", "--allow-empty", "-m", "elsewhere")  # a library commit outside the folder
    plant = repo / "processes" / "fixture-electrolysis" / "plant.yaml"
    plant.write_text(plant.read_text() + "\n# changed\n")
    _git(repo, "commit", "-qam", "change electrolysis")
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys)
    assert sorted(calls) == ["fixture-electrolysis"]
    assert report == {"fixture-ammonia": "cached", "fixture-electrolysis": "exported"}


def test_cache_misses_when_the_tool_version_changes(repo: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    _cached_run(repo, tmp_path, monkeypatch, capsys)
    monkeypatch.setenv("FAKE_CHEME_VERSION", "cheme-as-code 0.0.1")
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys)
    assert sorted(calls) == BOTH and set(report.values()) == {"exported"}
    assert json.loads((tmp_path / "snaps" / "fixture-ammonia" / "manifest.json").read_text())["tool"] == "cheme-as-code 0.0.1"
    calls, _ = _cached_run(repo, tmp_path, monkeypatch, capsys)
    assert calls == {}


def test_cache_misses_when_the_arguments_change(repo: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    _cached_run(repo, tmp_path, monkeypatch, capsys)
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys, "--public")  # adds the excludes
    assert sorted(calls) == ["fixture-electrolysis"] and report["fixture-electrolysis"] == "exported"
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys, "--public")
    assert calls == {} and report["fixture-electrolysis"] == "cached"
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys)  # the preview entry is kept
    assert calls == {} and report["fixture-electrolysis"] == "cached"
    key = json.loads((tmp_path / "cache" / "fixture-electrolysis" / "public" / "key.json").read_text())
    assert key["args"]["public"] is True and "docs/private/**" in key["args"]["exclude"]


def test_dirty_folder_is_always_exported_and_not_cached(repo: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    _cached_run(repo, tmp_path, monkeypatch, capsys)
    stored = (tmp_path / "cache" / "fixture-electrolysis" / "preview" / "key.json").read_text()
    plant = repo / "processes" / "fixture-electrolysis" / "plant.yaml"
    original = plant.read_text()
    plant.write_text(original + "\n# uncommitted\n")
    calls, report = _cached_run(repo, tmp_path, monkeypatch, capsys)
    assert sorted(calls) == ["fixture-electrolysis"]
    assert report == {"fixture-ammonia": "cached", "fixture-electrolysis": "exported"}
    assert (tmp_path / "cache" / "fixture-electrolysis" / "preview" / "key.json").read_text() == stored
    (repo / "processes" / "fixture-electrolysis" / "new.md").write_text("untracked\n")
    plant.write_text(original)
    assert sorted(_cached_run(repo, tmp_path, monkeypatch, capsys)[0]) == ["fixture-electrolysis"]
    (repo / "processes" / "fixture-electrolysis" / "new.md").unlink()
    assert _cached_run(repo, tmp_path, monkeypatch, capsys)[0] == {}  # clean again: the stored entry


def test_library_outside_git_is_exported_and_not_cached(library: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    for _ in range(2):
        calls, report = _cached_run(library, tmp_path, monkeypatch, capsys)
        assert sorted(calls) == BOTH and set(report.values()) == {"exported"}
    assert not any((tmp_path / "cache").glob("*/*/key.json"))
