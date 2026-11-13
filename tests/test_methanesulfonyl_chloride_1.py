"""methanesulfonyl-chloride-1 (#159): the folder's hand-written numbers against its own model.

From the files alone (the flowsheet's calculated streams, the materials' molar masses, heat
capacities and vapour-pressure lines), the test checks what the folder states by hand:

- the dose keeps the source's 4/3 mol thionyl chloride per mol of acid (Organic Syntheses,
  Coll. Vol. 4, 571: 2.0 mol on 1.5 mol) with the recycle (D-004);
- the recipe's batch times its batches per year is the flowsheet's 1000 t/a (D-002, D-003);
- the yield on the acid and the product's assay stated in DESIGN.md, README.md and process.yaml
  follow from the streams and carry their caveats (an upper bound; the source's 71-83 %);
- the hand duties Q7 and Q9 and the temperatures of S9 and S11 follow from the streams they name
  (bubble points at 4 kPa(a) by Raoult with materials.yaml);
- the crude's flash on evacuation is no duty of its own (no Q10): an adiabatic flash ends far
  above the crude's first bubble point, and its heat lies inside the still's Q3 and Q4 (D-007);
- the models write Q1 to Q6 and Q8 (core ADR 0059);
- the utilities keep their limits: steam desuperheated to saturation below the 115 C wall limit
  (the MTT) with a trip, brine above the product's freezing point, every cooler 10 K above the
  cooling water's supply;
- the vacuum pump's after-condenser: what E-103 lets past at 4 kPa(a) and what E-106 lets past
  at atmospheric pressure (D-007, D-010);
- the accumulated-dose release with its vapour against the vent capacity (a design finding);
- the LCI's utilities per kg are the sums of the flowsheet's duties;
- the process is public with CC-BY-4.0 (ADR 0036), and its sources have register rows.

With core, R101 is solved again: the accumulation, the vent's peak, the gas with its vapour and
the vapour's largest share against the vent capacity, the content's largest volume against the
vessel, the batch's lowest bubble point against the MTT, and the heating the endothermic dosing
needs against R-101's jacket (D-003, D-009, D-011, D-014).
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "methanesulfonyl-chloride-1"
R = 8.314  # kJ/(kmol K)
CYCLE = 9.531  # h, the recipe's cycle (process/recipe.yaml, D-003)


def _yaml(rel: str) -> dict:
    return yaml.safe_load((PROCESS / rel).read_text(encoding="utf-8"))


def _text(rel: str) -> str:
    """A file's text with its line breaks and runs of spaces as single spaces (phrases wrap)."""
    return " ".join((PROCESS / rel).read_text(encoding="utf-8").split())


@pytest.fixture(scope="module")
def model():
    materials = {c["id"]: c for c in _yaml("process/materials.yaml")["components"]}
    flowsheet = _yaml("process/flowsheet.yaml")
    streams = {s["id"]: s for s in flowsheet["streams"]}
    return materials, streams, flowsheet


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


def _mcp(model, sid: str) -> float:
    """kJ/(K h) of a liquid stream from the components' liquid heat capacities."""
    materials = model[0]
    return sum(n * materials[k].get("liquid_heat_capacity", 0.0) for k, n in _kmol(model, sid).items() if n)


def _duty(model, qid: str) -> float:
    return _state(model, qid)["duty"]["value"]


def _psat(materials, name: str, t: float) -> float:
    vp = materials[name].get("vapour_pressure")
    return 100.0 * 10.0 ** (vp["a"] - vp["b"] / (t + vp["c"])) if vp else 0.0


def _bubble(materials, kmols: dict[str, float], pressure: float) -> float:
    volatile = {k: v for k, v in kmols.items() if v > 0 and materials[k].get("vapour_pressure")}
    total = sum(volatile.values())
    lo, hi = 200.0, 600.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if sum(v / total * _psat(materials, k, mid) for k, v in volatile.items()) > pressure:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def _step(model, sid: str) -> dict:
    return next(s for s in model[2]["steps"] if s["id"] == sid)


def _utility(model, uid: str) -> dict:
    fs = model[2]
    return next(u for u in [*fs["feeds"], *fs["products"]] if u["id"] == uid)["utility"]


def test_dose_keeps_the_sources_ratio(model):
    assert _kmol(model, "S4")["SOCL2"] / _kmol(model, "S1")["MSA"] == pytest.approx(2.0 / 1.5, rel=1e-4)


