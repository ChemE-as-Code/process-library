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
        used = {f["chemical"].split("/")[0] for flows in chemistry.values() for f in flows}
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


def _run_manifest(library: Path, pid: str, publication: str = "public", publishable: bool = True) -> None:
    """core's run manifest (lca/manifest.json) with the result's policy (only what is read)."""
    path = library / "processes" / pid / "lca" / "manifest.json"
    result = {"classification": "screening", "label": "screening carbon footprint", "gaps": 0,
              "publication": publication, "publishable": publishable}
    path.write_text(json.dumps({"schema": "cheme/lca-manifest/v1", "result": result}))


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
    # without core's run manifest nothing says the sources permit publication
    _public(library, tmp_path / "out")
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["values_withheld"] == "no-run-manifest" and "totals" not in lca
    _run_manifest(library, "fixture-electrolysis")
    _public(library, tmp_path / "out2")
    lca = _json(tmp_path / "out2" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["factors_status"] != "placeholder"
    assert lca["totals"] == {"baseline": {"climate-change": 24.0}} and "values_withheld" not in lca
    assert lca["result"]["label"] == "screening carbon footprint" and lca["publishable"]
    assert _json(tmp_path / "out2" / "catalog.json")["processes"][0]["lca"]["value"] == 24.0


def test_restricted_sources_are_withheld(library: Path, tmp_path: Path) -> None:
    # e.g. a licensed database behind the results: published factors do not make them public
    _edit(library, "processes/fixture-electrolysis/lca/factors.yaml", lambda f: f.pop("example"))
    _run_manifest(library, "fixture-electrolysis", "restricted", publishable=False)
    snaps = _snapshots(tmp_path, _with_lca_answers)
    assert _public(library, tmp_path / "out", snaps).errors == []
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["values_withheld"] == "restricted-sources"
    assert "totals" not in lca and "contributions" not in lca
    summary = _json(tmp_path / "out" / "catalog.json")["processes"][0]["lca"]
    assert summary["value"] is None and summary["values_withheld"] == "restricted-sources"
    manifest = _json(tmp_path / "out" / "snapshots" / "fixture-electrolysis" / "manifest.json")
    assert "lca" not in manifest["entries"] and "file?path=lca/results.csv" not in manifest["entries"]


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
        lambda m, _: m["excluded"].remove("runs/**"),  # the run records missing
        lambda m, _: m["excluded"].remove("docs/private/**"),  # the process's own glob missing
    ],
    ids=["none", "default", "runs", "own"],
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
    _run_manifest(library, "fixture-electrolysis")
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


# --- facets ------------------------------------------------------------------------------------

EMPTY_FACETS = {"feedstock_basis": [], "product_classes": [], "unit_operations": [], "region": None}


def test_facets_are_in_summary_and_detail(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "out")
    summaries = {p["id"]: p for p in _json(tmp_path / "out" / "catalog.json")["processes"]}
    electrolysis = {
        "feedstock_basis": ["water", "electricity"],
        "product_classes": ["industrial-gases", "fuels"],
        "unit_operations": ["electrolysis"],
        "region": "generic",
    }
    assert summaries["fixture-electrolysis"]["facets"] == electrolysis
    assert _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["facets"] == electrolysis
    # partial facets are completed: missing lists [], missing region null
    ammonia = {**EMPTY_FACETS, "product_classes": ["fertilizers"], "unit_operations": ["reaction"]}
    assert summaries["fixture-ammonia"]["facets"] == ammonia
    assert _json(tmp_path / "out" / "processes" / "fixture-ammonia.json")["facets"] == ammonia


def test_process_without_facets_gets_empty_facets(library: Path, tmp_path: Path) -> None:
    _edit(library, "processes/fixture-ammonia/process.yaml", lambda m: m.pop("facets"))
    assert _build(library, tmp_path / "out").errors == []
    summary = next(p for p in _json(tmp_path / "out" / "catalog.json")["processes"] if p["id"] == "fixture-ammonia")
    assert summary["facets"] == EMPTY_FACETS
    assert _json(tmp_path / "out" / "processes" / "fixture-ammonia.json")["facets"] == EMPTY_FACETS


