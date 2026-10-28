"""The exchange formats beyond the workbook (process-library#51): the openLCA JSON-LD package and
the Brightway multifunctional file. Structural round trip without openLCA: every entity loads
with olca-schema and writes back unchanged, every reference resolves (in the package, or in
openLCA's reference units of ``olca_schema.units``), and openLCA's allocation of each
multi-output process gives the workbook's amounts per unit of each product. The import into
openLCA itself (olca-ipc against a running openLCA) is not run here.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
pytest.importorskip("openpyxl")
o = pytest.importorskip("olca_schema")
from olca_schema import zipio  # noqa: E402

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402
import export_formats  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
ASU = FIXTURES / "asu-lca"
CLASSES = {"processes": o.Process, "flows": o.Flow, "locations": o.Location}
ALLOCATION_KEY = re.compile(r"^Atlas key (\S+?)[.;]")


def _asu_library(tmp: Path) -> Path:
    library = tmp / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(KIT / "processes" / "asu-1" / "lca" / "mappings.yaml", library / "processes" / "asu-1" / "lca")  # its own overrides
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml", "results.csv"):
        shutil.copy(ASU / name, library / "processes" / "asu-1" / "lca")
    return library


def _entities(path: Path) -> dict[str, dict]:
    with zipfile.ZipFile(path) as package:
        return {name: json.loads(package.read(name)) for name in package.namelist()}


def _reference_units() -> dict[str, set[str]]:
    """openLCA's reference unit, unit group and flow property ids (olca_schema.units) -> their
    names (a unit's synonyms, m3 and m\u00b3, share its id)."""
    from olca_schema import units

    known: dict[str, set[str]] = {}
    with (Path(units.__file__).parent / "units.csv").open(encoding="utf-8") as f:
        for row in list(csv.reader(f))[1:]:
            for eid, name in ((row[1], row[0]), (row[3], row[2]), (row[5], row[4])):
                known.setdefault(eid, set()).add(name)
    return known


@pytest.fixture(scope="module")
def fixture_build(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("formats")
    assert build_lci.build(FIXTURES / "library", out, "0.1.0", commit="fixture").errors == []
    return out / "lci"


def test_index_lists_every_format_with_checksum_and_version(fixture_build: Path) -> None:
    index = json.loads((fixture_build / "index.json").read_text())
    names = [f["name"] for f in index["files"]]
    db = "cheme-as-code-atlas-0.1.0"
    assert names == [f"{db}.xlsx", f"{db}-olca-jsonld.zip", f"{db}-multifunctional.json", "datapackage.json", "benchmarks.json", "gaps.json"]
    for entry in index["files"]:
        assert entry["format"] and entry["format_version"] and len(entry["sha256"]) == 64
        assert entry["bytes"] == (fixture_build / entry["name"]).stat().st_size
    by_name = {f["name"]: f for f in index["files"]}
    assert by_name[f"{db}-olca-jsonld.zip"]["format_version"] == "2"
    assert by_name[f"{db}-multifunctional.json"]["format_version"] == export_formats.MULTIFUNCTIONAL_SCHEMA
    resources = json.loads((fixture_build / "datapackage.json").read_text())["resources"]
    assert [r["path"] for r in resources] == names[:3]


def test_jsonld_entities_load_with_olca_schema_and_references_resolve(fixture_build: Path) -> None:
    path = fixture_build / "cheme-as-code-atlas-0.1.0-olca-jsonld.zip"
    entities = _entities(path)
    assert entities.pop("olca-schema.json") == {"version": 2}
    units = _reference_units()
    ids = {name.split("/")[1].removesuffix(".json") for name in entities}
    for name, data in entities.items():
        folder, eid = name.split("/")
        assert data["@id"] == eid.removesuffix(".json")
        assert CLASSES[folder].from_dict(data).to_dict() == data, name  # nothing the schema does not know
        assert "lastChange" not in data  # reproducible: no time stamps

    def refs(value):
        if isinstance(value, dict):
            if "@type" in value and "@id" in value and value is not None:
                yield value
            for v in value.values():
                yield from refs(v)
        elif isinstance(value, list):
            for v in value:
                yield from refs(v)

    for name, data in entities.items():
        for ref in refs({k: v for k, v in data.items() if k not in ("@id", "@type")}):
            if ref["@type"] in ("Unit", "UnitGroup", "FlowProperty"):
                assert ref["name"] in units.get(ref["@id"], set()), (name, ref)
            else:
                assert ref["@id"] in ids, (name, ref)
    with zipio.ZipReader(path) as reader:
        # the electrolyser (H2 and O2, one multi-output process), ammonia and the hydrogen market
        assert len(reader.ids_of(o.Process)) == 3
        assert all(reader.read_process(pid).exchanges for pid in reader.ids_of(o.Process))


def test_jsonld_allocation_gives_the_workbook_amounts_per_unit_of_each_product(fixture_build: Path) -> None:
    entities = _entities(fixture_build / "cheme-as-code-atlas-0.1.0-olca-jsonld.zip")
    workbook = build_lci.read_workbook(fixture_build / "cheme-as-code-atlas-0.1.0.xlsx")
    checked = 0
    for name, data in entities.items():
        if not name.startswith("processes/") or data["category"] in ("ChemE-as-Code Atlas/proxies", "ChemE-as-Code Atlas/markets"):
            continue
        outputs = [e for e in data["exchanges"] if e["description"].startswith("Atlas key product:") and "; activity " in e["description"]]
        others = [e for e in data["exchanges"] if e not in outputs]
        factors = {f["product"]["@id"]: f["value"] for f in data.get("allocationFactors", []) if f["allocationType"] == data.get("defaultAllocationMethod")}
        assert (len(outputs) > 1) == bool(factors)
        for product in outputs:
            code = product["description"].split("; activity ")[1].split(";")[0]
            factor = factors.get(product["flow"]["@id"], 1.0)
            expected = {e["atlas key"]: e["amount"] for e in workbook[code]["exchanges"] if e["type"] != "production"}
            found = {ALLOCATION_KEY.match(e["description"]).group(1): e["amount"] * factor / product["amount"] for e in others}
            assert found.keys() == expected.keys(), code
            for key, amount in expected.items():
                assert found[key] == pytest.approx(amount, rel=1e-9), (code, key)
                checked += 1
    assert checked > 10


def test_a_market_is_exported_and_inputs_linked_to_it_resolve(fixture_build: Path) -> None:
    """markets/hydrogen.yaml of the fixture library: the market is a single-output process in
    the JSON-LD package and in the multifunctional file; the ammonia's hydrogen input (linked to
    the market) has the market's process as its default provider, and the market's supplier
    exchange the electrolyser's multi-output process."""
    entities = _entities(fixture_build / "cheme-as-code-atlas-0.1.0-olca-jsonld.zip")
    processes = {d["@id"]: d for n, d in entities.items() if n.startswith("processes/")}
    market_id = export_formats.atlas_uuid("process", "market:hydrogen:GLO")
    market = processes[market_id]
    assert market["category"] == "ChemE-as-Code Atlas/markets"
    reference = next(e for e in market["exchanges"] if e.get("isQuantitativeReference"))
    assert reference["flow"]["@id"] == export_formats.atlas_uuid("flow", "market:hydrogen:GLO") and reference["amount"] == 1.0
    workbook = build_lci.read_workbook(fixture_build / "cheme-as-code-atlas-0.1.0.xlsx")
    expected = {e["atlas key"]: e["amount"] for e in workbook["market:hydrogen:GLO"]["exchanges"] if e["type"] != "production"}
    found = {ALLOCATION_KEY.match(e["description"]).group(1): e for e in market["exchanges"] if e is not reference}
    assert {k: e["amount"] for k, e in found.items()} == pytest.approx(expected)
    electrolyser = next(pid for pid, d in processes.items() if d["category"] == "ChemE-as-Code Atlas/fixture-electrolysis")
    supply = [e for k, e in found.items() if k.startswith("supplier:")]
    assert supply and all(e["defaultProvider"]["@id"] == electrolyser for e in supply)

    ammonia = next(d for d in processes.values() if d["category"] == "ChemE-as-Code Atlas/fixture-ammonia")
    hydrogen = [e for e in ammonia["exchanges"] if e.get("defaultProvider", {}).get("@id") == market_id]
    assert len(hydrogen) == 1 and hydrogen[0]["isInput"] and hydrogen[0]["flow"]["@id"] == reference["flow"]["@id"]

    data = json.loads((fixture_build / "cheme-as-code-atlas-0.1.0-multifunctional.json").read_text())
    by_code = {p["code"]: p for p in data["processes"]}
    mf_market = by_code["market:hydrogen:GLO"]
    assert mf_market["type"] == "process" and mf_market["atlas market"] == "market:hydrogen:GLO"
    suppliers = [e for e in mf_market["exchanges"] if str(e.get("atlas key", "")).startswith("supplier:")]
    assert [e["atlas code"] for e in suppliers] == ["fixture-electrolysis:fixture-electrolysis:product:H2"]
    taken = [e for e in by_code["fixture-ammonia:fixture-ammonia-hb:product:ammonia"]["exchanges"] if e.get("atlas activity code")]
    assert [e["atlas activity code"] for e in taken] == ["market:hydrogen:GLO"] and "atlas code" not in taken[0]
    every = {e[k] for p in data["processes"] for e in p["exchanges"] for k in ("atlas code", "atlas activity code", "atlas plant code") if e.get(k)}
    assert every <= set(by_code) | {e["desired_code"] for p in data["processes"] for e in p["exchanges"] if e.get("desired_code")}


def test_jsonld_identifiers(fixture_build: Path, tmp_path: Path) -> None:
    entities = _entities(fixture_build / "cheme-as-code-atlas-0.1.0-olca-jsonld.zip")
    flows = {d["name"]: d for n, d in entities.items() if n.startswith("flows/")}
    # an elementary flow with a biosphere3 identity keeps its UUID; one without gets an Atlas id, said so
    assert flows["Water, river"]["@id"] == "8c75e7ab-8ab8-41e4-b394-c166ff5b050d"
    hydrogen = next(d for d in flows.values() if d["flowType"] == "ELEMENTARY_FLOW" and d["name"] == "Hydrogen")
    assert hydrogen["@id"] == export_formats.atlas_uuid("flow", "elementary", "Hydrogen", "air", "kilogram")
    assert "NOT an EF 3.1 or ecoinvent UUID" in hydrogen["description"]
    # an Atlas product flow by its activity code, stable across versions
    product = next(d for d in flows.values() if d["category"] == "ChemE-as-Code Atlas/fixture-electrolysis" and "ydrogen" in d["name"])
    assert product["@id"] == export_formats.atlas_uuid("flow", "fixture-electrolysis:fixture-electrolysis:product:H2")

    # ASU-1 of this library: the process is the dataset's own UUID (core: uuid5 of plant and
    # dataset id); the substitution variant gets its own; the v1 fixture, without a uuid, an Atlas one
    code = "asu-1:asu-1-500-t-d-gox"
    cases = (
        (KIT, "cutoff", "62b30292-ab30-52de-8732-1ab497ca8477"),
        (KIT, "substitution", export_formats.atlas_uuid("process", "substitution", code)),
        (_asu_library(tmp_path), "cutoff", export_formats.atlas_uuid("process", code)),
    )
    for number, (library, model, expected) in enumerate(cases):
        out = tmp_path / str(number)
        assert build_lci.build(library, out, "0.1.0", system_model=model).errors == []
        db = "cheme-as-code-atlas-0.1.0" + ("" if model == "cutoff" else "-substitution")
        processes = {d["name"]: d for n, d in _entities(out / "lci" / f"{db}-olca-jsonld.zip").items() if n.startswith("processes/")}
        asu = processes["Cryogenic air separation unit (500 t/d GOX)"]
        assert asu["@id"] == expected
        assert asu["defaultAllocationMethod"] == "PHYSICAL_ALLOCATION" and len(asu["allocationFactors"]) == 4 + 0  # exergy; no prices
        assert asu["version"] == "00.01.000"


def test_multifunctional_file_carries_only_sourced_allocation_properties(tmp_path: Path) -> None:
    library = _asu_library(tmp_path)
    assert build_lci.build(library, tmp_path / "out", "0.1.0").errors == []
    data = json.loads((tmp_path / "out" / "lci" / "cheme-as-code-atlas-0.1.0-multifunctional.json").read_text())
    assert data["schema"] == export_formats.MULTIFUNCTIONAL_SCHEMA and data["database"] == "cheme-as-code-atlas-0.1.0-multifunctional"
    asu = next(p for p in data["processes"] if p["code"] == "asu-1:asu-1-500-t-d-gox")
    assert asu["type"] == "multifunctional" and asu["default_allocation"] == "exergy"
    functional = [e for e in asu["exchanges"] if e.get("functional")]
    dataset = yaml.safe_load((ASU / "dataset.yaml").read_text())
    products = {e["key"]: e for e in dataset["exchanges"] if e["type"] == "product"}
    assert [e["atlas key"] for e in functional] == list(products)
    for edge in functional:
        given = products[edge["atlas key"]]
        assert edge["amount"] == given["amount"] and edge["desired_code"] == f"asu-1:asu-1-500-t-d-gox:{edge['atlas key']}"
        # mass (products in kg), the flowsheet's exergy and the build's share; no price or LHV is stated
        assert set(edge["properties"]) == {"mass", "exergy", "share"}
        assert edge["properties"]["exergy"] == given["properties"]["exergy"]
    assert sum(e["properties"]["share"] for e in functional) == pytest.approx(1.0)
    # the other exchanges are per basis (1 h): the power input is the dataset's
    power = next(e for e in asu["exchanges"] if e.get("atlas key") == "feed:POWER")
    assert power["amount"] == pytest.approx(next(e["amount"] for e in dataset["exchanges"] if e["key"] == "feed:POWER"))


def test_a_unit_openlca_has_no_reference_for_fails_the_build(tmp_path: Path) -> None:
    with pytest.raises(export_formats.FormatError, match="no openLCA reference unit"):
        export_formats._Olca("db", "cutoff", True, "DE").units("standard cubic meter", "here")


def test_utility_links_resolve_in_both_formats(tmp_path: Path) -> None:
    """The library utilities (#45): a utility output on an Atlas proxy that names an Atlas
    utility (the cooling tower's blowdown to the WWTP) has that utility's process as its default
    provider in the JSON-LD package, and in the multifunctional file its ``atlas activity code``
    (taken with prefer_atlas) beside the proxy's ``atlas code`` (the fallback)."""
    library = tmp_path / "library"
    for folder in ("chemicals", "lci"):
        shutil.copytree(KIT / folder, library / folder)
    for manifest in sorted((KIT / "processes").glob("utility-*/process.yaml")):
        shutil.copytree(manifest.parent, library / "processes" / manifest.parent.name)
    assert build_lci.build(library, tmp_path / "out", "0.1.0", commit="test").errors == []
    lci = tmp_path / "out" / "lci"
    tower, wwtp = "utility-cooling-tower:cooling-tower-evaporative-25-35:product:heat-rejected", "utility-wwtp:wwtp-activated-sludge-per-m3:product:wastewater"

    processes = {d["@id"]: d for n, d in _entities(lci / "cheme-as-code-atlas-0.1.0-olca-jsonld.zip").items() if n.startswith("processes/")}
    by_category = {d["category"]: pid for pid, d in processes.items()}
    blowdown = next(e for e in processes[by_category["ChemE-as-Code Atlas/utility-cooling-tower"]]["exchanges"] if ALLOCATION_KEY.match(e.get("description") or "") and ALLOCATION_KEY.match(e["description"]).group(1) == "output:blowdown")
    assert blowdown["defaultProvider"]["@id"] == by_category["ChemE-as-Code Atlas/utility-wwtp"]
    assert all(e["defaultProvider"]["@id"] in processes for d in processes.values() for e in d["exchanges"] if e.get("defaultProvider"))

    data = json.loads((lci / "cheme-as-code-atlas-0.1.0-multifunctional.json").read_text())
    by_code = {p["code"]: p for p in data["processes"]}
    codes = set(by_code) | {e["desired_code"] for p in data["processes"] for e in p["exchanges"] if e.get("desired_code")}
    taken = next(e for p in data["processes"] for e in p["exchanges"] if e.get("atlas key") == "output:blowdown" and p["code"].startswith("utility-cooling-tower"))
    assert taken["atlas activity code"] == wwtp and taken["atlas code"].startswith("proxy:")
    assert tower in codes
    every = {e[k] for p in data["processes"] for e in p["exchanges"] for k in ("atlas code", "atlas activity code", "atlas plant code") if e.get(k)}
    assert every <= codes
