"""methyltriphenylphosphonium-bromide-1 (#133): the folder's hand-written numbers against its model.

Fast, without core: the flowsheet's calculated streams (written by cheme process propagate) and
the materials' molar masses, heat capacities and vapour pressures are enough to check what the
folder states by hand (DESIGN.md D-004, D-007..D-012):

- the duties written as hand arithmetic (Q1, Q2, Q3's metal, Q5, Q6, Q7's heat-up and metal, Q8)
  follow from the streams they name;
- every energy flow reaches the LCI (library ADR 0035): LP steam, cooling water and brine per kg
  are the sums of their energy streams, as process.yaml and DESIGN.md state them;
- the jacket's coolant temperature is the cooling water's log-mean equivalent, not its supply,
  and the heating media stay below the stated temperature limits;
- the assumed temperatures of the charge (with the PPh3's heat of solution), the wash, the still
  feed and the vent header are the adiabatic mixes of their inlets;
- the hand splits DG101 and E201 and the recycle splitter X101 balance by component;
- the closed vessel's MTT (hazard.mtt) is the temperature at the relief's set pressure;
- the charge ratios (20 wt% PPh3, 1.05 mol methyl bromide per mol PPh3 in R-101) hold;
- the yield and assay stated hold and carry their caveat;
- the recipe's batch size times its batches per year gives the flowsheet's product rate;
- the process is not set public, and carries no licence, in the change that adds it.
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "methyltriphenylphosphonium-bromide-1"


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    flowsheet = _yaml("process/flowsheet.yaml")
    streams = {s["id"]: s for s in flowsheet["streams"]}
    steps = {s["id"]: s for s in flowsheet["steps"]}
    return materials, streams, steps


def _state(model, sid: str) -> dict:
    return model[1][sid]["state"]["design"]


def _kmol(model, sid: str) -> dict[str, float]:
    """kmol/h of each component of a material stream."""
    materials = model[0]
    state = _state(model, sid)
    flow = state["flow"]["value"]
    comp = state["composition"]
    if comp["basis"] == "mole_fraction":
        mm = sum(x * materials[k]["molar_mass"] for k, x in comp["values"].items())
        return {k: flow / mm * x for k, x in comp["values"].items()}
    return {k: flow * w / materials[k]["molar_mass"] for k, w in comp["values"].items()}


def _kg(model, sid: str) -> dict[str, float]:
    return {k: v * model[0][k]["molar_mass"] for k, v in _kmol(model, sid).items()}


def _mcp(model, sid: str) -> float:
    """kJ/(K h) of a stream from the components' liquid heat capacities."""
    return sum(n * model[0][k]["liquid_heat_capacity"] for k, n in _kmol(model, sid).items() if n)


def _t(model, sid: str) -> float:
    return _state(model, sid)["temperature"]["value"]


def _flow(model, sid: str) -> float:
    return _state(model, sid)["flow"]["value"]


def _duty(model, qid: str) -> float:
    return _state(model, qid)["duty"]["value"]


def _cycle(model) -> float:
    recipe = _yaml("process/recipe.yaml")
    return recipe["batch_size"]["value"] / _flow(model, "S15")


def _psat(model, cid: str, t: float) -> float:
    """kPa: the component's Antoine vapour pressure (log10 bar) of process/materials.yaml."""
    vp = model[0][cid]["vapour_pressure"]
    return 10 ** (vp["a"] - vp["b"] / (t + vp["c"])) * 100


def test_charge_ratios(model):
    s1, s3, s5, s6 = (_kmol(model, s) for s in ("S1", "S3", "S5", "S6"))
    pph3_kg = _kg(model, "S5")["PPH3"]
    assert _kg(model, "S5")["TOL"] / pph3_kg == pytest.approx(4.0, rel=1e-3)  # 20 wt% PPh3
    assert (s5["MEBR"] + s6["MEBR"]) / s5["PPH3"] == pytest.approx(1.05, rel=1e-3)
    assert s1["PPH3"] * _cycle(model) == pytest.approx(3.0, rel=1e-3)  # kmol a batch (D-004)
    assert s5["MEBR"] == pytest.approx(s3["MEBR"], rel=1e-6)  # the recycled methyl bromide