def test_public_build_keeps_facets(tmp_path: Path) -> None:
    _build(LIBRARY, tmp_path / "preview")
    _public(LIBRARY, tmp_path / "pub")
    preview = next(p for p in _json(tmp_path / "preview" / "catalog.json")["processes"] if p["id"] == "fixture-electrolysis")
    assert _json(tmp_path / "pub" / "catalog.json")["processes"][0]["facets"] == preview["facets"]
    rel = Path("processes") / "fixture-electrolysis.json"
    assert _json(tmp_path / "pub" / rel)["facets"] == _json(tmp_path / "preview" / rel)["facets"]


@pytest.mark.parametrize(
    "facets",
    [{"feedstock_basis": ["coal"]}, {"unit_operations": ["Cryogenic Distillation"]}, {"colour": "green"}],
    ids=["bad-feedstock", "not-a-slug", "unknown-key"],
)
def test_bad_facets_are_schema_errors(library: Path, tmp_path: Path, facets: dict) -> None:
    _edit(library, "processes/fixture-ammonia/process.yaml", lambda m: m.update(facets=facets))
    assert any("facets" in e for e in _build(library, tmp_path / "out").errors)


def test_a_stale_run_manifest_withholds(library: Path, tmp_path: Path) -> None:
    import hashlib

    from publication import lca_withheld

    folder = library / "processes" / "fixture-electrolysis"
    _edit(library, "processes/fixture-electrolysis/lca/factors.yaml", lambda f: f.pop("example"))
    _run_manifest(library, "fixture-electrolysis")
    path = folder / "lca" / "manifest.json"
    run = json.loads(path.read_text())
    lca = (folder / "lca" / "lca.yaml").read_bytes()
    run["inputs"] = {"lca/lca.yaml": "sha256:" + hashlib.sha256(lca).hexdigest()}
    path.write_text(json.dumps(run))
    assert lca_withheld(folder) is None
    # the scope changed after the run: the manifest describes another run
    (folder / "lca" / "lca.yaml").write_text((folder / "lca" / "lca.yaml").read_text() + "\n# changed\n")
    assert lca_withheld(folder) == "stale-run-manifest"
    # another backend than the run's
    run["inputs"] = {}
    run["background"] = {"backend": "brightway"}
    path.write_text(json.dumps(run))
    assert lca_withheld(folder) == "stale-run-manifest"



def test_results_written_by_another_run_withhold(library: Path) -> None:
    import hashlib

    from publication import lca_withheld

    folder = library / "processes" / "fixture-electrolysis"
    _edit(library, "processes/fixture-electrolysis/lca/factors.yaml", lambda f: f.pop("example"))
    _run_manifest(library, "fixture-electrolysis")
    path = folder / "lca" / "manifest.json"
    run = json.loads(path.read_text())
    csv_path = folder / "lca" / "results.csv"
    csv_path.write_text("category,total\ngwp,1\n")
    run["results"] = "sha256:" + hashlib.sha256(csv_path.read_bytes()).hexdigest()
    path.write_text(json.dumps(run))
    assert lca_withheld(folder) is None
    csv_path.write_bytes(b"category,total\r\ngwp,1\r\n")  # another checkout's line endings
    assert lca_withheld(folder) is None
    csv_path.write_text("category,total\ngwp,0.1\n")  # written by another run
    assert lca_withheld(folder) == "stale-run-manifest"
    csv_path.unlink()
    assert lca_withheld(folder) == "stale-run-manifest"
    run.pop("results")  # a manifest of an older core is not checked
    path.write_text(json.dumps(run))
    assert lca_withheld(folder) is None