def test_recipe_gives_the_capacity(model):
    basis = _yaml("process/design-basis.yaml")["capacity"]
    recipe = _yaml("process/recipe.yaml")
    assert recipe["batch_size"]["value"] == basis["batch_kg"]
    assert basis["batch_kg"] * basis["batches_per_year"] == pytest.approx(1.0e6, rel=1e-3)
    assert _state(model, "S10")["flow"]["value"] * 7920 == pytest.approx(1.0e6, rel=1e-4)
    assert basis["batch_kg"] == pytest.approx(_state(model, "S10")["flow"]["value"] * CYCLE, rel=1e-3)


def test_yield_and_assay_follow_and_carry_their_caveats(model):
    yield_acid = _kmol(model, "S10")["MSCL"] / _kmol(model, "S1")["MSA"]
    assert round(100 * yield_acid, 1) == 97.2
    s10 = _state(model, "S10")
    mm = sum(x * model[0][k]["molar_mass"] for k, x in s10["composition"]["values"].items())
    assay = s10["composition"]["values"]["MSCL"] * model[0]["MSCL"]["molar_mass"] / mm
    assert round(100 * assay, 2) == 99.95
    for rel in ("DESIGN.md", "README.md", "process.yaml"):
        text = _text(rel)
        assert "97.2 %" in text and "71-83 %" in text and "upper bound" in text, rel
        assert "99.95 wt%" in text, rel


def test_hand_temperatures_are_bubble_points_at_the_still(model):
    materials = model[0]
    for sid in ("S9", "S11"):
        t = _bubble(materials, _kmol(model, sid), 4.0)
        assert _state(model, sid)["temperature"]["value"] == pytest.approx(t, abs=0.02), sid


def test_hand_duties_follow_the_streams(model):
    materials = model[0]
    q7 = _mcp(model, "S10") * (_state(model, "S9")["temperature"]["value"] - _state(model, "S10")["temperature"]["value"]) / 3600
    assert _duty(model, "Q7") == pytest.approx(q7, rel=1e-3)
    naoh = _kmol(model, "S14")["NAOH"]
    t16 = _state(model, "S16")["temperature"]["value"]
    q9 = (naoh * 20_000.0 - _mcp(model, "S16") * (t16 - 298.15)) / 3600
    assert _duty(model, "Q9") == pytest.approx(q9, rel=1e-3)


def test_crude_flash_is_inside_the_stills_duties(model):
    """D-007, L-4: the crude at 368 K flashes on evacuation, but not to its first bubble point,
    and its heat is no duty of its own (Q4 condenses the whole forerun once)."""
    materials = model[0]
    assert "Q10" not in model[1]
    brine = next(p for p in model[2]["products"] if p["id"] == "BRINE")
    assert [p["id"] for p in brine["ports"]] == ["e102", "st101"]
    crude = {k: v for k, v in _kmol(model, "S5").items() if v > 0}
    t0 = _state(model, "S5")["temperature"]["value"]
    first = _bubble(materials, crude, 4.0)
    assert first == pytest.approx(301.8, abs=0.05)
    # the sensible heat down to the first bubble point would evaporate more than the batch holds
    assert _mcp(model, "S5") * (t0 - first) / materials["SOCL2"]["heat_of_vaporization"] > 1.4 * crude["SOCL2"]
    # an adiabatic, differential flash (Raoult, materials.yaml)
    left, gone, heat, t = dict(crude), dict.fromkeys(crude, 0.0), 0.0, t0
    while True:
        total = sum(left.values())
        partial = {k: v / total * _psat(materials, k, t) for k, v in left.items()}
        if sum(partial.values()) <= 4.0:
            break
        q = sum(v * materials[k]["liquid_heat_capacity"] for k, v in left.items()) * 0.01
        hv = sum(p * materials[k]["heat_of_vaporization"] for k, p in partial.items()) / sum(partial.values())
        for k in left:
            dn = partial[k] / sum(partial.values()) * q / hv
            left[k] -= dn
            gone[k] += dn
        heat += q
        t -= 0.01
    assert t == pytest.approx(321.1, abs=0.3)
    assert gone["SOCL2"] / crude["SOCL2"] == pytest.approx(0.70, abs=0.01)
    assert heat / 3600 == pytest.approx(2.6, abs=0.05)  # kW year average
    # the still's forerun duty holds the flash: Q4 condenses more than the flash takes
    assert _duty(model, "Q3") == _duty(model, "Q4") > heat / 3600
    design = _text("DESIGN.md")
    for phrase in ("about 321 K", "about 70 %", "2.6 kW"):
        assert phrase in design, phrase


def test_models_write_their_duties(model):
    for qid in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q8"):
        assert _state(model, qid)["duty"]["provenance"] == "calculated", qid
    r101 = _step(model, "R101")
    assert r101["energy_port"] == "q" and r101["batch"]["vent"]["condenser"]["energy_port"] == "qv"
    assert r101["batch"]["vent"]["vapour"]["components"] == ["SOCL2", "MSCL"]


