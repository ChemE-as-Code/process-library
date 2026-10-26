"""Market datasets (markets/*.yaml, issue #49): loading and checks, the market activities of the
LCI build (shares, transport, losses), the default link of an Atlas input to its market with the
plant beside it, and the compatibility check of every Atlas-to-Atlas link."""

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
import markets as mk  # noqa: E402
import registry as reg  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
ASU = FIXTURES / "asu-lca"
SCHEMA = KIT / "schemas" / "markets.schema.json"
LIN = "asu-1:asu-1-500-t-d-gox:product:LIN"
LIN_MARKET = "market:nitrogen/lin:RER"
USER = "fixture-lin-user:fixture-lin-user-inerting:product:INERTING"
H2 = "fixture-electrolysis:fixture-electrolysis:product:H2"
NH3 = "fixture-ammonia:fixture-ammonia-hb:product:ammonia"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _registry(path: Path = KIT / "chemicals" / "chemicals.yaml") -> reg.Registry:
    return reg.load(yaml.safe_load(path.read_text(encoding="utf-8")))


def _asu_library(tmp: Path, user: bool = True) -> Path:
    """ASU-1 (the fixture copy of its dataset), the real registry and markets, and the downstream
    LIN consumer; no lci/: the builder uses the library's lci/mappings.yaml."""
    library = tmp / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml"):
        shutil.copy(ASU / name, library / "processes" / "asu-1" / "lca")
    shutil.copytree(KIT / "chemicals", library / "chemicals")
    shutil.copytree(KIT / "markets", library / "markets")
    if user:
        shutil.copytree(FIXTURES / "lin-user", library / "processes" / "fixture-lin-user")
    return library


def _activities(out: Path) -> dict[str, dict]:
    return build_lci.read_workbook(next((out / "lci").glob("*.xlsx")))


def _exchange(activity: dict, key: str) -> dict:
    return next(e for e in activity["exchanges"] if e.get("atlas key") == key)


def _edit(path: Path, change) -> None:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# --- the library's markets -------------------------------------------------------------------


def test_library_markets_load_without_problems() -> None:
    markets, problems = mk.load(KIT / "markets", SCHEMA, _registry(), KIT)
    assert problems == []
    assert sorted(m.code for m in markets) == [
        "market:argon/gar:RER", "market:argon/lar:RER", "market:nitrogen/gan-8barg-10ppm:RER", LIN_MARKET,
        "market:oxygen/gox-30barg-99.5:RER", "market:oxygen/lox:RER",
    ]
    # every number has a status and a source; nothing in the liquid markets is presented as cited
    for market in markets:
        for fact in market.facts():
            assert fact["status"] in ("cited", "calculated", "assumed") and len(fact["source"]) >= 10
            if fact["status"] == "assumed":
                assert "ASSUMED" in fact["source"], (market.code, fact["what"])


def test_asu_markets_are_exported_with_transport_and_losses(tmp_path: Path) -> None:
    library = _asu_library(tmp_path, user=False)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    package = _json(tmp_path / "out" / "lci" / "datapackage.json")
    status = {m["code"]: m["status"] for m in package["markets"]}
    assert status == {
        "market:argon/gar:RER": "planned", "market:argon/lar:RER": "planned", "market:nitrogen/gan-8barg-10ppm:RER": "exported",
        LIN_MARKET: "exported", "market:oxygen/gox-30barg-99.5:RER": "exported", "market:oxygen/lox:RER": "exported",
    }
    assert "argon column" in next(m for m in package["markets"] if m["code"] == "market:argon/lar:RER")["reason"]
    index = _json(tmp_path / "out" / "lci" / "index.json")
    assert [m["code"] for m in index["markets"]] == sorted(c for c, s in status.items() if s == "exported")

    lin = _activities(tmp_path / "out")[LIN_MARKET]
    assert (lin["name"], lin["meta"]["reference product"], lin["meta"]["location"]) == ("market for nitrogen, liquid", "Nitrogen, liquid", "RER")
    gross = 1 / (0.995 * 0.99)  # boil-off 0.5 %, transfer 1 %: the losses multiply
    supply = _exchange(lin, "supplier:asu-1")
    assert supply["amount"] == pytest.approx(gross, rel=1e-11) and supply["atlas code"] == LIN and supply["atlas link"] == "supply"
    assert supply["database"] == "cheme-as-code-atlas-0.1.0" and supply["reference product"] == "Nitrogen, liquid"
    assert supply["atlas check"].startswith("compatible: grade nitrogen/lin")
    trailer = _exchange(lin, "distribution:cryogenic-trailer")  # 100 km of the loaded mass
    assert trailer["unit"] == "ton kilometer" and trailer["amount"] == pytest.approx(gross * 100 / 1000, rel=1e-11)
    assert trailer["name"] == "market for transport, freight, lorry, unspecified"
    assert not [e for e in lin["exchanges"] if e["type"] == "biosphere"]  # N2 is an atmospheric constituent
    assert "released as N2" in lin["meta"]["comment"] and "pass_through" in lin["meta"]["comment"]
    assert "equals production" in lin["meta"]["comment"]

    gox = _activities(tmp_path / "out")["market:oxygen/gox-30barg-99.5:RER"]
    assert [e["type"] for e in gox["exchanges"]] == ["production", "technosphere"]  # pipeline: no transport activity, no leakage
    assert _exchange(gox, "supplier:asu-1")["amount"] == 1
    assert any("Markets (code market:*)" in c for c in package["caveats"])