def test_data_sources_carry_the_attribution(library: Path, tmp_path: Path) -> None:
    _edit(library, "processes/fixture-electrolysis/lca/factors.yaml", lambda f: f.pop("example"))
    _run_manifest(library, "fixture-electrolysis")
    path = library / "processes" / "fixture-electrolysis" / "lca" / "manifest.json"
    run = json.loads(path.read_text())
    run["background"] = {
        "backend": "factors",
        "sources": [
            {"id": "desnz-ghg-2026", "title": "UK GHG Conversion Factors 2026", "provider": "DESNZ",
             "version": "2026 v1.2", "url": "https://www.gov.uk/", "licence": "OGL-3.0",
             "attribution": "Contains public sector information licensed under the OGL v3.0.",
             "checksum": "sha256:x", "publication": "public"}
        ],
    }
    path.write_text(json.dumps(run))
    _public(library, tmp_path / "out")
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    (source,) = lca["data_sources"]
    assert source["licence"] == "OGL-3.0" and "OGL v3.0" in source["attribution"]
    assert "checksum" not in source and lca["totals"]


# -- design cases and regional scenarios (core#172) -----------------------------------------


def _scenarios(out: Path) -> dict:
    return _json(out / "processes" / "fixture-electrolysis.json")["lca"]


def test_scenarios_reuse_one_design_and_keep_their_states(tmp_path: Path, library: Path) -> None:
    assert _build(library, tmp_path / "out").errors == []
    lca = _scenarios(tmp_path / "out")
    assert [c["id"] for c in lca["design_cases"]] == ["design", "part-load"]
    assert lca["technology"] == "PEM electrolysis (fixture)"
    design = lca["design_cases"][0]
    assert design["capacity"] == "1 t/d H2" and design["foreground"]["basis"] == "1 h of operation"
    by_id = {s["id"]: s for s in lca["scenarios"]}
    assert list(by_id) == ["baseline", "de-grid", "nl-grid", "part-load"]
    # a region swap keeps the design case and the foreground
    for sid in ("nl-grid", "de-grid"):
        assert by_id[sid]["design_case"] == "design"
        assert by_id[sid]["relation"] == "unchanged"
        assert by_id[sid]["foreground_fingerprint"] == by_id["baseline"]["foreground_fingerprint"]
    assert by_id["part-load"]["relation"] == "design-case"
    assert by_id["part-load"]["foreground_fingerprint"] != by_id["baseline"]["foreground_fingerprint"]
    nl_power = next(l for l in by_id["nl-grid"]["links"] if l["key"] == "feed:POWER")
    assert (nl_power["state"], nl_power["location"], nl_power["replaced"]) == ("linked", "NL", True)
    # missing regional data: a missing state and a non-comparable total, never a zero footprint
    de = by_id["de-grid"]
    assert next(l for l in de["links"] if l["key"] == "feed:POWER")["state"] == "missing"
    assert (de["comparable"], de["dropped"]) == (False, ["feed:POWER"])
    assert de["totals"] == {"climate-change": None}
    assert de["layers"] == {
        "foreground": "foreground",
        "linked_inventory": "linked-inventory",
        "impacts": "characterized-impact",
    }
    assert de["allocation"]["method"] == "mass" and de["functional_unit"]["product"] == "H2"
    # the study boundary beside every scenario; core's comparability verdict (core#306) and each
    # link's scope pass through; a record without a verdict gives null (de-grid: still not
    # comparable through its gaps, `comparable` false)
    assert de["boundary"] == lca["boundary"]
    assert de["comparability"] is None
    assert by_id["nl-grid"]["comparability"]["verdict"] == "not comparable"
    assert by_id["nl-grid"]["comparability"]["compared"][0]["differences"][0]["dimension"] == "basis"
    assert nl_power["scope"]["basis"] == "direct"
    assert next(l for l in de["links"] if l["key"] == "feed:POWER")["scope"] is None
    # the full core record is copied for other consumers
    record = _json(tmp_path / "out" / de["record"])
    assert record["schema"] == "cheme/lca-scenario/v1" and record["id"] == de["record_id"]


