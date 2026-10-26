"""LCI export round trip through Brightway 2.5: build the workbook, install it with
cheme_as_code_lci.install() into a temporary project against a stub background, and check that
an LCA of 1 t GOX reproduces plantcode's own result for ASU-1.

plantcode's study gives end-of-life recycling a credit, so the study is reproduced by the
substitution variant of the export; the default cut-off database must differ from it by exactly
those credits (docs/system-model.md).

The project lives in a temporary BRIGHTWAY2_DIR. biosphere3 is bw2io's default biosphere
(``bw2io.create_default_biosphere3()``, packaged data, no network). The background is a STUB:
one activity per background activity the mappings name, with a single "Carbon dioxide, fossil"
emission equal to the ASU's example factor (lca/factors.yaml), characterised 1:1 by a stub
method. So the background carries exactly plantcode's numbers, and any difference is a
difference in the export (allocation, amounts, proxies, linking), not in the data.

    uv run --python 3.12 --with pytest --with pyyaml --with jsonschema --with openpyxl \
        --with ./python --with bw2calc pytest -m brightway tests
"""

from __future__ import annotations

import csv
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.brightway

# bw2data reads BRIGHTWAY2_DIR when it is imported: set it first, never touch the user's projects.
os.environ["BRIGHTWAY2_DIR"] = tempfile.mkdtemp(prefix="atlas-lci-bw-")

if os.environ.get("ATLAS_REQUIRE_BRIGHTWAY"):  # CI: a missing package is a failure, not a skip
    import bw2calc as bc
    import bw2data as bd
    import bw2io as bi
    import openpyxl  # noqa: F401
    import yaml
else:
    yaml = pytest.importorskip("yaml")
    pytest.importorskip("openpyxl")
    bd = pytest.importorskip("bw2data")
    bi = pytest.importorskip("bw2io")
    bc = pytest.importorskip("bw2calc")

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))
sys.path.insert(0, str(KIT / "python"))

import build_lci  # noqa: E402
from cheme_as_code_lci import install  # noqa: E402

FIXTURES = KIT / "tests" / "fixtures"
ASU = FIXTURES / "asu-lca"
METHOD = ("atlas-test", "climate change", "stub GWP100")
#: factors.yaml units -> the Brightway unit the mappings use, and the factor to it
PER_UNIT = {"t": 1000.0, "MWh": 1000.0, "kg": 1.0, "kWh": 1.0, "m": 1.0, "m2": 1.0, "m3": 1.0, "ea": 1.0, "tkm": 1.0}


@pytest.fixture(scope="module")
def project():
    bd.projects.set_current("atlas-lci-test")
    if "biosphere3" not in bd.databases:
        bi.create_default_biosphere3()
    co2 = bd.get_node(database="biosphere3", name="Carbon dioxide, fossil", categories=("air",))
    method = bd.Method(METHOD)
    method.register(unit="kg CO2-eq")
    method.write([(co2.key, 1.0)])
    return co2


def _stub_background(name: str, co2, activities: dict[tuple[str, str, str, str], tuple[float, int]]) -> None:
    """*activities*: (name, reference product, unit, location) -> (score per unit, production).
    A treatment activity has production -1; its score is per unit treated, as in core."""
    if name in bd.databases:
        del bd.databases[name]
    data = {}
    for number, ((act, product, unit, location), (score, production)) in enumerate(sorted(activities.items())):
        code = f"stub-{number}"
        data[(name, code)] = {
            "name": act,
            "reference product": product,
            "unit": unit,
            "location": location,
            "type": "process",
            "exchanges": [
                {"input": (name, code), "amount": float(production), "type": "production"},
                {"input": co2.key, "amount": float(score), "type": "biosphere"},
            ],
        }
    bd.Database(name).write(data)


def _score(code: str, database: str, amount: float = 1.0) -> float:
    lca = bc.LCA({bd.get_node(database=database, code=code): amount}, METHOD)
    lca.lci()
    lca.lcia()
    return float(lca.score)


def _drop(name: str) -> None:
    if name in bd.databases:
        del bd.databases[name]


# --- ASU-1: the acceptance test ----------------------------------------------------------------