# --- issue #49 acceptance: a consumer of "nitrogen, liquid" links to the market ------------------


def test_a_consumer_of_liquid_nitrogen_links_to_the_market(tmp_path: Path) -> None:
    library = _asu_library(tmp_path)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    lin = _exchange(_activities(tmp_path / "out")[USER], "feed:LIN")
    assert lin["name"] == "market for nitrogen, liquid" and "database" not in lin  # the background link stays the default
    assert (lin["atlas code"], lin["atlas link"], lin["atlas activity"], lin["atlas location"]) == (LIN_MARKET, "market", "market for nitrogen, liquid", "RER")
    assert lin["atlas check"].startswith("compatible: grade nitrogen/lin (Nitrogen, liquid); unit kilogram; system model cutoff")
    assert "boundary delivered (production-mix, RER: transport and losses included)" in lin["atlas check"]
    # the plant beside it, for pinning: ASU-1's LIN, never its pipeline GAN (another grade)
    assert lin["atlas plant code"] == LIN and lin["atlas plant reference product"] == "Nitrogen, liquid"

    links = {(l["consumer"], l["key"]): l for l in _json(tmp_path / "out" / "lci" / "datapackage.json")["atlas_links"]}
    chain = links[(USER, "feed:LIN")]
    assert (chain["provider"], chain["kind"], chain["plant"], chain["compatible"]) == (LIN_MARKET, "market", LIN, True)
    assert set(chain["checks"]) == {"grade", "unit", "system_model", "allocation", "boundary"}
    assert chain["checks"]["allocation"] == {"status": "ok", "text": "exergy (physical-exergy)"}
    assert links[(LIN_MARKET, "supplier:asu-1")]["provider"] == LIN


def test_without_a_market_the_link_to_the_plant_gate_is_a_warning(tmp_path: Path) -> None:
    library = _asu_library(tmp_path)
    (library / "markets" / "nitrogen.yaml").unlink()
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == []
    (warning,) = report.warnings
    assert "fixture-lin-user: feed:LIN" in warning and "no market of nitrogen/lin" in warning and "plant gate" in warning
    lin = _exchange(_activities(tmp_path / "out")[USER], "feed:LIN")
    assert (lin["atlas code"], lin["atlas link"]) == (LIN, "plant") and "atlas plant activity" not in lin
    assert "boundary plant gate: no market of this grade" in lin["atlas check"]


def test_a_producer_of_another_grade_is_refused(tmp_path: Path) -> None:
    library = _asu_library(tmp_path)
    # the consumer wants LOX: ASU-1 makes it, but no producer of a nitrogen grade may stand in
    _edit(library / "processes" / "fixture-lin-user" / "process.yaml", lambda d: d["chemistry"]["inputs"][0].update(chemical="nitrogen/lin-99999"))
    _edit(library / "chemicals" / "chemicals.yaml", lambda d: next(c for c in d["chemicals"] if c["slug"] == "nitrogen")["grades"].append(
        {"slug": "lin-99999", "name": "Nitrogen, liquid, 99.999 %", "phase": "liquid"}))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    lin = _exchange(_activities(tmp_path / "out")[USER], "feed:LIN")
    assert "atlas activity" not in lin  # stays with the background
    refused = next(l for l in _json(tmp_path / "out" / "lci" / "datapackage.json")["atlas_links"] if l["kind"] == "refused")
    assert refused["consumer"] == USER and "nitrogen/lin, the input is nitrogen/lin-99999" in refused["checks"]["grade"]["text"]


def test_link_dataset_pins_the_plant_and_is_checked(tmp_path: Path) -> None:
    library = _asu_library(tmp_path)
    path = library / "processes" / "fixture-lin-user" / "lca" / "datasets" / "inerting.yaml"
    _edit(path, lambda d: d["exchanges"][0].update(link={"dataset": {"path": "processes/asu-1/lca/dataset.yaml", "product": "LIN"}}))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    lin = _exchange(_activities(tmp_path / "out")[USER], "feed:LIN")
    assert lin["database"] == "cheme-as-code-atlas-0.1.0" and lin["atlas code"] == LIN and lin["atlas link"] == "pinned"
    assert "boundary plant gate (pinned)" in lin["atlas check"]