def test_utilities_keep_their_limits(model):
    mtt = _step(model, "R101")["hazard"]["mtt"]
    assert mtt == pytest.approx(273.15 + 115.0)  # Organic Syntheses, Note 5
    lps = _utility(model, "LPS")
    steam = lps["supply_temperature"]["value"]
    assert steam < mtt
    # a let-down arrives superheated: desuperheated to saturation, with a trip below the MTT
    assert "desuperheater" in lps["supply_temperature"]["source"]
    assert "above 385 K" in lps["supply_temperature"]["source"] and 385.0 < mtt
    assert "desuperheater after the let-down valve" in _text("DESIGN.md")
    jacket = _yaml("process/recipe.yaml")["unit_procedures"][0]["vessel"]["jacket"]
    assert jacket["heating_temperature"] == steam
    assert _state(model, "S11")["temperature"]["value"] < mtt  # the pot's end
    brine = _utility(model, "BRINE")["supply_temperature"]["value"]
    assert brine - (273.15 - 32.0) >= 10.0  # MsCl freezes at -32 C (PubChem)
    cw = _utility(model, "CW")["supply_temperature"]["value"]
    for sid in ("S10", "S16", "S17"):
        assert _state(model, sid)["temperature"]["value"] - cw >= 10.0 - 1e-9, sid
    # the crude's own boiling point lies above the MTT (D-011)
    assert _bubble(model[0], _kmol(model, "S5"), 101.325) > mtt


M3_PER_KMOL = R * 368.15 / 101.325  # m3/kmol of gas at R-101's temperature and pressure


def _vapour_share(materials, kmols: dict[str, float], t: float = 368.15) -> float:
    """The vapour's share of the gas leaving R-101 saturated (Raoult, 101.325 kPa(a)): thionyl
    chloride and MsCl, the vent's vapour components."""
    liquid = {k: v for k, v in kmols.items() if k in ("SOCL2", "MSA", "MSCL", "H2O") and v > 0}
    total = sum(liquid.values())
    return sum(liquid[k] / total * _psat(materials, k, t) for k in ("SOCL2", "MSCL") if k in liquid) / 101.325


def _k368(rid: str) -> float:
    k = next(r for r in _yaml("process/reactions.yaml")["reactions"] if r["id"] == rid)["rate"]["k"]
    return k["A"] * math.exp(-k["Ea"] / (8.314 * 368.15))  # Ea in kJ/kmol, R in kJ/(kmol K)


def test_vent_capacity_and_the_design_findings(model):
    """D-014: every case on the capacity's basis, the gas with the liquid's vapour; an
    accumulated dose is far beyond it (design finding 1); the water-ingress margin."""
    r101 = _step(model, "R101")
    capacity = r101["hazard"]["vent_capacity"]
    source = r101["hazard"]["source"]
    design = _text("DESIGN.md")
    peak = 0.001682 * M3_PER_KMOL * 3600  # the recipe's peak of SO2 and HCl
    assert f"{peak:.1f} m3/h" in source
    # the base peak with the vapour's largest share (0.539, the end of the dosing) is a bound
    assert peak / (1 - 0.539) == pytest.approx(397, abs=1) and peak / (1 - 0.539) < capacity
    assert "397 m3/h" in source and "397 m3/h" in design
    # a stoichiometric dose accumulated unreacted on the batch's acid, warmed to 368.15 K
    materials = model[0]
    acid = _kmol(model, "S1")["MSA"] * CYCLE
    volume = acid * (materials["MSA"]["liquid_molar_volume"] + materials["SOCL2"]["liquid_molar_volume"])
    assert _k368("MSCL") == pytest.approx(7.5e-5, rel=1e-4)
    gas = 2 * _k368("MSCL") * acid * acid / volume * M3_PER_KMOL * 3600
    assert gas == pytest.approx(1281, rel=0.01)
    share = _vapour_share(materials, {"MSA": acid, "SOCL2": acid})
    assert share == pytest.approx(0.878, abs=0.002)
    assert gas / (1 - share) == pytest.approx(10_500, rel=0.01)
    assert gas / (1 - share) / capacity == pytest.approx(21, abs=0.5)
    assert _bubble(materials, {"MSA": acid, "SOCL2": acid}, 101.325) == pytest.approx(373.0, abs=0.1)
    for text in (source, design):
        assert "10,500 m3/h" in text and "21 times" in text
    assert "1280 m3/h, 3.2 times" not in source + design
    # water ingress: each kg of water gives 3/18.015 kmol of SO2 and HCl, carrying vapour at its
    # largest share, above the base batch's largest flow with the vapour (about 226 m3/h)
    margin = (capacity - 226) * (1 - 0.539) / (3 / 18.015 * M3_PER_KMOL)
    assert margin == pytest.approx(25, abs=0.5)
    assert "about 25 kg/h" in design


