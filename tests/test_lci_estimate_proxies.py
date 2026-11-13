"""Estimate proxies that name library products (ADR 0039): the mass on the stated basis, a
missing product, a circular link, a library producer's precedence, the estimate marked in the
exported dataset (flag, pedigree penalty, recomputed DQR) and the public build."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")
openpyxl = pytest.importorskip("openpyxl")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import build_lci  # noqa: E402

LIBRARY = KIT / "tests" / "fixtures" / "library"
DB = "cheme-as-code-atlas-0.1.0"
H2 = "fixture-electrolysis:fixture-electrolysis:product:H2"
H2_PATH = "processes/fixture-electrolysis/lca/dataset.yaml"
NH3 = "fixture-ammonia:fixture-ammonia-hb:product:ammonia"
NH3_PATH = "processes/fixture-ammonia/lca/datasets/ammonia.yaml"
USER = "fixture-user:fixture-user-blend:product:blend"
#: the consumer's pedigree; the fifth (technological) score is raised to 4 by the proxy
PEDIGREE = [2, 3, 1, 2, 2]


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(LIBRARY, copy)
    return copy


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _proxy(library: Path, **changes) -> None:
    """The fixture mappings get an estimate proxy ``solvent`` for the registry's unused-solvent:
    0.2 kg of fixture-electrolysis's hydrogen (a library product) and 0.8 kg of background water
    per kg, on a mass basis, and the technosphere entry that uses it."""
    path = library / "lci" / "mappings.yaml"
    data = yaml.safe_load(path.read_text())
    proxy = {
        "name": "solvent, from hydrogen and water (fixture estimate proxy)",
        "reference_product": "solvent, estimated",
        "unit": "kilogram",
        "location": "GLO",
        "chemical": "unused-solvent",
        "basis": "mass",
        "inputs": [
            {"dataset": {"path": H2_PATH, "product": "product:H2"}, "amount": 0.2, "source": "fixture: the hydrogen share"},
            {"use": "water", "amount": 0.8, "source": "fixture: the water share"},
        ],
        "source": "fixture estimate proxy",
    }
    proxy.update(changes)
    data.setdefault("proxies", {})["solvent"] = proxy
    data["technosphere"]["unused-solvent"] = {"proxy": "solvent", "source": "fixture: the estimate proxy stands for it"}
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _process(library: Path, pid: str, exchanges: list[dict], outputs: list[dict], public: bool = False) -> None:
    """A manifest-only process with one hand-written dataset ``<pid>-blend``."""
    folder = library / "processes" / pid
    (folder / "lca" / "datasets").mkdir(parents=True)
    manifest = {
        "schema": "cheme-as-code/process/v1", "id": pid, "title": f"Fixture: {pid}", "summary": "Synthetic test process; not engineering data.",
        "families": ["ammonia"], "facets": {"product_classes": ["fertilizers"], "unit_operations": ["reaction"]}, "maturity": "screening",
        "validation": {"status": "unreviewed"}, "chemistry": {"outputs": outputs}, "references": [{"title": "Fixture reference", "doi": "10.0000/fixture.1"}],
    }
    if public:
        manifest["publication"] = {"status": "public", "license": "CC-BY-4.0"}
    (folder / "process.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
    dataset = {"schema": "cheme/lci_dataset/v2", "kind": "lci_dataset", "id": f"{pid}-blend", "title": f"Fixture: {pid}", "basis": "1 t of product",
               "exchanges": exchanges, "provenance": {"generator": "hand-written fixture"}}
    (folder / "lca" / "datasets" / "blend.yaml").write_text(yaml.safe_dump(dataset, sort_keys=False))


def _consumer(library: Path, public: bool = False) -> None:
    """fixture-user blends 5 kg of the solvent (through the estimate proxy) per tonne."""
    _process(
        library, "fixture-user",
        [
            {"key": "feed:SOLVENT", "title": "Solvent", "type": "input", "amount": 5.0, "unit": "kg", "pedigree": {"scores": PEDIGREE, "reason": "fixture"}, "basic_uncertainty": 1.05},
            {"key": "feed:electricity", "title": "Mixer", "type": "input", "amount": 10.0, "unit": "kWh"},
            {"key": "product:blend", "title": "Blend", "type": "product", "amount": 1000.0, "unit": "kg"},
        ],
        [{"chemical": "ammonia", "role": "main-product", "inventory_key": "product:blend"}],
        public,
    )
    (library / "processes" / "fixture-user" / "lca" / "mappings.yaml").write_text(
        yaml.safe_dump({"schema": "cheme-as-code/lci-process-mappings/v1", "exchanges": {"feed:SOLVENT": {"use": "unused-solvent", "source": "fixture"}}})
    )


def _build(library: Path, out: Path, **kwargs) -> build_lci.Report:
    return build_lci.build(library, out, "0.1.0", commit="fixture", **kwargs)


def _activities(xlsx: Path) -> dict[str, dict]:
    """The workbook's activities by code, as bw2io's ExcelImporter reads them."""
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    found: dict[str, dict] = {}
    for ws in wb:
        rows = [list(r) for r in ws.iter_rows(values_only=True)]
        if rows and rows[0][0] == "skip":
            continue
        current, columns = None, None
        for row in rows:
            first = row[0] if row else None
            if first == "Activity":
                current, columns = {"meta": {}, "exchanges": []}, None
            elif current is None or first is None:
                continue
            elif first == "Exchanges":
                columns = []
            elif columns == []:
                columns = [c for c in row if c is not None]
            elif columns:
                current["exchanges"].append({c: v for c, v in zip(columns, row) if v is not None})
            else:
                current["meta"][first] = row[1]
                if first == "code":
                    found[row[1]] = current
    return found


def _exchange(activity: dict, key: str) -> dict:
    return next(e for e in activity["exchanges"] if e.get("atlas key") == key)


def test_a_proxy_links_a_library_product_and_the_consumer_is_marked_an_estimate(library: Path, tmp_path: Path) -> None:
    _proxy(library)
    _consumer(library)
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == [] and report.gaps == [], (report.errors, report.gaps)

    activities = _activities(out / "lci" / f"{DB}.xlsx")
    user = activities[USER]
    solvent = _exchange(user, "feed:SOLVENT")
    assert (solvent["name"], solvent["database"], solvent["atlas proxy"]) == ("solvent, from hydrogen and water (fixture estimate proxy)", DB, "solvent")
    assert solvent["atlas estimate"].startswith("ESTIMATE (ADR 0039): linked to proxy:solvent") and "technological correlation 2 -> 4" in solvent["atlas estimate"]
    assert solvent["atlas pedigree"] == "2,3,1,2,4"  # the penalty, and the lognormal it implies
    penalised = build_lci.pedigree_gsd2([2, 3, 1, 2, 4], 1.05)
    assert solvent["scale"] == pytest.approx(build_lci.math.log(penalised) / 2, rel=1e-9)
    assert user["meta"]["atlas estimates"] == 1 and "ESTIMATE: 1 exchange(s)" in user["meta"]["comment"]
    assert "atlas proxy" not in _exchange(user, "feed:electricity")

    # the proxy's library product is linked inside the Atlas, its background input by name
    proxy = activities["proxy:solvent"]
    assert proxy["meta"]["atlas estimate"] is True and proxy["meta"]["atlas basis"] == "mass"
    hydrogen = next(e for e in proxy["exchanges"] if e.get("atlas code") == H2)
    assert (hydrogen["amount"], hydrogen["database"], hydrogen["atlas link"]) == (0.2, DB, "proxy")
    assert hydrogen["atlas check"].startswith("compatible")
    water = _exchange(proxy, "proxy:water")
    assert water["amount"] == 0.8 and water["name"] == "market for water, deionised"

    package = _json(out / "lci" / "datapackage.json")
    page = next(a for a in package["activities"] if a["code"] == USER)
    assert page["estimated"] is True and page["estimates"] == 1
    entry = next(e for e in page["exchanges"] if e["key"] == "feed:SOLVENT")
    assert entry["estimate"]["proxy"] == "proxy:solvent" and entry["estimate"]["pedigree_before"] == PEDIGREE
    assert entry["pedigree"]["scores"] == [2, 3, 1, 2, 4] and entry["atlas"]["code"] == "proxy:solvent"
    proxy_page = next(a for a in package["activities"] if a["code"] == "proxy:solvent")
    assert proxy_page["estimate"] == {"chemical": "unused-solvent", "basis": "mass"} and proxy_page["estimated"] is True
    assert proxy_page["publication"] == "public" and proxy_page["preliminary"] is False  # fixture-electrolysis is public, without gaps
    assert ("proxy:solvent", H2, "proxy") in [(link["consumer"], link["provider"], link["kind"]) for link in package["atlas_links"]]
    # a dataset without a data quality rating records the penalty only
    dataset = next(p for p in package["processes"] if p["id"] == "fixture-user")["datasets"][0]
    assert dataset["data_quality"]["proxy_penalty"]["exchanges"] == ["feed:SOLVENT"]
    assert dataset["data_quality"]["proxy_penalty"]["recomputed"] is False


def test_the_dqr_is_recomputed_with_the_penalty(library: Path, tmp_path: Path) -> None:
    _proxy(library)
    _consumer(library)
    path = library / "processes" / "fixture-user" / "lca" / "datasets" / "blend.yaml"
    data = yaml.safe_load(path.read_text())
    data["exchanges"][1].update({"pedigree": {"scores": [4, 4, 1, 3, 3], "reason": "fixture"}, "basic_uncertainty": 1.05})
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    dataset = build_lci.Dataset(str(path), data, {}, "default", {}, data_quality={
        "TeR": 2.5, "GeR": 2.5, "TiR": 1.0, "dqr": 2.0, "P": 3.0, "C": 3.5, "dqr_pef": 2.25, "primary_share": 0.0,
        "weighted": False, "basis": "unit process (unweighted)", "weakest": "TeR", "exchanges": 2,
    })
    rating = build_lci.penalised_rating(dataset, {"feed:SOLVENT": (PEDIGREE, [2, 3, 1, 2, 4])})
    # TeR (4 + 3) / 2, DQR (3.5 + 2.5 + 1) / 3, DQR_PEF (3.5 + 2.5 + 1 + 3) / 4
    assert (rating["TeR"], rating["dqr"], rating["dqr_pef"], rating["weakest"]) == (3.5, 2.3333, 2.5, "TeR")
    assert rating["proxy_penalty"]["recomputed"] is True and rating["proxy_penalty"]["before"]["dqr"] == 2.0
    # a weighted rating is not recomputed: the exported pedigrees carry the penalty
    weighted = build_lci.penalised_rating(build_lci.Dataset(str(path), data, {}, "default", {}, data_quality={**dataset.data_quality, "weighted": True}), {"feed:SOLVENT": (PEDIGREE, [2, 3, 1, 2, 4])})
    assert weighted["TeR"] == 2.5 and weighted["proxy_penalty"]["recomputed"] is False


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"inputs": [{"dataset": {"path": H2_PATH, "product": "product:H2"}, "amount": 0.3, "source": "fixture"}, {"use": "water", "amount": 0.8, "source": "fixture"}]},
         "mass not conserved on its mass basis"),
        ({"unit": "kilowatt hour"}, "the proxy must be in kilogram"),
        ({"inputs": [{"use": "electricity", "amount": 1.0, "source": "fixture"}]}, "input 'electricity' is in kilowatt hour, not kilogram"),
    ],
    ids=["mass", "proxy-unit", "input-unit"],
)
def test_the_mass_on_the_basis_is_conserved(library: Path, tmp_path: Path, changes: dict, message: str) -> None:
    _proxy(library, **changes)
    report = _build(library, tmp_path / "out")
    assert any("proxies.solvent" in e and message in e for e in report.errors), report.errors


def test_a_declared_non_mass_basis_is_not_mass_checked(library: Path, tmp_path: Path) -> None:
    _proxy(library, basis="non-mass", basis_reason="fixture: the amounts conserve the hydrogen's energy, not mass",
           inputs=[{"dataset": {"path": H2_PATH, "product": "product:H2"}, "amount": 0.3, "source": "fixture"}, {"use": "water", "amount": 0.8, "source": "fixture"}])
    _consumer(library)
    report = _build(library, tmp_path / "out")
    assert report.errors == [], report.errors
    # without basis_reason the schema refuses it, and a library product needs a basis
    _proxy(library, basis="non-mass")
    assert any("basis_reason" in e for e in _build(library, tmp_path / "again").errors)
    _proxy(library, basis=None, chemical=None)
    data = yaml.safe_load((library / "lci" / "mappings.yaml").read_text())
    for key in ("basis", "chemical"):
        del data["proxies"]["solvent"][key]
    (library / "lci" / "mappings.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    assert any("proxies/solvent" in e for e in _build(library, tmp_path / "third").errors)


def test_a_missing_product_is_refused(library: Path, tmp_path: Path) -> None:
    _proxy(library, inputs=[{"dataset": {"path": H2_PATH, "product": "product:NOPE"}, "amount": 0.2, "source": "fixture"}, {"use": "water", "amount": 0.8, "source": "fixture"}])
    _consumer(library)
    report = _build(library, tmp_path / "out")
    assert any("proxies.solvent" in e and f"input {H2_PATH}#product:NOPE is not a product of this library" in e for e in report.errors), report.errors
    # reported once, and the exchange is not linked to the refused proxy
    assert sum("proxies.solvent" in e for e in report.errors) == 1
    # a proxy no exchange uses is not checked against the datasets (a library holding part of the processes)
    (library / "processes" / "fixture-user" / "lca" / "mappings.yaml").unlink()
    data = yaml.safe_load((library / "processes" / "fixture-user" / "lca" / "datasets" / "blend.yaml").read_text())
    data["exchanges"] = [e for e in data["exchanges"] if e["key"] != "feed:SOLVENT"]
    (library / "processes" / "fixture-user" / "lca" / "datasets" / "blend.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
    assert _build(library, tmp_path / "unused").errors == []


def test_a_content_the_product_does_not_state_is_refused(library: Path, tmp_path: Path) -> None:
    _process(library, "fixture-acid", [{"key": "feed:electricity", "title": "Power", "type": "input", "amount": 1.0, "unit": "kWh"},
                                       {"key": "product:acid", "title": "Acid 30 %", "type": "product", "amount": 1000.0, "unit": "kg",
                                        "composition": {"fractions": {"HCl": 0.3, "H2O": 0.7}, "formulas": {"HCl": "HCl", "H2O": "H2O"}}}],
             [{"chemical": "water", "role": "main-product", "inventory_key": "product:acid"}])
    _consumer(library)
    acid = "processes/fixture-acid/lca/datasets/blend.yaml"
    _proxy(library, inputs=[{"dataset": {"path": acid, "product": "product:acid"}, "amount": 0.5, "content": {"component": "HCl", "fraction": 0.4}, "source": "fixture"},
                            {"use": "water", "amount": 0.8, "source": "fixture"}])
    report = _build(library, tmp_path / "out")
    assert any("content HCl 0.4, but the product's composition states 0.3" in e for e in report.errors), report.errors


@pytest.mark.parametrize("composition", [{"fractions": {"HCl": 0.3, "H2O": 0.7}, "formulas": {"HCl": "HCl", "H2O": "H2O"}}, None], ids=["other-components", "no-composition"])
def test_a_content_component_the_product_does_not_contain_is_refused(library: Path, tmp_path: Path, composition: dict | None) -> None:
    # the fraction is checked, never taken on trust: NaCl is not in the acid's composition (or it has none)
    product = {"key": "product:acid", "title": "Acid 30 %", "type": "product", "amount": 1000.0, "unit": "kg"}
    if composition:
        product["composition"] = composition
    _process(library, "fixture-acid", [{"key": "feed:electricity", "title": "Power", "type": "input", "amount": 1.0, "unit": "kWh"}, product],
             [{"chemical": "water", "role": "main-product", "inventory_key": "product:acid"}])
    _consumer(library)
    acid = "processes/fixture-acid/lca/datasets/blend.yaml"
    _proxy(library, inputs=[{"dataset": {"path": acid, "product": "product:acid"}, "amount": 0.5, "content": {"component": "NaCl", "fraction": 0.4}, "source": "fixture"},
                            {"use": "water", "amount": 0.8, "source": "fixture"}])
    report = _build(library, tmp_path / "out")
    stated = "states H2O, HCl, not NaCl" if composition else "states no composition, not NaCl"
    assert any("proxies.solvent" in e and f"content NaCl 0.4, but the product's composition {stated}: the fraction cannot be checked" in e for e in report.errors), report.errors
    assert not any(e.get("atlas proxy") for e in _activities_or_empty(tmp_path / "out").get(USER, {}).get("exchanges", []))


def test_a_content_on_a_background_input_is_refused(library: Path, tmp_path: Path) -> None:
    # a background entry states no composition, so its content could never be checked: without the
    # refusal any fraction would balance the mass (here 0.2 + 1.6 x 0.5 = 1 kg per kg)
    _proxy(library, inputs=[{"dataset": {"path": H2_PATH, "product": "product:H2"}, "amount": 0.2, "source": "fixture"},
                            {"use": "water", "amount": 1.6, "content": {"component": "H2O", "fraction": 0.5}, "source": "fixture"}])
    _consumer(library)
    report = _build(library, tmp_path / "out")
    assert any("proxies/solvent/inputs/1" in e and "'dataset' is a dependency of 'content'" in e for e in report.errors), report.errors
    assert not any(e.get("atlas proxy") for e in _activities_or_empty(tmp_path / "out").get(USER, {}).get("exchanges", []))


def _activities_or_empty(out: Path) -> dict[str, dict]:
    xlsx = out / "lci" / f"{DB}.xlsx"
    return _activities(xlsx) if xlsx.is_file() else {}


def test_a_circular_link_is_refused(library: Path, tmp_path: Path) -> None:
    # the proxy rests on fixture-user's own blend, which consumes the proxy
    _consumer(library)
    _proxy(library, inputs=[{"dataset": {"path": "processes/fixture-user/lca/datasets/blend.yaml", "product": "product:blend"}, "amount": 1.0, "source": "fixture"}])
    report = _build(library, tmp_path / "out")
    assert any("proxies.solvent" in e and f"circular link: proxy:solvent -> {USER} -> proxy:solvent" in e for e in report.errors), report.errors


def test_a_dedicated_producer_takes_precedence_over_the_proxy(library: Path, tmp_path: Path) -> None:
    _proxy(library)
    _consumer(library)
    _process(library, "fixture-solvent", [{"key": "feed:electricity", "title": "Power", "type": "input", "amount": 50.0, "unit": "kWh"},
                                          {"key": "product:solvent", "title": "Solvent", "type": "product", "amount": 1000.0, "unit": "kg"}],
             [{"chemical": "unused-solvent", "role": "main-product", "inventory_key": "product:solvent"}])
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == [], report.errors
    producer = "fixture-solvent:fixture-solvent-blend:product:solvent"
    solvent = _exchange(_activities(out / "lci" / f"{DB}.xlsx")[USER], "feed:SOLVENT")
    assert (solvent["name"], solvent["database"], solvent["atlas code"], solvent["atlas link"]) == ("Fixture: fixture-solvent", DB, producer, "plant")
    assert "atlas proxy" not in solvent and "atlas estimate" not in solvent and solvent["atlas pedigree"] == "2,3,1,2,2"
    assert "proxy:solvent" not in _activities(out / "lci" / f"{DB}.xlsx")  # not exported: nothing uses it
    advisory = [w for w in report.advisories if "estimate proxy 'solvent' is not used" in w]
    assert advisory and producer in advisory[0] and not [w for w in report.strict_failures if "solvent" in w and "proxy" in w]


def test_a_public_build_without_the_product_leaves_a_gap(library: Path, tmp_path: Path) -> None:
    # the proxy names fixture-ammonia's ammonia (not public); fixture-user is public
    _proxy(library, inputs=[{"dataset": {"path": NH3_PATH, "product": "product:ammonia"}, "amount": 1.0, "source": "fixture"}])
    _consumer(library, public=True)
    preview = _build(library, tmp_path / "preview")
    assert preview.errors == [], preview.errors
    page = next(a for a in _json(tmp_path / "preview" / "lci" / "datapackage.json")["activities"] if a["code"] == "proxy:solvent")
    assert page["publication"] == "preview"  # it rests on an unpublished process

    out = tmp_path / "public"
    report = _build(library, out, public=True)
    assert report.errors == [], report.errors
    assert [(g["process"], g["key"]) for g in report.gaps] == [("fixture-user", "feed:SOLVENT")]
    assert "which this build cannot use" in report.gaps[0]["reason"]
    solvent = _exchange(_activities(out / "lci" / f"{DB}.xlsx")[USER], "feed:SOLVENT")
    assert "atlas gap" in solvent and "database" not in solvent
    assert not any(a["code"] == "proxy:solvent" for a in _json(out / "lci" / "datapackage.json")["activities"])


def test_the_library_proxy_for_chlorosulfonic_acid_conserves_mass() -> None:
    mappings = build_lci.load_mappings(KIT / "lci" / "mappings.yaml")
    proxy = mappings["proxies"]["chlorosulfonic-acid"]
    assert (proxy["chemical"], proxy["basis"]) == ("chlorosulfonic-acid", "stoichiometric")
    assert build_lci._proxy_mass(proxy) == pytest.approx(1.0, abs=1e-5)
    hcl = next(i for i in proxy["inputs"] if "dataset" in i)
    assert hcl["dataset"] == {"path": "processes/hydrogen-chloride-1/lca/dataset.yaml", "product": "product:HCLACID"}
    assert hcl["amount"] * hcl["content"]["fraction"] == pytest.approx(36.458 / 116.515, rel=1e-5)


def _producer(library: Path, public: bool = False) -> str:
    """fixture-solvent: a dedicated library producer of unused-solvent (the proxy's chemical)."""
    _process(library, "fixture-solvent", [{"key": "feed:electricity", "title": "Power", "type": "input", "amount": 50.0, "unit": "kWh"},
                                          {"key": "product:solvent", "title": "Solvent", "type": "product", "amount": 1000.0, "unit": "kg"}],
             [{"chemical": "unused-solvent", "role": "main-product", "inventory_key": "product:solvent"}], public)
    return "fixture-solvent:fixture-solvent-blend:product:solvent"


def _linked_to_producer(report: build_lci.Report, out: Path, producer: str) -> None:
    assert report.errors == [] and report.gaps == [] and report.estimates == [], (report.errors, report.gaps, report.estimates)
    activities = _activities(out / "lci" / f"{DB}.xlsx")
    solvent = _exchange(activities[USER], "feed:SOLVENT")
    assert (solvent["database"], solvent["atlas code"], solvent["atlas link"]) == (DB, producer, "plant")
    assert "atlas proxy" not in solvent and "atlas estimate" not in solvent and "atlas gap" not in solvent
    assert "proxy:solvent" not in activities
    assert any("estimate proxy 'solvent' is not used" in w and producer in w for w in report.advisories), report.warnings


@pytest.mark.parametrize("public", [False, True], ids=["preview", "public"])
def test_a_dedicated_producer_takes_precedence_over_an_unavailable_proxy(library: Path, tmp_path: Path, public: bool) -> None:
    # the proxy names fixture-ammonia's ammonia, which a public build does not hold; a public producer exists
    _proxy(library, inputs=[{"dataset": {"path": NH3_PATH, "product": "product:ammonia"}, "amount": 1.0, "source": "fixture"}])
    _consumer(library, public=True)
    producer = _producer(library, public=True)
    out = tmp_path / "out"
    report = _build(library, out, public=public)
    _linked_to_producer(report, out, producer)
    if public:
        assert any("unavailable in this build" in w for w in report.advisories), report.advisories


@pytest.mark.parametrize("public", [False, True], ids=["preview", "public"])
def test_a_dedicated_producer_takes_precedence_over_a_refused_proxy(library: Path, tmp_path: Path, public: bool) -> None:
    # a refused proxy (a missing product) is no error while a library producer is linked instead
    _proxy(library, inputs=[{"dataset": {"path": H2_PATH, "product": "product:NOPE"}, "amount": 0.2, "source": "fixture"}, {"use": "water", "amount": 0.8, "source": "fixture"}])
    _consumer(library, public=True)
    producer = _producer(library, public=True)
    out = tmp_path / "out"
    report = _build(library, out, public=public)
    _linked_to_producer(report, out, producer)
    assert any("it is also refused" in w for w in report.advisories), report.advisories


def test_the_estimates_are_listed_per_process_and_in_the_catalog(library: Path, tmp_path: Path) -> None:
    import build_catalog

    _proxy(library)
    _consumer(library, public=True)
    out = tmp_path / "out"
    report = _build(library, out)
    assert report.errors == [] and report.gaps == [], (report.errors, report.gaps)
    assert [(e["process"], e["key"], e["proxy"]) for e in report.estimates] == [("fixture-user", "feed:SOLVENT", "proxy:solvent")]
    package = _json(out / "lci" / "datapackage.json")
    entry = next(p for p in package["processes"] if p["id"] == "fixture-user")
    assert (entry["estimated"], entry["estimate_count"], entry["preliminary"]) == (True, 1, False)  # install() links it: not a gap
    assert entry["estimates"][0]["chemical"] == "unused-solvent" and entry["estimates"][0]["basis"] == "mass"
    index = _json(out / "lci" / "index.json")
    assert index["estimated"] == ["fixture-user"] and index["estimates"] == {"fixture-user": 1} and "fixture-user" not in index["preliminary"]
    assert all(a.get("estimated") is True for a in index["processes"]["fixture-user"])
    assert any(c.startswith("ESTIMATED: 1 exchange(s) of 1 process(es)") for c in index["caveats"])

    # the catalog: no gap is left, but the entry stays preliminary and says it is estimated
    manifest = library / "processes" / "fixture-user" / "process.yaml"
    data = yaml.safe_load(manifest.read_text())
    data["chemistry"]["inputs"] = [{"chemical": "unused-solvent", "role": "feedstock", "inventory_key": "feed:SOLVENT"}]
    manifest.write_text(yaml.safe_dump(data, sort_keys=False))
    for public in (False, True):
        catalog = tmp_path / f"catalog-{public}"
        assert not build_catalog.build(library, catalog, None, commit="fixture", public=public).errors
        summary = next(p for p in _json(catalog / "catalog.json")["processes"] if p["id"] == "fixture-user")
        assert (summary["preliminary"], summary["gap_count"], summary["estimated"], summary["estimate_count"]) == (True, 0, True, 1)
        detail = _json(catalog / "processes" / "fixture-user.json")
        assert (detail["preliminary"], detail["estimated"], detail["estimate_count"]) == (True, True, 1)
        assert detail["lci_estimates"] == [{"dataset": "fixture-user-blend", "key": "feed:SOLVENT", "proxy": "proxy:solvent", "chemical": "unused-solvent", "basis": "mass"}]
        other = next(p for p in _json(catalog / "catalog.json")["processes"] if p["id"] == "fixture-electrolysis")
        assert (other["preliminary"], other["estimated"], other["estimate_count"]) == (False, False, 0)