def test_public_build_withholds_scenario_values_not_their_evidence(tmp_path: Path, library: Path) -> None:
    assert build_catalog.build(library, tmp_path / "out", PREVIEWS, commit="fixture", public=True).errors == []
    lca = _scenarios(tmp_path / "out")
    for scenario in lca["scenarios"]:
        # the fixture's factors are placeholders: no numbers, but geography, states and gaps stay
        assert "totals" not in scenario
        assert scenario["values_withheld"] == "placeholder-factors"
        assert scenario["links"]
        record = _json(tmp_path / "out" / scenario["record"])
        assert "totals" not in record["impacts"] and "characterised_sum" not in record["impacts"]
        assert record["impacts"]["values_withheld"] == "placeholder-factors"
    # the verdict holds no numbers: it stays on a withheld scenario
    nl = next(s for s in lca["scenarios"] if s["id"] == "nl-grid")
    assert nl["comparability"]["verdict"] == "not comparable"


def test_a_stale_scenario_record_is_flagged_and_withheld(tmp_path: Path, library: Path) -> None:
    lca_yaml = library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml"
    lca_yaml.write_text(lca_yaml.read_text() + "# changed\n")
    report = _build(library, tmp_path / "out")
    assert any("nl-grid.json is stale" in w for w in report.warnings)
    nl = next(s for s in _scenarios(tmp_path / "out")["scenarios"] if s["id"] == "nl-grid")
    assert nl["stale"] is True


def test_a_process_without_scenario_records_has_no_scenarios(tmp_path: Path, library: Path) -> None:
    shutil.rmtree(library / "processes" / "fixture-electrolysis" / "lca" / "scenarios")
    assert _build(library, tmp_path / "out").errors == []
    lca = _scenarios(tmp_path / "out")
    assert "scenarios" not in lca and "design_cases" not in lca and "technology" not in lca


def test_the_asu_publishes_regional_scenarios_on_sourced_factors() -> None:
    folder = KIT / "processes" / "asu-1" / "lca" / "scenarios"
    records = {p.stem: _json(p) for p in folder.glob("*.json")}
    assert set(records) == {"baseline", "nl-grid", "de-grid"}
    fingerprints = {r["foreground"]["fingerprint"] for r in records.values()}
    assert len(fingerprints) == 1  # one 500 t/d design, one foreground
    assert {r["design_case"]["id"] for r in records.values()} == {"design"}
    power = {k: next(l for l in r["linked_inventory"]["exchanges"] if l["key"] == "feed:POWER") for k, r in records.items()}
    # NL and DE: the packaged EEA 2024 factors of their own country, declared proxies for the
    # scope (generation-based, no T&D or upstream) against the UK baseline at the consumer (D-101)
    for sid, code in (("nl-grid", "NL"), ("de-grid", "DE")):
        assert power[sid]["background"] == f"eea-ener038-2024:electricity-{code.lower()}"
        assert (power[sid]["state"], power[sid]["location"], power[sid]["year"]) == ("proxy", code, 2024)
        assert power[sid]["replaced"] is True
        assert records[sid]["impacts"]["comparable"] is True
        assert records[sid]["impacts"]["totals"]["climate-change"] > records["baseline"]["impacts"]["totals"]["climate-change"]
    assert not build_catalog._record_stale(KIT / "processes" / "asu-1", records["nl-grid"])


def test_lca_totals_drop_scenario_categories_a_record_says_are_not_computable(tmp_path: Path, library: Path) -> None:
    # a record whose total is null (data the baseline has is missing there): the catalog must not
    # show results.csv's lower sum for it
    folder = library / "processes" / "fixture-electrolysis"
    (folder / "lca" / "results.csv").write_text(
        (folder / "lca" / "results.csv").read_text()
        + "de-grid,climate-change,kg CO2-eq,total,,,,,0.05,1.0000,,,,\n"
    )
    report = build_catalog.Report()
    lca = build_catalog._lca(folder, "fixture", report)
    assert lca["totals"]["de-grid"] == {}
    assert lca["totals"]["baseline"]