def test_hand_duties_follow_the_streams(model):
    cycle = _cycle(model)
    metal_r101 = 3000.0 * 20.0 / cycle
    q1 = (_mcp(model, "S4") * (333.15 - _t(model, "S4")) + metal_r101) / 3600
    assert _duty(model, "Q1") == pytest.approx(q1, rel=2e-3)
    s5, s7 = _kmol(model, "S5"), _kmol(model, "S7")
    extent = s7["MTPPB"] + s7["MTPPB_S"] - s5.get("MTPPB", 0.0)
    q2 = (extent * 100_000 - _mcp(model, "S6") * 35.0) / 3600
    assert _duty(model, "Q2") == pytest.approx(q2, rel=2e-3)
    cr101 = model[2]["CR101"]["crystallizer"]["energy"]["heat_capacity"]
    q3 = (_flow(model, "S7") * cr101 * 20.0 + metal_r101) / 3600
    assert _duty(model, "Q3") == pytest.approx(q3, rel=2e-3)
    # CR101's heat capacity is the slurry's from the components (D-007)
    assert cr101 == pytest.approx(_mcp(model, "S7") / _flow(model, "S7"), abs=0.005)
    s18 = _kmol(model, "S18")
    q5 = (_flow(model, "S16") * 391.0 + _mcp(model, "S16") * 65.0 + (s18["TOL"] * 104.0 + s18["MEBR"] * 42.4) * 65.0) / 3600
    assert _duty(model, "Q5") == pytest.approx(q5, rel=2e-3)
    q6 = (_mcp(model, "S15") * (333.15 - _t(model, "S15")) + 4000.0 * (333.15 - _t(model, "S13")) / cycle) / 3600
    assert _duty(model, "Q6") == pytest.approx(q6, rel=2e-3)
    # Q7: the still's boil-up energy from its source, plus the heat-up and the metal
    src = _state(model, "Q7")["duty"]["source"]
    boil_kwh = float(re.search(r"the boil-up, ([0-9.]+) kWh per batch", src).group(1))
    t0 = float(re.search(r"to its bubble point ([0-9.]+) K", src).group(1))
    t1 = float(re.search(r"to the end's ([0-9.]+) K", src).group(1))
    q7 = (boil_kwh * 3600 / cycle + _mcp(model, "S17") * (t0 - _t(model, "S17")) + 2500.0 * (t1 - _t(model, "S17")) / cycle) / 3600
    assert _duty(model, "Q7") == pytest.approx(q7, rel=2e-3)
    s19 = _kmol(model, "S19")
    latent = sum(n * model[0][k]["heat_of_vaporization"] for k, n in s19.items() if n)
    q8 = (latent + _mcp(model, "S19") * ((t0 + t1) / 2 - _t(model, "S19"))) / 3600
    assert _duty(model, "Q8") == pytest.approx(q8, rel=2e-3)
    # the condenser takes what the boil-up gives (a total condenser): latent heat ~ boil-up
    assert latent == pytest.approx(boil_kwh * 3600 / cycle, rel=0.01)


def test_every_energy_flow_reaches_the_lci(model):
    _, streams, _ = model
    energy = [s for s in streams.values() if s.get("kind") == "energy"]
    by = {}
    for s in energy:
        end = s["from"] if s["from"].split(".")[0] in ("LPS", "POWER") else s["to"]
        by.setdefault(end.split(".")[0], set()).add(s["id"])
    assert by == {"LPS": {"Q1", "Q4", "Q7"}, "CW": {"Q2", "Q3", "Q6", "Q8"}, "BRINE": {"Q5"}, "POWER": {"P1", "P2", "P3"}}
    prod = _flow(model, "S15")
    per_kg = {k: sum(_duty(model, q) for q in v) / prod for k, v in by.items()}
    assert per_kg["LPS"] == pytest.approx(0.767, abs=0.0006)
    assert per_kg["CW"] == pytest.approx(0.703, abs=0.0006)
    assert per_kg["BRINE"] == pytest.approx(0.042, abs=0.0006)
    assert per_kg["POWER"] == pytest.approx(0.150, abs=0.0006)
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8", newline="") as handle:
        inventory = {row["key"]: row for row in csv.DictReader(handle)}
    for key, kind in (("feed:LPS", "LPS"), ("product:CW", "CW"), ("product:BRINE", "BRINE"), ("feed:POWER", "POWER")):
        assert float(inventory[key]["quantity"]) == pytest.approx(per_kg[kind], rel=1e-3), key
    for rel in ("process.yaml", "DESIGN.md"):
        text = _text(rel)
        for value in ("0.767 kWh", "0.703 kWh", "0.042 kWh", "0.150 kWh"):
            assert value in text, (rel, value)


