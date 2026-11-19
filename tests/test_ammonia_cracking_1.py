"""ammonia-cracking-1 (#519): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the duties given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml, lca/ and the benchmarks are checked against them:

- the cracker's outlet is the ideal-gas equilibrium of 2 NH3 <=> N2 + 3 H2 at 773.15 K and
  1100 kPa(a) on the data of process/materials.yaml (97.42 % cracked), near the 97.04 % that
  EP 4 337 600 A1's reference example 2 implies;
- the PSA recovers 79.4 % of the hydrogen, the product meets the ISO 14687 limits as the patent
  states them, and the product rate is 200 t/d;
- the elements (N, H, O, Ar) close over the plant, and the flue gas holds 2.0 mol% oxygen;
- the furnace closes: the tail gas's heat release with the preheated air covers Q1, Q2 and the
  air preheater's Q5, propagate's Q2 equals the superheater's duty, DESIGN.md's duty table
  matches the energy streams, and the bridgewall check of D-006 holds (the flue gas leaves the
  radiant section well above the tube outlet, the convection banks keep positive approaches);
- the stated specific consumptions follow from the streams, every energy stream reaches the
  LCI, the ammonia is linked to ammonia-1, and the benchmark derivations hold;
- the process is public with CC-BY-4.0 and requires cheme-as-code 1.13.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "ammonia-cracking-1"
R = 8.314462618


def _load(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def sheet() -> dict:
    return _load("process/flowsheet.yaml")


@pytest.fixture(scope="module")
def comps() -> dict[str, dict]:
    return {c["id"]: c for c in _load("process/materials.yaml")["components"]}


@pytest.fixture(scope="module")
def streams(sheet) -> dict[str, dict]:
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if "state" in s}


def _kmol(state: dict, comps) -> dict[str, float]:
    comp = state["composition"]
    x = comp["values"]
    flow = state["flow"]["value"]
    assert comp["basis"] == "mole_fraction"
    total = flow / sum(x[c] * comps[c]["molar_mass"] for c in x)
    return {c: total * v for c, v in x.items()}


def _kg(state: dict, comps) -> dict[str, float]:
    return {c: n * comps[c]["molar_mass"] for c, n in _kmol(state, comps).items()}


def _duty(streams, sid: str) -> float:
    return streams[sid]["duty"]["value"]


def _h(comp: dict, t: float) -> float:
    """Ideal-gas enthalpy on the elements basis, kJ/kmol."""
    a = comp["ideal_gas"]["cp_R"]
    integral = lambda tt: sum(a[i] * tt ** (i + 1) / (i + 1) for i in range(len(a)))  # noqa: E731
    return comp["ideal_gas"]["dHf_298"] + R * (integral(t) - integral(298.15))


def _s(comp: dict, t: float) -> float:
    a = comp["ideal_gas"]["cp_R"]
    rest = sum(a[i] / i * (t**i - 298.15**i) for i in range(1, len(a)))
    return comp["ideal_gas"]["S_298"] + R * (a[0] * math.log(t / 298.15) + rest)


def _enthalpy_kw(flows: dict[str, float], t: float, comps) -> float:
    return sum(n * _h(comps[c], t) for c, n in flows.items()) / 3600.0


def test_the_cracker_outlet_is_the_ideal_gas_equilibrium(streams, comps):
    t, p = streams["S4"]["temperature"]["value"], streams["S4"]["pressure"]["value"]
    assert (t, p) == (773.15, 1100)  # EP 4 337 600 A1: equilibrium at 11 bar and 500 C
    g = {c: _h(comps[c], t) - t * _s(comps[c], t) for c in ("NH3", "N2", "H2")}
    k = math.exp(-(0.5 * g["N2"] + 1.5 * g["H2"] - g["NH3"]) / (R * t))
    assert k == pytest.approx(266.7, rel=2e-3)
    y = _kmol(streams["S4"], comps)
    total = sum(y.values())
    y = {c: v / total for c, v in y.items()}
    q = (y["N2"] * p / 100) ** 0.5 * (y["H2"] * p / 100) ** 1.5 / (y["NH3"] * p / 100)
    assert q == pytest.approx(k, rel=2e-3)
    fed = _kmol(streams["S3"], comps)["NH3"]
    cracked = 1 - _kmol(streams["S4"], comps)["NH3"] / fed
    assert cracked == pytest.approx(0.9742, abs=5e-5)
    assert y["NH3"] == pytest.approx(0.0130, abs=5e-5)
    # the patent's reference example 2 implies 0.7705 / 0.794 = 97.04 %
    assert abs(cracked - 0.7705 / 0.794) < 0.005


def test_the_psa_split_and_the_product(streams, comps):
    feed, prod = _kmol(streams["S6"], comps), _kmol(streams["S7"], comps)
    assert prod["H2"] / feed["H2"] == pytest.approx(0.794, rel=1e-5)
    total = sum(prod.values())
    assert prod["H2"] / total >= 0.9999
    assert prod["N2"] / total * 1e6 == pytest.approx(84, abs=1)
    assert prod["N2"] / total * 1e6 < 300  # ISO 14687 as EP 4 337 600 A1 states it
    assert prod.get("NH3", 0.0) == 0.0
    h2 = _kg(streams["S7"], comps)["H2"]
    assert h2 * 24 / 1000 == pytest.approx(200, rel=1e-5)


def test_the_elements_close(streams, comps):
    atoms = {"NH3": {"N": 1, "H": 3}, "N2": {"N": 2}, "H2": {"H": 2}, "O2": {"O": 2},
             "H2O": {"H": 2, "O": 1}, "AR": {"Ar": 1}}

    def count(sids):
        out: dict[str, float] = {}
        for sid in sids:
            for c, n in _kmol(streams[sid], comps).items():
                for e, k in atoms[c].items():
                    out[e] = out.get(e, 0.0) + n * k
        return out

    ins, outs = count(["S1", "S9"]), count(["S7", "S11"])
    for e, v in ins.items():
        assert outs[e] == pytest.approx(v, rel=1e-4), e
    flue = _kmol(streams["S11"], comps)
    assert flue["O2"] / sum(flue.values()) == pytest.approx(0.02, abs=1e-6)
    assert flue.get("NH3", 0.0) == 0.0 and flue.get("H2", 0.0) == 0.0


def test_the_furnace_and_the_exchangers_close(streams, comps):
    q1, q2, q3, q4, q5 = (_duty(streams, q) for q in ("Q1", "Q2", "Q3", "Q4", "Q5"))
    t = lambda sid: streams[sid]["temperature"]["value"]  # noqa: E731
    k = lambda sid: _kmol(streams[sid], comps)  # noqa: E731
    assert q1 == pytest.approx(_enthalpy_kw(k("S4"), t("S4"), comps) - _enthalpy_kw(k("S3"), t("S3"), comps), abs=1)
    assert q2 == pytest.approx(_enthalpy_kw(k("S3"), t("S3"), comps) - _enthalpy_kw(k("S2"), t("S2"), comps), abs=1)
    assert q5 == pytest.approx(_enthalpy_kw(k("S12"), t("S12"), comps) - _enthalpy_kw(k("S10"), t("S10"), comps), abs=1)
    released = _enthalpy_kw(k("S8"), t("S8"), comps) + _enthalpy_kw(k("S12"), t("S12"), comps) - _enthalpy_kw(k("S11"), t("S11"), comps)
    assert released == pytest.approx(q1 + q2 + q5, abs=2)
    assert _enthalpy_kw(k("S4"), t("S4"), comps) - _enthalpy_kw(k("S5"), t("S5"), comps) == pytest.approx(q4, abs=2)
    assert _enthalpy_kw(k("S5"), t("S5"), comps) - _enthalpy_kw(k("S6"), t("S6"), comps) == pytest.approx(q3, abs=2)
    assert streams["Q2"]["duty"]["provenance"] == "calculated"
    design = _text("DESIGN.md")
    for sid in ("Q1", "Q4", "Q3", "Q5"):
        assert f"| {sid} | {_duty(streams, sid):.1f} kW |" in design
    assert f"| Q2 | {_duty(streams, 'Q2'):.1f} kW |" in design
    assert f"{t('S11'):.2f} K" in design and f"{t('S5'):.2f} K" in design


def _solve_t(target_kw: float, flows: dict[str, float], comps, lo: float = 250.0, hi: float = 3000.0) -> float:
    for _ in range(200):
        mid = (lo + hi) / 2
        if _enthalpy_kw(flows, mid, comps) > target_kw:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def test_the_bridgewall_check(streams, comps):
    t = lambda sid: streams[sid]["temperature"]["value"]  # noqa: E731
    k = lambda sid: _kmol(streams[sid], comps)  # noqa: E731
    flue = k("S11")
    h_in = _enthalpy_kw(k("S8"), t("S8"), comps) + _enthalpy_kw(k("S12"), t("S12"), comps)
    flame = _solve_t(h_in, flue, comps)
    bridgewall = _solve_t(h_in - _duty(streams, "Q1"), flue, comps)
    between = _solve_t(h_in - _duty(streams, "Q1") - _duty(streams, "Q2"), flue, comps)
    assert flame == pytest.approx(1885.8, abs=0.5)
    assert bridgewall == pytest.approx(993.1, abs=0.5)
    assert between == pytest.approx(671.5, abs=0.5)
    # the gas leaving the radiant section well above the tube outlet (D-006)
    assert bridgewall - t("S4") > 200
    # positive approaches in both convection banks: E-102 (S2 -> S3), then E-104 (S10 -> S12)
    assert bridgewall - t("S3") > 0 and between - t("S2") > 0
    assert between - t("S12") == pytest.approx(48.4, abs=0.5)
    assert t("S11") - t("S10") > 0
    design = _text("DESIGN.md")
    for stated in ("1885.8 K", "993.1 K", "671.5 K", "219.9 K", "48.4 K"):
        assert stated in design, stated


def test_the_stated_consumptions(streams, comps):
    product = streams["S7"]["flow"]["value"]
    h2 = _kg(streams["S7"], comps)["H2"]
    nh3 = streams["S1"]["flow"]["value"]
    assert nh3 / product == pytest.approx(7.272, abs=5e-4)
    assert nh3 / h2 == pytest.approx(7.281, abs=5e-4)
    assert streams["S9"]["flow"]["value"] / product == pytest.approx(11.96, abs=5e-3)
    assert streams["S11"]["flow"]["value"] / product == pytest.approx(18.2, abs=0.05)
    assert _duty(streams, "W1") / product == pytest.approx(0.0181, abs=5e-5)
    assert _duty(streams, "Q3") / product == pytest.approx(0.758, abs=5e-4)
    recovery = _kmol(streams["S7"], comps)["H2"] / (1.5 * _kmol(streams["S1"], comps)["NH3"])
    assert recovery == pytest.approx(0.7735, abs=5e-5)
    text = _text("process.yaml") + _text("README.md")
    for stated in ("7.27 kg", "7.28 per kg", "11.96 kg", "0.758 kWh", "97.4", "77.4 %", "492 K"):
        assert stated in text, stated


def test_every_energy_stream_reaches_the_lci(sheet):
    keys = {f["key"] for f in _load("lca/lca.yaml")["flows"]}
    for s in sheet["streams"]:
        if s.get("kind") != "energy":
            continue
        ends = {s["from"].split(".")[0], s["to"].split(".")[0]}
        if "POWER" in ends:
            assert "feed:POWER" in keys
        if "CW" in ends:
            assert "product:CW" in keys
    inventory = (PROCESS / "lca" / "inventory.csv").read_text(encoding="utf-8")
    assert "feed:NH3" in inventory and "product:FLUE" in inventory


def test_the_ammonia_is_linked_to_ammonia_1():
    maps = _load("lca/mappings.yaml")["exchanges"]
    assert maps["feed:NH3"]["dataset"] == {"path": "processes/ammonia-1/lca/dataset.yaml", "product": "product:NH3"}
    assert (KIT / "processes" / "ammonia-1" / "lca" / "dataset.yaml").exists()


def test_the_benchmark_derivations():
    bench = yaml.safe_load((KIT / "benchmarks" / "hydrogen.yaml").read_text(encoding="utf-8"))
    refs = {r["id"]: r for r in bench["kpis"]["ammonia-per-hydrogen"]["references"]}
    assert refs["jrc-2022-unpacking"]["range"][0] == pytest.approx(1 / 0.137, abs=5e-3)
    assert refs["ep4337600-ref2-ammonia"]["range"][0] == pytest.approx(17.031 / (1.5 * 2.016 * 0.7705), abs=5e-3)
    binding = next(d for d in bench["datasets"] if d["process"] == "ammonia-cracking-1")
    dataset = _load("lca/dataset.yaml")
    assert binding["dataset"] == dataset["id"]


def test_the_balance_script_cites_every_value_it_gives(sheet):
    cited = {s["id"] for s in sheet["streams"] if "scripts/balance.py" in str(s.get("state", ""))}
    assert {"Q1", "Q3", "Q4", "Q5", "W1", "S5", "S10", "S11"} <= cited


def test_published_public_with_cc_by():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["chemistry"]["outputs"][0]["inventory_key"] == "product:H2P"


def test_requires_core_1_13():
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.13"