def test_a_withheld_scenario_loses_its_lca_totals_too(tmp_path: Path, library: Path) -> None:
    detail = {
        "repository": None,
        "publication": None,
        "lca": {
            "publishable": True,
            "totals": {"baseline": {"gwp": 1.0}, "nl": {"gwp": 2.0}},
            "scenarios": [
                {"id": "baseline", "withheld_reason": None, "totals": {"gwp": 1.0}},
                {"id": "nl", "withheld_reason": "restricted-sources", "totals": {"gwp": 2.0}},
            ],
        },
    }
    build_catalog._publish(detail)
    assert detail["lca"]["totals"] == {"baseline": {"gwp": 1.0}}
    assert "totals" not in detail["lca"]["scenarios"][1]


def test_snapshot_withholding_covers_scenario_records(tmp_path: Path) -> None:
    target = tmp_path / "snap"
    (target / "data").mkdir(parents=True)
    entries = {}
    for key in ("lca", "file?path=lca/results.csv", "file?path=lca/scenarios/nl.json", "file?path=lca/dataset.yaml"):
        name = key.replace("?", "_").replace("/", "_")
        (target / "data" / name).write_text("x")
        entries[key] = {"file": name}
    manifest = {"entries": entries}
    build_catalog._withhold_lca_values(manifest, target)
    assert set(manifest["entries"]) == {"file?path=lca/dataset.yaml"}


def test_a_malformed_scenario_record_is_a_warning(tmp_path: Path, library: Path) -> None:
    bad = library / "processes" / "fixture-electrolysis" / "lca" / "scenarios" / "broken.json"
    bad.write_text(json.dumps({"schema": "cheme/lca-scenario/v1", "id": "x"}))
    report = _build(library, tmp_path / "out")
    assert report.errors == []
    assert any("broken.json: not a complete scenario record" in w for w in report.warnings)


def test_a_single_undeclared_design_case_shows_the_documented_capacity() -> None:
    report = build_catalog.Report()
    lca = build_catalog._lca(KIT / "processes" / "asu-1", "asu-1", report, "500 t/d GOX")
    (case,) = lca["design_cases"]
    assert (case["capacity"], case["capacity_source"]) == ("500 t/d GOX", "process.yaml basis.capacity")


# -- issues (fetch_issues.py output) ---------------------------------------------------------------

ISSUES = {
    "schema": "process-library/issues/v1",
    "repository": "o/library",
    "private": True,
    "web": "https://github.com/o/library",
    "issues": [
        {"number": 1, "title": "Fail positions", "state": "open", "status": "open", "type": "hold", "gate": "basic",
         "disciplines": ["control"], "source": "hazop", "waiting": "input", "processes": ["fixture-electrolysis"],
         "url": "https://github.com/o/library/issues/1", "updated": "2026-10-25T00:00:00Z", "closed": None},
        {"number": 2, "title": "Old action", "state": "closed", "status": "closed", "type": "action", "gate": "concept",
         "disciplines": [], "source": None, "waiting": None, "processes": ["fixture-electrolysis"],
         "url": "https://github.com/o/library/issues/2", "updated": "2026-10-25T00:00:00Z", "closed": "2026-10-25T00:00:00Z"},
        {"number": 3, "title": "Elsewhere", "state": "open", "status": "open", "type": "tq", "gate": None,
         "disciplines": [], "source": None, "waiting": None, "processes": ["fixture-ammonia"],
         "url": "https://github.com/o/library/issues/3", "updated": "2026-10-25T00:00:00Z", "closed": None},
    ],
}


