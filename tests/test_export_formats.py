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
    assert names == [f"{db}.xlsx", f"{db}-olca-jsonld.zip", f"{db}-multifunctional.json", "datapackage.json"]
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
        assert len(reader.ids_of(o.Process)) == 2  # the electrolyser (H2 and O2, one multi-output process) and ammonia
        assert all(reader.read_process(pid).exchanges for pid in reader.ids_of(o.Process))


def test_jsonld_allocation_gives_the_workbook_amounts_per_unit_of_each_product(fixture_build: Path) -> None:
    entities = _entities(fixture_build / "cheme-as-code-atlas-0.1.0-olca-jsonld.zip")
    workbook = build_lci.read_workbook(fixture_build / "cheme-as-code-atlas-0.1.0.xlsx")
    checked = 0
    for name, data in entities.items():
        if not name.startswith("processes/") or data["category"] == "ChemE-as-Code Atlas/proxies":
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
