"""potassium-chloride-1 (#514): the folder's stated numbers against its own files.

Fast, without core where it can be: the flowsheet's streams (propagated by core) are read as
YAML, and the statements the folder makes in DESIGN.md, README.md, process.yaml and lca/lca.yaml
are checked against them:

- the recovery (90.8 % of the ore's KCl in the product, SRC-1) and the ore per kg of product;
- the hot brine's KCl and NaCl per kg of water (D-004) and the crystallizer's per-pass yield
  from the linear solubility (D-007);
- the adiabatic flash of the crystallizer (D-007);
- the energy streams' arithmetic: the leach temperature, the vapour heat split, the steam heater
  and the power per t (D-008);
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
LATENT_MEAN = 2339.0  # kJ/kg at 340.65 K (thermo HEOS_FIT, SRC-6)


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


def test_hot_brine_and_the_crystallizer_yield(streams, mw):
    brine = _kg(streams, mw, "S5")
    assert brine["KCl"] / brine["H2O"] == pytest.approx(0.2149, abs=2e-4)
    assert brine["NaCl"] / brine["H2O"] == pytest.approx(0.2995, abs=5e-4)
    # D-004: SRC-2's 60 C brine at 1.25 kg/L carried to 90 C by a solubility doubling over 20-110 C
    s60 = 148 / (1250 - 148 - 254)
    s90 = s60 * (1 + 70 / 90) / (1 + 40 / 90)
    assert s90 == pytest.approx(0.2148, abs=1e-4)
    # D-007: the per-pass yield from 90 to 45 C at constant water
    assert 1 - (1 + 25 / 90) / (1 + 70 / 90) == pytest.approx(0.28, abs=0.002)
    feed = _kg(streams, mw, "S8")
    crystals = _kg(streams, mw, "S9")["KCl_s"]
    assert crystals / feed["KCl"] == pytest.approx(0.28, abs=1e-6)


def test_the_flash_is_adiabatic(streams, mw):
    brine = _flow(streams, "S5")
    makeup = _flow(streams, "S6")
    vapour = _flow(streams, "S11")
    needed = (brine * CP_BRINE * 45 - makeup * 4.18 * 20) / LATENT_MEAN
    assert vapour == pytest.approx(needed, rel=2e-3)
    # the condensate returns as dilution water
    assert _flow(streams, "S7") == pytest.approx(vapour, rel=1e-6)


def test_the_energy_streams(streams):
    ore, ml = _flow(streams, "S1"), _flow(streams, "S2")
    cp_ore = 0.273 * 0.688 + 0.5881 * 0.8642 + 0.0722 * 0.7163 + 0.0637 * 0.80 + 0.003 * 4.18
    t2 = 363.15 + ore * cp_ore * 65 / (ml * CP_BRINE)
    assert t2 == pytest.approx(streams["S2"]["temperature"]["value"], abs=0.01)
    vapour_heat = _flow(streams, "S11") * LATENT_MEAN / 3600
    q1, q2, q3 = _flow(streams, "Q1"), _flow(streams, "Q2"), _flow(streams, "Q3")
    assert q1 == pytest.approx(vapour_heat * 5 / 7, abs=0.05)
    assert q1 + q2 == pytest.approx(vapour_heat, abs=0.05)
    t15 = 318.15 + q1 * 3600 / (_flow(streams, "S14") * CP_BRINE)
    assert t15 == pytest.approx(351.18, abs=0.01)
    assert q3 == pytest.approx(_flow(streams, "S14") * CP_BRINE * (t2 - t15) / 3600, rel=1e-4)
    product_t = _flow(streams, "S16") / 1000
    assert q3 * 3.6 / product_t / 1000 == pytest.approx(1.07, abs=0.005)  # GJ per t
    assert _flow(streams, "P1") == pytest.approx(187.5 * product_t, abs=0.5)
    assert 312.5 * 0.6 == pytest.approx(187.5)  # SRC-4: per t K2O at 60 % K2O


def test_product_purity_and_tailings(streams, mw):
    product = _kg(streams, mw, "S16")
    total = sum(product.values())
    assert (product["KCl_s"] + product["KCl"]) / total == pytest.approx(0.9906, abs=1e-4)
    assert product["NaCl"] / total == pytest.approx(0.0084, abs=1e-4)
    assert _flow(streams, "S4") / _flow(streams, "S16") == pytest.approx(3.156, abs=5e-4)
    assert "99.06 wt% KCl" in _text("process.yaml") and "3.156 kg/kg" in _text("process.yaml")


def test_the_benchmarks_bind_the_dataset():
    bench = yaml.safe_load((KIT / "benchmarks" / "fertilizers.yaml").read_text(encoding="utf-8"))
    entry = next(d for d in bench["datasets"] if d["process"] == "potassium-chloride-1")
    dataset = _load("lca/dataset.yaml")
    assert entry["dataset"] == dataset["id"]
    assert set(entry["kpis"]) == {"kcl-specific-ore", "kcl-specific-electricity"}


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