def _with_issues(library: Path, tmp_path: Path, public: bool = False) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    issues = tmp_path / "issues.json"
    issues.write_text(json.dumps(ISSUES))
    forms = library / ".github" / "ISSUE_TEMPLATE"
    forms.mkdir(parents=True, exist_ok=True)
    (forms / "2-engineering-hold.yml").write_text('name: Engineering hold\nlabels: ["type:hold"]\nbody: []\n')
    out = tmp_path / ("public" if public else "out")
    report = build_catalog.build(library, out, PREVIEWS, commit="fixture", public=public, issues=issues)
    assert not report.errors, report.errors
    return out


def test_without_issues_nothing_is_added(tmp_path: Path) -> None:
    out = tmp_path / "out"
    _build(LIBRARY, out)
    assert _json(out / "processes" / "fixture-electrolysis.json")["issues"] is None
    assert all(p["open_issues"] is None for p in _json(out / "catalog.json")["processes"])


def test_each_process_gets_its_open_items(library: Path, tmp_path: Path) -> None:
    out = _with_issues(library, tmp_path)
    issues = _json(out / "processes" / "fixture-electrolysis.json")["issues"]
    assert [i["number"] for i in issues["open"]] == [1]
    assert issues["open"][0]["type"] == "hold" and issues["open"][0]["gate"] == "basic"
    assert issues["closed_count"] == 1 and issues["open_by_gate"] == {"basic": {"hold": 1}}
    assert issues["new"]["hold"].startswith("https://github.com/o/library/issues/new?template=2-engineering-hold.yml")
    assert "process=fixture-electrolysis" in issues["new"]["hold"]
    summaries = {p["id"]: p for p in _json(out / "catalog.json")["processes"]}
    assert summaries["fixture-electrolysis"]["open_issues"] == 1
    assert summaries["fixture-ammonia"]["open_issues"] == 1


def test_public_build_keeps_titles_but_no_links_into_a_private_repository(library: Path, tmp_path: Path) -> None:
    out = _with_issues(library, tmp_path, public=True)
    issues = _json(out / "processes" / "fixture-electrolysis.json")["issues"]
    assert issues["open"][0]["title"] == "Fail positions" and issues["open"][0]["url"] is None
    assert issues["new"] is None and issues["list_url"] is None and issues["repository"] is None


def test_issues_build_is_byte_identical(library: Path, tmp_path: Path) -> None:
    first = _with_issues(library, tmp_path / "a")
    second = _with_issues(library, tmp_path / "b")
    name = "processes/fixture-electrolysis.json"
    assert (first / name).read_bytes() == (second / name).read_bytes()


def test_issues_of_another_schema_are_refused(library: Path, tmp_path: Path) -> None:
    issues = tmp_path / "issues.json"
    issues.write_text(json.dumps({**ISSUES, "schema": "x"}))
    report = build_catalog.build(library, tmp_path / "out", PREVIEWS, commit="fixture", issues=issues)
    assert report.errors


def test_fetched_issue_counts_at_its_earliest_gate():
    import fetch_issues

    item = {
        "number": 9, "title": "t", "state": "open", "html_url": "u", "updated_at": "", "closed_at": None,
        "labels": [{"name": n} for n in ("process:p", "type:hold", "gate:detail", "gate:basic")],
    }
    assert fetch_issues.record(item)["gate"] == "basic"


def test_issue_forms_are_read_as_yaml(tmp_path: Path):
    forms = tmp_path / ".github" / "ISSUE_TEMPLATE"
    forms.mkdir(parents=True)
    (forms / "a.yml").write_text("name: A\nlabels: [type:action, other]\nbody: []\n")
    (forms / "b.yml").write_text('name: B\nlabels: "type:hold"\nbody: []\n')
    (forms / "config.yml").write_text("blank_issues_enabled: true\n")
    assert build_catalog._issue_forms(tmp_path) == {"action": "a.yml", "hold": "b.yml"}


# --- issue #250: a category whose every contribution is a gap has no total, never 0 (ADR 0026) ---