# --- layers, regions, imports ----------------------------------------------------------------


@pytest.fixture
def library(tmp_path: Path) -> Path:
    copy = tmp_path / "library"
    shutil.copytree(FIXTURES / "library", copy)
    return copy


def _markets(library: Path, *entries: dict) -> None:
    _edit(library / "markets" / "hydrogen.yaml", lambda d: d["markets"].extend(entries))


def test_consumption_mix_with_imports_and_a_technology_market(library: Path, tmp_path: Path) -> None:
    _markets(
        library,
        {
            "product": "hydrogen", "region": "DE", "layer": "consumption-mix", "trade_source": "fixture: synthetic trade shares",
            "suppliers": [
                {"process": "fixture-electrolysis", "share": {"value": 0.6, "status": "assumed", "source": "fixture: domestic share"}},
                {"market": "GLO", "share": {"value": 0.4, "status": "assumed", "source": "fixture: import share"},
                 "transport": [{"mode": "pipeline", "distance": {"value": 300, "unit": "km", "status": "assumed", "source": "fixture: import pipeline"}}]},
            ],
            "losses": [{"kind": "pipeline-leakage", "fraction": 0.01, "released_as": "H2", "status": "assumed", "source": "fixture: leakage"}],
        },
        {
            "product": "hydrogen", "region": "GLO", "layer": "technology", "technology": "pem",
            "suppliers": [{"process": "fixture-electrolysis", "technology": "pem", "share": {"value": 1, "status": "assumed", "source": "fixture: one plant"}}],
        },
    )
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors == [] and report.warnings == []
    activities = _activities(tmp_path / "out")
    de = activities["market:hydrogen:DE"]
    gross = 1 / 0.99
    assert _exchange(de, "supplier:fixture-electrolysis")["amount"] == pytest.approx(0.6 * gross, rel=1e-11)
    imported = _exchange(de, "supplier:GLO")
    assert imported["amount"] == pytest.approx(0.4 * gross, rel=1e-11) and imported["atlas code"] == "market:hydrogen:GLO" and imported["atlas link"] == "import"
    leak = _exchange(de, "loss:pipeline-leakage")  # H2 is a curated biosphere flow: exported as an emission
    assert leak["type"] == "biosphere" and leak["name"] == "Hydrogen" and leak["amount"] == pytest.approx(gross * 0.01, rel=1e-11)
    assert "consumption mix" in de["meta"]["comment"] and "fixture: synthetic trade shares" in de["meta"]["comment"]
    tech = activities["market:hydrogen:GLO:pem"]
    assert tech["name"] == "market for hydrogen (pem technology)" and tech["meta"]["atlas layer"] == "technology"
    # the ammonia (location GLO) links to the GLO production mix, never to a technology market
    assert _exchange(activities[NH3], "feed:hydrogen")["atlas code"] == "market:hydrogen:GLO"


def test_choose_prefers_the_consumers_region_then_glo_then_rer() -> None:
    def market(region: str, layer: str = "production-mix", **extra) -> mk.Market:
        return mk.Market("m", {"product": "hydrogen", "region": region, "layer": layer, "suppliers": [{"process": "p"}], **extra}, "hydrogen", None)

    found = [market("RER"), market("DE"), market("GLO"), market("NL", "technology", technology="pem")]
    assert mk.choose(found, "hydrogen", None, "DE")[0].region == "DE"
    assert mk.choose(found, "hydrogen", None, "FR")[0].region == "GLO"
    assert mk.choose([market("DE"), market("NL")], "hydrogen", None, "FR")[0] is None  # several, none fits: the caller warns
    assert mk.choose(found[:2], "hydrogen", None, "FR")[0].region == "RER"
    assert mk.choose(found[1:2], "hydrogen", None, "FR")[0].region == "DE"  # the only one
    assert mk.choose(found[3:], "hydrogen", None, "NL")[0] is None  # a technology market is chosen explicitly
    assert mk.choose(found, "hydrogen", "liquid", "DE")[0] is None  # another grade
    assert mk.choose(found, "hydrogen", None, "DE", exclude="p")[0] is None  # supplied only by the consumer itself


def test_public_build_withholds_a_market_of_unpublished_suppliers(library: Path, tmp_path: Path) -> None:
    path = library / "processes" / "fixture-electrolysis" / "process.yaml"
    path.write_text(path.read_text().replace("status: public", "status: candidate"))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture", public=True)
    assert report.errors == []
    (market,) = _json(tmp_path / "out" / "lci" / "datapackage.json")["markets"]
    assert market["status"] == "withheld" and "fixture-electrolysis" in market["reason"]
    assert _json(tmp_path / "out" / "lci" / "index.json")["markets"] == []


