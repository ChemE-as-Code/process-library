"""Registry v2 (grades, properties, checks), the family taxonomy and the coverage roadmap."""

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
import build_lci  # noqa: E402
import registry as reg  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
LIBRARY = FIXTURES / "library"
REGISTRY = KIT / "chemicals" / "chemicals.yaml"
ASU_MANIFEST = KIT / "processes" / "asu-1" / "process.yaml"

#: The registry as it was before v2 (main, 2026-10-24): the migration keeps every identity field.
V1 = [
    {"slug": "air", "name": "Air", "kind": "mixture"},
    {"slug": "argon", "name": "Argon", "kind": "substance", "formula": "Ar", "cas": "7440-37-1", "chebi": "CHEBI:49475", "inchikey": "XKRFYHLGVUSROY-UHFFFAOYSA-N"},
    {"slug": "carbon-dioxide", "name": "Carbon dioxide", "kind": "substance", "formula": "CO2", "cas": "124-38-9", "chebi": "CHEBI:16526", "inchikey": "CURLTUGMZLYLDI-UHFFFAOYSA-N"},
    {"slug": "cooling-water", "name": "Cooling water", "kind": "utility"},
    {"slug": "electricity", "name": "Electricity", "kind": "utility"},
    {"slug": "nitrogen", "name": "Nitrogen", "kind": "substance", "formula": "N2", "cas": "7727-37-9", "chebi": "CHEBI:17997", "inchikey": "IJGRMHOSHXDMSA-UHFFFAOYSA-N"},
    {"slug": "oxygen", "name": "Oxygen", "kind": "substance", "formula": "O2", "cas": "7782-44-7", "chebi": "CHEBI:15379", "inchikey": "MYMOFIZGZYHOMD-UHFFFAOYSA-N"},
    {"slug": "water", "name": "Water", "kind": "substance", "formula": "H2O", "cas": "7732-18-5", "chebi": "CHEBI:15377", "inchikey": "XLYOFNOQVPJJNP-UHFFFAOYSA-N"},
]


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(_json(KIT / "schemas" / name))


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


def _edit(path: Path, change) -> None:
    data = _yaml(path)
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# --- schema and migration --------------------------------------------------------------------


@pytest.mark.parametrize("path", [REGISTRY, LIBRARY / "chemicals" / "chemicals.yaml"], ids=["library", "fixture"])
def test_registries_match_the_v2_schema_and_pass_the_checks(path: Path) -> None:
    data = _yaml(path)
    assert data["schema"] == "cheme-as-code/chemicals/v2"
    assert list(_validator("chemicals.schema.json").iter_errors(data)) == []
    assert reg.check(reg.load(data)) == []


def test_a_v1_registry_still_validates() -> None:
    assert list(_validator("chemicals.schema.json").iter_errors({"schema": "cheme-as-code/chemicals/v1", "chemicals": V1})) == []


def test_migration_keeps_every_v1_entry_and_identity_field() -> None:
    chemicals = reg.load(_yaml(REGISTRY)).chemicals
    for old in V1:
        new = chemicals[old["slug"]]
        assert {k: new[k] for k in old} == old


def test_every_substance_property_has_a_unit_and_a_source() -> None:
    for slug, chem in reg.load(_yaml(REGISTRY)).chemicals.items():
        entries = [chem.get("properties") or {}, *((g.get("properties") or {}) for g in chem.get("grades", []))]
        for properties in entries:
            for name, prop in properties.items():
                assert prop["unit"] and len(prop["source"]) > 3, (slug, name)
        if chem["kind"] == "substance":
            assert {"molar_mass", "elemental_composition", "carbon_content", "standard_chemical_exergy"} <= set(chem["properties"]), slug


def test_no_price_without_an_open_source() -> None:
    """No prices yet: every one must name its open source, year, currency and region (schema)."""
    for chem in reg.load(_yaml(REGISTRY)).chemicals.values():
        for properties in [chem.get("properties") or {}, *((g.get("properties") or {}) for g in chem.get("grades", []))]:
            assert "price" not in properties