def _asu_library(tmp: Path) -> Path:
    library = tmp / "library"
    (library / "processes" / "asu-1" / "lca").mkdir(parents=True)
    (library / "chemicals").mkdir()
    shutil.copy(KIT / "processes" / "asu-1" / "process.yaml", library / "processes" / "asu-1")
    shutil.copy(KIT / "chemicals" / "chemicals.yaml", library / "chemicals")
    for name in ("dataset.yaml", "lca.yaml", "factors.yaml", "results.csv"):
        shutil.copy(ASU / name, library / "processes" / "asu-1" / "lca")
    return library  # no lci/: the builder uses the library's lci/mappings.yaml


def test_asu_round_trip_reproduces_the_plantcode_baseline(project, tmp_path: Path) -> None:
    co2 = project
    out = tmp_path / "out"
    library = _asu_library(tmp_path)
    report = build_lci.build(library, out, "test", system_model="substitution")
    assert report.errors == []
    variant = "cheme-as-code-atlas-test-substitution"
    workbook = out / "lci" / f"{variant}.xlsx"

    mappings = build_lci.load_mappings(KIT / "lci" / "mappings.yaml")
    factors = {f["id"]: f for f in yaml.safe_load((ASU / "factors.yaml").read_text())["factors"]}
    # ASU-1's power links at high voltage (33 kV, D-036); the study's example factor for it is
    # still named electricity.
    factor_of = {"electricity-high-voltage": "electricity"}
    stub = {}
    for tid, entry in mappings["technosphere"].items():
        fid = factor_of.get(tid, tid)
        if "activity" not in entry or fid not in factors:
            continue
        a = entry["activity"]
        location = "FR" if a["location"] == "site" else a["location"]
        factor = factors[fid]
        stub[(a["name"], a["reference_product"], a["unit"], location)] = (factor["values"]["climate-change"] / PER_UNIT[factor["unit"]], 1)
    _stub_background("stub-ecoinvent", co2, stub)
    _drop(variant)

    result = install(workbook, background="stub-ecoinvent", location="FR")
    assert result.unlinked == [], result.summary()
    assert result.written and result.location == "FR" and not result.location_is_default
    assert result.sign_flipped == [] and result.atlas_links == []  # this library has no markets/
    assert result.system_model == "substitution" and "system model substitution" in result.summary()

    rows = list(csv.DictReader((ASU / "results.csv").open(encoding="utf-8")))
    expected = next(float(r["impact"]) for r in rows if r["scenario"] == "baseline" and r["key"] == "total")
    goxp = _score("asu-1:asu-1-500-t-d-gox:product:GOXP", variant, 1000.0)  # 1 t GOXP
    # results.csv prints 6 significant digits (152.996): half a unit of the last digit, no more.
    print(f"ASU-1 round trip: Brightway {goxp!r} kg CO2-eq per t GOXP, plantcode {expected}")
    assert goxp == pytest.approx(expected, abs=5e-4), f"Brightway {goxp:.6f} vs plantcode {expected}"

    # Allocation conserves the burden: the co-products together carry the unallocated total.
    dataset = yaml.safe_load((ASU / "dataset.yaml").read_text())
    amounts = {e["key"]: e["amount"] for e in dataset["exchanges"] if e["type"] == "product"}
    per_hour = {k: _score(f"asu-1:asu-1-500-t-d-gox:{k}", variant, v) for k, v in amounts.items()}
    shares = {k: v / sum(per_hour.values()) for k, v in per_hour.items()}
    assert shares["product:GOXP"] == pytest.approx(0.701, abs=5e-4)  # results.md: exergy, GOXP 70.1 %

    # The default cut-off database: the same result without the recycling credits, no more.
    goxp_activity = build_lci.read_workbook(workbook)["asu-1:asu-1-500-t-d-gox:product:GOXP"]
    credits = sum(
        _score(code, variant, e["amount"] * 1000.0)
        for e in goxp_activity["exchanges"]
        if (code := {"steel-recycling": "proxy:steel-scrap-credit", "aluminium-recycling": "proxy:aluminium-scrap-credit"}.get(str(e.get("atlas key")).removeprefix("end-of-life:")))
    )
    assert credits < 0
    assert build_lci.build(library, tmp_path / "cutoff", "test").errors == []
    _drop("cheme-as-code-atlas-test")
    cutoff = install(tmp_path / "cutoff" / "lci", background="stub-ecoinvent", location="FR")
    assert cutoff.unlinked == [], cutoff.summary()
    goxp_cutoff = _score("asu-1:asu-1-500-t-d-gox:product:GOXP", "cheme-as-code-atlas-test", 1000.0)
    print(f"ASU-1 cut-off: {goxp_cutoff!r} kg CO2-eq per t GOXP (credits {credits!r})")
    assert goxp_cutoff == pytest.approx(goxp - credits, rel=1e-6)


