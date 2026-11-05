"""A process with a design case's own dataset (library ADR 0034, core ADR 0045).

``cheme assess lca --write --case <case>`` writes ``lca/datasets/<dataset id>-<case>.yaml`` beside
the study's ``lca/dataset.yaml``. The LCI build exports both: the case's activity is named after
the case (else the two designs would share name, reference product, location and unit), only
the study's dataset carries the study's allocation and data quality, and both are in the
workbook and the openLCA JSON-LD package with their own amounts. The fixture library's
electrolyser gets a case dataset here; co2-electrolysis-bpm-1 (#331) is the real one.
"""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402

LIBRARY = KIT / "tests" / "fixtures" / "library"
DB = "cheme-as-code-atlas-0.1.0"
SKIDS = "co2-electrolysis-bpm-1"


def _case_dataset(library: Path, case: str = "low", generator: str = "cheme assess lca") -> Path:
    """The fixture electrolyser's dataset as core writes a design case's (ADR 0045): id, title
    and uuid naming the case, provenance.case, half the power."""
    folder = library / "processes" / "fixture-electrolysis" / "lca"
    data = yaml.safe_load((folder / "dataset.yaml").read_text())
    data.update(
        id=f"{data['id']}-{case}",
        title=f"{data['title']}, case {case}",
        uuid="0d6c0f6e-3c1f-5c55-9a59-2b9d6f0c1a11",
        parent=data["uuid"],
        provenance={"generator": generator, "case": case},
    )
    for e in data["exchanges"]:
        if e["key"] == "feed:POWER":
            e["amount"] = e["amount"] / 2
    (folder / "datasets").mkdir(exist_ok=True)
    path = folder / "datasets" / f"{data['id']}.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path


def _activities(out: Path) -> dict[str, dict]:
    return build_lci.read_workbook(out / "lci" / f"{DB}.xlsx")


def _jsonld_processes(out: Path) -> list[dict]:
    with zipfile.ZipFile(out / "lci" / f"{DB}-olca-jsonld.zip") as z:
        return [json.loads(z.read(n)) for n in z.namelist() if n.startswith("processes/")]


def test_a_design_case_dataset_is_exported_beside_the_study_dataset(tmp_path: Path) -> None:
    library = tmp_path / "library"
    shutil.copytree(LIBRARY, library)
    _case_dataset(library)
    out = tmp_path / "out"
    report = build_lci.build(library, out, "0.1.0", commit="fixture")
    assert report.errors == [], report.errors
    acts = _activities(out)
    base = "fixture-electrolysis:fixture-electrolysis:product:H2"
    case = "fixture-electrolysis:fixture-electrolysis-low:product:H2"
    assert base in acts and case in acts
    assert acts[case]["name"] == acts[base]["name"] + ", case low"
    power = {code: next(e["amount"] for e in acts[code]["exchanges"] if e.get("atlas key") == "feed:POWER") for code in (base, case)}
    assert power[case] == pytest.approx(power[base] / 2)
    package = json.loads((out / "lci" / "datapackage.json").read_text())
    entries = {d["id"]: d for p in package["processes"] if p["id"] == "fixture-electrolysis" for d in p["datasets"]}
    assert set(entries) == {"fixture-electrolysis", "fixture-electrolysis-low"}
    # the study's allocation applies to lca/dataset.yaml only; the case dataset keeps its own
    assert entries["fixture-electrolysis"]["allocation"]["source"] == "study"
    assert entries["fixture-electrolysis-low"]["allocation"]["source"] != "study"
    provenance = {"provenance": {"generator": "cheme assess lca", "case": "low"}}
    assert build_lci.design_case(build_lci.Dataset(entries["fixture-electrolysis-low"]["path"], provenance, {}, "dataset", {})) == "low"
    # the study's own dataset is never a case dataset, whatever case it was derived from
    assert build_lci.design_case(build_lci.Dataset("processes/x/lca/dataset.yaml", provenance, {}, "study", {})) is None
    # the hydrogen market of the fixture library takes the study's dataset, not the case's
    market = acts["market:hydrogen:GLO"]
    supply = [e for e in market["exchanges"] if str(e.get("atlas key", "")).startswith("supplier:")]
    assert [e["name"] for e in supply] == [acts[base]["name"]]
    names = [p["name"] for p in _jsonld_processes(out) if p.get("category") == "ChemE-as-Code Atlas/fixture-electrolysis"]
    assert len(names) == 2 and len(set(names)) == 2, names