def test_air_composition_names_registry_chemicals_and_sums_to_100() -> None:
    air = reg.load(_yaml(REGISTRY)).chemicals["air"]
    components = air["composition"]["components"]
    assert {c["chemical"] for c in components} == {"nitrogen", "oxygen", "argon", "carbon-dioxide"}
    assert sum(c["value"] for c in components) == pytest.approx(100.0, abs=0.01)


# --- build-time checks -----------------------------------------------------------------------


@pytest.mark.parametrize(("cas", "valid"), [("7732-18-5", True), ("7782-44-7", True), ("1333-74-0", True), ("7732-18-4", False), ("124-38-0", False)])
def test_cas_check_digit(cas: str, valid: bool) -> None:
    assert reg.cas_valid(cas) is valid


@pytest.mark.parametrize(
    ("key", "problem"),
    [
        ("XLYOFNOQVPJJNP-UHFFFAOYSA-N", None),
        ("XLYOFNOQVPJJNP-UHFFFAOYNA-N", "not a standard InChIKey"),
        ("XLYOFNOQVPJJNP-UHFFFAOYSA", "14-10-1"),
    ],
)
def test_inchikey_format(key: str, problem: str | None) -> None:
    found = reg.inchikey_problem(key)
    assert found is None if problem is None else problem in found


def test_molar_mass_and_composition_follow_the_formula() -> None:
    assert reg.molar_mass("CO2") == pytest.approx(44.009, abs=1e-3)
    assert reg.mass_fractions("CH4")["C"] == pytest.approx(0.7487, abs=1e-4)
    with pytest.raises(ValueError):
        reg.parse_formula("Ca(OH)2")


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda c: c["oxygen"].update(cas="7782-44-8"), "CAS 7782-44-8 fails its check digit"),
        (lambda c: c["oxygen"].update(inchikey="MYMOFIZGZYHOMD-UHFFFAOYNA-N"), "not a standard InChIKey"),
        (lambda c: c["oxygen"]["properties"]["molar_mass"].update(value=32.5), "molar_mass 32.5"),
        (lambda c: c["carbon-dioxide"]["properties"]["carbon_content"].update(value=0.3), "carbon_content 0.3"),
        (lambda c: c["carbon-dioxide"]["properties"]["elemental_composition"].update(value={"C": 0.5, "O": 0.5}), "elemental_composition of C, O"),
        (lambda c: c["air"]["composition"]["components"][0].update(value=70), "sums to"),
        (lambda c: c["air"]["composition"]["components"][0].update(chemical="xenon"), "unknown chemical 'xenon'"),
        (lambda c: c["nitrogen"]["grades"][1]["crosswalk"].update(ecoinvent=["oxygen, liquid"]), "belongs to more than one entry"),
        (lambda c: c["nitrogen"]["grades"].append(dict(c["nitrogen"]["grades"][0])), "appears twice"),
    ],
)
def test_registry_checks_find_the_problem(change, message: str) -> None:
    data = _yaml(REGISTRY)
    change({c["slug"]: c for c in data["chemicals"]})
    problems = reg.check(reg.load(data))
    assert any(message in p for p in problems), problems


def test_flow_grades_must_name_a_known_grade() -> None:
    data = _yaml(REGISTRY)
    data["flow_grades"]["asu-1/product:LOX"] = "oxygen/lox-unknown"
    assert any("unknown grade oxygen/lox-unknown" in p for p in reg.check(reg.load(data)))


def test_a_registry_problem_fails_the_catalog_build(library: Path, tmp_path: Path) -> None:
    _edit(library / "chemicals" / "chemicals.yaml", lambda d: d["chemicals"][2].update(cas="1333-74-1"))
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    assert any("fails its check digit" in e for e in report.errors)
    report = build_lci.build(library, tmp_path / "lci", "0.1.0", commit="fixture")
    assert any("fails its check digit" in e for e in report.errors)


# --- grades ----------------------------------------------------------------------------------


def test_asu_products_are_four_distinct_grades_without_touching_its_manifest() -> None:
    products = reg.load(_yaml(REGISTRY))
    manifest = _yaml(ASU_MANIFEST)
    resolved = {}
    for item in manifest["chemistry"]["outputs"]:
        slug, grade, problem = reg.flow_grade(products, "asu-1", item)
        assert problem is None
        if item["role"] in ("main-product", "co-product"):
            resolved[item["inventory_key"]] = f"{slug}/{grade}"
    assert resolved == {
        "product:GOXP": "oxygen/gox-30barg-99.5",
        "product:GANP": "nitrogen/gan-8barg-10ppm",
        "product:LOX": "oxygen/lox",
        "product:LIN": "nitrogen/lin",
    }
    # the emissions stay at the substance
    assert reg.flow_grade(products, "asu-1", {"chemical": "nitrogen", "inventory_key": "emission:N2"})[1] is None