def test_jacket_on_the_log_mean_and_heating_below_the_limits(model):
    recipe = _yaml("process/recipe.yaml")
    react = next(u for u in recipe["unit_procedures"] if u["id"] == "REACT")
    jacket = react["vessel"]["jacket"]
    t_p, t_in, t_out = 333.15, 298.15, 308.15
    lmtd = ((t_p - t_in) - (t_p - t_out)) / math.log((t_p - t_in) / (t_p - t_out))
    assert jacket["coolant_temperature"] == pytest.approx(t_p - lmtd, abs=0.01)
    mtt = model[2]["R101"]["hazard"]["mtt"]
    melting = 503.65  # the salt, chemicals 1.5.2 Tm (DESIGN.md D-008)
    assert jacket["heating_temperature"] < mtt < melting
    steam = _yaml("process/flowsheet.yaml")["feeds"]
    lps = next(f for f in steam if f["id"] == "LPS")["utility"]["supply_temperature"]["value"]
    assert lps < melting  # the still's steam


def test_assumed_temperatures_are_the_adiabatic_mixes(model):
    pph3 = _kmol(model, "S1")["PPH3"]
    num = sum(_mcp(model, s) * _t(model, s) for s in ("S1", "S2", "S3")) - pph3 * 20_000
    t4 = num / sum(_mcp(model, s) for s in ("S1", "S2", "S3"))
    assert _t(model, "S4") == pytest.approx(t4, abs=0.02)
    tw = (_mcp(model, "S9") * _t(model, "S9") + _mcp(model, "S11") * _t(model, "S11")) / (_mcp(model, "S9") + _mcp(model, "S11"))
    for sid in ("S12", "S13", "S14"):
        assert _t(model, sid) == pytest.approx(tw, abs=0.02), sid
    assert model[2]["W101"]["crystallizer"]["temperature"] == pytest.approx(tw, abs=0.02)
    t17 = sum(_mcp(model, s) * _t(model, s) for s in ("S10", "S14", "S16")) / sum(_mcp(model, s) for s in ("S10", "S14", "S16"))
    assert _t(model, "S17") == pytest.approx(t17, abs=0.02)
    gas = {"TOL": 104.0, "MEBR": 42.4}
    g = {s: sum(n * gas[k] for k, n in _kmol(model, s).items()) for s in ("S23", "S18")}
    t24 = (g["S23"] * _t(model, "S23") + g["S18"] * _t(model, "S18")) / sum(g.values())
    assert _t(model, "S24") == pytest.approx(t24, abs=0.02)
    assert _yaml("process/simulation.yaml")["specs"]["W101"]["mode"] == "adiabatic"


def test_hand_splits_balance_by_component(model):
    for inlet, outlets in (("S8", ("S22", "S23")), ("S21", ("S16", "S18")), ("S19", ("S3", "S11"))):
        before = _kg(model, inlet)
        after: dict[str, float] = {}
        for sid in outlets:
            for k, v in _kg(model, sid).items():
                after[k] = after.get(k, 0.0) + v
        for k in set(before) | set(after):
            assert after.get(k, 0.0) == pytest.approx(before.get(k, 0.0), abs=0.02 + 1e-3 * _flow(model, inlet)), (inlet, k)
    # DG101 takes 90 % of the slurry's methyl bromide (D-007); E201 all of the vapour's
    assert _kmol(model, "S23")["MEBR"] / _kmol(model, "S8")["MEBR"] == pytest.approx(0.9, rel=1e-4)
    assert _kmol(model, "S18")["MEBR"] == pytest.approx(_kmol(model, "S21")["MEBR"], rel=1e-4)


