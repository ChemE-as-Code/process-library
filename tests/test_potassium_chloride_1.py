"""potassium-chloride-1 (#514): the folder's stated numbers against its own files.

Fast, without core where it can be: the flowsheet's streams (propagated by core) are read as
YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and lca/lca.yaml
are checked against them:

- the recovery (90.8 % of the ore's KCl in the product, SRC-1) and the ore per kg of product;
- the hot brine's KCl and NaCl per kg of water (D-004) and the crystallizer's per-pass yield, the
  equilibrium on the linear solubility, read from the flowsheet (D-007);
- the adiabatic flash of the crystallizer, an enthalpy balance (D-007);
- the energy streams: the leach temperature, the vapour heat split, the steam heater, the loop's
  heat balance, the dryer and the power per t (D-008);
- the tailings and the purge stay gaps in the Atlas build (D-010);
- the product purity and the tailings per t stated in process.yaml;
- the benchmarks bind the dataset; public with CC-BY-4.0; requires cheme-as-code 1.13.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "potassium-chloride-1"
CP_BRINE = 3.0  # kJ/(kg K), ASSUMED in D-007/D-008
CP_CAKE = 0.70  # kJ/(kg K), the dryer's cake heat capacity (D-008)
LATENT_MEAN = 2339.0  # kJ/kg at 340.65 K (thermo HEOS_FIT, SRC-6)
# kJ/(kg K): KCl(s), NaCl(s), CaSO4(s) from thermo 0.6.1 (SRC-6), insolubles ASSUMED (D-008)
CP_SOLIDS = {"KCl_s": 0.688, "NaCl_s": 0.8642, "CaSO4_s": 0.7163, "INSOL": 0.80}


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def mw() -> dict[str, float]:
    return {c["id"]: c["molar_mass"] for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams() -> dict[str, dict]:
    sheet = _load("process/flowsheet.yaml")
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _flow(streams, sid: str) -> float:
    s = streams[sid]
    return s["flow"]["value"] if "flow" in s else s["duty"]["value"]


def _kg(streams, mw, sid: str) -> dict[str, float]:
    """kg/h by component of a material stream."""
    s = streams[sid]
    total = s["flow"]["value"]
    comp = s["composition"]
    if comp["basis"] == "mass_fraction":
        return {n: total * x for n, x in comp["values"].items()}
    mass = {n: x * mw[n] for n, x in comp["values"].items()}
    m = sum(mass.values())
    return {n: total * v / m for n, v in mass.items()}


def test_recovery_and_ore_per_kg(streams, mw):
    ore = _kg(streams, mw, "S1")
    product = _kg(streams, mw, "S16")
    recovery = (product["KCl_s"] + product["KCl"]) / ore["KCl_s"]
    assert recovery == pytest.approx(0.908, abs=5e-4)
    assert product["KCl_s"] == pytest.approx(150000, rel=1e-5)
    per_kg = _flow(streams, "S1") / _flow(streams, "S16")
    assert per_kg == pytest.approx(3.996, abs=5e-4)
    assert "3.996 kg/kg" in _text("process.yaml")


def _step(sid: str) -> dict:
    return next(s for s in _load("process/flowsheet.yaml")["steps"] if s["id"] == sid)


def _solubility_line() -> tuple[float, float]:
    """D-004: SRC-2's 60 C brine (148 g/L KCl, 254 g/L NaCl at 1.25 kg/L) carried along a KCl
    solubility linear in temperature that doubles over 20-110 C: (s90, s45) in kg KCl per kg water."""
    s60 = 148 / (1250 - 148 - 254)
    s20 = s60 / (1 + 40 / 90)
    return s20 * (1 + 70 / 90), s20 * (1 + 25 / 90)


def test_hot_brine_and_the_crystallizer_yield(streams, mw):
    s90, s45 = _solubility_line()
    brine = _kg(streams, mw, "S5")
    # the spec `liquor` holds the hot brine on the line of D-004 (rounded up to 14.19 wt%)
    spec = next(s for s in _load("process/flowsheet.yaml")["specs"] if s["id"] == "liquor")
    assert brine["KCl"] / sum(brine.values()) == pytest.approx(spec["target"]["value"], abs=1e-5)
    assert brine["KCl"] / brine["H2O"] == pytest.approx(s90, abs=2e-4)
    assert brine["NaCl"] / brine["H2O"] == pytest.approx(0.2995, abs=5e-4)
    # D-007: the imposed yield is the equilibrium on the line: the mother liquor keeps the hot
    # brine's water and the make-up water (the flashed water returns as condensate)
    imposed = _step("X201")["crystallizer"]["yield"]["value"]
    equilibrium = 1 - s45 * (brine["H2O"] + _flow(streams, "S6")) / brine["KCl"]
    assert imposed == pytest.approx(equilibrium, abs=2e-4)
    feed = _kg(streams, mw, "S8")
    crystals = _kg(streams, mw, "S9")["KCl_s"]
    assert crystals / feed["KCl"] == pytest.approx(imposed, abs=1e-6)
    liquor = _kg(streams, mw, "S10")
    assert liquor["KCl"] / liquor["H2O"] == pytest.approx(s45, abs=3e-4)  # saturated, not under


def _vapour_heat(streams) -> float:
    """D-007: the crystallizer's enthalpy balance from 298.15 K, kW: the hot brine in at 363.15 K,
    the mother liquor and the cake out at 318.15 K (the condensate in and out at 318.15 K)."""
    return (_flow(streams, "S5") * CP_BRINE * 65 - _flow(streams, "S10") * CP_BRINE * 20
            - _flow(streams, "S9") * CP_CAKE * 20) / 3600  # fmt: skip


def test_the_flash_is_adiabatic(streams, mw):
    vapour = _flow(streams, "S11")
    assert vapour == pytest.approx(_vapour_heat(streams) * 3600 / LATENT_MEAN, rel=2e-4)
    fraction = _step("X201")["crystallizer"]["evaporation"]["solvent_fraction"]
    assert vapour / _kg(streams, mw, "S8")["H2O"] == pytest.approx(fraction, abs=2e-5)
    # the condensate returns as dilution water
    assert _flow(streams, "S7") == pytest.approx(vapour, rel=1e-5)


def _tailings_heat(streams, mw) -> float:
    """kW above 298.15 K of the tailings at 363.15 K: their brine at CP_BRINE, their solids at
    the solids' heat capacities (SRC-6; insolubles ASSUMED)."""
    tail = _kg(streams, mw, "S4")
    solids = sum(tail[k] * cp for k, cp in CP_SOLIDS.items())
    brine = sum(v for k, v in tail.items() if k not in CP_SOLIDS) * CP_BRINE
    return (solids + brine) * 65 / 3600