#: core's lca/results.csv of a study whose every exchange is a gap: a total row of 0 and nothing else
GAP_ONLY_RESULTS = (
    "scenario,category,category_unit,key,basis,quantity,unit,factor,impact,share,phase,status,source,year\n"
    "baseline,climate-change,kg CO2-eq,total,,,,,0,,,,,\n"
)
GAPS_HEADER = "scenario,category,key,reason,quantity,unit,phase,detail\n"


def _results(folder: Path, results: str, gaps: str | None) -> None:
    (folder / "lca" / "results.csv").write_text(results)
    if gaps is not None:
        (folder / "lca" / "gaps.csv").write_text(GAPS_HEADER + gaps)


def test_a_category_whose_every_contribution_is_a_gap_has_no_total(library: Path, tmp_path: Path) -> None:
    folder = library / "processes" / "fixture-electrolysis"
    shutil.rmtree(folder / "lca" / "scenarios")
    (folder / "lca" / "factors.yaml").write_text(
        "kind: lca_factors\ncategories:\n  - {id: climate-change, title: Climate change, unit: kg CO2-eq, method: GWP100}\n"
    )
    _results(
        folder,
        GAP_ONLY_RESULTS,
        "baseline,climate-change,feed:POWER,missing,55,kWh,operation,background to link\n"
        "baseline,climate-change,emission:N2,elementary-uncharacterised,0.1,kg,operation,\n",
    )
    assert _build(library, tmp_path / "out").errors == []
    lca = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")["lca"]
    assert lca["totals"] == {"baseline": {}}
    # the unknown burden is counted once per exchange; a flow outside the method is no gap here
    assert lca["not_computed"] == {"baseline": {"climate-change": {"reason": "every-contribution-a-gap", "gaps": 1}}}
    assert lca["contributions"] == [] and lca["factors_status"] == "none"
    headline = next(p for p in _json(tmp_path / "out" / "catalog.json")["processes"] if p["id"] == "fixture-electrolysis")["lca"]
    assert headline["value"] is None and headline["not_computed"] == "every-contribution-a-gap"


def test_a_real_zero_stays_zero(library: Path, tmp_path: Path) -> None:
    # no gap that leaves a burden unknown: 0 is the result (e.g. only flows outside the method)
    folder = library / "processes" / "fixture-electrolysis"
    for gaps in (None, "baseline,climate-change,emission:N2,elementary-uncharacterised,0.1,kg,operation,\n"):
        _results(folder, GAP_ONLY_RESULTS, gaps)
        lca = build_catalog._lca(folder, "fixture", build_catalog.Report())
        assert lca["totals"]["baseline"] == {"climate-change": 0.0}
        assert lca["not_computed"] == {}


def test_a_category_with_contributions_keeps_its_total_beside_its_gaps(library: Path) -> None:
    folder = library / "processes" / "fixture-electrolysis"
    (folder / "lca" / "gaps.csv").write_text(GAPS_HEADER + "baseline,climate-change,feed:WATER,missing,9,kg,operation,\n")
    lca = build_catalog._lca(folder, "fixture", build_catalog.Report())
    assert lca["totals"]["baseline"] == {"climate-change": 24.0}
    assert lca["not_computed"] == {}