def test_mtt_of_the_closed_vessel(model):
    """D-011: the temperature at which R-101 reaches 700 kPa(a) at the end of the dosing."""
    materials = model[0]
    cycle = _cycle(model)
    ch = {k: v * cycle for k, v in _kmol(model, "S5").items()}
    dose = _kmol(model, "S6")["MEBR"] * cycle
    mebr = 0.147 * (ch["MEBR"] + dose)  # the screening's largest accumulation
    reacted = ch["MEBR"] + dose - mebr
    liquid = {"TOL": ch["TOL"], "MEBR": mebr, "PPH3": ch["PPH3"] - reacted}
    v0 = sum(n * materials[k]["liquid_molar_volume"] for k, n in ch.items())
    v1 = v0 + dose * materials["MEBR"]["liquid_molar_volume"]
    pad = 230.0 * (6.3 - v0) / (6.3 - v1)
    total = sum(liquid.values())

    def pressure(t: float) -> float:
        return pad * t / 333.15 + sum(liquid[k] / total * _psat(model, k, t) for k in ("TOL", "MEBR"))

    low, high = 340.0, 500.0  # bisection: the pressure rises with the temperature
    while high - low > 1e-4:
        mid = (low + high) / 2
        low, high = (mid, high) if pressure(mid) < 700.0 else (low, mid)
    mtt = (low + high) / 2
    assert model[2]["R101"]["hazard"]["mtt"] == pytest.approx(mtt, abs=0.05)
    assert pad == pytest.approx(253.4, abs=0.2)
    assert pressure(333.15) == pytest.approx(279.4, abs=0.3)
    assert "430.99 K" in _text("DESIGN.md")


def test_yield_and_assay_as_stated_with_their_caveat(model):
    product = _kmol(model, "S15")
    yield_pph3 = product["MTPPB_S"] / _kmol(model, "S1")["PPH3"]
    assert yield_pph3 == pytest.approx(0.985, abs=0.0005)
    assay = _kg(model, "S15")["MTPPB_S"] / _flow(model, "S15")
    assert assay == pytest.approx(0.9987, abs=0.00005)
    description = " ".join(_yaml("process.yaml")["description"].split())
    assert "98.5 % on PPh3" in description and "99.87 wt%" in description
    assert "ASSUMED upper bounds" in description
    assert "ASSUMED upper bounds" in _text("DESIGN.md") and "ASSUMED upper bounds" in _text("README.md")
    assert "upper bound" in _yaml("process/design-basis.yaml")["products"][0]["purity"]
    # the source not read is not cited as read
    assert "not read" in _text("DESIGN.md").split("SRC-3")[1][:400]


def test_per_kg_feeds_as_stated(model):
    prod = _flow(model, "S15")
    assert _flow(model, "S1") / prod == pytest.approx(0.744, abs=0.0005)
    assert _flow(model, "S6") / prod == pytest.approx(0.281, abs=0.0005)
    assert _flow(model, "S2") / prod == pytest.approx(0.056, abs=0.0005)
    assert _flow(model, "S24") / prod == pytest.approx(0.022, abs=0.0005)
    assert _flow(model, "S20") / prod == pytest.approx(0.060, abs=0.0005)


def test_recipe_basis_and_capacity(model):
    recipe = _yaml("process/recipe.yaml")
    rate = _flow(model, "S15")
    batches = rate * recipe["hours_per_year"]["value"] / recipe["batch_size"]["value"]
    assert batches == pytest.approx(776.6, abs=0.1)
    assert rate * recipe["hours_per_year"]["value"] / 1000 == pytest.approx(820.9, abs=0.1)
    assert _cycle(model) == pytest.approx(10.198, abs=0.001)
    for rel in ("process.yaml", "DESIGN.md", "README.md"):
        assert "776.6" in _text(rel) and "820.9" in _text(rel), rel


def test_not_published_in_the_change_that_adds_it():
    publication = _yaml("process.yaml")["publication"]
    assert publication["status"] == "internal"
    assert "license" not in publication