def test_staged_mapping_flows_exist_in_biosphere3(project) -> None:
    mappings = build_lci.load_mappings(KIT / "lci" / "mappings.yaml")
    flows = [e["flow"] for e in mappings["biosphere"].values()] + [e["flow"] for e in mappings["pass_through"].values() if "flow" in e]
    known = {(f["name"], tuple(f["categories"])) for f in bd.Database("biosphere3")}
    missing = [f for f in flows if (f["name"], tuple(f["categories"])) not in known]
    assert missing == []


# --- fixture library: atlas linking, treatment sign, refusal, unlinked ------------------------------

FIXTURE_STUB = {
    ("market for electricity, medium voltage", "electricity, medium voltage", "kilowatt hour", "DE"): (0.4, 1),
    ("market for water, deionised", "water, deionised", "kilogram", "RoW"): (0.001, 1),
    ("market for hydrogen, gaseous", "hydrogen, gaseous", "kilogram", "GLO"): (10.0, 1),
    ("market for nitrogen, liquid", "nitrogen, liquid", "kilogram", "RER"): (0.2, 1),
    ("market for steel, low-alloyed, hot rolled", "steel, low-alloyed, hot rolled", "kilogram", "GLO"): (2.0, 1),
    ("treatment of wastewater, average, wastewater treatment", "wastewater, average", "cubic meter", "RoW"): (0.5, -1),
}


def test_fixture_install_links_inside_the_atlas_and_flips_treatment_signs(project, tmp_path: Path) -> None:
    co2 = project
    out = tmp_path / "out"
    assert build_lci.build(FIXTURES / "library", out, "fx").errors == []
    _stub_background("stub-fixture", co2, FIXTURE_STUB)
    _drop("cheme-as-code-atlas-fx")
    db = "cheme-as-code-atlas-fx"

    result = install(out / "lci", background="stub-fixture")  # the folder with index.json
    assert result.unlinked == [], result.summary()
    assert result.location == "DE" and result.location_is_default
    # the ammonia's hydrogen goes to the hydrogen market (markets/hydrogen.yaml), which takes the electrolyser's
    assert [(l.kind, l.provider_code) for l in result.atlas_links] == [
        ("market", "market:hydrogen:GLO"), ("supply", "fixture-electrolysis:fixture-electrolysis:product:H2"),
    ]
    assert all(l.compatible for l in result.atlas_links) and result.warnings == []
    assert result.chains() == ["Fixture: ammonia synthesis (manifest only) | Ammonia <- market for hydrogen | Hydrogen <- Fixture: water electrolysis | Hydrogen at 30 bar"]
    assert len(result.sign_flipped) == 2  # wastewater of the H2 and the O2 activity

    # Brightway stores matrix amounts in single precision (bw_processing.create_array: float32,
    # ~6e-8 relative), so a hand calculation agrees to about 1e-7, not to machine precision.
    share = 41.7 / (41.7 + 333.6)  # mass allocation
    h2 = share / 41.7 * (375.3 * 0.001 + 2293.5 * 0.4 + 0.25 * 0.5 + 0.5 * 2.0)  # H2 emission: CF 0
    assert _score("fixture-electrolysis:fixture-electrolysis:product:H2", db) == pytest.approx(h2, rel=1e-6)
    ammonia = "fixture-ammonia:fixture-ammonia-hb:product:ammonia"
    assert _score(ammonia, db) == pytest.approx(0.178 * h2 + 0.823 * 0.2 + 0.4 * 0.4, rel=1e-6)

    with pytest.raises(ValueError, match="overwrite=True"):
        install(out / "lci", background="stub-fixture")
    again = install(out / "lci", background="stub-fixture", prefer_atlas=False, overwrite=True)
    assert again.ok and [l.kind for l in again.atlas_links] == ["supply"]  # the market's own supplier only
    assert not again.verified  # matched by name only
    assert _score(ammonia, db) == pytest.approx(0.178 * 10.0 + 0.823 * 0.2 + 0.4 * 0.4, rel=1e-6)


