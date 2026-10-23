"""Catalog builder: schema, determinism, derived data, error and fallback states."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_catalog  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
LIBRARY = FIXTURES / "library"
PREVIEWS = FIXTURES / "previews"


def _build(library: Path, out: Path, previews: Path | None = PREVIEWS) -> build_catalog.Report:
    return build_catalog.build(library, out, previews, commit="fixture")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(_json(KIT / "schemas" / name))


@pytest.mark.parametrize(
    "manifest",
    [
        KIT / "processes" / "asu-1" / "process.yaml",
        KIT / "templates" / "process" / "process.yaml",
        *sorted(LIBRARY.glob("processes/*/process.yaml")),
    ],
    ids=lambda p: p.parent.name,
)
def test_manifests_match_the_schema(manifest: Path) -> None:
    errors = list(_validator("process.schema.json").iter_errors(yaml.safe_load(manifest.read_text())))
    assert errors == []


def test_registry_matches_the_schema_and_covers_the_staged_manifests() -> None:
    registry = yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text())
    assert list(_validator("chemicals.schema.json").iter_errors(registry)) == []
    slugs = [c["slug"] for c in registry["chemicals"]]
    assert slugs == sorted(slugs) and len(slugs) == len(set(slugs))
    for manifest in (KIT / "processes").glob("*/process.yaml"):
        chemistry = yaml.safe_load(manifest.read_text())["chemistry"]
        used = {f["chemical"] for flows in chemistry.values() for f in flows}
        assert used <= set(slugs), manifest


def test_fixture_library_builds(tmp_path: Path) -> None:
    report = _build(LIBRARY, tmp_path / "out")
    assert report.errors == []
    catalog = _json(tmp_path / "out" / "catalog.json")
    assert catalog["schema"] == "cheme-as-code/catalog/v1"
    assert [p["id"] for p in catalog["processes"]] == ["fixture-ammonia", "fixture-electrolysis"]
    assert catalog["library"] == {"commit": "fixture", "dirty": None}
    assert catalog["mode"] == "preview"


def test_build_is_byte_identical(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "a")
    _build(LIBRARY, tmp_path / "b")
    files_a = sorted(p.relative_to(tmp_path / "a") for p in (tmp_path / "a").rglob("*") if p.is_file())
    files_b = sorted(p.relative_to(tmp_path / "b") for p in (tmp_path / "b").rglob("*") if p.is_file())
    assert files_a == files_b
    for rel in files_a:
        assert (tmp_path / "a" / rel).read_bytes() == (tmp_path / "b" / rel).read_bytes(), rel


def test_manifest_only_process_needs_no_engineering_files(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "out")
    detail = _json(tmp_path / "out" / "processes" / "fixture-ammonia.json")
    assert detail["engineering"] is None
    assert detail["representations"] == []
    assert detail["lca"] is None
    summary = next(p for p in _json(tmp_path / "out" / "catalog.json")["processes"] if p["id"] == "fixture-ammonia")
    assert summary["engineering_project"] is False and summary["lca"] is None


def test_new_process_folder_appears_without_other_changes(library: Path, tmp_path: Path) -> None:
    new = library / "processes" / "fixture-new"
    new.mkdir()
    manifest = yaml.safe_load((library / "processes" / "fixture-ammonia" / "process.yaml").read_text())
    manifest.update(id="fixture-new", title="Fixture: a new process")
    (new / "process.yaml").write_text(yaml.safe_dump(manifest))
    assert _build(library, tmp_path / "out").errors == []
    assert "fixture-new" in [p["id"] for p in _json(tmp_path / "out" / "catalog.json")["processes"]]
    assert (tmp_path / "out" / "processes" / "fixture-new.json").is_file()


def test_lca_uses_the_stated_total_and_flags_placeholder_factors(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "out")
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["totals"] == {"baseline": {"climate-change": 24.0}}
    assert lca["factors_status"] == "placeholder"
    assert lca["functional_unit"]["label"] == "1 kg H2"
    assert [c["key"] for c in lca["contributions"]] == ["feed:POWER", "construction:steel"]
    assert {r["key"] for r in lca["inventory"]} == {"feed:WATER", "feed:POWER", "product:H2", "product:O2"}


def test_lca_without_a_total_row_sums_the_contributions(library: Path, tmp_path: Path) -> None:
    results = library / "processes" / "fixture-electrolysis" / "lca" / "results.csv"
    results.write_text("".join(line for line in results.read_text().splitlines(True) if ",total," not in line))
    _build(library, tmp_path / "out")
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["totals"]["baseline"]["climate-change"] == pytest.approx(24.0)


def test_representations_and_preview_states(tmp_path: Path) -> None:
    report = _build(LIBRARY, tmp_path / "out")
    reps = {r["id"]: r for r in _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["representations"]}
    assert reps["P-01"]["status"] == "preview"
    assert (tmp_path / "out" / reps["P-01"]["preview"]).is_file()
    assert reps["BFD"]["status"] == "not-generated"
    assert any("no preview rendered for BFD" in w for w in report.warnings)
    assert reps["process-model"]["status"] == "viewer"
    assert reps["lca"]["status"] == "viewer"
    assert [r["kind"] for r in reps.values()][:2] == ["bfd", "pid"]


def test_no_previews_directory_still_builds(tmp_path: Path) -> None:
    report = _build(LIBRARY, tmp_path / "out", previews=None)
    assert report.errors == []
    reps = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["representations"]
    assert {r["status"] for r in reps if r["kind"] in ("pid", "bfd")} == {"not-generated"}


def test_unsafe_preview_is_rejected(tmp_path: Path) -> None:
    previews = tmp_path / "previews"
    shutil.copytree(PREVIEWS, previews)
    svg = previews / "fixture-electrolysis" / "P-01.svg"
    svg.write_text(svg.read_text().replace("<rect", '<rect onload="alert(1)"'))
    report = _build(LIBRARY, tmp_path / "out", previews)
    assert any("scripts or external references" in e for e in report.errors)
    assert not (tmp_path / "out" / "artifacts" / "fixture-electrolysis" / "P-01.svg").exists()


def test_stale_previews_are_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    answers = {"rev-parse": str(LIBRARY), "log": "newer", "status": ""}
    monkeypatch.setattr(build_catalog, "_git", lambda library, *args: answers[args[0]])
    _build(LIBRARY, tmp_path / "out")
    provenance = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["provenance"]
    assert provenance["source_commit"] == "newer"
    assert provenance["previews_stale"] is True


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda m: m["chemistry"]["inputs"].append({"chemical": "unobtainium", "role": "feedstock"}), "unknown chemical 'unobtainium'"),
        (lambda m: m.update(id="another-id"), "differs from folder name"),
        (lambda m: m.update(maturity="finished"), "maturity"),
        (lambda m: m.pop("summary"), "'summary' is a required property"),
    ],
    ids=["unknown-chemical", "id-mismatch", "bad-enum", "missing-field"],
)
def test_manifest_errors(library: Path, tmp_path: Path, edit, message: str) -> None:
    path = library / "processes" / "fixture-ammonia" / "process.yaml"
    manifest = yaml.safe_load(path.read_text())
    edit(manifest)
    path.write_text(yaml.safe_dump(manifest))
    report = _build(library, tmp_path / "out")
    assert any(message in e for e in report.errors), report.errors


def test_missing_sheet_file_is_an_error(library: Path, tmp_path: Path) -> None:
    (library / "processes" / "fixture-electrolysis" / "pid" / "P-01.xml").unlink()
    report = _build(library, tmp_path / "out")
    assert any("pid/P-01.xml, which does not exist" in e for e in report.errors)


def test_unknown_inventory_key_is_a_warning(library: Path, tmp_path: Path) -> None:
    path = library / "processes" / "fixture-electrolysis" / "process.yaml"
    manifest = yaml.safe_load(path.read_text())
    manifest["chemistry"]["outputs"][1]["inventory_key"] = "product:NOPE"
    path.write_text(yaml.safe_dump(manifest))
    report = _build(library, tmp_path / "out")
    assert report.errors == []
    assert any("product:NOPE" in w for w in report.warnings)


def test_graph_and_chemicals_link_processes(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "out")
    graph = _json(tmp_path / "out" / "graph.json")
    edges = {(e["source"], e["target"], e["role"]) for e in graph["edges"]}
    assert ("process:fixture-electrolysis", "chemical:hydrogen", "main-product") in edges
    assert ("chemical:hydrogen", "process:fixture-ammonia", "reactant") in edges
    node_ids = {n["id"] for n in graph["nodes"]}
    assert "chemical:unused-solvent" not in node_ids
    assert {s for s, _, _ in edges} | {t for _, t, _ in edges} <= node_ids
    hydrogen = next(c for c in _json(tmp_path / "out" / "chemicals.json")["chemicals"] if c["slug"] == "hydrogen")
    assert hydrogen["produced_by"] == [{"process": "fixture-electrolysis", "role": "main-product"}]
    assert hydrogen["consumed_by"] == [{"process": "fixture-ammonia", "role": "reactant"}]


def test_cli_exit_codes(library: Path, tmp_path: Path) -> None:
    assert build_catalog.main(["--library", str(LIBRARY), "--out", str(tmp_path / "a"), "--artifacts", str(PREVIEWS), "--commit", "x"]) == 0
    assert build_catalog.main(["--library", str(LIBRARY), "--out", str(tmp_path / "b"), "--artifacts", str(PREVIEWS), "--commit", "x", "--strict"]) == 1
    (library / "processes" / "fixture-ammonia" / "process.yaml").write_text("schema: wrong\n")
    assert build_catalog.main(["--library", str(library), "--out", str(tmp_path / "c"), "--commit", "x"]) == 1


SNAPSHOTS = FIXTURES / "snapshots"


def test_viewer_snapshot_is_copied_and_described(tmp_path: Path) -> None:
    report = build_catalog.build(LIBRARY, tmp_path / "out", PREVIEWS, commit="fixture", snapshots=SNAPSHOTS)
    assert report.errors == []
    detail = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")
    viewer = detail["viewer"]
    assert viewer["snapshot"] == "snapshots/fixture-electrolysis/"
    assert (tmp_path / "out" / viewer["snapshot"] / "manifest.json").is_file()
    assert viewer["sheets"] == ["process/BFD.xml", "process/PFD.xml"]
    assert "streams" in viewer["views"] and "layout" not in viewer["views"]
    assert viewer["tool"].startswith("cheme-as-code")
    assert viewer["stale"] is False  # no folder commit to compare with outside a repo
    summary = {p["id"]: p for p in _json(tmp_path / "out" / "catalog.json")["processes"]}
    assert summary["fixture-electrolysis"]["interactive"] is True
    assert summary["fixture-ammonia"]["interactive"] is False
    assert _json(tmp_path / "out" / "processes" / "fixture-ammonia.json")["viewer"] is None


def test_without_snapshots_there_is_no_viewer(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "out")
    assert _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["viewer"] is None


def test_stale_snapshot_and_wrong_schema(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    answers = {"rev-parse": str(LIBRARY), "log": "newer", "status": ""}
    monkeypatch.setattr(build_catalog, "_git", lambda library, *args: answers[args[0]])
    build_catalog.build(LIBRARY, tmp_path / "out", PREVIEWS, commit="fixture", snapshots=SNAPSHOTS)
    assert _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["viewer"]["stale"] is True

    snaps = tmp_path / "snaps"
    shutil.copytree(SNAPSHOTS, snaps)
    manifest = snaps / "fixture-electrolysis" / "manifest.json"
    manifest.write_text(manifest.read_text().replace("cheme/viewer-snapshot/v1", "cheme/viewer-snapshot/v9"))
    report = build_catalog.build(LIBRARY, tmp_path / "out2", PREVIEWS, commit="fixture", snapshots=snaps)
    assert any("viewer-snapshot/v9" in e for e in report.errors)


def test_snapshot_staleness_follows_git_ancestry(tmp_path: Path) -> None:
    """A later commit elsewhere keeps a snapshot current; a later change to the process does not."""
    import subprocess

    def git(*args: str) -> str:
        return subprocess.run(["git", "-C", str(library), *args], check=True, capture_output=True, text=True).stdout.strip()

    library = tmp_path / "library"
    shutil.copytree(LIBRARY, library)
    git("init", "-q", "-b", "main")
    git("-c", "user.email=t@e", "-c", "user.name=t", "add", "-A")
    git("-c", "user.email=t@e", "-c", "user.name=t", "commit", "-qm", "library")
    snaps = tmp_path / "snaps"
    shutil.copytree(SNAPSHOTS, snaps)
    manifest_path = snaps / "fixture-electrolysis" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    def stale_after(change: Path) -> bool:
        manifest["source"]["commit"] = git("rev-parse", "HEAD")  # exported now
        manifest_path.write_text(json.dumps(manifest))
        change.write_text(change.read_text() + "\n# later change\n")
        git("-c", "user.email=t@e", "-c", "user.name=t", "commit", "-qam", f"change {change.name}")
        out = tmp_path / f"out-{change.name}"
        build_catalog.build(library, out, PREVIEWS, commit=None, snapshots=snaps)
        return _json(out / "processes" / "fixture-electrolysis.json")["viewer"]["stale"]

    assert stale_after(library / "chemicals" / "chemicals.yaml") is False
    assert stale_after(library / "processes" / "fixture-electrolysis" / "process.yaml") is True


# --- public builds -----------------------------------------------------------------------------

import publication  # noqa: E402

ELECTROLYSIS = "processes/fixture-electrolysis/process.yaml"


def _public(library: Path, out: Path, snapshots: Path | None = SNAPSHOTS) -> build_catalog.Report:
    return build_catalog.build(library, out, PREVIEWS, commit="fixture", snapshots=snapshots, public=True)


def _edit(library: Path, rel: str, change) -> None:
    path = library / rel
    data = yaml.safe_load(path.read_text())
    change(data)
    path.write_text(yaml.safe_dump(data))


def test_public_build_lists_only_published_processes(tmp_path: Path) -> None:
    report = _public(LIBRARY, tmp_path / "out")
    assert report.errors == []
    out = tmp_path / "out"
    catalog = _json(out / "catalog.json")
    assert catalog["mode"] == "public"
    assert [p["id"] for p in catalog["processes"]] == ["fixture-electrolysis"]
    assert sorted(p.name for p in (out / "processes").iterdir()) == ["fixture-electrolysis.json"]
    # fixture-ammonia (internal) is gone from the chemicals' uses and the graph too
    chemicals = {c["slug"]: c for c in _json(out / "chemicals.json")["chemicals"]}
    assert chemicals["hydrogen"]["consumed_by"] == []
    assert chemicals["ammonia"]["produced_by"] == []
    text = "".join(p.read_text() for p in out.rglob("*.json"))
    assert "fixture-ammonia" not in text
    node_ids = {n["id"] for n in _json(out / "graph.json")["nodes"]}
    assert "chemical:ammonia" not in node_ids and "chemical:hydrogen" in node_ids
    assert catalog["chemical_count"] == len([n for n in node_ids if n.startswith("chemical:")])


@pytest.mark.parametrize("status", ["internal", "candidate", None])
def test_only_status_public_is_published(library: Path, tmp_path: Path, status) -> None:
    _edit(library, ELECTROLYSIS, lambda m: m["publication"].update(status=status) if status else m.pop("publication"))
    report = _public(library, tmp_path / "out")
    assert report.errors == []
    assert _json(tmp_path / "out" / "catalog.json")["processes"] == []
    assert not (tmp_path / "out" / "snapshots").exists()
    assert not (tmp_path / "out" / "artifacts").exists()


def test_public_build_of_a_library_without_public_processes_succeeds(library: Path, tmp_path: Path, capsys) -> None:
    _edit(library, ELECTROLYSIS, lambda m: m["publication"].update(status="internal"))
    assert build_catalog.main(["--library", str(library), "--out", str(tmp_path / "out"), "--commit", "x", "--public"]) == 0
    assert "0 process(es)" in capsys.readouterr().out


@pytest.mark.parametrize(("access", "kept"), [("private", False), (None, False), ("public", True)])
def test_repository_is_dropped_unless_public(library: Path, tmp_path: Path, access, kept: bool) -> None:
    repository = {"url": "https://github.com/ChemE-as-Code/process-library", "path": "processes/fixture-electrolysis"}
    if access:
        repository["access"] = access
    _edit(library, ELECTROLYSIS, lambda m: m.update(repository=repository))
    _public(library, tmp_path / "pub")
    detail = _json(tmp_path / "pub" / "processes" / "fixture-electrolysis.json")
    assert detail["repository"] == (repository if kept else None)
    if not kept:
        assert "github.com" not in "".join(p.read_text() for p in (tmp_path / "pub").rglob("*.json"))
    _build(library, tmp_path / "preview")  # the preview build shows the library as it is
    assert _json(tmp_path / "preview" / "processes" / "fixture-electrolysis.json")["repository"] == repository


def test_publication_excludes_are_not_published(tmp_path: Path) -> None:
    _public(LIBRARY, tmp_path / "out")
    detail = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")
    assert detail["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_placeholder_footprints_are_withheld(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "preview")
    _public(LIBRARY, tmp_path / "pub")
    full = _json(tmp_path / "preview" / "processes" / "fixture-electrolysis.json")["lca"]
    lca = _json(tmp_path / "pub" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["values_withheld"] == "placeholder-factors"
    assert "totals" not in lca and "contributions" not in lca
    for key in ("goal", "functional_unit", "boundary", "allocation", "backend", "factors_status", "categories", "inventory", "sources"):
        assert lca[key] == full[key], key
    assert lca["inventory"] and lca["categories"]

    summary = _json(tmp_path / "pub" / "catalog.json")["processes"][0]["lca"]
    preview = next(p for p in _json(tmp_path / "preview" / "catalog.json")["processes"] if p["id"] == "fixture-electrolysis")["lca"]
    assert preview["value"] == 24.0 and "values_withheld" not in preview
    assert summary == {**preview, "value": None, "values_withheld": "placeholder-factors"}


def test_published_factors_are_shown(library: Path, tmp_path: Path) -> None:
    _edit(library, "processes/fixture-electrolysis/lca/factors.yaml", lambda f: f.pop("example"))
    rows = library / "processes" / "fixture-electrolysis" / "lca" / "results.csv"
    rows.write_text(rows.read_text().replace("ASSUMED", "PUBLISHED"))
    _public(library, tmp_path / "out")
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["factors_status"] != "placeholder"
    assert lca["totals"] == {"baseline": {"climate-change": 24.0}} and "values_withheld" not in lca
    assert _json(tmp_path / "out" / "catalog.json")["processes"][0]["lca"]["value"] == 24.0


def _snapshots(tmp_path: Path, change) -> Path:
    snaps = tmp_path / "snaps"
    shutil.copytree(SNAPSHOTS, snaps)
    path = snaps / "fixture-electrolysis" / "manifest.json"
    manifest = json.loads(path.read_text())
    change(manifest, snaps / "fixture-electrolysis")
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return snaps


def test_the_fixture_snapshot_was_exported_for_publication() -> None:
    manifest = _json(SNAPSHOTS / "fixture-electrolysis" / "manifest.json")
    process = yaml.safe_load((LIBRARY / ELECTROLYSIS).read_text())
    assert set(publication.snapshot_excludes(process)) <= set(manifest["excluded"])


@pytest.mark.parametrize(
    "change",
    [
        lambda m, _: m.pop("excluded"),  # an export before --exclude existed
        lambda m, _: m["excluded"].remove("reviews/**"),  # a default missing
        lambda m, _: m["excluded"].remove("docs/private/**"),  # the process's own glob missing
    ],
    ids=["none", "default", "own"],
)
def test_snapshot_not_exported_for_publication_is_an_error(tmp_path: Path, change) -> None:
    snaps = _snapshots(tmp_path, change)
    report = _public(LIBRARY, tmp_path / "out", snaps)
    assert any("snapshot was not exported for publication" in e for e in report.errors), report.errors
    assert not (tmp_path / "out" / "snapshots").exists()
    assert _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["viewer"] is None
    # the preview build does not ask
    assert build_catalog.build(LIBRARY, tmp_path / "preview", PREVIEWS, commit="x", snapshots=snaps).errors == []


def _with_lca_answers(manifest: dict, folder: Path) -> None:
    for key, name in [("lca", "lca.json"), ("file?path=lca/results.csv", "results.txt"), ("file?path=lca/lca.yaml", "study.txt")]:
        (folder / "data" / name).write_text("climate-change,24.0\n")
        manifest["entries"][key] = {"file": name, "status": 200, "type": "application/json"}


def test_placeholder_lca_answers_are_removed_from_the_snapshot(tmp_path: Path) -> None:
    snaps = _snapshots(tmp_path, _with_lca_answers)
    assert _public(LIBRARY, tmp_path / "out", snaps).errors == []
    target = tmp_path / "out" / "snapshots" / "fixture-electrolysis"
    manifest = _json(target / "manifest.json")
    assert "lca" not in manifest["entries"] and "file?path=lca/results.csv" not in manifest["entries"]
    assert not (target / "data" / "lca.json").exists() and not (target / "data" / "results.txt").exists()
    assert manifest["entries"]["file?path=lca/lca.yaml"]["file"] == "study.txt"  # the study is not a value
    assert all((target / "data" / e["file"]).is_file() for e in manifest["entries"].values())
    viewer = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["viewer"]
    assert "lca" not in viewer["views"]
    # the source snapshot is untouched, and the preview build keeps the answer
    assert "lca" in _json(snaps / "fixture-electrolysis" / "manifest.json")["entries"]
    build_catalog.build(LIBRARY, tmp_path / "preview", PREVIEWS, commit="x", snapshots=snaps)
    assert "lca" in _json(tmp_path / "preview" / "processes" / "fixture-electrolysis.json")["viewer"]["views"]


def test_published_lca_answer_stays_in_the_snapshot(library: Path, tmp_path: Path) -> None:
    _edit(library, "processes/fixture-electrolysis/lca/factors.yaml", lambda f: f.pop("example"))
    snaps = _snapshots(tmp_path, _with_lca_answers)
    assert _public(library, tmp_path / "out", snaps).errors == []
    manifest = _json(tmp_path / "out" / "snapshots" / "fixture-electrolysis" / "manifest.json")
    assert "lca" in manifest["entries"] and "file?path=lca/results.csv" in manifest["entries"]


def test_public_build_is_byte_identical(tmp_path: Path) -> None:
    _public(LIBRARY, tmp_path / "a")
    _public(LIBRARY, tmp_path / "b")
    files = sorted(p.relative_to(tmp_path / "a") for p in (tmp_path / "a").rglob("*") if p.is_file())
    assert files == sorted(p.relative_to(tmp_path / "b") for p in (tmp_path / "b").rglob("*") if p.is_file())
    for rel in files:
        assert (tmp_path / "a" / rel).read_bytes() == (tmp_path / "b" / rel).read_bytes(), rel