# --- checks ----------------------------------------------------------------------------------


GOOD = {"process": "fixture-electrolysis", "production_volume": {"value": 1, "unit": "t/a", "status": "assumed", "source": "fixture: volume"}}


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ({"product": "hydrogen/solid", "region": "DE", "layer": "production-mix", "suppliers": [GOOD], "consumption": {"equals_production": True, "reason": "fixture: no trade data at all"}}, "unknown grade"),
        ({"product": "hydrogen", "region": "DE", "layer": "production-mix", "suppliers": [GOOD]}, "states how it stands for consumption"),
        ({"product": "hydrogen", "region": "DE", "layer": "consumption-mix", "suppliers": [{**GOOD, "production_volume": None, "share": {"value": 1, "status": "assumed", "source": "fixture: share"}}]}, None),
        ({"product": "hydrogen", "region": "DE", "layer": "consumption-mix", "trade_source": "fixture: trade data", "suppliers": [{"process": "fixture-electrolysis", "share": {"value": 0.5, "status": "assumed", "source": "fixture: share"}}]}, "the shares sum to 0.5"),
        ({"product": "hydrogen", "region": "DE", "layer": "technology", "suppliers": [GOOD]}, "names its technology"),
        ({"product": "hydrogen", "region": "GLO", "layer": "production-mix", "suppliers": [GOOD], "consumption": {"equals_production": True, "reason": "fixture: no trade data at all"}}, "the same market as"),
        ({"product": "hydrogen", "region": "DE", "layer": "production-mix", "suppliers": [GOOD], "planned": "fixture: planned but with suppliers", "consumption": {"equals_production": True, "reason": "fixture: no trade data at all"}}, "is planned (with the reason) and has none"),
        ({"product": "hydrogen", "region": "DE", "layer": "production-mix", "suppliers": [{"market": "GLO", **{k: v for k, v in GOOD.items() if k != "process"}}], "consumption": {"equals_production": True, "reason": "fixture: no trade data at all"}}, "belong in a consumption mix"),
        ({"product": "hydrogen", "region": "DE", "layer": "production-mix", "suppliers": [GOOD], "consumption": {"equals_production": True, "reason": "fixture: no trade data at all"},
          "distribution": [{"mode": "rail", "distance": {"value": 10, "unit": "km", "status": "assumed", "source": "fixture: rail"}}]}, "needs a technosphere entry"),
        ({"product": "oxygen", "region": "DE", "layer": "production-mix", "suppliers": [GOOD], "consumption": {"equals_production": True, "reason": "fixture: no trade data at all"}}, "belongs in markets/oxygen.yaml"),
    ],
)
def test_invalid_markets_fail_with_the_reason(library: Path, tmp_path: Path, entry: dict, message: str | None) -> None:
    entry = {k: v for k, v in entry.items()}
    entry["suppliers"] = [{k: v for k, v in s.items() if v is not None} for s in entry["suppliers"]]
    _markets(library, entry)
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert report.errors, "expected an error"
    if message is None:  # a schema or layer error: a consumption mix without trade_source
        assert any("names its trade data" in e for e in report.errors), report.errors
    else:
        assert any(message in e and "markets/hydrogen.yaml" in e for e in report.errors), report.errors
    assert not (tmp_path / "out" / "lci").exists()


def test_a_supplier_that_does_not_make_the_product_fails(library: Path, tmp_path: Path) -> None:
    _edit(library / "markets" / "hydrogen.yaml", lambda d: d["markets"][0]["suppliers"][0].update(process="fixture-ammonia"))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert any("supplier fixture-ammonia exports no activity of hydrogen" in e for e in report.errors)


def test_a_loss_released_as_an_unmapped_component_fails(library: Path, tmp_path: Path) -> None:
    _edit(library / "markets" / "hydrogen.yaml", lambda d: d["markets"][0].update(
        losses=[{"kind": "handling", "fraction": 0.02, "released_as": "XE", "status": "assumed", "source": "fixture: a loss"}]))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert any("released as 'XE', which is neither in lci/mappings.yaml biosphere nor in pass_through" in e for e in report.errors)


def test_a_transport_leg_with_an_unknown_entry_fails(library: Path, tmp_path: Path) -> None:
    _edit(library / "markets" / "hydrogen.yaml", lambda d: d["markets"][0].update(
        distribution=[{"mode": "lorry", "use": "no-such-lorry", "distance": {"value": 50, "unit": "km", "status": "assumed", "source": "fixture: a lorry"}}]))
    report = build_lci.build(library, tmp_path / "out", "0.1.0", commit="fixture")
    assert any("uses unknown technosphere entry 'no-such-lorry'" in e for e in report.errors)