def test_install_checks_the_background_identity(project, tmp_path: Path) -> None:
    import bw2data as bd

    out = tmp_path / "out"
    assert build_lci.build(FIXTURES / "library", out, "fx").errors == []
    _stub_background("stub-identity", project, FIXTURE_STUB)
    _drop("cheme-as-code-atlas-fx")
    with pytest.raises(ValueError, match="records version '\\(none\\)', expected '3.10'"):
        install(out / "lci", background="stub-identity", expect={"version": "3.10"})
    bd.databases["stub-identity"]["version"] = "3.10"
    bd.databases.flush()
    report = install(out / "lci", background="stub-identity", expect={"version": "3.10"})
    assert report.ok and report.verified


def test_fixture_install_reports_unlinked_exchanges_and_writes_nothing(project, tmp_path: Path) -> None:
    co2 = project
    out = tmp_path / "out"
    assert build_lci.build(FIXTURES / "library", out, "fx2").errors == []
    stub = {k: v for k, v in FIXTURE_STUB.items() if not k[0].startswith("market for nitrogen")}
    _stub_background("stub-partial", co2, stub)
    _drop("cheme-as-code-atlas-fx2")

    result = install(out / "lci" / "cheme-as-code-atlas-fx2.xlsx", background="stub-partial", location="DE")
    assert not result.written and "cheme-as-code-atlas-fx2" not in bd.databases
    assert [(u["name"], u["atlas key"]) for u in result.unlinked] == [("market for nitrogen, liquid", "feed:nitrogen")]
    assert "NOT WRITTEN" in result.summary()


# --- markets (issue #49): a consumer of liquid nitrogen links to the market ---------------------


def test_liquid_nitrogen_consumer_links_to_the_market_with_trailer_and_boil_off(project, tmp_path: Path) -> None:
    """The acceptance test of #49: a downstream dataset that consumes "nitrogen, liquid" links to
    the Atlas market (cryogenic trailer, boil-off and transfer losses), the install report shows
    the chain, and a pin sends it to ASU-1's tank instead."""
    co2 = project
    library = _asu_library(tmp_path)
    shutil.copytree(KIT / "markets", library / "markets")
    shutil.copytree(FIXTURES / "lin-user", library / "processes" / "fixture-lin-user")
    out = tmp_path / "out"
    report = build_lci.build(library, out, "mk")
    assert report.errors == [] and report.warnings == []

    mappings = build_lci.load_mappings(KIT / "lci" / "mappings.yaml")
    stub = {}
    for tid, score in {"electricity-high-voltage": 0.5, "electricity": 0.4, "lorry": 0.1}.items():
        a = mappings["technosphere"][tid]["activity"]
        stub[(a["name"], a["reference_product"], a["unit"], "FR" if a["location"] == "site" else a["location"])] = (score, 1)
    for tid, entry in mappings["technosphere"].items():  # every other activity ASU-1 uses: no burden
        if "activity" in entry:
            a = entry["activity"]
            stub.setdefault((a["name"], a["reference_product"], a["unit"], "FR" if a["location"] == "site" else a["location"]), (0.0, 1))
    stub[("market for nitrogen, liquid", "nitrogen, liquid", "kilogram", "RER")] = (9.0, 1)  # the background LIN
    _stub_background("stub-markets", co2, stub)
    db = "cheme-as-code-atlas-mk"
    _drop(db)

    result = install(out / "lci", background="stub-markets", location="FR")
    assert result.unlinked == [], result.summary()
    user = "fixture-lin-user:fixture-lin-user-inerting:product:INERTING"
    lin_link = next(l for l in result.atlas_links if l.consumer_code == user)
    assert (lin_link.kind, lin_link.provider_code, lin_link.compatible) == ("market", "market:nitrogen/lin:RER", True)
    summary = result.summary()
    chain = "Fixture: tank inerting with liquid nitrogen | Inerting gas service <- market for nitrogen, liquid | Nitrogen, liquid <- Cryogenic air separation unit (500 t/d GOX) | Nitrogen, liquid"
    assert chain in result.chains() and chain in summary
    assert "boundary delivered (production-mix, RER: transport and losses included)" in summary

    plant = _score("asu-1:asu-1-500-t-d-gox:product:LIN", db)
    gross = 1 / (0.995 * 0.99)
    market = _score("market:nitrogen/lin:RER", db)
    assert market == pytest.approx(gross * plant + gross * 0.1 * 0.1, rel=1e-6)  # supply plus 100 km of trailer
    assert _score(user, db) == pytest.approx(0.05 * market + 0.01 * 0.4, rel=1e-6)

    pinned = install(out / "lci", background="stub-markets", location="FR", overwrite=True, pin=[user])
    assert pinned.ok and pinned.warnings == []
    assert next(l for l in pinned.atlas_links if l.consumer_code == user).kind == "pinned"
    assert _score(user, db) == pytest.approx(0.05 * plant + 0.01 * 0.4, rel=1e-6)
    assert install(out / "lci", background="stub-markets", location="FR", overwrite=True, prefer_atlas="plant").ok
    assert _score(user, db) == pytest.approx(0.05 * plant + 0.01 * 0.4, rel=1e-6)

    unused = install(out / "lci", background="stub-markets", location="FR", overwrite=True, pin=["no-such-activity"])
    assert unused.warnings == ["pin 'no-such-activity' matched no input linked inside the Atlas"]
    with pytest.raises(ValueError, match="prefer_atlas"):
        install(out / "lci", background="stub-markets", overwrite=True, prefer_atlas="cheapest")