def test_the_energy_streams(streams, mw):
    # D-008: the leach's enthalpy balance gives the mother liquor's temperature
    hot_brine = _flow(streams, "S5") * CP_BRINE * 65 / 3600
    t2 = 298.15 + (hot_brine + _tailings_heat(streams, mw)) * 3600 / (_flow(streams, "S2") * CP_BRINE)
    assert t2 == pytest.approx(streams["S2"]["temperature"]["value"], abs=0.01)
    q1, q2, q3 = _flow(streams, "Q1"), _flow(streams, "Q2"), _flow(streams, "Q3")
    assert q1 + q2 == pytest.approx(_vapour_heat(streams), abs=1.0)
    ml = _flow(streams, "S14") * CP_BRINE / 3600  # kW/K
    t15 = 318.15 + q1 / ml
    assert f"S14 (3.0 kJ/(kg K)) heated counter-currently from 318.15 to {t15:.2f} K" in _text("process/flowsheet.yaml")
    assert q3 == pytest.approx(ml * (t2 - t15), rel=1e-4)
    # the loop closes: the steam leaves with the cooling water, the tailings, the cake and the purge
    out = q2 + _tailings_heat(streams, mw) + _flow(streams, "S9") * CP_CAKE * 20 / 3600 + _flow(streams, "S12") * CP_BRINE * 20 / 3600
    assert q3 == pytest.approx(out, abs=5.0)
    product_t = _flow(streams, "S16") / 1000
    gj_per_t = q3 * 3.6 / product_t / 1000
    assert f"{gj_per_t:.2f} GJ of LP steam" in _text("README.md")
    assert f"{gj_per_t:.2f} GJ of steam per t" in _text("process.yaml")
    # core's dryer: the cake's heat and the evaporation over the dryer's efficiency
    energy = _step("DR301")["dryer"]["energy"]
    absorbed = (_flow(streams, "S9") * energy["heat_capacity"] * (423.15 - energy["inlet_temperature"])
                + _flow(streams, "S17") * energy["latent_heat"]["H2O"]) / 3600  # fmt: skip
    assert _flow(streams, "Q4") == pytest.approx(absorbed / energy["efficiency"], rel=1e-4)
    # the power per t stated in P1's source (SRC-1 Table 128 per t, D-008)
    p1 = next(s for s in _load("process/flowsheet.yaml")["streams"] if s["id"] == "P1")
    per_t = float(p1["state"]["design"]["duty"]["source"].split(" kWh per t")[0].split()[-1])
    assert _flow(streams, "P1") == pytest.approx(per_t * product_t, abs=0.5)
    assert f"{per_t} kWh" in _text("README.md")