def test_vacuum_pump_after_condenser(model):
    """D-007, D-010: E-103 at 4 kPa(a) lets 2.15 mol of thionyl chloride per mol of
    non-condensable gas past; the after-condenser E-106 at atmospheric pressure 0.028."""
    materials = model[0]
    p = _psat(materials, "SOCL2", 263.15)  # E-103's and E-106's gas outlet
    assert p == pytest.approx(2.73, abs=0.01)
    assert p / (4.0 - p) == pytest.approx(2.15, abs=0.01)
    assert p / (101.325 - p) == pytest.approx(0.028, abs=0.0005)
    # per batch: C-101's purge nitrogen (2.5 Nm3) and 1 kg/h of air in-leakage over 2.76 h
    inert = 2.5 / 22.414 + 1.0 / 28.96 * 2.76
    past = inert * p / (101.325 - p)
    assert past * materials["SOCL2"]["molar_mass"] == pytest.approx(0.68, abs=0.02)  # kg a batch
    fresh = _state(model, "S2")["flow"]["value"] * CYCLE
    assert past * materials["SOCL2"]["molar_mass"] / fresh < 0.001  # within the balance's tolerance
    design = _text("DESIGN.md")
    assert "2.15 mol of thionyl chloride" in design and "0.7 kg a batch" in design
    assert "E-106" in {e["tag"] for e in _yaml("equipment/equipment-list.yaml")["equipment"]}
    links = {link["ref"] for link in _step(model, "ST101")["links"]}
    assert {"E-103", "P-101", "E-106"} <= links


def test_lci_utilities_are_the_flowsheets_duties(model):
    product = _state(model, "S10")["flow"]["value"]
    sums = {
        "feed:LPS": ("Q1", "Q3", "Q5"),
        "product:CW": ("Q6", "Q7", "Q8", "Q9"),
        "product:BRINE": ("Q2", "Q4"),
        "feed:POWER": ("P1", "P2", "P3"),
    }
    with (PROCESS / "lca" / "inventory.csv").open(encoding="utf-8") as fh:
        rows = {r["key"]: float(r["quantity"]) for r in csv.DictReader(fh)}
    for key, ids in sums.items():
        assert rows[key] == pytest.approx(sum(_duty(model, q) for q in ids) / product, rel=1e-4), key
    brine = f"{rows['product:BRINE']:.3f} kWh"
    assert brine == "0.188 kWh"
    assert "brine 0.188 kWh" in _text("DESIGN.md") and "0.188 kWh/kg" in _text("process.yaml")
    assert rows["feed:SOCL2"] == pytest.approx(_state(model, "S2")["flow"]["value"] / product, rel=1e-4)