def test_a_background_of_another_system_model_is_reported(project, tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert build_lci.build(FIXTURES / "library", out, "fx3").errors == []
    _stub_background("stub-apos", project, FIXTURE_STUB)
    bd.databases["stub-apos"]["system_model"] = "apos"
    bd.databases.flush()
    _drop("cheme-as-code-atlas-fx3")
    report = install(out / "lci", background="stub-apos")
    assert report.ok and any("records system model 'apos'; the Atlas database is 'cutoff'" in w for w in report.warnings)


# --- dataset contract v2: elementary flows by UUID, pedigree, system model, deprecated datasets -----


def test_install_links_flows_by_uuid_writes_pedigree_and_reports_the_system_model(project, tmp_path: Path) -> None:
    import shutil

    library = tmp_path / "library"
    shutil.copytree(FIXTURES / "library", library)
    folder = library / "processes" / "fixture-electrolysis" / "lca"
    datasets = folder / "datasets"
    datasets.mkdir()
    revised = yaml.safe_load((folder / "dataset.yaml").read_text())
    revised.update(id="fixture-electrolysis-2", version="0.2.0")
    (datasets / "revised.yaml").write_text(yaml.safe_dump(revised, sort_keys=False))
    old = yaml.safe_load((folder / "dataset.yaml").read_text())
    old.update(version="0.1.0", superseded_by={"id": "fixture-electrolysis-2", "version": "0.2.0"})
    (folder / "dataset.yaml").write_text(yaml.safe_dump(old, sort_keys=False))
    out = tmp_path / "out"
    assert build_lci.build(library, out, "v2").errors == []
    db = "cheme-as-code-atlas-v2"
    _stub_background("stub-v2", project, FIXTURE_STUB)
    _drop(db)

    result = install(out / "lci", background="stub-v2")
    assert result.unlinked == [], result.summary()
    assert (result.system_model, result.methodology_version) == ("cutoff", build_lci.METHODOLOGY_VERSION)
    assert "system model: attributional, cut-off (cutoff); methodology" in result.summary()
    # the river water of both electrolysis datasets is linked by its biosphere3 UUID, the H2
    # emissions (no identity) by name and categories
    assert result.biosphere_by_uuid == 4 and result.biosphere_by_name == 4
    # the deprecated dataset is installed, with a pointer
    assert len(result.superseded) == 2 and all("->" in s for s in result.superseded)
    assert "fixture-electrolysis:fixture-electrolysis-2:product:H2" in result.superseded[0]
    assert "deprecated activities" in result.summary()

    node = bd.get_node(database=db, code="fixture-electrolysis:fixture-electrolysis:product:H2")
    flows = [e for e in node.exchanges() if e["type"] == "biosphere" and e.input["name"] == "Water, river"]
    assert len(flows) == 1 and flows[0].input["code"] == "8c75e7ab-8ab8-41e4-b394-c166ff5b050d"
    assert flows[0]["pedigree"] == {
        "reliability": 4, "completeness": 3, "temporal correlation": 1, "geographical correlation": 5, "further technological correlation": 3,
    }
    assert flows[0]["uncertainty type"] == 2
    assert node["atlas superseded by"].endswith(":fixture-electrolysis-2:product:H2")