def test_mass_and_exergy_allocation_follow_from_registry_data() -> None:
    """ASU-1's mass and exergy shares from its product amounts and the registry grades' sourced
    exergies; economic allocation needs registry prices, of which there are none yet."""
    products = reg.load(_yaml(REGISTRY))
    amounts = {"oxygen/gox-30barg-99.5": 20860.0, "nitrogen/gan-8barg-10ppm": 12510.0, "oxygen/lox": 470.0, "nitrogen/lin": 470.0}
    weights = {ref: amount * products.properties(*reg.split(ref))["exergy"]["value"] for ref, amount in amounts.items()}
    share = weights["oxygen/gox-30barg-99.5"] / sum(weights.values())
    assert share == pytest.approx(0.70, abs=0.01)  # the study's 0.701 (flowsheet exergies)
    assert amounts["oxygen/gox-30barg-99.5"] / sum(amounts.values()) == pytest.approx(0.608, abs=1e-3)
    assert all("price" not in products.properties(*reg.split(ref)) for ref in amounts)


def test_economic_allocation_without_a_price_says_the_registry_has_none() -> None:
    """With no price in the study or the dataset, economic allocation fails and says that the
    export takes no registry price (docs/registry.md, Missing prices), rather than guessing."""
    dataset = {"exchanges": [
        {"key": "product:A", "type": "product", "amount": 10.0, "unit": "kg"},
        {"key": "product:B", "type": "product", "amount": 10.0, "unit": "kg"},
    ]}
    with pytest.raises(build_lci.BuildError, match="no price of A in the study or the dataset, and the export takes no registry price"):
        build_lci.shares(dataset, {"method": "economic"}, "p")
    assert build_lci.shares(dataset, {"method": "economic", "prices": {"A": 3.0, "B": 1.0}}, "p")["product:A"] == pytest.approx(0.75)


def test_grade_exergy_is_chemical_plus_physical() -> None:
    """The gas grades' exergy: Szargut's chemical exergy per kg plus the physical exergy, which for
    a gas at T0 is close to the ideal-gas R T0 ln(p/p0) / M (the registry uses NIST real-fluid h, s)."""
    import math

    products = reg.load(_yaml(REGISTRY))
    for ref, pressure in (("oxygen/gox-30barg-99.5", 31.01325), ("nitrogen/gan-8barg-10ppm", 9.01325)):
        slug, grade = reg.split(ref)
        props = products.properties(slug, grade)
        molar = props["molar_mass"]["value"] / 1000
        ideal = props["standard_chemical_exergy"]["value"] / molar + 8.314462618 * 298.15 * math.log(pressure / 1.01325) / molar / 1000
        assert props["exergy"]["value"] == pytest.approx(ideal, rel=0.01)


@pytest.mark.parametrize(
    ("item", "mapped", "expected"),
    [
        ({"chemical": "oxygen/lox", "inventory_key": "product:X"}, None, ("oxygen", "lox", None)),
        ({"chemical": "oxygen"}, None, ("oxygen", None, None)),
        ({"chemical": "oxygen", "inventory_key": "product:X"}, "oxygen/lox", ("oxygen", "lox", None)),
        ({"chemical": "oxygen/lox", "inventory_key": "product:X"}, "oxygen/lox", ("oxygen", "lox", None)),
        ({"chemical": "oxygen/gox-30barg-99.5", "inventory_key": "product:X"}, "oxygen/lox", ("oxygen", "gox-30barg-99.5", "names grade")),
        ({"chemical": "nitrogen", "inventory_key": "product:X"}, "oxygen/lox", ("nitrogen", None, "but the flow is nitrogen")),
        ({"chemical": "oxygen/vapour"}, None, ("oxygen", "vapour", "unknown grade oxygen/vapour")),
    ],
)
def test_flow_grade_resolution(item: dict, mapped: str | None, expected: tuple) -> None:
    products = reg.load(_yaml(REGISTRY))
    if mapped:
        products.flow_grades["p/product:X"] = mapped
    slug, grade, problem = reg.flow_grade(products, "p", item)
    assert (slug, grade) == expected[:2]
    assert (problem is None) if expected[2] is None else (expected[2] in problem)


