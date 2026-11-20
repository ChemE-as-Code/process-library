"""2-ethylhexanol-1 (#511): the folder's stated numbers against its own flowsheet.

Fast and without core: the flowsheet's streams (propagated by core, the duties given by
scripts/balance.py) are read as YAML, and the statements the folder makes in DESIGN.md,
README.md, process.yaml and lca/ are checked against them:

- the crude, the isobutanal and the n-butanal meet the compositions of US 4 684 750 A, the
  aldol's organic phase holds more than 93 wt% 2-ethylhexenal and its aqueous phase 1-2 wt%
  NaOH, and the yield on n-butanal is the patent's 97.74 % of theory;
- every reaction balances its elements and its heat of reaction follows from the formation
  enthalpies scripts/balance.py uses (read from the script);
- the separators' outlets close on their inlets per component, and the folder states their
  number;
- scripts/balance.py closes every step's energy balance; R-101's heat covers C-102's reboiler
  and the rest goes to its trim cooler; C-102's condenser boils up only the organic overhead;
  the light gases are gaseous in M101's outlet; the four vacuum columns have their vacuum
  pumps' power; DESIGN.md's duty table matches the energy streams;
- C-101's pressures fall from the synthesis gas to the reactor, with the crude pumped up;
- the specific consumptions stated in process.yaml, README.md and lca/lca.yaml follow from the
  streams, the LCA outputs are current with their inputs, the feeds are linked to their library
  producers, and the process is public with CC-BY-4.0.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
PROCESS = KIT / "processes" / "2-ethylhexanol-1"


def _balance():
    spec = importlib.util.spec_from_file_location("eh_balance", PROCESS / "scripts" / "balance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    return {s["id"]: s["state"]["design"] for s in sheet["streams"] if s.get("kind") != "energy"}


@pytest.fixture(scope="module")
def duties(sheet) -> dict[str, float]:
    return {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"]
            if s.get("kind") == "energy"}


def _kg(state: dict, comps) -> dict[str, float]:
    comp = state["composition"]
    x = comp["values"]
    flow = state["flow"]["value"]
    if comp["basis"] == "mole_fraction":
        mw = sum(x[c] * comps[c]["molar_mass"] for c in x)
        return {c: flow / mw * x[c] * comps[c]["molar_mass"] for c in x if x[c] > 0}
    return {c: flow * x[c] for c in x if x[c] > 0}


def _wt(state, comps) -> dict[str, float]:
    kg = _kg(state, comps)
    total = sum(kg.values())
    return {c: v / total for c, v in kg.items()}


def test_public_and_core_version():
    manifest = _load("process.yaml")
    assert manifest["publication"] == {"status": "public", "license": "CC-BY-4.0"}
    assert manifest["maturity"] == "concept"
    assert _load("plant.yaml")["requires"] == "cheme-as-code>=1.13"


def test_compositions_of_the_patent(streams, comps):
    crude = _wt(streams["S13"], comps)
    aldehydes = crude["NBAL"] + crude["IBAL"] + crude["BUBU"]
    assert crude["IBAL"] / aldehydes == pytest.approx(0.050, abs=0.002)
    assert crude["BUBU"] / aldehydes == pytest.approx(0.010, abs=0.001)
    iso = _wt(streams["S15"], comps)
    assert iso["IBAL"] == pytest.approx(0.999, abs=0.0005)
    nbal = _wt(streams["S17"], comps)
    assert nbal["IBAL"] == pytest.approx(0.002, abs=0.0005)
    assert nbal["NBAL"] == pytest.approx(0.988, abs=0.002)
    organic = _wt(streams["S25"], comps)
    assert organic["EPA"] > 0.93
    caustic = _wt(streams["S23"], comps)
    assert 0.01 <= caustic["NAOH"] <= 0.02
    product = _wt(streams["S46"], comps)
    assert product["EH"] > 0.999


def test_yield_on_n_butanal(streams, comps):
    eh = _kg(streams["S46"], comps)["EH"] / comps["EH"]["molar_mass"]
    nbal = _kg(streams["S17"], comps)["NBAL"] / comps["NBAL"]["molar_mass"]
    assert eh / (nbal / 2) == pytest.approx(0.9774, abs=0.001)
    assert sum(_kg(streams["S46"], comps).values()) == pytest.approx(15000, rel=0.001)


def _atoms(formula: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        out[el] = out.get(el, 0) + (int(n) if n else 1)
    return out


def test_reactions_balance_and_heats(comps):
    hf = _balance().HF
    for r in _load("process/reactions.yaml")["reactions"]:
        change: dict[str, float] = {}
        for c, nu in r["stoichiometry"].items():
            for el, n in _atoms(comps[c]["formula"]).items():
                change[el] = change.get(el, 0) + nu * n
        assert all(abs(v) < 1e-9 for v in change.values()), r["id"]
        dh = sum(nu * hf[c] for c, nu in r["stoichiometry"].items())
        assert r["heat_of_reaction"]["value"] == pytest.approx(dh, abs=1.0), r["id"]


def test_separators_close(sheet, streams, comps):
    for step in sheet["steps"]:
        if "recovery" not in step:
            continue
        ins = [s for s in sheet["streams"] if s.get("kind") != "energy"
               and s["to"].split(".")[0] == step["id"]]
        outs = [s for s in sheet["streams"] if s.get("kind") != "energy"
                and s["from"].split(".")[0] == step["id"]]
        total_in: dict[str, float] = {}
        for s in ins:
            for c, v in _kg(streams[s["id"]], comps).items():
                total_in[c] = total_in.get(c, 0) + v
        total_out: dict[str, float] = {}
        for s in outs:
            for c, v in _kg(streams[s["id"]], comps).items():
                total_out[c] = total_out.get(c, 0) + v
        for c in set(total_in) | set(total_out):
            assert total_out.get(c, 0) == pytest.approx(total_in.get(c, 0), rel=1e-3, abs=0.05), (step["id"], c)


def test_reactor_heat_to_c102(duties):
    # R-101's heat covers C-102's whole reboiler, the rest to its trim cooler; R-301's steam
    # serves R-302 and the export; no steam goes to C-102 (the former Q2)
    assert duties["Q1"] + duties["Q17"] == pytest.approx(5205.7, abs=0.2)
    assert duties["Q1"] + duties["Q17"] + duties["Q18"] == pytest.approx(8697.6, abs=0.2)
    assert duties["Q3"] + duties["Q4"] == pytest.approx(4906.5, abs=0.2)
    assert "Q2" not in duties
    design = _text("DESIGN.md")
    for q in ("Q3", "Q4", "Q5", "Q8", "Q9", "Q12", "Q13", "Q18", "P4", "P5", "P6"):
        assert f"{duties[q]:.1f}" in design, q
    assert f"{duties['Q1']:.1f} + {duties['Q17']:.1f}" in design


def test_balance_script_closes_every_step(capsys):
    """balance.py checks each step's energy balance with its energy streams and stops if one is
    open by more than 1 kW (D-009); V-101 and C-101 close without a duty."""
    _balance().main()
    closures = dict(re.findall(r"closure (\w+): (-?[0-9.]+) kW", capsys.readouterr().out))
    assert {"M101", "R101", "V101", "C101", "C102", "C401"} <= set(closures)
    assert all(abs(float(v)) <= 1.0 for v in closures.values())


def test_light_gases_stay_gaseous_in_m101(sheet, streams):
    # the adiabatic mix of M101 cannot leave hotter than its hottest inlet (the light gases are
    # gaseous in the two-phase S5; only S1's propylene is liquid)
    inlets = [s["id"] for s in sheet["streams"] if s.get("to", "").startswith("M101.")]
    temps = [streams[s]["temperature"]["value"] for s in inlets]
    assert min(temps) <= streams["S5"]["temperature"]["value"] <= max(temps)


def test_decanted_water_condensed_once(sheet, streams):
    """C-102 and C-401 reflux their organic overhead; the decanted water is condensed once."""
    bal = _balance()
    _, comps, raw = bal.load()

    def lat(flows, t):
        return bal.enthalpy(flows, t, "vapor", comps) - bal.enthalpy(flows, t, "liquid", comps)

    def sensible(sid, t):
        st = raw[sid]["state"]["design"]
        return (bal.enthalpy(bal.kmol(raw[sid], comps), t, st["phase"]["value"], comps)
                - bal.enthalpy(bal.kmol(raw[sid], comps), st["temperature"]["value"],
                               st["phase"]["value"], comps))

    q = {s["id"]: s["state"]["design"]["duty"]["value"] for s in sheet["streams"]
         if s.get("kind") == "energy"}
    r = bal.REFLUX["C401"]
    lights = {c: v * (r + 1) for c, v in bal.kmol(raw["S41"], comps).items()}
    expected = (lat(lights, bal.TOP_K["C401"]) + lat(bal.kmol(raw["S40"], comps), bal.TOP_K["C401"])
                + sensible("S40", bal.TOP_K["C401"]) + sensible("S41", bal.TOP_K["C401"]))
    assert q["Q11"] == pytest.approx(expected, abs=0.2)
    water = lat(bal.kmol(raw["S16"], comps), bal.C102_TOP_K)
    assert water < 0.03 * q["Q5"]  # the water once, not (R + 1) times


def test_vacuum_columns_have_their_pumps(duties):
    # C-102 (its vent and leaks) and C-401 to C-403 (leaks), D-009
    leak = _balance().VACUUM_LEAK_KW
    assert duties["P4"] > leak and duties["P5"] == pytest.approx(3 * leak)
    equipment = {e["tag"]: e for e in _load("equipment/equipment-list.yaml")["equipment"]}
    assert equipment["P-102"]["type"] == equipment["P-401"]["type"] == "LiquidRingVacuumPump"


def test_c101_pressures_fall_to_the_reactor(streams):
    p = {s: streams[s]["pressure"]["value"] for s in ("S2", "S3", "S5", "S7", "S12", "S13", "S51")}
    assert p["S2"] > p["S13"] > p["S3"] > p["S5"] >= p["S7"] > p["S12"]
    assert p["S51"] > p["S3"]  # P-101 lifts V-101's liquid to C-101's head


def test_separator_count_stated(sheet):
    words = {9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
    n = words[sum(1 for step in sheet["steps"] if "recovery" in step)]
    for rel in ("README.md", "process.yaml"):
        assert f"{n} component separators" in _text(rel), rel


def test_heat_capacities_recorded(comps):
    src6 = _text("DESIGN.md")
    for c in ("EPA", "BUBU", "NAOH"):
        assert f"{comps[c]['liquid_heat_capacity']}" in src6, c
    assert comps["IBAL"]["liquid_heat_capacity"] == comps["NBAL"]["liquid_heat_capacity"]
    assert "isobutanal at n-butanal's 163.7, ASSUMED" in src6


def test_equipment_purge_matches_s24(streams, comps):
    purge = sum(_kg(streams["S24"], comps).values()) / 1000
    v201 = {e["tag"]: e for e in _load("equipment/equipment-list.yaml")["equipment"]}["V-201"]
    assert f"{purge:.1f} t/h" in v201["notes"]


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_lca_outputs_are_current_with_their_inputs():
    """cheme assess lca --check fails when an input changed after --write; so does this."""
    manifest = json.loads((PROCESS / "lca" / "manifest.json").read_text(encoding="utf-8"))
    dataset = _load("lca/dataset.yaml")
    recorded = {**manifest["inputs"], **dataset["provenance"]["files"]}
    assert "process.yaml" in recorded and "process/flowsheet.yaml" in recorded
    stale = [rel for rel, h in recorded.items() if _sha(PROCESS / rel) != h]
    assert not stale, f"edited after cheme assess lca --write: {stale}; rerun it and commit"


def test_specific_consumptions(streams, comps, duties):
    eh = sum(_kg(streams["S46"], comps).values())
    per = {s: sum(_kg(streams[s], comps).values()) / eh for s in ("S1", "S2", "S35", "S15")}
    desc = _text("process.yaml")
    assert f"{per['S1']:.3f} kg propylene" in desc
    assert f"{per['S2']:.3f} kg synthesis gas" in desc
    assert f"{per['S35']:.3f} kg hydrogen" in desc
    assert f"{per['S15']:.3f} kg isobutanal" in desc
    mps = (duties["Q8"] + duties["Q10"] + duties["Q12"] + duties["Q15"]) / eh
    assert f"{mps:.3f} kWh" in desc or f"{mps:.2f} kWh" in desc
    cw = sum(v for k, v in duties.items() if k in {"Q5", "Q6", "Q7", "Q9", "Q11", "Q13", "Q14",
                                                   "Q16", "Q18"}) / eh
    power = sum(v for k, v in duties.items() if k.startswith("P")) / eh
    ww = sum(_kg(streams["S50"], comps).values()) / eh
    readme = _text("README.md")
    for text in (readme, _text("DESIGN.md")):
        assert f"{mps:.3f} kWh" in text and f"{duties['Q4'] / eh:.3f} kWh" in text
        assert f"{cw:.2f} kWh" in text and f"{power:.3f} kWh" in text
    assert f"{ww:.3f} kg aqueous" in readme
    lca = _text("lca/lca.yaml")
    assert f"S1, {per['S1']:.3f} kg/kg" in lca and f"S50, {ww:.3f} kg/kg" in lca
    assert f"{mps:.3f} kWh/kg" in lca and f"{power:.3f} kWh/kg" in lca and f"{cw:.2f} kWh/kg" in lca


def test_lci_links():
    mappings = _load("lca/mappings.yaml")["exchanges"]
    assert "propylene-pdh-1" in mappings["feed:C3"]["dataset"]["path"]
    assert "hydrogen-1" in mappings["feed:H2F"]["dataset"]["path"]
    assert "chlor-alkali-1" in mappings["feed:NAOH"]["dataset"]["path"]
    lca = _load("lca/lca.yaml")
    shares = lca["allocation"]["shares"]
    assert sum(shares.values()) == pytest.approx(1.0)
    assert shares["LPSX"] == 0.0