def test_public_and_sources_registered():
    manifest = _yaml("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    design = _text("DESIGN.md")
    cited = set(re.findall(r"SRC-\d+", _text("process/materials.yaml") + _text("process/reactions.yaml")))
    for src in cited:
        assert f"| {src} |" in design, src


@pytest.fixture(scope="module")
def solved():
    pytest.importorskip("chemeascode")
    from chemeascode.domains.process.model import load
    from chemeascode.domains.process.stirred_tank import solve_node

    process, _ = load(PROCESS)
    fs = process.flowsheet
    item = next(s for s in fs.steps if s.id == "R101")
    inlets = [s for s in fs.streams if s.to.startswith("R101.") and getattr(s, "kind", None) != "energy"]
    result, _ = solve_node(process, item, inlets, "design")
    return result


def test_core_screening_figures(model, solved):
    """D-005, D-011: R101 solved by core: accumulation, vent peak, the batch's lowest bubble point."""
    materials = model[0]
    assert solved.max_accumulation == pytest.approx(0.297, abs=0.002)
    # the model runs one hour of the flowsheet's flows; a batch is CYCLE hours of them
    assert solved.peak_vent_flow * CYCLE == pytest.approx(0.001682, rel=0.005)  # kmol/s
    # core's vapour_share is the share over the liquid at the end of the batch, not the largest
    assert solved.vapour_share == pytest.approx(0.432, abs=0.002)
    lowest = min(
        _bubble(materials, {k: c.moles[k] for k in ("SOCL2", "MSA", "MSCL")}, 101.325)
        for c in solved.cooling_profile
        if c.moles["MSA"] + c.moles["SOCL2"] + c.moles["MSCL"] > 0
    )
    assert lowest == pytest.approx(390.6, abs=0.1)
    assert lowest > _step(model, "R101")["hazard"]["mtt"]


def _batch(point) -> dict[str, float]:
    """kmol in R-101 at a profile point: the model runs one hour of the flowsheet's flows."""
    return {k: v * CYCLE for k, v in point.moles.items()}


def test_vent_gas_with_its_vapour_over_the_batch(model, solved):
    """D-014: the vent capacity's basis over core's profile: the SO2 and HCl formed (the rate laws)
    with the vapour they carry; the vapour's largest share, at the end of the dosing."""
    materials = model[0]
    capacity = _step(model, "R101")["hazard"]["vent_capacity"]
    largest, top_share = 0.0, (0.0, 0.0)
    for point in solved.cooling_profile:
        n = _batch(point)
        volume = sum(v * materials[k]["liquid_molar_volume"] for k, v in n.items() if v > 0 and materials[k].get("liquid_molar_volume"))
        if not volume:
            continue
        rate = 2 * _k368("MSCL") * n["MSA"] * n["SOCL2"] / volume + 3 * _k368("HYD") * n["H2O"] * n["SOCL2"] / volume
        share = _vapour_share(materials, n)
        largest = max(largest, rate * M3_PER_KMOL * 3600 / (1 - share))
        top_share = max(top_share, (share, point.time))
    assert largest == pytest.approx(226, abs=3) and largest < 0.5 * capacity
    assert top_share[0] == pytest.approx(0.539, abs=0.002) and top_share[1] == pytest.approx(14400, abs=1)
    assert top_share[0] > solved.vapour_share


def test_content_is_largest_at_the_end_of_the_dosing(model, solved):
    """D-003, D-014 finding 4: core sizes R-101 on the content at the end of the batch; the
    content is largest at the end of the dosing."""
    materials = model[0]

    def volume(point):
        return sum(v * materials[k]["liquid_molar_volume"] for k, v in _batch(point).items() if v > 0 and materials[k].get("liquid_molar_volume"))

    biggest = max(solved.cooling_profile, key=volume)
    assert biggest.time == pytest.approx(14400, abs=1)  # the end of the dosing
    assert volume(biggest) == pytest.approx(1.19, abs=0.005)
    assert volume(biggest) > solved.volume * CYCLE == pytest.approx(1.10, abs=0.005)
    assert volume(biggest) / 1.6 == pytest.approx(0.74, abs=0.005) and volume(biggest) / 1.6 < 0.8
    # the whole dose unreacted on the acid (a heating failure) is more than the vessel
    whole = sum(
        v * CYCLE * materials[k]["liquid_molar_volume"]
        for sid in ("S1", "S4")
        for k, v in _kmol(model, sid).items()
        if v > 0
    )
    assert whole == pytest.approx(1.81, abs=0.005) and whole > 1.6
    design = _text("DESIGN.md")
    assert "1.19 m3 then (74 % full" in design and "about 1.81 m3" in design


def test_jacket_cannot_heat_the_dosing(model, solved):
    """D-009, D-014 finding 3: the endothermic dosing needs more heat than R-101's jacket gives."""
    reaction = next(r for r in _yaml("process/reactions.yaml")["reactions"] if r["id"] == "MSCL")
    # kW to warm the dose to the batch: the batch's dose (CYCLE hours of S4) over the 4 h dosing
    warming = _mcp(model, "S4") * CYCLE / 14400 * (368.15 - 298.15)
    points = solved.cooling_profile
    peak = 0.0
    for a, b in zip(points, points[1:]):
        if 0 < b.time <= 14400 and b.time > a.time:
            rate = -(b.moles["MSA"] - a.moles["MSA"]) / (b.time - a.time) * CYCLE
            peak = max(peak, rate * reaction["heat_of_reaction"]["value"] + warming)
    assert peak == pytest.approx(62.4, abs=0.5)
    # the jacket at the end of the dosing: the vessel's diameter from 1.6 m3 at aspect ratio 1.2
    diameter = (4 * 1.6 / (math.pi * 1.2)) ** (1 / 3)
    volume = solved.volume * CYCLE
    area = math.pi * diameter * volume / (math.pi / 4 * diameter**2) + math.pi / 4 * diameter**2
    steam = _utility(model, "LPS")["supply_temperature"]["value"]
    jacket = 0.3 * area * (steam - 368.15)
    assert jacket == pytest.approx(20.6, abs=0.3)
    assert peak > 3 * jacket