def _grade_the_fixture_hydrogen(library: Path) -> None:
    def change(data):
        for group in ("outputs", "inputs"):
            for item in data["chemistry"].get(group, []):
                if item["chemical"] == "hydrogen":
                    item["chemical"] = "hydrogen/gaseous-30bar"
    _edit(library / "processes" / "fixture-electrolysis" / "process.yaml", change)
    _edit(library / "processes" / "fixture-ammonia" / "process.yaml", change)


def test_catalog_aggregates_grades_by_slug(library: Path, tmp_path: Path) -> None:
    _grade_the_fixture_hydrogen(library)
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    assert report.errors == []
    detail = _json(tmp_path / "out" / "processes" / "fixture-electrolysis.json")
    h2 = next(f for f in detail["chemistry"]["outputs"] if f["inventory_key"] == "product:H2")
    assert (h2["chemical"], h2["grade"]) == ("hydrogen", "gaseous-30bar")
    o2 = next(f for f in detail["chemistry"]["outputs"] if f["inventory_key"] == "product:O2")
    assert o2["grade"] is None
    summary = next(p for p in _json(tmp_path / "out" / "catalog.json")["processes"] if p["id"] == "fixture-electrolysis")
    assert "hydrogen" in summary["outputs"]
    graph = _json(tmp_path / "out" / "graph.json")
    ids = {n["id"] for n in graph["nodes"]}
    assert "chemical:hydrogen" in ids and not any("/" in i for i in ids)
    hydrogen = next(c for c in _json(tmp_path / "out" / "chemicals.json")["chemicals"] if c["slug"] == "hydrogen")
    grades = {g["slug"]: g for g in hydrogen["grades"]}
    assert grades["gaseous-30bar"]["produced_by"] == [{"process": "fixture-electrolysis", "role": "main-product"}]
    assert grades["gaseous-30bar"]["consumed_by"] == [{"process": "fixture-ammonia", "role": "reactant"}]
    assert grades["liquid"]["produced_by"] == [] and grades["liquid"]["consumed_by"] == []
    assert hydrogen["produced_by"] == [{"process": "fixture-electrolysis", "role": "main-product"}]


def test_unknown_grade_is_a_catalog_error(library: Path, tmp_path: Path) -> None:
    _edit(library / "processes" / "fixture-electrolysis" / "process.yaml", lambda d: d["chemistry"]["outputs"][0].update(chemical="hydrogen/slush"))
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    assert any("unknown grade hydrogen/slush" in e for e in report.errors)


def test_lci_names_the_grade_as_reference_product(library: Path, tmp_path: Path) -> None:
    _grade_the_fixture_hydrogen(library)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == []
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    electrolysis = next(p for p in package["processes"] if p["id"] == "fixture-electrolysis")
    by_code = {a["code"].rsplit(":", 1)[1]: a for a in electrolysis["activities"]}
    assert by_code["H2"]["reference_product"] == "Hydrogen, gaseous, 30 bar"
    assert (by_code["H2"]["chemical"], by_code["H2"]["grade"]) == ("hydrogen", "gaseous-30bar")
    assert by_code["O2"]["reference_product"] == "Oxygen vented or sold"  # no grade: the title, as before


def _set_energy(library: Path, value: float) -> None:
    def change(data):
        for exchange in data["exchanges"]:
            if exchange["key"] == "product:H2":
                exchange["properties"] = {"energy": value, "source": "fixture"}
    _edit(library / "processes" / "fixture-electrolysis" / "lca" / "dataset.yaml", change)