def test_the_pcf_breakdown_is_not_an_impact_category(library: Path) -> None:
    # core writes the PCF breakdown as rows of category pcf in mixed units (kg CO2-eq, kg C,
    # kg CO2): they are lines of their own, never summed into a total or listed as contributions
    folder = library / "processes" / "fixture-electrolysis"
    results = folder / "lca" / "results.csv"
    results.write_text(
        results.read_text()
        + "baseline,pcf,kg CO2-eq,fossil,climate-change,,,,24,,,,,\n"
        + "baseline,pcf,kg C,product_carbon,climate-change,,,,0.4,,,,,\n"
    )
    lca = build_catalog._lca(folder, "fixture", build_catalog.Report())
    assert [c["id"] for c in lca["categories"]] == ["climate-change"]
    assert lca["totals"]["baseline"] == {"climate-change": 24.0}
    assert {c["category"] for c in lca["contributions"]} == {"climate-change"}
    assert lca["pcf"] == [
        {"key": "fossil", "basis": "climate-change", "value": 24.0, "unit": "kg CO2-eq"},
        {"key": "product_carbon", "basis": "climate-change", "value": 0.4, "unit": "kg C"},
    ]
    # a withheld LCA loses its PCF numbers with its totals
    detail = {"repository": None, "publication": None, "lca": {**lca, "publishable": False, "withheld_reason": "placeholder-factors"}}
    build_catalog._publish(detail)
    assert "pcf" not in detail["lca"] and "totals" not in detail["lca"]
    assert "not_computed" not in detail["lca"]  # its gap counts come from lca/gaps.csv


def test_the_pcf_impact_lines_of_a_gap_only_category_are_unknown(library: Path) -> None:
    # glycerol-1 (#250): fossil 0 and "including" -1.08 (biogenic withdrawal only) beside a
    # climate total that does not exist; the carbon content of the product stays a fact
    folder = library / "processes" / "fixture-electrolysis"
    _results(
        folder,
        GAP_ONLY_RESULTS
        + "baseline,pcf,kg CO2-eq,fossil,climate-change,,,,0,,,,,\n"
        + "baseline,pcf,kg CO2-eq,including,climate-change,,,,-1.07551,,,,,\n"
        + "baseline,pcf,kg C,product_carbon,climate-change,,,,0.39,,,,,\n",
        "baseline,climate-change,feed:POWER,missing,55,kWh,operation,background to link\n",
    )
    lca = build_catalog._lca(folder, "fixture", build_catalog.Report())
    reason = "every-contribution-a-gap"
    assert lca["pcf"] == [
        {"key": "fossil", "basis": "climate-change", "value": None, "unit": "kg CO2-eq", "not_computed": reason},
        {"key": "including", "basis": "climate-change", "value": None, "unit": "kg CO2-eq", "not_computed": reason},
        {"key": "product_carbon", "basis": "climate-change", "value": 0.39, "unit": "kg C"},
    ]


def test_the_shipped_library_reports_no_gap_only_total_as_zero(tmp_path: Path) -> None:
    # read from the raw files, independently of _not_computed: every shipped baseline category
    # with a gap that leaves a burden unknown and no contribution row has no total (#250)
    gap_only = []
    for folder in sorted((KIT / "processes").glob("*/lca/results.csv")):
        process = folder.parents[1]
        lca = build_catalog._lca(process, process.name, build_catalog.Report())
        gaps_csv = folder.parent / "gaps.csv"
        gapped = set()
        if gaps_csv.is_file():
            gapped = {
                g["category"]
                for g in build_catalog._csv(gaps_csv)
                if g.get("scenario") == "baseline" and g.get("reason") not in build_catalog.OUTSIDE_METHOD
            }
        contributed = {
            r["category"]
            for r in build_catalog._csv(folder)
            if r.get("scenario") == "baseline" and r["key"] != "total" and r["category"] != "pcf"
        }
        for category in gapped - contributed:
            assert category not in lca["totals"].get("baseline", {}), (process.name, category)
            assert category in lca["not_computed"]["baseline"], (process.name, category)
            gap_only.append(process.name)
        for line in lca["pcf"]:
            if line["basis"] in lca["not_computed"].get("baseline", {}) and line["unit"].endswith("CO2-eq"):
                assert line["value"] is None, (process.name, line)
        assert "pcf" not in {c["id"] for c in lca["categories"]}, process.name
    # 21 shipped processes had a gap-only headline at core 1.2.1 (ADR 0026); not pinned, so that
    # linking a background is no test change, but the rule must reach the shipped studies
    assert gap_only