def test_a_hand_written_twin_is_still_refused(tmp_path: Path) -> None:
    """Only a dataset core generated for a case gets the case in its name: a hand-written copy
    is still two activities the installer cannot tell apart."""
    library = tmp_path / "library"
    shutil.copytree(LIBRARY, library)
    _case_dataset(library, generator="hand-written fixture")
    errors = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture").errors
    assert any("cannot tell them apart" in e and "ADR 0034" in e for e in errors), errors


@pytest.fixture(scope="module")
def skids_build(tmp_path_factory) -> tuple[Path, dict[str, dict]]:
    """The library's two pilot-skid datasets (#331) in a library of their own."""
    tmp = tmp_path_factory.mktemp("skids")
    library = tmp / "library"
    folder = library / "processes" / SKIDS
    (folder / "lca").mkdir(parents=True)
    shutil.copy(KIT / "processes" / SKIDS / "process.yaml", folder)
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml", "mappings.yaml", "manifest.json"):
        shutil.copy(KIT / "processes" / SKIDS / "lca" / name, folder / "lca")
    shutil.copytree(KIT / "processes" / SKIDS / "lca" / "datasets", folder / "lca" / "datasets")
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    (library / "lci").mkdir()
    shutil.copy(KIT / "lci" / "mappings.yaml", library / "lci")
    out = tmp / "out"
    report = build_lci.build(library, out, "0.1.0", commit="skids")
    assert report.errors == [], report.errors
    datasets = {"A": yaml.safe_load((folder / "lca" / "dataset.yaml").read_text())}
    datasets["B"] = yaml.safe_load(next((folder / "lca" / "datasets").glob("*-skid-b.yaml")).read_text())
    return out, datasets


def test_both_skids_are_in_the_workbook_with_their_dataset_amounts(skids_build) -> None:
    out, datasets = skids_build
    acts = {c: a for c, a in _activities(out).items() if c.startswith(f"{SKIDS}:")}
    assert len(acts) == 2
    for skid, ds in datasets.items():
        code = f"{SKIDS}:{ds['id']}:product:CO"
        product = next(e["amount"] for e in ds["exchanges"] if e["key"] == "product:CO")
        exported = {e["atlas key"]: e["amount"] for e in acts[code]["exchanges"] if e.get("type") != "production"}
        for e in ds["exchanges"]:
            if e["key"] in exported:
                assert exported[e["key"]] == pytest.approx(e["amount"] / product, rel=1e-9), (skid, e["key"])
        # the KOH and the CO2 link to their (unchecked) background names; the parts are gaps
        assert {"feed:KOH-FILL", "feed:KOH-DOSE", "feed:CO2", "feed:POWER", "emission:CO2"} <= set(exported)
    assert acts[f"{SKIDS}:{datasets['B']['id']}:product:CO"]["name"].endswith(", case skid-b")
    # the replaced stack parts have no mapping: exported unlinked, listed as gaps (ADR 0026)
    gaps = json.loads((out / "lci" / "gaps.json").read_text())
    assert SKIDS in gaps["preliminary"]
    keys = {(g["dataset"], g["key"]) for g in gaps["processes"][SKIDS]}
    for ds in datasets.values():
        assert {(ds["id"], "consumable:membrane-bpm"), (ds["id"], "consumable:anode-ni-foam")} <= keys


def test_both_skids_are_in_the_jsonld_package_with_their_dataset_amounts(skids_build) -> None:
    out, datasets = skids_build
    processes = [p for p in _jsonld_processes(out) if p.get("category") == f"ChemE-as-Code Atlas/{SKIDS}"]
    assert len(processes) == 2
    for skid, ds in datasets.items():
        power = next(e["amount"] for e in ds["exchanges"] if e["key"] == "feed:POWER")
        match = [
            p for p in processes
            if any("Atlas key feed:POWER" in (e.get("description") or "") and e["amount"] == pytest.approx(power, rel=1e-9)
                   for e in p["exchanges"])
        ]  # fmt: skip
        assert len(match) == 1, (skid, [p["name"] for p in processes])


def test_the_public_build_leaves_the_internal_skids_out(tmp_path: Path) -> None:
    library = tmp_path / "library"
    folder = library / "processes" / SKIDS
    (folder / "lca").mkdir(parents=True)
    shutil.copy(KIT / "processes" / SKIDS / "process.yaml", folder)
    shutil.copy(KIT / "processes" / SKIDS / "lca" / "dataset.yaml", folder / "lca")
    shutil.copytree(KIT / "processes" / SKIDS / "lca" / "datasets", folder / "lca" / "datasets")
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    out = tmp_path / "out"
    build_lci.build(library, out, "0.1.0", commit="skids", public=True)
    package = json.loads((out / "lci" / "datapackage.json").read_text())
    assert SKIDS not in {p["id"] for p in package["processes"]}