def test_study_properties_are_checked_against_the_registry(library: Path, tmp_path: Path) -> None:
    _set_energy(library, 119960.0)  # kJ/kg, the registry's LHV
    report = build_lci.build(library, tmp_path / "a", "0.1.0", commit="fixture")
    assert report.warnings == []
    checks = next(p for p in _json(tmp_path / "a" / "lci" / "datapackage.json")["processes"] if p["id"] == "fixture-electrolysis")["datasets"][0]["property_checks"]
    assert [(c["key"], c["property"], c["status"]) for c in checks] == [("product:H2", "energy", "match")]

    _set_energy(library, 141790.0)  # an HHV given as the energy content
    report = build_lci.build(library, tmp_path / "b", "0.1.0", commit="fixture")
    assert any("energy 141790 kJ/kg differs from the registry's 119960 kJ/kg of hydrogen" in w for w in report.warnings)

    _edit(library / "lci" / "mappings.yaml", lambda d: d["exchanges"].update({"fixture-electrolysis/product:H2": {"properties_reason": "the study allocates by HHV on purpose"}}))
    report = build_lci.build(library, tmp_path / "c", "0.1.0", commit="fixture")
    assert report.warnings == []
    checks = next(p for p in _json(tmp_path / "c" / "lci" / "datapackage.json")["processes"] if p["id"] == "fixture-electrolysis")["datasets"][0]["property_checks"]
    assert checks[0]["status"] == "overridden" and checks[0]["reason"] == "the study allocates by HHV on purpose"


def test_property_without_a_registry_value_is_unchecked() -> None:
    products = reg.load(_yaml(REGISTRY))
    assert reg.compare_property(products, "argon", None, "energy", 10.0)["status"] == "unchecked"
    assert reg.compare_property(products, "argon", None, "energy", None) is None


def test_property_of_a_product_not_in_kg_is_unchecked(library: Path, tmp_path: Path) -> None:
    products = reg.load(_yaml(REGISTRY))
    result = reg.compare_property(products, "hydrogen", None, "energy", 10800.0, "m3")
    assert (result["status"], result["unit"], result["registry"]) == ("unchecked", "kJ/m3", None)

    def to_m3(data):  # about 10 800 kJ per m3 of hydrogen: no mismatch against 119 960 kJ/kg
        for exchange in data["exchanges"]:
            if exchange["key"] == "product:H2":
                exchange.update(unit="m3", amount=464.0, properties={"energy": 10800.0, "source": "fixture"})
        data["allocation"] = {"method": "shares", "shares": {"H2": 0.9, "O2": 0.1}, "source": "fixture"}  # mass cannot weigh m3
    _edit(library / "processes" / "fixture-electrolysis" / "lca" / "dataset.yaml", to_m3)
    _edit(library / "processes" / "fixture-electrolysis" / "lca" / "lca.yaml", lambda d: d.update(allocation={"method": "shares", "shares": {"H2": 0.9, "O2": 0.1}}))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and not any("differs from the registry" in w for w in report.warnings), (report.errors, report.warnings)
    checks = next(p for p in _json(tmp_path / "out" / "lci" / "datapackage.json")["processes"] if p["id"] == "fixture-electrolysis")["datasets"][0]["property_checks"]
    assert [(c["key"], c["status"], c["unit"]) for c in checks] == [("product:H2", "unchecked", "kJ/m3")]


def test_unused_flow_grades_are_a_catalog_warning(library: Path, tmp_path: Path) -> None:
    _edit(library / "chemicals" / "chemicals.yaml", lambda d: d.setdefault("flow_grades", {}).update({"fixture-electrolysis/product:H2-renamed": "hydrogen/gaseous-30bar"}))
    assert reg.unused_flow_grades(reg.load(_yaml(library / "chemicals" / "chemicals.yaml")), {"fixture-electrolysis/product:H2"}) == ["fixture-electrolysis/product:H2-renamed"]
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    assert report.errors == []
    assert any("flow_grades.fixture-electrolysis/product:H2-renamed: no process has a flow" in w for w in report.warnings), report.warnings


# --- taxonomy --------------------------------------------------------------------------------


def test_taxonomy_matches_its_schema_and_the_process_schema_enum() -> None:
    taxonomy = _yaml(KIT / "taxonomy" / "families.yaml")
    assert list(_validator("families.schema.json").iter_errors(taxonomy)) == []
    slugs = [f["slug"] for f in taxonomy["families"]]
    assert len(slugs) == len(set(slugs))
    groups = {g["slug"] for g in taxonomy["groups"]}
    assert {f["group"] for f in taxonomy["families"]} <= groups
    enum = _json(KIT / "schemas" / "process.schema.json")["$defs"]["family"]["enum"]
    assert enum == sorted(slugs), "add the family to taxonomy/families.yaml and to process.schema.json $defs.family together"