def test_product_purity_and_tailings(streams, mw):
    product = _kg(streams, mw, "S16")
    total = sum(product.values())
    assert (product["KCl_s"] + product["KCl"]) / total == pytest.approx(0.9907, abs=1e-4)
    assert product["NaCl"] / total == pytest.approx(0.0083, abs=1e-4)
    assert _flow(streams, "S4") / _flow(streams, "S16") == pytest.approx(3.155, abs=5e-4)
    assert "99.07 wt% KCl" in _text("process.yaml") and "3.155 kg/kg" in _text("process.yaml")


def test_the_wastes_stay_gaps():
    """D-010: the tailings and the purge carry slugs no LCI entry maps, so that the Atlas build
    leaves them gaps instead of linking sodium chloride or wastewater treatment."""
    outputs = {f["inventory_key"]: f["chemical"] for f in _load("process.yaml")["chemistry"]["outputs"]}
    assert outputs["product:TAIL"] == "potash-tailings" and outputs["product:BRINE"] == "potash-brine-purge"
    registry = {c["slug"] for c in yaml.safe_load((KIT / "chemicals" / "chemicals.yaml").read_text(encoding="utf-8"))["chemicals"]}
    assert {"potash-tailings", "potash-brine-purge"} <= registry
    shared = yaml.safe_load((KIT / "lci" / "mappings.yaml").read_text(encoding="utf-8"))
    for section in ("technosphere", "proxies"):
        assert "potash-tailings" not in shared[section] and "potash-brine-purge" not in shared[section]
    own = _load("lca/mappings.yaml")["exchanges"]
    assert "product:TAIL" not in own and "product:BRINE" not in own


def test_the_benchmarks_bind_the_dataset():
    bench = yaml.safe_load((KIT / "benchmarks" / "fertilizers.yaml").read_text(encoding="utf-8"))
    entry = next(d for d in bench["datasets"] if d["process"] == "potassium-chloride-1")
    dataset = _load("lca/dataset.yaml")
    assert entry["dataset"] == dataset["id"]
    assert set(entry["kpis"]) == {"kcl-specific-ore", "kcl-specific-electricity"}
    # the electricity reference is another plant than the dataset's source (D-008)
    ref = bench["kpis"]["kcl-specific-electricity"]["references"][0]
    amounts = {f["key"]: f["amount"] for f in dataset["exchanges"]}
    per_kg = amounts["feed:POWER"] / amounts["product:KCLP"]
    assert per_kg == pytest.approx(0.1413, abs=1e-4)
    assert ref["range"][0] != pytest.approx(per_kg, abs=1e-3)


def test_coverage_row():
    cov = yaml.safe_load((KIT / "coverage.yaml").read_text(encoding="utf-8"))
    row = next(e for e in cov["entries"] if e["id"] == "potassium-chloride")
    assert [c["process"] for c in row["covered_by"]] == ["potassium-chloride-1"]
    assert "npk-fertilizers" in row["feeds"]


def test_published_public_with_cc_by():
    assert _load("process.yaml")["publication"] == {"status": "public", "license": "CC-BY-4.0"}


def test_requires_core_1_13():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.13"
    assert "Needs cheme-as-code 1.13.0" in _text("README.md")
    assert "Needs cheme-as-code 1.13.0" in _text("process.yaml")