def test_asu_families_validate_and_unknown_families_do_not() -> None:
    validator = _validator("process.schema.json")
    manifest = _yaml(ASU_MANIFEST)
    assert list(validator.iter_errors(manifest)) == []
    manifest["families"] = [*manifest["families"], "space-elevators"]
    assert any("space-elevators" in e.message for e in validator.iter_errors(manifest))


def test_catalog_families_carry_the_isic_classes(tmp_path: Path) -> None:
    build_catalog.build(LIBRARY, tmp_path / "out", None, commit="fixture")
    families = {f["slug"]: f for f in _json(tmp_path / "out" / "catalog.json")["families"]}
    assert families["ammonia"] == {"slug": "ammonia", "count": 1, "title": "Ammonia", "group": "fertilizers", "isic": ["2012"], "nace": ["20.15"]}
    assert families["hydrogen"]["isic"] == ["2011"]


# --- coverage --------------------------------------------------------------------------------


def test_coverage_roadmap_is_complete_and_consistent() -> None:
    data = _yaml(KIT / "coverage.yaml")
    assert list(_validator("coverage.schema.json").iter_errors(data)) == []
    entries = data["entries"]
    assert len(entries) >= 50
    assert sorted(e["rank"] for e in entries) == list(range(1, len(entries) + 1))
    ids = {e["id"] for e in entries}
    assert len(ids) == len(entries)
    families = {f["slug"] for f in _yaml(KIT / "taxonomy" / "families.yaml")["families"]}
    for entry in entries:
        assert entry["family"] in families, entry["id"]
        assert set(entry.get("feeds", [])) <= ids, entry["id"]
        cited = [entry["volume"].get("source"), *entry.get("open_sources", [])]
        assert {s for s in cited if s} <= set(data["sources"]), entry["id"]
    assert sum(1 for e in entries if e.get("next")) == 10


def test_coverage_json_counts_the_covered_top_entries(library: Path, tmp_path: Path) -> None:
    shutil.copy(KIT / "coverage.yaml", library / "coverage.yaml")
    _edit(library / "coverage.yaml", lambda d: next(e for e in d["entries"] if e["id"] == "hydrogen").update(covered_by=[{"process": "fixture-electrolysis", "tier": 2}]))
    report = build_catalog.build(library, tmp_path / "out", None, commit="fixture")
    coverage = _json(tmp_path / "out" / "coverage.json")
    # asu-1 is not in the fixture library: its entry counts as uncovered here
    assert coverage["summary"] == {"basis": build_catalog.SUMMARY_BASIS, "top": 50, "covered": 1, "by_tier": {"2": 1}}
    assert any("covered_by unknown process 'asu-1'" in e for e in report.errors)
    assert [e["id"] for e in coverage["entries"]][:3] == ["ammonia", "hydrogen", "air-separation"]


def test_library_without_coverage_writes_none(tmp_path: Path) -> None:
    build_catalog.build(LIBRARY, tmp_path / "out", None, commit="fixture")
    assert not (tmp_path / "out" / "coverage.json").exists()


def test_the_library_coverage_counts_asu_1(tmp_path: Path) -> None:
    report = build_catalog.build(KIT, tmp_path / "out", None, commit="fixture")
    assert report.errors == []
    coverage = _json(tmp_path / "out" / "coverage.json")
    assert coverage["summary"]["covered"] >= 1
    air = next(e for e in coverage["entries"] if e["id"] == "air-separation")
    assert air["covered_by"][0]["process"] == "asu-1"


def test_docs_table_follows_coverage_yaml() -> None:
    import re

    rows = re.findall(r"^\| (\d+) \| `([a-z0-9-]+)`", (KIT / "docs" / "coverage.md").read_text(encoding="utf-8"), re.M)
    expected = [(str(e["rank"]), e["id"]) for e in sorted(_yaml(KIT / "coverage.yaml")["entries"], key=lambda e: e["rank"])]
    assert rows == expected, "regenerate the table in docs/coverage.md from coverage.yaml"
